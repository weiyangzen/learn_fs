# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/BouncyCastleFipsKeyStoreProvider.java

Purpose: Hadoop filesystem credential provider using Bouncy Castle FIPS keystore format.

Important APIs/types/functions: constants `SCHEME_NAME=bcfks`, `KEYSTORE_TYPE=bcfks`, and `ALGORITHM=HMACSHA512`; overrides scheme/type/algorithm hooks from `KeyStoreProvider`; nested `Factory` returns this provider when a configured URI uses the `bcfks` scheme.

Control flow: factory receives each configured provider URI from `CredentialProviderFactory`; matching scheme constructs the provider, which delegates path unnesting, filesystem setup, keystore loading/creation, and flush behavior to `KeyStoreProvider` and `AbstractJavaKeyStoreProvider`.

State/persistence: no additional fields beyond inherited keystore state. Persists credentials to the unnested Hadoop `FileSystem` path on flush.

Dependencies/integration: Java/Bouncy Castle provider availability for BCFKS keystore type and HMACSHA512 secret-key entries, Hadoop `FileSystem`, ServiceLoader registration of factory, and credential provider path config.

Risks: runtime must have BCFKS support installed; algorithm/type strings are provider-sensitive; remote filesystem writes inherit `KeyStoreProvider` overwrite and permission semantics. Test signals include ServiceLoader factory selection, BCFKS keystore creation/opening, missing provider failure, flush to HDFS/file URI, and password-required warnings.
