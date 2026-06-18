# sources/control-plane/mayastor/io-engine/tests/nexus_child_online.rs

Purpose: gRPC v1 integration test for offlining and onlining a nexus child replica, including state reason reporting after a no-space offline.

Important APIs/types/functions: `create_compose_test` starts two replica nodes and one nexus node. `create_test_storage` builds pools, thin replicas, shares them, creates and publishes a two-child nexus. Test uses `test_write_to_nexus`, `offline_child_replica_wait`, `online_child_replica_wait`, `offline_child_replica`, and `wait_replica_state` with `ChildState` and `ChildStateReason`.

Control flow: write a small amount of data to nexus, offline replica 0 and wait, online it and wait, offline it again, then wait for Degraded state with reason `NoSpace`.

State and persistence: compose containers with malloc-backed pools/replicas and published NVMf nexus. No durable state beyond container lifetime.

Dependencies and integration points: gRPC v1 pool/replica/nexus builders, NVMf sharing, child state transitions, wait/poll helpers.

Risks and edge cases: one-second waits are tight on slow systems. The `NoSpace` reason for offline operation is a specific control-plane/API mapping that could be surprising.

Test signals: covers online/offline child workflow and API state/reason propagation.
