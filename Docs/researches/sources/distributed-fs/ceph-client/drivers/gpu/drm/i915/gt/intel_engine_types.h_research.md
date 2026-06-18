# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_types.h

## Purpose
This header defines the core i915 GT engine data model. It names engine classes and physical engine IDs, describes the execlists hardware/software tracking block, and defines `struct intel_engine_cs`, the central object used by submission, reset, power management, PMU accounting, command parsing, workarounds, and user-visible engine enumeration.

## Important APIs, Types, and Functions
Important constants are engine classes (`RENDER_CLASS`, `COPY_ENGINE_CLASS`, `VIDEO_DECODE_CLASS`, `VIDEO_ENHANCEMENT_CLASS`, `COMPUTE_CLASS`, `OTHER_CLASS`), per-class maximums, `enum intel_engine_id`, `intel_engine_mask_t`, `ALL_ENGINES`, and `VIRTUAL_ENGINES`. `struct intel_hw_status_page` owns the engine HWSP VMA and CPU mapping. `struct intel_instdone` captures engine done/debug registers. `struct i915_ctx_workarounds` describes indirect/per-context workaround batches.

`struct intel_engine_execlists` carries execlists submission state: timers for timeslicing and preemption, context status buffer pointers, `active`, `inflight`, and `pending` ports, virtual-engine RB tree, context IDs, error bits, semaphore-yield state, and port count. `struct intel_engine_execlists_stats` and `struct intel_engine_guc_stats` provide alternate busyness accounting for execlists and GuC submission. `struct intel_engine_cs` ties everything together: GT/uncore pointers, IDs and UABI class/instance, logical masks, MMIO base, TLB invalidation registers, pinned contexts, sched engine, breadcrumbs, PMU samples, HWSP, workaround lists, IRQ callbacks, reset callbacks, emit/submit vfuncs, command-parser tables, statistics, sysfs-like scheduling properties, and OA/perf grouping.

The inline helpers expose engine capability bits such as command-parser use, stats support, preemption, semaphores, timeslices, virtual engine status, relative MMIO, and workaround hold-switchout usage.

## Control Flow
The header has no executable control flow beyond simple inline flag checks. Runtime flow is supplied by backends such as execlists or GuC, which fill `intel_engine_cs` callbacks during engine setup. Requests enter through `submit_request`, use emit helpers to build command buffers, update breadcrumb and active-request tracking, rely on IRQ callbacks for completion, and pass through reset hooks when recovery is required.

## State and Persistence Behavior
Most state is per-engine and persists for the engine lifetime: engine identity, UABI mapping fields, pinned kernel/bind contexts, scheduling defaults/properties, workaround lists, command-parser tables, PMU counters, status-page mappings, and reset/submission callbacks. Execlists arrays and timers are volatile submission state. `default_state`, workaround VMAs, context tags, and HWSP contents must survive normal operation but are sanitized after reset or resume.

## Dependencies and Integration Points
This header is consumed broadly by i915 GT code: engine discovery, UABI registration, execlists and GuC submission, logical-ring context setup, PMU, OA/perf, breadcrumbs, resets, workarounds, command parser, TLB invalidation, forcewake, and selftests. It depends on i915 GEM, scheduler priority lists, timelines, uncore access, wakeref handling, and platform workarounds.

## Risks
Changing engine IDs or class ordering can break legacy engine maps, UABI enumeration, GuC logical masks, and per-engine arrays. Incorrect flag semantics can enable preemption, semaphores, timeslicing, or command-parser behavior on unsupported hardware. `struct intel_engine_cs` is shared by many subsystems, so layout and lifetime changes can create subtle races around tasklets, timers, reset, PM, and request retirement.

## Test Signals
Useful signals include successful i915 build, engine discovery showing stable names and UABI classes, passing i915 selftests for engine setup, working execbuf submission on all engine classes, correct PMU busy counters, clean suspend/resume and reset, command-parser selftests, and no lockdep warnings around scheduler/tasklet/reset paths.
