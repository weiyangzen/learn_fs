# subset-b-005441 Research

Grouped source research for Linux thermal framework helpers, DT/sysfs/netlink/trace surfaces, TI SoC and UniPhier thermal drivers, and early Thunderbolt/USB4 ACPI/capability/CLx support. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/thermal/thermal_debugfs.h

## Purpose
`thermal_debugfs.h` is the thermal core's debugfs abstraction header. It lets core code call debug lifecycle, trip, and cooling-device instrumentation unconditionally while compiling to no-ops when `CONFIG_THERMAL_DEBUGFS` is disabled.

## Important APIs, Types, and Functions
The enabled declarations cover `thermal_debug_init`, cooling-device add/remove/state update hooks, thermal-zone add/remove/resume hooks, trip up/down hooks, and `thermal_debug_update_trip_stats`. The disabled path provides matching `static inline` stubs.

## Control Flow
There is no executable flow in the header beyond compile-time selection. Thermal registration, trip crossing, resume, and cdev update paths call these hooks; the implementation file owns the debugfs directories and statistics when enabled.

## State and Persistence Behavior
This header owns no state. With debugfs enabled, the paired implementation persists in-memory debug statistics and debugfs entries for the lifetime of thermal zones and cooling devices; with the stubs there is no runtime effect.

## Dependencies and Integration Points
It depends on `struct thermal_zone_device`, `struct thermal_cooling_device`, and `struct thermal_trip` declarations from the thermal core. Integration is internal to thermal core event paths and complements netlink and trace notifications.

## Risks and Edge Cases
The risk is API drift between enabled declarations and disabled stubs; mismatched signatures would break builds only in one configuration. Debug hooks must also avoid changing core behavior, because callers ignore return values.

## Test Signals
Build with and without `CONFIG_THERMAL_DEBUGFS`; exercise zone/cdev registration and trip crossings; inspect debugfs entries in enabled builds; verify no undefined references or side effects in disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_helpers.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/thermal_helpers.c

## Purpose
`thermal_helpers.c` contains shared thermal-core helper logic for trend detection, temperature reads, cooling-device target aggregation, and thermal-zone parameter accessors.

## Important APIs, Types, and Functions
Key APIs are `get_tz_trend`, `thermal_trip_is_bound_to_cdev`, `__thermal_zone_get_temp`, `thermal_zone_get_temp`, `thermal_cdev_update`, `thermal_cdev_update_nocheck`, `thermal_zone_get_slope`, and `thermal_zone_get_offset`. Exported APIs include trip/cdev binding checks, public temperature reads, and slope/offset access.

## Control Flow
Temperature reads go through `tz->ops.get_temp` under the zone lock. If thermal emulation is active, emulated temperature replaces the hardware value only when the real value is below the critical trip, preventing emulation from hiding critical heat. Cooling updates scan all `cdev->thermal_instances`, choose the deepest non-`THERMAL_NO_TARGET` state, call the cdev `set_cur_state` operation, then notify netlink, statistics, debugfs, and trace consumers.

## State and Persistence Behavior
The file mutates no persistent storage directly, but it updates live thermal/cooling state through driver callbacks and `cdev->updated`. Emulated temperature is read from `tz->emul_temperature`; statistics and debug state are updated in other modules.

## Dependencies and Integration Points
It depends on `thermal_core.h`, `thermal_trace.h`, guard-based zone/cdev locking, trip descriptors, thermal notifiers, debugfs hooks, and cooling-device statistics. It is central glue between governors, thermal-zone drivers, and cooling-device implementations.

## Risks and Edge Cases
Incorrect locking can race with governor binding or cdev state changes. Emulation must never suppress critical readings. `thermal_zone_get_temp` converts invalid sentinel temperatures to `-ENODATA`, so callers must handle that separately from driver read failures.

## Test Signals
Unit or KUnit coverage for trend fallback, emulation below/above critical trips, invalid temperature handling, deepest-state selection across multiple instances, and notification/statistics calls after state changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/thermal_hwmon.c

## Purpose
`thermal_hwmon.c` exposes thermal zones through the hwmon sysfs ABI so userspace monitoring tools can read `tempN_input` and, when available, `tempN_crit`.

## Important APIs, Types, and Functions
Important types are `thermal_hwmon_device`, `thermal_hwmon_attr`, and `thermal_hwmon_temp`. Public APIs are `thermal_add_hwmon_sysfs`, `thermal_remove_hwmon_sysfs`, and `devm_thermal_add_hwmon_sysfs`; show callbacks read current and critical temperatures.

## Control Flow
Adding a zone first finds or creates a shared hwmon device keyed by thermal zone type with hyphens replaced by underscores. It allocates one `thermal_hwmon_temp`, names attributes using the per-type count, creates `tempN_input`, optionally creates `tempN_crit`, and links the temp entry into the hwmon list. Removal reverses file creation, list membership, and device registration when the last zone of a type disappears. The devm helper registers a cleanup action after successful setup.

## State and Persistence Behavior
The module maintains the global `thermal_hwmon_list` protected by `thermal_hwmon_list_lock`. State is in memory only and tied to thermal-zone lifetime; sysfs files persist while their zone and shared hwmon device remain registered.

## Dependencies and Integration Points
It depends on the hwmon thermal namespace, `thermal_zone_get_temp`, zone `get_crit_temp`, sysfs device files, and devres. Thermal drivers call it directly or through devm helpers after registering a zone.

## Risks and Edge Cases
Shared numbering is monotonic per hwmon device and not compacted on removal. Error unwinding must remove partially created files and unregister newly created devices. If critical temperature validity changes after registration, the `tempN_crit` attribute set will not be dynamically adjusted.

## Test Signals
Build with `CONFIG_THERMAL_HWMON`; register multiple zones of the same type; verify shared hwmon naming, temperature reads, critical attr presence, removal cleanup, and devm cleanup on probe failure/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_hwmon.h -->
# sources/distributed-fs/ceph-client/drivers/thermal/thermal_hwmon.h

## Purpose
`thermal_hwmon.h` declares the thermal-to-hwmon bridge API and provides no-op stubs when hwmon exposure is disabled.

## Important APIs, Types, and Functions
The header declares `thermal_add_hwmon_sysfs`, `devm_thermal_add_hwmon_sysfs`, and `thermal_remove_hwmon_sysfs`. Disabled builds return success for add paths and no-op for remove.

## Control Flow
There is no runtime control flow in the header. It allows thermal drivers and core registration code to call hwmon setup without open-coding config guards.

## State and Persistence Behavior
No state is owned here. Enabled builds create hwmon sysfs state in `thermal_hwmon.c`; disabled builds preserve no hwmon state.

## Dependencies and Integration Points
The header includes `<linux/thermal.h>` and is consumed by thermal core code and drivers such as the TI thermal common layer.

## Risks and Edge Cases
Callers cannot detect disabled hwmon because stubs return success. That is intentional, but tests that expect sysfs files must run under `CONFIG_THERMAL_HWMON`.

## Test Signals
Compile both config branches and verify consumers build without conditional code. In enabled builds, pair with `thermal_hwmon.c` sysfs tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_hwmon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_mmio.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/thermal_mmio.c

## Purpose
`thermal_mmio.c` is a small platform thermal driver for simple memory-mapped temperature sensors. The current match table supports Amazon Annapurna Labs compatible `"amazon,al-thermal"`.

## Important APIs, Types, and Functions
`struct thermal_mmio` stores the mapped base, read callback, mask, and scale factor. `thermal_mmio_get_temperature` implements thermal-zone `.get_temp`; `thermal_mmio_probe` maps resources, applies match-data initialization, registers a DT thermal zone, and logs the first reading. `al_thermal_init` configures byte reads, `0xff` mask, and a `1000` factor.

## Control Flow
Probe allocates driver state, maps MMIO resource 0, calls the compatible-specific initializer, registers sensor id 0 with `devm_thermal_of_zone_register`, reads the current temperature through the thermal-zone callback, and reports success. Reads mask the MMIO value and multiply by the configured factor to produce millidegrees.

## State and Persistence Behavior
Runtime state is devm-managed and lasts until device removal. There is no suspend logic or nonvolatile persistence; hardware registers remain the source of truth.

## Dependencies and Integration Points
It integrates platform devices, OF matching, resource-managed ioremap, thermal OF zones, and the generic thermal framework. The DT thermal zone supplies trips/polling/cooling maps.

## Risks and Edge Cases
The generic math assumes raw code times factor is a valid millidegree value; additional compatibles must supply correct masks and scaling. There is no range checking, sign handling, or multi-register support.

## Test Signals
DT binding/probe smoke tests, ioremap failure paths, thermal zone registration, `temp` sysfs read returning raw byte times 1000, and future compatible tests for non-byte sensors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_mmio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_netlink.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/thermal_netlink.c

## Purpose
`thermal_netlink.c` implements the thermal framework's generic-netlink family for event multicast, sampling multicast, and request/reply commands exposing zones, trips, governors, cooling devices, CPU capabilities, and user thresholds.

## Important APIs, Types, and Functions
Important state includes `thermal_genl_family`, `thermal_genl_policy`, multicast groups, `struct param`, `event_cb`, `cmd_cb`, and `thermal_genl_chain`. Public APIs include `thermal_notify_tz_*`, `thermal_notify_cdev_*`, `thermal_notify_threshold_*`, `thermal_genl_sampling_temp`, `thermal_genl_cpu_capability_event`, notifier register/unregister, and init/exit.

## Control Flow
Sampling sends a `THERMAL_GENL_SAMPLING_TEMP` multicast only if listeners exist. Event helpers fill `struct param` and call `thermal_genl_send_event`, which allocates a skb, emits a generic-netlink header, runs the event encoder, ends the message, and multicasts to the event group. Command paths allocate reply messages for `doit` or write into dump skbs for `dumpit`, dispatch through `cmd_cb`, and encode nested zone/cdev/trip/threshold data. Threshold mutation commands require `CAP_SYS_ADMIN` and hold the target zone lock before changing the threshold list.

## State and Persistence Behavior
The netlink family is registered at thermal init and unregistered at exit. Listener bind/unbind is broadcast through a blocking notifier chain. The module does not persist data itself; it snapshots live thermal core state and mutates only user threshold lists via thermal threshold helpers.

## Dependencies and Integration Points
It depends on `<uapi/linux/thermal.h>`, generic netlink, capability checks, notifier chains, thermal zone/cdev iterators, `thermal_zone_get_temp`, `thermal_zone_trip_id`, and `thermal_thresholds_*`. It is the userspace ABI counterpart to sysfs and tracepoints.

## Risks and Edge Cases
Many commands use relaxed validation flags, so policy coverage and explicit attribute checks are important. Encoders return `-EMSGSIZE` on nested attribute failure; missing `nla_nest_cancel` on some command error paths is a common audit point. Event array indexing assumes valid enum values from internal callers.

## Test Signals
Generic-netlink family registration tests, listener/no-listener multicast behavior, `genl` dump/get commands for zones and cdevs, capability enforcement for threshold add/delete/flush, malformed attribute tests, and crossing thresholds to observe up/down events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_netlink.h -->
# sources/distributed-fs/ceph-client/drivers/thermal/thermal_netlink.h

## Purpose
`thermal_netlink.h` is the internal declaration and stub layer for thermal generic-netlink notifications and control.

## Important APIs, Types, and Functions
It defines `struct thermal_genl_cpu_caps`, multicast group enum values, notifier action constants, `struct thermal_genl_notify`, and all notification/init/notifier prototypes. Disabled builds return zero for every notification/control helper and no-op exit.

## Control Flow
The header has no runtime flow. It allows thermal core code to issue netlink notifications and sampling messages without config-specific branches.

## State and Persistence Behavior
No state is stored here. Enabled builds use `thermal_netlink.c` to maintain the netlink family and listener notifier chain; disabled builds drop all events.

## Dependencies and Integration Points
It forward-declares thermal zone, trip, and cooling-device types, and is included by the thermal core, helpers, and threshold code.

## Risks and Edge Cases
Because disabled stubs return success, callers cannot treat a zero return as proof that userspace saw an event. API drift between stubs and implementation is the key build risk.

## Test Signals
Compile with `CONFIG_THERMAL_NETLINK=y` and unset; verify all call sites build; in enabled builds, pair with netlink event/command tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_of.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/thermal_of.c

## Purpose
`thermal_of.c` parses Device Tree thermal-zone descriptions and registers thermal zones tied to sensor devices through resource-managed helpers.

## Important APIs, Types, and Functions
Important helpers parse trip types/properties, locate the thermal zone that references a sensor phandle/id, read polling delays and zone parameters, match cooling maps, and register/unregister OF-backed zones. Public APIs are `devm_thermal_of_zone_register` and `devm_thermal_of_zone_unregister`.

## Control Flow
Registration finds the `thermal-zones` child that references the caller's sensor and id, allocates trip descriptors from the `trips` subnode, reads polling delay properties, initializes `thermal_zone_params` from `sustainable-power` and `coefficients`, installs OF `should_bind`, optionally maps `critical-action` to reboot/shutdown callbacks, registers with trips, frees temporary trip storage, and enables the zone. Cooling binding later resolves the zone by name, walks `cooling-maps`, matches the trip phandle and cdev OF node, and returns lower/upper state limits plus contribution weight.

## State and Persistence Behavior
Device nodes are reference-counted and trips are copied into thermal-core state. Devres owns the registration cleanup; unregister disables and unregisters the zone. No file-backed persistence exists.

## Dependencies and Integration Points
It depends on OF phandle parsing, thermal core registration with trips, thermal zone params, cooling-device maps, and critical reboot/shutdown helpers. Platform sensor drivers call it after setting their `.get_temp` operations.

## Risks and Edge Cases
Malformed DT can fail registration through missing `temperature`, `hysteresis`, `type`, `thermal-sensors`, or cooling cells. The framework currently treats coefficients as slope/offset for one sensor, so multi-sensor zone modeling is limited.

## Test Signals
DT schema/probe tests for valid and malformed thermal zones, cooling-map binding tests, critical-action behavior, trip sysfs visibility after registration, and devm unregister on probe failure/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_of.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/thermal_sysfs.c

## Purpose
`thermal_sysfs.c` builds the thermal framework sysfs ABI for thermal zones, trips, cooling devices, cooling statistics, and thermal-instance binding attributes.

## Important APIs, Types, and Functions
Zone attributes include `type`, `temp`, `mode`, `policy`, `available_policies`, `sustainable_power`, PID coefficients, slope/offset, optional `emul_temp`, and generated trip attributes. Cooling attributes include `type`, `max_state`, `cur_state`, optional `stats/*`, `trip_point`, and `weight`. Public setup/teardown APIs are `thermal_zone_create_device_groups`, `thermal_zone_destroy_device_groups`, `thermal_cooling_device_setup_sysfs`, `thermal_cooling_device_destroy_sysfs`, `thermal_cooling_device_stats_update`, and `thermal_cooling_device_stats_reinit`.

## Control Flow
Zone stores parse user input, validate it under zone locking, call driver callbacks where present, update thermal-core trip state, and trigger zone updates. `create_trip_attrs` allocates `3 * num_trips + 1` attributes and assigns names/modes based on trip flags. Cooling `cur_state_store` validates requested state, calls the cdev operation under cdev locking, and updates statistics. Statistics track time in state and transitions under a spinlock and render a transition matrix bounded by `PAGE_SIZE`.

## State and Persistence Behavior
Sysfs groups are allocated per device and freed at teardown. Cooling statistics are in-memory state attached to `cdev->stats`; reset clears counters and timestamps. Zone parameter writes mutate live `tz->tzp` values only.

## Dependencies and Integration Points
It depends on thermal core locks, governors, trips, cdev operations, jiffies/ktime, sysfs attribute groups, optional thermal emulation, and optional statistics config.

## Risks and Edge Cases
Trip writes must avoid integer overflow around `THERMAL_TEMP_INVALID`. Transition tables can exceed one page and return `-EFBIG`. `cur_state_store` updates stats but does not send netlink/debug notifications, unlike helper-driven cdev updates.

## Test Signals
Sysfs read/write tests for all zone attributes, trip temperature/hysteresis validation, policy changes, emulation behavior, cooling state bounds, stats reset/time accumulation, and large transition table handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_thresholds.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/thermal_thresholds.c

## Purpose
`thermal_thresholds.c` implements user-defined thermal threshold lists used to request netlink notifications and update thermal trip windows when temperatures cross arbitrary user thresholds.

## Important APIs, Types, and Functions
The public API includes `thermal_thresholds_init`, `thermal_thresholds_flush`, `thermal_thresholds_exit`, `thermal_thresholds_handle`, `thermal_thresholds_add`, `thermal_thresholds_delete`, and `thermal_thresholds_for_each`. Internal helpers sort, find, evaluate raising/dropping crossings, and calculate next low/high boundaries.

## Control Flow
Initialization prepares `tz->user_thresholds`. Add either creates a sorted `user_threshold` entry or ORs an additional direction into an existing temperature. Delete removes a direction or frees the entry. Handle first updates low/high boundaries for hardware trip programming, then compares current and last temperatures to send up/down notifications only when a threshold was actually crossed.

## State and Persistence Behavior
Thresholds are heap-allocated list entries attached to the thermal zone and protected by the zone lock. They persist until explicit delete/flush or zone exit; there is no storage across reboot or driver removal.

## Dependencies and Integration Points
It depends on `thermal_core.h`, list sorting, netlink threshold notifications, and `__thermal_zone_device_update` reasons. Netlink command handlers are the main userspace mutation path.

## Risks and Edge Cases
Direction bitmasks must be validated by callers; this code accepts and stores the provided direction bits. Crossing detection needs a valid previous temperature and intentionally skips first samples and stable readings.

## Test Signals
Add/delete duplicate tests, sorted iteration, direction merge/split behavior, flush cleanup, first-sample no-event behavior, raising/dropping crossing notifications, and low/high boundary selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_thresholds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_thresholds.h -->
# sources/distributed-fs/ceph-client/drivers/thermal/thermal_thresholds.h

## Purpose
`thermal_thresholds.h` declares the user-threshold data structure and internal thermal core threshold API.

## Important APIs, Types, and Functions
`struct user_threshold` stores a list node, temperature, and direction bitmask. Prototypes cover lifecycle, handling, mutation, and iteration.

## Control Flow
There is no executable control flow in the header. It defines the contract used by netlink command handlers and thermal zone update code.

## State and Persistence Behavior
The header defines the per-threshold state shape; instances are owned by `thermal_thresholds.c` on each zone's `user_thresholds` list.

## Dependencies and Integration Points
It expects `struct thermal_zone_device` and `struct list_head` visibility from including context, normally via thermal core headers.

## Risks and Edge Cases
Because `direction` is a plain `int`, callers must pass valid `THERMAL_THRESHOLD_WAY_*` bits. API changes must be coordinated with netlink threshold command encoding.

## Test Signals
Compile coverage and the behavioral tests listed for `thermal_thresholds.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_thresholds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_trace.h -->
# sources/distributed-fs/ceph-client/drivers/thermal/thermal_trace.h

## Purpose
`thermal_trace.h` defines ftrace tracepoints for generic thermal-zone temperature updates, trip events, cooling-device updates, and CPU/devfreq power cooling activity.

## Important APIs, Types, and Functions
Trace events include `thermal_temperature`, `cdev_update`, `thermal_zone_trip`, `thermal_power_cpu_get_power_simple`, `thermal_power_cpu_limit`, `thermal_power_devfreq_get_power`, and `thermal_power_devfreq_limit`. It maps trip enum values to symbolic names with `TRACE_DEFINE_ENUM` and `show_tzt_type`.

## Control Flow
The file is declarative tracepoint metadata. Runtime callers invoke generated `trace_*` functions, which collect fields such as zone type/id, current/previous temperature, trip id/type, cdev target, CPU masks, frequencies, loads, and power values.

## State and Persistence Behavior
Tracepoints do not persist state in this file; they emit records to ftrace/perf buffers when enabled. Generated code is included through `trace/define_trace.h`.

## Dependencies and Integration Points
It depends on `linux/tracepoint.h`, `linux/thermal.h`, optional CPU thermal and devfreq thermal configs, and `thermal_core.h`. Thermal helpers and governors use these tracepoints for observability.

## Risks and Edge Cases
Trace ABI field names are consumed by tooling. CPU/devfreq events must remain behind the right config guards to avoid type visibility issues. Load calculation avoids divide-by-zero when total time is zero.

## Test Signals
Build with CPU/devfreq thermal enabled/disabled, enable trace events under tracing, drive thermal updates and cooling limits, and validate expected field values in trace output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_trace_ipa.h -->
# sources/distributed-fs/ceph-client/drivers/thermal/thermal_trace_ipa.h

## Purpose
`thermal_trace_ipa.h` defines tracepoints for the intelligent power allocator governor, capturing aggregate power allocation, per-actor grants, and PID controller terms.

## Important APIs, Types, and Functions
Trace events are `thermal_power_allocator`, `thermal_power_actor`, and `thermal_power_allocator_pid`. They record zone id, requested and granted power, actor counts, available power range, current temperature, delta temperature, PID error, integral, p/i/d terms, and output.

## Control Flow
The header declares trace metadata only. The power allocator governor emits generated `trace_thermal_power_*` calls during control-loop computation and actor allocation.

## State and Persistence Behavior
No persistent state is owned. Records appear in trace buffers only while tracing is active.

## Dependencies and Integration Points
It depends on tracepoint infrastructure and `thermal_core.h`; it is included by the power allocator governor to expose tuning and debugging signals.

## Risks and Edge Cases
Field type choices are ABI-visible to trace tooling. PID values use signed 64-bit fields for intermediate terms, which helps avoid truncation in diagnostics.

## Test Signals
Build the power allocator governor, enable `thermal_power_allocator*` trace events, force governor updates, and check aggregate power, actor grants, and PID terms for consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_trace_ipa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_trip.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/thermal_trip.c

## Purpose
`thermal_trip.c` centralizes thermal trip helper functions: type names, trip iteration, hardware trip-window programming, and trip-id derivation.

## Important APIs, Types, and Functions
Public APIs are `thermal_trip_type_name`, `for_each_thermal_trip`, `thermal_zone_for_each_trip`, `thermal_zone_set_trips`, and `thermal_zone_trip_id`.

## Control Flow
Trip iteration walks thermal trip descriptors and stops on the first callback error. The public locked iterator acquires the thermal-zone guard before delegating. `thermal_zone_set_trips` skips work if the driver lacks `.set_trips` or the low/high window is unchanged; otherwise it stores previous bounds and calls the driver.

## State and Persistence Behavior
The file mutates `tz->prev_low_trip` and `tz->prev_high_trip` to avoid redundant hardware programming. Other state lives in thermal zone trip arrays.

## Dependencies and Integration Points
It depends on `thermal_core.h`, trip descriptor layout, thermal-zone locking, and driver `.set_trips` callbacks. Netlink and sysfs use trip ids and names.

## Risks and Edge Cases
`thermal_zone_trip_id` assumes the trip pointer belongs to `tz->trips`; invalid pointers would compute meaningless ids. Hardware `set_trips` failures are logged but not propagated.

## Test Signals
Trip type name bounds tests, callback early-exit tests, locked iteration tests, duplicate set-trip skip tests, and driver failure logging coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_trip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/Kconfig

## Purpose
This Kconfig file controls build-time selection for the Texas Instruments SoC bandgap thermal driver and per-family support.

## Important APIs, Types, and Functions
Symbols are `TI_SOC_THERMAL`, `TI_THERMAL`, `OMAP3_THERMAL`, `OMAP4_THERMAL`, `OMAP5_THERMAL`, and `DRA752_THERMAL`. Family symbols depend on `TI_SOC_THERMAL` plus architecture or `COMPILE_TEST`.

## Control Flow
There is no runtime flow. User-selected symbols determine whether the core driver, generic thermal framework bridge, and per-SoC data files are compiled.

## State and Persistence Behavior
No runtime state. Kconfig choices persist in kernel configuration and drive object composition.

## Dependencies and Integration Points
The symbols feed `ti-soc-thermal/Makefile` and conditional externs in `ti-bandgap.h`. `TI_THERMAL` enables thermal-zone exposure and CPU cooling integration.

## Risks and Edge Cases
Selecting a family without matching data would produce null match data or missing objects, so symbol dependencies must stay aligned with OF match entries and Makefile fragments. OMAP3 help text warns about unreliable sensors.

## Test Signals
Kernel allmodconfig/allyesconfig and COMPILE_TEST builds for each family, plus DT probe tests for enabled compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/Makefile -->
# sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/Makefile

## Purpose
The Makefile composes the `ti-soc-thermal` object from the shared bandgap driver, optional thermal framework bridge, and selected per-SoC data tables.

## Important APIs, Types, and Functions
`obj-$(CONFIG_TI_SOC_THERMAL)` builds `ti-soc-thermal.o`. Component objects are `ti-bandgap.o`, optional `ti-thermal-common.o`, and per-family data objects for DRA752, OMAP3, OMAP4, and OMAP5.

## Control Flow
Build-system control flow is entirely Kconfig driven. The runtime OF match table in `ti-bandgap.c` references only data symbols whose configs are enabled.

## State and Persistence Behavior
No runtime state is owned by the Makefile. The built module or built-in object persists according to kernel build configuration.

## Dependencies and Integration Points
It is tightly coupled to `Kconfig` and conditional extern macros in `ti-bandgap.h`.

## Risks and Edge Cases
Missing an object for an enabled compatible would fail link or probe. Enabling `TI_SOC_THERMAL` without `TI_THERMAL` builds hardware support without thermal-zone exposure callbacks.

## Test Signals
Build matrix across `TI_THERMAL` and each family symbol; verify link coverage for all OF match data references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/dra752-bandgap.h -->
# sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/dra752-bandgap.h

## Purpose
`dra752-bandgap.h` defines DRA752-specific bandgap register offsets, bit masks, ADC conversion range, clock limits, and alert threshold constants.

## Important APIs, Types, and Functions
The file declares macros for two common control/status register groups, five sensor domains (`core`, `iva`, `mpu`, `dspeve`, `gpu`), temperature sensor fields, alert threshold masks, ADC start/end values `540..945`, and per-domain hot/cold thresholds and min/max clock rates.

## Control Flow
There is no executable control flow. `dra752-thermal-data.c` consumes these constants to populate `temp_sensor_registers`, `temp_sensor_data`, and `ti_bandgap_data`.

## State and Persistence Behavior
No state is stored. The macros describe hardware layout and default programming values.

## Dependencies and Integration Points
It depends on `BIT`/`GENMASK` style bit definitions through including context and integrates with the generic TI bandgap structures.

## Risks and Edge Cases
Wrong offsets or masks can program the wrong DRA752 domain or fail to clear/freeze alert state. DRA752 uses split control/status blocks, so copying masks between domains is particularly risky.

## Test Signals
Compile with `CONFIG_DRA752_THERMAL`, probe on DRA7 hardware or emulation, verify each domain reports plausible temperatures and hot/cold alert bits map correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/dra752-bandgap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/dra752-thermal-data.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/dra752-thermal-data.c

## Purpose
`dra752-thermal-data.c` instantiates the static TI bandgap configuration for DRA752, covering five sensors and the ADC-to-temperature conversion table.

## Important APIs, Types, and Functions
It defines `temp_sensor_registers` for core, IVA, MPU, DSPEVE, and GPU; `temp_sensor_data` thresholds/clock limits for each; the `dra752_adc_to_temp` table; and exported `const struct ti_bandgap_data dra752_data`.

## Control Flow
No functions execute here. At probe, `ti-bandgap.c` selects `dra752_data` through OF match, iterates the five sensors, checks efuses, programs alert thresholds, exposes thermal zones, and uses this file's conversion table when reading temperatures.

## State and Persistence Behavior
All objects are static configuration. Runtime state is created in `ti_bandgap` and per-zone thermal data, not in this file.

## Dependencies and Integration Points
It depends on `ti-thermal.h`, `ti-bandgap.h`, and `dra752-bandgap.h`. The CPU sensor registers cpufreq cooling callbacks; all domains use DRA752 PCB gradient constants.

## Risks and Edge Cases
The shared conversion table and `ERRATA_814` feature mean read correctness depends on the triple-read workaround in `ti-bandgap.c`. Register maps span two control/status regions; wrong domain mapping could silently report or alert on the wrong block.

## Test Signals
DRA752 build/probe tests, five thermal zone registrations, CPU cooling registration for MPU, ADC table bounds tests, alert IRQ tests for each status block, and errata read-path coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/dra752-thermal-data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/omap3-thermal-data.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/omap3-thermal-data.c

## Purpose
`omap3-thermal-data.c` provides OMAP34xx and OMAP36xx one-sensor bandgap configurations and conversion tables.

## Important APIs, Types, and Functions
It defines MPU `temp_sensor_registers`, sensor data with fixed 32768 Hz clock limits, ADC-to-mCelsius tables for OMAP34xx and OMAP36xx, and exported `omap34xx_data` and `omap36xx_data`.

## Control Flow
The data is consumed by `ti-bandgap.c` probe through OF matching. These SoCs are marked `TI_BANDGAP_FEATURE_CLK_CTRL | TI_BANDGAP_FEATURE_UNRELIABLE`, so runtime flow warns about unreliable readings, manages the clock, exposes one CPU thermal zone, and uses single-read conversion when reading temperature.

## State and Persistence Behavior
Static tables and descriptors only. Runtime sensor data is held in `ti_bandgap->regval[id].data` by the common thermal bridge.

## Dependencies and Integration Points
It depends on `ti-thermal.h` and `ti-bandgap.h`; thermal exposure uses `ti_thermal_expose_sensor` and removal uses `ti_thermal_remove_sensor`.

## Risks and Edge Cases
The comments explicitly warn that OMAP3 sensors are inaccurate and poorly placed. The conversion tables clamp high ADC values to 125 C, so policy decisions need conservative interpretation.

## Test Signals
Compile with `CONFIG_OMAP3_THERMAL`, OF match for OMAP34xx/36xx, single-zone registration, temperature read conversion, and warning visibility for unreliable sensors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/omap3-thermal-data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/omap4-thermal-data.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/omap4-thermal-data.c

## Purpose
`omap4-thermal-data.c` supplies OMAP4430, OMAP4460, and OMAP4470 bandgap configurations for a single MPU/CPU thermal sensor.

## Important APIs, Types, and Functions
The file defines register descriptors, threshold/clock data, conversion tables, and exported `omap4430_data`, `omap4460_data`, and `omap4470_data`. OMAP4460/4470 include TALERT, TSHUT, counter, mode, power-switch, and clock-control features.

## Control Flow
No functions run here. Probe selects the matching `ti_bandgap_data`, configures clocks and thresholds, registers CPU cooling where configured, exposes the CPU thermal zone, and reports TALERT events through `ti_thermal_report_sensor_temperature`.

## State and Persistence Behavior
Static descriptors and conversion tables only. Runtime state is stored by the bandgap and thermal common layers.

## Dependencies and Integration Points
It depends on `omap4xxx-bandgap.h`, `ti-bandgap.h`, and `ti-thermal.h`. CPU cooling uses `ti_thermal_register_cpu_cooling` and unregister counterpart.

## Risks and Edge Cases
OMAP4430 is continuous-mode-only and lacks the richer alert/shutdown programming used by OMAP4460/4470. ADC range differences must stay aligned with table sizes and conversion bounds.

## Test Signals
Build/probe each compatible, verify CPU zone and cpufreq cooling registration, TALERT/TSHUT behavior on OMAP4460/4470, and ADC conversion near table boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/omap4-thermal-data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/omap4xxx-bandgap.h -->
# sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/omap4xxx-bandgap.h

## Purpose
`omap4xxx-bandgap.h` defines register offsets, bitfields, ADC limits, clock limits, and threshold codes for OMAP4430 and OMAP4460/4470 bandgap sensors.

## Important APIs, Types, and Functions
Macros cover OMAP4430 fuse/temp sensor offsets, continuous mode, SOC/EOCZ/DTEMP bits, ADC range `13..107`, fixed 32768 Hz clock, and OMAP4460 control/counter/threshold/TSHUT/status offsets, 10-bit DTEMP, ADC range `530..932`, 1-1.5 MHz clock range, and default hot/cold/shutdown codes.

## Control Flow
There is no executable flow. `omap4-thermal-data.c` maps these macros into the generic TI bandgap structures.

## State and Persistence Behavior
No state is owned; the file is compile-time hardware description.

## Dependencies and Integration Points
It integrates with `ti-bandgap.h` through `temp_sensor_registers` initialization and with OMAP4 Kconfig selection.

## Risks and Edge Cases
OMAP4430 and OMAP4460 use different ADC widths and register blocks. Reusing constants across variants without checking feature differences can corrupt programming or conversion.

## Test Signals
Compile OMAP4 support, validate register programming on 4430 and 4460/4470 hardware, and verify threshold codes correspond to expected millidegree trip behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/omap4xxx-bandgap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/omap5-thermal-data.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/omap5-thermal-data.c

## Purpose
`omap5-thermal-data.c` provides OMAP5430 thermal configuration for MPU, GPU, and CORE sensors.

## Important APIs, Types, and Functions
It defines three `temp_sensor_registers`, three `temp_sensor_data` threshold/clock descriptors, `omap5430_adc_to_temp`, and exported `const struct ti_bandgap_data omap5430_data`.

## Control Flow
The data is consumed by bandgap probe. Feature bits select TSHUT threshold configuration, TALERT, counter-delay programming, history-buffer trend support, and freeze-bit reads. The MPU sensor also registers CPU cooling. Temperature reads freeze history where needed and convert ADC code using the OMAP5430 table.

## State and Persistence Behavior
All objects are static configuration. Runtime per-sensor data and saved registers live in `ti_bandgap`.

## Dependencies and Integration Points
It includes `omap5xxx-bandgap.h`, `ti-bandgap.h`, and `ti-thermal.h`; it integrates with thermal OF zones and cpufreq cooling.

## Risks and Edge Cases
The three domains share common control/status registers but use distinct masks and threshold offsets. Counter-delay values must match hardware-supported intervals, and history-buffer trend support depends on freeze/unfreeze correctness.

## Test Signals
OMAP5430 build/probe, three zone registrations, CPU cooling registration for MPU, history-buffer trend reads, TALERT notification, and ADC boundary conversion tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/omap5-thermal-data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/omap5xxx-bandgap.h -->
# sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/omap5xxx-bandgap.h

## Purpose
`omap5xxx-bandgap.h` defines OMAP5430 bandgap register offsets, bit masks, ADC range, clock limits, and threshold constants for GPU, MPU, and CORE sensors.

## Important APIs, Types, and Functions
Macros describe per-domain fuse/temp/threshold/TSHUT/history offsets, common control/status offsets, temperature sensor fields, freeze/hot/cold masks, counter mask, threshold masks, ADC range `540..945`, 1-1.5 MHz clocks, and default TSHUT/TALERT codes.

## Control Flow
No runtime flow exists. `omap5-thermal-data.c` consumes the definitions to initialize OMAP5430 descriptors.

## State and Persistence Behavior
No state is stored; it is static hardware metadata.

## Dependencies and Integration Points
It integrates with TI bandgap generic structures and OMAP5 Kconfig selection.

## Risks and Edge Cases
The comment labels CORE offsets as MPU in one heading, so readers must trust macro names and data initialization rather than comments alone. Wrong freeze masks or history offsets would break trend and errata-safe reads.

## Test Signals
Compile OMAP5 support, verify each domain's DTEMP/history registers, alert masks, TSHUT thresholds, and conversion bounds on OMAP5430 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/omap5xxx-bandgap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/ti-bandgap.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/ti-bandgap.c

## Purpose
`ti-bandgap.c` is the hardware driver for TI OMAP/DRA bandgap temperature sensors. It handles MMIO access, conversion, alert/shutdown interrupts, clocks, OF matching, thermal sensor exposure, and PM context save/restore.

## Important APIs, Types, and Functions
Key public APIs are `ti_bandgap_read_update_interval`, `ti_bandgap_write_update_interval`, `ti_bandgap_read_temperature`, `ti_bandgap_set_sensor_data`, `ti_bandgap_get_sensor_data`, and `ti_bandgap_get_trend`. Major internals include register RMW helpers, `ti_bandgap_power`, errata 814 temperature read, TALERT/TSHUT IRQ handlers, ADC conversion, single-read forcing, continuous-mode setup, TSHUT/TALERT init, `ti_bandgap_build`, probe/remove, and PM notifier/suspend/resume logic.

## Control Flow
Probe builds `ti_bandgap` from DT match data, maps MMIO, obtains optional TSHUT GPIO, checks efuses, configures clocks, powers sensors, programs counters and default thresholds, sets continuous mode when supported, registers cooling/exposes each sensor through callbacks, enables TALERT IRQs after setup, and registers a CPU PM notifier except on excluded OMAP4430 systems. Temperature reads validate sensor id, optionally force a single conversion, read/freezes DTEMP, apply errata workaround if needed, and convert ADC code to millidegrees. TALERT toggles hot/cold masks to wait for the opposite edge and reports temperatures; TSHUT calls `orderly_poweroff(true)`.

## State and Persistence Behavior
Runtime state is held in `struct ti_bandgap`: base address, clocks, lock, IRQ/GPIO, `regval` shadows, thermal private data, and suspend flag. PM save/restore preserves mode, counters, thresholds, masks, and TSHUT registers across suspend and CPU cluster idle. No nonvolatile persistence exists.

## Dependencies and Integration Points
It depends on clk, GPIO, IRQ, OF platform matching, sys_soc quirks, CPU PM, thermal/cpufreq bridge callbacks, and per-SoC `ti_bandgap_data` tables.

## Risks and Edge Cases
Clock-rate validation uses sensor 0 limits for the device. IRQ setup and error unwinding are complex. Wrong feature bits can cause unsupported register accesses. ADC out-of-range maps to `-EIO`. TSHUT shutdown behavior is intentionally severe and must be tested carefully.

## Test Signals
Per-compatible probe/remove, clock failure and IRQ failure unwinding, temperature conversion bounds, TALERT mask toggling, TSHUT interrupt handling in controlled tests, suspend/resume context restore, CPU PM notifier paths, and errata 814 triple-read coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/ti-bandgap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/ti-bandgap.h -->
# sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/ti-bandgap.h

## Purpose
`ti-bandgap.h` defines the shared data model, feature bits, and public APIs for the TI bandgap thermal driver and per-SoC data files.

## Important APIs, Types, and Functions
Core types are `temp_sensor_registers`, `temp_sensor_data`, `temp_sensor_regval`, `ti_bandgap`, `ti_temp_sensor`, and `ti_bandgap_data`. Feature macros include TSHUT, TSHUT_CONFIG, TALERT, MODE_CONFIG, COUNTER, POWER_SWITCH, CLK_CTRL, FREEZE_BIT, COUNTER_DELAY, HISTORY_BUFFER, ERRATA_814, UNRELIABLE, and CONT_MODE_ONLY. Public prototypes expose update intervals, temperature, private sensor data, and trend.

## Control Flow
The header has no executable flow. `ti-bandgap.c` interprets feature bits and descriptors to decide which registers to touch and which runtime paths to enable.

## State and Persistence Behavior
It defines runtime state shape: `ti_bandgap` owns MMIO, clocks, lock, IRQs, saved register values, and suspend state; `temp_sensor_regval` persists per-sensor context across PM transitions.

## Dependencies and Integration Points
It depends on spinlocks, CPU PM, device/PM runtime types, and conditional Kconfig externs for per-family data symbols. Per-SoC data files and `ti-thermal-common.c` include it.

## Risks and Edge Cases
Feature-bit accuracy is critical because it gates register access. Flexible-array `sensors[]` requires static initializers to keep `sensor_count` consistent. Conditional externs become `NULL` when configs are disabled.

## Test Signals
Build all family configurations, static checks for descriptor initialization, probe tests validating feature-driven paths, and PM save/restore tests for `temp_sensor_regval`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/ti-bandgap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/ti-thermal-common.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/ti-thermal-common.c

## Purpose
`ti-thermal-common.c` bridges TI bandgap sensors into the generic Linux thermal framework, including thermal-zone operations, hotspot extrapolation, hwmon exposure, asynchronous updates, and optional CPU cooling registration.

## Important APIs, Types, and Functions
`struct ti_thermal_data` stores cpufreq policy, thermal zones, cooling device, bandgap pointer, work item, sensor id, and ownership flags. Public APIs are `ti_thermal_expose_sensor`, `ti_thermal_remove_sensor`, `ti_thermal_report_sensor_temperature`, `ti_thermal_register_cpu_cooling`, and `ti_thermal_unregister_cpu_cooling`.

## Control Flow
Exposure builds or reuses sensor private data, registers a DT thermal zone using `.get_temp` and `.get_trend`, stores the data in bandgap `regval`, programs a 250 ms update interval, and adds hwmon sysfs. Temperature reads get bandgap temperature, optionally subtract PCB zone temperature, choose slope/constant from either zone params or sensor PCB calibration, and return extrapolated hotspot temperature. TALERT reports schedule work that calls `thermal_zone_device_update`. CPU cooling is skipped for DT thermal-sensor-cell deployments and otherwise registers cpufreq cooling for CPU 0.

## State and Persistence Behavior
Per-sensor state is devm-allocated and referenced from `ti_bandgap->regval[id].data`. Work items and cpufreq policies live until driver removal; hwmon is devm-managed.

## Dependencies and Integration Points
It depends on thermal OF registration, thermal hwmon, cpufreq/cpu cooling, optional PCB thermal zone named `"pcb"`, and TI bandgap APIs.

## Risks and Edge Cases
`ti_thermal_report_sensor_temperature` assumes sensor data exists. PCB zone read failures fall back to default slope/offset. CPU cooling registration can defer probe if no cpufreq policy exists.

## Test Signals
Zone registration and hwmon files, hotspot math with and without PCB zone, trend mapping from bandgap trend, TALERT workqueue update, cpufreq cooling register/unregister, and probe-defer behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/ti-thermal-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/ti-thermal.h -->
# sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/ti-thermal.h

## Purpose
`ti-thermal.h` declares TI thermal framework bridge functions and shared thermal constants for OMAP/DRA hotspot extrapolation and trip planning.

## Important APIs, Types, and Functions
It defines PCB gradient constants for OMAP4430/4460/4470/5430 and DRA752, common trip temperatures `OMAP_TRIP_COLD`, `OMAP_TRIP_HOT`, `OMAP_TRIP_SHUTDOWN`, trip count/step, and `FAST_TEMP_MONITORING_RATE`. Under `CONFIG_TI_THERMAL` it declares expose/remove/report/cooling APIs; otherwise it provides success-returning stubs.

## Control Flow
No runtime flow exists in the header. It lets per-SoC data files assign callbacks even when the generic thermal bridge is optional.

## State and Persistence Behavior
No state is stored here; constants are compile-time calibration and policy defaults.

## Dependencies and Integration Points
It includes `ti-bandgap.h` and is used by every TI SoC data file plus `ti-thermal-common.c`.

## Risks and Edge Cases
Disabled stubs mean the hardware bandgap driver can probe without exposing sensors to the thermal framework. Calibration constants directly affect reported hotspot temperatures and policy behavior.

## Test Signals
Build with `CONFIG_TI_THERMAL` enabled/disabled, verify callback presence in per-SoC data, and validate hotspot calculations against expected calibration constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/ti-thermal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/uniphier_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/uniphier_thermal.c

## Purpose
`uniphier_thermal.c` is a Socionext UniPhier platform thermal driver using a parent syscon regmap to configure PVT temperature monitoring, alert channels, and thermal-zone reporting.

## Important APIs, Types, and Functions
Important types are `uniphier_tm_soc_data` for per-SoC offsets and `uniphier_tm_dev` for runtime state. Key functions initialize calibration and monitor mode, set alerts, enable/disable sensor, read signed temperature, clear IRQs, handle threaded alarm updates, walk trips, probe, and remove.

## Control Flow
Probe allocates state, gets match data and IRQ, obtains the parent syscon regmap, initializes the sensor and calibration, requests a threaded IRQ, registers a DT thermal zone, walks all trips to program up to three alert channels, validates that a critical trip exists at or below 120 C, and enables monitoring. Hard IRQ disables the interrupt and clears alert bits, then the thread updates the thermal zone.

## State and Persistence Behavior
Runtime state tracks regmap, alert enable flags, thermal zone, and SoC offsets. Hardware monitor and alert registers persist while the device is active; remove disables alerts and stops PVT. There is no PM implementation in this file.

## Dependencies and Integration Points
It depends on syscon/regmap, OF match data, platform IRQs, `devm_thermal_of_zone_register`, and thermal trip iteration.

## Risks and Edge Cases
Only three alert channels are available; DT with more trips can overrun expectations unless thermal trip count is constrained externally. The hard IRQ disables the IRQ but the thread does not re-enable it in this file, so IRQ flow should be audited against irq-core semantics and hardware behavior.

## Test Signals
Probe on each compatible, calibration fallback property tests, signed temperature reads, alert programming for trips, critical-trip limit failure, IRQ-triggered thermal updates, and remove disabling sensor registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/uniphier_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/Kconfig

## Purpose
This Kconfig file selects the unified USB4/Thunderbolt driver and optional debug/test features.

## Important APIs, Types, and Functions
Symbols are `USB4`, `USB4_DEBUGFS_WRITE`, `USB4_DEBUGFS_MARGINING`, `USB4_KUNIT_TEST`, and `USB4_DMA_TEST`. `USB4` depends on PCI and selects crypto/hash/NVMEM support; test and debug features depend on KUnit or debugfs as appropriate.

## Control Flow
There is no runtime flow. Kconfig choices determine whether the main `thunderbolt` module, dangerous debugfs write/margining paths, KUnit tests, and the DMA loopback test module are built.

## State and Persistence Behavior
No runtime state. Configuration persists in the kernel `.config`.

## Dependencies and Integration Points
It feeds the Thunderbolt Makefile and user-visible module availability. Debug options intentionally carry warnings for non-production use.

## Risks and Edge Cases
`USB4_DEBUGFS_WRITE` and margining expose hardware mutation and should not be enabled in distro kernels. KUnit requires built-in KUnit (`KUNIT=y`).

## Test Signals
Build matrix for module/built-in, debugfs options, KUnit, and DMA test; verify dependencies prevent unsupported combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/Makefile -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/Makefile

## Purpose
The Thunderbolt Makefile composes the main `thunderbolt` driver object and optional ACPI, debugfs, KUnit, and DMA test objects.

## Important APIs, Types, and Functions
`obj-${CONFIG_USB4}` builds `thunderbolt.o`. Core objects include NHI, control, switch, capability, path, tunnel, domain, DMA port, ICM, property, xdomain, link-controller, TMU, USB4, NVM, retimer, quirks, and CLx code. Optional objects include `acpi.o`, `debugfs.o`, `test.o`, and `dma_test.o`.

## Control Flow
Build composition is driven by Kconfig. `ccflags-y := -I$(src)` supports local header inclusion, and `CFLAGS_test.o` disables structleak for KUnit tests.

## State and Persistence Behavior
No runtime state. The selected object list determines module contents.

## Dependencies and Integration Points
It is coupled to `drivers/thunderbolt/Kconfig` and the source files' conditional declarations.

## Risks and Edge Cases
Using `${CONFIG_USB4}` instead of the more common `$(CONFIG_USB4)` is accepted by kbuild but should remain consistent with local style. Optional objects must align with function references guarded by config.

## Test Signals
Build with ACPI on/off, DEBUG_FS on/off, USB4 KUnit, and DMA test module enabled/disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/acpi.c -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/acpi.c

## Purpose
`acpi.c` provides ACPI integration for Thunderbolt/USB4: runtime PM device links for tunneled ports, native-control policy checks, retimer power control through _DSM, and ACPI companion binding for routers and USB4 ports.

## Important APIs, Types, and Functions
Key APIs are `tb_acpi_add_links`, `tb_acpi_is_native`, `tb_acpi_may_tunnel_usb3`, `tb_acpi_may_tunnel_dp`, `tb_acpi_may_tunnel_pcie`, `tb_acpi_is_xdomain_allowed`, `tb_acpi_power_on_retimers`, `tb_acpi_power_off_retimers`, `tb_acpi_init`, and `tb_acpi_exit`. Internal helpers walk ACPI namespace, evaluate retimer DSM functions, and find companions.

## Control Flow
`tb_acpi_add_links` walks ACPI devices looking for `usb4-host-interface` references to the NHI, then creates PM runtime device links from PCIe root/downstream ports to the NHI. Policy helpers read global OSC native USB4 control bits. Retimer power checks whether the USB4 port supports offline mode, queries current DSM online state, and calls the set-online DSM when a transition is required. ACPI bus callbacks match Thunderbolt switches and USB4 port devices and locate companions by the documented NHI/host-router/downstream-port/device-router hierarchy.

## State and Persistence Behavior
Device links are managed by the driver core with autoremove flags. `usb4->can_offline` is set during ACPI setup when the retimer DSM is available. No file-backed persistence exists.

## Dependencies and Integration Points
It depends on ACPI, PM runtime, PCIe port type checks, Thunderbolt core types, USB4 port devices, and platform OSC variables.

## Risks and Edge Cases
DSM return values distinguish powered, busy, and error states; misinterpreting them can break retimer discovery. Device-link creation must keep NHI active long enough to establish supplier/consumer ordering. Companion lookup assumes ACPI topology conventions.

## Test Signals
ACPI namespace tests for NHI references, runtime PM ordering with tunneled PCIe ports, native-control policy checks under different OSC bits, retimer DSM success/busy/failure paths, and ACPI companion binding for host/device routers and ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/cap.c -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/cap.c

## Purpose
`cap.c` implements Thunderbolt switch and port capability-list traversal and lookup, including vendor-specific capability search.

## Important APIs, Types, and Functions
Public APIs are `tb_port_next_cap`, `tb_port_find_cap`, `tb_switch_next_cap`, `tb_switch_find_cap`, and `tb_switch_find_vse_cap`. Internal helpers handle legacy TMU access enable/disable and Light Ridge dummy reads.

## Control Flow
Port search optionally enables TMU access for Light Ridge/Eagle Ridge, walks linked capabilities from `first_cap_offset`, reads each header, compares the capability id, performs a dummy read for Light Ridge cleanup, and disables TMU access. Switch traversal reads capability headers and interprets next pointers differently for TMU, short VSE, and long VSE formats; invalid or unknown caps return errors or terminate when offsets exceed the VSE max.

## State and Persistence Behavior
The code temporarily toggles legacy TMU access bits in switch config space during port capability lookup. No driver-owned persistent state is created.

## Dependencies and Integration Points
It depends on Thunderbolt config-space read/write helpers, switch generation predicates, capability header layouts from `tb_regs.h`, and caller-held topology state.

## Risks and Edge Cases
Malformed capability lists can loop or point outside valid space; the code relies on hardware next pointers and max checks. Legacy TMU enable must be unwound even if capability search fails. Unknown switch capabilities return `-EINVAL`.

## Test Signals
KUnit or mocked config-space tests for no capability, matching capability, read failures, VSE short/long headers, Light Ridge dummy read, and TMU enable/disable error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/cap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/clx.c -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/clx.c

## Purpose
`clx.c` manages Thunderbolt/USB4 CLx low-power states on high-speed lanes, including detection, enable/disable, PM secondary resolution, and Titan Ridge objection masking.

## Important APIs, Types, and Functions
Public APIs are `tb_port_clx_is_enabled`, `tb_switch_clx_init`, `tb_switch_clx_enable`, and `tb_switch_clx_disable`. The module parameter `clx` controls global enablement. Internal helpers read/write lane adapter CL bits, check support, resolve primary/secondary PM roles, validate masks, and mask objections.

## Control Flow
Initialization skips ICM/host routers and unsupported/quirked platforms, then reads upstream and downstream CLx state and stores it in `sw->clx`. Enable validates requested state ordering, requires supported parent/child routers, restricts CL2 to USB4 v2 routers, resolves PM secondary roles, checks both link ends, enables requested CL bits on both ports, masks Titan Ridge objections, and rolls back on failure. Disable clears all stored CL states on both link ends unless the switch is unplugged, in which case it returns the remembered state without touching hardware.

## State and Persistence Behavior
`sw->clx` records enabled CL states for each switch. Hardware lane adapter control bits and Titan Ridge low-power objection masks are modified. The `clx_enabled` module parameter is read-only after module load.

## Dependencies and Integration Points
It depends on Thunderbolt port/switch config reads/writes, USB4 CLx support helpers, link-controller support checks, router generation predicates, quirks, lane adapter registers, and low-power capability offsets.

## Risks and Edge Cases
CLx is disabled for dual single-lane links, xdomain links, Tiger Lake, quirked routers, and unsupported endpoints. Partial enable failures must roll back both sides. CL1 requires CL0s in the validation mask, and CL2 requires v2 routers.

## Test Signals
Mocked switch/port tests for support filtering, mask validation, CL2 version gating, upstream/downstream mismatch warnings, enable rollback, Titan Ridge objection programming, unplugged disable behavior, and module parameter disabled mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/clx.c -->
