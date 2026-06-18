# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 50048-52421

## Scope

This chunk covers lines 50048-52421 of the generated AMD DPCS 4.2.0 shift/mask header. The range contains 2,132 `#define` constants across 243 register blocks: 1,065 `__SHIFT` macros and 1,067 `_MASK` macros. The two extra masks are expected for this sliced chunk because line 50048 starts in the middle of `DPCSSYS_CR2_LANE2_DIG_RX_ADPTCTL_ADPT_CFG_6`, where four `_MASK` definitions are present while their matching shifts were defined before the chunk boundary.

The content is declarative register metadata only. It defines bit positions and masks for DPCS CR2 lane 2, CR2 lane 3, and CR2 raw common registers. It contains no C functions, structs, enums, local storage, runtime branching, or software-owned persistence.

## Purpose

This header fragment provides symbolic bitfield definitions for AMDGPU display driver code that programs the DPCS 4.2.0 display PHY. Consumer code pairs these field macros with companion register-offset definitions and AMD display register helpers to build read-modify-write values without hard-coding literal bit positions.

The chunk is centered on three hardware surfaces:

- `DPCSSYS_CR2_LANE2_*`: lane 2 receive adaptation, RX statistics, MPHY/RX termination controls, digital analog override outputs, and lane 2 analog TX/RX control/status fields.
- `DPCSSYS_CR2_LANE3_*`: lane 3 ASIC-facing override/normal signal registers, TX power-control P-state and DCC controls, RX statistics, digital analog TX override/status fields, and analog TX controls.
- `DPCSSYS_CR2_RAWCMN_*`: CR2 common PHY reset, MPLLA/MPLLB override and spread-spectrum controls, common mode/RTUNE/HDMI/TX PWM clock overrides, MPLL state controls, calibration/status IDs, OCLA selection, support analog overrides, and always-on RTUNE readback values.

## Exported API Surface

There are no callable APIs or user-defined types. The public interface is the macro namespace itself. Each register field generally has:

- `REGISTER__FIELD__SHIFT`: starting bit for extracting or composing a field value.
- `REGISTER__FIELD_MASK`: bit mask for isolating the field in the corresponding memory-mapped register.

Important macro families in this range include:

- `DPCSSYS_CR2_LANE2_DIG_RX_ADPTCTL_*`: lane 2 RX adaptation configuration, reset, and status for ATT, VGA, CTLE boost/pole, DFE taps 1-5, DFE data/error VDAC offsets, even/odd slicer controls, error slicer level, adaptation reset, DAC control selection, and CR bank address/data windows.
- `DPCSSYS_CR2_LANE2_DIG_RX_STAT_*` and `DPCSSYS_CR2_LANE3_DIG_RX_STAT_*`: repeated RX statistics match/mask/control/counter blocks. These define pattern masks, pattern data, scope delay, symbol selectors, mask inversion, counter enables, saturation behavior, load values, sample counts, and statistic stop controls.
- `DPCSSYS_CR2_LANE2_DIG_ANA_*` and `DPCSSYS_CR2_LANE3_DIG_ANA_*`: digital-to-analog override/status surfaces for TX/RX controls, term-code overrides, EQ override outputs, RX VCO and power overrides, MPHY controls, signal-detect overrides, TX DCC DAC overrides, and analog status readbacks.
- `DPCSSYS_CR2_LANE2_ANA_TX_*`, `DPCSSYS_CR2_LANE2_ANA_RX_*`, and `DPCSSYS_CR2_LANE3_ANA_TX_*`: direct analog field maps for TX measurement, power override, alternate-bus controls, ATB measurement paths, DCC DAC/control, term code, override clocks, miscellaneous TX settings, and lane 2 RX clock/CDR/slicer/power/squelch/calibration/ATB/reserved fields.
- `DPCSSYS_CR2_LANE3_DIG_ASIC_*`: lane 3 ASIC-facing request/acknowledge, P-state, rate, width, MPLLB select, data-enable, main/pre/post cursor, HDMI mode, clock-ready, detect-RX, invert, low-power-detect, reset, loopback, AC JTAG, async-data, and override-enable fields.
- `DPCSSYS_CR2_LANE3_DIG_TX_PWRCTL_*`: lane 3 TX power-state programming for P0/P0S/P1/P2, TX power-up timing registers, DCC CR bank address/data, DCC DAC control/range/selection/ack/address, and TX clock alignment/LBERT controls.
- `DPCSSYS_CR2_RAWCMN_DIG_*`: common reset, MPLLA/MPLLB clock divider/bandwidth/SSC/frac-N overrides, lane FSM extension, initial calibration disable, RTUNE request override, HDMI mode override, TX PWM clock selection/enables, MPLL state/bank selection, TX calibration code, SRAM init done, OCLA probe selection, support analog overrides, PCS/FW ID code fields, and indexed AON common RTUNE RX/TXDN/TXUP readback fields.

## Register Areas Covered

The lane 2 RX adaptation block exposes the lower-level equalization and signal-sampling knobs that the display PHY uses during receive calibration. It covers VGA saturation thresholds/levels, DFE mu settings, initial error values, per-adaptation resets, live adaptation status codes, DFE tap status, even/odd data and error VDAC offsets, slicer controls, and adaptation reset. These fields are not algorithms by themselves; they are the bit contracts used by training, diagnostic, or low-level bring-up code to observe and influence the RX adaptation hardware.

The lane 2 and lane 3 RX statistic blocks provide programmable hardware counters and matchers. Register groups define data masks, pattern masks, pattern values, match control words, counter control, sample count, statistic counters 0-6, calibration comparison clock control, extra match controls, statistic control extensions, and stop bits. These are likely used for PHY diagnostics, calibration verification, and link-quality measurement rather than normal per-frame display traffic.

The lane 2 digital analog and analog RX/TX groups bridge digital control words to analog PHY behavior. They include TX/RX override output enables, transmitter term-code and EQ override controls, RX power/VCO/AFE/CTLE/scope/slicer/phase adjustment controls, analog status readback fields, MPHY override outputs, signal-detect overrides, TX DCC DAC overrides, direct analog TX power/ATB/DCC/term/misc controls, and direct lane 2 analog RX clock/CDR/slicer/power/squelch/calibration/ATB controls.

The lane 3 ASIC block describes the interface between higher-level ASIC link logic and the lane 3 PHY. It exposes both override input registers and normal ASIC input/output mirrors. The field pairs show a common pattern: value fields such as `REQ`, `PSTATE`, `RATE`, `WIDTH`, `DATA_EN`, `CLK_RDY`, `INVERT`, and `RESET` have adjacent `*_OVRD_EN` fields that gate whether the override value replaces the normal ASIC signal.

The lane 3 TX power-control block maps several power states and timing controls. P-state fields cover analog refgen, VCM hold, analog clock enable, power-down, high-Z, termination enable, DCC enable, output enable, serializer enable, divider controls, low-power DCC values, and reserved bits. Timing and DCC windows define power-up delays, DCC CR bank address/data access, DAC control/range/selection/ack/address, TX clock alignment, and LBERT controls.

The raw common block applies across the CR2 PHY rather than a single lane. It defines global PHY functional reset, MPLLA/MPLLB divider and bandwidth overrides, spread-spectrum and frac-N overrides, lane FSM extension, common override controls for MPLL initial calibration, RTUNE request, HDMI mode, TX PWM clock selection/enables, MPLL on/off state and bank selection, TX calibration code, SRAM init status, OCLA clock/probe selection, support analog overrides, firmware/PCS ID readbacks, and the beginning of indexed always-on RTUNE RX/TXDN/TXUP values.

## Control Flow And State Behavior

This file has no software control flow. Runtime behavior is created by driver code that uses these macros to access hardware registers.

The field names imply several hardware state machines and handshakes:

- RX adaptation sequencing: reset bits, status codes, `ASM1_DONE`/`ASM1_DON` flags, ATT/VGA/CTLE/DFE status fields, slicer levels, and VDAC offsets expose calibration progress and final tuned values.
- Statistics collection: load/start fields, sample counts, match masks/patterns, counter enables, saturation flags, stop controls, and statistic counters define a hardware measurement pipeline that must be configured, started, sampled, and stopped in a defined order by consumers.
- Lane request/ack and power state transitions: lane 3 `REQ`, `ACK`, `PSTATE`, `RATE`, `WIDTH`, `CLK_RDY`, `DATA_EN`, `DETECT_RX_REQ`, `DETRX_RESULT`, reset, disable, and power-state fields model PHY bring-up, link training, idle, and power-down transitions.
- Override gating: many fields have paired `*_OVRD_VAL`/`*_OVRD_EN` or value/`*_OVRD_EN` definitions. Software must enable override bits deliberately and usually restore hardware-owned control afterward.
- PLL/common clock control: MPLLA/MPLLB divider, bandwidth, SSC, frac-N, state, bank, and calibration-disable fields affect common clock generation shared by lanes.
- Analog measurement and calibration: ATB, DCC DAC, term code, RTUNE, VCO, support analog, OCLA, and TX calibration fields expose diagnostic and calibration state across analog and mixed-signal blocks.

No software persistence is implemented in this header. Hardware register contents persist or reset according to ASIC power, reset, and clock domains. Fields named `STATUS`, `ACK`, `DONE`, `VALID`, `ID_CODE`, `SRAM_INIT_DONE`, `RTUNE_*_VAL`, and statistic counters are readback/status-oriented; fields named `OVRD`, `RESET`, `PSTATE`, `DAC`, `TERM`, `DCC`, and `*_EN` are control-oriented. This distinction is semantic and must be enforced by consumer code and hardware documentation, not by the macros themselves.

## Dependencies And Integration Points

The only direct syntactic dependency is the C preprocessor. These definitions are meant to be included alongside DPCS 4.2.0 offset/address headers that provide the actual register locations. AMDGPU display code then uses common register helper macros to shift, mask, set, clear, or read the fields.

Integration points visible from naming:

- AMDGPU DRM display code under `drivers/gpu/drm/amd`, especially DC/DPCS link encoder, PHY, clock, link-training, and diagnostics code.
- Companion generated headers such as `dpcs_4_2_0_offset.h` or equivalent register-address maps for the same DPCS generation.
- DisplayPort and HDMI link paths, reflected by `RATE`, `WIDTH`, `PSTATE`, `HDMIMODE`, cursor/pre/post EQ, DETRX, data-enable, term-code, and MPLL fields.
- PHY diagnostics and validation paths that configure RX statistics, LBERT, OCLA, ATB, scope, slicer, DCC DAC, and RTUNE readbacks.
- Firmware or hardware-control paths that may own some lanes or common PLL state unless software explicitly enables override bits.

## Risks

- Generated-header drift is the main risk. A wrong shift or mask can silently write an adjacent hardware bit during a read-modify-write sequence, causing display link failures that may not be caught by compile tests.
- The chunk begins mid-register with masks for `DPCSSYS_CR2_LANE2_DIG_RX_ADPTCTL_ADPT_CFG_6`; naive per-chunk validators must account for the missing shifts being outside this range.
- Many lane 2 and lane 3 blocks are structurally similar but not identical. Copy-generation mistakes in lane prefixes, field widths, or mask values can affect only one lane and escape broad smoke tests.
- Override-enable fields are adjacent to override values. Accidentally setting an enable bit can seize a signal from normal hardware/firmware control; failing to set one can make a value write ineffective.
- Status/readback fields and writable control fields are intermixed. Consumers must not infer access direction from mask presence alone.
- Common MPLLA/MPLLB, RTUNE, reset, and HDMI/TX PWM clock fields can have cross-lane effects. A write intended for one lane's link mode can destabilize another lane if shared-resource ownership is misunderstood.
- Reserved fields have explicit masks throughout the chunk. Consumer code should preserve reserved bits unless the hardware specification explicitly requires a value.

## Test Signals

Useful validation is mostly build-time, generated-data, and hardware-integration oriented:

- Preprocess or compile AMDGPU display code that includes `dpcs_4_2_0_sh_mask.h`.
- Run generated-register consistency checks against the authoritative DPCS 4.2.0 register database and companion offset header.
- Verify this exact chunk has 1,065 shift macros and 1,067 mask macros, with the imbalance explained by the partial `ADPT_CFG_6` boundary.
- Check that every complete register block in the range has matching shift and mask entries for each field, including repeated `LANE2`, `LANE3`, `MPLLA`, `MPLLB`, and indexed RTUNE families.
- Compare compatible fields against nearby generated variants such as `dpcs_4_2_2_sh_mask.h` or `dpcs_4_2_3_sh_mask.h` where the hardware register database expects stable layouts.
- Runtime display tests on DPCS 4.2.0 ASICs: DP and HDMI link training, rate/width changes, suspend/resume, hotplug, lane power transitions, and multi-lane operation that exercises lane 2 and lane 3 independently.
- PHY diagnostic tests that read back RX adaptation status, DFE tap values, RX statistic counters, DETRX result, TX ack, SRAM init done, MPLL state, firmware ID, RTUNE values, and OCLA/ATB/DCC paths.
- Negative or recovery tests around override fields: enable an override only under controlled debug/bring-up code, restore normal ownership, and confirm no stale override remains across link reconfiguration.

## Chunk Notes For Merge

This document intentionally covers only lines 50048-52421 of `dpcs_4_2_0_sh_mask.h`. The later per-file merge should describe the full header as a generated DPCS 4.2.0 register bitfield map, not handwritten driver logic. Adjacent chunks are needed to cover the earlier part of lane 2 and the remaining raw common RTUNE fields after `DPCSSYS_CR2_RAWCMN_DIG_AON_CMN_RTUNE_TXDN_VAL_6`.
