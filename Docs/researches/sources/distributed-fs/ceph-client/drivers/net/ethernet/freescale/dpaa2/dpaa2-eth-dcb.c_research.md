# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-eth-dcb.c

## Purpose
This optional DPAA2 Ethernet sidecar implements DCB netlink operations for IEEE Priority Flow Control.

## Important APIs, Types, and Functions
The exported object is `dpaa2_eth_dcbnl_ops`. `dpaa2_eth_dcbnl_ieee_getpfc()` reports stored PFC state when PFC pause is enabled. `dpaa2_eth_dcbnl_ieee_setpfc()` validates unsupported fields, updates DPNI link options, configures congestion notifications by priority via `dpaa2_eth_set_pfc_cn()`, stores `priv->pfc`, updates `priv->pfc_enabled`, and adjusts RX taildrop. `dpaa2_eth_dcbnl_getdcbx()`, `setdcbx()`, and `getcap()` expose DCBX mode and capabilities.

## Control Flow
Userspace DCB changes enter through rtnetlink DCBNL ops. Setting PFC first rejects MBC/delay, skips no-op masks, warns if pause support is not enabled, toggles `DPNI_LINK_OPT_PFC_PAUSE` through `dpni_set_link_cfg()`, configures per-TC congestion thresholds, and updates driver state.

## State and Persistence
Runtime state is in `priv->pfc`, `priv->pfc_enabled`, `priv->dcbx_mode`, and Management Complex DPNI link/congestion configuration. No persistent storage is used.

## Dependencies and Integration Points
The file depends on `dpaa2-eth.h`, DCB netlink types, DPNI commands, link-state helpers, traffic-class count helpers, congestion threshold macros, and RX taildrop configuration from the main driver.

## Risks
`getcap()` reports `1 << (tc_count - 1)` for PFC TCs, which must match DCB expectations for advertised capability. PFC configuration may be accepted while pause is disabled, producing a warning but no immediate effect. Partial failure after link config but before local state update can leave hardware and software state divergent.

## Test Signals
Use `dcb pfc show/set`, test unsupported MBC/delay rejection, toggle pause and PFC combinations, verify DPNI congestion thresholds per TC, and test failure injection for `dpni_set_link_cfg()` and `dpni_set_congestion_notification()`.
