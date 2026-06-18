<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/event/exynos-nocp.c -->
# sources/distributed-fs/ceph-client/drivers/devfreq/event/exynos-nocp.c

Purpose: registers Samsung Exynos NoC Probe hardware as a devfreq-event provider for AXI bus bandwidth measurement.

Important APIs and control flow: `exynos_nocp_probe()` allocates `struct exynos_nocp`, parses DT resources, maps MMIO through regmap, registers one devfreq-event descriptor named from the node full name, stores driver data, and enables the optional `nocp` clock. `exynos_nocp_set_event()` disables statistics, sets period to zero, configures four counters for byte, chain, cycle, and chain events, programs min/max alarm mode, enables alarm/statistics and global enable, then re-enables measurements. `exynos_nocp_get_event()` reads four counter values and combines low/high register pairs into `load_count` and `total_count`. Remove disables the clock.

State and persistence behavior: persistent state is the provider object with regmap, clock, device, descriptor, and event device pointer. Counter state is in hardware; each `set_event` resets/reconfigures the measurement window and `get_event` samples current values.

Dependencies and integration points: uses the devfreq-event core, `exynos-nocp.h` register definitions, platform resource mapping, regmap-mmio, optional clock named `nocp`, and OF compatible `samsung,exynos5420-nocp`. Exynos bus can acquire this provider through `devfreq-events`.

Risks and test signals: the driver registers the event device before enabling the clock, so a very early consumer could call into unclocked hardware. Descriptor name uses `np->full_name`, while event-core fallback matching compares node names, making phandle matching the reliable path. `counter[1] << 16` is 32-bit arithmetic before assignment. Test signals include successful provider registration, regmap read/write success, nonzero load/total counts under bus traffic, repeated set/get windows, clock enable/disable balance, and Exynos bus consumer probe without permanent deferral.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/event/exynos-nocp.c -->
