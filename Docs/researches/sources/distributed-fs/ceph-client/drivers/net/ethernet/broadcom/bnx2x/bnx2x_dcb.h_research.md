# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_dcb.h

## Purpose
Defines the DCB/DCBX data model shared by the `bnx2x` core, DCB implementation, and optional DCB netlink support. It provides the software-side structures for application priorities, COS/ETS configuration, PFC masks, admin LLDP/DCBX configuration, and helper data used while converting negotiated CEE priority groups into hardware COS entries.

## Important APIs, Types, and Functions
Important public structs include `bnx2x_dcbx_app_params`, `bnx2x_dcbx_cos_params`, `bnx2x_dcbx_pg_params`, `bnx2x_dcbx_pfc_params`, `bnx2x_dcbx_port_params`, `bnx2x_config_lldp_params`, `bnx2x_admin_priority_app_table`, and `bnx2x_config_dcbx_params`. Internal algorithm helpers are represented by `cos_entry_help_data`, `cos_help_data`, `pg_entry_help_data`, and `pg_help_data`.

Important constants include `LLFC_DRIVER_TRAFFIC_TYPE_MAX`, `BNX2X_MAX_COS_SUPPORT`, `DCBX_COS_MAX_NUM`, strict-priority sentinel values, admin overwrite constants, `BNX2X_IS_ETS_ENABLED`, app protocol IDs for FCoE and iSCSI, PFC quanta/threshold values, illegal PG and invalid bandwidth sentinels, and macros that split priority masks into pauseable and non-pauseable sets.

The header declares `bnx2x_dcbx_update`, `bnx2x_dcbx_init_params`, `bnx2x_dcbx_set_state`, `bnx2x_dcbx_set_params`, `bnx2x_dcbx_pmf_update`, `bnx2x_dcbx_stop_hw_tx`, and `bnx2x_dcbx_resume_hw_tx`. Under `BCM_DCBNL`, it declares `bnx2x_dcbnl_ops` and `bnx2x_dcbnl_update_applist`.

## Control Flow
There is no direct runtime control flow in the header. Its macros drive branch decisions in `bnx2x_dcb.c`, especially pauseability checks such as `IS_DCBX_PFC_PRI_ONLY_PAUSE`, `IS_DCBX_PFC_PRI_ONLY_NON_PAUSE`, `IS_DCBX_PFC_PRI_MIX_PAUSE`, and `DCBX_IS_PFC_PRI_SOME_PAUSE`. The state enum gives the DCBX flow labels used by the attention/rtnl sequence: negotiated result received, TX paused for hardware reprogramming, and TX released.

## State and Persistence Behavior
The structs declared here are embedded in `struct bnx2x` and persisted for the lifetime of the PF instance. `bnx2x_config_dcbx_params` represents admin settings that can be copied into the firmware admin MIB. `bnx2x_dcbx_port_params` represents negotiated/effective runtime state. Sentinel values such as `BNX2X_DCBX_CONFIG_INV_VALUE`, `INVALID_TRAFFIC_TYPE_PRIORITY`, `DCBX_ILLEGAL_PG`, and `DCBX_INVALID_COS_BW` are part of the in-memory state contract.

## Dependencies and Integration Points
The header includes `bnx2x_hsi.h` for firmware-facing DCBX limits and MIB field helpers. It is consumed by `bnx2x_dcb.c`, `bnx2x.h`, `bnx2x_main.c`, and any build that wires DCBNL operations into `net_device`. Constants here must remain aligned with firmware CEE/DCBX definitions, hardware COS limits, and the queue setup path that maps priorities to COS/TC values.

## Risks
This header is hardware/firmware ABI-adjacent. Wrong COS limits, priority masks, invalid sentinels, or app protocol constants will make the implementation program bad PFC/ETS state while still compiling. The `bnx2x_dcbx_update` declaration appears without a matching definition in this source subset, which is a maintenance signal for stale API declarations or out-of-tree build variation. Macro type widths also matter because several masks are narrowed to `u8` in the implementation.

## Test Signals
Compile coverage with and without `BCM_DCBNL`, DCB-enabled and DCB-disabled probe paths, FCoE/iSCSI app priority mapping, PFC priority masks, E2/E3A0 versus E3B0 COS counts, and dcbnl operations that read/write `bnx2x_config_dcbx_params` are the primary validation signals.
