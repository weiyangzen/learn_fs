# sources/compression/zstd/programs/fileio.h

## Purpose
`fileio.h` declares the zstd CLI file I/O API and the compression/decompression filename conventions. It exposes preference and context handles, option setters, single-file and multi-file operations, list mode, collision checks, abort handling, and optional backend version queries.

## Important APIs, types, and functions
Constants define stdin/stdout sentinels, null output, and supported compressed suffixes such as `.zst`, `.zstd`, `.gz`, `.xz`, `.lzma`, and `.lz4` plus tar-short variants. `FIO_prefs_t` is an opaque-ish preference structure from `fileio_types.h`, while `FIO_ctx_t` is forward-declared as mutable operation context.

The header exports lifecycle functions, setters for compression type, overwrite, adaptive mode, worker count, checksum, dictionary ID, LDM, sparse write, rsyncable, stream/source size hints, test mode, literal compression mode, progress/display, exclusion of already compressed files, block device allowance, patch-from mode, content-size flag, async I/O, pass-through, and mmap dictionary mode. Operational APIs are `FIO_compressFilename()`, `FIO_decompressFilename()`, `FIO_compressMultipleFilenames()`, `FIO_decompressMultipleFilenames()`, `FIO_listMultipleFiles()`, and `FIO_checkFilenameCollisions()`.

## Control flow
The header supports a two-object setup: create preferences and context, mutate preferences/context with setters according to parsed CLI options, then call a single-file or multi-file operation. Multi-file functions accept optional output mirror directory, output directory, single output file, suffix, dictionary, compression level, and compression parameters.

## State and persistence behavior
The API controls filesystem side effects through preferences: output creation, overwrite, sparse writes, test mode, source removal, stdout/stdin, pass-through, and dictionary mapping. Context tracks multi-file progress and aggregate byte counts internally. The header itself declares no globals but includes setters for global display preferences implemented in `fileio.c`.

## Dependencies and integration points
The header depends on `fileio_types.h`, `util.h` for `FileNamesTable`, and zstd static APIs for compression parameters. It is consumed by zstd CLI command handling and abstracts the lower-level streaming, format, and filesystem behavior implemented in `fileio.c`.

## Risks and edge cases
Callers must respect sentinel names exactly for stdin/stdout, keep file-name arrays valid for the duration of calls, and understand that many errors may terminate through implementation macros rather than cleanly returning. Setter order can matter for warnings and compatibility checks, for example adaptive or rsyncable modes with worker count. Multi-file calls have several mutually exclusive output modes that the caller must populate consistently.

## Test signals
Compile-level tests should include this header from CLI code with zstd static-linking enabled. API tests should exercise preference defaults, setter effects, single versus multi-file routing, suffix constants, and display/version functions across builds with and without optional format libraries.
