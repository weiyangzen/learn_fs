# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcReply.java

Purpose: abstract base for ONC RPC replies, carrying accepted/denied state and verifier.

Important APIs/types/functions: `ReplyState`, constructor, `getVerifier`, static `read`, and `getState`.

Control flow: `read` consumes xid, validates message type is `RPC_REPLY`, reads reply state, and dispatches to `RpcAcceptedReply.read` or `RpcDeniedReply.read`.

State and persistence: immutable reply state and verifier; no persistence.

Dependencies and integration: used by clients, portmap registration, and tests to parse server replies.

Risks: `ReplyState.fromValue` does not bounds-check. A malformed XDR stream can throw unchecked exceptions. `getVerifier` returns `RpcAuthInfo` even though field type is `Verifier`.

Test signals: `TestRpcReply` covers read dispatch and reply-state handling.
