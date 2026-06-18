# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestPendingRecoveryBlocks.java

## Purpose
`TestPendingRecoveryBlocks` is a focused unit test for `PendingRecoveryBlocks`, the NameNode-side structure that suppresses repeated block recovery attempts within a recovery timeout. It verifies add/remove semantics and timeout-based re-admission for the same block.

## Important APIs, types, and functions
The test constructs `PendingRecoveryBlocks` with a `recoveryTimeout` of 1000 ms and uses `BlockInfoContiguous` wrapping `Block` instances as keys. Mockito spies the tracker so `getTime()` can be controlled deterministically. The public methods under test are `add`, `remove`, and `isUnderRecovery`.

## Control flow
`setUp` creates a spy tracker before each test. `testAddDifferentBlocks` adds three distinct blocks and verifies each is tracked as under recovery. `testAddAndRemoveBlocks` adds two blocks, removes the first, and verifies adding that block again succeeds. `testAddBlockWithPreviousRecoveryTimedOut` forces time to 0 for the first add, to half the timeout for a rejected duplicate add, and to twice the timeout for an accepted recovery retry.

## State and persistence behavior
All state is in-memory and scoped to the tracker. The important state transition is from absent to pending recovery, from pending to absent via `remove`, and from pending to expired when the current time passes the timeout. No persistence or cluster-level state is involved.

## Dependencies and integration points
This is a pure unit test except for Hadoop block model classes and Mockito. It intentionally avoids MiniDFSCluster, BlockManager, and background threads by controlling the clock through the spy.

## Risks and test signals
The main regression signal is whether duplicate recovery is blocked only during the active timeout. Missing behavior includes no checks for concurrent access, batch cleanup, or interaction with lease/block recovery in a running NameNode. The deterministic mocked time makes these tests stable and precise for the core timeout contract.
