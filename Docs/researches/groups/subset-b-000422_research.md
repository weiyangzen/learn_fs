# Research: subset-b-000422

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/publish/test_nexus_publish.py -->
# sources/control-plane/mayastor/test/python/tests/publish/test_nexus_publish.py

Purpose: legacy Mayastor gRPC tests for nexus lifecycle around create, publish, unpublish, and destroy with a mixed child set. It builds children from a local malloc bdev, a remotely shared NVMf bdev, and temporary aio/uring files, then repeats lifecycle flows for five deterministic UUIDs.

Important APIs and control flow: helpers convert sizes, deterministic UUIDs, child URIs, and publish protocol enums. Fixtures create `BaseBdev` devices through `bdev.Create`, share the remote child via `bdev.Share`, create temporary 64 MiB files with `sudo truncate`, track created nexuses, and clean them via `DestroyNexus`. Tests call `CreateNexus`, `PublishNexus`, `UnpublishNexus`, and `DestroyNexus`, asserting the final `ListNexus` count is zero.

State, dependencies, and integration: persistent state is temporary `/tmp/*-file.img` files and live Mayastor in-container bdev/nexus state. It depends on `common.mayastor` docker-compose fixtures, `mayastor_pb2`, sudo, and NVMf sharing between `ms0` and `ms1`.

Risks and test signals: cleanup is fixture-driven but a failing publish/destroy path may leave nexuses or temp files behind. Only `nvmf` is parameterized despite enum support for nbd/iscsi. The strongest signal is leak detection by `nexus_count() == 0` after all lifecycle variants.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/publish/test_nexus_publish.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/rebuild/docker-compose.yml -->
# sources/control-plane/mayastor/test/python/tests/rebuild/docker-compose.yml

Purpose: docker-compose environment for legacy rebuild tests. It launches one `rust:latest` Mayastor/io-engine container named `ms0` on static address `10.1.0.2` in `mayastor_net`.

Important configuration: the command runs `${SRCDIR}/${IO_ENGINE_DIR}/io-engine -g 0.0.0.0 -l ${MS0_CORES:-1,2} -r /tmp/ms0.sock`. Environment enables ANA and reservations, passes optional interrupt-mode and IOQ poll-period knobs, and exposes `RUST_LOG`. It mounts the source tree, `/nix`, hugepages, `/tmp`, and `/var/tmp`.

State, dependencies, and integration: tests use host `/tmp` files as aio children, so the `/tmp` mount is part of the persistence contract. SYS_ADMIN, SYS_NICE, IPC_LOCK, hugepages, and unconfined seccomp are required for io-engine and SPDK behavior. Static networking lets Python fixtures build gRPC handles from docker network metadata.

Risks and test signals: the file is single-node and therefore isolates rebuild behavior from network failures. Runtime correctness depends on environment variables resolving to a valid io-engine binary and host support for hugepages/capabilities. There are no direct assertions in the compose file; its signal is successful service readiness for rebuild feature tests.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/rebuild/docker-compose.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/rebuild/test_bdd_rebuild.py -->
# sources/control-plane/mayastor/test/python/tests/rebuild/test_bdd_rebuild.py

Purpose: legacy pytest-bdd coverage for nexus rebuild operations. It maps feature scenarios for running, stopping, pausing, resuming rebuilds and setting children online/offline.

Important APIs and control flow: helpers translate textual nexus, child, and action states into `mayastor_pb2` enums. `lookup_nexus`, `lookup_nexus_child`, and retrying `wait_child_state` poll observed state. Fixtures create two 64 MiB aio files, create a single-child nexus via `ms.CreateNexus`, then add a target child with `norebuild=True`. Step functions call `AddChildNexus`, `StartRebuild`, `PauseRebuild`, `ResumeRebuild`, `StopRebuild`, `GetRebuildStats`, `GetRebuildState`, and `ChildOperation`.

State, dependencies, and integration: state exists in host `/tmp/disk-rebuild-source.img` and target image, plus transient nexus child/rebuild state inside `ms0`. The file depends on pytest-bdd feature text, `retrying`, sudo file setup, `common.mayastor`, and legacy `mayastor_pb2`.

Risks and test signals: bare `except` in `rebuild_state` may hide unexpected gRPC failures. Offline waits retry only five times, making timing-sensitive regressions possible. Assertions cover nexus state, child state, rebuild count, explicit rebuild state, undefined state, and zero/non-zero rebuild stat counters.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/rebuild/test_bdd_rebuild.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/replica/docker-compose.yml -->
# sources/control-plane/mayastor/test/python/tests/replica/docker-compose.yml

Purpose: docker-compose fixture for legacy pool and replica BDD tests. It starts one `ms0` io-engine instance at `10.1.0.2`.

Important configuration: the service uses `${MS0_CORES:-1,2}`, static `mayastor_net`, ANA/reservation environment variables, optional interrupt mode, optional NVMe IOQ poll period, and `RUST_LOG`. It mounts the repo, `/nix`, hugepages, `/tmp`, and `/var/tmp`; capabilities and unconfined seccomp match SPDK/io-engine needs.

State and integration: pool tests create malloc or aio-backed pools, and replica tests create malloc-backed LVS pools. The shared `/tmp` mount enables aio image tests. Python fixtures locate `ms0` through docker-compose and create gRPC handles.

Risks and test signals: the single-node setup does not validate multi-node replica sharing, but it keeps pool/replica semantics deterministic. Any missing hugepages, permissions, or wrong `${IO_ENGINE_DIR}` will fail before test logic. The compose file itself has no assertions; readiness and gRPC connectivity are its effective signal.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/replica/docker-compose.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/replica/test_bdd_pool.py -->
# sources/control-plane/mayastor/test/python/tests/replica/test_bdd_pool.py

Purpose: legacy pytest-bdd pool management coverage for invalid block sizes, duplicate names, aio pools, multi-disk rejection, destruction, missing destruction, and listing.

Important APIs and control flow: fixtures create `/tmp/ms0-disk0.img`, find pools through `ms.ListPools(pb.Null())`, track created pools for cleanup, and wrap `ms.CreatePool`. Step functions create malloc or aio pools, expect `INVALID_ARGUMENT` for invalid block size and multiple disks, create duplicate pools, destroy pools, and list pools. Then steps assert creation failure/success, destruction success, and listing membership.

State, dependencies, and integration: state is a live pool in `ms0` and a temporary aio image. It depends on legacy `mayastor_pb2`, pytest-bdd feature files, `common.command.run_cmd`, and `common.mayastor` fixtures.

Risks and test signals: duplicate pool creation and missing pool destruction do not explicitly wrap expected gRPC errors in this file, so scenario behavior relies on pytest-bdd failing on unhandled exceptions. Cleanup iterates tracked pool names and can fail if a test deletes a pool without removing it from the dictionary. Strong signals are enum-specific invalid-argument checks and post-operation `find_pool`/list assertions.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/replica/test_bdd_pool.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/replica/test_bdd_replica.py -->
# sources/control-plane/mayastor/test/python/tests/replica/test_bdd_replica.py

Purpose: legacy pytest-bdd replica coverage for create/destroy/list/stats/share/unshare behavior on a single malloc-backed pool.

Important APIs and control flow: `share_protocol` maps BDD strings to legacy replica share enums. Module fixtures create pool `p0`, define fixed replica UUID and size, and expose `find_replica`, `current_replicas`, and `create_replica`. Steps create unshared or NVMf shared replicas, reject iSCSI sharing, recreate existing replicas, destroy replicas, list replicas, get stats, share with same/different protocols, and unshare by issuing `ShareReplica` with `REPLICA_NONE`.

State, dependencies, and integration: state is pool `p0`, a tracked dict of replicas, live replica bdevs, and share state inside Mayastor. It depends on `mayastor_pb2`, `grpc`, pytest-bdd feature files, and `common.mayastor`.

Risks and test signals: several then steps are no-op markers, and read/write scenarios are skipped with `NotImplementedError` bodies. Duplicate create and missing destroy rely on scenario-level failure behavior except where explicit invalid-argument checks exist. Signals include `find_replica`, list membership by UUID, stats UUID membership, and share enum equality.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/replica/test_bdd_replica.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/replica_uuid/docker-compose.yml -->
# sources/control-plane/mayastor/test/python/tests/replica_uuid/docker-compose.yml

Purpose: docker-compose environment for legacy replica UUID/name compatibility tests. It starts a single `ms0` io-engine service at `10.1.0.2`.

Important configuration: the service matches the standard single-node test stack with ANA/reservation env vars, optional interrupt mode, optional IOQ poll period, `RUST_LOG`, `ASAN_OPTIONS=detect_leaks=0`, static networking, source and `/tmp` mounts, hugepages, `/nix`, SYS_ADMIN/SYS_NICE/IPC_LOCK, and unconfined seccomp.

State and integration: replica UUID tests create a malloc pool and replicas via both old and v2 APIs. The compose file provides the gRPC endpoint and process state required by `common.mayastor` fixtures.

Risks and test signals: because it is single-node, it validates API compatibility and enumeration but not network share behavior. Environment misconfiguration surfaces as fixture startup failures rather than test assertions. Correctness is signaled by successful pool online state and replica enumeration in the Python test.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/replica_uuid/docker-compose.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/replica_uuid/test_replica_uuid.py -->
# sources/control-plane/mayastor/test/python/tests/replica_uuid/test_replica_uuid.py

Purpose: legacy/v2 compatibility tests for explicit replica names and UUIDs. It verifies replicas created with the newer API keep distinct name and UUID fields and that replicas created by the older API enumerate correctly through the newer listing API.

Important APIs and control flow: constants define pool, replica names, UUID, and size. A module fixture creates `pool0` with `pool_create` and destroys it best-effort. Steps create a v2 replica via `replica_create_v2(pool, name, uuid, size)`, inspect bdevs for name/UUID/size, enumerate with `replica_list_v2`, and create an old API replica with `replica_create(pool, name, size)`.

State, dependencies, and integration: state includes a malloc pool, replica bdev metadata, and v2 replica list responses. It depends on `common.mayastor` helper methods that are not defined in this file, pytest-bdd, and legacy `mayastor_pb2`.

Risks and test signals: the old API test asserts the returned old replica UUID equals the requested name but later asserts v2 enumeration UUID differs from name, making this an explicit compatibility contract. Cleanup only destroys the pool, relying on pool teardown to remove replicas. Assertions cover bdev metadata, enumeration fields, size, and pool name.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/replica_uuid/test_replica_uuid.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/rpc/docker-compose.yml -->
# sources/control-plane/mayastor/test/python/tests/rpc/docker-compose.yml

Purpose: docker-compose fixture for RPC timeout and reactor interrupt-mode smoke tests. It launches one service named `ms1` at `10.1.0.3`, unlike most single-node files that use `ms0`.

Important configuration: command runs io-engine with `${MS1_CORES:-3,4}` and `/tmp/ms1.sock`. Environment exposes ANA/reservation knobs, optional `ENABLE_INTERRUPT_MODE`, optional `NVME_IOQ_POLL_PERIOD`, `RUST_LOG`, PATH, and ASAN settings. Standard mounts and capabilities support SPDK and host temp file access.

State and integration: RPC timeout tests create `/var/tmp/pool1.img`; the compose mount includes `/var/tmp`. Interrupt tests inspect logs and Docker CPU stats for this container, so the fixed name `ms1` is part of the contract.

Risks and test signals: interrupt tests only run when `ENABLE_INTERRUPT_MODE=true`. CPU checks depend on Docker stats availability and host noise. The service must be named `ms1` for Python fixtures and log pattern checks to work.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/rpc/docker-compose.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/rpc/test_interrupt_mode.py -->
# sources/control-plane/mayastor/test/python/tests/rpc/test_interrupt_mode.py

Purpose: smoke tests for io-engine reactor interrupt mode. The file is explicitly scoped to regressions where the environment flag is ignored, idle reactors busy-poll, or futures fail to wake sleeping reactors.

Important APIs and control flow: `INTERRUPT_ENABLED` reads `ENABLE_INTERRUPT_MODE`; `interrupt_only` skips all tests unless it is `true`. `test_reactor_state_is_interrupt` searches container logs for global interrupt enablement and reactor transition messages. `test_idle_cpu_is_low` waits, calls `docker stats --no-stream`, parses CPU percentage, and asserts below 50%. `test_wakeup_from_sleep` times a `mayastor_info()` gRPC round trip and asserts under 500 ms.

State, dependencies, and integration: state is process log output and runtime CPU usage of `ms1`. It depends on Docker CLI, stable log strings, monotonic timing, and `common.mayastor` fixtures.

Risks and test signals: log-string coupling can break on harmless wording changes. CPU thresholds are intentionally broad but still host-sensitive. The tests provide direct signals for interrupt-mode activation, idle sleep behavior, and eventfd wakeup latency.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/rpc/test_interrupt_mode.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/rpc/test_rpc.py -->
# sources/control-plane/mayastor/test/python/tests/rpc/test_rpc.py

Purpose: asynchronous regression test for gRPC timeout handling during a long replica destroy.

Important APIs and control flow: fixtures define `/var/tmp/pool1.img`, create a 3 GiB file, and remove it afterward. `test_rpc_timeout` creates a pool and a 2 GiB replica on `ms1`, lowers the client timeout to 1 second, reconnects the handle to install the timeout, and calls `replica_destroy`. It expects a `grpc.RpcError` with `INVALID_ARGUMENT`, checks logs do not yet contain the timeout warning, retries destroy successfully, then checks logs contain the exact warning pattern for the timed-out call.

State, dependencies, and integration: state spans the large temp file, pool/replica state, client timeout configuration, reconnected gRPC stubs, and container logs. It depends on `common.command.run_cmd`, `common.mayastor`, `grpc`, asyncio pytest, and the log wording in io-engine.

Risks and test signals: a 1-second timeout and 2 GiB destroy are timing-sensitive. Exact log matching is brittle. The core signal is that timeout evidence is deferred until a later call detects the incomplete previous operation.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/tests/rpc/test_rpc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/hdl.py -->
# sources/control-plane/mayastor/test/python/v1/hdl.py

Purpose: reusable v1 Mayastor gRPC client wrapper for Python tests. `MayastorHandle` hides channel creation, stub construction, default timeouts, and request object boilerplate for bdev, pool, replica, snapshot, host, and nexus services.

Important APIs and control flow: constructor opens an insecure channel to `<ip>:10124`, creates service stubs, reads `config["grpc"]["client_timeout"]`, and runs `_readiness_check`. `install_stub` wraps every public stub method in `functools.partial(..., timeout=self.timeout)`, and `reconnect` rebuilds all stubs. Wrapper methods include `bdev_create/share/unshare/destroy/list`, `pool_create/destroy/list`, `replica_create/destroy/list`, `mayastor_info`, `nexus_create/publish/unpublish/destroy/list/add/remove`, `nexus_create_snapshot`, `pools_as_uris`, and `list_snapshots`.

State, dependencies, and integration: state is the gRPC channel, current timeout, IP address, and installed stubs. It depends on generated protobuf modules, pytest-testconfig, and docker-compose fixtures indirectly through callers.

Risks and test signals: `pool_create` accepts a `type` argument but does not send `pooltype`, so callers needing LVM use raw stubs. `Volume.create` appears to call `nexus_create` with an obsolete signature. Readiness catches only `_InactiveRpcError` and retries once. This file is tested indirectly by nearly every v1 test.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/hdl.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/mayastor.py -->
# sources/control-plane/mayastor/test/python/v1/mayastor.py

Purpose: shared pytest fixtures for v1 Mayastor tests. It converts docker-compose containers into `MayastorHandle` dictionaries at function or module scope and provides temp-file and size-check helpers.

Important APIs and control flow: `check_size(prev, current, delta)` asserts pool used-space change in MiB. `containers` and `container_mod` collect compose containers by name. `mayastors` and `mayastor_mod` create `MayastorHandle` instances using each container’s `mayastor_net` IPv4 address. `create_temp_files` removes and recreates `/tmp/<container>.img` as 1 GiB files for all containers.

State, dependencies, and integration: fixture state is dictionaries of Docker container objects and gRPC handles. Temporary state is host `/tmp` images shared into containers. It depends on pytest-docker-compose, `v1.hdl.MayastorHandle`, and `common.command.run_cmd`.

Risks and test signals: handles are not explicitly closed after yield. `create_temp_files` has no cleanup after the test beyond recreating at setup. The fixture assumes all containers join `mayastor_net`. Signals are indirect: downstream tests fail early if handles cannot connect or temp files are missing.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/mayastor.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/nexus/docker-compose.yml -->
# sources/control-plane/mayastor/test/python/v1/nexus/docker-compose.yml

Purpose: four-node v1 nexus test topology. Services `ms0` to `ms3` run io-engine on static `10.1.0.2` through `10.1.0.5`.

Important configuration: all nodes enable ANA, NVMe reservations, ASAN leak suppression, repo and `/tmp` mounts, hugepages, and SPDK capabilities. `ms0` uses cores `1,2`; `ms1`, `ms2`, and `ms3` use single cores `2`, `3`, and `4`. `ms3` additionally sets `NVME_KATO_MS=1000` and `NEXUS_DONT_READ_LABELS=true` for null-device nexus tests.

State, dependencies, and integration: the topology supports remote replicas on `ms1`/`ms2`, local/remote nexus targets on `ms0`/`ms3`, null bdev tests, failover tests, and reservation tests. Static IPs and `mayastor_net` are consumed by `v1.mayastor` fixtures.

Risks and test signals: core overlap between `ms0` and `ms1` can affect timing-sensitive tests. Host requirements include hugepages, NVMf, and Docker privileges. Compose success is validated by downstream nexus, fio, and NVMe CLI tests.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/nexus/docker-compose.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/nexus/test_multi_nexus.py -->
# sources/control-plane/mayastor/test/python/v1/nexus/test_multi_nexus.py

Purpose: stress-style v1 nexus tests that create many replicas/nexuses across nodes and run raw, filesystem, and SPDK fio while killing a child node.

Important APIs and control flow: constants create 15 nexuses and destroy 7 replicas in restart tests. `create_replicas_on_all_nodes` creates one aio pool per node, then 15 replicas per node while checking used-space deltas and list counts. `test_restart` kills/restarts `ms1`, reconnects, reimports the pool, verifies replica persistence, destroys 7 replicas, restarts again, and validates remaining count. `create_nexuses` builds published nexuses on `ms1` from replicas on `ms2`/`ms3`. Async tests connect NVMe devices or use SPDK fio and kill `ms3` during I/O.

State, dependencies, and integration: state includes `/tmp/<node>.img`, imported pools, persisted replicas, published NVMf devices, mounts under `/mnt<dev>`, and container lifecycle. Dependencies include fio helpers, NVMe CLI helpers, asyncio, pytest-asyncio, and `v1.mayastor`.

Risks and test signals: cleanup of `/mnt/dev` looks generic and may not match all mount paths. Killing nodes mid-fixture can complicate teardown. Signals cover persistence after restart and I/O survival during child-node loss.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/nexus/test_multi_nexus.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/nexus/test_nexus.py -->
# sources/control-plane/mayastor/test/python/v1/nexus/test_nexus.py

Purpose: broad v1 nexus integration tests for mirrored nexus creation, failover, ENOSPC, NVMe controller metadata, reservation keys, and multi-child failure states.

Important APIs and control flow: fixtures create pools on `ms1`/`ms2`, replicas, a nexus on `ms3`, and optionally a second preempting nexus on `ms0`. `test_enospace_on_volume` uses `Volume` with two pool URIs and expects `RESOURCE_EXHAUSTED`. Async tests run fio or SPDK fio while killing `ms2`, then assert nexus/child states. `test_nexus_cntlid` connects with NVMe CLI and checks controller ID plus ONCS bits. `test_nexus_resv_key` connects directly to a child URI and validates reservation report fields. Skipped preempt-key test documents intended reservation preemption behavior.

State, dependencies, and integration: state spans pools, replicas, NVMf shares, published nexus devices, NVMe host connections, container failure, and reservation registrations. Dependencies include `v1.hdl`, `v1.volume`, fio helpers, NVMe CLI helpers, generated v1 protobuf modules, and asyncio.

Risks and test signals: some assertions assume child ordering. `Volume.create` may call an outdated handle signature, so ENOSPC coverage is fragile. The tests are high-signal for degraded/faulted transitions, NVMf metadata, reservation setup, and I/O failure handling.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/nexus/test_nexus.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/nexus/test_nexus_snapshot.py -->
# sources/control-plane/mayastor/test/python/v1/nexus/test_nexus_snapshot.py

Purpose: pytest-bdd scenario for creating a nexus snapshot while a published one-replica nexus is under active fio I/O.

Important APIs and control flow: fixtures disconnect stale NVMe sessions, create pools on `ms1` and `ms2`, create one replica on `ms1`, create and publish a nexus on `ms3`, connect the nexus with NVMe, and start fio with `subprocess.Popen`. The snapshot step calls `mayastor_mod["ms3"].nexus_create_snapshot` with entity ID, transaction ID, snapshot name, and replica-to-snapshot UUID descriptors. Then steps validate `replicas_done`, no skipped replicas, snapshot fields from `ms1.list_snapshots()`, and fio exit status.

State, dependencies, and integration: state includes pool/replica/nexus objects, an NVMe host connection, a live fio process, and snapshot metadata. It depends on snapshot, pool, replica, common, and nexus protobufs plus `common.nvme` and `common.fio`.

Risks and test signals: `create_nexus_1` destroys by name through a method expecting UUID, but the primary fixture used for connection returns without teardown. Fio cleanup waits after the snapshot. Signals cover snapshot status fan-out, stored metadata, and no I/O errors.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/nexus/test_nexus_snapshot.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/nexus/test_null_nexus.py -->
# sources/control-plane/mayastor/test/python/v1/nexus/test_null_nexus.py

Purpose: v1 nexus test that creates many nexuses backed by shared null bdevs and runs fio against all published devices.

Important APIs and control flow: `check_nexus_state` asserts every nexus and child is online. Fixtures define three device nodes and one nexus node, create 15 null bdevs per device node, share every bdev, create 15 nexuses on `ms3` from zipped child share URIs, publish all nexuses, connect all devices via NVMe, and clean up bdevs/nexuses/shares. `test_null_nexus` checks state and runs fio randwrite across connected devices.

State, dependencies, and integration: state includes null bdevs, NVMf share URIs, published nexuses, NVMe host connections, and fio activity. It depends on `NEXUS_DONT_READ_LABELS=true` in compose, `common.nvme`, `common.fio`, and v1 handle wrappers.

Risks and test signals: enum use comes from legacy `mayastor_pb2` while handles use v1 nexus methods, so compatibility matters. Null devices cannot be read, limiting verification to write behavior. Signals are online state for every child and successful fio completion.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/nexus/test_null_nexus.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/nexus/test_remote_only.py -->
# sources/control-plane/mayastor/test/python/v1/nexus/test_remote_only.py

Purpose: repeated smoke test for a nexus that has only remote children and no local bdev on the nexus node.

Important APIs and control flow: `ensure_zero_devices` checks bdev lists on `ms0` and `ms1`; `create_publish` creates one nexus on the local node from remote child URIs, publishes it, waits two seconds, and destroys it; `delete_all_bdevs` unshares and destroys malloc bdevs. `test_remote_only` runs ten times, creates malloc bdevs on remote `ms1`, shares them, creates/publishes/destroys the nexus on `ms0`, deletes remote bdevs, and asserts no devices remain.

State, dependencies, and integration: state is malloc bdevs, share URIs, transient nexus records, and bdev lists on two nodes. It depends on v1 module-scoped fixtures and the four-node nexus compose stack.

Risks and test signals: `ensure_zero_devices` only asserts the last iterated node’s bdev count because the assertion is outside the loop. `create_publish` destroys without unpublishing. The main signal is leak detection after repeated remote-only create/publish/destroy cycles.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/nexus/test_remote_only.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/pool/docker-compose.yml -->
# sources/control-plane/mayastor/test/python/v1/pool/docker-compose.yml

Purpose: single-node v1 pool test environment with LVM support enabled.

Important configuration: `ms0` runs io-engine on `10.1.0.2` with cores `1,2`. Environment includes ANA/reservation settings, `PATH=${LLVM_SYMBOLIZER_DIR:-}:${LVM_BINS:-}`, ASAN leak suppression, and `ENABLE_LVM=true`. The service mounts repo, `/nix`, hugepages, `/tmp`, and `/var/tmp`, and exposes loop devices `/dev/loop0` through `/dev/loop7`.

State and integration: v1 pool tests create aio images and LVM volume groups using loop devices. The extra PATH and devices allow `pvcreate`, `vgcreate`, and related LVM commands invoked through `nix-sudo`.

Risks and test signals: LVM tests depend on host loop device availability and cleanup. Missing device mappings or LVM binaries cause setup failures. Compose correctness is indirectly validated by pool creation, import/export, LVM feature reporting, and list pool assertions.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/pool/docker-compose.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/pool/test_bdd_lvm.py -->
# sources/control-plane/mayastor/test/python/v1/pool/test_bdd_lvm.py

Purpose: v1 pytest-bdd coverage for LVM pool feature reporting, LVM pool creation/destruction on loop-backed volume groups, LVS pool creation/destruction, and list output pool type fields.

Important APIs and control flow: fixtures query `mayastor_info`, create a loop-backed `/tmp/ms0-disk0.img`, run `losetup`, `pvcreate`, and `vgcreate`, and create another aio image. Raw `pool_rpc.CreatePool` sends explicit `pooltype` because the high-level handle does not. Steps check `registration_info.features.logicalVolumeManager`, create LVM and LVS pools, destroy them, list pools, and validate capacity, used bytes, online state, and `pooltype`.

State, dependencies, and integration: state includes host loop devices, LVM VG `lvmpool`, aio file `ms0-disk1.img`, and Mayastor pools. Dependencies include `nix-sudo`, LVM tools, loop devices, pool protobufs, and v1 fixtures.

Risks and test signals: duplicate Python function names shadow earlier definitions but pytest-bdd decorators have already registered step handlers. Cleanup detaches loop device before explicit VG removal in this file, which may leave host LVM state if failures occur. Signals cover feature bit and pool listing metadata.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/pool/test_bdd_lvm.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/pool/test_bdd_pool.py -->
# sources/control-plane/mayastor/test/python/v1/pool/test_bdd_pool.py

Purpose: v1 pytest-bdd pool management coverage, including UUID validation, import/export, name-filtered listing, duplicate handling, invalid disks, aio pools, and destroy errors.

Important APIs and control flow: fixtures create `/tmp/ms0-disk0.img`, wrap `pool_rpc.CreatePool`, list by name, track pools for cleanup, and destroy any remaining tracked pools with name and UUID. Steps expect `INVALID_ARGUMENT` for invalid block size, invalid UUID, and multiple disks; create valid UUID pools; create/export/import aio pools; reject import with invalid UUID; list all/name-filtered pools; and capture duplicate or missing destroy errors. Then steps assert `ALREADY_EXISTS`, `NOT_FOUND`, empty/non-empty find results, filtered list sizes, and UUID preservation.

State, dependencies, and integration: state includes an aio image, pool records, optional UUID fields, exported/imported on-disk metadata, and live gRPC responses. It depends on `pool_pb2`, pytest-bdd, `grpc`, `run_cmd`, and `v1.mayastor`.

Risks and test signals: some create calls pass a string instead of list for disks in error paths, intentionally exercising validation but also coupling to protobuf coercion behavior. The test has strong signals for API status codes and persistent UUID import semantics.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/pool/test_bdd_pool.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/rebuild/docker-compose.yml -->
# sources/control-plane/mayastor/test/python/v1/rebuild/docker-compose.yml

Purpose: single-node v1 rebuild test environment. It launches `ms0` at `10.1.0.2`.

Important configuration: command runs io-engine with cores `1,2` and `/tmp/ms0.sock`. Environment enables ANA and reservations, sets PATH and ASAN leak suppression, and uses the standard source, `/nix`, hugepages, `/tmp`, and `/var/tmp` mounts. Capabilities and unconfined seccomp are granted for SPDK/io-engine.

State and integration: rebuild tests create aio files in host `/tmp`, which are visible to the container. Python v1 fixtures connect to the service over `mayastor_net` and call the v1 nexus rebuild RPCs.

Risks and test signals: only one node is present, so tests focus on local file-backed children and rebuild state transitions rather than network failures. Environment failures show up as gRPC readiness or file access failures. Assertions live in the paired rebuild tests.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/rebuild/docker-compose.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/rebuild/test_bdd_rebuild.py -->
# sources/control-plane/mayastor/test/python/v1/rebuild/test_bdd_rebuild.py

Purpose: v1 equivalent of the rebuild BDD tests, covering rebuild start/stop/pause/resume and child online/offline state transitions through the v1 nexus service.

Important APIs and control flow: helpers map text to `nexus_pb2` enum classes. Fixtures create two 64 MiB aio files, a named nexus with `minCntlId`, `maxCntlId`, reservation key, and one source child, then look it up through `nexus_rpc.ListNexus`. Step functions add a target child with `norebuild=True`, call `StartRebuild`, `PauseRebuild`, `ResumeRebuild`, `StopRebuild`, `GetRebuildStats`, `GetRebuildState`, and `ChildOperation`. Then steps assert nexus state, source/target child states, rebuild count, rebuild state string, undefined rebuild state, and stat counters.

State, dependencies, and integration: state lives in `/tmp/disk-rebuild-*.img`, v1 nexus child records, rebuild counters, and gRPC status. It depends on `nexus_pb2`, pytest-bdd, sudo, and v1 fixtures.

Risks and test signals: `rebuild_state` catches all exceptions and converts them to `None`, which can hide unexpected errors. Unlike the legacy variant, offline child operation does not retry for degraded state. Signals are direct enum and counter comparisons.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/rebuild/test_bdd_rebuild.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/rebuild/test_bdd_rebuild_history.py -->
# sources/control-plane/mayastor/test/python/v1/rebuild/test_bdd_rebuild_history.py

Purpose: v1 pytest-bdd coverage for rebuild history records. It focuses on full rebuild of a faulted replica; partial rebuild scenario is declared but not implemented.

Important APIs and control flow: fixtures create three 64 MiB aio files for source, target, and new child, create a two-child nexus, and expose lookup by UUID. Steps remove `target_uri`, add `new_child_uri` with `norebuild=True`, start a rebuild on the new child, sleep two seconds, call `GetRebuildHistory`, and assert exactly one record exists. Partial rebuild steps raise `NotImplementedError`.

State, dependencies, and integration: state includes three host image files, a v1 nexus with child replacement, rebuild execution state, and rebuild history records stored by io-engine. It depends on pytest-bdd feature files, `nexus_pb2`, sudo, and v1 fixtures.

Risks and test signals: the full rebuild waits a fixed two seconds instead of polling completion, so slow hosts may be flaky. The partial rebuild scenario will fail if enabled. Assertions only check record count, not record fields, child URI, or rebuild type. The file still provides useful coverage that history is populated and retrievable after a full rebuild path.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/rebuild/test_bdd_rebuild_history.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/replica/docker-compose.yml -->
# sources/control-plane/mayastor/test/python/v1/replica/docker-compose.yml

Purpose: v1 replica test environment with elevated LVM/udev access. It launches one `ms0` service.

Important configuration: environment enables LVM, debug logging, ANA/reservations, ASAN leak suppression, and LVM-aware PATH. Command runs io-engine on core `1` with `--reactor-freeze-detection`. It mounts repo, `/nix`, hugepages, `/tmp`, `/var/tmp`, `/dev`, and `/run/udev`, runs privileged with host IPC, and maps loop devices `/dev/loop0` through `/dev/loop2`.

State and integration: tests create LVS and LVM pools, loop-backed VGs, and replicas. The `/dev` and udev mounts plus privileged mode support LVM discovery and cleanup.

Risks and test signals: privileged host device access increases environmental coupling and cleanup risk. Missing loop devices or LVM tools will fail setup. Downstream replica tests validate creation, destruction, list filtering, pooltype metadata, and reactor stability.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/replica/docker-compose.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/replica/test_bdd_lvm_replica.py -->
# sources/control-plane/mayastor/test/python/v1/replica/test_bdd_lvm_replica.py

Purpose: v1 pytest-bdd tests for replicas backed by LVM pools and mixed listing of LVM/LVS replicas.

Important APIs and control flow: fixtures create replicas through `replica_rpc.CreateReplica`, find replicas with `ListReplicaOptions(pooltypes=[...])`, create pools with explicit pooltype, and provision/reuse an LVM VG `lvmpool` using loop setup and LVM commands. Scenarios create an LVM pool from a VG, create an LVM-backed replica using the VG UUID as pool UUID, destroy it, create an LVS pool with a replica, and list both pool types. Then steps assert LVM replica existence/removal and pooltype/size fields.

State, dependencies, and integration: state includes loop device, VG UUID, LVM and LVS pools, and replica records. It depends on `nix-sudo`, LVM tools, loop devices, pool/replica/common protobufs, and v1 fixtures.

Risks and test signals: `find_replica` returns `None` after inspecting the first non-matching replica, which can miss later matches. `create_replica` ignores its `pooltype` argument. Cleanup catches broad exceptions. Signals still cover basic LVM-backed creation/destruction and list metadata.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/replica/test_bdd_lvm_replica.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/replica/test_bdd_replica.py -->
# sources/control-plane/mayastor/test/python/v1/replica/test_bdd_replica.py

Purpose: comprehensive v1 pytest-bdd replica behavior tests for create, duplicate name/UUID, destroy error variants, list filtering, share/unshare, and unsupported iSCSI paths.

Important APIs and control flow: fixtures create an LVS pool and expose fixed replica name, UUID, and size. `create_lvs_replica` calls `replica_rpc.CreateReplica`; `find_replica` scans by name and UUID; listing steps use `ListReplicaOptions` by name or pool name. Error steps assert `ALREADY_EXISTS`, `NOT_FOUND`, `FAILED_PRECONDITION`, and `INVALID_ARGUMENT` for unsupported iSCSI or protocol change. Share/unshare calls use `ShareReplica`/`UnshareReplica`.

State, dependencies, and integration: state is the LVS pool, live replicas tracked in `current_replicas`, share state, and list filter responses. It depends on `pool_pb2`, `replica_pb2`, `common_pb2`, `grpc`, pytest-bdd, and v1 fixtures.

Risks and test signals: several then steps are pass-through markers, read/write scenarios are skipped, and duplicate function names for then handlers overwrite Python names though decorators keep registrations. Strong signals include explicit gRPC status codes, list counts by filter, and share enum state.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/replica/test_bdd_replica.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/volume.py -->
# sources/control-plane/mayastor/test/python/v1/volume.py

Purpose: small helper object intended to create a volume by creating replicas on pool URIs and publishing a nexus on a target node.

Important APIs and control flow: `Volume.__init__` stores UUID, nexus node URI, pool URIs, and size. `__parse_uri` splits URIs with `urlparse`. `__create_replicas` expects `pool://host/pool_name`, opens a `MayastorHandle`, lists the named pool to get UUID, creates an NVMf shared replica with fixed name `"replica-1"` and the volume UUID, and returns replica responses. `create` expects `nvmt://host`, converts replica URIs into children, creates a handle, calls `nexus_create`, publishes the nexus, and returns device URI.

State, dependencies, and integration: state spans remote pool lookup, replica creation on each pool, and nexus creation/publish on the target. It depends on `MayastorHandle`, `urlparse`, `common_pb2.NVMF`, and `pool_pb2.ListPoolOptions`.

Risks and test signals: `create` calls `handle.nexus_create(self.uuid, self.size, replicas)` but `MayastorHandle.nexus_create` requires name, uuid, size, controller IDs, reservation keys, and children; this helper appears stale. Fixed replica names can collide. It is indirectly exercised by `test_enospace_on_volume`.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/python/v1/volume.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.commitlintrc.json -->
# sources/control-plane/rook/.commitlintrc.json

Purpose: commitlint configuration for the Rook source tree using conventional commits with a project-specific type vocabulary.

Important rules: it extends `@commitlint/config-conventional`, enforces `type-enum` at severity 2 with `always`, and permits types such as `block`, `bot`, `build`, `ci`, `core`, `docs`, `helm`, `k8sutil`, `nfs`, `operator`, `pool`, `security`, `test`, and `tests`. It requires blank lines before body and footer and disables body max line length by setting severity 0.

State, dependencies, and integration: no runtime state is persisted by the file. It depends on commitlint and the conventional config package in the JavaScript/tooling environment. It integrates with commit/PR checks wherever commitlint is run.

Risks and test signals: the strict type list can reject otherwise valid conventional commit types if not updated with new Rook areas. Disabling body line length permits long generated or wrapped text. Signals are commitlint pass/fail results in local hooks or CI.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.commitlintrc.json -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.docs/macros/includes/main.py -->
# sources/control-plane/rook/.docs/macros/includes/main.py

Purpose: MkDocs macro helper that rewrites Rook GitHub links from `master` to the currently checked-out branch/tag.

Important APIs and control flow: module-level regex matches `github.com/.../rook/.../master/` links and a substitution template inserts the target ref. `define_env(env)` opens the current repository with `pygit2.Repository(".")`, reads `repo.head.shorthand`, and stores it in `env.variables["current_branch"]`. `on_post_page_macros(env)` skips rewriting on `master`; otherwise it runs `re.sub` over `env.markdown`.

State, dependencies, and integration: state is the macro environment variable `current_branch` and modified page markdown. It depends on pygit2, regex, MkDocs macros lifecycle hooks, and being executed from a Git worktree.

Risks and test signals: detached HEADs or nonstandard execution directories can produce unsuitable branch names or repository errors. The regex is broad and rewrites all matching markdown after macro expansion. Signals are rendered documentation links pointing at the active branch rather than master.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.docs/macros/includes/main.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/dependabot.yml -->
# sources/control-plane/rook/.github/dependabot.yml

Purpose: Dependabot configuration for Rook dependencies.

Important configuration: version 2 with beta ecosystems enabled. It checks Go modules in `/` weekly and groups updates into `golang-dependencies` for `github.com/golang*`, `k8s-dependencies` for `k8s.io*` and `sigs.k8s.io*`, and `github-dependencies` for `github.com*`. It also checks GitHub Actions dependencies in `/` weekly.

State, dependencies, and integration: Dependabot stores update state in GitHub and opens PRs based on this file. It integrates with `go.mod` at the repository root and workflows under `.github/workflows/*.yml`.

Risks and test signals: the broad `github.com*` group may overlap with the more specific `github.com/golang*` pattern depending on Dependabot grouping precedence. Weekly cadence can batch large update sets. Signals are generated Dependabot PRs grouped as configured and action-version update PRs.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/dependabot.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/auto-assign.yaml -->
# sources/control-plane/rook/.github/workflows/auto-assign.yaml

Purpose: GitHub Actions workflow that lets contributors self-assign issues by commenting `/assign`.

Important configuration and control flow: it triggers on `issue_comment` `created` and `edited` events. Global permissions grant read-only contents; the `assign` job grants `issues: write`, runs on Ubuntu latest, and invokes pinned `bdougie/take-action` with a thank-you message, trigger `/assign`, and the repository `GITHUB_TOKEN`.

State, dependencies, and integration: state changes occur in GitHub issue assignees and issue comments. It depends on the third-party action and GitHub token permissions. It integrates with issue triage rather than code builds.

Risks and test signals: a third-party action pin is a specific commit, which is good for supply-chain stability but needs manual updates. Edited comments can retrigger assignment. Signals are successful workflow runs and issue assignee changes after `/assign`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/auto-assign.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/build.yml -->
# sources/control-plane/rook/.github/workflows/build.yml

Purpose: Rook pull-request build workflow for macOS and Linux.

Important configuration and control flow: triggers on `pull_request`, uses strict bash defaults, cancels superseded runs by workflow/head ref, and grants contents read. `macos-build` skips PRs labeled `skip-ci`, checks out full history, installs Go 1.26 and Helm 3.18.2, runs build, codegen, module check, CRD generation, and RBAC generation, validating modified files after each generated step. `linux-build-all` runs on Ubuntu 22.04 for Go 1.25 and 1.26, installs QEMU, and delegates to `tests/scripts/github-action-helper.sh build_rook_all`.

State, dependencies, and integration: state is CI workspace output and generated file diffs. It depends on pinned checkout/setup-go/setup-helm/setup-qemu actions, Make targets, Go toolchains, Helm, Docker/QEMU, and Rook test scripts.

Risks and test signals: macOS `make -j$nproc` may rely on shell variable behavior; Linux uses a matrix for compatibility. Signals are build success and validation scripts confirming generated artifacts are committed.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/build.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/canary-integration-suite.yml -->
# sources/control-plane/rook/.github/workflows/canary-integration-suite.yml

Purpose: reusable workflow entry point for Rook canary integration tests.

Important configuration and control flow: triggers on pushes to tags `v*`, branches `master` and `release-*`, and pull requests targeting `master` or `release-*`, ignoring documentation and design path changes for PRs. It uses strict bash defaults, cancels superseded runs, grants contents read, and defines a single `canary-tests` job that calls `./.github/workflows/canary-integration-test.yml` with `ceph_images: ["quay.io/ceph/ceph:v19"]` and inherited secrets.

State, dependencies, and integration: state is delegated to the reusable canary workflow and its cluster/test resources. It depends on the called workflow contract accepting `ceph_images` and inherited secrets. It integrates release branches, tags, and PR validation.

Risks and test signals: changes outside ignored docs/design paths can trigger expensive integration jobs. The Ceph image is fixed to v19, so coverage tracks that version only unless updated. Signals are pass/fail results from the reusable workflow.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/canary-integration-suite.yml -->
