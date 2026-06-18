# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/pt_common.h

## Purpose

`pt_common.h` documents and declares the Generic PT format callback API, then layers common inline helpers on top of format-specific implementations and defaults.

## Important APIs, Types, and Functions

- Format callback contracts: `pt_attr_from_entry`, `pt_can_have_leaf`, `pt_clear_entries`, dirty helpers, `pt_entry_oa`, `pt_install_leaf_entry`, `pt_install_table`, `pt_load_entry_raw`, `pt_num_items_lg2`, `pt_possible_sizes`, `pt_table_pa`, and more.
- Derived helpers: `pt_entry_oa_lg2sz`, `pt_entry_oa_exact`, `pt_item_oa`, `pt_load_entry`, `pt_table_item_lg2sz`, `pt_table_oa_lg2sz`, `pt_table_ptr`, `pt_max_sw_bit`.
- Includes `pt_fmt_defaults.h` to supply missing optional callbacks.

## Control Flow

Format headers are included before this file and define macros mapping generic names to format-specific functions. `pt_common.h` then exposes a uniform API to walkers and IOMMU template code. `pt_load_entry` wraps raw entry loading and populates derived table pointers for table entries.

## State and Persistence Behavior

The helpers operate on `struct pt_common`, `struct pt_range`, and `struct pt_state` but do not own memory. They interpret current entry state and compute derived addresses, sizes, and capabilities.

## Dependencies and Integration Points

It depends on `pt_defs.h`, selected format headers, and `pt_fmt_defaults.h`. It is consumed by `pt_iter.h`, `iommu_pt.h`, and KUnit template headers.

## Risks and Edge Cases

- The callback API is macro-based; missing or incorrectly named format functions may silently fall back to defaults where that is not intended.
- Derived address helpers depend on correct contiguous-entry behavior from formats.
- Dirty and software-bit helpers may be absent depending on format support, changing generated IOMMU capabilities.

## Test Signals

`kunit_generic_pt.h` is the primary validation surface for callback contracts, including attribute round-trip, OA decode, page-size reporting, table pointer encode/decode, dirty helpers, and fallback defaults.
