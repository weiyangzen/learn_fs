<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/Kconfig

## Purpose

Defines the `INFINIBAND_RDMAVT` tristate for the RDMA verbs transport library.

## Important APIs, Types, And Functions

The option depends on `INFINIBAND_VIRT_DMA`, `X86_64`, and `PCI`. The help text identifies rdmavt as a common software verbs provider for RDMA networks.

## Control Flow

When enabled, kbuild compiles the rdmavt library module described in the local Makefile.

## State And Persistence Behavior

No runtime state exists in the Kconfig file.

## Dependencies And Integration Points

Exposes rdmavt to drivers that depend on the virtual DMA and PCI environment, historically hfi1/qib-style software verbs support.

## Risks And Edge Cases

The X86_64/PCI restrictions limit portability; relaxing them would require auditing low-level assumptions in the library and consumers.

## Test Signals

Kconfig dependency tests should confirm the symbol is unavailable without virtual DMA, X86_64, or PCI and that enabling it builds the rdmavt object list.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/Kconfig -->
