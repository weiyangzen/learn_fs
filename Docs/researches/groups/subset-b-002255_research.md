<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_0_3_offset.h -->
# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_0_3_offset.h

## Purpose

`dpcs_3_0_3_offset.h` is a generated AMDGPU register-address header for the DCN 3.0.3 DisplayPort/Display PHY Control Subsystem (DPCS). It exports symbolic register offsets for two link/PHY instances, `DPCSTX0`/`RDPCSTX0` and `DPCSTX1`/`RDPCSTX1`, plus `DPCSSYS_CR0` and `DPCSSYS_CR1` aliases for the PHY control-register address/data pair. DCN 3.0.3 display resource code includes this file together with the matching shift/mask header to populate link encoder register tables.

## Important APIs, Types, And Macros

The header defines no C functions, structs, or enums. Its public API is the `mm...` and `mm..._BASE_IDX` macro set:

- `mmDPCSTX0_DPCSTX_TX_CLOCK_CNTL` through `mmDPCSTX0_DPCSTX_PLL_UPDATE_DATA`, offsets `0x2928` through `0x292d`, base index `2`.
- `mmRDPCSTX0_RDPCSTX_CNTL` through `mmRDPCSTX0_RDPCSTX_DPALT_CONTROL_REG`, offsets `0x2930` through `0x2956`, base index `2`.
- `mmDPCSSYS_CR0_DPCSSYS_CR_ADDR` and `mmDPCSSYS_CR0_DPCSSYS_CR_DATA`, aliases at offsets `0x2934` and `0x2935`, base index `2`.
- `mmDPCSTX1_DPCSTX_TX_CLOCK_CNTL` through `mmDPCSTX1_DPCSTX_PLL_UPDATE_DATA`, offsets `0x2a00` through `0x2a05`, base index `2`.
- `mmRDPCSTX1_RDPCSTX_CNTL` through `mmRDPCSTX1_RDPCSTX_DPALT_CONTROL_REG`, offsets `0x2a08` through `0x2a2e`, base index `2`.
- `mmDPCSSYS_CR1_DPCSSYS_CR_ADDR` and `mmDPCSSYS_CR1_DPCSSYS_CR_DATA`, aliases at offsets `0x2a0c` and `0x2a0d`, base index `2`.

The main register groups cover DPCS TX clocking, FIFO/control, CBUS, interrupt status/masking, PLL update address/data, RDPCS TX control and SRAM, scratch/spare/status, DPALT access control, PHY control registers `0` through `14`, PHY fuse registers `0` through `3`, and PHY RX load values.

## Control Flow

This file has only a preprocessor include guard and constant definitions. Runtime control flow appears in consumers such as `display/dc/resource/dcn303/dcn303_resource.c`: the resource file includes this header, then `SRI(...)`, `LE_DCN3_REG_LIST(...)`, `DPCS_DCN2_MASK_SH_LIST(...)`, and related macros expand the offsets into `struct dcn10_link_enc_registers`, `struct dcn10_link_enc_shift`, and `struct dcn10_link_enc_mask` initializers. Link encoder construction then passes those tables into `dcn30_link_encoder_construct()`.

## State And Persistence Behavior

The header itself has no mutable state or persistence. It names MMIO-backed hardware registers whose values persist in the display hardware until firmware, driver programming, power gating, hotplug handling, or reset changes them. Address constants are compile-time state and must match the DCN 3.0.3 register specification for the ASIC selected by the resource pool.

## Dependencies

This header depends on AMD's generated register naming convention and the DCN register-base system where `BASE(mm..._BASE_IDX) + mm...` computes the final address. It is intended to be used with `dpcs_3_0_3_sh_mask.h` for field extraction and update masks. It also depends on DCN 3.0.3 resource selection: using these offsets on a different DPCS revision would make link encoder MMIO access target the wrong registers.

## Integration Points

The direct integration point is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn303/dcn303_resource.c`, which includes `dpcs/dpcs_3_0_3_offset.h` and `dpcs/dpcs_3_0_3_sh_mask.h`. That resource file supports two physical link encoders and initializes link encoder tables with `link_regs(0, A)` and `link_regs(1, B)`. Broader consumers are DC link encoder code paths in `display/dc/dio/dcn20` and `display/dc/dio/dcn30`, which use DPCS/RDPCS register tables for DP lane setup, PHY power, MPLL programming, FIFO control, DPALT control, and training-related status.

## Risks And Edge Cases

The two instances are nearly identical but not address-identical; instance 1 is shifted to the `0x2a00` range and must not reuse instance 0 offsets. The CR alias registers intentionally overlap the RDPCS TX CR address/data offsets, so tooling that tries to enforce unique macro values may flag false positives. Every macro uses `BASE_IDX` `2`; dropping or changing that base index during table generation would silently move all accesses. The offset header also does not expose `DPCSTX*_DPCSTX_DEBUG_CONFIG`, although the mask header has field definitions for the instance 0 debug config, so consumers need matching address availability before using that field.

## Test Signals

Compile coverage should include DCN 3.0.3 resource construction so all `mm...` macros referenced by link encoder register lists resolve. Static checks can compare every `mm...` offset and `BASE_IDX` against AMD register metadata and verify the `DPCSTX0` to `DPCSTX1` and `RDPCSTX0` to `RDPCSTX1` instance deltas. Hardware or simulator tests should exercise two-link configurations, DP link training, PHY reset/power sequencing, DPALT transitions, and PLL update flows to catch wrong offsets or swapped instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_0_3_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_0_3_sh_mask.h -->
# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_0_3_sh_mask.h

## Purpose

`dpcs_3_0_3_sh_mask.h` is the generated field-definition companion to `dpcs_3_0_3_offset.h`. For each DPCS/RDPCS register that DCN 3.0.3 display code can program or read, it exports `__SHIFT` and `_MASK` macros that describe bit positions and bit ranges. These constants let generic link encoder helpers update register fields without hard-coded bit arithmetic.

## Important APIs, Types, And Macros

The file defines no functions or C types. Its exported API is a large set of field macros in the pattern `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`.

Important field groups include:

- `DPCSTX0_DPCSTX_TX_CLOCK_CNTL` and `DPCSTX1_DPCSTX_TX_CLOCK_CNTL`: symbol-clock gate disable, enable, and clock-on status fields.
- `DPCSTX*_DPCSTX_TX_CNTL`: PLL update request/pending, 10-bit data swap/order inversion, 18-bit data-order inversion, FIFO enable/start/read delay, and TX soft reset.
- `DPCSTX*_DPCSTX_CBUS_CNTL`, `DPCSTX*_DPCSTX_INTERRUPT_CNTL`, and PLL update address/data fields: CBUS delay/reset, FIFO overflow/error status, clear bits, interrupt masks, and raw PLL update payload fields.
- `RDPCSTX*_RDPCSTX_CNTL` and `RDPCSTX*_RDPCSTX_CLOCK_CNTL`: CBUS/SRAM/TX reset, lane FIFO enables, FIFO timing, DPALT block status, register-block enables, external reference clock, per-lane TX clocks, TX clock gate/enable/status, SRAM clock gate/enable/status, and SRAM bypass.
- `RDPCSTX*_RDPCSTX_INTERRUPT_CONTROL`: register FIFO overflow, DPALT disable and 4-lane toggle interrupts, per-lane TX FIFO errors, clear bits, and interrupt mask bits.
- `RDPCSTX*_RDPCS_TX_CR_ADDR` and `RDPCSTX*_RDPCS_TX_CR_DATA`, plus `DPCSSYS_CR0/1`: 16-bit control-register bus address and data fields.
- `RDPCSTX*_RDPCS_TX_SRAM_CNTL`, scratch, spare, and `RDPCSTX*_RDPCSTX_CNTL2`: SRAM power-state control and CR conversion FIFO empty/full status.
- `RDPCSTX*_RDPCSTX_PHY_CNTL0` through `PHY_CNTL14`: PHY reset/APB reset, HDMI mode, reference range, vboost, retune handshake, CR mux selection, SRAM load status, power-gating stable bits, DP loopback, lane reset/disable/ready/data enable/request/ack, lane termination/inversion, rate/width/detect-RX, lane P-state and MPLL enable, DPALT flags, DP ref clock request, MPLLB fractional/SSC/multiplier/divider/state/calibration fields, and FRACN/PMIX enable.
- `RDPCSTX*_RDPCSTX_PHY_FUSE0` through `PHY_FUSE3` and `PHY_RX_LD_VAL`: lane equalization fuse values, MPLLB fuse trims, DCO trim/range, and RX reference/VCO load values.
- `RDPCSTX*_RDPCSTX_DMCU_DPALT_PHY_CNTL3`, `DMCU_DPALT_PHY_CNTL6`, `DMCU_DPALT_DIS_BLOCK_REG`, and `DPALT_CONTROL_REG`: reserved DMCU/DPALT shadow fields and driver-access gating.

The file defines full field sets for instance 0 and instance 1. The two instances generally share identical bit layouts while using different register-name prefixes.

## Control Flow

There is no runtime control flow inside this header. At compile time, the include guard exposes field constants to table-building macros. In DCN 3.0.3, `dcn303_resource.c` initializes `le_shift` with `DPCS_DCN2_MASK_SH_LIST(__SHIFT)` and `le_mask` with `DPCS_DCN2_MASK_SH_LIST(_MASK)` after including this file. Link encoder code then uses those populated shift/mask tables in register helper paths to read, compose, and write individual DPCS fields during display link setup.

## State And Persistence Behavior

The header's constants are immutable compile-time metadata. The state represented by the fields lives in DPCS hardware registers and includes volatile status bits, sticky error bits, clear-on-write controls, firmware/DPALT ownership gates, power-state controls, PLL programming fields, lane-training controls, fuse-derived trims, scratch/spare registers, and interrupt masks. Persistence differs by field: scratch/spare and control bits can survive until reset or reprogramming, error/status fields may be sticky or hardware-updated, and fuse fields reflect ASIC calibration values.

## Dependencies

This file depends on the matching offset header for register addresses and on the AMD DC register-helper convention that joins register symbols, field symbols, shifts, and masks through macros such as `LE_SF(...)`. It also depends on the shared DCN link encoder structures whose field names match these generated macro suffixes. The actual behavior of fields such as DPALT, MPLLB, and PHY lane control depends on hardware sequencing in DCN 2.x/3.x link encoder implementations, not on this header alone.

## Integration Points

The immediate integration point is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn303/dcn303_resource.c`, which includes this header and feeds its constants into link encoder shift/mask tables. The functional consumers are the DC link encoder and stream encoder paths under `display/dc/dio`, especially DCN 20/30 helpers that name fields such as `RDPCS_PHY_DP_TX*_CLK_RDY`, `RDPCS_PHY_DP_TX*_DATA_EN`, `RDPCS_PHY_DP_MPLLB_*`, `RDPCS_TX_FIFO_*`, `RDPCS_EXT_REFCLK_EN`, `RDPCS_SRAMCLK_*`, `DPCS_TX_DATA_ORDER_INVERT_18_BIT`, `RDPCS_PHY_TX_VBOOST_LVL`, `RDPCS_PHY_DPALT_DP4`, and `RDPCS_PHY_DPALT_DISABLE`. These are used for DP PHY bring-up, link training, clock enabling, lane power/state transitions, PLL setup, interrupt masking, and DPALT handoff.

## Risks And Edge Cases

The repeated instance layout invites copy/paste drift; any field that differs between `0` and `1` must be intentional. Some names contain a doubled `MASK_MASK` suffix because the field itself is named `..._MASK`; consumers must use the generated macro name exactly. Several fields are status or clear bits adjacent to enable/mask bits, so writing a composed value with stale status bits can accidentally clear or mask hardware events. DPALT driver-access fields imply ownership coordination with firmware/DMCU; setting PHY or MPLL fields while access is blocked can fail or race. The header also includes a `DPCSTX0_DPCSTX_DEBUG_CONFIG` field block without a corresponding offset macro in `dpcs_3_0_3_offset.h`, so use of that field needs an address source from another header or generated metadata.

## Test Signals

Build tests should cover `dcn303_resource.c` so every referenced `__SHIFT` and `_MASK` macro resolves through `DPCS_DCN2_MASK_SH_LIST`. Static validation can recompute each mask from width and shift, compare field names against the hardware register database, and compare instance 0 and instance 1 for expected layout symmetry. Runtime validation should include DP link training over one-lane, two-lane, and four-lane modes; hotplug or DPALT transitions; PHY power-gating and reset sequencing; interrupt mask/error-clear behavior; and PLL/MPLLB programming with spread-spectrum and fractional settings. Hardware logs showing successful HBR2/HBR3 training, stable clock-on bits, expected lane ready/ack handshakes, and no DPCS/RDPCS FIFO errors are strong integration signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_0_3_sh_mask.h -->
