# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 64389-66756

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask register-field slice. It contains no executable C logic; it publishes preprocessor constants that describe bit offsets and bit masks for fields in the `DPCSSYS_CR3` display PHY/control-register space. Driver code combines these constants with the matching `dpcs_4_2_2_offset.h` offsets so AMDGPU display register helpers can pack, extract, and update individual MMIO or indexed DPCS fields.

The range covers 2,368 lines with 2,143 `#define` entries: 1,076 `__SHIFT` macros, 1,067 `_MASK` macros, and 225 register comment markers. It begins at the mask half of `DPCSSYS_CR3_SUP_DIG_MPLLB_HDMI_CLK_OVRD_IN`, so the matching shifts for that register are just before this chunk. It ends cleanly after `DPCSSYS_CR3_LANE1_DIG_ASIC_TX_OVRD_IN_4`, while the rest of lane 1 continues in following chunks. Although the repository path is under a `ceph-client` mirror, this file is AMDGPU display hardware metadata and does not implement distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, or allocation APIs in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset of a DPCS register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask used to isolate or preserve the field during read-modify-write operations.

The main register families in this range are:

- `DPCSSYS_CR3_SUP_DIG_MPLLA_*` and `DPCSSYS_CR3_SUP_DIG_MPLLB_*`: digital supervisor MPLL A/B override, status, ASIC input, spread-spectrum, fractional-N, charge-pump, clock-divider, HDMI clock, calibration, power-control timer, DAC range, lock, and PMIX fields. The A/B families are mostly mirrored and describe two PHY PLL paths.
- `DPCSSYS_CR3_SUP_DIG_SUP_*`, `PRESCALER_*`, `LVL_*`, `BANDGAP_*`, and `RTUNE_*`: supervisor control/status fields for prescaler override, RTUNE request/override/configuration/status, TX calibration codes, level controls, bandgap state, and analog override outputs.
- `DPCSSYS_CR3_SUP_ANA_*`: analog supervisor fields for prescaler, RTUNE, bandgap, MPLL miscellaneous controls, analog test bus controls, MPLL control registers, reserved analog fields, and power measurement.
- `DPCSSYS_CR3_LANE0_DIG_*`: lane 0 digital ASIC override/input/output fields for lane loopback, TX request and power-state controls, TX rate/width/data enable, PLL selection, cursor coefficients, HDMI mode, reset, RX status capture, DCC DAC control, TX clock alignment, LBERT, and status-match/count registers.
- `DPCSSYS_CR3_LANE0_ANA_*`: lane 0 analog TX override/status fields for power override, alternate bus, analog test bus, DCC DAC/control, termination code, EQ controls, clock override, vref, slew/peaking, regulator bypass, and reserved analog fields.
- `DPCSSYS_CR3_LANE1_DIG_ASIC_*`: the beginning of lane 1, covering lane-level loopback and TX overrides through reset. This mirrors the lane 0 digital ASIC TX override shape but is incomplete at the artificial chunk boundary.

Most field values are 16-bit-style masks such as `0x0000FFFFL`, though some counter, data, and status fields use 32-bit masks in other parts of the header. Many field names include explicit override-enable bits (`*_OVRD_EN`, `*_OVR_EN`) paired with the value they force, which is important for distinguishing normal hardware-driven state from software-forced PHY state.

## Control Flow

This header has no runtime control flow. The runtime path is supplied by AMDGPU display code:

1. DCN 3.1.5 resource code includes `dpcs_4_2_2_offset.h` and this shift/mask header.
2. Register-list macros such as `DPCS_DCN31_REG_LIST`, `DPCS_DCN31_MASK_SH_LIST`, and `DCN3_1_RDPCSTX_REG_LIST` token-paste register and field names into per-block register, shift, and mask tables.
3. Link encoder, DPCS/RDPCS TX, UNIPHY, and broader DC resource initialization stores those numeric constants in hardware object tables.
4. Runtime display paths call register helpers to program PHY PLLs, lane power states, link rates, training/equalization controls, HDMI/DP mode bits, status counters, and analog overrides.

The macros do not encode sequencing. Consumers must still order PLL enable/calibration, power-up timers, lane resets, rate/width transitions, EQ/cursor changes, HDMI mode changes, link training, and power-gating transitions according to the hardware specification.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes hardware state in the CR3 DPCS register block:

- MPLL A/B configuration and observed state, including enable, divider, fractional-N quotient/remainder/denominator, SSC peak/step size, charge pump, VCO/frequency selection, calibration, clock synchronization, lock timers, and analog DAC outputs.
- Supervisor and analog support state for prescaler, RTUNE, bandgap, level controls, calibration codes, power measurement, and analog override/status outputs.
- Lane 0 TX state for request, power state, rate, width, PLL selection, data enable, main/pre/post cursor coefficients, async driver enable, HDMI mode, clock ready, receiver detect, invert, low-power detect, DC coupling, FIFO extension, MPHY mode, and reset.
- Lane 0 and lane 1 loopback/test state, including TX-to-RX serial loopback, RX-to-TX parallel loopback, AC JTAG enable, LBERT controls, RX status matching/counting, and analog test bus controls.
- Lane 0 analog TX state for power, DCC DAC, termination, equalization, regulator/vref/slew/peaking controls, and status readback.

Persistence is hardware-defined. Programmed fields generally last until link reconfiguration, PHY reset, power gating, suspend/resume restore, driver reset, or ASIC reset. Status, calibration, timer, counter, and ack fields may be read-only, sticky, self-clearing, write-one-to-clear, or valid only while the related PHY clocks and power islands are active. This generated header does not express those access semantics.

## Dependencies And Integration Points

This chunk must stay synchronized with AMD's generated DPCS 4.2.2 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` provides the matching `reg*`, `ix*`, and base-index address constants for these field macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` directly includes both DPCS 4.2.2 generated headers and defines `DPCS_BASE__INST0_SEG*` for this ASIC generation.
- The same resource file uses `DPCS_DCN31_REG_LIST(id)`, `DPCS_DCN31_MASK_SH_LIST(__SHIFT)`, `DPCS_DCN31_MASK_SH_LIST(_MASK)`, and `DCN3_1_RDPCSTX_REG_LIST(0..4)` to build DPCS and RDPCS TX register tables.
- Higher-level display components consume those tables through DCN 3.1 link encoder, UNIPHY/DIO, link training, clock source, hardware sequencing, and resource-pool paths.

Behaviorally, this slice integrates with DisplayPort/HDMI PHY bring-up: PLL programming, spread-spectrum setup, link clock generation, lane power-state transitions, lane width/rate selection, transmitter cursor/equalization programming, link-test diagnostics, and analog calibration/status collection.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while touching the wrong MMIO bits, corrupting adjacent fields, failing PLL lock, breaking link training, or producing marginal signal integrity.
- The file is generated metadata. Manual edits can diverge from the authoritative AMD register database, the offset header, firmware assumptions, and silicon documentation.
- The A/B MPLL families and lane 0/lane 1 families are highly repetitive. Instance-specific generator or copy errors can leave one PLL or lane broken while a neighboring instance works.
- The chunk starts after the `DPCSSYS_CR3_SUP_DIG_MPLLB_HDMI_CLK_OVRD_IN` shift definitions, so local shift/mask pair checks must account for that artificial boundary. The lane 1 register family also continues after this chunk.
- Override fields are hazardous because they can bypass normal hardware control. Setting an override-enable bit without the intended value, or failing to clear it, can force stale PLL, clock, power, lane, or analog state across modesets and suspend/resume.
- PLL and SSC fields are timing-sensitive. Bad fractional-N, spread-spectrum, charge-pump, lock-timer, or divider masks can cause unstable clocks, link-training failures, display blanking, or receiver-specific HDMI/DP issues.
- Analog and DCC/EQ controls affect electrical behavior. Incorrect termination, vref, peaking, cursor, slew, regulator, or DCC DAC programming may pass simple bring-up but fail compliance, high-bit-rate modes, long cables, or hotplug/retrain cycles.
- Status, ack, timer, and counter fields may have side effects or validity windows not visible in this header. Consumers must not infer read/write semantics from `_MASK` names alone.

## Test Signals

Useful validation should combine generated-header checks with hardware behavior:

- Build AMDGPU display support with DCN 3.1.5 enabled. Missing or renamed macros should fail where `dcn315_resource.c` expands DPCS and RDPCS register, shift, and mask tables.
- Mechanically diff this range against AMD's authoritative DPCS 4.2.2 register database and compatible nearby DPCS generated headers where the CR3 supervisor/lane layouts are expected to match.
- Check shift/mask pairing for fields wholly inside lines 64389-66756, allowing the known leading partial register where only masks are present in this chunk.
- Exercise DP and HDMI links on DCN 3.1.5 hardware across hotplug, modeset, suspend/resume, link-rate changes, lane-count changes, MST or multi-display configurations, and retraining after link errors.
- Validate PLL behavior with logs or hardware traces for MPLL lock, spread-spectrum enablement, fractional-N programming, calibration completion, and clock-stable timing.
- Run link-training and signal-quality tests that stress cursor/pre/post settings, EQ overrides, DCC/termination controls, long cables, high refresh rates, and high bit-depth modes.
- Monitor kernel logs and display diagnostics for failed link training, PHY reset loops, PLL timeout messages, HPD-only failures, resume-only blank displays, intermittent bit errors, compliance-test failures, or status counters that stop updating.

## Cross-Chunk Notes

This is a middle chunk of `dpcs_4_2_2_sh_mask.h` within the `DPCSSYS_CR3` block. Earlier chunks contain the CR3 indexed address/data accessors and the start of the supervisor register set, including the shift definitions for the leading `DPCSSYS_CR3_SUP_DIG_MPLLB_HDMI_CLK_OVRD_IN` masks. Later chunks continue lane 1 and subsequent DPCS register families. The final per-file research document should merge adjacent chunks before making whole-file claims about all DPCS instances, all lanes, or complete PLL/lane coverage.
