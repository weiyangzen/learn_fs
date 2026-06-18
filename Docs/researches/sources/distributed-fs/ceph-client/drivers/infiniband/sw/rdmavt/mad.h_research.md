<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mad.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mad.h

## Purpose

Declares rdmavt MAD processing and MAD agent lifecycle functions.

## Important APIs, Types, And Functions

Prototypes cover `rvt_process_mad()`, `rvt_create_mad_agents()`, and `rvt_free_mad_agents()`.

## Control Flow

Used by rdmavt core and driver setup to register MAD support for each port.

## State And Persistence Behavior

No state is defined here; per-port agent state is managed in rdmavt port structures.

## Dependencies And Integration Points

Includes RDMA VT public definitions and matches RDMA MAD callback signatures.

## Risks And Edge Cases

Any signature drift from RDMA core MAD APIs breaks registration.

## Test Signals

Compile coverage and per-port setup/teardown tests validate the header contract.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mad.h -->
