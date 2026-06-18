# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-csi-phy.h

## Purpose

This header declares CSI PHY power control for IPU7 ISYS CSI2 ports.

## Important APIs, Types, and Functions

It defines `PHY_MODE_DPHY`, `PHY_MODE_CPHY`, and declares `ipu7_isys_csi_phy_powerup()` plus `ipu7_isys_csi_phy_powerdown()`.

## Control Flow

No implementation flow. CSI2 stream enable code calls powerup before enabling capture and powerdown during teardown.

## State and Persistence Behavior

The functions operate on `struct ipu7_isys_csi2` state such as port, lane count, PHY mode, and parent ISYS.

## Dependencies and Integration Points

It forward-declares ISYS and references `struct ipu7_isys_csi2` without a forward declaration in this header, relying on include order from consumers.

## Risks and Edge Cases

The missing explicit `struct ipu7_isys_csi2` forward declaration can make include-order changes fragile. PHY mode values must match firmware/hardware expectations.

## Test Signals

Compile include-order tests and runtime DPHY/CPHY stream start/stop through CSI2.
