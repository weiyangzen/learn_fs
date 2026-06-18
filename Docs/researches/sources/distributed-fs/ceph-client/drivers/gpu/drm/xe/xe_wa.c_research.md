# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_wa.c

## Purpose

`xe_wa.c` defines and processes Xe hardware workaround tables. It covers GT-level register workarounds, engine reset workarounds, LRC/context-image workarounds, generated out-of-band GT/device workarounds, active-workaround bookkeeping, debug dumps, and rare tile-level workaround programming.

## Important APIs, Types, and Functions

The main static data tables are `gt_was[]`, `engine_was[]`, and `lrc_was[]`, each containing `xe_rtp_entry_sr` records with WA names, RTP match rules, and register actions. `oob_was[]` and `device_oob_was[]` include generated C fragments from rule files and are checked against generated counts with `static_assert()`.

Public processing functions are `xe_wa_process_device_oob()`, `xe_wa_process_gt_oob()`, `xe_wa_process_gt()`, `xe_wa_process_engine()`, and `xe_wa_process_lrc()`. Initialization functions are `xe_wa_device_init()` and `xe_wa_gt_init()`. Dump helpers are `xe_wa_device_dump()` and `xe_wa_gt_dump()`. `xe_wa_apply_tile_workarounds()` directly applies uncommon non-GT tile workarounds such as `22010954014` by MMIO RMW when active.

## Control Flow and State

During initialization, `xe_wa_device_init()` allocates a device OOB active bitset and `xe_wa_gt_init()` allocates one contiguous bitset block split across GT, engine, LRC, and OOB active categories. OOB processing builds an `xe_rtp_process_ctx`, enables active tracking, marks OOB initialized, and evaluates generated RTP entries to set active bits. GT, engine, and LRC processing evaluate static tables and store matching register actions into `gt->reg_sr`, `hwe->reg_sr`, or `hwe->reg_lrc`.

The tables are declarative: match rules cover platform, graphics/media version ranges, steps, subplatforms, engine classes, first render/compute selection, even engine instances, SR-IOV exclusion, and other helper predicates. Actions set, clear, or field-set register bits, sometimes with engine-base addressing or readback suppression flags.

## Dependencies and Integration Points

This file depends on the Xe RTP infrastructure, GT and engine types, register definitions, forcewake/MMIO infrastructure, platform and stepping helpers, SR-IOV predicates, generated WA headers and C fragments, and DRM managed memory. Processed register save/restore lists are consumed by GT reset/resume code, engine reset/GuC ADS setup, and LRC/default context setup. OOB bits are queried through `XE_GT_WA()` and `XE_DEVICE_WA()` in other files.

## Risks and Edge Cases

WA table maintenance is high-risk because a too-broad range can program unsupported registers on future IP versions, while a too-narrow range can miss required programming. Readback masks and `XE_RTP_NOCHECK` must be used only where hardware makes read verification impossible or misleading. Active bitset sizes must match table sizes, especially for generated OOB tables. Tile workaround application must skip SR-IOV VFs and should remain rare because it bypasses the RTP save/restore path.

## Test Signals

KUnit or simulated platform tests should verify RTP matching for representative platforms, steps, engine classes, first render/compute predicates, and SR-IOV cases. Static assertions catch generated OOB count drift. Dump tests can confirm active bit names appear. Probe error-injection for `xe_wa_gt_init()` should exercise `ALLOW_ERROR_INJECTION`. Register programming tests should validate GT/engine/LRC save-restore lists and tile RMW behavior for active device WA bits.
