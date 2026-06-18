# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestRolloverSignerSecretProvider.java

Purpose: Tests the abstract `RolloverSignerSecretProvider` base behavior using a deterministic subclass that returns a fixed sequence of byte-array secrets.

Important APIs and control flow: inner `TRolloverSignerSecretProvider` overrides `generateNewSecret()` to return `doctor`, `who`, then `tardis`. The test initializes with a 15-second rollover frequency, checks initial current secret and null previous slot, sleeps beyond each rollover interval, and verifies the two-secret window after each scheduled rollover.

State and dependencies: state is the provider’s scheduler plus current/previous secret array. Dependencies are JUnit and the base provider class. `destroy()` is called in a finally block to stop background scheduling.

Integration points: establishes the shared rollover contract inherited by random and ZooKeeper signer providers: current secret at `allSecrets[0]`, previous accepted secret at `allSecrets[1]`.

Risks and test signals: this is a slow timing test with sleeps of roughly 17 seconds per rollover, making it expensive and potentially flaky. It directly tests scheduler behavior rather than using controlled manual rolls, so runtime delays can affect it.
