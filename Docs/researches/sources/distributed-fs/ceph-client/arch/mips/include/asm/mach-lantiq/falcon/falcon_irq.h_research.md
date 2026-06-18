<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/falcon/falcon_irq.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/falcon/falcon_irq.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/falcon/falcon_irq.h` defines IRQ number layout and interrupt-controller constants for `mach-lantiq/falcon`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 10 macros including `_FALCON_IRQ__`, `INT_NUM_IRQ0`, `INT_NUM_IM0_IRL0`, `INT_NUM_IM1_IRL0`, `INT_NUM_IM2_IRL0`, `INT_NUM_IM3_IRL0`, `INT_NUM_IM4_IRL0`, `INT_NUM_EXTRA_START`, `INT_NUM_IM_OFFSET`, `MAX_IM`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `INT_NUM (8)`, `MAX_IM (1)`, `_FALCON (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is arch IRQ initialization, irqchip drivers, cascaded interrupt controllers, board files, and device platform data.

## Risks
overlapping bases or stale `NR_IRQS` values can route device interrupts to the wrong Linux IRQ; IRQ base changes require matching irqchip, device-tree, and board-platform updates.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; verify `/proc/interrupts`, cascaded controller probing, and device IRQ delivery under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/falcon/falcon_irq.h -->
