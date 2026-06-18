# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/security/TestRpcAuthInfo.java

Purpose: Tests authentication flavor mapping for ONC/RPC auth metadata.

Important APIs/types/functions: `RpcAuthInfo.AuthFlavor.fromValue`, `AUTH_NONE`, `AUTH_SYS`, `AUTH_SHORT`, `AUTH_DH`, and `RPCSEC_GSS`.

Control flow: asserts known wire values 0, 1, 2, 3, and 6 map to the expected flavors; value 4 must throw `IllegalArgumentException`.

State and persistence: none.

Dependencies/integration points: credential/verifier decoding for ONC/RPC requests and replies.

Risks: sparse enum mapping means ordinal-based implementations can be incorrect; tests cover value 4 gap but not other invalid values.

Test signals: confirms accepted auth flavors and invalid-flavor rejection.
