# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_arfs.h

## Purpose
`ice_arfs.h` defines the accelerated RFS data structures and the conditional public API for ARFS support in the ICE driver.

## Important APIs, Types, And Functions
`enum ice_arfs_fltr_state` defines the software lifecycle for ARFS filters: inactive, active, and to-delete. `struct ice_arfs_entry` stores the Flow Director filter payload, hash-list node, UDP activation timestamp, flow id, and state. `struct ice_arfs_entry_ptr` is a temporary pointer wrapper used for add lists so entries can remain in the hash table while hardware programming occurs. `struct ice_arfs_active_fltr_cntrs` tracks active TCP/UDP IPv4/IPv6 perfect-filter counts with atomics.

When `CONFIG_RFS_ACCEL` is enabled, the header declares the ARFS lifecycle, sync, CPU rmap, flow-steer, and Flow Director conflict-query functions. When disabled, it provides no-op or `-EOPNOTSUPP` inline stubs.

## Control Flow
The conditional API lets the rest of the driver call ARFS hooks unconditionally. Enabled builds allocate state on the PF VSI, accept flow-steer callbacks, and sync filters through the service task. Disabled builds compile those call sites out to inert behavior.

## State And Persistence
The header defines runtime ARFS state only. The fields live in `struct ice_vsi` via pointers declared in `ice.h`; no ARFS state persists across reset or driver reload.

## Dependencies And Integration Points
It includes `ice_fdir.h` because ARFS entries are programmed as Flow Director filters. The public API integrates with netdev RFS acceleration, PF/VSI setup and teardown, reset rebuild, and Flow Director perfect-filter management.

## Risks And Test Signals
Risks include keeping stubs semantically aligned with enabled behavior, filter state mismatches, and active counter misuse. Test signals include builds with and without `CONFIG_RFS_ACCEL`, RFS steering callbacks returning filter IDs, and correct cleanup on reset/remove.
