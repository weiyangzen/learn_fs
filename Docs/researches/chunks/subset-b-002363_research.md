# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 62004-64388

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice. It contains no executable C logic; it publishes preprocessor constants for bit positions (`__SHIFT`) and masks (`_MASK`) used by AMDGPU Display Core code when composing or decoding DPCS indirect hardware register fields.

The requested range contains 2,119 `#define` entries and 263 register comment groups. It starts at the tail of `DPCSSYS_CR2_LANEX_DIG_RX_CDR_CDR_CTL_4`, with only the final masks for that register in this chunk, then covers CR2 lane-X RX clock/data-recovery status, DPLL bounds, RX adaptation control/status, RX statistics, digital/analog lane controls, raw lane-X PCS/FSM/IRQ/PMA/TX/RX control fields, and early CR3 supervisor fields. It ends on the comment for `DPCSSYS_CR3_SUP_DIG_MPLLB_HDMI_CLK_OVRD_IN`; that register's shift/mask definitions are outside this slice.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, memory allocations, callbacks, or direct MMIO operations in this range. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for the hardware field.
- `<REGISTER>__<FIELD>_MASK`: bit mask used to isolate, compose, or update the field.

The main macro families in this chunk are:

- `DPCSSYS_CR2_LANEX_DIG_RX_CDR_*` and `DPCSSYS_CR2_LANEX_DIG_RX_DPLL_*`: CDR status and DPLL frequency/bound fields, including `PHUG_VALUE`, `FRUG_VALUE`, current DPLL frequency, and upper/lower frequency-bound controls.
- `DPCSSYS_CR2_LANEX_DIG_RX_ADPTCTL_*`: RX adaptation setup, reset, status, slicer, DFE, DAC-selection, and CR bank access fields. The groups cover adaptation timers and start bits, CTLE/VGA/attenuator/DFE enable and thresholds, adaptation step sizes, initial error values, reset bits for individual adaptation loops, done/status readbacks for ATT/VGA/CTLE/DFE taps, even/odd data/error VDAC offsets, slicer controls, and indexed CR bank address/data fields.
- `DPCSSYS_CR2_LANEX_DIG_RX_STAT_*`: RX statistic and pattern-match collection fields, including load values, data masks, match controls, statistic controls, sample-count and statistic-count words, calibration-comparison clock control, and statistic stop control.
- `DPCSSYS_CR2_LANEX_DIG_ANA_*` and `DPCSSYS_CR2_LANEX_ANA_*`: digital-facing analog override/readback and analog lane fields for TX override outputs, termination codes, EQ override words, RX control/power/VCO overrides, RX calibration, DAC controls, AFE ATT/VGA/CTLE, scope/slicer controls, IQ phase/sense/calibration enable, signal-change gating, analog status, signal-detect overrides, TX DCC DAC overrides, TX power/measurement/ATB/DCC/termination/misc controls, RX clock/CDR/slicer/power/squelch/calibration/ATB controls, and reserved analog latches.
- `DPCSSYS_CR2_RAWMEM_DIG_*`: raw common ROM/RAM single-data fields for CR2 common memory windows.
- `DPCSSYS_CR2_RAWLANEX_DIG_PCS_XF_*`: raw lane-X PCS transfer, override, ATE, and direction fields for TX/RX pstate, width, rate, MPLL selection, beacon, data-valid, adaptation request/ack/FOM, TX pre/main/post directions, lane number, reserved words, termination controls, RX EQ delta/IQ controls, PH2 calibration, loopback, and ATE override paths.
- `DPCSSYS_CR2_RAWLANEX_DIG_FSM_*`: raw lane-X finite-state-machine override, monitor, fast-sequence, calibration/adaptation, common calibration, flag, lock, DCC status, OCLA, TX EQ update, RCAL status, and RX IQ phase-offset fields.
- `DPCSSYS_CR2_RAWLANEX_DIG_IRQ_CTL_*`: raw lane-X IRQ request, status, clear, and mask fields for RX reset/request/rate/pstate/adaptation/PH2 calibration, lane transceiver mode, lane serial loopback, DCC on-demand, and TX reset/request events.
- `DPCSSYS_CR2_RAWLANEX_DIG_PMA_XF_*`: raw PMA transfer/override fields for lane, supervisor, TX, RX, RTUNE, MPHY, and RX adaptation override interfaces.
- `DPCSSYS_CR2_RAWLANEX_DIG_TX_CTL_*` and `DPCSSYS_CR2_RAWLANEX_DIG_RX_CTL_*`: TX/RX lane control, DCC/off-cancel/adaptation continuous-status, clock/data-enable/LOS-mask controls, and OCLA fields.
- `DPCSSYS_CR3_SUP_DIG_*`: the start of the CR3 supervisor block, covering ID-code low/high readback, reference-clock overrides, MPLLA divider and HDMI clock overrides, and MPLLB divider override definitions. The next CR3 HDMI-clock register is only introduced by comment at this chunk boundary.

Most masks are 16-bit-style values with an `L` suffix, matching the DPCS indirect register-field convention. The companion offset header maps representative groups in this range to offsets such as `0x9058` for `DPCSSYS_CR2_LANEX_DIG_RX_CDR_STAT`, `0xe0c8` for `DPCSSYS_CR2_RAWLANEX_DIG_PCS_XF_TX_OVRD_IN_2`, and `0x0006` for the CR3 `DPCSSYS_CR3_SUP_DIG_MPLLB_HDMI_CLK_OVRD_IN` register introduced at the end.

## Control Flow

This header has no runtime control flow. It participates in compile-time register-table construction:

1. DCN 3.1.5 resource code includes `dpcs_4_2_2_offset.h` and this shift/mask header.
2. Generated register-list, shift-list, and mask-list initializers token-paste register and field names into AMD Display Core resource tables.
3. Runtime display code uses register helpers to read, write, get, set, or update individual fields through matching offsets and these shift/mask constants.
4. Actual sequencing for DPLL/CDR programming, RX adaptation, statistic collection, analog override programming, PCS/PMA transfer control, FSM sequencing, IRQ handling, lane calibration, and CR3 supervisor reference-clock/MPLL setup lives in AMDGPU display code, firmware, and hardware state machines outside this header.

The macros only describe bit layout. They do not encode reset values, access width beyond the mask shape, read-only/write-only status, write-one-to-clear behavior, self-clearing behavior, polling order, clock-domain restrictions, or power-domain validity.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in CR2 lane-X and CR3 supervisor DPCS registers:

- CDR/DPLL fields expose live or programmed receive-clock recovery gains and frequency bounds.
- RX adaptation fields hold configuration and readback state for ATT, VGA, CTLE, DFE taps, slicers, DAC selections, indexed CR bank access, adaptation reset, and adaptation-done conditions.
- RX statistic fields hold match/mask/sample/count configuration and statistic counters used for PHY or receiver diagnostics.
- Digital/analog lane fields hold TX/RX override values and enables, term-code and EQ controls, VCO/calibration/DAC/slicer/scope controls, analog status, signal-detect overrides, TX DCC controls, RX power/CDR/squelch/calibration/ATB state, and reserved analog latches.
- Raw lane-X PCS/PMA/FSM/IRQ/TX/RX fields expose cross-interface control and state for link rate, pstate, width, MPLL selection, TX/RX data/valid paths, adaptation request/ack/FOM, direction updates, ATE overrides, PMA handoff, fast calibration/adaptation sequencing, common calibration status, IRQ latches/clears/masks, OCLA debug, DCC status, and loopback or termination override paths.
- CR3 supervisor fields expose ID-code readback and early reference-clock/MPLLA/MPLLB divider and HDMI-clock override controls.

Persistence is hardware-defined. Programmed control and override fields generally remain until modeset/link reprogramming, PHY power gating, suspend/resume, GPU reset, ASIC reset, or firmware/driver reinitialization rewrites them. Status, statistic, IRQ, ACK, lock, done, calibration, and diagnostic readback fields may be latched, sampled, self-clearing, read-only, or only valid while the relevant lane/common clock and power domains are active. This generated header does not define those semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 4.2.2 register database and its companion address map:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies matching `ixDPCSSYS_*` offsets for the register groups whose fields are defined here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` directly includes both `dpcs_4_2_2_offset.h` and `dpcs_4_2_2_sh_mask.h`, tying this generated contract to DCN 3.1.5 resource construction.
- The AMD Display Core register-helper layer consumes generated offset, shift, and mask tables to access hardware without open-coding bit positions.
- Firmware and hardware state machines share these fields with the driver for RX adaptation, signal detection, DCC and analog calibration, CDR/DPLL tuning, PCS/PMA handoff, IRQ signaling, test/ATE override routes, OCLA/debug capture, and supervisor reference-clock/MPLL setup.

Behaviorally, this range sits below the user-facing display stack. DisplayPort/HDMI link bring-up, PHY clock programming, lane calibration, hotplug/modeset, suspend/resume, diagnostics, and manufacturing/ATE flows can depend on these bitfield definitions being exactly correct.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while updating the wrong hardware bit, corrupting a reserved field, or decoding status incorrectly.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the companion offset header, firmware assumptions, and silicon documentation.
- The `LANEX` and `RAWLANEX` naming represents a repeated lane-template space rather than one ordinary C abstraction. A consumer that pairs these masks with the wrong lane or raw/normal offset block can manipulate the wrong hardware path.
- Many registers pair override value bits with override enable bits. Leaving enable bits asserted after debug, ATE, or validation use can bypass normal PHY, PCS, PMA, analog, CDR, DPLL, or supervisor state-machine control.
- RX adaptation, DFE tap, slicer, statistic, signal-detect, DCC, DAC, VCO, termination, and analog status fields are calibration-sensitive. Incorrect bit definitions can cause subtle link-training failures, degraded margins, misleading debug readbacks, or stuck polling loops.
- IRQ status/clear/mask groups repeat names across RX reset/request/rate/pstate/adaptation/PH2 and TX reset/request events. Misusing a clear or mask bit can hide real link events or produce repeated interrupt handling.
- PCS/PMA/FSM transfer fields have similar names across override input, hardware input, override output, and output/status groups. Consumers must pair each mask with the correct register offset and access direction.
- Supervisor reference-clock and MPLL divider/HDMI-clock override fields affect shared clocking. Bad masks can produce clock instability, lock failures, black screens, rate-specific retraining loops, or compliance regressions.
- Chunk boundaries are artificial. This chunk starts mid-register with only `DPCSSYS_CR2_LANEX_DIG_RX_CDR_CDR_CTL_4` masks and ends at the comment for `DPCSSYS_CR3_SUP_DIG_MPLLB_HDMI_CLK_OVRD_IN` before that register's definitions.

## Test Signals

Useful validation combines generated-header checks with display hardware behavior:

- Build AMDGPU display support for DCN 3.1.5. Missing, renamed, or malformed macros should fail where `dcn315_resource.c` and generated register tables consume DPCS 4.2.2 symbols.
- Mechanically verify that complete register groups in this range have matching `__SHIFT` and `_MASK` definitions, allowing the known start-boundary exception for `DPCSSYS_CR2_LANEX_DIG_RX_CDR_CDR_CTL_4` and the end-boundary comment-only exception for `DPCSSYS_CR3_SUP_DIG_MPLLB_HDMI_CLK_OVRD_IN`.
- Cross-check every complete register group in this chunk against `dpcs_4_2_2_offset.h`, especially the CR2 `LANEX` to `RAWLANEX` transition and the CR3 `dpcssys_cr3_rdpcstxcrind` address-block transition.
- Diff against AMD's generated source register database and adjacent DPCS versions where compatible hardware layout is expected.
- Exercise DP and HDMI link bring-up across lane counts, link rates, power states, and hotplug/modeset paths. Expected signals are stable link training, successful RX adaptation, valid CDR/DPLL status, correct signal-detect behavior, clean IRQ handling, and no unexpected lane or supervisor timeout.
- Exercise suspend/resume, GPU reset, low-power entry/exit, and display disable/enable paths to catch stale override, reference-clock, MPLL, PCS/PMA, DCC, analog calibration, or adaptation state.
- Use register dumps or PHY debug traces during failures to confirm adaptation values, DFE tap readbacks, slicer/DAC values, statistic counters, analog status, PCS/PMA transfer signals, FSM fast flags, IRQ status/clear behavior, DCC status, OCLA capture fields, CDR/DPLL values, and CR3 supervisor reference-clock/MPLL divider decodes correctly.
- Where supported, run debug/manufacturing paths for ATE overrides, loopback, ATB, analog test bus, OCLA, PMA override, PCS override, DCC bank access, signal-detect override, and supervisor clock overrides, then confirm normal link training resumes after overrides are released.

## Cross-Chunk Notes

The previous chunk should contain the beginning of `DPCSSYS_CR2_LANEX_DIG_RX_CDR_CDR_CTL_4` and earlier CR2 CDR control fields. This chunk continues from that partial register, covers the bulk of CR2 lane-X RX adaptation/statistics/analog/raw PCS-FSM-IRQ-PMA control definitions, and enters the CR3 supervisor address block at line 64329. The next chunk should provide the definitions for `DPCSSYS_CR3_SUP_DIG_MPLLB_HDMI_CLK_OVRD_IN` and continue the CR3 supervisor clock/MPLL register map. The final per-file report should reconcile these artificial boundaries before making whole-file claims about all DPCS 4.2.2 register groups.
