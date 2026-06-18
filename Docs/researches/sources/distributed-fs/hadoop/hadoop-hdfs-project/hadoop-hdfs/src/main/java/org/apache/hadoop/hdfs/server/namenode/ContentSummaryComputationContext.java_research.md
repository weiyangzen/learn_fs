# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ContentSummaryComputationContext.java

## Purpose
`ContentSummaryComputationContext` carries state and lock-yield policy for namespace content summary traversal. It holds active counts, snapshot counts, storage policy access, optional permission checker, and parameters for yielding long computations.

## Important APIs and Types
Constructors support yielding traversal with `FSDirectory`/`FSNamesystem` or blocking traversal with a `BlockStoragePolicySuite`. Key methods are `yield`, `getCounts`, `getSnapshotCounts`, `getBlockStoragePolicySuite`, `getErasureCodingPolicyName`, and `checkPermission`.

## Control Flow
`yield` checks whether the counted file/symlink/directory/snapshottable count exceeds the next threshold. If the context holds exactly the expected read locks and no write locks, it releases `FSDirectory` and global `FSNamesystem` read locks, sleeps for the configured interval, reacquires them, increments `yieldCount`, and continues. EC policy lookup handles striped files directly, replicated files with a constant, symlinks as empty, and directories by reading the EC xattr or recursing to parents.

## State and Persistence
The context is request-local and non-persistent. Its `yieldCount` is used by quota consistency checks to avoid comparing cached usage after a lock-yield window where state may have changed.

## Dependencies and Integration
It integrates with `FSDirectory`, `FSNamesystem`, `BlockStoragePolicySuite`, `FSPermissionChecker`, `XAttrFeature`, EC policy manager, and global/read lock APIs.

## Risks and Test Signals
Lock assumptions are strict: yielding is skipped if nested read holds or write locks are present. EC policy lookup can return empty string on parsing/lookup errors, which may hide metadata issues behind warnings. Tests should cover yield/no-yield paths, lock reacquisition ordering, permission audit behavior for superusers, inherited directory EC policy lookup, symlink behavior, and quota consistency with `yieldCount`.
