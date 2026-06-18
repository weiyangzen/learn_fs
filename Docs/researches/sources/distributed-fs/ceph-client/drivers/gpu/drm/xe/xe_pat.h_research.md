<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pat.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pat.h

## Purpose

`xe_pat.h` is the public interface for Xe PAT setup and introspection. It defines the PAT table entry metadata shared with the rest of the driver, cache/coherency constants, and the functions used during early device setup, GT hardware programming, page-table encoding, and diagnostics.

## Important APIs and Types

`struct xe_pat_table_entry` contains a platform-specific register `value`, a normalized `coh_mode`, and a `valid` bit for reserved entries. `XE_COH_NONE`, `XE_COH_1WAY`, and `XE_COH_2WAY` are the normalized coherency modes. `XE_PAT_INVALID_IDX` marks absent cache-level mappings. Exported functions are `xe_pat_init_early()`, `xe_pat_init()`, `xe_pat_dump()`, `xe_pat_dump_sw_config()`, `xe_pat_index_get_coh_mode()`, `xe_pat_index_get_comp_en()`, and `xe_pat_index_get_l3_policy()`. The header also publishes the L3 policy constants `XE_L3_POLICY_WB`, `XE_L3_POLICY_XD`, and `XE_L3_POLICY_UC`.

## Control Flow and State

Callers initialize software PAT selection once per device with `xe_pat_init_early()`, program each GT with `xe_pat_init()`, and later query table metadata by PAT index. The header itself stores no state; it exposes access to `xe_device` state filled by `xe_pat.c`.

## Dependencies and Integration Points

The interface is consumed by device probe, GT initialization, debug printers, BO/page-table encoding, and any logic that needs to inspect cacheability, coherency, compression, or L3 policy from a selected PAT index.

## Risks and Test Signals

Because this header is a cross-module contract, enum-like constants and function semantics must stay synchronized with `xe_pat.c` and `xe_pt_types.h`. Test signals include successful compile coverage across PAT users, valid behavior for invalid cache mappings, and platform tests that verify compression and coherency metadata match the programmed table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pat.h -->
