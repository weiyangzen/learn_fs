# subset-b-003418 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_3_d.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_3_d.h

### Purpose
`smu_7_1_3_d.h` is a generated AMD SMU 7.1.3 register-address header used by the DRM AMDGPU/Radeon-era ASIC register layer. It maps symbolic register names to memory-mapped or indirect-register offsets for the system management unit, graphics clock block, thermal monitor, power-management, ROM, firmware scratch/status, CAC, and fuse/register-table regions. The header contains no executable code; its value is the hardware ABI between driver code and SMU-family registers.

### Important APIs, Types, And Functions
There are no functions or C types. The public surface is the macro namespace:

- `mm*` macros define directly addressed MMIO register offsets, especially SMC/SMU/GCK/ROM indirect index and data ports such as `mmSMC_IND_INDEX`, `mmSMC_IND_DATA`, `mmSMC_MESSAGE_*`, `mmSMC_RESP_*`, `mmSMC_MSG_ARG_*`, and `mmSMU_IND_INDEX_*`.
- `ix*` macros define indirect indexed register addresses, including `ixSMC_SYSCON_*`, `ixCG_*`, `ixTHM_*`, `ixGENERAL_PWRMGT`, `ixPWR_*`, `ixROM_*`, and firmware-visible table slots.
- Repeated indexed ranges describe firmware tables: `ixMCARB_DRAM_TIMING_TABLE_1` through `_96`, `ixDPM_TABLE_1` through `_440`, `ixSOFT_REGISTERS_TABLE_1` through `_30`, and `ixSMU_PM_STATUS_0` through `_127`.
- Specialized blocks cover thermal/fan/tachometer registers, AVFS/CKS power registers, LCAC/CAC counters, SVI2 power status, current power-gating status, and ROM software command/data windows.

### Control Flow
The file has no runtime control flow. Driver control flow appears in consumers that choose the correct access path:

- Direct `mm*` offsets are read or written through MMIO helpers.
- Indirect `ix*` addresses are typically accessed by writing an address to an index register and then reading/writing the matching data register.
- SMC mailbox control flow is implied by the register triplets: callers write `mmSMC_MSG_ARG_*`, post a command through `mmSMC_MESSAGE_*`, and poll `mmSMC_RESP_*`.
- Table ranges are consumed by loops or generated field accessors in adjacent driver code; callers must preserve the same stride and base offsets encoded here.

### State, Persistence, And Dependencies
The header itself is stateless and persistent only as compile-time constants. The state it addresses is hardware state: clocks, fuses, firmware mailboxes, thermal readings, power-management state, ROM command buffers, SMU firmware tables, and status counters. It depends only on inclusion into C translation units and its include guard `SMU_7_1_3_D_H`, but semantically it depends on SMU 7.1.3 register layout compatibility. The numeric values must stay synchronized with AMD hardware documentation and with companion field/mask headers for the same ASIC family.

### Integration Points
This file integrates with AMD GPU driver code under `drivers/gpu/drm/amd` that performs ASIC-specific register access. It is likely included by SMU, powerplay, thermal, BIOS/ROM, and low-level register helper paths for hardware generations that use SMU 7.1.3 naming. It also pairs with `smu_7_1_3_enum.h` for symbolic field values and with generated `_sh_mask.h` or similar headers that define bit fields for the addresses listed here.

### Risks
The main risk is silent hardware misprogramming: a wrong constant can target the wrong register while still compiling cleanly. Multiple aliases share the same numeric offsets, such as SMC/GCK/SMU indirect index/data ports, so consumers must use the alias appropriate to their block without assuming a unique address implies a unique semantic. The large sequential table regions invite off-by-one mistakes in loop bounds, especially for DPM table entries ending at `_440` and PM status entries ending at `_127`. Mixed address spaces are also risky: `mm*` offsets and `ix*` indirect addresses are not interchangeable. Registers controlling clocks, thermal limits, power gating, ROM commands, and firmware mailboxes are high impact and may require ordering, polling, or firmware ownership rules outside this header.

### Test Signals
Useful validation is mostly integration-level: successful driver build with all dependent register macros resolved, GPU boot and SMU firmware initialization on matching hardware, SMC message/response handshakes completing, thermal/fan telemetry reporting plausible values, DPM and clock transitions succeeding, ROM reads returning a valid `0xaa55` signature through the associated ROM path, and no hangs during suspend/resume or power-gating transitions. Static checks can compare generated offsets against the upstream source or register database and assert table ranges have the expected stride.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_3_d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_3_enum.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_3_enum.h

### Purpose
`smu_7_1_3_enum.h` is the companion generated symbolic-value header for AMD SMU 7.1.3 register programming. Where the `_d.h` file names register addresses, this file names the numeric values placed into register fields: SMU mailbox message IDs, version constants, ROM signature, surface layout encodings, debug block IDs, data/number formats, tiling configuration values, cache/performance monitor modes, and memory power-control selections.

### Important APIs, Types, And Functions
The header defines macros and many `typedef enum` domains; it has no functions.

- SMU/firmware constants include address-range metadata, SFP/SAMU/SMU key ranges, `SMC_MSG_*` command IDs, `SMC_VERSION_MAJOR`, `SMC_VERSION_MINOR`, `SMC_HEADER_SIZE`, and `ROM_SIGNATURE`.
- Surface and address-layout enums include `SurfaceEndian`, `ArrayMode`, `PipeTiling`, `BankTiling`, `GroupInterleave`, `RowTiling`, `BankSwapBytes`, `SampleSplitBytes`, `NumPipes`, `PipeInterleaveSize`, `BankInterleaveSize`, `NumShaderEngines`, `ShaderEngineTileSize`, `NumGPUs`, `MultiGPUTileSize`, `RowSize`, `NumLowerPipes`, and later `TileType`, `MicroTileMode`, `TileSplit`, `SampleSplit`, `PipeConfig`, `NumBanks`, `BankWidth`, `BankHeight`, `BankWidthHeight`, and `MacroTileAspect`.
- Debug and tracing enums include the large `DebugBlockId` table plus legacy/derived `DebugBlockId_OLD`, `DebugBlockId_BY2`, `DebugBlockId_BY4`, `DebugBlockId_BY8`, and `DebugBlockId_BY16` mappings for different debug-block granularity encodings.
- Render/data format enums include `ColorTransform`, `CompareRef`, `ReadSize`, `DepthFormat`, `ZFormat`, `StencilFormat`, `CmaskMode`, `QuadExportFormat`, `QuadExportFormatOld`, `ColorFormat`, `SurfaceFormat`, `BUF_DATA_FORMAT`, `IMG_DATA_FORMAT`, `BUF_NUM_FORMAT`, and `IMG_NUM_FORMAT`.
- Cache, performance, surface-array, and memory-power enums include `GATCL1RequestType`, `TCC_CACHE_POLICIES`, `MTYPE`, `PERFMON_COUNTER_MODE`, `PERFMON_SPM_MODE`, `SurfaceTiling`, `SurfaceArray`, `ColorArray`, `DepthArray`, `ENUM_NUM_SIMD_PER_CU`, `MEM_PWR_FORCE_CTRL`, `MEM_PWR_FORCE_CTRL2`, `MEM_PWR_DIS_CTRL`, `MEM_PWR_SEL_CTRL`, and `MEM_PWR_SEL_CTRL2`.

### Control Flow
The file has no executable control flow. It guides control flow in consumers by providing exact values used in switch statements, register field packing, mailbox command dispatch, debug-block selection, tiling computations, and format validation. For example, a power-management path may select an `SMC_MSG_*` value before writing the SMC message register, while a debug path may encode a `DebugBlockId` into a debug selection field.

### State, Persistence, And Dependencies
There is no mutable state in the header. The persisted meaning is the numeric ABI shared by compiled driver code, GPU hardware, and SMU firmware. Dependencies are limited to C enum syntax and the include guard `SMU_7_1_3_ENUM_H`, but the values are semantically coupled to register field layouts in companion generated headers and to the addresses in `smu_7_1_3_d.h`.

### Integration Points
This header is consumed by AMD GPU register programming code that needs named field values rather than raw numbers. It bridges SMU mailboxes, graphics memory layout programming, debug/performance monitor configuration, render/depth/surface formats, cache policy, and memory power-control code. The `SMC_MSG_*` macros are especially tied to SMC message registers in `smu_7_1_3_d.h`, while the format and tiling enums are typically paired with bitfield masks in other ASIC headers.

### Risks
Numeric compatibility is the critical risk. Reordering or renumbering enum values would compile but corrupt hardware programming. The file mixes unrelated domains in one global namespace, so name collisions or using a value from the wrong enum domain can be hard to detect in C. Several enums include reserved values that should not be emitted except where hardware documentation says they are valid. The old and granularity-specific debug ID tables look similar but encode different numeric spaces; using `DebugBlockId_OLD` where `DebugBlockId` is expected can select the wrong block. SMU message IDs are firmware protocol values, so mismatch with loaded firmware can cause ignored commands, timeouts, or unsafe power-state transitions.

### Test Signals
Useful signals include compile coverage of all consumers, static comparison against the source register database, successful SMU command tests for each used `SMC_MSG_*`, debug/perfmon block selection producing sane counters, graphics tests that exercise color/depth/surface/tiling formats, and suspend/resume or DPM tests that touch memory power-control enums. Fuzz or assertion tests around register-field builders can reject reserved enum values and mismatched enum domains before MMIO writes are issued.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_3_enum.h -->
