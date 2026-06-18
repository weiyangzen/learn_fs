# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/PrimarySelector.java

## Purpose
`PrimarySelector` defines how a master determines and observes primary/standby leadership.

## Important APIs, Types, And Functions
The nested `Factory` creates ZooKeeper-backed selectors for master and job master using configured addresses and election/leader paths. The interface defines `start`, `stop`, `getState`, `getStateUnsafe`, `onStateChange`, and `waitForState`.

## Control Flow, State, Dependencies, Risks, And Tests
Implementations coordinate in-memory leadership state and external election state. The factory returns `UfsJournalMultiMasterPrimarySelector`, linking leader election to UFS journal multi-master operation. No persistent state is defined here, but election paths in ZooKeeper are external coordination state. Risks include configuration mixups between master and job master paths, synchronous listener execution expectations, and unsafe state reads. Tests should cover factory property usage, lifecycle calls, listener cleanup, wait semantics, and integration with journal mode transitions.
