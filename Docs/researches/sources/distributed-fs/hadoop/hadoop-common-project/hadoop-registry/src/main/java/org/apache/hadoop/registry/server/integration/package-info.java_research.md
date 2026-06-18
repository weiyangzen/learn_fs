# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/integration/package-info.java

## Purpose
This package descriptor identifies classes that integrate the registry server with the YARN resource manager.

## Important APIs and types
In this subset, the main class is `SelectByYarnPersistence`, a selector useful for YARN lifecycle cleanup.

## Control flow
No executable code is present.

## State and persistence behavior
The package works with persistent service-record attributes to decide lifecycle actions, but this descriptor stores no state.

## Dependencies and integration points
Integration is between YARN lifecycle identifiers/policies and registry server administration.

## Risks and test signals
End-to-end cleanup tests should verify that YARN application, attempt, and container completion events translate into correct selector criteria and registry deletions.
