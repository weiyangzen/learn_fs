# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/Makefile

## Purpose
This Makefile wires the QEDE Ethernet driver into the kernel build. It declares the `qede.o` module/object for `CONFIG_QEDE` and selects the component objects that implement main device logic, fastpath, filtering, ethtool, PTP, optional DCB, and optional RDMA integration.

## Important APIs, Types, And Functions
The build variables are `obj-$(CONFIG_QEDE) := qede.o`, the base `qede-y` object list, `qede-$(CONFIG_DCB) += qede_dcbnl.o`, and `qede-$(CONFIG_QED_RDMA) += qede_rdma.o`.

## Control Flow
Kbuild includes `qede.o` only when `CONFIG_QEDE` is enabled. The base driver always links `qede_main.o`, `qede_fp.o`, `qede_filter.o`, `qede_ethtool.o`, and `qede_ptp.o`. DCB netlink callbacks are linked only under `CONFIG_DCB`, and RDMA hooks are linked only under `CONFIG_QED_RDMA`.

## State, Persistence, And Dependencies
There is no runtime state. The file persists build-time dependency decisions. It depends on Linux Kbuild conventions and on config symbols supplied by the kernel configuration.

## Integration Points
This is the compilation boundary for QEDE. It determines whether functions declared in `qede.h`, such as `qede_set_dcbnl_ops()` and RDMA event helpers, are backed by linked objects or compiled out via conditional code elsewhere.

## Risks
Missing an object in `qede-y` causes link failures or absent runtime functionality. Optional object guards must match the `#ifdef`/`IS_ENABLED()` guards in source files. Since `qede_dcbnl.o` depends on `edev->ops->dcb`, enabling DCB at build time still requires hardware/core-driver DCB support at runtime.

## Test Signals
Build coverage should include `CONFIG_QEDE=y/m`, `CONFIG_DCB` enabled and disabled, and `CONFIG_QED_RDMA` enabled and disabled. Link tests should verify no unresolved DCB/RDMA symbols appear for each matrix entry.
