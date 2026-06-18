# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 212184-214673

## Scope

This chunk is a generated AMD DCN 3.2.0 shift/mask header slice. It contains preprocessor constants only: register-group comments, `_SHIFT` macros for field bit positions, and `_MASK` macros for register-positioned bit masks. There are no C functions, structs, enums, branches, loops, allocations, locks, or software persistence logic in this range.

The requested range covers 2,490 source lines, 2,071 `#define` lines, and 419 register-group comments. It starts inside `C20_PHY_CR4_RAWLANEAON1_DIG_TX_INIT_PWRUP_DONE`, where the first field shift is owned by the previous chunk, then covers the remainder of the RAWLANEAON1 TX calibration/readback block, a large RAWLANEAON1 RX calibration/adaptation block, and the beginning-to-middle of the parallel RAWLANEAON2 block. It ends inside `C20_PHY_CR4_RAWLANEAON2_DIG_RX_TX_EQ_DIR_POLARITY_CTL`; the remaining shifts and masks for that register are in the next chunk.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU Display Core hardware metadata for DCN/DPCS PHY programming, not Ceph filesystem code.

## Purpose

The purpose of this header range is to describe bit layouts for C20 PHY CR4 RAWLANEAON registers used by AMD display driver code on DCN 3.2.0-era hardware. The matching offset header supplies register addresses; this file supplies field positions and masks so generated register tables and helper macros can pack MMIO writes, decode MMIO reads, and preserve unrelated bits during read/modify/write operations.

The hardware surfaces represented here are:

- RAWLANEAON1 TX initialization, software disable override, MPLLA/MPLLB DCC calibration banks, calibration completion readbacks, selected TX DCC code readbacks, calibration-bank selection, and TX input status.
- RAWLANEAON1 RX startup calibration algorithm controls, startup/adaptation algorithm controls, continuous adaptation controls, fast flags, VDAC/IDAC offsets, signal-detect calibration, AFE trims, DCC bank values, IQ calibration values, calibration completion, adaptation readbacks, TX-equalization helper thresholds, RX adaptation control placeholders, CDR detector/recovery controls, RX override inputs/outputs, PMA override outputs, and RX input/output status.
- RAWLANEAON2 TX firmware-state, memory-breakpoint, SRAM-recorder, CCA/startup/continuous algorithm, fast-flag, protection, lane-mode, init-power, override, DCC calibration, and TX input status fields.
- RAWLANEAON2 RX startup calibration/adaptation controls and the same early RX VDAC/IDAC, DCC, IQ, calibration, adaptation, DFE-offset, reference-error, and adaptation-done readback families that appear earlier for RAWLANEAON1.

These macros are generated data rather than executable logic, but they form an ABI between AMDGPU display code, generated register tables, firmware-facing logic, and the PHY hardware. A wrong shift or mask can compile cleanly while causing PHY link training, calibration, equalization, power-up, or diagnostic paths to read or write the wrong hardware bits.

## Important APIs, Types, And Macros

This chunk exports the standard AMD generated register-field naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in register-positioned form.
- `//<REGISTER>` comments group the following definitions by hardware register.

There are no callable APIs or C data types in this chunk. Runtime code consumes these symbols through AMD display register-list and mask/shift-list infrastructure, normally together with offsets from `dcn_3_2_0_offset.h`.

Important macro families in this range include:

- `C20_PHY_CR4_RAWLANEAON1_DIG_TX_INIT_PWRUP_DONE`, `TX_OVRD_IN_0`, `TX_MPLLA_*`, `TX_MPLLB_*`, `TX_CAL_DONE*`, `TX_DCC_*`, `TX_CAL_BANK_SEL`, and `TX_IN_0`.
- `C20_PHY_CR4_RAWLANEAON1_DIG_RX_STARTUP_CAL_ALGO_CTL_*`, `RX_STARTUP_ADAPT_ALGO_CTL_0`, `RX_CONT_ALGO_CTL`, `RX_FAST_FLAGS`, and many RX calibration offset registers.
- `C20_PHY_CR4_RAWLANEAON1_DIG_RX_DCC_*_BANK_[0-3]`, `RX_IQ_CAL_BANK_[0-3]`, `RX_CAL_DONE_BANK_[0-3]`, selected aggregate DCC/IQ/calibration readbacks, and `RX_CAL_BANK_SEL`.
- `C20_PHY_CR4_RAWLANEAON1_DIG_RX_ADPT_*_BANK_[0-1]`, `RX_DFE_*_TAP1_OFST_BANK_[0-1]`, `RX_ADPT_REF_ERR_BANK_[0-1]`, and `RX_ADAPT_DONE_BANK_[0-1]`.
- `C20_PHY_CR4_RAWLANEAON1_DIG_RX_TX_*`, `RX_ADPT_CTL_[0-28]`, `RX_CDR_*`, `RX_OVRD_*`, `RX_PMA_OVRD_OUT_0`, `RX_IN_0`, and `RX_OUT_0`.
- `C20_PHY_CR4_RAWLANEAON2_DIG_TX_FW_STATES_*`, `TX_MEM_BREAKPOINT_2`, `TX_SRAM_REC_*`, `TX_CCA_*`, `TX_STARTUP_ALGO_CTL_0`, `TX_CONT_ALGO_CTL_0`, `TX_FAST_FLAGS_0`, `TX_TX_HP_PROT_EN_*`, `TX_LANE_XCVR_MODE_*`, and the RAWLANEAON2 TX DCC/calibration families.
- `C20_PHY_CR4_RAWLANEAON2_DIG_RX_STARTUP_CAL_ALGO_CTL_*`, `RX_STARTUP_ADAPT_ALGO_CTL_0`, `RX_CONT_ALGO_CTL`, `RX_FAST_FLAGS`, RX offset/calibration/DCC/IQ/readback families, and the beginning of `RX_TX_EQ_DIR_POLARITY_CTL`.

## RAWLANEAON1 TX Calibration And Status

The first visible lines are the tail of `C20_PHY_CR4_RAWLANEAON1_DIG_TX_INIT_PWRUP_DONE`: the chunk includes the reserved shift and both masks, while the `INIT_PWRUP_DONE__SHIFT` is in the previous chunk. `TX_OVRD_IN_0` then provides a software disable value plus its override-enable bit, with the rest of the 16-bit register reserved.

The TX DCC calibration block is organized by PLL and bank:

- `TX_MPLLA_DCC_CTRL_RANGE_BANK_0` through `BANK_3` and `TX_MPLLB_DCC_CTRL_RANGE_BANK_0` through `BANK_3` expose 4-bit `FULL_VAL` and 4-bit `HALF_VAL` range values.
- `TX_MPLLA_DCC_FULL_BANK_*`, `TX_MPLLA_DCC_HALF_BANK_*`, `TX_MPLLB_DCC_FULL_BANK_*`, and `TX_MPLLB_DCC_HALF_BANK_*` split calibration values into 8-bit common-mode and 8-bit differential fields.
- `TX_MPLLA_CAL_DONE_BANK_*` and `TX_MPLLB_CAL_DONE_BANK_*` expose `CAL_FULL_DONE` and `CAL_HALF_DONE` status bits per bank.
- Aggregate `TX_MPLLA_CAL_DONE`, `TX_MPLLB_CAL_DONE`, and `TX_CAL_DONE` registers collapse bank/full/half completion state into packed bit fields for faster readback.
- `TX_DCC_CTRL_RANGE_CODE`, `TX_DCC_CODE`, `TX_DCC_DIFF_CODE`, and `TX_DCC_CM_CODE` expose selected or consolidated DCC code readbacks.
- `TX_CAL_BANK_SEL` selects which calibration bank is active for relevant readback/programming paths.
- `TX_IN_0` exposes a TX input status/control bit named `TX_DISABLE`.

These definitions support TX duty-cycle-correction calibration around both MPLLA and MPLLB. The macros themselves do not say which PLL is active, when banks are selected, or whether completion bits are sticky or volatile; the link/PHY sequencing code and hardware documentation supply those rules.

## RAWLANEAON1 RX Startup, Calibration, And Offsets

The RAWLANEAON1 RX section starts with startup calibration and adaptation algorithm controls. `RX_STARTUP_CAL_ALGO_CTL_0` and `_1` contain enables for many startup calibration substeps, including VGEN, signal-detect, AFE, reference, DFE, IQ, DCC data/bypass/phase, and related one-time setup. `RX_STARTUP_ADAPT_ALGO_CTL_0` similarly enables startup adaptation behaviors for ATT, VGA, CTLE, DFE taps, IQ, reference error, and adaptation-done paths. `RX_CONT_ALGO_CTL` selects continuous adaptation behavior after startup, and `RX_FAST_FLAGS` exposes compact enable flags for fast/shortcut behavior around DFE, EQ, CDR, DCC, and calibration paths.

The next register families define calibration offsets and analog front-end trimming values:

- `RX_VGEN_VDAC_OFST`, `RX_SIGDET_CAL`, `RX_AFE_RTRIM`, `RX_REF_VDAC_OFST`, `RX_REF_EXT_VDAC_OFST`, `RX_REF_EE_VDAC_OFST`, and `RX_REF_EO_VDAC_OFST`.
- `RX_DFE_EE_VDAC_OFST`, `RX_DFE_EO_VDAC_OFST`, phase/data/bypass/error VDAC offsets for even/odd and high/low slicer paths, and setup offsets for CTLE/VGA/slicer IDAC paths.
- `RX_VDAC_RANGE_SEL`, `RX_AFE_ATT_IDAC_OFST`, `RX_AFE_CTLE_IDAC_OFST_BANK_0` through `BANK_3`, `RX_AFE_VGA1_IDAC_OFST`, and `RX_AFE_BUF_IDAC_OFST`.
- IQ calibration controls and limits through `RX_IQ_CAL_DIVN`, `RX_CAL_IQ_MAX`, `RX_CAL_IQ_MIN`, `RX_CAL_IQ_RESET`, and `RX_CAL_IQ_ADJUST`.

These constants are used to pack and decode analog calibration trims. They are hardware-state descriptions, not policy: valid signedness, scaling, calibration timing, and safe update windows are not encoded in the macro names.

## RAWLANEAON1 RX DCC, IQ, And Adaptation Readbacks

The RX DCC families are repeated across banks 0 through 3. Each bank has:

- `RX_DCC_CTRL_RANGE_BANK_N` with full/half range values.
- `RX_DCC_FULL_DATA_BANK_N`, `RX_DCC_FULL_BYP_BANK_N`, and `RX_DCC_FULL_PHASE_BANK_N` with common-mode and differential values.
- `RX_DCC_HALF_DATA_BANK_N`, `RX_DCC_HALF_BYP_BANK_N`, and `RX_DCC_HALF_PHASE_BANK_N` with common-mode and differential values.
- `RX_IQ_CAL_BANK_N` with IQ calibration value and valid bit.
- `RX_CAL_DONE_BANK_N` with completion flags for data, bypass, phase, and IQ calibration.

Aggregate registers then expose `RX_CAL_BANK_SEL`, range/code readbacks for DCC data/bypass/phase, split differential/common-mode readbacks for those DCC categories, `RX_IQ_CAL`, and `RX_CAL_DONE`. `RX_IQ_CTL_0`, `RX_IQ_CTL_1`, `RX_ADPT_IQ_LIMIT`, and `RX_ADPT_ERR_SLC_MODE` provide IQ and adaptation-control metadata around those calibration results.

The adaptation readback groups cover banked equalization state:

- `RX_ADPT_ATT_BANK_[0-1]`, `RX_ADPT_VGA_BANK_[0-1]`, and `RX_ADPT_CTLE_BANK_[0-1]`.
- `RX_ADPT_DFE_TAP1_BANK_[0-1]` through `RX_ADPT_DFE_TAP5_BANK_[0-1]`.
- DFE tap1 offset readbacks for data/error, even/odd, high/low paths: `RX_DFE_DEH_TAP1_OFST_BANK_*`, `RX_DFE_DEL_*`, `RX_DFE_DOH_*`, `RX_DFE_DOL_*`, `RX_DFE_EEH_*`, `RX_DFE_EEL_*`, `RX_DFE_EOH_*`, and `RX_DFE_EOL_*`.
- `RX_DFE_TAP1_OFST_VLD_BANK_*`, `RX_ADPT_IQ_BANK_*`, `RX_ADPT_REF_ERR_BANK_*`, and `RX_ADAPT_DONE_BANK_*`.

These fields are volatile or calibration-latched depending on the hardware sub-block. Driver code should treat them as PHY readback/state surfaces, not ordinary software variables.

## RAWLANEAON1 RX Equalization, Override, And I/O Status

The RAWLANEAON1 tail section connects adaptation results to TX-equivalent equalization helper controls and low-level RX override/status paths:

- `RX_TX_EQ_DIR_POLARITY_CTL`, `RX_TX_PRE_DIV`, `RX_TX_MAIN_ATT_THRESHOLD`, `RX_TX_MAIN_VGA_THRESHOLD`, `RX_TX_POST_BOOST_THRESHOLD`, and `RX_TX_POST_TAP1_THRESHOLD` define threshold/divider/polarity metadata used when RX-derived adaptation information is translated into TX equalization-related controls.
- `RX_ADPT_CTL_0` through `RX_ADPT_CTL_28` are full-register reserved placeholders in this generated range. They still matter for generated layout parity even though no named fields are exposed here.
- `RX_IQ_MARGIN_RANGE`, `RX_CDR_DETECTOR_CTL`, and `RX_CDR_RECOVERY_TIME` describe IQ margin and CDR detector/recovery timing fields.
- `RX_OVRD_IN_0` contains RX override value/enable pairs for power, DFE, adaptation, calibration run controls, sampler selects, CDR controls, VCO divider, signal-detect enable, and similar low-level controls.
- `RX_SIGDET_EN_MASK_CTL` and `RX_SIGDET_FILT_CTL` define signal-detect masking and filtering fields.
- `RX_OVRD_OUT_0` exposes overrideable readback/status values such as power acknowledgement, signal detect, RX valid, calibration status, and adaptation-done status.
- `RX_PMA_OVRD_OUT_0` exposes PMA-facing override outputs and corresponding override-enable bits.
- `RX_IN_0` and `RX_OUT_0` expose compact non-override RX input and output status, including power-state, calibration run, adaptation, DFE, RX valid, signal detect, and status acknowledgement fields.

The override sections are value/enable based. Setting a value without the matching enable bit has no effect; leaving an enable bit asserted can mask the normal ASIC/PMA path and make link training or recovery behave as if the hardware state were different from reality.

## RAWLANEAON2 TX And RX Beginning

The chunk then repeats the same style for `C20_PHY_CR4_RAWLANEAON2_DIG_*`, beginning with TX firmware and diagnostic controls:

- `TX_FW_STATES_0` and `_1` expose packed firmware-state fields.
- `TX_MEM_BREAKPOINT_2` and `TX_SRAM_REC_*` define breakpoint and SRAM-recorder controls, including enable, base/current address, max iteration, current iteration, hold, and stop-on-full behavior.
- `TX_CCA_START_LOOP_CNT`, `TX_CCA_WAIT_CNT`, `TX_STARTUP_ALGO_CTL_0`, `TX_CONT_ALGO_CTL_0`, and `TX_FAST_FLAGS_0` provide TX algorithm and fast-flag controls.
- `TX_TX_HP_PROT_EN_OVRD_IN`, `TX_TX_HP_PROT_EN_IN`, `TX_LANE_XCVR_MODE_OVRD_IN`, and `TX_LANE_XCVR_MODE_IN` expose high-power protection and lane transceiver-mode value/override fields.
- `TX_INIT_PWRUP_DONE`, `TX_OVRD_IN_0`, the MPLLA/MPLLB DCC bank families, TX calibration completion/readback families, `TX_CAL_BANK_SEL`, and `TX_IN_0` mirror the RAWLANEAON1 TX structure.

RAWLANEAON2 RX then mirrors the early RAWLANEAON1 RX structure. It includes startup calibration/adaptation controls, continuous algorithm control, fast flags, VDAC/IDAC offsets, signal-detect calibration, AFE trims, DCC banked full/half data/bypass/phase values, IQ bank values, calibration completion, aggregate DCC/IQ/calibration readbacks, IQ/adaptation controls, and adaptation readbacks for banks 0 and 1. The chunk ends after the first two shifts of `RX_TX_EQ_DIR_POLARITY_CTL`; the remaining fields and masks for that register are in the next chunk.

## Control Flow

There is no executable control flow in this header. Runtime flow is supplied by AMDGPU display code that includes this generated mask file, includes the matching generated offset file, and expands register helper macros or generated register-table macros.

Typical runtime usage is:

1. DCN 3.2 display, link, DMUB, clock, GPIO, IRQ, or resource code selects a hardware block/lane/register offset.
2. Generated tables or helper macros bind the offset to one or more `_SHIFT` and `_MASK` symbols from this file.
3. Register helpers perform packed writes, read/modify/write updates, status reads, polling loops, or diagnostic readbacks using those shift/mask pairs.
4. PHY hardware latches calibration, override, power, DCC, IQ, adaptation, firmware-state, or status fields and reports results through the corresponding readback registers.

This file does not encode reset values, valid enumerations, volatile semantics, write-one-to-clear behavior, side effects, required delays, or ordering rules between reset, power, PLL, DCC, IQ, CDR, DFE, CTLE, VGA, signal-detect, and adaptation fields.

## State And Persistence Behavior

No software state is stored by this file. It describes MMIO-backed hardware state whose lifetime is governed by GPU reset, display link initialization, link training, modesets, hotplug handling, suspend/resume, runtime power management, PHY calibration, firmware/DMUB interactions, and diagnostics.

Persistent or latched hardware configuration fields in this chunk include TX/RX override enables and values, TX disable and lane-mode controls, MPLLA/MPLLB DCC calibration banks, calibration-bank selection, startup and continuous algorithm enables, VDAC/IDAC offsets, AFE trims, IQ calibration controls, signal-detect filter/mask controls, CDR detector/recovery controls, SRAM-recorder settings, and TX firmware/CCA algorithm controls.

Volatile or readback-oriented fields include init-power-done, DCC full/half calibration results, calibration-done flags, aggregate DCC/IQ code readbacks, adaptation ATT/VGA/CTLE/DFE tap values, DFE offset-valid bits, reference-error values, adaptation-done flags, RX/TX input and output status, PMA override outputs, fast flags, firmware-state readbacks, and SRAM-recorder progress.

Side-effecting or sequencing-sensitive fields include override enables, calibration-run controls, bank selectors, reset/power/disable-style fields, signal-detect masking, CDR recovery timing, SRAM recorder enable/hold/stop controls, and algorithm-enable bits. Treating these as static configuration bits can leave a lane in a diagnostic or forced state, hide normal hardware inputs, or corrupt calibration sequencing.

## Dependencies And Integration Points

This chunk depends on the matching generated DCN 3.2.0 offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`

The offset and mask headers must be generated from the same hardware register database. Structurally related generated PHY content also appears in the DPCS generated headers, especially:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h`

Local consumers of the DCN 3.2.0 generated register set include AMD display resource, DMUB, IRQ, GPIO, and clock code under:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`

Practical integration points include display PHY bring-up, link training, TX/RX calibration, DCC/IQ calibration diagnostics, RX adaptation and equalization readback, CDR/signal-detect handling, firmware-state/DMUB diagnostics, runtime power transitions, suspend/resume restoration, and hardware register dump decoding.

## Risks And Edge Cases

- The chunk starts and ends inside register definitions. `TX_INIT_PWRUP_DONE` is partial at the beginning, and `RX_TX_EQ_DIR_POLARITY_CTL` is partial at the end. Adjacent chunks are required for complete register-family analysis.
- Generated-header drift from the authoritative DCN 3.2.0 register database is the primary risk. Wrong numeric shifts or masks usually compile but produce hardware failures.
- RAWLANEAON1 and RAWLANEAON2 content is highly repetitive. Copying a symbol with the wrong RAWLANEAON prefix can silently target the wrong lane/always-on block.
- TX and RX DCC banks use similar field names with different data/bypass/phase or MPLLA/MPLLB semantics. Text-based refactors must not collapse them by partial name matching.
- Override registers use value/enable pairs. Incorrect pairing can make writes ineffective or leave normal hardware/ASIC/PMA signals masked by stale forced values.
- Calibration and adaptation readbacks are sequencing-sensitive and often volatile. Mis-decoded `CAL_DONE`, `ADAPT_DONE`, DCC, IQ, DFE, CTLE, VGA, ATT, or reference-error fields can create false pass/fail decisions during link training or diagnostics.
- Bank selectors and banked readback registers must stay aligned. Selecting one bank while decoding another can make calibration data appear inconsistent.
- Reserved full-word placeholders such as `RX_ADPT_CTL_0` through `RX_ADPT_CTL_28` should not be removed merely because they expose no named fields; they preserve generated register layout.
- SRAM-recorder and firmware-state fields are diagnostic/state-machine surfaces. Accidental writes to enable/hold/stop controls could perturb firmware-assisted PHY debugging.
- This file contains only masks and shifts. It does not protect callers from invalid values, wrong write order, missing polling delays, or writes to read-only/status fields.

## Test Signals

Useful validation signals for this chunk include:

- Build AMDGPU Display Core with DCN 3.2.0 support enabled. Missing or malformed symbols should fail where generated register tables or helpers expand.
- Mechanically compare lines 212184-214673 against a regenerated `dcn_3_2_0_sh_mask.h` or the authoritative DCN 3.2.0 register database, accounting for the partial first and last registers.
- Run generated-header consistency checks: each field should have a matching `_SHIFT` and `_MASK` within complete registers, masks should match stated shift/width, fields should not unexpectedly overlap, and reserved masks should cover unused bits.
- Cross-check repeated RAWLANEAON1 and RAWLANEAON2 register layouts for expected parity and intentional differences.
- Exercise link training across supported rates and widths while checking TX disable, init-power-done, DCC calibration completion, RX signal detect, RX valid, adaptation-done, and calibration status readbacks.
- Validate DCC and IQ calibration diagnostics by reading banked full/half values, bank selectors, aggregate codes, and calibration-done fields.
- Validate RX adaptation diagnostics by observing ATT, VGA, CTLE, DFE tap values, DFE tap1 offsets, reference-error fields, IQ values, and adaptation-done flags.
- Test suspend/resume and runtime power transitions with register dumps around override enables, startup/continuous algorithm controls, calibration offsets, CDR controls, and RX/TX status.
- Exercise controlled override-only paths, then verify that clearing override-enable bits restores normal ASIC/PMA behavior.
- Compare hardware register dumps before and after link training, hotplug, power transitions, and diagnostics to confirm packed writes affect only intended bits and status decoding matches observed hardware behavior.

## Cross-Chunk Notes

The previous chunk owns the first shift for `C20_PHY_CR4_RAWLANEAON1_DIG_TX_INIT_PWRUP_DONE`; this chunk owns its reserved shift and masks. The next chunk owns the remainder of `C20_PHY_CR4_RAWLANEAON2_DIG_RX_TX_EQ_DIR_POLARITY_CTL` plus subsequent RAWLANEAON2 RX threshold/adaptation/override fields. The final merged file-level report should reconcile those boundaries and treat this chunk as one part of the larger generated DCN 3.2.0 PHY register description.
