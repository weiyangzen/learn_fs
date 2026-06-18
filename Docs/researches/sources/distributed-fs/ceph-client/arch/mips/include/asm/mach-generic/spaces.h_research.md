<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/spaces.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/spaces.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/spaces.h` overrides virtual/physical address-space constants for `mach-generic`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 21 macros including `_ASM_MACH_GENERIC_SPACES_H`, `IO_SPACE_LIMIT`, `CAC_BASE`, `IO_BASE`, `UNCAC_BASE`, `MAP_BASE`, `HIGHMEM_START`, `CKSEG0ADDR_OR_64BIT`, `CKSEG1ADDR_OR_64BIT`, `TO_PHYS`, `TO_CAC`, `TO_UNCAC`, `PAGE_OFFSET`, `FIXADDR_TOP`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are `linux/const.h`, `asm/mipsregs.h`. Major macro families are `CAC_BASE (2)`, `CKSEG0ADDR_OR (2)`, `CKSEG1ADDR_OR (2)`, `HIGHMEM_START (2)`, `IO_BASE (2)`, `MAP_BASE (2)`, `UNCAC_BASE (2)`, `FIXADDR_TOP (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the MIPS memory layout headers, fixmap/ioremap code, PCI I/O windows, and early boot address translation.

## Risks
bad base addresses or limits can make the kernel map RAM, uncached MMIO, or PCI I/O through the wrong segment; address-space changes can affect every driver using `readl`/`writel`, `ioremap`, PCI I/O, or uncached aliases.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise early boot, PCI/SoC MMIO drivers, and uncached register access with `CONFIG_DEBUG_VIRTUAL` or ioremap debug checks when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/spaces.h -->
