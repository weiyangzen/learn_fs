# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/api/PerformanceFlagEnum.java

## Purpose
`PerformanceFlagEnum` declares symbolic performance flags for S3A extension points and filesystem behavior toggles.

## Important APIs and control flow
The enum values are `Create`, `Delete`, `Mkdir`, and `Open`, with a note that additions should remain alphabetically ordered. There is no behavior beyond enum identity.

## State, dependencies, and integration
The enum is LimitedPrivate to S3A filesystem and extensions and unstable. It depends only on Hadoop annotations. Consumers can use it in `EnumSet` or configuration parsing for feature/performance modes.

## Risks and test signals
Risk is compatibility: renaming or reordering can affect serialized names or configuration parsing. Tests should verify parsing of all expected flag names and behavior when unknown flags are supplied.
