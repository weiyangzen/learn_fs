# sources/control-plane/mayastor/io-engine/tests/replica_timeout.rs

Purpose: ignored integration test for NVMe-oF child timeout/fault behavior when a replica container is suspended and later thawed.

Important APIs/types/functions: `replica_stop_cont` uses v0 gRPC bdev create/share RPCs, `Config::get_or_init` with short `NvmeBdevOpts`, `nexus_create`, `nexus_lookup_mut`, `UntypedBdev`, `bdev_get_name`, `NexusStatus`, and an external `initiator` binary.

Control flow: the test starts a replica io-engine container, creates/shares a malloc bdev, creates a local nexus with the remote child, pauses the replica container, submits a read expected to time out, waits past KATO, thaws the container, verifies subsequent read failure, then unshares a faulted nexus.

State/persistence: transient gRPC-created bdevs, one local nexus, and kernel/container pause state. Timeout configuration is applied globally through `Config`.

Dependencies/integration: covers docker-compose pause/thaw, SPDK NVMe bdev timeouts, nexus child faulting, the `initiator` binary, and NVMe-oF exported nexus access.

Risks: marked `#[ignore]` because it is timing-heavy and environment-dependent. It assumes fixed ports, localhost access, and reliable container suspension semantics.

Test signals: when run manually, success means a timed-out remote child is destroyed/faulted cleanly and a faulted nexus can still be unpublished.
