# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_dcb_nl.c

## Purpose
`ixgbe_dcb_nl.c` implements ixgbe's Linux DCB netlink operations. It exposes CEE and IEEE DCBX controls to user space, stages configuration in temporary adapter DCB state, applies changed settings to hardware, manages traffic-class resets, handles PFC and ETS set/get operations, and integrates DCB application priority changes with FCoE and SR-IOV defaults.

## Important APIs, Types, And Functions
- `ixgbe_dcbnl_ops` exports the driver's `struct dcbnl_rtnl_ops` callbacks.
- `ixgbe_copy_dcb_cfg()` compares `adapter->temp_dcb_cfg` against `adapter->dcb_cfg`, copies changed PG/PFC settings, and returns a bitmap of affected subsystems.
- CEE callbacks include state, permanent hardware address, PG TX/RX set/get, bandwidth group set/get, PFC set/get, `setall`, capabilities, TC count, PFC state, app get, and DCBX mode get/set.
- `ixgbe_dcbnl_set_all()` applies staged CEE changes: recalculates credits, programs ETS, updates netdev priority-to-TC maps, applies PFC or fallback link flow control, updates RX drop behavior, and resets for app/FCoE changes when needed.
- IEEE callbacks include `ieee_getets`, `ieee_setets`, `ieee_getpfc`, `ieee_setpfc`, `ieee_setapp`, and `ieee_delapp`.
- `ixgbe_dcbnl_devreset()` serializes with `__IXGBE_RESETTING`, stops the netdev if running, rebuilds interrupt scheme, reopens the netdev, and clears reset state.
- `ixgbe_dcbnl_setdcbx()` validates host-managed single-version DCBX modes and initializes ETS/PFC defaults when switching modes.

## Control Flow
CEE configuration is staged by individual setters into `temp_dcb_cfg`. `setall` copies changes into active `dcb_cfg`, determines whether PG, PFC, or app UP changed, then applies only affected hardware paths. PG changes calculate TX/RX credits from current MTU and FCoE jumbo constraints, unpack arrays, call `ixgbe_dcb_hw_ets_config()`, and update `netdev_set_prio_tc_map()`. PFC changes either program DCB PFC or reenable normal link flow control.

IEEE ETS set allocates `adapter->ixgbe_ieee_ets` lazily, initializes unknown UP-to-TC values, optionally reads current hardware map, computes `max_tc`, stores the requested ETS, validates TC count, calls `ixgbe_setup_tc()` when TC count changes or resets when only mapping changes, then programs hardware ETS. IEEE PFC set allocates/copies `ixgbe_ieee_pfc`, derives `prio_tc` from IEEE ETS, applies PFC or normal FC, and updates RX drop behavior. IEEE app add/delete delegates to kernel DCB helpers and then updates FCoE or VF default priority state as needed.

DCBX mode set rejects LLD-managed, mixed CEE+IEEE, and non-host modes. Switching to IEEE installs zeroed ETS/PFC defaults; switching to CEE marks all CEE subsystems changed and calls `setall`; disabling DCBX drops to single-TC mode.

## State And Persistence
State is runtime adapter memory and netdev/DCB core state, not filesystem state. Important fields include `adapter->dcb_cfg`, `temp_dcb_cfg`, `dcb_set_bitmap`, `dcbx_cap`, `ixgbe_ieee_ets`, `ixgbe_ieee_pfc`, `hw_tcs`, `flags`, `state`, FCoE UP, `default_up`, VF `pf_qos`/`pf_vlan`, and DCB app entries stored through kernel DCB helpers. Hardware programming persists until reset/reapply; traffic-class changes may rebuild interrupt schemes.

## Dependencies And Integration Points
The file depends on Linux DCBNL APIs, ixgbe adapter/netdev helpers, chip DCB backends, SR-IOV helpers (`ixgbe_set_vmvir`), traffic-class setup (`ixgbe_setup_tc`), RX drop policy (`ixgbe_set_rx_drop_en`), interrupt scheme management, optional `IXGBE_FCOE`, and kernel DCB app storage helpers (`dcb_getapp`, `dcb_ieee_setapp`, `dcb_ieee_delapp`, `dcb_ieee_getapp_mask`).

## Risks
- `ixgbe_dcbnl_ieee_setpfc()` assumes `adapter->ixgbe_ieee_ets` exists before dereferencing `prio_tc`; mode setup normally creates it, but unusual call ordering is a risk.
- DCBNL operations can trigger netdev stop/open and interrupt scheme rebuilds; locking and `__IXGBE_RESETTING` handling must prevent races with normal reset/service tasks.
- Incorrect change-bit detection can skip needed hardware updates or reset unnecessarily.
- CEE and IEEE state models are separate; mode switching must not leave stale PFC/ETS/app state in hardware.
- FCoE and VF default priority updates depend on app priority masks; regressions can break offload traffic class selection or guest VLAN/QoS programming.
- Capability reporting says fixed 8-TC support and rejects `setnumtcs`; callers need to handle fixed hardware policy.

## Test Signals
Exercise `dcbtool`/`lldptool`/`ip link dcb` CEE and IEEE flows, DCBX mode switching, ETS bandwidth/TSA programming, PFC enable/disable, app add/delete for FCoE and default ethertype priority, VF default UP propagation, reset during DCB changes, netdev open/close around TC changes, `ethtool -S` PFC counters, and error paths for invalid DCBX modes or TC mappings.
