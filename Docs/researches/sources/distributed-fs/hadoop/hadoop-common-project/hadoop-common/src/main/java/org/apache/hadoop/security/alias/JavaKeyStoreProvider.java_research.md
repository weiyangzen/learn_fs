# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/JavaKeyStoreProvider.java

Purpose: Hadoop `FileSystem` credential provider using Java JCEKS keystore format.

Important APIs/types/functions: constants `SCHEME_NAME=jceks`, `KEYSTORE_TYPE=jceks`, and `ALGORITHM=AES`; overrides scheme/type/algorithm hooks; nested `Factory` creates instances for `jceks://` URIs.

Control flow: provider URI is unnested by inherited logic, for example `jceks://hdfs@nn/path` becomes an HDFS path. Inherited `KeyStoreProvider` opens or creates the keystore through Hadoop `FileSystem`; inherited abstract provider handles aliases, credentials, password lookup, and flush.

State/persistence: no new fields; persistent credentials live in a JCEKS keystore at the target Hadoop filesystem path.

Dependencies/integration: Java JCEKS support, `KeyStoreProvider`, `CredentialProviderFactory`, Hadoop `FileSystem`, and service provider registration.

Risks: JCEKS is legacy compared with FIPS formats; default keystore password still applies if none configured; remote filesystem permissions and overwrite semantics come from `KeyStoreProvider`. Test signals include factory scheme selection, URI unnesting, JCEKS read/write, duplicate/missing alias behavior, and password source handling.
