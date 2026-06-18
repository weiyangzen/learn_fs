
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mmio_types.h

## Purpose

`xe_mmio_types.h` defines the persistent data structures used by Xe MMIO register access code: an MMIO region descriptor and a simple register-range descriptor.

## Important APIs, Types, and Functions

- `struct xe_mmio`: tile backpointer, mapped `regs` pointer, optional SR-IOV VF GT backpointer, register-region size, and address-adjustment fields.
- `struct xe_mmio_range`: inclusive `[start, end]` register range used by validation and filtering code.

## Control Flow

The structures are initialized by `xe_mmio_init()` or specialized SR-IOV helpers and then passed into `xe_mmio_*` accessors. Range tables are walked by helpers such as OA config validation.

## State and Persistence Behavior

`struct xe_mmio` persists for device/tile/GT lifetime and may share the same underlying ioremap with other regions. Its adjustment fields persistently affect all future accesses through that instance.

## Dependencies and Integration Points

The types are embedded in tile and GT objects and are used across IRQ, query, OA, MOCS, PAT, GSC, VRAM, hwmon, and workaround code.

## Risks and Edge Cases

Incorrect `regs_size`, `adj_limit`, or `adj_offset` values are global hazards for all register users of a region. `sriov_vf_gt` is only meaningful for GT MMIO while running as an SR-IOV VF.

## Test Signals

Structural compile coverage plus runtime assertions around size limits, address adjustment, and SR-IOV VF-specific access paths are the main signals.
