# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcDeniedReply.java

Purpose: represents the denied branch of an ONC RPC reply.

Important APIs/types/functions: `RejectState`, constructor, static `read`, `getRejectState`, `toString`, and `write`.

Control flow: read consumes a verifier and reject-state integer. Write emits xid, message type, reply state, verifier, and reject state.

State and persistence: immutable reply fields; no persistence.

Dependencies and integration: produced by `RpcProgram.sendRejectedReply` and parsed by clients such as `RegistrationClient`.

Risks: enum parsing uses ordinal indexing without validation. `toString` concatenates fields without separators in some places, which is harmless for logs but less readable.

Test signals: `TestRpcDeniedReply` covers read/write behavior and state access.
