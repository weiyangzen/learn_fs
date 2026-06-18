# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khrescache.h

## Purpose

`khrescache.h` declares small UI resource-cache helpers for bitmaps and custom image lists. It lets NetIDMgr cache GDI bitmaps by resource ID, wrap bitmap dimensions, and draw masked image-list entries without repeatedly loading or recomputing resources.

## Important APIs, Types, and Functions

- `khui_init_rescache()` and `khui_exit_rescache()` start and stop global resource caching.
- `khui_cache_bitmap()` stores an `HBITMAP` by numeric ID, and `khui_get_cached_bitmap()` retrieves it.
- `khui_bitmap` wraps an `HBITMAP` with dimensions.
- `khui_bitmap_from_hbmp()`, `khui_delete_bitmap()`, and `khui_draw_bitmap()` manage/draw bitmap wrappers.
- `khui_ilist` stores cell dimensions, capacity/growth counters, backing image and mask bitmaps, usage count, and an optional ID list.
- Image-list APIs create/delete lists, add masked bitmaps with optional IDs, look up IDs, and draw by index or ID with optional background color.
- `KHUI_SMICON_CX` and `KHUI_SMICON_CY` define 16x16 small icon dimensions.

## Control Flow

The UI initializes the cache, loads bitmaps once, wraps them or adds them to image lists, then draws cached images into device contexts during window painting. ID-based image lists allow callers to decouple credential or status type IDs from physical image indices. Exit tears down cached GDI resources.

## State and Persistence Behavior

Resource-cache contents and image lists are in-process GDI state. They are not persisted across sessions. Ownership must be clear: cached bitmaps and image-list backing bitmaps should be deleted exactly once by cache/list teardown or explicit bitmap delete APIs.

## Dependencies and Integration Points

The header depends on `khdefs.h` and Win32 GDI types (`HBITMAP`, `HDC`, `COLORREF`, `BOOL`). It is included by `khuidefs.h` and used by UI components, alerts, action lists, credential displays, and plugin icons.

## Risks and Edge Cases

- GDI handle leaks are the main risk if callers bypass delete APIs or cache the same ID repeatedly without defined replacement semantics.
- Drawing by ID uses `khui_ilist_lookup_id()` inline; if lookup returns an invalid index, draw code must handle it.
- Image-list growth fields (`n`, `ng`, `nused`) require bounds checking in implementation.
- Bitmap dimensions must be valid before drawing; zero-size or deleted handles should be rejected.

## Test Signals

- Initialize/exit repeatedly under leak checking for GDI object counts.
- Cache duplicate IDs and verify replacement or rejection behavior.
- Add masked images until growth occurs and draw every index.
- Lookup missing IDs and confirm draw-by-ID fails safely.
