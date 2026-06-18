<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/Makefile

## Purpose

Selects software RDMA provider subdirectories for the InfiniBand build.

## Important APIs, Types, And Functions

Builds `rdmavt/` for `CONFIG_INFINIBAND_RDMAVT`, `rxe/` for `CONFIG_RDMA_RXE`, and `siw/` for `CONFIG_RDMA_SIW`.

## Control Flow

The kernel build descends into enabled software provider directories.

## State And Persistence Behavior

No runtime state exists here.

## Dependencies And Integration Points

Integrates rdmavt, RXE, and SIW providers into the RDMA subsystem build.

## Risks And Edge Cases

Wrong symbol-to-directory mapping omits provider code or builds unsupported code.

## Test Signals

Kbuild coverage with each config enabled should compile the expected subdirectory.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/Makefile -->
