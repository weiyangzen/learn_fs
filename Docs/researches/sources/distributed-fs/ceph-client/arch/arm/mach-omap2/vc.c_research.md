<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vc.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vc.c

### Purpose
`vc.c` implements the OMAP Voltage Controller layer: PMIC I2C channel setup, bypass voltage scaling, sleep/off voltage signaling, and voltage-ramp timing calculation for OMAP3/4 voltage domains.

### Important APIs, Types, And Functions
Public APIs are `omap_vc_init_channel()`, `omap_vc_pre_scale()`, `omap_vc_post_scale()`, `omap_vc_bypass_scale()`, `omap3_vc_set_pmic_signaling()`, and `omap4_vc_set_pmic_signaling()`. Important internal structures include `omap_vc_channel_cfg`, `omap3_vc_timings`, and the static `vc` state used for PMIC signaling.

### Control Flow
Channel init validates PMIC and register callbacks, chooses default or mutant channel bit layouts, programs PMIC slave/register addresses, writes command voltage values, configures I2C mode and timing, and then applies OMAP3 or OMAP4 sleep/off timing setup. Bypass scaling updates the ON command value, writes a VC bypass command, waits for the valid bit, and delays for the PMIC slew interval.

### State, Persistence, And Dependencies
The file persists a global `vc` signaling state and one-time I2C initialization flags. It mutates per-domain `omap_vc_channel` fields and PRM/SCRM/control-module registers. Dependencies include PMIC conversion callbacks, voltage tables, power-domain state constants, oscillator timing from PM code, and SoC-specific VC register data.

### Integration Points
`omap_voltage_late_init()` calls `omap_vc_init_channel()` and may set a domain's scale method to `omap_vc_bypass_scale()`. VP force-update paths reuse `omap_vc_pre_scale()` and `omap_vc_post_scale()`.

### Risks
The global `vc` state assumes only one domain seeds PMIC sleep signaling. The bypass wait loop has fixed retry counts and returns timeout if the valid bit never settles. Unsupported sysclk values skip OMAP4 high-speed I2C timing programming. PMIC min/max clamping can hide requested off-range voltages except for warnings.

### Test Signals
Useful tests include boot-time VC register dumps, DVFS scale up/down, retention/off-idle PMIC signaling, high-speed I2C timing on each supported sysclk, and forced timeout/error injection for bypass scaling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vc.c -->
