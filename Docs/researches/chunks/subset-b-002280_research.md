# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 51227-53595

## Purpose

This chunk is a generated AMD DPCS 3.1.4 shift/mask header slice for display PHY, GPIO, DDC/I2C, HPD, AUX-pad, and RDPCSTX link-transmitter register fields. It contains no executable C code. Its public surface is a set of preprocessor constants that describe field bit positions and masks for DCN 3.1.4 display hardware.

The requested range contains 2,164 `#define` entries: 1,077 `__SHIFT` constants and 1,087 `_MASK` constants. It starts inside the tail of `DCIO_SOFT_RESET`, covers the `dpcssys_dcio_dcio_chip_dispdec` GPIO/DDC/AUX register block, covers the first two RDPCSTX transmitter instances, and ends inside `RDPCSTX1_RDPCSTX_PHY_CNTL16`. The boundaries are artificial chunk boundaries: the soft-reset register begins before this range, and the RDPCSTX1 PHY generic-bus fields continue after it.

Although this file lives under a local `ceph-client` source mirror, this chunk is AMDGPU display-controller metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this range. The API contract is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: the field's least-significant bit position inside the register.
- `<REGISTER>__<FIELD>_MASK`: the field's bit mask inside the register.

The main register-field families in this chunk are:

- `DCIO_SOFT_RESET` tail: reset controls for UNIPHY A-G, DSYNC A-G, and power sequencer blocks 0 and 1. The chunk starts after several soft-reset shift definitions, so the full register is split with the previous chunk.
- `DC_GPIO_GENERIC_*`: generic GPIO A-G mask, pull-down disable, receiver mode, output value (`A`), output enable (`EN`), and input/readback (`Y`) fields, plus a generic strength selector.
- `DC_GPIO_DDC1` through `DC_GPIO_DDC5` and `DC_GPIO_DDCVGA`: DDC clock/data mask, pull-down, receive, AUX-pad mode, AUX polarity, hardware pull-down allowance, drive-strength, output value, output enable, and readback fields. These are the low-level pins used for DDC/I2C and AUX pad selection.
- `DC_GPIO_GENLK_*`: genlock/swaplock GPIO mask, pull-down, receive, output, enable, and readback fields for clock/sync/swaplock pins.
- `DC_GPIO_HPD_*`: HPD1-HPD6 mask, pull-down, receive, output, enable, and readback fields, plus HPD disconnect output-enable controls in `DC_GPIO_HPD_EN`.
- `DC_GPIO_PWRSEQ0_EN` and `DC_GPIO_PWRSEQ1_EN`: backlight, panel power, panel reset, Vary-BL, BLON, and OTG-vsync selection/enabling fields for display panel power sequencing.
- `DC_GPIO_PAD_STRENGTH_1` and `DC_GPIO_PAD_STRENGTH_2`: drive-strength selectors for generic, DDC, genlock, swaplock, HPD, and power-sequencer pads.
- `PHY_AUX_CNTL`, `DC_GPIO_AUX_CTRL_0` through `DC_GPIO_AUX_CTRL_5`, `DC_GPIO_RXEN`, `DC_GPIO_PULLUPEN`, and `AUXI2C_PAD_ALL_PWR_OK`: AUX/DDC/HPD pad wake, receiver select, slew, spike filter, bias/resistance tuning, HPD electrical tuning, receiver enable, pull-up enable, AUX polarity/termination/hysteresis, AUX VOD tuning, DDC I2C mode, DDC 1.2 V supply, pad I2C control, and per-AUX/I2C PHY power-good fields.
- `RDPCSTX0_*` and `RDPCSTX1_*`: two repeated RDPCS transmitter instances. Each exposes TX control, clocks, interrupt/error control, PLL update data, CR address/data windows, SRAM power controls, scratch/spare registers, PHY encoding and timing controls, DP-alt-mode handshakes, PHY resets, lane disable/request/ack/data-enable/status fields, MPLLB controls, lane equalization fuse fields, RX load-value readback, DMCU-reserved DP-alt controls, driver-access gating, regulator/capacitor bypass fields, REXT controls, and PHY generic bus fields.
- `DPCSSYS_CR0_DPCSSYS_CR_ADDR` and `DPCSSYS_CR0_DPCSSYS_CR_DATA`: system-level CR address/data field definitions that mirror the RDPCS TX CR access window.
- `DCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED0` through `...RESERVED57`: reserved 32-bit UNIPHY1 macro-control words, each exposed as a full-width reserved field.

The RDPCSTX0 and RDPCSTX1 blocks are intentionally similar. Instance 0 is the canonical name most shared link-encoder field-list macros use for shifts and masks, while per-instance register offsets select the actual transmitter instance.

## Control Flow

This header has no runtime control flow. It participates in compile-time register table construction:

1. `dcn314_resource.c` includes `dpcs_3_1_4_offset.h` and this matching `dpcs_3_1_4_sh_mask.h`.
2. Resource setup and hardware-object headers use token-pasting macros such as `REG`, `REGI`, `SRI`, `LE_SF`, `SF_DDC`, and `SF_HPD` to combine generated offset, shift, and mask names into typed register tables.
3. GPIO, DDC, HPD, AUX, and link-encoder objects receive those tables during DCN 3.1.4 resource construction.
4. Runtime helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` use the stored offsets, shifts, and masks to manipulate MMIO bitfields.

The macros in this chunk do not define sequencing. Reset ordering, DDC/AUX pin mode transitions, HPD polling/interrupt behavior, panel power sequencing, DP/HDMI PHY programming, PLL updates, DP-alt-mode handshakes, and FIFO startup are controlled by driver code and hardware rules outside this generated header.

## State And Persistence Behavior

The header stores no software state and persists nothing itself. It names hardware-visible state fields:

- DCIO reset state for UNIPHY, DSYNC, and power sequencer blocks.
- GPIO state for generic pins, DDC clock/data pins, VGA DDC pins, genlock/swaplock pins, HPD pins, power-sequencer pins, receiver enables, pull-ups, output values, output enables, input readback, pull-down controls, and pad strengths.
- AUX/DDC/HPD electrical state for pad wake, AUX receiver routing, slew/spike filters, compensation/bias/resistance controls, termination, polarity swap, hysteresis, VOD tuning, I2C-mode selection, pad supply enable, and per-pad power-good reporting.
- RDPCSTX transmitter state for soft resets, TX FIFO enables/start/read delay, lane bit/byte order, DP-alt block status, clock enables and clock-on readback, interrupt/error flags and masks, CR access state, SRAM power state, PHY reset/status, HDMI mode, reference range, RTUNE request/ack, SRAM init/load status, lane disable/request/ack/data-enable/clock-ready handshakes, MPLLB fractional/SSC/divider/state controls, transmitter equalization/fuse values, DCO tuning, VSWING, VREF, REXT, and generic debug/control busses.
- Driver-access arbitration fields for DP-alt-mode control blocks, including allow-driver-access and blocked status.

Persistence and side effects are hardware-defined. Many fields are configuration bits that retain values until modeset, power gating, suspend/resume, GPU reset, or ASIC reset rewrites them. Status, interrupt, pending, clear, request/ack, and power-good fields can be latched, self-clearing, write-one-to-clear, read-only, or valid only while the relevant display block is powered and clocked. This generated file only supplies bit locations; it does not encode access semantics.

## Dependencies And Integration Points

This generated file must remain synchronized with AMD's DPCS 3.1.4 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h` supplies the matching register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c` directly includes this header and constructs DCN 3.1.4 resource tables for link encoders, HPD, DDC, AUX, and related display hardware.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h` consumes `RDPCSTX0_*` shift/mask names for link-encoder fields including TX FIFO enables, RDPCS clocks, PHY lane disable/request/ack/reset controls, PHY reset/reference/SRAM status, interrupt masks, CR address/data, MPLLB controls, and DP TX equalization/fuse fields. The DCN 3.1.4 resource file pairs those common masks with per-instance RDPCSTX offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/ddc_regs.h` consumes `DC_GPIO_DDC1_*`, `PHY_AUX_CNTL__AUX*_PAD_RXSEL`, and `DC_GPIO_AUX_CTRL_5__DDC_PAD*_I2CMODE` fields for DDC/I2C pin tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hpd_regs.h` consumes `DC_GPIO_HPD_*` fields for HPD GPIO tables and combines them with HPD interrupt/toggle-filter registers outside this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_ddc.c` uses DDC mask fields and AUX-pad mode fields to switch pads between I2C/DDC behavior and AUX behavior.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_translate_dcn315.c` and related translator implementations map DDC and HPD register/mask pairs to GPIO pin identities; these are the style of consumers that rely on the generated `DC_GPIO_DDC*` and `DC_GPIO_HPD*` constants being consistent across ASIC generations.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/atomfirmware.h` documents firmware transmitter-adjustment fields that map to RDPCSTX PHY fuse/equalization and VBOOST/VSWING controls represented in this chunk.

Behaviorally, this chunk sits under connector bring-up and link operation: connector GPIO detection, EDID/DDC access, AUX pad routing, HPD sensing, panel power/backlight sequencing, and physical link transmitter programming for DP/HDMI/DP-alt-mode paths.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while only corrupting one hardware field at runtime.
- The file is generated. Manual edits risk divergence from the authoritative register database, the offset header, firmware assumptions, and silicon documentation.
- Chunk boundaries are not semantic. The first lines are only the tail of `DCIO_SOFT_RESET`, and the final lines stop inside `RDPCSTX1_RDPCSTX_PHY_CNTL16`. Adjacent chunk reports must be merged before making whole-register or whole-file claims.
- DDC and AUX share pads. Incorrect `AUX_PAD*_MODE`, `AUX*_PAD_RXSEL`, `DDC_PAD*_I2CMODE`, pull-down, pull-up, polarity, or termination masks can break EDID reads, DPCD/AUX traffic, link training, or connector detection only on selected ports.
- HPD fields are connector-visible and often noisy. Wrong mask/readback/enable definitions can cause missed hotplug events, repeated connect/disconnect flapping, or incorrect sense reporting.
- Power-sequencer GPIO fields are panel-sensitive. Incorrect Vary-BL, BLON, panel-power, panel-reset, or OTG-vsync selection masks can affect eDP panel power-up/down timing, backlight behavior, or suspend/resume.
- Pad-strength and AUX electrical tuning fields affect signal integrity. Bad values or bit definitions can produce marginal failures that depend on cable, sink, voltage rail, board routing, temperature, or link rate.
- RDPCSTX reset, clock, FIFO, request/ack, and lane-enable fields are sequencing-sensitive. Incorrect masks can create hangs waiting for clock-on or ack bits, TX FIFO underflow/overflow, blank displays, or lane-count-specific failures.
- RDPCSTX interrupt-control names include status, clear, and mask fields in one register. Confusing `*_MASK` field names with generated `_MASK` suffixes or writing the wrong clear bit can hide FIFO/reg errors or leave errors latched.
- RDPCSTX PHY fuse/equalization fields map to firmware transmitter settings. Wrong masks for `EQ_MAIN`, `EQ_PRE`, `EQ_POST`, MPLLB tuning, DCO range/fine tune, VSWING, VREF, or REXT can cause link-training failures or intermittent high-rate DP/HDMI issues.
- Instance repetition is copy-sensitive. RDPCSTX0 and RDPCSTX1 should be structurally aligned where hardware intends; an instance-specific generator error can affect only one physical transmitter.
- The reserved UNIPHY1 macro-control fields expose full-width registers. Treating reserved fields as safe software controls would be risky unless explicitly required by silicon documentation or firmware handoff rules.

## Test Signals

Useful validation combines generated-header consistency checks with runtime display behavior:

- Build DCN 3.1.4 AMDGPU display support. Missing or renamed macros should surface in `dcn314_resource.c`, `dcn31_dio_link_encoder.h`, `ddc_regs.h`, `hpd_regs.h`, and GPIO translator users.
- Mechanically compare this range against the authoritative DPCS 3.1.4 register-field database and ensure every expected `_MASK` has a paired `__SHIFT`, allowing fields split by chunk boundaries.
- Cross-check this shift/mask range against `dpcs_3_1_4_offset.h` so every register family in the chunk has matching offsets/base indices.
- Run static repetition checks across `DC_GPIO_DDC1-5`, `DC_GPIO_DDCVGA`, `DC_GPIO_HPD1-6`, `AUX1-6` pad fields, and `RDPCSTX0/1` to catch unintended instance drift while allowing intentional per-instance or VGA differences.
- Exercise EDID reads and DDC transactions on every connector. Watch for stuck pull-downs, wrong pad mode, bad DDC clock/data direction, failed I2C-mode selection, or port-specific failures.
- Exercise DP AUX/DPCD reads and link training on every AUX-capable connector, including unplugged and timeout paths. Expected signals are correct AUX pad routing, stable power-good status, and no cross-connector aliasing.
- Exercise HPD connect/disconnect and HPD sense/readback across all exposed connectors. Expected signals are stable sense bits, correct GPIO mapping, and no repeated interrupts from bad mask/readback definitions.
- Validate panel power and backlight sequencing on internal-panel platforms, including boot, modeset, blank/unblank, suspend/resume, and fast display switching.
- Exercise DP/HDMI link bring-up across lane counts and link rates. Watch for TX FIFO errors, stuck clock-on/status bits, request/ack timeout, lane-disable mistakes, and link-training regressions.
- Compare RDPCSTX PHY/equalization programming against AtomBIOS/firmware transmitter settings and hardware register dumps, especially for high-rate DP, HDMI FRL/TMDS-adjacent paths when applicable, and marginal cables/sinks.
- Test DP-alt-mode or USB-C display paths where present, focusing on `DPALT_DISABLE`, `DPALT_DP4`, driver-access gating, and DMCU-reserved DP-alt handshake fields.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DCIO_SOFT_RESET`, including shift definitions before `DSYNCG_SOFT_RESET`. This chunk covers the corresponding soft-reset masks and then the DCIO GPIO/pad and RDPCSTX0/1 register groups. The next chunk should continue `RDPCSTX1_RDPCSTX_PHY_CNTL16` and the remaining DPCS register metadata. The final per-file research document should reconcile these boundaries before describing all DPCS 3.1.4 GPIO, AUX, HPD, UNIPHY, or RDPCSTX behavior.
