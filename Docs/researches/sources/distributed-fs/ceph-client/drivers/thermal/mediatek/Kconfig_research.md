# sources/distributed-fs/ceph-client/drivers/thermal/mediatek/Kconfig

Purpose: Kconfig menu for MediaTek thermal drivers. It gates the MediaTek submenu on `THERMAL_OF` and exposes legacy AUXADC, LVTS, and LVTS debugfs options.

Important entries: `MTK_THERMAL` is the parent tristate and documents MediaTek software thermal solutions. `MTK_SOC_THERMAL` enables the AUXADC controller driver and depends on `HAS_IOMEM`. `MTK_LVTS_THERMAL` enables the Low Voltage Thermal Sensor driver and depends on `HAS_IOMEM`. `MTK_LVTS_THERMAL_DEBUGFS` is a bool depending on `MTK_LVTS_THERMAL && DEBUG_FS`.

Control flow/integration: selecting the parent makes the child symbols visible. The Makefile maps the two implementation objects to `CONFIG_MTK_SOC_THERMAL` and `CONFIG_MTK_LVTS_THERMAL`; debugfs affects conditional code inside `lvts_thermal.c`.

State/persistence: no runtime state; build-time configuration only. Dependencies: thermal OF framework and MMIO support; LVTS debugfs additionally depends on debugfs.

Risks: the help text has a typo in "mechaisms"; the parent symbol can be enabled without selecting either concrete driver. Test signals are Kconfig visibility, module/built-in combinations, debugfs code exclusion when disabled, and successful allmodconfig-style dependency resolution.
