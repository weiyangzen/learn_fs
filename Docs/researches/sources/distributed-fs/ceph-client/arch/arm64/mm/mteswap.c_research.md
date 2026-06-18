# sources/distributed-fs/ceph-client/arch/arm64/mm/mteswap.c

## Purpose
This file preserves ARM64 MTE allocation tags across swap-out and swap-in. Because tags are separate metadata from page contents, the file stores per-page tag snapshots in an xarray keyed by swap entry value and restores them when swapped pages return.

## Important APIs, Types, and Functions
Persistent storage is `static DEFINE_XARRAY(mte_pages)`. Public helpers include `mte_allocate_tag_storage()`, `mte_free_tag_storage()`, `mte_save_tags()`, `mte_restore_tags()`, `mte_invalidate_tags()`, `mte_invalidate_tags_area()`, `arch_prepare_to_swap()`, and `arch_swap_restore()`. Internal cleanup helper `__mte_invalidate_tags()` derives the swap entry from a page.

## Control Flow
`arch_prepare_to_swap()` exits immediately without MTE support. Otherwise it iterates over each page in the folio and calls `mte_save_tags()`. `mte_save_tags()` skips untagged pages, allocates `MTE_PAGE_TAG_STORAGE`, saves tags from `page_address(page)`, and stores the buffer in `mte_pages` under `page_swap_entry(page).val`; replacement frees the old buffer. On failure, `arch_prepare_to_swap()` invalidates entries saved earlier in the folio.

`arch_swap_restore()` iterates over folio pages and increasing swap entries. `mte_restore_tags()` loads the saved buffer, attempts to enable page tagging with `try_page_mte_tagging()`, restores tags, and marks the page tagged. `mte_invalidate_tags()` and `mte_invalidate_tags_area()` erase per-entry or whole-swap-type metadata and free buffers.

## State and Persistence
Tag snapshots persist in the `mte_pages` xarray while the corresponding swap entries remain valid. The key is the raw `swp_entry_t.val`, so state lifetime must track swap invalidation. The page's `page_mte_tagged` state controls whether tags are saved and is restored after successful tag restoration.

## Dependencies and Integration Points
The file integrates with generic swap through `arch_prepare_to_swap()` and `arch_swap_restore()`, with swap invalidation through `mte_invalidate_tags*()`, with xarray for indexed storage, and with ARM64 MTE primitives such as `mte_save_page_tags()`, `mte_restore_page_tags()`, `try_page_mte_tagging()`, and `set_page_mte_tagged()`.

## Risks
Leaking tag buffers is the main state risk if swap invalidation paths miss an entry. Incorrect entry arithmetic for multi-page folios could restore tags to the wrong page. Allocation failure during swap preparation must clean up already-saved tags for the folio, which this file handles. Concurrency relies on xarray locking semantics; direct area invalidation uses explicit `xa_lock()`.

## Test Signals
MTE swap tests should allocate tagged memory, force swap-out/in, and verify tag preservation. Swapoff or swap-area invalidation should leave no leaked buffers. Multi-page folio swapping is an important edge case. Error-injection for `kmalloc()` or `xa_store()` should exercise cleanup.
