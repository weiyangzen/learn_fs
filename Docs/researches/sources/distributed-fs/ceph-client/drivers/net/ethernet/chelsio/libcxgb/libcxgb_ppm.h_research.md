# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/libcxgb/libcxgb_ppm.h

## Purpose

`libcxgb_ppm.h` defines the data structures, tag format, constants, inline tag helpers, and exported function prototypes for Chelsio iSCSI Direct Data Placement page-pod management.

## Important APIs, Types, and Functions

- Hardware structures: `struct cxgbi_pagepod_hdr` and `struct cxgbi_pagepod`.
- Task mapping: `struct cxgbi_task_tag_info` records per-task DDP mapping flags, page size, pod count, index/tag, header, and scatterlist metadata.
- Tag layout: `struct cxgbi_tag_format` stores page-size order, default index, free/color/index/reserved bit counts, and masks.
- Pool state: `struct cxgbi_ppm_pool` and `struct cxgbi_ppm`.
- Inline helpers include DDP/non-DDP tag checks and conversion, `cxgbi_ppm_make_non_ddp_tag()`, `cxgbi_ppm_decode_non_ddp_tag()`, `cxgbi_ppm_ddp_tag_get_idx()`, `cxgbi_ppm_make_ddp_tag()`, `cxgbi_ppm_get_tag_caller_data()`, `cxgbi_ppm_ddp_tag_update_sw_bits()`, `cxgbi_ppm_ppod_clear()`, and `cxgbi_tagmask_check()`.
- Exported prototypes include page index lookup, page-pod header creation, reserve/release/init/release, tagmask check/set.

## Control Flow

Consumers use `cxgbi_tagmask_check()` to derive tag bit layout from a hardware tag mask, initialize a PPM with `cxgbi_ppm_init()`, reserve page-pod ranges with `cxgbi_ppm_ppods_reserve()`, build page-pod headers with `cxgbi_ppm_make_ppod_hdr()`, and release ranges with `cxgbi_ppm_ppod_release()`. Inline tag helpers encode/decode DDP tags and preserve non-DDP software tags by inserting/removing the no-DDP marker bit.

## State and Persistence Behavior

The header defines the in-memory PPM state. Per-pod `cxgbi_ppod_data` tracks color, channel, pod count, and caller data. The tag format determines how 32-bit tags are interpreted and is copied into the PPM at initialization. No persistent storage is involved.

## Dependencies and Integration Points

It depends on Linux kernel, debugfs, list, netdevice, scatterlist, SKB, vmalloc, and bitmap APIs. It integrates with Chelsio iSCSI drivers that need DDP page-pod tags.

## Risks and Edge Cases

- Tag helper arithmetic is mask/shift sensitive; invalid tagmask values could produce negative or nonsensical bit allocations.
- `cxgbi_ppm_make_non_ddp_tag()` rejects software tags using bit 31 and treats zero specially as exactly `no_ddp_mask`.
- `cxgbi_ppm_ddp_tag_update_sw_bits()` validates free-bit capacity but depends on the original tag being a DDP tag.
- `PPOD_PI_EXTRACT_CTL_FLAG` references a `V_` macro name that is not defined in this header, so consumers should verify compile coverage for that macro path.

## Test Signals

Unit-style tests can validate tagmask-derived masks, DDP tag index/color extraction, non-DDP tag round trips, SW-bit update bounds, default page-size index, page-pod header clearing, and compile coverage of all macros used by consumers.
