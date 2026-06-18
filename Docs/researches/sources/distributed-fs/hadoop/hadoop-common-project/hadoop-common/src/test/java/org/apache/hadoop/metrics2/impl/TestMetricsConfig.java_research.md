# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/TestMetricsConfig.java

## Purpose

`TestMetricsConfig` validates metrics2 configuration loading, prefix scoping, wildcard defaults, instance extraction, missing-file behavior, load order, and comma-delimited values.

## Important APIs, Types, And Functions

The file uses `MetricsConfig.create(prefix, filenames...)`, `getInstanceConfigs(type)`, `ConfigBuilder`, `ConfigUtil.assertEq()`, and `getTestFilename(basename)`.

## Control Flow

`testCommon()` writes a properties file containing global defaults, prefix defaults, type defaults, and instance-specific values, creates a `MetricsConfig` for `p1`, asserts the scoped config, and delegates to `testInstances()`. Instance tests verify map sizes and default lookup fallbacks. Other tests assert missing files return an empty config, prefix-named default files load when available, explicit file load order works, and comma-delimited values become multiple properties.

## State And Persistence Behavior

The tests write `.properties` files under `test.build.classes` or `target/test-classes`. Configuration state is loaded from those files and in-memory Commons Configuration objects.

## Dependencies And Integration Points

It integrates Commons Configuration, Hadoop metrics2 config parsing, test config builder/utilities, and the classpath/test-build output directory convention used by metrics system tests.

## Risks And Test Signals

Risks include file collisions, wildcard/default precedence regressions, list delimiter changes, and accidentally treating missing files as fatal. Signals are exact scoped config equality, instance map counts, default lookup assertions, and split value equality.
