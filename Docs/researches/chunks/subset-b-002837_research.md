# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_offset.h lines 1-2477

## Purpose

This chunk is the opening portion of the generated AMDGPU MMHUB 9.4.1 register-offset header. It provides C preprocessor constants for MMHUB hardware register addresses and their SOC15 base-index selector values. The matching `mmhub_9_4_1_sh_mask.h` header defines bit layouts inside those registers; this offset header names the registers and gives the numeric offsets used by SOC15 register access helpers.

The covered range defines the include guard and the first 1,212 register offsets, plus 1,211 matching `_BASE_IDX` constants. The hardware blocks covered here are:

- `mmhub_dagb_dagbdec0` through `mmhub_dagb_dagbdec4`, base addresses `0x68000`, `0x68200`, `0x68400`, `0x68600`, and `0x68800`.
- `mmhub_ea_mmeadec0` and `mmhub_ea_mmeadec1`, base addresses `0x68a00` and `0x68f00`.
- The beginning of `mmhub_ea_mmeadec2`, base address `0x69400`, ending in this chunk at `mmMMEA2_ADDRDEC0_COL_SEL_LO_CS23`.

The file has no executable code, type definitions, or data storage. Its job is to make generated ASIC register names available to AMDGPU MMHUB v9.4 code at compile time.

## Important APIs, Types, And Macros

The public surface is entirely macro definitions:

- Include guard: `_mmhub_9_4_1_OFFSET_HEADER`.
- Register offset macros: `mm<REGISTER_NAME>` with a hexadecimal register offset.
- Register base selector macros: `mm<REGISTER_NAME>_BASE_IDX`, all equal to `1` in this chunk.

The `DAGB` decoder blocks are mechanically repeated for `DAGB0` through `DAGB4`. Each complete block contains 126 register offsets in a `0x80`-wide range. `DAGB0` spans `0x0000..0x007f`, `DAGB1` spans `0x0080..0x00ff`, `DAGB2` spans `0x0100..0x017f`, `DAGB3` spans `0x0180..0x01ff`, and `DAGB4` spans `0x0200..0x027f`. The repeated families include:

- Read-client and write-client entries: `mmDAGB*_RDCLI0..15` and `mmDAGB*_WRCLI0..15`.
- Read/write global controls: `RD_CNTL`, `WR_CNTL`, `RD_GMI_CNTL`, `WR_GMI_CNTL`, `RD_ADDR_DAGB`, `WR_ADDR_DAGB`, and `WR_DATA_DAGB`.
- Clock-gating controls: `RD_CGTT_CLK_CTRL`, `WR_CGTT_CLK_CTRL`, `L1TLB_*_CGTT_CLK_CTRL`, and `ATCVM_*_CGTT_CLK_CTRL`.
- Burst and lazy-timer controls for read address, write address, write data, and output paths.
- Virtual-channel controls: `RD_VC0_CNTL..RD_VC7_CNTL` and `WR_VC0_CNTL..WR_VC7_CNTL`.
- Credit and pending-status registers: TLB/data/misc credits, `RDCLI_*_PENDING`, `WRCLI_*_PENDING`, FIFO empty/full, and read/write credit-full status.
- Coherency override registers: `WRCLI_GPU_SNOOP_OVERRIDE` and `WRCLI_GPU_SNOOP_OVERRIDE_VALUE`.
- Diagnostics and counters: `DAGB_DLY`, `CNTL_MISC`, `CNTL_MISC2`, `PERFCOUNTER_LO`, `PERFCOUNTER_HI`, `PERFCOUNTER0_CFG`, `PERFCOUNTER1_CFG`, `PERFCOUNTER2_CFG`, `PERFCOUNTER_RSLT_CNTL`, and reserved slots.

The `MMEA` address-decode blocks are also repeated, with complete blocks for `MMEA0` and `MMEA1`. Each complete block has 233 register offsets. `MMEA0` spans `0x0280..0x0394`, and `MMEA1` spans `0x03c0..0x04d4`. These blocks include:

- DRAM, GMI, and IO client-to-group and group-to-virtual-channel maps.
- DRAM, GMI, and IO lazy timers, CAM controls, page-burst controls, priority aging, priority queuing, fixed priority, urgency, urgency masking, and priority quantum registers.
- Address normalization ranges: `ADDRNORM_BASE_ADDR*`, `ADDRNORM_LIMIT_ADDR*`, offset registers, DRAM/GMI hole controls, and non-power-of-two channel configuration.
- Address decoder controls: bank configuration, hash selection for DRAM/GMI banks, PC, chip-select fields, harvest enable, and per-address-decoder chip-select base/mask/config/select/column/rank-map registers.
- MAM client-to-group maps, MAM group-to-virtual-channel maps, MAM priority controls, and MAM D0-D3 memory controls.
- SDP arbitration and resource controls: `SDP_ARB_DRAM`, `SDP_ARB_GMI`, `SDP_ARB_FINAL`, per-target priorities, credits, tag/VCC/VCD reserves, and `SDP_REQ_CNTL`.
- Miscellaneous observability and reliability registers: `MISC`, `LATENCY_SAMPLING`, performance counters, `EDC_CNT`, `EDC_CNT2`, `EDC_CNT3`, DSM controls, `CGTT_CLK_CTRL`, `EDC_MODE`, `ERR_STATUS`, `MISC2`, and `ADDRDEC_SELECT`.

The `MMEA2` block begins at `0x0500` and this chunk covers 115 offsets through the early `ADDRDEC0` column-select registers. The rest of `MMEA2`, plus later `MMEA3..7` and VM/L2/L1 register families, are outside this chunk.

## Control Flow

There is no runtime control flow in this header. Control flow is created by AMDGPU code that includes the header and passes these macros into SOC15 register helpers. The relevant consumer is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c`, which includes:

- `mmhub/mmhub_9_4_1_offset.h`
- `mmhub/mmhub_9_4_1_sh_mask.h`
- `mmhub/mmhub_9_4_1_default.h`

Typical use follows this pattern:

1. Driver code names a register with a macro from this file, for example `mmDAGB0_WRCLI_GPU_SNOOP_OVERRIDE`, `mmDAGB0_CNTL_MISC2`, or `mmMMEA0_EDC_CNT`.
2. SOC15 helper macros combine the offset with the `MMHUB` IP block, instance number, and base-index information.
3. Read/write helpers such as `RREG32_SOC15_OFFSET()`, `WREG32_SOC15_OFFSET()`, `SOC15_REG_ENTRY()`, `SOC15_REG_ENTRY_OFFSET()`, and `SOC15_REG_FIELD()` access the hardware register or describe it for RAS handling.
4. If fields are manipulated, the paired shift/mask header supplies `REG_SET_FIELD()`, `REG_GET_FIELD()`, or direct mask operands.

Two concrete control patterns depend on the offsets in this chunk:

- `mmhub_v9_4_init_snoop_override_regs()` computes the distance between `mmDAGB1_WRCLI_GPU_SNOOP_OVERRIDE` and `mmDAGB0_WRCLI_GPU_SNOOP_OVERRIDE`, then iterates over DAGB instances to set SDMA GPU snoop override bits. The fixed `0x80` spacing between DAGB blocks is part of that contract.
- `mmhub_v9_4_update_medium_grain_clock_gating()` computes the distance between `mmDAGB1_CNTL_MISC2` and `mmDAGB0_CNTL_MISC2`, then toggles clock-gating disable bits over the DAGB instances using offsets from this header and masks from the shift/mask header.

## State And Persistence Behavior

The header itself is stateless. It persists only as source metadata compiled into register access expressions. The state described by these offsets lives in MMHUB hardware registers:

- DAGB arbitration and flow-control state for read/write clients, virtual channels, maximum burst sizes, lazy timers, pending request status, credits, and FIFO state.
- DAGB clock and power control state through CGTT and `CNTL_MISC2` registers.
- DAGB coherency override state, notably SDMA-related write-client GPU snoop override configuration.
- MMEA memory-address routing state for DRAM, GMI, IO, and MAM paths.
- MMEA address normalization and address-decoder state that maps memory addresses onto banks, pseudo-channels, chip selects, harvested channels, and memory-controller layout.
- MMEA SDP arbitration, priority, credit, reserve, and request-control state.
- MMEA reliability and diagnostics state, including EDC counters, error status, DSM controls, latency sampling, and performance counters.

Values written to these hardware registers persist until reset, reprogramming, power-state transitions, firmware/hardware ownership changes, or device removal. Driver initialization, GART enablement, reset recovery, suspend/resume, RAS query/reset, and clock-gating transitions must assume that MMHUB state can need reprogramming or rereading after those events.

## Dependencies And Integration Points

Primary dependencies:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c` is the direct MMHUB 9.4 consumer.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h` supplies matching bit shifts and masks for the registers named here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_default.h` supplies matching default values.
- SOC15 access infrastructure in `soc15.h` and `soc15_common.h` interprets the `mm*` offsets and `_BASE_IDX` constants.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c` selects `mmhub_v9_4_funcs`/RAS hooks for applicable devices and contains related golden-register programming for DAGB/MMEA names in the broader GMC v9 code.

Important integration details:

- The `DAGB` block spacing is used arithmetically by the driver. If any offset drifted from the generated `0x80` spacing, loops that program multiple DAGB instances would access the wrong registers.
- `mmhub_v9_4.c` uses `MMHUB_NUM_INSTANCES` and `MMHUB_INSTANCE_REGISTER_OFFSET` for hub instances, while this header supplies offsets inside a hub instance.
- RAS support in `mmhub_v9_4.c` builds `soc15_reg_entry` arrays for `MMEA*_EDC_CNT`, `MMEA*_EDC_CNT2`, `MMEA*_EDC_CNT3`, and `MMEA*_ERR_STATUS`; this chunk provides the complete `MMEA0` and `MMEA1` offsets and only the early part of `MMEA2`.
- Register names are generated from AMD hardware specifications and are internal kernel-driver ABI, not userspace ABI.

## Risks And Edge Cases

- Cross-generation mismatch: these offsets must be paired with the MMHUB 9.4.1 shift/mask/default headers. Combining offsets from this header with masks from another ASIC generation can compile but access or program the wrong hardware fields.
- Arithmetic spacing dependency: code derives per-instance distances from `DAGB1 - DAGB0` offsets. Mechanical changes to only one repeated block would break all looped DAGB programming.
- Base-index risk: every `_BASE_IDX` in this chunk is `1`. Changing base-index values without corresponding SOC15 table changes would redirect register accesses even if offsets remain correct.
- Partial block boundary: this research chunk stops inside `MMEA2`. RAS and address-decoder analysis for `MMEA2` is incomplete until later chunks cover the remaining `MMEA2` registers.
- Hardware-side consequences: incorrect DAGB offsets can affect SDMA coherency, outstanding request limits, clock gating, pending-status reporting, and performance-counter selection. Incorrect MMEA offsets can affect memory address decoding, channel/bank hashing, harvested-memory configuration, SDP arbitration, and RAS error reporting.
- Generated-file maintenance risk: the repeated register families make manual edits hard to audit. Regenerating from the authoritative hardware database is safer than hand-editing individual constants.
- Reserved and gap handling: the header includes explicit `RESERVE*` names and also leaves numeric holes in some blocks. Callers should not infer that every missing offset is safe or available.

## Test Signals

Useful validation signals are mostly build-time, register-access, and hardware-behavior checks:

- Compile AMDGPU configurations that include `mmhub_v9_4.c`; unresolved `mmDAGB*` or `mmMMEA*` names indicate offset-header drift.
- Check generated-header consistency: each register offset in this chunk should have the matching `_BASE_IDX` macro, and repeated `DAGB` blocks should preserve the `0x80` stride.
- Exercise GART/MMHUB initialization on MMHUB 9.4 hardware, especially paths that call `mmhub_v9_4_gart_enable()` and then initialize snoop overrides, TLB/cache settings, system domain, VMID configuration, and invalidation.
- Verify SDMA coherency behavior after `mmhub_v9_4_init_snoop_override_regs()`; failures may point at `WRCLI_GPU_SNOOP_OVERRIDE` offsets or block-stride assumptions.
- Validate clock-gating toggles with `mmhub_v9_4_set_clockgating()` and `mmhub_v9_4_get_clockgating()`; incorrect `DAGB*_CNTL_MISC2` offsets should show up as flags not matching hardware state or as register access errors.
- Run RAS query/reset paths for MMHUB v9.4 and confirm `MMEA0`/`MMEA1` EDC counters and error-status registers read coherently.
- Compare against hardware golden settings and generated register dumps when available, especially for `DAGB` client programming and `MMEA` priority/address-decoder state.

## Chunk Scope Notes

This document covers only lines 1-2477 of `mmhub_9_4_1_offset.h`. The source file continues beyond this point with the rest of `MMEA2`, later `MMEA` instances, and additional MMHUB register blocks. The final per-file research document should reconcile this chunk with later chunk documents before drawing conclusions about the complete MMHUB 9.4.1 register map.
