# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/package-info.java

## Purpose
This package descriptor marks `org.apache.hadoop.fs.s3a.audit.impl` as the internal implementation package for S3A auditing.

## Important APIs and control flow
There is no executable code. The package is annotated private and unstable, and documentation states it is not for extension use.

## State, dependencies, and integration
No state is present. Dependencies are Hadoop audience/stability annotations. Public extension contracts should live in `org.apache.hadoop.fs.s3a.audit`, not here.

## Risks and test signals
Downstream code depending on this package is brittle. Compatibility checks should focus on public audit interfaces while internal tests can freely exercise implementation details.
