# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 158823-161217

## Purpose

This chunk is a generated DCN 3.2.0 ASIC register shift/mask segment for the C20 PHY CR3 common always-on block and lane 0 digital PHY blocks. It contains C preprocessor constants that define bit positions (`__SHIFT`) and masks (`_MASK`) for 16-bit PHY register fields. The range is not executable code; it is a hardware register layout contract used by AMDGPU display, DMUB, BIOS transmitter-control, diagnostic, and low-level PHY programming paths.

The chunk contains 2,169 `#define` entries across 227 register field groups. It begins inside the complete field-definition block for `C20_PHY_CR3_RAWCMN_DIG_AON_SRAM_IN` because that register's comment marker is on the preceding line, then proceeds through CR3 raw common firmware/SRAM/supervisor registers, lane 0 ASIC-facing TX/RX override and status registers, TX/RX power-control registers, TX analog-transfer/calibration/status registers, RX CDR/VCO/adaptation/statistics registers, and ends at the complete `C20_PHY_CR3_LANE0_DIG_RX_STAT_MATCH_CTL6` field block.

## Important APIs, Types, and Register Groups

There are no functions, structs, enums, or runtime APIs declared here. The important interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the register word.
- Register address macros are supplied by the matching DCN 3.2.0 offset header; this file supplies only field encoding.

Major register domains covered in this chunk:

- `C20_PHY_CR3_RAWCMN_DIG_AON_*`: always-on common PHY control/status for SRAM bypass/init, firmware and raw version readback, RTUNE recalibration handshake, SRAM end/begin/recovery addresses, supervisor clock/firmware-stop/SRAM/ROM overrides, APB timeout configuration, power/clock supervisor status, MPLL context restore, metadata location, and SRAM recovery-address override.
- `C20_PHY_CR3_LANE0_DIG_ASIC_*`: lane-level ASIC-facing override and readback registers for TX and RX control. These include loopback, lane mode, clock-ready, reset, invert, data-enable, request, low-power detect, pstate, rate, width, MPLL selection, RX detect, VCO load, CDR load, DFE bypass, signal-detect, equalizer and DFE tap controls, valid/adaptation status, and miscellaneous override gates.
- `C20_PHY_CR3_LANE0_DIG_TX_PWRCTL_*`: TX pstate recipes for `P0`, `P0S`, `P1`, and `P2`; TX power-up timing; TX control and status. The pstate fields control analog reference generation, VCM hold, analog clock/reset/serial enable, digital clock, data enable, RX detect, voltage boost, analog DCC, regulator bleeders, and word clock enable.
- `C20_PHY_CR3_LANE0_DIG_TX_DCC_CTL_*`, `TX_STAT_*`, `TX_CLK_ALIGN_*`, `TX_LBERT_*`, and `TX_FIFO_CTL`: TX DCC offset overrides/status, statistic load and sample counters, calibration comparison clock control, stop controls, clock alignment control/status, loopback BERT pattern generation, level-calculation status, and FIFO gating.
- `C20_PHY_CR3_LANE0_DIG_ANA_XF_TX_*`: digital-to-analog TX transfer fields for analog override outputs, termination-code overrides, analog DCC enable/config/calibration controls, equalization overrides and status, analog status inputs/outputs, and TX analog CREG fields.
- `C20_PHY_CR3_LANE0_DIG_RX_PWRCTL_*`: RX pstate recipes for `P0`, `P0S`, `P1`, and `P2`; RX power-up timing; RX control and status. These fields gate AFE, clock regulators, divided clocks, DCC, deserializer, CDR, VCO reset/calibration, continuous calibration, digital clock, DFE, bypass slicer, and force-write behavior.
- `C20_PHY_CR3_LANE0_DIG_RX_VCOCAL_*`, `RX_CDR_*`, and `RX_DPLL_*`: RX VCO calibration configuration/timing/status, CDR control/status, and DPLL frequency/bound fields.
- `C20_PHY_CR3_LANE0_DIG_RX_ADPTCTL_*`: RX adaptation configuration/status for ATT, VGA, CTLE, DFE taps, slicer levels, DCC offsets, fast flags, reset behavior, adaptation timers/limits, search-state-machine configuration, and final-code reporting.
- `C20_PHY_CR3_LANE0_DIG_RX_STAT_*`: RX statistics and pattern-matching controls, including load values, data masks, match patterns, statistic/correlation source selection, sample counters, statistic counters, calibration comparison clock settings, freeze/stop controls, and `MATCH_CTL6` pattern fields.

Common field patterns are important. Many registers use explicit value/enable pairs such as `*_OVRD_VAL` plus `*_OVRD_EN`; those allow firmware, debug code, or bring-up paths to force a value over the normal sequencer output. Status and counter registers expose `*_DONE`, FSM state, abort, ack, valid, and power-state bits that are intended for polling or diagnostics. Reserved fields are fully represented with masks for generated table completeness, but consumers must not write reserved bits unless hardware documentation explicitly permits it.

## Control Flow

This header has no direct control flow. Runtime flow is introduced by code that includes the generated DCN offset and shift/mask headers and then composes MMIO field reads/writes from these constants.

Observed integration in this source tree:

- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c` includes `dcn_3_2_0_sh_mask.h` and the matching offset header for DCN 3.2 DMUB register metadata and boot-option handling.
- DCN 3.2 display code also includes this generated header from resource, clock-manager, GPIO, and IRQ service implementation files. Those include paths make the generated register contract visible to generation-specific display initialization and services.
- BIOS/DMUB transmitter-control paths route link enable/disable requests through `bp_transmitter_control`, DMUB VBIOS commands, PHY IDs, lane counts, link rates, signal type, and PHY-transition interlocks. These higher-level flows are the practical owners of PHY sequencing even when this exact chunk's macros are not directly spelled at normal call sites.
- DMUB boot options and service APIs expose PHY policy such as waiting for PHY init, skipping panel PHY-init sequencing, and disallowing host PHY access. Those ownership decisions determine whether host code or firmware programs the underlying C20 PHY registers described here.

The implied flow is: display link policy selects a transmitter/PHY and requested link state; BIOS/DMUB/link-encoder code performs or delegates transmitter and PHY programming; low-level register helpers use offset plus shift/mask definitions like these to encode individual C20 PHY fields; status and calibration fields are polled to confirm power, calibration, adaptation, and training progress.

## State and Persistence Behavior

The file itself stores no runtime state. Its macros describe persistent hardware state in C20 PHY MMIO/register-file locations. Values persist until modified by another MMIO write, firmware sequence, PHY reset, power gating, suspend/resume, display mode-set/link transition, or full device reset.

Important state domains represented here:

- Common always-on state: SRAM boot/bypass/init flags, firmware/raw version registers, recalibration handshake bits, APB timeout settings, supervisor clock/power/firmware-stop overrides, and SRAM recovery/metadata addresses.
- TX state: forced ASIC inputs, TX pstate recipes, power-up timing, DCC offset controls, clock alignment, LBERT pattern data, FIFO enables, analog output overrides, TX equalization status, and TX analog CREG settings.
- RX state: forced ASIC inputs, signal detect, VCO/CDR load and calibration controls, equalizer/DFE settings, RX pstate recipes, DPLL bounds, adaptation limits/status, DCC offset fields, fast flags, slicer/search configuration, and final adaptation code.
- Statistic state: sample counters, statistic counters, pattern masks, match values, counter enable bits, done bits, stop/freeze controls, and calibration comparison clock settings.

Some fields are configuration bits, some are status/readback bits, and some are clear/update/start/stop controls. A wrong mask can therefore corrupt both programming and observation: software may force the wrong pstate, fail to enable a clock, poll the wrong done bit, misread adaptation status, or leave an override enabled across later link transitions.

## Dependencies and Integration Points

This chunk depends on the generated AMD display register ecosystem:

- `dcn_3_2_0_offset.h` provides register addresses such as CR3 lane 0 offsets; `dcn_3_2_0_sh_mask.h` provides field shifts and masks.
- Display code includes this generated header from `dmub_dcn32.c`, `dcn32_resource.c`, `dcn32_clk_mgr.c`, `hw_translate_dcn32.c`, `hw_factory_dcn32.c`, and `irq_service_dcn32.c`.
- BIOS parser and transmitter-control code in `drivers/gpu/drm/amd/display/dc/bios/command_table2.c` maps display transmitter requests to AtomBIOS/DMUB command payloads, including PHY IDs and PHY transition parameters.
- Link encoder code under `drivers/gpu/drm/amd/display/dc/dio/dcn32/` maps transmitters to PHY IDs and participates in DP/alt-mode PHY-related command dispatch.
- DMUB command/service definitions under `drivers/gpu/drm/amd/display/dmub/` define boot options and VBIOS command payloads for PHY access, transmitter control, DPPHY init, and PHY-init wait behavior.
- Security/HDCP/CRC paths also carry PHY IDs for link-scoped operations. They do not program these masks directly, but they depend on stable transmitter-to-PHY mapping and link ownership decisions.

Within the searched display source, normal C code rarely spells the exact `C20_PHY_CR3_LANE0_*` field names directly. That suggests these definitions are primarily generated low-level metadata, firmware-facing register contract, bring-up/diagnostic support, or used indirectly through tables and register helper macros.

## Risks

- Bit layout drift is the primary risk. Any incorrect shift or mask silently encodes the wrong hardware field and can break PHY SRAM boot, RTUNE, APB access, supervisor clocks, lane power sequencing, link training, adaptation, or status polling.
- Override/value pairs are high risk. Mis-masking an `*_OVRD_EN` or `*_OVRD_VAL` field can force reset, pstate, rate, width, VCO, CDR, signal detect, equalizer, DFE, or loopback behavior and leave the lane unusable until reset.
- Pstate fields directly control analog and digital power. Bad TX/RX pstate masks can produce failed wake, missing clocks, unstable CDR, broken suspend/resume, excessive power draw, or intermittent link training failures.
- Calibration/status fields can be mistaken for ordinary configuration. Incorrect VCO, DCC, CDR, adaptation, statistic, or done-bit masks can make calibration timeouts look like hardware faults or make failing hardware appear healthy.
- Generated lane/register repetition increases copy/paste risk. The CR3 common and lane 0 field families mirror similar C20 PHY blocks elsewhere in the header; a lane or CR instance mismatch can compile cleanly while targeting the wrong PHY register.
- The range starts without the `SRAM_IN` comment marker because that marker is on the preceding line. Merge/reconciliation should associate the first eight macros with `C20_PHY_CR3_RAWCMN_DIG_AON_SRAM_IN`, not treat them as orphaned fields.
- Reserved masks are present throughout the chunk. Consumers must preserve reserved bits during read-modify-write sequences unless the hardware spec requires a defined write value.

## Test Signals

Useful validation signals are mostly build, generated-register, and hardware integration oriented:

- Build coverage: DCN 3.2 AMDGPU display, DMUB, GPIO, IRQ, clock, and resource code compiles with no missing or conflicting generated macro names.
- Generated-header consistency: CR3 C20 PHY register names in `dcn_3_2_0_offset.h` match the shift/mask groups in this file, and shared C20 PHY definitions stay consistent with any corresponding DPCS-generated headers.
- Link bring-up: DP, HDMI, and eDP links assigned to the relevant PHY resources train reliably across lane counts, link rates, hotplug, mode-set, blank/unblank, and fast-training paths.
- PHY ownership behavior: DMUB configurations that wait for PHY init, skip panel PHY init, or disallow host PHY access still initialize displays and do not race host-side PHY programming.
- Power behavior: suspend/resume, display idle, panel power sequencing, and link disable/re-enable do not regress, with no stuck TX/RX power-state machine status bits.
- Calibration behavior: SRAM init, RTUNE, TX/RX DCC, VCO calibration, CDR lock, signal detect, equalization, DFE/adaptation, and slicer/search-state-machine status converge without unexpected aborts or timeouts.
- Diagnostic/statistic behavior: RX/TX statistic counters, sample-done bits, pattern-match controls, LBERT patterns, FIFO status, ASIC valid/ack/adapt status, and power-state status report plausible values during training and idle.
- Reserved-bit hygiene: register write traces or hardware debug logs show read-modify-write sequences preserving unrelated and reserved fields when setting any mask from this chunk.
