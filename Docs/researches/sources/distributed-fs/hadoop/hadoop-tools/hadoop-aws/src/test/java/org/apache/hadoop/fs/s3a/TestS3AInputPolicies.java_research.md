# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AInputPolicies.java

## Purpose

Parameterized unit test for `S3AInputStream.calculateRequestLimit()` under normal, sequential, and random input policies.

## Important APIs, Types, and Functions

The test uses `S3AInputPolicy` enum values and feeds target position, requested length, content length, readahead, and expected request limit into `calculateRequestLimit()`.

## Control Flow

`data()` enumerates cases for unknown length, zero content length, full-file reads, explicit read lengths, readahead-limited random reads, zero/one-byte reads under random policy, and target positions past object length. The parameterized test initializes fields and asserts the calculated limit equals the expected value with a detailed argument string.

## State, Dependencies, and Integration Points

No external state or S3 calls. It integrates directly with S3A input stream range-planning logic and JUnit parameterized tests.

## Risks and Test Signals

The matrix documents range-request semantics. It catches regressions where random policy over-fetches or under-fetches, normal/sequential policy fails to read to object end, or out-of-range positions are not capped at content length.
