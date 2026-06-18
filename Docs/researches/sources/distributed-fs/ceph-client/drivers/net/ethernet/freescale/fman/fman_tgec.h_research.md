# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_tgec.h

## Purpose
Declares the TGEC/XGEC initialization entry point used by the generic FMan MAC platform driver.

## Important APIs, Types, and Functions
Includes `fman_mac.h`, forward declares `struct mac_device`, and declares `tgec_initialization(struct mac_device *mac_dev, struct device_node *mac_node, struct fman_mac_params *params)`.

## Control Flow and State
There is no runtime control flow. The declared function is the backend factory/initializer that populates `mac_device` operation pointers and creates the TGEC private state.

## Dependencies and Integration Points
Used by `mac.c` in its OF match table for `fsl,fman-xgec`. The prototype bridges generic FMan MAC probing with the 10G-specific implementation in `fman_tgec.c`.

## Risks and Test Signals
Risk is mainly signature drift between the generic MAC initialization table and backend implementation. Test signals are compile coverage with TGEC enabled and successful probe of an `fsl,fman-xgec` DT node.
