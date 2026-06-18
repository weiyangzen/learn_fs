<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-db1x00/bcsr.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-db1x00/bcsr.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-db1x00/bcsr.h` provides machine-specific constants and declarations for `mach-db1x00`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 139 macros including `_DB1XXX_BCSR_H_`, `DB1000_BCSR_PHYS_ADDR`, `DB1000_BCSR_HEXLED_OFS`, `DB1550_BCSR_PHYS_ADDR`, `DB1550_BCSR_HEXLED_OFS`, `PB1550_BCSR_PHYS_ADDR`, `PB1550_BCSR_HEXLED_OFS`, `DB1200_BCSR_PHYS_ADDR`, `DB1200_BCSR_HEXLED_OFS`, `PB1200_BCSR_PHYS_ADDR`, `PB1200_BCSR_HEXLED_OFS`, `DB1300_BCSR_PHYS_ADDR`, `DB1300_BCSR_HEXLED_OFS`, `BCSR_REG_WHOAMI`, `BCSR_REG_STATUS`, `BCSR_REG_SWITCHES`, `BCSR_REG_RESETS`, `BCSR_REG_PCMCIA`, `BCSR_REG_BOARD`, `BCSR_REG_LEDS`, `BCSR_REG_SYSTEM`, `BCSR_REG_INTCLR`, `BCSR_REG_INTSET`, `BCSR_REG_MASKCLR`, and 113 more; 0 structs: none; 2 enums: `bcsr_id`, `bcsr_whoami_boards`; 5 callable helpers/prototypes: `bcsr_init`, `bcsr_read`, `bcsr_write`, `bcsr_mod`, `bcsr_init_irq`; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `bcsr_init`, `bcsr_read`, `bcsr_write`, `bcsr_mod`, `bcsr_init_irq`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `BCSR_RESETS (29)`, `BCSR_STATUS (27)`, `BCSR_BOARD (21)`, `BCSR_REG (16)`, `BCSR_SWITCHES (10)`, `BCSR_PCMCIA (8)`, `BCSR_SYSTEM (7)`, `BCSR_LEDS (5)`. Typed contracts include no structs. Callable helpers or declarations include `bcsr_init`, `bcsr_read`, `bcsr_write`, `bcsr_mod`, `bcsr_init_irq`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is MIPS platform setup, generic architecture headers, board files, and device drivers that include this machine directory.

## Risks
the file is small but part of the architecture ABI; stale constants can fail only on the affected board family; the file contains 139 macros, so broad edits have high review cost and should be grouped by register block or bit-field family.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-db1x00/bcsr.h -->
