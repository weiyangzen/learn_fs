# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/RemotePeerFactory.java

Purpose: `RemotePeerFactory` is a private HDFS client extension point for constructing connected remote `Peer` instances used by block readers. It isolates socket creation, optional SASL/encryption setup, and DataNode identity handling from consumers such as `BlockReaderFactory`.

Important APIs/types/functions: the only method is `Peer newConnectedPeer(InetSocketAddress addr, Token<BlockTokenIdentifier> blockToken, DatanodeID datanodeId) throws IOException`. Inputs are the target socket address, block token for SASL or block access negotiation, and the destination DataNode identity.

Control flow: the interface has no implementation in this file. Implementations are expected to connect to the supplied address, wrap or negotiate the stream as configured, authenticate/authorize using the block token, and return a ready `Peer`. Failures are surfaced as `IOException`.

State and persistence behavior: this file defines no state. Implementations may use socket caches or security state, but the contract here returns a new connected peer from the caller perspective.

Dependencies and integration points: `BlockReaderFactory.nextTcpPeer()` calls this interface when peer-cache reuse is unavailable. `Peer` is the HDFS network abstraction consumed by `BlockReaderRemote`. `DatanodeID` and `BlockTokenIdentifier` tie the connection to HDFS block-transfer security.

Risks: because the interface abstracts security negotiation, callers must distinguish security exceptions from stale-socket I/O failures after implementations throw. Tests should inject implementations that return a peer, throw token/encryption errors, throw ordinary `IOException`, and verify `BlockReaderFactory` fallback and retry behavior.
