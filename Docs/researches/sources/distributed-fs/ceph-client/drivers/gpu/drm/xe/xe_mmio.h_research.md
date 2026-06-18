
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mmio.h

## Purpose

`xe_mmio.h` declares the Xe MMIO mapping and register accessor interface and provides the inline address-adjustment helper shared by low-level register users.

## Important APIs, Types, and Functions

The header exposes probe functions, `xe_mmio_init()`, typed accessors, read-modify-write, write-and-verify, range checking, 64-bit split reads, wait-until-match/not-match helpers, and `xe_mmio_init_vf_view()` when PCI IOV is enabled. `xe_mmio_adjusted_addr()` applies `adj_offset` to addresses below `adj_limit`.

## Control Flow

Callers initialize a `struct xe_mmio` with a tile, pointer, and size, then pass `struct xe_reg` descriptors to accessors. Address adjustment happens inline before the implementation touches hardware.

## State and Persistence Behavior

The header does not own state, but its inline helper defines how persistent `adj_limit`/`adj_offset` fields in `struct xe_mmio` affect all users.

## Dependencies and Integration Points

It includes `xe_mmio_types.h` and forward declares `xe_device`/`xe_reg`. It is included by most Xe hardware programming modules.

## Risks and Edge Cases

Consumers must pass valid `struct xe_reg` offsets for the target region. Incorrect adjustment fields can silently redirect every access below the limit.

## Test Signals

Build coverage catches API drift. Focused tests should validate adjusted and non-adjusted addresses, including boundary `addr == adj_limit`.
