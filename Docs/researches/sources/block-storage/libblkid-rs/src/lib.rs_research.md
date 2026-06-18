# File Research: sources/block-storage/libblkid-rs/src/lib.rs

Purpose: Crate root for the Rust libblkid binding.

Key APIs:
- Public re-exports for cache, constants, device wrappers, device numbers, encoding, errors, partitions, probes, tags, topology, utilities, version helpers, `Uuid`, and `blkid_loff_t`.

Implementation notes:
- Enforces `#![deny(missing_docs)]`.
- Keeps most implementation modules private while exposing selected public types and functions.
- Enables deprecated probe methods only behind the `deprecated` feature.

Notable risks:
- The public API is intentionally close to libblkid, so unsafe C ownership/lifetime rules leak into wrapper design.
- The crate-level docs mention modified behavior for `blkid_get_dev_size`, but the implementation exposes `BlkidDev::devsize` rather than a direct `&Path` function.
