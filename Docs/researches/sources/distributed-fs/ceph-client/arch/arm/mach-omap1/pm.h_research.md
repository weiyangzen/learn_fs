<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/pm.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/pm.h

## Purpose
Defines OMAP1 PM register addresses, bit masks, sleep constants, save-state enumerations, save/restore macros, and suspend/idle declarations shared by C and assembly PM code.

## Important APIs, Types, and Functions
Important APIs are `ARM_SAVE/RESTORE/SHOW`, `DSP_SAVE/RESTORE/SHOW`, `ULPD_SAVE/RESTORE/SHOW`, `MPUI1510_*`, `MPUI1610_*`, declarations for `omap1_pm_idle()`, `omap1_pm_suspend()`, `omap1510_cpu_suspend()`, and `omap1610_cpu_suspend()`.

## Control Flow
Compile-time constants guide both `pm.c` and `sleep.S`. Save/restore macros index the static arrays in `pm.c`; assembly offset constants let SRAM code write IDLECT and memory-controller registers.

## State and Persistence Behavior
No own state, but enumerations define the layout of PM save arrays. The assembly-visible constants must stay in sync with the C suspend code.

## Dependencies and Integration Points
Depends on OMAP1 IO address translation, clock/PM register definitions, and optional `CONFIG_OMAP_SERIAL_WAKE` stubs.

## Risks
Changing enum order or constants without updating consumers corrupts suspend save/restore. Assembly constants use physical-to-virtual encoded addresses and are boot-critical.

## Test Signals
Build with OMAP15xx and OMAP16xx PM enabled, assemble `sleep.S`, and run suspend/resume. Debugfs output from `pm.c` should match the enum-backed save slots.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/pm.h -->
