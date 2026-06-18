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
