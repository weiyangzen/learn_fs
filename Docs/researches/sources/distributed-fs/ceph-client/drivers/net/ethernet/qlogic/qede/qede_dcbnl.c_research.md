# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/qede_dcbnl.c

## Purpose
`qede_dcbnl.c` adapts Linux DCBNL rtnetlink operations to the QED core DCB operation table. It lets userspace query and configure DCB, PFC, ETS, CEE, IEEE application priorities, peer information, and DCBX state through the netdev's `dcbnl_ops`.

## Important APIs, Types, And Functions
Most functions are thin wrappers named `qede_dcbnl_*`. They get `struct qede_dev *edev = netdev_priv(netdev)` and delegate to `edev->ops->dcb` methods, passing `edev->cdev` and the DCBNL arguments. The static `qede_dcbnl_ops` table maps Linux callbacks such as `ieee_getpfc`, `ieee_setpfc`, `ieee_getets`, `ieee_setets`, `getstate`, `setstate`, `getpgtccfgtx`, `setpgtccfgtx`, `getapp`, `setapp`, peer CEE/IEEE queries, feature config, and DCBX config. `qede_set_dcbnl_ops()` installs the table on the netdev.

## Control Flow
There is almost no local policy. A DCBNL request enters through the kernel's rtnetlink DCB layer, the selected callback unwraps `qede_dev`, then calls the QED DCB op. The exception is `qede_dcbnl_ieee_setapp()`, which first calls `dcb_ieee_setapp(netdev, app)` to update the kernel DCB application table; only if that succeeds does it call the hardware/core `ieee_setapp` method.

## State, Persistence, And Dependencies
This file keeps no private state. Persistent changes live in the kernel DCB app table and in firmware/core-driver DCB state managed by QED. It depends on `CONFIG_DCB` build selection, `<net/dcbnl.h>`, rtnetlink serialization expectations, and a populated `edev->ops->dcb` table.

## Integration Points
`qede_set_dcbnl_ops()` is called by QEDE setup code when DCB support is available. The wrappers bridge Linux netdev DCBNL APIs to QED common hardware management. DCB configuration also interacts with traffic classes used by TX queue layout and with PFC/link behavior reported elsewhere through ethtool.

## Risks
The wrappers assume `edev->ops`, `edev->ops->dcb`, and every function pointer in the table are valid; there are no local NULL checks. If core DCB support is absent despite `CONFIG_DCB`, callbacks can crash. Error handling is delegated, so inconsistent return conventions in QED DCB ops would be visible directly to userspace. `ieee_setapp()` has a two-stage update, so failure after the kernel table update would need scrutiny for rollback behavior outside this file.

## Test Signals
Test with DCB enabled hardware/core ops, `dcbtool`/`lldptool` or netlink DCB commands for CEE and IEEE paths, PFC/ETS get and set, app priority add/delete, peer table reads, DCBX mode changes, and negative tests where unsupported DCB operations return clean errors rather than dereferencing missing ops.
