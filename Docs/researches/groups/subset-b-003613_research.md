# subset-b-003613 research

Grouped research for i915 GT workaround, mock-engine, and live selftest files. Each section preserves the original source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_workarounds.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_workarounds.c

Purpose: implements the i915 GT hardware workaround framework for context state, GT-global MMIO, engine reset domains, and nonprivileged register whitelists. The file converts platform/stepping-specific workaround rules into sorted `i915_wa_list` entries, applies them through MMIO or command-stream programming, verifies selected values, and exposes the public init/apply/verify hooks declared in `intel_workarounds.h`.

Important APIs/functions: list management is centered on `wa_init_start`, `wa_init_finish`, `_wa_add`, `wa_add`, `wa_mcr_add`, `wa_write*`, `wa_mcr_write*`, and `wa_masked_*`. Public context APIs are `intel_engine_init_ctx_wa()` and `intel_engine_emit_ctx_wa()`. GT APIs are `intel_gt_init_workarounds()`, `intel_gt_apply_workarounds()`, and `intel_gt_verify_workarounds()`. Whitelist APIs are `intel_engine_init_whitelist()` and `intel_engine_apply_whitelist()`. Engine APIs are `intel_engine_init_workarounds()`, `intel_engine_apply_workarounds()`, and `intel_engine_verify_workarounds()`.

Control flow: workaround construction starts with a small generic list builder that stores register offset, clear/set/read masks, masked-register semantics, and MCR status. `_wa_add()` keeps the list sorted by MMIO offset and merges duplicate register programming, warning when a new clear mask overlaps older settings. Context workaround initialization dispatches by engine class and graphics generation/stepping; render engines receive most per-context graphics workarounds, while Gen12+ also adds fake context programming such as nested batch-buffer compatibility and BLIT MOCS defaults. `intel_engine_emit_ctx_wa()` emits a flushed `MI_LOAD_REGISTER_IMM` sequence into a request, reads existing register values for RMW entries under forcewake/MCR locking, optionally appends `3DSTATE_MESH_CONTROL` for DG2/Xe_LPG render, and flushes again.

GT workaround control flow starts in `intel_gt_init_workarounds()`, which records tuning settings and platform-specific global reset/resume workarounds. It includes MCR steering setup for Gen9, ICL/Gen12, Xe_HP/DG2, Xe_LPG, and media GTs, plus reset-domain programming for clock gating, L3, FTLB, CCS, GAM, and slice/subslice routing. `wa_list_apply()` performs forcewake-protected MMIO RMW writes and multicasts MCR entries. `wa_list_verify()` reads back relevant bits when verification is meaningful. Whitelist construction builds per-engine `RING_FORCE_TO_NONPRIV` slots, validates access/range flags, and clears unused slots. Engine workaround initialization adds MOCS tuning, render/compute shared reset-domain programming, RCS/CCS/XCS-specific workarounds, and DG2 CCS load-balancing mode.

State and persistence behavior: the code manages four distinct persistence domains. Context workarounds are saved in the default context image and inherited by newly created contexts. GT workarounds are persisted in `gt->wa_list` and re-applied after GPU reset, suspend/resume, or similar loss of register state. Engine workarounds live in each `engine->wa_list`, are re-applied after engine reset, and may be handed to GuC save/restore paths when kernel submission does not control resets directly. Whitelist entries live in `engine->whitelist` and program hardware nonprivileged access slots. MCR steering also updates `gt->default_steering` and may disable steering-table entries when default steering covers a domain.

Dependencies and integration points: this file is tightly coupled to platform detection macros, `intel_gt_mcr` steering helpers, `intel_uncore` forcewake and raw MMIO, engine request/ring emission, i915 register definitions, GuC ADS save/restore expectations, CCS mode selection, and debug selftests through `selftest_workarounds.c`. It also interacts with display registers for FBC-related workarounds and with MOCS/GT topology data such as SSEU, mslice, l3bank, and engine class tables.

Risks: workaround tables are fragile because an incorrect generation/stepping predicate can program a register on the wrong hardware or omit a required workaround on affected hardware. MCR entries need correct steering and multicast behavior; readback verification is intentionally skipped for some write-only or firmware-locked registers, reducing test observability. Duplicate merge logic can silently coalesce settings, so conflicting clear/set masks need review. Context workaround emission depends on adequate ring space, forcewake coverage, and safe RMW under uncore and MCR locks. Whitelist mistakes can expose privileged registers or block userspace workarounds.

Test signals: debug builds verify GT and engine workaround readback through `wa_verify()`. `intel_engine_verify_workarounds()` stores register values to a scratch VMA with `MI_STORE_REGISTER_MEM`, skipping MCR ranges that cannot be verified from the command streamer path. The file is compiled with `selftest_workarounds.c` under `CONFIG_DRM_I915_SELFTEST`, and broader coverage comes from engine reset, context creation, GuC save/restore, suspend/resume, and platform CI that checks lost workaround reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_workarounds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_workarounds.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_workarounds.h

Purpose: declares the public i915 workaround lifecycle API and provides the inline cleanup helper for workaround lists.

Important APIs/functions: `intel_wa_list_free()` releases a list allocation with `kfree()` and zeroes the whole `i915_wa_list`. The header declares context APIs `intel_engine_init_ctx_wa()` and `intel_engine_emit_ctx_wa()`, GT APIs `intel_gt_init_workarounds()`, `intel_gt_apply_workarounds()`, `intel_gt_verify_workarounds()`, whitelist APIs `intel_engine_init_whitelist()` and `intel_engine_apply_whitelist()`, and engine APIs `intel_engine_init_workarounds()`, `intel_engine_apply_workarounds()`, `intel_engine_verify_workarounds()`.

Control flow: this header does not implement runtime control flow beyond freeing list storage. It forms the call boundary used by GT and engine initialization code, reset/resume paths, request emission for context state, and verification/selftest code.

State and persistence behavior: the only state mutation in the header is destructive cleanup of `wal->list` and reset of metadata fields. The declared functions initialize and apply state held in `struct intel_gt` and `struct intel_engine_cs`, but those structures are defined elsewhere.

Dependencies and integration points: includes `<linux/slab.h>` for memory free helpers and `intel_workarounds_types.h` for `struct i915_wa_list`. It forward-declares i915 request, engine, GT, and device-private structures to avoid pulling implementation headers into users.

Risks: callers must not use a workaround list after `intel_wa_list_free()` without reinitializing it, because the helper zeroes both metadata and pointer fields. The API split makes it easy to confuse context, GT, whitelist, and engine workaround domains; call sites should use the matching init/apply/verify hook.

Test signals: compile coverage confirms function prototypes match `intel_workarounds.c`. Runtime signal is indirect through selftests and reset/resume paths that call these APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_workarounds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_workarounds_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_workarounds_types.h

Purpose: defines the compact data structures used by the i915 workaround framework to describe register programming and grouped workaround lists.

Important APIs/types: `struct i915_wa` stores either an `i915_reg_t` or `i915_mcr_reg_t`, clear/set/read masks, and bitfields identifying masked-register and MCR semantics. `struct i915_wa_list` stores the owning `intel_gt`, list label, engine label, dynamically allocated array, entry count, and logical workaround count.

Control flow: the header contains no executable flow. Its data shape drives `_wa_add()` merge/sort behavior, MMIO apply/verify loops, context LRI emission, and whitelist slot programming.

State and persistence behavior: `i915_wa_list` persists generated workaround state in GT and engine objects across initialization and later apply/verify calls. `wa_count` can exceed `count` because multiple logical workarounds may merge into one register entry. `read` identifies bits safe/required to validate and can be zero for write-only or deliberately unverifiable entries.

Dependencies and integration points: includes Linux integer types and `i915_reg_defs.h` for typed MMIO register wrappers. Forward-declares `struct intel_gt` for ownership without importing full GT definitions.

Risks: the union means code must respect `is_mcr` before choosing singleton or MCR access paths. Incorrect `read` masks can create false CI failures or hide lost settings. Bitfield packing should remain simple because these structures are allocated in arrays and copied by value.

Test signals: validated indirectly by all workaround construction/apply/verify paths; compile failures catch register type changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_workarounds_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/ivb_clear_kernel.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/ivb_clear_kernel.c

Purpose: provides a generated Ivy Bridge render-clear shader/kernel as a static `u32` instruction array for Gen7 render clear batch generation.

Important APIs/types/functions: the only symbol is `static const u32 ivb_clear_kernel[]`. It is data, not callable code, and is intended to be included by the Gen7 render clear implementation that wraps it in a `cb_kernel` descriptor.

Control flow: none in C. At runtime, surrounding render clear code copies or references the instruction dwords when emitting a batch buffer that clears render state or GPRs on IVB-class hardware.

State and persistence behavior: immutable read-only data compiled into the driver. It has no local allocation, no persistent mutable state, and no cleanup.

Dependencies and integration points: depends on a surrounding translation unit providing `u32` and including this file or compiling it in the correct context. The generated timestamp in the comment identifies the source as IGT GPU Tools output, and the consumer is the Gen7 render clear path.

Risks: because the blob is opaque machine instructions, source review cannot easily validate semantics. Any mismatch between the blob and IVB EU ISA, batch layout, or consumer assumptions could produce GPU hangs or ineffective clears. Regeneration should preserve exact dword ordering and be tested on affected hardware.

Test signals: coverage is indirect through render clear setup tests and hardware execution on Ivy Bridge paths; compile coverage only confirms array syntax.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/ivb_clear_kernel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/mock_engine.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/mock_engine.c

Purpose: implements a software-only `intel_engine_cs` backend for i915 mock selftests. It supplies minimal engine, context, ring, scheduling, request submission, reset, breadcrumbs, and PM plumbing without real GPU execution.

Important APIs/functions: public constructors and lifecycle hooks are `mock_engine()`, `mock_engine_init()`, `mock_engine_flush()`, `mock_engine_reset()`, and `mock_engine_free()` from the companion header, although this file only defines an empty `mock_engine_reset()` and does not define `mock_engine_free()` in the read content. Internal helpers include `mock_ring()`, `mock_ring_free()`, `mock_context_alloc()`, `mock_context_pre_pin()`, `mock_context_destroy()`, `mock_request_alloc()`, `mock_submit_request()`, `mock_add_to_engine()`, `mock_remove_from_engine()`, `mock_reset_cancel()`, and timer callback `hw_delay_complete()`.

Control flow: `mock_engine()` allocates `struct mock_engine`, fills `base` fields, installs context/request/scheduler/reset callbacks, registers it in `gt->engine` and `gt->engine_class`, initializes a spinlocked fake hardware queue and timer, and marks the engine as user-visible. `mock_engine_init()` creates the mock scheduler, initializes execlists/PM/retire support, allocates breadcrumbs, creates the kernel context, and points the engine status page at the kernel timeline HWSP. Request submission calls `i915_request_submit()`, queues the request on `hw_queue`, and either completes it immediately or arms `hw_delay`. `hw_delay_complete()` advances the first completed request and drains following zero-delay requests. Reset cancel marks scheduler and fake hardware queue requests as EIO and signals breadcrumbs.

State and persistence behavior: `struct mock_engine` extends `intel_engine_cs` with `hw_lock`, `hw_queue`, and `hw_delay`. Mock contexts allocate a software ring plus timeline; pinning maps timeline HWSP and pins the ring VMA. Requests carry `request->mock.link` and `request->mock.delay` state. Completion removes requests from `hw_queue`, marks fences complete, and signals breadcrumbs. Release tears down scheduler, breadcrumbs, kernel context, and retire state.

Dependencies and integration points: integrates with i915 request objects, timelines, rings, GGTT VMAs, scheduler engine, execlists initialization, PM wakerefs, breadcrumbs, and mock request infrastructure. It is used by selftests that need request ordering and retirement behavior without hardware.

Risks: this engine approximates hardware behavior and can hide timing, reset, forcewake, cache, and command-stream issues. There is a suspicious error path in `mock_context_alloc()` that frees `ce->engine` if `intel_timeline_create()` fails; this is unusual for an allocation callback and worth reviewing against ownership expectations. Locking in `mock_remove_from_engine()` handles virtual engine engine-pointer instability, but mistakes around request engine changes could race. Timer cancellation must stay synchronized with queue mutation.

Test signals: mock selftests exercise construction, submission, flush, reset cancellation, request completion, breadcrumbs, and context cleanup. Failures typically appear as stuck requests, unexpected EIO, lockdep warnings, or use-after-free in mock-only CI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/mock_engine.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/mock_engine.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/mock_engine.h

Purpose: declares the mock i915 engine type and its public construction/control functions for selftests.

Important APIs/types: `struct mock_engine` embeds `struct intel_engine_cs base` and adds `hw_lock`, `hw_queue`, and `hw_delay`. Public functions are `mock_engine()`, `mock_engine_init()`, `mock_engine_flush()`, `mock_engine_reset()`, and `mock_engine_free()`.

Control flow: no executable flow in the header. Consumers create an engine with `mock_engine()`, initialize it with `mock_engine_init()`, flush queued fake work, reset as needed, and free via the declared cleanup hook.

State and persistence behavior: the embedded base object lets mock engines be passed anywhere an `intel_engine_cs` is expected. The added queue/timer state persists pending fake hardware work between submission and completion.

Dependencies and integration points: includes Linux list/spinlock/timer primitives and `gt/intel_engine.h`, making it part of the i915 GT test harness. It bridges generic engine code and mock-specific queue simulation.

Risks: the header declares `mock_engine_free()` but the inspected C file does not define it, so either another object provides it or the declaration is stale. Because `struct mock_engine` is layout-visible, changes must remain aligned with `container_of()` uses in the implementation.

Test signals: compile/link coverage validates the declared API. Mock selftests exercise the queue/timer fields and embedded base compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/mock_engine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_context.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_context.c

Purpose: provides live i915 selftests for GPU context size accounting, active context lifetime, idle barriers, and remote context activity tracking.

Important APIs/functions: entry point `intel_context_live_selftests()` runs `live_context_size`, `live_active_context`, and `live_remote_context`. Helpers include `request_sync()`, `context_sync()`, `__live_context_size()`, `__live_active_context()`, `__remote_sync()`, and `__live_remote_context()`.

Control flow: `request_sync()` manually commits and queues a request while retaining timeline lock context, then waits and retires it. `live_context_size()` iterates engines, hides default state, extends `engine->context_size` by one page, poisons a redzone at the end of the context state object, submits a request, forces a context switch with a kernel request, and checks that hardware did not write into the redzone. `live_active_context()` disables heartbeat, submits repeated requests on a context, verifies the context remains active after request completion until idle barriers run, flushes barriers, waits for kernel context synchronization, and confirms the engine parks. `live_remote_context()` verifies that `intel_context_prepare_remote_request()` remote fences do not clobber idle-barrier activity tracking.

State and persistence behavior: tests create temporary contexts, map context state objects, alter heartbeat intervals, temporarily modify `engine->default_state`, and use `ce->active` as the persistence signal for lifetime protection. All changes are restored or released on exit paths.

Dependencies and integration points: depends on `intel_engine_heartbeat`, `intel_engine_pm`, GT live subtest harness, request/timeline locking, mock context helpers, and `igt_flush_test()`. GuC submission paths skip idle-barrier assumptions because GuC signals safe unpin differently.

Risks: these tests intentionally perturb engine context size and heartbeat settings; cleanup must run even on errors. Redzone checks overlap execlists debugging behavior and assume mapped context state is coherent enough for CPU inspection. Short waits can be sensitive to very slow or wedged hardware.

Test signals: failures report redzone corruption, missing active context barriers, engines staying awake after idle barriers, or remote context activity becoming idle too early. The entry point skips work when the GT is wedged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_engine.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_engine.c

Purpose: acts as the top-level live engine selftest dispatcher for the i915 GT engine PM tests.

Important APIs/functions: `intel_engine_live_selftests()` iterates a NULL-terminated function table currently containing `live_engine_pm_selftests()`.

Control flow: the entry point obtains the primary GT with `to_gt(i915)`, calls each registered engine-level live selftest function in order, and returns immediately on the first error.

State and persistence behavior: this file owns no persistent state. It only sequences tests that may manipulate GT or engine state internally.

Dependencies and integration points: includes `i915_selftest.h` and `selftest_engine.h`. It is part of the i915 selftest registration surface and bridges drm device-private state to GT-oriented test functions.

Risks: the simple dispatcher means a failure in an early registered suite prevents later suites from running. Adding tests here changes live selftest ordering and may affect CI runtime or state contamination between suites.

Test signals: pass/fail is the return value from `live_engine_pm_selftests()`, with no additional logging in this wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_engine.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_engine.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_engine.h

Purpose: declares the GT-scoped engine PM selftest entry point used by the engine selftest dispatcher.

Important APIs/types: forward-declares `struct intel_gt` and declares `int live_engine_pm_selftests(struct intel_gt *gt)`.

Control flow: none in the header.

State and persistence behavior: none directly; the declared function runs tests that manipulate engine PM state.

Dependencies and integration points: included by `selftest_engine.c` and `selftest_engine_pm.c` to keep the selftest interface small.

Risks: prototype mismatch would break compilation. The header deliberately avoids pulling heavy GT internals into the dispatcher.

Test signals: compile coverage only; runtime signals come from `selftest_engine_pm.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_engine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_engine_cs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_engine_cs.c

Purpose: implements engine command-stream performance and structural mock selftests for batch-buffer start, large NOP execution, and engine MMIO base table ordering.

Important APIs/functions: live performance entry `intel_engine_cs_perf_selftests()` runs `perf_mi_bb_start` and `perf_mi_noop`. Mock entry `intel_engine_cs_mock_selftests()` runs `intel_mmio_bases_check`. Helpers include `perf_begin()`, `perf_end()`, `timestamp_reg()`, `write_timestamp()`, `create_empty_batch()`, `create_nop_batch()`, `trifilter()`, and `cmp_u32()`.

Control flow: performance tests force GT PM on, boost RPS by incrementing `gt->rps.num_waiters`, and iterate engines with command-stream timestamps. `perf_mi_bb_start()` times an empty batch buffer jump by storing timestamps before and after `emit_bb_start()`. `perf_mi_noop()` subtracts empty-batch overhead from execution of a 64 KiB NOP batch. Both collect five samples and use a weighted median-style filter before logging cycles. The mock MMIO-base test walks `intel_engines[]`, validates that `graphics_ver` entries decrease monotonically, stops at version 0, and rejects zero base addresses for real entries.

State and persistence behavior: temporary internal GEM objects and VMAs are created, pinned, synchronized, and released. Performance setup temporarily increases RPS waiters and holds a GT wakeref, then restores both through `perf_end()`.

Dependencies and integration points: uses i915 command emission, GGTT/user VMA pinning, timestamp registers, engine `emit_bb_start`, RPS workqueue, GT PM, and the global static engine info table. It skips unsupported engines on pre-Gen7 except RCS0.

Risks: performance numbers are informational but still require request completion; slow hardware can trip waits. Timestamp register selection differs for Gen5/G4X. Object/VMA cleanup paths must release pins after partial failures. The MMIO-base check compares table shape rather than live hardware behavior.

Test signals: `pr_info()` logs MI_BB_START and 16K MI_NOOP cycles per engine. Failures return allocation/pinning errors, EIO on request timeout/flush failure, or `-EINVAL` for malformed MMIO base metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_engine_cs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_engine_heartbeat.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_engine_heartbeat.c

Purpose: tests and exposes helper controls for i915 engine heartbeat behavior, especially idle-barrier flushing, manual pulse behavior, and disabling heartbeat without leaving scheduled work behind.

Important APIs/functions: entry point `intel_heartbeat_live_selftests()` runs `live_idle_flush`, `live_idle_pulse`, and `live_heartbeat_off`. Exported test helpers are `st_engine_heartbeat_disable()`, `st_engine_heartbeat_enable()`, `st_engine_heartbeat_disable_no_pm()`, and `st_engine_heartbeat_enable_no_pm()`. Internal helpers include `reset_heartbeat()`, `timeline_sync()`, `engine_sync_barrier()`, `pulse_create()`, `pulse_unlock_wait()`, and `__live_idle_pulse()`.

Control flow: idle pulse tests create a temporary `pulse` object with `i915_active`, preallocate/acquire an idle barrier on an awake engine, call either `intel_engine_flush_barriers()` or `intel_engine_pulse()`, verify barrier tasks were consumed, synchronize via the kernel timeline, and confirm the active object retires. `live_heartbeat_off()` gets an engine wakeref, verifies heartbeat delayed work is running, calls `intel_engine_set_heartbeat(engine, 0)`, flushes delayed work, checks that work and systole state are gone, and restores the default interval.

State and persistence behavior: tests temporarily force hangcheck high, disable/re-enable heartbeat intervals, hold engine PM references, and use a refcounted `pulse` object whose `i915_active` callback retains the object until retirement. The no-PM disable helper parks heartbeat only if the engine is already awake to avoid making engines appear busy.

Dependencies and integration points: integrates with `intel_engine_heartbeat`, GT request synchronization, active barrier infrastructure, delayed work, heartbeat properties/defaults, PM wakerefs, and GT live selftest harness.

Risks: heartbeat interval changes must always be restored or later tests may run without heartbeat coverage. Idle-barrier assumptions depend on non-wedged engines and correct kernel context timeline progress. Tests that hold PM refs can affect idle detection if cleanup fails.

Test signals: failures print missing heartbeat pulse, unflushed idle tasks, heartbeat still running/allocated after disable, or timeout waiting for kernel timeline progress. The suite skips wedged GTs and ignores `-ENODEV` from pulse on unsupported engines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_engine_heartbeat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_engine_heartbeat.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_engine_heartbeat.h

Purpose: declares heartbeat control helpers shared by i915 live selftests that need to suppress or restore heartbeat behavior around timing-sensitive scenarios.

Important APIs/types: forward-declares `struct intel_engine_cs` and declares `st_engine_heartbeat_disable()`, `st_engine_heartbeat_disable_no_pm()`, `st_engine_heartbeat_enable()`, and `st_engine_heartbeat_enable_no_pm()`.

Control flow: none in the header; implementations adjust heartbeat interval and optionally engine PM state.

State and persistence behavior: callers rely on these helpers to preserve and restore heartbeat behavior using engine defaults. The `_no_pm` variants are intended for tests that cannot take a PM reference just to disable heartbeat.

Dependencies and integration points: included by execlists, engine PM, and heartbeat selftests to coordinate heartbeat suppression during spinners, timeslicing, and reset scenarios.

Risks: callers must pair disable and enable variants correctly. Mixing PM and no-PM variants can leave wakeref accounting or heartbeat interval state inconsistent.

Test signals: compile coverage plus runtime evidence from all live selftests that use heartbeat suppression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_engine_heartbeat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_engine_pm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_engine_pm.c

Purpose: implements live selftests for engine timestamp correctness, busy-time accounting, and engine PM wakeref behavior under atomic contexts.

Important APIs/functions: public entry `live_engine_pm_selftests()` runs `live_engine_timestamps`, `live_engine_busy_stats`, and `live_engine_pm`. Helpers include `emit_wait()`, `emit_store()`, `emit_srm()`, `write_semaphore()`, `__measure_timestamps()`, `__live_engine_timestamps()`, `__spin_until_busier()`, and `trifilter()`.

Control flow: timestamp tests emit a request that signals a CPU semaphore, waits, stores ring and context timestamps before/after a controlled busy window, then compares GPU deltas with wall-clock time and with each other. Busy-stat tests measure near-zero busyness while idle, run an `igt_spinner` request to force 100% busy, optionally wait for GuC busyness propagation, and assert measured busy time is within tolerance. The PM test iterates `igt_atomic_phases`, takes a normal engine PM ref, then from atomic context tests `intel_engine_pm_get_if_awake()` and `intel_engine_pm_put_async()`, flushes PM, and checks the engine/GT return idle.

State and persistence behavior: uses engine status page slots as temporary semaphores/timestamp storage. Temporarily disables heartbeat around timestamp and busy-stat tests. Manipulates engine PM references and GT idle state, but should leave GT idle after each phase. The spinner is initialized once and ended after each engine.

Dependencies and integration points: depends on MI semaphore/store/SRM commands, timestamp registers, GT clock conversion helpers, GuC busy-time behavior, RPS/PM infrastructure, atomic selftest phases, spinner library, and heartbeat selftest helpers.

Risks: timing tolerances can be sensitive to virtualization, slow scheduling, or inaccurate `gt->clock_frequency`. Busy stats differ under GuC because accounting may update after workload start. CPU semaphore polling disables preemption/interrupts in tight windows, so tests should remain short. Cleanup must end spinners and re-enable heartbeat on errors.

Test signals: logs elapsed, CTX_TIMESTAMP, and RING_TIMESTAMP values; reports mismatch when deltas fall outside 25% tolerance. Busy-stat failures report idle busyness or busy percentage outside expected bounds. PM failures show failed `get_if_awake()`, engines still awake, or GT failing to idle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_engine_pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_execlists.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_execlists.c

Purpose: contains the main live selftest suite for execlists submission. It stresses logical ring contexts, lite-restore correctness, preemption, timeslicing, reset handling, cancellation, user-batch preemption, smoke scheduling, and virtual engine behavior.

Important APIs/functions: entry point `intel_execlists_live_selftests()` registers 28 subtests including `live_sanitycheck`, `live_unlite_switch`, `live_unlite_preempt`, `live_unlite_ring`, `live_pin_rewind`, `live_hold_reset`, `live_error_interrupt`, `live_timeslice_*`, `live_busywait_preempt`, `live_preempt*`, `live_nopreempt`, `live_chain_preempt`, `live_preempt_gang`, `live_preempt_user`, `live_preempt_smoke`, and `live_virtual_*`. Core helpers include `wait_for_submit()`, `wait_for_reset()`, semaphore queue builders, reset tasklet locking helpers, preempt client setup, smoke submission helpers, virtual sibling selection, and GPR test batch builders.

Control flow: the suite only runs when `submission_method == INTEL_SUBMISSION_ELSP` and the GT is not wedged. Early tests verify simple spinner execution and lite-restore/ring rewind edge cases by poisoning rings and forcing context switches or preemptions. Reset/error tests disable heartbeat, lock the reset tasklet, hold active execlists requests, inject bad commands, and confirm guilty requests receive `-EIO` while normal requests progress. Timeslice tests build semaphore chains, force short timeslices, verify rewind ordering, ensure queued high-priority work can slice in, and check no-preempt requests are not bypassed.

Preemption tests create low/high priority contexts and spinners, verify immediate and late preemption, suppress preemption for flagged requests, cancel active/queued/hostile requests through context banning and pulses, force reset-timeout fallback, avoid unnecessary self-preempt injection, preempt across long dependency chains, check ring rollback with small rings, and build priority gangs where higher priority batches release lower priority batches. User-batch preemption uses GPR increments and repeated kernel preemptions to prove instruction execution resumes at the current point instead of replaying from the start. Smoke tests submit many requests across contexts/engines with ordered and random priorities, with and without a batch full of `MI_ARB_CHECK`.

Virtual engine tests wrap physical engines in virtual contexts, measure request latency, enforce `execution_mask` routing, verify virtual requests timeslice in and out, check CS_GPR state preservation when a virtual context migrates between siblings, and test reset flow when a virtual request is active on a physical engine. Most scenarios use `igt_live_test_begin/end()` plus `igt_flush_test()` to detect hangs and leaked GPU state.

State and persistence behavior: the tests heavily mutate temporary context state, request priorities, engine timers, heartbeat intervals, preempt/reset timeout knobs, engine status page slots, GGTT scratch buffers, and virtual execution masks. Persistent driver state should be restored after each subtest: heartbeat re-enabled, spinners ended, contexts closed, VMAs unpinned, requests put, and timeout fields reset. The only intended lasting state on severe failures is wedging the GT to stop further unsafe execution.

Dependencies and integration points: depends on execlists internals (`pending`, `active`, timers, tasklet, hold/unhold, unwind), scheduler priority APIs, reset paths, heartbeat helpers, request fences, logical ring contexts, semaphores, MI commands, GGTT VMAs, spinner and random selftest libraries, virtual engine creation, and i915 live-test/flush infrastructure. It explicitly skips GuC submission for virtual-engine execlists assumptions and skips unsupported capabilities such as preemption, timeslicing, store-dword, or reset.

Risks: this file intentionally drives hardware into hangs, preemption failures, and reset paths; incorrect cleanup can leave heartbeat disabled, timers altered, requests referenced, or the GT wedged. Many tests use tight timeouts and direct execlists internals, so behavior may be sensitive to scheduler latency, virtualization, or platform-specific feature availability. Poisoned rings and invalid commands are safe only inside guarded live-test windows. Because tests inspect internal request order and GPR preservation, backend changes can require careful updates.

Test signals: success is measured by spinner start/completion, expected request errors, request wait deadlines, ordering of timestamp/GPR scratch values, lack of unexpected preempt hang counters, virtual request execution on expected engines, and clean `igt_live_test_end()` / `igt_flush_test()` results. Failures print engine dumps, trace dumps, and often wedge the GT to prevent cascading damage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_execlists.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_gt_pm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_gt_pm.c

Purpose: implements GT-level power-management live selftests for CS clock calibration, RC6/RPS suites, suspend/resume restore, and late RC6 context-workaround checks.

Important APIs/functions: entry points are `intel_gt_pm_live_selftests()` and `intel_gt_pm_late_selftests()`. Local helpers include `read_timestamp()`, `measure_clocks()`, `live_gt_clocks()`, and `live_gt_resume()`. The suite delegates to `live_rc6_manual`, multiple `live_rps_*` tests, and `live_rc6_ctx_wa` from included selftest headers.

Control flow: `live_gt_clocks()` skips unknown clock frequencies and pre-Gen4 devices, takes a GT wakeref, forces all uncore domains awake, measures engine timestamp deltas over five 1 ms windows with interrupts disabled, converts between GT clock ticks and nanoseconds, and checks both conversion directions within tolerance. `live_gt_resume()` loops until the IGT timeout, running suspend prepare/late, checking RC6 disabled during suspend, resuming GT, checking RC6 restored when supported, and verifying LLC state restoration. Live and late entry points skip wedged GTs and run ordered subtest arrays.

State and persistence behavior: temporarily holds GT PM and uncore forcewake. Suspend/resume test intentionally transitions GT power state and may call `intel_gt_set_wedged_on_init()` on serious restore failures. Late tests are marked as potentially leaving the system undesirable and are intended to run last.

Dependencies and integration points: depends on engine timestamp registers, GT clock conversion helpers, uncore forcewake, GT suspend/resume, RC6/RPS/LLC selftest modules, and i915 live subtest harness.

Risks: clock tests rely on stable `gt->clock_frequency` and CPU timing; inaccurate calibration can produce false failures. Suspend/resume cycling is invasive and can expose or cause broader GT state issues. Late RC6 tests may leave the system in a bad state, so test ordering matters.

Test signals: clock tests log cycles and nanoseconds per engine and fail if CS ticks diverge from wall time beyond tolerance. Resume tests fail if RC6 state is wrong or LLC verification fails. Subordinate RC6/RPS tests provide their own diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_gt_pm.c -->
