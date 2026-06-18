# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/package-info.java

## Purpose
This package descriptor marks server-side registry components.

## Important APIs and types
It describes server-only or test-JVM components such as server-side ZooKeeper support, DNS support, and potential REST services.

## Control flow
There is no executable code.

## State and persistence behavior
Server components in this package family generally manage ZooKeeper-backed registry persistence or in-memory services derived from it.

## Dependencies and integration points
The package boundary separates deployed server/test support from registry client APIs and data types.

## Risks and test signals
Packaging tests should ensure client artifacts do not accidentally depend on server-only classes unless intended.
