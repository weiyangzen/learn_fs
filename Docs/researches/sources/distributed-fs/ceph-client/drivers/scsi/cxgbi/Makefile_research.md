# sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/Makefile

## Purpose

This Makefile builds the shared Chelsio iSCSI library and the selected T3/T4 driver subdirectories. It also adds the shared Chelsio `libcxgb` include path needed by `libcxgbi` and children.

## Important APIs, Types, And Functions

The file sets `ccflags-y += -I $(srctree)/drivers/net/ethernet/chelsio/libcxgb`. It builds `libcxgbi.o cxgb3i/` when `CONFIG_SCSI_CXGB3_ISCSI` is enabled and `libcxgbi.o cxgb4i/` when `CONFIG_SCSI_CXGB4_ISCSI` is enabled.

## Control Flow

Kbuild evaluates the config-symbol object lists. If both drivers are enabled, `libcxgbi.o` is listed by both conditional lines; Kbuild normally handles object inclusion for the directory, but this duplication is a notable build-shape point.

## State And Persistence

The file has no runtime state. Build outputs are generated according to `.config` and Kbuild state.

## Dependencies And Integration Points

It integrates `drivers/scsi/cxgbi/libcxgbi.c`, `cxgb3i/Kbuild`, and `cxgb4i/Kbuild` with Chelsio Ethernet include headers. It depends on the Kconfig symbols defined in child Kconfig files.

## Risks

The duplicated `libcxgbi.o` conditional can be surprising when both T3 and T4 are enabled, although this is an established kernel build pattern in some shared-library directories. Include path changes in Chelsio net drivers can break compilation.

## Test Signals

Build with only T3, only T4, both, and neither enabled. Confirm `libcxgbi` is built when needed, no duplicate-symbol/link issue occurs, and both child modules resolve Chelsio Ethernet headers.
