# subset-b-000201 research

This grouped report covers the requested Moby integration CLI test sources. Each section is source-tree-aligned and bounded by reconciliation markers for deterministic splitting into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_rmi_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_rmi_test.go

## Purpose

`docker_cli_rmi_test.go` defines `DockerCLIRmiSuite`, the integration test suite for `docker rmi` behavior. It validates the user-visible contract for image untagging and deletion when images are referenced by containers, tags, repositories, parent/child image relationships, and image IDs. The file is not testing a narrow Go API; it drives the Docker CLI against a real test daemon and checks CLI output, exit status, daemon image metadata, and object survival.

The suite is especially focused on conflict semantics: when deletion is blocked, when `-f` can remove tags or images, and when `-f` must still refuse because a running container uses the image. It also covers edge cases around blank names, short IDs, parent images, and history-layer tags.

## Important APIs, Types, and Helpers

The primary type is `DockerCLIRmiSuite`, which holds a shared `*DockerSuite` and forwards `TearDownTest` and `OnTimeout` to the suite-level cleanup and diagnostics. Test methods use the integration helpers from `github.com/moby/moby/v2/integration-cli/cli`, especially `cli.DockerCmd`, `cli.Docker`, `cli.Args`, and `cli.BuildCmd`.

Important shared helpers from the integration package include `dockerCmdWithError` for expected failures, `inspectField` and `getIDByName` for daemon object inspection, `runSleepingContainerInImage` for live image references, and `build.WithDockerfile`/`build.WithoutCache` for constructing isolated images. Assertions are done with `gotest.tools/v3/assert`, `assert/cmp`, and `icmd.Expected`. The suite also uses `stringid.TruncateID` to match daemon conflict messages that include shortened image/container IDs.

## Control Flow and Coverage

The tests follow a consistent integration pattern: create or tag images, create running or stopped containers that reference them, run `docker rmi` with or without `-f`, then inspect CLI output and image/container state. `TestRmiWithContainerFails` confirms a plain `rmi busybox` fails while a container references the image and does not remove the `busybox` repository entry. `TestRmiTag`, `TestRmiImgIDMultipleTag`, and `TestRmiImgIDForce` build up multiple references to the same image ID and check the difference between removing a tag, deleting by ID with multiple tags, and forced deletion.

Conflict paths are covered in detail. `TestRmiImageIDForceWithRunningContainersAndMultipleTags` ensures that even forced deletion by image ID refuses when a running container uses the image. `TestRmiTagWithExistingContainers`, `TestRmiForceWithExistingContainers`, `TestRmiWithMultipleRepositories`, and `TestRmiForceWithMultipleRepositories` distinguish safe untag operations from true image deletion. `TestRmiContainerImageNotFound` verifies that a force-removed image for a stopped container does not confuse the error path for a running-container image.

Several regression-style cases protect parsing and graph relationships. `TestRmiBlank` expects a blank image name validation error instead of a generic missing-ID message. `TestRmiUntagHistoryLayer` and `TestRmiParentImageFail` are currently skipped or marked broken around BuildKit/containerd image-store behavior, documenting fragile historical assumptions. `TestRmiWithParentInUse` exercises commits layered on commits and removes the newest image. `TestRmiByIDHardConflict` ensures deletion by short image ID fails when a container exists and does not silently untag `busybox:latest`.

## State and Persistence Behavior

The file mutates daemon image state heavily: it creates containers, commits them into images, adds multiple tags and repository aliases, and removes images by tag and ID. Assertions rely on persistent daemon state observable through `docker images`, `docker inspect`, and subsequent `rmi` operations. Running containers are deliberately used as hard references that prevent image deletion; stopped containers and tags are used to verify weaker references and force-removal behavior.

Image graph semantics matter. The skipped parent/history tests show that parent/child metadata and historical layer addressing have changed across builders and image stores. Tests that use `testEnv.UsingSnapshotter()` skip legacy parent expectations because containerd-backed image storage treats images differently from the older graphdriver image store.

## Dependencies and Integration Points

This suite integrates the CLI, daemon image service, builder, container lifecycle, and image-reference parser. It assumes a seeded `busybox` image and, in some tests, platform-specific behavior such as Windows commit timing. The suite also depends on exact or partial daemon error strings, including conflict text, repository-reference wording, and running-container messages.

Build integration is required for custom image/tag graphs. Container integration is required because image deletion rules depend on active and stopped container references. Inspection integration is required to compare image IDs, parent fields, and tag survival.

## Risks and Maintenance Notes

The biggest maintenance risk is tight coupling to CLI and daemon error strings. Several assertions use exact conflict text or fixed substrings, so legitimate wording changes can break tests even when behavior is preserved. The second risk is image-store drift: BuildKit and containerd image store changes already caused skipped tests, and future parent/history semantics can invalidate old graph assumptions.

Tests that count lines in `docker images -a` are sensitive to output formatting and pre-existing images. The suite relies on shared test cleanup to isolate state. Running-container tests can be timing-sensitive, especially on Windows where commits wait for containers to exit.

## Test Signals

Passing tests signal that `docker rmi` preserves tags and images when references require it, force deletion removes allowable references, running-container conflicts remain hard conflicts, and invalid image names or ambiguous IDs produce safe errors. Skipped tests signal known gaps around history-layer untagging and parent image conflicts under newer builder/image-store behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_rmi_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_run_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_run_test.go

## Purpose

`docker_cli_run_test.go` is the broad cross-platform integration suite for `docker run`. It defines `DockerCLIRunSuite` and covers the CLI contract for container creation and start, stdio, exit codes, naming, working directories, network modes, links and aliases, volumes, bind mounts, users, environment variables, capabilities, devices, DNS and host files, namespaces, restart policies, auto-removal, logging failures, mount syntax, Windows CPU and credential-spec flags, and many regression cases.

This file is effectively an end-to-end specification of `docker run` behavior at the boundary between Docker CLI, API client, daemon validation, runtime setup, network driver, storage driver, and platform-specific container runtime behavior.

## Important APIs, Types, and Helpers

The primary type is `DockerCLIRunSuite`, with `TearDownTest` and `OnTimeout` delegated to `DockerSuite`. Most tests call `cli.DockerCmd` for success paths and `dockerCmdWithError` or `icmd.RunCommand` for expected failures. The file uses `inspectField`, `inspectFieldJSON`, `inspectMountPoint`, `inspectFilter`, `waitInspect`, `readContainerFile`, `containerStorageFile`, `runSleepingContainer`, `runSleepingContainerInImage`, `deleteImages`, and platform helpers such as `dPath`, `minimalBaseImage`, `sleepCommandForDaemonPlatform`, and `getPrefixAndSlashFromDaemonPlatform`.

External packages indicate the integration breadth: `client` and `api/types/network` for API inspection and port maps, `daemon` and `testutil/daemon` for isolated daemon tests, `fakecontext` and `build` for controlled images, `specialimage` for synthetic images, `mountinfo` for host `/etc/resolv.conf` handling, and `poll` for asynchronous removal checks. Standard library dependencies include process execution, pipes, temp files, JSON, networking, path handling, concurrency, and timeouts.

Helper functions local to the file include `testRunWriteSpecialFilesAndNotCommit`, `eqToBaseDiff`, `sliceEq`, `containerRemoved`, `testReadOnlyFile`, `testRunContainerWithCgroupParent`, `testRunInvalidCgroupParent`, and `delayedReader`. These helpers encapsulate repeated checks for special-file diffs, read-only rootfs behavior, cgroup-parent validation, auto-removal polling, and slow stdin closure.

## Control Flow and Behavioral Areas

The opening tests validate basic execution: stdout from `echo`, named containers, file descriptor leakage, DNS lookup, expected exit codes, stdin pipe behavior, detached ID printing, working directory flags, and disabled networking. Link and alias tests then verify legacy `--link` behavior and user-defined bridge DNS behavior, including aliases that resolve after linked containers start or restart.

The volume section checks `--volumes-from`, anonymous volumes, bind mounts, symlinked paths, duplicate mount-point validation, copy-up behavior, read-only inheritance, named volume retention, and cleanup of anonymous volumes. It explicitly distinguishes bind mounts, named volumes, anonymous volumes, image-declared volumes, and `--mount` syntax. Later mount tests compare equivalent `--volume` and `--mount` forms, reject duplicate targets and unsupported copy modes, and verify writable volumes on a read-only root filesystem.

User, environment, and process tests validate default root identity, `-u` by name/ID/range, unknown users, concurrent `run` calls, environment passthrough/override/erase semantics, entrypoint overrides, command-not-found exit codes, invalid command invocation, invalid image references, stdin close behavior, restart policy behavior with interactive runs, and slow stdin readers.

Security and namespace sections cover privileged and unprivileged access to `mknod`, `mount`, `/sys`, `/proc`, devices, `chroot`, capability add/drop ordering, group additions, IPC/PID/NET/UTS host and container namespace sharing, read-only rootfs exceptions for Docker-managed host files, AppArmor checks, `/proc` filtering, cgroup mount read-only behavior, cgroup-parent path sanitization, and `--device-cgroup-rule`.

Networking tests are extensive. They cover host network conflicts with links and DNS flags, user-defined networks, multiple networks, network isolation and reconnection, active-container network removal failures, restart behavior across multiple networks, host/none/container network conflict rules, loopback behavior in `--net=none`, MAC address validation, port allocation, publish and expose ranges, duplicate host ports, `--add-host`, and DNS behavior in normal and host modes.

State and daemon-specific tests verify container `State.Running` and PID changes across stop/start, restart-count and max retry fields, auto-remove behavior for new and pre-1.25 APIs, goroutine leak checks for failed attach/logging paths, daemon default ulimits, TLS verify flag behavior, and Windows-only CPU and credential-spec handling.

## State and Persistence Behavior

The suite creates persistent containers, images, volumes, networks, and daemon-level state, then inspects or removes them. Many tests depend on the teardown path to clean containers, networks, and volumes after each test. Tests use `docker inspect` to verify persisted `HostConfig`, `Config`, `NetworkSettings`, restart policy, ulimits, cgroup parent, mount metadata, MAC address, CPU settings, and image metadata.

Several tests modify host or daemon-adjacent state. `TestRunDNSDefaultOptions` temporarily rewrites `/etc/resolv.conf` and restores it. `TestRunResolvconfUpdate` is skipped but documents restart-time host resolver propagation. Local daemon tests create host temp directories, bind mounts, symlinks, files with adjusted permissions, listeners on host ports, and isolated daemon instances. Named volume tests intentionally check that named volumes persist after `--rm` or `rm -v`, while anonymous inherited volumes are removed when expected.

Network tests create user-defined bridge networks and connect/disconnect running containers. Auto-removal tests use polling because daemon-side removal is asynchronous. Goroutine leak tests query the daemon API before and after failure scenarios, making daemon internal runtime state part of the signal.

## Dependencies and Integration Points

This file integrates with nearly every daemon subsystem used by `docker run`: image lookup/pull error handling, container create/start/wait/logs/inspect/remove, networking/libnetwork, volume drivers, graph/image copy-up, exec, daemon configuration, logging drivers, API version negotiation, runtime namespaces, cgroups, AppArmor, seccomp-adjacent behavior, Windows HCS options, and CLI config/env parsing.

The tests depend on standard test images such as `busybox`, `busybox:glibc`, `debian:trixie-slim`, platform default images, and generated test images. Several cases require a local Linux daemon, non-userns mode, cgroup v1, AppArmor, network access, or Windows-specific daemon modes. These requirements are expressed with `testRequires` and `skip.If`.

## Risks and Maintenance Notes

The file has high brittleness because it asserts exact text for many CLI and daemon errors, including invalid flags, mount conflicts, network conflicts, port allocation errors, and platform-specific Windows warnings. It also depends on implementation details such as cgroup v1 file paths, `/proc` layout, default Google DNS fallback values, `busybox` command availability, and daemon graph paths.

Several tests are intentionally skipped or marked unstable, signaling known drift: resolver updates, cgroup v2 gaps, BuildKit/image-volume differences, and validations that moved from CLI to daemon. Tests that bind host root, edit `/etc/resolv.conf`, create `/dev` symlinks, or bind special network files require careful local-daemon isolation. Networking tests can be timing-sensitive because DNS names, restart propagation, and network endpoint state are asynchronous.

The suite is large and multi-domain; changes to `docker run` validation can break unrelated-looking tests because validation order affects the first returned error string and exit code. Platform branches also mean a fix for Linux may leave Windows behavior uncovered or vice versa.

## Test Signals

Passing this suite signals that the CLI can translate `docker run` options into daemon API calls correctly, daemon validation rejects unsafe combinations, runtime state is created with expected mounts/namespaces/cgroups/security settings, container output and exit codes propagate, cleanup paths remove or preserve objects as designed, and cross-subsystem interactions such as networking plus DNS or read-only rootfs plus special host files remain stable.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_run_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_run_unix_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_run_unix_test.go

## Purpose

`docker_cli_run_unix_test.go` is the non-Windows companion to the main `docker run` integration suite. It is guarded by `//go:build !windows` and focuses on Unix/Linux behaviors that require PTYs, Unix devices, cgroups, tmpfs, shm, sysctls, seccomp, AppArmor, Linux capabilities, no-new-privileges, and daemon-level seccomp profile configuration.

The file extends `DockerCLIRunSuite` and `DockerDaemonSuite` with tests that cannot be expressed portably in the cross-platform run suite. It validates the Linux kernel-facing contract of `docker run`.

## Important APIs, Types, and Helpers

There are no new suite types; methods attach to `DockerCLIRunSuite` or `DockerDaemonSuite`. The file uses `github.com/creack/pty` for interactive attach/detach tests, `github.com/moby/sys/mount` for host tmpfs setup, `github.com/moby/moby/v2/pkg/sysinfo` for CPU and memory node validation, `github.com/moby/profiles/seccomp` for default profile serialization, and `client.New` for API-level inspection of `NanoCPUs`.

Shared helpers include `cli.DockerCmd`, `dockerCmdWithError`, `inspectField`, `inspectFieldJSON`, `ensureSyscallTest`, `ensureNNPTest`, `testRequires`, and `skip.If`. The local `sysctlExists` helper checks for optional kernel sysctls before adding compatibility sysctl flags to capability tests.

## Control Flow and Behavioral Areas

The first group verifies terminal and attach behavior. `TestRunRedirectStdout` runs commands through a PTY and shell pipeline to ensure container stdout can be redirected. The attach/detach tests start interactive containers, connect with `docker attach`, write through a PTY, send default or configured escape sequences, wait for the attach command to exit, and confirm the container remains running. Config-file detach keys are tested through a temporary `$HOME/.docker/config.json`, and invalid escape sequences are checked for preservation in the stream.

Device and mount behavior is covered through recursive bind mounts, `/dev/snd` directory devices, symlinked devices, tmpfs ordering, `--tmpfs` options, default and explicit `/dev/shm` size, read-only `/dev/shm`, and PIDs/device cgroup lists. These tests inspect actual kernel mount output and cgroup files from inside containers.

Resource-control tests validate cgroup-backed CLI flags: `--cpu-quota`, `--cpu-period`, `--cpu-shares`, `--cpuset-cpus`, `--cpuset-mems`, `--blkio-weight`, memory limit, memory reservation, memory swap, swappiness, OOM exit code 137, PIDs limit, and `--cpus`/NanoCPUs. Many are skipped under cgroup v2 because the expected v1 files and semantics are not available.

Security tests cover sysctl setting and validation, custom seccomp profiles that deny specific syscalls, default seccomp profile behavior for clone/user namespace/acct/ns syscalls, 32-bit syscall allowance on amd64, setrlimit allowance, no-new-privileges preventing setuid transitions, AppArmor denial for `/proc` modifications, and daemon restart with a custom default seccomp profile.

Capability tests check that root has default effective capabilities while non-root users and `--cap-drop` lose them. Capabilities covered include CHOWN, DAC_OVERRIDE, FOWNER, SETUID, SETGID, NET_BIND_SERVICE, NET_RAW, SYS_CHROOT, and MKNOD. The tests use `syscall-test`, `busybox`, and kernel sysctls to distinguish permission failures from missing feature support.

## State and Persistence Behavior

Most tests create short-lived containers and inspect container or kernel state immediately. Some create persistent named containers to inspect `HostConfig` values after execution. PTY attach tests leave containers running until suite teardown. Host state is touched in controlled ways: temp directories are created and mounted as tmpfs, symlinks are created, `/dev/symzero` is temporarily created and removed, and custom seccomp profile JSON files are written to temp paths.

Daemon state is significant in the `DockerDaemonSuite` seccomp tests. Those tests start an isolated daemon with busybox loaded, run containers against it, and restart it with `--seccomp-profile` to verify daemon default profile persistence. Resource tests persist `HostConfig` values such as CPU quota, period, cpuset, memory, shm size, pids limit, and NanoCPUs for inspection.

## Dependencies and Integration Points

This file integrates directly with Linux kernel interfaces. It depends on `/sys/fs/cgroup/*` v1 paths, `/proc`, `/dev`, AppArmor, seccomp, user namespace availability, unprivileged user namespace clone policy, host sound devices, memory/swap controller support, pids controller support, CPU CFS quota/period support, and local daemon access. It also depends on helper images (`busybox`, `debian:trixie-slim`, `syscall-test`, `nnp-test`) and on test helpers that build or ensure those images.

The `DockerDaemonSuite` tests integrate daemon startup/restart flags with runtime enforcement, which catches differences between per-container `--security-opt seccomp=...` and daemon default seccomp policy.

## Risks and Maintenance Notes

The largest risk is cgroup-version drift. Many tests assert cgroup v1 file paths and are skipped under cgroup v2, so coverage may shrink as hosts migrate. Kernel configuration variability is another major risk: memory swap, swappiness, cpuset mems, pids limits, AppArmor, seccomp, `/dev/snd`, and unprivileged user namespaces are not uniformly available.

PTY tests can be timing-sensitive; they use sleeps between escape bytes and timeouts around `cmd.Wait`. Seccomp and capability tests assert specific stderr text such as "Operation not permitted" or "Permission denied", which can vary by runtime, libc, kernel, or image. Host mutation tests require cleanup discipline, especially `/dev/symzero` and temporary mounts.

## Test Signals

Passing tests signal that Linux-specific `docker run` options are translated into actual kernel/runtime state, not only accepted by the CLI. They verify interactive attach detachment, resource limit enforcement, tmpfs/shm/device behavior, seccomp and AppArmor policy application, no-new-privileges, daemon default seccomp profiles, and reduced effective capabilities for non-root or cap-dropped containers.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_run_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_save_load_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_save_load_test.go

## Purpose

`docker_cli_save_load_test.go` defines `DockerCLISaveLoadSuite`, the cross-platform file for image archive save/load integration tests, although most tests require a Linux daemon. It validates `docker save` and `docker load` behavior for repositories, tags, image IDs, archive contents, compression failure paths, parent metadata, missing images, multiple names, and load output messages.

The suite treats image archives as an interoperability boundary: saved image data must preserve inspect metadata where expected, contain the right OCI or legacy archive members, and restore image identity after deletion and reload.

## Important APIs, Types, and Helpers

The main type is `DockerCLISaveLoadSuite`, with teardown and timeout delegated to `DockerSuite`. The suite uses `cli.DockerCmd`, `dockerCmdWithError`, `RunCommandPipelineWithOutput`, `deleteImages`, `inspectField`, `loadSpecialImage`, and `cli.BuildCmd`. It also uses `image.InspectResponse` from `github.com/moby/moby/api/types/image` to compare structured inspect output after save/load.

The tests rely on shell tools invoked with `exec.Command`, including `tar`, `grep`, `xz`, and `gzip`. `icmd.RunCmd` is used where stdin/stdout wiring and expected exit code assertions are central to the test.

## Control Flow and Coverage

The compression tests create an image by running and committing a container, pipe `docker save` through `xz` and/or `gzip`, delete the image, and confirm `docker load` fails when given unsupported nested/compressed data. The important assertion is negative: failed load must not leave the repository inspectable afterward.

`TestSaveSingleTag` tags `busybox`, saves one tag, lists the tar archive, and checks for manifest/index files and the expected image ID. It adjusts expectations when the containerd snapshotter/image store is active. `TestSaveImageId` loads a synthetic empty filesystem image, tags it, obtains long and short IDs, saves by short ID, and checks the archive for the long content-addressed blob path.

`TestSaveAndLoadRepoFlags` pipes `docker save` directly into `docker load`, then compares `docker inspect` JSON before and after. It normalizes `Metadata.LastTagTime` under the snapshotter because that timestamp lives outside the portable archive contract. `TestSaveWithNoExistImage` validates the missing-image error path for `docker save -o`.

`TestSaveMultipleNames` verifies saving multiple repository references for the same image and reading `index.json` to ensure both tags are present. `TestLoadZeroSizeLayer` is skipped and documents a legacy archive format issue around deliberately empty layer files. `TestSaveLoadParents` creates two committed images with a parent-child relationship, saves both, removes the child, reloads, and checks the `Parent` field for legacy graphdriver stores. `TestSaveLoadNoTag` distinguishes load output when saving by image ID versus saving by repository name.

## State and Persistence Behavior

The tests mutate image state by tagging, committing, deleting, saving, and loading images. Several tests intentionally delete images between save and load to ensure restoration is real. Archive data is passed through stdout pipelines or temp files depending on the scenario. Inspect JSON is used as a persisted-state oracle for image identity and metadata.

Parent metadata behavior is explicitly store-dependent: `TestSaveLoadParents` skips when using the containerd snapshotter because the `Parent` image property is not supported there. Snapshotter mode also changes archive structure expectations and inspect timestamp comparisons.

## Dependencies and Integration Points

This suite integrates the CLI image commands, daemon image store, archive exporter/importer, content-addressed blob layout, snapshotter-specific OCI index behavior, and local command pipelines. It depends on external binaries (`tar`, `grep`, `xz`, `gzip`) being present in the test environment. It also depends on `busybox` and the special empty filesystem image helper.

The tests cross the CLI/daemon boundary through stdin/stdout streaming, `-o` and `-i` file options, and structured daemon inspection. That makes them sensitive to both archive format changes and user-facing load/save messages.

## Risks and Maintenance Notes

Archive format evolution is the main risk. The tests already contain conditional logic for snapshotter versus graphdriver behavior and a skipped legacy zero-layer case. Exact output strings such as "Loaded image:", "Loaded image ID:", and "No such image:" are user-facing contracts but can break if wording changes.

Pipelines through compression tools and `tar` make these tests dependent on host utilities. Saving by short ID is used because a TODO notes full image ID save behavior was failing at the time. Parent metadata tests are legacy-store-specific and should not be generalized to containerd image stores without a new contract.

## Test Signals

Passing tests signal that `docker save` emits archives with expected manifest/blob/tag contents, `docker load` restores image identity and metadata where supported, invalid or unsupported input does not create partial images, missing-image errors are clear, and load output correctly distinguishes named images from image-ID-only archives.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_save_load_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_save_load_unix_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_save_load_unix_test.go

## Purpose

`docker_cli_save_load_unix_test.go` is the Unix-only companion for save/load integration behavior that depends on PTYs and Unix stdin/stdout semantics. It verifies streaming save/load through files and stdin, refusal to write archive bytes to a terminal, load progress/conflict messaging, and failure when `docker load` is invoked with an empty terminal-backed stdin.

The file is guarded by `//go:build !windows` and adds tests to `DockerCLISaveLoadSuite`.

## Important APIs, Types, and Helpers

The tests use `cli.DockerCmd`, `dockerBinary`, `deleteImages`, `inspectField`, `build.WithDockerfile`, and `dockerCmdWithError` from the integration harness. `icmd.RunCmd` is used to run CLI commands with explicit stdin/stdout handles. `github.com/creack/pty` provides pseudo-terminal handles for terminal-safety checks. `context.WithTimeout` and `testutil.GetContext` bound the empty-stdin `docker load` case.

## Control Flow and Coverage

`TestSaveAndLoadRepoStdout` creates a container, commits it to `foobar-save-load-test`, saves the image to a temp tar file via stdout, deletes the image, reloads it from the temp file via stdin, and confirms the reloaded image ID matches the committed ID. It then deletes the image again and runs `docker save` with stdin/stdout/stderr all attached to a PTY, expecting failure and a terminal-safety message containing "cowardly refusing".

`TestSaveAndLoadWithProgressBar` builds a small image, saves it to a tar file, removes and retags an older image under the same name, then loads the tar and expects a message that the existing image is being renamed. It is skipped with the snapshotter because that progress/rename path was not implemented there.

`TestLoadNoStdinFail` attaches `docker load` to a PTY with no input and a five-second timeout. It expects the command to fail promptly and emit "requested load from stdin, but stdin is empty" rather than hanging indefinitely.

## State and Persistence Behavior

The tests use temp files for archive storage and persistent image tags to verify deletion and restoration. `TestSaveAndLoadRepoStdout` compares image IDs before deletion and after load, giving a direct persistence signal. The progress-bar test intentionally creates a tag conflict to validate load-time rename behavior and image-store mutation. PTY tests do not persist daemon state beyond attempted commands, but they validate CLI safeguards around terminal I/O.

## Dependencies and Integration Points

This file integrates image archive streaming with Unix file descriptors and terminal detection. It depends on `busybox`, local temp files, PTY support, and normal Unix process semantics. The progress test depends on builder behavior and image-store conflict handling.

## Risks and Maintenance Notes

PTY-driven tests can be sensitive to buffering and exact terminal error messages. The string "cowardly refusing" is a deliberate CLI UX contract but may be brittle. The progress/rename test is skipped under snapshotter, so behavior differs by image store. Empty-stdin failure is timeout-protected to avoid hangs, but slow or unusual terminal behavior could still make the test flaky.

## Test Signals

Passing tests signal that Unix `docker save`/`load` streaming works through regular files and stdin, terminal output safeguards prevent binary tar data from being dumped to a TTY, load handles tag conflicts with user-visible progress messages where supported, and `docker load` fails clearly when no stdin data is provided.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_save_load_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_search_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_search_test.go

## Purpose

`docker_cli_search_test.go` defines `DockerCLISearchSuite`, the integration test suite for `docker search`. It validates CLI search behavior against the central registry, including basic query results, filter validation, official/automated/star filters, no-trunc handling, dash-containing queries, and result limits.

Unlike the other files in this work item, this suite depends directly on external registry behavior and network availability. It primarily protects user-facing CLI parsing and daemon/registry search result formatting.

## Important APIs, Types, and Helpers

The primary type is `DockerCLISearchSuite`, with teardown and timeout delegated to `DockerSuite`. Tests use `cli.DockerCmd` for successful search invocations and `dockerCmdWithError` for invalid filters or invalid limits. Assertions use `gotest.tools/v3/assert` and standard `strings`/`fmt` helpers.

No local helper functions are defined in this file. The important contract is the CLI output shape: header plus result rows separated by newlines, result rows starting with repository names, and error output containing "invalid filter" for malformed filter values.

## Control Flow and Coverage

`TestSearchOnCentralRegistry` searches for `busybox` and expects the output to contain the known description "Busybox base image." `TestSearchStarsOptionWithWrongParameter` sends malformed values for `stars`, `is-automated`, and `is-official` through both long and short filter flags, expecting errors and "invalid filter" text.

`TestSearchCmdOptions` compares unfiltered `busybox` output against filtered results. It asserts that `is-official=false` excludes the official `busybox` row, `is-official=true` returns exactly header, one row, and trailing newline, `stars=10` returns no more rows than the unfiltered result, and combined `is-automated`, `stars`, and `--no-trunc=true` are accepted.

`TestSearchOnCentralRegistryWithDash` verifies that a query ending in a dash (`ubuntu-`) is accepted. `TestSearchWithLimit` checks valid limits of 10, 50, and 100 by counting output lines as `limit + 2`; it also checks that limit 101 errors. The negative limit case is skipped by `continue` with a FIXME because daemon validation did not reject `--limit=-1` consistently.

## State and Persistence Behavior

The search suite does not create daemon objects, images, containers, or local files. State is external and transient: results come from the central registry and can change over time. The only persistent behavior under test is CLI/daemon handling of request parameters and output formatting.

## Dependencies and Integration Points

The tests integrate Docker CLI search parsing, daemon registry search API handling, network access, Docker Hub/central registry search behavior, and formatted CLI output. They assume `busybox` remains an official image with stable enough description text and that search result ordering/counts are predictable for the chosen filters and limits.

## Risks and Maintenance Notes

This is a high-flakiness area because it depends on live registry data, external network connectivity, rate limits, service availability, and mutable search ranking or descriptions. Exact line-count assertions for limits assume the registry returns at least the requested number of rows for `docker`, and exact description checks assume Docker Hub metadata stays stable.

Filter validation tests are less dependent on registry data and provide stronger local signal. The skipped negative-limit validation documents a known mismatch between expected range errors and daemon behavior.

## Test Signals

Passing tests signal that `docker search` can reach the central registry, parse and reject invalid filters, apply official/star/automated filters, preserve output shape for filtered results, accept dash-containing queries, and enforce upper result-limit bounds.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_search_test.go -->
