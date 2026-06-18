<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/event/Makefile -->
# sources/distributed-fs/ceph-client/drivers/devfreq/event/Makefile

Purpose: maps devfreq-event Kconfig symbols to provider object files.

Important APIs and control flow: adds `exynos-nocp.o`, `exynos-ppmu.o`, and `rockchip-dfi.o` to the build according to `CONFIG_DEVFREQ_EVENT_EXYNOS_NOCP`, `CONFIG_DEVFREQ_EVENT_EXYNOS_PPMU`, and `CONFIG_DEVFREQ_EVENT_ROCKCHIP_DFI`.

State and persistence behavior: none at runtime.

Dependencies and integration points: included by the parent devfreq build. The object names match platform drivers that register devfreq-event devices.

Risks and test signals: the only practical risk is symbol/object drift when provider files are renamed or Kconfig symbols change. Test signals are successful built-in and module builds for each provider and expected module names in `modules.order`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/event/Makefile -->
