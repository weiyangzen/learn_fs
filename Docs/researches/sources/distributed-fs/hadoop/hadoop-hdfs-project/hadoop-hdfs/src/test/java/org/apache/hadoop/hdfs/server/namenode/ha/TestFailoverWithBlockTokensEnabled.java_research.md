# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestFailoverWithBlockTokensEnabled.java

## Purpose
`TestFailoverWithBlockTokensEnabled` verifies that HA clusters with HDFS block access tokens enabled keep token serial numbers distinct, reject tampered block tokens, and continue reading/writing after failover and block-token key updates.

## Important APIs, Types, And Functions
The fixture enables `DFS_BLOCK_ACCESS_TOKEN_ENABLE_KEY`, reduces retry window base, and starts a three-NameNode HA topology with one DataNode. Tests are `ensureSerialNumbersNeverOverlap`, `ensureInvalidBlockTokensAreRejected`, `testFailoverAfterRegistration`, and `TestFailoverAfterAccessKeyUpdate`. Helpers include `setAndCheckSerialNumber`, `writeUsingBothNameNodes`, `lowerKeyUpdateIntervalAndClearKeys`, and its namesystem overload.

## Control Flow
The serial test sets the same nominal serial number on all NameNode `BlockTokenSecretManager` instances and verifies each manager maps it to a unique effective serial. The invalid-token test writes a file, spies the `DFSClient`, alters each returned block token identifier expiry while keeping the old password, installs the spy back into the `DistributedFileSystem`, and expects read failure. Failover tests write on NN0 active, transition NN0 standby and NN1 active, delete and rewrite the file, optionally after lowering token key intervals and clearing NameNode/DataNode keys.

## State And Persistence
Persistent state is one HDFS file at `/test-path`; security state includes block token secret manager keys, serial numbers, token lifetime/update interval, DataNode cached block secret keys, and located block tokens returned to clients. Tampered token state is injected only in the client-side located-block response path.

## Dependencies And Integration Points
Dependencies include `BlockTokenSecretManager`, `BlockTokenIdentifier`, `DFSClientAdapter`, `LocatedBlocks`, `LocatedBlock`, `DataNode`, `FSNamesystem`, Mockito, `DFSTestUtil`, and `HATestUtil`. The tests connect HA failover, DataNode registration/key propagation, client block reads, and token validation.

## Risks
Block-token serial overlap across NameNodes can let one NameNode validate another's stale keys incorrectly. Short key intervals and sleeps are timing-sensitive. The invalid token path depends on token password mismatch behavior and exact client error text.

## Test Signals
Signals include non-equal effective serial numbers for all manager pairs, expected `Could not obtain block` failure for tampered tokens, and successful write/delete/write operations on different active NameNodes before and after key updates.
