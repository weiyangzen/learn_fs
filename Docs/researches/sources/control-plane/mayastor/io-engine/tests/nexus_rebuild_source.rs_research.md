# sources/control-plane/mayastor/io-engine/tests/nexus_rebuild_source.rs

Purpose: verifies rebuild source selection policy, especially preference for a local healthy replica on the nexus node and fallback to first available non-destination child.

Important APIs/types/functions: `TestNode`, `SharedRpcHandle`, `PoolBuilder`, `ReplicaBuilder`, `NexusBuilder`, `ChildState`, `ChildStateReason`, `test_src_selection`, and `get_rebuild_history`.

Control flow: the test starts three io-engine nodes, creates one pool per node, and builds `TestNode` helpers that create/share replicas. `test_src_selection` creates replicas according to a node-index topology, creates a nexus, offlines the destination child, waits for `Degraded/ByClient`, onlines it, waits for all children online, reads the first rebuild history record, maps `src_uri` and `child_uri` to child indexes, and asserts the source index equals the expected table value. The main test covers all-local, local/remote, remote/local, remote/remote/local, two-local, and all-remote layouts.

State and persistence behavior: no persistent store. Source-selection evidence is rebuild history. Each scenario destroys its nexus and clears replicas to avoid contamination.

Dependencies and integration points: gRPC builder APIs, remote NVMf sharing, child online/offline operations, and rebuild history RPC.

Risks: assertions encode implementation policy; future load-aware or randomized source choice would require test changes.

Test signals: expected source child index for every topology and successful return to online.
