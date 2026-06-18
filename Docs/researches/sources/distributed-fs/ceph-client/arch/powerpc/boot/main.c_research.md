# sources/distributed-fs/ceph-client/arch/powerpc/boot/main.c

Purpose: is the common zImage boot-wrapper orchestrator that prepares the kernel, initrd, ESM blob, command line, device tree, and final kernel jump.

Important APIs/types/functions: types `addr_range`, `elf_info`, `platform_ops`, `dt_ops`, `console_ops`, `loader_info`, `addr_range`; functions `prep_kernel`, `prep_initrd`, `prep_esm_blob`, `prep_esm_blob`, `prep_cmdline`, `start`; assembly labels/symbols `out`. Source size is 284 lines / 8616 bytes.

Implementation notes: prep_kernel samples or copies the ELF header, validates ELF32/ELF64, allocates or validates the target range, decompresses the payload, and flushes the cache. prep_initrd and prep_esm_blob relocate low payloads and write /chosen properties. start wires platform fixups, /chosen creation, command-line editing, FDT finalization, console close, and the final kernel ABI call.

Control flow is start() -> platform fixups -> /chosen preparation -> kernel decompression/copy -> initrd/ESM relocation -> command-line update -> device-tree finalization -> console close -> kernel entry.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `stdarg.h`, `stddef.h`, `elf.h`, `page.h`, `string.h`, `stdio.h`, `ops.h`, `reg.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include decompression length mismatches, low-memory overlap between wrapper/kernel/FDT/initrd, 32-bit truncation of initrd/ESM properties, cache flush omissions, and wrong kernel entry ABI. Test signals are compressed/uncompressed zImage boots, initrd and no-initrd boots, command-line editing, FDT validation, and negative decompressor/ELF tests.
