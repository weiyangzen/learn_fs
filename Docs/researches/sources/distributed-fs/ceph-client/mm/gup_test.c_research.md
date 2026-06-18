# sources/distributed-fs/ceph-client/mm/gup_test.c

## Purpose

`gup_test.c` provides a debugfs-backed test and benchmark interface for the GUP and PUP APIs implemented in `gup.c`. When `CONFIG_GUP_TEST` is enabled, late init creates `/sys/kernel/debug/gup_test` with ioctl commands defined in `gup_test.h`. User-space selftests and benchmark tools use this node to pin or get user pages in controlled batches, measure acquisition and release time, dump selected pages, and keep a long-term pin live across ioctl calls for COW and migration tests.

## Important APIs, Types, and Functions

The file registers `gup_test_fops` with `nonseekable_open`, `gup_test_ioctl`, `compat_ptr_ioctl`, and `gup_test_release`. The main dispatcher, `gup_test_ioctl()`, accepts benchmark/test commands (`GUP_FAST_BENCHMARK`, `PIN_FAST_BENCHMARK`, `PIN_LONGTERM_BENCHMARK`, `GUP_BASIC_TEST`, `PIN_BASIC_TEST`, `DUMP_USER_PAGES_TEST`) and long-term fixture commands (`PIN_LONGTERM_TEST_START`, `PIN_LONGTERM_TEST_STOP`, `PIN_LONGTERM_TEST_READ`).

`__gup_test_ioctl()` copies a `struct gup_test` from userspace, allocates a `struct page **` array, optionally takes `current->mm->mmap_lock`, loops over the requested address range in `nr_pages_per_call` chunks, invokes the requested GUP API, records elapsed microseconds for get/pin and release phases, optionally verifies DMA-pinned state, optionally dumps selected pages, and releases pages with either `put_page()` or `unpin_user_pages()`.

`put_back_pages()` mirrors the acquisition mode: ordinary GUP commands call `put_page()`, pin commands call `unpin_user_pages()`, and dump mode chooses according to `GUP_TEST_FLAG_DUMP_PAGES_USE_PIN`. `verify_dma_pinned()` checks `folio_maybe_dma_pinned()` for pin commands and `folio_is_longterm_pinnable()` for long-term pin benchmarks, warning and dumping a page on mismatch.

The stateful long-term fixture uses `pin_longterm_test_mutex`, `pin_longterm_test_pages`, and `pin_longterm_test_nr_pages`. `pin_longterm_test_start()` copies a `struct pin_longterm_test`, validates page alignment and flags, allocates an array, then calls `pin_user_pages()` or `pin_user_pages_fast()` with `FOLL_LONGTERM` and optional `FOLL_WRITE` until the full range is pinned or a failure occurs. `pin_longterm_test_read()` maps each pinned page with `kmap_local_page()`, copies one page at a time to a user-provided destination, and unmaps with `kunmap_local()`. `pin_longterm_test_stop()` unpins and frees the stored array, and `gup_test_release()` stops the fixture when the debugfs file is closed.

## Control Flow

The benchmark path is single-ioctl and mostly stateless. `gup_test_ioctl()` copies the input structure, `__gup_test_ioctl()` allocates storage, acquires `mmap_lock` for non-fast commands, walks the address interval, and stops early when a call returns fewer pages than requested or an error. It then updates the user-visible `get_delta_usec`, `put_delta_usec`, and adjusted `size` fields before copying the structure back to userspace. The actual return code remains `0` unless there was an ioctl, copy, allocation, or locking error; partial page acquisition is communicated through the adjusted structure.

The long-term fixture path is multi-ioctl. `PIN_LONGTERM_TEST_START` owns the global page array until `PIN_LONGTERM_TEST_STOP`, file release, or a failed start cleanup. The mutex serializes start/read/stop and prevents concurrent fixtures. `PIN_LONGTERM_TEST_READ` does not expose kernel addresses; it copies page contents through temporary local mappings.

## State and Persistence Behavior

Most benchmark state is transient and freed before ioctl return. The long-term fixture intentionally persists pinned pages in static globals, holding DMA pins across ioctl calls so user-space tests can modify mappings, fork, or otherwise observe COW behavior while the kernel retains pins. The state is process-independent at the file implementation level because the globals are file-static, so only one long-term fixture can exist system-wide for this debugfs node.

The file mutates user-provided `struct gup_test` fields before copying back, emits kernel warnings and `dump_page()` diagnostics, and can keep pages pinned until stop or release. It relies on `gup.c` for all actual pin semantics and on `highmem.c` `kmap_local_page()` support when reading pinned pages.

## Dependencies and Integration Points

Dependencies include `linux/debugfs.h`, `linux/highmem.h`, `linux/uaccess.h`, `linux/ktime.h`, and `gup_test.h`. The command numbers and ABI structures are shared with in-tree selftests such as `tools/testing/selftests/mm/gup_test.c` and COW tests that include `mm/gup_test.h`. The debugfs creation is conditional on `CONFIG_GUP_TEST` via `mm/Makefile` and `mm/Kconfig`.

## Risks and Edge Cases

The test interface is privileged by debugfs mode `0600`, but it still pins arbitrary current-process user memory and can consume memory proportional to `size / PAGE_SIZE`. `nr_pages_per_call` must be sensible; a zero value would make progress impossible in the loop, so user-space tests must provide a nonzero batch size. The long-term fixture returns `-EINVAL` if already active, but because state is global, concurrent unrelated test processes can interfere. `pin_longterm_test_start()` advances the local `pages` pointer while preserving the original in `pin_longterm_test_pages`; cleanup must always use the global original pointer, which it does.

`pin_longterm_test_read()` copies full pages to a user address without independently validating the destination range up front; it relies on `copy_to_user()` failure handling. Benchmark commands that acquire zero pages still perform release timing over zero pages and report the shortened `size`.

## Test Signals

This file is itself a test hook. Strong signals are successful open/ioctl cycles on `/sys/kernel/debug/gup_test`, passing selftests under `tools/testing/selftests/mm`, absence of `verify_dma_pinned()` warnings, expected page dumps for `DUMP_USER_PAGES_TEST`, and correct cleanup on file release. Long-term tests should verify both slow and fast pin modes, optional write pins, COW behavior after fork, readback through `PIN_LONGTERM_TEST_READ`, and cleanup through both explicit stop and close.
