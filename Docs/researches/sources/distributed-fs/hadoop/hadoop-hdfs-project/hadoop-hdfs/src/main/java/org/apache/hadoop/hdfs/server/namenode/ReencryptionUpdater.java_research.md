# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ReencryptionUpdater.java

## Purpose
`ReencryptionUpdater` consumes completed KMS re-encryption tasks, updates file encryption xattrs, advances zone checkpoints, and completes zones. It is deliberately single-threaded because updates require NameNode write locks.

## Important APIs, types, and functions
Nested `ZoneSubmissionTracker` tracks futures and checkpoint progress. `ReencryptionTask` carries zone id, batch, failure count, processed flag, updated count, and last file. `FileEdekInfo` stores inode id, original EDEK, and new EDEK. Main methods are `run`, `markZoneSubmissionDone`, `takeAndProcessTasks`, `processTask`, `processTaskEntries`, `processCheckpoints`, `checkPauseForTesting`, and `throttle`.

## Control flow
The updater blocks on `CompletionService.take`, throttles by configured lock ratio, skips canceled futures, then processes tasks under FSNamesystem and FSDirectory write locks. It resolves inodes by id, skips deleted or changed files, verifies key name/version and original encrypted key material, replaces file encryption xattrs, and advances checkpoints only across contiguous processed futures. Retriable and safe-mode errors sleep and retry; edit-log sync is done outside the write lock.

## State and persistence behavior
Runtime state includes pause flags, throttle timers, retry interval, and running flag. Persistent effects are file encryption xattr replacements, re-encryption progress/finish xattrs, and edit-log `logSetXAttrs` entries.

## Dependencies and integration points
It depends on `FSDirectory`, `FSDirEncryptionZoneOp`, `ReencryptionHandler`, `CompletionService`, `ZoneReencryptionStatus`, `EncryptedKeyVersion`, `FileEncryptionInfo`, xattrs, `RwLockMode`, `RetriableException`, and `SafeModeException`.

## Risks and invariants
There should be only one updater. Stale tasks must not overwrite files whose encryption info changed. Checkpoints can advance only in task order. Retrying indefinitely is intentional for temporary safe-mode/retriable conditions but may delay completion.

## Test signals
Test deleted inode skips, changed key/version/material skips, checkpoint ordering, dummy task completion, safe-mode retry, cancellation, edit-log xattr logging, pause hooks, and throttle behavior.
