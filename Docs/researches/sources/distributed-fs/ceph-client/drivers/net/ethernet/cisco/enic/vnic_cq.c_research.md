# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_cq.c

## Purpose
`vnic_cq.c` provides low-level allocation, initialization, cleanup, and free routines for Cisco vNIC completion queues.

## Important APIs, types, and functions
- `vnic_cq_alloc_with_type()` binds a `struct vnic_cq` to an MMIO resource and allocates a coherent descriptor ring.
- `vnic_cq_alloc()` is the normal `RES_TYPE_CQ` wrapper.
- `vnic_cq_init()` writes ring base, size, head/tail/color, interrupt enable, interrupt offset, and optional message address into CQ control registers.
- `vnic_cq_clean()` resets software cursor/color and hardware CQ pointers, then clears descriptor memory.
- `vnic_cq_free()` frees the coherent descriptor ring and drops the MMIO control pointer.

## Control flow and state
Allocation first hooks the resource using `vnic_dev_get_res()` and then allocates the descriptor ring. Initialization writes hardware-visible state in one sequence. Cleanup resets both software state (`to_clean`, `last_color`) and hardware head/tail/tail-color state to the initial empty ring convention.

## Dependencies and integration points
It depends on `vnic_dev` ring allocation and resource discovery. ENIC resource setup uses it after RQ/WQ allocation, and RX/TX completion paths rely on the cursors initialized here.

## Risks and test signals
Risks include missing resource mapping, wrong descriptor size for RQ extended CQ mode, stale color state after reset, and interrupt offset mismatch. Test signals are successful probe allocation, correct interrupt delivery per CQ, ring wrap behavior, and no stale completions after queue reset.
