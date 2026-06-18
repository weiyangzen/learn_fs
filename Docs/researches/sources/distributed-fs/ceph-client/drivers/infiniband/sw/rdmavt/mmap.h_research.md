<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mmap.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mmap.h

## Purpose

Declares rdmavt mmap initialization, mmap handling, and mmap-info creation/update/release helpers.

## Important APIs, Types, And Functions

Prototypes cover `rvt_mmap_init()`, `rvt_release_mmap_info()`, `rvt_mmap()`, `rvt_create_mmap_info()`, and `rvt_update_mmap_info()`.

## Control Flow

rdmavt setup calls init; mmap-capable objects create/update descriptors; RDMA core mmap calls route to `rvt_mmap()`.

## State And Persistence Behavior

No state is declared here; state lives in `struct rvt_dev_info` and `struct rvt_mmap_info`.

## Dependencies And Integration Points

Includes RDMA VT public definitions and exposes helpers used by CQ/QP/SRQ code.

## Risks And Edge Cases

All users must obey the descriptor lifetime rules or VMA close can free an object still in use.

## Test Signals

Compile and mmap lifecycle tests validate function signatures and object lifetime behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mmap.h -->
