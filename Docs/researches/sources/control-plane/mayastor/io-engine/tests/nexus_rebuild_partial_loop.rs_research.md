# sources/control-plane/mayastor/io-engine/tests/nexus_rebuild_partial_loop.rs

Purpose: extended soak test that runs verified FIO against a three-replica nexus while repeatedly restarting two replica nodes and forcing partial rebuilds back to online.

Important APIs/types/functions: `Node`, `ComposeTest`, `SharedRpcHandle`, `PoolBuilder`, `ReplicaBuilder`, `NexusBuilder`, `find_nexus_by_uuid`, `FioBuilder`, `FioJobBuilder`, `oneshot`, `Mutex`, `ChildState`, `Status`, `Code`, and `monitor_nexus`.

Control flow: with `extended-tests`, the test creates three 8 GiB replicas on aio pools, publishes a three-child nexus, and starts crc32 `randrw` FIO. A parallel restart loop alternates node 0 and node 1 restarts until FIO finishes. Each restart recreates the node's pool/share, onlines its child, and waits for all nexus children to return to `Online`.

State and persistence behavior: no etcd. Restart recovery depends on reusable pool/replica builders. Child states repeatedly move through degraded/rebuilding/online while host I/O continues.

Dependencies and integration points: compose restart, aio files, NVMf published nexus, FIO verification, and rebuild progress polling. `Drop` removes backing files.

Risks: long-running and timing-sensitive; comment notes around an hour or more. Slow rebuilds can hit the 120 second online timeout.

Test signals: FIO exits successfully, monitor observes all children online after each restart, and no timeout/fault status occurs.
