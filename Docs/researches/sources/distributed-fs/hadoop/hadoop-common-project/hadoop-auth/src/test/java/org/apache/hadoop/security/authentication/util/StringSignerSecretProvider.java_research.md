# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/StringSignerSecretProvider.java

Purpose: Test-only `SignerSecretProvider` implementation that derives a single signing secret from the `AuthenticationFilter.SIGNATURE_SECRET` string property.

Important APIs and control flow: `init(Properties, ServletContext, long)` reads `signatureSecret`, converts it to UTF-8 bytes, stores it in `secret`, and exposes it as a one-element `byte[][] secrets`. `getCurrentSecret()` returns the current byte array; `getAllSecrets()` returns the one-element array. There is no rollover, destruction, validation, or servlet-context behavior.

State and dependencies: state is two fields, `secret` and `secrets`, both initialized once. It depends on Hadoop classification annotations, `AuthenticationFilter`, servlet context type, and `StandardCharsets.UTF_8`.

Integration points: used by signer tests and created through `StringSignerSecretProviderCreator` because the class is package-private. It models the simplest static-secret provider contract used by `Signer`.

Risks and test signals: missing `SIGNATURE_SECRET` would throw a null dereference during `getBytes`, so callers must configure it. The provider returns internal byte arrays directly, matching test utility simplicity but not defensive-copy behavior. Its stability annotations mark it visible/testing and unstable, so production code should not depend on it.
