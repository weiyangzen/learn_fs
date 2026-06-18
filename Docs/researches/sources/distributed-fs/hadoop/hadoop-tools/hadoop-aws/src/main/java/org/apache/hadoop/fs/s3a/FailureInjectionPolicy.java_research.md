# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/FailureInjectionPolicy.java

Purpose: compact holder for S3A test failure-injection settings.

Important APIs/types: `DEFAULT_DELAY_KEY_SUBSTRING`, `throttleProbability`, `failureLimit`, constructor reading `FAIL_INJECT_THROTTLE_PROBABILITY`, getters/setters, `trueWithProbability(float)`, `toString()`, and private probability validation.

Control flow: construction reads config and validates probability in range `[0.0, 1.0]`. Callers can mutate failure limit and throttle probability. `trueWithProbability` uses `Math.random()` to decide whether to inject a failure.

State and persistence behavior: in-memory mutable policy values only; no persistence.

Dependencies and integration points: consumes S3A constants and Hadoop `Configuration`; intended for tests and failure-injecting client factories.

Risks: `Math.random()` makes behavior nondeterministic unless probability is 0 or 1. Validation throws on out-of-range config, which is useful for tests but can fail client setup.

Test signals: tests should assert probability bounds, configured throttle probability, failure limit mutation, and deterministic behavior at probabilities 0 and 1.
