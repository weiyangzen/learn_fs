# subset-b-007507 grouped research

This grouped report covers Hadoop HDFS NameNode snapshot diff/persistence code and Storage Policy Satisfier queue interfaces. Each section is source-tree aligned and intended for reconciliation into the corresponding `Docs/researches/<source>_research.md` file.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/DiffListByArrayList.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/DiffListByArrayList.java

## Purpose

`DiffListByArrayList` is the simple `DiffList<T>` implementation used for ordered snapshot diff lists when skip-list acceleration is disabled. It wraps a Java `ArrayList` and exposes the minimal indexed, searchable, iterable, append/prepend, and range APIs expected by `AbstractINodeDiffList` and directory/file snapshot diff consumers.

## Important APIs, Types, And Functions

The class is generic over `T extends Comparable<Integer>`, which matches diff objects comparable by snapshot ID. The public surface is `get`, `isEmpty`, `size`, `remove`, `addLast`, `addFirst`, `binarySearch`, `iterator`, and `getMinListForRange`. `getMinListForRange` returns `list.subList(startIndex, endIndex)`, so callers receive the raw chronological range without pre-combined diff shortcuts.

## Control Flow

Creation flows through `DirectoryDiffListFactory.createDiffList` or direct construction with an initial capacity. Snapshot diff insertion appends for normal in-memory operations and prepends during FSImage load because serialized diffs are read in reverse order. Binary search delegates to `Collections.binarySearch` against snapshot IDs. Deletion delegates to `ArrayList.remove`.

## State And Persistence Behavior

State is only the in-memory list. The class does not serialize itself; its contents are persisted by `SnapshotFSImageFormat` or `FSImageFormatPBSnapshot` through the owning diff list. In ordered snapshot deletion mode, `remove` asserts that only index `0` is removed, matching the first-snapshot-only deletion invariant.

## Dependencies And Integration Points

It depends on `DiffList`, `INodeDirectory` only for the interface signature, and `SnapshotManager.isDeletionOrdered()` for the deletion assertion. It integrates with `DirectoryWithSnapshotFeature.DirectoryDiffList`, `FileDiffList`, and FSImage loaders through `addFirst`/`addLast` ordering semantics.

## Risks And Edge Cases

Range reconstruction is linear and can be expensive for directories with many snapshots. `subList` is a view, so structural changes to the backing list while a caller holds the range would be unsafe. The ordered-deletion invariant is enforced only by `assert`, so production JVMs without assertions rely on callers to obey it. Index arguments are not validated beyond `ArrayList` exceptions.

## Test Signals

Useful tests cover binary-search insertion-point behavior, reverse-order FSImage load via repeated `addFirst`, ordered deletion rejecting nonzero removals when assertions are enabled, and equivalence with `DiffListBySkipList.getMinListForRange` for the same diff sequence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/DiffListByArrayList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/DiffListBySkipList.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/DiffListBySkipList.java

## Purpose

`DiffListBySkipList` is an optimized `DiffList<DirectoryDiff>` for directory snapshot diffs. It keeps a linear list for normal indexed access while adding skip pointers that cache combined `ChildrenDiff` values across ranges, reducing the cost of snapshot child-list reconstruction, snapshot deletion, and snapshot diff computation over long diff histories.

## Important APIs, Types, And Functions

The outer class implements `DiffList<DirectoryDiff>`. `SkipListNode` stores one `DirectoryDiff`, a level-0 `next` pointer, and an array of `SkipDiff` entries for higher levels. `SkipDiff` stores the target node and the pre-combined `ChildrenDiff` over that skip. Key methods are `addFirst`, `addLast`, `remove`, `binarySearch`, `iterator`, `getMinListForRange`, and the internal `combineDiff`, `findPreviousNodes`, and node `setSkipDiff4Target` helpers.

## Control Flow

Insertions choose a random level from `DirectoryDiffListFactory.randomLevel()`. `addLast` finds predecessor nodes for all relevant levels, links the new node, and updates predecessors with combined child diffs that cover the skipped interval. `addFirst` inserts before the current first node and, for higher levels, computes combined diffs that include the new element when the new skip has a target. `remove` unlinks the node at every level and either nulls stale skip diffs for tail deletion or combines predecessor and removed-node skip diffs to preserve interval summaries. `getMinListForRange` walks from the starting node, greedily selecting the highest skip whose target remains within the target snapshot ID, returning either the original diff or a synthetic `DirectoryDiff` carrying a combined `ChildrenDiff`.

## State And Persistence Behavior

The persisted state is still just the owning directory diff list; skip levels and cached combined diffs are rebuilt in memory as diffs are loaded with `addFirst`. `skipNodeList` preserves the same indexed order expected by `DiffList`, while `head` and skip pointers are an auxiliary acceleration structure. No skip metadata is written to FSImage.

## Dependencies And Integration Points

This class is selected by `DirectoryDiffListFactory` when the configured max skip levels is positive. It depends on `DirectoryWithSnapshotFeature.DirectoryDiff` and `ChildrenDiff.combinePosterior` to merge directory child changes. It is consumed by directory child-list reconstruction, directory snapshot cleanup, and diff report generation via `DirectoryDiffList.getDiffListBetweenSnapshots`.

## Risks And Edge Cases

Correctness depends on skip interval summaries matching the linear diff sequence after insertions and removals. Bugs in `remove` can leave stale combined diffs and produce incorrect snapshot child views. The implementation assumes sorted chronological diff insertion patterns and uses `Collections.binarySearch` over `skipNodeList`; arbitrary insertion is not supported. Random level generation can produce uneven structures, though indexed fallback remains available. The code is not internally synchronized and depends on NameNode locking.

## Test Signals

Tests should compare skip-list and array-list results for child-list reconstruction, `getMinListForRange`, snapshot deletion at head, middle, and tail, and repeated FSImage load with `addFirst`. Stress tests should use many snapshots, random child creates/deletes, and different skip intervals/max levels to verify output reports and quota/block cleanup match the array-list implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/DiffListBySkipList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/DirectoryDiffListFactory.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/DirectoryDiffListFactory.java

## Purpose

`DirectoryDiffListFactory` centralizes the choice between array-backed and skip-list-backed directory diff lists. It also owns the randomized level policy used when skip-list directory diffs are enabled.

## Important APIs, Types, And Functions

`createDiffList(int capacity)` invokes a volatile `IntFunction<DiffList<DirectoryDiff>>`. `init(int interval, int maxSkipLevels, Logger log)` records skip-list configuration and installs either `DiffListBySkipList` or `DiffListByArrayList`. `randomLevel()` uses `ThreadLocalRandom` to return a level between `0` and `maxLevels`, advancing to the next level with probability `1 / skipInterval`.

## Control Flow

`SnapshotManager` calls `init` during construction using HDFS snapshot skip-list configuration keys. From then on, `DirectoryWithSnapshotFeature.DirectoryDiffList.newDiffs()` calls `createDiffList`. When a skip-list insertion occurs, `DiffListBySkipList` calls `randomLevel` for the new node.

## State And Persistence Behavior

The factory has process-wide volatile state: the constructor function, skip interval, and maximum levels. These settings are not stored in snapshot diffs or FSImage; the in-memory representation after restart follows current NameNode configuration and rebuilds from persisted linear diffs.

## Dependencies And Integration Points

The factory depends on the two `DiffList` implementations, `DirectoryDiff`, Java `ThreadLocalRandom`, and logging supplied by `SnapshotManager`. It is a configuration integration point for `dfs.namenode.snapshot.skiplist.*` behavior.

## Risks And Edge Cases

`maxSkipLevels > 0` enables skip lists without validating that `interval` is positive; a nonpositive interval could make `Random.nextInt(skipInterval)` fail. Because the state is static and volatile, tests that reinitialize it can affect other tests in the same JVM. Changing configuration across restart changes performance and internal shape, not the serialized snapshot contract.

## Test Signals

Tests should initialize with `maxSkipLevels` zero and positive values, verify created diff-list classes, exercise `randomLevel` bounds, and validate that snapshot behavior is invariant when switching implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/DirectoryDiffListFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/DirectorySnapshottableFeature.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/DirectorySnapshottableFeature.java

## Purpose

`DirectorySnapshottableFeature` extends `DirectoryWithSnapshotFeature` for directories where snapshots may be created. It tracks snapshot roots by name, enforces per-directory quota, creates/removes/renames snapshots, captures open files when configured, and computes full or paginated snapshot diff reports.

## Important APIs, Types, And Functions

Important state includes `snapshotsByNames`, a name-sorted `List<Snapshot>`, and `snapshotQuota`. Key APIs include `getSnapshot`, `getSnapshotById`, `getSnapshotList`, `renameSnapshot`, `setSnapshotQuota`, `addSnapshot`, `removeSnapshot`, `computeDiff` overloads, `getSnapshotByName`, `findRenameTargetPath`, and test-oriented `dumpTreeRecursively`.

## Control Flow

Snapshot creation obtains the next ID from `SnapshotManager`, checks quota and duplicate names, creates a `Snapshot`, appends a `DirectoryDiff` marked with the snapshot root, inserts the snapshot by name, updates modification times, and optionally records modifications for open leased files beneath the snapshot root. Removal searches by name, finds the prior covering snapshot, validates ordered-deletion rules, sets reclaim context, calls `snapshotRoot.cleanSubtree`, removes the name entry only after cleanup, and updates mtime. Diff computation resolves `from` and `to` snapshot objects, then recursively walks the earlier snapshot tree, collecting directory `ChildrenDiff`s and file changes while detecting renames through `INodeReference.WithName`.

## State And Persistence Behavior

The name-sorted snapshot list and quota are persisted by FSImage snapshot sections. The chronological diff order lives in the inherited diff list. Snapshot roots preserve metadata through `Snapshot.Root` copies. Ordered deletion can rename/mark snapshots as deleted before a later GC removes them, so snapshots may remain visible internally with a deleted marker and generated `name#id` name.

## Dependencies And Integration Points

The feature integrates with `INodeDirectory`, `SnapshotManager`, `LeaseManager`, `DirectoryWithSnapshotFeature`, `FileWithSnapshotFeature`, `SnapshotDiffInfo`, `SnapshotDiffListingInfo`, `FSImage` loaders/savers, `INodeReference` rename tracking, content summary and quota accounting, and NameNode RPCs for create/delete/rename/list/diff snapshot operations.

## Risks And Edge Cases

There are two orderings to preserve: names in `snapshotsByNames` and chronological IDs in diffs. Rename must reinsert at the correct binary-search position. Diff code must handle null snapshots as current state, descendant-scoped diffs, renames whose target left the snapshot root, and resume paths in paginated diff listing. Snapshot deletion during edit-log replay has special tolerance for old ordered-deletion logs. Open-file capture can fail snapshot creation if lease scanning or modification recording fails.

## Test Signals

Tests should cover duplicate snapshot names, rename ordering, quota limits, snapshot deletion with and without ordered deletion, FSImage round trips, open-file capture, full and paginated diff reports, rename reports under and outside snapshot roots, descendant-scoped diff when enabled, and content summary counts for snapshots and snapshottable directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/DirectorySnapshottableFeature.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/DirectoryWithSnapshotFeature.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/DirectoryWithSnapshotFeature.java

## Purpose

`DirectoryWithSnapshotFeature` stores and applies directory snapshot diffs for any directory participating in snapshots. It records child create/delete/modify deltas, reconstructs historical child lists, manages snapshot cleanup and block reclamation for directory subtrees, and computes directory-level changes between snapshots.

## Important APIs, Types, And Functions

`ChildrenDiff` extends `Diff<byte[], INode>` for child-list changes and adds FSImage serialization helpers, created/deleted destruction, and replacement/removal utilities. `DirectoryDiff` extends `AbstractINodeDiff` and stores `childrenSize`, a `ChildrenDiff`, and `isSnapshotRoot`. `DirectoryDiffList` extends `AbstractINodeDiffList` and creates directory diffs/snapshot copies. Top-level APIs include `addChild`, `removeChild`, `getChildrenList`, `getChild`, `saveChild2Snapshot`, `clear`, quota/content summary methods, `computeDiffBetweenSnapshots`, `cleanDirectory`, `destroyDstSubtree`, and `cleanDeletedINode`.

## Control Flow

Mutations call `diffs.checkAndAddLatestSnapshotDiff` for the latest snapshot ID, update the `ChildrenDiff`, then apply the live children-list change with undo if the live operation fails. Historical reads find the diff for a snapshot and combine posterior diffs from that point to current state, reverse-applying them to current children. Snapshot deletion updates the prior snapshot, deletes the target diff, cleans recursive subtrees, destroys nodes created only in removed intervals, and handles renamed/reference nodes through specialized cleanup paths.

## State And Persistence Behavior

The durable state is the chronological `DirectoryDiffList`; each diff records child count, optional directory attribute copy or snapshot root, and created/deleted child lists. Created list entries persist by local name, while deleted list entries persist full inode data or references. Cleanup mutates diff lists and records quota/block reclamation in `INode.ReclaimContext`. ACL references attached to snapshot copies are released during destruction.

## Dependencies And Integration Points

The class depends on `AbstractINodeDiffList`, `Diff`, `INodeDirectory`, `INodeFile`, `INodeReference`, quota/content-summary infrastructure, ACL storage, `SnapshotFSImageFormat.ReferenceMap`, and `SnapshotManager.isDeletionOrdered`. It is used by `INodeDirectory` mutation paths, snapshot diff reports, FSImage save/load, rename handling, and block/quota reclamation.

## Risks And Edge Cases

Cleanup is lifecycle-sensitive: created nodes, deleted nodes, renamed reference nodes, and posterior diffs must be combined or destroyed exactly once. Ordered deletion forbids posterior combination in `DirectoryDiff.combinePosteriorAndCollectBlocks`. Historical child reconstruction assumes diff lists are sorted and `ChildrenDiff` operations are correct. Quota deltas are computed from before/after reclaim context counts and must be added for quota-bearing directories. Many methods depend on caller-held NameNode/FSDirectory locks.

## Test Signals

Strong tests include creating/removing children across multiple snapshots, reconstructing child lists for each snapshot, deleting current directories with snapshots, deleting snapshots with prior/posterior diffs, rename scenarios with `WithName`/`DstReference`, quota and content summary updates, ACL release behavior, and comparing skip-list versus array-list diff reconstruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/DirectoryWithSnapshotFeature.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/FSImageFormatPBSnapshot.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/FSImageFormatPBSnapshot.java

## Purpose

`FSImageFormatPBSnapshot` reads and writes snapshot-related sections in the protobuf FSImage format. It persists snapshottable directories, snapshots, inode references, file diffs, directory diffs, created/deleted lists, snapshot inode copies, block lists needed for snapshot truncation, and nonfatal image validation errors.

## Important APIs, Types, And Functions

The nested `Loader` exposes `loadINodeReferenceSection`, `loadSnapshotSection`, and `loadSnapshotDiffSection`, with helpers for `loadFileDiffList`, `loadCreatedList`, `loadDeletedList`, and `loadDirectoryDiffList`. The nested `Saver` exposes `serializeSnapshotSection`, `serializeINodeReferenceSection`, `serializeSnapshotDiffSection`, `serializeFileDiffList`, `serializeDirDiffList`, `buildINodeReference`, and `getNumImageErrors`.

## Control Flow

Loading first reconstructs inode references into the loader context reference list. Snapshot section loading restores `SnapshotManager` counters, marks directories as snapshottable, adds them to the manager, then loads snapshot roots and inserts snapshots into parent features. Snapshot diff loading reads entries keyed by inode ID and dispatches to file or directory diff loaders. Saving writes snapshottable directory IDs and snapshot roots, later serializes references from the saver context, and scans the inode map to emit file and directory diff entries. Diff lists are written in reverse order and loaded with `addFirst` to restore chronological order.

## State And Persistence Behavior

The protobuf image persists static snapshot state for NameNode restart. File diffs persist snapshot ID, file size, optional file attribute copy, and optional contiguous blocks. Directory diffs persist snapshot ID, child size, snapshot-root flag, optional directory copy, created-list names, and deleted inode IDs or reference indices. The saver counts missing referred inode IDs, repeated deleted-list names, and misordered deleted-list entries as image errors rather than throwing immediately.

## Dependencies And Integration Points

The class integrates with `FSImageFormatProtobuf`, protobuf `FsImageProto` sections, `FSImageFormatPBINode` attribute builders/loaders, `SnapshotManager`, `FSDirectory`, `INodeMap`, `BlockManager`, `INodeReference`, ACL/XAttr/quota loaders, and `SaveNamespaceContext` cancellation. It is the protobuf counterpart to the older `SnapshotFSImageFormat`.

## Risks And Edge Cases

Order is critical: created lists store only names and must resolve to current children or posterior deleted entries; deleted reference indices must match the reference section order. Loading file diffs assumes persisted file-diff blocks are contiguous and reconstructs missing block-map entries. Directory deleted lists are sorted after load, while save detects repeated or misordered entries. Striped-file attributes are handled differently from replication attributes. Cancellation may split snapshot diff sections into subsections.

## Test Signals

Tests should save and load snapshots with file truncation blocks, deleted references, ACLs, XAttrs, quotas, striped and replicated files, repeated/misordered deleted-list validation, missing referred inode detection, large inode-map snapshot diff subsection rollover, and equivalence between pre-save and post-load snapshot listings and diff reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/FSImageFormatPBSnapshot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/FileDiff.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/FileDiff.java

## Purpose

`FileDiff` records a file's state at a snapshot boundary. It captures the file length, optional file attribute snapshot copy, and, for truncate/block-list changes, a snapshot copy of block references needed to decide which blocks remain live.

## Important APIs, Types, And Functions

The class extends `AbstractINodeDiff<INodeFile, INodeFileAttributes, FileDiff>`. Important methods are `getFileSize`, `setBlocks`, `getBlocks`, `combinePosteriorAndCollectBlocks`, `write`, `destroyDiffAndCollectBlocks`, and `destroyAndCollectSnapshotBlocks`. `setBlocks` copies only enough `BlockInfo` entries to cover the saved file size.

## Control Flow

Normal creation records `file.computeFileSize()` and leaves blocks unset until a caller needs to preserve block references. FSImage load uses the constructor that accepts snapshot attributes and file size, then may call `setBlocks`. Snapshot deletion calls into `FileWithSnapshotFeature.updateQuotaAndCollectBlocks`, which combines block ownership with prior/later snapshots. Direct destruction emits blocks in the stored snapshot block list to `BlocksMapUpdateInfo`.

## State And Persistence Behavior

Durable fields are snapshot ID, file size, optional snapshot inode attributes, and, in protobuf FSImage, optional block references. The older non-protobuf `write` method writes snapshot ID, size, and attributes but not block arrays directly. After `destroyAndCollectSnapshotBlocks`, the block snapshot reference array is nulled to prevent duplicate collection.

## Dependencies And Integration Points

It depends on `BlockInfo`, `INodeFile`, file attribute snapshots, `FSImageSerialization`, and `FileWithSnapshotFeature`. It is held by `FileDiffList`, serialized by snapshot FSImage formats, and consumed during truncation, snapshot deletion, quota calculation, and block map cleanup.

## Risks And Edge Cases

`setBlocks` is intentionally one-shot; later calls do nothing, so callers must pass the correct block array the first time. The file-size loop assumes block lengths cover file length correctly. Block references are shared with block manager structures and must be collected only when no current, earlier, or later snapshot needs them. Snapshot attribute ACL references must be released by higher-level cleanup.

## Test Signals

Tests should cover truncation snapshots with partial block lists, repeated `setBlocks` calls, FSImage round trip of file diff blocks, snapshot deletion that preserves blocks referenced by earlier/later snapshots, and block collection when the last snapshot copy is removed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/FileDiff.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/FileDiffList.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/FileDiffList.java

## Purpose

`FileDiffList` is the file-specific `AbstractINodeDiffList` implementation. It creates `FileDiff` objects, stores snapshot file attribute copies, preserves block snapshots for truncate, and determines which blocks can be reclaimed when a file snapshot diff is removed.

## Important APIs, Types, And Functions

Key methods are `createDiff`, `createSnapshotCopy`, `destroyAndCollectSnapshotBlocks`, `saveSelf2Snapshot`, `findEarlierSnapshotBlocks`, `findLaterSnapshotBlocks`, and `combineAndCollectSnapshotBlocks`. It uses `BlockInfo` arrays to compare removed, earlier, later, and current file block references.

## Control Flow

When a file records itself to a snapshot, `saveSelf2Snapshot` creates or updates the latest diff and optionally stores the current block list. Snapshot deletion calls `combineAndCollectSnapshotBlocks`: if the removed diff has blocks, it may copy them to the prior diff, find later/current block arrays, skip blocks still referenced by either side, protect a truncate-recovery block, and collect remaining blocks for deletion. If the removed diff has no block array and the current file is deleted, it clears the file via `FileWithSnapshotFeature`.

## State And Persistence Behavior

The list itself is persisted by snapshot image formats through its `FileDiff` entries. Block arrays inside diffs are in-memory references restored from protobuf image data. Deletion mutates neighboring diffs by copying block arrays backward when needed and emits block deletions through reclaim context.

## Dependencies And Integration Points

It depends on `AbstractINodeDiffList`, `INodeFile`, `INodeFileAttributes.SnapshotCopy`, block management classes, and `FileWithSnapshotFeature`. It is used by file mutation, truncate, snapshot delete, FSImage load/save, and quota/block collection paths.

## Risks And Edge Cases

The block comparison is reference-based for earlier/later arrays and must avoid deleting blocks still shared by snapshots or current files. Truncate recovery has a special `dontRemoveBlock` path. `findEarlierSnapshotBlocks` and `findLaterSnapshotBlocks` rely on correct binary-search insertion point handling. Current-file-deleted state changes the meaning of missing removed block arrays.

## Test Signals

Useful tests cover append/truncate across multiple snapshots, deleting earlier/middle/later snapshots, current deleted file cleanup, under-construction truncate recovery blocks, FSImage reload of block arrays, and quota deltas after block collection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/FileDiffList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/FileWithSnapshotFeature.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/FileWithSnapshotFeature.java

## Purpose

`FileWithSnapshotFeature` attaches snapshot state to an `INodeFile`. It tracks file diffs, distinguishes files deleted from the current namespace but retained by snapshots, detects file changes between snapshots, and coordinates quota, ACL, replication, and block cleanup when snapshots or current files are removed.

## Important APIs, Types, And Functions

Important state is `FileDiffList diffs` and `isCurrentFileDeleted`. Key methods include `deleteCurrentFile`, `getMaxBlockRepInDiffs`, `changedBetweenSnapshots`, `cleanFile`, `clearDiffs`, `updateQuotaAndCollectBlocks`, and `collectBlocksAndClear`.

## Control Flow

Current-file deletion records a modification against the prior snapshot when needed, marks the feature deleted, computes old quota, and calls `collectBlocksAndClear`. Snapshot deletion updates the prior snapshot ID and asks the diff list to delete the target diff. Change detection compares file lengths at earlier/later points and, if equal, compares snapshot metadata copies. Block/quota cleanup builds a distinct set of blocks across current file, removed diff, and remaining diffs when snapshot attributes exist, releases ACL references, combines snapshot blocks, updates replication factors to the maximum required by current and remaining snapshots, and records quota delta.

## State And Persistence Behavior

The durable state is the `FileDiffList` and each diff's snapshot attributes/size/blocks. `isCurrentFileDeleted` is in-memory state implied by file location and snapshot ownership, not a standalone FSImage field in this class. Cleanup can clear file blocks when no current file and no diffs remain, null snapshot block arrays, and update replication-factor changes in collected block updates.

## Dependencies And Integration Points

The feature integrates with `INodeFile` mutation and deletion, `FileDiffList`, `AclStorage`, block storage policies, quota accounting, `BlockInfo`, `SnapshotDiffInfo`, FSImage formats, and block manager update flows.

## Risks And Edge Cases

Quota accounting must consider distinct block references and storage policy type quotas. Metadata comparison can miss changes if snapshot copies are not recorded at the correct time. Replication factors may need to remain elevated because a snapshot copy still needs a higher replication than the current file. `collectBlocksAndClear` must distinguish max snapshot size from current size and avoid deleting blocks retained by the latest snapshot block array.

## Test Signals

Tests should cover deleted-current-file retention by snapshots, metadata-only changes, length changes, replication changes across snapshots, ACL release, storage policy quota deltas, block collection beyond max snapshot size, and snapshot deletion when the final diff is removed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/FileWithSnapshotFeature.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/Snapshot.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/Snapshot.java

## Purpose

`Snapshot` represents a read-only snapshot of an HDFS subtree. It provides snapshot IDs, naming/path helpers, ID comparators, latest-covered-snapshot lookup, legacy FSImage read/write, and the `Snapshot.Root` directory view used as the snapshot root inode.

## Important APIs, Types, And Functions

Important constants are `CURRENT_STATE_ID` and `NO_SNAPSHOT_ID`. Static helpers include `generateDefaultSnapshotName`, `generateDeletedSnapshotName`, `getSnapshotPath`, `getSnapshotName`, `getSnapshotId`, `getSnapshotString`, `ID_COMPARATOR`, `ID_INTEGER_COMPARATOR`, and `findLatestSnapshot`. Instance APIs include `getId`, `getRoot`, `compareTo`, equality/hash by ID, and `write`. `Snapshot.Root` extends `INodeDirectory`.

## Control Flow

Creating a snapshot copies the source directory into a `Root`, sets its parent, and optionally sets the local snapshot name. Historical child lookups through `Root` delegate to the parent directory's snapshot-aware child-list methods. `findLatestSnapshot` walks ancestor directories and asks their diff lists to update the best prior snapshot below an anchor. Legacy read/write serialize the ID and root directory inode.

## State And Persistence Behavior

A snapshot stores immutable `id` and a `Root`. The root copy preserves ACL, XAttr, and quota features; quota features are copied rather than shared where needed. A root can be marked as deleted by an XAttr used by ordered snapshot deletion. Snapshot name is the root local name. Equality and hash code depend only on snapshot ID.

## Dependencies And Integration Points

The class integrates with `DirectorySnapshottableFeature`, `SnapshotManager`, `INodeDirectory`, FSImage serialization, `ContentSummaryComputationContext`, ACL/XAttr/quota feature classes, and HDFS `.snapshot` path conventions.

## Risks And Edge Cases

`CURRENT_STATE_ID` is intentionally near `Integer.MAX_VALUE`, and comparators rely on subtraction, so IDs must remain within the configured 28-bit snapshot ID space. `generateDefaultSnapshotName` uses wall-clock millisecond precision and can collide under very fast repeated calls, so higher layers still check duplicate names. `Root.metadataEquals` intentionally compares ACL feature references, which is stricter than value equality.

## Test Signals

Tests should verify default and deleted snapshot names, `.snapshot` path construction, ID comparator ordering with null/current state, root delegation for child/content summary access, deleted-marker XAttr behavior, quota/ACL/XAttr preservation, legacy FSImage round trip, and latest-snapshot lookup across ancestors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/Snapshot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/SnapshotDeletionGc.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/SnapshotDeletionGc.java

## Purpose

`SnapshotDeletionGc` is the background timer that completes ordered snapshot deletion. When deletion ordering is enabled, non-earliest snapshots may first be marked deleted and renamed; this GC periodically selects a deleted first snapshot and asks the namesystem to delete it for real.

## Important APIs, Types, And Functions

The class stores `FSNamesystem`, the configured GC period, and an `AtomicReference<Timer>`. Public APIs are `schedule()` and `cancel()`. Internals include `gcDeletedSnapshot(String name)` and nested `GcTask`.

## Control Flow

`schedule` creates a daemon `Timer` once using compare-and-set and schedules `GcTask` at a fixed rate after the configured delay. Each task acquires the FS read lock, calls `SnapshotManager.chooseDeletedSnapshot`, releases the lock, and if a deleted root exists calls `namesystem.gcDeletedSnapshot(snapshotRoot, snapshotName)`. Exceptions during selection are rethrown after logging; exceptions during deletion are logged and swallowed so future timer runs can continue.

## State And Persistence Behavior

The timer state is process-local. Deleted snapshot markers live in snapshot root XAttrs persisted by snapshot/FSImage mechanisms. The GC does not persist progress directly; successful deletion creates normal namespace/edit-log effects through `FSNamesystem.gcDeletedSnapshot`.

## Dependencies And Integration Points

It depends on `FSNamesystem`, `SnapshotManager.chooseDeletedSnapshot`, `Snapshot.Root.getRootFullPathName`, HDFS read locks, configuration keys from `SnapshotManager`, Java `Timer`, and NameNode deletion APIs.

## Risks And Edge Cases

Only one timer is scheduled per instance, but `TimerTask` execution is single-threaded; a long deletion can delay subsequent runs. Selection uses read lock while deletion occurs later through namesystem APIs, so state may change between selection and deletion. If GC is not scheduled when ordered deletion is enabled, marked snapshots can accumulate. A period of zero or negative configuration would be unsafe for `Timer.scheduleAtFixedRate`.

## Test Signals

Tests should cover idempotent scheduling/canceling, no-op when no snapshots are marked deleted, selecting only first deleted snapshots, actual GC through namesystem, exception logging paths, and ordered-deletion integration where a later snapshot is marked then eventually removed after earlier snapshots clear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/SnapshotDeletionGc.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/SnapshotDiffInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/SnapshotDiffInfo.java

## Purpose

`SnapshotDiffInfo` accumulates the full, non-paginated difference between two snapshots or a snapshot and current state. It records modified files/directories, directory child diffs, rename source/target pairs, traversal statistics, and generates a `SnapshotDiffReport`.

## Important APIs, Types, And Functions

The package-private class stores `snapshotRoot`, `snapshotDiffScopeDir`, `from`, `to`, a sorted `diffMap`, `dirDiffMap`, `renameMap`, and stats counters. `RenameEntry` stores source and target byte-array paths. Key methods are `addDirDiff`, `addFileDiff`, `setRenameTarget`, stats increment methods, `isFromEarlier`, and `generateReport`.

## Control Flow

`DirectorySnapshottableFeature` recursively calls `addDirDiff` and `addFileDiff`. Directory diffs add the directory to `diffMap`, store its `ChildrenDiff`, and detect renames by matching created references and deleted `INodeReference.WithName` entries with the same inode ID. `generateReport` walks `diffMap` in inode-path order, emits a MODIFY entry for every changed inode, then expands directory child diffs into CREATE, DELETE, or RENAME entries depending on direction and completed rename pairs.

## State And Persistence Behavior

The class is request-scoped and not persisted. It holds references to live/snapshot inode objects and byte-array relative paths while a diff RPC is computed. The generated `DiffStats` carries traversal counts and child-listing time into the response.

## Dependencies And Integration Points

It depends on HDFS protocol `SnapshotDiffReport`, inode classes, `ChildrenDiff`, `INodeReference`, Guava `SignedBytes`, and `ChunkedArrayList`. It is used by `SnapshotManager.diff` through `DirectorySnapshottableFeature.computeDiff`.

## Risks And Edge Cases

The recursive inode comparator compares parent chains and local names, so it assumes stable inode parent links during computation. Rename detection needs both source and target; incomplete pairs are reported as create/delete. Direction reversal flips create/delete and rename source/target. The report always includes MODIFY before child-level entries for changed directories. Large diffs can grow memory because this is the full-report path.

## Test Signals

Tests should cover create/delete/modify/rename reports in both directions, incomplete rename pairs, descendant-scoped paths, sorted output order, stats counters, current-state comparisons with null snapshots, and large reports using `ChunkedArrayList`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/SnapshotDiffInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/SnapshotDiffListingInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/SnapshotDiffListingInfo.java

## Purpose

`SnapshotDiffListingInfo` accumulates a bounded page of snapshot diff entries for the listing-style snapshot diff API controlled by `dfs.snapshotDiff-report.limit`. It tracks where computation stopped so clients can resume across RPC calls.

## Important APIs, Types, And Functions

Important state includes `maxEntries`, `snapshotRoot`, `snapshotDiffScopeDir`, `from`, `to`, `lastPath`, `lastIndex`, and separate `modifiedList`, `createdList`, and `deletedList`. Main APIs are `addDirDiff`, `addFileDiff`, `setLastPath`, `setLastIndex`, `getEarlier`, `getLater`, `isFromEarlier`, and `generateReport`.

## Control Flow

As recursive diff traversal finds a changed directory, `addDirDiff` first emits a modified directory entry if room remains, then appends created entries from the `ChildrenDiff`, then deleted entries, computing rename targets for deleted `WithName` references. If the page fills, it records the parent path and an index into the created/deleted stream and returns false to stop traversal. File changes are added as modified entries or set the last path if the page is full. `generateReport` returns the page plus cursor state.

## State And Persistence Behavior

The object is request-scoped and not persisted. Cursor fields `lastPath` and `lastIndex` are returned to clients in `SnapshotDiffReportListing` so the next RPC can resume. The class stores paths as byte arrays to match internal HDFS path handling.

## Dependencies And Integration Points

It depends on `SnapshotDiffReportListing`, `ChildrenDiff`, inode/reference classes, `DFSUtilClient` path byte helpers, and `ChunkedArrayList`. It is produced by `DirectorySnapshottableFeature.computeDiff` and returned by `SnapshotManager.diff` listing overload.

## Risks And Edge Cases

The index cursor spans created and deleted lists by offsetting deleted indexes by created-list size; off-by-one errors can duplicate or skip entries. `maxEntries` applies across all three lists. Resume path logic in the caller must align with `lastPath` and `lastIndex`. Rename target discovery is scoped to `snapshotDiffScopeDir`, which can differ from the root.

## Test Signals

Tests should force page boundaries before directory modify entries, inside created lists, inside deleted lists, and at file modifications. They should verify resume cursor correctness, no duplicate/skipped entries across pages, rename target inclusion, direction flags, and zero/one-entry limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/SnapshotDiffListingInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/SnapshotFSImageFormat.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/SnapshotFSImageFormat.java

## Purpose

`SnapshotFSImageFormat` is the legacy binary FSImage helper for snapshot data. It saves and loads snapshot IDs, snapshot quota, file and directory diff lists, created/deleted child lists, and reference-node maps outside the protobuf image path.

## Important APIs, Types, And Functions

Top-level APIs include `saveSnapshots`, `saveDirectoryDiffList`, `saveFileDiffList`, `loadFileDiffList`, `loadCreated`, `loadSnapshotList`, and `loadDirectoryDiffList`. Internal helpers include `saveINodeDiffs`, `loadFileDiff`, `loadCreatedList`, `loadDeletedList`, `loadSnapshotINodeInDirectoryDiff`, and `loadDirectoryDiff`. Nested `ReferenceMap` serializes and reloads `INodeReference.WithCount` objects while avoiding duplicate referred subtree writes.

## Control Flow

Saving writes snapshots by name-order ID list plus quota, and writes diff lists in reverse order so created-list names can resolve against posterior diffs during load. File diff loading reads snapshot ID, file size, and optional file attributes, then prepends each diff while threading posterior references. Directory diff loading reads snapshot ID, child size, snapshot-root/copy data, created-list names resolved through `loadCreated`, deleted inode records, and builds a `DirectoryDiff` with the current first diff as posterior.

## State And Persistence Behavior

This class persists the same logical snapshot state as the protobuf format but through `DataInput`/`DataOutput`. Created lists store names only; deleted lists store full inode images. `ReferenceMap` persists referred inodes once and subsequent references by ID, and tracks directory IDs whose subtrees have already been processed.

## Dependencies And Integration Points

It depends on `FSImageFormat.Loader`, `FSImageSerialization`, inode and attribute classes, `DirectoryWithSnapshotFeature`, `FileDiffList`, `Snapshot`, `INodeReference`, and HDFS snapshot diff tooling. It is retained for older FSImage compatibility and upgrade paths.

## Risks And Edge Cases

Created-list resolution can fail if reverse diff order or current children are inconsistent, producing an `IOException`. Reference-map consistency is required for renamed nodes and shared subtrees. The older file diff writer does not write block arrays here, unlike protobuf snapshot diff handling, so compatibility expectations must remain clear. Snapshot root versus ordinary snapshot copy is encoded with booleans and must be read in the same order.

## Test Signals

Tests should cover legacy FSImage save/load for snapshots, created-list resolution through posterior deleted entries and current children, deleted inode block-map updates, reference reuse, snapshot quota restoration, and compatibility with directories/files containing ACLs, XAttrs, quotas, and references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/SnapshotFSImageFormat.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/SnapshotManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/SnapshotManager.java

## Purpose

`SnapshotManager` is the NameNode manager for snapshottable directories and snapshots. It enforces snapshot configuration and limits, creates/deletes/renames snapshots, lists snapshot metadata, computes diff reports, handles ordered deletion policy, registers JMX stats, and persists global snapshot counters.

## Important APIs, Types, And Functions

Important state includes `FSDirectory`, capture/open-file flags, descendant diff flag, snapshot limits, ordered-deletion flag, `numSnapshots`, `snapshotCounter`, and `snapshottables`. Key APIs include `setSnapshottable`, `resetSnapshottable`, `createSnapshot`, `deleteSnapshot`, `renameSnapshot`, `getSnapshottableDirListing`, `getSnapshotListing`, `diff` overloads, `write`, `read`, `registerMXBean`, `shutdown`, `chooseDeletedSnapshot`, and helper assertions for ordered deletion. `DELETION_ORDERED` is a thread-local exposed to diff cleanup code.

## Control Flow

Construction reads configuration, validates per-directory limit not exceeding filesystem limit, and initializes `DirectoryDiffListFactory`. Creating a snapshot validates the directory, ID space, filesystem limit, and per-directory limit through `DirectorySnapshottableFeature`, then increments counters. Deletion either marks a non-earliest snapshot deleted and renames it when ordered deletion is enabled, or removes it immediately and decrements the global count. Diff calls resolve the snapshot root or allowed descendant scope and delegate recursive computation to the directory feature. JMX beans are built by iterating snapshottable directories and snapshots.

## State And Persistence Behavior

`snapshotCounter` and `numSnapshots` are written to FSImage along with snapshots. The `snapshottables` map is reconstructed during image load. Ordered deletion state is persisted through snapshot-root XAttrs and renamed snapshot roots, not through `SnapshotManager` fields alone. The manager's map is a `ConcurrentHashMap`, but higher-level operations still require FSNamesystem/FSDirectory locks.

## Dependencies And Integration Points

The manager integrates with `FSDirectory`, `FSNamesystem`, `INodeDirectory`, `DirectorySnapshottableFeature`, `LeaseManager`, FSImage formats, edit-log replay, `FSDirXAttrOp`, HDFS protocol status/report classes, MBeans, and `SnapshotDeletionGc`.

## Risks And Edge Cases

Snapshot ID rollover is unsupported after the 28-bit max. Ordered deletion requires only the first snapshot to be physically deleted; deleting later snapshots first creates XAttr-marked entries for GC. Nested snapshottable checks are O(number of snapshottable directories) and can be disabled only for tests. Descendant diff behavior is configuration-dependent. `shutdown` assumes a registered MBean name. `getSnapshottableAncestorDir` has subtle ancestor logic for files versus directories.

## Test Signals

Tests should cover config validation, snapshot ID exhaustion, filesystem and per-directory limits, nested snapshottable rejection, root snapshottable reset behavior, create/delete/rename edit-log replay, ordered deletion marking and GC selection, snapshot listings and JMX beans, descendant-scoped diffs, FSImage counter round trip, and shutdown/register behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/SnapshotManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/SnapshotStatsMXBean.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/SnapshotStatsMXBean.java

## Purpose

`SnapshotStatsMXBean` is the JMX management interface for exposing snapshot-related NameNode statistics.

## Important APIs, Types, And Functions

It declares two methods: `getSnapshottableDirectories()`, returning `SnapshottableDirectoryStatus.Bean[]`, and `getSnapshots()`, returning `SnapshotInfo.Bean[]`.

## Control Flow

There is no implementation in this file. `SnapshotManager` implements the interface, registers it as the `NameNode:SnapshotInfo` MBean, and fills the bean arrays by iterating current snapshottable directories and snapshots.

## State And Persistence Behavior

The interface has no state and no persistence. Returned beans reflect live `SnapshotManager` state at the moment the implementation is invoked.

## Dependencies And Integration Points

It depends on HDFS protocol bean types `SnapshotInfo.Bean` and `SnapshottableDirectoryStatus.Bean`. It integrates with Hadoop metrics/JMX infrastructure through `SnapshotManager.registerMXBean`.

## Risks And Edge Cases

Changing method names or return types changes the JMX contract. Implementations should avoid returning mutable internal objects, and large numbers of snapshots can make bean array construction expensive.

## Test Signals

Tests should verify MBean registration exposes both attributes, returned beans match snapshot manager listings, empty states return empty arrays, and unregistering on shutdown removes the MBean.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/SnapshotStatsMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/BlockMoveTaskHandler.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/BlockMoveTaskHandler.java

## Purpose

`BlockMoveTaskHandler` is the SPS abstraction for submitting concrete block movement tasks. It decouples the Storage Policy Satisfier from whether a move is sent directly to a DataNode or scheduled through NameNode/DataNode heartbeat mechanisms.

## Important APIs, Types, And Functions

The interface declares `submitMoveTask(BlockMovingInfo blkMovingInfo) throws IOException`. `BlockMovingInfo` carries block, source, target, and storage-type movement details.

## Control Flow

Implementations receive a planned block move from SPS scheduling code and submit it to the chosen transport. This interface itself has no control flow beyond the checked exception contract.

## State And Persistence Behavior

The interface has no state and no persistence. Implementations are expected to interact with live DataNode/NameNode channels and rely on later block reports or movement completion notifications for progress.

## Dependencies And Integration Points

It depends on `BlockStorageMovementCommand.BlockMovingInfo` and is mirrored by `Context.submitMoveTask`. It integrates with `StoragePolicySatisfier` block-move scheduling and movement-attempt tracking.

## Risks And Edge Cases

Implementations must handle duplicate submissions, unavailable DataNodes, stale storage reports, and partial failures without losing retry visibility. Throwing `IOException` should leave higher layers able to retry or requeue the file.

## Test Signals

Tests should mock implementations and verify SPS submits the expected `BlockMovingInfo`, propagates or handles `IOException`, and records attempted items only when submission semantics warrant it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/BlockMoveTaskHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/BlockMovementListener.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/BlockMovementListener.java

## Purpose

`BlockMovementListener` is the callback interface used to notify SPS that block movement attempts have finished or been tried, allowing SPS to recheck storage policy satisfaction and retry as needed.

## Important APIs, Types, And Functions

It declares `notifyMovementTriedBlocks(Block[] moveAttemptFinishedBlks)`. The input array contains blocks whose movement attempt completion was reported.

## Control Flow

DataNode or NameNode integration code calls the listener with finished blocks. SPS then consumes the blocks through attempted-item tracking, removes completed block entries, and requeues associated files for policy re-evaluation.

## State And Persistence Behavior

The interface has no state. Movement completion state is transient and maintained by implementations such as `BlockStorageMovementAttemptedItems` and the owning `SPSService`.

## Dependencies And Integration Points

It depends on HDFS protocol `Block` and integrates with `Context.notifyMovementTriedBlocks`, `SPSService.notifyStorageMovementAttemptFinishedBlk`, and DataNode block movement reports.

## Risks And Edge Cases

Callbacks can contain duplicate or stale block IDs, blocks from unknown attempts, or completions for only one target storage location. Implementations need idempotent handling and should not assume success means the file's policy is already satisfied.

## Test Signals

Tests should notify known, unknown, duplicate, and partial movement blocks and verify attempted-item queues, retry queues, and policy recheck behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/BlockMovementListener.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/BlockStorageMovementAttemptedItems.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/BlockStorageMovementAttemptedItems.java

## Purpose

`BlockStorageMovementAttemptedItems` tracks files whose block movement commands have been submitted to DataNodes. It watches for reported block movement completions, removes finished block targets, and requeues timed-out or completed files for another SPS policy-satisfaction check.

## Important APIs, Types, And Functions

Important state includes `storageMovementAttemptedItems`, `scheduledBlkLocs`, `movementFinishedBlocks`, monitor flags/thread, timeouts, the needed queue, context, and service. Key methods are `add`, `notifyReportedBlock`, `matchesReportedBlock`, `start`, `stop`, `stopGracefully`, `blocksStorageMovementUnReportedItemsCheck`, `blockStorageMovementReportedItemsCheck`, getters for tests, and `clearQueues`.

## Control Flow

SPS calls `add` with assigned blocks and target storage-node pairs. When a DataNode reports a block on a target storage type, `notifyReportedBlock` checks the scheduled locations, removes the matching pair, calls `context.notifyMovementTriedBlocks`, and when all target pairs for the block report, enqueues the block into `movementFinishedBlocks` and removes it from `scheduledBlkLocs`. The monitor thread periodically drains finished blocks and removes them from attempted file records; when a file has no remaining blocks, it adds an `ItemInfo` with incremented retry count to `BlockStorageMovementNeeded`. The same monitor also requeues attempted items whose last attempt/report time exceeds `selfRetryTimeout`.

## State And Persistence Behavior

All state is in-memory and cleared on stop. No attempted movement state is persisted across NameNode restart; SPS relies on xAttrs/queues and later scans to recover work. Timeouts are configured from SPS recheck and self-retry configuration keys.

## Dependencies And Integration Points

It depends on `SPSService`, `Context`, `BlockStorageMovementNeeded`, `StoragePolicySatisfier.AttemptedItemInfo`, `StorageTypeNodePair`, HDFS `Block`, `DatanodeInfo`, `StorageType`, and Hadoop `Daemon`. It is central to feedback between DataNode reports and SPS retry scheduling.

## Risks And Edge Cases

`matchesReportedBlock` iterates and removes from a set during enhanced-for iteration, then returns immediately; this relies on no further iterator use after removal. A block can be reported by one target but not all targets, leaving the file attempted until timeout. Completed files are requeued for policy recheck rather than declared done, so retry counts must not be interpreted as only failures. The monitor exits on `IOException`, which can stop further attempt processing. Synchronization is split between attempted list, scheduled map, and finished queue.

## Test Signals

Tests should cover successful block reports for all target pairs, partial reports followed by timeout, unknown reports, duplicate reports, monitor start/stop/interrupt, IOException from reported-item checks, configured timeouts, queue clearing, and retry count increments for both timeout and finished-block requeue paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/BlockStorageMovementAttemptedItems.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/BlockStorageMovementNeeded.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/BlockStorageMovementNeeded.java

## Purpose

`BlockStorageMovementNeeded` is the SPS queue for files needing storage policy satisfaction work. It also tracks directory scan progress so SPS can remove the satisfier xAttr once every file under a requested directory has been processed.

## Important APIs, Types, And Functions

Important state includes `storageMovementNeeded`, `pendingWorkForDirectory`, `Context`, `SPSPathIdProcessor`, and its daemon. Public APIs include `add`, `addAll`, `get`, `size`, `clearAll`, `removeItemTrackInfo`, `clearQueuesWithNotification`, `activate`, `close`, `markScanCompletedForDir`, and test setters/getters for status clearance. Nested `DirPendingWorkInfo` tracks `pendingWorkCount` and `fullyScanned`.

## Control Flow

Files are added directly or as scan results for a start path. Directory scan additions update pending-work counts and mark scans complete when the collector reports no more files. `SPSPathIdProcessor` runs while context is running, skips work in safe mode, pulls the next SPS path from context, scans files, removes xAttr for empty/completed directories, retries scan failures up to three times, and sleeps while idle or after errors. When movement for an item succeeds, `removeItemTrackInfo` decrements directory pending count and removes the directory xAttr when the scan is fully done and all child work is complete; file start paths remove their xAttr directly.

## State And Persistence Behavior

The queue and pending-work map are in-memory. Persistent intent is represented outside this class by SPS xAttrs/hints accessed through `Context.getNextSPSPath` and `removeSPSHint`. `clearQueuesWithNotification` removes outstanding hints before clearing local state.

## Dependencies And Integration Points

It depends on `Context` for safe mode, scanning, hint retrieval/removal, and file existence checks. It integrates with `SPSService.addFileToProcess`, recursive `FileCollector` implementations, `BlockStorageMovementAttemptedItems`, and NameNode xAttr state for SPS requests.

## Risks And Edge Cases

Directory pending counts can go negative if decrement calls outnumber queued file additions, but `isDirWorkDone` treats `<= 0` as done once fully scanned. If scanning fails three times, the path is skipped and may retain or lose external hint depending on subsequent handling. Safe mode causes the processor loop to spin without the normal idle sleep in the safe-mode branch. `clearQueuesWithNotification` calls synchronized `get` while already synchronized, relying on Java reentrant locks.

## Test Signals

Tests should cover file and directory item queueing, scan-complete marking, empty directory xAttr removal, child completion decrement/removal, deleted start paths, force clearing with hint cleanup, safe-mode behavior, scan retry limit, interruption, and concurrent add/get/remove access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/BlockStorageMovementNeeded.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/Context.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/Context.java

## Purpose

`Context` is the NameNode-facing service contract used by SPS code. It exposes lifecycle, namespace, storage policy, DataNode report, scanning, block move submission, and movement notification operations without binding SPS internals directly to `FSNamesystem` implementation details.

## Important APIs, Types, And Functions

The interface declares `isRunning`, `isInSafeMode`, `getNetworkTopology`, `isFileExist`, `getStoragePolicy`, `removeSPSHint`, `getNumLiveDataNodes`, `getFileInfo`, `getLiveDatanodeStorageReport`, `getNextSPSPath`, `scanAndCollectFiles`, `submitMoveTask`, and `notifyMovementTriedBlocks`.

## Control Flow

SPS queue workers call lifecycle/safe-mode methods to decide whether to scan, pull paths through `getNextSPSPath`, scan recursively through `scanAndCollectFiles`, query file and DataNode state for block movement planning, submit movement commands, and receive completion notifications. Implementations bridge these calls to NameNode namespace locks and block manager state.

## State And Persistence Behavior

The interface itself has no state. Persistent SPS intent is represented by NameNode hints/xAttrs that implementations expose via `getNextSPSPath` and mutate via `removeSPSHint`. Live DataNode and topology state is transient.

## Dependencies And Integration Points

It depends on `Block`, `BlockStoragePolicy`, `HdfsFileStatus`, `DatanodeStorageReport`, `BlockMovingInfo`, `NetworkTopology`, and `StoragePolicySatisfier.DatanodeMap`. It is consumed by `BlockStorageMovementNeeded`, `DatanodeCacheManager`, attempted-item tracking, and block move scheduling.

## Risks And Edge Cases

Implementations must obey NameNode locking rules and avoid returning stale namespace objects while SPS worker threads are active. Safe mode, deleted files, unavailable policies, and missing DataNode reports must be handled without leaking SPS hints. Network topology must correspond to the same DataNode map used for scheduling.

## Test Signals

Tests should use mock contexts to cover safe-mode pausing, missing files, hint removal failures, stale DataNode reports, move submission failures, movement notifications, and topology/datanode-map consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/Context.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/DatanodeCacheManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/DatanodeCacheManager.java

## Purpose

`DatanodeCacheManager` caches live DataNode storage reports for SPS block-movement planning. It refreshes reports at a configured interval, filters out storage volumes without remaining capacity, builds an SPS `DatanodeMap`, and caches the matching network topology.

## Important APIs, Types, And Functions

State includes `DatanodeMap datanodeMap`, `NetworkTopology cluster`, `refreshIntervalMs`, and `lastAccessedTime`. The main API is `getLiveDatanodeStorageReport(Context spsContext)`, with package-private `getCluster()` for the topology.

## Control Flow

Each call checks monotonic time since the last access. If the refresh interval elapsed, it resets the map, fetches live DataNode storage reports from context, walks each storage report, records only storage types and remaining sizes where remaining space is positive, adds the target DataNode to the map, and asks context for a topology built from that map. Calls before the interval expires return the existing map and cluster.

## State And Persistence Behavior

The cache is entirely in-memory and is not persisted. `lastAccessedTime` is updated on every call, so refresh cadence is based on access intervals. The returned `DatanodeMap` is the mutable cached object.

## Dependencies And Integration Points

It depends on SPS `Context`, `StoragePolicySatisfier.DatanodeMap`, `DatanodeStorageReport`, `StorageReport`, storage types, `NetworkTopology`, DFS configuration keys, and monotonic time. It feeds SPS target selection.

## Risks And Edge Cases

Updating `lastAccessedTime` before successful refresh means a failed refresh can delay the next attempt depending on caller behavior. There is no internal synchronization, so concurrent SPS callers could race on reset/add/topology updates. Storage with zero remaining capacity is excluded, which is appropriate for target selection but can hide otherwise live nodes. A zero refresh interval refreshes every call.

## Test Signals

Tests should verify refresh interval behavior, filtering of zero-capacity storage, topology refresh, cache reuse before interval expiry, IOException propagation from context, and behavior under empty live reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/DatanodeCacheManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/FileCollector.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/FileCollector.java

## Purpose

`FileCollector` is the SPS abstraction for recursively scanning a path and adding files that need storage policy satisfaction to the SPS needed-work queue.

## Important APIs, Types, And Functions

It declares `scanAndCollectFiles(long path) throws IOException, InterruptedException`, where `path` is a file or directory inode/path ID.

## Control Flow

`BlockStorageMovementNeeded.SPSPathIdProcessor` or `Context.scanAndCollectFiles` invokes an implementation for an SPS start path. The implementation walks namespace children, identifies candidate files, and adds them to `SPSService` or `BlockStorageMovementNeeded`, marking directory scan completion when done.

## State And Persistence Behavior

The interface has no state. Implementations read live namespace state and produce transient queue entries. Persistent SPS intent remains in path hints/xAttrs until scan and movement completion remove them.

## Dependencies And Integration Points

It depends only on Java exceptions and Hadoop classification annotations. It integrates with `Context`, `SPSService.addAllFilesToProcess`, and `BlockStorageMovementNeeded` directory pending-work tracking.

## Risks And Edge Cases

Implementations must handle interruption promptly, avoid holding NameNode locks for excessive time, handle deleted paths and permission/namespace errors, and correctly report scan completion for empty directories.

## Test Signals

Tests should cover recursive directory scans, file start paths, empty directories, interruption, deleted paths, batched queue additions, and scan-completion markers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/FileCollector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/ItemInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/ItemInfo.java

## Purpose

`ItemInfo` is the small value object SPS uses to track a file needing storage policy satisfaction and the original start path that caused it to be queued.

## Important APIs, Types, And Functions

It stores `startPathId`, `fileId`, and `retryCount`. Constructors initialize retry count to zero or a supplied value. Accessors are `getStartPath`, `getFile`, `isDir`, `getRetryCount`, and `increRetryCount`.

## Control Flow

Directory scans create `ItemInfo` for child files with `startPathId` set to the directory request and `fileId` set to the child file. File-level SPS requests use the same ID for both. Attempted-item retry paths construct new `ItemInfo` objects with incremented retry counts before requeueing them for policy recheck.

## State And Persistence Behavior

`ItemInfo` is transient in-memory queue state and is not serialized. The durable association with a user SPS request is held externally by SPS hints/xAttrs for the start path.

## Dependencies And Integration Points

It is used by `BlockStorageMovementNeeded`, `BlockStorageMovementAttemptedItems`, and `SPSService` queue APIs. It has no dependencies beyond Hadoop annotations.

## Risks And Edge Cases

`isDir` means "the item came from a directory start path", not that `fileId` itself is a directory. Fields are mutable only through retry increment, so callers creating retry objects must preserve the correct start/file IDs. There is no equality/hash implementation, so queue de-duplication cannot rely on object equality.

## Test Signals

Tests should verify constructor defaults, retry incrementing, `isDir` for file and directory-origin items, and retry requeue behavior preserving IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/ItemInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/SPSService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/SPSService.java

## Purpose

`SPSService` is the lifecycle and queue-management interface for the Storage Policy Satisfier service. It lets the NameNode initialize, start, stop, query, feed, and notify SPS implementations.

## Important APIs, Types, And Functions

The interface declares `init`, `start`, `stopGracefully`, `stop`, `isRunning`, `addFileToProcess`, `addAllFilesToProcess`, `processingQueueSize`, `getConf`, `markScanCompletedForPath`, and `notifyStorageMovementAttemptFinishedBlk`.

## Control Flow

NameNode code initializes the service with a `Context`, starts it in a configured `StoragePolicySatisfierMode`, and submits file or directory scan results as `ItemInfo` queues. Implementations expose queue size for monitoring, mark directory scans complete, handle DataNode block movement completion reports, and stop either gracefully or forcefully with optional hint cleanup.

## State And Persistence Behavior

The interface itself has no state. Implementations maintain in-memory queues, daemon threads, attempted-item tracking, DataNode caches, and configuration. Persistent SPS requests live in NameNode hints/xAttrs that implementations remove through `Context`.

## Dependencies And Integration Points

It depends on `Context`, `Configuration`, `ItemInfo`, `StoragePolicySatisfierMode`, `DatanodeInfo`, `StorageType`, and `Block`. It is the top-level contract implemented by `StoragePolicySatisfier` and used by NameNode SPS plumbing.

## Risks And Edge Cases

Implementations must define clear semantics for force stop versus graceful stop, avoid accepting work before `init`, handle duplicate `start` or `stop` calls, and safely process movement completion notifications for blocks no longer tracked. Queue-size reporting can be transient under concurrent worker activity.

## Test Signals

Tests should cover lifecycle ordering, graceful and forced stop behavior, queue additions for single files and directory batches, scan-complete handling, configuration access, running-state transitions, and block movement completion notification paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/SPSService.java -->
