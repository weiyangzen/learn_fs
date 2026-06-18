<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/SignerSecretProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/SignerSecretProvider.java

## Purpose
Defines the abstraction that supplies signing secrets to `Signer`, allowing fixed, file, random, ZooKeeper-backed, and custom providers.

## Important APIs, types, and functions
`init(Properties, ServletContext, long)` initializes provider state using filter configuration and token validity. `destroy()` is a lifecycle hook. `getCurrentSecret()` returns the secret for new signatures. `getAllSecrets()` returns every still-valid secret for verification.

## Control flow
Subclasses implement initialization and secret retrieval. The base class only supplies a no-op destroy.

## State and persistence
No base state exists. Subclasses decide whether secrets are in-memory only, file-backed, or ZooKeeper-backed.

## Dependencies and integration points
Used by `Signer` and selected by `AuthenticationFilter`. Accepts servlet context so providers can share clients or externally supplied objects.

## Risks and test signals
The contract says current secret should never be null and callers should not mutate returned arrays, but this is not enforced. Tests for each implementation should verify non-null current secret, all-secrets includes current, lifecycle cleanup, and mutation isolation or documented mutability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/SignerSecretProvider.java -->
