# subset-b-001050 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap.c

Purpose: this is the central Linux regmap implementation, providing a common register access layer above MMIO, I2C, SPI, and bus-specific callbacks. It normalizes register/value formatting, locking, cache interaction, paged register windows, raw and scalar transfers, field helpers, async writes, patch application, and device-resource integration.

Important APIs, types, and functions: exported entry points include `__regmap_init`, `__devm_regmap_init`, `regmap_attach_dev`, `regmap_exit`, `dev_get_regmap`, `regmap_write`, `regmap_write_async`, `regmap_raw_write`, `regmap_noinc_write`, `regmap_bulk_write`, `regmap_multi_reg_write`, `regmap_raw_write_async`, `regmap_read`, `regmap_read_bypassed`, `regmap_raw_read`, `regmap_noinc_read`, `regmap_bulk_read`, `regmap_multi_reg_read`, `regmap_update_bits_base`, field allocation/read/update helpers, `regmap_async_complete`, `regmap_register_patch`, and capability getters. The file manipulates `struct regmap`, `struct regmap_bus`, `struct regmap_config`, `struct regmap_range_node`, `struct regmap_field`, and `struct reg_sequence`.

Control flow: initialization validates configuration, selects lock type, computes register/value byte widths, chooses endian-specific format/parse callbacks, installs bus read/write adapters, builds range-window RB-tree entries, initializes cache via `regcache_init`, then attaches to devres/debugfs. Scalar writes validate stride and writeability, update cache unless bypassed or deferred, then call the selected bus write callback. Raw writes format the address into `work_buf`, set read/write flag masks, split by bus maximum transfer size, handle window paging through `_regmap_select_page`, and choose async, gather-write, direct-write, or manually linearized fallback paths. Reads first try cache unless bypassed, reject cache-only misses, then perform bus reads and backfill cache. Bulk reads use raw transfers for volatile/no-cache ranges and word-by-word cache reads otherwise. Update-bits uses bus-native `reg_update_bits` for volatile registers when present, otherwise performs read/modify/write.

State and persistence: persistent runtime state is in `struct regmap`: device pointer, name, bus/context, lock callbacks, format callbacks, cache mode flags, range tree, selector buffer, async lists, cache patch array, and debugfs hooks. Register values may persist in the regcache, while `cache_only`, `cache_dirty`, and `cache_bypass` control whether hardware is touched. Device association is represented as a devres resource so `dev_get_regmap()` can find maps by optional name. Teardown releases cache, debugfs, range nodes, selector/work buffers, async buffers, hwspinlock, bus context, bus object when owned, and patches.

Dependencies and integration points: this file depends on `internal.h`, regcache backends, debugfs helpers, hwspinlocks, firmware properties for endian selection, tracepoints from `drivers/base/regmap/trace.h`, kernel devres, and bus-specific `struct regmap_bus` callbacks. It is a shared substrate for many drivers, so callback contracts around sleeping, raw transfer limits, endian format, and cacheability are integration-critical.

Risks: register access policy predicates must be exact because wrong readable/writeable/volatile/no-increment decisions can corrupt devices or return stale cache values. Paged range selection mutates `map->work_buf` temporarily and can recurse through `_regmap_update_bits`; selector-window overlap bugs would be subtle. Async writes rely on caller buffer lifetime for raw async transfers and correct `regmap_async_complete()` use. No-increment FIFO handling intentionally caches only the last written value, which is a special semantic that callers must understand. Error cleanup in initialization is broad and must stay paired with every allocation/ownership path.

Test signals: direct tests are usually in regmap KUnit or bus-driver tests outside this file. Useful signals include exercising scalar, raw, bulk, no-increment, multi-register, paged-window, cache-only, cache-bypass, async, and endian-format paths under fault injection. Tracepoints (`regmap_reg_*`, `regmap_bulk_*`, `regmap_hw_*`, async events) provide runtime observability for transfer sequencing and cache/hardware decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/trace.h -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/trace.h

Purpose: this header declares the ftrace event surface for the regmap subsystem. It records scalar register reads/writes, cache reads, raw/bulk data transfers, hardware transfer boundaries, cache state changes, async write lifecycle events, cache sync status, and cache drop regions.

Important APIs, types, and functions: it defines event classes `regmap_reg`, `regmap_bulk`, `regmap_block`, `regmap_bool`, and `regmap_async`, plus concrete events such as `regmap_reg_write`, `regmap_reg_read`, `regmap_reg_read_cache`, `regmap_bulk_write`, `regmap_bulk_read`, `regmap_hw_read_start`, `regmap_hw_read_done`, `regmap_hw_write_start`, `regmap_hw_write_done`, `regcache_sync`, `regmap_cache_only`, `regmap_cache_bypass`, `regmap_async_write_start`, `regmap_async_io_complete`, `regmap_async_complete_start`, `regmap_async_complete_done`, and `regcache_drop_region`.

Control flow: users include the header normally for declarations; exactly one C file defines `CREATE_TRACE_POINTS` before including it to emit tracepoint definitions. Event payloads capture `regmap_name(map)`, register numbers, values, counts, buffer snapshots, flags, and status strings. Bulk events use a dynamic array and print data as hex.

State and persistence: this file stores no runtime state. Tracepoint definitions become kernel instrumentation hooks; when tracing is enabled, emitted event records persist only in the tracing ring buffer according to the active tracing configuration.

Dependencies and integration points: it includes `linux/ktime.h`, `linux/tracepoint.h`, and local `internal.h` for `struct regmap` and `regmap_name()`. `regmap.c` creates the tracepoints; regcache code can emit the cache-related events. `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` are set for `trace/define_trace.h`.

Risks: tracepoint ABI names and field layouts are consumed by tooling, so renaming events or changing fields can break diagnostics. Dynamic buffer capture can expose register contents in traces, so debug access controls matter. Incorrect include guard or `TRACE_INCLUDE_*` setup would break trace generation.

Test signals: building with tracing enabled validates the macro expansion. Runtime tests can enable `regmap:*` events and verify expected start/done pairs around reads, writes, cache-only/bypass transitions, async completion, and cache sync/drop operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/soc.c -->
# sources/distributed-fs/ceph-client/drivers/base/soc.c

Purpose: this file implements the generic SoC bus and SoC device registration helpers used to expose SoC identity information through sysfs and to let drivers match against machine/family/revision/SoC ID tuples.

Important APIs, types, and functions: `struct soc_device` wraps a `struct device`, `struct soc_device_attribute *`, and IDA-allocated numeric ID. Exported functions are `soc_device_to_device`, `soc_attr_read_machine`, `soc_device_register`, `soc_device_unregister`, and `soc_device_match`. It defines a `soc` bus type and sysfs attributes `machine`, `family`, `serial_number`, `soc_id`, and `revision`.

Control flow: registration first fills the machine string from DT model when absent. If the SoC bus is not registered yet, one early attribute pointer can be stored and later registered by the `core_initcall`. Normal registration allocates the device and attribute group array, assigns a unique ID via `ida_alloc`, configures bus/groups/release callback, names the device `socN`, and calls `device_register`. Attribute visibility is conditional: only attributes with non-NULL source strings are exposed. Matching iterates candidate match entries and bus devices, comparing requested fields with `glob_match`.

State and persistence: global state includes `soc_ida`, `soc_bus_registered`, and `early_soc_dev_attr`. Per-device state persists as a registered device until `soc_device_unregister`, at which point `soc_release` frees the ID, groups, and wrapper.

Dependencies and integration points: it integrates with the device core, sysfs, IDA, Open Firmware model reading, and `linux/sys_soc.h`. Consumers use `soc_device_match()` as a fallback when device-tree compatible strings are not enough to identify variants.

Risks: early registration supports only one pending SoC attribute, so competing early users get `-EBUSY`. The attribute strings are owned by the caller and the comment requires freeing `soc_dev->attr` only after unregister. Matching with glob patterns is flexible but can hide overly broad match rules.

Test signals: boot-time sysfs entries under the `soc` bus and callers of `soc_device_match()` are the main runtime signals. Tests should check early registration before `soc_bus_register`, missing optional attributes, glob matching, unregister cleanup, and ID reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/soc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/swnode.c -->
# sources/distributed-fs/ceph-client/drivers/base/swnode.c

Purpose: this file implements software firmware nodes, allowing kernel code to create fwnode-compatible property and graph hierarchies without ACPI or device tree backing. It also provides property-entry duplication/free helpers and device attachment helpers.

Important APIs, types, and functions: the internal `struct swnode` combines a kobject, `struct fwnode_handle`, backing `struct software_node`, root/child ID allocation, parent/child lists, and flags for dynamically allocated or device-managed nodes. Exported APIs include `is_software_node`, `to_software_node`, `software_node_fwnode`, `property_entries_dup`, `property_entries_free`, `software_node_find_by_name`, `software_node_register_node_group`, `software_node_unregister_node_group`, `software_node_register`, `software_node_unregister`, `fwnode_create_software_node`, `fwnode_remove_software_node`, `device_add_software_node`, `device_remove_software_node`, and `device_create_managed_software_node`.

Control flow: property helpers find entries by name, count elements by element size, read integer/string arrays, deep-copy inline or out-of-line data, duplicate strings, and free copied payloads. The `software_node_ops` table maps generic fwnode operations to these property readers, parent/child traversal, named child lookup, reference argument resolution, and graph endpoint helpers. Registration allocates a `struct swnode`, assigns a root or child ID, initializes a fwnode with software ops, creates a kobject under the optional parent, adds child list linkage, and emits `KOBJ_ADD`. Device attachment registers or references the node, sets it as secondary fwnode, and, if the device is registered, creates reciprocal sysfs links.

State and persistence: root IDs live in `swnode_root_ids`; all registered nodes live in the global `swnode_kset` and, for hierarchy, parent child lists. Dynamically created nodes own duplicated `property_entry` arrays and backing `software_node`; static nodes do not. Managed nodes are released by `software_node_notify_remove` when the device goes away.

Dependencies and integration points: it integrates with the generic firmware-node/property APIs, kobjects/ksets, sysfs, device secondary fwnodes, graph endpoint helpers, IDA, and property-entry macros. The base test `property-entry-test.c` exercises much of this behavior.

Risks: reference counting is delicate: `software_node_notify()` gets a kobject before creating links, but error paths after partial link creation must avoid leaks; `device_remove_software_node()` and managed-node removal must balance both device and node references. Parent ordering is mandatory for group registration and child-before-parent unregister. Reference properties require out-of-line storage and registered targets; unresolved targets return `-ENOTCONN`. Graph parsing depends on `port@N` naming conventions.

Test signals: KUnit property-entry tests cover numeric, string, bool, inline/out-of-line copy, and reference properties. Additional signals should cover device link creation/removal, managed node lifetime, parent/child traversal, graph endpoints, duplicate registration, bad parent rejection, and error unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/swnode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/syscore.c -->
# sources/distributed-fs/ceph-client/drivers/base/syscore.c

Purpose: this file manages `syscore` operations, a list of very low-level system core callbacks used during suspend, resume, and shutdown when normal driver/device ordering is no longer sufficient.

Important APIs, types, and functions: exported functions are `register_syscore`, `unregister_syscore`, `syscore_suspend`, and `syscore_resume`; `syscore_shutdown` is a core shutdown entry point. State is a global `syscore_list` protected by `syscore_lock`. Each element is a `struct syscore` whose `ops` can contain `suspend`, `resume`, and `shutdown` callbacks plus opaque `data`.

Control flow: registration appends to the list under mutex, while unregister removes under mutex. Suspend, when enabled by `CONFIG_PM_SLEEP`, emits power tracepoints, checks pending wakeup events, warns if interrupts are enabled, then walks the list in reverse registration order calling suspend callbacks. On failure, it reports the failing callback and resumes the remaining callbacks in forward continuation order. Resume walks forward and calls resume callbacks. Shutdown locks the list and walks reverse order, optionally logging when `initcall_debug` is set.

State and persistence: registered syscore entries persist globally until explicitly unregistered. Suspend/resume does not change the list; it only invokes callbacks. The callback order encodes dependency behavior: last registered suspends first and resumes later in the unwind sequence.

Dependencies and integration points: it integrates with PM sleep, wakeup-source checks, power tracepoints, the global `initcall_debug`, and subsystems that cannot rely on normal device PM late in suspend. Callers must ensure callback data remains valid while registered.

Risks: callbacks run with one CPU online and interrupts disabled in suspend/resume, so sleeping or enabling interrupts is a serious bug. The suspend path does not hold `syscore_lock`, assuming registration is not racing with suspend. Failure unwind correctness depends on list ordering and callbacks being idempotent enough for partial suspend rollback.

Test signals: suspend/resume trace events, warnings about interrupt state, injected failing syscore suspend callbacks, and shutdown ordering tests are useful. Runtime coverage should check reverse suspend/shutdown order and forward resume order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/syscore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/test/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/base/test/Kconfig

Purpose: this Kconfig file declares optional test modules for the Linux device model area in `drivers/base/test`.

Important APIs, types, and functions: it defines `TEST_ASYNC_DRIVER_PROBE`, `DM_KUNIT_TEST`, and `DRIVER_PE_KUNIT_TEST`. `TEST_ASYNC_DRIVER_PROBE` is a tristate module gated by module support (`depends on m`). The two KUnit options depend on `KUNIT` and default to `KUNIT_ALL_TESTS` while remaining individually selectable when not building all KUnit tests.

Control flow: the symbols here are consumed by the adjacent Makefile to include `test_async_driver_probe.o`, root/platform device-model KUnit tests, and property-entry KUnit tests. There is no runtime code in this file.

State and persistence: build configuration state determines which test objects are compiled. No kernel runtime state is stored here.

Dependencies and integration points: the file plugs into the kernel Kconfig tree and exposes test coverage for asynchronous driver probing, device-managed resource release on base devices, platform-device matching, and property-entry software-node APIs.

Risks: `TEST_ASYNC_DRIVER_PROBE` being module-only is intentional because it runs timing-sensitive setup at module load; changing the dependency can make it run too early or as built-in unexpectedly. Incorrect defaults could either hide tests from `KUNIT_ALL_TESTS` or force unwanted test modules into normal builds.

Test signals: selecting the symbols should produce the expected objects from `drivers/base/test/Makefile`. KUnit listings should show `root-device-devm`, `platform-device-devm`, `platform-device-match`, and `property-entry` when the corresponding options are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/test/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/test/Makefile -->
# sources/distributed-fs/ceph-client/drivers/base/test/Makefile

Purpose: this Makefile maps the device-model test Kconfig symbols to concrete test objects.

Important APIs, types, and functions: `obj-$(CONFIG_TEST_ASYNC_DRIVER_PROBE)` adds `test_async_driver_probe.o`; `obj-$(CONFIG_DM_KUNIT_TEST)` adds `root-device-test.o` and `platform-device-test.o`; `obj-$(CONFIG_DRIVER_PE_KUNIT_TEST)` adds `property-entry-test.o`. It also applies `$(DISABLE_STRUCTLEAK_PLUGIN)` to `property-entry-test.o`.

Control flow: the kernel build system expands the conditional `obj-*` lines according to configuration. The file has no runtime control flow.

State and persistence: generated object inclusion is persistent only for the build. No runtime state is introduced.

Dependencies and integration points: it depends on the Kconfig symbols declared in the adjacent Kconfig file and on the kernel Kbuild infrastructure. The `DISABLE_STRUCTLEAK_PLUGIN` flag is an integration signal that property-entry tests use initializers or patterns incompatible with structleak instrumentation assumptions.

Risks: a mismatch between Kconfig symbol names and object names would silently omit tests. Removing the structleak flag could create false-positive build failures or altered test behavior.

Test signals: `make` with the relevant configs should compile exactly these objects. `modinfo` or KUnit run output can confirm module descriptions and suites are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/test/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/test/platform-device-test.c -->
# sources/distributed-fs/ceph-client/drivers/base/test/platform-device-test.c

Purpose: this KUnit file tests platform-device behavior in two areas: device-managed resource release when platform devices are unregistered, and null firmware-node/device matching helpers.

Important APIs, types, and functions: `struct test_priv` tracks probe/release completion, waitqueues, and the target device. Test helpers include `platform_device_devm_init`, `devm_device_action`, `devm_put_device_action`, `fake_probe`, and `fake_driver`. Test cases cover unprobed and probed platform devices, with and without an extra device reference, plus `platform_device_find_by_null_test`.

Control flow: each devm test allocates or registers a platform driver/device, attaches a devm action, unregisters the platform device, and waits up to `RELEASE_TIMEOUT_MS` for the action to mark completion. The probed variants register `fake_driver`, set driver data before adding the device, wait for probe completion, then validate release. The null-match test creates a KUnit-managed platform device and asserts that `of_find_device_by_node(NULL)`, bus find-by-null helpers, and `device_match_*` predicates all fail cleanly.

State and persistence: all test state is KUnit-allocated or KUnit-managed. Waitqueues provide deterministic synchronization with probe/release callbacks. The fake driver is registered only within the relevant test cases and unregistered before exit.

Dependencies and integration points: it integrates with KUnit, KUnit platform-device helpers, devres, platform bus registration, OF/fwnode/ACPI match helpers, and waitqueue scheduling.

Risks: timing-based waits can fail on a broken release path or a severely stalled environment. The tests intentionally hold references in two cases; if devm release regresses to wait for final put rather than unregister, these tests catch it. Fake driver global state means tests must keep registration/unregistration balanced.

Test signals: KUnit suite names are `platform-device-devm` and `platform-device-match`. Passing tests signal that platform unregister releases devm actions for probed and unprobed devices and that null match inputs are handled as nonmatches rather than accidental matches or crashes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/test/platform-device-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/test/property-entry-test.c -->
# sources/distributed-fs/ceph-client/drivers/base/test/property-entry-test.c

Purpose: this KUnit file validates the property-entry and software-node property API implemented by the device property/fwnode stack.

Important APIs, types, and functions: test cases are `pe_test_uints`, `pe_test_uint_arrays`, `pe_test_strings`, `pe_test_bool`, `pe_test_move_inline_u8`, `pe_test_move_inline_str`, and `pe_test_reference`. They use property macros such as `PROPERTY_ENTRY_U8`, `PROPERTY_ENTRY_U16_ARRAY`, `PROPERTY_ENTRY_STRING_ARRAY`, `PROPERTY_ENTRY_BOOL`, `PROPERTY_ENTRY_REF`, and `PROPERTY_ENTRY_REF_ARRAY`; fwnode APIs such as `fwnode_create_software_node`, `fwnode_property_read_*`, count helpers, and `fwnode_property_get_reference_args`; and software-node group registration.

Control flow: tests create software nodes with static property entries, read properties back through generic fwnode helpers, assert exact values and error behavior for missing or overlarge reads, then remove the software node. Copy tests call `property_entries_dup` and inspect `is_inline`, `value`, and `pointer` storage choices. Reference tests register two software nodes, create reference properties to them, resolve references with different argument counts and indexes, and unregister the group.

State and persistence: each test creates temporary software nodes and removes them before returning. Duplicated property entries are explicitly freed. Static referenced nodes exist for test duration and are registered as a group only inside the reference test.

Dependencies and integration points: this is the main local test signal for `drivers/base/swnode.c` property handling. It also exercises generic fwnode property readers and KUnit assertions.

Risks: tests intentionally rely on current element-count semantics, including counting a 64-bit property as four 16-bit elements and a 16-bit array as two 64-bit chunks when divisible. Inline-storage checks are sensitive to `struct property_entry` layout and copy policy. Reference tests must unregister on all successful paths to avoid contaminating later tests.

Test signals: the KUnit suite is `property-entry`. Passing tests signal correct scalar/array/string/bool read behavior, error returns for missing or overflowed properties, deep-copy behavior for inline and heap data, and software-node reference resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/test/property-entry-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/test/root-device-test.c -->
# sources/distributed-fs/ceph-client/drivers/base/test/root-device-test.c

Purpose: this KUnit file verifies that bus-less root devices run device-managed actions when unregistered, even when another reference to the device is held.

Important APIs, types, and functions: `struct test_priv` records release completion and the `struct device *`. Helpers include `root_device_devm_init`, `devm_device_action`, and `devm_put_device_action`. Test cases are `root_device_devm_register_unregister_test` and `root_device_devm_register_get_unregister_with_devm_test`.

Control flow: each test registers a root device with `root_device_register`, adds a devm action through `devm_add_action_or_reset`, unregisters the root device, and waits for `release_done` on a waitqueue. The reference-holding test calls `get_device()` and uses a devm action that performs the balancing `put_device()` before signaling completion.

State and persistence: test state is KUnit-allocated and short-lived. The root device exists only for each test case. Waitqueue synchronization prevents the test from relying only on immediate synchronous behavior.

Dependencies and integration points: this targets the base device core, root-device helpers, devres release semantics, reference counting, KUnit resource allocation, and waitqueues.

Risks: the test catches regressions where devm actions are incorrectly deferred until final reference drop rather than device unregister. A timeout indicates either broken release semantics or scheduling issues. The extra-reference test must not leak the reference if the devm action fails to run.

Test signals: the KUnit suite is `root-device-devm`. Passing tests confirm root-device unregister triggers devm actions in both normal and extra-reference cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/test/root-device-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/test/test_async_driver_probe.c -->
# sources/distributed-fs/ceph-client/drivers/base/test/test_async_driver_probe.c

Purpose: this loadable module tests the device core's asynchronous driver probing behavior by comparing registration latency for async-preferred and forced-synchronous platform drivers.

Important APIs, types, and functions: global atomics track `warnings`, `errors`, `timeout`, and `async_completed`. `test_probe` sleeps for `TEST_PROBE_DELAY`, validates timeout state, and checks NUMA locality for async probes. `async_driver` uses `PROBE_PREFER_ASYNCHRONOUS`; `sync_driver` uses `PROBE_FORCE_SYNCHRONOUS`. `test_platform_device_register_node`, `test_async_probe_init`, and `test_async_probe_exit` manage platform devices and drivers.

Control flow: module init registers one async device per online CPU, times async driver registration, expects it to return faster than half the probe delay, registers a second async device set and again expects fast registration, then registers synchronous devices/driver and expects registration paths to take at least the threshold. It then verifies async probes completed while synchronous work was running. Error paths unregister drivers/devices in reverse order and report accumulated warnings/errors. Module exit unregisters both drivers and fixed-size device arrays.

State and persistence: static arrays store up to `NR_CPUS * 2` async devices and two sync devices. Atomics persist for module lifetime. Platform devices may carry NUMA node information set from CPU topology.

Dependencies and integration points: it integrates with platform bus probing, async probe scheduling, NUMA APIs, CPU iteration, timekeeping, and module init/exit. It is module-only by Kconfig because it performs active timing tests at load time.

Risks: timing thresholds are environment-sensitive; slow systems or heavy load can produce false failures. The init path has a suspicious local use of `cpu_to_node(cpu)` after a `for_each_online_cpu` loop for the first synchronous device, relying on the loop variable value after iteration even though the device is registered with `NUMA_NO_NODE`. Exit loops unregister fixed array sizes and assume NULL-safe platform unregister behavior for entries not created after partial failures.

Test signals: successful module load logs fast async registration, slow sync registration, and "completed successfully". Failures increment atomics and return an error from module init, making the module load fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/test/test_async_driver_probe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/topology.c -->
# sources/distributed-fs/ceph-client/drivers/base/topology.c

Purpose: this file exposes CPU topology information through sysfs and adds a per-CPU capacity attribute.

Important APIs, types, and functions: macro-generated show/read functions expose IDs and cpumasks for package, die, cluster, core, thread siblings, core siblings, package CPUs, and optional book/drawer topology. `topology_add_dev`, `topology_remove_dev`, and `topology_sysfs_init` register the `topology` sysfs group through CPU hotplug. `DEFINE_PER_CPU(cpu_scale)` stores CPU capacity; `topology_set_cpu_scale`, `cpu_capacity_show`, and `register_cpu_capacity_sysctl` expose capacity.

Control flow: at `device_initcall`, `cpuhp_setup_state` installs callbacks that create/remove the `topology` attribute group on CPU devices. Text attributes use `sysfs_emit` with `topology_*` accessors. Binary cpumask attributes allocate a temporary cpumask, copy the topology mask, and print either bitmask or list format for partial reads. The `ppin` attribute is hidden when `topology_ppin()` returns zero. Capacity sysfs setup uses a dynamic CPU hotplug state to create/remove `cpu_capacity`.

State and persistence: CPU topology values come from architecture topology providers. `cpu_scale` is per-CPU state initialized to `SCHED_CAPACITY_SCALE` and mutated by `topology_set_cpu_scale`.

Dependencies and integration points: it depends on CPU device registration, CPU hotplug state management, cpumask printing helpers, architecture `topology_*` macros/functions, and scheduler capacity definitions.

Risks: sysfs callbacks assume `get_cpu_device(cpu)` succeeds in topology add/remove; the capacity path explicitly handles missing devices. Binary attributes allocate cpumasks per read, so memory allocation failure returns `-ENOMEM`. Optional topology macros change the visible ABI across architectures. Capacity hotplug setup ignores the return value from `cpuhp_setup_state`, always returning zero.

Test signals: sysfs entries under `/sys/devices/system/cpu/cpu*/topology/` and `cpu_capacity` are the main signals. CPU hotplug tests should verify group creation/removal and partial reads of cpumask/list binary attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/topology.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/trace.c -->
# sources/distributed-fs/ceph-client/drivers/base/trace.c

Purpose: this C file instantiates the device-core tracepoints declared in `drivers/base/trace.h`.

Important APIs, types, and functions: it defines `CREATE_TRACE_POINTS` and includes `"trace.h"`. There are no functions or exported symbols in this file; its role is tracepoint definition emission.

Control flow: compile-time macro expansion from `trace/define_trace.h` creates the tracepoint objects for the device-core `devres_log` event. Runtime emission happens from call sites elsewhere in the device core.

State and persistence: no explicit state is stored here. Generated tracepoint objects become part of the kernel image/module and feed tracing ring buffers when enabled.

Dependencies and integration points: it must be the single translation unit that defines `CREATE_TRACE_POINTS` for the local `trace.h`. It integrates with ftrace/perf tracepoint infrastructure and any devres code that calls the generated tracepoint.

Risks: adding another `CREATE_TRACE_POINTS` includer for the same header would cause duplicate definitions; removing this file would leave only declarations and fail linking for tracepoint references.

Test signals: a successful build with tracing enabled and the presence of the `dev:devres_log` event in tracing infrastructure validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/trace.h -->
# sources/distributed-fs/ceph-client/drivers/base/trace.h

Purpose: this header declares the device-core trace event used for devres logging.

Important APIs, types, and functions: it sets `TRACE_SYSTEM dev`, declares event class `devres`, and defines concrete event `devres_log`. The event captures a device name, device pointer, operation string, devres node pointer, resource name, and resource size.

Control flow: normal includers get declarations, while `drivers/base/trace.c` defines `CREATE_TRACE_POINTS` to emit the tracepoint. The print format renders device name, operation, node address, resource name, and byte count.

State and persistence: no direct state is stored. Event payloads are recorded only when tracing infrastructure is active.

Dependencies and integration points: it includes `linux/device.h`, `linux/tracepoint.h`, and `linux/types.h`, then includes `trace/define_trace.h` outside the guard with `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE trace`.

Risks: operation and resource name pointers must point to valid strings at trace time. Event field changes can affect tools consuming `dev:devres_log`. Include path macros must remain aligned with the file location.

Test signals: enable device trace events and perform devres allocation/release operations; `devres_log` records should show the expected operation and resource metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/transport_class.c -->
# sources/distributed-fs/ceph-client/drivers/base/transport_class.c

Purpose: this file implements generic transport class support on top of attribute containers, allowing subsystem transport-specific sysfs objects and attributes to be attached to generic devices.

Important APIs, types, and functions: exported APIs include `transport_class_register`, `transport_class_unregister`, `anon_transport_class_register`, `anon_transport_class_unregister`, `transport_setup_device`, `transport_add_device`, `transport_configure_device`, `transport_remove_device`, and `transport_destroy_device`. Internal callbacks include `transport_setup_classdev`, `transport_add_class_device`, `transport_configure`, `transport_remove_classdev`, and `transport_destroy_classdev`.

Control flow: class registration wraps `class_register`/`class_unregister`. Anonymous transport classes configure an attribute container with no class devices and dummy setup/remove functions. Device setup triggers matching containers to allocate/initialize class devices. Add makes class devices visible, then adds optional statistics and encryption sysfs groups. Configure invokes the transport class's `configure` callback. Remove invokes the class `remove`, removes optional groups, and deletes the class device. Destroy drops the class-device reference for non-anonymous classes.

State and persistence: transport class/container state is owned by callers. This file creates and removes sysfs visibility and class-device references through attribute-container infrastructure but does not maintain a separate global list.

Dependencies and integration points: it depends on `linux/attribute_container.h`, `linux/transport_class.h`, sysfs groups, class devices, and subsystem-specific transport classes such as SCSI transport layers.

Risks: lifecycle ordering matters: setup, add, configure, remove, and destroy are intentionally separate. Missing remove/destroy leaves sysfs objects or references behind. Error paths in add must remove partially added class devices and call transport `remove`. Anonymous transport classes rely on the dummy function sentinel to skip normal class-device deletion.

Test signals: subsystem tests should verify sysfs attributes appear after add, optional groups are removed on failure and removal, configure callbacks run after setup, and destroy releases references. Fault injection around `attribute_container_add_class_device` and `sysfs_create_group` is useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/transport_class.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/bcma/Kconfig

Purpose: this Kconfig file declares the Broadcom-specific AMBA (BCMA) bus subsystem and its optional host, core-driver, flash, GPIO, debugging, and SoC support options.

Important APIs, types, and functions: symbols include `BCMA_POSSIBLE`, `BCMA`, `BCMA_BLOCKIO`, `BCMA_HOST_PCI_POSSIBLE`, `BCMA_HOST_PCI`, `BCMA_HOST_SOC`, `BCMA_DRIVER_PCI`, `BCMA_DRIVER_PCI_HOSTMODE`, `BCMA_DRIVER_MIPS`, `BCMA_PFLASH`, `BCMA_SFLASH`, `BCMA_NFLASH`, `BCMA_DRIVER_GMAC_CMN`, `BCMA_DRIVER_GPIO`, and `BCMA_DEBUG`.

Control flow: this file influences the Makefile composition and conditional compilation in BCMA sources. `BCMA` is the main tristate menu. Host PCI support selects the PCI core driver by default when PCI is built in. MIPS support enables parallel/NAND flash defaults. GPIO support depends on `GPIOLIB` and selects `GPIOLIB_IRQCHIP` for SoC hosting.

State and persistence: configuration state determines which BCMA features are built. No runtime state is stored here.

Dependencies and integration points: it integrates with architecture features (`HAS_IOMEM`, `HAS_DMA`, `MIPS`), PCI, legacy PCI host-mode support, GPIOLIB, and compile-test coverage. The resulting symbols control the object list and inline fallbacks in `bcma_private.h`.

Risks: dependency mistakes can produce invalid combinations, such as MIPS-only host-mode support without needed PCI infrastructure or GPIO IRQ support without the IRQ chip helper. Defaults enable several features, so build coverage must account for more than the minimal bus core.

Test signals: configuration matrix builds should cover PCI-hosted, SoC-hosted, MIPS, GPIO, and debug combinations. The adjacent Makefile should include the expected object files for each symbol combination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/Makefile -->
# sources/distributed-fs/ceph-client/drivers/bcma/Makefile

Purpose: this Makefile composes the BCMA bus driver object from core files and feature-specific modules selected by Kconfig.

Important APIs, types, and functions: `bcma-y` always includes `main.o`, `scan.o`, `core.o`, `sprom.o`, `driver_chipcommon.o`, `driver_chipcommon_pmu.o`, and `driver_chipcommon_b.o`. Conditional additions cover pflash, sflash, nflash, PCI, PCIe2, PCI host mode, MIPS, GMAC common, GPIO, PCI host, and SoC host. `obj-$(CONFIG_BCMA)` links the aggregate `bcma.o`; `ccflags-$(CONFIG_BCMA_DEBUG)` adds `-DDEBUG`.

Control flow: Kbuild expands the object list into one composite BCMA module or built-in object. There is no runtime code in this file.

State and persistence: build state is derived entirely from Kconfig. No runtime state is stored here.

Dependencies and integration points: it must match prototypes and conditional fallbacks in `bcma_private.h` and Kconfig dependencies. Object ordering matters modestly for composite initialization/linking but most inter-file integration is via symbols.

Risks: missing an object for a selected feature causes unresolved symbols; including an object without its dependency can break builds on unsupported architectures. Debug flag behavior depends on all sources using `dev_dbg`/`bcma_debug` appropriately.

Test signals: build BCMA as built-in and module under multiple config combinations. Link success and expected symbol availability validate the Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/bcma_private.h -->
# sources/distributed-fs/ceph-client/drivers/bcma/bcma_private.h

Purpose: this private header defines BCMA-internal logging helpers, cross-file function prototypes, and conditional inline fallbacks for optional BCMA components.

Important APIs, types, and functions: logging macros `bcma_err`, `bcma_warn`, `bcma_info`, and `bcma_debug` prefix messages with bus number. It declares main bus lifecycle, scanning, SPROM, ChipCommon, ChipCommon B, PMU, flash, host PCI/SoC, PCI/PCIe2, watchdog, PCI host mode, MIPS, GMAC common, and GPIO functions. Conditional sections provide no-op or warning fallbacks when features such as `CONFIG_BCMA_PFLASH`, `CONFIG_BCMA_SFLASH`, `CONFIG_BCMA_NFLASH`, `CONFIG_BCMA_DRIVER_PCI`, `CONFIG_BCMA_DRIVER_PCI_HOSTMODE`, `CONFIG_BCMA_DRIVER_MIPS`, `CONFIG_BCMA_DRIVER_GMAC_CMN`, or `CONFIG_BCMA_DRIVER_GPIO` are disabled.

Control flow: compile-time configuration selects either external prototypes or inline fallback implementations. Runtime call sites can invoke common helpers without duplicating preprocessor conditionals.

State and persistence: no state is stored in the header. It exposes stateful structures defined in public BCMA headers, such as `struct bcma_bus`, `struct bcma_device`, and driver-specific structs.

Dependencies and integration points: it includes `linux/bcma/bcma.h` and `linux/delay.h`, and is included by the BCMA driver implementation files. It is the key boundary between optional object composition and unconditional call sites in the BCMA core.

Risks: fallback behavior must match call-site expectations. Some disabled-feature fallbacks log errors but return success for unsupported flash init, while GPIO init returns `-ENOTSUPP`; inconsistent conventions can surprise callers. Prototypes must stay synchronized with source definitions and Kconfig/Makefile conditions.

Test signals: all relevant Kconfig combinations should compile. Runtime signals include clear error logs when unsupported optional flash paths are detected and no unresolved symbols when features are disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/bcma_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/core.c -->
# sources/distributed-fs/ceph-client/drivers/bcma/core.c

Purpose: this file implements low-level BCMA core operations for reset, enable/disable, clock mode, PLL resource requests, and DMA translation.

Important APIs, types, and functions: exported functions are `bcma_core_is_enabled`, `bcma_core_disable`, `bcma_core_enable`, `bcma_core_set_clockmode`, `bcma_core_pll_ctl`, and `bcma_core_dma_translation`. Internal `bcma_core_wait_value` polls a DMP register until masked bits match a target or timeout.

Control flow: enable first disables the core with requested flags, then writes IO control with clock and force-gated clock, clears reset, and finally leaves clock plus flags enabled. Disable waits for reset status to clear, asserts reset, then writes IO control flags. Clock mode FAST sets `FORCEHT` and waits up to roughly 15 ms for `HAVEHT`; DYNAMIC clears the force bit. PLL control sets or clears external resource request bits and waits for status when enabling.

State and persistence: state is in hardware registers (`BCMA_IOCTL`, `BCMA_RESET_CTL`, `BCMA_RESET_ST`, `BCMA_CLKCTLST`, `BCMA_IOST`). No heap state is owned here. `core->irq` is not changed in this file.

Dependencies and integration points: it depends on public BCMA accessors (`bcma_aread32`, `bcma_awrite32`, `bcma_read32`, masks/set helpers), jiffies timing, udelay/usleep, and host type information. Higher-level BCMA drivers call these helpers before touching core-specific registers.

Risks: polling timeouts indicate hardware readiness failures; wrong delays or flag values can leave cores reset, clock-gated, or over-requesting PLL resources. DMA translation depends on host type and `BCMA_IOST_DMA64`; unsupported host types log an error and return none.

Test signals: hardware bring-up logs, core enable state checks, DMA-capable device operation, and timeout warnings are primary signals. Unit-style tests would need mocked register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/driver_chipcommon.c -->
# sources/distributed-fs/ceph-client/drivers/bcma/driver_chipcommon.c

Purpose: this file implements the BCMA ChipCommon core driver, handling common chip capabilities, flash detection, PMU handoff, GPIO register helpers, watchdog registration, LED timing, and MIPS UART discovery.

Important APIs, types, and functions: exported or cross-file APIs include `bcma_chipco_get_alp_clock`, `bcma_chipco_watchdog_register`, `bcma_core_chipcommon_early_init`, `bcma_core_chipcommon_init`, `bcma_chipco_watchdog_timer_set`, `bcma_chipco_irq_mask`, `bcma_chipco_irq_status`, `bcma_chipco_gpio_in`, `bcma_chipco_gpio_out`, `bcma_chipco_gpio_outen`, `bcma_chipco_gpio_control`, `bcma_chipco_gpio_intmask`, `bcma_chipco_gpio_polarity`, `bcma_chipco_gpio_pullup`, `bcma_chipco_gpio_pulldown`, and conditionally `bcma_chipco_serial_init`.

Control flow: early init initializes the GPIO spinlock, reads ChipCommon status/capability registers, initializes PMU early when present, detects flash for SoC hosts, and guards with `early_setup_done`. Full init calls early init, configures pullup/pulldown defaults for selected chips, initializes PMU and reports unimplemented power-control support, writes LED duty-cycle timing from SPROM or defaults, computes watchdog ticks per millisecond, and marks setup done. Watchdog registration builds `struct bcm47xx_wdt` callbacks and registers a platform device unless the chip has a known broken watchdog. Flash detection dispatches to serial, parallel, or NAND init based on capability bits and revision/chip ID. GPIO helpers use a shared masked-write helper under `gpio_lock` for mutable GPIO registers.

State and persistence: `struct bcma_drv_cc` stores capabilities, status, PMU state, flash descriptors, GPIO spinlock, watchdog platform device, serial port descriptors, and setup flags. Hardware registers persist the configured pullups, LED timer, IRQ masks, GPIO state, and watchdog value.

Dependencies and integration points: it integrates with PMU code, flash platform devices, bcm47xx watchdog platform data, GPIO driver code, SPROM data, MIPS serial init, BCMA register accessors, and SoC host detection.

Risks: chip-specific watchdog and clock quirks are easy to regress. Flash init is deliberately early and only prepares platform devices because full device registration is not safe yet. GPIO masked writes require locking to avoid read/modify/write races. Serial init is limited by ChipCommon revision and assumes UART register spacing.

Test signals: boot logs for flash detection, watchdog device registration, GPIO operation, serial console availability on MIPS, and absence of timeout/error logs during PMU/watchdog setup are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/driver_chipcommon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/driver_chipcommon_b.c -->
# sources/distributed-fs/ceph-client/drivers/bcma/driver_chipcommon_b.c

Purpose: this file supports the BCMA ChipCommon B unit, primarily exposing an MII management write path through an additional mapped register block.

Important APIs, types, and functions: `bcma_chipco_b_mii_write` writes an MII offset and value with busy-bit waits. `bcma_core_chipcommon_b_init` maps the secondary core address into `ccb->mii`; `bcma_core_chipcommon_b_free` unmaps it. Internal `bcma_wait_reg` polls an MMIO address until masked bits match.

Control flow: init is guarded by `setup_done`, then maps `core->addr_s[1]` for `BCMA_CORE_SIZE` and returns `-ENOMEM` on failure. MII writes write the control register, wait for busy clear, write command data, and wait again. Free unmaps only when a mapping exists.

State and persistence: runtime state is `ccb->setup_done` and `ccb->mii`. Hardware MII management registers persist the side effects of writes.

Dependencies and integration points: it uses raw `readl`/`writel`, `ioremap`/`iounmap`, BCMA logging, and ChipCommon B register offsets. Network/PHY-related code can use the exported MII write helper.

Risks: the wait helper logs timeout but `bcma_chipco_b_mii_write` does not propagate failure, so callers cannot distinguish timed-out hardware from success. Mapping the wrong secondary address would make all MII operations unsafe. Repeated init after failed mapping leaves `setup_done` set before mapping, preventing retry.

Test signals: hardware PHY configuration success and absence of MII timeout logs are the main signals. Fault tests should verify behavior when `ioremap` fails and when busy never clears.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/driver_chipcommon_b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/driver_chipcommon_nflash.c -->
# sources/distributed-fs/ceph-client/drivers/bcma/driver_chipcommon_nflash.c

Purpose: this file prepares BCMA ChipCommon NAND flash support and platform data for Broadcom NAND drivers.

Important APIs, types, and functions: it defines global platform device `bcma_nflash_dev`, alternate driver name `bcma_brcmnand`, partition probe list `bcm47xxpart`, and init function `bcma_nflash_init`.

Control flow: init first rejects unsupported chip/revision combinations, then verifies `BCMA_CC_CAP_NFLASH`. It marks NAND present, detects a booting NAND configuration for ChipCommon revision 38 with `BCMA_CC_CHIPST_5357_NAND_BOOT`, reads chip-select information from `BCMA_CC_NAND_CS_NAND_SELECT`, fills `brcmnand_info` with chip select, partition probe, ECC step size, and ECC strength, and renames the platform device to the alternate name. Finally it stores `&cc->nflash` as platform data without registering the platform device yet.

State and persistence: NAND state persists in `cc->nflash` and the global `bcma_nflash_dev.dev.platform_data`. The platform device object is static and later registration is expected elsewhere.

Dependencies and integration points: it integrates with `linux/platform_data/brcmnand.h`, Broadcom partition probing, BCMA ChipCommon status/capability registers, and later platform-device registration from BCMA host code.

Risks: static global platform device state can only represent one active BCMA NAND instance cleanly. Unsupported chips return errors; callers must not assume NAND exists from flash capability alone. Chip-select calculation uses `ffs(reg) - 1`, so a zero register would produce `-1` if reached.

Test signals: boot logs and MTD/NAND device registration are primary signals. Tests should cover unsupported board rejection, missing capability rejection, and correct platform data for NAND-booting rev-38 devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/driver_chipcommon_nflash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/driver_chipcommon_pflash.c -->
# sources/distributed-fs/ceph-client/drivers/bcma/driver_chipcommon_pflash.c

Purpose: this file prepares platform data and resources for ChipCommon-attached parallel flash on BCMA SoCs.

Important APIs, types, and functions: it defines `bcma_pflash_data` with `bcm47xxpart` partition probing, `bcma_pflash_resource` for memory-mapped flash, global platform device `bcma_pflash_dev` named `physmap-flash`, and init function `bcma_pflash_init`.

Control flow: init marks `cc->pflash.present`, reads `BCMA_CC_FLASH_CFG` to choose flash bus width 1 or 2, and sets the memory resource to `BCMA_SOC_FLASH2` through `BCMA_SOC_FLASH2 + BCMA_SOC_FLASH2_SZ`. Device registration is deferred to later BCMA code.

State and persistence: state is stored in `cc->pflash`, static `bcma_pflash_data.width`, and static resource start/end fields. Hardware state is not modified except for reading flash configuration.

Dependencies and integration points: it integrates with the MTD physmap flash driver, Broadcom partition parser, platform devices, and ChipCommon flash capability detection.

Risks: static platform data/resource objects limit clean multi-instance support. Resource end calculation appears inclusive-style but uses base plus size; if consumers expect inclusive end, this may represent one byte beyond the range depending on kernel convention in surrounding code. Width detection relies on `BCMA_CC_FLASH_CFG_DS`.

Test signals: successful registration of a `physmap-flash` platform device and MTD partitions from `bcm47xxpart` validate the path. Hardware tests should verify correct bus width and flash address range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/driver_chipcommon_pflash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/driver_chipcommon_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/bcma/driver_chipcommon_pmu.c

Purpose: this file implements BCMA ChipCommon PMU support: indirect PLL/chip/reg control access, crystal measurement, PLL initialization, resource masks, chip workarounds, ALP/bus/CPU clock derivation, and spur-avoidance PLL programming.

Important APIs, types, and functions: exported helpers include `bcma_chipco_pll_read`, `bcma_chipco_pll_write`, `bcma_chipco_pll_maskset`, `bcma_chipco_chipctl_maskset`, `bcma_chipco_regctl_maskset`, `bcma_chipco_bcm4331_ext_pa_lines_ctl`, `bcma_pmu_early_init`, `bcma_pmu_init`, `bcma_pmu_get_alp_clock`, `bcma_pmu_get_bus_clock`, `bcma_pmu_get_cpu_clock`, and `bcma_pmu_spuravoid_pllupdate`. Internal helpers compute xtal frequency, initialize PMU2 PLL target frequency, configure min/max resource masks, apply chip-specific workarounds, and calculate PLL outputs.

Control flow: early init selects a separate PMU core when AOB PMU is present, otherwise uses ChipCommon, reads PMU capability revision, and logs it. Full init toggles `NOILPONW` according to PMU revision, initializes PLL for specific chips, sets resource masks, and applies workarounds. Clock getters switch on chip IDs to return fixed ALP clocks or calculated PLL clocks. Spur-avoidance updates choose chip-family-specific PLL control register values, then set `PLL_UPD` and sometimes preserve/add `NOILPONW`.

State and persistence: PMU state is held in `cc->pmu.core` and `cc->pmu.rev`; most lasting state is hardware register programming in PMU PLL, chip-control, resource-mask, and control registers.

Dependencies and integration points: it depends on ChipCommon register accessors, public BCMA chip IDs/constants, the core `bcma_wait_value` helper, PMU register macros, and chip-specific radio/SoC bring-up expectations. MIPS clock code and watchdog timing consume CPU/bus/ALP clock helpers.

Risks: this file is highly chip-specific; wrong constants can destabilize clocks, power resources, wireless PHY behavior, or external PA lines. Several unknown-chip paths fall back to default clocks and warnings, which may be insufficient for new hardware. `BUG_ON` guards in PLL calculations can panic if called with invalid PLL index/divider. Spur-avoidance array indexing assumes valid `spuravoid` values.

Test signals: board boot stability, clock rate correctness, wireless operation, watchdog timing, and absence of PMU warnings are key signals. Hardware matrix testing across listed chip IDs is more important than synthetic tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/driver_chipcommon_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/driver_chipcommon_sflash.c -->
# sources/distributed-fs/ceph-client/drivers/bcma/driver_chipcommon_sflash.c

Purpose: this file detects and describes ChipCommon-attached serial flash devices and prepares a BCMA serial flash platform device.

Important APIs, types, and functions: it defines static resource `bcma_sflash_resource`, global platform device `bcma_sflash_dev`, flash descriptor type `struct bcma_sflash_tbl_e`, lookup tables for ST/M25P, SST, and Atmel flashes, command helper `bcma_sflash_cmd`, and init function `bcma_sflash_init`.

Control flow: `bcma_sflash_init` switches on flash capability type. For ST serial flash it issues deep-powerdown/release-ID commands, reads manufacturer/device IDs from `FLASHDATA`, and looks up SST or ST tables. It rejects unsupported ID `0x13` and unknown IDs. For Atmel serial flash it reads status ID bits and looks up the Atmel table. On success it fills `cc->sflash` block size, block count, total size, and present flag; logs the detected flash; sets the static resource end based on size; and stores platform data for later device registration.

State and persistence: state persists in `cc->sflash` and static platform-device/resource fields. The command helper changes ChipCommon flash control/address registers.

Dependencies and integration points: it uses BCMA ChipCommon register accessors, platform device infrastructure, static flash geometry tables, and later MTD/platform code that consumes `bcma_sflash_dev`.

Risks: unsupported flash IDs return `-ENOTSUPP`, so newer flash parts need table updates. `bcma_sflash_cmd` only logs timeout and returns void, so callers may proceed after a command timeout with invalid data. Static global platform device state limits multi-instance support. Resource end is computed from start plus size and should be checked against resource conventions.

Test signals: boot logs should identify flash name, size, block size, and block count. MTD registration and partition probing validate that the prepared platform data is consumed correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/driver_chipcommon_sflash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/driver_gmac_cmn.c -->
# sources/distributed-fs/ceph-client/drivers/bcma/driver_gmac_cmn.c

Purpose: this small file initializes the BCMA GBIT MAC COMMON core state.

Important APIs, types, and functions: it defines `bcma_core_gmac_cmn_init`, which initializes `gc->phy_mutex` in `struct bcma_drv_gmac_cmn`.

Control flow: the function is a straight-line initializer with no guards, allocations, or return value.

State and persistence: persistent state is the initialized mutex embedded in the GMAC common driver struct. No hardware registers are touched here.

Dependencies and integration points: it depends on `bcma_private.h`, public BCMA structures, and Linux mutex initialization. Ethernet/PHY code using the GMAC common core expects this mutex before serializing PHY access.

Risks: calling this repeatedly on an active mutex would be unsafe if users hold or wait on it. The simplicity means most correctness depends on callers invoking it before any PHY operations.

Test signals: network bring-up paths using the GMAC common core should not warn about uninitialized locking and should serialize PHY operations correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/driver_gmac_cmn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/driver_gpio.c -->
# sources/distributed-fs/ceph-client/drivers/bcma/driver_gpio.c

Purpose: this file registers a GPIO controller backed by BCMA ChipCommon GPIO registers and optionally wires it into the IRQ subsystem for SoC-hosted BCMA devices.

Important APIs, types, and functions: GPIO callbacks include `bcma_gpio_get_value`, `bcma_gpio_set_value`, `bcma_gpio_direction_input`, `bcma_gpio_direction_output`, `bcma_gpio_request`, and `bcma_gpio_free`. IRQ support includes `bcma_gpio_irq_unmask`, `bcma_gpio_irq_mask`, `bcma_gpio_irq_chip`, `bcma_gpio_irq_handler`, `bcma_gpio_irq_init`, and `bcma_gpio_irq_exit` when built for relevant SoCs. Exported integration functions are `bcma_gpio_init` and `bcma_gpio_unregister`.

Control flow: initialization fills `struct gpio_chip` callbacks, parent, fwnode, GPIO count based on chip ID, and base number policy. SoC/built-in configurations request the ChipCommon IRQ, clear interrupt masks, enable the ChipCommon GPIO interrupt bit, configure gpiochip IRQ metadata, and then register the gpiochip with `gpiochip_add_data`. GPIO request hands control to software, clears pulldown, and enables pullup. IRQ unmask samples current input and sets polarity so future edge-like changes are detected; handler computes `(input ^ polarity) & mask`, dispatches each set bit through the gpio IRQ domain, and updates polarity.

State and persistence: state is embedded in `cc->gpio` and hardware GPIO output, output-enable, control, pullup, pulldown, IRQ mask, and polarity registers. IRQ registration persists until unregister.

Dependencies and integration points: it integrates with gpiolib, optional gpiolib irqchip helpers, Linux IRQ handling, device firmware nodes, BCMA ChipCommon GPIO helpers, and SoC chip ID tables.

Risks: IRQ support is conditional and only meaningful for SoC hosts. The handler treats GPIO interrupts through polarity flipping; races around input changes and mask/polarity updates can lose or retrigger interrupts if hardware semantics differ. Absolute GPIO bases for SoC/built-in cases preserve legacy user-space expectations but can conflict if multiple controllers are misnumbered.

Test signals: gpiochip registration, line request/free, input/output toggling, pull configuration, and GPIO interrupt delivery validate behavior. Error-path tests should confirm IRQ is freed if gpiochip registration fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/driver_gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/driver_mips.c -->
# sources/distributed-fs/ceph-client/drivers/bcma/driver_mips.c

Purpose: this file initializes the BCMA Broadcom MIPS core support, including IRQ routing, CPU clock reporting, boot flash detection for NVRAM, serial setup, and chip-specific interrupt quirks.

Important APIs, types, and functions: exported APIs are `bcma_core_mips_irq`, `bcma_cpu_clock`, `bcma_core_mips_early_init`, and `bcma_core_mips_init`. Internal helpers include quirk detectors for BCM47162A0 and BCM5357B0, `bcma_core_mips_irqflag`, `bcma_core_mips_set_irq`, `bcma_core_mips_set_irq_name`, IRQ dump/print helpers, `bcma_boot_dev`, `bcma_core_mips_nvram_init`, and `bcma_fix_i2s_irqflag`. `enum bcma_boot_dev` classifies ROM, parallel, serial, NAND, and unknown boot sources.

Control flow: IRQ lookup reads or synthesizes an OOB IRQ flag, maps it through MIPS74K interrupt mask registers, and returns logical states for assigned, disabled, or unsupported. IRQ assignment clears old masks, evicts an existing user of a target IRQ to IRQ0 when needed, writes the new mask, and updates `dev->irq` to Linux IRQ number `irq + 2`. Early init initializes ChipCommon serial ports and NVRAM source based on boot device. Full init applies the I2S IRQ fixup, then routes IRQs for known chip families or falls back to `bcma_core_irq` and logs an unknown-device error.

State and persistence: state is in `mcore->early_setup_done`, `mcore->setup_done`, each `core->irq`, MIPS interrupt mask registers, OOB selector registers, and NVRAM initialization state when `CONFIG_BCM47XX` is enabled.

Dependencies and integration points: it depends on ChipCommon PMU clock helpers, BCMA core lookup, ChipCommon serial init, BCM47xx NVRAM initialization, public chip/core IDs, and MIPS interrupt register definitions.

Risks: IRQ routing is chip-table-driven and can break devices if a core ID/unit mapping is wrong. Some DMP register reads hang on known revisions, so quirk guards must be preserved. Unknown chip fallback logs an error and may still produce usable but suboptimal IRQs. NVRAM source detection depends on boot flash state and compile-time BCM47XX support.

Test signals: serial port availability, NVRAM load success, correct per-core IRQs, absence of interrupt storms, and debug IRQ dumps on supported chips are primary signals. Hardware tests should include the listed BCM4716/4748/5356/47162/53572/5357/4749/4706 families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/driver_mips.c -->
