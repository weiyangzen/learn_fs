# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/InvalidChecksumSizeException.java

## Purpose

`InvalidChecksumSizeException` is an `IOException` raised when checksum metadata has an invalid bytes-per-checksum value or invalid checksum type.

## Important APIs, Types, And Functions

The class only provides `InvalidChecksumSizeException(String s)` and a `serialVersionUID`.

## Control Flow, State, And Persistence

It carries only the inherited exception message and stack trace. No mutable state or persistence is involved.

## Dependencies And Integration Points

It depends on `java.io.IOException` and integrates with checksum/meta-file parsing code that must distinguish malformed checksum configuration from other I/O failures.

## Risks And Test Signals

The class has no cause-taking constructor, so callers lose causal chaining unless they encode it in the message. Tests should assert it is catchable as `IOException` and preserves messages for invalid checksum metadata paths.
