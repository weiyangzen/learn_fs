# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains2xxx_data.c

## Purpose
`powerdomains2xxx_data.c` defines and registers OMAP2420/2430 powerdomain sets. It covers DSP, MPU, CORE, shared WKUP/GFX, and the OMAP2430 modem powerdomain.

## Important APIs, Types, and Functions
Important descriptors are `dsp_pwrdm`, `mpu_24xx_pwrdm`, `core_24xx_pwrdm`, and `mdm_pwrdm`. Init arrays are `powerdomains_omap24xx[]` and `powerdomains_omap2430[]`. Entry points are `omap242x_powerdomains_init()` and `omap243x_powerdomains_init()`.

## Control Flow
Each init function checks CPU type, registers `omap2_pwrdm_operations`, registers common OMAP24xx domains, optionally registers the 2430 modem domain, then calls `pwrdm_complete_init()` to force initial next states to ON.

## State and Persistence Behavior
Static descriptors become runtime framework state after registration. Hardware power targets are initialized to ON by `pwrdm_complete_init()` to avoid context loss in non-PM kernels.

## Dependencies and Integration Points
It depends on SoC detection, shared OMAP2/3 data, PRCM/PRM register offsets, and `omap2_pwrdm_operations`. It integrates with OMAP2 clockdomain and PM paths.

## Risks
OMAP2420 and 2430 have different DSP/modem topology. Registering `mdm_pwrdm` on 2420 or missing it on 2430 would misrepresent hardware. Memory-bank state definitions affect retention/off behavior.

## Test Signals
Boot OMAP2420 and OMAP2430 configs, confirm correct domain list, no PRCM operation failures, and valid transitions for DSP/MPU/CORE/GFX/MDM. PM debugfs should show initial ON state counters.
