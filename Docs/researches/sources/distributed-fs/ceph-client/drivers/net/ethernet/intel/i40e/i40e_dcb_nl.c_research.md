# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_dcb_nl.c

## Purpose

`i40e_dcb_nl.c` implements the kernel DCBNL interface for i40e when `CONFIG_I40E_DCB` is enabled. It exposes IEEE and CEE DCB operations to user space, mirrors firmware-negotiated app TLVs into the DCB app table, and routes host-managed DCB changes through `i40e_hw_dcb_config()`.

## Important APIs, Types, And Functions

- IEEE getters/setters: `i40e_dcbnl_ieee_getets()`, `i40e_dcbnl_ieee_getpfc()`, `i40e_dcbnl_ieee_setets()`, `i40e_dcbnl_ieee_setpfc()`, `i40e_dcbnl_ieee_setapp()`, and `i40e_dcbnl_ieee_delapp()`.
- CEE operations cover state, PG Tx mappings and bandwidth, PFC per-priority settings, capabilities, TC count queries, PFC state, and app lookup.
- `i40e_dcbnl_cee_set_all()` commits staged CEE config from `pf->tmp_cfg`.
- `i40e_dcbnl_setdcbx()` switches host DCBX mode between IEEE and CEE while rejecting firmware-managed and mixed modes.
- `dcbnl_ops` binds the file’s functions into `struct dcbnl_rtnl_ops`.
- `i40e_dcbnl_set_all()` pushes negotiated firmware DCB apps into the netdevice app table and sends `dcbnl_ieee_notify()`.
- `i40e_dcbnl_flush_apps()` removes stale app entries from all VSIs when the DCB configuration changes.

## Control Flow

User-space DCBNL calls enter through `dcbnl_ops`. Most write paths first check whether the PF supports the requested DCBX version and whether firmware LLDP management owns DCBX; firmware-managed modes reject host writes. IEEE setters copy `hw.local_dcbx_config` into `pf->tmp_cfg`, modify the requested ETS/PFC/app fields, and call `i40e_hw_dcb_config()`. CEE setters generally stage fields in `pf->tmp_cfg`, with `setall` performing the commit.

Firmware-negotiated DCB updates call `i40e_dcbnl_set_all()` to add app entries only when DCB is enabled, host DCB is not active, MFP restrictions allow it, and the app’s traffic class is enabled on the VSI. App flush compares old and new configs and deletes removed entries from every netdev-backed VSI.

## State And Persistence

State is held in `pf->dcbx_cap`, PF flags such as `I40E_FLAG_DCB_ENA`, `pf->hw.local_dcbx_config`, `pf->hw.desired_dcbx_config`, and `pf->tmp_cfg`. Netdevice DCB app state is maintained through `dcb_ieee_setapp()` and `dcb_ieee_delapp()`. Changes become hardware/firmware state only after `i40e_hw_dcb_config()` succeeds.

## Dependencies And Integration Points

The file depends on `<net/dcbnl.h>`, `i40e.h`, the i40e PF/VSI/netdev mapping helpers, DCB core helpers, `i40e_hw_dcb_config()`, and firmware/driver flags for DCB capability and MFP state. It is compiled out unless `CONFIG_I40E_DCB` is enabled.

## Risks

- Write paths return generic `-EINVAL` or DCBNL status errors, so callers can lose detailed firmware failure context except for logged AQ status.
- `pf->tmp_cfg` is shared staging state; concurrent DCBNL operations rely on higher-level DCBNL/RTNL serialization.
- `i40e_dcbnl_ieee_delapp()` intentionally keeps one firmware-required app, which can surprise user space that expects complete deletion.
- CEE Rx bandwidth and PG setters are no-ops because hardware does not support them, but the interface still exposes callbacks.

## Test Signals

Exercise `dcbtool`/`lldptool` or DCBNL netlink tests for IEEE and CEE modes, host versus firmware-managed rejection, app add/delete/flush behavior, MFP non-iSCSI suppression, and failure paths from `i40e_hw_dcb_config()`. Trace or assert emitted DCBNL notifications after firmware-negotiated app updates.
