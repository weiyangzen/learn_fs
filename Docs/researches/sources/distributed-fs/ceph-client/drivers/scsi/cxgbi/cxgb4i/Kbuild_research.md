# sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/cxgb4i/Kbuild

## Purpose

This Kbuild fragment compiles the Chelsio T4 iSCSI offload module and supplies include paths for the T4 Ethernet driver and common Chelsio library headers.

## Important APIs, Types, And Functions

It adds `drivers/net/ethernet/chelsio/cxgb4` and `drivers/net/ethernet/chelsio/libcxgb` to `ccflags-y`, then maps `CONFIG_SCSI_CXGB4_ISCSI` to `cxgb4i.o`.

## Control Flow

When the parent cxgbi Makefile descends into `cxgb4i/`, Kbuild compiles `cxgb4i.c` if the T4 iSCSI config is enabled.

## State And Persistence

No runtime state exists here. Build state is determined by `.config`.

## Dependencies And Integration Points

This file ties the T4 iSCSI driver to cxgb4 Ethernet headers and the common Chelsio library. It is selected through the parent `cxgbi/Makefile` and child Kconfig symbol.

## Risks

Header path drift in cxgb4 or libcxgb breaks compilation. Flags are local to the subdirectory and do not affect `libcxgbi.o`.

## Test Signals

Enable `CONFIG_SCSI_CXGB4_ISCSI=m` or `=y` and confirm `cxgb4i.o` builds cleanly with cxgb4 and libcxgb include dependencies.
