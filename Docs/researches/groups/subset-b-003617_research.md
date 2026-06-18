# Research: subset-b-003617

Work item `subset-b-003617` covers the i915 GuC submission and HuC/uC orchestration files under `sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_submission.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_submission.c

## Purpose

This file implements the GuC-backed i915 command submission backend. It replaces execlists-style scheduling with GuC context registration, GuC ID management, H2G submit/schedule-control messages, G2H completion/reset handlers, GuC-owned busyness accounting, TLB invalidation, virtual-engine support, and multi-LRC parallel submission. The large top-level comment is accurate: the driver owns LRC tail updates, context lifecycle, and host-side state consistency while GuC owns firmware scheduling once contexts are registered and enabled.

## Important APIs, Types, And Functions

Important exported entry points are `intel_guc_submission_init_early()`, `intel_guc_submission_init()`, `intel_guc_submission_setup()`, `intel_guc_submission_enable()`, `intel_guc_submission_disable()`, `intel_guc_submission_fini()`, reset/cancel helpers, busyness park/unpark, G2H handlers, debug printers, and `intel_guc_virtual_engine_has_heartbeat()`. Internal state is centered on `struct intel_guc::submission_state`, `context_lookup` xarray, `guc_id` refs on `struct intel_context`, `ce->guc_state.sched_state`, and the single shared `i915_sched_engine` tasklet.

The scheduling-state bit helpers manage pending enable/disable, registered, destroyed, banned, closed, deregister-to-register wait, and a blocked counter. `guc_request_alloc()` is the key request-preparation hook: it reserves GuC request space, emits cache/TLB invalidation, initializes GuC context state, cancels delayed schedule-disable work, pins or steals a GuC ID, registers the context if needed, and attaches request submit fences when disable or deregister G2H replies are pending.

Submission flows through `guc_submit_request()`, `queue_request()`, `guc_submission_tasklet()`, `guc_dequeue_one_context()`, `try_context_registration()`, `guc_wq_item_append()` for multi-LRC, `guc_set_lrc_tail()` for normal contexts, and `guc_add_request()`. Context registration supports both pre-1.0 GuC submission descriptors in a shared LRC descriptor pool and v1.0+ KLV-style registration structures. `guc_context_policy_init_v70()` and the v69 descriptor policy code push priority, timeslice, preemption timeout, forced preempt-to-idle, and SLPC context-frequency metadata.

## Control Flow

Early init creates locks, lists, ID allocators, workers, timestamp work, default schedule-disable delay, GuC ID limits, and support/selection booleans. `intel_guc_submission_init()` allocates the v69 descriptor pool when required, initializes TLB invalidation lookup state, allocates the multi-LRC GuC ID bitmap, computes timestamp worker cadence, and marks submission initialized. `intel_guc_submission_setup()` installs GuC engine vfuncs, a shared virtual sched engine, breadcrumbs, IRQ handlers, request hooks, reset hooks, and RCS-specific emit overrides.

Enable routes Gen12 semaphore interrupts to GuC, initializes pinned kernel contexts, starts GuC usage stats, and programs global scheduling policy for newer firmware. Disable cancels busyness sampling and routes semaphores back to the host. Runtime request submission tries a direct H2G path when the context is already mapped, the queue is empty, submission is enabled, and no stalled request exists; otherwise it queues work on the tasklet. Stalls on full CT/work queues are persisted in `guc->stalled_request` plus `submission_stall_reason` and retried by the tasklet.

Reset prepare disables submission, interrupts, CT receive handling, heartbeats, and destroyed-context work, then scrubs outstanding G2H effects so lost replies cannot leak GuC IDs or leave fences blocked. Reset replays pinned parent contexts, resets guilty requests, unwinds incomplete requests back to the priority queue, destroys the context lookup, and wakes TLB waiters. Reset finish clears unexpected outstanding G2H count, restores global policies, reenables submission, unparks heartbeats, and wakes invalidation waiters.

## State, Persistence, And Concurrency

The driver persists GuC context identity in an IDA for normal contexts and a reserved bitmap region for contiguous multi-LRC parent/children. Unpinned normal contexts with zero request refs are added to a reusable list and may have their GuC ID stolen. The xarray maps active GuC IDs to contexts and doubles as a registration-present test. Destroyed contexts are queued to a worker because deregistration can need GT PM and cannot always run in atomic context.

`ce->guc_state.lock`, `guc->submission_state.lock`, and `sched_engine->lock` protect distinct domains, with documented lock ordering. The blocked sw fence prevents resubmission while schedule-disable or deregistration is in flight. Outstanding G2H replies are counted in `guc->outstanding_submission_g2h` and waited on by suspend/idle paths. Busyness state extends GuC 32-bit GT timestamps into monotonic 64-bit accounting with a delayed worker and reset-aware rollback.

## Dependencies And Integration Points

The file integrates with i915 LRC/ring helpers, scheduler priority lists, GT PM and reset, GuC CT/H2G APIs, GuC ADS, capture, breadcrumbs, engine IRQs, MOCS, SLPC policy fields, runtime PM, xarray/IDA/bitmap allocators, and debug/error capture. It is called from the broader `intel_uc.c` load/reset/suspend path after GuC firmware and CT communication are ready.

## Risks And Test Signals

Risk is concentrated in races around lost G2H replies, context close versus request allocation, GuC ID stealing, schedule-disable fences, reset while CT is full, and multi-LRC work-queue wrap/handshake correctness. The state bits are compact and lock-sensitive, so missing a lock or decrement can deadlock submissions or leak IDs. TLB invalidation is in reclaim-sensitive paths and has serial-slot fallback under memory pressure. Test signals include GuC submission selftests included at file end, hangcheck and multi-LRC selftests, suspend/resume, GT reset and wedged paths, debugfs context dumps, PMU engine busyness, CT timeout logs, no stuck `outstanding_submission_g2h`, and successful virtual/parallel engine workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_submission.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_submission.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_submission.h

## Purpose

This header exposes the GuC submission backend contract to the rest of i915 GT/uC code. It declares lifecycle, setup, reset-visible, debug, busyness, virtual-engine heartbeat, and pending-message wait APIs while keeping implementation details in `intel_guc_submission.c`.

## Important APIs, Types, And Functions

The public functions cover early/init/enable/disable/fini, per-engine setup, debug printing, active request dumping, busyness park/unpark, pending-message wait, and work flushing. The inline predicates `intel_guc_submission_is_supported()`, `intel_guc_submission_is_wanted()`, and `intel_guc_submission_is_used()` map `struct intel_guc` booleans and firmware use state into the common uC state model.

## Control Flow

`intel_uc.c` calls these APIs in order: early selection during uC early init, memory initialization before firmware load, engine vfunc setup during engine initialization, enable after GuC firmware/CT communication are running, reset hooks during GT reset, disable/fini during unload or failed init, and debug functions through GuC/UC debugfs.

## State, Dependencies, Risks, And Test Signals

The header depends on `intel_guc.h`, `linux/types.h`, and forward declarations for `drm_printer` and engines. Its main risk is contract drift: callers rely on `is_used()` requiring both a running GuC and selected submission. Build coverage, GuC-enabled boot, debugfs registration, reset/suspend paths, and users of `intel_uc_wait_for_idle()` are the key test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_submission.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_huc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_huc.c

## Purpose

This file manages the HuC media microcontroller lifecycle and authentication state. The kernel does not provide HuC runtime services to userspace; it loads or coordinates loading of HuC firmware, authenticates it through GuC or GSC depending on platform, tracks delayed GSC/PXP load state, and reports status for getparam/debugfs.

## Important APIs, Types, And Functions

Exported functions include `intel_huc_init_early()`, `intel_huc_init()`, `intel_huc_fini()`, `intel_huc_fini_late()`, `intel_huc_sanitize()`, `intel_huc_auth()`, `intel_huc_wait_for_auth_complete()`, `intel_huc_is_authenticated()`, `intel_huc_check_status()`, `intel_huc_update_auth_status()`, notifier registration helpers, and `intel_huc_load_status()`. The delayed-load helpers use `huc->delayed_load.fence`, `hrtimer`, notifier block, and `enum intel_huc_delayed_load_status`.

## Control Flow

Early init initializes generic firmware state and a completed delayed-load fence, rejects HuC when no VCS engine exists, and selects the authentication status registers for GuC and GSC modes. `check_huc_loading_mode()` reads GSC-load fuses where applicable, validates whether the blob has GSC headers or DMA subimage offsets, and ensures DG2 MEI or newer GSCCS dependencies exist. `intel_huc_init()` allocates a GSCCS HECI packet VMA when needed, initializes the firmware object, and marks it loadable.

Authentication through GuC calls `intel_guc_auth_huc()` with the RSA GGTT offset and waits for the configured status register. Authentication through GSC calls `intel_huc_fw_auth_via_gsccs()` for two-step platforms. DG2-style GSC-loaded HuC uses a notifier and delayed fence: MEI-GSC binding moves status to waiting-on-PXP, MEI/PXP load completion should authenticate HuC, and timers fail the delayed load if the devices do not bind in time.

## State, Dependencies, Risks, And Test Signals

State persists in `huc->fw`, `status[]`, `loaded_via_gsc`, optional `heci_pkt`, and delayed-load fence/timer/notifier state. Dependencies include GuC auth, GSC/GSCCS, MEI-GSC/MEI-PXP, PXP command definitions, RPS frequency reads, runtime PM, and HuC firmware parsing. Risks include platform-mode mismatches, missing DMA subimage offsets in GSC-enabled blobs, delayed-load races on suspend/resume or notifier unbind, and long authentication under throttling. Test signals are `I915_PARAM_HUC_STATUS`, debugfs `huc_info`, HuC auth logs, DG2 GSC delayed-load behavior, MTL two-step auth, suspend/resume reloads, and media workload power/performance behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_huc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_huc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_huc.h

## Purpose

This header defines the HuC object shape and public lifecycle/authentication API. It connects generic uC firmware management with HuC-specific status registers, delayed GSC/PXP loading, and GSCCS authentication packet storage.

## Important APIs, Types, And Functions

`enum intel_huc_delayed_load_status` distinguishes waiting on GSC, waiting on PXP, and delayed-load error. `enum intel_huc_authentication_type` defines GuC and GSC auth slots. `struct intel_huc` embeds `struct intel_uc_fw`, per-auth status register/mask/value triplets, delayed-load fence/timer/notifier/status, optional `heci_pkt`, and `loaded_via_gsc`.

The inline helpers expose supported/wanted/used state through generic firmware status, identify GSC-load mode, and tell callers whether submissions must wait for GSC authentication.

## Control Flow, Dependencies, Risks, And Test Signals

`intel_uc.h` embeds this structure in `struct intel_uc`; `intel_huc.c`, `intel_huc_fw.c`, and debugfs consume the declarations. The main contract risk is that `intel_huc_is_used()` asserts the firmware has moved past transient selected state, so callers must run fetch/init in order. `intel_huc_wait_required()` can stall userspace submission until delayed GSC authentication finishes, so fence completion paths and status updates are critical. Build coverage, HuC status getparam, debugfs, and delayed-load tests are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_huc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_huc_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_huc_debugfs.c

## Purpose

This file registers HuC-specific debugfs reporting under the GT uC debugfs tree. It provides a narrow `huc_info` file that dumps HuC load and authentication state through the common DRM printer.

## Important APIs, Control Flow, And Integration

`huc_info_show()` obtains `struct intel_huc` from `seq_file::private`, returns `-ENODEV` for unsupported HuC, and delegates formatting to `intel_huc_load_status()`. `intel_huc_debugfs_register()` registers a single `intel_gt_debugfs_file` when HuC is supported. It is invoked by `intel_uc_debugfs_register()` after creating the `uc` directory.

## State, Risks, And Test Signals

The file does not own persistent state. It depends on `intel_gt_debugfs`, `drm_print`, and `intel_huc_load_status()`, which may take runtime PM to read registers. Risk is mostly stale or missing status exposure if support predicates diverge. Test signals are presence/absence of `uc/huc_info`, correct unsupported error behavior, and output containing firmware dump plus HuC status register value on supported platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_huc_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_huc_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_huc_debugfs.h

## Purpose

This header exposes HuC debugfs registration to the UC debugfs aggregator.

## APIs, Dependencies, Risks, And Test Signals

It forward-declares `struct intel_huc` and `struct dentry` and declares `intel_huc_debugfs_register()`. The dependency surface is intentionally small to avoid pulling debugfs internals into other uC headers. Contract risk is limited to signature drift with `intel_huc_debugfs.c` and callers. Build coverage and the presence of `uc/huc_info` when HuC is supported are sufficient signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_huc_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_huc_fw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_huc_fw.c

## Purpose

This file handles HuC firmware binary details that are specific to GSC-enabled images and GSCCS/PXP authentication. It parses GSC CPD headers, extracts version and DMA subimage information, sends MTL-style HECI authentication packets, and delegates DG2-style GSC load/auth to PXP.

## Important APIs, Types, And Functions

`struct mtl_huc_auth_msg_in` and `struct mtl_huc_auth_msg_out` wrap GSC MTL headers around PXP 4.3 HuC auth payloads. `intel_huc_fw_auth_via_gsccs()` maps the preallocated HECI packet object, fills a PXP `NEW_HUC_AUTH` request with HuC GGTT address and size, submits through `intel_gsc_uc_heci_cmd_submit_packet()`, handles pending replies with retries, validates reply size, and accepts success or already-loaded status.

`intel_huc_fw_get_binary_info()` validates CPD marker/version/header length, walks CPD entries, reads `"HUCP.man"` version data through `intel_uc_fw_version_from_gsc_manifest()`, and records `dma_start_offset` when `"huc_fw"` points to a CSS-valid legacy subimage. `intel_huc_fw_load_and_auth_via_gsc()` handles GSC-loaded mode through PXP and status polling. `intel_huc_fw_upload()` performs legacy DMA upload unless GSC loading is selected.

## State, Dependencies, Risks, And Test Signals

State updates are made in `huc->fw.file_selected.ver`, `huc->fw.dma_start_offset`, `huc->fw` status, and the HECI packet object map. Dependencies include GSC binary header definitions, GSC HECI submission, PXP HuC load/auth, GGTT VMA offsets, GEM object mapping, and CSS/CPD formats. Risks include malformed firmware size/offset handling, CPD entry offsets that are only checked before CSS validation, retry exhaustion on pending GSC replies, accepting `OP_NOT_PERMITTED` as already-loaded, and object mapping lifetime mistakes. Test signals include GSC-enabled HuC firmware parsing, MTL GSCCS auth, DG2 PXP load/auth, bad firmware rejection, and HuC status transitioning to running.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_huc_fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_huc_fw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_huc_fw.h

## Purpose

This header exposes HuC firmware upload, GSC load/auth, GSCCS authentication, and GSC-binary parsing helpers.

## APIs, Dependencies, Risks, And Test Signals

Declared APIs are `intel_huc_fw_load_and_auth_via_gsc()`, `intel_huc_fw_auth_via_gsccs()`, `intel_huc_fw_upload()`, and `intel_huc_fw_get_binary_info()`. It forward-declares `struct intel_huc` and `struct intel_uc_fw` and includes `linux/types.h` for `size_t`. The risk is lifecycle misuse: callers must allocate `huc->heci_pkt` before GSCCS auth and fetch firmware data before parsing/upload. Build coverage plus legacy DMA upload, DG2 GSC load, and MTL GSC-header parsing/auth are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_huc_fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_huc_print.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_huc_print.h

## Purpose

This header provides HuC-prefixed logging macros layered on top of GT logging.

## APIs, Dependencies, Risks, And Test Signals

`huc_printk()` expands to `gt_<level>(huc_to_gt(_huc), "HuC: " ...)`, and convenience macros cover error, warning, notice, info, debug, and probe-error levels. It depends on `intel_gt.h` and `intel_gt_print.h`, especially `huc_to_gt()`. The main risk is macro argument side effects because `_huc` is evaluated inside another macro; existing usage passes simple pointers. Test signals are compile-time macro use and boot/auth logs consistently prefixed with `HuC:`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_huc_print.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_uc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_uc.c

## Purpose

This file orchestrates the GuC, HuC, and GSC uC stack for a GT. It expands `enable_guc` defaults, confirms supported/wanted options, fetches and cleans firmware, initializes software objects, programs WOPCM, loads firmware in the required order, enables GuC communication/submission/SLPC, and handles reset, suspend, runtime suspend, resume, and teardown.

## Important APIs And Functions

Public functions include early/late init, driver remove/late release, MMIO init, reset prepare/reset/finish, cancel requests, suspend/runtime suspend, resume/runtime resume. The static `intel_uc_ops` tables select either off-mode checks/fini or full GuC-on behavior. `__uc_init_hw()` is the central hardware bring-up function: print firmware versions, validate loadability, program WOPCM, reset GuC, upload HuC, reset ADS, write GuC params, upload GuC, enable CT communication, authenticate/update HuC, enable GuC submission, and enable SLPC or lower RPS.

## Control Flow

`uc_expand_default_options()` enables nothing before Gen12, disables older Gen12 defaults, enables HuC-only on pre-RaptorLake ADL-S, and otherwise defaults to HuC plus GuC submission. Firmware fetch is GuC-first; GuC fetch failure forces HuC/GSC firmware status out of transient selected state. Hardware init retries GuC firmware upload three times on Gen9 workarounds and once elsewhere while temporarily disabling low PL1 power limits and raising unslice frequency.

Communication uses CT enable/disable plus scratch-register capture for messages that arrive while CT is disabled. Runtime suspend waits briefly for outstanding submission G2H replies, then disables communication. Full suspend flushes GSC work, wakes TLB invalidation waiters, flushes GuC submission work, and sends GuC suspend under runtime PM. Runtime resume reenables CT communication and ARAT interrupt masking when needed, resumes GuC/GSC, and invalidates engine and GuC TLBs if available.

## State, Dependencies, Risks, And Test Signals

Persistent state includes `uc->ops`, embedded `guc/huc/gsc`, `load_err_log`, `reset_in_progress`, `fw_table_invalid`, and GuC `mmio_msg`. Dependencies span GT reset, uncore MMIO, GuC CT, GuC ADS/SLPC/submission, HuC auth, GSC firmware, RPS/HWMON, runtime PM, WOPCM partitioning, and scratch registers. Risks include unsafe fallback after WOPCM has been locked, missed MMIO messages around CT transitions, HuC upload/auth failures being tolerated differently than GuC failures, reset nesting, and suspend races with outstanding CTB/G2H. Test signals are GuC/HuC firmware boot logs, WOPCM register programming, GuC load retries, captured GuC error log on failure, suspend/resume and runtime PM, GuC submission enablement, SLPC enablement, and TLB invalidation after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_uc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_uc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_uc.h

## Purpose

This header defines the aggregate `struct intel_uc` and the operation indirection used by GT code to call uC lifecycle hooks regardless of whether GuC is enabled.

## Important APIs, Types, And Functions

`struct intel_uc_ops` contains optional hooks for sanitize, firmware fetch/cleanup, software init/fini, hardware init/fini, and mapping resume. `struct intel_uc` embeds `intel_gsc_uc`, `intel_guc`, and `intel_huc`, records the last failed GuC load log, and tracks reset/fw-table flags. State-checker macros generate `supports`, `wants`, and `uses` helpers for GuC, HuC, GuC submission, SLPC, RC, and GSC uC. Operation-wrapper macros provide no-op/default-return behavior when a hook is absent.

## Control Flow, Dependencies, Risks, And Test Signals

The header is consumed by GT driver init, reset, PM, debugfs, and the GuC/HuC modules. The comment documents the four-state model: not supported, supported, wanted, and in use, with “in use” committing the driver to microcontroller operation once blobs are found. Risks are state-model drift and wrappers hiding absent operations, especially when off-mode must still perform hardware safety checks. Build coverage, all `enable_guc` combinations, firmware-missing cases, and reset/suspend calls through wrappers are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_uc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_uc_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_uc_debugfs.c

## Purpose

This file creates the top-level GT `uc` debugfs directory and registers aggregate GuC/HuC/GSC debug views.

## Important APIs And Control Flow

`uc_usage_show()` prints supported/wanted/used booleans for GuC, HuC, and GuC submission using generated state helpers. `intel_uc_debugfs_register()` returns early without a GT root or without GuC support, creates `uc`, stores it in `uc->guc.dbgfs_node`, registers the `usage` file, then delegates to GSC, GuC, and HuC debugfs registration.

## State, Dependencies, Risks, And Test Signals

The only persistent side effect is the debugfs dentry pointer in GuC. Dependencies include Linux debugfs, DRM printers, `intel_gt_debugfs`, and each subcomponent debugfs registrar. Risks include partial debugfs registration if one subcomponent is unsupported and user-visible confusion when GuC unsupported suppresses HuC/GSC entries. Test signals are the `uc/usage` file content across `enable_guc` modes and the presence of nested GuC/HuC/GSC debug files on supported platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_uc_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_uc_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_uc_debugfs.h

## Purpose

This header exposes the aggregate uC debugfs registration hook.

## APIs, Dependencies, Risks, And Test Signals

It forward-declares `struct intel_uc` and `struct dentry` and declares `intel_uc_debugfs_register()`. The small surface keeps debugfs details out of core uC headers. Risk is limited to declaration/definition drift or callers passing a null/invalid GT root. Build coverage and creation of the `uc` debugfs directory with `usage` are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_uc_debugfs.h -->
