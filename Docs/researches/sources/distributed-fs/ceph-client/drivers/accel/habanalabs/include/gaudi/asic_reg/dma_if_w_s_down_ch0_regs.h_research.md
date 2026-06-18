# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_w_s_down_ch0_regs.h

## Purpose

`dma_if_w_s_down_ch0_regs.h` is the generated register map for the west/south DMA interface downstream channel 0 block, `DMA_IF_W_S_DOWN_CH0 (Prototype: RTR_CTRL)`. It mirrors the west/north channel-0 downstream register layout but uses the south-side `0x481xxx` address window. The file starts with `mmDMA_IF_W_S_DOWN_CH0_PERM_SEL` (`0x481108`) and ends with `mmDMA_IF_W_S_DOWN_CH0_NL_HBM_PC_SEL_3` (`0x481CBC`).

## Important APIs, Types, And Register Families

The file exports 437 macros and no executable code. Major families are identical to the W/N downstream channel maps:

- `PERM_SEL`.
- `HBM_POLY_H3_0..27` and `SRAM_POLY_H3_0..14`.
- `SCRAM_SRAM_EN` and `SCRAM_HBM_EN`.
- `RL_HBM_*`, `RL_PCI_*`, and `RL_SRAM_*`.
- `E2E_HBM_EN`, `E2E_PCI_EN`, HBM/PCI read/write size registers, AW/AR PCI/HBM counters, and per-HBM-channel E2E counter wrap/count registers.
- `NON_LIN_EN` plus `NL_*` bank/offset/HBM pseudo-channel controls.
- `RANGE_SEC_*` and `RANGE_PRIV_*` AW/AR base/mask tables with 16 entries per table.
- `RANGE_SEC_HIT_*` and `RANGE_PRIV_HIT_*`.
- `RGL_*` latency, token, bank-id, and watchdog registers.

## Control Flow

There is no local control flow. The macros are used after `gaudi_regs.h` includes the header. `gaudi.c` programs this channel during SRAM/HBM scrambler initialization and E2E setup. `gaudi_security.c` includes the south channel 0 secure range hit/base/mask registers in high-bandwidth range-register arrays before the north entries, making this header part of the protected HBW path setup.

## State And Persistence Behavior

The file persists no state. Its register addresses identify hardware state for scrambler enables, E2E protection counters, non-linear address mapping, range protection configuration, and range hit status. Initialization writes are conditional on firmware security state and boot status, so the driver does not overwrite firmware-owned configuration.

## Dependencies

The header depends on inclusion through `gaudi_regs.h` and on consumers using the correct MMIO helper and bitfield shifts. `gaudi_security.c` depends on the register layout matching the expected 16-entry secure-range table shape. The south-side address window must stay consistent with `mmDMA_IF_W_S_DOWN_CH0_BASE` in `gaudi_blocks.h`.

## Integration Points

The main integration points are `gaudi.c` scrambler/E2E initialization and `gaudi_security.c` high-bandwidth range protection arrays. The file also pairs with `dma_if_w_s_down_ch1_regs.h` for the second south downstream channel and with the W/N downstream headers for north/south symmetry.

## Risks

Address mistakes can silently program the wrong downstream south channel. Security risk is concentrated in the dense `RANGE_SEC_*` and `RANGE_PRIV_*` base/mask tables and in the hit registers consumed for violation reporting. Since this file is generated and macro-only, accidental manual edits or stale generated output are hard to detect from the compiler alone.

## Test Signals

Compile coverage through `gaudi_regs.h`, Gaudi boot paths that write `SCRAM_*` and `E2E_*`, protected-range programming tests that include W/S downstream channel 0, and register-map generation diffs are the best signals. Runtime validation should confirm that W/S channel 0 writes fall under the `0x481xxx` window and do not collide with W/N or channel 1.
