<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page_idle.h -->
# sources/distributed-fs/ceph-client/include/linux/page_idle.h

## Purpose
This header provides folio young/idle flag operations for configurations where page idle bits do not fit in `page->flags` and are stored in page extensions.

## Important APIs, types, and functions
Under `CONFIG_PAGE_IDLE_FLAG && !CONFIG_64BIT`, it defines `folio_test_young()`, `folio_set_young()`, `folio_test_clear_young()`, `folio_test_idle()`, `folio_set_idle()`, and `folio_clear_idle()` using `PAGE_EXT_YOUNG` and `PAGE_EXT_IDLE`.

## Control flow
Each helper obtains the folio's `page_ext`, tests/sets/clears the relevant bit, and puts the extension. Missing page_ext returns false or no-op. On 64-bit or disabled page-idle configs, these helpers are supplied by `page-flags.h` or become false/no-op there.

## State and persistence
Young/idle state persists in page_ext flags for affected 32-bit configurations. No separate header state exists.

## Dependencies and integration points
It depends on bitops, page flags, page_ext, page idle tracking, memory reclaim/idle page tracking, and architectures with limited page flag bits.

## Risks and test signals
Risks include page_ext absence causing lost idle/young state, missing puts, races with reclaim/page-idle scanners, and config-specific API differences. Test 32-bit `CONFIG_PAGE_IDLE_FLAG`, idle page tracking sysfs/proc interfaces, reclaim young clearing, page_ext allocation, and 64-bit compile paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page_idle.h -->
