# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_twl.c

## Purpose
`omap_twl.c` registers TWL4030/TWL6030 PMIC voltage-control data with OMAP voltage domains. It supplies voltage selector conversion functions, voltage-processor timing parameters, I2C register addresses, and OMAP3/4 PMIC wiring assumptions.

## Important APIs, Types, and Functions
Important functions are `twl4030_vsel_to_uv()`, `twl4030_uv_to_vsel()`, `twl6030_vsel_to_uv()`, `twl6030_uv_to_vsel()`, `omap3_twl_init()`, and `omap4_twl_init()`. Data objects include `omap3_mpu_pmic`, `omap3_core_pmic`, `omap4_mpu_pmic`, `omap4_iva_pmic`, and `omap4_core_pmic`.

## Control Flow
Common PM late init calls `omap3_twl_init()` and `omap4_twl_init()`. OMAP3 registers PMIC data for `mpu_iva` and `core`; OMAP4 registers `mpu`, `iva`, and `core` unless a Motorola CPCAP node is present. TWL6030 conversion lazily reads `REG_SMPS_OFFSET` via TWL I2C and caches the offset.

## State and Persistence Behavior
Static PMIC descriptor data persists for the voltage layer. Mutable file-local state is `is_offset_valid` and `smps_offset`, caching the TWL6030 eFuse offset. Hardware persistence is PMIC voltage register programming through the voltage processor.

## Dependencies and Integration Points
It depends on `linux/mfd/twl.h`, `soc.h`, `voltage.h`, and `pm.h`. It integrates with voltage-domain lookup, `omap_voltage_register_pmic()`, OMAP VC/VP I2C signaling, TWL MFD I2C access, SmartReflex, and OPP voltage scaling.

## Risks
Voltage conversion errors are high risk: they can underpower or overvolt MPU/core/IVA rails. TWL6030 has special >1.3V handling and a hardcoded 1.35V selector; unsupported voltages intentionally log errors and clamp. CPCAP detection must prevent conflicting PMIC registration on Motorola boards.

## Test Signals
Boot OMAP3/TWL4030 and OMAP4/TWL6030 boards, verify PMIC registration for expected voltage domains, exercise cpufreq/OPP voltage changes, validate SmartReflex/VC transactions, and check stable suspend/resume. Confirm CPCAP boards skip TWL OMAP4 registration.
