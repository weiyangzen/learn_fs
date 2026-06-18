# subset-b-009779 Research

Grouped research report for the requested rclone fstest/testserver/lib subset. Each section preserves the source path in its title and is bounded by reconciliation markers for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/fstests/fstests.go -->
# sources/user-network-fs/rclone/fstest/fstests/fstests.go

Purpose: package `fstests` is rclone's generic backend integration-test suite for `fs.Fs`, `fs.Object`, and `fs.Directory` behavior. It is intended to be imported by backend tests and exercises the common contract that every backend should meet: remote creation/removal, listings, object reads/writes, metadata, modtimes, optional feature methods, wrapper completeness, chunked uploads, bucket edge cases, and shutdown behavior.

Important APIs/types/functions: `InternalTester` lets a backend add backend-specific checks. `ChunkedUploadConfig`, `SetUploadChunkSizer`, `SetUploadCutoffer`, and `SetCopyCutoffer` provide test-only tuning hooks for multipart upload/copy sizing. `NextPowerOfTwo`, `NextMultipleOf`, `PutTestContentsMetadata`, `PutTestContents`, `TestPutLarge`, `TestPutLargeStreamed`, and `ReadObject` are reusable helpers. `Opt` carries backend-specific skips and capability settings. The central API is `Run(t, opt)`.

Control flow: `Run` initializes fstest config, optionally starts a `testserver`, creates a randomized remote via `fs.NewFs`, then builds a deeply nested `t.Run` tree. Early tests validate core `Fs` identity and empty directory behavior; nested tests create directories and objects before exercising list, copy, move, purge, object metadata, public links, tiering, bucket-based path edge cases, stream/unknown-size upload, directory metadata, and final purge. Tests frequently skip based on `fs.Features()` capabilities rather than failing unsupported optional interfaces.

State/persistence: the suite creates temporary remote trees and local state, writes random test objects, changes global config flags such as `Metadata` and `UseListR` in scoped contexts, and stores `InternalTestFiles` for backend-specific internal tests. Cleanup purges the remote at the end and removes local temp directories for local remotes. Eventual consistency is handled with retries and listing retry flags.

Dependencies/integration: heavily integrated with `github.com/rclone/rclone/fs`, `cache`, `config`, `fspath`, `hash`, `object`, `operations`, `walk`, `fstest`, and `testserver`. It relies on `testify` assertions, random content generation, rclone encoders, and fs feature flags as the negotiated capability contract.

Risks: because this file mutates live remotes, failures can leave remote objects behind if cleanup is interrupted. Tests involving public links, metadata, directory modtimes, chunked uploads, and change notification are backend-sensitive and can be flaky under eventual consistency. Several skips and backend-specific bypasses indicate known feature gaps. A duplicated `unwrappableFsMethods` initializer appears in the read source and should be checked if compiling this exact tree.

Test signals: the file is itself a test harness; success means a backend satisfies broad rclone interface semantics. Failures are intentionally granular through nested test names such as `FsMkdir/FsPutFiles/ObjectOpenRange`, which feed the retry/re-run machinery in `fstest/runs`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/fstests/fstests.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/mockdir/dir.go -->
# sources/user-network-fs/rclone/fstest/mockdir/dir.go

Purpose: package `mockdir` provides the smallest useful `fs.Directory` test double. Its only public API is `New(name string) fs.Directory`, which returns `fs.NewDir(name, time.Time{})`.

Important APIs/types/functions: `New` is the complete surface. It preserves the remote name and uses the zero time as directory modtime, leaving richer metadata behavior to callers or other mocks.

Control flow: there is no branching beyond constructing and returning the directory value.

State/persistence: no package state and no persistence. Each call returns an independent directory object.

Dependencies/integration: depends on rclone `fs.NewDir` and Go `time`. It integrates with tests that need directory entries in `fs.DirEntries` without standing up a backend.

Risks: zero modtime may be unsuitable for tests that assert directory timestamp behavior. It does not exercise optional directory metadata or set-modtime interfaces.

Test signals: no local tests in this file; correctness is indirectly signaled by tests that consume mock directory entries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/mockdir/dir.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/mockfs/mockfs.go -->
# sources/user-network-fs/rclone/fstest/mockfs/mockfs.go

Purpose: package `mockfs` defines a minimal in-memory `fs.Fs` implementation for unit tests that need a registered rclone backend-like object without remote I/O.

Important APIs/types/functions: `Register` registers backend name `mockfs` with one required `potato` option. `Fs` stores `name`, `root`, filled `features`, a root-only `fs.DirEntries` listing, and supported `hash.Set`. `NewFs` constructs it. `AddObject`, `SetHashes`, `List`, and `NewObject` are the functional test hooks. `Put`, `Mkdir`, and `Rmdir` deliberately return `ErrNotImplemented`.

Control flow: `NewFs` fills features from the concrete object. `AddObject` appends to `rootDir` and calls a test-only `SetFs(fs.Fs)` method on the object if present. `List` only succeeds for root. `NewObject` only searches objects directly under root and returns `fs.ErrorObjectNotFound` otherwise.

State/persistence: all state is process-local memory on the `Fs` instance. There is no locking; callers should treat it as a simple single-test fixture.

Dependencies/integration: uses rclone `fs`, `configmap`, and `hash`. It pairs naturally with `mockobject.ContentMockObject`, which can accept the owning Fs through `SetFs`.

Risks: root-only behavior and unimplemented mutations mean it is not a full fake backend. Type assertion in `NewObject` assumes matching entries are `fs.Object`, not directories.

Test signals: compile-time assertion `var _ fs.Fs = (*Fs)(nil)` verifies interface completeness for core methods; behavior is validated indirectly by unit tests using this mock.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/mockfs/mockfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/mockobject/mockobject.go -->
# sources/user-network-fs/rclone/fstest/mockobject/mockobject.go

Purpose: package `mockobject` supplies lightweight `fs.Object` implementations for tests: a bare path-only object and a content-backed object with optional seek behavior.

Important APIs/types/functions: `Object` is a string-backed `fs.Object`; `New` constructs it. Most mutation/read methods on bare `Object` return `errNotImpl`. `SeekMode` selects no seek, `io.Seeker`, or rclone `RangeSeek` support. `ContentMockObject` adds `content`, `seekMode`, optional owning `fs.Fs`, unknown-size mode, and modtime. Public methods include `WithContent`, `SetFs`, `SetUnknownSize`, `Open`, `Size`, `Hash`, `ModTime`, and `SetModTime`.

Control flow: `Open` decodes `fs.SeekOption` and `fs.RangeOption`, rejects unsupported mandatory options, slices or seeks into a `bytes.Reader`, and wraps it in the requested closer type. `Hash` builds a one-hash multihasher and returns the digest for the requested hash.

State/persistence: all object data is in memory. `SetModTime`, `SetFs`, and `SetUnknownSize` mutate the mock object instance.

Dependencies/integration: integrated with rclone `fs.OpenOption`, `RangeOption`, `SeekOption`, `RangeSeek`, and `hash`. It is often used with `mockfs.AddObject`.

Risks: no bounds checks are added beyond Go slicing behavior, so invalid seek/range combinations can panic if callers pass impossible offsets. Bare `Object` has zero size and no content, so tests must choose `WithContent` when reads matter.

Test signals: no direct tests here, but it is a focused utility for testing object consumers against seek/range/unknown-size permutations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/mockobject/mockobject.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/run.go -->
# sources/user-network-fs/rclone/fstest/run.go

Purpose: package `fstest`'s `run.go` provides reusable integration-test setup and teardown for tests that need paired local and remote rclone filesystems.

Important APIs/types/functions: `Run` holds `LocalName`, `Flocal`, `Fremote`, `FremoteName`, precision, cleanup hooks, mkdir cache, and logging callbacks. `TestMain`, `ResetRun`, `NewRun`, `NewRunIndividual`, `Retry`, `WriteFile`, `WriteObjectTo`, `WriteObject`, `WriteUncheckedObject`, `WriteBoth`, listing/check helpers, `CheckDirectoryModTimes`, and `Finalise` are the main APIs.

Control flow: `TestMain` parses flags and either creates one shared run or leaves individual tests to call `NewRunIndividual`. `newRun` initializes fstest, creates a random remote plus a local temp Fs, and computes modify-window precision. Shared-run tests override cleanup to remove all remote entries between tests. Write helpers ensure remote mkdir, compute hashes, retry retriable upload errors, and create matching `Item` records.

State/persistence: uses global `oneRun`, command-line flags, local temp directories, remote random directories, and rclone cache state. Cleanup removes local temp paths, clears cache, and either purges per-test remotes or empties the shared remote.

Dependencies/integration: integrates with `fs`, `cache`, `fserrors`, `hash`, `object`, `walk`, `lib/file`, and `testify`. It is a foundational helper for rclone integration tests outside the generic `fstests.Run` harness.

Risks: shared mode requires robust cleanup; interrupted runs can leave remote data. `Finalise` assumes `cleanRemote` is valid, so partially constructed runs need care. `Retry` only handles caller-provided errors and cannot make non-idempotent writes safe by itself.

Test signals: this file supports tests rather than containing assertions. Its behavior is exercised across rclone integration suites that call `fstest.NewRun`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/run.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/runs/config.go -->
# sources/user-network-fs/rclone/fstest/runs/config.go

Purpose: package `runs` config handling converts YAML test/backends matrices into executable `Run` records for `fstest/test_all`.

Important APIs/types/functions: `Test` describes a Go test package path and package-level flags. `Backend` describes a configured remote, backend name, feature flags, ignored tests, retry settings, extra timeout, and environment. `Config` groups tests and backends. Key methods are `Backend.includeTest`, `Backend.MakeRuns`, `NewConfig`, `Config.MakeRuns`, `FilterBackendsByRemotes`, `FilterBackendsByBackends`, and `FilterTests`.

Control flow: `NewConfig` reads and YAML-unmarshals the config. `Config.MakeRuns` computes the Cartesian product of included backends and tests. `Backend.MakeRuns` expands fast-list variants, parses `MaxFile`, applies `LocalOnly`, attaches ignore maps/env/list retry settings, and optionally appends backend name to the package path.

State/persistence: no persistent state; it reads a YAML file and mutates in-memory `Config` slices during filters.

Dependencies/integration: depends on rclone `fs.ConfigFs` to synthesize backend records for explicit remotes absent from YAML, `fs.SizeSuffix` for max file parsing, and `gopkg.in/yaml.v3`.

Risks: unknown filter names silently drop tests/backends except for remote synthesis; invalid `maxfile` logs but leaves size limit zero. Backend/test names must match source package paths exactly.

Test signals: exercised by `test_all` and indirectly by run reports; no direct unit tests in this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/runs/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/runs/report.go -->
# sources/user-network-fs/rclone/fstest/runs/report.go

Purpose: `report.go` builds summaries for a `test_all` run, including log directory setup, pass/fail grouping, JSON, HTML, optional email, and optional rclone upload.

Important APIs/types/functions: `Report` stores run metadata, start/duration, passed/failed runs, version, branch/commit, and output URLs. `ReportRun` feeds the HTML template. Main functions/methods are `NewReport`, `gitBranchAndCommit`, `End`, `AllPassed`, `RecordResult`, `Title`, `LogSummary`, `LogJSON`, `LogHTML`, `EmailHTML`, `uploadTo`, and `Upload`.

Control flow: `NewReport` discovers the previous output directory, creates a dated log directory, forms a public URL, and probes git. Completed runs are recorded as passed or failed, then `End` sorts/group them. Logging methods emit console summary, `index.json`, and `index.html`; side-effect methods shell out to `mail` or `rclone sync` when configured.

State/persistence: writes dated directories under `RunOpt.OutputDir`, plus `index.json` and `index.html`. `Upload` mirrors that directory to a configured remote path and a `current` alias.

Dependencies/integration: uses rclone `fs` logging/version, `lib/file`, Go templates/JSON, `git`, `mail`, `rclone`, and `open.Start` for local browser opening.

Risks: `LogHTML` opens a browser as a side effect, which is undesirable in headless automation. `EmailHTML` and `Upload` fatal on command failure. Previous-run detection simply uses the last directory entry without sorting.

Test signals: no direct tests; report correctness is visible through generated HTML/JSON and `test_all` exit behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/runs/report.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/runs/run.go -->
# sources/user-network-fs/rclone/fstest/runs/run.go

Purpose: `run.go` executes one configured integration-test command, optionally retries failing leaf tests, and feeds results back to `test_all`.

Important APIs/types/functions: `RunOpt` carries global execution flags. `Run` stores backend/remote/package config plus command, trial, output, failed tests, and log names. `Runs` implements sorting. Helpers include `testsToRegexp`, `findFailures`, `nextCmdLine`, `trial`, `GOPATH`, binary path/name helpers, `MakeTestBinary`, `RemoveTestBinary`, `Init`, `Logs`, `FailedTestsCSV`, `Run`, and `toShell`.

Control flow: `Run.Init` builds either `go test` or precompiled test-binary argv with timeout, remote, verbosity, fast-list, short, size-limit, and run regexp. `trial` starts a testserver for the remote, runs the command in the test package directory, tees output to a log and buffer, parses failures, and marks pass/fail. `Run` repeats trials up to `MaxTries`, narrowing retries to failed leaf tests with `-test.run`.

State/persistence: writes per-trial logs into the report log directory and may build/delete `.test` binaries in package directories. It uses global `oneOnly` mutexes for backends marked exclusive.

Dependencies/integration: integrates with `testserver.Start`, Go `exec`, rclone logging/config, and package paths from `runs.Config`. Failure parsing relies on standard `go test -v` output.

Risks: regex parsing can miss non-standard failure output or setup failures without `--- FAIL` lines. `toShell` is for display only and quotes minimally. Precompiled binaries modify source package directories during the run.

Test signals: paired with `run_test.go`, especially for retry regexp construction and live `go test -run` selection behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/runs/run.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/runs/run_test.go -->
# sources/user-network-fs/rclone/fstest/runs/run_test.go

Purpose: unit tests verify the retry-selection regexp generated by `testsToRegexp`.

Important APIs/types/functions: `TestTestsToRegexp` checks expected regex strings for flat and nested test names. `TestTestsToRegexpLive` executes `go test -v -run <regexp>` against local nested `TestTests` to ensure Go actually selects the intended parent/child tests. `runRe` parses `=== RUN` lines; `nilTest` provides no-op leaves.

Control flow: table-driven tests call `testsToRegexp`, compare strings, then run a live subprocess and compare observed run names.

State/persistence: no persistent state; it spawns `go test` in the current package.

Dependencies/integration: uses `exec.Command`, regex parsing, and `testify`. It directly protects the retry behavior in `runs.Run.findFailures`.

Risks: live subprocess tests depend on the local Go tool and package layout. Expected string ordering is tied to deterministic sorting in trie matching.

Test signals: strong focused coverage for nested retry regexp behavior, which is critical for reducing flaky integration reruns to failing leaves.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/runs/run_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/test_all/clean.go -->
# sources/user-network-fs/rclone/fstest/test_all/clean.go

Purpose: cleanup support for `test_all -clean`, removing leftover randomized integration-test directories from configured remotes.

Important APIs/types/functions: `MatchTestRemote` identifies names like `rclone-test-<random>` plus optional `_segments`. `cleanFs` optionally runs backend cleanup, lists top-level directories, and purges matching test dirs. `cleanRemotes` iterates configured backends.

Control flow: `cleanFs` opens the remote, optionally calls `operations.CleanUp`, lists sorted directories, joins remote root and directory path, and purges each matching directory unless dry-run is set. Errors are logged and the last cleanup/purge error is returned.

State/persistence: mutates external remotes by deleting test directories. It does not edit local files except through logging.

Dependencies/integration: uses rclone `fs`, `fspath`, `list`, `operations`, and `runs.Config`. The regex is copied from fstest naming to avoid importing extra flags.

Risks: cleanup is intentionally destructive for names matching the test pattern. If a user has real data matching that pattern in a configured remote root, it can be purged. Listing failures abort the remote cleanup.

Test signals: no direct tests here; dry-run logging and integration cleanup outcomes are the main operational signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/test_all/clean.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/test_all/config.yaml -->
# sources/user-network-fs/rclone/fstest/test_all/config.yaml

Purpose: YAML matrix defining which rclone package tests run against which configured test remotes.

Important APIs/types/functions: top-level `tests` entries define package paths and flags such as `addbackend`, `nobinary`, `short`, `fastlist`, and `localonly`. `backends` entries map backend names to remotes and tune `fastlist`, `listretries`, `maxfile`, `extratime`, `oneonly`, `cleanup`, `env`, `tests`, `ignore`, and `ignoretests`.

Control flow: consumed by `runs.NewConfig` and expanded by `Config.MakeRuns`. `addbackend` makes the generic `backend` test path backend-specific. Backend `ignore` entries suppress known failing test names during retry/failure parsing; `ignoretests` prevents entire packages from running for a backend.

State/persistence: declarative only. It references external remotes, local Docker-backed remotes, and environment paths such as Kerberos config/ccache files.

Dependencies/integration: integrates with the rclone config file and the `fstest/testserver/init.d` scripts for names like `TestS3Minio`, `TestSFTPOpenssh`, `TestSMBKerberos`, `TestHdfs`, and WebDAV/Seafile servers.

Risks: stale ignore entries can hide regressions, while missing ignores can cause persistent known failures. Remote credentials/config must exist outside this file. Some commented entries document unavailable accounts or high rate-limit risk.

Test signals: this file is the authoritative signal for the intended integration-test coverage breadth and backend-specific exception policy.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/test_all/config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/test_all/test_all.go -->
# sources/user-network-fs/rclone/fstest/test_all/test_all.go

Purpose: command `test_all` is rclone's integration-test runner across configured remotes and packages.

Important APIs/types/functions: global `Opt *runs.RunOpt` is populated by flags in `init`. `main` loads config, filters by requested remotes/backends/tests, optionally cleans, builds test binaries, runs tests concurrently, records results, and emits reports.

Control flow: after flag parsing and config install, CSV parsing handles remote names with commas. Test runs are shuffled, a `runs.Report` is created, one binary per package is built unless disabled, and goroutines execute `run.Run` behind a token dispenser bounded by `-n`. Results are gathered, summarized, written to JSON/HTML, optionally emailed/uploaded, and nonzero exit is used if any run failed.

State/persistence: writes report/log output under `-output`, may build/delete test binaries in source directories, sets `RCLONE_CACHE_DB_WAIT_TIME`, starts test servers, and registers `testserver.CleanupAll` with `atexit`.

Dependencies/integration: imports all backends, configfile installer, `runs`, `testserver`, `atexit`, and `pacer`.

Risks: high concurrency can stress remote APIs or local Docker. `LogHTML` browser opening is inherited from report generation. Interrupt handling depends on `atexit` to stop test servers.

Test signals: exit status plus generated report files are the primary signals. Per-run logs preserve exact command output for triage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/test_all/test_all.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/Dockerfile -->
# sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/Dockerfile

Purpose: builds a minimal Debian-based HDFS Docker image for rclone HDFS integration tests, with optional Kerberos support.

Important APIs/types/functions: installs OpenJDK 8, curl, Python, Kerberos KDC/admin packages; downloads Hadoop 3.2.1; configures `JAVA_HOME`, `HADOOP_HOME`, `HADOOP_CONF_DIR`, `PATH`, and Hadoop data/name directories; adds Hadoop XML configs, Kerberos configs, ACL, and `run.sh`.

Control flow: package install, Hadoop download/extract, symlink `/etc/hadoop`, create data/log directories, copy configs, make `run.sh` executable, and set it as `CMD`.

State/persistence: image contains Hadoop under `/opt`, configs under `/etc`, and runtime data directories under `/hadoop*`. Containers started from it format namenode state at runtime.

Dependencies/integration: used by `init.d/TestHdfs`, which runs image `rclone/test-hdfs` and maps HDFS/Kerberos ports.

Risks: Debian stretch and Hadoop 3.2.1 are old; download URL availability and image rebuild reliability are external dependencies. Embedded test Kerberos realm is intentionally insecure and local-only.

Test signals: successful container startup exposes namenode `127.0.0.1:8020` and optional KDC state for HDFS backend tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/core-site.xml -->
# sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/core-site.xml

Purpose: Hadoop core-site configuration for the HDFS test image.

Important APIs/types/functions: sets `fs.defaultFS` to `hdfs://localhost:8020`, configures static HTTP user/proxy settings for root, and includes a Kerberos block enabling authentication, authorization, RPC integrity, and static user group mapping.

Control flow: declarative XML consumed by Hadoop at startup. `run.sh` removes the Kerberos-marked block when `KERBEROS=false`.

State/persistence: no direct state; controls Hadoop process behavior in the container.

Dependencies/integration: copied by the Dockerfile into `/etc/hadoop/core-site.xml`; paired with `hdfs-site.xml` and `krb5.conf`.

Risks: permissive proxy host setting and static mapping are test-only. Kerberos markers must remain intact for `sed` removal to work.

Test signals: correct config lets rclone HDFS tests connect to the local namenode with or without Kerberos.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/core-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/hdfs-site.xml -->
# sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/hdfs-site.xml

Purpose: HDFS service configuration for the test image's single-container namenode/datanode setup.

Important APIs/types/functions: configures hostname usage, name/data directories, bind hosts, access-time precision, replication factor, safemode timing, and Kerberos principals/keytabs/data-transfer encryption within marker comments.

Control flow: declarative XML. The Kerberos block is removed by `run.sh` when not running Kerberos tests.

State/persistence: points namenode data to `/hadoop/dfs/name` and datanode data to `/hadoop/dfs/data`, which are container-local unless volumes are added.

Dependencies/integration: used by Hadoop daemons launched in `run.sh`; ports are exposed by `TestHdfs`.

Risks: replication is set to `2` in a one-container test environment, which may rely on pseudo/distributed behavior and could affect health timing. Encryption settings use test-compatible values.

Test signals: successful HDFS startup and readable/writable remote through rclone validate this configuration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/hdfs-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/httpfs-site.xml -->
# sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/httpfs-site.xml

Purpose: placeholder Hadoop HttpFS configuration for the HDFS test image.

Important APIs/types/functions: contains an empty `<configuration>` element.

Control flow: loaded passively if HttpFS components look for it; no properties alter behavior.

State/persistence: no state.

Dependencies/integration: copied into `/etc/hadoop/httpfs-site.xml` by the Dockerfile to satisfy expected Hadoop config file presence.

Risks: empty config means any HttpFS-specific behavior is default-only; this image primarily tests native HDFS access.

Test signals: absence of errors from Hadoop config loading is the only signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/httpfs-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/kdc.conf -->
# sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/kdc.conf

Purpose: minimal Kerberos KDC realm configuration for HDFS Kerberos integration tests.

Important APIs/types/functions: defines realm `KERBEROS.RCLONE` and points `acl_file` to `/etc/krb5kdc/kadm5.acl`.

Control flow: read by Kerberos KDC services when `run.sh` enables Kerberos setup.

State/persistence: KDC database is created at container runtime with `kdb5_util`; this file only defines realm metadata.

Dependencies/integration: Dockerfile installs it under `/etc/krb5kdc/`; `run.sh` creates principals and keytabs for HDFS and HTTP services.

Risks: test realm has hard-coded local settings and is not production-secure.

Test signals: successful KDC restart and principal creation in `run.sh` indicate the file is usable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/kdc.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/kms-site.xml -->
# sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/kms-site.xml

Purpose: placeholder Hadoop KMS configuration in the HDFS test image.

Important APIs/types/functions: empty `<configuration>` element.

Control flow: passive config file; no KMS properties are set.

State/persistence: none.

Dependencies/integration: copied to `/etc/hadoop/kms-site.xml` so Hadoop config paths are complete.

Risks: tests do not exercise a customized Hadoop KMS through this file.

Test signals: only config-load success.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/kms-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/krb5.conf -->
# sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/krb5.conf

Purpose: client Kerberos configuration for the HDFS test image.

Important APIs/types/functions: sets default realm `KERBEROS.RCLONE`, disables DNS realm/KDC lookup, enables forwardable/proxiable tickets, and maps the realm to KDC `localhost`.

Control flow: read by Kerberos tools and Hadoop when `KERBEROS=true`.

State/persistence: no state; tickets are generated separately by `kinit` in `run.sh`.

Dependencies/integration: installed into `/etc/krb5.conf`; works with `kdc.conf` and generated principals.

Risks: localhost KDC assumption is specific to single-container tests.

Test signals: `kinit user` and `klist` in `run.sh` validate this client config.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/krb5.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/mapred-site.xml -->
# sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/mapred-site.xml

Purpose: minimal MapReduce/YARN configuration for the HDFS image.

Important APIs/types/functions: sets `mapreduce.framework.name` to `yarn` and binds the node manager to `0.0.0.0`.

Control flow: declarative Hadoop config.

State/persistence: none.

Dependencies/integration: copied into `/etc/hadoop` with other configs, although rclone HDFS tests mainly require HDFS daemons.

Risks: minimal YARN config may not be enough for real MapReduce workloads; it is test-image support only.

Test signals: absence of Hadoop config errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/mapred-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/run.sh -->
# sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/run.sh

Purpose: container entrypoint for the HDFS test image.

Important APIs/types/functions: reads `KERBEROS` env flag; when true it creates a Kerberos database, admin/user principals, HDFS/HTTP service principals, keytab, starts KDC, and obtains a user ticket. When false it removes Kerberos-marked config blocks from core/hdfs site files. It then formats the namenode and launches namenode and datanode.

Control flow: Kerberos conditional setup, config mutation, `hdfs namenode -format test`, background namenode/datanode, then `exec sleep infinity` to keep the container alive.

State/persistence: mutates config files in-place, creates Kerberos DB/keytab/ticket cache, and initializes HDFS data directories in the container.

Dependencies/integration: invoked by Docker `CMD`; `TestHdfs` maps ports and may copy the Kerberos ccache from the container.

Risks: fixed passwords and repeated namenode formatting are appropriate only for disposable containers. A fixed sleep/daemon startup model can be timing-sensitive.

Test signals: exposed HDFS port accepts connections; with Kerberos, copied ticket cache enables authenticated rclone HDFS access.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/yarn-site.xml -->
# sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/yarn-site.xml

Purpose: YARN timeline/logging configuration included in the HDFS test image.

Important APIs/types/functions: enables log aggregation and timeline service, configures shuffle service, binds node manager/timeline service to all interfaces, and sets remote app log/timeline paths.

Control flow: declarative XML consumed by Hadoop/YARN services.

State/persistence: refers to `/app-logs` and `/hadoop/yarn/timeline` paths inside the container.

Dependencies/integration: copied by Dockerfile; supports Hadoop config completeness more than rclone core behavior.

Risks: duplicate `yarn.nodemanager.bind-host` appears; harmless but noisy. Timeline hostname is fixed to `historyserver.hadoop`.

Test signals: config-load success; rclone HDFS tests do not directly validate YARN behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/yarn-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/images/test-sftp-openssh/Dockerfile -->
# sources/user-network-fs/rclone/fstest/testserver/images/test-sftp-openssh/Dockerfile

Purpose: minimal Alpine OpenSSH server image for SFTP integration tests.

Important APIs/types/functions: installs `openssh`, generates host keys, creates user `rclone`, sets password `password`, and runs `/usr/sbin/sshd -D`.

Control flow: image build prepares user/keys; container entrypoint starts sshd in foreground.

State/persistence: user and host keys are image-local. Test file data lives in the container filesystem unless volumes are added.

Dependencies/integration: used by `init.d/TestSFTPOpenssh`, which maps port 22 to a local test port and emits rclone SFTP config.

Risks: hard-coded password and no custom sshd hardening are test-only. Alpine `latest` can change behavior over time.

Test signals: successful TCP connection to mapped port and SFTP authentication as `rclone`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/images/test-sftp-openssh/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestFTPProftpd -->
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestFTPProftpd

Purpose: starts a ProFTPD Docker container and emits rclone FTP remote config for integration tests.

Important APIs/types/functions: defines `NAME=proftpd`, user/password, sources `docker.bash`, and implements `start` with `docker run hauptmedia/proftpd`.

Control flow: `run.bash` dispatches `start`; the script starts the container, prints `type=ftp`, host from `docker_ip`, user, obscured password, encoding flags, and `_connect` probe.

State/persistence: container is disposable (`--rm`) and stopped by shared Docker helpers. Credentials are fixed test credentials.

Dependencies/integration: consumed by `testserver.Start`, which turns printed key/value lines into `RCLONE_CONFIG_TESTFTPPROFTPD_*` environment variables.

Risks: depends on external Docker image availability and Docker network IP inspection. FTP encoding expectations are server-specific.

Test signals: `_connect=<container-ip>:21` lets `testserver` wait until FTP accepts connections.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestFTPProftpd -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestFTPPureftpd -->
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestFTPPureftpd

Purpose: starts a Pure-FTPd Docker test server and emits rclone FTP config.

Important APIs/types/functions: configures username/password/home, client/connection limits, passive port range, and encoding flags for Pure-FTPd behavior.

Control flow: `start` runs `stilliard/pure-ftpd`, then echoes `type=ftp`, Docker IP host, credentials, encoding settings, and `_connect`.

State/persistence: disposable Docker container with `/data` as FTP home inside the container.

Dependencies/integration: uses `docker.bash` and `run.bash`; consumed by `testserver.Start`.

Risks: passive ports are configured in the container environment but not explicitly published here, so tests rely on Docker networking behavior reachable from host/container context. External image drift can alter FTP behavior.

Test signals: port 21 probe and successful FTP backend operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestFTPPureftpd -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestFTPRclone -->
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestFTPRclone

Purpose: starts `rclone serve ftp` against a local temp data directory for FTP backend integration tests.

Important APIs/types/functions: sets `NAME`, `USER`, `PASS`, loopback IP, port `28622`, and `start` calls helper `run rclone serve ftp --user --pass --addr`.

Control flow: `rclone-serve.bash` manages pidfile/data directory and sources `run.bash`; `start` launches the server if not already running and prints FTP config plus `_connect`.

State/persistence: data lives under `/tmp/rclone-serve-ftp-data`; pid/log files live under `/tmp`.

Dependencies/integration: depends on the current `rclone` binary in PATH and the shared serve/run helpers.

Risks: fixed port can conflict with another local process. Leftover pidfiles are handled, but stale data can persist in `/tmp`.

Test signals: TCP connection to `127.0.0.1:28622` and FTP test success.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestFTPRclone -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestFTPVsftpd -->
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestFTPVsftpd

Purpose: starts a vsftpd Docker server for FTP integration tests.

Important APIs/types/functions: runs `fauria/vsftpd` with `FTP_USER` and `FTP_PASS`, then emits rclone FTP config including `writing_mdtm=true` and encoding flags.

Control flow: Docker start followed by environment output; lifecycle is delegated to `docker.bash`/`run.bash`.

State/persistence: disposable container state only.

Dependencies/integration: used by `testserver.Start` for remote `TestFTPVsftpd`.

Risks: external image behavior and Docker IP availability. FTP timestamp behavior is explicitly enabled, so backend tests may reveal server differences.

Test signals: `_connect` FTP port and successful rclone FTP operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestFTPVsftpd -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestFTPVsftpdTLS -->
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestFTPVsftpdTLS

Purpose: starts an rclone-maintained vsftpd image variant intended for TLS-capable FTP testing.

Important APIs/types/functions: uses image `rclone/vsftpd`, fixed FTP user/password, `writing_mdtm=true`, and encoding flags.

Control flow: same as other Docker FTP scripts: run container, echo config, rely on shared lifecycle dispatcher.

State/persistence: disposable Docker container.

Dependencies/integration: `docker.bash`, `run.bash`, and `testserver.Start` consume the emitted config.

Risks: despite the name, this emitted config does not include explicit TLS options in the visible file; TLS behavior may be image default or configured elsewhere. Fixed credentials are test-only.

Test signals: connect probe on port 21 and integration test behavior against this server.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestFTPVsftpdTLS -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestHdfs -->
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestHdfs

Purpose: starts the local HDFS Docker test server and emits rclone HDFS config.

Important APIs/types/functions: `KERBEROS` env flag selects Kerberos mode. `start` runs image `rclone/test-hdfs` with hostname `rclone-hdfs`, maps HDFS/Kerberos ports to loopback, sleeps 30 seconds, optionally copies a Kerberos ticket cache, then prints `type=hdfs`, namenode, username, and `_connect`.

Control flow: lifecycle through `docker.bash`/`run.bash`; explicit sleep allows namenode/datanode startup before returning config.

State/persistence: disposable container; Kerberos mode copies `/tmp/krb5cc_<uid>` to host `/tmp`.

Dependencies/integration: depends on the HDFS image built from `images/test-hdfs`, Docker, and rclone HDFS backend tests.

Risks: fixed sleep can be too short/long. Port collisions on 8020/9866/88/750. Kerberos ticket cache path can collide with user state.

Test signals: TCP connect to `127.0.0.1:8020` and backend operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestHdfs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestS3Exaba -->
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestS3Exaba

Purpose: starts an Exaba S3-compatible server container for rclone S3 provider testing.

Important APIs/types/functions: maps API port `28635` and web UI port `28636`, sets cluster name/size, and emits provider `Exaba` config with endpoint/webui URLs.

Control flow: Docker run, then print S3 config. Access/secret strings are placeholders instructing use of the web UI.

State/persistence: disposable container with internal cluster data.

Dependencies/integration: shared Docker lifecycle and `testserver.Start`.

Risks: credentials are not automatically generated into usable values, so this may require manual web UI interaction before tests can pass. External image availability matters.

Test signals: connect probe to API port and valid S3 authentication/config.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestS3Exaba -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestS3Minio -->
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestS3Minio

Purpose: starts a Minio S3-compatible test server.

Important APIs/types/functions: defines fixed access/secret keys and port `28625`; `start` runs `minio/minio server /data` and emits rclone S3 provider `Minio` config.

Control flow: Docker start followed by config emission and `_connect`.

State/persistence: disposable container data under `/data`.

Dependencies/integration: Docker helper lifecycle and rclone S3 backend tests.

Risks: old Minio env names `MINIO_ACCESS_KEY`/`MINIO_SECRET_KEY` may differ in newer images. Fixed port can conflict.

Test signals: TCP connect to `127.0.0.1:28625` and S3 operation success.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestS3Minio -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestS3MinioEdge -->
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestS3MinioEdge

Purpose: starts Minio edge image to test rclone S3 behavior against a less stable/latest Minio line.

Important APIs/types/functions: same shape as `TestS3Minio`, but image `minio/minio:edge`, credentials differ, and port is `28626`.

Control flow: Docker run, emit S3 config, wait by `_connect`.

State/persistence: disposable container data.

Dependencies/integration: Docker and S3 tests; configured separately in `test_all/config.yaml`.

Risks: edge images can change or break without warning. Same credential-env compatibility risk as Minio stable.

Test signals: connection to port 28626 and S3 suite results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestS3MinioEdge -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestS3Rclone -->
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestS3Rclone

Purpose: starts `rclone serve s3` as a local S3-compatible test endpoint.

Important APIs/types/functions: uses `ACCESS_KEY_ID`, `SECRET_ACCESS_KEY`, loopback port `28624`, and `rclone-serve.bash`'s `run` helper.

Control flow: launches `rclone serve s3 --auth-key key,secret --addr`, then emits provider `Rclone`, endpoint, credentials, and `_connect`.

State/persistence: served data directory under `/tmp/rclone-serve-s3-data`; pid/log under `/tmp`.

Dependencies/integration: current rclone executable, serve helper, testserver env parser, S3 backend tests.

Risks: testing rclone S3 client against rclone S3 server can hide incompatibilities with third-party S3 services while still being valuable for protocol regression. Fixed port can conflict.

Test signals: local TCP connection and S3 operation results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestS3Rclone -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestSFTPOpenssh -->
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestSFTPOpenssh

Purpose: starts the OpenSSH SFTP Docker image and emits rclone SFTP config.

Important APIs/types/functions: maps local port `28627` to container port 22, uses user `rclone` and password `password`, and sets `copy_is_hardlink=true`.

Control flow: Docker run, config emission, `_connect` probe.

State/persistence: disposable container filesystem.

Dependencies/integration: image `rclone/test-sftp-openssh` and shared Docker lifecycle.

Risks: password-auth SFTP with fixed credentials is test-only. Hardlink copy behavior is server/filesystem-specific.

Test signals: SSH/SFTP connection to port 28627 and backend tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestSFTPOpenssh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestSFTPRclone -->
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestSFTPRclone

Purpose: starts `rclone serve sftp` with password authentication for SFTP integration tests.

Important APIs/types/functions: loopback port `28621`, fixed user/password, and `rclone-serve.bash` process/data management.

Control flow: `start` invokes `run rclone serve sftp --user --pass --addr`, then emits rclone SFTP config and `_connect`.

State/persistence: data under `/tmp/rclone-serve-sftp-data`; pid/log under `/tmp`.

Dependencies/integration: local rclone binary and testserver env setup.

Risks: fixed port and persistent `/tmp` data can interfere between abnormal runs.

Test signals: SFTP connection and operations against the rclone server.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestSFTPRclone -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestSFTPRcloneSSH -->
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestSFTPRcloneSSH

Purpose: starts `rclone serve sftp` and tests rclone's SFTP backend through an explicit `ssh` command using generated-on-start key files.

Important APIs/types/functions: writes a static OpenSSH private/public key pair to `/tmp`, starts `rclone serve sftp --authorized-keys`, and emits `type=sftp` plus an `ssh=ssh -i ... -p ... user@host` config line.

Control flow: key files are created/chmodded, server launches through `rclone-serve.bash`, and `_connect` is printed.

State/persistence: private/public keys remain under `/tmp/${NAME}.key(.pub)` unless cleaned manually; data/pid/log follow serve helper conventions.

Dependencies/integration: local `ssh` client behavior, rclone serve SFTP, and rclone SFTP backend's `ssh` option.

Risks: static private key material is embedded and written to `/tmp`; acceptable only for local tests. Long heredoc content makes maintenance awkward. Fixed port `28623` can conflict.

Test signals: TCP connect and successful SFTP operations through the custom ssh command.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestSFTPRcloneSSH -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestSMB -->
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestSMB

Purpose: starts a Samba container for SMB backend integration tests.

Important APIs/types/functions: uses `dperson/samba`, maps local port `28630` to SMB 445 TCP/UDP, creates user `rclone`, workgroup `thepub`, read-only `public` share, and writable `rclone` share.

Control flow: Docker run, then config emission with host, port, credentials, domain, and `_connect`.

State/persistence: disposable container shares.

Dependencies/integration: Docker lifecycle and rclone SMB backend tests.

Risks: SMB on nonstandard local port depends on backend support. Fixed credentials and guest share are test-only.

Test signals: connect to local SMB port and successful operations on share `rclone`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestSMB -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestSMBKerberos -->
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestSMBKerberos

Purpose: builds and starts a Samba AD DC container for SMB Kerberos integration tests using a host Kerberos config and credential cache.

Important APIs/types/functions: defines realm/domain, SMB/Kerberos ports, default `KRB5_CONFIG` and `KRB5CCNAME`, builds an Alpine image with `samba-dc`, provisions a domain, creates user `rclone`, configures shares, gets a Kerberos ticket cache, and emits SMB config with `use_kerberos=true`.

Control flow: inline Docker build, container run, host krb5.conf creation/copy, ccache generation/copy, KDC port rewrite, config echo.

State/persistence: writes `/tmp/rclone_krb5/krb5.conf` and ccache, builds a local Docker image, and runs a disposable container.

Dependencies/integration: Docker build/run, Samba tooling, Kerberos environment passed from `config.yaml`.

Risks: inline image build is expensive and can fail if Alpine packages change. Host `/tmp` Kerberos files can collide or become stale. Port conflicts on 28633/28634.

Test signals: SMB TCP probe plus successful Kerberos-authenticated SMB access.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestSMBKerberos -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestSMBKerberosCcache -->
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestSMBKerberosCcache

Purpose: variant of SMB Kerberos test server that passes an explicit `kerberos_ccache` rclone config value instead of relying solely on `KRB5CCNAME`.

Important APIs/types/functions: defaults `KRB5_CONFIG` and `RCLONE_TEST_CUSTOM_CCACHE_LOCATION` under `/tmp/rclone_krb5_ccache`, builds a Samba AD DC image, creates a Kerberos ticket cache, and emits `kerberos_ccache=<path>`.

Control flow: same provisioning model as `TestSMBKerberos`, with separate ports `28637`/`28638` and separate temp directory.

State/persistence: writes krb5.conf and ccache to host `/tmp`, builds image `rclone/test-smb-kerberos-ccache`, and runs a disposable container.

Dependencies/integration: used by `test_all/config.yaml` with `KRB5_CONFIG` env; validates rclone SMB ccache option handling.

Risks: same Docker/Samba/Kerberos drift risks, plus stale explicit ccache file can affect repeated runs.

Test signals: config emission includes `kerberos_ccache`; integration tests confirm auth through that cache.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestSMBKerberosCcache -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestSeafile -->
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestSeafile

Purpose: starts a Seafile 7+ docker-compose stack and creates a default library for rclone Seafile backend tests.

Important APIs/types/functions: exports compose environment including MySQL/admin credentials, loopback port `8087`, data root, version, and compose dir. `start` runs docker-compose, waits for HTTP 200, obtains auth token, creates default repo, and emits Seafile config.

Control flow: compose up, polling loop, token curl, default-repo curl, config echo. `stop` and `status` are custom compose-aware implementations.

State/persistence: data persists under `${SEAFILE_TEST_DATA}/${NAME}` (default `/tmp/seafile-test-data/seafile7`), unlike most disposable containers.

Dependencies/integration: requires `docker-compose`, compose file in `init.d/seafile`, curl, and Seafile API.

Risks: persistent data can leak between runs; `latest` image drift can break startup/API. Token parsing via sed assumes exact JSON shape.

Test signals: HTTP connect to port 8087 and successful library access.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestSeafile -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestSeafileEncrypted -->
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestSeafileEncrypted

Purpose: starts a Seafile stack and creates an encrypted library to test encrypted Seafile backend behavior.

Important APIs/types/functions: fixed encrypted library name/password, admin credentials, port `8088`, and `library_key` emitted obscured for rclone.

Control flow: compose up, fixed 60-second sleep, token retrieval, encrypted repo creation through API, config echo, custom compose stop/status.

State/persistence: data stored under `/tmp/seafile-test-data/seafile7encrypted` by default.

Dependencies/integration: docker-compose, Seafile API, curl, rclone obscure.

Risks: fixed sleep is less precise than polling. Persistent data and `latest` image drift can cause flaky repeated runs. Token sed parsing is brittle.

Test signals: connect probe on port 8088 and successful encrypted library operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestSeafileEncrypted -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestSeafileV6 -->
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestSeafileV6

Purpose: legacy Seafile v6-style single-container test server.

Important APIs/types/functions: sets port `8086`, admin credentials, data root, and image `seafileltd/seafile:${SEAFILE_VERSION}`. `start` runs Docker with `/shared` volume, sleeps, gets token, creates default library, and emits config.

Control flow: unlike newer compose scripts, uses `docker.bash` lifecycle. Startup waits by fixed 60-second sleep.

State/persistence: data persists under `/tmp/seafile-test-data/seafile6`.

Dependencies/integration: Docker, curl, Seafile v6 image/API, rclone obscure.

Risks: legacy image availability and API behavior may drift. Persistent data can affect idempotency.

Test signals: HTTP connection to port 8086 and default library operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestSeafileV6 -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestSia -->
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestSia

Purpose: starts a Sia antfarm test network for rclone Sia backend integration.

Important APIs/types/functions: `wait_for_sia` polls `/renter/uploadready` for `"ready":true`. `start` pulls `ivandeex/sia-antfarm:latest`, maps API to `127.0.0.1:39980`, waits up to 300 seconds, and emits `type=sia` with `api_url`.

Control flow: Docker pull, run, readiness polling through exported shell function, config echo. `stop` captures container logs to `sia-test.log` before killing.

State/persistence: disposable container; local log file `sia-test.log` accumulates stop logs.

Dependencies/integration: Docker, curl, timeout, Sia backend tests.

Risks: pulling `latest` makes runs network-dependent and non-reproducible. Startup can take minutes. Local log file can grow over repeated runs.

Test signals: upload-ready API response and successful Sia operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestSia -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestSwiftAIO -->
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestSwiftAIO

Purpose: starts OpenStack Swift All-In-One for Swift backend integration tests.

Important APIs/types/functions: maps local port `28628` to container 8080 and bind-mounts `TestSwiftAIO.d/remakerings` to create storage policy `Policy-1`. Emits Swift v1 auth config.

Control flow: Docker run, config echo, shared lifecycle through `docker.bash`/`run.bash`.

State/persistence: disposable container; remakerings mutates Swift ring config inside container startup.

Dependencies/integration: `openstackswift/saio` image, remakerings script, Swift backend tests.

Risks: external image and custom ring replacement are fragile. Fixed credentials are test defaults.

Test signals: auth endpoint connection and Swift operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestSwiftAIO -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestSwiftAIO.d/remakerings -->
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestSwiftAIO.d/remakerings

Purpose: replacement Swift ring-building script mounted into the SAIO container to add storage policy `Policy-1`.

Important APIs/types/functions: appends `[storage-policy:1]` to `swift.conf` if absent, removes old builder/ring files, creates/rebalances object, container, account, and object-1 rings with six local devices.

Control flow: sequential shell commands using `swift-ring-builder`.

State/persistence: mutates Swift config and ring files inside the container.

Dependencies/integration: mounted by `TestSwiftAIO` and `TestSwiftAIOsegments`; requires Swift tooling in `openstackswift/saio`.

Risks: assumes working directory and device names used by the SAIO image. Any image layout changes can break ring creation.

Test signals: Swift container starts with default and Policy-1 rings available.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestSwiftAIO.d/remakerings -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestSwiftAIOsegments -->
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestSwiftAIOsegments

Purpose: Swift AIO variant that disables rclone's segments container behavior.

Important APIs/types/functions: same SAIO image and remakerings mount as `TestSwiftAIO`, but port `28632` and emitted `use_segments_container=false`.

Control flow: Docker run, config echo, shared lifecycle.

State/persistence: disposable container.

Dependencies/integration: tests Swift backend behavior when large object segments are configured differently.

Risks: same SAIO image/ring fragility and fixed port risk.

Test signals: Swift auth connection and backend tests with `use_segments_container=false`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestSwiftAIOsegments -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestWebdavInfiniteScale -->
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestWebdavInfiniteScale

Purpose: starts ownCloud Infinite Scale (ocis) for WebDAV integration tests.

Important APIs/types/functions: prepares config directory `/tmp/ocis-config`, runs `owncloud/ocis init`, then starts ocis with basic auth enabled, insecure TLS, debug logging, and port `28639`. Emits WebDAV URL under the admin user's spaces path with vendor `infinitescale`.

Control flow: initialization container run, server container run, config echo with `_connect_delay=5s`.

State/persistence: config persists under `/tmp/ocis-config` between runs.

Dependencies/integration: Docker image `owncloud/ocis`, WebDAV backend tests, `docker.bash`.

Risks: persistent config plus forced overwrite can create surprising state. Uses insecure TLS and basic auth for tests. Fixed admin user id is embedded.

Test signals: HTTPS connect to port 28639 after delay and WebDAV operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestWebdavInfiniteScale -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestWebdavNextcloud -->
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestWebdavNextcloud

Purpose: starts a Nextcloud container for WebDAV backend tests.

Important APIs/types/functions: sets SQLite DB, admin user/password, trusted domains, maps port `28629`, and emits WebDAV files URL for user `rclone` with vendor `nextcloud`.

Control flow: Docker run followed by config echo and `_connect`.

State/persistence: disposable container state.

Dependencies/integration: `nextcloud:latest`, Docker lifecycle, WebDAV tests.

Risks: `latest` image startup/API behavior can drift. `_connect` only checks TCP, not that Nextcloud initialization is fully complete.

Test signals: connect probe and successful WebDAV authentication/listing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestWebdavNextcloud -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestWebdavOwncloud -->
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestWebdavOwncloud

Purpose: starts ownCloud Server for WebDAV integration tests.

Important APIs/types/functions: maps port `38081`, sets SQLite, admin credentials, trusted domain, disables Redis, and emits `/remote.php/webdav/` URL with vendor `owncloud`.

Control flow: Docker run, config emission, lifecycle via Docker helper.

State/persistence: disposable container state.

Dependencies/integration: `owncloud/server` Docker image and WebDAV backend.

Risks: hard-coded `OWNCLOUD_DOMAIN=localhost:8080` differs from mapped port and may be tolerated only because trusted domains includes 127.0.0.1. Fixed port is outside the nearby 286xx range.

Test signals: TCP connect to 38081 and WebDAV operation results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestWebdavOwncloud -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestWebdavRclone -->
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestWebdavRclone

Purpose: starts `rclone serve webdav` for local WebDAV backend tests.

Important APIs/types/functions: fixed user/password, loopback port `28620`, `rclone-serve.bash` process/data management, and emitted vendor `rclone`.

Control flow: `start` runs `rclone serve webdav --user --pass --addr`, then echoes URL, credentials, and `_connect`.

State/persistence: data under `/tmp/rclone-serve-webdav-data`; pid/log under `/tmp`.

Dependencies/integration: current rclone binary and WebDAV backend tests.

Risks: client/server same-code testing can miss third-party WebDAV quirks. Fixed port and stale `/tmp` data risks.

Test signals: TCP connect and WebDAV operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/TestWebdavRclone -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/docker.bash -->
# sources/user-network-fs/rclone/fstest/testserver/init.d/docker.bash

Purpose: shared Docker lifecycle helpers for testserver init scripts.

Important APIs/types/functions: `stop` stops container `$NAME` if `status` says it is running. `status` checks `docker ps --format '{{.Names}}'` for an exact name. `docker_ip` extracts the first Docker network IP via `docker inspect`.

Control flow: helper functions are sourced by concrete scripts and invoked by `run.bash` dispatch.

State/persistence: no direct persistent state; acts on Docker containers named by callers.

Dependencies/integration: Docker CLI and caller-defined `NAME`.

Risks: exact-name grep must be correctly quoted by callers; Docker network IPs may not be reachable on all host configurations. No force removal here; `run.bash force-stop` calls script-level `stop`.

Test signals: `status` exit code and successful Docker stop/IP lookup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/docker.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/rclone-serve.bash -->
# sources/user-network-fs/rclone/fstest/testserver/init.d/rclone-serve.bash

Purpose: shared lifecycle helper for scripts that start `rclone serve ...` processes.

Important APIs/types/functions: defines `PIDFILE=/tmp/${NAME}.pid`, `DATADIR=/tmp/${NAME}-data`, `stop`, `status`, and `run`. `run` creates data dir, starts command with `nohup`, writes pidfile, and disowns the process.

Control flow: concrete scripts define `start` using `run`; this helper sources `run.bash` for command dispatch/refcounting.

State/persistence: writes pidfiles, logs, and data directories under `/tmp`.

Dependencies/integration: shell job control, local rclone binary, and `run.bash`.

Risks: pid reuse is possible if pidfile is stale and process exists but is unrelated. Logs/data can persist across runs.

Test signals: `status` probes process liveness with `kill -0`; `_connect` is emitted by concrete scripts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/rclone-serve.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/run.bash -->
# sources/user-network-fs/rclone/fstest/testserver/init.d/run.bash

Purpose: common command dispatcher and refcounting layer for testserver init scripts.

Important APIs/types/functions: calculates `RUN_BASE`, `RUN_ROOT`, lock/refcount/env files, `_is_running`, `_acquire_lock`, `_release_lock`, and handles `start`, `stop`, `reset`, `force-stop`, `status`.

Control flow: `start` locks, resets stale refcounts if server is gone, starts the server only for first client, caches emitted env output, increments refcount, and prints cached env. `stop` decrements and stops at zero. `reset` stops and removes state. `force-stop` unconditionally stops and zeroes refcount. `status` delegates without lock.

State/persistence: stores per-server runtime state under `${STATE_DIR:-${XDG_RUNTIME_DIR:-/tmp}/rclone-test-server}/${NAME}`.

Dependencies/integration: requires caller-defined `start/stop/status`, `flock`, and POSIX-ish bash. `testserver.Start` invokes scripts with `start` and returned cleanup invokes `stop`.

Risks: refcount correctness is central; stale lock/state files can confuse manual debugging. It uses `set -euo pipefail`, so missing variables in sourced scripts can fail quickly.

Test signals: cached env output plus refcounted server lifecycle across concurrent tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/run.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/seafile/docker-compose.yml -->
# sources/user-network-fs/rclone/fstest/testserver/init.d/seafile/docker-compose.yml

Purpose: docker-compose stack used by Seafile testserver scripts.

Important APIs/types/functions: services are `db` (`mariadb:10.5`), `memcached`, and `seafile` (`seafileltd/seafile-mc:${SEAFILE_VERSION}`). Environment variables configure DB password, admin account, server hostname, and data volumes.

Control flow: compose starts DB and memcached before Seafile; Seafile maps `${SEAFILE_IP}:${SEAFILE_PORT}:80`.

State/persistence: MariaDB and Seafile data persist under `${SEAFILE_TEST_DATA}/${NAME}/...`.

Dependencies/integration: consumed by `TestSeafile` and `TestSeafileEncrypted` with project names and env vars.

Risks: compose file version 2.0 and older service images may require compatible docker-compose. Persistent volumes can retain stale users/libraries.

Test signals: Seafile scripts poll or sleep, then use the API to create libraries before tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/init.d/seafile/docker-compose.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/testserver.go -->
# sources/user-network-fs/rclone/fstest/testserver/testserver.go

Purpose: package `testserver` bridges Go tests and shell init scripts that start local integration-test services.

Important APIs/types/functions: `findConfig` locates `fstest/testserver/init.d`; `cmdPath`, `hasStartCommand`, `run`, `envKey`, `start`, `stop`, `Start`, and `CleanupAll` implement lifecycle. `trackedServers` records servers started by the process for force cleanup.

Control flow: `Start(remote)` parses the rclone remote, skips local/unconfigured names, locates script directory once, skips remotes with no script, runs `<script> start`, parses `key=value` output into `RCLONE_CONFIG_<REMOTE>_<KEY>` env vars, optionally probes `_connect` with retries and `_connect_delay`, tracks the server, and returns an idempotent stop closure. `CleanupAll` force-stops all still-tracked servers.

State/persistence: mutates process environment and in-memory tracked refcounts. Shell scripts manage external containers/processes and runtime state.

Dependencies/integration: uses `fspath.Parse`, rclone logging, Go networking, and all `init.d` scripts with the shared `run.bash` contract.

Risks: environment variables are process-global and can leak across tests. `_connect` only verifies TCP-level readiness. If script output includes unexpected lines, they are ignored unless matching key/value.

Test signals: start failures surface as Go errors; cleanup logging reports force-stop failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testserver/testserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testy/testy.go -->
# sources/user-network-fs/rclone/fstest/testy/testy.go

Purpose: small test utility package for CI and Docker availability gating.

Important APIs/types/functions: `CI` checks `CI` env var. `SkipUnreliable` skips tests on CI. `HaveDocker` caches whether Docker can be used by checking OS and `docker version`. `SkipUnlessDocker` skips tests when Docker is unavailable.

Control flow: `HaveDocker` uses `sync.Once`; Windows immediately returns false because init.d scripts are bash, otherwise it runs `docker version`.

State/persistence: cached in-memory `dockerOnce.ok`; no persistence.

Dependencies/integration: used by tests that require the fstest/testserver Docker framework.

Risks: `docker version` can be slow or fail for permission reasons. Cached false means Docker becoming available later in the same process is not detected.

Test signals: skip messages distinguish unavailable Docker and unreliable-on-CI tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/testy/testy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/atexit/atexit.go -->
# sources/user-network-fs/rclone/lib/atexit/atexit.go

Purpose: package `atexit` registers cleanup functions to run once on normal shutdown or selected exit signals.

Important APIs/types/functions: globals hold registered function handles, mutexes, signal channel, `sync.Once`s, and atomic `signalled`/`runCalled`. Public APIs are `Register`, `Signalled`, `Unregister`, `IgnoreSignals`, `Run`, and `OnError`. `FnHandle` is a pointer to the registered function value.

Control flow: first `Register` installs a signal goroutine for platform `exitSignals`. On signal, it stops signal delivery, marks signalled, logs, calls `Run`, and exits with platform-specific code. `Run` marks running, locks the function map, and executes registered functions once. `OnError` wraps a cleanup so it runs either at exit or when a deferred error pointer is non-nil.

State/persistence: process-global registry only.

Dependencies/integration: used by `test_all` to force-stop servers and by `batcher` to flush pending batches.

Risks: functions run while holding `fnsMutex`; a handler that tries to register/unregister can deadlock. Map iteration order is nondeterministic. Handlers registered after `Run` starts are ignored.

Test signals: platform exit-code behavior is covered in `atexit_test.go`; signal execution is typically integration-tested by consumers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/atexit/atexit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/atexit/atexit_other.go -->
# sources/user-network-fs/rclone/lib/atexit/atexit_other.go

Purpose: platform-specific signal settings for Windows and Plan 9.

Important APIs/types/functions: build tag `windows || plan9`; defines `exitSignals = []os.Signal{os.Interrupt}` and `exitCode` returning `exitcode.UncategorizedError`.

Control flow: consumed by `atexit.Register` when installing signal notifications and deciding process exit code.

State/persistence: none beyond package variables.

Dependencies/integration: imports `os` and rclone `lib/exitcode`.

Risks: unlike Unix, it does not encode signal number in exit status; this is intentional for platforms without the same convention.

Test signals: `TestExitCode` asserts this behavior on Windows/Plan 9.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/atexit/atexit_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/atexit/atexit_test.go -->
# sources/user-network-fs/rclone/lib/atexit/atexit_test.go

Purpose: tests platform-specific `exitCode` behavior.

Important APIs/types/functions: `fakeSignal` implements `os.Signal` without being a real syscall signal. `TestExitCode` checks Windows/Plan 9 return uncategorized errors, Unix returns `128+signal` for known signals, and fake signals return uncategorized.

Control flow: runtime OS switch selects expectations.

State/persistence: none.

Dependencies/integration: uses `runtime`, `os`, `exitcode`, and `testify/assert`.

Risks: assumes POSIX signal numbers for SIGINT and SIGKILL on Unix-like platforms, as noted in comments.

Test signals: direct coverage of `atexit_other.go` and `atexit_unix.go` exit-code helpers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/atexit/atexit_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/atexit/atexit_unix.go -->
# sources/user-network-fs/rclone/lib/atexit/atexit_unix.go

Purpose: Unix platform signal list and exit-code conversion for `atexit`.

Important APIs/types/functions: build tag excludes Windows/Plan 9. `exitSignals` handles `SIGINT` and `SIGTERM`, intentionally not `SIGQUIT`. `exitCode` returns `128+signum` for real positive `syscall.Signal`, else uncategorized.

Control flow: used by signal goroutine in `atexit.Register`.

State/persistence: no mutable state here.

Dependencies/integration: imports `os`, `syscall`, and `exitcode`.

Risks: only selected signals trigger cleanup; unhandled fatal signals and SIGQUIT use default behavior.

Test signals: covered by `TestExitCode` on Unix-like systems.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/atexit/atexit_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/batcher/batcher.go -->
# sources/user-network-fs/rclone/lib/batcher/batcher.go

Purpose: generic batching engine for grouping many item commits into fewer backend/API calls.

Important APIs/types/functions: `Options` configures mode, size, timeout, max size, and defaults. `CommitBatchFn[Item, Result]` is the user callback. `Batcher[Item, Result]` manages channels, async mode, shutdown, atexit registration, and waitgroup. Public methods are `New`, `Batching`, `Shutdown`, and `Commit`.

Control flow: `New` validates options, resolves defaults for `sync`, `async`, or `off`, creates buffered input channel, and starts `commitLoop` if active. `Commit` sends a request and either waits for a response in sync mode or returns immediately in async mode. `commitLoop` commits when batch size is reached, idle timeout fires, or shutdown occurs. `commitBatch` invokes the user callback with parallel results/errors arrays and distributes per-item responses.

State/persistence: in-memory pending request queue. Active batchers register `Shutdown` with `atexit` to flush on process exit.

Dependencies/integration: uses rclone config for default sync batch size, logging, fatal retry error wrapping, and `atexit`.

Risks: async mode cannot report per-item commit failures to callers. `Commit` sends to `b.in` without selecting on context cancellation, so a blocked channel can block the caller. User callback must fill result/error slices correctly.

Test signals: `batcher_test.go` covers construction validation, batch commit, failure propagation, shutdown, and async behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/batcher/batcher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/batcher/batcher_test.go -->
# sources/user-network-fs/rclone/lib/batcher/batcher_test.go

Purpose: unit tests for generic batcher behavior.

Important APIs/types/functions: defines simple test item/result types and test commit callbacks. Tests include `TestBatcherNew`, `TestBatcherCommit`, `TestBatcherCommitFail`, `TestBatcherCommitShutdown`, and `TestBatcherCommitAsync`.

Control flow: tests instantiate batchers under different modes/options, submit commits, wait for size/timeout commits, induce callback errors, call shutdown, and assert returned entries/errors.

State/persistence: uses in-memory counters/channels only; active batchers are shut down in tests to avoid atexit leakage.

Dependencies/integration: uses Go testing and `testify` assertions. It validates generic behavior independent of any backend.

Risks: timing-sensitive tests around idle timeout can be flaky if timeouts are too tight, but the file keeps scopes small.

Test signals: direct coverage of sync vs async semantics and error propagation, protecting backend upload batching users.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/batcher/batcher_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/batcher/options.go -->
# sources/user-network-fs/rclone/lib/batcher/options.go

Purpose: exposes batcher settings as rclone backend options.

Important APIs/types/functions: `(*Options).FsOptions(extra string) []fs.Option` returns option definitions for `batch_mode`, `batch_size`, `batch_timeout`, and hidden legacy `batch_commit_timeout`.

Control flow: builds help text with configured max/default values and caller-provided extra documentation.

State/persistence: no state; declarative option metadata.

Dependencies/integration: depends on rclone `fs.Option` and `fs.Duration`; backend config structs can embed/use these options.

Risks: help text must stay aligned with actual `batcher.New` behavior. Hidden `batch_commit_timeout` is retained for compatibility and no longer used.

Test signals: indirectly covered by backends parsing options and by batcher constructor tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/batcher/options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/bucket/bucket.go -->
# sources/user-network-fs/rclone/lib/bucket/bucket.go

Purpose: utility package for bucket-based backend path handling and bucket existence/deletion caching.

Important APIs/types/functions: `ErrAlreadyDeleted`, `Split`, `Join`, `IsAllSlashes`, `Cache`, `NewCache`, `MarkOK`, `MarkDeleted`, `Create`, `Remove`, and `IsDeleted`. `CreateFn` and `ExistsFn` abstract backend operations.

Control flow: `Split` separates first path component as bucket. `Join` concatenates without cleaning to preserve slashes. `Cache.Create` serializes creates, optionally re-checks externally deleted buckets, calls `create`, and marks success. `Cache.Remove` serializes removes and returns `ErrAlreadyDeleted` for known-deleted buckets. Separate create/remove mutexes avoid simultaneous conflicting operations.

State/persistence: `Cache.status` is an in-memory map of bucket name to known present/deleted.

Dependencies/integration: used by bucket-based backends to avoid redundant creates/removes and to preserve path semantics that `path.Join` would normalize away.

Risks: cache can become stale if buckets are changed externally. `Create`/`Remove` unlock the map around user callbacks, so status may change concurrently; outer create/remove mutexes limit same-operation races but not all external effects.

Test signals: `bucket_test.go` covers path functions and cache state transitions/errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/bucket/bucket.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/bucket/bucket_test.go -->
# sources/user-network-fs/rclone/lib/bucket/bucket_test.go

Purpose: validates bucket utility path semantics and cache state transitions.

Important APIs/types/functions: `TestSplit`, `TestJoin`, `TestIsAllSlashes`, and `TestCache`.

Control flow: table tests check split/join/slash edge cases. `TestCache` manually inspects cache status after marks, creates, exists errors, root operations, removes, already-deleted detection, and callback errors.

State/persistence: in-memory cache only.

Dependencies/integration: uses `testify/assert`.

Risks: tests access unexported `c.status` because they are in package `bucket`, making them precise but coupled to implementation representation.

Test signals: strong coverage for preserving multiple/trailing slashes and for avoiding repeat bucket deletion/creation calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/bucket/bucket_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/buildinfo/arch.go -->
# sources/user-network-fs/rclone/lib/buildinfo/arch.go

Purpose: reports runtime architecture details, especially ARM compatibility levels relevant to Go builds.

Important APIs/types/functions: `GetSupportedGOARM` inspects `runtime.GOARCH` and `golang.org/x/sys/cpu` ARM feature flags to return 7, 6, 5, or 0. `GetArch` returns `runtime.GOARCH` with explanatory ARM suffixes.

Control flow: if running 32-bit ARM with initialized CPU feature data, VFPv3 maps to GOARM 7, VFP to 6, and no VFP to 5. `GetArch` annotates `arm64` as ARMv8-compatible and `arm` based on supported GOARM.

State/persistence: no state.

Dependencies/integration: used by rclone build/version reporting to describe architecture. Depends on `runtime` and `x/sys/cpu`.

Risks: it reports CPU-supported GOARM, not necessarily the GOARM value used to build the binary, as comments explain. Non-ARM returns unannotated runtime architecture.

Test signals: no direct test in this subset; behavior is observable in build info output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/buildinfo/arch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/buildinfo/cgo.go -->
# sources/user-network-fs/rclone/lib/buildinfo/cgo.go

Purpose: records the `cgo` build tag in build information when compiled with cgo enabled.

Important APIs/types/functions: build tag `cgo`; `init` appends `"cgo"` to package variable `Tags`.

Control flow: Go runtime executes `init` during package initialization only in cgo builds.

State/persistence: mutates in-memory `buildinfo.Tags`.

Dependencies/integration: integrates with `buildinfo/tags.go` and version/build-info display.

Risks: relies on shared mutable `Tags` ordering with other build-tag init files.

Test signals: build output including `cgo` tag when compiled with cgo.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/buildinfo/cgo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/buildinfo/osversion.go -->
# sources/user-network-fs/rclone/lib/buildinfo/osversion.go

Purpose: non-Windows OS version/kernel reporting for build info.

Important APIs/types/functions: build tag `!windows`; `GetOSVersion() (osVersion, osKernel string)` uses `gopsutil/host` to collect platform, version, kernel version, and kernel architecture.

Control flow: platform/version form `osVersion`; kernel version forms `osKernel`; kernel arch appends `(64 bit)` to OS version when appropriate and appends architecture to kernel string.

State/persistence: no state.

Dependencies/integration: used by rclone version/build diagnostics; depends on `github.com/shirou/gopsutil/v4/host`.

Risks: all host probes are best-effort and silently omit fields on error. 64-bit detection is string-suffix based.

Test signals: observable in build/version output; no direct tests here.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/buildinfo/osversion.go -->
