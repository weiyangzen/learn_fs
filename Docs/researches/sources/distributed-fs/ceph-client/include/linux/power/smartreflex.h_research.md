# sources/distributed-fs/ceph-client/include/linux/power/smartreflex.h

Purpose: defines OMAP SmartReflex register offsets, bit fields, platform data, runtime device state, class-driver hooks, and public enable/disable APIs for adaptive voltage scaling.

Important APIs and types: macros define SmartReflex IP versions, register offsets, bit shifts/masks for sensor enable, error generation, min/max/avg, IRQ status/enable, clock lengths, and OMAP3430 defaults. `struct omap_sr` stores runtime device state including platform device, nvalue table, voltage domain, debugfs dir, IRQ, clock, IP type, calibration/tuning values, MMIO base, autocomp and enabled flags. `sr_test_cond_timeout()` busy-waits with microsecond delay. `struct omap_sr_pmic_data`, `struct omap_smartreflex_dev_attr`, `struct omap_sr_class_data`, `struct omap_sr_nvalue_table`, and `struct omap_sr_data` describe PMIC hooks, device attributes, class operations, efuse n-target data, and platform data. APIs include OMAP voltage-domain enable/disable/reset and class-driver hooks when `CONFIG_POWER_AVS_OMAP` is enabled.

Control flow: platform data describes each SR instance and voltage domain. The SmartReflex driver maps registers, initializes clocks/IRQs/calibration, class driver registers callbacks, and runtime enable/configure paths program sensors/error/minmax generation and notify class code of IRQ events. Voltage-domain code can enable/disable SR or reset voltage through the exported APIs.

State and persistence: runtime state includes register programming, clock/IRQ handles, voltage-domain association, calibration n-values from efuse, autocomp state, debugfs data, and enable bit. Efuse calibration is persistent hardware data; header state itself is live kernel state.

Dependencies and integration points: integrates with OMAP voltage domains, PMIC setup, platform devices, clocks, MMIO, IRQs, debugfs, delay loops, and optional AVS config. Disabled AVS builds provide no-op voltage-domain APIs and omit class hook prototypes.

Risks and test signals: risks include wrong register offsets by IP version, busy-wait timeouts, IRQ status mask mistakes, efuse n-value mismatch to voltage domain, class callback lifetime, voltage reset errors, and no-op stubs masking missing AVS. Test OMAP3/OMAP4 SR enable/disable, IRQ/errorgen/minmax configuration, voltage-domain integration, PMIC init, efuse table parsing, timeout paths, and AVS-disabled builds.
