# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zpl_file_range.c

## Purpose
Implements Linux range-copy and reflink-style operations for ZFS block cloning. It maps `copy_file_range`, `FICLONE`, `FICLONERANGE`, and remap callbacks to `zfs_clone_range()` where possible, with generic copy fallback for `copy_file_range`.

## Main APIs and Data
- `zpl_clone_file_range_impl()` is the shared block-clone implementation.
- `zpl_copy_file_range()` attempts clone first, then falls back to generic byte-copy APIs when available and appropriate.
- `zpl_remap_file_range()` implements modern remap/reflink entry point.
- `zpl_clone_file_range()` supports older clone-file-range VFS API.
- `zpl_dedupe_file_range()` currently returns unsupported.

## Control Flow
The clone implementation checks the global block-clone tunable and destination pool feature flag `SPA_FEATURE_BLOCK_CLONING`. It locks source shared when source and destination differ, locks destination exclusive, holds credentials, marks fstrans, and calls `zfs_clone_range()` with mutable offsets/length. The returned cloned length may be shorter than requested.

`copy_file_range()` requires zero flags, tries clone, and falls back for `EOPNOTSUPP`, `EINVAL`, `EXDEV`, or `EAGAIN` depending on available kernel helper (`generic_copy_file_range`, `splice_copy_file_range`, or old-kernel `-EOPNOTSUPP` signaling).

`remap_file_range()` rejects unsupported flags, rejects dedupe, expands zero length to EOF, attempts clone, and enforces full-length cloning unless `REMAP_FILE_CAN_SHORTEN` is set. The older `clone_file_range()` similarly requires full cloning.

## Integration Points
This file bridges Linux file-range APIs to ZFS block cloning in `zfs_vnops` and feature detection in `zfeature`. It is referenced by `zpl_file_operations`.

## Invariants and Edge Cases
- Destination pool must have block cloning enabled.
- Dedupe is explicitly unsupported.
- Zero-length clone/remap means clone from offset to EOF.
- Short clones are valid only where the VFS API allows shortening.
- Copy fallback behavior depends on kernel version/configuration.

## Risks and Testing Signals
Test cross-filesystem failures, same-file cloning, dirty data causing shortened clones, old and new kernel VFS entry points, copy fallback correctness, feature-disabled behavior, and unsupported dedupe requests.
