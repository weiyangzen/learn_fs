# subset-b-003762 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_packet.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_packet.h

Purpose: Defines the VC4/V3D command-list packet opcodes, packet byte sizes, render/binning bit fields, texture descriptor fields, tiling identifiers, and texture data type enum used by the VC4 render and validation code. It is a hardware ABI header inside the driver: no executable code, but many safety checks and command emitters depend on these constants matching hardware.

Important APIs/types/functions: `enum vc4_packet` names hardware packets plus the driver-only `VC4_PACKET_GEM_HANDLES` relocation pseudo-packet. `VC4_PACKET_*_SIZE` constants feed command-list length accounting in `vc4_validate.c` and RCL allocation in `vc4_render_cl.c`. The `VC4_LOADSTORE_*`, `VC4_RENDER_CONFIG_*`, `VC4_BIN_CONFIG_*`, `VC4_TEX_P*_*`, and `enum vc4_texture_data_type` definitions describe the packed fields later accessed through `VC4_GET_FIELD()` and `VC4_SET_FIELD()`.

Control flow: None locally. The header shapes control flow elsewhere by defining packet dispatch indexes in `cmd_info[]`, RCL packet emission order, and texture relocation decoding.

State and persistence: No runtime state. The values are persistent driver/hardware ABI constants; changing them affects submitted command streams, render target validation, and texture bounds checks.

Dependencies and integration points: Includes `vc4_regs.h` for bit helpers. Used by `vc4_validate.c` to whitelist and relocate bin CL packets, by `vc4_render_cl.c` to synthesize render CL packets, and by shader/texture validation to interpret uniforms. It also indirectly couples to userspace UAPI structs whose `bits` fields are expected to contain these encodings.

Risks: A bad size constant can under-allocate or overrun validated command buffers. A bad mask/shift can validate one field while hardware interprets another. The duplicated `VC4_LOADSTORE_FULL_RES_*` block should be treated carefully during edits. `VC4_PACKET_GEM_HANDLES` is not hardware, so consumers must keep filtering it out of emitted CLs.

Test signals: Submit CL validation tests should fail invalid packets/lengths and pass legal primitive/shader/binning packets. Render tests should exercise load/store general, full-res MSAA, tiling formats, texture formats, and `VC4_SUBMIT_RCL_SURFACE_*` combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_packet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_perfmon.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_perfmon.c

Purpose: Implements VC4 V3D performance monitor objects for gen4-era hardware. It exposes ioctl-backed creation, destruction, lookup, and value retrieval for hardware performance counters, and programs the active V3D counter registers while jobs run.

Important APIs/types/functions: `vc4_perfmon_get()`/`put()` refcount `struct vc4_perfmon`. `vc4_perfmon_start()` writes event selectors to `V3D_PCTRS(i)`, clears counters through `V3D_PCTRC`, enables them with `V3D_PCTRE`, and records `vc4->active_perfmon`. `vc4_perfmon_stop()` optionally accumulates `V3D_PCTR(i)` into 64-bit software counters and disables hardware counting. File lifetime is managed by `vc4_perfmon_open_file()`/`close_file()` and the file-local `xarray`. Ioctls are `vc4_perfmon_create_ioctl()`, `vc4_perfmon_destroy_ioctl()`, and `vc4_perfmon_get_values_ioctl()`.

Control flow: Open initializes an allocating xarray. Create validates V3D presence, counter count, and event IDs, allocates a flexible `vc4_perfmon`, initializes event selectors/refcount, inserts it with `xa_alloc()`, and returns an ID. Lookups lock the xarray, load by ID, and take a ref. Destroy erases by ID, stops it if active, and drops the ref. Close walks and deletes all remaining perfmons.

State and persistence: Per-file monitor state is held in `vc4_file->perfmons`; device-global active state is `vc4->active_perfmon`. Counter values persist in the perfmon object until destroy/close and are accumulated across stop calls when capture is true. No state persists beyond file/device lifetime.

Dependencies and integration points: Depends on `vc4_drv.h` definitions, V3D register helpers, DRM UAPI perfmon structs, xarray, refcounting, `copy_to_user()`, and V3D job code that starts/stops perfmons. All entry points reject `vc4->gen > VC4_GEN_4`.

Risks: Active perfmon ownership is protected mainly by call ordering and WARNs; misuse could program counters while another monitor is active. Destroy of an active monitor stops without capture, losing in-flight values. Event validation relies on `VC4_PERFCNT_NUM_EVENTS`. User pointer copy failures are handled, but callers must always balance `vc4_perfmon_put()`.

Test signals: Ioctl tests should cover invalid counts, invalid events, missing V3D, create/find/destroy/get-values, close cleanup, active destroy, and gen>4 rejection. Hardware tests should confirm counter accumulation after render workloads and no counter leakage between file descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_perfmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_plane.c

Purpose: Implements VC4 DRM plane support by converting DRM atomic plane state into HVS display-list words. It validates clipping, scaling, formats, modifiers, alpha/color settings, allocates HVS temporary memories, estimates bandwidth/load, supports async updates, and creates primary/overlay/cursor planes.

Important APIs/types/functions: `hvs_formats[]` maps DRM formats to HVS pixel formats/order and gen constraints. State hooks are `vc4_plane_reset()`, `vc4_plane_duplicate_state()`, and `vc4_plane_destroy_state()`. `vc4_plane_setup_clipping_and_scaling()` derives clipped source/destination rectangles and scaler modes. `vc4_plane_mode_set()` emits HVS4/HVS5 display lists; `vc6_plane_mode_set()` emits HVS6 display lists. `vc4_plane_allocate_lbm()` and `vc6_plane_allocate_upm()` allocate temporary HVS memories. `vc4_plane_atomic_check()`, `vc4_plane_write_dlist()`, `vc4_plane_async_set_fb()`, async check/update helpers, `vc4_format_mod_supported()`, `vc4_plane_init()`, and `vc4_plane_create_additional_planes()` provide DRM integration.

Control flow: Atomic check clears the new dlist, skips disabled planes, builds the generation-specific dlist, allocates LBM and for gen6 UPM, and returns errors before commit if unsupported. Mode-set first clips/scales with DRM helpers and margin adjustment, computes tiling-specific source offsets, emits control/position/pointer/pitch/CSC/scaling/filter words, patches the dlist size/next field, marks whether background fill is needed, and records load estimates. CRTC flush later calls `vc4_plane_write_dlist()` to copy words to HVS memory.

State and persistence: Per-plane derived state lives in `struct vc4_plane_state`: dlist buffer/count, offsets of mutable words, LBM node, UPM handles, load estimates, source/destination rectangles, scaling flags, and `needs_bg_fill`. LBM and UPM allocations persist across atomic state lifetime and are freed on state destruction or gen6 plane disable. Framebuffer BO use counts are incremented/decremented in prepare/cleanup.

Dependencies and integration points: Uses DRM atomic helpers, framebuffer DMA helpers, modifiers, blend/color properties, GEM BO helpers, HVS memory managers (`lbm_mm`, `upm_mm`), filter kernel allocation, CRTC margin/HVS flush paths, and register fields from `vc4_regs.h`. It is central to display output across HVS4, HVS5, VC6 C, and VC6 D variants.

Risks: Display-list packing is generation-sensitive; wrong fields can cause corrupt scanout or hardware hangs. T-tiled/SAND/P030 offset math is subtle, especially reflection and subsampled chroma. Async update is safe only when immutable dlist words match; missing a mutable word could overwrite HVS context. LBM/UPM refcount and `drm_mm` handling must stay balanced. Bandwidth estimates are conservative but still affect admission control elsewhere.

Test signals: KMS atomic tests should cover format/modifier matrix, RGB/YUV/P030/SAND/T-tiled, scaling up/down, reflection, margins, alpha/blend modes, color encoding/range, async page flips, disabled-plane cleanup, gen6 UPM reuse/free, and failure on unsupported modifiers or exhausted LBM/UPM memory. Visual tests should check chroma alignment, flips, fractional source rectangles, and background fill behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_qpu_defines.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_qpu_defines.h

Purpose: Defines VC4 QPU instruction encoding constants: ALU opcodes, register addresses, signal values, mux/condition/pack/unpack enums, and bit masks/shifts for 64-bit QPU instructions.

Important APIs/types/functions: Key enums are `qpu_op_add`, `qpu_op_mul`, `qpu_raddr`, `qpu_waddr`, `qpu_sig_bits`, `qpu_mux`, `qpu_cond`, `qpu_pack_mul`, `qpu_pack_a`, and `qpu_unpack_r4`. Macros `QPU_MASK()` and `QPU_GET_FIELD()` plus `QPU_*_SHIFT/MASK` constants decode signals, unpack/pack, conditions, branch bits, register addresses, muxes, add/mul operations, immediates, and branch targets.

Control flow: None locally. Consumers use these constants to build/decode shader instructions and to reason about shader validation results.

State and persistence: No runtime state. The header is a stable hardware encoding contract.

Dependencies and integration points: Standalone except for standard integer types from includers. Ties into shader compiler/validator paths and debug tooling that decode QPU programs. In this subset, `vc4_validate.c` depends on prevalidated shader metadata rather than decoding QPU instructions directly, but those metadata originate from code that uses these definitions.

Risks: QPU encodings are dense and overloaded; wrong shifts or enum values can miscompile shaders or misinterpret validation. `QPU_MASK()` uses 64-bit shifts, so callers must avoid invalid high/low ranges. Some enum values alias hardware special registers and must match A/B file semantics.

Test signals: Shader validation/disassembly/compiler tests should decode and encode representative ALU, branch, signal, pack/unpack, small-immediate, and register-address instructions. Rendering tests should catch regressions in shader execution and uniform/texture access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_qpu_defines.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_regs.h

Purpose: Provides register offsets, field masks, field helper macros, HVS display-list field definitions, and hardware constants for VC4/V3D display, render, HDMI/audio/CEC, pixel valve, HVS4/5/6, and scaler blocks.

Important APIs/types/functions: `VC4_MASK()`, `VC4_SET_FIELD()`, `VC4_GET_FIELD()`, `VC6_SET_FIELD()`, and `VC6_GET_FIELD()` are the primary bitfield helpers. Register groups cover `V3D_*` command lists/interrupts/perf counters, `PV_*` pixel valve timing, `SCALER_*` HVS4/5 control/status/display-list fields, `SCALER6*`/`SCALER6D*` HVS6 variants, HDMI audio/video/CEC fields, `enum hvs_pixel_format`, pixel order constants, CSC coefficients, tiling/scaling fields, and pointer/pitch fields.

Control flow: No executable flow, but the VC6 helper macros conditionally choose C vs D register layouts based on `hvs->vc4->gen`, so includers must have an `hvs` variable in scope for those macros.

State and persistence: No runtime state. Constants encode the hardware programming model and are persistent ABI between driver code and MMIO/display-list hardware.

Dependencies and integration points: Includes Linux bitfield/bitops helpers. Used broadly by VC4 V3D, HVS, HDMI, pixel valve, TXP, plane, perfmon, and validation/render code. `vc4_plane.c` consumes the display-list fields and CSC coefficients; `vc4_v3d.c` and `vc4_perfmon.c` consume V3D/perf counter registers; `vc4_txp.c` uses `VC4_SET_FIELD()`.

Risks: The header mixes multiple hardware generations and duplicate-looking fields; accidentally using HVS5 fields on HVS6 or C-layout fields on D-layout can silently corrupt MMIO programming. `VC4_SET_FIELD()` warns on overflow, so tests that hit warnings indicate invalid caller math or masks. Register constants are not self-validating.

Test signals: Runtime smoke tests should cover V3D ID reads, perf counters, HVS display-list programming, HDMI/audio/CEC paths, PV timing, and TXP writes. KUnit or compile-time tests can exercise field helpers with boundary values. Hardware debugfs register dumps provide integration evidence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_render_cl.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_render_cl.c

Purpose: Generates kernel-owned VC4 render command lists (RCLs). Instead of accepting userspace RCLs, it validates submitted render surfaces and emits the small set of legal tile load, bin-list branch, and store packets needed for rendering.

Important APIs/types/functions: `struct vc4_rcl_setup` tracks surface BOs, the allocated RCL BO, and write offset. `rcl_u8/u16/u32()` append packet data. `emit_tile()` emits per-tile load(s), tile coordinates, optional semaphore wait/sub-list branch, and stores. `vc4_create_rcl_bo()` sizes/allocates the RCL BO and fills it. `vc4_full_res_bounds_check()`, `vc4_rcl_msaa_surface_setup()`, `vc4_rcl_surface_setup()`, and `vc4_rcl_render_config_surface_setup()` validate surface descriptors. `vc4_get_rcl()` is the public entry point.

Control flow: `vc4_get_rcl()` rejects gen>4, validates tile ranges and binning bounds, resolves and validates color/Z/MSAA read/write surfaces, requires at least one write target, then calls `vc4_create_rcl_bo()`. RCL creation computes exact packet size, emits clear colors if requested, emits `TILE_RENDERING_MODE_CONFIG`, iterates tiles in requested order, and records CT1 start/end addresses in `exec`.

State and persistence: Allocates a `VC4_BO_TYPE_RCL` BO added to `exec->unref_list` for job lifetime. Records write BOs in `exec->rcl_write_bo[]`, CT1 addresses in `exec->ct1ca/ct1ea`, and surface pointers only in stack setup. No global state.

Dependencies and integration points: Uses UAPI submit structs, BO lookup via `vc4_use_bo()`, texture/render-size validation via `vc4_check_tex_size()`, packet constants from `vc4_packet.h`, and V3D submit scheduling that later runs CT1. Coupled to binner output through `exec->tile_alloc_offset` and bin tile dimensions.

Risks: Packet size accounting must match emitted bytes; `BUG_ON(setup->next_offset != size)` catches mismatches but would be fatal. Full-res tile bounds math and tile ordering are security-sensitive because they generate DMA addresses. Misordered tile coordinates/load/store packets can violate hardware sequencing. The code is gen4-only.

Test signals: Submit tests should validate bad tile ranges, missing write surfaces, invalid tiling/format bits, unaligned offsets, out-of-bounds full-res/MSAA buffers, and legal color/Z/MSAA combinations. Rendering tests should exercise clears, partial tile ranges, fixed RCL order flags, binned and binless submits, and EOF placement on the last store.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_render_cl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_trace.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_trace.h

Purpose: Declares Linux tracepoints for VC4 wait/submit/interrupt events, enabling ftrace/perf-style observation of GPU job submission and completion without changing normal driver behavior.

Important APIs/types/functions: `TRACE_SYSTEM vc4` and `TRACE_INCLUDE_FILE vc4_trace` define the trace namespace. Trace events are `vc4_wait_for_seqno_begin`, `vc4_wait_for_seqno_end`, `vc4_submit_cl_ioctl`, `vc4_submit_cl`, `vc4_bcl_end_irq`, and `vc4_rcl_end_irq`. Each event records DRM minor index and event-specific fields such as seqno, timeout, CL sizes, BO count, queue type, and CTN address range.

Control flow: No driver control flow; trace macros expand into static tracepoint definitions. The include guard allows `TRACE_HEADER_MULTI_READ`, and the file ends by setting `TRACE_INCLUDE_PATH` and including `trace/define_trace.h` as required by the kernel tracepoint pattern.

State and persistence: Tracepoints maintain kernel tracing metadata when compiled; event records are transient in tracing buffers. No VC4 state is modified.

Dependencies and integration points: Includes Linux tracepoint headers and expects `struct drm_device` fields such as `primary->index`. Instantiated by `vc4_trace_points.c`; called from wait, submit, and IRQ paths elsewhere in the VC4 driver.

Risks: Tracepoint prototypes must match call sites exactly or builds fail. Dereferencing `dev->primary` assumes a registered DRM device. Changing event fields affects userspace tracing scripts.

Test signals: Build with tracing enabled, enable `vc4:*` trace events, submit workloads, and verify begin/end seqnos, ioctl sizes, BCL/RCL selection, and interrupt completion events appear in order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_trace_points.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_trace_points.c

Purpose: Instantiates the tracepoints declared in `vc4_trace.h` for the VC4 driver.

Important APIs/types/functions: Defines `CREATE_TRACE_POINTS` before including `vc4_trace.h`, guarded by `#ifndef __CHECKER__` to avoid sparse/static-analysis issues. Includes `vc4_drv.h` for driver context expected by trace declarations.

Control flow: No runtime control flow. Compilation of this translation unit emits the tracepoint storage/definitions.

State and persistence: Creates static tracepoint metadata and call sites at build/load time. No mutable driver state.

Dependencies and integration points: Must be compiled exactly once with `CREATE_TRACE_POINTS`; other files include `vc4_trace.h` without defining it. Integrated with Linux trace infrastructure.

Risks: Removing or duplicating this file can cause missing or duplicate tracepoint definitions. The `__CHECKER__` guard avoids sparse incompatibility, so changes should preserve that behavior.

Test signals: Kernel build/link should have no duplicate trace symbols. Runtime tracefs should list the `vc4` events declared in the header when tracing support is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_trace_points.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_txp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_txp.c

Purpose: Implements the VC4 TXP/MOP writeback pipeline as a DRM CRTC, encoder, and writeback connector. It configures TXP destination registers so HVS output can be written into a framebuffer instead of a physical display.

Important APIs/types/functions: `struct vc4_txp` wraps `vc4_crtc`, `vc4_encoder`, writeback connector, platform device, data, and MMIO base. Register definitions cover `TXP_DST_PTR`, `TXP_DST_PITCH`, `TXP_DIM`, `TXP_DST_CTRL`, progress, and 40-bit high-address registers. Atomic writeback hooks are `vc4_txp_connector_atomic_check()` and `_commit()`. CRTC hooks use `vc4_hvs_atomic_*`. IRQ handling is in `vc4_txp_interrupt()`. Platform/component binding is `vc4_txp_bind()`/`unbind()` with data for bcm2835 TXP and bcm2712 MOP/MOPLET.

Control flow: Bind maps registers, initializes a CRTC, virtual encoder, writeback connector with supported formats, and IRQ. Atomic check validates writeback job size, format, and 16-byte pitch alignment, then marks the CRTC state armed. Commit computes TXP control bits from format/alpha/platform flags, writes destination address/pitch/dim/control, queues the writeback job, and relies on IRQ completion. Disable aborts busy hardware and powers down pre-gen6 TXP.

State and persistence: Runtime state is MMIO register programming and the writeback job queued on the connector. `txp_armed` is stored in `vc4_crtc_state`. Platform data persists per device and records HVS output/channel, encoder type, 40-bit support, byte-enable support, and dimension convention.

Dependencies and integration points: Uses DRM writeback, atomic helpers, framebuffer DMA helpers, vblank, component framework, platform OF matches, HVS CRTC helpers, and `vc4_regs.h` field helpers. It is an HVS output endpoint, not a render engine path.

Risks: Format arrays `drm_fmts[]` and `txp_fmts[]` must stay index-aligned. Incorrect address high register handling breaks >32-bit DMA. Interrupt completion must disable `TXP_EI` and signal writeback exactly once. Busy abort loop is polling with a timeout. KUnit guard macros intentionally fail tests on real MMIO access.

Test signals: DRM writeback tests should cover all advertised formats, alpha/no-alpha output, pitch alignment rejection, framebuffer/mode size mismatch, irq completion, disable during busy TXP, 40-bit addresses on bcm2712 data, and connector always-connected behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_txp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_v3d.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_v3d.c

Purpose: Binds and manages the gen4 V3D hardware block for VC4: MMIO/debugfs exposure, runtime power management, IRQ install, hardware init, and shared binner memory allocation used by binning command lists.

Important APIs/types/functions: `v3d_regs[]` defines debugfs register dumps. `vc4_v3d_debugfs_ident()` reports V3D revision/slices/TMUs/QPUs/semaphores. `vc4_v3d_pm_get()`/`put()` wrap runtime PM with `vc4->power_refcount`. `vc4_v3d_get_bin_slot()` allocates a 512 KiB binner slot or waits for render completion. `bin_bo_alloc()`, `vc4_v3d_bin_bo_get()`, `bin_bo_release()`, and `vc4_v3d_bin_bo_put()` manage a 16 MiB bin BO. Runtime PM callbacks enable/disable clocks and IRQs. `vc4_v3d_bind()`/`unbind()` integrate with the component framework.

Control flow: Bind allocates `vc4_v3d`, maps registers, obtains clock/IRQ, enables runtime PM, checks `V3D_IDENT0`, clears old binner overflow registers, installs IRQs, sets autosuspend, and stores `vc4->v3d`. Binner allocation loops until it gets a 16 MiB BO that does not cross a 256 MiB high-nibble boundary, then initializes slot allocator state and enables OOM interrupts. Slot allocation is guarded by `job_lock`, waits on last render seqno when full, and returns a bit index.

State and persistence: Device state includes `vc4->v3d`, `vc4->irq`, `power_refcount`, `bin_bo`, `bin_bo_kref`, `bin_alloc_size`, `bin_alloc_used`, and `bin_alloc_overflow`. The binner BO persists while referenced by jobs and is released by kref. Runtime PM state persists in the platform device.

Dependencies and integration points: Uses platform/component framework, runtime PM, clocks, VC4 IRQ helpers, BO allocator, render job wait/seqno helpers, debugfs, and V3D registers from `vc4_regs.h`. Validation allocates bin slots through `vc4_v3d_get_bin_slot()`, and submit paths require PM refs.

Risks: Binner memory addressing workaround is critical; a BO crossing the 256 MiB boundary can cause bad DMA addressing. Power refcount imbalance can leave V3D powered or suspend while in use. Slot exhaustion waits on render completion and must handle signals. Bind failure paths must drop runtime PM refs. All paths reject gen>4.

Test signals: Probe tests should verify IDENT0 mismatch failure, IRQ install/uninstall, runtime suspend/resume clock behavior, debugfs output, binner BO allocation under fragmented DMA memory, slot allocation/reuse after job completion, and no stale BPOA/BPOS across unbind/rebind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_v3d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_validate.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_validate.c

Purpose: Validates untrusted VC4 userspace binning command lists and shader records before the GPU reads them. Because VC4 lacks an IOMMU, this file is a central security boundary for preventing arbitrary DMA reads/writes via command streams, textures, vertex/index buffers, and shader uniforms.

Important APIs/types/functions: `vc4_use_bo()` validates BO indexes and rejects shader BO misuse. `vc4_check_tex_size()` validates dimensions/tiling/offset against BO size. `vc4_validate_bin_cl()` walks the bin CL with a packet whitelist. Packet validators include `validate_flush()`, `validate_start_tile_binning()`, `validate_increment_semaphore()`, `validate_indexed_prim_list()`, `validate_gl_array_primitive()`, `validate_gl_shader_state()`, `validate_tile_binning_config()`, and `validate_gem_handles()`. `reloc_tex()` validates/relocates texture and direct UBO uniforms. `validate_gl_shader_rec()` relocates shader records, uniforms, textures, and vertex attributes. `vc4_validate_shader_recs()` validates all referenced shader states.

Control flow: Bin CL validation copies allowed packets to the validated BO, skips pseudo `GEM_HANDLES`, dispatches validators from `cmd_info[]`, relocates address fields to DMA addresses, stops at HALT, sets CT0 end address, and requires start-tile-binning plus increment-semaphore/flush termination. Shader validation consumes handle tables and shader record packets, checks shader BO metadata and thread mode, copies uniforms, relocates texture descriptors/UBOs, fills uniform-address reset slots, and validates attributes against maximum primitive index.

State and persistence: Mutates `struct vc4_exec_info`: BO index table, shader state array/count, `found_*` packet flags, bin tile dimensions, bin slots, tile alloc offset, CT0 end address, shader/uniform CPU and GPU pointers, and max indices. It allocates binner slots through V3D state. No permanent state outside the job except temporarily allocated bin slots released by submit completion.

Dependencies and integration points: Depends on UAPI submit structs, `vc4_packet.h`, V3D binner allocation, BO metadata from shader validation, DRM GEM DMA objects, and render CL generation that consumes bin tile information. Texture bounds logic is reused by `vc4_render_cl.c`.

Risks: This is high-risk security code: integer overflow, off-by-one BO checks, incomplete packet whitelist, wrong shader record size, or texture mip/cube-map math bugs can expose arbitrary DMA. The shader handle check uses `src_handles[i] > exec->bo_count`; boundary correctness should be reviewed with surrounding BO array allocation. `cmd_info` must stay synchronized with packet sizes. Gen>4 is unsupported.

Test signals: Fuzz malformed bin CLs and shader records. Cover bad packet IDs/lengths/order, missing flush/semaphore, duplicate bin config/start, invalid BO handles, shader BO misuse, index/vertex bounds overflow, direct UBO bounds, unsupported texture formats, mip underflow, cube-map stride errors, tile count/bin slot allocation, and successful legal GL indexed/array primitive submits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_validate.c -->
