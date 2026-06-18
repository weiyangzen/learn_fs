# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/TestKeyProviderFactory.java

## Purpose
`TestKeyProviderFactory` validates provider discovery, provider CRUD semantics, user-provider credential persistence, JCEKS persistence and recovery, keystore permissions, password-file handling, direct URI lookup, and behavior with keytool-created keystores.

## Important APIs, Types, and Functions
The suite exercises `KeyProviderFactory.getProviders`, `KeyProviderFactory.get`, `UserProvider`, `JavaKeyStoreProvider`, `FailureInjectingJavaKeyStoreProvider`, `KeyProvider` CRUD methods, `ProviderUtils.unnestUri`, `FileSystem` status/permissions, and `UserGroupInformation` credentials. `checkSpecificProvider()` is the shared provider contract for missing keys, create/delete/recreate, wrong key lengths, roll, flush, reload, key listing, and version listing.

## Control Flow
Factory tests parse comma-separated provider paths and error on unknown or malformed URIs. `testUserProvider()` runs the shared contract and then verifies secret keys landed in current-user credentials. `testJksProvider()` creates a file-backed JCEKS provider, runs the shared contract, injects flush failures, verifies state rollback, checks file mode, tests recovery from `_OLD` and `_NEW` files, validates conflict handling when current and `_NEW` coexist, tests permission retention, and rejects uppercase key names. Password tests create a keystore with a configured password file and verify bad/missing password settings fail. URI and keytool tests check direct factory lookup and error handling for non-Hadoop keytool entries.

## State and Persistence
The test writes real keystore files under a `FileSystemTestHelper` temp root. It manipulates current, `_OLD`, and `_NEW` keystore files, filesystem permissions, and current-user credentials. Provider flush/reload boundaries are central to the persistence contract.

## Dependencies and Integration Points
Dependencies include local `FileSystem`, `FileStatus`, `FsPermission`, `Path`, `Configuration`, `ProviderUtils`, `UserGroupInformation`, `Credentials`, test keystore resource `hdfs7067.keystore`, and the failure-injecting provider factory.

## Risks and Edge Cases
High-risk behavior includes crash recovery around `_NEW`/`_OLD`, rollback after failed flush, file permission preservation, uppercase key-name rejection, password file discovery, and compatibility with keystores containing non-Hadoop secret-key entries. The write-failure helper has a suspicious setter bug, so failure-injection coverage should be interpreted carefully.

## Test Signals
Passing tests signal provider path parsing, user and JCEKS key lifecycle correctness, durable reload after flush, credential storage, recovery file handling, permission retention, password-file enforcement, direct URI provider lookup, and defensive errors for incompatible keytool entries.
