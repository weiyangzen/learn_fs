<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/SaslDataTransferTestCase.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/SaslDataTransferTestCase.java

Purpose: Shared fixture for SASL data-transfer tests that need Kerberos principals, keytabs, and HTTPS-only secure HDFS configuration.

Important APIs/types/functions: `MiniKdc`, `KeyStoreTestUtil`, `SecurityUtil.setAuthenticationMethod`, `createSecureConfig`, and getters for generated user/HDFS keytabs and principals.

Control flow: `initKdc` creates a test directory, starts MiniKdc, generates a random user principal and an `hdfs/localhost` plus `HTTP/localhost` principal, and stores keytab paths. `shutdownKdc` stops KDC, deletes base directory, and cleans SSL config. `createSecureConfig` sets Kerberos auth, NameNode/DataNode principals and keytabs, SPNEGO principal, block tokens, requested data transfer QOPs, HTTPS-only policy, ephemeral HTTPS addresses, SASL retry count, and SSL resources.

State and persistence behavior: Persists temporary keytab files, KDC state, and generated SSL config under test directories, then deletes them at suite end.

Dependencies and integration points: Used by SASL data-transfer integration tests to start secure `MiniDFSCluster` instances with realistic Kerberos and SSL settings.

Risks: Class-level static directories and SSL paths are shared by subclasses. Cleanup must run or credentials/config files can remain. MiniKdc startup can be environment-sensitive.

Test signals: Subclass success indicates this fixture produced valid principals, keytabs, SSL resources, and HDFS security configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/SaslDataTransferTestCase.java -->
