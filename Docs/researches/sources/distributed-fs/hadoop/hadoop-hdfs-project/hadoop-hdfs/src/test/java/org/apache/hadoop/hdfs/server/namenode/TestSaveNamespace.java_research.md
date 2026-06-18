# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestSaveNamespace.java

Purpose: Comprehensive saveNamespace/checkpoint fault-injection suite for the NameNode. It validates recovery from partial fsimage writes, bad storage directories, VERSION write failures, failed checkpoints, edit-log rolling during save, txid persistence, cancellation cleanup, lease serialization edge cases, snapshot-section filtering, saveNamespace skip thresholds, and seen_txid repair.

Important APIs and functions: Fault helpers `FaultySaveImage`, `FaultyWriteProperties`, and `saveNamespaceWithInjectedFault` use Mockito spies on `FSImage` and `NNStorage`. Tests use `FSNamesystem.loadFromDisk`, `DFSTestUtil.formatNameNode`, `fsn.saveNamespace`, `fsn.rollEditLog`, `NameNodeRpcServer.saveNamespace`, `Canceler`, `GenericTestUtils.DelayAnswer`, `MD5FileUtils`, and local helper `doAnEdit`/`checkEditExists`.

Control flow: Most tests format a two-directory NameNode, inject a failure at a precise save step, enter safemode, run saveNamespace, optionally expect failure, then leave safemode, perform further edits, close, reload from disk, and verify edits survived. Other tests simulate permission-denied storage reinsertion, concurrent cancellation during image save, open/dangling leases, bogus snapshot diffs, checkpoint suppression by recent time/tx gap, and corrupt `seen_txid` in one directory.

State and persistence behavior: The suite directly exercises fsimage files, `.ckpt` temporary images, VERSION files, storage directory removal/reinsertion, edit-log segments, transaction IDs, lease paths, snapshot diff serialization, checkpoint transaction IDs, and `seen_txid` consistency across name dirs.

Dependencies and integration points: Integrates `FSImage`, `NNStorage`, `FSNamesystem`, `FSEditLog`, local filesystem storage, NameNode metrics/init, safemode, leases, snapshots, block ID generation, cancellation, and Mockito/Whitebox fault injection.

Risks: Checkpoint recovery must never leave only corrupt images or orphan temporary files. Cancellation must remove partial fsimage artifacts. Fault tests rely on private implementation call order and storage-directory counts, so refactors to save sequencing or storage iteration may require test updates.

Test signals: Signals include reloadable namespace after failures, removed storage directory count returning to zero, expected save failures when all dirs fail, exact last-written txid progression, only original image/MD5 files after cancellation, successful save with renamed/dangling leases, removal of bogus snapshot feature after restart, checkpoint txid skip/update behavior, and repaired identical `seen_txid` files.
