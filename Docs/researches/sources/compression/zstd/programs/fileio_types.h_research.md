# sources/compression/zstd/programs/fileio_types.h

## Purpose

This header defines shared preference and dictionary data structures used by zstd CLI file I/O, compression, decompression, and dictionary handling code.

## Important APIs, Types, and Functions

`FIO_progressSetting_e` controls automatic, never, or always progress display. `FIO_display_prefs_t` stores display level and progress policy. `FIO_compressionType_t` selects zstd, gzip, xz, lzma, or lz4 output. `FIO_prefs_t` is the central mutable preferences object, covering algorithm parameters, sparse/dict/checksum options, adaptive and LDM settings, stream-size hints, source removal and overwrite behavior, async I/O, memory/thread limits, block-device/pass-through behavior, patch mode, and mmap dictionary policy. `FIO_Dict_t` owns loaded or mapped dictionary data plus a Windows handle when needed.

## Control Flow, State, and Persistence

The file has no logic; it is a contract for state populated by `zstdcli.c` and consumed by `fileio` routines. Preferences are process-local and persist only for the CLI invocation.

## Dependencies and Integration Points

It enables `ZSTD_STATIC_LINKING_ONLY` before including `zstd.h`, so internal/advanced zstd parameter types are visible. It integrates with `fileio.h`, `fileio_asyncio.h`, and CLI parsing.

## Risks and Test Signals

`FIO_prefs_t` contains many interdependent fields where defaults matter. Tests should cover option translation from CLI flags, compression format selection, mmap versus malloc dictionaries, async toggles, and pass-through/block-device policy.
