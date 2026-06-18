# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_dcb_lib.h

## Purpose
`ice_dcb_lib.h` exposes the runtime DCB helper API to the rest of the ice driver and provides no-op or conservative fallbacks when `CONFIG_DCB` is disabled. It bridges core PF/VSI/ring code with the DCB library implementation.

## Important APIs, Types, And Functions
With `CONFIG_DCB`, it defines DCB return/status constants (`ICE_DCB_HW_CHG_RST`, `ICE_DCB_NO_HW_CHG`, `ICE_DCB_HW_CHG`) and declares the DCB runtime functions for initialization, config apply, rebuild, VSI/ring TC setup, stats update, PFC hang diagnosis, VLAN priority preparation, RDMA QoS export, and LLDP MIB-change processing. Inline helpers include `ice_find_q_in_range()`, `ice_set_cgd_num()`, `ice_is_dcb_active()`, and `ice_get_pfc_mode()`.

Without `CONFIG_DCB`, it returns one traffic class, marks DCB inactive, rejects PF DCB initialization/configuration with `-EOPNOTSUPP`, sets default RDMA QoS to one TC at 100 percent bandwidth, and makes stats/reconfig/MIB handlers no-ops.

## Control Flow
The header lets core paths call DCB helpers regardless of build option. The compile-time branch determines whether those calls perform real DCB work or collapse to default single-TC behavior. `ice_is_dcb_active()` abstracts whether firmware LLDP or DCB tagging currently makes DCB operational.

## State And Persistence
No persistent state is stored in the header. Inline helpers read or set fields in caller-owned structures: `tlan_ctx->cgd_num`, PF flags, and `local_dcbx_cfg.pfc_mode`. Fallbacks set transient VSI/RDMA QoS defaults.

## Dependencies And Integration Points
It includes `ice.h`, `ice_base.h`, and `ice_lib.h`, so it is tightly coupled to PF, VSI, Tx context, ring, and IIDC RDMA types. It is consumed by transmit setup, VSI configuration, reset, DCBNL, and event-processing code.

## Risks
The non-DCB stubs must preserve core driver behavior without silently advertising unavailable DCB features. One signature inconsistency is worth watching: the non-DCB `ice_tx_prepare_vlan_flags_dcb()` stub is declared `int` while the real function returns `void`; build coverage likely catches this depending on call sites and compiler diagnostics. Inline state readers assume `pf->hw.port_info` exists.

## Test Signals
Build both `CONFIG_DCB=y` and disabled variants, run sparse/compile checks for prototype consistency, validate single-TC fallback behavior, and verify callers do not rely on side effects from stubbed functions.
