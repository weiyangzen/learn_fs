# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_7_0_d.h

## Purpose

`gfx_7_0_d.h` is the GFX 7.0 register address map for the AMD GPU driver subtree. It does not implement executable logic; it exports preprocessor constants that bind symbolic register names such as `mmCP_RB0_BASE`, `mmGB_TILE_MODE0`, `mmGRBM_STATUS`, `mmRLC_CNTL`, and `mmSQ_THREAD_TRACE_BASE` to their hardware register offsets. The companion driver code includes this header so register reads, writes, indirect debug accesses, firmware loads, queue setup, render state setup, clock/power management, and status polling can be expressed symbolically instead of with raw numeric offsets.

The file is guarded by `GFX_7_0_D_H` and is consistent with generated AMD ASIC register documentation: it is almost entirely `#define` statements, with no functions, structs, variables, inline helpers, or persistent software state. Its value is contractual. A wrong constant routes `RREG32()` or `WREG32()` to the wrong GPU register and can break initialization, command submission, power management, diagnostics, or memory-layout programming.

## Register Families And Exported Surface

The exported API is the macro namespace itself. Important groups include:

- Color buffer and depth buffer state: `mmCB_*` and `mmDB_*` cover blend constants, color target base/pitch/slice/view/info/attrib registers, CMASK/FMASK registers, depth/stencil base and clear registers, render/depth control, z-pass and occlusion counters, and CB/DB performance counters.
- Command processor and rings: `mmCP_*`, `mmCPC_*`, `mmCPF_*`, and `mmCPG_*` include graphics ring base/control/read/write pointer registers, microcode address/data registers for PFP/ME/CE/MEC, interrupt/status registers, DMA/coherency registers, EOP/fence/streamout/stat counters, scratch registers, HQD/MQD compute queue registers, and command-processor performance counters.
- Graphics backend and GRBM routing: `mmGB_*`, `mmCC_*`, `mmGC_USER_*`, and `mmGRBM_*` include address configuration, tile/macro-tile mode tables, backend disable masks, shader-array configuration, graphics block manager status, soft reset, GFX instance selection, debug, scratch, and performance counter registers.
- Primitive assembly, rasterization, and viewport state: `mmPA_*`, `mmVGT_*`, `mmIA_*`, `mmWD_*`, and `mmGFX_PIPE_*` cover clipper/viewport/scissor/rasterizer/screen-space state, primitive/input-assembler controls, draw/event initiators, DMA/index registers, tessellation and geometry-shader ring state, and related debug/perf counters.
- Compute and shader programming: `mmCOMPUTE_*`, `mmSPI_*`, `mmSQ_*`, `mmSQC_*`, and `mmSH_*` cover dispatch dimensions, program addresses, TBA/TMA trap addresses, resource registers, per-stage shader program/user data registers, shader memory configuration, wave/debug state, SQ resources, and thread trace registers.
- RLC and power/clock control: `mmRLC_*`, `mmCGTT_*`, `mmCGTS_*`, and related clock-gating macros expose RLC firmware loading, RLC status/control, save/restore scratch programming, safe mode, SPM, load balancing, static/dynamic power gating, memory sleep, and clock gating controls.
- Texture/cache/GDS blocks: `mmTA_*`, `mmTD_*`, `mmTCP_*`, `mmTCC_*`, `mmTCA_*`, `mmTCS_*`, and `mmGDS_*` cover texture address/data/cache blocks, L1/L2 cache policy and counters, GDS VMID ranges, atomics, GWS/OA resources, and GDS perf/debug state.
- Debug and indirect register names: `ixCLIPPER_DEBUG_REG*`, `ixSQ_WAVE_*`, `ixGDS_DEBUG_REG*`, `ixDIDT_*`, and similar `ix*` constants identify indexed or indirect debug register selectors rather than MMIO-style `mm*` offsets.

Some names intentionally alias the same offset, for example `mmCP_RB0_BASE` and `mmCP_RB_BASE`, or `mmCP_RING0_PRIORITY` and `mmCP_ME0_PIPE0_PRIORITY`. These aliases preserve different hardware/manual naming conventions used by different call sites.

## Control Flow And Integration Points

There is no local control flow in this header. Control flow appears when the macros are consumed by the GFX 7 driver:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v7_0.c` includes this file directly and pairs it with `gfx_7_2_sh_mask.h` field masks/enums. It uses `WREG32()`/`RREG32()` and field helpers to program the offsets defined here.
- Tiling initialization writes sequential register windows such as `mmGB_TILE_MODE0 + reg_offset` and `mmGB_MACROTILE_MODE0 + reg_offset`. This depends on the header preserving the contiguous layout of the tile-mode tables.
- `gfx_v7_0_select_se_sh()` writes `mmGRBM_GFX_INDEX` to route later instanced register operations to a selected shader engine, shader array, or broadcast destination.
- `gfx_v7_0_constants_init()` writes `mmGB_ADDR_CONFIG`, shader-memory registers, DB/CB/SPI/SQ defaults, rasterizer FIFOs, and related 3D-engine state during hardware bring-up.
- Graphics ring initialization writes `mmCP_RB0_CNTL`, `mmCP_RB0_WPTR`, `mmCP_RB0_RPTR_ADDR`, `mmCP_RB0_BASE`, and `mmCP_RB0_BASE_HI`, then starts and tests the ring.
- Compute queue initialization uses the HQD/MQD register block from `mmCP_HQD_VMID` through `mmCP_MQD_CONTROL` and from `mmCP_MQD_BASE_ADDR` through `mmCP_HQD_ACTIVE`, writing a serialized `struct cik_mqd` into hardware registers. This relies on register ordering matching the MQD struct layout expected by the driver.
- RLC bring-up and power management write `mmRLC_CNTL`, `mmRLC_GPM_UCODE_ADDR/DATA`, `mmRLC_LB_*`, `mmRLC_SERDES_*`, `mmRLC_PG_CNTL`, `mmRLC_AUTO_PG_CTRL`, and save/restore pointer registers while polling status registers such as `mmRLC_GPM_STAT`.
- Idle, reset, and diagnostics use `mmGRBM_STATUS`, `mmGRBM_STATUS2`, `mmGRBM_SOFT_RESET`, and CP halt registers to detect busy GPU state, halt engines, and recover.

Other generation siblings such as `gfx_8_1_d.h` and newer `gc_*_offset.h` files provide the same kind of register contract for later GPU IP generations. Older and newer amdgpu files share symbolic names where offsets or base-index conventions differ by generation.

## State And Persistence Behavior

The file itself has no runtime state and performs no persistence. Its constants address hardware state that is persistent inside the GPU until changed by driver register writes, firmware execution, reset, suspend/resume, or power-gating transitions. Examples include ring base pointers, tile-mode tables, VMID/GDS ranges, shader memory configuration, MQD/HQD queue state, RLC save/restore buffers, clock-gating controls, and performance counter selectors/counters.

Persistence-sensitive users include compute MQD programming, where selected hardware queue registers are mirrored into a driver-owned MQD buffer, and RLC save/restore setup, where register lists and clear-state descriptors are written through RLC scratch/register base macros so the firmware can restore graphics state across power transitions.

## Dependencies

This header has no include dependencies beyond the C preprocessor. It depends semantically on:

- GFX 7.0 hardware register documentation and the ASIC generation's register layout.
- Field mask headers such as `gca/gfx_7_2_sh_mask.h`, which define bit positions and masks for values read from or written to these offsets.
- Driver MMIO helpers such as `RREG32()`, `WREG32()`, `WDOORBELL32()`, `REG_SET_FIELD()`, and `REG_GET_FIELD()` in the amdgpu stack.
- Synchronization in consumers, especially `grbm_idx_mutex` and `srbm_mutex`, because some offsets are instanced or selected through GRBM/SRBM routing before access.
- Firmware blobs for CP/RLC/MEC code paths that load microcode through the `mmCP_*_UCODE_*` and `mmRLC_GPM_UCODE_*` registers.

## Risks

- Address-map drift is high impact. Changing any numeric offset without matching hardware documentation can corrupt unrelated GPU state.
- Contiguous register assumptions are embedded in consumers. Loops over `mmGB_TILE_MODE0 + reg_offset` and HQD/MQD ranges require the constants to remain ordered and gap-compatible with the hardware and data structures.
- Alias removal can break call sites that use different names for the same register role.
- Cross-generation name reuse is easy to misread. A macro name can appear in GFX 7, GFX 8, and SOC15-era headers with different offset conventions, so includes must stay generation-specific.
- Endianness and pointer-width handling lives in consumers, but the targeted registers here include 64-bit base/address pairs. Swapping low/high or using the wrong shift, such as the ring-address `>> 8` convention, can break command submission or memory writes.
- Debug and indirect `ix*` constants are not interchangeable with `mm*` MMIO offsets; using them through the wrong access path would target the wrong mechanism.

## Test Signals

Useful validation signals are mostly integration and hardware-facing:

- Build coverage that compiles `gfx_v7_0.c` with this header and its mask headers catches missing or renamed macros.
- GFX ring bring-up should pass `amdgpu_ring_test_helper()` after programming the `mmCP_RB0_*` registers.
- Compute queue setup should initialize MQDs and activate HQDs without timeout in `gfx_v7_0_mqd_deactivate()` or queue commit paths.
- GPU idle checks should observe `mmGRBM_STATUS` and `mmGRBM_STATUS2` returning expected idle values after initialization and before reset/suspend.
- RLC firmware load/start should complete after writes to `mmRLC_GPM_UCODE_*` and `mmRLC_CNTL`, with `mmRLC_GPM_STAT` polling clearing busy bits.
- Tiling and address-config paths should preserve expected display/render correctness after writes to `mmGB_ADDR_CONFIG`, `mmGB_TILE_MODE*`, and `mmGB_MACROTILE_MODE*`.
- Power and clock gating transitions should not hang while touching `mmRLC_CGCG_CGLS_CTRL`, `mmRLC_CGTT_MGCG_OVERRIDE`, `mmCGTS_SM_CTRL_REG`, and related RLC/SERDES registers.
