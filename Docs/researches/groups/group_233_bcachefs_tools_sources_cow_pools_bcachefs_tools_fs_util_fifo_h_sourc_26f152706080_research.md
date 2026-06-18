# Group Research: group_233_bcachefs_tools_sources_cow_pools_bcachefs_tools_fs_util_fifo_h_sourc_26f152706080

Scope verified against `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/fifo.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/fifo.h

Purpose: Header-only generic circular FIFO macros for typed queues with selectable index widths.

Key APIs and behavior:
- Defines `FIFO(type)`, `FIFO_U16_IDX`, `FIFO_U32_IDX`, `FIFO_U64_IDX`, and declaration helpers.
- `init_fifo()` allocates a power-of-two backing buffer with `kvmalloc`; `free_fifo()` releases it.
- Tracks absolute `front` and `back` counters and indexes storage with `idx & mask`.
- Supports push/pop at both ends, peek, pointer/index conversion, move, swap, grow, and forward/reverse iteration.

Integration:
- Depends on `util.h` for allocation, `roundup_pow_of_two`, `swap`, and `typecheck`.
- Used by higher-level utility code such as SIX-lock wait machinery.

Risks and invariants:
- `fifo_grow()` assumes old data can be duplicated into both halves to preserve absolute-index masking.
- Counters wrap according to the chosen index type, so small index variants require bounded occupancy/lifetime use.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/fifo.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/mean_and_variance.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/mean_and_variance.c

Purpose: Exported accessors for the streaming mean, median, and MAD estimator.

Key APIs and behavior:
- `mean_and_variance_get_mean()` returns exact `sum / n`, or zero with no samples.
- `mean_and_variance_get_mad()` returns current median absolute deviation estimate.
- `mean_and_variance_get_stddev()` reports Gaussian-equivalent spread as approximately `1.4826 * MAD`.
- `mean_and_variance_get_median()` returns the current median estimate.

Integration:
- Implements functions declared in `mean_and_variance.h`.
- Exports symbols with `EXPORT_SYMBOL_GPL`.
- Used by time statistics and related latency reporting.

Risks and invariants:
- The file intentionally preserves a "stddev" readout label while using robust MAD semantics.
- The scaled stddev approximation uses `(mad * 1518) >> 10`, so precision is approximate by design.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/mean_and_variance.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/mean_and_variance.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/mean_and_variance.h

Purpose: Defines a compact streaming estimator for exact mean plus stochastic-gradient median and MAD.

Key APIs and behavior:
- `struct mean_and_variance` stores `n`, `sum`, `median`, and `mad`.
- `sgm_median_mad_step()` updates median and MAD using sign-gradient steps.
- `mean_and_variance_update()` always tracks exact count/sum, and updates robust spread using either all-time or weighted mode.
- Weight `0` selects an approximate `1/n` Robbins-Monro schedule via `ilog2(n)`; nonzero weight selects exponential behavior.

Integration:
- Included by `time_stats.h`, `util.h`, and tests.
- Public getter declarations are implemented in `mean_and_variance.c`.

Risks and invariants:
- `abs(x - *median)` on signed values depends on inputs staying in a sane range.
- The estimator is robust and cheap, but callers must not expect exact variance.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/mean_and_variance.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/mean_and_variance_test.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/mean_and_variance_test.c

Purpose: KUnit tests for the streaming median/MAD estimator.

Key test coverage:
- Basic exact mean/count behavior and MAD decay after many constant samples.
- Weighted constant-stream convergence toward the constant value.
- Weighted step response moving monotonically toward a new value.
- Bounded response to a single large outlier.

Integration:
- Uses `kunit_test_suite()` with four test cases.
- Includes only `mean_and_variance.h`.

Risks and gaps:
- Tests assert convergence-shaped properties, not exact estimator values.
- No explicit overflow or extreme signed-value tests are present.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/mean_and_variance_test.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/printbuf.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/printbuf.c

Purpose: Implements growable best-effort string buffers for structured textual output.

Key APIs and behavior:
- `bch2_printbuf_make_room_gfp()` grows heap buffers with `krealloc` or `kvrealloc`; external buffers set overflow instead.
- `bch2_prt_printf()` and `bch2_prt_vprintf()` append formatted text and post-process indentation/tab controls.
- Newline, tab, right-justified tab, indent, and tabstop helpers maintain layout state.
- Human-readable unit printers, string-option printer, bitflag printers, and elastic tab alignment are implemented.

Integration:
- Implements `printbuf.h`; re-exported through aliases in `util.h`.
- Uses `darray` for elastic tab alignment column-width storage.
- Used broadly by diagnostics, sysfs/debug output, and error messages.

Risks and invariants:
- Allocation failures are sticky state, not direct hard errors for most printers.
- `bch2_printbuf_tabstop_align()` replaces heap storage and must preserve ownership flags correctly.
- Mixed raw `\n`, `\t`, and `\r` should go through printbuf helpers for correct indentation/alignment.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/printbuf.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/printbuf.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/printbuf.h

Purpose: Public interface and inline helpers for print buffers.

Key APIs and behavior:
- `struct printbuf` tracks buffer pointer, size, position, indentation, tabstops, allocation mode, and output flags.
- Provides `PRINTBUF` for heap-backed buffers and `PRINTBUF_EXTERN` for caller-owned buffers.
- Inline append helpers cover chars, repeated chars, bytes, strings, and hex bytes.
- State save/restore, reset, atomic allocation guards, and indent guards are provided.

Integration:
- Depends on Linux kernel string/hex helpers.
- Function implementations live in `printbuf.c`.
- The RAII-style `DEFINE_CLASS` and `DEFINE_GUARD` helpers support scoped cleanup/indent/atomic state.

Risks and invariants:
- `printbuf_remaining_size()` clamps invalid positions with `WARN_ON`.
- External buffers cannot grow and use overflow signaling.
- `prt_bytes()` calls `printbuf_nul_terminate()` after copying, which may allocate.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/printbuf.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/rcu_pending.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/rcu_pending.c

Purpose: Per-CPU batching layer for processing objects after RCU or SRCU grace periods.

Key APIs and behavior:
- Supports generic process callbacks plus special kvfree and call_rcu modes.
- Uses per-CPU `rcu_pending_pcpu` state with a darray of genradix-backed batches and fallback linked lists.
- Tracks grace-period poll cookies and moves expired objects into processing.
- Uses a single RCU callback per CPU to schedule worker processing, rearming while pending items remain.
- Provides dequeue APIs, including predicate-based claim/dequeue from current or all CPUs.

Integration:
- Implements `rcu_pending.h`.
- Wraps normal RCU and SRCU operations behind helper functions.
- Uses `darray`, `generic-radix-tree`, percpu allocation, workqueues, and `bch2_alloc_percpu_init`.

Risks and invariants:
- Locking is subtle: per-CPU spinlocks protect queues, but callbacks and work processing drop locks before invoking callbacks.
- kvfree mode encodes a low-bit flag in `rcu_head->func` for allocated heads.
- `rcu_pending_exit()` loops on barriers and work flushing until all pending/armed state drains.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/rcu_pending.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/rcu_pending.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/rcu_pending.h

Purpose: Public declarations for the RCU-pending batching facility.

Key APIs and behavior:
- `struct rcu_pending` stores per-CPU state, optional SRCU domain, and process callback.
- Declares enqueue, dequeue, dequeue-from-all, predicate dequeue, init, and exit functions.
- `rcu_pending_process_fn` receives the parent pending queue and object `rcu_head`.

Integration:
- Implemented by `rcu_pending.c`.
- Includes `<linux/rcupdate.h>` and forward-declares per-CPU internals.

Risks and invariants:
- Callers must initialize with `rcu_pending_init()` and drain with `rcu_pending_exit()`.
- Predicate callbacks run with internal queue lock held and must not sleep.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/rcu_pending.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/seqmutex.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/seqmutex.h

Purpose: Minimal mutex wrapper with a sequence counter for drop-and-relock validation.

Key APIs and behavior:
- `struct seqmutex` contains `struct mutex lock` and `u32 seq`.
- `seqmutex_lock()` takes the mutex and increments the sequence.
- `seqmutex_unlock()` releases and returns the sequence value.
- `seqmutex_relock()` only succeeds if the sequence is unchanged before and after `mutex_trylock()`.

Integration:
- Header-only helper, depends on `<linux/mutex.h>`.

Risks and invariants:
- `seqmutex_init()` initializes only the mutex, not explicitly the sequence; callers need zeroed storage or manual initialization.
- Sequence wrap is possible but likely acceptable for intended validation use.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/seqmutex.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/siphash.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/siphash.c

Purpose: BSD-licensed SipHash implementation with selectable compression/finalization rounds.

Key APIs and behavior:
- `SipHash_Init()` seeds state from a 128-bit key.
- `SipHash_Update()` streams bytes through 8-byte blocks.
- `SipHash_End()` pads with message length, finalizes, zeroes context, and returns a 64-bit digest.
- `SipHash_Final()` writes little-endian digest bytes.
- `SipHash()` is the one-shot helper.

Integration:
- Implements `siphash.h`.
- Uses unaligned little-endian loads and `rol64`.

Risks and invariants:
- `ctx->bytes` is a `u32`, so very long streams wrap length encoding.
- `SipHash_Update()` copies trailing bytes into `ctx->buf[used]`; correctness depends on `used` handling across partial updates.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/siphash.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/siphash.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/siphash.h

Purpose: Public SipHash types, constants, and round-profile macros.

Key APIs and behavior:
- Defines block, key, and digest lengths.
- `SIPHASH_CTX` stores state words, partial block buffer, and byte count.
- `SIPHASH_KEY` stores two little-endian 64-bit key words.
- Declares generic `SipHash_*` functions and convenience macros for SipHash-2-4 and SipHash-4-8.

Integration:
- Implemented by `siphash.c`.
- Uses Linux integer types.

Risks and invariants:
- Callers must provide a 16-byte key.
- Macro profiles pass fixed round counts into generic functions.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/siphash.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/six.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/six.c

Purpose: Implementation of sleepable shared/intent/exclusive locks.

Key APIs and behavior:
- Fast path uses an atomic state word for read, intent, write, wait bits, and no-spin flag.
- Optional per-CPU reader mode avoids atomic reader increments.
- Slow path inserts stable RCU wait slots, supports waitlist growth, and wakes eligible waiters.
- Non-reader wakeups choose the oldest matching transaction start time; readers wake as a group.
- Supports trylock, relock by sequence, blocking lock with cycle-detection callback, contended-only path, unlock, downgrade, upgrade, conversion, recursive count increment, wake-all, counts, reader-count adjustment, init, and exit.

Integration:
- Implements `six.h`.
- Uses lockdep, scheduler tracing, RCU, percpu allocation, and optional optimistic spinning.
- Designed for bcachefs tree/transaction locking where intent avoids read-to-write upgrade deadlocks.

Risks and invariants:
- Write lock requires intent ownership.
- Wait slots are RCU-visible and must not move while cycle detectors may scan them.
- `should_sleep_fn` errors can require undoing a lock that was concurrently acquired.
- Per-CPU reader mode relies on memory barriers paired across read and write paths.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/six.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/six.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/six.h

Purpose: Public interface and data structures for SIX locks.

Key APIs and behavior:
- Documents read, intent, and write semantics, sequence relock, reentrancy counters, and cycle-detection waiters.
- Defines `enum six_lock_type`, `struct six_lock_waiter`, wait-slot/fifo types, and `struct six_lock`.
- Provides init macro, trylock/relock/unlock wrappers for each lock type, and generic type-based APIs.
- Declares conversion, downgrade, upgrade, wake-all, counts, and reader-count adjustment helpers.

Integration:
- Implemented by `six.c`.
- Includes `fifo.h` and `util.h`.
- Exposes lockdep fields under debug lock allocation.

Risks and invariants:
- Waiter `trans_start_time` is used for fairness and cycle-detection cursoring.
- Inline FIFO starts with eight waiters and grows under wait lock.
- Reentrancy is not automatic; upper layers must track held locks and call increment APIs correctly.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/six.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/thread_with_file.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/thread_with_file.c

Purpose: Runs a kernel thread attached to an anonymous file descriptor, with optional stdio-style redirection.

Key APIs and behavior:
- `bch2_run_thread_with_file()` creates a kthread, creates an anon inode file, installs an fd, and starts the task.
- `bch2_thread_with_file_exit()` stops the task and drops the task reference.
- Stdio mode implements read, write, poll, flush, release, and ioctl file operations.
- Input/output buffers are darrays protected by spinlocks and wait queues.
- Provides blocking/nonblocking writes, read, readline with timeout, printf/vprintf output, and stdout-only mode.

Integration:
- Implements `thread_with_file.h`.
- Guarded by `NO_BCACHEFS_FS`.
- Uses anon inodes, kthreads, file descriptors, fault-in/copy nofault helpers, wait queues, and darray.

Risks and invariants:
- Release marks stdio done, stops the kthread, frees buffers, then calls caller exit op.
- Nonblocking output writes are atomic by message.
- Readline can grow the destination darray and tracks `waiting_for_line` to avoid chopping lines.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/thread_with_file.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/thread_with_file.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/thread_with_file.h

Purpose: Public API for fd-backed kernel threads and stdio redirection.

Key APIs and behavior:
- Defines low-level `struct thread_with_file` with task, return value, and done flag.
- Defines `thread_with_stdio_ops` for exit, main function, and ioctl hook.
- Defines `struct thread_with_stdio` combining thread state, stdio buffers, and ops.
- Declares run/init/read/readline/write/printf helpers.

Integration:
- Implemented by `thread_with_file.c`.
- Uses `thread_with_file_types.h`.

Risks and invariants:
- Low-level users with custom file operations must call `bch2_thread_with_file_exit()` from release.
- Closing the fd is the shutdown signal.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/thread_with_file.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/thread_with_file_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/thread_with_file_types.h

Purpose: Shared buffer types for thread-with-stdio plumbing.

Key APIs and behavior:
- `struct stdio_buf` contains a spinlock, wait queue, char darray, and `waiting_for_line`.
- `struct stdio_redirect` contains input and output buffers plus a done flag.

Integration:
- Included by `thread_with_file.h` and used by `thread_with_file.c`.
- Depends on `darray.h`.

Risks and invariants:
- Buffer locking/wakeup behavior is implemented externally.
- `done` terminates blocking reads/writes.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/thread_with_file_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/time_stats.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/time_stats.c

Purpose: Collects and formats duration and inter-arrival-time statistics.

Key APIs and behavior:
- Chooses display units from ns through years/eon.
- Updates duration and frequency stats with exact mean plus median/MAD estimates.
- Optional quantile estimator uses Eytzinger-indexed entries.
- Automatically switches to per-CPU buffering for frequent events unless disabled.
- Emits human-readable text and JSON through `seq_buf`.
- Provides reset, init, no-percpu init, and exit.

Integration:
- Implements `time_stats.h`.
- Uses `mean_and_variance`, `eytzinger`, percpu buffers, local clock, and spinlocks.
- Used by writeback throttling and diagnostics.

Risks and invariants:
- Buffered per-CPU events are flushed under the main stats lock before rendering.
- `__bch2_time_stats_clear_buffer()` iterates the full fixed entry array, not just `nr`, which can process zeroed entries after init/reset.
- Min fields initialize to `U64_MAX`; JSON maps that to zero for empty output.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/time_stats.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/time_stats.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/time_stats.h

Purpose: Public data model and helpers for bcachefs time statistics.

Key APIs and behavior:
- Defines `time_unit`, quantile constants/structures, per-CPU event buffer, and `struct bch2_time_stats`.
- Tracks min/max/total duration, min/max frequency, last event times, lifetime start, and weighted/unweighted estimators.
- `bch2_time_stats_update()` records an event ending at `local_clock()`.
- `track_event_change()` tracks boolean state intervals.
- Declares text/JSON output, init/reset/exit, and quantile wrapper init/exit.

Integration:
- Implemented by `time_stats.c`.
- Depends on `mean_and_variance.h`.

Risks and invariants:
- Time values are nanoseconds.
- `TIME_STATS_MV_WEIGHT` gives weighted estimator half-life around 256 samples.
- Quantiles are explicitly discouraged for new code unless manually enabled.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/time_stats.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/two_state_shared_lock.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/two_state_shared_lock.c

Purpose: Blocking slow path for the two-state shared lock.

Key APIs and behavior:
- `__bch2_two_state_lock()` waits until `bch2_two_state_trylock(lock, s)` succeeds.
- Uses `__wait_event()` on the lock wait queue.

Integration:
- Implements the out-of-line path declared in `two_state_shared_lock.h`.

Risks and invariants:
- Wakeups rely on unlock waking all waiters when the shared count reaches zero.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/two_state_shared_lock.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/two_state_shared_lock.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/two_state_shared_lock.h

Purpose: Lock where two opposing states are each shared internally but mutually exclusive.

Key APIs and behavior:
- `two_state_lock_t` stores a signed atomic count and wait queue.
- Positive count represents one state; negative count represents the other.
- `bch2_two_state_trylock()` atomically increments or decrements only if the opposite state is absent.
- `bch2_two_state_unlock()` subtracts the state count and wakes all when zero.
- `bch2_two_state_lock()` uses trylock then blocking slow path.

Integration:
- Slow path implemented in `two_state_shared_lock.c`.
- Uses `EBUG_ON` from `util.h`.

Risks and invariants:
- Caller-provided state `s` is interpreted as boolean.
- Overflow of the signed atomic count is not guarded.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/two_state_shared_lock.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/util.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/util.c

Purpose: General utility implementations for parsing, printing, throttling, bio handling, and misc helpers.

Key APIs and behavior:
- Human-readable numeric parsers accept decimal fractions and binary/SI suffixes.
- Flag-list parser maps comma/semicolon-separated names to a bitmask.
- Implements zero checking, binary printing, line-safe printk output, stack backtrace capture/printing, datetime/time-unit printing.
- Renders `bch2_time_stats` through printbuf and JSON-through-seqbuf.
- Implements rate-limit delay/increment and PD controller update/debug output.
- Implements bio mapping/chaining, synchronous buffer submit, bio page allocation, random bounded u64, bio memcpy helpers, debug bio corruption, and bio text dump.
- Implements percpu u64 accumulation, colon-separated device splitting, kvmalloc mempool wrappers, and iowait-aware wait-bit timeout.

Integration:
- Implements declarations in `util.h`.
- Uses printbuf, time_stats, mean_and_variance, eytzinger, bio/block APIs, mempool APIs, and scheduler helpers.

Risks and invariants:
- `bch2_bio_map_and_chain()` submits earlier chain segments and returns only the tail.
- `bch2_bio_alloc_pages()` requires power-of-two block size and aligned size.
- Human-size parsing carefully checks overflow, but signed conversion stores through `u64` before assignment.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/util.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/util.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/util.h

Purpose: Broad utility header for kernel/userspace portability, allocation, printing, parsing, bio helpers, and low-level macros.

Key APIs and behavior:
- Provides debug `EBUG_ON`, endian detection, type compatibility macros, kernel-version shims, and allocation helpers.
- Re-exports printbuf APIs under shorter names.
- Declares human-readable string parsers, print helpers, backtrace helpers, time-stat renderers, rate limiter, and PD controller APIs.
- Defines list, array, gap-buffer, sort, percpu, qstr, bit, flag-mapping, and error-propagation helpers.
- Declares bio helpers and kthread wait macros.
- Provides u64 copy/move helpers that intentionally bypass some fortify limitations for array-like storage.
- Defines memalloc guard class and wait-bit IO timeout wrapper.

Integration:
- Included by many utility and VFS files.
- Depends on closure, darray, printbuf, mean_and_variance, and time_stats.

Risks and invariants:
- Many helpers are macros with side effects and type assumptions.
- Some compatibility shims are kernel-version-sensitive.
- Low-level memory helpers expect caller-provided object-size correctness.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/util.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/varint.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/varint.c

Purpose: Encodes and decodes bcachefs variable-length unsigned integers.

Key APIs and behavior:
- `bch2_varint_encode()` emits 1 to 9 bytes using low-bit prefix markers.
- `bch2_varint_decode()` determines width with `ffz()` and checks the buffer end.
- Fast variants assume it is safe to read/write up to 8 bytes beyond the logical varint footprint, while still reporting bounds errors.
- Values needing 9 bytes use marker byte `255` followed by raw little-endian u64.

Integration:
- Implements `varint.h`.
- Uses `BCH_ERR_varint_decode_error` from `errcode.h`.

Risks and invariants:
- Fast decode requires padded readable memory; Valgrind memory is marked defined when configured.
- Decode comments say "encode" in one docblock, but behavior is decode.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/varint.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/varint.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/varint.h

Purpose: Public declarations for varint encode/decode helpers.

Key APIs and behavior:
- Declares safe encode/decode and fast encode/decode variants.
- All functions operate on `u8 *`/`const u8 *` buffers and `u64` values.

Integration:
- Implemented by `varint.c`.

Risks and invariants:
- Header does not document the fast-path padding assumptions; callers need to know them from implementation or surrounding conventions.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/varint.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/vstructs.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/vstructs.h

Purpose: Macros for variable-length on-disk structures whose payload length is measured in u64s.

Key APIs and behavior:
- Reads `_s->u64s` with endian conversion depending on field type.
- Computes total u64s, bytes, block count, sector count, next/end pointers, and indexed entries.
- Provides iteration macros over variable-length embedded records.

Integration:
- Depends on `util.h` for type inspection and common helpers.
- Intended for structures with `_data`, `start`, and `u64s` conventions.

Risks and invariants:
- Assumes `_data` offset is u64-aligned.
- Notes inability to distinguish `__le64` from `u64` with `type_is`, assuming little-endian semantics for u64 fields.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/vstructs.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/vfs/buffered.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/vfs/buffered.c

Purpose: Buffered VFS read, readahead, writeback, and buffered-write implementation for bcachefs.

Key APIs and behavior:
- Readahead collects folios, creates bcachefs folio state, extends bios across extents when profitable, and submits reads through bcachefs extent lookup.
- `bch2_read_single_folio()` performs synchronous single-folio reads for page faults/write preparation.
- Writeback builds `bch_writepage_io` bios from dirty folio-sector ranges, throttles against allocator/journal pressure, and accounts sectors on completion.
- `bch2_write_begin()` and `bch2_write_end()` implement buffered write reservation, partial-folio read/zero handling, dirty marking, i_size update, and reservation release.
- `bch2_buffered_write()` performs multi-folio atomic user copies with fault-in, fallback for short/no copies, dirty balancing, and pagecache cleanup after short post-EOF writes.
- `bch2_write_iter()` dispatches direct IO separately and serializes buffered writes against snapshot creation.

Integration:
- Uses bcachefs read/write paths, btree transactions, snapshot lookup/locks, pagecache helpers, folio reservations, allocator/journal waiters, and Linux writeback APIs.
- Declared in `buffered.h`; also calls direct-write API from `direct.h`.

Risks and invariants:
- `bchfs_read()` temporarily mutates `bio.bi_iter.bi_size`; comments warn transaction-restart behavior would be dangerous there.
- Writeback relies on per-sector folio state and write counts to end writeback exactly once.
- Buffered writes assume synchronous same-task lock/unlock around snapshot create lock.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/vfs/buffered.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/vfs/buffered.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/vfs/buffered.h

Purpose: Public declarations for buffered VFS IO.

Key APIs and behavior:
- Defines `struct bch_writepage_io` wrapping inode pointer and trailing `bch_write_op`.
- Declares single-folio read, VFS read_folio, writepages, readahead, write_begin/write_end, and write_iter.
- Adapts `write_begin`/`write_end` prototypes for kernel version 6.17+.

Integration:
- Implemented by `buffered.c`.
- Guarded by `NO_BCACHEFS_FS`.
- Includes write type definitions.

Risks and invariants:
- `bch_writepage_io` requires `op` to remain last for container/bioset allocation layout.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/vfs/buffered.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/vfs/direct.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/vfs/direct.c

Purpose: Direct IO read/write implementation for bcachefs VFS.

Key APIs and behavior:
- Direct reads validate 512-byte alignment, clamp to file size, build one or more bios from the iov_iter, and complete synchronously or asynchronously via closures.
- Direct read path flushes overlapping cached writes before issuing O_DIRECT.
- `bch2_read_iter()` dispatches direct reads or falls back to `filemap_read` under pagecache-add guard.
- Direct writes validate block alignment, perform generic write checks, invalidate overlapping pagecache, block pagecache additions, and use inode DIO lifetime references.
- Write loop maps user pages under faults-disabled mapping tracking, handles dropped pagecache locks, trims unaligned tails, reserves quota/disk space, and submits bcachefs writes.
- Async direct writes copy iovec state when continuation may outlive caller stack and use `kthread_use_mm()` for continuation mapping.
- Dsync writes optionally flush journal and nocow writes before completion.

Integration:
- Declared in `direct.h`.
- Uses VFS/pagecache helpers, bcachefs data read/write, quota/accounting, fault-disabled mapping table from `fdm.h`, and enumerated write refs.

Risks and invariants:
- Direct writes extending i_size are forced synchronous.
- Fault handler/pagecache invalidation interaction is delicate and signaled through `fdm_dropped_locks`.
- Async path must own copied iovecs before returning `-EIOCBQUEUED`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/vfs/direct.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/vfs/direct.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/vfs/direct.h

Purpose: Public direct-IO structures and function declarations.

Key APIs and behavior:
- `struct dio_read` contains closure, kiocb, return value, dirty-page decision, and embedded read bio.
- `struct dio_write` tracks request, mapping, inode, mm, iov copy, async/sync flags, quota reservation, written sectors, iterator, inline vectors, and trailing write op.
- Declares direct read, direct write, and read_iter entry points.

Integration:
- Implemented by `direct.c`.
- Depends on bcachefs read/write and VFS IO types.

Risks and invariants:
- `bch_write_op op` must remain last in `dio_write` for allocation/container layout.
- Async write continuation depends on saved iterator/iovec lifetime.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/vfs/direct.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/vfs/fdm.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/vfs/fdm.h

Purpose: Faults-disabled-mapping hash table used by direct IO to avoid page-fault deadlocks.

Key APIs and behavior:
- Fixed-size 3-way cuckoo-style table keyed by current task.
- `fdm_set()` records current task's mapping and waits on a closure waitlist if all candidate slots are occupied.
- `fdm_get()` retrieves current task's mapping.
- `fdm_set_dropped_locks()` sets a low-bit flag in the mapping word.
- `fdm_dropped_locks()` tests that flag.
- `fdm_clear()` removes current task and wakes waiters.
- `fdm_init()` zeroes the table and seeds independent hash functions.

Integration:
- Used by direct IO write mapping/page-fault coordination in `direct.c`.
- Intended to replace a removed per-task `faults_disabled_mapping` field.
- Uses `closure_waitlist`, random seeds, and lockless READ/WRITE_ONCE with barriers.

Risks and invariants:
- Only the owning current task should insert/remove its entry.
- Low bit of `address_space *` is stolen for dropped-lock signaling, relying on pointer alignment.
- Recursive retry in `fdm_set()` handles lost races after wakeup.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/vfs/fdm.h -->