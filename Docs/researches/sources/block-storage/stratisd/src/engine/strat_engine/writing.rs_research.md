# File Research: sources/block-storage/stratisd/src/engine/strat_engine/writing.rs

## Purpose

This file provides small write helpers for device/file sector wiping, with a `SyncAll` abstraction so production `File`, buffered writers, and test cursors can share the same sync contract.

## Main API

`SyncAll` extends `Write` with `sync_all()`.

Implementations:

- `File`: delegates to `File::sync_all()`.
- `Cursor<T>` in tests: no-op sync, because data is in memory.
- `BufWriter<T>` where `T: SyncAll`: flushes the buffer and then syncs the wrapped writer.

`wipe_sectors(path, offset, length)` writes zeroed sectors at the given sector offset for the specified sector count. It delegates to private `write_sectors()` with a zeroed sector buffer.

## Internal Flow

`write_sectors(path, offset, length, buf)`:

1. Opens the path write-only.
2. Wraps it in a `BufWriter` whose capacity is the smaller of `1 MiB` and the requested byte length.
3. Seeks to `offset.bytes()`.
4. Writes the provided one-sector buffer `length` times.
5. Flushes and syncs via `SyncAll`.
6. Returns `StratisResult<()>`.

## Dependencies

- `devicemapper::{Sectors, IEC, SECTOR_SIZE}` for block units.
- `StratisResult` for project error propagation.
- Standard `File`, `OpenOptions`, `BufWriter`, `Seek`, and `Write`.

## Correctness Notes

- The helper writes whole sectors only; callers must provide sector-granular offsets and lengths.
- It syncs once after all writes, not after each sector.
- Integer conversions use project conversion macros, so offset/capacity conversion failures propagate rather than silently truncating.
- The function is used by thin-pool initialization to zero fresh thin metadata headers before device-mapper adopts them.
