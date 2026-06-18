# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/proto/test_rpc_service_legacy.proto

Purpose: Legacy service schema for Hadoop IPC tests using `test_legacy.proto` messages and a distinct generated outer class. It mirrors the current service schema while preserving a legacy generated-code path.

Important APIs/types/functions: Uses `syntax = "proto2"`, Java package `org.apache.hadoop.ipc.protobuf`, outer class `TestRpcServiceProtosLegacy`, generic services, generated equals/hash, and imports `test_legacy.proto`. It declares the same service set and RPC methods as `test_rpc_service.proto`.

Control flow: Generated legacy service interfaces dispatch the same ping, echo, error, slow ping, add, exchange, sleep, auth/user, postponed response, protocol compatibility, custom protocol, and handoff sleep methods. The practical control flow is in test implementations that bind these generated services to Hadoop IPC.

State and persistence behavior: No persistent state in the schema. Wire-level method and message definitions are intended to parallel the current schema while generating separate Java classes, allowing side-by-side compatibility tests.

Dependencies and integration points: Depends on `test_legacy.proto` and protobuf generic service generation. It integrates with Hadoop IPC tests that need legacy class names and service descriptors separate from the current message/service artifacts.

Risks: The file must remain synchronized with `test_rpc_service.proto`; divergence should be intentional and documented because it affects compatibility assertions. It also relies on generic service support and legacy generated-code behavior.

Test signals: Protoc generation of `TestRpcServiceProtosLegacy`, successful imports from `TestProtosLegacy`, and legacy IPC service/client tests exercising the mirrored method set validate this schema.
