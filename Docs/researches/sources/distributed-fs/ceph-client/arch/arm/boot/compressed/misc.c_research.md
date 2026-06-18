<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/misc.c -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/misc.c

## Purpose
This file provides the small C runtime for the ARM zImage decompressor: console output, fatal error handling, global allocation bounds, machine type capture, optional EP93xx setup, and the call into `do_decompress()`.

## Important APIs, Types, and Functions
Functions and exported helpers include `icedcc_putc`, `putstr`, `error`, `__div0`, `decompress_kernel`, `__fortify_panic`. Local constants include `putc`, `arch_error`. Includes are `<linux/compiler.h>`, `<linux/types.h>`, `<linux/linkage.h>`, `"misc.h"`, `"misc-ep93xx.h"`.

## Control Flow
`decompress_kernel()` receives output address, malloc range, and architecture id from `head.S`; initializes `output_data`, `free_mem_ptr`, `free_mem_end_ptr`, and `__machine_arch_type`; runs platform decompressor setup; prints progress; calls `do_decompress()`; and either halts through `error()` or announces handoff to the kernel. Debug ICEDCC variants provide `putc()` when configured.

## State and Persistence Behavior
State is transient decompressor state in registers, BSS, the temporary malloc area, and possibly the in-memory FDT. It persists only until the decompressed kernel takes control, but it directly determines the kernel image bytes, boot arguments, initrd metadata, memory base, and early diagnostics seen by the real kernel.

## Dependencies and Integration Points
Dependencies include `head.S`, `misc.h`, the compressed linker script, libfdt sources where enabled, configured decompressor backends, generated `piggy_data`, debug UART/ICEDCC hooks, and bootloader-provided ATAG/FDT/register conventions.

## Risks
Risks are printing through an uninitialized debug transport, malloc bounds too small for the decompressor, platform setup touching wrong early registers, division-by-zero or fortify panic paths looping before diagnostics are visible, and non-const initialized data breaking XIP assumptions.

## Test Signals
Boot with and without `DEBUG_UNCOMPRESS`, with EP93xx setup enabled, and with each compressor. Confirm the progress banner, successful handoff, and that bad compressed input reaches the halt path.

Source read size: 160 lines, 3066 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/misc.c -->
