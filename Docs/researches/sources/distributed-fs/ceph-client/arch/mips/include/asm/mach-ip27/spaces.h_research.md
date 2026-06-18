<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/spaces.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/spaces.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/spaces.h` overrides virtual/physical address-space constants for `mach-ip27`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 9 macros including `_ASM_MACH_IP27_SPACES_H`, `HSPEC_BASE`, `IO_BASE`, `MSPEC_BASE`, `UNCAC_BASE`, `CAC_BASE`, `TO_MSPEC`, `TO_HSPEC`, `HIGHMEM_START`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are `linux/const.h`, `asm/mach-generic/spaces.h`. Major macro families are `CAC_BASE (1)`, `HIGHMEM_START (1)`, `HSPEC_BASE (1)`, `IO_BASE (1)`, `MSPEC_BASE (1)`, `TO_HSPEC (1)`, `TO_MSPEC (1)`, `UNCAC_BASE (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the MIPS memory layout headers, fixmap/ioremap code, PCI I/O windows, and early boot address translation.

## Risks
bad base addresses or limits can make the kernel map RAM, uncached MMIO, or PCI I/O through the wrong segment; address-space changes can affect every driver using `readl`/`writel`, `ioremap`, PCI I/O, or uncached aliases; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise early boot, PCI/SoC MMIO drivers, and uncached register access with `CONFIG_DEBUG_VIRTUAL` or ioremap debug checks when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/spaces.h -->
