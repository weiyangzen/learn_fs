# subset-b-003614 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_hangcheck.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_hangcheck.c Research

Purpose: this live selftest suite stress-tests i915 GT hang detection, GPU reset, per-engine reset, stuck waiter recovery, reset queue replay, reset-time eviction, error handling, and atomic reset paths. It fabricates requests that deliberately hang by writing a breadcrumb to a hardware-status page and then recursively starting the same batch buffer so reset code has a controlled guilty request.

Important APIs/types/functions: `struct hang` owns the kernel context, HWS object, active batch object, mapped `seqno`, and batch pointer used by `hang_init()`, `hang_create_request()`, `wait_until_running()`, and `hang_fini()`. Reset tests include `igt_reset_nop()`, `igt_reset_nop_engine()`, `igt_reset_fail_engine()`, `__igt_reset_engine()`, `__igt_reset_engines()`, `igt_reset_queue()`, `igt_reset_wait()`, eviction variants, `igt_handle_error()`, and atomic reset helpers. It relies heavily on `intel_gt_reset()`, `intel_engine_reset()`, `__intel_engine_reset_bh()`, reset counters in `i915_gpu_error`, `igt_spinner`, `igt_flush_test()`, scheduler policy modifiers, and heartbeat disable/enable helpers.

Control flow: `intel_hangcheck_live_selftests()` gates on GPU reset support, rejects already wedged GTs, takes a runtime PM wakeref, then runs the subtest table through `intel_gt_live_subtests()`. The common hang flow allocates and maps internal GEM objects, pins them into the context VM, emits a self-looping batch with an initial `MI_STORE_DWORD_IMM` breadcrumb, submits it, waits until the breadcrumb proves execution, and then exercises reset or waiter logic. Several tests loop under `IGT_TIMEOUT`, compare reset counters before/after, and flush the GT after each phase.

State and persistence: this file mutates live GT state: reset flags, reset counters, engine heartbeat state, request fence errors, scheduler policy knobs, engine reset timeout injection, context priority, global reset lock, runtime PM references, and temporary GGTT/PPGTT/fence VMA state. `hang_fini()` patches the hanging batch to `MI_BATCH_BUFFER_END`, flushes the chipset, unpins maps, releases objects, closes the kernel context, and flushes tests. Eviction tests spawn kthreads that block on active VMAs or fence pinning until a reset breaks the wait.

Dependencies/integration: it integrates with GEM context/object management, i915 VM pin/evict code, engine PM, scheduler helpers, reset core, heartbeat selftest hooks, atomic-section helpers, and mock context helpers. GuC submission changes expectations: some engine resets are skipped or verified through request completion instead of KMD-triggered engine reset counters.

Risks and test signals: the suite is intentionally destructive and can wedge the GT if reset handling breaks. False failures can arise from engines without store-dword support, GuC reset semantics, scheduler priority capability, timing under heavy load, or platforms without per-engine reset. Strong pass signals are expected reset counter deltas, guilty request `-EIO`, unrelated queued requests preserving zero fence error, kthreads unblocking after reset, no global reset when engine reset is expected, and clean `igt_flush_test()` results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_hangcheck.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_llc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_llc.c Research

Purpose: this is a focused LLC/RPS selftest that verifies the firmware pcode ring-frequency table matches the driver-computed IA and ring frequencies over the supported GPU frequency range.

Important APIs/types/functions: `gen6_verify_ring_freq()` is the only substantive helper and `st_llc_verify()` is the exported selftest entrypoint declared in `selftest_llc.h`. It uses `struct intel_llc`, `struct ia_constants`, `struct intel_rps`, `get_ia_constants()`, `calc_ia_freq()`, `snb_pcode_read()`, and `intel_gpu_freq()`.

Control flow: `st_llc_verify()` calls `gen6_verify_ring_freq()`. The helper takes a runtime PM wakeref, fetches IA constants from the LLC code, and iterates from `consts.min_gpu_freq` to `consts.max_gpu_freq`. For each frequency it calculates expected IA and ring values, asks pcode for `GEN6_PCODE_READ_MIN_FREQ_TABLE`, extracts low and high bytes, and compares them against expectations. The loop stops on read failure or mismatch.

State and persistence: no persistent driver state is intentionally changed. The test temporarily holds runtime PM to make pcode access valid and reads firmware tables. It returns after releasing the wakeref.

Dependencies/integration: this file is a selftest facade over the production LLC and RPS frequency code. It validates the contract between software table generation and pcode-visible hardware state, including Gen9 scaling through `GEN9_FREQ_SCALER`.

Risks and test signals: failures indicate either pcode read failure (`-ENXIO`) or a mismatch between expected CPU/ring ratios and firmware-visible entries (`-EINVAL`). The test depends on valid IA constants and platforms where the pcode table is available; if constants cannot be obtained it exits without error. Diagnostic output includes GPU frequency in MHz and expected/found table fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_llc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_llc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_llc.h Research

Purpose: this small header exposes the LLC selftest entrypoint to the i915 selftest wiring while avoiding a hard include dependency on the full LLC type definition.

Important APIs/types/functions: it forward-declares `struct intel_llc` and declares `int st_llc_verify(struct intel_llc *llc);`. The include guard is `SELFTEST_LLC_H`.

Control flow: there is no runtime control flow. The header lets callers compile against `st_llc_verify()` without needing internal implementation details from `selftest_llc.c`.

State and persistence: the header owns no state. The pointed-to `intel_llc` instance remains owned by GT/LLC code; the implementation only borrows it.

Dependencies/integration: it is consumed by selftest registration or LLC init/check paths that want to run table verification. Its narrow forward declaration reduces rebuild coupling and avoids accidental dependency on broader GT headers.

Risks and test signals: the main risk is prototype drift with the implementation or callers. Since it declares a single external function, build success is the signal that the interface remains synchronized.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_llc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_lrc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_lrc.c Research

Purpose: this live selftest suite validates logical ring context behavior: context image layout, fixed register offsets, live ring state, GPR clearing, timestamp save/restore, register isolation between contexts, context workaround batch execution, recovery from corrupted context state, and PPHWSP runtime accounting.

Important APIs/types/functions: entrypoint `intel_lrc_live_selftests()` runs subtests such as `live_lrc_layout()`, `live_lrc_fixed()`, `live_lrc_state()`, `live_lrc_gpr()`, `live_lrc_isolation()`, `live_lrc_timestamp()`, `live_lrc_garbage()`, `live_pphwsp_runtime()`, `live_lrc_indirect_ctx_bb()`, and `live_lrc_per_ctx_bb()`. Key helpers parse default LRC images (`store_context()`, `load_context()`), create scratch VMAs, emit semaphore waits, load/store MMIO registers, poison register state, and compare sampled state.

Control flow: tests generally iterate over each engine, pin contexts and scratch VMAs, emit MI command streams, wait for submission or completion, then compare hardware-written memory against expected context state. Layout tests compare `__lrc_init_regs()` output with `engine->default_state`. Isolation tests capture reference register streams, poison a separate context with LRI commands, release a semaphore, and compare before/after samples. Workaround-batch tests install canaries in indirect/per-context WA BB pages and verify `RING_START` is captured at restore time. Garbage tests corrupt the saved LRC image and expect reset recovery.

State and persistence: this file touches context state pages, `ce->lrc_reg_state`, WA batch pages, status-page semaphores, CS GPRs, timestamps, scheduler tasklets during garbage reset, engine heartbeat state, PM references, and runtime underflow counters. All scratch/result VMAs and contexts are released after each path, and most engine loops call `igt_flush_test()` to catch leaks or wedging.

Dependencies/integration: it is tightly coupled to LRC register layout definitions, MI command encoding, engine class rules, GGTT scratch allocation, shmem-backed default state, engine PM/heartbeat, request submission, and runtime accounting in PPHWSP. Platform gates skip unsupported or known-broken isolation/timestamp cases.

Risks and test signals: these tests are sensitive to hardware generation, engine class masks, context image format changes, scheduler timing, and platforms where register access is masked or aliased. Pass signals include matching LRI register offsets, zeroed new-context GPRs after preemption and non-preemption paths, monotonic timestamps, unchanged reference registers despite remote poison, correct WA BB canaries, reset error on corrupted contexts, and zero PPHWSP runtime underflows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_lrc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_migrate.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_migrate.c Research

Purpose: this suite verifies and benchmarks i915 migrate BLT support for copying and clearing memory across system/internal memory and local memory, including flat CCS metadata handling, ring-space edge cases, concurrency, and throughput reporting.

Important APIs/types/functions: correctness helpers include `copy()`, `clear()`, `intel_context_copy_ccs()`, `intel_migrate_ccs_copy()`, wrappers around `intel_migrate_copy()`, `intel_context_migrate_copy()`, `intel_migrate_clear()`, and `intel_context_migrate_clear()`. Live subtests are `live_migrate_copy()`, `live_migrate_clear()`, `live_emit_pte_full_ring()`, and threaded copy/clear variants. Performance tests use `perf_clear_blt()` and `perf_copy_blt()`.

Control flow: copy tests allocate source and destination objects, initialize source with incremental dwords and destination with bitwise inverse values, call a migrate/global copy function under ww locking, wait for the output request, and sample one random dword per page for correctness. Clear tests initialize an object, optionally write/read CCS via `intel_migrate_ccs_copy()` on flat-CCS LMEM objects, call the clear function, verify data dwords, and verify CCS bytes were zeroed. Threaded tests spawn `num_online_cpus() + 1` workers that repeatedly run 2*`CHUNK_SZ` operations. The full-ring regression shrinks a migrate context ring and ensures `emit_pte()` waits for space rather than overwriting reserved space.

State and persistence: the tests create and pin GEM objects, lock them with ww contexts, pin WC maps, submit migrate requests, spawn temporary kthreads, use an `igt_spinner`, and temporarily create migrate contexts. Performance helpers lock and pin objects, run several passes, sort timings, and print MiB/s. All objects, maps, contexts, and request refs are released.

Dependencies/integration: it integrates with GEM LMEM/internal allocation, scatter-gather page lists, PAT indices, migrate VM/context code, CCS access helpers, request waits, timers, and kernel thread management. It gates live tests on `gt->migrate.context` and perf tests additionally skip wedged GTs.

Risks and test signals: risks include allocation pressure from large sizes, Small BAR limitations, ww deadlock retry paths, interruptible kthread stops, and timing-sensitive ring-space behavior. Strong signals are correct sampled dwords after copy/clear, zero CCS metadata after clear, no reserved-space assertion in the ring test, no worker failures under concurrency, and printed throughput for perf lanes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_migrate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_mocs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_mocs.c Research

Purpose: this live suite checks that Memory Object Control State and L3 cache-control tables are programmed as expected for kernel contexts, new user contexts, and after engine/global reset.

Important APIs/types/functions: `struct live_mocs` bundles expected `drm_i915_mocs_table`, optional MOCS/L3CC pointers, a scratch VMA, and mapped result memory. Core helpers are `live_mocs_init()`, `read_regs()`, `read_mocs_table()`, `read_l3cc_table()`, `check_mocs_engine()`, `active_engine_reset()`, and `__live_mocs_reset()`. Entrypoint `intel_mocs_live_selftests()` runs `live_mocs_kernel`, `live_mocs_clean`, and `live_mocs_reset`.

Control flow: initialization queries `get_mocs_settings()` to discover which tables exist, creates a GGTT scratch page, and maps it WB. Per-engine checks create a request, mark scratch active for write, emit `MI_STORE_REGISTER_MEM_GEN8` commands to read the MOCS and render-only L3CC tables into scratch, wait for completion, and compare each entry with `for_each_mocs()` / `for_each_l3cc()`. Reset tests modify scheduler policy for fast reset, create a large-ring context, test clean reset, active spinner reset, and GT reset, then re-read the tables.

State and persistence: it reads live MMIO state through command streamer stores, temporarily disables normal scheduling policy, uses engine PM references, holds the global reset lock for reset checks, runs spinners, and may reset engines or the GT. Scratch VMA mappings are released by `live_mocs_fini()`.

Dependencies/integration: it depends on MOCS table generation, MOCS register addressing, L3CC register layout, engine PM, reset helpers, spinner selftests, and GuC reset semantics. MCR-ranged L3CC registers are skipped for CS readback because CPU MCR routing does not apply to command-streamer access.

Risks and test signals: failures indicate missing MOCS settings, register readback mismatch, reset not preserving programmed tables, or spinner/reset problems. The test is hardware-sensitive around global vs per-engine MOCS, render-only L3CC, MCR ranges, and GuC-submitted engines where KMD cannot manually perform the same reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_mocs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_rc6.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_rc6.c Research

Purpose: this file tests RC6 low-power residency behavior and a context-info workaround path that reads `GEN8_RC6_CTX_INFO` without causing reset.

Important APIs/types/functions: `rc6_residency()` sums RC6/RC6p/RC6pp residency. `live_rc6_manual()` manually disables RC6, samples residency/power, parks into RC6, verifies residency and power reduction, and unparks. `__live_rc6_ctx()` emits an SRM of `GEN8_RC6_CTX_INFO` into a request HWSP, `randomised_engines()` builds a shuffled engine list, and `live_rc6_ctx_wa()` runs the context-info poke twice per engine.

Control flow: manual RC6 testing skips disabled RC6 and Valleyview/Cherryview PCU-driven RC6. It takes runtime PM, disables RC6, sleeps, validates residency does not rise, optionally measures RAPL power, parks RC6, sleeps again, verifies residency rose, compares RC6 power against RC0 power, then unparks. The context workaround test creates sacrificial contexts per engine, submits a register-store request, waits for GT idle/PM idle, logs the value, and asserts engine reset counters did not change.

State and persistence: the test temporarily changes RC6 state with `__intel_rc6_disable()`, `intel_rc6_park()`, and `intel_rc6_unpark()`, holds runtime PM, reads forcewake-visible registers, samples RAPL energy, creates contexts, and observes reset counters. It should restore RC6 before returning from the normal manual path.

Dependencies/integration: it depends on RC6 residency APIs, RPS frequency reads, librapl, engine PM, ring command emission, timeline HWSP offsets, i915 reset counters, and GT idle waits. It is generation-gated for context-info reads and platform-gated for manual RC6 control.

Risks and test signals: timing and power measurements can be noisy, so power validation only runs when librapl is supported. Pass signals are no residency accumulation while disabled, increasing residency while parked, RC6 power not exceeding half RC0 power, and no reset count increment after context-info reads. Failures taint CI on reset-needed context-info paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_rc6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_rc6.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_rc6.h Research

Purpose: this header declares the two RC6 live selftest functions for registration from other i915 selftest aggregation code.

Important APIs/types/functions: it exposes `int live_rc6_ctx_wa(void *arg);` and `int live_rc6_manual(void *arg);` under include guard `SELFTEST_RC6_H`.

Control flow: there is no runtime behavior in the header. Both functions accept the selftest `void *arg` convention, expected to be an `intel_gt *` by the implementation.

State and persistence: no state is owned by the header. The implementation mutates RC6 and context state, but that is not represented here.

Dependencies/integration: the header is the integration point between RC6 selftest implementation and the broader i915 selftest runner. It deliberately avoids including GT or RC6 structure definitions.

Risks and test signals: build failures are the main signal if prototypes drift. The narrow interface keeps compile-time coupling low.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_rc6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_reset.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_reset.c Research

Purpose: this live suite verifies base GT reset behavior independent of hangcheck-specific request replay: global reset accounting, stolen-memory preservation, wedged recovery, and atomic-context reset paths.

Important APIs/types/functions: central helper `__igt_reset_stolen()` CRCs stolen memory before and after reset. Subtests include `igt_reset_device_stolen()`, `igt_reset_engines_stolen()`, `igt_global_reset()`, `igt_wedged_reset()`, `igt_atomic_reset()`, and `igt_atomic_engine_reset()`. Entrypoint `intel_reset_live_selftests()` gates on GPU reset support.

Control flow: stolen-memory tests use the GGTT error-capture node to map each stolen page, fill unused pages with `STACK_MAGIC`, record CRCs, perform either full GT reset or per-engine reset while spinners are active, then re-map pages and compare CRCs. Global reset records `i915_reset_count()` before/after `intel_gt_reset()`. Wedged reset sets the GT wedged and expects reset to clear it. Atomic tests iterate `igt_atomic_phases`, wrap reset prepare/finish around `intel_gt_reset_all_engines()` or call `__intel_engine_reset_bh()` with tasklets disabled and bottom halves controlled.

State and persistence: it takes the global reset lock, runtime PM/GT PM references, manipulates stolen-memory scratch mappings through GGTT, runs spinners, disables tasklets during engine atomic reset, sets/clears wedged state, and forces final resets after poking reset internals. It frees CRC buffers and temporary pages on exit.

Dependencies/integration: this file integrates with stolen memory management, GGTT insert/clear operations, io-mapped WC reads, reset prepare/finish, atomic section test helpers, spinner selftests, and GuC submission gates. It skips per-engine reset tests when unsupported or GuC submission owns reset.

Risks and test signals: stolen-memory CRC differences below the reserved bias are informational, while clobbering unreserved stolen pages above `I915_GEM_STOLEN_BIAS` fails. Other pass signals are reset count increments, wedged state recovery, and successful reset under each atomic phase. Risks include platform-specific stolen memory layout, missing error-capture nodes, and strict atomic-context assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_ring.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_ring.c Research

Purpose: this mock selftest validates ring-buffer wrap arithmetic, especially `intel_ring_direction()` and `intel_ring_wrap()` behavior around half-ring ambiguity.

Important APIs/types/functions: `mock_ring()` allocates an in-memory `intel_ring` with a backing command area, initialized refcount, size, wrap value, effective size, vaddr, pin count, and computed space. `check_ring_direction()`, `check_ring_step()`, and `check_ring_offset()` assert direction semantics. `igt_ring_direction()` is the sole subtest run by `intel_ring_mock_selftests()`.

Control flow: the test creates a 4096-byte mock ring, then probes offsets at zero, half-ring, near wrap, and oversized unwrapped values. For increasing powers-of-two steps below half-ring it validates same-position equality, forward direction, and backward direction. It also tests a `half - 64` step and unwrapped inputs beyond ring size.

State and persistence: all state is local heap memory; no hardware or GEM object is touched. The ring is freed at the end.

Dependencies/integration: it exercises production ring helper arithmetic without requiring a device. It uses `i915_subtests()` rather than a live GT runner.

Risks and test signals: this catches regressions in wrap comparison that can corrupt request space accounting or command ordering. The known precision limit is ring size divided by two; the test stays below that except for deliberate boundary coverage. Any mismatch returns `-EINVAL` with the computed and expected direction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_ring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_ring_submission.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_ring_submission.c Research

Purpose: this live suite tests legacy ring-submission inter-context workaround batch behavior. It ensures the workaround batch runs when switching between user contexts, but not for kernel context or repeated same-user-context execution.

Important APIs/types/functions: `create_wally()` creates and pins a batch VMA that writes `STACK_MAGIC` near offset 4000 and stores a dummy context in `vma->private`. `context_sync()`, `new_context_sync()`, `mixed_contexts_sync()`, `double_context_sync_00()`, and `kernel_context_sync_00()` create request sequences and inspect the marker. `__live_ctx_switch_wa()` temporarily installs the custom batch at `engine->wa_ctx.vma`.

Control flow: `live_ctx_switch_wa()` runs only for legacy ring submission (`submission_method <= INTEL_SUBMISSION_RING`) and skips engines without store-dword support or Gen4/5 privileged store issues. For each engine it saves and clears the existing WA context VMA, installs the marker batch, synchronizes kernel and user contexts in specific patterns, validates marker writes, then restores the original VMA after flushing.

State and persistence: it temporarily mutates `engine->wa_ctx.vma`, creates user contexts, pins a high user VMA, maps the batch WC, and releases the dummy context plus VMA map during cleanup. The mutation is restored even on the normal error path after `__live_ctx_switch_wa()`.

Dependencies/integration: it depends on legacy ring submission code, context switching, WA batch plumbing, GEM internal objects, VM pinning/sync, engine PM, and `igt_flush_test()`.

Risks and test signals: incorrect WA execution can leak user-visible state or skip required workarounds. Pass signals are zero marker for kernel-context execution, `STACK_MAGIC` after user context switches, zero marker for repeated same context, and clean flush. The test is intentionally not used for execlists/GuC submission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_ring_submission.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_rps.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_rps.c Research

Purpose: this suite validates Render Power States frequency control, clock interval conversion, command-streamer frequency scaling, SRM-based frequency observation, PM interrupt generation, power reduction at lower frequency, and dynamic reclocking.

Important APIs/types/functions: exported subtests are `live_rps_clock_interval()`, `live_rps_control()`, `live_rps_frequency_cs()`, `live_rps_frequency_srm()`, `live_rps_interrupt()`, `live_rps_power()`, and `live_rps_dynamic()`. Helpers include `create_spin_counter()`, `wait_for_freq()`, `rps_set_check()`, `measure_frequency_at()`, `measure_cs_frequency_at()`, `scaled_within()`, interrupt probes `__rps_up_interrupt()` / `__rps_down_interrupt()`, and RAPL power measurement helpers.

Control flow: most tests idle the GT, replace `rps->work.func` with `dummy_rps_work` to suppress normal reclocking work, disable heartbeats around spinners, then drive engines busy or idle while programming frequencies. Clock interval tests program RPS evaluation interval registers and compare GT clock conversion to wall time. Frequency tests run a command-streamer counter loop and compare counts at min/max RPS. Interrupt tests force min/max, sleep for evaluation intervals, and inspect `pm_iir`. Dynamic tests start from min, run a spinner, and expect frequency to rise and later fall.

State and persistence: this file actively changes RPS requested frequencies, `rps->work.func`, RC6 state, PM interrupt enable/disable, forcewake registers, PM QoS latency requests, engine heartbeat state, CS GPRs, and spinner batches. Cleanup restores work function, removes PM QoS requests, ends spinners, re-enables RC6/heartbeats, and flushes tests.

Dependencies/integration: it integrates with RPS/RP registers, GT clock utilities, engine PM, RC6, librapl, PM QoS, command streamer MI math/SRM commands, pcode frequency tables, and performance-limit reason registers. The header exports these functions for selftest registration.

Risks and test signals: platform firmware throttling, C-state latency, RAPL availability, fragile PCU behavior, and timing jitter can affect results. Some scaling mismatches are logged as `-EINTR` to continue probing. Strong pass signals are requested frequencies being reached, clock intervals within 80-125% tolerance, command counters scaling with frequency, UP/DOWN PM interrupts recorded without unexpected frequency changes, lower-frequency power saving, and dynamic busy/idle reclocking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_rps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_rps.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_rps.h Research

Purpose: this header exposes the RPS live selftest functions to the i915 selftest registration code.

Important APIs/types/functions: it declares `live_rps_control()`, `live_rps_clock_interval()`, `live_rps_frequency_cs()`, `live_rps_frequency_srm()`, `live_rps_power()`, `live_rps_interrupt()`, and `live_rps_dynamic()`. All take the selftest runner's `void *arg` convention, implemented as an `intel_gt *`.

Control flow: no executable logic is present; it is a declaration boundary.

State and persistence: the header owns no state. The implementations mutate live RPS/PM state and restore it internally.

Dependencies/integration: this header lets other GT selftest modules include RPS subtests without pulling in implementation internals. It has a single include guard, `SELFTEST_RPS_H`.

Risks and test signals: interface drift is caught by build errors. Because the declarations are direct and narrow, accidental dependency expansion is low.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_rps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_slpc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_slpc.c Research

Purpose: this live suite validates GuC SLPC frequency control: min/max frequency requests, RP0 grant behavior, power scaling, and multi-tile interaction when several GTs exercise SLPC concurrently.

Important APIs/types/functions: helpers `slpc_set_min_freq()`, `slpc_set_max_freq()`, `slpc_set_freq()`, and `slpc_restore_freq()` wrap GuC SLPC H2G calls and delay for completion. `vary_min_freq()`, `vary_max_freq()`, `max_granted_freq()`, and `slpc_power()` perform assertions. `run_test()` is the shared engine/GT harness. Entrypoint `intel_slpc_live_selftests()` runs vary max/min, max granted, power, and tile interaction tests.

Control flow: `run_test()` skips non-SLPC platforms and fused min/max frequencies, initializes a spinner, records original SLPC min/max, forces min to RPn, disables efficient-frequency bias, takes GT PM, and iterates store-dword-capable engines. For each engine it starts a spinner on the kernel context, runs the selected frequency/power assertion, checks actual frequency rises above min for non-power tests, ends the spinner, and restores heartbeats. It then restores original min/max and efficient-frequency behavior. Tile interaction starts one kthread worker per GT and runs `run_test(..., TILE_INTERACTION)` in parallel.

State and persistence: the file changes GuC SLPC min/max frequency limits, ignore-efficient-frequency mode, GT PM wakerefs, engine heartbeat state, and spinner activity. It restores frequency bounds and efficient-frequency mode through `slpc_restore_freq()`, flushes GEM tests, releases PM, and waits for idle.

Dependencies/integration: it depends on GuC SLPC APIs, RPS actual/punit frequency reads, perf-limit registers, librapl, engine spinners, GT iteration across tiles, and kthread workers. Media GT/video engine frequency differences are explicitly skipped for some max-grant checks.

Risks and test signals: risks include H2G latency, pcode throttling, media-engine RP0 differences, RAPL noise, and restoration failure if an early setup path returns before cleanup. Pass signals are SW request bounded by min/max plus request unit tolerance, actual frequency exceeding min under load, RP0 granted or explained by perf-limit reasons, lower-frequency power reduction, and no parallel tile worker errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_slpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_timeline.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_timeline.c Research

Purpose: this file tests intel timeline synchronization and HWSP breadcrumb allocation in both mock and live modes. It covers cacheline reuse, sync-map wrap comparisons, benchmark characteristics, independent HWSP writes, seqno rollover, delayed GPU reads of HWSP, and breadcrumb slot recycling.

Important APIs/types/functions: mock helpers include `mock_hwsp_freelist()`, `igt_sync()`, and `bench_sync()`. Live helpers include `selftest_tl_pin()`, `checked_tl_write()`, `live_hwsp_engine()`, `live_hwsp_alternate()`, `live_hwsp_wrap()`, `live_hwsp_read()`, `live_hwsp_rollover_kernel()`, `live_hwsp_rollover_user()`, and `live_hwsp_recycle()`. `struct hwsp_watcher` manages a GPU-visible result buffer and request used to read delayed HWSP references.

Control flow: mock tests create timelines on a mock GEM device, pin HWSP allocations, insert cachelines into a radix tree to detect duplicates, shuffle/free histories, and exercise `__intel_timeline_sync_is_later()` across wrap cases. Live tests create thousands of timelines, emit GGTT store-dword requests to each HWSP slot, flush, and verify stored values. Wrap tests force `tl->seqno` near `UINT_MAX`, obtain new seqnos, and validate old/new HWSP cachelines remain valid. The delayed read test creates watcher requests with software fences, obtains HWSP addresses before/after timeline wrapping, and checks before reads are `< seqno` while after reads are `>= seqno`.

State and persistence: it allocates timelines, pins/unpins HWSP GGTT objects, mutates timeline seqnos for rollover simulation, temporarily assigns a user context to a shared timeline, creates large watcher VMAs, manipulates request timeline locks, disables heartbeats in rollover tests, and retires requests to recycle HWSP storage. All timelines and VMAs are released.

Dependencies/integration: dependencies include timeline allocation/sync internals, GEM ww locking, mock GEM device, engine PM, MI store/LRM/SRM commands, software fences, request retirement, and GT flush tests.

Risks and test signals: key risks are timeline lock ordering, stale HWSP references across wrap, duplicate cacheline allocation, and request retirement/recycling races. Pass signals include unique HWSP cachelines, expected sync comparison outcomes across `INT_MAX`/`UINT_MAX` wrap, correct per-timeline stored values, old HWSP retained over wrap, watcher comparisons passing, and completed pre-wrap requests for kernel and user timelines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_timeline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_tlb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_tlb.c Research

Purpose: this live selftest verifies that GT TLB invalidation revokes active PTE translations. It forces a spinning GPU batch to observe a remapped PTE and requires a full invalidate to make the updated physical backing visible.

Important APIs/types/functions: `pte_tlbinv()` builds the core scenario. `mem_tlbinv()` allocates paired memory objects and runs the scenario across engines and page sizes. `tlbinv_full()` calls `intel_gt_invalidate_tlb_full()`, `invalidate_full()` runs system-memory and LMEM variants, and `intel_tlb_live_selftests()` iterates GTs.

Control flow: for each memory type, `mem_tlbinv()` creates objects A and B, maps them WC, creates a PPGTT, and replaces a context VM with that PPGTT. For each supported page size it first sanity-checks that a self-mapped VMA can end the conditional batch, then maps VMA A at a random aligned offset, aliases VMA B onto the same PTE node, writes `-1` through A and `0` through B, starts a `MI_CONDITIONAL_BATCH_BUFFER_END` loop, swaps PTE entries to B with `insert_entries()`, calls the invalidate callback, and waits for the request to complete.

State and persistence: it creates internal or LMEM objects, pins VMAs into a private PPGTT, temporarily edits `vb->node` to overwrite the same PTE, creates command batches, writes object mappings directly, changes context VM ownership, updates PTEs, and invalidates GT TLB. It restores VMA node state, unpins/unbinds, releases PPGTT, and flushes tests.

Dependencies/integration: it depends on GEM memory regions, PPGTT creation, page-size runtime info, VMA resource descriptors, PAT/PTE flags including `PTE_LM`, MI conditional batch semantics, engine request submission, and TLB sequence APIs. It skips pre-Gen8 because TLB invalidation is not implemented.

Risks and test signals: risks include large LMEM allocation limits, Small BAR sizing, 64K-page alignment rules requiring 2M PT coverage, slow OTHER_CLASS engines, and aliasing `vb->node` carefully. Pass signal is that the spinning request does not complete before remap/invalidate, then completes within timeout after invalidate; unexpected early completion or no completion is a failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_tlb.c -->
