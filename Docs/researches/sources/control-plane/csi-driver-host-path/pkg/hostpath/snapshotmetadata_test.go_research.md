## sources/control-plane/csi-driver-host-path/pkg/hostpath/snapshotmetadata_test.go

Purpose: unit-tests hostpath snapshot metadata block scanning for both delta and allocated metadata. The tests exercise `newFileBlockReader`, `seekToStartingOffset`, and `getChangedBlockMetadata` with synthetic sparse-like image files built from fixed-size 4096-byte blocks.

Control flow is table-driven. Delta cases create source and target files, overwrite selected target blocks, then loop until `io.EOF`, collecting pages and validating both total metadata and page count under `maxResult`. Allocated cases use an empty base path and validate that all target blocks are reported, with variable-length metadata coalescing contiguous ranges.

State and persistence are temporary files only; helpers create and mutate block contents with `os.CreateTemp`, `Seek`, and `Write`. Dependencies include CSI `BlockMetadata`, hostpath `state.BlockSizeBytes`, and the unlisted block reader implementation. Risks covered include off-by-one offsets, different source/target sizes, pagination, starting offsets, and variable-length coalescing. Gaps include gRPC stream behavior, cancellation/deadline handling, invalid offsets, and real sparse file allocation semantics.
