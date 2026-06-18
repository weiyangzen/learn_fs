# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/BlockLocalPathInfo.java

## Purpose
`BlockLocalPathInfo` carries the local filesystem paths for a block data file and its metadata file on a DataNode.

## Important APIs, types, and functions
The constructor stores an `ExtendedBlock`, block file path, and metadata file path. `getBlockPath`, `getBlock`, and `getMetaPath` expose those values.

## Control flow
There is no behavior beyond construction and getters.

## State and persistence behavior
State is the block reference and two path strings. The path strings are initialized to empty defaults but set by the constructor. No local persistence occurs here.

## Dependencies and integration points
It depends on `ExtendedBlock` and is returned by `ClientDatanodeProtocol#getBlockLocalPathInfo`. `BlockReaderLocalLegacy` consumes it to open local block and checksum files.

## Risks and test signals
Tests should verify path preservation, empty/null path handling as supplied by the DataNode, and integration with legacy short-circuit reads. Security risk is external: exposing paths is only safe under DataNode-side authorization and Kerberos/token checks.
