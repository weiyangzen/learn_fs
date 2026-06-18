<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/fdt_check_mem_start.c -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/fdt_check_mem_start.c

## Purpose
This decompressor helper validates or corrects the physical memory base computed by `AUTO_ZRELADDR` using the supplied FDT memory nodes and optional crash-kernel usable-memory range.

## Important APIs, Types, and Functions
Functions and exported helpers include `get_cells`, `get_val`, `compatibility`. Local constants include none. Includes are `<linux/kernel.h>`, `<linux/libfdt.h>`, `<linux/sizes.h>`, `"misc.h"`.

## Control Flow
`fdt_check_mem_start()` rejects missing/non-FDT input, reads root address/size cell counts, optionally clips memory ranges by `/chosen/linux,usable-memory-range`, walks memory nodes and `linux,usable-memory` or `reg` properties, returns the original masked PC-derived base if it is valid, or otherwise returns the lowest usable base rounded up to 2 MiB.

## State and Persistence Behavior
State is transient decompressor state in registers, BSS, the temporary malloc area, and possibly the in-memory FDT. It persists only until the decompressed kernel takes control, but it directly determines the kernel image bytes, boot arguments, initrd metadata, memory base, and early diagnostics seen by the real kernel.

## Dependencies and Integration Points
Dependencies include `head.S`, `misc.h`, the compressed linker script, libfdt sources where enabled, configured decompressor backends, generated `piggy_data`, debug UART/ICEDCC hooks, and bootloader-provided ATAG/FDT/register conventions.

## Risks
Risks are malformed cell counts, memory above the 32-bit address space, incorrect clipping for crash kernels, failure to find a memory node, and choosing a base that violates ARM phys/virt patching alignment assumptions.

## Test Signals
Exercise boot with FDT memory starts that are and are not 128 MiB aligned, with multiple memory banks, with `linux,usable-memory-range`, and with invalid DTBs. Confirm the chosen start matches the kernel log and does not overlap reserved crash regions.

Source read size: 168 lines, 4426 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/fdt_check_mem_start.c -->
