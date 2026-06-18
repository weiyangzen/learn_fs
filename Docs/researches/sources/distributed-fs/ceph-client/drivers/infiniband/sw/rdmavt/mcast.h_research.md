<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mcast.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mcast.h

## Purpose

Declares rdmavt multicast initialization and attach/detach helpers.

## Important APIs, Types, And Functions

Prototypes cover `rvt_driver_mcast_init()`, `rvt_attach_mcast()`, `rvt_detach_mcast()`, and `rvt_mcast_tree_empty()`.

## Control Flow

Drivers initialize multicast state during rdmavt device setup and expose attach/detach through RDMA core verbs.

## State And Persistence Behavior

No state is defined here; multicast rb trees and counts live in rdmavt device/port structs.

## Dependencies And Integration Points

Includes RDMA VT public definitions.

## Risks And Edge Cases

Header users also need exported `rvt_mcast_find()` from the implementation if they walk multicast groups directly; it is not declared here, so external declarations must come from another public header.

## Test Signals

Compile tests should validate operation signatures and driver integration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mcast.h -->
