# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains44xx_data.c

## Purpose
`powerdomains44xx_data.c` defines OMAP44xx powerdomain descriptors generated from TI hardware databases. It models CORE, GFX, ABE, DSS, TESLA, WKUP, CPU0/CPU1, EMU, MPU, IVAHD, CAM, L3INIT, L4PER, always-on core, and CEFUSE domains.

## Important APIs, Types, and Functions
The main API is `omap44xx_powerdomains_init()`, which registers `omap4_pwrdm_operations` and `powerdomains_omap44xx[]`. Each descriptor declares PRM partition, instance offset, voltage domain, supported states, logic-retention states, memory-bank state capabilities, and low-power-state-change flags where supported.

## Control Flow
OMAP4 SoC init calls `omap44xx_powerdomains_init()`. The generic framework registers all descriptors and initializes their next states to ON. Later `pm44xx.c` programs suspend targets using `pwrdm_get_valid_lp_state()`.

## State and Persistence Behavior
Generated static descriptors become mutable runtime objects. Hardware power state persists in OMAP4 PRM partition registers via `omap4_pwrdm_operations`.

## Dependencies and Integration Points
It depends on OMAP4430 PRM/PRCM register headers and powerdomain framework APIs. It integrates with OMAP4 voltage domains, clockdomains, MPUSS low-power code, and PM suspend setup.

## Risks
Generated data should stay synchronized with hardware databases. Wrong PRCM partition/offset or memory-bank capability can hang suspend or cause data loss. CPU powerdomains are treated specially by `pm44xx.c`.

## Test Signals
Boot OMAP4430/4460/4470 variants, verify domain registration, voltage-domain association, PM init target setup, and suspend/idle transitions for CORE, MPU, CPU, ABE, DSS, GFX, and L4PER domains.
