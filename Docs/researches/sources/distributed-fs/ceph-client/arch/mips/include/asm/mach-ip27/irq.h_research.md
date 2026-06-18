<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/irq.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/irq.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/irq.h` defines IRQ number layout and interrupt-controller constants for `mach-ip27`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 7 macros including `__ASM_MACH_IP27_IRQ_H`, `NR_IRQS`, `IP27_HUB_PEND0_IRQ`, `IP27_HUB_PEND1_IRQ`, `IP27_RT_TIMER_IRQ`, `IP27_HUB_IRQ_BASE`, `IP27_HUB_IRQ_COUNT`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are `asm/mach-generic/irq.h`. Major macro families are `IP27_HUB (4)`, `IP27_RT (1)`, `NR_IRQS (1)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is arch IRQ initialization, irqchip drivers, cascaded interrupt controllers, board files, and device platform data.

## Risks
overlapping bases or stale `NR_IRQS` values can route device interrupts to the wrong Linux IRQ; IRQ base changes require matching irqchip, device-tree, and board-platform updates; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; verify `/proc/interrupts`, cascaded controller probing, and device IRQ delivery under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/irq.h -->
