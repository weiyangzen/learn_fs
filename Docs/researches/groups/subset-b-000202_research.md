# Research Report: subset-b-000202

Grouped research for Moby integration CLI and integration test files. Each section preserves the source path and is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_service_create_test.go -->
## sources/cloud-native/moby/integration-cli/docker_cli_service_create_test.go

Purpose: verifies `docker service create` behavior for swarm services on non-Windows daemons, especially volume/tmpfs mounts, secrets, configs, and network aliases. Important entry points are `DockerSwarmSuite` tests such as `TestServiceCreateMountVolume`, the secret/config target-path tests, duplicate-reference tests, `TestServiceCreateMountTmpfs`, and `TestServiceCreateWithNetworkAlias`.

Control flow: each test creates a swarm daemon with `s.AddDaemon(ctx, c, true, true)`, issues CLI commands, then polls swarm task state until a task has node and container status. It inspects service specs and concrete containers, unmarshalling JSON into `mount.Mount`, `container.MountPoint`, `swarm.SecretReference`, and `swarm.ConfigReference`.

State and persistence: secrets/configs are created through the API and attached into task files; volumes persist as Docker volumes; tmpfs is runtime-only. Dependencies include swarm API types, CLI helpers, `poll`, and suite `nodeCmd`. Risks are polling races, unordered map iteration, and platform-only semantics. Test signals are spec fields, mounted file contents, `HostConfig.Mounts`, `Mounts`, and alias lists.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_service_create_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_service_health_test.go -->
## sources/cloud-native/moby/integration-cli/docker_cli_service_health_test.go

Purpose: validates swarm task lifecycle integration with container health checks. `TestServiceHealthRun` confirms an initially healthy service task becomes failed when its health check turns unhealthy. `TestServiceHealthStart` confirms an unhealthy-at-start task remains in `TaskStateStarting` until the health check passes.

Important APIs are `cli.BuildCmd` with inline Dockerfiles, `d.GetServiceTasks`, `d.GetTask`, `d.Cmd("inspect", "--format=...")`, and `container.ErrContainerUnhealthy`. Control flow builds custom busybox images with `HEALTHCHECK`, creates a service, polls task state and container health, mutates `/status` with `docker exec`, then asserts swarm task states.

State lives in built images, swarm task status, and container health state. Dependencies include Linux-only busybox behavior, health-check timing, swarm executor errors, and `defaultReconciliationTimeout`. Risks are timing flakes around health transitions and large retry values masking failures. Test signals are `healthy/unhealthy`, failing streaks, `TaskStateStarting`, `TaskStateRunning`, `TaskStateFailed`, and the expected unhealthy-container error.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_service_health_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_service_logs_test.go -->
## sources/cloud-native/moby/integration-cli/docker_cli_service_logs_test.go

Purpose: exercises `docker service logs` across retrieval, ordering, `--tail`, `--since`, `--follow`, task-id addressing, TTY/raw behavior, deleted containers, and log details. The local `logMessage` type coordinates async follow reads; `countLogLines` is a polling helper that runs `service logs -t --raw`.

Control flow creates swarm services that emit deterministic lines, waits for task/container readiness, then runs CLI log queries and validates stdout content. The follow test starts `docker service logs -f` with pipes and scans three log messages before killing the process. The deleted-container test removes the backing container and asserts logs returns within a timeout.

State and persistence are json-file log records, task/container IDs, service metadata, and log-driver detail fields. Dependencies include daemon suite helpers, `icmd`, `poll`, `exec.Command`, pipes, timestamps, and busybox shell loops. Risks include timing/order flakes, stdout/stderr multiplexing differences with TTY, and hung log streams. Test signals are exact log counts, timestamp-derived filtering, task IDs in lines, CRLF raw TTY output, and `--details` key-value text.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_service_logs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_service_scale_test.go -->
## sources/cloud-native/moby/integration-cli/docker_cli_service_scale_test.go

Purpose: checks `docker service scale` accepts valid replicated-service scaling and rejects invalid replica values and global-mode scaling. The single `TestServiceScale` covers a replicated service and a global service.

Control flow creates a swarm daemon, builds platform-specific sleep commands with `sleepCommandForDaemonPlatform`, creates two services, scales `TestService1=2`, and then runs negative cases for `foobar`, `-1`, and `TestService2=2`. State is the swarm service mode and replica count. The file depends on `DockerSwarmSuite`, daemon CLI wrappers, `testutil.GetContext`, and assertion comparators.

Risks are limited but include platform differences in long-running command choice and daemon validation message drift. Integration points are swarm service spec validation and CLI error rendering. Test signals are successful CLI exit for valid scaling and output containing the service name plus either `invalid replicas value` or `scale can only be used with replicated or replicated-job mode`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_service_scale_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_sni_test.go -->
## sources/cloud-native/moby/integration-cli/docker_cli_sni_test.go

Purpose: intended regression coverage that the Docker CLI sets TLS SNI when contacting a registry-like HTTPS endpoint. The suite type forwards teardown and timeout to `DockerSuite`. `TestClientSetsTLSServerName` is currently skipped as flaky.

Control flow would start an `httptest.NewTLSServer`, record `r.TLS.ServerName` for incoming requests, derive the expected server name from the server URL, run `docker pull <hostport>/dockercli/image:latest`, and assert every recorded request used the expected SNI value.

State is in the in-memory slice of observed server names and the transient TLS server. Dependencies include Go `httptest`, `net/url`, `exec.Command`, and the external `dockerBinary`. Risks are inherent flakiness, multiple request attempts, TLS handshake errors, and registry pull behavior that may change before reaching the handler. Test signal is disabled, but if enabled it would fail on missing hits or mismatched TLS ServerName.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_sni_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_start_test.go -->
## sources/cloud-native/moby/integration-cli/docker_cli_start_test.go

Purpose: validates `docker start` behavior around attach mode, exit-code propagation, recorded start errors, paused containers, multiple starts, rename races, restart policies, and `--rm`. The suite wraps `DockerSuite` teardown and timeout.

Control flow uses CLI helpers to create/run containers, stops or waits for them, then invokes `start` variants. Tests use goroutines and timeouts for attach-return behavior, inspect helpers for `State.Error` and running state, and `icmd.Expected` for exit codes. Linux-only cases cover links, pause, and port conflicts.

State includes container runtime state, link dependencies, restart counters, names, port allocation, and inspect `State.Error`. Dependencies are `cli.DockerCmd`, `dockerCmdWithError`, `inspectField`, `runSleepingContainer`, and `icmd`. Risks include races in rename/attach test, timing around container exit, and platform unsupported features. Test signals include exact output, nonzero errors, exit codes 1/11/12/137, paused-container message, and correct running states after partial multi-container starts.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_start_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_stats_test.go -->
## sources/cloud-native/moby/integration-cli/docker_cli_stats_test.go

Purpose: covers `docker stats` CLI behavior on Linux: non-streaming completion, not-found errors, default running-only scope, `--all`, dynamic inclusion of newly created containers, and formatting.

Control flow starts busybox containers, waits for running/exited states, then invokes `stats` through `exec.Command` or CLI helpers. `TestStatsNoStream` guards with a three-second timeout; streaming behavior is tested by reading stdout with a scanner while creating another container. Regex checks ensure stats columns contain nonzero data for running containers and zeros for stopped containers under `--all`.

State is live cgroup/container metrics exposed by the daemon and CLI table rendering. Dependencies include Linux stats support, busybox `top`, `bufio.Scanner`, regex, and timeouts. Risks are resource-metric timing, output column assumptions after the 12-character ID, and streaming process cleanup. Test signals are container IDs/names in output, absence of stopped containers without `--all`, not-found messages, and formatted `{{.Name}}` output.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_stats_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_swarm_test.go -->
## sources/cloud-native/moby/integration-cli/docker_cli_swarm_test.go

Purpose: broad non-Windows integration coverage for swarm CLI and daemon behavior. It spans swarm init/update, external CAs, IPv6 joins, service/node/task filters, publish updates, overlay attachable networks, ingress lifecycle, remote plugin rejection, env/TTY/DNS/service-network updates, autolock and unlock-key rotation, manager/worker lock state, network/IPAM edge cases, node availability, readonly rootfs, stop signals, join/leave loops, and cluster event filtering.

Important helpers include `setupRemoteGlobalNetworkPlugin`, `getNodeStatus`, `checkKeyIsEncrypted`, `checkSwarmLockedToUnlocked`, `checkSwarmUnlockedToLocked`, `waitForEvent`, and `getUnlockKey`. Tests heavily use `daemon.Daemon`, swarm API types, CLI helpers, `pollCheck`, `reducedCheck`, `net/http/httptest`, libnetwork plugin endpoints, netlink veth creation, PEM/certificate parsing, and swarmkit key encryption helpers.

Control flow usually starts one or more daemons via `s.AddDaemon`, applies CLI operations, then polls swarm, task, node, network, or event state. Plugin tests create `/etc/docker/plugins/*.spec` and HTTP handlers. Autolock tests restart daemons to force locked/unlocked transitions and read `root/swarm/certificates/swarm-node.key`. Event tests bound queries by daemon time and filter scope/type.

State includes raft/swarm specs, overlay networks, service specs, task containers, node membership, unlock keys, encrypted key files, plugin spec files, and event streams. Risks are high: timing-sensitive raft convergence, leader availability, debug-log matching for KEK rotation, host-global `/etc/docker/plugins` mutation, architecture skips, and event ordering. Test signals are CLI output/errors, swarm spec fields, task counts, network inspect data, node local state, encrypted PEM state, and event text containing expected IDs and attributes.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_swarm_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_swarm_unix_test.go -->
## sources/cloud-native/moby/integration-cli/docker_cli_swarm_unix_test.go

Purpose: Unix-only swarm plugin coverage. `TestSwarmVolumePlugin` verifies a service task remains pending when a requested volume plugin is missing, then schedules once the plugin is available. `TestSwarmNetworkPluginV2` validates global network plugin scheduling across manager and worker nodes and behavior after disabling the plugin on one node.

Control flow starts swarm daemons, creates services/networks with plugin drivers, polls task states and active container counts, inspects container mounts, and installs/disables a v2 plugin by name. State includes plugin availability, service task scheduling, overlay/global network membership, and volume mount metadata.

Dependencies are suite plugin helpers such as `newVolumePlugin`, daemon CLI wrappers, swarm task-state checks, `reducedCheck`, and amd64-only plugin image availability. Risks include external plugin image availability, 20-second fixed sleep after plugin disable, plugin lazy loading, and long swarm reconciliation delays. Test signals are pending task error `missing plugin on 1 node`, one running task after plugin load, mount `Name`/`Driver`, and only one global-service instance when one node lacks the network plugin.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_swarm_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_top_test.go -->
## sources/cloud-native/moby/integration-cli/docker_cli_top_test.go

Purpose: validates `docker top` process listing across Linux and Windows paths, including argument handling, nonprivileged containers, Windows core processes, and privileged Linux containers.

Control flow starts long-running containers via `runSleepingContainer` or explicit privileged `docker run`, runs `docker top` once or twice, then checks output. `TestTopMultipleArgs` branches expected behavior by daemon OS: Linux should show a `PID` header for `-o pid`, Windows should reject extra arguments. Windows-specific coverage looks for core process names. Linux privileged coverage is skipped under user namespaces.

State is the process list inside a running container and platform-specific process model. Dependencies include `DockerCLITopSuite`, `cli.Docker`, `icmd`, requirement gates, and platform defaults. Risks are output-format drift, Windows process-name assumptions, and userns restrictions. Test signals are CLI output containing `top` or `busybox.exe`, Windows process names, expected error text, and repeated successful listings.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_top_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_update_test.go -->
## sources/cloud-native/moby/integration-cli/docker_cli_update_test.go

Purpose: declares `DockerCLIUpdateSuite`, a thin suite container shared by platform-specific update tests. The file has no tests or helper methods beyond the `ds *DockerSuite` field.

Control flow and behavior are provided by companion files such as `docker_cli_update_unix_test.go`. State is limited to the embedded suite pointer used for teardown and timeout forwarding in platform files. Dependencies are only package `main` and `DockerSuite` from the integration CLI harness.

Risks are structural: removing or renaming this type would break methods declared in build-tagged companion files. Test signals are indirect; the Go test compiler links methods with this suite type, and suite registration elsewhere depends on the type existing.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_update_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_update_unix_test.go -->
## sources/cloud-native/moby/integration-cli/docker_cli_update_unix_test.go

Purpose: Unix/Linux coverage for `docker update` resource mutation semantics. Tests cover running, restarted, stopped, and paused containers; untouched fields; invalid memory values; swap memory; stats memory-limit stability; restart monitor behavior; and NanoCPUs conflicts/updates.

Control flow starts containers with memory/CPU settings, runs `docker update`, inspects `HostConfig`, and reads cgroup files inside containers. Some tests call the API stats endpoint, attach through a pty to exit a restart-policy container, or inspect through the Go client. Requirement gates skip unsupported cgroup and Linux capabilities; several tests skip cgroups v2.

State includes container `HostConfig`, kernel cgroup files, API stats responses, restart count, and NanoCPUs fields. Dependencies include `cli`, `dockerCmdWithError`, `inspectField`, `request.Get`, `creack/pty`, and cgroup feature probes. Risks are cgroup v1-specific paths, kernel validation ordering, resource feature variability, and pty cleanup. Test signals are exact byte values, error messages, unchanged memory stats, restart count `1`, and conflict messages for CPU quota versus NanoCPUs.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_update_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_userns_test.go -->
## sources/cloud-native/moby/integration-cli/docker_cli_userns_test.go

Purpose: tests daemon user namespace remapping with `--userns-remap=default` and vfs storage. It validates UID/GID maps, host file ownership for bind mounts, auto-created bind source directories, and per-container `--userns host` override.

Control flow starts the daemon with remapping, runs containers, derives the remapped UID/GID from the daemon root directory basename, chowns a temp directory, mounts existing and non-existing host paths, and inspects `/proc/<pid>/uid_map` and `gid_map` through a shell pipeline. `findUser` parses `docker top` output to identify the process user.

State includes daemon root path, host filesystem ownership, running container PID namespace mappings, and created bind directories/files. Dependencies include Linux user namespace kernel support, `RunCommandPipelineWithOutput`, `stringid`, and `syscall.Stat_t`. Risks include assumptions about daemon root naming, root privileges for chown, and `/proc` availability. Test signals are `stat` output `0:0` in-container, remapped user in `top`, matching uid/gid maps, and root user under `--userns host`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_userns_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_v2_only_test.go -->
## sources/cloud-native/moby/integration-cli/docker_cli_v2_only_test.go

Purpose: registry regression test ensuring daemon operations do not contact Docker registry v1 endpoints. `makefile` creates temporary Dockerfiles; `TestV2Only` uses a mock registry with `/v2/` and `/v1/.*` handlers.

Control flow registers `/v2/` to return 404 and `/v1/.*` to fail the test immediately, starts the daemon with the mock registry as insecure, creates a Dockerfile referencing the registry, then attempts build, run, login, tag, push, and pull. Errors from those operations are intentionally ignored because the signal is whether the v1 handler is touched.

State is the mock registry handler set, temporary build directory, daemon registry configuration, image tags, and login attempt. Dependencies include `internal/testutil/registry`, `net/http`, temp files, and `DockerRegistrySuite`. Risks are that ignored command errors can hide other behavior, but any v1 request remains a hard failure. Test signal is absence of the fatal v1 endpoint hit.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_v2_only_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_volume_test.go -->
## sources/cloud-native/moby/integration-cli/docker_cli_volume_test.go

Purpose: comprehensive CLI coverage for Docker volumes: create, inspect, list formats, filters, remove/force behavior, labels, driver/options, in-use semantics, and duplicate mountpoint resolution for `--volumes-from`, binds, and API mounts.

Important APIs and helpers include `DockerCLIVolumeSuite`, `assertVolumesInList`, CLI wrappers, Go client `ContainerCreate`, `container.HostConfig`, `mount.Mount`, and `network.NetworkingConfig`. Control flow creates volumes and containers, runs commands with `-v` or `--volumes-from`, inspects volume/containers, and sometimes manipulates the local volume directory to simulate missing mountpoints.

State and persistence are core: named volumes retain data across container removal, labels/options persist in volume metadata, and in-use reference counts include both created and started containers. Dependencies include local daemon access for some tests, Linux tmpfs mount semantics, and build helper images. Risks include host filesystem mutation, filter output assumptions, and legacy mount conflict behavior that is intentionally preserved. Test signals are volume list/inspect output, error messages, persisted `hello` data, tmpfs mount options, label filtering, and absence/presence of volume references after duplicate-target scenarios.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_volume_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_hub_pull_suite_test.go -->
## sources/cloud-native/moby/integration-cli/docker_hub_pull_suite_test.go

Purpose: defines `DockerHubPullSuite`, an isolated daemon suite for pull/push tests that need a clean image store rather than the globally preloaded integration daemon.

Control flow: `SetUpSuite` requires Linux and a local daemon, constructs a `daemon.Daemon` with the current environment, and starts it. `SetUpTest` requires network access. `TearDownTest` removes all images from the suite daemon and delegates generic cleanup to `DockerSuite`. `Cmd`, `CmdWithError`, and `MakeCmd` wrap `docker --host <suite-sock>` invocations.

State is the dedicated daemon, its image store, and the suite socket path. Dependencies include `integration-cli/daemon`, `internal/testutil/daemon`, network requirement checks, and `exec.Command`. Risks include reliance on Docker Hub/network availability, destructive image cleanup within the isolated daemon, and command wrappers that use combined output. Test signals are indirect: consuming tests get a fresh daemon and fail through `assert.Assert` on nonzero command errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_hub_pull_suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_utils_test.go -->
## sources/cloud-native/moby/integration-cli/docker_utils_test.go

Purpose: shared integration-CLI utility layer for Docker command execution, inspect helpers, file IO, daemon time, environment construction, sleeping containers, goroutine polling, error decoding, polling composition, and special image loading.

Important functions include `dockerCmdWithError`, `inspectField`, `inspectMountPoint`, `daemonTime`, `daemonUnixTime`, `appendBaseEnv`, `runSleepingContainer`, `getGoroutineNumber`, `waitForStableGoroutineCount`, `pollCheck`, `reducedCheck`, `sumAsIntegers`, and `loadSpecialImage`. Control flow is mostly helper wrapping: run CLI/API commands, parse JSON or text, poll until comparisons pass, and fail tests on unexpected errors.

State touches daemon image/container stores, host container storage files, temp tar/image paths, and API `Info` fields. Dependencies include `cli`, `client`, `daemon`, `archive`, `specialimage`, `icmd`, and `poll`. Risks are deprecated helpers preserving old behavior, direct host storage reads, fragile text parsing of `docker info`, and poll timeouts hiding slow convergence. Test signals are helper-level assertions, returned IDs/fields, stable goroutine counts, decoded error messages, and loaded image refs.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/environment/environment.go -->
## sources/cloud-native/moby/integration-cli/environment/environment.go

Purpose: small wrapper around `internal/testutil/environment.Execution` that records the Docker CLI binary path for integration CLI tests.

Important API: package variable `DefaultClientBinary` reads `TEST_CLIENT_BINARY`, `init` defaults it to `docker`, `Execution` embeds `environment.Execution` and stores `dockerBinary`, `DockerBinary` returns that path, and `New` constructs the base environment then resolves the CLI via `exec.LookPath`.

Control flow is straightforward: environment discovery happens first, then binary lookup, then a pointer to the composed `Execution` is returned. State is process environment plus the embedded daemon/test environment. Dependencies are Go `os`, `os/exec`, and Moby testutil environment package. Risks are missing `docker` binary, stale `TEST_CLIENT_BINARY`, and shadowing between client binary and daemon binary. Test signals are startup failures from `New` and later use of `DockerBinary()` by suites.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/environment/environment.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/events_utils_test.go -->
## sources/cloud-native/moby/integration-cli/events_utils_test.go

Purpose: utility support for CLI event tests. It defines matcher/processor function types, `eventObserver` for long-running `docker events`, regex-style event parsing helpers, and event action filtering by ID/type.

Control flow: `newEventObserver` computes a daemon-relative `--since` timestamp, prepares an `exec.Cmd`, and attaches stdout to a scanner. `Start` launches it; `Match` scans lines, buffers them, and invokes a processor for matches. `CheckEventError` recovers from scanner disconnects by querying `docker events --since/--until`. Matching uses `eventstestutils.ScanMap` and can resolve IDs through event attributes.

State includes the observer buffer, command process, scanner error, and channels closed or signaled by `processEventMatch`. Dependencies include daemon time helpers, Docker CLI, containerd logging, and event test utilities. Risks are event stream disconnections, race windows around since/until, and simple comma/equals parsing of attributes. Test signals are observed action channels, fatal diagnostics with buffered output, and parsed action lists.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/events_utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/fixtures/auth/docker-credential-shell-test -->
## sources/cloud-native/moby/integration-cli/fixtures/auth/docker-credential-shell-test

Purpose: shell credential-helper fixture implementing the Docker credential helper protocol commands `store`, `get`, `erase`, and `list` for auth integration tests.

Control flow branches on `$1`. `store` reads JSON from stdin, extracts `ServerURL`, `Username`, and `Secret` with `jq`, hashes the server with `sha1sum`, writes credentials under `$TEMP/$hash`, and updates a JSON server-to-username list. `get` hashes stdin and returns the stored payload or exits with `credentials not found in native keychain`. `erase` deletes the credential file and removes the server from the list. `list` returns `{}` or the saved list.

State persists in temporary files under `$TEMP`, especially `shell_test_list.json` and hashed credential files. Dependencies are bash, `jq`, `sha1sum`, `awk`, and `$TEMP`. Risks include unquoted JSON values, concurrent tests sharing `$TEMP`, and missing list file during erase. Test signals are JSON stdout payloads and nonzero exit on unknown or missing credentials.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/fixtures/auth/docker-credential-shell-test -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/fixtures/credentialspecs/valid.json -->
## sources/cloud-native/moby/integration-cli/fixtures/credentialspecs/valid.json

Purpose: static Windows credential spec fixture representing a valid Group Managed Service Account configuration for integration tests that parse or submit credential specs.

Structure: top-level `CmsPlugins` contains `ActiveDirectory`; `DomainJoinConfig` supplies SID, machine account name, GUID, DNS tree/name, and NetBIOS name; `ActiveDirectoryConfig.GroupManagedServiceAccounts` lists the account name scoped to both `hyperv.local` and `hyperv`.

State is immutable fixture data. Dependencies are consumers that expect Docker credential-spec JSON schema shape and Windows/Active Directory semantics. Risks are schema drift, tests assuming exact whitespace-insensitive JSON fields, and the fixture being used on non-Windows paths without requirement gates. Test signals are successful JSON parsing and validation by credential-spec code; failures would usually be invalid field names, missing gMSA data, or malformed GUID/SID strings.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/fixtures/credentialspecs/valid.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/fixtures_linux_daemon_test.go -->
## sources/cloud-native/moby/integration-cli/fixtures_linux_daemon_test.go

Purpose: builds or loads Linux-only fixture images used by daemon integration tests: `syscall-test` and `nnp-test` for syscall/seccomp/no-new-privileges scenarios.

Control flow: `ensureSyscallTest` and `ensureNNPTest` first protect the image and return if it already exists. If daemon OS differs from host OS, they delegate to Docker-build paths that load frozen Debian images. Otherwise they compile C fixtures with `gcc`, write a temporary Dockerfile, honor `DOCKER_BUILD_ARGS`, and run `docker build`. The NNP image sets a setuid bit; syscall image optionally builds a 32-bit exit binary on linux/amd64.

State includes protected images, temporary build dirs, compiled binaries, Dockerfiles, and frozen base image availability. Dependencies include local `gcc`, `debian:trixie-slim`, contrib fixture sources, and `load.FrozenImagesLinux`. Risks include typo-like tag mismatch in `ensureNNPTestBuild` (`npp-test`), cross-platform build slowness, missing compiler, and environment build args. Test signals are successful image existence/protection and build command success.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/fixtures_linux_daemon_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/requirements_test.go -->
## sources/cloud-native/moby/integration-cli/requirements_test.go

Purpose: central requirement-gating helpers for integration CLI tests. Functions report daemon OS, architecture, network availability, AppArmor, snapshotter mode, userns support, pause support, registry hosting, swarm inactivity, and BuildKit mode.

Control flow is mostly predicate evaluation against `testEnv.DaemonInfo`, environment variables, filesystem probes, HTTP GET to Docker Hub, or lightweight Docker/API calls. `testRequires` iterates predicates and skips the test with a derived requirement name when any returns false.

State observed includes daemon info, host `/proc` and `/sys` files, environment variables, registry binary PATH, swarm local node state, and existing networks. Dependencies include Docker client, containerd plugin constants, registry utilities, and Go reflection/runtime to format skip names. Risks are network probe panics on errors, predicates with side effects such as running a container for read-only userns, and requirement names derived from function symbols. Test signals are skip decisions, not pass/fail assertions, but incorrect predicates can hide coverage or run unsupported tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/requirements_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/requirements_unix_test.go -->
## sources/cloud-native/moby/integration-cli/requirements_unix_test.go

Purpose: Unix-specific requirement predicates for cgroup, memory, swap, blkio, seccomp, and unprivileged user namespace support.

Control flow initializes global `sysInfo` via `sysinfo.New()` in `setupLocalInfo`, then individual functions read either `testEnv.DaemonInfo` fields, `sysInfo` fields, cgroups mode, or `/proc/sys/kernel/unprivileged_userns_clone`. Some predicates additionally require a local daemon.

State observed includes kernel cgroup mode, daemon resource feature flags, and sysinfo capability probes. Dependencies are containerd cgroups v3 and Moby `pkg/sysinfo`. Risks include global `sysInfo` needing initialization before use, cgroup v2 skip behavior in older tests, and rootless/local-daemon differences. Test signals are skip gating for resource-management tests; wrong values produce either unsupported test execution or lost coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/requirements_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/requirements_windows_test.go -->
## sources/cloud-native/moby/integration-cli/requirements_windows_test.go

Purpose: Windows build companion for requirement helpers. `setupLocalInfo` is a no-op and `onlyCgroupsv2` always returns false.

Control flow is intentionally empty because Windows does not use the Unix `sysinfo`/cgroups path. State and persistence are none. Dependencies are only package `main` and build selection by filename/build constraints.

Risks are semantic drift if tests begin relying on other Unix-only requirement helpers without Windows counterparts. Test signals are indirect through compilation and skip decisions: Windows builds can link shared tests that call `setupLocalInfo` or `onlyCgroupsv2` without importing Unix-only packages.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/requirements_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/test_vars_test.go -->
## sources/cloud-native/moby/integration-cli/test_vars_test.go

Purpose: platform-neutral helper that chooses a long-running container command for the daemon OS. `sleepCommandForDaemonPlatform` returns `["sleep", "240"]` for Windows because Windows busybox lacks `top`, and `["top"]` otherwise.

Control flow is a simple branch on `testEnv.DaemonInfo.OSType`. State is read-only daemon platform metadata. Dependencies are package-level `testEnv` and companion platform constants.

Risks are tests assuming `top` behavior on Windows or the fixed 240-second sleep being insufficient for slow tests. Integration points are service scale tests, container lifecycle helpers, and any test needing an idle container. Test signals are indirect: containers remain running long enough for subsequent CLI/API assertions on supported platforms.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/test_vars_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/test_vars_unix_test.go -->
## sources/cloud-native/moby/integration-cli/test_vars_unix_test.go

Purpose: Unix build constants for integration CLI tests. It sets `isUnixCli = true` and `expectedFileChmod = "-rw-r--r--"`.

Control flow and state are compile-time only. The constants feed shared tests that branch on CLI platform or compare formatted permissions. Dependencies are Go build tags (`!windows`) and package `main`.

Risks are limited to permission-format assumptions and ensuring Windows builds use the companion file instead. Test signals are indirect through shared file permission and CLI-platform assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/test_vars_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/test_vars_windows_test.go -->
## sources/cloud-native/moby/integration-cli/test_vars_windows_test.go

Purpose: Windows build constants for integration CLI tests. It sets `isUnixCli = false` and uses Windows expected chmod rendering `"-rwxr-xr-x"` for historical compatibility.

Control flow and state are compile-time only. Dependencies are Windows build selection and shared tests that use `UnixCli` or `expectedFileChmod`.

Risks include stale permission expectation if Windows CLI output changes. Test signals are indirect through platform-conditional assertions in shared test files.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/test_vars_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/utils_test.go -->
## sources/cloud-native/moby/integration-cli/utils_test.go

Purpose: general cross-platform helpers for integration CLI tests. It normalizes daemon paths, parses cgroup files, creates random temp paths, runs command pipelines, lists existing Docker objects, and filters pre-existing objects from CLI output.

Important APIs are `getPrefixAndSlashFromDaemonPlatform`, `dPath`, `ParseCgroupPaths`, `RandomTmpDirPath`, `RunCommandPipelineWithOutput`, `existingElements`, `ExistingContainerIDs`, `ExistingContainerNames`, `RemoveLinesForExistingElements`, and `RemoveOutputForExistingElements`.

Control flow is text and process oriented: convert paths by daemon OS, split `/proc/<pid>/cgroup` lines into controller paths, wire stdout pipes between commands, and remove matching lines by substring. State observed includes `testEnv.DaemonInfo`, environment `TEMP`, and current Docker object lists. Dependencies include `cli`, `exec.Cmd`, and `testutil.GenerateRandomAlphaOnlyString`. Risks include substring false positives when filtering output, pipeline wait error handling, and Windows path conversion edge cases. Test signals are helper returns used by many tests to make assertions deterministic.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/utils_unix_test.go -->
## sources/cloud-native/moby/integration-cli/utils_unix_test.go

Purpose: Unix implementation of `getLongPathName`. It is a no-op because Unix paths do not have Windows short-name expansion.

Control flow simply returns the input path and nil error. State and persistence are none. Dependencies are package `main` and Unix build selection.

Risks are minimal; shared callers must still handle the `(string, error)` signature. Test signals are indirect through path-normalization tests that compile/run on Unix without Windows syscall dependencies.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/utils_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/utils_windows_test.go -->
## sources/cloud-native/moby/integration-cli/utils_windows_test.go

Purpose: Windows implementation of `getLongPathName`, expanding short 8.3-style path components such as `ADMIN~1` to long names using Windows APIs.

Control flow converts the input string to UTF-16, calls `windows.GetLongPathName` with an initial buffer, reallocates if the return length exceeds the buffer, and converts the result back to a Go string. State is only the path queried from the Windows filesystem. Dependencies are `golang.org/x/sys/windows`.

Risks include UTF-16 conversion failures, race with filesystem changes, and buffer-size handling. Test signals are returned long paths or propagated errors for callers that normalize Windows filesystem output.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/utils_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/capabilities/capabilities_linux_test.go -->
## sources/cloud-native/moby/integration/capabilities/capabilities_linux_test.go

Purpose: verifies `no-new-privileges=true` interacts correctly with file capabilities. It builds an image where `/bin/cat` has `CAP_DAC_OVERRIDE` and a non-root user attempts to read a root-only file.

Control flow creates a fake build context with a Dockerfile, builds the image through the API, then runs two subtests. One requests `CAP_DAC_OVERRIDE` and expects stdout `hello`; the other drops the capability and expects an operation-not-permitted stderr. Both runs set user `test` and security option `no-new-privileges=true`, wait for exit, and read logs via `stdcopy`.

State includes a built test image, container capability sets, file capability metadata, and logs. Dependencies include Linux base image, `libcap2-bin`, internal container helpers, fakecontext, and API log demultiplexing. Risks are package install/network behavior during build, capability semantics across kernels, and exact error text. Test signals are trimmed stdout/stderr matching the expected strings.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/capabilities/capabilities_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/capabilities/main_linux_test.go -->
## sources/cloud-native/moby/integration/capabilities/main_linux_test.go

Purpose: test harness setup for the Linux capabilities integration package. It configures tracing, creates the shared test environment, ensures frozen Linux images are available, prints environment information, runs tests, and cleans tracing state.

Control flow in `TestMain` starts an OpenTelemetry span, calls `environment.New`, calls `environment.EnsureFrozenImagesLinux`, runs `m.Run`, marks the span on failure, ends tracing, and exits with the test code. `setupTest` starts a per-test span, protects all known resources, and registers environment cleanup.

State includes global `testEnv` and `baseContext`, tracing spans, protected images/resources, and environment-managed cleanup state. Dependencies are `internal/testutil`, `internal/testutil/environment`, and OpenTelemetry. Risks are fatal setup failure if environment discovery or frozen-image loading fails; all package tests depend on this global setup. Test signals are package startup success and cleanup isolation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/capabilities/main_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/config/config_test.go -->
## sources/cloud-native/moby/integration/config/config_test.go

Purpose: API-level swarm config integration tests. Coverage includes inspect raw JSON fidelity, listing and filters, create/delete errors, label updates, rejection of data updates, templated configs referencing secrets/configs, and ID/name-prefix resolution.

Important functions are `createConfig`, `configNamesFromList`, and tests such as `TestConfigInspect`, `TestConfigList`, `TestConfigsUpdate`, `TestTemplatedConfig`, and `TestConfigCreateResolve`. Control flow starts a swarm via `integration/internal/swarm`, creates configs/secrets through the Go client, lists/inspects/updates/removes them, and for templating creates a service, waits for a running task, execs `cat /templated_config`, and checks tmpfs mount output.

State includes swarm configs, labels, versions, secrets, services, task files, and raw API JSON. Dependencies include client config APIs, errdefs, swarm helpers, `stdcopy`, `poll`, and Windows skips. Risks include swarm convergence timing, config version requirements, templating semantics, and name-vs-ID ambiguity. Test signals are list names, not-found/invalid-argument errors, updated labels, rendered config content, tmpfs mount text, and successful prefix resolution rules.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/config/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/config/main_test.go -->
## sources/cloud-native/moby/integration/config/main_test.go

Purpose: package-level setup for integration config tests. It initializes tracing and the Moby test environment, ensures frozen Linux images, prints environment diagnostics, runs the package tests, and provides per-test cleanup.

Control flow mirrors other integration packages: `TestMain` creates a root context/span, calls `environment.New`, loads frozen images, runs `m.Run`, records nonzero exit status on the span, shuts tracing down, and exits. `setupTest` starts a span from `baseContext`, protects all resources, and schedules `testEnv.Clean`.

State includes global `testEnv`, `baseContext`, tracing spans, protected resources, and environment cleanup. Dependencies are `internal/testutil`, `internal/testutil/environment`, and OpenTelemetry. Risks are global setup failure blocking all config tests and cleanup mistakes leaking swarm/config resources between tests. Test signals are successful environment setup and deterministic cleanup isolation for `config_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/config/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/attach_test.go -->
## sources/cloud-native/moby/integration/container/attach_test.go

Purpose: API-level attach behavior tests. `TestAttach` verifies attach response media type differs for TTY and non-TTY containers. `TestAttachDisconnectLeak` is a Linux regression test for goroutine leaks after attach disconnect.

Control flow creates containers through the Go client, calls `ContainerAttach`, and reads `attach.MediaType()`. The leak test starts a fresh daemon to isolate goroutine counts, creates a long-running container, records stable goroutine count, attaches stdout, waits for count increase, closes the attach stream, then polls for the original count.

State includes container config TTY flag, attach HTTP connection, daemon goroutine count, and a dedicated daemon lifecycle. Dependencies include API client, internal container/system helpers, `daemon.New`, `poll`, and Linux skip. Risks are goroutine-count noise, timeout sensitivity, and attach stream cleanup. Test signals are media types `application/vnd.docker.multiplexed-stream` or raw stream and goroutine count returning to baseline.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/attach_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/cdi_test.go -->
## sources/cloud-native/moby/integration/container/cdi_test.go

Purpose: integration coverage for Container Device Interface support. Tests verify CDI device requests are persisted and applied, CDI spec dirs appear in system info, discovered devices are exposed, and `/etc/cdi` is honored even in rootless-related paths.

Control flow starts isolated daemons with `--cdi-spec-dir`, config files, or `--feature cdi`; writes sample CDI JSON specs; runs containers with `container.WithCDIDevices`; inspects `HostConfig.DeviceRequests`; reads container logs for injected env; and checks `Info.CDISpecDirs` and `Info.DiscoveredDevices`.

State includes daemon CDI feature config, spec directories/files, discovered device list, container device requests, and temporary or `/etc/cdi` host files. Dependencies include local daemon control, Linux, non-remote daemon, testdata CDI specs, system info API, and cleanup of `/etc/cdi` artifacts. Risks are host-global `/etc/cdi` mutation, rootless permission differences, Windows skips, and exact default spec-dir expectations. Test signals are expected `DeviceRequest`, `FOO=injected`, exact `CDISpecDirs`, and expected `system.DeviceInfo`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/cdi_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/checkpoint_test.go -->
## sources/cloud-native/moby/integration/container/checkpoint_test.go

Purpose: intended checkpoint/restore integration test using CRIU, but the test is currently unconditionally skipped as broken. It documents desired behavior for creating checkpoints with and without stopping the container, listing checkpoints, restoring from a checkpoint, and removing checkpoints.

Control flow after the skip would require non-Windows experimental daemon, run `criu check`, start a container with tmpfs, bind `true` over ip6tables tools to avoid missing modules, create checkpoint `test` with `Exit:false`, create a file, create checkpoint `test2` with `Exit:true`, restore with `CheckpointID:test2`, verify file existence, and remove both checkpoints.

State would include CRIU dump files, container running/exited state, checkpoint metadata, tmpfs contents, and temporary bind mounts on host binaries. Dependencies include CRIU, experimental daemon, request API client, internal container helpers, and host mount privileges. Risks are high and acknowledged by the skip: host mutation, CRIU/kernel variability, dump-log parsing, and cleanup complexity. Test signal is currently only the skip.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/checkpoint_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/container_test.go -->
## sources/cloud-native/moby/integration/container/container_test.go

Purpose: validates JSON request-body error handling for Docker API POST endpoints that expect JSON. It ensures unsupported content types, invalid JSON, trailing content, and empty body cases return appropriate client errors rather than server errors.

Control flow iterates endpoints `/commit`, `/containers/create`, `/containers/foobar/exec`, `/containers/foobar/update`, and `/exec/foobar/start`. For each endpoint it runs parallel subtests posting raw strings with `request.Post`, either `ContentType("text/plain")` or `request.JSON`, then reads response bodies and checks status/message content.

State is only HTTP request/response state against the test daemon. Dependencies include `internal/testutil/request`, per-test spans from `setupTest`, and Go HTTP status constants. Risks are exact error-message drift and parallel subtests sharing the same daemon, though requests are independent. Test signals are `400 Bad Request` for invalid content type/JSON/trailing content, body messages with specific diagnostics, and empty-body status below 500.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/container_test.go -->
