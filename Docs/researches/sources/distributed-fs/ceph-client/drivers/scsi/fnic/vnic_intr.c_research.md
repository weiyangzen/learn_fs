# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_intr.c

## Purpose

`vnic_intr.c` implements basic allocation, initialization, cleanup, and release of vNIC interrupt control resources.

## Important APIs, types, and functions

- `vnic_intr_alloc()` binds a software interrupt object to a `RES_TYPE_INTR_CTRL` MMIO resource.
- `vnic_intr_init()` programs coalescing timer, coalescing type, mask-on-assertion behavior, and clears credits.
- `vnic_intr_clean()` clears interrupt credits.
- `vnic_intr_free()` drops the MMIO control pointer.

## Control flow

Probe/setup allocates one interrupt control object per vector and initializes coalescing policy. Runtime code uses inline helpers from `vnic_intr.h` to mask, unmask, and return credits. Teardown clears software pointers.

## State and persistence behavior

State is primarily hardware register state in `struct vnic_intr_ctrl`. The software object persists an index, device pointer, and MMIO control address.

## Dependencies and integration points

The file depends on `vnic_dev_get_res()` and the register layout from `vnic_intr.h`. It integrates with FNIC interrupt setup and completion servicing.

## Risks and edge cases

- Missing interrupt control resources return `-EINVAL`, so probe must handle partial resource tables.
- Coalescing timer values are not range-checked here; callers must respect hardware limits.

## Test signals

Tests should cover vector allocation, coalescing initialization, mask/unmask and credit-return behavior, and cleanup during reset/remove.
