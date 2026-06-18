# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_2_1_0_offset.h

## Purpose

`dpcs_2_1_0_offset.h` is the generated offset header for the DPCS 2.1.0 hardware block used by the DCN 2.1 resource path. Compared with DPCS 2.0.3, it expands the register surface substantially: it defines five DPCS/RDPCS transmitter instances, numbered 0 through 4, and adds register offsets for debug, SRAM power control, spare/cntl2, DP Alt mode control, DMCU DPALT override/block registers, PHY fuse registers, RX load values, `PHY_CNTL15` through `PHY_CNTL17`, `DEBUG_CONFIG2`, and DPCSSYS CR aliases for each instance.

The direct user in this tree is `dcn21_resource.c`, which includes `dpcs_2_1_0_offset.h` with the matching `dpcs_2_1_0_sh_mask.h` and builds five link encoder register entries for Renoir/DCN 2.1 style hardware.

## Important APIs, Types, and Macros

The header exports preprocessor constants only:

- `mmDPCSTX{0..4}_DPCSTX_TX_CLOCK_CNTL`, `TX_CNTL`, `CBUS_CNTL`, `INTERRUPT_CNTL`, `PLL_UPDATE_ADDR`, `PLL_UPDATE_DATA`, and `DEBUG_CONFIG`.
- `mmRDPCSTX{0..4}_RDPCSTX_CNTL`, `CLOCK_CNTL`, `INTERRUPT_CONTROL`, `PLL_UPDATE_DATA`, `RDPCS_TX_CR_ADDR`, `RDPCS_TX_CR_DATA`, `RDPCS_TX_SRAM_CNTL`, `SCRATCH`, `SPARE`, `CNTL2`, `DMCU_DPALT_DIS_BLOCK_REG`, `DEBUG_CONFIG`, `PHY_CNTL0` through `PHY_CNTL17`, `PHY_FUSE0` through `PHY_FUSE3`, `PHY_RX_LD_VAL`, `DMCU_DPALT_PHY_CNTL3`, `DMCU_DPALT_PHY_CNTL6`, `DPALT_CONTROL_REG`, and `DEBUG_CONFIG2`.
- `mmDPCSSYS_CR{0..4}_DPCSSYS_CR_ADDR` and `mmDPCSSYS_CR{0..4}_DPCSSYS_CR_DATA` aliases, which map to the same CR address/data offsets as the matching `RDPCSTX` instance.
- Every defined register has a companion `..._BASE_IDX` with value `2`.

The instance offsets follow a regular stride by address block base: instance 0 starts around `0x2928`, instance 1 around `0x2a00`, instance 2 around `0x2ad8`, instance 3 around `0x2bb0`, and instance 4 around `0x2c88`. The corresponding RDPCS and DPCSSYS CR aliases sit inside each instance block.

## Control Flow

Like the other ASIC register headers, the only control flow is build-time expansion:

1. `dcn21_resource.c` includes this header and defines `BASE(seg)` against the DCN 2.1 MMIO segment macros.
2. `link_regs(id, phyid)` expands `DPCS_DCN21_REG_LIST(id)` for each of five encoder instances.
3. Register-list macros paste tokens such as `mmRDPCSTX2_RDPCSTX_PHY_CNTL7_BASE_IDX` and `mmRDPCSTX2_RDPCSTX_PHY_CNTL7` into address initializers.
4. The populated `link_enc_regs[]` table is passed into `dcn21_link_encoder_construct`, after transmitter IDs are mapped to physical instances.
5. Runtime link encoder code accesses the registers indirectly through the populated table and matching shift/mask metadata.

This file does not enforce sequencing. It only makes the hardware addresses available.

## State and Persistence Behavior

The header stores no software state. It names hardware state that controls and reports DPCS/RDPCS behavior. The expanded 2.1.0 register surface includes additional state for SRAM power, debug control, DP Alt mode coordination with DMCU, fuse-calibrated PHY settings, and per-lane/PLL programming. Persistence and reset behavior are hardware-defined. Driver code must assume that fields can be affected by ASIC reset, display power gating, firmware/DMCU access, hotplug/link training flows, and suspend/resume transitions.

## Dependencies and Integration Points

Important dependencies and integration points include:

- `dpcs_2_1_0_sh_mask.h`, which supplies field positions and masks for the offsets in this file.
- `dcn21_resource.c`, the direct resource-file consumer for DCN 2.1.
- `dcn20_link_encoder.h` and DCN 2.1 link encoder code, which expect DPCS register names to exist for the selected ASIC generation.
- Base segment macros such as `DMU_BASE__INST0_SEG2`; every `_BASE_IDX` here is `2`.
- DPCSSYS CR aliases that intentionally share offsets with per-instance `RDPCS_TX_CR_ADDR` and `RDPCS_TX_CR_DATA`.

Because this file defines generic macro names used by token-pasting helpers, it should be included only in translation units that are intentionally building for DPCS 2.1.0.

## Risks and Edge Cases

- The header exposes five instances; consumers must map logical transmitter IDs to valid array indexes. `dcn21_resource.c` has a dedicated transmitter-to-phy mapping path, so off-by-one or unsupported transmitter IDs would be a runtime risk outside this header.
- DPCSSYS CR aliases duplicate address values already exposed through `RDPCSTX*_RDPCS_TX_CR_*`. This is likely intentional, but mixed use can hide aliasing bugs if code assumes they are independent registers.
- Wrong `_BASE_IDX` or offset values would affect every register access constructed from these macros and may not be caught by the compiler.
- Expanded debug, fuse, SRAM, and DP Alt mode registers often have sequencing or ownership constraints. The offset header cannot express whether the display driver, firmware, or hardware owns a field at a given time.
- The regular instance stride makes copy/paste or generator bugs easy to miss in review; register specification diffs are more reliable than visual inspection.

## Test Signals

Useful validation signals include:

- Build coverage of `dcn21_resource.c` and the DCN 2.1 link encoder path to verify all token-pasted register names resolve.
- Static comparison against the DPCS 2.1.0 generated register specification, including the aliasing between `RDPCS_TX_CR_*` and `DPCSSYS_CR*`.
- Hardware smoke tests on DCN 2.1 systems with multiple active outputs, exercising all five possible link encoder entries where hardware supports them.
- DP and HDMI mode-set/link-training tests that program PHY lane control, PLL, FIFO, clock, and reset registers.
- Suspend/resume, hotplug, and USB-C/DP Alt mode scenarios that exercise the added SRAM power and DPALT/DMCU-related register ranges.
