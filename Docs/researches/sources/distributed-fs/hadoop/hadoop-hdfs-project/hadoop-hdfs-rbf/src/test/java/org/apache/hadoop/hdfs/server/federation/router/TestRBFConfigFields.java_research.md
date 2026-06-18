# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRBFConfigFields.java

## Purpose

`TestRBFConfigFields` is a configuration consistency test. It compares Java constants in `RBFConfigKeys` against `hdfs-rbf-default.xml` and fails on missing properties in either direction.

## Important APIs, types, and functions

The class extends `TestConfigurationFieldsBase` and overrides `initializeMemberVariables()`. It sets `xmlFilename` to `hdfs-rbf-default.xml`, `configurationClasses` to `RBFConfigKeys.class`, and enables both `errorIfMissingConfigProps` and `errorIfMissingXmlProps`.

## Control flow

There are no local `@Test` methods because the inherited base class drives the comparison. Initialization also creates skip sets and excludes dynamic fair-handler prefixes: `DFS_ROUTER_FAIR_HANDLER_COUNT_KEY_PREFIX` and `DFS_ROUTER_FAIR_HANDLER_PROPORTION_KEY_PREFIX`.

## State and persistence behavior

The test reads configuration metadata from class constants and XML resources. It does not mutate runtime Router state or the state store.

## Dependencies and integration points

This file integrates RBF config definitions with Hadoop's shared config-field test framework. It ensures default XML documentation and code constants remain synchronized.

## Risks and test signals

The skip-prefix list is important because fair-handler keys are prefix families rather than concrete XML entries. A failure usually means a new RBF config key was added without XML documentation/defaults, an XML property lacks a Java constant, or a dynamic prefix needs explicit skip handling.
