# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/AlreadyClosedException.java

## Purpose

`AlreadyClosedException.java` defines an `IOException` subtype thrown when code attempts to use a closed Hadoop compressor or decompressor.

## Important APIs, types, and functions

- `AlreadyClosedException` extends `IOException`.
- The constructor accepts a message and passes it to `IOException`.

## Control flow

There is no local control flow beyond exception construction. Compressor/decompressor implementations throw it from their own state checks after close/end operations.

## State and persistence behavior

The exception stores only standard `Throwable` message/cause state inherited from `IOException`. It has no serialization contract beyond Java exception serialization and no `serialVersionUID`.

## Dependencies and integration points

It depends on `IOException` and is documented against Hadoop `Compressor` and `Decompressor` interfaces. It gives callers a specific checked exception type for closed-resource misuse.

## Risks and edge cases

- The class name is precise, but the javadoc contains a typo: "decopressor".
- There is no cause-taking constructor, so wrappers must use `initCause()` if they need causal chaining.
- Callers catching only generic `IOException` may not distinguish closed-state bugs from IO failures.

## Test signals

Tests should verify compressor/decompressor methods throw this exception after close/end, message contents are preserved, and repeated close/end calls follow the intended idempotence or failure contract of each implementation.
