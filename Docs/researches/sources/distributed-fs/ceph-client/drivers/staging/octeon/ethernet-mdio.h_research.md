# sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-mdio.h

## Purpose
Shared declarations and common includes for Octeon PHY/MDIO support.

## Important APIs, Types, And Functions
Declares `cvm_oct_ethtool_ops`, `cvm_oct_ioctl()`, and `cvm_oct_phy_setup_device()`. It includes netdevice, ethtool, proc/seq, routing, and optional XFRM headers.

## Control Flow
Core netdev operations include this header to attach ethtool ops, ioctl handlers, and PHY setup helpers.

## State And Persistence
No state; declarations only.

## Dependencies And Integration Points
Links `ethernet.c`, port-mode helpers, and `ethernet-mdio.c` through shared prototypes and kernel networking headers.

## Risks
Broad includes increase compile coupling. Prototype mismatches would surface at build time.

## Test Signals
Compile all Octeon objects, verify netdev ops can reference the declared symbols, and build with optional XFRM enabled/disabled.
