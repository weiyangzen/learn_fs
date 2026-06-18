# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 23896-26285

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice. It contains C preprocessor constants for DPCS register bitfields, not executable driver logic. The constants are consumed by AMDGPU display code so higher-level register helpers can set, clear, update, and decode fields without hard-coding bit positions.

The requested range contains 2,390 source lines with 1,065 `__SHIFT` macros, 1,077 `_MASK` macros, and 266 register/comment boundary lines. It starts inside `DPCSSYS_CR0_LANEX_ANA_RX_ATB_MEAS1`, covers CR0 lane-X analog RX measurement and raw lane PCS/FSM/IRQ/PMA/TX/RX/ATE control fields, then crosses into the `dpcssys_cr1_rdpcstxcrind` address block for CR1 support digital/analog, MPLLA/MPLLB, clock/reset, spread-spectrum, and rtune fields. The last line is the comment for `DPCSSYS_CR1_SUP_DIG_ANA_MPLLA_OVRD_OUT_2`; that register's field definitions continue in the next chunk.

Although the path is under a local `ceph-client` source mirror, this file belongs to AMDGPU display-controller hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, memory allocations, locks, or direct MMIO operations in this range. The public surface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit index of a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask of that field within the register value.

The main macro families in this chunk are:

- `DPCSSYS_CR0_LANEX_ANA_RX_ATB_*` and nearby analog RX definitions: analog test bus and RX measurement selection fields such as ATB master enable, voltage/regulator measurement selects, CDR VCO measurement, calibration VREF, ATB force values, and reserved/NC fields.
- `DPCSSYS_CR0_RAWMEM_DIG_ROM/RAM_*`: raw memory data windows for common ROM/RAM fields, represented as 16-bit `DATA` masks.
- `DPCSSYS_CR0_RAWLANEX_DIG_PCS_XF_*`: PCS transfer controls for TX and RX. These include TX/RX pstate, low-power detect, width, rate, MPLL selection/enables, master MPLL override, async enable/data overrides, reset/request/detect-RX handshakes, TX/RX data-enable overrides, loopback controls, RX equalization/CTLE/DFE-related overrides, PH2 calibration, lane number, and ATE/test override forms of many of the same controls.
- `DPCSSYS_CR0_RAWLANEX_DIG_FSM_*`: micro-FSM override, monitor, status, fast-path calibration/adaptation flags, common calibration status, DCC flags/status, OCLA enable, TX EQ update flags, register/memory lock bits, and RX IQ phase offset fields.
- `DPCSSYS_CR0_RAWLANEX_DIG_IRQ_CTL_*`: RX/TX reset/request/rate/pstate/adaptation/PH2/loopback/DCC interrupt status, clear, and mask fields.
- `DPCSSYS_CR0_RAWLANEX_DIG_PMA_XF_*`: PMA transfer override and readback fields for lane/supply/TX/RX, including TX/RX request/ack, reset/data enable, PMA ack, retune request/ack, async/PWM controls, RX termination, and MPHY override controls.
- `DPCSSYS_CR0_RAWLANEX_DIG_TX_CTL_*` and `DPCSSYS_CR0_RAWLANEX_DIG_RX_CTL_*`: TX/RX lane control fields for FSM behavior, TX clock selection and DCC status, RX LOS masking, data-enable override counters, continuous off-cancel/adaptation status, and UPCS/OCLA observation gates.
- `DPCSSYS_CR1_SUP_DIG_*`: support-digital CR1 controls for IDCODE low/high data, reference clock overrides, MPLLA/MPLLB divider and HDMI clock overrides, PLL override controls, SSC peak/stepsize/fract-N values, charge pump controls, supply/prescaler/lane-level overrides, ASIC input mirrors, and debug fields.
- `DPCSSYS_CR1_SUP_ANA_*`: support-analog CR1 fields for prescaler, rtune, bandgap, analog switch/power measurement, MPLLA/MPLLB miscellaneous controls, analog PLL override bits, ATB measurement, PLL control registers, reserved analog controls, and duplicated A/B PLL control banks.
- `DPCSSYS_CR1_SUP_DIG_MPLLA_MPLL_PWR_CTL_*` and `DPCSSYS_CR1_SUP_DIG_MPLLB_MPLL_PWR_CTL_*`: MPLL power-control override/status/timing/calibration/DAC fields for both MPLL instances.
- `DPCSSYS_CR1_SUP_DIG_CLK_RST_*` and `DPCSSYS_CR1_SUP_DIG_RTUNE_*`: bandgap/reference clock startup timing, VPHUD reference enable/select, rtune manual/debug/config/status/set/stat fields, and rtune timing counters.
- `DPCSSYS_CR1_SUP_DIG_ANA_MPLLA_OVRD_OUT_*`: readback/output fields for MPLLA word/HDMI/div/output clocks, analog enable/reset/calibration, gearshift, standby, and analog integer output. The range ends just as `OVRD_OUT_2` begins.

Several field names carry hardware sequencing semantics even though this header only records bit layout: `*_OVRD_EN`, `*_OVRD_VAL`, `*_REQ`, `*_ACK`, `*_DONE`, `*_IRQ`, `*_IRQ_CLR`, `*_MSK`, `*_FAST_*`, `*_CAL`, `*_STAT`, and `*_LOCK`.

## Control Flow

This header has no runtime control flow. It participates in AMDGPU display code through compile-time table construction:

1. The matching DPCS 4.2.2 offset header supplies register addresses or indirect register indexes.
2. This shift/mask header supplies field positions for those registers.
3. AMDGPU display resource, link-encoder, PHY, and register helper code combines offsets with shift/mask macros through generated field-list macros and token-pasting helpers.
4. Runtime helpers such as register read/modify/write paths use the resulting tables to program or inspect DPCS hardware.

Any real sequencing, such as asserting resets, waiting for request/ack transitions, masking or clearing interrupts, forcing ATE overrides, changing PLL/divider settings, triggering calibration, or polling rtune/MPLL status, lives in display driver code, firmware, and hardware state machines outside this generated header.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It identifies hardware-visible state and control fields:

- CR0 lane-X analog and raw lane state: RX ATB/measurement controls, TX/RX PCS override inputs and outputs, RX equalization and phase calibration values, PH2 calibration request/ack bits, FSM status/monitor/debug flags, interrupt state/clear/mask bits, PMA transfer handshakes, TX/RX lane controls, and ATE override fields.
- CR1 support-digital and support-analog state: reference clock and bandgap controls, MPLLA/MPLLB enable/divider/HDMI/SSC/fract-N/charge-pump controls, ASIC input mirrors, analog ATB and PLL control registers, MPLL power-control override/status/timers/calibration/DAC fields, clock/reset startup timers, and rtune controls/status.

Persistence is hardware-defined. Control fields may remain programmed until a modeset path, link reconfiguration, suspend/resume, GPU reset, ASIC reset, or power-gating transition rewrites them. Status, ack, calibration, IRQ, and readback fields may be read-only, latched, write-one-to-clear, self-clearing, or valid only while the relevant DPCS block is powered and clocked. This file does not encode access direction, reset values, volatility, or legal programming sequences.

## Dependencies And Integration Points

This generated header must stay synchronized with its ASIC register database and with the matching DPCS 4.2.2 offset definitions. Shift/mask consumers generally assume that every register field in the shift/mask header has a compatible register offset in the companion offset header and that field names match the token-pasted names used by AMD display register lists.

Integration points include:

- Companion AMD DPCS 4.2.2 generated headers under `drivers/gpu/drm/amd/include/asic_reg/dpcs/`, especially the matching offset header and adjacent chunks of this `dpcs_4_2_2_sh_mask.h` file.
- AMDGPU Display Core resource and link-encoder code that builds register access tables from ASIC-specific offset and mask/shift headers.
- DPCS/RDPCS register access helpers that use these constants for PHY/link bring-up, DisplayPort/HDMI lane control, link training, clock/PLL programming, signal detect, calibration, interrupt handling, and debug/test override flows.
- Firmware or hardware microcontroller interfaces that rely on matching interpretations of MPLL, rtune, FSM, calibration, and ATE fields.

The chunk crosses from the CR0 raw lane-X block to the CR1 support block at line 25043. That boundary matters for the merge lane: CR0 lane-X fields describe one lane/control context, while CR1 support fields describe another DPCS instance/address block with its own reference clock, MPLL, analog, and rtune controls.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly and only fail as a hardware programming bug.
- The file is generated. Manual edits risk divergence from AMD's register source, companion offset headers, firmware expectations, and silicon documentation.
- Chunk boundaries are not semantic. The first lines continue `DPCSSYS_CR0_LANEX_ANA_RX_ATB_MEAS1` from the previous chunk, and the final line only introduces `DPCSSYS_CR1_SUP_DIG_ANA_MPLLA_OVRD_OUT_2`.
- Many fields are paired `*_OVRD_VAL` and `*_OVRD_EN` controls. Mixing the value and enable masks can force clocks, resets, data enables, PLL selection, loopback, RX termination, or analog controls away from hardware/firmware ownership.
- Request/ack, done, IRQ, clear, and status fields are sequencing-sensitive. Incorrect definitions can cause false readiness, missed interrupts, uncleared latched events, link training timeouts, or hangs in PHY bring-up/teardown.
- Analog and clocking fields such as MPLLA/MPLLB dividers, SSC peak/stepsize, fract-N quotient/remainder/denominator, charge pump values, bandgap startup timers, VPHUD, rtune, CTLE/DFE/VGA/ATT/phase, and DCC values may only fail at specific link rates, board designs, cable/sink combinations, or voltage/temperature corners.
- Reserved and `NC` masks appear throughout the chunk. Driver code should not repurpose them unless the authoritative programming guide explicitly says so.
- Similar MPLLA/MPLLB and CR0/CR1 field names are easy to confuse. Token-pasted users must include the ASIC-specific header and register-list variant that matches the hardware generation.
- Some field names use `DATA` while others use `data`, and generated spelling/case is part of the API. Renaming for style would break consumers.

## Test Signals

Useful validation should combine generated-header consistency checks with hardware-oriented display testing:

- Build AMDGPU display configurations that include DPCS 4.2.2 support. Missing, renamed, or misspelled macros should surface in resource/link-encoder register table compilation.
- Mechanically compare this range against the authoritative DPCS 4.2.2 register database and ensure each complete field has a consistent `__SHIFT`/`_MASK` pair; account for the split first and last registers.
- Cross-check every complete register group in this chunk against the matching DPCS 4.2.2 offset header so register names in shift/mask macros have corresponding offsets.
- Run structural diff checks across repeated MPLLA/MPLLB groups and repeated override/status families to catch accidental generator drift while allowing intentional A/B PLL differences.
- Exercise DisplayPort/HDMI link bring-up, link-rate changes, hotplug, modeset, blank/unblank, suspend/resume, and GPU reset on hardware using this DPCS generation.
- Watch runtime logs and register dumps for request/ack timeouts, stuck reset/data-enable overrides, IRQs that fail to clear, missed RX/TX request events, RX adaptation failures, signal-detect instability, rtune failures, and MPLL lock/power-control anomalies.
- Validate ATE/test/debug override paths only in controlled diagnostics, since forcing override bits can bypass normal PHY control.
- Compare dumps decoded with these masks against hardware documentation or known-good tools for PLL dividers, SSC/fract-N values, rtune status, bandgap/reference startup timing, TX/RX lane controls, PH2 calibration, DCC calibration, and analog ATB/measurement fields.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DPCSSYS_CR0_LANEX_ANA_RX_ATB_MEAS1`, including at least the register comment and first field(s) before line 23896. This chunk then covers CR0 lane-X analog/RX, raw memory, PCS transfer, FSM, IRQ, PMA, TX/RX control, and ATE definitions through `DPCSSYS_CR0_RAWLANEX_DIG_PCS_XF_TX_OVRD_IN_2`, followed by the start of the CR1 support block. The next chunk should complete `DPCSSYS_CR1_SUP_DIG_ANA_MPLLA_OVRD_OUT_2` and continue the remaining CR1 support output/readback definitions. The final merged per-file report should reconcile these split register groups before making whole-file coverage claims.
