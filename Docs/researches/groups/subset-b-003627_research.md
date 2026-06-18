# Research: subset-b-003627

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_runtime_pm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_runtime_pm.c

Purpose: Implements i915's device-level runtime PM wakeref API over Linux `pm_runtime`, including debug ref tracking, display-interface adapters, autosuspend policy, and driver load/unload ownership handoff. It is the common guard for code that may touch graphics hardware while the PCI device can runtime-suspend into D3.

Important APIs/functions: `intel_runtime_pm_get()`, `intel_runtime_pm_get_raw()`, `intel_runtime_pm_get_if_in_use()`, `intel_runtime_pm_get_if_active()`, `intel_runtime_pm_get_noresume()`, `intel_runtime_pm_put()`, `intel_runtime_pm_put_raw()`, `intel_runtime_pm_put_unchecked()`, `intel_runtime_pm_enable()`, `intel_runtime_pm_disable()`, `intel_runtime_pm_driver_release()`, `intel_runtime_pm_driver_last_release()`, and `intel_runtime_pm_init_early()`. The file also exports `i915_display_rpm_interface`, adapting the same operations to `struct intel_display_rpm_interface`.

Control flow: get paths call into `pm_runtime_get_sync()` or conditional `pm_runtime_get_if_*()` first, then update `rpm->wakeref_count` through `intel_runtime_pm_acquire()`. Put paths untrack any debug cookie, update the biased wakeref counter through `intel_runtime_pm_release()`, mark the device last busy, and call `pm_runtime_put_autosuspend()`. Conditional gets return `NULL` when the device is inactive or unused. Enable configures no-direct-complete, autosuspend delay, autosuspend usage, runtime PM allow policy for non-dgfx, and drops the load-time core reference; disable reacquires ownership from the core and disables autosuspend.

State/persistence: `rpm->wakeref_count` combines raw wakerefs and biased wakelock refs. Under `CONFIG_DRM_I915_DEBUG_RUNTIME_PM`, `rpm->debug` tracks live wakeref cookies and prints outstanding refs when the counter reaches zero unexpectedly. `rpm->available` decides whether runtime PM is truly available or a permanent reference must be kept. Early init wires `rpm->kdev`, initializes lmem userfault tracking state, and initializes the automatic userfault wakeref.

Dependencies/integration: Depends on Linux runtime PM, PCI device plumbing, i915 debug/ref-tracker helpers, `intel_wakeref_auto`, and display parent RPM interface. The API is consumed by GEM, GT, display, PXP, uncore, and selftests before register access or memory-management paths that require the device to be powered.

Risks: Mismatched get/put calls leak device power or drop power while hardware is accessed. Raw refs bypass wakelock assertions and should stay limited to recovery/error paths. Conditional gets must not be followed by MMIO on failure. The non-dgfx-only `pm_runtime_allow()` policy and dgfx autosuspend suppression make platform behavior intentionally asymmetric. Debug ref tracking is compiled out in normal builds, so correctness still relies on API symmetry.

Test signals: Runtime PM debug warnings report suspended-device access and wakeref leaks. Related selftests exercise suspend/hibernate paths and use `with_intel_runtime_pm()` guards. Failures often appear as RPM wakelock/raw-wakeref warnings, leaked counts at `driver_release`, or MMIO access while suspended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_runtime_pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_runtime_pm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_runtime_pm.h

Purpose: Declares the runtime PM state object, wakeref counting model, assertion helpers, public get/put API, and scoped `with_intel_runtime_pm*` macros used throughout i915.

Important APIs/types: `struct intel_runtime_pm` holds `wakeref_count`, `kdev`, availability flags, lmem userfault list/lock, `userfault_wakeref`, and optional debug tracker. Counter helpers `intel_rpm_raw_wakeref_count()` and `intel_rpm_wakelock_count()` decode the biased atomic. Assertions include `assert_rpm_device_not_suspended()`, `assert_rpm_raw_wakeref_held()`, and `assert_rpm_wakelock_held()`. Temporary assertion bypass helpers are `disable_rpm_wakeref_asserts()` and `enable_rpm_wakeref_asserts()`.

Control flow: Header macros provide for-loop scoped acquisition/release wrappers for unconditional, in-use, and active-only runtime PM references. In non-debug builds, `intel_runtime_pm_put()` is an inline wrapper around unchecked put; in debug builds it requires the tracked wakeref cookie.

State/persistence: The lower half of `wakeref_count` tracks raw refs while the upper half tracks wakelock refs by adding `INTEL_RPM_WAKELOCK_BIAS`. This allows single-atomic assertions for both "device must be on" and "caller holds a wakelock-class ref." `no_wakeref_tracking` can disable debug tracking without disabling runtime PM itself.

Dependencies/integration: Includes `intel_wakeref.h` and Linux runtime PM. Display code receives `i915_display_rpm_interface` from the implementation file. Any caller that touches hardware must use these APIs or display power-domain equivalents.

Risks: The bypass helpers artificially add/subtract both raw and wakelock counts, so imbalance can hide real missing refs. `get_noresume()` is only valid when an active wakeref is already held. The raw accessors intentionally avoid wakelock assertion coverage and increase misuse risk.

Test signals: Assertions warn on suspended-device access or missing refs. Debug builds can print active ref trackers through `print_intel_runtime_pm_wakeref()`. Suspend/resume selftests and runtime PM paths are the main coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_runtime_pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_step.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_step.c

Purpose: Converts PCI revision IDs or GMD IP step fields into normalized Intel graphics/media stepping values stored in runtime info.

Important APIs/functions: `intel_step_init()` selects a platform-specific revision table or GMD-based conversion, then writes `RUNTIME_INFO(i915)->step`. `intel_step_name()` returns printable step names. `gmd_to_intel_step()` maps GMD step numbers onto the `STEP_A0`-based enum and clamps future values to `STEP_FUTURE`.

Control flow: If `HAS_GMD_ID(i915)` is true, graphics and media IP step fields are converted directly. Otherwise `intel_step_init()` selects one of many static `intel_step_info` tables for SKL/KBL/BXT/GLK/ICL/JSL/EHL/TGL/RKL/DG1/ADL/RPL/DG2 variants. Unknown gaps warn, then use the next non-empty table entry if possible; out-of-range values become future graphics stepping.

State/persistence: No persistent allocations. The only state mutation is `RUNTIME_INFO(i915)->step`. Static tables encode platform knowledge and preserve unusual non-monotonic revision-to-step mappings.

Dependencies/integration: Depends on platform detection macros, PCI revision via `INTEL_REVID()`, `drm_warn/drm_dbg`, and `drm/intel/step.h` enum values. Other i915 workarounds and feature gates use normalized stepping.

Risks: Missing or stale table entries can select incorrect workarounds. Gap fallback may be wrong for non-monotonic stepping tables, but avoids defaulting to zero. `gmd_to_intel_step()` assumes four numeric steps per letter as documented in the header.

Test signals: Boot logs show warnings for unknown revisions and debug messages for fallback/future steppings. Coverage is mostly platform bring-up and workaround selection behavior rather than standalone unit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_step.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_step.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_step.h

Purpose: Defines the normalized stepping data structure and public stepping helpers.

Important APIs/types: `struct intel_step_info` has `graphics_step` and `media_step`, where graphics represents the compute tile on Xe HPC. Exports `intel_step_init()` and `intel_step_name()`.

Control flow: None in the header beyond declarations. The comment establishes the numeric convention that GMD step conversion relies on: four numeric steps per letter.

State/persistence: No state. It describes the shape of `RUNTIME_INFO(i915)->step` values written by the implementation.

Dependencies/integration: Includes Linux types and `drm/intel/step.h` for `enum intel_step`. Consumed by platform init and code that prints or compares hardware stepping.

Risks: Any enum-layout change in `drm/intel/step.h` that violates the four-steps-per-letter assumption would break GMD conversion.

Test signals: Build-time type checking and runtime unknown-revision warnings from `intel_step.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_step.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_uncore.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_uncore.c

Purpose: Implements i915 uncore MMIO access, forcewake domain management, platform forcewake/shadow-register tables, unclaimed-MMIO detection, MMIO mapping, runtime/system suspend forcewake sanitization, and register wait helpers.

Important APIs/functions: Public entry points include `intel_uncore_setup_mmio()`, `intel_uncore_init_early()`, `intel_uncore_init_mmio()`, `intel_uncore_fini_mmio()`, `intel_uncore_suspend()`, `intel_uncore_resume_early()`, `intel_uncore_runtime_resume()`, `intel_uncore_forcewake_get/put/put_delayed/flush()`, locked forcewake variants, `intel_uncore_forcewake_user_get/put()`, `intel_uncore_forcewake_for_reg()`, `__intel_wait_for_register()` and `_fw`, `intel_uncore_unclaimed_mmio()`, and `intel_uncore_arm_unclaimed_mmio_detection()`.

Control flow: Init maps MMIO, sanity-checks BAR access, checks dgfx LMEM init, selects raw or forcewake-aware MMIO function tables, initializes forcewake domains, sanitizes forcewake state, assigns per-platform forcewake and shadow tables, and arms unclaimed-MMIO flags. Read/write wrappers assert runtime PM, optionally lock `uncore->lock`, check unclaimed accesses, derive needed forcewake domains from sorted tables, automatically forcewake inactive domains, perform raw reads/writes, and emit tracepoints. Forcewake get increments per-domain `wake_count` and sends register requests for newly active domains; put decrements and either clears immediately or arms a high-resolution delayed release timer.

State/persistence: `struct intel_uncore` owns MMIO base, function pointers, forcewake domains, domain timers, active/timer/saved bitmasks, FIFO count, debug state, PMIC bus notifier, and platform flags. Forcewake domains are dynamically allocated and freed. Runtime and S3 paths save/restore active user forcewake domains through `fw_domains_saved`. Unclaimed-MMIO debugging stores suspend nesting and one-shot counters in `intel_uncore_mmio_debug`.

Dependencies/integration: Integrates with runtime PM assertions, GT engine masks, IOSF PUNIT/PMIC bus arbitration, platform macros, GSC/media GT type, vGPU detection, DRM managed cleanup, i915 register definitions, wait helpers, selftests, and `intel_uncore_trace` tracepoints. PXP, GT, display, GEM, and interrupt code all depend on these MMIO accessors.

Risks: Forcewake table gaps or unsorted ranges can cause MMIO while power wells are off. Shadow table mistakes can avoid required forcewake for writes. Timer and wake-count imbalance can leave domains stuck on or prematurely off. PMIC notifier forcewake happens without a normal RPM wakeref and depends on temporary assertion bypass. BAR reads of all ones indicate catastrophic MMIO loss. Driver-initiated FLR on fini is destructive and intentionally only done as a final teardown action.

Test signals: Includes selftests under `CONFIG_DRM_I915_SELFTEST`, especially forcewake/shadow table validation in `selftests/intel_uncore.c`. Runtime evidence includes unclaimed-MMIO warnings, forcewake ack timeouts, FIFO debug messages, MMIO `0xffffffff` detection, and register tracepoints. Suspend/resume paths exercise forcewake reset and restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_uncore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_uncore.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_uncore.h

Purpose: Defines the uncore data model and inline MMIO API used by i915 code to access registers safely across power-gated GT/media/GSC domains.

Important APIs/types: `struct intel_uncore`, `struct intel_uncore_funcs`, `struct intel_uncore_fw_get`, `struct intel_forcewake_range`, `struct intel_uncore_mmio_debug`, forcewake domain enums and bitmasks, raw accessors `__raw_uncore_read/write*`, traced accessors `intel_uncore_read/write*`, untraced accessors, `_fw` raw critical-section accessors, forcewake APIs, register wait helpers, `intel_uncore_rmw()`, `intel_uncore_rmw_fw()`, `intel_uncore_read64_2x32()`, and `raw_reg_read/write()`.

Control flow: Inline read/write functions dispatch through `uncore->funcs`, which the C file initializes based on platform and forcewake requirements. Raw helpers apply `gsi_offset` for GSI registers below `0x40000`. `intel_uncore_read64_2x32()` locks uncore, forcewakes both halves, and retries upper/lower reads to reduce rollover races.

State/persistence: The header lays out persistent uncore state: MMIO base, GT/runtime PM pointers, forcewake tables, shadow tables, timers, active counts, user forcewake count, FIFO count, and debug flags. The `UNCORE_NEEDS_FLR_ON_FINI` flag persists teardown policy until `intel_uncore_fini_mmio()`.

Dependencies/integration: Includes Linux locking/timer/io helpers and i915 register definitions. Used almost everywhere hardware registers are touched. The locked `_fw` accessors are intended for IRQ/critical sections where callers explicitly manage serialization and forcewake.

Risks: Raw and `_fw` helpers bypass normal tracing, forcewake acquisition, and some safety checks; callers must hold the right locks and domains. 64-bit writes are explicitly unsupported due to 32-bit split-write hazards. `raw_reg_read/write()` does not apply `gsi_offset`, so GSI users must compensate manually.

Test signals: Compile-time coverage through inline use, runtime warnings from implementation assertions, and selftest validation for forcewake/shadow behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_uncore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_uncore_trace.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_uncore_trace.c

Purpose: Instantiates the uncore MMIO tracepoints declared in `intel_uncore_trace.h`.

Important APIs/functions: Defines `CREATE_TRACE_POINTS` before including the trace header, guarded out for `__CHECKER__`.

Control flow: No runtime control flow beyond tracepoint definition emission at compile time.

State/persistence: No state. It creates tracepoint metadata and hooks for the kernel tracing subsystem.

Dependencies/integration: Depends directly on `intel_uncore_trace.h`; MMIO read/write wrappers in `intel_uncore.c` call `trace_i915_reg_rw()`.

Risks: Incorrect include guards or trace include path would break tracepoint generation. The checker guard avoids sparse issues.

Test signals: Build success and availability of `i915_reg_rw` trace events; runtime tracing verifies MMIO access logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_uncore_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_uncore_trace.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_uncore_trace.h

Purpose: Declares the `i915_reg_rw` trace event used for i915 MMIO reads and writes.

Important APIs/types: `TRACE_EVENT_CONDITION(i915_reg_rw, ...)` records write/read flag, register offset, value, access length, and a caller-provided `trace` condition. Trace include path/file metadata points back to the i915 trace header location.

Control flow: The trace event only emits when `trace` is true. Fast assignment converts `i915_reg_t` to offset and stores a 64-bit value so 8/16/32/64-bit reads can share the same event.

State/persistence: No driver state; trace records are transient in ftrace/perf buffers.

Dependencies/integration: Includes `i915_reg_defs.h`, Linux tracepoint headers, and is included by `intel_uncore.c` accessors and `intel_uncore_trace.c` for instantiation.

Risks: Tracepoints can expose high-volume MMIO traffic and should remain conditionally controlled. Format assumes values can be represented as two 32-bit halves.

Test signals: Enabled kernel tracing should show formatted `read/write reg=..., len=..., val=...` events for traced uncore accessors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_uncore_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_wakeref.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_wakeref.c

Purpose: Implements a higher-level wakeref object that wraps runtime PM with first-user/last-user callbacks, async or delayed release, idle waiting, automatic autosuspend extension, and debug ref printing.

Important APIs/functions: `__intel_wakeref_get_first()`, `__intel_wakeref_put_last()`, `__intel_wakeref_init()`, `intel_wakeref_wait_for_idle()`, `intel_wakeref_auto_init()`, `intel_wakeref_auto()`, `intel_wakeref_auto_fini()`, and `intel_ref_tracker_show()`.

Control flow: First acquisition takes an i915 runtime PM wakeref, locks the wakeref mutex, stores the runtime cookie, calls `ops->get()`, and increments the active count. Last put either schedules delayed work when async/contended or calls `ops->put()` under the mutex; only a successful put releases the stored runtime PM wakeref. Delayed work rechecks the count before final put. `intel_wakeref_auto()` extends an existing RPM wakeref using a timer and refcount balancing.

State/persistence: `struct intel_wakeref` holds atomic count, mutex, stored RPM wakeref cookie, callbacks, delayed work, and optional debug tracker. `struct intel_wakeref_auto` holds timer, wakeref cookie, spinlock, refcount, and i915 pointer. Timer/delayed-work state persists until idle/fini.

Dependencies/integration: Depends on `intel_runtime_pm`, i915 workqueues, ref trackers, wait-bit helpers, and callback users such as GT/display subsystems that need park/unpark semantics.

Risks: Callback failure intentionally retains runtime PM until a later retry; callback implementations must reschedule release on deferral. Async put paths must not race with new gets. `intel_wakeref_auto()` assumes the caller already holds an RPM wakelock and only extends an active wakeref. Debug `BUG_ON` behavior differs between debug and normal builds.

Test signals: `intel_wakeref_wait_for_idle()` provides synchronization for tests and teardown. Ref tracker dumps report leaks. Runtime PM cleanup warnings can reveal leaked auto wakerefs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_wakeref.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_wakeref.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_wakeref.h

Purpose: Declares wakeref abstractions for refcounted runtime-PM-backed resource lifetime management and debug tracking.

Important APIs/types: `intel_wakeref_t`, `struct intel_wakeref_ops`, `struct intel_wakeref`, `struct intel_wakeref_lockclass`, `struct intel_wakeref_auto`, `intel_wakeref_init()`, `intel_wakeref_get()`, `__intel_wakeref_get()`, `intel_wakeref_get_if_active()`, `intel_wakeref_put()`, `intel_wakeref_put_async()`, `intel_wakeref_put_delay()`, lock/unlock helpers, `intel_wakeref_is_active()`, `__intel_wakeref_defer_park()`, and ref-tracker helpers.

Control flow: Inline get fast path increments `count` if nonzero; first get delegates to the C implementation. Put fast path decrements unless count is one, in which case the C implementation handles last-release callbacks. Delay flags combine async bit and encoded delay. Lock helpers protect first/last callback execution.

State/persistence: `INTEL_WAKEREF_DEF` is a sentinel ref tracker cookie. Optional `CONFIG_DRM_I915_DEBUG_WAKEREF` tracking stores live holders in `wf->debug`. `intel_wakeref_auto` stores a temporary RPM wakeref until timer expiry or fini.

Dependencies/integration: Includes Linux atomic, lockdep, mutex, refcount, ref_tracker, timer, and workqueue APIs. The type is used by runtime PM and many i915 resource lifetime paths.

Risks: `__intel_wakeref_get()` is only valid when already active. `intel_wakeref_wait_for_idle()` waits for third-party holders too and must be used only when ownership is controlled. `__intel_wakeref_defer_park()` manipulates `count` directly and requires the mutex. Misencoded delay flags can corrupt put behavior.

Test signals: Debug ref tracking and leak reports; `i915_active` and other lifetime selftests indirectly cover callback and wait behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_wakeref.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp.c

Purpose: Top-level Protected Xe Path lifecycle and policy implementation: capability selection, backend setup, hardware enable/disable, session start/end orchestration, protected-object key validation, and invalidation of protected contexts after key loss.

Important APIs/functions: `intel_pxp_is_supported()`, `intel_pxp_is_enabled()`, `intel_pxp_is_active()`, `intel_pxp_init()`, `intel_pxp_fini()`, `intel_pxp_start()`, `intel_pxp_end()`, `intel_pxp_init_hw()`, `intel_pxp_fini_hw()`, `intel_pxp_get_readiness_status()`, `intel_pxp_get_backend_timeout_ms()`, `intel_pxp_key_check()`, `intel_pxp_invalidate()`, and `intel_pxp_mark_termination_in_progress()`.

Control flow: Init picks a control GT either for full protected content or a TEE link needed by HuC authentication. Full PXP creates session-management state, a pinned VCS context, and either a GSC-CS backend or a MEI TEE component backend. Start waits for firmware/backend readiness, drives a teardown/restart path if the arb session is invalid, then expects worker completion to recreate the session. End synchronously tears down the arb session, disables hardware, and drops RPM. Invalidation scans GEM contexts, bans protected-content contexts, and releases their PXP wakeref.

State/persistence: `i915->pxp` is allocated and freed here. `arb_is_valid`, `key_instance`, `platform_cfg_is_bad`, `termination`, `session_events`, `ce`, `ctrl_gt`, and `kcr_base` define persistent subsystem state. `key_instance` is incremented on new arb-session creation and is used to reject objects encrypted with stale keys.

Dependencies/integration: Integrates with GT engines, VCS pinned contexts, KCR registers, PXP IRQ/session/PM modules, GSC-CS backend, MEI TEE backend, HuC firmware dependencies, runtime PM, GEM context lists, and protected-content UAPI semantics.

Risks: Incorrect backend selection can expose unavailable PXP to userspace or break HuC loading. Session validity is software-tracked because hardware state may remain "in play" after keys are gone. Context invalidation races with execbuf are acknowledged and mitigated by fast banning. Readiness return values are UAPI-visible and must remain compatible.

Test signals: Debugfs `pxp/info`, PXP status GET_PARAM, protected-object execution failures (`-ENODEV`, `-ENOEXEC`), session timeout logs, and suspend/runtime PM paths that invalidate sessions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp.h

Purpose: Public PXP subsystem interface for i915 callers.

Important APIs/types: Declares capability predicates, init/fini, hardware init/fini, termination marking, readiness/status helpers, start/end, backend timeout, protected-object `intel_pxp_key_check()`, and `intel_pxp_invalidate()`.

Control flow: Header only declares calls; consumers use predicates to guard optional PXP behavior before protected-content operations.

State/persistence: No state, but functions operate on `struct intel_pxp` allocated in `i915->pxp`.

Dependencies/integration: Forward declares DRM GEM object, i915 private, and PXP types. Used by GEM object/context paths, PM paths, IRQ handling, debugfs, session code, and backends.

Risks: `intel_pxp_tee_end_arb_fw_session()` is declared here but implemented by the TEE backend, exposing a backend-specific finalization call at the top-level interface. Callers must distinguish supported, enabled, and active.

Test signals: Build coverage across PXP-enabled and disabled configurations, plus runtime protected-content tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_cmd.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_cmd.c

Purpose: Emits GPU batch commands to select and inline-terminate a PXP session on the PXP VCS context.

Important APIs/functions: `intel_pxp_terminate_session()` is the public command path. Helpers emit session selection (`MI_SET_APPID`, protected-memory `MI_FLUSH_DW`), inline `CRYPTO_KEY_EXCHANGE`, wait commands, and commit the request at max priority.

Control flow: Termination creates a request on `pxp->ce`, optionally emits init breadcrumb, reserves ring space for selection+termination+wait, advances the ring, commits/queues the request, waits up to `HZ/5`, and returns command or timeout errors. Disabled PXP returns success without doing work.

State/persistence: No persistent state except use of `pxp->ce` and request lifetime. The hardware session is affected by submitted commands.

Dependencies/integration: Depends on GT request/timeline/ring infrastructure, GPU command definitions, request tracing, and `intel_pxp_session.c` for higher-level teardown.

Risks: Ring-length constants must match emitted dwords. A failed or timed-out request leaves software marking the session invalid but may not complete hardware teardown. Commit bypasses normal caller priority by using `I915_PRIORITY_MAX`.

Test signals: Session teardown logs and timeouts from PXP suspend/restart/debugfs termination. Request tracing shows the termination batch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_cmd.h

Purpose: Declares the GPU command based PXP session termination API.

Important APIs/types: `intel_pxp_terminate_session(struct intel_pxp *pxp, u32 idx)`.

Control flow: None in header.

State/persistence: None.

Dependencies/integration: Forward declares `struct intel_pxp` and includes Linux types. Called by session teardown code.

Risks: API only terminates one indexed session; future multiple-session support would need broader command emission.

Test signals: Build linkage and PXP teardown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_cmd_interface_42.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_cmd_interface_42.h

Purpose: Defines PXP firmware wire formats for API 4.2 init-session and stream-key invalidation commands.

Important APIs/types: `PXP42_CMDID_INIT_SESSION`, `PXP42_CMDID_INVALIDATE_STREAM_KEY`, `struct pxp42_create_arb_in/out`, `struct pxp42_inv_stream_key_in/out`, and `PXP42_ARB_SESSION_MODE_HEAVY`.

Control flow: No code. Backends populate these packed structs before sending to MEI/GSC firmware.

State/persistence: Wire payloads carry session id, protection mode, stream id, and command status. No driver state.

Dependencies/integration: Includes common PXP command header. Used by TEE backend and by GSC-CS invalidation even when API version is set to 4.3.

Risks: Packed layout and reserved fields must match firmware ABI exactly. Wrong API version/command id causes platform config or protocol failures.

Test signals: Firmware command success/failure status in PXP init/invalidation logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_cmd_interface_42.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_cmd_interface_43.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_cmd_interface_43.h

Purpose: Defines PXP firmware API 4.3 command ids, maximum HECI sizes, HuC authentication payloads, and arb-session init payloads.

Important APIs/types: `PXP43_CMDID_START_HUC_AUTH`, `PXP43_CMDID_NEW_HUC_AUTH`, `PXP43_CMDID_INIT_SESSION`, `PXP43_MAX_HECI_INOUT_SIZE`, `PXP43_HUC_AUTH_INOUT_SIZE`, `pxp43_start_huc_auth_in`, `pxp43_new_huc_auth_in`, `pxp43_huc_auth_out`, `pxp43_create_arb_in/out`, and field masks for stream/session/protection flags.

Control flow: No code. GSC-CS and HuC paths fill these packed structs for firmware.

State/persistence: Payloads encode HuC DMA address/size, arb session id, app type, protection mode, and firmware status.

Dependencies/integration: Includes common command header and Linux size/page macros. Used by GSC-CS backend and HuC load/auth.

Risks: The max HECI size drives buffer allocation; mismatches risk truncation or `-ENOSPC`. Endianness differs between HuC address fields (`__le64` in one command, plain `u64` in another).

Test signals: GSC firmware reply status, HuC authentication result, and PXP session creation logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_cmd_interface_43.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_cmd_interface_cmn.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_cmd_interface_cmn.h

Purpose: Provides common PXP firmware ABI definitions shared by multiple API versions.

Important APIs/types: `PXP_APIVER()`, `enum pxp_status`, `struct pxp_cmd_header`, and stream id bit masks for session-valid, app-type, and session-id fields.

Control flow: None.

State/persistence: The packed header carries API version, command id, either status or stream id, and payload length excluding the header.

Dependencies/integration: Used by all PXP command-interface headers and both firmware backends.

Risks: Only status codes handled by the kernel are named; unknown codes must be logged and treated conservatively. ABI packing and bit masks must remain firmware-compatible.

Test signals: Backend error logs translate selected status codes to readable strings and set `platform_cfg_is_bad` for platform configuration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_cmd_interface_cmn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_debugfs.c

Purpose: Registers PXP debugfs controls for inspecting PXP state and forcing a termination event.

Important APIs/functions: `intel_pxp_debugfs_register()`, `pxp_info_show()`, and the `terminate_state` simple attribute setter.

Control flow: Registration creates `pxp/info` and `pxp/terminate_state` under DRM debugfs when PXP is supported. Reading `info` prints enabled/active state and key instance. Writing `terminate_state` simulates a termination interrupt under `gt->irq_lock`, then waits for the PXP termination completion with backend-specific timeout.

State/persistence: Does not own state; observes `arb_is_valid`, `key_instance`, and uses `termination` completion. The setter mutates session events through the IRQ handler.

Dependencies/integration: Uses debugfs, DRM seq printers, PXP IRQ/session state, and backend timeout helpers.

Risks: Debugfs termination intentionally disrupts protected sessions and invalidates contexts. It requires active PXP and may timeout if worker/backend completion fails.

Test signals: Manual debugfs reads and writes; `terminate_state` can exercise IRQ/session recovery without real hardware interrupt injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_debugfs.h

Purpose: Declares optional debugfs registration for PXP.

Important APIs/types: `intel_pxp_debugfs_register()` with a stub when `CONFIG_DRM_I915_PXP` is disabled.

Control flow: Header-only conditional compilation.

State/persistence: None.

Dependencies/integration: Used by i915 debugfs setup code.

Risks: Disabled-config stub means callers need not add extra ifdefs, but no debugfs diagnostics exist without PXP config.

Test signals: Build coverage in PXP/non-PXP configs and presence of debugfs files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_gsccs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_gsccs.c

Purpose: Implements the GSC command streamer backend for PXP firmware communication on platforms with a GSC engine.

Important APIs/functions: `intel_pxp_gsccs_init()`, `intel_pxp_gsccs_fini()`, `intel_pxp_gsccs_is_ready_for_sessions()`, `intel_pxp_gsccs_create_session()`, and `intel_pxp_gsccs_end_arb_fw_session()`. Internal core is `gsccs_send_message()` plus pending-retry wrapper.

Control flow: Init allocates and pins a large HECI packet VMA and a batch-buffer VMA, creates a GSC context using the GT VM, seeds a host session handle, then initializes PXP hardware under RPM. Message send builds a GSC MTL header, copies input into the packet buffer, submits a nonpriv HECI packet on the GSC engine, validates reply marker/status, handles pending replies by retrying with firmware's message handle, and copies bounded output. Fini sends cleanup for the host session handle, releases context and VMAs, and disables hardware under RPM.

State/persistence: `pxp->gsccs_res` stores host session handle, context, packet/batch VMAs, and CPU mappings. `platform_cfg_is_bad` is set on selected firmware statuses. Retry state is per message.

Dependencies/integration: Depends on GSC firmware/HECI submit helpers, GEM internal objects, i915 VMAs, GT GSC engine, PXP command ABI 4.2/4.3, runtime PM, and HuC/GSC readiness checks.

Risks: Buffer size calculations must include GSC headers and firmware maximums. Pending replies can take up to the configured retry budget. Cleanup messages with empty packets are special and must be sent before dropping resources. Firmware platform-config errors are persistent until reconfiguration. Mutex `tee_mutex` serializes this backend too, so long firmware waits block other PXP messaging.

Test signals: Logs for invalid validity marker, GSC reply status, pending timeout, session init/invalidate statuses, and readiness via HuC authenticated plus GSC proxy init done.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_gsccs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_gsccs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_gsccs.h

Purpose: Declares the GSC-CS PXP backend API and timeout constants.

Important APIs/types: `GSC_PENDING_RETRY_MAXCOUNT`, `GSC_PENDING_RETRY_PAUSE_MS`, `GSCFW_MAX_ROUND_TRIP_LATENCY_MS`, init/fini, session create/end, and readiness predicate. Stubs are provided when PXP is disabled.

Control flow: Header only; timeout macro combines base HECI reply latency with retry budget.

State/persistence: No state, but APIs operate on `pxp->gsccs_res`.

Dependencies/integration: Includes GSC HECI submit header for latency constants. Used by top-level PXP and PM/debugfs timeout logic.

Risks: Timeout constant influences user-visible readiness/termination waits; too short yields false timeout, too long delays suspend and debugfs operations. Disabled-config stubs return no readiness.

Test signals: Build across config variants and timeout behavior in PXP start/end paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_gsccs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_huc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_huc.c

Purpose: Sends HuC load/authentication requests through the PXP TEE streaming path for platforms where HuC is loaded by GSC via PXP.

Important APIs/functions: `intel_pxp_huc_load_and_auth()`.

Control flow: Verifies PXP and component availability, obtains HuC firmware object DMA address, builds a PXP 4.3 `START_HUC_AUTH` message, sends it through `intel_pxp_tee_stream_message()`, and accepts success or `PXP_STATUS_OP_NOT_PERMITTED` as benign when HuC may already survive resume.

State/persistence: Does not own state. Reads HuC firmware object and PXP component; firmware authentication state is updated externally by GSC/HuC logic.

Dependencies/integration: Depends on GEM DMA address helper, GT/HuC state, PXP TEE streaming, and PXP 4.3 command ABI.

Risks: Requires `pxp->pxp_component`, so it is tied to the MEI component backend. Incorrect DMA address or component absence fails HuC auth. Accepting OP_NOT_PERMITTED relies on later authentication-bit checks to catch real failures.

Test signals: HuC load/auth logs, GSC error status, and subsequent HuC authenticated state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_huc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_huc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_huc.h

Purpose: Declares the PXP-assisted HuC load/authentication helper.

Important APIs/types: `intel_pxp_huc_load_and_auth(struct intel_pxp *pxp)`.

Control flow: None.

State/persistence: None.

Dependencies/integration: Used by HuC/GSC loading paths through the TEE backend bind flow.

Risks: Header has no config stub, so callers must be in appropriate PXP-enabled build context.

Test signals: Build linkage and HuC authentication path results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_huc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_irq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_irq.c

Purpose: Handles KCR/PXP interrupt events and enables/disables PXP interrupt delivery.

Important APIs/functions: `intel_pxp_irq_handler()`, `intel_pxp_irq_enable()`, and `intel_pxp_irq_disable()`.

Control flow: IRQ handler requires `gt->irq_lock`, ignores empty IIR, marks termination in progress for terminated/app-terminated events, sets invalidation and event-source bits, records reset-complete events, and queues `session_work`. Enable resets stale GEN11_KCR IIR once, unmasks/enables GEN12 PXP interrupt bits, and sets `irq_enabled`. Disable requires PXP inactive, masks interrupts, synchronizes IRQs, resets IIR, and flushes session work.

State/persistence: Mutates `pxp->session_events`, `irq_enabled`, `arb_is_valid` via termination marking, and the `termination` completion state.

Dependencies/integration: Uses GT IRQ lock, GEN11/GEN12 interrupt registers, uncore MMIO, `intel_synchronize_irq()`, PXP session worker, and runtime PM-aware hardware init/fini.

Risks: Events are bit-accumulated under irq_lock and consumed asynchronously; missing locks can lose events. Disabling while active is warned because restart must force global termination after re-enable. Worker flushing during disable prevents stale session work after hardware teardown.

Test signals: Debugfs termination path simulates interrupt handling. Runtime logs show session event processing and termination completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_irq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_irq.h

Purpose: Declares PXP interrupt bits and optional IRQ helper APIs.

Important APIs/types: Interrupt bit macros for terminated, firmware-requested app termination, and reset complete; `GEN12_PXP_INTERRUPTS`; declarations/stubs for enable, disable, and handler.

Control flow: Header-only conditional compilation.

State/persistence: None.

Dependencies/integration: Used by PXP hardware init/fini, GT IRQ dispatch, debugfs, and session worker.

Risks: Interrupt bit definitions must match hardware KCR IIR layout. Disabled-config stubs make calls no-ops.

Test signals: Build across configs and interrupt-driven PXP recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_pm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_pm.c

Purpose: Provides PXP hooks for system suspend/resume and runtime suspend/resume.

Important APIs/functions: `intel_pxp_suspend_prepare()`, `intel_pxp_suspend()`, `intel_pxp_resume_complete()`, `intel_pxp_runtime_suspend()`, and `intel_pxp_runtime_resume()`.

Control flow: Suspend prepare ends active PXP synchronously and invalidates protected contexts. Suspend disables PXP hardware under RPM and clears invalidated flag. Resume initializes hardware either with an explicit wakeref after system resume or without one in runtime-resume context. TEE backend resume defers hardware init until component bind if the MEI component is not bound; GSC-CS backend can initialize directly.

State/persistence: Mutates `arb_is_valid` and `hw_state_invalidated`, and toggles hardware/IRQ state via init/fini. Protected contexts are invalidated during suspend prepare.

Dependencies/integration: Runtime PM, top-level PXP end/invalidate/init_hw/fini_hw, IRQ hooks, and backend component availability.

Risks: Runtime suspend declares the arb session invalid without full context invalidation here; correctness depends on higher-level sequencing. Resume must not initialize TEE-backed hardware before component rebind. Missing wakeref on system resume would risk MMIO while suspended, so `_pxp_resume()` optionally takes one.

Test signals: Suspend/hibernate tests and protected-content behavior after resume; logs for PXP end timeout or reinit failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_pm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_pm.h

Purpose: Declares optional PM hook entry points for PXP.

Important APIs/types: Suspend prepare, suspend, resume complete, runtime suspend, and runtime resume declarations with disabled-config stubs.

Control flow: Header-only conditional compilation.

State/persistence: None.

Dependencies/integration: Called from i915 PM flows.

Risks: Stubbed no-op behavior means callers rely on config gating for protected-content support.

Test signals: Build coverage and system/runtime PM tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_regs.h

Purpose: Defines KCR/PXP MMIO register offsets and bits.

Important APIs/types: `GEN12_KCR_BASE`, `MTL_KCR_BASE`, `KCR_INIT()`, `KCR_INIT_ALLOW_DISPLAY_ME_WRITES`, `KCR_SIP()`, and `KCR_GLOBAL_TERMINATE()`.

Control flow: No code. Macros parameterize base address differences between legacy and media-tile KCR.

State/persistence: Hardware registers track display/ME write permission, session-in-play bits, and global termination trigger.

Dependencies/integration: Used by PXP lifecycle and session code through uncore MMIO accessors.

Risks: Wrong base selection causes writes to the wrong MMIO block. Global terminate and session-in-play register use must be under appropriate runtime PM/uncore access.

Test signals: PXP hardware init toggles `KCR_INIT`; session wait polls `KCR_SIP`; teardown writes `KCR_GLOBAL_TERMINATE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_session.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_session.c

Purpose: Manages PXP arb-session creation, termination, global teardown, key-instance update, and asynchronous session-event work.

Important APIs/functions: `intel_pxp_session_management_init()` and `intel_pxp_terminate()`. Important internals are `pxp_create_arb_session()`, `pxp_terminate_arb_session_and_global()`, `pxp_wait_for_session_state()`, `intel_pxp_session_is_in_play()`, `pxp_terminate_complete()`, and `pxp_session_work()`.

Control flow: Session creation verifies the arb session is not already in play, sends create-session through GSC-CS or TEE backend, waits for `KCR_SIP` to show the session active, increments nonzero `key_instance`, and marks `arb_is_valid`. Termination submits GPU inline session termination, waits for `KCR_SIP` to clear, writes global terminate, asks firmware to end/invalidate the arb session, and completes or restarts depending on event flow. Worker consumes `session_events`, invalidates contexts if requested, skips work if runtime-suspended, performs termination on request, and recreates sessions after reset completion when `hw_state_invalidated` was set.

State/persistence: Tracks `arb_is_valid`, `key_instance`, `hw_state_invalidated`, `termination` completion, and `session_events`. Hardware state is observed through `KCR_SIP`. Runtime suspend is treated as session off by conditional wakeref paths.

Dependencies/integration: Uses PXP command submission, GSC-CS/TEE firmware backends, KCR regs, uncore register waits, runtime PM, IRQ event bits, and GEM context invalidation.

Risks: Firmware and hardware teardown must stay coherent; if GPU termination fails, completion is forced but PXP remains inactive until another termination. `key_instance` wrap avoids zero but stale objects must still be rejected. Worker event ordering deliberately drops reset-complete when termination request is in the same batch.

Test signals: Debugfs termination, IRQ-driven termination/reset-complete events, PXP start/end timeouts, and protected-object key checks after session recreation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_session.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_session.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_session.h

Purpose: Declares optional PXP session-management functions.

Important APIs/types: `intel_pxp_session_management_init()` and `intel_pxp_terminate()`, with stubs when PXP is disabled.

Control flow: Header-only conditional compilation.

State/persistence: None directly; implementation operates on `struct intel_pxp`.

Dependencies/integration: Used by PXP init, IRQ worker, PM/end paths, and command backends.

Risks: Disabled-config stubs remove all session behavior, so callers must only expect real behavior when PXP is configured and enabled.

Test signals: Build in both configs and session recovery behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_session.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_tee.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_tee.c

Purpose: Implements the legacy MEI PXP TEE component backend and streaming command path used for PXP firmware commands and HuC load/auth flows.

Important APIs/functions: `intel_pxp_tee_component_init()`, `intel_pxp_tee_component_fini()`, `intel_pxp_tee_cmd_create_arb_session()`, `intel_pxp_tee_end_arb_fw_session()`, and `intel_pxp_tee_stream_message()`. Component callbacks bind/unbind the MEI device and may trigger HuC loading.

Control flow: Component init optionally allocates a one-page LMEM streaming command object on dgfx, then registers a typed component. Bind stores `pxp_component`, sets `tee_dev`, optionally adds a device link, loads HuC via GSC if required, and initializes PXP hardware if runtime active. Normal message I/O serializes under `tee_mutex`, sends then receives via component ops with 5s timeout. Streaming message copies input to the pinned command object and calls component `gsc_command`. Session create and stream-key invalidation build API 4.2 packets; invalidation retries up to three times for coherency.

State/persistence: Maintains `pxp_component`, `dev_link`, `pxp_component_added`, and `stream_cmd` object/vaddr. Firmware platform config failures set `platform_cfg_is_bad`.

Dependencies/integration: Linux component framework, MEI PXP interface, i915 component IDs, GEM LMEM/internal mapping, HuC/GSC loading, runtime PM, and PXP command ABI 4.2/4.3.

Risks: Component binding is asynchronous relative to i915 probe and PM, so all message paths must handle `-ENODEV`. Stream command supports one page only. Device-link policy differs for HECI PXP platforms. Long TEE timeouts hold `tee_mutex`. Failed component unregister or missed hardware fini can leave interrupts/hardware enabled.

Test signals: Component bind/unbind logs, HuC load/auth result, PXP readiness status waiting for component bound, and TEE send/recv error logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_tee.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_tee.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_tee.h

Purpose: Declares the MEI TEE backend API for PXP.

Important APIs/types: Component init/fini, arb-session create, and streaming message send helper.

Control flow: Header only.

State/persistence: None; implementation operates on `pxp->pxp_component` and `pxp->stream_cmd`.

Dependencies/integration: Includes top-level PXP header and is used by PXP init/session/HuC paths.

Risks: No disabled-config stubs here, so inclusion assumes PXP build context. Streaming message API exposes raw lengths and caller-owned buffers; size validation occurs in implementation.

Test signals: Build linkage and firmware-command behavior through TEE backend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_tee.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_types.h

Purpose: Defines persistent PXP subsystem state shared by top-level logic, PM, IRQ/session code, and firmware backends.

Important APIs/types: `struct intel_pxp`, nested `gsccs_session_resources`, session event bit macros `PXP_TERMINATION_REQUEST`, `PXP_TERMINATION_COMPLETE`, `PXP_INVAL_REQUIRED`, and `PXP_EVENT_TYPE_IRQ`.

Control flow: No executable flow; comments describe ownership and locking. `tee_mutex` protects component binding and messaging; `arb_mutex` protects arb session start; `termination` completion coordinates teardown; `session_events` is protected by `gt->irq_lock`.

State/persistence: Holds control GT, platform bad-config latch, KCR base, GSC-CS resources, MEI component/device link state, kernel PXP context, arb validity, key instance, stream command object, hardware invalidation flag, IRQ enabled flag, completion, work item, and event bits.

Dependencies/integration: Forward declares GT/context/component/i915 types and includes Linux completion/mutex/workqueue APIs. It is the central shared contract across all PXP files.

Risks: Multiple locks protect different fields; mixing them incorrectly can race backend messages, session starts, IRQ event updates, or PM transitions. `platform_cfg_is_bad` intentionally persists after firmware reports platform issues. `arb_is_valid` is a software truth distinct from hardware session-in-play bits.

Test signals: Debugfs exposes active/key instance; logs and completion waits reveal event/session state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_active.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_active.c

Purpose: Provides live selftests and debug helpers for `i915_active`, validating request tracking, retirement callbacks, barriers, and wait/flush behavior.

Important APIs/functions: `i915_active_live_selftests()`, `i915_active_print()`, and `i915_active_unlock_wait()`. Test cases include `live_active_wait()`, `live_active_retire()`, and `live_active_barrier()`.

Control flow: Tests allocate a `live_active` wrapper with active/retire callbacks, create kernel requests on all UABI engines, hold submission behind a software fence, add requests to `i915_active`, then release and check counts/retirement. Wait test explicitly waits active idle; retire test uses `igt_flush_test()`; barrier test preallocates/acquires engine barriers and waits retirement. Unlock wait flushes signaled active fences and waits for callback/work completion.

State/persistence: `live_active` stores `i915_active`, kref, and retired flag. Active callbacks take/drop refs so the object survives until retirement. `i915_active_print()` walks the active tree and preallocated barriers for diagnostics.

Dependencies/integration: Uses GT engines, request creation, software fences, `igt_flush_test`, active fence internals, DMA fence callback lists, and DRM printers.

Risks: Tests depend on all UABI engines making progress; wedged GT skips tests. Direct manipulation of active fence slots in `active_flush()` assumes signaled fences and internal structure invariants. Barrier detection uses memory barriers to avoid racing with active-barrier updates.

Test signals: Selftest failures print missing retirement, incorrect active counts, active tree/barrier details, and flush errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_active.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_gem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_gem.c

Purpose: Live GEM selftests for suspend, hibernate, stolen-memory loss simulation, context switching after resume, and GEM wound/wait locking behavior.

Important APIs/functions: `i915_gem_live_selftests()`, `igt_gem_suspend()`, `igt_gem_hibernate()`, `igt_gem_ww_ctx()`, `switch_to_context()`, and PM helper shims.

Control flow: Suspend/hibernate tests create a mock file and live context, submit requests on all context engines, run GEM suspend/freeze paths under runtime PM where needed, simulate hibernate by overwriting stolen memory through GGTT aperture, resume GGTT/GEM/PAT state, and submit again. WW test creates two internal objects and locks them repeatedly using a GEM ww context, handling `-EDEADLK` by backing off and retrying.

State/persistence: No lasting state after tests. Temporarily mutates stolen memory contents, GGTT suspend/resume state, GEM object locks, and context/request state.

Dependencies/integration: GEM PM, GGTT, stolen memory, runtime PM, PAT setup, mock DRM files, live contexts, internal GEM objects, and `igt_flush_test` patterns.

Risks: Stolen-memory trashing is intentionally destructive in a controlled test slot and only works when GGTT aperture exists. PM sequencing must mimic real S3/S4 enough to catch restoration bugs without full platform sleep. WW locking test relies on correct deadlock handling.

Test signals: Context switch failures after resume, stolen restore issues, GEM PM failures, and ww lock/backoff errors. Wedged GT skips the live suite.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_gem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_gem_evict.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_gem_evict.c

Purpose: Mock and live selftests for GEM/GGTT eviction behavior under full, pinned, color-constrained, VM-wide, overcommit, and context-allocation pressure scenarios.

Important APIs/functions: `i915_gem_evict_mock_selftests()`, `i915_gem_evict_live_selftests()`, `igt_evict_something()`, `igt_overcommit()`, `igt_evict_for_vma()`, `igt_evict_for_cache_color()`, `igt_evict_vm()`, and `igt_evict_contexts()`.

Control flow: Mock tests fill GGTT with page-sized internal objects marked by a tiling quirk for cleanup ownership. They verify eviction fails while objects are pinned, succeeds after unpinning, fails overcommit pinning, handles fixed-node eviction, respects cache-color constraints, and evicts whole VMs under a ww context. Live context test reserves/fills GGTT with unevictable nodes to simulate small space, creates many contexts/requests per engine with submission held by a fence, and verifies request/context construction triggers eviction rather than unexpected allocation failures.

State/persistence: Temporarily fills GGTT bound lists, pins/unpins VMAs, mutates `ggtt->vm.mm.color_adjust`, reserves DRM MM nodes, uses `igt_evict_ctl.fail_if_busy`, and holds runtime PM during live context pressure. Cleanup drains freed objects and removes reserved nodes.

Dependencies/integration: GEM internal objects, GGTT VM insertion/eviction, DRM MM, cache coloring/PAT indices, software fences, contexts, GT idle waits, runtime PM, mock GEM device, and `igt_flush_test`.

Risks: Cleanup depends on tiling quirk as an ownership marker and must clear all pinned VMAs. Changing color-adjust semantics or GGTT cache-color policy can invalidate assumptions. Live test is meaningful only with full PPGTT and skips otherwise. Unevictable reservations must always be removed to avoid corrupting subsequent tests.

Test signals: Explicit error messages for unexpected `-ENOSPC`/`-EBUSY`, failed eviction calls, color eviction mistakes, GT idle failures, and request allocation errors under pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_gem_evict.c -->
