# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestConnectionManager.java

## Purpose
`TestConnectionManager` validates router NameNode connection pooling, cleanup, connection creation failure handling, per-connection concurrency, protocol support, state-id alignment, and duplicate creation suppression.

## Important APIs, Types, and Functions
The class exercises `ConnectionManager`, `ConnectionPool`, `ConnectionPoolId`, `ConnectionContext`, `ConnectionManager.ConnectionCreator`, `ConnectionPool.newConnection()`, `getConnection()`, `cleanup()`, `getPools()`, `getNumCreatingConnections()`, and alignment through `RouterFederatedStateProto` on `Server.Call`. It covers `ClientProtocol` and `NamenodeProtocol`.

## Control Flow
Setup creates a `ConnectionManager`, adds static host resolution for `nn1`, and starts the manager. Cleanup tests seed pools with total/active connections and assert idle cleanup respects minimum active ratio and minimum size. Concurrency tests set max concurrency per connection, consume slots, detect unusable active connections when saturated, then add a new connection. Failure tests verify unresolvable hosts do not kill `ConnectionCreator` and that eager bad pool construction throws. Basic get-connection tests exhaust idle connections for client and namenode protocols. State-id tests set thread-local `Server.Call` federated namespace state and assert the pool alignment context advances from state id 1 to 2. Duplicate-creation tests close the background creator and confirm repeated requests for the same pool only enqueue one creation, while another user creates a second. Unsupported protocol tests assert the error message.

## State and Persistence
State is in-memory connection pools keyed by UGI, NameNode address, and protocol; per-connection active counts; creator queue state; and thread-local server call state. No durable persistence is involved.

## Dependencies and Integration Points
The test integrates Hadoop RPC client creation, UGI identity, network address resolution, router config keys for concurrency and cleanup ratio, and router state-id propagation to NameNode connections.

## Risks and Test Signals
Tests use real connection construction to a statically resolved address and background threads. Identity comparison of UGI in helper checks is intentional because keys are created with the same static instances. Passing tests signal pool cleanup safety, saturation handling, robust async creation, protocol validation, and correct propagation of federated namespace state ids.
