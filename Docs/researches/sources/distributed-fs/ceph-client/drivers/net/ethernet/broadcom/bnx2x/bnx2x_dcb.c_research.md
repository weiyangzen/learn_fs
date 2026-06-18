# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_dcb.c

## Purpose
Implements Data Center Bridging support for the Broadcom/QLogic `bnx2x` Ethernet driver. The file translates firmware/MFW DCBX negotiation results from shared LLDP/DCBX MIBs into driver state, traffic-class mapping, priority flow control programming, ETS scheduling, firmware TX-start parameters, and optional DCB netlink callbacks.

## Important APIs, Types, and Functions
The exported runtime entry points are `bnx2x_dcbx_set_params`, `bnx2x_dcbx_set_state`, `bnx2x_dcbx_init_params`, `bnx2x_dcbx_init`, `bnx2x_dcbx_pmf_update`, `bnx2x_dcbx_stop_hw_tx`, and `bnx2x_dcbx_resume_hw_tx`. When `BCM_DCBNL` is enabled, it also exports `bnx2x_dcbnl_ops` and `bnx2x_dcbnl_update_applist`.

The MIB path uses `bnx2x_dcbx_read_mib`, `bnx2x_dcbx_read_shmem_neg_results`, and `bnx2x_dcbx_read_shmem_remote_mib` to copy local/remote LLDP MIBs from shared memory with prefix/suffix sequence-number validation. Feature extraction is split across `bnx2x_dcbx_get_ap_feature`, `bnx2x_dcbx_get_pfc_feature`, `bnx2x_dcbx_get_ets_feature`, and `bnx2x_get_dcbx_drv_param`.

COS construction is the densest part of the file. The `bnx2x_dcbx_get_num_pg_traf_type`, `bnx2x_dcbx_fill_cos_params`, E2/E3A0 two-COS helpers, E3B0 three-COS helpers, `bnx2x_dcbx_join_pgs`, and `bnx2x_dcbx_spread_strict_pri` functions convert CEE priority groups, strict-priority PG 15, application priorities, and PFC pauseability into `bp->dcbx_port_params.ets.cos_params[]`.

Hardware programming is handled by `bnx2x_pfc_set`, `bnx2x_pfc_clear`, `bnx2x_pfc_set_pfc`, `bnx2x_dcbx_update_ets_params`, `bnx2x_dcbx_2cos_limit_update_ets_config`, `bnx2x_dcbx_update_ets_config`, and `bnx2x_dcbx_fw_struct`.

## Control Flow
The normal negotiation flow starts when attention handling in `bnx2x_main.c` calls `bnx2x_dcbx_set_params(..., BNX2X_DCBX_STATE_NEG_RECEIVED)`. That state deletes old dcbnl app TLVs, optionally reads the remote MIB, reads local negotiated results, logs them, derives software DCB parameters, marks `DRV_FLAGS_DCB_CONFIGURED`, re-adds app TLVs, schedules TC setup through `bnx2x_schedule_sp_rtnl`, notifies peer functions in multi-function mode, and schedules TX stop.

After TX is stopped, `BNX2X_DCBX_STATE_TX_PAUSED` applies PFC, applies ETS, and reinitializes local congestion management. After TX resumes, `BNX2X_DCBX_STATE_TX_RELEASED` sends `DRV_MSG_CODE_DCBX_PMF_DRV_OK` to firmware and emits a CEE dcbnl notification when built with DCBNL.

Initialization flows through `bnx2x_dcbx_init_params`, which seeds default admin CEE settings, and `bnx2x_dcbx_init`, which validates DCB enablement, takes `HW_LOCK_RESOURCE_DCBX_ADMIN_MIB`, updates the admin MIB if requested, sends `DRV_MSG_CODE_DCBX_ADMIN_PMF_MSG`, and releases the lock after MFW has acknowledged the read. PMF migration uses `bnx2x_dcbx_pmf_update` to reload previous PMF negotiation output from shared memory.

## State and Persistence Behavior
Persistent driver state is mostly in `struct bnx2x`: `dcb_state`, `dcbx_enabled`, `dcbx_mode_uset`, `dcbx_config_params`, `dcbx_port_params`, `dcbx_local_feat`, `dcbx_remote_feat`, `dcbx_error`, `dcbx_remote_flags`, `prio_to_cos`, and incrementing `dcb_version`. Firmware-visible persistence is in shmem2 LLDP/DCBX offsets, local/remote MIBs, admin MIBs, and driver flags such as `DRV_FLAGS_DCB_CONFIGURED` and `DRV_FLAGS_DCB_MFW_CONFIGURED`.

Hardware state is programmed through link/PHY helpers and function ramrods: PFC changes update NIG/MAC/BRB through `bnx2x_update_pfc`; ETS changes call `bnx2x_ets_disabled`, `bnx2x_ets_bw_limit`, `bnx2x_ets_strict`, or `bnx2x_ets_e3b0_config`; TX stop/start uses `bnx2x_func_state_change`.

## Dependencies and Integration Points
This file depends on `bnx2x.h`, `bnx2x_cmn.h`, `bnx2x_dcb.h`, `bnx2x_hsi.h` LLDP/DCBX layout definitions, DCB netlink APIs, shared-memory access macros, register access macros, PHY locks, hardware locks, link setup, slowpath rtnl scheduling, and firmware ramrod state machinery. Main-driver integration is visible in `bnx2x_main.c`: DCBX attention events call `bnx2x_dcbx_set_params`, rtnl work calls TX stop/resume and TC setup, PMF changes call `bnx2x_dcbx_pmf_update`, probe initializes DCB state, and `dev->dcbnl_ops` is set to `bnx2x_dcbnl_ops`.

## Risks
The main risk is incorrect reduction of negotiated ETS/PFC data into hardware-supported COS layouts, especially the E2/E3A0 two-COS limit, E3B0 three-COS limit, strict-priority PG 15, mixed pauseable/non-pauseable groups, and application priority defaults. MIB reads rely on sequence-number stability and fixed shared-memory offsets; stale or partially updated firmware data can disable features or program wrong priorities. DCBNL setters modify admin config in memory but only apply it through `setall`, so tests must verify the full set/commit path. Hardware programming is serialized through PHY/HW locks and TX stop/resume sequencing; regressions here can affect live traffic, PFC losslessness, ETS bandwidth, or multi-function synchronization.

## Test Signals
Useful signals include DCBX negotiation with FCoE/iSCSI/default app TLVs, CEE peer reads through dcbnl, `dcbtool`/`lldptool` setall flows, PMF migration, multi-function link sync, TX stop/resume completion, PFC frame counters, ETS bandwidth behavior under traffic, `setup_tc` queue count changes, and error injection for missing shmem offsets, mismatched MIB sequence numbers, remote MIB errors, and recovery-state rejection.
