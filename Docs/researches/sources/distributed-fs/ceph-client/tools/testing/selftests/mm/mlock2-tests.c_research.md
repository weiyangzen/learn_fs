# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mlock2-tests.c

## Purpose

`mlock2-tests.c` validates `mlock2()` and `mlockall()` lock-on-fault behavior using `/proc/self/maps` and `/proc/self/smaps` observations. It verifies immediate locking, on-fault locking, unlock cleanup, and VMA split/merge behavior.

## Important APIs, Types, and Functions

The file uses `mlock2_()`, `mlockall()`, `munlock()`, `munlockall()`, `mmap()`, `/proc/self/maps`, and `/proc/self/smaps`. Helpers include `get_vm_area()`, `is_vmflag_set()`, `get_value_for_name()`, `is_vma_lock_on_fault()`, `lock_check()`, `unlock_lock_check()`, `onfault_check()`, `unlock_onfault_check()`, and `test_vma_management()`.

## Control Flow

`main()` first probes `mlock2(MLOCK_ONFAULT)` on a three-page mapping and exits finished if the syscall is unavailable. It then runs 13 planned checks. Immediate lock mode should set the `lo` VmFlag and make RSS equal VMA size. On-fault mode should mark the VMA locked while only faulting one page. `munlockall()` cases clear both immediate and on-fault locks. VMA management locks three pages, unlocks the middle page to force VMA splitting, then unlocks the full range to verify merging.

## State and Persistence Behavior

The tests alter process memory-lock state and VMA attributes, then clean them with `munlock()`, `munlockall()`, and `munmap()`. Observed state is read from procfs. No persistent files are written.

## Dependencies and Integration Points

It depends on the local `mlock2.h` wrapper and procfs smaps parsing. It integrates with mm VMA flag handling, RSS accounting, and VMA split/merge behavior for locked ranges.

## Risks and Edge Cases

The plan count is 13 even though some helper tests emit multiple results; this matches the existing code but makes result counting sensitive to helper behavior. Procfs text parsing assumes stable labels such as `VmFlags:`, `Size:`, and `Rss:`. The header wrapper's errno handling is nonstandard.

## Test Signals

Success is indicated by `lo` VmFlag presence/absence, RSS equal or less than VMA size as appropriate, and expected maps boundaries after split and merge operations.
