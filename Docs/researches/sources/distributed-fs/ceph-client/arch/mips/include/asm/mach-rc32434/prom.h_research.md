<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/prom.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/prom.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/prom.h` declares board, firmware, memory, and platform-data contracts for `mach-rc32434`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 9 macros including `PROM_ENTRY`, `SR_NMI`, `SERIAL_SPEED_ENTRY`, `FREQ_TAG`, `KMAC_TAG`, `MEM_TAG`, `BOARD_TAG`, `BOARD_RB532`, `BOARD_RB532A`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `BOARD_RB532 (1)`, `BOARD_RB532A (1)`, `BOARD_TAG (1)`, `FREQ_TAG (1)`, `KMAC_TAG (1)`, `MEM_TAG (1)`, `PROM_ENTRY (1)`, `SERIAL_SPEED (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is machine setup code, boot parameter parsing, platform device registration, board identification, and firmware handoff.

## Risks
layout drift between firmware, board files, and consumers can cause wrong memory maps, device registration, or machine identity.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/prom.h -->
