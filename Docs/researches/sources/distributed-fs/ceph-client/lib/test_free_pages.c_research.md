
# sources/distributed-fs/ceph-client/lib/test_free_pages.c

## Purpose

This module stress-tests `free_pages()` behavior when a page has a speculative reference, checking that compound and non-compound high-order page frees do not leak memory.

## Important APIs, Types, And Functions

`test_free_pages(gfp_t gfp)` loops one million times, allocates order-3 pages with `__get_free_pages()`, gets the first page, calls `get_page()`, frees the allocation with `free_pages()`, then drops the speculative reference with `put_page()`. `m_in()` runs this once with `GFP_KERNEL` and once with `GFP_KERNEL | __GFP_COMP`.

## Control Flow And State

All work happens during module init. There is no persistent state and exit is a no-op. The loop stresses reference accounting and freeing paths under repeated allocations.

## Dependencies And Integration Points

It depends on the page allocator, page reference APIs, `virt_to_page()`, and module init/exit. It integrates by being loaded manually or by kselftest infrastructure.

## Risks And Test Signals

The test is CPU and allocator intensive and does not check allocation failure before `virt_to_page()`, so it assumes the order-3 allocations succeed in the test environment. Signals are kernel logs for the three phases and external memory-leak/page-ref debug tooling.
