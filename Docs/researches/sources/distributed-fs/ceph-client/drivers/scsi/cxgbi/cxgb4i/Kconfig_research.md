# sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/cxgb4i/Kconfig

## Purpose

This Kconfig file defines `SCSI_CXGB4_ISCSI`, the Chelsio T4-generation iSCSI offload driver option.

## Important APIs, Types, And Functions

The option is `tristate "Chelsio T4 iSCSI support"`. It depends on `PCI && INET`, `PTP_1588_CLOCK_OPTIONAL`, `THERMAL || !THERMAL`, `ETHERNET`, and `TLS || TLS=n`. It selects `NET_VENDOR_CHELSIO`, `CHELSIO_T4`, `CHELSIO_LIB`, and `SCSI_ISCSI_ATTRS`.

## Control Flow

Kconfig exposes the option only when dependencies are satisfied. When selected, Kbuild compiles shared `libcxgbi.o` and descends into `cxgb4i/` to build `cxgb4i.o`.

## State And Persistence

The selected state persists in `.config` as `CONFIG_SCSI_CXGB4_ISCSI`. This file has no runtime state.

## Dependencies And Integration Points

The option integrates PCI/INET networking, Chelsio T4 Ethernet support, shared Chelsio library support, iSCSI transport attributes, optional PTP, thermal, and TLS compatibility constraints.

## Risks

The `TLS || TLS=n` dependency prevents unsupported TLS combinations but can make the option disappear in configurations where TLS is modular or otherwise incompatible. The thermal dependency is a compatibility pattern that should match cxgb4 requirements. As with T3, `select` pulls lower-level Chelsio components into the configuration.

## Test Signals

Kconfig tests should cover built-in and modular combinations for TLS/PTP/THERMAL, verify option visibility, confirm selected dependencies, and build both module and built-in configurations.
