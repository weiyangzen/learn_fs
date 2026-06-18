# subset-b-001248 research

This grouped report covers the Linux devfreq core, devfreq-event framework, event providers, standard governors, and several SoC-specific devfreq users. Each source file has a delimited section for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/devfreq-event.c -->
# sources/distributed-fs/ceph-client/drivers/devfreq/devfreq-event.c

Purpose: implements the devfreq-event framework, a class-level registry for hardware event providers that expose raw load/total counters to devfreq device drivers. Providers register `struct devfreq_event_desc` instances and consumers acquire them directly or through device-tree phandles.

Important APIs and control flow: exported APIs include `devfreq_event_enable_edev()`, `devfreq_event_disable_edev()`, `devfreq_event_is_enabled()`, `devfreq_event_set_event()`, `devfreq_event_get_event()`, `devfreq_event_reset_event()`, `devfreq_event_get_edev_by_phandle()`, `devfreq_event_get_edev_count()`, `devfreq_event_add_edev()`, `devfreq_event_remove_edev()`, and devres wrappers. Enable/disable are reference-counted with `edev->enable_count`; provider `enable` and `disable` callbacks run only on 0-to-1 and 1-to-0 transitions. `set_event`, `get_event`, and `reset_event` validate enabled state, then serialize provider ops through `edev->lock`. Registration allocates a `devfreq_event_dev`, sets its class device name to `eventN`, adds sysfs read-only `name` and `enable_count`, and links it into the global list.

State and persistence behavior: global state is `devfreq_event_class`, `devfreq_event_list`, and `devfreq_event_list_lock`. Per-provider state is the descriptor pointer, enable count, mutex, class device, and list node. The framework does not persist counter samples; provider drivers own hardware state and driver data. Device-managed registration removes devices automatically on parent teardown.

Dependencies and integration points: depends on `include/linux/devfreq-event.h`, device core, devres, OF phandle parsing, class sysfs, and provider callbacks. Exynos bus and RK3399 DMC are direct consumers; Exynos PPMU/NoCP and Rockchip DFI are providers in this subset.

Risks and test signals: `devm_devfreq_event_add_edev()` returns `ERR_PTR(-ENOMEM)` instead of preserving provider registration errors, so probe diagnostics can be less precise. `enable_count_show()` reads without taking `edev->lock`. Phandle lookup first matches parent OF node, then falls back to node name versus descriptor name, which is fragile if DT naming changes. Test signals include balanced enable/disable counts, unbalanced disable warning, failed ops leaving counts unchanged, class devices under `/sys/class/devfreq-event/`, phandle lookup against real DT providers, and provider removal warning when still enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/devfreq-event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/devfreq.c -->
# sources/distributed-fs/ceph-client/drivers/devfreq/devfreq.c

Purpose: provides the generic Dynamic Voltage and Frequency Scaling framework for non-CPU devices. It owns devfreq class devices, governor registration and switching, OPP/PM QoS integration, polling helpers, transition statistics, transition notifiers, debugfs summaries, and devres convenience APIs.

Important APIs and control flow: `devfreq_add_device()` validates a parent/profile/governor, builds or adopts a frequency table, initializes frequency bounds from OPPs, registers a class device, allocates transition stats, installs PM QoS min/max requests and notifiers, locates or autoloads the governor, starts it, creates governor-specific sysfs visibility, and optionally registers a thermal cooling device. `devfreq_remove_device()` unregisters cooling, stops the governor, and unregisters the class device; `devfreq_dev_release()` removes list membership, QoS resources, profile exit hooks, OPP table references, SRCU notifier state, and memory. `devfreq_update_target()` asks the governor for a target, clamps it through `devfreq_get_freq_range()`, and calls `devfreq_set_target()`, which emits pre/post transition notifiers, invokes the profile `target()` callback, updates tracepoints, transition stats, `previous_freq`, and resume frequency. Polling governors use `devfreq_monitor_start/stop/suspend/resume()` and `devfreq_update_interval()`.

State and persistence behavior: global state includes `devfreq_class`, `devfreq_debugfs`, `devfreq_wq`, `devfreq_governor_list`, and `devfreq_list`. Per-device state includes profile callbacks, governor/data pointers, OPP table reference, PM QoS requests, min/max scaling bounds, delayed work, transition stats, SRCU notifier chain, suspend count, previous/resume/suspend frequencies, and optional cooling device. Statistics persist for the devfreq instance until `trans_stat` is reset or the device is removed.

Dependencies and integration points: integrates with OPP (`devfreq_recommended_opp()`, OPP notifiers, OPP-derived freq tables), PM QoS min/max frequency constraints, sysfs class attributes (`governor`, `cur_freq`, `target_freq`, `min_freq`, `max_freq`, `available_frequencies`, `trans_stat`, governor attrs), debugfs `devfreq/devfreq_summary`, thermal cooling, module autoload for governors, OF phandle helpers, and SRCU transition notifiers. Platform drivers in this subset call `devm_devfreq_add_device()` and usually `devm_devfreq_register_opp_notifier()`.

Risks and test signals: governor switching must roll back correctly if the new governor fails to start; remove paths depend on class-device release for cleanup; `devm_devfreq_unregister_opp_notifier()` and notifier devres matching use a devfreq-only matcher despite different resource payloads; freq tables can exceed one-page `trans_stat` output; QoS values convert Hz to kHz with different rounding for min and max; suspend/resume nesting depends on atomic counts. Test signals include governor autoload/switching, immutable-governor rejection, PM QoS min/max writes clamping targets, OPP availability changes recomputing bounds, polling interval and timer sysfs changes, transition notifier ordering, suspend frequency and resume restoration, cooling registration, and debugfs summary consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/devfreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/event/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/devfreq/event/Kconfig

Purpose: defines build-time configuration for devfreq-event provider support and the Exynos NoCP, Exynos PPMU, and Rockchip DFI event drivers.

Important APIs and control flow: `PM_DEVFREQ_EVENT` is a boolean menu gate for the event framework and its provider submenu. `DEVFREQ_EVENT_EXYNOS_NOCP` is tristate, depends on `ARCH_EXYNOS || COMPILE_TEST`, and selects `PM_OPP` plus `REGMAP_MMIO`. `DEVFREQ_EVENT_EXYNOS_PPMU` is tristate, depends on Exynos or compile testing, and selects `PM_OPP`. `DEVFREQ_EVENT_ROCKCHIP_DFI` is tristate, depends on Rockchip or compile testing.

State and persistence behavior: no runtime state; this file controls which provider modules are compiled and therefore whether DT phandles to those providers can bind.

Dependencies and integration points: consumed by the drivers/devfreq build. The selected symbols align with provider implementation dependencies on regmap, OPP, and SoC-specific headers. Consumer drivers such as Exynos bus and RK3399 DMC need matching providers available or probes defer.

Risks and test signals: missing `PM_DEVFREQ_EVENT` prevents all event providers from building even if consumers reference them. Rockchip DFI has optional perf-event code but no Kconfig select for `PERF_EVENTS`; it compiles that block only when the global symbol is enabled. Test signals are allmodconfig/allyesconfig builds, module builds for each tristate, and DT boot where providers probe before consumers or consumers defer cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/event/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/event/Makefile -->
# sources/distributed-fs/ceph-client/drivers/devfreq/event/Makefile

Purpose: maps devfreq-event Kconfig symbols to provider object files.

Important APIs and control flow: adds `exynos-nocp.o`, `exynos-ppmu.o`, and `rockchip-dfi.o` to the build according to `CONFIG_DEVFREQ_EVENT_EXYNOS_NOCP`, `CONFIG_DEVFREQ_EVENT_EXYNOS_PPMU`, and `CONFIG_DEVFREQ_EVENT_ROCKCHIP_DFI`.

State and persistence behavior: none at runtime.

Dependencies and integration points: included by the parent devfreq build. The object names match platform drivers that register devfreq-event devices.

Risks and test signals: the only practical risk is symbol/object drift when provider files are renamed or Kconfig symbols change. Test signals are successful built-in and module builds for each provider and expected module names in `modules.order`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/event/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/event/exynos-nocp.c -->
# sources/distributed-fs/ceph-client/drivers/devfreq/event/exynos-nocp.c

Purpose: registers Samsung Exynos NoC Probe hardware as a devfreq-event provider for AXI bus bandwidth measurement.

Important APIs and control flow: `exynos_nocp_probe()` allocates `struct exynos_nocp`, parses DT resources, maps MMIO through regmap, registers one devfreq-event descriptor named from the node full name, stores driver data, and enables the optional `nocp` clock. `exynos_nocp_set_event()` disables statistics, sets period to zero, configures four counters for byte, chain, cycle, and chain events, programs min/max alarm mode, enables alarm/statistics and global enable, then re-enables measurements. `exynos_nocp_get_event()` reads four counter values and combines low/high register pairs into `load_count` and `total_count`. Remove disables the clock.

State and persistence behavior: persistent state is the provider object with regmap, clock, device, descriptor, and event device pointer. Counter state is in hardware; each `set_event` resets/reconfigures the measurement window and `get_event` samples current values.

Dependencies and integration points: uses the devfreq-event core, `exynos-nocp.h` register definitions, platform resource mapping, regmap-mmio, optional clock named `nocp`, and OF compatible `samsung,exynos5420-nocp`. Exynos bus can acquire this provider through `devfreq-events`.

Risks and test signals: the driver registers the event device before enabling the clock, so a very early consumer could call into unclocked hardware. Descriptor name uses `np->full_name`, while event-core fallback matching compares node names, making phandle matching the reliable path. `counter[1] << 16` is 32-bit arithmetic before assignment. Test signals include successful provider registration, regmap read/write success, nonzero load/total counts under bus traffic, repeated set/get windows, clock enable/disable balance, and Exynos bus consumer probe without permanent deferral.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/event/exynos-nocp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/event/exynos-nocp.h -->
# sources/distributed-fs/ceph-client/drivers/devfreq/event/exynos-nocp.h

Purpose: defines the Exynos NoC Probe register offsets and bit masks used by `exynos-nocp.c`.

Important APIs and control flow: the header is macro/enum-only. `enum nocp_reg` maps control, statistic, alarm, source, alarm-mode, and value registers. Masks cover `NOCP_MAIN_CTL` enable bits, `NOCP_CFG_CTL` global/active bits, counter source event selection values such as cycle, busy, packet, byte, and chain, and counter alarm modes.

State and persistence behavior: none. It encodes the software-hardware ABI for the NoC Probe register block.

Dependencies and integration points: included only by the NoCP provider and relies on kernel `BIT()` availability through the including C file.

Risks and test signals: bitfield mistakes silently program wrong counters or alarms, causing governors to misread load. Test signals include register traces matching the Exynos hardware manual, `set_event()` programming byte/cycle sources as intended, and hardware counter values changing with synthetic memory traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/event/exynos-nocp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/event/exynos-ppmu.c -->
# sources/distributed-fs/ceph-client/drivers/devfreq/event/exynos-ppmu.c

Purpose: registers Samsung Exynos PPMU v1.1 and v2.0 performance monitor blocks as devfreq-event providers, usually for bus or memory utilization sampling.

Important APIs and control flow: `exynos_ppmu_probe()` parses MMIO and clock resources, discovers child `events` nodes, allocates a descriptor per event, registers devfreq-event devices, and enables the optional `ppmu` clock. Event names map through `ppmu_events[]` to one of four hardware counters. v1 callbacks `exynos_ppmu_set_event()`, `exynos_ppmu_get_event()`, and `exynos_ppmu_disable()` enable the cycle counter plus selected PM counter, program event type, reset counters, sample `CCNT` and PM counter values, then disable the selected counter. v2 callbacks reset more registers, program `PPMU_V2_CH_EVx_TYPE`, use manual start mode, and handle the wider counter 3 high/low pair.

State and persistence behavior: per-controller state includes regmap, clock, ppmu type, descriptor array, event-device array, and event count. Individual event state is mostly descriptor data (`name`, `event_type`, ops, driver_data). Hardware counters are reset on `set_event` and sampled on `get_event`; no software accumulation is kept.

Dependencies and integration points: depends on devfreq-event core, `exynos-ppmu.h`, regmap-mmio, DT child nodes under `events`, optional `event-name` and `event-data-type` properties, OF compatibles `samsung,exynos-ppmu` and `samsung,exynos-ppmu-v2`, and consumers such as Exynos bus. `MODULE_SOFTDEP` in Exynos bus expects this provider to load first.

Risks and test signals: unknown child names are skipped but `info->num_events` remains the original child count, leaving trailing zero descriptors that can fail registration. v2 `set_event()` does not explicitly reject a negative ID before shifting. The clock is enabled after event-device registration. `exynos_ppmu_v2_get_event()` returns success if reading `PPMU_V2_CNTENC` fails. Test signals include DTs with all valid event children, v1 and v2 counter reads, default event data type selection, skipped unknown child behavior, counter 3 high/low handling, clocked register access, and consumer utilization values under generated traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/event/exynos-ppmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/event/exynos-ppmu.h -->
# sources/distributed-fs/ceph-client/drivers/devfreq/event/exynos-ppmu.h

Purpose: defines register offsets, counter IDs, event encodings, operating modes, and bit masks for Exynos PPMU v1.1 and v2.0 blocks.

Important APIs and control flow: enums identify enable/disable state, four PM counters, v1 event types such as read/write data/request/busy/latency counts, v1 register offsets, v2 modes, v2 event types, and v2 register offsets. Macros define PMNC reset/enable bits, counter masks, and indexed register helpers `PPMU_PMNCT()`, `PPMU_BEVTxSEL()`, `PPMU_V2_PMNCT()`, and `PPMU_V2_CH_EVx_TYPE()`.

State and persistence behavior: none at runtime; this header fixes the register ABI used by the PPMU provider.

Dependencies and integration points: included by `exynos-ppmu.c`. It depends on `BIT()` through the including kernel headers.

Risks and test signals: duplicated PMNC macro names in v1 and v2 sections are currently identical but can hide hardware-version differences. Any offset or mask error changes measured load and governor decisions. Test signals are register programming traces for v1/v2, counter reset and enable bits matching datasheets, and event type values matching DT bindings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/event/exynos-ppmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/event/rockchip-dfi.c -->
# sources/distributed-fs/ceph-client/drivers/devfreq/event/rockchip-dfi.c

Purpose: exposes Rockchip DDR DFI monitor counters as both a devfreq-event provider and, when `CONFIG_PERF_EVENTS` is enabled, a `rockchip_ddr` perf PMU for DDR bandwidth/cycle accounting.

Important APIs and control flow: `rockchip_dfi_probe()` maps DDR monitor registers, obtains the PMU GRF syscon, initializes SoC-specific DDR type/channel/bus-width/stride data for RK3399/RK3568/RK3588, registers one devfreq-event descriptor, and initializes the optional perf PMU. `rockchip_dfi_enable()` reference-counts users, enables the monitor clock, translates DDR type to control bits, programs each active channel, and enables software counting. `rockchip_dfi_get_event()` reads per-channel counters, subtracts the last event sample, reports the busiest channel's access count times four as load and clock cycles as total, then stores the new sample. Perf support accumulates 32-bit wrapping counters into 64-bit totals using a seqlock and one-second hrtimer, exposes cycles/read/write/bytes events, and migrates the PMU context on CPU hotplug.

State and persistence behavior: persistent state includes event descriptor, last devfreq-event sample, perf last/total samples, seqlock, device/MMIO/syscon/clock, usecount mutex, DDR type, active channel mask, channel bus widths, stride/control quirks, LPDDR5 mode, count multiplier, perf PMU, hrtimer, CPU, and active event count. Hardware counters run while enabled; software accumulates perf totals across counter wraps.

Dependencies and integration points: depends on devfreq-event core, Rockchip GRF headers, syscon/regmap, DDR type constants, clock framework, perf events, CPU hotplug, hrtimers, and compatibles `rockchip,rk3399-dfi`, `rockchip,rk3568-dfi`, and `rockchip,rk3588-dfi`. RK3399 DMC consumes this event provider through `devfreq-events`.

Risks and test signals: `rockchip_dfi_enable()` increments `usecount` before clock/control setup and does not roll it back on later failures, which can leave the provider logically enabled after an error. Devfreq-event load uses a hardcoded multiplier of four rather than SoC bus-width/burst metadata used by perf. Perf add/del updates `active_events` without explicit locking. LPDDR5 monitor version >= 0x40 is rejected. Test signals include balanced usecount under devfreq plus perf users, correct DDR type detection, channel masks and widths per SoC, stable perf counts across 32-bit wrap, CPU hotplug migration, RK3399 DMC utilization changes, and graceful rejection of unsupported memory types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/event/rockchip-dfi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/exynos-bus.c -->
# sources/distributed-fs/ceph-client/drivers/devfreq/exynos-bus.c

Purpose: generic Exynos bus frequency driver using devfreq. Parent bus nodes use simple-ondemand with devfreq-event counters; child bus nodes can use passive devfreq to follow a parent. It can also instantiate an Exynos interconnect provider child device.

Important APIs and control flow: `exynos_bus_probe()` determines passive versus parent mode from a `devfreq` phandle, parses clocks and OPPs, then registers a devfreq profile. Parent mode calls `exynos_bus_parent_parse_of()` to set `vdd` regulators, acquire `devfreq-events`, and read an optional saturation ratio. `exynos_bus_profile_init()` sets polling, target, status, and exit callbacks, registers the simple-ondemand devfreq device, registers an OPP notifier, enables event providers, and starts sampling. Passive mode finds the parent devfreq and registers `DEVFREQ_GOV_PASSIVE`. `exynos_bus_target()` uses `devfreq_recommended_opp()` and `dev_pm_opp_set_rate()`. `exynos_bus_get_dev_status()` picks the busiest event provider and scales load by the saturation ratio.

State and persistence behavior: per-bus state includes parent device, optional interconnect child platform device, devfreq pointer, event provider array/count, mutex, current frequency, regulator token, bus clock, and saturation ratio. OPP/regulator/event resources live until profile exit or probe error cleanup.

Dependencies and integration points: depends on devfreq core, passive and simple-ondemand governors, devfreq-event providers, OPP/regulator/clock frameworks, OF phandles, and `exynos-generic-icc` when `#interconnect-cells` is present. It soft-depends on `exynos_ppmu`.

Risks and test signals: passive cleanup does not put regulators because passive mode never sets them; parent error labels call `dev_pm_opp_put_regulators(bus->opp_token)` even when passive mode may leave the token unset. Suspend/resume unconditionally toggles event devices, which may be wrong for passive nodes without events. `busy_time = load_count * 100 / ratio` can overflow for very large counters. Test signals include parent and passive DT topologies, event-provider deferral, OPP rate/voltage transitions, interconnect child creation/removal, suspend/resume for both modes, saturation-ratio effects, and governor stats under generated bus traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/exynos-bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/governor_passive.c -->
# sources/distributed-fs/ceph-client/drivers/devfreq/governor_passive.c

Purpose: implements the immutable passive devfreq governor, which derives a child device frequency from either a parent devfreq transition stream or CPUFreq policy transitions.

Important APIs and control flow: `devfreq_passive_get_target_freq()` delegates to driver-provided `devfreq_passive_data.get_target_freq` when present; otherwise it uses required OPP translation or index interpolation for `DEVFREQ_PARENT_DEV`, and required OPP translation or percentage interpolation for `CPUFREQ_PARENT_DEV`. For devfreq parents, `devfreq_passive_register_notifier()` installs a transition notifier and `devfreq_passive_notifier_call()` updates children before parent frequency decreases and after parent frequency increases. For CPUFreq parents, `cpufreq_passive_register_notifier()` registers a CPUFreq transition notifier, builds one `devfreq_cpu_data` entry per related policy, holds CPU OPP tables, and triggers an initial target update. CPUFreq post-change notifications update cached policy frequency and call `devfreq_update_target()`.

State and persistence behavior: driver-supplied `struct devfreq_passive_data` is mutated to store `this`, notifier block, and CPU data list. CPU parent state includes per-policy device pointer, first CPU, OPP table reference, current/min/max kHz values. The governor itself is a global immutable `struct devfreq_governor`.

Dependencies and integration points: depends on devfreq transition notifiers, CPUFreq notifiers/policies, cpumasks, OPP required-opps translation, PM QoS clamped `devfreq_get_freq_range()`, and child drivers such as Exynos bus and MediaTek CCI.

Risks and test signals: CPU interpolation divides by `cpu_max - cpu_min`, so malformed CPU policies with equal bounds are unsafe. Error unwinding after partial CPU data allocation does not call `delete_parent_cpu_data()` in all paths. Notifier callbacks must avoid lock inversions; the devfreq-parent path uses nested locking. Required-OPP absence falls back to index/percentage mappings that may not reflect real hardware ratios. Test signals include parent devfreq scale-up/down ordering, CPUFreq transition handling for multi-policy systems, required-opps translation, fallback interpolation, governor immutability in sysfs, notifier unregister on stop, and CPU OPP table reference cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/governor_passive.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/governor_performance.c -->
# sources/distributed-fs/ceph-client/drivers/devfreq/governor_performance.c

Purpose: registers the standard `performance` governor, which always requests the maximum available frequency.

Important APIs and control flow: `devfreq_performance_func()` returns `DEVFREQ_MAX_FREQ`; the core clamps this to the current max frequency and passes least-upper-bound/floor behavior to the profile target. `devfreq_performance_handler()` performs one immediate `update_devfreq()` on `DEVFREQ_GOV_START`. Module init/exit add and remove the governor.

State and persistence behavior: only global state is the static governor object. No per-device governor data is allocated.

Dependencies and integration points: depends on devfreq core and governor API. It is used by drivers that want deterministic maximum performance, including HiSilicon uncore when not platform-controlled.

Risks and test signals: it does not react to suspend/resume/update-interval events itself, so updates after QoS/OPP changes rely on core notifiers. Test signals include initial max-frequency transition, PM QoS max limiting the result, OPP table changes triggering core updates, and successful governor removal when no devices use it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/governor_performance.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/governor_powersave.c -->
# sources/distributed-fs/ceph-client/drivers/devfreq/governor_powersave.c

Purpose: registers the standard `powersave` governor, which always requests the minimum available frequency.

Important APIs and control flow: `devfreq_powersave_func()` returns `DEVFREQ_MIN_FREQ`; the core clamps this to the current min frequency. `devfreq_powersave_handler()` forces an immediate update on governor start. Module init and exit add/remove the governor.

State and persistence behavior: no per-device state; only the static governor object persists while loaded.

Dependencies and integration points: depends on devfreq core/governor API and the device profile target callback selected by the consumer driver.

Risks and test signals: like performance, it is event-minimal and relies on core QoS/OPP notifier paths for later constraint changes. Test signals include initial transition to minimum, PM QoS min raising the actual target, OPP availability updates, sysfs governor switching, and clean module unload when unused.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/governor_powersave.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/governor_simpleondemand.c -->
# sources/distributed-fs/ceph-client/drivers/devfreq/governor_simpleondemand.c

Purpose: implements the common polling governor that scales frequency from device busy/total time samples.

Important APIs and control flow: `devfreq_simple_ondemand_func()` calls `devfreq_update_stats()`, reads `df->last_status`, applies default or driver-provided thresholds (`upthreshold`, `downdifferential`), requests max frequency when total time is zero, when busy exceeds the up-threshold, or when current frequency is unknown, keeps current frequency in the hysteresis band, otherwise computes a proportional target from busy ratio and current frequency. `devfreq_simple_ondemand_handler()` starts/stops/suspends/resumes devfreq monitoring and applies interval updates through core helper functions.

State and persistence behavior: no private allocation. Per-device tuning is read from `struct devfreq_simple_ondemand_data` passed as `df->data`; polling state is owned by the devfreq core.

Dependencies and integration points: depends on profile `get_dev_status`, devfreq monitor helpers, and optional sysfs governor attrs `polling_interval` and `timer`. Used by Exynos bus, RK3399 DMC, Allwinner MBUS, and as a generic fallback for many other drivers.

Risks and test signals: threshold validation rejects `upthreshold > 100` or `upthreshold < downdifferential`, but a zero effective denominator can still occur if both are badly chosen around integer precedence in the target calculation. Busy/total values are shifted down only when either exceeds 24 bits, which changes precision. Test signals include zero-total max behavior, hysteresis band behavior, proportional downscaling, custom threshold rejection, polling interval zero/nonzero transitions, suspend/resume monitor state, and overflow-prone large counter samples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/governor_simpleondemand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/governor_userspace.c -->
# sources/distributed-fs/ceph-client/drivers/devfreq/governor_userspace.c

Purpose: implements the `userspace` governor, allowing users to request a device frequency through a governor-specific sysfs attribute.

Important APIs and control flow: `userspace_init()` allocates `struct userspace_data`, stores it in `devfreq->governor_data`, and creates a `userspace/set_freq` sysfs group. `set_freq_store()` parses an unsigned long, records it as valid under `devfreq->lock`, and calls `update_devfreq()`. `devfreq_userspace_func()` returns the stored user frequency when valid or keeps `previous_freq` before the first write. `userspace_exit()` removes the sysfs group if the kobject is still active and frees governor data.

State and persistence behavior: per-device governor state is `user_frequency` plus a valid bit. It persists while the governor is active and is discarded on governor switch/stop.

Dependencies and integration points: depends on devfreq core, sysfs, `kstrtoul`, and device profile target callbacks. i.MX bus and i.MX8M DDRC use this governor by default.

Risks and test signals: user writes are not prevalidated against OPPs; invalid values are resolved or rejected by the core/profile target path. State is lost across governor switching. Test signals include `set_freq` showing `undefined` before writes, target update after valid writes, OPP clamping/rejection for unsupported values, sysfs group creation/removal during governor switches, and cleanup after device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/governor_userspace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/hisi_uncore_freq.c -->
# sources/distributed-fs/ceph-client/drivers/devfreq/hisi_uncore_freq.c

Purpose: ACPI/PCC-backed HiSilicon uncore frequency scaling driver. It discovers firmware-supported uncore frequencies, registers dynamic OPPs, exposes related CPUs, and lets either the OS or platform firmware control uncore frequency through devfreq.

Important APIs and control flow: probe allocates `hisi_uncore_freq`, finds a PCC subspace ID from ACPI `_CRS`, requests and validates the PCC mailbox channel, queries platform frequency count and values, registers dynamic OPPs, queries capabilities, conditionally registers a shared `hisi_platform` governor, marks related CPUs from `related-package` or `related-cluster` properties, and registers a devfreq device. `hisi_uncore_cmd_send()` serializes PCC access, enforces minimum turnaround time, writes command/data to shared memory, rings the mailbox, polls command-complete/error status, copies returned data, and completes tx. `hisi_uncore_target()` sends SET_FREQ in MHz after OPP selection; `hisi_uncore_get_cur_freq()` sends GET_FREQ. The custom `hisi_platform` governor switches firmware mode to platform control on start and OS control on stop while suppressing polling through the IRQ-driven flag.

State and persistence behavior: per-device state stores PCC channel/client, channel ID, last command completion time, PCC mutex, devfreq pointer, related CPU mask, and capability flags. Dynamic OPPs live until devres cleanup. The custom governor has global usage counting protected by `hisi_platform_gov_usage_lock`.

Dependencies and integration points: depends on ACPI resources, PCC mailbox, devfreq/OPP/governor APIs, PM QoS units, CPU topology, device properties, and ACPI ID `HISI04F1`.

Risks and test signals: PCC shared memory ABI, command status polling, and `min_turnaround_time` handling are firmware-sensitive. Global governor registration must stay balanced across multiple devices. Related CPU discovery treats malformed firmware as fatal. The platform governor deliberately marks itself IRQ-driven though no IRQ exists. Test signals include PCC timeout/error handling, dynamic OPP list matching firmware, OS/platform mode transitions on governor start/stop/remove, multiple uncore domains sharing the governor, `related_cpus` sysfs output, and frequency get/set round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/hisi_uncore_freq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/imx-bus.c -->
# sources/distributed-fs/ceph-client/drivers/devfreq/imx-bus.c

Purpose: generic i.MX bus frequency scaling driver. It exposes a bus clock as a devfreq device, typically controlled from userspace, and can spawn a matching i.MX interconnect provider.

Important APIs and control flow: `imx_bus_probe()` allocates state, obtains the bus clock, loads the OPP table, fills a devfreq profile with `target`, `get_cur_freq`, `exit`, and initial clock rate, registers a userspace-governed devfreq device, and optionally calls `imx_bus_init_icc()`. `imx_bus_target()` chooses a recommended OPP and applies it with `dev_pm_opp_set_rate()`. `imx_bus_get_cur_freq()` reports `clk_get_rate()`. Exit removes the OPP table and unregisters the optional interconnect child.

State and persistence behavior: state is a profile, devfreq pointer, clock, and optional interconnect platform device. OPP state is loaded from DT and removed in profile exit or probe error.

Dependencies and integration points: depends on clk, OPP, devfreq userspace governor, OF compatibles for i.MX8M NoC/NIC variants, and optional `CONFIG_INTERCONNECT_IMX` provider names supplied through match data.

Risks and test signals: the clock is intentionally not enabled, relying on safe `clk_set_rate()` while disabled. `imx_bus_init_icc()` logs but returns success for unknown interconnect driver match data, so missing ICC providers can be easy to miss. Test signals include OPP rate changes through userspace `set_freq`, current frequency reporting, disabled-clock rate programming, OPP-table cleanup on failure, ICC child creation when `#interconnect-cells` is present, and no crash when interconnect support is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/imx-bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/imx8m-ddrc.c -->
# sources/distributed-fs/ceph-client/drivers/devfreq/imx8m-ddrc.c

Purpose: i.MX8M DDR controller devfreq driver. It uses NXP firmware SMC calls for DDR DVFS while keeping the Linux clock tree aligned with firmware-selected clock parents and rates.

Important APIs and control flow: probe queries firmware for supported frequency count and per-index metadata, gets DRAM core/pll/alt/apb clocks, loads DT OPPs, disables OPPs not reported by firmware, and registers a userspace-governed devfreq profile. `imx8m_ddrc_target()` resolves a requested OPP, skips no-op transitions, finds matching firmware frequency info, calls `imx8m_ddrc_set_freq()`, then verifies the resulting core clock. `imx8m_ddrc_set_freq()` obtains new mux parents by firmware-provided indexes, prepares/enables them, calls `imx8m_ddrc_smc_set_freq()`, updates Linux clock parents, refreshes the PLL rate, and drops temporary references. The SMC helper disables local IRQs and passes an online CPU mask encoded by CPU index.

State and persistence behavior: per-device state stores the devfreq profile/device, four clocks, firmware frequency count, and up to four firmware frequency descriptors. OPPs come from DT but are pruned dynamically according to firmware support.

Dependencies and integration points: depends on ARM SMCCC SIP service `0xc2000004`, clk provider internals for parent-by-index lookup, devfreq/OPP/userspace governor, and compatible `fsl,imx8m-ddrc`.

Risks and test signals: firmware-reported clock parent indexes must match Linux clock parent ordering; SMC failures are not directly reported by the firmware call wrapper; CPU mask encoding assumes CPU numbers fit byte slots in a 32-bit value; `clk_prepare_enable(NULL)` relies on common clock tolerance for optional parents. Test signals include firmware frequency enumeration, unsupported DT OPP disabling, successful high/low DDR transitions, clock parent/rate consistency after SMC, local IRQ-disabled switching behavior, and rejection of invalid firmware parent indexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/imx8m-ddrc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/mtk-cci-devfreq.c -->
# sources/distributed-fs/ceph-client/drivers/devfreq/mtk-cci-devfreq.c

Purpose: MediaTek CCI devfreq driver that follows CPUFreq through the passive governor and changes CCI PLL frequency with coordinated processor/SRAM regulator voltage tracking.

Important APIs and control flow: probe obtains CCI and intermediate clocks, optional `proc` and `sram` regulators, enables supplies and CCI clock, loads OPPs, determines intermediate voltage, raises to the highest OPP voltage, registers a passive devfreq device with `CPUFREQ_PARENT_DEV`, and registers an OPP voltage-change notifier. `mtk_ccifreq_target()` resolves an OPP, computes target voltage, scales voltage up before frequency increases, reparents CCI to the intermediate clock, changes the original PLL rate, reparents back, and scales voltage down when safe. `mtk_ccifreq_set_voltage()` enforces proc/SRAM voltage delta constraints iteratively according to SoC data. The OPP notifier adjusts voltage immediately when the current OPP voltage changes.

State and persistence behavior: per-device state includes devfreq pointer, regulators, CCI/intermediate clocks, intermediate voltage, previous frequency, regulator mutex, OPP notifier, SoC voltage constraints, and retry limit. Resources are manually disabled/removed in remove and probe-error paths.

Dependencies and integration points: depends on passive governor, CPUFreq parent support, OPP/regulator/clock frameworks, MediaTek DT compatibles `mediatek,mt8183-cci` and `mediatek,mt8186-cci`, and SoC-specific voltage tracking constants.

Risks and test signals: no profile `get_cur_freq` means core state relies on target history. Error paths before `devm_devfreq_add_device()` must disable regulators/clocks exactly once. Voltage rollback cannot recover all partial hardware states if reparenting back fails. Passive CPUFreq interpolation depends on CPU OPP/topology. Test signals include regulator delta tracking in both scale directions, reparenting to/from intermediate clock, current-voltage OPP notifier behavior, CPUFreq-driven passive updates, optional SRAM regulator absence on MT8183, and remove cleanup with supplies disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/mtk-cci-devfreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/rk3399_dmc.c -->
# sources/distributed-fs/ceph-client/drivers/devfreq/rk3399_dmc.c

Purpose: Rockchip RK3399 DMC devfreq driver. It scales DDR frequency and center voltage using simple-ondemand decisions driven by a Rockchip DFI devfreq-event provider, and programs DDR power-down/ODT timings through Trusted Firmware SMC calls.

Important APIs and control flow: probe obtains `center` regulator, `dmc_clk`, DFI event provider, enables events, reads optional timing properties, reads DDR type and ODT disable frequency from PMU GRF when present, initializes firmware DRAM config, loads OPPs, gets current rate/voltage, registers a simple-ondemand devfreq profile, and registers an OPP notifier. `rk3399_dmcfreq_target()` selects target OPP, blocks Rockchip PMU power-domain transitions, computes idle/ODT arguments from target DDR controller MHz, sends SMC timing updates, raises voltage before scaling up, calls `clk_set_rate()`, verifies the actual clock, scales voltage down after scaling down, updates cached rate/voltage, and unblocks PMU. Status reads DFI event counts. Suspend disables the event provider and suspends devfreq; resume re-enables both.

State and persistence behavior: per-device state includes devfreq profile/device, simple-ondemand data, DMC clock, event provider, mutex, center regulator, PMU regmap, cached current and target rate/voltage, and DT timing thresholds. Event provider state persists separately in `rockchip-dfi.c`.

Dependencies and integration points: depends on devfreq core/simple-ondemand, devfreq-event DFI provider, OPP/regulator/clock, Rockchip PM domains, syscon GRF, SMCCC Rockchip SIP, and compatible `rockchip,rk3399-dmc`.

Risks and test signals: `rk3399_dmcfreq_of_props()` ORs optional property failures and the return is ignored, so missing timing properties become zero values. If `devfreq_suspend_device()` fails after event disable, resume expectations can be uneven. Voltage rollback after failed clock set assumes cached voltage is still valid. Test signals include DFI event deferral and enable/disable balance, DDR type-specific ODT thresholds, SMC timing arguments, PMU block/unblock pairing, clock-rate verification, voltage sequencing on up/down transitions, suspend/resume, and simple-ondemand response to memory traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/rk3399_dmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/sun8i-a33-mbus.c -->
# sources/distributed-fs/ceph-client/drivers/devfreq/sun8i-a33-mbus.c

Purpose: Allwinner sun8i/sun50i MBUS/DRAM devfreq driver. It performs DRAM frequency switching through MBUS MDFS registers and uses MBUS PMU peak bandwidth counters for simple-ondemand load feedback.

Important APIs and control flow: probe maps DRAM and MBUS register ranges, enables the bus clock, obtains DRAM/MBUS clocks, takes exclusive rate locks, builds dynamic OPPs from parent clock divided by allowed DRAM dividers, initializes hardware, registers a simple-ondemand devfreq device, and sets a dynamic suspend frequency. `sun8i_a33_mbus_set_dram_freq()` changes the DRAM clock rate, disables self-refresh/VTF, configures MDFS double-buffering, updates refresh timing, toggles ODT based on frequency and saved ODT map, starts MDFS, polls completion, restores VTF/self-refresh, restarts PMU counters, and updates nominal bandwidth. `sun8i_a33_mbus_get_dram_status()` reports peak PMU bandwidth as busy time and nominal bandwidth as total time.

State and persistence behavior: per-device state stores variant limits, MMIO bases, clocks, devfreq pointer, governor/profile data, DRAM data width, nominal bandwidth, saved ODT map, refresh timings, and flexible-array frequency table. Dynamic OPPs and devfreq state persist until remove, which restores the initial DRAM frequency.

Dependencies and integration points: depends on devfreq simple-ondemand, dynamic OPP helpers, clk exclusive-rate APIs, IO polling, platform named resources `dram` and `mbus`, module parameter `pmu_period`, and compatibles `allwinner,sun50i-a64-mbus` and `allwinner,sun50i-h5-mbus`.

Risks and test signals: PMU period is a module parameter with no range validation; bad values can program invalid periods or skew utilization. Frequency switching touches refresh, ODT, self-refresh, and VTF registers directly, so failures can affect memory stability. `data_width` can become zero if no DX lane is enabled. Test signals include dynamic OPP table contents, MDFS completion polling, refresh timing values by DRAM type, ODT enable threshold, PMU bandwidth under load, suspend clock gating, removal restoring initial frequency, and behavior with edge `pmu_period` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/sun8i-a33-mbus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/tegra30-devfreq.c -->
# sources/distributed-fs/ceph-client/drivers/devfreq/tegra30-devfreq.c

Purpose: NVIDIA Tegra30/114/124 ACTMON devfreq driver. It registers an interrupt-driven immutable `tegra_actmon` governor that scales EMC memory frequency from ACTMON memory-access counters, watermarks, and CPU frequency contribution.

Important APIs and control flow: probe maps ACTMON registers, obtains reset/ACTMON/EMC clocks, requests a threaded IRQ with `IRQ_NOAUTOEN`, configures OPP supported-hardware filtering and custom clock config that skips OPP clock programming, resets/enables ACTMON hardware, discovers max EMC rate, initializes MCALL/MCCPU monitor devices, registers the governor, and registers a devfreq device. `tegra_actmon_configure_device()` initializes average counts, watermarks, count weights, interrupt status, and control bits. The threaded ISR handles device watermark interrupts, updates boost frequency and watermarks, clears interrupts, and calls `update_devfreq()`. The custom governor updates stats, computes target frequency from both ACTMON devices, adds boost and optional static CPU-to-EMC contribution, converts kHz to Hz, and handles start/stop/update-interval/suspend/resume by coordinating devfreq monitoring, ACTMON IRQs, clock notifiers, and CPUFreq notifiers.

State and persistence behavior: per-driver state includes devfreq pointer, reset/clock/MMIO resources, EMC clock/max/current kHz, clock and CPUFreq notifiers, delayed CPU update work, two ACTMON device states with avg/boost/target kHz, IRQ number, started flag, and SoC config. Boost frequency persists while the governor is started and resets on restart. OPP and cooling state are owned by devfreq/OPP core.

Dependencies and integration points: depends on devfreq core/governor API, CPUFreq notifications, clock notifiers, reset controller, OPP supported-hw based on Tegra fuse speedo ID, thermal cooling via `is_cooling_device`, threaded IRQs, and OF compatibles `nvidia,tegra30-actmon`, `nvidia,tegra114-actmon`, and `nvidia,tegra124-actmon`.

Risks and test signals: file-scope `tegra_devfreq_profile` and `tegra_devfreq_governor` are shared objects, which is risky if multiple ACTMON instances were ever probed. The governor is marked IRQ-driven but also starts core monitoring. CPUFreq notifier uses `mutex_trylock()` and delayed work, so CPU contribution updates are intentionally eventual. Polling interval updates must stay <= 256 ms to fit hardware. Test signals include ACTMON IRQ enable/disable balance, watermark programming after EMC clock changes, CPUFreq contribution changes, boost up/down hysteresis, OPP target selection without duplicate clock programming, suspend/resume restart, thermal cooling registration, and supported-hardware OPP filtering by speedo ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/tegra30-devfreq.c -->
