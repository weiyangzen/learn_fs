# File Research: sources/cow-pools/bcachefs-tools/src/commands/strip_alloc.rs

## Purpose
Implements `bcachefs strip-alloc`, which strips allocation information from a clean filesystem for read-only/small-image use, with a capacity guard for reconstruction limits.

## Main Interfaces
- CLI struct: `Cli`
- Command export: `CMD = typed_cmd!("strip-alloc", ...)`
- Main handler: `cmd_strip_alloc`

## Behavior
- Opens supplied devices with `nostart`.
- If the filesystem is not clean, starts recovery, drops the fs handle, and loops to reopen.
- Computes total capacity across devices from `nbuckets * bucket_size`.
- Refuses to strip allocation info if total capacity exceeds 1 TiB.
- Calls C helper `rust_strip_alloc_do(fs.raw)` to perform the strip.
- Prints the first device path being stripped.

## Dependencies and Coupling
- Uses `device_scan::open_scan`.
- Uses raw `(*fs.raw).sb.clean`.
- Uses `bch2_fs_start` for recovery and `rust_strip_alloc_do` for stripping.
- Uses `fs.dev_get` and device member metadata for capacity calculation.

## Important Implementation Notes
- The loop retries after recovery until the filesystem opens clean.
- Capacity is computed in bytes by shifting bucket sectors by 9.

## Risks and Edge Cases
- The loop can repeat if recovery does not leave the filesystem clean.
- The 1 TiB limit is hardcoded based on allocation-info reconstruction capability.
- Recovery is triggered even though the command otherwise opens with `nostart`.
