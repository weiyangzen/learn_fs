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
