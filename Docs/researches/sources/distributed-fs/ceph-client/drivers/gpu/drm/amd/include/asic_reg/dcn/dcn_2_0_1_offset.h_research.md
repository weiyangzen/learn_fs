# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001638`: lines 1-2584, `Docs/researches/chunks/subset-b-001638_research.md`
- `subset-b-001639`: lines 2585-5134, `Docs/researches/chunks/subset-b-001639_research.md`
- `subset-b-001640`: lines 5135-6193, `Docs/researches/chunks/subset-b-001640_research.md`

## Chunk Research

### subset-b-001638: lines 1-2584

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_offset.h lines 1-2584

## Purpose

This chunk is the first portion of AMDGPU's generated DCN 2.0.1 register offset header. It contains no executable logic; it publishes preprocessor constants that map display-controller register names to MMIO offsets and to the hardware base segment used by SOC15-style register addressing.

Every exposed register appears as a pair:

- `mm<REGISTER>`: the register's offset within a display/MMIO segment.
- `mm<REGISTER>_BASE_IDX`: the base-segment selector that consumers pass to a `BASE(...)` macro before adding the offset.

The assigned range covers the header prologue and 1,199 register offsets: DCCG/display clocks, RBBM interface status, Azalia/HDA audio, HUBBUB memory arbitration and return-path state, four HUBP/HUBPREQ/HUBPRET/cursor instances, all DPP0 and DPP1 top/conversion/scaler/color-management blocks, and the start of DPP2 through `mmDSCL2_LB_DATA_FORMAT` at the chunk boundary. Most `_BASE_IDX` values are `2`; the DCCG clock-generator group uses base index `1`.

Although the repository path is under a local `ceph-client` tree, this file is AMD display hardware metadata. It has no Ceph filesystem, distributed storage, networking protocol, or persistent filesystem behavior.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, globals, or runtime APIs in this range. The macro namespace is the API.

Important macro groups in lines 1-2584 include:

- Header guard `_dcn_2_0_1_OFFSET_HEADER` and AMD MIT license prologue.
- DCCG/DENTIST clock registers such as `mmDENTIST_DISPCLK_CNTL`, `mmDISPCLK_FREQ_CHANGE_CNTL`, `mmDPPCLK*_DTO_PARAM`, `mmDCCG_AUDIO_DTO*`, `mmDP_DTO*`, `mmDCCG_GATE_DISABLE_CNTL*`, and `mmDCCG_SOFT_RESET`.
- DMU/RBBM interface timeout/status registers: `mmRBBMIF_TIMEOUT`, `mmRBBMIF_STATUS*`, `mmRBBMIF_INT_STATUS`, and timeout-disabling/status-flag registers.
- HDA/Azalia audio registers for the controller, root function, endpoint index/data windows, input endpoints, payload capabilities, CRC controls, DMA controls, power state, and cyclic buffer state.
- HUBBUB return-path and arbitration registers including DCC configuration arrays, CRC values, QoS/urgent watermarks for watermark sets A-D, DRAM clock-change watermarks, timeout detection/interrupts, VTG controls, soft reset, clock controls, global timer, and memory power controls.
- Four HUBP instances, `HUBP0` through `HUBP3`, with repeated `DCSURF_*`, viewport, request-size, clock, debug, and measurement-window registers.
- Four HUBPREQ instances, `HUBPREQ0` through `HUBPREQ3`, with surface pitch/address/meta-address pairs, flip controls, surface-in-use/earliest-in-use status, TTU/QoS timing controls, vblank/nominal/flip/prefetch parameters, cursor settings, per-line delivery, memory power, and destination timing registers.
- Four HUBPRET instances, `HUBPRET0` through `HUBPRET3`, with read-line controls, read-line values/status, interrupts, and memory power state.
- Four cursor/DC metadata blocks, `CURSOR0_0` through `CURSOR0_3`, with cursor address, size, position, hotspot, stereo, destination offset, memory power, and `DMDATA_*` sideband metadata registers.
- DPP0 and DPP1 display pipe processor blocks: `DPP_TOP`, `CNVC_CFG`, `CNVC_CUR`, `DSCL`, and very large `CM` color-management ranges.
- The beginning of DPP2: `DPP_TOP2`, `CNVC_CFG2`, `CNVC_CUR2`, and the first part of `DSCL2`.

The `CM0` and `CM1` color-management blocks dominate this chunk. They define degamma, blend-gamma, gamut remap, shaper, 3D LUT, coefficient-format, HDR multiplier, dealpha, memory power, test-debug, and many RAM A/B region/start/end/slope registers. These offsets are consumed together with field definitions from `dcn_2_0_1_sh_mask.h`.

## Control Flow

This header has no runtime control flow. Its behavior is entirely compile-time macro expansion.

The normal consumer pattern in DCN201 code is:

1. Include `dcn/dcn_2_0_1_offset.h` and `dcn/dcn_2_0_1_sh_mask.h`.
2. Define a `BASE_INNER(seg)` macro using the ASIC IP-offset header, for this generation commonly `DMU_BASE__INST0_SEG##seg` from `cyan_skillfish_ip_offset.h`.
3. Define register-list helper macros such as `SR(reg_name)` and `SRI(reg_name, block, id)`.
4. Expand a hardware-object register list into static register tables by computing `BASE(mm..._BASE_IDX) + mm...`.
5. Use the resulting table fields with `REG_READ`, `REG_SET`, `REG_UPDATE`, IRQ setup, clock setup, or hardware sequencing helpers.

Concrete include and expansion sites in this tree include `display/dc/resource/dcn201/dcn201_resource.c`, `display/dc/irq/dcn201/irq_service_dcn201.c`, and `display/dc/clk_mgr/dcn201/dcn201_clk_mgr.c`. `dcn201_resource.c` builds tables for clock sources, audio, IPP/DPP, OPP, MPC, timing generators, HUBP instances, and HUBBUB. `irq_service_dcn201.c` uses `SRI(...)` to compute HPD, plane-flip, vblank/vline, and vupdate interrupt registers. `dcn201_clk_mgr.c` uses `SR(...)` for clock-manager registers such as DENTIST/DCCG programming.

Within the lines covered here, the most direct register-list integration is HUBP and HUBBUB. `hubp/dcn10/dcn10_hubp.h` and `hubp/dcn201/dcn201_hubp.h` expand `SRI(DCSURF_ADDR_CONFIG, HUBP, id)`, `SRI(DCSURF_PRIMARY_SURFACE_ADDRESS, HUBPREQ, id)`, `SRI(DCSURF_SURFACE_FLIP_INTERRUPT, HUBPREQ, id)`, cursor registers, prefetch registers, and flip-parameter registers against the `HUBP*`, `HUBPREQ*`, and `CURSOR0_*` macros in this chunk. `hubbub/dcn201/dcn201_hubbub.h` expands common HUBBUB registers and `SR(DCHUBBUB_CRC_CTRL)` against the HUBBUB offsets in this chunk.

## State And Persistence Behavior

The file stores no software state and performs no MMIO access by itself. Its constants describe hardware state that other DCN201 code reads or writes.

The represented hardware state includes display clocks and DTOs; audio endpoint/controller state; HUBBUB request arbitration, watermarks, QoS, CRC, timeout, and power state; HUBP surface address/tiling/viewport/flip/cursor state; request timing and prefetch state; and DPP scaler/color-conversion/color-management LUT state.

Persistence is hardware-defined rather than file-defined. Register values programmed through these offsets can be latched until mode set, surface flip, power-gating transition, suspend/resume, firmware interaction, or ASIC reset. Some offsets point to live status or interrupt registers, some to sticky status/clear registers, some to LUT index/data windows, and some to memory-power controls. This header does not encode read-only versus writable behavior, write-one-to-clear rules, self-clearing fields, sequencing requirements, or valid value ranges.

The `_BASE_IDX` values are part of the addressing contract. A wrong base index sends every consumer using that macro to a different segment even when the local offset is numerically correct. In this chunk, DCCG register pairs use base index `1`, while DMU/RBBMIF, HDA/Azalia, HUBBUB, HUBP/HUBPREQ/HUBPRET/cursor, and DPP blocks use base index `2`.

## Dependencies

This generated offset header depends on companion hardware metadata:

- `dcn/dcn_2_0_1_sh_mask.h` provides the matching field shifts and masks for the same register names.
- `cyan_skillfish_ip_offset.h` provides `DMU_BASE__INST0_SEG*` constants used by DCN201 consumers to turn `_BASE_IDX` into an absolute MMIO base.
- Display helper macros from `reg_helper.h` and hardware-object headers convert `SR(...)`, `SRI(...)`, `HUBP_SF(...)`, `SF(...)`, and related macro expansions into register-address and field tables.
- DCN201 resource, IRQ, HUBP, HUBBUB, DPP, audio, and clock-manager code depend on the exact generated names. The preprocessor concatenates names, so a spelling change in this header breaks table generation at compile time.
- The underlying hardware register database is the real source of truth for offsets, base indices, field semantics, reserved fields, and reset behavior.

This chunk is also tied to neighboring chunks of the same header. The physical file continues past line 2584 into the rest of `DSCL2`, DPP2 color-management blocks, later display pipeline blocks, link/audio/PHY/DCIO offsets, and indirect endpoint definitions. This research document intentionally covers only lines 1-2584.

## Integration Points

The main integration point is DCN201 resource construction. Static register tables created in `dcn201_resource.c` are passed into hardware-object constructors such as HUBP, DPP, HUBBUB, timing-generator, audio, clock-source, OPP, and link-encoder constructors. Once constructed, higher-level display code accesses registers through object-local table fields rather than by naming these generated macros directly.

Specific display subsystems touched by this chunk are:

- Clock management: DCCG/DENTIST offsets feed display clock, DPP clock, audio DTO, DP DTO, gate disable, soft reset, and clock status programming.
- Audio: Azalia controller/root/endpoint offsets feed HDMI/DP audio setup, endpoint indirect access, DMA controls, payload capability reporting, cyclic buffer status, and audio power management.
- HUBBUB: arbitration and watermark offsets feed memory request scheduling, QoS, DRAM clock-change allowance, timeout detection, CRC capture, and memory power behavior.
- HUBP/HUBPREQ/HUBPRET: offsets feed primary and secondary surface programming, metadata addresses, tiling/address configuration, viewport programming, flip control and interrupts, cursor programming, request timing, prefetch, blanking, and read-line status.
- DPP: DPP top, CNVC, DSCL, and CM offsets feed pixel-format conversion, keying, cursor color, scaling ratios and taps, line-buffer configuration, degamma/blend/shaper/3D-LUT programming, gamut remap, HDR multiplier, and DPP CRC/debug.
- IRQ service: plane flip interrupts use `HUBPREQx_DCSURF_SURFACE_FLIP_INTERRUPT`; HPD/vblank/vline/vupdate registers are resolved by the same generated-offset pattern, although some of those later or related blocks are outside this chunk.

The source is source-tree-aligned with `include/asic_reg/dcn`: it is a low-level hardware register map, not an algorithmic driver module.

## Risks And Edge Cases

- A wrong offset or `_BASE_IDX` can compile cleanly but make the driver read or write the wrong MMIO register, causing blank display, failed modeset, bad surface flips, audio failure, clock misprogramming, memory-arbitration issues, interrupt loss, or hangs during power transitions.
- Register-list macros rely on exact name construction. Instance families such as `HUBP0` through `HUBP3`, `HUBPREQ0` through `HUBPREQ3`, `CURSOR0_0` through `CURSOR0_3`, and `CM0`/`CM1` are especially vulnerable to generated suffix drift.
- The chunk ends in the middle of the `DSCL2` block. A chunk-only review must not assume DPP2 is fully represented here; `mmDSCL2_LB_DATA_FORMAT` lacks its paired `_BASE_IDX` within this line range because the pair is on the next line outside the requested chunk.
- The header exposes address constants only. It does not protect consumers from illegal sequencing, status-versus-control confusion, write-one-to-clear semantics, or LUT index/data ordering requirements.
- Repeated CM LUT and region registers are dense and similar. Copy-generation mistakes in one RAM A/B block or one color-management instance can affect only specific pipes or color paths and may escape compile-time detection.
- Base index `1` versus `2` is subtle. Mixing the DCCG base convention with the display-pipe/HUBBUB/HUBP convention would redirect clock programming or pipe programming to the wrong segment.
- Some register names describe memory power, clock gating, soft reset, timeout detection, and interrupt clear/mask behavior. Misuse of these offsets can create hardware state that persists until reset or makes later diagnostics misleading.
- Because this is generated hardware metadata, manual edits should be avoided unless synchronized with the ASIC register database and matching `dcn_2_0_1_sh_mask.h` definitions.

## Test Signals

Useful validation signals are mostly compile-time, register-table, and hardware/display behavior:

- AMDGPU display builds for DCN201/Cyan Skillfish paths should compile all `SR(...)`, `SRI(...)`, and field-mask references that combine this header with `dcn_2_0_1_sh_mask.h`.
- Static generated-header checks should verify every register in this chunk, including base index values, against the ASIC register database and against neighboring generated headers for DCN 2.0.0/2.1.0 where appropriate.
- Resource-table inspection should confirm that DCN201 `hubp_regs[]`, `hubbub_reg`, `tf_regs[]`, audio registers, IRQ source entries, and clock-manager registers resolve to expected absolute addresses.
- Display smoke tests should cover boot modeset, hotplug, suspend/resume, runtime power management, multi-plane composition, page flips, cursor movement, and vblank/flip interrupt delivery on hardware using DCN201 offsets.
- Surface programming tests should exercise linear/tiled/compressed surfaces, luma/chroma address pairs, metadata surfaces, primary/secondary surfaces, viewport changes, and triple-buffer/flip-control paths.
- Watermark and clock tests should verify DCCG/DENTIST programming, DPP clock/dispclk changes, audio DTO, DP DTO, HUBBUB watermarks, DRAM clock-change allowance, and timeout status under bandwidth stress.
- Color and scaler tests should exercise DPP0/DPP1 and, in later chunks, complete DPP2 programming: scaler taps/ratios, line-buffer state, degamma, blend gamma, shaper, gamut remap, HDR multiplier, and 3D LUT paths.
- Audio tests should validate Azalia endpoint access, payload capability, stream DMA, cyclic-buffer state, and HDMI/DP audio under modeset and suspend/resume.
- Failure symptoms from bad constants include register readbacks from unexpected addresses, lost HPD/vblank/flip interrupts, incorrect cursor or surface address programming, flicker/blank display, wrong colors or scaling, failed audio, clock update failures, HUBBUB timeout interrupts, or hangs during reset/power-gating sequences.

## Cross-Chunk Notes

This is the first chunk of `dcn_2_0_1_offset.h`. Later chunks must complete the DPP2 `DSCL` block, remaining DPP/color-management and display-link register families, and the final header guard close. The final per-file report should describe the complete file as a generated DCN 2.0.1 MMIO offset contract paired with `dcn_2_0_1_sh_mask.h`, with this chunk contributing the clock/audio/HUBBUB/HUBP/DPP-front portion of that contract.

### subset-b-001639: lines 2585-5134

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_offset.h lines 2585-5134

## Scope

This chunk is part of the generated AMD DCN 2.0.1 ASIC register offset header. It covers lines 2585-5134 of `dcn_2_0_1_offset.h`, beginning inside the tail of the DPP2 scaler block and ending at the first DIO I2C transaction registers. The slice is constants-only: it exports `#define` macros for memory-mapped display register offsets plus companion `_BASE_IDX` macros, with no C functions, structs, enums, or local runtime control flow.

The chunk contains display pipeline front-end, composition, output, timing, and DDC/I2C register address coverage for DCN 2.0.1. Most macros use the `mm<block>_<register>` naming convention, while each matching `mm..._BASE_IDX` macro selects the register aperture segment used by the display register helper layer.

## Purpose

The purpose of this chunk is to bind symbolic DCN 2.0.1 display register names to exact MMIO offsets. AMDGPU display code uses these offsets, together with the matching `dcn_2_0_1_sh_mask.h` field definitions, to build register tables and to perform typed register reads, writes, updates, polling, and interrupt acknowledgement without scattering literal offsets through functional code.

The visible hardware domains are:

- The tail of DPP2 DSCL register coverage for line-buffer format, line-buffer/scaler/OBUF memory power, and vertical counter state.
- DPP2 color management (`CM2`) registers for input CSC, gamut remap, bias, degamma/blend gamma/output gamma RAM A/B programming, LUT access, legacy palette controls, memory power, and debug data.
- DPP3 top, converter/config, cursor, scaler, and color-management blocks (`DPP_TOP3`, `CNVC_CFG3`, `CNVC_CUR3`, `DSCL3`, `CM3`) with the same front-end display processing themes for pipe 3.
- MPC/MPCC registers for five MPCC instances, global MPC control, output muxing, vupdate-lock routing, denormalization clamps, per-MPCC output gamma, and output CSC matrices.
- OPP/FMT/DPG/OPPBUF/pipe CRC register copies for output pipes 0 and 1, including output formatting, dithering, clamps, 4:2:0/4:2:2 handling, display pattern generation, 3D parameters, pipe enable/control, and CRC capture.
- OPTC/ODM and OTG registers for two timing generators, including horizontal/vertical totals, blanking/sync windows, stereo, snapshots, interrupts, CRC windows, static screen, global sync lock, master update locking, DRR, and DSC start position.
- Miscellaneous display output selection and clock controls (`DWB_SOURCE_SELECT`, `GSL_SOURCE_SELECT`, `OPTC_CLOCK_CONTROL`).
- DIO DDC/I2C controller offsets for arbitration, interrupt control, software/hardware status, DDC1/DDC2 speed/setup, and transaction programming.

## Important API Surface

The exported API is preprocessor register metadata. Each usable register normally appears as a pair:

- `mm<register>`: the register offset inside the selected DCN register address space.
- `mm<register>_BASE_IDX`: the base segment selector consumed by `BASE(...)`, `SRI(...)`, `REG(...)`, and related helper macros.

Representative examples from this chunk include:

- `mmCM2_CM_DGAM_LUT_INDEX`, `mmCM2_CM_DGAM_LUT_DATA`, and `mmCM2_CM_OGAM_LUT_DATA` for pipe 2 DPP transfer-function programming.
- `mmCNVC_CFG3_CNVC_SURFACE_PIXEL_FORMAT`, `mmCNVC_CUR3_CURSOR0_CONTROL`, and `mmDSCL3_SCL_HORZ_FILTER_SCALE_RATIO` for pipe 3 pixel conversion, cursor, and scaling setup.
- `mmMPCC0_MPCC_TOP_SEL` through `mmMPCC4_MPCC_STATUS` for repeated MPCC instance routing, blending, update-lock, power, stall, and status control.
- `mmMPC_CLOCK_CONTROL`, `mmMPC_SOFT_RESET`, `mmMPC_OUT0_MUX`, and `mmMPC_OUT1_DENORM_CONTROL` for global MPC behavior and output routing.
- `mmMPCC_OGAM0_MPCC_OGAM_MODE` through `mmMPCC_OGAM4_MPCC_OGAM_RAMB_REGION_32_33` for per-MPCC output-gamma LUT programming.
- `mmMPC_OUT_CSC_COEF_FORMAT`, `mmMPC_OUT0_CSC_MODE`, and `mmMPC_OUT1_CSC_C33_C34_B` for output color-space conversion.
- `mmFMT0_FMT_BIT_DEPTH_CONTROL`, `mmFMT1_FMT_MAP420_MEMORY_CONTROL`, `mmDPG0_DPG_CONTROL`, and `mmOPP_PIPE_CRC1_OPP_PIPE_CRC_RESULT2` for output formatting, pattern generation, and CRC readback.
- `mmODM0_OPTC_INPUT_GLOBAL_CONTROL` and `mmODM1_OPTC_MEMORY_CONFIG` for output data-merger input control.
- `mmOTG0_OTG_H_TOTAL`, `mmOTG0_OTG_VERTICAL_INTERRUPT0_CONTROL`, `mmOTG1_OTG_MASTER_UPDATE_LOCK`, and `mmOTG1_OTG_DRR_CONTROL` for timing generator programming and synchronization.
- `mmDC_I2C_CONTROL`, `mmDC_I2C_DDC1_SPEED`, and `mmDC_I2C_TRANSACTION1` for display DDC/I2C transactions.

The block inventory in this slice is:

- DPP/CM/scaler: DPP2 DSCL tail, `CM2`, `DPP_TOP3`, `CNVC_CFG3`, `CNVC_CUR3`, `DSCL3`, `CM3`.
- MPC: `MPCC0`-`MPCC4`, `MPC`, `MPCC_OGAM0`-`MPCC_OGAM4`, `MPC_OUT_CSC`.
- OPP: `FMT0`, `DPG0`, `OPPBUF0`, `OPP_PIPE0`, `OPP_PIPE_CRC0`, and the same pipe-1 families.
- OPTC: `ODM0`, `ODM1`, `OTG0`, `OTG1`, OPTC misc source/clock controls.
- DIO: common DC I2C controller and DDC1/DDC2 setup/status registers.

## Control Flow

There is no executable control flow in this header chunk. Runtime flow is external and macro-driven:

- DCN 2.0.1 resource construction includes this header and expands register list macros into per-block register tables. For example, DPP, MPC, OPP, OPTC, clock, and IRQ code use symbolic names that paste an instance id into `mm...` and `mm..._BASE_IDX` identifiers.
- Register helper macros combine `BASE(mm..._BASE_IDX)` with `mm...` to produce the final MMIO address. The `SRI(reg_name, block, id)` pattern in the DCN 2.0.1 IRQ service demonstrates this for instance-addressed interrupt registers.
- Functional display code then uses `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET`, polling helpers, and table initializers with the generated offset and mask/shift headers.
- Hardware sequencing rules are enforced by the consumer code and by DCN hardware, not by this file. The header only supplies the addresses needed to execute sequences such as scaler programming, color LUT loading, MPCC tree updates, OPP enablement, OTG locking, vblank/vline interrupt programming, and DDC transactions.

The implicit ordering contract is significant. Callers must program related register groups in safe order: update locks before multi-register changes, LUT index/data windows in the correct sequence, power controls before depending on memory-backed blocks, OTG timing before master enable, interrupt clears with the right status semantics, and I2C transaction registers while the controller is idle/arbitrated.

## State and Persistence

The file itself has no software state. The constants point to hardware state that persists while the display IP block is powered and until reprogrammed or reset:

- DPP CM, DSCL, CNVC, and cursor registers hold per-pipe conversion, scaling, cursor, gamma, and color-management state.
- MPC and MPCC registers hold compositor topology, OPP routing, blending gains, background color, stall state, vupdate-lock routing, output muxing, and memory-power status.
- MPCC OGAM and DPP CM gamma registers expose indexed LUT/RAM programming windows; index/data/control writes mutate hardware LUT state rather than ordinary software memory.
- OPP/FMT/DPG/CRC registers hold output formatting, bit depth, dither seeds, clamp limits, test pattern, 3D, pipe-control, and CRC capture state.
- OTG/ODM registers hold active timing, blank/sync positions, trigger/manual force state, stereo controls, frame counters, snapshot state, vertical interrupt positions, CRC windows, global sync lock, master update lock, DRR, and DSC start position.
- DIO I2C registers hold controller arbitration, setup/speed, status, interrupt, and transaction descriptors for DDC access.

Bad offsets can therefore persist as hardware misconfiguration: visible corruption, wrong color transforms, scaler artifacts, failed composition, stuck update locks, lost vblank/vline interrupts, broken CRC diagnostics, display timing failure, missed DDC/EDID reads, or power-management dead states until a modeset, block reset, or GPU reset repairs the affected registers.

## Dependencies and Integration Points

This header is tightly coupled to:

- `dcn_2_0_1_sh_mask.h`, which defines the field masks and shifts for the same register names.
- DCN 2.0.1 display files that include it directly: `display/dc/resource/dcn201/dcn201_resource.c`, `display/dc/irq/dcn201/irq_service_dcn201.c`, and `display/dc/clk_mgr/dcn201/dcn201_clk_mgr.c`.
- Register list and helper macros in the AMD display core, including DPP transfer-function lists, MPC/MPCC register tables, OPP/OPTC register tables, IRQ source descriptors, and clock-manager register access.
- SOC15/IP base definitions such as `cyan_skillfish_ip_offset.h`, `soc15_hw_ip.h`, and the `DMU_BASE__INST0_SEG...` style base-address macros that make `_BASE_IDX` meaningful.
- Cross-generation DCN headers. Similar register families exist in DCN 2.0.0, DCN 2.1, DCN 3.x, and later headers, but offsets, instance counts, and register presence can differ. Consumers must include the matching generation header rather than assuming a common address map.

The repeated instance patterns are a major integration contract. `CM2` and `CM3`, `MPCC0`-`MPCC4`, `MPCC_OGAM0`-`MPCC_OGAM4`, `FMT0`/`FMT1`, `DPG0`/`DPG1`, `ODM0`/`ODM1`, and `OTG0`/`OTG1` are expected to align with instance-id macro expansion in display code. A single wrong offset in one instance can affect only that pipe or output path and may not be caught by single-display testing.

## Risks

- Offset/base-index mismatch is the primary risk. `mm...` values are not useful alone; using the wrong `_BASE_IDX` can target a different MMIO aperture even when the symbolic register name is correct.
- Repeated instance drift is easy to introduce. The MPCC, MPCC OGAM, FMT/DPG/OPP, ODM, and OTG blocks are near copies with different base offsets; copy/paste or generation errors can break one pipe while adjacent pipes still work.
- Indexed LUT programming registers are stateful. Wrong CM/OGAM LUT index/data/control offsets can corrupt transfer functions, gamut remap, blending gamma, or output gamma and produce subtle color regressions.
- Update-lock and synchronization registers have cross-block effects. Incorrect MPC vupdate-lock, OTG update-lock, master update, or global sync offsets can cause partial updates, timing glitches, or hangs during modesets and flips.
- Interrupt and CRC registers mix control, mask, status, and readback semantics. Wrong OTG vertical interrupt or CRC offsets can lose vblank/vline events, acknowledge the wrong source, or make diagnostics misleading.
- Power-control and status registers are easy to confuse. DPP DSCL/OBUF, CM memory power, MPCC memory power, OPP clock, and OTG clock controls can leave display sub-blocks gated or incorrectly reported if offsets are wrong.
- DIO I2C offsets affect monitor discovery. Broken DDC speed/setup/transaction/status addresses can prevent EDID reads, HPD-related probing, or AUX/DDC fallback behavior from working reliably.
- This chunk begins and ends mid-file. The DPP2 DSCL block starts before line 2585, and the DIO I2C block continues after line 5134; the merge lane must combine adjacent chunks for a complete file-level map.

## Test Signals

Useful validation signals are mostly compile-time macro expansion plus runtime display behavior:

- AMDGPU/display compilation should catch missing or renamed offset macros in DCN 2.0.1 resource, clock-manager, IRQ, DPP, MPC, OPP, and OPTC table construction.
- Static comparison against the vendor register database and adjacent generated DCN 2.0.1 mask/shift header should confirm every offset has the expected `_BASE_IDX` and matching field definitions.
- Modeset tests should exercise one and two active pipes, pipe 3 DPP use, MPCC composition, OPP0/OPP1 output paths, ODM0/ODM1 routing, OTG0/OTG1 timing, and DSC start-position programming.
- Color tests should cover degamma, blend gamma, output gamma, gamut remap, CSC, denorm clamp, dither, 4:2:0/4:2:2 output handling, and LUT programming on the affected DPP/MPC/OPP paths.
- Synchronization tests should verify vblank, vline, vupdate, frame counters, update locks, global sync lock, DRR, stereo, and master enable behavior on both OTG instances.
- Diagnostic paths should validate DPP/MPC/OPP/OTG CRC controls and readback registers, DPG pattern generation, pixel readback/status registers, and performance/status counters where available.
- Power-management tests should cover suspend/resume, runtime clock/memory gating, repeated modesets, blank/unblank, static-screen handling, and recovery from underflow or stalled MPCC state.
- DDC/I2C tests should confirm EDID reads, DDC1/DDC2 speed/setup programming, arbitration, SW/HW status transitions, interrupt behavior, and transaction sequencing on real connectors.

## Chunk Notes

This is a generated register-offset slice, so its research value is the hardware map and consumer contracts rather than algorithmic behavior. The most important areas for reconciliation are the repeated instance families and the high-impact stateful blocks: color/gamma LUTs, MPCC routing, output formatting, OTG timing/interrupts, update locks, power controls, and DDC/I2C transactions.

### subset-b-001640: lines 5135-6193

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_offset.h lines 5135-6193

## Scope

This chunk is the final 1,059-line slice of the generated AMD DCN 2.0.1 register offset header. The file ends at line 6193, so this range includes the tail of the display I/O offset map and the header guard terminator. It exports preprocessor constants only: memory-mapped register offsets named with `mm...` prefixes, per-register base-index constants named `mm..._BASE_IDX`, and indirect Azalia endpoint register indices named with `ix...` prefixes. There are no C functions, structs, enums, inline helpers, or local algorithms in this slice.

The visible hardware domains are:

- The tail of `dce_dc_dio_dout_i2c_dispdec`, including DDC/I2C transaction, data, EDID-detect, and read-request interrupt registers.
- `dce_dc_dio_dio_misc_dispdec` for DIO scratch registers, memory power controls/status, DIO/DIG clock controls, HDMI RX status timer, generic DIO interrupt message, and generic interrupt clear.
- `dce_dc_dio_hpd0_dispdec` and `dce_dc_dio_hpd1_dispdec` for two hot-plug-detect blocks.
- `dce_dc_dio_dp_aux0_dispdec` and `dce_dc_dio_dp_aux1_dispdec` for two DisplayPort AUX/I2C-over-AUX engines.
- `dce_dc_dio_dig0_dispdec` and `dce_dc_dio_dig1_dispdec` for two digital front-end and HDMI/AFMT/TMDS formatter instances.
- `dce_dc_dio_dp0_dispdec` and `dce_dc_dio_dp1_dispdec` for two DisplayPort link encoder instances.
- `dce_dc_dcio_dcio_dispdec` and `dce_dc_dcio_dcio_chip_dispdec` for DCIO, UNIPHY, pinstrap, GPIO/DDC/HPD/AUX pad, and pad-power control offsets.
- `azf0endpoint0_endpointind`, `azf0endpoint1_endpointind`, `azf0inputendpoint0_inputendpointind`, and `azf0inputendpoint1_inputendpointind` for HDA/Azalia display-audio endpoint and input-endpoint indirect indices.

## Purpose

The purpose of this chunk is to bind the DCN 2.0.1 display driver to the exact hardware register addresses for external display I/O, link encoding, AUX/DDC, HPD, HDMI/DP metadata, and display audio endpoint programming. The AMD display core avoids scattering raw register numbers through functional code; instead, resource and IRQ setup code includes this header and expands macros such as `SR`, `SRI`, `SRII`, and `SRI_IX` into per-block register tables.

In this chunk, most `mm...` register offsets have `_BASE_IDX` value `2`, which the DCN201 resource and IRQ code converts through `DMU_BASE__INST0_SEG2` before adding the register offset. The `ix...` constants are different: they are not memory-mapped MMIO offsets themselves, but endpoint-indirect register indices used with Azalia endpoint index/data registers. This distinction is a core integration contract for display audio.

## Important API Surface

The exported API surface is macro names and numeric constants. Important groups include:

- DDC/I2C control surface: `mmDC_I2C_TRANSACTION2`, `mmDC_I2C_TRANSACTION3`, `mmDC_I2C_DATA`, `mmDC_I2C_EDID_DETECT_CTRL`, and `mmDC_I2C_READ_REQUEST_INTERRUPT`.
- DIO shared state/control: `mmDIO_SCRATCH0` through `mmDIO_SCRATCH7`, `mmDIO_MEM_PWR_STATUS`, `mmDIO_MEM_PWR_CTRL`, `mmDIO_MEM_PWR_CTRL2`, `mmDIO_MEM_PWR_CTRL3`, `mmDIO_POWER_MANAGEMENT_CNTL`, `mmDIG_SOFT_RESET`, `mmDIO_CLK_CNTL`, `mmDIO_CLK_CNTL2`, and `mmDIO_CLK_CNTL3`.
- HPD instance registers: `mmHPD0_DC_HPD_INT_STATUS`, `mmHPD0_DC_HPD_INT_CONTROL`, `mmHPD0_DC_HPD_CONTROL`, `mmHPD0_DC_HPD_FAST_TRAIN_CNTL`, `mmHPD0_DC_HPD_TOGGLE_FILT_CNTL`, and matching `HPD1` forms.
- AUX instance registers: `mmDP_AUX0_AUX_CONTROL`, `mmDP_AUX0_AUX_SW_CONTROL`, `mmDP_AUX0_AUX_ARB_CONTROL`, `mmDP_AUX0_AUX_INTERRUPT_CONTROL`, `mmDP_AUX0_AUX_SW_STATUS`, `mmDP_AUX0_AUX_LS_STATUS`, data registers, DPHY TX/RX controls, and matching `DP_AUX1` forms.
- DIG/HDMI/AFMT/TMDS registers for instances 0 and 1: `DIG_FE_CNTL`, `DIG_OUTPUT_CRC_*`, `DIG_CLOCK_PATTERN`, `DIG_TEST_PATTERN`, FIFO/status, HDMI metadata/generic/audio/ACR/VBI/infoframe/GC/DB controls, AFMT ISRC/generic/audio/status/ramp/60958 controls, `DIG_BE_CNTL`, `DIG_BE_EN_CNTL`, `TMDS_*`, `DIG_VERSION`, `DIG_LANE_ENABLE`, and `AFMT_CNTL`.
- DP link registers for instances 0 and 1: `DP_LINK_CNTL`, `DP_PIXEL_FORMAT`, `DP_MSA_COLORIMETRY`, `DP_CONFIG`, `DP_VID_STREAM_CNTL`, `DP_DPHY_*`, CRC, fast training, secondary packet/audio timing, MST MSE allocation/status, MSA timing parameters, DSC controls, DP DB, VBID misc, metadata transmission, and DSC bytes-per-pixel.
- DCIO/PHY/GPIO registers: `mmDC_GENERICA`, `mmUNIPHYA_LINK_CNTL`, `mmUNIPHYA_CHANNEL_XBAR_CNTL`, `mmUNIPHYB_LINK_CNTL`, `mmUNIPHYB_CHANNEL_XBAR_CNTL`, `mmDCIO_WRCMD_DELAY`, `mmDC_PINSTRAPS`, `mmDCIO_CLOCK_CNTL`, `mmDCIO_SOFT_RESET`, `mmDC_GPIO_DDC1_*`, `mmDC_GPIO_DDC2_*`, `mmDC_GPIO_HPD_*`, `mmDC_GPIO_PAD_STRENGTH_1`, `mmPHY_AUX_CNTL`, `mmDC_GPIO_AUX_CTRL_1` through `_5`, and `mmAUXI2C_PAD_ALL_PWR_OK`.
- Azalia endpoint indices: converter format, stream/channel ID, digital converter, stream formats, supported rates, stripe/ramp/GTC controls, pin capabilities, unsolicited response, pin sense, widget control, channel speaker, audio descriptors 0-13, multichannel controls, lipsync/HBR, sink info 0-8, hot-plug control, configuration default, codec channel-status overrides, LPIB snapshot/timer, coding type, format changed, wireless display identification, remote keepalive, and audio enable/disable/format-change interrupt status. Input endpoint indices mirror input converter and input pin controls with channel allocation and infoframe fields.

The DCN201 inclusion sites found in this repository include `display/dc/resource/dcn201/dcn201_resource.c`, `display/dc/irq/dcn201/irq_service_dcn201.c`, and `display/dc/clk_mgr/dcn201/dcn201_clk_mgr.c`. `dcn201_resource.c` uses this offset header with the matching `dcn_2_0_1_sh_mask.h` field header, then macro-expands address lists into static register tables for audio, stream encoders, AUX engines, HPD blocks, link encoders, and other display blocks.

## Control Flow

There is no local control flow in this header. Runtime control flow is external and looks like this:

1. DCN201 resource initialization includes this header and defines helper macros such as `SR(reg_name)`, `SRI(reg_name, block, id)`, `SRII(...)`, and `SRI_IX(...)`.
2. Register-list macros from object headers, for example `AUD_COMMON_REG_LIST(id)`, `SE_DCN2_REG_LIST(id)`, `DCN2_AUX_REG_LIST(id)`, `HPD_REG_LIST(id)`, `LE_DCN_COMMON_REG_LIST(id)`, and `UNIPHY_DCN2_REG_LIST(phyid)`, paste symbolic names into this header's `mm...` or `ix...` constants.
3. The expanded constants populate typed register tables such as `dce_audio_registers`, `dcn10_stream_enc_registers`, `dcn10_link_enc_aux_registers`, `dcn10_link_enc_hpd_registers`, and `dcn10_link_enc_registers`.
4. Functional display code uses `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET`, `AZ_REG_READ`, `AZ_REG_WRITE`, HPD helpers, AUX helpers, and link/stream encoder methods against those register tables.
5. IRQ setup in `irq_service_dcn201.c` uses `SRI(DC_HPD_INT_STATUS, HPD, reg_num)` and similar generated expressions to set HPD status, enable, and acknowledge register addresses for `DC_IRQ_SOURCE_HPD1`, `DC_IRQ_SOURCE_HPD2`, `DC_IRQ_SOURCE_HPD1RX`, and `DC_IRQ_SOURCE_HPD2RX`.

Hardware sequencing is therefore enforced by the consuming code, not by this header. For example, the stream encoder controls when `DIG_FE_CNTL.DIG_START` is updated, link encoder code handles DP/TMDS setup and training state, AUX code performs arbitration and transfer polling, and audio code writes Azalia endpoint registers through index/data indirection.

## State and Persistence

The header itself has no software state, storage, or persistence beyond compile-time constants. The constants point at hardware state that persists in MMIO registers until hardware reset, power-gating transitions, driver reprogramming, or a register-specific clear/ack operation.

State represented by this chunk includes:

- DDC/I2C transaction descriptors and data FIFOs used for EDID and monitor-side I2C access.
- HPD sense, interrupt enable, interrupt acknowledge, fast-training, and toggle-filter state for the two physical connector-detect paths.
- AUX engine control, arbitration, SW/LS status, data, DPHY TX/RX tuning, and interrupt state used by DisplayPort link management and DP AUX transactions.
- DIG front-end, HDMI packet/metadata/audio, AFMT, TMDS, and DP stream state used while a display stream is active.
- DP link training, PHY pattern, scrambler, CRC, MST slot allocation, secondary data packet, DSC, VBID, and metadata transmission state.
- DCIO soft reset, clock control, UNIPHY link/channel crossbar, GPIO DDC/HPD/AUX pads, pad strength, and AUX/I2C pad-power state.
- Azalia endpoint codec state for display audio capabilities, descriptors, pin-sense/hot-plug, ELD/sink info, channel/speaker setup, HBR/lipsync reporting, LPIB snapshots, and audio status interrupts.

Because these are hardware register addresses, a bad offset can leave the driver writing a different register than intended. The visible effects may persist until a full display modeset, DC reset, GPU reset, or suspend/resume cycle reinitializes the affected blocks.

## Dependencies and Integration Points

This chunk is tightly coupled to:

- `dcn_2_0_1_sh_mask.h`, which supplies the field masks and shifts for the registers whose addresses are defined here.
- `cyan_skillfish_ip_offset.h`, which provides the `DMU_BASE__INST0_SEG*` base segments used by DCN201 `BASE(...)` expansion.
- Display resource construction in `display/dc/resource/dcn201/dcn201_resource.c`, where these constants are assembled into register tables for two audio, stream encoder, AUX, HPD, and link encoder instances.
- DCN201 IRQ setup in `display/dc/irq/dcn201/irq_service_dcn201.c`, which uses `HPD0`/`HPD1` status/control offsets for hot-plug and HPD RX interrupt mapping.
- DCN201 link encoder code in `display/dc/dcn201/dcn201_link_encoder.c`, which receives register tables containing DP, UNIPHY, AUX, and HPD offsets and then delegates most operations to DCN10/DCN20 link encoder helpers.
- DCE/DCN shared audio code in `display/dc/dce/dce_audio.c`, which uses Azalia endpoint index/data accessors and the `ixAZF0...` endpoint indices represented in this chunk.
- DCE/DCN shared AUX, HPD, stream encoder, and link encoder helpers under `display/dc/dce`, `display/dc/dio/dcn10`, `display/dc/dio/dcn20`, and `display/dc/dcn20`.

The repeated instance layout is part of the contract. DCN201 resource code creates arrays with two stream encoders, two AUX register sets, two HPD register sets, two link encoders, and two audio register sets. This chunk mirrors that with `DIG0`/`DIG1`, `DP0`/`DP1`, `DP_AUX0`/`DP_AUX1`, `HPD0`/`HPD1`, `UNIPHYA`/`UNIPHYB`, and `AZF0ENDPOINT0`/`AZF0ENDPOINT1` definitions.

## Risks

- Offset drift is high impact. If any `mm...` value is wrong, register helper calls still compile but target the wrong MMIO address, causing display bring-up failure, missing HPD events, bad AUX/DDC transactions, failed link training, broken HDMI/DP audio, or writes into unrelated DCN state.
- `mm..._BASE_IDX` values are as important as the offsets. A correct offset with an incorrect segment index would calculate the wrong absolute MMIO address in DCN201 resource and IRQ code.
- Instance-copy mistakes can affect only one connector path. `HPD0` versus `HPD1`, `DP_AUX0` versus `DP_AUX1`, `DIG0` versus `DIG1`, and `DP0` versus `DP1` are nearly parallel blocks with different offsets; one mismatched constant may reproduce only on a specific port or PHY.
- Indirect `ixAZF0...` constants must not be treated as direct MMIO offsets. They are endpoint register indices written through Azalia endpoint index/data registers. Confusing `mm` and `ix` address spaces would corrupt audio programming.
- Clear/ack/status registers are sensitive. HPD, AUX, AFMT, generic DIO, and Azalia audio interrupt status fields can be sticky or write-one-to-clear in the corresponding mask header. A wrong register address or shared helper mapping can miss events or clear the wrong event.
- Power and reset registers carry broad blast radius. `DIO_MEM_PWR_CTRL*`, `DIO_POWER_MANAGEMENT_CNTL`, `DIG_SOFT_RESET`, `DCIO_CLOCK_CNTL`, and `DCIO_SOFT_RESET` can disable or reset active display I/O blocks if programmed at the wrong time.
- The chunk starts mid-I2C block at `mmDC_I2C_TRANSACTION2` and ends with the file-level `#endif`. Whole-file reconciliation must combine it with earlier chunks to describe the complete I2C block and the rest of the DCN 2.0.1 register map.

## Test Signals

Good validation signals for this chunk are mostly compile-time coverage plus hardware/display behavior:

- A full AMDGPU display build should catch missing or renamed macros in DCN201 resource, clock manager, IRQ, audio, AUX, HPD, stream encoder, and link encoder code.
- Header-generation or static-diff checks against AMD's register database and adjacent generated headers such as `dcn_2_0_0_offset.h`, `dcn_2_1_0_offset.h`, and matching `dcn_2_0_1_sh_mask.h` should flag unexpected offset, base-index, or instance-count changes.
- Connector tests should verify HPD plug/unplug, HPD RX, HPD toggle filtering, and IRQ acknowledgement on both connector instances.
- DisplayPort tests should exercise AUX reads/writes, DPCD access, link training, fast training, CRC/test patterns, MST slot allocation/status, DSC enablement, and secondary packet/metadata transmission on both DP links.
- HDMI/TMDS tests should cover mode set, TMDS encoder setup, HDMI infoframes, ACR/audio packet programming, generic metadata packets, AFMT status, and display audio hot-plug behavior.
- EDID/DDC tests should validate I2C transaction programming, data handling, EDID detect, and read-request interrupt behavior.
- Suspend/resume, runtime power management, display hotplug storms, and multi-monitor modes should show no stuck DIO/DCIO resets, pad-power failures, AUX pad power-not-OK state, missed HPD interrupts, or audio endpoint status regressions.

## Chunk Notes

This is a generated constants-only slice, so the research value is the hardware coverage and integration contract rather than local logic. The chunk is especially important for DCN201 external-display behavior because it contains the two-instance register maps for HPD, AUX, DIG, DP, UNIPHY, GPIO pads, and Azalia display-audio endpoint indices. Any edits to these constants should be treated as hardware-spec changes and validated against both generated register sources and real display-path behavior.
