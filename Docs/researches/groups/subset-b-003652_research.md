# subset-b-003652 Research

Grouped research for the MSM display MDP5/MDP and DisplayPort source files. Each section is bounded for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_kms.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_kms.c

Purpose: Implements the MDP5 platform/KMS root for Qualcomm MSM display. It binds the `qcom,mdp5`/`qcom,mdss_mdp` platform device, maps registers, acquires clocks and IRQs, initializes runtime PM, builds MDP5 hardware resource objects, and creates DRM modeset objects for planes, CRTCs, encoders, and connectors.

Important APIs/functions: `msm_mdp_register()` and `msm_mdp_unregister()` register the platform driver. `mdp5_dev_probe()` allocates `struct mdp5_kms`, sets interconnect bandwidth, maps `mdp_phys`, fetches mandatory and optional clocks, stores the IRQ, and delegates to `msm_drv_probe()`. `mdp5_kms_init()` is the DRM-facing initializer: it calls `mdp5_init()`, initializes the generic `mdp_kms`, disables bootloader-left interface timing engines, creates the KMS GPU VM, runs `modeset_init()`, and configures DRM mode limits/vblank behavior. `mdp5_hw_init()`, `mdp5_prepare_commit()`, `mdp5_wait_flush()`, and `mdp5_complete_commit()` provide the `msm_kms_funcs` hooks. Global atomic state is exposed through `mdp5_get_existing_global_state()` and `mdp5_get_global_state()`.

Control flow: probe creates a minimally initialized KMS object; DRM component bind later calls `mdp5_kms_init()`. `mdp5_init()` enables runtime PM, reads `REG_MDP5_HW_VERSION`, selects SoC config, initializes optional SMP, CTL manager, hardware pipes, layer mixers, and interfaces. `modeset_init()` initializes connectors/encoders per configured interface, then creates as many CRTCs as there are encoders capped by available mixers, assigning primary/cursor/overlay plane types from the pipe list.

State and persistence: runtime state is in `mdp5_kms`, including clock handles, MMIO base, resource lock, enable count, hardware resource arrays, config handler, CTL manager, SMP pointer, and the DRM private object `glob_state`. `glob_state` is duplicated per atomic transaction and carries pipe, mixer, and SMP allocation state. No disk persistence exists; all state is device-lifetime or atomic-lifetime kernel memory.

Dependencies/integration: depends on DRM core, MSM KMS/DRM private state, MDP5 generated register macros, MDP5 cfg/ctl/irq/crtc/encoder/plane/mixer/pipe/smp modules, HDMI/DSI modeset helpers, runtime PM, interconnect, clocks, IOMMU/GPUVM, and OF platform matching.

Risks and test signals: register accesses require runtime PM and `enable_count > 0`; clock enable/disable imbalance is guarded only by warnings. Interface-to-DSI mapping must match hardware config. `mdp5_flush_commit()` is a TODO, so commit completion relies on CRTC wait paths. Test by boot/probe on each MDP5 SoC, atomic modeset with HDMI/DSI, suspend/resume, hotplug, vblank IRQs, SMP allocation changes, and bootloader-left scanout disable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_kms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_kms.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_kms.h

Purpose: Central private header for MDP5 KMS. It defines the MDP5 device object, global atomic resource state, plane/CRTC/encoder private state, interface descriptors, register access helpers, IRQ mapping helpers, and cross-module prototypes.

Important APIs/types: `struct mdp5_kms` extends `struct mdp_kms` and stores DRM device, platform device, hardware pipe/mixer/interface arrays, config handler, caps, global private object, SMP and CTL managers, MMIO, clocks, resource lock, runtime PM flag, error handler, and enable count. `struct mdp5_global_state` aggregates `mdp5_hw_pipe_state`, `mdp5_hw_mixer_state`, and `mdp5_smp_state` under a DRM private state. `struct mdp5_plane_state` tracks assigned left/right pipes, blend stage, and dirtyfb needs. `struct mdp5_crtc_state` tracks CTL, pipeline, IRQ masks, command mode, and deferred start. `mdp5_write()`/`mdp5_read()` wrap MMIO with an enable-count warning.

Control flow/integration: Other MDP5 modules include this header to share resource ownership contracts. Plane check code writes pipe assignments into `mdp5_global_state`; CRTC code consumes mixer/interface pipeline state; KMS commit hooks prepare/complete SMP state. Inline `intf2vblank()`, `intf2err()`, and `lm2ppdone()` map logical interfaces/mixers to hardware IRQ bits used by CRTC and IRQ code.

State and persistence: The header describes volatile kernel objects only. Atomic state clones are the persistence boundary across check/commit phases. The `resource_lock` protects shared registers such as `REG_MDP5_DISP_INTF_SEL`.

Dependencies: Pulls in MSM DRM/KMS, generic MDP definitions, MDP5 cfg, generated `mdp5.xml.h`, pipe/mixer/ctl/smp headers, and optional DSI command encoder declarations gated by `CONFIG_DRM_MSM_DSI`.

Risks and test signals: Header-level risks are ABI coupling between modules and assumptions about array sizes such as `SSPP_MAX`, 8 mixers, and 5 interfaces. The register helpers warn but do not prevent unclocked access. Validate by building all MDP5 configurations, running atomic state debug printing, exercising DSI command mode vblank mapping, writeback mapping, and source split paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_kms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_mixer.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_mixer.c

Purpose: Provides atomic allocation and release of MDP5 layer mixers (LMs), including source-split right-mixer pairing, plus construction of `struct mdp5_hw_mixer` instances from SoC config.

Important APIs/functions: `mdp5_mixer_assign()` selects a mixer for a CRTC according to required caps and current global atomic assignment state. Optional `r_mixer` requests source-split pairing, using `get_right_pair_idx()` and the hard-coded pair map LM0->LM1 and LM2->LM5. `mdp5_mixer_release()` clears a mixer-to-CRTC assignment in the duplicated global state. `mdp5_mixer_init()` fills immutable hardware metadata such as LM id, caps, ping-pong id, DSPP id, name, and CTL flush mask.

Control flow: CRTC atomic check obtains `mdp5_global_state` with locking, then asks this module to assign one or two mixers. The assign loop skips mixers owned by other CRTCs, skips mixers lacking requested caps, and prefers pair-capable mixers so later source-split transitions can avoid a full modeset when possible. Release validates that the mixer is currently assigned before clearing it.

State and persistence: Assignment is stored in `global_state->hwmixer.hwmixer_to_crtc[]`, not directly in hardware. Hardware identity is devm-allocated for device lifetime. No persistent storage exists.

Dependencies/integration: Depends on `mdp5_kms`, SoC `mdp5_lm_instance` config, DRM atomic state, CRTC objects, and CTL flush mask helpers. CRTC pipeline setup consumes the assigned mixers.

Risks and test signals: Pairing is hard-coded and assumes known MDP5 source-split combinations. Returning `-EINVAL` for missing pair capability can fail otherwise usable single-mixer modes if caller requested a right mixer. Test with multiple CRTCs, source-split wide modes, mixer release/reassign sequences, and atomic check rollback after failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_mixer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_mixer.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_mixer.h

Purpose: Declares MDP5 layer mixer objects and their atomic allocation state.

Important APIs/types: `struct mdp5_hw_mixer` records array index, name, LM hardware id, capability bits, ping-pong id, DSPP id, and flush mask. `struct mdp5_hw_mixer_state` maps up to 8 mixer indices to owning DRM CRTCs. Public functions are `mdp5_mixer_init()`, `mdp5_mixer_assign()`, and `mdp5_mixer_release()`.

Control flow/state: The state struct is embedded in `mdp5_global_state`, so mixer allocation participates in DRM atomic duplicate/check/commit flow. Hardware mixer metadata is immutable once initialized from SoC config.

Dependencies/integration: Used by MDP5 KMS initialization and CRTC/pipeline allocation. The flush mask integrates with CTL commit programming.

Risks and test signals: The fixed 8-entry assignment array must cover all configured LMs. Tests should compile all cfg variants and exercise atomic debug state for mixer ownership during source split and CRTC disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_mixer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_pipe.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_pipe.c

Purpose: Provides atomic allocation/release of MDP5 source pipes (SSPPs) to DRM planes and constructs pipe descriptors from SoC config.

Important APIs/functions: `mdp5_pipe_assign()` selects a pipe matching required caps and optional right-pipe source-split needs. It checks both new and old global pipe state to avoid immediate reuse of pipes still scanning out or still owning non-double-buffered SMP allocations. It also handles SMP block assignment through `mdp5_smp_assign()`. `mdp5_pipe_release()` releases global pipe ownership and SMP blocks. `mdp5_pipe_init()` creates immutable pipe metadata and CTL flush mask.

Control flow: Plane atomic check computes required caps from format, scale, rotation, cursor type, and source split. If reallocation is needed, it asks `mdp5_pipe_assign()` for a left pipe and optionally a right pipe. Candidate selection rejects pipes already in old/new state, caps mismatches, cursor-pipe misuse, and for source split, mismatched right-pipe type/order. After successful assignment, old pipes are released in the same duplicated atomic state.

State and persistence: Ownership lives in `global_state->hwpipe.hwpipe_to_plane[]`; per-pipe immutable metadata includes `pipe`, `reg_offset`, `caps`, `flush_mask`, and the last SMP `blkcfg`. No disk persistence exists.

Dependencies/integration: Tied to MDP5 KMS global atomic state, plane check/update, SMP allocator, DRM plane types, and CTL flush masks.

Risks and test signals: Reuse avoidance can transiently consume more pipes and cause `-ENOMEM` during complex updates. Right-pipe selection does not explicitly check old/new ownership for the right candidate in the visible loop, so source-split behavior needs careful regression coverage. Test cursor versus overlay pipe selection, YUV/scale caps, SMP allocation changes, disabling planes, and wide source split.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_pipe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_pipe.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_pipe.h

Purpose: Declares MDP5 source pipe descriptors and global pipe assignment state.

Important APIs/types: `SSPP_MAX` is defined as `SSPP_CURSOR1 + 1`. `struct mdp5_hw_pipe` stores index, name, enum pipe id, register offset, capability bits, CTL flush mask, and SMP block configuration. `struct mdp5_hw_pipe_state` maps pipe indices to owning DRM planes. Public functions are `mdp5_pipe_assign()`, `mdp5_pipe_release()`, and `mdp5_pipe_init()`.

Control flow/state: The state struct is part of `mdp5_global_state`, letting pipe ownership be changed transactionally in atomic check and committed only after the DRM atomic swap succeeds.

Dependencies/integration: Used by MDP5 KMS construction, plane atomic check/update, SMP state, and CTL flush programming.

Risks and test signals: The `SSPP_MAX` dependency on generated enum ordering must remain valid. `blkcfg` is cached in the pipe object and must track the active allocation. Compile all MDP5 cfgs and test plane allocation for each pipe class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_pipe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_plane.c

Purpose: Implements DRM plane support for MDP5, including plane properties, atomic state allocation/printing, framebuffer preparation, atomic validation, async cursor/position updates, hardware pipe programming, scaling, pixel extension, CSC, source addresses, supported formats, and plane construction.

Important APIs/functions: `mdp5_plane_init()` creates DRM planes with MDP5 formats and helper callbacks. `mdp5_plane_atomic_check_with_state()` validates source bounds, scale limits, source split, caps, SMP block needs, and pipe allocation/release. `mdp5_plane_atomic_update()` and `mdp5_plane_atomic_async_update()` program active planes. `mdp5_plane_mode_set()` converts DRM source/destination rectangles to hardware fields, splits wide planes across two pipes, calculates scaling steps and pixel extension, and calls `mdp5_hwpipe_mode_set()`. `mdp5_plane_pipe()`, `mdp5_plane_right_pipe()`, and `mdp5_plane_get_flush()` expose committed pipe ids and flush masks.

Control flow: Atomic check computes max LM dimensions from config, accepts up to 2x max width only when source split is supported, invokes `drm_atomic_helper_check_plane_state()`, derives needed pipe caps from YUV, scaling, rotation, and cursor type, recalculates SMP `blkcfg`, then assigns/release pipes in global state. Atomic update assumes check succeeded and writes registers. Async update is restricted to same CRTC, same FB, same dimensions, unchanged visibility, and already allocated pipe; it updates position registers, commits only the plane flush mask, then swaps private plane state.

State and persistence: `struct mdp5_plane_state` carries assigned left/right pipes, blend stage, and dirtyfb needs across atomic states. Hardware register state is programmed in source pipe registers and committed via CTL flush. Framebuffer mappings are prepared/cleaned through MSM framebuffer helpers.

Dependencies/integration: Uses DRM atomic/helpers, damage clips, GEM prepare helper, MDP5 pipe/SMP/KMS/CRTC/CTL interfaces, MSM framebuffer format/IOVA helpers, default CSC tables, and generated register macros.

Risks and test signals: Scaling math uses fixed hardware limits and can overflow or reject edge cases. Source split assumes equal half-width programming. YUV always enables scale path for chroma upsampling. Async update manually copies private state and temporarily preserves old FB, so refcount and visibility regressions are important. Test RGB/YUV, all rotations/reflections, scaling up/down, cursor async movement, source split, SMP exhaustion, command-mode dirtyfb, and format rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_smp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_smp.c

Purpose: Implements MDP5 Shared Memory Pool allocation and hardware programming for source pipe fetch buffering.

Important APIs/functions: `mdp5_smp_init()` creates the SMP handler from cfg block count/size and seeds reserved MMB state. `mdp5_smp_calculate()` computes per-plane block counts encoded into `blkcfg`. `mdp5_smp_assign()` allocates blocks per SMP client for a pipe. `mdp5_smp_release()` removes a pipe's client allocations from global state. `mdp5_smp_prepare_commit()` writes newly assigned blocks and FIFO thresholds before scanout uses them. `mdp5_smp_complete_commit()` clears FIFO thresholds for released pipes after scanout completion. `mdp5_smp_dump()` prints allocation state for atomic debug.

Control flow: Plane check computes `blkcfg` and pipe assignment calls `mdp5_smp_assign()`. Assign walks pipe clients, allocates blocks from the duplicated global state, and marks the pipe in `assigned`. Release clears per-client bitmaps and marks the pipe in `released`. KMS commit hooks call prepare before flush/wait and complete after commit completion to respect non-double-buffered SMP allocation registers.

State and persistence: `struct mdp5_smp` stores device lifetime config, reserved blocks, block geometry, and register-cache arrays for allocation/FIFO registers. `struct mdp5_smp_state` stores global and per-client bitmaps plus assigned/released masks in atomic private state.

Dependencies/integration: Depends on DRM formats for plane count/subsampling, MDP5 cfg client ids, KMS global state, pipe client counts, and MDP5 register macros.

Risks and test signals: SMP registers are not double buffered, so early release can corrupt active scanout. `smp_request_block()` assumes client bitmaps are empty on assign. Reserved blocks reduce requested count. Test format width changes, YUV plane counts, SMP exhaustion, atomic test-only rollback, plane disable/enable on separate CRTCs, and debug dump consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_smp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_smp.h

Purpose: Documents and declares the MDP5 Shared Memory Pool API and its atomic state model.

Important APIs/types: `struct mdp5_smp_state` contains a global block bitmap, per-client bitmaps, and bitmasks of assigned and released pipes. Public functions initialize the SMP, calculate required blocks, assign/release blocks, dump state, and prepare/complete commit hardware updates.

Control flow/state: The header explicitly describes the two-step update contract: prepare commit writes new assignments before pipes use them; complete commit clears released clients after old scanout is done. The state is embedded in `mdp5_global_state`.

Dependencies/integration: Depends on DRM printing and MSM/MDP5 generated SMP types. Plane allocation and KMS commit hooks are the primary callers.

Risks and test signals: The API relies on callers respecting the prepare/complete split. Tests should check atomic rollback, debug printing, and plane reallocation where old and new SMP allocations overlap in time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_smp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp_format.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp_format.c

Purpose: Defines MSM/MDP pixel format metadata and default color-space conversion tables used by MDP5 and related display blocks.

Important APIs/functions: `mdp_get_format()` maps a DRM fourcc plus modifier to a `struct msm_format`, selecting the linear table for modifier 0 or the UBWC table for `DRM_FORMAT_MOD_QCOM_COMPRESSED`. `mdp_get_default_csc_cfg()` returns default `struct csc_cfg` entries for RGB/RGB, YUV/RGB, RGB/YUV, and YUV/YUV. Macro families define packed RGB/RGBA/RGBX, DX 10-bit variants, interleaved YUV, pseudo-planar YUV, planar YUV, and UBWC/tiled variants.

Control flow: Callers ask for a format at framebuffer validation/programming time. The lookup rejects unknown modifiers and unsupported fourccs with DRM errors. Plane programming consumes fields such as fetch type, bits per component, unpack order/count, bpp, chroma sample, fetch mode, flags, plane count, and tile height.

State and persistence: The format and CSC tables are static const/static global data. Returned pointers are immutable shared metadata, except CSC table returns non-const pointer to static entries.

Dependencies/integration: Depends on DRM fourcc/modifier definitions, DRM framebuffer info, MSM driver logging, generic MDP register enums, and the `mdp_kms.h` CSC type definitions.

Risks and test signals: UBWC aliases intentionally map some ARGB/XRGB formats to hardware-native ABGR/ARGB ordering, so format/modifier validation must match hardware expectations. Unsupported modifiers fail hard. Test framebuffer creation for all advertised formats, UBWC scanout, YUV CSC, P010/DX formats, and error messages for invalid fourcc/modifier pairs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp_format.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp_format.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp_format.h

Purpose: Declares the MSM display format metadata structure and helper flags/macros used by MDP and DPU plane programming.

Important APIs/types: `enum msm_format_flags` defines YUV, DX, compressed, tight unpack, and MSB-aligned unpack bits. `struct msm_format` describes DRM fourcc, component bit widths, element order, fetch type, chroma sampling, alpha presence, unpack count, bytes per pixel, flags, number of planes including metadata, fetch mode, and tile height. Macros classify YUV, DX, linear, tile, and UBWC formats.

Control flow/state: This is a pure metadata contract. Runtime callers receive `struct msm_format` from lookup code and branch on macros during validation and hardware programming.

Dependencies/integration: Depends on generated `mdp_common.xml.h` enums and is included by `mdp_kms.h`, MDP5 plane code, and other MSM display blocks.

Risks and test signals: Misclassified compressed or plane-count fields can cause incorrect framebuffer IOVA programming. Compile coverage and framebuffer validation tests should include linear RGB, YUV, UBWC RGB/YUV, and DX/P010 formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp_format.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp_kms.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp_kms.c

Purpose: Implements generic MDP IRQ registration, dispatch, mask aggregation, vblank mask updates, and short IRQ wait helper shared by MDP generations.

Important APIs/functions: `mdp_irq_register()` and `mdp_irq_unregister()` add/remove transient `struct mdp_irq` handlers. `mdp_dispatch_irqs()` walks registered handlers matching the IRQ status and invokes callbacks outside the list lock. `mdp_update_vblank_mask()` toggles userspace vblank IRQ bits. `mdp_irq_update()` recomputes the hardware IRQ mask. `mdp_irq_wait()` registers a temporary handler and waits up to 100 ms for a mask.

Control flow: The module keeps a global `list_lock` and wait queue. `update_irq()` ORs the vblank mask with all registered handler masks and calls the generation-specific `set_irqmask()` hook with old/new masks. Dispatch marks `in_irq` to defer immediate hardware mask updates while callbacks may register/unregister handlers, then recomputes the mask after the pass.

State and persistence: Per-KMS IRQ state lives in `struct mdp_kms`: handler list, current mask, vblank mask, and `in_irq`. The wait helper uses stack state and a global wait queue. No persistent storage exists.

Dependencies/integration: Used by MDP4/MDP5 IRQ code, CRTC vblank/commit wait paths, and CTL/encoder housekeeping. Requires `mdp_kms_funcs->set_irqmask`.

Risks and test signals: The lock is global, so multiple MDP devices would serialize and share the wait queue. Callback invocation outside the lock requires handler lifetime to be valid until unregister completes. `mdp_irq_wait()` has a fixed timeout and does not return status. Test vblank enable/disable, nested register/unregister from IRQ handlers, commit-done waits, and IRQ mask transitions under concurrent CRTCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp_kms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp_kms.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp_kms.h

Purpose: Defines the generic MDP KMS wrapper, IRQ helper structures, display capability bits, pipe/mixer capability bits, and CSC types used across MDP generations.

Important APIs/types: `struct mdp_kms_funcs` extends `msm_kms_funcs` with `set_irqmask`. `struct mdp_kms` embeds `msm_kms` and tracks IRQ handler list, vblank mask, current mask, and IRQ dispatch state. `struct mdp_irq` describes transient IRQ callbacks. Capability defines cover SMP, DSC, CDM, source split, pipe flip/scale/CSC/decimation/pixel-extension/cursor, and layer mixer display/writeback/pair support. `struct csc_cfg` stores matrix, bias, and clamp values.

Control flow/state: `mdp_kms_init()` initializes function pointers and the IRQ list, then delegates to `msm_kms_init()`. `mdp_kms_destroy()` delegates to `msm_kms_destroy()`. Other functions are implemented in `mdp_kms.c`.

Dependencies/integration: Includes Linux clock/platform/regulator headers, MDP format metadata, MSM driver/KMS headers, and generated common MDP enums. MDP5 cfg, pipe, mixer, and plane modules consume the capability bits.

Risks and test signals: This header is a cross-generation contract; changing capability bit values or CSC layout affects multiple drivers. Test by building MDP4, MDP5, and DPU users and by exercising YUV/CSC and IRQ paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp_kms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/msm_disp_snapshot.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/msm_disp_snapshot.c

Purpose: Provides asynchronous display devcoredump capture infrastructure for MSM KMS failures.

Important APIs/functions: `msm_disp_snapshot_init()` initializes `kms->dump_mutex`, creates a kthread worker named `disp_snapshot`, and initializes work. `msm_disp_snapshot_state()` queues snapshot work for a DRM device. `msm_disp_snapshot_state_sync()` allocates `struct msm_disp_state`, initializes it, and captures state while caller holds `dump_mutex`. `_msm_disp_snapshot_work()` serializes capture, optionally prints to console, and publishes the dump through `dev_coredumpm()`. `msm_disp_snapshot_destroy()` tears down the worker and mutex.

Control flow: Fault or debug callers queue `dump_work`. The worker locks `dump_mutex`, captures state through utility code, unlocks, and hands ownership to devcoredump with `disp_devcoredump_read()` and `msm_disp_state_free()` callbacks. The read callback prints the captured state through a DRM coredump printer.

State and persistence: Captured state is an allocated `struct msm_disp_state` containing register blocks and duplicated atomic state. It persists only until devcoredump consumption or replacement. Worker/mutex state lives in `struct msm_kms`.

Dependencies/integration: Depends on DRM printer/coredump helpers, Linux kthread workers, devcoredump, MSM KMS dump fields, and snapshot utility functions.

Risks and test signals: `msm_disp_snapshot_init()` logs worker creation failure but still returns 0, so later queueing must tolerate error pointers/null. The sync function warns if mutex is not held. Test manual snapshot trigger, devcoredump read/free, repeated dumps while one is pending, worker destruction during driver removal, and builds with coredump disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/msm_disp_snapshot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/msm_disp_snapshot.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/msm_disp_snapshot.h

Purpose: Declares MSM display snapshot data structures and capture/print/free APIs.

Important APIs/types: `struct msm_disp_state` stores device pointers, a list of register blocks, duplicated DRM atomic state, and capture time. `struct msm_disp_state_block` stores a named register block, size, copied register state, and base address. APIs initialize/destroy snapshot support, trigger async capture, capture synchronously under `dump_mutex`, print, capture register/atomic state, free dumps, and add named register blocks. Constants define max blocks, console dump switch, and register dump alignment.

Control flow/state: KMS/DP/DSI/DPU snapshot providers call `msm_disp_snapshot_add_block()` during capture; print/free iterate the block list. `msm_disp_snapshot_state_sync()` is the synchronous entry for the worker.

Dependencies/integration: Includes DRM atomic/device/print internals, Linux debugfs/list/kthread/devcoredump/PM headers, and MSM KMS definitions. The relative include of `drm_crtc_internal.h` couples it to DRM internals.

Risks and test signals: The header exposes DRM-internal dependencies and a fixed name buffer size. Test builds across kernel DRM internal changes and capture of multiple register blocks with long formatted names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/msm_disp_snapshot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/msm_disp_snapshot_util.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/msm_disp_snapshot_util.c

Purpose: Implements display snapshot register capture, printing, atomic-state duplication, and memory cleanup.

Important APIs/functions: `msm_disp_snapshot_add_block()` allocates a block, formats its name, aligns length, dumps registers, and appends it. `msm_disp_snapshot_capture_state()` invokes DP, DSI, and KMS-specific snapshot callbacks, then duplicates DRM atomic state. `msm_disp_state_print()` prints metadata, each block, and the DRM atomic state. `msm_disp_state_free()` releases duplicated atomic state, register dumps, block nodes, and the state object.

Control flow: Register dump allocates a padded u32 buffer and reads four registers per 16-byte row with relaxed reads, zero-filling out-of-range columns. Atomic capture records real time, locks all modeset locks with backoff, duplicates state, then drops locks. Capture order is DP blocks, DSI blocks, KMS snapshot callback, atomic state.

State and persistence: Captured register data is an owned copy detached from MMIO after capture. Atomic state is reference-counted through DRM. All allocations are freed by the devcoredump free callback.

Dependencies/integration: Depends on generated kernel release string, DRM atomic helpers/printers, MSM DP/DSI/KMS snapshot callbacks, MMIO read helpers, kvzalloc/kvfree, and Linux list management.

Risks and test signals: `num_rows = len / REG_DUMP_ALIGN` while allocation uses `aligned_len * REG_DUMP_ALIGN`; this code treats `aligned_len` as byte length after callers pass raw lengths and alignment. Snapshot capture can be expensive under modeset locks. Test odd register lengths, missing allocation handling, DP+DSI mixed devices, atomic duplication during hotplug, and devcoredump free after partial capture failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/msm_disp_snapshot_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_audio.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_audio.c

Purpose: Implements DisplayPort audio register programming and HDMI-codec bridge callbacks for the MSM DP driver.

Important APIs/functions: `msm_dp_audio_get()` allocates `struct msm_dp_audio_private` and returns the public `struct msm_dp_audio`. `msm_dp_audio_prepare()` validates that DP display power is on, stores channel count, programs audio SDPs, ACR, safe-to-exit level, enables audio, signals audio start, and marks audio enabled. `msm_dp_audio_shutdown()` disables audio only if it was enabled and signals completion so display clocks can be shut down. Helper functions program stream, timestamp, infoframe, copy-management, and ISRC SDP headers, ACR link-rate selection, mainlink safe-to-exit level, and `MMSS_DP_AUDIO_CFG`.

Control flow: HDMI-codec calls prepare after bridge/display setup. The code relies on `msm_dp_display->power_on` to avoid unclocked register access and on `audio_enabled` to guard shutdown after disconnect. SDP headers are packed through `msm_dp_utils_pack_sdp_header()` and written to link registers before enabling audio.

State and persistence: Public state stores lane count and bandwidth code for the current link. Private state stores pdev, DRM dev pointer, link base, channel count, and embedded public object. State is device-managed and not persistent.

Dependencies/integration: Depends on DP display bridge conversion, DP panel/reg/utils headers, DRM DP helper definitions, HDMI codec params, and link register MMIO. Display code supplies lane count/bw code and handles audio start/complete signals.

Risks and test signals: `drm_dev` is present but not set in `msm_dp_audio_get()`, so debug logging using it must tolerate null. ACR selection defaults on unknown link rate. Shutdown depends on `audio_enabled`, not connector status. Test audio prepare before connect, normal playback, disconnect while audio active, all link rates/lane counts, and repeated prepare/shutdown cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_audio.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_audio.h

Purpose: Declares the public DP audio object and HDMI-codec callbacks.

Important APIs/types: `struct msm_dp_audio` stores current lane count and bandwidth code. `msm_dp_audio_get()`/`msm_dp_audio_put()` manage allocation. `msm_dp_audio_prepare()` and `msm_dp_audio_shutdown()` are bridge/codec callbacks for enabling and disabling audio.

Control flow/state: Display code owns the returned object, updates link fields as modes are configured, and exposes prepare/shutdown to the audio codec path.

Dependencies/integration: Includes platform device and HDMI codec headers, forward-declares `drm_bridge`, and integrates with DP display bridge code.

Risks and test signals: Public state is minimal and assumes the caller updates link parameters before prepare. Build and runtime tests should cover HDMI-codec integration and hot unplug during audio.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_audio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_aux.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_aux.c

Purpose: Implements the MSM DP AUX adapter, including AUX/I2C-over-AUX transfers, HPD control, IRQ completion, runtime PM, EDID segment workarounds, and PHY recalibration/reset handling.

Important APIs/functions: `msm_dp_aux_get()` allocates and initializes a `drm_dp_aux` adapter with transfer and HPD wait callbacks. `msm_dp_aux_transfer()` is the DRM AUX transfer implementation. `msm_dp_aux_isr()` decodes AUX IRQ bits, records error status, clears hardware interrupts when needed, and completes waiting transfers. `msm_dp_aux_init()`/`deinit()` enable/disable AUX hardware. `msm_dp_aux_enable_xfers()` gates external DP transfers when disconnected. HPD APIs enable/disable HPD, HPD IRQs, read/ack HPD status, and report link-connected state.

Control flow: Transfer resumes the device with runtime PM, locks the AUX mutex, rejects uninitialized or disconnected external-DP transactions, tracks EDID segment/offset writes, sends helper segment/offset transactions for non-compliant sinks, programs the command FIFO, waits up to 250 ms for completion, decodes error status into DP replies or errno, and resets/recalibrates on failures. FIFO TX writes address/size/data into `REG_DP_AUX_DATA` then starts `REG_DP_AUX_TRANS_CTRL`; FIFO RX clears GO and reads indexed data bytes.

State and persistence: Private state tracks mutex/completion, last error, retry count, command busy flag, request type, no-send flags, init/connect gates, EDID offset/segment, eDP mode, PHY pointer, and MMIO base. All state is device-lifetime volatile memory.

Dependencies/integration: Depends on DRM DP AUX helpers, runtime PM, PHY API, HPD/AUX register macros, and callers in DP display/link/panel code. IRQ dispatch comes through `msm_dp_ctrl_isr()`.

Risks and test signals: `aux->native` and read detection use bitwise expressions that depend on request bit layout. EDID workaround mutates offset/segment across transactions. Unexpected IRQs when not busy are ignored. Test DPCD native reads/writes, EDID reads beyond two blocks, disconnect gating, eDP always-on AUX, timeout/reset path, HPD IRQ masking, repeated native failures triggering `phy_calibrate()`, and AUX char device access while unplugged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_aux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_aux.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_aux.h

Purpose: Declares the MSM DP AUX adapter API.

Important APIs/types: Public functions register/unregister the DRM AUX adapter, service AUX IRQs, enable/disable transfers, initialize/deinitialize/reconfigure hardware, manage HPD and HPD IRQs, read HPD status/link state, and allocate/free the AUX adapter with device, PHY, eDP flag, and MMIO base.

Control flow/state: DP display/control code owns the returned `drm_dp_aux` and calls init/deinit around power state, `enable_xfers()` around external HPD connect state, and `msm_dp_aux_isr()` from the controller IRQ handler.

Dependencies/integration: Includes DRM DP helper and forward-declares PHY. It is included by `dp_ctrl.h` and other DP modules.

Risks and test signals: API users must not call transfer paths before `msm_dp_aux_init()` and must gate external-DP transfers on connection. Test registration ordering, eDP panel probing before full DRM AUX registration, and HPD enable/disable sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_aux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_ctrl.c

Purpose: Implements the MSM DP controller core: reset, IRQ masking/dispatch, AUX interrupt handoff, mainlink enable/disable, link training, transfer unit calculation, MSA/source timing setup, PHY pattern compliance handling, PSR control, clock/OPP management, and stream/link power sequencing.

Important APIs/functions: Public entry points include `msm_dp_ctrl_get()`, `msm_dp_ctrl_reset()`, `msm_dp_ctrl_core_clk_enable()`/`disable()`, `msm_dp_ctrl_phy_init()`/`exit()`, `msm_dp_ctrl_on_link()`, `msm_dp_ctrl_on_stream()`, `msm_dp_ctrl_off_link_stream()`, `msm_dp_ctrl_off_link()`, `msm_dp_ctrl_off()`, `msm_dp_ctrl_isr()`, `msm_dp_ctrl_handle_sink_request()`, `msm_dp_ctrl_config_psr()`, and `msm_dp_ctrl_set_psr()`. Core private state is `struct msm_dp_ctrl_private`, which embeds the public object and stores panel/link/AUX/PHY pointers, AHB/link MMIO bases, clock handles, PHY opts, completions, hardware revision, and clock-on booleans.

Control flow: `msm_dp_ctrl_on_link()` enables core clocks, chooses link rate/lane count from panel or compliance request, powers/configures PHY and link clocks, then repeatedly calls mainlink setup and link training. Training configures sink lane/rate DPCD, downspread/channel coding/ASSR, trains LTTPRs from farthest to nearest, then trains DPRX. Failures downshift link rate or lane count, reinitialize mainlink clocks/PHY, and retry. `msm_dp_ctrl_on_stream()` ensures link clocks, sets/enables pixel clock, optionally retrains, clears training pattern, programs source params/MSA/TU, sends video, and waits for video-ready completion plus mainlink-ready polling. Off paths disable VSC SDP, mainlink, pixel/link clocks, OPP rate, and PHY with variants for full link+stream or link only.

State and persistence: Clock booleans prevent duplicate enables but are not reference counts. Link parameters and PHY voltage/pre-emphasis are updated in `struct msm_dp_link`. Completions (`idle_comp`, `psr_op_comp`, `video_comp`) synchronize IRQ-driven operations. `hw_revision` is cached after reset. No state persists beyond device lifetime.

Dependencies/integration: Depends on DRM DP helper DPCD/training utilities, DP panel/link/AUX modules, Linux PHY/OPP/clock APIs, fixed-point/rational math, generated DP register macros, and DRM logging. AUX IRQs are delegated to `msm_dp_aux_isr()`, panel timing and VSC/DSC helpers program stream details, and link helpers translate colorimetry/test depths and sink requests.

Risks and test signals: Link training contains many hardware timing assumptions, retry/downshift branches, and LTTPR paths. TU calculation is complex fixed-point code with DSC/FEC scaffolding but current inputs set DSC/FEC off. Pixel clock is halved for wide bus or YUV420; MSA uses the original pixel rate. `msm_dp_ctrl_irq_phy_exit()` is declared in the header but not implemented in this file. Test hotplug, link training across RBR/HBR/HBR2/HBR3 and 1/2/4 lanes, LTTPR, YUV420, wide bus, PSR entry/exit, idle pattern completion, video-ready IRQ timeout, sink compliance PHY patterns, link-status-updated maintenance, suspend/resume clock sequencing, and failure cleanup after training errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_ctrl.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_ctrl.h

Purpose: Declares the public MSM DP controller interface used by DP display, bridge, IRQ, panel, and link code.

Important APIs/types: `struct msm_dp_ctrl` currently exposes `wide_bus_en`. Public functions cover link/stream power on/off, idle push, IRQ handling, sink request handling, allocation, reset, PHY init/exit, PSR config/set, core clock enable/disable, and IRQ mask enable/disable. The header also declares `msm_dp_ctrl_irq_phy_exit()`.

Control flow/state: Display code obtains a controller with `msm_dp_ctrl_get()`, initializes PHY/clocks around connector state, calls `on_link()` before stream, `on_stream()` to send video, and matching off calls during disable/disconnect. IRQ code calls `msm_dp_ctrl_isr()`.

Dependencies/integration: Includes DP AUX, panel, and link headers and forward-declares PHY. The single public field `wide_bus_en` is consumed by timing setup and pixel-clock decisions.

Risks and test signals: `msm_dp_ctrl_irq_phy_exit()` lacks a visible implementation in the researched source, so link errors or external users may hit a missing symbol depending on build scope. Test full DP display enable/disable and compile/link coverage for all declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_ctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_debug.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_debug.c

Purpose: Provides optional debugfs files for MSM DP runtime state and compliance test controls when `CONFIG_DEBUG_FS` is enabled.

Important APIs/functions: `msm_dp_debug_init()` allocates private debug state and creates `dp_debug`; for non-eDP it also creates `dp_test_active`, `dp_test_data`, and `dp_test_type`. `msm_dp_debug_show()` reports link capabilities, mode timings, bpp, sink request, lane count/rate, link clock, and PHY levels. `msm_dp_test_data_show()` reports requested compliance video dimensions and bpc. `msm_dp_test_type_show()` reports video pattern type. `msm_dp_test_active_write()` toggles `panel->video_test`, accepting only value `1` as active.

Control flow: Debugfs read callbacks dereference live panel/link/connector state and print through seq_file. The active write copies user input with `memdup_user_nul()`, parses decimal, and changes test state only when connector is connected. eDP skips compliance files.

State and persistence: Private debug object stores pointers to link, panel, and connector. `panel->video_test` is mutable runtime state; debugfs files do not persist.

Dependencies/integration: Depends on debugfs, DRM connector/file helpers, DP AUX/CTRL/display/link/panel structures, and DRM DP helper conversions.

Risks and test signals: Debug state stores raw pointers and assumes connector/panel/link lifetimes exceed debugfs files. The files are created with mode `0444`, but `dp_test_active` has a write handler, making write availability depend on debugfs permission behavior. Test debugfs reads while connected/disconnected, compliance toggling, eDP path, connector removal, and builds with debugfs disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_debug.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_debug.h

Purpose: Declares the optional DP debugfs initialization API and provides a stub when debugfs is disabled.

Important APIs/types: `msm_dp_debug_init()` accepts device, panel, link, connector, debugfs root, and eDP flag. Under `CONFIG_DEBUG_FS` it is implemented by `dp_debug.c`; otherwise the static inline stub returns `-EINVAL`.

Control flow/state: DP display setup calls this during connector/debugfs initialization. The eDP flag controls whether compliance test files are created.

Dependencies/integration: Includes DP panel and link headers and forward declarations through those includes. Uses DRM connector and debugfs types in the function signature.

Risks and test signals: Callers must tolerate `-EINVAL` when debugfs is disabled. Build-test both debugfs-enabled and disabled configurations and confirm no required runtime path depends on debugfs success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_debug.h -->
