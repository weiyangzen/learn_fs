<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/Makefile

## Purpose

Builds the VMware PVRDMA driver module from its component source files when `CONFIG_INFINIBAND_VMWARE_PVRDMA` is enabled.

## Important APIs, Types, And Functions

The module target is `vmw_pvrdma.o`, composed of `pvrdma_cmd.o`, `pvrdma_cq.o`, `pvrdma_doorbell.o`, `pvrdma_main.o`, `pvrdma_misc.o`, `pvrdma_mr.o`, `pvrdma_qp.o`, `pvrdma_srq.o`, and `pvrdma_verbs.o`.

## Control Flow

The kernel build system compiles each object and links them into the module according to the Kconfig symbol.

## State And Persistence Behavior

No runtime state exists here. The file determines which source files participate in the module.

## Dependencies And Integration Points

Integrates with the kernel kbuild system and the local headers that tie the objects together.

## Risks And Edge Cases

Missing an object here would produce unresolved symbols or silently omit verbs functionality. Adding a new implementation file requires updating this list.

## Test Signals

`make M=drivers/infiniband/hw/vmw_pvrdma` or equivalent kernel builds should compile and link the module with no unresolved symbols.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/Makefile -->
