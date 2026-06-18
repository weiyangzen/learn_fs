# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h - subset-b-002023

## Scope

- Chunk id: `subset-b-002023`
- Source lines: 5158-7651
- Source file: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h`
- Observed content: 2,494 generated header lines covering 24 address-block comments, 1,200 register-offset macros, and 1,200 matching `_BASE_IDX` macros.

This chunk is part of the generated AMD DCN 3.2.1 register-offset header. It has no executable C logic; it publishes MMIO register offsets and base-index selectors for DCN321 display blocks. The slice starts at MPCC OGAM instance 1, covers OGAM instances 1-3, MPCC MCM instances 0-3, MPC OCSC, ABM instances 0-3, OPP/DPG/FMT/OPPBUF/OPP pipe CRC instances 0-2, and ends at the first `FMT2` register.

## Purpose

The chunk provides symbolic register-address constants used by the AMDGPU display core to construct per-ASIC register tables. Each hardware register has two generated macros:

- `reg...`: the register's offset within the DCN register aperture.
- `reg..._BASE_IDX`: an index into `ctx->dcn_reg_offsets[]`, allowing the same source-level register list macros to resolve to ASIC-specific segment bases.

At runtime, DCN321 resource creation includes this header and combines the offset and base-index macros through helpers such as `SRI`, `SRII`, and `REG`. For example, `dcn321_resource.c` includes `dcn_3_2_1_offset.h` and `dcn_3_2_1_sh_mask.h`; `dcn321_mpc_create()` expands `dcn_mpc_regs_init()`, and `dcn321_opp_create()` expands `opp_regs_init()` for OPP instances. The effect is that shared DCN32 MPC/OPP/ABM code can call register helpers without hard-coding DCN321 addresses.

## Important APIs, Types, and Macros

There are no functions, structs, enums, or storage definitions in this chunk. Its public API is the generated preprocessor namespace:

- `regMPCC_OGAM1_*`, `regMPCC_OGAM2_*`, and `regMPCC_OGAM3_*`: 88 registers per instance for output gamma on MPCC pipes. These include `MPCC_OGAM_CONTROL`, LUT index/data/control registers, RAM A and RAM B start/end/offset/region programming registers for B/G/R channels, gamut remap control/mode, and matrix coefficient registers `C11_C12` through `C33_C34` for banks A and B.
- `regMPCC_MCM0_*` through `regMPCC_MCM3_*`: 139 registers per instance for multi-color management. Each instance includes shaper control/offset/scale/LUT programming, shaper RAM A/B region registers, 3D LUT mode/index/data/control/output normalization/offset registers, 1D LUT control/index/data/control, 1D LUT RAM A/B start/slope/base/end/offset/region registers, and `MPCC_MCM_MEM_PWR_CTRL`.
- `regMPC_OCSC_*`: 69 MPC output color-space-conversion registers. The block includes coefficient-format/mode control plus coefficient registers for banks A and B.
- `regABM0_*` through `regABM3_*`: 60 registers per Adaptive Backlight Management instance. Each instance exposes backlight PWM levels and duty-cycle controls, ABM control, ACE offset/slope and threshold controls, histogram/luma statistic registers, sample-rate registers, histogram-bin shift controls, 24 histogram-result registers, and `DC_ABM1_BL_MASTER_LOCK`.
- `regDPG0_*`, `regDPG1_*`, and `regDPG2_*`: 8 Display Pattern Generator registers per visible instance, including control, ramp control, dimensions, RGB/YCbCr colors, offset/segment, and status.
- `regFMT0_*`, `regFMT1_*`, and the beginning of `regFMT2_*`: formatter clamp, dynamic expansion, control, bit-depth, dither seed, side-by-side stereo, 4:2:0 memory-map, and 4:2:2 control registers. The chunk ends after `regFMT2_FMT_CLAMP_COMPONENT_R`.
- `regOPPBUF0_*` and `regOPPBUF1_*`: output-pixel-processor buffer control and 3D parameter registers.
- `regOPP_PIPE0_OPP_PIPE_CONTROL` and `regOPP_PIPE1_OPP_PIPE_CONTROL`: per-pipe OPP control registers.
- `regOPP_PIPE_CRC0_*` and `regOPP_PIPE_CRC1_*`: OPP pipe CRC control, mask, and result registers.

The base-index pattern is meaningful: the MPC/MPCC and ABM groups in this chunk use base index `3`, while the OPP/DPG/FMT/OPPBUF/CRC groups use base index `2`. Consumers must add the correct base segment before touching hardware.

## Control Flow

This header chunk has no local branches or calls. Runtime flow is supplied by the display-core resource and register-helper layers:

1. DCN321 resource construction includes the generated offset and shift/mask headers.
2. Register-list macros in component headers, such as DCN32 MPC lists, DCN20 OPP lists, and DCN32 ABM lists, are expanded with DCN321's `SRI`/`SRII` helpers.
3. The helpers compute absolute register addresses as `ctx->dcn_reg_offsets[reg..._BASE_IDX] + reg...`.
4. Component constructors store those computed addresses in register tables for MPC, OPP, ABM, and related display blocks.
5. Shared component code later uses `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and wait helpers with the computed register table plus matching field masks/shifts from `dcn_3_2_1_sh_mask.h`.

The register families imply hardware sequencing even though no sequencing is encoded here: LUT programming uses index/data/control patterns; double-buffered gamma and color-management flows select RAM A or RAM B; ABM collects luma/histogram state before programming backlight/PWM responses; OPP DPG/FMT/CRC blocks are configured during test-pattern, mode-set, color-depth, and CRC-capture paths.

## State and Persistence Behavior

The macros themselves are compile-time constants with no storage or persistence. They describe MMIO registers whose state is owned by hardware:

- MPCC OGAM and MCM state persists in hardware registers and LUT RAMs until reset, power-gating, or explicit reprogramming. This includes gamma modes, RAM bank selection, LUT entries, region definitions, shaper LUTs, 3D LUT content, 1D LUT content, gamut remap coefficients, and memory power-control state.
- MPC OCSC state persists as matrix format/mode and coefficient banks. It affects output color-space conversion after pipe composition.
- ABM state includes persistent configuration such as PWM user/current/target levels, duty-cycle limits, ACE thresholds, sample rates, and master locks, plus live or latched telemetry such as luma sums, min/max luma, pixel counts, histogram bins, and read-progress flags.
- OPP state includes formatter clamp/dither/depth and 4:2:0/4:2:2 settings, DPG test-pattern parameters, OPPBUF active/3D geometry, and CRC control/mask state. CRC result registers are readback state produced by the display pipe.
- `_BASE_IDX` constants are not hardware state; they select the base segment used for address translation. A wrong base index would redirect all subsequent register operations for that block.

## Dependencies

This chunk depends on AMDGPU/DC generated-register conventions:

- Matching field layout definitions in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h`.
- DCN321 resource glue in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c`, especially the `BASE`, `SRI`, `SRII`, and `REG` macros that turn these constants into absolute addresses.
- Register-list macros and component structs in DC display code, including DCN32 MPC, DCN20 OPP, and DCN32 ABM definitions.
- The DC context's populated `dcn_reg_offsets[]` table. The generated offsets are relative values and are only valid after adding the correct base segment.
- Low-level AMDGPU MMIO helpers and display-core register access macros that expect the `regNAME` and `regNAME_BASE_IDX` naming convention.

The header is generated data, not a hand-authored API. Correctness depends on the hardware register database, generator, offset header, shift/mask header, and component register lists staying in lockstep.

## Integration Points

Primary integration points are:

- `dcn321_resource.c`: includes this header and initializes register tables for DCN321 resource objects. `dcn321_mpc_create()` builds the MPC register table used by `dcn32_mpc_construct()`, while `dcn321_opp_create()` builds OPP register tables for OPP instances 0-3. ABM register arrays are also initialized through DCN32 ABM register-list macros.
- `dc/mpc/dcn32/dcn32_mpc.c`: consumes MPCC MCM and OGAM addresses to control LUT memory power, program shaper LUTs, program 1D LUTs, program 3D LUTs, and manage color/gamut remap behavior.
- `dc/opp/dcn10` and `dc/opp/dcn20`: consume FMT, DPG, OPPBUF, and OPP pipe CRC addresses for clamping, dither/bit-depth behavior, test-pattern generation, 3D output buffering, CRC capture, and state readback.
- `dc/dce/dmub_abm_lcd.c` and ABM resource/hwseq paths: use ABM register addresses for histogram/luma setup, PWM/backlight level tracking, ABM pipe binding, and DMUB-managed backlight commands.
- User-visible display flows: mode sets, color-management updates, HDR/color-space programming, panel self-refresh/backlight behavior, debug test patterns, and CRC validation all depend on these offsets being correct for DCN321 hardware.

## Risks and Edge Cases

- Offset drift is high impact. A one-register error in an OGAM/MCM LUT, ABM PWM register, FMT register, or CRC result register can silently program the wrong hardware and produce color corruption, broken backlight behavior, invalid CRCs, or display instability.
- The base-index value is as important as the offset. MPC/ABM blocks in this chunk use base index `3`, while OPP-related blocks use base index `2`; swapping these would address a different register aperture even if the relative offset is correct.
- The chunk starts after OGAM instance 0 and ends in the middle of the FMT2 block. Final per-file analysis must merge adjacent chunks before making complete claims about all instances.
- Repeated register families invite copy/paste mistakes. OGAM1-3, MCM0-3, ABM0-3, and OPP instances have very similar names but different offsets and base-address comments.
- LUT and matrix programming has ordering requirements outside this header. Index/data/control registers must be used in the sequence expected by hardware; this file only gives addresses.
- ABM telemetry registers and read-progress flags can be live or latched. Consumers need to honor existing read/clear/update semantics to avoid stale histogram/luma data or missed-frame indicators.
- OPP CRC result registers are diagnostic outputs, not configuration. Code must avoid treating them like ordinary writable controls.
- Generated headers can compile successfully while still being semantically wrong for a new ASIC stepping. Hardware validation is required in addition to build coverage.

## Test Signals

Useful validation signals for consumers of this chunk include:

- Build coverage for DCN321 resource construction and every register-list macro that references OGAM, MCM, ABM, DPG, FMT, OPPBUF, OPP pipe, and CRC registers.
- Generated-header consistency checks verifying that each `reg...` macro has a matching `reg..._BASE_IDX` macro and that register-list macros refer only to names present in both offset and shift/mask headers.
- Address-table spot checks for representative instances: `MPCC_OGAM1_MPCC_OGAM_CONTROL`, `MPCC_MCM0_MPCC_MCM_SHAPER_CONTROL`, `MPCC_MCM3_MPCC_MCM_MEM_PWR_CTRL`, `ABM0_BL1_PWM_USER_LEVEL`, `ABM3_DC_ABM1_HG_RESULT_24`, `DPG2_DPG_STATUS`, `FMT1_FMT_422_CONTROL`, `OPPBUF1_OPPBUF_CONTROL1`, and `OPP_PIPE_CRC1_OPP_PIPE_CRC_RESULT2`.
- Hardware or emulator tests for color-management programming: output gamma bank switching, MCM shaper/1D LUT/3D LUT programming, gamut-remap coefficients, and memory power-control transitions.
- ABM tests covering PWM level writes/readbacks, histogram/luma sampling, missed-read progress clearing, DMUB ABM commands, suspend/resume, and eDP panel backlight transitions.
- OPP tests covering test-pattern generation, formatter clamp/bit-depth/dither behavior, 4:2:0/4:2:2 modes, OPPBUF 3D/segmentation parameters, and pipe CRC enable/mask/result readback.

## Chunk Boundary Notes

Line 5158 begins at `dce_dc_mpc_mpcc_ogam1_dispdec`; OGAM instance 0 is outside this chunk. Line 7651 stops after `regFMT2_FMT_CLAMP_COMPONENT_R_BASE_IDX`; the rest of FMT2 and later OPP instance 2/3 blocks continue in the following chunk. The merge/reconciliation lane should combine this report with adjacent chunk reports for complete per-file coverage of `dcn_3_2_1_offset.h`.
