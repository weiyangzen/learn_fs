# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 112526-115025

## Purpose

This chunk is generated AMD DCN 3.2.0 register field metadata. It contains no executable C logic; it publishes preprocessor constants for field shifts and masks in C20 PHY CR1 raw-lane always-on digital registers. The names describe low-level Display PHY lane control and status fields for TX and RX calibration, adaptation, signal detection, clock/data recovery, override, and debug support.

The requested range starts inside the tail of the `C20_PHY_CR1_RAWLANEAON1` TX MPLLB DCC bank definitions, then covers a large part of the `RAWLANEAON1` RX calibration/adaptation block, and then enters `C20_PHY_CR1_RAWLANEAON2`. For `RAWLANEAON2`, the range includes TX firmware/debug/state controls, TX DCC calibration banks for MPLLA/MPLLB, TX calibration-complete status, TX disable control, startup/continuous RX calibration controls, RX calibration result banks, and RX adaptation state through `RX_CDR_DETECTOR_CTL`. Adjacent chunks are required for the beginning of AON1 and the remainder of AON2.

Although the repository path is under a local `ceph-client` mirror, this header is AMDGPU display hardware metadata. It has no Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or callbacks in this range. The interface is the generated macro namespace:

- `<register>__<field>__SHIFT`: bit position for a field within the corresponding PHY register.
- `<register>__<field>_MASK`: bit mask for the same field.
- Register comments such as `//C20_PHY_CR1_RAWLANEAON1_DIG_RX_DCC_CTRL_RANGE_BANK_0` group the following field macros by hardware register.

Major register families in this chunk:

- TX DCC and calibration status: `TX_MPLLA_*`, `TX_MPLLB_*`, `TX_DCC_*`, `TX_CAL_DONE`, `TX_CAL_BANK_SEL`, and `TX_IN_0` define MPLL A/B duty-cycle-correction control ranges, full/half-rate common-mode and differential codes, per-bank completion bits, selected recalibration bank, and TX disable state.
- RX startup and continuous algorithm gates: `RX_STARTUP_CAL_ALGO_CTL_0/1`, `RX_STARTUP_ADAPT_ALGO_CTL_0`, and `RX_CONT_ALGO_CTL` expose skip bits for AFE, reference, attenuation, VGA, CTLE, IQ, phase, DFE, DCC, bypass/error, signal-detect, adaptation, figure-of-merit, and margining procedures.
- RX calibration offsets and limits: `RX_VGEN_VDAC_OFST`, `RX_SIGDET_CAL`, `RX_AFE_RTRIM`, `RX_REF_*`, `RX_DFE_*_VDAC_OFST`, `RX_SETUP_*_IDAC_OFST`, `RX_AFE_*_IDAC_OFST`, `RX_VDAC_RANGE_SEL`, `RX_IQ_CAL_DIVN`, `RX_CAL_IQ_MAX/MIN/RESET/ADJUST`, and `RX_IQ_CTL_*` describe analog trim, voltage/current DAC offset, IQ calibration, and slicer/reference tuning fields.
- RX DCC banked results: `RX_DCC_CTRL_RANGE_BANK_[0-3]`, `RX_DCC_FULL_*_BANK_[0-3]`, `RX_DCC_HALF_*_BANK_[0-3]`, `RX_IQ_CAL_BANK_[0-3]`, `RX_CAL_DONE_BANK_[0-3]`, and consolidated `RX_DCC_*_CODE` registers carry banked full/half-rate DCC results for data, bypass, and phase paths.
- RX adaptation state: `RX_ADPT_ATT/VGA/CTLE_BANK_[0-1]`, `RX_ADPT_DFE_TAP[1-5]_BANK_[0-1]`, DFE tap1 offset registers for data/error high/low and odd/even paths, `RX_ADPT_IQ_BANK_[0-1]`, `RX_ADPT_REF_ERR_BANK_[0-1]`, `RX_ADAPT_DONE_BANK_[0-1]`, and `RX_ADPT_CTL_0` through `RX_ADPT_CTL_28` define live or retained adaptation values and validity/done flags.
- Link/PHY support controls: `RX_TX_EQ_DIR_POLARITY_CTL`, `RX_TX_PRE_DIV`, `RX_TX_MAIN_*_THRESHOLD`, `RX_TX_POST_*_THRESHOLD`, `RX_IQ_MARGIN_RANGE`, `RX_CDR_DETECTOR_CTL`, `RX_CDR_RECOVERY_TIME`, `RX_OVRD_IN_0`, `RX_SIGDET_*`, `RX_OVRD_OUT_0`, `RX_PMA_OVRD_OUT_0`, `RX_IN_0`, and `RX_OUT_0` define equalization direction polarity, thresholding, margin bounds, CDR detector mode, receiver override knobs, signal-detect filters, PMA override outputs, and receiver status.
- AON2-only TX firmware/debug controls visible near the middle of the chunk: `TX_FW_STATES_*`, `TX_MEM_BREAKPOINT_2`, `TX_SRAM_REC_*`, `TX_CCA_*`, `TX_STARTUP_ALGO_CTL_0`, `TX_CONT_ALGO_CTL_0`, `TX_FAST_FLAGS_0`, `TX_TX_HP_PROT_EN_*`, `TX_LANE_XCVR_MODE_*`, `TX_INIT_PWRUP_DONE`, and `TX_OVRD_IN_0`.

Most visible registers are 16-bit PHY-side fields rather than the 32-bit DCN display-pipe fields seen elsewhere in the file. Many fields are paired low/high nibbles or bytes, for example 4-bit DCC control ranges, 8-bit common-mode/differential DCC codes, 12-bit DFE tap values, and single-bit valid/done/disable/override flags.

## Control Flow

This header has no runtime control flow. Runtime sequencing is imposed by the display driver, firmware, or PHY access helpers that include `dcn_3_2_0_sh_mask.h` together with `dcn_3_2_0_offset.h`.

Typical use is:

1. A register table or indirect PHY access path identifies a C20 PHY CR1 raw-lane register, usually using the matching `ixC20_PHY_*` offset macro from `dcn_3_2_0_offset.h`.
2. Register helper macros use the `__SHIFT` and `_MASK` constants to compose, update, or decode fields without hand-coded bit arithmetic.
3. Link bring-up, link-rate changes, lane training, calibration, debug, or validation code programs skip/override/control fields, waits for calibration/adaptation done bits, and reads result/status fields.

The macros do not encode ordering constraints. Consumers still need to sequence PHY power, PLL state, lane mode, TX/RX disable, startup calibration, continuous adaptation, bank selection, CDR enablement, and signal-detect handling according to the hardware programming guide.

## State And Persistence Behavior

This chunk stores no software state and persists nothing in memory or on disk. It describes MMIO or indirect-register-backed PHY state.

The represented hardware state includes:

- Per-bank TX and RX DCC calibration results for full-rate and half-rate operation.
- Per-bank calibration and adaptation completion bits.
- Selected recalibration banks for TX and RX.
- Startup and continuous calibration/adaptation skip policy.
- Receiver analog trims and offsets for reference, AFE, CTLE, VGA, DFE, IQ, data, phase, bypass, error, and slicer paths.
- RX adaptation results for attenuation, VGA, CTLE, DFE taps, IQ, and reference error.
- TX firmware/debug state for AON2, including SRAM recovery and breakpoint controls.
- Override inputs and observable outputs for receiver disable, termination, signal detect, VREF generator, PMA state, and TX disable.
- CDR detector enable and mode bits, signal-detect filter settings, and RX/TX equalization threshold controls.

Persistence is hardware-defined. Calibration and adaptation results may remain valid until a PHY reset, lane power transition, link-rate change, retraining event, suspend/resume cycle, or explicit recalibration. Done/status fields may be read-only, sticky, self-clearing, banked, or firmware-owned. Override and skip fields are especially sequencing-sensitive because they can bypass normal PHY firmware algorithms or force analog state.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.2.0 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`, which provides the matching `ixC20_PHY_*` register offsets for C20 PHY indirect accesses.
- The surrounding generated portions of `dcn_3_2_0_sh_mask.h`, because this range starts and ends inside repeated C20 PHY lane families.
- DCN register helper macros that consume generated shift/mask names through token pasting or direct register-field definitions.

Observed direct include sites for the DCN 3.2.0 offset and mask headers in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`

The exact `C20_PHY_CR1_RAWLANEAON*` names are generated hardware symbols and are not ordinary C APIs. Direct textual references outside generated register headers may be sparse because PHY programming can be routed through firmware tables, indirect register helpers, or generated token-paste macros rather than handwritten references to every field.

## Risks And Edge Cases

- Shift or mask drift is the core risk. These are untyped constants; a wrong bit position or mask can compile while corrupting a neighboring analog PHY field.
- The register families are heavily repeated across lanes, AON instances, banks, MPLLA/MPLLB, and full/half-rate variants. Copy-generation errors may affect only one lane, one bank, one PLL selection, or one link rate.
- The chunk boundaries are artificial. The first lines are only the end of an AON1 MPLLB DCC bank, and the final line stops at AON2 `RX_CDR_DETECTOR_CTL` before the rest of that register and later RX override/status fields.
- Calibration skip and override fields are high risk. Forcing or skipping AFE, DFE, IQ, DCC, CDR, signal-detect, or termination behavior can produce failures that only appear during link training, retraining, low-power exit, marginal cables, or high bit rates.
- Banked calibration fields require consistent bank selection and validity checks. Reading a stale bank or writing a full-rate value into a half-rate field can create intermittent link instability.
- Status and done fields may be firmware-owned or timing-sensitive. Polling the wrong bit, assuming a sticky bit is live, or clearing/overriding a bit too early can cause false training success or timeout loops.
- Reserved masks are present throughout the range. Consumers must avoid writing reserved bits unless the hardware specification explicitly requires preserved values.
- These low-level PHY fields can have board-, connector-, and lane-dependent effects. A bad mask may pass basic display bring-up but fail on multi-lane DisplayPort, USB-C retimer paths, spread-spectrum clocks, suspend/resume, hotplug, or high-bandwidth modes.

## Test Signals

Useful validation combines generated-header consistency checks with hardware display coverage:

- Build AMDGPU/DC with DCN 3.2 support enabled; missing or renamed field macros should fail where generated register tables or direct helpers reference them.
- Mechanically verify that every `__SHIFT` macro in lines 112526-115025 has a matching `_MASK` macro for the same register field, except where the generated chunk boundary cuts a pair.
- Compare this range against AMD's authoritative DCN 3.2.0 register database and against adjacent repeated families for CR0/CR1/CR2 and AON0/AON1/AON2 where identical lane blocks are expected.
- Exercise DisplayPort and USB-C/DP-alt-mode link training across supported lane counts and link rates, including retraining, hotplug, suspend/resume, low-power exit, and high-bandwidth modes.
- Validate scenarios likely to touch DCC and CDR behavior: full-rate versus half-rate operation, spread-spectrum clocks, marginal cables, retimers, high refresh rates, and link-rate changes without a full reboot.
- Watch kernel logs and display diagnostics for AUX/link-training timeouts, CDR lock failures, signal-detect instability, blank displays, intermittent flicker, CRC errors, underflow, PHY firmware timeout messages, or resume-only failures.
- For debug or lab validation, read back done/valid/status fields around calibration and adaptation sequences to confirm the selected bank, valid flags, DFE/IQ adaptation values, CDR detector mode, and signal-detect outputs align with expected hardware behavior.

## Cross-Chunk Notes

Previous chunks are needed for the beginning of `C20_PHY_CR1_RAWLANEAON1` and its earlier TX definitions. Later chunks continue `C20_PHY_CR1_RAWLANEAON2` after `RX_CDR_DETECTOR_CTL` and then proceed through additional repeated C20 PHY raw-lane definitions. The final per-file research document should merge adjacent chunks before making complete claims about all DCN 3.2.0 PHY lane registers or all C20 PHY CR instances.
