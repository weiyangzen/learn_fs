# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_w_n_down_ch0_regs.h

## Purpose

`dma_if_w_n_down_ch0_regs.h` is an auto-generated Gaudi ASIC register address map for the west/north DMA interface downstream channel 0 block, labeled in the file as `DMA_IF_W_N_DOWN_CH0 (Prototype: RTR_CTRL)`. It exports preprocessor constants only: there are no functions, types, inline helpers, or mutable C objects. The constants map symbolic register names to 32-bit MMIO offsets in the `0x4C1xxx` region, starting at `mmDMA_IF_W_N_DOWN_CH0_PERM_SEL` (`0x4C1108`) and ending at `mmDMA_IF_W_N_DOWN_CH0_NL_HBM_PC_SEL_3` (`0x4C1CBC`).

The block is one member of a symmetric set of Gaudi DMA downstream channels. Compared with channel 1 and the south-side variants, the register families are identical and the distinguishing feature is the base address window and name prefix.

## Important APIs, Types, And Register Families

The file exports 437 `#define` macros in the `mmDMA_IF_W_N_DOWN_CH0_*` namespace. The important groups are:

- `PERM_SEL`: permission selection/configuration for the downstream router-control prototype.
- `HBM_POLY_H3_0..27` and `SRAM_POLY_H3_0..14`: polynomial or hash/scrambling tables used by HBM and SRAM routing/scrambling logic.
- `SCRAM_SRAM_EN` and `SCRAM_HBM_EN`: enable registers written during Gaudi scrambler initialization.
- `RL_HBM_*`, `RL_PCI_*`, and `RL_SRAM_*`: rate-limiter enable, saturation, reset, timeout, and SRAM reduction controls.
- `E2E_*`: end-to-end protection/credit controls, including HBM/PCI enable bits, read/write sizes, PCI/HBM counter set controls, counter wrap registers, and per-HBM-channel AW/AR counter wrap/count registers.
- `NL_*` and `NON_LIN_EN`: non-linear SRAM/HBM selection, bank, offset, and HBM pseudo-channel selection controls.
- `RANGE_SEC_*` and `RANGE_PRIV_*`: high-bandwidth access range base and mask tables for AW and AR paths. There are 16 entries for each low/high half across secure and privileged range classes.
- `RANGE_SEC_HIT_AW`, `RANGE_SEC_HIT_AR`, `RANGE_PRIV_HIT_AW`, and `RANGE_PRIV_HIT_AR`: hit/status registers consumed by security violation handling.
- `RGL_*`: regulator or routing-governor latency, token, bank-id, watchdog configuration.

There are no C APIs in this header; the "API" is the stable macro naming contract consumed by `gaudi_regs.h`, `gaudi.c`, and `gaudi_security.c`.

## Control Flow

The header has no runtime control flow. Its behavior enters the driver through inclusion by `include/gaudi/asic_reg/gaudi_regs.h`, which exposes the macros to Gaudi initialization and security code. Runtime control flow is in consumers:

- `gaudi_init_scrambler_sram()` writes `mmDMA_IF_W_N_DOWN_CH0_SCRAM_SRAM_EN` when firmware security is not owning the feature and the SRAM scrambler has not already been initialized.
- `gaudi_init_scrambler_hbm()` writes `mmDMA_IF_W_N_DOWN_CH0_SCRAM_HBM_EN` under analogous HBM boot/security checks.
- `gaudi_init_e2e()` writes the channel's E2E HBM/PCI read/write size registers and then enables E2E HBM and PCI controls.
- `gaudi_security.c` stores the channel 0 secure range hit/base/mask macros in high-bandwidth range-register arrays used to program and inspect protected memory windows.

## State And Persistence Behavior

The header persists no state itself. It defines addresses for hardware state that persists in device registers until reset, firmware reprogramming, or driver writes. Driver-level persistence is guarded by hardware capability flags such as `HW_CAP_SRAM_SCRAMBLER` and `HW_CAP_HBM_SCRAMBLER`, plus firmware boot status bits that indicate whether firmware already initialized scrambler or E2E/HBM credit features. The range and hit registers represent security configuration and violation state in hardware, not in the header.

## Dependencies

The only compile-time dependency is inclusion order through `gaudi_regs.h`; the file uses normal include guards and no external symbols. Runtime users depend on:

- MMIO write/read helpers such as `WREG32` in the Gaudi driver.
- Bitfield shift macros such as `DMA_IF_DOWN_CHX_SCRAM_SRAM_EN_VAL_SHIFT`, `DMA_IF_DOWN_CHX_SCRAM_HBM_EN_VAL_SHIFT`, `DMA_IF_DOWN_CHX_E2E_HBM_EN_VAL_SHIFT`, and `DMA_IF_DOWN_CHX_E2E_PCI_EN_VAL_SHIFT`.
- Security helper logic in `gaudi_security.c` that assumes the 16-entry range tables are contiguous with a 4-byte stride from the `_0` symbols.

## Integration Points

`gaudi_regs.h` includes this header directly. `gaudi.c` uses the scrambler and E2E symbols during golden-register initialization. `gaudi_security.c` integrates the secure range hit and base/mask symbols into high-bandwidth range arrays, and protection-block setup references the corresponding block base from `gaudi_blocks.h` (`mmDMA_IF_W_N_DOWN_CH0_BASE`). This file is paired with `dma_if_w_n_down_ch1_regs.h` and the `W_S` downstream channel headers to cover all west-side north/south DMA downstream paths.

## Risks

The main risk is generated-address drift: a wrong offset would compile cleanly but program the wrong hardware register. Dense table families are especially sensitive because security code relies on contiguous `_0..15` layout and 4-byte strides when programming ranges. The file also has no semantic type safety; any macro can be passed to any MMIO helper. E2E and scrambler enable registers are guarded in runtime code, but incorrect values or boot-status detection could leave hardware features disabled or double-programmed. Because the file is auto-generated, manual edits should be treated as suspect.

## Test Signals

Useful signals include compile coverage of `gaudi_regs.h`, boot-time Gaudi initialization paths that execute scrambler and E2E setup, security tests that program protected HBW ranges and inspect `RANGE_SEC_HIT_*`/`RANGE_PRIV_HIT_*`, and register-generation diff checks against the authoritative ASIC database. Runtime smoke tests should verify that writes to `SCRAM_*`, `E2E_*`, and range registers land in the expected `0x4C1xxx` window.
