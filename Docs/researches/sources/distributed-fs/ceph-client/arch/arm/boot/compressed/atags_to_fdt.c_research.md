<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/atags_to_fdt.c -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/atags_to_fdt.c

## Purpose
This decompressor helper converts legacy ARM ATAG boot parameters into properties inside an appended or supplied flattened device tree before the real kernel starts. It handles bootargs, memory banks, initrd location, and serial number propagation.

## Important APIs, Types, and Functions
Functions and exported helpers include `node_offset`, `setprop`, `setprop_string`, `setprop_cell`, `get_cell_size`, `merge_fdt_bootargs`, `hex_str`, `atags_to_fdt`, `for_each_tag`. Local constants include `do_extend_cmdline`, `NR_BANKS`. Includes are `<linux/libfdt_env.h>`, `<asm/setup.h>`, `<libfdt.h>`, `"misc.h"`.

## Control Flow
`atags_to_fdt()` validates alignment and ATAG_CORE, expands the FDT with `fdt_open_into`, walks each tag, updates `/chosen` bootargs, records `linux,initrd-start/end`, serializes up to 16 memory banks using the DT root `#size-cells`, and repacks the FDT. If the input already points to a DTB it returns success without conversion; bad ATAG locations return `1` so the assembly caller can retry the conventional RAM+0x100 address.

## State and Persistence Behavior
State is transient decompressor state in registers, BSS, the temporary malloc area, and possibly the in-memory FDT. It persists only until the decompressed kernel takes control, but it directly determines the kernel image bytes, boot arguments, initrd metadata, memory base, and early diagnostics seen by the real kernel.

## Dependencies and Integration Points
Dependencies include `head.S`, `misc.h`, the compressed linker script, libfdt sources where enabled, configured decompressor backends, generated `piggy_data`, debug UART/ICEDCC hooks, and bootloader-provided ATAG/FDT/register conventions.

## Risks
Risks are insufficient temporary FDT space, command line truncation, incorrect cell-size handling for 64-bit memory sizes, silently skipping more than 16 memory banks, and conflicting DT/ATAG bootargs where append versus replace policy changes command-line precedence.

## Test Signals
Boot with `CONFIG_ARM_ATAG_DTB_COMPAT` using ATAG-only, DTB-only, and mixed ATAG+appended-DTB flows. Validate `/chosen/bootargs`, initrd properties, `serial-number`, and `/memory/reg` in the resulting FDT and include command-line extension versus replacement configurations.

Source read size: 218 lines, 5572 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/atags_to_fdt.c -->
