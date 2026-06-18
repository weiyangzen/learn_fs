# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/pt_defs.h

## Purpose

`pt_defs.h` provides the foundational Generic PT language, core types, feature gating, address arithmetic wrappers, atomic table-install helpers, top-table encoding, and debug assertion behavior.

## Important APIs, Types, and Functions

- Core types: `enum pt_entry_type`, `struct pt_range`, `struct pt_state`, and forward `struct pt_table_p`.
- Feature gates: `PT_SUPPORTED_FEATURES`, `PT_FORCE_ENABLED_FEATURES`, `pt_feature`, and `pts_feature`.
- Atomic install helpers: `pt_table_install64` and `pt_table_install32`.
- `PT_WARN_ON`: debug-only invariant reporting.
- VA/OA log2 arithmetic aliases and full-VA variants.
- Top pointer helpers: `_pt_top_set`, `pt_top_set`, `pt_top_set_level`, `pt_top_get_level`.

## Control Flow

Every format instantiation includes this before its format header and before `pt_common.h`. It normalizes feature availability, expands debug-mode feature matrices, and provides low-level helpers used by descriptor callbacks and walkers.

## State and Persistence Behavior

`struct pt_range` captures a snapshot of the root table pointer, top level, current VA interval, and maximum VA width. `struct pt_state` captures a walker position and loaded entry. `top_of_table` stores a pointer with low bits reserved for top-level encoding.

## Dependencies and Integration Points

It depends on `linux/generic_pt/common.h`, atomics, bit helpers, Kconfig, and `pt_log2.h`. It is the base include for all Generic PT implementation files.

## Risks and Edge Cases

- Pointer/level packing assumes table alignment leaves enough low bits for `PT_TOP_LEVEL_BITS`.
- Debug mode rewrites supported feature masks, so production and debug behavior can differ intentionally.
- `pt_table_install64` is unavailable under `CONFIG_GENERIC_ATOMIC64`, matching Kconfig restrictions.
- Full-VA helper variants are needed because shifting by the type width would be undefined.

## Test Signals

Build all formats in debug and non-debug modes. KUnit bitops and top-range tests validate arithmetic, feature handling, range construction, and atomic install assumptions.
