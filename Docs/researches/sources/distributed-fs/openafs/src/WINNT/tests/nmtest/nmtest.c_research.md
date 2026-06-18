# sources/distributed-fs/openafs/src/WINNT/tests/nmtest/nmtest.c

## Purpose

`nmtest.c` generates and verifies deterministic block-oriented test files for Windows filesystem stress. It writes a file containing a metadata bitmap followed by 1024-byte pseudo-random data blocks derived from each block offset, optionally overwrites random blocks with a second deterministic variant, and later verifies every block against the bitmap.

## Important APIs, Types, and Functions

- Uses Win32 CryptoAPI (`CryptAcquireContext`, `CryptCreateHash`, `CryptHashData`, `CryptDeriveKey`, `CryptEncrypt`, `CryptGenRandom`) to generate deterministic block bytes.
- Uses Win32 file APIs with byte-range locking: `CreateFile`, `SetFilePointerEx`, `ReadFile`, `WriteFile`, `LockFileEx`, `UnlockFileEx`, `FlushFileBuffers`, and `GetFileSizeEx`.
- `hash_data` combines `offset` and `param` as the deterministic seed.
- `bitmap` stores magic `BMAGIC`, data length, data offset, and per-data-block overwrite bits.
- `allocbits()`, `setbit()`, and `getbit()` manage bitmap state.
- `write_bitmap()` and `read_bitmap()` serialize/deserialize the bitmap in block-sized chunks at the start of the file.
- `do_write_test()` implements `-w N M filename`; `do_verify_test()` implements `-r filename`.
- `parse_cmdline()` selects write or verify mode.

## Control Flow

Write mode rounds `N` and `M` up to `BLOCKSIZE`, creates/truncates the output file, allocates a bitmap whose data offset is block-aligned after the bitmap, initializes CryptoAPI, writes the bitmap header area, and sequentially writes deterministic `param=0` blocks for the full data range. It flushes and reopens the file for random access, then performs `M / BLOCKSIZE` random overwrite attempts: choose a random block in the data range, generate deterministic `param=1` data for that offset, lock/seek/write/unlock the block, and mark the bitmap bit. Finally it rewrites the bitmap so verification knows which blocks were overwritten.

Verify mode opens the file read-only, reads and validates the bitmap, checks file size and data offset, initializes CryptoAPI, then sequentially locks/reads each data block. For each offset it chooses expected `param=1` if the bitmap bit is set, otherwise `param=0`, regenerates the block, and compares all 1024 bytes.

## State and Persistence

The persistent state is the generated file: a bitmap header at offset zero, padded to a block boundary, followed by data blocks. Global process state includes `h_prov`, `N`, `M`, `filename`, and mode flags. Crypto provider state is acquired per test and released at exit.

## Dependencies and Integration Points

This standalone test depends on Windows CryptoAPI and filesystem byte-range locking. It is suitable for AFS cache/server validation because it detects stale reads, lost writes, random overwrite failures, file-size errors, and locking/seek problems.

## Risks and Edge Cases

- `parse_cmdline()` uses `atol()`, so sizes larger than `long` or nonnumeric suffixes are not handled robustly despite `offset_t` being 64-bit.
- `show_offsets` is never set from the command line in this file.
- `write_bitmap()` and data writes use synchronous `WriteFile()` with an `OVERLAPPED` only for lock offsets; correctness depends on explicit file-pointer positioning where used.
- Some error paths after a failed read/write can leave locks held because unlock is not always in a guaranteed cleanup block.
- `CryptEncrypt()` is called with a zeroed buffer and `cb_data = BLOCKSIZE`; this deterministic stream depends on provider behavior for RC4 derivation.

## Test Signals

Write mode prints phase progress and exits zero on success. Verify mode prints file size, verification progress, and `Verify succeeded!` on success. Failure signals include corrupt magic, invalid file size/data offset, lock/read/write errors, and exact verification offset for mismatched blocks.
