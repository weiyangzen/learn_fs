# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains7xx_data.c

## Purpose
`powerdomains7xx_data.c` defines DRA7xx/DRA72x/DRA74x/DRA76x powerdomain descriptors. It models multimedia, CPU, interconnect, wakeup, DSP, EVE, camera, display, GPU, VPE, efuse, and always-on domains for the OMAP4-style framework.

## Important APIs, Types, and Functions
The entry point is `dra7xx_powerdomains_init()`. Base descriptors are in `powerdomains_dra7xx[]`, with variant-specific `powerdomains_dra76x[]`, `powerdomains_dra74x[]`, and `powerdomains_dra72x[]` selecting customer efuse behavior. Domains include IVA, RTC, IPU, DSS, L4PER, GPU, WKUPAON, CORE, COREAON, CPU0/CPU1, VPE, MPU, L3INIT, EVE1-4, EMU, DSP1/2, and CAM.

## Control Flow
Init registers `omap4_pwrdm_operations`, registers the common DRA7xx domain set, then conditionally registers the appropriate CUSTEFUSE domain based on `soc_is_dra76x()`, `soc_is_dra74x()`, or `soc_is_dra72x()`. It completes generic init afterward.

## State and Persistence Behavior
Descriptors become mutable runtime objects with counters/locks after registration. Hardware state is programmed in DRA7xx PRM and MPU PRCM partitions. Many DRA7 domains allow OFF/ON only, with memory banks ON-only.

## Dependencies and Integration Points
It depends on DRA7xx PRM/PRCM headers, SoC detection, and the generic powerdomain framework. It integrates with `pm44xx.c`, DRA7 static dependency handling, remoteproc/media/display/GPU subsystems, and clockdomain registration.

## Risks
Variant-specific CUSTEFUSE handling is easy to get wrong because the same `custefuse_pwrdm` name maps to always-on or controllable descriptors. DRA7 has many accelerator domains; missing a domain can prevent driver PM or remoteproc operation.

## Test Signals
Boot DRA72x, DRA74x, and DRA76x variants, verify correct CUSTEFUSE descriptor selection and all accelerator domains register. Test suspend/idle, remoteproc DSP/EVE/IPU power cycling, display/GPU/CAM/VPE use, and PM debug counters.
