## sources/cloud-native/overlaybd/src/overlaybd/zstd/zstdfile.cpp

Purpose: Photon read-only adaptor that exposes a sequential decompressed view over a ZSTD-framed compressed `IFile`.

Important types/functions: `ZStdAdaptorFile` derives from `VirtualReadOnlyFile`, owns or borrows an underlying `IFile`, maintains a `ZSTD_DStream`, input buffer sized by `ZSTD_DStreamInSize`, and a `ZSTD_inBuffer`. `read` fills caller output by reading compressed chunks and calling `ZSTD_decompressStream`. `open_zstdfile_adaptor` constructs the adaptor. `is_zstdfile` checks the 4-byte ZSTD magic header and seeks back to offset 0.

Control flow: `read` loops until the caller buffer is full or underlying EOF is reached. When the input buffer is exhausted it reads more compressed bytes. On `ZSTD_decompressStream` error it returns `EIO`. When a frame ends (`ret == 0`) it reinitializes the stream for a possible following frame. `fstat` delegates to the compressed file, so size is not decompressed size.

State/persistence: streaming state is in `ZSTD_DStream`, `m_buffer`, and `m_input`; persistent state is only the underlying compressed file. Dependencies are libzstd, Photon file abstractions, and logging.

Integration points: intended for consumers that only need sequential `read`; random access methods and `lseek` are unimplemented. Risks: `is_zstdfile` uses `read` then `lseek`, so it requires a seekable source and changes/readv state on unusual file objects; `read` returning compressed `fstat` size may confuse callers expecting raw size; no listed tests exercise multi-frame or error cases.
