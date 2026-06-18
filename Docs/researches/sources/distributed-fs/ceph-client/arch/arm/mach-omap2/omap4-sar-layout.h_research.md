<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap4-sar-layout.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap4-sar-layout.h

## Purpose
`omap4-sar-layout.h` defines the Save-And-Restore RAM layout used by OMAP4/OMAP5 low-power code, WakeupGen context save, L2/SCU context, CPU wakeup physical addresses, and secure RAM metadata.

## Important APIs, Types, and Functions
Important constants include SAR bank offsets, `SCU_OFFSET*`, `OMAP_TYPE_OFFSET`, `L2X0_*` offsets, CPU wakeup NS PA offsets for OMAP4 and OMAP5, secure RAM metadata offsets, WakeupGen save offsets for OMAP4 and OMAP5, AuxCoreBoot offsets, PTM sync offsets, and `SAR_BACKUP_STATUS_WAKEUPGEN`.

## Control Flow
There is no runtime control flow. Low-power C and assembly code write/read SAR addresses based on these offsets before and after MPUSS context loss.

## State and Persistence Behavior
The header defines persistent-in-low-power SAR locations. SAR RAM contents survive the relevant retention/off transitions and are consumed by ROM or restore code.

## Dependencies and Integration Points
It integrates with `omap-mpuss-lowpower.c`, `omap-wakeupgen.c`, `omap4-common.c`, and secure/ROM restore paths.

## Risks
Offset mistakes directly corrupt low-power restore data and can hang resume. OMAP4 and OMAP5 layouts differ, so sharing constants incorrectly is high risk.

## Test Signals
Suspend/resume and cpuidle OSWR/CSWR tests on OMAP4 and OMAP5 should restore CPU, GIC, WakeupGen, SCU, and L2 state. Debug SAR dumps can verify values at documented offsets before idle entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap4-sar-layout.h -->
