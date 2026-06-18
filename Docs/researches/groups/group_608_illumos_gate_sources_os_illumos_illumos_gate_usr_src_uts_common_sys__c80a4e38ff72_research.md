# Group Research: group_608_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__c80a4e38ff72

Scope checked against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pcifm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pcifm.h

## Purpose
Defines PCI/PCI-X fault-management data structures used to gather, preserve, and post PCI error-register state for ereports.

## Main Interfaces
- Device flags: `PCI_BRIDGE_DEV`, `PCIX_DEV`.
- Valid-bit masks for PCI status, bridge status/control, PCI-X status, ECC status, and PCI-X bridge status.
- Error register structures:
  - `pci_bdg_error_regs_t`
  - `pci_error_regs_t`
  - `pci_erpt_t`
  - `pcix_ecc_regs_t`
  - `pcix_error_regs_t`
  - `pcix_bdg_error_regs_t`
- Bus-specific and target-error structures:
  - `pci_fme_bus_specific_t`
  - `pci_target_err_t`
- `PCI_FM_SEV_INC(x)`: macro that increments severity counters based on `DDI_FM_*` status.

## Dependencies And Relationships
Includes `sys/dditypes.h` for `ddi_acc_handle_t` and uses `dev_info_t` plus DDI fault-management severity constants. It is consumed by PCI error-report setup/post/teardown paths.

## Research Notes
The structures are containers for snapshots of config-space and PCI-X ECC state. Valid flags are important because not every device or bridge exposes every register.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pcifm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pcmcia.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pcmcia.h

## Purpose
Defines private PCMCIA nexus, adapter-driver, card-services, socket/window, device-node, resource, property, and regspec interfaces.

## Main Interfaces
- Capacity constants for adapters, sockets, windows, and power entries.
- Nexus names and node type strings:
  - `PCMCIA_NEXUS_NAME`
  - `PCMCIA_ADAPTER_NODE`
  - `PCMCIA_SOCKET_NODE`
  - `PCMCIA_PCCARD_NODE`
- Adapter/Card Services ops:
  - `pcmcia_if_t`
  - `pcmcia_cs_t`
  - call-through macros such as `GET_ADAPTER`, `GET_SOCKET`, `SET_WINDOW`, `SET_IRQ`, `CLEAR_IRQ`.
- Nexus private state:
  - `pcmcia_adapter_nexus_private`
  - `pcm_regs`
  - `inthandler_t`
  - `pcmcia_parent_private`
  - `pcmcia_adapter`
  - `pcmcia_logical_window_t`
  - `pcmcia_mif`
- Socket/resource helpers:
  - `socket_enum_t`
  - `PR_GET`, `PR_SET`, `PR_CLEAR`, `PR_ZERO`
  - `PR_MAX_IO_LEN`, `PR_MAX_MEM_LEN`, range/count constants.
- Device matching and node construction:
  - `pcm_device_info`
  - `pcm_dev_node_t`
  - `init_dev_t`
  - `str_int_t`
  - device class, function, manufacturer, VERSION_1, JEDEC, naming, and no-CIS flags.
- 1275-style regspec helpers:
  - `PC_REG_*`
  - `PC_GET_REG_*`
  - `PC_INCR_REFCNT`
  - `PC_DECR_REFCNT`
  - `PC_REG_PHYS_HI`
- Property identifiers such as `PCMCIA_PROP_SOCKET`, `PCMCIA_PROP_REG`, and `PCMCIA_PROP_INTR`.

## Dependencies And Relationships
Includes `sys/modctl.h` and uses DDI types, `dev_info_t`, `dev_ops`, interrupt cookies, soft interrupts, kernel mutexes, and Card Services concepts. It is the common contract between the PCMCIA nexus, adapter-specific drivers, and card services.

## Research Notes
This is a broad private compatibility header. Several macros encode 1275-compatible `reg` properties and also carry Solaris-private reference counts in the same physical-high word.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pcmcia.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pctypes.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pctypes.h

## Purpose
Defines shared PCMCIA primitive types and little-endian conversion helpers.

## Main Interfaces
- `irq_t`: IRQ level type.
- `baseaddr_t`: memory base address pointer type.
- `ioaddr_t`: `uint32_t` on x86, `caddr_t` on SPARC.
- `intrfunc_t`: interrupt callback signature returning `uint32_t`.
- `acc_handle_t`: opaque data access handle.
- `leshort()` and `lelong()`: byte-swap on big-endian systems, identity on little-endian systems.

## Dependencies And Relationships
Depends on base illumos integer/address types being available. Used by PCMCIA and related adapter code that needs architecture-neutral I/O address and endian handling.

## Research Notes
The endian helpers are macro-only and assume their arguments are integer values. `ioaddr_t` intentionally differs between x86 and SPARC.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pctypes.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pfmod.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pfmod.h

## Purpose
Defines the STREAMS packet-filter module ioctl ABI and the encoded packet-filter instruction language.

## Main Interfaces
- `PFIOCSETF`: ioctl to replace the current packet filter.
- Filter sizes:
  - `ENMAXFILTERS`
  - `PF_MAXFILTERS`
- Filter structures:
  - `struct packetfilt`
  - `struct Pf_ext_packetfilt`
- Instruction encoding:
  - action/operator bit split: `ENF_NBPA`, `ENF_NBPO`
  - operators: `ENF_EQ`, `ENF_LT`, `ENF_GE`, `ENF_AND`, `ENF_OR`, `ENF_XOR`, `ENF_NEQ`, and conditional variants.
  - actions: `ENF_PUSHLIT`, `ENF_PUSHZERO`, `ENF_LOAD_OFFSET`, `ENF_BRTR`, `ENF_BRFL`, `ENF_POP`, `ENF_PUSHWORD`.

## Dependencies And Relationships
Used by consumers that install packet filters on open Ethernet/packet streams. The filter executes as a stack machine over 16-bit words and accepts packets when the final stack value is true.

## Research Notes
The extended structure increases filter length from 255 to 2047 short words. The comments document the virtual machine semantics and ownership rules for the filter command list.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pfmod.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pg.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pg.h

## Purpose
Defines the kernel processor-group framework for grouping CPUs by logical or physical relationships and dispatching CPU/thread events to group classes.

## Main Interfaces
- Types:
  - `pgid_t`
  - `pg_cid_t`
  - `pg_relation_t`
  - `pg_cb_ops_t`
  - `pg_t`
  - `struct pg_ops`
  - `pg_class_t`
  - `cpu_pg_t`
  - `pg_cpu_itr_t`
- CPU iteration helpers:
  - `PG_CPU_ITR_INIT`
  - `PG_CPU_GET_FIRST`
  - `PG_NUM_CPUS`
- Framework routines:
  - `pg_init()`
  - `pg_class_register()`
- CPU lifecycle hooks:
  - `pg_cpu0_init()`
  - `pg_cpu_init()`
  - `pg_cpu_fini()`
  - `pg_cpu_active()`
  - `pg_cpu_inactive()`
  - `pg_cpu_startup()`
  - `pg_cpu_bootstrap()`
- CPU partition and group manipulation:
  - `pg_cpupart_in()`
  - `pg_cpupart_out()`
  - `pg_cpupart_move()`
  - `pg_create()`
  - `pg_destroy()`
  - `pg_cpu_add()`
  - `pg_cpu_delete()`
  - `pg_cpu_find_pg()`
  - `pg_cpu_next()`
  - `pg_cpu_find()`
- Event/observability:
  - `pg_callback_set_defaults()`
  - `pg_ev_thread_swtch()`
  - `pg_ev_thread_remain()`
  - `pg_policy_name()`

## Dependencies And Relationships
Visible for `_KERNEL` and `_KMEMUSER`. Includes CPU, group, processor, bitset, atomic, types, and kstat headers. Physical processor groups are extended by `pghw.h`.

## Research Notes
The framework separates processor group class registration from concrete CPU membership. Callback vectors let scheduling and observability code react to thread switch/remain events.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pghw.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pghw.h

## Purpose
Defines hardware-backed processor groups that represent shared CPU resources such as caches, memory pipes, chips, memory domains, and power-management domains.

## Main Interfaces
- `pghw_type_t`: hardware sharing types including instruction pipeline, cache, FPU, memory pipe, chip, memory, active power domain, and idle power domain.
- `PGHW_PROCNODE`: aliases processor nodes to memory-pipe-style sharing.
- `PGHW_IS_PM_DOMAIN(hw)`: tests power-management domain types.
- `PGHW_INSTANCE_ANON`: anonymous instance sentinel.
- `pghw_handle_t`: platform-specific opaque handle.
- `pghw_util_t`: capacity/utilization counters and timestamps.
- `pghw_t`: embeds `pg_t` and adds hardware type, instance, kstats, generation, CPU list, and utilization state.
- `cpu_physid_t`: chip/core/cache identifiers for a CPU.
- Lifecycle and lookup routines:
  - `pghw_init()`, `pghw_fini()`, `pghw_cpu_add()`, `pghw_place_cpu()`, `pghw_cmt_fini()`
  - `pghw_physid_create()`, `pghw_physid_destroy()`
  - `pghw_find_pg()`, `pghw_find_by_instance()`, `pghw_set_lookup()`
- Platform hooks:
  - `pg_plat_hw_shared()`
  - `pg_plat_cpus_share()`
  - `pg_plat_hw_instance_id()`
  - `pg_plat_hw_rank()`
  - `pg_plat_get_core_id()`
- `pghw_type_string()`: string representation for hardware type.

## Dependencies And Relationships
Extends `pg.h` and includes CPU, group, processor, bitmap, atomic, types, and kstat support. Platform-specific CPU topology code supplies the sharing and ranking hooks.

## Research Notes
The header explicitly avoids a `PGHW_CORE` type because “core” varies by platform. Capacity/utilization kstats depend on generation tracking and a cached CPU list.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pghw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/physmem.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/physmem.h

## Purpose
Defines ioctl command numbers and argument structures for a physical-memory mapping/allocation interface.

## Main Interfaces
- Ioctls:
  - `PHYSMEM_SETUP`
  - `PHYSMEM_MAP`
  - `PHYSMEM_DESTROY`
- Mapping flags:
  - `PHYSMEM_CAGE`
  - `PHYSMEM_RETIRED`
- `struct physmem_setup_param`: requested physical address, length, user VA, and returned destroy cookie.
- `struct physmem_map_param`: requested physical address, returned VA, and flags.

## Dependencies And Relationships
Uses fixed-width integer types. Consumers pass these structures through the corresponding driver ioctl interface.

## Research Notes
The interface distinguishes setup/destroy lifecycle from mapping. Flags allow callers to request caged or retired-page behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/physmem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pkp_hash.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pkp_hash.h

## Purpose
Declares a Pearson-style string hash used by kernel code.

## Main Interfaces
- `PKP_HASH_SIZE`: hash table size of 256.
- `pkp_tab_hash(char *, int)`: computes a hash over a character buffer and length.

## Dependencies And Relationships
Includes `sys/types.h`. The comment references Pearson’s string hash algorithm from CACM.

## Research Notes
This is a small declaration header; the hash table or algorithm implementation lives elsewhere.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pkp_hash.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/plat/pci_prd.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/plat/pci_prd.h

## Purpose
Defines the platform PCI Resource Discovery interface used by generic PCI enumeration to discover platform-specific root complexes, resource windows, slot names, and compatibility behavior.

## Main Interfaces
- `pci_prd_rsrc_t`: resource types for I/O ports, MMIO, prefetchable memory, and PCI buses.
- `pci_prd_upcalls_t`: upcall table, currently `pru_bus2dip_f`.
- Lifecycle:
  - `pci_prd_init()`
  - `pci_prd_fini()`
- Discovery:
  - `pci_prd_max_bus()`
  - `pci_prd_find_resource()`
  - `pci_prd_multi_root_ok()`
  - `pci_prd_root_complex_iter()`
  - `pci_prd_slot_name()`
- Compatibility:
  - `pci_prd_compat_flags_t`
  - `PCI_PRD_COMPAT_NONE`
  - `PCI_PRD_COMPAT_ISA`
  - `PCI_PRD_COMPAT_PCI_NODE_NAME`
  - `PCI_PRD_COMPAT_SUBSYS`
  - `pci_prd_compat_flags()`

## Dependencies And Relationships
Includes `sys/types.h`, `sys/memlist.h`, and `sys/sunddi.h`. The comments state that platform modules named `pci_prd` implement these functions and may depend on platform mechanisms such as ACPI.

## Research Notes
Interfaces are generally called from kernel context during boot, single-threaded by the caller. Resource discovery primarily fills gaps not visible through ordinary PCI scanning.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/plat/pci_prd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pm.h

## Purpose
Defines the user/kernel power-management ioctl command set, request payloads, state-change notifications, and 32-bit structure mirrors.

## Main Interfaces
- `pm_cmds`: power-management commands, including many obsolete commands plus current component threshold, current/full power, dependency, CPU power management, S3/autos3, and CPU deep-idle controls.
- Compatibility aliases:
  - `PM_GET_POWER`
  - `PM_SET_POWER`
- Request structures:
  - obsolete `pm_request`
  - `pm_req_t`
  - `pm_searchargs_t`
- Dependency aliases:
  - `pmreq_keeper`
  - `pmreq_kept`
- State-change interface:
  - `psc_events`
  - `PSC_EVENT_LOST`
  - `PSC_ALL_LOWEST`
  - `PM_LEVEL_UNKNOWN`
  - `pm_state_change_t`
- 32-bit kernel views:
  - `pm_request32`
  - `pm_req32_t`
  - `pm_state_change32_t`
  - `pm_searchargs32_t`
- `pm_states`: return values describing PM enabled/disabled, thresholds, direct management, CPU PM, autos3, and S3 support states.

## Dependencies And Relationships
Includes `sys/types.h`. The header is a public ioctl ABI consumed by PM tools and handled by kernel PM code.

## Research Notes
Several commands and structures are explicitly documented as obsolete or test-only. `pm_state_change_t` orders `event` and `flags` differently by endianness to preserve layout semantics.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/policy.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/policy.h

## Purpose
Declares kernel security policy and privilege-check routines used across filesystems, networking, process control, zones, devices, ZFS, auditing, and resource management.

## Main Interfaces
- Generic policy checks:
  - `priv_policy()`
  - `priv_policy_only()`
  - `priv_policy_choice()`
  - `PRIV_POLICY`
  - `PRIV_POLICY_CHOICE`
  - `PRIV_POLICY_ONLY`
- Large family of `secpolicy_*()` checks for:
  - auditing, clock, contracts, coreadm, CPC, error injection, modctl, kmdb
  - filesystem mount/unmount/quota/linkdir/minfree and vnode access/setattr/chown/setid/sticky policies
  - IPC, NFS, PPP, SMB/SMBFS, RPC module open
  - networking, raw access, privileged ports, MAC awareness/implicit policies, observability
  - process access, owner checks, zones, processor binding/sets/online, priority, resource controls
  - power management, pools, tasks, devices, system info/configuration, ZFS, `zinject`, ucode updates
- `secpolicy_vnode_setattr()`: combined vnode setattr policy helper that may alter `va_mask`.
- `in_port_t` definition guard for kernel use.

## Dependencies And Relationships
Kernel-only declarations guarded by `_KERNEL`. Includes credentials, vnodes, and snode support; forward-declares several subsystem types. It centralizes policy entry points used by many kernel modules.

## Research Notes
The three generic privilege helpers differ in auditing/debugging behavior. Callers must choose the variant appropriate for normal, choice-style, or interrupt-context checks.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/policy.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/poll.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/poll.h

## Purpose
Defines the public `poll(2)` file-descriptor event ABI and kernel pollhead notification interface.

## Main Interfaces
- `pollfd_t`: fd, requested events, returned events.
- `nfds_t`: number-of-fds type.
- Public event bits:
  - `POLLIN`, `POLLPRI`, `POLLOUT`
  - `POLLRDNORM`, `POLLWRNORM`, `POLLRDBAND`, `POLLWRBAND`
  - `POLLRDHUP`, `POLLNORM`
  - `POLLERR`, `POLLHUP`, `POLLNVAL`
  - `/dev/poll` controls: `POLLREMOVE`, `POLLONESHOT`, `POLLET`
- Kernel-only flags:
  - `POLLRDDATA`
  - `POLLNOERR`
  - `POLLCLOSED`
- Kernel poll interface:
  - `pollhead_t`
  - `pollwakeup()`
  - `polllock()`
  - `pollunlock()`
  - `pollrelock()`
  - `pollcleanup()`
  - `pollblockexit()`
  - `pollcacheclean()`
  - `pollhead_clean()`
- User prototype:
  - `poll(struct pollfd *, nfds_t, int)`

## Dependencies And Relationships
Kernel and kmem-user paths include `sys/thread.h` and expose pollhead state. `poll_impl.h` contains the private caching implementation.

## Research Notes
`pollhead_t` keeps unused padding for DDI size compatibility; only `ph_list` is semantically used.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/poll.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/poll_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/poll_impl.h

## Purpose
Defines private caching-poll subsystem structures and routines used by `poll(2)`, `/dev/poll`, event ports, and recursive poll/epoll-style operations.

## Main Interfaces
- Core types:
  - `pollcache_t`
  - `pollstate_t`
  - `pcachelink_t`
  - `polldat_t`
  - `pollcacheset_t`
  - `xref_t`
- Cache sizing and hash constants:
  - `POLLFDSETS`
  - `POLLMAXDEPTH`
  - `POLLCHUNKSHIFT`
  - `POLLHASHCHUNKSZ`
  - `POLLHASHINC`
  - `POLLHASHTHRESHOLD`
  - `POLLHASH`
  - `POLLMAPCHUNK`
- Poll state flags/results:
  - `POLLSTATE_STALEMATE`
  - `POLLSTATE_ULFAIL`
  - `PSE_SUCCESS`
  - `PSE_FAIL_DEPTH`
  - `PSE_FAIL_LOOP`
  - `PSE_FAIL_DEADLOCK`
  - `PSE_FAIL_POLLSTATE`
- Cross-reference sentinels:
  - `POLLPOSINVAL`
  - `POLLPOSTRANS`
- Recursive cache link states:
  - `PCL_INIT`, `PCL_VALID`, `PCL_STALE`, `PCL_INVALID`, `PCL_FREE`
- Pollcache flags:
  - `PC_POLLWAKE`
  - `PC_EPOLL`
  - `PC_PORTFS`
- Internal routines:
  - `pollnotify()`
  - `pollhead_clean()`
  - `polldat_associate()`, `polldat_disassociate()`
  - `pollstate_create()`, `pollstate_destroy()`, `pollstate_enter()`, `pollstate_exit()`
  - `pcache_alloc()`, `pcache_create()`, `pcache_insert()`, `pcache_poll()`, `pcache_clean()`, `pcache_destroy()`
  - `pcache_lookup_fd()`, `pcache_alloc_fd()`, `pcache_insert_fd()`, `pcache_delete_fd()`, `pcache_grow_hashtbl()`, `pcache_grow_map()`, `pcache_update_xref()`, `pcache_clean_entry()`, `pcache_wake_parents()`
  - `pcacheset_create()`, `pcacheset_destroy()`, `pcacheset_cache_list()`, `pcacheset_remove_list()`, `pcacheset_resolve()`, `pcacheset_cmp()`, `pcacheset_invalidate()`, `pcacheset_reset_count()`, `pcacheset_replace()`

## Dependencies And Relationships
Includes `sys/poll.h`, `sys/thread.h`, `sys/file.h`, and `sys/port_kernel.h`. Event ports intentionally present a `port_fdcache_t` through `t_pollcache`, requiring matching lock/flag offsets with `pollcache_t`.

## Research Notes
The header documents the caching design in detail: per-thread `pollstate_t`, reusable `pollcache_t`, fd bitmaps, polldat hash tables, cached user pollfd sets, and parent/child cache links for recursive polling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/poll_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pool.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pool.h

## Purpose
Defines the kernel pool framework interface for resource pools, pool IDs, pool state, process binding, configuration, synchronization, and change callbacks.

## Main Interfaces
- Constants:
  - `POOL_DEFAULT`
  - `POOL_MAXID`
  - `POOL_INVALID`
  - `POOL_DISABLED`
  - `POOL_ENABLED`
- Kernel pool structure:
  - `pool_t`: pool ID, process reference count, list linkage, properties, and associated processor set.
- Binding/class constants:
  - `POOL_BIND_PSET`
  - `POOL_BIND_ALL`
  - `POOL_CLASS_UNSET`
  - `POOL_CLASS_INVAL`
- Global kernel state:
  - `pool_count`
  - `pool_default`
  - `pool_state`
  - `pool_buf`
  - `pool_bufsz`
- Lookup:
  - `pool_lookup_pool_by_id()`
  - `pool_lookup_pool_by_name()`
  - `pool_lookup_pool_by_pset()`
- Configuration/binding:
  - `pool_init()`, `pool_status()`, `pool_create()`, `pool_destroy()`
  - `pool_transfer()`, `pool_xtransfer()`
  - `pool_assoc()`, `pool_dissoc()`
  - `pool_bind()`, `pool_do_bind()`, `pool_query_binding()`
  - `pool_get_class()`
  - `pool_pack_conf()`
  - `pool_propput()`, `pool_proprm()`, `pool_propget()`
  - `pool_commit()`, `pool_get_name()`
- Synchronization:
  - `pool_lock()`, `pool_lock_intr()`, `pool_lock_held()`, `pool_unlock()`
  - `pool_barrier_enter()`, `pool_barrier_exit()`
- Change notifications:
  - `pool_event_t`
  - `pool_event_cb_t`
  - `pool_event_cb_register()`
  - `pool_event_cb_unregister()`

## Dependencies And Relationships
Includes types, time, nvpair, procset, and list headers. `pool_pset.h` defines the processor-set backing resource used by pools.

## Research Notes
The state comments appear inverted for `POOL_DISABLED`/`POOL_ENABLED`, but the constants are clearly named. Pool callbacks notify enable, disable, and change events.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pool.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pool_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pool_impl.h

## Purpose
Defines private pools driver ioctl commands, exacct catalog IDs, object classes, ioctl payload structures, property metadata, and 32-bit compatibility layouts.

## Main Interfaces
- Ioctl command codes:
  - `POOL_STATUS`, `POOL_STATUSQ`, `POOL_CREATE`, `POOL_DESTROY`, `POOL_QUERY`
  - `POOL_ASSOC`, `POOL_DISSOC`, `POOL_TRANSFER`, `POOL_XTRANSFER`
  - `POOL_PROPGET`, `POOL_PROPPUT`, `POOL_PROPRM`
  - `POOL_BIND`, `POOL_BINDQ`, `POOL_COMMIT`
- Exacct catalog IDs for system, pool, pset, and CPU groups/properties/timestamps.
- Element classes:
  - `pool_elem_class_t`
  - `pool_resource_elem_class_t`
  - `pool_component_elem_class_t`
- Buffer sizing constants:
  - `POOL_IDLIST_SIZE`
  - `POOL_PROPNAME_SIZE`
  - `POOL_PROPBUF_SIZE`
- Ioctl payloads:
  - `pool_status_t`, `pool_create_t`, `pool_destroy_t`, `pool_query_t`
  - `pool_assoc_t`, `pool_dissoc_t`
  - `pool_transfer_t`, `pool_xtransfer_t`
  - `pool_propget_t`, `pool_propgetall_t`
  - `pool_propput_t`, `pool_proprm_t`
  - `pool_bind_t`, `pool_bindq_t`
- 32-bit variants for pointer-bearing payloads.
- Property flags:
  - `PP_READ`, `PP_WRITE`, `PP_RDWR`, `PP_OPTIONAL`, `PP_STORED`, `PP_INIT`, `PP_HIDDEN`
- Kernel property helpers:
  - `pool_property_t`
  - `pool_propput_common()`
  - `pool_proprm_common()`

## Dependencies And Relationships
Includes CPU partition, exacct catalog, and nvpair support. This is lower-level than `pool.h` and represents the devpool ioctl ABI.

## Research Notes
The header uses packing around `pool_transfer_t` on ABIs where 64-bit alignment differs between native and 32-bit callers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pool_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pool_pset.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pool_pset.h

## Purpose
Defines the kernel processor-set resource component used by pools, including pset properties, CPU properties, binding, transfer, packing, and zone visibility hooks.

## Main Interfaces
- `pool_pset_t`: pset ID, pool membership count, list link, and nvlist properties.
- Global state:
  - `pool_pset_default`
  - `pool_pset_mod`
  - `pool_cpu_mod`
- Lifecycle/configuration:
  - `pool_pset_init()`
  - `pool_pset_enable()`
  - `pool_pset_disable()`
  - `pool_pset_create()`
  - `pool_pset_destroy()`
  - `pool_pset_assoc()`
- Binding/transfer:
  - `pool_pset_bind()`
  - `pool_pset_xtransfer()`
  - `pset_bind_start()`
  - `pset_bind_abort()`
  - `pset_bind_finish()`
- Property operations:
  - `pool_pset_proprm()`, `pool_pset_propput()`, `pool_pset_propget()`
  - `pool_cpu_proprm()`, `pool_cpu_propput()`, `pool_cpu_propget()`
- Serialization/state:
  - `pool_pset_pack()`
  - `pool_pset_enabled()`
- Zone visibility:
  - `pool_pset_visibility_add()`
  - `pool_pset_visibility_remove()`

## Dependencies And Relationships
Kernel-only. Includes CPU partition, procset, nvpair, exacct, time, and list support. Integrates with `pool.h` and zone visibility.

## Research Notes
Modification timestamps distinguish pset changes from CPU changes, which matters for pool configuration snapshots.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pool_pset.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/port.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/port.h

## Purpose
Defines the public event-port ABI: event sources, event records, notification records, file event objects, alert flags, and file-watch event masks.

## Main Interfaces
- Event sources:
  - `PORT_SOURCE_AIO`
  - `PORT_SOURCE_TIMER`
  - `PORT_SOURCE_USER`
  - `PORT_SOURCE_FD`
  - `PORT_SOURCE_ALERT`
  - `PORT_SOURCE_MQ`
  - `PORT_SOURCE_FILE`
- Structures:
  - `port_event_t`
  - `port_notify_t`
  - `file_obj_t`
- 32-bit variants under `_SYSCALL32`:
  - `file_obj32_t`
  - `port_event32_t`
  - `port_notify32_t`
- Alert flags:
  - `PORT_ALERT_SET`
  - `PORT_ALERT_UPDATE`
  - `PORT_ALERT_INVALID`
- File watch events:
  - `FILE_ACCESS`
  - `FILE_MODIFIED`
  - `FILE_ATTRIB`
  - `FILE_TRUNC`
  - `FILE_NOFOLLOW`
- File exception events:
  - `FILE_DELETE`
  - `FILE_RENAME_TO`
  - `FILE_RENAME_FROM`
  - `UNMOUNTED`
  - `MOUNTEDOVER`

## Dependencies And Relationships
Includes `sys/types.h`. Private kernel implementation details are split into `port_kernel.h` and `port_impl.h`.

## Research Notes
`port_event_t` is source-polymorphic: object and event meanings depend on `portev_source`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/port.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/port_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/port_impl.h

## Purpose
Defines private event-port implementation structures for system call dispatch, port queues, alert state, fd associations, file-object watches, VFS/vnode watch state, and file event masks.

## Main Interfaces
- Port syscall codes:
  - `PORT_CREATE`, `PORT_ASSOCIATE`, `PORT_DISSOCIATE`, `PORT_SEND`, `PORT_SENDN`, `PORT_GET`, `PORT_GETN`, `PORT_ALERT`, `PORT_DISPATCH`
  - `PORT_SYS_NOPORT`, `PORT_SYS_NOSHARE`, `PORT_CODE_MASK`
- Limits and flags:
  - `PORT_SHARE_EVENT`
  - `PORT_MAX_LIST`
  - `PORT_SCACHE_SIZE`
  - `PORT_SHASH`
  - `PORT_CLEANUP_DONE`, `PORT_KEV_CACHE`, `PORT_KEV_WIRED`
  - `PORT_FREE_EVENT`
- Kernel structures:
  - `port_alert_t`
  - `port_queue_t`
  - `port_t`
  - `port_control_t`
  - `portget_t`
  - `port_gettimer_t`
  - `portfd_t`
  - `portfop_t`
  - `portfop_vfs_t`
  - `portfop_vfs_hash_t`
  - `portfop_vp_t`
  - `port_kstat_t`
- Queue and port flags:
  - `PORTQ_ALERT`, `PORTQ_CLOSE`, `PORTQ_WAIT_EVENTS`, `PORTQ_POLLIN`, `PORTQ_POLLOUT`, `PORTQ_BLOCKED`, `PORTQ_POLLWK_PEND`
  - `PORT_INIT`, `PORT_CLOSED`, `PORT_EVENTS`
  - `PORTGET_ALERT`
- File-operation event flags and masks:
  - `FOP_FILE_*`
  - `FOP_MODIFIED_MASK`
  - `FOP_ACCESS_MASK`
  - `FOP_ATTRIB_MASK`
  - `FOP_TRUNC_MASK`
  - `FILE_EVENTS_MASK`
- Internal functions:
  - `port_alloc_event_block()`
  - `port_push_eventq()`
  - `port_remove_done_event()`
  - `port_get_kevent()`
  - `port_block()`, `port_unblock()`
  - `port_pcache_remove_fd()`
  - `port_remove_fd_object()`
  - `addfd_port()`, `delfd_port()`

## Dependencies And Relationships
Includes `poll_impl.h`, `port.h`, `port_kernel.h`, vnode, and FEM support. It builds on poll caching for fd events and uses vnode/FEM hooks for file event notification.

## Research Notes
The header is explicitly private and changeable. File watch state has distinct locks: vnode list state is protected by `pvp_mutex`, while most `portfop_t` fields are protected by the source-cache lock.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/port_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/port_kernel.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/port_kernel.h

## Purpose
Defines kernel-private event-port event/source/cache structures and kernel APIs for associating sources, fd/file objects, sending events, and managing event memory.

## Main Interfaces
- `port_kevent_t`: kernel internal event object, including source, events, flags, pid, object, user cookie, callback, source arg, owning port, and list node.
- Event flags:
  - `PORT_KEV_PRIVATE`
  - `PORT_KEV_CACHED`
  - `PORT_KEV_SCACHED`
  - `PORT_KEV_VALID`
  - `PORT_KEV_DONEQ`
  - `PORT_KEV_FREE`
  - `PORT_KEV_NOSHARE`
- Allocation/callback flags:
  - `PORT_ALLOC_DEFAULT`, `PORT_ALLOC_PRIVATE`, `PORT_ALLOC_CACHED`, `PORT_ALLOC_SCACHED`
  - `PORT_CALLBACK_DEFAULT`, `PORT_CALLBACK_CLOSE`, `PORT_CALLBACK_DISSOCIATE`
- Limits:
  - `PORT_DEFAULT_PORTS`
  - `PORT_MAX_PORTS`
  - `PORT_DEFAULT_EVENTS`
  - `PORT_MAX_EVENTS`
- Source/cache types:
  - `port_source_t`
  - `portfop_cache_t`
  - `port_fdcache_t`
  - `port_ksource_t`
- Kernel APIs:
  - `port_associate_ksource()`
  - `port_dissociate_ksource()`
  - `port_alloc_event()`
  - `port_pollwkup()`
  - `port_pollwkdone()`
  - `port_send_event()`
  - `port_free_event()`
  - `port_init_event()`
  - `port_dup_event()`
  - `port_associate_fd()`
  - `port_dissociate_fd()`
  - `port_associate_fop()`
  - `port_dissociate_fop()`
  - `port_free_event_local()`
  - `port_alloc_event_local()`
  - `port_close_pfd()`

## Dependencies And Relationships
Kernel-only. Includes vnode and list support. `port_fdcache_t` deliberately matches `pollcache_t` field offsets for `pc_lock` and `pc_flag`.

## Research Notes
This header is the kernel API for non-user event sources to interact with event ports. `port_ksource_tab` support lets kernel subsystems associate at port creation time to avoid repeated runtime checks.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/port_kernel.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/portif.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/portif.h

## Purpose
Defines the SCSI Target Mode Framework local-port/provider interface, including data-buffer stores, local/remote ports, sessions, provider callbacks, and registration APIs.

## Main Interfaces
- `stmf_dbuf_store_t`: data-buffer allocation/free/setup/teardown callbacks.
- `PORTIF_REV_1`: current port interface revision.
- `stmf_local_port_t`: local port identity, alias, provider, data-buffer store, abort timeout, and operations for transfer, status, task free, abort, polling, control, info, and events.
- `stmf_remote_port_t`: remote transport ID and size.
- `stmf_dflt_scsi_tptid_t`: default SCSI transport ID layout with endian-dependent bitfields.
- `STMF_LPORT_ABORT_TASK`: abort command.
- `stmf_port_provider_t`: provider metadata and callback.
- `STMF_SESSION_ID_NONE`
- `stmf_scsi_session_t`: session identity, local/remote ports, alias, and session ID.
- Registration/control:
  - `stmf_register_port_provider()`
  - `stmf_deregister_port_provider()`
  - `stmf_register_local_port()`
  - `stmf_deregister_local_port()`
  - `stmf_register_scsi_session()`
  - `stmf_add_rport_info()`
  - `stmf_remove_rport_info()`
  - `stmf_deregister_scsi_session()`
  - `stmf_set_port_standby()`
  - `stmf_set_port_alua()`

## Dependencies And Relationships
Includes `sys/stmf_defines.h` and references STMF data buffers, tasks, status codes, SCSI device descriptors, and transport IDs. `pppt_ic_if.h` uses STMF session and remote-port types for proxy/interconnect messages.

## Research Notes
The interface splits STMF-private and provider/private storage on buffers, ports, providers, and sessions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/portif.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ppmio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ppmio.h

## Purpose
Defines platform power-management driver ioctl commands and user/kernel payload structures for querying and controlling power domains and device/domain mappings.

## Main Interfaces
- Ioctls:
  - `PPMIOCSET`
  - `PPMIOCGET`
  - `PPMGET_DPWR`
  - `PPMGET_DOMBYDEV`
  - `PPMGET_DEVBYDOM`
  - x86 test-only `PPMGET_NORMAL`, `PPMSET_NORMAL`
- Payloads:
  - `ppmreq_t`
  - `struct ppm_dpwr`
  - `struct ppm_bydev`
  - `struct ppm_bydom`
  - `struct ppm_norm`
- 32-bit variants:
  - `ppm_dpwr32`
  - `ppm_bydev32`
  - `ppm_bydom32`
  - `ppm_norm32`
- Power/LED values:
  - `PPMIO_POWER_OFF`
  - `PPMIO_POWER_ON`
  - `PPMIO_LED_BLINKING`
  - `PPMIO_LED_SOLIDON`
  - compatibility aliases `PPM_IDEV_POWER_OFF`, `PPM_IDEV_POWER_ON`

## Dependencies And Relationships
Includes `sys/types.h`. Consumed by PPM driver ioctl paths; `ppmvar.h` defines the driver-private domain/control structures.

## Research Notes
Some ioctls are documented as legacy or test-only. Pointer-bearing structures have explicit ILP32 kernel views.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ppmio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ppmvar.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ppmvar.h

## Purpose
Defines private platform power-management driver state for devices, domains, control methods, configuration database entries, locks, debug flags, and common driver hooks.

## Main Interfaces
- Driver/unit state:
  - `ppm_unit_t`
  - `PPM_STATE_SUSPENDED`
- Domain helpers and LED timing:
  - `PPM_DOMAIN_UP`
  - `PPM_LED_PULSE`, `PPM_LEDON_INTERVAL`, `PPM_LEDOFF_INTERVAL`
  - `PPM_LEDON`, `PPM_LEDOFF`
- Configuration/device/domain types:
  - `ppm_db_t`
  - `ppm_cdata`
  - `ppm_dev_t`
  - `ppm_owned_t`
  - `ppm_dc_t`
  - `ppm_domain_t`
  - `ppm_domit`
  - `ppm_funcs`
- Device flags:
  - `PPMDEV_PCI66_D2`
  - `PPMDEV_PCI_PROP_CLKPM`
  - `PPM_PM_POWEROP`
  - `PPM_PHC_WHILE_SET_POWER`
- Domain-control commands:
  - `PPMDC_CPU_NEXT`, `PPMDC_PRE_CHNG`, `PPMDC_CPU_GO`, `PPMDC_POST_CHNG`
  - `PPMDC_FET_ON`, `PPMDC_FET_OFF`, `PPMDC_LED_ON`, `PPMDC_LED_OFF`
  - clock, pre/post power, reset, and S3 enter/exit commands.
- Control methods:
  - `PPMDC_KIO`
  - `PPMDC_CPUSPEEDKIO`
  - `PPMDC_VCORE`
  - SPARC-only `PPMDC_I2CKIO`
- Domain models and flags:
  - `PPMD_CPU`, `PPMD_FET`, `PPMD_LED`, `PPMD_PCI`, `PPMD_PCI_PROP`, `PPMD_PCIE`, `PPMD_SX`
  - `PPMD_IS_PCI`
  - `PPMD_OFF`, `PPMD_ON`
  - `PPMD_LOCK_ONE`, `PPMD_LOCK_ALL`, PCI speed/init/offline/CPU-ready flags.
- Global state and hooks:
  - `ppm_domain_p`, `ppm_statep`, `ppm_inst`, `ppm_domains`, `ppmf`
  - `ppm_dev_init()`, `ppm_dev_fini()`, `ppm_create_db()`, `ppm_claim_dev()`, `ppm_rem_dev()`, `ppm_get_dev()`
  - lookup/layer/init/ownership/power-change helpers.
- Private-data and locking macros:
  - `PPM_GET_PRIVATE`
  - `PPM_SET_PRIVATE`
  - `PPM_LOCK_DOMAIN`
  - `PPM_UNLOCK_DOMAIN`
- Debug-only flags and `PPMD`/`DPRINTF`.

## Dependencies And Relationships
Includes `sys/epm.h` and `sys/sunldi.h`, and uses layered driver handles to issue control operations to platform control devices. It backs the ioctl ABI in `ppmio.h`.

## Research Notes
`ppm_dc_t` uses a method-selected union where the first fields of each substructure must remain ordered as `iord`, `iowr`, and `val`. Domain lock macros maintain a reference count while conditionally acquiring/releasing the mutex.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ppmvar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pppt_ic_if.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pppt_ic_if.h

## Purpose
Defines the STMF/PPPT ALUA interconnect messaging API, including message types, payload layouts, allocator functions, free/transmit hooks, and receive entry points.

## Main Interfaces
- Message types:
  - proxy port register/deregister
  - LUN register/deregister/active
  - SCSI command/data/data-done/status/R2T
  - generic status
  - session create/destroy
  - echo request/reply
- `stmf_ic_msgid_t`: 64-bit message identifier.
- `stmf_ic_msg_t`: generic message container with type, ID, optional nvlist, and typed message pointer.
- Message payload structs:
  - `stmf_ic_reg_port_msg_t`
  - `stmf_ic_dereg_port_msg_t`
  - `stmf_ic_reg_dereg_lun_msg_t`
  - `stmf_ic_scsi_cmd_msg_t`
  - `stmf_ic_scsi_data_msg_t`
  - `stmf_ic_scsi_data_xfer_done_msg_t`
  - `stmf_ic_scsi_status_msg_t`
  - `stmf_ic_r2t_msg_t`
  - `stmf_ic_status_msg_t`
  - `stmf_ic_session_create_destroy_msg_t`
  - `stmf_ic_echo_request_reply_msg_t`
- Message status:
  - `STMF_IC_MSG_SUCCESS`
  - `STMF_IC_MSG_IC_DOWN`
  - `STMF_IC_MSG_TIMED_OUT`
  - `STMF_IC_MSG_INTERNAL_ERROR`
- Allocator typedefs and functions for register/deregister port, register/deregister/active LUN, SCSI command/data/data-done/status/R2T, status, session create/destroy, and echo messages.
- Message lifecycle/transport:
  - `stmf_ic_ioctl_cmd()`
  - `stmf_ic_msg_free()`
  - `stmf_ic_tx_msg()`
  - `stmf_ic_rx_msg()`
  - `stmf_msg_rx()`

## Dependencies And Relationships
Includes `sys/stmf_defines.h` and uses STMF SCSI task/session/port/status types, SCSI device descriptors, remote port data, and nvlists. Function typedefs support dynamic symbol import via `ddi_modsym()`.

## Research Notes
The generic message may share string/array storage with its backing nvlist after unmarshalling; callers must keep the nvlist alive while using such fields. `stmf_ic_tx_msg()` frees messages after sending.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pppt_ic_if.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pppt_ioctl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pppt_ioctl.h

## Purpose
Defines PPPT ioctl versioning, command numbers, and the common ioctl data structure used for daemon door installation and peer messages.

## Main Interfaces
- `PPPT_VERSION_1`
- `PPPT_IOC`: command base.
- `PPPT_INSTALL_DOOR`: installs a door for daemon communication.
- `PPPT_MESSAGE`: passes data from a peer.
- `pppt_iocdata_t`: version, error, door fd, buffer size, and 64-bit buffer address.

## Dependencies And Relationships
Used by PPPT kernel/user control paths that communicate with a daemon and pass peer message buffers.

## Research Notes
The structure uses fixed-width fields and a 64-bit buffer address, making it explicit for ioctl marshalling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pppt_ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/priocntl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/priocntl.h

## Purpose
Defines the `priocntl(2)` and `priocntlset(2)` scheduling-control ABI, command codes, class/parameter structures, varargs parameter format, and 32-bit compatibility forms.

## Main Interfaces
- `PC_VERSION`
- User functions:
  - `priocntl()`
  - `priocntlset()`
- Commands:
  - `PC_GETCID`, `PC_GETCLINFO`, `PC_SETPARMS`, `PC_GETPARMS`
  - `PC_ADMIN`, `PC_GETPRIRANGE`
  - `PC_DONICE`, `PC_SETXPARMS`, `PC_GETXPARMS`
  - `PC_SETDFLCL`, `PC_GETDFLCL`, `PC_DOPRIO`
- Class metadata:
  - `PC_CLNULL`
  - `PC_CLNMSZ`
  - `PC_CLINFOSZ`
  - `PC_CLPARMSZ`
  - `pcinfo_t`
  - `pcparms_t`
- Nice/priority:
  - `PC_GETNICE`, `PC_SETNICE`, `pcnice_t`
  - `PC_GETPRIO`, `PC_SETPRIO`, `pcprio_t`
- Extended varargs:
  - `PC_VAPARMCNT`
  - `PC_KY_NULL`
  - `PC_KY_CLNAME`
  - `pc_vaparm_t`
  - `pc_vaparms_t`
  - 32-bit packed variants where required.
- POSIX/admin structures:
  - `pcpri_t`
  - `pcadmin_t`
  - `pcadmin32_t`

## Dependencies And Relationships
Includes `sys/types.h` and `sys/procset.h`. Used by scheduler classes, libc, `dispadmin`, and POSIX scheduling interfaces.

## Research Notes
Several command codes and structures are marked not for general use. Alignment-sensitive 32-bit translation is guarded by architecture alignment checks.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/priocntl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/priv.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/priv.h

## Purpose
Defines the public and kernel-facing privilege API types, privilege syscall subcodes, implementation-info layout, per-credential flags, privilege-info records, special pseudo-privileges, and kernel helper routines.

## Main Interfaces
- Types:
  - `priv_chunk_t`
  - `priv_set_t`
  - kernel `priv_ptype_t`/`priv_t` as integers
  - userland `priv_ptype_t`/`priv_t` as strings
  - `priv_op_t`
- Syscall subcodes:
  - `PRIVSYS_SETPPRIV`
  - `PRIVSYS_GETPPRIV`
  - `PRIVSYS_GETIMPLINFO`
  - `PRIVSYS_SETPFLAGS`
  - `PRIVSYS_GETPFLAGS`
  - `PRIVSYS_ISSETUGID`
  - KLPD and pfexec register/unregister subcodes.
- Implementation layout:
  - `priv_impl_info_t`
  - `PRIV_IMPL_INFO_SIZE`
  - `PRIV_PRPRIV_INFO_OFFSET`
  - `PRIV_PRPRIV_SIZE`
- Credential flags:
  - `PRIV_DEBUG`, `PRIV_AWARE`, `PRIV_AWARE_INHERIT`
  - `NET_MAC_AWARE`, `NET_MAC_AWARE_INHERIT`
  - `PRIV_AWARE_RESET`, `PRIV_XPOLICY`, `PRIV_PFEXEC`
  - `PRIV_USER`
- Info records:
  - `priv_info_t`
  - `priv_info_uint_t`
  - `priv_info_set_t`
  - `priv_info_names_t`
  - `PRIV_INFO_SETNAMES`, `PRIV_INFO_PRIVNAMES`, `PRIV_INFO_BASICPRIVS`, `PRIV_INFO_FLAGS`
- Special pseudo-privileges:
  - `PRIV_ALL`, `PRIV_MULTIPLE`, `PRIV_NONE`, `PRIV_ALLZONE`, `PRIV_GLOBAL`
- Kernel APIs:
  - `/proc` conversion: `priv_prgetprivsize()`, `cred2prpriv()`, `priv_pr_spriv()`
  - implementation info: `priv_hold_implinfo()`, `priv_release_implinfo()`, `priv_get_implinfo_size()`
  - lookup: `priv_getset()`, `priv_getinfo()`, `priv_getbyname()`, `priv_getsetbyname()`, `priv_getbynum()`, `priv_getsetbynum()`
  - set operations: empty/fill/add/delete/member/equality/subset/intersect/union/inverse
  - credential permission and privilege-aware helpers
  - `setpflags()`, `getpflags()`

## Dependencies And Relationships
Includes `sys/types.h`, `sys/cred.h`, and generated/name constants from `sys/priv_names.h`. `priv_impl.h` defines the actual set representation for kernel/kmem consumers.

## Research Notes
The privilege implementation info is variable length and may be followed by additional typed records. Userland sees privileges by name while the kernel uses numeric IDs.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/priv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/priv_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/priv_impl.h

## Purpose
Defines the kernel-private privilege-set storage layout, credential privilege container, fast privilege bit operations, and internal privilege-set globals.

## Main Interfaces
- `struct priv_set`: array of `PRIV_SETSIZE` `priv_chunk_t` words.
- `cred_priv_t`: per-credential privilege sets plus credential privilege flags.
- Globals:
  - `priv_basic`
  - `priv_unsafe`
  - `priv_fullset`
- `priv_init()`
- Credential privilege access macros:
  - `CR_EPRIV`
  - `CR_IPRIV`
  - `CR_PPRIV`
  - `CR_LPRIV`
  - `CR_FLAGS`
  - `CR_OEPRIV`
  - `CR_OPPRIV`
- Awareness/validation:
  - `PRIV_EISAWARE`
  - `PRIV_PISAWARE`
  - `PRIV_VALIDSET`
  - `PRIV_VALIDOP`
  - `PRIV_FULLSET`
- Bit layout and operations:
  - `PRIV_SETBYTES`
  - `__NBWRD`
  - `privmask()`
  - `privword()`
  - `PRIV_ASSERT`
  - `PRIV_CLEAR`
  - `PRIV_ISASSERT`

## Dependencies And Relationships
Includes `sys/priv_const.h` and `sys/priv.h`. Relies on `CR_PRIVS()` from `sys/cred_impl.h`.

## Research Notes
Debug kernels route bit operations through checked helper functions; non-debug kernels use direct bit manipulation. Bit numbering is arranged through `privmask()` using high-bit-first placement within each word.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/priv_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/prnio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/prnio.h

## Purpose
Defines printer-interface ioctl commands, capability/status bits, interface/device-id buffer structures, timeout structure, and 32-bit kernel compatibility structures.

## Main Interfaces
- Ioctls:
  - `PRNIOC_GET_IFCAP`
  - `PRNIOC_SET_IFCAP`
  - `PRNIOC_GET_IFINFO`
  - `PRNIOC_GET_STATUS`
  - `PRNIOC_GET_1284_DEVID`
  - `PRNIOC_GET_1284_STATUS`
  - `PRNIOC_GET_TIMEOUTS`
  - `PRNIOC_SET_TIMEOUTS`
  - `PRNIOC_RESET`
- Capability bits:
  - `PRN_BIDI`
  - `PRN_HOTPLUG`
  - `PRN_1284_DEVID`
  - `PRN_1284_STATUS`
  - `PRN_TIMEOUTS`
  - `PRN_STREAMS`
- Structures:
  - `prn_interface_info`
  - `prn_1284_device_id`
  - `prn_timeouts`
- Recommended interface strings:
  - `PRN_PARALLEL`
  - `PRN_SERIAL`
  - `PRN_USB`
  - `PRN_1394`
- Status bits:
  - `PRN_ONLINE`
  - `PRN_READY`
  - IEEE 1284 status pins: `PRN_1284_NOFAULT`, `PRN_1284_SELECT`, `PRN_1284_PE`, `PRN_1284_BUSY`
- 32-bit kernel structures:
  - `prn_interface_info32`
  - `prn_1284_device_id32`

## Dependencies And Relationships
Includes `sys/types.h` and `sys/ioccom.h`. Intended for printer device drivers and userland printer-management tools.

## Research Notes
Pointer-bearing structures preserve 32-bit layout with explicit filler or alternate `caddr32_t` forms.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/prnio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/proc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/proc.h

## Purpose
Defines the central kernel process structure, process/LWP directory state, PID state, process flags, signal/process-management macros, and many kernel process/thread/LWP/signal function prototypes.

## Main Interfaces
- Profiling and context:
  - `struct prof`
  - `lwpent_t`
  - `pctxop_t`
  - `lwpdir_t`
  - `tidhash_t`
  - `ret_tidhash_t`
- `proc_t`: central process object containing address space, credentials, parent/child/session/PID links, locks/condition variables, signal state, LWP/thread directories, `/proc` state, watchpoints, stack/page-size state, microstate/resource accounting, profiling, door state, audit state, LDT state on x86, timers, task/project/pool/zone/brand/security/resource-control state, event-port count, upanic state, and embedded `struct user`.
- Kernel globals:
  - `practive`
  - `proc_sched`
  - `proc_init`
  - `proc_pageout`
  - `proc_fsflush`
  - `p0`, `p0lock`, `pid0`
- UID process counts:
  - `struct upcount`
- PID support:
  - `struct pid`
  - `p_pgrp`, `p_pid`, `p_slot`, `p_detached`
  - `PID_HOLD`, `PID_RELE`
  - `PID_ALLOC_PROC`
- Persistent lock:
  - `struct plock`
  - `p_lock` macro.
- Process states:
  - `SSLEEP`, `SRUN`, `SZOMB`, `SSTOP`, `SIDL`, `SONPROC`, `SWAIT`
- Child notification and process flags:
  - `CLDPEND`, `CLDCONT`, `CLDNOSIGCHLD`, `CLDWAITPID`
  - `/proc` flags `P_PR_*`
  - process flags `SSYS`, `SEXITING`, `SFORKING`, `SWATCHOK`, `SKILLED`, `SEXECED`, `SMSACCT`, `SDOCORE`, and others.
  - pool flags `PBWAIT`, `PEXITED`
  - upanic flags `P_UPF_*`
- Signal/process macros:
  - `PTOU`
  - `tracing`
  - `ISSIG`, `ISSIG_FAST`, `ISSIG_PENDING`
  - `ISSTOP`, `ISHOLD`, `MUSTRETURN`, `pr_watch_active`
- Constants/types:
  - `FORREAL`, `JUSTLOOKING`
  - `SUSPEND_NORMAL`, `SUSPEND_PAUSE`
  - `NOCLASS`, `CLASS_UNUSED`
  - `lwp_stat_id_t`
  - `prkillinfo_t`
- Kernel prototypes for:
  - process lifecycle and VM release
  - signals and signal queues
  - PID lookup/allocation/group/session helpers
  - microstate accounting
  - thread creation/context/TSD
  - LWP lifecycle, hold/run/continue/fork/register handling
  - signal queue allocation, delivery, and wait-status conversion.

## Dependencies And Relationships
Includes thread, credentials, user, watchpoint, timers, model, refstr, AVL/list, rctl, doors, signalfd, and security flags. It is one of the central kernel headers used by process management, `/proc`, signals, scheduling, resource controls, zones, brands, doors, and pools.

## Research Notes
Many `proc_t` fields are grouped by lock ownership in comments: no explicit lock, `pidlock`, `p_lock`, `as_rangelock`, dedicated locks, and subsystem locks. The first two fields of related project structs and lock macros elsewhere depend on stable layout conventions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/proc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/processor.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/processor.h

## Purpose
Defines public processor identifiers, processor online/state flags, processor info layout, CPU binding constants, and user/kernel processor system-call interfaces.

## Main Interfaces
- Types:
  - `lgrpid_t`
  - `processorid_t`
  - `chipid_t`
- `p_online(2)`/processor state constants:
  - `P_OFFLINE`, `P_ONLINE`, `P_STATUS`, `P_FAULTED`, `P_POWEROFF`, `P_NOINTR`, `P_SPARE`, `P_DISABLED`, `P_BAD`, `P_FORCED`
- State strings:
  - `PS_OFFLINE`, `PS_ONLINE`, `PS_FAULTED`, `PS_POWEROFF`, `PS_NOINTR`, `PS_SPARE`, `PS_DISABLED`
- `processor_info_t`: state, CPU type string, FPU type string, and clock MHz.
- Binding constants:
  - `PBIND_NONE`
  - `PBIND_QUERY`
  - `PBIND_HARD`
  - `PBIND_SOFT`
  - `PBIND_QUERY_TYPE`
- Sentinel:
  - `P_ALL_SIBLINGS`
- User APIs:
  - `p_online()`
  - `processor_info()`
  - `processor_bind()`
  - `getcpuid()`
  - `gethomelgroup()`
- Kernel APIs:
  - `p_online_internal()`
  - `p_online_internal_locked()`

## Dependencies And Relationships
Includes `sys/types.h` and `sys/procset.h`. The header notes that public `P_*` flags are not for inspecting in-kernel CPU state; kernel code should use `sys/cpuvar.h`.

## Research Notes
`processor_info_t` is explicitly ABI-stable and should not be modified. String fields are guaranteed NUL-terminated.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/processor.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/procfs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/procfs.h

## Purpose
Defines the structured `/proc` ABI for process/LWP control, status, psinfo, memory maps, credentials, privileges, watchpoints, I/O, resource usage, page data, fd info, core-file notes, and ILP32 compatibility structures.

## Main Interfaces
- Structured-proc selection:
  - `_STRUCTURED_PROC`
  - falls back to `sys/old_procfs.h` for non-kernel old-interface users.
- `/proc` control codes:
  - `PCNULL`, `PCSTOP`, `PCDSTOP`, `PCWSTOP`, `PCTWSTOP`, `PCRUN`
  - signal/fault/syscall tracing controls
  - register, watchpoint, agent, read/write, credential, privilege, zone controls.
- `PCRUN` flags:
  - `PRCSIG`, `PRCFAULT`, `PRSTEP`, `PRSABORT`, `PRSTOP`
- Status/info structures:
  - `lwpstatus_t`
  - `pstatus_t`
  - `lwpsinfo_t`
  - `psinfo_t`
- Flags/reasons:
  - `PR_STOPPED`, `PR_ISTOP`, `PR_DSTOP`, `PR_STEP`, `PR_ASLEEP`, `PR_AGENT`, process flags, and traced modes.
  - stop reasons `PR_REQUESTED`, `PR_SIGNALLED`, `PR_SYSENTRY`, `PR_SYSEXIT`, `PR_JOBCONTROL`, `PR_FAULTED`, `PR_SUSPENDED`, `PR_CHECKPOINT`
- Mapping structures:
  - `prmap_t`
  - `prxmap_t`
  - memory attribute flags `MA_READ`, `MA_WRITE`, `MA_EXEC`, `MA_SHARED`, `MA_ANON`, `MA_ISM`, `MA_NORESERVE`, `MA_SHM`
  - obsolete `MA_BREAK`, `MA_STACK`
- Credentials/privileges/security:
  - `prcred_t`
  - `prpriv_t`
  - `prsecflags_t`
- Watchpoint/I/O:
  - `prwatch_t`
  - `WA_READ`, `WA_WRITE`, `WA_EXEC`, `WA_TRAPAFTER`
  - `priovec_t`
- Usage/page data:
  - `prusage_t`
  - `prpageheader_t`
  - `prasmap_t`
  - `PG_REFERENCED`, `PG_MODIFIED`, `PG_HWMAPPED`
- File descriptor/core data:
  - `prfdinfo_core_t`
  - `prfdinfo_t`
  - `PRFDINFO_ROUNDUP`
  - `pr_misc_header_t`
  - `enum PR_MISC_TYPES`
  - socket option bit summaries in `prsockopts_bool_opts_t`
  - `prlwpname_t`
  - `prheader_t`
  - `prupanic_t`
  - `prcwd_t`
- Set manipulation macros:
  - `prfillset`
  - `premptyset`
  - `praddset`
  - `prdelset`
  - `prismember`
- 32-bit kernel views under `_SYSCALL32`:
  - `lwpstatus32_t`, `pstatus32_t`, `lwpsinfo32_t`, `psinfo32_t`
  - `prmap32_t`, `prxmap32_t`, `prcred32_t`, `prwatch32_t`, `priovec32_t`
  - `prusage32_t`, `prpageheader32_t`, `prasmap32_t`, `prheader32_t`

## Dependencies And Relationships
Includes feature tests, types, time, signal/siginfo, fault, syscall, pset, procfs ISA register layouts, privileges, stat, param, security flags, and thread name sizing. Closely mirrors state from `proc.h`, `priv.h`, and architecture-specific procfs headers.

## Research Notes
This is ABI-heavy. Many fields are reserved/filler for compatibility, and comments distinguish deprecated `psinfo` flags from structured status flags. Misc fd info uses self-describing variable-length records.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/procfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/procset.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/procset.h

## Purpose
Defines process-set identifiers and set-combination operations used by signal, priority, wait, and event-exit interfaces.

## Main Interfaces
- Initial identifiers:
  - `P_INITPID`
  - `P_INITUID`
  - `P_INITPGID`
- `idtype_t`: identifies process sets by PID, PPID, PGID, SID, scheduling class, UID, GID, all, LWP ID, task, project, pool, zone, contract, CPU, or processor set.
- `idop_t`: set operations `POP_DIFF`, `POP_AND`, `POP_OR`, `POP_XOR`.
- `procset_t`: left/right simple set plus set operator.
- `setprocset()`: initialization macro.
- Kernel helpers:
  - `dotoprocs()`
  - `dotolwp()`
  - `procinset()`
  - `sigsendproc()`
  - `sigsendset()`
  - `cur_inset_only()`
  - `getmyid()`

## Dependencies And Relationships
Includes feature tests, types, and signal definitions. Used by `sigsend`, `priocntl`, `waitid`, and related system calls. Some names are hidden under strict XPG namespace conditions.

## Research Notes
The comments define `POP_AND` as “set disjunction” and `POP_OR` as “set conjunction,” but their described behavior is intersection and union respectively.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/procset.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/project.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/project.h

## Purpose
Defines kernel project state, project resource accounting, project kstats, project lifecycle helpers, and project resource-control handles.

## Main Interfaces
- `kproject_kstat_t`: zone name, usage, and value kstat fields.
- `kproject_data_t`: per-project accounting for shared memory, IPC, locked memory, contracts, crypto memory, and kstats.
- `kproject_t`: project ID, zone ID/pointer, reference count, shares, rctls, list links, subsystem data, pool binding lock, LWP/task/process counters and controls, CPU cap pointer, and extended policy pointer.
- Flags for lookup:
  - `PROJECT_HOLD_FIND`
  - `PROJECT_HOLD_INSERT`
- Kernel routines:
  - `project_init()`
  - `project_hold()`
  - `project_hold_by_id()`
  - `project_rele()`
  - `project_walk_all()`
  - `curprojid()`
- Globals:
  - `proj0p`
  - `rc_project_nlwps`
  - `rc_project_nprocs`
  - `rc_project_ntasks`
  - `rc_project_locked_mem`
  - `rc_project_crypto_mem`

## Dependencies And Relationships
Includes kstat, types, mutex, rctl, IPC resource controls, and zones. Integrates with pools, CPU caps, KLPD policy, and resource controls.

## Research Notes
The first two fields of `kproject_t` must not be reordered. Comments document which subsystem lock protects each quantity.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/project.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/protosw.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/protosw.h

## Purpose
Defines the classic protocol switch table interface for socket protocol modules, protocol flags, user-request command codes, control-input command codes, and control-output request codes.

## Main Interfaces
- `struct protosw`: socket type, domain, protocol number, flags, protocol hooks, user request hook, init/fast/slow timeout/drain hooks.
- Timer rates:
  - `PR_SLOWHZ`
  - `PR_FASTHZ`
- Protocol flags:
  - `PR_ATOMIC`
  - `PR_ADDR`
  - `PR_CONNREQUIRED`
  - `PR_WANTRCVD`
  - `PR_RIGHTS`
  - `PR_OOB_ADDR`
- User request codes:
  - `PRU_ATTACH`, `PRU_DETACH`, `PRU_BIND`, `PRU_LISTEN`, `PRU_CONNECT`, `PRU_ACCEPT`
  - disconnect/shutdown/send/receive/OOB/control/address/timer/protocol internal requests.
- Optional debug name arrays under:
  - `PRUREQUESTS`
  - `PRCREQUESTS`
  - `PRCOREQUESTS`
- Control-input commands:
  - `PRC_IFDOWN`, `PRC_ROUTEDEAD`, unreachable/redirect/time-exceeded/parameter/gateway commands.
- Control-output commands:
  - `PRCO_GETOPT`
  - `PRCO_SETOPT`
- Kernel lookup:
  - `pffindproto()`
  - `pffindtype()`

## Dependencies And Relationships
Part of the socket/protocol stack ABI inherited from BSD/AT&T lineage. References `struct domain`, sockets, mbufs, and protocol-specific control paths by convention.

## Research Notes
The comments warn that some control-input numeric values are assumed by existing code and should be changed only with extreme care.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/protosw.h -->