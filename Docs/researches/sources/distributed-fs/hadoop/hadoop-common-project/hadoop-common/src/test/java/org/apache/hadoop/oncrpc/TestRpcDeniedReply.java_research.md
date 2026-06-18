# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/TestRpcDeniedReply.java

Purpose: Unit coverage for denied ONC/RPC replies and reject-state wire mapping.

Important APIs/types/functions: `RpcDeniedReply`, `RpcDeniedReply.RejectState.fromValue`, `RpcReply.ReplyState`, `RpcMessage.Type.RPC_REPLY`, and `VerifierNone`.

Control flow: maps reject values 0 and 1 to `RPC_MISMATCH` and `AUTH_ERROR`, checks value 2 throws, then constructs a denied reply and verifies xid, message type, reply state, and reject state.

State and persistence: no persistent state.

Dependencies/integration points: server-side rejected responses emitted by RPC authorization/version checks.

Risks: constructor uses `ReplyState.MSG_ACCEPTED` in the test despite a denied reply type, so the test checks fields rather than semantic consistency; enum mapping remains wire-sensitive.

Test signals: confirms invalid reject codes fail and reply metadata remains accessible for decoding/serialization paths.
