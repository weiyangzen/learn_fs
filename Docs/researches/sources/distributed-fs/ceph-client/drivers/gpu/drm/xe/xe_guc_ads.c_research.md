# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_ads.c

## Purpose

`xe_guc_ads.c` builds and populates the GuC Additional Data Structures blob. The ADS is a single pinned mapped BO containing the GuC ADS header, scheduler policies, GT system info, engine usage, UM queue parameters, MMIO save/restore regsets, golden LRCs, workaround KLVs, capture lists, UM queues, and firmware private data.

## Important APIs, Types, and Functions

- `xe_guc_ads_init()` computes pre-hwconfig worst-case sizes and allocates the ADS BO.
- `xe_guc_ads_init_post_hwconfig()` recalculates sizes after engine discovery and asserts they fit the original allocation slack.
- `xe_guc_ads_populate_minimal()` writes enough ADS state for minimal GuC load and hwconfig retrieval.
- `xe_guc_ads_populate()` writes full policies, engine masks, regsets, golden LRC addresses, mapping table, capture lists, doorbell info, workaround KLVs, UM queues, and ADS pointers.
- `xe_guc_ads_populate_post_load()` copies captured default LRC images into the ADS.
- `xe_guc_ads_scheduler_policy_toggle_reset()` sends an updated policy buffer over CT.
- Static helpers calculate region sizes/offsets, write regsets, populate capture-list pointers, and build workaround KLVs.

## Control Flow

The ADS layout starts with fixed structs and then page-aligns dynamic regions. Init calculates golden LRC, capture, regset, and workaround sizes, then allocates a BO with extra golden-LRC slack. Minimal population zeroes the BO and writes policies, invalid mapping, golden context addresses, doorbell count, and key ADS pointers. Full population zeroes again, fills engine masks from discovered hardware engines, serializes save/restore MMIO registers including MCR steering metadata, prepares capture lists, writes workaround KLVs, initializes UM queue parameters if USM is supported, and points GuC ADS fields at GGTT offsets.

## State and Persistence Behavior

Persistent ADS metadata lives in `struct xe_guc_ads` and the BO contents consumed by GuC firmware. The BO is managed and pinned for the GuC lifetime. Population is destructive because it clears the whole BO before rebuilding. Scheduler policy toggling uses a temporary GuC buffer cache allocation and does not rewrite the main ADS in place except for reading defaults.

## Dependencies and Integration Points

This file integrates GuC ABI structures, hardware engine lists, register save/restore xarrays, LRC sizing/default LRC data, capture-list generation, MCR steering, workarounds, UM/page-response queues, GGTT BO mapping, CT commands, and GT/DRM logging.

## Risks and Edge Cases

Offset/size arithmetic is ABI-critical. Post-hwconfig size growth relies on `MAX_GOLDEN_LRC_SIZE` slack. Capture-list population logs overflow but continues by writing null lists when unavailable. Workaround KLV buffer size is fixed to one page and excess KLVs only warn. Regset sizing includes slack; missing a new extra register can overflow assertions.

## Test Signals

Tests should validate region offsets/alignment, minimal versus full ADS pointer fields, engine enable masks, mapping-table invalid values, regset counts, MCR steering flags, capture-list size accounting, KLV population under workaround combinations, and policy-toggle CT payloads. Fault injection on ADS allocation is already enabled.
