# sources/control-plane/mayastor/io-engine/tests/nexus_thin.rs

Purpose: validates nexus creation constraints involving thin replicas and checks pool committed-space accounting.

Important APIs/types/functions: `ThinTest`, `ComposeTest`, `SharedRpcHandle`, `PoolBuilder`, `ReplicaBuilder`, `NexusBuilder`, and tonic error codes.

Control flow: `ThinTest::new` starts one io-engine, creates a pool, then creates two 50 MiB thin replicas, one 50 MiB thick replica, and one 30 MiB thick replica. `nexus_thin_create_1` attempts a nexus with a thin replica and a bad-size thick replica and expects an internal error. `nexus_thin_create_2` creates a valid nexus from two thin replicas and checks pool `committed` equals the sum of replica sizes.

State and persistence behavior: no persistent store. State under test is replica thin flag, size compatibility, nexus creation validation, and pool committed accounting.

Dependencies and integration points: compose, v1 gRPC builder wrappers, and pool usage reporting.

Risks: the negative test may fail due to size mismatch rather than thin/thick mixing, despite the file-level comment.

Test signals: invalid create returns `tonic::Code::Internal`, valid two-thin nexus create succeeds, and pool committed size matches total replica size.
