# sources/distributed-fs/ceph-client/include/linux/mmap_lock.h

## Purpose
`mmap_lock.h` defines the public locking API for `mm_struct::mmap_lock` and optional per-VMA locking. It wraps rwsem operations with tracing, assertions, seqcount updates, RCU-oriented VMA read locking, and cleanup guards.

## Important APIs, Types, And Functions
The file provides `MMAP_LOCK_INITIALIZER()`, mmap lock tracepoints, `mmap_assert_locked()`, `mmap_assert_write_locked()`, `mm_lock_seqcount_*()`, `mmap_lock_speculate_try_begin()`, `mmap_lock_speculate_retry()`, `vma_lock_init()`, `vma_start_read_locked_nested()`, `vma_start_read_locked()`, `vma_end_read()`, `vma_start_write()`, `vma_start_write_killable()`, VMA lock assertions, VMA attach/detach helpers, `lock_vma_under_rcu()`, `lock_next_vma()`, and the standard `mmap_write_*()`/`mmap_read_*()` APIs including `DEFINE_GUARD(mmap_read_lock, ...)`.

## Control Flow And State
All mmap lock acquisitions trace start/acquire/release when tracing is enabled. Write acquisition takes the rwsem and begins the per-mm seqcount; write unlock or downgrade ends all per-VMA write locks by ending the seqcount before releasing or downgrading the rwsem. With `CONFIG_PER_VMA_LOCK`, VMA read locks increment `vm_refcnt`, lockdep marks a shared lock, and `vma_refcount_put()` wakes waiters when the final reader blocking an exclusive writer leaves. VMA write locking compares `vma->vm_lock_seq` with `mm->mm_lock_seq` and can sleep while excluding readers. Without per-VMA locks, helpers collapse to mmap-lock assertions or no-ops.

## Dependencies And Integration Points
Dependencies include lockdep, `mm_types.h`, `mmdebug.h`, rwsems, tracepoint definitions, cleanup guards, and scheduler MM helpers. Integration points include page-fault fast paths, RCU VMA lookup, mmap/munmap/mprotect writers, lockdep, tracepoints, per-VMA lock sequence state in `mm_struct`/`vm_area_struct`, and the maple-tree VMA iterator.

## Risks And Test Signals
Risks include unmatched seqcount begin/end, retaining per-VMA write locks after releasing mmap write lock, unsafe detached VMA access, refcount overflow or missed wakeups, false assumptions when lockdep is disabled, and nonblock paths accidentally sleeping. Test signals include lockdep runs, mmap/fault/munmap/mremap stress with per-VMA locking enabled and disabled, RCU VMA lookup races, signal-interrupted write locking, tracepoint coverage, and KCSAN/rwsem contention tests.
