
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mocs.c

## Purpose

`xe_mocs.c` defines and programs platform-specific MOCS/L3 cacheability tables for Xe GTs. It selects uncached/writeback indices used elsewhere, writes global MOCS and LNCF/L3CC registers, and supports debug dumping of programmed table state.

## Important APIs, Types, and Functions

- Data model: `struct xe_mocs_entry`, `struct xe_mocs_info`, and `struct xe_mocs_ops`.
- Platform tables: Gen12, DG1, DG2, PVC, Meteor Lake, Xe2, and Xe3P/Crescent Island variants.
- Selection and lookup: `get_mocs_settings()`, `get_entry_control()`, `get_entry_l3cc()`, and `l3cc_combine()`.
- Programming: `xe_mocs_init_early()`, `xe_mocs_init()`, `__init_mocs_table()`, and `init_l3cc_table()`.
- Diagnostics: `xe_mocs_dump()` with per-platform dump callbacks.

## Control Flow

Early GT init calls `xe_mocs_init_early()` to populate `gt->mocs.uc_index` and `gt->mocs.wb_index`. Full init skips SR-IOV VFs, selects the platform table, decides whether global MOCS and/or LNCF MOCS registers are present, and writes each register either through MCR multicast or direct MMIO depending on platform/GT type. Dumping takes runtime PM and forcewake, then reads and prints the relevant registers.

## State and Persistence Behavior

The programmed register state persists in hardware until reset/reprogramming. The selected UC/WB indices persist in `gt->mocs` for command emitters such as migration copy/clear and OA programming. Undefined table entries are filled from `unused_entries_index` to keep hardware registers deterministic.

## Dependencies and Integration Points

MOCS depends on platform info, GT type, MCR register access, MMIO helpers, forcewake/runtime PM, SR-IOV mode checks, and register definitions. MOCS indices are consumed by batch emitters and other memory-transaction programming paths.

## Risks and Edge Cases

- MOCS tables are hardware ABI; changing existing entries can break userspace assumptions.
- Missing `unused_entries_index` is asserted because index 0 is not a safe default on most platforms.
- DG2 leaves the last entry out of validation because hardware treats it as read-only.
- SR-IOV VFs skip programming, so PF/firmware must provide usable state.
- Dumping requires forcewake domain selection to match table type.

## Test Signals

KUnit coverage via `tests/xe_mocs.c`, platform table selection tests, register write/readback dumps, forcewake timeout tests, and validation that `gt->mocs.uc_index`/`wb_index` match expected platform values are useful signals.
