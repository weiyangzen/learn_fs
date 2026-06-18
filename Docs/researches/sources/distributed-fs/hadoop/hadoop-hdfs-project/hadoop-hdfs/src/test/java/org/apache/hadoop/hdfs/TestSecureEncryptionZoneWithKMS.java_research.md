# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSecureEncryptionZoneWithKMS.java

Purpose: JUnit 5 integration coverage for HDFS encryption zones backed by a secure Kerberos MiniKMS and a secure MiniDFSCluster. It proves that encrypted file creation and encryption-zone creation keep working with KMS authentication, HTTPS-only HDFS endpoints, block access tokens, SASL retries, delegation-token forcing, and a deliberately small KMS encrypted-key cache.

Important APIs and types: `MiniKdc`, `MiniKMS`, `MiniDFSCluster`, `HdfsAdmin.createEncryptionZone`, `KMSClientProvider`, `KeyStoreTestUtil`, `UserGroupInformation.loginUserFromKeytabAndReturnUGI`, `UserGroupInformation.createProxyUser`, `FileSystemTestWrapper`, `DFSTestUtil.createKey`, and `DFSTestUtil.createFile`. The two tests are `testSecureEncryptionZoneWithKMS` and `testCreateZoneAfterAuthTokenExpiry`.

Control flow: `@BeforeAll init` creates a temp target directory, starts MiniKdc, generates principals/keytab, configures Kerberos, HTTPS, proxy-user mapping, KMS ACLs, and low auth-token validity, writes `kms-site.xml`, and starts MiniKMS. `@BeforeEach setup` starts a secure MiniDFSCluster using the KMS URI, creates the test key once, and prepares `FileSystem` and `HdfsAdmin`. The first test creates an EZ owned by a proxied Oozie user and creates three files to trigger KMS EDEK cache refill. The second logs in as hdfs, creates one zone, sleeps beyond auth token validity, and creates another zone to verify token refresh.

State and persistence behavior: State is mostly ephemeral test infrastructure in `baseDir`, generated keytab, keystore files, KMS keystore, MiniKMS service, and MiniDFSCluster metadata. `testKeyCreated` is static so repeated per-test clusters reuse the logical key without recreating it. No long-lived repository files are modified.

Dependencies and integration points: This test touches HDFS security configuration, KMS authentication, SSL config resources, DFS block-token/data-transfer protection, proxy users, KMS ACL enforcement, encryption-zone creation, and DFS client file creation in EZs.

Risks and test signals: It is sensitive to Kerberos hostname behavior, token-expiry timing, HTTPS keystore cleanup, and static key state across test methods. Passing tests signal that secure KMS/HDFS integration supports proxied encrypted writes and KMS auth-token renewal after expiration.
