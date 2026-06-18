# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/package-info.java

## Purpose

This package descriptor documents the top-level `org.apache.hadoop.security` package.

## Important APIs, Types, and Functions

It applies `@InterfaceAudience.LimitedPrivate({"HDFS", "MapReduce", "YARN", "HBase"})` to the package.

## Control Flow

There is no executable control flow.

## State and Persistence Behavior

The file owns no state or persistence.

## Dependencies and Integration Points

It imports the Hadoop classification annotation and marks the package that contains UGI, security utilities, group mapping, SASL, credentials, and related security infrastructure.

## Risks and Edge Cases

The only substantive risk is stale audience metadata if top-level package exposure changes.

## Test Signals

Compilation and javadoc/package annotation generation are sufficient.
