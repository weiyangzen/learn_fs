# subset-b-003412 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_1_d.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_1_d.h

### Purpose
`smu_7_1_1_d.h` is the generated register-address contract for the AMD SMU 7.1.1 block used by the VI/Iceland GPU path. It exports numeric `#define` constants for direct MMIO registers (`mm...`) and indirect SMC/SMU register addresses (`ix...`) so driver code can address clocks, power management, firmware scratch/status, thermal sensors, GPIO pads, ROM access, fuses, DPM tables, and memory-controller tables without embedding raw literals.

### Important APIs, Types, And Functions
This header defines no functions or C types; its API surface is 1099 preprocessor constants protected by `SMU_7_1_1_D_H`. Important register families include `mmSMC_IND_INDEX_*`/`mmSMC_IND_DATA_*` and `mmSMU_IND_INDEX_*`/`mmSMU_IND_DATA_*` indirect windows, `mmSMC_MESSAGE_*`, `mmSMC_RESP_*`, and `mmSMC_MSG_ARG_*` firmware mailbox registers, `ixCG_*` clock and thermal registers, `ixSMU_*` firmware/status/input registers, `ixMCARB_DRAM_TIMING_TABLE_*`, `ixMC_REGISTERS_TABLE_*`, `ixDPM_TABLE_*`, `ixSOFT_REGISTERS_TABLE_*`, `ixPM_FUSES_*`, `ixSMU_PM_STATUS_*`, `ixPWR_*` and `ixSCLK_*` power controls, `ixLCAC_*` leakage/CAC controls, and `ixROM_*`/`ixROM_SW_DATA_*` ROM access registers.

### Control Flow
There is no executable control flow in this file. Runtime flow is created by include sites that pass these constants to register helpers. In this tree, `amdgpu/vi.c` includes the file and uses constants such as `mmSMC_IND_INDEX_11`, `mmSMC_IND_DATA_11`, `mmSMC_IND_INDEX_4`, `mmSMC_IND_DATA_4`, `ixCGTT_ROM_CLK_CTRL0`, `ixROM_INDEX`, and `ixROM_DATA` for SMU-indirect and ROM access. `pm/powerplay/smumgr/iceland_smumgr.c` includes it and uses `SMC_IND` access plus `FIRMWARE_FLAGS`, `mmSMC_IND_INDEX_0`, `mmSMC_IND_DATA_0`, and `SMC_IND_ACCESS_CNTL` to wait on firmware state and transfer data through auto-incrementing indirect registers.

### State, Persistence, And Dependencies
The header has no in-memory state and persists nothing by itself. It describes persistent hardware state: writes to mailbox, DPM, thermal, ROM, fuse, and power registers can affect SMU firmware behavior and device power/clock state until hardware, firmware, or driver code changes it. It depends on companion generated mask headers, especially `smu_7_1_1_sh_mask.h`, for field masks and shifts used with these addresses. Consumers also depend on AMDGPU/PowerPlay register access helpers such as `RREG32`, `WREG32`, `WREG32_NO_KIQ`, `cgs_write_register`, `PHM_WRITE_FIELD`, and indirect-field wait macros.

### Integration Points
The file is part of the ASIC register include set under `include/asic_reg/smu`, alongside SMU 7.1.0, 7.1.2, 7.1.3, and 8.0 variants. It is selected by the VI/Iceland code paths where the register layout differs from neighboring ASICs. The SMC mailbox definitions integrate with PowerPlay firmware command paths, the indirect-window definitions integrate with ROM and firmware memory access paths, and the DPM/PM/thermal register tables provide the numeric base for higher-level SMU manager policy code.

### Risks
The main risk is numeric drift from the hardware specification: a wrong address can write an unrelated hardware register, break firmware handshakes, misread thermal/power state, or corrupt ROM/SMC indirect accesses. Several address families are dense sequential tables, so off-by-one generation errors are plausible and hard to catch by review. Similar macro names across ASIC versions make wrong-header inclusion dangerous. The duplicate indirect aliases, including indexed `mmSMC_IND_INDEX_*` and block-prefixed aliases, require consumers to choose the window expected by the hardware sequence. Direct writes to DPM, PM, thermal, fuse, and ROM control registers are high impact and should remain behind established driver helpers.

### Test Signals
Useful signals are compile coverage of `vi.c` and `iceland_smumgr.c`, boot/probe on an Iceland/SMU 7.1.1 GPU, successful SMU firmware load and response polling, ROM reads through `vi.c`, PowerPlay DPM table programming, thermal/fan telemetry sanity, suspend/resume with power-gating state intact, and register-trace comparison against known-good SMU 7.1.1 hardware documentation. Static checks should ensure this header is paired with `smu_7_1_1_sh_mask.h` and not substituted with adjacent SMU 7.1.x variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_1_d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_1_enum.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_1_enum.h

### Purpose
`smu_7_1_1_enum.h` is the generated value-enumeration contract for SMU 7.1.1 and related AMD GPU register fields. It assigns stable numeric encodings to SMC firmware messages, ROM/header constants, tiling and memory-layout modes, debug block IDs, color/depth/surface formats, cache policy values, memory types, and performance monitor modes.

### Important APIs, Types, And Functions
The file defines 51 scalar `#define` constants and 59 C `typedef enum` types behind `SMU_7_1_1_ENUM_H`. Important defines include SRBM/RCU/SFP/SAMU/SMU key-chain range constants, SMC mailbox command IDs such as `SMC_MSG_TEST`, `SMC_MSG_CONFIG_LCLK_DPM`, `SMC_MSG_CONFIG_THERMAL_CNTL`, `SMC_MSG_EN_PM_CNTL`, `SMC_MSG_RESET`, and `SMC_MSG_VOLTAGE`, plus `SMC_VERSION_MAJOR`, `SMC_VERSION_MINOR`, `SMC_HEADER_SIZE`, and `ROM_SIGNATURE`. Important enum groups cover endian and array modes (`SurfaceEndian`, `ArrayMode`), memory tiling geometry (`PipeTiling`, `BankTiling`, `RowTiling`, `TileSplit`, `PipeConfig`, `NumBanks`, `BankWidth`, `BankHeight`, `MacroTileAspect`), debug routing (`DebugBlockId`, `DebugBlockId_OLD`, and BY2/BY4/BY8/BY16 compressed variants), render/depth formats (`DepthFormat`, `ZFormat`, `StencilFormat`, `CmaskMode`, `ColorFormat`, `SurfaceFormat`, `BUF_DATA_FORMAT`, `IMG_DATA_FORMAT`, numeric format enums), cache/memory policy (`GATCL1RequestType`, `TCC_CACHE_POLICIES`, `MTYPE`), performance monitoring (`PERFMON_COUNTER_MODE`, `PERFMON_SPM_MODE`), and surface array shape (`SurfaceTiling`, `SurfaceArray`, `ColorArray`, `DepthArray`, `ENUM_NUM_SIMD_PER_CU`).

### Control Flow
There is no executable control flow in this file. Its values become control inputs when other driver or firmware-interface code writes register fields, encodes SMC mailbox commands, decodes ROM or firmware metadata, configures tiling, or selects debug/performance blocks. In this local tree, direct textual inclusion of `smu_7_1_1_enum.h` was not found outside the header itself, but the enum layout mirrors neighboring generated ASIC enum headers and supplies the same kind of constants expected by generated register-field users.

### State, Persistence, And Dependencies
The header has no mutable state and performs no persistence. The numeric values are persisted indirectly when written into hardware registers, firmware mailboxes, command buffers, or tables interpreted by SMU/GPU blocks. It depends only on C enum/preprocessor semantics, but it is semantically coupled to `smu_7_1_1_d.h` for register addresses and `smu_7_1_1_sh_mask.h` for masks/shifts. It is also coupled to firmware ABI expectations for SMC message IDs and to graphics memory-layout ABI expectations for tiling and format encodings.

### Integration Points
SMC message defines integrate with mailbox registers declared in `smu_7_1_1_d.h` (`mmSMC_MESSAGE_*`, `mmSMC_RESP_*`, and `mmSMC_MSG_ARG_*`) and with PowerPlay/SMU manager logic that sends firmware commands. Tiling and format enums align with AMDGPU address-library, graphics, display, and buffer/image programming concepts, even when this exact header is not directly included by a local C file. Debug block IDs integrate with debug/perf register programming, and `PERFMON_*` values provide legal modes for performance counter setup.

### Risks
The critical risk is ABI mismatch. If an SMC message ID does not match firmware, the driver can issue the wrong firmware command or wait for a response that never arrives. If tiling, pipe, bank, format, or memory-type enum values drift from hardware, surfaces can be laid out incorrectly, producing rendering corruption, memory faults, or cache coherency failures. The debug block ID tables are large and include legacy/compressed variants, so using the wrong variant can route debug/perf requests to the wrong block. Because many values are shared-looking across ASIC headers, accidental cross-ASIC reuse may compile cleanly while programming invalid encodings.

### Test Signals
Useful test signals include compilation of any code that consumes generated enum headers, firmware mailbox tests for SMC commands and expected responses, DPM/thermal/power feature enablement on SMU 7.1.1 hardware, graphics tests that exercise linear/tiled/depth/color/compressed formats, display scanout from tiled surfaces, debug/perf counter routing tests for representative `DebugBlockId` values, and trace comparison of programmed field values against hardware specification fixtures. Static checks should compare enum names and numeric values against generated source data and adjacent SMU 7.1.x headers where deliberate ASIC differences are documented.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_1_enum.h -->
