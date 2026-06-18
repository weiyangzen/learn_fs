# subset-b-003610 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt.c

### Purpose
`intel_gt.c` is the central lifecycle implementation for an i915 GT. It allocates and initializes root and extra GTs, wires GGTT/local-memory ownership, initializes MMIO-facing GT subsystems, brings hardware up and down, clears faults, manages scratch/kernel address-space state, registers debugfs/sysfs, and provides GT-wide helpers used by engines, GuC, RPS, MCR, and memory-management code.

### Important APIs, Types, And Functions
Important entry points include `intel_gt_common_init_early()`, `intel_root_gt_init_early()`, `intel_gt_assign_ggtt()`, `intel_gt_init_mmio()`, `intel_gt_init_hw()`, `intel_gt_init()`, `intel_gt_driver_register()`, `intel_gt_driver_remove()`, `intel_gt_driver_unregister()`, `intel_gt_driver_release()`, `intel_gt_driver_late_release_all()`, `intel_gt_probe_all()`, `intel_gt_tiles_init()`, `intel_gt_wait_for_idle()`, `intel_gt_check_and_clear_faults()`, `intel_gt_clear_error_registers()`, `intel_gt_flush_ggtt_writes()`, `intel_gt_coherent_map_type()`, and bind-context readiness helpers.

### Control Flow
Early init prepares locks, lists, reset/request/timeline/TLB state, PM wakerefs, WOPCM, GuC/HuC, and RPS. Probe creates the root GT, maps per-tile MMIO, instantiates extra tile or media GTs from platform definitions, assigns GGTTs, then discovers local memory. MMIO init records timestamp frequency, initializes UC MMIO, SSEU, MCR steering, and engines. Full init allocates the scratch VMA, initializes PM, creates a kernel VM, initializes engines and UC, resumes hardware, captures default context images, verifies workarounds, initializes late UC and migration. Removal wedges/suspends the GT, releases engines and pooled buffers, unregisters user-visible state, resets engines under runtime PM, then late release drains RCU and frees per-engine/timeline/reset/TLB resources.

### State, Persistence, And Dependencies
Persistent state lives in `struct intel_gt`: `i915`, `uncore`, `ggtt`, `uc`, `gsc`, `wopcm`, `rps`, `rc6`, `llc`, timelines, request retirement, TLB state, reset flags, `vm`, scratch VMA, buffer pool, steering tables, default steering, engine arrays, CCS slice mask, sysfs kobjects, and perf data. The file depends on GEM object/VMA allocation, GGTT/PPGTT, runtime PM, forcewake, engine setup, UC firmware, MOCS, workarounds, MCR, RPS/RC6, GSC, sysfs/debugfs, and platform definition tables.

### Integration Points
This file is called from i915 probe, tile setup, suspend/resume, runtime PM, driver unregister/remove/release, engine reset, memory-region setup, and user-visible registration. It coordinates with GuC/HuC/GSC firmware, engine initialization, renderstate capture, MOCS programming, GGTT flushing, local memory discovery, and media GT setup.

### Risks
The main risks are lifecycle ordering and generation-specific register behavior. Forcewake must cover early hardware initialization and fault clearing; scratch/VM/engine/UC allocation failures must unwind without leaving active engines; media GTs share GGTTs but have separate uncore and interrupt handling; wedging on init or fini changes later behavior; and default context capture depends on engines becoming idle and requests completing without fence errors.

### Test Signals
Useful signals include probe on single-GT, multi-tile, and standalone media platforms; local-memory setup failures; init failure at scratch, VM, engine, UC, or resume stages; suspend/resume after faults; GGTT flushing on coherent and non-coherent systems; default-state capture with request errors; driver unload while GSC work is pending; and bind-context readiness around resume/suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt.h

### Purpose
`intel_gt.h` is the public GT core interface. It exposes GT lifecycle functions, fault/error helpers, PM and flushing helpers, iterator macros, workaround predicates, UC-to-GT conversion helpers, and small inline state queries used throughout i915 GT code.

### Important APIs, Types, And Functions
The header declares the core APIs implemented in `intel_gt.c`, including init/probe/remove/register/release routines, idle wait, fault clearing, GGTT flush helpers, info printing, coherent map selection, bind-context readiness, and asynchronous wedging. It also defines `IS_GFX_GT_IP_RANGE()`, `IS_MEDIA_GT_IP_RANGE()`, stepping predicates, `GT_TRACE()`, `gt_is_root()`, `NEEDS_FASTCOLOR_BLT_WABB()`, `for_each_gt()`, `for_each_engine()`, `for_each_engine_masked()`, `intel_gt_scratch_offset()`, `intel_gt_has_unrecoverable_error()`, and `intel_gt_is_wedged()`.

### Control Flow
Callers include this header to move between device, GT, UC, GuC, HuC, GSC, and engine objects and to iterate the active GT/engine arrays. Inline wedged checks read reset flags before request submission or hardware access. IP/stepping macros gate workarounds and feature paths at compile-time-checked version boundaries.

### State, Persistence, And Dependencies
The header stores no state, but its inlines depend on `struct intel_gt`, reset flags, engine masks, scratch VMA offsets, and platform version macros. It includes engine types, GT types, and reset declarations.

### Integration Points
Nearly all GT implementation files depend on this header for object conversion and iteration. Workaround, memory, PM, reset, UC, and engine code use the IP range macros to keep platform tests consistent.

### Risks
Incorrect platform predicates can apply or skip hardware workarounds broadly. Iterator macros assume `i915->gt[]` and `gt->engine[]` entries are stable under the caller's lifecycle context. The wedged helpers assert that unrecoverable init/fini wedge bits imply the main wedged bit.

### Test Signals
Compile coverage across graphics and media GT IP predicates, multi-GT iteration, mocked GTs, and code paths using `for_each_engine_masked()` are the main signals. Runtime signals include correct workaround selection on stepping-bound platforms and safe behavior after init/fini wedging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_buffer_pool.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_buffer_pool.c

### Purpose
`intel_gt_buffer_pool.c` implements a small reusable pool of internal GEM buffers, mainly for command parser shadow copies. It caches read-only internal objects by size bucket and map type, keeps them active while requests reference them, returns idle buffers to the shrinker, and reaps stale entries.

### Important APIs, Types, And Functions
Public functions are `intel_gt_get_buffer_pool()`, `intel_gt_buffer_pool_mark_used()`, `intel_gt_init_buffer_pool()`, `intel_gt_flush_buffer_pool()`, and `intel_gt_fini_buffer_pool()`. Key internals are `bucket_for_size()`, `node_create()`, `pool_retire()`, `pool_free_older_than()`, `pool_free_work()`, and `node_free()`.

### Control Flow
Requests round the desired size to pages and scan an RCU-protected bucket for a node with sufficient size and matching map type. Claiming a node atomically changes `age` from a nonzero jiffies value to zero, removes it from the list, and acquires its `i915_active` reference. New nodes allocate internal GEM objects and mark them read-only. `mark_used()` pins pages and hides the object from the shrinker; active request tracking returns the node to the pool through `pool_retire()`, which unpins pages, makes the object purgeable, records an age, and schedules delayed reap work.

### State, Persistence, And Dependencies
State lives in `intel_gt.buffer_pool`: four size buckets, a spinlock, delayed work, and per-node active state, GEM object pointer, RCU list node, age, map type, and pinned flag. It depends on GEM internal object allocation, i915 active tracking, shrinker visibility, RCU list deletion, unordered workqueue execution, and request association from callers.

### Integration Points
Command parser and other GT clients request temporary shadow buffers and attach the node to an `i915_request` through the header helper. GT init/fini initializes and asserts the pool is empty, while driver remove flushes stale nodes.

### Risks
The pool relies on `age == 0` meaning active/claimed and nonzero meaning reusable. Race bugs in RCU claiming or list removal could double-use a buffer. Buffers must be marked active after being used, otherwise they can return to the pool too early. Delayed cleanup uses `spin_trylock_irq()`, so stale buffers can persist until a later pass.

### Test Signals
Test buffer reuse by size bucket and map type, concurrent get/put/retire paths, failure in object allocation or active acquire, request completion returning nodes, shrinker visibility toggling, flush on driver remove, and final empty-list assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_buffer_pool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_buffer_pool.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_buffer_pool.h

### Purpose
`intel_gt_buffer_pool.h` exposes the GT buffer pool API used by command parsing and other temporary-buffer users.

### Important APIs, Types, And Functions
It declares `intel_gt_get_buffer_pool()`, `intel_gt_buffer_pool_mark_used()`, init/flush/fini functions, and inline helpers `intel_gt_buffer_pool_mark_active()` and `intel_gt_buffer_pool_put()`.

### Control Flow
Callers obtain a node, pin/mark it used before writing or mapping, attach it to an `i915_request` with `mark_active()`, and release their active hold with `put()`. Retirement happens asynchronously through the active callback in the implementation.

### State, Persistence, And Dependencies
The header owns no state. It depends on `i915_active`, `i915_request`, `intel_gt_buffer_pool_types.h`, and the GEM warning helper used to verify that callers pinned before marking active.

### Integration Points
The API connects request lifetime to pooled GEM object reuse. It is part of GT initialization and teardown through the public init/flush/fini declarations.

### Risks
The inline `mark_active()` only warns if the node was not pinned; it cannot fix misuse. Callers must not drop the node without balancing the active acquisition.

### Test Signals
Compile coverage for users, runtime warnings when `mark_active()` is called without `mark_used()`, request completion returning nodes, and cleanup with no outstanding active nodes are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_buffer_pool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_buffer_pool_types.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_buffer_pool_types.h

### Purpose
`intel_gt_buffer_pool_types.h` defines the data structures backing the GT buffer pool.

### Important APIs, Types, And Functions
It defines `struct intel_gt_buffer_pool` with a spinlock, four cache lists, and delayed cleanup work, plus `struct intel_gt_buffer_pool_node` with `i915_active`, GEM object, list linkage, pool/free/RCU union, age, map type, and pinned state.

### Control Flow
The fields support the implementation's claimed versus cached transitions: `age` marks reusable nodes, `active` links GPU request lifetime to retirement, `link` places cached nodes in buckets, and the union supports active ownership, stale free chains, or RCU freeing.

### State, Persistence, And Dependencies
The types persist inside `struct intel_gt` and per cached object. Dependencies are Linux list/spinlock/workqueue primitives, GEM object types, and i915 active types.

### Integration Points
Included by `intel_gt_types.h` to embed the pool in every GT and by the public buffer-pool API.

### Risks
The union requires strict lifecycle separation: a node cannot simultaneously be in a pool, stale free chain, and RCU callback. `pinned` is represented as `u32` and must match actual GEM page pin state.

### Test Signals
Static checking, KASAN/KCSAN runs around get/retire/free, and teardown assertions that all cache lists are empty provide the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_buffer_pool_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_ccs_mode.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_ccs_mode.c

### Purpose
`intel_gt_ccs_mode.c` computes the DG2 fixed CCS load-balancing mode value from the GT's available CCS slices.

### Important APIs, Types, And Functions
The exported function is `intel_gt_apply_ccs_mode()`. It uses `CCS_MASK(gt)`, `gt->ccs.cslices`, `I915_MAX_CCS`, `XEHP_CCS_MODE_CSLICE()`, and `XEHP_CCS_MODE_CSLICE_MASK`.

### Control Flow
Non-DG2 platforms return zero. DG2 picks the first available CCS engine, then iterates compute slices. Enabled slices are mapped to that first CCS engine; unavailable slices are marked with the reserved/unavailable mask.

### State, Persistence, And Dependencies
The function reads GT platform data and the `ccs.cslices` mask but writes no persistent state. The returned mode is consumed by register programming elsewhere. Dependencies are platform macros and GT register definitions.

### Integration Points
Engine and workaround setup paths use the computed value when programming `XEHP_CCS_MODE`/related CCS mode state on DG2.

### Risks
The function assumes `CCS_MASK(gt)` is nonzero on DG2 before `__ffs()` is used. Incorrect `cslices` discovery can route work to unavailable CCS slices or over-constrain load balancing.

### Test Signals
Test DG2 configurations with one, multiple, and sparse CCS slices; non-DG2 zero behavior; and register programming that consumes the returned mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_ccs_mode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_ccs_mode.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_ccs_mode.h

### Purpose
`intel_gt_ccs_mode.h` declares the CCS mode helper for compute-slice load-balancing register setup.

### Important APIs, Types, And Functions
It forward-declares `struct intel_gt` and declares `intel_gt_apply_ccs_mode()`.

### Control Flow
Consumers include the header when they need to compute a register value from `struct intel_gt` CCS topology.

### State, Persistence, And Dependencies
The header stores no state and only depends on a GT forward declaration.

### Integration Points
Used by platform/workaround or engine setup code that programs DG2 CCS mode registers.

### Risks
The narrow API hides platform assumptions in the implementation; callers must only use the returned value with the matching hardware register semantics.

### Test Signals
Compile coverage and DG2 CCS register programming validation are sufficient.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_ccs_mode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_clock_utils.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_clock_utils.c

### Purpose
`intel_gt_clock_utils.c` determines the GT timestamp clock frequency for each generation and converts between GT clock/PM intervals and nanoseconds.

### Important APIs, Types, And Functions
Public functions are `intel_gt_init_clock_frequency()`, debug-only `intel_gt_check_clock_frequency()`, `intel_gt_clock_interval_to_ns()`, `intel_gt_pm_interval_to_ns()`, `intel_gt_ns_to_clock_interval()`, and `intel_gt_ns_to_pm_interval()`. Internal readers cover Gen11+, Gen9, Gen6, Gen5, G4x, and Gen4.

### Control Flow
Initialization reads platform registers such as `CTC_MODE`, `TIMESTAMP_OVERRIDE`, and `RPM_CONFIG0` or uses documented fixed frequencies. It stores `gt->clock_frequency` and `gt->clock_period_ns`, with a special Icelake CTX timestamp period. Conversion helpers use integer multiply/divide and Gen6 PM interval conversion rounds to a multiple of 25 to avoid known RPS issues.

### State, Persistence, And Dependencies
State is persisted in `gt->clock_frequency` and `gt->clock_period_ns`. Dependencies include uncore MMIO reads, platform version checks, `i915_freq` helpers, GT register definitions, and integer math helpers.

### Integration Points
GT MMIO init calls this before subsystems that need timestamp scaling. RPS/PM code, debugfs, request timing, and GuC busyness paths use the conversion helpers.

### Risks
Clock registers are assumed stable after initialization. Wrong source selection or crystal-clock decoding skews timeouts, PM thresholds, busyness accounting, and debug output. Zero frequency on unsupported generations must not be used by conversion callers.

### Test Signals
Test frequency decoding on Gen4 through Gen12+, timestamp override paths, debug check warnings when firmware changes clocking, conversion round-trip behavior, and Gen6 PM rounding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_clock_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_clock_utils.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_clock_utils.h

### Purpose
`intel_gt_clock_utils.h` exposes GT clock initialization, optional debug validation, and clock/PM interval conversion helpers.

### Important APIs, Types, And Functions
It declares `intel_gt_init_clock_frequency()`, `intel_gt_check_clock_frequency()`, `intel_gt_clock_interval_to_ns()`, `intel_gt_pm_interval_to_ns()`, `intel_gt_ns_to_clock_interval()`, and `intel_gt_ns_to_pm_interval()`.

### Control Flow
The debug check compiles to a no-op unless `CONFIG_DRM_I915_DEBUG_GEM` is enabled. Other callers use the conversion helpers after GT MMIO initialization has populated clock fields.

### State, Persistence, And Dependencies
The header stores no state and depends only on integer types plus a `struct intel_gt` forward declaration.

### Integration Points
Included by GT initialization, PM, RPS, debugfs, and code that converts hardware timestamp units.

### Risks
Callers must not use conversion helpers before initialization or when `clock_frequency` is zero.

### Test Signals
Build coverage with debug enabled/disabled and runtime checks on platforms with different timestamp sources are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_clock_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_debugfs.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_debugfs.c

### Purpose
`intel_gt_debugfs.c` creates the per-GT debugfs root and registers core GT debug controls, including reset injection/status and MCR steering reports.

### Important APIs, Types, And Functions
Public functions are `intel_gt_debugfs_register()`, `intel_gt_debugfs_register_files()`, `intel_gt_debugfs_reset_show()`, and `intel_gt_debugfs_reset_store()`. Internal files include `reset` and `steering`.

### Control Flow
Registration creates `gtN` under the DRM debugfs root, installs core files, then delegates to engine, PM, SSEU, and UC debugfs registration. The reset read maps terminal wedge status to 0/1, and reset write waits for reset backoff to clear before calling `intel_gt_handle_error()` with the user-provided engine mask. The steering file prints MCR steering state through a `drm_printer`.

### State, Persistence, And Dependencies
The file persists debugfs dentries through debugfs infrastructure and reads GT reset/MCR state. Dependencies include debugfs, DRM printers, reset handling, MCR reporting, and submodule debugfs registration.

### Integration Points
Called from `intel_gt_driver_register()`. It is the parent registration point for GT engine, PM, SSEU, and UC diagnostics.

### Risks
Reset writes are a privileged debug interface and can disrupt active work. Registration silently skips when debugfs is absent. File registration relies on optional `eval()` callbacks to avoid exposing invalid files.

### Test Signals
Debugfs presence, per-GT directory creation on multi-GT systems, manual reset triggering, steering output on MCR platforms, and conditional file visibility are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_debugfs.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_debugfs.h

### Purpose
`intel_gt_debugfs.h` provides helper macros and registration types for per-GT debugfs files.

### Important APIs, Types, And Functions
It defines `DEFINE_INTEL_GT_DEBUGFS_ATTRIBUTE()`, `DEFINE_INTEL_GT_DEBUGFS_ATTRIBUTE_WITH_SIZE()`, `struct intel_gt_debugfs_file`, and declarations for GT debugfs registration and reset show/store helpers.

### Control Flow
The macros generate `single_open` file operations that pass `inode->i_private` to a show callback. Registration code consumes arrays of `intel_gt_debugfs_file` entries and optional evaluation callbacks.

### State, Persistence, And Dependencies
The header stores no state. It depends on Linux file operations and forward-declared GT structures.

### Integration Points
GT, engine, PM, SSEU, and UC debugfs modules use these helpers to keep per-GT file creation consistent.

### Risks
Generated file operations are read-only unless a custom fops table supplies writes. Callback data must remain valid for the debugfs file lifetime.

### Test Signals
Compile coverage of generated fops and runtime file open/read behavior for each registered GT debugfs module are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_defines.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_defines.h

### Purpose
`intel_gt_defines.h` centralizes simple GT-wide constants.

### Important APIs, Types, And Functions
It defines `I915_MAX_GT` as `2`, setting the array bound for GT instances in this tree.

### Control Flow
There is no runtime control flow. The constant constrains iteration and storage in code that supports a root GT plus one extra tile/media GT.

### State, Persistence, And Dependencies
The header stores no state and has no dependencies beyond include guards.

### Integration Points
Used by GT arrays, `for_each_gt()`, and platform code that enumerates extra GT definitions.

### Risks
If future platforms expose more GTs than this constant allows, probe and iteration would silently lack capacity until the constant and associated arrays are updated.

### Test Signals
Compile-time array sizing and multi-GT probe tests on platforms with root plus media/tile GTs validate the current bound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_defines.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_engines_debugfs.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_engines_debugfs.c

### Purpose
`intel_gt_engines_debugfs.c` exposes a per-GT debugfs `engines` file that dumps state for each initialized engine.

### Important APIs, Types, And Functions
The public registration function is `intel_gt_engines_debugfs_register()`. Internally, `engines_show()` iterates `for_each_engine()` and calls `intel_engine_dump()`.

### Control Flow
Registration adds the `engines` file under a GT debugfs root. Opening the file creates a seq_file; reading it prints every engine's debug dump with the engine name as a label.

### State, Persistence, And Dependencies
The file owns no persistent state. It reads `gt->engine[]` and engine-private state through `intel_engine_dump()`. Dependencies include DRM printers, GT debugfs helpers, engine dump support, and seq_file.

### Integration Points
Registered from GT debugfs setup and used by developers/support tooling to inspect engine state during hangs or scheduling problems.

### Risks
Dump content can race with active engine state and must rely on engine dump routines for locking/consistency. The file exposes only initialized engines.

### Test Signals
Reading debugfs on systems with different engine classes, during idle and active workloads, and after engine reset provides useful coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_engines_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_engines_debugfs.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_engines_debugfs.h

### Purpose
`intel_gt_engines_debugfs.h` declares per-GT engine debugfs registration.

### Important APIs, Types, And Functions
It forward-declares `struct intel_gt` and `struct dentry`, and declares `intel_gt_engines_debugfs_register()`.

### Control Flow
GT debugfs code includes this header and delegates engine file creation to the implementation.

### State, Persistence, And Dependencies
The header stores no state.

### Integration Points
Connects core GT debugfs registration with engine-specific diagnostics.

### Risks
No direct runtime risk beyond registration ordering.

### Test Signals
Build coverage and presence of the `engines` debugfs file under each `gtN` directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_engines_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_irq.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_irq.c

### Purpose
`intel_gt_irq.c` implements GT interrupt dispatch, reset, and postinstall programming for Gen5/6, Gen8, and Gen11+ interrupt layouts, including engine interrupts, PM/RPS interrupts, GuC/GSC/PXP events, media GT routing, and parity errors.

### Important APIs, Types, And Functions
Public functions include `gen11_gt_irq_handler()`, `gen11_gt_irq_reset()`, `gen11_gt_irq_postinstall()`, `gen11_gt_reset_one_iir()`, `gen8_gt_irq_handler()`, `gen8_gt_irq_reset()`, `gen8_gt_irq_postinstall()`, `gen6_gt_irq_handler()`, `gen5_gt_irq_handler()`, `gen5_gt_irq_reset()`, `gen5_gt_irq_postinstall()`, `gen5_gt_enable_irq()`, and `gen5_gt_disable_irq()`. Important internals include `guc_irq_handler()`, `gen11_gt_engine_identity()`, `gen11_gt_identity_handler()`, `pick_gt()`, `gen11_other_irq_handler()`, and parity error handling.

### Control Flow
Gen11+ handlers lock `gt->irq_lock`, scan interrupt banks from the master control value, select an identity register for each set bit, decode engine class/instance/interrupt bits, route media/video/GSC cases to the appropriate GT, and call engine or subsystem handlers before clearing the bank bit. Reset functions disable and mask engine, GuC, GSC, PM, and CCS interrupt registers. Postinstall enables class interrupts and unmasks only supported engine lanes and firmware events. Older generations read generation-specific IIR registers and dispatch to fixed engine class slots.

### State, Persistence, And Dependencies
The file updates `gt->gt_imr`, `gt->pm_ier`, and `gt->pm_imr`, and reads engine class maps, UC interrupt enable state, media GT pointers, and platform feature bits. Dependencies include raw uncore MMIO, i915 IRQ helpers, engine IRQ callbacks, RPS handlers, GuC host events, GSC proxy, PXP, GMD interrupt register definitions, and GT register definitions.

### Integration Points
Top-level display/device IRQ handlers call these generation-specific GT handlers. Engine breadcrumb signaling, GuC submission, RPS frequency control, PXP, GSC firmware, and media GT all receive events through this layer.

### Risks
Interrupt ordering is strict: Gen11 shared/selector identity must be serviced before clearing `GT_INTR_DW`, and `gen11_gt_reset_one_iir()` must unlock a stuck bit by servicing identity first. Media GT routing can misdeliver GSC/video events if engine topology checks are wrong. Masks must match enabled engines to avoid lost interrupts or storms.

### Test Signals
Signals include engine breadcrumb completion on each class/instance, GuC and media GuC events, GSC/HECI2 interrupts, RPS interrupts, parity errors, IRQ reset/postinstall across generations, interrupt storm recovery via `gen11_gt_reset_one_iir()`, and multi-GT media routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_irq.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_irq.h

### Purpose
`intel_gt_irq.h` declares GT interrupt handlers and setup helpers and provides small engine IRQ callback helpers.

### Important APIs, Types, And Functions
It declares Gen5/6/8/11 handler, reset, and postinstall functions; `gen11_gt_reset_one_iir()`; `GEN8_GT_IRQS`; `intel_engine_cs_irq()`; and `intel_engine_set_irq_handler()`.

### Control Flow
Top-level IRQ code chooses the generation-specific handler. Engine setup installs an IRQ handler with `smp_store_mb()` so live interrupts see a coherent callback pointer.

### State, Persistence, And Dependencies
The header stores no state but manipulates `engine->irq_handler` through the inline setter. It depends on engine types and integer types.

### Integration Points
Used by i915 IRQ setup, engine initialization, PM IRQ code, and generation-specific interrupt paths.

### Risks
The callback update barrier is required because interrupts can become live during engine allocation/setup. Callers must not pass NULL engines to `intel_engine_cs_irq()` when `iir` is nonzero.

### Test Signals
Compile coverage, live interrupt delivery after handler updates, and generation-specific postinstall/reset tests are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_mcr.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_mcr.c

### Purpose
`intel_gt_mcr.c` implements support for multicast/replicated GT registers. It initializes platform steering tables, chooses non-terminated read targets, serializes steering register access, supports unicast and multicast reads/writes/RMWs, reports steering state, and provides an MCR-aware wait helper.

### Important APIs, Types, And Functions
Public APIs are `intel_gt_mcr_init()`, `intel_gt_mcr_lock()`, `intel_gt_mcr_unlock()`, `intel_gt_mcr_lock_sanitize()`, `intel_gt_mcr_read()`, `intel_gt_mcr_read_any()`, `intel_gt_mcr_read_any_fw()`, `intel_gt_mcr_unicast_write()`, `intel_gt_mcr_multicast_write()`, `intel_gt_mcr_multicast_write_fw()`, `intel_gt_mcr_multicast_rmw()`, `intel_gt_mcr_get_nonterminated_steering()`, `intel_gt_mcr_report_steering()`, `intel_gt_mcr_get_ss_steering()`, and `intel_gt_mcr_wait_for_reg()`.

### Control Flow
Initialization sets `gt->mcr_lock`, derives mslice and L3 bank masks from fuse/SSEU registers, and assigns steering tables for media OADDRM, Xe_LPG, DG2, ICL, and related platforms. Reads that need steering choose a valid group/instance based on register range and fuse state; explicit reads/writes program the MCR selector under lock and forcewake. On MTL+, a hardware steering semaphore is acquired in addition to the software spinlock and restored on unlock. Multicast writes force multicast mode before writing all instances.

### State, Persistence, And Dependencies
Persistent state includes `gt->steering_table[]`, `gt->info.l3bank_mask`, `gt->info.mslice_mask`, `gt->default_steering`, and `gt->mcr_lock`. Dependencies include uncore forcewake/MMIO, platform fuses, SSEU topology, GT register definitions, wait helpers, DRM printers, and generation/stepping macros.

### Integration Points
Workaround programming, fault handling, register dumps, OA/perf, debugfs steering reports, and any code touching MCR registers must use this API rather than raw uncore accesses. GT resume sanitizes the hardware semaphore through this module.

### Risks
Steering to a fused or powered-down instance returns zero or drops writes. Lock order matters: `mcr_lock` must precede `uncore->lock`. MTL hardware semaphore timeouts taint CI because firmware/hardware may be holding the lock. Register range tables must remain accurate as platforms add MCR classes.

### Test Signals
Use platforms with L3BANK, MSLICE, LNCF, DSS, INSTANCE0, OADDRM, and media GT steering; verify read-any values are nonzero when expected; stress concurrent MCR access; test MTL semaphore sanitize/resume; validate debugfs steering tables; and exercise timeout paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_mcr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_mcr.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_mcr.h

### Purpose
`intel_gt_mcr.h` exposes the MCR steering API and iteration helper for code that reads or writes multicast/replicated GT registers.

### Important APIs, Types, And Functions
It declares MCR init, lock/unlock/sanitize, explicit and read-any accessors, unicast/multicast writes, multicast RMW, steering lookup/report helpers, MCR wait helper, `_HAS_SS()`, and `for_each_ss_steering()`.

### Control Flow
Consumers use the API to avoid terminated reads/writes. The subslice steering iterator maps logical DSS/subslice IDs to group/instance pairs and skips fused-off units through SSEU topology checks.

### State, Persistence, And Dependencies
The header owns no state but depends on `struct intel_gt`, MCR register types, SSEU helpers, and graphics IP version macros.

### Integration Points
Included by workaround, register access, debugfs, and GT fault code that needs safe MCR access.

### Risks
Callers of `_fw` variants must already hold forcewake and `mcr_lock`. Incorrect use of raw MMIO for MCR registers bypasses the protections defined here.

### Test Signals
Compile and runtime coverage of `for_each_ss_steering()`, explicit MCR access, and `_fw` variants under lockdep are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_mcr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_pm.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_pm.c

### Purpose
`intel_gt_pm.c` manages GT runtime power state, suspend/resume sequencing, park/unpark behavior, user forcewake preservation, engine sanitization, and awake-time accounting.

### Important APIs, Types, And Functions
Public functions include `intel_gt_pm_init_early()`, `intel_gt_pm_init()`, `intel_gt_pm_fini()`, `intel_gt_resume_early()`, `intel_gt_resume()`, `intel_gt_suspend_prepare()`, `intel_gt_suspend_late()`, `intel_gt_runtime_suspend()`, `intel_gt_runtime_resume()`, and `intel_gt_get_awake_time()`. Key internals are `__gt_unpark()`, `__gt_park()`, `gt_sanitize()`, `wait_for_suspend()`, `user_forcewake()`, `runtime_begin()`, and `runtime_end()`.

### Control Flow
Early init creates the GT wakeref and stats seqcount. On unpark, the GT holds a display `POWER_DOMAIN_GT_IRQ`, unparks RC6/RPS, notifies PMU/GuC busyness, starts request retirement, and begins awake accounting. On park, it ends accounting, parks requests/busyness/VMA/PMU/RPS/RC6, synchronizes IRQs, and asynchronously drops the display power reference. Resume sanitizes MCR locks, uncore, faults, engines, UC, RPS, and RC6, initializes hardware, restarts engines, enables RC6/RPS/LLC, resumes UC, and restores user forcewake counts. Suspend marks bind context unready, drains requests, optionally disables power-management features for non-s2idle, and sanitizes hardware.

### State, Persistence, And Dependencies
State includes `gt->wakeref`, `gt->awake`, `gt->stats`, `gt->user_wakeref`, bind-context readiness, reset flags, RC6/RPS/LLC/UC state, and engine serials. Dependencies include runtime PM, display power domains, forcewake, IRQ synchronization, engine reset/resume hooks, request retirement, GuC busyness, PXP PM, MCR, and suspend target state.

### Integration Points
Engine submission paths hold GT wakerefs; suspend/resume and runtime PM call this file; debugfs forcewake users adjust `user_wakeref`; PMU and GuC busyness depend on park/unpark notifications.

### Risks
Suspend must not race active requests or user forcewake refs. Park/unpark ordering affects interrupt latency and display DC state behavior. Resume failure wedges the GT. Awake-time seqcount updates disable local IRQs and rely on the wakeref mutex as the associated lock.

### Test Signals
Runtime PM idle/wake cycles, system suspend/resume including s2idle and deeper sleep, forcewake debugfs open across suspend, wedged GT resume, engine resume failure, request drain timeout, and awake-time accounting are high-value signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_pm.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_pm.h

### Purpose
`intel_gt_pm.h` exposes GT wakeref helpers and PM lifecycle declarations.

### Important APIs, Types, And Functions
It defines inline helpers `intel_gt_pm_is_awake()`, get/put tracked and untracked wakeref routines, `intel_gt_pm_get_if_awake()`, async put helpers, `with_intel_gt_pm`, `with_intel_gt_pm_if_awake`, `intel_gt_pm_wait_for_idle()`, `is_mock_gt()`, and declarations for init/fini/suspend/resume/runtime PM and awake-time retrieval.

### Control Flow
Callers acquire GT wakerefs before hardware access or submission and release them synchronously or asynchronously. Conditional helpers run code only if the GT is already awake. Lifecycle functions are called by probe, driver teardown, runtime PM, and system PM.

### State, Persistence, And Dependencies
The header manipulates `gt->wakeref` and, for mock detection, `gt->awake`. It depends on `intel_wakeref` and GT types.

### Integration Points
Used throughout i915 GT, engine, debugfs, sysfs, and runtime PM code to keep GT hardware powered while accessing registers or submitting work.

### Risks
Unbalanced wakeref get/put calls keep the GT awake or allow premature suspend. Tracked handles must be passed back to the matching put helper.

### Test Signals
Wakeref debug tracking, runtime PM autosuspend, lockdep, and tests that exercise get-if-awake and async put paths validate this header's contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_pm_debugfs.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_pm_debugfs.c

### Purpose
`intel_gt_pm_debugfs.c` registers per-GT debugfs files for forcewake, RC/DRPC state, frequency information, LLC/eDRAM data, RPS boost state, and performance limit reasons.

### Important APIs, Types, And Functions
Public functions are `intel_gt_pm_debugfs_register()`, `intel_gt_pm_frequency_dump()`, `intel_gt_pm_debugfs_forcewake_user_open()`, and `intel_gt_pm_debugfs_forcewake_user_release()`. Debugfs show paths include `fw_domains_show()`, `drpc_show()` with ILK/VLV/Gen6/MTL variants, `frequency_show()`, `llc_show()`, `rps_boost_show()`, and perf-limit get/clear callbacks.

### Control Flow
Opening `forcewake_user` increments `user_wakeref`, gets a GT PM ref, and takes user forcewake on Gen6+. Release reverses the operation. DRPC show obtains runtime PM and chooses platform-specific register dumps. Frequency and LLC dumps read RPS, pcode, IOSF, or legacy frequency registers. RPS boost prints software and hardware autotuning state. Perf limit reasons read or clear the log bits of the GT perf-limit register.

### State, Persistence, And Dependencies
State read includes uncore forcewake counters, RC6 residency, RPS frequencies/thresholds, power-gate status, pcode frequency tables, `gt->awake`, perf-limit log/status bits, and `gt->user_wakeref`. Dependencies include debugfs, seq_file, runtime PM, uncore, pcode, IOSF sideband, RPS/RC6/LLC helpers, and GT register definitions.

### Integration Points
Registered under each GT debugfs root by core GT debugfs. Upper-level non-GT debugfs code can call the forcewake helpers. The files are support and CI diagnostics for PM and frequency behavior.

### Risks
Debugfs reads touch live power-management registers and must hold runtime PM/forcewake where needed. `forcewake_user` can intentionally pin the GT awake. Some frequency data is platform-specific and may be unavailable or hidden when GuC SLPC replaces legacy RPS.

### Test Signals
Reading all PM debugfs files across ILK, VLV/CHV, Gen6+, Gen11+, MTL, SLPC and non-SLPC systems; holding/releasing forcewake_user across suspend; clearing perf limit log bits; and checking conditional file visibility are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_pm_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_pm_debugfs.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_pm_debugfs.h

### Purpose
`intel_gt_pm_debugfs.h` declares the GT PM debugfs registration and helper interfaces.

### Important APIs, Types, And Functions
It declares `intel_gt_pm_debugfs_register()`, `intel_gt_pm_frequency_dump()`, and forcewake-user open/release helpers.

### Control Flow
Core GT debugfs calls the registration function. Other debugfs layers may use the forcewake helpers to share the same user-forcewake accounting.

### State, Persistence, And Dependencies
The header stores no state. It depends on forward declarations for GT, dentry, and DRM printer.

### Integration Points
Connects PM diagnostics with core GT debugfs and any upper-level debugfs files that need forcewake behavior.

### Risks
Callers must pair forcewake open/release helpers or leak a GT PM/forcewake reference.

### Test Signals
Compile coverage and forcewake reference balance during debugfs open/release validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_pm_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_pm_irq.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_pm_irq.c

### Purpose
`intel_gt_pm_irq.c` manages GT PM/RPS interrupt enable and mask state for Gen6+ interrupt layouts.

### Important APIs, Types, And Functions
It implements `gen6_gt_pm_unmask_irq()`, `gen6_gt_pm_mask_irq()`, `gen6_gt_pm_enable_irq()`, `gen6_gt_pm_disable_irq()`, and `gen6_gt_pm_reset_iir()`. Internal helpers are `write_pm_imr()`, `write_pm_ier()`, and `gen6_gt_pm_update_irq()`.

### Control Flow
Callers hold `gt->irq_lock`, then enable/disable or mask/unmask PM bits in `gt->pm_ier` and `gt->pm_imr`. Register selection depends on generation: Gen11 uses upper-half WGBOXPERF registers, Gen8 uses `GEN8_GT_*R(2)`, and older Gen6 uses `GEN6_PM*`. Reset writes the IIR twice and posting-reads it.

### State, Persistence, And Dependencies
Persistent state is `gt->pm_ier` and `gt->pm_imr`. Dependencies include GT interrupt locking, uncore MMIO writes, platform version checks, and GT PM register definitions.

### Integration Points
RPS and GT IRQ setup use this file to enable or suppress PM events without disturbing engine interrupts.

### Risks
All functions require `gt->irq_lock`; missing it risks races with IRQ handlers or postinstall/reset. Gen11 bit shifting must match hardware upper-half placement.

### Test Signals
RPS interrupt enable/disable, PM IIR reset behavior, lockdep coverage, and register programming checks on Gen6, Gen8, and Gen11+ platforms are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_pm_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_pm_irq.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_pm_irq.h

### Purpose
`intel_gt_pm_irq.h` declares GT PM interrupt mask, enable, disable, and reset helpers.

### Important APIs, Types, And Functions
It declares `gen6_gt_pm_unmask_irq()`, `gen6_gt_pm_mask_irq()`, `gen6_gt_pm_enable_irq()`, `gen6_gt_pm_disable_irq()`, and `gen6_gt_pm_reset_iir()`.

### Control Flow
RPS/PM code includes this header to update PM IRQ state while holding the GT IRQ lock.

### State, Persistence, And Dependencies
The header stores no state and only forward-declares `struct intel_gt`.

### Integration Points
Used by RPS and interrupt setup paths to control PM interrupt delivery.

### Risks
The API name is Gen6-prefixed but covers later generations via implementation-specific register selection; callers must still respect lock requirements.

### Test Signals
Build coverage and PM IRQ behavior on Gen6+ platforms validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_pm_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_print.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_print.h

### Purpose
`intel_gt_print.h` provides GT-scoped logging and warning macros that prefix messages with the GT id.

### Important APIs, Types, And Functions
It defines `gt_err()`, `gt_warn()`, `gt_warn_once()`, `gt_notice()`, `gt_info()`, `gt_dbg()`, rate-limited error/notice helpers, `gt_probe_error()`, `gt_WARN()`, `gt_WARN_ONCE()`, `gt_WARN_ON()`, and `gt_WARN_ON_ONCE()`.

### Control Flow
Macros expand to DRM or device logging helpers using `(_gt)->i915->drm` and `(_gt)->info.id`. Warning macros feed the GT id into DRM warning output.

### State, Persistence, And Dependencies
No state is stored. Dependencies are DRM print helpers, GT types, and i915 utility macros.

### Integration Points
Used throughout GT code for diagnostics in probe, PM, MCR, faults, and error paths.

### Risks
Macros evaluate `_gt` for message context; callers must pass a valid GT pointer. Logging level and rate limiting affect support visibility.

### Test Signals
Compile coverage and dmesg/debug output that includes the expected `GT%u` prefix validate the macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_print.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_regs.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_regs.h

### Purpose
`intel_gt_regs.h` is the GT register definition catalog. It defines MMIO and MCR register offsets and bitfields for GT clocks, MCR steering, context state, workaround registers, performance counters, fault reporting, PAT/MOCS, CCS mode, PM/RPS/RC6, forcewake, interrupt registers, media offsets, and many generation-specific chicken/debug registers.

### Important APIs, Types, And Functions
The file is macro-only. Important groups include `MTL_MIRROR_TARGET_WP1`, `RPM_CONFIG0`, MCR selector/semaphore fields, context-size registers, ring fault and TLB fault registers, PAT and MOCS macros, XeHP/Xe_LPG MCR registers, RPS/RC6 registers, `XEHP_CCS_MODE`, forcewake ack/control registers, Gen11+ interrupt enable/mask/identity registers, and `MTL_MEDIA_GSI_BASE`.

### Control Flow
There is no direct control flow. Other GT files use these macros to select registers and bit masks for platform-specific read/write/RMW operations. Some macros compute offsets from engine class, PAT/MOCS index, stream index, or CCS slice.

### State, Persistence, And Dependencies
The header stores no runtime state. It depends on `i915_reg_defs.h` and its `_MMIO`, `MCR_REG`, `REG_BIT`, `REG_GENMASK`, and field-prep helpers.

### Integration Points
This header feeds almost every GT subsystem: initialization, workarounds, MCR, PM, IRQ, RPS/RC6, renderstate/context setup, debugfs/sysfs, fault clearing, and media GT support.

### Risks
Incorrect offsets or masks can corrupt hardware state, break interrupts, misdecode faults, or apply workarounds to the wrong register. MCR registers must be accessed through MCR helpers even though they are defined next to normal MMIO registers. Generation comments and duplicate legacy fields require careful use.

### Test Signals
Hardware bring-up on supported generations, register read/write selftests, workaround verification, interrupt delivery, RPS/RC6 sysfs/debugfs output, MCR steering tests, and fault decode validation are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_requests.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_requests.c

### Purpose
`intel_gt_requests.c` handles request retirement, engine retirement work, periodic GT retirement while awake, submission flushing for idle waits, and request watchdog cancellation.

### Important APIs, Types, And Functions
Public functions are `intel_engine_init_retire()`, `intel_engine_add_retire()`, `intel_engine_fini_retire()`, `intel_gt_retire_requests_timeout()`, `intel_gt_init_requests()`, `intel_gt_park_requests()`, `intel_gt_unpark_requests()`, `intel_gt_fini_requests()`, and `intel_gt_watchdog_work()`. Internals include `retire_requests()`, `flush_submission()`, `engine_retire()`, `add_retire()`, and `retire_work_handler()`.

### Control Flow
Idle timelines are queued to an engine retirement work item using a tagged lockless list in `tl->retire`. Engine retire work tries to lock each timeline and retire completed requests. GT retirement scans `gt->timelines.active_list`, optionally waits on the last request fence with a timeout, retires requests under the timeline mutex, releases inactive timelines after dropping the list spinlock, and flushes submission/idle-barrier work before and after scanning. GT unpark schedules periodic retirement; park cancels it.

### State, Persistence, And Dependencies
State includes active timeline lists, timeline request lists, `tl->last_request`, `tl->retire`, engine retire work, engine wakeref work, GT delayed retire work, watchdog llist, and request references. Dependencies include dma fences, workqueues, timeline locking/refcounts, engine submission flushes, PM awake state, and request cancel/retire primitives.

### Integration Points
GT PM uses park/unpark and idle waits; engine code queues idle timelines; request completion and watchdog paths use this file to retire or cancel hung work; driver late release drains retirement and watchdog work.

### Risks
Retirement is best-effort when timeline mutexes are busy. List iteration temporarily drops `timelines->lock`, so reference pinning and list reset are critical. Timeout semantics feed suspend/idle decisions. Watchdog cancellation must put request references exactly once.

### Test Signals
Tests should cover idle timeline retirement, busy timeline retry, timeout waits, signal interruption through callers, park/unpark periodic work, virtual engine exclusion in `intel_engine_add_retire()`, watchdog expiry cancellation, and teardown with pending retirement work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_requests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_requests.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_requests.h

### Purpose
`intel_gt_requests.h` declares GT and engine request-retirement helpers.

### Important APIs, Types, And Functions
It declares `intel_gt_retire_requests_timeout()`, inline `intel_gt_retire_requests()`, engine retire init/add/fini helpers, and GT request init/park/unpark/fini helpers.

### Control Flow
Callers can request immediate best-effort retirement with timeout zero or wait for fences with a positive timeout. PM and engine code use the lifecycle helpers around GT park/unpark and engine setup.

### State, Persistence, And Dependencies
The header stores no state. It forward-declares GT, engine, and timeline structures.

### Integration Points
Used by PM, engine setup/teardown, request submission, and driver release paths.

### Risks
The inline no-timeout retirement does not wait for outstanding work, so callers that require quiescence must use the timeout API or higher-level idle waits.

### Test Signals
Build coverage and runtime request retirement behavior under active and idle workloads validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_requests.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_sysfs.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_sysfs.c

### Purpose
`intel_gt_sysfs.c` creates per-GT sysfs kobjects and bridges legacy parent-device GT PM attributes with newer `gt/gtN` objects.

### Important APIs, Types, And Functions
Public functions are `is_object_gt()`, `intel_gt_sysfs_get_drvdata()`, `intel_gt_sysfs_register()`, and `intel_gt_sysfs_unregister()`. It also defines the `id` attribute and `kobj_gt_type`.

### Control Flow
Registration first creates legacy PM sysfs files on the parent device for root GT only, then initializes `gt->sysfs_gt` under `i915->sysfs_gt` as `gtN`, creates a `.defaults` child kobject, and initializes PM sysfs under the per-GT object. Unregister releases `.defaults` and the GT kobject. `intel_gt_sysfs_get_drvdata()` detects whether the caller is a `gtN` object or the parent device and returns the appropriate GT.

### State, Persistence, And Dependencies
State lives in `gt->sysfs_gt` and `gt->sysfs_defaults`. Dependencies include Linux kobjects/sysfs, DRM device objects, i915 sysfs helpers, GT PM sysfs, and GT id state.

### Integration Points
Called from GT driver registration/unregistration. PM sysfs code uses its object detection and drvdata helper to serve both ABI locations.

### Risks
Kobject lifetimes must be balanced even on partial registration failure. Name-based `is_object_gt()` assumes GT sysfs object names begin with `gt`. Legacy parent attributes intentionally aggregate root/all-GT behavior, so callers must use the helper rather than assuming private data type.

### Test Signals
Sysfs layout checks for `/gt/gt0`, optional `/gt/gt1`, `.defaults`, legacy parent power files, correct `id`, and clean unregister are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_sysfs.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_sysfs.h

### Purpose
`intel_gt_sysfs.h` exposes helpers for GT sysfs object detection, kobject-to-GT conversion, registration, and private-data lookup.

### Important APIs, Types, And Functions
It declares `is_object_gt()`, `intel_gt_sysfs_register()`, `intel_gt_sysfs_unregister()`, `intel_gt_sysfs_get_drvdata()`, and inline `kobj_to_gt()`. It also declares `kobj_to_i915()`.

### Control Flow
PM sysfs show/store functions use `intel_gt_sysfs_get_drvdata()` to support both per-GT kobjects and legacy parent-device attributes.

### State, Persistence, And Dependencies
The header stores no state but assumes `struct intel_gt` contains `sysfs_gt`. It depends on kobject types, ctype, GEM bug checks, and GT types.

### Integration Points
Used by GT sysfs core and PM sysfs implementation.

### Risks
`kobj_to_gt()` is only valid for kobjects embedded in `struct intel_gt`; callers must use object detection when handling legacy parent-device attributes.

### Test Signals
Compile coverage and sysfs reads/writes from both legacy and per-GT paths validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_sysfs_pm.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_sysfs_pm.c

### Purpose
`intel_gt_sysfs_pm.c` implements sysfs power-management and frequency attributes for GTs, including RC6 residency, RPS frequencies and thresholds, SLPC controls, throttle reason status, media frequency factor, media RP0/RPn frequencies, and default values.

### Important APIs, Types, And Functions
The public entry point is `intel_gt_sysfs_pm_init()`. Important helpers include generic read/write dispatchers for parent versus per-GT objects, RC6 residency readers, RPS frequency show/store functions, SLPC `ignore_eff_freq` and power-profile handlers, throttle reason bool attributes, media frequency factor show/store, media RP0/RPn pcode readers, RPS threshold show/store functions, and default attribute readers.

### Control Flow
Initialization creates RC6 groups when PM and RC6 are supported, creates Gen6+ RPS frequency files, optional VLV efficient-frequency files, optional RPS thresholds when GuC SLPC is not used, and per-GT-only files for punit frequency, SLPC controls, throttle reasons, media ratio mode, and `.defaults`. Legacy parent attributes aggregate across GTs: frequency reads return the maximum across GTs, RC6 reads return the minimum, and writes apply to every GT. Per-GT attributes operate on the specific `gtN`.

### State, Persistence, And Dependencies
State read/written includes `gt->rc6.enabled`, RC6 residency counters, RPS requested/actual/min/max/boost frequencies, RPS up/down thresholds, `gt->defaults`, GuC SLPC power profile and media ratio mode, performance limit reason registers, pcode fused media frequencies, and runtime PM-protected MMIO state. Dependencies include sysfs, kobjects, i915 sysfs compatibility, RPS/RC6, GuC SLPC, pcode, GT registers, runtime PM, and throttle reason masks.

### Integration Points
Called by `intel_gt_sysfs_register()` for both legacy and per-GT locations. Userspace power management tools and tests consume these ABI files. It bridges old `gt_*` device attributes and new `rps_*` per-GT attributes.

### Risks
ABI compatibility drives non-obvious aggregate semantics. Store operations through legacy parent files update all GTs and can partially fail. Input parsing must reject invalid SLPC profile strings and unsupported media ratio factors. Runtime PM must cover MMIO reads. Conditional creation must match hardware capabilities to avoid dead sysfs files.

### Test Signals
Sysfs ABI tests should cover root and media GT layouts, legacy parent aggregation, min/max frequency writes, boost frequency, RPS thresholds with and without SLPC, RC6 residency, throttle reason files, media frequency factor scaling, media RP0/RPn reads, invalid stores, and `.defaults` contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_sysfs_pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_sysfs_pm.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_sysfs_pm.h

### Purpose
`intel_gt_sysfs_pm.h` declares GT PM sysfs initialization.

### Important APIs, Types, And Functions
It declares `intel_gt_sysfs_pm_init(struct intel_gt *gt, struct kobject *kobj)`.

### Control Flow
GT sysfs registration calls this function once for the legacy parent object on root GT and once for each per-GT kobject.

### State, Persistence, And Dependencies
The header stores no state. It includes kobject and GT type declarations.

### Integration Points
Connects core GT sysfs object creation with PM/RPS/RC6/SLPC attribute registration.

### Risks
No direct runtime risk, but callers must pass the correct kobject type because the implementation changes behavior for legacy versus `gtN` objects.

### Test Signals
Build coverage and expected sysfs files under both legacy and per-GT paths validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_sysfs_pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_types.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_types.h

### Purpose
`intel_gt_types.h` defines the central `struct intel_gt` object and related GT-wide enums/types. It is the persistent state model for a graphics, tile, or media GT in the i915 driver.

### Important APIs, Types, And Functions
Major definitions include `struct intel_mmio_range`, `enum intel_steering_type`, `enum intel_submission_method`, `struct gt_defaults`, `enum intel_gt_type`, `struct intel_gt`, `struct intel_gt_definition`, `enum intel_gt_scratch_field`, and `intel_gt_support_legacy_fencing()`.

### Control Flow
The type layout supports initialization flow from early allocation through MMIO setup, engine/UC/PM init, runtime operation, sysfs/debugfs registration, suspend/resume, reset, and final release. Engine arrays provide lookup by global id and by class/instance; nested structs group TLB, timeline, request, watchdog, PM stats, CCS, info, MOCS, and sysfs state.

### State, Persistence, And Dependencies
`struct intel_gt` persists device ownership pointers, uncore and GGTT pointers, UC/GSC/WOPCM, TLB invalidation batching, workaround lists, active timelines, request retirement, watchdog work, wakerefs, closed VMAs, reset state, awake stats, clock frequency, LLC/RC6/RPS, interrupt masks, engines, submission method, CCS slices, kernel VM, buffer pool, scratch VMA, migration context, MCR steering, physical MMIO base, topology/info/hwconfig, MOCS indexes, sysfs kobjects, wedge work, perf data, and GGTT list linkage.

### Integration Points
Included by most GT modules and embedded indirectly in the top-level i915 device's GT array. It connects engine, UC, PM, reset, memory, interrupt, sysfs, debugfs, perf, and MCR subsystems through shared state.

### Risks
Because it is the central shared state object, lifecycle and locking rules around each field are critical. `irq_lock` is a pointer to support per-GT allocation, MCR lock order is documented, stats use seqcount under wakeref mutex, and union-like subsystem ownership requires init/fini symmetry. Adding fields without clear ownership can create teardown races.

### Test Signals
Multi-GT probe, suspend/resume, runtime PM, engine init/fini, MCR steering, sysfs/debugfs registration, request retirement, and wedge/reset selftests all validate that the shared state model remains coherent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_types.h -->
