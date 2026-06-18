# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomain.h

## Purpose
`powerdomain.h` defines the OMAP powerdomain data model, power-state constants, feature flags, limits, SoC operation callback interface, and public framework API.

## Important APIs, Types, and Functions
Important constants are `PWRDM_POWER_OFF`, `PWRDM_POWER_RET`, `PWRDM_POWER_INACTIVE`, `PWRDM_POWER_ON`, state bitfields such as `PWRSTS_OFF_RET_ON`, flags such as `PWRDM_HAS_HDWR_SAR`, `PWRDM_HAS_MPU_QUIRK`, and `PWRDM_HAS_LOWPOWERSTATECHANGE`, plus `PWRDM_MAX_MEM_BANKS` and `PWRDM_MAX_CLKDMS`. Key types are `struct powerdomain` and `struct pwrdm_ops`.

## Control Flow
No code executes in the header. It defines contracts used by data files, PRM/CM operation backends, PM code, debugfs code, clockdomain association, and voltage-domain registration.

## State and Persistence Behavior
`struct powerdomain` contains both descriptor data and mutable runtime state: voltage-domain pointer, clockdomain list, list nodes, current state, counters, locks, debug timers, and context shadow. `struct pwrdm_ops` abstracts hardware register access.

## Dependencies and Integration Points
It includes list and spinlock types and is included by almost every OMAP PM/powerdomain file. It integrates with clockdomain and voltage-domain structures by forward declaration.

## Risks
Changing structure layout affects static initializers and debug/context code. Raising/lowering limits for banks or clockdomains impacts data tables. Callback contract changes require updating every SoC backend.

## Test Signals
Build all mach-omap2 PM configs. Runtime signals include successful powerdomain registration, correct debugfs counter/timer behavior, valid memory-bank programming, and no lockdep or transition warnings.
