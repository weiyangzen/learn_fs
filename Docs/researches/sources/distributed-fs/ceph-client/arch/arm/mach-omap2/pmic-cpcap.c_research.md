# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pmic-cpcap.c

## Purpose
`pmic-cpcap.c` registers PMIC voltage-control data for Motorola OMAP4 CPCAP systems and associated external regulators. It covers CPCAP core/IVA regulators, MAX8952 MPU regulator, and FAN535503/FAN535508 regulators used on non-Droid-Bionic CPCAP boards.

## Important APIs, Types, and Functions
Important functions are `omap_cpcap_vsel_to_uv()`, `omap_cpcap_uv_to_vsel()`, `omap_max8952_vsel_to_uv()`, `omap_max8952_uv_to_vsel()`, `omap_fan535503_vsel_to_uv()`, `omap_fan535508_vsel_to_uv()`, corresponding `uv_to_vsel()` helpers, `omap4_cpcap_init()`, and `cpcap_late_init()`. Data objects are `omap_cpcap_core`, `omap_cpcap_iva`, `omap443x_max8952_mpu`, `omap4_fan_core`, and `omap4_fan_iva`.

## Control Flow
Common late PM init calls `omap4_cpcap_init()`. It returns unless a `motorola,cpcap` node exists, registers MAX8952 for `mpu`, then registers CPCAP core/IVA only on `motorola,droid-bionic` or FAN regulators otherwise. A late initcall configures OMAP4 VC PMIC signaling to retention for CPCAP boards.

## State and Persistence Behavior
All descriptor state is static. Hardware state is voltage-domain PMIC registration and VC/VP signaling configuration. Conversion helpers clamp selector/voltage values into supported ranges.

## Dependencies and Integration Points
It depends on OF compatible detection, `voltage.h`, `pm.h`, `vc.h`, and OMAP4 SoC detection. It integrates with Motorola CPCAP MFD/PMIC DT nodes, OMAP voltage domains, and OPP scaling.

## Risks
Board-specific regulator topology matters. Selecting CPCAP versus FAN core/IVA regulators incorrectly can program the wrong I2C slave/register pair. Voltage clamping hides invalid requests but can still produce unstable OPP behavior if tables and regulators disagree.

## Test Signals
Boot Motorola CPCAP OMAP4 boards, verify PMIC registration for `mpu`, `core`, and `iva`, confirm VC signaling setup, exercise OPP transitions, and compare actual rail voltages where possible. Test both Droid Bionic and non-Bionic CPCAP board compatibles.
