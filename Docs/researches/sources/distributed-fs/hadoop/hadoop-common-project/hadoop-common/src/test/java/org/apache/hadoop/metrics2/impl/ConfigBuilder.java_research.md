# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/ConfigBuilder.java

## Purpose

`ConfigBuilder` is a test helper for constructing Apache Commons `PropertiesConfiguration` instances fluently and saving them to metrics2 config files.

## Important APIs, Types, And Functions

The class exposes public final `config`, constructor initialization with `DefaultListDelimiterHandler(',')`, `add(String,Object)`, `save(String)`, and `subset(String)`.

## Control Flow

Tests create a builder, chain `add()` calls to append properties, optionally call `save()` to write a properties file, or call `subset(prefix)` to return a `SubsetConfiguration` with `.` delimiter. `save()` wraps any write failure in `RuntimeException`.

## State And Persistence Behavior

State is the mutable `PropertiesConfiguration`. `save()` persists the configuration to a filename with `FileWriter`; callers are responsible for target directories and cleanup. The list delimiter makes comma-separated values split consistently in metrics config tests.

## Dependencies And Integration Points

It integrates with Commons Configuration and is used across metrics tests for filters, metrics-system setup, Ganglia sinks, and config parsing.

## Risks And Test Signals

Risks include unclosed writer behavior, target-file collisions in shared test classpaths, and delimiter changes affecting list-valued tests. It is itself a helper, so signals come from dependent tests successfully loading saved configs and subset views.
