# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/LocalBouncyCastleFipsKeyStoreProvider.java

Purpose: local-filesystem credential provider using Bouncy Castle FIPS keystore format.

Important APIs/types/functions: constants `SCHEME_NAME=localbcfks`, `KEYSTORE_TYPE=bcfks`, and `ALGORITHM=HMACSHA512`; overrides inherited hooks; factory creates provider for `localbcfks://` URIs.

Control flow: factory match constructs the provider. `LocalKeyStoreProvider` resolves the local file URI, handles local streams and permissions, while `AbstractJavaKeyStoreProvider` handles keystore loading and credential operations.

State/persistence: no fields beyond inherited local file, permissions, keystore, and changed flag. Persists to a local BCFKS file on flush.

Dependencies/integration: BCFKS-capable Java security provider, `LocalKeyStoreProvider`, ServiceLoader factory, and local filesystem permission APIs or Windows winutils.

Risks: fails if BCFKS support is unavailable; local permission restoration differs between POSIX and Windows; `localbcfks` URI must unnest to a valid file URI. Test signals include factory selection, provider availability, local create/open/flush, permission preservation, and password-required behavior.
