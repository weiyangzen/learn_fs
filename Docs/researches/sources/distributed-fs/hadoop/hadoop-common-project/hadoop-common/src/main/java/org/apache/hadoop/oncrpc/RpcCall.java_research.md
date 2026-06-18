# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcCall.java

Purpose: models an ONC RPC call header as defined by RFC 1831, including xid, program, version, procedure, credentials, and verifier.

Important APIs/types/functions: `RPC_VERSION`, static `read`, `getInstance`, constructor validation, getters, `write`, and `toString`.

Control flow: `read` consumes header fields and delegates credential/verifier decoding. Constructor validates message type is `RPC_CALL` and RPC version is 2. `write` emits the fixed header then credential and verifier auth blocks.

State and persistence: immutable per-call fields; no persistence.

Dependencies and integration: central input object for `RpcUtil.RpcMessageParserStage`, `RpcProgram`, security handlers, and portmap requests. Depends on `Credentials` and `Verifier`.

Risks: malformed auth flavors throw during parse. `toString` assumes credential and verifier are non-null. Validation currently only checks type and RPC version, not program/version/procedure ranges.

Test signals: `TestRpcCall` covers XDR serialization, invalid versions/types, and credential/verifier handling.
