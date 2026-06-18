# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/wrappedio/impl/package-info.java

## Purpose

This package descriptor documents `org.apache.hadoop.io.wrappedio.impl` as implementation and testing support for wrapped IO.

## Important APIs, control flow, and state

It contains no executable code or state. It applies `@InterfaceAudience.LimitedPrivate("testing")` and `@InterfaceStability.Unstable` to the implementation package.

## Dependencies and integration points

The package contains `DynamicWrappedIO` and `DynamicWrappedStatistics`, which are used by tests and compatibility callers. The descriptor depends only on Hadoop classification annotations.

## Risks and test signals

The risk is API expectation drift: classes in this package are not promised as stable public APIs even though they are useful for compatibility tests. Package-level annotation behavior is indirectly validated by compilation and javadoc/classification checks.
