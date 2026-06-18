# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 7301-9720

## Purpose

This chunk is generated AMD DPCS 3.1.4 register field metadata. It contains no executable C logic; it publishes C preprocessor constants for bit shifts and masks inside DPCSSYS CR0 raw-lane registers. Consumers pair these macros with register offsets from `dpcs_3_1_4_offset.h` and with AMD display register helpers to read, write, update, and poll lane-level PHY/PCS/FSM/IRQ state.

The requested range covers a mid-file raw-lane slice. It starts inside the tail of `DPCSSYS_CR0_RAWLANE0_DIG_PMA_XF_LANE_OVRD_OUT`, then covers the rest of lane 0 PMA/TX/RX/ATE fields, the full lane 1 PCS/FSM/IRQ/PMA/TX/RX/ATE field groups, and most of the same lane 2 groups through `DPCSSYS_CR0_RAWLANE2_DIG_PCS_XF_ATE_TX_OVRD_IN`. The final requested line is only the marker for `DPCSSYS_CR0_RAWLANE2_DIG_PCS_XF_ATE_TX_OVRD_IN_1`; that register's fields continue in the next chunk.

The range contains 2,145 `#define` lines: 1,071 `__SHIFT` definitions and 1,074 `_MASK` definitions. It is split across `RAWLANE0` tail coverage, complete `RAWLANE1` coverage for these blocks, and partial `RAWLANE2` coverage. Although this file lives under a local `ceph-client` source mirror, the content is AMDGPU display hardware metadata, not Ceph or distributed filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocation paths, locking primitives, or local includes in this chunk. The interface is the generated macro namespace:

- `<register>__<field>__SHIFT`: the low bit position of a field inside a 16-bit DPCS indirect register.
- `<register>__<field>_MASK`: the bit mask for the same field.
- Register names use lane-scoped prefixes such as `DPCSSYS_CR0_RAWLANE1_DIG_PCS_XF_...`, `DPCSSYS_CR0_RAWLANE1_DIG_FSM_...`, `DPCSSYS_CR0_RAWLANE1_DIG_IRQ_CTL_...`, and `DPCSSYS_CR0_RAWLANE1_DIG_PMA_XF_...`.

Major field families in this slice:

- `PMA_XF_*`: lane-to-PMA interface override and status fields, including MPLLA/MPLLB lane enable, supervisor state override, TX/RX request and reset override, beacon and async enable override, data-enable override, TX-to-RX and RX-to-TX loopback enable override, retune request/ack, MPHY PWM/term control, RX PMA async/PWM selection, and RX IQ phase-adjust override.
- `TX_CTL_*` and `RX_CTL_*`: lane TX/RX controller controls and status, including TX wait time before MPLL off, whether RX detection is allowed in power states P0/P0s/P1/P2, TX clock enable and selection, async beacon wait time, DCC continuous status, OCLA enables, RX control FSM enable, rate changes in P1, RX loss-of-signal mask count, RX data-enable override delay/count, OFFCAN and adaptation continuous status, and UPCS OCLA data/clock enables.
- `PCS_XF_TX_*` and `PCS_XF_RX_*`: PCS transmit and receive override/status fields for lane state, rate, width, pstate, low-power detect, MPLL selection/enables, TX/RX reset and request signaling, data-valid signaling, TX and RX data enables, async data and beacon controls, serial/parallel loopback controls, RX loss-of-signal thresholding, adaptation/off-cancel controls, VCO/ref load override values, and TX pre/main/post direction outputs.
- `PCS_XF_ATE_*`: ATE-oriented override registers for manufacturing, lab, or low-level bring-up paths. These fields can override rate, width, pstate, LPD, MPLL state, async data, VBOOST, IBOOST, beaconing, RX LOS behavior, RX adaptation requests, continuous adaptation/off-cancel behavior, VCO load values, ref load values, RX valid, and lane loopback/data enable state.
- `FSM_*`: lane finite-state-machine override, monitor, calibration, adaptation, and status fields. Covered registers expose manual memory-address monitor selectors, FSM state/address/running/debug status, fast-path timers for RX startup/adaptation/AFE/DFE/bypass/reference/IQ calibration, supervisor and TX common-mode/RX-detect timing, RX power-up/VCO wait/VCO calibration, common calibration status, continuous RX calibration/adaptation/data/phase/AFE timing, aggregated fast flags, CR lock status, TX DCC flags/status, TX EQ update flags, RCAL status, and RX IQ phase offset.
- `IRQ_CTL_*`: lane interrupt request, clear, and mask fields for RX reset/request/rate/pstate/adaptation, RX phase-2 calibration, lane transceiver mode, loopback, DCC on-demand, TX reset/request, and the combined IRQ masks. Many individual IRQ and IRQ clear registers in this chunk are single-bit fields.
- `PCS_XF_TXRX_TERM_*` and `PCS_XF_RX_EQ_*`: TX/RX termination control, RX EQ delta IQ override, FFE/DCO adaptation override, VGA override, and phase-2 calibration control fields.

Reserved-field macros are generated alongside active fields. They are not API invitations to write reserved bits; they document layout and let generated code or diagnostics mask whole register widths when needed.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMD display code:

1. DCN 3.1.4 resource code includes `dpcs_3_1_4_offset.h` and this `dpcs_3_1_4_sh_mask.h`.
2. Register helper macros and generated register-field tables token-paste register and field names into constants such as `DPCSSYS_CR0_RAWLANE1_DIG_PCS_XF_RX_OVRD_IN_2__VCO_LD_VAL_OVRD_MASK`.
3. The companion offset header provides `ixDPCSSYS_CR0_RAWLANE<n>_...` register indices. This mask header provides field placement within those indirect registers.
4. Link encoder, PHY bring-up, link training, diagnostics, IRQ handling, and low-level display code use `REG_SET`, `REG_UPDATE`, `REG_GET`, read-modify-write helpers, and poll/wait helpers to apply or inspect the represented fields.

The macros do not encode ordering. Consumers must still sequence PLL enablement, power-state transitions, TX/RX reset handshakes, RX detection, link training, clock gating, calibration/adaptation, retuning, IRQ clear/mask operations, loopback setup, and suspend/resume restoration correctly.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It describes MMIO or indirect-register-backed GPU state. The represented hardware state includes:

- Per-lane PCS state for TX/RX request, reset, pstate, LPD, width, rate, MPLL selection, MPLL state, async data, beaconing, loopback, data-enable, RX-valid, RX LOS, and adaptation signaling.
- Per-lane PMA interface state for lane MPLL enables, PMA supervisor state, TX/RX requests and acks, retune handshakes, PWM and termination controls, RX async selection, and IQ phase-adjust override.
- Calibration and adaptation control/status state for RX startup, AFE/DFE/reference/IQ calibration, continuous adaptation/calibration, VCO and common calibration status, DCC status, TX EQ update indication, RCAL status, and CR lock.
- Per-lane interrupt state for request, clear, and mask paths. Several fields are likely sticky, write-one-to-clear, or clear-on-read depending on the hardware register, but this generated mask header does not encode those side effects.
- Test, lab, or bring-up override state through ATE registers and OCLA observability controls.

Persistence is hardware-defined. Control fields generally retain values until the lane block is reprogrammed, power-gated, reset, or the GPU enters a suspend/resume or ASIC reset path. Status, IRQ, clear, ack, monitor, and calibration fields may be volatile or side-effect-sensitive. The generated shift/mask file deliberately does not classify fields as read-only, write-only, sticky, self-clearing, or write-one-to-clear.

## Dependencies And Integration Points

This chunk depends on AMD's generated DPCS 3.1.4 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h`, which gives the `ixDPCSSYS_CR0_RAWLANE<n>_...` register indices. The offsets show the lane stride used by these masks, for example lane 0 at `0x3000`-style addresses, lane 1 at `0x3100`-style addresses, and lane 2 at `0x3200`-style addresses for these register families.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c`, which directly includes this header together with the matching DPCS offset header and the DCN 3.1.4 register headers.
- AMD display register helper infrastructure such as `reg_helper.h` and the generated field-table macros that consume `*_MASK` and `*__SHIFT` definitions.

The broader integration point is the DCN/DPCS display link stack. These fields are lane-local primitives beneath link encoder setup, DisplayPort and HDMI PHY programming, power sequencing, training pattern handling, RX detection, AUX-related link bring-up, diagnostics, and IRQ processing. Other ASIC generations in this tree use the same naming pattern, so drift from neighboring generated headers can be detected mechanically, but the authoritative contract for this ASIC generation is the `dpcs_3_1_4_*` pair.

## Risks And Edge Cases

- Generated metadata drift is the central risk. A wrong mask or shift can compile cleanly while causing writes to the wrong bit, partial writes to a multi-bit field, broken reads, stuck status polling, or reserved-bit writes.
- The chunk is lane-repetitive and copy-sensitive. Lane 1 and lane 2 should generally preserve the same field layout for corresponding registers, while lane 0 coverage is split across neighboring chunks. A single lane-specific typo may only fail on some link-lane counts, connector mappings, link rates, or training patterns.
- Chunk boundaries are artificial. The range begins after the start of `RAWLANE0_DIG_PMA_XF_LANE_OVRD_OUT` and ends before the fields for `RAWLANE2_DIG_PCS_XF_ATE_TX_OVRD_IN_1`; adjacent chunks are required before making complete per-file claims.
- Override fields are high risk because many pairs use a value bit plus an enable bit. Setting an override value without its enable may do nothing; setting an enable with a stale value can force a lane into an unintended rate, width, pstate, reset, async, data-enable, or loopback state.
- IRQ clear and mask fields are side-effect-sensitive. Incorrect shifts can leave interrupts stuck, clear the wrong condition, mask real link faults, or produce hotplug/link-training instability that only appears under error paths.
- Calibration and adaptation fields are timing-sensitive. Bad fast-timer, continuous-adaptation, VCO, IQ, AFE, DFE, DCC, or RCAL fields can cause intermittent link failures, marginal signal integrity, or resume-only regressions.
- Reserved masks exist in the generated header, but writing reserved bits remains unsafe unless the consuming code has a hardware-specific reason.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU/DC with DCN 3.1.4 support enabled. Missing or renamed macros should fail in `dcn314_resource.c` and any generated register-field table that references DPCS fields.
- Mechanically verify that every active field in lines 7301-9720 has exactly one `__SHIFT` and one `_MASK`, allowing for the known chunk-boundary exceptions at the beginning and end.
- Cross-check corresponding lane 1 and lane 2 registers for identical field layouts where the hardware register names match, and compare lane 0 fields by merging adjacent chunks.
- Diff this range against AMD's authoritative DPCS 3.1.4 database or nearby generated headers such as `dpcs_3_0_3_sh_mask.h`, `dpcs_4_0_0_sh_mask.h`, and `dpcs_4_2_0_sh_mask.h` where compatibility is expected.
- Exercise display paths that use different physical lanes and lane counts: 1-lane, 2-lane, and 4-lane DisplayPort where available; HDMI/FRL or TMDS modes where applicable; link-rate changes; training retries; lane remapping; and suspend/resume.
- Validate IRQ behavior by observing RX reset/request/rate/pstate/adaptation events, RX phase-2 calibration events, lane transceiver mode events, loopback events, DCC on-demand events, and TX reset/request events. Look for stuck IRQs, missed clears, and unexpected masks.
- Run signal-integrity and link-stability checks around RX detection, retune, continuous adaptation, DCC, VCO calibration, TX EQ updates, loopback modes, and high-rate modes. Kernel logs should be watched for link-training failures, AUX or DPCD errors caused by failed link bring-up, display blanking, CRC mismatch, underflow, and resume failures.

## Cross-Chunk Notes

Previous chunks are needed for the beginning of `RAWLANE0_DIG_PMA_XF_LANE_OVRD_OUT` and the earlier lane 0 PCS/FSM/IRQ fields. Later chunks are needed for `RAWLANE2_DIG_PCS_XF_ATE_TX_OVRD_IN_1` and the remaining DPCS 3.1.4 register-field namespace. The final per-file research document should merge those chunks before claiming full coverage of all raw lanes or the complete `dpcs_3_1_4_sh_mask.h` header.
