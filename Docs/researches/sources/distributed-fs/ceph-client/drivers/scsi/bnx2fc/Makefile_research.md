# sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/Makefile

## Purpose

`Makefile` maps `CONFIG_SCSI_BNX2X_FCOE` to the `bnx2fc` kernel object and lists the implementation objects linked into the driver.

## Important APIs, Types, and Definitions

`obj-$(CONFIG_SCSI_BNX2X_FCOE) += bnx2fc.o` declares the composite object. `bnx2fc-y` includes `bnx2fc_els.o`, `bnx2fc_fcoe.o`, `bnx2fc_hwi.o`, `bnx2fc_io.o`, `bnx2fc_tgt.o`, and `bnx2fc_debug.o`.

## Control Flow

The kernel build system links these objects when the config option is enabled. Runtime entry comes from module init in `bnx2fc_fcoe.o`.

## State and Persistence Behavior

No runtime state is stored. The file persists the driver’s build composition.

## Dependencies and Integration Points

It integrates the bnx2fc sources with the SCSI driver build tree and assumes local headers plus relative Broadcom network headers are available.

## Risks and Edge Cases

Omitting an object breaks link-time or runtime behavior: lifecycle/templates, firmware/queue handling, SCSI I/O, rport/session handling, ELS, and debug functionality are split across the listed objects.

## Test Signals

Use `make M=drivers/scsi/bnx2fc`, allmodconfig/link coverage, module load/unload, and `modinfo bnx2fc`.
