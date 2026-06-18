# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains54xx_data.c

## Purpose
`powerdomains54xx_data.c` defines OMAP54xx powerdomain descriptors for the OMAP4-style framework. It covers CORE, ABE, COREAON, DSS, CPU0/CPU1, EMU, MPU, CUSTEFUSE, DSP, CAM, L3INIT, GPU, WKUPAON, and IVA.

## Important APIs, Types, and Functions
The entry point is `omap54xx_powerdomains_init()`, registering `omap4_pwrdm_operations` and `powerdomains_omap54xx[]`. Descriptors define voltage domains `core`, `mpu`, `wkup`, and `mm`, PRM partitions/instances, supported power states, logic-retention states, memory-bank retention/on states, and low-power-state-change flags.

## Control Flow
SoC powerdomain init registers the descriptor list and completes generic initialization. `pm44xx.c` then treats OMAP5 as an OMAP4+ PM target, including CPU OSWR disable erratum handling and static MPU-to-EMIF dependency.

## State and Persistence Behavior
Static descriptors become runtime powerdomain objects with counters, locks, and voltage-domain pointers. Hardware state is persisted in OMAP54xx PRM registers.

## Dependencies and Integration Points
It depends on OMAP54xx PRM/PRCM/MPU PRCM headers and the generic powerdomain framework. It integrates with OMAP5 PM, clockdomains, voltage domains, and CPU low-power code.

## Risks
Some memory-bank `pwrsts_mem_on` values are retention/off-retention rather than simply ON, so assumptions from OMAP4 data may not apply. Bad generated offsets or state capabilities can break deep idle or context retention.

## Test Signals
Boot OMAP5, verify all listed domains register and PM init succeeds, check MPU/CPU/CORE/DSP/GPU/IVA transitions through debugfs or tracepoints, and run suspend/idle cycles without context-loss warnings.
