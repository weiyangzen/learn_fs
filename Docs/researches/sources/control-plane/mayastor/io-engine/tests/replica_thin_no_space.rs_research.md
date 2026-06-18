# sources/control-plane/mayastor/io-engine/tests/replica_thin_no_space.rs

Purpose: fault-injection-enabled Tokio integration tests for ENOSPC propagation from thin replicas. It verifies both real thin-pool exhaustion and injected NVMe `NO_SPACE` errors become fio-visible `ENOSPC`.

Important APIs/types/functions: `replica_thin_nospc` builds an io-engine container, malloc pool, thin 80 MiB replica on a 100 MiB backing pool, and a second thick filler replica. `replica_nospc_inject` uses `InjectionBuilder`, `FaultDomain::BdevIo`, `FaultIoStage::Submission`, and `NvmeStatus::NO_SPACE`. Both use `PoolBuilder`, `ReplicaBuilder`, `GrpcConnect`, `FioBuilder`, and `FioJobResult`.

Control flow: each test initializes composer, starts one io-engine, creates/shares a replica, opens the exported NVMe-oF target, runs a direct libaio write workload, then asserts the single fio job failed with `Errno::ENOSPC`.

State/persistence: all state is transient docker/malloc/SPDK state cleaned by the compose harness. The tests depend on thin allocation accounting and fault injection state inside io-engine during the run.

Dependencies/integration: integrates io-engine gRPC v1 helpers, the fault injection subsystem, SPDK NVMe status translation, NVMe-oF host connect helpers, and fio result parsing.

Risks: feature-gated by `fault-injection`; requires fio, NVMe-oF, and container networking. The real exhaustion case is sensitive to pool sizing and write pattern; the injection case is sensitive to matching device name `r0`.

Test signals: passing tests show ENOSPC survives both bdev submission injection and backend allocation failure all the way to host I/O.
