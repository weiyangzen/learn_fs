# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/constants/ConfigConstants.java

## Purpose

`ConfigConstants` is a small final test-support constants holder for configuration keys used across Hadoop tests. It currently exposes the Avro serialization trusted-packages system property name.

## Important APIs and types

- `public final class ConfigConstants` with a private constructor to prevent instantiation.
- `CONFIG_AVRO_SERIALIZABLE_PACKAGES = "org.apache.avro.SERIALIZABLE_PACKAGES"`.

## Control flow

There is no runtime control flow beyond class loading. The private constructor enforces static-only usage.

## State and persistence behavior

The class contains a single immutable string constant and no mutable state or persistence behavior.

## Dependencies and integration points

The constant integrates tests with Avro's serialization package trust configuration. Keeping it centralized avoids string duplication across test code.

## Risks and edge cases

- The class is in test sources but documents an external dependency's system property; changes in Avro's property name would require coordinated updates.
- Because it is a constant, downstream references may inline the value at compile time.

## Test signals

The useful signal is compilation and use by tests that need to configure Avro trusted packages. There are no direct behavioral tests in this file.
