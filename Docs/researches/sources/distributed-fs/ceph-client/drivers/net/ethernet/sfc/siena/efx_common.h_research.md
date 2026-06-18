# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/efx_common.h

## Purpose
Declares common Siena lifecycle, reset, datapath, port, stats, feature, PCI error, and utility APIs.

## Important APIs and definitions
Includes common init/fini and I/O setup, queue size constants, flow-control helpers, start/stop all, net stats, reset workqueue functions, monitor start, port reconfiguration, reset functions, dummy ops, disabled-device checks, NAPI scheduling helpers, optional MCDI logging hooks, MAC/RX mode/features/MTU/physical-port functions, PCI error handlers, and feature check.

## Control flow and integration
`efx.c` uses these functions during probe/remove/open/stop/PM. Ettool uses reset, stats, and feature functions. Channel and NIC code use scheduling and reset assertion helpers.

## State and persistence behavior
No state is stored here. Inline helpers read or mutate NIC and channel runtime state.

## Dependencies
Depends on core driver structures, Linux netdev/PCI types, and `enum reset_type`. Queue constants must match hardware and channel/ethtool limits.

## Risks
`EFX_ASSERT_RESET_SERIALISED` documents but cannot enforce all locking. Calling lifecycle APIs without RTNL or expected locks can race with reset/open/close.

## Test signals
Compile optional MCDI logging configs and exercise reset, open/close, MTU, feature toggling, stats, and PCI error paths.
