# subset-b-000805 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/iommu.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/iommu.c

## Purpose
Implements pSeries PCI DMA/IOMMU setup for bare-metal and LPAR guests. It provides TCE table allocation, TCE set/clear/get operations, default DMA-window discovery, dynamic DMA window (DDW) creation/removal, SPAPR TCE IOMMU API hooks for VFIO/KVM, memory-hotplug TCE maintenance, and OF reconfiguration cleanup.

## Important APIs, Types, And Functions
Core table helpers are `iommu_pseries_alloc_table`, `iommu_pseries_alloc_group`, `iommu_pseries_free_group`, and `iommu_table_setparms_common`. Non-LPAR TCE ops are `tce_build_pSeries`, `tce_clear_pSeries`, and `tce_get_pseries`; LPAR hcall-backed ops are `tce_build_pSeriesLP`, `tce_buildmulti_pSeriesLP`, `tce_free_pSeriesLP`, `tce_freemulti_pSeriesLP`, and `tce_get_pSeriesLP`. DDW state is represented by `struct dynamic_dma_window_prop`, `struct dma_win`, `struct ddw_query_response`, and `struct ddw_create_response`. Major DDW paths are `query_ddw`, `create_ddw`, `enable_ddw`, `remove_dma_window_named`, `spapr_tce_create_table`, `spapr_tce_unset_window`, `spapr_tce_take_ownership`, and `spapr_tce_release_ownership`.

## Control Flow
`iommu_init_early_pSeries` installs pSeries PCI DMA setup callbacks and registers memory and OF reconfig notifiers. Non-LPAR boot divides PHB DMA space among slots and uses firmware-provided `linux,tce-base`/`linux,tce-size`. LPAR boot walks up device-tree nodes with `pci_dma_find`, creates a table group around an `ibm,dma-window` or 64-bit window property, initializes the table, registers the IOMMU group, and attaches devices. When a device has a DMA mask above 32 bits, `iommu_bypass_supported_pSeriesLP` attempts `enable_ddw`: query firmware, optionally remove/reset default windows or enable limited-address mode, choose an IO page size and window size, create a DDW, add an OF property, premap RAM for direct mapping, and optionally install a dynamic TCE table.

## State And Persistence
Persistent runtime state includes per-PCI-node `table_group`, TCE tables, device `dma_offset`/`bus_dma_limit`, `dma_win_list` entries for created windows, `failed_ddw_pdn_list` entries that suppress unsafe retries, and dynamic OF properties such as `linux,direct64-ddr-window-info`, `ibm,dma-window`, and `ibm,dma-window-saved`. Per-CPU `tce_page` buffers cache indirect TCE pages. Firmware owns the actual LIOBN windows and TCE mappings.

## Dependencies And Integration Points
Depends on PAPR RTAS DDW calls, PAPR hcalls for TCE put/get/stuff/indirect operations, PCI OF nodes and `pci_dn`, EEH-derived BUID/config addressing, generic DMA-IOMMU ops, Linux IOMMU group/table APIs, VFIO SPAPR TCE ownership paths, memory hotplug notifiers, and OF reconfig notifiers. It is a key integration point between pSeries PCI enumeration and DMA mapping.

## Risks And Edge Cases
High-risk areas are replacing an in-use default window, partial DDW creation cleanup, stale OF properties during kexec/kdump, direct-map TCE updates during memory hotplug, limited-address mode reset behavior, and VFIO ownership ordering. Some failure paths add a parent node to the failed-DDW list to avoid reattempting operations that could race with in-flight DMA and trigger EEH. A few allocation helper failure paths must free both property names and values. Direct mappings must not premap persistent memory outside the hotplug maximum.

## Test Signals
Useful signals include pSeries LPAR boots with and without DDW, PCI devices with 32-bit, limited, and 64-bit DMA masks, kdump boots preserving/removing DDWs, memory online/offline with direct DDWs, VFIO SPAPR TCE table create/unset/take/release flows, DLPAR PCI node detach, `disable_ddw` and `multitce=off` boot parameters, and DMA stress under devices sharing a PE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/iommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/kexec.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/kexec.c

## Purpose
Handles pSeries CPU teardown during kexec and crash shutdown. It unregisters hypervisor per-CPU facilities when safe and tears down the active interrupt controller backend.

## Important APIs, Types, And Functions
The file defines `pseries_kexec_cpu_down(int crash_shutdown, int secondary)`. It uses `firmware_has_feature(FW_FEATURE_SPLPAR)`, `unregister_dtl`, `unregister_slb_shadow`, `unregister_vpa`, `xive_enabled`, `xive_teardown_cpu`, `xive_shutdown`, and `xics_kexec_teardown_cpu`.

## Control Flow
For shared-processor LPARs on non-crash kexec, the current CPU unregisters its dispatch trace log if enabled, then unregisters SLB shadow and VPA areas using the hardware CPU id. It logs but does not abort on deregistration failure. Interrupt teardown then branches on XIVE versus XICS: XIVE per-CPU teardown always runs and the primary CPU shuts down XIVE globally; XICS uses its kexec CPU teardown with the secondary flag.

## State And Persistence
The function clears hypervisor registrations for DTL, SLB shadow, and VPA so the next kernel is less likely to inherit stale host references. It does not persist state in the filesystem and deliberately avoids unregister hcalls during crash shutdown.

## Dependencies And Integration Points
Integrates with the architecture kexec path, SPLPAR per-CPU registration code in `lpar.c`, XIVE/XICS interrupt controllers, paca/lppaca state, and PAPR hcall wrappers.

## Risks And Edge Cases
Crash shutdown skips unregistering hypervisor facilities, trading cleanup for lower risk while the kernel may be corrupted. Failed unregisters are warnings only. The primary/secondary distinction matters for avoiding duplicate global XIVE shutdown. Incorrect CPU ids would leave hypervisor references to old memory.

## Test Signals
Exercise normal kexec and crash kexec on SPLPAR and non-SPLPAR systems, with both XIVE and XICS configurations. Check logs for deregistration warnings and validate that the next kernel boots without stale VPA/DTL or interrupt-controller state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/kexec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/lpar.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/lpar.c

## Purpose
Provides pSeries LPAR hypervisor integration for hcalls, dispatch trace logs, VPA registration, hash/radix MMU setup, HPT operations, HPT resizing, CMO page hints, hcall tracing, memory entitlement helpers, and debug/proc visibility.

## Important APIs, Types, And Functions
Externally visible functions include exported hcall wrappers, `alloc_dtl_buffers`, `register_dtl_buffer`, `vpa_init`, `pseries_paravirt_steal_clock`, `hpte_init_pseries`, `radix_init_pseries`, `arch_free_page`, `h_get_mpp`, and `h_get_mpp_x`. Hash MMU ops include `pSeries_lpar_hpte_insert`, `pSeries_lpar_hpte_remove`, `pSeries_lpar_hpte_updatepp`, `pSeries_lpar_hpte_invalidate`, `pSeries_lpar_flush_hash_range`, `pseries_hpte_clear_all`, and hugepage invalidation helpers. Dispatch statistics use `struct dtl_worker`, `struct vcpu_dispatch_data`, `dtl_access_lock`, per-CPU DTL indices, and proc handlers for `powerpc/vcpudispatch_stats`.

## Control Flow
During CPU setup, `vpa_init` registers the lppaca as VPA, optionally registers SLB shadow for SPLPAR hash-MMU guests, and registers any allocated DTL buffer. DTL accounting allocates per-CPU buffers, registers them with the hypervisor, and optionally starts delayed workers that parse DTL records to update vCPU dispatch locality statistics. Hash MMU init installs pSeries `mmu_hash_ops`; HPTE insert/update/remove paths translate Linux page attributes into PAPR hcalls. Flush paths choose H_BLOCK_REMOVE, H_BULK_REMOVE, or per-entry invalidation based on firmware features and block-size characteristics. HPT resize prepares with the hypervisor, commits under stop-machine, then updates local hash-table globals.

## State And Persistence
State is mostly per-CPU and MMU-global: paca DTL pointers, lppaca DTL/VPA fields, dispatch-stat counters, VPHN associativity caches, `hblkrm_size`, hash table globals, CMO hint boot parameter state, and hcall trace recursion depth. Debugfs can expose raw VPA data. No durable storage is used.

## Dependencies And Integration Points
Depends on PAPR hcalls, paca/lppaca layout, SPLPAR firmware features, VPHN topology hcalls, CPU hotplug, procfs/debugfs, generic hash and radix MMU code, stop_machine, fadump/kexec paths, CMO firmware support, and tracepoints. `lparcfg.c` consumes `h_get_mpp` and `h_get_mpp_x`.

## Risks And Edge Cases
Hash table hcalls are low-level and often `BUG_ON` unexpected hypervisor results. TLB invalidation batching must preserve AVPN/slot ordering and obey block alignment. DTL workers must stay pinned to the intended CPU and coordinate with hotplug. HPT resize has timeout and stop-machine failure modes. CMO free-page hints are disabled for radix and gated by firmware/boot parameter. Hcall tracepoints guard against recursion but cannot catch every tracing-induced hcall.

## Test Signals
Boot SPLPAR with hash and radix MMU, enable/disable `vcpudispatch_stats`, vary `vcpudispatch_stats_freq`, hotplug CPUs, run THP and hugetlb workloads, kexec with hash MMU, exercise `bulk_remove=off`, test HPT resize under load, verify paravirt steal time, inspect VPA debugfs, and check `lparcfg` memory entitlement output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/lpar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/lparcfg.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/lparcfg.c

## Purpose
Creates `/proc/powerpc/lparcfg`, a pSeries partition configuration and entitlement interface. It reports processor, memory, capacity, pool, CMO, dispatch, power, security, and identity data, and on SPLPAR systems allows selected entitlement/weight updates.

## Important APIs, Types, And Functions
The main proc handlers are `lparcfg_open`, `lparcfg_data`, `pseries_lparcfg_data`, and `lparcfg_write`. Data collection helpers include `h_get_ppp`, `parse_ppp_data`, `parse_mpp_data`, `parse_mpp_x_data`, `read_lpar_name`, `parse_system_parameter_string`, `pseries_cmo_data`, `splpar_dispatch_data`, `parse_em_data`, `maxmem_data`, and `show_gpci_data`. Update paths are `update_ppp` and `update_mpp`.

## Control Flow
Reads emit module/version, system model, serial, partition id, then SPLPAR-specific or dedicated-processor capacity data. SPLPAR reads combine PAPR system parameters, H_GET_PPP/H_PIC processor data, H_GET_MPP/H_GET_MPP_X memory data, lppaca counters, PURR/TB values, and security flavor. Writes parse `name=value` pairs for `partition_entitled_capacity`, `capacity_weight`, `entitled_memory`, and `entitled_memory_weight`; they call H_SET_PPP or H_SET_MPP and translate common hcall returns to errno or byte count.

## State And Persistence
The file stores `boot_pool_idle_time` captured at init. Other displayed state is read live from firmware, device tree, lppaca, CMO, VIO, and memory metadata. Writes persist entitlement changes in the hypervisor partition configuration rather than kernel-local durable storage.

## Dependencies And Integration Points
Depends on procfs/seq_file, PAPR sysparm helpers, hcall wrappers, RTAS/device tree properties, lppaca counters, `h_get_mpp` from `lpar.c`, CMO helpers, VIO CMO entitlement validation, hugepage and dynamic memory metadata, and VAS CPU DLPAR reconfiguration after processor entitlement updates.

## Risks And Edge Cases
Input parsing is intentionally narrow and truncates at 64 bytes. Failed H_PIC at boot affects since-boot pool-idle statistics. Firmware or QEMU may omit the dynamic LPAR name, forcing a device-tree fallback. Entitlement writes can return constrained success, busy, hardware, or parameter errors. Memory entitlement writes must be accepted by VIO before changing firmware state.

## Test Signals
Read `/proc/powerpc/lparcfg` on SPLPAR and non-SPLPAR guests, with CMO/XCMO enabled and disabled. Test writes for all accepted keys, invalid formats, non-SPLPAR writes, H_BUSY/H_PARAMETER fault injection, VAS reconfiguration on processor entitlement changes, and lparstat compatibility fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/lparcfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/mobility.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/mobility.c

## Purpose
Implements pSeries partition mobility and migration support. It updates the live device tree after migration, drives VASI/H_JOIN/ibm,suspend-me handshakes, coordinates all CPUs through stop-machine, and exposes a sysfs migration trigger.

## Important APIs, Types, And Functions
Device-tree update helpers include `mobility_rtas_call`, `pseries_devicetree_update`, `delete_dt_node`, `update_dt_node`, `update_dt_property`, `add_dt_node`, and `post_mobility_fixup`. Migration flow helpers are `poll_vasi_state`, `wait_for_vasi_session_suspending`, `do_suspend`, `do_join`, `pseries_suspend`, `pseries_cancel_migration`, `pseries_migrate_partition`, and `rtas_syscall_dispatch_ibm_suspend_me`. Sysfs setup uses `migration_store` and `mobility_sysfs_init`.

## Control Flow
Migration first suspends VAS and HVPIPE, waits for the VASI session to enter suspending state, optionally relaxes hardlockup watchdog timeout, and calls `stop_machine` so all online CPUs enter `H_JOIN`. The CPU that receives `H_CONTINUE` performs `ibm,suspend-me`; on completion one CPU marks the shared state done and prods the rest. Successful migration runs `post_mobility_fixup`: activate firmware, lock CPU hotplug readers, tear down cacheinfo, process RTAS update-nodes/update-properties directives, rebuild cacheinfo, refresh mitigations, and reread hv-24x7 system info. Failed suspend attempts can retry while VASI remains suspending; final failure signals cancellation.

## State And Persistence
Persistent kernel state includes the `/sys/kernel/mobility` kobject, watchdog LPM factor sysctl when enabled, temporary update buffers, and live device-tree changes. Migration changes firmware/hypervisor session state and may alter runtime topology, cache nodes, mitigation choices, VAS, and HVPIPE availability.

## Dependencies And Integration Points
Depends on RTAS `ibm,update-nodes`, `ibm,update-properties`, and `ibm,suspend-me`; PAPR hcalls `H_VASI_STATE`, `H_JOIN`, `H_PROD`, and `H_VASI_SIGNAL`; DLPAR attach/detach/configure helpers; cacheinfo; CPU hotplug; stop_machine; watchdog code; VAS and HVPIPE migration handlers; hv-24x7; and sysfs.

## Risks And Edge Cases
Firmware can split property updates across calls, remove/add platform-facilities nodes that drivers cannot handle, or omit VASI state support. The code intentionally ignores platform-facilities add/remove operations. H_JOIN can return prematurely due to unrelated prods and must retry until shared done state is visible. Destination systems can have fewer SLB entries, so the code clamps SLB size before suspend. Device tree update failures leave partially refreshed topology.

## Test Signals
Run migration through sysfs and RTAS syscall dispatch, including successful, retry, and cancellation paths. Validate device-tree changes, cacheinfo rebuild, CPU hotplug exclusion, VAS/HVPIPE disable and resume, watchdog timeout restoration, VASI completion wait, platform-facilities handling, and PRRN/migration-scope update processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/mobility.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/msi.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/msi.c

## Purpose
Implements pSeries PCI MSI/MSI-X support using RTAS `ibm,change-msi` and `ibm,query-interrupt-source-number`, and exposes it through Linux MSI parent IRQ domains.

## Important APIs, Types, And Functions
Key helpers are `rtas_change_msi`, `rtas_disable_msi`, `rtas_query_irq_number`, `check_req_msi`, `check_req_msix`, `msi_quota_for_device`, `rtas_prepare_msi_irqs`, `pseries_msi_ops_prepare`, `pseries_msi_ops_teardown`, `pseries_irq_domain_alloc`, `pseries_irq_domain_free`, `pseries_msi_allocate_domains`, `pseries_msi_free_domains`, and `rtas_msi_pci_irq_fixup`. Per-allocation state is `struct pseries_msi_device`.

## Control Flow
Initialization locates RTAS tokens and installs a PCI IRQ fixup callback. Domain allocation creates an MSI parent IRQ domain per PHB. For a device request, `rtas_prepare_msi_irqs` checks firmware request properties, computes the PE quota, rounds MSI-X counts when firmware requires powers of two, tries explicit MSI/MSI-X and 32-bit variants, and falls back to legacy change calls. IRQ allocation queries the hardware interrupt source number for the MSI index, allocates parent interrupts, and installs a pSeries MSI chip.

## State And Persistence
Static RTAS tokens are cached. Each MSI allocation stores quota and used count in `struct pseries_msi_device` until teardown, where the firmware allocation is disabled all-at-once. The chip caches MSI messages instead of rewriting MSI-X vector table entries.

## Dependencies And Integration Points
Depends on PCI device-tree properties `ibm,req#msi`, `ibm,req#msi-x`, and `ibm,pe-total-#msi`; EEH PE topology; RTAS; generic MSI library parent ops; Linux IRQ domains; PCI config space; and pSeries PHB setup.

## Risks And Edge Cases
RTAS cannot disable a single vector, so teardown happens at MSI-domain teardown. Firmware may reject non-power-of-two MSI-X counts. Old firmware lacks explicit or 32-bit MSI functions, forcing fallback or a Gen2 32-bit MSI address hack. Quota calculation must avoid starving peer devices in a PE. Devices without LSI or MSI request properties are intentionally left alone by the fixup.

## Test Signals
Test MSI and MSI-X allocation under PowerVM/QEMU, quota clamping across multiple PE devices, 32-bit DMA-mask devices, PCIe Gen2 fallback, vector teardown, suspend/resume MSI message composition, and PHB domain allocation failures. Boot logs should show RTAS token discovery and no unexpected `ibm,change-msi` errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/msi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/nvram.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/nvram.c

## Purpose
Provides pSeries NVRAM access through RTAS fetch/store calls and integrates NVRAM partitions with RTAS error logging and oops/pstore preservation.

## Important APIs, Types, And Functions
Important functions are `pSeries_nvram_read`, `pSeries_nvram_write`, `pSeries_nvram_get_size`, `nvram_write_error_log`, `nvram_read_error_log`, `nvram_clear_error_log`, `clobbering_unread_rtas_event`, `pseries_nvram_init_log_partitions`, and `pSeries_nvram_init`. Static state includes `nvram_size`, RTAS tokens, `nvram_buf`, `nvram_lock`, and unread event timestamps.

## Control Flow
Initialization finds the OF `nvram` node, reads `#bytes`, caches RTAS tokens, and installs `ppc_md` NVRAM callbacks. Reads and writes clamp the request to NVRAM size, serialize on a spinlock, chunk transfers to 32 bytes, and call RTAS with a low physical address buffer. Log partition initialization scans NVRAM, initializes RTAS and oops partitions, and records unread event timing on writes.

## State And Persistence
NVRAM contents are persistent firmware storage. Kernel state tracks size, service tokens, a shared transfer buffer, and timestamps for unread RTAS events. `last_rtas_event` is also exported under `CONFIG_PSTORE`.

## Dependencies And Integration Points
Depends on RTAS NVRAM services, OF NVRAM node data, `ppc_md` machine callbacks, generic PowerPC NVRAM partition helpers, RTAS log partition definitions, pstore when enabled, and timekeeping.

## Risks And Edge Cases
The static transfer buffer is protected by a spinlock because RTAS accesses are serialized and physically addressed. Partial or mismatched RTAS byte counts are treated as I/O errors. `nvram_clear_error_log` marks an event logged rather than erasing it. Oops logging can clobber an unread RTAS event if both partitions overlap, so `clobbering_unread_rtas_event` uses a short timeout heuristic.

## Test Signals
Boot with a valid and missing NVRAM node, read/write `/dev/nvram` through machine callbacks, validate partition scanning, inject RTAS fetch/store failures, test RTAS event write/read/clear, and verify oops/pstore behavior when oops and RTAS log partitions share storage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/nvram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/of_helpers.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/of_helpers.c

## Purpose
Provides small Open Firmware helper routines used by pSeries runtime device-tree and DRC handling code.

## Important APIs, Types, And Functions
Defines `pseries_of_derive_parent` and exports `of_read_drc_info_cell`. The latter fills `struct of_drc_info` fields from a packed `ibm,drc-info` style property cell.

## Control Flow
`pseries_of_derive_parent` rejects root, computes the dirname of a node path, finds that node with `of_find_node_by_path`, and returns either the parent node or an encoded error. `of_read_drc_info_cell` walks a property cursor through two encoded strings and five big-endian integer fields, updates the caller's cursor to the next entry, and calculates the last DRC index.

## State And Persistence
No persistent state is kept. Callers receive referenced OF nodes or decoded stack/caller-owned data and are responsible for node references.

## Dependencies And Integration Points
Depends on Linux OF string/u32 property iteration helpers, allocation APIs, and `struct of_drc_info` from PowerPC OF code. It supports pSeries DLPAR and mobility-style dynamic tree manipulation.

## Risks And Edge Cases
Malformed property buffers return `-EINVAL`. Allocation failure while deriving a parent returns `-ENOMEM`. The DRC parser stores string pointers into the original property data, so the property lifetime must outlive the decoded struct use. Root path has no parent and is rejected.

## Test Signals
Unit-style tests can feed valid and truncated DRC-info entries, root and nested paths, missing parent paths, and allocation-failure injection. Runtime signals are successful DLPAR connector parsing and dynamic OF node attachment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/of_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/of_helpers.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/of_helpers.h

## Purpose
Declares the pSeries OF helper interface for deriving a parent device node from a full OF path.

## Important APIs, Types, And Functions
Includes `<linux/of.h>` and declares `struct device_node *pseries_of_derive_parent(const char *path);`.

## Control Flow
This header has no runtime control flow. It allows other pSeries compilation units to call the implementation in `of_helpers.c`.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Depends on Linux OF types and is integrated by pSeries code that needs to create or reparent dynamic device-tree nodes.

## Risks And Edge Cases
The header does not declare `of_read_drc_info_cell` even though `of_helpers.c` defines and exports it; that API is presumably declared in broader PowerPC OF headers. Include guard prevents duplicate declarations.

## Test Signals
Compile coverage is the useful signal: users of `pseries_of_derive_parent` should include this header without missing-type warnings or duplicate definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/of_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-hvpipe.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-hvpipe.c

## Purpose
Implements `/dev/papr-hvpipe`, a userspace interface to the PAPR hypervisor pipe for inband communication with supported sources such as HMCs.

## Important APIs, Types, And Functions
The device ioctl path is `papr_hvpipe_dev_ioctl` and `papr_hvpipe_dev_create_handle`. Per-source file operations are `papr_hvpipe_handle_read`, `papr_hvpipe_handle_write`, `papr_hvpipe_handle_poll`, and `papr_hvpipe_handle_release`. RTAS wrappers are `rtas_ibm_receive_hvpipe_msg` and `rtas_ibm_send_hvpipe_msg`. Event handling uses `hvpipe_event_interrupt`, `papr_hvpipe_work_fn`, `set_hvpipe_sys_param`, `enable_hvpipe_IRQ`, and exported `hvpipe_migration_handler`.

## Control Flow
Init checks RTAS properties/tokens, allocates an ordered workqueue, registers the HVPIPE event IRQ, creates the miscdevice, and enables the firmware sysparm. Users open the miscdevice, issue create-handle ioctl with an HMC source id, then read/write/poll on the returned anonymous inode. Incoming event interrupts parse RTAS error-log HVPIPE sections, find a matching source, set status flags and wake waiters, or queue a worker to drain unmonitored messages. Reads return a small header plus payload and clear pending state; writes build a PAPR buffer-list and issue send.

## State And Persistence
Runtime state includes global source list, per-source waitqueues and status flags, global feature enable state, event buffer, workqueue, work item, and RTAS token. No durable filesystem state is written; firmware pipe enablement is controlled through a PAPR system parameter.

## Dependencies And Integration Points
Depends on RTAS send/receive/check-exception calls, RTAS work areas, PAPR sysparm, event-source IRQ registration, anonymous inodes, miscdevice, uapi HVPIPE structures, and mobility's suspend/resume notifications.

## Risks And Edge Cases
Only one process may own a source. If user space is not listening, messages are drained to avoid blocking the single partition pipe. Migration disables the feature and makes operations fail or poll hang up until resumed. User buffer sizes are capped to one 4048-byte payload plus header. Event parsing assumes the RTAS error log contains the HVPIPE section.

## Test Signals
Test miscdevice creation only when firmware advertises capability, create-handle validation, duplicate source rejection, read/write bounds, poll wakeups, lost-connection events, unmonitored message drain, release with pending payload, migration suspend/resume, and RTAS error mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-hvpipe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-hvpipe.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-hvpipe.h

## Purpose
Defines internal HVPIPE constants, event/source state structures, migration actions, and the pSeries migration hook declaration.

## Important APIs, Types, And Functions
Defines `HVPIPE_HMC_ID_MASK`, `HVPIPE_MAX_WRITE_BUFFER_SIZE`, `RTAS_HVPIPE_CLOSED`, `HVPIPE_HDR_LEN`, `enum hvpipe_migrate_action`, `struct hvpipe_source_info`, `struct hvpipe_event_buf`, and `hvpipe_migration_handler`.

## Control Flow
No runtime control flow is present. The declarations guide `papr-hvpipe.c` and `mobility.c` interactions.

## State And Persistence
`struct hvpipe_source_info` describes per-source runtime list membership, status, source id, and poll waitqueue. `struct hvpipe_event_buf` mirrors the firmware event payload. The header itself stores no state.

## Dependencies And Integration Points
Depends on list and waitqueue types through including translation units. It links the HVPIPE driver with partition migration code and the uapi HVPIPE header's message flags/header structure.

## Risks And Edge Cases
The source-id mask supports only HMC-style ids in the current driver. The comment documents the source id format; mismatched firmware encoding would break filtering in ioctl/event paths.

## Test Signals
Compile coverage for HVPIPE and mobility builds, plus runtime source-id validation and event decoding, are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-hvpipe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-indices.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-indices.c

## Purpose
Implements `/dev/papr-indices`, exposing PAPR sensor/indicator index retrieval and dynamic sensor/indicator get/set operations to userspace.

## Important APIs, Types, And Functions
The sequence retrieval path uses `struct rtas_get_indices_params`, `rtas_ibm_get_indices`, `indices_sequence_begin`, `indices_sequence_end`, `indices_sequence_fill_work_area`, `papr_indices_create_handle`, and `papr_indices_handle_read`. Dynamic operations use `papr_dynamic_indice_buf_from_user`, `papr_dynamic_indicator_ioc_set`, and `papr_dynamic_sensor_ioc_get`. The miscdevice ioctl dispatcher is `papr_indices_dev_ioctl`.

## Control Flow
For `PAPR_INDICES_IOC_GET`, user input selects sensor versus indicator and type. The code builds a `papr_rtas_sequence`, serializes the RTAS sequence under `rtas_ibm_get_indices_lock`, accumulates complete fixed-size work-area pages through common PAPR blob helpers, and returns an anonymous fd for read/seek/release. Dynamic sensor and indicator ioctls copy a location-code block from user space, validate NULL termination, build an RTAS work area, issue the appropriate RTAS call under its function lock, and return or store state.

## State And Persistence
The indices retrieval result is immutable blob data attached to an anonymous file until release. Dynamic indicator sets persist in platform firmware/device state. There is no kernel durable storage.

## Dependencies And Integration Points
Depends on RTAS work areas and function locks, PAPR common sequence helpers, miscdevice/ioctl/uaccess, uapi `papr-indices` structures, and PAPR RTAS functions `ibm,get-indices`, `ibm,set-dynamic-indicator`, and `ibm,get-dynamic-sensor-state`.

## Risks And Edge Cases
`ibm,get-indices` does not report bytes written, so each successful call appends the full fixed work-area size and read requires at least that size. RTAS `RTAS_SEQ_START_OVER` maps to `-EAGAIN` and is retried by common sequence code. Location-code strings must be terminated and length includes the NULL. Indicator/sensor absence maps to `-EOPNOTSUPP`.

## Test Signals
Test device registration with missing and present RTAS tokens, sequence retry on start-over, multi-buffer reads and llseek, too-small read buffers, malformed location strings, dynamic sensor get, dynamic indicator set with read-only fd rejection, and RTAS hardware/parameter errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-indices.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-phy-attest.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-phy-attest.c

## Purpose
Implements `/dev/papr-physical-attestation`, allowing userspace to submit a physical attestation command and read the complete RTAS response through an fd-backed blob.

## Important APIs, Types, And Functions
Key pieces are `struct rtas_phy_attest_params`, `rtas_physical_attestation`, `phy_attest_sequence_begin`, `phy_attest_sequence_end`, `phy_attest_sequence_fill_work_area`, `papr_phy_attest_create_handle`, `papr_phy_attest_dev_ioctl`, and the common read/seek/release handlers from `papr-rtas-common.c`.

## Control Flow
The ioctl copies a `papr_phy_attest_io_block` from userspace, derives the command length, and constructs a `papr_rtas_sequence`. The begin callback locks the physical-attestation RTAS lock, allocates a 4K work area, copies the command into it, and initializes sequence state. The work callback calls RTAS until more-data or complete states stop, appending only the reported bytes. The common setup helper returns an anonymous fd containing the immutable response blob.

## State And Persistence
State is per ioctl: allocated params, RTAS work area, sequence number, bytes written, and a blob attached to the returned fd. No durable storage is written. Firmware attestation state is accessed transiently.

## Dependencies And Integration Points
Depends on RTAS `ibm,physical-attestation`, RTAS work areas, `rtas_ibm_physical_attestation_lock`, uapi `papr-physical-attestation`, miscdevice/ioctl, and common PAPR RTAS sequence helpers.

## Risks And Edge Cases
The command length comes from a big-endian user-provided field and is copied into a 4K work area; bounds depend on the uapi structure size and firmware behavior. The code warns and aborts if firmware reports more bytes than the work area. A copy-from-user failure leaks the allocated params in this source as written because the early return occurs before sequence cleanup.

## Test Signals
Test missing RTAS token, valid multi-part attestation responses, invalid parameters, hardware errors, reported length exceeding work area, fatal signal interruption during common retries, copy-from-user failure, read/seek/release behavior, and repeated concurrent ioctls serialized by the RTAS lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-phy-attest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-platform-dump.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-platform-dump.c

## Purpose
Implements `/dev/papr-platform-dump`, a userspace interface for streaming platform dumps from the hypervisor and invalidating completed dumps.

## Important APIs, Types, And Functions
The core state is `struct ibm_platform_dump_params`. Major functions are `rtas_ibm_platform_dump`, `papr_platform_dump_handle_read`, `papr_platform_dump_handle_release`, `papr_platform_dump_invalidate_ioctl`, `papr_platform_dump_create_handle`, and `papr_platform_dump_dev_ioctl`. Global synchronization uses `platform_dump_list_mutex` and `platform_dump_list`.

## Control Flow
Userspace passes a dump tag to the miscdevice create-handle ioctl. The driver rejects duplicate in-progress tags, allocates params and a 4K work area, creates an anonymous fd, and adds the request to the list. Each read calls RTAS with the current dump tag and sequence numbers, copies returned bytes to userspace, and updates sequence/status. When firmware reports complete, the next read returns EOF and marks the local buffer length zero. A handle ioctl invalidates the completed dump by calling RTAS with a NULL buffer.

## State And Persistence
Each open dump fd owns RTAS sequence numbers, bytes returned, status, work area, and list membership. The hypervisor retains the dump until userspace invalidates it after complete retrieval. Kernel state is freed on fd release.

## Dependencies And Integration Points
Depends on RTAS `ibm,platform-dump`, RTAS work areas, anonymous inodes, miscdevice/ioctl/read handlers, and uapi `papr-platform-dump` definitions.

## Risks And Edge Cases
Duplicate dump tags are blocked to avoid interleaving one dump stream. Reads require at least 1 KiB and are capped to the 4K work area. Firmware-reported bytes larger than the user buffer are treated as a kernel/firmware bug and fail. Invalidating before complete returns `-EINPROGRESS`; mismatched dump tags return `-EINVAL`.

## Test Signals
Test create/read/invalidate/release with complete and multi-read dumps, duplicate dump tag rejection, small read buffers, unauthorized and hardware RTAS errors, invalidation before EOF, mismatched invalidation tag, and cleanup when userspace closes without invalidating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-platform-dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-rtas-common.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-rtas-common.c

## Purpose
Provides common helpers for PAPR RTAS calls that must run a serialized multi-call sequence, collect all result chunks, and expose the immutable result through an anonymous read-only fd.

## Important APIs, Types, And Functions
Blob helpers are `papr_rtas_blob_has_data`, `papr_rtas_blob_free`, `papr_rtas_blob_extend`, and `papr_rtas_blob_generate`. Sequence helpers are `papr_rtas_sequence_set_err`, `papr_rtas_run_sequence`, `papr_rtas_retrieve`, and `papr_rtas_sequence_should_stop`. File interface helpers are `papr_rtas_setup_file_interface`, `papr_rtas_common_handle_read`, `papr_rtas_common_handle_release`, and `papr_rtas_common_handle_seek`.

## Control Flow
Callers provide a `struct papr_rtas_sequence` with optional begin/end callbacks and a work callback. `papr_rtas_retrieve` repeatedly runs complete sequences until success, hard error, or fatal signal; `-EAGAIN` represents firmware start-over. A run invokes begin, repeatedly calls work while it returns data, appends each chunk with `kvrealloc`, invokes end, then either returns the blob or an error. `papr_rtas_setup_file_interface` wraps the completed blob in an anonymous read-only fd.

## State And Persistence
State is per sequence and per returned file: sequence error state, caller params, allocated blob data, and fd private data. Data persists only until the anonymous file is released.

## Dependencies And Integration Points
Used by `papr-indices.c` and `papr-phy-attest.c`, and suitable for similar PAPR sequence calls such as VPD. It depends on anonymous inodes, file descriptor allocation, scheduler signal checks, slab/vmalloc allocation, and simple/fixed-size file helpers.

## Risks And Edge Cases
The first recorded sequence error is preserved. Empty blobs are treated as allocation/data failure. Callers must provide correct locking in begin/end if firmware disallows interleaving. `papr_rtas_blob_generate` returns `ERR_PTR(-EINVAL)` if no work callback is present but otherwise returns NULL for empty/error, which the run path maps to `-ENOMEM` unless the sequence recorded another error.

## Test Signals
Test successful single and multi-chunk sequences, start-over retry, hard errors, fatal signal interruption, missing work callback, empty result, allocation failure, read with offsets, llseek bounds, and release freeing blob memory exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-rtas-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-rtas-common.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-rtas-common.h

## Purpose
Declares the shared PAPR RTAS sequence and blob interface used by fd-oriented RTAS retrieval drivers.

## Important APIs, Types, And Functions
Defines sequence return constants `RTAS_SEQ_COMPLETE`, `RTAS_SEQ_MORE_DATA`, and `RTAS_SEQ_START_OVER`; `struct papr_rtas_blob`; and `struct papr_rtas_sequence`. Declares blob, sequence, setup, read, release, and seek helpers implemented in `papr-rtas-common.c`.

## Control Flow
No runtime flow is implemented in the header. The callback fields in `struct papr_rtas_sequence` define the expected begin/end/work lifecycle used by common code.

## State And Persistence
`struct papr_rtas_blob` represents immutable result data owned by a file handle. `struct papr_rtas_sequence` carries mutable in-progress error state and caller params. The header itself stores no state.

## Dependencies And Integration Points
Depends on Linux types and file operation types through translation units. It is included by PAPR miscdevice drivers that retrieve multi-call RTAS results.

## Risks And Edge Cases
Callers must use `papr_rtas_sequence_set_err` to preserve first-error semantics and must ensure callbacks allocate/free any RTAS work area even across retries. The struct names in comments say `papr_sequence`, but the actual exported type is `papr_rtas_sequence`.

## Test Signals
Compile coverage across all users, plus runtime tests in indices and physical-attestation paths, validate that the declared callback contract matches implementation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-rtas-common.h -->
