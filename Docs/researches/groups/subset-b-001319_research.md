# Research: subset-b-001319

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_object.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_object.c

## Purpose
Implements AMDGPU buffer-object lifecycle and placement policy on top of DRM GEM and TTM. It creates user, VM, kernel, ISP-imported, and fixed-offset VRAM BOs; maps and unmaps them for the CPU; pins, unpins, fences, syncs, wipes, and reports them; and initializes/finalizes the driver memory manager.

## Important APIs, Types, and Functions
Key exported entry points are `amdgpu_bo_create`, `amdgpu_bo_create_user`, `amdgpu_bo_create_vm`, `amdgpu_bo_create_reserved`, `amdgpu_bo_create_kernel`, `amdgpu_bo_create_kernel_at`, `amdgpu_bo_create_isp_user`, `amdgpu_bo_free_kernel`, `amdgpu_bo_free_isp_user`, `amdgpu_bo_kmap`, `amdgpu_bo_pin`, `amdgpu_bo_unpin`, `amdgpu_bo_fault_reserve_notify`, `amdgpu_bo_release_notify`, `amdgpu_bo_sync_wait_resv`, and GPU-address helpers. `amdgpu_bo_placement_from_domain` translates AMDGPU GEM domains into TTM placements including VRAM, GTT, CPU, GDS/GWS/OA, doorbell, and preemptible memory. `amdgpu_bo_set_metadata`, `amdgpu_bo_get_metadata`, and tiling helpers handle user BO side metadata.

## Control Flow
Creation validates domain capacity, normalizes alignment, initializes a GEM private object, derives placement, calls `ttm_bo_init_reserved`, optionally clears VRAM with a kernel fence, and unreserves unless the caller supplied a reservation object. Kernel helpers then reserve, pin, optionally bind GART, and map. Pinning rejects userptrs, narrows imported BOs to GTT, selects preferred VRAM/GTT policy, validates placement through TTM, increments pin counters, and updates VRAM/GART pin accounting. Move and release callbacks update VM state, invalidate exported dma-buf mappings, unmap CPU kmap state, and wipe flagged VRAM before release.

## State and Persistence Behavior
Persistent runtime state lives in `struct amdgpu_bo` and TTM resources: preferred/allowed domains, placement array, flags, kmap, VM base, parent BO, KFD association, and XCP partition ID. User BO metadata and tiling flags are heap-owned by `struct amdgpu_bo_user`. Device accounting is held in atomics such as `vram_pin_size`, `visible_pin_size`, `gart_pin_size`, and `num_vram_cpu_page_faults`. No on-disk persistence is performed, but release wiping protects prior VRAM contents from later users.

## Dependencies and Integration Points
Depends heavily on DRM GEM, dma-buf, dma-resv, TTM, AMDGPU VM, VRAM/GTT managers, KFD eviction fences, GMC address translation, and tracepoints. It is called by GEM ioctls, GPU VM code, display scanout paths, firmware/kernel allocations, ISP/V4L2 integration, debugfs BO reporting, and page fault handling.

## Risks and Test Signals
Risks include incorrect domain fallback, leaked reservations on error paths, stale CPU mappings across moves, imported dma-buf pin imbalance, visible-VRAM migration failure on CPU faults, and release-wipe failures during suspend/unplug. Test by exercising GEM BO creation flags, VRAM-only and VRAM/GTT fallback, CPU faults on invisible VRAM, exported/imported dma-bufs, KFD eviction release, suspend teardown, debugfs BO output, and pin accounting under repeated pin/unpin cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_object.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_object.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_object.h

## Purpose
Defines the public BO interface for AMDGPU memory management. It exposes the core `amdgpu_bo` structures, BO creation parameters, VM mapping records, reservation/refcount helpers, GPU address helpers, suballocation helpers, and all function prototypes implemented by object and suballocation code.

## Important APIs, Types, and Functions
`struct amdgpu_bo_param` carries allocation size, alignment, domain, preferred domain, flags, TTM type, reservation object, destroy callback, and XCP partition selector. `struct amdgpu_bo_va_mapping` and `struct amdgpu_bo_va` model VM mappings, invalid/valid mapping lists, PT update fence state, XGMI flag, and queue reference state. `struct amdgpu_bo` wraps `ttm_buffer_object`, placement state, kmap state, flags, VM pointer, parent, optional MMU notifier, KFD memory, and XCP ID. `struct amdgpu_bo_user` adds tiling and metadata; `struct amdgpu_bo_vm` appends flexible VM entries.

## Control Flow
The header supplies inline adapters used throughout the driver: `ttm_to_amdgpu_bo`, `amdgpu_mem_type_to_domain`, `amdgpu_bo_reserve`, `amdgpu_bo_unreserve`, `amdgpu_bo_size`, GPU-page sizing, mmap offset, explicit-sync check, and encryption check. Callers build `amdgpu_bo_param`, call creation helpers, reserve before metadata/address operations, pin when a fixed GPU address is required, and unreserve/unref on completion.

## State and Persistence Behavior
The state model is reservation-centered: most mutable fields are protected by the BO reservation or VM page-directory reservation as documented inline. Mapping lists and queue references persist for the lifetime of a BO/VM relationship, while metadata persists only on user BOs until replacement or destruction. The XCP ID is immutable after creation except as encoded by the allocation parameters.

## Dependencies and Integration Points
Includes DRM AMDGPU UAPI definitions, the broad `amdgpu.h` device model, resource cursors, and optional MMU notifier support. Function prototypes connect this header to GEM ioctl handling, TTM callbacks, VM code, KFD, debugfs, and the DRM suballocator-backed SA manager.

## Risks and Test Signals
Risks are primarily contract mismatches: using user-only helpers on kernel BOs, accessing mapping lists without the documented reservation lock, failing to account for `AMDGPU_BO_MAX_PLACEMENTS`, and forgetting that `xcp_id_plus1 == 0` means any partition. Test signals include lockdep coverage for reservation rules, VM map/unmap stress, metadata ioctl tests, encrypted/explicit-sync flag behavior, and SA allocation/free tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_object.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_pll.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_pll.c

## Purpose
Computes pixel PLL divider settings and finds opportunities to share existing PPLLs across CRTCs. This is display clock plumbing for legacy ATOMBIOS/DC paths that need reference, feedback, fractional feedback, and post divider values matching a requested pixel clock.

## Important APIs, Types, and Functions
`amdgpu_pll_compute` is the main exported computation routine. Helpers `amdgpu_pll_reduce_ratio` and `amdgpu_pll_get_fb_ref_div` reduce target/reference ratios and clamp divider values. `amdgpu_pll_get_use_mask` reports active PPLL IDs. `amdgpu_pll_get_shared_dp_ppll` reuses an existing DP PPLL, while `amdgpu_pll_get_shared_nondp_ppll` reuses non-DP PPLLs when connector, mode clock, adjusted clock, and spread-spectrum state match.

## Control Flow
PLL computation derives allowed feedback, reference, and post divider ranges from `struct amdgpu_pll` flags and limits. It scales by ten when fractional feedback is enabled, reduces the target/reference ratio, scans post dividers for the smallest clock error, recomputes final feedback/reference dividers, applies fractional-jitter avoidance, and writes results plus the computed dot clock. Sharing helpers walk `dev->mode_config.crtc_list`, skip the current CRTC, inspect `amdgpu_crtc` encoder and PLL state, and return `ATOM_PPLL_INVALID` when reuse is unavailable.

## State and Persistence Behavior
The file is mostly stateless; it reads CRTC state and PLL descriptors and returns computed values. Persistent state is maintained by callers in `amdgpu_crtc->pll_id`, `adjusted_clock`, connector, encoder, and spread-spectrum fields.

## Dependencies and Integration Points
Depends on DRM CRTC lists, AMDGPU CRTC state, ATOMBIOS encoder mode checks, `struct amdgpu_pll`, Linux `gcd`, and integer division helpers. It feeds display mode setting code that programs hardware PLL registers elsewhere.

## Risks and Test Signals
Risks include divider overflow or underflow when requested clocks sit outside PLL ranges, wrong fractional scaling, family-specific ref divider limits, and accidental PLL sharing across incompatible non-DP modes. Test via mode-setting on DP and non-DP connectors, fractional PLL panels, spread-spectrum changes, multi-CRTC clone setups, low/high pixel clocks, and debug KMS divider logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_pll.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_pll.h

## Purpose
Declares the AMDGPU PLL helper API used by display code. It is intentionally small and exposes only divider computation and PPLL sharing queries.

## Important APIs, Types, and Functions
The header declares `amdgpu_pll_compute`, `amdgpu_pll_get_use_mask`, `amdgpu_pll_get_shared_dp_ppll`, and `amdgpu_pll_get_shared_nondp_ppll`. Inputs include `struct amdgpu_device`, `struct amdgpu_pll`, requested frequency, output divider pointers, and `struct drm_crtc`.

## Control Flow
Callers include this header when preparing display mode programming. They compute divider outputs before register programming or query sharing helpers before assigning a PPLL ID to a CRTC.

## State and Persistence Behavior
No state is defined here. It relies on externally owned DRM CRTC and AMDGPU PLL/device structures.

## Dependencies and Integration Points
Requires the including translation unit to know `struct amdgpu_device`, `struct amdgpu_pll`, `struct drm_crtc`, and `u32`. It integrates with ATOMBIOS/display mode-setting code.

## Risks and Test Signals
The API is pointer-output heavy, so callers must pass valid storage for every output. Test signals are compile coverage from display code and runtime mode-setting paths that verify the returned dividers and sharing decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_pll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_pmu.c

## Purpose
Registers AMDGPU hardware performance-monitoring units with Linux perf for ASIC-specific Data Fabric and XGMI events. It exposes sysfs event/format descriptions under perf event sources and wires perf operations to AMDGPU DF counter callbacks.

## Important APIs, Types, and Functions
`struct amdgpu_pmu_event_attribute` describes one sysfs event/format attribute. `struct amdgpu_pmu_entry` tracks a registered PMU for one device/type. Static config tables define Vega20 and Arcturus events, formats, and event config types. Perf callbacks are `amdgpu_perf_event_init`, `amdgpu_perf_add`, `amdgpu_perf_del`, `amdgpu_perf_start`, `amdgpu_perf_stop`, and `amdgpu_perf_read`. Public lifecycle functions are `amdgpu_pmu_init` and `amdgpu_pmu_fini`.

## Control Flow
Initialization selects configs by ASIC. Vega20 registers both a DF-specific PMU and an aggregate `amdgpu_<minor>` PMU; Arcturus registers the aggregate PMU. Each entry allocates format/event attribute arrays, fills sysfs attribute groups, duplicates the group pointer list, registers with `perf_pmu_register`, and appends to a global list. Perf add decodes the config type, reserves a hardware counter via `df.funcs->pmc_start(..., add counter)`, optionally starts, then read/stop/del interact with `pmc_get_count` and `pmc_stop`.

## State and Persistence Behavior
Registered PMUs persist in the global `amdgpu_pmu_list` until device finalization. Counter index, previous count, current count, and config type live in each perf event's `hw_perf_event`. Attribute storage is dynamically allocated per PMU and freed on `amdgpu_pmu_fini`.

## Dependencies and Integration Points
Depends on Linux perf core, sysfs attribute groups, AMDGPU ASIC IDs, DRM minor index naming, and `adev->df.funcs` for hardware counter operations. User integration is via `perf stat -e` and `/sys/bus/event_source/devices/amdgpu*`.

## Risks and Test Signals
Risks include registering events without DF callbacks, leaking partially allocated attributes, event config type mismatches, counter exhaustion, and incorrect count deltas if hardware counters wrap unexpectedly. Test by inspecting sysfs event sources on Vega20/Arcturus, running perf on each event, forcing init failure paths, unloading the driver, and verifying no stale PMU entries remain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_pmu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_pmu.h

## Purpose
Defines the small public interface and event-type encoding for AMDGPU perf PMUs.

## Important APIs, Types, and Functions
`enum amdgpu_pmu_perf_type` distinguishes no PMU, DF-only PMU, and aggregate PMU. `enum amdgpu_pmu_event_config_type` identifies config-encoded event families such as DF and XGMI. `AMDGPU_PMU_EVENT_CONFIG_TYPE_SHIFT` and `AMDGPU_PMU_EVENT_CONFIG_TYPE_MASK` define where the type field lives in `perf_event_attr.config`. Public functions are `amdgpu_pmu_init` and `amdgpu_pmu_fini`.

## Control Flow
PMU implementation code reads these enum values when registering PMUs and when decoding perf event config into `hw_perf_event.config_base`.

## State and Persistence Behavior
No storage is declared here. It defines ABI-like constants used by sysfs event descriptions and perf event parsing.

## Dependencies and Integration Points
Integrated with Linux perf event config encoding, the AMDGPU device lifecycle, and DF/XGMI counter code. Any new event type must be reflected in the enum and the PMU implementation tables.

## Risks and Test Signals
Risks are ABI drift between sysfs event strings and config decoding, especially if the shift/mask changes. Test by reading generated sysfs events and verifying raw perf configs decode to the intended counter family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_preempt_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_preempt_mgr.c

## Purpose
Implements the AMDGPU TTM resource manager for preemptible memory. This manager does not allocate real address ranges; it accounts preemptible BO usage and exposes current usage through sysfs.

## Important APIs, Types, and Functions
`mem_info_preempt_used_show` backs the read-only `mem_info_preempt_used` device attribute. `amdgpu_preempt_mgr_new` allocates a generic `ttm_resource`, initializes it, and sets `start` to `AMDGPU_BO_INVALID_OFFSET`. `amdgpu_preempt_mgr_del` finalizes and frees the resource. Public lifecycle functions are `amdgpu_preempt_mgr_init` and `amdgpu_preempt_mgr_fini`.

## Control Flow
Init sets `man->use_tt`, installs the resource manager function table, initializes the manager with a nominal 1 GiB size, creates the sysfs file, registers it as `AMDGPU_PL_PREEMPT`, and marks it used. Allocation simply accounts a resource; no DRM MM range is assigned. Finalization marks the manager unused, evicts all resources, removes sysfs if available, cleans up, and unregisters the manager.

## State and Persistence Behavior
Runtime usage is tracked by the TTM resource manager and reported via `ttm_resource_manager_usage`. Each resource has an invalid GPU start because preemptible memory is not represented by a stable GPU physical address in this manager.

## Dependencies and Integration Points
Depends on AMDGPU memory manager state, TTM resource manager APIs, sysfs device attributes, and the `AMDGPU_PL_PREEMPT` placement selected by BO placement code for preemptible GTT-like allocations.

## Risks and Test Signals
Risks include treating preemptible resources as addressable memory, failing finalization while resources are still live, or exposing stale sysfs after device removal. Test with preemptible BO creation/destruction, sysfs `mem_info_preempt_used`, eviction paths, driver unload, and BO placement that sets `AMDGPU_GEM_CREATE_PREEMPTIBLE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_preempt_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_psp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_psp.c

## Purpose
Implements the Platform Security Processor IP block for AMDGPU. It selects ASIC-specific PSP function tables, loads PSP and non-PSP firmware, creates and drives the PSP command ring, manages trusted memory regions, initializes and invokes trusted applications, supports RAS/XGMI/HDCP/DTM/RAP/SecureDisplay services, handles suspend/resume/reset, exposes firmware update/dump interfaces, and registers PSP IP block versions.

## Important APIs, Types, and Functions
IP lifecycle is provided through `psp_ip_funcs`: `psp_early_init`, `psp_sw_init`, `psp_sw_fini`, `psp_hw_init`, `psp_hw_fini`, `psp_suspend`, and `psp_resume`. Command transport centers on `psp_cmd_submit_buf`, `acquire_psp_cmd_buf`, `release_psp_cmd_buf`, and `psp_ring_cmd_submit`. Firmware loading uses `psp_init_sos_microcode`, `psp_init_ta_microcode`, `psp_init_cap_microcode`, `psp_execute_ip_fw_load`, `psp_load_non_psp_fw`, `psp_load_fw`, `psp_rlc_autoload_start`, and `amdgpu_psp_get_fw_type`. TA helpers are `psp_ta_load`, `psp_ta_unload`, `psp_ta_invoke`, and `psp_ta_init_shared_buf`.

## Control Flow
Early init maps MP0 IP versions to version-specific PSP ops and feature flags, then requests microcode. Software init allocates command/fence/firmware BOs, checks runtime DB entries, and optionally performs memory training. Hardware init initializes firmware BOs, creates or reuses the PSP ring, runs bootloader stages, updates firmware-reserved VRAM, sets up TMR/VMR, loads SMU and other firmware in the required order, starts RLC autoload, and initializes ASD plus optional TA services. Command submission copies a command into the shared command BO, writes a ring frame, waits for the fence value with timeout/RAS-interrupt handling, records PSP response status, and returns failures in SR-IOV or timeout cases. Suspend/hw_fini terminate TAs, unload TMR, and stop/destroy rings; resume repeats memory training and firmware/TA load.

## State and Persistence Behavior
All PSP state is anchored in `adev->psp`: BOs and GPU addresses for private firmware, command, fence, ring, TMR, TA shared buffers, firmware descriptors, command mutex, fence counter, autoload/TMR feature flags, runtime boot config, memory training cache, TA session IDs/status, and staged flash buffers. Runtime DB and boot config are read from VRAM/PSP firmware interfaces; firmware reservation state is reflected into TTM reserved VRAM ranges. Flash staging buffers persist between sysfs write and read-triggered update.

## Dependencies and Integration Points
Depends on version-specific PSP backends (`psp_v3_1` through `psp_v15_0_8`), firmware request/parsing helpers, AMDGPU BO allocation, TTM VRAM reservation, GMC addressing, RAS, XGMI hive state, SecureDisplay helpers, DRM device enter/exit, sysfs attribute groups, debugfs, runtime PM, and SR-IOV policy. It is central to secure firmware loading for gfx, SDMA, SMU, multimedia, DMUB, VPE, ISP, UMSCH, and related IPs.

## Risks and Test Signals
Risks are high because this file gates boot and recovery: wrong firmware order, stale GPU addresses after XGMI migration, command timeout handling, TMR sizing/alignment, SR-IOV skip policy, optional TA failures that should not hard-fail init, mutex deadlocks around command and TA shared buffers, flash buffer bounds, and sysfs/debugfs exposure of firmware update paths. Test signals include successful firmware load on each MP0 generation, SR-IOV VF reset, suspend/resume, RAS error injection/query, XGMI topology discovery, HDCP/DTM/SecureDisplay enablement, IFWI/USB-C PD update visibility gated by capability flags, SPI ROM debugfs dump serialization, and fallback to direct firmware load on PSP init failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_psp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_psp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_psp.h

## Purpose
Defines the PSP public data model, firmware descriptors, TA contexts, runtime DB structures, command constants, function-table hooks, wrapper macros, IP block declarations, and exported PSP service prototypes.

## Important APIs, Types, and Functions
Important definitions include PSP command/fence buffer sizes, TMR sizing/alignment, mailbox masks, `enum ta_type_id`, `enum psp_bootloader_cmd`, `enum psp_ring_type`, `struct psp_ring`, `enum psp_reg_prog_id`, `struct psp_funcs`, `struct ta_funcs`, `struct psp_bin_desc`, `struct ta_mem_context`, `struct ta_context`, TA-specific contexts for XGMI/RAS/HDCP/DTM/RAP/SecureDisplay, memory-training structures, runtime DB entries, debugfs SPI ROM BO triplets, and the large `struct psp_context`.

## Control Flow
Version backends fill `struct psp_funcs`; generic code calls wrapper macros such as `psp_ring_create`, `psp_bootloader_load_sos`, `psp_mem_training`, `psp_load_usbc_pd_fw`, `psp_update_spirom`, and `psp_get_fw_type`. Public prototypes expose command waiting, firmware loading, reset, TA operations, XGMI/RAS/HDCP/DTM/RAP/SecureDisplay invocation, RLC autoload, register programming, microcode parsing, firmware reservation, partition changes, SQ perfmon config, and debugfs init.

## State and Persistence Behavior
The header documents persistent PSP state in `struct psp_context`: firmware BOs, command/fence BOs, TMR, firmware binary descriptors, loaded firmware handles, TA session contexts, memory training cache, boot config, flash support flags, IFWI staging, and debugfs dump ownership. TA shared memory sizes are fixed by enum and used to allocate host-visible buffers for PSP communication.

## Dependencies and Integration Points
Includes PSP GFX and TA interface headers, AMDGPU core structures, XGMI/RAS/RAP/SecureDisplay protocol types, and exports IP block version objects consumed by device discovery. It forms the contract between generic PSP code and ASIC-specific PSP implementations.

## Risks and Test Signals
Risks include macro wrappers dereferencing missing function pointers, protocol constant mismatch with firmware, TA shared buffer sizing drift, and incompatible runtime DB layout assumptions. Test through build coverage for every PSP generation, firmware-load tests that exercise optional hook absence, TA protocol version checks, and sysfs/debugfs feature visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_psp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_psp_ta.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_psp_ta.c

## Purpose
Provides debugfs interfaces for manually loading, invoking, and unloading PSP trusted applications. In this version, the debugfs path only accepts RAS TA operations.

## Important APIs, Types, and Functions
Debugfs write handlers are `ta_if_load_debugfs_write`, `ta_if_unload_debugfs_write`, and `ta_if_invoke_debugfs_write`. Helpers include `get_bin_version`, `prep_ta_mem_context`, `is_ta_type_valid`, and `set_ta_context_funcs`. `ras_ta_funcs` maps the debugfs generic TA calls to `psp_ras_initialize`, `psp_ras_invoke`, and `psp_ras_terminate`. `amdgpu_ta_if_debugfs_init` creates `ta_if/ta_load`, `ta_if/ta_unload`, and `ta_if/ta_invoke`.

## Control Flow
`ta_load` copies TA type, binary length, and binary payload from userspace, validates the type and one-megabyte limit, selects the RAS context, allocates shared memory if needed, unloads any embedded TA, fills the binary descriptor, initializes the TA, and copies the resulting session ID back to the caller. `ta_unload` reads type and session ID, selects the context, terminates the TA, and frees shared memory. `ta_invoke` reads type, session, command ID, shared buffer length, and payload; validates initialization; copies payload into the TA shared buffer; invokes the TA under the RAS mutex; and copies the shared buffer back.

## State and Persistence Behavior
The debugfs operations mutate `psp->ras_context.context`, `psp->ta_funcs`, session ID, response status, binary descriptor, and TA shared BO/buffer state. Loaded TA binaries copied from userspace are freed after load returns; persistent TA execution uses the PSP-owned session and shared memory.

## Dependencies and Integration Points
Depends on CONFIG_DEBUG_FS, PSP TA helpers from `amdgpu_psp.c`, RAS TA protocol, DRM minor debugfs root, and userspace-supplied binary command buffers. The non-debugfs build compiles a no-op init function.

## Risks and Test Signals
Risks include debugfs ABI misuse, only partial TA type validation on invoke, shared buffer length validation relying on `prep_ta_mem_context`, RAS mutex coupling, and manual TA replacement disrupting normal RAS state. Test with CONFIG_DEBUG_FS on/off builds, malformed writes, oversized TA binary, invalid TA type, unload/reload cycles, RAS command invocation, and concurrent debugfs access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_psp_ta.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_psp_ta.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_psp_ta.h

## Purpose
Declares the debugfs TA interface initializer and provides convenience macros for calling the currently selected TA function table.

## Important APIs, Types, and Functions
Macros `psp_fn_ta_initialize`, `psp_fn_ta_invoke`, and `psp_fn_ta_terminate` dispatch through `psp->ta_funcs`. `amdgpu_ta_if_debugfs_init` is the only function prototype.

## Control Flow
`amdgpu_psp_ta.c` first calls its context-selection helper to set `psp->ta_funcs`, then uses these macros for load/invoke/unload. Callers must not use the macros before selecting a valid function table.

## State and Persistence Behavior
No state is owned by the header. The macros operate on mutable `psp_context.ta_funcs` and the TA contexts owned by `amdgpu_psp.h`.

## Dependencies and Integration Points
Requires `struct psp_context` and `struct ta_funcs` definitions from the PSP header path. Integrated with debugfs-only TA manipulation.

## Risks and Test Signals
The main risk is NULL function-table dereference if a caller skips validation. Test signals are debugfs TA load/invoke/unload coverage and static/build checking for macro use sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_psp_ta.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_rap.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_rap.c

## Purpose
Adds a debugfs test interface for RAP TA L0 policy validation. It lets a privileged user write an opcode to `rap_test` and reports validation success or detailed RAP output through kernel logs.

## Important APIs, Types, and Functions
`amdgpu_rap_debugfs_write` is the write handler. It parses a tiny userspace opcode, powers the device, disables GFX off, invokes `psp_rap_invoke`, decodes `struct ta_rap_shared_memory` output on failure, then restores power/GFX state. `amdgpu_rap_debugfs_init` creates the `rap_test` file only when the RAP TA context is initialized.

## Control Flow
The write path only accepts offset zero and size two, parses the integer opcode, runtime-resumes the DRM device, disables GFX off because RAP cannot handle that state, supports opcode `2` (`TA_CMD_RAP__VALIDATE_L0`), logs success or failure details, then re-enables GFX off and drops runtime PM. Unsupported opcodes are logged but still return the write size after cleanup.

## State and Persistence Behavior
The file does not persist state beyond PSP/RAP shared memory side effects and runtime PM activity. It reads RAP output fields such as last subsection, total validations, valid count, last address, and observed/expected values from the RAP shared buffer.

## Dependencies and Integration Points
Depends on debugfs, runtime PM, GFX off control, RAP TA protocol types, and the PSP RAP invocation path in `amdgpu_psp.c`. It is exposed under the primary DRM minor debugfs root.

## Risks and Test Signals
Risks include strict write-size parsing, power-management imbalance on early errors, RAP invocation while the TA is not initialized, and GFX-off handling around validation. Test by checking `rap_test` visibility only after RAP init, writing valid and invalid opcodes, forcing runtime PM failures, and confirming GFX-off is restored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_rap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_rap.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_rap.h

## Purpose
Declares the RAP debugfs initialization hook for AMDGPU.

## Important APIs, Types, and Functions
The only public declaration is `amdgpu_rap_debugfs_init(struct amdgpu_device *adev)`.

## Control Flow
Debugfs setup code can include this header and call the initializer; the implementation decides whether RAP is initialized enough to expose `rap_test`.

## State and Persistence Behavior
No state is defined here. It depends on `adev->psp.rap_context` managed by PSP code.

## Dependencies and Integration Points
Includes `amdgpu.h` for `struct amdgpu_device` and integrates with DRM debugfs setup plus the PSP RAP TA service.

## Risks and Test Signals
Risk is minimal; the important signal is that builds see the prototype and debugfs creation remains gated in the implementation. Test with RAP-capable and RAP-absent firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_rap.h -->
