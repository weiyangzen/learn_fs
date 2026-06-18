# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_repr.h

## Purpose

`ice_repr.h` defines the representor data model and public API used by the `ice` eswitch, bridge, datapath, and ethtool integration. It is the shared contract for VF/SF port representor creation, lookup, stats accounting, and queue state control.

## Important APIs And Types

`struct ice_repr_pcpu_stats` stores synchronized per-CPU CPU-hit counters: Rx packets/bytes, Tx packets/bytes, and Tx drops. `enum ice_repr_type` distinguishes VF and SF representors. `struct ice_repr` carries the represented source VSI, netdev, metadata destination, bridge port, stats pointer, representor id, parent MAC, type, VF/SF union, and a small ops table for add/remove/ready behavior.

The header declares creation (`ice_repr_create_vf`, `ice_repr_create_sf`), destruction (`ice_repr_destroy`), queue control (`ice_repr_start_tx_queues`, `ice_repr_stop_tx_queues`), netdev conversion and type check (`ice_netdev_to_repr`, `ice_is_port_repr_netdev`), stats increments, and PF representor lookup (`ice_repr_get`).

## Control Flow Role

The ops table lets common eswitch code invoke family-specific representor lifecycle without checking whether the represented endpoint is a VF or SF at every call. `ice_repr_get` provides xarray-backed lookup by representor id, while `ice_netdev_to_repr` is the fast path for netdev callbacks.

## State And Persistence Behavior

The header declares runtime-only state. `struct ice_repr` owns pointers to objects whose lifetime is coordinated outside the header: VSI, netdev, metadata destination, bridge port, VF/SF, and per-CPU stats. No persistent storage is involved.

## Dependencies And Integration Points

It includes `<net/dst_metadata.h>` and depends on forward declarations/types from the broader `ice` driver through includers such as `ice.h`. The API is used by eswitch attach/detach, bridge forwarding/offload code, TxRx stats paths, TC setup, and ethtool representor operations.

## Risks And Edge Cases

The union requires `type` and ops to stay consistent with the active member. Callers must not use `vf` fields for SF representors or `sf` fields for VF representors. Stats updates require `stats` to be allocated and valid on all CPUs. The `dst` and `br_port` pointers imply integration with metadata and bridge offload lifetimes, so detach order matters.

## Test Signals

Compile-time users should agree on the structure layout and prototypes. Runtime signals include successful `ice_netdev_to_repr` in netdev callbacks, correct VF/SF-specific ops selected after creation, valid stats accounting, and representor lookup returning the expected object from `pf->eswitch.reprs`.
