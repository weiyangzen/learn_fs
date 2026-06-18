# sources/control-plane/mayastor/io-engine/tests/nexus_restart.rs

Purpose: validates that a published nexus can be recreated after its hosting io-engine is killed/restarted while host I/O is running, then rebuilt back to three replicas without verification failure.

Important APIs/types/functions: `TestCluster`, `StorageNode`, `NodeConfig`, `NexusBuilder`, `PoolBuilder`, `ReplicaBuilder`, `NvmfLocation`, `NmveConnectGuard`, `FioBuilder`, `FioJobBuilder`, watch `Sender`/`Receiver`, `run_io_task`, and `run_manage_task`.

Control flow: cluster setup creates backing files, starts etcd plus three io-engine containers, and creates one pool/replica per node. The test creates and publishes a three-child nexus. `run_io_task` connects, signals readiness, runs randwrite FIO with crc32 metadata, then randread verify FIO. `run_manage_task` waits, kills and restarts the nexus node, recreates the nexus with one child, recreates a pool, adds two children with rebuild, and republishes.

State and persistence behavior: node 2 uses etcd, but the test explicitly recreates the nexus and child set. It exercises target disappearance, replacement, rebuild, and host I/O continuity.

Dependencies and integration points: etcd, compose kill/start, direct file binds, NVMf host connection, FIO verification, persistent-store CLI option, and gRPC builders.

Risks: fixed sleeps are host-speed dependent; FIO unwraps yield strong but coarse failure diagnostics.

Test signals: write FIO and verify FIO succeed, recreate/add/publish calls succeed, and concurrent restart management does not panic.
