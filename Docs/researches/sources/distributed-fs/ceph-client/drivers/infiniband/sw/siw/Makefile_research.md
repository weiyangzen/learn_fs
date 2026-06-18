# sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/Makefile

## Purpose

`Makefile` defines the Kbuild composition of the SIW software iWARP driver.

## Important APIs, Types, and Functions

`obj-$(CONFIG_RDMA_SIW) += siw.o` builds the composite target. `siw-y` links `siw_cm.o`, `siw_cq.o`, `siw_main.o`, `siw_mem.o`, `siw_qp.o`, `siw_qp_tx.o`, `siw_qp_rx.o`, and `siw_verbs.o`.

## Control Flow

Kbuild evaluates `CONFIG_RDMA_SIW`, compiles the listed objects when enabled, and links them into `siw.o` for built-in or module output.

## State and Persistence Behavior

The file affects build artifacts only. The object list determines which SIW subsystems are present: CM, CQ, main registration, memory, QP core, TX/RX protocol, and verbs.

## Dependencies and Integration Points

It integrates with the SIW Kconfig symbol and source files in the directory. Runtime dependencies are expressed in Kconfig.

## Risks and Edge Cases

Adding, removing, or renaming SIW source files without updating `siw-y` causes missing functionality or build failures. The stable object/module name is externally visible.

## Test Signals

Run directory module builds, full kernel built-in/module builds, and module load smoke tests after object list changes.
