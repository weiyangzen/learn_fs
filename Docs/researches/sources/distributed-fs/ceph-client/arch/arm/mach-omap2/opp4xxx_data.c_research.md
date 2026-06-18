# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/opp4xxx_data.c

## Purpose
`opp4xxx_data.c` defines OMAP443x and OMAP446x voltage data for MPU, IVA, and CORE domains. It supplies nominal voltages, eFuse offsets, and SmartReflex/voltage-processor error parameters for OMAP4 voltage scaling.

## Important APIs, Types, and Functions
The exported arrays are `omap443x_vdd_mpu_volt_data[]`, `omap443x_vdd_iva_volt_data[]`, `omap443x_vdd_core_volt_data[]`, `omap446x_vdd_mpu_volt_data[]`, `omap446x_vdd_iva_volt_data[]`, and `omap446x_vdd_core_volt_data[]`, all terminated by zero rows.

## Control Flow
No functions execute in this file. Late PM/voltage initialization selects the correct arrays based on OMAP4 revision and registers them with the voltage framework after PMIC data has been attached.

## State and Persistence Behavior
It stores static voltage-calibration data only. Runtime persistence is in voltage domain structures, eFuse-derived calibration, and PMIC/VC/VP programmed state.

## Dependencies and Integration Points
It depends on `soc.h`, `control.h`, `omap_opp_data.h`, and `pm.h`. It integrates with TWL6030 or CPCAP/FAN/MAX8952 PMIC support, SmartReflex, OMAP4 OPP/cpufreq, and the MPU/IVA/CORE voltage domains.

## Risks
OMAP4430 and OMAP4460 tables differ; using the wrong voltages or eFuse offsets can cause unstable high OPPs or excess power. CORE over-voltage entries must remain aligned with silicon requirements.

## Test Signals
Boot OMAP443x/446x boards with their PMICs, verify voltage-domain table selection and eFuse reads, exercise OPP transitions, and run suspend/resume plus CPU/IVA load tests at turbo/nitro-class operating points where available.
