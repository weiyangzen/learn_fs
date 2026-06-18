# Research: subset-b-004599

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_dev.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_dev.c

## Purpose
`qed_dev.c` is the central PF/VF hardware lifecycle and resource-management implementation for the QLogic/Marvell FastLinQ `qed` core driver. It prepares PCI BAR access, discovers chip/MFW/NVM capabilities, negotiates firmware load ownership, allocates and initializes shared driver resources, programs init-tool runtime data, starts and stops PF/VF hardware, maps relative resource identifiers to firmware-global identifiers, manages LLH classification filters, performs doorbell recovery, programs queue coalescing, and applies PF/vport bandwidth policies. It also integrates storage and RDMA personalities by sizing queue-manager resources and calling protocol-specific alloc/setup/free hooks.

## Important APIs, Types, And Functions
The doorbell recovery path uses `struct qed_db_recovery_entry` to track a doorbell address, backing data pointer, width, address space, and owning hwfn. `qed_db_recovery_add()`, `qed_db_recovery_del()`, `qed_db_recovery_execute()`, `qed_db_recovery_setup()`, and `qed_db_recovery_teardown()` maintain per-hwfn recovery lists under `db_recovery_info.lock` and replay 32-bit or 64-bit doorbells with `wmb()` barriers.

The LLH classification path defines local filter structs and `struct qed_llh_info`, allocated from `cdev->ppfid_bitmap`. `qed_llh_add_mac_filter()`, `qed_llh_remove_mac_filter()`, `qed_llh_add_protocol_filter()`, `qed_llh_remove_protocol_filter()`, `qed_llh_clear_all_filters()`, `qed_llh_set_ppfid_affinity()`, and `qed_llh_set_roce_affinity()` keep a shadow table with reference counts and then program NIG LLH registers, sometimes by PF pretend and DMAE for non-native PPFID rows.

Core initialization APIs exported through `qed_dev_api.h` are implemented here: `qed_init_dp()`, `qed_init_struct()`, `qed_resc_alloc()`, `qed_resc_setup()`, `qed_resc_free()`, `qed_hw_prepare()`, `qed_hw_init()`, `qed_hw_stop()`, `qed_hw_stop_fastpath()`, `qed_hw_start_fastpath()`, and `qed_hw_remove()`. `qed_hw_prepare_single()` is the per-hwfn discovery step. `qed_hw_init_common()`, `qed_hw_init_port()`, and `qed_hw_init_pf()` correspond to firmware load scopes returned by MCP. `qed_final_cleanup()` asks firmware to clean PF/VF remnants before a non-engine load.

Queue-manager setup is driven by `qed_get_pq_flags()`, the `qed_init_qm_get_*()` sizing helpers, `qed_init_qm_info()`, `qed_alloc_qm_data()`, and `qed_qm_reconf()`. `qed_get_cm_pq_idx*()` return TX PQ indices for L2, VF, offload, low-latency, and multi-CoS callers.

Resource discovery and defaults are handled by `qed_hw_get_resc()`, `qed_hw_set_soft_resc_size()`, `qed_hw_set_resc_info()`, `qed_hw_get_dflt_resc()`, `qed_hw_get_ppfid_bitmap()`, `qed_hw_set_feat()`, and `qed_hw_get_resc_name()`. Device and NVM discovery use `qed_get_dev_info()`, `qed_get_hw_info()`, `qed_hw_get_nvm_info()`, `qed_get_num_funcs()`, `qed_hw_info_port_num()`, and `qed_get_eee_caps()`.

Runtime service APIs include `qed_fw_l2_queue()`, `qed_fw_vport()`, `qed_fw_rss_eng()`, `qed_set_queue_coalesce()`, `qed_set_rxq_coalesce()`, `qed_set_txq_coalesce()`, `qed_configure_vport_wfq()`, `qed_configure_vp_wfq_on_link_change()`, `qed_configure_pf_max_bandwidth()`, `qed_configure_pf_min_bandwidth()`, `qed_clean_wfq_db()`, `qed_device_num_ports()`, and `qed_set_fw_mac_addr()`.

## Control Flow
The normal PF bring-up sequence begins with `qed_init_struct()` setting hwfn backpointers, ids, DMAE mutexes, active flags, and cache defaults. `qed_hw_prepare()` initializes init metadata, prepares hwfn 0, reads chip identity and CMT mode, and if necessary splits BAR0/BAR1 for hwfn 1. `qed_hw_prepare_single()` validates register access, reads function ids, allocates PTTs, initializes MCP command state, reads NVM and hardware capabilities, requests PF FLR on the leading hwfn, populates NVM shadows, and allocates init runtime arrays.

After discovery, `qed_resc_alloc()` allocates software resources per hwfn. It sets up doorbell recovery, context manager state, PF context parameters, QM tables, ILT layout, context tables, SPQ/EQ/ConSQ, interrupts, SR-IOV, L2, optional LL2, FCoE/iSCSI/NVMeTCP/RDMA structures, DMAE, DCBX, debug user data, LLH shadow tables, and reset statistics. On any allocation failure it falls through to `qed_resc_free()` to unwind already-created resources. `qed_resc_setup()` then initializes allocated objects, reads the MCP mailbox shadow, registers the common EQE callback, and calls protocol setup hooks.

`qed_hw_init()` is the firmware load and hardware programming phase. For PFs it loads firmware data, calculates the init `hw_mode`, sets VLAN ethertype runtime registers when required, sends `qed_mcp_load_req()`, clears recovery state, updates MCP capabilities, performs final cleanup for function/port loads, clears PGLUE errors, enables PFID master transactions, allocates firmware overlay memory, and runs one or more init phases based on the MCP load code. Engine loads run common initialization, port loads run port initialization, and all supported loads run PF initialization. PF init programs protocol search bits, runs PF and QM_PF phases, initializes interrupts, computes the doorbell BAR/DPI layout, initializes LLH, optionally enables interrupts, and sends the PF start ramrod. The function then sends load done, triggers DCBX/OEM updates, publishes firmware version/MTU/driver state/eswitch state to MCP, and marks `hw_init_done`.

Stop and removal are layered. `qed_hw_stop_fastpath()` gates ingress, disables parser searches, and clears fastpath interrupt runtime state while preserving slowpath. `qed_hw_start_fastpath()` reopens ingress and restores RDMA parser search if needed. Full `qed_hw_stop()` sends unload request, synchronizes slowpath IRQs, sends PF stop, gates NIG, disables protocol searches, stops timers, disables attentions, disables DORQ/QM PF blocks, removes primary LLH MAC filters, sends unload done, and clears PFID master enable after all hwfns have stopped. `qed_hw_remove()` updates driver state to not loaded, frees init/PTT/MCP structures, releases VF state, frees IOV hardware info, and frees NVM shadows. `qed_resc_free()` separately releases software resources allocated by `qed_resc_alloc()`.

## State And Persistence Behavior
Most state is in-memory driver state anchored at `struct qed_dev` and `struct qed_hwfn`: `hw_info`, `qm_info`, `mcp_info`, `db_recovery_info`, `p_llh_info`, protocol-specific pointers, resource start/count arrays, feature counts, flags, and link/bandwidth data. The file persists selected state into device firmware/shared memory via MCP commands, into hardware registers via GRC/PTT writes, and into init-tool runtime arrays via `STORE_RT_REG*()` before `qed_init_run()`. NVM values are read but not permanently modified here except for management updates such as storm firmware version, driver state, MTU, and eswitch mode.

Doorbell recovery entries persist only while their owning queues/entities are registered. LLH shadow state mirrors hardware filters and uses reference counts to avoid removing filters still requested by multiple callers. QM and WFQ state persists in `p_hwfn->qm_info`; link-change reconfiguration recomputes hardware WFQ values from the saved per-vport `wfq_data`. Resource discovery persists MCP-provided or default resource ranges in `RESC_NUM/RESC_START`.

## Dependencies And Integration Points
This file is tightly integrated with the rest of the `qed` core: MCP mailbox (`qed_mcp_*`), init-tool operations (`qed_init_*`, `qed_qm_*`), context management (`qed_cxt_*`), interrupts/IGU (`qed_int_*`), slowpath (`qed_sp*`), DMAE (`qed_dmae_*`), SR-IOV (`qed_iov_*`, `qed_sriov_*`, `qed_vf_*`), L2/LL2, RDMA, FCoE, iSCSI, NVMeTCP, DCBX, debug, and register definitions. Public consumers call through `qed_dev_api.h`; protocol files such as `qed_fcoe.c` depend on PQ/resource mapping and lifecycle hooks in this file. `qed_main.c` drives these lifecycle methods during probe, load, unload, recovery, and client operation.

## Risks And Edge Cases
Hardware ordering is a primary risk. Doorbell replay depends on valid doorbell backing data and write barriers, and list membership bugs can replay stale data. LLH programming changes PF pretend state and must always restore the original PF; error paths in register programming or DMAE can leave shadow and hardware out of sync. Hardware init has many partial-failure exits: load-lock release is handled, but callers must still unwind resource and prepare layers in the correct order. PTT acquisition failures commonly return `-EAGAIN` or `-EBUSY` and must be propagated by callers.

Resource sizing is sensitive to MFW support. When MCP resource commands are unsupported, default allocations are used; mismatches with actual firmware or chip mode can produce later failures in QM, ILT, or protocol setup. Coalescing has a documented shared-status-block timer-resolution constraint that is not globally enforced here. WFQ is unsupported for CMT and has strict validation around one-percent minimums and total requested rates. Several paths skip deeper cleanup during `recov_in_prog`, so recovery flows must ensure subsequent load performs final cleanup.

## Test Signals
Useful test signals include probe/load/unload on PF and VF devices, CMT and non-CMT devices, BB and AH/K2 chips, and all supported personalities. Fault-injection should cover MCP command failures, PTT acquisition failure, insufficient BAR/DPI space, unsupported resource commands, ILT overcommit retry, allocation failures inside `qed_resc_alloc()`, and `qed_sp_pf_start/stop()` failures. Runtime tests should exercise LLH add/remove/refcount behavior, doorbell add/delete/replay, queue coalescing ranges, PF/vport bandwidth configuration, fastpath stop/start, and recovery load after a simulated fatal error. Debug logs from `DP_NOTICE/DP_ERR`, MCP load/unload responses, resource dumps, and hardware counters are the main observability signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_dev_api.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_dev_api.h

## Purpose
`qed_dev_api.h` is the internal API contract for the `qed` device lifecycle and low-level hardware services implemented mainly by `qed_dev.c` and related core files. It exposes initialization, resource allocation, hardware start/stop, PTT window management, DMAE copy helpers, chain allocation, firmware resource-id translation, LLH filter control, cleanup, queue coalescing, PFID enable, doorbell recovery, and resource-name helpers to other driver modules.

## Important APIs, Types, And Functions
Initialization and teardown declarations include `qed_init_dp()`, `qed_init_struct()`, `qed_resc_alloc()`, `qed_resc_setup()`, `qed_resc_free()`, `qed_hw_prepare()`, `qed_hw_init()`, `qed_hw_stop()`, `qed_hw_stop_fastpath()`, `qed_hw_start_fastpath()`, and `qed_hw_remove()`.

`enum qed_override_force_load`, `struct qed_drv_load_params`, and `struct qed_hw_init_params` describe MCP load behavior, crash-kernel role, engine-reset avoidance, lock timeout, tunnel configuration, interrupt mode, firmware data, and NPAR TX-switching policy. PTT APIs are `qed_ptt_acquire()`, `qed_ptt_acquire_context()`, and `qed_ptt_release()`.

DMA and memory-service declarations include `enum qed_dmae_address_type_t`, `qed_dmae_host2grc()`, `qed_dmae_grc2host()`, `qed_dmae_host2host()`, `qed_chain_alloc()`, and `qed_chain_free()`. Firmware-id mapping APIs include `qed_fw_l2_queue()`, `qed_fw_vport()`, and `qed_fw_rss_eng()`.

LLH-related declarations define `enum qed_eng`, `enum qed_llh_prot_filter_type_t`, `QED_LLH_DONT_CARE`, `qed_llh_get_num_ppfid()`, `qed_llh_set_ppfid_affinity()`, `qed_llh_set_roce_affinity()`, `qed_llh_add_mac_filter()`, `qed_llh_remove_mac_filter()`, `qed_llh_add_protocol_filter()`, and `qed_llh_remove_protocol_filter()`. Cleanup and runtime configuration APIs include `qed_final_cleanup()`, `qed_get_queue_coalesce()`, `qed_set_queue_coalesce()`, `qed_pglueb_set_pfid_enable()`, `qed_db_recovery_add()`, `qed_db_recovery_del()`, and `qed_hw_get_resc_name()`.

## Control Flow
The header encodes the expected lifecycle ordering without implementing it: callers prepare the device, allocate resources, set them up, initialize hardware, run fastpath operations, stop hardware, free resources, and finally remove prepare-time state. PTT acquisition functions are documented as entry/exit helpers around hardware register flows. DMAE functions expect a caller-owned PTT and optional parameter block. LLH and coalescing functions are intended as runtime operations after resource and hardware setup have made `cdev`, `p_hwfn`, and queue ids valid.

## State And Persistence Behavior
The header defines data passed across modules rather than persistent storage itself. `struct qed_drv_load_params` and `struct qed_hw_init_params` are short-lived input contracts for `qed_hw_init()`. LLH calls mutate the driver's LLH shadow and hardware registers. PTT calls allocate and release limited hardware windows. Doorbell recovery calls register pointers to caller-owned doorbell data; callers must keep those data objects alive until deletion. Queue coalescing and PFID enable declarations describe register-persistent hardware state controlled by implementations.

## Dependencies And Integration Points
The header includes Linux kernel types, `qed_chain.h`, `qed_if.h`, and `qed_int.h`, and depends on many forward-declared driver structs from `qed.h` and related includes. It is consumed by protocol implementations such as FCoE/iSCSI/RDMA/L2, main probe/remove code, interrupt code, and management/recovery paths. It is a boundary between feature modules and the hardware core, so changes here have broad compile-time and behavioral impact.

## Risks And Edge Cases
Because this is a shared internal contract, signature changes can break many `qed` modules. The comments capture important constraints that are easy to violate: PTT acquire/release pairing, atomic-context behavior for `qed_ptt_acquire_context()`, coalescing timer-resolution sharing across queues on one status block, PF/VF semantics for `qed_final_cleanup()`, and doorbell recovery ownership of `db_data`. The FCoE-disabled inline equivalents live in `qed_fcoe.h`, not here, so callers must respect feature guards from the implementation side.

## Test Signals
Compile coverage across `CONFIG_QED_FCOE`, SR-IOV, RDMA, and storage personalities is the first signal for this header. Runtime signals come from exercising each declared lifecycle phase, acquiring/releasing PTTs under normal and atomic context, DMAE copies, LLH filter add/remove, coalescing configuration, final cleanup, and doorbell recovery registration. Static analysis should check ownership and pairing of PTT and doorbell APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_dev_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_devlink.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_devlink.c

## Purpose
`qed_devlink.c` provides the `devlink` integration for the `qed` core. It registers a devlink instance, exposes firmware and board identity through `devlink info`, provides one runtime driver parameter for iWARP CMT mode, and creates a firmware-fatal health reporter capable of collecting a binary debug dump and initiating driver recovery.

## Important APIs, Types, And Functions
`enum qed_devlink_param_id` reserves `QED_DEVLINK_PARAM_ID_IWARP_CMT` after generic devlink ids. `struct qed_fw_fatal_ctx` carries an `enum qed_hw_err_type` to reporter dump context.

`qed_report_fatal_error()` is the external reporting entrypoint. If a firmware reporter exists, it calls `devlink_health_report()` with a fatal message and error context. `qed_fw_fatal_reporter_dump()` allocates a `vzalloc()` buffer sized by `qed_dbg_all_data_size()`, optionally sets `cdev->print_dbg_data` when invoked after a fatal event, collects debug data via `qed_dbg_all_data()`, and emits it with `devlink_fmsg_binary_pair_put()`. `qed_fw_fatal_reporter_recover()` delegates recovery to `qed_recovery_process()`.

`qed_fw_reporters_create()` and `qed_fw_reporters_destroy()` manage the `fw_fatal` health reporter. `qed_dl_param_get()` and `qed_dl_param_set()` read and write `cdev->iwarp_cmt`. `qed_devlink_info_get()` publishes board serial number from `hwfns[0].hw_info.part_num`, stored management firmware version from `common_dev_info.mfw_rev`, and running app firmware version from `common_dev_info.fw_*`. `qed_devlink_register()` allocates and registers devlink state; `qed_devlink_unregister()` reverses the setup.

## Control Flow
Registration starts in `qed_devlink_register()`: allocate devlink private storage, store `cdev`, register the `iwarp_cmt` parameter, default `cdev->iwarp_cmt` to false, create firmware health reporters, then call `devlink_register()`. Unregistration calls `devlink_unregister()`, destroys the reporter, unregisters params, and frees the devlink object.

Fatal reporting is asynchronous to normal lifecycle. A hardware error path calls `qed_report_fatal_error()`, devlink invokes the reporter dump callback when requested, and the recover callback invokes the driver's recovery process. Info queries are pull-based from userspace and read already-populated device information.

## State And Persistence Behavior
The devlink private object stores only `cdev` and the reporter pointer. The `iwarp_cmt` parameter persists in memory as `cdev->iwarp_cmt` for the life of the device and is runtime-changeable. Reporter dumps are transient vmalloc buffers. `cdev->print_dbg_data` is temporarily set based on whether dump context exists, but this function does not restore it, so later debug behavior depends on wider driver expectations.

## Dependencies And Integration Points
This file depends on Linux `devlink`, `devlink_health_reporter`, vmalloc, `qed_dbg_all_data*()`, `qed_recovery_process()`, and common device information populated during hardware prepare/init. `qed_main.c` wires these functions into the public common operations table as `.devlink_register`, `.devlink_unregister`, and `.report_fatal_error`. Userspace integration is through `devlink info`, `devlink param`, and `devlink health`.

## Risks And Edge Cases
Reporter creation failure is logged and tolerated by setting `fw_reporter` to `NULL`, so fatal errors may not produce devlink reports on low-memory or API failure paths. Dump allocation size is determined by firmware debug data size and can be large; allocation or collection failure aborts the dump. `qed_report_fatal_error()` always returns 0 even when no reporter exists. Parameter setting has no validation beyond the boolean type and may interact with hardware modes that are not active until other code observes `cdev->iwarp_cmt`.

## Test Signals
Tests should verify devlink registration/unregistration without leaks, runtime get/set of `iwarp_cmt`, `devlink info` content after successful hardware discovery, reporter creation failure handling, fatal error reporting with and without a reporter, dump allocation failure, debug data collection failure, and recover callback invocation of `qed_recovery_process()`. User-visible signals are devlink health events, binary dump presence, and firmware version strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_devlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_devlink.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_devlink.h

## Purpose
`qed_devlink.h` is the small internal declaration surface for the `qed` devlink integration. It lets the main driver register and unregister devlink state, create and destroy firmware health reporters, and report fatal hardware errors without exposing the implementation details in `qed_devlink.c`.

## Important APIs, Types, And Functions
The header declares `qed_devlink_register(struct qed_dev *cdev)`, `qed_devlink_unregister(struct devlink *devlink)`, `qed_fw_reporters_create(struct devlink *devlink)`, `qed_fw_reporters_destroy(struct devlink *devlink)`, and `qed_report_fatal_error(struct devlink *dl, enum qed_hw_err_type err_type)`. It includes `linux/qed/qed_if.h` for core qed types and `<net/devlink.h>` for the devlink object.

## Control Flow
The intended call flow is probe-side registration through `qed_devlink_register()`, optional reporter creation as part of registration, fatal-error reporting through `qed_report_fatal_error()` during error handling, and remove-side cleanup through `qed_devlink_unregister()`. The explicit reporter create/destroy declarations also allow code that already has a devlink object to manage health reporters independently, although current implementation creates them inside registration.

## State And Persistence Behavior
This header owns no state. The implementation stores state in devlink private data and in the associated `struct qed_dev`. Callers are responsible for retaining the returned `struct devlink *` and passing it back on unregister and fatal report paths.

## Dependencies And Integration Points
It is included by `qed_devlink.c` and by main/common operation wiring that exposes devlink support to the upper driver. Its dependency on netdev devlink APIs makes it kernel-version-sensitive if devlink function signatures change.

## Risks And Edge Cases
The declarations do not provide stubs for builds without devlink, implying the surrounding build always expects devlink support for this driver version. Callers must handle `ERR_PTR()` from register and `NULL` devlink in unregister. Fatal report callers should not assume the report produced a dump, because reporter creation may have failed.

## Test Signals
Compile coverage catches signature drift. Runtime signals are successful devlink registration, safe unregister on a valid pointer or `NULL`, and correct propagation of fatal report calls to the reporter when one exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_devlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_fcoe.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_fcoe.c

## Purpose
`qed_fcoe.c` implements the `qed` core support layer for FCoE offload. It allocates FCoE per-hwfn state, initializes FCoE task contexts, starts and stops the firmware FCoE function, manages connection handles and firmware CIDs, posts FCoE ramrods for connection offload and termination, exposes device and queue information to the upper FCoE client, gathers FCoE statistics, and exports a `struct qed_fcoe_ops` table to protocol drivers.

## Important APIs, Types, And Functions
`struct qed_fcoe_conn` is the central per-connection object. It stores list linkage, ownership behavior, driver and firmware connection ids, DMA/PBL addresses for SQ, transfer queue, confirmation/response queue, termination params, encoded source/destination MAC fields, FC payload/timer/vlan/queue settings, FC source/destination ids, flags, and default queue index.

Slowpath ramrod helpers include `qed_sp_fcoe_func_start()`, `qed_sp_fcoe_func_stop()`, `qed_sp_fcoe_conn_offload()`, and `qed_sp_fcoe_conn_destroy()`. Allocation and lifecycle helpers are `qed_fcoe_alloc()`, `qed_fcoe_setup()`, `qed_fcoe_free()`, `qed_fcoe_allocate_connection()`, `qed_fcoe_free_connection()`, `qed_fcoe_acquire_connection()`, and `qed_fcoe_release_connection()`.

Client-facing operation implementations include `qed_fill_fcoe_dev_info()`, `qed_register_fcoe_ops()`, `qed_fcoe_start()`, `qed_fcoe_stop()`, `qed_fcoe_acquire_conn()`, `qed_fcoe_release_conn()`, `qed_fcoe_offload_conn()`, `qed_fcoe_destroy_conn()`, `qed_fcoe_stats()`, and `qed_get_protocol_stats_fcoe()`. The exported module entrypoints are `qed_get_fcoe_ops()` and `qed_put_fcoe_ops()`.

## Control Flow
Core driver resource allocation calls `qed_fcoe_alloc()` for FCoE personalities, creating `p_hwfn->p_fcoe_info` and its free list. `qed_resc_setup()` later calls `qed_fcoe_setup()`, which initializes the lock and prepares every configured task context by zeroing it, setting timer logical-client valid bits, and marking FCoE task connection type.

The upper FCoE client obtains ops through `qed_get_fcoe_ops()`, calls `.fill_dev_info` to learn common device information, BDQ producer addresses, WWPN/WWNN, and CQ count, registers callbacks with `.register_ops`, and starts offload with `.start`. `qed_fcoe_start()` posts `FCOE_RAMROD_CMD_ID_INIT_FUNC`, sets `QED_FLAG_STORAGE_STARTED`, initializes `cdev->connections`, and optionally returns TID memory layout to the caller.

Connection setup starts with `.acquire_conn`, which allocates a hash wrapper, acquires a FCoE CID from the context manager, obtains or allocates a `qed_fcoe_conn`, computes `fw_cid`, inserts the wrapper into `cdev->connections`, and returns the doorbell address if requested. `.offload_conn` copies caller-provided queue DMA addresses, timers, MACs, FC ids, VLAN, flags, and default queue index into the connection and posts `FCOE_RAMROD_CMD_ID_OFFLOAD_CONN`. `.destroy_conn` sets the termination params DMA address and posts `FCOE_RAMROD_CMD_ID_TERMINATE_CONN`. `.release_conn` removes the hash entry, returns the connection to the free list, and releases the CID.

Function stop requires all connections to have been returned. `qed_fcoe_stop()` rejects stop when `cdev->connections` is non-empty, acquires a PTT, posts `FCOE_RAMROD_CMD_ID_DESTROY_FUNC`, clears the storage-started flag, and releases the PTT. `qed_fcoe_free()` is part of core resource teardown and frees cached connection DMA memory from the free list before freeing `p_fcoe_info`.

## State And Persistence Behavior
FCoE driver state is in `p_hwfn->p_fcoe_info`, the connection free list, `cdev->connections`, `QED_FLAG_STORAGE_STARTED`, protocol callback pointers in `cdev->protocol_ops.fcoe`, `cdev->ops_cookie`, and FCoE fields under `p_hwfn->pf_params.fcoe_pf_params`. Connection DMA pages for transfer and confirmation queues are allocated coherently and cached on the free list for reuse. CID ownership is persisted in the context manager until release. Firmware-visible state is created and destroyed through slowpath ramrods and task context memory.

Statistics are read directly from TSTORM and PSTORM memory through PTT reads and translated into `qed_fcoe_stats` or `qed_mcp_fcoe_stats`. `qed_get_protocol_stats_fcoe()` combines firmware counters with optional upper-client login-failure counters.

## Dependencies And Integration Points
This file depends on `qed_dev.c` for resource setup, FCoE personality detection, queue-manager PQ mapping, BDQ resources, PTT acquisition, and lifecycle calls. It uses context management (`qed_cxt_*`), slowpath queue APIs (`qed_sp_init_request()`, `qed_spq_post()`), LL2 common ops, MCP function WWN data, register address macros, storm context layouts, Linux DMA coherent allocation, kernel hash tables, and exported `linux/qed/qed_fcoe_if.h` client contracts. It is conditionally compiled through `CONFIG_QED_FCOE` with stubs in `qed_fcoe.h`.

## Risks And Edge Cases
The stop path refuses to stop while hash entries remain, so leaked upper-layer connection handles block clean shutdown. Connection objects are recycled on a free list and retain coherent DMA allocations; every acquire/release path must pair CID ownership and hash membership correctly. Some connection allocations are done outside the lock after CID acquisition, with explicit CID release on allocation failure. `qed_fcoe_release_connection()` always caches the connection rather than freeing it immediately, so `qed_fcoe_free()` must run to release DMA memory.

FCoE start allocates `tid_info` with `GFP_ATOMIC` and rolls back by calling stop on failure. Ramrod posting is synchronous blocking mode for the public operations, so firmware timeout/error behavior propagates directly to callers. BDQ producer address helpers return `NULL` and log when `QED_BDQ` was not allocated. Stats acquisition respects atomic context through `qed_ptt_acquire_context()`, but failure only logs and leaves the caller with zeroed or partial stats depending on the wrapper.

## Test Signals
FCoE coverage should include builds with `CONFIG_QED_FCOE=y/m` and disabled builds using stubs. Runtime tests should start/stop FCoE, request TID memory, acquire/release multiple connections, offload and destroy connections with representative queue DMA addresses, verify stop fails with active connections, verify free-list reuse, inject CID and DMA allocation failures, and validate stats reads. Hardware/firmware signals include FCoE init/offload/terminate/destroy ramrod completions, BDQ producer addresses, TSTORM/PSTORM counters, `QED_FLAG_STORAGE_STARTED`, and hash-table emptiness on stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_fcoe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_fcoe.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_fcoe.h

## Purpose
`qed_fcoe.h` declares the internal FCoE support hooks used by the `qed` core resource lifecycle and statistics paths. It also provides compile-time stubs when `CONFIG_QED_FCOE` is disabled, allowing the rest of the core driver to compile while treating FCoE allocation as unsupported.

## Important APIs, Types, And Functions
`struct qed_fcoe_info` holds a spinlock protecting connection resources and a `free_list` of reusable `struct qed_fcoe_conn` objects owned by the implementation. When FCoE is enabled, the header declares `qed_fcoe_alloc()`, `qed_fcoe_setup()`, `qed_fcoe_free()`, and `qed_get_protocol_stats_fcoe()`. When FCoE is disabled, `qed_fcoe_alloc()` returns `-EINVAL`, setup/free are no-ops, and protocol stats collection is a no-op.

## Control Flow
The core device flow calls these hooks from `qed_resc_alloc()`, `qed_resc_setup()`, `qed_resc_free()`, and MCP/statistics paths only when the hwfn personality is FCoE or when protocol stats are requested. The enabled implementation allocates per-hwfn state first, initializes task contexts during setup, frees cached connection resources during teardown, and reads protocol stats on demand. The disabled implementation short-circuits those flows.

## State And Persistence Behavior
The header defines the visible state container for FCoE connection-resource management. Actual persistent state lives in `p_hwfn->p_fcoe_info`, the connection free list, and firmware contexts managed by `qed_fcoe.c`. The disabled stubs do not allocate or mutate state.

## Dependencies And Integration Points
The header includes kernel list/slab/spinlock types, `linux/qed/qed_fcoe_if.h`, `qed_chain.h`, and internal core headers for `qed`, HSI, MCP, and slowpath structures. It is included by `qed_dev.c` and `qed_fcoe.c`, binding the generic device lifecycle to optional FCoE support.

## Risks And Edge Cases
Callers must not assume FCoE support is present; the disabled stub returns `-EINVAL` from allocation. Because `qed_fcoe_info.lock` protects connection resources, implementation paths that manipulate the free list must initialize the lock before use and avoid mixing unlocked hash-table state with locked free-list state. The stats stub silently leaves caller-provided stats unchanged, so callers should account for configuration.

## Test Signals
Compile tests should cover both enabled and disabled FCoE configurations. Enabled runtime signals include successful allocation/setup/free in the FCoE personality and non-empty statistics after traffic. Disabled tests should verify the core handles `qed_fcoe_alloc()` returning `-EINVAL` only when an FCoE personality is incorrectly requested without support and that non-FCoE builds do not reference missing implementation symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_fcoe.h -->
