# sources/distributed-fs/ceph-client/drivers/infiniband/hw/cxgb4/Makefile

## Purpose

`Makefile` defines how the Chelsio `iw_cxgb4` iWARP/RDMA driver is compiled. It adds include paths for the Chelsio Ethernet and shared library headers, connects the object to `CONFIG_INFINIBAND_CXGB4`, and lists the translation units that form the driver.

## Important APIs, Types, and Functions

- `ccflags-y` adds `drivers/net/ethernet/chelsio/cxgb4` and `drivers/net/ethernet/chelsio/libcxgb` include directories.
- `obj-$(CONFIG_INFINIBAND_CXGB4) += iw_cxgb4.o` creates the built-in or module target controlled by Kconfig.
- `iw_cxgb4-y` is composed from `device.o`, `cm.o`, `provider.o`, `mem.o`, `cq.o`, `qp.o`, `resource.o`, `ev.o`, `id_table.o`, and `restrack.o`.

## Control Flow

There is no runtime flow. Kbuild evaluates `CONFIG_INFINIBAND_CXGB4`; when enabled, it compiles the listed source files with the extra include paths and links them into the composite `iw_cxgb4` object. In module mode, that composite becomes `iw_cxgb4.ko`; in built-in mode, it is linked into the kernel image.

## State and Persistence Behavior

The file affects build artifacts only. It does not persist runtime state. The object list determines which driver subsystems are present: device registration, connection management, verbs provider operations, memory registration, CQ/QP handling, resource management, event processing, ID tables, and RDMA resource tracking.

## Dependencies and Integration Points

The include paths are the main integration point: RDMA driver sources include Chelsio low-level adapter, firmware/offload, and shared connection-management helpers from the Ethernet tree and `libcxgb`. The composite object integrates with the RDMA core through provider code and with the Chelsio T4 Ethernet ULD interface through device/CM/resource code.

## Risks and Edge Cases

Header include paths are relative to `$(srctree)`, so source-tree moves or header reshuffling in the Chelsio Ethernet driver can break RDMA builds even if local `hw/cxgb4` files are unchanged. Adding a new source file without updating `iw_cxgb4-y` silently omits code from the driver. Removing a file or renaming an object without updating the list causes build failures. Because this Makefile applies include flags to all objects in the directory, local header names can accidentally collide with Chelsio Ethernet headers.

## Test Signals

Useful checks include `make M=drivers/infiniband/hw/cxgb4`, full kernel builds with `CONFIG_INFINIBAND_CXGB4=y` and `=m`, clean builds after Chelsio Ethernet header changes, module load/unload smoke tests for `iw_cxgb4`, and link checks that all object-local symbols expected by provider, CM, CQ/QP, resource, event, ID table, and restrack code are present.
