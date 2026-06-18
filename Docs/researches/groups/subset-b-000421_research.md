# subset-b-000421 research

Grouped research report for Mayastor legacy gRPC tests, Python pytest/BDD helpers, Docker Compose fixtures, Kubernetes PVC/fio manifests, and related test configuration. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/grpc/test_nexus.js -->
# sources/control-plane/mayastor/test/grpc/test_nexus.js

## Purpose
Legacy Mocha/Chai coverage for the Mayastor nexus gRPC API. It validates nexus creation, listing, child add/remove, publish/unpublish, NVMf datapath behavior, ANA state changes, controller ID handling, and destructive/error cases across `bdev`, `aio`, `nvmf`, and conditionally `uring` children.

## Important APIs, Types, And Functions
Key helpers are `controlPlaneTest`, `doUring`, promise wrappers for `publish`, `unpublish`, `createNexus`, `createNexusV2`, `destroyNexus`, and `createNexusWithAllTypes`. It drives `client.createNexus`, `listNexus`, `addChildNexus`, `removeChildNexus`, `publishNexus`, `unpublishNexus`, `setNvmeAnaState`, and `getNvmeAnaState`, plus JSON-RPC calls such as `nexus_share` and `nvmf_subsystem_remove_ns`.

## Control Flow
The suite starts a separate NVMf target Mayastor and a primary Mayastor instance, creates malloc/aio/uring backing devices, then runs ordered tests that build a nexus, mutate children, publish over NVMf, inspect NVMe identify data, and finally exercise cleanup and invalid-argument paths. NBD tests exist but are skipped.

## State And Persistence
State lives in temporary files under `/tmp`, in two Mayastor processes, in exported NVMf namespaces, and in the single global gRPC client. Cleanup stops all Mayastor processes, restores NBD permissions, and removes temporary files.

## Dependencies And Integration Points
Depends on `test_common`, `grpc_enums`, Node `grpc`, SPDK JSON-RPC, the `initiator` helper, `nvme` CLI, root permissions, hugepages, and loop/device access. It integrates directly with Mayastor's legacy protobuf service and NVMf subsystem implementation.

## Risks
The source contains legacy fragility: skipped NBD coverage, duplicated lines in promise/NBD blocks, asynchronous `doUring` detection that can return before `exec` completes, and heavy reliance on timing, root commands, and local networking. Error-code assertions encode current implementation quirks such as oversized nexus creation returning INTERNAL.

## Test Signals
Passing tests signal that nexus child URI validation, NVMf publication, ANA reporting, controller ID assignment, namespace loss faulting, and idempotent create/destroy behavior work through the legacy gRPC surface.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/grpc/test_nexus.js -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/grpc/test_rebuild.js -->
# sources/control-plane/mayastor/test/grpc/test_rebuild.js

## Purpose
Mocha/Chai tests for rebuild task behavior on a legacy Mayastor nexus. The suite verifies running, stopping, pausing, resuming rebuilds and child online/offline operations using a one-child nexus plus a second aio child added as rebuild target.

## Important APIs, Types, And Functions
The file defines `createGrpcClient`, `checkState`, `checkNumRebuilds`, `checkRebuildState`, retry helpers, and `checkRebuildStats`. It drives `AddChildNexus`, `StartRebuild`, `StopRebuild`, `PauseRebuild`, `ResumeRebuild`, `ChildOperation`, `GetRebuildState`, `GetRebuildStats`, and `ListNexus`.

## Control Flow
Setup creates two 100 MiB aio files, starts Mayastor, creates a nexus with the source child, then each nested `describe` block adds the target child, performs the rebuild action under test, and asserts nexus, child, rebuild-count, and stats state. Teardown removes the target child and eventually destroys the nexus and files.

## State And Persistence
State is transient Mayastor in-memory nexus/rebuild state plus two `/tmp` backing files. Rebuild progress and counters are queried over gRPC and not persisted by the test itself.

## Dependencies And Integration Points
Uses `grpc-promise` over `mayastor.proto`, `sleep-promise` for polling, `test_common` for process startup and NBD permission management, and aio bdev URIs. It covers the legacy gRPC rebuild API that v1 compatibility tests also exercise.

## Risks
The teardown block includes a suspicious stray brace/comma in the source, and the tests are timing-sensitive because rebuild state transitions are polled with short retry windows. Some assertions compare numeric counts to string literals, which depends on proto loader conversion behavior.

## Test Signals
Successful runs indicate that rebuild state transitions, task counters, child degradation, and stats fields remain observable and compatible through the legacy API.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/grpc/test_rebuild.js -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/grpc/test_replica.js -->
# sources/control-plane/mayastor/test/grpc/test_replica.js

## Purpose
Legacy gRPC tests for pool and replica lifecycle behavior. It covers pool creation/list/destroy, replica create/list/share/unshare/stats/destroy, NVMf exported replica datapath reads/writes, data reset after recreation, and optional uring-backed pools.

## Important APIs, Types, And Functions
Important helpers are `createTestDisk`, `destroyTestDisk`, and `ensureNoTestPool`. The suite drives `createPool`, `listPools`, `destroyPool`, `createReplica`, `shareReplica`, `listReplicas`, `statReplicas`, and `destroyReplica`.

## Control Flow
The suite starts Mayastor when no external endpoint is supplied, creates or uses disk devices, creates an aio pool, validates invalid inputs, exercises replica share-state transitions, creates multiple replicas, destroys the pool, then runs optional `uring` tests and an NVMf datapath section using the `initiator` helper to write/read blocks.

## State And Persistence
State includes a loop-backed `/tmp/mayastor_test_disk`, pool metadata, replica bdevs, exported NVMf URI, and temporary `/tmp/test_block` data. The tests clean up the test pool, loop device, block file, and NBD permissions.

## Dependencies And Integration Points
Depends on Node `grpc`, `async`, `chai`, local root access, `losetup`, `truncate`, `initiator`, Mayastor's legacy gRPC service, and `test_common`. It can point at an externally running Mayastor through `MAYASTOR_ENDPOINT` and `MAYASTOR_DISKS`.

## Risks
The suite is environment-sensitive and has legacy duplicated object keys/lines in the source. It assumes specific capacity accounting, share enum strings, 4 MiB clusters, and root device permissions.

## Test Signals
Passing tests signal compatibility of pool/replica CRUD, share idempotency, NVMf URI formatting, basic replica IO, and pool cleanup through the legacy gRPC interface.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/grpc/test_replica.js -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/common/command.py -->
# sources/control-plane/mayastor/test/python/common/command.py

## Purpose
Shared command execution helpers for Python tests. It wraps local synchronous commands, local async shell commands, and remote async SSH commands with consistent return objects and error messages.

## Important APIs, Types, And Functions
Exports `CommandReturn`, `run_cmd`, `run_cmd_async`, and `run_cmd_async_at`. Async helpers capture stdout/stderr and raise `ChildProcessError` with command context on nonzero exit.

## Control Flow
`run_cmd` delegates to `subprocess.run`. `run_cmd_async` creates an asyncio shell process and waits for completion. `run_cmd_async_at` opens an `asyncssh` connection, runs the command, and converts the result.

## State And Persistence
No persistent state is stored. Remote state changes are whatever the invoked commands perform.

## Dependencies And Integration Points
Used by fio/NVMe tests, Mayastor fixtures, and remote initiator utilities. Depends on `asyncio`, `subprocess`, and `asyncssh`.

## Risks
Commands are shell strings, so callers must handle quoting. Remote SSH identity/configuration is assumed. The helper raises generic `ChildProcessError`, so tests rely on message text for diagnosis rather than typed failures.

## Test Signals
Failures surface as rich command logs in pytest, while successful calls return decoded stdout/stderr for downstream assertions.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/common/command.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/common/constants.py -->
# sources/control-plane/mayastor/test/python/common/constants.py

## Purpose
Centralizes the Mayastor/OpenEBS NVMe NQN prefix used by tests.

## Important APIs, Types, And Functions
Defines `nvme_nqn_prefix = "nqn.2019-05.io.openebs"`.

## Control Flow
There is no control flow.

## State And Persistence
No state beyond the module constant.

## Dependencies And Integration Points
Imported by publish BDD tests and any code constructing expected NVMf subsystem names.

## Risks
If production NQN naming changes, tests using this constant can fail broadly or assert stale names.

## Test Signals
Consistent URI/NQN assertions across suites indicate naming compatibility.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/common/constants.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/common/csi_hdl.py -->
# sources/control-plane/mayastor/test/python/common/csi_hdl.py

## Purpose
Minimal Python gRPC handle for CSI service tests. It creates stubs for CSI identity and node services over an insecure channel.

## Important APIs, Types, And Functions
Defines `CsiHandle.__init__`, `__del__`, and `close`. The active stubs are `IdentityStub` and `NodeStub`; the controller stub line is present but commented.

## Control Flow
Construction opens a gRPC channel to the supplied CSI socket and installs service stubs. `close` delegates to `__del__`.

## State And Persistence
State is the open gRPC channel and stub objects. No persistent data is written.

## Dependencies And Integration Points
Depends on generated `csi_pb2` and `csi_pb2_grpc` modules and `grpc`. It is a fixture-level utility for CSI node/identity tests outside this subset.

## Risks
The destructor only deletes the Python channel reference and does not explicitly close all gRPC resources. Controller service coverage is disabled unless a caller adds it.

## Test Signals
Successful stub calls through this handle validate CSI socket reachability and generated protobuf compatibility.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/common/csi_hdl.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/common/fio.py -->
# sources/control-plane/mayastor/test/python/common/fio.py

## Purpose
Builds fio command strings for kernel-device IO tests.

## Important APIs, Types, And Functions
Defines class `Fio` with constructor parameters for job name, rw mode, device(s), optional size, runtime, and extra options; `build()` returns a `nix-sudo fio` command using `linuxaio`, direct IO, 4 KiB blocks, iodepth 64, group reporting, and `norandommap`.

## Control Flow
`build` normalizes a single device to a list, joins multiple devices with `:`, conditionally adds `--size`, and formats the command.

## State And Persistence
The object stores command configuration plus unused `output` and `success` dictionaries. fio itself writes to the target devices only when the built command is executed by tests.

## Dependencies And Integration Points
Used throughout nexus, multipath, fault, and Kubernetes-style tests to generate fio workloads. Depends on `shutil.which("fio")` but the built command uses `$PATH` via `nix-sudo fio`.

## Risks
The command is returned as a shell string, so tests that split it can break if option strings contain spaces. Privileged execution and local fio availability are required.

## Test Signals
fio exit code zero and uninterrupted runtime are used as datapath health signals for connected NVMe devices and mounted filesystems.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/common/fio.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/common/fio_spdk.py -->
# sources/control-plane/mayastor/test/python/common/fio_spdk.py

## Purpose
Builds SPDK fio command strings for direct userspace NVMe/TCP workloads against Mayastor NVMf URIs.

## Important APIs, Types, And Functions
Class `FioSpdk` parses one or more NVMf URIs into SPDK filename descriptors and `build()` returns a command using `LD_PRELOAD=<spdk_nvme>`, `$FIO --ioengine=spdk`, 4 KiB direct IO, iodepth 64, and per-URI `--filename`.

## Control Flow
The constructor normalizes `uris`, parses host/port/subnqn fields, escapes colon characters in NQNs, and stores formatted filenames. `build` resolves `FIO_SPDK` or falls back to `SPDK_ROOT_DIR` or a relative `spdk-rs` build path.

## State And Persistence
Only stores fio command metadata. Persistent effects are produced by fio after test execution.

## Dependencies And Integration Points
Used by nexus and CLI controller tests to generate SPDK fio traffic without kernel NVMe devices. Integrates with SPDK build artifacts, environment variables, and Mayastor NVMf exports.

## Risks
Environment fallback paths are repository-layout sensitive. The command uses `sudo`, `$FIO`, and shell quoting, so test hosts must provide compatible tooling.

## Test Signals
Successful SPDK fio runs validate userspace initiator connectivity, controller stats accounting, and degraded/faulted nexus IO behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/common/fio_spdk.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/common/hdl.py -->
# sources/control-plane/mayastor/test/python/common/hdl.py

## Purpose
Provides the central Python `MayastorHandle` wrapper around legacy Mayastor gRPC stubs. It gives tests a concise API for bdev, pool, replica, nexus, NVMe controller stats, and Mayastor info operations.

## Important APIs, Types, And Functions
Important methods include `install_stub`, `_readiness_check`, `reconnect`, `bdev_create/share/unshare/destroy/list`, `pool_create/destroy/list`, `replica_create/create_v2/share/destroy/list/list_v2`, `nexus_create/create_v2/publish/unpublish/destroy/shutdown/list/list_v2/add_replica/remove_replica`, `pools_as_uris`, `stat_nvme_controllers`, and `mayastor_info`.

## Control Flow
Construction opens `grpc.insecure_channel(<ip>:10124)`, installs `BdevRpcStub` and `MayastorStub`, and performs a readiness check by listing bdevs and pools with a one-retry workaround for an inactive-channel error. `install_stub` wraps all stub functions with a default timeout.

## State And Persistence
The handle stores the target IP, gRPC timeout, channel, and stubs. All persistent Mayastor state is remote in io-engine containers.

## Dependencies And Integration Points
Depends on generated legacy `mayastor_pb2`/`mayastor_pb2_grpc`, `grpc`, `pytest_testconfig`, and docker-compose fixture plugins. It is the main integration layer used by nearly all Python tests in this subset.

## Risks
The wrapper mixes old and v2 APIs and has minimal type validation, intentionally allowing invalid URIs through to Mayastor. Channel cleanup is by deletion rather than explicit close, and timeout wrapping only applies to stubs installed through `install_stub`.

## Test Signals
If this handle can create/list/destroy resources, it proves container networking, protobuf generation, gRPC server readiness, and basic Mayastor control plane operations are aligned.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/common/hdl.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/common/mayastor.py -->
# sources/control-plane/mayastor/test/python/common/mayastor.py

## Purpose
Reusable pytest fixtures for Docker Compose based Mayastor integration tests.

## Important APIs, Types, And Functions
Exports `check_size`, function-scoped fixtures `containers`, `mayastors`, `create_temp_files`, and module-scoped fixtures `container_mod`, `mayastor_mod`.

## Control Flow
Container fixtures enumerate `docker_project.compose.ps()` and map names to container objects. Mayastor fixtures turn container IPs on `mayastor_net` into `MayastorHandle` instances. `create_temp_files` removes and recreates `/tmp/<container>.img` files.

## State And Persistence
State is fixture-scoped dictionaries of Docker containers and gRPC handles plus temporary host image files. The fixtures do not commit any state; test cases create and destroy remote Mayastor resources.

## Dependencies And Integration Points
Depends on `pytest`, pytest-docker-compose, `MayastorHandle`, and `run_cmd`. It binds compose service names such as `ms0`-`ms3` to test code.

## Risks
Fixture correctness depends on compose network names and static service naming. `check_size` subtracts current from previous pool usage, so callers must pass snapshots in the expected order.

## Test Signals
Most Python test failures begin here when containers are not reachable, gRPC readiness fails, or temporary backing files cannot be prepared.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/common/mayastor.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/common/msclient.py -->
# sources/control-plane/mayastor/test/python/common/msclient.py

## Purpose
Wrapper around the `io-engine-client` CLI for tests that inspect Mayastor controller state through command-line output.

## Important APIs, Types, And Functions
Defines `MayastorClient.__call__`, `with_url`, `with_json_output`, `with_default_output`, `with_verbose`, and `get_msclient`. Calls include `-o <output>`, optional `-q`, `-v`, and backend URL arguments.

## Control Flow
`get_msclient` locates the binary under `mayastor_target_dir()`. Invoking the client constructs an argv list, executes it via `subprocess.check_output(shell=False)`, decodes UTF-8 output, and parses JSON when requested.

## State And Persistence
The client stores mutable configuration such as URL and output mode. The CLI may mutate Mayastor state depending on commands, but this wrapper itself persists nothing.

## Dependencies And Integration Points
Depends on `SRCDIR`/`IO_ENGINE_DIR` through `mayastor_target_dir`, `subprocess`, and JSON output conventions. Used by CLI controller tests to inspect NVMe controller list/stats.

## Risks
Missing build artifacts cause immediate `FileNotFoundError`. Mutating builder methods return `self`, so reuse across tests can leak output mode or URL settings if not scoped carefully.

## Test Signals
JSON CLI output matching gRPC-created controllers validates the CLI, controller reporting, and target URL routing.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/common/msclient.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/common/nvme.py -->
# sources/control-plane/mayastor/test/python/common/nvme.py

## Purpose
Shared NVMe CLI helpers for kernel and remote initiator tests. It connects, discovers, disconnects, identifies, and inspects NVMe/TCP devices and controllers.

## Important APIs, Types, And Functions
Exports `nvme_hostids`, remote helpers `nvme_remote_connect_all`, `nvme_remote_connect`, `nvme_remote_disconnect`, `nvme_remote_discover`, local helpers `nvme_connect`, `nvme_id_ctrl`, `nvme_find_ctrl`, `nvme_resv_report`, `nvme_discover`, `nvme_disconnect`, `nvme_disconnect_controller`, `nvme_disconnect_all`, `nvme_list_subsystems`, `identify_namespace`, and `nvme_delete_controller`.

## Control Flow
URI helpers parse NVMf URLs into host, port, and NQN, run `nix-sudo nvme` commands, parse JSON outputs, assert a single matching subsystem/controller where required, and return device paths or metadata. Forced controller deletion writes to `/sys/class/nvme/<ctrl>/delete_controller`.

## State And Persistence
State is in kernel NVMe subsystems/controllers and optional host ID/NQN environment variables. The module does not cache state.

## Dependencies And Integration Points
Depends on `nvme-cli`, `nix-sudo`, `json`, `/sys`, async SSH via `run_cmd_async_at`, and Mayastor NVMf URI conventions. Used by ANA, nexus, multipath, fault, and Kubernetes-adjacent tests.

## Risks
Helpers assume exactly one matching connection in several paths and can disrupt host NVMe state through `disconnect-all` or forced controller deletion. The remote discover helper has a likely bug from awaiting `.stdout` on the coroutine result expression incorrectly.

## Test Signals
Successful discovery/connect/list/reservation-report calls are strong datapath and multipath signals for Mayastor NVMf exports.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/common/nvme.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/common/util.py -->
# sources/control-plane/mayastor/test/python/common/util.py

## Purpose
Small utility for resolving the Mayastor build output directory used by CLI/protobuf tests.

## Important APIs, Types, And Functions
Exports `mayastor_target_dir()`, which requires `SRCDIR` and returns `${SRCDIR}/${IO_ENGINE_DIR}`.

## Control Flow
The function checks the environment and raises an exception if `SRCDIR` is missing.

## State And Persistence
No persistent state.

## Dependencies And Integration Points
Used by `msclient.py` to locate `io-engine-client` and indirectly by CLI tests. Depends on `SRCDIR` and `IO_ENGINE_DIR` environment conventions.

## Risks
The docstring has a typo, and the function assumes the target directory naming scheme without validating `IO_ENGINE_DIR`.

## Test Signals
Correct path resolution allows setup and CLI tests to find generated binaries.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/common/util.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/common/volume.py -->
# sources/control-plane/mayastor/test/python/common/volume.py

## Purpose
Convenience abstraction for creating a replicated Mayastor volume from pool URIs and a target nexus node.

## Important APIs, Types, And Functions
Class `Volume` stores `uuid`, `nexus`, `pools`, and `size`. Internal helpers `__parse_uri` and `__create_replicas` parse `pool://host/pool` URIs and create replicas. `create()` creates replicas, creates a nexus, publishes it, and returns its device URI.

## Control Flow
`create()` validates an `nvmt://host` nexus target, creates a replica on each configured pool via a fresh `MayastorHandle`, then creates and publishes a nexus on the target.

## State And Persistence
State is remote Mayastor pools, replicas, nexus, and NVMf publication. The object has no cleanup method, so callers own teardown.

## Dependencies And Integration Points
Depends on `MayastorHandle` and Python URL parsing. Used by nexus tests to model volume creation and ENOSPC behavior.

## Risks
Lack of cleanup and fresh handle creation per pool can leave resources behind on failure. It assumes `pool` and `nvmt` URI schemes and does not support v2 naming fields.

## Test Signals
Successful `Volume.create()` proves pool URI discovery, replica creation, nexus creation, and publish flow work end to end.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/common/volume.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/cross-grpc-version/nexus/docker-compose.yml -->
# sources/control-plane/mayastor/test/python/cross-grpc-version/nexus/docker-compose.yml

## Purpose
Docker Compose environment for cross-version nexus tests.

## Important APIs, Types, And Functions
Defines two services, `ms0` and `ms1`, running `${SRCDIR}/${IO_ENGINE_DIR}/io-engine` with static IPs `10.1.0.2` and `10.1.0.3`, ANA and reservation support enabled, and shared source/Nix/hugepages/tmp mounts.

## Control Flow
pytest-docker-compose starts both containers on `mayastor_net`; fixtures map them to legacy and v1 gRPC handles.

## State And Persistence
State is container-local Mayastor runtime plus host-mounted `/tmp` and hugepages. No named volumes are declared.

## Dependencies And Integration Points
Requires Docker, rust image, mounted build tree, `/nix`, hugepages, and seccomp/capability relaxations. Used by cross-version nexus BDD tests.

## Risks
Static IPs and shared network names can conflict with other compose runs. Host `/tmp` sharing means stale test files can affect runs.

## Test Signals
Successful container startup enables v0-created nexus resources to be operated through v1 gRPC.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/cross-grpc-version/nexus/docker-compose.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/cross-grpc-version/nexus/test_bdd_nexus.py -->
# sources/control-plane/mayastor/test/python/cross-grpc-version/nexus/test_bdd_nexus.py

## Purpose
BDD compatibility tests proving that v1 nexus gRPC calls can operate on nexuses created through the legacy API.

## Important APIs, Types, And Functions
Scenario functions cover duplicate create, destroy, list/filter, child remove/add, publish/unpublish, republish protocol checks, and crypto-key publish. Fixtures build base malloc bdevs, shared remote bdev URIs, local aio/uring/malloc child URIs, v0 and v1 nexus creators, and `find_nexus`.

## Control Flow
Fixtures create local and remote bdevs, share a remote bdev over NVMf, assemble children, create v0 nexuses via `mayastor_pb2`, then perform v1 operations through `nexus_pb2`. Step assertions inspect legacy `ListNexus` results to confirm cross-version effects.

## State And Persistence
State includes module-scoped base bdevs, temporary local files under `/tmp`, a `created_nexuses` cleanup map, and published device URIs. Teardown destroys bdevs and nexuses.

## Dependencies And Integration Points
Depends on `pytest_bdd`, legacy `mayastor_pb2`, v1 `nexus_pb2`/`common_pb2`, common and v1 Mayastor fixtures, gRPC status codes, and feature files.

## Risks
Some steps intentionally expect current legacy/v1 mismatches, such as duplicate v1 create returning INTERNAL. Duplicate Python function names for publish steps can obscure reporting, though decorators still bind at import time.

## Test Signals
Passing scenarios signal v1 API compatibility for legacy nexus identity, children, publication state, error mapping, and list filters.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/cross-grpc-version/nexus/test_bdd_nexus.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/cross-grpc-version/pool/docker-compose.yml -->
# sources/control-plane/mayastor/test/python/cross-grpc-version/pool/docker-compose.yml

## Purpose
Single-node Docker Compose environment for cross-version pool API tests.

## Important APIs, Types, And Functions
Defines service `ms0` at `10.1.0.2`, enabling ANA/reservations and running io-engine with `--env-context=--iova-mode=pa`.

## Control Flow
pytest brings up `ms0`; legacy and v1 fixtures connect to the same service for mixed API operations.

## State And Persistence
Runtime state is in the container, with source tree, `/nix`, hugepages, `/tmp`, and `/var/tmp` mounted from the host.

## Dependencies And Integration Points
Requires host hugepages and Docker capabilities. Used by `test_bdd_pool.py`.

## Risks
Static network and shared host tmp can conflict with concurrent tests. The PA IOVA mode is a test-specific runtime assumption.

## Test Signals
Container readiness indicates both v0 and v1 pool APIs can target the same io-engine instance.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/cross-grpc-version/pool/docker-compose.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/cross-grpc-version/pool/test_bdd_pool.py -->
# sources/control-plane/mayastor/test/python/cross-grpc-version/pool/test_bdd_pool.py

## Purpose
BDD tests for v1 pool operations against pools created by the legacy API.

## Important APIs, Types, And Functions
Scenarios cover duplicate name creation, same-name/different-disk failure, list all, list by name, list non-existent name, and destroy. Fixtures include `create_v0_pool`, `create_v1_pool`, cleanup maps, `find_pool`, and v1 `ListPools` filters.

## Control Flow
A legacy pool is created with malloc disk URIs, v1 pool RPCs are attempted or used to list/destroy, and assertions compare gRPC status codes or list contents.

## State And Persistence
Fixture dictionaries track v0 and v1-created pools for teardown. Pool state itself is remote in `ms0`.

## Dependencies And Integration Points
Depends on `pytest_bdd`, legacy `mayastor_pb2`, v1 `pool_pb2`, common/v1 Mayastor fixtures, and gRPC status codes.

## Risks
Cleanup must reconcile resources created by either API version. Name/disk semantics are tightly coupled to current v1 error mapping.

## Test Signals
Passing tests prove v1 can list and destroy legacy pools and preserves expected conflict behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/cross-grpc-version/pool/test_bdd_pool.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/cross-grpc-version/rebuild/docker-compose.yml -->
# sources/control-plane/mayastor/test/python/cross-grpc-version/rebuild/docker-compose.yml

## Purpose
Single-node Docker Compose environment for cross-version rebuild BDD tests.

## Important APIs, Types, And Functions
Defines `ms0` at `10.1.0.2`, with ANA/reservation environment and io-engine cores `1,2`.

## Control Flow
The container runs one io-engine instance; tests create aio-backed nexus children on host-mounted `/tmp` and issue mixed v0/v1 rebuild commands.

## State And Persistence
State resides in the container and host `/tmp` image files created by tests.

## Dependencies And Integration Points
Used by `test_bdd_rebuild.py`, with mounted source tree, `/nix`, hugepages, and relaxed capabilities/seccomp.

## Risks
Shared `/tmp` and static network can interfere with parallel jobs. Rebuild tests need enough time and IO resources for state transitions.

## Test Signals
Container startup enables the same Mayastor instance to expose legacy nexus creation and v1 rebuild operations.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/cross-grpc-version/rebuild/docker-compose.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/cross-grpc-version/rebuild/test_bdd_rebuild.py -->
# sources/control-plane/mayastor/test/python/cross-grpc-version/rebuild/test_bdd_rebuild.py

## Purpose
BDD tests for v1 rebuild operations on a nexus created through the legacy API.

## Important APIs, Types, And Functions
Defines state conversion helpers, `lookup_nexus`, `lookup_nexus_child`, `wait_child_state`, `mayastor_nexus`, `rebuild_state`, and steps for add child, start/stop/pause/resume rebuild, child online/offline, stats retrieval, and assertions over nexus/child/rebuild counters.

## Control Flow
Module fixtures create source and target aio files. A legacy nexus is created with the source child, v1 nexus RPCs add the target child and control rebuild state, and then legacy/v1 state reads verify transitions and counters.

## State And Persistence
State includes `/tmp/disk-rebuild-source.img`, `/tmp/disk-rebuild-target.img`, the legacy nexus, target child, and rebuild task. Cleanup destroys the nexus and removes files.

## Dependencies And Integration Points
Depends on `pytest_bdd`, legacy `mayastor_pb2`, v1 `nexus_pb2`, gRPC status handling, `retrying.retry`, and both common/v1 Mayastor fixtures.

## Risks
Polling expects state to settle within retry defaults. Conversion maps must stay in sync with v1 enum names. Rebuild stats assertions depend on task progress being nonzero at the right moment.

## Test Signals
Passing scenarios validate cross-version rebuild command compatibility, child action mapping, stopped-state handling, and rebuild statistics visibility.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/cross-grpc-version/rebuild/test_bdd_rebuild.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/cross-grpc-version/replica/docker-compose.yml -->
# sources/control-plane/mayastor/test/python/cross-grpc-version/replica/docker-compose.yml

## Purpose
Single-node Docker Compose fixture for cross-version replica API tests.

## Important APIs, Types, And Functions
Defines `ms0` at `10.1.0.2`, io-engine cores `0,1`, ANA/reservation env vars, source/Nix/hugepages/tmp mounts, and `mayastor_net`.

## Control Flow
pytest starts one container and both legacy and v1 fixtures connect to it.

## State And Persistence
Replica and pool state is remote in `ms0`; host-mounted `/tmp` is available for tests.

## Dependencies And Integration Points
Used by `test_bdd_replica.py` and requires Docker, hugepages, and the local io-engine build.

## Risks
Static IP/network and host mounts can conflict with concurrent suites. Resource cleanup is delegated to pytest fixtures.

## Test Signals
Readiness means the same io-engine process can serve legacy replica creation and v1 replica operations.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/cross-grpc-version/replica/docker-compose.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/cross-grpc-version/replica/test_bdd_replica.py -->
# sources/control-plane/mayastor/test/python/cross-grpc-version/replica/test_bdd_replica.py

## Purpose
BDD compatibility tests for v1 replica operations against legacy-created pools and replicas.

## Important APIs, Types, And Functions
Scenarios cover duplicate name/UUID create failures, list all/by name/by pool, share NVMf, invalid iSCSI share, same/different protocol share, unshare, idempotent unshare, and destroy. Fixtures create a legacy pool, legacy replicas, v1 replicas, `find_replica`, and share protocol mapping.

## Control Flow
The legacy API creates a pool and v0 replicas. v1 replica RPCs then create/list/share/unshare/destroy or intentionally fail, while assertions inspect v1 `ListReplicas` output and gRPC status codes.

## State And Persistence
Fixture dictionaries track current replicas by UUID and clean them up through legacy or v1 APIs. The pool is module-scoped and destroyed after tests.

## Dependencies And Integration Points
Depends on `replica_pb2`, `common_pb2`, legacy `mayastor_pb2`, pytest-bdd feature files, and common/v1 Mayastor fixtures.

## Risks
The suite assumes stable mapping between legacy `ShareProtocolReplica` and v1 `common_pb` share enums. Duplicate resource cleanup can be fragile if a test fails midway.

## Test Signals
Passing scenarios show v1 replica RPCs can discover, share, unshare, reject invalid operations, and destroy legacy replicas.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/cross-grpc-version/replica/test_bdd_replica.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/k8s/fio.yaml -->
# sources/control-plane/mayastor/test/python/k8s/fio.yaml

## Purpose
Kubernetes manifest for running fio against multiple Mayastor PVCs.

## Important APIs, Types, And Functions
Defines a `ConfigMap` named `fiomap` containing `fio.conf` and a `Pod` named `fio` using image `mayadata/fio`. It mounts PVCs `ms-1` through `ms-6` and the fio config.

## Control Flow
When applied, Kubernetes creates the config map and pod; the pod runs `fio /config/fio.conf` and exits.

## State And Persistence
The fio job writes `vol.test` files under mounted PVC paths. The pod is `restartPolicy: Never`; PVC and ConfigMap lifecycle are managed by tests.

## Dependencies And Integration Points
Used by `test_pvc.py` through Kubernetes Python utilities. Integrates with default namespace PVCs, Mayastor storage classes, and fio verification settings.

## Risks
The config defines jobs for volume-1 through volume-4 but mounts six PVCs; dynamic manifest code may cover six elsewhere. PVC names are hard-coded.

## Test Signals
A succeeded fio pod validates PVC binding, filesystem mounts, and IO correctness with crc32 verification.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/k8s/fio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/k8s/test_pvc.py -->
# sources/control-plane/mayastor/test/python/k8s/test_pvc.py

## Purpose
Async pytest coverage for Kubernetes Mayastor pool, PVC, and fio workflows.

## Important APIs, Types, And Functions
Defines Kubernetes helpers `get_api`, `create_msp`, `delete_msp`, `create_pvc`, `delete_pvc`, `wait_for_it`, `wait_until_gone`, `watch_for`, `fio_delete`, `fio_from_yaml`, `create_fio_manifest`, and test `test_msp`.

## Control Flow
The test loads kube config, creates MayastorPool custom resources, creates PVCs against a storage class, waits for Bound/Running/Succeeded phases, runs fio from either static YAML or generated manifests, and deletes resources.

## State And Persistence
State is Kubernetes CRDs, PVCs, ConfigMaps, Pods, and Mayastor-backed volumes. Cleanup deletes PVC/fio resources but depends on cluster behavior for finalizers.

## Dependencies And Integration Points
Depends on the Kubernetes Python client, dynamic client, watch API, asyncio, `yaml`, and local `fio.yaml`. Integrates with Mayastor CRDs and storage classes.

## Risks
Cluster-specific names, namespaces, storage classes, and CRD schema can break tests. The watch/wait loops use fixed iteration counts and sleep behavior, and `assert event["object"].status.phase, "Succeeded"` appears to assert truthiness rather than equality.

## Test Signals
PVC Bound state, fio pod Succeeded state, and MayastorPool online status provide end-to-end Kubernetes control-plane and datapath signals.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/k8s/test_pvc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/pool/docker-compose.yml -->
# sources/control-plane/mayastor/test/python/pool/docker-compose.yml

## Purpose
Docker Compose environment for pool tests that require direct device access.

## Important APIs, Types, And Functions
Defines a single privileged `ms0` service at `10.1.0.2` with `RUST_LOG=mayastor=trace`, reservation support, `/dev` mounted, hugepages, source tree, `/nix`, `/tmp`, and `/var/tmp`.

## Control Flow
pytest starts `ms0`; pool tests can create pools over host-visible devices or temporary files.

## State And Persistence
State includes remote Mayastor pool metadata and host device/file effects through `/dev` and `/tmp` mounts.

## Dependencies And Integration Points
Used by `pool/test_unmap.py`. Requires privileged Docker and host device access.

## Risks
Privileged `/dev` mounting gives tests broad host access. Static network naming can conflict with other suites.

## Test Signals
Container readiness with `/dev` access enables block discard/unmap behavior to be validated.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/pool/docker-compose.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/pool/test_unmap.py -->
# sources/control-plane/mayastor/test/python/pool/test_unmap.py

## Purpose
Tests pool behavior around unmap/discard support.

## Important APIs, Types, And Functions
Uses Mayastor fixtures and command helpers to create backing storage, create a pool, likely issue discard/unmap-relevant IO, and compare used-space accounting.

## Control Flow
The test creates a pool on the single compose Mayastor instance, creates/writes/removes data, and checks pool usage changes to ensure unmap/discard releases space as expected.

## State And Persistence
State is the test pool, backing file/device, and pool usage counters. Cleanup destroys the pool and removes temporary artifacts.

## Dependencies And Integration Points
Depends on the `pool/docker-compose.yml` privileged container, common Mayastor fixtures, local shell tools, and io-engine pool accounting.

## Risks
Discard semantics depend on backing device support and filesystem/kernel behavior. Space accounting can be asynchronous or rounded by pool cluster size.

## Test Signals
Observed pool used-space decrease after discard/unmap is the main behavioral signal.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/pool/test_unmap.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/pytest.ini -->
# sources/control-plane/mayastor/test/python/pytest.ini

## Purpose
pytest configuration for Mayastor Python tests.

## Important APIs, Types, And Functions
Sets `log_cli = true`, `log_level = warn`, `console_output_style = classic`, and `asyncio_default_fixture_loop_scope = function`.

## Control Flow
pytest reads this configuration before collecting tests.

## State And Persistence
No runtime state beyond pytest configuration.

## Dependencies And Integration Points
Applies to pytest, pytest-asyncio, and logging output for the Python test tree.

## Risks
Changing async fixture loop scope can affect tests using module-scoped async resources. Warn-level logging may hide useful debug details in flaky integration failures.

## Test Signals
Consistent collection/runtime behavior and visible warnings/errors in console output.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/pytest.ini -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/setup.sh -->
# sources/control-plane/mayastor/test/python/setup.sh

## Purpose
Bootstraps the Python test environment and generated gRPC modules.

## Important APIs, Types, And Functions
Runs `grpc_tools.protoc` for legacy `mayastor.proto` and v1 protobufs, then creates `test/python/venv` and installs `requirements.txt`.

## Control Flow
The script uses `set -euxo pipefail`, requires `SRCDIR`, changes to it, generates Python protobuf code into `test/python`, creates a virtualenv without setuptools, and installs dependencies.

## State And Persistence
Writes generated protobuf Python files and a virtualenv under the source tree.

## Dependencies And Integration Points
Depends on Python, `grpc_tools`, `virtualenv`, requirements, `SRCDIR`, and the protobuf submodule path under `utils/dependencies/apis/io-engine/protobuf`.

## Risks
Generated files can become stale if protos change and setup is not rerun. The script assumes `IO_ENGINE_DIR` indirectly through tests but not here.

## Test Signals
Successful setup means Python tests can import generated legacy and v1 gRPC modules.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/setup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/test_common.py -->
# sources/control-plane/mayastor/test/python/test_common.py

## Purpose
Small smoke tests for the reusable Mayastor Python fixtures and handle methods.

## Important APIs, Types, And Functions
Uses `containers` and `mayastors` fixtures and asserts that container mappings and gRPC handles are available, including pool/bdev list readiness.

## Control Flow
pytest collects simple tests that access fixture-provided dictionaries and perform basic handle operations against compose services.

## State And Persistence
No resources are intentionally persisted; any state is read-only inspection of running Mayastor containers.

## Dependencies And Integration Points
Depends on `common.mayastor` fixtures and the active Docker Compose test environment.

## Risks
These tests mostly validate fixture wiring, so they can pass while deeper control/data path behavior is broken.

## Test Signals
Passing smoke tests show compose service discovery, network IP extraction, and gRPC readiness are functional.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/test_common.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/test_config.ini -->
# sources/control-plane/mayastor/test/python/test_config.ini

## Purpose
pytest-testconfig configuration for Mayastor Python tests.

## Important APIs, Types, And Functions
Defines `[grpc] client_timeout = 120`.

## Control Flow
`pytest_testconfig` loads this value; `MayastorHandle` reads it to set default gRPC call timeouts.

## State And Persistence
No runtime state beyond configuration.

## Dependencies And Integration Points
Used by `common/hdl.py` and all tests that instantiate `MayastorHandle`.

## Risks
A single global timeout may be too high for fast-fail tests or too low for overloaded integration hosts.

## Test Signals
Consistent timeout behavior across gRPC test calls.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/test_config.ini -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/ana_client/docker-compose.yml -->
# sources/control-plane/mayastor/test/python/tests/ana_client/docker-compose.yml

## Purpose
Four-node compose topology for ANA/multipath client behavior tests.

## Important APIs, Types, And Functions
Defines `ms0`-`ms3` with static IPs `10.1.0.2`-`10.1.0.5`, ANA/reservations enabled, configurable cores, interrupt/poll/log environment, and `NVME_KATO_MS=1000` on `ms3`.

## Control Flow
pytest starts all services; tests create replicas/nexuses across nodes and connect kernel NVMe paths.

## State And Persistence
State is container runtime, Mayastor pools/replicas/nexuses, and host kernel NVMe connections.

## Dependencies And Integration Points
Requires Docker, hugepages, capabilities, source/Nix mounts, and static `mayastor_net`. Used by `test_ana_client.py`.

## Risks
Multipath tests are sensitive to kernel NVMe behavior, KATO timing, and concurrent use of the static network.

## Test Signals
Ready topology supports ANA path and namespace GUID validation across multiple Mayastor nodes.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/ana_client/docker-compose.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/ana_client/test_ana_client.py -->
# sources/control-plane/mayastor/test/python/tests/ana_client/test_ana_client.py

## Purpose
Tests Linux ANA/multipath client behavior against multiple published Mayastor nexuses.

## Important APIs, Types, And Functions
Fixtures `create_replicas` and `create_nexuses` build pools/replicas and publish nexuses on `ms2`/`ms3`. Helpers connect multiple paths. Tests `test_io_policy` and `test_namespace_guid` inspect NVMe subsystem paths, sysfs virtual controller links, IO policy files, nexus info keys, and namespace identifiers.

## Control Flow
The suite disconnects all NVMe controllers, creates replicas on `ms0`/`ms1`, publishes two nexuses with the same GUID, connects both paths, asserts one multipath namespace, verifies path ANA state and sysfs policy, then checks namespace NGUID/EUI64 values.

## State And Persistence
State includes pools, replicas, nexuses, kernel NVMe connections, and sysfs multipath entries. Teardown disconnects NVMe and destroys nexuses/pools.

## Dependencies And Integration Points
Depends on `common.nvme`, `mayastor_pb2`, Docker fixtures, `/sys/class/nvme-subsystem`, `/sys/block/<dev>/queue/iopolicy`, and Linux NVMe multipath.

## Risks
Sysfs layout and path state names are kernel-version dependent. The tests use `glob` and fixed expectations for virtual controller counts.

## Test Signals
Passing tests indicate Mayastor ANA exports form a single multipath namespace with optimized live paths and correct namespace identity.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/ana_client/test_ana_client.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/cli_controller/docker-compose.yml -->
# sources/control-plane/mayastor/test/python/tests/cli_controller/docker-compose.yml

## Purpose
Three-node compose topology for testing `io-engine-client` controller list/stat commands.

## Important APIs, Types, And Functions
Defines services `ms1`, `ms2`, and `ms3` with static IPs, ANA/reservations, configurable cores, interrupt/poll/log variables, and KATO on `ms3`.

## Control Flow
Tests create replicas on `ms1`/`ms2` and a nexus on `ms3`, then point the CLI at target URLs.

## State And Persistence
State is transient pools, replicas, nexus, and NVMf controllers created during tests.

## Dependencies And Integration Points
Requires Docker, hugepages, source/Nix mounts, `mayastor_net`, and the built `io-engine-client`.

## Risks
CLI tests fail if binary paths or service names differ. Static IPs can collide with other compose suites.

## Test Signals
Ready services allow CLI controller output to be compared with gRPC-created resources.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/cli_controller/docker-compose.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/cli_controller/test_cli_controller.py -->
# sources/control-plane/mayastor/test/python/tests/cli_controller/test_cli_controller.py

## Purpose
Validates Mayastor CLI controller listing and statistics for nexus child controllers.

## Important APIs, Types, And Functions
Fixtures create replicas and a published nexus. Helpers `assure_controllers` and `ctrl_name_from_uri` map child URIs to expected controller names. Tests `test_controller_list` and `test_controller_stats` use `get_msclient().with_json_output()` and SPDK fio traffic.

## Control Flow
The tests create two remote replicas and a nexus, query controller lists from replica and nexus nodes, remove/add a child, then run SPDK fio and assert stats counters and byte counts are present for both controllers.

## State And Persistence
State includes pools, replicas, nexus, child controllers, CLI output, and fio-generated IO. Fixture teardown destroys pools and nexus.

## Dependencies And Integration Points
Depends on common fixtures, `MayastorClient`, `FioSpdk`, v0 gRPC, JSON CLI output, and SPDK fio.

## Risks
Controller naming is parsed from URI path components and can break with URI format changes. Stats expectations depend on fio completing and controller counters being updated before the next CLI query.

## Test Signals
Passing tests prove CLI controller list/stat views match active nexus child controllers and show IO activity.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/cli_controller/test_cli_controller.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/nexus/docker-compose.yml -->
# sources/control-plane/mayastor/test/python/tests/nexus/docker-compose.yml

## Purpose
Four-node compose topology for general nexus integration tests.

## Important APIs, Types, And Functions
Defines `ms0`-`ms3`, static IPs, ANA/reservation env vars, `NEXUS_DONT_READ_LABELS=true` on `ms3`, and source/Nix/hugepages/tmp mounts.

## Control Flow
Tests create pools and replicas on remote nodes and nexuses on `ms0`/`ms3`, then connect kernel or SPDK initiators.

## State And Persistence
State includes pools, replicas, nexuses, NVMf publications, kernel connections, and temporary aio/null devices.

## Dependencies And Integration Points
Used by multiple `tests/nexus/*.py` files. Requires Docker, hugepages, static `mayastor_net`, and local io-engine build.

## Risks
Shared service names and static IPs limit concurrent execution. `NEXUS_DONT_READ_LABELS` is test-specific and can hide label-reading paths.

## Test Signals
Ready services support multi-node nexus data path, fault, shutdown, null-device, and remote-only tests.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/nexus/docker-compose.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/nexus/test_multi_nexus.py -->
# sources/control-plane/mayastor/test/python/tests/nexus/test_multi_nexus.py

## Purpose
Tests multiple simultaneous nexuses and replica behavior across all compose nodes.

## Important APIs, Types, And Functions
Fixtures create temp files, pools, multiple replicas on all nodes, nexuses, connected devices, and mounted filesystems. Tests include restart behavior and multiple raw, filesystem, and SPDK fio workloads.

## Control Flow
The setup creates one pool per node from `/tmp/<node>.img`, creates several replicas with shared UUIDs across nodes, creates nexuses over those replicas, connects NVMe devices, optionally mounts filesystems, then runs fio while containers may restart or multiple nexuses run concurrently.

## State And Persistence
State includes per-node image files, pools, replicas, nexuses, kernel NVMe devices, mounts, and fio workloads. Fixtures attempt cleanup through destroy/disconnect/unmount paths.

## Dependencies And Integration Points
Depends on `MayastorHandle`, common command/NVMe/fio/SPDK helpers, docker fixtures, asyncio, and pytest-asyncio.

## Risks
Concurrent IO and container restarts make timing and cleanup sensitive. Reusing UUID patterns across nodes requires precise teardown to avoid stale resources.

## Test Signals
Passing tests signal that multiple nexuses can coexist and survive restart/data path scenarios without corrupting IO.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/nexus/test_multi_nexus.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/nexus/test_nexus.py -->
# sources/control-plane/mayastor/test/python/tests/nexus/test_nexus.py

## Purpose
Core Python integration tests for two-replica nexuses, v2 nexus fields, reservation keys, controller IDs, and failure/degraded behavior under IO.

## Important APIs, Types, And Functions
Fixtures create pools, replicas, v1-style and v2-style nexuses, UUID/name/controller/reservation-key values. Tests cover ENOSPC via `Volume`, killing one or all replica containers during fio/SPDK IO, controller ID support, Dataset Management/Write Zeroes bits, reservation reports, and skipped preempt-key behavior.

## Control Flow
Most tests create pools on `ms1`/`ms2`, create replicas, create/publish nexus on `ms3` or `ms0`, connect kernel NVMe or run SPDK fio, induce container failure, and assert nexus/child states or NVMe metadata.

## State And Persistence
State includes pools, replicas, nexuses, NVMf connections, reservation registrations, fio IO, and Docker container lifecycle. Fixtures destroy resources after each test.

## Dependencies And Integration Points
Depends on common fixtures, `Volume`, `Fio`, `FioSpdk`, NVMe helpers, legacy `mayastor_pb2`, gRPC status codes, and Docker restart/kill behavior.

## Risks
Failure timing and fio completion are race-prone. Reservation/preempt coverage is partly skipped, and assertions depend on kernel NVMe CLI JSON formats and Mayastor state propagation.

## Test Signals
Passing tests show nexus creation/publish, degraded/faulted state transitions, NVMe identify/reservation behavior, and IO continuity/failure behavior across replica failures.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/nexus/test_nexus.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/nexus/test_nexus_rebuild.py -->
# sources/control-plane/mayastor/test/python/tests/nexus/test_nexus_rebuild.py

## Purpose
Tests nexus rebuild behavior in the Python integration suite.

## Important APIs, Types, And Functions
Uses Mayastor handles, pool/replica/nexus fixtures, child add/remove, rebuild state/stat APIs, fio or command helpers, and assertions over child/nexus states.

## Control Flow
The test creates a degraded nexus, adds or replaces a child, starts rebuild or waits for automatic rebuild, polls states/statistics, and verifies the target child returns online or the expected rebuild state is observed.

## State And Persistence
State is remote pools, replicas, nexus children, and rebuild tasks. Cleanup removes children, destroys nexuses/replicas/pools, and disconnects any devices.

## Dependencies And Integration Points
Depends on `tests/nexus/docker-compose.yml`, common Mayastor/NVMe/fio helpers, and legacy protobuf state enums.

## Risks
Rebuild timing is asynchronous and data-size dependent. Polling windows and child ordering assumptions can introduce flakes.

## Test Signals
Passing tests signal that adding/rebuilding children restores mirrored nexus health and exposes correct rebuild progress.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/nexus/test_nexus_rebuild.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/nexus/test_nexus_shutdown.py -->
# sources/control-plane/mayastor/test/python/tests/nexus/test_nexus_shutdown.py

## Purpose
BDD-style tests for the `ShutdownNexus` operation and initiator behavior while a nexus is shut down.

## Important APIs, Types, And Functions
Defines fixtures for published/connected nexus, pools, replicas, and fio workload. Steps verify shutdown state, degraded children, repeated shutdown idempotency, and fio remaining blocked rather than failing.

## Control Flow
The suite creates a two-child nexus, connects it with NVMe, starts fio, issues `nexus_shutdown`, asserts nexus state `NEXUS_SHUTDOWN` and child degraded states, then verifies fio does not exit with IO errors and a second shutdown succeeds.

## State And Persistence
State includes published nexus, kernel NVMe controller, running fio process, pools, replicas, and container resources. Cleanup forcibly deletes NVMe controller and destroys resources.

## Dependencies And Integration Points
Depends on `pytest_bdd`, common NVMe helpers including forced controller deletion, fio, Docker compose fixtures, and legacy Mayastor shutdown RPC.

## Risks
The desired fio behavior is a hang/wait condition, so test timeouts must distinguish success from deadlock. Kernel NVMe controller state may survive failed cleanup.

## Test Signals
Passing scenarios show shutdown is idempotent, visible in gRPC state, and does not cause immediate filesystem/initiator IO failure.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/nexus/test_nexus_shutdown.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/nexus/test_null_nexus.py -->
# sources/control-plane/mayastor/test/python/tests/nexus/test_null_nexus.py

## Purpose
Tests nexuses built from Mayastor `null` bdevs that can be written but not read.

## Important APIs, Types, And Functions
Helpers/fixtures create null devices on selected nodes, share them, create/publish nexuses on a target node, connect devices with NVMe, and run fio. `check_nexus_state` asserts expected nexus state.

## Control Flow
The test creates null devices, shares them over NVMf, creates multiple nexuses from grouped children, publishes and connects all, then runs randwrite fio across connected devices.

## State And Persistence
State is transient null bdevs, NVMf exports, nexuses, kernel NVMe connections, and fio writes. Cleanup unpublishes/destroys nexuses and disconnects devices.

## Dependencies And Integration Points
Depends on `NEXUS_DONT_READ_LABELS=true` in compose, common NVMe/fio/command helpers, and Mayastor bdev/nexus APIs.

## Risks
Null bdevs do not support reads, so any unexpected read path or label read breaks behavior. Multiple device connection cleanup is critical.

## Test Signals
Successful write-only fio across null-backed nexuses confirms Mayastor can operate with label-read-disabled test devices.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/nexus/test_null_nexus.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/nexus/test_remote_only.py -->
# sources/control-plane/mayastor/test/python/tests/nexus/test_remote_only.py

## Purpose
Stress/regression test for nexuses whose children are all remote NVMf bdevs.

## Important APIs, Types, And Functions
Defines `ensure_zero_devices`, `create_publish`, `delete_all_bdevs`, and parametrized `test_remote_only` running ten iterations.

## Control Flow
For each iteration, the test ensures no bdevs exist, creates remote malloc bdevs and shares them, creates/publishes nexuses on a local node using remote children, destroys/publishes cleanup, deletes remote bdevs, waits briefly, and verifies all nodes return to zero bdevs.

## State And Persistence
State includes remote malloc bdevs, shared NVMf URIs, local nexus bdevs, and published resources. The test is designed to leave no bdevs behind.

## Dependencies And Integration Points
Depends on module-scoped Mayastor fixtures and remote NVMf bdev creation/sharing through `MayastorHandle`.

## Risks
Fixed sleeps and ten-iteration loops can be flaky or slow. `ensure_zero_devices` is strict and may fail due to unrelated leftovers from previous tests.

## Test Signals
Passing iterations indicate remote-only nexus creation and teardown do not leak local or remote bdevs.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/nexus/test_remote_only.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/nexus_fault/docker-compose.yml -->
# sources/control-plane/mayastor/test/python/tests/nexus_fault/docker-compose.yml

## Purpose
Two-node compose topology for nexus fault and replacement tests.

## Important APIs, Types, And Functions
Defines `ms0` and `ms1` with ANA/reservation support, configurable cores, interrupt/poll/log variables, static IPs `10.1.0.2` and `10.1.0.3`, and shared source/Nix/hugepages/tmp mounts.

## Control Flow
Tests use one node as local nexus and one as remote replica, then restart/recreate resources to force fault handling.

## State And Persistence
State is transient pools, replicas, nexuses, kernel NVMe controllers, mounted filesystems, and host `/tmp` backing files.

## Dependencies And Integration Points
Used by `test_nexus_fault.py`. Requires Docker, hugepages, capabilities, and local fio/NVMe tooling on the host.

## Risks
Container restart timing and KATO/fault detection can vary by host load.

## Test Signals
Ready topology enables filesystem-over-NVMe tests during temporary nexus faults and path replacement.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/nexus_fault/docker-compose.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/nexus_fault/test_nexus_fault.py -->
# sources/control-plane/mayastor/test/python/tests/nexus_fault/test_nexus_fault.py

## Purpose
BDD tests ensuring a temporary nexus fault or path replacement does not cause the initiator filesystem workload to fail.

## Important APIs, Types, And Functions
Scenarios cover remote Mayastor restart and recreating/replacing a faulted nexus. Fixtures create pool/replica/nexus, publish NVMf, connect kernel NVMe, mount ext4, run fio, republish on same or alternate node, find controllers, and check remote readiness.

## Control Flow
The test creates a single-replica remote nexus, connects and mounts it, starts fio on a file, restarts or recreates the remote backing resources, optionally connects a replacement nexus and disconnects the old controller, then waits for fio and verifies the filesystem is still mounted.

## State And Persistence
State includes aio backing files, pool, replica, nexus, kernel NVMe controller, mounted filesystem, and a running fio process. Cleanup unmounts, disconnects, and destroys/recreates Mayastor resources.

## Dependencies And Integration Points
Depends on pytest-bdd, retrying, `nix-sudo` mount/mkfs commands, fio, NVMe helper functions, Docker restart, and v2 nexus creation.

## Risks
Filesystem and NVMe recovery timing is highly environment-dependent. Reusing the same replica UUID during recreate paths requires careful teardown.

## Test Signals
fio exit code zero and a still-mounted filesystem are the primary evidence that temporary nexus fault/replacement did not surface as application IO failure.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/nexus_fault/test_nexus_fault.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/nexus_multipath/docker-compose.yml -->
# sources/control-plane/mayastor/test/python/tests/nexus_multipath/docker-compose.yml

## Purpose
Four-node compose topology for nexus multipath and reservation-key tests.

## Important APIs, Types, And Functions
Defines `ms0`-`ms3`, static IPs, ANA/reservation support, configurable cores, KATO on `ms3`, and shared source/Nix/hugepages/tmp mounts.

## Control Flow
Tests create replicas on `ms1`/`ms2` and multiple nexuses on `ms0`/`ms1`/`ms2`/`ms3` to form multiple paths to one namespace.

## State And Persistence
State includes pools, replicas, multiple published nexuses, kernel multipath controllers, and reservation registrations.

## Dependencies And Integration Points
Used by both imperative and BDD multipath test files. Requires Linux NVMe multipath behavior and Docker network stability.

## Risks
Static network/IPs and host kernel multipath state can conflict across parallel tests. KATO/path-state timing can vary.

## Test Signals
Ready topology supports path count, path state, failover, and reservation key validation.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/nexus_multipath/docker-compose.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/nexus_multipath/test_bdd_nexus_multipath.py -->
# sources/control-plane/mayastor/test/python/tests/nexus_multipath/test_bdd_nexus_multipath.py

## Purpose
BDD tests for ANA NVMe multipath behavior and replacing a failed IO path on demand.

## Important APIs, Types, And Functions
Fixtures create two-replica nexuses, a second nexus over the same replicas, one-replica connected/disconnected nexuses, pools, replicas, controller IDs, and reservation keys. Steps connect clients, verify path states, run fio, degrade a path, add a second path, remove the failed path, and wait for fio completion.

## Control Flow
The first scenario connects two controllers to one namespace, starts fio, and checks IO statistics route through the active nexus. The second scenario starts fio through one path, restarts the serving container to degrade it, connects another nexus as replacement, removes the broken controller, and verifies fio finishes.

## State And Persistence
State includes pools/replicas, multiple v2 nexuses, kernel NVMe controllers, fio processes, and path states. Setup/teardown disconnects all NVMe controllers around the module.

## Dependencies And Integration Points
Depends on pytest-bdd feature files, common Mayastor/NVMe/fio helpers, Docker container restarts, legacy protobuf enums, and Linux multipath sysfs/CLI output.

## Risks
Path states such as `live` and `connecting` are timing-sensitive. The IO stats assertion assumes specific controller selection and may vary with ANA/path policy changes.

## Test Signals
Passing scenarios show multipath namespace merging, IO path preference, live replacement of failed paths, and fio continuity.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/nexus_multipath/test_bdd_nexus_multipath.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/nexus_multipath/test_nexus_multipath.py -->
# sources/control-plane/mayastor/test/python/tests/nexus_multipath/test_nexus_multipath.py

## Purpose
Imperative pytest coverage for multi-path nexus behavior, NVMe reservation registrations, and adding/removing paths.

## Important APIs, Types, And Functions
Fixtures create nexuses without immediate destroy, second/third path nexuses, connected devices, pools, replicas, controller IDs, reservation keys, fio workload, and path verification. Tests cover reservation report with two controllers, adding a third path, removing a third path, and removing all paths.

## Control Flow
The suite creates two replicas, publishes one or more nexuses over the same children from different nodes, connects them with `nvme_connect`, verifies they map to one namespace, inspects `nvme list-subsys` path counts/states, and checks `nvme resv-report` registration keys and controller status bits.

## State And Persistence
State includes pools, replicas, multiple nexuses sharing children, kernel NVMe multipath controllers, reservation state on child replicas, and fio IO. Cleanup disconnects and destroys resources through fixtures.

## Dependencies And Integration Points
Depends on common `Volume`, `MayastorHandle`, NVMe helpers, fio, retrying, Docker fixtures, and `mayastor_pb2` enums.

## Risks
Reservation report ordering, path state values, and multipath timing are kernel and load dependent. Several fixtures intentionally delay cleanup until after path manipulation, so failed tests can leave controllers behind.

## Test Signals
Passing tests show correct namespace coalescing, reservation key registration across controllers, and path add/remove behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/nexus_multipath/test_nexus_multipath.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/publish/docker-compose.yml -->
# sources/control-plane/mayastor/test/python/tests/publish/docker-compose.yml

## Purpose
Two-node compose topology for BDD nexus publish/lifecycle tests.

## Important APIs, Types, And Functions
Defines `ms0` and `ms1` with ANA/reservation support, configurable cores, interrupt/poll/log variables, static IPs, and shared source/Nix/hugepages/tmp mounts.

## Control Flow
Tests create local and remote bdevs, create nexuses, and exercise publish/unpublish operations on these two nodes.

## State And Persistence
State is transient bdevs, local files, shared NVMf URI, nexuses, and published device URIs.

## Dependencies And Integration Points
Used by `tests/publish/test_bdd_nexus.py`; requires Docker, hugepages, and local io-engine build.

## Risks
Only two nodes are available, so broader multipath behavior is outside this fixture. Static IP/network conflicts are possible.

## Test Signals
Ready services enable BDD lifecycle coverage for nexus creation, child validation, publish protocol rules, and cleanup.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/publish/docker-compose.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/publish/test_bdd_nexus.py -->
# sources/control-plane/mayastor/test/python/tests/publish/test_bdd_nexus.py

## Purpose
BDD tests for legacy nexus creation, destruction, listing, child mutation, and publish/unpublish behavior.

## Important APIs, Types, And Functions
Scenarios cover creating a nexus, duplicate create, in-use children, no children, missing children, mixed block sizes, oversized nexus, destroy variants, list, remove/add child, publish/unpublish, republish same/different protocol, and crypto-key publish. Fixtures provide bdevs, shared remote bdev URI, local aio/uring/malloc files, child lists, created nexus cleanup, and `find_nexus`.

## Control Flow
The suite creates base bdevs on local/remote nodes, shares one remote bdev over NVMf, prepares local file-backed child URIs, creates legacy nexuses, executes BDD steps through legacy Mayastor gRPC calls, and asserts list state, child URI sets, device URI presence, or expected gRPC errors.

## State And Persistence
State includes module-scoped bdevs, temporary local files, shared NVMf exports, created nexuses map, and published device URIs. Fixtures destroy bdevs/nexuses and remove files.

## Dependencies And Integration Points
Depends on pytest-bdd, common Mayastor fixtures, `Volume`, `grpc`, legacy `mayastor_pb2`, `nvme_nqn_prefix`, and feature files.

## Risks
Error-code assertions document current behavior, including INTERNAL for no-children and oversized cases. The file uses duplicate function names for some BDD steps, which is legal but can make debugging less clear.

## Test Signals
Passing scenarios provide broad legacy nexus API contract coverage for lifecycle, validation, child management, and publication semantics.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/publish/test_bdd_nexus.py -->
