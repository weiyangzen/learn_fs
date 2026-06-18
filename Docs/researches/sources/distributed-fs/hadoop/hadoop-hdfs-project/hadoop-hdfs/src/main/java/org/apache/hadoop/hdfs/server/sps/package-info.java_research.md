<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/package-info.java

## Purpose

This package-info describes the external/server SPS package as a mechanism for satisfying a path's storage policy.

## Important APIs and types

The package includes the external SPS process entry point, context, file collector, block move handler, and fault injector. It is annotated `@InterfaceAudience.Private` and `@InterfaceStability.Unstable`.

## Control flow

There is no executable code. The annotations communicate that the package is internal and unstable.

## State and persistence behavior

No state is defined in this file. State lives in the package classes and the HDFS namespace/block placement they manipulate.

## Dependencies and integration points

It depends only on Hadoop classification annotations and package-level Java metadata.

## Risks and test signals

Risk is documentation drift: the package has both external-process orchestration and block movement support. Javadoc/package annotation checks are the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/package-info.java -->
