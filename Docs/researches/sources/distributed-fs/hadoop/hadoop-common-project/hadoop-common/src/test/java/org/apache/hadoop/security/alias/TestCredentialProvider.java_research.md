# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/alias/TestCredentialProvider.java

Purpose: narrowly tests credential entry value storage and nested provider URI unwrapping.

Important APIs and types: `CredentialProvider.CredentialEntry`, `ProviderUtils.unnestUri`, `Path`, `URI`, and JUnit equality/array assertions.

Control flow: `testCredentialEntry` creates an entry with alias `cred1` and a char-array credential, then asserts alias and array contents. `testUnnestUri` checks that nested provider URIs are converted into the expected Hadoop `Path`, including HDFS authorities, query/fragment retention, nested schemes with multiple `@` separators, and `user:///` handling.

State and persistence: no durable state; all objects are in-memory.

Dependencies and integration points: supports the broader credential provider factory by verifying URI normalization used by keystore-backed provider paths.

Risks: URI unnesting behavior is subtle and can regress with changes to URI parsing around authority, path, query, or fragments. The credential entry test does not check defensive copying of char arrays.

Test signals: focused signal for simple alias/credential accessors and provider URI conversion rules.
