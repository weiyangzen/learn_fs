# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/PositionStripeReader.java

`PositionStripeReader` is a `StripeReader` for positional reads of a complete aligned erasure-coded stripe. It prepares decode inputs backed by one pooled `ByteBuffer`, creates missing data/parity chunks, decodes, and returns the buffer to the pool on close.

Important methods are `prepareDecodeInputs()`, `prepareParityChunk(int)`, `decode()`, `initDecodeInputs(AlignedStripe)`, and `close()`. The only field introduced here is `codingBuffer`.

`prepareDecodeInputs()` lazily initializes `decodeInputs`. `initDecodeInputs()` computes span length, allocates a buffer large enough for data plus parity chunks from `DFSStripedInputStream`'s buffer pool, creates `ECChunk` slices for data indexes, and attaches missing aligned-stripe chunks. `prepareParityChunk()` validates that the target index is parity and currently missing, creates a parity `ECChunk` at the correct offset, and stores a `StripingChunk`. `decode()` finalizes inputs and calls `decodeAndFillBuffer(true)`.

State is per-read and memory-only; `close()` nulls decode inputs and returns `codingBuffer` to the pool. Dependencies include `StripeReader`, `AlignedStripe`, `StripingChunk`, `ECChunk`, `RawErasureDecoder`, `DFSStripedInputStream`, corrupted-block tracking, EC policy, and located block metadata.

Risks include buffer partition offset mistakes corrupting adjacent chunks, leaked pooled buffers if `close()` is skipped, and reliance on superclass ownership semantics because this close method does not call a superclass close. Test signals include lazy allocation, chunk offset layout, parity preparation validation, decode with missing chunks, direct/heap buffer behavior, and buffer return on close.
