# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/random/TestOsSecureRandom.java

## Purpose
`TestOsSecureRandom` verifies the OS-backed secure-random implementation on Linux, including changing output for bytes/primitives and reservoir refill behavior.

## Important APIs, Types, and Functions
`getOsSecureRandom()` assumes Linux, creates `OsSecureRandom`, and calls `setConf(new Configuration())`. Tests call `nextBytes`, `nextInt`, `nextLong`, `nextFloat`, `nextDouble`, `close`, and the repeated `nextLong` path that refills the internal reservoir.

## Control Flow
Each randomness test creates a configured random source, obtains two values, loops until they differ, then closes the random. `testRefillReservoir()` calls `nextLong()` 8196 times to exceed the reservoir capacity and exercise refill without validating individual values.

## State and Persistence
The implementation owns an OS random stream that must be closed. Test data stays in memory; no durable files are created by the test itself.

## Dependencies and Integration Points
Dependencies include `OsSecureRandom`, Hadoop `Configuration`, Apache Commons `SystemUtils.IS_OS_LINUX`, JUnit assumptions/timeouts, and Java arrays.

## Risks and Edge Cases
The suite only runs on Linux. Like the OpenSSL random tests, it is a constant-output smoke test rather than statistical validation. The refill test guards a long-running internal state path and could reveal stream or reservoir boundary bugs.

## Test Signals
Passing tests signal Linux-only OS random initialization, non-constant byte and primitive output, close behavior after use, and reservoir refill stability.
