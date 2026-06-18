# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_2_0_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002247`: lines 1-2378, `Docs/researches/chunks/subset-b-002247_research.md`
- `subset-b-002248`: lines 2379-3912, `Docs/researches/chunks/subset-b-002248_research.md`

## Chunk Research

### subset-b-002247: lines 1-2378

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_2_0_0_sh_mask.h lines 1-2378

## Scope

This chunk covers the beginning of the generated AMD DPCS 2.0.0 shift/mask header through line 2378. It includes the license/header guard and the DPCS transmit, retimed DPCS transmit, and CR access bitfield definitions for DPCSTX/RDPCSTX instances 0, 1, and 2, plus the start of instance 3 through the `RDPCSTX3_RDPCSTX_PHY_CNTL11` shifts. The file continues after this chunk, so receive-side `DPCSRX` definitions and later parts of RDPCSTX3/instances 4-5 are intentionally out of scope here.

## Purpose

`dpcs_2_0_0_sh_mask.h` is a generated hardware register bitfield contract for DCN 2.0 DPCS blocks. Each field is represented as paired preprocessor constants:

- `...__SHIFT`: the bit offset for a register field.
- `..._MASK`: the masked bit range for that field.

The companion offset header supplies register addresses, while this header supplies the field layout used by AMD display register helper macros to build typed register/field tables. It does not implement logic itself; it gives higher-level display code stable names for clock, FIFO, PHY, PLL, DP-alt-mode, interrupt, SRAM, fuse, and debug controls.

## Chunk Inventory

Within lines 1-2378 the chunk has 11 `addressBlock` sections, 163 register comment groups, 2161 `#define`s, 1082 shift definitions, and 1078 mask definitions. The covered address blocks are:

- `dpcssys_dpcs0_dpcstx0_dispdec`
- `dpcssys_dpcs0_rdpcstx0_dispdec`
- `dpcssys_dpcssys_cr0_dispdec`
- `dpcssys_dpcs0_dpcstx1_dispdec`
- `dpcssys_dpcs0_rdpcstx1_dispdec`
- `dpcssys_dpcssys_cr1_dispdec`
- `dpcssys_dpcs0_dpcstx2_dispdec`
- `dpcssys_dpcs0_rdpcstx2_dispdec`
- `dpcssys_dpcssys_cr2_dispdec`
- `dpcssys_dpcs0_dpcstx3_dispdec`
- `dpcssys_dpcs0_rdpcstx3_dispdec` through `RDPCSTX3_RDPCSTX_PHY_CNTL11`.

The repeated per-link shape is the main design signal. For each full link instance in this chunk, `DPCSTXn` exposes seven high-level transmitter/control register groups, `RDPCSTXn` exposes 35 retimer/PHY-oriented register groups, and `DPCSSYS_CRn` exposes two indexed CR address/data groups. Instance 3 is partial in this chunk because the mapped line range ends mid-register.

## Important APIs, Types, and Register Groups

There are no C functions, structs, or enums in this header. Its API is the macro namespace consumed by register-table initializers and `REG_*` helpers.

Important `DPCSTXn` groups:

- `DPCSTX_TX_CLOCK_CNTL`: symbol clock gating/enabling and clock-on status (`DPCS_SYMCLK_GATE_DIS`, `DPCS_SYMCLK_EN`, `DPCS_SYMCLK_CLOCK_ON`, `DPCS_SYMCLK_DIV2_CLOCK_ON`).
- `DPCSTX_TX_CNTL`: PLL update request/pending bits, data swap/order inversion, FIFO enable/start/read-delay, and TX soft reset.
- `DPCSTX_CBUS_CNTL`: CBUS write-command delay and soft reset.
- `DPCSTX_INTERRUPT_CNTL`: register FIFO overflow, per-lane TX FIFO errors, clear bits, and interrupt masks.
- `DPCSTX_PLL_UPDATE_ADDR` / `DPCSTX_PLL_UPDATE_DATA`: indirect PLL update address/data payloads.
- `DPCSTX_DEBUG_CONFIG`: debug mux enable/select fields and test-debug write enable.

Important `RDPCSTXn` groups:

- `RDPCSTX_CNTL`: CBUS/SRAM/TX soft reset, per-lane FIFO enable, FIFO start/read-delay, CR register block enable, non-DP-alt register block enable, and DP-alt block status.
- `RDPCSTX_CLOCK_CNTL`: external refclock, per-lane symclk-div2 enables, SRAM clock gating/enabling/status, and SRAM clock bypass.
- `RDPCSTX_INTERRUPT_CONTROL`: register FIFO overflow, DP-alt disable/4-lane toggles, per-lane TX FIFO errors, clear bits, and mask bits.
- `RDPCS_TX_CR_ADDR` / `RDPCS_TX_CR_DATA` and `DPCSSYS_CRn_DPCSSYS_CR_ADDR/DATA`: 16-bit CR address/data windows.
- `RDPCS_TX_SRAM_CNTL`, `RDPCSTX_MEM_POWER_CTRL`, and `RDPCSTX_MEM_POWER_CTRL2`: memory power disable/force/state, fuse repair fields, power-collapse/isolation controls, and SRAM low-voltage-min disable.
- `RDPCSTX_DMCU_DPALT_DIS_BLOCK_REG`, `RDPCSTX_DMCU_DPALT_PHY_CNTL3`, `RDPCSTX_DMCU_DPALT_PHY_CNTL6`, and `RDPCSTX_DPALT_CONTROL_REG`: DP-alt-mode access arbitration and DMCU-reserved overrides for PHY lane reset/disable/ready/request/ack and P-state/MPLL/refclk controls.
- `RDPCSTX_PHY_CNTL0` through `PHY_CNTL14` for full instances 0-2: PHY reset, TCA/APB reset, HDMI mode, ref-range, VBOOST, retune request/ack, reference clock detection, SRAM init/load status, power gating, loopback, lane reset/disable/data-enable/request/ack, termination/invert/EQ bypass/high-protection, lane LPD/rate/width/detect-rx, per-lane P-state/MPLL, DP-alt mode and refclk control, MPLLB fractional-N, SSC, multiplier/divider/state/calibration controls.
- `RDPCSTX_PHY_FUSE0` through `PHY_FUSE3` and `PHY_RX_LD_VAL`: per-lane equalization fuse values plus MPLLB/DCO and RX load values.

The line-range boundary matters: line 2378 ends just before the first `RDPCSTX3_RDPCSTX_PHY_CNTL11` mask, so this chunk records the shifts for `RDPCSTX3_PHY_CNTL11` but not the matching masks or later RDPCSTX3 groups.

## Control Flow and State

This header has no runtime control flow. The effective control flow is compile-time macro expansion:

1. A DCN 2.0 resource file includes `dpcs_2_0_0_offset.h` and this shift/mask header.
2. Register-list macros such as `DPCS_DCN2_REG_LIST(id)` map logical link-encoder fields to per-instance MMIO addresses from the offset header.
3. Shift/mask-list macros such as `DPCS_DCN2_MASK_SH_LIST(__SHIFT)` and `DPCS_DCN2_MASK_SH_LIST(_MASK)` expand this header's field constants into `dcn10_link_enc_shift` and `dcn10_link_enc_mask` tables.
4. Link encoder code uses `REG_GET`, `REG_UPDATE`, and related helpers against those tables, so the masks here directly determine which hardware bits are read or modified.

The state represented by these macros is all hardware state: clock gates, FIFO starts/status, interrupt latch/mask bits, DP-alt-mode handshakes, PLL programming windows, SRAM power state, PHY power/reset/training settings, fuse calibration values, and debug mux settings. The header does not persist software state and does not allocate memory. Persistence is in device registers across the lifetime of the hardware block, subject to reset and power management.

## Dependencies and Integration Points

Primary dependency:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_2_0_0_offset.h` for the matching MMIO register addresses/base indices.

Observed integration:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c` includes this header and uses `DPCS_DCN2_REG_LIST(id)`, `DPCS_DCN2_MASK_SH_LIST(__SHIFT)`, and `DPCS_DCN2_MASK_SH_LIST(_MASK)` to initialize DCN 2.0 link encoder register, shift, and mask tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_link_encoder.h` declares the DPCS-related register field list that expects fields present here, including MPLLB controls, lane rate/width, clock gates, FIFO delays, DP-alt controls, fuse/equalization fields, and debug configs.
- Later ASIC generations have parallel DPCS shift/mask headers (`dpcs_2_0_3`, `dpcs_2_1_0`, `dpcs_3_0_0`, etc.), so this file is part of a generated family where field names are kept stable when hardware layout allows.

## Risks

- Bitfield accuracy is critical. A wrong shift or mask can silently write adjacent hardware fields, causing display link bring-up failures, PHY instability, power-management regressions, or interrupt storms.
- The repeated per-instance definitions are easy to update inconsistently. Instance 0-2 definitions are complete in this chunk, while instance 3 is split across chunks; reconciliation must not infer completeness from this document alone.
- Several registers contain request/ack or status/control pairs (`PLL_UPDATE_REQ/PENDING`, lane `REQ/ACK`, `DPALT_DISABLE/ACK`, clock enable/status bits). Driver code must preserve required sequencing and polling; this header only names the bits.
- Mask names such as `...ERROR_MASK_MASK` are generated from fields already named `*_MASK`. They are awkward but intentional; manual cleanup would break expected macro names.
- DMCU/DP-alt reserved fields expose ownership boundaries between firmware/display microcontroller and driver. Writing reserved override masks from the wrong path can conflict with firmware-managed link state.
- Since this is a generated hardware contract, hand-editing is high risk. Any changes should come from the register database/generator or be reviewed against hardware documentation.

## Test Signals

Useful validation for this chunk is mostly build-time and hardware smoke coverage:

- Compile a DCN 2.0 AMDGPU configuration. This catches missing/misspelled `__SHIFT` and `_MASK` symbols used by `DPCS_DCN2_MASK_SH_LIST`.
- Ensure `dcn20_resource.c` still initializes `link_enc_regs`, `le_shift`, and `le_mask` without duplicate or absent fields.
- On hardware or emulator, exercise DP/HDMI link bring-up, link training at multiple rates/lane counts, hotplug, suspend/resume, and display mode changes. Failures would implicate clock, FIFO, PLL, PHY, and DP-alt fields defined here.
- Watch kernel logs and debug counters for DPCS FIFO/register errors, DP-alt toggle interrupts, stuck PLL update pending bits, missing clock-on status, and PHY request/ack timeouts.
- Compare generated shifts/masks against adjacent ASIC headers only as a sanity check; differences may be legitimate hardware-version changes, so the authoritative check is the DCN 2.0 register specification/generator output.

### subset-b-002248: lines 2379-3912

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_2_0_0_sh_mask.h lines 2379-3912

## Scope And Purpose

This chunk is the final large slice of the generated AMD DPCS 2.0.0 shift/mask header. It contains C preprocessor constants that describe bit positions and bit masks for DisplayPort/USB-C PHY control registers in the AMD display controller stack. The constants are consumed with the matching DPCS offset header by DCN 2.0 display-resource code, including `drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`, which includes both `dpcs/dpcs_2_0_0_offset.h` and this `dpcs/dpcs_2_0_0_sh_mask.h`.

The chunk starts in the middle of the `RDPCSTX3` register family, covering the tail of its MPLLB and PHY fuse fields, then defines the CR address/data window for TX3, the shared DPCSRX receiver-side block, and complete TX4/TX5 DPCSTX plus RDPCSTX register families. These macros are not executable logic; they are a register contract between AMD DC code and the DPCS hardware register map. Their purpose is to let higher-level register helper macros set, clear, and extract precise fields without embedding numeric bit positions throughout the driver.

The dominant hardware areas represented here are TX/RX clocking, FIFO enable/start/error controls, CBUS access delays, PLL-update staging, PHY lane reset/disable/request/ack state, DisplayPort alternate-mode ownership bits, PHY power-gating state, MPLLB fractional and spread-spectrum parameters, lane equalization fuse data, and indirect CR address/data windows.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or exported runtime APIs in this chunk. The public surface is entirely `#define` constants using the generated AMD naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field lsb position.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.

The chunk contains several distinct macro families:

- `RDPCSTX3_RDPCSTX_PHY_CNTL12` through `RDPCSTX3_RDPCSTX_DPALT_CONTROL_REG`: tail fields for TX3, including MPLLB divider/state/SSC controls, MPLLB fractional mode and calibration bits, lane equalization fuse fields, DCO trim/range fuses, RX load values, reserved DMCU DP-alt PHY controls, and driver-access arbitration.
- `DPCSSYS_CR3_DPCSSYS_CR_ADDR` and `DPCSSYS_CR3_DPCSSYS_CR_DATA`: 16-bit indirect CR address/data fields for the TX3 CR window.
- `DPCSRX_*`: shared DPCS receiver-side controls, including PHY reset, symbol-clock gating/enable/status, lane/FIFO enable, FIFO read-start delay, CBUS delay/reset, register and RX FIFO error status/clear/mask bits, index-mode address/data, and debug selection fields.
- `DPCSTX4_DPCSTX_*` and `DPCSTX5_DPCSTX_*`: non-RDPCS TX-side fields for TX4/TX5, covering symbol clock enable/status, PLL update request/pending, data swap/order inversion, FIFO controls, CBUS write delay/reset, interrupt status/masks, PLL update indirect address/data, and debug clock/select fields.
- `RDPCSTX4_*` and `RDPCSTX5_*`: replicated RDPCS-side TX4/TX5 control blocks with FIFO/lane control, clocks, interrupt control, PLL update data, CR address/data, SRAM/memory power, scratch, DMCU DP-alt disable block, debug counters/selectors, PHY control registers 0-14, PHY fuse registers 0-3, RX load values, reserved DMCU DP-alt PHY controls, and DP-alt driver-access control.
- `DPCSSYS_CR4_*` and `DPCSSYS_CR5_*`: 16-bit indirect CR address/data fields for the TX4 and TX5 CR windows.

The low-level integration convention is that callers combine these constants with matching register offsets and helper macros, commonly in the AMD display code through `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_SET_2`, and related register-helper patterns. A mask/shift pair here is therefore an ABI-like dependency for generated register access code.

## Control Flow

This chunk has no runtime control flow. It is a declarative register layout. The effective control flow appears in consumers: driver code reads or writes a memory-mapped DPCS register, uses the `*_MASK` and `*__SHIFT` constants to isolate or place a field, and then waits for corresponding status bits when the field is part of a hardware handshake.

Several implicit hardware sequences are visible from the field names:

- PHY power and reset sequencing uses fields such as `RDPCS_PHY_RESET`, `RDPCS_PHY_TCA_PHY_RESET`, `RDPCS_PHY_TCA_APB_RESET_N`, `RDPCS_PHY_PCS_PWR_EN`, `RDPCS_PHY_PCS_PWR_STABLE`, `RDPCS_PHY_PMA_PWR_EN`, `RDPCS_PHY_PMA_PWR_STABLE`, `RDPCS_PHY_ANA_PWR_EN`, and `RDPCS_PHY_ANA_PWR_STABLE`.
- Lane bring-up and teardown use per-lane groups in `PHY_CNTL3`, `PHY_CNTL5`, and `PHY_CNTL6`: reset, disable, clock-ready, data-enable, request/ack, rate, width, detect-RX request/result, P-state, MPLL enable, DP-alt disable/ack, and reference-clock request/enable.
- FIFO data path setup uses TX/RX lane enable bits, FIFO enable bits, FIFO start bits, and read-start delay fields. Error status and clear bits in interrupt/status registers indicate when FIFO or register access sequencing failed.
- PLL programming is represented by PLL-update request/pending fields, indirect PLL update address/data fields, and RDPCS MPLLB controls for fraction denominator/quotient/remainder, SSC peak/stepsize/up-spread, multiplier, HDMI dividers, reference-clock dividers, TX clock divider, fractional enable, calibration force, and PMIX enable.
- DP-alt mode ownership uses `RDPCS_ALLOW_DRIVER_ACCESS`, `RDPCS_DRIVER_ACCESS_BLOCKED`, `RDPCS_DPALT_DISABLE`, `RDPCS_DPALT_DISABLE_ACK`, `RDPCS_DPALT_DP4`, DMCU reserved shadow fields, and DP-alt disable/toggle interrupt bits.

Because all of this is macro data, sequencing correctness depends on the code that writes the registers, but the macro values define the only bit positions those sequences can legally use for this ASIC generation.

## State And Persistence Behavior

The header itself keeps no software state and persists nothing. Its constants describe state that lives in hardware registers. State represented by this chunk includes:

- Reset and power state: PHY reset bits, SRAM reset, CBUS reset, TX/RX soft reset, PCS/PMA/analog power enables, and corresponding stable/done/status bits.
- Clock state: symbol-clock gate disable, enable, selector, and clock-on bits for DPCSRX and TX4/TX5, plus RDPCS ext-refclk, per-lane div2 clocks, SRAM clock enable/status, and bypass controls.
- FIFO and error state: TX/RX FIFO enables, lane enables, start flags, read-start delays, FIFO overflow/error bits, error clear bits, and error mask bits.
- PHY lane state: per-lane TX reset/disable/clock-ready/data-enable/request/ack, loopback, termination, inversion, low-power disable, rate, width, detect-RX request/result, P-state, and MPLL enable.
- Calibration and fuse-backed state: equalization main/pre/post fuses for each lane, MPLLB charge-pump and VCO/frequency trims, DCO fine-tune/range, RX reference/VCO load values, and SRAM/memory power fuse fields.
- Debug and scratch state: async/debug selectors, CR counters, test clock selections, test-debug write enable, scratch registers, and indirect index-mode/CR address-data registers.

Any persistence is hardware or firmware owned. Some fields are fuse-derived or describe SRAM power/fuse repair settings, so incorrect mask definitions can corrupt hardware initialization paths even though this file itself does not write those values.

## Dependencies And Integration Points

This chunk depends on the companion generated register-offset header for DPCS 2.0.0. A mask/shift macro only becomes actionable when paired with an offset such as the corresponding `mm...` register constant from `dpcs_2_0_0_offset.h`. The full DCN 2.0 resource code includes both files, alongside `dcn/dcn_2_0_0_offset.h`, `dcn/dcn_2_0_0_sh_mask.h`, and other ASIC-specific register maps.

The direct integration point in this repository is AMDGPU DC display bring-up for Navi/DCN 2.0-class hardware under `drivers/gpu/drm/amd/display`. Register helper code turns these definitions into read-modify-write operations. The naming also aligns with neighboring generated versions such as `dpcs_2_1_0_sh_mask.h`, `dpcs_3_0_0_sh_mask.h`, and later `dpcs_4_2_x` headers, so ASIC-version selection is an important integration boundary.

Hardware integration points visible in this chunk include:

- DPCSRX receiver-side datapath and debug registers.
- DPCSTX4/TX5 non-RDPCS TX datapath registers.
- RDPCSTX3/TX4/TX5 replicated PHY/register access blocks.
- DPCSSYS CR3/CR4/CR5 indirect CR address/data windows.
- DMCU/DP-alt coordination fields that arbitrate access between driver, firmware/display microcontroller, and alternate-mode control logic.
- MPLLB clock-generation programming shared by DP and HDMI timing paths.

The chunk is in a Ceph-client source tree mirror, but functionally it belongs to the Linux AMDGPU DRM display driver, not to Ceph filesystem logic.

## Risks And Edge Cases

The highest risk is silent hardware misprogramming from an incorrect mask or shift. A one-bit error can put a requested field into a neighboring control bit, causing display link training failures, hangs while waiting for `*_ACK`, lost clock enables, incorrect FIFO timing, or failed power sequencing.

The TX4 and TX5 blocks are nearly identical by construction. That duplication makes manual edits risky: a fix applied to one replicated family but not the other could produce connector-dependent failures that appear only on specific link encoders or PHY instances. The TX3 tail also has the same late PHY and DP-alt fields as TX4/TX5, but the chunk boundary starts after earlier TX3 fields, so cross-chunk reconciliation must preserve continuity.

Several field names include `_RESERVED` in the DMCU DP-alt PHY control registers. Even though masks are defined, consumers should treat them as hardware/firmware-reserved unless an ASIC programming guide or existing driver code explicitly requires access. Writing reserved fields can break firmware-driver ownership assumptions.

The DPCSRX error fields use names such as `DPCS_REG_FIFO_ERROR_MASK_MASK` and `DPCS_RX_FIFO_ERROR_MASK_MASK`. This generated double-`MASK` naming is intentional because the hardware field itself is named `..._MASK`; downstream code must not "clean up" those macro names or it will break generated register-helper references.

The indirect CR and index-mode address/data registers expose 16-bit or 18-bit address windows and 16-bit/32-bit data windows. Bad mask use around these fields can redirect indirect operations to the wrong PHY subregister, which is harder to diagnose than a direct MMIO bit mistake.

ASIC-version drift is another risk. Later DPCS headers have similar macro names but different bit layouts for some fields. Code compiled against DPCS 2.0.0 must use this header with the matching offsets and resource tables; mixing masks across ASIC generations can compile cleanly while programming the wrong hardware bits.

## Test Signals

Build-level validation should ensure all AMDGPU DCN 2.0 code that includes `dpcs_2_0_0_sh_mask.h` compiles with the companion offset header and register helpers. Because these are generated constants, compile failures usually indicate renamed fields or missing generation coverage.

Static validation can check that every `__SHIFT` has a corresponding `_MASK` for each field in this chunk and that each mask covers the width implied by repeated lane patterns. Useful invariants include lane groups separated by 8 bits in `PHY_CNTL3`, `DMCU_DPALT_PHY_CNTL3`, and related reserved variants; per-lane TX equalization fuse fields in 6-bit groups; and CR address/data masks remaining 16-bit.

Runtime display test signals include successful DCN 2.0 display bring-up on ports mapped to TX4 and TX5, stable link training across one-, two-, and four-lane DP modes, HDMI timing modes that exercise MPLLB HDMI dividers, suspend/resume paths that cycle PHY and SRAM power bits, and USB-C/DP-alt mode transitions that exercise driver-access arbitration and DP-alt disable/ack fields.

Failure signals tied to this chunk include stuck waits on PHY request/ack or DP-alt disable/ack bits, FIFO overflow/error status in TX/RX interrupt registers, missing symbol-clock `CLOCK_ON` status after enable, failed PLL update pending/request transitions, display modes that work on lower-numbered PHYs but fail on TX4/TX5, and register dumps where fields extracted with these masks do not match expected lane, clock, or power state.

For regression coverage after any regeneration or manual patch, compare this chunk against the authoritative ASIC register database or against adjacent generated DPCS versions only where the hardware generation is known to match. A textual comparison alone is insufficient, because later versions intentionally move some fields.
