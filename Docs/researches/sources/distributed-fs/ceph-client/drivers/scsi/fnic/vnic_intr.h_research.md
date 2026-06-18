# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_intr.h

## Purpose

`vnic_intr.h` defines vNIC interrupt control registers and inline helpers for masking, unmasking, credit accounting, and legacy PBA reads.

## Important APIs, types, and data

- `VNIC_INTR_TIMER_MAX` bounds the coalescing timer.
- `VNIC_INTR_TIMER_TYPE_ABS` and `VNIC_INTR_TIMER_TYPE_QUIET` define coalescing modes.
- `struct vnic_intr_ctrl` maps coalescing, mask, credit, and credit-return registers.
- `struct vnic_intr` stores vector index, device pointer, and MMIO control pointer.
- Inline helpers: `vnic_intr_unmask()`, `vnic_intr_mask()`, `vnic_intr_return_credits()`, `vnic_intr_credits()`, `vnic_intr_return_all_credits()`, and `vnic_intr_legacy_pba()`.

## Control flow

Completion handling typically reads/returns credits and optionally unmasks and resets the coalescing timer in one write to `int_credit_return`. Mask and unmask helpers directly write the `mask` register.

## State and persistence behavior

Interrupt state persists in hardware registers. Credits represent completion/interrupt work acknowledged back to the device.

## Dependencies and integration points

It depends on MMIO accessors and `vnic_dev.h`. It integrates with CQ servicing and interrupt-vector management in FNIC.

## Risks and edge cases

- Credit return packs credits, unmask, and reset-timer bits into one register; incorrect bit shifts can cause interrupt storms or stalls.
- `vnic_intr_legacy_pba()` intentionally reads without clearing, so callers must not assume acknowledgement.
- Timer range checking is left to callers.

## Test signals

Hardware tests should verify interrupt masking, credit return after CQ service, coalescing modes, and legacy PBA behavior under INTx.
