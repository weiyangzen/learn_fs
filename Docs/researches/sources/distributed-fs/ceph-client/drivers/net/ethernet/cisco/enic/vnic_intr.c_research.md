# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_intr.c

## Purpose
`vnic_intr.c` implements low-level allocation, initialization, coalescing timer programming, cleanup, and free routines for Cisco vNIC interrupt control resources.

## Important APIs, types, and functions
- `vnic_intr_alloc_with_type()` binds a `struct vnic_intr` to an interrupt-control MMIO resource.
- `vnic_intr_alloc()` uses the normal `RES_TYPE_INTR_CTRL` resource.
- `vnic_intr_init()` programs coalescing timer, coalescing type, mask-on-assertion, and clears credits.
- `vnic_intr_coalescing_timer_set()` converts microseconds to hardware cycles via `vnic_dev_intr_coal_timer_usec_to_hw()` before writing the control register.
- `vnic_intr_clean()` clears interrupt credits.
- `vnic_intr_free()` drops the MMIO control pointer.

## Control flow and state
Allocation only hooks MMIO resources; no coherent ring is allocated. Initialization writes hardware interrupt policy. Runtime credit return/masking logic is mostly inline in `vnic_intr.h`.

## Dependencies and integration points
It depends on resource discovery and interrupt coalescing conversion from `vnic_dev.c`. ENIC resource initialization configures one `vnic_intr` per firmware interrupt resource.

## Risks and test signals
Risks include wrong coalescing conversion factors, resource absence, and stale credits after reset. Test with coalescing timer changes, INTx/MSI/MSI-X interrupt delivery, mask/unmask behavior, and interrupt credit accounting under load.
