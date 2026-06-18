# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt.c

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
