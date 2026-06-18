# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/data/io.rs

- Rust Future wrappers for bcachefs read and write operations backed by C shims.
- Declares C submit functions `rust_write_submit` and `rust_read_submit`.
- Defines max I/O size as 1 MiB, matching `RUST_IO_MAX`.
- `WriteOp` allocates pinned state containing `bch_write_op`, bio vecs, completion flag, and waker; submit errors are surfaced as `BchError`.
- `ReadOp` similarly pins `bch_read_bio` and completion state, with endio callback recovering the container by offset.
- Polling stores a waker, checks atomic completion with acquire/release ordering, and returns C error conversion.
- Includes a simple spin/yield `block_on` executor and no-op waker.
