
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/Makefile

## Purpose

This Makefile builds the first-generation Hisilicon Network Subsystem support objects and composite drivers.

## Important APIs, Types, and Functions

- `obj-$(CONFIG_HNS) += hnae.o` builds the HNAE framework object.
- `obj-$(CONFIG_HNS_DSAF) += hns_dsaf.o` builds a composite DSAF acceleration-engine object from adapt, GMAC, MAC, misc, main, PPE, RCB, and XGMAC sources.
- `obj-$(CONFIG_HNS_ENET) += hns_enet_drv.o` builds a composite Ethernet driver from `hns_enet.o` and `hns_ethtool.o`.

## Control Flow

There is no runtime control flow. Kbuild links composite objects according to Kconfig.

## State and Persistence

Only build artifacts are affected.

## Dependencies and Integration Points

This file integrates with `CONFIG_HNS`, `CONFIG_HNS_DSAF`, and `CONFIG_HNS_ENET` from the parent Kconfig and groups related HNS implementation files into modules/built-ins.

## Risks and Edge Cases

Composite object lists must stay synchronized with source-level symbol references. Object order can matter for initialization sections and unresolved symbols, so changes need module and built-in build coverage.

## Test Signals

Expected build outputs are `hnae.o`, `hns_dsaf.o` containing all DSAF pieces, and `hns_enet_drv.o` containing ENET plus ethtool support when the corresponding symbols are enabled.
