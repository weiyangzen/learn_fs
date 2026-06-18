# sources/control-plane/mayastor/io-engine/tests/nexus_crd.rs

Purpose: validates controller retry delay behavior for NVMf nexus targets, including failure with `--tgt-crdt 0`, survival with a nonzero CRD window, and reservation-conflict delay-slot selection.

Important APIs/types/functions: `Builder`, `Binary`, `GrpcConnect`, `SharedRpcHandle`, `PoolBuilder`, `ReplicaBuilder`, `NexusBuilder`, `NvmfLocation`, `NmveConnectGuard`, `FioBuilder`, `FioJobBuilder`, `FioJobResult`, `InjectionBuilder`, `FaultDomain::NexusChild`, `NexusNvmePreemption`, `NvmeReservation`, `test_nexus_fail`, `run_io_task`, and `run_nexus_manage_task`.

Control flow: `test_nexus_fail` builds one replica node and one nexus node, creates and publishes a nexus, derives child read/write fault injection URIs from the live child device name, then runs concurrent FIO and management tasks. The management task injects faults, waits, destroys the nexus, removes injections, recreates the same UUID/name nexus, and republishes it. `nexus_crd_resv` creates two reservation-holding nexuses over one replica and checks that the reservation conflict returns quickly when the selected CRD slot is zero.

State and persistence behavior: no etcd is used, but the test depends on stable nexus UUID/NQN identity across destroy/recreate and on PTPL directory state for reservation tests.

Dependencies and integration points: compose containers, NVMf host connection helpers, FIO, Linux errno behavior, fault-injection RPCs, and SPDK NVMe reservation handling.

Risks: sleeps and FIO runtime make this timing-sensitive; `EBADE` is Linux-specific; all tests are gated by `fault-injection` except only where the file is compiled.

Test signals: FIO error vs success depending on CRD, reservation conflict result and duration, successful replacement nexus publish, and expected reservation errno.
