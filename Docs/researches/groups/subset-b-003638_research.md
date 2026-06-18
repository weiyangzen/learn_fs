# subset-b-003638 Research

Grouped worker report for DRM driver files under Lima, LogiCVC, and Loongson. Each section preserves the source path and is bounded by reconciliation markers for per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_regs.h

Purpose: central register and bitfield catalog for the Lima Mali Utgard DRM driver. It defines PMU, L2 cache, GP, PP, MMU, VM page-table, DLBU, and broadcast register offsets used by the Lima device, scheduler, MMU, L2, GP, PP, and DLBU code.

Important APIs/types/functions: this header exports macros only. Key groups include `LIMA_PMU_*`, `LIMA_L2_CACHE_*`, `LIMA_GP_*`, `LIMA_PP_*`, `LIMA_MMU_*`, `LIMA_VM_FLAG_*`, `LIMA_VM_FLAGS_CACHE`, and `LIMA_VM_FLAGS_UNCACHE`.

Control flow: no executable flow exists here; runtime code consumes the constants when powering blocks, flushing cache, starting GP/PP jobs, masking/clearing interrupts, switching MMU page directories, and forming PTE values.

State and persistence: the header encodes hardware state layout, not driver-owned state. VM flag macros are persistent ABI assumptions for page-table entries and must match the Mali MMU format.

Dependencies and integration points: depends on Linux `BIT()`/`GENMASK()` style bit helpers from includers. Integrated by `lima_vm.c`, GP/PP/MMU/L2/PMU modules, and error recovery paths.

Risks and test signals: wrong masks or offsets can cause hangs, bogus page faults, missed interrupts, or memory corruption. Test by exercising GP and PP submits, MMU faults, cache flushes, suspend/resume power sequencing, and register dumps on Mali-400 and Mali-450 variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_sched.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_sched.c

Purpose: implements Lima's DRM GPU scheduler backend, per-pipe fences, runtime PM bracketing, VM switching, timeout/error recovery, and error-task capture.

Important APIs/types/functions: `lima_sched_slab_init/fini`, `lima_sched_task_init/fini`, `lima_sched_context_init/fini`, `lima_sched_context_queue_task`, `lima_sched_pipe_init/fini`, and `lima_sched_pipe_task_done`. Internal anchors are `struct lima_fence`, `lima_sched_run_job`, `lima_sched_timedout_job`, `lima_sched_build_error_task_list`, and `lima_sched_recover_work`.

Control flow: userspace submission creates a `lima_sched_task`, arms a `drm_sched_job`, pushes it to the scheduler, and receives the finished fence. `run_job` resumes runtime PM, creates a pipe fence, records `current_task`, flushes L2 caches, switches MMU(s) to the task VM, traces the run, and calls pipe-specific `task_run`. IRQ completion calls `lima_sched_pipe_task_done`, which either signals the fence and idles PM or schedules recovery/fault handling. Timeout handling masks processor IRQs, stops the scheduler, records blame, optionally dumps task buffers, resumes page faults, clears current state, idles PM, resubmits jobs, and restarts the scheduler.

State and persistence: pipe state includes current task/VM, fence context/sequence, error flag, work item, and callback table. Task state holds BO references, VM ref, frame, heap, recoverability, and pipe fence. Error dumps persist in `ldev->error_task_list` until consumed elsewhere.

Dependencies and integration points: depends on DRM scheduler/fence APIs, Lima PM/devfreq, MMU, L2 cache, GEM/BO, tracepoints, and pipe-specific GP/PP callbacks. It is the bridge between submit ioctls and hardware engines.

Risks and test signals: race windows around IRQ latency, timeout versus fence completion, and RCU fence release are critical. BO/VM reference leaks or missing `lima_vm_bo_del` can leak VA mappings. Test with normal submits, forced hangs, MMU faults, reset recovery, runtime suspend/resume, and debug dump retrieval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_sched.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_sched.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_sched.h

Purpose: declares Lima scheduler data structures and entry points shared by submit, GP/PP, MMU, and device lifecycle code.

Important APIs/types/functions: `struct lima_sched_task`, `struct lima_sched_context`, `struct lima_sched_pipe`, and `struct lima_sched_error_task`. Public functions cover task init/fini, entity init/fini, job queueing, pipe init/fini, task completion, slab init/fini, and the inline `lima_sched_pipe_mmu_error`.

Control flow: pipe users fill callback slots (`task_validate`, `task_run`, `task_fini`, `task_error`, `task_mmu_error`, `task_recover`, `task_mask_irq`) before initializing the DRM scheduler. Running jobs update `current_task` and `current_vm`, while MMU error paths mark `pipe->error` and delegate to pipe-specific handling.

State and persistence: the header defines persistent in-memory scheduler state: fence counters, current VM ref, arrays of MMU/L2/processor IP blocks, broadcast IPs, task slab, error flag, done mask, atomic task count, and recovery work. `struct lima_sched_task` owns BO references and a VM ref across job lifetime.

Dependencies and integration points: imports `drm/gpu_scheduler.h`, Linux lists, xarray, and Lima device/VM forward declarations. It is consumed by scheduler implementation plus processor-specific modules.

Risks and test signals: callback contract mismatches can crash during timeout or completion. Array maximums must cover hardware topology. Test by initializing GP and PP pipes on all supported SoCs, exercising MMU errors, and checking fence completion/cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_sched.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_trace.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_trace.c

Purpose: instantiates Lima tracepoints declared in `lima_trace.h`.

Important APIs/types/functions: defines `CREATE_TRACE_POINTS` and includes `lima_trace.h` after including `lima_sched.h`, causing the kernel trace infrastructure to emit storage and metadata for the trace events.

Control flow: no runtime control flow beyond compile-time tracepoint generation. Scheduler code calls `trace_lima_task_submit` and `trace_lima_task_run` when tracepoints are enabled.

State and persistence: tracepoint state is maintained by the kernel tracing subsystem, not this file. It persists only as runtime trace buffers when tracing is active.

Dependencies and integration points: depends on `lima_sched.h` for `struct lima_sched_task` visibility and on Linux tracepoint generation through `trace/define_trace.h` in the header.

Risks and test signals: include ordering and `TRACE_INCLUDE_PATH` must remain correct or build breaks. Test by building the driver with tracepoints enabled and verifying `lima:lima_task_submit` and `lima:lima_task_run` appear under tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_trace.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_trace.h

Purpose: declares Lima scheduler trace events for task submission and task execution.

Important APIs/types/functions: `DECLARE_EVENT_CLASS(lima_task)` captures finished fence context, seqno, and scheduler pipe name from `struct lima_sched_task`. `DEFINE_EVENT` creates `lima_task_submit` and `lima_task_run`.

Control flow: event call sites in `lima_sched.c` pass a task pointer. The fast assignment reads `task->base.s_fence->finished` metadata and scheduler name, then `TP_printk` formats the trace line.

State and persistence: trace events record transient task scheduling metadata into ftrace/perf buffers when enabled. No Lima-owned persistent state is modified.

Dependencies and integration points: uses Linux tracepoint macros and requires `TRACE_INCLUDE_PATH ../../drivers/gpu/drm/lima` so generated trace code can locate the header from build output.

Risks and test signals: dereferencing scheduler/fence fields assumes task init/arm completed before trace calls. Test with ftrace enabled during command submission and confirm both submit and run events carry coherent context/seqno/pipe values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_vm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_vm.c

Purpose: implements Lima GPU virtual address spaces, BO-to-VA tracking, page-table allocation, mapping, unmapping, and VM lifetime management.

Important APIs/types/functions: internal `struct lima_bo_va` binds a BO to a VM with a `drm_mm_node` and refcount. Public functions include `lima_vm_bo_add`, `lima_vm_bo_del`, `lima_vm_get_va`, `lima_vm_create`, `lima_vm_release`, `lima_vm_print`, and `lima_vm_map_bo`.

Control flow: `lima_vm_create` allocates a write-combined page directory, optionally maps the reserved DLBU page, and initializes a `drm_mm` VA allocator. `lima_vm_bo_add` finds or creates a per-BO VA record, allocates VA space, lazily allocates page-table bundles, and maps every DMA page with cacheable permissions. Delete decrements the BO-VA refcount, clears PTEs, removes the `drm_mm_node`, and frees the VA record. `lima_vm_map_bo` remaps later BO pages from a page offset, used for heap growth.

State and persistence: VM state is in-memory and refcounted with `kref`. Page directory and page-table bundles are DMA-coherent/write-combined allocations visible to hardware until VM release. BO VA records live on each BO's `va` list and are protected by `bo->lock`; `vm->lock` protects `drm_mm` and PTE mutation.

Dependencies and integration points: consumes Lima BO/GEM scatter-gather tables, device VA bounds, reserved DLBU DMA address, `drm_mm`, DMA mapping, and VM flag macros from `lima_regs.h`. Scheduler switches MMUs to these VMs before running jobs.

Risks and test signals: `lima_vm_bo_del` assumes a mapping exists; missing add/del pairing can underflow or crash. Partial mapping failure must unmap already written PTEs. Test BO submission, heap remapping, VA reuse, VM refcount release, DLBU reservation, and MMU fault diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_vm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_vm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_vm.h

Purpose: declares Lima VM layout constants, VM page structures, VM object state, and public VM management helpers.

Important APIs/types/functions: page constants (`LIMA_PAGE_SIZE`, `LIMA_PAGE_ENT_NUM`), bundle table sizing (`LIMA_VM_NUM_PT_PER_BT`, `LIMA_VM_NUM_BT`), reserved VA range for DLBU, `struct lima_vm_page`, `struct lima_vm`, and helpers `lima_vm_get/put`.

Control flow: callers create a VM, add BOs before submission, query BO VA for command streams or error dumps, optionally map additional BO pages, and release refs through `lima_vm_put`.

State and persistence: `struct lima_vm` owns a mutex, kref, `drm_mm`, Lima device pointer, one page directory, and bundle table pages. Its lifetime is explicit through `kref`.

Dependencies and integration points: depends on DRM MM and Linux kref. It is included by scheduler, submit, GEM, MMU, and device code.

Risks and test signals: VA reserve constants must align with device VA configuration; table sizing must match `lima_vm.c` index macros. Test compile coverage plus runtime submits that switch VMs and free contexts under job pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_vm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/Kconfig

Purpose: defines the build-time configuration symbol for the Xylon LogiCVC DRM driver.

Important APIs/types/functions: `config DRM_LOGICVC` is tristate, depends on `DRM` and `OF || COMPILE_TEST`, and selects DRM client selection, KMS helper, DMA KMS helper, DMA GEM helper, `REGMAP`, and `REGMAP_MMIO`.

Control flow: no runtime flow. Kconfig controls whether the driver is built in, as a module, or omitted.

State and persistence: persists only in kernel configuration. It influences whether `logicvc-drm.o` is linked by the Makefile.

Dependencies and integration points: reflects actual source dependencies on device tree, regmap MMIO, DRM atomic/KMS, GEM DMA, and fbdev client setup.

Risks and test signals: missing selects would cause link or compile failures in minimal configs. Test with `COMPILE_TEST`, OF-enabled platform builds, module build, and allmodconfig-style coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/Makefile

Purpose: lists the object files that form the `logicvc-drm` module.

Important APIs/types/functions: `logicvc-drm-y` includes CRTC, DRM probe/core, interface, layer, mode, and OF parser objects. `obj-$(CONFIG_DRM_LOGICVC)` links them as `logicvc-drm.o`.

Control flow: build-system only; no runtime behavior.

State and persistence: build composition persists in generated objects/modules.

Dependencies and integration points: must match symbols declared across `logicvc_*.h`, especially probe calling layer/CRTC/interface/mode init in sequence.

Risks and test signals: omitting an object breaks unresolved symbols; adding stale objects breaks builds. Test module and built-in configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_crtc.c

Purpose: implements the single LogiCVC CRTC, including mode timing programming, control-signal polarity, vblank event management, IRQ-driven page-flip completion, and CRTC registration.

Important APIs/types/functions: `logicvc_crtc_init`, `logicvc_crtc_vblank_handler`, CRTC helper callbacks `mode_valid`, `atomic_begin`, `atomic_enable`, `atomic_disable`, and CRTC funcs for vblank enable/disable.

Control flow: atomic enable computes porch/sync/active timing fields from adjusted mode and writes LogiCVC timing registers. It configures HSYNC/VSYNC/DE and clock polarity from mode flags and connector bus flags, resets internal state through `LOGICVC_DTYPE_REG`, enables vblank, and captures pending flip events. Atomic begin handles events for already-active CRTCs; atomic disable shuts off vblank/control bits and sends leftover events synchronously. IRQ handling calls `logicvc_crtc_vblank_handler`, which invokes DRM vblank handling and sends stored events.

State and persistence: `struct logicvc_crtc` stores the DRM CRTC and one pending `drm_pending_vblank_event`. Hardware timing/control registers persist until reprogrammed or reset.

Dependencies and integration points: depends on regmap, DRM atomic/vblank helpers, connector bus flags through `logicvc->interface`, primary layer from `logicvc_layer_get_primary`, and OF graph port 1.

Risks and test signals: event handling must pair `drm_crtc_vblank_get/put`; missed IRQs can hang page flips. Test modesets with positive/negative sync flags, panel bus flags, page flips on active and enabling CRTCs, disable with pending event, and vblank interrupt masking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_crtc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_crtc.h

Purpose: declares the LogiCVC CRTC wrapper and public CRTC entry points.

Important APIs/types/functions: `struct logicvc_crtc` embeds `struct drm_crtc` and holds a pending vblank event pointer. Exports `logicvc_crtc_vblank_handler` and `logicvc_crtc_init`.

Control flow: the core probe path calls `logicvc_crtc_init`; the top-level IRQ handler calls `logicvc_crtc_vblank_handler`.

State and persistence: pending event state is stored between atomic commit and vblank IRQ. No persistent storage beyond runtime DRM object state.

Dependencies and integration points: forward-declares DRM pending event and `logicvc_drm`. Used by core DRM, IRQ, and interface/layer setup.

Risks and test signals: structure ownership assumes one CRTC per device. Test initialization order with primary layer present and vblank event delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_crtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_drm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_drm.c

Purpose: platform-driver core for LogiCVC. It owns probe/remove/shutdown, DRM driver registration, regmap setup, reserved memory handling, clocks, IRQ handling, device-tree config parsing, and top-level component initialization.

Important APIs/types/functions: `logicvc_drm_probe`, `logicvc_drm_remove`, `logicvc_drm_shutdown`, `logicvc_drm_irq_handler`, `logicvc_drm_gem_dma_dumb_create`, `logicvc_drm_config_parse`, `logicvc_clocks_prepare/unprepare`, and caps matching.

Control flow: probe initializes reserved memory, obtains parent syscon regmap or maps MMIO and creates regmap, requests IRQ, allocates `logicvc_drm`, matches IP version, prepares clocks, parses DT config and layers count, initializes DRM mode config, layers, CRTC, interface, KMS mode config, registers the DRM device, and starts client setup. Remove unregisters, performs atomic shutdown, finalizes mode polling, disables clocks, and releases reserved memory.

State and persistence: `struct logicvc_drm` stores caps, parsed config, regmap, reserved memory base, clocks, layer list, CRTC, and interface. Hardware registers persist until shutdown or next modeset.

Dependencies and integration points: platform OF matching for `xylon,logicvc-*`, Linux reserved memory, syscon/regmap MMIO, clocks, DRM GEM DMA/fbdev helpers, and local layer/CRTC/interface/mode/OF helpers.

Risks and test signals: error unwinding must disable clocks and release reserved memory. Parent syscon fallback must handle both shared and direct register mappings. Test probe deferral for panels/bridges, missing clocks/IRQ/layers, dumb buffer pitch, IRQ vblank delivery, and remove/shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_drm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_drm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_drm.h

Purpose: defines top-level LogiCVC configuration, capability, and device structures.

Important APIs/types/functions: display interface/colorspace constants, `logicvc_drm(d)` container helper, `struct logicvc_drm_config`, `struct logicvc_drm_caps`, and `struct logicvc_drm`.

Control flow: no executable flow; probe fills config/caps and submodules consume fields during mode, layer, and interface initialization.

State and persistence: `logicvc_drm` is the runtime state root: DRM device, reserved memory base, regmap, clocks, layer list, CRTC pointer, and interface pointer.

Dependencies and integration points: includes Linux regmap and DRM device definitions. Shared by all LogiCVC C files.

Risks and test signals: config semantics must match DT parser and layer/interface users. Test multiple IP versions and display interfaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_interface.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_interface.c

Purpose: creates the LogiCVC output interface: encoder, optional native connector, panel, or bridge, plus panel power sequencing.

Important APIs/types/functions: `logicvc_interface_init`, `logicvc_interface_attach_crtc`, encoder helper `enable/disable`, connector `get_modes`, and mapping helpers for encoder/connector type.

Control flow: init allocates `logicvc_interface`, discovers panel or bridge through `drm_of_find_panel_or_bridge`, initializes encoder type from configured display interface, optionally initializes a connector for native DVI or panel-backed outputs, attaches connector to encoder, and attaches bridge if present. Encoder enable turns on `LOGICVC_POWER_CTRL_VIDEO_ENABLE` and prepares/enables panel; disable reverses panel state.

State and persistence: stores encoder, connector, and panel/bridge pointers in `logicvc->interface`. Hardware video power bit remains set until disabled or reset.

Dependencies and integration points: depends on DRM OF, panel, bridge, connector, encoder, and probe helper APIs; consumes display interface config from `logicvc_drm.h`; attaches to the CRTC after CRTC creation.

Risks and test signals: native DVI mode probing is not implemented, so native connector without panel returns no modes. Panel/bridge probe deferral must be propagated. Test RGB/LVDS/DVI configs, panel get_modes, bridge attach, and encoder enable/disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_interface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_interface.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_interface.h

Purpose: declares LogiCVC output-interface state and setup helpers.

Important APIs/types/functions: `struct logicvc_interface` embeds a DRM encoder and connector and stores optional `drm_panel`/`drm_bridge`. Exports `logicvc_interface_init` and `logicvc_interface_attach_crtc`.

Control flow: core probe calls init, then attach after CRTC setup.

State and persistence: interface object persists for DRM device lifetime under devm allocation. It is the output endpoint for atomic modesets.

Dependencies and integration points: includes DRM bridge, connector, encoder, and panel headers. Consumed by CRTC for bus flags and by mode/probe setup.

Risks and test signals: assumes one output interface per device. Test with bridge-only, panel connector, and native connector paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_interface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_layer.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_layer.c

Purpose: implements LogiCVC hardware layers as DRM planes, including DT layer parsing, format selection, atomic plane validation/update/disable, reserved-memory offset mapping for older IP, alpha, zpos, and layer list management.

Important APIs/types/functions: `logicvc_layers_init`, `logicvc_layers_attach_crtc`, `logicvc_layer_get_*`, `logicvc_layer_buffer_find_setup`, and internal `logicvc_plane_atomic_check/update/disable`.

Control flow: layer init walks the `layers` DT node, filters `layer` children, parses per-layer properties, resolves supported DRM formats from colorspace/depth/alpha, skips the final background layer if configured, initializes a primary or overlay plane, creates alpha/zpos properties, and appends it to `layers_list`. Atomic check rejects negative positions, verifies reserved-memory offset feasibility on IP without direct layer-address registers, and delegates no-scaling checks to DRM. Atomic update writes size, address or buffer/offset selectors, position, alpha, and control bits. Disable clears the layer control register.

State and persistence: each `struct logicvc_layer` stores parsed config, format table, OF node, DRM plane, list node, and hardware index. Hardware layer registers persist until changed.

Dependencies and integration points: depends on DRM atomic/plane/blend/fb DMA helpers, OF parsing helpers, LogiCVC caps/config, reserved memory base, regmap, and CRTC dimensions.

Risks and test signals: older IP address derivation is sensitive to reserved memory base, base offset, buffer offset, row stride, and pixel size. Plane positioning is only allowed for configurable non-final overlays. Test direct-address and offset-based IP versions, alpha modes, primary layer detection, background layer, unsupported formats, and page flips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_layer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_layer.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_layer.h

Purpose: declares LogiCVC layer/plane configuration structures and layer helper APIs.

Important APIs/types/functions: layer colorspace/alpha constants, `struct logicvc_layer_buffer_setup`, `struct logicvc_layer_config`, `struct logicvc_layer_formats`, `struct logicvc_layer`, and lookup/init/attach helpers.

Control flow: no executable flow; defines the data contract used by layer parsing and plane updates.

State and persistence: per-layer runtime state includes parsed DT config and associated DRM plane. Buffer setup is transient output from offset computation.

Dependencies and integration points: includes OF and DRM plane headers and is shared by core, CRTC, and layer code.

Risks and test signals: fields must remain synchronized with `logicvc_of.c` property parser and `logicvc_layer.c` format tables. Test DT parsing and plane creation with varied layer depths and alpha modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_layer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_mode.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_mode.c

Purpose: initializes and finalizes DRM mode configuration for LogiCVC.

Important APIs/types/functions: `logicvc_mode_init`, `logicvc_mode_fini`, and `logicvc_mode_config_funcs` with GEM framebuffer creation and atomic check/commit helpers.

Control flow: init initializes vblank support for the configured CRTC count, finds the primary layer to derive preferred depth, sets min/max dimensions and mode config funcs, resets mode config, and starts KMS helper polling. Fini stops polling.

State and persistence: populates `drm_dev->mode_config` fields and vblank state. Preferred depth persists in DRM mode config for clients.

Dependencies and integration points: depends on primary layer initialization having completed, DRM vblank, GEM framebuffer helper, atomic helper, and polling helper APIs.

Risks and test signals: max dimensions are fixed at 2048 and may reject wider hardware configs. Missing primary layer aborts KMS init. Test vblank initialization, fb creation, hotplug polling, and preferred depth for alpha and non-alpha primary layers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_mode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_mode.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_mode.h

Purpose: declares mode configuration lifecycle hooks for LogiCVC.

Important APIs/types/functions: `logicvc_mode_init` and `logicvc_mode_fini`.

Control flow: core probe calls init after CRTC/interface setup; remove calls fini before clock teardown.

State and persistence: no state in the header; mode state lives in `drm_device`.

Dependencies and integration points: forward-declares `logicvc_drm` and is included by the core DRM file.

Risks and test signals: lifecycle order must match probe/remove. Test probe failure unwinding after mode init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_mode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_of.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_of.c

Purpose: parses and validates LogiCVC device-tree properties for display and layer configuration.

Important APIs/types/functions: static string/value tables for display interface/colorspace and layer colorspace/alpha mode; property descriptor table; `logicvc_of_property_parse_u32`, `logicvc_of_property_parse_bool`, and `logicvc_of_node_is_layer`.

Control flow: `parse_u32` validates property index, enforces required properties, reads either strings mapped through `logicvc_of_property_sv_value` or numeric u32 values, applies optional ranges, and writes the result. Boolean parsing returns presence. Node helper matches child node name `layer`.

State and persistence: property metadata is static. Parsed values persist in `logicvc_drm_config` or `logicvc_layer_config`.

Dependencies and integration points: depends on Linux OF APIs, DRM print support, and constants from `logicvc_drm.h` and `logicvc_layer.h`. Called by core and layer config parsing.

Risks and test signals: descriptor ranges currently constrain layer colorspace to RGB only, so YUV layer strings are declared but not accepted. Missing required properties return `-ENODEV`. Test valid/invalid DT bindings, optional booleans, string enum parsing, and range failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_of.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_of.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_of.h

Purpose: declares LogiCVC OF property IDs, property metadata structs, and parser helpers.

Important APIs/types/functions: `enum logicvc_of_property_index`, `struct logicvc_of_property_sv`, `struct logicvc_of_property`, and parse/node helper prototypes.

Control flow: no executable flow; the enum indexes the descriptor table in `logicvc_of.c`.

State and persistence: property descriptors define required/optional and range semantics used during probe.

Dependencies and integration points: used by core config parsing and layer parsing. Expects Linux device-node types from includers.

Risks and test signals: enum order must match descriptor table entries. Test compile coverage and DT parsing for every enum value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_of.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_regs.h

Purpose: defines LogiCVC register offsets and bitfields used by core, CRTC, layer, interface, and IRQ code.

Important APIs/types/functions: timing registers, `LOGICVC_CTRL_*`, `LOGICVC_INT_*`, `LOGICVC_POWER_CTRL_*`, IP version masks, layer register macros, buffer select encoding, alpha/control bits, and maximum dimension constants.

Control flow: no code flow. Runtime modules use these macros to program modes, layers, interrupts, video power, and version/capability detection.

State and persistence: hardware register layout and bit semantics are encoded as compile-time constants.

Dependencies and integration points: consumed with regmap operations across the LogiCVC driver. Requires bit helper macros from included kernel environment.

Risks and test signals: `LOGICVC_LAYER_ADDRESS_REG` and `LOGICVC_LAYER_HOFFSET_REG` intentionally share offset for different IP modes; misuse can program wrong addressing path. Test register writes under both caps variants, vblank IRQ mask/stat handling, and plane enable/disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/Kconfig

Purpose: defines the Loongson DRM driver configuration symbol.

Important APIs/types/functions: `config DRM_LOONGSON` is tristate, depends on DRM/PCI and LoongArch, MIPS, or `COMPILE_TEST`, and selects DRM client selection, KMS helper, TTM, TTM helper, I2C, and bit-banged I2C.

Control flow: no runtime flow; controls whether the `loongson` module is built.

State and persistence: persisted in kernel config and affects linked objects through the Makefile.

Dependencies and integration points: mirrors source dependencies on PCI probing, DRM atomic/KMS, TTM memory management, and GPIO-emulated DDC I2C.

Risks and test signals: missing dependencies cause compile/link failures. Test LoongArch/MIPS builds, `COMPILE_TEST`, module and built-in configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/Makefile

Purpose: defines object composition for the Loongson DRM module.

Important APIs/types/functions: `loongson-y` includes benchmark, CRTC, debugfs, core PCI DRM, GEM, GFX PLL, I2C, IRQ, LS7A1000/LS7A2000 outputs, planes, pixel PLL, probe, TTM, device descriptors, and module entry. `obj-$(CONFIG_DRM_LOONGSON)` links `loongson.o`.

Control flow: build-system only.

State and persistence: determines the module's linked symbol set.

Dependencies and integration points: all files in the list cooperate through `lsdc_drv.h` and chip-specific function tables.

Risks and test signals: excluding `lsdc_ttm.o` or a chip output file would break core references. Test module link and allmodconfig builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/loongson_device.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/loongson_device.c

Purpose: provides chip descriptors and KMS function tables for LS7A1000 and LS7A2000 display controllers.

Important APIs/types/functions: `ls7a1000_kms_funcs`, `ls7a2000_kms_funcs`, `ls7a1000_gfx`, `ls7a2000_gfx`, and `lsdc_device_probe`.

Control flow: PCI probe passes a chip id; `lsdc_device_probe` indexes the descriptor table and returns the `lsdc_desc`. Core modeset init then calls descriptor-provided hooks to create I2C, outputs, planes, and CRTCs.

State and persistence: descriptors are static constants containing max clock/size, cursor capabilities, pitch alignment, vblank counter capability, config register base, PLL offsets, chip id, and model string.

Dependencies and integration points: connects generic core code to chip-specific output, cursor, CRTC, and IRQ implementations. Uses register offsets from `lsdc_regs.h`.

Risks and test signals: descriptor values directly affect mode validation and hardware setup. Test both PCI IDs, max-mode limits, cursor sizes, pitch alignment, vblank counter path, and debugfs model reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/loongson_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/loongson_module.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/loongson_module.c

Purpose: module entry/exit and module parameters for the Loongson DRM driver.

Important APIs/types/functions: `loongson_modeset` parameter, exported `loongson_vblank` parameter, `loongson_module_init`, and `loongson_module_exit`.

Control flow: init refuses to load when modeset is disabled or firmware-only video drivers are requested, otherwise registers the PCI driver. Exit unregisters the PCI driver.

State and persistence: module parameters persist for module lifetime. `loongson_vblank` controls whether probe initializes vblank IRQ support.

Dependencies and integration points: depends on PCI driver object from `lsdc_drv.c` and `video_firmware_drivers_only`.

Risks and test signals: `loongson_modeset` default `-1` means enabled unless explicitly set to zero. Test module load with `modeset=0`, firmware-only boot, and `vblank=0/1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/loongson_module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/loongson_module.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/loongson_module.h

Purpose: shares module-level Loongson symbols between module entry and core driver.

Important APIs/types/functions: declares `extern int loongson_vblank` and `extern struct pci_driver lsdc_pci_driver`.

Control flow: no executable flow.

State and persistence: `loongson_vblank` is runtime module parameter state used by PCI probe.

Dependencies and integration points: included by `loongson_module.c` and `lsdc_drv.c`.

Risks and test signals: declarations must match definitions. Test compile/link and vblank parameter behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/loongson_module.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_benchmark.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_benchmark.c

Purpose: debugfs benchmark helper for CPU copy throughput between Loongson GTT and VRAM buffer objects.

Important APIs/types/functions: copy helpers for GTT-to-VRAM, VRAM-to-GTT, GTT-to-GTT, `lsdc_benchmark_copy`, and exported `lsdc_show_benchmark_copy`.

Control flow: the debugfs entry allocates two kernel-pinned BOs in selected domains, maps both, copies a 1920x1080x4 buffer 60 times with the appropriate memcpy variant, measures jiffies elapsed, frees BOs, and prints throughput.

State and persistence: temporary pinned BOs are allocated and freed per benchmark invocation. No persistent state except debug output.

Dependencies and integration points: depends on TTM BO helpers, `lsdc_domain_to_str`, DRM printer, and debugfs caller in `lsdc_debugfs.c`.

Risks and test signals: time can be zero for very fast paths, risking divide-by-zero. Benchmark pins significant memory and should not run on low-memory systems. Test debugfs benchmark on VRAM/GTT paths and cleanup after errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_benchmark.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_benchmark.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_benchmark.h

Purpose: declares the Loongson debugfs copy benchmark entry point.

Important APIs/types/functions: `lsdc_show_benchmark_copy(struct lsdc_device *, struct drm_printer *)`.

Control flow: debugfs code calls the function to print benchmark results.

State and persistence: no state in the header.

Dependencies and integration points: includes `lsdc_drv.h` for `struct lsdc_device`.

Risks and test signals: declaration must match implementation and debugfs use. Test compile and `benchmark` debugfs file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_benchmark.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_crtc.c

Purpose: implements Loongson CRTC hardware operations, DRM CRTC funcs/helpers, pixel PLL atomic state, mode validation/programming, vblank handling, debugfs register views, and LS7A1000/LS7A2000 CRTC initialization.

Important APIs/types/functions: `ls7a1000_crtc_init`, `ls7a2000_crtc_init`, `lsdc_crtc_hw_ops`, reset/enable/disable/vblank/flip/clone/mode functions, `lsdc_pixpll_atomic_check`, `lsdc_crtc_mode_set_nofb`, and scanout-position helpers.

Control flow: reset allocates private CRTC state and writes minimal CFG reset values for S3 recovery. Atomic check computes pixel PLL parameters for enabled modes. Mode validation enforces chip max width/height, max pixel clock, and pitch alignment. Mode set updates PLL, optional DMA step, and timing registers. Atomic enable turns vblank on and enables output; disable turns vblank off, disables output, and sends pending events. Atomic flush arms or sends vblank events. Debugfs late registration exposes regs, pixclk, scan position, vblank count, and manual operations.

State and persistence: private CRTC state stores PLL parameters across atomic check to commit. Hardware CFG, timing, vblank counter, scan position, and PLL registers persist. `struct lsdc_crtc` stores chip ops, pixpll, debugfs metadata, and vblank capability.

Dependencies and integration points: depends on DRM atomic/vblank helpers, pixel PLL, register map macros, descriptor limits, planes supplied by `lsdc_plane.c`, and IRQ handlers delivering vblanks.

Risks and test signals: PLL computation failure rejects modes; pitch alignment differs by chip; LS7A1000 lacks working vblank counter. Test suspend/resume, mode switches across common clocks, page flips, vblank timestamps, debugfs manual ops, and odd-width DMA-step selection on LS7A2000.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_debugfs.c

Purpose: registers device-level debugfs diagnostics for the Loongson DRM driver.

Important APIs/types/functions: debugfs show functions for chip identity, DRM MM, GFX PLL clocks, benchmark, PCI command enabling, and `lsdc_debugfs_init`.

Control flow: `lsdc_debugfs_init` stores `ldev` in every info entry, creates files under DRM debugfs root, and delegates TTM debugfs setup. Individual show callbacks print CPU PRID/model, VMA offset manager, GFX PLL rates, benchmark results, BO list, or PCI command changes.

State and persistence: mostly read-only diagnostic state. `dc_enable` mutates PCI command bits to enable IO/MEM, so it has side effects.

Dependencies and integration points: depends on `lsdc_probe.c` CPU PRID helper, `lsdc_gfxpll`, benchmark, GEM BO reporting, TTM debugfs, PCI config access, and DRM debugfs.

Risks and test signals: debugfs callbacks can be invoked while device state changes; BO list paths use internal locking in callees. Test file creation, read stability under modesets, benchmark cleanup, and `dc_enable` on systems where firmware left PCI bits disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_drv.c

Purpose: core PCI DRM driver for Loongson display controllers. It handles DRM driver ops, PCI probe/remove/shutdown, VRAM discovery, TTM/GEM init, KMS object creation, IRQ/vblank setup, client setup, and PM suspend/resume.

Important APIs/types/functions: `lsdc_drm_driver`, `lsdc_modeset_init`, `lsdc_mode_config_init`, `lsdc_get_dedicated_vram`, `lsdc_create_device`, `lsdc_pci_probe/remove/shutdown`, `lsdc_drm_freeze`, and PM ops.

Control flow: PCI probe selects a chip descriptor, enables bus mastering and DMA mask, enables PCI device, creates DRM device, locates GPU BAR2 VRAM via sibling PCI device, removes conflicting framebuffers, initializes TTM/GEM, maps DC BAR0 registers, initializes mode config and KMS objects through descriptor hooks, resets mode config, registers VGA arbitration, starts polling, optionally initializes vblank and shared IRQ, registers DRM device, and starts clients. Suspend unpins VRAM BOs, evicts VRAM, suspends mode config, saves PCI state, disables device, and powers down; resume restores state, re-enables device, and resumes mode config.

State and persistence: `struct lsdc_device` stores PCI devices, descriptor, TTM device, MMIO base, VRAM/GTT ranges, display pipes, GEM object list, IRQ status, and pinned memory counters. Hardware state is restored through DRM helper resume and CRTC resets.

Dependencies and integration points: depends on PCI, aperture conflict removal, VGA arbitration, DRM atomic/KMS/fbdev TTM/GEM helpers, local TTM/GEM, descriptor function tables, module `loongson_vblank`, and IRQ handlers.

Risks and test signals: VRAM discovery assumes GPU at BDF 00:06.0 and DC at 00:06.1. Suspend unpins all VRAM BOs and must not race with userspace. Test both PCI IDs, missing sibling GPU, framebuffer takeover, IRQ sharing, vblank disabled mode, suspend/resume, and PRIME/dumb buffer flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_drv.h

Purpose: central Loongson DRM header defining chip descriptors, KMS function tables, DRM object wrappers, device state, conversion helpers, prototypes, and MMIO accessors.

Important APIs/types/functions: `struct lsdc_desc`, `struct loongson_gfx_desc`, `struct lsdc_crtc_hw_ops`, `struct lsdc_crtc`, primary/cursor ops and wrappers, `struct lsdc_output`, `struct lsdc_display_pipe`, `struct lsdc_kms_funcs`, `struct lsdc_crtc_state`, `struct lsdc_gem`, `struct lsdc_device`, conversion helpers, and register read/write helpers.

Control flow: no executable flow beyond inline accessors. Core code uses descriptors to dispatch chip-specific KMS construction and hardware ops.

State and persistence: `lsdc_device` is the root runtime state for PCI, DRM, TTM, MMIO, VRAM/GTT, display pipes, GEM tracking, IRQ status, and pinned memory.

Dependencies and integration points: includes PCI, DRM connector/CRTC/encoder/file/plane/TTM, and local I2C/IRQ/GFXPLL/output/pixpll/register headers. It is included across the Loongson driver.

Risks and test signals: structure layout underpins container conversions; mismatches can corrupt memory. MMIO helpers do not lock except where callers use `reglock`. Test compile coverage, KMS init for both descriptors, concurrent I2C/register access, and TTM/GEM cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_gem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_gem.c

Purpose: implements Loongson GEM object functions on top of TTM BOs, dumb buffer creation, PRIME import/export pinning, vmap/mmap, BO tracking, and debugfs BO listing.

Important APIs/types/functions: `lsdc_gem_object_funcs`, `lsdc_gem_object_create`, `lsdc_prime_import_sg_table`, `lsdc_dumb_create`, `lsdc_gem_init`, and `lsdc_show_buffer_object`.

Control flow: GEM creation calls `lsdc_bo_create`, clears new non-imported BOs, assigns object funcs, and adds the BO to the tracked list. Dumb creation computes size/pitch with descriptor alignment, rejects buffers larger than half VRAM, creates VRAM GEM, and returns a handle. PRIME import creates a GTT-domain BO using the dma-buf reservation and marks it shared. vmap pins, TTM-vmaps, reference-counts mappings, and unpins on final vunmap. mmap delegates to TTM and drops GEM ref.

State and persistence: `ldev->gem.objects` tracks driver-created BOs under mutex. Each `lsdc_bo` carries vmap count, map, sharing count, and TTM state.

Dependencies and integration points: depends on local TTM BO helpers, DRM GEM/PRIME/dumb APIs, dma-resv, and debugfs.

Risks and test signals: BO list removal must be handled by TTM code outside this file; leaks show in debugfs. Dumb error print shifts by pages while labelling MiB. Test dumb create/map, PRIME import/export, vmap/vunmap nesting, mmap, BO debugfs, and large allocation rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_gem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_gem.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_gem.h

Purpose: declares Loongson GEM creation, PRIME import, dumb-create, GEM init, and BO debugfs helpers.

Important APIs/types/functions: `lsdc_gem_object_create`, `lsdc_dumb_create`, `lsdc_gem_init`, `lsdc_show_buffer_object`, and `lsdc_prime_import_sg_table`.

Control flow: core driver plugs these into DRM driver ops and initialization; planes and debugfs consume GEM/BO state through TTM helpers.

State and persistence: header defines no state; implementation maintains GEM object list in `lsdc_device`.

Dependencies and integration points: depends on DRM GEM/file types and local device definitions.

Risks and test signals: prototype consistency is required for DRM driver callbacks. Test build and GEM ioctl behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_gem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_gfxpll.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_gfxpll.c

Purpose: maps and reports the Loongson shared GFX PLL used by DC, GMC, and GPU.

Important APIs/types/functions: bitfield/union representation of the 64-bit PLL register, `loongson_gfxpll_get_rates`, `loongson_gfxpll_print`, `loongson_gfxpll_init/fini`, and `loongson_gfxpll_create`.

Control flow: create allocates the PLL object, derives register base from chip descriptor, assigns funcs, maps MMIO, initializes reference clock, prints rates, stores the object in caller output, and registers managed cleanup. Rate reading snapshots the register, updates cached parameters, computes pre-output and per-consumer MHz values. Update is currently a TODO no-op.

State and persistence: object stores MMIO pointer, register base/size, funcs, and cached parameters. Hardware PLL settings are read but not modified by the current update function.

Dependencies and integration points: used by core device creation and debugfs clock reporting. Depends on chip descriptor config base/offsets and DRM managed cleanup.

Risks and test signals: division by zero is possible if firmware left dividers zero. No-op update means clock changes are unsupported here. Test debugfs clock output on both chips, 32-bit versus 64-bit register access, and cleanup after probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_gfxpll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_gfxpll.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_gfxpll.h

Purpose: declares Loongson shared GFX PLL parameters, operation table, object state, and creation helper.

Important APIs/types/functions: `struct loongson_gfxpll_parms`, `struct loongson_gfxpll_funcs`, `struct loongson_gfxpll`, and `loongson_gfxpll_create`.

Control flow: no executable flow; the function table abstracts init/update/rate/print operations.

State and persistence: PLL object stores DRM device, MMIO, register location, funcs, and cached divider parameters.

Dependencies and integration points: included by `lsdc_drv.h`, used by core creation and debugfs.

Risks and test signals: future chip variants may need different funcs. Test descriptor offsets and debugfs reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_gfxpll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_i2c.c

Purpose: creates bit-banged DDC I2C adapters using Loongson display-controller GPIO registers.

Important APIs/types/functions: low-level GPIO set/get helpers, I2C algo callbacks, managed destroy action, and `lsdc_create_i2c_chan`.

Control flow: channel creation allocates `lsdc_i2c`, assigns SDA/SCL masks by display pipe, points to GPIO direction/data registers, fills `i2c_algo_bit_data`, initializes adapter metadata, registers the bit-bang bus, and registers DRM-managed cleanup. Set high switches the pin to input so pull-ups raise it; set low switches to output and writes zero. Reads force input and sample data.

State and persistence: each display pipe stores `dispipe->li2c`. Adapter and GPIO state persist until DRM-managed cleanup removes the adapter and frees memory.

Dependencies and integration points: used by descriptor `create_i2c` hook before output init. Output connectors use adapter as DDC. Register access is serialized with `ldev->reglock`.

Risks and test signals: invalid index leaks the allocated object because the error path returns before freeing. GPIO register semantics are chip-specific. Test EDID reads on both pipes, probe error cleanup, lock coverage under concurrent HPD/modeset, and invalid index handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_i2c.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_i2c.h

Purpose: declares Loongson GPIO-backed I2C state and creation helper.

Important APIs/types/functions: `struct lsdc_i2c` with adapter, bit-algo data, DRM device pointer, GPIO direction/data register pointers, and SDA/SCL masks; `lsdc_create_i2c_chan`.

Control flow: core modeset init calls creation per display pipe before connector creation.

State and persistence: per-pipe I2C adapter state persists for DRM device lifetime.

Dependencies and integration points: depends on Linux I2C and i2c-algo-bit. Used by output init for DDC.

Risks and test signals: adapter lifetime must match DRM device and display pipe. Test I2C bus registration/removal and EDID probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_irq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_irq.c

Purpose: handles Loongson display-controller vblank interrupts for LS7A1000 and LS7A2000 variants.

Important APIs/types/functions: `ls7a2000_dc_irq_handler` and `ls7a1000_dc_irq_handler`.

Control flow: both handlers read `LSDC_INT_REG`, return `IRQ_NONE` if no status bits are set, save status to `ldev->irq_status`, clear interrupt status using chip-specific semantics, and call `drm_handle_vblank` for CRTC0/CRTC1 VSYNC bits. LS7A2000 clears by writing ones; LS7A1000 clears by writing zeroes for VSYNC bits.

State and persistence: `ldev->irq_status` records the last interrupt register snapshot. Hardware interrupt enable/status bits persist in `LSDC_INT_REG`.

Dependencies and integration points: registered from PCI probe when `loongson_vblank` is enabled. CRTC vblank enable/disable toggles corresponding enable bits.

Risks and test signals: wrong clear semantics can storm or lose interrupts. Warnings on shared IRQ with no status may be noisy. Test vblank counters/events on both chips, shared IRQ behavior, and page-flip completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_irq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_irq.h

Purpose: declares Loongson display-controller IRQ handlers.

Important APIs/types/functions: prototypes for `ls7a1000_dc_irq_handler` and `ls7a2000_dc_irq_handler`.

Control flow: chip descriptors reference these handlers through `lsdc_kms_funcs`.

State and persistence: no state in the header.

Dependencies and integration points: includes IRQ return types and local driver definitions.

Risks and test signals: prototype mismatch would break descriptor initialization. Test build and IRQ registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_output.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_output.h

Purpose: declares chip-specific output initialization hooks for Loongson display pipes.

Important APIs/types/functions: `ls7a1000_output_init` and `ls7a2000_output_init`.

Control flow: core modeset setup calls the descriptor's `output_init` for each pipe after I2C creation.

State and persistence: no state in header; implementations initialize `lsdc_output` encoder/connector objects embedded in display pipes.

Dependencies and integration points: includes `lsdc_drv.h` and is part of `lsdc_kms_funcs`.

Risks and test signals: prototype must match descriptor function pointer. Test output init on both chips with and without DDC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_output.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_output_7a1000.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_output_7a1000.c

Purpose: implements LS7A1000 DVO/DPI output connectors and encoders.

Important APIs/types/functions: `ls7a1000_output_init`, DPI connector mode/detect helpers, best-encoder helper, and pipe encoder reset callbacks.

Control flow: connector mode probing reads EDID over DDC when available or adds fallback no-EDID modes with 1024x768 preferred. Detect probes DDC or reports unknown without it. Encoder reset programs DVO configuration registers needed for S3 recovery. Output init creates a TMDS encoder, DPI connector with DDC, helper callbacks, attaches connector to encoder, and enables connect/disconnect polling.

State and persistence: encoder/connector live in `lsdc_display_pipe.output`. DVO configuration register state persists across modes until reset or reprogram.

Dependencies and integration points: called by LS7A1000 descriptor; uses DRM EDID/probe helpers, DDC adapter from `lsdc_i2c.c`, and DVO register macros.

Risks and test signals: external encoders are assumed transparent, so non-transparent bridge chips are unsupported. Test EDID and fallback modes, S3 resume display restoration, hotplug polling, and both DVO pipes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_output_7a1000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_output_7a2000.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_output_7a2000.c

Purpose: implements LS7A2000 HDMI/VGA-style output handling, HDMI PHY/PLL setup, AVI infoframes, HPD detection, connector mode probing, debugfs, and output initialization.

Important APIs/types/functions: `ls7a2000_output_init`, connector get_modes/detect helpers, HDMI encoder reset/enable/disable/mode_set, `ls7a2000_hdmi_phy_pll_config`, and `ls7a2000_hdmi_set_avi_infoframe`.

Control flow: output init creates per-pipe TMDS encoder and HDMI connector, attaches helper funcs, and enables polling. Encoder reset programs DVO clock/data and disables hardware I2C in favor of GPIO DDC, then releases HDMI PHY reset. Atomic mode set configures HDMI PHY PLL based on pixel clock bands and writes AVI infoframe content. Atomic enable programs zone, PHY control, and interface control; disable clears PHY/interface enable bits. Detection reads HPD bits and optionally probes DDC for pipe 0 fallback.

State and persistence: HDMI registers, PHY PLL, AVI packet registers, HPD status, and DVO config persist in hardware. Debugfs exposes HDMI register snapshots.

Dependencies and integration points: called by LS7A2000 descriptor, uses DRM EDID/HDMI helpers, DDC I2C, register access helpers, and CRTC mode state.

Risks and test signals: AVI content extraction casts unaligned bytes to `unsigned int *`; this may be risky on strict-alignment architectures. HDMI PLL wait has bounded polling but only logs failure. Test 25 MHz through 340 MHz modes, HPD and DDC fallback, both HDMI pipes, AVI infoframe correctness, and debugfs register reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_output_7a2000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_pixpll.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_pixpll.c

Purpose: implements per-pipe Loongson pixel PLL setup, parameter lookup/computation, register programming, frequency reading, and printing.

Important APIs/types/functions: static known-clock table, `lsdc_pixel_pll_setup`, `lsdc_pixpll_find`, `lsdc_pixel_pll_compute`, low-level register read/write, power/bypass/parameter ops, `lsdc_pixpll_update`, `lsdc_pixpll_get_freq`, `lsdc_pixpll_print`, and `lsdc_pixpll_init`.

Control flow: init maps the chip-specific PLL register and allocates cached parameter storage. Atomic CRTC check calls compute; it first tries the static table, then brute-forces divider combinations under PLL constraints and tolerance. Commit calls update, which bypasses/off/powers down PLL, toggles parameter update, writes dividers, powers up, waits for lock, enables output, and unbypasses.

State and persistence: `lsdc_pixpll` stores MMIO register, descriptor-derived address, funcs, and private parameter cache. Hardware PLL state persists until next modeset or reset.

Dependencies and integration points: used by `lsdc_crtc.c` for mode validation/commit and debugfs clock reporting. Register locations come from `loongson_gfx_desc`.

Risks and test signals: compute can fail modes outside tolerance; update does not return lock failure. Divider arithmetic uses integer truncation. Test common VESA/CEA modes, table hits and misses, lock polling, suspend/resume, and debugfs frequency diff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_pixpll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_pixpll.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_pixpll.h

Purpose: declares Loongson pixel PLL parameters, function table, object state, and initialization helper.

Important APIs/types/functions: `struct lsdc_pixpll_parms`, `struct lsdc_pixpll_funcs`, `struct lsdc_pixpll`, and `lsdc_pixpll_init`.

Control flow: no executable flow; CRTC code calls function table methods through initialized `lsdc_pixpll`.

State and persistence: pixel PLL object stores DRM device, register address/size, MMIO pointer, funcs, and private parameter storage.

Dependencies and integration points: included by `lsdc_drv.h`; implemented by `lsdc_pixpll.c`; consumed by CRTC private state.

Risks and test signals: future chips with different PLL layout need alternate funcs. Test both current chip descriptors and PLL cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_pixpll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_plane.c

Purpose: implements Loongson primary and cursor DRM planes, framebuffer BO pinning, primary scanout register programming, cursor update/disable paths, async cursor updates, and chip-specific cursor quirks.

Important APIs/types/functions: `lsdc_primary_plane_init`, `ls7a1000_cursor_plane_init`, `ls7a2000_cursor_plane_init`, plane prepare/cleanup helpers, primary/cursor atomic check/update/disable helpers, hardware ops tables, and register update functions.

Control flow: prepare pins framebuffer BOs into VRAM, refs them, and delegates to GEM plane helper; cleanup unpins and unrefs. Primary atomic update computes physical scanout address from BO GPU offset plus VRAM base and source offset, writes address/stride, and updates format when needed. Cursor checks enforce no scaling and 32x32 on LS7A1000 or 32/64 square on LS7A2000. Cursor updates program position, BO address, and cursor format/size; disables program cursor format disable. Async update mutates current plane state for cursor moves under DRM helper constraints.

State and persistence: plane wrappers store hardware ops and `ldev`. BO pin counts and pinned memory counters are maintained by TTM helpers. Hardware FB address, stride, format, cursor address/position/config registers persist.

Dependencies and integration points: depends on DRM atomic/GEM plane helpers, local TTM BO helpers, CRTC pipe index, and register macros.

Risks and test signals: primary address update appears to write the currently in-use FB register based on `FB_REG_IN_USING`; verify against hardware expectations for page flip. Async cursor path swaps FB references and must remain DRM-helper compliant. Test page flips, panning via src offsets, cursor move/resize/disable, LS7A1000 shared-cursor quirk, BO pin/unpin leak checks, and suspend unpin behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_probe.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_probe.c

Purpose: provides low-level CPU PRID detection helper for Loongson diagnostics and potential host-specific behavior.

Important APIs/types/functions: PRID masks/shifts/constants and `loongson_cpu_get_prid`.

Control flow: depending on architecture, inline assembly reads LoongArch `cpucfg` PRID or MIPS CP0 PRID, extracts implementation and revision bytes if output pointers are provided, and returns raw PRID.

State and persistence: no persistent state. Debugfs uses the returned values for display.

Dependencies and integration points: used by `lsdc_debugfs.c` `chips` file. Compile-time architecture guards select assembly path.

Risks and test signals: on unsupported architectures under `COMPILE_TEST`, PRID remains zero. Test LoongArch and MIPS builds/runs, plus compile-test on other architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_probe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_probe.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_probe.h

Purpose: declares the Loongson CPU PRID helper.

Important APIs/types/functions: `loongson_cpu_get_prid(u8 *impl, u8 *rev)`.

Control flow: no executable flow; debugfs calls the helper.

State and persistence: no state.

Dependencies and integration points: included by debugfs and implemented by `lsdc_probe.c`.

Risks and test signals: declaration requires `u8` type visibility from includers. Test compile on LoongArch, MIPS, and compile-test architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_probe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_regs.h

Purpose: central register and bitfield map for the Loongson display controller, pixel/GFX PLLs, CRTC timing/config, DVO, cursor, interrupts, GPIO I2C, HDMI, AVI infoframes, vblank counters, and audio PLL registers.

Important APIs/types/functions: `LSDC_PLL_REF_CLK_KHZ`, chip config bases and PLL offsets, pixel format and DMA-step enums, CRTC CFG/timing/address registers, cursor format/size/location enums, interrupt masks/enables, GPIO registers, HDMI PHY/interface/PLL bits, HPD flags, AVI packet bits, and vblank counter registers.

Control flow: no code flow. CRTC, plane, IRQ, I2C, output, and PLL modules use these definitions for MMIO accesses.

State and persistence: describes persistent hardware register state. Comments document chip-specific oddities such as mixed CRTC register offsets, one-cursor LS7A1000 behavior, and different interrupt clear semantics.

Dependencies and integration points: includes Linux bitops/types. Integrated across all `lsdc_*` modules.

Risks and test signals: incorrect offsets affect display timing, scanout addresses, cursor, HDMI, or interrupts. The `LSDC_HDMI1_AVI_CONTENT0` value overlaps `LSDC_HDMI1_PHY_CAL_REG`; verify against hardware docs. Test register dumps, HDMI modes, vblank IRQs, cursor ops, GPIO DDC, and both LS7A1000/LS7A2000 paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_regs.h -->
