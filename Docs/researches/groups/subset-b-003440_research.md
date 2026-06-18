# Research: subset-b-003440

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_5_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_5_0_sh_mask.h

## Purpose

`uvd_5_0_sh_mask.h` is a generated AMDGPU hardware register field-layout header for the UVD 5.0 video decode block. It contains no executable code; it exports preprocessor constants that describe masks and shifts for the fields inside UVD semaphore, firmware command, tiling/address-configuration, clock/power, local-memory-interface, ring-buffer, VCPU, reset, status, and SUVD/JPEG registers.

The include guard is `UVD_5_0_SH_MASK_H`. The public API is the AMD register convention where `REGISTER__FIELD_MASK` is the already-positioned bit mask and `REGISTER__FIELD__SHIFT` is the matching right-shift amount. The file has 1,019 `#define`s and no functions, structs, enums, or variables.

## Important APIs, Types, And Macros

Important macro families include:

- `UVD_SEMA_*`: semaphore address, command, VMID enable, VMID, request command, write phase, timeout, and control fields.
- `UVD_GPCOM_VCPU_*`: firmware/VCPU command mailbox fields, including `CMD_SEND`, command payload, command source, and two 32-bit data registers.
- `UVD_UDEC_*`, `UVD_MIF_*`, and `UVD_JPEG_ADDR_CONFIG`: address swizzle and tiling geometry fields such as pipe count, pipe interleave size, bank interleave, shader engine count, shader-engine tile size, multi-GPU tile size, row size, and lower-pipe count.
- `UVD_CGC_*`, `UVD_CGC_UDEC_STATUS`, `UVD_CGC_MEM_CTRL`, `UVD_CGC_CTRL2`, and `UVD_PGFSM_*`: clock-gating, memory light-sleep, dynamic clock ramp, power-gating state-machine, tile-read, and power-status fields.
- `UVD_LMI_*`: 64-bit BAR split fields, address extension, memory-client coherency, urgent signaling, swap controls, cache controls, VMID routing, and LMI clean/idle status.
- `UVD_MPC_*`: multiplexer, ALU, replacement, average-weight, debug, and urgent fields for the media pipeline controller.
- `UVD_VCPU_*`: VCPU cache offsets/sizes and VCPU control bits for resets, clocks, tracing, timeout behavior, codec enablement, and offload.
- `UVD_SOFT_RESET`: per-subblock reset bits and reset-status bits for RBC, LBSI, LMI, VCPU, UDEC, CSM, CXW, TAP, MPC, IH, MPRD, IDCT, MIF, LCM, SUVD, and clock-domain reset indicators.
- `UVD_RBC_*` and `UVD_STATUS`: ring-buffer controller VMID, IB size, read/write pointers, buffer size/block size, fetch/update controls, read-pointer writeback address, RBC busy state, and VCPU report bits.
- `UVD_SUVD_CGC_*`: secondary UVD/SUVD H.264/HEVC clock-gating and status fields; UVD 5.0 includes additional `SCLR` and `UVD_SC` gate/status/control fields compared with the UVD 6.0 header in this work item.

## Control Flow And Data Flow

This header has no control flow. It participates in driver control flow as a bitfield contract:

1. Driver code selects a register address from a compatible UVD 5.0 address header.
2. It composes or decodes register values by applying the `*_MASK` and `*__SHIFT` constants.
3. MMIO or indexed-register helpers read and write the UVD hardware registers.
4. Hardware updates stateful fields such as ring pointers, busy bits, clean/idle bits, timeout latches, and power/reset status.

Representative flows enabled by these fields are semaphore command setup, firmware mailbox submission, VCPU cache window setup, ring-buffer controller initialization, VMID assignment for UVD memory clients, LMI coherency/swap programming, clock-gating/power-gating changes, block reset, and status polling.

## State And Persistence Behavior

The header stores no process or persistent software state. The constants describe persistent hardware state in the GPU. Values written through consumers remain in the UVD block until changed by the driver, firmware, power management, GPU reset, or hardware side effects.

Stateful areas are ring bases and pointers, VCPU cache layout, LMI VMID/cache/coherency/swap state, semaphore timeout latches, clock-gating and memory light-sleep configuration, power-gating FSM state, and soft-reset status. Because these constants define a hardware ABI, an incorrect mask or shift can persist as device misconfiguration until a later corrective write or reset.

## Dependencies And Integration Points

The file depends only on the C preprocessor. It is normally paired with a matching UVD 5.0 register-address header and with AMDGPU register access helpers such as MMIO read/modify/write code.

Integration points include AMDGPU UVD initialization, firmware boot and command submission, ring setup for decode jobs, semaphore synchronization, power-management and clock-gating code, GPU reset paths, memory-controller coherency programming, VMID routing for internal UVD clients, JPEG/SUVD decode support, and generated-register synchronization tooling.

## Risks And Edge Cases

- Manual edits are high risk because compile-time checks rarely prove that a mask still targets the intended hardware bit.
- Many fields are full-width address or data slices; consumers must preserve alignment and high/low word ordering for 64-bit BARs and ring addresses.
- Reset, clock, power, and cache-coherency fields have ordering requirements not encoded in this header.
- Timeout/status/clear fields may have write-one-to-clear or latch semantics defined outside this file.
- UVD 5.0 and UVD 6.0 masks are very similar but not identical; generation drift around SUVD `SCLR`/`UVD_SC`, VMID, and power/MIF fields can break one ASIC generation while appearing correct for another.
- Reserved or `RFU` fields should not be set opportunistically.

## Test Signals

Useful validation signals are AMDGPU builds for ASICs using UVD 5.0, register-generation diffs against AMD's canonical database, boot/probe on matching GPUs, firmware loading and VCPU boot, UVD decode ring submission, semaphore wait/signal timeout behavior, suspend/resume and GPU reset tests, clock/power-gating transitions, LMI cache/coherency tests, JPEG/SUVD codec paths, and VMID/isolation checks for internal UVD memory clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_5_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_6_0_d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_6_0_d.h

## Purpose

`uvd_6_0_d.h` is a generated AMDGPU register-address header for the UVD 6.0 video decode block. It exports symbolic MMIO offsets (`mmUVD_*`) and indexed-register offsets (`ixUVD_*`) used by driver code to program UVD semaphores, firmware mailboxes, ring buffers, local memory interface, clock/power management, VCPU cache, resets, status, and JPEG/SUVD address configuration.

The include guard is `UVD_6_0_D_H`. The file contains 107 `#define`s and no executable logic, functions, structs, enums, or mutable state.

## Important APIs, Types, And Macros

The address surface includes:

- Semaphore and firmware mailbox registers: `mmUVD_SEMA_ADDR_LOW`, `mmUVD_SEMA_ADDR_HIGH`, `mmUVD_SEMA_CMD`, `mmUVD_GPCOM_VCPU_CMD`, `mmUVD_GPCOM_VCPU_DATA0`, and `mmUVD_GPCOM_VCPU_DATA1`.
- Core control and tiling registers: `mmUVD_ENGINE_CNTL`, `mmUVD_UDEC_ADDR_CONFIG`, `mmUVD_UDEC_DB_ADDR_CONFIG`, `mmUVD_UDEC_DBW_ADDR_CONFIG`, `mmUVD_JPEG_ADDR_CONFIG`, and MIF address config registers.
- Ring-buffer and BAR registers: `mmUVD_RB_BASE_LO/HI`, `mmUVD_RB_SIZE`, `mmUVD_RB_RPTR`, `mmUVD_RB_WPTR`, second and third ring variants, LMI RBC ring/IB 64-bit BAR high/low registers, and VCPU cache 64-bit BAR high/low registers.
- Clock and power registers: `mmUVD_CGC_GATE`, `mmUVD_CGC_STATUS`, `mmUVD_CGC_CTRL`, `mmUVD_CGC_UDEC_STATUS`, `mmUVD_SUVD_CGC_*`, `mmUVD_PGFSM_CONFIG`, `mmUVD_PGFSM_READ_TILE1` through tile 7, `mmUVD_POWER_STATUS`, and `mmUVD_POWER_STATUS_U`.
- LMI and memory-routing registers: `mmUVD_LMI_CTRL`, `mmUVD_LMI_CTRL2`, `mmUVD_LMI_STATUS`, `mmUVD_LMI_ADDR_EXT`, `mmUVD_LMI_SWAP_CNTL`, `mmUVD_MP_SWAP_CNTL`, and indexed VMID/cache/swap/address-extension registers.
- VCPU, reset, and status registers: `mmUVD_VCPU_CACHE_OFFSET*`, `mmUVD_VCPU_CACHE_SIZE*`, `mmUVD_VCPU_CNTL`, `mmUVD_SOFT_RESET`, `mmUVD_STATUS`, `mmUVD_CONTEXT_ID`, and semaphore timeout-control/status registers.

## Control Flow And Data Flow

This file has no runtime control flow. Driver code uses these address constants with field masks from `uvd_6_0_sh_mask.h`:

1. Select an `mmUVD_*` or `ixUVD_*` offset for the desired register.
2. Compose a value using the matching mask/shift macros.
3. Access the register through MMIO or the indexed-register accessor.
4. Poll, submit, reset, or power-manage the UVD block based on the hardware response.

The address ordering reflects common initialization flow: configure semaphores and address swizzles, set up ring/BAR/cache memory windows, program LMI and VMID routing, enable clocks/power, boot or command the VCPU, then monitor ring/status/timeout registers during job execution and reset.

## State And Persistence Behavior

The header itself has no storage. Each macro names a hardware register whose contents persist in the GPU until changed by software, firmware, reset, or power-management hardware. Stateful areas include firmware mailbox contents, ring buffer bases/sizes/pointers, VCPU cache regions, LMI coherency and VMID routing, clock-gating and power-gating state, context IDs, timeout latches, and reset/status bits.

## Dependencies And Integration Points

The file depends only on the C preprocessor. It is integrated with `uvd_6_0_sh_mask.h`, `uvd_6_0_enum.h`, AMDGPU MMIO/indexed-register helpers, UVD firmware loading and command paths, decode ring management, power-management code, reset code, and memory-management/VMID setup for internal UVD clients.

## Risks And Edge Cases

- Offsets must match the UVD 6.0 hardware generation; using UVD 5.0 or 7.0 offsets with UVD 6.0 field masks can write the wrong register.
- `mm*` and `ix*` offsets require different accessor paths. Mixing them is a real integration risk.
- The header does not encode access semantics such as read-only, write-only, write-one-to-clear, latch-on-read, sequencing, or polling delays.
- Ring and BAR registers are split into high/low words and need correct ordering and address alignment.
- Power-gating and soft-reset registers can disrupt active decode jobs if written outside the expected quiesce/reset flow.

## Test Signals

Validation should include AMDGPU compile coverage for UVD 6.0, register-database diffs, successful GPU probe and UVD firmware boot, decode job submission through all supported rings, semaphore timeout behavior, suspend/resume and power-gating tests, GPU reset recovery, LMI coherency checks, and coverage for both MMIO and indexed-register access paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_6_0_d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_6_0_enum.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_6_0_enum.h

## Purpose

`uvd_6_0_enum.h` is a generated enum catalog for UVD 6.0 and related AMDGPU register programming. It gives symbolic names to firmware command opcodes, debug block identifiers, surface tiling/addressing modes, color/depth/buffer/image formats, cache policies, memory types, performance monitor modes, and memory power-control states. It contains 64 `typedef enum` declarations and no functions or state.

The include guard is `UVD_6_0_ENUM_H`. Although it lives under the UVD register directory, many enum groups are generic AMD GPU register values used by multiple blocks when programming address, texture, render, cache, debug, and perf fields.

## Important APIs, Types, And Macros

Important exported enum types include:

- `UVDFirmwareCommand`: firmware command IDs such as fence, trap, decoded address, macroblock address, IT buffer, display address/pitch/tiling, bitstream address/size, and end-of-decode.
- `DebugBlockId` plus `_BY2`, `_BY4`, `_BY8`, and `_BY16` variants: numeric debug-block selectors for VMC, SRBM/GRBM, IH, UVD, SDMA, CP, shader, texture, cache, color/depth backend, TCP/TCC, LDS, and reserved slots at different granularity.
- Surface/addressing enums: `SurfaceEndian`, `ArrayMode`, `PipeTiling`, `BankTiling`, `GroupInterleave`, `RowTiling`, `BankSwapBytes`, `SampleSplitBytes`, `NumPipes`, `PipeInterleaveSize`, `BankInterleaveSize`, `NumShaderEngines`, `ShaderEngineTileSize`, `NumGPUs`, `MultiGPUTileSize`, `RowSize`, and `NumLowerPipes`.
- Format enums: `ColorTransform`, `CompareRef`, `ReadSize`, `DepthFormat`, `ZFormat`, `StencilFormat`, `CmaskMode`, `QuadExportFormat`, `QuadExportFormatOld`, `ColorFormat`, `SurfaceFormat`, `BUF_DATA_FORMAT`, `IMG_DATA_FORMAT`, `BUF_NUM_FORMAT`, and `IMG_NUM_FORMAT`.
- Tiling detail enums: `TileType`, `NonDispTilingOrder`, `MicroTileMode`, `TileSplit`, `SampleSplit`, `PipeConfig`, `NumBanks`, `BankWidth`, `BankHeight`, and `MacroTileAspect`.
- Cache, memory, perf, and power enums: `GATCL1RequestType`, `TCC_CACHE_POLICIES`, `MTYPE`, `PERFMON_COUNTER_MODE`, `PERFMON_SPM_MODE`, `SurfaceTiling`, `SurfaceArray`, `ColorArray`, `DepthArray`, `ENUM_NUM_SIMD_PER_CU`, `MEM_PWR_FORCE_CTRL`, `MEM_PWR_FORCE_CTRL2`, `MEM_PWR_DIS_CTRL`, `MEM_PWR_SEL_CTRL`, and `MEM_PWR_SEL_CTRL2`.

## Control Flow And Data Flow

This header has no control flow. Consumers use these enum constants as named values when populating fields defined in mask headers or packet/register structures. Data flow is value-oriented:

1. Higher-level driver code chooses a semantic value, for example a firmware command, tiling mode, surface format, cache policy, perf counter mode, or memory power request.
2. The enum value is shifted and masked into a register field or compared with a decoded hardware field.
3. Hardware or firmware interprets the numeric value according to the ASIC programming contract.

For UVD-specific paths, `UVDFirmwareCommand` is the clearest integration point: it maps software command intent into the firmware command protocol used by the UVD VCPU mailbox/ring logic.

## State And Persistence Behavior

The enum declarations hold no runtime state. Persistence happens only when an enum value is written into a hardware register, firmware command stream, descriptor, or context. Once written, the chosen numeric value can affect persistent hardware state such as tiling interpretation, format interpretation, memory routing, power-control mode, cache behavior, or debug/performance muxing.

## Dependencies And Integration Points

This file has no include dependencies beyond the C compiler's enum support. Integration points include UVD firmware command submission, register field composition with `uvd_6_0_sh_mask.h`, GPU address-library or tiling setup code, memory-management and cache-policy code, debug block selection, performance-monitor setup, and power-management code.

## Risks And Edge Cases

- Enum numeric values are hardware ABI values. Renumbering or pruning "reserved" entries can break binary register programming even if C compilation still succeeds.
- The debug block ID tables are long and contain many reserved/unused names. Consumers must pick the variant that matches the target register field width/granularity.
- Some enum names are generic and may collide semantically with similar names from other ASIC generations if headers are mixed.
- Format and tiling enums must match the mask field widths in the consumer registers; out-of-range values may be truncated.
- Reserved values should not be used unless required by a hardware workaround or documented programming sequence.

## Test Signals

Useful validation includes compile coverage for all UVD 6.0 consumers, static or generated diffs against AMD's enum database, firmware command tests that exercise fences/traps/EOD and bitstream/display address commands, decode tests using tiled and linear surfaces, format compatibility tests, debug/perf selector smoke tests, and power-management tests that confirm memory power force/select values produce expected transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_6_0_enum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_6_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_6_0_sh_mask.h

## Purpose

`uvd_6_0_sh_mask.h` is the generated field mask/shift companion to the UVD 6.0 address header. It describes the bit layout of UVD 6.0 registers for semaphores, VCPU command mailboxes, decode address configuration, clock/power gating, local memory interface, media pipeline controls, VCPU control, soft reset, ring-buffer controller, status, timeout handling, SUVD/JPEG, VMID routing, cache control, and MIF/JPEG address configuration.

The include guard is `UVD_6_0_SH_MASK_H`. The file has 1,007 `#define`s and exports no functions, structs, enums, or variables.

## Important APIs, Types, And Macros

Major macro groups are:

- `UVD_SEMA_ADDR_LOW/HIGH`, `UVD_SEMA_CMD`, `UVD_SEMA_CNTL`, and timeout registers: semaphore address, command, phase, mode, VMID, enable, timeout counter, resend timer, status, and clear fields.
- `UVD_GPCOM_VCPU_CMD/DATA*` and `UVD_ENGINE_CNTL`: firmware command send/source/payload and engine start controls.
- `UVD_UDEC_ADDR_CONFIG`, `UVD_UDEC_DB_ADDR_CONFIG`, `UVD_UDEC_DBW_ADDR_CONFIG`, `UVD_MIF_*_ADDR_CONFIG`, and `UVD_JPEG_ADDR_CONFIG`: repeated tiling/address-geometry fields.
- `UVD_CGC_GATE`, `UVD_CGC_STATUS`, `UVD_CGC_CTRL`, `UVD_CGC_UDEC_STATUS`, `UVD_CGC_MEM_CTRL`, `UVD_CGC_CTRL2`, `UVD_SUVD_CGC_*`, `UVD_PGFSM_*`, `UVD_POWER_STATUS`, and `UVD_POWER_STATUS_U`: clock status, gate bits, dynamic clock modes, memory light sleep, power FSM read/write, DPG pause, timeout, and power-gating enable fields.
- `UVD_LMI_*`: 64-bit BAR slices, extension registers, coherency enables, urgent controls, LMI clean/idle state, byte-swap controls, cache enable/flush fields, and internal VMID routing.
- `UVD_MPC_*`: media pipeline multiplexer and ALU controls.
- `UVD_VCPU_CACHE_*`, `UVD_VCPU_CNTL`, `UVD_SOFT_RESET`, `UVD_RBC_*`, `UVD_STATUS`, and `UVD_CONTEXT_ID`: firmware cache layout, VCPU control, per-block reset, ring-buffer controller setup, ring pointer fields, busy/report status, and context IDs.

Compared with the UVD 5.0 mask header in this work item, this UVD 6.0 header has slightly fewer SUVD `SCLR`/`UVD_SC` fields but retains the broader MIF/JPEG address-config and power-status coverage.

## Control Flow And Data Flow

The header has no executable control flow. It supports register programming flows:

1. A driver selects a UVD 6.0 register offset from `uvd_6_0_d.h`.
2. Values are encoded with this header's `*_MASK` and `*__SHIFT` constants.
3. MMIO or indexed access writes the value or reads back status.
4. Higher-level code polls busy/clean/power/reset bits or sends firmware/ring commands.

The data flow covers decode-ring setup, command mailbox submission, VCPU cache window programming, LMI address extension and VMID routing, cache flush/coherency behavior, clock/power changes, reset sequencing, semaphore waits/signals, and status reporting.

## State And Persistence Behavior

This header stores no software state. The hardware fields it describes are stateful: ring pointers and sizes, VCPU cache offsets/sizes, BARs, LMI coherency and VMID state, clock-gating modes, power-gating FSM state, timeout latches, reset bits/status, context IDs, firmware command mailbox values, and UVD busy/report status.

Incorrect masks can alter persistent hardware behavior until reset. Some fields are latched status or clear/ack controls, so consumers need register-specific semantics beyond this file.

## Dependencies And Integration Points

The file depends only on the C preprocessor and is intended to be paired with `uvd_6_0_d.h` and, for symbolic values, `uvd_6_0_enum.h`. Integration points include AMDGPU UVD init, ring and IB submission, firmware command handling, VMID/memory routing, LMI cache/coherency code, clock/power gating, suspend/resume, GPU reset, JPEG/SUVD codec paths, and generated-register validation tooling.

## Risks And Edge Cases

- Masks and shifts are hardware ABI constants; a one-bit error can break decode, memory coherency, power management, or reset recovery.
- Repeated address-config fields look identical across UDEC/MIF/JPEG registers, so consumer code can accidentally program the wrong register with plausible values.
- 64-bit BAR and address-extension fields require correct split-word handling and alignment.
- Reset and clock/power fields must be sequenced with idle polling; the mask header cannot express timing constraints.
- UVD 5.0 and 6.0 field layouts are similar enough to invite accidental cross-generation includes, but not identical.
- VMID and cache-control fields affect memory isolation and coherency.

## Test Signals

Validation signals include AMDGPU build coverage, canonical register diffing, hardware probe on UVD 6.0 ASICs, firmware boot and mailbox command tests, decode ring and IB submission, ring pointer writeback checks, semaphore timeout tests, LMI cache/coherency tests, power-gating and clock-gating transitions, suspend/resume, GPU reset recovery, JPEG/SUVD decode coverage, and VMID routing checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_6_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_7_0_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_7_0_offset.h

## Purpose

`uvd_7_0_offset.h` is a generated UVD 7.0 register-offset header. Unlike the UVD 6.0 `_d.h` file, it uses offset plus base-index pairs: each `mm*` register macro is paired with `mm*_BASE_IDX`, allowing AMDGPU access helpers to combine a block-relative offset with the correct register base. The file defines 187 macros and no functions, structs, enums, or variables.

The include guard is `_uvd_7_0_OFFSET_HEADER`. The comments identify three address blocks: `uvd0_uvd_pg_dec` at base `0x1fb00`, `uvd0_uvdnpdec` at base `0x20000`, and `uvd0_uvddec` at base `0x20c00`.

## Important APIs, Types, And Macros

Important address groups include:

- `uvd0_uvd_pg_dec`: power-gated decode and DPG ring setup registers such as `mmUVD_POWER_STATUS`, `mmUVD_DPG_RBC_RB_CNTL`, DPG ring base high/low, read/write pointers, write-pointer control, DPG VCPU cache BAR high/low, and DPG cache offset.
- `uvd0_uvdnpdec`: non-power-gated decode/JPEG-facing registers such as `mmUVD_JPEG_ADDR_CONFIG`, firmware command mailbox registers, UDEC address configuration, SUVD clock-gating controls, VCPU cache BARs, `mmUVD_POWER_STATUS_U`, no-op, GP scratch, primary and secondary ring base/size/pointers, JRBC read pointer, and LMI RBC/IB 64-bit BARs.
- `uvd0_uvddec`: decode core registers such as `mmUVD_SEMA_CNTL`, JRBC BAR/write pointer, third ring buffer, JPEG/UVD clock gating, context index/data, GP scratch, LMI controls, master interrupt enable, firmware status, VM control, swap controls, MPC controls, VCPU cache layout, VCPU control, soft reset, RBC IB/RB controls, status, semaphore timeout controls, and `mmUVD_CONTEXT_ID`/`mmUVD_CONTEXT_ID2`.
- Every register has a corresponding `_BASE_IDX` macro, and all observed base index values are `1` in this file.

## Control Flow And Data Flow

The header has no runtime control flow. Consumers use it as address data:

1. Select a UVD 7.0 register offset and its `_BASE_IDX`.
2. Use AMDGPU register access helpers that understand offset/base-index addressing.
3. Combine with matching UVD 7.0 field masks from companion mask headers.
4. Program power-gated decode state, firmware mailboxes, rings, LMI, clocks, interrupts, reset, and status polling.

The block split is important to runtime flow. DPG-specific registers support dynamic power-gated ring operation; non-power-gated decode registers host mailbox and shared ring/BAR setup; decode-core registers manage semaphores, LMI, VCPU, interrupts, and reset/status.

## State And Persistence Behavior

This header stores no software state. The offsets identify persistent hardware registers in the UVD 7.0 block. Hardware state includes DPG ring pointers and bases, VCPU cache BARs and offsets, firmware command mailbox data, UDEC/JPEG address geometry, LMI and VM controls, clock-gating configuration, interrupt enables, VCPU control, soft-reset state, RBC ring state, context IDs, firmware status, and semaphore timeout latches.

## Dependencies And Integration Points

The file depends only on the preprocessor. It integrates with AMDGPU register helpers that use `mmREG` plus `mmREG_BASE_IDX`, UVD 7.0 mask headers, firmware loading and mailbox code, decode ring management, dynamic power-gating support, LMI/VM setup, interrupt handling, JPEG/SUVD paths, reset recovery, and generated ASIC register databases.

## Risks And Edge Cases

- The base-index contract is part of the API. Dropping or mismatching `_BASE_IDX` can access the wrong register aperture even when the offset is correct.
- UVD 7.0 splits registers across address blocks; assuming UVD 6.0 flat offsets can misprogram DPG or decode-core registers.
- DPG ring and power-status registers require power-management sequencing that this header does not encode.
- Ring/BAR high/low registers still require correct split address programming and alignment.
- Interrupt, reset, timeout, and firmware status registers can have side effects or latch/clear semantics outside the offset definitions.
- The presence of new UVD 7.0 registers such as `mmUVD_FW_STATUS`, `mmUVD_LMI_VM_CTRL`, `mmUVD_CONTEXT_ID2`, DPG RBC registers, and JPEG clock-gating registers means older UVD generation assumptions should not be reused blindly.

## Test Signals

Validation signals include AMDGPU compile coverage for UVD 7.0, generated-register diffing, hardware probe on UVD 7.0 GPUs, UVD firmware boot and `mmUVD_FW_STATUS` checks, DPG ring setup and pause/resume behavior, decode and JPEG submission tests, interrupt delivery, LMI/VM setup and coherency checks, suspend/resume with power gating, GPU reset recovery, and register-access tests that verify base-index addressing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_7_0_offset.h -->
