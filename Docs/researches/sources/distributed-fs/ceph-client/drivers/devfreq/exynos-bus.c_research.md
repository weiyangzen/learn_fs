<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/exynos-bus.c -->
# sources/distributed-fs/ceph-client/drivers/devfreq/exynos-bus.c

Purpose: generic Exynos bus frequency driver using devfreq. Parent bus nodes use simple-ondemand with devfreq-event counters; child bus nodes can use passive devfreq to follow a parent. It can also instantiate an Exynos interconnect provider child device.

Important APIs and control flow: `exynos_bus_probe()` determines passive versus parent mode from a `devfreq` phandle, parses clocks and OPPs, then registers a devfreq profile. Parent mode calls `exynos_bus_parent_parse_of()` to set `vdd` regulators, acquire `devfreq-events`, and read an optional saturation ratio. `exynos_bus_profile_init()` sets polling, target, status, and exit callbacks, registers the simple-ondemand devfreq device, registers an OPP notifier, enables event providers, and starts sampling. Passive mode finds the parent devfreq and registers `DEVFREQ_GOV_PASSIVE`. `exynos_bus_target()` uses `devfreq_recommended_opp()` and `dev_pm_opp_set_rate()`. `exynos_bus_get_dev_status()` picks the busiest event provider and scales load by the saturation ratio.

State and persistence behavior: per-bus state includes parent device, optional interconnect child platform device, devfreq pointer, event provider array/count, mutex, current frequency, regulator token, bus clock, and saturation ratio. OPP/regulator/event resources live until profile exit or probe error cleanup.

Dependencies and integration points: depends on devfreq core, passive and simple-ondemand governors, devfreq-event providers, OPP/regulator/clock frameworks, OF phandles, and `exynos-generic-icc` when `#interconnect-cells` is present. It soft-depends on `exynos_ppmu`.

Risks and test signals: passive cleanup does not put regulators because passive mode never sets them; parent error labels call `dev_pm_opp_put_regulators(bus->opp_token)` even when passive mode may leave the token unset. Suspend/resume unconditionally toggles event devices, which may be wrong for passive nodes without events. `busy_time = load_count * 100 / ratio` can overflow for very large counters. Test signals include parent and passive DT topologies, event-provider deferral, OPP rate/voltage transitions, interconnect child creation/removal, suspend/resume for both modes, saturation-ratio effects, and governor stats under generated bus traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/exynos-bus.c -->
