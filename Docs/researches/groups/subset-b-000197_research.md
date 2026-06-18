# Research: subset-b-000197

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_logs_test.go -->
# sources/cloud-native/moby/integration-cli/docker_api_logs_test.go

Purpose: exercises the Engine API `/containers/{id}/logs` behavior through both raw HTTP requests and the Go client. The file focuses on stdout/stderr option validation, follow behavior, timestamped output, not-found handling, and `until` filtering.

Important APIs, types, and functions: `TestLogsAPIWithStdout`, `TestLogsAPINoStdoutNorStderr`, `TestLogsAPIFollowEmptyOutput`, `TestLogsAPIContainerNotFound`, `TestLogsAPIUntilFutureFollow`, `TestLogsAPIUntil`, and `TestLogsAPIUntilDefaultValue`. It uses `client.ContainerLogsOptions`, `client.ContainerLogs`, `request.Get`, `stdcopy.StdCopy`, `daemonTime`, and integration helpers from `cli` and `testutil`.

Control flow: tests create BusyBox containers with deterministic log-producing commands, wait for container state where needed, then stream or decode log responses. `TestLogsAPIWithStdout` reads the first followed line on a goroutine and bounds it with a 30-second timeout. The `until` tests first collect timestamped logs, derive a cutoff from daemon time or an observed log timestamp, and assert later messages are excluded while `"0"` preserves default behavior.

State and persistence behavior: no repository persistence is changed. Runtime state is Docker daemon container state plus container log buffers. Follow tests deliberately hold HTTP response bodies/readers open and close them in goroutines; `UntilFutureFollow` synchronizes through `chLog` and `stop`.

Dependencies and integration points: depends on the integration daemon, BusyBox image, Docker CLI helpers, raw test HTTP request helpers, Moby client API types, `stdcopy` multiplex decoding, and `containerd/errdefs` for invalid-argument matching. Linux-only gating is used for daemon-time-sensitive follow/until behavior.

Risks and edge cases: timing-heavy tests can be sensitive to slow daemons, log driver delays, or clock skew between test process and daemon. `TestLogsAPIUntil` assumes at least three split log lines and timestamp format stability. The follow-empty-output regression checks response immediacy but does not inspect response status before closing the body.

Test signals: validates successful followed stdout streaming with timestamps, invalid requests with neither stdout nor stderr, immediate follow response for quiet containers, 404 for missing containers, bounded log streaming until future daemon time, exclusion of later logs by timestamp cutoff, and preservation of all logs when `Until` is the default `"0"`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_logs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_network_test.go -->
# sources/cloud-native/moby/integration-cli/docker_api_network_test.go

Purpose: tests Docker Engine network API integration for inspecting networks, creating and deleting user-defined bridge networks, connecting and disconnecting containers, IPAM overlap detection, and rejecting create/delete operations for predefined networks.

Important APIs, types, and functions: `TestAPINetworkInspectBridge`, `TestAPINetworkInspectUserDefinedNetwork`, `TestAPINetworkConnectDisconnect`, `TestAPINetworkIPAMMultipleBridgeNetworks`, `TestAPICreateDeletePredefinedNetworks`, plus helpers `createDeletePredefinedNetwork`, `isNetworkAvailable`, `getNetworkResource`, `createNetwork`, `connectNetwork`, `disconnectNetwork`, and `deleteNetwork`. API payloads use `network.CreateRequest`, `network.IPAM`, `network.IPAMConfig`, `network.ConnectRequest`, `client.NetworkDisconnectOptions`, `network.Inspect`, and `network.CreateResponse`.

Control flow: tests create networks through `/networks/create`, inspect them through `/networks/{id}`, enumerate `/networks`, attach running BusyBox containers via `/connect`, verify addresses against `findContainerIP`, and remove resources through `DELETE /networks/{id}`. The IPAM test creates one bridge network, verifies a second overlapping subnet is forbidden, deletes the first, then verifies the formerly-overlapping network can be created.

State and persistence behavior: state lives in daemon-local network definitions, bridge devices/IPAM allocations, and container endpoint membership. Tests clean up explicit test networks through `deleteNetwork`; the suite teardown handles created containers. Predefined networks are intentionally not mutated because create should return forbidden and delete should not return OK.

Dependencies and integration points: Linux and non-swarm assumptions are enforced with `testRequires`. The file integrates raw API request helpers with Moby network API structs, netip prefix/address parsing, CLI container startup, and `findContainerIP` from the broader integration suite.

Risks and edge cases: fixed private subnets can conflict with host or CI routing. Helper `createNetwork` returns an ID for negative expected status values, but requested tests only use positive expected status codes. Network availability checks are name-based and assume no concurrent unrelated test reuses these names.

Test signals: confirms bridge inspect exposes driver/scope/IPAM/container endpoint data, user-defined network inspect preserves IPAM/options, connect/disconnect updates endpoint state and IP address, overlapping bridge IPAM is rejected until conflicting network removal, automatic IPAM chooses non-overlapping ranges, and predefined `bridge`, `none`, and `host` networks cannot be created or deleted through the API.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_network_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_stats_test.go -->
# sources/cloud-native/moby/integration-cli/docker_api_stats_test.go

Purpose: validates `/containers/{id}/stats` behavior for non-streaming CPU stats, stopped-container stream cleanup, network packet counters, and `one-shot` stats for containers sharing another container's network namespace.

Important APIs, types, and functions: `TestAPIStatsNoStreamGetCpu`, `TestAPIStatsStoppedContainerInGoroutines`, `TestAPIStatsNetworkStats`, `getNetworkStats`, and `TestAPIStatsNoStreamConnectedContainers`. It decodes `container.StatsResponse`, `container.NetworkStats`, and `system.Info`, and uses `request.Get`, `cli.DockerCmd`, `runSleepingContainer`, `findContainerIP`, and host `ping`.

Control flow: CPU tests run a busy shell loop, call `stats?stream=false`, and calculate CPU percentage from Linux-style `CPUStats`/`PreCPUStats` or Windows 100ns interval data. Goroutine cleanup records `/info` `NGoroutines`, opens a stats stream for a stopped container, closes it, and polls until goroutine count returns to baseline. Network stats compare packet counters before and after a host ping. Connected-container stats create a second container using `--net container:<id>` and assert `one-shot` returns exactly one JSON object.

State and persistence behavior: state is transient daemon/container resource accounting. Tests depend on counters, daemon goroutine counts, and network namespace sharing. There is no file persistence. HTTP bodies are explicitly closed to trigger stream teardown.

Dependencies and integration points: integrates Engine stats API, daemon info API, BusyBox workloads, host `ping`, platform-specific counter math, cgroup version gating, local-daemon requirements, and Windows containerd skips. It relies on external process execution for `ping` and includes a Linux AppArmor workaround using the dynamic linker path.

Risks and edge cases: CPU percentage can be zero on unsupported/idle accounting paths, so cgroup v2 is skipped. Goroutine-count assertions can be noisy if unrelated daemon work occurs. Network packet assertions account for ARP on Linux but still depend on host reachability and ping availability. The connected-container test uses a 10-second context to prevent hangs, signaling prior risk in shared-network stats collection.

Test signals: covers JSON content type, non-zero CPU accounting, stream goroutine cleanup after client disconnect, RX/TX packet counter increases after traffic, and one-shot stats returning a single object with the requested container ID for container network namespace sharing.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_stats_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_swarm_node_test.go -->
# sources/cloud-native/moby/integration-cli/docker_api_swarm_node_test.go

Purpose: tests Swarm node API behavior for listing nodes, updating node availability, force-removing nodes, and scheduler reactions to drain and pause availability states.

Important APIs, types, and functions: `TestAPISwarmListNodes`, `TestAPISwarmNodeUpdate`, `TestAPISwarmNodeRemove`, and `TestAPISwarmNodeDrainPause`. It uses `DockerSwarmSuite.AddDaemon`, `daemon.Daemon.ListNodes`, `UpdateNode`, `GetNode`, `RemoveNode`, `RestartNode`, `SwarmInfo`, `CreateService`, `UpdateService`, `CheckActiveContainerCount`, `ActiveContainers`, and shared service helpers `simpleTestService` and `setInstances`.

Control flow: tests build small clusters, inspect returned node IDs against daemon node IDs, mutate `swarm.Node.Spec.Availability`, and poll until scheduler state converges. Drain/pause creates a replicated service over two nodes, drains one node and verifies tasks move, reactivates and resizes the service, then pauses the node and verifies scale-up places only new tasks on the active node.

State and persistence behavior: mutates real swarm cluster state: node membership, node availability, service desired replica count, and task/container placement. `TestAPISwarmNodeRemove` verifies removed node membership is not restored by restarting the daemon. Polling is required because raft replication and scheduler reconciliation are asynchronous.

Dependencies and integration points: `!windows` build-tagged. Uses Moby swarm API types, integration daemon helpers, custom checkers, `poll.WaitOn`, and network availability for force removal. Depends on helper functions and default timeout from `docker_api_swarm_test.go`.

Risks and edge cases: node restart after removal uses a fixed one-second wait, which can be brittle on slow CI. Drain/pause assertions depend on scheduler balancing and may be sensitive to image pull/startup delays. The file assumes the shared service helper creates long-running BusyBox `top` tasks.

Test signals: validates node list completeness, node availability update persistence, force removal preventing rejoin after restart, drain rescheduling all tasks away from a node, reactivation allowing future task placement, and pause preserving existing tasks while blocking new task assignments.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_swarm_node_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_swarm_service_test.go -->
# sources/cloud-native/moby/integration-cli/docker_api_swarm_service_test.go

Purpose: exercises Swarm service API behavior beyond basic cluster management: service creation/listing/inspection, endpoint port updates, replicated and global scheduling, rolling updates and rollbacks, update failure handling, placement constraints, placement preferences, and task replacement after container/process death.

Important APIs, types, and functions: `setPortConfig`, `TestAPIServiceUpdatePort`, `TestAPISwarmServicesEmptyList`, `TestAPISwarmServicesCreate`, `TestAPISwarmServicesMultipleAgents`, `TestAPISwarmServicesCreateGlobal`, `TestAPISwarmServicesUpdate`, `TestAPISwarmServicesUpdateStartFirst`, `TestAPISwarmServicesFailedUpdate`, `TestAPISwarmServiceConstraintRole`, `TestAPISwarmServiceConstraintLabel`, `TestAPISwarmServicePlacementPrefs`, and `TestAPISwarmServicesStateReporting`. It uses `swarm.Service`, `swarm.PortConfig`, `swarm.EndpointSpec`, `swarm.UpdateOrderStartFirst`, `swarm.TaskStateStarting`, `swarm.PlacementPreference`, node labels, `client.ServiceInspectOptions`, and shared constructors from `docker_api_swarm_test.go`.

Control flow: tests create clusters with one or more managers/workers, create services with constructor callbacks, and use polling checks against active container counts, task images, service update state, node readiness, and task placement. Rolling update tests tag images locally, update service specs, observe batch-by-batch image changes, and invoke CLI rollback. Start-first update tests build an unhealthy image, observe new tasks in `Starting`, manually mark them healthy by touching `/status`, and verify old/new task counts during each batch.

State and persistence behavior: mutates swarm raft state for service specs, endpoint specs, update/rollback configs, node labels, placement constraints, and service tasks. It also mutates local daemon image tags and builds a temporary test image. Scheduler state is asynchronous and observed through daemon helper polling. State reporting kills managed containers both through Docker and direct `SIGKILL`, then expects service reconciliation to replace them.

Dependencies and integration points: `!windows` build-tagged. Uses daemon test helpers, Moby client service inspect/update APIs, Docker CLI rollback and build paths, `golang.org/x/sys/unix` for direct process kill, `gotest.tools` assertions, `icmd`, and custom polling/checker utilities. Heavily depends on shared service constructors (`simpleTestService`, `serviceForUpdate`, `setInstances`, `setImage`, `setFailureAction`, `setMaxFailureRatio`, `setParallelism`, `setConstraints`, `setPlacementPrefs`, `setGlobalMode`).

Risks and edge cases: many tests are timing-sensitive and rely on `defaultReconciliationTimeout`. Placement preference expectations assume deterministic spread counts for a three-node topology and four replicas. Constraint tests use short sleeps to let the scheduler try unsatisfiable placements. Start-first update uses healthcheck timing and manual execs into starting tasks. State-reporting is local-Linux-only because it inspects and kills host PIDs.

Test signals: covers empty service lists, service creation/removal, default insertion during service inspect by ID or name, service scaling, leader-side reconciliation across stopped nodes, global services running on newly joined nodes, rolling update and rollback batch sizes, paused failed updates after failure-ratio threshold, role and label constraint enforcement including unsatisfiable constraints, spread placement preferences, endpoint port mutation, and recovery of service replicas after container stop or external process kill.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_swarm_service_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_swarm_test.go -->
# sources/cloud-native/moby/integration-cli/docker_api_swarm_test.go

Purpose: provides the core Swarm API integration tests and shared service-construction helpers used by the swarm node and service test files. It validates cluster initialization, join token handling, CA configuration, manager promotion/demotion, leader proxying/election/quorum, swarm leave/restore paths, manager restart persistence, force-new-cluster recovery, service scaling, unlock/error handling, and repeated root CA rotation.

Important APIs, types, and functions: `defaultReconciliationTimeout`, `TestAPISwarmInit`, `TestAPISwarmJoinToken`, `TestUpdateSwarmAddExternalCA`, `TestAPISwarmPromoteDemote`, `TestAPISwarmLeaderProxy`, `TestAPISwarmLeaderElection`, `TestAPISwarmRaftQuorum`, `TestAPISwarmLeaveRemovesContainer`, `TestAPISwarmLeaveOnPendingJoin`, `TestAPISwarmRestoreOnPendingJoin`, `TestAPISwarmManagerRestore`, `TestAPISwarmScaleNoRollingUpdate`, `TestAPISwarmInvalidAddress`, `TestAPISwarmForceNewCluster`, `simpleTestService`, `serviceForUpdate`, `setInstances`, `setUpdateOrder`, `setRollbackOrder`, `setImage`, `setFailureAction`, `setMaxFailureRatio`, `setParallelism`, `setConstraints`, `setPlacementPrefs`, `setGlobalMode`, `checkClusterHealth`, `TestAPISwarmRestartCluster`, `TestAPISwarmServicesUpdateWithName`, `TestAPISwarmUnlockNotLocked`, `TestAPISwarmErrorHandling`, `TestAPISwarmHealthcheckNone`, and `TestSwarmRepeatedRootRotation`.

Control flow: tests assemble clusters with `AddDaemon`, initialize or join swarm nodes, mutate specs/nodes/services through daemon helpers and raw API calls, and poll for raft/scheduler convergence. Leader and quorum tests stop/start managers to force elections and loss of quorum. Leave and restore tests cover active and pending join states. Restart tests stop all managers/workers concurrently and restart them before checking cluster health from every node. Root rotation loops multiple CA rotations and verifies cluster and node TLS info converge.

State and persistence behavior: this file stresses persistent swarm state in daemon data directories: raft membership, service specs/tasks, join tokens, CA root material, node certificates, manager/worker roles, local node state, and restored manager data after stop/restart/kill. It reads a node certificate from `root/swarm/certificates/swarm-node.crt` to confirm role OU changes after demotion. Force-new-cluster rewrites cluster identity while preserving service continuity on the surviving manager.

Dependencies and integration points: `!windows` build-tagged. Uses Moby client and swarm/container API types, raw request helpers for explicit status-code checks, daemon helper APIs, CFSSL helpers/initca for certificate parsing and root generation, swarmkit CA expiration constants, Go networking for port-conflict setup, and shared checker/poll utilities. Exports practical helper constructors that other swarm test files in this group reuse.

Risks and edge cases: cluster and raft tests are inherently timing-sensitive and skip some architectures for leader election/quorum. Error-message assertions depend on daemon wording. Certificate-file probing assumes the daemon data directory layout. Root rotation polling has bounded retries and may be sensitive to slow certificate propagation. `TestAPISwarmHealthcheckNone` is skipped pending root-cause investigation.

Test signals: validates manager/worker active states across leave/join/restart, required and rotated join tokens, external CA spec preservation with redaction behavior, manager promotion/demotion and last-manager protection, non-leader request proxying, stable leader election, quorum failure and restoration, swarm leave preserving standalone containers while removing service tasks, pending join cleanup/restore, manager data persistence after restart/kill, scale-up without replacing existing containers, invalid address rejection, force-new-cluster recovery, service update by name, unlock error behavior on unlocked swarms, bind-address error handling, full-cluster restart health, and repeated root CA rotation propagation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_swarm_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_test.go -->
# sources/cloud-native/moby/integration-cli/docker_api_test.go

Purpose: defines the `DockerAPISuite` wrapper used by API integration tests in this directory. It delegates lifecycle hooks to the shared `DockerSuite`.

Important APIs, types, and functions: `type DockerAPISuite struct { ds *DockerSuite }`, `TearDownTest(ctx context.Context, t *testing.T)`, and `OnTimeout(t *testing.T)`.

Control flow: the test harness calls suite hook methods; each method forwards directly to the embedded shared suite pointer. There is no test case logic in this file.

State and persistence behavior: no direct state or persistence. The only state is the pointer to `DockerSuite`; cleanup and timeout diagnostic behavior are owned by that shared suite.

Dependencies and integration points: imports `context` and `testing`, and integrates API tests with the broader integration CLI suite lifecycle. Files such as `docker_api_logs_test.go`, `docker_api_network_test.go`, and `docker_api_stats_test.go` attach methods to this suite.

Risks and edge cases: the wrapper assumes `ds` is initialized by the test registration path. A nil `ds` would panic during teardown or timeout handling, but normal suite setup should prevent that.

Test signals: enables consistent teardown and timeout handling for all `DockerAPISuite` tests; it has no standalone assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_attach_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_attach_test.go

Purpose: validates cross-platform Docker CLI `attach` behavior for multiple simultaneous attachments, attach failure without a usable TTY stdin, stdin disconnect semantics, and attach rejection for paused containers.

Important APIs, types, and functions: `attachWait`, `DockerCLIAttachSuite`, `TearDownTest`, `OnTimeout`, `TestAttachMultipleAndRestart`, `TestAttachTTYWithoutStdin`, `TestAttachDisconnect`, and `TestAttachPausedContainer`. It uses `exec.Command`, `StdoutPipe`, `StdinPipe`, `bufio.Reader`, `sync.WaitGroup`, `cli.DockerCmd`, `cli.WaitRun`, `inspectField`, `runSleepingContainer`, and `icmd`.

Control flow: the multiple-attach test starts a long-running echo container, launches three `docker attach` subprocesses, waits until each reads `"hello"`, kills the container, and waits for all attach commands to finish. The TTY-without-stdin test starts an interactive container and expects attach to fail with the "input device is not a TTY" message. The disconnect test attaches to `cat`, sends a line, verifies echo, closes stdin, and confirms the container remains running. The paused test pauses a container and asserts `docker attach` exits with code 1 and the expected error.

State and persistence behavior: state is transient process/container lifecycle and attached stdio streams. No files are persisted. Goroutine and process cleanup is handled with `Wait`, `Kill`, deferred pipe closes, and suite teardown.

Dependencies and integration points: integrates CLI wrappers with direct `os/exec` process handling, the configured `dockerBinary`, daemon feature gates (`DaemonIsLinux`, `IsPausable`), and test result helpers from `gotest.tools/icmd`. The suite wrapper delegates shared cleanup to `DockerSuite`.

Risks and edge cases: attach subprocesses and pipe reads are timing-sensitive and bounded by `attachWait`. Some behavior is Linux-gated due to known Windows TTY instability. The multiple-attach goroutines report errors with `c.Error` from background goroutines, which can make failure ordering less direct. `TestAttachDisconnect` kills the attach command process in cleanup even after stdin close.

Test signals: confirms multiple clients can attach and all detach/exit when the container is killed, TTY attach fails fast without a terminal stdin, closing an attached stdin does not stop a detached interactive container, and paused containers reject attach with a specific error.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_attach_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_attach_unix_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_attach_unix_test.go

Purpose: adds Unix-only pseudo-terminal coverage for CLI attach lifecycle: attach exits cleanly when a container stops, a container can be reattached after using the detach key sequence, and detach leaves the container running.

Important APIs, types, and functions: `TestAttachClosedOnContainerStop`, `TestAttachAfterDetach`, and `TestAttachDetach`. It uses `github.com/creack/pty.Open`, `exec.Command`, pty stdin/stdout/stderr wiring, detach byte sequence `16` then `17` (`Ctrl-p`, `Ctrl-q`), `cli.DockerCmd`, `cli.WaitRun`, `inspectField`, and `bufio.Reader`.

Control flow: the stop test opens a pty, starts `docker attach`, stops the container from a goroutine, waits for `docker wait`, and asserts the attach command exits without error. The after-detach test starts `docker run -ti`, sends the detach sequence through the pty, waits for the original run command to exit, opens a new pty, attaches again, sends a newline, and checks for a shell prompt. The long-ID detach test attaches to a `cat` container, verifies echoed input, sends the detach sequence, waits for attach to exit, and verifies the container is still running.

State and persistence behavior: state is Unix pty file descriptors, subprocess lifecycle, and container runtime state. No repository or daemon configuration is persisted. Tests explicitly close ptys and kill attach processes where needed.

Dependencies and integration points: build-tagged `!windows` and depends on local daemon behavior for pty attach. It extends the `DockerCLIAttachSuite` defined in `docker_cli_attach_test.go` and uses the same `attachWait` timeout constant.

Risks and edge cases: pty timing is fragile, with short sleeps around detach sequence writes and prompt reads. `TestAttachClosedOnContainerStop` requires a local daemon because remote attach/pty behavior can differ. Prompt assertion depends on BusyBox shell prompt text. Deferred process kill in reattach cleanup may race with normal attach exit but is bounded.

Test signals: confirms attach returns on container stop without surfacing an error, detach sequence exits the client while leaving the container alive, reattach after detach reaches an interactive shell, and detach works with a long container ID in TTY mode.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_attach_unix_test.go -->
