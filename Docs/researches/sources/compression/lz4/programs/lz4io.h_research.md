# sources/compression/lz4/programs/lz4io.h

Purpose: public LZ4 program I/O interface for configuring and running file compression, decompression, and listing.

Important APIs/types: special names `stdinmark`, `stdoutmark`, `NULL_OUTPUT`, `nulmark`; opaque `LZ4IO_prefs_t`; preference creation/freeing and setters; single/multiple filename compression/decompression; `LZ4IO_displayCompressedFilesInfo()`.

Control flow/state contract: callers create prefs, mutate settings, run operations, then free prefs. Operations may read/write files or stdio and return success/error counts.

Dependencies/integration: implemented by `lz4io.c`, consumed by `lz4cli.c`; includes only `<stddef.h>`.

Risks: implementation can terminate on fatal errors; source removal and overwrite behavior are controlled through prefs; NULL-safety is not broadly guaranteed.

Test signals: all CLI tests indirectly exercise this API; list tests cover the listing entry point.
