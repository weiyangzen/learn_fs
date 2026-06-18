# Research group subset-b-005853

This grouped report covers Linux kernel interface headers under `sources/distributed-fs/ceph-client/include/linux`. Each section is delimited for the reconciliation splitter and preserves the original source path in its title.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/ti-cppi5.h -->
# sources/distributed-fs/ceph-client/include/linux/dma/ti-cppi5.h

## Purpose
This header defines the descriptor layout and inline manipulation helpers for Texas Instruments CPPI5/UDMA descriptors. It covers common descriptor headers, host packet descriptors, monolithic descriptors, transfer request descriptors, transfer request records, and transfer response records. It is a hardware ABI header: the packed/aligned structures and bitfield masks must match what TI DMA hardware consumes and produces.

## Important APIs, types, and functions
Key data structures are `struct cppi5_desc_hdr_t`, `struct cppi5_host_desc_t`, `struct cppi5_desc_epib_t`, `struct cppi5_monolithic_desc_t`, the TR record layouts `cppi5_tr_type0_t`, `cppi5_tr_type1_t`, `cppi5_tr_type2_t`, `cppi5_tr_type3_t`, `cppi5_tr_type15_t`, and `struct cppi5_tr_resp_t`. The constants define descriptor type fields, packet length fields, return queue policy, tag IDs, PS data sizes, TR record sizes, trigger modes, and response statuses.

The helper API is entirely inline. Common descriptor helpers include `cppi5_desc_get_type()`, `cppi5_desc_get_errflags()`, `cppi5_desc_get_pktids()`, `cppi5_desc_set_pktids()`, `cppi5_desc_set_retpolicy()`, `cppi5_desc_get_tags_ids()`, `cppi5_desc_set_tags_ids()`, `cppi5_desc_is_tdcm()`, and `cppi5_desc_dump()`. Host descriptor helpers include `cppi5_hdesc_calc_size()`, `cppi5_hdesc_init()`, `cppi5_hdesc_update_flags()`, `cppi5_hdesc_update_psdata_size()`, packet length/PS flag/packet type getters and setters, buffer attach/reset helpers, host-buffer-descriptor link helpers, and accessors for in-descriptor PS data and software data. TR helpers include `cppi5_trdesc_calc_size()`, `cppi5_trdesc_init()`, `cppi5_tr_init()`, `cppi5_tr_set_trigger()`, and `cppi5_tr_csf_set()`.

## Control flow, state, and persistence
The header has no runtime ownership or allocation logic. State is encoded directly into descriptor words that are later submitted to hardware rings. The inline functions update selected bit ranges by masking and shifting, so the observable state is the descriptor memory image itself. Host descriptors carry current and original buffer addresses/lengths; `cppi5_hdesc_reset_to_original()` restores `buf_ptr` and `buf_info1` from the original buffer fields. Descriptor chains persist through `next_desc` until reset. TR descriptors encode reload index/count and record size in header words; the reload count can request infinite looping.

## Dependencies and integration points
It depends on `linux/bitops.h` for `BIT()`, `GENMASK()`, and `ALIGN()`, on `linux/printk.h` for descriptor dumps, and on DMA address types from the kernel environment. DMA controller drivers using TI K3 UDMA/CPPI5 include this header to construct ring descriptors, parse completion descriptors, attach protocol metadata, and generate transfer request packets. The packed and aligned annotations make it part of a device-facing ABI.

## Risks and test signals
The main risks are hardware ABI drift, incorrect PS data sizing, invalid alignment, bad return ring IDs, and unguarded caller input. For example, `cppi5_hdesc_init()` and `cppi5_hdesc_update_psdata_size()` do not enforce the maximum or 4-byte multiple, while `cppi5_hdesc_calc_size()` only rejects too-large PS data. `cppi5_trdesc_init()` assumes `tr_count > 0` and a valid `tr_size`; otherwise `tr_count - 1` and `ffs(tr_size >> 4) - 1` encode invalid fields. Tests should exercise descriptor field round trips, size calculations, EPIB and PS-data placement, host buffer reset/link behavior, TR record size encoding for 16/32/64/128 byte records, and known hardware completion response values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/ti-cppi5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/xilinx_dma.h -->
# sources/distributed-fs/ceph-client/include/linux/dma/xilinx_dma.h

## Purpose
This header exposes Xilinx VDMA channel configuration to DMAEngine clients and drivers. It is a narrow bridge between the generic DMAEngine API and Xilinx-specific video DMA features such as frame delay, frame parking, genlock, interrupt coalescing, external frame sync, and vertical flip.

## Important APIs, types, and functions
The central type is `struct xilinx_vdma_config`, with integer configuration fields for frame delay, genlock, master selection, frame count enable, park mode/frame, coalescing, delay counter, reset, external fsync, plus `bool vflip_en`. The exported function `xilinx_vdma_channel_set_config(struct dma_chan *dchan, struct xilinx_vdma_config *cfg)` applies the configuration to a DMAEngine channel.

## Control flow, state, and persistence
The header itself holds no state. The caller prepares a config object and passes it to the Xilinx DMA driver, which persists the values in channel registers or channel-private state. `reset` is an action-like field, so callers must treat the config as a command as well as a state description.

## Dependencies and integration points
It includes `linux/dma-mapping.h` and `linux/dmaengine.h`, and integrates with the generic `struct dma_chan` acquisition/submission path. Video pipelines, DRM, V4L2, and SoC display/capture drivers are likely clients.

## Risks and test signals
There is no compile-time range checking for frame numbers, coalescing, delay, or fsync source. Tests should validate that invalid channel pointers fail in the implementation, that reset does not leak resources, and that frame parking/genlock/vflip settings are reflected in hardware-visible behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/xilinx_dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/xilinx_dpdma.h -->
# sources/distributed-fs/ceph-client/include/linux/dma/xilinx_dpdma.h

## Purpose
This small header defines peripheral configuration for Xilinx DPDMA transfers. It gives DMAEngine clients a typed way to mark a transfer as part of a video group.

## Important APIs, types, and functions
The only type is `struct xilinx_dpdma_peripheral_config`, containing `bool video_group`. There are no functions or inline helpers.

## Control flow, state, and persistence
No control flow is present. State is carried by the config struct and consumed by the DPDMA driver through `dma_slave_config.peripheral_config` or a similar driver-specific path.

## Dependencies and integration points
It depends only on `linux/types.h`. Integration is with Xilinx display DMA clients and the generic DMAEngine peripheral-configuration field.

## Risks and test signals
The risk is contract ambiguity: callers and the driver must agree on the lifetime and exact interpretation of `video_group`. Tests should cover grouped and non-grouped video transfers and verify that the driver rejects or ignores the option consistently when unsupported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/xilinx_dpdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dmaengine.h -->
# sources/distributed-fs/ceph-client/include/linux/dmaengine.h

## Purpose
This is the core public DMAEngine interface for kernel DMA providers and clients. It defines transaction types, transfer directions, descriptor flags, capability masks, channel/device structures, descriptor metadata semantics, async transaction descriptors, client request helpers, device registration APIs, and status/termination helpers.

## Important APIs, types, and functions
Important enums include `dma_status`, `dma_transaction_type`, `dma_transfer_direction`, `dma_ctrl_flags`, `sum_check_flags`, `dma_desc_metadata_mode`, `dma_slave_buswidth`, `dma_residue_granularity`, `dmaengine_tx_result`, and `dmaengine_alignment`. Important structs include `dma_interleaved_template`, `data_chunk`, `dma_vec`, `dma_chan`, `dma_chan_dev`, `dma_slave_config`, `dma_slave_caps`, `dmaengine_result`, `dmaengine_unmap_data`, `dma_descriptor_metadata_ops`, `dma_async_tx_descriptor`, `dma_tx_state`, `dma_slave_map`, `dma_filter`, and `dma_device`.

Provider-facing APIs are centered on `struct dma_device`, which holds capability masks and a vtable for resource allocation, DMA prep operations, slave config, pause/resume/terminate/synchronize, status polling, issue-pending, release, and optional debugfs summary. Registration APIs include `dma_async_device_register()`, `dmaenginem_async_device_register()`, `dma_async_device_unregister()`, `dma_async_device_channel_register()`, and `dma_async_device_channel_unregister()`.

Client-facing helpers include `dma_request_chan()`, `devm_dma_request_chan()`, `dma_request_chan_by_mask()`, `dma_request_channel()`, `dma_release_channel()`, `dma_get_slave_caps()`, `dmaengine_slave_config()`, `dmaengine_prep_slave_single()`, `dmaengine_prep_slave_sg()`, `dmaengine_prep_peripheral_dma_vec()`, `dmaengine_prep_dma_cyclic()`, `dmaengine_prep_interleaved_dma()`, `dmaengine_prep_dma_memset()`, `dmaengine_prep_dma_memcpy()`, `dmaengine_submit()`, `dma_async_issue_pending()`, `dmaengine_tx_status()`, `dma_async_is_tx_complete()`, `dma_async_is_complete()`, `dma_sync_wait()`, and `dma_wait_for_async_tx()`.

## Control flow, state, and persistence
DMA transaction state is tracked by cookies. Positive `dma_cookie_t` values identify submitted requests and negative values are errors; `dma_submit_error()` normalizes this convention. Each channel stores its last issued and completed cookies, client counts, router data, private data, and sysfs/debug names. Providers create descriptors, clients submit them with `tx_submit`, and hardware work begins only when `device_issue_pending()` is called.

Metadata state is per descriptor. `DESC_METADATA_CLIENT` means the client owns the buffer and attaches it before submit; `DESC_METADATA_ENGINE` means the provider owns metadata and the client uses get/set helpers. The header explicitly warns that the modes are incompatible for a descriptor and that engine metadata is valid only until completion callback return. Termination has two paths: async termination may return before transfers and callbacks have stopped, while sync termination calls `dmaengine_synchronize()` to guarantee quiescence.

## Dependencies and integration points
The header integrates with the device model, scatterlists, bitmaps, async_tx, DMA mapping, OF/client lookup, sysfs class devices, debugfs, and optional RapidIO. Provider drivers populate `struct dma_device`; client drivers use request/config/prep/submit/issue/status/terminate helpers. Capability masks gate features such as cyclic, interleaved, repeat, PQ, XOR, memset, slave, and async memory operations.

## Risks and test signals
Several helper families are null-safe for prep operations, but other helpers assume valid objects and vtables. For example, status, submit, issue-pending, pause, resume, and termination wrappers dereference `chan` or `desc` directly. Descriptor reuse requires `dma_get_slave_caps()` and `descriptor_reuse`; `dmaengine_desc_free()` calls `desc_free()` only after the reuse flag is set. `dma_maxpq()` depends on max source count and continuation flags and can underflow conceptually if provider limits are too small. Tests should include cookie wraparound logic in `dma_async_is_complete()`, metadata mode exclusivity, disabled-`CONFIG_DMA_ENGINE` stubs, terminate-async/synchronize ordering, repeat interleaved capability rejection, alignment helpers, descriptor reuse permission, and provider registration/unbind behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dmaengine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dmapool.h -->
# sources/distributed-fs/ceph-client/include/linux/dmapool.h

## Purpose
This header declares DMA-coherent memory pool APIs for allocating many fixed-size DMA-able objects such as descriptors. It provides both explicit lifetime and device-managed variants.

## Important APIs, types, and functions
The main API is `dma_pool_create_node()`, `dma_pool_create()`, `dma_pool_destroy()`, `dma_pool_alloc()`, `dma_pool_zalloc()`, and `dma_pool_free()`. Managed variants are `dmam_pool_create()` and `dmam_pool_destroy()`. `struct dma_pool` is opaque.

## Control flow, state, and persistence
Pool state is owned by the implementation. Creation binds a pool to a device, object size, alignment, boundary, and NUMA node. Allocation returns a CPU virtual address plus DMA address handle; free requires both the virtual address and DMA address. Managed pools persist until explicit managed destroy or device resource release.

## Dependencies and integration points
It depends on NUMA node definitions, scatterlist declarations, and I/O mapping headers. It is consumed by DMA controller, USB, network, and storage drivers that need coherent descriptor memory.

## Risks and test signals
When `CONFIG_HAS_DMA` is disabled all creation/allocation helpers become no-op stubs returning `NULL`, so callers must handle failure. Tests should verify alignment and boundary guarantees, zeroing through `dma_pool_zalloc()`, freeing with matching handles, and device-managed cleanup on driver detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dmapool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dmar.h -->
# sources/distributed-fs/ceph-client/include/linux/dmar.h

## Purpose
This header declares Intel DMAR/VT-d table, device-scope, interrupt-remapping, and MSI fault-handling interfaces. It models ACPI DMAR hardware units, their PCI scopes, hotplug notifications, and interrupt remapping table entries.

## Important APIs, types, and functions
Important types are `struct dmar_dev_scope`, `struct dmar_drhd_unit`, `struct dmar_pci_path`, `struct dmar_pci_notify_info`, and `struct irte`. Global state includes `dmar_tbl`, `dmar_global_lock`, and `dmar_drhd_units` when DMAR table support is enabled. Iteration helpers include `for_each_drhd_unit`, `for_each_active_drhd_unit`, `for_each_iommu`, `for_each_active_iommu`, `for_each_dev_scope`, and `for_each_active_dev_scope`.

The API declares table and scope lifecycle functions (`dmar_table_init()`, `dmar_dev_scope_init()`, `dmar_alloc_dev_scope()`, `dmar_free_dev_scope()`, `dmar_insert_dev_scope()`, `dmar_remove_dev_scope()`), device notification hooks (`dmar_device_add()`, `dmar_device_remove()`, `dmar_register_bus_notifier()`), IOMMU detection/init hooks, DMAR parser callbacks for RMRR/ATSR/SATC, hotplug hooks, IRQ remapping hotplug, platform opt-in checks, and DMAR MSI/fault functions such as `dmar_set_interrupt()`, `dmar_fault()`, `dmar_alloc_hwirq()`, and `dmar_free_hwirq()`.

## Control flow, state, and persistence
DMAR state is persistent global kernel state sourced from ACPI tables and maintained in RCU-protected lists. `dmar_rcu_check()` allows safe list dereference when the global rwsem is held or during boot. Device scopes carry RCU pointers to devices plus bus/devfn identifiers. `struct irte` is a packed hardware-format entry with shared, remapped, and posted interrupt views; `dmar_copy_shared_irte()` copies only fields common to both modes.

## Dependencies and integration points
It integrates with ACPI DMAR parsing, Intel IOMMU, PCI hotplug, IRQ remapping, MSI message programming, RCU lists, rwsems, and boot-time system state. If `CONFIG_DMAR_TABLE`, `CONFIG_INTEL_IOMMU`, or `CONFIG_IRQ_REMAP` are disabled, many APIs compile to no-op or `-ENODEV` stubs.

## Risks and test signals
Risks include unsafe iteration without the DMAR lock/RCU guarantees, incorrect interrupt remapping bit layout, stale RCU device scopes on hotplug, and configuration stubs masking missing functionality. Tests should cover ACPI table parse failures, device scope add/remove, hotplug insertion/removal, platform opt-in flags, interrupt remapping in remapped and posted modes, and disabled-config stub behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dmar.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dmi.h -->
# sources/distributed-fs/ceph-client/include/linux/dmi.h

## Purpose
This header exposes Desktop Management Interface and SMBIOS table discovery helpers. It lets drivers match systems, read firmware strings, enumerate DMI devices, walk raw DMI entries, and query memory-device metadata.

## Important APIs, types, and functions
Important types are `enum dmi_device_type`, `enum dmi_entry_type`, `struct dmi_header`, `struct dmi_device`, `struct dmi_a_info_entry`, `struct dmi_a_info`, and `struct dmi_dev_onboard` under `CONFIG_DMI`. APIs include `dmi_check_system()`, `dmi_first_match()`, `dmi_get_system_info()`, `dmi_find_device()`, `dmi_setup()`, `dmi_get_date()`, `dmi_get_bios_year()`, `dmi_name_in_vendors()`, `dmi_name_in_serial()`, `dmi_walk()`, `dmi_match()`, `dmi_memdev_name()`, `dmi_memdev_size()`, `dmi_memdev_type()`, `dmi_memdev_handle()`, and `dmi_string_nosave()`.

## Control flow, state, and persistence
The persistent state is populated from firmware tables during setup and exposed through `dmi_kobj`, global availability state, and internal DMI device lists. `dmi_walk()` provides callback-driven table traversal. `dmi_string_nosave()` returns transient strings from a DMI record rather than saved copies.

## Dependencies and integration points
It depends on list handling, kobjects, and `mod_devicetable.h` for system ID fields. It is integrated with platform quirks, firmware drivers, memory inventory, and onboard-device discovery. Without `CONFIG_DMI`, most helpers become conservative stubs.

## Risks and test signals
Risks are malformed firmware tables, missing DMI support, lifetime confusion around non-saved strings, and quirk matching that is too broad. Tests should include positive and negative `dmi_system_id` matches, date parsing, raw table walking, memory-device queries, and disabled-config fallback values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dnotify.h -->
# sources/distributed-fs/ceph-client/include/linux/dnotify.h

## Purpose
This header declares legacy directory notification support. It associates directory notification masks with file descriptors and file owners, and exposes the fcntl setup and flush hooks.

## Important APIs, types, and functions
`struct dnotify_struct` stores a linked-list node, event mask, file descriptor, `struct file *`, and owner. `DNOTIFY_ALL_EVENTS` combines delete, modify, access, attrib, create, rename, and move events. Kernel APIs are `dnotify_flush()` and `fcntl_dirnotify()` when `CONFIG_DNOTIFY` is enabled.

## Control flow, state, and persistence
State persists as per-file dnotify records. `fcntl_dirnotify()` installs or updates notification state for a file descriptor; `dnotify_flush()` removes records for an owner when a file is closed or ownership ends.

## Dependencies and integration points
It depends on `linux/fs.h` for file, owner, and event flags. It integrates with fcntl, VFS file lifetime, and fsnotify-style events. When disabled, `fcntl_dirnotify()` returns `-EINVAL` and flush is a no-op.

## Risks and test signals
Risks include stale owner/file references, event mask mismatch with fsnotify flags, and compatibility behavior for applications still using dnotify. Tests should cover install, event delivery, close/flush cleanup, unsupported-config behavior, and interaction with rename/move child events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dnotify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dns_resolver.h -->
# sources/distributed-fs/ceph-client/include/linux/dns_resolver.h

## Purpose
This header declares the in-kernel DNS resolver upcall API used by network filesystems such as CIFS DFS and AFS. It abstracts hostname and record resolution through key/request-key style infrastructure.

## Important APIs, types, and functions
The only exported function is `dns_query(struct net *net, const char *type, const char *name, size_t namelen, const char *options, char **_result, time64_t *_expiry, bool invalidate)`. It takes a network namespace, record type, name and length, option string, output result buffer, output expiry time, and invalidation flag.

## Control flow, state, and persistence
The header itself has no state. The implementation resolves or invalidates cached resolver entries and returns dynamically managed result data plus an expiry timestamp. The `invalidate` argument makes the call a cache-control operation as well as a query.

## Dependencies and integration points
It includes the UAPI resolver definitions and forward-declares `struct net`. It integrates with network namespaces, request-key/upcall resolver mechanisms, and filesystem referral code.

## Risks and test signals
Risks include result ownership/lifetime mistakes, namespace leakage, stale cache entries, malformed names/options, and timeout/expiry handling. Tests should cover successful lookup, missing records, invalidation, per-netns isolation, and callers freeing result buffers correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dns_resolver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dpll.h -->
# sources/distributed-fs/ceph-client/include/linux/dpll.h

## Purpose
This header declares the kernel API for Digital Phase Locked Loop devices and pins. It lets hardware drivers register DPLL devices, register pins, expose mode/lock/frequency/phase operations over generic netlink, and attach DPLL pin handles to network devices.

## Important APIs, types, and functions
Provider operation tables are `struct dpll_device_ops` and `struct dpll_pin_ops`. Device ops cover mode get/set, supported modes, lock status, temperature, clock quality level, phase offset monitor, phase offset averaging, and frequency monitor state. Pin ops cover frequency, direction, state on parent pin or DPLL, priority, phase offset/adjustment, fractional frequency offset, measured frequency, embedded sync, and reference sync state.

Data types include `struct dpll_pin_frequency`, `struct dpll_pin_phase_adjust_range`, `struct dpll_pin_esync`, `struct dpll_pin_properties`, notifier info structs, and the optional `dpll_tracker` ref-tracking type. APIs include `dpll_device_get/put/register/unregister`, `dpll_pin_get/put/register/unregister`, `dpll_pin_on_pin_register/unregister`, `dpll_pin_fwnode_set()`, `dpll_pin_ref_sync_pair_add()`, device and pin change notification helpers, netdev pin-handle helpers, and DPLL notifier registration.

## Control flow, state, and persistence
DPLL and pin objects are reference-counted objects obtained by clock ID and driver ID, then registered with ops and private data. Pin properties persist labels, type, capabilities, supported frequencies, phase range, and granularity. Notifier events report created/deleted/changed state for devices and pins. Optional ref tracking records acquisition sites when configured.

## Dependencies and integration points
It depends on DPLL UAPI enums, device model, generic netlink, network devices, notifier chains, and rtnetlink. Drivers expose hardware clock synchronization control, while netdev integrations allow user space to correlate network ports with DPLL pins. When `CONFIG_DPLL` is disabled, netdev handle helpers are harmless stubs, but core declarations remain visible.

## Risks and test signals
Risks include mismatched get/put lifetimes, registering pins without stable properties, exposing unsupported ops, netlink extack omissions, and missing notifications after hardware state changes. Tests should cover registration/unregistration ordering, pin-on-pin topology, ref-sync pairs, extack errors for invalid mode/frequency/phase requests, netdev pin handle encoding, and notifier delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dpll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dqblk_qtree.h -->
# sources/distributed-fs/ceph-client/include/linux/dqblk_qtree.h

## Purpose
This header defines the shared in-memory interface for quota formats that store quota entries in a tree/trie. It abstracts format-specific disk entry conversion from generic qtree traversal and update logic.

## Important APIs, types, and functions
Constants `QTREE_INIT_ALLOC`, `QTREE_INIT_REWRITE`, `QTREE_DEL_ALLOC`, and `QTREE_DEL_REWRITE` describe block update costs. `struct qtree_fmt_operations` supplies `mem2disk_dqblk`, `disk2mem_dqblk`, and `is_id`. `struct qtree_mem_dqinfo` stores superblock, quota type, block counts, free block/entry heads, block size, entry size, usable block size, qtree depth, and operation table. APIs include `qtree_write_dquot()`, `qtree_read_dquot()`, `qtree_delete_dquot()`, `qtree_release_dquot()`, `qtree_entry_unused()`, `qtree_depth()`, and `qtree_get_next_id()`.

## Control flow, state, and persistence
Persistent state lives in the quota file tree and free lists. `qtree_mem_dqinfo` mirrors version-specific quota file metadata in memory. `qtree_depth()` computes how many levels are needed to address 32-bit quota IDs based on entries per block.

## Dependencies and integration points
It depends on quota `struct dquot`, `struct kqid`, and `struct super_block` from surrounding quota/VFS code. Format-specific headers such as v2 quota reuse the qtree block-cost constants.

## Risks and test signals
Risks include incorrect block-size math, stale free-list heads, conversion callbacks that do not preserve IDs, and tree-depth overflow if usable block size is invalid. Tests should cover create/read/update/delete/release paths, free entry reuse, ID iteration, and format-specific conversion round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dqblk_qtree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dqblk_v1.h -->
# sources/distributed-fs/ceph-client/include/linux/dqblk_v1.h

## Purpose
This header records block allocation and rewrite cost constants for the old quota file format.

## Important APIs, types, and functions
It defines `V1_INIT_ALLOC`, `V1_INIT_REWRITE`, `V1_DEL_ALLOC`, and `V1_DEL_REWRITE`. There are no types or functions.

## Control flow, state, and persistence
No runtime logic is present. The constants inform quota code how many blocks may be allocated or rewritten for init and delete operations in v1 quota format.

## Dependencies and integration points
It has no include dependencies beyond its guard. It is integrated by quota format implementations that need to estimate journal credits or block reservations.

## Risks and test signals
The risk is underestimating update costs, which can cause journal reservation failures. Tests should exercise v1 quota creation and deletion under journaling and quota-file full conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dqblk_v1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dqblk_v2.h -->
# sources/distributed-fs/ceph-client/include/linux/dqblk_v2.h

## Purpose
This header maps v2 quota format update-cost constants to the generic qtree quota constants.

## Important APIs, types, and functions
It includes `linux/dqblk_qtree.h` and defines `V2_INIT_ALLOC`, `V2_INIT_REWRITE`, `V2_DEL_ALLOC`, and `V2_DEL_REWRITE` as aliases of `QTREE_*` values.

## Control flow, state, and persistence
No runtime logic is present. It documents that v2 quota files use the qtree update model.

## Dependencies and integration points
Its only dependency is the qtree quota header. Quota code uses these constants for block and journal credit planning.

## Risks and test signals
Risks follow qtree behavior: if qtree costs change, v2 reservations change with them. Tests should verify v2 quota write/delete paths under journaling and compare block reservations against actual qtree mutations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dqblk_v2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/drbd.h -->
# sources/distributed-fs/ceph-client/include/linux/drbd.h

## Purpose
This header defines core DRBD public ABI constants and state encodings shared by the kernel module and user space. It covers policy enums, return codes, role/connection/disk state, state transition return values, metadata flags, UUID indices, notification types, peer state, write ordering, magic numbers, and metadata index constants.

## Important APIs, types, and functions
Important enums include `drbd_io_error_p`, `drbd_fencing_p`, `drbd_disconnect_p`, `drbd_after_sb_p`, `drbd_on_no_data`, `drbd_on_congestion`, `drbd_read_balancing`, `drbd_ret_code`, `drbd_role`, `drbd_conns`, `drbd_disk_state`, `drbd_state_rv`, `drbd_uuid_index`, `drbd_timeout_flag`, `drbd_notification_type`, `drbd_peer_state`, and `write_ordering_e`. `union drbd_state` packs role, peer role, connection state, local and peer disk state, and suspension flags into a 32-bit integer.

## Control flow, state, and persistence
The header has no executable control flow, but it defines persistent protocol and metadata values. `union drbd_state` is transmitted as a big-endian 32-bit value, while its bitfield layout is conditional on host bitfield endianness. Metadata flags such as `MDF_CONSISTENT`, `MDF_PRIMARY_IND`, `MDF_FULL_SYNC`, and `MDF_AL_CLEAN` persist on disk. UUID index constants define on-disk and netlink UUID vector positions.

## Dependencies and integration points
It is usable from both kernel and user space, selecting kernel types or libc/endian headers accordingly. It is included by DRBD generic-netlink definitions and admin tools. Magic values are used in metadata and network packets.

## Risks and test signals
The file warns not to reorder certain enums. ABI risks include inserting return codes in the wrong place, changing bitfield layout, or mismatching protocol version expectations. Tests should cover state serialization on little and big endian, user/kernel enum agreement, metadata magic recognition, and admin-tool decoding of every return code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/drbd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/drbd_config.h -->
# sources/distributed-fs/ceph-client/include/linux/drbd_config.h

## Purpose
This header declares DRBD compile-time version information and the build tag accessor.

## Important APIs, types, and functions
It declares `const char *drbd_buildtag(void)` and defines `REL_VERSION` as `8.4.11`, `PRO_VERSION_MIN` as `86`, and `PRO_VERSION_MAX` as `101`.

## Control flow, state, and persistence
The header has no runtime state. Version constants shape protocol negotiation and user-visible module identification.

## Dependencies and integration points
It is consumed by DRBD kernel code and tools that need release/protocol compatibility boundaries.

## Risks and test signals
Risks are stale protocol version bounds or release strings that do not match the implementation. Tests should verify version reporting, protocol negotiation against min/max, and build tag availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/drbd_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/drbd_genl.h -->
# sources/distributed-fs/ceph-client/include/linux/drbd_genl.h

## Purpose
This header is macro input for DRBD's generic-netlink schema generator. It defines nested top-level attributes, configuration structures, notifications, and admin operations for DRBD control and status reporting.

## Important APIs, types, and functions
The file uses generator macros such as `GENL_struct`, `GENL_mc_group`, `GENL_notification`, `GENL_op`, `GENL_tla_expected`, `GENL_op_init`, and `GENL_doit`. Structures include config reply/context, disk config, resource options, net config, role/resize/new-current-UUID/timeout/disconnect/detach parameters, state info, resource/device/connection/peer-device info, statistics blocks, notification header, and helper info.

Admin operations include status query, new/delete minor, new/delete resource, resource opts, connect, change net opts, disconnect, attach, change disk opts, resize, primary/secondary role changes, new current UUID, online verify, detach, invalidate, pause/resume sync, suspend/resume I/O, outdate, timeout query, down, dump resources/devices/connections/peer devices, initial-state dump, and helper notifications. The `events` multicast group carries state and helper notifications.

## Control flow, state, and persistence
Control flow is declarative: generator includes turn these macro records into enums, policies, conversion functions, operation tables, and multicast helpers. State carried over netlink includes persistent DRBD configuration, runtime connection/disk/role state, counters, UUIDs, bitmaps, pending request counts, and helper execution status. Required, invariant, optional, and sensitive flags affect validation and output handling.

## Dependencies and integration points
It depends on `drbd.h`, `drbd_limits.h` defaults, and the `genl_magic_*` generator headers included by `drbd_genl_api.h`. It is tightly coupled to kernel handlers named in `GENL_doit()` and dump callbacks. User-space DRBD admin tools must match the generated command numbers and attribute schema.

## Risks and test signals
Risks include duplicate field names across generated structs, changing command numbers, failing to mark required/invariant fields, exposing sensitive fields such as `shared_secret`, and schema drift between kernel and user tools. Tests should validate generated nla policies, required-attribute rejection, dumpit pagination/done callbacks, event multicast payloads, handler command numbers, and backward compatibility for optional fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/drbd_genl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/drbd_genl_api.h -->
# sources/distributed-fs/ceph-client/include/linux/drbd_genl_api.h

## Purpose
This header defines the DRBD-specific generic-netlink family header and wires the DRBD schema into the generic netlink macro generator.

## Important APIs, types, and functions
`struct drbd_genlmsghdr` carries `minor` plus a union of request `flags` and reply `ret_code`. `DRBD_GENL_F_SET_DEFAULTS` is the current request flag. `enum drbd_state_info_bcast_reason` defines status reply, state change, helper pre/post, and sync-progress reasons. Generator configuration macros define the family version, family name, header size, and include file before including `linux/genl_magic_struct.h`.

## Control flow, state, and persistence
The header has no runtime logic, but it defines the fixed family header prepended to DRBD generic-netlink messages. The `minor` field selects a device unless the request is resource/connection scoped, in which case the context attribute is used.

## Dependencies and integration points
It includes `linux/drbd.h`, undefines the preprocessor symbol `linux` to avoid include path conflicts, then includes generator support. It is consumed by generated netlink struct and function code.

## Risks and test signals
Changing the header layout or family header size is ABI-sensitive. Tests should encode/decode messages for minor-scoped and resource-scoped commands, verify reply return code handling, and confirm generator output includes the expected DRBD schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/drbd_genl_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/drbd_limits.h -->
# sources/distributed-fs/ceph-client/include/linux/drbd_limits.h

## Purpose
This header centralizes DRBD configuration limits, defaults, and scale units for minors, ports, startup timeouts, network parameters, synchronization, disk sizing, congestion, activity log layout, and feature defaults.

## Important APIs, types, and functions
It defines `*_MIN`, `*_MAX`, `*_DEF`, and `*_SCALE` constants for options such as minor count, port, wait-for-connection timeouts, network timeout, disk timeout, connect interval, ping interval/timeouts, max epoch size, send/receive buffer sizes, max buffers, unplug watermark, KO count, resync rate, activity log extents, minor number, disk size, bio vectors, resync planning rates, congestion fill/extents, AL stripes, socket-check timeout, and resync discard granularity. It also maps defaults to enums from `drbd.h`, such as `DRBD_ON_IO_ERROR_DEF`, `DRBD_FENCING_DEF`, and `DRBD_PROTOCOL_DEF`.

## Control flow, state, and persistence
No control flow is present. These constants define validation and default state for generated netlink policies and DRBD configuration. Some values directly affect persistent on-disk layout, especially activity log extents, stripe count, stripe size, and disk-size constraints.

## Dependencies and integration points
The constants are consumed by `drbd_genl.h`, DRBD configuration parsers, and user-space tools. They depend on policy enums from `drbd.h`.

## Risks and test signals
Risks include accepting nonsensical ranges, changing defaults that alter established behavior, and overflow in unit-scaled values. Tests should validate boundary values, generated policy min/max/default propagation, user-space error messages, and compatibility for historical defaults like discard-zeroes-if-aligned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/drbd_limits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ds2782_battery.h -->
# sources/distributed-fs/ceph-client/include/linux/ds2782_battery.h

## Purpose
This header declares platform data for DS278x battery fuel gauge drivers.

## Important APIs, types, and functions
The only type is `struct ds278x_platform_data`, with `int rsns` representing the sense resistor value or related board-specific calibration.

## Control flow, state, and persistence
No runtime logic is present. The platform data is supplied by board code or device setup and consumed during driver probe.

## Dependencies and integration points
It has no external includes. It integrates with legacy platform-data based battery/power-supply drivers.

## Risks and test signals
The main risk is unit ambiguity or an unset resistor value causing wrong current/capacity calculations. Tests should verify probe behavior with valid, missing, and boundary `rsns` values and compare reported power-supply properties against calibration data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ds2782_battery.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dsa/8021q.h -->
# sources/distributed-fs/ceph-client/include/linux/dsa/8021q.h

## Purpose
This header declares DSA tag_8021q helpers that encode DSA switch and source-port metadata into VLAN IDs. It supports DSA switches that use standard 802.1Q tags as an internal CPU-port tagging format.

## Important APIs, types, and functions
The API includes `dsa_tag_8021q_register()`, `dsa_tag_8021q_unregister()`, `dsa_tag_8021q_bridge_join()`, `dsa_tag_8021q_bridge_leave()`, `dsa_tag_8021q_bridge_vid()`, `dsa_tag_8021q_standalone_vid()`, `dsa_8021q_rx_switch_id()`, `dsa_8021q_rx_source_port()`, and `vid_is_dsa_8021q()`. `DSA_TAG_8021Q_MAX_NUM_BRIDGES` documents the three-bit VBID bridge limit with zero reserved.

## Control flow, state, and persistence
The header has no implementation, but the API implies switch registration state, bridge membership state, and deterministic VID encoding/decoding. Bridge join can report whether TX forwarding offload is active and can return extended netlink errors.

## Dependencies and integration points
It depends on `net/dsa.h`, Linux types, `struct dsa_bridge`, `struct dsa_switch`, `struct dsa_port`, and `netlink_ext_ack`. It is used by DSA taggers and switch drivers.

## Risks and test signals
Risks include VID collisions, exceeding seven bridge IDs, stale bridge-leave cleanup, and incorrect source-port decode. Tests should cover standalone and bridged VID encode/decode, bridge limit errors, unregister cleanup, and interoperability with VLAN-aware bridges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dsa/8021q.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dsa/brcm.h -->
# sources/distributed-fs/ceph-client/include/linux/dsa/brcm.h

## Purpose
This header provides Broadcom DSA tag helper macros for packing and unpacking a port and queue value into a single tag field.

## Important APIs, types, and functions
Macros are `BRCM_TAG_SET_PORT_QUEUE(p, q)`, `BRCM_TAG_GET_PORT(v)`, and `BRCM_TAG_GET_QUEUE(v)`.

## Control flow, state, and persistence
No runtime state exists. The macros encode the port in bits above the low byte and queue in the low byte.

## Dependencies and integration points
It is included by Broadcom Ethernet and DSA tag code. It has no include dependencies.

## Risks and test signals
There is no masking in `BRCM_TAG_SET_PORT_QUEUE()`, so out-of-range queue or port values can leak bits into adjacent fields. Tests should cover encode/decode round trips and boundary values for supported port and queue widths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dsa/brcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dsa/ksz_common.h -->
# sources/distributed-fs/ceph-client/include/linux/dsa/ksz_common.h

## Purpose
This header contains common Microchip KSZ DSA tagger support for timestamp decoding, deferred transmission, hardware timestamp state callbacks, and skb control-block data.

## Important APIs, types, and functions
`KSZ_TSTAMP_SEC_MASK` and `KSZ_TSTAMP_NSEC_MASK` define the 2-bit seconds plus 30-bit nanoseconds timestamp format. `ksz_decode_tstamp()` converts that format to `ktime_t`. `struct ksz_deferred_xmit_work` stores DSA port, skb, and kthread work. `struct ksz_tagger_data` carries tagger callbacks. `struct ksz_skb_cb` stores clone, PTP type, correction-update flag, and timestamp. `KSZ_SKB_CB()` casts an skb control block, and `ksz_tagger_data()` returns `ds->tagger_data`.

## Control flow, state, and persistence
Deferred transmit state persists in `kthread_work` until executed. Per-packet timestamp state is stored in `skb->cb` and must survive through tagger transmit/completion handling. Hardware timestamp enable state is controlled through the tagger callback.

## Dependencies and integration points
It depends on DSA, skbuff, kthread work, bitfield helpers, and time conversion helpers. It integrates with KSZ switch taggers and PTP timestamping paths.

## Risks and test signals
Risks include misinterpreting the nonstandard timestamp layout, skb control-block collisions with other users, and missing deferred work cleanup on port teardown. Tests should validate timestamp conversion around second rollover, TX/RX PTP clone handling, and tagger callback presence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dsa/ksz_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dsa/lan9303.h -->
# sources/distributed-fs/ceph-client/include/linux/dsa/lan9303.h

## Purpose
This header shares LAN9303 switch driver internals with its DSA tagger. It declares PHY access callbacks, the address lookup record cache, and the main chip state structure.

## Important APIs, types, and functions
`struct lan9303_phy_ops` provides `phy_read` and `phy_write` for PHY 1 and 2 access. `LAN9303_NUM_ALR_RECORDS` is 512. `struct lan9303_alr_cache_entry` stores MAC address, port bitmap, and STP override flag. `struct lan9303` holds device, regmap, IRQ chip data, reset GPIO/duration, PHY base, DSA switch pointer, indirect and ALR mutexes, ops, bridge state, saved port state, and static ALR cache.

## Control flow, state, and persistence
The header models driver-owned persistent state. The indirect mutex serializes indexed register access; the ALR mutex serializes address table cache updates. `is_bridged` and `swe_port_state` preserve switching mode, and the flat ALR cache compensates for hardware that cannot read a specific ALR entry.

## Dependencies and integration points
It includes Ethernet address constants and relies on device, regmap, GPIO descriptor, mutex, and DSA types from including code. It is shared between the LAN9303 core driver and tagger.

## Risks and test signals
Risks include stale ALR cache entries, lock ordering between indirect and ALR paths, reset timing errors, and bridge-state mismatches. Tests should cover static MAC add/delete, bridge join/leave, reset sequencing, PHY read/write callbacks, and concurrent ALR operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dsa/lan9303.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dsa/mv88e6xxx.h -->
# sources/distributed-fs/ceph-client/include/linux/dsa/mv88e6xxx.h

## Purpose
This header defines special VLAN IDs used by Marvell mv88e6xxx DSA tagging.

## Important APIs, types, and functions
`MV88E6XXX_VID_STANDALONE` is `0`, and `MV88E6XXX_VID_BRIDGED` is `VLAN_N_VID - 1`. There are no functions.

## Control flow, state, and persistence
No runtime logic is present. The constants encode tagging/classification state for standalone and bridged ports.

## Dependencies and integration points
It includes `linux/if_vlan.h` for `VLAN_N_VID`. It is consumed by mv88e6xxx DSA tag and switch code.

## Risks and test signals
Risks include collision with user-configured VLANs and inconsistent handling between switch setup and tagger paths. Tests should cover standalone/bridged transitions and VLAN filtering interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dsa/mv88e6xxx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dsa/ocelot.h -->
# sources/distributed-fs/ceph-client/include/linux/dsa/ocelot.h

## Purpose
This header defines Ocelot/Felix DSA tagger metadata, injection/extraction header layout helpers, PTP rewrite operation selection, deferred transmit work, and VLAN-tag handling for CPU-injected frames.

## Important APIs, types, and functions
Important constants define tag lengths, prefix lengths, tag types, and rewrite op codes. `struct ocelot_skb_cb` stores clone, PTP class, TX time, low timestamp bits, PTP command, and timestamp ID in the skb control block. `struct felix_deferred_xmit_work` and `struct ocelot_8021q_tagger_data` support deferred TX. Accessors and mutators such as `ocelot_xfh_get_rew_val()`, `ocelot_xfh_get_len()`, `ocelot_xfh_get_src_port()`, `ocelot_xfh_get_qos_class()`, `ocelot_xfh_get_tag_type()`, `ocelot_xfh_get_vlan_tci()`, and `ocelot_ifh_set_*()` pack/unpack bit ranges via `packing()`.

`ocelot_ptp_rew_op()` selects two-step or origin PTP rewrite operations based on skb control-block state. `ocelot_xmit_get_vlan_info()` decides which VLAN TCI and tag type to place in the injection header, removing an skb VLAN header when the bridge is VLAN-aware and otherwise using VID 0 with C-tag type.

## Control flow, state, and persistence
Per-packet state is in `skb->cb` and tag headers. Deferred transmission persists as kthread work. The extraction header parser computes frame length from LLEN/WLEN fields and extracts source/QoS/VLAN metadata. VLAN handling mutates the skb by removing VLAN tags for VLAN-aware bridges.

## Dependencies and integration points
It depends on bridge VLAN helpers, VLAN headers, kthread work, packing bitfield helpers, skbuffs, and DSA. It integrates with Ocelot and Felix switch taggers, PTP timestamping, and VLAN-aware bridge forwarding.

## Risks and test signals
Risks include bit-range packing mistakes, skb control-block collisions, incorrect length calculation (`60 * wlen + llen - 80`), VLAN tag removal side effects, and `BUG_ON()` if tagger protocol is unexpected. Tests should cover extraction/injection bit round trips, PTP two-step clone handling, VLAN-aware and VLAN-unaware bridge injection, short/long/no-prefix frames, and Seville destination-width differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dsa/ocelot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dsa/sja1105.h -->
# sources/distributed-fs/ceph-client/include/linux/dsa/sja1105.h

## Purpose
This header shares SJA1105/SJA1110 DSA tagger constants, timestamp metadata, deferred transmit work, and tagger callback data between switch drivers and tagger code.

## Important APIs, types, and functions
Constants define tag EtherTypes, default VLAN, link-local filter MAC/masks, and follow-up metadata frame source/destination MACs. `enum sja1110_meta_tstamp` distinguishes TX and RX metadata timestamps. `struct sja1105_deferred_xmit_work`, `struct sja1105_tagger_data`, and `struct sja1105_skb_cb` carry deferred TX, global tagger callbacks, clone/timestamp, and timestamp ID state. `SJA1105_SKB_CB()` casts skb control data. `sja1105_tagger_data()` validates the active tag protocol and returns `ds->tagger_data`.

## Control flow, state, and persistence
State is per-packet in `skb->cb`, per-switch in tagger data, and deferred in kthread work. Metadata timestamp handling is callback-based: tagger code receives metadata frames and invokes the driver-provided handler with switch, port, timestamp ID, direction, and timestamp.

## Dependencies and integration points
It depends on skbuffs, Ethernet helpers, DSA 8021Q helpers, and DSA core. It integrates with SJA1105/SJA1110 taggers, PTP timestamping, and link-local filtering.

## Risks and test signals
Risks include protocol mismatch causing `BUG_ON()`, skb control-block reuse, wrong metadata MAC filtering, and timestamp ID mismatches between clones and metadata frames. Tests should cover PTP TX/RX metadata delivery, deferred TX cleanup, tag protocol selection, and link-local filter behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dsa/sja1105.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dsa/tag_qca.h -->
# sources/distributed-fs/ceph-client/include/linux/dsa/tag_qca.h

## Purpose
This header defines Qualcomm/Atheros DSA tag layout constants and management packet structures for in-band MDIO/register access, MIB autocast, and register write/read acknowledgements.

## Important APIs, types, and functions
Constants define the 2-byte QCA header version, RX fields, TX fields, packet types, management check code, management packet component lengths, and bitfields for sequence, check code, command, length, and address. `struct qca_mgmt_ethhdr` emulates an Ethernet header containing command, sequence, first MDIO data word, and QCA header. `enum mdio_cmd` provides write/read command values. `struct mib_ethhdr` carries the first MIB counter data and QCA header. `struct qca_tagger_data` provides ack and MIB callback hooks.

## Control flow, state, and persistence
The header has no implementation. Per-packet state is encoded in the QCA tag and management packet headers. Tagger data callbacks let switch drivers receive asynchronous in-band management acknowledgements and MIB autocast frames.

## Dependencies and integration points
It depends on Linux bitfield/type helpers and forward-declares DSA switch and skb structures. It integrates with QCA DSA taggers and switch drivers using Ethernet management frames.

## Risks and test signals
Risks include endian mistakes in packed headers, wrong minimum packet padding, invalid management check codes, and callback/lifetime issues for async acknowledgements. Tests should cover RX/TX header encode/decode, MDIO read/write management packets, MIB autocast handling, and invalid packet rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dsa/tag_qca.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dtlk.h -->
# sources/distributed-fs/ceph-client/include/linux/dtlk.h

## Purpose
This header defines constants, ioctl numbers, status bits, commands, and settings layout for the DoubleTalk speech synthesizer driver.

## Important APIs, types, and functions
Constants include `DTLK_MINOR`, I/O extent, ioctl command values `DTLK_INTERROGATE` and `DTLK_STATUS`, clear command, retry calculation, TTS status bits, LPC speak commands, and LPC status bits. `struct dtlk_settings` describes the data returned by the interrogate command, including serial number, ROM version, mode, punctuation level, formant frequency, pitch, speed, volume, tone, expression, dictionary flags, free RAM, articulation, reverb, end marker, and indexing support.

## Control flow, state, and persistence
No functions are declared. State is read from device hardware via ioctl and interpreted through `struct dtlk_settings` and status bit masks. Retry behavior depends on `loops_per_jiffy` and `HZ`.

## Dependencies and integration points
The header is consumed by the DoubleTalk character device driver and possibly user-space ioctl callers. It assumes kernel timing symbols are visible where retry constants are used.

## Risks and test signals
Risks include ABI packing assumptions for `struct dtlk_settings`, ioctl number stability, timing-dependent retries, and incorrect interpretation of status bits across device modes. Tests should cover interrogate/status ioctl decoding, clear command behavior, writable/readable polling, and LPC buffer underflow reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dtlk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dtpm.h -->
# sources/distributed-fs/ceph-client/include/linux/dtpm.h

## Purpose
This header declares Dynamic Thermal Power Management hierarchy support. It models powercap zones as DTPM nodes and provides registration and hierarchy creation APIs.

## Important APIs, types, and functions
`struct dtpm` embeds `struct powercap_zone` and stores parent/child/sibling links, ops, flags, power limit/max/min, and weight. `struct dtpm_ops` provides set/get/update power and release callbacks. `struct dtpm_subsys_ops` declares subsystem init/exit/setup. `enum DTPM_NODE_TYPE` distinguishes virtual and device-tree nodes, and `struct dtpm_node` describes static hierarchy nodes. APIs include `to_dtpm()`, `dtpm_update_power()`, `dtpm_release_zone()`, `dtpm_init()`, `dtpm_unregister()`, `dtpm_register()`, `dtpm_create_hierarchy()`, and `dtpm_destroy_hierarchy()`.

## Control flow, state, and persistence
DTPM state persists as a powercap-zone hierarchy. Parent/child lists model aggregate and leaf power zones; ops update current power and limits. Hierarchy creation consumes OF match tables and subsystem setup callbacks.

## Dependencies and integration points
It depends on `linux/powercap.h` and device-tree types. It integrates with thermal/powercap control, SoC energy models, and platform-specific DTPM subsystems.

## Risks and test signals
Risks include inconsistent parent/child accounting, missing release callbacks, unit mistakes for microwatts, and hierarchy teardown leaks. Tests should cover registration/unregistration, aggregate power updates, power limit propagation, OF hierarchy creation, and release paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dtpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dw_apb_timer.h -->
# sources/distributed-fs/ceph-client/include/linux/dw_apb_timer.h

## Purpose
This header declares common support for Synopsys DesignWare APB timers used as clockevent and clocksource devices.

## Important APIs, types, and functions
`APBTMRS_REG_SIZE` is the timer register span. `struct dw_apb_timer` stores MMIO base, frequency, and IRQ. `struct dw_apb_clock_event_device` embeds a clock event device, timer, and optional end-of-interrupt callback. `struct dw_apb_clocksource` embeds a timer and clocksource. APIs initialize/register clockevents and clocksources, start a clocksource, and read its counter.

## Control flow, state, and persistence
Timer state persists in MMIO registers and wrapper structs. Clockevent registration wires interrupts and event callbacks into the generic timekeeping framework. Clocksource start/read controls a free-running counter used for timekeeping.

## Dependencies and integration points
It depends on clockchips, clocksources, and interrupt headers. It is shared by platform timer drivers on ARM and other SoCs with DW APB timers.

## Risks and test signals
Risks include wrong frequency, invalid MMIO base, IRQ/EIO handling mistakes, and clocksource wrap/width assumptions. Tests should cover init failure paths, interrupt event delivery, clocksource monotonicity, suspend/resume if implemented in callers, and per-CPU clockevent registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dw_apb_timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dynamic_debug.h -->
# sources/distributed-fs/ceph-client/include/linux/dynamic_debug.h

## Purpose
This header implements the compile-time and runtime callsite metadata interface for dynamic debug. It places descriptors and class maps in special ELF sections, then wraps debug print calls in runtime flags or jump-label branches.

## Important APIs, types, and functions
`struct _ddebug` describes a callsite with module, function, file, format, line, class ID, flags, and optional static key. Flag bits control printing and whether module/function/line/TID/source/stack are included. `enum class_map_type`, `struct ddebug_class_map`, `DECLARE_DYNDBG_CLASSMAP()`, `struct _ddebug_info`, and `struct ddebug_class_param` support class-based debug controls.

When dynamic debug is enabled, exported functions include `__dynamic_pr_debug()`, `__dynamic_dev_dbg()`, `__dynamic_netdev_dbg()`, and `__dynamic_ibdev_dbg()`. Macros such as `DEFINE_DYNAMIC_DEBUG_METADATA_CLS()`, `dynamic_pr_debug_cls()`, `dynamic_pr_debug()`, `dynamic_dev_dbg()`, `dynamic_netdev_dbg()`, `dynamic_ibdev_dbg()`, and `dynamic_hex_dump()` create metadata and conditionally call print functions. Module parameter hooks are `ddebug_dyndbg_module_param_cb()`, `param_set_dyndbg_classes()`, `param_get_dyndbg_classes()`, and `param_ops_dyndbg_classes`.

## Control flow, state, and persistence
Each debug macro creates a static `_ddebug` descriptor in `__dyndbg`; class maps go into `__dyndbg_classes`. Runtime control changes descriptor flags and optional static keys through debugfs/module parameters. The branch path is static-key backed when jump labels are available, or flag-checked otherwise. If dynamic debug is disabled, macros compile to `no_printk()` or dead code while retaining format checking.

## Dependencies and integration points
It depends on jump labels when enabled, build bug checks, module metadata, debugfs control infrastructure, printk/device/netdev/ibdev debug routines, and kernel parameter ops. It integrates with `pr_debug()`, device debug wrappers, and subsystem-specific class controls.

## Risks and test signals
Risks include format string duplication in macros, class ID overflow, static-key state desynchronization, stack dump overhead when enabled, and control file parsing errors. Tests should cover compile-time format checking in disabled builds, enabling/disabling callsites through dynamic_debug/control, class-map parameter parsing, jump-label branch toggling, and no-op behavior when only core support is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dynamic_debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dynamic_queue_limits.h -->
# sources/distributed-fs/ceph-client/include/linux/dynamic_queue_limits.h

## Purpose
This header defines Dynamic Queue Limits, a feedback mechanism for producer/consumer queues such as network hardware rings. It adjusts a queue limit to keep enough queued work to avoid starvation while minimizing latency and queued data.

## Important APIs, types, and functions
`struct dql` stores enqueue-path counters (`num_queued`, `adj_limit`, `last_obj_cnt`), stall tracking state, completion-path counters and previous state, slack tracking, configured min/max/hold time, and reported stall metrics. Constants include `DQL_HIST_LEN`, `DQL_MAX_OBJECT`, and `DQL_MAX_LIMIT`. Inline helpers are `dql_queue_stall()`, `dql_queued()`, and `dql_avail()`. Implemented elsewhere are `dql_completed()`, `dql_reset()`, and `dql_init()`.

## Control flow, state, and persistence
Enqueue callers check `dql_avail()`, then call `dql_queued()` with the number of objects queued. Completion callers call `dql_completed()` to retire objects and recalculate the limit. Stall tracking records jiffies bits in a ring history if `stall_thrs` is set. State is in-memory only and must be protected by caller-provided locking; enqueue and completion paths may use different locks according to the header comments.

## Dependencies and integration points
It depends on bitops, bug/WARN support, jiffies, barriers, and cacheline alignment. It is used by networking and other queueing subsystems to tune hardware/software queue depth.

## Risks and test signals
Risks include missing serialization, counter overflow, invalid count values, barrier mistakes in stall history, and stale limits after reset. `dql_queued()` warns and returns if `count > DQL_MAX_OBJECT`. Tests should cover enqueue/completion race patterns with caller locks, limit growth/shrink behavior, stall detection, reset/init defaults, and overflow boundary values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dynamic_queue_limits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/earlycpio.h -->
# sources/distributed-fs/ceph-client/include/linux/earlycpio.h

## Purpose
This header declares a helper for finding files in an early CPIO archive, commonly used during early boot before the full VFS is available.

## Important APIs, types, and functions
`MAX_CPIO_FILE_NAME` is 18. `struct cpio_data` carries a data pointer, size, and fixed-size name. `find_cpio_data(const char *path, void *data, size_t len, long *offset)` searches a CPIO memory range for a named entry and returns its data descriptor.

## Control flow, state, and persistence
No state is stored by the header. The implementation scans an archive buffer and can report the offset of the found entry or scan position.

## Dependencies and integration points
It depends on Linux types and integrates with early initramfs/initrd parsing and boot-time firmware/data loading.

## Risks and test signals
Risks include fixed name buffer truncation, malformed CPIO records, alignment/padding errors, and invalid offset handling. Tests should cover found/missing files, long names, zero-length files, malformed archives, and offset progression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/earlycpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ecryptfs.h -->
# sources/distributed-fs/ceph-client/include/linux/ecryptfs.h

## Purpose
This header defines eCryptfs shared kernel/user authentication token structures, version constants, feature bits, cipher identifiers, key sizes, and passphrase/private-key token layouts.

## Important APIs, types, and functions
Version constants include major/minor and supported file version. Feature bits advertise passphrase, pubkey, plaintext passthrough, policy, xattr, multikey, devmisc, HMAC, filename encryption, and GCM support. Size constants define password, salt, signature, key, encrypted key, and PKI-name limits. Cipher constants mirror RFC2440 values.

Structures include `struct ecryptfs_session_key`, `struct ecryptfs_password`, `enum ecryptfs_token_types`, `struct ecryptfs_private_key`, and packed `struct ecryptfs_auth_tok`. Session-key flags indicate whether user space should decrypt/encrypt and whether decrypted/encrypted key data is present. Password tokens carry hash parameters, session-key encryption key, hex signature, and salt. Private-key tokens carry key size, signature, PKI type, and flexible data.

## Control flow, state, and persistence
There is no code, but the structs are persistent ABI data exchanged between kernel and user space and stored or referenced in keyrings/auth flows. The packed auth token layout is especially ABI-sensitive.

## Dependencies and integration points
It integrates with eCryptfs mount helpers, key management, sysfs feature reporting, cryptographic token parsing, and encrypted filesystem metadata handling.

## Risks and test signals
Risks include ABI layout changes, exposing decrypted key material, buffer-size mistakes around hex signatures and salts, and accepting unsupported cipher/version combinations. Tests should cover struct size/layout compatibility, passphrase and private-key token parsing, feature-bit reporting, key length bounds, and secure zeroing in implementation code that handles these structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ecryptfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/edac.h -->
# sources/distributed-fs/ceph-client/include/linux/edac.h

## Purpose
This header defines the Error Detection and Correction core interfaces for memory controllers and newer RAS device features. It models memory topology, DIMMs/ranks/csrows, error counters, raw error reports, controller operations, scrub/ECS/memory-repair feature operations, and EDAC device registration.

## Important APIs, types, and functions
Global state includes `edac_op_state` and `edac_get_sysfs_subsys()`. `opstate_init()` normalizes unsupported operation states to polling. Enums define device width (`dev_type`), hardware memory-controller error severity (`hw_event_mc_err_type`), memory technology (`mem_type`), EDAC capability (`edac_type`), scrub capability (`scrub_type`), memory hierarchy layers (`edac_mc_layer_type`), RAS feature type (`edac_dev_feat`), memory repair type, and memory repair command.

Core topology structs are `edac_mc_layer`, `dimm_info`, `rank_info`, `csrow_info`, `errcount_attribute_data`, `edac_raw_error_desc`, and `mem_ctl_info`. `mem_ctl_info` holds device/sysfs identity, global list linkage, capabilities, scrub mode and callbacks, `edac_check`, page-to-physical translation, csrow and DIMM arrays, private driver data, no-info counters, completion, driver attributes, delayed work, raw error descriptor, debugfs state, fake injection fields, operation state, and flexible hierarchy layers. `mci_for_each_dimm()` iterates DIMMs, and `edac_get_dimm()` maps layer coordinates to a DIMM.

RAS feature APIs include `struct edac_scrub_ops`, `edac_scrub_get_desc()`, `struct edac_ecs_ops`, `edac_ecs_get_desc()`, `struct edac_mem_repair_ops`, `edac_mem_repair_get_desc()`, `struct edac_dev_data`, `struct edac_dev_feat_ctx`, `struct edac_dev_feature`, and `edac_dev_register()`.

## Control flow, state, and persistence
EDAC controller state persists in `mem_ctl_info` objects registered with the EDAC core. Error counters are stored at DIMM, rank/csrow, and controller levels. Polling, interrupt, and NMI operation modes determine how `edac_check()` is invoked by implementation code. Raw error details are staged in the controller-owned `edac_raw_error_desc`. Scrub, ECS, and memory repair operations expose driver callbacks through sysfs-style descriptors when configured.

## Dependencies and integration points
It depends on device model, completions, workqueues, debugfs, NUMA, atomics, and optional EDAC feature configs. It integrates with memory-controller drivers, firmware error reporting, sysfs/debugfs, RAS tools, CXL-like memory repair flows, and page offlining/poison handling in implementation layers.

## Risks and test signals
Risks include topology index mistakes in `edac_get_dimm()`, direct driver mutation of fields meant for the core, stale counters, unsafe fake injection, missing mandatory memory-repair callbacks, and inconsistent sysfs descriptors when feature configs are disabled. Tests should cover layer-to-DIMM indexing for one/two/three layers, error counter updates, poll work scheduling, scrub/ECS/memory-repair descriptor stubs, memory repair validation requiring `do_repair` and HPA/DPA setters, and controller registration/unregistration cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/edac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/edd.h -->
# sources/distributed-fs/ceph-client/include/linux/edd.h

## Purpose
This header exposes BIOS Enhanced Disk Drive data collected during early x86 boot. It wraps the UAPI EDD structures and declares the global kernel `edd` table.

## Important APIs, types, and functions
It includes `uapi/linux/edd.h` and declares `extern struct edd edd` outside assembly.

## Control flow, state, and persistence
The persistent state is populated by boot code from BIOS int 13h EDD information and later used by firmware/EDD drivers to identify BIOS boot disks. The header has no functions.

## Dependencies and integration points
It integrates with x86 boot setup code, boot parameters, and `drivers/firmware/edd.c`. The comment emphasizes that setup assembly is sensitive to UAPI structure sizes.

## Risks and test signals
Risks include structure-size drift, bootloader/BIOS malformed records, and incorrect disk matching. Tests should verify boot-time population, UAPI layout stability, and mapping between BIOS devices and kernel block devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/edd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/eeprom_93cx6.h -->
# sources/distributed-fs/ceph-client/include/linux/eeprom_93cx6.h

## Purpose
This header defines a bit-banged access abstraction for 93cx6 EEPROM chips used by PCI/network drivers. It supplies opcodes, address widths, controller callbacks, line-state fields, quirks, and read/write helper declarations.

## Important APIs, types, and functions
Constants define widths for 93C46/56/66/86, opcode width, read/write/erase and write-enable/disable opcodes, and `PCI_EEPROM_QUIRK_EXTRA_READ_CYCLE`. `struct eeprom_93cx6` contains private data, `register_read` and `register_write` callbacks, width, quirks, drive-data flag, and register line fields for data in/out, clock, and chip select. APIs include word and byte read/multiread functions, `eeprom_93cx6_wren()`, `eeprom_93cx6_write()`, and `has_quirk_extra_read_cycle()`.

## Control flow, state, and persistence
The implementation toggles the line-state fields and calls driver-provided register read/write callbacks to clock commands and data into the EEPROM. EEPROM contents persist in hardware; the struct stores transient bus line state and controller-specific context.

## Dependencies and integration points
It depends on `linux/bits.h` and integrates with drivers that provide register access to EEPROM pins, such as wireless or Ethernet adapters.

## Risks and test signals
Risks include wrong address width, missing extra read cycle for quirky chips, write-enable misuse, endian mistakes in multiread, and callbacks that do not update line fields correctly. Tests should cover read/write opcode sequencing, byte and word reads, write enable/disable, quirk handling, and driver callback ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/eeprom_93cx6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/efi-bgrt.h -->
# sources/distributed-fs/ceph-client/include/linux/efi-bgrt.h

## Purpose
This header declares ACPI BGRT support for EFI boot graphics resource table handling. It exposes initialization/parsing hooks and the parsed BGRT image metadata when enabled.

## Important APIs, types, and functions
When `CONFIG_ACPI_BGRT` is enabled, APIs are `efi_bgrt_init(struct acpi_table_header *table)` and `acpi_parse_bgrt(struct acpi_table_header *table)`. Extern data are `bgrt_image_size` and `bgrt_tab`. When disabled, both functions are inline no-ops returning success for parse.

## Control flow, state, and persistence
The implementation parses an ACPI BGRT table during boot and stores the image size and table data globally. The data is valid only if the underlying BGRT image exists, as noted by the header comment.

## Dependencies and integration points
It depends on ACPI table definitions and integrates with EFI firmware boot logo/resource handling and ACPI table parsing.

## Risks and test signals
Risks include malformed ACPI tables, stale image pointers, disabled-config no-op behavior hiding missing support, and boot-time memory lifetime issues. Tests should cover valid and invalid BGRT parsing, disabled-config stubs, image-size reporting, and use only after a valid BGRT image is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/efi-bgrt.h -->
