<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/reader.rs -->
## sources/cloud-native/nydus/utils/src/reader.rs

### Purpose
This module provides two reader adapters: one for reading a fixed byte range from a file descriptor without moving the file cursor, and one for tracking buffered-reader position while optionally computing a SHA-256 digest of bytes read.

### APIs, Types, and Control Flow
`FileRangeReader::new()` captures a `File` raw fd, offset, and remaining size. Its `Read` implementation clamps reads to the remaining range, calls `nix::sys::uio::pread()`, then advances internal offset and decreases remaining size. `BufReaderInfo<R>` wraps `BufReader<R>` inside `Arc<Mutex<BufReaderState<R>>>`, where state contains `reader`, `pos`, and a `Sha256` hasher. `read()` updates position and feeds the hasher if digest calculation is enabled. `seek()` updates `pos` to the underlying reader position, and `Clone` shares the same reader state.

### State, Dependencies, and Integration
The raw fd in `FileRangeReader` depends on the original `File` outliving the reader. `BufReaderInfo` state is shared across clones, so clones serialize reads through one mutex and observe the same position/hash. Digest updates use `crate::digest::DigestHasher`; pread errors are converted through the local `last_error!()` macro.

### Risks and Test Signals
The lifetime marker in `FileRangeReader` helps express borrow intent, but the struct stores only the fd, so misuse through manual lifetime extension would be dangerous. Seeking after digest calculation does not rewind or reset the digest, so callers must disable digesting or avoid seeks when computing blob digests. Tests cover fixed-range reads, partial reads, position tracking, digest enable/disable behavior, seek position updates, and clone state sharing.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/reader.rs -->
