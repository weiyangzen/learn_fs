# sources/distributed-fs/ceph-client/include/soc/amlogic/meson_ddr_pmu.h

Purpose: declares the Amlogic Meson DDR controller performance-monitor interface used by the DDR PMU platform driver.

Important APIs and types: `MAX_CHANNEL_NUM` and counter IDs define aggregate and per-channel monitor slots. `struct dmc_counter` stores total DDR controller request counts, idle/16-bit/all request variants, and per-channel counters. `struct dmc_hw_info` is the hardware operations table with `enable`, `disable`, AXI filter binding, IRQ counter collection, direct counter reads, controller/channel counts, sysfs format attributes, and capability bits. `struct dmc_info` binds those operations to mapped DDR/PLL registers, timer value, and IRQ. Public entry points are `meson_ddr_pmu_create()` and `meson_ddr_pmu_remove()`.

Control flow: a platform driver creates a PMU instance, programs filters and counters through `dmc_hw_info`, enables sampling, and collects counts either from interrupts or direct reads.

State and persistence: state is runtime-only MMIO mapping, IRQ number, timer period, and accumulated counter snapshots. No firmware or persistent configuration is stored.

Dependencies and integration points: integrates with platform devices, perf/PMU driver code, sysfs attributes, IRQ handling, and SoC-specific DDR controller register layouts.

Risks and test signals: risks include channel count exceeding fixed arrays, mismatched hardware callbacks, filter programming races while counters run, incorrect timer units, and register layout drift between Meson SoCs. Test PMU registration/removal, interrupt sampling, filter selection, all-channel versus per-channel counters, capability exposure, and build coverage for SoC variants.
