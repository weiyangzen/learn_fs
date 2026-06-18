# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestMalformedURLs.java

## Purpose
Regression test that malformed/untrimmed URL-like configuration values in `hdfs-site.malformed.xml` are read and trimmed correctly enough for `MiniDFSCluster` startup.

## Important APIs, Types, and Functions
- Adds default resource `hdfs-site.malformed.xml`.
- Compares `Configuration.get` and `Configuration.getTrimmed` for `DFS_NAMENODE_HTTP_ADDRESS_KEY`.
- Starts `MiniDFSCluster` from the loaded `Configuration`.

## Control Flow
- `setUp` registers the malformed config resource and creates a fresh `Configuration`.
- `testTryStartingCluster` verifies the raw and trimmed values differ, then builds and activates a cluster.
- `tearDown` shuts down the cluster if startup succeeded.

## State and Persistence Behavior
- No filesystem persistence is intentionally inspected; the key state is configuration parsing and cluster process state.

## Dependencies and Integration Points
- Relies on a test resource named `hdfs-site.malformed.xml` on the test classpath.
- Integrates configuration parsing with NameNode HTTP address binding during mini-cluster startup.

## Risks and Edge Cases
- Only validates one configured key and successful startup, not all malformed URL handling paths.
- Global `Configuration.addDefaultResource` can affect later tests in the same JVM if resource loading behavior changes.

## Test Signals
- Compact startup smoke test for trimming and tolerance of malformed-looking NameNode HTTP address configuration.
