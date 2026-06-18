# subset-b-005893 Research

Grouped research report for the requested ceph-client Linux header subset. Each section preserves the original source path and is bounded by the required file markers for deterministic reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmzone.h -->
# sources/distributed-fs/ceph-client/include/linux/mmzone.h

## Purpose
`mmzone.h` is the core memory-management topology header for zones, nodes, zonelists, LRU vectors, per-CPU page caches, VM statistics, and sparse memory sections. It gives page allocator, reclaim, compaction, memory hotplug, NUMA, and sparsemem code a shared ABI for describing physical memory layout and allocator state.

## Important APIs, Types, and Functions
Key allocator constants include `MAX_PAGE_ORDER`, `MAX_ORDER_NR_PAGES`, `NR_PAGE_ORDERS`, `PAGE_ALLOC_COSTLY_ORDER`, `PAGE_BLOCK_MAX_ORDER`, `MAX_FOLIO_ORDER`, `MAX_FOLIO_NR_PAGES`, and vmemmap-tail sizing macros. `enum migratetype` defines allocator mobility classes (`MIGRATE_UNMOVABLE`, `MIGRATE_MOVABLE`, `MIGRATE_RECLAIMABLE`, `MIGRATE_HIGHATOMIC`, optional `MIGRATE_CMA`, `MIGRATE_ISOLATE`), with helpers such as `is_migrate_cma()`, `is_migrate_movable()`, and `migratetype_is_mergeable()`.

Statistics are declared through `enum zone_stat_item`, `enum node_stat_item`, `enum numa_stat_item`, and helpers `vmstat_item_print_in_thp()` and `vmstat_item_in_bytes()`. LRU state is represented by `enum lru_list`, `struct lruvec`, and, under `CONFIG_LRU_GEN`, `struct lru_gen_folio`, `struct lru_gen_mm_state`, `struct lru_gen_mm_walk`, and `struct lru_gen_memcg`.

The main persistent in-memory structures are `struct zone`, `struct zoneref`, `struct zonelist`, and `pg_data_t` (`struct pglist_data`). Accessors include `wmark_pages()`, `min_wmark_pages()`, `low_wmark_pages()`, `high_wmark_pages()`, `promo_wmark_pages()`, `zone_managed_pages()`, `zone_cma_pages()`, `zone_end_pfn()`, `zone_spans_pfn()`, `zone_is_initialized()`, `zone_is_empty()`, `zone_intersects()`, `managed_zone()`, `populated_zone()`, `zone_to_nid()`, `zone_idx()`, `is_highmem()`, and `has_managed_dma()`.

Allocation traversal and topology APIs include `build_all_zonelists()`, `__zone_watermark_ok()`, `zone_watermark_ok()`, `wakeup_kswapd()`, `kswapd_try_clear_hopeless()`, `kswapd_clear_hopeless()`, `kswapd_test_hopeless()`, `init_currently_empty_zone()`, `lruvec_init()`, `first_online_pgdat()`, `next_online_pgdat()`, `next_zone()`, `first_zones_zonelist()`, `next_zones_zonelist()`, `for_each_online_pgdat`, `for_each_zone`, `for_each_populated_zone`, and zonelist iteration macros.

Sparse memory support defines section/subsection geometry and state with `struct mem_section_usage`, `struct mem_section`, `SECTION_*` flag bits, `pfn_to_section_nr()`, `section_nr_to_pfn()`, `__nr_to_section()`, `__pfn_to_section()`, `present_section*()`, `valid_section*()`, `online_section*()`, `pfn_section_valid()`, `pfn_valid()`, `first_valid_pfn()`, `next_valid_pfn()`, and present/valid PFN iteration helpers.

## Control Flow and State
The header does not implement allocator algorithms directly, but defines the state those algorithms mutate. Allocation paths consult zonelists, zone watermarks, `managed_pages`, free areas, per-CPU pagesets, and migratetypes. Reclaim and compaction paths use `lruvec`, zone flags, compact cached PFNs, `kswapd` fields, and watermark state. Memory hotplug updates `present_pages`, section flags, and node/zone span fields under locks or hotplug synchronization.

Multi-gen LRU state flows through generation counters (`max_seq`, `min_seq`), per-generation folio lists, refault/eviction accounting, and memcg aging lists. Sparsemem validity checks flow from PFN to section number, then through `mem_section` flags and optional subsection bitmaps under scheduler RCU.

## State and Persistence Behavior
All state is in-kernel runtime state. It is not persisted across boots, but some fields are externally observable through `/proc/vmstat`, `/proc/meminfo`, debug paths, and memory hotplug/NUMA interfaces. `pg_data_t`, `zone`, `lruvec`, and `mem_section` instances are long-lived global topology records. Counters are a mix of atomic, per-CPU, seqlock-protected, RCU-protected, and lock-protected fields.

## Dependencies and Integration Points
This header depends on page flags/layout, `mm_types`, node masks, spinlocks, seqlocks, atomic operations, local locks, zswap, architecture page/sparsemem definitions, and optional hotplug/highmem/NUMA/CMA/compaction/LRU_GEN/ZONE_DEVICE features. It is consumed by `mm/page_alloc.c`, reclaim, compaction, memory hotplug, sparsemem, vmstat, NUMA balancing, zswap, and filesystem/page-cache code that needs zone or LRU information.

## Risks
Risks are mostly ABI and concurrency risks: incorrect zone flag packing breaks `struct page` flag decoding; mismatched stat enum ordering breaks vmstat output; stale section state can make `pfn_valid()` lie; missing locks around node/zone span updates can race allocator hot paths; and changing migratetype semantics can fragment memory or break CMA/isolation. Sparsemem code relies on flag-bit alignment assumptions and RCU lifetime rules.

## Test Signals
Useful signals include boot on FLATMEM and SPARSEMEM/VMEMMAP configs, memory hotplug online/offline, NUMA allocation fallback, CMA allocation, compaction and THP tests, `/proc/vmstat` sanity, page allocator stress, kswapd wakeup/reclaim tests, `pfn_valid()` boundary tests, and configs with/without `CONFIG_LRU_GEN`, `CONFIG_HIGHMEM`, `CONFIG_ZONE_DEVICE`, and `CONFIG_MEMORY_HOTPLUG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmzone.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mnt_idmapping.h -->
# sources/distributed-fs/ceph-client/include/linux/mnt_idmapping.h

## Purpose
`mnt_idmapping.h` defines VFS mount-idmapping helpers for converting between kernel IDs, filesystem IDs, and VFS-visible IDs. It supports idmapped mounts and preserves type separation between `kuid_t`/`kgid_t` and `vfsuid_t`/`vfsgid_t`.

## Important APIs, Types, and Functions
The header declares `struct mnt_idmap`, `nop_mnt_idmap`, `invalid_mnt_idmap`, and `init_user_ns`. It introduces `vfsuid_t` and `vfsgid_t`, validated with `static_assert()` to have the same layout as `kuid_t` and `kgid_t`. Helpers include `is_valid_mnt_idmap()`, `__vfsuid_val()`, `__vfsgid_val()`, `vfsuid_valid()`, `vfsgid_valid()`, equality helpers, `VFSUIDT_INIT`, `VFSGIDT_INIT`, `INVALID_VFSUID`, `INVALID_VFSGID`, `AS_KUIDT`, `AS_KGIDT`, `vfsgid_in_group_p()`, `mnt_idmap_get()`, `mnt_idmap_put()`, `make_vfsuid()`, `make_vfsgid()`, `from_vfsuid()`, `from_vfsgid()`, `vfsuid_has_fsmapping()`, `vfsgid_has_fsmapping()`, `vfsuid_has_mapping()`, `vfsgid_has_mapping()`, `vfsuid_into_kuid()`, `vfsgid_into_kgid()`, `mapped_fsuid()`, and `mapped_fsgid()`.

## Control Flow and State
Creation paths map a kernel UID/GID through a mount idmap and filesystem user namespace into a VFS ID. Commit paths convert VFS IDs back to kernel IDs after checking filesystem mappings. `mapped_fsuid()` and `mapped_fsgid()` use the current task credentials to initialize ownership for newly created filesystem objects.

## State and Persistence Behavior
The file only declares helpers and external idmap objects. Reference management is via `mnt_idmap_get()` and `mnt_idmap_put()`. Persistent filesystem ownership is affected indirectly when callers use mapped IDs for inode or quota creation.

## Dependencies and Integration Points
It depends on `linux/uidgid.h`, current credential helpers, user namespaces, and mount state from `struct vfsmount`. It is used by VFS inode creation, permission checks, quota code, and filesystems that support idmapped mounts.

## Risks
Mixing raw `uid_t`/`gid_t` with VFS IDs bypasses namespace checks. Treating `nop_mnt_idmap` as a normal idmap can skip fast-path semantics. Invalid IDs intentionally compare false, so callers must check validity before committing ownership. `CONFIG_MULTIUSER=n` forces value accessors to zero, which changes tests and assumptions.

## Test Signals
Exercise idmapped mount creation, inode ownership under user namespaces, invalid mapping failures, group membership checks, `nop_mnt_idmap` behavior, and builds with and without `CONFIG_MULTIUSER`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mnt_idmapping.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mnt_namespace.h -->
# sources/distributed-fs/ceph-client/include/linux/mnt_namespace.h

## Purpose
`mnt_namespace.h` declares the kernel-facing mount namespace lifecycle and `/proc` mount-view operations.

## Important APIs, Types, and Functions
It forward-declares `struct mnt_namespace`, `struct fs_struct`, `struct user_namespace`, and `struct ns_common`; exposes `init_mnt_ns`; declares `copy_mnt_ns()`, `put_mnt_ns()`, `from_mnt_ns()`, and the `proc_mounts_operations`, `proc_mountinfo_operations`, and `proc_mountstats_operations` file operations. `DEFINE_FREE(put_mnt_ns, ...)` provides cleanup-scope release for namespace pointers.

## Control Flow and State
Namespace creation/copy code calls `copy_mnt_ns()` with clone flags, a source namespace, target user namespace, and filesystem struct. Namespace users release references with `put_mnt_ns()` or the cleanup helper. `/proc` operations render namespace mount lists and statistics.

## State and Persistence Behavior
Mount namespace state is process namespace state, retained by reference counts and visible through procfs. It is not on-disk persistence, but it controls the mounted tree visible to processes.

## Dependencies and Integration Points
It integrates with namespace core (`ns_common`), VFS mount management, process `fs_struct`, user namespaces, cleanup helpers, and procfs.

## Risks
The main risk is lifetime: failing to drop namespace references leaks mount namespaces, while dropping error pointers or null pointers incorrectly is guarded by the cleanup macro. Copy semantics must respect user namespace and clone flag constraints.

## Test Signals
Signals include mount namespace clone/unshare tests, proc mountinfo/mountstats visibility, namespace teardown leak checks, and cleanup-helper compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mnt_namespace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mod_devicetable.h -->
# sources/distributed-fs/ceph-client/include/linux/mod_devicetable.h

## Purpose
`mod_devicetable.h` defines the device-ID table records exported by modules and parsed by `scripts/mod/file2alias.c` to generate modaliases for userspace autoloading. It is a cross-subsystem ABI header and must stay synchronized with alias generation logic.

## Important APIs, Types, and Functions
The header defines `kernel_ulong_t`, `PCI_ANY_ID`, bus-specific match flags, modalias prefixes, and a large set of ID structs: `pci_device_id`, `ieee1394_device_id`, `usb_device_id`, `hid_device_id`, `ccw_device_id`, `ap_device_id`, `css_device_id`, `acpi_device_id`, `pnp_device_id`, `pnp_card_device_id`, `serio_device_id`, `hda_device_id`, `sdw_device_id`, `of_device_id`, `vio_device_id`, `pcmcia_device_id`, `input_device_id`, `eisa_device_id`, `parisc_device_id`, `sdio_device_id`, `ssb_device_id`, `bcma_device_id`, `virtio_device_id`, `hv_vmbus_device_id`, `rpmsg_device_id`, `i2c_device_id`, `pci_epf_device_id`, `i3c_device_id`, `spi_device_id`, `slim_device_id`, `apr_device_id`, `spmi_device_id`, `dmi_system_id`, `platform_device_id`, `mdio_device_id`, `zorro_device_id`, `isapnp_device_id`, `amba_id`, `mips_cdmm_device_id`, `x86_cpu_id`, `cpu_feature`, `ipack_device_id`, `mei_cl_device_id`, `rio_device_id`, `mcb_device_id`, `ulpi_device_id`, `fsl_mc_device_id`, `tb_service_id`, `typec_device_id`, `tee_client_device_id`, `wmi_device_id`, `mhi_device_id`, `auxiliary_device_id`, `ssam_device_id`, `dfl_device_id`, `ishtp_device_id`, `cdx_device_id`, `vchiq_device_id`, and `coreboot_device_id`.

## Control Flow and State
Driver code declares static ID arrays and exports them with `MODULE_DEVICE_TABLE()`. During build, `file2alias.c` reads these structures from module ELF metadata and emits modalias patterns. At runtime, bus cores compare device attributes against these tables and pass matched entries to probe callbacks.

## State and Persistence Behavior
The tables are static read-only module data and may also become userspace-visible module alias metadata. `driver_data`/`driver_info` fields persist for the lifetime of the driver table and often encode quirk flags or indices.

## Dependencies and Integration Points
The header is tightly coupled to bus cores, module metadata generation, kmod autoloading, `file2alias.c`, uevent/modalias strings, and userspace tools such as udev/modprobe. Some structures use `uuid_t`, `guid_t`, MEI, PCI, USB, ACPI, OF, DMI, and network PHY conventions.

## Risks
Any layout, name, size, or field-order change can break module alias generation or userspace ABI. Pointer-sized `kernel_ulong_t` makes cross-architecture output sensitive. Match flags must align with bus matching code. Tables often require zero terminators; missing terminators can overrun matching loops.

## Test Signals
Build `modpost`, inspect generated `modules.alias`, run hotplug/autoload tests across representative buses, verify 32-bit and 64-bit module builds, and compile drivers using each table macro.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mod_devicetable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/module.h -->
# sources/distributed-fs/ceph-client/include/linux/module.h

## Purpose
`module.h` is the main public kernel header for loadable module metadata, lifecycle entry points, module state, module memory layout, symbol access, reference management, sysfs/kallsyms integration, taint/signature state, and feature sections.

## Important APIs, Types, and Functions
It defines `MODULE_NAME_LEN`, `struct modversion_info`, `struct module_kobject`, `struct module_attribute`, `struct module_version_attribute`, `module_init()`, `module_exit()`, initcall aliases for modules, `MODULE_ALIAS`, `MODULE_SOFTDEP`, `MODULE_WEAKDEP`, `MODULE_FILE`, `MODULE_LICENSE`, `MODULE_AUTHOR`, `MODULE_DESCRIPTION`, `MODULE_DEVICE_TABLE`, `MODULE_VERSION`, `MODULE_FIRMWARE`, and `MODULE_IMPORT_NS`.

Core state types include `enum module_state`, `struct mod_tree_node`, `enum mod_mem_type`, `struct module_memory`, `struct mod_kallsyms`, optional `struct klp_modinfo`, and the large `struct module`. `struct module` tracks state, list membership, name, build ID, sysfs objects, exported symbols, parameter arrays, signature status, init function, memory regions, arch data, taints, exception tables, kallsyms, per-CPU storage, trace/BPF/debug/livepatch/KUnit/static-call/FTRACE data, unload dependency lists, exit callback, refcount, constructors, error injection, and dynamic debug data.

Runtime APIs include `__symbol_get()`, `__symbol_get_gpl()`, `symbol_get()`, `kallsyms_symbol_value()`, `module_is_live()`, `module_is_coming()`, `__module_text_address()`, `__module_address()`, `is_module_address()`, `is_module_percpu_address()`, `within_module_mem_type()`, `within_module_core()`, `within_module_init()`, `within_module()`, `find_module()`, `try_module_get()`, `module_put()`, `__module_get()`, `module_name()`, `module_buildid()`, `dereference_module_function_descriptor()`, module notifiers, `print_modules()`, `module_requested_async_probing()`, `is_livepatch_module()`, and kallsyms lookup functions.

## Control Flow and State
For built-ins, `module_init()` maps to initcall sections and `module_exit()` maps to an exitcall that is discarded for non-modular use. For modules, `module_init()` and `module_exit()` alias driver functions to `init_module` and `cleanup_module`. Loading moves `struct module` through `UNFORMED`, `COMING`, and `LIVE`; unloading moves it toward `GOING`, checks reference counts, runs exit callbacks, removes sysfs/kallsyms/trace state, and frees memory.

Symbol access flows through exported symbol metadata and optional GPL-only enforcement. Address lookup flows through module memory regions and optional tree lookup. Config-disabled paths provide stubs so code compiles when modules or kallsyms are absent.

## State and Persistence Behavior
Module state is runtime kernel state, surfaced through sysfs, kallsyms, proc/debug interfaces, taint flags, and module lists. Module metadata persists in the `.ko` ELF and `.modinfo` sections; runtime `struct module` data persists while the module is loaded.

## Dependencies and Integration Points
The header integrates with kobjects/sysfs, module parameters, ELF, export symbols, kallsyms, exception tables, livepatch, tracepoints, SRCU, BPF events, BTF, jump labels, ftrace, kprobes, static calls, KUnit, printk indexing, constructors, module signatures, retpoline checks, and architecture-specific module layout.

## Risks
Module lifetime is sensitive: missing `module_put()` leaks or blocks unload, while using module memory after `GOING` risks UAF. Metadata macros affect build output and autoloading. `struct module` layout is highly config-dependent. GPL-only symbol enforcement and signature state are policy-critical. Address lookup must handle init memory that can be freed after initialization.

## Test Signals
Load/unload modules repeatedly, exercise dependency/refcount paths, verify sysfs attributes and parameters, inspect kallsyms/address lookup, test signature enforcement configs, build without `CONFIG_MODULES`, run livepatch and tracing module tests, and compile representative drivers using `MODULE_DEVICE_TABLE()` and metadata macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/module.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/module_signature.h -->
# sources/distributed-fs/ceph-client/include/linux/module_signature.h

## Purpose
`module_signature.h` declares module signature validation support.

## Important APIs, Types, and Functions
It includes UAPI `struct module_signature` and declares `mod_check_sig(const struct module_signature *ms, size_t file_len, const char *name)`.

## Control Flow and State
The module loader reads appended signature metadata from a module file and calls `mod_check_sig()` with the signature descriptor, total file length, and module name. The implementation validates bounds and cryptographic signature data elsewhere.

## State and Persistence Behavior
Signature data is persisted in the module file. Runtime validation result is reflected in module loading policy and `struct module::sig_ok` when module signature support is enabled.

## Dependencies and Integration Points
It integrates with the module loader, public-key/keyring verification, UAPI signature layout, and module signature enforcement policy.

## Risks
Incorrect file length or descriptor validation can allow malformed modules, reject valid modules, or misreport signature status. It is security-sensitive and must be tested with enforcement enabled and disabled.

## Test Signals
Load signed, unsigned, truncated, and tampered modules; verify enforcement and permissive modes; and check error reporting names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/module_signature.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/module_symbol.h -->
# sources/distributed-fs/ceph-client/include/linux/module_symbol.h

## Purpose
`module_symbol.h` defines small symbol metadata helpers shared by module and symbol tooling.

## Important APIs, Types, and Functions
It defines `enum ksym_flags` with `KSYM_FLAG_GPL_ONLY` and `is_mapping_symbol()`, which filters ELF mapping symbols starting with `.L`, `L0`, or `$`.

## Control Flow and State
Symbol consumers call `is_mapping_symbol()` while walking ELF or kallsyms data to skip local mapping artifacts that should not be treated as real exported/kernel symbols.

## State and Persistence Behavior
No runtime state is owned here. Flags are encoded alongside symbol metadata.

## Dependencies and Integration Points
It integrates with module symbol export handling, kallsyms, modpost, and architecture ELF symbol conventions.

## Risks
Over-filtering can hide legitimate symbols; under-filtering pollutes kallsyms/export processing with mapping markers. GPL flag semantics must match export enforcement.

## Test Signals
Build modules on architectures that emit mapping symbols, inspect kallsyms/export lists, and verify GPL-only symbol checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/module_symbol.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/moduleloader.h -->
# sources/distributed-fs/ceph-client/include/linux/moduleloader.h

## Purpose
`moduleloader.h` declares architecture hooks used by the generic module loader for ELF validation, section adjustment, relocation, finalization, and cleanup.

## Important APIs, Types, and Functions
The header declares `module_elf_check_arch()`, `module_frob_arch_sections()`, `arch_mod_section_prepend()`, `module_init_section()`, `module_exit_section()`, `module_init_layout_section()`, `apply_relocate()`, `apply_relocate_add()`, optional livepatch `clear_relocate_add()`, `module_finalize()`, `flush_module_init_free_work()`, `module_arch_cleanup()`, and `module_arch_freeing_init()`.

## Control Flow and State
During load, the module loader validates ELF headers, lets architecture code adjust sections, applies REL or RELA relocations, finalizes architecture-specific state, and later frees init memory. On unload or failure, architecture cleanup hooks release any arch-owned state. Unsupported relocation formats return `-ENOEXEC` via stubs.

## State and Persistence Behavior
The header does not own persistent state, but its hooks mutate `struct module` memory, architecture-specific fields, relocation targets, and livepatch relocation cleanup state.

## Dependencies and Integration Points
It depends on `linux/module.h` and ELF definitions, and integrates with architecture module backends, livepatch, init/exit section classification, and module memory freeing.

## Risks
Relocation bugs corrupt executable module memory. Section classification affects whether memory is kept, freed, or considered init/core by address lookups. Livepatch relocation cleanup is architecture-sensitive. Stubs must only be used when the corresponding relocation format is genuinely unsupported.

## Test Signals
Load modules with REL and RELA relocations on supported architectures, test module unload/reload, run livepatch reload scenarios, verify init memory freeing, and build architectures with only one relocation format enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/moduleloader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/moduleparam.h -->
# sources/distributed-fs/ceph-client/include/linux/moduleparam.h

## Purpose
`moduleparam.h` provides the declaration and parsing framework for module parameters and built-in kernel parameters. It creates `.modinfo` metadata and `__param` table entries, supports sysfs exposure, and supplies standard type parsers.

## Important APIs, Types, and Functions
Important constants and macros include `__MODULE_NAME_LEN`, `MODULE_PARAM_PREFIX`, `MODULE_INFO()`, `MODULE_PARM_DESC()`, `module_param()`, `module_param_unsafe()`, `module_param_named()`, `module_param_cb()`, staged parameter callbacks (`core_param_cb`, `postcore_param_cb`, `arch_param_cb`, `subsys_param_cb`, `fs_param_cb`, `device_param_cb`, `late_param_cb`), `__module_param_call()`, `module_param_call()`, `core_param()`, `module_param_string()`, array parameter macros, and hardware parameter macros.

Core types are `struct kernel_param_ops`, `struct kernel_param`, `struct kparam_string`, `struct kparam_array`, and `enum hwparam_type`. Standard ops and parser functions are declared for byte, short, int, uint, long, ulong, ullong, hexint, charp, bool, bool-enable-only, invbool, bint, arrays, and strings. Parser APIs include `parameq()`, `parameqn()`, `parse_args()`, `kernel_param_lock()`, `kernel_param_unlock()`, `module_destroy_params()`, `module_param_sysfs_setup()`, and `module_param_sysfs_remove()`.

## Control Flow and State
Parameter declaration macros perform compile-time type checks, emit metadata, and place `struct kernel_param` entries in the `__param` section. Boot or module load code calls `parse_args()` over a parameter table and dispatches each value to `kernel_param_ops::set`. Sysfs read/write paths use `get`/`set` operations and optional `param_lock`. Module unload destroys dynamically allocated parameter values such as `charp`.

## State and Persistence Behavior
Parameter values live in module/global variables. Metadata persists in module ELF sections. Sysfs exposes runtime state under module parameter directories when permissions allow. Unsafe and hardware flags affect taint/lockdown policy.

## Dependencies and Integration Points
It integrates with initcall ordering, sysfs, module loading, command-line parsing, lockdown, tainting, and driver configuration. It also relies on permission verification and section placement.

## Risks
Writable parameters require locking around concurrent use. `charp` parameters can be reallocated and freed. Permission mistakes expose sensitive or unsafe controls. Incorrect type checks or array sizes can corrupt memory. Hardware parameters must respect lockdown restrictions.

## Test Signals
Boot parameter parsing, module insertion with valid/invalid arguments, sysfs reads/writes under concurrency, unload of charp parameters, array parsing, unsafe taint behavior, lockdown rejection of hardware parameters, and builds with/without `CONFIG_SYSFS` and `CONFIG_MODULES`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/moduleparam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/most.h -->
# sources/distributed-fs/ceph-client/include/linux/most.h

## Purpose
`most.h` defines the MOST (Media Oriented Systems Transport) core API for hardware driver modules, application/interface modules, components, channels, and MOST buffer objects.

## Important APIs, Types, and Functions
It defines interface types (`enum most_interface_type`), channel directions, channel data types, and MBO status flags. Data structures include `struct most_channel_capability`, `struct most_channel_config`, `struct mbo`, `struct most_interface`, and `struct most_component`.

Registration and channel APIs include `most_register_interface()`, `most_deregister_interface()`, `most_submit_mbo()`, `most_stop_enqueue()`, `most_resume_enqueue()`, `most_register_component()`, `most_deregister_component()`, `most_get_mbo()`, `most_put_mbo()`, `channel_has_mbo()`, `most_start_channel()`, `most_stop_channel()`, configfs registration, link add/remove, channel configuration setters, `most_cfg_complete()`, and `most_interface_register_notify()`.

## Control Flow and State
Hardware drivers allocate and initialize `struct most_interface`, then register it with the core. Components register `struct most_component` and are connected to channels. The core allocates MBOs and hands them to hardware drivers through `enqueue()`. Ownership transfers to the hardware driver until it fills status/processed length and calls `mbo->complete()`. Channel close flows through `poison_channel()` and requires all outstanding MBOs to be returned.

## State and Persistence Behavior
MOST state is runtime device/channel/component state. Capabilities and configs are exposed through sysfs/configfs. MBOs are recycled or freed by the core after completion. The header explicitly states the core does not track MBOs while owned by hardware drivers.

## Dependencies and Integration Points
It depends on device model types, DMA addressing, modules, configfs, sysfs, and MOST core implementation. It integrates adapter drivers (USB, PCIe, MediaLB, etc.) with higher-level application modules.

## Risks
MBO ownership is the largest risk: hardware drivers must return every MBO before deregistration or unload, or memory leaks and dangling DMA buffers occur. Calling core-owned fields while an HDM owns the MBO violates the contract. Channel config values may be adjusted by hardware callbacks and must be honored by components.

## Test Signals
Register/deregister HDM drivers under load, start/stop channels, poison channels with outstanding MBOs, verify DMA allocation/free pairing, configfs link creation/removal, sysfs capability reporting, and fault injection for enqueue failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/most.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mount.h -->
# sources/distributed-fs/ceph-client/include/linux/mount.h

## Purpose
`mount.h` declares the core VFS mount object, mount flags, write access helpers, mount creation/destruction APIs, expiry helpers, mountpoint checks, and kernel mount helpers.

## Important APIs, Types, and Functions
It defines `enum mount_flags`, including user-settable flags (`MNT_NOSUID`, `MNT_NODEV`, `MNT_NOEXEC`, atime flags, `MNT_READONLY`, `MNT_NOSYMFOLLOW`), internal flags (`MNT_INTERNAL`, `MNT_DOOMED`, `MNT_SYNC_UMOUNT`, `MNT_LOCKED`), lock flags, and masks. `struct vfsmount` contains `mnt_root`, `mnt_sb`, `mnt_flags`, and `mnt_idmap`. `mnt_idmap()` reads the mount idmap with release/acquire pairing expectations.

Declared APIs include `mnt_want_write()`, `mnt_want_write_file()`, `mnt_drop_write()`, `mnt_drop_write_file()`, `mntput()`, `mntget()`, `mnt_make_shortterm()`, `mnt_clone_internal()`, `__mnt_is_readonly()`, `mnt_may_suid()`, `clone_private_mount()`, `mnt_get_write_access()`, `mnt_put_write_access()`, `fc_mount()`, `fc_mount_longterm()`, `vfs_create_mount()`, `vfs_kern_mount()`, expiry helpers, `path_is_mountpoint()`, `our_mnt()`, `kern_mount()`, `kern_unmount()`, `may_umount_tree()`, `may_umount()`, `do_mount()`, path collection helpers, `kern_unmount_array()`, and `cifs_root_data()`.

## Control Flow and State
Mount creation flows from filesystem context or filesystem type into a `vfsmount`. Write paths first acquire mount write access and drop it afterward. Unmount paths test whether trees can be unmounted, mark/expire mounts, and release references. Idmapped mounts read `mnt_idmap` through `mnt_idmap()`.

## State and Persistence Behavior
`vfsmount` is runtime VFS state. It references persistent superblocks/dentries but is itself namespace/mount-table state. Mount flags are user-visible through mount APIs and proc views; write access counters and internal flags are transient.

## Dependencies and Integration Points
It integrates with superblocks, dentries, paths, file descriptors, filesystem contexts, user namespaces, mount namespaces, idmapping, CIFS root parsing, and kernel-internal mounts.

## Risks
Incorrect write-access pairing can allow writes on read-only mounts or block unmount. Mount flag locking must prevent privilege changes. `mnt_idmap()` ordering matters for idmapped mount setup. Reference leaks in `mntget()`/`mntput()` keep mounts alive.

## Test Signals
Mount/umount stress, remount read-only/write tests, idmapped mounts, nosuid/nodev/noexec enforcement, mount expiry, kernel mount/unmount helpers, and CIFS root mount parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mount.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/moxtet.h -->
# sources/distributed-fs/ceph-client/include/linux/moxtet.h

## Purpose
`moxtet.h` defines the Turris MOX module configuration bus interface, including module IDs, bus state, IRQ mapping, driver registration, and device access helpers.

## Important APIs, Types, and Functions
It defines `TURRIS_MOX_MAX_MODULES`, CPU/module ID enums, `MOXTET_NIRQS`, `struct moxtet`, `struct moxtet_driver`, `to_moxtet_driver()`, `__moxtet_register_driver()`, `moxtet_unregister_driver()`, `moxtet_register_driver()`, `module_moxtet_driver()`, `struct moxtet_device`, `moxtet_device_read()`, `moxtet_device_write()`, `moxtet_device_written()`, and `to_moxtet_device()`.

## Control Flow and State
The bus tracks detected modules in `moxtet::modules`, transmit bytes in `tx`, and IRQ state in an embedded domain/chip/mask/existence/position table. Drivers register with an ID table and device-driver object. Device read/write helpers communicate one-byte state to individual MOX modules.

## State and Persistence Behavior
State is runtime bus/device state. Debugfs state is optional. IRQ masks and module arrays persist while the bus device exists.

## Dependencies and Integration Points
It depends on the Linux device model, IRQ domains/chips, mutexes, modules, and optional debugfs. It integrates Turris MOX module drivers with the platform bus implementation.

## Risks
IRQ position and mask bookkeeping must match physical modules. The fixed module count limits probing. Device read/write ordering must respect the bus mutex. Driver registration lifetime follows device-model rules.

## Test Signals
Probe systems with each module ID, test IRQ delivery/masking, register/unregister module drivers, validate debugfs output, and read/write devices under concurrent access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/moxtet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mpage.h -->
# sources/distributed-fs/ceph-client/include/linux/mpage.h

## Purpose
`mpage.h` declares multipage block I/O helpers for filesystems that map page-cache folios to disk blocks through `get_block_t`.

## Important APIs, Types, and Functions
Under `CONFIG_BLOCK`, it declares `mpage_readahead()`, `mpage_read_folio()`, `__mpage_writepages()`, and inline `mpage_writepages()` which calls `__mpage_writepages()` with no custom write-folio callback.

## Control Flow and State
Read paths use readahead or single-folio helpers to build BIOs containing multiple page-cache pages. Writeback calls `mpage_writepages()` or `__mpage_writepages()` to walk dirty folios, translate blocks with `get_block`, and submit block I/O.

## State and Persistence Behavior
The header owns no state. Its helpers operate on page-cache and mapping/writeback state and persist data through the block device/filesystem.

## Dependencies and Integration Points
It depends on block layer support, `address_space`, `folio`, `writeback_control`, `readahead_control`, and filesystem block mapping callbacks.

## Risks
Incorrect `get_block` behavior can corrupt I/O ranges. Filesystems with complex extents, holes, or delayed allocation may need custom write callbacks. It is absent when `CONFIG_BLOCK` is disabled.

## Test Signals
Filesystem read/writeback tests using mpage helpers, readahead behavior, sparse file reads, writeback under memory pressure, and no-block configuration builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mpage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mpi.h -->
# sources/distributed-fs/ceph-client/include/linux/mpi.h

## Purpose
`mpi.h` declares the kernel multi-precision integer library, derived from GnuPG/GMP-style limb arithmetic, for cryptographic and big-number operations.

## Important APIs, Types, and Functions
It defines limb sizing macros, `mpi_limb_t`, `mpi_limb_signed_t`, `struct gcry_mpi`, and `MPI`. APIs cover allocation (`mpi_alloc()`, `mpi_free()`, `mpi_resize()`, `mpi_copy()`), encoding/decoding (`mpi_read_raw_data()`, `mpi_read_from_buffer()`, `mpi_read_raw_from_sgl()`, `mpi_get_buffer()`, `mpi_read_buffer()`, `mpi_write_to_sgl()`), arithmetic (`mpi_add()`, `mpi_sub()`, `mpi_addm()`, `mpi_subm()`, `mpi_mul()`, `mpi_mulm()`, `mpi_mod()`, `mpi_powm()`), division/remainder (`mpi_tdiv_r()`, `mpi_fdiv_r()`), comparison (`mpi_cmp_ui()`, `mpi_cmp()`), bit operations (`mpi_normalize()`, `mpi_get_nbits()`, `mpi_test_bit()`, `mpi_set_bit()`, `mpi_rshift()`), and `mpi_get_size()`.

## Control Flow and State
Callers allocate an `MPI`, read or construct limb data, perform arithmetic, and serialize results into buffers or scatterlists. Most functions return negative errors on allocation or invalid input failure.

## State and Persistence Behavior
`struct gcry_mpi` owns dynamically allocated limb storage. Sensitive values may be flagged for secure memory by implementation conventions. The header itself does not persist data, but consumers may encode MPI values into keys/signatures.

## Dependencies and Integration Points
It depends on Linux integer types and scatterlists. It is typically used by crypto, public-key, signature, and key parsing code.

## Risks
Big-number code is security-sensitive: length/sign mistakes, non-normalized values, scatterlist truncation, and allocation failures can break signature verification. Arithmetic may not be constant-time unless implementations guarantee it.

## Test Signals
Known-answer cryptographic tests, encode/decode round trips, scatterlist boundary cases, modular exponentiation, negative number handling, allocation failure injection, and 32-bit/64-bit limb builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mpi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mpls.h -->
# sources/distributed-fs/ceph-client/include/linux/mpls.h

## Purpose
`mpls.h` provides kernel-side convenience masks for decoded MPLS label stack fields.

## Important APIs, Types, and Functions
It includes UAPI MPLS definitions and derives `MPLS_TTL_MASK`, `MPLS_BOS_MASK`, `MPLS_TC_MASK`, and `MPLS_LABEL_MASK` by shifting the UAPI label-stack masks.

## Control Flow and State
No functions are implemented. Callers use the masks while parsing or constructing MPLS label stack entries.

## State and Persistence Behavior
No state is owned. MPLS packet metadata is transient network data.

## Dependencies and Integration Points
It depends on `uapi/linux/mpls.h` and integrates with MPLS routing, tunnel, and packet parsing code.

## Risks
Masks must stay aligned with UAPI shift definitions. Incorrect masks corrupt TTL, bottom-of-stack, traffic class, or label extraction.

## Test Signals
MPLS packet parse/build tests and compile checks against UAPI definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mpls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mpls_iptunnel.h -->
# sources/distributed-fs/ceph-client/include/linux/mpls_iptunnel.h

## Purpose
`mpls_iptunnel.h` exposes kernel code to the UAPI definitions for MPLS IP tunnel attributes.

## Important APIs, Types, and Functions
It only includes `uapi/linux/mpls_iptunnel.h`.

## Control Flow and State
No local control flow exists. Tunnel code uses the imported UAPI constants and structures.

## State and Persistence Behavior
No state is declared here. Tunnel configuration is managed by networking subsystems and netlink.

## Dependencies and Integration Points
It integrates MPLS tunnel implementation code with userspace netlink ABI definitions.

## Risks
The main risk is assuming additional local helpers exist; this file is a thin ABI include. UAPI changes drive behavior.

## Test Signals
MPLS tunnel netlink configuration tests and compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mpls_iptunnel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mroute.h -->
# sources/distributed-fs/ceph-client/include/linux/mroute.h

## Purpose
`mroute.h` declares IPv4 multicast routing interfaces and IPv4-specific MFC cache entries built on top of `mroute_base.h`.

## Important APIs, Types, and Functions
It provides `ip_mroute_opt()`, `ip_mroute_setsockopt()`, `ip_mroute_getsockopt()`, `ipmr_ioctl()`, `ipmr_compat_ioctl()`, `ip_mr_init()`, `ipmr_rule_default()`, `ipmr_sk_ioctl()`, `VIFF_STATIC`, `struct mfc_cache_cmp_arg`, `struct mfc_cache`, and `ipmr_get_route()`. Disabled `CONFIG_IP_MROUTE` builds return `-ENOPROTOOPT`, `-ENOIOCTLCMD`, default success for init, and conservative rule behavior.

## Control Flow and State
Socket options and ioctls configure multicast routing tables and VIFs. IPv4 route cache entries embed common `struct mr_mfc` state first, then add IPv4 group/origin keys used by rhashtable comparisons. Route lookup fills `rtmsg` data for userspace queries.

## State and Persistence Behavior
State lives in per-network-namespace multicast route tables, VIFs, and MFC caches declared in the base header. Entries are runtime networking state and are removed on namespace/table teardown.

## Dependencies and Integration Points
It depends on IPv4 address types, PIM definitions, fib rules/notifiers, UAPI mroute constants, sockptr, and `mroute_base.h`. It integrates with raw sockets, routing daemons, netlink route dumps, and multicast forwarding.

## Risks
Disabled stubs must preserve caller expectations. The embedded common struct must remain first for casting. Wrong key comparison breaks multicast forwarding. Userspace ioctl buffers must match UAPI layouts.

## Test Signals
IPv4 multicast routing daemon tests, setsockopt/getsockopt/ioctl coverage, route dump queries, multi-table rules, disabled-config behavior, and forwarding counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mroute.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mroute6.h -->
# sources/distributed-fs/ceph-client/include/linux/mroute6.h

## Purpose
`mroute6.h` declares IPv6 multicast routing interfaces and IPv6-specific MFC cache entries built on `mroute_base.h`.

## Important APIs, Types, and Functions
It defines `ip6_mroute_opt()`, `ip6_mroute_setsockopt()`, `ip6_mroute_getsockopt()`, `ip6_mr_input()`, `ip6mr_compat_ioctl()`, `ip6_mr_init()`, `ip6_mr_output()`, `ip6_mr_cleanup()`, `ip6mr_ioctl()`, `ip6mr_rule_default()`, `VIFF_STATIC`, `struct mfc6_cache_cmp_arg`, `struct mfc6_cache`, `MFC_ASSERT_THRESH`, `ip6mr_get_route()`, `mroute6_is_socket()`, `ip6mr_sk_done()`, and `ip6mr_sk_ioctl()`. Stubs preserve normal IPv6 output when multicast routing is disabled.

## Control Flow and State
IPv6 multicast socket options/ioctls configure routing tables. Input and output hooks route multicast packets through MFC/VIF state when enabled; disabled output falls back to `ip6_output()`. `ip6mr_sk_ioctl()` copies UAPI request structs through `sock_ioctl_inout()` for supported commands.

## State and Persistence Behavior
Runtime state resides in per-net IPv6 multicast routing tables, shared base MFC/VIF structures, and socket associations. The header adds IPv6 address keys and assert-throttle timing.

## Dependencies and Integration Points
It depends on IPv6 networking, PIM, skbuffs, net namespaces, fib rules, sockptr, UAPI mroute6, and shared multicast routing base code.

## Risks
IPv6 disabled stubs must avoid breaking normal output. Usercopy ioctl wrappers must use correct request sizes. Multi-table rule defaults depend on config. MFC key layout must match rhashtable comparison code.

## Test Signals
IPv6 multicast forwarding, PIM daemon operations, ioctl compatibility tests, route dumps, disabled-config output tests, multi-table rules, and assert rate-limiting behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mroute6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mroute_base.h -->
# sources/distributed-fs/ceph-client/include/linux/mroute_base.h

## Purpose
`mroute_base.h` provides common multicast routing table, virtual interface, multicast forwarding cache, notifier, lookup, dump, and proc-iteration infrastructure shared by IPv4 and IPv6 multicast routing.

## Important APIs, Types, and Functions
Core types include `struct vif_device`, `struct vif_entry_notifier_info`, `struct mr_mfc`, `struct mfc_entry_notifier_info`, `struct mr_table_ops`, `struct mr_table`, `struct mr_vif_iter`, and `struct mr_mfc_iter`. Helpers include `mr_call_vif_notifier()`, `mr_call_vif_notifiers()`, `VIF_EXISTS`, `mr_cache_put()`, `mr_cache_hold()`, `mr_call_mfc_notifier()`, `mr_call_mfc_notifiers()`, `mr_can_free_table()`, `vif_device_init()`, `mr_table_free()`, `mr_table_alloc()`, `mr_mfc_find_parent()`, `mr_mfc_find_any_parent()`, `mr_mfc_find_any()`, `mr_mfc_find()`, `mr_fill_mroute()`, `mr_table_dump()`, `mr_rtm_dumproute()`, `mr_dump()`, and proc sequence helpers.

## Control Flow and State
Protocol-specific code allocates `struct mr_table` with hash parameters and an expire timer. VIF operations initialize table entries and emit FIB notifications. MFC entries are unresolved with queued skbs until userspace resolves them, or resolved with TTL arrays, counters, last-use/assert timestamps, and refcounts. Route dumps walk hash/list state under appropriate locks and RCU. Proc iteration switches between unresolved and resolved cache lists, unlocking in `mr_mfc_seq_stop()`.

## State and Persistence Behavior
State is per-network-namespace runtime routing state. VIFs hold RCU-protected device pointers and ref trackers. MFC entries are refcounted and freed via RCU callback. Unresolved entries use timers and queues; resolved entries hold atomic byte/packet/wrong-if counters.

## Dependencies and Integration Points
It depends on netdevice, rhashtable, spinlocks, net namespaces, sockets, fib notifiers, IP FIB, timers, RCU work, seq_file, and netlink dump paths. IPv4 and IPv6 wrappers provide protocol-specific keys and route filling.

## Risks
RCU and refcount correctness are critical. Notifier callers require correct RTNL assertions and sequence increments. Unresolved queue length must be bounded. Proc iteration must unlock the right list. Common structs are embedded first in protocol-specific cache structs for casting.

## Test Signals
IPv4/IPv6 multicast route add/delete, unresolved queue expiry, hardware offload notification, netns teardown, route dumps, proc VIF/MFC reads, refcount/RCU debug, and `CONFIG_IP_MROUTE_COMMON=n` stub builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mroute_base.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/msdos_fs.h -->
# sources/distributed-fs/ceph-client/include/linux/msdos_fs.h

## Purpose
`msdos_fs.h` imports FAT/MS-DOS filesystem UAPI definitions and provides a kernel helper for validating FAT boot-sector media bytes.

## Important APIs, Types, and Functions
It includes `uapi/linux/msdos_fs.h` and defines `fat_valid_media(u8 media)`, accepting fixed-disk media values `>= 0xf8` and floppy marker `0xf0`.

## Control Flow and State
FAT code calls `fat_valid_media()` while parsing boot sectors or validating filesystem metadata.

## State and Persistence Behavior
No state is owned. The helper validates on-disk FAT metadata.

## Dependencies and Integration Points
It integrates with FAT filesystem parsing and UAPI FAT constants.

## Risks
Changing accepted media bytes could reject valid FAT volumes or accept corrupt metadata.

## Test Signals
Mount FAT images with common media bytes, reject invalid boot sectors, and compile FAT code using UAPI definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/msdos_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/msdos_partition.h -->
# sources/distributed-fs/ceph-client/include/linux/msdos_partition.h

## Purpose
`msdos_partition.h` defines the classic MBR partition entry layout, label magic, and common system-indicator partition type values.

## Important APIs, Types, and Functions
It defines `MSDOS_LABEL_MAGIC`, packed `struct msdos_partition`, and `enum msdos_sys_ind` values for extended partitions, Linux data/LVM/RAID, Solaris, disk managers, BSDs, Minix, and UnixWare/Hurd/SCO.

## Control Flow and State
Partition parsers read packed entries from sector 0 or extended boot records, validate magic, interpret CHS/LBA fields, and use `sys_ind` to classify partitions.

## State and Persistence Behavior
The struct maps on-disk MBR/EBR data. No runtime state is owned here.

## Dependencies and Integration Points
It integrates with block partition scanning and disk-label code. Endianness is explicit for LBA fields via `__le32`.

## Risks
Packed layout must not change. CHS fields are legacy and often unreliable; parsers should prefer LBA. Type aliases can be ambiguous, especially `0x82`.

## Test Signals
Partition scan tests with primary, extended, logical, Linux RAID/LVM, BSD, Solaris, and malformed MBR images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/msdos_partition.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/msg.h -->
# sources/distributed-fs/ceph-client/include/linux/msg.h

## Purpose
`msg.h` declares the internal SysV message queue message structure while importing the public UAPI message queue definitions.

## Important APIs, Types, and Functions
It includes `linux/list.h` and `uapi/linux/msg.h`, then defines `struct msg_msg` with list linkage, message type, text size, next segment pointer, security pointer, and inline payload storage immediately following the struct.

## Control Flow and State
SysV IPC code allocates messages, links them into queues via `m_list`, stores type/length/security metadata, chains extra `msg_msgseg` segments for larger payloads, and copies the payload after the header.

## State and Persistence Behavior
Messages are runtime IPC state stored in kernel memory until received or queue removal. Security metadata integrates with LSM state.

## Dependencies and Integration Points
It integrates with SysV IPC queues, memory accounting, LSM hooks, and UAPI message queue operations.

## Risks
Payload follows the struct directly, so allocation size and copy bounds are critical. Segment chains must be freed fully. Type and size validation protects usercopy paths.

## Test Signals
SysV msgget/msgsnd/msgrcv tests, large segmented messages, LSM labeling, queue removal cleanup, and usercopy bounds checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/msi.h -->
# sources/distributed-fs/ceph-client/include/linux/msi.h

## Purpose
`msi.h` defines low-level Message Signaled Interrupt data structures and APIs for interrupt core, PCI/MSI core, MSI domains, IOMMU/VFIO/NTB-style low-level consumers, and architecture integration. Driver-facing lookup APIs are intentionally separated into `msi_api.h`.

## Important APIs, Types, and Functions
Core message and descriptor types include `struct msi_msg`, `struct pci_msi_desc`, `union msi_domain_cookie`, `struct msi_desc_data`, `struct msi_desc`, `enum msi_desc_filter`, and `struct msi_dev_domain`. Descriptor APIs include `msi_setup_device_data()`, descriptor locking helpers and guard, `msi_domain_first_desc()`, `msi_first_desc()`, `msi_next_desc()`, iteration macros, `msi_desc_set_iommu_msi_iova()`, `msi_msg_set_addr()`, `msi_domain_insert_msi_desc()`, `msi_insert_msi_desc()`, and descriptor free-range helpers.

Generic MSI domain support defines `struct msi_domain_ops`, `struct msi_domain_info`, `struct msi_domain_template`, MSI domain flags, chip flags, `struct msi_parent_ops`, parent/domain creation APIs, device-domain creation/removal/matching, IRQ allocation/free range APIs, `msi_domain_alloc_irq_at()`, `msi_get_domain_info()`, platform MSI helpers, and `msi_device_has_isolated_msi()`. PCI-specific helpers include MSI message read/write/mask/unmask and domain helpers under `CONFIG_PCI_MSI`.

## Control Flow and State
Device MSI setup creates per-device descriptor storage and optional per-device IRQ domains. Allocation inserts descriptors, maps hardware or software indices to Linux IRQs, initializes domain/chip callbacks, and writes MSI messages. Free paths tear down IRQs and descriptors by domain/range. Descriptor iteration requires the MSI descriptor mutex. IOMMU MSI address override flows through `msi_desc_set_iommu_msi_iova()` and `msi_msg_set_addr()`.

## State and Persistence Behavior
MSI state is runtime per-device interrupt state. Descriptors cache the last programmed MSI message, affinity, IRQ number, domain-specific cookies, PCI attributes, optional sysfs attributes, and IOMMU address override. It persists while MSI interrupts are allocated.

## Dependencies and Integration Points
It depends on irq domains, IRQ chips, CPU masks, device model, PCI, sysfs, architecture MSI types, IOMMU MSI support, Xen fallback paths, and platform MSI. It is central to PCI/MSI-X, IMS, per-device domains, VFIO, and interrupt remapping.

## Risks
Regular drivers should not store `msi_desc` pointers; lifetime and locking are controlled by MSI core. Missing descriptor locks can race allocation/free. Domain flags must match parent capabilities. MSI address programming with IOMMU shifts is easy to corrupt. Config stubs must preserve behavior when generic or PCI MSI is disabled.

## Test Signals
PCI MSI and MSI-X allocation/free, dynamic MSI-X, affinity changes, suspend/resume restore, IOMMU interrupt remapping, sysfs MSI entries, Xen/fallback configurations, descriptor lockdep, and builds with generic MSI disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/msi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/msi_api.h -->
# sources/distributed-fs/ceph-client/include/linux/msi_api.h

## Purpose
`msi_api.h` exposes the small driver-relevant MSI API for mapping MSI indices to Linux virtual IRQ numbers and carrying implementation-specific instance cookies.

## Important APIs, Types, and Functions
It defines `enum msi_domain_ids` with `MSI_DEFAULT_DOMAIN` and `MSI_MAX_DEVICE_IRQDOMAINS`, `union msi_instance_cookie`, `struct msi_map`, `MSI_ANY_INDEX`, `msi_domain_get_virq()`, and inline `msi_get_virq()`.

## Control Flow and State
Drivers or subsystem code query a device/domain/index mapping through `msi_domain_get_virq()` or the default-domain wrapper. Allocation APIs elsewhere may return `struct msi_map`, where negative `index` carries an error.

## State and Persistence Behavior
No state is stored here. It references MSI mappings maintained by the MSI core.

## Dependencies and Integration Points
It is included by `msi.h` and driver code that only needs safe lookup-level access.

## Risks
Callers must distinguish missing mapping (`0` virq) from valid IRQs and negative allocation errors in `msi_map.index`. Domain IDs are intentionally bounded.

## Test Signals
Driver MSI lookup tests, default and non-default domain mappings, dynamic index allocation with `MSI_ANY_INDEX`, and disabled/no-mapping behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/msi_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/bbm.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/bbm.h

## Purpose
`mtd/bbm.h` defines NAND/OneNAND bad-block table descriptors, flags, generic BBM state, and the OneNAND default bad-block-table entry point.

## Important APIs, Types, and Functions
It defines `NAND_MAX_CHIPS`, `struct nand_bbt_descr`, many `NAND_BBT_*` option flags, `NAND_BBT_SCAN_MAXBLOCKS`, OneNAND read error flags, `struct bbm_info`, and `onenand_default_bbt()`.

## Control Flow and State
NAND code uses descriptors to locate, create, version, scan, and write bad-block tables. `bbm_info` holds the in-memory BBT bitmap, option flags, erase-shift geometry, bad-block checker callback, optional scan pattern, and private data. Flash-based BBTs may reserve blocks and store markers in OOB or in-band.

## State and Persistence Behavior
The BBT can be both runtime state (`bbt` pointer) and persistent flash metadata. Version bytes, descriptor pages, and reserved block codes affect on-flash state.

## Dependencies and Integration Points
It integrates with MTD NAND/OneNAND drivers, OOB layouts, ECC policy, chip arrays, and `struct mtd_info`.

## Risks
BBT option combinations are delicate: `NO_OOB_BBM` must be paired with flash-based BBT, dynamic descriptors must be freed, and incorrect version/page fields can overwrite data or lose factory bad-block marks. ECC layouts that cover spare area need special handling.

## Test Signals
NAND bad-block scan/create/write tests, multi-chip BBT, OOB and no-OOB modes, version rollover, reserved block handling, OneNAND BBT creation, and power-failure recovery scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/bbm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/blktrans.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/blktrans.h

## Purpose
`mtd/blktrans.h` declares the MTD block translation layer, which exposes MTD devices through block-device style disks backed by translation drivers.

## Important APIs, Types, and Functions
It defines `struct mtd_blktrans_dev`, `struct mtd_blktrans_ops`, `register_mtd_blktrans()`, `deregister_mtd_blktrans()`, `add_mtd_blktrans_dev()`, `del_mtd_blktrans_dev()`, `mtd_blktrans_cease_background()`, and `module_mtd_blktrans()`.

## Control Flow and State
Translation drivers register operations. When matching MTD devices appear, `add_mtd()` creates `mtd_blktrans_dev` instances with request queues, disks, tag sets, locks, references, and optional background workers. Block requests are translated to `readsect`, `writesect`, `discard`, `flush`, and geometry callbacks. Removal calls `remove_dev()` and tears down disks/queues.

## State and Persistence Behavior
State is runtime block/MTD translation state. Data persistence is provided by underlying MTD storage. `open`, `readonly`, `writable`, `bg_stop`, kref, and queue fields track live block-device behavior.

## Dependencies and Integration Points
It depends on mutexes, krefs, sysfs, block layer types, request queues, `gendisk`, MTD core, and module ownership. Users include translation drivers such as block2mtd/ftl-style components.

## Risks
Open/release and add/remove callbacks run under `mtd_table_mutex`. Queue locking, background worker stop, and kref lifetime are critical during hot removal. Sector size/shift mismatches can corrupt I/O. Writable/readonly flags must match hardware state.

## Test Signals
Register/deregister translation drivers, hot-add/remove MTD devices, block read/write/discard/flush tests, background worker shutdown, open-during-remove races, and module unload with active disks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/blktrans.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/cfi.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/cfi.h

## Purpose
`mtd/cfi.h` defines Common Flash Interface data structures and helpers for probing and controlling NOR flash chips through MTD map drivers and CFI command sets.

## Important APIs, Types, and Functions
It defines interleave helpers (`cfi_interleave*`, `cfi_interleave_supported()`), CFI device/interface constants, query structs (`cfi_ident`, `cfi_extquery`, Intel/AMD/Atmel PRI structs, OTP/block/region programming info), command-set IDs (`P_ID_*`), mode constants, and `struct cfi_private`. Functional APIs include `cfi_build_cmd_addr()`, `cfi_build_cmd()`, `cfi_merge_status()`, `cfi_send_gen_cmd()`, `cfi_read_query()`, `cfi_read_query16()`, `cfi_udelay()`, query-mode helpers, `cfi_read_pri()`, `struct cfi_fixup`, manufacturer IDs, `cfi_fixup()`, `varsize_frob_t`, and `cfi_varsize_frob()`.

## Control Flow and State
Probe code enters CFI query mode, reads query bytes/words through `map_read()`, converts endianness with map swap settings, identifies command sets and geometry, applies fixups, and initializes `struct cfi_private` with chip count, command set setup, manufacturer/device IDs, erase command, chip shift, quirks, and per-chip `flchip` state. Runtime operations build interleaved commands and send generic command sequences to one or more chips.

## State and Persistence Behavior
Runtime CFI state lives in `struct cfi_private` and per-chip `flchip` records. Persistent data is the NOR flash contents and hardware CFI query data. Fixups alter runtime interpretation, not flash contents by themselves.

## Dependencies and Integration Points
It depends on delay/interrupt helpers, MTD flashchip/map APIs, CFI endianness helpers, XIP annotations, and MTD command-set drivers for Intel/AMD/Jedec-style chips.

## Risks
Interleave and bank-width errors send commands to wrong lanes. Endianness conversion is hardware-dependent. Flexible query structs contain non-host-ordered fields and variable tails. Missing `CONFIG_MTD_CFI_Ix` support triggers a BUG path. Fixups can mask hardware quirks but also misconfigure erase/program behavior.

## Test Signals
Probe NOR devices with x8/x16/x32 interleaves, big/little/host endian maps, Intel and AMD command sets, XIP query-mode paths, erase/write/read tests, CFI fixup coverage, and unsupported interleave builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/cfi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/cfi_endian.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/cfi_endian.h

## Purpose
`mtd/cfi_endian.h` defines byte-order conversion helpers for CFI flash access based on map swap policy.

## Important APIs, Types, and Functions
It defines `CFI_HOST_ENDIAN`, `CFI_LITTLE_ENDIAN`, `CFI_BIG_ENDIAN`, `CFI_DEFAULT_ENDIAN`, `cfi_default()`, `cfi_be()`, `cfi_le()`, `cfi_host()`, `cpu_to_cfi8/16/32/64()`, `cfi8/16/32/64_to_cpu()`, and internal `_cpu_to_cfi()`, `_cfi_to_cpu()`, `_swap_to_cfi()`, `_swap_to_cpu()` macros.

## Control Flow and State
CFI map code sets or leaves `map->swap`; conversion macros either pass values through for host endian or call CPU endian conversion macros for big/little CFI byte order.

## State and Persistence Behavior
No state is owned. It interprets `map_info::swap` and Kconfig defaults.

## Dependencies and Integration Points
It depends on architecture byteorder helpers and CFI map drivers. It is included by `cfi.h`.

## Risks
Wrong default endian selection or map swap value corrupts command/query interpretation. The file intentionally has no include guard, so repeated inclusion must be harmless.

## Test Signals
CFI probe on big-endian/little-endian systems, map swap option tests, read/write query values, and config coverage for NOSWAP/LE/BE advanced options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/cfi_endian.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/concat.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/concat.h

## Purpose
`mtd/concat.h` declares the MTD concatenation layer, which presents multiple MTD devices as one larger virtual MTD device and supports device-tree driven virtual concatenation.

## Important APIs, Types, and Functions
It defines `struct mtd_concat`, `mtd_concat_create()`, `mtd_concat_destroy()`, `mtd_virt_concat_node_create()`, `mtd_virt_concat_add()`, `mtd_virt_concat_create_join()`, `mtd_virt_concat_destroy()`, `mtd_virt_concat_destroy_joins()`, and `mtd_virt_concat_destroy_items()`.

## Control Flow and State
Manual concatenation passes an array of subdevice pointers to `mtd_concat_create()` and later destroys the wrapper. Virtual concatenation discovers intended components, adds matching `mtd_info` objects as they appear, creates/registers the joined device once complete, and destroys joins/items during removal or cleanup.

## State and Persistence Behavior
`struct mtd_concat` owns runtime wrapper state and a flexible array of subdevice pointers. Underlying MTD contents persist independently; concatenation only changes the logical view.

## Dependencies and Integration Points
It integrates with MTD core, `struct mtd_info`, device-tree based MTD discovery, and MTD registration/removal paths.

## Risks
Subdevice ordering and size boundaries must be correct or offsets map to wrong chips. Removal of a subdevice must tear down the concat and re-register individual devices as documented. Lifetime of subdevice pointers is critical.

## Test Signals
Create/destroy concatenated MTDs, read/write across subdevice boundaries, device-tree virtual concat discovery, subdevice removal, partial component arrival, and cleanup of joins/items.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/concat.h -->
