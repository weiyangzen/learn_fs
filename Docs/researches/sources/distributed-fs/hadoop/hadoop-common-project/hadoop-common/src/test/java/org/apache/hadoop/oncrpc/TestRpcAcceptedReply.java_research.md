# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/TestRpcAcceptedReply.java

Purpose: Unit coverage for accepted ONC/RPC reply metadata and accept-state enum mapping.

Important APIs/types/functions: `RpcAcceptedReply`, `RpcAcceptedReply.AcceptState.fromValue`, `RpcReply.ReplyState`, `Verifier`, and `VerifierNone`.

Control flow: tests map wire values 0 through 5 to `SUCCESS`, `PROG_UNAVAIL`, `PROG_MISMATCH`, `PROC_UNAVAIL`, `GARBAGE_ARGS`, and `SYSTEM_ERR`; value 6 must throw. Constructor coverage verifies xid, message type, reply state, verifier reference, and accept state.

State and persistence: no persistent state; all objects are local immutable-style message instances.

Dependencies/integration points: ONC/RPC reply serialization model and JUnit assertions.

Risks: enum ordinal mapping is wire-protocol-sensitive; adding enum values without adjusting invalid-value tests can hide protocol drift.

Test signals: validates accepted-reply wire constants and constructor invariants for downstream RPC response handling.
