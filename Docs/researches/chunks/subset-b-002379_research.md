# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 100132-102491

## Work Item

- Chunk id: `subset-b-002379`
- Source path: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h`
- Line range: 100132-102491
- Scope note: this is a chunk of a very large generated AMD DPCS ASIC register mask header. The chunk begins in the tail of `DPCSSYS_CR4_SUPX_DIG_RTUNE_CONFIG` mask definitions, starts its first complete register block at `DPCSSYS_CR4_SUPX_DIG_RTUNE_STAT`, and ends at the first `__SHIFT` field for `DPCSSYS_CR4_LANEX_ANA_RX_ATB_MEAS3`.

## Purpose

This chunk defines C preprocessor constants for DPCS 4.2.2 CR4 supervisor and per-lane register bitfields. The constants provide the bit shift and mask values used by AMDGPU display/link code to read, write, compose, and decode packed hardware register fields without embedding literal bit positions throughout driver code.

The visible register families cover:

- Supervisor digital RTUNE controls and status, including RX/TX termination calibration status and set values.
- Supervisor digital-to-analog overrides for MPLLA/MPLLB, analog RTUNE, bandgap/reference controls, and PMIX controls.
- Lane digital ASIC override and ASIC input/output observation blocks for TX, RX, EQ, CDR/VCO, lane state, and OCLA.
- Lane TX power control, DCC DAC programming, clock alignment, and LBERT controls.
- Lane RX power control, VCO calibration, CDR/DPLL controls, adaptation control/status, match/stat counters, and LBERT controls.
- Lane digital analog-bridge override/status blocks that drive TX/RX analog controls from the digital register interface.
- Lane analog TX and RX control blocks for measurement, ATB routing, DCC, termination, clocks, CDR/deserializer, slicer, power, squelch, calibration, and register-reference controls.

## Important APIs, Types, and Functions

There are no functions, structs, enums, or runtime APIs in this range. The exported surface is a set of `#define` macros whose names follow the generated AMD register field convention:

- `DPCSSYS_CR4_<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit index.
- `DPCSSYS_CR4_<REGISTER>__<FIELD>_MASK` gives the field mask already shifted into register position.
- Register block comments of the form `//DPCSSYS_CR4_<REGISTER>` group the related field macros.

The chunk contains 2,139 `#define` lines, split almost exactly into 1,069 `__SHIFT` definitions and 1,070 `_MASK` definitions. The one-count imbalance is caused by the line-range boundary ending after `DPCSSYS_CR4_LANEX_ANA_RX_ATB_MEAS3__meas_atb_cdr_vco_gd__SHIFT` before the corresponding mask definitions in the following chunk.

Key complete or nearly complete groups in this range include:

- `DPCSSYS_CR4_SUPX_DIG_RTUNE_*`: termination tuning status and RX/TX set/stat values, timing counters, and TX calibration code.
- `DPCSSYS_CR4_SUPX_DIG_ANA_MPLLA_*` and `DPCSSYS_CR4_SUPX_DIG_ANA_MPLLB_*`: override outputs for MPLL clock enables, output enables, analog enable, reset, calibration, dividers, feedback clock, gearshift, standby, integer and charge-pump fields.
- `DPCSSYS_CR4_LANEX_DIG_ASIC_*`: digital override input registers and ASIC-observed input/output registers for lane, TX, RX, RX EQ, and RX CDR/VCO paths.
- `DPCSSYS_CR4_LANEX_DIG_TX_PWRCTL_*`: TX P-state fields, reset/enable delay counters, DCC DAC bank address/data/control/range/select/ack/address fields.
- `DPCSSYS_CR4_LANEX_DIG_RX_PWRCTL_*`: RX P-state fields and RX power-up timing.
- `DPCSSYS_CR4_LANEX_DIG_RX_VCOCAL_*`: VCO calibration mode, configuration, timing, and status fields.
- `DPCSSYS_CR4_LANEX_DIG_RX_CDR_*` and `DPCSSYS_CR4_LANEX_DIG_RX_DPLL_*`: CDR control/status and DPLL frequency/bounds fields.
- `DPCSSYS_CR4_LANEX_DIG_RX_ADPTCTL_*`: adaptation configuration fields, reset fields, and status readback for ATT, VGA, CTLE, DFE taps, slicer offsets, DAC control selection, and CR bank addressing.
- `DPCSSYS_CR4_LANEX_DIG_RX_STAT_*`: programmable match/stat collection fields, counters, sample count, stop, and calibration compare clock control.
- `DPCSSYS_CR4_LANEX_DIG_ANA_*`: digital-side override outputs toward analog TX/RX/MPHY/sigdet/DCC/term-code controls plus analog status readback.
- `DPCSSYS_CR4_LANEX_ANA_TX_*`: analog-side TX measurement, power override, alternate bus, ATB routing, DCC DAC/control, termination code/control, clock override, and miscellaneous/reserved fields.
- `DPCSSYS_CR4_LANEX_ANA_RX_*`: analog-side RX clock, CDR/deserializer, slicer, power, squelch, calibration, ATB/register-reference, and measurement fields.

## Control Flow

This header has no executable control flow. Runtime control flow appears in consumers that include this header and combine masks/shifts with register access helpers. A typical consumer pattern is:

1. Read a hardware register through the AMDGPU display register access layer.
2. Extract a field with `value & FIELD_MASK`, then shift by `FIELD__SHIFT`.
3. Compose an updated field by shifting a value by `FIELD__SHIFT`, masking it with `FIELD_MASK`, and OR-ing it into a register update.
4. Write the updated register back through the MMIO/register abstraction.

The control semantics represented by the field names are hardware state-machine controls rather than C branches. Examples include P-state selection, RX/TX power-up timers, VCO calibration start/done/status fields, adaptation enables and windows, override-enable bits, reset bits, and LBERT enable/error fields.

## State and Persistence Behavior

The macros are compile-time constants and do not store software state. They map to persistent hardware register state in the DPCS block while the GPU/display hardware is powered. The most important state categories visible in this chunk are:

- Calibration and tuning state: RTUNE set/stat values, TX calibration code, RX VCO calibration controls/status, and DCC DAC controls.
- Power/link state: TX/RX P-state fields, lane power-up timing fields, MPHY RX controls, and analog enable/override fields.
- Clocking and CDR state: MPLLA/MPLLB enables, RX CDR controls, DPLL frequency/bounds, VCO override fields, and IQ phase adjustment fields.
- Adaptation state: ATT/VGA/CTLE/DFE adaptation configuration and status fields, slicer offsets, and error slicer level.
- Diagnostic and measurement state: LBERT controls/errors, OCLA fields, stat match/counter registers, ATB measurement selection, and analog status readbacks.

Because this is hardware state, persistence depends on GPU reset, display engine reset, power-gating, link training, and firmware or driver reprogramming sequences. The header itself does not document reset values or access permissions, so consumers must rely on register offset headers, hardware programming guides, and driver sequencing.

## Dependencies and Integration Points

This chunk depends only on the C preprocessor and the broader generated AMD ASIC register-header ecosystem. It is expected to be included alongside companion DPCS headers that define register offsets, base indices, and possibly default values.

Integration points include:

- AMDGPU display core and DCN link training code that configures DisplayPort/PHY/DPCS lanes.
- Register accessor macros/helpers that use `_MASK` and `__SHIFT` names to set or read fields.
- Diagnostic paths that expose or inspect LBERT, OCLA, stat counters, CDR/VCO status, adaptation status, or ATB measurement selection.
- Generated ASIC-specific include selection for DPCS 4.2.2, where matching the correct generation-specific mask header to the correct register-offset header is required.

The field naming suggests integration with serializer/deserializer, PLL, CDR, DFE/adaptation, MPHY, and analog measurement logic in the display PHY. No Linux kernel APIs are directly invoked in this chunk.

## Risks and Edge Cases

- Boundary risk: this chunk is partial at both ends. The preceding chunk owns the earlier `DPCSSYS_CR4_SUPX_DIG_RTUNE_CONFIG` shift lines, while the following chunk owns most of `DPCSSYS_CR4_LANEX_ANA_RX_ATB_MEAS3`. Merge logic must not treat this chunk alone as a complete register map.
- Generated-header drift: a wrong mask or shift silently corrupts hardware programming. Errors can cause failed link training, unstable displays, bad calibration, or hangs in low-level display initialization.
- Reserved and `NC` fields are numerous. Consumers should preserve reserved bits on read-modify-write unless hardware documentation explicitly permits writing them.
- Override fields are high risk because they bypass automatic hardware/firmware control. Incorrect `*_OVRD_EN`, reset, clock enable, or power bits can leave the lane analog path disabled, stuck in reset, or driven with invalid calibration values.
- Many fields are narrow packed values, often 1 to 10 bits inside 16-bit masks. Consumer code must validate value widths before shifting to avoid truncation or reserved-bit writes.
- Read-only status fields and writeable control fields are mixed in the same header naming style. The masks do not encode access direction, volatility, reset value, or side effects.
- Field spelling reflects generated hardware names, including lower-case field fragments and names such as `tresh`. Renaming for style would break consumers and generated consistency.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware-integration oriented:

- The kernel tree should compile with this header included by AMDGPU display code; duplicate or malformed macro names would normally surface as preprocessor/build failures.
- Static checks can verify each complete register block has paired `__SHIFT` and `_MASK` macros for each field. The expected exception in this chunk is the partial `DPCSSYS_CR4_LANEX_ANA_RX_ATB_MEAS3` block at the end.
- Mask/shift consistency can be checked mechanically by confirming each mask's least-significant set bit matches its corresponding shift and that masks do not overlap unexpectedly within a register unless the hardware definition intentionally aliases fields.
- Runtime display validation should cover DP/USB-C link bring-up, link training across rates/lanes, hotplug, suspend/resume, GPU reset, and displays requiring RX/TX calibration or CDR adaptation paths.
- Diagnostic validation should include LBERT/OCLA/stat-counter paths and analog measurement/ATB paths if the platform exposes them.

## Open Questions for Later Merge

- The complete per-file report should correlate these masks with the companion address header for DPCS 4.2.2 to identify the actual register offsets for each block.
- Access semantics, reset values, and sequencing constraints are not visible in this mask header and must be inferred from consumers or hardware documentation.
- The next chunk is needed to complete `DPCSSYS_CR4_LANEX_ANA_RX_ATB_MEAS3` and continue into raw memory/raw lane definitions that begin immediately after this range.
