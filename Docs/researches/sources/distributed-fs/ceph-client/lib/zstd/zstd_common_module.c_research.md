# sources/distributed-fs/ceph-client/lib/zstd/zstd_common_module.c

## Purpose
`zstd_common_module.c` exports common Zstd helper symbols shared by the kernel compression and decompression modules. It packages error handling and entropy-table parsing functions into a common GPL-visible module surface.

## Important APIs, types, and functions
The file exports `FSE_readNCount`, `HUF_readStats`, `HUF_readStats_wksp`, `ZSTD_isError`, `ZSTD_getErrorName`, and `ZSTD_getErrorCode`. It undefines `ZSTD_isError` first because `zstd_internal.h` may define it as a macro.

## Control flow
There is no custom runtime path beyond module loading. The export declarations make common routines available to separately linked Zstd compression and decompression modules.

## State and persistence
The file maintains no runtime state. Module metadata declares dual BSD/GPL licensing and the description `Zstd Common`.

## Dependencies and integration points
It includes Linux module support plus Zstd common `huf.h`, `fse.h`, and `zstd_internal.h`. It is a dependency boundary for `zstd_compress_module.c` and `zstd_decompress_module.c`.

## Risks and test signals
Risks are missing exports after upstream symbol changes, macro/function name mismatches, and license/export incompatibilities for consumers. Test signals include module link/load tests, `modpost` export validation, and compression/decompression module builds as separate objects.
