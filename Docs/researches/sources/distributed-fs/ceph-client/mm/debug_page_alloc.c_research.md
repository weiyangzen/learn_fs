# sources/distributed-fs/ceph-client/mm/debug_page_alloc.c

## Purpose
This file implements early configuration and small helpers for debug page allocation and guard pages. It owns static keys used by page allocator debug paths and supports boot parameters for enabling debug page allocation and choosing the guard-page minimum order.

## Important APIs, Types, And Functions
Global state includes `_debug_guardpage_minorder`, `_debug_pagealloc_enabled_early`, `_debug_pagealloc_enabled`, and `_debug_guardpage_enabled`. `_debug_pagealloc_enabled_early` and `_debug_pagealloc_enabled` are exported.

Boot parameter handlers are `early_debug_pagealloc()` for `debug_pagealloc=` and `debug_guardpage_minorder_setup()` for `debug_guardpage_minorder=`.

Allocator helpers are `__set_page_guard()` and `__clear_page_guard()`.

## Control Flow
`early_debug_pagealloc()` parses a boolean string into `_debug_pagealloc_enabled_early`. `debug_guardpage_minorder_setup()` parses an unsigned long, rejects values greater than `MAX_PAGE_ORDER / 2`, stores `_debug_guardpage_minorder`, and logs the configured value.

When the buddy allocator wants to mark a page as a guard page, `__set_page_guard()` rejects orders greater than or equal to `debug_guardpage_minorder()`, sets the guard flag, initializes `buddy_list`, stores the order in page private data, and returns true. `__clear_page_guard()` clears the guard flag and resets private data.

## State And Persistence
Configuration is global and set during early boot. Static keys allow other MM paths to branch efficiently when debug page allocation or guard pages are enabled.

Guard page state is stored in page flags and page private data until cleared.

## Dependencies And Integration Points
The file depends on core MM page flags, page isolation/list definitions, static keys, and early boot parameter parsing. It is integrated into page allocator debug behavior through externally referenced symbols and `debug_guardpage_minorder()`.

## Risks And Edge Cases
Invalid `debug_guardpage_minorder` values are logged and ignored by returning `0` from the early parameter handler. `__set_page_guard()` does not touch zone accounting directly in this file; callers must handle surrounding allocator state correctly.

The order comparison means only orders strictly below the configured minimum become guard pages. Misunderstanding that threshold can disable more or fewer guard pages than expected.

## Test Signals
No direct tests are present here. Validation is mostly via boot-parameter behavior, allocator debug configurations, and runtime page allocator assertions.
