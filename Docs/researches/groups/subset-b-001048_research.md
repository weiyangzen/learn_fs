# Research: subset-b-001048

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/power/runtime.c -->
# sources/distributed-fs/ceph-client/drivers/base/power/runtime.c

## Purpose
This file is the Linux device core runtime PM state machine. It implements the public `pm_runtime_*()` entry points, the internal suspend/resume/idle execution paths, autosuspend timers, runtime PM usage counting, parent/child accounting, device-link supplier coordination, wake IRQ handoff, and force-suspend/force-resume helpers used during system sleep transitions.

## Important APIs, Types, And Functions
The main internal callbacks are `rpm_idle()`, `rpm_suspend()`, and `rpm_resume()`, all called with `dev->power.lock` held and interrupts disabled. Public exports include `__pm_runtime_idle()`, `__pm_runtime_suspend()`, `__pm_runtime_resume()`, `pm_schedule_suspend()`, `__pm_runtime_set_status()`, `pm_runtime_barrier()`, `__pm_runtime_disable()`, `pm_runtime_enable()`, devres wrappers, `pm_runtime_forbid()`, `pm_runtime_allow()`, `pm_runtime_no_callbacks()`, `pm_runtime_irq_safe()`, autosuspend setters, supplier helpers, link helpers, and `pm_runtime_force_suspend()/pm_runtime_force_resume()`.

## Control Flow And State
The device state lives in `dev->power`: `runtime_status`, `last_status`, `disable_depth`, `usage_count`, `child_count`, `runtime_error`, `runtime_auto`, request fields, autosuspend timer fields, `deferred_resume`, `irq_safe`, `no_callbacks`, `needs_force_resume`, accounting timestamps, and supplier link counts. `rpm_check_suspend_allowed()` gates suspend on errors, disabled runtime PM, nonzero usage, active children, pending resumes, QoS latency, and current status. `rpm_suspend()` handles autosuspend expiration, request cancellation, concurrent suspend waits, wake IRQ enable sequencing, `runtime_suspend` callback execution, parent child-count decrement, supplier idling, deferred resume, and error rollback. `rpm_resume()` clears pending requests, waits or defers across concurrent state changes, resumes parents and suppliers, disables wake IRQs, calls `runtime_resume`, increments parent child-count, marks last busy, and queues an idle notification.

Asynchronous requests are stored as `RPM_REQ_*` and executed by `pm_runtime_work()` on `pm_wq`; delayed suspends are driven by an `hrtimer`. Accounting is updated before runtime status changes and exposed as active/suspended nanosecond totals.

## Dependencies And Integration Points
This file depends on `linux/pm_runtime.h`, `linux/pm_wakeirq.h`, hrtimers, device links, PM QoS, workqueues, `trace/events/rpm.h`, and driver/bus/class/type/PM-domain `dev_pm_ops`. Wake IRQ integration calls `dev_pm_enable_wake_irq_check()`, `dev_pm_enable_wake_irq_complete()`, and `dev_pm_disable_wake_irq_check()`. Device-link integration keeps suppliers active while consumers resume and releases them after suspend or failed resume. Sysfs `power/control` routes through `pm_runtime_allow()` and `pm_runtime_forbid()`.

## Risks And Test Signals
The main risks are unbalanced usage counts, parent child-count drift, callback return-code misuse, races around `RPM_ASYNC`/`RPM_NOWAIT`, improper `irq_safe` usage, and failure to call `regcache_mark_dirty()`-style driver hooks after power loss. Test signals include runtime PM selftests or driver tests that exercise suspend/resume failure, autosuspend rescheduling, supplier failure, wake IRQ ordering, `pm_runtime_barrier()` cancellation, usage-count underflow warnings, tracepoints (`rpm_*`), and sysfs status/time changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/power/runtime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/power/sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/base/power/sysfs.c

## Purpose
This file exposes device power-management state and policy through per-device sysfs `power/` attributes. It bridges user-visible policy controls to runtime PM, wakeup-source configuration, PM QoS constraints, wakeup statistics, async system sleep configuration, and advanced runtime PM debugging attributes.

## Important APIs, Types, And Functions
The exported setup/removal functions are `dpm_sysfs_add()`, `dpm_sysfs_change_owner()`, `wakeup_sysfs_add()`, `wakeup_sysfs_remove()`, `pm_qos_sysfs_add_*()`, `pm_qos_sysfs_remove_*()`, `rpm_sysfs_remove()`, and `dpm_sysfs_remove()`. Attribute handlers include `control_show/store`, `runtime_status_show`, runtime active/suspended time, `autosuspend_delay_ms`, PM QoS resume latency, latency tolerance, no-power-off flag, wakeup enable/disable, wakeup counters/timers, `runtime_usage`, `runtime_active_kids`, `runtime_enabled`, and `async`.

## Control Flow And State
`dpm_sysfs_add()` creates the base `power` group, merges runtime attributes unless callbacks are suppressed, merges wakeup attributes when the device is wake-capable, merges latency tolerance attributes when supported, and adds wakeup-source stats if needed. Error paths unmerge groups in reverse order. Store handlers parse sysfs text with `sysfs_streq()` or `kstrto*()`, then call core helpers such as `pm_runtime_allow()`, `pm_runtime_forbid()`, `pm_runtime_set_autosuspend_delay()`, `device_set_wakeup_enable()`, and PM QoS update APIs.

Wakeup statistic reads take `dev->power.lock` before dereferencing `dev->power.wakeup`; if no wakeup source is attached they emit a blank line. Runtime status maps internal states to `active`, `suspended`, `suspending`, `resuming`, `unsupported`, or `error`.

## Dependencies And Integration Points
This file depends on sysfs/kobject APIs, runtime PM, wakeup framework functions from `wakeup.c`, PM QoS, and optional config blocks: `CONFIG_PM_SLEEP`, `CONFIG_PM_AUTOSLEEP`, and `CONFIG_PM_ADVANCED_DEBUG`. It is called from device registration/removal and wakeup capability transitions.

## Risks And Test Signals
Risks include partial sysfs group creation failure, stale wakeup-source pointers, invalid user input handling, owner-change mismatches, and incorrect visibility when `pm_runtime_no_callbacks()` removes runtime attributes. Test signals include sysfs read/write tests for `power/control`, wakeup enable toggles, autosuspend delay parsing, PM QoS special values (`n/a`, `auto`, `any`), group cleanup on simulated failure, and uevent emission on wakeup attribute changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/power/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/power/trace.c -->
# sources/distributed-fs/ceph-client/drivers/base/power/trace.c

## Purpose
This file implements the legacy PM trace facility for diagnosing suspend/resume hangs when normal storage or logging may be unavailable. It encodes compact hashes of a trace point and device into RTC time fields, then decodes and matches those hashes after reboot.

## Important APIs, Types, And Functions
Public symbols are `pm_trace_rtc_abused`, `set_trace_device()`, `generate_pm_trace()`, and `show_trace_dev_match()`. Internal helpers include `set_magic_time()`, `read_magic_time()`, `hash_string()`, `show_file_hash()`, `show_dev_hash()`, `pm_trace_notify()`, `early_resume_init()`, and `late_resume_init()`.

## Control Flow And State
`set_trace_device()` hashes `dev_name(dev)` with `DEVSEED` into `dev_hash_value`. `generate_pm_trace()` hashes file/line trace data plus the current device hash and writes the combined value into RTC year/month/day/hour/minute fields with `mc146818_set_time()`, setting `pm_trace_rtc_abused`. On boot, `early_resume_init()` reads the RTC-derived value and registers a PM notifier. `late_resume_init()` splits the value into user/file/device hashes, logs the magic number, scans linker-provided `__tracedata` records for file matches, and scans `dpm_list` for matching devices. The notifier warns after suspend/hibernate if the RTC was intentionally abused.

## Dependencies And Integration Points
This is x86 legacy RTC-specific through `mc146818rtc` and `x86_platform.legacy.rtc`. It integrates with PM notifier hooks, core/late initcalls, linker trace-data sections, the global device PM list, and `/sys/power/pm_trace_dev_match`-style consumers via `show_trace_dev_match()`.

## Risks And Test Signals
The scheme is lossy by design: 24-bit-ish space can collide, RTC values are corrupted intentionally, and systems with slow reboot or no legacy RTC cannot use it. Tests are mostly integration/manual: enable PM trace, force a suspend hang, reboot, confirm magic number and candidate device/file matches, and verify RTC-abuse warning after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/power/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/power/wakeirq.c -->
# sources/distributed-fs/ceph-client/drivers/base/power/wakeirq.c

## Purpose
This file manages wake IRQ attachment for devices, including normal device IRQs used as wake sources and dedicated threaded wake IRQs used to resume runtime-suspended devices or abort system suspend.

## Important APIs, Types, And Functions
Exports include `dev_pm_set_wake_irq()`, `dev_pm_clear_wake_irq()`, `devm_pm_set_wake_irq()`, `dev_pm_set_dedicated_wake_irq()`, and `dev_pm_set_dedicated_wake_irq_reverse()`. Runtime/system PM helpers include `dev_pm_enable_wake_irq_check()`, `dev_pm_disable_wake_irq_check()`, `dev_pm_enable_wake_irq_complete()`, `dev_pm_arm_wake_irq()`, and `dev_pm_disarm_wake_irq()`. Dedicated IRQ handling is done by `handle_threaded_wake_irq()`.

## Control Flow And State
`dev_pm_attach_wake_irq()` stores a `struct wake_irq` in `dev->power.wakeirq` under `dev->power.lock` and attaches it to the device wakeup source when present. Non-dedicated wake IRQs allocate only metadata. Dedicated wake IRQs allocate a name, set `IRQ_DISABLE_UNLAZY`, request a threaded IRQ with `IRQF_ONESHOT | IRQF_NO_AUTOEN`, then mark allocation and optional reverse-order status bits. Runtime suspend calls enable helpers before or after callbacks depending on `WAKE_IRQ_DEDICATED_REVERSE`; resume calls disable helpers. System sleep arming uses `device_may_wakeup()` to call `enable_irq_wake()` and possibly enable a disabled dedicated IRQ.

## Dependencies And Integration Points
This code depends on IRQ core APIs, runtime PM, wakeup-source attachment in `wakeup.c`, and the runtime state machine in `runtime.c`. The threaded handler calls `pm_wakeup_event()` if the IRQ is configured for wakeup, otherwise synchronously resumes the device via `pm_runtime_resume()`.

## Risks And Test Signals
Risks include double attachment, wrong reverse-order selection, unbalanced enable/disable for dedicated IRQs, freeing IRQs while still attached, wake IRQs without wakeup capability, and lost device IRQ semantics after wake-only interrupts. Test signals include suspend/resume with `device_may_wakeup` toggles, runtime suspend/resume ordering checks, threaded wake IRQ resume warnings, IRQ wake enable counts, and devres cleanup on probe failure/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/power/wakeirq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/power/wakeup.c -->
# sources/distributed-fs/ceph-client/drivers/base/power/wakeup.c

## Purpose
This file implements the system wakeup event framework. It registers and tracks wakeup sources, attaches them to devices, manages wakeup IRQ arming, maintains global wakeup event counters used to abort suspend, provides stay-awake/relax event APIs, and exposes aggregate wakeup-source statistics through debugfs.

## Important APIs, Types, And Functions
Exports include wakeup source lifecycle (`wakeup_source_register()`, `wakeup_source_unregister()`), list traversal (`wakeup_sources_read_lock()`, `wakeup_sources_walk_start()`, `wakeup_sources_walk_next()`), device policy (`device_wakeup_enable()`, `device_wakeup_disable()`, `device_set_wakeup_capable()`, `device_set_wakeup_enable()`), wake IRQ attachment and arming, event APIs (`__pm_stay_awake()`, `pm_stay_awake()`, `__pm_relax()`, `pm_relax()`, `pm_wakeup_ws_event()`, `pm_wakeup_dev_event()`), suspend-abort APIs (`pm_wakeup_pending()`, `pm_system_wakeup()`, `pm_system_cancel_wakeup()`, `pm_wakeup_clear()`, `pm_system_irq_wakeup()`, `pm_wakeup_irq()`), and wakeup-count APIs (`pm_get_wakeup_count()`, `pm_save_wakeup_count()`).

## Control Flow And State
Global state includes `events_check_enabled`, two recorded wakeup IRQ slots, `pm_abort_suspend`, `combined_event_count`, `saved_count`, `events_lock`, `wakeup_sources`, `wakeup_count_wait_queue`, `wakeup_srcu`, deleted-source aggregate stats, and `wakeup_ida`. A wakeup source has a spinlock, timer, active flag, event counters, timing totals, autosleep fields, optional sysfs device, and optional wake IRQ.

Activation increments active/event accounting and the low bits of `combined_event_count`; deactivation updates total/max/prevent-sleep time and atomically increments the registered-event count while decrementing in-progress count. `pm_save_wakeup_count()` snapshots the registered count and enables checking only if nothing is in progress. `pm_wakeup_pending()` compares the current count/in-progress pair to the saved value and disables checking after a detected wakeup. Timed events use `pm_wakeup_timer_fn()` to relax a source after a requested processing window.

## Dependencies And Integration Points
The file integrates with device sysfs (`wakeup_sysfs_add/remove()` and `wakeup_source_sysfs_add/remove()`), wake IRQ helpers, suspend core (`s2idle_wake()` and wakeup count protocol), debugfs, SRCU-protected list traversal, timers, tracepoints from `trace/events/power.h`, and device registration state.

## Risks And Test Signals
Risks include leaked wakeup sources, stale wake IRQ pointers, wrong SRCU/list locking, timer races around relax/activate, overflow of packed event counters, suspend abort false positives/negatives, and missing wakeup sysfs on capability changes. Test signals include wakeup_count protocol tests, suspend aborts from `pm_wakeup_event()`, debugfs `wakeup_sources` totals, active-source logging, deleted-source accounting, wake IRQ arm/disarm behavior, and stress with concurrent IRQ events and unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/power/wakeup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/power/wakeup_stats.c -->
# sources/distributed-fs/ceph-client/drivers/base/power/wakeup_stats.c

## Purpose
This file creates a dedicated sysfs class for per-wakeup-source statistics. It mirrors selected `struct wakeup_source` counters and timing fields as attributes under generated `wakeupN` devices.

## Important APIs, Types, And Functions
The key entry points are `wakeup_source_sysfs_add()`, `pm_wakeup_source_sysfs_add()`, `wakeup_source_sysfs_remove()`, and the `postcore_initcall()` `wakeup_sources_sysfs_init()`. Attribute handlers expose `name`, `active_count`, `event_count`, `wakeup_count`, `expire_count`, `relax_count`, `active_time_ms`, `total_time_ms`, `max_time_ms`, `last_change_ms`, and `prevent_suspend_time_ms`.

## Control Flow And State
`wakeup_sources_sysfs_init()` creates the global `wakeup` class. `wakeup_source_device_create()` allocates a `struct device`, initializes it, sets class/parent/groups/release callback, stores the wakeup source as driver data, marks PM not required, assigns a stable name `wakeup%d` from `ws->id`, and calls `device_add()`. Removal unregisters `ws->dev`. Time attributes compute live active time by adding `ktime_get() - ws->last_time` when `ws->active`, and autosleep prevention time when `ws->autosleep_enabled`.

## Dependencies And Integration Points
This file depends on the wakeup source lifecycle in `wakeup.c`, the device core, sysfs attribute groups, ktime, and the `device_set_pm_not_required()` marker so generated stats devices do not get their own PM sysfs burden.

## Risks And Test Signals
Risks include missing class initialization, lifetime coupling between `ws` and generated stats device, unprotected reads of fields updated under `ws->lock`, and stale `ws->dev` if add/remove ordering is wrong. Test signals include class presence, one `wakeupN` per registered source, correct parent links for device-associated sources, attribute monotonicity during active events, and clean device removal on wakeup source unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/power/wakeup_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/property.c -->
# sources/distributed-fs/ceph-client/drivers/base/property.c

## Purpose
This file implements the unified firmware-node/device-property API. It lets drivers read properties, references, child nodes, DMA attributes, PHY modes, IRQs, graph endpoints, match data, and device connections without caring whether the backing firmware description is Device Tree, ACPI, software node, or a secondary fwnode.

## Important APIs, Types, And Functions
Exports include `__dev_fwnode()`, `device_property_present()`, typed `device_property_read_*()` and `fwnode_property_read_*()` helpers, string matching helpers, `fwnode_property_get_reference_args()`, `fwnode_find_reference()`, node naming/parent/child iteration helpers, `fwnode_handle_get()`, `fwnode_device_is_available()`, child count helpers, `device_dma_supported()`, `device_get_dma_attr()`, PHY helpers, `fwnode_iomap()`, IRQ helpers, graph endpoint helpers, `device_get_match_data()`, and connection matching helpers.

## Control Flow And State
Most device helpers are thin wrappers around `dev_fwnode(dev)` and the fwnode operation table. Property lookups first call the primary fwnode operation and often fall back to `fwnode->secondary` when the primary returns false or `-EINVAL`. Typed integer reads funnel through `fwnode_property_read_int_array()`. String matching counts strings, allocates a temporary array, reads values, then uses `match_string()`. Reference helpers return fwnode handles that callers must put.

Child and graph traversal helpers manage references carefully: `fwnode_get_next_parent()` and `fwnode_get_next_child_node()` consume the previous handle, endpoint iteration can continue into secondary fwnodes, and graph lookup can filter disabled/unconnected remotes unless flags request otherwise. Connection matching first checks graph endpoints and then named reference properties.

## Dependencies And Integration Points
The file depends on `linux/property.h` fwnode ops, optional OF support, PHY string tables, IRQ and iomap fwnode ops, ACPI/DT/software-node implementations behind the operation table, and driver subsystems that consume graph endpoints or named references.

## Risks And Test Signals
Risks include inconsistent primary/secondary fallback semantics, reference leaks or double puts, wrong error-code propagation (`-EINVAL`, `-ENOENT`, `-ENODATA`, `-ENOTCONN`), disabled remote endpoint filtering surprises, and string allocation failures. Test signals include firmware-agnostic driver tests with DT/ACPI/software nodes, property count/read/match error cases, reference lifetime checks, graph endpoint selection with `FWNODE_GRAPH_ENDPOINT_NEXT`, IRQ name lookup, PHY mode parsing, and connection matching across graph and property references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/property.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/Kconfig

## Purpose
This Kconfig file declares the build symbols for generic regmap support, regmap KUnit/build helpers, and transport-specific regmap backends.

## Important APIs, Types, And Functions
Key symbols are `REGMAP`, `REGMAP_KUNIT`, `REGMAP_BUILD`, `REGMAP_AC97`, `REGMAP_I2C`, `REGMAP_SLIMBUS`, `REGMAP_SPI`, `REGMAP_SPMI`, `REGMAP_W1`, `REGMAP_MDIO`, `REGMAP_MMIO`, `REGMAP_IRQ`, `REGMAP_RAM`, `REGMAP_SOUNDWIRE`, `REGMAP_SOUNDWIRE_MBQ`, `REGMAP_SCCB`, `REGMAP_I3C`, `REGMAP_SPI_AVMM`, and `REGMAP_FSI`.

## Control Flow And State
`REGMAP` is a hidden bool that defaults to enabled when any transport or IRQ regmap user is selected. Transport symbols are mostly tristates with dependency constraints on their bus subsystems. `REGMAP_IRQ` selects `IRQ_DOMAIN`; `REGMAP_KUNIT` depends on `KUNIT && REGMAP`, defaults with `KUNIT_ALL_TESTS`, and selects `REGMAP_RAM`. `REGMAP_BUILD` exists to force core regmap availability for tests without a concrete transport user.

## Dependencies And Integration Points
This file is consumed by the kernel Kconfig system and directly controls object inclusion in the regmap Makefile. It integrates with bus subsystems such as I2C, SPI, SPMI, W1, PHYLIB/MDIO, SoundWire, I3C, and FSI.

## Risks And Test Signals
Risks include missing dependency expressions that allow impossible builds, hidden `REGMAP` not enabling when a new backend is added, and KUnit tests not selecting a usable RAM backend. Test signals include allmodconfig/allyesconfig, minimal KUnit regmap builds, and checking that new `CONFIG_REGMAP_*` symbols are mirrored in the Makefile and `REGMAP` default expression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/Makefile -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/Makefile

## Purpose
This Makefile maps regmap Kconfig symbols to compiled objects for the core, cache implementations, debugfs, KUnit, RAM test backend, and bus-specific adapters.

## Important APIs, Types, And Functions
The key build rules compile `regmap.o`, `regcache.o`, `regcache-rbtree.o`, `regcache-flat.o`, `regcache-maple.o`, `regmap-debugfs.o`, `regmap-kunit.o`, and transport objects such as `regmap-ac97.o`, `regmap-i2c.o`, `regmap-spi.o`, `regmap-mmio.o`, `regmap-irq.o`, `regmap-sdw.o`, `regmap-sccb.o`, `regmap-i3c.o`, `regmap-mdio.o`, and `regmap-fsi.o`.

## Control Flow And State
The file is declarative. `CFLAGS_regmap.o := -I$(src)` ensures `include/trace/define_trace.h` can include the local `trace.h`. Core cache backends are built whenever `CONFIG_REGMAP` is enabled, while adapters follow their specific Kconfig symbol.

## Dependencies And Integration Points
It must remain synchronized with `Kconfig`, source files in this directory, and trace include layout. Debugfs and KUnit objects are guarded by their respective config symbols.

## Risks And Test Signals
Risks include adding a backend in Kconfig without adding its object here, stale object names after renames, and trace include path breakage. Test signals include `make drivers/base/regmap/`, config matrix builds for each backend, and KUnit regmap builds with `CONFIG_REGMAP_KUNIT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/internal.h -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/internal.h

## Purpose
This internal header defines the private regmap core structures, cache backend interface, debugfs hooks, range/window bookkeeping, async state, formatting helpers, and internal function prototypes shared by regmap implementation files.

## Important APIs, Types, And Functions
Important types include `struct regmap`, `struct regmap_format`, `struct regmap_async`, `struct regcache_ops`, `struct regmap_range_node`, `struct regmap_field`, and `struct regmap_ram_data`. It declares core predicates (`regmap_readable()`, `regmap_writeable()`, `regmap_volatile()`), low-level write/raw-write functions, cache lifecycle/sync helpers, async completion, endian selection, cache backend ops instances, and RAM regmap initialization helpers.

## Control Flow And State
`struct regmap` centralizes locking, bus callbacks, register format, access tables, raw/single/multi IO limits, cache configuration and state (`cache_only`, `cache_bypass`, `cache_dirty`, defaults, patch list), async queues, debugfs state, range windows, and optional hwspinlock. `struct regcache_ops` is the polymorphic cache backend contract with init/exit/populate/read/write/sync/drop/debugfs hooks.

Inline helpers compute register offsets and cache indexes using stride or stride order, expose cached value addresses, and return a user-facing regmap name. Debugfs hooks compile to no-ops without `CONFIG_DEBUG_FS`.

## Dependencies And Integration Points
This header is consumed by all regmap core, cache, debugfs, transport, and KUnit files. It depends on public `linux/regmap.h` for external configuration/types and internal regmap locking conventions.

## Risks And Test Signals
Risks include ABI-like internal structure coupling across many files, incorrect cache word-size assumptions, lock misuse when backend code calls map operations, and config-specific missing prototypes. Test signals include full regmap build coverage, lockdep with mutex/spin/raw-spin regmaps, KUnit RAM backend tests, cache backend matrix tests, and sparse/compile checks across debugfs and non-debugfs configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regcache-flat.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regcache-flat.c

## Purpose
This file implements flat-array regcache backends. It stores register values in a dense array indexed by register stride and tracks validity with a bitmap, providing both legacy flat behavior and sparse flat behavior.

## Important APIs, Types, And Functions
The internal data type is `struct regcache_flat_data` with `valid` bitmap and flexible `data[]`. Backend hooks are `regcache_flat_init()`, `regcache_flat_exit()`, `regcache_flat_populate()`, read variants, `regcache_flat_write()`, and `regcache_flat_drop()`. Exported backend descriptors are `regcache_flat_ops` and `regcache_flat_sparse_ops`.

## Control Flow And State
Initialization requires a power-of-two stride path (`reg_stride_order >= 0`) and a known `max_register`, then allocates one slot per possible register index plus a validity bitmap. Population writes explicit defaults and optionally fills missing values via `reg_default_cb`. Legacy `flat` reads return zero-initialized data and warn once if a slot was never valid; `flat-sparse` returns `-ENOENT` for invalid slots. Writes set data and validity. Sparse drop clears validity bits for a register range.

## Dependencies And Integration Points
The backend is selected by `regcache.c` through `REGCACHE_FLAT` or `REGCACHE_FLAT_S`. It relies on cache index helpers from `internal.h`, bitmap APIs, and regmap allocation flags.

## Risks And Test Signals
Risks include huge memory use for sparse register maps, invalid max-register configuration, legacy zero-read surprises, and bitmap range mistakes. Test signals include cache read/write/drop KUnit cases, sparse invalid-read behavior, default callback population, non-power-of-two stride rejection, and memory allocation failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regcache-flat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regcache-maple.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regcache-maple.c

## Purpose
This file implements a maple-tree based regcache backend. It stores contiguous cached register ranges as dynamically allocated arrays indexed by maple tree ranges, improving sparse/fragmented cache behavior while supporting range sync and drop.

## Important APIs, Types, And Functions
Backend hooks include `regcache_maple_init()`, `regcache_maple_exit()`, `regcache_maple_populate()`, `regcache_maple_read()`, `regcache_maple_write()`, `regcache_maple_drop()`, and `regcache_maple_sync()`. Helper functions include `regcache_maple_insert_block()` and `regcache_maple_sync_block()`. The backend descriptor is `regcache_maple_ops`.

## Control Flow And State
Reads use an RCU read-side maple lookup and return `-ENOENT` when no range contains the register. Writes update an existing range or search adjacent lower/upper ranges, allocate a merged array spanning `index..last`, store the range under maple-tree lock, and free replaced arrays. Drops iterate intersecting entries, optionally preserve lower/upper fragments outside the drop interval, erase the old node, and store preserved fragments. Population groups contiguous default registers into one maple range per block. Sync scans cached ranges and emits only contiguous subranges whose values need sync, using raw writes when beneficial.

## Dependencies And Integration Points
The backend depends on `linux/maple_tree.h`, RCU read sections, regmap locking as the outer serializer, `_regmap_write()`, `_regmap_raw_write()`, `regcache_reg_needs_sync()`, and value formatting helpers.

## Risks And Test Signals
Risks include off-by-one range lengths, RCU/lifetime mistakes when freeing replaced arrays, false sharing between maple locks and regmap locks, raw-write length errors, and fragmentation during repeated drop/write cycles. Test signals include sparse write/read/merge/drop tests, lockdep with maple tree locking, raw vs single sync behavior, allocation-failure injection, and cache sync after reset with default skipping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regcache-maple.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regcache-rbtree.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regcache-rbtree.c

## Purpose
This file implements the red-black-tree regcache backend. It stores cached registers in rb-tree nodes, each containing a block of adjacent registers plus a presence bitmap, optimized for sparse maps with local adjacency.

## Important APIs, Types, And Functions
Internal types are `struct regcache_rbtree_node` and `struct regcache_rbtree_ctx`. Backend hooks include `regcache_rbtree_init()`, `regcache_rbtree_exit()`, `regcache_rbtree_populate()`, `regcache_rbtree_read()`, `regcache_rbtree_write()`, `regcache_rbtree_sync()`, `regcache_rbtree_drop()`, and optional debugfs `rbtree_show()`. The backend descriptor is `regcache_rbtree_ops`.

## Control Flow And State
Lookup first checks `cached_rbnode`, then traverses the rb-tree by base/top register range. Writes update an existing block, expand a nearby block if within a heuristic distance, or allocate a new node sized from a readable access table range when possible. Expanding a block reallocates value storage and presence bitmap, shifts existing data when prepending, updates base/length, and marks the new register present. Sync walks rb nodes in order, clips to the requested region, and delegates block syncing to `regcache_sync_block()` with async enabled. Drop clears presence bits within affected blocks but keeps node allocations.

## Dependencies And Integration Points
This backend uses Linux rbtree/debugfs/seq_file APIs, regcache block sync helpers, cache value formatting, and map access tables. It is selected through `regcache.c` for `REGCACHE_RBTREE`.

## Risks And Test Signals
Risks include overlapping rb nodes during block expansion, bitmap shift mistakes, stale `cached_rbnode` after structural changes, memory growth after dropping regions, and async completion errors during sync. Test signals include sparse/random register write/read tests, expansion/prepend cases, readable-range allocation cases, drop then read `-ENOENT`, debugfs output sanity, and async sync completion failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regcache-rbtree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regcache.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regcache.c

## Purpose
This file is the shared regcache orchestration layer. It selects cache backends, owns default-value preparation, exposes cache read/write/sync/drop/control APIs, manages dirty/bypass/cache-only state, applies register patches, and provides common block-sync and value-format helpers used by cache backends.

## Important APIs, Types, And Functions
Exports include `regcache_sort_defaults()`, `regcache_sync()`, `regcache_sync_region()`, `regcache_drop_region()`, `regcache_cache_only()`, `regcache_mark_dirty()`, `regcache_cache_bypass()`, and `regcache_reg_cached()`. Internal/public-to-regmap helpers include `regcache_init()`, `regcache_exit()`, `regcache_read()`, `regcache_write()`, `regcache_reg_needs_sync()`, `regcache_set_val()`, `regcache_get_val()`, `regcache_lookup_reg()`, `regcache_sync_val()`, and `regcache_sync_block()`.

## Control Flow And State
`regcache_init()` validates defaults, selects a backend from `cache_types`, copies explicit defaults or derives defaults from raw defaults/hardware, sets max-register when needed, initializes and populates the backend, and handles cleanup on errors. `regcache_hw_init()` can read all raw registers from hardware or individual readable/nonvolatile registers to build defaults. Reads and writes skip volatile registers. `regcache_sync()` locks the map, restores initial bypass state on exit, writes patches first, syncs either through backend-specific sync or default register iteration, clears `cache_dirty` on success, resets `no_sync_defaults`, and rewrites selector registers for paged maps. Region sync is the bounded equivalent.

`cache_only` means API writes update only cache; `cache_bypass` means writes target hardware only. `regcache_mark_dirty()` sets `cache_dirty` and `no_sync_defaults` after reset/power loss. Block sync chooses raw writes for contiguous ranges when the bus supports them and single writes otherwise.

## Dependencies And Integration Points
This file depends on backend ops from flat/rbtree/maple, `regmap` core IO (`_regmap_write`, `_regmap_raw_write`, `regmap_read`, `regmap_raw_read`), tracepoints, bsearch/sort helpers, range-tree paging selectors, and map locks.

## Risks And Test Signals
Risks include stale defaults, failing to restore bypass/async state on errors, incorrect default skipping after reset, volatile/writeable filtering errors, patch write failures, selector-cache mismatch in paged maps, and raw block boundary mistakes. Test signals include regmap KUnit cache tests, dirty/sync/default skip cases, cache-only/bypass warnings, volatile register cache rejection, hardware-read default generation, patch application failures, and async/raw-write completion checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-ac97.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-ac97.c

## Purpose
This file provides the regmap bus adapter for AC'97 codecs. It lets AC'97 codec drivers use generic regmap APIs over `snd_ac97` bus read/write operations and supplies a default volatile-register policy for common AC'97 status/identity registers.

## Important APIs, Types, And Functions
Exports include `regmap_ac97_default_volatile()`, `__regmap_init_ac97()`, and `__devm_regmap_init_ac97()`. Internal bus callbacks are `regmap_ac97_reg_read()` and `regmap_ac97_reg_write()`, referenced by `ac97_regmap_bus`.

## Control Flow And State
The volatile helper returns true for reset, powerdown, paging, extended ID/status, GPIO status, vendor IDs, codec class/revision, PCI subsystem IDs, function select/info, and sense info registers. Reads and writes cast bus context to `struct snd_ac97` and call `ac97->bus->ops->read()` or `write()`. Init wrappers pass `&ac97->dev`, the static regmap bus, and the codec context to core managed or unmanaged regmap initialization.

## Dependencies And Integration Points
This file depends on ALSA AC'97 codec definitions and regmap core initialization. Kconfig/Makefile include it behind `CONFIG_REGMAP_AC97`. Driver integrations typically use the volatile helper in `struct regmap_config`.

## Risks And Test Signals
Risks include AC'97 bus ops returning no error status, volatile list omissions that cause stale cache values, and lifetime mismatch between `snd_ac97` and managed regmap instances. Test signals include AC'97 driver probe using regmap, read/write passthrough verification with a fake bus, cache behavior for volatile registers, and remove-path checks for devm initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-ac97.c -->
