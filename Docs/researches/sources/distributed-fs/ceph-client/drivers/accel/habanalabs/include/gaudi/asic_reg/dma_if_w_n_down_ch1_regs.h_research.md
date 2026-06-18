# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_w_n_down_ch1_regs.h

## Purpose

`dma_if_w_n_down_ch1_regs.h` is the auto-generated register address map for Gaudi's west/north DMA interface downstream channel 1 block, `DMA_IF_W_N_DOWN_CH1 (Prototype: RTR_CTRL)`. It is the channel-1 sibling of `dma_if_w_n_down_ch0_regs.h`: the macro families are equivalent, but addresses move into the `0x4C2xxx` channel window. The first exported register is `mmDMA_IF_W_N_DOWN_CH1_PERM_SEL` (`0x4C2108`) and the last is `mmDMA_IF_W_N_DOWN_CH1_NL_HBM_PC_SEL_3` (`0x4C2CBC`).

## Important APIs, Types, And Register Families

This header exports 437 `#define` macros and no C functions or structs. Important macro families are:

- `PERM_SEL` for permission selection.
- `HBM_POLY_H3_0..27` and `SRAM_POLY_H3_0..14` for HBM/SRAM polynomial or routing tables.
- `SCRAM_SRAM_EN` and `SCRAM_HBM_EN` for driver-controlled scrambler enable paths.
- `RL_HBM_*`, `RL_PCI_*`, and `RL_SRAM_*` for rate-limiter programming.
- `E2E_*` for HBM/PCI E2E enable, read/write sizing, AW/AR counters, and per-HBM-channel counter wrap/count registers.
- `NON_LIN_EN`, `NL_HBM_SEL_*`, `NL_SRAM_BANK_*`, `NL_SRAM_OFFSET_*`, `NL_HBM_OFFSET_*`, and `NL_HBM_PC_SEL_*` for non-linear address mapping and HBM pseudo-channel selection.
- `RANGE_SEC_*` and `RANGE_PRIV_*` base/mask tables for AW and AR high-bandwidth protection ranges.
- `RANGE_SEC_HIT_*` and `RANGE_PRIV_HIT_*` status registers for security hit reporting.
- `RGL_*` latency/token/bank/watchdog controls.

## Control Flow

The file has no executable code. Runtime behavior is created by consumers after `gaudi_regs.h` includes it. `gaudi.c` writes this channel's `SCRAM_SRAM_EN`, `SCRAM_HBM_EN`, E2E size, and E2E enable registers in the same initialization functions that program channel 0. `gaudi_security.c` includes channel 1 in the high-bandwidth range-register arrays for secure hit, base, and mask programming, so channel 1 receives the same protection-window treatment as channel 0.

## State And Persistence Behavior

No software state is stored in the header. The symbols name hardware registers whose state persists in the device until reset or reprogramming. The driver avoids overwriting firmware-owned scrambler/E2E state by checking firmware security and boot status bits before writes. Range base/mask settings and hit registers represent hardware protection state and violation evidence.

## Dependencies

The header depends only on C preprocessing and include-guard discipline. Consumers depend on MMIO accessors, Gaudi boot/security property fields, and bitfield shift definitions. Security programming depends on the generated ordering of range table entries: `_0` symbols must be followed by the remaining entries at the expected stride and in the expected secure/privileged AW/AR order.

## Integration Points

`gaudi_regs.h` is the integration surface. `gaudi.c` writes channel 1 scrambler/E2E registers next to the corresponding east, south, and channel 0 registers. `gaudi_security.c` maps this channel into `GAUDI_NUMBER_OF_HBW_RR_REGS` arrays, and protected-block setup can protect `mmDMA_IF_W_N_DOWN_CH1_BASE` from `gaudi_blocks.h`.

## Risks

Risks mirror channel 0: incorrect generated offsets silently target the wrong MMIO address; table-size or stride mismatches could corrupt security range programming; and macro-only APIs provide no type checking. Channel 1 is also easy to confuse with channel 0 because the macro names and register families are identical except for the channel token and `0x1000` address-window shift.

## Test Signals

Compile tests should include `gaudi_regs.h` and any code that references `mmDMA_IF_W_N_DOWN_CH1_*`. Runtime validation should exercise Gaudi golden-register initialization and protected-range setup across both W/N downstream channels. Register-map tests should verify that channel 1 offsets are consistently shifted from channel 0 while preserving register order and count.
