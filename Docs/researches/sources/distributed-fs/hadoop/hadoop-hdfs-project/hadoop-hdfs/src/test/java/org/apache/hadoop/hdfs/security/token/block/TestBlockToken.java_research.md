# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/security/token/block/TestBlockToken.java

## Purpose
`TestBlockToken` is a broad security test suite for HDFS block access tokens. It validates `BlockTokenIdentifier` serialization in legacy and protobuf formats, `BlockTokenSecretManager` token generation and verification, `BlockPoolTokenSecretManager` key distribution, token-backed datanode RPC authorization, storage type and storage ID matching, block-token serial number ranges, and client behavior when a last in-progress block token expires.

## Important APIs, Types, and Functions
The file centers on `BlockTokenSecretManager`, `BlockTokenIdentifier`, `BlockPoolTokenSecretManager`, `ExportedBlockKeys`, `Token<BlockTokenIdentifier>`, `ExtendedBlock`, `LocatedBlock`, and `MiniDFSCluster`. Helper methods include `generateTokenId`, `checkAccess`, `tokenGenerationAndVerification`, `createMockDatanode`, `testBlockTokenRpc`, `testBlockTokenRpcLeak`, `testCraftedBlockTokenIdentifier`, `writeAndReadBlockToken`, and `testBadStorageIDCheckAccess`. `GetLengthAnswer` is a Mockito `Answer` used by a mock `ClientDatanodeProtocolPB` RPC endpoint to verify the current UGI contains exactly the expected block token.

## Control Flow
Each test resets UGI to simple auth, then specific RPC tests enable Kerberos-style SASL. Secret-manager tests create master/slave managers, export keys from the master, import them into the slave, generate single-mode and multi-mode tokens, update keys, and repeat verification. RPC tests start a local protobuf RPC server with a secret manager, attach a token to a remote UGI, call `getReplicaVisibleLength`, and assert that server-side token identity and access checks pass. Serialization tests deliberately parse token bytes with both encodings and assert the auto-detecting `readFields` path chooses the expected format. MiniDFSCluster tests create files, fetch located blocks, shorten token lifetime, and read after expiry to assert no slow refetch path is required for completed last blocks.

## State and Persistence Behavior
The suite mutates global `UserGroupInformation` configuration, uses per-test `BlockTokenSecretManager` key state, writes token identifiers to `DataOutputBuffer`, reads them through `DataInputBuffer` and `DataInputStream`, and creates temporary MiniDFSCluster file/block state. The RPC leak test counts `/proc/self/fd` descriptors and is guarded by `assumeTrue(FD_DIR.exists())`. `FieldUtils` mutates private identifier storage fields to simulate old NameNodes that did not include storage metadata.

## Dependencies and Integration Points
Dependencies span HDFS security token classes, protobuf RPC, IPC client/server code, `DFSUtilClient` datanode proxy creation, MiniDFSCluster, `DistributedFileSystem`, Mockito, Apache Commons reflection, and `SecurityTestUtil`. The tests integrate block-token semantics with storage type/ID authorization, RPC SASL token transport, block location generation, and NameNode block manager token expiry behavior.

## Risks and Test Signals
Important risks are global UGI state leakage, timing sensitivity in token expiry and RPC leak loops, platform dependence on `/proc/self/fd`, brittle crafted-byte expectations, and compatibility between legacy and protobuf token encodings. Strong signals include equality checks for parsed identifiers, expected `InvalidToken` failures for bad storage IDs, key-update range assertions, RPC round-trip authorization, descriptor leak bounds, and MiniDFSCluster reads after token expiry.
