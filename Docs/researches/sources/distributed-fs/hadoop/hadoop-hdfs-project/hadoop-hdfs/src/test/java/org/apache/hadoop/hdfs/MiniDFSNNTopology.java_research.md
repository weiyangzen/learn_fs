# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/MiniDFSNNTopology.java

## Purpose
`MiniDFSNNTopology` is a small configuration model used by `MiniDFSCluster` to describe NameNode layouts for tests: single NameNode, HA, federation, and HA federation.

## Important APIs, Types, and Functions
- `simpleSingleNN(int nameNodePort, int nameNodeHttpPort)` creates one unnamed nameservice with one unnamed NN.
- `simpleHATopology()` and `simpleHATopology(int)` create one nameservice, `minidfs-ns`, with multiple NN IDs.
- `simpleHATopology(int nnCount, int basePort)` creates HA NNs with explicit alternating IPC/HTTP ports.
- `simpleFederatedTopology(int)` and `simpleFederatedTopology(String)` create federated single-NN nameservices.
- `simpleHAFederatedTopology(int)` creates multiple nameservices, each with two NNs.
- Instance methods include `setFederation`, `addNameservice`, `countNameNodes`, `getOnlyNameNode`, `isFederated`, `isHA`, `allHttpPortsSpecified`, `allIpcPortsSpecified`, and `getNameservices`.
- Nested `NSConf` stores nameservice ID plus a list of `NNConf`.
- Nested `NNConf` stores NN ID, HTTP port, IPC port, and optional cluster ID override.

## Control Flow
Factory methods build topologies by chaining `addNameservice` and `addNN`. `addNameservice` rejects empty nameservices. `isFederated` returns true when more than one nameservice exists or when the explicit federation flag is set. `isHA` scans for any nameservice with more than one NN. Port-specified checks scan all NNs for nonzero HTTP/IPC ports.

## State and Persistence Behavior
The object is an in-memory mutable builder-style model. It does not persist anything itself. Its state is later consumed by `MiniDFSCluster.configureNameNodes` and `configureNameService`, which translate IDs and ports into HDFS configuration keys and on-disk name/shared-edits directories.

## Dependencies and Integration Points
It uses Hadoop `Preconditions` and `Lists`. Its primary integration is `MiniDFSCluster.Builder.nnTopology(...)`; `MiniDFSCluster` depends on the topology to decide federation, HA, config keys, shared edits, formatting strategy, and default FS behavior.

## Risks and Edge Cases
- Several factory methods use `null` nameservice or NN IDs intentionally for non-federated/non-HA layouts; downstream code must tolerate these nulls.
- `simpleFederatedTopology(String)` splits on commas without trimming, so whitespace in input becomes part of nameservice IDs.
- The `federation` boolean can force federated behavior even with one nameservice.
- Default ports are zero, meaning ephemeral ports; HA checkpoint/log-roll behavior may be disabled by `MiniDFSCluster` when explicit ports are absent.

## Test Signals
Useful tests are topology-shape checks: NN counts, HA/federation booleans, explicit port detection, rejection of empty nameservices, and correct generated IDs for federated/HA factories. Most coverage is indirect through MiniDFSCluster HA and federation tests.
