# sources/compression/lz4/tests/freestanding.c

## Purpose
`freestanding.c` is a minimal freestanding-environment smoke test for compiling and running LZ4 and LZ4HC without the normal C runtime support expected by hosted programs.

## Important APIs, Types, and Functions
On x86_64 Linux it defines `LZ4_FREESTANDING`, maps LZ4 memory hooks to local `memmove`, `memcpy`, and `memset`, includes `../lib/lz4.c` and `../lib/lz4hc.c` directly, and tests `LZ4_compress_default()`, `LZ4_compress_HC()`, and `LZ4_decompress_safe()`. It also provides `_start()`, `main()`, `MY_exit()`, `MY_abort()`, `__assert_fail()`, and implementations of required memory functions.

## Control Flow, State, and Persistence
Non-x86_64 or non-Linux builds return success without exercising freestanding code. The Linux path compresses and decompresses a static 256-byte README excerpt with both normal and HC compressors, compares bytes, and exits via a raw `SYS_exit` syscall. All buffers are static; there is no heap or persistent state.

## Dependencies and Integration Points
It depends only on `<stddef.h>`, `<stdint.h>`, inline assembly syscall support, and direct inclusion of LZ4 library sources. This test protects the `LZ4_FREESTANDING` configuration used by embedded or kernel-like integrations.

## Risks and Test Signals
Risks include architecture specificity, direct inclusion hiding separate-object link issues, and a small test corpus. Strong signals are absence of libc calls under `-ffreestanding -nostdlib`, byte-exact round trips, and exit code equal to source line on failure.
