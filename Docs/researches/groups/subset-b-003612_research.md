# subset-b-003612 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ring.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ring.h

### Purpose
`intel_ring.h` declares the i915 ring-buffer allocation, pinning, space accounting, reset, and request command emission helpers used by legacy ringbuffer submission and context-owned rings.

### Important APIs, Types, And Functions
The exported helpers are `intel_engine_create_ring()`, `intel_ring_begin()`, `intel_ring_update_space()`, `intel_ring_pin()`, `intel_ring_unpin()`, `intel_ring_reset()`, and `intel_ring_free()`. Inline helpers manage krefs, validate and wrap ring offsets, advance command emission, compute available space, and set `ring->tail` after asserting hardware tail constraints.

### Control Flow
Request construction reserves dwords with `intel_ring_begin()`, writes commands into `ring->vaddr + ring->emit`, then calls the inline `intel_ring_advance()` as a consistency check. Submission paths eventually call `intel_ring_set_tail()` and program `RING_TAIL`. Wrap and direction calculations keep offsets within power-of-two ring size.

### State, Persistence, And Dependencies
State lives in `struct intel_ring` from `intel_ring_types.h`: VMA, CPU mapping, head/tail/emit, space, size, wrap bit, and pin/ref counts. It depends on GEM assertions, i915 requests, cacheline constants, and the hardware rule that head/tail sharing a cacheline cannot be programmed with head greater than tail.

### Integration Points
Legacy submission, execlists context rings, request retirement, and reset code use these helpers to keep software ring state aligned with hardware registers.

### Risks
Misaligned or out-of-range offsets can hang GPUs. The tail cacheline assertion is subtle because software `ring->head` is only a conservative last-known hardware head. `intel_ring_advance()` is a debug placeholder, so callers must still reserve the right number of dwords.

### Test Signals
Useful signals include ring selftests, wraparound request emission, tail/head cacheline boundary tests, reset-to-tail behavior, and GPU hang reports around invalid `RING_TAIL` updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ring_submission.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ring_submission.c

### Purpose
`intel_ring_submission.c` implements legacy pre-execlists i915 ringbuffer submission for Gen2-Gen7 engines. It programs ring registers, status pages, context switches, PPGTT state, request preambles, reset handling, IRQ hooks, and engine setup.

### Important APIs, Types, And Functions
The public entry point is `intel_ring_submission_setup()`. Major internal paths include `xcs_resume()`, `xcs_sanitize()`, `reset_prepare()`, `reset_rewind()`, `reset_cancel()`, `i9xx_submit_request()`, `gen6_bsd_submit_request()`, `ring_context_ops`, `load_pd_dir()`, `mi_set_context()`, `switch_mm()`, `switch_context()`, `ring_request_alloc()`, engine-class setup helpers, and Gen7 render-clear workaround VMA setup.

### Control Flow
Setup installs common engine callbacks, selects render/video/copy/VEBox emitters and interrupt masks, creates one legacy timeline and one global ring, pins both under a ww context, optionally allocates a Gen7 residual-clear batch, and hands cleanup to `ring_release()`. Request allocation reserves a legacy preamble budget, emits invalidate flushes, switches address spaces, emits `MI_SET_CONTEXT` if needed, handles L3 remap state, and clears residual state when mitigations require it. Submission marks the request submitted, drains writes with `wmb()`, and writes `RING_TAIL`; Gen6 BSD wraps tail updates with wake and PSMI workarounds.

### State, Persistence, And Dependencies
Persistent driver state attaches to `engine->legacy.ring`, `engine->legacy.timeline`, `engine->status_page`, `engine->wa_ctx`, context state VMAs, and the scheduler request list. Hardware state is in ring registers, HWS PGA registers, PP_DIR registers, interrupt masks, and MI command streams. Dependencies include generation-specific command emitters, PPGTT, breadcrumbs, reset, engine PM, i915 mitigations, render-clear batches, GEM WW locking, and uncore MMIO helpers.

### Integration Points
It plugs into `intel_engine_cs` callbacks for resume, sanitize, reset, submit, request allocation, context ops, IRQ enable/disable, and release. Timelines and status pages integrate with breadcrumbs and request retirement. PPGTT and context state are shared with GEM contexts.

### Risks
This code is register-ordering sensitive. Resume/reset must disable and empty rings before reprogramming start/head/tail/ctl, and failed head reset can lead to unrecoverable hangs. Context switch command lengths must match emitted dwords. PPGTT loads require flush and invalidate barriers. Residual clear ownership in `wa_ctx.vma->private` must not leak references. The Gen6 BSD wake sequence and Gen7 workarounds are platform-specific fault points.

### Test Signals
Selftests include `selftest_ring_submission.c`. Runtime signals include suspend/resume on Gen2-Gen7, GPU reset recovery, context switch stress, PPGTT aliasing, L3 remap tests, residual-clear mitigation tests, interrupt delivery after reset, and Gen6 BSD media workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ring_submission.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ring_types.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ring_types.h

### Purpose
`intel_ring_types.h` defines the ring-buffer state object shared by i915 request emission, submission, pinning, retirement, and reset code.

### Important APIs, Types, And Functions
The central type is `struct intel_ring`. It contains a kref, backing `i915_vma`, CPU virtual address, atomic pin count, head/tail/emit offsets, cached free space, total size, wrap-direction helper bit, and effective usable size. It also defines `CACHELINE_BYTES` and `CACHELINE_DWORDS`.

### Control Flow
The type itself has no behavior, but its fields are advanced through the lifecycle: allocation creates a VMA and mapping, pinning makes it GGTT-visible, request construction advances `emit`, retirement updates `head`, submission updates `tail`, and reset rewinds software offsets.

### State, Persistence, And Dependencies
The ring is in-memory driver state backed by a GEM object/VMA that persists while referenced or pinned. `pin_count` is atomic because rings can be global engine rings or context-owned rings. It depends on Linux atomics, krefs, integer types, and `struct i915_vma`.

### Integration Points
`intel_ring.h`, ringbuffer submission, logical contexts, request retirement, and selftests consume this type. Hardware integration comes through the GGTT offset and CPU-visible command buffer.

### Risks
The structure permits lockless readers of head/tail-like fields in some paths, so updates rely on higher-level serialization and conservative invariants. `effective_size` and cacheline reservation must stay consistent with hardware ring-buffer restrictions.

### Test Signals
Tests should cover ref/pin balancing, power-of-two sizes, wrap accounting, global versus context ring use, and tail/head behavior across reset and retirement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ring_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_rps.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_rps.c

### Purpose
`intel_rps.c` implements i915 Render Power States frequency control. It initializes hardware frequency caps, enables dynamic reclocking, handles PM interrupts or timer-based busy sampling, processes wait boosting, exposes frequency setters/getters, integrates GuC SLPC delegation, and provides Gen5 IPS callbacks.

### Important APIs, Types, And Functions
Public APIs include `intel_rps_init_early()`, `intel_rps_init()`, `intel_rps_enable()`, `intel_rps_disable()`, `intel_rps_park()`, `intel_rps_unpark()`, `intel_rps_boost()`, frequency getters/setters, threshold setters, IRQ handlers, `gen6_rps_frequency_dump()`, IPS exports such as `i915_read_mch_val()`, and the display-facing `i915_display_rps_interface`. Key internal functions are `rps_timer()`, `rps_work()`, `rps_set()`, Gen5/6/8/9/VLV/CHV enable/init helpers, cap readers, conversion helpers, and interrupt mask helpers.

### Control Flow
Early init creates locks, timer, work item, and wait counters. Init reads platform caps and derives hard limits, soft limits, boost, idle, efficient frequency, thresholds, and interrupt mask must-be-zero bits. Enable chooses a platform path, programs thresholds/control registers, resets to minimum, and selects either busy-stat timer or PM interrupts. Unpark activates RPS and starts monitoring; park stops monitoring, drops frequency to idle with forcewake if needed, and biases the next resume downward. IRQs mask RPS events and queue `rps_work()`, which combines PM events, VLV C0 workaround data, and client boost waiters to choose a new clamped frequency.

### State, Persistence, And Dependencies
Persistent state is `struct intel_rps`: locks, flags, timer/work, PM event masks, current/last/soft/hard frequencies, thresholds, boost counters, EI samples, and Gen5 IPS accounting. Hardware state lives in RP control/status registers, Punit/IOSF registers, interrupt masks, and SLPC state when GuC owns control. Dependencies include runtime PM, uncore forcewake, GT PM IRQ helpers, pcode, VLV sideband, display RPS hooks, engine busy stats, workqueues, and `intel_ips`.

### Integration Points
GT power management calls enable/disable/park/unpark. Request wait paths call `intel_rps_boost()` and retirement decrements waiters. Sysfs/debugfs-style controls call min/max/boost/threshold accessors. Display code calls the exported display RPS interface. GuC SLPC paths bypass local control for many operations.

### Risks
Locking spans `rps->lock`, `rps->power.mutex`, `gt->irq_lock`, and `mchdev_lock`; ordering mistakes can deadlock or race with interrupts. Frequency units differ by platform and SLPC, so conversion bugs can silently set wrong limits. PM interrupt masks include platform bits that must remain unmasked. VLV/CHV IOSF and Gen5 IPS paths are hardware-specific. Timer busy heuristics can oscillate or underboost multi-engine workloads.

### Test Signals
Selftests include `selftest_rps.c` and `selftest_slpc.c`. Runtime tests should exercise min/max/boost sysfs controls, waitboost under blocked requests, park/unpark loops, suspend/resume sanitize, PM interrupt storms, timer-based busy stats, GuC SLPC mode, VLV/CHV sideband reads, and Gen5 IPS exported callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_rps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_rps.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_rps.h

### Purpose
`intel_rps.h` declares the RPS lifecycle, frequency-control, IRQ, boost, dump, and display-integration APIs for GT power management.

### Important APIs, Types, And Functions
It exposes initialization and registration functions, enable/disable, park/unpark, waitboost APIs, frequency conversion helpers, getters/setters for requested/actual/min/max/boost/RP0/RP1/RPn frequencies, threshold accessors, unslice raise/lower controls, throttle/MMIO helpers, IRQ handlers, and `gen6_rps_frequency_dump()`. Inline flag helpers manipulate `INTEL_RPS_ENABLED`, `ACTIVE`, `INTERRUPTS`, and `TIMER`.

### Control Flow
Callers initialize `struct intel_rps`, initialize platform caps, enable during GT power setup, transition active state on GT unpark/park, and use setters/getters from sysfs/debug and request wait paths. IRQ handlers route PM events into worker processing.

### State, Persistence, And Dependencies
The header depends on `intel_rps_types.h`, register definitions, `struct i915_request`, and `struct drm_printer`. It does not store state itself; it defines the API contract for the state in `struct intel_rps`.

### Integration Points
GT PM, request scheduling, display RPS, debugfs/sysfs, GuC SLPC, and legacy IPS module callbacks include this API.

### Risks
Many functions expect caller-side locking or active runtime PM conditions, especially setters and MMIO readers. Inline flag operations are low-level and should remain consistent with enable/park state transitions.

### Test Signals
Compile coverage across SLPC and non-SLPC configs, RPS selftests, sysfs frequency-limit tests, display boost paths, and IRQ handler tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_rps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_rps_types.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_rps_types.h

### Purpose
`intel_rps_types.h` defines the data structures behind i915 RPS and Gen5 IPS power accounting.

### Important APIs, Types, And Functions
Key types are `struct intel_ips`, `struct intel_rps_ei`, `struct intel_rps_freq_caps`, and `struct intel_rps`. `intel_rps` stores synchronization, timer/work, PM interrupt state, hardware and software frequency limits, boost and waiter counters, power-mode thresholds, and manual residency samples.

### Control Flow
The fields are initialized in early and platform init, updated by enable/park/unpark paths, modified by interrupt or timer work, and read by sysfs/debugfs/display/IPS integrations. `intel_rps_freq_caps` is populated by hardware cap readers before deriving limits.

### State, Persistence, And Dependencies
All fields are volatile kernel driver state, not disk persistence. Frequency fields are platform-encoded hardware units, not always MHz. Dependencies include atomics, mutexes, timers, ktime, and workqueues.

### Integration Points
`struct intel_gt` embeds `struct intel_rps`; GT PM, GuC SLPC, request waitboost, display RPS, debug dumps, and IPS callbacks all observe or mutate it.

### Risks
The unit distinction for frequency fields is easy to misuse. `flags` and `pm_iir` have separate lock domains from `power` fields. Gen5 IPS data is protected by an external spinlock, not the RPS mutex.

### Test Signals
Lockdep, KCSAN-style race checks, RPS selftests, and platform frequency conversion tests help validate this type’s invariants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_rps_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_sa_media.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_sa_media.c

### Purpose
`intel_sa_media.c` sets up a standalone media GT instance that shares the primary GT MMIO mapping while using its own uncore object and physical address metadata.

### Important APIs, Types, And Functions
The single public function is `intel_sa_mediagt_setup(struct intel_gt *gt, phys_addr_t phys_addr, u32 gsi_offset)`. It allocates an `intel_uncore`, seeds `gsi_offset`, reuses the primary GT IRQ lock, calls common GT and uncore early init, reuses primary uncore registers, stores `gt->uncore` and `gt->phys_addr`, and caches the media GT at `i915->media_gt`.

### Control Flow
Setup allocates managed memory through DRM managed allocation. It initializes shared lock and early GT state before attaching the uncore register mapping. It validates that the primary uncore register mapping exists and warns if a media GT is already cached.

### State, Persistence, And Dependencies
State persists in the lifetime of the DRM device through managed allocation and `i915->media_gt`. The uncore shares register memory with the primary GT but carries a separate GSI offset. Dependencies include DRM managed allocation, GT common init, uncore early init, i915 device state, and the primary GT lock.

### Integration Points
Platform discovery code for standalone media calls this before normal GT initialization. Later GT paths use `i915->media_gt` for quick lookup and use the initialized uncore for media register access.

### Risks
Sharing the primary MMIO mapping means offset handling must be correct. The code assumes current platforms have only one media GT. A missing primary mapping returns `-EIO`; allocation failure returns `-ENOMEM`.

### Test Signals
Probe tests on media-GT platforms, MMIO access using GSI offsets, interrupt lock sharing, duplicate setup warnings, and boot logs around `i915->media_gt` initialization are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_sa_media.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_sa_media.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_sa_media.h

### Purpose
`intel_sa_media.h` declares the standalone media GT setup entry point.

### Important APIs, Types, And Functions
It forward-declares `struct intel_gt` and declares `intel_sa_mediagt_setup(struct intel_gt *gt, phys_addr_t phys_addr, u32 gsi_offset)`.

### Control Flow
The header defines no runtime flow. Callers include it when platform probing needs to initialize a media GT with a physical base and GSI offset.

### State, Persistence, And Dependencies
No state is stored here. It depends on Linux integer and physical address types.

### Integration Points
The declaration connects platform/GT discovery code to `intel_sa_media.c`.

### Risks
The include guard macro name and trailing comment differ slightly, which is harmless to compilation but worth noting for consistency. API misuse mainly means passing an uninitialized `intel_gt` or incorrect GSI offset.

### Test Signals
Compile coverage and probe coverage on standalone media platforms validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_sa_media.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_sseu.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_sseu.c

### Purpose
`intel_sseu.c` discovers and reports slice/subslice/EU or Xe_HP DSS topology for i915 GTs, translates hardware fuse registers into `sseu_dev_info`, builds RPCS powergating requests, and copies topology masks to userspace.

### Important APIs, Types, And Functions
Public functions include `intel_sseu_set_info()`, `intel_sseu_subslice_total()`, `intel_sseu_get_hsw_subslices()`, `intel_sseu_copy_eumask_to_user()`, `intel_sseu_copy_ssmask_to_user()`, `intel_sseu_info_init()`, `intel_sseu_make_rpcs()`, `intel_sseu_dump()`, `intel_sseu_print_topology()`, `intel_sseu_print_ss_info()`, and `intel_slicemask_from_xehp_dssmask()`. Internal generation paths parse HSW, CHV, BDW, Gen9, Gen11, Gen12, and Xe_HP fuse layouts.

### Control Flow
`intel_sseu_info_init()` dispatches by graphics version/platform. Each generation helper reads fuse/disable registers, sets topology dimensions, fills slice/subslice/DSS masks and EU masks, computes totals, and records powergating capabilities. Copy helpers linearize masks into query-ioctl byte layouts. `intel_sseu_make_rpcs()` converts requested per-context SSEU powergating into RPCS bits, with special Gen11 subslice rules and perf exclusive-stream override.

### State, Persistence, And Dependencies
Topology persists in `gt->info.sseu` for the GT lifetime. It depends on uncore register reads, platform macros, bitmap helpers, i915 perf state, query UAPI copy routines, DRM printers, and GT register definitions.

### Integration Points
GT init calls topology discovery. Query ioctl code uses copy helpers. Context setup and render powergating use RPCS values. Debugfs and error-state dumping use print/dump helpers. Perf can pin a stable SSEU request.

### Risks
Fuse interpretation is highly generation-specific. Xe_HP collapses hardware concepts into a fake slice 0 for UAPI compatibility. RPCS field limits, Gen11 two-slice translation, and EU pair expansion can be off-by-one or platform-invalid. Userspace-visible mask layout must remain stable.

### Test Signals
Topology query tests, per-platform fuse fixtures, debugfs topology output, perf exclusive stream tests, RPCS programming validation, and regression checks on Gen9/Gen11/Xe_HP systems are high-value signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_sseu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_sseu.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_sseu.h

### Purpose
`intel_sseu.h` defines the topology data model and API for i915 slice/subslice/EU and Xe_HP DSS discovery, reporting, and powergating requests.

### Important APIs, Types, And Functions
Important definitions include maximum slice/subslice/EU constants, `intel_sseu_ss_mask_t`, `struct sseu_dev_info`, and `struct intel_sseu`. Inline helpers include `intel_sseu_from_device_info()`, `intel_sseu_has_subslice()`, and `intel_sseu_find_first_xehp_dss()`. It declares topology init, mask copy, RPCS generation, dump/print, and slice-mask conversion functions.

### Control Flow
The header has inline query/conversion logic only. Runtime flow is implemented in `intel_sseu.c`, which fills the declared structures and uses the inline helpers to abstract HSW-style masks versus Xe_HP bitmaps.

### State, Persistence, And Dependencies
`sseu_dev_info` persists in GT info and captures available hardware topology; `intel_sseu` is a per-context/engine powergating request. Dependencies include Linux bitmaps, kernel helpers, GEM warning macros, and DRM/i915 forward declarations.

### Integration Points
GT init, query UAPI, perf, context state, RPCS programming, debugfs, and topology dumps all include this header.

### Risks
The unioned HSW and Xe_HP mask representations require callers to branch on `has_xehp_dss`. `intel_sseu_from_device_info()` uses HSW fields and is not a general Xe_HP conversion. UAPI stride constants must match userspace expectations.

### Test Signals
Builds across platforms, topology query ABI tests, bitmap boundary tests up to `I915_MAX_SS_FUSE_BITS`, and RPCS generation tests validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_sseu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_sseu_debugfs.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_sseu_debugfs.c

### Purpose
`intel_sseu_debugfs.c` exposes available and currently enabled SSEU topology through GT debugfs files.

### Important APIs, Types, And Functions
Public functions are `intel_sseu_status()` and `intel_sseu_debugfs_register()`. Internal status readers are `cherryview_sseu_device_status()`, `bdw_sseu_device_status()`, `gen9_sseu_device_status()`, and `gen11_sseu_device_status()`. `i915_print_sseu_info()` formats counts and powergating fields.

### Control Flow
`intel_sseu_status()` prints static device info from `gt->info.sseu`, allocates a temporary `sseu_dev_info`, initializes its dimensions, enters runtime PM, dispatches the platform-specific ACK register reader, prints enabled status, and frees the temporary object. Debugfs show functions wrap this status and topology printing. Registration adds `sseu_status` and `sseu_topology` files.

### State, Persistence, And Dependencies
The file stores no persistent state. It depends on runtime PM, debugfs file registration, uncore register reads, SSEU topology helpers, sequence files, and platform register definitions.

### Integration Points
GT debugfs registration calls `intel_sseu_debugfs_register()`. The top-level debugfs path can call `intel_sseu_status()` directly, so the GT is passed explicitly through `seq_file` private data or function arguments.

### Risks
Status reflects live powergating ACK registers and can differ from available topology. Register layouts differ by platform, and Gen11 has a FIXME around valid subslice masks. Allocation failure returns `-ENOMEM`; pre-Gen8 returns `-ENODEV`.

### Test Signals
Debugfs reads on CHV/BDW/Gen9/Gen11+, runtime PM coverage, comparison against query topology, and output parsing for enabled versus available counts are useful tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_sseu_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_sseu_debugfs.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_sseu_debugfs.h

### Purpose
`intel_sseu_debugfs.h` declares SSEU debugfs status and registration functions.

### Important APIs, Types, And Functions
It forward-declares `struct intel_gt`, `struct dentry`, and `struct seq_file`, and declares `intel_sseu_status()` plus `intel_sseu_debugfs_register()`.

### Control Flow
There is no runtime logic in the header. GT debugfs setup includes it to register files, while top-level debugfs status code can call the status printer.

### State, Persistence, And Dependencies
The header stores no state and has minimal dependencies through forward declarations.

### Integration Points
It links GT debugfs code with the implementation in `intel_sseu_debugfs.c`.

### Risks
Callers must provide a valid live `intel_gt` and `seq_file`; runtime PM and platform support checks happen in the implementation.

### Test Signals
Compile coverage with debugfs enabled and smoke reads of `sseu_status`/`sseu_topology` validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_sseu_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_timeline.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_timeline.c

### Purpose
`intel_timeline.c` implements i915 request timelines: fence contexts, seqno allocation, hardware status page storage, active tracking, sync-map pruning, pinning, RCU lifetime, and debug dumping.

### Important APIs, Types, And Functions
Public functions include `__intel_timeline_create()`, `intel_timeline_create_from_engine()`, `intel_timeline_pin_map()`, `intel_timeline_pin()`, `intel_timeline_reset_seqno()`, `intel_timeline_enter()`, `intel_timeline_exit()`, `intel_timeline_get_seqno()`, `intel_timeline_read_hwsp()`, `intel_timeline_unpin()`, `__intel_timeline_free()`, GT timeline init/fini, and `intel_gt_show_timelines()`. Internal helpers allocate HWSP VMAs and manage `i915_active` callbacks.

### Control Flow
Creation either borrows an engine status-page VMA at a fixed offset or allocates a private page and marks that it has an initial breadcrumb. Pinning maps the HWSP, pins it high in GGTT, converts the offset to a GGTT address, and acquires active tracking. Entering a timeline adds it to the GT active list and resets HWSP seqno to guard against volatile status-page contents. Seqno allocation increments by one or two depending on initial breadcrumb use; on wrap it advances to another HWSP slot while preserving hardware semaphore constraints. Exit removes idle timelines and drops syncmap history.

### State, Persistence, And Dependencies
State persists in `struct intel_timeline`: kref, mutex, pin/active counts, HWSP map/VMA/offset, seqno, request list, last request fence, syncmap, active object, GT active-list links, and RCU head. Dependencies include GEM object allocation, GGTT pinning, i915 active fences, syncmaps, DMA fence contexts, runtime locking, and DRM printers.

### Integration Points
Contexts and engines use timelines for request ordering and breadcrumbs. Legacy ring submission creates an engine timeline from the status page. Semaphore waits use `intel_timeline_read_hwsp()`. GT debug/error paths call `intel_gt_show_timelines()`.

### Risks
Pin and active counts intentionally model different lifetimes and must stay balanced. HWSP memory may be lost over suspend/resume, so reset-on-enter is critical. RCU access to `from->timeline` and request completion races make `intel_timeline_read_hwsp()` subtle. Seqno wrap and bit-5 MI_FLUSH_DW workarounds can break semaphores if mishandled.

### Test Signals
Selftests include mock and real timeline tests. Useful runtime signals include semaphore waits, seqno wrap tests, suspend/resume, request retirement races, debug timeline dumps under load, and lockdep coverage of timeline mutex/list handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_timeline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_timeline.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_timeline.h

### Purpose
`intel_timeline.h` declares the timeline API and inline sync/ref helpers for i915 request ordering.

### Important APIs, Types, And Functions
It declares creation, get/put, pin/unpin, enter/exit, seqno allocation, HWSP read, reset, GT init/fini, and timeline dump functions. Inline helpers wrap krefs and `i915_syncmap` operations and test whether a request is last in a timeline.

### Control Flow
Callers create or acquire timelines, pin before request construction, enter while adding requests, allocate seqnos, exit when construction/activity is done, and unpin when no longer needed. Sync helpers record and compare latest waited fence seqnos by context.

### State, Persistence, And Dependencies
The header has no state itself; it exposes `struct intel_timeline` from `intel_timeline_types.h`. Dependencies include lockdep, active tracking, list utilities, syncmaps, and request/GT forward declarations.

### Integration Points
Context code, engine submission, request dependency emission, debug/error reporting, and selftests include this API.

### Risks
The API assumes callers hold the right timeline mutex around enter/exit and request-list operations. `intel_timeline_get()`/`put()` and pin/unpin lifetimes are independent and easy to confuse.

### Test Signals
Compile-time selftest declarations, lockdep, request ordering tests, syncmap dependency tests, and timeline refcount tests are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_timeline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_timeline_types.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_timeline_types.h

### Purpose
`intel_timeline_types.h` defines `struct intel_timeline`, the state container for i915 request sequencing, hardware seqno storage, synchronization history, and lifetime tracking.

### Important APIs, Types, And Functions
The structure contains fence context and seqno, a request-flow mutex, atomic pin and active counts, HWSP map/VMA/offset fields, an initial-breadcrumb flag, outstanding request list, last-request active fence, `i915_active`, retire chain pointer, syncmap pointer, GT/list links, kref, and RCU head.

### Control Flow
The fields are initialized during timeline creation, mutated during pin/enter/request emission/exit/unpin, observed by retirement and debug paths, and finally freed via RCU after kref release.

### State, Persistence, And Dependencies
State is kernel memory plus a GEM-backed HWSP VMA. It persists while referenced and may remain pinned independently of active request tracking. Dependencies include lists, krefs, mutexes, RCU, `i915_active_types`, and forward-declared i915/GT types.

### Integration Points
`intel_timeline.c`, request scheduling, breadcrumbs, semaphores, context code, and debug timeline dumping all rely on this structure.

### Risks
`pin_count` and `active_count` are deliberately separate and must not be collapsed. `last_request` is RCU guarded and does not hold a request reference. Syncmap pruning on idle is safe only when all tracked fences have completed.

### Test Signals
Timeline selftests, KASAN/KCSAN checks, lockdep around mutex/list usage, and stress of request retirement plus debug dumps validate invariants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_timeline_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_tlb.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_tlb.c

### Purpose
`intel_tlb.c` implements full GT TLB invalidation for modern i915 platforms, using GuC invalidation where available or MMIO invalidation registers otherwise.

### Important APIs, Types, And Functions
Public functions are `intel_gt_invalidate_tlb_full()`, `intel_gt_init_tlb()`, and `intel_gt_fini_tlb()`. Internal helpers are `wait_for_invalidate()`, `mmio_invalidate_full()`, and `tlb_seqno_passed()`.

### Control Flow
Callers pass a seqno barrier. The public invalidation path skips mock or wedged GTs and already-passed barriers, then runs only if the GT is awake. Under `gt->tlb.invalidate_lock`, it rechecks the seqno, asks GuC to invalidate engines if supported and ready, otherwise writes invalidate requests to awake engines through per-engine MMIO or MCR registers, waits for done bits, applies an OA invalidation workaround on affected Gen12 platforms, and advances the seqcount barrier.

### State, Persistence, And Dependencies
Persistent GT state is `gt->tlb.invalidate_lock` plus the seqcount used as an invalidation barrier. Hardware state is per-engine TLB invalidate registers and optional OA TLB invalidation control. Dependencies include GT PM, forcewake, MCR locking, uncore lock serialization with reset, GuC readiness, engine PM awake checks, and wait helpers.

### Integration Points
VM invalidation callers use `intel_gt_next_invalidate_tlb_full()` from the header to request a future full invalidation and then call this function to satisfy it. GuC, engine PM, GT reset, and OA workarounds intersect in the invalidation path.

### Risks
Skipping sleeping engines is intentional but relies on power transitions flushing state as needed. Register writes must be serialized with GT reset. MCR versus non-MCR register selection is per engine. GuC not-ready during reset is treated as safe because reset clobbers TLBs.

### Test Signals
Selftests include `selftest_tlb.c`. Useful runtime signals include page-table update stress, GuC and non-GuC modes, reset races, Gen12 OA workaround platforms, MCR platforms, and timeout logs for engines that fail to clear done bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_tlb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_tlb.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_tlb.h

### Purpose
`intel_tlb.h` declares GT TLB invalidation APIs and inline seqcount helpers.

### Important APIs, Types, And Functions
It declares `intel_gt_invalidate_tlb_full()`, `intel_gt_init_tlb()`, and `intel_gt_fini_tlb()`. Inline helpers are `intel_gt_tlb_seqno()` and `intel_gt_next_invalidate_tlb_full()`, which returns an odd seqno representing a pending full invalidation barrier.

### Control Flow
Callers read the current seqcount, request an invalidation barrier with the next odd value, and later rely on `intel_gt_invalidate_tlb_full()` to advance the seqcount so the barrier is considered passed.

### State, Persistence, And Dependencies
The header operates on `gt->tlb.seqno` from `struct intel_gt`. It depends on seqlock types and GT type definitions.

### Integration Points
VM and page-table management code include this header to coordinate TLB invalidation with GT-level state.

### Risks
The odd/even seqno convention matters: only a full invalidate should advance the barrier enough for `tlb_seqno_passed()` semantics in the implementation.

### Test Signals
TLB selftests, seqno wrap/barrier checks, and VM invalidation stress cover this API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_tlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_wopcm.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_wopcm.c

### Purpose
`intel_wopcm.c` computes and validates the WOPCM layout used by GuC and HuC firmware plus reserved hardware context space.

### Important APIs, Types, And Functions
Public functions are `intel_wopcm_init_early()` and `intel_wopcm_init()`. Internal helpers compute context reservations, validate Gen9 dword-gap and HuC-fit restrictions, verify whole layout bounds, detect locked GuC WOPCM registers, check register writability under GuC deprivilege, and map `intel_wopcm` back to `intel_gt`.

### Control Flow
Early init sets the platform default WOPCM size for GTs with microcontrollers: 2 MiB on Gen11+ and 1 MiB on earlier Gen9-era platforms. Full init reads GuC/HuC upload sizes and reserved context size. If firmware sizes are absent it returns. If registers are already locked, it trusts programmed base/size, relaxing total-size validation when i915 cannot write deprivileged registers. Otherwise it rejects unlocked media-GT cases, computes a HuC-reserving aligned GuC base, assigns remaining aligned space to GuC, validates all restrictions, and stores `wopcm->guc.base/size`.

### State, Persistence, And Dependencies
State persists in `struct intel_wopcm` embedded in GT. Hardware state is reflected in `DMA_GUC_WOPCM_OFFSET`, `GUC_WOPCM_SIZE`, and deprivilege shim registers. Dependencies include GuC/HuC firmware metadata, `intel_uc_supports_huc()`, i915 platform macros, uncore reads, and size/alignment constants.

### Integration Points
GuC/HuC firmware upload and register programming consume the computed GuC WOPCM region. Platform init must run early enough that firmware loading can abort if layout is invalid.

### Risks
Layout math is constrained by several hardware reservations and Gen9 quirks. Media-GT platforms are expected to have prelocked deprivileged registers; unlocked media GT returns without configuring WOPCM. Prelocked BIOS/IFWI values are trusted more than calculated values on deprivileged systems, deferring impossible layouts to firmware DMA failure.

### Test Signals
Boot logs for WOPCM calculations, GuC/HuC firmware load success/failure, Gen9 small firmware-layout tests, deprivileged prelocked register tests, media-GT probe paths, and boundary tests for firmware sizes and alignment validate this code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_wopcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_wopcm.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_wopcm.h

### Purpose
`intel_wopcm.h` defines the WOPCM state structure and accessors for GuC WOPCM base and size.

### Important APIs, Types, And Functions
`struct intel_wopcm` stores total WOPCM `size` and nested GuC region `base` and `size`. Inline accessors `intel_wopcm_guc_base()` and `intel_wopcm_guc_size()` return zero when GuC is not present or not in use. It declares early and full initialization functions.

### Control Flow
Callers initialize the structure early, then call full init after firmware upload sizes are known. Later GuC setup reads the accessors to program or validate WOPCM registers.

### State, Persistence, And Dependencies
The structure is GT-owned in-memory state. It depends only on Linux integer types in the header.

### Integration Points
GT microcontroller initialization, GuC firmware upload, HuC reservation checks, and WOPCM register programming include this header.

### Risks
Zero is both the default and the "not in use" accessor result, so callers must ensure initialization succeeded before relying on a nonzero GuC region. The header intentionally hides layout math in the C file.

### Test Signals
Compile coverage, GuC/HuC firmware boot tests, and assertions that accessors match programmed WOPCM registers are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_wopcm.h -->
