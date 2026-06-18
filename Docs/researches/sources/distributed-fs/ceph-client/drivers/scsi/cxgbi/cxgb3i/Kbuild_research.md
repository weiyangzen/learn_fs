# sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/cxgb3i/Kbuild

## Purpose

This Kbuild fragment compiles the Chelsio T3 iSCSI offload module and supplies include paths for T3 Ethernet and common Chelsio library headers.

## Important APIs, Types, And Functions

It adds `drivers/net/ethernet/chelsio/cxgb3` and `drivers/net/ethernet/chelsio/libcxgb` to `ccflags-y`, then maps `CONFIG_SCSI_CXGB3_ISCSI` to `cxgb3i.o`.

## Control Flow

When the top-level cxgbi Makefile descends into `cxgb3i/`, Kbuild uses this fragment to compile `cxgb3i.c` if the T3 iSCSI config is enabled.

## State And Persistence

No runtime state exists here. Build state is determined by `.config`.

## Dependencies And Integration Points

This file ties `cxgb3i.c` to the cxgb3 Ethernet driver headers and shared Chelsio library headers that define CPLs, offload device APIs, L2T, and pagepod support.

## Risks

Header path drift in the Ethernet driver tree will break this module. Because this is a Kbuild fragment, placing module-wide flags here only affects this subdirectory, not `libcxgbi.o`.

## Test Signals

Enable `CONFIG_SCSI_CXGB3_ISCSI=m` or `=y` and confirm `cxgb3i.o` builds with no missing `cxgb3` or `libcxgb` includes.
