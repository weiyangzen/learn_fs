# subset-b-001047 Research

Grouped research for Linux driver-core files under `sources/distributed-fs/ceph-client/drivers/base`. Each section preserves the original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/memory.c -->
# sources/distributed-fs/ceph-client/drivers/base/memory.c

## Purpose
Implements the driver-core sysfs representation of sparse physical memory as `/sys/devices/system/memory/memoryN`, plus memory hotplug control, memory-block lookup, memory-block-to-node linking support, memory groups, and optional memory-failure controls.

## Important APIs, Types, And Functions
Exports memory hotplug entry points such as `register_memory_notifier()`, `unregister_memory_notifier()`, `memory_notify()`, `memory_block_size_bytes()`, `create_memory_block_devices()`, `remove_memory_block_devices()`, `walk_memory_blocks()`, `for_each_memory_block()`, and memory group APIs `memory_group_register_static()`, `memory_group_register_dynamic()`, and `memory_group_unregister()`. Internal state is organized around `struct memory_block` devices stored in the `memory_blocks` xarray and `struct memory_group` objects stored in the marked `memory_groups` xarray. Sysfs attributes expose `phys_index`, `state`, `phys_device`, `removable`, optional `valid_zones`, root-level `block_size_bytes`, `auto_online_blocks`, hotplug `probe`, crash-hotplug support, and memory-failure page offlining.

## Control Flow
Boot initialization through `memory_dev_init()` validates the architecture block size, registers the `memory` subsystem bus, calculates `sections_per_block`, and creates one memory-block device per present sparsemem block. Hot-add flows call `create_memory_block_devices()`, which checks block alignment, creates offline blocks with `add_memory_block()`, registers devices, and rolls back created blocks on failure. Sysfs writes to `state` parse `online`, `online_kernel`, `online_movable`, or `offline`, take the device hotplug sysfs lock, and call `device_online()` or `device_offline()`. Bus `.online`/`.offline` callbacks serialize through the device lock, transition `mem->state`, and call `online_pages()` or `offline_pages()` under `mem_hotplug_begin()`/`mem_hotplug_done()`.

## State And Persistence
State persists in kernel objects and sysfs, not on disk. `mem->state`, `online_type`, `nid`, `zone`, `altmap`, `group`, and hardware-poison counters determine whether a block can be onlined/offlined and where it belongs. The `memory_blocks` xarray is the fast lookup index; `memory_groups` tracks static and dynamic hotplug grouping and uses `MEMORY_GROUP_MARK_DYNAMIC` for iteration. Memory block devices hold references via `get_device()` and are released by `memory_block_release()`, which warns if altmap cleanup was missed.

## Dependencies And Integration
Depends on SPARSEMEM, memory hotplug core (`online_pages()`, `offline_pages()`, `zone_for_pfn_range()`), NUMA node support, memblock boot discovery, sysfs, notifier chains, xarray, memory failure, kexec crash hotplug, and architecture hooks such as `memory_block_size_bytes()` and `arch_get_memory_phys_device()`. `node.c` calls `memory_block_add_nid_early()` and `unregister_memory_block_under_nodes()` to maintain memory-node links.

## Risks And Test Signals
Main risks are hotplug locking mistakes, reference leaks around xarray/device lookup, partial hot-add rollback failures, incorrect zone selection for blocks spanning zones or nodes, altmap accounting mismatches, and ABI regressions in long-lived sysfs files. Test signals include memory hotplug on/offline tests, NUMA sysfs link checks, memory-failure injection, `valid_zones` output, dynamic/static memory group lifecycle tests, and boot-time creation of all present memory blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/memory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/module.c -->
# sources/distributed-fs/ceph-client/drivers/base/module.c

## Purpose
Maintains sysfs relationships between registered device drivers and the modules or built-in module kobjects that provide them.

## Important APIs, Types, And Functions
`module_add_driver()` creates a `module` link under the driver's private kobject and a reverse link under `/sys/module/<module>/drivers/<bus>:<driver>`. `module_remove_driver()` removes both links. `make_driver_name()` creates the stable reverse-link name, while `module_create_drivers_dir()` lazily creates the module's `drivers` directory under a static mutex.

## Control Flow
Driver registration calls `module_add_driver()` with the owning module and driver. If the driver is built in and carries `mod_name`, the function looks up or creates a built-in module kobject and stores it in `drv->p->mkobj`. It then creates the driver-to-module symlink, allocates the reverse name, creates the module `drivers` directory if needed, and adds the reverse symlink. Each failure path unwinds the links and allocated name created so far. Removal is symmetric and tolerates NULL drivers and missing module kobjects.

## State And Persistence
The only persistent state is live sysfs topology and, for built-in drivers, the cached `drv->p->mkobj` pointer. No disk state is written. Lifetime is governed by kobject references and the driver's private object lifetime.

## Dependencies And Integration
Uses driver private kobjects from the driver core, module kobjects from the module subsystem, sysfs link APIs, `lookup_or_create_module_kobject()`, and `drv->bus->name` for namespace-stable reverse names.

## Risks And Test Signals
Risks include stale or duplicate sysfs links, unbalanced kobject references for built-in module kobjects, and inconsistent cleanup when reverse-link creation fails. Test signals are driver registration/unregistration with loadable modules and built-in `mod_name` drivers, sysfs link presence under both driver and module directories, and repeated unload/reload without leaked links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/node.c -->
# sources/distributed-fs/ceph-client/drivers/base/node.c

## Purpose
Implements `/sys/devices/system/node` devices, NUMA node attributes, CPU and memory-block links, heterogeneous-memory access metadata, memory-side cache metadata, and node state root attributes.

## Important APIs, Types, And Functions
Exports `register_node_notifier()`, `unregister_node_notifier()`, `node_notify()`, `node_set_perf_attrs()`, `node_update_perf_attrs()`, `register_cpu_under_node()`, `unregister_cpu_under_node()`, `register_memory_node_under_compute_node()`, `register_memory_blocks_under_node_hotplug()`, `unregister_memory_block_under_nodes()`, `register_node()`, and `unregister_node()`. Important local types are `struct node_access_nodes` for ranked initiator/target relationships and `struct node_cache_info` for memory-side cache levels. `node_devices[MAX_NUMNODES]` is the global node device table.

## Control Flow
`node_dev_init()` registers the `node` subsystem, creates devices for all online nodes, links present CPUs, initializes optional caches, and links boot memory blocks to nodes by walking memblock regions. `register_node()` allocates a node device, registers standard sysfs groups, installs hugetlb/compaction/reclaim node hooks, and links CPUs already assigned to the node. Hotplug memory registration walks memory blocks in a PFN range and creates bidirectional node-memory sysfs links. HMEM paths lazily create `accessN` devices and populate initiator/target links and performance attributes.

## State And Persistence
State is live kernel/sysfs state: `node_devices[]`, per-node access lists, per-node cache lists, sysfs links to CPU and memory block devices, and root node-state masks such as `possible`, `online`, `has_memory`, and `has_cpu`. Performance coordinates and cache attributes persist only as in-memory device attributes until node removal.

## Dependencies And Integration
Integrates with NUMA topology, cpumasks, memblock, memory hotplug, memory block lookup from `memory.c`, hugetlb, compaction, reclaim, VM statistics, mempolicy HMEM performance data, runtime PM no-callback devices, and optional architecture node attribute groups.

## Risks And Test Signals
Risks include dangling sysfs links during CPU/memory/node hotplug, missing `put_device()` on memory block lookup, duplicate cache level devices, incorrect handling of memory blocks spanning multiple nodes, and drift in meminfo/vmstat formatting. Test signals include NUMA sysfs layout checks, CPU hotplug link creation/removal, memory hotplug node links, HMEM initiator/target link tests, cache attribute registration tests, and validation of node state masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/node.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/physical_location.c -->
# sources/distributed-fs/ceph-client/drivers/base/physical_location.c

## Purpose
Adds optional ACPI physical-location metadata to devices and exposes it through a `physical_location` sysfs attribute group.

## Important APIs, Types, And Functions
`dev_add_physical_location()` is the core entry point. It reads ACPI `_PLD` data into `struct acpi_pld_info`, allocates `dev->physical_location`, and copies panel, vertical position, horizontal position, dock, and lid flags. Sysfs show functions map enum values to strings for `panel`, `vertical_position`, `horizontal_position`, `dock`, and `lid`. `dev_attr_physical_location_group` publishes these attributes under a named group.

## Control Flow
Callers first check device physical location support through `dev_add_physical_location()`. The function refuses devices without an ACPI companion or without retrievable PLD data, allocates the driver-core physical-location object, copies fields, frees ACPI memory, and returns whether metadata was installed. Sysfs reads assume `dev->physical_location` is present and translate stored values without re-querying firmware.

## State And Persistence
The copied physical-location fields live in `dev->physical_location` for the lifetime of the device. They are derived from firmware and are not persisted locally. The sysfs group provides read-only ABI state to userspace.

## Dependencies And Integration
Depends on ACPI companion discovery, `acpi_get_physical_device_location()`, ACPI memory freeing, driver core device storage, sysfs, and `str_yes_no()` for boolean attributes. The paired header supplies no-op stubs when ACPI is disabled.

## Risks And Test Signals
Risks include assuming sysfs attributes are installed only when `dev->physical_location` is non-NULL, firmware enum values outside known ranges, and memory leaks if callers do not release the device field in core teardown. Test signals are ACPI devices with valid and missing `_PLD`, sysfs string output for all enum cases, and non-ACPI builds using the stubbed header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/physical_location.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/physical_location.h -->
# sources/distributed-fs/ceph-client/drivers/base/physical_location.h

## Purpose
Provides the driver-core internal interface for optional physical-location support, with ACPI-backed declarations when enabled and harmless stubs when disabled.

## Important APIs, Types, And Functions
When `CONFIG_ACPI` is enabled, declares `dev_add_physical_location()` and `dev_attr_physical_location_group`. Otherwise it defines `dev_add_physical_location()` as an inline function returning `false` and provides an empty `attribute_group`.

## Control Flow
Including code can call `dev_add_physical_location()` and reference the attribute group without surrounding every use in ACPI preprocessor conditionals. The compiled behavior is selected at build time.

## State And Persistence
The header stores no runtime state. In non-ACPI builds, the empty static attribute group avoids exposing physical-location sysfs files.

## Dependencies And Integration
Includes `<linux/device.h>` for `struct device` and `struct attribute_group`. It pairs directly with `physical_location.c` and the driver-core code that installs optional device groups.

## Risks And Test Signals
Risks are mostly ABI and build-integration issues: the empty group must remain safe for users that iterate attribute groups, and declarations must match `physical_location.c`. Test signals are ACPI and non-ACPI build coverage plus device registration paths that include the group unconditionally.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/physical_location.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/pinctrl.c -->
# sources/distributed-fs/ceph-client/drivers/base/pinctrl.c

## Purpose
Bridges the driver core and pinctrl subsystem by binding pinctrl handles and selecting initial/default pin states before a device probes.

## Important APIs, Types, And Functions
`pinctrl_bind_pins()` allocates `dev->pins`, obtains a managed pinctrl handle, resolves `default`, optional `init`, and optional PM `sleep`/`idle` states, selects `init` when present or `default` otherwise, and cleans up when pinctrl data is absent or invalid.

## Control Flow
The function returns immediately for reused OF nodes. Otherwise it allocates managed pin state storage, calls `devm_pinctrl_get()`, looks up the default state, optionally looks up an init state, and selects the state to apply before probe. With PM enabled, it records optional sleep and idle states for later PM transitions. Cleanup drops the pinctrl handle, frees `dev->pins`, and maps ordinary absence such as `-ENOENT` to success while preserving `-EPROBE_DEFER` and `-EINVAL`.

## State And Persistence
State lives in `dev->pins` and devres-managed pinctrl resources. Selected pin state affects hardware mux/configuration, while sleep/idle/default/init pointers are cached for later device-core PM operations.

## Dependencies And Integration
Depends on pinctrl consumer APIs, device-tree state naming conventions, devres allocation, and driver-core probe sequencing. It follows pinctrl semantics defined in `<linux/pinctrl/pinctrl-state.h>`.

## Risks And Test Signals
Risks include masking real pinctrl errors as optional absence, failing to preserve probe deferral, leaving `dev->pins` partially initialized, and incorrect state selection for devices that require `init` rather than `default`. Test signals are probe deferral tests, devices with no pinctrl, devices with default-only and init/default states, PM sleep/idle pin state transitions, and reused OF node cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/pinctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/platform-msi.c -->
# sources/distributed-fs/ceph-client/drivers/base/platform-msi.c

## Purpose
Provides MSI domain setup and teardown helpers for platform devices using the generic MSI parent-domain model, with migration compatibility for older platform MSI users.

## Important APIs, Types, And Functions
Exports `platform_device_msi_init_and_alloc_irqs()` and `platform_device_msi_free_irqs_all()`. The local `platform_msi_template` supplies an irq chip named `pMSI`, parent mask/unmask operations, `platform_msi_write_msi_msg()` as the write-message indirection, a descriptor setter, and `DOMAIN_BUS_DEVICE_MSI`.

## Control Flow
Initialization validates that the device has a parent MSI domain and a write-message callback, creates a managed child MSI domain with fixed vector count, stores the write callback as domain data, and allocates interrupts over the range `0..nvec-1`. Freeing releases all interrupts from `MSI_DEFAULT_DOMAIN` and removes the device IRQ domain.

## State And Persistence
State is device-managed MSI domain state and allocated MSI descriptors/interrupt mappings. Hardware IRQ numbers are derived from `desc->msi_index`, and message programming is delegated through the stored callback.

## Dependencies And Integration
Depends on generic MSI domain APIs, irqdomain, `struct msi_desc`, irq chip parent operations, and platform device parent MSI domains installed by architecture or firmware-specific code.

## Risks And Test Signals
Risks include failing when no parent domain exists, leaking device IRQ domains if allocation succeeds partially, incorrect vector range handling when `nvec` is zero, and callback mismatch during message writes. Test signals are platform MSI allocation/free tests, interrupt delivery on all allocated vectors, devres/device removal cleanup, and platforms migrated from legacy platform MSI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/platform-msi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/platform.c -->
# sources/distributed-fs/ceph-client/drivers/base/platform.c

## Purpose
Implements the Linux platform pseudo-bus: resource and IRQ lookup helpers, platform device allocation/registration/unregistration, platform driver registration/probing, bus matching/uevents, DMA setup, PM callbacks, and platform bus initialization.

## Important APIs, Types, And Functions
Exports `platform_bus`, `platform_bus_type`, resource helpers (`platform_get_resource()`, `platform_get_mem_or_io()`, `platform_get_resource_byname()`), ioremap helpers, IRQ helpers (`platform_get_irq*()`, `platform_irq_count()`, `devm_platform_get_irqs_affinity()`), device lifecycle helpers (`platform_device_alloc()`, `platform_device_add_resources()`, `platform_device_add_data()`, `platform_device_add()`, `platform_device_del()`, `platform_device_register_full()`), and driver helpers (`__platform_driver_register()`, `platform_driver_unregister()`, `__platform_driver_probe()`, `__platform_create_bundle()`, `__platform_register_drivers()`). The `platform_devid_ida` allocates automatic IDs.

## Control Flow
Resource lookup scans `pdev->resource[]` by type, index, or name. IRQ lookup prioritizes firmware IRQs from OF/ACPI, falls back to resources, sets trigger type from resource flags, supports ACPI GPIO IRQ fallback for index zero, and treats IRQ 0 as invalid. Device registration initializes DMA masks, assigns a parent and bus, formats the device name from explicit/none/auto IDs, claims memory/I/O resources, and calls `device_add()`, with rollback for IDA and resources. Driver registration assigns bus ownership and delegates to `driver_register()`. Probe attaches PM domains, applies OF clock defaults, rejects one-shot probe functions after initial use, and invokes the platform driver's `probe()`.

## State And Persistence
State includes registered platform devices on `platform_bus_type`, claimed resources under `iomem_resource`/`ioport_resource`, allocated auto IDs, copied resources/platform data/software nodes, OF node references, DMA mask fields, driver override matching state, and `pdev->id_entry` from ID-table matching. No local disk state is used.

## Dependencies And Integration
Integrates with OF, ACPI, IRQ mapping/affinity, devres, IOMMU default domains, DMA configuration, PM domains, runtime/system PM generic ops, module loading via modalias uevents, and the broader driver core bus/device/driver model.

## Risks And Test Signals
High-risk areas are rollback on partial resource insertion, auto-ID freeing, OF/ACPI IRQ fallback differences, probe deferral suppression in `__platform_driver_probe()`, DMA/IOMMU cleanup for driver-managed DMA, modalias ABI stability, and matching order changes. Test signals include platform device KUnit/selftests, resource conflict tests, IRQ-by-index/name tests for OF and ACPI, auto-ID register/unregister loops, driver override matching, PM-domain attach/detach behavior, and module autoload modalias checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/power/Makefile -->
# sources/distributed-fs/ceph-client/drivers/base/power/Makefile

## Purpose
Builds the driver-core power-management objects selected by kernel configuration.

## Important APIs, Types, And Functions
The Makefile contributes `sysfs.o`, `generic_ops.o`, `common.o`, `qos.o`, `runtime.o`, and `wakeirq.o` for `CONFIG_PM`; `main.o`, `wakeup.o`, and `wakeup_stats.o` for `CONFIG_PM_SLEEP`; `trace.o` for `CONFIG_PM_TRACE_RTC`; `clock_ops.o` for `CONFIG_HAVE_CLK`; and KUnit objects for PM QoS and runtime PM tests.

## Control Flow
Kbuild evaluates `obj-$(CONFIG_...)` variables and compiles only the objects enabled by the configuration. `ccflags-$(CONFIG_DEBUG_DRIVER)` adds `-DDEBUG` for debug driver builds.

## State And Persistence
No runtime state is stored. The file controls which PM capabilities are present in the built kernel and therefore which exported symbols and sysfs/runtime behaviors exist.

## Dependencies And Integration
Integrates with Kbuild and the driver-core PM configuration matrix. The object split matches feature gates used throughout `power.h` and the individual PM source files.

## Risks And Test Signals
Risks are missing objects under a config combination, test object build failures, or unintended debug flag changes. Test signals are allmodconfig/allyesconfig/tiny config builds, `CONFIG_PM=n` builds, and KUnit builds for `CONFIG_PM_QOS_KUNIT_TEST` and `CONFIG_PM_RUNTIME_KUNIT_TEST`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/power/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/power/clock_ops.c -->
# sources/distributed-fs/ceph-client/drivers/base/power/clock_ops.c

## Purpose
Provides generic PM clock management for devices: clock acquisition, list ownership, suspend/resume enable sequencing, runtime PM wrappers, and bus notifiers that attach clock-backed PM domains.

## Important APIs, Types, And Functions
With `CONFIG_PM_CLK`, exports `pm_clk_add()`, `pm_clk_add_clk()`, `of_pm_clk_add_clks()`, `pm_clk_remove_clk()`, `pm_clk_init()`, `pm_clk_create()`, `pm_clk_destroy()`, `devm_pm_clk_create()`, `pm_clk_suspend()`, `pm_clk_resume()`, `pm_clk_runtime_suspend()`, `pm_clk_runtime_resume()`, and `pm_clk_add_notifier()`. `struct pm_clock_entry` tracks connection ID, `struct clk *`, status, and whether prepare implies enable. Locking uses `pm_subsys_data` spinlock plus `clock_mutex`.

## Control Flow
Adding a clock allocates an entry, gets or adopts the clock, prepares it unless prepare already enables it, and appends it to the PM clock list. Suspend walks the list in reverse and disables enabled clocks; resume walks forward and enables prepared/acquired clocks. `pm_clk_op_lock()` selects spinlock-only operation when clock ops cannot sleep, otherwise requires non-atomic context and a mutex. Notifiers create/destroy PM clock data on bus add/delete; when PM clock support is disabled, the notifier forcibly enables/disables clocks on bind/unbind instead.

## State And Persistence
State lives in `dev->power.subsys_data`: clock list, refcount, `clock_op_might_sleep`, and locks. Each entry stores status transitions among acquired, prepared, enabled, and error. Devres can own destruction through `devm_pm_clk_create()`.

## Dependencies And Integration
Depends on common PM subsystem data from `common.c`, clk APIs, OF clock enumeration, runtime PM generic callbacks, PM domains, bus notifiers, and devres.

## Risks And Test Signals
Risks include sleeping clock operations from atomic PM paths, list mutation races with suspend/resume, unbalanced clk prepare/enable/put, partial OF clock add rollback, and status drift after enable errors. Test signals are clk prepare/enable tracing, runtime PM suspend/resume on devices with multiple clocks, notifier attach/delete paths, atomic-context warnings, and OF clock enumeration failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/power/clock_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/power/common.c -->
# sources/distributed-fs/ceph-client/drivers/base/power/common.c

## Purpose
Provides shared driver-core PM helpers for `dev->power.subsys_data` lifetime and device PM-domain attachment, list attachment, detachment, start, domain assignment, and performance-state requests.

## Important APIs, Types, And Functions
Exports `dev_pm_get_subsys_data()`, `dev_pm_put_subsys_data()`, `dev_pm_domain_attach()`, `dev_pm_domain_attach_by_id()`, `dev_pm_domain_attach_by_name()`, `dev_pm_domain_attach_list()`, `devm_pm_domain_attach_list()`, `dev_pm_domain_detach()`, `dev_pm_domain_detach_list()`, `dev_pm_domain_start()`, `dev_pm_domain_set()`, and `dev_pm_domain_set_performance_state()`. `struct pm_subsys_data` is reference-counted under `dev->power.lock` and initialized for PM clocks.

## Control Flow
Subsystem data acquisition allocates optimistically, takes the device power lock, either increments an existing refcount or installs a new object and initializes PM clock state, then frees unused allocation. PM-domain attach first rejects devices already in a domain, tries ACPI attach and generic PM domain attach, and records detach-power-off policy. List attach counts OF power domains or uses named entries, attaches virtual devices by ID/name, optionally installs required OPP configs, optionally creates runtime-PM device links, and rolls back all prior domains, links, and OPP tokens on failure. Devres list attach registers automatic detach.

## State And Persistence
State lives in `dev->power.subsys_data`, `dev->pm_domain`, `dev->power.detach_power_off`, `struct dev_pm_domain_list` arrays of attached devices/links/OPP tokens, and device links. No persistent storage is used.

## Dependencies And Integration
Integrates with ACPI PM, generic PM domains, OF `power-domains`, device links, OPP required devices, PM clock initialization, and driver-core callback recalculation through `device_pm_check_callbacks()`.

## Risks And Test Signals
Risks include racing PM callbacks during attach/detach, leaking virtual PM-domain devices or device links on partial failure, changing PM domains after a device is bound, and incorrect behavior when `PD_FLAG_NO_DEV_LINK`, `PD_FLAG_DEV_LINK_ON`, or `PD_FLAG_REQUIRED_OPP` are combined. Test signals include multi-domain OF devices, attach-by-name/id failures, devres cleanup, OPP token cleanup, and bound-device domain-change warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/power/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/power/generic_ops.c -->
# sources/distributed-fs/ceph-client/drivers/base/power/generic_ops.c

## Purpose
Supplies generic subsystem PM callbacks that simply dispatch to the currently bound driver's `struct dev_pm_ops` when present.

## Important APIs, Types, And Functions
The `CALL_PM_OP()` macro safely locates `dev->driver->pm` and invokes a named callback or returns success when absent. Runtime exports include `pm_generic_runtime_suspend()` and `pm_generic_runtime_resume()`. Sleep-state helpers cover prepare, suspend, freeze, poweroff, thaw, resume, restore, noirq, late/early, and complete phases.

## Control Flow
Each helper is a thin pass-through for one PM phase. Return-valued helpers propagate the driver callback return code; `pm_generic_complete()` calls `complete()` only when present. Compile-time `CONFIG_PM` and `CONFIG_PM_SLEEP` gates expose only the helpers relevant to the build.

## State And Persistence
No state is stored. These functions are dispatch adapters used by buses, classes, domains, and platform PM operations to avoid duplicating driver callback checks.

## Dependencies And Integration
Depends on `struct device`, `struct device_driver`, `struct dev_pm_ops`, runtime PM config, and symbol exports consumed by platform bus and other subsystems.

## Risks And Test Signals
Risks are low but include calling through stale driver pointers if invoked outside driver-core locking expectations and missing a PM phase when `dev_pm_ops` grows. Test signals are compile coverage for PM config variants and subsystem PM tests verifying callback ordering and return-code propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/power/generic_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/power/main.c -->
# sources/distributed-fs/ceph-client/drivers/base/power/main.c

## Purpose
Implements the system-wide device PM core: device registration into PM lists, prepare/suspend/late/noirq and resume/noirq/early/complete sequencing, dependency-aware asynchronous PM, direct-complete and smart-suspend optimization, wakeup propagation, PM watchdog support, and exported PM iteration/wait helpers.

## Important APIs, Types, And Functions
Exports `pm_hibernate_is_recovering()`, `dpm_resume_start()`, `dpm_resume_end()`, `dpm_suspend_end()`, `dpm_suspend_start()`, `__suspend_report_result()`, `device_pm_wait_for_dev()`, and `dpm_for_each_dev()`. Device lifecycle helpers include `device_pm_sleep_init()`, `device_pm_add()`, `device_pm_remove()`, move helpers, `device_pm_check_callbacks()`, `dev_pm_skip_suspend()`, and `dev_pm_skip_resume()`. Core lists are `dpm_list`, `dpm_prepared_list`, `dpm_suspended_list`, `dpm_late_early_list`, and `dpm_noirq_list`.

## Control Flow
Registered devices enter `dpm_list` in discovery order. Suspend starts with `dpm_prepare()`, which waits for probes, blocks probing, suspends thermal control, calls `prepare()`, blocks runtime PM, and moves devices to `dpm_prepared_list`. `dpm_suspend()`, `dpm_suspend_late()`, and `dpm_suspend_noirq()` walk from leaf devices toward parents/suppliers, using completions to respect child and device-link dependencies and moving devices through staged lists. Resume reverses the direction from roots toward children/consumers through noirq, early, normal, and complete phases. Callback selection prioritizes PM domain, type, class, bus, then driver callbacks, with legacy bus callbacks as fallback. Errors set `async_error`, save failed step/device, complete pending devices, and trigger partial resume.

## State And Persistence
State lives in `dev->power`: list entry, completion, `is_prepared`, `is_suspended`, `is_late_suspended`, `is_noirq_suspended`, `direct_complete`, `smart_suspend`, `must_resume`, wakeup flags, async flags, and callback-presence cache. Global state includes `pm_transition`, `async_error`, and PM lists protected by `dpm_list_mtx`. Nothing is persisted across boot.

## Dependencies And Integration
Integrates with the driver core, runtime PM, wake IRQs, device links, async framework, suspend tracing, cpufreq/devfreq/thermal PM hooks, PM trace, PM domains, syscore flags, wakeup sources, and optional DPM watchdog timers.

## Risks And Test Signals
Risks are high: dependency ordering regressions, races with device removal during async PM, incorrect direct-complete handling, runtime PM disable/enable imbalance, wakeup propagation loss, missed completion causing suspend hangs, and wrong rollback after phase errors. Test signals include suspend/hibernate/resume stress tests, async suspend enabled/disabled runs, device-link dependency tests, wakeup abort tests, DPM watchdog coverage, runtime PM interaction tests, and tracing of failed PM steps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/power/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/power/power.h -->
# sources/distributed-fs/ceph-client/drivers/base/power/power.h

## Purpose
Defines internal driver-core PM initialization helpers, wake-IRQ state, runtime PM declarations/stubs, sysfs/QoS hooks, system-sleep PM list declarations, and configuration-dependent no-op fallbacks.

## Important APIs, Types, And Functions
`device_pm_init_common()` initializes `dev->power.lock`, QoS pointer, and `early_init`. `pm_runtime_early_init()` sets runtime PM disable depth differently depending on `CONFIG_PM`. `struct wake_irq` tracks wake IRQ ownership flags, IRQ number, device, and name. The header declares runtime PM internals, wake IRQ helpers, PM sysfs helpers, PM QoS sysfs helpers, system-sleep list helpers, wakeup source sysfs hooks, and `device_pm_init()`.

## Control Flow
Device initialization calls `device_pm_init()`, which performs common initialization, system-sleep initialization, and runtime PM initialization. Compile-time gates turn runtime PM and system sleep functions into no-ops when disabled while keeping callers buildable.

## State And Persistence
State initialized here is embedded in `struct device::power`: locks, QoS pointer, runtime PM depth/status, wakeup pointers, PM list entry, and completion fields. Wake IRQ status bits track allocation, devres management, reverse ordering, and enabled state.

## Dependencies And Integration
Includes PM QoS and depends on `CONFIG_PM`/`CONFIG_PM_SLEEP` structure. It is consumed by driver-core device creation, platform bus PM, runtime PM, wake IRQ, wakeup, sysfs, and PM QoS modules.

## Risks And Test Signals
Risks include inconsistent stub semantics between PM-enabled and PM-disabled builds, missing initialization before other driver-core code touches `dev->power`, and wake IRQ status-bit misuse. Test signals are broad config matrix builds, device registration tests with PM disabled, wake IRQ setup/teardown tests, and runtime PM KUnit coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/power/power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/power/qos-test.c -->
# sources/distributed-fs/ceph-client/drivers/base/power/qos-test.c

## Purpose
Provides KUnit coverage for frequency QoS aggregation and request lifecycle behavior.

## Important APIs, Types, And Functions
Tests use `struct freq_constraints`, `struct freq_qos_request`, `freq_constraints_init()`, `freq_qos_add_request()`, `freq_qos_update_request()`, `freq_qos_remove_request()`, and `freq_qos_read_value()`. Test cases are `freq_qos_test_min`, `freq_qos_test_maxdef`, and `freq_qos_test_readd`.

## Control Flow
The min test adds two minimum requests, verifies that the aggregate is the highest min, and checks aggregate changes as requests are removed. The max-default test verifies default max requests do not change the aggregate, then updates requests and checks that the effective max is the lowest active max. The readd test verifies a request object can be reused after removal.

## State And Persistence
All state is in stack-allocated constraints and request objects inside KUnit cases. No persistent kernel state or device state is touched.

## Dependencies And Integration
Depends on KUnit and PM QoS frequency constraint APIs. The Makefile includes it when `CONFIG_PM_QOS_KUNIT_TEST` is enabled.

## Risks And Test Signals
The tests directly signal regressions in aggregate min/max semantics, default-value handling, and request invalidation after removal. Gaps remain around notifier behavior, device PM QoS wrappers, flags, latency tolerance, and concurrency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/power/qos-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/power/qos.c -->
# sources/distributed-fs/ceph-client/drivers/base/power/qos.c

## Purpose
Implements per-device PM QoS constraints for resume latency, latency tolerance, min/max frequency, and flags, including kernel request APIs, notifier registration, userspace sysfs exposure, and cleanup on device removal.

## Important APIs, Types, And Functions
Exports flag/read APIs `dev_pm_qos_flags()` and `dev_pm_qos_read_value()`, request APIs `dev_pm_qos_add_request()`, `dev_pm_qos_update_request()`, `dev_pm_qos_remove_request()`, notifier APIs, `dev_pm_qos_add_ancestor_request()`, sysfs exposure/hide APIs for latency limit, flags, and latency tolerance, and `dev_pm_qos_update_user_latency_tolerance()`. State is protected by `dev_pm_qos_mtx`, `dev_pm_qos_sysfs_mtx`, and `dev->power.lock`.

## Control Flow
First use allocates `struct dev_pm_qos`, initializes resume-latency and latency-tolerance constraint lists, frequency constraints, flag list, and notifier heads, then installs it under the device power lock. Request add/update/remove validates request state and type, traces the operation, and dispatches to `pm_qos_update_target()`, `freq_qos_apply()`, or `pm_qos_update_flags()`. Cleanup removes sysfs files, hides user requests, drains every constraint list, marks `dev->power.qos` as `ERR_PTR(-ENODEV)`, and frees memory. Sysfs exposure creates a dedicated request, installs it in the QoS object under locks, then adds the sysfs attribute, rolling back if sysfs creation fails.

## State And Persistence
State is per-device in `dev->power.qos`: constraints, notifiers, user-space request pointers, frequency constraints, and flags. The `ERR_PTR(-ENODEV)` sentinel prevents new use after device removal. Userspace-visible values persist only while the device and exposed sysfs files exist.

## Dependencies And Integration
Depends on PM QoS core plist handling, freq QoS, runtime PM for flag/latency-tolerance sysfs safety, tracepoints, driver-core PM cleanup, and sysfs helpers declared in `power.h`.

## Risks And Test Signals
Risks include request object reuse without removal, races between sysfs removal and request updates, stale requests after device removal, runtime-suspended devices when mutating flags, notifier leaks, and locking-order regressions. Test signals include KUnit frequency QoS tests, device removal with active requests/notifiers, sysfs expose/hide cycles, latency tolerance callbacks, and tracepoints for add/update/remove behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/power/qos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/power/runtime-test.c -->
# sources/distributed-fs/ceph-client/drivers/base/power/runtime-test.c

## Purpose
Provides KUnit tests for runtime PM core behavior on synthetic KUnit devices.

## Important APIs, Types, And Functions
Tests use `kunit_device_register()`, `pm_runtime_enable()`, `pm_runtime_get_sync()`, `pm_runtime_put_sync()`, `pm_runtime_suspend()`, `pm_runtime_autosuspend()`, request helpers, status helpers, `pm_runtime_set_active()`, `pm_runtime_set_suspended()`, `pm_runtime_barrier()`, and `pm_runtime_resume_and_get()`. Test cases cover depth handling, already-suspended operations, idle behavior, disabled runtime PM, runtime error recovery, and probe-active flow.

## Control Flow
Each test registers a fresh device named `pm_runtime_test_device`. The depth test exercises usage-count transitions from suspended to active and back. Already-suspended and idle tests verify return codes when no transition is needed or usage count blocks idle. Disabled tests confirm runtime PM disabled devices are treated as active and return `-EACCES` while keeping refcounts balanced. Error tests inject `dev->power.runtime_error`, verify operations fail with `-EINVAL`, clear the error via `pm_runtime_set_suspended()`, and retest normal behavior. The probe-active test models a probe that marks the device active before enabling runtime PM and then idles it.

## State And Persistence
State is isolated to KUnit-created devices and their embedded `dev->power` runtime PM fields: disable depth, runtime status, usage count, runtime error, and pending work. No external persistence is used.

## Dependencies And Integration
Depends on KUnit device helpers and runtime PM APIs from `runtime.c`. The Makefile builds it under `CONFIG_PM_RUNTIME_KUNIT_TEST`.

## Risks And Test Signals
The suite is a direct regression signal for runtime PM return-code semantics, usage-count balancing, disabled/error handling, barrier behavior, and probe sequencing. Gaps include real driver callbacks, autosuspend delay timing, parent/child runtime PM, and concurrent operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/power/runtime-test.c -->
