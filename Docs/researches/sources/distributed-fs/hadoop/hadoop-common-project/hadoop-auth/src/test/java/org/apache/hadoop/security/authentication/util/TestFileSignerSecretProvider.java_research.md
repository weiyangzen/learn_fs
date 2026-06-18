# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestFileSignerSecretProvider.java

Purpose: Unit tests for `FileSignerSecretProvider`, ensuring secrets can be loaded from a configured file and that empty secret files fail fast.

Important APIs and control flow: `testGetSecrets` creates `target/test-dir/http-secret.txt` under `test.build.data` fallback, writes `hadoop`, initializes the provider with `AuthenticationFilter.SIGNATURE_SECRET_FILE`, then checks `getCurrentSecret()` and `getAllSecrets()`. `testEmptySecretFileThrows` creates an empty temp file and expects `RuntimeException` during `init`, with a message starting `No secret in signature secret file:`.

State and dependencies: state is filesystem-backed secret content and provider byte arrays. Dependencies include Java `FileWriter`, JUnit assertions, and `AuthenticationFilter` configuration keys.

Integration points: covers static secret file loading for authentication cookie signing. The one-element all-secrets result confirms no rollover or previous-secret support in this provider.

Risks and test signals: the first test does not clean up the generated file, relying on build temp-directory lifecycle. It uses platform default charset for expected bytes and file writing, unlike the string provider’s UTF-8, which can matter on unusual default encodings.
