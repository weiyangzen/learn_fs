# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h lines 12712-15215

## Purpose

This chunk is part of AMD's generated DCE 12.0 register-offset header. It does not implement runtime logic; it provides preprocessor constants that map display-engine register names to MMIO register offsets and base-index selectors used by the AMDGPU display stack.

The assigned range covers the display PHY register-map area for DCE 12.0. It starts in the tail of the `DCIO_UNIPHY1` reserved macro-control table, then defines repeated COMBOPHY common, transmit-lane, and PLL register blocks for PHY instances 1 through 5, and ends in the beginning of the `DCIO_UNIPHY6` reserved macro-control table.

The highest-value content is the repeated PHY programming surface:

- `DCIO_UNIPHY[1-6]_UNIPHY_MACRO_CNTL_RESERVED*` reserved macro-control offsets.
- `DC_COMBOPHYCMREGS[1-5]_COMMON_*` common combo-PHY control and fuse offsets.
- `DC_COMBOPHYTXREGS[1-5]_*_LANE[0-3]` per-lane TX command, margin/de-emphasis, and RFU offsets.
- `DC_COMBOPHYPLLREGS[1-5]_*` per-PHY PLL frequency, bandwidth, calibration, loop, regulator, observe, and DFT offsets.

These constants let display code address the low-level physical link hardware behind DisplayPort/HDMI-style outputs without embedding numeric offsets throughout the driver.

## Important APIs, Types, And Functions

There are no functions, structs, or callable APIs in this range. The exported interface is the macro namespace:

- `mm...` register-offset macros, such as `mmDC_COMBOPHYTXREGS5_CMD_BUS_TX_CONTROL_LANE2`, whose values are register offsets in the DCE 12.0 MMIO space.
- Matching `mm..._BASE_IDX` macros, all `2` in this slice, selecting the register base segment expected by AMD display register-access helpers.
- Address-block comments generated into the header, such as `dce_dc_dc_combophytxregs5_dispdec`, which group the following macros by hardware block.
- `base address` comments, which document the underlying block base used by the register generator. In this slice, COMBOPHY instances 1-2 use base address `0x320`, instances 3-5 use `0xfa0`, and `DCIO_UNIPHY6` uses `0x12c0`.

The macros are intended to be combined with the AMD display register-access infrastructure included by DCE 12.0 modules, alongside the companion `dce_12_0_sh_mask.h` bit-field definitions. Files that include this offset header include DCE 12.0 timing-generator, IRQ, GPIO, hardware-sequencer, resource, and GMC code.

## Control Flow

This chunk has no C control flow. The "flow" is compile-time symbol availability:

1. A DCE 12.0 source file includes `dce/dce_12_0_offset.h`.
2. Hardware-specific register tables or direct register-access macros use these `mm...` and `mm..._BASE_IDX` constants.
3. The driver's register access layer combines the offset and base index to read or write the corresponding MMIO register.

The generated layout is highly regular. Each PHY instance repeats the same groups:

- COMBOPHY common registers: `COMMON_FUSE1` through `COMMON_FUSE3`, `COMMON_MAR_DEEMPH_NOM`, `COMMON_LANE_PWRMGMT`, `COMMON_TXCNTRL`, `COMMON_TMDP`, `COMMON_LANE_RESETS`, `COMMON_ZCALCODE_CTRL`, and `COMMON_DISP_RFU1` through `COMMON_DISP_RFU7`.
- COMBOPHY TX registers: four lanes, each with `CMD_BUS_TX_CONTROL`, `MARGIN_DEEMPH`, `CMD_BUS_GLOBAL_FOR_TX`, and `TX_DISP_RFU0` through `TX_DISP_RFU12`.
- COMBOPHY PLL registers: `FREQ_CTRL0` through `FREQ_CTRL3`, `BW_CTRL_COARSE`, `BW_CTRL_FINE`, `CAL_CTRL`, `LOOP_CTRL`, `VREG_CFG`, `OBSERVE0`, `OBSERVE1`, and `DFT_OUT`.
- UNIPHY reserved macro-control tables: sequential `UNIPHY_MACRO_CNTL_RESERVEDn` offsets with matching base-index macros.

The range boundaries are partial: line 12712 begins at `DCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED88`, after reserved entries 0-87 in the previous chunk; line 15215 ends at `DCIO_UNIPHY6_UNIPHY_MACRO_CNTL_RESERVED39_BASE_IDX`, before the rest of `DCIO_UNIPHY6` in the next chunk.

## State And Persistence Behavior

The header stores no runtime state and performs no persistence. Its constants describe hardware state locations. Any persistence is in the GPU hardware registers that other driver code reads or writes using these offsets.

The state represented by this chunk is physical display-link state:

- COMBOPHY common registers can represent PHY fuses, lane power management, TX control, TMDP behavior, lane resets, impedance/calibration controls, and reserved display RFU fields.
- COMBOPHY TX lane registers can represent lane-specific transmit command bus settings, de-emphasis/margin programming, and reserved per-lane controls.
- COMBOPHY PLL registers can represent frequency programming, bandwidth controls, calibration, loop behavior, regulator configuration, observation/status, and design-for-test outputs.
- UNIPHY reserved tables reserve contiguous macro-control address space that may be hardware-defined or used by generated sequences outside hand-written driver logic.

Because these are raw hardware offsets, changing a value changes the address that later code touches. Such an edit can redirect display bring-up writes to the wrong register and cause link-training, hotplug, clock, or power-management failures.

## Dependencies

This file depends on the DCE 12.0 hardware register map produced by AMD's ASIC register-generation flow. The header guard `_dce_12_0_OFFSET_HEADER` protects the generated macro namespace from repeated inclusion.

Runtime users depend on surrounding AMDGPU display infrastructure:

- `dce_12_0_sh_mask.h` supplies the companion bit masks and shifts for register fields.
- DCE 12.0 display modules include this header to instantiate register offset tables for timing generation, IRQ routing, GPIO/DDC/AUX handling, resource construction, hardware sequencing, and memory-controller/display integration.
- Register read/write helpers depend on the `_BASE_IDX` values to select the correct MMIO base aperture. In this chunk the base index is consistently `2`.
- The constants assume DCE 12.0 silicon layout. They should not be shared with DCE, DCN, or DPCS register blocks unless the including code intentionally maps the matching ASIC generation.

The source tree also contains newer or different generated register maps with similar UNIPHY names, for example DPCS headers that use `reg...` prefixes and different offsets. Those are not interchangeable with this `mm...` DCE 12.0 namespace.

## Integration Points

The main integration point is the AMD display core's DCE 12.0 backend. PHY-related code uses the register definitions indirectly through hardware register tables and helper macros rather than hand-coding every numeric offset.

This chunk lines up with display-output programming responsibilities:

- Link initialization and training need TX lane and de-emphasis controls from `DC_COMBOPHYTXREGS*`.
- PHY power sequencing and resets need common lane power-management, TX control, TMDP, lane reset, and calibration controls from `DC_COMBOPHYCMREGS*`.
- Pixel/link clock setup and validation can depend on PLL frequency, bandwidth, calibration, loop, regulator, and observe registers from `DC_COMBOPHYPLLREGS*`.
- Board- or ASIC-specific sequences may refer to UNIPHY reserved macro-control offsets when applying generated PHY programming tables.

The repeated instance numbering is important for connector routing. Instances 1 through 5 expose similar common/TX/PLL register sets at different offsets, while the range's partial UNIPHY1 and UNIPHY6 sections are only slices of larger reserved tables.

## Risks And Edge Cases

- This is generated register-map data. Manual edits are high risk because a one-word offset or base-index mistake can compile cleanly while programming the wrong hardware register.
- The chunk starts and ends inside UNIPHY reserved tables. A line-bounded review must not treat the visible reserved ranges as complete definitions for UNIPHY1 or UNIPHY6.
- The visible repeated COMBOPHY blocks are easy to miscompare. Instances 1-5 share naming patterns but have different offset ranges; copy/paste or generator drift can create subtle instance skew.
- Most macros in the UNIPHY sections are named `RESERVED`. Their semantics are not self-documenting, but their positions can still matter for firmware, BIOS table sequences, or generated display initialization scripts.
- All `_BASE_IDX` values in this slice are `2`. Any accidental change to a different base index would route otherwise-correct offsets through the wrong MMIO aperture.
- The PLL register sequence skips one numeric offset between `LOOP_CTRL` and `VREG_CFG` for each instance. Tests or scripts that assume fully contiguous named PLL registers need to tolerate reserved holes.
- Similar macro families exist in other ASIC headers with different prefixes and offsets. Mixing DCE 12.0 `mm...` constants with DPCS `reg...` constants would be an integration bug.
- Since this header contains no type checking, incorrect use of an offset in the wrong block or instance is detected only by display behavior, hardware readback, or generated-table validation.

## Test Signals

Useful validation is mostly build-time, static, and hardware bring-up oriented:

- AMDGPU display code that includes `dce_12_0_offset.h` should compile without duplicate macro definitions or missing symbols.
- Static register-map checks should verify that every `mm...` macro has a matching `mm..._BASE_IDX` macro and that all base indices in this chunk remain `2`.
- Generator-diff checks should compare these offsets against AMD's authoritative DCE 12.0 register database and flag manual drift.
- Instance-pattern checks should confirm that `DC_COMBOPHYCMREGS[1-5]`, `DC_COMBOPHYTXREGS[1-5]`, and `DC_COMBOPHYPLLREGS[1-5]` expose the expected repeated register names with consistent per-instance spacing and the known PLL reserved hole.
- Hardware validation should cover display link bring-up on DCE 12.0 ASICs: connector detection, HPD/IRQ handling, AUX/DDC access, link training, mode set, suspend/resume, and hotplug after low-power states.
- Register readback or tracing during display initialization should show accesses landing in the expected PHY instance and lane when programming COMBOPHY common, TX, and PLL registers.
- Negative validation should ensure DCE 12.0 paths do not include or use similarly named DPCS `reg...` headers for these PHY registers.
