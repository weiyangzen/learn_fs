# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_cq.h

## Purpose
`vnic_cq.h` defines the completion queue MMIO control layout, software CQ object, cursor helpers, and exported CQ management prototypes.

## Important APIs, types, and functions
- `struct vnic_cq_ctrl` mirrors hardware CQ control registers.
- `struct vnic_rx_bytes_counter` supports adaptive RX coalescing by separating small and large packet byte counts.
- `struct vnic_cq` stores index, vdev, control pointer, descriptor ring, software clean cursor, color bit, interrupt offset, and adaptive coalescing fields.
- `vnic_cq_to_clean()` returns the current descriptor pointer.
- `vnic_cq_inc_to_clean()` advances the cursor and toggles `last_color` on wrap.

## Control flow and state
The important state machine is color-based CQ traversal: consumers compare descriptor color with `last_color`, process entries until they match, and use `vnic_cq_inc_to_clean()` to wrap and toggle expected color.

## Dependencies and integration points
The header depends on `cq_desc.h` and `vnic_dev.h`. It is shared by ENIC resource allocation, RX/TX CQ service, and interrupt/coalescing code.

## Risks and test signals
An incorrect color convention or descriptor-size calculation leads to missed or duplicate completions. Test with high packet rates, ring wrap, CQ clean/reset, and interrupt offset validation.
