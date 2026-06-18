# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h lines 22324-24720

## Purpose

This chunk is generated AMD GC 11.0.0 register bitfield metadata. It contains no executable C logic; it exposes `__SHIFT` and `_MASK` constants used by AMDGPU, AMDKFD, display, MES, SDMA, IMU, and SOC21 support code to compose or decode 32-bit GC register values. The matching register addresses live in companion generated offset headers, especially `gc_11_0_0_offset.h`.

The range is mostly graphics context state for primitive assembly, scan conversion, variable-rate shading, render targets, color compression, queue targeting, shader memory setup, and command processor debug controls. It starts inside the `PA_CL_NGG_CNTL` definition, then covers many context-register masks, moves through `gc_pfvf_cpdec`, `gc_pfvf_grbmdec`, `gc_pfvf_padec`, and `gc_pfvf_sqdec`, and ends at the beginning of `gc_pfonly_cpdec` `CP_DEBUG_2` shift definitions. Although the repository path is under `ceph-client`, this header is AMD GPU driver hardware metadata and has no Ceph filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, callbacks, global variables, allocations, locks, or persistence APIs in this chunk. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit of a field.
- `<REGISTER>__<FIELD>_MASK` gives the in-register mask.
- Consumers combine these with `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32`, `WREG32`, and packet-building code that writes context registers.

Major register families in this range:

- Primitive, tessellation, and NGG setup: `PA_CL_NGG_CNTL`, `VGT_HOS_MAX_TESS_LEVEL`, `VGT_HOS_MIN_TESS_LEVEL`, `VGT_ENHANCE`, `IA_ENHANCE`, `VGT_DMA_SIZE`, `VGT_DMA_MAX_SIZE`, `VGT_DMA_INDEX_TYPE`, `WD_ENHANCE`, `VGT_PRIMITIVEID_EN`, `VGT_DMA_NUM_INSTANCES`, `VGT_PRIMITIVEID_RESET`, `VGT_EVENT_INITIATOR`, `VGT_DRAW_PAYLOAD_CNTL`, `VGT_ESGS_RING_ITEMSIZE`, `VGT_REUSE_OFF`, `VGT_GS_MAX_VERT_OUT`, `GE_NGG_SUBGRP_CNTL`, `VGT_TESS_DISTRIBUTION`, `VGT_SHADER_STAGES_EN`, `VGT_LS_HS_CONFIG`, `VGT_TF_PARAM`, and `VGT_GS_INSTANCE_CNT`.
- Rasterizer, scanner, anti-aliasing, and VRS state: `PA_SU_OVER_RASTERIZATION_CNTL`, `PA_STEREO_CNTL`, `PA_STATE_STEREO_X`, `PA_CL_VRS_CNTL`, `PA_SU_POINT_SIZE`, `PA_SU_POINT_MINMAX`, `PA_SU_LINE_CNTL`, `PA_SC_LINE_STIPPLE`, `PA_SC_MODE_CNTL_0`, `PA_SC_MODE_CNTL_1`, `PA_SC_CENTROID_PRIORITY_0/1`, `PA_SC_LINE_CNTL`, `PA_SC_AA_CONFIG`, `PA_SU_VTX_CNTL`, clip/discard adjust registers, the `PA_SC_AA_SAMPLE_LOCS_*` matrix, `PA_SC_AA_MASK_*`, `PA_SC_SHADER_CONTROL`, `PA_SC_BINNER_CNTL_0/1/2`, `PA_SC_CONSERVATIVE_RASTERIZATION_CNTL`, `PA_SC_NGG_MODE_CNTL`, `PA_SC_VRS_SURFACE_CNTL`, and `PA_SC_VRS_SURFACE_CNTL_1`.
- Depth and polygon state: `DB_HTILE_SURFACE`, `DB_SRESULTS_COMPARE_STATE0/1`, `DB_PRELOAD_CONTROL`, `DB_ALPHA_TO_MASK`, and the `PA_SU_POLY_OFFSET_*` scale/offset/clamp registers.
- Stream-out and opaque draw state: `VGT_STRMOUT_DRAW_OPAQUE_OFFSET`, `VGT_STRMOUT_DRAW_OPAQUE_BUFFER_FILLED_SIZE`, and `VGT_STRMOUT_DRAW_OPAQUE_VERTEX_STRIDE`.
- Color buffer render-target state: repeated `CB_COLOR0` through `CB_COLOR7` register groups for `BASE`, `VIEW`, `INFO`, `ATTRIB`, `FDCC_CONTROL`, `DCC_BASE`, `BASE_EXT`, `DCC_BASE_EXT`, `ATTRIB2`, and `ATTRIB3`. These include format, number type, component swap, blend optimization, slice/mip view, fragment count, destination alpha forcing, DCC/FDCC block sizing, independent block flags, compression-disable bits, and high address-extension fields.
- Virtualization-safe CP and GRBM targeting: under `gc_pfvf_cpdec`, `CONFIG_RESERVED_REG0/1`, `CP_MEC_CNTL`, and `CP_ME_CNTL`; under `gc_pfvf_grbmdec`, `GRBM_GFX_CNTL` and `GRBM_NOWHERE`.
- PA/PH implementation and performance controls: under `gc_pfvf_padec`, `PA_SC_ENHANCE*`, binner override/flag/DSM/tile-steering/FIFO/wave-table/event/timeout/performance controls, trap-screen hypervisor locks, `PA_PH_INTERFACE_FIFO_SIZE`, and `PA_PH_ENHANCE`.
- Shader queue and memory controls: under `gc_pfvf_sqdec`, `SQ_RUNTIME_CONFIG`, `SQ_DEBUG_STS_GLOBAL`, `SQ_DEBUG_STS_GLOBAL2`, `SH_MEM_BASES`, `SH_MEM_CONFIG`, `SQ_DEBUG`, `SQ_SHADER_TBA_LO/HI`, and `SQ_SHADER_TMA_LO/HI`.
- Privileged command-processor debug: the chunk starts `gc_pfonly_cpdec` with `CP_DEBUG_2` shift fields such as `CHIU_NOALLOC_OVERRIDE`, `RCIU_SECURE_CHECK_DISABLE`, packet-injector disable, context-done copy-state disable, NOP discard disable, DC interleave/clock/broadcast controls, and hardware detect disable fields. The chunk boundary ends before the corresponding `CP_DEBUG_2` masks.

## Control Flow

This header has no runtime control flow. The runtime pattern is:

1. ASIC-specific code includes `gc/gc_11_0_0_sh_mask.h` with a matching offset header.
2. Driver code selects a register offset or packet context-register slot.
3. A register value is built with these masks/shifts, usually through `REG_SET_FIELD` or direct shifts when constructing MQDs and default state.
4. Surrounding code writes the value through MMIO, SOC15 helpers, MES/CP packets, firmware-loaded MQDs, or display modifier/tiling paths.

Observed consumers in this tree include `gfx_v11_0.c`, `soc21.c`, `mes_v11_0.c`, `sdma_v6_0.c`, `amdgpu_amdkfd_gfx_v11.c`, `kfd_device_queue_manager_v11.c`, `kfd_mqd_manager_v11.c`, `imu_v11_0.c`, `amdgpu_display.c`, and `display/amdgpu_dm/amdgpu_dm_plane.c`.

Typical flows are GFX initialization programming default `SH_MEM_CONFIG` and `SH_MEM_BASES`; KFD queue-manager code building per-process shader memory policy; KFD MQD code encoding CP HQD and SDMA queue fields adjacent to the same generated namespace; SOC21 selecting GRBM pipe/ME/VMID/queue targets through `GRBM_GFX_CNTL`; GFX golden settings programming PA/VRS registers such as `PA_SC_VRS_SURFACE_CNTL_1`; and display code negotiating DCC-capable framebuffer modifiers that must stay compatible with the render-target DCC/FDCC fields in this generated family.

## State And Persistence Behavior

The file persists no software state. It describes hardware state stored in GC registers or context images.

Many fields in the PA/VGT/DB/CB families are graphics context state: they are programmed per draw, per pipeline state object, or through clear-state/context images, and they can be saved/restored by command processor context switching. Color buffer base, DCC base, extension, view, format, and compression fields describe GPU memory addresses and surface metadata that remain meaningful only while the relevant BOs, tiling metadata, and VM mappings are valid.

`SH_MEM_BASES`, `SH_MEM_CONFIG`, `SQ_SHADER_TBA_*`, and `SQ_SHADER_TMA_*` are process or VMID-sensitive shader execution state. They are initialized for graphics and compute contexts and may be rewritten on process activation, queue load, trap setup, reset recovery, or suspend/resume.

GRBM and CP control fields affect register access routing and command-processor engine state. Their values are transient control state and must be restored to a safe broadcast or default target after targeted writes. PA/PH enhancement, binner, FIFO, VRS, and performance registers are hardware configuration knobs that may be set by golden-register programming or ASIC-specific setup, and may be lost across reset or power transitions.

The macros do not encode access permissions or side effects. Some described fields are read-only status, some are write-only controls, some are privileged-only, some are context registers, and some are self-clearing or reserved according to hardware documentation outside this header.

## Dependencies And Integration Points

Direct dependencies are generated offsets and default-state files for the same ASIC generation, especially `gc_11_0_0_offset.h`, plus consumers that understand SOC15 register addressing and packet context-register ranges.

Key integration points:

- `gfx_v11_0.c` includes this header for GFX11 bring-up, golden register programming, shader memory defaults, GRBM indexing, CP/ME/MEC control, HQD/MQD programming, interrupt enablement, and reset paths.
- `soc21.c` uses `GRBM_GFX_CNTL` field masks to select pipe, ME, VMID, and queue before writing `regGRBM_GFX_CNTL`.
- `amdgpu_amdkfd_gfx_v11.c` and `kfd_device_queue_manager_v11.c` use `SH_MEM_CONFIG` and `SH_MEM_BASES` fields for KFD process memory policy and LDS/shared/private aperture setup.
- `kfd_mqd_manager_v11.c` uses the same generated mask style for CP HQD/MQD, SDMA MQD, doorbell, queue-size, context-save, and AQL fields used by user-mode compute queues.
- `mes_v11_0.c` builds MES and HQD control values and shares the same generated field contract for queue reset, queue activation, persistent state, doorbells, and VMID assignment.
- `sdma_v6_0.c` includes this header because GFX11 SDMA queue fields live in the generated GC namespace; SDMA ring initialization and KFD SDMA MQD construction depend on compatible mask definitions.
- `amdgpu_dm_plane.c` and `amdgpu_display.c` integrate with DCC/FDCC surface metadata exposed to userspace through DRM format modifiers. The CB DCC/FDCC fields in this chunk must agree with the modifier policy advertised for GC 11.0.0.
- `clearstate_gfx11.h` contains clear-state entries for context registers such as `VGT_SHADER_STAGES_EN` and `CB_COLOR0_INFO`, which depend on the same hardware register layout.
- `imu_v11_0.c` and firmware-loading paths depend on generated GC register definitions when building initialization microcode or golden programming sequences.

## Risks And Edge Cases

- Header/offset mismatch is the main structural risk. These untyped macros can compile with the wrong offset family and silently program the wrong register or field.
- This chunk starts and ends at artificial boundaries: `PA_CL_NGG_CNTL` is incomplete at the beginning, and `CP_DEBUG_2` has only shift definitions here. Adjacent chunks are required for a complete register audit.
- Context register fields must preserve reserved bits and respect packet/register address class. A value that is syntactically valid with `_MASK` can still be invalid for a context register, privileged register, or read-only status field.
- GRBM targeting is fragile. A stale `GRBM_GFX_CNTL` pipe/ME/VMID/queue selection can direct later register writes to one queue or VMID instead of broadcast state.
- `SH_MEM_BASES` and `SH_MEM_CONFIG` are VM/process sensitive. Wrong private/shared base, address mode, alignment mode, or instruction prefetch values can break shader memory addressing, trap handling, or KFD queues.
- Trap base/address fields split low and high address bits; `SQ_SHADER_TBA_HI__TRAP_EN` shares the high register with address bits. Misplaced shifts can corrupt trap address or enable state.
- Render-target address fields are unit-scaled, such as `BASE_256B` and high extension fields. Treating them as byte addresses can point CB or DCC metadata at the wrong memory.
- DCC/FDCC fields are tightly coupled to tiling, display modifiers, userspace metadata, and compression capabilities. Advertising incompatible DCC modifiers or programming inconsistent independent-block/max-block fields can cause corruption, scanout rejection, or decompression failures.
- VRS and AA sample-location masks are dense packed fields. Bad packing can produce rendering artifacts without obvious kernel errors.
- CP debug and disable fields can alter hardware detection, packet injection, broadcast, clocking, NOP discard, or context-copy behavior. These are privileged controls and should not be changed without ASIC-specific validation.
- Full-width masks such as `0xFFFFFFFFL` do not imply safe arbitrary writes; they may represent data payloads, address fragments, status, or hardware-owned counters.

## Test Signals

Useful validation is mostly build, generated-header consistency, and hardware behavior:

- Build coverage for GFX11/SOC21 paths that include `gc_11_0_0_sh_mask.h`, especially `gfx_v11_0.c`, `soc21.c`, `mes_v11_0.c`, `sdma_v6_0.c`, `amdgpu_amdkfd_gfx_v11.c`, KFD v11 queue/MQD code, display plane code, and IMU code.
- Generated-header checks that every complete field has matching `__SHIFT` and `_MASK`, masks align with shifts, fields do not overlap unexpectedly within a register, and register names match `gc_11_0_0_offset.h`.
- GFX ring and compute ring smoke tests that initialize queues, submit packets, complete fences, reset queues, and survive GPU reset or suspend/resume.
- KFD tests that create, run, preempt, evict, restore, and destroy user queues across multiple VMIDs, with trap/debug paths exercising `SQ_SHADER_TBA/TMA` and `SH_MEM_*` state.
- Display modifier tests for GC 11.0.0 DCC scanout and rendering: linear, DCC, DCC retile, 64B/128B independent blocks, 4K-or-larger modes, page flips, and BO import/export metadata.
- Graphics rendering tests that cover tessellation, GS/NGG, stream-out, primitive ID reset, VRS, MSAA/sample locations, conservative rasterization, depth/stencil, polygon offset, color compression, and all eight color render targets.
- Reset and power-transition tests that confirm golden PA/VRS/PH settings, shader memory defaults, GRBM broadcast state, queue state, and CB/DCC programming are restored correctly.
- Negative signals include GPU hangs during draw or queue activation, failed fences, wrong VMID/queue register targeting, KFD trap failures, corrupted render targets, DCC scanout rejection, VRS/AA artifacts, unexpected CP/MES reset behavior, or ASIC-specific regressions isolated to GC 11.0.0/SOC21 devices.
