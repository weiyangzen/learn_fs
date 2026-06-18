# sources/distributed-fs/ceph-client/drivers/ufs/Makefile

## Purpose

This Makefile wires the top-level UFS directory into the kernel build.

## Important APIs, Types, and Functions

The single build rule adds `core/` and `host/` to `obj-$(CONFIG_SCSI_UFSHCD)`.

## Control Flow

If `CONFIG_SCSI_UFSHCD` is enabled, kbuild descends into the UFS core and host subdirectories. The comment notes link order is important: the generic core must initialize before vendor host drivers.

## State and Persistence Behavior

No runtime state exists. Build artifacts and module linkage are affected by the selected configuration.

## Dependencies and Integration Points

This file integrates UFS with kbuild and enforces core-before-host ordering that host glue drivers rely on.

## Risks and Test Signals

Risks are link-order regressions and missing subdirectory traversal. Test signals include built-in and modular builds verifying `ufshcd-core` symbols are available to host drivers.
