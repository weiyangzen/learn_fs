# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/gaudi_blocks.h lines 1-4303

## Scope

This chunk is the first 4,303 lines of the auto-generated Gaudi ASIC block map header. It is not Ceph filesystem logic despite the source snapshot path; it belongs to the Habana Labs accelerator driver register-definition layer. The file declares compile-time constants for Gaudi MMIO block base addresses, maximum offsets, and block spacing/section sizes.

The covered range starts at the SPDX/header guard and extends through most of the `TPC3_EML_TPC_CFG` debug/emulation tensor sub-block definitions. It stops at `KERNEL_TENSOR_14_TPC3_EML_TPC_CFG_MAX_OFFSET`; the matching `KERNEL_TENSOR_14_TPC3_EML_TPC_CFG_SECTION` and the rest of the file continue in the next chunk.

## Purpose

The header provides the coarse address map used by the Gaudi driver to locate functional blocks before adding per-register offsets from the generated `*_regs.h` headers. Each block generally appears as a macro triplet:

- `mm..._BASE`: the 64-bit base address of the block in the Gaudi register aperture.
- `..._MAX_OFFSET`: the maximum offset used by that generated register block.
- `..._SECTION`: the spacing from this block to the next block or the reserved section size in the generated map.

Within lines 1-4303 there are 4,289 `#define` entries: 1,430 base macros, 1,430 max-offset macros, 1,428 section macros, and the header guard macro. The section count is lower because `mmNIC0_PHY0_BASE` has no visible `SECTION` companion in this range and because the chunk ends before one TPC3 EML `SECTION` companion.

The data is security- and bring-up-sensitive because higher-level code derives block strides, protection-bit targets, ECC-report addresses, queue-manager bases, and debug apertures from these constants.

## Important APIs, Types, And Definitions

There are no C functions, structs, enums, or runtime APIs in this chunk. The important API surface is the macro namespace exported through `gaudi_regs.h`, which includes `gaudi_blocks.h` before the per-register headers.

Major macro families in this chunk include:

- MME runtime blocks for `MME0` through `MME3`: `ACC`, `SBAB`, `PRTN`, `CTRL`, architecture views, four shadow views, and `QM` bases. These start near `mmMME0_ACC_BASE` and repeat at regular offsets for all four MMEs.
- SRAM fabric blocks for `Y0` through `Y3` and `X0` through `X7`: each bank has a `BANK` base and router `RTR` base, followed later by CoreSight/debug `FUNNEL` bases.
- Interface routers: `SIF_RTR_[0-7]`, `SIF_RTR_CTRL_[0-7]`, `NIF_RTR_[0-7]`, and `NIF_RTR_CTRL_[0-7]`.
- DMA interface, sync-manager, PLL, core, and queue-manager blocks: four directional DMA interfaces (`W_S`, `E_S`, `W_N`, `E_N`), eight DMA cores, and eight DMA QMs.
- Memory and platform control blocks: `HBM0` through `HBM3`, `GIC`, PCIe wrapper/DBI/core/aux/PHY/MSI/PMA blocks, `MMU_UP`, `STLB`, PSOC peripherals, CPU/CA53 blocks, and top-level trace/debug blocks.
- NIC runtime blocks for NIC0 through NIC4: MAC channels, statistics, XPCS, MAC core/aux, PHY, queue managers, QPC, RX/TX datapath blocks, gateways, timers, timestamp, PLL, and power-management blocks. Not every NIC has exactly the same tail set; for example NIC2 carries HBM/MME/TPC PLL entries where NIC3/NIC4 do not in this visible runtime region.
- TPC runtime blocks for TPC0 through TPC7: CFG, kernel tensor descriptors 0-15, kernel sync object, kernel TPC sub-block, QM tensor descriptors 0-15, QM sync object, QM TPC sub-block, E2E credit block, and TPC QM block.
- CoreSight/debug/emulation address map entries in the `0x7FFE...` and `0x7FFF...` apertures, including MME trace blocks, SRAM funnels, interface funnels, DMA trace/bus-monitor blocks, CPU trace blocks, PCIe/MMU/PSOC debug blocks, NIC debug blocks, and TPC EML blocks through part of TPC3.

The most consumed definitions are the base macros for repeated engines. Examples visible in this chunk include `mmMME0_ACC_BASE`, `mmMME0_QM_BASE`, `mmDMA0_QM_BASE`, `mmTPC0_QM_BASE`, `mmTPC0_CFG_BASE`, `mmNIC0_QM0_BASE`, `mmNIC0_QM1_BASE`, `mmHBM0_BASE`, and `mmHBM1_BASE`.

## Control Flow

This file has no runtime control flow. Its "flow" is compile-time inclusion:

1. `gaudi_regs.h` includes `gaudi_blocks.h`.
2. Gaudi driver C files include Gaudi private headers or generated register headers that expose these macros.
3. Runtime driver code combines a block base from this header with a per-register offset from a `*_regs.h` file or with a stride computed from two base macros.
4. MMIO helpers such as `WREG32()` and `RREG32()` operate on the resulting addresses.

The file order matters to maintainers because repeated block families are laid out in address order. The chunk starts with runtime CSR space near `0x7FFC...`, later moves into debug/CoreSight space near `0x7FFE...`, and reaches TPC EML space near `0x7FFF...`.

## State And Persistence Behavior

The header itself stores no state and persists nothing at runtime. Its constants are compiled into the driver and become part of the driver's hardware contract for a specific Gaudi ASIC register map.

Hardware state is affected indirectly by users of these constants. For example:

- Security initialization calculates protection-bit addresses from block bases such as `mmMME0_ACC_BASE`, `mmMME0_CTRL_BASE`, and `mmNIC0_QM0_BASE`.
- ECC and error handling calculate engine-specific diagnostic addresses from `mmTPC0_CFG_BASE`, `mmMME0_ACC_BASE`, and generated stride macros.
- Queue-manager handling derives queue-manager MMIO bases from `mmTPC0_QM_BASE`, `mmDMA0_QM_BASE`, `mmMME0_QM_BASE`, and NIC QM bases.

If any base or section constant is wrong, the software state may still look valid while MMIO reaches the wrong hardware block.

## Dependencies And Integration Points

The direct dependency is the generated register header inclusion chain. `gaudi_regs.h` includes this block map and then includes per-block register headers such as DMA, MME, TPC, NIC, MMU, PCIe, NIF, SIF, and PSOC register definitions.

Important integration points in the Gaudi driver include:

- `gaudiP.h`, which derives reusable strides such as `GAUDI_HBM_CFG_OFFSET`, `DMA_QMAN_OFFSET`, `TPC_QMAN_OFFSET`, `MME_QMAN_OFFSET`, `NIC_MACRO_QMAN_OFFSET`, `NIC_ENGINE_QMAN_OFFSET`, `TPC_CFG_OFFSET`, `DMA_CORE_OFFSET`, `SIF_RTR_CTRL_OFFSET`, `NIF_RTR_CTRL_OFFSET`, `MME_ACC_OFFSET`, and `SRAM_BANK_OFFSET`.
- `gaudi_security.c`, which uses block bases to protect MME, NIC, TPC, DMA, PLL, and related register blocks through protection-bit programming.
- `gaudi.c` error handling, which maps event IDs to TPC CFG, MME ACC/SBAB, DMA QM, TPC QM, MME QM, and NIC QM bases.
- Debug and trace tooling, which relies on the CoreSight-style `STM`, `CTI`, `ETF`, `SPMU`, `BMON`, `FUNNEL`, ROM table, and EML block bases in the later portion of the chunk.

The constants also integrate with the driver's address-space convention around `CFG_BASE` and protection-bit offsets. Many runtime users subtract `CFG_BASE` from these generated absolute-like addresses before programming lower-level device registers.

## Risks And Edge Cases

The file is auto-generated and explicitly says not to edit below the banner. Manual edits risk desynchronizing the driver from the ASIC register database.

The macro triplets encode a hardware ABI. A single incorrect `_BASE`, `_MAX_OFFSET`, or `_SECTION` can redirect MMIO, corrupt unrelated device state, break interrupt/error handling, or weaken security programming. This is especially risky for protection-bit code because it computes protection-bit apertures from block base addresses and register offsets.

Repeated engines invite copy/generation drift. DMA0-DMA7, TPC0-TPC7, NIC0-NIC4, MME0-MME3, SRAM bank grids, and NIF/SIF router banks should preserve expected spacing patterns, but this header also contains intentional asymmetries. Tests should distinguish real hardware-layout differences from generator mistakes.

Stride macros derived outside this file depend on stable differences between adjacent base addresses. If a block's base is changed without updating all sibling definitions, code that indexes engines by `base + index * stride` can reach the wrong engine.

The chunk boundary is mid-triplet. A chunk-only consumer must not treat line 4303 as the complete definition set for `KERNEL_TENSOR_14_TPC3_EML_TPC_CFG`; the corresponding section macro is outside this requested range.

Address widths matter. Bases are suffixed with `ull` and often exceed 32 bits. Refactors that store these values in 32-bit temporaries before subtracting `CFG_BASE` or computing offsets can truncate addresses.

Some max offsets exceed or differ from nearby section sizes. That appears to reflect generated hardware metadata rather than a simple invariant. Validation should avoid assuming `MAX_OFFSET <= SECTION` for every block without checking the generator's meaning of `SECTION`.

## Test Signals

High-signal validation for this chunk is mostly build-time, generator, and hardware bring-up oriented:

- Compile the Gaudi driver with `gaudi_regs.h` included and treat missing or duplicate macro names as failures.
- Compare this header against the authoritative ASIC register database or regeneration output; manual diffs should be empty except for intentional generator updates.
- Static-check macro triplets for every visible `mm..._BASE`: expected `_MAX_OFFSET` companion, expected `_SECTION` companion, and known exceptions such as `mmNIC0_PHY0_BASE` and the chunk-boundary TPC3 entry.
- Verify derived offsets in `gaudiP.h`: DMA QM/core stride, TPC QM/CFG stride, MME QM/ACC stride, NIC macro/engine QM stride, NIF/SIF router-control stride, HBM CFG stride, and SRAM bank stride.
- Run Gaudi bring-up or simulator tests that exercise MMIO reads/writes through representative blocks from each family: MME, DMA, TPC, NIC, HBM, PCIe, PSOC, MMU/STLB, sync manager, routers, and debug/trace blocks.
- Validate security initialization by reading back representative protection-bit words for blocks whose bases come from this chunk, especially MME ACC/SBAB/PRTN/CTRL/QM, NIC QM, TPC CFG/QM/E2E credit, DMA core/QM, and PLL blocks.
- Exercise error paths that map event IDs to block bases, including TPC CFG ECC extraction, MME ACC/SBAB ECC extraction, and QMAN error handling for TPC, MME, DMA, and NIC queue managers.
- Check 64-bit address handling under static analysis so these `ull` base constants are not truncated in intermediate calculations.

Regression indicators include failed MMIO access to known-good registers, protection-bit writes landing outside the expected block, queue-manager error handlers reporting the wrong engine, ECC extraction reading impossible syndromes, trace/debug collection failures, or asymmetric behavior between repeated engines that should be identical.
