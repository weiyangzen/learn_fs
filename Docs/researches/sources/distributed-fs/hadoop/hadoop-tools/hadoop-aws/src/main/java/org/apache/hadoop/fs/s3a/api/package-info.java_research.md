# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/api/package-info.java

## Purpose
This package descriptor defines `org.apache.hadoop.fs.s3a.api` as the home for interfaces implemented in S3A internals but exposed to S3A extensions without requiring access to `.impl` packages.

## Important APIs and control flow
There is no executable logic. The package is LimitedPrivate to extensions and unstable. The documentation explicitly warns that public extension points may change.

## State, dependencies, and integration
No state is present. Dependencies are Hadoop classification annotations. The package is an integration boundary for `RequestFactory`, performance flags, and request exceptions.

## Risks and test signals
Risk is accidental reliance by downstream extensions on unstable implementation details. Compatibility tests should focus on intended extension APIs rather than internal implementation classes.
