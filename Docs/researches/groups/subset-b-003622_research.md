# Research: subset-b-003622

Grouped source research for subset B work item `subset-b-003622`. Each delimited section preserves the source path and can be split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_driver.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_driver.c

## Purpose
`i915_driver.c` is the main DRM PCI driver entry point for Intel i915. It owns device construction, probe and teardown ordering, DRM registration, open/postclose hooks, system/runtime power-management callbacks, the DRM ioctl table, the display parent interface used by the split display code, and the top-level `drm_driver` registration contract.

## Important APIs, Types, and Functions
Core exported functions are `i915_driver_probe()`, `i915_driver_remove()`, `i915_driver_shutdown()`, `i915_driver_suspend_switcheroo()`, `i915_driver_resume_switcheroo()`, `i915_driver_parent_interface()`, and `i915_print_iommu_status()`. Important private phases are `i915_driver_early_probe()`, `i915_driver_mmio_probe()`, `i915_driver_hw_probe()`, `i915_driver_register()`, and their mirrored cleanup helpers. The file defines `i915_pm_ops`, `i915_driver_fops`, `i915_ioctls[]`, and `i915_drm_driver`. It also supplies the `intel_display_parent_interface parent`, wiring display-side callbacks to i915 BO, DPT, DSB, HDCP, IRQ, overlay, PC8, pcode, RPM, RPS, stolen-memory, VMA, and frontbuffer interfaces.

## Control Flow
Probe first enables PCI, allocates `struct drm_i915_private`, copies module parameters, attaches display device data, and initializes software-only state: runtime device info, stepping, sideband locks, runtime PM, workqueues, TTM, root GT, GEM early state, IRQ scaffolding, display early probe, clock-gating hooks, and pre-production warnings. MMIO probe then locates the GMCH bridge, maps uncore MMIO for each GT, enables MCHBAR when needed, initializes runtime device/display info, initializes GT MMIO, and sanitizes inherited GPU state. Hardware probe validates vGPU capabilities, detects eDRAM, programs DMA masks, initializes perf, probes/enables GGTT, removes conflicting apertures, probes GT tiles and memory regions, enables bus mastering/MSI, sets up opregion, initializes pcode, detects DRAM, and initializes bandwidth data.

After GVT, display noirq/nogem probe, IRQ install, GEM init, PXP init, full display probe, and `drm_dev_register()`, the driver exposes debugfs, sysfs, perf, GT registration, hwmon, display registration, power domains, runtime PM, and switcheroo. Remove and release reverse the phases: unregister userspace-visible surfaces, synchronize RCU, suspend GEM, remove GVT/display/IRQs, clear error state, remove GEM, release hw resources, release GGTT and memory regions, drop MMIO, and late-release software state. Suspend, hibernate, switcheroo, shutdown, and runtime PM paths orchestrate display access, client suspend, IRQs, HPD, encoders, DPT/GGTT, DMC, PXP, GT/uncore, opregion notifications, and runtime wakeref assertions in a strict order.

## State and Persistence Behavior
Persistent device state is stored in `drm_i915_private`: parameters, runtime info, capabilities, GT array, display pointer, workqueues, runtime PM, GEM memory manager, GPU error state, PXP, PMU, hwmon, GVT, GMCH/MCHBAR state, and `do_release`. Probe copies global module parameters into per-device parameters. `i915_pm_ops` keeps suspend/resume state through `suspend_count`, runtime PM wakerefs, saved display/GGTT state, opregion state, and GT/uncore runtime state. `i915_driver_release()` is gated by `do_release` so early probe failures do not run full teardown on a partially exposed device.

## Dependencies and Integration Points
The file integrates Linux PCI, DRM core, DRM KMS helpers, fbdev helper ops, runtime PM, VGA switcheroo, aperture conflict removal, DMA APIs, debugfs/sysfs, PMU, hwmon, GVT, PXP, GuC/GT, GEM, GGTT, display driver phases, opregion/ACPI, pcode, DMC, HPD, power domains, and i915 UAPI ioctls. Its `drm_ioctl_desc` table is the central dispatch surface for legacy no-op ioctls, GEM memory ioctls, execbuffer, query, perf, contexts, VMs, reset stats, and register reads.

## Risks
Ordering is the main risk. Runtime PM must not be enabled before all callbacks can tolerate it, interrupts must be resumed before GEM/display hardware initialization that submits work, GGTT must be enabled before DPT/GEM resume, and userspace must not be exposed before all ioctl-visible subsystems are ready. Probe failure unwind is complex and asymmetric in places, with comments noting FIXME cleanup paths. DMA mask quirks for gen2 and 965 must be preserved before GGTT probing. Runtime suspend intentionally drops PCI/root-port D3cold state for some platforms; incorrect handling can freeze machines or lose display hotplug. The ioctl table exposes many long-lived UAPI contracts; handler replacement or flag changes can break userspace.

## Test Signals
Useful signals include successful probe/remove on integrated and dGPU platforms, failure-injection through `ALLOW_ERROR_INJECTION` paths, suspend/resume/S0ix/S3/S4/runtime PM cycles with no wakeref leaks, switcheroo suspend/resume, successful KMS modeset and GEM submission after resume, debugfs/sysfs/perf/hwmon registration, correct `/proc` fdinfo, successful aperture conflict removal, MSI behavior on pre-gen5 versus newer platforms, and i915 UAPI ioctl coverage from IGT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_driver.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_driver.h

## Purpose
This header is the small public-internal interface for the i915 top-level driver module. It names the driver, exposes power-management operations, declares PCI probe/remove/shutdown entry points, switcheroo suspend/resume helpers, display parent-interface access, and IOMMU status printing.

## Important APIs, Types, and Functions
It defines `DRIVER_NAME` as `"i915"` and `DRIVER_DESC` as `"Intel Graphics"`. Exports are `i915_pm_ops`, `i915_driver_probe()`, `i915_driver_remove()`, `i915_driver_shutdown()`, `i915_driver_resume_switcheroo()`, `i915_driver_suspend_switcheroo()`, `i915_driver_parent_interface()`, and `i915_print_iommu_status()`. Forward declarations keep dependencies light for PCI, DRM private state, DRM printers, and display parent interfaces.

## Control Flow
There is no implementation control flow. The declarations are consumed by PCI driver registration code, switcheroo code, display code, and diagnostic paths. Calls flow from Linux PCI/PM entry points into `i915_driver.c`, while display code calls `i915_driver_parent_interface()` to acquire parent callbacks.

## State and Persistence Behavior
The header stores no state. It defines ABI-like internal linkage for the singleton `i915_pm_ops` and for functions operating on persistent `struct drm_i915_private` instances.

## Dependencies and Integration Points
The header depends only on `linux/pm.h` for `pm_message_t` and forward declarations. It is the integration point between i915 core, PCI binding, runtime/system PM, VGA switcheroo, display parent code, and debug printing.

## Risks
Because this header is widely included, adding heavy includes can increase rebuild scope or create dependency cycles. The function declarations must stay aligned with `i915_driver.c`; changing names or signatures breaks PCI, PM, and display integration. `DRIVER_NAME` is user-visible in DRM registration and logs.

## Test Signals
Build coverage is the primary signal. Runtime signals are successful PCI probe/remove, PM callback registration, switcheroo operation, display parent interface retrieval, and IOMMU status appearing in debug device info dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_drm_client.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_drm_client.c

## Purpose
`i915_drm_client.c` tracks per-DRM-file client accounting for fdinfo and internal object attribution. It allocates `i915_drm_client` objects, manages references, reports memory and engine runtime statistics, and associates internal context objects with a client when `/proc` support is enabled.

## Important APIs, Types, and Functions
Public functions are `i915_drm_client_alloc()`, `__i915_drm_client_free()`, `i915_drm_client_fdinfo()`, `i915_drm_client_add_object()`, `i915_drm_client_remove_object()`, and `i915_drm_client_add_context_objects()`. Internal helpers include `obj_meminfo()`, `show_meminfo()`, `busy_add()`, and `show_client_class()`. `uabi_class_names[]` maps render, copy, video, video-enhance, and compute engine classes to fdinfo keys.

## Control Flow
Open paths allocate a client with initialized kref, context list lock, and optional object list lock. fdinfo first accounts public GEM handles from `file->object_idr`, then internal objects from the client's RCU-protected `objects_list`, and prints DRM memory stats by memory region. For gen8+ it then sums closed-context runtime from `client->past_runtime[class]` with live context runtime gathered under RCU from each context's engines, printing per-engine-class time and capacity. Object add/remove updates `obj->client` and the RCU list under `objects_lock`. Context object attribution adds context state objects and non-legacy ring backing objects.

## State and Persistence Behavior
Client state persists for the lifetime of a DRM file and may outlive object list removal under RCU. `past_runtime[]` accumulates runtime from closed contexts. `ctx_list` links live contexts to the client. Under `CONFIG_PROC_FS`, `objects_list` tracks driver-internal objects attributed to a client in addition to public handles. Object client references are kref-managed and released after RCU deletion.

## Dependencies and Integration Points
This file integrates with DRM fdinfo (`drm_show_fdinfo`), GEM object IDRs, GEM object memory regions, dma-resv activity tests, i915 GEM contexts and engines, `intel_context_get_total_runtime_ns()`, memory region UABI names, and `/proc` conditional compilation. It is called from `i915_gem_open()`, context lifecycle code, object lifecycle code, and `i915_driver.c` through `.show_fdinfo`.

## Risks
Accounting must tolerate concurrent object/context teardown. The object list uses RCU plus object ref acquisition; missing refs can cause use-after-free. Runtime totals can race with engine/context changes but are intended as stats, not synchronization. `I915_LAST_UABI_ENGINE_CLASS` must cover all indexed classes or fdinfo arrays can be undersized. Memory stats distinguish shared/private via GEM helpers and may underreport internal objects when `/proc` is disabled.

## Test Signals
Check `/proc/<pid>/fdinfo/<drm-fd>` for `drm-memory-*`, `drm-engine-*`, and capacity fields; verify public and internal object accounting across create/close; run workloads on each engine class and observe runtime growth; close contexts and verify runtime migrates into `past_runtime`; use KCSAN/lockdep/RCU debug to exercise concurrent object removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_drm_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_drm_client.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_drm_client.h

## Purpose
This header defines the per-file i915 DRM client accounting object and its reference/accounting API. It is the contract between file-private setup, GEM context lifecycle, internal GEM object attribution, and fdinfo reporting.

## Important APIs, Types, and Functions
`struct i915_drm_client` contains a `kref`, `ctx_lock`, `ctx_list`, optional `objects_lock` and `objects_list`, and `atomic64_t past_runtime[]` indexed through `I915_LAST_UABI_ENGINE_CLASS`. Inline helpers are `i915_drm_client_get()` and `i915_drm_client_put()`. Declared functions allocate/free clients, print fdinfo, and add/remove internal objects or context objects, with no-op inline stubs when `CONFIG_PROC_FS` is disabled.

## Control Flow
There is no executable flow beyond the inlines. Client users take references when linking objects, drop them when unlinking, and use `i915_drm_client_fdinfo()` from DRM fdinfo callbacks. Conditional stubs let non-proc builds compile without object attribution work.

## State and Persistence Behavior
The structure persists per DRM file and owns lists of live contexts and optionally client-attributed objects. Closed context runtime is retained in `past_runtime[]` after live context objects disappear.

## Dependencies and Integration Points
The header includes UAPI engine class definitions, GEM object types, Intel context types, and file-private declarations. It integrates `i915_file_private.h`, GEM context/object code, and DRM printers.

## Risks
Array sizing depends on `I915_LAST_UABI_ENGINE_CLASS` matching the highest class used by UAPI. The context and object lists require their documented locks/RCU rules. Adding fields here affects every open DRM file and should be weighed for memory footprint.

## Test Signals
Build with and without `CONFIG_PROC_FS`, fdinfo output under active workloads, object attribution for context state/rings, client cleanup after file close, and lockdep coverage for `ctx_lock` and `objects_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_drm_client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_drv.h

## Purpose
`i915_drv.h` is the central private i915 device header. It defines `struct drm_i915_private`, key driver-wide state containers, platform and feature predicates, and conversion helpers used across GEM, GT, display, PM, perf, error capture, virtualization, and memory-management code.

## Important APIs, Types, and Functions
Major types include `struct i915_dsm`, `struct intel_l3_parity`, `struct i915_gem_mm`, `struct i915_virtual_gpu`, `struct i915_selftest_stash`, and `struct drm_i915_private`. Helper inlines convert `drm_device`, `device`, and `pci_dev` to i915 private state and return the root GT. Macros expose device/runtime info (`INTEL_INFO`, `RUNTIME_INFO`, `DRIVER_CAPS`, `INTEL_DEVID`, `GRAPHICS_VER`, `MEDIA_VER`, stepping accessors), platform checks (`IS_PLATFORM`, `IS_SUBPLATFORM`, specific platform/subplatform macros), and feature checks (`HAS_LLC`, `HAS_EDRAM`, `HAS_EXECLISTS`, `HAS_PPGTT`, `HAS_LMEM`, `HAS_GT_UC`, `HAS_RUNTIME_PM`, `HAS_PXP`, and many others).

## Control Flow
There is no runtime algorithm beyond inline predicates. The macros are used throughout i915 to select platform workarounds, register programming paths, memory behavior, UAPI answers, power features, PPGTT support, GuC/PXP capabilities, and display/GT quirks. `IS_PLATFORM()` and `IS_SUBPLATFORM()` compute bit positions inside runtime platform masks and assert that platform constants are compile-time constants.

## State and Persistence Behavior
`drm_i915_private` persists for the DRM device lifetime. It owns the embedded `drm_device`, display pointer, release flag, parameters, static and runtime device info, stolen memory data, uncore, virtual GPU state, GVT pointer, GMCH bridge/MCHBAR state, user engine containers, IRQ state, sideband locks, ordered and unordered workqueues, GEM memory manager, L3 parity state, eDRAM size, GPU error state, suspend count, runtime PM, perf, hwmon, GT array, media GT quick lookup, GEM context/mmap singleton state, frontbuffer lock, PXP, overlay, PMU, TTM device, and optional selftest stash.

## Dependencies and Integration Points
The header pulls together UAPI, TTM, GEM context/shrinker/stolen types, GT and GuC types, error capture, params, perf, scheduler, runtime PM, uncore, memory regions, and device info. Almost every i915 subsystem depends on this header for feature predicates and root device state.

## Risks
This header is a dependency hub, so additions can create include cycles or widespread rebuild cost. Platform predicates are correctness-critical; a wrong feature macro can select unsafe register sequences or expose unsupported UAPI. `struct drm_i915_private` layout embeds `drm_device` first and display immediately after it, and `i915_driver.c` asserts the display member placement. State fields have subsystem-specific locking rules that are not all enforced locally.

## Test Signals
Build coverage across many config combinations is essential. Runtime signals include correct platform/subplatform names, feature macro behavior in `i915_welcome_messages`, successful probe on old and new platforms, selftests for GEM/GT paths using predicates, suspend/resume behavior, and no sparse/lockdep warnings from state access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_dsb_buffer.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_dsb_buffer.c

## Purpose
`i915_dsb_buffer.c` implements the i915 backing-buffer interface used by display DSB command submission. It allocates a GEM object, pins it in the GGTT, maps it write-combined, exposes read/write/fill/flush helpers, and exports those hooks through `intel_display_dsb_interface`.

## Important APIs, Types, and Functions
The local `struct intel_dsb_buffer` stores `cmd_buf`, pinned `vma`, and `buf_size`. Interface methods are `intel_dsb_buffer_ggtt_offset()`, `intel_dsb_buffer_write()`, `intel_dsb_buffer_read()`, `intel_dsb_buffer_fill()`, `intel_dsb_buffer_create()`, `intel_dsb_buffer_cleanup()`, and `intel_dsb_buffer_flush_map()`. The exported object is `i915_display_dsb_interface`.

## Control Flow
Create allocates the wrapper, creates contiguous LMEM if `HAS_LMEM()` or an internal shmem GEM object otherwise, sets shmem cache coherency to uncached for system memory, pins the object globally in the GGTT via `i915_gem_object_ggtt_pin()`, maps it with `I915_MAP_WC`, and stores state. Cleanup calls `i915_vma_unpin_and_release()` with map release and frees the wrapper. Fill bounds-checks the byte range against `buf_size` and then writes through the CPU mapping.

## State and Persistence Behavior
The buffer persists while display code owns the returned `intel_dsb_buffer`. Its GEM object remains pinned in GGTT and mapped WC. The GGTT offset is stable until cleanup. Writes are CPU-visible in the mapping and `flush_map` pushes GEM map writes as needed.

## Dependencies and Integration Points
This file integrates display DSB code with i915 GEM internal/shmem/LMEM allocation, GGTT pinning, VMA lifetime management, cache coherency, and display parent interfaces. It is reached through `i915_driver.c`'s display parent interface.

## Risks
Allocation and pinning failures must release the GEM object and wrapper exactly once. DSB command memory must be contiguous in LMEM where required. Fill takes a byte size but an index in dwords; incorrect callers can still trigger WARN-only bounds issues. Forgetting `flush_map` before hardware consumption can leave stale command contents.

## Test Signals
Display DSB paths should allocate buffers, program commands, flush maps, and complete modeset/plane update flows. Exercise both LMEM and system-memory platforms, error injection in object creation/pinning/mapping, and warnings for fill bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_dsb_buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_dsb_buffer.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_dsb_buffer.h

## Purpose
This header exposes the i915 implementation of the display DSB buffer interface to display parent-interface wiring.

## Important APIs, Types, and Functions
It declares `extern const struct intel_display_dsb_interface i915_display_dsb_interface`.

## Control Flow
There is no control flow. Display code receives this interface through `i915_driver_parent_interface()` and calls the function pointers implemented in `i915_dsb_buffer.c`.

## State and Persistence Behavior
The header stores no state. The exported interface object is static storage in the implementation file.

## Dependencies and Integration Points
The header intentionally avoids including the display interface definition and relies on external declarations. It integrates i915 GEM-backed DSB buffers with split display code.

## Risks
Signature drift in `intel_display_dsb_interface` will surface at build time in `i915_dsb_buffer.c`. The header is minimal; adding includes can expand dependencies.

## Test Signals
Build i915 display code and run display DSB modeset/update paths that consume the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_dsb_buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_edram.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_edram.c

## Purpose
`i915_edram.c` detects platform eDRAM and records its size in `drm_i915_private`. That value drives feature predicates such as `HAS_EDRAM()` and write-through cache behavior.

## Important APIs, Types, and Functions
The public function is `i915_edram_detect()`. The helper `gen9_edram_size_mb()` decodes `HSW_EDRAM_CAP` bank, way, and set fields into megabytes using fixed tables.

## Control Flow
Detection returns early for platforms before Haswell/Broadwell/gen9+. It reads `HSW_EDRAM_CAP` with forcewake-safe uncore access, ignores disabled eDRAM, assigns a fixed 128 MB size for pre-gen9 capability formats, or calculates gen9+ size from register fields. It then logs the detected amount.

## State and Persistence Behavior
The only persistent state is `i915->edram_size_mb`, set during hardware probe and used as a device capability for the rest of the driver lifetime. The code does not program eDRAM registers; it only reads capability state.

## Dependencies and Integration Points
It depends on platform macros, uncore register reads, `HSW_EDRAM_CAP` bitfield macros, and DRM logging. `i915_driver_hw_probe()` calls it before DMA/GGTT setup. `i915_drv.h` exposes `HAS_EDRAM()` and `HAS_WT()` based on the stored size.

## Risks
Register format differences are handled coarsely: pre-gen9 always reports 128 MB when enabled. Reading too early without uncore access would fail, so probe ordering matters. Incorrect decode tables would affect cache policy and reported capabilities.

## Test Signals
Boot Haswell/Broadwell/gen9 eDRAM systems and confirm the `Found ...MB of eDRAM` log, `HAS_EDRAM()` behavior, WT cache paths, and no eDRAM report on unsupported or disabled platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_edram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_edram.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_edram.h

## Purpose
This header declares the eDRAM detection helper used during i915 hardware probe.

## Important APIs, Types, and Functions
The only API is `void i915_edram_detect(struct drm_i915_private *i915)`.

## Control Flow
There is no internal flow. Callers invoke the function before later feature predicates and cache policy code depend on `i915->edram_size_mb`.

## State and Persistence Behavior
The header stores no state; the implementation updates `drm_i915_private`.

## Dependencies and Integration Points
It forward-declares `struct drm_i915_private` and is included by `i915_driver.c` and other code that needs explicit eDRAM probing.

## Risks
The include guard says `__I915_DRAM_H__`, which is harmless but easy to confuse with DRAM-related display code. Signature changes must match the implementation.

## Test Signals
Build coverage and successful hardware probe with eDRAM detection are sufficient signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_edram.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_file_private.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_file_private.h

## Purpose
`i915_file_private.h` defines the per-open DRM file state used by GEM contexts, proto-contexts, VMs, client accounting, and client ban scoring.

## Important APIs, Types, and Functions
`struct drm_i915_file_private` stores the owning `drm_i915_private`, either `drm_file *file` or RCU head for deferred free, `proto_context_lock`, `proto_context_xa`, `context_xa`, `vm_xa`, default BSD engine selection, ban scoring fields, hang timestamp, and `i915_drm_client *client`. Ban constants are `I915_CLIENT_SCORE_HANG_FAST`, `I915_CLIENT_FAST_HANG_JIFFIES`, `I915_CLIENT_SCORE_CONTEXT_BAN`, and `I915_CLIENT_SCORE_BANNED`.

## Control Flow
The header has no executable code. `i915_gem_open()` allocates and initializes the structure, context creation and lookup populate the xarrays, postclose tears contexts down and frees it through RCU, and hang/context-ban logic updates `ban_score` and `hang_timestamp`.

## State and Persistence Behavior
The structure persists for one DRM file lifetime. Proto-contexts allow userspace to configure a context ID through UAPI before it is finalized into a full `i915_gem_context`; `proto_context_lock` serializes both proto-context manipulation and finalization. `context_xa` and `vm_xa` persist live context/VM handles. Ban score persists across contexts owned by the file and prevents more work after threshold.

## Dependencies and Integration Points
It integrates DRM file-private storage, GEM context UAPI, xarray handle allocation, VM handles, client fdinfo accounting, and context-ban/hangcheck policy. The detailed comments document why proto-context locking is deliberately broad.

## Risks
The proto-context/context xarray split is race-prone if any path bypasses `proto_context_lock`. File-private free is RCU-deferred, so users must respect lifetime rules. Ban score constants affect denial-of-service mitigation and must be consistent with hang accounting expectations.

## Test Signals
IGT context create/setparam/getparam/destroy tests, VM create/destroy tests, concurrent context lookup/finalization, file close during active contexts, client ban tests after rapid hangs, and RCU/lockdep coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_file_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_freq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_freq.c

## Purpose
`i915_freq.c` decodes legacy chipset strap registers into front-side-bus and memory frequencies for pre-modern Intel graphics platforms.

## Important APIs, Types, and Functions
Exported functions are `i9xx_fsb_freq()`, `ilk_fsb_freq()`, and `ilk_mem_freq()`. They read `CLKCFG`, `CSIPLL0`, and `DDRMPLL1` respectively and map register values to kHz-like integer frequencies.

## Control Flow
`i9xx_fsb_freq()` masks `CLKCFG_FSB_MASK` and uses different switch tables for Pineview/mobile versus desktop straps, returning defaults with `MISSING_CASE()` for unknown values. `ilk_fsb_freq()` decodes Ironlake CPU-side PLL values and returns `0` on unknown values after debug logging. `ilk_mem_freq()` decodes DDR PLL values for 800/1066/1333/1600 MHz memory and returns `0` for unknown values.

## State and Persistence Behavior
The file stores no state. It reads current strap/PLL registers each time. Comments note that some BIOSes can configure straps independently from actual FSB frequency, so returned values are capability/strap interpretations rather than guaranteed live clocks.

## Dependencies and Integration Points
It depends on uncore register access, platform predicates, `intel_mchbar_regs.h`, and DRM debug logging. Callers use these helpers for legacy bandwidth, watermark, or platform information calculations.

## Risks
The mapping is based on legacy documentation and straps, not live measurement. Unknown values fall back to a desktop default in `i9xx_fsb_freq()` but to zero in Ironlake helpers, so callers must handle both. Register access requires MCHBAR/uncore availability.

## Test Signals
Boot legacy i9xx/Pineview/Ironlake systems and compare decoded frequencies with platform expectations; exercise unknown strap debug logs via simulation/selftests where possible; verify callers tolerate zero returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_freq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_freq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_freq.h

## Purpose
This header declares legacy i915 frequency decode helpers.

## Important APIs, Types, and Functions
It declares `i9xx_fsb_freq()`, `ilk_fsb_freq()`, and `ilk_mem_freq()`, all taking `struct drm_i915_private *` and returning unsigned integer frequencies.

## Control Flow
There is no control flow. Callers include the header when they need legacy strap/PLL decode helpers.

## State and Persistence Behavior
The header stores no state and only forward-declares the i915 private type.

## Dependencies and Integration Points
It is a lightweight interface between legacy display/bandwidth code and the implementation in `i915_freq.c`.

## Risks
Return units are implicit in implementation conventions and should be preserved by callers. Adding includes can create unnecessary coupling.

## Test Signals
Build coverage and runtime frequency decode on legacy hardware are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_freq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gem.c

## Purpose
`i915_gem.c` implements core i915 GEM lifecycle and several legacy GEM UAPI operations: aperture reporting, object unbinding, pread/pwrite, software-finish cache flushes, runtime suspend cleanup, GGTT pinning, madvise/shrinker list transitions, workqueue draining, GEM hardware initialization/removal/release, and per-file GEM open.

## Important APIs, Types, and Functions
Important exported functions include `i915_gem_get_aperture_ioctl()`, `i915_gem_object_unbind()`, `i915_gem_pread_ioctl()`, `i915_gem_pwrite_ioctl()`, `i915_gem_sw_finish_ioctl()`, `i915_gem_runtime_suspend()`, `i915_gem_object_ggtt_pin_ww()`, `i915_gem_object_ggtt_pin()`, `i915_gem_madvise_ioctl()`, `i915_gem_drain_freed_objects()`, `i915_gem_drain_workqueue()`, `i915_gem_init()`, `i915_gem_driver_register()`, `i915_gem_driver_unregister()`, `i915_gem_driver_remove()`, `i915_gem_driver_release()`, `i915_gem_init_early()`, `i915_gem_cleanup_early()`, and `i915_gem_open()`.

## Control Flow
Pread/pwrite first reject unsupported gen12+ non-Tigerlake platforms, validate userspace pointers, look up GEM handles, bounds-check object ranges, and honor object-specific `ops->pread/pwrite` hooks. Generic pread waits for object idleness, tries shmem page reads with cache flush handling, and falls back to GGTT reads if needed. Generic pwrite waits for all activity, attempts fast GGTT writes for non-struct-page or clflush-needing objects, then falls back to shmem writes on page faults or ENOSPC. GGTT access uses `i915_gem_gtt_prepare()` to set GTT domain, opportunistically pin an untiled mappable VMA, or allocate a temporary one-page mappable GGTT node and insert object pages page-by-page.

`i915_gem_object_unbind()` walks an object's VMA list under object lock, gets runtime PM first to avoid shrinker/ACPI deadlocks, optionally tests only, tries async unbind, active unbind, VM trylock unbind, or normal VMA unbind, and uses an RCU barrier retry when VM refs could be in deferred release. GGTT pinning creates/reuses VMA instances, checks mappable aperture size and nonblocking heuristics, discards misplaced active/pinned VMAs by removing them from the object tree and retrying, unbinds idle misplaced VMAs, pins with `PIN_GLOBAL`, revokes unnecessary fences, and waits for bind completion.

Initialization verifies cache-level enum assumptions, adjusts vGPU page-size capabilities, fetches uC firmware and WOPCM data per GT, programs private PAT for gen8+, initializes GGTT, applies clock gating/workarounds before context state capture, initializes each GT, and registers UABI engines. On `-EIO`, it can wedge GTs and keep KMS minimally alive by re-enabling GGTT and clock gating. Removal suspends late GEM, removes GTs, clears UABI engines, drains work; release frees GTs/uC firmware and verifies context list cleanup.

## State and Persistence Behavior
GEM state lives in `i915->mm`, object VMA lists, shrink/purge lists, userfault lists, GGTT nodes, fence registers, runtime PM lists, contexts, and file-private state. `madvise` persists object purgeability unless already purged, moves objects between shrink and purge lists, and can truncate backing storage. Runtime suspend releases GTT mmap/userfault mappings and marks unpinned fence registers dirty because hardware fence state is lost across powerdown. `i915_gem_open()` allocates per-file state, client accounting, context xarrays, VM xarray, default engine selection, and hang timestamp.

## Dependencies and Integration Points
This file integrates GEM objects and regions, GGTT, VMA bind/unbind, TTM workqueues, DMA reservation waits, runtime PM, frontbuffer invalidation/flush, cache coherency/clflush, display fences, vGPU capability reporting, uC firmware, WOPCM, GT init, clock-gating workarounds, DRM UAPI handles, and i915 fd private/client accounting.

## Risks
Legacy pread/pwrite paths mix usercopy, cache maintenance, runtime PM, tiled-object restrictions, and temporary GGTT mappings; page fault fallback behavior is subtle. Object unbind can race with VMA destruction, VM release, shrinkers, and active requests, so lock ordering and runtime wakerefs are critical. GGTT pinning heuristics intentionally return ENOSPC in nonblocking cases to avoid aperture ping-pong; callers need fallbacks. `-EIO` initialization recovery keeps the driver partially alive and must not leave later teardown assuming full init. Workqueue drain loops rely on RCU barriers and bounded recursive passes.

## Test Signals
IGT GEM pread/pwrite/sw_finish/get_aperture/madvise tests, usercopy fault injection, tiled versus untiled object coverage, runtime PM suspend with GTT mmap faults, GGTT pin/unpin tests under aperture pressure, vGPU huge-GTT capability tests, GT init failure injection including `-EIO`, shrinker/purge behavior, lockdep for object/VM locks, and context/file open-close leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gem.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gem.h

## Purpose
`i915_gem.h` declares core GEM lifecycle, unbind, GGTT pinning, runtime suspend, and per-file open APIs, and defines GEM debug/tracing macros and shared constants.

## Important APIs, Types, and Functions
Declarations cover early init/cleanup, workqueue draining, `i915_gem_object_ggtt_pin_ww()`, `i915_gem_object_ggtt_pin()`, `i915_gem_object_unbind()`, runtime suspend, driver init/register/unregister/remove/release, and `i915_gem_open()`. It defines `I915_GEM_GPU_DOMAINS`, unbind flags (`ACTIVE`, `BARRIER`, `TEST`, `VM_TRYLOCK`, `ASYNC`), `I915_GEM_IDLE_TIMEOUT`, `GEM_QUIRK_PIN_SWIZZLED_PAGES`, and debug macros `GEM_BUG_ON`, `GEM_WARN_ON`, `GEM_TRACE`, and related variants.

## Control Flow
The header itself has only macro flow. In debug builds, `GEM_BUG_ON()` emits trace/error diagnostics and either warns or BUGs depending on config; in non-debug builds it compiles conditions through `BUILD_BUG_ON_INVALID` to preserve type checking without runtime cost. Trace macros either emit ftrace/pr_err data or compile away.

## State and Persistence Behavior
The header stores no state. Its constants define object domain masks, unbind behavior, idle timeout, and quirk bits persisted in driver/object state.

## Dependencies and Integration Points
It is included by broad GEM, GT, driver, and error paths. It depends on DRM driver types and i915 utility macros, while forward-declaring GEM object, VMA, file, private, ww context, and GTT view types.

## Risks
Macro behavior changes can alter assertions globally. Unbind flag semantics must match `i915_gem.c`; adding flags requires auditing all callers. Debug macros can have side effects in expressions if used incorrectly, so conditions should be side-effect-free.

## Test Signals
Build with `CONFIG_DRM_I915_DEBUG_GEM`, `CONFIG_DRM_I915_TRACE_GEM`, and non-debug configs; run GEM selftests and ensure assertions catch invalid lock/state conditions without affecting release builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gem_evict.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gem_evict.c

## Purpose
`i915_gem_evict.c` frees virtual address space in i915 GTT address spaces. It evicts idle or waitable VMAs from `drm_mm` ranges to satisfy new bindings, fixed-node reservations, or full-VM defragmentation, without freeing the objects' backing memory.

## Important APIs, Types, and Functions
Public APIs are `i915_gem_evict_something()`, `i915_gem_evict_for_node()`, and `i915_gem_evict_vm()`. Helpers include `dying_vma()`, `ggtt_flush()`, `grab_vma()`, `ungrab_vma()`, `mark_free()`, and `defer_evict()`. Selftest state `igt_evict_ctl.fail_if_busy` can force busy behavior.

## Control Flow
`i915_gem_evict_something()` assumes `vm->mutex` is held, initializes a `drm_mm_scan` for the requested hole, retires requests, then scans `vm->bound_list` in rough LRU order. It defers active or scanout VMAs on the first pass by moving them to the tail, tries to grab object locks and add unpinned VMAs to the scanner, and on success pins candidates temporarily, removes nonselected blocks, unbinds selected VMAs, and evicts color-conflicting neighbors. If no hole exists in GGTT and nonblocking is not set, it idles all GTs sharing the GGTT with `ggtt_flush()`, marks the next pass nonblocking, and scans again.

`i915_gem_evict_for_node()` targets a fixed `drm_mm_node` range, expands the search for cache-color guard pages, refuses unevictable/pinned/nonblocking-active overlaps, grabs and temporarily pins overlapping VMAs, then unbinds them. `i915_gem_evict_vm()` evicts all unpinned VMAs from a VM, flushing GGTT first to unpin context/ring objects, splitting VMAs into already-locked and newly-locked lists, optionally returning a referenced `busy_bo` when trylock fails, and ignoring most non-interrupt unbind failures so it can continue cleansing.

## State and Persistence Behavior
Eviction mutates VM `bound_list` ordering, `drm_mm` node allocation state, VMA pin counts, and VMA binding state. It takes temporary object refs/locks to stabilize VMAs. It does not destroy GEM objects or free backing pages. For GGTT, it may force GPU idleness and request retirement to release active pins on contexts/rings.

## Dependencies and Integration Points
The code depends on `drm_mm` scanning, VMA flags and node colors, object ww locking, GT request retirement/idling, GGTT multi-GT lists, tracepoints, and `__i915_vma_unbind()`. It is called by GTT insertion/reservation and VMA bind/pin paths.

## Risks
Locking is subtle: callers hold `vm->mutex`, while object locks are trylocked through ww contexts to avoid deadlocks. Dying objects need special handling because ref acquisition can fail. Active/scanout deferral protects current work but can return ENOSPC under nonblocking pressure. GGTT flushing may stall indefinitely up to `MAX_SCHEDULE_TIMEOUT`. Color guard-page handling must evict neighbors only when colors conflict; mistakes can corrupt cache-domain isolation.

## Test Signals
IGT/selftests for eviction under fragmented address spaces, fixed-node conflicts, cache coloring, pinned and unevictable nodes, active nonblocking VMAs, full-VM eviction with busy_bo return, GGTT context/ring unpinning after idle, and lockdep/KCSAN coverage for ww locking paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gem_evict.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gem_evict.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gem_evict.h

## Purpose
This header declares the i915 GTT virtual-address-space eviction API.

## Important APIs, Types, and Functions
It declares `i915_gem_evict_something()`, `i915_gem_evict_for_node()`, and `i915_gem_evict_vm()`, with forward declarations for `drm_mm_node`, `i915_address_space`, `i915_gem_ww_ctx`, and GEM objects.

## Control Flow
There is no control flow. GTT insertion and bind paths call these functions while holding the relevant VM mutex.

## State and Persistence Behavior
The header stores no state. Its APIs mutate VM/VMA binding state in the implementation.

## Dependencies and Integration Points
It is the contract between `i915_gem_gtt.c`, VMA binding code, execbuf defragmentation, and the eviction implementation.

## Risks
Callers must satisfy locking and interpret ENOSPC/EBUSY/EINTR correctly. Function signatures expose flags shared with GTT pinning; semantics must remain aligned with `i915_gem_gtt.h`.

## Test Signals
Build and eviction selftests covering all three entry points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gem_evict.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gem_gtt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gem_gtt.c

## Purpose
`i915_gem_gtt.c` provides common GEM-to-GTT helpers: DMA mapping/unmapping object page tables and allocating/reserving `drm_mm_node` ranges in i915 address spaces with eviction fallback.

## Important APIs, Types, and Functions
Public functions are `i915_gem_gtt_prepare_pages()`, `i915_gem_gtt_finish_pages()`, `i915_gem_gtt_reserve()`, and `i915_gem_gtt_insert()`. The local helper `random_offset()` selects an aligned random replacement address for first-attempt eviction.

## Control Flow
`prepare_pages()` attempts bidirectional DMA mapping with skip-sync/no-kernel-mapping/no-warn attributes. If mapping fails, it repeatedly invokes the GEM shrinker for bound and unbound objects sized to the target object and retries until shrinker progress stops, then returns ENOSPC. `finish_pages()` optionally sleeps briefly for `ggtt->do_idle_maps` and unmaps the sg table.

`gtt_reserve()` validates alignment/range/node state, initializes the node, tries exact `drm_mm_reserve_node()`, and if the only failure is ENOSPC and eviction is allowed, calls `i915_gem_evict_for_node()` before retrying. `gtt_insert()` validates arguments, chooses low/high/best insertion mode from flags, normalizes small alignment to zero for `drm_mm`, tries direct insertion, optionally retries without one-shot mode, rejects no-evict, tries one random fixed reservation to avoid pathological LRU scans, and finally calls `i915_gem_evict_something()` plus an evict-mode `drm_mm_insert_node_in_range()`.

## State and Persistence Behavior
DMA mapping state persists in the sg table until `finish_pages()`. Insert/reserve mutate `node->size/start/color` and the VM's `drm_mm` allocation state. They may indirectly unbind other VMAs through eviction, changing VM bound lists and VMA binding state.

## Dependencies and Integration Points
This file depends on DMA mapping, GEM shrinker, GGTT idle-map policy, `drm_mm`, random number generation, VM cache coloring, GTT page-size constants, eviction APIs, tracepoints, and vGPU/device page-size behavior through callers. VMA bind/pin and object page preparation paths use these helpers.

## Risks
DMA remap failure recovery can trigger reclaim/eviction while the target object pages are being prepared; the code asserts it is not shrinking the same page set. Insert alignment and range checks are strict and use `GEM_BUG_ON()` for programmer errors. Random replacement avoids worst-case scans but can evict surprising objects. Flags such as `PIN_NOEVICT`, `PIN_NOSEARCH`, `PIN_MAPPABLE`, and `PIN_HIGH` materially change placement and fallback behavior.

## Test Signals
GTT selftests for direct insert, fixed reserve, random eviction, no-evict/no-search flags, low/high/mappable placement, cache-color guard pages, DMA map failure with shrinker progress, and unmap after idle-map delays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gem_gtt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gem_gtt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gem_gtt.h

## Purpose
This header declares common GTT page-preparation and address-space allocation helpers and defines pin/bind placement flags shared across GEM/VMA code.

## Important APIs, Types, and Functions
It declares `i915_gem_gtt_prepare_pages()`, `i915_gem_gtt_finish_pages()`, `i915_gem_gtt_reserve()`, and `i915_gem_gtt_insert()`. It defines `I915_COLOR_UNEVICTABLE` and flags `PIN_NOEVICT`, `PIN_NOSEARCH`, `PIN_NONBLOCK`, `PIN_MAPPABLE`, `PIN_ZONE_4G`, `PIN_HIGH`, `PIN_OFFSET_BIAS`, `PIN_OFFSET_FIXED`, `PIN_OFFSET_GUARD`, `PIN_VALIDATE`, `PIN_GLOBAL`, `PIN_USER`, and `PIN_OFFSET_MASK`.

## Control Flow
No executable flow is present. Callers pass flags into VMA pin/bind and GTT insertion paths to control search, eviction, mappable placement, fixed offsets, guard pages, validation-only behavior, and global/user binding.

## State and Persistence Behavior
The header stores no state. Its constants influence persistent VMA/node placement and binding flags.

## Dependencies and Integration Points
It includes IO mapping, `drm_mm`, Intel GTT constants, and i915 scatterlist helpers. It is consumed by GEM object, VMA, execbuf, eviction, and error-capture code.

## Risks
Flag values are ABI internal but widely shared; changing them breaks bitmask users. `PIN_OFFSET_MASK` overlaps low address bits by design and must stay aligned with GTT page masks. `I915_COLOR_UNEVICTABLE` is used to protect non-VMA nodes from eviction.

## Test Signals
Build coverage plus GTT/VMA selftests for each flag combination and unevictable-color behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gem_gtt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gem_ww.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gem_ww.c

## Purpose
`i915_gem_ww.c` implements i915's wrapper around Linux dma-resv wound/wait locking for GEM objects. It tracks objects locked within an acquire context and provides deadlock backoff handling.

## Important APIs, Types, and Functions
Public functions are `i915_gem_ww_ctx_init()`, `i915_gem_ww_ctx_fini()`, `i915_gem_ww_ctx_backoff()`, and `i915_gem_ww_unlock_single()`. The local helper `i915_gem_ww_ctx_unlock_all()` unlocks and drops references for every object in `ww->obj_list`.

## Control Flow
Init initializes `ww_acquire_ctx` with `reservation_ww_class`, the object list, interruptible flag, and `contended`. Normal finish unlocks all tracked objects, warns if `contended` remains, and finalizes the acquire context. Backoff requires a contended object, unlocks all currently held objects, slow-locks the contended object's dma-resv interruptibly or uninterruptibly, adds it to the object list on success, or drops its reference on failure, then clears `contended`.

## State and Persistence Behavior
The ww context is short-lived per multi-object locking operation. It owns references to locked GEM objects via `obj_list` and temporarily owns `contended` across an `-EDEADLK` retry.

## Dependencies and Integration Points
It depends on dma-resv ww locking, GEM object lock/unlock/ref helpers, and the reservation ww class. It is used by GEM pinning, execbuf, eviction, and other multi-object operations.

## Risks
Every object added to `obj_list` must be referenced and locked; otherwise `unlock_all` will corrupt lifetime. Missing backoff after `-EDEADLK` can deadlock. Interruptible contexts must propagate EINTR. `i915_gem_ww_unlock_single()` assumes the object is on the list.

## Test Signals
Multi-object locking selftests, forced `-EDEADLK` backoff paths, interruptible signal handling, lockdep ww-class validation, and refcount leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gem_ww.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gem_ww.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gem_ww.h

## Purpose
This header defines the i915 GEM wound/wait context structure and retry-loop helper used for deadlock-safe multi-object reservation locking.

## Important APIs, Types, and Functions
`struct i915_gem_ww_ctx` contains `ww_acquire_ctx ctx`, `obj_list`, `contended`, and `intr`. It declares init/fini/backoff/unlock-single functions and defines inline `__i915_gem_ww_fini()` plus the `for_i915_gem_ww()` retry macro.

## Control Flow
`for_i915_gem_ww()` initializes a ww context, runs the loop while the caller returns `-EDEADLK`, and lets `__i915_gem_ww_fini()` perform backoff or final cleanup. If backoff succeeds it deliberately returns `-EDEADLK` to rerun the caller's locking body with the contended object held.

## State and Persistence Behavior
The context is stack/local operation state. It stores locked object refs until final cleanup and a contended object between trylock failure and slow-lock backoff.

## Dependencies and Integration Points
It includes DRM driver types for the ww class and forward references GEM objects. It is used throughout i915 GEM/VMA code for multi-object lock ordering.

## Risks
The macro expects callers to assign `_err` correctly inside the loop. Returning success too early without cleanup would leak locks, while mishandling `-EDEADLK` can spin or deadlock.

## Test Signals
Compiler coverage of macro users, lockdep ww tests, and runtime paths that force contended object backoff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gem_ww.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_getparam.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_getparam.c

## Purpose
`i915_getparam.c` implements the legacy `DRM_IOCTL_I915_GETPARAM` UAPI. It reports chipset IDs, engine availability, memory/cache capabilities, reset and scheduler capabilities, firmware/PXP status, mmap/perf versions, topology fields, and timestamp frequencies.

## Important APIs, Types, and Functions
The exported entry point is `i915_getparam_ioctl()`. It consumes `drm_i915_getparam_t`, writes to `param->value`, and switches on `I915_PARAM_*` constants. It calls helpers such as `intel_engine_lookup_user()`, `intel_overlay_available()`, `i915_cmd_parser_get_version()`, `intel_sseu_subslice_total()`, `intel_huc_check_status()`, `intel_pxp_get_readiness_status()`, `i915_gem_mmap_gtt_version()`, `intel_engines_has_context_isolation()`, and i915 perf timestamp/version helpers.

## Control Flow
The ioctl rejects old UMS/DRI parameters with ENODEV, returns PCI device/revision and fence counts directly, checks UABI engine lookup for BSD/BLT/VEBOX/BSD2, returns feature macros for LLC/WT/PPGTT/secure batches, gates secure batches on `CAP_SYS_ADMIN`, reports scheduler bits, GuC-dependent context frequency hints, context isolation, and topology masks. Xe_HP and newer reject legacy slice/subslice masks in favor of topology queries. Unknown parameters log a debug message and return EINVAL. The final value is copied to userspace with `put_user()`.

## State and Persistence Behavior
The function reads current immutable or semi-persistent device state: PCI IDs, GGTT fences, engine registry, runtime SSEU topology, scheduler caps, module params, firmware readiness, PXP readiness, GT clock frequency, coherent GGTT flag, and perf timestamp frequency. It does not mutate driver state.

## Dependencies and Integration Points
It integrates legacy i915 UAPI, PCI, display overlay, engine UABI registry, command parser, SSEU topology, GuC/HuC/PXP, GEM mmap versioning, scheduler caps, perf OA, and capability macros from `i915_drv.h`.

## Risks
This is user-visible ABI. Values must remain compatible even when newer query ioctls exist. Returning true for always-supported features is intentional for historical UAPI, but unsupported hardware exceptions must be explicit. Topology deprecation boundaries such as Xe_HP must remain correct. Firmware/PXP helpers can return negative errors that propagate to userspace.

## Test Signals
IGT `getparam` coverage for every parameter, unknown-param EINVAL, invalid userspace pointer EFAULT, capability values on platforms with/without engines and GuC/PXP/HuC, topology mask behavior before and after Xe_HP, and perf timestamp frequency sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_getparam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_getparam.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_getparam.h

## Purpose
This header declares the i915 GETPARAM ioctl handler.

## Important APIs, Types, and Functions
It declares `int i915_getparam_ioctl(struct drm_device *dev, void *data, struct drm_file *file_priv)`.

## Control Flow
No control flow is present. `i915_driver.c` registers the function in `i915_ioctls[]` for `DRM_IOCTL_I915_GETPARAM`.

## State and Persistence Behavior
The header stores no state; the implementation reads device capability state.

## Dependencies and Integration Points
It forward-declares DRM device/file types and bridges the ioctl table to `i915_getparam.c`.

## Risks
Signature drift breaks ioctl registration. The lightweight header should stay free of unnecessary dependencies.

## Test Signals
Build coverage and GETPARAM ioctl tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_getparam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gmch.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gmch.c

## Purpose
`i915_gmch.c` manages legacy GMCH bridge discovery and MCHBAR enablement/resource allocation. It ensures memory-controller registers are accessible during early i915 MMIO/runtime-info probing.

## Important APIs, Types, and Functions
Public functions are `i915_gmch_bridge_setup()`, `i915_gmch_bar_setup()`, and `i915_gmch_bar_teardown()`. Internal helpers are `i915_gmch_bridge_release()`, `mchbar_reg()`, and `intel_alloc_mchbar_resource()`.

## Control Flow
Bridge setup locates bus 0 device/function 0 in the same PCI domain as the graphics device and registers a DRM-managed `pci_dev_put()` action. MCHBAR setup skips Valleyview/Cherryview, checks whether MCHBAR is already enabled via `DEVEN` on i915G/GM or the MCHBAR register on later chips, allocates a resource if ACPI/PNP did not reserve the current address, writes high/low address dwords as needed, marks that disable is required, and sets the enable bit. Teardown disables MCHBAR only if this driver enabled it and releases any allocated resource.

## State and Persistence Behavior
Persistent state lives in `i915->gmch`: bridge `pdev`, resource `mch_res`, and `mchbar_need_disable`. DRM-managed action releases the bridge reference with the DRM device. MCHBAR may remain enabled if firmware had already enabled it; the driver only disables self-enabled instances.

## Dependencies and Integration Points
The file depends on PCI config access, PNP reserved range checks, DRM managed actions, PCI resource allocation, platform predicates, and Intel PCI config register definitions. It is called from `i915_driver_mmio_probe()` before runtime device info reads and torn down in MMIO release.

## Risks
Incorrect resource allocation or enable bits can conflict with firmware/ACPI reservations or leave MCHBAR inaccessible. Teardown must not disable firmware-enabled MCHBAR. Legacy platform differences between i915G/GM and gen4+ are encoded in separate register paths. Missing bridge device aborts probe.

## Test Signals
Boot legacy GMCH systems with and without firmware-enabled MCHBAR, verify no resource conflicts, confirm runtime info reads dependent on MCHBAR, check teardown on probe failure, and inspect PCI config before/after driver unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gmch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gmch.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gmch.h

## Purpose
This header declares GMCH bridge and MCHBAR setup/teardown helpers.

## Important APIs, Types, and Functions
It declares `i915_gmch_bridge_setup()`, `i915_gmch_bar_setup()`, and `i915_gmch_bar_teardown()`.

## Control Flow
There is no control flow. `i915_driver.c` calls setup during MMIO probe and teardown during MMIO release/failure unwind.

## State and Persistence Behavior
The header stores no state; implementation updates `i915->gmch`.

## Dependencies and Integration Points
It forward-declares `struct drm_i915_private` and links driver probe code to legacy GMCH support.

## Risks
The setup/teardown pairing is ordering-sensitive around runtime info and uncore register access.

## Test Signals
Build coverage and legacy platform probe/unload testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gmch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gpu_error.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gpu_error.c

## Purpose
`i915_gpu_error.c` captures, stores, formats, exposes, and frees i915 GPU error/coredump state. It records device, GT, engine, request, context, GuC, VMA, fence, display snapshot, and parameter data after hangs or on-demand debug capture, then serves it through debugfs and `/sys/class/drm/card*/error`.

## Important APIs, Types, and Functions
Public functions include `i915_error_printf()`, `i915_gpu_coredump_copy_to_buffer()`, `__i915_gpu_coredump_free()`, `intel_engine_coredump_alloc()`, `intel_engine_coredump_add_request()`, `intel_engine_coredump_add_vma()`, `i915_gpu_coredump_alloc()`, `intel_gt_coredump_alloc()`, `i915_vma_capture_prepare()`, `i915_vma_capture_finish()`, `i915_error_state_store()`, `i915_capture_error_state()`, `i915_reset_error_state()`, `i915_disable_error_state()`, optional `intel_klog_error_capture()`, `i915_gpu_error_debugfs_register()`, `i915_gpu_error_sysfs_setup()`, and `i915_gpu_error_sysfs_teardown()`. Internal helpers implement scatterlist-backed text buffers, emergency page pools, optional zlib compression, VMA snapshot/copy, register recording, GuC CTB/HW-state capture, formatted printing, and debugfs/sysfs file operations.

## Control Flow
Capture starts in `i915_capture_error_state()`, which serializes through a static mutex in `i915_gpu_coredump()`, allocates a top-level coredump if error capture is enabled, snapshots global device metadata, allocates a GT coredump, prepares VMA compression, optionally records GuC firmware/log/CTB state, records GT info and engines, captures display snapshot, stores the first non-simulated error with `cmpxchg`, logs an ecode string, and drops the local reference. Engine capture records registers unless GuC capture supplies them, finds the hung request/context, captures context metadata and ring/HW context/batch/user VMAs, optionally matches GuC capture nodes, appends HW status and workaround context dumps, and links non-simulated engine coredumps.

VMA capture uses held `i915_vma_resource` snapshots, copies pages via a reserved GGTT error-capture slot, LMEM IO mapping, or shmem page kmap, compresses or stores pages into `i915_vma_coredump`, and later prints them as ASCII85 with a compression marker. Formatting lazily builds a scatterlist of text chunks on first read, printing kernel time, platform, PCI ID, IOMMU, runtime PM state, GT registers/fences/engines, GuC state, capabilities, params, and display snapshot. Reads copy from the cached scatterlist using `error->fit` as a cursor hint. Writes to debugfs/sysfs clear the stored first error.

## State and Persistence Behavior
The persistent device error slot is `i915->gpu_error.first_error`, protected by `gpu_error.lock` for reset/read and installed with `cmpxchg` so only the first error is saved. `ERR_PTR()` values can mark capture failure or disabled state. Coredumps are kref-managed and contain copied metadata, copied firmware path strings, VMA page lists, scatterlist text cache, display snapshot, and GT/engine linked lists. Captured data is a snapshot and does not hold live GEM objects, because VMA resources and pages are copied into anonymous memory.

## Dependencies and Integration Points
The file integrates GT reset/hang detection, engine register access, execlists, GuC capture and CT buffers, firmware metadata, GEM contexts and requests, VMA resources, GGTT error-capture aperture, LMEM and shmem memory access, zlib/ascii85, display snapshot capture, runtime PM, params/device-info printing, debugfs, sysfs, and optional debug GEM klog dumping.

## Risks
Capture often runs near reset/hang paths where memory allocation and locking are constrained; it uses `ALLOW_FAIL` and emergency page pools but can still fail. The GGTT error-capture slot must be serialized by `ggtt->error_mutex` and cleared after use. Compression and ASCII85 formatting can be large and slow; klog dumping chunks output to avoid huge lines but still risks console latency. Sysfs reads can be inconsistent if another client clears/replaces the dump mid-read, as noted by FIXME. GuC capture and non-GuC register capture have different ownership of register groups, so mixing flags can print stale/missing data. `intel_hdcp_gsc_context_free` is unrelated but double-release style bugs in similar VMA cleanup patterns would be severe here.

## Test Signals
IGT hang/error-state tests, forced engine resets, GuC and execlists submission coverage, error capture disabled mode, simulated no-error-capture contexts, sysfs/debugfs read/write clearing, large VMA compression/decompression parsing by userspace tools, LMEM and shmem VMA capture, display snapshot presence, klog capture under debug GEM, allocation failure injection, and lockdep around error capture mutexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gpu_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gpu_error.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gpu_error.h

## Purpose
`i915_gpu_error.h` defines the structures and APIs for i915 GPU coredump/error capture. It is the shared contract between reset/hang paths, GT/engine capture code, debugfs/sysfs exposure, and no-op builds when error capture is disabled.

## Important APIs, Types, and Functions
Key structs are `i915_vma_coredump`, `i915_request_coredump`, `intel_engine_coredump`, `intel_ctb_coredump`, `intel_gt_coredump`, `i915_gpu_coredump`, `i915_gpu_error`, and `drm_i915_error_state_buf`. Inlines expose reset counters and increment engine reset counts. APIs include capture allocation for GPU/GT/engine, request/VMA coredump addition, VMA compression prepare/finish, error state store/reset/disable, kref get/put, copy-to-buffer, debugfs/sysfs registration, and optional klog capture. `CORE_DUMP_FLAG_IS_GUC_CAPTURE` marks GuC-sourced register capture.

## Control Flow
When `CONFIG_DRM_I915_CAPTURE_ERROR` is enabled, callers can allocate coredumps, add engine/request/VMA state, store the first error, expose it, and reset it. When disabled, the same APIs compile to stubs that do nothing or return NULL, allowing callers to avoid preprocessor complexity. Reset count inlines always operate on atomics in `i915_gpu_error`.

## State and Persistence Behavior
`i915_gpu_error` persists in `drm_i915_private` and holds `first_error`, global reset count, and per-engine-class reset counts. Coredump structs are snapshot-owned and kref-counted. Engine and GT coredumps are linked lists; VMA coredumps own copied page lists; formatted output may be cached as scatterlists.

## Dependencies and Integration Points
The header depends on atomic/kref/time/sched, DRM MM, Intel engine/GT/uC firmware types, device info, GEM/GTT, params, and scheduler types. It is included by driver core, reset paths, GT code, GEM capture paths, and user-visible debug setup.

## Risks
The structures are large and tightly coupled to register-generation behavior. Adding fields requires updating allocation, printing, and cleanup. Stubs must preserve call-site expectations in non-capture builds. Reset engine count indexes by engine class, so class bounds must remain valid.

## Test Signals
Build with capture enabled/disabled, debug GEM enabled/disabled, GuC capture paths, reset counter updates, first-error lifetime/refcount tests, and userspace error-state reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gpu_error.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gtt_view_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gtt_view_types.h

## Purpose
This header defines the compact data structures that describe alternate GTT views of GEM objects: normal, rotated, partial, and remapped. Display and VMA code use these views to bind object memory in layouts suitable for scanout and partial mappings.

## Important APIs, Types, and Functions
Types are `struct intel_remapped_plane_info`, `struct intel_rotation_info`, `struct intel_partial_info`, `struct intel_remapped_info`, `enum i915_gtt_view_type`, and `struct i915_gtt_view`. View type values encode the size of the corresponding payload for rotated, partial, and remapped views.

## Control Flow
There is no executable flow. Callers populate `i915_gtt_view` and pass it to VMA/GGTT pinning and display mapping helpers, which use `type` to interpret the union payload.

## State and Persistence Behavior
View structures are value descriptors. `intel_remapped_plane_info` is packed and uses bitfields to store page offsets and linear-vs-tiled interpretation. No global state is stored here.

## Dependencies and Integration Points
It depends only on Linux integer types. It integrates display plane rotation/remapping, partial object views, and GEM VMA instance lookup, where the view becomes part of the VMA identity.

## Risks
The comments explicitly require no holes/padding in union members. Packing and enum values tied to struct sizes are part of hashing/comparison assumptions in VMA code. Bitfield layout and page-based units must be preserved.

## Test Signals
Display rotation/remapped-plane tests, partial view bindings, VMA view identity tests, static size/layout assertions where available, and modeset/plane updates using rotated framebuffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gtt_view_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_hdcp_gsc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_hdcp_gsc.c

## Purpose
`i915_hdcp_gsc.c` implements the i915 display HDCP-over-GSC interface. It allocates command buffers, pins them in the media GT GGTT, builds GSC HECI headers, submits synchronous HDCP messages to GSC firmware, handles pending replies, and exports callbacks to display HDCP code.

## Important APIs, Types, and Functions
The local `struct intel_hdcp_gsc_context` stores the i915 pointer, pinned VMA, input command mapping, and output command mapping. Interface methods are `intel_hdcp_gsc_check_status()`, `intel_hdcp_gsc_context_alloc()`, `intel_hdcp_gsc_context_free()`, and `intel_hdcp_gsc_msg_send()`. Helpers include `intel_hdcp_gsc_initialize_message()` and `intel_gsc_send_sync()`. The exported interface object is `i915_display_hdcp_interface`.

## Control Flow
Status check verifies a media GT exists and the GSC firmware is running. Context allocation allocates the wrapper, creates a two-page shmem GEM object for input/output, maps it with the GT's coherent map type, creates a VMA in the media GGTT, pins it `PIN_GLOBAL | PIN_HIGH`, zeroes the buffer, and stores input/output page pointers. Message send validates GSC use, rejects payloads larger than one page minus header, clears both pages, generates a host session ID, emits an MTL HECI header for HDCP, copies the input payload, and calls `intel_gsc_send_sync()` with GGTT offsets. If GSC returns message-pending, it retries up to 20 times with 50 ms sleeps using the message handle in the header. On success it bounds the reply size and copies output payload to the caller.

## State and Persistence Behavior
The context persists across display HDCP transactions until freed. The two-page GEM object remains pinned and mapped; input is at page 0 and output at page 1. Each message overwrites headers/payloads and uses a fresh host session ID. Firmware state is external in the media GT GSC.

## Dependencies and Integration Points
This file integrates display HDCP code, media GT/GSC uC firmware, HECI command submission, GEM shmem allocation, VMA GGTT pinning, coherent map selection, random bytes, sleep/retry logic, and DRM KMS logging. It is wired through `i915_driver.c`'s display parent interface.

## Risks
`intel_hdcp_gsc_context_free()` calls `i915_vma_unpin_and_release()` twice on the same `vma` pointer in the inspected source, which is a serious double-release risk unless the helper nulls the pointer and tolerates a second call. Message size arithmetic must include headers correctly to avoid firmware buffer overruns. Pending-message retry has a fixed one-second total wait and may fail slow firmware. Status checks rely on `i915->media_gt`; platforms without media GT return not ready.

## Test Signals
HDCP 2.2 authentication on GSC platforms, GSC firmware-not-running status path, oversized input/output ENOSPC, pending-message retry behavior, command submission failure propagation, reply-size mismatch logs, context allocation failure unwinds, and KASAN/Kmemleak coverage for context free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_hdcp_gsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_hdcp_gsc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_hdcp_gsc.h

## Purpose
This header exposes the i915 implementation of the display HDCP GSC interface.

## Important APIs, Types, and Functions
It declares `extern const struct intel_display_hdcp_interface i915_display_hdcp_interface`.

## Control Flow
There is no control flow. Display HDCP code obtains this interface through the display parent interface and invokes callbacks implemented in `i915_hdcp_gsc.c`.

## State and Persistence Behavior
The header stores no state. The implementation owns per-transaction/per-context state.

## Dependencies and Integration Points
It is a lightweight bridge between i915 core and split display HDCP/GSC code.

## Risks
Signature drift in `intel_display_hdcp_interface` must be reflected in the implementation. The header should remain dependency-light.

## Test Signals
Build coverage and HDCP GSC runtime tests on supported platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_hdcp_gsc.h -->
