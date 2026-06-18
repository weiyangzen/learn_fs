# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 110397-112789

## Scope

This chunk is part of the generated AMD DCN 4.1.0 ASIC register shift/mask header. It covers 2,177 `#define` entries for bit positions and bit masks in DPCSSYS CR2 DisplayPort/PHY lane registers, beginning inside lane 2 RX ASIC input fields and ending inside lane 3 RX statistic match controls. The source is declarative rather than executable: each register comment is followed by `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros that other register-access helpers use to pack, update, and extract hardware fields.

The covered register families are mostly 16-bit DPCS/PHY lane controls. Line boundaries split the full header, so the first register, `DPCSSYS_CR2_LANE2_DIG_ASIC_RX_ASIC_IN_0`, is continued from the previous chunk and `DPCSSYS_CR2_LANE3_DIG_RX_STAT_MATCH_CTL1` continues into the next chunk.

## Purpose

The chunk provides the field layout contract for low-level display PHY lane programming on DCN 4.1.0 hardware. It lets typed-ish C macro layers refer to symbolic fields instead of hard-coded bit constants when programming:

- Lane 2 digital ASIC RX/TX control and override/status registers.
- Lane 2 TX/RX power-state and power-up timing registers.
- Lane 2 CDR, DPLL, VCO calibration, RX adaptation, statistic counters, MPHY, and analog override/status registers.
- Lane 2 analog TX/RX trim, ATB/measurement, termination, equalization, VREG, CDR, signal detect, and slicer controls.
- The start of lane 3 digital ASIC and TX power-control/statistic registers.

## Important APIs And Macros

This header exposes no functions or C types. Its API is the macro naming convention consumed by register helper layers:

- `REG__FIELD__SHIFT` gives the starting bit index for a field.
- `REG__FIELD_MASK` gives the mask at its final shifted position.
- The `FD_SHIFT(reg, field)` and `FD_MASK(reg, field)` helpers in `drivers/gpu/drm/amd/display/dmub/src/dmub_reg.h` concatenate tokens to these generated names.
- `REG_SET`, `REG_UPDATE`, `REG_GET`, and related display-register helpers use the shift/mask values to form read-modify-write operations.
- The macros pair with generated offset headers such as `dcn_4_1_0_offset.h` and DPCS offset headers, where `ixDPCSSYS_CR2_LANE2_*` and `ixDPCSSYS_CR2_LANE3_*` provide register addresses while this file provides field layout.

Important register groups in this chunk include:

- `DPCSSYS_CR2_LANE2_DIG_ASIC_*`: lane 2 digital ASIC handshakes, TX/RX request/status, link state fields, loopback, override enables, async data, main/pre/post cursor, drive boost, RX CDR/VCO load values, termination, alignment, and OCLA controls.
- `DPCSSYS_CR2_LANE2_DIG_TX_PWRCTL_*`: TX power-state templates for P0/P0S/P1/P2, TX power-up timing, DCC CR bank address/data, DAC control/range/select/ack/address, TX clock alignment, and TX LBERT controls.
- `DPCSSYS_CR2_LANE2_DIG_RX_PWRCTL_*`: RX power-state templates for P0/P0S/P1/P2 and RX power-up timing fields for CDR, AFE, VCO reset/calibration, deserializer, and digital clock enable sequencing.
- `DPCSSYS_CR2_LANE2_DIG_RX_VCOCAL_*`, `DPCSSYS_CR2_LANE2_DIG_RX_CDR_*`, and `DPCSSYS_CR2_LANE2_DIG_RX_DPLL_*`: calibration, load values, lock/status, coarse/fine CDR, DPLL frequency, and frequency-bound fields.
- `DPCSSYS_CR2_LANE2_DIG_RX_ADPTCTL_*`: RX adaptation configuration and status fields for ATT/VGA/CTLE/DFE tap values, slicer offsets, DAC selection, and adaptation reset.
- `DPCSSYS_CR2_LANE2_DIG_RX_STAT_*`: pattern-match setup, masks, sample counters, statistic counters, statistic clocking, valid-loss controls, and stop controls.
- `DPCSSYS_CR2_LANE2_DIG_ANA_*` and `DPCSSYS_CR2_LANE2_ANA_*`: digital-to-analog override/status fields for TX/RX clocks, equalization, termination, signal detect, RX AFE/CTLE/slicer, ATB measurement, VDAC range, VREG, and CDR analog controls.
- `DPCSSYS_CR2_LANE3_DIG_*`: start of lane 3 digital ASIC lane/TX/RX override and actual ASIC-input/output fields, TX power-state/timing/DCC controls, TX clock alignment, TX LBERT, and the beginning of RX statistic controls.

## Control Flow

There is no runtime control flow in this chunk. Control flow is imposed by consumers that include the header and expand token-pasting macros. The effective flow is:

1. A DCN 4.1.0 source file includes `dcn_4_1_0_offset.h` and `dcn_4_1_0_sh_mask.h`.
2. Register lists or direct register helpers name a register and field.
3. `FD_MASK(reg, field)` expands to `reg__field_MASK`; `FD_SHIFT(reg, field)` expands to `reg__field__SHIFT`.
4. Helper code combines offset, mask, shift, and field value for MMIO or indirect register read/write operations.

Direct include sites found in this tree are DCN 4.0.1 display components such as `dmub/src/dmub_dcn401.c`, `dc/irq/dcn401/irq_service_dcn401.c`, `dc/clk_mgr/dcn401/dcn401_clk_mgr.c`, `dc/resource/dcn401/dcn401_resource.c`, and DCN 4.0.1 GPIO factory/translate code. This particular DPCSSYS lane slice may also be compiled for availability even when only a subset of fields is referenced by a given C file.

## State And Persistence

The macros themselves hold no mutable state and persist nothing. They describe hardware state stored in display PHY/DPCS registers. Many fields in the chunk are stateful at the hardware level:

- Power-state template bits enable or reset analog/digital lane blocks.
- Override enable bits can force hardware-controlled lane signals to software-selected values.
- Status bits and counters expose acknowledgements, calibration status, lock status, sample completion, statistic counts, and valid-loss conditions.
- CR bank and DAC select/address/data fields mediate indirect access to sub-block calibration and DAC controls.

Because these are hardware register fields, persistence depends on ASIC reset, power-gating, display engine reset, and PHY lane power transitions rather than on kernel data structures.

## Dependencies

This chunk depends on the generated AMD register naming scheme remaining consistent across:

- `dcn_4_1_0_offset.h` for MMIO/instance base offsets.
- `dcn_4_1_0_sh_mask.h` for token-pasted field macros.
- Display register helper headers such as `dmub_reg.h` and common AMD register macros in `cgs_common.h`.
- DPCS offset headers under `include/asic_reg/dpcs/`, which expose matching `ixDPCSSYS_CR2_LANE2_*` and `ixDPCSSYS_CR2_LANE3_*` indirect addresses for the same hardware register names.

The field values are generated from ASIC register specifications. Manual edits risk desynchronizing software from the hardware layout.

## Integration Points

The header integrates with the AMD display stack at compile time. It is included by DCN 4.0.1 display code to initialize field mask/shift tables and to support `REG_*` helper expansion. The lane registers in this chunk are part of the DisplayPort/PHY path, so practical consumers are expected around link training, PHY bring-up, debug, diagnostics, calibration, and low-level power sequencing, even when references are indirect or generated.

The offset/mask split is important: an access needs both the `mm`/`ix` register address from an offset header and the field layout from this header. A correct field macro with an incorrect paired offset, or vice versa, can update the wrong hardware bits.

## Risks

- Bitfield drift is the main risk. Incorrect shift or mask values can silently corrupt unrelated bits in PHY lane registers.
- Override fields are especially sensitive because they can bypass normal hardware sequencing for TX/RX requests, power states, data enable, reset, clocking, equalization, and adaptation status.
- Power-state and timing fields can break lane bring-up, link training, suspend/resume, hotplug recovery, or low-power transitions if values are packed incorrectly.
- Reserved/NC fields are present throughout the chunk. Callers should avoid writing them except through hardware-approved sequences; generated masks that include reserved fields must not be used casually as full-register writable masks.
- Several multiword concepts are split across registers, such as TX VCM hold time, VBOOST disable time, CR1A/CR1B pattern/mask values, TX equalization leg controls, and analog measurement selections. Consumers must combine fields in the intended order.
- The chunk starts and ends mid-register-family because of file chunking, so whole-file analysis must merge adjacent chunks before making completeness claims about lane 2 RX input and lane 3 RX statistic controls.

## Test Signals

Useful validation signals for this chunk are compile-time and hardware-facing:

- Build coverage for DCN 4.0.1 display code, especially files that include `dcn_4_1_0_sh_mask.h`, catches missing or renamed field macros through token-pasting expansion failures.
- Static consistency checks can compare every `*_MASK` to the width implied by adjacent field shifts and verify that fields for each 16-bit DPCSSYS register do not overlap unexpectedly.
- Header/offset consistency checks can ensure every register comment in this chunk has a matching address define in the paired DCN or DPCS offset headers.
- Runtime smoke tests include display link detection, DisplayPort/HDMI link training, hotplug, suspend/resume, and multi-lane operation on DCN 4.0.1 hardware.
- PHY diagnostics or debugfs/register-dump tests should preserve reserved bits across read-modify-write helpers and confirm that status/counter fields such as CDR lock, VCO calibration, statistic sample done, and TX/RX acknowledgements behave as expected.
