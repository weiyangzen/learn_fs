# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestStringSignerSecretProvider.java

Purpose: Minimal unit test for `StringSignerSecretProvider`, checking that a configured string secret is exposed as the current and only signing secret.

Important APIs and control flow: the test creates a provider, sets `AuthenticationFilter.SIGNATURE_SECRET` to `secret`, calls `init`, and asserts `getCurrentSecret()` and `getAllSecrets()[0]` match `secret.getBytes()`, with exactly one available secret.

State and dependencies: state is a one-element byte-array secret. Dependencies are JUnit and `AuthenticationFilter`.

Integration points: supports `Signer` tests and validates the test-only static provider contract.

Risks and test signals: expected bytes use platform default charset while the provider itself uses UTF-8; ASCII `secret` avoids differences. It does not test null/missing secret behavior.
