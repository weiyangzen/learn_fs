# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/libcxgb/Makefile

## Purpose

This Makefile builds the shared Chelsio library object `libcxgb.o` when `CONFIG_CHELSIO_LIB` is enabled.

## Important APIs, Types, and Functions

- `ccflags-y := -I $(src)/../cxgb4` adds the sibling cxgb4 include directory.
- `obj-$(CONFIG_CHELSIO_LIB) += libcxgb.o` controls inclusion.
- `libcxgb-y := libcxgb_ppm.o libcxgb_cm.o` links page-pod manager and connection-management helpers into the composite object.

## Control Flow

Kbuild conditionally builds `libcxgb.o` and links the two helper implementation files into it. Other Chelsio upper-layer drivers can depend on this library.

## State and Persistence Behavior

No runtime state exists in this build file.

## Dependencies and Integration Points

The file integrates with kernel Kbuild and `CONFIG_CHELSIO_LIB`. The include path supports direct inclusion of cxgb4 headers by library sources.

## Risks and Edge Cases

If `CONFIG_CHELSIO_LIB` is disabled while consumers expect exported symbols from `libcxgb_cm.c` or `libcxgb_ppm.c`, link failures occur. New library sources must be added to `libcxgb-y`.

## Test Signals

Build with `CONFIG_CHELSIO_LIB=m`/`=y` and with dependent Chelsio iSCSI/RDMA consumers enabled to verify exported symbol resolution.
