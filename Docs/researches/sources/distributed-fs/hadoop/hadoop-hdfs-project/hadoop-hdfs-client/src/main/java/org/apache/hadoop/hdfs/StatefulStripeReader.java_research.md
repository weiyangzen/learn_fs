# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/StatefulStripeReader.java

Purpose: `StatefulStripeReader` specializes `StripeReader` for reading a complete `AlignedStripe` that belongs to a single stripe. It uses buffers owned by `DFSStripedInputStream` so decoded or fetched data can be placed into the current stripe buffer and parity buffer.

Important APIs/types/functions: constructor forwards the aligned stripe, EC policy, target blocks, block-reader state, corrupted-block tracker, raw erasure decoder, and striped input stream to the base class. Overrides are `prepareDecodeInputs()`, `prepareParityChunk(int)`, and `decode()`.

Control flow: `prepareDecodeInputs()` duplicates the current stripe buffer under synchronization on `dfsStripedInputStream`, creates the `decodeInputs` array if needed, and maps each data unit into a slice based on `alignedStripe` offset/span, cell size, and data index. Missing data chunks get `StripingChunk` wrappers around the same buffers. `prepareParityChunk()` validates that the target index is a parity slot and unprepared, slices the parity buffer for the stripe span, creates an `ECChunk`, and installs a `StripingChunk`. `decode()` finalizes inputs and calls `decodeAndFillBuffer(false)` because stateful reads already target the current stripe buffer.

State and persistence behavior: all state is transient and buffer backed. It mutates `decodeInputs` and `alignedStripe.chunks`; no file-system metadata is persisted. Synchronization is limited to safely duplicating the current stripe buffer reference.

Dependencies and integration points: depends on `StripeReader`, `DFSStripedInputStream`, `StripedBlockUtil`, `ECChunk`, `RawErasureDecoder`, `ErasureCodingPolicy`, and `LocatedBlock`. It participates in erasure-coded reads after block layout has produced an aligned stripe.

Risks: buffer slicing math is sensitive to `bufOff % cellSize`, `cellSize * i`, and span length. Bad alignment can corrupt data placement or decode inputs. Tests should cover single-stripe partial offsets, missing data chunks, parity read preparation, direct/non-direct decoder preferences through the base class, and decode behavior where output already resides in the current stripe buffer.
