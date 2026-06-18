<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/decompress.c -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/decompress.c

## Purpose
This file selects and wraps the configured kernel decompressor implementation for the ARM zImage decompressor.

## Important APIs, Types, and Functions
Functions and exported helpers include `do_decompress`. Local constants include `_LINUX_STRING_H_`, `STATIC`, `STATIC_RW_DATA`, `Assert`, `Trace`, `Tracev`, `Tracevv`, `Tracec`, `Tracecv`, `memmove`, `memcpy`. Includes are `<linux/compiler.h>`, `<linux/types.h>`, `<linux/stddef.h>`, `<linux/linkage.h>`, `<asm/string.h>`, `"misc.h"`, `"../../../../lib/decompress_inflate.c"`, `"../../../../lib/decompress_unlzo.c"`, `"../../../../lib/decompress_unlzma.c"`, `"../../../../lib/decompress_unxz.c"`, `"../../../../lib/decompress_unlz4.c"`.

## Control Flow
The preprocessor includes exactly the decompressor backend selected by `CONFIG_KERNEL_GZIP`, `LZO`, `LZMA`, `XZ`, or `LZ4`, defines standalone diagnostic/string hooks needed by those sources, and `do_decompress()` calls the common `__decompress()` entry on `input_data` and the output buffer supplied by `misc.c`.

## State and Persistence Behavior
State is transient decompressor state in registers, BSS, the temporary malloc area, and possibly the in-memory FDT. It persists only until the decompressed kernel takes control, but it directly determines the kernel image bytes, boot arguments, initrd metadata, memory base, and early diagnostics seen by the real kernel.

## Dependencies and Integration Points
Dependencies include `head.S`, `misc.h`, the compressed linker script, libfdt sources where enabled, configured decompressor backends, generated `piggy_data`, debug UART/ICEDCC hooks, and bootloader-provided ATAG/FDT/register conventions.

## Risks
Risks are missing string helpers in the freestanding decompressor environment, KASAN/fortify macro conflicts, multiple or no compressor configurations, and backend memory requirements exceeding the 64 KiB malloc window.

## Test Signals
Build and boot zImages for each supported compressor. Corrupt `piggy_data` for a negative test and confirm `error()` halts cleanly. Use `V=1` to verify only the intended decompressor backend is included.

Source read size: 66 lines, 1817 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/decompress.c -->
