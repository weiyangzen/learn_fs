# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_w_s_regs.h

## Purpose

`dma_if_w_s_regs.h` is the generated register map for Gaudi's top-level west/south DMA interface block, `DMA_IF_W_S`. It is the south-side counterpart to `dma_if_w_n_regs.h`, exporting HBM credit controls, low-bandwidth SOB/DMA protection ranges, hit/status registers, and miscellaneous HBM/bin controls. It contains 419 macros in the `mmDMA_IF_W_S_*` namespace, from `mmDMA_IF_W_S_HBM0_WR_CRED_CNT` (`0x480000`) to `mmDMA_IF_W_S_HBM_MISC` (`0x480834`).

## Important APIs, Types, And Register Families

No functions or types are declared. Register families include:

- `HBM0_WR_CRED_CNT`, `HBM1_WR_CRED_CNT`, `HBM0_RD_CRED_CNT`, `HBM1_RD_CRED_CNT`.
- `HBM_LIMITER_0..3`, `HBM_ALMOST_EN_0..1`, `HBM_CRED_EN_0..1`.
- SOB low-bandwidth min/max read/write protection and privilege tables (`SOB_MIN_RPROT_0..15`, `SOB_MAX_RPROT_0..15`, and analogous WPROT/RPRIV/WPRIV families).
- DMA0 and DMA1 low-bandwidth protection/privilege range tables with the same 16-entry shape.
- `SOB_HIT_*`, `DMA0_HIT_*`, and `DMA1_HIT_*` protection/privilege hit registers.
- `HBM_BIN`, `MME_BIN`, `TPC_BIN`, `DMA_BIN`, `SOB_CG_EN`, `HBM_I2C_ADDR_0..4`, and `HBM_MISC`.

## Control Flow

The header is declarative. Driver behavior is provided by:

- `gaudi_init_hbm_cred()`, which writes W/S HBM credit count registers and then enables read/write credits via `HBM_CRED_EN_0` and `HBM_CRED_EN_1` when firmware has not already initialized HBM credits.
- `gaudi_security.c`, which uses W/S SOB/DMA0/DMA1 low-bandwidth min/max and hit macros in arrays for range programming and violation inspection.

## State And Persistence Behavior

The header does not keep state. The named hardware registers hold HBM credit configuration, low-bandwidth protection windows, hit status, and miscellaneous HBM settings. Those register values persist in the ASIC until reset or reconfiguration. Firmware security ownership and boot status bits control whether the driver writes some of these registers during initialization.

## Dependencies

The file is included by `gaudi_regs.h` and consumed by Gaudi C sources. Runtime use depends on `WREG32`, security range programming helpers, HBM credit enable bit shifts, and the generated table ordering. Protection code expects `_0` table symbols to be suitable bases for 16 consecutive range entries.

## Integration Points

`gaudi.c` uses the HBM credit macros for south-side west DMA credit setup. `gaudi_security.c` uses the low-bandwidth range and hit macros alongside east/south and north blocks to build full-device protection coverage. `gaudi_blocks.h` provides `mmDMA_IF_W_S_BASE` for protected-block setup and related infrastructure, while this file provides the offsets used inside that block.

## Risks

Wrong HBM credit offsets or enable registers can affect memory traffic scheduling. Wrong low-bandwidth protection offsets can create false positives or leave SOB/DMA accesses unprotected. The similarity to `dma_if_w_n_regs.h` means generator or merge errors may be easy to miss unless address windows are checked. Macro-only definitions offer no compile-time validation of register purpose.

## Test Signals

Useful tests include Gaudi driver compile coverage, boot tests that execute HBM credit initialization, security tests that program SOB/DMA ranges and trigger hit status, and generated-register consistency checks that compare W/S and W/N macro families for expected address-window differences with identical ordering.
