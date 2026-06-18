# Research: subset-b-000965

This grouped report covers generated Gaudi DMA interface register-map headers under `sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg`. Each section is split-ready for the reconciliation lane and preserves the exact source path in its title.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_w_n_down_ch0_regs.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_w_n_down_ch0_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_w_n_down_ch1_regs.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_w_n_down_ch1_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_w_n_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_w_n_regs.h

## Purpose

`dma_if_w_n_regs.h` is the auto-generated register address map for the top-level Gaudi west/north DMA interface block, `DMA_IF_W_N`. It covers HBM credit controls, low-bandwidth protection range registers for SOB/DMA initiators, hit/status registers, and miscellaneous bin/I2C/misc controls. The file exports 419 macro constants in the `mmDMA_IF_W_N_*` namespace. The address window starts at `mmDMA_IF_W_N_HBM0_WR_CRED_CNT` (`0x4C0000`) and ends at `mmDMA_IF_W_N_HBM_MISC` (`0x4C0834`).

## Important APIs, Types, And Register Families

There are no functions, data structures, or inline APIs. The public interface is the macro set:

- `HBM0_WR_CRED_CNT`, `HBM1_WR_CRED_CNT`, `HBM0_RD_CRED_CNT`, and `HBM1_RD_CRED_CNT`: programmed by `gaudi_init_hbm_cred()` with per-HBM read/write credit patterns.
- `HBM_LIMITER_0..3`, `HBM_ALMOST_EN_0..1`, and `HBM_CRED_EN_0..1`: HBM credit and limiter controls; the enable registers are written after credit counts.
- `SOB_*`, `DMA0_*`, and `DMA1_*` range tables: 16-entry low-bandwidth minimum/maximum windows for read/write protection (`RPROT`, `WPROT`) and read/write privilege (`RPRIV`, `WPRIV`).
- `SOB_HIT_*`, `DMA0_HIT_*`, and `DMA1_HIT_*`: hit/status registers for protection or privilege violations.
- `HBM_BIN`, `MME_BIN`, `TPC_BIN`, `DMA_BIN`, and `SOB_CG_EN`: miscellaneous binning/clock-gate style controls.
- `HBM_I2C_ADDR_0..4` and `HBM_MISC`: HBM sideband address and miscellaneous control registers.

## Control Flow

The header itself is declarative. In driver control flow:

- `gaudi_init_hbm_cred()` writes the four HBM credit count registers for west/north, then enables read/write HBM credits through `HBM_CRED_EN_0` and `HBM_CRED_EN_1` if firmware has not already done so.
- `gaudi_security.c` includes the `SOB`, `DMA0`, and `DMA1` low-bandwidth hit/min/max registers in arrays that program or inspect low-bandwidth protected ranges. The arrays depend on the `_0` entry as the base of each 16-register table.
- `gaudi_coresight.c` uses related W/N DMA interface block bases from `gaudi_blocks.h` for tracing/monitoring integration, while this header provides the functional block's register offsets.

## State And Persistence Behavior

The header has no software state. It names persistent hardware registers. HBM credit programming persists until reset or reconfiguration. Low-bandwidth protection windows and hit registers represent device security state; hits may be latched or inspected by security paths depending on the hardware behavior encoded outside this header. Driver writes are conditional on firmware security ownership and boot status bits such as `CPU_BOOT_DEV_STS0_HBM_CRED_EN`.

## Dependencies

Compile-time dependency is inclusion by `gaudi_regs.h`. Runtime dependencies include `WREG32`, HBM credit bit shifts such as `DMA_IF_HBM_CRED_EN_READ_CREDIT_EN_SHIFT` and `DMA_IF_HBM_CRED_EN_WRITE_CREDIT_EN_SHIFT`, and the security code's range-register programming helpers. The low-bandwidth tables depend on generated contiguity: each of SOB, DMA0, and DMA1 has repeated 16-entry min/max tables for read/write protection and privilege.

## Integration Points

This header integrates with:

- `gaudi.c` golden-register initialization for HBM credit count and enable registers.
- `gaudi_security.c` low-bandwidth protection arrays for SOB/DMA0/DMA1 ranges and hit status.
- `gaudi_regs.h`, which aggregates generated register headers for the Gaudi driver.
- `gaudi_blocks.h`, whose `mmDMA_IF_W_N_BASE` identifies the block base used by protected-block logic and tracing infrastructure.

## Risks

The highest risk is security range misprogramming. The low-bandwidth protection arrays in `gaudi_security.c` assume the generated min/max tables are ordered consistently and can be addressed from `_0`. A single wrong offset can produce a security hole or false violation. HBM credit registers affect traffic flow; wrong credit values or enable registers can throttle, deadlock, or overload the memory path. Because this is macro-only generated code, compiler type checking cannot distinguish a protection register from a credit register.

## Test Signals

Good test signals include successful Gaudi driver compilation, boot tests that run `gaudi_init_hbm_cred()`, security tests that configure SOB/DMA low-bandwidth protection ranges, and negative tests that intentionally trigger read/write protection hits and observe the `*_HIT_*` registers. Generator validation should compare this file with the authoritative ASIC register database and with the south-side sibling for expected `0x40000` north/south address separation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_w_n_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_w_s_down_ch0_regs.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_w_s_down_ch0_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_w_s_down_ch1_regs.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_w_s_down_ch1_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_w_s_regs.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_w_s_regs.h -->
