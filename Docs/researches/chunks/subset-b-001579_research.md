# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h lines 10477-13111

## Scope

This chunk covers lines 10477-13111 of the generated AMD DCN 1.0 register offset header. It contains only C preprocessor constants: no functions, structs, enums, inline helpers, or executable control flow. The chunk starts at the `dce_dc_dcio_dcio_chip_dispdec` address block with DC GPIO offsets and ends inside the `azinputendpoint_f2codecind` indexed Azalia input endpoint block after the first input pin configuration-default register.

The slice contains 2635 source lines, 2404 `#define` lines, and 32 named `addressBlock` sections. Most direct MMIO-style macros are paired with a `_BASE_IDX` macro, while indexed register blocks use `ix*` names without `_BASE_IDX`. The exported surface is therefore an ABI-like set of symbolic register addresses for DCN 1.0 display, GPIO, PHY, VGA, and Azalia audio code.

## Purpose

The macros map hardware register names to DCN 1.0 offsets or indexed-register addresses. Driver code combines these constants with ASIC base-address data and companion shift/mask headers to program display I/O hardware.

The major hardware areas in this chunk are:

- DCIO GPIO register groups for generic GPIO, DVO data, DDC1-DDC6, DDC VGA, sync, genlock/swaplock, HPD, power sequencing, pad strength, AUX/I2C pads, DVO strength/reference/skew control, I2S/SPDIF, AUX control, RX enable, and pull-up control.
- DAC and UNIPHY reserved macro-control windows, including four large repeated `DCIO_UNIPHY{0..3}_UNIPHY_MACRO_CNTL_RESERVED{0..159}` blocks.
- Four COMBOPHY instances, each split into common/fuse/RFU registers, TX lane command/DFE/RFU registers, and PLL frequency/spread-spectrum/RFU/wrapper-control registers.
- ZCAL macro-control, compensation enable, auto-calibration control, and fuse offsets.
- Indexed VGA sequencer, CRT controller, graphics controller, and attribute-controller registers.
- Indexed Azalia F2 codec output endpoint registers, audio descriptor and sink-info tables, CRC result windows, and the beginning of the Azalia input endpoint register map.

## Important Macro Families

Direct MMIO offset macros in this chunk follow a paired pattern:

- `mmREGISTER` gives the register offset within its hardware address segment.
- `mmREGISTER_BASE_IDX` selects the base segment index used by local register helper macros such as `BASE(mmREGISTER_BASE_IDX) + mmREGISTER`.

Indexed-register macros follow an `ixREGISTER` form. These values are not simple direct MMIO offsets in the same way as `mm*` macros; they are indices or codec verb-style node/register addresses for indirect VGA and Azalia access paths.

The `dce_dc_dcio_dcio_chip_dispdec` block has 148 defines. It exposes the DC GPIO hardware that DCN GPIO translation code maps to software GPIO IDs: generic pins, DDC lines, HPD lines, sync pins, genlock/swaplock pins, DVO data, power sequencing, and I2C/AUX related pads. Representative macros include `mmDC_GPIO_GENERIC_MASK`, `mmDC_GPIO_DDC1_A`, `mmDC_GPIO_DDC6_Y`, `mmDC_GPIO_DDCVGA_A`, `mmDC_GPIO_SYNCA_A`, `mmDC_GPIO_GENLK_A`, `mmDC_GPIO_HPD_A`, `mmDC_GPIO_PWRSEQ_A`, `mmDC_GPIO_I2CPAD_A`, `mmDC_GPIO_AUX_CTRL_0`, `mmDC_GPIO_RXEN`, and `mmDC_GPIO_PULLUPEN`.

The `dce_dc_dcio_dcio_dac_dispdec` block is a small reserved DAC macro-control window: `mmDAC_MACRO_CNTL_RESERVED0` through `mmDAC_MACRO_CNTL_RESERVED3`, each with base index 2.

The UNIPHY blocks are highly regular. `dce_dc_dcio_dcio_uniphy0_dispdec`, `...uniphy1...`, `...uniphy2...`, and `...uniphy3...` each provide 160 reserved macro-control offsets and 160 base-index macros. These appear as `mmDCIO_UNIPHYN_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED159` for N = 0..3. They reserve a broad register-address surface for PHY macro internals without exposing field-level meaning in the offset header.

Each COMBOPHY instance has three related address blocks:

- `dce_dc_combophy_dc_combophycmregsN_dispdec` exposes common registers, fuse registers, spare/RFU control, and display RFU offsets such as `COMMON_FUSE1`, `COMMON_FUSE2`, `COMMON_TXCNTRL`, `COMMON_RXCNTRL`, `COMMON_TXCNTRL2`, `COMMON_ZCALCODE_CTRL`, and `COMMON_DISP_RFU0` through `COMMON_DISP_RFU7`.
- `dce_dc_combophy_dc_combophytxregsN_dispdec` exposes per-lane TX registers for four lanes, including `CMD_BUS_TX_CONTROL_LANE{0..3}`, `TX_CONTROL_LANE{0..3}`, `TX_DISP_RFU0_LANE{0..3}` through `TX_DISP_RFU12_LANE{0..3}`, and DFE/RFU lane registers.
- `dce_dc_combophy_dc_combophypllregsN_dispdec` exposes PLL registers such as `FREQ_CTRL0`, `FREQ_CTRL1`, spread-spectrum control, observation/RFU registers, and `PLL_WRAP_CNTRL`.

The ZCAL region is split between five reserved macro-control offsets in `dce_dc_dcio_dcio_zcal_dispdec` and functional ZCAL registers in `dce_dc_zcal_dc_zcalregs_dispdec`: `mmCOMP_EN_CTL`, `mmCOMP_MISC_CTL_0`, and `mmZCAL_FUSES`.

The VGA blocks expose legacy indexed register numbers: sequencer `ixSEQ00` through `ixSEQ04`, CRT controller `ixCRT00` through selected higher registers including `ixCRT18`, `ixCRT1E`, `ixCRT1F`, and `ixCRT22`, graphics controller `ixGRA00` through `ixGRA08`, and attribute controller `ixATTR00` through `ixATTR14`.

The Azalia output endpoint block `azendpoint_f2codecind` maps F2 codec converter and pin-control register indices. It includes converter format/channel/digital-converter/stripe/ramp/GTC registers, converter capability parameters, pin widget control, unsolicited response, pin sense, configuration defaults, speaker and channel allocation, downmix, audio descriptor selection/data, multichannel enables, lipsync, HBR, audio sink info index/data, IEC 60958 channel-status override registers, association info, digital output status, LPIB snapshot registers, coding type, format-change reporting, wireless display identification, remote keepalive, and pin capability parameters.

The `azendpoint_descriptorind` and `azendpoint_sinkinfoind` blocks expose indexed audio descriptor slots `ixAUDIO_DESCRIPTOR0` through `ixAUDIO_DESCRIPTOR13` and sink-info fields such as manufacturer/product IDs, sink description length, port IDs, and `ixSINK_DESCRIPTION0` through `ixSINK_DESCRIPTION17`.

The Azalia CRC blocks provide eight channel result indices each for input CRC0, input CRC1, output CRC0, and output CRC1.

The final `azinputendpoint_f2codecind` block begins the input endpoint map. Within this chunk it covers input converter format/channel/digital-converter fields, input converter capability parameters, input pin widget control, unsolicited response, pin sense, and the first input pin configuration-default register. The rest of the input endpoint block continues after this chunk.

## APIs, Types, and Functions

There are no callable APIs, C types, or functions in this source slice. The macro names are the interface.

Typical consumers use helper macros like the DCN10 GPIO code's `REG(reg_name)`, which expands `BASE(mmREG_BASE_IDX) + mmREG`. The same source files include `dcn/dcn_1_0_offset.h`, `dcn/dcn_1_0_sh_mask.h`, `soc15_hw_ip.h`, and `vega10_ip_offset.h`; the offset header supplies register locations, the shift/mask header supplies field layout, and SoC/IP offset headers supply base address selection.

Observed local include users include:

- `display/dc/gpio/dcn10/hw_translate_dcn10.c`, where `mmDC_GPIO_*_A` offsets are translated to logical GPIO IDs and DDC/HPD/generic line IDs.
- `display/dc/gpio/dcn10/hw_factory_dcn10.c`, where GPIO, DDC, HPD, and generic register tables are assembled using DCN 1.0 offset and shift/mask macros.
- `display/dc/irq/dcn10/irq_service_dcn10.c`, which includes the offset header as part of DCN10 interrupt service construction.
- `display/dc/resource/dcn10/dcn10_resource.c`, which includes the generated DCN 1.0 register data for resource setup.
- Powerplay BACO command tables for older ASIC managers (`ci_baco.c`, `fiji_baco.c`, `polaris_baco.c`, `tonga_baco.c`) that reference `mmDC_GPIO_GENERIC_MASK` directly for power-transition scripting.

## Control Flow

The header itself has no runtime control flow. It shapes driver control flow by naming the hardware registers that register helper code reads and writes:

1. Select the correct macro family for the hardware domain: `mmDC_GPIO_*` for GPIO/DDC/HPD, `mmDCIO_UNIPHYN_*` or `mmDC_COMBOPHYN_*` for PHY-related registers, `ixSEQ*`/`ixCRT*`/`ixGRA*`/`ixATTR*` for VGA indexed registers, or `ixAZALIA_*` for Azalia codec/register windows.
2. For direct MMIO registers, add the address segment base chosen by the paired `_BASE_IDX` macro to the `mm*` offset.
3. For field-level programming, combine this offset header with `dcn_1_0_sh_mask.h` so software can preserve reserved bits and update only the intended field.
4. For indexed windows, write/select the `ix*` index through the appropriate VGA, Azalia, descriptor, sink-info, or CRC access path rather than treating it as a normal `mm*` offset.
5. Read back state or status where required by the hardware flow, such as HPD/DDC GPIO state, sink/audio endpoint information, CRC channel results, or PHY/calibration state.

The most sequencing-sensitive runtime flows implied by this chunk are display hotplug/DDC GPIO access, AUX/I2C pad control, PHY/PLL bring-up or diagnostics, ZCAL programming, legacy VGA access, and Azalia endpoint/audio descriptor/sink-info programming. The offset macros do not encode ordering rules; those must come from the hardware programming model and the caller's register access helpers.

## State and Persistence

This header stores no software state and has no persistence. It names hardware state that persists in registers until reset, power transition, firmware/hardware action, or driver writes change it.

State domains visible in this chunk include:

- GPIO state for input/output value, output enable, mask, and active-state registers across generic GPIO, DDC, DDC VGA, sync, genlock, HPD, power-sequence, and I2C pad groups.
- Pad and electrical-control state for GPIO pad strength, DVO strength/reference/skew, AUX control, RX enable, pull-up enable, and I2S/SPDIF pins.
- Reserved or low-level PHY macro state for DAC, UNIPHY0-3, COMBOPHY common/TX/PLL, and ZCAL macro-control windows.
- Calibration/fuse state through ZCAL compensation enable, misc control, and fuse offsets.
- Legacy VGA indexed state in sequencer, CRT, graphics, and attribute controller registers.
- Azalia output endpoint state for converter format, channel/stream ID, digital converter controls, GTC embedding, pin widget behavior, unsolicited responses, pin sense, speaker/channel allocation, audio descriptors, multichannel and HBR/lipsync controls, sink info, IEC channel-status overrides, LPIB snapshots, coding type, format-change reporting, wireless display identification, and remote keepalive.
- Azalia CRC result state for eight channels in four CRC result windows.
- Partial Azalia input endpoint state for input converter and input pin control.

Because many of these registers are hardware-facing latches, status windows, or indirectly indexed tables, software must preserve reserved bits, use the correct access path, and coordinate with power-management state. The `_BASE_IDX` value of 2 is repeated across the direct DCIO/PHY/ZCAL offsets in this chunk and is part of that addressing contract.

## Dependencies and Integration Points

This chunk depends only on the C preprocessor, but it is meaningful only with the rest of the AMDGPU display register ecosystem:

- `dcn_1_0_sh_mask.h` supplies field shifts and masks for many of the offsets defined here.
- `soc15_hw_ip.h` and `vega10_ip_offset.h` provide base segment constants such as the `DCE_BASE__INST0_SEG*` values used by DCN10 helper macros.
- DCN10 GPIO factory/translation code maps these offsets to `enum gpio_id`, DDC line IDs, HPD IDs, sync IDs, and generic GPIO instances.
- HPD, DDC, and generic GPIO register table headers use the same offset/shift/mask naming conventions to populate register structs.
- Power-management BACO scripts depend on at least `mmDC_GPIO_GENERIC_MASK` remaining stable for direct read/modify/write command tables.
- Display audio code and diagnostics depend on the Azalia `ix*` endpoint, descriptor, sink-info, and CRC indices matching the hardware codec/register windows.
- Cross-generation generated headers reuse many names with different offsets or identical indexed values; callers must include the header for the active ASIC generation rather than mixing DCN/DCE generations.

The repeated instance structure is an important integration signal. UNIPHY and COMBOPHY instance numbers are encoded in macro names, while GPIO lines and Azalia channel slots are represented by repeated adjacent macro families. Callers should select these symbolically rather than deriving raw offsets by arithmetic unless a local register-table abstraction already proves the layout.

## Risks

The primary risk is silent hardware misaddressing. An incorrect offset or base index can compile cleanly while causing driver writes to touch the wrong GPIO, PHY, ZCAL, VGA, or Azalia register. Symptoms would likely be display hotplug failure, DDC/I2C probing failure, broken AUX or pad behavior, PHY/PLL bring-up instability, audio endpoint misconfiguration, missing sink descriptors, bad CRC diagnostics, or power-transition failures.

Direct and indexed register spaces are easy to confuse. `mm*` macros in this chunk are direct offsets paired with `_BASE_IDX`; `ix*` macros are indexed values for VGA or Azalia windows. Treating an `ix*` value as an MMIO offset, or adding a base index to it, would address the wrong hardware path.

Generated reserved/RFU blocks are still part of the hardware contract. The UNIPHY `RESERVED0..159`, COMBOPHY RFU, DAC reserved, and ZCAL reserved offsets may be used by firmware, diagnostics, bring-up code, or later local patches even though the names do not document field semantics. Renaming or pruning them would break generated-header compatibility.

Repeated instance blocks carry copy/generation risk. A one-register drift among UNIPHY0-3 or COMBOPHY0-3 would be hard to catch by normal compilation and could affect only one physical link, lane group, or connector.

GPIO offsets are tied to logical pin translation. The DCN10 translation code switches on offsets such as `REG(DC_GPIO_DDC1_A)` and uses shift/mask macros to identify pins. A mismatch between offset and mask headers can make the driver classify a pin incorrectly even if both headers compile.

Power-management interaction is sensitive. BACO tables use `mmDC_GPIO_GENERIC_MASK` directly, so changes in this region can affect low-power entry/exit behavior outside the display core.

The chunk boundary is not a semantic boundary. It starts cleanly at a DCIO address block, but it ends in the middle of `azinputendpoint_f2codecind`; the remaining input endpoint, Azalia root, and later stream blocks continue in following lines. Final per-file reconciliation must merge adjacent chunks before presenting the Azalia input endpoint as complete.

## Test Signals

Useful validation signals for this chunk are mostly static, build-time, and hardware-smoke oriented:

- Build coverage for DCN10 display code that includes `dcn_1_0_offset.h`, especially GPIO factory/translation, IRQ service, and resource setup.
- Static generated-header checks that each direct `mm*` macro in these address blocks has the expected paired `_BASE_IDX`, that base indices match the generated ASIC database, and that no duplicate macro names collide.
- Cross-generation regeneration diffs against the authoritative DCN 1.0 register source, with attention to repeated UNIPHY0-3 and COMBOPHY0-3 layouts.
- GPIO smoke tests for DDC1-DDC6, DDC VGA, HPD1-HPD6, generic GPIO A/B, sync, genlock/swaplock, I2C pad, and power-sequence pin access.
- Display connector tests that exercise EDID reads, hotplug interrupts, AUX/DDC probing, and low-power entry/exit paths that touch DC GPIO masks.
- PHY bring-up or diagnostics that verify COMBOPHY common/TX/PLL and ZCAL offsets are reachable on all exposed instances and that reserved/RFU offsets are not accidentally shifted between instances.
- Legacy VGA access tests for sequencer, CRT, graphics, and attribute indexed register selection if the platform uses the VGA path.
- HDMI/DP audio tests that read/write Azalia endpoint converter/pin controls, audio descriptor slots, sink-info strings, multichannel/HBR/lipsync controls, IEC channel status overrides, LPIB snapshot state, and CRC channel result windows.
- Negative/static tests that keep `ix*` indexed-register constants out of direct `REG()` style MMIO expansion paths.

## Cross-Chunk Notes

This is an interior slice of a large generated register offset header. The previous lines cover earlier DCIO, power, backlight, impedance-calibration, interrupt, semaphore, and USB-C flip-selection offsets immediately before the DC GPIO block. The following lines continue the Azalia input endpoint block, then Azalia root and stream indexed blocks. The final merged per-file research should treat this document as the DCIO GPIO/PHY/VGA/Azalia-endpoint slice, not as the complete DCN 1.0 offset-header story.
