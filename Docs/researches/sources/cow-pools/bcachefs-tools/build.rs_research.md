# File Research: sources/cow-pools/bcachefs-tools/build.rs

- Top-level Cargo build script.
- Links the Rust binary against local static `libbcachefs.a` with whole-archive semantics.
- Links required system libraries: urcu, zstd, blkid, uuid, sodium, z, lz4, udev, keyutils, aio, and unwind.
- Adds `-rdynamic` for binaries so C-side symbol/backtrace helpers can resolve static symbols.
- Notes that `fuser` uses `/dev/fuse` directly, so libfuse3 is not linked here.
