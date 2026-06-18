# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_base.h

## Purpose

`ice_base.h` declares the queue-base services implemented in `ice_base.c`. It is the public header for VSI queue allocation, Rx/Tx queue configuration, interrupt mapping, queue-pair enable/disable, Tx queue metadata fill, and TxTime descriptor count calculation.

The header is intentionally thin. It includes `ice.h` for all core driver structures and exports function prototypes rather than defining data structures of its own.

## Important APIs and Types

The declared API groups are:

- Rx queue configuration: `ice_vsi_cfg_single_rxq()`, `ice_vsi_cfg_rxqs()`, `ice_vsi_ctrl_one_rx_ring()`, `ice_vsi_wait_one_rx_ring()`.
- PF queue ID assignment: `__ice_vsi_get_qs()` using `struct ice_qs_cfg`.
- q-vector lifecycle and ring mapping: `ice_vsi_alloc_q_vectors()`, `ice_vsi_map_rings_to_vectors()`, `ice_vsi_free_q_vectors()`.
- Tx queue configuration: `ice_vsi_cfg_single_txq()`, `ice_vsi_cfg_lan_txqs()`, `ice_vsi_cfg_xdp_txqs()`.
- interrupt setup: `ice_cfg_itr()`, `ice_cfg_txq_interrupt()`, `ice_cfg_rxq_interrupt()`, `ice_trigger_sw_intr()`.
- Tx queue stop metadata and operations: `ice_vsi_stop_tx_ring()`, `ice_fill_txq_meta()`.
- queue-pair operations: `ice_qp_ena()`, `ice_qp_dis()`.
- TxTime sizing: `ice_calc_ts_ring_count()`.

Types are not defined here but are central to the API contract: `struct ice_vsi`, `struct ice_qs_cfg`, `struct ice_hw`, `struct ice_q_vector`, `struct ice_tx_ring`, `struct ice_txq_meta`, and `enum ice_disq_rst_src`.

## Control Flow and Integration

This header allows higher-level driver code to sequence queue lifecycle steps without knowing the implementation details in `ice_base.c`. Typical ordering is:

1. Allocate PF queue IDs for a VSI through `__ice_vsi_get_qs()`.
2. Allocate and map q-vectors with `ice_vsi_alloc_q_vectors()` and `ice_vsi_map_rings_to_vectors()`.
3. Configure Tx and Rx rings with `ice_vsi_cfg_lan_txqs()`, `ice_vsi_cfg_xdp_txqs()`, and `ice_vsi_cfg_rxqs()`.
4. Configure MSI-X/ITR using `ice_cfg_itr()`, `ice_cfg_txq_interrupt()`, and `ice_cfg_rxq_interrupt()`.
5. Use `ice_qp_dis()` and `ice_qp_ena()` for dynamic per-queue restarts.

The declarations bridge queue lifecycle callers such as VSI rebuild, netdev open/close, AF_XDP setup, reset recovery, and SR-IOV control paths to the common hardware/AdminQ layer.

## State and Persistence Behavior

Although the header has no storage, its function contracts mutate persistent state in:

- VSI queue maps, ring arrays, ring `q_vector` pointers, and q-vector arrays.
- hardware Rx/Tx queue context registers and queue interrupt registers.
- firmware scheduler state through Tx queue add/remove operations.
- NAPI, IRQ allocation, XDP RXQ registration, page-pool ownership, and netdev queue/carrier state.

Callers should treat these APIs as stateful hardware operations, not pure configuration helpers.

## Dependencies

`ice_base.h` depends on `ice.h` for full type declarations and feature constants. Implementation users also indirectly depend on `ice_common.h`, scheduler/AdminQ declarations, SR-IOV helpers, XDP/page-pool APIs, and Linux netdev/NAPI infrastructure.

## Risks and Contract Notes

- Several functions accept raw queue indexes. Some implementations validate bounds, while others assume caller validation. Public use should check `q_idx`, `rxq_idx`, and ring pointer validity before calling.
- `__ice_vsi_get_qs()` has a double-underscore name but is exported within the driver; callers need to understand its locking and partial queue-count behavior.
- `ice_vsi_alloc_q_vectors()` may adjust `vsi->num_q_vectors` on partial allocation and still return success when at least one vector exists.
- `ice_vsi_stop_tx_ring()` requires correctly populated `struct ice_txq_meta`; callers should use `ice_fill_txq_meta()` unless they have a specific reset-flow reason not to.

## Test Signals

Header-level validation is mostly compile and integration coverage:

- Compile all translation units including `ice_base.h` under relevant feature configs.
- Confirm no prototype drift between `ice_base.h` and `ice_base.c`.
- Exercise callers from VSI open/rebuild, queue-pair restart, AF_XDP queue setup, VF queue setup, and Tx timestamping.
- Static analysis should flag any unchecked raw queue index passed to control or wait functions.
