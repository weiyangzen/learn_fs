# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 1-2386

## Purpose

This chunk is the opening slice of the generated AMD DPCS 4.2.3 shift/mask header. It contains the copyright/license prologue, include guard, and preprocessor constants that describe bit positions and masks for early DPCS display register blocks. There is no executable C logic here; the file's role is to provide compile-time register-field metadata for AMDGPU display code that programs the DisplayPort/PHY control system.

The requested range contains 2,386 source lines and 2,160 `#define` entries: 1,080 `__SHIFT` constants and 1,079 `_MASK` constants, plus the include guard. The shift/mask count is intentionally unbalanced in this chunk because line 2386 ends immediately after `RDPCSTX3_RDPCSTX_CLOCK_CNTL__RDPCS_EXT_REFCLK_EN__SHIFT`; the matching mask and the rest of `RDPCSTX3_RDPCSTX_CLOCK_CNTL` continue in a later chunk.

Although the repository path is under a local `ceph-client` source tree, this header is AMDGPU display hardware metadata. It does not implement Ceph, filesystem, networking, or distributed-storage behavior.

## Important APIs, Types, And Macros

This range exports only preprocessor macros. It defines no functions, structs, enums, global variables, inline helpers, includes, locks, memory allocation, or direct MMIO access. The naming convention is the public interface:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position of a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask used by AMD register helpers to extract or compose the value.

The register families covered in this chunk are:

- `DPCSSYS_CR0_DPCSSYS_CR_ADDR` / `DATA` through `DPCSSYS_CR4_DPCSSYS_CR_ADDR` / `DATA`: indirect CR address/data windows for five DPCS CR instances. Each address and data field is a 16-bit `RDPCS_TX_CR_*` value.
- `PWRSEQ0_*` and `PWRSEQ1_*`: two panel power-sequencer and backlight PWM register sets. The repeated fields cover GPIO power-sequence enable/control/mask/readback for `VARY_BL`, `DIGON`, and `BLON`; panel sequence control and state; power-up/down delay programming; reference dividers; PWM active count, period, fractional/enable bits, update timing, lock control, and spare fields.
- `RDPCSTX0_*`, `RDPCSTX1_*`, and `RDPCSTX2_*`: complete repeated RDPCS transmitter register groups for three links/PHY instances.
- `RDPCSTX3_RDPCSTX_CNTL`: the complete top-level control register for the fourth transmitter group.
- `RDPCSTX3_RDPCSTX_CLOCK_CNTL`: only the first shift definition is included at the chunk boundary.

The RDPCSTX groups expose dense field definitions for:

- Core transmitter control: CBUS/SRAM/TX soft reset, interrupt mask, PLL update request/pending, FIFO lane enables, FIFO start/read delay, lane bit-order reverse, lane pack order, CR/non-DPALT register block enables, and DPALT block status.
- Clock and interrupt control: external reference clock, reference clock source selection, PLL update clock domain controls, clock enables/resets/ready status, interrupt type/status/ack bits, ACK mask overrides, and per-lane AFE ready interrupt handling.
- CR/SRAM/debug/pll-update access: PLL update data, TX CR address/data, SRAM test/run address and write data, scratch/spare registers, debug compare/write-enable controls, and DMCU DPALT disable-block controls.
- PHY control registers `PHY_CNTL0` through `PHY_CNTL17`: lane and common PHY control for DP TX lanes 0-3, common resets, disable/enable handshakes, clock/data enables, P-state and MPLL enable fields, DPALT disable/ack/ref-clock controls, vreg bypass, generic in/out buses, debug muxing, and lane load values.
- PHY fuse registers `PHY_FUSE0` through `PHY_FUSE3`: per-lane and common fuse-style values for TX margining, voltage/regulator, deemphasis, predriver, resistor, tune, data-rate, RTUNE, and supplementary settings.
- DPALT and diagnostics: `DMCU_DPALT_PHY_CNTL3`, `DMCU_DPALT_PHY_CNTL6`, `DPALT_CONTROL_REG`, `DEBUG_CONFIG`, and `DEBUG_CONFIG2` expose reserved DMCU/DPALT handshakes, driver-access gating, debug source selection, compare selection, and valid-bit replacement.
- Byte-order and PLL update overrides: `RDPCS_CNTL3`, `RDPCS_TX_PLL_UPDATE_ADDR_OVRRD`, and `RDPCS_TX_PLL_UPDATE_DATA_OVRRD` describe per-lane byte-order change fields and override address/data payloads.

Most fields are 32-bit register fields with an `L`-suffixed hexadecimal mask. The CR address/data windows use 16-bit masks, while some PLL update payloads use full-width `0xFFFFFFFFL` masks.

## Control Flow

This header has no runtime control flow. It participates in AMDGPU display control indirectly:

1. Version-specific AMD display code includes the DPCS 4.2.3 offset header and this shift/mask header.
2. Generated register table macros token-paste register names, shifts, and masks into hardware description structures.
3. Runtime code uses register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, or `REG_UPDATE` against those structures.
4. The actual sequencing for panel power, backlight PWM, link encoder setup, PHY reset, PLL update, DPALT access, FIFO enablement, interrupt acknowledgement, and debug sampling lives in the display driver code that consumes these constants.

The constants do not describe access type, reset values, write-one-to-clear behavior, self-clearing bits, required polling order, clock-domain constraints, timing delays, or reserved-bit preservation rules. Those semantics must come from the hardware programming code and ASIC documentation.

## State And Persistence Behavior

This chunk stores no software state and persists nothing itself. It names hardware-visible state in several DPCS register blocks:

- The CR address/data windows select and transfer indirect RDPCS TX CR register addresses and payloads. Their visible state is whatever address/data pair the driver or firmware last placed into the indexed CR window.
- `PWRSEQ0` and `PWRSEQ1` contain panel and backlight state: GPIO enables, pull-up/receiver/mask controls, DIGON/BLON/SYNCEN override and polarity bits, target power state, sequencer done/current-state readback, programmed power-up/down delays, reference dividers, PWM period/active count, PWM enable/fractional mode, update delay, lock bits, and spare state.
- Each complete `RDPCSTX0`-`RDPCSTX2` block contains transmitter state for resets, lane FIFO enablement, PLL update handshakes, clock gates, reference clock source/enable state, interrupt status/acknowledgement, SRAM/CR access, PHY lane control, DPALT access, DMCU-reserved handshakes, PHY fuses, debug routing, byte-order selection, and PLL update override values.
- The partial `RDPCSTX3` coverage includes its high-level transmitter control state but only the opening shift for its clock-control register.

Persistence is hardware-defined. Programmed configuration fields generally last until a modeset/link reprogram, panel power transition, PHY power-gating event, suspend/resume, GPU reset, ASIC reset, firmware intervention, or driver reinitialization changes them. Status and handshake fields such as PLL update pending, clock ready, interrupt status, AFE ready, DPALT access blocked, and panel sequencer done may be latched, sampled, self-clearing, or valid only while the associated power or clock domain is active. This header does not encode those lifetime rules.

## Dependencies And Integration Points

This file must remain synchronized with AMD's DPCS 4.2.3 register database and the matching offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h` supplies the corresponding `reg...` offsets and base indices.
- The offset header maps the CR windows to base-indexed display registers such as `regDPCSSYS_CR0_DPCSSYS_CR_ADDR` through `regDPCSSYS_CR4_DPCSSYS_CR_DATA`.
- The two power sequencer blocks map to `regPWRSEQ0_*` around `0x2f10` and `regPWRSEQ1_*` around `0x2f7c`.
- The RDPCSTX groups are repeated with regular per-instance offset spacing: `RDPCSTX0` starts around `0x2930`, `RDPCSTX1` around `0x2a08`, `RDPCSTX2` around `0x2ae0`, and `RDPCSTX3` around `0x2bb8`.

Likely consumers are AMD Display Core register tables, link encoder code, PHY programming paths, panel/backlight power-sequence code, DisplayPort/HDMI link bring-up and teardown, suspend/resume reinitialization, interrupt handlers, and diagnostic register-dump/debug paths. Firmware or DMCU-controlled DPALT flows may also coordinate with these registers through the driver-access and reserved handshake fields.

Behaviorally, this header sits below user-facing display APIs. It gives higher-level AMDGPU code the bit layout needed to safely write display PHY and panel-control registers for DPCS 4.2.3 hardware.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile successfully while setting the wrong hardware field, dropping a status bit, corrupting a neighboring field, or accidentally touching a reserved bit.
- The file is generated metadata. Manual edits can diverge from AMD's authoritative register database, the companion offset header, firmware expectations, or silicon documentation.
- The RDPCSTX blocks are repetitive and copy-sensitive. `RDPCSTX0`, `RDPCSTX1`, and `RDPCSTX2` should keep matching layouts where the hardware repeats the transmitter block; a generator or merge error in one instance may only fail on the affected link/PHY.
- The chunk boundary is inside a register. `RDPCSTX3_RDPCSTX_CLOCK_CNTL` has only `RDPCS_EXT_REFCLK_EN__SHIFT` in this range, so any per-register analysis must be reconciled with the following chunk before treating that register as complete.
- Power-sequencer masks can affect panel safety and user-visible behavior. Incorrect DIGON/BLON/SYNCEN polarity, override, delay, reference-divider, PWM enable, or lock masks could produce black screens, bad brightness control, or incorrect panel power timing.
- PHY and clock-control fields are link-critical. Bad masks for resets, clock enables, clock ready, PLL update, FIFO start, lane enable, DPALT disable, or MPLL/P-state fields could cause link-training failures, stuck lanes, or failures after resume.
- Interrupt and ACK fields require semantic care outside this header. The macro names alone do not identify whether bits are write-one-to-clear, level-triggered, latched, masked, or sourced from a separate clock domain.
- DPALT and DMCU reserved fields are risky to interpret from names alone. Several fields are marked `RESERVED` but still have masks; consumers must preserve or program them according to hardware/firmware rules rather than assuming ordinary driver-owned state.
- Fuse and analog PHY fields can be board-, ASIC-, or stepping-sensitive. Misdecoding voltage, deemphasis, predriver, RTUNE, data-rate, or margin fields can lead to subtle electrical failures instead of immediate compile-time or boot failures.

## Test Signals

Useful validation combines generated-header consistency checks with display hardware behavior:

- Build AMDGPU display support for the ASIC generation using DPCS 4.2.3. Missing or renamed macros should fail during versioned register table initialization.
- Mechanically verify that each complete field in lines 1-2386 has both a `__SHIFT` and `_MASK`, with the known exception that `RDPCSTX3_RDPCSTX_CLOCK_CNTL` is split at the chunk end.
- Cross-check register names and block repetition against `dpcs_4_2_3_offset.h`, especially the CR0-CR4 windows, `PWRSEQ0`/`PWRSEQ1`, and repeated `RDPCSTX0`-`RDPCSTX3` offsets.
- Diff this generated DPCS 4.2.3 header against AMD's source register database and nearby generated DPCS variants where the layout should be identical or intentionally changed.
- Exercise panel power on/off, backlight enable/disable, brightness changes, PWM updates, and lock/unlock paths. Expected signals are correct DIGON/BLON sequencing, stable PWM period/active values, and no unexpected panel power-state stalls.
- Exercise DisplayPort/HDMI link bring-up, hotplug, modeset, stream disable/enable, suspend/resume, and GPU reset across available PHY lanes. Expected signals are stable link training, no stuck PLL update pending bits, expected FIFO/lane enables, and clock-ready/interrupt status that decodes correctly.
- Use register dumps around failing links to confirm masks decode RDPCSTX control, clock, interrupt, PHY control, DPALT, fuse, debug, and PLL update override fields correctly for each instance.
- Validate diagnostic/debug paths that use scratch/spare, debug compare/source selection, generic PHY in/out buses, DMCU DPALT handshakes, and driver-access gates, because these fields may not be exercised by ordinary display modesets.

## Cross-Chunk Notes

This is the first chunk of `dpcs_4_2_3_sh_mask.h`, so it owns the file prologue, include guard, CR0-CR4 address/data window masks, both PWRSEQ blocks, all of `RDPCSTX0`, `RDPCSTX1`, and `RDPCSTX2`, and the beginning of `RDPCSTX3`. The next chunk should continue from `RDPCSTX3_RDPCSTX_CLOCK_CNTL` and provide the matching mask plus the remaining RDPCSTX3 register definitions.
