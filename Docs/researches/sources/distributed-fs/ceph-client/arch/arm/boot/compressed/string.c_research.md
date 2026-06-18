<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/string.c -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/string.c

## Purpose
This file implements minimal freestanding string and memory routines for the compressed ARM boot environment, avoiding fortified libc/kernel string dependencies before the full kernel is running.

## Important APIs, Types, and Functions
Functions and exported helpers include `strlen`, `strnlen`, `memcmp`, `strcmp`. Local constants include `__NO_FORTIFY`. Includes are `<linux/string.h>`.

## Control Flow
`memcpy`, `memmove`, `memcmp`, `strcmp`, `memchr`, `strchr`, `strrchr`, and `memset` operate directly on byte pointers. `memmove` chooses forward or backward copying for overlap. Alias symbols provide `__memcpy`, `__memmove`, and `__memset` names expected by compiler-generated calls.

## State and Persistence Behavior
State is transient decompressor state in registers, BSS, the temporary malloc area, and possibly the in-memory FDT. It persists only until the decompressed kernel takes control, but it directly determines the kernel image bytes, boot arguments, initrd metadata, memory base, and early diagnostics seen by the real kernel.

## Dependencies and Integration Points
Dependencies include `head.S`, `misc.h`, the compressed linker script, libfdt sources where enabled, configured decompressor backends, generated `piggy_data`, debug UART/ICEDCC hooks, and bootloader-provided ATAG/FDT/register conventions.

## Risks
Risks are overlap mistakes in `memmove`, compiler replacement with unavailable builtins, performance regressions in the decompressor, and missing helper variants required by a newly included decompressor backend.

## Test Signals
Build compressed images with each compiler and compressor, then run unit-style checks in a host harness if extracted. Boot tests should include XZ, because that path explicitly protects `memmove`/`memcpy` macro behavior.

Source read size: 162 lines, 2971 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/string.c -->
