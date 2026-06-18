# sources/control-plane/mayastor/io-engine/tests/nexus_create_destroy.rs

Purpose: stress-tests simple v0 nexus lifecycle RPC behavior by repeatedly creating and destroying malloc-backed nexuses.

Important APIs/types/functions: v0 `CreateNexusRequest`, `DestroyNexusRequest`, `Nexus`, `GrpcConnect`, `RpcHandle`, `Builder`, `uuid::Uuid::new_v4`, `nexus_create_destroy`, `nexus_create_multiple_then_destroy`, and helper `create_nexuses`.

Control flow: `nexus_create_destroy` starts a single debug io-engine container, creates ten 10 MiB nexuses one at a time with distinct malloc children, and destroys each immediately by returned UUID. `nexus_create_multiple_then_destroy` creates ten nexuses, destroys them in creation order, recreates ten, then destroys them in reverse order.

State and persistence behavior: no persistent store is configured. The state under test is the in-memory nexus registry, child malloc bdev cleanup, UUID handling, and ordering independence during teardown.

Dependencies and integration points: the file uses only the compose harness and v0 mayastor gRPC surface; it avoids NVMf, FIO, rebuild, and multi-node behavior.

Risks: success is inferred from RPC calls; the tests do not explicitly list nexuses after destroy to assert an empty registry.

Test signals: every create returns a nexus, every destroy succeeds, second-batch recreate works, and reverse-order teardown does not expose stale state.
