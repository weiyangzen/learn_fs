# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/resolver/TestFederationNamespaceInfo.java

## Purpose
This small regression test verifies `FederationNamespaceInfo` ordering/equality behavior when stored in a `TreeSet`, specifically for HDFS-15900.

## Important APIs, Types, and Functions
The test constructs two `FederationNamespaceInfo` instances with the same nameservice id but different block-pool and cluster/name fields, inserts them into a `TreeSet`, and uses AssertJ `assertThat(set).hasSize(2)`.

## Control Flow
`testHashCode()` first adds an instance with an empty block-pool id, then adds another with `bp1` but the same `ns1`. The assertion requires comparison/hash semantics to preserve both records rather than collapsing by nameservice alone.

## State and Persistence
All state is local to the test method. There is no resolver or state-store interaction.

## Dependencies and Integration Points
The test depends on Java collection semantics and the `FederationNamespaceInfo` comparable/hash implementation used by namespace sets in resolvers such as `MockResolver` and state-store-backed membership resolvers.

## Risks and Test Signals
The test is narrow by design. Passing it signals that empty block-pool ids do not cause namespace records to compare equal incorrectly, protecting namespace discovery and disabled-namespace filtering from losing records.
