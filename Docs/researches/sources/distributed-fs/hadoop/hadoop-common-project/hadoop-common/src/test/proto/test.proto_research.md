# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/proto/test.proto

Purpose: Core protobuf message schema for Hadoop common IPC tests. It defines request/response payloads used by test RPC services for ping, echo, add, exchange, auth, user identity, and sleep/timing scenarios.

Important APIs/types/functions: Uses `syntax = "proto2"`, Java package `org.apache.hadoop.ipc.protobuf`, outer class `TestProtos`, and generated equals/hash. Messages include empty request/response, required and optional echo messages, sleep requests/responses, slow ping, repeated-string echo, add requests/responses, exchange value lists, auth method response, user response, and extended sleep timing messages.

Control flow: The schema itself has no executable control flow; generated builders/messages are consumed by RPC service definitions in `test_rpc_service.proto` and corresponding Java test code. Required fields enforce initialized messages for core request/response types, while optional fields support compatibility tests around evolving RPC signatures.

State and persistence behavior: Proto2 wire state is field-numbered and package-scoped under `hadoop.common`. Repeated fields preserve ordered lists of strings or integers for echo/exchange/add2 tests. Optional sleep timing fields allow request/response timestamps to be omitted.

Dependencies and integration points: Imported by `test_rpc_service.proto`. Generated Java classes are used by Hadoop IPC unit/integration tests for protobuf engines, compatibility, authentication, postponed responses, and handoff timing.

Risks: Message names and field numbers are shared test ABI with service schemas; changing them breaks generated stubs and tests. Required fields can make compatibility evolution harder, which is why optional variants are present for some RPC compatibility cases.

Test signals: Protoc generation, successful import by service proto, generated builders enforcing required fields, and RPC tests exercising each message family validate the schema.
