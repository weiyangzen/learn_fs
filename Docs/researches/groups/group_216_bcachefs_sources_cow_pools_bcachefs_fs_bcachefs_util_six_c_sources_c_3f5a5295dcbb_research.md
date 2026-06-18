# Group Research: group_216_bcachefs_sources_cow_pools_bcachefs_fs_bcachefs_util_six_c_sources_c_3f5a5295dcbb

Scope: `Docs/research_subset_a.md` only. All 20 listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/six.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/six.c

## Summary
Implements bcachefs “six” locks: sleepable shared/intent/exclusive locks with optional percpu reader accounting, sequence numbers, reentrancy counters, lockdep integration, wait-list exposure for deadlock cycle detection, and optional optimistic spinning.

## Main Responsibilities
- Provides trylock, blocking lock, relock, unlock, conversion, downgrade, reentrant increment, reader-count adjustment, count reporting, wakeup, init, and teardown operations.
- Encodes read/intent/write ownership and waiter bits in `lock->state`.
- Supports percpu read mode to reduce reader-side atomic contention.
- Maintains an RCU-swappable stable-index waiter array so lockless cycle detectors can traverse waiters without entries moving.
- Wakes read waiters in batches and intent/write waiters by oldest transaction start time.
- Integrates with lockdep/lockstat and saves owner backtraces under debug builds.

## Key APIs
- `six_trylock_ip()`, `six_lock_ip_waiter()`, `six_relock_ip()`, `six_unlock_ip()`.
- `six_lock_downgrade()`, `six_lock_tryupgrade()`, `six_trylock_convert()`.
- `six_lock_increment()`, `six_lock_readers_add()`.
- `six_lock_wakeup_all()`, `six_lock_counts()`.
- `__six_lock_init()`, `six_lock_exit()`.

## Important Behavior
Read locks conflict with write locks, intent locks conflict with other intent locks, and write locks require the current task to already own intent. Write unlock increments the lock sequence so callers can drop and later relock only if protected state did not change.

The slow path installs a `six_lock_waiter` before sleeping, then runs an optional `should_sleep_fn` callback. This lets bcachefs’ upper layers detect lock dependency cycles and abort/restart transactions.

Percpu read mode temporarily increments the current CPU reader slot and uses barriers to race safely with write acquisition. Failed percpu trylocks may return a negative wakeup code so conflicting waiters are not stranded.

## Risks
Correctness depends on tight memory ordering between wait-slot removal, `lock_acquired`, percpu reader counts, and state bits. Waiter objects live on blocked task stacks, so wakeup and abort paths must not dereference them after publishing acquisition or removal. Reentrant counters are only partial support; upper layers must track ownership correctly.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/six.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/six.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/six.h

## Summary
Declares the six-lock interface, data structures, waiter representation, and initialization helpers for bcachefs shared/intent/exclusive locking.

## Main Contents
- `enum six_lock_type` with `SIX_LOCK_read`, `SIX_LOCK_intent`, and `SIX_LOCK_write`.
- `struct six_lock_waiter`, used both for sleeping and upper-layer cycle detection.
- `struct six_lock_wait_slot` and `struct six_lock_wait_fifo`, an RCU-replaceable stable-index wait array.
- `struct six_lock`, containing state, sequence number, reentrancy counters, owner, optional percpu readers, wait lock, wait FIFO, inline waiter storage, and optional lockdep map.
- `SIX_LOCK_INIT_PCPU` initialization flag.
- Inline wrappers for trylock, relock, and unlock variants.

## Important Behavior
The header documents six-lock semantics: intent is exclusive against intent but compatible with readers, and write is taken under intent. Sequence numbers let callers drop read/intent locks for blocking work and later relock if no writer intervened.

The waiter interface is intentionally exposed so a caller can embed `six_lock_waiter` in its own transaction/held-lock structures and walk wait lists for deadlock avoidance.

## Risks
The lock itself does not know which task owns read locks. Any reentrancy or self-deadlock avoidance involving read locks must be implemented by the upper layer. Lock waiters are externally visible, so users must preserve waiter lifetime until acquisition or abort completes.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/six.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/thread_with_file.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/thread_with_file.c

## Summary
Implements helpers for launching a kthread and exposing it through an anonymous inode file descriptor, plus a higher-level stdio-style bidirectional pipe interface.

## Main Responsibilities
- Creates a kthread and anonymous inode fd with read/write mode derived from supplied file operations.
- Stops and releases the task when the fd is released.
- Provides `thread_with_stdio` read, write, poll, flush, release, and ioctl file operations.
- Buffers input and output through dynamically allocated `darray_char` buffers guarded by spinlocks and waitqueues.
- Supports line-oriented input reads, timeout reads, printf-style output, blocking/nonblocking behavior, and stdout-only mode.

## Key APIs
- `bch2_run_thread_with_file()`, `bch2_thread_with_file_exit()`.
- `bch2_thread_with_stdio_init()`, `__bch2_run_thread_with_stdio()`.
- `bch2_run_thread_with_stdio()`, `bch2_run_thread_with_stdout()`.
- `bch2_stdio_redirect_read()`, `bch2_stdio_redirect_readline_timeout()`, `bch2_stdio_redirect_readline()`.
- `bch2_stdio_redirect_write()`, `bch2_stdio_redirect_vprintf()`, `bch2_stdio_redirect_printf()`.

## Important Behavior
Closing the file marks the thread/stdout state done, wakes readers and writers, stops the kthread, frees buffers, and calls the operation-specific exit hook. Flush returns the kthread function’s saved return value.

Input buffering tries to cap ordinary buffered data around 4096 bytes, but it can grow to preserve line/message semantics. Output writes are all-or-error for a single message; nonblocking mode returns `-EAGAIN` instead of partially appending.

## Risks
The code mixes user-copy fault probing, nofault copies, spinlocks, waitqueues, and kthread lifetime. Callers of the lower-level API must provide a release method that invokes `bch2_thread_with_file_exit()`. Stdio consumers must handle `-EPIPE`, `-EAGAIN`, `-ETIME`, and `-1` EOF-style returns consistently.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/thread_with_file.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/thread_with_file.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/thread_with_file.h

## Summary
Declares the fd-backed kthread and stdio-redirection interfaces.

## Main Contents
- `struct thread_with_file` with task pointer, return code, and done flag.
- `struct thread_with_stdio_ops` with `exit`, thread `fn`, and optional `unlocked_ioctl`.
- `struct thread_with_stdio`, embedding `thread_with_file`, `stdio_redirect`, and ops pointer.
- Public APIs for running file-backed threads, stdio-backed threads, stdout-only threads, and stdio read/write/printf helpers.

## Important Behavior
The comments define two tiers: low-level custom `file_operations`, where the caller owns release cleanup, and high-level stdio redirection with implemented polling and pipe-like shutdown semantics.

## Risks
The header’s API contract is lifetime-sensitive: lower-level users must stop the kthread on fd release, while higher-level users must initialize buffers and provide an exit hook suitable for release-time cleanup.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/thread_with_file.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/thread_with_file_types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/thread_with_file_types.h

## Summary
Defines the buffer types shared by the thread-with-stdio implementation.

## Main Contents
- `struct stdio_buf`: spinlock, waitqueue, `darray_char` buffer, and `waiting_for_line` flag.
- `struct stdio_redirect`: input buffer, output buffer, and done flag.

## Risks
These structures are directly shared between kthread-side helpers and fd file operations, so callers must rely on the implementation’s locking and wakeup protocol rather than manipulating buffers directly.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/thread_with_file_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/time_stats.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/time_stats.c

## Summary
Implements bcachefs event-duration and inter-arrival statistics collection with optional quantile tracking, optional percpu buffering, and text/JSON reporting.

## Main Responsibilities
- Chooses readable time units from nanosecond values.
- Updates duration and frequency mean/variance, weighted mean/variance, min/max, and totals.
- Maintains approximate quantile entries when enabled.
- Switches high-frequency stats to percpu buffers unless disabled.
- Flushes percpu buffers before reporting or reset.
- Emits aligned human-readable text through `seq_buf`.
- Emits structured JSON summaries.

## Key APIs
- `bch2_pick_time_units()`.
- `__bch2_time_stats_update()`, `__bch2_time_stats_clear_buffer()`.
- `bch2_time_stats_reset()`.
- `bch2_time_stats_to_seq_buf()`, `bch2_time_stats_to_json()`.
- `bch2_time_stats_init()`, `bch2_time_stats_init_no_pcpu()`, `bch2_time_stats_exit()`.

## Important Behavior
Stats are updated directly under a spinlock until the source is frequent enough, then `alloc_percpu_gfp()` is attempted and each CPU buffers up to 31 start/end pairs. Reporting drains all CPU buffers under the main spinlock.

Quantiles use an Eytzinger-order array and adaptive step values. Text output can be suppressed for zero-count stats with `TIME_STATS_PRINT_NO_ZEROES`.

## Risks
Readers/reporters mutate state by draining percpu buffers, so reporting is not a purely const operation. The percpu pointer uses sentinel values, making checks against `TIME_STATS_NONPCPU` important. Quantiles are approximate and marked “do not use” for new code in the header.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/time_stats.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/time_stats.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/time_stats.h

## Summary
Declares bcachefs time-statistics structures, update helpers, printing APIs, and optional quantile support.

## Main Contents
- `struct time_unit`.
- `struct quantiles` with 15 quantile entries.
- `struct time_stat_buffer` with 31 buffered event pairs.
- `struct bch2_time_stats`, storing min/max/total duration, min/max frequency, last event times, lifetime start, mean/variance, weighted mean/variance, lock, buffer pointer, and quantile flag.
- `struct bch2_time_stats_quantiles`.
- Inline helpers `bch2_time_stats_update()` and `track_event_change()`.

## Important Behavior
`track_event_change()` records the duration of true/false state intervals by remembering `last_event_start` and updating stats when the state changes back.

Initialization sets min fields to `U64_MAX` and captures `local_clock()` as the stats epoch. `bch2_time_stats_init_no_pcpu()` disables automatic percpu buffering.

## Risks
The stats object is not passive: callers that inspect or reset it must respect the lock and percpu-buffer lifecycle. `last_event_start` doubles as state storage in `track_event_change()`, so direct manipulation can break interval tracking.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/time_stats.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/two_state_shared_lock.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/two_state_shared_lock.c

## Summary
Provides the blocking slow path for the two-state shared lock.

## Main Responsibilities
- Implements `__bch2_two_state_lock()`.
- Waits until `bch2_two_state_trylock()` succeeds for the requested state.

## Important Behavior
The wait uses the lock’s waitqueue and retries the inline atomic trylock predicate.

## Risks
All substantive state handling lives in the header. Wakeup correctness depends on unlock waking all waiters when the aggregate counter returns to zero.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/two_state_shared_lock.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/two_state_shared_lock.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/two_state_shared_lock.h

## Summary
Defines a compact lock with two shared states where holders in the same state can coexist, but opposite states conflict.

## Main Contents
- `two_state_lock_t` with signed atomic counter and waitqueue.
- `two_state_lock_init()`.
- `bch2_two_state_trylock()`.
- `bch2_two_state_lock()`.
- `bch2_two_state_unlock()`.

## Important Behavior
State `s` maps to `+1` or `-1`. A positive counter means one or more holders of one state; a negative counter means holders of the other state. Trylock fails if the current sign conflicts with the requested state. Unlock subtracts the state’s sign and wakes all waiters when the counter reaches zero.

## Risks
The lock does not track owners, recursion, or fairness. Mispaired unlock state values corrupt the signed counter and can admit incompatible holders.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/two_state_shared_lock.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/util.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/util.c

## Summary
Implements broad bcachefs utility routines for parsing, printing, time-stat formatting, rate control, bio mapping, random values, bio copying, debugging, percpu accumulation, device-list splitting, mempool allocation, and wait-bit timeout behavior.

## Main Responsibilities
- Parses human-readable integer strings with binary/decimal unit suffixes.
- Parses comma/semicolon flag lists.
- Prints binary integers, multiline strings, stack traces, datetimes, time units, and time stats.
- Implements ratelimit delay/increment and a proportional-derivative controller.
- Maps kernel/vmalloc buffers into bios and builds chained bios over large buffers.
- Allocates bio pages, submits buffer bios synchronously, and copies to/from bios.
- Emits textual bio diagnostics.
- Accumulates percpu u64 arrays and zeroes source CPU copies.
- Splits colon-separated device strings into allocated string arrays.
- Provides `mempool_kvmalloc` shims and an IO-accounted wait-bit timeout helper.

## Key APIs
- `bch2_strtoint_h()`, `bch2_strtouint_h()`, `bch2_strtoll_h()`, `bch2_strtoull_h()`, `bch2_strtou64_h()`.
- `bch2_read_flag_list()`, `bch2_is_zero()`.
- `bch2_save_backtrace()`, `bch2_prt_backtrace()`, `bch2_prt_task_backtrace()`.
- `bch2_time_stats_to_text()`, `bch2_time_stats_json_to_text()`.
- `bch2_ratelimit_delay()`, `bch2_ratelimit_increment()`.
- `bch2_pd_controller_update()`, `bch2_pd_controller_init()`, `bch2_pd_controller_debug_to_text()`.
- `bch2_bio_map()`, `bch2_bio_map_and_chain()`, `bch2_bio_submit_buf_wait()`, `bch2_bio_alloc_pages()`.
- `bch2_get_random_u64_below()`, `memcpy_to_bio()`, `memcpy_from_bio()`, `bch2_bio_to_text()`.
- `bch2_acc_percpu_u64s()`, `bch2_split_devs()`, `bch2_bit_wait_io_timeout()`.

## Important Behavior
Human-readable parsing supports decimal fractions and suffixes such as SI one-letter units, `KiB`-style binary units, and `kB`-style decimal units with overflow checking.

`bch2_bio_map_and_chain()` returns the tail bio while submitting earlier chained bios in sector order, preserving forward submission and applying `REQ_PREFLUSH` only to the first bio.

The PD controller adjusts a rate based on proportional and derivative error terms and can suppress rate increases under backpressure when work is already delayed.

## Risks
This file contains low-level helpers used across storage and VFS paths. Incorrect bio chaining, page allocation sizing, or buffer lifetime assumptions can lead to I/O completion surprises. Several helpers assume caller-side locking, especially percpu accumulation and bio/page operations.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/util.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/util.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/util.h

## Summary
Declares and defines bcachefs’ general utility interface, including compatibility shims, print helpers, parsing helpers, rate-control structures, bio helpers, kthread wait macros, memory movement helpers, array helpers, percpu helpers, bit helpers, error-propagation macros, memalloc guard classes, mempool shims, wait-bit timeout helpers, and percpu initialization support.

## Main Contents
- Debug macro `EBUG_ON()`.
- Endianness and type-detection macros.
- Kernel-version compatibility helpers such as `bio_inline_vecs()` and `bdev_rot()`.
- `bch2_kvmalloc()` wrapper.
- Printbuf aliases and UUID/date/time print helpers.
- Human-readable integer parsing declarations.
- Stacktrace darray type and backtrace APIs.
- `struct bch_ratelimit` and `struct bch_pd_controller`.
- Sysfs helper macros for PD controller fields.
- Bio mapping/submission/copy/debug APIs.
- `kthread_wait()` and `kthread_wait_freezable()`.
- u64-specialized memcpy/memmove helpers.
- array insertion/removal and gap-buffer helpers.
- percpu sum/set/accumulate helpers.
- little-endian bit helpers.
- flag mapping macros.
- `try()` and `errptr_try()`.
- scoped `memalloc_flags` guard.
- `wait_on_bit_io_timeout()`.
- `bch2_alloc_percpu_init()`.

## Important Behavior
Many functions are inline for hot paths, including memory movement and percpu helpers. On x86-64, u64 copy/move helpers use `rep movsq` assembly when KMSAN is not enabled. `try()` returns immediately on nonzero errors, creating a compact error-propagation idiom used throughout bcachefs.

## Risks
This header is a wide dependency surface. Macro helpers can evaluate arguments in non-obvious contexts, and some helpers assume alignment, non-overlap direction, or external synchronization. Version shims and userspace/kernel conditional paths must be kept synchronized with supported build targets.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/util.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/varint.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/varint.c

## Summary
Implements bcachefs unsigned 64-bit variable-length integer encoding and decoding, including fast variants for callers that can overread/overwrite within safe padding.

## Main Responsibilities
- Encodes `u64` values into 1 to 9 bytes.
- Decodes varints with bounds checking.
- Provides fast encode/decode paths using unaligned 64-bit stores/loads.

## Key APIs
- `bch2_varint_encode()`.
- `bch2_varint_decode()`.
- `bch2_varint_encode_fast()`.
- `bch2_varint_decode_fast()`.

## Important Behavior
For 1 to 8 byte encodings, low marker bits encode the byte length and the value is shifted left by the byte count. A 9-byte encoding starts with `0xff` followed by the raw little-endian 64-bit value.

The checked decoder returns `-BCH_ERR_varint_decode_error` if the encoded length would pass `end`. The fast decoder may read up to 8 bytes from `in`, but still reports an error if the varint logically extends past `end`.

## Risks
Fast variants require caller-provided padding/safety for wide memory access. The decode comment says “encode” but behavior is decode. Consumers must handle the bcachefs-specific negative error code rather than generic `-1`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/varint.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/varint.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/varint.h

## Summary
Declares bcachefs varint encode/decode APIs.

## Main Contents
- Checked encode/decode declarations.
- Fast encode/decode declarations.

## Risks
The header does not document the fast-path padding requirements; callers must know them from `varint.c`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/varint.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/vstructs.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/vstructs.h

## Summary
Defines macros for working with variable-sized bcachefs structures whose payload length is expressed as a count of u64 words.

## Main Contents
- `vstruct_u64s()`, `vstruct_bytes()`, `vstruct_blocks()`, `vstruct_blocks_plus()`, `vstruct_sectors()`.
- `vstruct_next()`, `vstruct_last()`, `vstruct_end()`.
- `vstruct_for_each()` and `vstruct_for_each_safe()`.
- `vstruct_idx()`.

## Important Behavior
The macros assume structures have an `_data` payload and often a `start` flexible element. Length fields may be `u64`, `u32`, `u16`, or `u8` and are converted as little-endian values.

## Risks
The file notes that `type_is` cannot distinguish `__le64` from `u64`, so u64 length fields are assumed little-endian. These macros are type/layout-sensitive and can silently produce bad pointer arithmetic if used on structures without the expected `_data` and `start` conventions.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/vstructs.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/vfs/buffered.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/vfs/buffered.c

## Summary
Implements bcachefs buffered VFS I/O: readahead, single-folio reads, writeback, write_begin/write_end, multi-folio buffered writes, and the buffered branch of `write_iter`.

## Main Responsibilities
- Converts readahead folios into read bios and submits extent reads.
- Extends read bios across adjacent folios and can opportunistically allocate more folios for expensive partial reads.
- Reads a single folio synchronously for pagecache misses and partial-write preparation.
- Builds writeback bios from dirty folio-sector state and submits bcachefs write operations.
- Handles writeback throttling on allocator and journal pressure.
- Manages folio disk reservations for buffered writes.
- Handles EOF-straddling folios, post-EOF zeroing, short writes, pagecache cleanup, dirtying, and inode size updates.
- Routes `bch2_write_iter()` between direct and buffered paths.

## Key APIs
- `bch2_readahead()`.
- `bch2_read_single_folio()`, `bch2_read_folio()`.
- `bch2_writepages()`.
- `bch2_write_begin()`, `bch2_write_end()`.
- `bch2_write_iter()`.

## Important Behavior
`bchfs_read()` walks the extents btree for an inode/subvolume snapshot, resolves indirect/reflink extents, sets page state from the extent, and calls the lower read path. It temporarily narrows the bio size to an extent fragment and either submits the last fragment directly or clones for earlier fragments.

Writeback snapshots each folio’s sector reservations under the folio-state spinlock before unlocking the folio. It updates per-sector states to allocated, clears reservations, starts writeback, and batches contiguous dirty sectors into `bch_writepage_io`.

Buffered writes lock contiguous folios, read boundary folios when required, reserve sectors, copy from the user iterator atomically, mark successful ranges uptodate/dirty, and update `i_size`.

## Risks
This path is tightly coupled to folio-private state, btree transaction locking, extent semantics, disk reservations, and writeback lifetime. The read path explicitly warns that transaction restarts after `bch2_read_extent()` would be dangerous because the rbio iterator may already have been handed off. Partial writes and reservation failures must preserve pagecache and iterator consistency.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/vfs/buffered.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/vfs/buffered.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/vfs/buffered.h

## Summary
Declares the buffered I/O interface and writepage I/O container.

## Main Contents
- `struct bch_writepage_io`, containing the target inode and trailing `struct bch_write_op`.
- Declarations for folio read, readahead, writepages, write_begin/write_end, and write_iter.
- Kernel-version-dependent `write_begin`/`write_end` signatures.

## Risks
`struct bch_writepage_io` relies on `bch_write_op` being last because bios are allocated from a bioset and recovered with `container_of()`. Signature guards must match the kernel version being built.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/vfs/buffered.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/vfs/direct.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/vfs/direct.c

## Summary
Implements bcachefs direct I/O read and write paths plus the VFS `read_iter` dispatcher.

## Main Responsibilities
- Performs aligned O_DIRECT reads into user-backed iterator pages.
- Supports sync and async direct-read completion through closures.
- Flushes overlapping pagecache before direct reads.
- Performs aligned O_DIRECT writes with pagecache invalidation/blocking.
- Handles async direct-write continuation after each write operation.
- Reserves quota and disk space, checks whether existing allocated extents can satisfy writes, and accounts inode sectors.
- Handles extending writes, dsync flushes, and inode direct-I/O lifetime.
- Detects and handles page faults that dropped pagecache locks via FDM tracking.

## Key APIs
- `bch2_direct_IO_read()`.
- `bch2_read_iter()`.
- `bch2_direct_write()`.

## Important Behavior
Direct reads require sector alignment, trim reads to EOF, shorten the iterator to a block-aligned size for the lower read path, and dirty user pages unless the iterator is kernel/internal backed.

Direct writes require filesystem block alignment. Extending writes remain inode-locked and force sync behavior so `i_size` is updated safely. Non-extending writes can drop the inode lock after setting up direct-I/O and pagecache blocking.

The write loop fills bios from the iterator, invalidates pagecache again if a page fault dropped locks, trims unaligned tail bytes, initializes a `bch_write_op`, reserves quota/disk space, submits the write, and either continues asynchronously or loops synchronously.

## Risks
Direct I/O interlocks with page faults, mmap/pagecache invalidation, quotas, disk reservations, journal flushing, and async callback lifetime. Async writes may need to copy iovecs because caller stack storage can disappear after returning `-EIOCBQUEUED`. The FDM dropped-lock path is subtle and must re-invalidate before using newly pinned pages.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/vfs/direct.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/vfs/direct.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/vfs/direct.h

## Summary
Declares bcachefs direct I/O state structures and public direct read/write APIs.

## Main Contents
- `struct dio_read`: closure, request pointer, return value, dirty-page flag, and embedded `bch_read_bio`.
- `struct dio_write`: request, mapping, inode, mm, optional copied iovec storage, state flags, quota reservation, written sector count, iterator, inline iovecs, and trailing `bch_write_op`.
- Declarations for direct read, direct write, and `read_iter`.

## Risks
Both structures rely on embedded/trailing bio/write-op layout for `container_of()` recovery. Async write continuation depends on `mm` and copied iovec lifetime being valid until completion.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/vfs/direct.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/vfs/fdm.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/vfs/fdm.h

## Summary
Defines the faults-disabled-mapping table used by bcachefs direct I/O to replace removed per-task kernel fault tracking.

## Main Contents
- `struct fdm_slot` with task pointer and mapping pointer plus a low-bit dropped-locks flag.
- `struct fdm_hash` with three random hash seeds, a closure waitlist, and 512 slots.
- Helpers `fdm_get()`, `fdm_dropped_locks()`, `fdm_set_dropped_locks()`, `fdm_set()`, `fdm_clear()`, and `fdm_init()`.

## Important Behavior
Each task can install one current mapping. Lookup checks exactly three task-hashed slots. Insertion waits on a closure waitlist if all candidate slots are occupied, writes mapping first, uses a write barrier, then publishes task as the valid marker. Clearing removes the task marker, barriers, and wakes waiters.

The low bit of the mapping word records that a fault handler dropped and retook locks; direct I/O can then invalidate pagecache again and retry safely.

## Risks
The table is intentionally lockless and assumes each task writes only its own entry. Correctness relies on address-space pointer alignment for low-bit stealing, memory barriers around the task valid marker, and low occupancy of the fixed-size hash. `fdm_set()` retries recursively after a lost race.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/vfs/fdm.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/vfs/fiemap.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/vfs/fiemap.c

## Summary
Implements bcachefs FIEMAP support by merging extent-btree mappings with dirty pagecache holes and reporting physical, inline, shared, encoded, unwritten, delalloc, and alignment flags.

## Main Responsibilities
- Converts bcachefs extent keys into FIEMAP records.
- Reports direct data pointers, inline data, reservations/delalloc, and skips error keys.
- Scans pagecache holes to synthesize delayed-allocation extents for dirty cached data.
- Handles reflink pointer resolution through `bch2_read_indirect_extent()`.
- Iterates the requested file range under btree transactions and emits extents in order.
- Marks the final emitted extent with `FIEMAP_EXTENT_LAST`.

## Key APIs
- `bch2_fiemap()`.

## Important Behavior
`bch2_fill_extent()` reports each decoded direct-data pointer. Reflink-value extents are marked shared. Compressed extents are marked encoded; uncompressed physical offsets include CRC offset. Unaligned physical offsets or sizes get `FIEMAP_EXTENT_NOT_ALIGNED`.

For holes in the extent btree, the code scans pagecache for data and fabricates an extent key with a dummy pointer and `FIEMAP_EXTENT_DELALLOC`. It first tries a nonblocking scan while holding btree locks, then drops locks for a blocking scan on `-EAGAIN`.

## Risks
The file documents a semantic compromise: pagecache should take precedence for COW dirty data, but without per-sector writeback tracking this can over-report delalloc for clean cached data. FIEMAP mappings are not stable because bcachefs background relocation can move data after reporting.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/vfs/fiemap.c -->