# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 49876-52500

## Purpose

This chunk is part of AMD's generated DCE 12.0 register shift/mask header. It defines C preprocessor constants for bit-field positions (`__SHIFT`) and bit-field masks (`_MASK`) used by the AMDGPU display driver when programming DCE display PHY, DisplayPort transmitter, PLL, and DCIO UNIPHY registers.

The assigned range covers the tail of the `dce_dc_dc_combophycmregs4_dispdec` block, all of the COMBOPHY TX and PLL mask definitions for PHY instances 4 and 5, the DCIO UNIPHY reserved-register masks for UNIPHY5 and UNIPHY6, and the beginning of the COMBOPHY instance 6 common/TX/PLL definitions. It ends inside `DC_COMBOPHYPLLREGS6_LOOP_CTRL`, so the remaining PLL6 loop-control masks and subsequent PLL6 fields are owned by the following chunk.

The data here is hardware-description surface, not executable logic. Its purpose is to give display code stable names for bit operations such as "set the TX lane power field", "read PLL lock/observe fields", or "compose a fractional clock-control word" without hard-coding numeric shifts and masks at each call site.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or runtime APIs in this slice. The important interface is the generated macro namespace consumed by register helper macros elsewhere in the AMD display stack.

Key macro families in this chunk:

- `DC_COMBOPHYCMREGS4_COMMON_*`, `DC_COMBOPHYCMREGS5_COMMON_*`, and `DC_COMBOPHYCMREGS6_COMMON_*`: common COMBOPHY fields for fuse data, nominal TX margin/de-emphasis values, lane power management, TX control, lane resets, impedance/calibration override, and display RFU registers.
- `DC_COMBOPHYTXREGS4_*`, `DC_COMBOPHYTXREGS5_*`, and `DC_COMBOPHYTXREGS6_*`: per-lane transmitter fields for lanes 0 through 3 on each covered PHY instance. Each lane has `CMD_BUS_TX_CONTROL`, `MARGIN_DEEMPH`, `CMD_BUS_GLOBAL_FOR_TX`, and thirteen `TX_DISP_RFU*` full-width reserved fields.
- `DC_COMBOPHYPLLREGS4_*`, `DC_COMBOPHYPLLREGS5_*`, and the start of `DC_COMBOPHYPLLREGS6_*`: PLL frequency-control, bandwidth-control, calibration, loop-control, regulator, observation, and DFT-output fields.
- `DCIO_UNIPHY5_UNIPHY_MACRO_CNTL_RESERVED*` and `DCIO_UNIPHY6_UNIPHY_MACRO_CNTL_RESERVED*`: 160 reserved full-width DCIO UNIPHY register masks per instance, each represented as shift 0 and mask `0xFFFFFFFFL`.

Representative fields with behavioral meaning include:

- Common PHY fuse fields: `fuse*_valid`, `fuse1_ron_override_val`, `fuse1_rtt_override_val`, `fuse2_tx_fifo_ptr`, and `fuse3_ei_det_thresh_sel`.
- Common PHY control fields: `pgdelay`, `pgmask`, `vprot_en`, `clkgate_dis`, `slew_rate_ctl_gen1/2/3`, `dual_dvi_mstr_en`, `dual_dvi_en`, lane reset bits, `zcalcode_override`, and `tx_binary_code_override_val`.
- TX lane fields: `tx_pwr`, `tx_pg_en`, `tx_rdy`, `txmarg_sel`, `deemph_sel`, `tx_margin_en`, `link_speed`, `gang_mode`, `max_linkrate`, `pcs_freq`, `pcs_clken`, `pcs_clkdone`, `pll1_always_on`, `rdclk_div2_en`, `tx_boost_adj`, `tx_boost_en`, and `tx_binary_ron_code_offset`.
- PLL fields: `fcw*_frac`, `fcw*_int`, `fcw_denom`, `fcw_slew_frac`, `refclk_div`, `vco_pre_div`, `fracn_en`, `ssc_en`, `freq_jump_en`, `tdc_resolution`, coarse/fine bandwidth controls, calibration gates and ratios, loop feedback controls, regulator controls, observation selectors, and DFT output data.

## Control Flow

This header has no control flow of its own. It is included by DCE120 display implementation files such as `display/dc/resource/dce120/dce120_resource.c`, `display/dc/dce120/dce120_timing_generator.c`, `display/dc/irq/dce120/irq_service_dce120.c`, GPIO translation/factory code, and DCE120 hardware sequencing code. Those C files combine the masks and shifts with generated offset definitions from `dce_12_0_offset.h`.

The runtime pattern in consumers is:

1. Register list macros, for example `SR()` and `SRI()` in `dce120_resource.c`, map generated `mm...` offset constants to MMIO addresses.
2. Mask/shift list macros in the display component headers expand selected `*_MASK` and `*__SHIFT` names into per-block mask/shift structs.
3. Register helper code uses those fields to read, update, and write MMIO registers with correctly positioned bit values.

This chunk only supplies the compile-time constants for that flow. It does not perform MMIO, branch, loop, allocate, or validate values.

## State And Persistence Behavior

The macros are compile-time constants and have no software state. They do not persist data, allocate memory, hold locks, or create side effects.

The hardware state affected by these definitions is indirect. When a display component uses one of these masks to program a register, the resulting state lives in the GPU display block until reset, power-gating, link reprogramming, or a later MMIO write changes it. Examples include persistent lane power/reset state, PLL frequency/calibration state, transmitter margin/de-emphasis settings, and reserved or diagnostic register values.

Because reserved fields are represented with full-width masks, the generated header permits consumers to describe the whole register word. Correct behavior still depends on higher-level code avoiding writes to reserved fields unless the hardware specification or firmware sequence requires them.

## Dependencies

This header depends on the DCE 12.0 register database that generated the symbolic names, shifts, and masks. It is paired with `dce_12_0_offset.h`, which provides the matching `mm...` register offsets and base indices. The shift/mask names are useful only when the consumer also knows the target register address.

Important integration dependencies include:

- The AMDGPU display core register-helper layer, which expects mask and shift constants in the generated `REG__FIELD_MASK` and `REG__FIELD__SHIFT` naming convention.
- DCE120 resource construction, which includes this header and builds register, mask, and shift tables for timing generators, link encoders, stream encoders, AUX, memory input, audio, and hardware sequencing.
- Link encoder and clock-source code that programs DisplayPort/DVI PHY behavior, lane controls, link speed, PLL configuration, and display clocking.
- The ASIC register-generation process. Manual edits risk desynchronizing this mask header from the offset header and from the actual hardware specification.

## Integration Points

The covered COMBOPHY common registers integrate with display PHY setup. Fuse and calibration masks describe hardware-programmed trim and override fields; lane power management and reset masks support link bring-up, power gating, and recovery; TX control masks describe clock gating, slew, and dual-DVI behavior.

The COMBOPHY TX register families integrate with DisplayPort and DVI link training. Per-lane `tx_pwr`, `tx_pg_en`, and `tx_rdy` fields are relevant to lane enable and readiness sequencing. `txmarg_sel`, `deemph_sel`, and `tx_margin_en` represent signal-integrity controls. `CMD_BUS_GLOBAL_FOR_TX` fields connect lane programming to link rate, PCS clocking, gang mode, PLL behavior, and transmitter boost/impedance adjustment.

The COMBOPHY PLL register families integrate with DCE120 clock-source setup. Frequency-control fields encode fractional and integer FCW values and reference/VCO divisors. Calibration and bandwidth fields influence lock behavior, loop stability, spread-spectrum clocking, and dynamic frequency changes. Observation and DFT fields support diagnostics and bring-up validation.

The DCIO UNIPHY reserved-register masks preserve register-map coverage for UNIPHY instances 5 and 6. These definitions may be used by generated tables, debug dumps, or low-level sequences that need to address a full reserved register word, but they do not convey semantic subfields beyond "the entire 32-bit register."

The range boundaries matter for reconciliation: the first line is inside the COMBOPHY4 common fuse area that began before this chunk, and the final line only includes the first PLL6 loop-control mask. The merge lane should combine this with adjacent chunks before drawing per-file conclusions about the complete COMBOPHY4 and PLL6 register groups.

## Risks And Edge Cases

- A wrong shift or mask silently corrupts MMIO field programming. For display PHY and PLL registers, that can appear as link-training failures, unstable clocks, blank displays, intermittent hotplug failures, or power-management regressions.
- The generated naming is highly repetitive across PHY instances 4, 5, and 6. Copy/paste or generator drift between instances can create asymmetric behavior where one connector path fails while another works.
- Some fields are active-low or status-oriented by hardware convention, but the header does not encode access type, reset value, read/write permission, or sequencing requirements. Consumers must rely on the register spec and higher-level driver logic.
- Reserved fields have full-width masks. Accidentally treating an RFU or `UNIPHY_MACRO_CNTL_RESERVED*` definition as safe writable configuration could disturb undocumented hardware state.
- The chunk starts and ends mid-address-block. Research or tooling that treats this slice as a complete file region would miss `COMMON_FUSE1/FUSE2` context before line 49876 and the rest of `DC_COMBOPHYPLLREGS6_LOOP_CTRL` after line 52500.
- The constants use `L`-suffixed masks such as `0xFFFFFFFFL`. Refactors should preserve unsigned 32-bit MMIO semantics and avoid sign-extension surprises when values are widened or combined.
- These masks must stay synchronized with the corresponding `dce_12_0_offset.h` definitions and with the ASIC base-index mapping used by `BASE()`, `SR()`, and `SRI()` macros.

## Test Signals

Useful validation signals are primarily compile-time, hardware bring-up, and display conformance checks:

- AMDGPU display code that includes `dce_12_0_sh_mask.h` should compile without missing mask or shift symbols for DCE120 resources, IRQ, timing-generator, GPIO, AUX, link-encoder, and hardware-sequencing paths.
- Static checks can compare each `*_MASK` against its `*__SHIFT` and expected field width, and compare repeated PHY instances 4, 5, and 6 for intentional symmetry.
- Register-generation validation should confirm this header matches the same DCE 12.0 source database as `dce_12_0_offset.h`.
- Display bring-up on DCE12 hardware should complete without PLL lock failures, PHY power sequencing timeouts, lane readiness timeouts, or link-training errors on connectors mapped to the covered PHY/UNIPHY instances.
- DisplayPort validation should exercise multiple link rates, lane counts, voltage-swing/pre-emphasis levels, spread-spectrum settings, power-gating transitions, hotplug cycles, suspend/resume, and monitor reconnects.
- Diagnostics should confirm that debug or trace register writes using these masks preserve unrelated bits in the same register word.
- Regression tests should include connectors backed by each repeated instance, because instance-asymmetric mask mistakes often show up only on a subset of physical ports.
