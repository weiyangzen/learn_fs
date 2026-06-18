<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/Kconfig

## Purpose
`rmnet/Kconfig` defines the RMNET MAP driver configuration option.

## Important APIs, Types, and Data
- `menuconfig RMNET` is a tristate labeled "RmNet MAP driver".
- Defaults to disabled.
- Selects `GRO_CELLS`.
- Help text describes MAP multiplexing and aggregation over IP-mode physical devices.

## Control Flow
Kconfig controls whether the rmnet module is built. No runtime flow exists in this file.

## State and Persistence
The selected value persists in kernel `.config` and determines build output.

## Dependencies and Integration Points
The option feeds `rmnet/Makefile` through `CONFIG_RMNET` and ensures GRO cell support required by the virtual netdev data path.

## Risks and Edge Cases
Selecting `GRO_CELLS` pulls in additional networking support. With the option disabled, rtnetlink kind `"rmnet"` is unavailable even if userspace expects it.

## Test Signals
`CONFIG_RMNET=m` should build `rmnet.ko`; disabled configs should omit the module and rtnl link kind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/Kconfig -->
