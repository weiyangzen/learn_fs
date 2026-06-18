# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/LocalJavaKeyStoreProvider.java

Purpose: local-filesystem credential provider using Java JCEKS keystore format.

Important APIs/types/functions: constants `SCHEME_NAME=localjceks`, `KEYSTORE_TYPE=jceks`, and `ALGORITHM=AES`; factory creates instances for `localjceks://` provider URIs.

Control flow: URI selection happens in the nested factory. Local file resolution, zero-length handling, permission stashing/restoration, keystore load/create, credential mutation, and flush are inherited from `LocalKeyStoreProvider` and `AbstractJavaKeyStoreProvider`.

State/persistence: inherited state only. Persists credentials to a local JCEKS file after `flush`.

Dependencies/integration: Java JCEKS keystore support, local filesystem, Hadoop credential provider path config, and ServiceLoader.

Risks: local file URI syntax must be valid; default password remains weak; JCEKS has legacy security properties; permission behavior varies on Windows. Test signals include creating a new local keystore, loading existing non-empty keystore, ignoring zero-length file as missing, preserving permissions, and factory non-match on other schemes.
