# sources/control-plane/mayastor/io-engine/tests/replica_crd.rs

Purpose: validates that replica NVMf targets use the third CRD value for data transfer errors, with a zero third slot preventing long retry delay.

Important APIs/types/functions: `PoolBuilder`, `ReplicaBuilder`, `InjectionBuilder`, `FaultDomain::BdevIo`, `FaultIoOperation::Write`, `FaultIoStage::Submission`, `FaultMethod::DATA_TRANSFER_ERROR`, `FioBuilder`, `FioJobBuilder`, `FioJobResult`, `Errno::EIO`, and `add_fault_injection`.

Control flow: with `fault-injection`, the test starts one io-engine using `--tgt-crdt 15,15,0`, creates and shares a thin replica, installs a bdev-I/O write-submission injection at offset 1000, opens the NVMf location, runs a direct libaio write FIO job, and inspects its result and runtime.

State and persistence behavior: no persistent store. State is target CRD configuration and injection registry.

Dependencies and integration points: NVMf replica share, FIO, Linux errno, and fault-injection RPCs.

Risks: Linux-specific errno and timing assertion; FIO must hit the injected range.

Test signals: FIO job returns `EIO` and total runtime is below the delay that would occur if the wrong CRD slot were used.
