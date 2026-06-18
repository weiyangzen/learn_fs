# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains3xxx_data.c

## Purpose
`powerdomains3xxx_data.c` defines OMAP3, AM35x, and TI81xx powerdomain descriptors and TI81xx-specific powerdomain operations. It selects descriptor sets based on exact silicon revision and registers them with the generic framework.

## Important APIs, Types, and Functions
Important OMAP3 descriptors include `iva2_pwrdm`, `mpu_3xxx_pwrdm`, core variants, `dss_pwrdm`, `sgx_pwrdm`, `cam_pwrdm`, `per_pwrdm`, `emu_pwrdm`, `neon_pwrdm`, `usbhost_pwrdm`, and DPLL pseudo-domains. TI81xx descriptors include ALWON, DEVICE, ACTIVE, DEFAULT, IVHD/GEM/HDVPSS/SGX/ISP domains. Entry point is `omap3xxx_powerdomains_init()`. TI81xx callbacks include set/read power state and wait-transition helpers.

## Control Flow
Init exits unless OMAP34xx or TI81xx. Non-TI81xx registers `omap3_pwrdm_operations`; TI81xx paths register custom `ti81xx_pwrdm_operations`. Revision selection registers AM35x, TI814x, TI816x, or OMAP3430 common plus ES-specific arrays, then calls `pwrdm_complete_init()`.

## State and Persistence Behavior
Static descriptors become mutable runtime powerdomain state. TI81xx callbacks persist hardware power targets in TI81xx PRM registers and poll transition bits with a bailout timeout.

## Dependencies and Integration Points
It depends on SoC/revision detection, shared OMAP2/3 domains, PRM/CM register headers, and OMAP3/TI81xx backend operations. It feeds OMAP3 PM code, hwmod code, and PM debug.

## Risks
Revision gating is critical: OMAP3430 ES3.1+ enables hardware SAR for core/USBTLL while earlier chips avoid broken SAR errata. AM35x domains are mostly ON-only. TI81xx has custom register layout and a special GFX status source. Wrong selection can hang suspend or misread state.

## Test Signals
Boot OMAP3430 ES1/ES2/ES3.1, OMAP3630, AM35x, TI814x, and TI816x where available. Verify correct domain list, SAR flag behavior, TI81xx transition polling, and stable off/retention transitions under OMAP3 PM.
