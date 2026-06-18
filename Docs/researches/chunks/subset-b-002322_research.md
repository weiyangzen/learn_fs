# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 81060-83443

## Scope

This chunk is a generated AMD DPCS 4.2.0 shift/mask header slice. It covers lines 81060-83443 and defines 2,118 preprocessor constants: 1,064 `__SHIFT` macros and 1,054 `_MASK` macros. The mismatch is expected for this exact slice because it starts with the final mask of `DPCSSYS_CR3_LANEX_DIG_TX_PWRCTL_TX_PSTATE_P2` and ends inside the shift half of `DPCSSYS_CR3_RAWLANEX_DIG_PMA_XF_TX_OVRD_OUT`, before that register's masks.

The content is declarative hardware metadata. There are no C functions, structs, enums, branches, loops, allocation paths, locks, direct MMIO accesses, or local software state. The public surface is the macro namespace consumed by AMDGPU/DC register helpers together with the matching DPCS offset header.

## Purpose

The header provides symbolic bit positions for DPCS 4.2.0 display PHY registers. Each hardware field is represented by a shift and a mask so callers can compose, update, and decode register values without hard-coding raw bit constants.

This range covers the late CR3 lane transceiver block. It begins at lane-X TX power sequencing, then covers CR3 lane-X RX power sequencing, RX VCO calibration, RX CDR/DPLL/adaptation/statistics, MPHY controls, digital analog TX/RX overrides, analog TX/RX controls and test-bus fields, raw memory placeholders, raw PCS lane interface fields, raw lane FSM status/fast-path controls, raw lane IRQ status/clear/mask registers, and ends in raw PMA TX override output fields.

## Important APIs, Types, And Macros

There are no callable APIs or local data types. The effective API is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: field bit offset.
- `<REGISTER>__<FIELD>_MASK`: field mask for extraction, clearing, or insertion.

Important macro families in this chunk:

- `DPCSSYS_CR3_LANEX_DIG_TX_PWRCTL_*`: TX P2 reserved tail, TX power-up timing, DCC CR-bank address/data, DCC DAC control/range/select/ack/address, TX clock alignment, and TX LBERT control.
- `DPCSSYS_CR3_LANEX_DIG_RX_PWRCTL_*`: RX P0/P0S/P1/P2 power-state tables and RX power-up timing. Fields describe AFE, clock regulator, clock, deserializer, CDR, VCO reset/calibration, continuous calibration, digital clock, equalization, adaptation, and DFE enables.
- `DPCSSYS_CR3_LANEX_DIG_RX_VCOCAL_*`: RX VCO calibration control, timing, calibration interval/sequence settings, and status fields such as calibration done, low-frequency indication, VCO code, reference code, and thermometer-like state.
- `DPCSSYS_CR3_LANEX_DIG_RX_CDR_*` and `DPCSSYS_CR3_LANEX_DIG_RX_DPLL_*`: CDR tuning/status and DPLL frequency/bounds fields.
- `DPCSSYS_CR3_LANEX_DIG_RX_ADPTCTL_*`: RX adaptation configuration, reset, ATT/VGA/CTLE/DFE tap status, slicer controls, DFE data/error offsets, error slicer level, DAC control selectors, and CR bank address/data.
- `DPCSSYS_CR3_LANEX_DIG_RX_STAT_*`: programmable RX status/match/statistics controls, data masks, load values, sample count, multiple statistic counters, comparator clock control, and stop control.
- `DPCSSYS_CR3_LANEX_DIG_MPHY_*`: MPHY RX PWM, low-speed termination, and analog PWM clock-stable count fields.
- `DPCSSYS_CR3_LANEX_DIG_ANA_*`: digital override and readback-facing analog fields for TX/RX power/control, term code, TX equalization, RX VCO, calibration, DAC, AFE ATT/VGA/CTLE, RX scope, slicer, IQ phase/sense, signal-change clocks, analog status, MPHY override, signal detect, and TX DCC DAC.
- `DPCSSYS_CR3_LANEX_ANA_TX_*` and `DPCSSYS_CR3_LANEX_ANA_RX_*`: direct analog TX/RX register field maps for power override, measurement/test buses, DCC DAC, termination code, override clocks, TX misc/reserved fields, RX clocks, CDR/deserializer, slicer, power, squelch, calibration, analog test buses, and reserved RX fields.
- `DPCSSYS_CR3_RAWMEM_*`: raw ROM/RAM common memory field placeholders.
- `DPCSSYS_CR3_RAWLANEX_DIG_PCS_XF_*`: raw PCS interface override/input/output fields for TX, RX, ATE, adaptation ack/FOM, equalization requests, lane number, termination control, and phase-2 calibration.
- `DPCSSYS_CR3_RAWLANEX_DIG_FSM_*`: raw finite-state-machine override/status, memory monitor, fast RX/TX calibration/adaptation step controls, flags, common calibration status, DCC status, OCLA, TX EQ update, RCAL status, and IQ phase offset fields.
- `DPCSSYS_CR3_RAWLANEX_DIG_IRQ_CTL_*`: raw lane IRQ status, clear, reset-return request, IRQ masks, and second TX IRQ mask register for RX/TX reset/request/rate/pstate/adaptation, lane mode, phase-2 calibration, loopback, and DCC on-demand events.
- `DPCSSYS_CR3_RAWLANEX_DIG_PMA_XF_*`: raw PMA interface override and PMA input fields for lane MPLL A/B enables, supervisor MPLL state, and the beginning of TX override output values/enables.

## Register Areas Covered

The `LANEX_DIG_TX_PWRCTL` region describes lane-X TX sequencing rather than a single immediate register write. Timing fields cover refgen enable, TX clock enable, VCM hold, VBOOST disable, RX detect, reset, serial enable, fast RX detect, and skip bits. DCC bank/DAC fields indicate indexed access and handshake around TX DCC calibration or compensation.

The `LANEX_DIG_RX_PWRCTL`, `RX_VCOCAL`, `RX_CDR`, `RX_DPLL`, and `RX_ADPTCTL` regions define the core RX bring-up and training controls. The power-state tables identify which analog/digital subblocks are enabled for each state. VCO calibration and CDR/DPLL fields expose lock/tracking configuration and readback. Adaptation fields carry the programmable knobs and observed results for ATT, VGA, CTLE, DFE taps, slicers, DAC selectors, and reset behavior.

The `RX_STAT` region is a diagnostic counter/match engine. It can load compare values, mask received data, select match/stat modes, count samples, expose several counter registers, gate comparator clocks, and stop statistic collection. This makes it a validation/debug surface rather than normal display-mode state alone.

The digital analog and direct analog regions bridge software-visible DPCS logic to analog PHY behavior. They include override enables and values for TX/RX resets, clocks, term codes, equalization, VCO/CDR signals, calibration DACs, signal detect, MPHY, and test-bus measurement fields. The paired status fields are readback surfaces for analog state and calibration observations.

The raw PCS/FSM/IRQ/PMA regions expose lower-level hardware interfaces beneath the higher-level lane-X register map. They are useful for debug, manufacturing validation, OCLA observation, fast calibration sequencing, interrupt handling, and PMA boundary override/readback. The range ends before the masks for `DPCSSYS_CR3_RAWLANEX_DIG_PMA_XF_TX_OVRD_OUT`, so the next chunk owns the remainder of that register.

## Control Flow

This header has no local control flow. Runtime control flow is implied by how AMDGPU display code uses generated offset and shift/mask headers:

1. Select DCN 3.1 resource code, which includes `dpcs_4_2_0_offset.h` and `dpcs_4_2_0_sh_mask.h`.
2. Pair `ixDPCSSYS_CR3_*` offsets from the offset header with these `DPCSSYS_CR3_*__SHIFT` and `_MASK` constants.
3. Use register helper macros and DC link/PHY code to compose read-modify-write values, program power-state/timing/adaptation tables, read live status, poll calibration/ack bits, or clear/mask IRQs.
4. Let hardware execute the real TX/RX power, reset, calibration, adaptation, FSM, and interrupt behavior.

The header does not encode ordering. Callers must follow the hardware sequencing rules for reset, clock enable, pstate changes, CDR/VCO calibration, DCC DAC handshakes, adaptation reset, statistics clear/stop, IRQ clear, and PMA/PCS overrides.

## State And Persistence Behavior

No software state is stored here. The macros describe fields whose values live in hardware registers.

- Power-state and timing fields persist programmed TX/RX lane behavior until later writes, reset, or power-domain loss.
- Override fields can force analog, PCS, FSM, PMA, TX, RX, loopback, term-code, data-enable, reset, request, calibration, and signal-detect behavior while their corresponding override-enable bits remain set.
- Status, IRQ, counter, ACK, FOM, VCO, CDR, DPLL, adaptation, analog, and FSM fields expose live or latched hardware state.
- Clear, stop, update-clock, request, and handshake fields may have side effects or self-clearing semantics defined by the hardware specification, not by this generated header.
- Reserved fields are part of the register layout but should be preserved and not used as software-owned storage.

The file does not define reset values, retention across suspend/resume, or which fields are read-only/write-only. Those properties must come from the ASIC register database and consumer code.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h`, which defines matching `ixDPCSSYS_CR3_*` register offsets. For this slice, the offset range runs from the CR3 lane-X TX power-control registers around `0x9024` through raw lane PMA/PCS/FSM/IRQ/PMA registers around `0xe000+`.

The observed in-tree include point is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`, which includes both `dpcs_4_2_0_offset.h` and `dpcs_4_2_0_sh_mask.h`. That resource file uses AMD DC register helper conventions that token-paste register and field names into offset, shift, and mask constants.

Likely consumers are AMDGPU DC link encoder, PHY, link-training, display power, diagnostics, and interrupt paths for DCN 3.1 ASICs using DPCS 4.2.0. The same generated naming scheme appears in sibling DPCS/DCN ASIC headers, so the exact ASIC generation matters even when names look structurally similar.

## Risks And Edge Cases

- Generated-header drift is high impact: an incorrect mask or shift can compile successfully while writing the wrong silicon bit.
- This chunk begins and ends mid-register. The previous chunk owns most of `DPCSSYS_CR3_LANEX_DIG_TX_PWRCTL_TX_PSTATE_P2`; the next chunk owns the rest of `DPCSSYS_CR3_RAWLANEX_DIG_PMA_XF_TX_OVRD_OUT`.
- The register surface mixes writable configuration, read-only status, latched IRQ status, write-to-clear bits, stop/update controls, counters, override enables, and reserved fields. Treating all fields as ordinary writable configuration can clear status, leave forced overrides active, or corrupt reserved bits.
- TX/RX power, reset, clock, VCO, CDR, DPLL, DCC, adaptation, and PMA/PCS override fields are sequencing-sensitive. Writes at the wrong link-training or display-active phase can cause link loss, failed training, flicker, or hardware hangs.
- CR bank address/data fields imply indexed internal state. Callers need strict address/data ordering and should avoid concurrent or interleaved bank access without the relevant hardware locking/serialization.
- The raw lane/FSM/IRQ/PMA regions expose low-level debug and validation controls. They are powerful enough to bypass normal hardware ownership and should be restored to non-override operation after use.
- Reserved masks are present for completeness but do not make reserved bits safe to write. Consumers should preserve existing reserved values unless the hardware spec explicitly says otherwise.

## Test Signals

Useful validation signals for this chunk are build-time, generated-header, and hardware-integration oriented:

- Compile/preprocess DCN 3.1 AMDGPU display code that includes `dpcs_4_2_0_sh_mask.h`; missing or renamed fields should fail in register helper users.
- Mechanical checks that all complete register groups have paired `__SHIFT` and `_MASK` definitions. For this exact slice, expect 2,118 defines, 1,064 shifts, and 1,054 masks because of the partial start/end registers.
- Diff this header against the authoritative AMD DPCS 4.2.0 register database and the matching `dpcs_4_2_0_offset.h`.
- Cross-check sibling DPCS 4.2.x/DCN headers only where the IP block is expected to be compatible; similar names do not prove identical bit layout.
- Runtime validation on DPCS 4.2.0/DCN 3.1 hardware: DP/HDMI link training, link-rate and lane-count changes, hotplug, suspend/resume, GPU reset recovery, low-power transitions, and DP Alt Mode attach/detach where applicable.
- Register readback during link bring-up should show expected movement through TX/RX request/ack, reset, pstate, power-up timing, VCO calibration, CDR/DPLL tuning, DCC calibration, RX adaptation, and FSM fast-path status.
- IRQ tests should exercise RX/TX reset/request/rate/pstate/adaptation, lane mode, phase-2 calibration, loopback, and DCC on-demand status/mask/clear behavior.
- Diagnostic tests should cover LBERT, OCLA, RX statistic counters, analog test bus, MPHY controls, signal detect overrides, PMA/PCS overrides, and cleanup that returns override-enable bits to hardware ownership.

## Chunk Notes For Merge

This document intentionally covers only lines 81060-83443 of `dpcs_4_2_0_sh_mask.h`. The final per-file report should merge it with adjacent chunks for the full generated DPCS 4.2.0 field map. Reconciliation should note that this chunk begins with the last mask of `DPCSSYS_CR3_LANEX_DIG_TX_PWRCTL_TX_PSTATE_P2` and ends after `DPCSSYS_CR3_RAWLANEX_DIG_PMA_XF_TX_OVRD_OUT__TX_DWORD_CLK_SYNC_OVRD_VAL__SHIFT`, before the remaining shifts and masks for that PMA TX override register.
