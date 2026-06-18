<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_timer.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_timer.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_timer.h` provides machine-specific constants and declarations for `mach-bcm63xx`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 1 macros including `BCM63XX_TIMER_H_`; 0 structs: none; 0 enums: none; 6 callable helpers/prototypes: `bcm63xx_timer_register`, `bcm63xx_timer_unregister`, `bcm63xx_timer_set`, `bcm63xx_timer_enable`, `bcm63xx_timer_disable`, `bcm63xx_timer_countdown`; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `bcm63xx_timer_register`, `bcm63xx_timer_unregister`, `bcm63xx_timer_set`, `bcm63xx_timer_enable`, `bcm63xx_timer_disable`, `bcm63xx_timer_countdown`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `BCM63XX_TIMER (1)`. Typed contracts include no structs. Callable helpers or declarations include `bcm63xx_timer_register`, `bcm63xx_timer_unregister`, `bcm63xx_timer_set`, `bcm63xx_timer_enable`, `bcm63xx_timer_disable`, `bcm63xx_timer_countdown`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is MIPS platform setup, generic architecture headers, board files, and device drivers that include this machine directory.

## Risks
the file is small but part of the architecture ABI; stale constants can fail only on the affected board family.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise the specific device path: RTC read/write, floppy DMA/IRQ, timer callbacks, or reset assertion/deassertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_timer.h -->
