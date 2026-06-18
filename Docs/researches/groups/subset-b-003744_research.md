# Research group subset-b-003744

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_vop2_reg.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_vop2_reg.c

### Purpose

`rockchip_vop2_reg.c` is the SoC capability and register-operation table for Rockchip VOP2 display controllers. It describes supported DRM pixel formats/modifiers, per-window register fields, video-port limits, debug register dump ranges, interface muxing, clock divider setup, alpha blending, overlay layer assignment, and platform-driver matching for RK3566, RK3568, RK3576, and RK3588.

### Important APIs, Types, and Functions

The file is mostly static data consumed by `rockchip_drm_vop2.c` through `struct vop2_data`, `struct vop2_win_data`, `struct vop2_video_port_data`, `struct reg_field`, `struct vop2_regs_dump`, and `struct vop2_ops`. Format arrays distinguish cluster, esmart, smart, RK3576-specific cluster/esmart, AFBC, RK3576 32x8 AFBC half mode, and linear-only planes.

Executable helpers include `rk3568_set_intf_mux()`, `rk3576_set_intf_mux()`, `rk3588_calc_dclk()`, `rk3588_calc_cru_cfg()`, `rk3588_set_intf_mux()`, `vop2_parse_alpha()`, `vop2_setup_cluster_alpha()`, `vop2_setup_alpha()`, `rk3568_vop2_setup_layer_mixer()`, `rk3576_vop2_setup_layer_mixer()`, SoC-specific overlay setup functions, and background-delay setup functions. `vop2_dt_match`, `vop2_probe()`, `vop2_remove()`, and `vop2_platform_driver` connect the table to platform devices and the component framework.

### Control Flow

Platform probing is intentionally thin: `vop2_probe()` registers the component with `vop2_component_ops`, while compatible strings provide the correct `struct vop2_data`. During atomic modeset/commit, the shared VOP2 implementation calls the SoC operations selected from `rk3568_vop_ops`, `rk3576_vop_ops`, or `rk3588_vop_ops`.

Interface setup reads display mode state and output endpoint ID, computes mux selections and polarity fields, writes VOP system interface registers, and, on RK3588/RK3568, also writes GRF/regmap bits for HDMI/eDP/MIPI/RGB routing. RK3588 adds clock-tree calculations for HDMI, eDP, DP, MIPI, and DPI, returning the desired input dclk rate for the common clock code.

Overlay setup walks the DRM CRTC plane list, builds a video-port window mask, configures cluster alpha if a cluster window is present, assigns layers to ports, programs alpha mixers, and writes window delay/background pre-scan timing. RK3568/RK3588 share global overlay layer/port registers guarded by `vop2->ovl_lock` plus polling for cfg-done effects; RK3576 uses per-VP overlay registers and immediate per-window VP selection/delay fields.

### State and Persistence Behavior

Most state is immutable platform data. Runtime writes persist in memory-mapped VOP registers and GRF/PMU regmaps until the next atomic commit, reset, or power cycle. `vop2->old_layer_sel` and `vop2->old_port_sel` cache shared overlay programming so subsequent commits can migrate layers without selecting one window on multiple layers. Per-window `delay`, per-VP `win_mask`, and CRTC state-derived alpha/mode data are transient commit state.

The alpha helpers translate DRM blend state into hardware mixer fields. Cluster windows get an internal cluster mixer pass, while the VP mixer handles zpos > 0 layers and special propagation of bottom-layer global alpha into the HDR mixer path for VP0.

### Dependencies and Integration Points

The file depends on DRM atomic plane/CRTC state, DRM fourcc modifiers, blend constants, Rockchip output endpoint IDs, VOP2 register macros and accessors from `rockchip_drm_vop2.h`, Linux `regmap`, `FIELD_PREP`, `readx_poll_timeout_atomic`, and the component/platform bus. It integrates with device-tree compatible matching, Rockchip encoder/connector output routing, CRTC state (`rockchip_crtc_state`), and debug dump code that consumes `regs_dump`.

### Risks and Edge Cases

Clock and mux programming is highly SoC-specific; a wrong endpoint ID, polarity mapping, or divider can black-screen only one output type. RK3588 eDP1 programming clears HDMI1/eDP1 masks but appears to use HDMI0 divider field macros in the assignment path, which should be reviewed against the register definition. Shared RK3568/RK3588 overlay registers require strict ordering; skipping the port/layer cfg-done waits can cause layer migration artifacts. Alpha code assumes active planes have framebuffers when computing `fb->format->has_alpha`; callers must not pass malformed atomic state. Many array fields use `0xf` as "not attachable"; new VP/window additions must keep layer IDs, possible VP masks, AXI IDs, and win count consistent. AFBC modifier lists must match the hardware format restrictions or userspace can submit unsupported buffers.

### Test Signals

Useful signals include KMS atomic plane tests across all VPs and zpos orderings, alpha/global-alpha/premultiplied blend tests, AFBC and linear buffer scanout tests, YUV420 high-clock mode tests, output mux smoke tests for HDMI/eDP/DP/MIPI/RGB/LVDS, suspend/resume display restoration, register dump availability, and lockdep/poll-timeout logs during layer migration. SoC bring-up should specifically validate RK3568, RK3576, and RK3588 multi-output combinations because they use different overlay and clock-control paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_vop2_reg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_vop_reg.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_vop_reg.c

### Purpose

`rockchip_vop_reg.c` is the platform data table for the earlier Rockchip VOP display controller family. It maps generic VOP concepts such as windows, scaling, alpha, interrupts, modeset timing, output pins, AFBC, YUV conversion, LUTs, and common control bits to concrete register offsets/masks for RK3036, RK3126, PX30, RK3066, RK3188, RK3288, RK3366, RK3368, RK3399, RK3228, RK3328, RK3506, and RV1126.

### Important APIs, Types, and Functions

`_VOP_REG()`, `VOP_REG()`, `VOP_REG_SYNC()`, and `VOP_REG_MASK_SYNC()` create `struct vop_reg` descriptors with offset, mask, shift, write-mask behavior, and relaxed/non-relaxed write semantics. The core data structures are `struct vop_scl_regs`, `struct vop_scl_extension`, `struct vop_win_phy`, `struct vop_win_data`, `struct vop_intr`, `struct vop_modeset`, `struct vop_output`, `struct vop_common`, `struct vop_misc`, `struct vop_yuv2yuv_phy`, `struct vop_win_yuv2yuv_data`, `struct vop_afbc`, and `struct vop_data`.

The only executable functions are `vop_probe()`, which rejects devices without an OF node and registers `vop_component_ops`, and `vop_remove()`, which unregisters the component. `vop_driver_dt_match` binds compatible strings to a specific `struct vop_data`; `vop_platform_driver` exposes the platform driver.

### Control Flow

The platform driver is selected by OF compatible. Probe does not parse hardware itself; it lets the common VOP component code retrieve `of_device_id.data` and use the static table for later atomic modesets. During normal display operation, common code iterates windows, programs fields through `struct vop_reg` descriptors, enables interrupts, applies timing and output configuration, sets cfg-done, and uses optional AFBC/YUV2YUV/LUT descriptors when present.

The data is layered from reusable register blocks. For example, RK3288-style full windows are reused by RK3368/RK3399/RK3228/RK3328 with base offsets or slight output/common overrides; PX30-style windows are reused by RV1126 and RK3506 variants. Interrupt arrays map logical `DSP_HOLD_VALID_INTR`, `FS_INTR`, `LINE_FLAG_INTR`, and `BUS_ERROR_INTR` positions to differing status/enable/clear layouts.

### State and Persistence Behavior

This file owns no mutable runtime state beyond component registration. Its descriptors drive persistent hardware register writes made by the common VOP driver. Per-SoC `vop_data` persists for the device lifetime and defines maximum output size, LUT size, supported modifiers, VOP version, feature flags, and number/type of DRM planes.

### Dependencies and Integration Points

It depends on `rockchip_drm_vop.h` for the descriptor types, `rockchip_vop_reg.h` for raw register offsets, DRM fourcc/plane constants, the Rockchip AFBC modifier, and the Linux component/platform/OF module APIs. It is integrated with the Rockchip DRM driver registration code and common VOP atomic plane/CRTC implementation.

### Risks and Edge Cases

The table is a hardware contract; wrong masks or base offsets can program unrelated registers. Reusing descriptors across related SoCs reduces duplication but can hide subtle register-layout differences. Some compatible strings represent "big" and "lit" variants with different max output, LUT size, and plane layout; matching the wrong compatible can expose unsupported planes or resolutions. `vop_probe()` rejects missing OF nodes, so non-DT instantiation is unsupported. Modifier lists must be accurate, especially RK3399 primary-plane AFBC. Cursor windows are sometimes substituted with overlay windows because dedicated cursor alpha support is incomplete.

### Test Signals

Build coverage should include Rockchip DRM with all listed compatibles. Runtime testing should cover probe from DT, plane enumeration, primary/overlay/cursor use, full and lite VOP variants, interrupt handling, line flag/vblank delivery, scaling limits, YUV formats and 10-bit formats where advertised, AFBC scanout on RK3399, gamma LUT updates, output enable/polarity per encoder type, and suspend/resume cfg-done restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_vop_reg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_vop_reg.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_vop_reg.h

### Purpose

`rockchip_vop_reg.h` defines raw MMIO register offsets for the older Rockchip VOP controller generations. It is the address map used by `rockchip_vop_reg.c` to build typed field descriptors for system control, display timing, windows, alpha, interrupts, AFBC, MMU, color conversion, LUTs, BCSH/CABC, HDR/SDR conversion, and MCU bypass regions.

### Important APIs, Types, and Functions

The file has no functions or C types. Its API is a set of preprocessor macros grouped by SoC/register layout: RK3288, RK3368, RK3366, RK3399, RK3328, RK3036, RK3126, PX30, RK3188, RK3066, and RK3506. Macro families include common controller registers (`*_SYS_CTRL`, `*_DSP_CTRL*`, `*_REG_CFG_DONE`), window registers (`WIN0..WIN3_*`), hardware cursor registers (`HWC_*`), timing registers (`DSP_HTOTAL_HS_END`, `DSP_HACT_ST_END`, etc.), interrupt registers, AFBCD blocks, YUV2YUV/CSC coefficient ranges, MMU registers, LUT address windows, and post-processing/HDR blocks.

### Control Flow

There is no executable control flow. Include guards prevent duplicate definitions. Consumers include the header and use symbolic offsets to build `struct vop_reg` descriptors or direct table entries.

### State and Persistence Behavior

The header owns no state. It names persistent hardware locations, so writes through these offsets alter display controller state until later reprogramming, reset, runtime PM, or power loss. LUT address ranges and MMU/AFBC offsets identify memory-backed programming windows with side effects outside simple scalar registers.

### Dependencies and Integration Points

It has no external includes and is tightly integrated with `rockchip_vop_reg.c`. The macro names form an internal contract with the common VOP driver and any future table additions for the same controller generations.

### Risks and Edge Cases

Offset mistakes are difficult to catch at compile time. Several SoCs share near-identical maps with small shifts in interrupt, MMU, LUT, or HDR regions, so copy/paste changes are risky. Some maps include reserved/debug/post-processing registers that may not be safe to program generically. New code should avoid assuming that similarly named registers have the same width or bit layout across SoCs; `rockchip_vop_reg.c` must still provide masks and shifts per field.

### Test Signals

Compile-time signal is use by all VOP table definitions. Runtime validation comes from successful modeset, vblank interrupt, LUT, AFBC, MMU, and plane programming on each SoC family. Register dumps from vendor documentation or hardware bring-up are useful to compare every offset group before enabling new features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_vop_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/Makefile -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/Makefile

### Purpose

This Makefile builds the DRM GPU scheduler library object and conditionally descends into the KUnit test directory. It is the Kbuild entry point for scheduler core code shared by DRM drivers.

### Important APIs, Types, and Functions

There are no C APIs. `gpu-sched-y` aggregates `sched_main.o`, `sched_fence.o`, and `sched_entity.o` into the composite `gpu-sched.o`. `obj-$(CONFIG_DRM_SCHED)` includes the scheduler library when enabled, and `obj-$(CONFIG_DRM_SCHED_KUNIT_TEST)` includes `tests/`.

### Control Flow

Kbuild evaluates configuration symbols. If `CONFIG_DRM_SCHED=y` or `m`, the three core objects are linked into `gpu-sched.o`. If scheduler KUnit testing is enabled, the `tests` subdirectory is visited.

### State and Persistence Behavior

The file has no runtime state. Its persistent effect is build composition: exported symbols from the scheduler objects become available to DRM drivers only when the config selects this target.

### Dependencies and Integration Points

It integrates with Linux Kbuild, `CONFIG_DRM_SCHED`, `CONFIG_DRM_SCHED_KUNIT_TEST`, and the scheduler test Makefile.

### Risks and Edge Cases

Forgetting to add a new scheduler compilation unit here causes unresolved symbols or missing functionality. Enabling tests without the core scheduler config would be an invalid build setup unless guarded by Kconfig dependencies. License comments are inherited from the original AMD scheduler code while test files use SPDX in their subdirectory.

### Test Signals

Signals are successful allmodconfig/allyesconfig builds, module linkage when `CONFIG_DRM_SCHED=m`, and KUnit target discovery when `CONFIG_DRM_SCHED_KUNIT_TEST=y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/gpu_scheduler_trace.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/gpu_scheduler_trace.h

### Purpose

`gpu_scheduler_trace.h` defines tracepoints for observing DRM scheduler job lifecycle and dependency behavior. The documented events are treated as stable uAPI for tooling that follows queued, run, dependency, completion, and unschedulable-job events.

### Important APIs, Types, and Functions

The trace API consists of `DECLARE_EVENT_CLASS(drm_sched_job)`, `DEFINE_EVENT(drm_sched_job, drm_sched_job_queue)`, `DEFINE_EVENT(drm_sched_job, drm_sched_job_run)`, `TRACE_EVENT(drm_sched_job_done)`, `TRACE_EVENT(drm_sched_job_add_dep)`, and `TRACE_EVENT(drm_sched_job_unschedulable)`. Events record scheduler/ring name, device name, software queue count, hardware credit count, scheduler fence context/seqno, dependency context/seqno, and DRM client ID.

### Control Flow

Including `sched_main.c` with `CREATE_TRACE_POINTS` instantiates the tracepoints. `sched_entity.c` emits queue/add-dependency/unschedulable events, `sched_main.c` emits run and done events, and consumers read them through ftrace/perf trace infrastructure. The header deliberately places `TRACE_INCLUDE_PATH` and `trace/define_trace.h` outside the include guard, as required by Linux tracepoint generation.

### State and Persistence Behavior

Tracepoints do not own scheduler state. They take snapshots of job/entity/fence fields at emission time. Because the event documentation states they depend on `drm_sched_job_arm()`, jobs must have valid `sched` and `s_fence` fields before tracing.

### Dependencies and Integration Points

The file depends on Linux tracepoint macros, `stringify`, type declarations for `struct drm_sched_job`, `struct drm_sched_entity`, `struct drm_sched_fence`, DMA fences, and the single-producer/single-consumer queue count helper. It integrates with scheduler code and external tracing tools that rely on stable field names.

### Risks and Edge Cases

Changing field names, print formats, or event semantics can break user-space tracing tools. Trace fast assignments dereference scheduler, device, entity queue, and fence pointers, so events must only be emitted while those structures are alive. `hw_job_count` is sourced from `credit_count`, so it reflects in-flight credits rather than a literal job count.

### Test Signals

Signals include building with tracepoints enabled, seeing `gpu_scheduler:*` events under tracing, validating queue/run/done ordering during GPU submissions, and checking that dependency events appear for syncobj/reservation dependencies. ABI-sensitive changes should be tested with existing trace parsers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/gpu_scheduler_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/sched_entity.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/sched_entity.c

### Purpose

`sched_entity.c` implements DRM scheduler entities: per-context software queues that own ordered jobs before the scheduler moves them to hardware. It handles entity initialization, scheduler selection, job push/pop, dependency blocking, priority updates, flush/fini/destroy, killed-process cleanup, and guilty-context cancellation.

### Important APIs, Types, and Functions

Exported APIs are `drm_sched_entity_init()`, `drm_sched_entity_modify_sched()`, `drm_sched_entity_error()`, `drm_sched_entity_flush()`, `drm_sched_entity_fini()`, `drm_sched_entity_destroy()`, `drm_sched_entity_set_priority()`, and `drm_sched_entity_push_job()`. Internal helpers include `drm_sched_entity_is_idle()`, `drm_sched_entity_kill()`, `drm_sched_entity_kill_jobs_work()`, `drm_sched_entity_wakeup()`, `drm_sched_entity_add_dependency_cb()`, `drm_sched_job_dependency()`, `drm_sched_entity_pop_job()`, and `drm_sched_entity_select_rq()`.

### Control Flow

Drivers initialize an entity with one or more schedulers and a priority. Jobs are initialized/armed in `sched_main.c`, then `drm_sched_entity_push_job()` timestamps and queues them in the SPSC queue. The first job adds the entity to its runqueue and wakes the scheduler. When `sched_main.c` selects the entity, `drm_sched_entity_pop_job()` checks explicit xarray dependencies and backend `prepare_job()` dependencies. Unsatisfied dependencies install a DMA fence callback and make the entity temporarily not ready; the callback clears `entity->dependency` and wakes the scheduler.

Scheduler selection for multi-engine entities happens only when the entity queue is empty and the last scheduled fence is signaled. This keeps an entity's ordered jobs on the same engine while prior work is outstanding. Flush waits for the queue to drain or, on SIGKILL process exit, kills remaining queued jobs after dependencies finish to avoid data corruption.

### State and Persistence Behavior

Persistent entity state includes `rq`, scheduler list, priority, SPSC job queue, fence context pair, sequence counter, last scheduled finished fence under RCU, dependency fence/callback, last user task, idle completion, stopped flag, guilty pointer, and FIFO rb-tree node timestamp. Jobs are popped from the entity queue before hardware submission and then have `job->entity` nulled because entity and job lifetimes diverge.

### Dependencies and Integration Points

This file depends on `drm/gpu_scheduler.h`, `sched_internal.h`, DMA fences, xarrays, completions, RCU, SPSC queues, scheduler tracepoints, and runqueue helpers implemented in `sched_main.c`. Backends provide optional `prepare_job()` and mandatory free paths used during kill cleanup.

### Risks and Edge Cases

Ordering relies on the documented common lock around `drm_sched_job_arm()` and `drm_sched_entity_push_job()`. Dependency callbacks race with entity teardown, so `fini()` must remove callbacks and drop references carefully. Same-entity fences are ignored to avoid self-deadlock; changing fence contexts can break that logic. Killed-job cleanup deliberately waits for dependencies, which can delay teardown but prevents memory corruption. Priority changes update only `entity->priority`; callers must understand when runqueue placement changes. Pushing to a stopped entity logs an error after the job was queued, so driver lifetime ordering matters.

### Test Signals

Important tests cover entity init with invalid scheduler lists, multi-scheduler selection, FIFO and RR queue ordering, dependency callback wakeups, same-entity dependency elision, priority changes, guilty entity cancellation, SIGKILL flush cleanup, entity destroy with pending dependencies, and lockdep around entity/rq locks. KUnit scheduler tests and real driver workloads with syncobj/reservation dependencies are the strongest signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/sched_entity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/sched_fence.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/sched_fence.c

### Purpose

`sched_fence.c` implements `struct drm_sched_fence`, the scheduler's paired DMA-fence abstraction. Each job gets a `scheduled` fence signaled when the job has been submitted to hardware/firmware and a `finished` fence signaled when execution completes or errors.

### Important APIs, Types, and Functions

Exported/internal scheduler functions are `drm_sched_fence_alloc()`, `drm_sched_fence_init()`, `drm_sched_fence_free()`, `drm_sched_fence_scheduled()`, `drm_sched_fence_finished()`, and exported `to_drm_sched_fence()`. Fence operations include driver/timeline name callbacks, release callbacks for scheduled/finished fences, and `drm_sched_fence_set_deadline_finished()` for deadline propagation.

### Control Flow

Module init creates a slab cache for scheduler fences. Job initialization allocates an uninitialized fence object; job arm initializes the scheduled and finished DMA fences with adjacent contexts and the same sequence number. When `run_job()` returns a parent hardware fence, `drm_sched_fence_scheduled()` stores a reference to that parent before signaling the scheduled fence. When the hardware parent signals or an error path completes, `drm_sched_fence_finished()` sets any error and signals the finished fence.

Release is split: the scheduled fence release drops the parent and schedules RCU freeing of the containing `drm_sched_fence`; the finished fence release drops the extra reference held by the scheduled fence. Deadline setting on the finished fence stores the earliest deadline and forwards it to the parent if already known, using acquire/release ordering to handle races with parent installation.

### State and Persistence Behavior

The slab cache persists for the module lifetime. Each scheduler fence persists until both DMA fences and the parent reference are released. Fence state includes owner, DRM client ID for tracing, scheduler pointer, lock, optional parent fence, deadline, and the two embedded DMA fences.

### Dependencies and Integration Points

It depends on Linux DMA fence APIs, RCU, slab caches, module init/exit, and `drm/gpu_scheduler.h`. It is called by `sched_main.c` during job init/arm/run/done and by `sched_entity.c` for dependency classification and killed-job cleanup.

### Risks and Edge Cases

Fence lifetime is subtle because two embedded fences share one allocation. Calling `drm_sched_fence_free()` after initialization is invalid and guarded by `fence->sched`. Parent deadline propagation depends on memory barriers; weakening them can lose deadlines. `to_drm_sched_fence()` checks the ops pointer, so external fences safely return NULL but any ops mismatch breaks scheduler-fence identification. `drm_sched_fence_scheduled()` treats error/NULL parent specially; consumers waiting for parent after scheduled signal must handle no-parent cases.

### Test Signals

Tests should cover allocation failure unwind, unarmed cleanup, armed job completion, error propagation, parent fence callback completion, deadline propagation before and after parent installation, RCU/slab teardown, and `to_drm_sched_fence()` for scheduled, finished, and non-scheduler fences. Lockdep/KASAN help catch release-order issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/sched_fence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/sched_internal.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/sched_internal.h

### Purpose

`sched_internal.h` is the private interface shared by the DRM scheduler implementation files. It declares the global scheduling policy, runqueue/entity helpers, scheduler-fence helpers, and tiny queue helpers that are not part of the public DRM scheduler header.

### Important APIs, Types, and Functions

It declares `drm_sched_policy` plus `DRM_SCHED_POLICY_RR` and `DRM_SCHED_POLICY_FIFO`; runqueue helpers `drm_sched_rq_add_entity()`, `drm_sched_rq_remove_entity()`, `drm_sched_rq_update_fifo_locked()`, and `drm_sched_wakeup()`; entity helpers `drm_sched_entity_select_rq()` and `drm_sched_entity_pop_job()`; fence helpers `drm_sched_fence_alloc()`, `drm_sched_fence_init()`, `drm_sched_fence_free()`, `drm_sched_fence_scheduled()`, and `drm_sched_fence_finished()`. Inline helpers pop/peek SPSC queue nodes and test entity readiness.

### Control Flow

There is no standalone runtime flow. `sched_main.c`, `sched_entity.c`, and `sched_fence.c` include this header to call across compilation units without exposing those helpers to drivers.

### State and Persistence Behavior

The header owns no storage except the external declaration of `drm_sched_policy`, which is defined and module-param-controlled in `sched_main.c`. Inline queue helpers operate on entity job queues but do not allocate or persist state.

### Dependencies and Integration Points

It depends on public scheduler types, SPSC queue primitives, DMA fences, and runqueue structures from `drm/gpu_scheduler.h`. It is an internal contract between the scheduler's core files and should evolve with them.

### Risks and Edge Cases

The inline `drm_sched_entity_is_ready()` only checks queue count and current dependency; callers must separately handle credit limits and stopped schedulers. Queue pop/peek assume the node belongs to `struct drm_sched_job`. Changing policy constants affects module parameter semantics and runqueue selection behavior.

### Test Signals

Compile coverage of all scheduler objects validates declarations. Runtime coverage comes indirectly from queue selection, dependency blocking, FIFO/RR policy switching, and fence lifecycle tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/sched_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/sched_main.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/sched_main.c

### Purpose

`sched_main.c` implements the DRM GPU scheduler core: runqueues, priority/FIFO/RR entity selection, credit-based flow control, job initialization/arming/dependency helpers, hardware submission work, finished-job freeing, timeout/TDR handling, reset recovery support, scheduler init/fini, and workqueue pause/resume controls.

### Important APIs, Types, and Functions

Exported APIs include timeout/recovery controls (`drm_sched_tdr_queue_imm()`, `drm_sched_fault()`, `drm_sched_suspend_timeout()`, `drm_sched_resume_timeout()`, `drm_sched_stop()`, `drm_sched_start()`, `drm_sched_resubmit_jobs()`), job APIs (`drm_sched_job_init()`, `drm_sched_job_arm()`, dependency add helpers, `drm_sched_job_has_dependency()`, `drm_sched_job_cleanup()`, `drm_sched_job_is_signaled()`), scheduler APIs (`drm_sched_pick_best()`, `drm_sched_init()`, `drm_sched_fini()`, `drm_sched_increase_karma()`, `drm_sched_wqueue_ready()`, `drm_sched_wqueue_stop()`, `drm_sched_wqueue_start()`, `drm_sched_is_stopped()`), and internal runqueue/work helpers.

### Control Flow

Drivers initialize a scheduler with backend ops, credit limit, timeout, priority count, and workqueues. Jobs are initialized against an entity, assigned nonzero credits, armed to initialize scheduler fences and choose the current scheduler/runqueue, populated with explicit/syncobj/reservation dependencies, and pushed by `sched_entity.c`.

`drm_sched_run_job_work()` selects the highest-priority ready entity using FIFO rb-tree or round-robin list policy. It enforces credit availability, pops one dependency-free job, increments in-flight credits, adds it to `pending_list`, starts the timeout, calls backend `run_job()`, signals the scheduled fence, installs a callback on the returned hardware fence, and requeues itself for more work. Completion callbacks call `drm_sched_job_done()`, which subtracts credits, signals the finished fence, and queues free-job work. `drm_sched_free_job_work()` removes finished jobs from `pending_list`, calls backend `free_job()`, restarts timeout for the next pending job, and wakes submission.

Timeout work removes the oldest pending job, calls backend `timedout_job()`, handles false timeouts by reinserting the job, and restarts timeout unless the device is gone. Reset recovery uses `drm_sched_stop()` to pause workqueues and detach callbacks, driver reset logic, and `drm_sched_start()` to reattach callbacks or finish canceled jobs.

### State and Persistence Behavior

Scheduler state includes backend ops, runqueue array, `pending_list`, `job_list_lock`, ordered submit workqueue, timeout workqueue/delayed work, `ready` and `pause_submit`, credit limit/count, shared or private score, job ID counter, timeout/hang limit, and free-guilty marker. Runqueues maintain an entity list plus FIFO rb-tree keyed by oldest waiting job timestamp. Jobs persist from init through backend `free_job()` and carry credits, priority, scheduler pointer, dependencies xarray, pending-list node, callbacks, and scheduler fence.

### Dependencies and Integration Points

It depends on public DRM scheduler types, DMA fences/reservations, GEM objects, syncobjs, Linux workqueues, wait queues, completions, rbtrees, atomics, module parameters, and tracepoints. DRM drivers integrate by supplying `struct drm_sched_backend_ops` (`run_job`, `free_job`, `timedout_job`, optional `prepare_job`/`cancel_job`) and by wiring scheduler entities to contexts or queues.

### Risks and Edge Cases

Credit accounting must stay balanced across run, done, stop, false-timeout, and restart paths or the scheduler can starve or overrun hardware capacity. Job arm is a point of no return: drivers must push armed jobs and cannot clean them up directly. Timeout recovery has many lifetime races with free-job work and hardware-fence callbacks; `drm_sched_stop()` cancels work before mutating pending jobs for this reason. `drm_sched_resubmit_jobs()` is explicitly deprecated because generic resubmission around DMA fences is unsafe. `drm_sched_job_init()` logs through `job->sched->dev` even before `memset(job, 0)`, so callers need a job object whose scheduler pointer is meaningful in the no-rq error path. Scheduler teardown can leak pending jobs if the backend lacks `cancel_job()`.

### Test Signals

Coverage should include FIFO and RR policy behavior, priority ordering, credit-limit throttling including oversized jobs, dependency deduplication by fence context, syncobj and implicit reservation dependencies, job arm/push/cleanup misuse paths, hardware-fence completion and error propagation, false timeout handling, reset stop/start with guilty job retention, scheduler fini with and without `cancel_job`, workqueue stop/start, and KUnit mock scheduler tests. Real driver tests should run with lockdep, KASAN, and tracing enabled under GPU hang/recovery stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/sched_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/tests/Makefile -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/tests/Makefile

### Purpose

This Makefile builds the DRM scheduler KUnit test module.

### Important APIs, Types, and Functions

There are no runtime APIs. `drm-sched-tests-y` combines `mock_scheduler.o` and `tests_basic.o`; `obj-$(CONFIG_DRM_SCHED_KUNIT_TEST)` emits `drm-sched-tests.o`.

### Control Flow

Kbuild includes the test object only when scheduler KUnit testing is enabled. The parent scheduler Makefile descends into this directory under the same config.

### State and Persistence Behavior

The file has no runtime state. Its persistent build effect is making mock scheduler infrastructure and basic tests available to KUnit.

### Dependencies and Integration Points

It depends on Kbuild, `CONFIG_DRM_SCHED_KUNIT_TEST`, and the source files named in `drm-sched-tests-y`. It integrates with the parent DRM scheduler build and the kernel KUnit runner.

### Risks and Edge Cases

Adding a new test source without listing it here leaves it unbuilt. If the config is enabled without required scheduler/KUnit dependencies, the build will fail elsewhere. Whitespace uses continuation lines, so future edits need normal Kbuild syntax.

### Test Signals

Signals are successful KUnit builds and execution of the DRM scheduler test suite, especially mock scheduler and basic scheduling tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/tests/Makefile -->
