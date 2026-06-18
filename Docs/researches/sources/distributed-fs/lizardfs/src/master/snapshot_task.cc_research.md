# sources/distributed-fs/lizardfs/src/master/snapshot_task.cc

## Purpose

`snapshot_task.cc` implements `SnapshotTask`, a task-manager-backed recursive snapshot/clone operation that copies filesystem nodes and queues child clones for directories. The source was read as a complete 254-line implementation.

## Important APIs, Types, and Functions

Important methods are `cloneNodeTest`, `cloneToExistingNode`, `cloneToNewNode`, `cloneToExistingFileNode`, `cloneChunkData`, two `cloneDirectoryData` overload declarations with the const overload implemented here, `cloneSymlinkData`, `emitChangelog`, `cloneNode`, and `execute`.

## Control Flow

`execute` clones the current source inode to the destination parent/name, advances the iterator, optionally ignores missing sources, and splices locally generated child tasks into the global work queue. `cloneNode` resolves source and destination parent, rejects trash/reserved sources, checks quota/type/overwrite constraints, clones over an existing node or creates a new node, updates checksums, emits or simulates changelog version advancement, and validates requested destination inode. Directories queue child snapshot tasks when `enqueue_work_` is true.

## State and Persistence Behavior

Snapshotting mutates in-memory metadata by creating/replacing nodes, copying mode/owners/timestamps/goal/trashtime/chunks/symlink paths/devices, updating parent stats and quota usage for file sizes, incrementing chunk file references, and emitting `CLONE` changelog records when enabled. Without changelog emission it increments `gMetadata->metaversion` directly.

## Dependencies and Integration Points

Dependencies include filesystem checksum, metadata, operations, quota checks/updates, chunk reference updates, `TaskManager`, `HString`, and node type definitions. Restore replay uses `fs_clone_node`, which links to this task via metarestore CMake.

## Risks and Edge Cases

Quota checks for file size use a delta of 1 before actual chunk copy, so deeper quota validation may be elsewhere. Existing file replacement unlinks and recreates the file if length/chunks differ. Chunk IDs missing from chunk metadata are logged as structure errors but cloning continues. The header declares a non-const `cloneDirectoryData` overload not implemented in this file, implying either inline/unused linkage expectations or dead declaration. Ignoring missing sources converts `ENOENT` to success.

## Test Signals

Tests should cover cloning each node type, overwrite rules, destination inode mismatch, recursive directory cloning, quota failures, missing source ignore behavior, chunk reference increments, stats/quota updates, and changelog versus metarestore metaversion behavior.
