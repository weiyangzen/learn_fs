# subset-b-009685 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/moodycamel/concurrentqueue.h -->
# sources/user-network-fs/mergerfs/vendored/moodycamel/concurrentqueue.h

## Purpose

This header vendors Cameron Desrochers' `moodycamel::ConcurrentQueue`, a C++11 header-only multi-producer, multi-consumer queue. It is intended to provide high-throughput lock-free enqueue/dequeue operations for mergerfs or vendored consumers without requiring a compiled library. The design uses per-producer subqueues, fixed-size element blocks, producer/consumer tokens, and atomic coordination rather than one central locked queue.

## Important APIs, Types, And Functions

- `moodycamel::ConcurrentQueueDefaultTraits` configures `size_t`, `index_t`, `BLOCK_SIZE`, initial block-index sizes, implicit producer hash size, explicit consumer rotation quota, `MAX_SUBQUEUE_SIZE`, `MAX_SEMA_SPINS`, allocation hooks, and whether dynamically allocated blocks are recycled.
- `moodycamel::ConcurrentQueue<T, Traits>` is the main public type. Public operations include constructors with preallocation hints, move construction/assignment, `swap`, `enqueue`, `try_enqueue`, `enqueue_bulk`, `try_enqueue_bulk`, `try_dequeue`, token-aware dequeue variants, `try_dequeue_bulk`, `try_dequeue_from_producer`, `size_approx`, and `is_lock_free`.
- `moodycamel::ProducerToken` owns an explicit producer stream. It is movable, non-copyable, has `valid()`, and marks its underlying producer inactive on destruction.
- `moodycamel::ConsumerToken` stores a consumer's current producer selection, desired producer, global rotation offset, and per-producer consumption quota state.
- Internal `ProducerBase`, `ExplicitProducer`, and `ImplicitProducer` implement subqueue-specific enqueue/dequeue behavior. Explicit producers keep a circular linked list of blocks plus a published block index. Implicit producers are looked up by thread ID and use a separate lock-free block-index table.
- Internal `Block` stores `BLOCK_SIZE` in-place `T` objects in aligned raw storage, plus empty flags or a completed-dequeue counter. It is also a node in the queue's lock-free free list.
- Internal `FreeList<N>` is a CAS-based free list with a refcount and a "should be on free list" bit to avoid freeing nodes while another thread is reading the list head.
- `details::ThreadExitNotifier` and `ThreadExitListener` retire implicit producers when a thread exits on platforms where C++11 `thread_local` is enabled.
- `moodycamel::swap` overloads support queue, producer token, consumer token, and internal implicit producer hash-entry swapping.

## Control Flow

Construction initializes atomic queue state, the implicit producer hash if enabled, and an initial block pool sized from either raw capacity or producer/capacity hints. Public implicit `enqueue` resolves the calling thread to an implicit producer through `get_or_add_implicit_producer`; explicit `enqueue` uses the `ProducerToken`'s producer directly. The producer then reserves space at `tailIndex`, allocates or reuses a block if the tail crosses a block boundary, placement-news the element, and finally publishes the incremented `tailIndex` with release ordering.

`try_enqueue` follows the same producer paths with `AllocationMode::CannotAlloc`, so it can fail when block-index growth, block allocation, or capacity growth would be required. Bulk enqueue preallocates all needed block-index entries and blocks first, then constructs elements block by block, reverting partially built state on constructor exceptions.

General `try_dequeue` scans producer subqueues, prefers a heuristically largest non-empty producer, and falls back to all producers if the preferred one races empty. Token-aware dequeue uses `ConsumerToken` rotation: consumers start at different producers, consume up to `EXPLICIT_CONSUMER_CONSUMPTION_QUOTA_BEFORE_ROTATE`, then increment `globalExplicitConsumerOffset` so all token consumers gradually move to the next producer. Producer-specific dequeue bypasses this scan and directly drains one explicit producer.

Both explicit and implicit producers use the same optimistic dequeue pattern: read `tailIndex`, compare `dequeueOptimisticCount - dequeueOvercommit` against the tail, increment the optimistic counter, re-read the tail with acquire ordering, then either claim a `headIndex` slot or repair overcommit. Claimed elements are moved into the caller's output, destroyed in place, and their block slot is marked empty. Implicit blocks are returned to the global free list once all slots are empty; explicit producers keep their circular block list and reuse empty blocks.

Implicit producer lookup hashes a platform-specific thread ID into the current `ImplicitProducerHash`, searches current and previous hash tables, lazily copies older entries forward, and resizes when the table crosses about half full. Thread-exit notification marks implicit producer hash entries reusable with `invalid_thread_id2` and sets the producer inactive for later reuse.

Destruction is explicitly not thread-safe. It walks the producer list, invalidates live tokens, destroys producer-owned elements and block-index structures, frees implicit hash tables, drains the global free list, and destroys the initial block pool.

## State And Persistence Behavior

All state is in memory. Persistent queue state consists of atomics and heap/preallocated structures inside the queue object: producer list tail/count, initial block pool and cursor, global free list, implicit producer hash chain and resize flag, consumer rotation counters, and per-producer head/tail/dequeue counters. Elements are stored in raw block storage and explicitly constructed/destructed.

The queue is movable and swappable only when no other thread is using it. Moving transfers producers, block pools, free lists, and hash state, then calls `reown_producers()` so producer parent pointers refer to the destination queue. Tokens remain semantically attached to the moved queue state, not to the original object address.

Memory allocation is controlled through traits. `aligned_malloc` uses trait `malloc` directly for normal alignments and stores a raw pointer prefix for over-aligned internal types. `RECYCLE_ALLOCATED_BLOCKS` controls whether dynamically allocated blocks go into the free list or return to the heap when no longer owned.

## Dependencies

The header depends on C++11 atomics, type traits, aligned storage assumptions, arrays, threads, mutexes, and platform-specific thread ID strategies. It conditionally uses Windows `GetCurrentThreadId`, Apple `TargetConditionals.h`, Relacy headers for race-detection builds, compiler-specific TLS storage, TSAN suppression attributes, and optional internal debug headers. It has no runtime file, socket, or process persistence.

## Integration Points

Consumers include this header and instantiate `ConcurrentQueue<T>` or `ConcurrentQueue<T, CustomTraits>`. Blocking variants are only forward declared here and are expected to be supplied by the companion blocking queue header. Explicit producer tokens are created from either `ConcurrentQueue` or `BlockingConcurrentQueue` through friend constructors. A custom mergerfs integration can tune block size, initial producer hash size, allocation hooks, max subqueue size, and allocation recycling through a traits subclass.

The source is vendored under `sources/user-network-fs/mergerfs/vendored/moodycamel`, so updates should be treated as third-party upgrades. Local changes to memory ordering, token lifetime, or trait defaults would be high risk.

## Risks And Edge Cases

- Destruction, move, and swap are not thread-safe. External synchronization must prove no producers or consumers are active.
- `ProducerToken` and `ConsumerToken` are non-copyable and queue-specific. Reusing a token after its queue is destroyed or with the wrong moved/swapped queue state is invalid.
- `try_enqueue` is not strictly allocation-free for first-time implicit producer creation, and it can fail if implicit producer hashing is disabled or block/index capacity is insufficient.
- `size_approx()` is only accurate when the queue has stabilized and concurrent operations are not racing the estimate.
- `index_t` wraparound is part of the design, but narrow `index_t` values with high turnover can trigger correctness risks noted in the traits comments.
- The queue does not support element types whose alignment exceeds their size.
- Exception paths try to destroy or revert partially enqueued/dequeued elements, but user-provided `T` move assignment or construction behavior can still affect observable dequeue semantics.
- TSAN may report false positives in lock-free paths; the header suppresses selected functions only when Clang TSAN feature detection is active.
- Platform TLS support controls implicit producer cleanup. Defining `MOODYCAMEL_NO_THREAD_LOCAL` or building on unsupported TLS platforms changes implicit producer reuse behavior.

## Test Signals

Useful validation includes compiling all translation units that include this header with the repository's actual compiler flags, running producer/consumer stress tests with implicit and explicit producers, exercising bulk and single-item APIs, validating `try_enqueue` under constrained preallocation traits, running queue destruction only after joining worker threads, and testing with non-trivial `T` types that throw on construction or assignment. Concurrency tests should cover high producer churn to exercise implicit producer hash resize and thread-exit reuse. Sanitizer results need interpretation because lock-free code may generate TSAN noise.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/moodycamel/concurrentqueue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/moodycamel/lightweightsemaphore.h -->
# sources/user-network-fs/mergerfs/vendored/moodycamel/lightweightsemaphore.h

## Purpose

This header vendors `moodycamel::LightweightSemaphore`, a small C++11 semaphore abstraction used by moodycamel blocking queues and other producer/consumer code. It combines an atomic count with a platform semaphore so uncontended waits remain cheap while contended waits sleep in the operating system.

## Important APIs, Types, And Functions

- `moodycamel::details::Semaphore` is a platform wrapper. Implementations exist for Windows, Mach/Darwin, POSIX Unix, and z/OS. It exposes `wait`, `try_wait`, `timed_wait`, and `signal`.
- `moodycamel::LightweightSemaphore` is the public type. It defines signed `ssize_t`, stores `std::atomic<ssize_t> m_count`, a `details::Semaphore m_sema`, and `int m_maxSpins`.
- Public methods are `tryWait`, `wait()`, `wait(timeout_usecs)`, `tryWaitMany(max)`, `waitMany(max, timeout_usecs)`, `waitMany(max)`, `signal(count)`, and `availableApprox()`.
- Private helpers `waitWithPartialSpinning` and `waitManyWithPartialSpinning` implement the spin-then-block paths and timeout repair logic.

## Control Flow

Construction asserts non-negative initial count and spin count, initializes the atomic count, and initializes the underlying platform semaphore with its default initial count. Fast-path `tryWait` repeatedly loads `m_count` and uses CAS to decrement it only when it is positive. `wait()` first calls `tryWait`; if no token is available it enters `waitWithPartialSpinning`.

`waitWithPartialSpinning` spins up to `m_maxSpins`, each time trying to decrement a positive count with acquire semantics and using `atomic_signal_fence` to keep the compiler from collapsing the loop. If spinning fails, it decrements `m_count`. A positive old count means it acquired a token without sleeping. A non-positive old count means it is now represented as a waiter, so it blocks on the OS semaphore for indefinite waits or uses the platform timed wait for positive timeouts.

If a timed wait expires, the method must repair `m_count` because it already decremented it before sleeping. The repair loop either consumes a semaphore signal that arrived after timeout bookkeeping (`oldCount >= 0 && m_sema.try_wait()`) or CAS-increments a negative waiter count back toward zero and returns false.

`tryWaitMany` greedily decrements up to `max` available tokens with one CAS. `waitManyWithPartialSpinning` first tries the same spin/CAS approach, otherwise blocks for one token and then greedily drains additional tokens with `tryWaitMany(max - 1)`. `signal(count)` release-adds to `m_count` and signals the OS semaphore only for the portion of `count` that corresponds to negative pre-existing waiters.

## State And Persistence Behavior

The semaphore has no persistent state outside process memory. `m_count` is positive for available tokens, zero for no available tokens/no known waiters, and negative when waiters have decremented the count before blocking. The platform semaphore is the sleep/wakeup mechanism for negative-count waiters. `availableApprox()` is a relaxed snapshot and returns zero for non-positive counts.

Platform wrappers own OS resources: Windows closes the handle, Mach destroys the Mach semaphore, and POSIX/zOS calls `sem_destroy`. Copy construction and assignment are disabled.

## Dependencies

The header depends on C++ atomics, assertions, errno handling, `std::size_t`, integer types, `clock_gettime`, and `std::make_signed`. Platform dependencies are direct declarations of Windows semaphore APIs, Mach semaphore APIs, z/OS semaphore APIs, or POSIX `sem_t`. On glibc 2.30+ with `_GNU_SOURCE`, POSIX timed waits use `sem_clockwait` with `CLOCK_MONOTONIC`; otherwise they use `sem_timedwait` with `CLOCK_REALTIME`.

## Integration Points

This file is the low-level wait primitive for moodycamel blocking queues. The default spin count matches `ConcurrentQueueDefaultTraits::MAX_SEMA_SPINS`, and blocking queue code can tune spin behavior through construction. It is header-only and does not include `windows.h`, which keeps global namespace pollution low for mergerfs translation units.

## Risks And Edge Cases

- Unsupported platforms fail at compile time with `#error Unsupported platform!`.
- Timed waits use microseconds, but Windows converts to milliseconds by integer division, so sub-millisecond waits become zero-millisecond waits.
- POSIX non-monotonic timed waits use `CLOCK_REALTIME`; system clock adjustments can affect timeout duration unless the monotonic glibc path is enabled.
- `signal(count)` casts the number of OS releases to `int`; extremely large counts beyond `int` range would be unsafe even though normal use signals modest counts.
- `waitMany(max)` asserts that it acquired at least one token. Passing zero to the no-timeout overload is inconsistent with that assertion and should be avoided.
- Like most synchronization primitives, destruction while threads may be waiting is unsafe and must be externally synchronized.
- The repair loop after timeout is subtle. Changes to memory ordering or semaphore try-wait behavior can introduce lost wakeups.

## Test Signals

Validation should cover uncontended `tryWait`/`signal`, many waiters woken by one `signal(count)`, timeout expiration, signals racing with timeout repair, `waitMany` greedy acquisition, and destruction only after all waiters have joined. Platform CI should compile at least Linux/POSIX and any target OS mergerfs supports. On Linux, tests should exercise both realtime and monotonic timed wait builds when feature macros permit.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/moodycamel/lightweightsemaphore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/nonstd/string.hpp -->
# sources/user-network-fs/mergerfs/vendored/nonstd/string.hpp

## Purpose

This header vendors a "bare" subset of Martin Moene's `string-lite`. It provides header-only string-view compatibility and a collection of free string utility functions under `nonstd`, with optional support for several character types. The default configuration enables `char` utilities and disables wide/UTF character utilities and regex variants unless a tweak header or configuration macro changes that.

## Important APIs, Types, And Functions

- Configuration macros include `string_CONFIG_PROVIDE_CHAR_T`, `string_CONFIG_PROVIDE_WCHAR_T`, `string_CONFIG_PROVIDE_CHAR8_T`, `string_CONFIG_PROVIDE_CHAR16_T`, `string_CONFIG_PROVIDE_CHAR32_T`, `string_CONFIG_PROVIDE_REGEX`, and `string_CONFIG_NO_EXCEPTIONS`.
- Feature macros detect C++ language level, compiler versions, `constexpr`, `noexcept`, `nodiscard`, `nullptr`, `string_view`, `char8_t`, regex, and type traits support.
- `nonstd::string::npos` mirrors `std::string_view::npos` or `std::string::npos`.
- `nonstd::string::std17::basic_string_view<CharT, Traits>` aliases `std::basic_string_view` when available. Otherwise the header defines a local minimal string view with constructors from pointers and strings, conversion to `std::basic_string`, `find`, `rfind`, `find_first_of`, `find_last_of`, `find_first_not_of`, `find_last_not_of`, `compare`, `substr`, iterators, and comparison operators.
- Character-specific typedefs include `string_view`, `wstring_view`, `u8string_view`, `u16string_view`, and `u32string_view` when enabled.
- `nonstd` free functions are macro-generated by character type: `is_empty`, `length`, `size`, `find_first`, `find_last`, `find_first_of`, `find_last_of`, `find_first_not_of`, `find_last_not_of`, `contains`, `contains_all_of`, `contains_any_of`, `contains_none_of`, `starts_with`, `starts_with_all_of`, `starts_with_any_of`, `starts_with_none_of`, `ends_with`, `ends_with_all_of`, `ends_with_any_of`, `ends_with_none_of`, `append`, `erase`, `erase_all`, `erase_first`, `erase_last`, `insert`, `replace`, `replace_all`, `replace_first`, `replace_last`, `strip_left`, `strip_right`, `strip`, `substring`, `to_lowercase`, `to_uppercase`, `capitalize`, `join`, `split`, `split_left`, `split_right`, and `compare`.
- Helpers in `nonstd::string::detail` implement null strings, default strip sets, string-view-to-string conversion, locale-backed case conversion, erase/replace-all loops, and split primitives.

## Control Flow

At inclusion time the header optionally includes `<nonstd/string.tweak.hpp>`, sets configuration defaults, detects compiler and standard-library capabilities, and includes standard headers. If the standard library has `std::basic_string_view`, `nonstd::string::std17::basic_string_view` aliases it; otherwise a local non-owning view class is compiled.

The fallback view stores only `data_` and `size_`. Search functions delegate to standard algorithms such as `std::search`, `std::find_end`, `std::find_first_of`, and `std::find_if`. `substr` either asserts or throws `std::out_of_range` depending on exception configuration.

Most public utilities are generated by macros for each configured `CharT`. Observer functions forward to string-view methods. Search and predicate functions build on string-view find operations. Prefix/suffix functions use native C++20 `starts_with`/`ends_with` when available and otherwise use `std::equal`. Modifier-style functions generally return a new `std::basic_string<CharT>` and leave inputs untouched.

`erase_all` and `replace_all` copy the input string and loop over `find_first` from the current position until no match remains. `replace_all` exits early if the replacement equals the needle. `strip_left`, `strip_right`, and `strip` remove characters in a default or supplied strip set. Case conversion copies to `std::basic_string` and applies `std::tolower`/`std::toupper` with a default `std::locale`. `split` repeatedly calls `split_left` and returns a vector of string views into the original text.

At the end of the file all `string_MK_*` implementation macros are undefined, leaving the generated functions and type aliases.

## State And Persistence Behavior

The header has no mutable global state and no persistence. It defines compile-time constants, inline functions, and type aliases. Fallback `basic_string_view` is non-owning and depends on the lifetime of the referenced character data. Most transformation utilities allocate and return new `std::basic_string` objects. Split functions return `basic_string_view` slices into the original input, so callers must keep the original string storage alive.

## Dependencies

The header depends on `<cassert>`, `<algorithm>`, `<iterator>`, `<locale>`, `<limits>`, `<string>`, `<tuple>`, and `<vector>`, with optional `<string_view>` and `<regex>`. It may include `<nonstd/string.tweak.hpp>` if available. It uses compiler feature macros for MSVC, Clang, Apple Clang, and GCC.

## Integration Points

Mergerfs code can include this header to get portable string utilities without requiring C++17 `std::string_view`. Default exports are `char`-only, which keeps compile time lower. Wider character support is controlled by defining configuration macros before inclusion or through the tweak header. The API lives mostly in namespace `nonstd`, while compatibility types and helpers live under `nonstd::string`.

## Risks And Edge Cases

- Returned `string_view` slices from `split`, `split_left`, and `split_right` are non-owning. Passing a temporary string can leave dangling views.
- `erase_all` and `replace_all` do not guard against an empty `what` needle. With an empty needle, repeated erase/replace operations can loop forever or repeatedly insert, depending on the standard-library behavior.
- `replace_first` and `replace_last` return an empty string when the needle is not found, while `erase_first` and `erase_last` return the original string. That asymmetry is easy to misuse.
- `strip_right` computes `find_last_not_of(set) + 1`; when all characters are stripped, `npos + 1` wraps to zero for unsigned `size_t`, which happens to erase from the beginning but relies on wraparound.
- Case conversion uses `std::tolower` and `std::toupper` with `std::locale()` and generic `CharT`; behavior for UTF character types is not Unicode case folding.
- `starts_with_all_of` and `ends_with_all_of` require all characters in the set to appear in the contiguous prefix or suffix, not simply that the first/last character belongs to a set.
- Fallback `basic_string_view(CharT const*)` calls `Traits::length(s)` and does not accept null pointers.
- Because large API families are macro-generated, configuration changes can silently add many overloads and increase compile time.

## Test Signals

Useful tests include compiling under C++11 and C++17/20 modes, verifying fallback and standard `string_view` paths, exercising default `char` APIs, enabling each optional character type in a small translation unit, and checking edge cases for empty strings, empty needles, all-whitespace strip inputs, not-found replace calls, split view lifetimes, and locale-sensitive case conversion. Tests should also verify that consumers include the header with their intended configuration macros before any first inclusion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/nonstd/string.hpp -->
