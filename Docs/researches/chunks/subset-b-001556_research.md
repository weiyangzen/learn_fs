# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 47204-49875

## Scope

This chunk covers lines 47204-49875 of the generated AMD DCE 12.0 register shift/mask header. It begins in the tail of `DC_COMBOPHYPLLREGS1_VREG_CFG`, covers the remaining observation/DFT fields for COMBOPHY PLL instance 1, then defines complete UNIPHY reserved-register blocks for UNIPHY2, UNIPHY3, and UNIPHY4. Between those reserved blocks it covers COMBOPHY common, TX-lane, and PLL register masks for instances 2 and 3. It ends at the start of `dce_dc_dc_combophycmregs4_dispdec`, after the full `DC_COMBOPHYCMREGS4_COMMON_FUSE1` field definitions and just before `COMMON_FUSE2`.

The file content is generated-style C preprocessor metadata only. There are no functions, structs, enums, inline helpers, includes, or executable statements in this range. The exported surface is a large set of `#define` constants naming bit shifts and already-positioned masks for memory-mapped AMD display PHY registers.

## Purpose

The chunk provides field-level definitions for DCE 12.0 display PHY hardware programming. The visible register families describe:

- PLL instance 1 diagnostic tail fields: `DC_COMBOPHYPLLREGS1_VREG_CFG` masks for voltage-regulator/DPLL config bits, `OBSERVE0`, `OBSERVE1`, and `DFT_OUT`.
- UNIPHY macro reserved windows for instances 2, 3, and 4: `DCIO_UNIPHY{2,3,4}_UNIPHY_MACRO_CNTL_RESERVED0` through `...RESERVED159`, each modeled as a full 32-bit reserved payload.
- COMBOPHY common registers for instances 2 and 3: fuse calibration, margin/de-emphasis nominal defaults, lane power management, TX common controls, TMDS/DisplayPort mode fields, lane resets, Z-calibration control, and display reserved-for-future-use registers.
- COMBOPHY TX-lane registers for instances 2 and 3: per-lane command-bus TX control, per-lane margin/de-emphasis, per-lane global TX controls, and lane-local reserved slots across lanes 0-3.
- COMBOPHY PLL registers for instances 2 and 3: frequency-control words, bandwidth control, calibration, loop control, voltage-regulator configuration, observation selectors, lock timing, and DFT output.
- The start of COMBOPHY common instance 4 fuse metadata: `DC_COMBOPHYCMREGS4_COMMON_FUSE1`.

These constants let AMDGPU display code compose precise MMIO read/modify/write values without embedding raw bit offsets and masks at each call site.

## Important Macro Families

`DC_COMBOPHYPLLREGS1_*` in this range is partial. Lines 47204-47208 finish the `VREG_CFG` mask list with `sel_bump`, `sel_rladder_x`, `short_rc_filt_x`, `vref_pwr_on`, and `dpll_cfg_2`. The following `OBSERVE0` fields expose lock-detection TDC steps, sticky-lock clear, lock-detect disable, DCO config, and analog observation select. `OBSERVE1` exposes digital observation selectors, trigger selectors/dividers, and a `lock_timer`. `DFT_OUT` is a full-width `dft_data` readout.

`DCIO_UNIPHY2_UNIPHY_MACRO_CNTL_RESERVED*`, `DCIO_UNIPHY3_UNIPHY_MACRO_CNTL_RESERVED*`, and `DCIO_UNIPHY4_UNIPHY_MACRO_CNTL_RESERVED*` are highly regular blocks. Each instance has 160 register comments in this chunk, numbered `0` through `159`. Each register defines exactly one field, `UNIPHY_MACRO_CNTL_RESERVED`, with shift `0x0` and mask `0xFFFFFFFFL`. These are placeholders for a contiguous reserved hardware-control aperture; the generated header still publishes symbols so offset/mask tables stay aligned with the ASIC register database.

`DC_COMBOPHYCMREGS2_COMMON_*` and `DC_COMBOPHYCMREGS3_COMMON_*` share the same layout. `COMMON_FUSE1`, `COMMON_FUSE2`, and `COMMON_FUSE3` carry validity bits, impedance override values, lane/RON/RTT controls, refresh calibration, drive/current controls, mode enables, and spare or unpopulated fields. `COMMON_MAR_DEEMPH_NOM` stores nominal de-emphasis and margin selections. `COMMON_LANE_PWRMGMT` exposes lane power state fields. `COMMON_TXCNTRL` includes common TX enable/termination-style controls. `COMMON_TMDP` covers TMDS/DP-related common-mode behavior. `COMMON_LANE_RESETS` contains per-lane reset controls and related reset-state fields. `COMMON_ZCALCODE_CTRL` controls impedance calibration code behavior. `COMMON_DISP_RFU1` through `COMMON_DISP_RFU7` are full-width reserved display registers.

`DC_COMBOPHYTXREGS2_*` and `DC_COMBOPHYTXREGS3_*` repeat per physical TX lane. For each of lanes 0-3, the block defines `CMD_BUS_TX_CONTROL_LANE<n>`, `MARGIN_DEEMPH_LANE<n>`, `CMD_BUS_GLOBAL_FOR_TX_LANE<n>`, and `TX_DISP_RFU0_LANE<n>` through `TX_DISP_RFU12_LANE<n>`. The command-bus fields include TX enable/reset-style controls. Margin/de-emphasis fields expose per-lane electrical tuning. The global command bus fields include broader TX configuration bits, while the RFU registers preserve full-width masks for unused or undocumented per-lane slots.

`DC_COMBOPHYPLLREGS2_*` and `DC_COMBOPHYPLLREGS3_*` also share a generated layout. `FREQ_CTRL0` through `FREQ_CTRL3` define fractional/integer frequency control, denominator or ref-divider style fields, slew and spread-spectrum related fields, and DPLL configuration fragments. `BW_CTRL_COARSE` and `BW_CTRL_FINE` expose loop bandwidth tuning. `CAL_CTRL` covers calibration start/enable/override-style controls. `LOOP_CTRL` includes loop filter, DCO, and PLL control parameters. `VREG_CFG` carries regulator and DPLL config bits. `OBSERVE0` and `OBSERVE1` mirror the instance-1 observation fields, and `DFT_OUT` publishes full-width design-for-test data.

`DC_COMBOPHYCMREGS4_COMMON_FUSE1` is only the first register of the next COMBOPHY common instance. It defines fuse validity, RON override value/control, RTT override value/control, refresh calibration enable, spare bits, and several unpopulated fields. `COMMON_FUSE2` is named at line 49875 but its fields are outside this chunk.

## APIs, Types, and Functions

There are no callable APIs or C type definitions in this chunk. The relevant interface is the macro naming contract:

- `REGISTER__FIELD__SHIFT` gives the field's bit offset.
- `REGISTER__FIELD_MASK` gives the positioned bit mask for the same field.
- Address-block comments such as `dce_dc_dc_combophypllregs2_dispdec` map groups of masks to companion register-address definitions in other ASIC headers.

Driver code normally consumes these constants through generated or handwritten AMDGPU register helper macros. The correctness contract is therefore name-based: the register name, field name, instance number, lane number, shift, and mask must match the hardware register database and the corresponding register offset header.

## Control Flow

This chunk has no runtime control flow. The effective control flow exists in display-driver callers that use these constants when programming hardware:

1. Select an instance-specific register address, usually from a companion `dce_12_0_*` register header.
2. Read the MMIO value, or build a fresh register value where the hardware programming sequence allows it.
3. Clear affected bits with one or more `*_MASK` constants.
4. Shift field values by the matching `*__SHIFT` constants and OR them into the value.
5. Write the value back to the display PHY register.
6. For lock, calibration, observation, or DFT paths, poll or read back status/diagnostic fields after the write sequence.

The field names imply several order-sensitive external sequences: PLL frequency setup before enable/update, calibration and Z-calibration sequencing, lane reset release before link training, per-lane TX margin/de-emphasis programming during link setup, sticky-lock clear before lock diagnostics, and DFT/observation selector programming before debug readout.

## State and Persistence

The header itself has no mutable software state and writes nothing. It describes persistent or semi-persistent hardware state in display PHY registers. That state remains in the device until changed by MMIO, reset, power-gating, firmware initialization, or hardware side effects.

Important hardware state represented here includes:

- PLL instance state: frequency controls, bandwidth controls, calibration controls, loop behavior, regulator settings, lock-detection behavior, observation mux selection, lock timers, and DFT output.
- UNIPHY macro reserved state: 160 full-width reserved registers for each of UNIPHY2, UNIPHY3, and UNIPHY4. Even though semantically reserved, these addresses may be preserved for register-map compatibility.
- COMBOPHY common state: fuse-derived impedance/current settings, per-lane power-management controls, common TX controls, TMDS/DP mode state, lane reset state, and Z-calibration code behavior.
- COMBOPHY lane state: lane-local TX enable/control, margin and de-emphasis tuning, global per-lane TX configuration, and reserved lane slots.
- Diagnostic state: observation selectors, sticky lock clear, digital trigger selection/dividers, lock timers, and full-width DFT data outputs.

Several fields are likely interpreted by hardware as control strobes or status-affecting toggles rather than ordinary stored software values. The header does not encode read/write, write-one-to-clear, timing, or reset-default semantics; consumers must follow the DCE 12.0 hardware programming guide and existing AMDGPU sequencing.

## Dependencies and Integration Points

The only direct dependency is the C preprocessor. There are no local includes in this range. Integration depends on the wider AMDGPU register-header set under `drivers/gpu/drm/amd/include/asic_reg/dce`, especially files that define register offsets for the same DCE 12.0 address blocks.

Likely integration points in the AMDGPU display stack include:

- Display Core link encoder and PHY programming paths that configure COMBOPHY TX lanes for DisplayPort, HDMI, or DVI signaling.
- Clock and PLL programming paths that choose COMBOPHY PLL frequency, loop, calibration, and regulator settings for a requested pixel/link clock.
- Link training and modeset paths that adjust per-lane margin, de-emphasis, lane power, and reset state.
- ASIC initialization, resume, and power-management code that preserves or restores PHY register state.
- Hardware debug and diagnostics paths that use observation, DFT, lock-detection, and reserved-register readback.
- Generated register accessor macros that expect all field names and masks to be globally visible.

The repeated instance suffixes are part of the integration contract. Code must select `COMBOPHYCMREGS2/TXREGS2/PLLREGS2` for one PHY instance and `COMBOPHYCMREGS3/TXREGS3/PLLREGS3` for another; mixing instance-specific macros can silently program the wrong physical PHY.

## Risks

The main risk is silent hardware misprogramming. These macros compile to constants, so an incorrect shift or mask will not usually fail at build time. It can instead alter reserved bits, choose the wrong lane, corrupt PLL state, or destabilize display link training.

The UNIPHY reserved blocks are especially sensitive. They are full-width masks over names marked reserved; casual writes through these symbols can affect undocumented hardware behavior. Their presence should be treated as register-map completeness, not as permission to freely program them.

The repeated layouts create copy/generation risk. Instances 2 and 3 should remain structurally identical where the hardware says they are identical, while instance prefixes must still be distinct. Lane blocks must preserve lane numbers in every macro name. A single wrong prefix in a generated macro can route a caller to the wrong PHY instance or lane.

PLL and TX electrical fields are timing and board dependent. Bad frequency-control, loop, regulator, impedance, margin, de-emphasis, or calibration values can cause link instability, black screens, intermittent training failure, high error rates, or excessive signal margin changes without a clear software exception.

Mask width and type are another concern. Many fields use `0xFFFFFFFFL`, and smaller fields use long-suffixed masks such as `0x0003FC00L`. Callers should use appropriate unsigned 32-bit intermediates and helper macros rather than signed arithmetic or narrower storage.

The chunk starts and ends inside larger logical families. A per-file reader must reconcile this with the previous chunk for the start of `DC_COMBOPHYPLLREGS1_VREG_CFG` and with the next chunk for the rest of `DC_COMBOPHYCMREGS4_COMMON_FUSE2` and later instance-4 common/TX/PLL definitions.

## Test Signals

Useful validation is mostly build-time, static, and hardware-integration oriented:

- Compile coverage for AMDGPU display translation units that include `dce_12_0_sh_mask.h`.
- Static checks that every `REGISTER__FIELD__SHIFT` has a matching `REGISTER__FIELD_MASK`, and that every mask aligns with its shift and implied width.
- Generated-header diff checks against the authoritative DCE 12.0 register database for COMBOPHY, UNIPHY, and DCIO blocks.
- Instance- and lane-consistency checks comparing `COMBOPHYCMREGS2` with `COMBOPHYCMREGS3`, `COMBOPHYTXREGS2` with `COMBOPHYTXREGS3`, and lane 0-3 layouts within each TX block.
- Modeset and link-training smoke tests across ports that exercise PHY instances 2 and 3, including DisplayPort and HDMI/DVI paths where applicable.
- PLL programming tests that verify requested clocks, lock status, sticky-lock clearing, and stable output after bandwidth/calibration/regulator programming.
- Electrical tuning tests or hardware lab validation for lane margin, de-emphasis, impedance, and Z-calibration fields.
- Suspend/resume and runtime power-management tests that catch lost lane power, reset, PLL, or calibration state.
- Debug readback tests for `OBSERVE0`, `OBSERVE1`, and `DFT_OUT` fields to confirm selector and data masks target the intended bits.

## Cross-Chunk Notes

This is a middle slice of a much larger generated header. It is not a complete file-level view. The final merged research should connect this chunk to the preceding COMBOPHYPLLREGS1 definitions and the following COMBOPHYCMREGS4/TXREGS4/PLLREGS4 material, then summarize all DCE 12.0 PHY instances and reserved register apertures consistently.
