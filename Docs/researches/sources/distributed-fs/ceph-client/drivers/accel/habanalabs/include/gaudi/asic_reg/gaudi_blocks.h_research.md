# Research: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/gaudi_blocks.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-000966`: lines 1-4303, `Docs/researches/chunks/subset-b-000966_research.md`
- `subset-b-000967`: lines 4304-4974, `Docs/researches/chunks/subset-b-000967_research.md`

## Chunk Research

### subset-b-000966: lines 1-4303

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

### subset-b-000967: lines 4304-4974

# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/gaudi_blocks.h lines 4304-4974

## Scope

This chunk is the final slice of the generated Gaudi ASIC block-address header. It starts inside the `TPC3_EML_TPC_CFG` sub-block definitions, covers the complete EML block maps for `TPC4`, `TPC5`, `TPC6`, and `TPC7`, then closes the `GAUDI_BLOCKS_H_` include guard.

The file is not Ceph filesystem logic despite its location under the Ceph-client source snapshot. It is a HabanaLabs accelerator-driver hardware address map: preprocessor constants that name Gaudi MMIO block base addresses, maximum offsets, and section spans.

## Purpose

The chunk gives the driver symbolic names for the upper half of the first-generation Gaudi Tensor Processor Core EML address space. These macros let C code refer to stable block names instead of hard-coded 64-bit MMIO addresses.

The covered blocks include:

- The tail of `TPC3_EML_TPC_CFG`, including kernel tensor 14/15, kernel sync-object, kernel TPC, QM tensor 0-15, QM sync-object, QM TPC, `TPC3_EML_TPC_QM`, and `TPC3_EML_CS`.
- Full `TPC4` through `TPC6` EML maps, each containing ROM table, SPMU, ETF, STM, CTI, FUNNEL, four BUSMON blocks, EML CFG, EML TPC CFG, kernel tensor descriptors, kernel sync object, kernel TPC view, QM tensor descriptors, QM sync object, QM TPC view, TPC QM, and CS block.
- The full visible `TPC7` EML map through `mmTPC7_EML_CS_BASE` and `TPC7_EML_CS_MAX_OFFSET`, followed immediately by the header guard close.

The values define a repeated high-address pattern. `TPC4`, `TPC5`, `TPC6`, and `TPC7` each occupy a 0x200000-wide region in the 0x7FFF800000-0x7FFFFFF000 range, with sub-block offsets repeated per TPC instance.

## Important Macros And Address Groups

This header has no functions, structs, enums, or exported runtime APIs in the usual C sense. Its API surface is the macro namespace consumed by the Gaudi driver and related generated register headers.

Each block normally has up to three macros:

- `mm..._BASE`: absolute Gaudi MMIO base address as a 64-bit `ull` constant.
- `..._MAX_OFFSET`: largest valid or described offset within the block.
- `..._SECTION`: span from this block to the next top-level generated block or sub-block grouping.

The covered `TPC4` instance is representative:

- Debug/trace/support blocks: `mmTPC4_ROM_TABLE_BASE`, `mmTPC4_EML_SPMU_BASE`, `mmTPC4_EML_ETF_BASE`, `mmTPC4_EML_STM_BASE`, `mmTPC4_EML_CTI_BASE`, `mmTPC4_EML_FUNNEL_BASE`, and `mmTPC4_EML_BUSMON_0_BASE` through `mmTPC4_EML_BUSMON_3_BASE`.
- Configuration blocks: `mmTPC4_EML_CFG_BASE` and `mmTPC4_EML_TPC_CFG_BASE`.
- Kernel descriptor views: `mmKERNEL_TENSOR_0_TPC4_EML_TPC_CFG_BASE` through `mmKERNEL_TENSOR_15_TPC4_EML_TPC_CFG_BASE`, plus `mmKERNEL_SYNC_OBJECT_TPC4_EML_TPC_CFG_BASE` and `mmKERNEL_TPC4_EML_TPC_CFG_BASE`.
- Queue-manager descriptor views: `mmQM_TENSOR_0_TPC4_EML_TPC_CFG_BASE` through `mmQM_TENSOR_15_TPC4_EML_TPC_CFG_BASE`, plus `mmQM_SYNC_OBJECT_TPC4_EML_TPC_CFG_BASE` and `mmQM_TPC4_EML_TPC_CFG_BASE`.
- Execution/control blocks: `mmTPC4_EML_TPC_QM_BASE` and `mmTPC4_EML_CS_BASE`.

`TPC5`, `TPC6`, and `TPC7` repeat the same macro layout with base addresses shifted upward by 0x200000 per TPC. For example, `mmTPC4_EML_CFG_BASE` is `0x7FFF840000ull`, `mmTPC5_EML_CFG_BASE` is `0x7FFFA40000ull`, `mmTPC6_EML_CFG_BASE` is `0x7FFFC40000ull`, and `mmTPC7_EML_CFG_BASE` is `0x7FFFE40000ull`.

## Control Flow

There is no runtime control flow in this chunk. The only control behavior is C preprocessing:

1. A source file includes `gaudi_blocks.h` directly or indirectly through Gaudi driver headers.
2. The `GAUDI_BLOCKS_H_` include guard prevents duplicate macro definitions.
3. The compiler substitutes these `#define` constants into register-access code, array initializers, debug tables, security policy code, and generated register helpers.

At runtime, control flow lives in the consumers. Examples elsewhere in the Gaudi driver include CoreSight tables that use EML STM/ETF/FUNNEL/SPMU base macros, queue-manager setup paths that depend on `TPC*_QM` address families, and security code that computes protection-bit block addresses from generated MMIO constants.

## State And Persistence Behavior

This chunk does not allocate memory, perform I/O, write registers, or persist host-side state. It defines compile-time constants only.

The constants describe persistent hardware address-map state: the Gaudi ASIC exposes these MMIO windows until reset or by virtue of the chip design. The driver source treats the generated header as the software source of truth for those windows. If the header is wrong, all compiled consumers inherit the wrong hardware address.

Because the macros are preprocessor definitions, they are not type checked beyond the expressions into which consumers place them. Most `mm..._BASE` values use the `ull` suffix, which helps preserve 64-bit addresses when used in arithmetic, but the `MAX_OFFSET` and `SECTION` constants are unsuffixed integer literals.

## Dependencies

The chunk depends on the surrounding generated header structure:

- The SPDX/license comment and generated-file warning appear at the top of `gaudi_blocks.h`.
- The `GAUDI_BLOCKS_H_` guard is opened earlier and closed in this chunk.
- Earlier portions of the file define the lower TPC, MME, DMA, NIC, SRAM, CPU, PCIe, PSOC, and other Gaudi block windows.

Consumers depend on these macros through HabanaLabs Gaudi driver includes. The values integrate with:

- Register-specific headers such as `gaudi_regs.h`, where individual register offsets are named relative to the same hardware map.
- Driver-private offset helpers in `gaudiP.h`, including patterns like `TPC_QMAN_OFFSET`, `TPC_CFG_OFFSET`, and other base-to-base deltas.
- CoreSight setup in `gaudi_coresight.c`, which uses EML trace component bases for STM, ETF, funnel, and SPMU registration.
- Security initialization code in `gaudi_security.c`, which relies on coherent generated address definitions when mapping MMIO register blocks to protection-bit storage.

## Integration Points

The main integration point is MMIO address calculation. Driver code that programs or dumps TPC EML registers uses these constants as absolute block bases, then adds register-specific offsets or derives per-instance offsets from adjacent bases.

The tensor and sync-object sub-blocks are important integration surfaces for TPC command and descriptor programming. `KERNEL_TENSOR_*` and `QM_TENSOR_*` names distinguish two views inside the same EML TPC CFG area: kernel-facing tensor descriptor registers and queue-manager-facing tensor descriptor registers. The `KERNEL_SYNC_OBJECT_*` and `QM_SYNC_OBJECT_*` blocks provide the matching synchronization-object windows, while `KERNEL_TPC*` and `QM_TPC*` identify broader TPC configuration views.

The trace/debug blocks integrate with CoreSight and diagnostics. `SPMU`, `ETF`, `STM`, `CTI`, `FUNNEL`, and `BUSMON` bases let debug code address per-TPC performance, trace, trigger, funneling, and bus-monitor blocks. The `TPC*_EML_CS_BASE` constants identify a per-TPC CoreSight/control slice near the end of each TPC EML aperture.

The `TPC*_EML_TPC_QM_BASE` constants identify queue-manager register windows. These are relevant to command submission, queue state inspection, reset/debug flows, and protection-bit policy because queue-manager registers include sensitive producer/consumer, command processor, and arbitration state in other Gaudi register headers.

## Boundary Notes

The chunk starts mid-pattern. Lines 4304-4373 finish `TPC3` EML definitions that began before this chunk, so a file-level summary should reconcile the preceding `TPC3` ROM/debug/config definitions from the previous chunk.

The chunk also ends the file. `TPC4`, `TPC5`, and `TPC6` each define `TPCx_EML_CS_SECTION 0x1000` after their CS max-offset macro. The visible `TPC7` tail defines `mmTPC7_EML_CS_BASE` and `TPC7_EML_CS_MAX_OFFSET`, then closes the include guard without a `TPC7_EML_CS_SECTION` macro. A repository search in this snapshot found no `TPC7_EML_CS_SECTION` references, so the omission is not an immediate compile dependency here, but it is a useful generated-map asymmetry for reviewers to know.

## Risks And Edge Cases

The primary risk is generated address-map drift. These macros are normally treated as authoritative; a single wrong base, offset, or section size can redirect MMIO to a different hardware block, break diagnostics, corrupt queue-manager programming, or weaken protection-bit calculations.

The repetitive TPC layout is easy to misread. Most `TPC4` through `TPC7` macros differ only by the TPC number and high address nibble. Copy/paste or generator bugs can leave one instance pointing into another instance's aperture while still compiling cleanly.

The `SECTION` values are not always the same as `MAX_OFFSET`. For example, the EML TPC CFG block has a 0x4000 section while nested tensor/sync/TPC sub-blocks have larger max-offset values that describe address reach within the parent aperture. Consumers should not blindly interpret `SECTION` as the legal register range for every nested block without checking how the generated map defines it.

The chunk exposes 64-bit MMIO addresses near the top of the Gaudi address map. Any consumer that truncates `mm..._BASE` values to 32 bits before adding `CFG_BASE` adjustments, protection-bit offsets, or register offsets will compute invalid addresses.

The final `TPC7_EML_CS` asymmetry is low risk if no code expects `TPC7_EML_CS_SECTION`, but it is still a regression signal for scripts that assume every block has a base/max/section triple. New generated-map validation should account for final-block exceptions or intentionally flag this as a missing macro if the hardware specification says it should exist.

Because this is an auto-generated header marked "DO NOT EDIT", manual changes are risky. Fixes should normally be made in the register-map generator or source data, then regenerated consistently across related headers.

## Test Signals

Useful validation is mostly static, build-time, and hardware bring-up oriented:

- Build the Gaudi driver code that includes `gaudi_blocks.h` and ensure no macro consumers fail on the TPC3-tail through TPC7 definitions.
- Run a generated-map consistency check that verifies `TPC4`, `TPC5`, `TPC6`, and `TPC7` share the same relative offsets for ROM, SPMU, ETF, STM, CTI, FUNNEL, BUSMON, CFG, TPC_CFG, tensor descriptors, sync objects, TPC_QM, and CS.
- Verify the expected 0x200000 stride between corresponding `TPC4`-`TPC7` EML bases.
- Check that section spans line up with the next block base where that is the intended meaning, especially `TPCx_EML_TPC_QM_SECTION 0x1BD000` leading to `TPCx_EML_CS_BASE`.
- Compile or run any scripts that derive protection-bit or register-dump regions from `mm..._BASE`, `MAX_OFFSET`, and `SECTION` macros, with attention to the missing `TPC7_EML_CS_SECTION`.
- On real hardware or a simulator, read harmless identification/status registers in representative TPC4-TPC7 EML trace/config/QM windows and confirm the addresses hit the expected TPC instance.
- Exercise CoreSight registration and debug collection for `TPC4` through `TPC7` EML components. Failures to read STM/ETF/FUNNEL/SPMU blocks are strong signals that the base map is wrong.
- Exercise TPC queue-manager bring-up and security/protection-bit initialization for TPC4-TPC7, watching for RAZWI events, MMIO faults, queue setup failures, or instance-asymmetric behavior.
