# sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/Kconfig

## Purpose

This top-level Kconfig file includes the Chelsio iSCSI offload driver configuration fragments for T3 (`cxgb3i`) and T4+ (`cxgb4i`). It provides no direct option itself; it composes the submenu content from child directories.

## Important APIs, Types, And Functions

The only directives are `source "drivers/scsi/cxgbi/cxgb3i/Kconfig"` and `source "drivers/scsi/cxgbi/cxgb4i/Kconfig"`.

## Control Flow

During kernel configuration, Kconfig reads this file and then evaluates each child config. Selecting either child driver controls object inclusion through the sibling Makefile.

## State And Persistence

Configuration state persists in the kernel `.config` as `CONFIG_SCSI_CXGB3_ISCSI` and/or `CONFIG_SCSI_CXGB4_ISCSI`. This file owns no runtime state.

## Dependencies And Integration Points

It integrates the Chelsio iSCSI offload family into the SCSI driver Kconfig tree and delegates all dependency selection to child Kconfig files.

## Risks

If this file is omitted from the parent SCSI Kconfig, neither child option is visible. If child paths are renamed without updating these `source` lines, configuration fails.

## Test Signals

Run menuconfig/olddefconfig with the parent SCSI Kconfig and confirm both Chelsio T3 and T4 iSCSI options appear and can be selected subject to their dependencies.
