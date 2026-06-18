<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_regs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_regs.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_regs.h` maps SoC register blocks, offsets, bit fields, and reset/clock identifiers for `mach-bcm63xx`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 952 macros including `BCM63XX_REGS_H_`, `PERF_REV_REG`, `REV_CHIPID_SHIFT`, `REV_CHIPID_MASK`, `REV_REVID_SHIFT`, `REV_REVID_MASK`, `PERF_CKCTL_REG`, `CKCTL_3368_MAC_EN`, `CKCTL_3368_TC_EN`, `CKCTL_3368_US_TOP_EN`, `CKCTL_3368_DS_TOP_EN`, `CKCTL_3368_APM_EN`, `CKCTL_3368_SPI_EN`, `CKCTL_3368_USBS_EN`, `CKCTL_3368_BMU_EN`, `CKCTL_3368_PCM_EN`, `CKCTL_3368_NTP_EN`, `CKCTL_3368_ACP_B_EN`, `CKCTL_3368_ACP_A_EN`, `CKCTL_3368_EMUSB_EN`, `CKCTL_3368_ENET0_EN`, `CKCTL_3368_ENET1_EN`, `CKCTL_3368_USBU_EN`, `CKCTL_3368_EPHY_EN`, and 928 more; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `GPIO_MODE (56)`, `USBH_PRIV (22)`, `MPI_CSBASE (21)`, `CKCTL_6362 (20)`, `USBD_EVENT (19)`, `CKCTL_3368 (18)`, `CKCTL_6368 (18)`, `USBD_CSR (17)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is board setup, clock/reset drivers, pinctrl, IRQ, Ethernet, PCI, USB, serial, SPI, watchdog, and other platform devices.

## Risks
register definitions are executable hardware ABI; a single wrong offset or bit can reset, clock-gate, or misconfigure a peripheral; the file contains 952 macros, so broad edits have high review cost and should be grouped by register block or bit-field family.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_regs.h -->
