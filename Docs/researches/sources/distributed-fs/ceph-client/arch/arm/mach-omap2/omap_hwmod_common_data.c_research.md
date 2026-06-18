# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_hwmod_common_data.c

## Purpose
`omap_hwmod_common_data.c` provides shared hwmod sysconfig bitfield descriptions and a few common device attributes used by multiple OMAP SoC hwmod data files. It centralizes how different IP generations encode idle, standby, wakeup, reset, autoidle, and DMA-disable bits in SYSCONFIG-style registers.

## Important APIs, Types, and Functions
The exported data objects are `omap_hwmod_sysc_type1`, `omap_hwmod_sysc_type2`, `omap_hwmod_sysc_type3`, `omap2_3_dss_dispc_dev_attr`, `omap34xx_sr_sysc_fields`, `omap36xx_sr_sysc_fields`, `omap3_sham_sysc_fields`, `omap3xxx_aes_sysc_fields`, `omap_hwmod_sysc_type_mcasp`, and `omap_hwmod_sysc_type_usb_host_fs`. They are `struct sysc_regbits` or small hwmod device-attribute structures.

## Control Flow
There is no imperative control flow. Other hwmod descriptor files reference these objects through `.sysc_fields` and device attribute pointers. At runtime the hwmod framework reads those offsets while composing register masks and values for reset, idle mode, standby mode, and wakeup configuration.

## State and Persistence Behavior
All state is static descriptor state compiled into the kernel. Persistent effects occur only indirectly when hwmod operations write hardware sysconfig registers based on these shared field maps.

## Dependencies and Integration Points
The file depends on `omap_hwmod.h`, `omap_hwmod_common_data.h`, and `linux/platform_data/ti-sysc.h`. It supports legacy hwmod users and also aligns with the newer `ti-sysc` platform data path in `pdata-quirks.c`.

## Risks
Incorrect bit shifts are high impact because they affect many modules, not one device. A wrong field can disable wakeups, fail resets, select unsupported idle modes, or make crypto/display/SmartReflex/McASP/USB host modules misbehave across several SoCs.

## Test Signals
Compile all OMAP hwmod users. Runtime signals include successful reset/idle cycles for type1, type2, type3, SmartReflex, SHAM, AES, McASP, and USB host FS blocks. Suspended systems should still wake from modules with wakeup-capable sysconfig fields.
