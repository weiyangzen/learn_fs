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
