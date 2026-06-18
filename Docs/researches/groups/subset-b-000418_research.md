# Research Report: subset-b-000418

This grouped report covers io-engine integration and SPDK runtime tests under `sources/control-plane/mayastor/io-engine/tests`. Each section is source-tree-aligned and wrapped for reconciliation into a per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_crd.rs -->
# sources/control-plane/mayastor/io-engine/tests/nexus_crd.rs

Purpose: validates controller retry delay (CRD) behavior for nexus NVMf targets, including recovery from a failed and recreated nexus while initiator I/O is in flight, and reservation-conflict CRD selection when multiple CRD delay slots are configured.

Important APIs and types: `Builder`, `Binary`, `GrpcConnect`, `SharedRpcHandle`, `PoolBuilder`, `ReplicaBuilder`, `NexusBuilder`, `NvmfLocation`, `NmveConnectGuard`, `FioBuilder`, `FioJobBuilder`, `FioJobResult`, `InjectionBuilder`, `FaultDomain::NexusChild`, `FaultIoOperation::{Read,Write}`, `NexusNvmePreemption`, and `NvmeReservation`. `NexusManageTask` packages the nexus handle, replica builder, and write/read injection URIs for the concurrent management task.

Control flow: `nexus_fail_no_crd` and `nexus_fail_crd` both call `test_nexus_fail` with different `--tgt-crdt` values. The helper starts one replica node and one nexus node, creates a thick replica, publishes a nexus, builds child read/write injections from the actual child device name, then runs two tokio tasks. `run_io_task` connects to the published nexus and runs several randwrite FIO jobs; `run_nexus_manage_task` waits for connection, injects read/write faults, destroys the nexus, removes injections, recreates the same UUID/name nexus, and republishes it. The no-CRD test expects FIO to error; the CRD-enabled test expects I/O to survive the freeze/retry window.

State and persistence behavior: this file does not use etcd persistence, but it relies on stable nexus UUID, NQN, and serial identity across destroy/recreate so the initiator retry path can complete against the replacement target. The reservation test uses `--ptpl-dir` and host IDs to exercise target-side persistent reservation metadata.

Integration points: containerized io-engine, NVMf host utilities, FIO, Linux errno mapping, fault injection RPCs, and SPDK/NVMe reservation behavior. `nexus_crd_resv` creates two competing nexuses over one replica with different reservation keys and checks that an I/O reservation conflict uses the zero-delay CRD slot by asserting FIO completion time is below the configured total delay.

Risks: timing-sensitive sleeps make failures possible on slow CI; CRD semantics depend on kernel NVMe retry behavior and Linux-specific `EBADE`; recreated nexus identity must exactly match the original. A code typo in comments does not affect behavior, but tests gated by `fault-injection` will not run without that feature.

Test signals: expected success/failure of FIO, reservation-error result and duration, child fault injection path, NVMf reconnect behavior, and successful recreation/publish of the same nexus identity.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_crd.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_create_destroy.rs -->
# sources/control-plane/mayastor/io-engine/tests/nexus_create_destroy.rs

Purpose: stress-tests basic v0 nexus lifecycle RPCs by repeatedly creating and destroying malloc-backed nexuses on a single io-engine instance.

Important APIs and types: v0 `CreateNexusRequest`, `DestroyNexusRequest`, `Nexus`, `GrpcConnect`, `RpcHandle`, `Builder`, and dynamically generated `uuid::Uuid` values. `NEXUS_COUNT` fixes each test at ten lifecycle iterations.

Control flow: `nexus_create_destroy` creates one container, opens a v0 gRPC handle, then loops ten times creating a 10 MiB nexus with one `malloc:///d{i}` child and immediately destroying it by returned UUID. `nexus_create_multiple_then_destroy` first creates ten nexuses with `create_nexuses`, destroys them in original order, recreates ten more, and destroys the second batch in reverse order.

State and persistence behavior: no explicit persistent store is configured. The tests validate in-memory registry cleanup, child malloc bdev cleanup, UUID handling, and destroy ordering independence. Because child URIs are unique per index within each batch, stale child/device state would show up as create failures on a later batch.

Dependencies and integration points: this file uses the compose harness and v0 mayastor RPC surface. It is intentionally narrow and avoids NVMf, FIO, or multi-node orchestration.

Risks: the tests assert only that RPC calls succeed; they do not list nexuses afterward to prove the registry is empty. They also depend on the io-engine test harness cleaning container state between tests.

Test signals: successful create response, successful destroy by returned UUID, absence of create collisions across two batches, and absence of reverse-order teardown bugs.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_create_destroy.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_fault_injection.rs -->
# sources/control-plane/mayastor/io-engine/tests/nexus_fault_injection.rs

Purpose: validates io-engine fault injection at nexus-child and replica-bdev layers, including URI parsing, write/read submission and completion faults, time and range activation windows, and injected NVMe error propagation to FIO.

Important APIs and types: `InjectionBuilder`, `Injection`, `FaultDomain::{NexusChild,BdevIo,BlockDevice}`, `FaultIoOperation`, `FaultIoStage`, `FaultMethod`, `IoCompletionStatus`, `NvmeStatus`, `add_fault_injection`, `list_fault_injections`, `NexusBuilder`, `ReplicaBuilder`, `PoolBuilder`, `ChildState`, `ChildStateReason`, `FioBuilder`, and `test_write_to_nexus`.

Control flow: `create_compose_test` starts two replica nodes and a nexus node. `create_test_storage` creates two thin replicas, shares them, creates and publishes a two-child nexus. `test_injection_uri` formats an `inject://<device>?...` URI for the first child, adds it, lists injections, writes to the nexus, and expects the first child to fault. Four tests vary operation and stage. `nexus_fault_injection_time_based` verifies an injection is inactive, later faults the child, expires, and no longer faults after onlining. `nexus_fault_injection_range_based` verifies block-range boundaries around offsets 128..144.

State and persistence behavior: state is in-memory child state and injection registry. The time-based test explicitly transitions a child from online to faulted and back to online. Range tests use repeated online operations and later writes to prove injection activation is tied to block windows rather than permanent device state.

Integration points: compose containers, gRPC injection helpers, SPDK child state transitions, FIO, NVMf connection helpers, and Linux `std::io::ErrorKind`. `injection_uri_creation` is a pure serialization/deserialization test proving built URIs round-trip all fields.

Risks: `test_injection_uri` appears to compare `children[0].state` to `ChildStateReason::CannotOpen as i32`; that assertion likely intends `state_reason`, so this test path is suspicious. Time windows depend on sleeps. Feature gate `fault-injection` excludes the file unless enabled.

Test signals: listed injection count and device match, child `Faulted`/`IoFailure` or `Online` states, URI round-trip equality across all injection fields, and expected FIO success/failure around injected bdev I/O.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_fault_injection.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_fio.rs -->
# sources/control-plane/mayastor/io-engine/tests/nexus_fio.rs

Purpose: uses FIO against published nexuses to validate thin-provisioned ENOSPC handling for a single overcommitted remote replica and a mixed two-replica nexus where one replica still has enough backing capacity.

Important APIs and types: `PoolBuilder`, `ReplicaBuilder`, `NexusBuilder`, `FioBuilder`, `FioJobBuilder`, `DataSize`, and `test_fio_to_nexus`. Constants model an 80 MiB pool, a 60 MiB thick filler replica, an overcommitted thin replica, and data sizes below/above remaining pool capacity.

Control flow: `nexus_fio_single_remote` starts one replica node and one nexus node. It creates a filler thick replica, an overcommitted thin replica, shares the thin replica, creates a one-child nexus, runs an OK FIO job, then runs an oversized FIO job and expects an `Other` I/O error containing `SPDK FIO error:`. `nexus_fio_mixed` adds a second node with an overcommitted thin replica but no filler, builds a two-child nexus, and expects both the small and larger FIO workloads to succeed because at least one mirror child can absorb the write.

State and persistence behavior: no persistent store is configured. State under test is pool space accounting, replica thin allocation, child fault/degraded behavior after ENOSPC, and nexus-level write success when redundancy remains viable.

Integration points: multi-container compose, NVMf shared replicas, the common FIO wrapper, and io-engine pool/replica/nexus gRPC builders.

Risks: capacity constants rely on metadata overhead remaining stable; a future pool allocator change could shift the exact ENOSPC threshold. Tests check FIO result text and generic error kind rather than a typed ENOSPC error.

Test signals: OK FIO under safe data size, expected FIO error when one thin replica exhausts backing space, and successful mirrored FIO when another child remains healthy.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_fio.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_io.rs -->
# sources/control-plane/mayastor/io-engine/tests/nexus_io.rs

Purpose: broad nexus I/O test suite covering NVMf multipath and ANA, NVMe reservations and preemption, write-zeroes correctness, subsystem pause/unshare/share races, and frozen nexus behavior after child failures or ENOSPC.

Important APIs and types: `nexus_create`, `nexus_create_v2`, `nexus_lookup`, `nexus_lookup_mut`, `nexus_destroy`, `NexusNvmeParams`, `NexusPauseState`, `NvmeAnaState`, `NvmeReservation`, `NexusNvmePreemption`, `NexusStatus`, `ChildState`, `FaultReason`, `Lvs`, `PoolArgs`, v0 gRPC pool/replica/nexus requests, `MayastorTest`, NVMe CLI helpers, `NmveConnectGuard`, and `reactor_poll!`.

Control flow: `nexus_io_multipath` creates the same nexus identity on a local in-process Mayastor and a remote container, connects to both paths, changes ANA state, checks `nvme list-subsys`, disconnects both controllers, and verifies replica reservation registration. `nexus_io_resv_acquire` creates a local nexus with a configured reservation key, then a remote nexus over the same replica, and validates reservation report entries. `nexus_io_resv_preempt` creates an exclusive-access reservation, then a second preempting nexus; subsequent local I/O fails, the first nexus transitions to `Shutdown`, children fault with no device or I/O handle, and PTPL reservation survives remote restart. `nexus_io_resv_preempt_tabled` iterates reservation types, keys, and local/remote creation paths.

State and persistence behavior: PTPL directories hold reservation state for preemption tests. In-process nexus state transitions include shared, paused, unpaused, frozen, shutdown, and destroyed. Freeze tests confirm that a faulted frozen nexus rejects add/online operations, remains frozen through unshare, and distinguishes ENOSPC faulting from subsystem freeze.

Integration points: kernel `nvme` command output, libnvme reservation report parsing, NVMf target, local LVS pools, compose containers, in-process Mayastor reactors, crossbeam channels, and asynchronous reactor polling.

Risks: several tests rely on Linux NVMe tooling and host kernel behavior; `nexus_io_multipath` is ignored. Race tests intentionally exercise unstable ordering, so they may expose timing-dependent behavior. The file mixes v0 RPC and direct in-process APIs, increasing setup complexity.

Test signals: reservation report fields (`rtype`, `regctl`, `ptpls`, `rcsts`, `rkey`, `hostid`), ANA state string, write/read data patterns, write-zeroes returning zeros from both replicas, expected `Shutdown` and child handle cleanup after preemption, pause/freeze state assertions, and rejection of operations while frozen.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_io.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_rebuild.rs -->
# sources/control-plane/mayastor/io-engine/tests/nexus_rebuild.rs

Purpose: validates low-level and nexus-level rebuild behavior, including rebuild job lookup, source tracking, pausing, parallel source use, raw bdev rebuild transfer counts, partial bitmap transfer counts, and mixed cluster-size rebuilds.

Important APIs and types: `device_create`, `device_destroy`, `device_open`, `nexus_lookup_mut`, `BdevRebuildJob`, `NexusRebuildJob`, `RebuildState`, `SegmentMap`, `MayastorTest`, `Mthread`, `Protocol::Off`, `PoolBuilder`, `ReplicaBuilder`, `NexusBuilder`, and `wait_for_rebuild`.

Control flow: helpers create temporary aio-backed disks, derive `aio://` or injected error URIs, create a nexus, optionally fill it with random data via host-side `dd`, share it as a local device, and compare the first child. `rebuild_replica` creates a six-child nexus, adds a seventh child, starts rebuild, asserts no source lookup exists before start, verifies the chosen source has exactly one job, pauses it, adds another child, starts a second rebuild, then validates rebuilt data with MD5 and checks history. `rebuild_bdev` directly rebuilds one malloc bdev to another and asserts `blocks_transferred`. `rebuild_bdev_partial` builds several `SegmentMap` bitmaps and asserts the job transfers exactly dirty blocks. `rebuild_across_mixed_cluster_sizes` creates replicas on pools with 4 MiB and 32 MiB cluster sizes and verifies adding a thin remote child reaches `Online`.

State and persistence behavior: no etcd. State is rebuild job registry, rebuild history, child membership, source lookup map, and segment dirty bitmap. The tests explicitly remove added children and destroy the nexus to clean local SPDK state.

Integration points: SPDK bdev creation/open, local files under `/tmp`, io-engine rebuild modules, compose RPC builders, DMA buffers, and MD5 validation.

Risks: uses `static mut` for error-device indexes and global nexus name protected by a mutex; parallel test execution could still be fragile. Data validation skips metadata offset manually, so layout assumptions matter. `NexusRebuildJob::lookup_src` assertions encode implementation details.

Test signals: rebuild job lookup presence/absence, source job count, `RebuildState::Completed`, exact transferred block counts, MD5 equality between source and rebuilt child, non-empty rebuild history, and online state after mixed-cluster rebuild.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_rebuild.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_rebuild_parallel.rs -->
# sources/control-plane/mayastor/io-engine/tests/nexus_rebuild_parallel.rs

Purpose: stress-tests many concurrent rebuilds by creating 20 three-node volumes, initially omitting one replica from each nexus, then adding that replica to all volumes and waiting for every rebuild to complete.

Important APIs and types: `Volume { replicas, nex }`, `PoolBuilder`, `ReplicaBuilder`, `NexusBuilder`, `GrpcConnect`, `ChildState`, `Status`, and tonic `Code`.

Control flow: the test creates three large `/tmp/disk_<r>` backing files, starts three io-engine containers with bound `/tmp`, creates one pool per node, then loops 20 times creating three thick replicas per volume. Each nexus initially uses replicas 1 and 2 on node 2. After setup, it adds replica 0 to every nexus with rebuild enabled and calls `monitor_volumes`.

State and persistence behavior: no persistent store. The core state is per-volume child state: `Online`, `Degraded` with `rebuild_progress`, `Faulted`, or `Unknown`. The monitor detects any `Faulted` child as test failure and returns once all volumes have no degraded/unknown children.

Integration points: compose containers, aio bdev files, remote NVMf replica shares, gRPC builders, and timed polling over many nexus objects.

Risks: fixed 30 second timeout may be tight on slow hosts because all 20 rebuilds run in parallel. The test prints states for visibility but does not validate data contents after rebuild. Disk cleanup occurs only after monitor success.

Test signals: no child reaches `Faulted`, progress eventually leaves `Degraded`, all volume children reach `Online`, and timeout returns `Code::Cancelled` if rebuilds stall.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_rebuild_parallel.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_rebuild_partial.rs -->
# sources/control-plane/mayastor/io-engine/tests/nexus_rebuild_partial.rs

Purpose: validates partial rebuild logging and fallback behavior when children are offlined, faulted by I/O, or faulted during a rebuild. It checks exact transferred segment counts and data equality after recovery.

Important APIs and types: `NexusBuilder`, `ReplicaBuilder`, `PoolBuilder`, `validate_replicas`, `test_write_to_nexus`, `ChildState`, `ChildStateReason`, `RebuildJobState`, `InjectionBuilder`, `FaultDomain::NexusChild`, `FaultIoStage::Completion`, FIO builders, and `DataSize`.

Control flow: `create_compose_test` starts one nexus node and two source nodes; `create_test_storage` creates two thick shared replicas and a two-child published nexus. `nexus_partial_rebuild_io_fault` injects a write-completion failure after segment 7, writes a set of chunk patterns spanning selected rebuild segments, observes child fault with `IoFailure` and `has_io_log`, removes injection, onlines the child, validates replicas, and asserts a single partial history entry with 12 segments transferred. `nexus_partial_rebuild_offline_online` offlines a child, writes ranges that round to three segments, onlines, validates history, then repeats with a second partial rebuild. `nexus_partial_rebuild_double_fault` offlines a child, starts partial rebuild and concurrent FIO through an injected write failure, then expects a failed partial rebuild followed by a full rebuild and then a successful partial rebuild.

State and persistence behavior: state is in the nexus child I/O log, rebuild history, child degraded/faulted reasons, and dirty segment map. The double-fault test verifies that a failed partial rebuild without a usable log forces the next recovery to be full.

Integration points: fault injection, FIO, NVMf replicas, data validators, and rebuild history RPCs.

Risks: exact block counts depend on segment size and metadata start/end blocks. The double-fault path accepts either `IoFailure` or `RebuildFailed`, acknowledging race order. Fault-injection-only tests are gated and will not run in default feature sets.

Test signals: child state/reason, `has_io_log`, exact `blocks_transferred`, `is_partial` flags, `RebuildJobState` sequence, data equality via `validate_replicas`, and successful child re-online.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_rebuild_partial.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_rebuild_partial_loop.rs -->
# sources/control-plane/mayastor/io-engine/tests/nexus_rebuild_partial_loop.rs

Purpose: extended soak test that runs long verified random read/write FIO against a three-replica nexus while alternately restarting two replica nodes and forcing partial rebuilds back to online.

Important APIs and types: `Node`, `ComposeTest`, `SharedRpcHandle`, `PoolBuilder`, `ReplicaBuilder`, `NexusBuilder`, `find_nexus_by_uuid`, `FioBuilder`, `FioJobBuilder`, `oneshot`, `Mutex`, `ChildState`, `Status`, and `Code`.

Control flow: gated by `extended-tests`. The test creates three 8 GiB replicas on aio-backed pools, builds a three-child nexus on node 2, publishes it, and starts a FIO task using crc32 verify and e2e-like parameters. In parallel, a restart loop checks whether FIO has completed; while it has not, it sleeps, restarts node 0 and node 1 in turn, recreates their pools/shares via `Node::restart`, onlines the restarted replica into the nexus, and waits with `monitor_nexus` until every child reports `Online`.

State and persistence behavior: no etcd. Restart recovery depends on the saved pool and replica builder configuration being reusable after container restart. The nexus child states move through degraded/rebuilding/online repeatedly while verified I/O is active.

Integration points: compose restart support, aio files under `/tmp`, NVMf published nexus, FIO verification, and rebuild progress polling. `Drop` for `Node` deletes its backing file.

Risks: designed to run for about an hour or more; timing and disk performance heavily affect reliability. Since it polls every 100 ms for up to 120 seconds per online operation, slow rebuilds can fail despite eventual correctness. Extended feature gate likely keeps it out of normal CI.

Test signals: FIO returns success with crc32 verification, every restarted child returns to `Online`, monitor output shows progress rather than fault, and no timeout/status error is returned.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_rebuild_partial_loop.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_rebuild_source.rs -->
# sources/control-plane/mayastor/io-engine/tests/nexus_rebuild_source.rs

Purpose: verifies rebuild source selection prefers local healthy replicas on the nexus node when available, otherwise falls back to the first available non-destination child.

Important APIs and types: `TestNode`, `SharedRpcHandle`, `PoolBuilder`, `ReplicaBuilder`, `NexusBuilder`, `ChildState`, `ChildStateReason`, and rebuild history records returned by `get_rebuild_history`.

Control flow: the test starts three io-engine nodes, creates one pool per node, and builds reusable `TestNode` structures. `test_src_selection` creates replicas according to a vector of node indexes, creates a nexus on a specified node, offlines the destination child, waits for `Degraded/ByClient`, onlines it, waits for all children online, then reads the first rebuild history record and maps recorded source/destination URIs back to child indexes. The main test runs a table covering all-local, local/remote mixes, remote/local/remote, remote/remote/local, two locals, and all-remote cases.

State and persistence behavior: no persistent store. The meaningful state is child URI ordering and the rebuild history `src_uri`/`child_uri`. After each scenario the nexus is destroyed and every node clears its replicas to avoid cross-case contamination.

Integration points: gRPC builder APIs, remote replica sharing, child online/offline operations, and rebuild history RPC.

Risks: source selection is implementation-specific and may need updating if selection policy changes from first/local preference to load-aware selection. One-second timeouts are short but the replicas are small.

Test signals: exact source child index equals expected table value for every topology, destination child returns to online, and cleanup succeeds after each scenario.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_rebuild_source.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_rebuild_verify.rs -->
# sources/control-plane/mayastor/io-engine/tests/nexus_rebuild_verify.rs

Purpose: verifies rebuild verification failure handling by injecting data corruption/miscompare into a rebuilding child and expecting the rebuild to fail and the child to fault with `RebuildFailed`.

Important APIs and types: `NexusBuilder`, `ReplicaBuilder`, `PoolBuilder`, `SharedRpcHandle`, `ChildState`, `ChildStateReason`, `RebuildJobState`, `InjectionBuilder`, `FaultDomain::BlockDevice`, `FaultMethod::Data`, and `NEXUS_REBUILD_VERIFY=fail`.

Control flow: `test_rebuild_verify` creates and publishes a two-child nexus, records the first child device name, offlines that replica, adds a block-device write-submission data fault at offset 10240, onlines the child, waits until it is `Faulted` with `RebuildFailed`, and asserts the rebuild history has one failed record. `nexus_rebuild_verify_remote` uses two remote replica nodes plus a nexus node; `nexus_rebuild_verify_local` uses one local replica on the nexus node and one remote replica.

State and persistence behavior: no persistent store. The file explicitly disables partial rebuild with `NEXUS_PARTIAL_REBUILD=0` so the test forces rebuild I/O and verification. Rebuild history records the failed job.

Integration points: fault injection, rebuild verification environment variables, local and remote replica topology, and gRPC child state polling.

Risks: feature gated by `fault-injection`; failures depend on injected offset being exercised during full rebuild. Environment variable comment misspells "verify" but actual variable is correct.

Test signals: child reaches `Faulted/RebuildFailed` within five seconds and rebuild history contains exactly one `Failed` job.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_rebuild_verify.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_replica_resize.rs -->
# sources/control-plane/mayastor/io-engine/tests/nexus_replica_resize.rs

Purpose: tests multi-replica nexus expansion under several conditions: attempting to resize before all replicas expand, resizing after all replicas expand, resizing while a replica is rebuilding, and resizing around nexus snapshots with I/O running.

Important APIs and types: `ResizeTest`, `ResizeTestTrait`, `StorConfig`, `PoolBuilder`, `ReplicaBuilder`, `NexusBuilder`, `NexusState`, `SnapshotParams`, `NexusCreateSnapshotReplicaDescriptor`, `FioBuilder`, `FioJobBuilder`, `JoinHandle<Fio>`, and `OnceCell<PathBuf>` for the connected NVMf path.

Control flow: `compose_ms_nodes` starts a nexus node and two replica nodes. `setup_cluster_and_run` creates three 200 MiB replicas, builds and publishes a three-child nexus, opens it over NVMf, starts a 20 second randrw FIO, waits two seconds, then dispatches the selected `ResizeTest`. `do_resize_without_replica_resize` asserts nexus resize fails if zero or only one replica is expanded. `do_resize_after_replica_resize` expands all replicas then the nexus and checks the exact expanded size. `do_resize_with_rebuilding_replica` removes and re-adds the last child to start rebuild before resizing. `do_resize_after_snapshot` creates a snapshot before expansion, expands the volume, waits for FIO, creates a second snapshot, and runs post-resize I/O.

State and persistence behavior: snapshots carry UUID/name/timestamp metadata through `SnapshotParams`; no external persistent store is configured. Resize state is visible in replica returned sizes and nexus size/state. The rebuilding case asserts `NexusDegraded` before attempting resize.

Integration points: compose, NVMf, FIO, snapshot creation RPCs, replica resize RPCs, and nexus resize RPCs.

Risks: `NEXUS_CONNECT_PATH` is a global `OnceCell`, so concurrent test execution could reuse the first path. Resizing while FIO runs is timing-sensitive. The snapshot test uses generated descriptors and assumes all replicas support snapshot creation.

Test signals: expected resize errors before all replicas expand, returned replica sizes at least expanded size, nexus size exactly `EXPANDED_SIZE`, degraded state during rebuild resize, successful snapshot creation before and after expansion, and successful post-resize FIO.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_replica_resize.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_restart.rs -->
# sources/control-plane/mayastor/io-engine/tests/nexus_restart.rs

Purpose: validates that a published nexus can be recreated after its io-engine process is killed and restarted while host I/O is running, then rebuilt back to three replicas without FIO verification failure.

Important APIs and types: `TestCluster`, `StorageNode`, `NodeConfig`, `NexusBuilder`, `PoolBuilder`, `ReplicaBuilder`, `NvmfLocation`, `NmveConnectGuard`, `FioBuilder`, `FioJobBuilder`, watch `Sender`/`Receiver`, and etcd client startup configuration.

Control flow: `TestCluster::create` creates backing files, starts etcd plus three io-engine containers, gives only node 2 a persistent-store endpoint, and creates one pool/replica per node. `nexus_restart` creates and publishes a three-child nexus, then runs two tasks. `run_io_task` connects to the nexus, signals readiness, runs randwrite FIO with crc32 metadata, then randread verify FIO. `run_manage_task` waits for the signal, sleeps, kills node 2, waits, starts it, recreates the nexus with one child, recreates one pool, adds the second and third children with rebuild, then republishes.

State and persistence behavior: uses etcd for the nexus node, but the management path explicitly recreates the nexus rather than relying only on import. The test exercises external initiator I/O continuity across NVMf target disappearance and later re-publication. Child rebuild state is implied by add-child calls.

Integration points: etcd container, compose kill/start, direct file binds, NVMf host connection, FIO verification, persistent-store command-line option, and gRPC builders.

Risks: timing constants (`SLEEP_BEFORE`, `SLEEP_DOWN`, `SLEEP_ADD_CHILD`) are fixed and could be host-dependent. The I/O task unwraps FIO errors, so failures provide strong signal but little structured diagnosis.

Test signals: write FIO succeeds, verify FIO succeeds after restart/rebuild, nexus recreate/add/publish calls succeed, and no task panics during concurrent restart management.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_restart.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_share.rs -->
# sources/control-plane/mayastor/io-engine/tests/nexus_share.rs

Purpose: tests local in-process nexus sharing semantics, especially idempotent NVMf sharing for a nexus and rejection of direct NVMf sharing through the generic bdev path.

Important APIs and types: `nexus_create`, `nexus_lookup_mut`, `MayastorTest`, `MayastorCliArgs`, `Reactor::block_on`, `Share`, `Protocol`, `UntypedBdev`, and `mayastor_env_stop`.

Control flow: the test starts an in-process Mayastor with two reactors. It creates a two-child malloc-backed nexus, shares it over NVMf twice through the nexus-specific `share_nvmf` path and asserts both URIs match and `nexus.shared()` is `Nvmf`. It then looks up the same bdev through `UntypedBdev` and asserts generic `share_nvmf` errors. Finally it unshares the nexus, checks both nexus and bdev report `Protocol::Off`, destroys the nexus, and stops the environment.

State and persistence behavior: all state is local SPDK/nexus share state. No external persistence. The test checks that the nexus abstraction and underlying bdev share status remain synchronized after unshare.

Integration points: in-process SPDK environment, reactor blocking, nexus and untyped bdev APIs.

Risks: direct sharing behavior is policy-sensitive; if generic bdev sharing becomes supported for nexus bdevs, the assertion should change. The test must stop the environment to avoid leaking reactors into later tests.

Test signals: same share URI for repeated nexus share, generic bdev share error, `Protocol::Off` after unshare, and clean destroy/stop.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_share.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_thin.rs -->
# sources/control-plane/mayastor/io-engine/tests/nexus_thin.rs

Purpose: validates nexus creation rules for thin-provisioned replicas and pool committed-space accounting.

Important APIs and types: `ThinTest`, `ComposeTest`, `SharedRpcHandle`, `PoolBuilder`, `ReplicaBuilder`, `NexusBuilder`, and tonic error codes.

Control flow: `ThinTest::new` starts one io-engine container, creates one pool, and creates two 50 MiB thin replicas, one 50 MiB thick replica, and one 30 MiB thick replica. `nexus_thin_create_1` attempts to create a 50 MiB nexus with a 50 MiB thin replica and a 30 MiB thick/bad-size replica, expecting an internal error. `nexus_thin_create_2` creates a 50 MiB nexus from two thin replicas and then sums all pool replica sizes to compare with the pool's committed accounting.

State and persistence behavior: no persistent store. The tested state is replica thin flag, size compatibility, nexus child compatibility, and pool committed bytes after replica creation.

Integration points: compose, v1 gRPC builder wrappers, and pool usage reporting.

Risks: the file comments mention mixing thin and thick replicas, but the first negative test combines thin with a bad-size thick replica, so the exact failure reason could be size rather than provisioning type. The unused thick same-size replica is prepared but not used by assertions.

Test signals: failed create returns `tonic::Code::Internal`; valid two-thin nexus creation succeeds; pool `committed` equals sum of replica sizes.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_thin.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_thin_no_space.rs -->
# sources/control-plane/mayastor/io-engine/tests/nexus_thin_no_space.rs

Purpose: verifies ENOSPC behavior for thin-provisioned nexus children in local and remote topologies, including recovery after freeing pool space and onlining a degraded child.

Important APIs and types: `PoolBuilder`, `ReplicaBuilder`, `NexusBuilder`, `DataSize`, `test_write_to_nexus`, `find_nexus_by_uuid`, `ChildState`, and `ChildStateReason`.

Control flow: `nexus_thin_nospc_local_single` creates a local thin replica and one-child nexus, writes 30 MiB successfully, then writes 80 MiB and expects raw `ENOSPC`. `nexus_thin_nospc_remote_single` repeats with a remote shared replica and separate nexus node. `nexus_thin_nospc_local` creates two local pools, fills one pool with a thick replica, creates two thin replicas, builds a two-child nexus, and calls `test_recover_from_enospc`. `nexus_thin_nospc_remote` repeats across two replica nodes and one nexus node. `test_recover_from_enospc` writes more data than the first pool has free, asserts the first child is `Degraded/NoSpace`, destroys the filler replica, onlines the child, and expects `Degraded/OutOfSync` indicating rebuild started.

State and persistence behavior: no etcd. Important state is pool allocation, child no-space degradation, freeing space through replica destruction, and transition from no-space to out-of-sync rebuild state.

Integration points: local and remote replica sharing, nexus NVMf publish, gRPC state reads, Linux `libc::ENOSPC`.

Risks: capacity thresholds depend on metadata overhead. The recovery helper checks that rebuild starts but does not wait for online completion or validate data equality.

Test signals: direct ENOSPC errno for single-child nexus, child `Degraded/NoSpace` for mirrored nexus, and child `Degraded/OutOfSync` after online once space is freed.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_thin_no_space.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_thin_rebuild.rs -->
# sources/control-plane/mayastor/io-engine/tests/nexus_thin_rebuild.rs

Purpose: ensures rebuilding into a new thin-provisioned replica preserves thin usage semantics and data consistency across local-to-local, local-to-remote, remote-to-local, and remote-to-remote topologies.

Important APIs and types: `StorConfig`, `PoolBuilder`, `ReplicaBuilder`, `NexusBuilder`, `DataSize`, `test_write_to_nexus`, `validate_pools_used_space`, and `validate_replicas`.

Control flow: `test_thin_rebuild` creates three thin replicas on configurable source and destination handles, creates a nexus from two source replicas, writes 14 MiB, adds the destination replica with rebuild enabled, waits for all children online, then validates pool used-space accounting and replica data equality. Four tests vary where the nexus/source/destination handles are placed: remote-to-local, remote-to-remote, local-to-remote, and local-to-local.

State and persistence behavior: no persistent store. State under test is thin allocation on all pools after rebuild, child online state, and byte-for-byte replica equality after rebuilding only written data onto a thin target.

Integration points: compose multi-node topology, remote NVMf sharing, builder APIs, data validation helpers, and pool usage validators.

Risks: used-space validation likely assumes known cluster allocation behavior; future metadata or allocation changes could require relaxed checks. The helper waits only ten seconds for rebuild completion.

Test signals: successful add-replica/rebuild to `Online`, pool used-space validation passes, and all three replicas validate as identical.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_thin_rebuild.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_with_local.rs -->
# sources/control-plane/mayastor/io-engine/tests/nexus_with_local.rs

Purpose: validates handling of a nexus that includes a local `bdev:///` child and a remote NVMf child, focusing on local bdev alias lifecycle through remove/add/destroy operations.

Important APIs and types: v1 `CreatePoolRequest`, `CreateReplicaRequest`, `CreateNexusRequest`, `AddChildNexusRequest`, `RemoveChildNexusRequest`, `DestroyBdevRequest`, `ListBdevOptions`, `RpcHandle`, and `NVME_NQN_PREFIX`.

Control flow: the test starts two io-engine containers. `create_replicas` creates a pool and shared replica on each node. It creates a nexus on node 1 with a local `bdev:///repl0` child and a remote `nvmf://...` child from node 2. `check_aliases` lists bdevs and checks whether any alias contains `bdev:///`. The test removes the local child and expects aliases gone, re-adds it and expects success, tries to add it again and expects an error, verifies alias presence, then destroys the local bdev URI.

State and persistence behavior: no persistent store. The state under test is bdev alias registration for local child devices, duplicate child detection, and alias cleanup on remove/destroy.

Integration points: v1 gRPC services for pool, replica, nexus, and bdev; NVMf URI construction; local bdev URI child handling.

Risks: alias checks are broad (`contains("bdev:///")`) rather than tied to a specific bdev, so unrelated aliases could cause false positives if more bdevs exist. The test uses fixed UUIDs and names but runs in clean containers.

Test signals: alias present after local child is in nexus, absent after remove, duplicate add fails, and bdev destroy succeeds.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_with_local.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nvme_device_timeout.rs -->
# sources/control-plane/mayastor/io-engine/tests/nvme_device_timeout.rs

Purpose: verifies NVMe bdev I/O timeout actions. One test expects an outstanding read against a paused NVMf target to complete with error after timeout/reset; the other expects `Ignore` to leave the I/O outstanding without invoking the completion callback.

Important APIs and types: `Config`, `NvmeBdevOpts`, `DeviceTimeoutAction`, `BlockDevice`, `BlockDeviceHandle`, `IoCompletionStatus`, `ReadOptions`, `DmaBuf`, `AsIoVecs`, `AtomicPtr`, `AtomicCell`, `OnceCell`, `device_create`, `device_open`, and `device_destroy`.

Control flow: `get_config` initializes short NVMe timeout/keepalive settings. `test_io_timeout` creates and shares a remote malloc bdev over NVMf, imports it locally, opens a handle, sets the timeout action, pauses the target container, submits an asynchronous `readv_blocks` with a raw context pointer, and waits up to two minutes for the callback to report non-success exactly once. `io_timeout_reset` invokes this path with `Reset`. `io_timeout_ignore` repeats setup but sets `Ignore`, submits the read, waits five timeout intervals, asserts the callback did not fire, then destroys the imported device.

State and persistence behavior: no persistent store. State is local NVMe controller timeout policy, imported bdev lifetime, outstanding I/O callback flag, and target pause/thaw state. Raw pointers are used to keep handles and DMA buffers alive across async boundaries.

Integration points: compose pause, NVMf bdev share, local io-engine SPDK bdev import, NVMe transport options, DMA buffers, and C-style completion callbacks.

Risks: unsafe raw-pointer ownership is correct only if all destroy paths execute; panics before cleanup could leak. Timing depends on kernel/SPDK timeout behavior and container pause actually quiescing the target. `Ignore` intentionally leaves active I/O until device destroy.

Test signals: configured timeout action round-trips, callback receives correct device name/context string, reset mode callback fires with non-success, ignore mode callback remains false, and imported device destruction succeeds.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nvme_device_timeout.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nvmf.rs -->
# sources/control-plane/mayastor/io-engine/tests/nvmf.rs

Purpose: validates NVMf target subsystem behavior, target interface selection, and ignored RDMA target publishing/connectivity.

Important APIs and types: `bdev_create`, `NvmfSubsystem`, `SubType`, `UntypedBdev`, `MayastorEnvironment`, `BdevShareRequest`, `BdevUri`, v1 pool/replica/nexus/publish requests, `ShareProtocolNexus`, `NetworkMode`, `Regex`, and host NVMe connect/disconnect helpers.

Control flow: `nvmf_target` starts an in-process environment, creates an aio bdev, creates and starts an NVMf subsystem, verifies duplicate subsystem creation fails, counts subsystems including discovery, checks bdev claim ownership by `NVMe-oF Target`, stops non-discovery subsystem, performs unsafe shutdown, and confirms claim release. `nvmf_set_target_interface` starts containers with different `-T` selectors (`name:lo` and subnet selectors), shares a malloc bdev, parses the NVMf URI, and asserts the advertised target IP matches expected interface/subnet. `test_rdma_target` is ignored; it sets up an rxe RDMA device, starts privileged host-network io-engine with `--enable-rdma`, creates a pool/replica/nexus, publishes the nexus, checks URI scheme `nvmf+rdma+tcp`, connects with NVMe RDMA, disconnects, tears down containers, and deletes the rxe device.

State and persistence behavior: no persistent store. State includes NVMf subsystem registry, bdev claimed/unclaimed state, target address selection, and published nexus URI scheme.

Integration points: SPDK NVMf target, Linux network interface/subnet selection, Docker host networking for RDMA, NVMe CLI, regex parsing, and v0/v1 gRPC APIs.

Risks: RDMA test requires host privileges and is ignored. Interface selection tests assume Docker network naming and IP assignment. Unsafe subsystem shutdown is deliberate but must remain scoped.

Test signals: duplicate subsystem creation errors, subsystem count, bdev claim owner string, shared URI IP matches selected interface, RDMA URI scheme and host NVMe connection success.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nvmf.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nvmf_connect.rs -->
# sources/control-plane/mayastor/io-engine/tests/nvmf_connect.rs

Purpose: exercises concurrent nonblocking NVMf qpair connection creation, and races between qpair connection attempts and device destruction.

Important APIs and types: `MayastorTest`, `Lvs`, `LvsLvol`, `PoolArgs`, `Share`, `device_create`, `device_lookup`, `device_destroy`, `CoreError`, `BdevError`, `OnceCell`, and `Pin`.

Control flow: `init_nvmf_share` creates an in-process LVS pool on a malloc bdev, creates an lvol replica, shares it over NVMf, and returns its share URI. `nvmf_connect_async` loops 20 times: imports the NVMf URI, starts three concurrent `get_io_handle_nonblock` futures against the same device, requires all to succeed, then destroys the device. `nvmf_connect_async_drop` loops 20 times doing the same three handle futures plus concurrent device destroy, expecting handle acquisition errors and destroy success. `deinit_nvmf_share` destroys the pool afterward.

State and persistence behavior: no external persistence. State is local imported NVMf device, shared lvol lifetime, and qpair connection future state. The drop test ensures destruction resolves outstanding connection attempts rather than hanging or succeeding with stale handles.

Integration points: in-process LVS, NVMf target share, SPDK async qpair connection path, and device import/destroy APIs.

Risks: the two cfg branches in `nvmf_connect_async_drop` currently assert errors in both feature and non-feature cases, so the conditional is redundant. Timing-sensitive races may differ if SPDK connection behavior changes.

Test signals: all three nonblocking handle acquisitions succeed without destruction; all three fail when destruction races them; device destroy returns OK in every loop; pool cleanup succeeds.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nvmf_connect.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/persistence.rs -->
# sources/control-plane/mayastor/io-engine/tests/persistence.rs

Purpose: validates nexus persistent-store behavior in etcd: clean shutdown tracking, child health updates after I/O failure, add/rebuild/remove child persistence, behavior during persistent-store outage, and the transaction helper API.

Important APIs and types: v0 `CreateNexusRequest`, `DestroyNexusRequest`, `AddChildNexusRequest`, `RemoveChildNexusRequest`, `PublishNexusRequest`, `RebuildStateRequest`, `Nexus`, `Child`, `NexusInfo`, `ChildInfo`, `PersistentStore`, `PersistentStoreBuilder`, `Client`, `MayastorTest`, and `Url`.

Control flow: `start_infrastructure` starts etcd and four io-engine containers with `-p <etcd endpoint>`. `persist_unexpected_restart` creates two NVMf children and a nexus, reads etcd JSON directly, checks `clean_shutdown=false` and healthy children, restarts the nexus container, then expects `clean_shutdown=true`. `persist_clean_shutdown` does the same but destroys the nexus cleanly and checks persisted clean shutdown. `persist_io_failure` publishes a nexus, unshares one child, pauses etcd to force save retries, runs FIO through the nexus, verifies runtime degraded/faulted states, checks etcd child health, adds a third child, observes unhealthy while rebuilding, waits for rebuild completion, verifies healthy, removes it, and confirms it disappears from persisted info. `persistent_store_connection` pauses etcd before create, expects a timeout, thaws etcd, and later sees the nexus created. `pstor_txn_api` starts etcd, connects `PersistentStore`, and validates compare-and-set transaction success.

State and persistence behavior: this is the primary persistence test file. It directly inspects etcd values by nexus UUID, deserializes `NexusInfo`, and checks `clean_shutdown`, child UUID health, and child removal. Helper `uuid` extracts child UUIDs from URI query parameters.

Integration points: etcd binary/container, mayastor persistent-store client, libnvme target connect, FIO verifier, v0 gRPC services, and persistent-store transaction API.

Risks: tests use fixed port `2379` and endpoint constants; parallel runs can collide. Some timeout behavior is intentionally asynchronous: a timed-out create may later complete after etcd thaw. Direct JSON shape assumptions couple tests to `NexusInfo`.

Test signals: exact persisted booleans and child health, runtime `NexusDegraded`/child states, successful rebuild state polling, absent removed child in persisted entry, expected timeout while etcd paused, later nexus visibility, and successful transaction response.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/persistence.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/poller.rs -->
# sources/control-plane/mayastor/io-engine/tests/poller.rs

Purpose: tests SPDK poller lifecycle behavior: drop-before-poll, repeated polling, pause/resume/stop, mutable callback state, and running a poller on a non-master core.

Important APIs and types: `PollerBuilder`, `Reactors`, `MayastorEnvironment`, `MayastorCliArgs`, `Cores`, `AtomicCell`, and `parking_lot::Mutex`.

Control flow: the test initializes a two-core Mayastor environment. It builds and immediately drops a poller, polls once, and confirms the callback did not run. It builds another poller, polls the master 64 times, checks count 64, pauses and confirms no increment, resumes and checks count 128, then stops and confirms no further increment. It then builds a poller with captured mutable local state to show callback state persists across polls. Finally it creates a data-bearing poller on core 1, sleeps briefly to let it run, checks its counter is nonzero and that callback saw `Cores::current() == 1`, stops it, and stops the environment.

State and persistence behavior: no persistence. State under test is poller registration/liveness, pause flag, per-poller callback data, and core affinity.

Integration points: SPDK poller API via `spdk_rs`, io-engine reactor abstraction, cross-thread reactor polling, and core affinity.

Risks: the non-master poller relies on a short sleep; very slow or overloaded environments might not increment before the assertion. The global `COUNT` is shared across the test.

Test signals: exact callback count after poll batches, unchanged count after pause/stop, mutable local state does not panic, core-1 poller counter increments, and clean environment stop.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/poller.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/reactor.rs -->
# sources/control-plane/mayastor/io-engine/tests/reactor.rs

Purpose: validates reactor startup/shutdown state, CPU pinning, and unaffinitized thread placement relative to io-engine reactor cores.

Important APIs and types: `MayastorEnvironment`, `MayastorCliArgs`, `Reactors`, `ReactorState`, `Cores`, `Mthread`, `mayastor_env_stop`, and `AtomicUsize`.

Control flow: `reactor_start_stop` starts a two-core environment. It asserts every reactor is either `Delayed` or `Running`, sends a future to each reactor that checks `Cores::current()` equals `sched_getcpu`, and decrements a global wait counter while the master polls until all complete. It then spawns one unaffinitized OS thread per core via `Mthread::spawn_unaffinitized`, each sleeping and asserting its CPU is greater than the last reactor core id. After a delay it stops the Mayastor environment and joins all threads.

State and persistence behavior: no persistence. State is reactor state machine, core identity, and thread affinity behavior.

Integration points: SPDK reactor environment, Linux `sched_getcpu`, io-engine Mthread helper, and reactor future scheduling.

Risks: requires at least two CPUs and assumes unaffinitized threads run outside the reactor CPU mask. Uses a `static mut Lazy<AtomicUsize>` pattern, which is awkward but scoped to test.

Test signals: reactor state matches allowed values, each reactor future runs on expected CPU, wait counter reaches zero, unaffinitized threads avoid reactor cores, and shutdown/join completes.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/reactor.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/reactor_block_on.rs -->
# sources/control-plane/mayastor/io-engine/tests/reactor_block_on.rs

Purpose: regression test for nested `Reactor::block_on` behavior and scheduling a future from within a blocked reactor context.

Important APIs and types: `MayastorEnvironment`, `MayastorCliArgs`, `Reactor::block_on`, `Reactors::master().send_future`, `mayastor_env_stop`, and `AtomicCell`.

Control flow: the test initializes a default environment, enters `Reactor::block_on`, asserts a global counter is zero, sets it to one, schedules a future on the master that expects the counter to be two, then calls nested `Reactor::block_on` to assert one and set two. After leaving the outer block, it stops the environment and verifies the scheduled future observed the updated state by checking the counter is two.

State and persistence behavior: no persistence. State is the shared counter and reactor scheduling order between nested blocking and queued future execution.

Integration points: in-process SPDK environment and reactor executor.

Risks: minimal; if reactor scheduling order changes, this regression catches it. The global counter is shared but initialized once.

Test signals: nested block executes, scheduled future runs without deadlock, and final count is two after environment stop.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/reactor_block_on.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/reactor_interrupt.rs -->
# sources/control-plane/mayastor/io-engine/tests/reactor_interrupt.rs

Purpose: regression test ensuring `mayastor_env_stop` accepts a reactor in `Interrupt` state when interrupt mode is enabled, avoiding a previous shutdown panic.

Important APIs and types: `MayastorEnvironment`, `MayastorCliArgs`, `Reactors`, `ReactorState::Interrupt`, and `mayastor_env_stop`.

Control flow: the test initializes an environment with `reactor_mask=0x1` and `interrupt_mode=true`, explicitly drives the master reactor into interrupt mode using `enter_interrupt_mode`, asserts the state is `Interrupt`, then calls `mayastor_env_stop(0)`.

State and persistence behavior: no persistence. State under test is the reactor state machine during shutdown.

Integration points: SPDK environment interrupt mode and io-engine shutdown handling.

Risks: narrow regression; it does not validate real signal delivery, only the same state transition used by `.start()`.

Test signals: reactor state equals `Interrupt` and shutdown does not panic.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/reactor_interrupt.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/replica_crd.rs -->
# sources/control-plane/mayastor/io-engine/tests/replica_crd.rs

Purpose: validates that replica NVMf targets use the third CRD value for data transfer errors, and that a zero third CRD avoids long retry delay when an injected replica write fault is hit.

Important APIs and types: `PoolBuilder`, `ReplicaBuilder`, `InjectionBuilder`, `FaultDomain::BdevIo`, `FaultIoOperation::Write`, `FaultIoStage::Submission`, `FaultMethod::DATA_TRANSFER_ERROR`, `FioBuilder`, `FioJobBuilder`, `FioJobResult`, `Errno::EIO`, and `add_fault_injection`.

Control flow: gated by `fault-injection`. The test starts one io-engine with `--tgt-crdt 15,15,0`, creates a thin replica, shares it over NVMf, installs a bdev-I/O submission injection at offset 1000, opens the replica NVMf location, runs a direct libaio write FIO job, and inspects the result.

State and persistence behavior: no persistent store. State is the replica target's CRD configuration and fault injection registry. The replica remains shared while the injected fault maps to a host-visible I/O error.

Integration points: NVMf replica share, FIO, Linux errno, and fault injection.

Risks: Linux-specific errno and timing assertion. The test assumes the FIO write reaches the injected block range.

Test signals: FIO job result is `EIO`, and total runtime is less than the artificial delay that would apply if the wrong CRD slot were used.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/replica_crd.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/replica_snapshot.rs -->
# sources/control-plane/mayastor/io-engine/tests/replica_snapshot.rs

Purpose: ignored snapshot integration test for local and remote replicas behind a nexus, checking snapshot creation, sharing a snapshot over NVMf, data stability, and handling of unsupported custom NVMe admin commands.

Important APIs and types: `Lvs`, `PoolArgs`, `PoolBackend`, `SnapshotParams`, `UntypedBdevHandle`, `nexus_create`, v0 pool/replica/share RPCs, `MayastorTest`, `bdev_io`, `Uuid`, and `Utc`.

Control flow: the test creates a remote NVMf replica in a compose container and a local LVS lvol with the same UUID. In an in-process Mayastor it creates a two-child nexus, writes and reads data patterns, sends an unimplemented vendor admin opcode and expects an error, creates a snapshot through `UntypedBdevHandle::create_snapshot`, then confirms normal I/O still works. It shares the remote snapshot, creates a second nexus using snapshot child URIs produced by `format_snapshot_name`, writes new data to the original nexus, and verifies the snapshot nexus still reads the old data and zeros at an unwritten offset.

State and persistence behavior: snapshot state is local LVS snapshot metadata plus remote replica snapshot/share state. No etcd. Snapshot naming is timestamp-suffixed by helper and later reused for both local and NVMf children.

Integration points: local LVS, remote NVMf replica, nexus creation, snapshot RPC/handle API, NVMe admin passthrough, and data pattern helpers.

Risks: test is ignored and comments note snapshot read-only write enforcement is not yet enabled. It uses same UUID for local and remote children, so behavior is tightly tied to snapshot naming conventions.

Test signals: unsupported admin command errors, pre/post snapshot reads succeed, snapshot creation returns a timestamp, snapshot share succeeds, original writes do not alter snapshot reads, and unwritten snapshot region reads as zero.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/replica_snapshot.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/replica_thin.rs -->
# sources/control-plane/mayastor/io-engine/tests/replica_thin.rs

Purpose: validates replica-level thin provisioning usage metrics by comparing a thin and thick replica on the same pool before and after writing to the thin replica over NVMf.

Important APIs and types: `PoolBuilder`, `ReplicaBuilder`, `GrpcConnect`, `Binary`, `DataSize`, and `test_write_to_nvmf`.

Control flow: the test starts one io-engine container, creates a 200 MiB pool, creates a 40 MiB thin replica and a 40 MiB thick replica, shares both, and captures pool and replica usage. It asserts the thin replica has fewer allocated clusters/bytes than capacity and the thick replica has allocated clusters/bytes equal to capacity. It writes 30 MiB to the thin replica over NVMf, then fetches usage again and asserts the thin allocation and pool used bytes increased while remaining below total cluster/capacity.

State and persistence behavior: no persistent store. State is pool usage and replica usage metadata (`num_allocated_clusters`, `num_clusters`, `allocated_bytes`, `capacity_bytes`) before and after I/O.

Integration points: compose, NVMf write helper, pool usage reporting, and replica usage reporting.

Risks: cluster allocation expectations depend on allocator behavior and cluster size. It does not test freeing space or snapshot interactions.

Test signals: thin allocation initially below full capacity, thick allocation exactly full, thin allocation increases after write, pool used bytes increase, and thin allocation remains below capacity.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/replica_thin.rs -->
