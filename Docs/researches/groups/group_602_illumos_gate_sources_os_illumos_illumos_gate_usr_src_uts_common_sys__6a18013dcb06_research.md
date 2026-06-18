# Group Research: group_602_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__6a18013dcb06

Scope: `Docs/research_subset_a.md`, source tree `sources/os/illumos/illumos-gate`.

Summary: This group is a mixed set of illumos common system headers. The filesystem-adjacent pieces are mount/mnttab/mmap/mode/model/module linkage and memory/device ABIs; the storage-specific centerpiece is `mdi_impldefs.h` for MPxIO multipathing. Several headers are network MAC/MII support, machine-description firmware support, generic kernel utilities, audio/mouse legacy ABI, and digest constants. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_provider.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_provider.h

Purpose: Defines the GLDv3 MAC provider interface used by network drivers to register links, advertise capabilities, expose callbacks, and interact with MAC-layer rings, groups, offloads, VLAN handling, transceivers, and LEDs.

Key interfaces:
- Versioning: `MAC_VERSION_V1`, `MAC_VERSION`.
- Capability enum: checksum, LSO, rings, shares, multiple factory addresses, VNIC/aggr/VRRP/overlay/transceiver/LED capabilities.
- Driver callbacks: `mac_callbacks_t` and `MC_*` flags for optional callbacks.
- Ring/group capability structures: `mac_capab_rings_t`, `mac_ring_info_t`, `mac_group_info_t`.
- Registration: `mac_register_t`, `mac_alloc()`, `mac_register()`, `mac_unregister()`.
- Data path notifications: `mac_rx()`, `mac_rx_ring()`, link/unicast/TX/capability update calls.
- Packet offload inspection: `mac_ether_offload_info_t`, `mac_ether_l2_info()`, `mac_partial_offload_info()`.

Important details:
- The callback flag model preserves binary compatibility: new optional callbacks require new `MC_*` bits.
- VLAN ID zero is translated to `MAC_VLAN_UNTAGGED` at the provider boundary to disambiguate untagged traffic from priority-tagged VLAN 0.
- Ring classification distinguishes no/software/hardware/passthrough classification and determines whether MAC must classify incoming traffic.
- Private APIs at the bottom expose packet header/offload metadata and explicitly note synchronization requirements with the userspace `mac_test` program.

Relevance to subset A: Not filesystem code, but it is core OS/network kernel infrastructure in the included illumos tree.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_provider.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_soft_ring.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_soft_ring.h

Purpose: Defines MAC soft rings and soft ring sets, the queueing, fanout, worker/polling, flow-control, and quiesce/restart machinery used by GLDv3 receive/transmit scaling.

Key structures:
- `mac_soft_ring_t`: per-lane queue with lock, packet chain, TX watermarks, RX callback, worker thread, CPU binding, stats, teardown state, and parent SRS pointer.
- `mac_soft_ring_set_t`: shared Rx/Tx queue/controller with SRS type/state flags, ring arrays, bandwidth control, CPU binding, poll/worker threads, client/flow/ring backpointers, and embedded `mac_srs_rx_t`/`mac_srs_tx_t`.
- `mac_srs_rx_t`: receive-side callbacks, polling thresholds, high/low watermarks, and many poll/drain counters.
- `mac_srs_tx_t`: transmit mode, TX function, hardware ring/group pointers, queue thresholds, stats, aggregation ring mapping.

State model:
- `mac_soft_ring_state_t` separates immutable `ST_RING_*` traits from live `S_RING_*` processing, blocking, blanking, quiesce, restart, and condemn flags.
- `mac_soft_ring_set_type` describes static or administrative traits such as link/flow, Tx/Rx, no soft rings, protocol fanout, latency optimization, default group, bandwidth control, DLS bypass, and client polling.
- `mac_soft_ring_set_state_t` captures live SRS processing state: worker/poll ownership, polling mode, TX blocking/high-water, client processing, quiesce/restart/condemn, and global-list membership.

Key macros and APIs:
- `MAC_SRS_POLLING_OFF`, `MAC_COUNT_CHAIN`, and `MAC_UPDATE_SRS_COUNT_LOCKED` encode hot-path queue/poll transitions.
- Exports creation, destruction, wakeup, polling, DLS bypass, client polling, quiesce/restart, fanout setup, TX SRS setup, ring add/delete, bandwidth updates, and worker drain routines.

Important details:
- The file documents strict ownership around `SRS_PROC`/`S_RING_PROC` and lock release while processing packets.
- Quiesce/condemn/restart is explicit at both SRS and soft-ring level, with condition variables and counters for teardown synchronization.
- Receive polling tracks packets queued between SRS and soft rings so hardware interrupt re-enable decisions account for backlog not yet delivered to clients.

Relevance to subset A: Not filesystem code, but important illumos kernel scheduling/queueing infrastructure.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_soft_ring.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_stat.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_stat.h

Purpose: Declares MAC-layer statistics structures and kstat lifecycle helpers for flows, rings, SRSes, soft rings, drivers, and defunct lanes.

Key structures:
- `mac_rx_stats_t`: local, poll, interrupt, drop, chain-size, and input-error counters.
- `mac_tx_stats_t`: output bytes/packets/errors, descriptor block/unblock counters, and soft drops.
- `mac_misc_stats_t`: multicast/broadcast counters, TX errors, defunct lane stats, and link-protection drops.

Key APIs:
- `mac_misc_stat_create/delete()`
- `mac_ring_stat_create/delete()`
- `mac_srs_stat_create/delete()`, `mac_tx_srs_stat_recreate()`
- `mac_soft_ring_stat_create/delete()`
- `mac_driver_stat_create/delete()`, `mac_driver_stat_default()`
- ring stat getters for RX/TX.

Important detail: TX block and unblock counters are intended to match in healthy descriptor-flow behavior; mismatch indicates a lower-layer wakeup failure.

Relevance to subset A: Network infrastructure, not filesystem-specific.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_stat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_wifi.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_wifi.h

Purpose: Defines the WiFi MAC-type plugin contract for GLDv3 wireless drivers.

Key definitions:
- Plugin identifier: `MAC_PLUGIN_IDENT_WIFI`.
- Maximum WiFi header size: `WIFI_HDRSIZE`.
- WiFi statistics enum beginning at `MACTYPE_STAT_MIN`.
- Security modes: `WIFI_SEC_NONE`, `WIFI_SEC_WEP`, `WIFI_SEC_WPA`.
- `wifi_data_t`: option flags, BSSID, operation mode, security header allocation policy, and QoS padding.

Important details:
- `wd_opts` is reserved as an extensibility bitmap so drivers and plugin can evolve independently.
- `wd_qospad` handles hardware needing 802.11 QoS/4-address header padding.

Relevance to subset A: Network plugin ABI, outside filesystem focus.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_wifi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/machelf.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/machelf.h

Purpose: Provides machine-class-transparent ELF typedefs and macros so common code can use native `Ehdr`, `Shdr`, `Sym`, `Phdr`, `Dyn`, etc. independent of ELF32/ELF64 build mode.

Key behavior:
- Selects architecture ELF header definitions for amd64/i386/sparc.
- Under `_ELF64` without `_ELF32_COMPAT`, maps generic names to `Elf64_*`; otherwise maps to `Elf32_*`.
- In kernel builds, maps relocation and symbol helper macros to `ELF32_*` or `ELF64_*`.
- Defines `EC_*` printf cast macros for shared format strings across ELF classes.

Important detail: `EC_NATPTR()` casts via `uintptr_t` for native pointers to avoid compiler complaints about direct pointer-to-wide-integer casts.

Relevance to subset A: Core executable/module support; indirectly relevant to kernel module loading and exec handling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/machelf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/map.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/map.h

Purpose: Declares legacy kernel resource-map allocation routines.

Key APIs:
- `rmallocmap()`, `rmallocmap_wait()`, `rmfreemap()`
- `rmalloc()`, `rmalloc_wait()`, `rmfree()`

Important detail: The public type is opaque (`struct map` forward declaration); callers use map handles through the allocation/free routines.

Relevance to subset A: Kernel memory/resource allocation utility that may be used by low-level subsystems.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/map.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/md4.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/md4.h

Purpose: Declares the RSA MD4 message-digest context and routines.

Key definitions:
- `MD4_DIGEST_LENGTH` is 16 bytes.
- `MD4_CTX` contains four-word state, bit count, and 64-byte input buffer.
- APIs: `MD4Init()`, `MD4Update()`, `MD4Final()`.

Important detail: This is classic MD4 compatibility code; it should be treated as a legacy digest interface, not modern cryptographic security.

Relevance to subset A: General kernel/common utility header.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/md4.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/md5.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/md5.h

Purpose: Declares RFC 1321-style MD5 hashing context and routines.

Key definitions:
- `MD5_DIGEST_LENGTH` is 16 bytes.
- `MD5_CTX` stores four-word state, bit count, and a 64-byte buffer union with byte and aligned `uint32_t` views.
- APIs: `MD5Init()`, `MD5Update()`, `MD5Final()`.

Important detail: The buffer union supports realigned input access for implementation efficiency.

Relevance to subset A: General digest utility; may support checksums/legacy formats but is not filesystem-specific here.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/md5.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/md5_consts.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/md5_consts.h

Purpose: Defines the MD5 round constants, initialization constants, and shift amounts from RFC 1321.

Key definitions:
- `MD5_CONST_0` through `MD5_CONST_63`.
- Initial state constants `MD5_INIT_CONST_1` through `MD5_INIT_CONST_4`.
- Shift constants for all four MD5 rounds.

Important detail: This header contains constants only; the transform logic is elsewhere.

Relevance to subset A: General digest implementation support.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/md5_consts.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mdesc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mdesc.h

Purpose: Defines the external machine-description format and API for logical domains receiving a virtual machine description from the hypervisor.

Key definitions:
- Header offsets and sizes: `MD_HEADER_*`, `MD_HEADER_SIZE`, `MD_ELEMENT_SIZE`.
- Transport version: `MD_TRANSPORT_VERSION`.
- Element tags: list end, null, node, node end, property arc/value/string/data.
- Opaque handles: `md_t`, `mde_cookie_t`, `mde_str_cookie_t`, `md_diff_cookie_t`.
- Invalid cookie/generation constants.

Key APIs:
- Lifecycle and metadata: `md_init_intern()`, `md_fini()`, `md_node_count()`, `md_root_node()`, `md_get_gen()`, `md_get_bin_size()`.
- Lookup/walk: `md_find_name()`, `md_scan_dag()`, `md_walk_dag()`.
- Property access: `md_get_prop_val()`, `md_get_prop_str()`, `md_get_prop_data()`, `md_get_prop_arcs()`.
- Diff interface: `md_diff_init()`, `md_diff_added()`, `md_diff_removed()`, `md_diff_matched()`, `md_diff_fini()`.
- `mdesc` device ioctls for quote buffer sizing/discard.

Important detail: The DAG walker passes both parent and current node to callbacks because nodes can have multiple parents, but the walk visits each node once.

Relevance to subset A: Virtualization/platform hardware description support.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mdesc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mdesc_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mdesc_impl.h

Purpose: Defines internal representation and byte-order helpers for machine descriptions.

Key structures:
- `md_header_t`: transport version and byte sizes for node, name, and data blocks.
- `md_element_t`: 16-byte element with tag, name metadata, and value/data/arc union.
- `md_impl_t`: parsed machine description session with allocator hooks, block pointers, sizes, counts, root node, generation, and magic value.

Key macros:
- `LIBMD_MAGIC`.
- `mdtoh*` and `htomd*` byte-order conversions; machine descriptions are stored in network byte order.
- Accessors for element tag, name, property offsets/lengths, values, and indexes.

Key APIs:
- `md_ident_name_str()`
- `md_find_node_prop()`

Important detail: Elements are referenced by index derived from byte offset divided by 16, avoiding alignment-sensitive pointers into the node block.

Relevance to subset A: Virtualization/platform support internals.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mdesc_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mdi_impldefs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mdi_impldefs.h

Purpose: Defines internal Multiplexed Device Interface (MDI/MPxIO) structures, locks, state flags, pathinfo state transitions, vhci cache data, path selection, and failover APIs.

Architecture described:
- `mpxio` provides the core multipath framework.
- vHCI drivers manage a multipath class, such as `scsi_vhci`.
- pHCI drivers provide physical transport paths.
- Client devices are target/leaf drivers such as disk drivers.
- `mdi_pathinfo` nodes connect client devices and pHCIs into a matrix.

Key structures:
- `mdi_vhci_ops_t`: vHCI callbacks for path init/uninit/state change, failover, client attach, and support probing.
- `mdi_vhci_t`: registered virtual HCI with class name, devinfo, config, load-balancing policy, pHCI list, and client hash.
- `mdi_phci_t`: physical HCI with path list, flags, unstable counter, and vHCI-private data.
- `mdi_client_t`: multipath client with GUID, driver name, load-balancing policy, path list, state, failover/power/unconfigure state, and private data.
- `struct mdi_pathinfo`: per path tuple tying client to pHCI with address, instance, state, properties, private data, kstats, preferred flag, and flags.
- `mdi_pi_kstats` and `pi_errs`: per client-pHCI aggregate I/O/error stats.
- `mdi_vhci_cache_t`, `mdi_vhci_config_t`, and related cache structs: on-disk vHCI busconfig cache and asynchronous path configuration state.

State and locking:
- The header documents lock granularity and ordering across global MDI, vHCI pHCI/client locks, pHCI lock, client lock, and pathinfo lock.
- pHCI/client unstable counters block hotplug/failover during transient path state.
- pHCI and client flags cover offline, suspend, power down, detach, user/driver disable, transient disable, and power transition.
- Pathinfo macros implement init, online, offline, standby, fault, transient, hidden, removed, and disable states while preserving extended-state bits.

Key APIs:
- vHCI registration: `mdi_vhci_register()`, `mdi_vhci_unregister()`.
- Path counts and path-to-devinfo helpers for pHCI/client.
- Path selection: `mdi_select_path()`, load-balancing setters/getter, selection flags.
- Failover: `mdi_failover()` with sync/async flags.
- Device support probe: `mdi_is_dev_supported()`.
- Path kstat helpers and path state/private-data helpers.
- Property packing and obsolete path iteration helpers.

Relevance to subset A: Highly relevant storage infrastructure. This is the main block-storage/multipathing contract in the group and directly affects disk path selection, failover, hotplug behavior, and observability.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mdi_impldefs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mem.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mem.h

Purpose: Defines memory device minor numbers, private `/dev/mem` ioctls, FMA memory retirement ioctls, and kernel helpers/logging structures.

Key definitions:
- Minor numbers: `/dev/mem`, `/dev/kmem`, `/dev/null`, `/dev/allkmem`, `/dev/zero`, `/dev/full`.
- `MEM_VTOP` ioctl and `mem_vtop_t`/`mem_vtop32_t` for virtual-to-physical translation.
- Private FMD ioctls: naming/info, page retire/unretire/isretired/error queries, retire causes, serial ID.
- Page error bits and `MEM_FMRI_MAX_BUFSIZE`.
- `mem_name_t` and `mem_info_t` for memory FRU/naming and topology data.

Kernel-only:
- `impl_obmem_pfnum()`
- `plat_mem_do_mmio()`
- `mm_logentry_t` for logging writes to memory devices.

Important detail: Several interfaces are explicitly private to FMD/libkvm and not stable application/driver contracts.

Relevance to subset A: Core memory/device ABI, relevant to OS kernel behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mem_cage.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mem_cage.h

Purpose: Declares kernel memory-caging interfaces and state.

Key definitions:
- Cage creation return/status constants: `KCT_FAILURE`, `KCT_CRIT`, `KCT_NONCRIT`.
- Global cage state and thresholds: enable flags, cageout thread, free/need/lots/des/min/throttle free counts.
- Direction enum: `KCAGE_UP`, `KCAGE_DOWN`.

Key APIs:
- Free-memory accounting: `kcage_freemem_add/sub()`.
- Throttle and range setup: `kcage_create_throttle()`, `kcage_range_init()`, `kcage_range_add()`.
- Range queries/deletion: `kcage_current_pfn()`, `kcage_range_delete()`, `kcage_range_delete_post_mem_del()`.
- Threshold recalculation and pageout/clock hooks: `kcage_recalc_thresholds()`, `kcage_cageout_init()`, `kcage_cageout_wakeup()`, `kcage_tick()`.
- Pagelist integration: `kcage_next_range()`.

Relevance to subset A: Kernel physical memory management, relevant to memory delete/relocation behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mem_cage.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mem_config.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mem_config.h

Purpose: Declares kernel physical memory add/delete interfaces, query/status structures, error codes, callback registration, and architecture hooks.

Key structures:
- `memquery_t`: physical, managed, nonrelocatable page counts and nonrelocatable PFN range.
- `memdelstat_t`: physical, managed, and collected page counts during delete.
- `kphysm_setup_vector_t`: post-add, pre-delete, and post-delete callbacks.

Key APIs:
- Add: `kphysm_add_memory_dynamic()`.
- Delete handle lifecycle: `kphysm_del_gethandle()`, `kphysm_del_release()`, `kphysm_del_cancel()`.
- Delete span and query: `kphysm_del_span()`, `kphysm_del_span_query()`.
- Delete execution/status: `kphysm_del_start()`, `kphysm_del_status()`.
- Callback register/unregister.
- Architecture lower interfaces: span check, relocate, support query, PFN deletion query.

Important detail: Error codes model sequencing, nonrelocatable memory, resource shortage, viability failure, cancellation, duplicate spans, and async completion states.

Relevance to subset A: Physical memory hotplug/remove infrastructure.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mem_config.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/memlist.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/memlist.h

Purpose: Defines the common boot/kernel memory segment list format.

Key definitions:
- `memlist_t`: doubly-linked list of address/size memory segments.
- `phys_install`: installed physical memory list, mutable as memory is added/deleted.
- x86-only `bios_rsvd`: BIOS reserved memory list.
- `address_in_memlist()` and `num_phys_pages()`.

Important detail: Readers of `phys_install` are expected to use `memlist_read_lock()`/`memlist_read_unlock()` even though those lock APIs are declared elsewhere.

Relevance to subset A: Core physical memory inventory structure.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/memlist.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/memlist_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/memlist_impl.h

Purpose: Declares common internal helpers for allocating, freeing, inserting, deleting, finding, and modifying `struct memlist` spans.

Key APIs:
- Allocation/free: `memlist_get_one()`, `memlist_free_one()`, `memlist_free_list()`, `memlist_free_block()`.
- List mutation: `memlist_insert()`, `memlist_del()`.
- Lookup: `memlist_find()`.
- Span operations: `memlist_add_span()`, `memlist_delete_span()`.

Key return codes:
- `MEML_SPANOP_OK`
- `MEML_SPANOP_ESPAN`
- `MEML_SPANOP_EALLOC`

Relevance to subset A: Internal physical memory list manipulation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/memlist_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mhd.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mhd.h

Purpose: Defines multi-host device ioctl commands and structures, primarily for SCSI-3 persistent group reservations.

Key definitions:
- Ioctls: failfast, take ownership, release, status, in-keys, in-reservations, register, reserve, preempt/preempt-and-abort, clear, register-and-ignore-key, query reserve, re-register device ID.
- `mhioctkown`: ownership delay parameters.
- Reservation key/list/descriptor/list structures with 32-bit syscall variants.
- Register, preempt-and-abort, and register-and-ignore-key request structures.
- SCSI-3 reservation type and scope codes.

Important detail: 8-byte reservation keys are fixed by `MHIOC_RESV_KEY_SIZE`.

Relevance to subset A: Storage clustering/multi-host reservation ABI, directly relevant to block-storage correctness.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mhd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mii.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mii.h

Purpose: Declares the generic MII/PHY support framework for MAC drivers.

Key model:
- Drivers provide `mii_ops_t` callbacks for PHY register read/write, link notification, and optional reset.
- MII framework calls driver entry points asynchronously from a taskq and holds internal locks, so drivers must not hold their own locks across calls into MII.

Key APIs:
- Lifecycle: `mii_alloc()`, `mii_alloc_instance()`, `mii_free()`.
- Control: `mii_set_pauseable()`, `mii_reset()`, `mii_start()`, `mii_stop()`, `mii_resume()`, `mii_suspend()`, `mii_probe()`, `mii_check()`.
- Query: PHY address/id, speed, duplex, state, flow control.
- Loopback support: `mii_get_loopmodes()`, `mii_set_loopback()`, `mii_get_loopback()`, `mii_m_loop_ioctl()`.
- MAC callback helpers: `mii_m_getprop()`, `mii_m_setprop()`, `mii_m_propinfo()`, `mii_m_getstat()`.

Important details:
- Monitoring starts only after `mii_start()`.
- `mii_stop()` and `mii_suspend()` guarantee the MII layer is no longer executing driver entry points on return.
- Helper functions are designed to reduce repetitive MAC driver property/stat/ioctl code.

Relevance to subset A: Network driver support, outside filesystem focus.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mii.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/miiregs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/miiregs.h

Purpose: Defines MII register addresses, bit masks, auto-negotiation fields, 1000Base-T master/slave fields, extended status bits, and known PHY OUIs/models.

Key definitions:
- Standard register indexes: control, status, PHY IDs, auto-negotiation, master/slave, extended status, vendor space.
- Control bits: reset, loopback, speed, auto-negotiation, powerdown, isolate, restart AN, full duplex, gigabit.
- Status and ability bits for 10/100/1000 speeds, full/half duplex, pause/asymmetric pause.
- PHY ID extraction macros: `MII_PHY_MFG()`, `MII_PHY_MODEL()`, `MII_PHY_REV()`.
- Manufacturer OUI and model constants for common PHY vendors.

Important detail: This is a constants-only companion to the MII framework.

Relevance to subset A: Network PHY support, outside filesystem focus.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/miiregs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mixer.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mixer.h

Purpose: Defines audio mixer modes, default audio format settings, mixer ioctls, and variable-sized mixer control/sample-rate structures.

Key definitions:
- Modes: `AM_MIXER_MODE`, `AM_COMPAT_MODE`.
- Defaults: 8000 Hz, mono, 8-bit u-law, mid gain.
- Mixer ioctls for multiple/single open, sample rates, info, channel info, and mode get/set.
- `am_control_t`: audio device info plus variable channel-open bitmap.
- `am_sample_rates_t`: play/record type, flags, count, and variable sample-rate array.

Important detail: Macros compute variable structure sizes based on channel/sample-rate count.

Relevance to subset A: Legacy audio ABI, not filesystem-specific.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mixer.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mkdev.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mkdev.h

Purpose: Defines device major/minor bit sizes and userland device-number construction/extraction interfaces.

Key definitions:
- SVR3/pre-EFT major/minor sizes and maxima.
- 32-bit Solaris device major/minor sizes: 14/18 bits.
- 64-bit Solaris device major/minor sizes: 32/32 bits.
- Native `NBITSMAJOR`, `NBITSMINOR`, `MAXMAJ`, `MAXMIN` selected by `_LP64`.

Userland interfaces:
- `makedev()`, `major()`, `minor()` and underlying `__makedev()`, `__major()`, `__minor()`.
- Format selectors: `OLDDEV`, `NEWDEV`, `COMPATDEV`.

Important detail: In non-kernel builds it undefines possible `sysmacros.h` macros before declaring the illumos functions/macros.

Relevance to subset A: Device-number ABI used by filesystems, mount tables, device nodes, and drivers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mkdev.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mman.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mman.h

Purpose: Defines memory mapping protections, mapping flags, mmap/mprotect/msync/mlock/shm/madvise/memcntl/meminfo APIs, and mmapobj result structures.

Key definitions:
- Protections: `PROT_READ`, `PROT_WRITE`, `PROT_EXEC`, `PROT_NONE`; kernel-only `PROT_USER`, `PROT_ALL`.
- Mapping types/flags: `MAP_SHARED`, `MAP_PRIVATE`, `MAP_FIXED`, `MAP_NORESERVE`, `MAP_ANON`, `MAP_ALIGN`, `MAP_TEXT`, `MAP_INITDATA`, `_MAP_LOW32`, `_MAP_NEW`.
- mmapobj flags: `MMOBJ_PADDING`, `MMOBJ_INTERPRET`; result flags `MR_PADDING`, `MR_HDR_ELF`, kernel-only `MR_RESV`.
- `mmapobj_result_t` and 32-bit variant.
- `memcntl_mha`, `meminfo_t`, 32-bit variants.
- Advice, msync, mlockall, memcntl command, HAT advise, and meminfo request constants.

Key APIs:
- Standard: `mmap()`, `munmap()`, `mprotect()`, `msync()`.
- Large-file variants through feature-test remapping.
- Realtime/POSIX: `mlock()`, `munlock()`, `mlockall()`, `munlockall()`, `shm_open()`, `shm_unlink()`, `posix_madvise()`.
- illumos extensions: `mincore()`, `memcntl()`, `madvise()`, `getpagesizes()`, `mmapobj()`, `meminfo()`.

Important details:
- Feature-test guards are carefully documented because this header has a long compatibility history.
- `_MAP_NEW` preserves backward object compatibility for old mmap return semantics.
- `mmapobj_result_t` records both mapping size and file size so ELF/object mappings can describe padding and header placement.

Relevance to subset A: Highly relevant VM/filesystem boundary ABI because file-backed mappings, object mapping, page advice, locking, and sync behavior interact with VFS and vnode operations.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mman.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mmapobj.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mmapobj.h

Purpose: Declares kernel-side mmap object helpers.

Key definitions:
- `LIBVA_CACHED_SEGS` is 3, the number of `mmapobj_result_t` entries expected to be stack-cached for common ELF objects.

Key APIs:
- Kernel-only `mmapobj_unmap()`.
- Kernel-internal `mmapobj(vnode_t *, uint_t, mmapobj_result_t *, uint_t *, size_t, cred_t *)`.

Important detail: This header expects `mmapobj_result_t` from `sys/mman.h` and uses vnode/credential types, tying object mapping directly to VFS objects.

Relevance to subset A: Directly relevant to VFS-backed executable/object mapping.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mmapobj.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mntent.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mntent.h

Purpose: Defines mount table/vfstab path constants, filesystem type names, and mount option string constants.

Key definitions:
- Paths: `MNTTAB`, `VFSTAB`.
- Filesystem type strings: ZFS, UFS, SMBFS, NFS variants, PCFS, LOFS, HSFS, swap, tmpfs, autofs, mntfs, dev, ctfs, objfs, sharefs.
- Mount option strings: read/write mode, quotas, NFS behavior, suid/device/setuid controls, remount, lookup behavior, automount maps, locking, largefiles, direct I/O, logging, atime/deferred atime, nbmand, xattr, exec, browsing, zone, and many more.

Important detail: This header is mostly string constants shared by mount tooling and consumers, not structure definitions.

Relevance to subset A: Direct filesystem administration ABI support.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mntent.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mntio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mntio.h

Purpose: Defines private mntfs ioctl commands and request/lookup structures.

Key definitions:
- Ioctls: number of mounts, mounted device list, set/clear tag, show hidden, get mount entry, get extended mount entry, get matching mount.
- Return codes: `MNTFS_EOF`, `MNTFS_TOOLONG`.
- `MAX_MNTOPT_TAG`.

Key structures:
- `mnttagdesc` and 32-bit variant: major/minor, mount point, tag.
- `mntlookup` and 32-bit variant: mount-point offset/pointer, major/minor, inode, fstype.

Important detail: Several commands are marked private and are part of mntfs plumbing rather than a broad stable API.

Relevance to subset A: Directly relevant to in-kernel mount table filesystem behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mntio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mnttab.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mnttab.h

Purpose: Defines mount table record structures and userland parsing/query functions.

Key definitions:
- `MNTTAB`, `MNT_LINE_MAX`, and parse errors for too long/too many/too few fields.
- `mntnull()` macro and disabled `putmntent()` macro.
- `struct mnttab`: special, mount point, fstype, options, time.
- `struct extmnttab`: same initial layout plus major/minor.
- `struct mntentbuf`: extended entry pointer and backing buffer.

Key APIs outside kernel:
- `resetmnttab()`
- `getmntent()`
- `getextmntent()`
- `getmntany()`
- `hasmntopt()`
- `mntopt()`

Important detail: Comments require matching field layout across `mnttab`, `extmnttab`, `mntentbuf`, and their 32-bit kernel counterparts so code can safely cast between related record types.

Relevance to subset A: Direct mount table user/kernel ABI.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mnttab.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/modctl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/modctl.h

Purpose: Defines loadable module linkage structures, module control syscall commands, module metadata structures, kernel module loader state, and module loader/exported APIs.

Key structures:
- `mod_ops`: install/remove/info vector.
- Module linkage structs: driver, syscall, filesystem, CPU, crypto, misc, IPP, streams, scheduler, exec, DACF, PCBE, brand, socket module, kiconv.
- `modlinkage`: revision and NULL-terminated linkage array.
- `modconfig`/`modconfig32`: driver binding configuration.
- `modspecific_info`, `modinfo`, and 32-bit variants for `MODINFO`.
- Stub structures: `mod_stub_info`, `mod_modinfo`.
- `modctl_t`: persistent kernel module control record with ID, module image, linkage, names, state bits, reference count, dependencies, load count, DTrace probe count, text range, generation count.

Command surface:
- `MODLOAD`, `MODUNLOAD`, `MODINFO`, path/binding/name/device policy/minor permission/retire/hotplug operations, and event/devname/hotplug subcommands.
- `MOD_MAXPATH`, `MOD_DEFPATH`, module name/linkinfo length limits.
- `MI_INFO_*` flags and `MI_LOADED`/`MI_INSTALLED`.

Kernel APIs:
- Module load/unload/hold/release/lookup, system file parsing, driver major/name helpers, stubs install/uninstall/reset, symbol lookup, autounload state, DDI dynamic module open/sym/close.
- DDI/DKI-visible module entry points: `_init()`, `_fini()`, `_info()`, `mod_install()`, `mod_remove()`, `mod_info()`.

Important details:
- `MI_INFO_NOBASE` exists so 32-bit apps on 64-bit kernels can avoid `EOVERFLOW` from base addresses.
- `modctl_t` repeats module text range so `mod_containing_pc()` can operate without grabbing locks.
- `moddebug` bit flags expose detailed loader/autounloader behavior toggles.

Relevance to subset A: Important OS infrastructure. Filesystem modules use `modlfs`/`mod_fsops`; executable, driver, and device policy loading also affect VFS/device integration.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/modctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mode.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mode.h

Purpose: Provides kernel conversion macros between vnode types and encoded file type/mode bits used by `stat(2)` and `mknod(2)`.

Key definitions:
- External conversion tables: `iftovt_tab[]`, `vttoif_tab[]`.
- `IFTOVT(M)`: mode bits to `enum vtype`.
- `VTTOIF(T)`: vnode type to inode/stat file type bits.
- `MAKEIMODE(T, M)`: combines vnode type with permission/mode bits.

Important detail: Only visible for `_KERNEL` or `_FAKE_KERNEL`.

Relevance to subset A: Direct VFS/filesystem helper for translating vnode metadata to user-visible mode bits.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/model.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/model.h

Purpose: Defines data-model constants and helper macros for handling 32-bit vs 64-bit user data structures in the kernel.

Key definitions:
- `DATAMODEL_ILP32`, `DATAMODEL_LP64`, `DATAMODEL_NATIVE`, `DATAMODEL_MASK`, `DATAMODEL_NONE`.
- `model_t`.

Kernel LP64 helper macros:
- `STRUCT_HANDLE`, `STRUCT_DECL`, `STRUCT_SET_HANDLE`, `STRUCT_INIT`.
- `STRUCT_SIZE`, `STRUCT_FADDR`, `STRUCT_FGET`, `STRUCT_FGETP`, `STRUCT_FSET`, `STRUCT_FSETP`, `STRUCT_BUF`.
- `SIZEOF_PTR`, `SIZEOF_STRUCT`.

Data-model APIs:
- `lwp_getdatamodel()`
- `get_udatamodel()`

Important detail: On 64-bit kernels the macros create a dual 32/64 pointer view over the same logical structure; on 32-bit kernels they collapse to native-only behavior.

Relevance to subset A: Critical syscall/ioctl ABI support. Many filesystem, mount, memory, and device structs in this group have 32-bit variants that depend on this model.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/model.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/modhash.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/modhash.h

Purpose: Declares the generic kernel hash table API.

Key abstractions:
- Opaque key/value types: `mod_hash_key_t`, `mod_hash_val_t`.
- Reservation handle: `mod_hash_hndl_t`.
- Opaque hash: `mod_hash_t`.

Key APIs:
- Constructors/destructors for string, pointer, and ID hash tables.
- Extended constructor with custom key destructor, value destructor, hash algorithm, algorithm data, key comparator, and allocation flag.
- Hash lifecycle: destroy, clear.
- Null destructors.
- Operations: insert, replace, remove, destroy key, find, find with callback, walk.
- Reservation operations for preallocation and reserved insert.

Return codes:
- `MH_ERR_NOMEM`, `MH_ERR_DUPLICATE`, `MH_ERR_NOTFOUND`.
- Walker controls: continue or terminate.

Important detail: Reservation APIs allow callers to allocate outside critical paths and then insert with a reserved handle.

Relevance to subset A: Generic kernel utility; used by larger subsystems, including the MDI vHCI cache in this group.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/modhash.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/modhash_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/modhash_impl.h

Purpose: Defines internal structures and helpers for the generic kernel hash implementation.

Key structures:
- `mod_hash_entry`: key/value and chain pointer.
- `mod_hash_stat`: hit, miss, collision, element, and allocation-failure counters.
- `mod_hash`: rwlock, name, allocation behavior, chain count, destructors, comparator, hash algorithm, private algorithm data, global-list link, stats, and flexible chain array.

Key macros/APIs:
- `MH_SIZE(n)` computes allocation size for a hash with `n` chains.
- `mod_hash_init()`.
- Internal no-sync routines for hash, insert, remove, find, walk, clear.

Important detail: No-sync routines are internal and require callers to handle locking correctly.

Relevance to subset A: Generic utility internals.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/modhash_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mount.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mount.h

Purpose: Defines `mount(2)` and `umount2(2)` flags plus userland prototypes.

Key definitions:
- Mount flags: read-only, old/new mount ABI, nosuid, remount, notrunc, overlay, option string, global, forced unmount, omit mnttab.
- Kernel-internal domount flags: sysspace, nosplice, nocheck.
- `MS_CRYPT` for loading encryption keys before mount.
- `MS_MASK`, `MS_UMOUNT_MASK`.
- `MAX_MNTOPT_STR`.

Userland APIs:
- `mount()`
- `umount()`
- `umount2()`

Important detail: `MS_CRYPT` is documented as not being seen by the kernel, avoiding glibc compatibility issues.

Relevance to subset A: Direct filesystem mount ABI.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mouse.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mouse.h

Purpose: Defines AT&T 320 / PS/2-style mouse command and response byte constants.

Key definitions:
- Commands: reset, resend, set defaults, disable/enable, set sampling/button mode, get device type, prompt/echo/stream/report/status/resolution/scaling commands.
- Response/status bytes: `MSE_ACK`, post-reset `MSE_AA`, `MSE_00`.

Relevance to subset A: Legacy device ABI, not filesystem-related.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mouse.h -->