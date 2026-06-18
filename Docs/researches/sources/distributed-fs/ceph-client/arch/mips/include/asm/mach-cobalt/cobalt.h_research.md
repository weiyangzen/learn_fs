<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cobalt/cobalt.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cobalt/cobalt.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cobalt/cobalt.h` declares board, firmware, memory, and platform-data contracts for `mach-cobalt`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 5 macros including `__ASM_COBALT_H`, `COBALT_BRD_ID_QUBE1`, `COBALT_BRD_ID_RAQ1`, `COBALT_BRD_ID_QUBE2`, `COBALT_BRD_ID_RAQ2`; 0 structs: none; 0 enums: none; 2 callable helpers/prototypes: `cobalt_machine_halt`, `cobalt_machine_restart`; 1 extern variables: `cobalt_board_id`. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `cobalt_machine_halt`, `cobalt_machine_restart`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `COBALT_BRD (4)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include `cobalt_machine_halt`, `cobalt_machine_restart`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is machine setup code, boot parameter parsing, platform device registration, board identification, and firmware handoff.

## Risks
layout drift between firmware, board files, and consumers can cause wrong memory maps, device registration, or machine identity.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cobalt/cobalt.h -->
