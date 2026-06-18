# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_dcb_nl.c

## Purpose
`ice_dcb_nl.c` implements Linux DCBNL operations for the ice driver. It maps userspace DCB requests and notifications to the driver's DCBX config model, supporting IEEE ETS/PFC, CEE state/PG/PFC/app interfaces, DCBX mode changes, DSCP APP mapping, and synchronization of firmware-learned APP TLVs to netdev DCB state.

## Important APIs, Types, And Functions
The main public entry points are `ice_dcbnl_setup()`, `ice_dcbnl_set_all()`, and `ice_dcbnl_flush_apps()`. Static DCBNL callbacks populate `struct dcbnl_rtnl_ops`: IEEE `getets/setets`, `getpfc/setpfc`, `setapp/delapp`; CEE state, PG, PFC, capability, app, and set-all operations; and DCBX get/set mode operations.

Key helpers include `ice_dcbnl_devreset()` for down/up resync after hardware-changing DCB updates, `ice_dcbnl_find_app()` to compare APP tables, and `ice_dcbnl_vsi_del_app()` to remove stale apps. DSCP app handling in `ice_dcbnl_setapp()` and `ice_dcbnl_delapp()` is the most stateful userspace path.

## Control Flow
`ice_dcbnl_setup()` attaches DCBNL ops to the VSI netdev only when the PF is DCB-capable, then seeds netdev app state via `ice_dcbnl_set_all()`. Getter callbacks copy local DCBX state and stats into kernel DCBNL structures. Setter callbacks generally reject changes when firmware LLDP/LLD-managed mode owns DCBX, when the requested standard is unsupported, or when the PF is bonded. Accepted changes update `desired_dcbx_cfg`, call `ice_pf_dcb_cfg()` under `tc_mutex`, and may reset the netdev if a hardware-changing update requires it.

DSCP APP setup only accepts `IEEE_8021QAZ_APP_SEL_DSCP`, requires HOST IEEE mode and feature support, validates DSCP and TC ranges, records the app through DCB core helpers, switches firmware PFC mode from VLAN to DSCP if needed, initializes default DSCP maps, applies the requested mapping, appends it to `desired_dcbx_cfg.app`, and commits through `ice_pf_dcb_cfg()`. Deleting the last DSCP mapping switches back to VLAN mode and default software DCB config.

## State And Persistence
The file mutates `pf->dcbx_cap`, `desired_dcbx_cfg`, `local_dcbx_cfg` through apply paths, `dscp_mapped` bitmap, DSCP map arrays, PFC config, ETS tables, and netdev DCB app state maintained by the kernel DCB subsystem. Firmware persistence is indirect via `ice_pf_dcb_cfg()` and `ice_set_dcb_cfg()`.

## Dependencies And Integration Points
It depends on `<net/dcbnl.h>`, `ice_dcb.h`, `ice_dcb_lib.h`, netdev open/close/state change APIs, bonding state (`pf->lag->bonded`), DCB app helpers (`dcb_ieee_setapp`, `dcb_ieee_delapp`, `dcb_getapp`), feature flags, and DCBNL notifications. It integrates userspace tools such as lldpad/iproute2 with firmware DCB and driver runtime reconfiguration.

## Risks
Mode gating is critical: allowing userspace changes while firmware LLDP manages DCBX would fight firmware state. DSCP mode has non-negotiated behavior and must not be mixed with unsupported app selectors. APP deletion shifts entries using `old_cfg` data after clearing `new_cfg`, which should be reviewed carefully for consistency. Several CEE setters update desired state without immediately committing until `setall`; userspace ordering matters. Netdev reset waits for reset-in-progress loops, so long resets can delay DCBNL calls.

## Test Signals
Run DCBNL userspace tests for IEEE ETS/PFC set/get, CEE set-all, DCBX mode changes, DSCP add/delete including last mapping, bonded PF rejection, firmware-managed rejection, unsupported selector rejection, netdev reset after hardware-changing updates, app notification after firmware MIB changes, and DCB-disabled build stubs through `ice_dcb_nl.h`.
