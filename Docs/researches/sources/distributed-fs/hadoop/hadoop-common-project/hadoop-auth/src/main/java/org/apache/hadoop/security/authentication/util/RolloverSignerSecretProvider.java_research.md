<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/RolloverSignerSecretProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/RolloverSignerSecretProvider.java

## Purpose
Base class for signer-secret providers that rotate secrets while keeping the immediately previous secret valid for cookie verification.

## Important APIs, types, and functions
`init()` creates the initial secret and starts a scheduled rollover. `initSecrets()` initializes `{current, previous}`. `startScheduler()` starts a single-thread fixed-rate executor. `rollSecret()` generates a new secret and shifts the old current secret into previous. `getCurrentSecret()` and `getAllSecrets()` expose secrets to `Signer`. `destroy()` shuts down the scheduler.

## Control flow
Subclasses implement `generateNewSecret()`. The scheduler first runs after `tokenValidity` milliseconds and then repeats at the same period. Reads observe a volatile `byte[][]` so sign/verify callers see atomically replaced secret arrays.

## State and persistence
State is in-memory only: current/previous secret array, scheduler, and lifecycle booleans. There is no durable persistence in this base class.

## Dependencies and integration points
Extended by `RandomSignerSecretProvider` and `ZKSignerSecretProvider`. Used by `Signer` through the `SignerSecretProvider` contract.

## Risks and test signals
Risks include scheduler thread lifecycle leaks, invalid token-validity values, null secrets from subclasses, returning mutable secret arrays, and lack of `awaitTermination()` on destroy. Tests should cover rollover timing, previous-secret verification, repeated destroy, concurrent reads during rollover, and subclass null-secret failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/RolloverSignerSecretProvider.java -->
