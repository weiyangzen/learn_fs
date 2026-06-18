# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-core.c

## Purpose
`coresight-core.c` is the central CoreSight framework implementation. It registers the CoreSight bus, tracks devices and topology, resolves paths from sources to sinks, manages helper devices, exposes common claim/register helpers, coordinates runtime PM references, integrates CTI associations, initializes perf/syscfg support, and handles panic-time synchronization.

## Important APIs, Types, And Functions
Global state includes `coresight_mutex`, per-CPU default sinks, a device-name index list, and optional CTI association callbacks. Claim helpers (`coresight_claim_device*()`, `coresight_disclaim_device*()`, `coresight_clear_self_claim_tag*()`) protect CoreSight devices from external debug agents using claim tags. Topology helpers include `coresight_add_helper()`, `coresight_find_input_type()`, `coresight_find_output_type()`, orphan connection fixup, and connection removal.

Path management is implemented by `_coresight_build_path()`, `coresight_build_path()`, `coresight_release_path()`, `coresight_enable_path()`, and `coresight_disable_path()`. Sink/source utilities include default sink discovery, sink lookup by ID, per-CPU sink setters/getters, trace ID assignment, and source pause/resume wrappers. Registration is handled by `coresight_register()` and `coresight_unregister()`. Common driver helpers include `coresight_alloc_device_name()`, `coresight_init_driver()`, `coresight_remove_driver()`, `coresight_etm_get_trace_id()`, and `coresight_get_enable_clocks()`.

## Control Flow
Module init registers the CoreSight bus, initializes ETM perf support, installs a panic notifier, and initializes syscfg. Individual drivers call `coresight_register()` with a descriptor; registration creates a `coresight_device`, registers it on the bus, creates perf sink links and connection sysfs groups, fixes orphan connections, and notifies CTI association code. Unregistration removes CTI associations, sysfs links, topology references, platform data, and the device.

Path construction recursively walks output connections from source to sink, handles per-CPU source-to-sink shortcuts, powers and pins each device/helper through runtime PM and module references, and builds a source-to-sink list. Path enable iterates reverse order, enabling helpers first, then sinks and links; sources are enabled by sysfs/perf callers. Errors unwind already-enabled components. Disable skips the first source node, disables sinks/links, then adjacent helpers; `coresight_disable_source()` separately disables source helpers.

## State And Persistence
Core state is in registered `coresight_device` objects, topology connection arrays, per-device default sink cache, refcounts, bus registration, and per-prefix name index lists keyed by firmware node. Runtime PM/module references are acquired for active paths and released by `coresight_release_path()`. Panic sync visits all enabled devices and invokes optional panic ops.

## Dependencies And Integration Points
This file is the integration hub for AMBA/platform drivers, firmware graph data, CoreSight sysfs/perf helpers, CTI, syscfg, trace ID allocation, panic notifiers, runtime PM, clocks, and device links. Device-specific drivers depend on its exported registration, path, claim, timeout, access, and clock APIs.

## Risks
Topology handling must account for probe ordering; orphan fixup and helper dynamic connections are therefore sensitive to locking and fwnode lifetime. Path enable/disable order matters because enabling a sink/link can disrupt existing sessions if unwound incorrectly. Claim-tag races with external debuggers intentionally fail with `-EBUSY`, but stale or invalid tag states can block tracing. Name-index storage persists until module exit, so failed allocations leave lists for cleanup later. Recursive graph traversal assumes firmware topology has no harmful cycles.

## Test Signals
Key tests include mixed probe orders, hot-unplug/unregister, helper association before/after primary devices, default sink selection, path build/release refcount balance, sysfs and perf enable paths, trace ID allocation, runtime PM counts, external claim-tag contention, and panic notifier execution. KASAN/lockdep runs are useful around orphan fixup and connection removal.
