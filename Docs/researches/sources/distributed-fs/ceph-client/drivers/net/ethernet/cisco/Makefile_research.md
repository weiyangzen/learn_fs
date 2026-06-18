<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/Makefile

## Purpose

This Makefile connects Cisco Ethernet driver builds to the kernel object tree.

## Important APIs, Types, and Functions

It adds the `enic/` subdirectory when `CONFIG_ENIC` is enabled: `obj-$(CONFIG_ENIC) += enic/`.

## Control Flow

There is no runtime behavior. Kbuild descends into `drivers/net/ethernet/cisco/enic` only for ENIC-enabled builds.

## State and Persistence Behavior

No runtime state exists. Build output depends on the selected `.config`.

## Dependencies and Integration Points

This file is consumed by Kbuild and depends on the child ENIC Makefile for object composition.

## Risks and Edge Cases

If `CONFIG_ENIC=m`, this arrangement builds the child directory as a module object as defined by the child Makefile. Incorrect symbol naming here would silently omit the driver.

## Test Signals

Build with `CONFIG_ENIC=y`, `m`, and unset to confirm the directory is included only when expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/Makefile -->
