<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/RandomSignerSecretProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/RandomSignerSecretProvider.java

## Purpose
Provides rolling random secrets for signing Hadoop Auth cookies when no shared configured secret is supplied.

## Important APIs, types, and functions
Extends `RolloverSignerSecretProvider`. The default constructor uses `SecureRandom`; the testing constructor uses deterministic `Random(seed)`. `generateNewSecret()` returns a new 32-byte secret.

## Control flow
The superclass initializes a current secret and schedules rollover at token-validity intervals. Each rollover calls `generateNewSecret()` to replace current/previous secrets.

## State and persistence
State is the random generator and inherited in-memory secret array. Secrets are not persisted, so process restart invalidates existing cookies unless a shared provider is used.

## Dependencies and integration points
Used by `AuthenticationFilter` fallback secret-provider selection. Depends on Java random APIs and inherited scheduler behavior.

## Risks and test signals
Random fallback is not cluster-stable and can log users out across restart or load-balanced instances. Tests should cover generated length, deterministic seeded output, inherited rollover acceptance of previous secret, and restart invalidation expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/RandomSignerSecretProvider.java -->
