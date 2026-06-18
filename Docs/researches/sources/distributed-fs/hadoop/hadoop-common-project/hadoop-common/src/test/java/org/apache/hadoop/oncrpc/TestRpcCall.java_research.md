# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/TestRpcCall.java

Purpose: Unit tests for construction and validation rules of ONC/RPC call headers.

Important APIs/types/functions: `RpcCall`, `RpcCall.RPC_VERSION`, `RpcMessage.Type.RPC_CALL`, `CredentialsNone`, `VerifierNone`, and getter methods for xid/program/version/procedure/auth fields.

Control flow: a valid constructor call is created and every exposed field is asserted. Two negative tests assert `IllegalArgumentException` for unsupported RPC version and for message type `RPC_REPLY` passed to a call constructor.

State and persistence: local message objects only; no external state.

Dependencies/integration points: ONC/RPC call validation used by frame decoding, clients, and server programs.

Risks: protocol validation must stay strict; allowing a wrong message type or version would corrupt server dispatch and error handling.

Test signals: confirms call headers enforce version/type invariants and preserve authentication verifier objects.
