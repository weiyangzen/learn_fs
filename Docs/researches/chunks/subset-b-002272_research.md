# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 31718-34157

## Purpose

This chunk is a generated AMD DPCS 3.1.4 shift/mask header slice for display PHY/controller register fields. It contains no executable C logic; its public surface is a set of preprocessor constants that encode bit positions (`__SHIFT`) and bit masks (`_MASK`) for DPCS register fields.

The requested range contains 2,142 `#define` entries over 2,440 lines. It starts inside the `DPCSSYS_CR1_LANEX_DIG_TX_PWRCTL_TX_PWRUP_TIME_0` field pair, covers a large CR1 per-lane TX/RX/PCS/PMA/FSM/IRQ register-field section, then crosses into the `addressBlock: dpcssys_cr2_rdpcstxcrind` supervisor/common PLL block. The range ends inside `DPCSSYS_CR2_SUP_DIG_MPLLA_SSC_PEAK_2`, before that register's mask definitions.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or direct MMIO accesses in this range. The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: the field's least-significant bit position inside the hardware register.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used to isolate or update that field.

The main register-field families in this chunk are:

- TX lane power and timing fields: `TX_PWRUP_TIME_0-5`, DCC control-bank address/data, DCC DAC control/range/select/ack/address, TX clock alignment, and TX LBERT pattern/error-injection controls.
- RX lane power state and bring-up fields: `RX_PSTATE_P0`, `P0S`, `P1`, `P2`, RX power-up timers, analog AFE/clock/deserializer/CDR enable bits, VCO reset/calibration bits, and digital clock enable bits.
- RX VCO and CDR fields: VCO calibration control, start values, calibration steps, result/status readbacks, CDR SSC on/off counters, loop gain override fields, DPLL frequency, and frequency-bound enable/range fields.
- RX adaptation and equalization fields: adaptation configuration registers, reset controls, attenuation/VGA/CTLE/DFE tap status, DFE data/error DAC offsets, slicer controls, DAC control selectors, and indirect CR bank address/data.
- RX status/statistics fields: load-value, data mask, match controls, statistic controls, sample counts, statistic counters, calibration-comparison clock control, and statistic stop fields.
- MPHY and analog lane fields: MPHY PWM/termination/stable-count fields, analog TX/RX override outputs, TX equalization override fields, RX DAC/AFE/CTLE/scope/slicer/IQ/calibration controls, analog status, termination-code overrides, signal-detect overrides, TX DCC DAC overrides, and raw analog TX/RX control/readback registers.
- Raw lane PCS/PMA transfer fields: TX/RX override input/output, PCS input/output, ACK handshakes, pstate and MPLL select/enable fields, serial/parallel loopback controls, lane number, RX adaptation ACK/FOM, directed TX pre/main/post cursor fields, ATE override surfaces, RX EQ override fields, PMA lane/supervisor override and status fields, MPHY override fields, and RX adaptation override output.
- Raw lane FSM and IRQ fields: FSM override, memory/status monitors, fast RX startup/adaptation/calibration/power-up/VCO wait/VCO cal controls, common calibration status, fast flags, CR lock, TX DCC flags/status, OCLA debug fields, TX EQ update flag, RX IQ phase offset, RX/TX reset/request/rate/pstate/adaptation IRQs, clear registers, IRQ masks, lane transceiver-mode IRQs, loopback IRQs, PH2 calibration IRQs, and DCC on-demand/TX IRQ fields.
- Raw lane TX/RX control fields: TX FSM/clock controls, TX DCC continuous status, OCLA/UPCS OCLA fields, RX FSM/LOS mask/data-enable override controls, off-cancel/continuous-adaptation status, and RX UPCS OCLA.
- CR2 supervisor/common PLL fields: ID code placeholders, reference-clock override fields, MPLLA/MPLLB divider and HDMI clock override fields, MPLLA enable/divider/VCO/calibration/frac-N/SSC fields, MPLLA multiplier, and the beginning of MPLLA SSC peak programming.

Most masks in this range are 16-bit style values ending in `L`, matching the DPCS indirect-register field width used by these lane and supervisor blocks.

## Control Flow

This header has no runtime control flow. It participates in compile-time register-table construction:

1. DCN 3.1.4 resource code includes `dpcs_3_1_4_offset.h` and this matching `dpcs_3_1_4_sh_mask.h`.
2. Register-list and shift/mask-list macros token-paste DPCS register and field names into typed tables for the display resource pool and PHY/link encoder plumbing.
3. Runtime display code uses AMD register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` with those offset/shift/mask tables.
4. The actual sequencing for power-up, PLL programming, lane training, calibration, interrupt handling, and debug readback is implemented in DC/link/PHY code and hardware state machines outside this generated header.

The macros in this chunk describe where bits live; they do not encode which fields are read-only, write-one-to-clear, self-clearing, latched, or sequencing-sensitive.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in DPCS CR1 per-lane and CR2 supervisor/common registers:

- TX and RX power-state configuration, including analog enable, clock enable, reset, data enable, receive-detect, common-mode, Vboost, DCC compensation, and programmed bring-up delays.
- Calibration and adaptation state for RX VCO, CDR/DPLL, AFE, VGA, CTLE, DFE taps, slicer offsets, IQ phase, and continuous adaptation controls.
- Test and diagnostic state for LBERT, OCLA, alternate buses, analog test bus measurement, statistic counters, match controls, debug selectors, and raw status/readback fields.
- PCS/PMA handshake state for pstate, MPLL selection and enablement, lane override enables, ACK bits, lane numbering, RX valid override, TX/RX serial or parallel loopback, and RX/TX directed coefficient controls.
- Interrupt state for RX/TX reset and request events, rate and pstate changes, adaptation request/disable events, PH2 calibration request/disable events, lane mode changes, loopback enable changes, and DCC on-demand events.
- Supervisor PLL/reference-clock state for reference clock source/range, bandgap, HDMI mode, MPLLA/MPLLB divider/HDMI clock overrides, MPLLA enable, standby, VCO frequency, calibration force, fractional-N, SSC enable/update, and SSC peak programming.

Persistence is hardware-defined. Configuration fields generally remain until link reprogramming, modeset, power gating, suspend/resume, GPU reset, or ASIC reset rewrites them. Status, ACK, IRQ, and statistics fields may be latched, clear-on-write, sampled, self-clearing, or valid only while the lane/common PLL power and clock domains are active. This generated header does not record those access semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 3.1.4 register database and its companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h` supplies matching `ixDPCSSYS_*` register offsets for the fields described here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c` directly includes both DPCS 3.1.4 generated headers and initializes DCN 3.1.4 resource tables.
- The same resource file uses `DPCS_DCN31_MASK_SH_LIST(__SHIFT)`, `DPCS_DCN31_MASK_SH_LIST(_MASK)`, and `DCN3_1_RDPCSTX_REG_LIST(...)` around the DPCS include site, so field names in this header are consumed through DCN 3.1-era DPCS table macros.
- Display link encoder, PHY, AUX/link-training, clock-source, and hardware-sequencing code consume those initialized tables indirectly when programming display PHY lanes and shared MPLL/reference-clock state.

Behaviorally, this range sits under display link bring-up and maintenance. It describes the low-level bit layout used when the driver enables or powers down TX/RX lanes, selects MPLLs, configures reference/HDMI clocks, runs receiver calibration/adaptation, handles lane-level interrupts, or reads debug/status counters.

## Risks And Edge Cases

- These constants are untyped preprocessor values. An incorrect shift or mask can compile cleanly while writing the wrong DPCS field, corrupting an adjacent reserved bit, or misreading status.
- The file is generated metadata. Manual edits risk divergence from the authoritative AMD register database, the matching offset header, firmware assumptions, and silicon documentation.
- Chunk boundaries are artificial. Line 31718 starts with the two masks for `TX_PWRUP_TIME_0`; the corresponding shifts are just before this range. Line 34157 stops after `MPLLA_SSC_PEAK_2` shifts; its masks are in the next chunk.
- Power and calibration fields are sequencing-sensitive. Bad masks for RX/TX pstate enables, VCO reset/calibration, DPLL bounds, CDR SSC gains, DCC DAC handshakes, or MPLL enable/divider fields can cause link-training failures, blank displays, unstable clocks, high error rates, or resume-only failures.
- ACK, IRQ, and clear fields are side-effect-sensitive. Confusing IRQ status, clear, and mask bits can cause missed lane events, stuck interrupts, repeated IRQs, or failure to observe adaptation/pstate/rate changes.
- The raw PCS/PMA override and ATE fields can bypass normal state-machine control. Incorrect override masks may force loopback, pstate, MPLL, RX-valid, or TX/RX data-enable behavior that is hard to diagnose from higher-level display state.
- Repeated lane-style register groups are copy-sensitive. A generator error can affect one lane path or one sub-block while nearby groups still appear correct.
- Debug/statistic counter fields are not functional programming knobs, but wrong masks can hide useful failure evidence during link bring-up, PHY characterization, or manufacturing diagnostics.
- CR2 supervisor fields affect shared clock resources. Bad reference clock, MPLLA/MPLLB divider, HDMI clock, fractional-N, or SSC masks can break multiple links or modes that share the same common PLL resource.

## Test Signals

Useful validation combines generated-header checks with display hardware behavior:

- Build AMDGPU display support with DCN 3.1.4 enabled. Missing or renamed macros should fail where `dcn314_resource.c` initializes DPCS register, shift, and mask tables.
- Mechanically verify that each field in this range has the expected `__SHIFT`/`_MASK` pair, while allowing the known chunk-boundary exceptions for `TX_PWRUP_TIME_0` and `MPLLA_SSC_PEAK_2`.
- Cross-check this slice against `dpcs_3_1_4_offset.h` so every complete register group in the chunk has a corresponding `ixDPCSSYS_*` offset.
- Diff against AMD's authoritative DPCS 3.1.4 register database and nearby generated variants such as `dpcs_3_0_3_sh_mask.h`, `dpcs_4_0_0_sh_mask.h`, or `dpcs_4_2_0_sh_mask.h` where register layouts are expected to be compatible.
- Exercise DisplayPort/HDMI link bring-up across all available PHY lanes and rates. Expected signals are stable link training, correct lane power transitions, no false lane IRQs, and no stuck ACK/status bits.
- Exercise hotplug, modeset, stream disable/enable, suspend/resume, and GPU reset paths to catch persistence or reinitialization mistakes in power, pstate, PLL, and calibration fields.
- Validate high-bandwidth and clock-sensitive modes that stress MPLL divider, HDMI clock, fractional-N, and SSC programming. Watch for blank displays, link retraining loops, PHY lock failures, or display corruption.
- Use register dumps or PHY debug traces during failing links to confirm RX adaptation, VCO/CDR status, statistic counters, DCC status, and FSM status fields decode correctly.
- Exercise diagnostic paths where available: LBERT, OCLA, statistic match/count controls, analog test bus/readback fields, loopback controls, and ATE overrides.

## Cross-Chunk Notes

The previous chunk owns most of TX power-state programming and the shifts for `DPCSSYS_CR1_LANEX_DIG_TX_PWRCTL_TX_PWRUP_TIME_0`; this chunk starts with that register's masks. The next chunk should begin with the missing masks for `DPCSSYS_CR2_SUP_DIG_MPLLA_SSC_PEAK_2` and continue MPLLA SSC step-size and later CR2 supervisor/common PLL fields. The final per-file research document should reconcile those boundaries before making whole-file claims about all DPCS 3.1.4 lane and supervisor fields.
