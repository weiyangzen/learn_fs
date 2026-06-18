# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestCredentials.java

Purpose: Tests Hadoop `Credentials` token/secret-key serialization, merge semantics, and adding credentials to UGI.

Important APIs/types/functions: `Credentials`, `Token`, `TokenIdentifier`, `Text`, `write`, `readFields`, `writeProto`, `readProto`, `writeTokenStorageToStream`, `readTokenStorageStream`, `addAll`, `mergeAll`, `UserGroupInformation.addCredentials`, and `KeyGenerator`.

Control flow: setup creates a temp dir. Tests write/read legacy writable storage with two tokens and ten HMAC keys, proto empty/non-empty credentials, stream empty/non-empty credentials, sequential proto records for writable compatibility, duplicate handling in `addAll` and `mergeAll`, and token transfer into a remote UGI.

State and persistence: temporary files under `GenericTestUtils.getTestDir("mapred")`, in-memory token maps and secret-key maps, static token/service/secret arrays.

Dependencies/integration points: Hadoop security token storage formats, Java crypto HMAC key generation, filesystem streams, UGI credential container.

Risks: temp directory cleanup only deletes the directory, not recursively; random generated keys require byte equality; serialization compatibility is broad but does not test malformed input.

Test signals: confirms token/key counts and values survive all supported encodings, overwrite vs preserve semantics differ between `addAll` and `mergeAll`, and UGI stores exact token instances.
