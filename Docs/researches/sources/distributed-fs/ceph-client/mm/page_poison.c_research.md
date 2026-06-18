# sources/distributed-fs/ceph-client/mm/page_poison.c

## Purpose
`page_poison.c` implements debug page poisoning for the page allocator. When enabled, freed pages are filled with `PAGE_POISON`; allocation checks verify the pattern to detect use-after-free or memory corruption.

## Important APIs, Types, And Functions
- `_page_poisoning_enabled_early` and `_page_poisoning_enabled` expose boot-time and static-key runtime enable state.
- `early_page_poison_param()` parses `page_poison=`.
- `__kernel_poison_pages()` fills one or more pages with the poison byte.
- `__kernel_unpoison_pages()` checks one or more pages before reuse.
- `check_poison_mem()` locates the corrupt range, distinguishes single-bit flips, prints a hex dump, stack, and page details under rate limiting.
- `__kernel_map_pages()` is a no-op fallback when architecture debug-pagealloc unmapping is unavailable.

## Control Flow
On free, allocator hooks call `__kernel_poison_pages()`, which locally maps each page, disables KASAN for the current task, clears any memory tag before `memset()`, and unmaps. On allocation, `__kernel_unpoison_pages()` maps each page and calls `check_poison_mem()` over the full page. The checker returns silently for intact poison, otherwise rate limits error reporting and emits diagnostics.

## State And Persistence Behavior
State is the byte pattern stored in freed page memory plus enable flags/static key. There is no persistent storage. KASAN state is temporarily disabled only around the poison memory access so KASAN does not treat the deliberately poisoned free page as normal in-use memory.

## Dependencies And Integration Points
The file integrates with page allocator debug hooks, early kernel parameters, static keys exported to other MM code, highmem local mapping, KASAN tag reset/disable helpers, ratelimited printk, hex dumps, `dump_stack()`, and `dump_page()`.

## Risks
- It is a debug feature with significant memory bandwidth cost on free and allocation.
- Corruption reports are sampled by rate limiting; repeated corruptions can be suppressed.
- The check assumes every freed page was poisoned, so partial or skipped poisoning in caller paths would cause false positives.
- KASAN interaction must keep tag reset and disable/enable balanced.

## Test Signals
- Boot with `page_poison=on` and allocate/free pages across orders and highmem-capable paths.
- Deliberately corrupt a freed page in a test module and verify single-bit versus general corruption messages.
- Run with KASAN enabled to ensure poisoning does not trigger spurious sanitizer reports.
