# subset-b-004992 research

Grouped research for Linux Open Firmware / devicetree core files under `sources/distributed-fs/ceph-client/drivers/of`. Each section preserves the source path for reconciliation into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/base.c -->
# sources/distributed-fs/ceph-client/drivers/of/base.c

## Purpose
`base.c` is the main live devicetree access layer. It exposes global OF roots (`of_root`, `of_chosen`, `of_aliases`, `of_stdout`), implements node/property lookup and matching, parses phandle argument lists, mutates live node properties, scans `/aliases`, resolves stdout, discovers cache topology, and translates requester IDs through `iommu-map`/`msi-map` style bindings.

## Important APIs, types, and functions
Key globals are `of_mutex`, `devtree_lock`, `aliases_lookup`, `of_kset`, and the `phandle_cache`. Public APIs include `of_find_property()`, `of_get_property()`, `of_find_all_nodes()`, `of_find_node_by_path()`, `of_find_node_by_name()`, `of_find_compatible_node()`, `of_match_node()`, `of_find_node_by_phandle()`, `of_parse_phandle_with_args_map()`, `of_count_phandle_with_args()`, `of_add_property()`, `of_remove_property()`, `of_update_property()`, `of_alias_scan()`, `of_alias_get_id()`, `of_console_check()`, `of_find_next_cache_node()`, `of_find_last_cache_level()`, and `of_map_id()`. Internal helpers prefixed `__of_` assume locking or detached-tree ownership.

## Control flow and state
`of_core_init()` registers OF reconfiguration notifiers, creates `/sys/firmware/devicetree`, attaches all existing nodes to sysfs, seeds the phandle cache, and creates the legacy `/proc/device-tree` symlink. Traversal APIs walk child/sibling/parent pointers under `devtree_lock` and pair returned nodes with reference increments. Matching computes scores from compatible order, type, and name. Phandle parsing uses `of_phandle_iterator` to walk packed `__be32` lists, resolve providers, read `#*-cells`, and fill `struct of_phandle_args`.

Property updates are serialized by `of_mutex`, alter the linked property lists under `devtree_lock`, update sysfs mirrors, and emit dynamic-tree notifications. Removed and replaced properties are moved to `deadprops` because callers may hold raw pointers returned by `of_get_property()`.

## Dependencies and integration
This file depends on `of_private.h` declarations, sysfs helpers from `kobj.c`, dynamic notifier glue from `dynamic.c`, FDT-created globals from `fdt.c`, console registration, CPU/cache helpers, and device-core fwnode flags. It is consumed by most OF subsystems and driver buses.

## Risks and test signals
Risk centers on reference counting, raw property pointer lifetime, lock ordering between `of_mutex` and `devtree_lock`, phandle cache invalidation on detach, malformed phandle lists, and alias/stdout parsing. KUnit coverage in this subset checks root lookup indirectly, while broader kernel OF tests exercise phandle, address, overlay, and dynamic update behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/cpu.c -->
# sources/distributed-fs/ceph-client/drivers/of/cpu.c

## Purpose
`cpu.c` maps devicetree CPU nodes to logical Linux CPU IDs, extracts hardware thread IDs, and resolves CPU idle-state nodes. It provides generic weak matching hooks that architectures can override when firmware CPU numbering does not match Linux logical numbering.

## Important APIs, types, and functions
The key exported APIs are `of_get_cpu_hwid()`, `of_get_cpu_node()`, `of_cpu_device_node_get()`, `of_cpu_node_to_id()`, and `of_get_cpu_state_node()`. Weak hooks `arch_match_cpu_phys_id()` and `arch_find_n_match_cpu_physical_id()` provide default physical-ID matching. `__of_find_n_match_cpu_property()` reads either `reg` or PowerPC's `ibm,ppc-interrupt-server#s`.

## Control flow and state
`of_get_cpu_hwid()` reads the CPU node's `reg` property using the parent address-cell count and returns the requested thread slot. `of_get_cpu_node()` iterates all CPU nodes and applies the architecture matching hook, returning a referenced node. `of_cpu_device_node_get()` first tries the registered CPU device's `of_node` and falls back to scanning firmware. `of_cpu_node_to_id()` inverts the mapping by scanning possible CPUs. `of_get_cpu_state_node()` prefers hierarchical `power-domains` plus `domain-idle-states`, then falls back to flat `cpu-idle-states`.

## Dependencies and integration
This file depends on core OF traversal and phandle parsing from `base.c`, CPU device registration from the driver core, and architecture-provided matching overrides. CPU idle and power-management code consume these helpers.

## Risks and test signals
Malformed `reg` lengths, absent address-cell metadata, or architecture-specific physical IDs can make CPU lookup fail. Callers must release returned nodes. Idle-state resolution may be sensitive to mixed old and new bindings. Test signals are boot-time CPU topology correctness, CPU hotplug device association, and cpuidle binding tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/device.c -->
# sources/distributed-fs/ceph-client/drivers/of/device.c

## Purpose
`device.c` bridges devicetree nodes to `struct device`. It handles driver match lookup, DMA/IOMMU setup from DT properties, restricted DMA pool assignment, modalias generation, uevent metadata, and stable bus ID construction.

## Important APIs, types, and functions
Exports include `of_match_device()`, `of_dma_configure_id()`, `of_device_get_match_data()`, `of_device_modalias()`, `of_device_uevent()`, `of_device_uevent_modalias()`, and `of_device_make_bus_id()`. `of_dma_set_restricted_buffer()` is the internal helper that detects a compatible and available `restricted-dma-pool` memory-region.

## Control flow and state
`of_match_device()` refuses reused OF nodes and delegates to `of_match_node()`. `of_dma_configure_id()` finds the DMA parent, parses `dma-ranges`, clamps DMA masks, sets `bus_dma_limit` and `dma_range_map`, configures IOMMU, applies architecture DMA ops, and falls back to restricted DMA pools when no IOMMU is active. It preserves error semantics for deferred IOMMU probes by clearing temporary maps and freeing the parsed map.

Modalias and uevent paths expose OF name, full path, type, compatible list, alias entries, and module alias strings to user space. `of_device_make_bus_id()` uses translated `reg` addresses when possible, otherwise prepends parent names until a unique-looking device name is built.

## Dependencies and integration
The file integrates with DMA direct mapping, `of_iommu_configure()`, reserved-memory device setup, platform devices, module autoloading, and the global `aliases_lookup` protected by `of_mutex`.

## Risks and test signals
Main risks are stale or conflicting `dma_range_map`, `-EPROBE_DEFER` handling, non-set `dev->dma_mask`, restricted DMA pool selection when multiple memory regions exist, modalias buffer truncation, and reused OF nodes. Runtime signals include DMA mask logs, IOMMU probe ordering, module autoload events, and sysfs/uevent environment contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/dynamic.c -->
# sources/distributed-fs/ceph-client/drivers/of/dynamic.c

## Purpose
`dynamic.c` implements runtime devicetree mutation. It owns node reference APIs, OF reconfiguration notifier registration, attach/detach operations, dynamic node/property allocation and free paths, and transactional changeset apply/revert helpers used by overlays and other dynamic DT clients.

## Important APIs, types, and functions
Exports include `of_node_get()`, `of_node_put()`, `of_reconfig_notifier_register()`, `of_reconfig_notifier_unregister()`, `of_reconfig_get_state_change()`, `of_detach_node()`, `of_changeset_create_node()`, `of_changeset_init()`, `of_changeset_destroy()`, `of_changeset_apply()`, `of_changeset_revert()`, `of_changeset_action()`, and property-construction helpers for string, string-array, u32-array, bool, and string update actions. Core internal helpers include `__of_attach_node()`, `__of_detach_node()`, `__of_prop_dup()`, `__of_node_dup()`, and changeset entry apply/revert/notify functions.

## Control flow and state
Node references are backed by embedded kobjects. Reconfiguration events flow through a blocking notifier chain and use `struct of_reconfig_data`. Attach parses `name` and phandle properties, links the node into its parent's child list, clears `OF_DETACHED`, marks the fwnode as not a device, and attaches sysfs. Detach unlinks from siblings, marks `OF_DETACHED`, invalidates the phandle cache, and detaches sysfs.

Changesets collect ordered `struct of_changeset_entry` items. Apply runs entries forward under `of_mutex`, reverts already-applied entries if an apply step fails, then emits notifiers with the mutex dropped. Revert runs entries in reverse and reapplies on revert failure. Destroy waits for pending device-link removals before releasing entries to avoid freeing nodes still referenced by devices.

## Dependencies and integration
This file relies on property mutation helpers in `base.c`, sysfs hooks in `kobj.c`, fwnode link cleanup, device-link removal, OF overlay flags, and notifier consumers such as OF platform population.

## Risks and test signals
Risk is high around reference balance, overlay lifetime flags, mutation while readers traverse under `devtree_lock`, notifier failures after structural changes, and changeset rollback leaving unknown state when both apply and revert fail. Test signals include overlay KUnit tests, dynamic reconfiguration device add/remove behavior, kobject underflow warnings, and memory leak diagnostics in `of_node_release()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/dynamic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/fdt.c -->
# sources/distributed-fs/ceph-client/drivers/of/fdt.c

## Purpose
`fdt.c` handles flattened devicetree boot-time processing and conversion to live `struct device_node` trees. It verifies and stores the boot FDT, scans early memory and `/chosen` metadata, reserves FDT and memreserve regions, unflattens nodes/properties, publishes raw FDT sysfs data, and supports built-in empty-root fallback.

## Important APIs, types, and functions
Important APIs include `of_fdt_limit_memory()`, `of_fdt_device_is_available()`, `__unflatten_device_tree()`, `of_fdt_unflatten_tree()`, `early_init_fdt_scan_reserved_mem()`, `early_init_fdt_reserve_self()`, `of_scan_flat_dt()`, `of_scan_flat_dt_subnodes()`, `of_get_flat_dt_prop()`, `of_flat_dt_get_addr_size()`, `of_flat_dt_match_machine()`, `early_init_dt_scan_root()`, `dt_mem_next_cell()`, `early_init_dt_scan_memory()`, `early_init_dt_scan_chosen()`, `early_init_dt_verify()`, `early_init_dt_scan_nodes()`, `early_init_dt_scan()`, `unflatten_device_tree()`, and `unflatten_and_copy_device_tree()`.

## Control flow and state
`early_init_dt_verify()` validates the FDT header, records `initial_boot_params` and physical address, computes a CRC, and reads root cell counts. `early_init_dt_scan_nodes()` reads `/chosen`, memory nodes, usable-memory ranges, and kexec handover metadata before the live tree exists. Memory parsing adds page-aligned regions to memblock and marks hotpluggable memory.

Unflattening is two-pass: `unflatten_dt_nodes()` first sizes allocations, then populates `device_node` and `property` structures from FDT offsets. Missing `name` properties are synthesized from unit names. Child lists are reversed after creation to restore `.dts` order. `unflatten_device_tree()` runs reserved-memory late initialization first, unflattens into `of_root`, scans aliases/chosen/stdout, and initializes unittest overlay base data.

## Dependencies and integration
The file integrates with libfdt, memblock, initrd, crash dump, dm-crypt crash keys, random seed consumption, earlycon, kexec handover, sysfs firmware files, and reserved-memory scanning in `of_reserved_mem.c`.

## Risks and test signals
Risks include invalid FDT headers, property size mismatches, depth overflows, skipped disabled nodes when `CONFIG_OF_KOBJ` is off, CRC mismatch preventing `/sys/firmware/fdt`, early memory alignment truncation, and security-sensitive seed wiping. KUnit `of_dtb` root tests, boot logs, memblock maps, earlycon startup, and raw-FDT sysfs presence are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/fdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/fdt_address.c -->
# sources/distributed-fs/ceph-client/drivers/of/fdt_address.c

## Purpose
`fdt_address.c` translates addresses directly from the flattened boot FDT before a live devicetree exists. It is a minimal early-boot counterpart to normal OF address translation.

## Important APIs, types, and functions
The central type is `struct of_bus`, containing `count_cells`, `map`, and `translate` callbacks. The default bus implementation includes `fdt_bus_default_count_cells()`, `fdt_bus_default_map()`, and `fdt_bus_default_translate()`. `fdt_translate_one()` applies one `ranges` level, `fdt_translate_address()` walks parent buses, and `of_flat_dt_translate_address()` is the exported init API.

## Control flow and state
Translation starts from a node's `reg` property, reads parent `#address-cells` and `#size-cells`, copies the child address into a bounded local array, then walks up through parent offsets. Each level requires valid parent cell counts and a usable `ranges` property. Empty `ranges` means identity mapping. Non-empty `ranges` are searched for the child address, then rewritten into parent bus address cells with offset applied. Reaching the root returns the accumulated address.

## Dependencies and integration
The file depends on `initial_boot_params`, libfdt accessors, numeric helpers from OF core, and constants/macros in `of_private.h`. Early reserved-memory and boot scanners can use this when live address translation is unavailable.

## Risks and test signals
The implementation only supports the default bus translator in this file. Translation fails on missing `reg`, invalid cell counts, absent or nonmatching `ranges`, and `#size-cells == 0`. Risks are malformed FDT data and overflow-limited address cell arrays. Boot-time address/resource logs and later live-tree address KUnit tests are relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/fdt_address.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/irq.c -->
# sources/distributed-fs/ceph-client/drivers/of/irq.c

## Purpose
`irq.c` resolves devicetree interrupt descriptions into Linux IRQ mappings. It parses `interrupts`, `interrupts-extended`, `interrupt-parent`, and `interrupt-map`, initializes interrupt controllers in parent-first order, and resolves MSI parent/domain mappings.

## Important APIs, types, and functions
Exports include `irq_of_parse_and_map()`, `of_irq_find_parent()`, `of_imap_parser_init()`, `of_imap_parser_one()`, `of_irq_parse_raw()`, `of_irq_parse_one()`, `of_irq_to_resource()`, `of_irq_get()`, `of_irq_get_byname()`, `of_irq_count()`, `of_irq_to_resource_table()`, `of_irq_init()`, `of_msi_xlate()`, `of_msi_get_domain()`, and `of_msi_configure()`. `struct of_intc_desc` stages interrupt-controller initialization. `of_irq_imap_abusers` lists legacy controllers whose `interrupt-map` must be ignored by core parsing.

## Control flow and state
`of_irq_parse_one()` copies the device `reg` address into a bounded buffer, prefers `interrupts-extended`, otherwise finds the interrupt parent and reads `interrupts` cells, then calls `of_irq_parse_raw()`. Raw parsing verifies `#interrupt-cells`, builds a match array from address and interrupt specifier cells, walks interrupt-map translations, and stops at an interrupt-controller unless a valid map overrides it. Successful parse returns a referenced controller node.

`of_irq_get()` converts parsed phandle args into an IRQ domain mapping, returning `-EPROBE_DEFER` if the domain is not registered yet. `of_irq_init()` scans matched interrupt controllers, computes their parents, then initializes roots before children. MSI helpers walk up device parents and use `msi-map`, `msi-map-mask`, or simple `msi-parent` to select a target node and ID.

## Dependencies and integration
The file integrates with irqdomain, resource creation, OF phandle parsing, `of_map_id()`, platform IRQ controller drivers, MSI domains, and architecture workarounds such as OldWorld Mac parsing and `OF_IMAP_NO_PHANDLE`.

## Risks and test signals
Risks include malformed `interrupt-map` lengths, parent phandle leaks, unavailable domains, old firmware workarounds, address-cell mismatch, self-referential maps, and unsupported multiple MSI parents. Test signals include boot interrupt-controller order, deferred-probe behavior, resource tables, MSI device domains, and interrupt-map parser users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/kexec.c -->
# sources/distributed-fs/ceph-client/drivers/of/kexec.c

## Purpose
`kexec.c` prepares a new FDT for a kexec or crash-kernel boot. It removes stale reservations and properties, carries forward or replaces initrd and bootargs, adds crash dump metadata, random seeds, IMA buffers, and kexec handover metadata.

## Important APIs, types, and functions
The main exported-style API is `of_kexec_alloc_and_setup_fdt()`. Helpers include `fdt_find_and_del_mem_rsv()`, `get_addr_size_cells()`, `do_get_kexec_buffer()`, `ima_get_kexec_buffer()`, `ima_free_kexec_buffer()`, `remove_ima_buffer()`, `setup_ima_buffer()`, and `kho_add_chosen()`.

## Control flow and state
`of_kexec_alloc_and_setup_fdt()` sizes a new buffer from current `initial_boot_params`, command line length, fixed extra space, and caller extra space. It opens the current FDT into the new buffer, removes the current FDT reservation, ensures `/chosen` exists, removes stale crash properties, replaces initrd properties and reservation, adds crash elfcorehdr and usable-memory-range for crash images, adds KHO metadata, updates bootargs, refreshes `kaslr-seed` and `rng-seed` only if the RNG is initialized, marks `linux,booted-from-kexec`, removes old IMA buffer metadata, and optionally adds a new IMA buffer reservation.

IMA helper functions parse `linux,ima-kexec-buffer` using root address/size cells and validate or free the region via memblock.

## Dependencies and integration
This file depends on libfdt mutation APIs, kexec image fields, memblock, IMA, random subsystem, crash dump resources, dm-crypt crash-key handoff, root cell-count helpers from OF core, and `initial_boot_params`.

## Risks and test signals
Risks include insufficient FDT slack, failed reservation deletion, stale sensitive seeds, malformed address/size properties, missing `/chosen`, RNG unavailability, and losing crash metadata. Test signals are successful kexec/kdump boot, FDT property inspection in the next kernel, reservation map correctness, and IMA measurement carryover.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/kexec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/kobj.c -->
# sources/distributed-fs/ceph-client/drivers/of/kobj.c

## Purpose
`kobj.c` mirrors live devicetree nodes and properties into sysfs under `/sys/firmware/devicetree`. It provides kobject type glue, binary property attributes, safe name handling, and attach/detach helpers used by core and dynamic OF code.

## Important APIs, types, and functions
Key functions are `of_node_is_attached()`, `__of_add_property_sysfs()`, `__of_sysfs_remove_bin_file()`, `__of_remove_property_sysfs()`, `__of_update_property_sysfs()`, `__of_attach_node_sysfs()`, and `__of_detach_node_sysfs()`. `of_node_ktype` binds node kobject release to `of_node_release()` when dynamic OF is enabled, or a no-op without dynamic freeing.

## Control flow and state
Node attach sets the node kset, chooses a name (`base` for root-like nodes, basename for children), adds the kobject under the parent, creates bin attributes for existing properties, and takes a node reference for sysfs lifetime. Property add initializes a bin attribute, masks `security-*` properties to mode `0400` and size zero, and creates the sysfs file. Removal deletes the bin file and frees the duplicated sysfs attribute name. Detach removes properties, deletes the kobject, and drops the sysfs-held node reference.

## Dependencies and integration
The file depends on `of_kset` from `base.c`, `of_node_release()` from `dynamic.c` when configured, kernfs/sysfs APIs, and property lists maintained by OF core.

## Risks and test signals
Risks include duplicate property or node names, sysfs name allocation failures, leaking property attribute names, exposing sensitive property values, and attach/detach imbalance. Signals are sysfs tree shape, duplicate-name warnings, property file permissions, kobject lifetime warnings, and dynamic overlay sysfs updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/kobj.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/module.c -->
# sources/distributed-fs/ceph-client/drivers/of/module.c

## Purpose
`module.c` builds OF modalias strings and requests matching kernel modules for devicetree nodes. It supports module autoloading from node name, device type, and compatible strings.

## Important APIs, types, and functions
`of_modalias()` formats a modalias into a caller-provided buffer and returns the total length that would be required. `of_request_module()` allocates a correctly sized alias and calls `request_module()`.

## Control flow and state
`of_modalias()` validates buffer and length arguments, writes an `of:N<name>T<type>` prefix, then appends each compatible string with a `C` prefix. Spaces in compatible strings are normalized to underscores in the written buffer. It tracks total size separately from copied size so callers can detect truncation. `of_request_module()` first asks for size with a zero-length call, allocates one extra byte for NUL termination, emits the alias, requests the module, then frees the temporary string.

## Dependencies and integration
The file uses OF property string iteration, `%pOFn` formatting, module loader APIs, and is consumed by `device.c` for modalias uevents.

## Risks and test signals
Risks include negative lengths, NULL buffers with nonzero length, truncation, unexpected spaces in compatible strings, and unbounded module autoload behavior for malformed firmware strings. Test signals are modalias sysfs/uevent output and successful autoload of OF-matched drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/of_kunit_helpers.c -->
# sources/distributed-fs/ceph-client/drivers/of/of_kunit_helpers.c

## Purpose
`of_kunit_helpers.c` provides test-managed helper APIs for OF KUnit tests. It centralizes common skip logic for systems without a populated DT root and wraps node/overlay cleanup in KUnit resource actions.

## Important APIs, types, and functions
Exports include `of_root_kunit_skip()`, `of_overlay_fdt_apply_kunit()` when overlays and early flattree are enabled, and `of_node_put_kunit()`. The file uses `KUNIT_DEFINE_ACTION_WRAPPER()` to bind `of_node_put()` as a KUnit cleanup action.

## Control flow and state
`of_root_kunit_skip()` skips on ARM64 or RISC-V ACPI boots where DT may not populate `of_root`. `of_overlay_fdt_apply_kunit()` applies an overlay, stores the overlay changeset ID in KUnit-managed memory, and registers an action that removes the overlay when the test ends or if action registration fails. `of_node_put_kunit()` registers a cleanup action to drop a node reference and fails the test if resource allocation fails.

## Dependencies and integration
This file integrates KUnit resource management, OF overlay APIs, early flattree availability, and the shared `of_root` global. It supports tests in `of_test.c` and other OF KUnit suites.

## Risks and test signals
Risks are mostly test-infrastructure risks: missing cleanup action registration, running DT tests on ACPI-only boots, overlay apply failure, and leaked node references. Signals are KUnit skip messages, overlay removal after tests, and absence of reference leak warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/of_kunit_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/of_numa.c -->
# sources/distributed-fs/ceph-client/drivers/of/of_numa.c

## Purpose
`of_numa.c` parses NUMA topology from devicetree. It discovers CPU node IDs, memory ranges per NUMA node, distance matrices, and provides a runtime node-to-NID lookup for devices.

## Important APIs, types, and functions
Important functions are `of_numa_init()` and `of_node_to_nid()`. Internal parsers are `of_numa_parse_cpu_nodes()`, `of_numa_parse_memory_nodes()`, `of_numa_parse_distance_map_v1()`, and `of_numa_parse_distance_map()`.

## Control flow and state
CPU parsing scans CPU nodes for `numa-node-id` and marks parsed node IDs. Memory parsing scans `device_type = "memory"` nodes with `numa-node-id`, converts each address range through `of_address_to_resource()`, adds ranges to `numa_add_memblk()`, and marks parsed nodes. Distance parsing finds a compatible `numa-distance-map-v1` node and consumes `distance-matrix` triplets of source node, destination node, and distance, validating local and remote distance rules before setting distances. `of_node_to_nid()` walks a device's parents until it finds `numa-node-id`, then returns it only if possible.

## Dependencies and integration
This file depends on OF traversal/address conversion, `numa_memblks`, architecture NUMA constants and distance APIs, and the weak fallback in `base.c` when `CONFIG_NUMA` is enabled.

## Risks and test signals
Risks include invalid NID values, malformed memory nodes, missing resources, asymmetric or invalid distance matrix entries, and `numa=off` causing otherwise valid firmware IDs to map to `NUMA_NO_NODE`. Signals are boot NUMA logs, node masks, memory block layout, and device locality behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/of_numa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/of_private.h -->
# sources/distributed-fs/ceph-client/drivers/of/of_private.h

## Purpose
`of_private.h` is the internal contract for the OF core. It declares shared globals, conditional stubs, internal helpers, FDT constants, reserved-memory entry points, DMA hooks, address bounds, and transaction iteration macros not intended as public OF API.

## Important APIs, types, and functions
The key type is `struct alias_prop`, shared by alias scanning and uevent code. Important declarations include `of_mutex`, `devtree_lock`, `aliases_lookup`, `of_kset`, dynamic change helpers, sysfs attach/update helpers, overlay locks, `__unflatten_device_tree()`, `of_alias_scan()`, `__of_prop_dup()`, `__of_node_dup()`, internal path/property mutation helpers, `__of_detach_node()`, `of_dma_get_range()`, `__of_get_dma_parent()`, `fdt_scan_reserved_mem()`, `fdt_scan_reserved_mem_late()`, and `of_fdt_device_is_available()`.

## Control flow and state
The header selects real implementations or no-op stubs based on config symbols such as `CONFIG_OF_DYNAMIC`, `CONFIG_OF_KOBJ`, `CONFIG_OF_ADDRESS`, `CONFIG_HAS_DMA`, `CONFIG_OF_OVERLAY`, and KUnit/unit-test settings. It also defines default root cell counts, reserved-memory limits, illegal phandle marker, maximum address cells, and validation macros used by early FDT address translation.

## Dependencies and integration
This header is included by the OF core C files in this subset and coordinates boundaries between base traversal, dynamic mutation, sysfs mirroring, FDT boot code, reserved memory, DMA address parsing, IRQ parsing, overlays, and tests.

## Risks and test signals
The main risk is contract drift: changing a stub or declaration can silently alter behavior for many config combinations. Locking declarations and underscored helper comments are especially important because callers may bypass normal references and locking only on detached trees or under locks. Build coverage across config matrices is the primary test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/of_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/of_reserved_mem.c -->
# sources/distributed-fs/ceph-client/drivers/of/of_reserved_mem.c

## Purpose
`of_reserved_mem.c` discovers, reserves, allocates, initializes, and assigns devicetree `/reserved-memory` regions. It supports static `reg` regions, dynamic `size` plus `alloc-ranges` regions, `no-map`, compatible-specific callbacks, and device assignment through `memory-region`.

## Important APIs, types, and functions
Boot APIs include `fdt_scan_reserved_mem()` and `fdt_scan_reserved_mem_late()`. Runtime exports include `of_reserved_mem_device_init_by_idx()`, `of_reserved_mem_device_init_by_name()`, `of_reserved_mem_device_release()`, `of_reserved_mem_lookup()`, `of_reserved_mem_region_to_resource()`, `of_reserved_mem_region_to_resource_byname()`, and `of_reserved_mem_region_count()`. Internal helpers include `early_init_dt_alloc_reserved_memory_arch()`, `__reserved_mem_reserve_reg()`, `__reserved_mem_alloc_size()`, `fdt_fixup_reserved_mem_node()`, `fdt_validate_reserved_mem_node()`, and `__reserved_mem_init_node()`.

## Control flow and state
Early scan checks `/reserved-memory` cell counts and `ranges`, reserves static `reg` regions first, saves dynamic-size nodes, then allocates dynamic regions after static reservations to avoid overlap. Dynamic allocation honors alignment, `alloc-ranges`, and `no-map`, and can choose bottom-up or top-down based on nearby existing reservations. Late scan allocates a right-sized `reserved_mem` array, initializes static regions, and checks overlaps.

Compatible-specific reserved-memory ops are discovered from `__reservedmem_of_table` and can validate, fix up FDT nodes, initialize region data, and attach/release devices. Device assignments are tracked in `of_rmem_assigned_device_list` under a mutex so release can call matching `device_release` callbacks.

## Dependencies and integration
The file integrates with libfdt, memblock, kmemleak, reserved-memory driver tables, OF phandle parsing, resource APIs, and DMA setup in `device.c` for restricted pools.

## Risks and test signals
Risks include overlap, bad root cell counts, array overflow beyond `MAX_RESERVED_REGIONS`, failed memblock reservations, `no-map` conflicts with already reserved memory, callback failure rollback, and device assignment leaks. Signals are reserved-memory boot logs, overlap warnings, memblock maps, resource conversion tests, and driver-specific reserved-memory behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/of_reserved_mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/of_test.c -->
# sources/distributed-fs/ceph-client/drivers/of/of_test.c

## Purpose
`of_test.c` contains KUnit tests for selected OF core behavior. In this subset it verifies a loaded root DTB and validates resource-bound calculations for OF address resources.

## Important APIs, types, and functions
The `of_dtb` suite includes `of_dtb_root_node_found_by_path()` and `of_dtb_root_node_populates_of_root()`, gated by `of_dtb_test_init()`. The `of_address` suite defines `struct of_address_resource_bounds_case`, parameter descriptions, `of_address_resource_bounds_cases`, and `of_address_resource_bounds()` to exercise `__of_address_resource_bounds()`.

## Control flow and state
The DTB suite skips when helper logic determines there is no populated DT root or when early flattree is not enabled. It then checks `of_find_node_by_path("/")` and `of_root`. The address suite skips without `CONFIG_OF_ADDRESS`, runs parameterized start/size pairs, expects either success with exact `resource` start/end/size values or `-EOVERFLOW` for ranges that cannot fit `resource_size_t`.

## Dependencies and integration
The tests depend on KUnit, `of_root_kunit_skip()` from `of_kunit_helpers.c`, OF path lookup from `base.c`, and an address helper exported under the KUnit namespace. They import `EXPORTED_FOR_KUNIT_TESTING`.

## Risks and test signals
Coverage is focused rather than broad. It catches regressions in root availability assumptions and resource overflow handling, especially on 32-bit `resource_size_t` builds. It does not cover the wider IRQ, dynamic, reserved-memory, or kexec paths in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/of_test.c -->
