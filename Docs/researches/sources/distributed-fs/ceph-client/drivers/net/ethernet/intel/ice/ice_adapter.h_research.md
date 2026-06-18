# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_adapter.h

## Purpose
`ice_adapter.h` defines the shared adapter data structure and its reference-management API. It abstracts resources that are common to multiple PFs on the same physical ICE adapter.

## Important APIs, Types, And Functions
`struct ice_port_list` wraps a list of ports with a mutex. `struct ice_adapter` contains a refcount, spinlocks for GLTSYN_TIME and GLCOMM_QTX_CNTX_CTL access, a control PF pointer, shared port list, and cached 64-bit adapter index. The public API is `ice_adapter_get()` and `ice_adapter_put()`.

## Control Flow
PF probe gets an adapter reference and stores it in `struct ice_pf`. PF remove releases the reference. Consumers use the embedded locks to serialize access to shared hardware registers and use the ports list to coordinate adapter-level port relationships.

## State And Persistence
All adapter fields are runtime state. `refcount` is the ownership mechanism; `ctrl_pf` identifies the control PF when one is selected; `ports` tracks adapter ports; the index identifies which PFs share the object.

## Dependencies And Integration Points
The header uses Linux type, spinlock, and refcount declarations and forward-declares PCI and PF types. It is included by `ice.h`, making the adapter pointer available throughout the driver.

## Risks And Test Signals
Risks include lock ordering against PF locks, stale `ctrl_pf`, and port-list lifetime mismatches. Test signals include multi-function probe/remove, PTP operations on shared timer registers, and no adapter free warnings about non-empty port lists.
