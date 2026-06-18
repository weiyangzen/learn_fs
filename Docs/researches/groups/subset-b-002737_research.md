# subset-b-002737 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_8_1_d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_8_1_d.h

## Purpose
`gmc_8_1_d.h` is the generated-style register-address catalog for the AMD GPU GMC 8.1 memory-controller block used by VI-era ASIC support. It gives driver code symbolic names for direct MMIO register offsets (`mm...`) and indexed memory-controller debug-table entries (`ix...`) covering GPU memory arbitration, the hub and client interfaces, GPUVM apertures and page-table contexts, ATC/ATS translation state, memory-controller sequencing, PHY training, power management, performance counters, display writeback MCIF paths, and debug machinery.

The file is not an implementation module. Its purpose is to freeze the hardware address contract so higher-level AMDGPU, display, KFD, SDMA, UVD, and power-management code can read and write named registers instead of embedding raw offsets.

## Important APIs, Types, And Functions
The header exports 1,681 preprocessor constants behind the `GMC_8_1_D_H` include guard. It declares no C functions, structs, enums, or storage.

Important constant families include:

- `mmMC_ARB_*`: memory-controller arbitration, GRUB/realtime priority, request aging, DRAM timing, return credits, refresh, power, address swizzle/hash, GECC, and bandwidth throttle registers.
- `mmMC_CITF_*`: client-interface credits, read/write grouping, DAGB delay, return mode, and performance monitor registers.
- `mmMC_HUB_*`: hub read-request, write-data-path, write-return, bypass, credit, clock-gating, idle/status, and per-client path registers for graphics, SDMA, UVD, VCE, ACP, ISP, MCD*, and other clients.
- `mmMC_RPB_*`, `mmMC_XBAR_*`, and `mmMC_XPB_*`: reorder buffer, crossbar, peer-to-peer, XDMA routing, aperture, destination map, CLG, sticky status, and interface controls.
- `mmMC_VM_*` and `mmVM_*`: framebuffer, AGP, system aperture, VF framebuffer size/offset, L1/L2 TLB/cache, page-table base/start/end registers, context controls, invalidation, PRT apertures, and VM protection-fault reporting.
- `mmATC_*`: ATC aperture, ATS control/status/fault, L1/L2 cache, VMID-to-PASID mapping, and performance counter registers.
- `mmGMCON_*`: register engine, save/restore ranges, performance monitors, power-gating FSM, masks, low-power target, and debug registers.
- `mmMC_SEQ_*`, `mmMC_TRAIN_*`, `mmMC_IO_*`, `mmMPLL_*`, and `mmMC_BIST_*`: memory sequencer, firmware upload, GDDR/PHY timing, training, BIST, memory PLL, framing, EDC/DBI, low-power timing, dynamic voltage scaling, and standby controls.
- `ixMC_TSM_DEBUG_*` and `ixMC_IO_DEBUG_*`: indirect indices used through debug index/data registers for training state-machine and memory IO lane inspection/programming.
- `mmMCIF_WB*_*`: display/writeback memory-client interface registers, including the base writeback instance and WB0/WB1/WB2 aliases at separate register ranges.

The paired `gmc_8_1_sh_mask.h` provides bit masks and shifts for these address constants. Call sites typically combine this header's offsets with `RREG32`, `WREG32`, `WREG32_P`, `REG_SET_FIELD`, `REG_GET_FIELD`, `amdgpu_ring_emit_wreg`, or display `dm_read_reg`/`dm_write_reg`.

## Control Flow
This header has no executable control flow. It influences control flow by choosing which hardware register a caller touches.

In `amdgpu/gmc_v8_0.c`, these constants drive the GMC v8 initialization and runtime paths: golden-register programming, MC firmware upload through `mmMC_SEQ_IO_DEBUG_INDEX`, `mmMC_SEQ_IO_DEBUG_DATA`, and `mmMC_SEQ_SUP_PGM`, memory training status polling through `mmMC_SEQ_TRAIN_WAKEUP_CNTL`, VRAM/aperture discovery from `mmMC_VM_FB_LOCATION` and `mmMC_VM_FB_OFFSET`, AGP/system aperture programming, GPUVM L1/L2 setup, VM context programming for VMIDs, TLB invalidation through `mmVM_INVALIDATE_REQUEST`/`mmVM_INVALIDATE_RESPONSE`, PRT aperture setup, VM fault interrupt handling, and clock-gating updates for hub, XPB, ATC, and VM L2 blocks.

Other use is table-driven. `vi.c` includes addresses such as `mmMC_ARB_RAMCFG` in golden-register arrays and switch cases. UVD, SDMA, DCE/display, KFD GFX v8, SMU, and BACO power paths include this header so ASIC-specific bring-up and low-power sequences can reference the same GMC register map.

## State And Persistence Behavior
The header itself is stateless; all values are compile-time integer macros. The state it names is persistent GPU hardware state: memory-controller arbitration settings, aperture registers, VM page-table bases, TLB/cache controls, PASID mappings, fault latches, sequencer firmware/training state, BIST state, memory PHY/PLL tuning, power-gating state, and performance counters.

Writes through these addresses persist in the device until reset, suspend/resume reinitialization, power-gating save/restore, or explicit driver reprogramming. Some registers are intentionally sticky or write-one-to-clear, such as XPB sticky status or VM fault/status latches, so incorrect access ordering can lose diagnostic information or leave stale fault state visible to later code. Indirect `ix...` values persist only when used to select and program debug-table data through the corresponding index/data MMIO pair.

## Dependencies
The file depends only on the C preprocessor and its include guard, but its meaning depends on the surrounding AMDGPU register stack:

- `gmc_8_1_sh_mask.h` supplies field masks and shifts for many register addresses.
- Register access helpers such as `RREG32`, `WREG32`, `WREG32_P`, `REG_SET_FIELD`, and `REG_GET_FIELD` provide the actual MMIO transactions and bit manipulation.
- The constants are valid for GMC 8.1/VI-era hardware paths. They should not be mixed with other generation address catalogs such as GMC 6.x/7.x or SOC15-style offset/index headers unless the caller is explicitly selecting compatible hardware.
- MC firmware blobs and memory-training tables must agree with the `mmMC_SEQ_*` and `ixMC_IO_DEBUG_*` address/index contract used by the driver.

## Integration Points
Direct include sites in this tree include `amdgpu/gmc_v8_0.c`, `amdgpu/vi.c`, `amdgpu/dce_v10_0.c`, `amdgpu/sdma_v3_0.c`, `amdgpu/uvd_v6_0.c`, `amdgpu/amdgpu_amdkfd_gfx_v8.c`, several PowerPlay SMU and BACO managers (`fiji`, `tonga`, `polaris`, `iceland`, `vegam`), `pm/powerplay/inc/smu7_common.h`, and `display/dc/dce112/dce112_compressor.c`.

The strongest integration is with `gmc_v8_0.c`, where this address map is the substrate for VRAM/GART layout, VMID programming, PRT, TLB invalidation, memory controller firmware/training, fault decode, and clock gating. Display integration uses GMCON and MCIF writeback addresses, for example compressor code writes `mmGMCON_LPT_TARGET`. Power-management integration uses the same map for BACO, SMU memory-controller setup, and low-power transitions.

## Risks
The main risk is silent hardware misprogramming. A wrong address or wrong generation header can still compile and can target a valid but unrelated register, producing VM faults, corrupted aperture setup, broken memory training, bad power gating, display writeback failures, or GPU hangs.

The direct/indirect split is another important risk. `mm...` values are direct register offsets, while `ix...` values are indices for debug index/data registers. Passing an indirect index to a direct MMIO helper, or writing a direct offset into an indexed debug path, will not be caught by the type system.

The MCIF writeback aliases are also easy to misuse. The generic `mmMCIF_WB_*` names alias WB0 addresses, while WB1 and WB2 use offset ranges around `0x5eb8` and `0x5ef8`; code that assumes the generic name selects the active writeback pipe may program only WB0.

Generated hardware headers have little local validation. Review must check that any new use pairs the correct address family with the correct mask header, hardware generation, access macro, polling semantics, and reset/power state. Fault/status registers and sticky W1C registers need particular care so diagnostics are not cleared while being decoded.

## Test Signals
Build-time signals are successful compilation of all direct include sites with `gmc_8_1_d.h` and `gmc_8_1_sh_mask.h`, no macro redefinition conflicts, and no missing masks for newly used register fields.

Runtime signals include successful VI-family probe, correct VRAM size and aperture logging, successful MC firmware load and memory training, working PCIE GART and VMID page-table programming, clean TLB invalidation responses, absence of unexpected VM protection faults, stable suspend/resume and BACO transitions, and working UVD/SDMA/display paths that depend on hub and MCIF access.

Diagnostic signals include meaningful VM fault reports from `mmVM_CONTEXT1_PROTECTION_FAULT_*`, expected `mmATC_VMID*_PASID_MAPPING` behavior for KFD, stable clock-gating register transitions in hub/XPB/ATC/VM L2, usable performance counter reads, and no hangs when golden-register tables touch GMC addresses during initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_8_1_d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_8_1_enum.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_8_1_enum.h

## Purpose
`gmc_8_1_enum.h` is the generated-style value-domain catalog for GMC 8.1 and closely related graphics/memory register fields. It gives symbolic names to encoded integer values used in register fields and packet/state programming, including surface tiling, address configuration, debug block IDs, render target formats, image and buffer formats, cache modes, performance monitor modes, and memory power-control requests.

Unlike `gmc_8_1_d.h`, this file does not name register addresses. Its role is to make field payloads readable and stable so code can select values such as a tiling mode, pipe layout, debug block, or color format without hard-coding unexplained numeric encodings.

## Important APIs, Types, And Functions
The header exports 64 `typedef enum` types behind the `GMC_8_1_ENUM_H` include guard. It declares no functions, structs, global objects, or executable code.

Important enum groups include:

- Surface and tiling basics: `SurfaceEndian`, `ArrayMode`, `PipeTiling`, `BankTiling`, `GroupInterleave`, `RowTiling`, `BankSwapBytes`, `SampleSplitBytes`, `SurfaceTiling`, `SurfaceArray`, `ColorArray`, and `DepthArray`.
- Addressing and macro-tiling layout: `NumPipes`, `PipeInterleaveSize`, `BankInterleaveSize`, `NumShaderEngines`, `ShaderEngineTileSize`, `NumGPUs`, `MultiGPUTileSize`, `RowSize`, `NumLowerPipes`, `TileType`, `NonDispTilingOrder`, `MicroTileMode`, `TileSplit`, `SampleSplit`, `PipeConfig`, `NumBanks`, `BankWidth`, `BankHeight`, `BankWidthHeight`, and `MacroTileAspect`.
- Debug block selectors: `DebugBlockId`, legacy `DebugBlockId_OLD`, and compressed/stride variants `DebugBlockId_BY2`, `DebugBlockId_BY4`, `DebugBlockId_BY8`, and `DebugBlockId_BY16`.
- Render, depth/stencil, and export values: `ColorTransform`, `CompareRef`, `ReadSize`, `DepthFormat`, `ZFormat`, `StencilFormat`, `CmaskMode`, `QuadExportFormat`, `QuadExportFormatOld`, `ColorFormat`, and `SurfaceFormat`.
- Buffer and image resource formats: `BUF_DATA_FORMAT`, `IMG_DATA_FORMAT`, `BUF_NUM_FORMAT`, and `IMG_NUM_FORMAT`.
- Cache, translation, and performance monitoring: `GATCL1RequestType`, `TCC_CACHE_POLICIES`, `MTYPE`, `PERFMON_COUNTER_MODE`, and `PERFMON_SPM_MODE`.
- Device-configuration and power values: `ENUM_NUM_SIMD_PER_CU`, `MEM_PWR_FORCE_CTRL`, `MEM_PWR_FORCE_CTRL2`, `MEM_PWR_DIS_CTRL`, `MEM_PWR_SEL_CTRL`, and `MEM_PWR_SEL_CTRL2`.

Representative values include `ARRAY_2D_TILED_THIN1` for tiling, `ADDR_SURF_P8_32x64_32x32` for pipe configuration, `FMT_BC7` and `IMG_DATA_FORMAT_BC7` for compressed formats, `PERFMON_COUNTER_MODE_ACCUM` for counters, `MTYPE_CC` for cacheable coherent memory type, and `FORCE_DEEP_SLEEP_REQUEST` for memory power control.

## Control Flow
The header has no runtime control flow. It affects control flow only when compiled code compares, switches on, or writes these enum values into hardware fields or command/state packets.

The debug-block enums are likely to feed diagnostic selection logic where a caller chooses a block ID and writes it to a debug selector register. The tiling and format enums feed address-library or register-field programming paths where the encoded value controls how memory is interpreted by the GPU. The power and performance enums feed low-power or counter-setup decisions where a selected symbolic state becomes a small integer written to a control field.

No direct include of `gmc_8_1_enum.h` was found in the checked AMDGPU source subtree during this research. That makes it a generated companion contract rather than an obviously active local implementation dependency, but the names and encodings still match the same ASIC generation's register-field vocabulary.

## State And Persistence Behavior
The header itself has no mutable state. The encoded values can become persistent hardware state when callers write them into registers, command buffers, context state, debug selectors, or power-management controls. Once programmed, those field values persist according to the owning register or command processor state until reset, context reprogramming, power transition, or explicit overwrite.

Some enum domains describe software-visible resource metadata rather than standalone hardware state. For example, tiling and image/buffer format values determine how surfaces, buffers, FMASK data, depth/stencil data, and compressed formats are interpreted. A mismatch between metadata and actual memory layout can persist as corrupted rendering or invalid memory interpretation even if the enum header itself is correct.

## Dependencies
This file has minimal syntactic dependencies, but semantic dependencies are strong:

- Register bitfields and packet definitions must allocate enough bits for the enum values used from this file.
- Address computation and surface layout code must agree with `ArrayMode`, `PipeConfig`, bank, row, tile split, and sample split encodings.
- Render, display, compute, and texture code must map DRM/KMS, Mesa, firmware, or kernel format concepts onto the correct `ColorFormat`, `SurfaceFormat`, `BUF_*`, and `IMG_*` values.
- Debug and performance tooling must choose the correct debug block ID family. The `DebugBlockId_OLD` and `*_BY2/BY4/BY8/BY16` variants are not interchangeable with the primary `DebugBlockId` list.
- Power-management code must pair `MEM_PWR_*` values with the correct GMC 8.1 memory-power registers and masks.

## Integration Points
The enum names mirror the field vocabulary used by the AMDGPU register headers in `include/asic_reg/gmc/` and by broader generation-specific AMD register catalogs. They integrate conceptually with GMC 8.1 address and mask headers: `gmc_8_1_d.h` names the register, `gmc_8_1_sh_mask.h` names the bit position, and this file names valid field payloads.

The address-format enums integrate with surface allocation and GPUVM setup because memory layout depends on pipe count, bank count, interleave size, tile split, macro-tile aspect, and array mode. The render/format enums integrate with color/depth/stencil state, buffer/image resource descriptors, and compression metadata. Debug block IDs integrate with register debug selectors and performance/debug dumps. Memory-power enums integrate with memory-controller power state transitions in SMU or BACO-style code.

Within the checked tree, direct users were not found by include-name search, so active local usage may be indirect, generated out, stale compatibility coverage, or available for out-of-tree/user-facing generated code. That absence is itself an integration signal: changes to this header should be treated as ABI-like register contract changes rather than refactors driven by local call-site compiler errors.

## Risks
The primary risk is numeric encoding drift. These enum values are hardware ABI, not arbitrary software choices. Renaming is usually harmless to generated users, but changing a numeric value can make a valid build program the wrong tiling, format, debug block, cache policy, performance mode, or power state.

Several domains contain reserved values and closely related names. `ColorFormat`, `SurfaceFormat`, `BUF_DATA_FORMAT`, and `IMG_DATA_FORMAT` overlap conceptually but are not identical; using a color-buffer format where an image descriptor format is required can silently produce wrong resource interpretation. Similarly, `DebugBlockId`, `DebugBlockId_OLD`, and stride-compressed debug ID variants encode different selector spaces.

The enums are plain C enum typedefs with no strong type enforcement at register-write boundaries. Callers can cast or pass any integer to field helpers, and the compiler generally cannot prove that a value belongs to the field being programmed.

Portability risk also exists because enum names such as `SurfaceEndian`, `ArrayMode`, or `PipeConfig` can appear in other generation headers. Including multiple generated enum catalogs in one translation unit may create type-name collisions unless the surrounding code keeps generation-specific includes isolated.

## Test Signals
Build-time signals are successful compilation of any translation unit that includes this header, absence of typedef-name collisions with other ASIC generation enum headers, and successful static checks that field masks can represent the maximum enum values selected by code.

Runtime signals depend on the consuming field. For tiling/address enums, useful signals are correct surface allocation, scanout, rendering, texture sampling, and VM access across linear, 1D, 2D, 3D, PRT, and thick/thin tile modes. For format enums, signals include correct color/depth/stencil rendering, buffer/image load-store behavior, FMASK/MSAA behavior, and compressed BC/APC/CTX formats. For debug and perf enums, signals are meaningful block selection and counter readings. For memory-power enums, signals are stable low-power transitions, resume, BACO, and memory-controller wake without training or VM faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_8_1_enum.h -->
