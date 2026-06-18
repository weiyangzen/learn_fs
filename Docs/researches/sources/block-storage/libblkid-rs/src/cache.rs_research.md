# File Research: sources/block-storage/libblkid-rs/src/cache.rs

Purpose: Defines `BlkidCache`, the high-level Rust handle for libblkid cache operations.

Key APIs:
- `get_cache`, `put_cache`, `gc_cache`
- block-device probing: `probe_all`, `probe_all_new`, `probe_all_removable`
- cache lookups: `get_dev`, `get_tag_value`, `get_devname`, `find_dev_with_tag`, `verify`
- cached-device iteration through `BlkidDevIter`

Implementation notes:
- Wraps `libblkid_rs_sys::blkid_cache` plus a boolean tracking whether `blkid_put_cache` has already been called.
- Converts Rust strings/paths into `CString`; non-UTF-8 paths are rejected through `BlkidErr::InvalidConv`.
- Frees strings returned by libblkid with `libc::free`.

Notable risks:
- `put_cache(&mut self)` frees/releases the C cache but does not consume `self`; later method calls can use a stale pointer.
- `Drop` calls raw `free()` when `put_cache` was not called, instead of a libblkid-specific release API. If the cache owns nested allocations, this risks incomplete cleanup.
- `get_dev` wraps the returned pointer without a null check, so a null `blkid_dev` can enter safe Rust as `BlkidDev`.
