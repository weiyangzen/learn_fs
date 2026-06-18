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
