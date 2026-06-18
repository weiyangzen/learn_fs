# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/libcxgb/libcxgb_ppm.c

## Purpose

`libcxgb_ppm.c` implements the Chelsio iSCSI Direct Data Placement PagePod Manager. It allocates and frees page-pod index ranges, builds DDP tags and page-pod headers, initializes shared/per-CPU page-pod pools, and manages the lifetime of a `struct cxgbi_ppm` instance.

## Important APIs, Types, and Functions

- `cxgbi_ppm_find_page_index()` maps a page size to one of the configured DDP page-size indices.
- Allocation helpers: `ppm_find_unused_entries()`, `ppm_get_cpu_entries()`, `ppm_get_entries()`, and `ppm_mark_entries()`.
- Release helpers: `ppm_unmark_entries()` and exported `cxgbi_ppm_ppod_release()`.
- Exported reservation: `cxgbi_ppm_ppods_reserve()` reserves enough page pods for a number of pages and returns both software index and wire DDP tag.
- Exported header builder: `cxgbi_ppm_make_ppod_hdr()` fills `cxgbi_pagepod_hdr` with valid flag, TID, tag bits, max offset, and page offset.
- Lifetime: `cxgbi_ppm_init()`, `cxgbi_ppm_release()`, `ppm_destroy()`, and `ppm_free()`.
- Tag mask sizing: `cxgbi_tagmask_set()`.

## Control Flow

Initialization computes total page pods from iSCSI DDR/EDRAM sizes, optionally reserves per-CPU pools based on `reserve_factor`, allocates one `vzalloc()` block containing `struct cxgbi_ppm`, per-pod data, and the shared bitmap, handles EDRAM/DDR boundary reservation, initializes locks/refcount, copies the tag format, sets base indices, and stores the pointer in the caller's `ppm_pp`. If another initializer wins the race, it frees the new object and increments the existing refcount.

Reservation converts page count to page-pod count, tries the current CPU pool first, then the shared pool, marks caller data and advances color, computes hardware index as `base_idx + idx`, builds a DDP tag with color and optional page selector bits, and returns count/index/tag. Release validates index and `npods`, then clears either the per-CPU bitmap or shared bitmap and rewinds the next search pointer if possible. Header creation masks off wire-only page selector bits and fills a hardware page-pod header.

## State and Persistence Behavior

State is volatile in `struct cxgbi_ppm`: refcount, device pointers, tag format, total/low-limit/base indices, per-CPU pool reservation, shared bitmap, per-pod metadata (`color`, `npods`, `caller_data`), and next-search cursors. Per-CPU pools use their own spinlocks; shared allocation uses `map_lock`. Refcount release clears the caller's ppm pointer and frees pools/object.

## Dependencies and Integration Points

The file depends on Linux bitmap, per-CPU allocation, scatterlist/SKB/PIC headers, Chelsio iSCSI page-pod types from `libcxgb_ppm.h`, and exports symbols for Chelsio iSCSI consumers.

## Risks and Edge Cases

- The extra-bit mask calculation compares `ppod_bmap_size >> 3` to pod count; bitmap sizing logic should be verified for non-multiple-of-word pod counts.
- `cxgbi_ppm_ppod_release()` does not clear `pdata->npods` after unmarking, so double release is only guarded if bitmap state or caller discipline prevents it.
- Per-CPU allocation uses `get_cpu()`/`put_cpu()` before locking the pool pointer; migration is disabled only during pointer acquisition.
- EDRAM/DDR contiguity assumptions reject noncontiguous regions and reserve one boundary pod.

## Test Signals

Test initialization with DDR-only, EDRAM+DDR contiguous, noncontiguous EDRAM rejection, reserve factor on/off, page size mapping, reserve/release wraparound, per-CPU and shared fallback allocation, DDP tag color rollover, tag page selector bits, concurrent reserve/release, and refcounted double initialization/release.
