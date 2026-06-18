# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/wrappedio/package-info.java

## Purpose

This package descriptor defines the role of `org.apache.hadoop.io.wrappedio`: dynamic access to filesystem operations absent from older Hadoop releases.

## Important APIs, control flow, and state

It contains no runtime logic or state. The documentation states that public classes in the package export methods to be loaded by reflection and that tests should use reflection to guarantee the compatibility surface remains stable.

## Dependencies and integration points

The package holds `WrappedIO` and `WrappedStatistics`. It is annotated `@InterfaceAudience.Public` and `@InterfaceStability.Evolving`, so it is a deliberate public compatibility layer rather than a private helper.

## Risks and test signals

The main risk is changing method names or signatures and breaking reflection clients. `TestWrappedIO` and `TestWrappedStatistics` explicitly check method resolution and missing-method behavior, which are the right package-level signals.
