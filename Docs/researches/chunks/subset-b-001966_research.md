# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 90770-93178

## Chunk Scope

This chunk is a generated AMD DCN 3.2.0 ASIC register shift/mask header segment. It contains preprocessor constants only: `#define` pairs for hardware bitfield offsets (`__SHIFT`) and masks (`_MASK`), plus generated `//REGISTER_NAME` grouping comments. There are no C functions, structs, enums, global variables, allocation paths, locks, or executable branches in the selected lines.

The requested range contains 2,409 source lines with 2,166 macro definitions: 1,087 shift constants and 1,081 mask constants, organized under 243 register comments. The range starts in the tail of `C20_PHY_CR1_SUP_DIG_MPLLA_SSC_SSC_RAMP`, covers CR1 super/common and lane0 PHY programming fields, and ends mid-register at `C20_PHY_CR1_LANE0_DIG_ANA_XF_TX_STAT_OUT_0__TX_ANA_VCM_HOLD_MASK`; the remaining masks for that register begin on the following source lines outside this chunk. Although this file is under a mirrored `ceph-client` tree, this content is AMDGPU display-driver ASIC metadata, not distributed filesystem logic.

## Purpose

The purpose of this header region is to publish symbolic bit layouts for DCN 3.2 C20 PHY CR1 registers. Runtime AMD display code uses the matching offset header plus these shift/mask names to compose read/modify/write operations through generated register tables and helper macros such as `FD_SHIFT`, `FD_MASK`, `SF`, `REG_SET`, `REG_UPDATE`, and `REG_GET`.

At the hardware level, this chunk describes fields for:

- Super-digital MPLL spread-spectrum, power-control, calibration, lock/status, output timing, and analog crossover controls for MPLLA and especially MPLLB.
- CR1 common/raw-common controls, clock gates, context-restore selection, context images for supervisor/MPLLA/MPLLB programming, AON SRAM/power-gating/supervisor controls, recalibration bank selection, RTUNE values, metadata location, and firmware/raw version reporting.
- Lane0 ASIC-facing override and status fields for TX control, power states, reset, lane muxing, USB/DisplayPort-related symbols, reference clocks, SSC, CDR/regulator controls, and miscellaneous PHY inputs.
- Lane0 TX power, DCC, status counters, clock-alignment, LBERT pattern/test controls, level-calculation status, FIFO controls, and analog TX override/status fields.

The macros do not define semantic values or sequencing by themselves. They give bit positions and masks that other DCN 3.2 code must apply to the correct C20 PHY indirect register addresses.

## Important Macro Groups

### MPLL And Spread-Spectrum Fields

The chunk opens with MPLLA spread-spectrum ramp/config fields and then moves into a complete set of MPLLB UPLL/MPLL power-control and spread-spectrum fields. Important fields include `MPLL_CAL_OVRD_VAL`, `MPLL_CAL_OVRD_EN`, `MAX_RANGE`, `OVRD_SEL`, `MPLL_FBDIGCLK_EN`, `MPLL_PCLK_EN`, `FAST_MPLL_PWRUP`, `FAST_MPLL_LOCK`, `DTB_SEL`, `FSM_STATE`, `MPLL_LOCK`, lane synchronization status, power-up/down timing fields, analog DAC status, `FRAC_OUT_OVRD_VAL`, `SSC_RAMP_OVRD_VAL`, `BYPASS_MPLL_LOGIC`, and `SSC_FRAC_CLK_SEL`.

These constants are part of link-clock generation and spread-spectrum handling. Incorrect masks here can affect MPLL calibration, lock detection, output enablement, clock stability, and EMI-related SSC behavior.

### Super-Digital Analog Crossover And Override Fields

The `C20_PHY_CR1_SUP_DIG_ANA_XF_*` family defines status and override fields that bridge digital control logic to analog bandgap, reference, supervisor, MPLLA, MPLLB, PMIX, RTUNE, and CREG state. Visible fields include analog enable/reset bits, VREF/reference/regulator selections, term controls, MPLLA/MPLLB output enablement, PLL dividers, PMIX enables, tune overrides, calibration force/standby, async reset, and raw analog CREG payload/override fields.

Most override registers follow a repeated value-plus-override-enable pattern, for example `*_OVRD_EN`, `*_OVRD_VAL`, `*_ANA_*`, `*_PMIX_*`, and `*_TUNE_*` fields. This pattern matters because setting only the value bit without the corresponding override-enable bit may have no hardware effect, while setting override-enable bits out of sequence can bypass normal PHY firmware/control-state behavior.

### RAWCMN Common, Context, And AON Fields

The `C20_PHY_CR1_RAWCMN_DIG_*` family provides common control and always-on state for CR1. It includes global/common enable and clock-gate controls, MPLL configuration, ATE ALU debug/control registers, MPLL input selectors, firmware power-up/config/status bits, static configuration status, async override/recalibration bank fields, and `MPLLA_FRAC_UPDATE` / `MPLLB_FRAC_UPDATE` triggers.

The context-restore fields are a major part of this range. `CNTX_RSTR_REQ_CTRL`, `CNTX_SEL_OVRD_IN_*`, `SUP_CNTX_CFG_*`, `MPLLA_CNTX_CFG_0` through `_9`, and `MPLLB_CNTX_CFG_0` through `_10` describe saved or selectable hardware context payloads for supervisor and MPLL state. The AON portion then covers SRAM power-gating, MPLLA/MPLLB tune banks, calibration bank selection, tune-done status, tune payloads, in-recalibration flags, power-gate/supervisor overrides, PMA recalibration bank selection, common calibration status, RTUNE status and per-bank RX/TXDN/TXAVG values, SRAM override/input/output, firmware/raw version fields, SRAM end/begin-of-context addresses, APB and supervisor controls, metadata location, and SRAM record address override/readback fields.

These fields are stateful hardware configuration and restoration data. They are not persistent software storage, but they can affect what the PHY restores after low-power transitions, recalibration, or firmware-managed bring-up.

### Lane0 ASIC-Facing TX Inputs And Outputs

The `C20_PHY_CR1_LANE0_DIG_ASIC_*` family describes the ASIC-side lane and TX control interface for lane0. The `LANE_OVRD_IN` and `TX_OVRD_IN_0` through `_5` registers carry override values and override-enable bits for lane enable/reset, TX power state, power-source selection, TX reset, USB-mode signaling, idle/low-power entry, raw data/status selects, LBERT enable, pattern selection, TX mux select, alternate PCS grants, data bus enables, voltage boost, loopback, RX detect, reference selection, SSC enable, CDR/regulator controls, and clock selection. The matching `ASIC_*_IN` and `ASIC_*_OUT` registers expose the non-overridden input/status view.

The fields are heavily paired: many controls have both a value and an `*_OVRD_EN` bit. This shape is an important integration signal for PHY bring-up/debug code because a register write often needs to preserve unrelated override controls and update value/enable pairs atomically.

### Lane0 TX Power, DCC, Status, Clock, And LBERT Fields

The `C20_PHY_CR1_LANE0_DIG_TX_*` blocks define lane0 transmitter behavior after the ASIC-facing interface. Power-control registers cover TX P-states (`P0`, `P0S`, `P1`, `P2`), power-up/down timing, TX reset, power-source selection, enablement, current power state, requested state, and PLL/clock-related status. DCC fields expose differential/common-mode IDAC offsets, calibration status, and calibration clock controls. Status/counter fields include sample count, stat count, load values, stop controls, and comparator/DCC data.

Clock-alignment and LBERT blocks provide `TX_CTL_*`, `CLK_ALIGN_*`, LBERT pattern-selection, invert/enable/symbol-mask controls, pattern words (`PAT1_*`, `EXT_PAT_*`), test error/injection/status controls, and signal detect. These are diagnostic and link-training-adjacent fields; mistakes can surface as lane bring-up failures, unstable test modes, or misleading PHY debug counters.

### Lane0 Analog TX Override And Status Fields

The final part of the chunk covers `C20_PHY_CR1_LANE0_DIG_ANA_XF_TX_*` fields. `TX_OVRD_OUT_0` through `_3` expose override controls for analog TX clocks, reset, serializer/data enable, refgen, VCM hold, regulator bypass/fast-start/bleeders, data rate, clock loopback, RX detect, reference select, voltage boost, word clock enable, miscellaneous analog controls, and async reset. Term-code and DCC calibration registers define analog termination load/clock controls, DCC enable/configuration, DCC calibration comparator/control/range/data fields, and self-clear-disable bits.

The chunk ends in analog TX status/equalization: `TX_STAT_EQ_OVRD_0` through `_4` define post/pre emphasis and leg pull direction/enable payloads, and `TX_STAT_OUT_0` starts the readback/status layout for analog clock/reset/data/refgen/VCM/regulator/loopback state. The selected range stops after `TX_ANA_VCM_HOLD_MASK`, so the remaining status masks for `TX_STAT_OUT_0` must be taken from the following chunk.

## Important APIs, Types, And Functions

This range exports no callable APIs or C types. Its interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the mask for the same field.
- Register comments such as `//C20_PHY_CR1_RAWCMN_DIG_AON_MPLLA_TUNE_BANK_0` preserve generated grouping and instance identity.

The practical consumers are generated register-list and field-list macros. In this tree, direct include sites for `dcn_3_2_0_sh_mask.h` include `display/dmub/src/dmub_dcn32.c`, `display/dc/resource/dcn32/dcn32_resource.c`, `display/dc/irq/dcn32/irq_service_dcn32.c`, `display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`, `display/dc/gpio/dcn32/hw_factory_dcn32.c`, `display/dc/gpio/dcn32/hw_translate_dcn32.c`, and `amdgpu/gmc_v11_0.c`. Common helper headers such as `display/dc/inc/reg_helper.h` and `display/dmub/src/dmub_reg.h` token-paste register and field names into the generated `__SHIFT` and `_MASK` symbols.

## Control Flow

There is no runtime control flow in the chunk. Its effective flow is compile-time and table-driven:

1. DCN 3.2 source includes the matching offset header and this shift/mask header.
2. Register-table macros concatenate register and field names into generated symbols such as `C20_PHY_CR1_SUP_DIG_MPLLB_UPLL_PWR_CTL_STAT__MPLL_LOCK_MASK` or `C20_PHY_CR1_LANE0_DIG_TX_LBERT_CTL__LBERT_EN__SHIFT`.
3. Runtime code uses populated register, shift, and mask tables with MMIO or indirect-register access helpers to read, update, poll, or preserve fields.
4. Hardware sequencing lives outside this header: DCN/DMUB/PHY/link code decides when to power up PLLs, restore contexts, run calibration, switch power states, program test patterns, align clocks, and inspect status.

The generated order is hardware-register order, not execution order. Most registers list all shift definitions first and the matching mask definitions second.

## State And Persistence Behavior

The header stores no software state and persists nothing to disk. The represented state is hardware state in CR1 PHY registers:

- MPLL and SSC state: calibration override, lock/status, output enablement, timing, fractional/ramp override, and SSC configuration fields.
- Analog control state: bandgap/reference/supervisor/MPLL/PMIX/RTUNE/CREG values, override-enable bits, async resets, standby/calibration force, and analog readbacks.
- Common/AON state: clock gates, firmware power-up/config status, context restore selection, supervisor/MPLL context images, SRAM power/record addresses, calibration bank selection, tune banks, firmware/raw version, metadata location, and RTUNE calibration values.
- Lane0 TX state: ASIC lane/TX inputs, override selectors, TX P-state requests/status, DCC calibration and offsets, status counters, clock-alignment state, LBERT pattern/test state, FIFO behavior, analog TX termination/DCC/equalization/status fields.

Persistence is hardware-defined. Many configuration and override fields can retain state until reprogramming, power-gating, suspend/resume restore, firmware intervention, or ASIC reset. Status, counter, calibration, self-clearing, and request/done fields can be read-only, sticky, self-clearing, or write-one-to-clear according to the hardware specification; this generated header does not encode access type or side effects.

## Dependencies And Integration Points

This chunk must match the paired DCN 3.2.0 offset header, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`, which supplies the corresponding register/indirect-register addresses. The shift/mask names are useful only when paired with a correct address/index and a helper that understands the register access path.

Important integration points include:

- DCN 3.2 resource, DMUB, IRQ, clock-manager, GPIO, and GMC code that includes this generated header and relies on token-pasted field names.
- Register helper infrastructure in `display/dc/inc/reg_helper.h` and `display/dmub/src/dmub_reg.h`, where `FD_SHIFT`, `FD_MASK`, `REG_UPDATE`, `REG_GET`, and related helpers consume these constants.
- PHY/link bring-up, link training, diagnostics, and low-power restore paths that program C20 PHY MPLL, lane, TX, DCC, clock-alignment, and LBERT state through generated register tables.
- Firmware/DMUB-managed paths that may use the AON/context/tune metadata to coordinate hardware-owned restoration or calibration with driver-owned programming.

The file also cross-relates to generated DPCS/C20 PHY offset/index headers in neighboring ASIC directories. Those headers provide the index namespace; this chunk provides the field layout for DCN 3.2's embedded C20 PHY CR1 fields.

## Risks And Edge Cases

- Generated-header drift is the main risk. A stale shift or mask can compile cleanly while corrupting a different hardware field at runtime.
- This is a PHY-control region, so field mistakes can cause hard-to-triage display failures: PLL lock timeouts, unstable clocks, failed link training, incorrect lane power state, broken recovery after suspend/resume, or PHY firmware/driver ownership conflicts.
- Value and override-enable pairs must be kept together. Misprogramming `*_OVRD_EN` bits can leave intended values inactive or force manual values when firmware/hardware state machines should own the field.
- Status, request, self-clear-disable, tune-done, in-recalibration, and calibration/control fields have side effects or handshake semantics outside the header. Generic read/modify/write code must preserve unrelated bits and honor hardware sequencing.
- Repeated context, tune-bank, RTUNE, and lane/TX fields are structurally similar, which increases the chance of generator or caller mix-ups between MPLLA/MPLLB, supervisor/MPLL context payloads, or lane/aggregate register spaces.
- Full-width payload masks such as context words, CREG data, LBERT pattern words, leg-pull fields, SRAM addresses, and RTUNE values must remain wide enough for the hardware payload; accidental narrowing can silently truncate calibration or diagnostic data.
- The chunk ends in the middle of `C20_PHY_CR1_LANE0_DIG_ANA_XF_TX_STAT_OUT_0`. Whole-file research must merge the following chunk before making complete claims about that register or the remaining lane0 analog TX status fields.

## Test Signals

Useful validation signals for changes touching this range include:

- Build coverage for DCN 3.2 display code so all token-pasted shift/mask references in resource, DMUB, IRQ, clock, GPIO, and GMC paths resolve.
- Mechanical comparison of every `C20_PHY_CR1_*` shift/mask in this range against AMD's authoritative DCN 3.2 register database or known-good generated headers.
- Static consistency checks that each non-reserved field has matching `__SHIFT` and `_MASK` macros, that value/override-enable field pairs remain present, and that repeated bank/context/register families remain structurally consistent.
- DisplayPort/HDMI modeset and hotplug tests across CR1-backed PHY paths, including link training, retraining, deep-color/clock changes, suspend/resume, power-gating restore, and multi-display activity.
- PHY PLL validation: MPLLA/MPLLB calibration, lock polling, power-up/down timing, SSC fractional/ramp override behavior, and clock-output enablement under expected and low-power transitions.
- Lane0 TX validation: P-state transitions, TX reset/power-source changes, DCC calibration, clock-alignment status, FIFO behavior, and analog TX status readbacks.
- Diagnostic validation for LBERT pattern programming, error/status reporting, signal-detect paths, TX level/equalization fields, and RTUNE/tune-bank readbacks.
- Regression checks for firmware/driver coordination around AON SRAM/context restore, tune-done/in-recalibration flags, metadata location, and firmware version/status fields.

## Cross-Chunk Notes

Earlier chunks of `dcn_3_2_0_sh_mask.h` contain the preceding C20 PHY CR1 register fields that lead into `C20_PHY_CR1_SUP_DIG_MPLLA_SSC_SSC_RAMP`. Later chunks continue `C20_PHY_CR1_LANE0_DIG_ANA_XF_TX_STAT_OUT_0` after line 93178 and then cover the remaining lane0/laneX or subsequent PHY fields. The final per-file report should synthesize this chunk with adjacent chunks before describing the complete DCN 3.2.0 shift/mask namespace.
