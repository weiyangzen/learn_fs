<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/zstd_common_module.c -->
# sources/compression/zstd/contrib/linux-kernel/zstd_common_module.c

## Purpose
This file turns common zstd entropy/error helpers into a Linux kernel module export surface.

## Important APIs, Types, And Functions
It exports `FSE_readNCount`, `HUF_readStats`, `HUF_readStats_wksp`, `ZSTD_isError`, `ZSTD_getErrorName`, and `ZSTD_getErrorCode` with `EXPORT_SYMBOL_GPL`, then declares dual BSD/GPL licensing and the module description.

## Control Flow
There is no runtime control flow beyond module loading. The included zstd common implementation provides the actual logic; this wrapper only exposes selected symbols.

## State And Persistence
No module-owned mutable state or persistence exists. State belongs to callers and the imported zstd routines.

## Dependencies And Integration Points
It depends on the kernel-contrib common source aggregation headers and Linux module macros. Compress and decompress modules rely on these common helpers when built as split kernel modules.

## Risks
Export-set drift is the main risk: missing or wrongly licensed exports break module linkage for compressor/decompressor users.

## Test Signals
The linux-kernel tests and macro compile checks confirm that common symbols are visible and linkable.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/zstd_common_module.c -->
