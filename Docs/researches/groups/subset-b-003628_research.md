# Group Research: subset-b-003628

This grouped report covers i915 selftest source files under `sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/`. Each file section is bounded for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_gem_gtt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_gem_gtt.c

## Purpose
This file is the i915 GEM GTT selftest suite. It validates GPU virtual address-space behavior across mock GGTT, live GGTT, and per-process PPGTT address spaces. The main target is correctness of allocation, page-table population, hole walking, fixed-offset pinning, eviction, shrinker interaction, resource-backed VMA reservation/insertion, misalignment handling, and direct GGTT page insertion.

## Important APIs, Types, And Functions
- `i915_gem_gtt_mock_selftests()` builds a mock GEM device, assigns and initializes a mock GGTT, then runs mock subtests.
- `i915_gem_gtt_live_selftests()` runs live PPGTT/GGTT subtests through `i915_live_subtests()`.
- `fake_dma_object()`, `fake_get_pages()`, `fake_put_pages()`, and `fake_ops` provide synthetic GEM objects with preallocated scatterlists so address-space tests can allocate very large objects without real backing content.
- Hole exercisers include `lowlevel_hole()`, `fill_hole()`, `walk_hole()`, `pot_hole()`, `drunk_hole()`, `shrink_hole()`, `shrink_boom()`, and `misaligned_pin()`.
- Wrappers `exercise_ppgtt()`, `exercise_ggtt()`, and `exercise_mock()` apply those exercisers to the desired VM.
- `reserve_gtt_with_resource()` and `insert_gtt_with_resource()` allocate `i915_vma_resource` metadata and call `i915_gem_gtt_reserve()` / `i915_gem_gtt_insert()`.

## Control Flow
The suite creates a target address space, identifies a hole range, then drives one of several placement patterns. Fixed-offset tests bind and unbind VMAs at exact offsets; random tests generate shuffled orders with `i915_random_order()`; power-of-two boundary tests straddle page-table boundaries; shrink tests enable fault injection on `vm->fault_attr`; misalignment tests iterate memory regions and compare expected VMA/node size expansion. GGTT testing sorts the `drm_mm` hole stack and restarts traversal after mutations to avoid stale hole iteration. Mock tests build a synthetic context VM and cap the range to system RAM.

## State And Persistence
State is intentionally transient: mock devices, contexts, fake GEM objects, VMAs, page-table stashes, `drm_mm_node`s, and runtime PM wakerefs are created only for each test and released before return. The file mutates `vm->fault_attr` for shrink fault injection and restores it to zero. It temporarily changes GGTT mappings through `insert_entries`, `insert_page`, and `clear_range`; cleanup drains freed GEM objects to prevent cross-test pollution. No persistent on-disk state exists.

## Dependencies And Integration Points
It depends on GEM object internals, PPGTT/GGTT VM methods, `drm_mm`, runtime PM, memory-region page-size rules, mock GEM/GTT setup, and selftest helpers (`i915_random`, `igt_flush_test`, `mock_context`). The live suite integrates with the driver selftest dispatcher via `i915_live_subtests`; the mock suite integrates via `i915_subtests`.

## Risks
These tests intentionally stress large address spaces and can hit allocation pressure; many allocation failures are treated as expected when they stem from test scale. Cleanup correctness is high risk because leaked pinned pages or bound VMAs would corrupt later selftests. Misaligned and shrinker cases rely on exact page-size and fault-injection behavior, so changes in memory-region alignment, GGTT page-size selection, or resource ownership can produce subtle false failures.

## Test Signals
Success is signaled by exact VMA placement, `drm_mm_node` allocation state, expected `-EINVAL`/`-ENOSPC` errors for invalid requests, no stale mappings after unbind, correct direct GGTT reads after `insert_page`, and clean mock/live subtest completion. Failures log detailed offsets, sizes, expected placements, and errnos.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_gem_gtt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_live_selftests.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_live_selftests.h

## Purpose
This header is the ordered live selftest registry for the i915 driver. It is included multiple times with different definitions of the `selftest(name, function)` macro to build enums, module parameters, and the runtime dispatch table in `i915_selftest.c`.

## Important APIs, Types, And Functions
It does not define callable functions itself. Its API is the macro list of `selftest()` entries, including live suites for uncore, workarounds, GT engines/timelines/contexts/LRC/MOCS/PM/heartbeat/TLB, requests, migrate, active objects, GEM object/mman/dmabuf/VMA/coherency/GTT/evict/hugepage/context/client/migrate tests, reset, memory regions, hangcheck, execlists, ring submission, perf, SLPC, GuC, and late GT PM.

## Control Flow
Consumers include this file after defining `selftest`. `i915_selftest.c` uses it to generate an enum, a `live_selftests[]` table, and per-test module parameters with line-numbered names. Execution order is exactly the textual order. `sanitycheck` is kept first as a self-check and `late_gt_pm` is kept last.

## State And Persistence
The header itself holds no mutable state. Its entries become mutable `enabled` flags in `live_selftests[]` and module parameters once expanded by `i915_selftest.c`.

## Dependencies And Integration Points
Every listed function must be linked into the i915 selftest build and match the live signature `int (*)(struct drm_i915_private *)`. It is tightly coupled to the selftest runner’s macro-inclusion pattern and module parameter naming.

## Risks
Ordering is behavior: moving entries can alter hardware state expectations. Names must remain unique C identifiers. Adding a function with the wrong signature or missing conditional compilation breaks the generated dispatch table.

## Test Signals
The signal is indirect: `i915_live_selftests()` prints and invokes entries from this registry, respecting module parameters and filters. A missing or misordered entry manifests as absent live coverage or a build/link failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_live_selftests.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_mock_selftests.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_mock_selftests.h

## Purpose
This header is the ordered mock selftest registry for i915. It lists unit-style selftests that can run against mock hardware before or without normal live device operation.

## Important APIs, Types, And Functions
The file exposes a macro list only. Entries include sanity check, shmem utilities, software fence, scatterlist, syncmap, uncore, ring, engine, timelines, requests, objects, physical GEM, dmabuf, VMA, eviction, GTT, hugepages, and memory-region mock suites.

## Control Flow
`i915_selftest.c` repeatedly includes this header with macro definitions that generate enum constants, the `mock_selftests[]` dispatch table, and module parameters. The textual ordering controls execution order through `run_selftests(mock, NULL)`.

## State And Persistence
No state is stored in the header. Expanded entries become `struct selftest` records with mutable `enabled` flags in the compiled runner.

## Dependencies And Integration Points
Each listed function must have signature `int function(void)`. The file is part of the selftest macro contract and therefore cannot include normal include guards around the list expansion beyond the fallback `selftest` definition.

## Risks
Name collisions break enum/table generation. Reordering can hide dependencies between mock setup and later tests. Adding live-only behavior here would violate the no-hardware mock execution path.

## Test Signals
The generated mock runner prints the selected test name and stops on the first nonzero error. Build failures or absent module parameters are the primary signals of registry misuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_mock_selftests.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_perf.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_perf.c

## Purpose
This file tests the i915 perf/OA stream setup and NOA wait batch behavior. It verifies that a minimal OA metric configuration can be registered, opened as a perf stream, used to execute the NOA wait delay, and that the generated wait sequence preserves user GPR and scratch state.

## Important APIs, Types, And Functions
- `alloc_empty_config()`, `destroy_empty_config()`, and `get_empty_config()` manage a temporary `i915_oa_config` in `perf->metrics_idr`.
- `test_stream()` creates an `i915_perf_stream` using render engine OA properties and calls `i915_oa_stream_init()`.
- `stream_destroy()` tears the stream down under `gt->perf.lock`.
- `live_sanitycheck()` checks stream creation/destruction.
- `write_timestamp()` emits a `PIPE_CONTROL` timestamp write into the engine status page.
- `live_noa_delay()` measures timestamp deltas around `stream->noa_wait`.
- `live_noa_gpr()` poisons context scratch, loads GPR registers with `STACK_MAGIC`, executes the NOA wait batch, stores GPRs back, and verifies no clobbering.
- `i915_perf_live_selftests()` owns registration, execution, and cleanup of the temporary OA config.

## Control Flow
The live entry first skips if perf metrics are unavailable or the GT is wedged. It allocates the empty config, runs `live_sanitycheck`, `live_noa_delay`, and `live_noa_gpr`, then removes the config. The delay test constructs a kernel request, writes timestamps before and after dispatching the secure NOA wait batch, polls status-page slots from the CPU, and checks GPU clock-derived duration against the expected programming delay. The GPR test creates a user context request, initializes 32 GPR dwords, dispatches `noa_wait`, stores all GPR values into the global HWSP, waits for completion, and inspects both GPR storage and scratch-page poison.

## State And Persistence
The file temporarily mutates `perf->metrics_idr`, OA config references, stream state, engine status-page slots, GPR registers during a request, and context scratch memory. It restores by destroying the stream and unregistering the OA config. No persistent metric set survives a normal run.

## Dependencies And Integration Points
It depends on perf/OA internals, render engine lookup, OA format selection by graphics version, request/ring emission, status-page access, `i915_live_subtests()`, `igt_hexdump()`, and secure batch dispatch. It integrates with the live selftest registry through `perf` in `i915_live_selftests.h`.

## Risks
OA stream locking and config reference handling are important; failure paths must release configs and stream allocations. Timing thresholds can be sensitive to hardware clock conversion and polling latency. The GPR test intentionally touches low-level registers and scratch pages, so incorrect addressing can corrupt context state or produce difficult hardware failures.

## Test Signals
Failures include inability to create stream/config, delay outside the accepted threshold, request timeout that wedges the GT, GPR value mismatch, or scratch page poison corruption. Success confirms the OA stream can open and the NOA wait helper behaves as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_perf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_perf_selftests.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_perf_selftests.h

## Purpose
This header is the ordered registry for performance-oriented i915 selftests. It is macro-expanded by the selftest runner to generate perf test enums, module parameters, and dispatch records.

## Important APIs, Types, And Functions
The macro list registers `engine_cs`, `request`, `migrate`, and `region` performance suites. It defines no runtime functions itself.

## Control Flow
`i915_selftest.c` includes the file with `selftest()` defined to produce `perf_selftests[]`. `i915_perf_selftests()` then runs selected entries in order when `perf_selftests` are enabled.

## State And Persistence
No intrinsic state exists. Expanded records carry per-test `enabled` flags controlled by module parameters.

## Dependencies And Integration Points
Each listed function must match `int (*)(struct drm_i915_private *)`. This registry connects low-level perf suites, including request and memory-region perf tests in this subset, to the global i915 selftest module parameters.

## Risks
Perf tests can be longer-running and hardware-sensitive; adding them here exposes them to the perf selftest lane. Name uniqueness and signature correctness are required.

## Test Signals
Signals are generated by the central perf runner: selected test names are logged, failures stop the perf suite, and disabled entries are skipped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_perf_selftests.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_random.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_random.c

## Purpose
This file provides deterministic pseudo-random helpers used by many i915 selftests. It centralizes 64-bit random generation, array shuffling, random order allocation, and aligned random offset selection using the global selftest seed.

## Important APIs, Types, And Functions
- `i915_prandom_u64_state()` combines two 32-bit PRNG draws.
- `i915_prandom_shuffle()` implements Fisher-Yates shuffle for small element sizes.
- `i915_random_reorder()` shuffles an array of unsigned indices.
- `i915_random_order()` allocates and shuffles an index array from `0..count-1`.
- `igt_random_offset()` chooses an aligned address in `[start, end)` that can contain `len`.

## Control Flow
Callers create an `rnd_state` with macros from `i915_random.h`, then request shuffled order or offsets. `i915_random_order()` fills the array sequentially, shuffles it, and returns ownership to the caller. `igt_random_offset()` validates the requested range with `BUG_ON`, computes the aligned range, uses modulo reduction on a 64-bit random number, and returns the rounded-up aligned result.

## State And Persistence
No global state is mutated directly. Determinism is controlled by the caller-provided `struct rnd_state`, usually seeded from `i915_selftest.random_seed`. Allocated order arrays are caller-owned.

## Dependencies And Integration Points
It depends on Linux PRNG helpers, allocation APIs, math64 helpers, and i915 utility overflow checks. It is used by GTT, request, memory-region, VMA, and syncmap selftests for reproducible randomized stress paths.

## Risks
`i915_prandom_shuffle()` refuses elements larger than its 128-byte stack buffer and warns on oversized count. `igt_random_offset()` assumes valid non-overflowing ranges and will `BUG_ON` invalid inputs, so callers must pre-check size/alignment.

## Test Signals
The helper itself has no selftest entry. Its signals appear in dependent randomized tests: repeatability from a logged seed, shuffled coverage of holes/engines/objects, and deterministic reproduction of failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_random.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_random.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_random.h

## Purpose
This header declares and seeds the pseudo-random helper API for i915 selftests. It gives tests a uniform way to use the global `i915_selftest.random_seed` while allowing nested deterministic substates.

## Important APIs, Types, And Functions
- `I915_RND_STATE_INITIALIZER(seed)` initializes `struct rnd_state`.
- `I915_RND_STATE(name)` seeds a state from `i915_selftest.random_seed`.
- `I915_RND_SUBSTATE(name, parent)` derives a child state from a parent PRNG.
- `i915_prandom_u32_max_state()` scales a 32-bit draw to `[0, ep_ro)`.
- Declarations cover `i915_prandom_u64_state`, random order/reorder/shuffle, and `igt_random_offset`.

## Control Flow
Most tests instantiate a local `I915_RND_STATE(prng)` at entry. Loops then call helpers to shuffle placement order or select random offsets. Substates let nested loops reproduce inner random choices while advancing outer choices deterministically.

## State And Persistence
The header does not store state; it defines stack-local PRNG initialization patterns. Persistent reproducibility comes from the global module parameter `st_random_seed` in `i915_selftest.c`.

## Dependencies And Integration Points
It includes Linux `prandom`, `math64`, and `../i915_selftest.h`. It is shared by most stress-oriented selftests in this subset.

## Risks
Changing the scaling helper or seed macros changes reproducibility of existing failures. `i915_prandom_u32_max_state()` assumes callers handle zero/invalid upper bounds appropriately.

## Test Signals
The logged global seed from `__run_selftests()` is the key diagnostic signal. Tests that fail after randomized ordering can be rerun with the same seed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_random.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_request.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_request.c

## Purpose
This file is the main request selftest suite. It validates mock request lifecycle and fence waiting, live request submission across engines, cancellation and reset behavior, breadcrumb signaling under concurrency, and performance characteristics of request dispatch, context switching, preemption, completion, and multi-engine throughput.

## Important APIs, Types, And Functions
- Public entries are `i915_request_mock_selftests()`, `i915_request_live_selftests()`, and `i915_request_perf_selftests()`.
- Mock tests include `igt_add_request()`, `igt_wait_request()`, `igt_fence_wait()`, `igt_request_rewind()`, and `mock_breadcrumbs_smoketest()`.
- Live tests include `live_nop_request()`, `live_empty_request()`, `live_all_engines()`, `live_sequential_engines()`, `live_parallel_engines()`, `live_cancel_request()`, and `live_breadcrumbs_smoketest()`.
- Cancellation helpers cover inactive, active, completed, and reset-backed non-preemptable requests.
- Perf helpers include timestamp/semaphore command emitters, `measure_*()` latency probes, `perf_request_latency()`, `perf_series_engines()`, and `perf_parallel_engines()`.
- Structs `smoketest`, `smoke_thread`, `parallel_thread`, `perf_stats`, `perf_series`, and `p_thread` hold per-run concurrency and measurement state.

## Control Flow
Mock tests create a mock GEM device, acquire runtime PM, and run basic request/fence scenarios. Breadcrumb smoke tests spawn kthread workers that allocate batches of requests across many contexts, gate submission through software fences, await DMA fences, and verify all request fences are signaled. Live tests iterate UABI engines, use `igt_live_test_begin/end` to enforce idle/reset invariants, create empty or recursive batches, submit requests concurrently or sequentially, and resolve recursive batches to let GPU execution finish. Cancellation tests use `igt_spinner` to create inactive/active/completed/hung requests and check fence errors and follow-up request progress. Perf tests pin contexts, disable heartbeats, pin RPS frequency, emit status-page timestamp commands, compute filtered cycle deltas, and print throughput/busy/runtime summaries.

## State And Persistence
The suite creates contexts, requests, fences, batches, VMAs, kthread workers, runtime PM wakerefs, QoS requests, and temporary engine property changes. State is expected to be fully released after each test. Some failure paths wedge the GT intentionally to avoid continued execution on corrupted or hung hardware. Perf tests temporarily disable c-states, heartbeat, and force high GPU frequency.

## Dependencies And Integration Points
The file depends on request, engine, context, ring, breadcrumb, scheduler, software fence, live-test, spinner, flush, mock GEM, runtime PM, and GT clock APIs. It integrates with all three selftest lanes: mock, live, and perf registries. It also relies on `i915_random` for randomized context/order coverage.

## Risks
This is high-blast-radius test code because it manipulates real engine queues, heartbeats, resets, and low-level ring commands. Kthread synchronization and reference handling must be exact to avoid leaked requests or dangling fences. Timing tests are sensitive to hardware generation, clock conversion, CPU latency, and engine wedging. Cancellation/reset tests intentionally exercise paths that can hang the GPU if arbitration or reset behavior regresses.

## Test Signals
Correctness signals include expected wait timeouts before submission, successful waits after submission, fence signaled bits, request completion state, preserved ordering across engines, cancelled fence error `-EINTR`, no unexpected GPU reset inside live sections, and clean flush after cancellation. Perf signals are printed latency, busy, runtime, and count summaries; fatal measurement failures wedge the GT and return errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_request.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_selftest.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_selftest.c

## Purpose
This file is the central i915 selftest runner. It expands mock, live, and perf registries into dispatch tables and module parameters, manages global selftest seed/timeout/filter state, runs selected tests, provides subtest setup/teardown helpers, and supplies diagnostics such as timeout checks and hex dumps.

## Important APIs, Types, And Functions
- Global `struct i915_selftest i915_selftest` stores timeout, seed, filter, and lane enable flags.
- `i915_mock_selftests()`, `i915_live_selftests()`, and `i915_perf_selftests()` are lane entry points.
- `__run_selftests()` seeds randomness, computes timeout jiffies, enables all tests when none are explicitly enabled, logs configuration, and invokes table entries.
- `apply_subtest_filter()` parses `st_filter` tokens, including `caller/name` and `!` exclusions.
- Setup/teardown helpers include `__i915_nop_setup`, `__i915_live_setup`, `__i915_live_teardown`, `__intel_gt_live_setup`, and `__intel_gt_live_teardown`.
- `__i915_subtests()` runs individual `struct i915_subtest` entries with filtering and setup/teardown.
- `__igt_timeout()` and `igt_hexdump()` are shared diagnostics.

## Control Flow
The file includes registry headers multiple times with different `selftest` macro definitions to create enum values, arrays, and module parameters. Lane entry points check whether their lane is enabled, wait for required GSC proxy/HuC flows for live/perf, then call `run_selftests()`. Subtest execution checks signals, applies filters, calls setup, runs the subtest, then calls teardown. Live teardown flushes GT state and drains freed GEM objects.

## State And Persistence
Selftest state is module-parameter-backed and persists for the loaded module: `st_random_seed`, `st_timeout`, `st_filter`, and lane flags. Runtime state includes computed `timeout_jiffies`. Live execution temporarily disables render powergating on selected platforms and waits for firmware/component initialization. The runner records failure errnos into lane flags for later module-load behavior.

## Dependencies And Integration Points
It depends on i915 driver, GT PM, firmware proxy/HuC state, reset counters, flush helper, wait utilities, and all registry headers. It is the integration point between kernel module parameters and individual selftest files.

## Risks
Macro inclusion makes registry names/order fragile. Positive errors or `-ENOTTY` from tests conflict with runner magic values and are normalized. Filter parsing assumes allocation succeeds; an allocation failure would make string traversal unsafe only if not handled elsewhere. Live tests assume an idle system and can fail if firmware initialization or power management is still in progress.

## Test Signals
The runner logs seed, timeout, lane name, and each test/subtest name. Failures identify setup, subtest, or teardown stage. `__igt_timeout()` logs optional timeout context and respects pending signals. `igt_hexdump()` compresses repeated rows to keep diagnostic output readable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_selftest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_sw_fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_sw_fence.c

## Purpose
This file tests the i915 software fence primitive. It validates completion, dependency graphs, cycle detection, chains, many-to-one and one-to-many relationships, cross-workqueue signaling, timed fences, and wrapping of DMA fences with optional timeout behavior.

## Important APIs, Types, And Functions
- `alloc_fence()`, `free_fence()`, and `fence_notify()` create and destroy test fences while leaving memory ownership to the caller.
- Dependency tests include `test_self()`, `test_dag()`, `test_AB()`, `test_ABC()`, `test_AB_C()`, `test_C_AB()`, and `test_chain()`.
- `task_ipc` and `test_ipc()` validate use as an inter-thread synchronization primitive.
- `test_timer()` validates `timed_fence`.
- `alloc_dma_fence()`, `wrap_dma_fence()`, and `test_dma_fence()` test software fence waits on external DMA fences.
- `i915_sw_fence_mock_selftests()` registers all tests as mock subtests.

## Control Flow
Tests create fences, add await relationships with `i915_sw_fence_await_sw_fence_gfp()` or `i915_sw_fence_await_dma_fence()`, commit fences in controlled order, and inspect `i915_sw_fence_done()`. DAG tests intentionally try recursive and cyclic dependencies when DAG checking is enabled. IPC queues a work item that waits on one fence, updates a value, and commits another. Timer and DMA tests wait for delayed completion and then verify early/late signaling semantics.

## State And Persistence
All state is heap-allocated fence objects, DMA fences, workqueue/work structs, and timed fence timers. State is transient and freed at the end of each test. DMA fence tests signal the DMA fence on all failure paths to unblock wrappers.

## Dependencies And Integration Points
It depends on the i915 software fence implementation, Linux DMA fences, workqueues, completions, timers/jiffies, and the selftest subtest runner. The mock request tests also rely on software fences, making this file foundational for higher-level request coverage.

## Risks
Reference and notification ordering are critical: freeing before dependency completion would corrupt waiters. Some timing checks tolerate oversleep by skipping late timeout validation. DAG checks are conditional on `CONFIG_DRM_I915_SW_FENCE_CHECK_DAG`, so cycle coverage can be absent in some builds.

## Test Signals
Expected signals are early-not-done and later-done states, cycle insertion returning `-EINVAL`, ordered propagation through chains, worker value update only after input fence commit, timer not firing before target jiffies, and DMA timeout/non-timeout wrappers completing at the right events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_sw_fence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_syncmap.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_syncmap.c

## Purpose
This file tests `i915_syncmap`, a compressed radix-style map from 64-bit context IDs to sequence numbers. It validates initialization, single-leaf insertion, tree growth above and below existing leaves, neighbour packing, branch compaction, random insertion, and sequence-number freshness checks.

## Important APIs, Types, And Functions
- `i915_syncmap_mock_selftests()` registers the suite.
- `i915_syncmap_print_to_buf()` and `dump_syncmap()` format the internal tree for failure diagnostics.
- `check_syncmap_free()`, `check_seqno()`, `check_one()`, and `check_leaf()` are invariant helpers.
- Test functions are `igt_syncmap_init()`, `igt_syncmap_one()`, `igt_syncmap_join_above()`, `igt_syncmap_join_below()`, `igt_syncmap_neighbours()`, `igt_syncmap_compact()`, and `igt_syncmap_random()`.

## Control Flow
Each test initializes a syncmap pointer, performs controlled `i915_syncmap_set()` insertions, checks returned leaf/parent topology, and uses `i915_syncmap_is_later()` to validate lookups. Join-above tests insert IDs with shrinking common prefixes. Join-below and compaction tests force branch replacement and skipped single-child branch behavior. Random tests first populate random contexts for a short phase, then replay a deterministic context stream across changing seqnos and compare expected `seqno_later()` outcomes.

## State And Persistence
The syncmap tree is heap-backed and transient. Tests mutate `*sync` as insertions may return the active leaf, not always the root; diagnostic printing climbs to the root through `parent` links. Every path calls `i915_syncmap_free()` and verifies the pointer is cleared.

## Dependencies And Integration Points
It depends on the internal syncmap layout (`height`, `prefix`, `bitmap`, `__sync_child`, `__sync_seqno`, `KSYNCMAP`, `SHIFT`, `MASK`) and selftest random helpers. It is registered in the mock selftest list.

## Risks
The tests inspect internal representation, so legitimate implementation changes to compression or layout require updates. Failure diagnostics allocate a page-sized buffer and may skip tree printing if allocation fails. Random tests depend on seed reproducibility.

## Test Signals
Signals include exact bitmap population, leaf height zero where expected, parent/child placement, root compaction shape, correct absence for neighbouring but uninserted IDs, correct seqno freshness results, and pointer clearing after free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_syncmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_vma.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_vma.c

## Purpose
This file tests VMA creation, lookup, pinning, GTT view remapping, rotated views, partial views, and live GGTT remapped IO behavior. It verifies both metadata identity and the scatterlist/page ordering generated for non-normal GTT views.

## Important APIs, Types, And Functions
- Public entries are `i915_vma_mock_selftests()` and `i915_vma_live_selftests()`.
- `checked_vma_instance()` wraps `i915_vma_instance()` and validates `i915_vma_compare()`.
- `igt_vma_create()` creates many objects and mock contexts, then checks VMA creation and lookup under pinned/unpinned states.
- `igt_vma_pin1()` exercises boundary cases for `i915_vma_pin()` flags and sizes.
- `assert_rotated()`, `assert_remapped()`, `rotated_index()`, `remapped_index()`, and `remapped_size()` validate view scatterlists.
- `igt_vma_rotate_remap()` tests rotated and remapped mock views with two planes.
- `igt_vma_partial()` validates partial GTT views and reuse.
- `igt_vma_remapped_gtt()` writes through live remapped/rotated GGTT mappings and verifies through the normal view.

## Control Flow
Mock setup creates a mock device and GGTT, then runs VMA subtests. Creation tests grow object/context counts by primes and use two passes to pin and unpin all VMA combinations. Pin tests iterate a table of expected valid, `-EINVAL`, and `-ENOSPC` cases. Remap tests enumerate many plane geometry combinations and prime offsets, pin view VMAs, inspect scatterlists, unbind, and reschedule. Partial tests build every prime-sized window within a 1021-page object, assert pages match source DMA addresses, and check object VMA list counts. Live tests use a mappable GGTT view, write coordinates through transformed views, then read expected coordinates from normal backing offsets.

## State And Persistence
State is transient GEM objects, mock contexts, VMAs, pinned mappings, and IO mappings. Mock setup initializes and tears down a GGTT. Live tests hold runtime PM while performing IO mapping. VMAs remain on object lists during an object lifetime but disappear when objects are released.

## Dependencies And Integration Points
It depends on GEM object internals, context VM lookup, GGTT pinning, VMA comparison, scatterlist iteration, transformed GTT view structures, runtime PM, and mock GTT setup. It integrates with mock and live registries under `vma`.

## Risks
The tests assert internal VMA list counts and scatterlist shapes, so changes in VMA caching or coalescing can require corresponding test updates. Live IO mapping depends on aperture availability and correct cache/domain transitions. Pin boundary cases encode assumptions about flag bits and mappable/total GGTT boundaries.

## Test Signals
Signals include correct VM/size/view type, `i915_vma_compare()` equality, expected pin errno, exact transformed DMA ordering, no use of original pages for transformed views, exact partial page mapping, unchanged VMA list counts after normal full-view lookup, and correct live readback through normal mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_vma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_atomic.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_atomic.c

## Purpose
This file defines reusable atomic-context phases for selftests that need to run code under preemption, softirq, or hardirq-disabled conditions.

## Important APIs, Types, And Functions
The exported object is `igt_atomic_phases[]`, an array of `struct igt_atomic_section`. Local helpers pair begin/end functions for `preempt_disable`/`preempt_enable`, `local_bh_disable`/`local_bh_enable`, and `local_irq_disable`/`local_irq_enable`.

## Control Flow
Consumers iterate `igt_atomic_phases` until the sentinel empty record. For each phase they call `critical_section_begin()`, execute the code under test, then call `critical_section_end()`.

## State And Persistence
The file stores only a constant table. Runtime state is the CPU’s preemption, bottom-half, or interrupt enable state while a phase is active.

## Dependencies And Integration Points
It depends on Linux preempt, bottom-half, and irq flag APIs, and on the declaration in `igt_atomic.h`. It is a helper for low-level selftests that validate behavior in atomic contexts.

## Risks
Callers must always pair begin/end or the CPU context will remain altered. Tests must avoid sleeping in phases where sleep is illegal.

## Test Signals
This file produces no direct test result; downstream tests report whether their operation is safe across these atomic phases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_atomic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_atomic.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_atomic.h

## Purpose
This header declares the atomic-context phase abstraction used by i915 selftests.

## Important APIs, Types, And Functions
It defines `struct igt_atomic_section` with a phase name and begin/end callbacks, and declares `extern const struct igt_atomic_section igt_atomic_phases[]`.

## Control Flow
Consumers include this header, iterate the exported table, and wrap test bodies with the callback pair for each phase.

## State And Persistence
The header stores no state. It exposes constant metadata and function pointers defined in `igt_atomic.c`.

## Dependencies And Integration Points
It has no heavy includes, making it easy to use in low-level selftest files. It integrates with the phase table implementation in `igt_atomic.c`.

## Risks
The abstraction does not enforce callback pairing; caller discipline is required.

## Test Signals
Signals are indirect through tests that iterate the phases and report phase-specific failures by `name`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_flush_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_flush_test.c

## Purpose
This file provides a shared live-test cleanup gate. It waits for all GTs to become idle after a test and wedges a GT if it does not flush, preventing later tests from running on suspect hardware state.

## Important APIs, Types, And Functions
The single exported function is `igt_flush_test(struct drm_i915_private *i915)`.

## Control Flow
The helper iterates every GT and every engine in each GT. It records the maximum engine preempt timeout, checks whether the GT is already wedged, then waits for GT idle for about twice the longest preempt timeout. On timeout, it logs the caller address, dumps GEM trace data, wedges the GT, and returns `-EIO`.

## State And Persistence
It reads engine properties and GT wedge state. On failure it persistently marks the GT wedged for the current driver lifetime. It does not allocate or retain memory.

## Dependencies And Integration Points
It depends on `intel_gt_wait_for_idle()`, engine iteration, GT wedge APIs, and GEM tracing. It is used by live-test teardown, request cancellation, and other hardware selftests.

## Risks
The timeout is heuristic and tied to preemption properties. Too small a timeout causes false wedging; too large delays failure detection. Wedge state is intentionally severe and affects subsequent tests.

## Test Signals
Return `0` means all GTs idled. Return `-EIO` means existing wedge or idle timeout, with trace dump and caller symbol in logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_flush_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_flush_test.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_flush_test.h

## Purpose
This header declares the shared `igt_flush_test()` live-test cleanup helper.

## Important APIs, Types, And Functions
It forward-declares `struct drm_i915_private` and declares `int igt_flush_test(struct drm_i915_private *i915)`.

## Control Flow
Consumers call the function after live GPU operations, typically from teardown or explicit cleanup points.

## State And Persistence
The header has no state. The implementation may wedge a GT on timeout.

## Dependencies And Integration Points
It is intentionally lightweight and included by the central selftest runner and live helper files.

## Risks
The API exposes only an i915-wide flush, not per-GT/per-engine control, so callers must treat failure as broad hardware contamination.

## Test Signals
Callers interpret `0` as clean idle and `-EIO` as flush failure or wedge.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_flush_test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_live_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_live_test.c

## Purpose
This file provides begin/end guards for live hardware selftests. It ensures GTs are idle before a test and detects unexpected global or per-engine resets after the test.

## Important APIs, Types, And Functions
- `igt_live_test_begin()` stores the i915 pointer, function/name labels, baseline global reset count, and per-engine reset counts.
- `igt_live_test_end()` flushes the GPU, compares reset counters against the baseline, and reports unexpected reset activity.

## Control Flow
Begin iterates all GTs, waits indefinitely for idle, then records reset counts for each engine. End calls `igt_flush_test()`, checks global reset count, then checks every engine reset count. Any mismatch returns `-EIO`.

## State And Persistence
State is held in the caller-provided `struct igt_live_test`. The implementation reads persistent driver reset counters and may observe wedge state through `igt_flush_test()`.

## Dependencies And Integration Points
It depends on GT idle wait, reset-count helpers, GT logging, and `igt_flush_test`. Live tests in request and VMA files use it to bracket hardware exercises.

## Risks
Tests that intentionally reset hardware must not be wrapped by this helper or must bracket reset separately, because any reset count change is treated as failure.

## Test Signals
Failure logs identify `func(name)` and the reset count delta for global or engine-specific resets. Success means no unexpected reset and clean idle flush.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_live_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_live_test.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_live_test.h

## Purpose
This header declares the live-test guard state and begin/end functions.

## Important APIs, Types, And Functions
`struct igt_live_test` stores the i915 pointer, function/test labels, global reset baseline, and `reset_engine[I915_MAX_GT][I915_NUM_ENGINES]`. It declares `igt_live_test_begin()` and `igt_live_test_end()`.

## Control Flow
Callers allocate the struct on the stack, call begin before GPU work, and call end after cleanup to validate reset/idle state.

## State And Persistence
The struct stores per-test snapshots only. Reset counters it compares are maintained elsewhere in the driver.

## Dependencies And Integration Points
It includes GT and engine constants for array dimensions and is consumed by live request, memory, VMA, and perf helpers.

## Risks
Array dimensions must match engine/GT enumeration limits. The helper assumes tests are not expected to reset the GPU.

## Test Signals
The end function returns `0` for clean execution and `-EIO` for flush failure or reset-count drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_live_test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_mmap.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_mmap.c

## Purpose
This file provides helper functions for selftests that need to mmap a GEM VMA offset through a DRM file.

## Important APIs, Types, And Functions
- `igt_mmap_offset_with_file()` maps a specific DRM VMA offset using a supplied `struct file`.
- `igt_mmap_offset()` obtains a mock DRM file for the primary node, calls the file-specific helper, then releases the file.

## Control Flow
The helper looks up the exact `drm_vma_offset_node` under the manager lock, temporarily grants the file access with `drm_vma_node_allow()`, calls `vm_mmap()` with node offset/size, revokes access, and returns the userspace address or errno.

## State And Persistence
It temporarily mutates VMA-node access permissions for the file’s private data. The mapping may persist to the caller if `vm_mmap()` succeeds; permission is revoked immediately after mmap setup.

## Dependencies And Integration Points
It depends on DRM VMA offset management, mock DRM file creation, and kernel `vm_mmap`. It is a utility for GEM mmap selftests.

## Risks
The helper assumes the selftest owns the object and skips extra refcounting on the node. Exact offset/size lookup must match a registered mmap node. Error values are returned as unsigned long addresses following mmap conventions.

## Test Signals
Failure signals include `-ENOENT` for missing nodes, permission errors from `drm_vma_node_allow()`, or mmap error values. Success is a mapped address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_mmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_mmap.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_mmap.h

## Purpose
This header declares mmap helpers for i915 selftests.

## Important APIs, Types, And Functions
It forward-declares `drm_i915_private`, `drm_vma_offset_node`, and `file`, and declares `igt_mmap_offset()` plus `igt_mmap_offset_with_file()`.

## Control Flow
Callers choose either the convenience path that creates a mock file or the explicit file path when they already own a DRM file.

## State And Persistence
The header has no state. Successful mappings and temporary node permissions are handled by the implementation.

## Dependencies And Integration Points
It exposes the helper without pulling in heavy DRM headers. GEM mmap selftests use it to drive mmap paths from kernel tests.

## Risks
The API returns `unsigned long`, so callers must use mmap error conventions when checking failures.

## Test Signals
Signals are returned addresses or encoded errnos from the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_mmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_reset.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_reset.c

## Purpose
This file provides reset-control helpers for selftests that need to serialize against or force GT reset paths.

## Important APIs, Types, And Functions
- `igt_global_reset_lock()` blocks reset backoff and per-engine reset bits, waiting for any existing reset users.
- `igt_global_reset_unlock()` clears engine reset bits and reset backoff, then wakes waiters.
- `igt_force_reset()` wedges and resets the GT, returning whether the GT recovered from wedged state.

## Control Flow
The lock helper sets `I915_RESET_BACKOFF`, then sets every `I915_RESET_ENGINE + id` bit, waiting where needed. Unlock clears every engine bit and wakes per-bit waiters plus the reset queue. Force reset calls `intel_gt_set_wedged()` followed by `intel_gt_reset()`.

## State And Persistence
It mutates `gt->reset.flags` and can change GT wedged/recovered state. These changes affect global reset behavior beyond the local helper call until unlocked or reset completes.

## Dependencies And Integration Points
It depends on GT reset flags, engine iteration, wait queues, and core GT reset APIs. Reset and hangcheck tests use it to coordinate reset-sensitive sections.

## Risks
Forgetting to unlock leaves reset bits set and can block reset progress. `igt_force_reset()` is invasive and should be used only where a reset is expected.

## Test Signals
Lock/unlock do not return status; force reset returns true only if the GT is no longer wedged after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_reset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_reset.h

## Purpose
This header declares reset helpers used by i915 selftests.

## Important APIs, Types, And Functions
It forward-declares `struct intel_gt` and declares `igt_global_reset_lock()`, `igt_global_reset_unlock()`, and `igt_force_reset()`.

## Control Flow
Callers lock around reset-sensitive operations, unlock afterward, or call force reset to provoke recovery.

## State And Persistence
No state in the header; implementation mutates GT reset state.

## Dependencies And Integration Points
The header keeps reset helper consumers decoupled from the full reset implementation headers.

## Risks
The lock API is manual and must be paired.

## Test Signals
The only direct signal is the boolean return from `igt_force_reset()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_spinner.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_spinner.c

## Purpose
This file implements a reusable GPU spinner for i915 selftests. A spinner is a tiny batch buffer that writes its request seqno to a status page, then loops on itself until the test patches the batch to end.

## Important APIs, Types, And Functions
- `igt_spinner_init()` allocates the status-page object and batch object.
- `igt_spinner_pin()` pins/maps both objects into a specific context VM, optionally under a ww context.
- `igt_spinner_create_request()` emits the spinner batch and returns an unsignaled request.
- `igt_spinner_end()` overwrites the batch start with `MI_BATCH_BUFFER_END`.
- `igt_spinner_fini()` ends, unpins, unmaps, and releases all objects.
- `igt_wait_for_spinner()` waits until the hardware status page records the request seqno.

## Control Flow
Initialization creates an LLC-coherent HWS object and a batch object. Pinning obtains VMAs and CPU maps, then pins both in the target VM. Request creation validates `store_dword` support, moves VMAs active, writes commands to store seqno and recursively jump to the batch start, flushes, emits optional breadcrumb initialization, and emits BB start. Waiting flushes submission if ready and polls the HWS seqno first in microseconds then jiffies.

## State And Persistence
`struct igt_spinner` owns GEM objects, VMAs, mapped CPU pointers, the target context pointer, and a seqno page. The spinner mutates GPU-visible batch memory; `igt_spinner_end()` changes execution from loop to termination. State is transient but must be finalized to unpin mappings.

## Dependencies And Integration Points
It depends on GEM internal objects, VMA pinning, context request creation, MI command encoding across graphics generations, chipset flush, and wait utilities. Request cancellation and parallel-engine tests use it to occupy engines.

## Risks
Incorrect MI command generation or address mode can hang engines. The helper is context-specific after pinning and warns on reuse with a different context. Failure after request creation must add the errored request to complete cleanup semantics.

## Test Signals
`igt_wait_for_spinner()` returning true signals that the request started on the GPU. Ending and waiting on the request should then complete. `-ENODEV` is expected on engines that cannot store dwords.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_spinner.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_spinner.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_spinner.h

## Purpose
This header declares the i915 GPU spinner helper and its owned state.

## Important APIs, Types, And Functions
`struct igt_spinner` stores GT, HWS object, batch object, context, VMAs, batch pointer, and seqno pointer. The API includes init, pin, fini, request creation, end, and wait functions.

## Control Flow
Callers initialize a spinner, create a spinner request for a context and arbitration command, wait for it to start, perform the test scenario, end the spinner, wait/cancel as needed, then finalize.

## State And Persistence
The struct is caller-owned but contains references and pinned mappings that must be released with `igt_spinner_fini()`.

## Dependencies And Integration Points
It includes GEM context, engine, request, and selftest headers. It is shared by request, scheduler, hangcheck, and reset-oriented tests.

## Risks
Improper lifecycle handling leaks pinned VMAs or leaves a looping batch active. The helper assumes the target GT matches the context VM GT.

## Test Signals
Callers use returned request pointers and `igt_wait_for_spinner()` booleans to decide whether the GPU reached the loop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_spinner.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/intel_memory_region.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/intel_memory_region.c

## Purpose
This file tests Intel memory-region allocation behavior, especially the TTM buddy-backed region manager and local memory (LMEM). It covers mock region fill/reserve/contiguous fragmentation, non-power-of-two region geometry, scatterlist segment limits, mappable IO aperture behavior, live LMEM creation/clearing/CPU/GPU writes, and memcpy performance between regions.

## Important APIs, Types, And Functions
- Public entries are `intel_memory_region_mock_selftests()`, `intel_memory_region_live_selftests()`, and `intel_memory_region_perf_selftests()`.
- Object helpers include `close_objects()`, `igt_object_create()`, `igt_object_release()`, and `is_contiguous()`.
- Mock tests include `igt_mock_fill()`, `igt_mock_reserve()`, `igt_mock_contiguous()`, `igt_mock_splintered_region()`, `igt_mock_max_segment()`, and `igt_mock_io_size()`.
- Live LMEM tests include `igt_lmem_create()`, `igt_lmem_create_with_ps()`, `igt_lmem_create_cleared_cpu()`, `igt_lmem_write_gpu()`, and `igt_lmem_write_cpu()`.
- Perf helpers include `create_region_for_mapping()`, `_perf_memcpy()`, and `perf_memcpy()`.

## Control Flow
Mock tests create a mock 2 GiB region and allocate progressively or randomly sized objects, pin pages, reserve random subranges, fragment contiguous space, inspect TTM buddy block metadata, verify scatterlist segment size/alignment, and model mappable-vs-non-mappable allocation pressure. Live tests skip without LMEM or on wedged GTs. They create LMEM objects with page-size constraints, verify DMA alignment, alternate cleared/dirty allocations, issue GPU dword writes and CPU readback, or use a copy engine migration clear followed by randomized WC CPU writes. Perf tests iterate all source/destination memory-region pairs, map objects WB/WC, and measure `memcpy`, long-word copy, and `i915_memcpy_from_wc` across fixed sizes.

## State And Persistence
State consists of mock memory regions, GEM objects, pinned pages, TTM buddy resources, scatterlists, context/file handles, engine PM references, DMA reservation fences, mapped CPU pointers, and temporary migration requests. Cleanup unpins pages, drops object pages to avoid region pollution, drains freed objects, destroys mock regions, and releases contexts/files. No persistent storage is written.

## Dependencies And Integration Points
It depends on memory-region APIs, GEM LMEM/TTM helpers, `gpu_buddy`, migrate context, copy engines, object mapping/cache-domain helpers, mock region/device setup, random helpers, and live flush behavior. It integrates with mock, live, and perf registries.

## Risks
Allocation-size tests intentionally approach region exhaustion; `-ENOMEM`, `-ENXIO`, and `-E2BIG` can be expected in bounded cases. Contiguous allocation logic is sensitive to buddy fragmentation and page size. Live CPU/GPU write tests depend on copy-engine availability, cache-domain transitions, and proper fence reservation. Perf numbers are diagnostic rather than pass/fail, but mapping failures must be normalized for unavailable regions.

## Test Signals
Signals include matching allocation/free-space accounting, contiguous scatterlists where required, expected failure for too-large contiguous requests, correct buddy `max_order`, no oversized scatterlist segments, mappable allocation totals, zeroed CPU-cleared LMEM, aligned page-size allocations, correct CPU readback after GPU writes, randomized CPU write verification, and memcpy throughput logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/intel_memory_region.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/intel_scheduler_helpers.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/intel_scheduler_helpers.c

## Purpose
This file provides scheduler policy helpers for i915 selftests. It can find an engine, temporarily modify scheduling/reset policy to accelerate hang/reset scenarios, restore saved policy, and wait for a request with a fixed reset-oriented timeout.

## Important APIs, Types, And Functions
- `intel_selftest_find_any_engine()` returns the first engine in a GT or logs absence.
- `intel_selftest_modify_policy()` saves reset/flags/timeslice/preempt settings and applies either fast-reset or no-hangcheck policy.
- `intel_selftest_restore_policy()` restores saved policy and updates GuC global policy where needed.
- `intel_selftest_wait_for_rq()` waits up to `WAIT_FOR_RESET_TIME_MS`.

## Control Flow
Modify first snapshots current engine/i915 settings into `intel_selftest_saved_policy`. For fast reset it enables reset mode `2`, forced preemption, and reduced timeslice/preempt timeout. For no hangcheck it sets preempt timeout to zero. If the engine uses GuC, it pushes policy changes via `intel_guc_global_policies_update()` and restores on update failure. Restore reverses the fields and also updates GuC policy.

## State And Persistence
The helper intentionally mutates global driver reset parameters, engine flags, and engine scheduling properties. The saved-policy struct is caller-owned and must be restored after the test. GuC policy updates persist until restored.

## Dependencies And Integration Points
It depends on GT/engine iteration, i915 params, scheduler property fields, GuC policy update APIs, and request wait. It is used by scheduler and hang/reset selftests that need shorter timeouts.

## Risks
Forgetting restore leaves the driver in altered reset/preemption mode. Invalid modify type returns `-EINVAL` after saving fields but before mutation. GuC update failures require rollback, which this helper attempts.

## Test Signals
Success is `0` from modify/restore and request wait. Request timeout or interrupted wait returns the underlying negative result.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/intel_scheduler_helpers.c -->
