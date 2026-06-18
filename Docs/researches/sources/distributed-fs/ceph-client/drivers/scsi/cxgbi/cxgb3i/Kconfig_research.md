# sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/cxgb3i/Kconfig

## Purpose

This Kconfig file defines the `SCSI_CXGB3_ISCSI` option for Chelsio T3 iSCSI offload support.

## Important APIs, Types, And Functions

The option is `tristate "Chelsio T3 iSCSI support"`. It depends on `PCI && INET` and selects `NETDEVICES`, `ETHERNET`, `NET_VENDOR_CHELSIO`, `CHELSIO_T3`, `CHELSIO_LIB`, and `SCSI_ISCSI_ATTRS`.

## Control Flow

When selected, Kconfig enables the necessary Chelsio Ethernet and iSCSI transport support. Kbuild then compiles `libcxgbi.o` and the `cxgb3i` subdirectory through the parent Makefile.

## State And Persistence

The selected state persists as `CONFIG_SCSI_CXGB3_ISCSI` in `.config`; no runtime state exists in this file.

## Dependencies And Integration Points

The option integrates SCSI iSCSI transport attributes, the Chelsio T3 Ethernet offload driver, common Chelsio library support, PCI, and IPv4/INET networking.

## Risks

The `select` chain can force lower-level networking drivers on, so dependency correctness matters. The help text is minimal and does not mention firmware/offload requirements or hardware generation limits beyond T3.

## Test Signals

Kconfig tests should verify that the symbol is visible only with PCI and INET, that selecting it pulls in Chelsio T3/library and iSCSI attrs, and that module/built-in builds both link.
