# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/alias/TestCredentialProviderFactory.java

Purpose: validates provider discovery, error handling, credential CRUD/persistence, password lookup fallback, UGI-backed secret storage, keystore file permissions, and unsupported local BCFKS creation.

Important APIs and types: `CredentialProviderFactory`, `CredentialProvider`, `UserProvider`, `JavaKeyStoreProvider`, `LocalJavaKeyStoreProvider`, `LocalBouncyCastleFipsKeyStoreProvider`, `ProviderUtils.unnestUri`, `Configuration.getPassword`, `CredentialProvider.CLEAR_TEXT_FALLBACK`, `Credentials`, `UserGroupInformation`, `FileSystem`, `FileStatus`, `FsPermission`, and `Path`.

Control flow: `testFactory` configures `user:///` plus JKS provider URIs and asserts provider order, classes, and string forms. Error tests assert precise messages for unknown scheme and malformed URI. `checkSpecificProvider` performs common CRUD: missing credential checks, create, duplicate create failure, delete, missing delete failure, create two credentials, flush, `Configuration.getPassword` lookup through provider, clear-text fallback behavior, reload from provider, and alias list. `testUserProvider` verifies UGI credentials receive secret keys. JKS/local JKS tests assert keystore file creation with `rw-------`, then chmod to `777` and verify permission retention after flush. BCFKS test expects `IOException("Can't create keystore")`.

State and persistence: writes keystore files under `GenericTestUtils.getTestDir("creds")`, changes filesystem permissions, and mutates current user's UGI credentials for user provider tests.

Dependencies and integration points: integrates provider path parsing, filesystem APIs, Hadoop configuration password lookup, local and file-based keystores, permissions, and UGI credential storage.

Risks: random password generation is nondeterministic but only used for equality after round trip. File permission checks may vary on filesystems that do not preserve POSIX permissions. Current-user credentials are global to the test JVM. BCFKS behavior depends on crypto provider availability.

Test signals: strong coverage for provider resolution, persistent keystore semantics, permission creation/retention, config password fallback policy, and UGI secret integration.
