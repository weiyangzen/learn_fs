# sources/control-plane/mayastor/io-engine/src/grpc/v0/nexus_grpc.rs

Purpose: this helper module contains v0 nexus conversion and lookup utilities shared by `mayastor_grpc.rs`. It bridges internal nexus/child state and legacy v0 protobuf shapes, including the historical `nexus-{uuid}` naming convention.

Important APIs/types/functions: `map_fault_reason` and `map_child_state` map internal `FaultReason` and `ChildStateClient` into v0 child state/reason enums. `NexusChild::to_grpc`, `Nexus::to_grpc`, and `Nexus::to_grpc_v2` build v0 nexus responses. `name_to_uuid`, `uuid_to_name`, `nexus_lookup`, `nexus_add_child`, and `nexus_destroy` implement compatibility lookup and child/destruction behavior.

Control flow: lookups first try exact name, then UUID lookup, then `nexus-<uuid>` name conversion. `to_grpc_v2` reads ANA state only for NVMf-published nexuses. `nexus_add_child` looks up the nexus, adds a child with the request’s `norebuild` flag, then returns the child by URI. `nexus_destroy` is idempotent: if no nexus exists but the input is a UUID, it best-effort destroys the PTPL file.

State and persistence: conversions are read-only except for rebuild progress/ANA queries. `nexus_add_child` mutates nexus children. `nexus_destroy` mutates nexus state and may remove PTPL persistence.

Dependencies and integration points: depends on internal `nexus` types, `NexusPtpl`, `Share`, rebuild job count, UUID parsing, and `io_engine_api::v0`. It is used by the v0 Mayastor service and is intentionally separate because some macros cannot use `?` inline.

Risks: v0 maps `HotRemove` to `None`, unlike v1’s explicit hot-removed reason; `nexus_add_child` has a TODO for idempotency and may duplicate a child if URI parameters differ; lookup fallback accepts unconventional names; PTPL deletion on missing nexus can mask not-found cases. Test signals should verify state mapping, name/UUID compatibility, ANA visibility only when shared, child duplicate behavior, and idempotent destroy.
