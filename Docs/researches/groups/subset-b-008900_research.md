# subset-b-008900 Research

This grouped report covers TiKV `tikv_util` memory, metrics, channel, quota, store, stream, and system utility files. Each section is source-tree-aligned and intended to be split into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/memory.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/memory.rs

## Purpose
Provides low-level memory accounting helpers for TiKV utility code: approximate heap-size estimation for common container/protobuf types, unsafe vector layout conversion, and an atomic quota counter that can reject or force account allocations. It is performance-sensitive and favors O(1) approximations over deep traversal.

## Important APIs, Types, and Functions
- `unsafe fn vec_transmute<F, T>(Vec<F>) -> Vec<T>` reinterprets a vector after debug-checking size and alignment; correctness depends entirely on the caller preserving layout invariants.
- `trait HeapSize` exposes `approximate_heap_size` and `approximate_mem_size`; implementations exist for scalars, `Vec<T>`, `Option<T>`, tuples, `HashMap<K,V>`, `Either`, and selected `kvproto` structures.
- `MemoryQuotaExceeded` is the lightweight error for denied quota allocations.
- `MemoryQuota` owns `in_use: AtomicIsize` and `capacity: AtomicUsize`, with `new`, `in_use`, `used_ratio`, `capacity`, `set_capacity`, `alloc`, `alloc_force`, and `free`.
- `OwnedAllocated` is an RAII allocation token that records bytes successfully allocated from an `Arc<MemoryQuota>` and returns them on drop.

## Control Flow
`HeapSize` implementations compute capacity-based estimates; `Vec<T>` and `HashMap<K,V>` sample the first element/key-value pair to avoid O(n) deep scans. `MemoryQuota::alloc` first checks the current capacity and hard maximum, then atomically increments `in_use`; if a concurrent race pushes usage beyond capacity, it rolls the addition back and returns `MemoryQuotaExceeded`. `free` subtracts bytes and compensates if over-freeing would drive the counter negative. `alloc_force` bypasses capacity but still respects `MAX_MEMORY_ALLOC_SIZE`.

## State and Persistence Behavior
All quota state is in process memory through atomics. No durable persistence exists. `OwnedAllocated` couples state lifetime to Rust drop semantics, so leaking or forgetting the owner leaks quota accounting until process exit. Capacity can be changed dynamically with relaxed atomic stores.

## Dependencies and Integration Points
The file depends on `kvproto` protobuf structs for size estimates, `collections::HashMap`, crate-level `Either`, logging macros, and atomics. It is suitable for cache admission, request accounting, and components that need coarse memory pressure checks without allocator introspection.

## Risks
`vec_transmute` is unsafe and can cause undefined behavior if element layouts diverge. Heap-size estimates are approximate and can undercount shared protobuf bytes or heterogeneous collections. `used_ratio` divides by capacity and assumes capacity is not zero in callers. Relaxed atomics are adequate for approximate accounting but should not be treated as strict synchronization.

## Test Signals
Unit tests cover single-thread and multi-thread quota accounting, resize behavior, RAII release, force allocation, hard maximum behavior, and representative heap-size estimates for vectors, tuples, options, and hash maps.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/memory.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/metrics/allocator_metrics.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/metrics/allocator_metrics.rs

## Purpose
Registers a custom Prometheus collector for allocator-level and allocator-thread statistics exposed by `tikv_alloc`.

## Important APIs, Types, and Functions
- `monitor_allocator_stats(namespace)` creates and registers `AllocStatsCollector`.
- `AllocStatsCollector` owns descriptor lists and four metric families: allocator stats, per-arena thread stats, per-thread allocation counters, and arena count.
- `Collector::collect` refreshes metrics from `tikv_alloc::{fetch_stats,get_arena_count,iterate_arena_allocation_stats,iterate_thread_allocation_stats}`.

## Control Flow
Collector construction creates gauge vectors with a caller-provided namespace. Every Prometheus scrape calls `collect`, which fetches allocator global stats if available, sets arena count, iterates arena resident/mapped/retained values by thread name, iterates alloc/dealloc counters, then concatenates each metric family.

## State and Persistence Behavior
Collector state is process-local Prometheus metric state. Values are overwritten on each scrape from allocator snapshots; there is no persistent storage. Missing `fetch_stats` data is silently skipped while arena and thread allocation snapshots still run.

## Dependencies and Integration Points
Depends on `prometheus` collector APIs and `tikv_alloc` allocator instrumentation. It is re-exported by `metrics/mod.rs` and usually installed during TiKV metrics initialization.

## Risks
Metric labels use allocator-provided thread names, so cardinality and stale label values depend on allocator behavior. Registration can fail on duplicate metric names. Unsupported allocator stats produce partial output rather than a hard error.

## Test Signals
No local tests in this file; integration confidence comes from Prometheus collector semantics and allocator instrumentation consumers.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/metrics/allocator_metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/metrics/metrics_reader.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/metrics/metrics_reader.rs

## Purpose
Provides a small helper for reading the average value newly recorded into a Prometheus `Histogram` since the previous read.

## Important APIs, Types, and Functions
- `HistogramReader { histogram, sum, count }` stores a histogram handle and the last observed sum/count.
- `HistogramReader::new(histogram)` snapshots the initial sum and count.
- `read_latest_avg` returns `(new_sum - old_sum) / (new_count - old_count)` or `0.0` if no new samples arrived.

## Control Flow
Each read fetches current histogram sum and count. If count is unchanged, the previous baseline is retained and zero is returned. Otherwise the delta average is computed and the stored baseline is advanced.

## State and Persistence Behavior
State is local to the reader instance and reflects the last successful read. It does not persist across process restarts and does not reset the underlying histogram.

## Dependencies and Integration Points
Uses `prometheus::Histogram`. It is re-exported from `metrics/mod.rs` for components that want interval averages without separately tracking counters.

## Risks
The helper assumes histogram sum/count are monotonic. If the histogram is reset or replaced, deltas can become misleading. Concurrent observations are fine, but concurrent reads of the same `HistogramReader` require external synchronization.

## Test Signals
No direct unit tests; expected behavior is simple delta arithmetic over Prometheus histogram accessors.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/metrics/metrics_reader.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/metrics/mod.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/metrics/mod.rs

## Purpose
Aggregates TiKV utility metrics exports, conditionally selects platform process/thread collectors, provides Prometheus text dumping, defines shared counters/gauges, and converts internal maps to PD protobuf record pairs.

## Important APIs, Types, and Functions
- Conditional exports: Linux uses `threads_linux` and `process_linux`; other platforms use dummy modules.
- `monitor_allocator_stats`, `monitor_threads`, `monitor_process`, and `HistogramReader` are public metric entry points.
- `dump(should_simplify)` and `dump_to` gather and encode Prometheus metrics.
- Static metrics include `CRITICAL_ERROR`, `NON_TXN_COMMAND_THROTTLE_TIME_COUNTER_VEC`, its static auto-flush wrapper, and `INSTANCE_BACKEND_CPU_QUOTA`.
- `convert_record_pairs(HashMap<String,u64>)` produces `Vec<pdpb::RecordPair>`.

## Control Flow
`dump_to` gathers all Prometheus metric families. In full mode it encodes all families. In simplified mode it filters zero-valued counters and empty histograms before encoding, leaving other metric types untouched. Static metric declarations are registered through `lazy_static` when first accessed.

## State and Persistence Behavior
Metric state lives in the process-wide Prometheus registry. Dump output is a transient text snapshot. Static metrics persist for process lifetime once initialized.

## Dependencies and Integration Points
Depends on `prometheus`, `prometheus_static_metric`, `kvproto::pdpb`, platform-specific collectors, and allocator metrics. It is the central import point for TiKV components that need utility-level metrics.

## Risks
Duplicate metric registration can panic or return errors in submodules. Simplified dumping intentionally drops zero counters and empty histograms, so it is unsuitable for consumers that require full metric schemas. The typo in the comment does not affect behavior.

## Test Signals
`test_dump_metrics` registers counter, counter vec, histogram vec, and gauge metrics, checks full and simplified output are non-empty and duplicate-free, and verifies simplification reduces output until metrics receive samples.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/metrics/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/metrics/process_dummy.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/metrics/process_dummy.rs

## Purpose
Provides the non-Linux no-op implementation of process metrics registration so cross-platform builds keep the same public API.

## Important APIs, Types, and Functions
- `monitor_process() -> std::io::Result<()>` returns `Ok(())` and registers nothing.

## Control Flow
There is no runtime control flow beyond immediate success.

## State and Persistence Behavior
No state is created or persisted.

## Dependencies and Integration Points
Selected by `metrics/mod.rs` under `#[cfg(not(target_os = "linux"))]` and exported as `monitor_process`.

## Risks
Non-Linux builds compile and run, but process metrics are absent. Callers must not assume metrics registration implies metric availability across all platforms.

## Test Signals
No tests; behavior is intentionally trivial.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/metrics/process_dummy.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/metrics/process_linux.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/metrics/process_linux.rs

## Purpose
Implements a Linux Prometheus process collector focused on CPU, virtual memory, RSS, and start time while deliberately omitting file descriptor collection to avoid fragmentation with many open descriptors.

## Important APIs, Types, and Functions
- `monitor_process()` registers `ProcessCollector`.
- `ProcessCollector::new()` creates descriptors and initializes immutable process start time from `procfs::boot_time_secs` and `/proc/self/stat`.
- `Collector::collect` reads current process stat, updates memory gauges, advances CPU counter, and returns metric families.
- `PAGESIZE` caches `libc::sysconf(_SC_PAGESIZE)`.

## Control Flow
On construction, metric descriptors are built and process start time is set if boot time and process stat are available. During each scrape, `/proc/self/stat` is read through `procfs`; errors produce an empty vector. CPU total is converted from ticks to seconds, compared to the existing counter value, and the counter is incremented by the delta.

## State and Persistence Behavior
Prometheus metric objects retain previous CPU counter value and start time. Memory gauges are overwritten each scrape. No durable persistence exists.

## Dependencies and Integration Points
Depends on `procfs`, `prometheus`, `libc`, and `crate::sys::thread::ticks_per_second`. It is selected only for Linux by `metrics/mod.rs`.

## Risks
The CPU counter update assumes monotonic process CPU time and that `total >= past`; abnormal resets could underflow. RSS uses page count times page size. `/proc` read failures silently suppress all process metrics for that scrape.

## Test Signals
No local tests; coverage is indirect through metrics registration and Linux process stat assumptions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/metrics/process_linux.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/metrics/threads_dummy.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/metrics/threads_dummy.rs

## Purpose
Provides no-op non-Linux thread metrics and thread-info statistics so the utility API remains portable.

## Important APIs, Types, and Functions
- `monitor_threads(namespace)` returns `Ok(())`.
- `ThreadInfoStatistics::{new,record,get_cpu_usages,get_read_io_rates,get_write_io_rates}` are stubs returning empty maps.
- `Default` delegates to `new`.

## Control Flow
Methods perform no sampling and return immediately.

## State and Persistence Behavior
`ThreadInfoStatistics` has no fields and no persistent state.

## Dependencies and Integration Points
Selected by `metrics/mod.rs` on non-Linux targets and keeps callers source-compatible with Linux builds.

## Risks
Feature parity is intentionally absent. Components using thread CPU/IO maps must tolerate empty results on non-Linux systems.

## Test Signals
No tests; the primary signal is successful non-Linux compilation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/metrics/threads_dummy.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/metrics/threads_linux.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/metrics/threads_linux.rs

## Purpose
Collects Linux per-thread Prometheus metrics and provides sampled per-thread CPU/read/write rate aggregation by thread name.

## Important APIs, Types, and Functions
- `monitor_threads(namespace)` registers `ThreadsCollector` for the current process.
- `Metrics` owns gauge vectors for per-thread CPU totals, IO totals, thread states, and voluntary/nonvoluntary context switches.
- `ThreadsCollector` synchronously scrapes thread IDs, `/proc/<pid>/task/<tid>/stat`, IO, and status.
- `ThreadInfoStatistics` records interval CPU and IO rates by thread command/name.
- `TidRetriever` caches thread ID lists and backs off refresh interval from 15 seconds to 10 minutes when unchanged.
- Helpers include `sanitize_thread_name`, `state_to_str`, `collect_metrics_by_name`, and `update_metric`.

## Control Flow
Prometheus collection locks the metric set and TID retriever. If the TID list changes, all metric vectors are reset to avoid stale labels. For each thread, it reads full stat, resolves a sanitized name from `THREAD_NAME_HASHMAP` when available or `/proc` command otherwise, sets CPU total, increments state count, and optionally sets IO and context-switch metrics.
`ThreadInfoStatistics::record` computes elapsed wall time, clears rate maps, refreshes TIDs, reads totals, and converts positive deltas into per-second rates. CPU deltas are pre-multiplied by 100 so results are percentages.

## State and Persistence Behavior
Prometheus collector state persists per registered collector and is refreshed on scrape. `ThreadInfoStatistics` stores last instant, known TID names, previous totals, and current rates in memory. TID caching is adaptive and process-local.

## Dependencies and Integration Points
Depends on `procinfo`, `prometheus`, `crate::sys::thread` for IDs/stats/name map, and `crate::time::Instant`. It integrates with thread wrapper hooks that populate `THREAD_NAME_HASHMAP`.

## Risks
Frequent TID scanning can fragment memory, so caching is deliberate but can delay visibility of short-lived threads. Metrics label cardinality tracks thread names and IDs. `thread::thread_ids(pid).unwrap()` in `TidRetriever` can panic if `/proc` access fails. Rate computation ignores zero/negative deltas, so resets can leave stale previous totals.

## Test Signals
Tests cover thread IO visibility, IO rate accumulation, high-CPU percentage sampling, thread-name sanitization, and collector smoke registration/collection.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/metrics/threads_linux.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/mpsc/future.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/mpsc/future.rs

## Purpose
Implements an async-aware MPSC channel whose receiver is a `futures::Stream`, with bounded/unbounded queues, configurable wake policy, timeout receive, and batch-stream adaptation.

## Important APIs, Types, and Functions
- `WakePolicy::{Immediately,TillReach(usize)}` controls when senders wake the receiver.
- `Sender<T>::send` and `send_with` push into the queue and wake according to policy.
- `Receiver<T>` implements `Stream<Item=T>`, plus `try_recv` and `recv_timeout`.
- `unbounded(policy)` and `bounded(cap, policy)` construct channels.
- `BatchReceiver<T,I,C>` wraps a receiver and emits collected batches up to `max_batch_size`.

## Control Flow
The channel stores a raw pointer to a heap-allocated `Queue<T>`, with a bitfield-like `liveness` counter tracking sender and receiver presence. Sending first checks receiver liveness, pushes into `SegQueue` or `ArrayQueue`, then wakes immediately or once queue length reaches a threshold. The receiver polls by popping first, registering its waker if empty, retrying to avoid lost wakeups, and returning `None` when no senders remain.

## State and Persistence Behavior
State is entirely in memory: queue contents, `AtomicWaker`, and liveness counter. The heap queue is manually freed when the last sender/receiver side drops. `BatchReceiver` owns its receiver and collector closures.

## Dependencies and Integration Points
Uses `crossbeam::queue::{SegQueue,ArrayQueue}`, `futures::{Stream,AtomicWaker}`, and `crate::future::block_on_timeout`. It complements the synchronous MPSC wrapper in `mpsc/mod.rs`.

## Risks
Raw-pointer lifetime management and manual liveness arithmetic are the main safety risks. `WakePolicy::TillReach` improves batching but can delay messages until a threshold or disconnect wake. Bounded sends fail if the `ArrayQueue` is full, and wake is currently attempted even when push fails.

## Test Signals
Tests cover threshold wake behavior, immediate wake behavior, batch collection, sender/receiver wake transitions on disconnect, drop semantics for queued values, and bounded queue overflow.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/mpsc/future.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/mpsc/mod.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/mpsc/mod.rs

## Purpose
Wraps `crossbeam_channel` to add explicit sender-side close detection and a loose bounded sender variant for high-throughput paths that can tolerate approximate capacity enforcement.

## Important APIs, Types, and Functions
- Public submodules: `future` and `priority_queue`.
- `Sender<T>` wraps `crossbeam::Sender<T>` with shared `State { sender_cnt, connected }`.
- `Receiver<T>` wraps `crossbeam::Receiver<T>`.
- `unbounded`, `bounded`, and `loose_bounded` constructors mirror channel styles.
- `LooseBoundedSender<T>` supports `try_send`, `force_send`, `close_sender`, and connection checks.

## Control Flow
Cloning a sender increments `sender_cnt`; dropping decrements it and closes the sender side when the last sender is dropped. `Sender::send` and `try_send` check `connected` before delegating to crossbeam. Dropping the receiver stores `connected=false`, causing future sends to return disconnected. `LooseBoundedSender::try_send` only checks `len() < limit` every `CHECK_INTERVAL` attempts, using a failpoint to override the interval in tests.

## State and Persistence Behavior
State is process-local channel state. The close flag is separate from crossbeam's own disconnection and allows sender-side early rejection after explicit close or receiver drop.

## Dependencies and Integration Points
Depends on `crossbeam::channel`, atomics, `fail` failpoints, and local async/priority channel submodules. It is a common utility for internal worker queues.

## Risks
Closing a sender does not wake a receiver blocked on `recv`; comments note this is a deliberate performance tradeoff. Loose bounding can temporarily exceed the configured limit and uses `len()` as an approximate concurrent signal. `sender_cnt` uses `AtomicIsize`; misuse outside clone/drop invariants would be unsafe logically.

## Test Signals
Tests cover bounded/unbounded send/receive/disconnect/timeouts, explicit close behavior, zero-capacity blocking, loose-bound overflow, force sends, failpoint-driven capacity checks, and receiver drop handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/mpsc/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/mpsc/priority_queue.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/mpsc/priority_queue.rs

## Purpose
Implements an unbounded priority-based multi-producer/multi-consumer channel where lower `u64` priority values are received first and equal priorities preserve FIFO through a sequence number.

## Important APIs, Types, and Functions
- `unbounded<T: Send>()` returns `Sender<T>` and `Receiver<T>`.
- `PriorityQueue<T>` stores a `SkipMap<MapKey, Cell<T>>`, sequence counter, sender count, and receiver count.
- `MapKey { priority, sequence }` gives sorted ordering.
- `Sender::{send,try_send}` insert values and unpark receivers.
- `Receiver::{try_recv,recv}` pop the front entry, spin briefly, then park with `parking_lot_core`.

## Control Flow
Senders reject messages when no receivers remain, insert a boxed value in a `Cell`, and unpark one waiter using the queue address. Receivers pop the lowest key from the skip map; if empty and all senders are gone they report disconnection, otherwise they spin and then park until a sender unparks or disconnection wakes all waiters. Dropping the last sender calls `unpark_all`.

## State and Persistence Behavior
All queue state is in memory. `Cell` uses an atomic pointer and `take` to move values out exactly once; its drop path releases any unconsumed value. Sender/receiver counts are atomics tied to clone/drop.

## Dependencies and Integration Points
Uses `crossbeam_skiplist::SkipMap`, `parking_lot_core` park/unpark primitives, and crossbeam channel error types for API compatibility. It is exposed as `mpsc::priority_queue`.

## Risks
The implementation relies on raw pointers in `Cell` and correct single-take semantics. `SeqCst` is used for value pointer swaps and disconnection checks, but queue length in the park validation closure is still a race-prone condition handled by the park API. Unbounded storage can grow without backpressure.

## Test Signals
Tests validate priority ordering, FIFO under equal priority via sequence, send errors after receiver drop, disconnect after sender drop, blocking receive wakeup, draining after sender drop, and multi-threaded producer/consumer sum preservation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/mpsc/priority_queue.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/quota_limiter.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/quota_limiter.rs

## Purpose
Implements foreground/background throttling for CPU time, read/write bandwidth, and background IOPS so TiKV tasks can trade completion latency for stable resource usage.

## Important APIs, Types, and Functions
- `LimiterItems` bundles CPU, write bandwidth, read bandwidth, and IOPS `Limiter`s.
- `QuotaLimiter::new` builds separate foreground/background limiters and stores max delay plus auto-tune flag.
- `Sample` accumulates read bytes, write bytes, CPU time, IOPS, and CPU-limit enablement.
- `Sample::observe_cpu` and `observe_cpu_async` measure thread CPU time with `cpu_time::ThreadTime`.
- `QuotaLimiter::consume_sample` consumes a sample asynchronously and delays via `GLOBAL_TIMER_HANDLE`.
- `QuotaLimitConfigManager` applies online config changes.

## Control Flow
Callers create a sample for foreground or background work, record resource usage as the task runs, then call `consume_sample`. The limiter computes independent delay durations for CPU microseconds, write bytes, read bytes, and IOPS. The chosen delay is the maximum of those durations, capped by `max_delay_duration` when nonzero, and awaited through the global timer. Online config dispatch mutates individual limiter speeds and flags.

## State and Persistence Behavior
Limiter buckets, consumed counters, max delay, and auto-tune flags are in memory. Atomic fields allow concurrent reads/updates of config knobs. No throttling state persists beyond process lifetime.

## Dependencies and Integration Points
Depends on `crate::time::Limiter`, `GLOBAL_TIMER_HANDLE`, `ReadableDuration`, `ReadableSize`, `online_config::ConfigManager`, `cpu_time::ThreadTime`, and `futures` compatibility adapters. It integrates with runtime paths that can sample IO/CPU work units.

## Risks
CPU tracking measures thread CPU during guarded scopes or future polls, so uninstrumented work is invisible. `ThreadTime` is declared `Send` only through an unsafe wrapper because it is used within each poll. Max-delay capping can intentionally under-enforce configured rates. Config key names must match online config producers exactly.

## Test Signals
The unit test exercises foreground and background CPU, read/write bandwidth, max-delay capping, zero-as-unlimited behavior, dynamic limiter changes, IOPS-only limiting, and combined IOPS/read throttling.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/quota_limiter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/range_latch.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/range_latch.rs

## Purpose
Provides mutual exclusion for overlapping key ranges, currently aimed at avoiding concurrent RocksDB compaction-filter writes and ingest-SST operations over the same keyspace.

## Important APIs, Types, and Functions
- `RangeLatch` owns `Mutex<BTreeMap<Vec<u8>, (Arc<Mutex<()>>, (Vec<u8>, Vec<u8>))>>`.
- `RangeLatch::acquire(start_key, end_key)` blocks until no overlapping active range exists and returns `RangeLatchGuard`.
- `RangeLatchGuard` removes the active range entry on drop.

## Control Flow
Acquisition locks the range map, scans entries with start keys before the requested end key, filters true overlaps, and either inserts a new latch mutex or drops the map lock and waits on each overlapping range mutex. It loops until a conflict-free insert succeeds. The guard holds the range-specific mutex and removes its map entry when dropped.

## State and Persistence Behavior
Active latch state is in memory only. Ranges are keyed by start key and removed when guards drop. `ManuallyDrop` and lifetime transmute are used to ensure the mutex guard is dropped before the backing `Arc<Mutex<()>>` can be removed.

## Dependencies and Integration Points
Uses standard `BTreeMap`, `Mutex`, `Arc`, and range bounds. It integrates with RocksDB ingest/compaction-filter coordination where concurrency is low and range conflicts are rare.

## Risks
The code documents possible livelock under repeated conflicting acquisitions, though deadlock is avoided because threads wait on one range mutex at a time. Duplicate start keys are asserted absent; overlapping ranges with identical starts cannot coexist. The lifetime transmute is unsafe-adjacent and depends on drop ordering enforced manually.

## Test Signals
Tests cover non-overlapping single-thread ranges, several overlap shapes with blocking/unblocking behavior, and randomized concurrent range acquisition to assert no active overlaps.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/range_latch.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/resizable_threadpool.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/resizable_threadpool.rs

## Purpose
Implements a resizable Tokio runtime wrapper by replacing the entire runtime and draining old tracked tasks on a keeper runtime.

## Important APIs, Types, and Functions
- `DeamonRuntime` wraps `Option<Runtime>` plus `TaskTracker` and shuts down the runtime in `Drop`.
- `DeamonRuntimeHandle` is a weak handle that can `spawn` or `block_on` tracked tasks if the runtime is still alive.
- `ResizableRuntime` stores current size/version, thread prefix, keeper runtime, current runtime, construction callback, and post-adjust callback.
- `adjust_with(new_size)` creates a new runtime, swaps it in, and schedules old-runtime drain/drop.

## Control Flow
Construction creates a one-thread keeper runtime and the initial worker runtime. Spawns and block-ons go through a handle that briefly locks the current runtime to clone the Tokio handle and task tracker, then schedules the tracked future. Resizing increments a versioned thread-name suffix, builds a replacement runtime, swaps it under lock, updates size, and uses the keeper runtime to close and wait for the old tracker before dropping the old runtime.

## State and Persistence Behavior
Runtime state is process-local. Old runtimes remain alive until all tracked tasks complete; pending forever tasks prevent cleanup of that old runtime. Dropping `ResizableRuntime` drops current and keeper runtimes, and weak handles after drop log and ignore tasks.

## Dependencies and Integration Points
Depends on `tokio`, `tokio_util::task::TaskTracker`, `futures::Future`, and `crate::thread_name_prefix::RUNTIME_KEEPER_THREAD`. Callers supply the runtime-building policy and resize side-effect callback.

## Risks
The type name consistently uses `Deamon` rather than `Daemon`, which is cosmetic but public. Infinite or stuck tasks keep old runtimes alive after resize. `block_on` through stale handles may run on the runtime current at call time, not necessarily the runtime current when the handle was created.

## Test Signals
Tests cover resizing and cleanup after finite tasks, old-runtime retention for pending tasks, drop behavior with pending spawned/blocking tasks, and many concurrent handle operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/resizable_threadpool.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/resource_control.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/resource_control.rs

## Purpose
Encodes resource-control task metadata compactly and maps override priorities to TiKV task-priority classes.

## Important APIs, Types, and Functions
- `DEFAULT_RESOURCE_GROUP_NAME` is `"default"`.
- `TaskMetadata<'a>` wraps borrowed or owned bytes using `Cow`.
- `TaskMetadata::from_ctx` encodes non-default `ResourceControlContext` fields into a mask byte plus optional native-endian priority and group name bytes.
- `override_priority`, `group_name`, `to_vec`, and `deep_clone` decode or materialize metadata.
- `priority_from_task_meta` and `TaskPriority::{High,Medium,Low}` map resource priorities to scheduling classes.

## Control Flow
Encoding sets bit flags for nonzero override priority and non-default group name. Empty metadata means priority zero and group `"default"`. Decoding checks the mask, reads four bytes after the mask when priority exists, and computes the group-name offset from whether priority was present.

## State and Persistence Behavior
Metadata is byte-level in-memory state that can be owned or borrowed. It is not self-describing beyond the first-byte mask and is not versioned.

## Dependencies and Integration Points
Depends on `kvproto::kvrpcpb::ResourceControlContext` and `strum` enum helpers. It is likely carried with tasks/requests to scheduling and resource control queues.

## Risks
Priority is encoded with `to_ne_bytes`, so bytes are native-endian and should not be treated as portable wire data across architectures. Decoding assumes valid lengths and will panic on malformed metadata with a priority mask but fewer than five bytes. Debug assertion allows priorities up to 16 but release builds still map all larger values to `High`.

## Test Signals
Tests cover default and non-default group/priority encoding round-trips and priority mapping boundaries for low, medium, and high.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/resource_control.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/smoother.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/smoother.rs

## Purpose
Implements a generic fixed-capacity sliding-window smoother for recent numeric observations, including average, max, 90th percentile, and coarse trend detection.

## Important APIs, Types, and Functions
- `Trend::{Increasing,Decreasing,NoTrend}` reports trend direction.
- `Smoother<T, CAP, STALE_DUR, MIN_TIME_SPAN>` stores a `VecDeque<(T, Instant)>` and running `total`.
- `observe` and `observe_with_time` add records, enforce capacity, and remove stale records while keeping at least two records.
- Read methods include `get_count`, `get_recent`, `get_avg`, `get_max`, `get_percentile_90`, and `trend`.

## Control Flow
Adding a record evicts the oldest when capacity is full, updates the running total, pushes the new timestamped record, then removes stale front records beyond `STALE_DUR` as long as at least two records remain. Trend detection returns no trend for too few or stale records; otherwise it compares left/right averages by time split when `MIN_TIME_SPAN > 0`, or by count split when zero, using a tolerance of 2.0.

## State and Persistence Behavior
The smoother stores only in-memory recent observations and a running sum. It can be cloned when `T: Clone`, preserving the current window snapshot.

## Dependencies and Integration Points
Depends on `num_traits::{AsPrimitive,FromPrimitive}` and crate `time::Instant`. It is a reusable helper for flow/stat smoothing in higher-level components.

## Risks
`partial_cmp(...).unwrap()` will panic for non-orderable values such as `NaN` floats. `get_percentile_90` sorts a temporary vector and mutably borrows `self` despite not modifying fields. Running total depends on arithmetic traits and can overflow for integer `T` in release builds if callers choose unsuitable types/capacities.

## Test Signals
Tests cover average/recent/max/percentile behavior, capacity count, count-based trends, time-span-gated trends, increasing/decreasing/no-trend cases, and stale-record no-trend behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/smoother.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/store/mod.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/store/mod.rs

## Purpose
Defines the `store` utility module boundary and re-exports peer, query-stat, and region helper APIs under a single namespace.

## Important APIs, Types, and Functions
- Submodules: `peer`, `query_stats`, and `region`.
- Re-exports peer lookup/construction/removal helpers, `QueryStats` and `is_read_query`, and region range/store-membership helpers.

## Control Flow
There is no runtime control flow outside re-export wiring. Tests construct regions and peers to validate re-exported region membership helpers.

## State and Persistence Behavior
No module-level state is kept.

## Dependencies and Integration Points
Depends on submodules and `kvproto::metapb::Region` in tests. It is the import convenience layer for TiKV store-related utilities.

## Risks
API changes in submodules are exposed through this facade. Tests mostly cover region helpers, not every re-export.

## Test Signals
Tests validate `region_on_same_stores` across voter/learner/witness-like combinations and `region_on_stores` behavior with empty and non-empty target store lists.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/store/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/store/peer.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/store/peer.rs

## Purpose
Provides small helper functions for locating, mutating, removing, and constructing `kvproto::metapb::Peer` values inside a region.

## Important APIs, Types, and Functions
- `find_peer`, `find_peer_mut`, and `find_peer_by_id` search region peer lists.
- `remove_peer` removes the first peer with a matching store ID.
- Constructors include `new_peer`, `new_incoming_voter`, `new_learner_peer`, and `new_witness_peer`.
- `is_learner` checks `PeerRole::Learner`.

## Control Flow
Search helpers iterate the region peer vector. Constructors initialize default peers, set store ID, peer ID, role, and witness flag when needed. `remove_peer` finds a position then removes from `mut_peers`.

## State and Persistence Behavior
Functions mutate only the supplied `Region` or returned `Peer`; there is no global state.

## Dependencies and Integration Points
Depends on `kvproto::metapb::{Peer,PeerRole,Region}`. These helpers are re-exported by `store/mod.rs` and used in tests and region-manipulation code.

## Risks
`remove_peer` matches by store ID rather than peer ID, which is correct for many region operations but can surprise callers expecting peer-ID removal. Constructors do not set extra metadata beyond role/witness fields.

## Test Signals
The unit test checks voter/learner construction, learner detection, successful removal, idempotent missing removal, and post-removal lookup failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/store/peer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/store/query_stats.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/store/query_stats.rs

## Purpose
Wraps `pdpb::QueryStats` with arithmetic helpers for per-query-kind counters and read-query aggregation.

## Important APIs, Types, and Functions
- `QUERY_KINDS` lists supported kinds excluding `Others`.
- `QueryStats(pub pdpb::QueryStats)` derives debug/clone/default/partial-eq.
- `get_query_num`, `add_query_num`, `add_query_stats`, `sub_query_stats`, `fill_query_stats`, `get_read_query_num`, `pop`, and `get_all_query_num`.
- `is_read_query` classifies `Get`, `Coprocessor`, and `Scan`.

## Control Flow
Setter/getter methods use match arms over `QueryKind`. Aggregate operations iterate `QUERY_KINDS`. `pop` swaps the inner protobuf with a default value, returning the previous stats and resetting the wrapper.

## State and Persistence Behavior
State is the wrapped protobuf counters. Operations mutate in memory only. `sub_query_stats` uses unsigned subtraction and assumes the left operand is greater or equal for each kind.

## Dependencies and Integration Points
Depends on `kvproto::pdpb`. It is re-exported by `store/mod.rs` for PD reporting and store query-stat aggregation.

## Risks
Unsigned subtraction can underflow in release builds if callers subtract larger counters. `Others` is intentionally ignored in most operations. Adding counters can overflow `u64` if used without bounds over very long intervals.

## Test Signals
No local tests in this file; behavior is deterministic match/iteration logic. Store module tests do not cover query stats.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/store/query_stats.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/store/region.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/store/region.rs

## Purpose
Provides key-range membership and store-membership helpers for `kvproto::metapb::Region`.

## Important APIs, Types, and Functions
- `check_key_in_region_exclusive` checks `(start_key, end_key)`.
- `check_key_in_region_inclusive` checks `[start_key, end_key]`.
- `check_key_in_region` checks `[start_key, end_key)`.
- `region_on_same_stores` compares peer store IDs, roles, and witness flags between two regions.
- `region_on_stores` checks if a region has any peer on target stores, with empty target list meaning true.

## Control Flow
Range checks compare byte slices and treat an empty end key as unbounded. Store comparison first requires equal peer counts, then ensures every left peer has a right peer with matching store ID, role, and witness status. `region_on_stores` performs nested `any` checks.

## State and Persistence Behavior
All helpers are pure reads over supplied region values.

## Dependencies and Integration Points
Depends on `kvproto::metapb::Region`, re-exported by `store/mod.rs`, and used by region movement, placement, and validation logic.

## Risks
`region_on_same_stores` assumes at most one replica per store for the same region; duplicate peers could make equality semantics ambiguous. Boundary inclusivity differs across the three range helpers, so callers must choose carefully.

## Test Signals
Tests cover empty/unbounded ranges, boundary inclusion/exclusion, same-store comparisons with voter/learner/witness distinctions through store module tests, and target-store membership.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/store/region.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/stream.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/stream.rs

## Purpose
Provides stream and retry utilities for external IO paths: converting `AsyncRead` into a byte stream, blocking on Tokio-based external IO, exponential-backoff retry helpers, and timeout wrapping.

## Important APIs, Types, and Functions
- `AsyncReadAsSyncStreamOfBytes<R>` wraps an `AsyncRead` in a `Mutex` and reusable 2 MiB buffer, implementing `Stream<Item=io::Result<Bytes>>`.
- `error_stream` returns a one-item error stream.
- `block_on_external_io` creates a current-thread Tokio runtime and blocks on a future.
- `RetryError`, `RetryExt`, `JustRetry`, `retry`, `retry_all_ext`, `retry_ext`, and `retry_expr!` implement retry policy.
- `with_timeout` maps Tokio timeout expiry into a boxed error conversion.

## Control Flow
The read stream polls the inner reader into the reusable buffer and copies the read slice into `Bytes`; zero bytes ends the stream. Retry starts at a one-second delay, invokes optional failure hooks, checks retryability, caps attempts, sleeps with random 0-999 ms jitter, and doubles delay up to `max_retry_delay`. `retry_ext` also honors a `retry_count` failpoint override.

## State and Persistence Behavior
Stream state is the reader plus buffer. Retry state is local per call: attempt count, delay, extension hook, and max values. No persistent state exists.

## Dependencies and Integration Points
Depends on `bytes`, `futures`, `futures_util::io::AsyncRead`, `tokio`, `rand`, and `fail`. Intended for object storage/external file IO paths that need manual retry behavior.

## Risks
`block_on_external_io` must not be nested, as documented. The stream copies bytes out of the reusable buffer each poll. Retry macros evaluate the action expression multiple times and can hide capture subtleties; callers should prefer function forms where possible. `with_timeout` requires an `Unpin` future.

## Test Signals
Tests verify retry futures remain `Send` with a non-`Sync` output type and use a failpoint to confirm retry-count failure/success boundaries.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/stream.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/sys/cgroup.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/sys/cgroup.rs

## Purpose
Detects Linux cgroup v1/v2 limits for memory, CPU quota, and cpuset cores, including container mount-root path reconstruction from `/proc/self/mountinfo`.

## Important APIs, Types, and Functions
- `CGroupSys::new` reads `/proc/self/cgroup`, detects unified v2 mode via `statfs`, parses cgroup paths, and parses cgroup mount points.
- `memory_limit_in_bytes`, `cpuset_cores`, and `cpu_quota` read controller files and return optional/empty limits.
- Parsers include `parse_proc_cgroup_v1/v2`, `parse_mountinfos_v1/v2`, `build_path`, `parse_memory_max`, `parse_cpu_cores`, `parse_cpu_quota_v1/v2`, and `capping_parse_int`.

## Control Flow
Construction branches on v1/v2. v1 maps individual controllers such as `memory`, `cpuset`, and `cpu`; v2 uses the empty controller name. Limit queries look up the process cgroup path and mounted root, reconstruct an accessible absolute path, then read the appropriate controller file. Numeric parsing treats `"max"` or negative/unlimited values as no limit and caps integer overflow to type bounds where intended.

## State and Persistence Behavior
`CGroupSys` snapshots cgroup path and mount-point mappings at construction. Actual limit files are read when query methods run. No durable state is written.

## Dependencies and Integration Points
Depends on `procfs`, `libc::statfs`, filesystem reads, `num_traits::Bounded`, and `config::normalize_path`. `sys/mod.rs` keeps a lazy static `SELF_CGROUP` and also offers current re-read variants.

## Risks
Container mount layouts are complex; `build_path` can fail when cgroup paths do not align with mount roots. Missing mount points or file read errors return no limit/empty cpuset after logging. Parsing intentionally tolerates malformed values, which can hide configuration issues. The manual cgroup integration test requires privileged cgroup tools and is feature-gated.

## Test Signals
Tests cover default no-limit behavior, mountinfo parsing with and without cgroups, cgroup v1/v2 parsing, relative/conflicting mount roots, missing mountinfo, memory max parsing including overflow/malformed input, cpuset parsing, CPU quota parsing, cgroup paths containing colons, and a feature-gated live cgroup test.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/sys/cgroup.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/sys/cpu_time.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/sys/cpu_time.rs

## Purpose
Provides cross-platform process CPU time and system CPU tick snapshots, with Linux-style CPU fields and a `ProcessStat` interval CPU-usage helper.

## Important APIs, Types, and Functions
- `LinuxStyleCpuTime` stores user/nice/system/idle/iowait/irq/softirq/steal/guest/guest_nice ticks and computes `total`.
- `LinuxStyleCpuTime::current` delegates to platform implementation.
- `cpu_time()` returns process CPU `Duration`.
- `ProcessStat::{cur_proc_stat,cpu_usage}` tracks previous wall and CPU times to compute usage ratio.
- Platform implementations cover Linux/FreeBSD `/proc/stat` plus `clock_gettime`, macOS host/getrusage APIs, and Windows process time APIs.

## Control Flow
On Linux/FreeBSD, `current` reads the first `/proc/stat` line and parses CPU tick fields. `cpu_time` uses `CLOCK_PROCESS_CPUTIME_ID`. `ProcessStat::cpu_usage` reads new process CPU duration, swaps old state, measures elapsed real time, and returns CPU delta divided by real-time delta.

## State and Persistence Behavior
Only `ProcessStat` instances hold in-memory previous readings. There is no global state beyond platform calls.

## Dependencies and Integration Points
Uses `libc`, `derive_more::{Add,Sub}`, and Windows/macOS system APIs under cfg. `quota_limiter` uses thread CPU time from a separate crate, while this module supports process-level monitoring.

## Risks
Platform support is uneven; Windows `current` is unsupported. Linux `/proc/stat` parsing expects all fields present. Long-running high-core Windows conversion comments note potential overflow risk when converting to nanoseconds. The CPU usage test is timing-sensitive.

## Test Signals
`test_process_usage` sleeps to expect near-zero usage, then spawns busy loops and expects usage above 0.9; it is marked in comments as a test that should run alone.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/sys/cpu_time.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/sys/disk.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/sys/disk.rs

## Purpose
Maintains process-wide disk capacity/usage/reservation/status snapshots and exposes filesystem free-space stats.

## Important APIs, Types, and Functions
- Atomic setters/getters for disk capacity, used size, available size, reserved space, and raft reserved space.
- `set_disk_status` and `get_disk_status(store_id)` encode/decode `kvproto::disk_usage::DiskUsage`.
- `get_disk_space_stats(path)` returns total and available space via `fs2::statvfs`.

## Control Flow
Setters store values with release ordering; getters load with acquire ordering. `get_disk_status` first checks per-store failpoints for almost-full/already-full overrides, then maps the stored integer to the protobuf enum. Disk-space stats can be replaced by a failpoint-provided `capacity,available` pair.

## State and Persistence Behavior
All disk state is in static atomics for process lifetime. It represents the latest values set by monitors and is not persisted.

## Dependencies and Integration Points
Depends on `kvproto::disk_usage::DiskUsage`, `fail`, `fs2`, and `Path`. Store/raft monitoring code can set these values, while scheduling or health checks can read them.

## Risks
The status integer panics if corrupted to an unexpected value. Values are global, while failpoints allow store-specific status injection for stores 1 through 5. Stale values remain until updated by external monitor code.

## Test Signals
`sys/mod.rs` tests cover `get_disk_space_stats` for the current directory and an invalid path. Failpoints provide additional test hooks.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/sys/disk.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/sys/inspector.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/sys/inspector.rs

## Purpose
Defines a platform abstraction for inspecting current-thread IO and disk-device statistics, with a Linux `/proc` implementation and no-op fallback elsewhere.

## Important APIs, Types, and Functions
- `IoStat { read, write }` and `DiskStat` mirror process IO and diskstat fields.
- `ThreadInspector` trait exposes `io_stat`, `get_device`, and `disk_stat`.
- Linux `ThreadInspectorImpl` wraps `procfs::process::Process` rooted at `/proc/<pid>/task/<tid>`.
- Linux helpers convert `procfs::process::Io` and `procfs::DiskStat`, identify device major/minor with `fstat`, and scan `/proc/diskstats`.
- `self_thread_inspector()` constructs an inspector for the current thread.

## Control Flow
On Linux, current process/thread IDs are used to create a procfs `Process` rooted at the task directory. `io_stat` reads task IO counters. `get_device` opens a path and uses `fstat` to determine device major/minor. `disk_stat` reads and parses `/proc/diskstats`, returning the matching device entry.

## State and Persistence Behavior
Inspector instances hold a procfs process handle/root. Each stat query reads current kernel state. No persistent state is written.

## Dependencies and Integration Points
Depends on `procfs`, `libc`, and `crate::sys::thread`. The abstraction lets code collect backend IO and disk stats where supported while compiling elsewhere.

## Risks
Linux implementation relies on procfs format and permissions. `disk_stat` returns an error if any line parsing fails before a match, which can make malformed unrelated lines fatal. Device identification opens the target path and can fail for missing/inaccessible paths.

## Test Signals
Linux tests verify current-thread IO write delta after syncing a temporary file and confirm disk stats can be found for the current directory's device.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/sys/inspector.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/sys/ioload.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/sys/ioload.rs

## Purpose
Snapshots Linux block-device IO counters from `/sys/block/*/stat` into typed `IoLoad` structures.

## Important APIs, Types, and Functions
- `IoLoad` stores read/write IO counts, merges, sectors, ticks, in-flight, queue time, and optional discard counters.
- `IoLoad::snapshot()` returns a `HashMap<String, IoLoad>` on Unix; non-Unix returns an empty map in the cfg branch.

## Control Flow
The Unix snapshot walks `/sys/block/`, reads each `stat` file, parses whitespace-separated numbers into `f64`s with malformed values defaulting to zero, skips devices with fewer than 11 fields, and records optional discard fields when present.

## State and Persistence Behavior
The method returns a point-in-time map and stores no global state.

## Dependencies and Integration Points
Uses filesystem reads and `HashMap`. It is exported through `sys/mod.rs` for monitoring code that needs block-device load snapshots.

## Risks
Device names are inserted with `format!("{:?}", entry.file_name())`, which includes debug formatting rather than plain string conversion. Parse failures become zero values, potentially hiding malformed stats. The non-Unix signature references `NICLoad` in the unused cfg branch, which would matter only on non-Unix compilation.

## Test Signals
No local tests; expected behavior follows Linux block stat format documented in comments.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/sys/ioload.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/sys/mod.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/sys/mod.rs

## Purpose
Centralizes system utility exports and platform quota helpers: CPU/memory quotas, global memory usage/high-water checks, cache info, mount-point comparison, hostname, and submodules for disk/thread/IO inspection.

## Important APIs, Types, and Functions
- Public modules: `cpu_time`, `disk`, `inspector`, `ioload`, `thread`, and Linux-only `cgroup`.
- Re-exports selected `sysinfo` traits and defines `HIGH_PRI`.
- `SysQuota::{cpu_cores_quota,cpu_cores_quota_current,memory_limit_in_bytes,memory_limit_in_bytes_current,log_quota}` combines hardware, cgroup, and env-var limits.
- Global memory functions: `record_global_memory_usage`, `get_global_memory_usage`, `register_memory_usage_high_water`, `memory_usage_reaches_high_water`, and `memory_usage_reaches_near_high_water`.
- `cache_size`, `cache_line_size`, `path_in_diff_mount_point`, and `hostname`.

## Control Flow
Linux quota methods use a lazy `SELF_CGROUP` snapshot for stable quota and construct a fresh `CGroupSys` for current quota. CPU quota starts from `num_cpus`, then takes the minimum with cpuset and cgroup CPU quota, then applies `TIKV_CPU_CORES_QUOTA` if valid. Memory quota takes the minimum of sysinfo total memory and cgroup memory limit. Memory high-water checks compare the recorded RSS against either exact high water or a near-high-water margin: 90% below 10 GiB usage and fixed 1 GiB margin above.

## State and Persistence Behavior
Global memory usage and high-water mark are static atomics. The Linux cgroup snapshot is lazy static and can become stale if cgroup limits change; current variants re-read. No state is durable.

## Dependencies and Integration Points
Depends on `sysinfo`, `num_cpus`, `procinfo`, `page_size`, `fail`, `ReadableSize`, Linux cgroup helpers, and platform hostname APIs. Other modules and resource managers use these helpers for quota sizing and pressure checks.

## Risks
`record_global_memory_usage` unwraps `procinfo::pid::statm_self` on Linux. Environment quota parsing silently ignores invalid values. Mount-point detection parses `/proc/mounts` manually and returns false on errors, favoring non-disruptive behavior over strict detection.

## Test Signals
Tests cover hostname parity with the `hostname` command, mount-point difference behavior, mount parsing with spaces/tabs/comments, disk-space stats, and near-high-water threshold decisions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/sys/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/sys/thread.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/sys/thread.rs

## Purpose
Provides unified process/thread ID, thread CPU stat, thread priority, thread-name tracking, and thread-start/stop hook integration across standard threads, Tokio runtimes, and futures thread pools.

## Important APIs, Types, and Functions
- `ThreadStat { s_time, u_time }` and `total_cpu_time`.
- Platform exports from `imp`: `Pid`, `FullStat`, `ticks_per_second`, `process_id`, `thread_id`, `thread_ids`, `full_thread_stat`, `set_priority`, and `get_priority`.
- `thread_stat` and `current_thread_stat`.
- `StdThreadBuildWrapper::spawn_wrapper` and `ThreadBuildWrapper::{with_sys_and_custom_hooks,with_sys_hooks}`.
- Globals: `THREAD_NAME_HASHMAP` and `THREAD_START_HOOKS`.
- Hook helpers: `hook_thread_start`, `call_thread_start_hooks`, `add_thread_name_to_map`, `remove_thread_name_from_map`.

## Control Flow
Linux thread IDs come from cached process ID and thread-local `SYS_gettid`; thread lists read `/proc/<pid>/task`. Full stats use `procinfo::pid::stat_task`, and priority uses `setpriority/getpriority` after clearing errno for `getpriority`. Wrapped thread builders install common start hooks: call registered start hooks, add allocator memory accessor, allocate an exclusive arena, record thread name, run custom start hook, and on stop remove name/accessor plus custom end hook.

## State and Persistence Behavior
Thread-name and start-hook registries are process-global mutex-protected maps/vectors. Thread IDs are cached per thread on Linux. Allocator memory accessors are registered for thread lifetime and removed on stop. No durable state exists.

## Dependencies and Integration Points
Depends on `tikv_alloc` thread memory APIs, `collections::HashMap`, `defer`, `libc`/platform APIs, Tokio runtime builder hooks, futures `ThreadPoolBuilder`, and TiKV Yatp tests. Metrics code uses `THREAD_NAME_HASHMAP` to label per-thread metrics.

## Risks
The global hook vector grows monotonically; no unregister API exists. Builder wrappers must be used consistently or thread metrics/allocation tracking will be incomplete. Comments note a potential issue if a user only calls an after-start wrapper without before-stop cleanup in external APIs. Non-Linux implementations are best-effort stubs.

## Test Signals
Tests verify nonzero/different thread IDs, thread list membership while threads are alive and absence after stop, Linux priority set/get behavior with permission handling, and thread-name tracking across std thread wrapper, Yatp future pool, and Tokio builder hooks.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/sys/thread.rs -->
