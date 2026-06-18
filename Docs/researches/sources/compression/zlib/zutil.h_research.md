# sources/compression/zlib/zutil.h

Purpose: private zlib implementation header that centralizes target configuration, internal types/macros, allocation wrappers, diagnostics, byte swapping, and optional one-time initialization support. Applications should use `zlib.h`, not this file.

Important APIs/types: it defines `ZLIB_INTERNAL`, `local`, byte/word aliases (`uch`, `ush`, `ulg`), optional 64-bit type `Z_U8`, `z_errmsg`, `ERR_MSG`, `ERR_RETURN`, defaults for window/memory level, block-kind constants, match length constants, `OS_CODE`, and `F_OPEN`. It maps `zmemcpy`/`zmemcmp`/`zmemzero` either to libc/far-memory variants or declares local fallbacks. `ZALLOC`, `ZFREE`, and `TRY_FREE` wrap stream allocators. `ZSWAP32` performs 32-bit byte swapping.

Control flow and state: the file is preprocessor-driven. It selects platform headers and gzip OS identifiers for DOS, VMS, z/OS, Atari, OS/2, Mac, RISC OS, Windows, BeOS, IBM i, Apple, and default Unix. Under `ZLIB_DEBUG`, trace/assert macros call `z_error`; otherwise they compile away. Under `Z_ONCE`, it defines `z_once_t` and a local `z_once()` using C11 atomics when available, falling back to a warning-producing non-thread-safe volatile implementation.

Dependencies, integration, risks, and test signals: every core zlib C file includes this header, so macro changes affect ABI internals and cross-platform builds. Risks include legacy compiler branches, macro collisions, non-atomic `Z_ONCE` fallback, and assumptions about endian/size constants. Test signals come from broad zlib compile matrices, debug builds, `Z_SOLO`, no-memcpy builds, and threaded users of one-time CRC/table initialization.
