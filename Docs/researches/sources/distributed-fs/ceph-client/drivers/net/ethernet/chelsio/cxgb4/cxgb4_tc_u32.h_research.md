# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_u32.h

Purpose: exposes the cxgb4 TC u32 offload entry points and a capability helper.

Important APIs/types: `can_tc_u32_offload`, `cxgb4_config_knode`, `cxgb4_delete_knode`, `cxgb4_init_tc_u32`, and `cxgb4_cleanup_tc_u32`.

Control flow/state: `can_tc_u32_offload` gates offload on `NETIF_F_HW_TC` and initialized `adap->tc_u32`. The implementation owns all parser state and hardware filter state.

Dependencies/integration: includes `<net/pkt_cls.h>` and assumes `netdev2adap` plus `struct adapter` are available from core cxgb4 headers. TC dispatch in `cxgb4_main.c` calls these functions for `TC_SETUP_CLSU32`.

Risks: capability is per-netdev feature plus adapter table pointer; callers must avoid invoking config/delete after cleanup clears `adap->tc_u32`.

Test signals: TC setup dispatch with `NETIF_F_HW_TC` toggled, init failure fallback, and cleanup after active or absent u32 state.
