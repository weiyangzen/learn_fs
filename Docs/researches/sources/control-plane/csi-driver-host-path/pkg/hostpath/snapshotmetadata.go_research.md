# sources/control-plane/csi-driver-host-path/pkg/hostpath/snapshotmetadata.go

## Purpose
This file implements block-difference scanning helpers for the optional CSI SnapshotMetadata service. It compares target snapshot files with either zero blocks or a base snapshot file and returns changed block metadata in fixed or merged variable-length form.

## Important APIs, Types, And Functions
`fileBlockReader` owns optional base file, target file, current offset, block size, metadata type, and maximum result count. `newFileBlockReader` opens files and constructs the reader. Methods `seekToStartingOffset`, `Close`, and `getChangedBlockMetadata` manage file positioning/lifetime and scanning. Helpers include `openFiles`, `readFileBlock`, `blockChanged`, `createBlockMetadata`, and `extendBlock`.

## Control Flow
The reader opens the target and optional base files, seeks both to the starting offset, then repeatedly reads `blockSize` chunks until it accumulates `maxResult` changed blocks, reaches EOF, or context is canceled. Without a base file, it compares target blocks to zero blocks and reports allocated/non-zero blocks. With a base file, it compares base and target bytes. For `VARIABLE_LENGTH`, adjacent changed blocks extend the previous metadata entry instead of appending a new one. The reader advances its offset as it scans so callers can request subsequent batches.

## State, Persistence, And Dependencies
State is held in open file descriptors and the mutable offset. The code reads snapshot files but does not write them. Dependencies are Go `bytes`, `io`, `os`, context cancellation, CSI block metadata types, and klog.

## Integration Points
The optional snapshot metadata gRPC server uses these helpers to implement allocated and delta metadata streaming when `EnableSnapshotMetadata` is configured. Snapshot files are those created by controller snapshot methods.

## Risks
The buffer size is `blockSize`; very large block sizes allocate large buffers. If `blockSize` or `maxResult` validation is missing in callers, zero/negative values could cause incorrect behavior. Partial final blocks are reported with full `blockSize` metadata, which may overstate changed size at EOF. Sequential file reads under long streams can be expensive.

## Test Signals
The companion snapshot metadata tests outside this work item cover changed and allocated block metadata scenarios. Additional tests should include cancellation, partial final blocks, invalid block sizes, seek offsets, fixed versus variable-length merging, and close error handling.
