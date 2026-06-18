# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestFederationUtil.java

## Purpose

`TestFederationUtil` validates reflective resolver creation through `FederationUtil`. It ensures RBF can instantiate configured resolver classes both with and without optional contextual objects.

## Important APIs, types, and functions

`testInstanceCreation()` uses `HdfsConfiguration`, config keys `FEDERATION_NAMENODE_RESOLVER_CLIENT_CLASS` and `FEDERATION_FILE_RESOLVER_CLIENT_CLASS`, `MockResolver`, `ActiveNamenodeResolver`, `FileSubclusterResolver`, `StateStoreService`, and `Router`. It calls `FederationUtil.newActiveNamenodeResolver(conf, stateStore)`, `FederationUtil.newActiveNamenodeResolver(conf, null)`, `FederationUtil.newFileSubclusterResolver(conf, router)`, and `FederationUtil.newFileSubclusterResolver(conf, null)`.

## Control flow

The test registers `MockResolver` as both the namenode resolver implementation and file-subcluster resolver implementation. It then constructs resolver instances through utility methods and asserts all returned references are non-null. It does not start Router services.

## State and persistence behavior

No state store persistence is exercised. The supplied `StateStoreService` and `Router` are constructor-context probes: the test checks that resolver construction paths can tolerate both present and missing context.

## Dependencies and integration points

This file touches resolver extension wiring, especially the constructor-selection behavior in `FederationUtil`. It is an integration point for pluggable resolver classes and the config keys that bind them.

## Risks and test signals

The test will catch obvious reflection or constructor signature regressions, but it does not assert exact class identity, initialized state, or resolver behavior after construction. Failures here indicate resolver bootstrap breakage rather than runtime federation routing problems.
