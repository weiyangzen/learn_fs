# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 24370-26787

## Purpose

This chunk is a generated AMD DPCS 3.1.4 shift/mask header slice for DCN 3.1.4 display PHY/link hardware. It contains no executable C logic; it publishes preprocessor constants that describe bit positions and bit masks for indexed DPCS CR registers under `DPCSSYS_CR1_RAWLANE*`.

The requested range contains 2,145 `#define` entries: 1,073 `__SHIFT` macros and 1,072 `_MASK` macros. The line boundary is artificial. The chunk starts in the middle of `DPCSSYS_CR1_RAWLANE0_DIG_PMA_XF_RX_OVRD_OUT`, after the `RX_REQ_*` shifts but before their masks, and ends inside `DPCSSYS_CR1_RAWLANE2_DIG_PCS_XF_ATE_RX_OVRD_IN_2`, before that register's masks.

Although this file lives under a local `ceph-client` source mirror, this is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this range. The public surface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit position for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for isolating or updating that field.

The chunk covers DPCS CR1 raw-lane register fields for portions of lanes 0, 1, and 2:

- `DPCSSYS_CR1_RAWLANE0_*`: tail fields for lane 0, mostly PMA receive override/acknowledge, lane retune, MPHY override, RX adaptation override, TX/RX control, and ATE PCS override registers.
- `DPCSSYS_CR1_RAWLANE1_*`: a complete raw-lane 1 block, including PCS TX/RX override and PCS-facing state, RX adaptation status/FOM and TX equalization direction fields, lane number/reserved registers, ATE override fields, FSM monitor/fast-sequence status, IRQ status/clear/mask fields, PMA override/status registers, and TX/RX control registers.
- `DPCSSYS_CR1_RAWLANE2_*`: the beginning and most of raw-lane 2, with the same PCS, FSM, IRQ, PMA, TX control, RX control, and ATE override structure as lane 1, stopping midway through `ATE_RX_OVRD_IN_2`.

Important field families include:

- PCS TX controls: `PSTATE`, `LPD`, lane `WIDTH`, link `RATE`, `MPLLB_SEL`, `MPLL_EN`, `OVRD_EN`, master MPLL state overrides, `DETRX_REQ`, `VBOOST_EN`, `IBOOST_LVL`, beacon enable, serial loopback enable, TX data enable, and TX async data overrides.
- PCS RX controls and status: RX request/reset/rate/pstate/width/low-power/valid/data-enable inputs, loss-of-signal LFPS and threshold overrides, adaptation request/continuous flags, offset-cancel continuous flags, VCO/reference load overrides, RX adaptation acknowledge, figure-of-merit readback, and RX-to-TX equalization direction fields for pre/main/post cursor.
- PMA controls and handshakes: lane/PMA/supervisor override inputs and outputs, TX/RX PMA acknowledge fields, TX/RX PMA data-enable overrides, RX reset/request overrides, lane retune request and acknowledge, MPHY PWM/async/termination override fields, and RX IQ phase adjustment map override.
- FSM status and debug fields: override controls, memory-address monitor, current FSM state and substate, fast RX startup/adaptation/calibration stage bits, common calibration MPLL/RCAL status, TX DCC flags/status, OCLA control/status, TX EQ update flag, RX IQ phase offset, CR lock flags, and broad fast-state flag readbacks.
- IRQ fields: RX reset/request/rate/pstate/adaptation request/adaptation disable IRQ status and clear registers; lane transceiver mode IRQ; RX phase-2 calibration request/disable IRQs; lane RX-to-TX serial loopback IRQ; DCC on-demand IRQ; TX reset/request IRQs; and `IRQ_MASK`/`IRQ_MASK_2` enable masks.
- TX/RX control registers: TX FSM timing and RX detect permissions across power states, TX clock enable/source/beacon wait fields, TX DCC continuous status, RX control FSM enable and rate-change-in-P1 control, RX LOS mask count, RX data-enable override timing, and continuous offset-cancel/adaptation status.

Most registers in this slice are 16-bit indirect CR register layouts, visible from masks such as `0xFFFFL`, `0xFFFEL`, and field masks within bits 0-15.

## Control Flow

This header has no runtime control flow. Its role is compile-time metadata for AMDGPU display register helpers:

1. DCN 3.1.4 resource code includes `dpcs_3_1_4_offset.h` and this shift/mask header.
2. Link encoder resource tables use token-pasting macros such as `DPCS_DCN31_MASK_SH_LIST(__SHIFT)` and `DPCS_DCN31_MASK_SH_LIST(_MASK)` to populate shift and mask structures.
3. Runtime link encoder code calls AMD display register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.
4. The helpers combine register offsets, shifts, and masks to update DPCS fields without disturbing adjacent hardware bits.

The macros in this chunk do not encode sequencing. PHY reset, lane power state changes, MPLL selection, TX/RX request/ack handshakes, RX adaptation, calibration, IRQ acknowledgement, retuning, and loopback/test overrides are ordered by driver code and hardware specifications outside this generated file.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It describes hardware-visible lane state:

- Per-lane TX state for link rate/width, power state, low-power detect, MPLL enable/source, beaconing, voltage/current boost, TX data enable, async data, loopback, and reset/request handshakes.
- Per-lane RX state for request/reset/rate/pstate/width, RX valid/data enable, low-power detect, loss-of-signal threshold and LFPS behavior, adaptation request/continuous operation, offset-cancel continuous operation, RX IQ phase adjustment, and VCO/reference load override values.
- Calibration and monitor state for FSM fast-sequence progress, RX AFE/DFE/IQ/reference-level/VCO calibration, RX continuous adaptation/data/phase/AFE calibration, common MPLL/RCAL status, TX DCC state, CR lock, OCLA, and TX equalization update flags.
- Interrupt state for RX/TX request/reset/rate/pstate/adaptation/phase-calibration/loopback/DCC events, including separate clear and mask registers.
- PMA/MPHY handshakes, retune request/acknowledge state, and supervisor/PMA override paths.

Persistence and side effects are hardware-defined. Configuration fields usually remain until the lane is reprogrammed, the link is disabled, suspend/resume restores state, power gating removes state, or a GPU/ASIC reset occurs. Status, IRQ, clear, acknowledge, and monitor fields can be read-only, sticky, write-one-to-clear, self-clearing, or valid only while the DPCS block and relevant PHY clocks are powered. The generated masks do not carry access semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 3.1.4 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h` provides matching indirect register identifiers such as `ixDPCSSYS_CR1_RAWLANE1_DIG_*` and `ixDPCSSYS_CR1_RAWLANE2_DIG_*`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c` directly includes both DPCS 3.1.4 generated headers and initializes link encoder shift/mask tables with `DPCS_DCN31_MASK_SH_LIST`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h` defines the DCN 3.1 DPCS register and field-list macros consumed by DCN 3.1.4 resources. Those public lists mostly expose the higher-level `RDPCSTX*` DPCS fields used by link encoder code; this chunk provides lower-level CR raw-lane fields that must remain name-compatible with generated indirect CR offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.c` and related DCN 3.1 link encoder paths consume the register tables for DP/HDMI PHY setup, transmitter enable/disable, DP Alt Mode checks, clocking, lane state, and DPCS interrupt control.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_link_encoder.*` uses related RDPCS/DPCS register metadata for high-performance DisplayPort link encoder behavior.

Behaviorally, this slice sits under display link bring-up and diagnostics: DP/HDMI PHY lane programming, receiver detection, link-rate and lane-width selection, MPLL state, lane calibration/adaptation, equalization, retuning, interrupt handling, test/ATE override paths, and debug/status readback.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while updating the wrong indirect CR bit.
- The file is generated. Manual edits risk divergence from the authoritative AMD register database, the matching offset header, firmware assumptions, and silicon documentation.
- Chunk boundaries are not semantic. The first register has masks for fields whose shifts are in the previous chunk, while the final register has shifts whose masks are in the next chunk.
- Lane layouts are highly repetitive. A generator error can affect only raw lane 1 or raw lane 2, so one working lane does not prove the others are correct.
- Register names mix normal control, override, status, clear, mask, ATE, and reserved fields. Using a status/clear/mask field with the wrong access convention can leave IRQs stuck, miss lane events, or acknowledge the wrong condition.
- TX/RX power-state, rate, width, MPLL, and request/reset fields are sequencing-sensitive. Incorrect masks can cause failed link training, blank displays, unstable DP Alt Mode, bad HDMI/DP PHY enable, or resume-only failures.
- Calibration/adaptation fields are timing-sensitive. Bad masks around RX AFE/DFE/IQ/VCO/reference-level calibration or continuous adaptation can produce marginal links, intermittent bit errors, or failures only at high link rates.
- PMA and MPHY override fields can bypass normal hardware control. Accidentally enabling override bits or writing wrong override values can force lanes into loopback, reset, disabled data paths, invalid termination, or unsupported async/PWM modes.
- IRQ mask and clear fields are per-event and per-lane. Cross-lane copy mistakes can cause interrupt storms, lost RX/TX request transitions, or misleading diagnostics when only one connector path is active.
- Reserved field masks occupy large portions of many 16-bit registers. Read-modify-write paths must preserve reserved bits according to hardware guidance rather than assuming all visible bits are safe to modify.

## Test Signals

Useful validation combines generated-header consistency checks with hardware behavior:

- Build AMDGPU display support with DCN 3.1.4 enabled. Missing or renamed macros should surface in `dcn314_resource.c`, `dcn31_dio_link_encoder.h`, and related DPCS register-table construction.
- Mechanically compare lines 24370-26787 against AMD's authoritative DPCS 3.1.4 register database, including the boundary cases where fields are split across adjacent chunks.
- Cross-check every register prefix in this range against `dpcs_3_1_4_offset.h` to ensure corresponding `ixDPCSSYS_CR1_RAWLANE*` offsets exist.
- Run static checks that every complete field in this chunk has a paired `__SHIFT` and `_MASK`, allowing the known artificial boundary exceptions at `RAWLANE0_DIG_PMA_XF_RX_OVRD_OUT` and `RAWLANE2_DIG_PCS_XF_ATE_RX_OVRD_IN_2`.
- Compare repeated lane 1 and lane 2 layouts for expected structural identity, while accounting for the fact that lane 2 is truncated by this chunk boundary.
- Exercise DP and HDMI link bring-up, link training, disable/re-enable, hotplug, suspend/resume, and GPU reset on DCN 3.1.4 hardware. Expected signals are stable modesets, correct lane count/rate behavior, no stuck TX/RX request or reset handshakes, and no DPCS interrupt storms.
- Test high-rate DisplayPort modes, DP Alt Mode, MST where available, and reduced link-rate fallback to catch lane width/rate/MPLL/equalization mask issues.
- Capture DPCS/PHY register dumps during successful and failing link training to verify RX adaptation, calibration status, TX DCC status, CR lock, and IRQ bits decode consistently with the shift/mask definitions.
- Exercise diagnostic or manufacturing-style paths only in controlled environments: loopback, ATE overrides, PMA/MPHY overrides, OCLA, retune, and forced adaptation/offset-cancel controls.

## Cross-Chunk Notes

The previous chunk owns the beginning of raw lane 0 and the first two `RX_REQ_*` shifts for `DPCSSYS_CR1_RAWLANE0_DIG_PMA_XF_RX_OVRD_OUT`. This chunk then finishes the lane 0 tail and covers raw lane 1 fully. The next chunk must finish `DPCSSYS_CR1_RAWLANE2_DIG_PCS_XF_ATE_RX_OVRD_IN_2`, continue lane 2, and likely cover later lane 2/lane 3 definitions. The final per-file research document should reconcile those boundaries before making whole-file claims about all DPCS CR1 raw lanes.
