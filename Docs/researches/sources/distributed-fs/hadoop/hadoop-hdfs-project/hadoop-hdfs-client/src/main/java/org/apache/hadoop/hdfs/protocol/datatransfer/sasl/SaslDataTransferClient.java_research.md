# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/SaslDataTransferClient.java

## Purpose
`SaslDataTransferClient` performs client-side SASL negotiation for HDFS data transfer connections. It is used by both HDFS clients and DataNodes acting as clients to other DataNodes.

## Important APIs, Types, and Functions
Constructors accept configuration, a `SaslPropertiesResolver`, a `TrustedChannelResolver`, and optionally an `AtomicBoolean` that indicates fallback to simple auth.

`newSocketSend`, `socketSend`, and `peerSend` are entry points. They either return raw streams/peer when no handshake is required or wrapped streams/`EncryptedPeer` after negotiation. `checkTrustAndSend` requires both local and remote trust to skip negotiation.

`send` implements the handshake decision tree: use encrypted SASL when a `DataEncryptionKey` is available; skip in unsecured mode; skip on privileged DataNode transfer ports in secure mode; skip if fallback to simple auth is active; use general SASL when a resolver is configured; otherwise skip for the rare secured/no-SASL testing edge.

`getEncryptedStreams` builds privacy SASL props from a data encryption key, optionally updates the block token with a DataNode downstream secret/QOP, encodes the encryption key as username/password, and delegates to `doSaslHandshake`. `getSaslStreams` obtains client SASL properties for the peer address, optionally overwrites downstream QOP and token password, builds username/password from the block token, and delegates to the handshake.

`doSaslHandshake` writes the SASL magic number, sends the initial response plus optional handshake secret, processes server challenge, optionally sends supported cipher options for privacy QOP, reads the negotiated cipher option, validates SASL completion/QOP, unwraps negotiated cipher keys, and returns either crypto streams or SASL streams. On `IOException`, it attempts to send a generic SASL error message but rethrows the original exception with any send failure suppressed.

## Control Flow
The handshake is three-step client SASL exchange plus optional cipher negotiation. Secret-key token mutation is used for DataNode-to-DataNode downstream QOP changes. Trusted-channel checks happen before any key creation on peer/socket paths except `newSocketSend`, which checks local trust before asking for a key.

## State and Persistence Behavior
The object stores configuration, resolvers, fallback flag, and `targetQOP` for testing. It mutates `accessToken` in `updateToken` for downstream DataNode communication by changing the `BlockTokenIdentifier` handshake message and recomputing token password/id. No persistent state is written by this class.

## Dependencies and Integration Points
It depends on `DataTransferSaslUtil`, `SaslParticipant`, HDFS peer/socket abstractions, block tokens, data encryption keys, `TrustedChannelResolver`, `SaslPropertiesResolver`, `UserGroupInformation`, `SecurityUtil`, `SecretManager`, crypto cipher options, and configuration keys. It is constructed by `DFSClient`, DataNode, and balancer/dispatcher code.

## Risks and Edge Cases
Security and compatibility risks are significant. Incorrect trust resolver behavior can bypass negotiation. QOP overwrite mutates tokens and must only happen for DataNode downstream flows with a secret key. `doSaslHandshake` must preserve `InvalidEncryptionKeyException` and `InvalidBlockTokenException` for caller retry/refresh. Cipher-suite negotiation only sends options when privacy is requested. Fallback-to-simple-auth must not be accidentally enabled in secure clusters.

## Test Signals
`TestSaslDataTransfer` covers trust decisions and SASL negotiation; `TestEncryptedTransfer` covers encrypted handshakes and cipher options; `TestDataXceiverBackwardsCompat` covers handshake compatibility. Focused tests should cover every branch in `send`, token mutation in `updateToken`, handshake-secret presence/absence, invalid key/token error propagation, and AES/SM4 cipher negotiation.
