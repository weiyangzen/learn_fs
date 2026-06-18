# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/TestRpcMessage.java

Purpose: Unit tests for the abstract base `RpcMessage`.

Important APIs/types/functions: anonymous `RpcMessage` subclass, `getXid`, `getMessageType`, `validateMessageType`, and `XDR write` contract.

Control flow: helper creates an anonymous message with a no-op `write`. Tests assert constructor fields, successful validation for matching type, and `IllegalArgumentException` for mismatched expected type.

State and persistence: local message instance only.

Dependencies/integration points: common base for `RpcCall` and `RpcReply` hierarchy.

Risks: validation is a core guardrail; weak tests around `write` mean serialization correctness belongs to concrete subclasses.

Test signals: verifies basic identity fields and type-check failure behavior for protocol message dispatch.
