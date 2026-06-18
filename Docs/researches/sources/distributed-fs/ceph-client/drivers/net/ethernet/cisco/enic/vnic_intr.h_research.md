# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_intr.h

## Purpose
`vnic_intr.h` defines the vNIC interrupt-control MMIO layout, software interrupt object, inline mask/credit helpers, and interrupt management prototypes.

## Important APIs, types, and functions
- `struct vnic_intr_ctrl` mirrors coalescing, mask, credit, and credit-return registers.
- `struct vnic_intr` stores index, vNIC device pointer, and MMIO control pointer.
- Inline helpers: `vnic_intr_unmask()`, `vnic_intr_mask()`, `vnic_intr_masked()`, `vnic_intr_return_credits()`, `vnic_intr_credits()`, `vnic_intr_return_all_credits()`, and `vnic_intr_legacy_pba()`.
- Constants define absolute and quiet coalescing timer modes.

## Control flow and state
The credit-return helper packs credit count, unmask, and reset-timer bits into one register write. Mask helpers write direct MMIO bits. The legacy PBA helper reads pending state without clearing.

## Dependencies and integration points
This header is used by ENIC interrupt handlers and resource initialization. It depends on `vnic_dev.h` for conversion and vdev references.

## Risks and test signals
Wrong bit packing can lose interrupts or leave vectors masked. Test interrupt moderation, credit return after NAPI, MSI-X vector masking, and INTx legacy pending-bit reads.
