# sources/distributed-fs/ceph-client/drivers/thermal/mediatek/Makefile

Purpose: build mapping for MediaTek thermal drivers.

Important entries: `obj-$(CONFIG_MTK_SOC_THERMAL) += auxadc_thermal.o` builds the legacy AUXADC thermal driver. `obj-$(CONFIG_MTK_LVTS_THERMAL) += lvts_thermal.o` builds the LVTS driver.

Control flow/integration: this file is consumed by Kbuild under `drivers/thermal/mediatek`. It matches the symbols declared in the adjacent Kconfig and contains no composite objects or conditional subdirectories.

State/persistence: build-time only. Dependencies are exactly the Kconfig symbols.

Risks/test signals: risk is low; failures would be missing object inclusion, stale symbol names, or module build errors. Test with built-in and module configurations for both symbols and with `CONFIG_MTK_LVTS_THERMAL_DEBUGFS` toggled to ensure it only changes `lvts_thermal.o` contents.
