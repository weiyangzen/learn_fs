<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ti-emif-sram.h -->
# sources/distributed-fs/ceph-client/include/linux/ti-emif-sram.h

## Purpose
defines TI AM33xx EMIF register save/restore layouts and SRAM-resident power-management function table interfaces.

## Important APIs, Types, and Functions
The file is 140 lines and exports these visible symbol families: types/enums `emif_regs_amx3`, `ti_emif_pm_data`, `ti_emif_pm_functions`, `gen_pool`; macros/constants none; function-like macros none; inline helpers `ti_emif_asm_offsets`; external prototypes `offsetof`, `BLANK`, `DEFINE`, `ti_emif_copy_pm_function_table`, `ti_emif_get_mem_type`.

## Control Flow
Platform PM code copies low-level EMIF routines into SRAM with `ti_emif_copy_pm_function_table()`, uses generated offsets for assembly, saves EMIF register context, enters/exits self-refresh, and restores DDR configuration around low-power states.

## State and Persistence Behavior
`emif_regs_amx3` stores captured controller/PHY register values; `ti_emif_pm_data` stores virtual/physical controller and context addresses; `ti_emif_pm_functions` stores SRAM function offsets. These records persist across suspend transitions.

## Dependencies and Integration Points
It depends on kbuild offset generation, packed/aligned layout, gen_pool SRAM allocation, IO memory, and TI SoC EMIF hardware. Direct includes are `linux/kbuild.h`, `linux/types.h`.

## Risks and Edge Cases
Assembly offsets, packing, and alignment must remain exact. Wrong physical addresses or SRAM function offsets can corrupt DDR during suspend/resume and hang the system.

## Test Signals
Run offset-generation builds, compare struct offsets with assembly users, suspend/resume AM33xx hardware repeatedly, and validate memory type detection for supported DDR variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ti-emif-sram.h -->
