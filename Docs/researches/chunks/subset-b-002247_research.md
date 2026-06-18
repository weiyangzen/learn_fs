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
