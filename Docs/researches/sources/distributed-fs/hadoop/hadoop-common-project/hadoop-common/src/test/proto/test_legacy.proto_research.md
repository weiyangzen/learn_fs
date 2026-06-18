# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/proto/test_legacy.proto

Purpose: Legacy variant of the common IPC test protobuf messages. It mirrors `test.proto` message content and Java options but omits an explicit `syntax = "proto2"` line, preserving older protoc/default-syntax behavior for compatibility tests.

Important APIs/types/functions: Java package is `org.apache.hadoop.ipc.protobuf`, outer class is `TestProtosLegacy`, and generated equals/hash is enabled. It defines the same message set as `test.proto`: empty, echo, optional echo, sleep, slow ping, repeated echo, add, exchange, auth method, user, and sleep timing request/response messages.

Control flow: No executable control flow. Generated legacy message classes are imported by `test_rpc_service_legacy.proto` and used to test legacy protobuf service generation and RPC compatibility.

State and persistence behavior: Wire fields and required/optional/repeated declarations match the non-legacy schema, but generated Java class names differ. Because syntax is omitted, the file relies on proto2 defaults in older protobuf tooling.

Dependencies and integration points: Imported by `test_rpc_service_legacy.proto`. It integrates with Hadoop IPC tests that need both current and legacy generated protobuf classes available side by side.

Risks: Omitting `syntax` can produce warnings or different behavior under newer protobuf toolchains if defaults change or enforcement tightens. The schema must stay synchronized with `test.proto` for meaningful legacy/current comparisons while retaining distinct outer class names.

Test signals: Successful legacy protoc generation, import by legacy service proto, and side-by-side IPC tests comparing current and legacy generated classes validate this file.
