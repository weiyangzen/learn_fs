<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/am33xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/am33xx.h

## Purpose
Collects AM33xx and AM43xx base physical addresses for slow L4, control module, PRCM, and TAP blocks.

## Important APIs, Types, and Functions
Defines `L4_SLOW_AM33XX_BASE`, `AM33XX_SCM_BASE`, `AM33XX_CTRL_BASE`, `AM33XX_PRCM_BASE`, `AM43XX_PRCM_BASE`, and `AM33XX_TAP_BASE`.

## Control Flow
No runtime flow. Address constants are consumed by map/control/PRCM/TAP setup code.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Integrates with AM33xx/AM43xx IO mapping and register access helpers.

## Risks
Incorrect base addresses break early control-module and PRCM access and can prevent boot or reset.

## Test Signals
Build AM33xx/AM43xx configs and verify early init can map/read control and PRCM registers without data aborts.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/am33xx.h -->
