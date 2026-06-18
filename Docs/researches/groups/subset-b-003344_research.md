# subset-b-003344 Research

Grouped source research for the subset B work item. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/oss_2_4_d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/oss_2_4_d.h

## Purpose
`oss_2_4_d.h` is the OSS 2.4 register address header for the AMDGPU Linux driver. It contains only preprocessor constants mapping symbolic register names to MMIO register indices for the OSS block generation used by Iceland/CIK-era hardware. The companion headers in the same directory provide field masks and enum values; this file anchors those fields to actual register offsets consumed by low-level `RREG32()` and `WREG32()` accessors.

The covered hardware areas are interrupt handler (`IH_*`), semaphore/mailbox (`SEM_*`), system register bus manager (`SRBM_*`), SDMA0/SDMA1 engine control and rings, and HDP/XDP host data path registers.

## Important APIs, Types, and Functions
- The public interface is a flat list of `#define mm...` constants. There are no C functions, structs, or runtime declarations.
- IH address constants include `mmIH_VMID_0_LUT` through `mmIH_VMID_15_LUT`, `mmIH_RB_CNTL`, `mmIH_RB_BASE`, `mmIH_RB_RPTR`, `mmIH_RB_WPTR`, writeback pointer address registers, interrupt control/status, DSM match controls, and `mmIH_VERSION`.
- SEM constants cover MCIF and client request configuration (`mmSEM_MCIF_CONFIG`, `mmSDMA_CONFIG`, `mmUVD_CONFIG`, `mmVCE_CONFIG`, `mmACP_CONFIG`, `mmCPG_CONFIG`, `mmCPC1_CONFIG`, `mmCPC2_CONFIG`), status/EDC, mailbox payload/control, and "chicken bit" workaround controls.
- SRBM constants include core control/status, soft reset, clock enable controls, read/firewall error reporting, DSM triggers, perf counters, domain address windows, GRBM index/select indirection, virtualization controls, and CAM registers.
- SDMA constants are repeated for engines 0 and 1. Each engine has microcode, power/clock, ring buffer, indirect buffer, context, doorbell, virtual address, watermark, CSA, dummy, preempt, performance, and status registers. Register ranges are separated by engine and queue context, for example `mmSDMA0_GFX_*`, `mmSDMA0_RLC0_*`, `mmSDMA0_RLC1_*`, then the same pattern for `SDMA1`.
- HDP/XDP constants define host path, nonsurface addressing, tiling/address config, memio access, direct-to-HDP flush/bar update slots, peer-to-peer mailbox/BAR config, status/debug, and high BAR address bits.

## Control Flow
There is no executable control flow in this header. Runtime control flow appears in consumers such as `amdgpu/iceland_ih.c`, `amdgpu/sdma_v2_4.c`, `amdgpu/cik.c`, and `amdgpu/vi.c`, where code selects one of these register offsets, reads or writes it through AMDGPU MMIO helpers, and composes fields using `oss_2_4_sh_mask.h`. For example, interrupt setup writes IH ring base/read/write pointer registers and toggles `mmIH_RB_CNTL`; SDMA setup iterates engine offsets from `mmSDMA0_*` to configure rings, IBs, writeback pointers, and enable bits.

## State and Persistence Behavior
This file stores no driver state. The values are compile-time ABI constants for hardware registers. State lives in the GPU registers reached through these offsets and in driver-owned objects that decide what to write. Because many registers control persistent hardware modes until reset or reprogramming, incorrect constants can persist as bad ring setup, disabled interrupts, stale writeback addresses, bad VMID selection, or broken host cache behavior until device reset.

## Dependencies and Integration Points
- Included directly by `drivers/gpu/drm/amd/amdgpu/iceland_ih.c` and `drivers/gpu/drm/amd/amdgpu/sdma_v2_4.c` for OSS 2.4-specific register programming.
- Designed to be included with `oss_2_4_sh_mask.h` so address constants and field masks share the same register schema.
- Indirectly relies on AMDGPU register access helpers such as `RREG32`, `WREG32`, `REG_SET_FIELD`, and engine offset tables in SDMA code.
- Register names overlap with newer generation headers, so include ordering and ASIC-specific source selection are the boundary that keeps OSS 2.4 offsets from being used on incompatible hardware.

## Risks
- A wrong offset silently targets a different hardware register. The highest risk areas are reset, interrupt ring control, SDMA ring base/write pointer registers, and HDP cache flush controls because errors can hang command submission or lose interrupts.
- The `SDMA0` and `SDMA1` blocks are highly repetitive; manual edits can accidentally update one engine but not the other or use the wrong engine offset.
- The header contains both low address spaces such as IH/SRBM and high address ranges such as perf counters and CAM/domain registers; callers must use the correct MMIO access path for the target ASIC.
- Constants are generated hardware documentation artifacts. Refactoring names without preserving compatibility can break existing driver code that uses these exact macros.

## Test Signals
- Compile coverage: build the AMDGPU driver with `CONFIG_DRM_AMDGPU` and an affected ASIC path to catch missing or renamed macros.
- Runtime bring-up signals: IH ring initialization succeeds, interrupts are delivered, SDMA rings start and process jobs, and no SRBM read/firewall errors appear in kernel logs.
- Targeted checks: compare `mmIH_RB_CNTL`, `mmIH_RB_BASE`, `mmSDMA0_GFX_RB_CNTL`, `mmSDMA1_GFX_RB_CNTL`, and `mmHDP_XDP_CGTT_BLK_CTRL` values against the vendor register database for OSS 2.4.
- Regression symptoms: GPU reset loops, stuck SDMA fences, IRQ storms or missing IRQs, HDP cache coherency failures, or failed suspend/resume on affected hardware.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/oss_2_4_d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/oss_2_4_enum.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/oss_2_4_enum.h

## Purpose
`oss_2_4_enum.h` defines named numeric values for OSS 2.4 register fields and related GPU programming domains. It turns raw field encodings into C enum constants for interrupt client ranges, perf monitor selectors, SRBM/GRBM target selectors, SDMA performance events, tiling/addressing modes, debug block IDs, color/depth/surface formats, cache policies, memory types, and perf counter modes.

Although stored under the OSS register directory, the enum catalog is broader than OSS-only control registers. It includes shared register-field encodings used by graphics, memory layout, HDP addressing, and debug/performance plumbing on the same ASIC generation.

## Important APIs, Types, and Functions
- There are no functions or structs. The API is a set of `typedef enum` types with stable integer values matching hardware field encodings.
- Interrupt/perf enums: `IH_CLIENT_ID` maps client source ID ranges for DC, VGA, CAP, VIP, ROM, BIF, SAM, SRBM, UVD, VMC, RLC, PDMA, and CG; `IH_PERF_SEL`, `SRBM_PERFCOUNT1_SEL`, and `SDMA_PERF_SEL` define event selectors written into perf-control fields.
- Routing/select enums: `SYS_GRBM_GFX_INDEX_SEL` and `SRBM_GFX_CNTL_SEL` select blocks for indirect GRBM/SRBM controls, including BIF, SDMA0/1, UVD, VCE0/1, ACP, SMU, SAMMSP/SAMSCP, ISP, test, and additional SDMA instances.
- Tiling/address enums: `SurfaceEndian`, `ArrayMode`, `PipeTiling`, `BankTiling`, `GroupInterleave`, `RowTiling`, `BankSwapBytes`, `SampleSplitBytes`, `NumPipes`, `PipeInterleaveSize`, `BankInterleaveSize`, `NumShaderEngines`, `ShaderEngineTileSize`, `NumGPUs`, `MultiGPUTileSize`, `RowSize`, `NumLowerPipes`, `TileType`, `NonDispTilingOrder`, `MicroTileMode`, `TileSplit`, `SampleSplit`, `PipeConfig`, `NumBanks`, `BankWidth`, `BankHeight`, `BankWidthHeight`, and `MacroTileAspect`.
- Debug enums: `DebugBlockId` gives a dense newer client block map; `DebugBlockId_OLD` preserves the older debug block ID map; `DebugBlockId_BY2`, `DebugBlockId_BY4`, `DebugBlockId_BY8`, and `DebugBlockId_BY16` provide reduced block ID maps for stride/grouped debug selection.
- Format enums: `ColorTransform`, `CompareRef`, `ReadSize`, `DepthFormat`, `ZFormat`, `StencilFormat`, `CmaskMode`, `QuadExportFormat`, `QuadExportFormatOld`, `ColorFormat`, `SurfaceFormat`, `BUF_DATA_FORMAT`, `IMG_DATA_FORMAT`, `BUF_NUM_FORMAT`, and `IMG_NUM_FORMAT`.
- Miscellaneous hardware-policy enums: `GATCL1RequestType`, `TCC_CACHE_POLICIES`, `MTYPE`, `PERFMON_COUNTER_MODE`, `PERFMON_SPM_MODE`, `SurfaceTiling`, `SurfaceArray`, `ColorArray`, `DepthArray`, and `ENUM_NUM_SIMD_PER_CU`.

## Control Flow
This header has no executable paths. Control flow in consumers uses these enum constants as values shifted into register fields or compared against decoded field values. For example, an SDMA perf setup path can pick an `SDMA_PERF_SEL_*` selector, shift it into `SDMA0_PERFMON_CNTL__PERF_SEL*`, then write the register address from `oss_2_4_d.h`. Debug paths use the debug block ID enums to select hardware blocks before reading debug data.

## State and Persistence Behavior
The enum constants themselves are immutable compile-time symbols. They represent state encodings stored in GPU registers, ring packets, debug selectors, or tiling descriptors. Once a consumer writes one of these values to hardware, the selected performance event, debug block, memory tiling mode, format, or cache policy remains active according to the lifetime of the associated register or command until overwritten, reset, or consumed by hardware.

## Dependencies and Integration Points
- The enum values are meaningful only with register masks from `oss_2_4_sh_mask.h` and address definitions from `oss_2_4_d.h`.
- AMDGPU code also uses generic helper macros such as `REG_SET_FIELD`, so enum constants often appear as the value operand while mask headers provide the exact field placement.
- Graphics and memory-layout enum families need to stay consistent with packet formats, tiling/address library logic, and ASIC register documentation, even when this header is not directly included by every consumer.
- The header is guarded by `OSS_2_4_ENUM_H`, so it can be included by ASIC-specific code without duplicate type definitions.

## Risks
- Hardware enum values are ABI-like. Renumbering an enum to make it look cleaner would program different hardware behavior.
- Several enums include reserved or legacy names. Removing them can break code that preserves old debug layouts or handles reserved encodings defensively.
- Typographical artifacts such as `RESEVERED0` are part of the published symbol surface; fixing spelling without aliases can be source-incompatible.
- The file mixes unrelated domains. A consumer can compile while using the wrong enum family for a field if the value width happens to fit, so review must verify the target register field, not just C type compatibility.

## Test Signals
- Compile AMDGPU with warnings enabled to catch missing enum names or duplicate type definitions.
- Static review should verify each enum value against the OSS 2.4 hardware register database, especially selector enums and format/tiling encodings.
- Runtime test signals include valid interrupt source decoding, perf counters counting the selected event, debug reads targeting the expected block, and correct rendering/compute memory layout for surfaces using these format and tiling values.
- Negative signals include nonsensical perf counts, unreadable debug blocks, corrupted surfaces, failed VM/cache operations, or command processor faults after format or tiling changes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/oss_2_4_enum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/oss_2_4_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/oss_2_4_sh_mask.h

## Purpose
`oss_2_4_sh_mask.h` is the OSS 2.4 register field header. For each register defined by `oss_2_4_d.h`, it declares bit masks and shift values in the generated AMD style: `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`. These definitions are used by AMDGPU register helpers to compose, update, and decode 32-bit MMIO register values without hard-coded bit arithmetic in driver code.

The field catalog covers IH interrupt ring handling, SEM request/mailbox control, SRBM status/reset/debug/perf/virtualization, SDMA0/SDMA1 engine and queue contexts, and HDP/XDP host-data-path/cache/peer-to-peer controls.

## Important APIs, Types, and Functions
- There are no functions or data types. The interface is a generated set of `#define` macros.
- IH fields include PASID LUT entries, ring enable/size/writeback/overflow bits, base/read/write pointer fields, interrupt enable and MC VMID/high-water/credit controls, level/status bits, perf monitor selectors and counters, DSM match fields, and version value.
- SEM fields define MC request swap/credits, client request urgent/transaction bits for SDMA/UVD/VCE/ACP/CPG/CPC, status FIFO/pending flags, EDC disable, mailbox client routing, side/host mailbox payloads, mailbox enables, and workaround bits.
- SRBM fields define power/read behavior, graphics queue selection (`PIPEID`, `MEID`, `VMID`, `QUEUEID`), status/busy/pending bits, soft reset bits for many blocks, clock-enable delays, debug snapshots, read/firewall error attribution, DSM triggers, perf monitor controls, CAM remap fields, per-domain address windows, GRBM/SRBM indirect selection data, and virtualization reset/enable controls.
- SDMA fields are mirrored for `SDMA0` and `SDMA1`. They include microcode address/data, power/clock, global control, chicken/workaround bits, tiling/hash, status/perf, freeze/quantum, power gating/FSM, EDC/threshold/id/version, and GFX/RLC0/RLC1 ring/IB/context/doorbell/watermark/CSA/preempt registers.
- HDP/XDP fields include host path credits/cache invalidation, nonsurface base/info/size/flags, tiling and address config, memio command/status/data, D2H flush/bar update, P2P mailbox/BAR address and validity, MC/host/side config, FIFO/depth/gating controls, busy/sticky/debug status, and BAR high address nibbles.

## Control Flow
The header has no runtime control flow, but it shapes many driver control paths. Code reads a register, clears a mask, shifts a value by the matching `__SHIFT`, applies the mask, and writes it back. The local AMDGPU code also uses `REG_SET_FIELD(register_value, REGISTER, FIELD, value)`, which expands against these macros. Typical flows include:
- IH init: program ring base/writeback addresses, set `IH_RB_CNTL` size/writeback/overflow fields, enable interrupts in `IH_CNTL`, and clear overflow when detected.
- SDMA init: for each SDMA instance and queue, set ring size, endian/swap behavior, writeback controls, VMID/priv bits, polling addresses, IB base/size, doorbell enables, and finally `RB_ENABLE`.
- Reset and idle paths: inspect `SRBM_STATUS*` and `SDMA*_STATUS*` fields, then toggle `SRBM_SOFT_RESET__SOFT_RESET_*` bits if needed.
- HDP flush/config paths: use HDP/XDP masks to configure cache behavior, flush/invalidate, peer BARs, and clock-gating controls.

## State and Persistence Behavior
The macros do not hold state, but every mask maps to persistent hardware state bits in OSS 2.4 registers. Many fields are control latches (`RB_ENABLE`, soft reset, clock gating, cache invalidate), while others are status or sticky/error fields (`RB_OVERFLOW`, `READ_ERROR`, firewall violation, doorbell captured, sticky W1C). Some fields require write-one-to-clear or clear-after-set sequencing; callers must follow the hardware protocol rather than simply setting masks blindly.

## Dependencies and Integration Points
- Must match `oss_2_4_d.h` register names exactly, minus the `mm` prefix used for addresses.
- Pairs with enum values from `oss_2_4_enum.h` for selector fields such as perf events, GRBM/SRBM block selectors, tiling modes, endian modes, and format/address encodings.
- Consumed by `iceland_ih.c` and `sdma_v2_4.c` directly, and by broader AMDGPU CIK/VI-style paths using equivalent register names and `REG_SET_FIELD`.
- Depends on AMDGPU bitfield helper conventions: the double-underscore naming pattern is not cosmetic, it is how helper macros derive `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`.

## Risks
- A mask or shift mismatch corrupts neighboring fields. This is especially risky in compound control registers such as `IH_RB_CNTL`, `IH_CNTL`, `SRBM_GFX_CNTL`, `SDMA*_GFX_RB_CNTL`, and `HDP_MISC_CNTL`.
- Some fields have names ending in `MASK_MASK` because the hardware field itself is named `..._MASK`. Generic tooling must not collapse these names or assume it is a typo.
- SDMA0 and SDMA1 definitions are intentionally parallel. Divergence can break only one engine, which may appear as intermittent hangs depending on ring assignment.
- Write-one-to-clear and sticky status fields require exact semantics. Treating all masks as normal read-modify-write controls can lose error status or repeatedly clear important events.
- This generated header is large and easy to partially update; address/header/schema version skew between `_d.h`, `_enum.h`, and `_sh_mask.h` can compile but program invalid hardware fields.

## Test Signals
- Compile AMDGPU paths that include this header and use `REG_SET_FIELD` to catch missing macro pairs.
- Exercise IH and SDMA on OSS 2.4 hardware: interrupts arrive, IH overflow clear works, SDMA fences complete, ring writeback pointers update, and doorbells are accepted.
- Inspect debugfs or register dumps for expected field values after init: `IH_RB_CNTL.RB_ENABLE`, `SDMA*_GFX_RB_CNTL.RB_ENABLE/RB_SIZE`, `SRBM_GFX_CNTL` queue routing, and HDP flush/cache fields.
- Stress tests should include suspend/resume, GPU reset, command submission on both SDMA engines, interrupt storms, and cache-coherency-sensitive CPU/GPU buffer sharing.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/oss_2_4_sh_mask.h -->
