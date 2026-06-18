# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/resolver/TestInitializeMountTableResolver.java

## Purpose
This test validates `MountTableResolver` default nameservice initialization from configuration, including explicit disablement.

## Important APIs, Types, and Functions
It constructs `MountTableResolver` with `Configuration` values for `DFS_ROUTER_DEFAULT_NAMESERVICE`, `DFS_ROUTER_DEFAULT_NAMESERVICE_ENABLE`, `DFS_NAMESERVICE_ID`, and `DFS_NAMESERVICES`, then checks `getDefaultNamespace()` and `isDefaultNSEnable()`.

## Control Flow
Tests cover no configured default, an explicitly empty default string, a router default nameservice value, and a disabled default namespace even when HDFS nameservice settings are present. Empty string is expected to disable default namespace routing.

## State and Persistence
Only resolver initialization state is used. There is no mount table, cache mutation, or state-store persistence.

## Dependencies and Integration Points
The test depends on HDFS client configuration keys and router configuration keys. It protects router startup behavior for mount-table resolution before any state-store entries are loaded.

## Risks and Test Signals
The class only tests initialization, not later changes through setters. Passing tests signal that missing or disabled defaults produce an empty namespace, explicit empty defaults disable fallback routing, and configured router defaults are honored.
