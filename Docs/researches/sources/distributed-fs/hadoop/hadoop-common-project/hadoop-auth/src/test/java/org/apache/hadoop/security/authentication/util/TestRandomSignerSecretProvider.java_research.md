# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestRandomSignerSecretProvider.java

Purpose: Tests `RandomSignerSecretProvider` rollover scheduling and secret-array semantics using deterministic random seeds.

Important APIs and control flow: a spy subclass overrides `rollSecret()` as a no-op so Mockito can verify the scheduler calls it, while `realRollSecret()` delegates to `super.rollSecret()` for controlled state transitions. The test predicts three 32-byte secrets from a seeded `Random`, initializes the provider with a 250 ms rollover frequency, verifies initial current/previous slots, waits for scheduled roll invocations with Mockito `timeout`, then manually rolls and validates current and previous secret positions.

State and dependencies: state includes scheduled background rollover, current/previous secret arrays, and deterministic RNG seed. Dependencies include Mockito spy/timeout, Log4j level configuration, and JUnit.

Integration points: protects the `SignerSecretProvider` contract expected by `Signer`: current secret at index 0 and previous at index 1 during rollover windows.

Risks and test signals: scheduler timing is inherently flaky under heavy load, though the no-op override avoids races in state mutation. Seed from `System.currentTimeMillis()` is deterministic only within each run because expected secrets are generated from the same seed.
