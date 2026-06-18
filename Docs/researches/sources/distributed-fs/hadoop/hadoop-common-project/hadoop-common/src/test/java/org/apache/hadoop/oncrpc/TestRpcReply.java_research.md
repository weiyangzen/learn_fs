# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/TestRpcReply.java

Purpose: Unit coverage for base RPC reply state mapping and constructor behavior.

Important APIs/types/functions: `RpcReply`, `RpcReply.ReplyState.fromValue`, `VerifierNone`, anonymous `RpcReply` subclass, and `RpcMessage.Type.RPC_REPLY`.

Control flow: maps values 0 and 1 to `MSG_ACCEPTED` and `MSG_DENIED`, checks value 2 throws, and constructs an anonymous reply to assert xid, message type, and state.

State and persistence: no external state.

Dependencies/integration points: base class for accepted and denied RPC replies.

Risks: enum ordinal mapping is protocol-sensitive; serialization is not tested here.

Test signals: validates reply-state constants and base constructor invariants used by concrete reply classes.
