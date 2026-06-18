<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/irq.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/irq.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/irq.h` defines IRQ number layout and interrupt-controller constants for `mach-rc32434`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 18 macros including `__ASM_RC32434_IRQ_H`, `NR_IRQS`, `IC_GROUP0_PEND`, `IC_GROUP0_MASK`, `IC_GROUP_OFFSET`, `NUM_INTR_GROUPS`, `GROUP0_IRQ_BASE`, `GROUP1_IRQ_BASE`, `GROUP2_IRQ_BASE`, `GROUP3_IRQ_BASE`, `GROUP4_IRQ_BASE`, `UART0_IRQ`, `ETH0_DMA_RX_IRQ`, `ETH0_DMA_TX_IRQ`, `ETH0_RX_OVR_IRQ`, `ETH0_TX_UND_IRQ`, `GPIO_MAPPED_IRQ_BASE`, `GPIO_MAPPED_IRQ_GROUP`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are `asm/mach-generic/irq.h`, `asm/mach-rc32434/rb.h`. Major macro families are `ETH0_DMA (2)`, `GPIO_MAPPED (2)`, `IC_GROUP0 (2)`, `ETH0_RX (1)`, `ETH0_TX (1)`, `GROUP0_IRQ (1)`, `GROUP1_IRQ (1)`, `GROUP2_IRQ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is arch IRQ initialization, irqchip drivers, cascaded interrupt controllers, board files, and device platform data.

## Risks
overlapping bases or stale `NR_IRQS` values can route device interrupts to the wrong Linux IRQ; IRQ base changes require matching irqchip, device-tree, and board-platform updates.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; verify `/proc/interrupts`, cascaded controller probing, and device IRQ delivery under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/irq.h -->
