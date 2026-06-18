# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_w_s_down_ch1_regs.h

## Purpose

`dma_if_w_s_down_ch1_regs.h` is the generated register map for Gaudi's west/south DMA interface downstream channel 1 block, `DMA_IF_W_S_DOWN_CH1 (Prototype: RTR_CTRL)`. It is structurally identical to the other downstream DMA interface channel maps and occupies the `0x482xxx` address window. It starts at `mmDMA_IF_W_S_DOWN_CH1_PERM_SEL` (`0x482108`) and ends at `mmDMA_IF_W_S_DOWN_CH1_NL_HBM_PC_SEL_3` (`0x482CBC`).

## Important APIs, Types, And Register Families

This header exports 437 register macros in the `mmDMA_IF_W_S_DOWN_CH1_*` namespace. Important groups are:

- `PERM_SEL`.
- `HBM_POLY_H3_*` and `SRAM_POLY_H3_*` tables.
- `SCRAM_SRAM_EN`, `SCRAM_HBM_EN`.
- `RL_HBM_*`, `RL_PCI_*`, `RL_SRAM_*`.
- `E2E_*` enable, sizing, counter-set, counter-wrap, and counter-count registers.
- `NON_LIN_EN` and `NL_*` non-linear SRAM/HBM mapping controls.
- `RANGE_SEC_*` and `RANGE_PRIV_*` 16-entry base/mask tables for both AW and AR paths.
- `RANGE_SEC_HIT_AW`, `RANGE_SEC_HIT_AR`, `RANGE_PRIV_HIT_AW`, and `RANGE_PRIV_HIT_AR`.
- `RGL_*` governor/latency/token/watchdog registers.

## Control Flow

No code executes in the header. Consumers create behavior:

- `gaudi.c` writes `SCRAM_SRAM_EN`, `SCRAM_HBM_EN`, and E2E registers during hardware initialization when firmware has not already enabled those features.
- `gaudi_security.c` includes W/S channel 1 in its HBW range-register arrays, allowing the same protected-range programming and hit inspection as W/S channel 0.

## State And Persistence Behavior

The macros identify device register state. Scrambler, E2E, non-linear mapping, regulator, and range-protection settings persist in hardware until device reset or reprogramming. The header stores none of that state in memory. Firmware ownership checks in runtime code determine whether driver writes are skipped.

## Dependencies

Dependencies are the generated-register include chain, MMIO helpers, bitfield shift macros, and the security code's assumptions about contiguous 16-entry register tables. The base address must align with `mmDMA_IF_W_S_DOWN_CH1_BASE` in `gaudi_blocks.h`.

## Integration Points

`gaudi_regs.h` includes this file. `gaudi.c` programs it in lockstep with the east/west and north/south downstream channels for scrambler and E2E setup. `gaudi_security.c` indexes its secure range registers as part of the `GAUDI_NUMBER_OF_HBW_RR_REGS` high-bandwidth register arrays. It complements `dma_if_w_s_down_ch0_regs.h` for the south DMA downstream pair.

## Risks

The risk profile is generated-register correctness: incorrect offsets can break E2E setup, disable security protection on this channel, or make hit reporting point at the wrong status register. Channel symmetry increases copy/paste and generator-template risk because only the prefix and address window distinguish this file from its siblings.

## Test Signals

Signals include driver compilation, boot-time writes into the `0x482xxx` range, high-bandwidth security range programming that covers both W/S downstream channels, and generator validation comparing channel 1 against channel 0 for expected address shifts and identical register ordering.
