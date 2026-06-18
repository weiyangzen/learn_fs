# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcMessage.java

Purpose: abstract base for ONC RPC call and reply messages, carrying xid and message type.

Important APIs/types/functions: `Type` enum, constructor, abstract `write`, `getXid`, `getMessageType`, and `validateMessageType`.

Control flow: constructor rejects any type except `RPC_CALL` or `RPC_REPLY`. `Type.fromValue` returns null for out-of-range values.

State and persistence: immutable `xid` and `messageType`; no persistence.

Dependencies and integration: extended by `RpcCall` and `RpcReply`; used by parser and response code.

Risks: invalid wire type becomes null, then subclass validation throws. Type ordinal order is protocol significant and must not be reordered.

Test signals: `TestRpcMessage` covers type mapping and validation.
