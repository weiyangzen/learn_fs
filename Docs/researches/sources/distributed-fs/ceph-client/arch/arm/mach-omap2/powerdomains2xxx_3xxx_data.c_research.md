# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains2xxx_3xxx_data.c

## Purpose
`powerdomains2xxx_3xxx_data.c` defines powerdomain descriptors shared by OMAP2 and OMAP3: the graphics powerdomain and wakeup powerdomain. It captures common PRCM offsets, allowed states, memory-bank behavior, and voltage-domain names.

## Important APIs, Types, and Functions
The exported descriptors are `gfx_omap2_pwrdm` and `wkup_omap2_pwrdm`. `gfx_omap2_pwrdm` supports OFF/RET/ON with one memory bank retained in RET and ON in ON. `wkup_omap2_pwrdm` is always ON.

## Control Flow
There is no local function flow. OMAP2 and OMAP3 SoC-specific init arrays include these descriptors when appropriate; the generic framework registers them and initializes their state.

## State and Persistence Behavior
The descriptors are static but become mutable after registration because `struct powerdomain` includes list nodes, counters, locks, and voltage-domain pointer replacement.

## Dependencies and Integration Points
It depends on `powerdomain.h`, `prcm-common.h`, and `prm.h`. It is declared by `powerdomains2xxx_3xxx_data.h` and consumed by `powerdomains2xxx_data.c` and `powerdomains3xxx_data.c`.

## Risks
The file notes GFX is not present on 3430ES2, so SoC-specific arrays must include it carefully. Shared descriptor mutation means the same object should not be registered twice in one boot path.

## Test Signals
Boot OMAP2/3 variants and verify expected presence/absence of `gfx_pwrdm` and always-on `wkup_pwrdm`. Use PM debugfs to confirm counters and valid state transitions.
