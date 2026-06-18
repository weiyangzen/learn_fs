# subset-b-003621 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/scheduler.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/scheduler.c

### Purpose
`scheduler.c` implements Intel GVT-g virtual GPU workload submission. It converts guest execlist context descriptors into i915 requests, shadows guest ring buffers and batch buffers, maps guest PPGTT state onto host shadow page tables, switches virtualized MMIO ownership during context scheduling, and retires completed workloads back into guest-visible context and interrupt state.

### Important APIs, Types, And Functions
The public entry points are `intel_gvt_scan_and_shadow_workload()`, `intel_gvt_init_workload_scheduler()`, `intel_gvt_clean_workload_scheduler()`, `intel_gvt_wait_vgpu_idle()`, `intel_vgpu_setup_submission()`, `intel_vgpu_reset_submission()`, `intel_vgpu_clean_submission()`, `intel_vgpu_select_submission_ops()`, `intel_vgpu_create_workload()`, `intel_vgpu_destroy_workload()`, `intel_vgpu_clean_workloads()`, and `intel_vgpu_queue_workload()`. Key internal helpers include `populate_shadow_context()`, `dispatch_workload()`, `prepare_workload()`, `prepare_shadow_batch_buffer()`, `prepare_shadow_wa_ctx()`, `complete_current_workload()`, `workload_thread()`, and `shadow_context_status_change()`. The central state objects are `struct intel_vgpu_workload`, `struct intel_vgpu_submission`, `struct intel_gvt_workload_scheduler`, i915 `struct intel_context`, `struct i915_request`, and GVT shadow MM objects.

### Control Flow
Workload creation translates the guest LRCA into a ring context GPA, reads guest head/tail/ring control and RCS WA context fields, validates GGTT ranges, allocates a workload from a per-vGPU slab, prepares the shadow PPGTT, optionally scans the first queued workload immediately, and pins the per-engine shadow context. `intel_vgpu_queue_workload()` appends it to the per-engine vGPU queue, kicks GVT scheduling, and wakes the engine worker. Each `workload_thread()` picks work only for the current scheduled active vGPU, takes runtime PM and forcewake as needed, updates virtual ring state, dispatches the workload as an i915 request, waits for request completion, then calls `complete_current_workload()`.

Dispatch allocates an i915 request, scans and shadows ring/batch content, copies guest LRC state into a host shadow context while preserving host OA registers, pins shadow MM roots, syncs out-of-sync GTT pages, flushes post-shadow changes, copies the shadow ring into the i915 ring, pins relocated non-PPGTT batch buffers, patches WA context pointers, runs submission-model hooks, and finally adds the request. Completion waits until the shadow context is scheduled out, maps request fence errors to workload status, writes back guest ring head/tail/context pages and guest PDPs, injects pending virtual events, drops the request and shadow MM pins, destroys the workload, and wakes waiters.

### State, Persistence, And Dependencies
Persistent state is kept in `gvt->scheduler` engine threads, wait queues, current workloads, current/next vGPU policy state, MMIO context owner slots, and the per-vGPU submission object. Per-workload state persists shadow MM refs, LRI shadow MM refs, copied ring metadata, pending events, shadow batch buffer objects/VMAs, WA context objects, OA register snapshots, active status, and request ownership. The file depends on i915 execlist/LRC internals, `intel_context` pinning and single-submission flags, request lifecycle, GGTT/PPGTT shadowing, GVT command scanning, GVT MMIO switch logic, runtime PM, forcewake, notifier chains, and the selected `intel_vgpu_submission_ops`.

### Integration Points
GVT execlist emulation calls `intel_vgpu_create_workload()` and `intel_vgpu_queue_workload()` after guest ELSP writes. Scheduler policy code controls `current_vgpu`, reschedule requests, and `intel_vgpu_stop_schedule()`. i915 engine context status notifiers call `shadow_context_status_change()` so GVT can switch render MMIO save/restore between host and vGPUs. Guest reset and vGPU destroy paths call the reset/clean helpers to stop, flush, and release queued and running workloads.

### Risks
This code relies on precise ordering across `vgpu_lock`, `sched_lock`, request context-switch notifications, runtime PM, and shadow MM pin/unpin. Incorrect guest GPA validation, LRC copyback ranges, PDP replacement, or batch relocation can expose host memory or corrupt guest GPU state. Error paths must avoid leaking pinned objects, VMAs, shadow contexts, and request refs. Some operations deliberately patch page-directory DMA addresses and contain comments noting this is fragile. A failed dispatch can push the guest into failsafe mode, and request fence `-EIO` suppresses guest context-switch interrupts to emulate a vGPU hang.

### Test Signals
Useful signals include GVT guest boot with execlist submission, invalid LRCA/ring/WA context rejection, RCS WA context shadowing, guest PPGTT LRI changes, non-PPGTT batch buffer relocation, context restore-inhibit reuse, request hang/error propagation, vGPU reset while workloads are pending/running, host-to-vGPU and vGPU-to-vGPU MMIO context switches, runtime PM/forcewake balance checks, and leak checks for shadow batch buffers, contexts, and MM refs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/scheduler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/scheduler.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/scheduler.h

### Purpose
`scheduler.h` defines the GVT-g workload scheduler and per-workload data contracts used by virtual submission code. It exposes the queueing, setup, reset, cleanup, scheduler init, and workload creation APIs implemented in `scheduler.c`.

### Important APIs, Types, And Functions
The main types are `struct intel_gvt_workload_scheduler`, `struct shadow_indirect_ctx`, `struct shadow_per_ctx`, `struct intel_shadow_wa_ctx`, `struct intel_vgpu_workload`, and `struct intel_vgpu_shadow_bb`. It declares `intel_vgpu_queue_workload()`, `intel_gvt_init_workload_scheduler()`, `intel_gvt_clean_workload_scheduler()`, `intel_gvt_wait_vgpu_idle()`, `intel_vgpu_setup_submission()`, `intel_vgpu_reset_submission()`, `intel_vgpu_clean_submission()`, `intel_vgpu_select_submission_ops()`, `intel_vgpu_create_workload()`, `intel_vgpu_destroy_workload()`, and `intel_vgpu_clean_workloads()`.

### Control Flow
The header does not implement logic, but its structures encode the runtime flow: workloads move through per-engine `workload_q_head()` lists, can be shadowed, dispatched, completed through submission hooks, and tracked as current work by `intel_gvt_workload_scheduler`.

### State, Persistence, And Dependencies
Scheduler state includes current/next vGPU selection, current workload per engine, engine MMIO owners, wait queues, worker threads, and policy ops. Workload state includes request pointers, shadow MM refs, shadow ring buffer storage, guest ring register snapshots, ELSP descriptor fields, pending events, shadow batch buffers, WA context state, and OA registers. The header depends on i915 engine types and GVT execlist/interrupt definitions.

### Integration Points
GVT submission models include this header to build workloads from guest execlist descriptors. Scheduler policy code uses `sched_data` and `sched_ops`, while vGPU lifecycle code uses setup/reset/cleanup declarations.

### Risks
Most fields are shared across scheduler threads, context status notifiers, and reset paths, so lock ownership from the implementation is part of the API contract even though it is not visible in this header. The usercopy slab range for workload allocation depends on the position and size of `rb_tail`, so layout changes must be reviewed carefully.

### Test Signals
Compile-time coverage should catch struct dependency drift. Runtime tests should exercise queueing and cleanup across all engines, workload destruction after partial setup, and submission ops switching with active and inactive vGPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/scheduler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/trace.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/trace.h

### Purpose
`trace.h` declares Linux tracepoints for Intel GVT internals. The events cover shadow page table lifecycle, guest-to-host address translation, out-of-sync page handling, command scanning, interrupt propagation, MSI injection, and render MMIO switching.

### Important APIs, Types, And Functions
It defines `TRACE_SYSTEM gvt` and trace events `spt_alloc`, `spt_free`, `gma_index`, `gma_translate`, `spt_refcount`, `spt_change`, `spt_guest_change`, `oos_change`, `oos_sync`, `gvt_command`, `write_ir`, `propagate_event`, `inject_msi`, and `render_mmio`. It also sets `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` for `trace/define_trace.h`.

### Control Flow
The header is included by GVT code to emit trace events and by `trace_points.c` with `CREATE_TRACE_POINTS` to instantiate them. Each event describes arguments, copies fields into a trace entry, and formats a compact print string for ftrace/perf consumers.

### State, Persistence, And Dependencies
The file holds no runtime state. Trace state is owned by the kernel tracing subsystem. Dynamic arrays are used for raw command dwords in `gvt_command`; fixed-size local buffers are used for formatted event text. Dependencies include tracepoint macros, Linux types, stringify helpers, and architecture TSC inclusion.

### Integration Points
GVT MM, command parser, interrupt, and scheduler code can call generated `trace_*` helpers. Users observe these through ftrace, tracefs, perf, or kernel tracing infrastructure when GVT tracepoints are enabled.

### Risks
Trace formatting must not read beyond command length or overflow fixed buffers; the code uses `snprintf()` and dynamic arrays for those cases. Event ABI names and field layouts are consumed by tracing tools, so renaming or changing field meaning can break diagnostics. Tracing command contents may expose guest workload details to privileged tracing users.

### Test Signals
Build tests must verify tracepoint generation with and without multiple includes. Runtime signals include enabling each GVT trace event under tracefs while creating, running, resetting, and destroying vGPUs, and checking that command events print the expected raw dword arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/trace_points.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/trace_points.c

### Purpose
`trace_points.c` is the single compilation unit that instantiates the GVT tracepoints declared in `trace.h`.

### Important APIs, Types, And Functions
The file defines `CREATE_TRACE_POINTS` before including `trace.h`, guarded by `#ifndef __CHECKER__` for sparse/static analysis compatibility. It exports no normal C functions.

### Control Flow
At build time, including `trace.h` with `CREATE_TRACE_POINTS` causes the tracepoint definitions to be emitted exactly once. Other GVT files include the same header without this macro and only see declarations.

### State, Persistence, And Dependencies
Runtime tracepoint state is registered by the kernel tracing framework. The only dependency is `trace.h` and the kernel tracepoint generation machinery.

### Integration Points
This file must be linked into the GVT object set whenever GVT trace events are referenced. Without it, callers of generated trace helpers would have unresolved tracepoint symbols.

### Risks
Multiple compilation units defining `CREATE_TRACE_POINTS` would duplicate tracepoint definitions, while omitting this unit would break linkage. The sparse guard means checker builds do not instantiate these macros.

### Test Signals
Build and module link success are the key tests. Runtime validation is covered by enabling events declared in `trace.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/trace_points.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/vgpu.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/vgpu.c

### Purpose
`vgpu.c` manages Intel GVT virtual GPU types and vGPU lifecycle. It initializes guest-visible PVINFO resources, derives supported mediated-device types from host aperture/hidden memory capacity, activates and deactivates vGPUs, creates and destroys vGPU runtime subsystems, and implements device-model or GT reset behavior.

### Important APIs, Types, And Functions
Important functions include `populate_pvinfo_page()`, `intel_gvt_init_vgpu_types()`, `intel_gvt_clean_vgpu_types()`, `intel_gvt_activate_vgpu()`, `intel_gvt_deactivate_vgpu()`, `intel_gvt_release_vgpu()`, `intel_gvt_destroy_vgpu()`, `intel_gvt_create_idle_vgpu()`, `intel_gvt_destroy_idle_vgpu()`, `intel_gvt_create_vgpu()`, `intel_gvt_reset_vgpu_locked()`, and `intel_gvt_reset_vgpu()`. Static vGPU type templates live in `intel_vgpu_configs[]`.

### Control Flow
Type initialization computes available low/high graphics memory after host reservations, allocates type and mdev type arrays, filters templates that fit host resources, names types by graphics generation, and publishes them for mediated-device creation. vGPU creation allocates an ID, initializes locks, IDRs, radix trees, PCI config space, MMIO, resource allocation, PVINFO, GTT, opregion, display, submission, scheduling policy, debugfs, opregion data, EDID, and register whitelists. Failure paths unwind in reverse order. Deactivation clears the active bit, waits for running workloads to drain, and stops scheduling. Reset stops scheduling, waits if the vGPU was current, resets submission, optionally invalidates PPGTT/GGTT/resources/MMIO/display/config space, repopulates PVINFO, and clears failsafe or PV notification state for device-model resets.

### State, Persistence, And Dependencies
Persistent state includes `gvt->types`, `gvt->mdev_types`, `gvt->num_types`, `gvt->vgpu_idr`, each vGPU's status bits, scheduling weight, locks, dmabuf/object/page tracking lists and IDRs, D3 and failsafe flags, `resetting_eng`, allocated graphics resources, MMIO image, GTT state, display/opregion state, submission state, and scheduler policy state. Dependencies include GVT resource allocation, GTT/MMIO/display/opregion/submission/scheduling modules, i915 PVINFO definitions, mediated device type structures, and EDID helpers.

### Integration Points
Mediated-device management calls the type and vGPU create/destroy functions. Guest PCI FLR and guest GT reset paths call reset functions. Submission and scheduler code observe status bits and `resetting_eng`. Debugfs and dmabuf helpers are added and removed here as part of vGPU lifecycle.

### Risks
Lifecycle ordering is critical because many subsystems depend on earlier initialization. Reset paths temporarily drop `vgpu_lock` while waiting for workloads, which requires state to remain valid and protected by scheduling stop semantics. DMLR and D3 transitions intentionally treat PPGTT and PV notification state differently. Type capacity calculations must avoid exposing configurations that exceed low/high GM or fence resources.

### Test Signals
High-value tests include type enumeration on different aperture sizes, create failure injection at each initialization step, activate/deactivate with in-flight workloads, vGPU release versus destroy ordering, DMLR after D3 and non-D3 states, full and per-engine GT reset, EDID/opregion setup on BDW/BXT versus newer ports, and leak checks for IDRs, debugfs, dmabufs, GTT, and submission resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/vgpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_active.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_active.c

### Purpose
`i915_active.c` implements i915's composite GPU activity tracker. It records the latest fence per timeline plus an optional exclusive fence, provides active/retire callbacks around resource lifetime, waits or wires dependencies onto active GPU work, and supports idle barriers that defer retirement through engine kernel-context requests.

### Important APIs, Types, And Functions
The main APIs are `__i915_active_init()`, `i915_active_add_request()`, `i915_active_set_exclusive()`, `i915_active_acquire()`, `i915_active_acquire_if_busy()`, `i915_active_release()`, `__i915_active_wait()`, `i915_request_await_active()`, `i915_sw_fence_await_active()`, `i915_active_fini()`, `i915_active_acquire_preallocate_barrier()`, `i915_active_acquire_barrier()`, `i915_request_add_active_barriers()`, `__i915_active_fence_set()`, `i915_active_fence_set()`, `i915_active_create()`, `i915_active_get()`, `i915_active_put()`, `i915_active_module_init()`, and `i915_active_module_exit()`. Internal state uses `struct active_node`, `struct i915_active`, `struct i915_active_fence`, rb-trees, RCU fence pointers, dma-fence callbacks, low-level lists, and a slab cache.

### Control Flow
Initialization sets locks, the rb-tree, cached node, exclusive tracker, preallocated barrier list, work item, and debug object state. Callers acquire an active ref before adding requests. `i915_active_add_request()` finds or allocates the per-timeline node, replaces pending barriers when needed, installs the request fence callback, and ensures timeline ordering by awaiting the previous fence. Fence callbacks clear the RCU pointer and call `active_retire()`, which decrements the active count and either retires immediately or queues work if retirement may sleep. Final retirement prunes the tree to one reusable cached node, calls the owner's retire callback, wakes waiters, and frees discarded nodes.

Wait and dependency APIs snapshot existing active fences, enable signaling, optionally flush idle barriers, and attach waits to either an i915 request or software fence. Barrier acquisition preallocates per-physical-engine proto-nodes while active, inserts them into the active rb-tree, queues them on engine `barrier_tasks`, and later `i915_request_add_active_barriers()` links them onto a kernel-context barrier request fence so retirement happens after that request.

### State, Persistence, And Dependencies
State persists in `atomic_t count`, `mutex`, `tree_lock`, timeline rb-tree, cached node, `excl` fence, flags, callbacks, work item, preallocated barriers, and the module-global active-node slab cache. RCU protects fence pointer reads, dma-fence locks protect callback list migration, `tree_lock` protects rb-tree mutation, and the active mutex serializes first activation. Dependencies include dma-fence, i915 requests/timelines, engine PM and barrier tasks, debugobjects, workqueues, lockdep, RCU, and the i915 selftest include.

### Integration Points
GEM objects, VMAs, contexts, and other i915 resources embed `struct i915_active` to defer freeing or mutation until GPU access has ceased. Request submission calls `i915_active_add_request()` or `i915_active_fence_set()`. Other requests and software fences call the await helpers to synchronize with current resource activity.

### Risks
The code is highly concurrency-sensitive: fence memory can be RCU-reused, callback lists migrate between old and new fences, active count transitions trigger lifetime callbacks, and barriers are manipulated from low-level lists without the normal timeline lock in some paths. Missing acquire/release pairing can leak activity or retire too early. Barrier proto-nodes use `ERR_PTR(-EAGAIN)` in the fence pointer, so callers must not treat all non-NULL fence values as real fences.

### Test Signals
Signals include i915 selftests for active tracking, concurrent add/wait/release stress, exclusive and per-timeline dependency ordering, RCU fence reuse scenarios, barrier preallocation on virtual and physical engines, `I915_ACTIVE_RETIRE_SLEEPS` workqueue retirement, interruptible wait behavior, module init/exit slab checks, and debugobject assertions under `CONFIG_DRM_I915_DEBUG_GEM`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_active.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_active.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_active.h

### Purpose
`i915_active.h` is the public interface for i915 active fence and composite active tracking. It documents why i915 treats requests as synchronization fences and exposes helpers to set, get, wait on, await, acquire, release, and allocate active trackers.

### Important APIs, Types, And Functions
The header defines `__i915_active_fence_init()`, `INIT_ACTIVE_FENCE`, `i915_active_fence_get()`, `i915_active_fence_isset()`, the `i915_active_init()` lock-class wrapper, `i915_active_wait()`, `__i915_active_acquire()`, `i915_active_is_idle()`, and `__i915_request_await_exclusive()`. It declares all implemented APIs in `i915_active.c` and flags `I915_ACTIVE_AWAIT_EXCL`, `I915_ACTIVE_AWAIT_ACTIVE`, and `I915_ACTIVE_AWAIT_BARRIER`.

### Control Flow
Consumers initialize embedded trackers, acquire an active phase before associating GPU requests, add timeline or exclusive fences, and release when their update is complete. Waiters either block until idle or attach request/software-fence waits to the currently tracked fences. Inline getters use RCU to safely reference the current fence.

### State, Persistence, And Dependencies
The header includes `i915_active_types.h` and `i915_request.h`, and forward-declares request, engine, and timeline types. The persistent state is the `struct i915_active` or `struct i915_active_fence` embedded by callers.

### Integration Points
This is included by GEM, VMA, request, scheduler, and resource lifetime code that needs implicit GPU activity synchronization. `__i915_request_await_exclusive()` is a small convenience used when a request must wait for a resource's exclusive active fence.

### Risks
The documentation highlights a common naming trap: these are dma-fence synchronization objects, not i915 hardware fence registers. `i915_active_fence_isset()` can report stale idle fences because retirement is lazy. Callers using `__i915_active_acquire()` must already hold an active reference.

### Test Signals
Compile coverage across i915 users, lockdep class separation from `i915_active_init()`, RCU fence getter tests, and request await ordering tests are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_active.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_active_types.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_active_types.h

### Purpose
`i915_active_types.h` defines the storage layout for i915 active fence and active tracker objects without pulling in the full active API.

### Important APIs, Types, And Functions
It defines `struct i915_active_fence`, containing an RCU-protected `struct dma_fence *` and callback, and `struct i915_active`, containing reference count, mutex, rb-tree state, cached node, exclusive fence, flags, active/retire callbacks, work item, and preallocated barrier list. It also defines `I915_ACTIVE_RETIRE_SLEEPS`.

### Control Flow
There is no executable flow in this header. The layout supports the implementation's lifecycle: count transitions activate/retire, rb-tree nodes track per-timeline activity, `excl` tracks exclusive activity, work defers sleeping retirement, and `preallocated_barriers` stages barrier nodes.

### State, Persistence, And Dependencies
State persists wherever i915 embeds `struct i915_active`. The header depends on Linux atomics, dma-fence, llist, mutex, rb-tree, RCU, and workqueue types.

### Integration Points
This header lets low-level i915 structures embed active trackers while avoiding larger include dependencies. `i915_active.h` builds the public API on top of these types.

### Risks
The forward-declared `struct active_node` and cache/rb-tree fields are private to `i915_active.c`; external users should not manipulate them. Layout changes can affect lockdep/debugobject assumptions and any structure embedding these types.

### Test Signals
Build coverage and i915 active selftests catch layout and dependency regressions. Runtime lockdep/debugobject tests catch bad lifecycle transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_active_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_bo.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_bo.c

### Purpose
`i915_bo.c` adapts i915 GEM buffer objects to the display-core `intel_display_bo_interface`. It exposes display-facing predicates, panic/debug helpers, framebuffer mmap/read operations, framebuffer validation, and framebuffer object lookup for i915 GEM objects.

### Important APIs, Types, And Functions
The exported object is `i915_display_bo_interface`. Its callbacks are backed by `i915_bo_is_tiled()`, `i915_bo_is_userptr()`, `i915_bo_is_shmem()`, `i915_bo_is_protected()`, `i915_bo_key_check()`, `i915_bo_fb_mmap()`, `i915_bo_read_from_page()`, `i915_bo_describe()`, `i915_bo_framebuffer_init()`, `i915_bo_framebuffer_fini()`, and `i915_bo_framebuffer_lookup()`.

### Control Flow
Framebuffer initialization locks the GEM object, reads tiling and fence stride, and validates the requested framebuffer modifier and pitch against i915 tiling constraints. Legacy addfb infers X tiling but rejects Y tiling. Gen2/3 enforce exact tiling/modifier agreement. Lookup resolves a GEM handle from the DRM file and rejects non-local-memory objects on LMEM-capable devices when the display requires local buffers.

### State, Persistence, And Dependencies
This file does not own persistent state. It reads GEM object tiling, stride, memory placement, protection state, dirty/debug metadata, and PXP key state. Dependencies include display parent interface types, Intel framebuffer modifier helpers, GEM mmap/object helpers, debugfs object description, and PXP key checking.

### Integration Points
The display driver calls this interface for framebuffer creation, panic scanout/readback, mmap support, and BO metadata. DRM framebuffer lookup uses this path to bridge user GEM handles into display-usable objects.

### Risks
Tiling/modifier mismatch can cause corrupt scanout or fence misuse, so validation is strict. Discrete devices must reject remote-memory framebuffer objects. PXP-protected buffers require key checks before display access. Pitch must match fence stride when tiling is active.

### Test Signals
Tests should cover modifier and legacy addfb paths for linear/X/Y tiling, gen2/3 exact tiling enforcement, tiled pitch mismatch, LMEM remote-object rejection, PXP key-check failures, mmap/read-from-page callbacks, and debug description output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_bo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_bo.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_bo.h

### Purpose
`i915_bo.h` declares the i915 display buffer-object interface object.

### Important APIs, Types, And Functions
It declares `extern const struct intel_display_bo_interface i915_display_bo_interface`.

### Control Flow
There is no runtime flow. Display integration code includes this header and binds to the callback table implemented in `i915_bo.c`.

### State, Persistence, And Dependencies
The header carries no state and forward-depends on `struct intel_display_bo_interface` being visible to consumers through display parent interface headers.

### Integration Points
It connects i915 GEM BO support with the shared Intel display code.

### Risks
The header intentionally does not include the interface definition; include ordering must provide it where used. Any name/signature mismatch with `i915_bo.c` breaks link or compile.

### Test Signals
Build integration of display/i915 code is the relevant test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_bo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_cmd_parser.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_cmd_parser.c

### Purpose
`i915_cmd_parser.c` implements the i915 software batch-buffer command parser. It audits user batch buffers for privileged commands, restricted register access, and privileged memory access patterns, then produces a validated shadow batch or trampoline sequence for hardware execution.

### Important APIs, Types, And Functions
Public APIs are `intel_engine_init_cmd_parser()`, `intel_engine_cleanup_cmd_parser()`, `intel_engine_cmd_parser()`, and `i915_cmd_parser_get_version()`. Core types include `struct drm_i915_cmd_descriptor`, `struct drm_i915_cmd_table`, `struct drm_i915_reg_descriptor`, `struct drm_i915_reg_table`, and `struct cmd_node`. Important helpers include command length decoders for gen7/gen9 engines, sorted-table validators, `init_hash_table()`, `find_cmd()`, `find_reg()`, `copy_batch()`, `check_cmd()`, `check_bbstart()`, and `alloc_whitelist()`.

### Control Flow
Engine initialization selects command and register tables based on graphics generation and engine class: gen7 render/video/blitter/VEBOX and gen9 blitter are supported, with gen9 BCS marked as requiring the parser. It validates sorted tables, builds a hash table keyed by opcode, records register whitelist tables, and sets engine flags. Parsing copies the source batch into a shadow GEM object, allocates a bitmap of already executed command indices for recursive BB_START validation when not using a trampoline, canonicalizes original and shadow addresses, and then walks commands until `MI_BATCH_BUFFER_END`.

For each command, the parser finds an explicit or default descriptor, derives length, bounds-checks it against the batch, rejects forbidden commands, validates whitelisted registers and mask/value constraints, validates command bitmask constraints, and rewrites legal `MI_BATCH_BUFFER_START` targets to the equivalent shadow address only if the jump stays inside the batch and targets a previously executed command. In trampoline mode the shadow contains a privileged first execution and a second non-privileged chain; unsafe but hardware-valid batches are redirected to the original non-secure batch.

### State, Persistence, And Dependencies
Persistent per-engine state includes `cmd_hash`, `reg_tables`, `reg_table_count`, `get_cmd_length_mask`, and parser flags. The parser uses temporary shadow object mappings, optional jump whitelist bitmaps, cache flush flags, and register/command static tables. Dependencies include i915 engine metadata, GEM object read/write mapping helpers, DRM cache flush helpers, command/register definitions, WC memcpy optimization, and VMA offsets.

### Integration Points
Request submission code invokes `intel_engine_cmd_parser()` for engines using or requiring parser support. UAPI reports parser availability through `i915_cmd_parser_get_version()`. Cleanup runs during engine teardown. The parser complements hardware parsing by enabling safe secure execution for selected operations and falling back to hardware validation when needed.

### Risks
This is a security boundary. Missing a privileged command, register, GGTT bit, or recursive jump case can grant userspace unauthorized GPU access. Length decoding errors can overrun the batch or skip checks. Register whitelist ordering is required for binary search. `copy_batch()` must handle cache-coherent and WC mappings correctly. The jump whitelist intentionally constrains BB_START recursion and must stay synchronized with command offsets.

### Test Signals
High-value tests include parser init on IVB/HSW/gen9 BCS, sorted-table validation failures, rejected privileged commands, register whitelist accepts/rejects including masked registers, GGTT bit rejection, short-command rejection, batches without BBE, recursive BB_START to current/previous/future/out-of-range commands, trampoline fallback behavior, cache flush/map failure injection, and UAPI version reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_cmd_parser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_cmd_parser.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_cmd_parser.h

### Purpose
`i915_cmd_parser.h` declares the software command parser API used by i915 engine setup and batch submission paths.

### Important APIs, Types, And Functions
It declares `i915_cmd_parser_get_version()`, `intel_engine_init_cmd_parser()`, `intel_engine_cleanup_cmd_parser()`, and `intel_engine_cmd_parser()`, and defines `I915_CMD_PARSER_TRAMPOLINE_SIZE` as 8.

### Control Flow
Consumers initialize parser state per engine, call the parser for candidate batches with source and shadow VMAs, and clean parser state during engine teardown.

### State, Persistence, And Dependencies
The header owns no state. Parser state is stored in `struct intel_engine_cs`; batch storage is represented by `struct i915_vma`.

### Integration Points
It is included by engine initialization, request submission, and any code needing to report parser version support.

### Risks
Callers must pass aligned offsets and lengths and a shadow VMA large enough for parser/trampoline use. The trampoline size constant is part of the allocation contract.

### Test Signals
Build coverage plus parser submission tests that allocate correct shadow/trampoline sizes are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_cmd_parser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_config.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_config.c

### Purpose
`i915_config.c` provides a small configuration helper for dma-fence wait timeouts.

### Important APIs, Types, And Functions
It implements `i915_fence_context_timeout(u64 context)`.

### Control Flow
If `CONFIG_DRM_I915_FENCE_TIMEOUT` is nonzero and the fence context argument is nonzero, the helper converts the configured millisecond timeout to jiffies with `msecs_to_jiffies_timeout()`. Otherwise it returns zero, meaning no timeout.

### State, Persistence, And Dependencies
There is no mutable state. Behavior depends on the kernel config symbol and the context argument. It includes `i915_config.h` and `i915_jiffies.h`.

### Integration Points
i915 code that waits on fences can call this helper, or the `i915_fence_timeout()` wrapper in the header, to use the configured global timeout policy.

### Risks
Context zero explicitly disables timeout even if the config is set. Misinterpreting zero as immediate timeout rather than no timeout would be a caller bug.

### Test Signals
Tests should cover config enabled/disabled builds and context zero versus nonzero inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_config.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_config.h

### Purpose
`i915_config.h` declares fence timeout helpers for i915.

### Important APIs, Types, And Functions
It declares `i915_fence_context_timeout(u64 context)` and defines inline `i915_fence_timeout()` as a call with `U64_MAX`.

### Control Flow
Callers either request a timeout for a specific fence context or use the generic nonzero-context wrapper.

### State, Persistence, And Dependencies
The header has no state and depends on Linux integer limits/types.

### Integration Points
Fence wait call sites include this header to use i915's configured timeout policy.

### Risks
The generic wrapper intentionally forces a nonzero context, so it will enable configured timeout behavior. Callers needing context-zero semantics must call the underlying function directly.

### Test Signals
Compile coverage and direct helper tests for timeout conversion are sufficient.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_debugfs.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_debugfs.c

### Purpose
`i915_debugfs.c` registers i915 debugfs files and implements diagnostic/control views for capabilities, GEM objects, frequencies, swizzling, runtime PM, engines, workaround registers, SSEU, RPS boost state, wedged/reset control, NOA delay, forcewake, and cache dropping.

### Important APIs, Types, And Functions
Exported functions are `i915_debugfs_register()` and `i915_debugfs_describe_obj()`. Important debugfs handlers include `i915_capabilities()`, `i915_gem_object_info()`, `i915_frequency_info()`, `i915_swizzle_info()`, `i915_rps_boost_info()`, `i915_runtime_pm_status()`, `i915_engine_info()`, `i915_wa_registers()`, `i915_wedged_get/set()`, `i915_perf_noa_delay_get/set()`, `i915_drop_caches_get/set()`, `i915_sseu_status()`, and forcewake open/release hooks.

### Control Flow
Registration creates the parameter directory, forcewake control, simple writable control files, standard DRM info files, and GPU error debugfs entries. Read handlers format current driver/device/GT/object state through `seq_file` and `drm_printer`. Writable controls update reset state across GTs, program NOA delay after validating CS timestamp interval bounds, or drop caches by retiring requests, waiting for idle/PM idle, resetting wedged GTs, flushing buffer pools, shrinking GEM memory, running RCU barriers, and draining freed objects.

### State, Persistence, And Dependencies
The file reads and sometimes mutates driver state: i915 params, memory regions, GEM shrink counters, object VMA lists, PAT/cache metadata, swizzle registers, runtime PM usage, RPS fields, engine timelines, WA lists, perf NOA delay, wedged GT state, and GEM caches. Dependencies include DRM debugfs, seq_file, GT PM/debugfs helpers, GEM shrink/buffer-pool code, runtime PM, uncore register reads, RCU, and debugfs params.

### Integration Points
Users and test infrastructure consume these files through debugfs. Display BO debug descriptions call `i915_debugfs_describe_obj()`. Reset/drop-cache knobs integrate with GT reset, request retirement, buffer-pool flushing, and GEM shrinkers.

### Risks
Debugfs control files can perturb the driver: forcewake pins hardware awake, drop-caches waits or resets engines, and wedged writes affect all GTs. Object description walks VMA lists while dropping and reacquiring the object VMA lock around printing, so it must tolerate concurrent changes. Register reads require runtime PM wake refs on older swizzle paths. Debug output exposes kernel/GPU state to privileged debugfs users.

### Test Signals
Signals include debugfs registration on single and multi-GT devices, reading all info files during GPU activity and suspend/resume, forcewake open/release balance, wedged and drop-caches writes, NOA delay bounds validation, object description for GGTT/DPT/PPGTT and normal/partial/rotated/remapped views, and lockdep while objects mutate concurrently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_debugfs.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_debugfs.h

### Purpose
`i915_debugfs.h` declares i915 debugfs registration and GEM-object description helpers, with no-op stubs when debugfs is disabled.

### Important APIs, Types, And Functions
It declares `i915_debugfs_register()` and `i915_debugfs_describe_obj()` under `CONFIG_DEBUG_FS`; otherwise it provides inline empty versions. It forward-declares `struct drm_i915_private`, `struct drm_i915_gem_object`, `struct drm_connector`, and `struct seq_file`.

### Control Flow
Driver init code can call `i915_debugfs_register()` unconditionally because the header compiles it out when debugfs is disabled. Debug output users can similarly call `i915_debugfs_describe_obj()` without local config guards.

### State, Persistence, And Dependencies
The header has no persistent state. It depends on `CONFIG_DEBUG_FS` to choose declarations versus stubs.

### Integration Points
It is used by i915 driver registration and by display BO support that wants to describe GEM objects.

### Risks
When debugfs is disabled, callers get no output or registration side effects. Code must not rely on debugfs helpers for functional behavior.

### Test Signals
Builds with `CONFIG_DEBUG_FS=y` and disabled debugfs validate both branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_debugfs_params.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_debugfs_params.c

### Purpose
`i915_debugfs_params.c` creates debugfs files for i915 module/runtime parameters and implements typed read/write handlers for integer, unsigned integer, boolean, unsigned long, and string parameters.

### Important APIs, Types, And Functions
The exported function is `i915_debugfs_params()`. Internal handlers include `i915_param_int_show/open/write()`, `i915_param_uint_show/open/write()`, `i915_param_charp_show/open/write()`, typed `file_operations` for read-write and read-only modes, `notify_guc()`, typed create helpers, and `_i915_param_create_file()`.

### Control Flow
`i915_debugfs_params()` creates an `i915_params` directory under the DRM debugfs root, then iterates `I915_PARAMS_FOR_EACH()` and creates one file per parameter with the mode declared in parameter metadata. Reads print the current value. Writes parse integers or booleans for int/uint parameters; string writes replace the old string with `strndup_user()`. Writing the unsigned `reset` parameter additionally updates GuC global policies on GTs using GuC submission and rolls back the value on failure.

### State, Persistence, And Dependencies
Files point directly at fields in `struct i915_params`, using unsafe debugfs file creation for numeric values. String writes allocate new memory and free the previous pointer. Dependencies include Linux debugfs, seq_file, i915 params metadata, GT iteration, GuC policy update, and container macros to recover `drm_i915_private` from a parameter pointer.

### Integration Points
`i915_debugfs_register()` calls this during debugfs setup. Developers and tests use the files to inspect and, for writable params, alter driver parameter state at runtime.

### Risks
`debugfs_create_file_unsafe()` assumes the i915 device and params outlive the debugfs entries. Writable parameters can affect live driver behavior, and only `reset` has a special GuC synchronization path here. String writes accept up to `PAGE_SIZE` and replace pointers without additional semantic validation.

### Test Signals
Tests should verify directory/file creation for all parameter types and modes, int/uint boolean parsing, read-only mode refusing writes, string replacement and free behavior, reset writes with GuC policy success/failure rollback, and device teardown while debugfs files exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_debugfs_params.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_debugfs_params.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_debugfs_params.h

### Purpose
`i915_debugfs_params.h` declares the helper that creates debugfs parameter files for an i915 device.

### Important APIs, Types, And Functions
It declares `struct dentry *i915_debugfs_params(struct drm_i915_private *i915)`.

### Control Flow
Debugfs registration code calls the function and receives the created directory dentry or an error dentry.

### State, Persistence, And Dependencies
The header holds no state and forward-declares `struct dentry` and `struct drm_i915_private`.

### Integration Points
It connects `i915_debugfs.c` with the parameter-file implementation.

### Risks
Callers should treat the return as debugfs best-effort infrastructure and not as required device functionality.

### Test Signals
Build coverage and debugfs registration tests cover this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_debugfs_params.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_deps.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_deps.c

### Purpose
`i915_deps.c` implements a small dependency collection for dma-fences used by i915 migration/unbind paths. It coalesces fences by context, stores referenced fences in a growable array, and can synchronously wait on them when collection or later synchronization requires it.

### Important APIs, Types, And Functions
The public APIs are `i915_deps_init()`, `i915_deps_fini()`, `i915_deps_add_dependency()`, `i915_deps_add_resv()`, and `i915_deps_sync()`. Internal helpers are `i915_deps_reset_fences()` and `i915_deps_grow()`. The state type is `struct i915_deps`.

### Control Flow
Initialization points the fence array at inline single-fence storage. Adding a dependency ignores NULL fences, returns signaled fence errors immediately, replaces older same-context fences with later ones, or appends a referenced fence by growing the array. If growth allocation fails, it waits for the incoming fence according to `ttm_operation_ctx`; `no_wait_gpu` produces `-EBUSY` for unsignaled fences. Reservation import iterates all read/write reservation fences and adds them. Sync walks collected fences, waits according to the TTM operation context, and stops at the first wait or fence error.

### State, Persistence, And Dependencies
`struct i915_deps` stores an inline `single` pointer, the active fence pointer array, count, capacity, and allocation GFP flags. The code holds references on all stored fences until `i915_deps_fini()`. Dependencies include dma-fence, dma-resv iteration, TTM operation context, and kernel allocation helpers.

### Integration Points
GT migration and async unbind code can feed collected dependencies into later fence-array or synchronization logic, while avoiding redundant older fences from the same timeline/context.

### Risks
On add failure the helper finalizes the whole collection, so callers must not continue using stored fences as if they remain referenced. Context-zero fences are never coalesced. Allocation failure fallback can block unless `no_wait_gpu` forbids it. Fence error propagation is deliberate and aborts collection/sync.

### Test Signals
Tests should cover single-fence inline storage, growth to heap storage, same-context older/later replacement, context-zero non-coalescing, signaled error fences, allocation failure with wait and no-wait contexts, reservation object import, interruptible waits, and fini idempotence assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_deps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_deps.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_deps.h

### Purpose
`i915_deps.h` defines the i915 fence dependency collection type and declares its management APIs.

### Important APIs, Types, And Functions
It defines `struct i915_deps` with inline single-fence storage, a fence pointer array, count, capacity, and GFP mode. It declares `i915_deps_init()`, `i915_deps_fini()`, `i915_deps_add_dependency()`, `i915_deps_add_resv()`, and `i915_deps_sync()`.

### Control Flow
Users initialize, add fences or reservation-object fences, optionally sync, and finalize to drop references and free heap storage.

### State, Persistence, And Dependencies
The collection owns references to stored dma-fences until finalized. The header forward-declares `ttm_operation_ctx`, `dma_fence`, and `dma_resv`.

### Integration Points
Migration, TTM, and unbind paths include this header when they need to collect and wait on explicit or reservation-derived dependencies.

### Risks
The API contract requires `i915_deps_fini()` after successful initialization. After add errors, the implementation has already finalized the collection, so caller cleanup paths must account for that.

### Test Signals
Compile tests and dependency collection unit/selftests validate struct usage and lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_deps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_display_pc8.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_display_pc8.c

### Purpose
`i915_display_pc8.c` implements the i915 side of the display PC8 blocking interface. It prevents entry into deep PC8 power state by holding GT forcewake and releases that block on demand.

### Important APIs, Types, And Functions
The exported object is `i915_display_pc8_interface`, with callbacks `i915_display_pc8_block()` and `i915_display_pc8_unblock()`.

### Control Flow
`block()` recovers `intel_uncore` from the DRM device and calls `intel_uncore_forcewake_get(FORCEWAKE_ALL)`. `unblock()` calls the matching `intel_uncore_forcewake_put(FORCEWAKE_ALL)`.

### State, Persistence, And Dependencies
The file owns no state, but forcewake reference counts persist in uncore/runtime PM state. Dependencies include the display parent PC8 interface, i915 device conversion, and uncore forcewake helpers.

### Integration Points
Shared Intel display power-management code calls this interface when display operations need to prevent PC8 residency.

### Risks
Block/unblock imbalance will keep hardware awake or release forcewake too early. The callbacks assume the DRM device belongs to i915 and that uncore state is initialized.

### Test Signals
Power-management tests should verify balanced forcewake refs across display PC8 block/unblock, suspend/resume behavior, and no PC8 entry during blocked sections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_display_pc8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_display_pc8.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_display_pc8.h

### Purpose
`i915_display_pc8.h` declares the i915 implementation of the shared Intel display PC8 interface.

### Important APIs, Types, And Functions
It declares `extern const struct intel_display_pc8_interface i915_display_pc8_interface`.

### Control Flow
There is no executable logic. Display initialization code binds to the callback table implemented in `i915_display_pc8.c`.

### State, Persistence, And Dependencies
The header has no state and relies on consumers having the interface type available.

### Integration Points
It connects i915 uncore forcewake handling to the display power-management layer.

### Risks
As with other minimal interface headers, include ordering must provide the interface type where needed.

### Test Signals
Build integration and display power-management tests cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_display_pc8.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_dpt.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_dpt.c

### Purpose
`i915_dpt.c` implements i915 display page tables (DPT) as a specialized `i915_address_space` backed by a GEM object. It allocates the page-table object, writes gen8 PTEs into an iomapped GGTT pin, binds display VMAs into the DPT, and exposes lifecycle callbacks to shared display code.

### Important APIs, Types, And Functions
The key type is private `struct intel_dpt`, embedding `struct i915_address_space` plus the backing GEM object, GGTT VMA, and iomem pointer. Public functions are `i915_dpt_to_vm()`, `i915_dpt_pin_to_ggtt()`, `i915_dpt_unpin_from_ggtt()`, `i915_dpt_offset()`, and `i915_display_dpt_interface`. Internal helpers include `i915_vm_to_dpt()`, `dpt_insert_page()`, `dpt_insert_entries()`, `dpt_clear_range()`, `dpt_bind_vma()`, `dpt_unbind_vma()`, `dpt_cleanup()`, `i915_dpt_create()`, `i915_dpt_destroy()`, `i915_dpt_suspend()`, and `i915_dpt_resume()`.

### Control Flow
Creation sizes the DPT object from the target object size or explicit page count, allocates contiguous LMEM first, stolen memory if GGTT aperture exists, or shmem on non-LMEM platforms, sets cache level to uncached, initializes an address space with DPT class and GGTT PTE encoder, and marks the object as DPT. Pinning takes runtime PM, increments pending framebuffer pin accounting, locks the object with ww retry handling, pins it into GGTT, maps it with `i915_vma_pin_iomap()`, stores the VMA/iomem, marks the object dirty, and drops PM/accounting refs. Binding writes PTEs for VMA backing pages and marks both global and local bind flags because DPT has one PTE space. Destroy clears `is_dpt` and drops the VM reference; cleanup drops the object ref.

### State, Persistence, And Dependencies
Persistent DPT state includes the embedded VM, backing object, pinned VMA, iomap pointer, `vm->total`, DPT flag, PTE encoder, bind/unbind ops, and object `is_dpt` marker. Dependencies include GEM internal/LMEM/stolen/shmem allocation, GGTT pin/iomap helpers, i915 address-space init, gen8 PPGTT definitions, display restore pending pin accounting, runtime PM, and suspend/resume GGTT VM helpers.

### Integration Points
Shared display DPT code calls `i915_display_dpt_interface.create/destroy/suspend/resume`. Framebuffer/display code pins DPTs to GGTT, obtains offsets for hardware programming, and unpins them during teardown. Debugfs object description treats DPT VMAs as a distinct VMA type.

### Risks
`dpt_clear_range()` is empty, so unbind does not scrub PTEs; correctness depends on DPT lifetime and rebind behavior. PTE_READ_ONLY is ignored in `dpt_insert_entries()` with a warning that callers must not let users override read-only access. Pin/unpin balance for both iomap and VMA refs is critical. Allocation fallback changes memory domain and cache behavior. The DPT object is marked dirty after pinning because display hardware reads it.

### Test Signals
Tests should cover LMEM, stolen, and shmem allocation fallback; cache-level failure unwind; GGTT pin/iomap failure unwind; bind entries with LMEM/read-only flags; DPT offset reporting; suspend/resume callbacks; pin/unpin reference balance; and display scanout using DPT-backed framebuffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_dpt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_dpt.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_dpt.h

### Purpose
`i915_dpt.h` declares i915 display page-table helpers and the display DPT interface object.

### Important APIs, Types, And Functions
It forward-declares `struct intel_dpt`, `struct i915_address_space`, and `struct i915_vma`, and declares `i915_dpt_to_vm()`, `i915_dpt_pin_to_ggtt()`, `i915_dpt_unpin_from_ggtt()`, `i915_dpt_offset()`, and `i915_display_dpt_interface`.

### Control Flow
Display code creates a DPT through the interface, converts it to an address space for binding, pins it to GGTT for hardware visibility, reads the offset, and later unpins/destroys it.

### State, Persistence, And Dependencies
The header owns no state. State is hidden in the private `struct intel_dpt` implementation.

### Integration Points
It is the bridge between shared Intel display code and i915-specific DPT address-space/GEM handling.

### Risks
The `struct intel_dpt` internals are intentionally opaque; callers must use the declared helpers and interface callbacks to preserve pin and VM lifetime rules.

### Test Signals
Build integration with display DPT users and runtime DPT pin/unpin tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_dpt.h -->
