<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/loongson_regs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/loongson_regs.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/loongson_regs.h` maps SoC register blocks, offsets, bit fields, and reset/clock identifiers for `mach-loongson64`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 116 macros including `_LOONGSON_REGS_H_`, `LOONGSON_CFG0`, `LOONGSON_CFG0_PRID`, `LOONGSON_CFG1`, `LOONGSON_CFG1_FP`, `LOONGSON_CFG1_FPREV`, `LOONGSON_CFG1_MMI`, `LOONGSON_CFG1_MSA1`, `LOONGSON_CFG1_MSA2`, `LOONGSON_CFG1_CGP`, `LOONGSON_CFG1_WRP`, `LOONGSON_CFG1_LSX1`, `LOONGSON_CFG1_LSX2`, `LOONGSON_CFG1_LASX`, `LOONGSON_CFG1_R6FXP`, `LOONGSON_CFG1_R6CRCP`, `LOONGSON_CFG1_R6FPP`, `LOONGSON_CFG1_CNT64`, `LOONGSON_CFG1_LSLDR0`, `LOONGSON_CFG1_LSPREF`, `LOONGSON_CFG1_LSPREFX`, `LOONGSON_CFG1_LSSYNCI`, `LOONGSON_CFG1_LSUCA`, `LOONGSON_CFG1_LLSYNC`, and 92 more; 0 structs: none; 0 enums: none; 8 callable helpers/prototypes: `cpu_has_cfg`, `read_cpucfg`, `cpu_has_csr`, `csr_readl`, `csr_readq`, `csr_writel`, `csr_writeq`, `drdtime`; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `cpu_has_cfg`, `read_cpucfg`, `cpu_has_csr`, `csr_readl`, `csr_readq`, `csr_writel`, `csr_writeq`, `drdtime`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `linux/types.h`, `linux/bits.h`, `asm/mipsregs.h`, `asm/cpu.h`. Major macro families are `LOONGSON_CFG1 (31)`, `LOONGSON_CFG2 (28)`, `LOONGSON_CFG3 (15)`, `LOONGSON_CSR (12)`, `CSR_MAIL (7)`, `LOONGSON_CSRF (6)`, `CSR_IPI (3)`, `LOONGSON_CFG5 (3)`. Typed contracts include no structs. Callable helpers or declarations include `cpu_has_cfg`, `read_cpucfg`, `cpu_has_csr`, `csr_readl`, `csr_readq`, `csr_writel`, `csr_writeq`, `drdtime`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is board setup, clock/reset drivers, pinctrl, IRQ, Ethernet, PCI, USB, serial, SPI, watchdog, and other platform devices.

## Risks
register definitions are executable hardware ABI; a single wrong offset or bit can reset, clock-gate, or misconfigure a peripheral; the file contains 116 macros, so broad edits have high review cost and should be grouped by register block or bit-field family; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/loongson_regs.h -->
