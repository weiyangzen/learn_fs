# subset-b-001045 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/bus.c -->
## sources/distributed-fs/ceph-client/drivers/base/bus.c

### Purpose
`bus.c` implements Linux driver-core bus and subsystem registration for the Ceph client source tree. It owns `/sys/bus`, `/sys/devices/system`, bus-level sysfs attributes, bus device/driver lists, driver bind/unbind controls, subsystem interfaces, bus notifiers, and helper registration for system and virtual subsystems.

### Important APIs, Types, And Functions
The file centers on `struct subsys_private`, `struct bus_type`, `struct device_driver`, and kobject/kset/klist glue. Exported entry points include `bus_register()`, `bus_unregister()`, `bus_add_device()`, `bus_remove_device()`, `bus_add_driver()`, `bus_remove_driver()`, `bus_for_each_dev()`, `bus_find_device()`, `bus_for_each_drv()`, `bus_rescan_devices()`, `device_reprobe()`, `subsys_interface_register()`, `subsys_interface_unregister()`, `subsys_system_register()`, `subsys_virtual_register()`, `driver_find()`, `bus_get_dev_root()`, and `buses_init()`. Sysfs helpers include `bus_create_file()`, `bus_remove_file()`, driver `bind`, `unbind`, `uevent`, and bus `drivers_probe`, `drivers_autoprobe`, and `uevent`.

### Control Flow
`buses_init()` creates the global `/sys/bus` and `/sys/devices/system` ksets. `bus_register()` allocates a `subsys_private`, registers the bus kset, creates `devices` and `drivers` child ksets, initializes interface lists and klist iterators, adds probe control files, and installs bus attribute groups. `bus_add_device()` attaches bus attributes and sysfs links, then adds the device to the bus klist; `bus_probe_device()` performs initial probing and notifies registered `subsys_interface` callbacks. `bus_add_driver()` creates driver kobjects, adds the driver to the bus driver klist, optionally probes existing devices, adds module links and bind/unbind files, and leaves cleanup to error labels on early failures. Removal mirrors this order, detaching drivers and dropping the bus reference taken at add time.

### State, Persistence, And Dependencies
Persistent runtime state is held in global `bus_kset`, `system_kset`, and each bus's `subsys_private` ksets, klists, mutex, lockdep key, notifier chain, root device, and autoprobe flag. The persistent external surface is sysfs. Dependencies include kobject/kset/klist, sysfs, driver probing (`driver_attach()`, `device_attach()`), module links, driver core PM hooks, and `base.h` internals.

### Integration Points
This file is a foundation for all devices and drivers in the tree, including block, network, platform, CPU, and container/system subsystems. `subsys_system_register()` and `subsys_virtual_register()` are used by compatibility-style subsystems that want a root device under `/sys/devices/system` or `/sys/devices/virtual`. `bus_notify()` feeds bus notifier users, while `drivers_probe` and driver `bind`/`unbind` expose manual reprobe controls to userspace.

### Risks
Reference counting is subtle: `bus_to_subsys()` returns an incremented reference, and add paths intentionally retain an extra reference until the corresponding remove path, causing several valid double-`subsys_put()` sequences. Bind/unbind sysfs paths must cope with devices disappearing between lookup and attach. Probe controls require parent locking for buses with `need_parent_lock`. `bus_add_driver()` logs and continues after some sysfs group failures, so partial optional files can exist. `driver_find()` deliberately returns a raw driver pointer without preventing concurrent unregister; callers must provide exclusion.

### Test Signals
Useful signals include bus register/unregister leak checks, sysfs layout under `/sys/bus/<name>`, manual bind/unbind/probe behavior, `drivers_autoprobe=0` versus `1`, notifier ordering, subsystem interface add/remove callbacks for already-present devices, reprobe with parent locking, and fault injection through kset/sysfs allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/cacheinfo.c -->
## sources/distributed-fs/ceph-client/drivers/base/cacheinfo.c

### Purpose
`cacheinfo.c` detects per-CPU cache topology and publishes it through CPU sysfs devices. It supports firmware-derived cache data from Device Tree and ACPI, architecture fallback hooks, shared CPU maps, last-level-cache sharing queries, and CPU hotplug setup/teardown.

### Important APIs, Types, And Functions
Key state is the per-CPU `struct cpu_cacheinfo`, arrays of `struct cacheinfo`, per-CPU `cache` devices, and per-index cache devices. Public or weak-extension functions include `get_cpu_cacheinfo()`, `last_level_cache_is_valid()`, `last_level_cache_is_shared()`, `init_of_cache_level()`, `cache_setup_acpi()`, `early_cache_level()`, `init_cache_level()`, `populate_cache_leaves()`, `fetch_cache_info()`, `detect_cache_attributes()`, and `cache_get_priv_group()`. Hotplug integration is through `cacheinfo_cpu_online()`, `cacheinfo_cpu_pre_down()`, and `cpuhp_setup_state()`.

### Control Flow
Cache discovery starts with `fetch_cache_info()`, which prefers ACPI on ACPI systems, otherwise Device Tree, then falls back to architecture hooks. `detect_cache_attributes()` ensures cacheinfo storage exists, populates cache leaves via architecture or firmware hooks, fills firmware properties if needed, and computes shared CPU maps. Device Tree parsing counts cache leaves from `cache-size`, `i-cache-size`, `d-cache-size`, or fallback unified/split assumptions, then walks cache nodes and records size, line size, set count, associativity, type, firmware token, and optional cache ID. CPU hotplug online detection creates `cpuX/cache` and `indexN` devices; pre-down removes sysfs devices and clears shared maps.

### State, Persistence, And Dependencies
State persists for the life of the kernel in per-CPU `ci_cpu_cacheinfo`; the file comments note cacheinfo memory is never freed after allocation, even across hotplug. Runtime sysfs state is tracked in `ci_cache_dev`, `ci_index_dev`, and `cache_dev_map`. `coherency_max_size` and per-CPU data-slice size are updated from discovered leaves. Dependencies include OF and ACPI cache description APIs, CPU hotplug, cpumasks, sysfs device helpers, architecture weak overrides, and `setup_pcp_cacheinfo()`.

### Integration Points
Consumers use `last_level_cache_is_shared()` and `get_cpu_cacheinfo()` to reason about CPU topology. Userspace observes `/sys/devices/system/cpu/cpuX/cache/indexY/` attributes such as `type`, `level`, `size`, `shared_cpu_map`, `shared_cpu_list`, and policy fields. Architecture code can override the weak discovery hooks or add a private sysfs attribute group per cache leaf.

### Risks
Firmware descriptions may be incomplete or inconsistent; the code falls back to architecture data only under specific conditions and treats invalid OF hierarchy ordering as errors. Shared-map correctness depends on cache IDs or stable firmware tokens; the fallback assumption marks all non-L1 caches as system-wide shared. `cache_private_groups` is a static mutable array used to splice one private group, so it assumes compatible use across leaves. CPU hotplug paths must keep sysfs devices, shared maps, and per-CPU slice sizes synchronized.

### Test Signals
High-value tests include DT systems with unified and split L1 caches, multi-level cache nodes, missing cache-size fallback, ACPI PPTT cache data, architecture fallback-only systems, CPU online/offline cycles, shared cache maps across sibling CPUs, last-level cache query correctness, hidden sysfs attributes for zero-valued fields, and allocation failure in cacheinfo or index-device creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/cacheinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/class.c -->
## sources/distributed-fs/ceph-client/drivers/base/class.c

### Purpose
`class.c` implements driver-core device classes under `/sys/class`. It registers class ksets, class attribute files, class device iteration, class interfaces, dynamically-created classes, compatibility links, and class registration state queries.

### Important APIs, Types, And Functions
The file uses `struct class`, `struct class_interface`, `struct class_dev_iter`, `struct class_compat`, and `struct subsys_private`. Important exported functions are `class_register()`, `class_unregister()`, `class_create()`, `class_destroy()`, `class_create_file_ns()`, `class_remove_file_ns()`, `class_dev_iter_init()`, `class_dev_iter_next()`, `class_dev_iter_exit()`, `class_for_each_device()`, `class_find_device()`, `class_interface_register()`, `class_interface_unregister()`, `show_class_attr_string()`, `class_compat_register()`, `class_compat_unregister()`, `class_compat_create_link()`, `class_compat_remove_link()`, `class_is_registered()`, and `classes_init()`.

### Control Flow
`classes_init()` creates the top-level `/sys/class` kset. `class_register()` validates namespace callback consistency, allocates `subsys_private`, initializes the class device klist and interface list, registers the class kset, and creates class attribute groups. Class attributes route sysfs show/store through `class_attr_show()` and `class_attr_store()`. Iterators use the class klist and take device references through klist callbacks. Interface registration adds the interface under the class mutex and immediately invokes `add_dev()` for existing class devices; unregister removes the interface and invokes `remove_dev()` for current devices.

### State, Persistence, And Dependencies
Global `class_kset` anchors all class ksets. Each class owns a `subsys_private` with a device klist, interface list, glue directory kset, namespace operations, lockdep key, and mutex. Dynamic classes created by `class_create()` are freed through the `class_create_release()` callback when unregistered. The file depends on kobjects, sysfs, klist, class and device internals, and namespace ownership callbacks.

### Integration Points
`core.c` uses class private state when placing class devices in sysfs, creating class symlinks, iterating class interfaces, and changing sysfs ownership. Device classes such as `devlink`, block, net, tty, and char-device classes depend on these APIs to expose class-level and device-level sysfs views. Compatibility classes support migration from class devices to bus devices while preserving legacy userspace paths.

### Risks
As with bus code, reference handling is nontrivial: `class_to_subsys()` increments a reference, interface registration keeps a reference until unregister, and iterator init also stores a reference that must be released by `class_dev_iter_exit()`. `class_for_each_device()` and `class_find_device()` call `class_to_subsys()` and then `class_dev_iter_init()`, so their paired `subsys_put()` calls are intentional. Namespace callbacks must be provided as a matched pair or class registration fails. `class_is_registered()` is only momentary and can race with unregister.

### Test Signals
Test class lifecycle with normal and dynamic classes, class group creation failures, namespaced class attributes, iterator start/type filtering, `class_find_device()` reference ownership, interface callbacks for pre-existing and removed devices, compatibility symlink creation/removal, and registration state checks under concurrent unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/class.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/component.c -->
## sources/distributed-fs/ceph-client/drivers/base/component.c

### Purpose
`component.c` implements the component helper for aggregate devices whose logical driver is assembled from multiple independently-probed component devices. This is common for SoC display and media stacks where no single bus-level abstraction captures the hardware relationship.

### Important APIs, Types, And Functions
Internal types are `struct component_match_array`, `struct component_match`, `struct aggregate_device`, and `struct component`. Global state is protected by `component_mutex` and stored in `component_list` and `aggregate_devices`. Exported helpers include `component_match_add_release()`, `component_match_add_typed()`, `component_master_add_with_match()`, `component_master_del()`, `component_master_is_bound()`, `component_bind_all()`, `component_unbind_all()`, `component_add_typed()`, `component_add()`, `component_del()`, and compare/release helpers for OF nodes, devices, and device names.

### Control Flow
Aggregate drivers build a devres-managed match list, then call `component_master_add_with_match()`. Registration trims the match array, creates an `aggregate_device`, adds it to the aggregate list, and tries to bind immediately. Component drivers call `component_add()` or `component_add_typed()`, which adds a `component` to the component list and attempts to bring up any now-complete aggregate. `find_components()` binds match entries to available component objects, `try_to_bring_up_aggregate_device()` calls the aggregate `bind()` once all matches are present, and aggregate `bind()` normally calls `component_bind_all()` to invoke per-component `bind()` callbacks in match order. Removal tears down the aggregate first, unbinding components in reverse order.

### State, Persistence, And Dependencies
State is entirely in-memory and process-lifetime: match records point to compare data and matched components, components point back to an aggregate, and aggregate devices track `bound`. Debugfs optionally exposes aggregate/component status under `device_component`. The file depends on device core devres groups for rollback, OF references, debugfs, mutex/list primitives, and component public headers.

### Integration Points
Drivers integrate by adding match entries from their parent device, registering the aggregate master, and using `component_bind_all()`/`component_unbind_all()` inside master callbacks. Component drivers register from probe and unregister from remove. The helper does not solve runtime PM or suspend dependencies; the file explicitly points users to device links for that behavior.

### Risks
The global mutex must be held across matching and aggregate bind/unbind expectations; `component_bind_all()` and `component_unbind_all()` warn if called without it. Duplicate component matches are tracked and skipped during bind/unbind to avoid double-calling a component. Error rollback relies on devres groups opened on both the aggregate parent and component device. A failed aggregate bind removes only the new aggregate; a failed component add detaches the component from any match and frees it. Compare-data release is tied to parent devres lifetime, so callers must use the release variant for referenced objects such as OF nodes.

### Test Signals
Test aggregate registration before and after components, missing component defer behavior, duplicate match entries, typed subcomponents, bind failure rollback, reverse-order unbind, component removal while bound, master removal while bound, debugfs status, OF node reference release, and concurrent add/remove serialization under `component_mutex`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/component.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/container.c -->
## sources/distributed-fs/ceph-client/drivers/base/container.c

### Purpose
`container.c` defines the small system bus used for container devices under the driver core. It provides a bus type named `container` and registers it as a system subsystem.

### Important APIs, Types, And Functions
The main exported object is `container_subsys`, a `struct bus_type` with `.name`, `.dev_name`, `.online`, and `.offline`. `trivial_online()` always succeeds. `container_offline()` converts `struct device` to `struct container_dev` and delegates to the optional `container_dev.offline` callback. `container_dev_init()` registers the subsystem with `subsys_system_register()`.

### Control Flow
At init time, `container_dev_init()` calls `subsys_system_register(&container_subsys, NULL)`. That creates the bus and root system device through `bus.c` helpers. Online requests succeed unconditionally. Offline requests only do work if the concrete container device supplies an `.offline` method; otherwise they succeed.

### State, Persistence, And Dependencies
The file has no private mutable state. Persistent state is created by the driver core when registering `container_subsys`, including sysfs directories and the root device. Dependencies are `linux/container.h`, `base.h`, and the bus/subsystem registration path in `bus.c`.

### Integration Points
Container device providers use the `container_subsys` bus and `struct container_dev` callbacks to expose devices under the system-device hierarchy. The generic `online` and `offline` sysfs attribute handling comes from `core.c` when the bus supports these callbacks.

### Risks
The online path is intentionally a no-op, so any device-specific reactivation work must live elsewhere or be unnecessary. Offline behavior depends entirely on the optional container callback and returns success when none is provided. Registration failure is logged but not recovered in this file.

### Test Signals
Signals include successful `/sys/devices/system/container` registration, offline callback invocation and return propagation, no-op online success, behavior without an offline callback, and init-time error logging if subsystem registration fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/container.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/core.c -->
## sources/distributed-fs/ceph-client/drivers/base/core.c

### Purpose
`core.c` is the central Linux driver model implementation for devices. It handles device initialization, registration, sysfs placement, device links and firmware-node dependencies, hotplug online/offline, class/bus integration, uevents, devtmpfs nodes, device movement and renaming, shutdown ordering, logging helpers, and firmware node attachment.

### Important APIs, Types, And Functions
Major exported APIs include `device_initialize()`, `device_add()`, `device_register()`, `device_del()`, `device_unregister()`, `get_device()`, `put_device()`, `device_for_each_child()`, `device_find_child()`, `devices_init()`, `device_offline()`, `device_online()`, `device_create()`, `device_create_with_groups()`, `device_destroy()`, `device_rename()`, `device_move()`, `device_change_owner()`, `device_shutdown()`, logging helpers such as `dev_err_probe()`, firmware-node helpers such as `set_primary_fwnode()`, `device_add_of_node()`, and match helpers such as `device_match_name()` and `device_match_fwnode()`. Device-link APIs include `device_link_add()`, `device_link_del()`, `device_link_remove()`, `device_links_check_suppliers()`, and driver-bound/cleanup helpers.

### Control Flow
`devices_init()` creates `/sys/devices`, `/sys/dev/{block,char}`, and a device-link workqueue. `device_initialize()` prepares kobject, locks, devres, PM, NUMA, DMA, SWIOTLB, and device-link lists. `device_add()` allocates private state if needed, assigns a name, resolves the parent or class glue directory, adds the kobject, creates uevent/class/device attributes, adds the device to its bus, PM, devtmpfs, class, parent, and firmware-link structures, emits add notifications, marks it ready to probe, and calls `bus_probe_device()`. `device_del()` reverses the registration path: marks dead, unhooks fwnode, notifies removal, drops PM/sysfs/devtmpfs/class/bus/deferred-probe/device-link state, releases devres, emits remove uevent, deletes the kobject, and cleans glue directories.

### State, Persistence, And Dependencies
Global state includes `devices_kset`, `/sys/dev` kobjects, `device_hotplug_lock`, firmware-link lists, device-link locks/SRCU/workqueue, deferred sync-state lists, and `fw_devlink` policy flags from early parameters. Per-device persistent state is in `struct device`, `struct device_private`, devres lists, PM state, kobject, class/bus memberships, fwnode/of_node links, and supplier/consumer device links. Dependencies span sysfs/kobject, PM runtime and system sleep, bus/class code, devtmpfs, ACPI, OF, software nodes, DMA/SWIOTLB, cpufreq, notifier chains, and deferred probing.

### Integration Points
Every registered device in the Ceph client kernel source tree passes through these APIs. `bus.c` supplies bus add/remove/probe hooks; `class.c` supplies class directories and interface callbacks; `component.c` and other subsystems rely on devres and device references. Firmware graph dependencies are converted into device links so suppliers probe before consumers and `sync_state()` is delayed until active consumers are ready. Userspace sees the result through sysfs attributes, uevents, devtmpfs nodes, and `/sys/class/devlink` link devices.

### Risks
The largest risk is ordering: add/remove paths must unwind in the reverse order of side effects, while leaving objects reference-counted until final `put_device()`. Device links combine mutexes, SRCU, PM-runtime references, and delayed work; incorrect flag combinations can create probe deadlocks, missed supplier synchronization, or leaked PM references. Firmware dependency cycle relaxation is complex and deliberately conservative. Glue directory cleanup has a documented race that is mitigated with `gdp_mutex` and kobject reference checks. `device_rename()` is explicitly racy and discouraged for new code. `get_dev_from_fwnode()` warns about possible UAF unless callers can guarantee the associated device cannot disappear concurrently.

### Test Signals
Useful tests include device add/remove with all combinations of bus, class, type groups, devt, OF node, and parent; fault-injection of each `device_add()` error label; class glue directory concurrent add/remove; device-link add/remove flag validation; supplier probe deferral and unblocking; firmware dependency cycles; sync-state timeout and strict modes; CPU/device hotplug online/offline sysfs; devtmpfs node creation/removal; move/rename rollback; shutdown ordering from the tail of `devices_kset`; and probe error logging for `-EPROBE_DEFER`, `-ENOMEM`, and fatal errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/core.c -->
