# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestReencryptionWithKMS.java

Purpose: Runs the inherited `TestReencryption` suite against a real `MiniKMS` provider instead of the default local JKS provider, and adds a KMS ACL regression test. It is tagged slow.

Important APIs and functions: Overrides `getKeyProviderURI()` to return a `kms://` URI based on `miniKMS.getKMSUrl()`. `setup()` creates a unique KMS config directory, starts `MiniKMS`, then calls `super.setup()`. `setProvider()` is intentionally empty because the client provider should be the KMS provider. `rollKey()` rolls through `dfsAdmin.getKeyProvider()` without JKS flush.

Control flow: The inherited tests create encryption zones, roll keys, submit/cancel re-encryption, and inspect status through KMS. The local `testReencryptionKMSACLs()` edits `kms-acls.xml` to blacklist get/get_keys ACLs, reloads `KMSWebApp` ACLs, then runs `testReencryptionBasic()` to verify re-encryption does not require those reads.

State and persistence behavior: Persistent state includes the temporary MiniKMS keystore/config directory, KMS ACL XML, NameNode re-encryption status, and KMS key versions. Teardown stops both HDFS and KMS.

Dependencies and integration points: Integrates `MiniKMS`, `KMSClientProvider`, `KMSACLs`, `KMSConfiguration`, `KMSWebApp`, and the full HDFS re-encryption machinery inherited from `TestReencryption`.

Risks: This suite is slower and more environment-sensitive than JKS tests because it depends on an embedded KMS web service and ACL reload behavior. ACL changes must avoid over-constraining operations actually needed by re-encryption.

Test signals: Passing inherited re-encryption behavior through MiniKMS and passing basic re-encryption while GET and GET_KEYS ACLs are blacklisted show correct provider integration and minimal KMS permissions.
