# subset-b-000207 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/service/create_test.go -->
# sources/cloud-native/moby/integration/service/create_test.go

## Purpose
Exercises Docker Swarm service creation paths against real daemons. The file validates service `Init`, repeated create/remove cycles, name conflict handling, max replica scheduling, secret/config file modes, sysctl and capability propagation, and resource knobs for memory swap and memory swappiness.

## Important APIs, Types, And Functions
- `TestServiceCreateInit` and `testServiceCreateInit` start swarms with and without `daemon.WithInit()` and compare generated task container `HostConfig.Init`.
- `inspectServiceContainer` locates the one task container by `com.docker.swarm.service.id` label and returns a `container.InspectResponse`.
- `TestCreateServiceMultipleTimes`, `TestCreateServiceConflict`, and `TestCreateServiceMaxReplicas` cover basic service lifecycle invariants.
- `TestCreateServiceSecretFileMode` and `TestCreateServiceConfigFileMode` create Swarm secrets/configs, mount them into a service, and read service logs for Unix mode bits.
- `TestCreateServiceSysctls`, `TestCreateServiceCapabilities`, `TestCreateServiceMemorySwap`, and `TestCreateServiceMemorySwappiness` inspect service specs, task specs, and task containers for plumbed options.

## Control Flow
Each test calls `setupTest`, starts an isolated Swarm daemon with `swarm.NewSwarm`, creates API clients, creates services through integration helpers or direct client calls, waits for convergence with `poll.WaitOn`, then inspects service/task/container state. Resource tests iterate table cases and reuse the same daemon. Secret/config tests explicitly remove services, wait for task removal, and remove the created secret/config.

## State And Persistence
State is held in the test daemon's Swarm raft state, overlay networks, services, tasks, secrets, configs, and task containers. Daemons are stopped with `defer d.Stop(t)`, and the package cleanup path removes non-protected resources after each test. `TestCreateServiceMultipleTimes` deliberately checks that after service removal and task deallocation, an overlay network can be removed without lingering task references.

## Dependencies And Integration Points
Depends on Moby's client APIs, Swarm integration helpers, network helpers, `testutil.StartSpan`, `daemon` options, `gotest.tools` assertions, and `poll`. The tests integrate with SwarmKit scheduling, service controller updates, container creation, secret/config materialization, cgroup/resource host config translation, and daemon environment flags such as swap support.

## Risks And Edge Cases
Many tests are skipped on Windows; several assume Linux-specific file modes and Swarm behavior. Task convergence and network removal are asynchronous, so polling and retry loops are required. The memory swap container assertion is conditional on daemon swap-limit support, while memory swappiness is only asserted at service/task spec level because host support can silently clear container host config fields.

## Test Signals
Strong signals include one running task per service, expected service conflict errors, service and task specs matching requested sysctls/capabilities/resources, secret/config `ls -l` output containing requested modes, and task container `HostConfig` reflecting the service-level options where the daemon supports them.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/service/create_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/service/inspect_test.go -->
# sources/cloud-native/moby/integration/service/inspect_test.go

## Purpose
Validates that `ServiceInspect` returns a rich Swarm service object equivalent to the service spec submitted through the API, including annotations, container spec, DNS config, restart policy, update and rollback config, service mode, IDs, and timestamps.

## Important APIs, Types, And Functions
- `TestInspect` creates a two-replica service from `fullSwarmServiceSpec`, waits for tasks, inspects the service, and compares against an expected `swarmtypes.Service`.
- `cmpServiceOpts` builds `cmp` options that compare `CreatedAt` and `UpdatedAt` within a 20 second threshold and equate `netip` comparable values.
- `fullSwarmServiceSpec` constructs the canonical expected service specification used here and by list tests.

## Control Flow
The test skips remote daemons and Windows, starts a Swarm daemon, records `time.Now`, creates the service with `QueryRegistry: false`, waits for both tasks to run, inspects by ID, and performs a deep comparison with relaxed timestamp handling.

## State And Persistence
Persistent state is the Swarm service object and its tasks inside the temporary test daemon. No explicit service removal is needed because package cleanup and daemon shutdown own teardown. Time state is intentionally approximate because service creation timestamps are daemon-generated.

## Dependencies And Integration Points
Uses the API client `ServiceCreate` and `ServiceInspect`, Swarm polling helpers, `google/go-cmp`, and Moby Swarm API types. It touches serialization/deserialization of service specs and SwarmKit's storage metadata.

## Risks And Edge Cases
The expected version index is hard-coded to `11`, which can be brittle if SwarmKit object creation sequencing changes. The timestamp comparator tolerates clock and scheduling delay but only within 20 seconds. The fixture assumes `busybox:latest` is available through frozen images.

## Test Signals
Passing means the inspected service preserves the full submitted spec, includes the expected ID and metadata, and exposes timestamps close to creation time.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/service/inspect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/service/jobs_test.go -->
# sources/cloud-native/moby/integration/service/jobs_test.go

## Purpose
Tests Swarm job service modes: creating replicated and global jobs, running a replicated job to completion, and updating a completed replicated job to start a new job iteration.

## Important APIs, Types, And Functions
- `TestCreateJob` creates services with `ReplicatedJob` and `GlobalJob` modes and waits for one running task.
- `TestReplicatedJob` sets `MaxConcurrent` and `TotalCompletions`, uses command `true`, and waits for `swarm.JobComplete`.
- `TestUpdateReplicatedJob` increments `TaskTemplate.ForceUpdate`, updates the service, checks `JobIteration` increases, and waits for the second completion.

## Control Flow
All tests skip remote daemons and Windows, create an isolated Swarm, create job-mode services, then rely on polling to observe running tasks or completed job status. The update path inspects the service before and after `ServiceUpdate`.

## State And Persistence
Job state lives in Swarm service `Mode`, `JobStatus`, service versions, and task history. Completed job tasks remain part of Swarm history until daemon cleanup.

## Dependencies And Integration Points
Uses Swarm service APIs, `swarm.CreateService`, `swarm.JobComplete`, `client.ServiceUpdate`, and SwarmKit job orchestration. The tests integrate with scheduler completion accounting and job iteration versioning.

## Risks And Edge Cases
The replicated job deliberately keeps total completions low because CI startup overhead can make higher totals time out. Polling must distinguish a completed job from transient task creation. Behavior is Linux/local-daemon oriented.

## Test Signals
Successful signals are running tasks for job services, `JobComplete` success for command `true`, and a strictly increasing `JobStatus.JobIteration.Index` after a forced update.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/service/jobs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/service/list_test.go -->
# sources/cloud-native/moby/integration/service/list_test.go

## Purpose
Ensures `ServiceList` honors the `Status` option: default list responses omit service status, while `Status: true` includes desired and running task counts matched to each service.

## Important APIs, Types, And Functions
- `TestServiceListWithStatuses` creates three replicated services using `fullSwarmServiceSpec`.
- Inline polling uses `TaskList` filtered by service ID and counts tasks in `TaskStateRunning`.
- `ServiceListOptions{Status: true}` is the API feature under test.

## Control Flow
The test starts Swarm, creates three services with 1, 2, and 3 replicas, waits for each service's running tasks, lists services without status and checks nil `ServiceStatus`, then lists with status and checks desired/running counts equal each service's replica count.

## State And Persistence
Service and task state persists in the test Swarm until cleanup. No local files are written.

## Dependencies And Integration Points
Integrates Moby API service list handling with SwarmKit status aggregation. Reuses the inspect test's full spec helper and Moby client filters.

## Risks And Edge Cases
The test intentionally avoids unconverged service status assertions because reliably inducing and observing partial convergence is difficult. It assumes all created services are the only services visible in the isolated daemon.

## Test Signals
Passing means `ServiceStatus` is absent by default and present with correct `DesiredTasks` and `RunningTasks` when requested.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/service/list_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/service/main_test.go -->
# sources/cloud-native/moby/integration/service/main_test.go

## Purpose
Provides package-level setup and per-test cleanup for `integration/service` tests.

## Important APIs, Types, And Functions
- Global `testEnv *environment.Execution` and `baseContext context.Context` are shared by tests.
- `TestMain` configures tracing, creates the environment, ensures frozen Linux images, prints environment details, runs tests, and shuts tracing down.
- `setupTest` starts a span, protects baseline resources, and registers environment cleanup.

## Control Flow
`TestMain` runs before tests, builds a root OpenTelemetry span, initializes daemon environment metadata, loads required frozen images, then delegates to `m.Run`. Each test calls `setupTest`, which wraps the test context and schedules cleanup.

## State And Persistence
Holds package-wide environment state and protected resource snapshots. Cleanup removes test-created daemon resources after each test while preserving protected baseline objects.

## Dependencies And Integration Points
Depends on `internal/testutil`, `internal/testutil/environment`, OpenTelemetry, and the integration environment's frozen image setup. Every service integration test relies on this harness.

## Risks And Edge Cases
Failures during environment creation or frozen image setup panic before tests run. Cleanup behavior is shared and can mask or expose resource leaks across tests.

## Test Signals
Successful package startup prints environment details and allows tests to run under traced contexts with cleanup attached.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/service/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/service/network_linux_test.go -->
# sources/cloud-native/moby/integration/service/network_linux_test.go

## Purpose
Exercises Linux Swarm and overlay networking behavior around API compatibility, reconnect idempotency, IPv4 requirements, config-derived swarm-scoped networks, ingress iptables ordering, and firewalld reload recovery.

## Important APIs, Types, And Functions
- `TestDockerNetworkConnectAliasPreV144` starts a daemon with `DOCKER_MIN_API_VERSION=1.43` and validates alias preservation with an API v1.43 client.
- `TestDockerNetworkReConnect` checks duplicate `NetworkConnect` errors do not mutate container network settings.
- `TestSwarmNoDisableIPv4` expects a clear error when disabling IPv4 on a Swarm-scoped network.
- `TestSwarmScopedNetFromConfig` creates a config-only bridge network and a swarm-scoped network from it.
- `TestDockerIngressChainPosition` uses an isolated L3 segment, published ingress port, daemon restart, `wget`, and golden iptables output.
- `TestRestoreIngressRulesOnFirewalldReload` reloads firewalld and verifies ingress remains reachable.

## Control Flow
Tests start Swarm daemons, create overlay or bridge networks, create containers or services, and poll for runtime/network convergence. The ingress-chain test runs daemon and HTTP checks inside an isolated network namespace, checks `DOCKER-FORWARD` before and after restart, and uses golden output. The firewalld test waits for HTTP response before and after `networking.FirewalldReload`.

## State And Persistence
State spans overlay networks, container endpoint settings, Swarm services, iptables chains, firewalld rules, and daemon restart persistence. Network namespace state from `NewL3Segment` is destroyed with `defer`.

## Dependencies And Integration Points
Depends on Linux networking helpers, libnetwork scope constants, Swarm helpers, daemon options, API version negotiation, `iptables`, `wget` or `curl`, firewalld, and gotest golden files. It integrates daemon networking, libnetwork, Swarm ingress, and firewall backends.

## Risks And Edge Cases
Many tests skip rootless, remote daemon, nftables, or missing firewalld cases. Firewall tests are environment-sensitive and can be flaky if host networking differs. Duplicate endpoint comparison needs `cmpopts.EquateComparable` for `netip` values.

## Test Signals
Signals include expected aliases, stable container network settings after rejected reconnect, error text for IPv4-disabled swarm networks, running service tasks on config-derived networks, reachable ingress HTTP returning 404, preserved golden iptables chain ordering, and ingress recovery after firewalld reload.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/service/network_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/service/plugin_test.go -->
# sources/cloud-native/moby/integration/service/plugin_test.go

## Purpose
Validates Swarm plugin services across a multi-node cluster: plugin image distribution through a local registry, environment propagation, service update to a new plugin reference, removal cleanup, placement constraints, and default naming when plugin spec name is omitted.

## Important APIs, Types, And Functions
- `TestServicePlugin` builds/pushes two plugin references, starts two managers and one worker, creates plugin-runtime services, and polls plugin state on each node.
- `makePlugin` mutates a `swarmtypes.Service` to use `RuntimePlugin`, sets `PluginSpec` remote/name/env, and optional placement constraints.
- Daemon helper pollers `PluginIsRunning`, `PluginReferenceIs`, and `PluginIsNotPresent` provide node-level checks.

## Control Flow
The test first uses a regular daemon to create and push two plugin artifacts to a local registry. It then starts a three-node experimental Swarm, creates a plugin service, validates plugin installation/running on all nodes and env filtering, updates to the second reference, removes it, repeats with manager-only constraints, and repeats with no explicit plugin name.

## State And Persistence
State includes local registry content, plugin images, cluster services/tasks, node-local plugin installations, plugin settings/env, and service placement. Cleanup stops daemons and removes services, but registry artifacts exist only for the test registry lifetime.

## Dependencies And Integration Points
Requires local daemon control, amd64, non-Windows, non-remote execution, experimental daemon mode, plugin fixture creation, registry fixture, Swarm multi-node join, and plugin management API support.

## Risks And Edge Cases
Environment- and architecture-sensitive. Plugin installation/update/removal is asynchronous across nodes. Invalid env entries are expected to be ignored while valid `foo=bar` remains. Placement constraints must avoid installing on workers.

## Test Signals
Passing requires plugin running on expected nodes, reference updating to `repo2`, plugin removal on all nodes, manager-only constraints excluding the worker, and plugin spec env containing `foo=bar` without invalid `baz`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/service/plugin_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/service/swarm_test.go -->
# sources/cloud-native/moby/integration/service/swarm_test.go

## Purpose
Regression coverage for Swarm CA fingerprint validation during node join.

## Important APIs, Types, And Functions
- `TestSwarmCAHash` mutates the CA hash segment of a valid worker join token and attempts `SwarmJoin` from a second daemon.
- Uses `d1.JoinTokens(t).Worker`, `d2.SwarmListenAddr`, and `client.SwarmJoinOptions`.

## Control Flow
The test skips nftables firewall backends, starts a manager Swarm and a second standalone daemon, replaces token field 2 with a bogus hash, then verifies join fails with the expected fingerprint mismatch message.

## State And Persistence
Only temporary daemon and Swarm state are created. The second daemon never joins because validation fails.

## Dependencies And Integration Points
Integrates Swarm token parsing, CA fingerprint validation, daemon Swarm join API, and daemon helper methods.

## Risks And Edge Cases
The test assumes the token format remains hyphen-delimited with the CA hash at index 2. It is skipped for nftables backends because Swarm is unavailable there.

## Test Signals
The expected signal is an error containing `remote CA does not match fingerprint`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/service/swarm_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/service/update_test.go -->
# sources/cloud-native/moby/integration/service/update_test.go

## Purpose
Tests Swarm service update paths for labels, secrets, configs, network attachments, and PIDs limits, including spec persistence and runtime container host config propagation.

## Important APIs, Types, And Functions
- `TestServiceUpdateLabel` mutates `Spec.Labels` through add/remove/add cycles and waits for service version progression.
- `TestServiceUpdateSecrets` and `TestServiceUpdateConfigs` add and remove `SecretReference` or `ConfigReference` entries.
- `TestServiceUpdateNetwork` removes the service network attachment and expects overlay load-balancer endpoints to disappear.
- `TestServiceUpdatePidsLimit` creates and updates `Resources.Limits.Pids` and inspects the task container.
- Helpers `getServiceTaskContainer`, `getService`, `serviceIsUpdated`, and `serviceSpecIsUpdated` encapsulate inspect/poll behavior.

## Control Flow
Tests start a Swarm, create a service, inspect the latest service object, mutate the spec, submit `ServiceUpdate` with the current version, poll for completion or version index change, and re-inspect. The PIDs test carries service ID/state across ordered subtests to exercise create, unset, and update.

## State And Persistence
State includes service versions, update status, labels, secret/config references, network endpoints, and task containers. The network test directly observes `NetworkInspect` container endpoint counts before and after update.

## Dependencies And Integration Points
Depends on Swarm service APIs, network helpers, Moby API types, and poll. It bridges Swarm spec updates to engine task reconciliation and container host config.

## Risks And Edge Cases
All tests skip non-Linux. The PIDs table is order-dependent because later cases update the service created by the first case. Network endpoint counts are sensitive to Swarm load-balancer implementation details. `serviceIsUpdated` requires `UpdateStatus.State == completed`, which depends on Swarm controller status.

## Test Signals
Passing confirms service labels exactly match expected maps, secret/config lists are added then emptied, overlay endpoints are removed after network detachment, and container `HostConfig.Resources.PidsLimit` mirrors nonzero limits while zero unsets it.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/service/update_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/session/main_test.go -->
# sources/cloud-native/moby/integration/session/main_test.go

## Purpose
Provides package-level tracing, environment initialization, frozen image setup, and per-test cleanup for session integration tests.

## Important APIs, Types, And Functions
- `TestMain` configures tracing, initializes `environment.Execution`, ensures frozen Linux images, prints environment metadata, runs tests, and exits with the test code.
- `setupTest` wraps tests in spans, protects baseline resources, and registers `testEnv.Clean`.

## Control Flow
Startup mirrors other integration packages: create base context/span, create environment, ensure images, run tests, then shut tracing down.

## State And Persistence
Stores `testEnv` and `baseContext` package globals. The environment protection snapshot controls what cleanup preserves.

## Dependencies And Integration Points
Depends on `internal/testutil`, `environment`, and OpenTelemetry. Session tests use this to reach the configured daemon.

## Risks And Edge Cases
Environment setup failures panic before tests. Cleanup is broad, so session tests must protect resources they expect to survive.

## Test Signals
Package readiness is signaled by successful environment creation and frozen-image preparation before `m.Run`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/session/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/session/session_test.go -->
# sources/cloud-native/moby/integration/session/session_test.go

## Purpose
Validates the daemon `/session` HTTP endpoint's h2c upgrade behavior and bad-upgrade error responses.

## Important APIs, Types, And Functions
- `TestSessionCreate` posts to `/session` with `X-Docker-Expose-Session-Uuid` and `Upgrade: h2c`, expecting `101 Switching Protocols`.
- `TestSessionCreateWithBadUpgrade` posts with no upgrade and with `Upgrade: foo`, expecting `400 Bad Request` with specific messages.
- Uses `internal/testutil/request` raw HTTP helpers.

## Control Flow
Both tests skip Windows, call `setupTest`, derive the daemon host, issue POST requests, close or read response bodies, and assert status codes/headers/body fragments.

## State And Persistence
No durable daemon state is intended. A successful session upgrade creates a transient upgraded connection identified by the header-provided UUID.

## Dependencies And Integration Points
Integrates direct HTTP request handling, API router upgrade validation, session manager, and h2c negotiation. It bypasses the high-level client to verify protocol-level details.

## Risks And Edge Cases
The successful upgrade body must be closed to avoid leaks. Tests are disabled on Windows with FIXME notes. Error assertions depend on response message text.

## Test Signals
Expected signals are `101` plus `Upgrade: h2c` for valid requests, and `400` bodies containing `no upgrade` or `not supported` for invalid upgrades.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/session/session_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/system/api_test.go -->
# sources/cloud-native/moby/integration/system/api_test.go

## Purpose
Checks that the daemon returns a JSON API error response for an unmatched route when the client requests JSON.

## Important APIs, Types, And Functions
- `TestAPIErrorNotFoundJSON` performs `GET /notfound` with `request.JSON`, reads into `common.ErrorResponse`, and checks the error text.

## Control Flow
The test gets a setup context, sends a raw request, asserts HTTP 404, then decodes the response through `request.ReadJSONResponse`.

## State And Persistence
No daemon state changes are made.

## Dependencies And Integration Points
Touches the API router's 404 path, JSON error encoding, `common.ErrorResponse`, and request test helpers.

## Risks And Edge Cases
404 uses a different error path from normal handler errors, so this test is deliberately narrow. It depends on exact `page not found` error text.

## Test Signals
Passing means the not-found path emits status 404 and a JSON error object whose error string is `page not found`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/system/api_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/system/cgroupdriver_systemd_test.go -->
# sources/cloud-native/moby/integration/system/cgroupdriver_systemd_test.go

## Purpose
Regression test for setting container memory limits when a daemon runs with the native systemd cgroup driver.

## Important APIs, Types, And Functions
- `hasSystemd` checks `/run/systemd/system` to decide whether systemd is the host init system.
- `TestCgroupDriverSystemdMemoryLimit` starts a daemon with `--exec-opt native.cgroupdriver=systemd`, disables iptables, creates a container with 64 MiB memory limit, starts it, and inspects host config.

## Control Flow
The test skips Windows and non-systemd hosts, runs in parallel, starts an isolated daemon with busybox loaded, creates and starts a container, then inspects it.

## State And Persistence
Temporary daemon root, cgroup configuration, and container state are created. Container removal and daemon stop are deferred.

## Dependencies And Integration Points
Requires Linux with systemd, cgroup support, a runnable local daemon, test daemon helpers, and container integration helpers. It integrates daemon cgroup-driver configuration with container resource setup.

## Risks And Edge Cases
Host systemd detection is filesystem-based and may be false in containers. The test cannot run on Windows and may fail on hosts without suitable cgroup/systemd support.

## Test Signals
Passing confirms `ContainerInspect.HostConfig.Memory` equals `64 * 1024 * 1024` under the systemd cgroup driver.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/system/cgroupdriver_systemd_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/system/disk_usage_prune_test.go -->
# sources/cloud-native/moby/integration/system/disk_usage_prune_test.go

## Purpose
Regression coverage for concurrent `DiskUsage` calls while images are being removed from a containerd image-store daemon.

## Important APIs, Types, And Functions
- `TestDiskUsageConcurrentPrune` loads ten synthetic images with ten layers each, launches five `DiskUsage` goroutines, and concurrently removes images.
- Uses `specialimage.MultiLayerCustom`, `image.Load`, `client.DiskUsageOptions{Images: true}`, `sync.WaitGroup`, and an error channel.

## Control Flow
The test skips Windows, remote daemons, and non-snapshotter environments, starts a fresh daemon, loads unique multilayer images, schedules cleanup, then starts concurrent disk-usage readers after a removal goroutine closes a start channel. All goroutines complete before errors are asserted.

## State And Persistence
Creates many images and snapshots in an isolated daemon. Image deletion races with snapshot accounting. Cleanup force-removes images after the test.

## Dependencies And Integration Points
Integrates image build/load helpers, containerd image store snapshot metadata, daemon disk usage accounting, image removal, and Go concurrency primitives.

## Risks And Edge Cases
Race reproduction is probabilistic; more layers/images raise odds but increase runtime. The test only applies to the containerd image store. Ignored image-remove errors during the race are intentional because the regression target is `DiskUsage` returning errors.

## Test Signals
Passing means none of the concurrent `DiskUsage` calls returns an error while image removal is active.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/system/disk_usage_prune_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/system/disk_usage_test.go -->
# sources/cloud-native/moby/integration/system/disk_usage_test.go

## Purpose
Validates daemon disk-usage API accounting for images, containers, volumes, and build cache across an empty daemon, after loading busybox, and after running a container. It also verifies option filtering for every supported resource-type combination.

## Important APIs, Types, And Functions
- `TestDiskUsage` starts an isolated daemon, runs staged state transitions, calls `apiClient.DiskUsage`, and compares `client.DiskUsageResult` structures.
- `adjustedExpectedUsage` tolerates a one-block drift for rootless snapshotter environments.
- Comparisons ignore container `Status` and equate `netip` comparable values.

## Control Flow
The test skips Windows, runs in parallel, starts a daemon with iptables disabled, then executes three sequential steps: empty daemon, after `LoadBusybox`, and after `container.Run`. After each step it runs subtests for container-only, image-only, volume-only, build-cache-only, and mixed option combinations to ensure omitted types are zero.

## State And Persistence
State is accumulated in the test daemon: initially empty storage, a loaded busybox image, then a running container. `stepDU` carries the expected snapshot from one stage into filter assertions. Daemon cleanup removes storage after the test.

## Dependencies And Integration Points
Uses daemon helpers, image loading, container helpers, disk-usage client APIs, and Moby API result types. It integrates daemon storage accounting, image/container metadata, and API response filtering.

## Risks And Edge Cases
Disk usage can vary by snapshotter/rootless filesystem block behavior. The test assumes no build cache or volumes are created by the staged operations. It intentionally avoids parallel subtests for disk usage options due to an outstanding TODO.

## Test Signals
Signals include zeroed empty daemon usage, one loaded busybox image with positive size and no active containers, one active container linked to the image, `ImageManifestDescriptor` absent from container disk-usage summaries, and exact resource-type filtering.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/system/disk_usage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/system/event_test.go -->
# sources/cloud-native/moby/integration/system/event_test.go

## Purpose
Tests daemon events for exec lifecycle, nonblocking event API behavior, and avoiding duplicate volume create events when a volume is later mounted by a container.

## Important APIs, Types, And Functions
- `TestEventsExecDie` subscribes to `exec_die` events for a container and checks event fields after `ExecStart`.
- `TestEventsNonBlocking` performs raw `GET /events` and asserts it returns quickly.
- `TestEventsVolumeCreate` captures daemon time, creates a volume, queries filtered events with `Since`/`Until`, then creates a container with that volume and checks only one create event exists.

## Control Flow
Tests use setup context and the environment API client. Event tests subscribe or query, perform daemon actions, and select/poll with timeouts. `getEvents` drains event streams until EOF or timeout.

## State And Persistence
Creates containers, exec instances, volumes, and event log entries in the daemon. Context cancellation bounds event streams.

## Dependencies And Integration Points
Uses events API, exec API, volume API, container mount helpers, raw request helpers, daemon time helpers, and Moby event filter types.

## Risks And Edge Cases
Windows skips indicate event timing/behavior uncertainty there. Event tests are race-prone if event subscription starts too late or daemon time boundaries are too tight. The nonblocking test uses a three-second grace period.

## Test Signals
Passing signals include an `exec_die` container event with matching container ID, exec ID, and exit code `0`; immediate `/events` response with HTTP 200; and exactly one volume create event despite subsequent container attachment.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/system/event_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/system/info_linux_test.go -->
# sources/cloud-native/moby/integration/system/info_linux_test.go

## Purpose
Linux-only coverage for `/info` API compatibility fields around binary commit metadata and deprecated bridge nftables fields.

## Important APIs, Types, And Functions
- `TestInfoBinaryCommits` defines local `legacyCommit`/`legacyInfo` structs and compares current `/info` with `/v1.48/info`.
- `TestInfoLegacyFields` unmarshals `/v1.49/info` and `/v1.50/info` into a map and checks presence or absence of `BridgeNfIp6tables` and `BridgeNfIptables`.

## Control Flow
The tests issue raw JSON requests, read bodies, unmarshal into local structs/maps, and assert version-specific field values.

## State And Persistence
Read-only daemon metadata; no persistent state is changed.

## Dependencies And Integration Points
Touches API version negotiation, `/info` serialization, binary commit metadata for containerd/runc/init, and legacy field removal behavior.

## Risks And Edge Cases
The file is excluded on Windows. Assertions depend on binary commit IDs being known and not `N/A`. Legacy compatibility boundaries are version-specific and will need updating if API deprecation policy changes.

## Test Signals
Current API should expose commit IDs but empty `Expected` fields; API v1.48 should mirror `Expected` to `ID`; v1.49 should include bridge nftables booleans while v1.50 should omit them.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/system/info_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/system/info_test.go -->
# sources/cloud-native/moby/integration/system/info_test.go

## Purpose
Tests general `/info` API fields and daemon configuration reporting, including warning output for insecure TCP listeners, debug metrics, insecure registries, and registry mirrors.

## Important APIs, Types, And Functions
- `TestInfoAPI` checks core `Info` fields from the environment daemon.
- `TestInfoAPIWarnings` starts a daemon listening on `0.0.0.0:23756` and checks root-access warning strings.
- `TestInfoDebug` starts `--debug` and checks debug flag, descriptor/goroutine counts, and root dir.
- `TestInfoInsecureRegistries` starts with CIDR and host insecure registry options and validates `RegistryConfig`.
- `TestInfoRegistryMirrors` starts with two mirrors and validates normalized/sorted mirror URLs.

## Control Flow
Some tests use the shared daemon; daemon-configuration tests skip remote/Windows, run in parallel, start isolated daemons with specific flags, call `Info`, and compare returned fields.

## State And Persistence
Isolated daemons create temporary roots and sockets. Info calls are read-only, but daemon startup flags define reported persistent config for the daemon lifetime.

## Dependencies And Integration Points
Integrates daemon startup flags, registry config parsing, info API serialization, warning generation, debug-mode metrics, and test daemon helpers.

## Risks And Edge Cases
Remote and Windows environments skip local daemon startup cases. Warning tests compare string fragments from formatted `Info`, which can be fragile. Insecure registry CIDR ordering is handled by membership checks while mirrors are sorted before compare.

## Test Signals
Passing means core info fields are populated and internally consistent; insecure TCP warning includes the bound host; debug mode reports true and nonzero runtime counters; insecure registry and mirror config are normalized as expected.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/system/info_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/system/login_test.go -->
# sources/cloud-native/moby/integration/system/login_test.go

## Purpose
Verifies registry login with known bad credentials fails with an unauthorized error that includes the default registry endpoint.

## Important APIs, Types, And Functions
- `TestLoginFailsWithBadCredentials` checks `requirement.HasHubConnectivity`, calls `RegistryLogin`, and asserts error substrings.

## Control Flow
The test skips if Docker Hub connectivity is unavailable, then uses the environment API client to attempt login with `no-user`/`no-password`.

## State And Persistence
No successful auth state is created. A failed remote registry request may create transient network activity only.

## Dependencies And Integration Points
Depends on internet connectivity to Docker Hub, registry package default host, and daemon registry login API.

## Risks And Edge Cases
High external dependency risk: network, Hub availability, auth message changes, or rate limiting can affect the test. It is guarded by a connectivity requirement but still depends on remote error text.

## Test Signals
Expected error contains `unauthorized: incorrect username or password` and the default registry `/v2/` URL.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/system/login_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/system/main_test.go -->
# sources/cloud-native/moby/integration/system/main_test.go

## Purpose
Package-level test harness for system integration tests.

## Important APIs, Types, And Functions
- `TestMain` configures tracing, creates `environment.Execution`, ensures frozen Linux images, prints environment data, runs tests, and exits.
- `setupTest` creates a per-test span, protects baseline resources, and schedules cleanup.

## Control Flow
The flow is identical to service/session/volume package harnesses: initialize once, run all tests, then shut down tracing.

## State And Persistence
Holds global environment and base context. Per-test cleanup removes resources created by system tests while preserving protected initial state.

## Dependencies And Integration Points
Depends on `internal/testutil`, `environment`, OpenTelemetry, and frozen image provisioning.

## Risks And Edge Cases
Any failure before `m.Run` panics and prevents tests from executing. Cleanup is broad and can interact with tests that start their own daemons or rely on the shared daemon state.

## Test Signals
Successful startup yields a usable `testEnv` and traced base context for all system tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/system/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/system/ping_test.go -->
# sources/cloud-native/moby/integration/system/ping_test.go

## Purpose
Validates `/_ping` HTTP and client behavior: cache headers, GET/HEAD bodies and API version headers, Swarm status header state transitions, and builder version reporting.

## Important APIs, Types, And Functions
- `TestPingCacheHeaders`, `TestPingGet`, and `TestPingHead` use raw request helpers.
- `TestPingSwarmHeader` starts a daemon, checks ping before Swarm init, after init, and after leave.
- `TestPingBuilderHeader` starts daemons with default config and with BuildKit disabled via a generated `daemon.json`.

## Control Flow
Raw ping tests use the shared environment. Swarm and builder tests skip remote/Windows as needed, start isolated daemons, perform daemon state transitions, call `apiClient.Ping`, and compare returned fields.

## State And Persistence
Swarm test mutates daemon Swarm state from inactive to active and back. Builder test writes a `daemon.json` under the test daemon root and starts/stops daemons with different config.

## Dependencies And Integration Points
Touches API router ping endpoint, client ping response parsing, Swarm local node status, BuildKit feature config, daemon startup config-file handling, and raw HTTP request helpers.

## Risks And Edge Cases
Builder default differs on Windows, though the local-daemon builder test skips Windows. The BuildKit-disabled case writes config directly with `os.WriteFile` and assumes daemon root exists before start.

## Test Signals
Signals include no-cache headers, GET body `OK`, empty HEAD body, nonempty `Api-Version`, correct Swarm inactive/active/control flags, and builder version switching from BuildKit default to v1 when disabled.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/system/ping_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/system/version_test.go -->
# sources/cloud-native/moby/integration/system/version_test.go

## Purpose
Tests server version API component metadata and rejection of clients older than the daemon's minimum supported API version.

## Important APIs, Types, And Functions
- `TestVersion` calls `ServerVersion`, finds the `Engine` component, and compares detail fields with top-level version and environment daemon info.
- `TestAPIClientVersionOldNotSupported` decrements the daemon minimum API minor version and expects a precise too-old-client error.

## Control Flow
Both tests use the shared daemon. The first scans `version.Components` for `Engine`; the second constructs a client with an intentionally unsupported API version and calls `ServerVersion`.

## State And Persistence
Read-only metadata checks; no daemon state changes.

## Dependencies And Integration Points
Integrates client API version negotiation, server version serialization, component metadata, and request client construction.

## Risks And Edge Cases
The old-client test assumes semantic `major.minor` parsing and minor version decrement remain valid. Error text is exact and can be brittle.

## Test Signals
Passing means Engine component details include API version, minimum API version, OS, and experimental flag matching daemon info, and unsupported clients receive the expected upgrade error.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/system/version_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/volume/main_test.go -->
# sources/cloud-native/moby/integration/volume/main_test.go

## Purpose
Package-level harness for volume integration tests.

## Important APIs, Types, And Functions
- `TestMain` configures tracing, initializes environment, ensures frozen images, prints environment details, runs tests, and exits.
- `setupTest` starts a per-test span, protects baseline daemon resources, and registers cleanup.

## Control Flow
Initialization is performed once before all tests. Each test calls `setupTest` to get a traced context and cleanup behavior.

## State And Persistence
Stores package globals for the environment and base context. Cleanup removes unprotected volumes, containers, images, networks, and plugins after each test.

## Dependencies And Integration Points
Uses `internal/testutil`, `environment`, OpenTelemetry, and frozen-image setup. Volume tests rely heavily on busybox availability.

## Risks And Edge Cases
Harness failure prevents all package tests. Cleanup is critical because volume tests create named and anonymous volumes that would otherwise interfere with later cases.

## Test Signals
Successful package initialization supplies a working API client and cleanup-managed environment for volume tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/volume/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/volume/mount_test.go -->
# sources/cloud-native/moby/integration/volume/mount_test.go

## Purpose
Exercises volume and image mount subpath behavior, including safe path validation, symlink escape prevention, file mounts, copy-up behavior, image mount removal semantics, multiple image mounts, and daemon restart persistence for image subpaths.

## Important APIs, Types, And Functions
- `TestRunMountVolumeSubdir` creates a populated test volume and table-tests valid/invalid `mount.VolumeOptions.Subpath` cases.
- `TestRunMountImage` builds a test image and table-tests `mount.ImageOptions.Subpath`, image removal while mounted, and force removal plus restart.
- `setupTestVolume` creates files, directories, and symlinks inside a named volume.
- `setupTestImage` builds a scratch image with files and symlinks using `fakecontext`.
- `TestRunMountImageMultipleTimes` mounts `hello-world:frozen` at two destinations in one container.
- `TestRunMountImageSubpathDaemonRestart` restarts a snapshotter daemon and verifies an image subpath mount survives.

## Control Flow
Tests build or create backing data, create containers with `HostConfig.Mounts`, branch on expected create/start errors, start containers, collect output, inspect exit code and mounts, and perform cleanup. Image removal cases inspect image IDs and restart containers. The daemon-restart test starts a separate daemon, runs a long-lived container with restart policy, restarts the daemon, inspects mounts/running state, and execs into the container.

## State And Persistence
State includes named volumes with filesystem content, built images, image mount references, container mount metadata, image deletion state, and daemon restart persistence. Symlinks inside volumes/images are used to test safe-path traversal.

## Dependencies And Integration Points
Depends on API versions 1.45 for volume subpaths and 1.48 for image mounts, `safepath` error types, container helpers, fake build contexts, daemon helpers, snapshotter mode for restart test, and frozen images.

## Risks And Edge Cases
Several cases skip Windows because file bind/image mounts or copy behavior differ. Safe-path tests are sensitive to symlink and path-cleaning behavior. The daemon-restart image-subpath test skips rootless and non-snapshotter modes due to known issue coverage.

## Test Signals
Passing signals include expected stdout from mounted subpaths/files, expected create/start errors for path escape or missing paths, image-in-use errors without force, successful restart after force image removal, two inspectable image mounts, and image subpath availability after daemon restart.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/volume/mount_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/volume/volume_test.go -->
# sources/cloud-native/moby/integration/volume/volume_test.go

## Purpose
Tests core volume APIs: create/list metadata, remove conflict and force behavior, removal while Swarm is enabled, inspect timestamp stability, invalid JSON error handling, anonymous-volume prune semantics, and pruning anonymous volumes created from image `VOLUME` declarations.

## Important APIs, Types, And Functions
- `TestVolumesCreateAndList` checks local driver metadata and mountpoint path.
- `TestVolumesRemove` and `TestVolumesRemoveSwarmEnabled` verify in-use conflict, successful removal after container removal, not-found behavior, and force behavior.
- `TestVolumesInspect` confirms `CreatedAt` does not change after touching the `_data` directory.
- `TestVolumesInvalidJSON` sends malformed requests to `/volumes/create`.
- `getPrefixAndSlashFromDaemonPlatform` abstracts Unix/Windows volume target syntax.
- `TestVolumePruneAnonymous` checks new API behavior pruning anonymous volumes by default and all volumes with `All: true`, plus old API v1.41 behavior.
- `TestVolumePruneAnonFromImage` builds an image with `VOLUME`, creates a container, removes it, and verifies prune removes the generated anonymous volume.

## Control Flow
Tests use setup context and API client, create containers/volumes/images, inspect daemon responses, and remove resources. The Swarm-enabled removal case starts a separate daemon and initializes Swarm to verify cluster-volume-related behavior. Invalid JSON tests run endpoint subtests in parallel and inspect HTTP status/body.

## State And Persistence
Creates named volumes, anonymous volumes, containers, daemon-side volume directories, images, and Swarm state. `TestVolumesInspect` mutates `_data` directory atime/mtime to ensure logical creation time is stable.

## Dependencies And Integration Points
Depends on Moby volume API, container helper volume creation, build helper/fakecontext for `VOLUME`, client API version selection, error definitions, and raw request helpers. Integrates with volume store metadata and prune policy compatibility.

## Risks And Edge Cases
Windows case-insensitive names and path prefixes are handled explicitly. Old API behavior is intentionally different from current API, so compatibility assertions must track API-version gates. Timestamp parsing assumes RFC3339 and minute-level tolerance.

## Test Signals
Signals include exact volume metadata, conflict errors while volumes are in use, nil error for forced missing volume removal, stable `CreatedAt`, 400 responses for invalid content type/JSON/trailing content, no 5xx for empty body, expected prune deletion lists, and pruning image-declared anonymous volumes after container removal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/volume/volume_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/iterutil/iterutil.go -->
# sources/cloud-native/moby/internal/iterutil/iterutil.go

## Purpose
Provides small generic helpers for Go 1.23-style iterators: unordered multiset comparison, pointer dereferencing, sequence concatenation, and mapping for one- and two-value iterators.

## Important APIs, Types, And Functions
- `SameValues[T comparable]` counts yielded values from two `iter.Seq[T]` sequences and compares count maps.
- `Deref[T any, P *T]` converts `iter.Seq[P]` to `iter.Seq[T]` by dereferencing pointers.
- `Chain[T]` concatenates multiple `iter.Seq[T]` values.
- `Chain2[K,V]` concatenates multiple `iter.Seq2[K,V]` values.
- `Map[T,U]` and `Map2` apply mapping functions lazily.

## Control Flow
All helpers return lazy iterator functions except `SameValues`, which eagerly consumes both inputs into maps. Lazy helpers stop immediately when downstream `yield` returns false.

## State And Persistence
No persistent state. `SameValues` allocates temporary maps; mapping/chaining helpers keep only closure-captured inputs and functions.

## Dependencies And Integration Points
Uses standard `iter` and `maps` packages. Intended as internal glue for code using Go iterators.

## Risks And Edge Cases
`Deref` panics on nil pointers. `SameValues` requires comparable values and consumes entire sequences, which can be expensive or nonterminating for infinite iterators. Map helpers propagate mapper panics.

## Test Signals
Unit tests validate duplicate-aware comparison, dereferencing, chaining, map collection, and two-value map iteration transformations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/iterutil/iterutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/iterutil/iterutil_test.go -->
# sources/cloud-native/moby/internal/iterutil/iterutil_test.go

## Purpose
Unit tests for iterator utility helpers.

## Important APIs, Types, And Functions
- `TestSameValues` checks order-insensitive but duplicate-sensitive equality.
- `TestDeref` collects dereferenced integer pointers.
- `TestChain` and `TestChain2` verify concatenation for sequences and map iterators.
- `TestMap` and `TestMap2` verify transformation to strings and uppercase map keys.

## Control Flow
Tests build slices/maps, adapt them with `slices.Values` or `maps.All`, call iterutil helpers, collect with `slices.Collect` or `maps.Collect`, and compare expected values.

## State And Persistence
Only in-memory test data.

## Dependencies And Integration Points
Uses standard `maps`, `slices`, `strconv`, `strings`, and gotest assertions. Serves as regression coverage for `internal/iterutil`.

## Risks And Edge Cases
The tests do not cover early-yield cancellation or nil pointers for `Deref`. Map iteration order is irrelevant because maps are compared structurally.

## Test Signals
Passing confirms helper behavior for basic and duplicate cases, chained nested sequences, and one-/two-value mapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/iterutil/iterutil_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/namesgenerator/names-generator.go -->
# sources/cloud-native/moby/internal/namesgenerator/names-generator.go

## Purpose
Generates Docker-style random container names from a frozen adjective list and a frozen list of notable surnames/names, formatted as `adjective_name` with an optional numeric suffix on retry.

## Important APIs, Types, And Functions
- Package-level arrays `left` and `right` hold adjectives and names with comments explaining many name origins.
- `GetRandomName(retry int)` chooses one random element from each list using `math/rand`, rejects the special `boring_wozniak` combination, and appends a random digit if `retry > 0`.

## Control Flow
The generator loops via `goto begin` only for the disallowed combination, then conditionally appends a digit and returns the string.

## State And Persistence
No package-local mutable state is maintained, but `math/rand` global state controls randomness. The lists are static and documented as officially frozen.

## Dependencies And Integration Points
Uses `math/rand` and `strconv`. The function is used by Docker/Moby name generation where a human-readable random name is needed, commonly for containers when no explicit name is provided.

## Risks And Edge Cases
Randomness is not cryptographic and is intentionally marked with `nolint:gosec`. Retry suffix is only a single digit, so it reduces but does not eliminate collisions. The function is not deterministic unless the global random source is seeded predictably by callers/runtime.

## Test Signals
Tests validate underscore format, absence of digits when `retry == 0`, presence of a digit when `retry > 0`, and benchmark allocation/performance.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/namesgenerator/names-generator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/namesgenerator/names-generator_test.go -->
# sources/cloud-native/moby/internal/namesgenerator/names-generator_test.go

## Purpose
Tests and benchmarks random name formatting behavior.

## Important APIs, Types, And Functions
- `TestNameFormat` calls `GetRandomName(0)` and checks underscore plus no digits.
- `TestNameRetries` calls `GetRandomName(1)` and checks underscore plus a digit.
- `BenchmarkGetRandomName` repeatedly calls `GetRandomName(5)` and reports allocations.

## Control Flow
The tests perform a single random generation each and assert string properties with `strings.Contains`/`ContainsAny`. The benchmark stores the last result to keep the call observable.

## State And Persistence
No persistent state beyond global random source advancement during tests.

## Dependencies And Integration Points
Uses standard `strings` and `testing`. Covers `internal/namesgenerator` public function.

## Risks And Edge Cases
Because generation is random, the tests verify format properties rather than exact values. They do not explicitly test the disallowed `boring_wozniak` combination or collision rates.

## Test Signals
Passing confirms generated names contain an underscore, retry-zero names do not include digits, retry-positive names include a digit, and the benchmark can run without allocations surprises being hidden.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/namesgenerator/names-generator_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/sliceutil/sliceutil.go -->
# sources/cloud-native/moby/internal/sliceutil/sliceutil.go

## Purpose
Provides generic slice helpers for dereferencing pointer slices, deduplicating comparable slices while preserving first occurrence order, mapping slices, and turning a mapper function into a reusable slice mapper.

## Important APIs, Types, And Functions
- `Deref[T]` converts `[]*T` to `[]T`, returns nil for nil input, and skips nil pointers.
- `Dedup[T comparable]` tracks seen values in a map and appends first occurrences.
- `Map[S ~[]In, In, Out]` returns nil for nil input and otherwise maps every element into a same-length `[]Out`.
- `Mapper[In,Out]` returns a closure that applies `Map`.

## Control Flow
All functions are simple linear scans. `Map` preallocates exact output length; `Deref` and `Dedup` preallocate capacity and append conditionally.

## State And Persistence
No persistent state. `Dedup` allocates a temporary key map; other helpers allocate output slices as needed.

## Dependencies And Integration Points
No external dependencies. Intended for internal callers needing concise generic slice transformations.

## Risks And Edge Cases
`Deref` silently drops nil pointers, which may be surprising if callers need positional preservation. `Dedup` uses a map and therefore requires comparable element types. `Map` distinguishes nil input from empty input.

## Test Signals
Companion tests cover mapping values, nil and empty slice behavior, type conversion, and `Mapper` closures.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/sliceutil/sliceutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/sliceutil/sliceutil_test.go -->
# sources/cloud-native/moby/internal/sliceutil/sliceutil_test.go

## Purpose
Unit tests for slice mapping helpers.

## Important APIs, Types, And Functions
- `TestMap` doubles integers and verifies nil input returns nil while empty input returns non-nil empty output.
- `TestMap_TypeConvert` maps integers to strings.
- `TestMapper` builds a reusable `netip.MustParseAddr` mapper and tests normal, nil, and empty inputs.

## Control Flow
Tests call `sliceutil.Map` or a `Mapper` closure, compare lengths and values, and use ordinary `testing` failures.

## State And Persistence
Only local slices and parsed addresses are used.

## Dependencies And Integration Points
Imports the package as `sliceutil_test`, so it exercises only exported API. Uses `net/netip` and `strconv`.

## Risks And Edge Cases
Tests do not cover `Deref` or `Dedup`, so those helpers rely on indirect or absent coverage here. Mapper panic behavior for invalid addresses is not covered.

## Test Signals
Passing confirms `Map` and `Mapper` preserve length, support output type conversion, and preserve the nil-versus-empty distinction.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/sliceutil/sliceutil_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/test/suite/interfaces.go -->
# sources/cloud-native/moby/internal/test/suite/interfaces.go

## Purpose
Defines lifecycle interfaces for Moby's lightweight internal test suite runner.

## Important APIs, Types, And Functions
- `SetupAllSuite` requires `SetUpSuite(context.Context, *testing.T)`.
- `SetupTestSuite` requires `SetUpTest(context.Context, *testing.T)`.
- `TearDownAllSuite` requires `TearDownSuite(context.Context, *testing.T)`.
- `TearDownTestSuite` requires `TearDownTest(context.Context, *testing.T)`.
- `TimeoutTestSuite` declares `OnTimeout()`.

## Control Flow
This file only defines interfaces; `suite.go` performs discovery and invocation.

## State And Persistence
No state.

## Dependencies And Integration Points
Uses `context` and `testing`. Suite implementations can opt into lifecycle hooks by implementing these exact signatures.

## Risks And Edge Cases
Signature mismatches are detected in `suite.go` and panic with explicit messages. `TimeoutTestSuite` is defined but not invoked by the runner in the neighboring implementation.

## Test Signals
Behavior is covered indirectly by suite runner usage; no direct tests are in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/test/suite/interfaces.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/test/suite/suite.go -->
# sources/cloud-native/moby/internal/test/suite/suite.go

## Purpose
Implements a small reflection-based test suite runner as a lighter alternative to testify's suite package.

## Important APIs, Types, And Functions
- `TimeoutFlag` aliases the standard `-timeout` flag but is marked `DO NOT USE`.
- `Run(ctx, t, suite)` discovers suite methods and runs `Test*` methods as subtests.
- `getSetupAllSuite`, `getSetupTestSuite`, `getTearDownTestSuite`, and `getTeardownAllSuite` validate lifecycle hook signatures.
- `failOnPanic` converts panics into test failures with stack traces.
- `methodFilter` accepts methods named `Test*` with receiver plus `*testing.T`.

## Control Flow
`Run` starts a span, defers panic recovery and suite teardown, reflects over exported methods, filters test methods, and invokes each with `t.Run`. For each subtest it sets test context, lazily runs suite setup once before the first test, runs per-test setup, calls the reflected test method, and defers per-test teardown.

## State And Persistence
State is in-memory: `suiteSetupDone`, suite context, and testing context storage through `testutil.SetContext`/`CleanupContext`. No files or daemon state are modified directly.

## Dependencies And Integration Points
Uses `reflect`, `runtime/debug`, `strings`, `testing`, and `internal/testutil` tracing/context helpers. Intended for internal test suites that want lifecycle hooks without pulling in testify dependencies.

## Risks And Edge Cases
Reflection only sees exported methods. Suite setup runs lazily on the first matching test, so a suite with no tests will not run setup/teardown. Panic recovery calls `FailNow`, which aborts the current test goroutine. `TimeoutTestSuite` is not wired into timeout behavior.

## Test Signals
Expected behavior is subtests for each matching suite method, setup/teardown hook invocation with exact signatures, panic-to-failure conversion, and context availability during each test.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/test/suite/suite.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/archive.go -->
# sources/cloud-native/moby/internal/testutil/archive.go

## Purpose
Computes the canonical digest of an uncompressed tar stream from a potentially compressed tar reader.

## Important APIs, Types, And Functions
- `UncompressedTarDigest(compressedTar io.Reader) (digest.Digest, error)` wraps `compression.DecompressStream`, streams decompressed bytes into `digest.Canonical.Digester`, and returns the digest.

## Control Flow
The function opens a decompressor, defers close, copies all decompressed data into the canonical hash, propagates decompression or copy errors, then returns the computed digest.

## State And Persistence
No persistent state. It streams data and allocates only decompressor/hash state.

## Dependencies And Integration Points
Uses `github.com/moby/go-archive/compression` and `github.com/opencontainers/go-digest`. Useful in tests comparing image/archive contents independent of compression.

## Risks And Edge Cases
All input is consumed. Invalid compression or read errors return errors. Digest is over raw uncompressed tar bytes, so tar metadata ordering and headers still affect the result.

## Test Signals
No direct tests in this item; callers can verify known compressed tar inputs produce expected canonical digests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/archive.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/daemon/container.go -->
# sources/cloud-native/moby/internal/testutil/daemon/container.go

## Purpose
Adds a daemon helper for listing active/running containers in the daemon's isolated environment.

## Important APIs, Types, And Functions
- `(*Daemon).ActiveContainers(ctx, t)` creates a daemon-scoped client, calls `ContainerList` without `All`, and returns container IDs from the response.

## Control Flow
The helper creates a client, defers close, lists containers, asserts no error, then maps summaries to IDs.

## State And Persistence
Read-only helper. It observes currently running containers but does not modify daemon state.

## Dependencies And Integration Points
Uses the `Daemon` client factory, Moby client container API, and gotest assertions. Used by integration tests that need to assert runtime container counts.

## Risks And Edge Cases
Only running containers are returned because `All` is not set. The function ignores the passed context in `ContainerList` and uses `context.Background`, so caller cancellation is not honored.

## Test Signals
Expected signal is a slice of running container IDs with no API error.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/daemon/container.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/daemon/daemon.go -->
# sources/cloud-native/moby/internal/testutil/daemon/daemon.go

## Purpose
Core test harness for creating, starting, stopping, restarting, configuring, inspecting, and cleaning isolated `dockerd` processes used by integration tests.

## Important APIs, Types, And Functions
- `Daemon` stores root paths, socket paths, command/log handles, storage/userns/rootless options, Swarm options, extra environment, and cached info.
- Constructors `NewDaemon` and `New` create isolated folders, data roots, exec roots, socket roots, rootless runtime dirs, and apply `Option` values.
- Lifecycle methods `Start`, `StartWithError`, `StartWithLogFile`, `StartWithBusybox`, `Stop`, `StopWithError`, `Kill`, `Restart`, and `RestartWithError` manage the daemon process.
- Client/log helpers include `NewClient`, `NewClientT`, `ReadLogFile`, `TailLogs`, `ScanLogs`, and poll matchers.
- Configuration/introspection helpers include `BinaryPath`, `RootDir`, `Sock`, `Info`, `FirewallBackendDriver`, `FirewallReloadedAt`, `ReloadConfig`, `SetEnvVar`, `LoadImage`, `LoadBusybox`, `TamperWithContainerConfig`, and cleanup helpers.
- Path helpers `sanitizedTestName` and `sanitizePathComponent` make test names safe for filesystem/artifact tooling.

## Control Flow
Construction chooses a destination, creates directories, configures rootless ownership if needed, and stores options. `StartWithLogFile` assembles dockerd arguments, defaulting to debug mode and optionally applying storage/firewall/userns/experimental/init/rootless settings, starts the process, launches a wait goroutine, then polls `/_ping` until ready or timeout. Stop sends interrupt, waits, retries interrupts, and kills on timeout. Restart composes stop/start. Cleanup removes mounts, raft data, storage directories, and network namespaces.

## State And Persistence
The harness creates persistent-on-disk test state under the configured destination: daemon folder, `root`, `docker.log`, pid file, exec root, socket under `/tmp/docker-integration`, rootless XDG runtime dir, optional resolv.conf override, and daemon storage. `d.Root` may be updated after startup by querying `/info`, especially for user namespace remap.

## Dependencies And Integration Points
Integrates with OS process management, Unix/TLS sockets, Moby client, test request helpers, containerd namespace flags, dockerd command-line flags, OpenTelemetry environment, storage drivers, rootless `sudo`, and platform-specific signal/mount helpers.

## Risks And Edge Cases
Startup readiness depends on polling within 60 seconds. Rootless mode requires user/ownership setup and forbids non-default dockerd binaries. `SetEnvVar` has an index check that only replaces entries at index greater than zero, so an existing first entry is appended instead of replaced. Cleanup intentionally preserves logs for artifacts and may leave root folders. Direct config tampering assumes on-disk daemon layout.

## Test Signals
Strong signals are successful `/_ping`, successful `/info` root query, clean stop or kill fallback, readable logs, expected sanitized paths, image load into isolated daemon, and cleanup removing storage subdirectories without failing tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/daemon/daemon.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/daemon/daemon_freebsd.go -->
# sources/cloud-native/moby/internal/testutil/daemon/daemon_freebsd.go

## Purpose
Provides FreeBSD-specific stubs for daemon cleanup and cgroup namespace behavior.

## Important APIs, Types, And Functions
- `cleanupNetworkNamespace` is a no-op on FreeBSD.
- `(*Daemon).CgroupNamespace` fails the test because cgroup namespaces are unsupported on FreeBSD.

## Control Flow
No runtime cleanup is performed. Calling `CgroupNamespace` asserts false and returns an empty string after the assertion path.

## State And Persistence
No state changes.

## Dependencies And Integration Points
Uses build tag `freebsd`, `testing`, and gotest assertions. Completes the platform-specific API expected by `daemon.go`.

## Risks And Edge Cases
Any test that calls `CgroupNamespace` on FreeBSD fails immediately. Network namespace cleanup is intentionally absent because the concept does not apply.

## Test Signals
Compile-time platform selection is the main signal; unsupported cgroup namespace tests fail clearly if invoked.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/daemon/daemon_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/daemon/daemon_linux.go -->
# sources/cloud-native/moby/internal/testutil/daemon/daemon_linux.go

## Purpose
Linux-specific daemon helpers for cleaning network namespace mounts and reading the daemon's cgroup namespace.

## Important APIs, Types, And Functions
- `cleanupNetworkNamespace` walks `<execRoot>/netns`, lazily unmounts entries, logs non-benign errors, and removes paths.
- `(*Daemon).CgroupNamespace` reads `/proc/<pid>/ns/cgroup` and trims the link target.

## Control Flow
Cleanup traverses the daemon-specific netns directory with `filepath.WalkDir`, attempts `unix.Unmount(MNT_DETACH)`, ignores `EINVAL` and `ENOENT`, and removes each path. Namespace reading uses the daemon process PID.

## State And Persistence
Cleanup mutates the daemon exec root by unmounting/removing network namespace files. `CgroupNamespace` is read-only.

## Dependencies And Integration Points
Requires Linux `/proc`, `golang.org/x/sys/unix`, and daemon process state. Complements `Daemon.Cleanup`.

## Risks And Edge Cases
Walk errors are ignored by the callback signature, so missing directories are benign. Unmount failures are logged but do not fail tests. `CgroupNamespace` requires a running daemon with a valid PID.

## Test Signals
Expected behavior is no leaked netns mounts after cleanup and a nonempty cgroup namespace link for running daemons.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/daemon/daemon_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/daemon/daemon_test.go -->
# sources/cloud-native/moby/internal/testutil/daemon/daemon_test.go

## Purpose
Regression tests for sanitizing test names into safe filesystem paths.

## Important APIs, Types, And Functions
- `TestSanitizeTestName` runs subtests whose names contain quotes, spaces, dots, dashes, underscores, slashes, and path traversal-like text, then compares `sanitizedTestName(t)` with expected paths.

## Control Flow
Each table row runs as a subtest, calls `sanitizedTestName`, converts expected slash separators through `filepath.FromSlash`, and reports mismatch with `t.Errorf`.

## State And Persistence
No persistent state; it only uses subtest names.

## Dependencies And Integration Points
Tests `sanitizePathComponent`/`sanitizedTestName`, which are used by daemon constructor paths and artifact tooling safety.

## Risks And Edge Cases
The table captures important path edge cases such as `../foo`, bare quotes, and leading dashes. It does not test non-ASCII names.

## Test Signals
Passing means daemon test directories will not contain shell-hostile quotes or path traversal components derived from test names.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/daemon/daemon_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/daemon/daemon_unix.go -->
# sources/cloud-native/moby/internal/testutil/daemon/daemon_unix.go

## Purpose
Unix-specific daemon helpers for root cleanup, diagnostic/reload signals, and process group setup.

## Important APIs, Types, And Functions
- `cleanupMount` unmounts the daemon root using `moby/sys/mount.Unmount`.
- `SignalDaemonDump` sends `SIGQUIT` to trigger daemon stack dump.
- `signalDaemonReload` sends `SIGHUP` for config reload.
- `setsid` ensures rootless sudo-launched daemon commands run in a new session.

## Control Flow
Functions directly call OS signal or mount APIs and either ignore/log errors depending on caller. `setsid` initializes `SysProcAttr` if needed before setting `Setsid`.

## State And Persistence
`cleanupMount` can alter mount state for daemon root. Signal helpers mutate daemon process state by causing dump/reload behavior.

## Dependencies And Integration Points
Build tag `!windows`; uses Unix signals, `moby/sys/mount`, and `golang.org/x/sys/unix`. Called by `Daemon.Cleanup`, `DumpStackAndQuit`, and `ReloadConfig`.

## Risks And Edge Cases
Unmount failure is logged but not fatal. Signals require a live process and proper permissions. `setsid` matters for rootless signal propagation through sudo.

## Test Signals
Expected signals are successful stack dumps on SIGQUIT, reload events after SIGHUP, and best-effort daemon root unmount during cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/daemon/daemon_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/daemon/daemon_windows.go -->
# sources/cloud-native/moby/internal/testutil/daemon/daemon_windows.go

## Purpose
Windows-specific daemon helper implementations for diagnostic signaling and unsupported Unix cleanup/namespace operations.

## Important APIs, Types, And Functions
- `SignalDaemonDump` opens and pulses a global Windows event named for the daemon PID.
- `signalDaemonReload` returns an unsupported error.
- `cleanupMount` and `cleanupNetworkNamespace` are no-ops.
- `(*Daemon).CgroupNamespace` asserts false and returns an unsupported message.
- `setsid` is a no-op.

## Control Flow
Diagnostic dump attempts event lookup and returns silently if unavailable. Reload and cgroup namespace calls fail explicitly. Cleanup stubs do nothing.

## State And Persistence
Pulsing the global event may cause the daemon to emit a dump. No filesystem or namespace cleanup occurs here.

## Dependencies And Integration Points
Uses Windows build defaults, `golang.org/x/sys/windows`, and gotest assertions. Satisfies platform-specific function references from `daemon.go`.

## Risks And Edge Cases
Missing dump event is silently ignored. Reload is unsupported on Windows. Tests expecting Unix namespace behavior must skip Windows.

## Test Signals
Compile success on Windows and graceful unsupported behavior are the primary signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/daemon/daemon_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/daemon/doc.go -->
# sources/cloud-native/moby/internal/testutil/daemon/doc.go

## Purpose
Declares the `daemon` package for internal test utilities.

## Important APIs, Types, And Functions
No APIs are defined in this file beyond the package declaration.

## Control Flow
No executable control flow.

## State And Persistence
No state.

## Dependencies And Integration Points
Serves as package documentation scaffold for the broader daemon test helper package.

## Risks And Edge Cases
No direct risks.

## Test Signals
Compilation confirms package membership.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/daemon/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/daemon/node.go -->
# sources/cloud-native/moby/internal/testutil/daemon/node.go

## Purpose
Provides Swarm node helper methods on `Daemon` for inspect, remove, update, and list operations in integration tests.

## Important APIs, Types, And Functions
- `NodeConstructor` mutates a `swarm.Node`.
- `GetNode` inspects a node and optionally tolerates errors through supplied predicates.
- `RemoveNode` removes a node with optional force.
- `UpdateNode` retries node updates on `update out of sequence` errors.
- `ListNodes` returns all Swarm nodes.

## Control Flow
Each helper creates a daemon client and defers close. `UpdateNode` loops up to 11 attempts: inspect latest node, apply constructors, submit update with current version, retry short sleeps for sequence errors, otherwise assert success.

## State And Persistence
Mutates Swarm node objects for updates/removals. Node state persists in Swarm raft state until changed or cleaned.

## Dependencies And Integration Points
Uses Moby Swarm node APIs, daemon client helpers, gotest assertions, and string matching for sequence errors.

## Risks And Edge Cases
Retry detection depends on error text. `GetNode` returns nil if an allowed error predicate matches, so callers must handle nil. Update constructors mutate the inspected object in place.

## Test Signals
Expected signals are successful node inspect/list, node removal without API error, and robust update despite transient version conflicts.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/daemon/node.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/daemon/ops.go -->
# sources/cloud-native/moby/internal/testutil/daemon/ops.go

## Purpose
Defines functional options for configuring test daemon instances.

## Important APIs, Types, And Functions
- `Option func(*Daemon)` is the configuration primitive.
- Options configure containerd socket, user namespace remap, cgroup namespace mode, test logger, experimental/init flags, dockerd binary, Swarm ports/listen address/iptables/default address pools/data path port, environment-derived settings, storage driver, rootless user, OOM score, extra environment variables, and resolv.conf content.

## Control Flow
Each option returns a closure that mutates fields on a `Daemon` before startup. `WithUserNsRemap` contains special storage-driver compatibility logic for `DOCKER_GRAPHDRIVER=overlayfs`. `WithRootlessUser` panics if the named user cannot be found.

## State And Persistence
Options only mutate the in-memory `Daemon` configuration. Some options later cause persistent effects during daemon construction/startup, such as writing a resolv.conf override or changing rootless ownership.

## Dependencies And Integration Points
Integrates test environment metadata, OS user lookup, netip prefixes, and daemon startup argument assembly in `daemon.go`.

## Risks And Edge Cases
`WithRootlessUser` panics instead of returning an error. `WithEnvVars` appends variables and can create duplicates unless later replaced by `SetEnvVar`. User namespace storage-driver workaround is tied to a documented issue.

## Test Signals
Configuration is validated indirectly by tests that start daemons with these options and observe expected behavior, such as Swarm ports, experimental mode, init mode, or custom resolv.conf.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/daemon/ops.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/daemon/plugin.go -->
# sources/cloud-native/moby/internal/testutil/daemon/plugin.go

## Purpose
Provides polling predicates for plugin state on a test daemon.

## Important APIs, Types, And Functions
- `PluginIsRunning`, `PluginIsNotRunning`, `PluginIsNotPresent`, and `PluginReferenceIs` return `poll.Check` functions.
- `withPluginInspect` wraps plugin inspection and delegates to a predicate.
- `withClient` creates/closes a daemon client for each poll.

## Control Flow
Poll predicates inspect a plugin by name through a new client. They translate not-found and state/reference mismatches into `poll.Continue`, success into `poll.Success`, and unexpected errors into `poll.Error`.

## State And Persistence
Read-only observation of daemon plugin state. Polling creates short-lived clients repeatedly.

## Dependencies And Integration Points
Uses plugin API types, client plugin inspect, containerd errdefs, daemon client helpers, and gotest poll.

## Risks And Edge Cases
Name/reference ambiguity matters because plugin service tests may use explicit names or remote references. Creating a new client on every poll is simple but can add overhead.

## Test Signals
Signals are successful plugin running state, disabled/not-running state, not-found state, or matching plugin remote reference.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/daemon/plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/daemon/service.go -->
# sources/cloud-native/moby/internal/testutil/daemon/service.go

## Purpose
Adds Swarm service/task helper methods on `Daemon` for integration tests.

## Important APIs, Types, And Functions
- `ServiceConstructor func(*swarm.Service)` mutates a service object before create/update.
- `createServiceWithOptions` builds a default replicated busybox service and calls `ServiceCreate`.
- `CreateService`, `GetService`, `GetServiceTasks`, `GetServiceTasksWithFilters`, `UpdateService`, `RemoveService`, `ListServices`, and `GetTask` wrap common service APIs.

## Control Flow
Create builds a `swarm.Service` object with defaults, applies constructors, and submits the spec. Update applies constructors to an existing service and submits with current version. Task helpers filter by service or task ID and assert expected results.

## State And Persistence
Mutates Swarm service/task state in the daemon's cluster. Defaults create one-replica busybox services with command `top`.

## Dependencies And Integration Points
Uses Moby Swarm service/task APIs, daemon clients, client filters, gotest assertions, and service versioning.

## Risks And Edge Cases
Default service values may be inappropriate for specialized tests unless constructors override them. `GetTask` asserts exactly one task for an ID filter. `GetServiceTasksWithFilters` mutates the provided additional filter by adding the service filter.

## Test Signals
Expected signals are successful service IDs, inspectable services, correctly filtered task lists, successful updates/removals, and exact task lookup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/daemon/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/daemon/swarm.go -->
# sources/cloud-native/moby/internal/testutil/daemon/swarm.go

## Purpose
Provides Swarm cluster lifecycle and management helpers for integration-test daemons.

## Important APIs, Types, And Functions
- Constants define default test Swarm port/listen address and start args with or without iptables.
- `StartNode`, `StartNodeWithBusybox`, `RestartNode`, `StartAndSwarmInit`, and `StartAndSwarmJoin` compose daemon startup with Swarm initialization/join.
- `SwarmListenAddr`, `NodeID`, `SwarmInitWithError`, `SwarmInit`, `SwarmJoin`, `SwarmLeave`, `SwarmInfo`, `SwarmUnlock`, `GetSwarm`, `UpdateSwarm`, `RotateTokens`, `JoinTokens`, and `startArgs` wrap Swarm APIs.
- `SpecConstructor` mutates `swarm.Spec` for update helpers.

## Control Flow
Startup helpers start daemons with Swarm-friendly arguments, load busybox where needed, initialize or join clusters using default listen addresses/ports and configured pools. API helpers create clients, fill missing request fields, submit Swarm operations, assert or return errors, and refresh cached daemon info after init/join.

## State And Persistence
Creates and mutates Swarm raft state, node membership, join tokens, Swarm specs, cached node info, and daemon runtime state. Start args disable iptables unless `WithSwarmIptables(true)` is set.

## Dependencies And Integration Points
Integrates daemon lifecycle helpers with Moby Swarm APIs, client options, Swarm request/response types, and busybox image loading.

## Risks And Edge Cases
Default listen address is `0.0.0.0`, while advertised address is only set when customized. Cached `NodeID` is valid only after successful init/join. Swarm tests requiring iptables must opt in. Join token selection depends on manager flag.

## Test Signals
Signals include successful daemon startup as Swarm node, initialized/joined clusters, inspectable Swarm info, token rotation, swarm spec updates, and node IDs available from cached info.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/daemon/swarm.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/doc.go -->
# sources/cloud-native/moby/internal/testutil/doc.go

## Purpose
Declares the `testutil` package and documents it as common testing helpers, such as running dockerd.

## Important APIs, Types, And Functions
No functions or types are declared in this file.

## Control Flow
No executable control flow.

## State And Persistence
No state.

## Dependencies And Integration Points
Package documentation anchor for `internal/testutil`.

## Risks And Edge Cases
No direct risks.

## Test Signals
Compilation confirms package membership.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/environment/clean.go -->
# sources/cloud-native/moby/internal/testutil/environment/clean.go

## Purpose
Implements environment cleanup for integration tests by removing all unprotected daemon resources after each test while preserving baseline protected objects.

## Important APIs, Types, And Functions
- `(*Execution).Clean` coordinates cleanup for containers, images, volumes, networks, Linux plugins, and default bridge restoration.
- `unpauseAllContainers` and `getPausedContainers` ensure paused containers can be removed.
- `deleteAllContainers`, `deleteAllImages`, `removeImage`, `deleteAllVolumes`, `deleteAllNetworks`, and `deleteAllPlugins` perform resource-specific cleanup.

## Control Flow
`Clean` starts an OpenTelemetry span, obtains the environment API client, unpauses containers when supported, removes unprotected containers/images/volumes/networks, then on Linux removes unprotected plugins and restores default bridge state. Resource deletion helpers list current objects, skip protected IDs/names and default networks, and force removal where appropriate.

## State And Persistence
Mutates the shared test daemon by deleting resources created during tests. Protected maps in `Execution` decide what persists. Linux cleanup also restores default bridge settings.

## Dependencies And Integration Points
Uses Moby client interfaces for container/image/volume/network/plugin APIs, containerd errdefs, OpenTelemetry, and environment protection state. Called by package `setupTest` cleanup functions across integration packages.

## Risks And Edge Cases
Broad cleanup can hide resource leaks but is required for isolation. It ignores not-found images and container removal already in progress. Windows preserves predefined NAT network and skips plugin/default-bridge cleanup. Docker EE may return not-implemented for cluster-wide plugin management, which is ignored.

## Test Signals
Expected signals are no unprotected containers/images/volumes/networks/plugins remaining after cleanup, paused containers unpaused before removal, protected resources preserved, and bridge state restored on Linux.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/environment/clean.go -->
