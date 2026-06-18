# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 54780-57274

## Scope

This chunk is part of AMD's generated DCN 4.2.0 register shift/mask header. It contains preprocessor constants only: each hardware bitfield is represented by a `...__SHIFT` bit position and a matching `..._MASK` mask value. There are no C functions, structs, enums, variables, includes, locks, allocations, branches, or direct MMIO operations in this range.

The requested range contains 2,092 `#define` lines across 374 distinct register names. It starts at an artificial boundary inside `VPG8_VPG_GSP_IMMEDIATE_UPDATE_CTRL`, completes the tail of the HPO VPG8 generic-packet block, covers HPO DP symbol32 stream/link/DPHY instance 3, covers MPCC mixer instances 0 through 3, covers complete MPCC output-gamma/gamut-remap instances 0 and 1, and ends inside the beginning of `MPCC_OGAM2_MPCC_OGAM_RAMA_REGION_6_7`. Neighboring chunks are required for the complete boundary registers and for the rest of MPCC_OGAM2.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement distributed filesystem behavior.

## Purpose

The purpose of this chunk is to publish exact DCN 4.2.0 bitfield metadata for high-performance DisplayPort output, generic packet generation, stream/link PHY control, MPC blending, output gamma, and gamut remap hardware. Runtime display code combines these field constants with matching register offsets from `dcn_4_2_0_offset.h` and AMD display register helpers to perform masked reads, writes, updates, and polling without hand-coded bit arithmetic.

Important covered surfaces:

- `VPG8_*` tail fields define HPO generic packet update/status, VPG memory-power control, and ISRC indexed payload access.
- `DP_SYM32_ENC3_*` defines the third HPO DP 32-bit-symbol stream encoder fields for enable/reset, pixel-to-symbol FIFO, MSA double buffering, pixel format, video MSA payload words, generic SDP/GSP scheduling, audio SDP, metadata packets, VBID, stream enable, panel replay, CRC, symbol counters, ALPM, wake interrupt state, memory power, and spare bits.
- `DP_LINK_ENC3_*` defines HPO DP link-encoder clock-control and spare fields for the same output path.
- `DP_DPHY_SYM323_*` defines symbol32 DP DPHY control/status, VC-rate programming, slot-allocation-table entries and status for virtual channels 0-3, eDP ASSR, ALPM, test-pattern generation, error status, and symbol counters.
- `MPCC0_*` through `MPCC3_*` define Multi-Plane Composition Controller mixer fields for input selection, OPP routing, blending/alpha/global gain, stereo/segment mode, update lock selection, background color, OGAM memory power, and status.
- `MPCC_OGAM0_*` and `MPCC_OGAM1_*` define complete output-gamma and gamut-remap bitfields for two MPCC OGAM instances: LUT access, RAM A/B piecewise-linear curve controls and region tables, coefficient format, gamut-remap mode/current status, and A/B matrix coefficient banks.
- `MPCC_OGAM2_*` begins the same OGAM layout for instance 2, from control/LUT access through the first RAM A region-table registers. This block continues after the chunk boundary.

## Important APIs, Types, And Macros

There are no typed C APIs in this range. The exported interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's starting bit position inside the hardware register.
- `<REGISTER>__<FIELD>_MASK` gives the field mask used by AMD register helpers to preserve unrelated bits.
- Address-block comments, such as `dce_dc_hpo_dp_sym32_enc3_dispdec` and `dce_dc_mpc_mpcc_ogam0_dispdec`, preserve the register-database grouping used by generated offset and field headers.

Major macro families:

- VPG8 generic-packet fields: `VPG_GENERIC*_IMMEDIATE_UPDATE`, `VPG_GENERIC*_IMMEDIATE_UPDATE_PENDING`, `VPG_GENERIC_LOCK_STATUS`, `VPG_GENERIC_CONFLICT_OCCURED`, `VPG_GENERIC_CONFLICT_CLR`, `VPG_GSP_MEM_LIGHT_SLEEP_DIS`, `VPG_GSP_LIGHT_SLEEP_FORCE`, `VPG_GSP_MEM_PWR_STATE`, `VPG_ISRC1_2_DATA_INDEX`, and four indexed ISRC data bytes.
- DP symbol32 stream encoder fields: `DP_SYM32_ENC_ENABLE`, reset/reset-done, pixel FIFO enable/reset/overflow, MSA and pixel-format double-buffer enable/pending, `PIXEL_ENCODING_TYPE`, uncompressed pixel encoding and component depth, `MSA_DATA`, HBLANK minimum symbol width, and 15 replicated `SDP_GSP_CONTROLn` blocks.
- GSP/SDP scheduling fields in each `SDP_GSP_CONTROLn`: continuous video/idle transmission enable, one-shot trigger and position, double-buffer enable/pending, payload size, SOF reference, deadline missed, transmission pending, and transmission line number.
- Audio and metadata packet fields: audio SDP continuous/line/send-at-hblank controls, audio HBLANK/TU interval, metadata packet enable/pending/deadline status, MSA/VBID controls, and stream-control fields.
- CRC and diagnostic fields: video CRC enable/continuous/selection, four CRC result registers, CRC status, symbol count status/control, DPHY error status, DPHY symbol count status/control, and test-pattern configuration/data fields.
- ALPM and panel replay fields: panel replay enable/status update, ALPM sleep and wake minimum symbol counts, request-offset, ready control, hardware mode control, ALPM status, ALPM start, and wake interrupt enable/status.
- DP DPHY VC and SAT fields: `DPHY_SYM32_ENABLE`, reset/reset-done, lane enable, link-rate, power-down, mux mode, PHY status, VC rate programming and update, SAT slot assignments for VC0-VC3, SAT/VC update requests, and update-pending/status bits.
- MPCC mixer fields: top/bottom select, OPP ID, MPCC mode, alpha blend/multiplied mode, active-overlap-only, global alpha/gain, background bit depth, bottom gain mode, control-current status, stereoscopic mode control, update lock select, top/bottom gains, movable color-management location, background RGB/YCbCr components, memory power controls, and disabled/idle/busy status.
- OGAM LUT and RAM fields: `MPCC_OGAM_MODE`, select/current status, PWL disable, LUT index/data/control, write color mask, read color select/debug, host select, config mode, RAM A/B start/end/offset/base/slope controls for B/G/R channels, and 34 curve-region descriptors per RAM.
- Gamut-remap fields: coefficient format, mode/current status, and A/B banks of matrix coefficient registers such as `C11_C12`, `C13_C14`, `C21_C22`, `C23_C24`, `C31_C32`, and `C33_C34`.

The repeated instance prefixes are semantically important. `DP_SYM32_ENC3`, `DP_LINK_ENC3`, and `DP_DPHY_SYM323` belong to one HPO DP output path; `MPCC0` through `MPCC3` are separate composition/mixer instances; and `MPCC_OGAM0` through `MPCC_OGAM2` are per-MPCC output gamma/remap instances.

## Control Flow

This header has no executable control flow. Runtime flow is created by consumers that include this file with the matching offset header and expand register-list macros into register tables.

Typical use is:

1. DCN 4.2 display code selects `dcn_4_2_0_offset.h` and `dcn_4_2_0_sh_mask.h`.
2. Component headers and constructors token-paste symbolic register names into register descriptors, pairing offsets/base indexes with these shift/mask definitions.
3. Runtime paths call AMD display helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, `REG_UPDATE`, or wait/poll helpers against those descriptors.
4. The driver uses the resulting masked operations during modeset, atomic plane composition, color-management programming, DP link setup, secondary-data packet scheduling, audio/metadata setup, ALPM/panel-replay handling, diagnostics, and power-management transitions.

The hardware programming order is not encoded here. For example, stream encoder enable/reset, FIFO reset, MSA/pixel-format double-buffer updates, GSP packet one-shot or continuous transmission, DPHY VC-rate/SAT programming, ALPM wake/sleep sequencing, MPCC update locks, OGAM LUT loads, and gamut-remap bank switching are sequenced by the display driver and hardware specification.

## State And Persistence Behavior

The file itself holds no mutable or persistent software state. All represented state lives in hardware registers.

Hardware-backed state described by this chunk includes:

- VPG state: generic packet update requests and pending bits, conflict/lock state, indexed ISRC data bytes, and VPG GSP memory power state.
- HPO DP stream state: encoder enable/reset state, pixel-to-symbol FIFO state, MSA words, pixel format, SDP/GSP packet scheduling, audio SDP timing, metadata packet state, VBID/stream enable, panel replay, CRC state/results, symbol counts, and ALPM control/status.
- HPO DP link/PHY state: link encoder clock state, DPHY lane/link/mux/power/reset state, virtual-channel rates, slot-allocation tables, eDP ASSR registers, ALPM configuration, test-pattern generator state, error status, and symbol counters.
- MPCC composition state: selected top/bottom inputs, selected OPP, blend mode, alpha/global gain, background color, stereo mode, movable color-management location, update-lock target, OGAM memory-power controls, and idle/busy/disabled status.
- OGAM state: selected mode and LUT bank, indexed LUT payload, RAM A/B curve start/end/base/slope/offset and region tables, gamut-remap coefficient format, active/current gamut-remap mode, and A/B matrix coefficient banks.

Persistence is hardware-defined. Values usually remain programmed until modeset, atomic update, block disable, power gating, suspend/resume, GPU reset, display engine reset, or ASIC reset rewrites them. Status, pending, interrupt-like, CRC, overflow, reset-done, and update-pending fields may be read-only, sticky, self-clearing, or valid only while the relevant block is powered and clocked. This generated header does not encode those access semantics.

## Dependencies And Integration Points

Direct dependencies:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h` supplies the matching register offsets and base-index selectors for these field names.
- AMD display register-helper infrastructure supplies the masked register access macros that consume `__SHIFT` and `_MASK` symbols.
- AMD's DCN 4.2.0 register database is the authoritative source for the generated names and bit positions.

Important integration points visible from the naming and surrounding tree:

- HPO DP stream/link code consumes `DP_SYM32_ENC*`, `DP_LINK_ENC*`, and `DP_DPHY_SYM32*` field lists for DP 2.x stream encoder, link encoder, DPHY VC-rate/SAT, ALPM, panel replay, CRC, and diagnostics.
- Generic packet and metadata paths consume the `VPG8_*`, `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL*`, audio SDP, and metadata packet fields during infoframe, SDP, audio, ISRC, and metadata programming.
- MPC/MPCC code consumes `MPCC0_*` through `MPCC3_*` for plane blending, OPP routing, update-lock selection, stereo mode, background color, and memory-power handling.
- Color-management code consumes `MPCC_OGAM*` fields for output gamma LUT programming, RAM A/B PWL region setup, bank selection/current-mode checks, and gamut-remap matrix programming.
- Generated register tables depend on exact instance alignment. The stream encoder instance `3`, link encoder instance `3`, and DPHY instance `323` must pair with the matching offsets, while MPCC and OGAM instance numbers must line up with the resource-pool pipe/plane topology.

## Risks And Failure Modes

- A wrong shift or mask can compile cleanly while corrupting adjacent fields in the same register. Failures may appear only as runtime display symptoms.
- Chunk boundaries are not semantic. This range starts after the first `VPG8_VPG_GSP_IMMEDIATE_UPDATE_CTRL` fields and ends in the middle of `MPCC_OGAM2`; final per-file reconciliation must merge adjacent chunks before making whole-block claims.
- HPO DP instance alignment is critical. Mixing `DP_SYM32_ENC3`, `DP_LINK_ENC3`, or `DP_DPHY_SYM323` with another instance's offsets can program the wrong stream or PHY path.
- GSP/SDP packet controls have trigger, pending, deadline-missed, double-buffer, and line-number fields. Incorrect masks can cause missed infoframes, stale metadata, one-shot packets that never fire, or packet updates at the wrong scanline.
- Reset, reset-done, overflow, pending, clear, and interrupt-status fields require correct access semantics in the caller. This header gives only bit positions, so consumers must preserve write-one-to-clear, self-clear, and poll timing rules from the hardware model.
- DP DPHY VC-rate and slot-allocation-table fields are bandwidth critical. Bad masks can break MST-style allocation, high-bandwidth modes, eDP ASSR, ALPM wake/sleep, panel replay, or symbol-rate accounting.
- MPCC blend and routing fields are multi-plane sensitive. Errors may only appear with certain plane counts, alpha modes, stereo modes, OPP mappings, or background formats.
- OGAM LUT and RAM A/B region fields are dense and repeated. A single wrong mask can distort color, break bank switching, corrupt only one color channel, or affect only instance 0, 1, or 2.
- Gamut-remap coefficient banks rely on paired 16-bit fields and active/current mode bits. Misprogramming can cause color matrix errors that are visible only under specific color-management configurations.
- Memory-power fields for VPG, stream encoder, MPCC OGAM, and related blocks can produce timing-dependent failures if consumers write them while a block is active or read status while clocks are gated.

## Test Signals

Useful validation signals include:

- Build AMDGPU display with DCN 4.2 enabled. Missing or renamed macros should fail in HPO DP, MPC/MPCC, VPG/APG/DME, color-management, DMUB, IRQ, or resource-table compilation.
- Mechanically compare this shift/mask range against the matching `dcn_4_2_0_offset.h` range and AMD's register database so each consumed register has matching address and field metadata.
- Validate HPO DP output path 3 with modeset, stream enable/disable, link training, high-bandwidth modes, MST or VC allocation where supported, eDP ASSR, panel replay, ALPM sleep/wake, suspend/resume, and GPU reset.
- Exercise generic packet flows: infoframes/SDPs, audio SDP, metadata packets, ISRC indexed writes, immediate and frame update requests, one-shot triggers, continuous transmission, pending/deadline status, and conflict-clear behavior.
- Exercise DP diagnostics: video CRC enable/results/status, symbol counts, DPHY error status, test patterns, PRBS/custom pattern programming, and FIFO overflow status.
- Exercise MPCC instances 0-3 with single-plane and multi-plane composition, alpha blending, global gain/alpha, top/bottom selection, OPP routing, stereo mode, background color, update locks, and memory-power transitions.
- Exercise OGAM instances 0-2 with LUT index/data access, RAM A/B PWL loads, region table programming, mode/current status polling, bank switching, gamut-remap coefficient format, and A/B matrix coefficient programming.
- Include reset and power-management scenarios: hotplug, atomic modeset, suspend/resume, display-engine reset, GPU reset, clock gating, and memory low-power transitions. Expected signals are no stuck pending bits, no unexpected CRC/overflow/error status, stable link training, and visually correct color output.

## Cross-Chunk Notes

This is a source-tree-aligned chunk report only. It intentionally does not attempt a final per-file synthesis for `dcn_4_2_0_sh_mask.h`; the merge/reconciliation lane should combine this with adjacent chunks. The previous chunk is needed for the start of `VPG8_VPG_GSP_IMMEDIATE_UPDATE_CTRL`, and the next chunk is needed for the rest of `MPCC_OGAM2` after `MPCC_OGAM2_MPCC_OGAM_RAMA_REGION_6_7`.
