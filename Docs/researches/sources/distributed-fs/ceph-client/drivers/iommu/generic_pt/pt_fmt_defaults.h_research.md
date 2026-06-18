# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/pt_fmt_defaults.h

## Purpose

`pt_fmt_defaults.h` supplies default Generic PT format callbacks for common radix geometry, no-contiguous mappings, no dirty tracking, OA/item conversion, max output address, system page-size support, entry clearing, software-bit helpers, and leaf argument validation.

## Important APIs, Types, and Functions

- Defaults for `pt_table_item_lg2sz`, `pt_pgsz_lg2_to_level`, `pt_entry_num_contig_lg2`, `pt_contig_count_lg2`, `pt_dirty_supported`, `pt_entry_make_write_dirty`, `pt_possible_sizes`, and `pt_full_va_prefix`.
- OA conversion helpers that derive `pt_item_oa` from `pt_entry_oa` or vice versa.
- `pt_clear_entries32`, `pt_clear_entries64`, and generic `pt_clear_entries`.
- Software-bit helpers `pt_test_sw_bit_acquire` and `pt_set_sw_bit_release` when a format defines `pt_sw_bit`; otherwise trap-like stubs call `__pt_no_sw_bit`.
- `pt_check_install_leaf_args`: shared validation for leaf alignment, size, and index alignment.

## Control Flow

After a format header defines its specialized callbacks, `pt_common.h` includes this file to fill gaps. Generic template code then calls the uniform callback names without caring whether the implementation is format-specific or default.

## State and Persistence Behavior

Defaults operate on current page-table memory through `pt_state`. Software-bit helpers update entries atomically and use acquire/release barriers for DMA-incoherent synchronization markers.

## Dependencies and Integration Points

It depends on `pt_defs.h`, Linux log2 helpers, and optional format-provided macros. All Generic PT formats transitively use at least some defaults.

## Risks and Edge Cases

- Fallbacks can hide a missing format implementation; tests must ensure defaults are intended.
- Software-bit stubs deliberately reference `__pt_no_sw_bit` so accidental use without format support fails at link/runtime.
- `pt_check_install_leaf_args` uses Generic PT invariants and cannot validate hardware-specific reserved-bit constraints.

## Test Signals

KUnit should cover formats relying on defaults and formats overriding them, especially page-size computation, entry clearing, software-bit synchronization, and invalid leaf-install arguments under debug checks.
