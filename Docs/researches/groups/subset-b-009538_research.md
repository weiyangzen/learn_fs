# Group Research: subset-b-009538

This grouped report covers the requested xfstests-bld GCE appliance scripts, KCS/LTM Go services, shared Go utilities, appliance image builders, syzkaller wrapper tests, and xfstests common helpers. Each section is delimited for deterministic splitting into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-load-kernel -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-load-kernel

Purpose: early boot script that installs or kexecs the kernel under test and unpacks test appliance overlays before normal test setup. It reads GCE metadata through `gce_attribute`, copies hooks and tarballs from GCS, updates `/run/test-env`, and either exits for stock-kernel runs, installs a Debian kernel package, or writes and executes `/root/do_kexec`.

Important flow: source `/usr/local/lib/gce-funcs`; optionally honor an existing `/root/do_kexec`; set the gcloud zone; fetch hooks, xfstests tarball, replacement `files.tar.gz`, and module tarball; read kernel/test metadata such as `kexec`, `kopt`, `cmd`, memory, CPUs, mount/disk options, fstest config/set/exclusions, API/string options, and NFS server mode. Non-kexec runs persist test parameters to `/run/test-env` and report the current kernel. `.deb` kernels update GRUB command line, install with retry while dpkg settles, select the matching grub menu entry, and reboot. Raw kernel images are copied to `/root/bzImage` and launched via `kexec`.

State and dependencies: writes `/root/hooks`, `/root/xfstests`, `/root/test-config`, `/run/test-env`, `/root/kernel-deb.deb`, `/root/bzImage`, `/root/do_kexec`, and GRUB drop-ins. It depends on GCE metadata, GCS helpers, `tar`, `depmod`, `dpkg`, `grub-reboot`, `kexec`, `systemctl`, and `fuser`.

Integration points: hands environment to `gce-setup`, invokes `run_hooks kexec`, uses `gce-add-metadata` for kernel status, and transforms device names in uploaded `files.tar.gz` configs for GCE mapper devices.

Risks and test signals: metadata values are interpolated into kernel command lines and shell fragments, so quoting and trusted inputs matter. Debian package menu parsing is brittle against GRUB output. Kexec failures stop the test appliance. Evidence is mostly integration-level: serial logs, metadata status, `/run/test-env`, and successful transition into `gce-setup`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-load-kernel -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-logger -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-logger

Purpose: central status logger for GCE test VMs. It converts human status messages into VM metadata, `/var/www` status files, `/results/status`, and syslog entries.

Important flow: source `gce-funcs`; accept `--force`; invoke `run_hooks logger` unless already inside hook recursion; detect messages beginning `run xfstest`; append completed tests to `$RESULT_BASE/completed`; compute percentage from `rpt_status`, `tests-to-run`, and unique completed test names; prepend `/run/fstest-config` if present; throttle metadata updates to once per minute except for the first test or forced updates.

State and dependencies: mutates `$RESULT_BASE/completed`, `/run/last_logged`, `/var/www/statusz`, `/var/www/status`, `/results/status`, and metadata key `status`. It depends on `/root/xfstests/bin/syncfs`, `gce-add-metadata`, `logger`, shell arithmetic, and test result layout.

Integration points: LTM shard monitoring reads VM metadata status to detect progress and timeouts. The web status files expose the same status locally. Hooks can annotate or react to status changes.

Risks and test signals: progress math can divide by zero if status files are malformed, although missing files fall back to `--%`. Metadata update throttling can hide rapid state changes. Integration tests should assert metadata/status file writes and progress computation with repeated sections.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-logger -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-ltm-batch-watcher -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-ltm-batch-watcher

Purpose: long-running appliance loop that watches a GCS batch command directory and executes queued shell fragments through `gce-run-batch`.

Important flow: set a GCE/xfs-friendly PATH, source `gce-funcs`, read `ltm_wait` metadata, then loop forever. Each iteration runs `script -c "/usr/local/lib/gce-run-batch --gce-dir ltm-batch"` into a temporary transcript, uploads that transcript to `gs://$GS_BUCKET/ltm-batch.log`, removes the local file, and either blocks on metadata change via `wait_for_change=true` or sleeps for 60 seconds.

State and dependencies: uses `/run/ltm-batch.$$` as transient log state and GCS `ltm-batch.log` as persistent operational evidence. It depends on metadata service semantics, `script`, `gcs_cp`, and `gce-run-batch`.

Integration points: used for remote administrative or scheduled commands against LTM machines. It shares batch directory semantics with `gce-run-batch`.

Risks and test signals: command execution is intentionally privileged and trusts GCS batch contents. A failure in `gce-run-batch` does not break the infinite loop. Test evidence is the uploaded transcript and deletion of processed batch objects when `gce-run-batch` is not in keep mode.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-ltm-batch-watcher -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-remove-metadata -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-remove-metadata

Purpose: small concurrency-safe wrapper for removing metadata keys from the current GCE instance.

Important flow: source `gce-funcs`, create `/run/xattr.lock` if absent, and use `flock` to serialize `gcloud compute instances -q remove-metadata --zone $ZONE $(hostname) --keys "$@"`.

State and dependencies: persistent state is only the lock file. It depends on `gcloud`, `$ZONE`, hostname matching the instance name, and write access to GCE metadata.

Integration points: complements `gce-add-metadata` and scripts that coordinate through metadata keys such as status, shutdown reasons, and LTM wait signals.

Risks and test signals: all arguments are passed as one comma/key string to `--keys`; callers must provide valid key syntax. Failures are redirected to `/dev/null`, so tests should verify metadata side effects rather than logs.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-remove-metadata -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-repo-cache -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-repo-cache

Purpose: provisions and mounts a persistent disk used as kernel compile/cache storage for KCS.

Important flow: source GCE and test config, define disk name `kcs-cache-disk`, by-id path `google-kcs-cache`, and default size 60 GB. If the disk does not exist, create it. Attach it to the current instance as `kcs-cache`, disable auto-delete, verify the device, format ext4 only on first creation, mount it at `/cache`, create `/cache/ccache`, and append `CCACHE_DIR=/cache/ccache` to root's shell profile.

State and dependencies: persistent GCE disk, `/cache`, `/cache/ccache`, and `/root/.bashrc`. It depends on `gcloud`, instance variables from `/root/test-config`, `mkfs.ext4`, and block device naming.

Integration points: KCS Git repositories live under `/cache/repositories` via the Go git utility, and build logs can use cache-backed ccache.

Risks and test signals: by-id device creation can lag after attach; the script exits immediately if not present. It appends to `.bashrc` every run. Tests should validate idempotent existing-disk attach and first-create formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-repo-cache -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-repo-cleanup -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-repo-cleanup

Purpose: periodic cleaner for cached KCS Git repositories on `/cache`.

Important flow: exit if `/cache/repositories` is absent, wait while `/run/kernel-building` exists, update `linux.reference` weekly with `git fetch --all`, run `git gc --auto`, remove non-reference repos whose `last-used` is older than 30 days, clean active repos weekly with `git clean -xf -e /last-*`, and trim `/cache`.

State and dependencies: uses marker files `last-fetch`, `last-used`, and `last-touched`; deletes repository directories; calls `fstrim`. Depends on Git and GNU `find` mtime behavior.

Integration points: aligned with `util/git` repository storage under `/cache/repositories`; should not run while builds are active.

Risks and test signals: `rm -rf` of stale repos is destructive, so correctness depends on marker maintenance elsewhere. Weekly `git clean` may remove untracked build artifacts except last markers. Tests should create fake repo directories with marker mtimes and assert cleanup decisions.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-repo-cleanup -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-run-batch -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-run-batch

Purpose: downloads and runs queued shell script fragments from a GCS batch directory.

Important flow: source GCE/test config, parse `--keep` and `--gce-dir`, sync `gs://$GS_BUCKET/$GCE_DIR` to `/run/batch-cmds`, iterate sorted files, optionally delete the remote object before execution, run each file under `/bin/bash -vx` via `script -a` into `/var/log/gce-run-batch.log`, and remove the local command file.

State and dependencies: uses `/run/batch-cmds`, `/var/log/gce-run-batch.log`, and GCS objects. It depends on `gcs_rsync`, `gcs_rm`, `script`, and Bash.

Integration points: driven by `gce-ltm-batch-watcher` for LTM command processing.

Risks and test signals: executing trusted bucket content as root is powerful; deleting before execution means failed commands are not retried unless `--keep` is set. Tests should check sorting, deletion semantics, option parsing, and transcript append behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-run-batch -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/kcs/bisect.go -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/kcs/bisect.go

Purpose: KCS-side Git bisect coordinator. It owns one cloned repository per bisect, builds each candidate commit, dispatches LTM tests, records test history, aggregates final results, uploads a bisector tarball, and emails a summary.

Important APIs/types: `GitBisector` stores request metadata, repository, bad/good commits, log/result directories, history, timeout channel, and status. Main methods are `Start`, `Step`, `Finish`, `Build`, `StartTest`, `Clean`, `Info`, and `CheckActive`. Package functions `RunBisect` and `BisectorStatus` route internal LTM requests and expose active state.

Control flow: `RunBisect` creates a bisector for `LTMBisectStart` or looks one up for `LTMBisectStep`, validates commit identity, advances git bisect, then loops building and skipping build-error commits until a testable commit is built. `Build` sets a one-run kernel GCS path, updates `TaskRequest` fields for LTM, and calls `RunBuild` or `MockRunBuild`. `Finish` aggregates per-step LTM results from GCS, packs a combined tarball, deletes per-step result objects, emails, and cleans.

State and dependencies: global `bisectorMap` protected by `bisectorLock`; per-bisect repo under `/cache/repositories`; logs in `logging.KCSLogDir`; GCS result objects; SendGrid email. It depends on `util/git`, `util/gcp`, `util/server`, `gce-xfstests get-results`, `tar`, and `xz`.

Risks and test signals: state is in-memory, so server restart loses active bisects. `Clean` sends on `done` while called under lock and after log closure paths; double cleanup would panic. Commit validation mutates missing `origin/` prefixes. Existing tests cover only a small bisect start path, so integration tests around KCS/LTM round trips, build-error skips, and cleanup are important.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/kcs/bisect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/kcs/bisect_test.go -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/kcs/bisect_test.go

Purpose: unit/integration test entry for KCS bisect startup behavior.

Important flow: constructs a `TaskRequest` with git repo, bad/good commits, config, and email-like options; invokes bisect-related logic; and verifies expected setup or status. The test is small and relies on KCS environment assumptions for repository and GCE config.

State and dependencies: depends on the same config, repo cache, and logging paths as the KCS service. It may require network/Git access and appliance-local config files, so it is closer to an appliance integration test than a hermetic unit test.

Integration points: gives a signal that the bisector can parse task options and initialize a repo, but it does not fully exercise LTM result callbacks, result packing, or timeout cleanup.

Risks and test signals: limited coverage means regressions in `RunBisect`, `Finish`, and GCS cleanup may not be caught. A robust suite would add mocked `git.Repository`, fake GCP storage, and deterministic result callbacks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/kcs/bisect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/kcs/build.go -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/kcs/build.go

Purpose: KCS kernel build handler and repository cache manager.

Important APIs/state: package globals `repoMap` and `repoLock` cache `*git.Repository` by parsed repo URL. `StartBuild` receives a `server.TaskRequest`, chooses a GCS kernel path, clones or reuses a repo, checks out the requested commit, builds/uploads the kernel, and optionally forwards a test request back to LTM.

Control flow: initialize KCS log dir in `init`; on request, set failure-report defers; read `GS_BUCKET`; derive repo id via `git.ParseURL`; lock all repo operations to serialize builds; call `git.NewRepository` on cache miss; call `repo.Checkout`; pass kernel config, build opts, and arch to `RunBuild` or `MockRunBuild`; update `GsKernel` and `ExtraOptions.Requester=KCSTest` before internal LTM dispatch.

State and dependencies: local repo cache under `/cache/repositories`, KCS build logs in `/var/log/go/kcs_logs`, GCS kernel object `kernels/bzImage-<testID>-onerun.deb`, and SendGrid failure mail. Depends on `util/git`, `util/gcp`, `util/server`, and external build upload script through `RunBuild`.

Risks and test signals: `repoLock` serializes all repo builds, reducing race risk but limiting concurrency. `repoMap` is in-memory and stale repo directories may outlive processes. Mock mode tests result forwarding, while real validation requires a configured KCS host.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/kcs/build.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/kcs/main.go -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/kcs/main.go

Purpose: HTTPS entrypoint for the Kernel Compile Server.

Important endpoints: `/gce-xfstests` accepts authenticated user build requests; `/internal` accepts password-protected LTM internal requests; `/internal-status` returns active bisectors to LTM. `runCompile` parses `TaskRequest`, assigns or reuses test IDs, routes plain builds, LTM builds, and bisect start/step requests. `status` wraps `BisectorStatus`.

Control flow: create `server.Instance` on `:443`; register handlers with `LoginHandler` for user endpoint and `FailureHandler` for panic-to-JSON handling; start `StartTracker` in a goroutine, start TLS server, and block on tracker completion.

State and dependencies: relies on shared server package for TLS, auth, session cookies, and internal password validation. It uses `mymath.GetTimeStamp` for generated IDs and KCS build/bisect package globals for active work.

Risks and test signals: request handling immediately starts goroutines and returns success before build/test completion. Panics are converted to JSON for request setup failures but asynchronous worker failures are reported through logs/email. Endpoint tests should cover routing for user, LTM build, bisect start/step, and invalid requester.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/kcs/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/kcs/mock.go -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/kcs/mock.go

Purpose: mock kernel build implementation used when `logging.MOCK` is enabled.

Important API: `MockRunBuild(repo, gsBucket, gsPath, gsConfig, kConfigOpts, kbuildOpts, arch, testID, buildLog, log) server.ResultType`.

Control flow: read `mock.txt` from the repository directory and map first line `good` to `server.Pass`, `bad` to `server.Fail`, and `undefined` to `server.Error`; any other content panics.

State and dependencies: depends on a local `git.Repository` and `check.ReadLines`. It does not upload kernels or create build artifacts.

Integration points: used by KCS build and bisect code to simulate build/test outcomes without real kernel builds.

Risks and test signals: missing or empty `mock.txt` can panic through `lines[0]`. It is useful for control-flow testing but does not validate `RunBuild`, GCS upload, or build option handling.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/kcs/mock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/kcs/tracker.go -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/kcs/tracker.go

Purpose: KCS lifecycle tracker that keeps the compile server available while needed and shuts it down after idle periods.

Important flow: periodically checks for active builds/bisectors and server/debug settings, updates status, and initiates VM shutdown or cleanup when KCS is idle long enough. It integrates with `server.accessKCS` assumptions that LTM launches KCS and checks shutdown metadata before relaunch.

State and dependencies: depends on KCS in-memory maps, logging paths, GCE metadata/config, and likely the appliance shutdown path. It coordinates with `main.go` through a `finished` channel so the KCS server can stop when tracker decides the instance is done.

Integration points: LTM `SendInternalRequest` may launch or relaunch KCS through `gce-xfstests launch-kcs`; tracker prevents abandoned KCS instances from persisting after build/bisect work.

Risks and test signals: because build state is in-memory, tracker decisions after process restart can differ from existing external work. Tests should cover idle timeout with and without active bisectors, debug mode behavior, and shutdown metadata interactions.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/kcs/tracker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/ltm/build.go -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/ltm/build.go

Purpose: LTM-to-KCS forwarding helper for build and bisect requests.

Important API: `ForwardKCS(req server.TaskRequest, testID string)` creates an LTM log directory, initializes a log file, defers failure email, and calls `server.SendInternalRequest(req, log, true)`.

State and dependencies: writes `/var/log/go/ltm_logs/<testID>/run.log`; depends on `util/server` for internal HTTPS request delivery, `util/email` for panic reports, and `util/logging`.

Integration points: called by LTM `runTests` for user `--commit`, watch, and bisect flows; called by mock sharder when reporting bisect step results.

Risks and test signals: failures in KCS reachability surface through panic/failure email. The helper is intentionally thin, so tests focus on request fields set by callers and `SendInternalRequest` behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/ltm/build.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/ltm/main.go -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/ltm/main.go

Purpose: HTTPS entrypoint for the Lightweight Test Manager.

Important endpoints: `/gce-xfstests` accepts authenticated user requests; `/internal` accepts KCS callbacks; `/status` returns LTM local state plus KCS bisector status. `runTests` parses requests, assigns a timestamp or user-provided test ID, routes unwatch/watch/bisect/build requests to watcher or KCS forwarding, otherwise starts a `ShardScheduler`.

Control flow: user branch watch creates `GitWatcher`; bisect and commit build create `InternalOptions` and `ForwardKCS`; plain tests call `NewShardScheduler` and `Run` in a goroutine; mock mode uses `MockNewShardScheduler`. `status` calls `server.InternalQuery` to merge KCS status with `SharderStatus` and `WatcherStatus`.

State and dependencies: uses `sharderMap`, `watcherMap`, KCS internal HTTPS, GCE config, and log directories. Authentication and panic wrapping come from the shared server package.

Risks and test signals: asynchronous launch means HTTP success only means work was accepted. Request classification relies on option combinations. Tests should cover each route, authentication boundaries, and status aggregation when KCS is absent.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/ltm/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/ltm/mock.go -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/ltm/mock.go

Purpose: JSON dump/load and mock execution support for LTM sharder state.

Important types: `JsonSharder` and `JsonShard` mirror selected `ShardScheduler` and `ShardWorker` fields for serialization. Methods `Dump`, `ShardWorker.Dump`, `JsonShard.Read`, and `ReadSharder` round-trip state. `MockNewShardScheduler` and `MockRun` avoid actual VM launches.

State and dependencies: reads/writes JSON files, reconstructs a GCP service in `ReadSharder`, and initializes logs through `logging.InitLogger`. Mock run may forward KCS bisect step callbacks.

Integration points: useful for development, reproducing sharder command construction, and testing LTM/KCS control flow without launching GCE VMs when `logging.MOCK` is true.

Risks and test signals: JSON read/write errors are ignored in this file, so malformed mocks can produce zero-valued sharders. Mock mode does not exercise quota selection, VM monitoring, result aggregation, or GCS cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/ltm/mock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/ltm/shard.go -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/ltm/shard.go

Purpose: manages one GCE test VM shard from launch through monitoring, result retrieval, classification, and cleanup.

Important type/API: `ShardWorker` stores shard identity, VM command args, status tracking, timeout/reset state, log paths, result names, and unpacked result directory. Key methods are `Run`, `monitor`, `updateSerialData`, `shutdownOnTimeout`, `finish`, `getResults`, `Info`, and `exit`.

Control flow: `NewShardWorker` builds a `gce-xfstests` command with instance name, zone, bucket, kernel, bucket subdir, config, arch options, image project defaults, no-email, and default `--no-vm-timeout`. `Run` launches the command with `check.LimitedRun`, then `monitor` polls Compute instance state, serial output, and metadata status. If status stalls beyond `monitorTimeout`, it resets the VM; launch timeouts or repeated reset failures classify as errors. `finish` finds result tarballs in GCS, runs `gce-xfstests get-results`, checks reboot markers, deletes shard result/summary objects, and updates status.

State and dependencies: GCE instance metadata/status, serial output log, command log, local unpacked results, GCS result objects, and `ShardScheduler` GCP client. Depends on Compute API, `gce-xfstests`, `results_no_reboots`, `tar` extraction performed by external script, and logrus.

Risks and test signals: metadata status is the heartbeat, so logger failures can cause resets. Serial output offset gaps are recorded but not recovered. Result lookup retries are fixed. Tests should mock GCP instance states, metadata transitions, missing tarballs, and timeout classification.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/ltm/shard.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/ltm/sharder.go -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/ltm/sharder.go

Purpose: schedules a full LTM test request across multiple shards, aggregates shard outputs, emails results, reports back to KCS for bisect flows, and uploads aggregate artifacts.

Important type/API: `ShardScheduler` stores request/test metadata, GCE config, kernel info, shard controls, result state, log/aggregate paths, parsed args/configs, GCP service, and shard list. Important methods include `NewShardScheduler`, `initLocalSharding`, `initRegionSharding`, `getKernelInfo`, `Run`, `finish`, `aggResults`, `concatResults`, `createInfo`, `createRunStats`, `genResultsSummary`, `emailReport`, `sendKCSReport`, `sendWatcherResult`, `packResults`, `clean`, and `SharderStatus`.

Control flow: decode original command, load GCE config, parse shardable configs via `parser.Cmd`, query kernel info with `gce-xfstests get-kernel-info`, open GCP service, choose region or local sharding from quotas, start all shards concurrently, aggregate result directories/serial logs, concatenate common files, generate summary/JUnit with `gen_results_summary`, determine pass/fail/error, email reports, tar/xz/upload aggregate results and XML, optionally upload summary, notify KCS or watchers, then clean local aggregate state.

State and dependencies: global `sharderMap`, local logs under `/var/log/go/ltm_logs`, aggregate directory, GCS uploads/deletes, Compute quotas, zone avoid list, and in-process shard status. Depends on `util/gcp`, `util/parser`, `util/server`, `gce-xfstests`, `gen_results_summary`, `tar`, `xz`, and SendGrid.

Risks and test signals: `getConfigs` returns nil error on parser error, which may hide invalid commands. `initLocalSharding` uses `mymath.MaxInt` for maxShards override, which increases rather than caps. Region sharding assumes zone quota availability maps to shard capacity. Tests should cover config splitting, quota-driven shard counts, summary classification, aggregate uploads, and KCS watcher callbacks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/ltm/sharder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/ltm/watcher.go -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/ltm/watcher.go

Purpose: watches a remote Git branch and triggers KCS build plus LTM test runs when HEAD changes.

Important type/API: `GitWatcher` stores watcher ID, command, bucket/report settings, original task request, test history, pack history, build counter, remote repo handle, done channel, and log/result paths. Functions include `NewGitWatcher`, `Run`, `watch`, `InitTest`, `tidyUp`, `Clean`, `Info`, `UpdateTest`, `StopWatcher`, `WatcherStatus`, and `UpdateWatcherTest`.

Control flow: create a watcher with a unique test ID, parse bucket config and original command, initialize `git.RemoteRepository`, seed `ExtraOptions` for KCS builds, and register in `watcherMap`. The watch loop initializes a first test, then every minute polls remote HEAD with exponential skip backoff after update errors; on changes it starts another build/test. Every seven days it calls currently minimal `tidyUp`. Test completion updates are routed by splitting LTM test IDs back to watcher base IDs.

State and dependencies: in-memory `watcherMap` protected by `watcherLock`, per-watcher history protected by `historyLock`, logs under LTM log dir, remote Git via `git ls-remote`, KCS forwarding, and email on watcher failures.

Risks and test signals: watchers are not durable across LTM restart. `Clean` closes `done` after removal; sending to `done` concurrently can race if lifecycle is mishandled. `tidyUp` is intentionally a placeholder. Tests should mock remote head changes, stop behavior, history length, and KCS forwarding fields.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/ltm/watcher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/check/check.go -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/check/check.go

Purpose: shared utility package for command execution, filesystem checks, file copying, and log-aware error handling.

Important APIs: `Run`, `Output`, `LimitedRun`, `LimitedOutput`, `CombinedOutput`, `CreateDir`, `FileExists`, `DirExists`, `ReadLines`, `CopyFile`, `Panic`, `NoError`, and `ContainsStr`. Constants set server source root and a capped/rate-limited external command budget.

Control flow/state: command helpers set working directory, merge provided environment into `os.Environ`, and attach stdout/stderr writers. Limited helpers use a channel cap of 12 and a rate limiter of one command per second to reduce concurrent `gce-xfstests` pressure. `ReadLines` loads a whole file and filters empty lines. `CopyFile` removes existing destination before rewriting.

Dependencies: `os/exec`, `context`, `golang.org/x/time/rate`, logrus, and filesystem APIs.

Risks and test signals: `LimitedRun` and `LimitedOutput` can leak cap slots if `limiter.Wait` returns after sending to the cap channel. `CopyFile` is not atomic. `ReadLines` is whole-file and unsuitable for very large files. Tests should cover env merging, rate/cap behavior under errors, and file helper edge cases.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/check/check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/email/email.go -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/email/email.go

Purpose: SendGrid-backed plain-text email sender and panic failure reporter for KCS/LTM.

Important APIs: `Send(subject, content, receivers)` and deferred `ReportFailure(log, logFile, email, subject)`.

Control flow: `Send` splits comma-separated recipients, loads `SENDGRID_API_KEY` and optional `GCE_REPORT_SENDER`, builds a SendGrid v3 mail with plain text content, sends, and treats only 2xx responses as success. `ReportFailure` recovers panics, logs stack trace, builds a message from panic content, syncs and appends the associated log file if available, and calls `Send`.

State and dependencies: GCE config secrets, SendGrid client, logrus log files, and `check.FileExists`.

Risks and test signals: `logging.GetFile` can return nil for non-file outputs, but the code dereferences it; most callers use file-backed logs. Recipients are not trimmed. Tests should mock SendGrid or use appliance-only integration; current test requires LTM/KCS host config.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/email/email.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/email/email_test.go -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/email/email_test.go

Purpose: appliance integration test for the email utility.

Important flow: skip unless hostname is `xfstests-ltm` or `xfstests-kcs`; read `GCE_REPORT_EMAIL` from config; call `email.Send("test", "test msg", receiver)` and fail on errors.

State and dependencies: requires real GCE config and SendGrid API key, and sends a real email.

Integration points: confirms production credentials and SendGrid connectivity in a live appliance environment.

Risks and test signals: not suitable for regular CI because it is side-effecting and environment-gated. It does not test `ReportFailure`, recipient parsing, or non-2xx responses.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/email/email_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/gcp/config.go -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/gcp/config.go

Purpose: parses GCE, LTM, and KCS shell-style config files into thread-safe key/value maps.

Important APIs/state: `Config` wraps `kv`; globals `GceConfig`, `LTMConfig`, `KCSConfig`, paths for appliance config and generated instance configs, and `configLock`. `init` loads `/usr/local/lib/gce_xfstests.config`, derives project-specific `.ltm_instance_*` and `.kcs_instance_*` paths, and optionally loads them. `Update` refreshes all available configs. `Get(configFile)` parses a file; `(*Config).Get(key)` returns a value or error.

Parsing behavior: regex accepts lines like `declare -- KEY="value"`, `declare -x KEY="value"`, and `KEY=value`. It ignores malformed lines and keeps quotes in simple assignment values when the file includes them.

State and dependencies: reads config files from fixed appliance paths; guarded by RW mutex; depends on `check.ReadLines`.

Risks and test signals: regex only captures non-whitespace values for declare lines, so values with spaces are ignored/truncated. `Get` takes a read lock on the same global lock even for independent config objects. Tests cover accepted/ignored line forms and empty values.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/gcp/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/gcp/config_test.go -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/gcp/config_test.go

Purpose: unit tests for config parsing.

Important flow: table-driven cases write temporary config content with `declare` and simple `KEY=value` forms, call `Get`, and compare parsed `kv` maps with expected maps. Tests assert malformed spacing is ignored and empty values can be represented.

State and dependencies: uses `/tmp/gce-xfstests-test.config`; depends on reflection equality and local filesystem writes.

Integration points: protects the parser used by server auth/config, GCP project lookup, bucket selection, and internal IP discovery.

Risks and test signals: tests focus on parser shape, not concurrent `Update`, global init paths, or values containing spaces. They are hermetic aside from the package init requiring the real appliance config unless adjusted by the test environment.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/gcp/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/gcp/gcp.go -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/gcp/gcp.go

Purpose: shared Google Cloud Platform wrapper for Compute Engine instance operations, quota discovery, and Cloud Storage object management.

Important types/APIs: `Service` owns context, compute service, and optional storage bucket; `Quota` stores zone-level CPU/IP/SSD shard capacity. APIs include `NewService`, `Close`, instance metadata/get/delete/reset/start, region and zone quota lookup, `GetMaxShard`, storage listing/deletion/upload, and `NotFound`.

Control flow: `NewService` uses application default credentials with Cloud Platform scope, creates Compute and Storage clients, and validates the bucket if supplied. Quota calculation chooses an UP zone in a region and computes shard capacity from available CPUs/2, IPs, and SSD GB divided by `max(50, GCE_MIN_SCR_SIZE)`. Storage helpers list by prefix, delete all matched objects, or upload one local file.

State and dependencies: external GCP resources and context cancellation. Depends on Google Cloud Go storage, compute API, oauth default credentials, and config for scratch disk sizing.

Risks and test signals: quota uses regional quota and one chosen zone, which may not reflect per-zone machine availability. `UploadFile` name says file or directory but only opens files. Delete-by-prefix can remove broad object sets if callers pass bad prefixes. Tests should mock GCP clients; current code has no unit tests here.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/gcp/gcp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/git/git.go -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/git/git.go

Purpose: repository management for KCS builds/bisects and LTM branch watchers.

Important types/APIs: `Repository` tracks local repo id/url/base/dir with a mutex; `RemoteRepository` tracks remote URL/branch/head. APIs include `NewRepository`, `GetCommit`, `Checkout`, `Valid`, `BisectStart`, `BisectStep`, `BisectLog`, `BisectReset`, `BuildUpload`, `Delete`, `Dir`, `NewRemoteRepository`, `Update`, `Head`, `getHead`, and `ParseURL`.

Control flow: `NewRepository` ensures `/cache/repositories/linux.reference` mirror exists, derives a base repo directory from URL, clones with reference if needed, then clones a shared per-id working repo and fetches all remotes. `Checkout` first tries direct hex commit checkout, then fetches and tries `origin/<commit>` and `<commit>`. Bisect methods wrap Git CLI commands and classify test results into `good`, `bad`, or `skip`. `BuildUpload` invokes `/usr/local/lib/gce-build-upload-kernel` with build/GCS env. Remote watcher uses `git ls-remote --heads`.

State and dependencies: persistent repo cache under `/cache/repositories`, Git CLI, reference Linux mirror, build upload shell script, and locks per repository.

Risks and test signals: shared clone/cache layout depends on marker cleanup scripts and Git object availability. `ParseURL` assumes at least two path elements and no SSH scp-style URLs. Tests are environment-gated to KCS for clone/checkout and likely expensive; parser tests for URL edge cases would be useful.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/git/git.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/git/git_test.go -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/git/git_test.go

Purpose: integration tests for local repository creation and checkout behavior.

Important flow: tests skip unless hostname is `xfstests-kcs`; use `https://github.com/tytso/ext4.git`; create a repository id `test`; verify reference repo and working repo directories exist; delete and assert removal; checkout known tag/commit values.

State and dependencies: uses real `/cache/repositories`, network Git access, and KCS appliance host identity. It mutates cache state and may leave directories if interrupted.

Integration points: validates the same repository code KCS uses for builds and bisects.

Risks and test signals: not hermetic and only covers happy-path clone/delete/checkout. It does not cover bisect commands, BuildUpload, malformed URLs, concurrent access, or remote watcher updates.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/git/git_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/logging/logging.go -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/logging/logging.go

Purpose: logrus logger initialization and file lifecycle helpers for KCS/LTM.

Important APIs: constants define `/var/log/go/`, `server.log`, `ltm_logs/`, `kcs_logs/`, and cache log dir. Flags `DEBUG` and `MOCK` are compile-time constants. Functions `InitLogger`, `CloseLog`, `Sync`, and `GetFile` create file-backed debug loggers, close/sync file outputs, and expose the underlying file.

State and dependencies: appends to log files with mode 0644; falls back to stdout if the file cannot be opened; uses logrus text formatter and caller reporting.

Integration points: every server, sharder, watcher, bisector, build, and failure email path uses this package.

Risks and test signals: `InitLogger("")` falls back to stdout, used by mock code. Caller reporting can be expensive. `GetFile` returns nil for non-file outputs, requiring callers to check before dereferencing; `email.ReportFailure` currently assumes non-nil. Tests should cover fallback behavior and close/sync no-ops.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/logging/logging.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/mymath/mymath.go -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/mymath/mymath.go

Purpose: small math helper package plus unique timestamp generation for test IDs.

Important APIs/state: package channels `query` and `timestamp` feed a goroutine that returns `time.Now()` then sleeps 1100 ms. `GetTimeStamp` formats `YYYYMMDDHHMMSS`. Also exports `MinInt`, `MaxInt`, `MaxIntSlice`, and `MinIntSlice`.

Control flow: timestamp requests serialize through an unbuffered channel, ensuring generated second-level timestamps are spaced far enough apart to avoid duplicates. Slice min/max return an error on empty input.

Integration points: LTM and KCS main handlers use `GetTimeStamp` for generated test IDs; GCP quota code uses min/max helpers.

Risks and test signals: timestamp generation intentionally throttles concurrent requests, which limits request admission rate. `MinIntSlice` returns error text saying `MaxIntSlice`. Tests cover blocked and unblocked timestamp timing.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/mymath/mymath.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/mymath/timestamp_test.go -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/mymath/timestamp_test.go

Purpose: timing tests for `GetTimeStamp` uniqueness/throttling.

Important flow: `TestBlockedTimeStamps` starts five concurrent calls and expects total duration between four and five seconds, then asserts adjacent timestamps differ. `TestUnblockedTimeStamps` waits between calls and asserts each call returns quickly.

State and dependencies: depends on real wall clock timing and package-level goroutine state.

Integration points: protects LTM/KCS assumption that generated test IDs are unique at second precision.

Risks and test signals: timing-sensitive tests can be flaky on heavily loaded systems. They do not cover min/max helpers.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/mymath/timestamp_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/parser/parser.go -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/parser/parser.go

Purpose: parses base64 user command lines and converts gce-xfstests config selection into LTM shardable filesystem/config lists while removing LTM-incompatible options.

Important APIs/state: `Cmd`, `sanitizeCmd`, `expandAliases`, `processConfigs`, `defaultConfigs`, `singleConfig`, and `DecodeCmd`. Constants set primary filesystem `ext4` and config root `/root`. Invalid boolean and option lists strip arguments such as `ltm`, instance/bucket/email/kernel/repo/bisect options, and monitor-timeout.

Control flow: `Cmd` splits on shell whitespace, strips invalid options and their values, expands `smoke` to `-c 4k -g quick`, and processes the first `-c` config argument. Config parsing supports `<fs>/<cfg>`, `<fs>`, `<cfg>`, and `<primary>:<fs>/<cfg>`, reading `.list` files under `/root/fs/<fs>/cfg/`.

State and dependencies: reads xfstests config files on disk; returns sanitized args and map of filesystem to config names.

Integration points: LTM `ShardScheduler` turns parsed configs into `fs/cfg` shard strings and passes sanitized args to each `gce-xfstests` shard command.

Risks and test signals: `strings.Fields` does not preserve shell quoting. `processConfigs` assumes `-c` has a following value and only handles the first one. Missing config files are silently ignored in `singleConfig`. Tests cover common config forms and invalid option stripping.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/parser/parser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/parser/parser_test.go -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/parser/parser_test.go

Purpose: table-driven tests for LTM command parsing.

Important flow: defines expected ext4 config expansions and command cases such as `ltm smoke`, explicit `-c ext4/4k -g quick`, default configs, primary filesystem override, invalid options, and duplicate handling. `TestParse` compares valid args and config maps from `Cmd`.

State and dependencies: relies on local `/root/fs/...` config files being available, so some cases are appliance/environment dependent.

Integration points: protects command sanitization used before sharding test runs.

Risks and test signals: tests are only as deterministic as the config files they read. They do not cover quoting, missing `-c` argument panic, or base64 `DecodeCmd`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/parser/parser_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/parser/set.go -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/parser/set.go

Purpose: minimal string set implementation used by the parser.

Important APIs: `NewSet`, `Add`, `Remove`, `Contain`, and `ToSlice`. Internally stores keys in `map[string]struct{}` with a package-level empty sentinel.

State and dependencies: no external dependencies; set ordering from `ToSlice` is map-randomized.

Integration points: `sanitizeCmd` uses sets for invalid booleans and invalid options.

Risks and test signals: `ToSlice` is nondeterministic and should not be used where order matters. No direct tests exist; parser tests indirectly cover `Contain`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/parser/set.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/server/info.go -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/server/info.go

Purpose: shared status response structures and KCS status query helper.

Important types/APIs: `SharderInfo`, `ShardInfo`, `TestInfo`, `WatcherInfo`, `BisectorInfo`, and `StatusResponse`, each with JSON tags and human-readable `String` methods where appropriate. `InternalQuery` asks KCS for running bisectors.

Control flow: `InternalQuery` checks if KCS is active without launching it, refreshes config, reads `GCE_KCS_INT_IP`, posts a password-protected `TaskRequest` with requester `Query` to `https://<ip>/internal-status`, validates status, decodes `StatusResponse`, and returns empty status if KCS is absent.

State and dependencies: depends on server package password, TLS send helper, GCE config, and KCS instance config generated by launch scripts.

Integration points: LTM `/status` includes local sharders/watchers plus `InternalQuery` bisectors.

Risks and test signals: string formatting can grow large because bisect logs are embedded. KCS query panics on network/config errors after active check. Tests should cover empty KCS response and JSON compatibility of status structs.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/server/info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/server/server.go -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/server/server.go

Purpose: shared HTTPS server, authentication, request/response schema, internal LTM/KCS RPC, and KCS launch/discovery logic.

Important types/APIs: request enums `RequestType`, `ResultType`; JSON structs `UserOptions`, `InternalOptions`, `TaskRequest`, `SimpleResponse`; server `Instance`; handlers `Login`, `LoginHandler`, `FailureHandler`, `ParseTaskRequest`, `SendResponse`; RPC helpers `SendInternalRequest`, `sendRequest`, `accessKCS`, `runLaunchKCS`, and `fetchLTMConfig`.

Control flow: init loads/generates cookie secret, reads LTM or KCS password from config, verifies project config, and derives TLS client certificate path. `Instance.Start` logs startup through `gce-logger` and serves TLS. User endpoints use cookie sessions; internal endpoints validate shared password in `ExtraOptions`. `SendInternalRequest` discovers peer internal IP config, injects password, sends mTLS-ish HTTPS with `InsecureSkipVerify`, and retries connection attempts. KCS access may launch KCS by running `gce-xfstests launch-kcs`.

State and dependencies: `/usr/local/lib/gce-server/.sessions_secret_key`, lighttpd/server certs, project-specific `.gce_xfstests_cert_*.pem`, generated `.ltm_instance_*`/`.kcs_instance_*`, GCE config, external `gce-xfstests`, and `gce-logger`.

Risks and test signals: TLS skips server verification while using a client certificate. Internal password is copied into request JSON logs. `RequestType.String` omits an element for `Query`, so calling it on `Query` would panic. Tests should cover auth failures, panic handler JSON, internal retry behavior, and KCS launch races.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/server/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-setup -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-setup

Purpose: main test VM setup orchestrator after kernel selection. It configures result storage, scratch disks, optional Filestore/NFS, PTS, syslog capture, metadata, and appliance state before tests run.

Important flow: source GCE funcs, test config, runtime utils, and `/run/test-env`; protect rsyslog/sshd from OOM; fetch config from GCS if missing; derive Filestore parameters from `NFSSRV`; if reboot setup marker exists, append dmesg and remount Filestore/PTS only. First boot runs pre-setup hooks, logs disk setup, decodes original command line to `/var/www/cmdline`, computes partition sizes unless PTS or blktests mode, applies `GCE_MIN_SCR_SIZE`, updates kernel metadata, starts setup-results/scratch/filestore scripts in parallel, writes `/var/www/varz` and hostname, exposes proc files and logs, removes one-time kernel/module objects, waits, installs syslog config, disables boot disk auto-delete, and runs post-setup hooks.

State and dependencies: `/results`, `/var/www`, `/run/test-env`, `/run/filestore-param`, setup marker files, GCE metadata, attached disks, syslog config, and hook directories. Depends on helper scripts in the same directory.

Integration points: consumes environment from `gce-load-kernel`, calls `gce-setup-results`, `gce-setup-scratch`, `gce-setup-filestore`, `gce-setup-pts`, and feeds shutdown/result collection.

Risks and test signals: many background jobs share failure handling through logs rather than immediate exit. Partition size computation is critical to test coverage. Integration tests should inspect created LVs/mounts, `/results/setup-syslog`, metadata, and reboot remount behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-setup -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-setup-filestore -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-setup-filestore

Purpose: creates or discovers a Google Filestore NFS instance for NFS-backed xfstests and writes runtime mount parameters.

Important flow: describe configured Filestore instance; if missing, derive the VM network from instance JSON, create Filestore with configured size/tier/location and share name `nfstest`, then describe it again. Extract IP with `jq`, mount `ip:/nfstest` on `/mnt`, create per-instance `test` and `scratch` directories plus busy marker, unmount, and write `/run/filestore-param`.

State and dependencies: GCP Filestore instance, `/mnt/<instance>/test`, `/mnt/<instance>/scratch`, `/mnt/busy-<instance>`, and `/run/filestore-param`. Depends on `gcloud`, `jq`, NFS mount support, and config variables from `gce-setup`.

Integration points: `gce-setup` runs it on first boot and reboot remount; `gce-shutdown` reads `/run/filestore-param` to remove per-instance directories and delete Filestore when no busy markers remain.

Risks and test signals: create/describe operations are synchronous and can fail due to quota or network readiness. Busy markers are best-effort coordination. Tests should verify param file content and cleanup interaction with shutdown.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-setup-filestore -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-setup-pts -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-setup-pts

Purpose: provisions storage and state for Phoronix Test Suite runs on GCE.

Important flow: source configs, start `apt-get update` in background, prefer local SSD if present, otherwise create and attach a persistent SSD disk named `${instance}-disk` as `pts`. Format with `mkfs.$FSTESTTYP` if filesystem type differs, mount at `/pts`, restore PTS state/results tarballs from GCS if first use, bind mount `/pts/phoronix-test-suite` to `/var/lib/phoronix-test-suite`, wait for apt update, and install `pts/disk`.

State and dependencies: PTS disk/local SSD, `/pts`, `/var/lib/phoronix-test-suite`, GCS `pts-state.tar.xz`, `pts-results.tar.xz`, and per-instance results tarballs. Depends on gcloud, mkfs tools, GCS helpers, mount, and `phoronix-test-suite`.

Integration points: invoked by `gce-setup` when command mode is `pts`; `pts-save` later archives state/results.

Risks and test signals: formatting decision depends solely on `blkid TYPE`, so wrong target device is destructive. Local SSD state is ephemeral. Tests should validate idempotent remount and state restoration without reformatting.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-setup-pts -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-setup-results -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-setup-results

Purpose: initializes `/results` for a test run.

Important flow: create `/results`, touch `runtests.log`, copy `/var/www/cmdline`, copy hooks and `/proc/config.gz` if available, write `uname -r` and `$TESTRUNID`, fetch `check-time.tar.gz` from GCS, unpack it in `/results`, and move `check.time.*` files into per-results directories with `check.time` names.

State and dependencies: `/results` tree, `kernel_version`, `testrunid`, unpacked historical timing files. Depends on `gcs_cp`, tar, and environment variables.

Integration points: run by `gce-setup` before tests; shutdown and LTM result aggregation consume `/results` files.

Risks and test signals: missing check-time tarball is tolerated only through redirected command behavior; subsequent tar may fail if `/tmp/check-time.tar.gz` is absent. Tests should check initialization with and without optional hooks/config/timing files.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-setup-results -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-setup-scratch -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-setup-scratch

Purpose: provisions the scratch/test block storage layout for GCE xfstests.

Important flow: prefer local SSD/NVMe devices, otherwise parse `DISK_SPEC` for scope, disk type, and size; create zonal or regional PD with replica zones; attach as `scratch`; set auto-delete; verify by-id device. In blktests mode it exits after attach. Otherwise, if volume group `xt` does not exist, create PV/VG and logical volumes `vdb`, `vdc`, `vdd`, `vde`, `vdf`, `vdi`, and `vdj` according to computed sizes, formatting `vdb` ext4 for primary test use.

State and dependencies: GCE disk `${instance}-scratch`, `/dev/disk/by-id/google-scratch`, LVM VG `xt`, logical volumes under `/dev/mapper/xt-*`. Depends on `gcloud`, `pvcreate`, `vgcreate`, `lvcreate`, `mke2fs`, config/env from `gce-setup`.

Integration points: sizes come from `compute_partition_sizes` in `gce-setup`; `/root/test-config` maps test devices through `/dev/mapper/xt-*`.

Risks and test signals: parsing `DISK_SPEC` is permissive and silently falls back. Regional disk zone selection is heuristic. Existing VG prevents resizing/recreation. Tests should cover zonal/regional parsing, local SSD preference, and LVM idempotence.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-setup-scratch -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-syslog.conf -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-syslog.conf

Purpose: rsyslog configuration fragment for copying system logs into the results volume.

Important behavior: the file contains a single rule/config line used by `gce-setup` when installing `/etc/rsyslog.d/gce-syslog.conf`, after which rsyslog is restarted and setup syslog is captured.

State and dependencies: affects rsyslog routing and `/results` log collection. It is consumed by `gce-setup`.

Risks and test signals: a malformed single-line rsyslog rule can break log capture or rsyslog restart. Validation should run `rsyslogd -N1` in an appliance build and confirm `/results/syslog` content during shutdown.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-syslog.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gen-ssh-keys -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gen-ssh-keys

Purpose: generates missing SSH host keys according to `sshd_config`.

Important APIs/flow: `get_config_option` extracts case-insensitive `HostKey` values from `/etc/ssh/sshd_config`; `host_keys_required` returns configured paths or OpenSSH defaults; `create_key` conditionally runs `ssh-keygen` for a requested file if it is required and absent, restores SELinux context if `restorecon` exists, and prints fingerprint; `create_keys` covers RSA, DSA, ECDSA, and ED25519.

State and dependencies: writes `/etc/ssh/ssh_host_*` private/public keys. Depends on Perl, `ssh-keygen`, optional `restorecon`, and OpenSSH config format.

Integration points: enabled as `gen-ssh-keys.service` by appliance image build scripts so cloned images do not share host keys.

Risks and test signals: parser is simple and may not handle all sshd include semantics. DSA key generation may be undesirable on modern systems but only occurs if required. Tests should remove keys in a disposable root and verify configured/default key creation.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gen-ssh-keys -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/get-check-failures.sed -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/get-check-failures.sed

Purpose: sed script used during shutdown to extract per-test failure blocks from `runtests.log`.

Important behavior: invoked as `sed -n -f /usr/local/lib/get-check-failures.sed < /results/runtests.log` by `gce-shutdown`. The script is intentionally tiny and acts as part of the failure summary pipeline.

State and dependencies: no state; depends on xfstests log markers such as `BEGIN`, `END`, and failure output shapes.

Integration points: feeds `/results/failures`, which is included in result tarballs and email summaries.

Risks and test signals: if xfstests log format changes, failure extraction can miss relevant context. Regression tests should run the sed script against representative passing, failing, and interrupted logs.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/get-check-failures.sed -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/start-stress -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/start-stress

Purpose: starts background stress workload for the appliance.

Important flow: a small shell wrapper that launches `stress` with configured/default CPU, IO, VM, or disk pressure options and records/daemonizes it for test runs that request stress conditions.

State and dependencies: depends on the `stress` package installed by image builders and runtime environment variables or arguments. It may leave background processes that tests or shutdown must clean.

Integration points: xfstests configurations and hooks can use it to add load while tests run.

Risks and test signals: resource pressure can amplify flakiness or hide root causes. Tests should verify process launch, option propagation, and cleanup behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/start-stress -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/sbin/gce-shutdown -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/sbin/gce-shutdown

Purpose: finalizes a GCE test VM by summarizing results, sending emails, uploading result artifacts, cleaning Filestore state, running shutdown hooks, and deleting or powering off the instance.

Important flow: skip image-build instances; enforce singleton; handle self-shutdown marker; if results exist and shutdown reason is not abort, stop tests, append shutdown reason, copy xUnit results, handle timeout missing-END/error cases, generate xfstests or blktests summary/failures, optionally upload summary, choose report/failure/JUnit recipients from metadata, send SendGrid mail through `send-mail.py`, tar/xz `/results`, and upload results tarball and XML to GCS. Then remove Filestore per-instance directories and possibly delete Filestore, run shutdown hooks, log shutdown, and either power off or delete the VM.

State and dependencies: `/results`, `/tmp/results.xml`, GCS result objects, GCE metadata, Filestore directories, `/run` markers, SendGrid credentials, `gen_results_summary`, `gce-logger`, `gcs_cp`, and `gcloud`.

Integration points: LTM shards poll for result tarballs uploaded here. `gce-setup-filestore` writes parameters consumed here. `gce-logger` metadata updates help LTM monitoring.

Risks and test signals: shutdown is dense and mostly best-effort; failures late in upload/email can lose diagnostics. Regex summaries need maintenance with xfstests/blktests output changes. Integration tests should validate normal, timeout, abort, power-button, and Filestore cleanup paths.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/sbin/gce-shutdown -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/sbin/get-results -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/sbin/get-results

Purpose: extracts summary or failure lines from a result log.

Important flow: choose default summary regex or `--failures/-F` regex, read input files or stdin, grep selected lines, and in failure mode detect unmatched `BEGIN` without `END` to report a missing END for the last started test.

State and dependencies: no persistent state; depends on grep, shell, and xfstests log marker conventions.

Integration points: useful for local result inspection and overlaps with shutdown summary extraction.

Risks and test signals: regexes are shell variables and must track log formats. Failure mode reads the input multiple times, so stdin is not suitable there unless buffered externally. Tests should cover file input and interrupted test logs.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/sbin/get-results -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/sbin/pts-save -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/sbin/pts-save

Purpose: saves Phoronix Test Suite state and/or results from a GCE PTS instance back to GCS.

Important flow: source `gce-funcs`, parse flags such as `--state` and `--results`, package `/pts` or `/var/lib/phoronix-test-suite` content into `.tar.xz`, and upload to bucket names used by `gce-setup-pts` for later restoration.

State and dependencies: reads PTS data directories, writes temporary tarballs, uploads `pts-state.tar.xz`, `pts-results.tar.xz`, or per-instance result archives to `gs://$GS_BUCKET`. Depends on tar/xz and GCS helpers.

Integration points: paired with `gce-setup-pts`, which restores these archives at setup time.

Risks and test signals: large result archives can be expensive and partial uploads can leave stale state. Tests should validate flag selection and archive path compatibility with restore logic.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/sbin/pts-save -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/sbin/send-mail.py -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/sbin/send-mail.py

Purpose: command-line SendGrid mail sender used by shutdown scripts.

Important flow: parse options such as sender and subject, read message body from stdin, build a SendGrid email to one or more recipients, use `SENDGRID_API_KEY` from environment, send, and return an error on API failure.

State and dependencies: no persistent local state; depends on Python 3, SendGrid Python package installed by image build, and environment credentials.

Integration points: `gce-shutdown` invokes it for summary and JUnit emails because shutdown is shell-based while Go services use `util/email`.

Risks and test signals: mail body size can be large when full logs are sent. Credentials must be present in environment. Tests should mock SendGrid client and verify CLI argument parsing and stdin body handling.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/sbin/send-mail.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/sbin/ver -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/sbin/ver

Purpose: tiny helper for printing appliance or kernel version information.

Important behavior: two-line shell helper, likely used interactively or by scripts to show version state.

State and dependencies: no persistent state; depends on shell and whatever command it delegates to.

Integration points: operational convenience for test appliance debugging.

Risks and test signals: minimal risk; validation is simply that it executes in the appliance image and prints expected version output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/sbin/ver -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/gce-create-image -->
# sources/test-tools/xfstests-bld/test-appliance/gce-create-image

Purpose: host-side GCE image creation orchestrator. It stages appliance payloads in GCS, launches a temporary build VM with startup metadata, waits for the VM to shut itself down, and creates a reusable GCE image from the boot disk.

Important flow: source run-fstests config/image/arch helpers; require `GS_BUCKET`, `GCE_PROJECT`, and `GCE_ZONE`; parse arch, distro, datecode, root FS family, packages, and Phoronix version; select Debian suite/image/backport package variables; stage `xfstests.tar.gz`, templated `gce-xfstests-bld.sh`, `files.tar.gz`, and run-fstests helper payloads; update `git-versions`; sync create-image payloads and debs to GCS; delete old build instance/disk; create build VM with startup-script-url metadata; wait until the instance disappears; create an image from the preserved boot disk and list images.

State and dependencies: temporary directory under `/tmp`, GCS `create-image/` and `debs/`, temporary GCE instance/disk `xfstests-bld`, final image family/name, labels from git versions. Depends on gcloud wrappers, tar, gzip/pigz, sed templating, run-fstests utilities, and local build artifacts.

Integration points: feeds `gce-xfstests-bld.sh` as startup script and installs the files that become the test appliance.

Risks and test signals: destructive cleanup deletes same-named build instances/disks. Template substitution is sed-based and sensitive to special characters in package lists. End-to-end validation is a bootable image and successful appliance self-deletion.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/gce-create-image -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/gce-xfstests-bld.sh -->
# sources/test-tools/xfstests-bld/test-appliance/gce-xfstests-bld.sh

Purpose: startup script run inside the temporary GCE image-build VM to install packages, unpack appliance files, build Go servers, configure services, clean state, and preserve the boot disk for image creation.

Important flow: redirect output to `/image-build.log`; install Debian packages/backports and optional Phoronix; rewrite apt suite if metadata requests it; configure serial/telnet gettys; fetch staged tarballs from GCS; unpack xfstests and root files; install Python requirements and drgn; configure lighttpd, test config, result directories, LVM discard, fsgqa users, systemd services, tmp mount, NFS service defaults, custom debs, gcloud components, and Go toolchain; build KCS and LTM binaries into `/usr/local/lib/bin`; label root filesystem, remove caches/SSH host keys, fstrim, and delete the build instance keeping boot disk.

State and dependencies: modifies the entire root filesystem of the build VM; uses metadata placeholders filled by `gce-create-image`; depends on apt, curl, gcloud storage, Go download, systemd, pip, tar, and xfstests-bld payloads.

Integration points: creates the runtime environment consumed by every GCE appliance script and Go server in this subset.

Risks and test signals: hardcoded Go version must be available for architecture. PEP 668 override and package names vary by Debian suite. The script deletes SSH host keys for later regeneration. Validation is image boot, service enablement, Go binary existence, and successful `gce-load-kernel`/`gce-setup` path on instances.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/gce-xfstests-bld.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/gen-image -->
# sources/test-tools/xfstests-bld/test-appliance/gen-image

Purpose: local root filesystem/image builder for the xfstests appliance, using debootstrap and optional fakechroot/fakeroot.

Important flow: parse output tar/image/update/resume/suite/mirror/networking/drgn/log/source-date/package options; choose suite from build metadata; optionally re-exec under `script`, fakechroot, or fakeroot; compute package list; define helpers for staging xfstests, symlink repair, final qcow2 conversion, cleanup, chroot execution, and abort cleanup. It formats/mounts a raw ext4 image unless fakechroot, binds apt/deb caches, runs debootstrap and optional second stage for foreign chroots, installs backports/manual debs, copies xfstests appliance files, creates device/mount directories and fsgqa users, configures systemd gettys/services, prunes docs/logs, handles fakechroot device nodes, optionally installs drgn, emits a deterministic tarball, converts raw to qcow2, and cleans.

State and dependencies: `rootdir`, raw/qcow2 images, apt cache directories, `debs`, `var.cache.apt.archives`, `var.lib.apt.lists`, and output tar/image. Depends on root privileges or fakechroot, debootstrap, qemu-img, mke2fs/e2fsck, chroot, tar, and systemd files inside rootfs.

Integration points: non-GCE image path parallel to `gce-create-image`; shares appliance `files/` payload and xfstests tarball.

Risks and test signals: cleanup uses mounts and can leave loop/bind mounts on interruption. Fakechroot handling is complex. Resume stages require operator accuracy. Tests should validate generated tar/image bootability and idempotent cleanup after failures.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/gen-image -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/get-backports-pkgs -->
# sources/test-tools/xfstests-bld/test-appliance/get-backports-pkgs

Purpose: cut-down debootstrap-based downloader for Debian backport packages into a target root.

Important flow: set suite to `<arg>-backports`, target to second argument, load debootstrap functions and suite script, read package list from `backport-packages-<suite>`, configure checksum variables, redirect debootstrap logs to `$TARGET/debootstrap/debootstrap.log`, then call `download_indices` and `download`.

State and dependencies: writes `$TARGET/debootstrap` metadata and downloaded deb paths. Depends on installed debootstrap internals, package lists, Debian mirror, `pkgdetails`, and checksums.

Integration points: `gen-image` uses it at stage 5 to download and install backports into the rootfs.

Risks and test signals: tightly coupled to debootstrap implementation and script variables. Missing package list or suite script aborts. Tests should run in a temporary target and verify `debpaths` for expected backport package names.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/get-backports-pkgs -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/run-chroot -->
# sources/test-tools/xfstests-bld/test-appliance/run-chroot

Purpose: convenience helper to enter the generated `rootdir` chroot.

Important flow: set `ROOTDIR=$(pwd)/rootdir`, mount proc and sysfs into it, copy `/proc/mounts` to `etc/mtab`, `cd` into rootdir, run `chroot $ROOTDIR /bin/bash`, then unmount proc and sysfs.

State and dependencies: transient mounts under `rootdir/proc` and `rootdir/sys`; modifies `rootdir/etc/mtab`. Requires root privileges and a valid rootdir.

Integration points: useful for debugging `gen-image` output between stages.

Risks and test signals: if the chroot shell exits abnormally or the script is interrupted, mounts may remain. Tests are manual: enter/exit chroot and confirm mounts unmount cleanly.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/run-chroot -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/syz/001 -->
# sources/test-tools/xfstests-bld/test-appliance/syz/001

Purpose: xfstests test case wrapper for a syzkaller reproducer named `001`.

Important flow: set standard xfstests variables, source `common/rc` and `common/filter`, install cleanup trap, require generic Linux scratch support, mount scratch, cd to scratch mount, then run either an executable reproducer `$here/$seqfull.exe` with 60-second timeout or a `.syz` program via `run-syz`; otherwise `_notrun`.

State and dependencies: writes `$RESULT_DIR/001` and `.full`, uses scratch filesystem, temp files, and xfstests status conventions. Depends on `syz-execprog` or executable reproducer.

Integration points: listed in `syz/group` and can be run by xfstests harness as group `syz`.

Risks and test signals: `seqfull=$0` means paths can include directories; the executable lookup uses `$here/$seqfull.exe`. Repro timeout kills the process but kernel side effects may persist. Test signal is harness pass/notrun/failure and `.full` output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/syz/001 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/syz/group -->
# sources/test-tools/xfstests-bld/test-appliance/syz/group

Purpose: xfstests group file registering syzkaller reproducer test `001`.

Important behavior: contains `001 syz`, placing test 001 in the `syz` group.

State and dependencies: no runtime state; consumed by xfstests group selection.

Integration points: lets `./check -g syz` or equivalent run the syzkaller wrapper.

Risks and test signals: group membership is minimal. Validation is that xfstests discovers `syz/001` when selecting group `syz`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/syz/group -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/syz/repro -->
# sources/test-tools/xfstests-bld/test-appliance/syz/repro

Purpose: generic/template xfstests wrapper for a syzkaller reproducer named by the invoked script path.

Important flow: identical to `syz/001`: source xfstests common helpers, require scratch, mount scratch, run `$seqfull.exe` with timeout or `$seqfull.syz` through `run-syz`, otherwise `_notrun`.

State and dependencies: writes result files for the invoked sequence, uses scratch mount, and requires syzkaller executor for `.syz` inputs.

Integration points: can be copied or symlinked for new syzkaller repro cases.

Risks and test signals: path-derived `seq` and `seqfull` must match reproducer file naming. Kernel crashes or hangs are expected signals for repro tests, so harness and LTM timeout handling are important.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/syz/repro -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/common/Makefile -->
# sources/test-tools/xfstests/common/Makefile

Purpose: build/install rules for xfstests common helper files.

Important flow: include top-level `include/builddefs` and `$(BUILDRULES)`, set `COMMON_DIR=common`, and define `install` to create `$(PKG_LIB_DIR)/common` and install all files with mode 644. `install-dev` and `install-lib` are empty.

State and dependencies: installation copies common helper scripts into package library directory. Depends on xfstests build system variables and `$(INSTALL)`.

Integration points: makes common shell libraries available to installed tests.

Risks and test signals: installs every file in `common` as non-executable 0644, appropriate for sourced helper files but wrong if an executable lands there. Build tests should verify package contents and modes.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/common/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/common/config -->
# sources/test-tools/xfstests/common/config

Purpose: core xfstests configuration loader. It sets tool paths, defaults, filesystem-specific mount/mkfs/fsck options, host config section parsing, device validation, overlay overrides, and canonicalization.

Important APIs/flow: exports common environment (`LANG=C`, `HOST`, `CHECK_OPTIONS`, stress factors, debugfs, overlay constants, fsck codes); resolves dozens of program paths (`mkfs`, `mount`, xfs/e2fs/btrfs/f2fs tools, fio, dmsetup, fsverity, etc.); defines `set_mkfs_prog_path_with_opts`, `_common_mount_opts`, `_mount_opts`, `_test_mount_opts`, `_mkfs_opts`, `_fsck_opts`, `_source_specific_fs`, `known_hosts`, `get_config_sections`, `_check_device`, `_canonicalize_mountpoint`, `_canonicalize_devices`, overlay override/restore helpers, `parse_config_section`, and `get_next_config`.

State and persistence: sources host config once or by section; exports `CONFIG_INCLUDED`, `HOST_OPTIONS_SECTIONS`, `OPTIONS_HAVE_SECTIONS`, `FSTYP`, device paths, mount/mkfs/fsck options, and overlay/base variables. It may canonicalize symlink devices and derive `SCRATCH_DEV` from `SCRATCH_DEV_POOL`.

Dependencies and integration: sourced by xfstests `common/rc` and many tests. It depends on Linux, block devices or network fs syntaxes, optional filesystem-specific common files, and many userland tools.

Risks and test signals: this file is central and highly stateful; re-sourcing behavior differs between sectioned and non-sectioned configs. Overlay overrides intentionally mutate `FSTYP`, `TEST_DEV`, `SCRATCH_DEV`, and mount points. Device validation is filesystem-specific. Test signals include running `./check` across sectioned configs, overlay configs, btrfs pools, tmpfs, and missing-tool scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/common/config -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/common/dmdust -->
# sources/test-tools/xfstests/common/dmdust

Purpose: common xfstests helpers for device-mapper dust fault-injection devices.

Important APIs: exports `DUST_NAME="dust-test.$seq"` and defines `_init_dust`, `_mount_dust`, `_unmount_dust`, and `_cleanup_dust`.

Control flow: `_init_dust` gets scratch device sector count, builds a dust table mapping the scratch device with 512-byte sector size, and creates `/dev/mapper/$DUST_NAME` through `_dmsetup_create`. `_mount_dust` computes scratch mount options and mounts `$DUST_DEV` at `$SCRATCH_MNT`. `_cleanup_dust` resumes the mapper in case a load failed, unmounts scratch best-effort, and removes the mapper.

State and dependencies: creates a device-mapper target and mounts it. Depends on `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$FSTYP`, dmsetup helpers from other common files, and mount/unmount wrappers.

Integration points: tests can source this helper to inject read/write dust behavior on scratch filesystems.

Risks and test signals: cleanup must run even after partial setup to avoid hung unmounts. Device-mapper target availability is required. Tests should validate mapper creation/removal and cleanup after simulated load failure.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/common/dmdust -->
