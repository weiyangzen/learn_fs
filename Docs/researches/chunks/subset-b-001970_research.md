# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 100341-102725

## Purpose

This chunk is a generated DCN 3.2.0 shift/mask header segment for C20 PHY lane control registers. It contains C preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for receiver adaptation/statistics/analog-transfer controls on `C20_PHY_CR1_LANE2`, followed by transmitter and receiver override, status, calibration, and power-state controls on `C20_PHY_CR1_LANE3`.

The range contains 2,177 `#define` entries across 208 register comment sections. It is not executable code, but it is an MMIO register layout contract: higher-level AMDGPU display, DMUB firmware-control, BIOS transmitter-control, and PHY sequencing paths rely on these generated definitions being consistent with the hardware register map and the matching offset header.

## Important APIs, Types, and Register Groups

There are no functions, structs, or runtime APIs declared in this chunk. The important interface is the generated naming scheme consumed by AMD display register helpers:

- `<register>__<field>__SHIFT` gives the starting bit position for a field.
- `<register>__<field>_MASK` gives the field mask in the register word.
- The names pair with same-register offset definitions from the DCN/DPCS register headers and can be folded into generated shift/mask tables or direct MMIO helper invocations.

Major register domains in the chunk:

- `C20_PHY_CR1_LANE2_DIG_RX_ADPTCTL_*`: RX adaptation and data clock compensation controls, including DCC data/bypass offset values, override enables, fast-settle flags, adaptation saturation limits, slicer search mode (`SSM_*`) configuration, final DAC code/status, and abort/FSM status.
- `C20_PHY_CR1_LANE2_DIG_RX_STAT_*`: sample/statistic collection controls and results, pattern masks, correlation/stat source selection, counter enables, sample counters, statistic counters, clock control, stop/freeze behavior, and extended load values.
- `C20_PHY_CR1_LANE2_DIG_RX_IQC_CTL_*`: RX IQ correction reset/config/status fields, including bypass/data values, step-size/jump configuration, data enable, DFE-bypass use, and FSM state.
- `C20_PHY_CR1_LANE2_DIG_ANA_XF_RX_*`: digital-to-analog RX transfer and override fields for power, signal detect, VCO, calibration, DAC control, AFE override inputs, scope/slicer selection, analog IQ calibration, loopback, update enables, sample selection, termination override, analog status, and analog CREG registers.
- `C20_PHY_CR1_LANE3_DIG_ASIC_*`: lane 3 ASIC-facing TX/RX controls for reset/data/request/pstate/rate/width/VCO/loopback/equalizer/signal-detect overrides, ASIC input snapshots, ASIC output handshake (`ACK`, `VALID`, `ADAPT_STS`), and miscellaneous override enables.
- `C20_PHY_CR1_LANE3_DIG_TX_PWRCTL_*`: TX P-state programming for `P0`, `P0S`, `P1`, and `P2`, plus TX power-up timing and status. Fields control refgen, VCM hold, analog clock/reset/serial enable, digital clock enable, data enable, RX detect, voltage boost, analog DCC, voltage-regulator bleeders, and word clock enable.
- `C20_PHY_CR1_LANE3_DIG_TX_DCC_CTL_*`, `TX_STAT_*`, `TX_CLK_ALIGN_*`, `TX_LBERT_*`, and `TX_FIFO_CTL`: TX DCC offset overrides/status, statistic counters, calibration clock control, clock-alignment control/status, LBERT pattern generation, level-calculation status, and FIFO control.
- `C20_PHY_CR1_LANE3_DIG_ANA_XF_TX_*`: TX analog transfer/override state for power, equalization, DCC calibration, termination overrides, analog status outputs/inputs, equalizer outputs, and TX analog CREG registers.
- `C20_PHY_CR1_LANE3_DIG_ASIC_RX_*`: lane 3 RX ASIC override controls and readbacks for reset/invert/data/requests, pstate, DFE bypass, reference and VCO load values, clock and CDR controls, signal detect, equalization/DFE taps, CDR VCO config, and ASIC RX status.
- `C20_PHY_CR1_LANE3_DIG_RX_PWRCTL_RX_PSTATE_P0*`: beginning of lane 3 RX P-state programming. The chunk fully covers `RX_PSTATE_P0` and starts `RX_PSTATE_P0S`, ending at the first two P0S masks.

Representative field semantics:

- Override/value pairs follow a common convention: a field such as `*_OVRD_VAL`, `*_OVRD`, or a raw tuning value is paired with `*_OVRD_EN` so firmware or driver debug paths can force a hardware value rather than use automatic sequencer state.
- P-state fields describe persistent lane power recipes for active and lower-power states. TX fields enable or hold analog/digital blocks; RX fields enable AFE, clock regulators, deserializer, CDR, VCO reset/calibration, continuous calibration, digital clock, DFE, and bypass-slicer paths.
- Statistic and calibration registers include start/stop, load, sample-count-done, counter enable, FSM state, final code, and status fields used to observe adaptation or calibration progress.
- Reserved fields are explicitly listed with masks, which is useful for full generated table completeness but dangerous if software ever writes them intentionally.

## Control Flow

This header has no direct control flow. Runtime behavior appears when DCN 3.2 code or firmware-support code uses the register layout to compose MMIO reads and writes:

- DCN 3.2 DMUB support includes `dcn_3_2_0_offset.h` and `dcn_3_2_0_sh_mask.h` in `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`; that file initializes register offset/shift/mask tables for DMUB reset, mailbox, GPINT, firmware boot status, diagnostic, and boot-option handling. This chunk is in the same generated header, although the C20 PHY lane macros are not prominent direct call-site names in the normal display source.
- Display resource and link layers for DCN 3.2/3.2.1 construct link encoders, stream encoders, HPO DP link encoders, AUX engines, and clocks. Link-enable flows ultimately go through BIOS/DMUB/transmitter control interfaces that program PHY state and wait for PHY initialization.
- BIOS transmitter-control paths in `drivers/gpu/drm/amd/display/dc/bios/command_table2.c` map link transmitter IDs to PHY IDs and carry lane count, signal type, symbol clock, link rate, and PHY transition bitmasks into AtomBIOS or ACPI interlock calls. Those flows are the practical owners of C20 PHY lane sequencing on production paths.
- DMUB boot options expose PHY-related policy such as skipping panel PHY-init sequencing or disallowing PHY access. If those options route PHY ownership to firmware, these masks still document the register layout that firmware-facing or diagnostic code must match.

Because this range is a data-only generated header, the "flow" is best understood as: link policy chooses a PHY lane and requested link state, BIOS/DMUB/link-encoder code programs or delegates lane power/training/calibration, and these constants define how individual register fields are encoded when software touches the C20 PHY register file.

## State and Persistence Behavior

The file itself stores no runtime state. Its constants describe hardware state that persists in PHY MMIO registers until reset, power gating, firmware reprogramming, link disable/re-enable, suspend/resume, or another MMIO write changes it.

Important state domains represented here include:

- RX adaptation state: DCC offsets, CTLE/DFE saturation limits, slicer search mode setup, final DAC code, adaptation abort flags, and RX IQ correction FSM state.
- RX/TX statistic state: sample counters, statistic counters, correlation and data masks, sample-count done bits, freeze/stop controls, and calibration comparison clock settings.
- Analog override state: lane power enables, signal-detect thresholds, VCO calibration, AFE/DFE/equalizer tuning, DAC ranges, termination codes, and analog CREG override bits.
- ASIC handshake state: lane request/ack/valid/adaptation status fields that bridge the PHY digital logic to ASIC control logic.
- TX state: P-state recipes, power-up timing, DCC calibration offsets/status, clock alignment, LBERT pattern generation, FIFO operation, equalization outputs, and DCC calibration data.
- RX state on lane 3: RX reset/invert/data/low-power/pstate controls, CDR and VCO configuration, signal detect, equalization/DFE taps, ASIC input/output status, and P0/P0S power-state fields.

Several fields are status or clear/update controls rather than simple latched configuration. Incorrect masks can therefore create persistent mis-observation as well as bad programming: polling can wait on the wrong bit, ack writes can clear the wrong status, and override enables can leave a lane forced after a mode change.

## Dependencies and Integration Points

This chunk depends on the generated DCN/DPCS register ecosystem:

- The matching offset header supplies register addresses and instance offsets; this file supplies the field encoding.
- The same C20 PHY field families also appear in `drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h`, indicating the generated register database exposes the C20 PHY through DPCS/DCN-oriented headers as well.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c` directly includes the DCN 3.2 offset and shift/mask headers and initializes per-generation DMUB register metadata.
- `drivers/gpu/drm/amd/display/dmub/dmub_srv.h` and related DMUB source files expose PHY ownership/policy flags such as `disallow_phy_access`, `lower_hbr3_phy_ssc`, and PHY-init wait behavior.
- `drivers/gpu/drm/amd/display/dc/bios/command_table2.c` integrates display link policy with BIOS transmitter-control, including PHY ID lookup, lane count, signal, symbol clock, DP link rate, PHY transition bitmask, and ACPI transition interlocks.
- `drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.c` and DCN 3.2/3.2.1 resource code show the surrounding link encoder architecture that assigns link encoder instances and exposes DP PHY pattern, fast-training, and PHY mux behavior.

There are no normal in-tree C call sites that spell these exact C20 lane field constants in the searched display source; that suggests these fields are mostly generated low-level register metadata, firmware-facing definitions, or diagnostics/debug support rather than routine mode-set code paths.

## Risks

- Bit layout drift is the dominant risk. Any wrong shift or mask silently encodes the wrong hardware field and can break link bring-up, lane power sequencing, calibration, signal detect, RX/TX equalization, or status polling.
- Lane-copy errors are plausible because the same C20 PHY register families repeat across lanes. A lane 2/lane 3 mismatch can compile cleanly while touching the wrong lane's state or giving misleading debug output.
- Override-enable fields are high risk. A bad mask can unintentionally force reset, pstate, rate, width, CDR, VCO, equalizer, signal-detect, or DFE state and leave the lane unusable until a full reset.
- P-state fields directly control analog and digital power. Incorrect TX/RX P-state masks can cause excessive power use, failed wake, unstable data recovery, missing clocks, or broken suspend/resume behavior.
- Calibration and statistic fields can be both configuration and observation points. Mis-masked final-code, FSM-state, counter-done, or abort bits can make calibration timeouts look like hardware failures.
- The chunk boundary ends mid-register for `C20_PHY_CR1_LANE3_DIG_RX_PWRCTL_RX_PSTATE_P0S`; merge/reconciliation must treat adjacent chunks as one continuous register description to avoid losing the remaining P0S masks.
- Reserved-bit masks are present. Any generated table or manual code that writes a whole register using these constants must preserve reserved bits unless hardware documentation explicitly permits writing them.

## Test Signals

Useful validation signals are mostly integration and hardware oriented:

- Build coverage: AMDGPU display and DMUB DCN 3.2 code compiles with no missing generated field names or duplicate macro conflicts.
- Register-table sanity: generated offset and shift/mask headers agree on C20 PHY register names, and C20 PHY definitions in DCN and DPCS headers remain consistent for shared blocks.
- Link bring-up: DP/HDMI/eDP links using lane 2/lane 3 PHY resources train reliably across common rates, lane counts, hotplug, and mode-set transitions.
- PHY power behavior: suspend/resume, display blank/unblank, idle power, panel power sequencing, and PHY init waits do not regress.
- Calibration behavior: RX DCC, VCO, signal-detect, IQ correction, slicer search, TX DCC, clock alignment, and equalization status converge without timeout or sticky abort bits.
- Override/debug behavior: any diagnostics that force PHY fields can set and clear override-enable bits without leaving lanes stuck in reset, wrong pstate, or forced equalizer/CDR state.
- Error counters/status: RX/TX statistic counters, sample-done bits, LBERT pattern paths, FIFO state, and ASIC handshake status report plausible values during link training and link idle.
- Firmware ownership tests: configurations that skip PHY init or disallow host PHY access continue to boot DMUB and initialize displays, confirming software and firmware agree on PHY control boundaries.
