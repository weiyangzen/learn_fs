# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 77828-80268

## Purpose

This chunk is a generated AMD DPCS 4.2.3 shift/mask header slice for DCN316-era display PHY and DPCS register fields. It contains no executable C logic; its interface is preprocessor metadata that gives bit positions and masks for 16-bit DPCS CR registers. Runtime AMDGPU display code pairs these macros with `dpcs_4_2_3_offset.h` register offsets and register helper/table macros to program or decode link, receiver, analog, PCS, PMA, FSM, interrupt, and PLL state.

The range starts mid-register with the final masks for `DPCSSYS_CR3_LANEX_DIG_RX_ADPTCTL_ADPT_CFG_6`, then covers the end of the CR3 lane-X indexed register block. It crosses into `addressBlock: dpcssys_cr4_rdpcstxcrind` and begins the CR4 supervisor/common-digital block. It ends at the `DPCSSYS_CR4_SUP_DIG_MPLLB_ASIC_IN_0` register marker, before that register's fields appear in the next chunk.

Within this slice there are 2,151 `#define` lines and 287 register comment markers. The macros are mostly the generated pair convention:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit offset of a field.
- `<REGISTER>__<FIELD>_MASK`: the field mask used for packing, extracting, and read-modify-write operations.

Although the file is under this repository's mirrored `ceph-client` source tree, it is AMDGPU display hardware metadata and has no Ceph or distributed-filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, callbacks, locks, allocation paths, or includes in this chunk. The exported surface is the generated macro namespace.

Major field families in this range are:

- CR3 receiver adaptation control: `DPCSSYS_CR3_LANEX_DIG_RX_ADPTCTL_*` covers VGA/DFE adaptation configuration, adaptation resets, ATT/VGA/CTLE/DFE tap status, data/error VDAC offsets, slicer controls, error slicer levels, DAC-control selection, and CR bank address/data fields.
- CR3 RX statistics and pattern matching: `DPCSSYS_CR3_LANEX_DIG_RX_STAT_*` defines load values, data masks, match controls, stat controls, sample counts, multi-word statistic counters, calibration comparison clock control, and stop controls.
- CR3 MPHY and digital analog override/readback: `DPCSSYS_CR3_LANEX_DIG_MPHY_*`, `DPCSSYS_CR3_LANEX_DIG_ANA_TX_*`, `DPCSSYS_CR3_LANEX_DIG_ANA_RX_*`, `DPCSSYS_CR3_LANEX_DIG_ANA_STATUS_*`, signal-detect, and DCC DAC fields expose low-speed PWM/termination, TX/RX override outputs, EQ/DAC/VCO/slicer/phase/calibration controls, status, and analog signal-change controls.
- CR3 analog TX/RX controls: `DPCSSYS_CR3_LANEX_ANA_TX_*` and `DPCSSYS_CR3_LANEX_ANA_RX_*` define analog power, alternate bus, ATB measurement, DCC DAC, termination, clock, misc, CDR, slicer, squelch, calibration, and reserved/test fields.
- CR3 raw-lane PCS/PMA handoff: `DPCSSYS_CR3_RAWLANEX_DIG_PCS_XF_*` and `DPCSSYS_CR3_RAWLANEX_DIG_PMA_XF_*` describe override and hardware handoff fields for TX/RX reset, request, data enable, clocking, pstate, rates, lane number, adaptation figure of merit, directed TX-pre/main/post requests, ATE overrides, RX EQ overrides, phase-2 calibration, lane/supervisor PMA state, RTUNE, MPHY, and RX adaptation outputs.
- CR3 raw-lane FSM and IRQ control: `DPCSSYS_CR3_RAWLANEX_DIG_FSM_*` exposes FSM override, command/status monitoring, fast-mode calibration/adaptation flags, common calibration status, OCLA, DCC status, EQ update, and IQ phase offset fields. `DPCSSYS_CR3_RAWLANEX_DIG_IRQ_CTL_*` names status and clear bits for RX/TX reset/request/rate/pstate/adaptation, lane transceiver mode, phase-2 calibration, loopback, DCC on-demand, and interrupt masks.
- CR3 TX/RX control monitors: `DPCSSYS_CR3_RAWLANEX_DIG_TX_CTL_*`, `DPCSSYS_CR3_RAWLANEX_DIG_RX_CTL_*`, and ATE/master-MPLL override fields describe FSM clock/reset control, continuous DCC/off-cancel/adaptation status, OCLA, LOS mask, data-enable override, and auxiliary ATE override paths.
- CR4 supervisor digital common block: `DPCSSYS_CR4_SUP_DIG_*` begins with ID code low/high fields, reference-clock overrides, MPLLA/MPLLB divided and HDMI clock overrides, MPLLA/MPLLB override inputs, SSC peak/stepsize split fields, fractional-N quotient/remainder/denominator, charge-pump overrides, supervisor/prescaler/level overrides, supervisor output state overrides, debug selection, and MPLLA ASIC input fields.

Several complete registers include fields named `RESERVED_*` or full-width reserved/debug/test fields. These are still part of the generated hardware contract: consumers should preserve reserved bits according to hardware access rules rather than treating the names as permission for arbitrary writes.

## Control Flow

This header has no runtime control flow. Its effective flow is compile-time token expansion followed by hardware register access elsewhere:

1. DCN316 resource code includes `dpcs/dpcs_4_2_3_offset.h` and `dpcs/dpcs_4_2_3_sh_mask.h`.
2. Link-encoder/resource macros such as `DPCS_DCN31_REG_LIST(id)` and `DPCS_DCN31_MASK_SH_LIST(...)` concatenate register and field names into offset, shift, and mask tables.
3. Runtime display code uses AMD register helpers against those tables to read, update, poll, or clear DPCS fields during link bring-up, link training, modeset, diagnostics, suspend/resume, and hardware validation.
4. Hardware state machines perform the actual sequencing for receiver adaptation, calibration, PLL programming, lane request/ack transitions, PCS/PMA ownership, IRQ latching, and supervisor/common PLL state.

The macros only describe bit layout. They do not encode read/write access type, reset value, write-one-to-clear behavior, stickiness, polling order, or required delays.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It names hardware-visible state that can persist in powered DPCS/PHY domains until a later register write, power-gating transition, firmware intervention, hotplug/link reset, or GPU reset changes it.

State described by this chunk includes:

- Receiver equalization/adaptation state: ATT/VGA/CTLE/DFE settings, adaptation reset bits, adaptation done/status bits, VDAC offsets, slicer controls, error levels, and RX EQ override values.
- Measurement and diagnostic state: RX statistic counters, pattern masks, sample counts, OCLA/debug selectors, ATB measurement fields, analog status fields, FSM state/command monitors, DCC status, IQ phase offsets, and figure-of-merit values.
- Lane and PHY handoff state: PCS/PMA override enables/values, TX/RX reset/request/data-enable/clock state, lane number, loopback, pstate/rate/width, adaptation requests, phase-2 calibration, termination control, and ATE/manufacturing overrides.
- Interrupt state: raw-lane IRQ status, clear, and mask bits for RX/TX events, adaptation, pstate/rate changes, lane mode changes, phase-2 calibration, loopback, and DCC on-demand events.
- Common supervisor and PLL state: reference clock selection, MPLLA/MPLLB overrides, fractional-N and SSC parameters, charge-pump controls, prescaler/DCO settings, RTUNE handshake, PLL state overrides, bandgap state overrides, level/VBOOST/VREF overrides, and MPLLA ASIC inputs.

Because access semantics are not present in this generated header, consumers must rely on the matching hardware documentation and driver sequencing code to know which fields are read-only, sticky, clear-on-write, self-clearing, or unsafe to update while clocks or power domains are inactive.

## Dependencies And Integration Points

This chunk is tightly coupled to the generated DPCS 4.2.3 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h`, which provides the corresponding indexed register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which directly includes the DPCS 4.2.3 offset and shift/mask headers and builds DCN316 link encoder register, shift, and mask tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h`, where `DPCS_DCN31_REG_LIST(id)` and `DPCS_DCN31_MASK_SH_LIST(mask_sh)` define the token-pasted register/table contract used by DCN31-family DPCS link encoders.

Most fields in this particular chunk are lower-level CR3 lane-X and CR4 supervisor metadata rather than the small public subset listed in `DPCS_DCN31_MASK_SH_LIST`. They still matter for bring-up, debug, firmware/hardware validation, and any code path that uses the generated DPCS namespace directly to access indexed CR registers.

Adjacent generated headers such as `dpcs_4_2_0_sh_mask.h` and `dpcs_4_2_2_sh_mask.h` have similar shapes, but they are not interchangeable. Field widths, masks, register coverage, and literal formatting can vary by ASIC/IP version.

## Risks And Edge Cases

- A wrong shift or mask compiles as an ordinary integer constant but can update the wrong hardware bit, causing failed link training, unstable RX adaptation, bad PLL programming, missed interrupts, bad analog tuning, stuck resets, or display bring-up failures.
- The chunk begins and ends on artificial boundaries. The `ADPT_CFG_6` shifts are in the previous chunk, while `DPCSSYS_CR4_SUP_DIG_MPLLB_ASIC_IN_0` fields are in the next chunk. Pair-completeness checks must allow those boundaries.
- Many CR3 analog, FSM, ATE, PCS, PMA, and reserved fields are hardware-sensitive. Manual writes outside known sequences can perturb calibration, production test state, or ownership handoff between hardware, firmware, and the driver.
- IRQ status, clear, and mask fields are adjacent and similarly named. Confusing them can either drop diagnostics or leave events latched.
- Supervisor PLL fields are split across multiple registers for fractional-N, SSC peak/stepsize, dividers, charge pump, and prescaler configuration. Partial or out-of-order programming can produce marginal clocks that fail only at specific link rates, lane counts, cables, or thermal conditions.
- Reserved masks are emitted explicitly. Driver code should preserve or update them only as documented; treating reserved fields as free scratch bits risks future ASIC incompatibility.
- Generated DPCS versions are repetitive. Copying CR3 lane-X or CR4 supervisor definitions from a sibling version without checking the companion offset file and hardware database can produce a table that builds but targets the wrong silicon contract.

## Test Signals

Useful validation for this chunk includes:

- Build or preprocess AMDGPU display support for the DCN316 path that includes `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`; missing or renamed macros should surface in resource and link-encoder table initialization.
- Static consistency checks that each consumed CR3/CR4 register name has both an offset macro in `dpcs_4_2_3_offset.h` and matching field macros in this shift/mask header, with chunk-boundary exceptions for `ADPT_CFG_6` and `MPLLB_ASIC_IN_0`.
- Generated-header diff checks against AMD's authoritative DPCS 4.2.3 register source and against neighboring DPCS 4.2.x headers where repeated CR3 lane-X and CR4 supervisor fields are expected to match.
- Hardware link tests on DCN316 systems across DP/HDMI link rates, lane counts, retraining, HPD IRQ, suspend/resume, and DP-alt/USB-C paths, watching for RX adaptation, PLL, pstate, and lane request/ack failures.
- Diagnostics that read RX statistic counters, FSM status, OCLA/debug fields, analog status, DCC status, IQ phase offset, and IRQ status/clear paths after controlled link-training or calibration events.
- Stress tests around MPLLA/MPLLB fractional, SSC, prescaler, RTUNE, and level/VBOOST/VREF override programming, especially under power gating and clock changes.

## Cross-Chunk Notes

This is chunk 33 of `dpcs_4_2_3_sh_mask.h`. The final per-file research should merge this with the previous chunk for the beginning of `DPCSSYS_CR3_LANEX_DIG_RX_ADPTCTL_ADPT_CFG_6` and with the next chunk for the rest of `DPCSSYS_CR4_SUP_DIG_MPLLB_ASIC_IN_0` and later CR4 fields. This document intentionally covers only lines 77828-80268 and does not replace the later per-file reconciliation report.
