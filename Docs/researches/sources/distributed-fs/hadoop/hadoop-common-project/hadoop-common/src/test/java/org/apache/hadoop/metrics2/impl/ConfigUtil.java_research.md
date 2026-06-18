# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/ConfigUtil.java

## Purpose

`ConfigUtil` is a package-private metrics2 test utility for dumping Commons configurations and asserting two configurations contain exactly the same keys and values.

## Important APIs, Types, And Functions

It provides `dump(Configuration)`, `dump(String, Configuration)`, `dump(String, Configuration, PrintWriter)`, and `assertEq(Configuration expected, Configuration actual)`.

## Control Flow

`dump()` copies the input into a `PropertiesConfiguration`, optionally prints a header, and writes it to the supplied writer. `assertEq()` iterates expected keys to assert presence/value equality in actual, then iterates actual keys to reject extras.

## State And Persistence Behavior

The utility has no persistent state. `dump()` writes to a `PrintWriter` provided by caller or `System.out`; `assertEq()` only reads configurations.

## Dependencies And Integration Points

It integrates with Commons Configuration and JUnit assertions. `TestMetricsConfig` uses `assertEq()` to validate merged and instance-specific metrics configuration behavior.

## Risks And Test Signals

Risks include value equality differences for list-valued properties and iterator ordering assumptions for debug output. Signals are precise missing-key, mismatched-value, and extra-key assertions in config tests.
