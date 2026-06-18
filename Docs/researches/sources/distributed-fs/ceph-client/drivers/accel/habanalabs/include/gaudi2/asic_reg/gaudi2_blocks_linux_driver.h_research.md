# Research: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/gaudi2_blocks_linux_driver.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-000986`: lines 1-4331, `Docs/researches/chunks/subset-b-000986_research.md`
- `subset-b-000987`: lines 4332-8831, `Docs/researches/chunks/subset-b-000987_research.md`
- `subset-b-000988`: lines 8832-13499, `Docs/researches/chunks/subset-b-000988_research.md`
- `subset-b-000989`: lines 13500-18084, `Docs/researches/chunks/subset-b-000989_research.md`
- `subset-b-000990`: lines 18085-22762, `Docs/researches/chunks/subset-b-000990_research.md`
- `subset-b-000991`: lines 22763-27893, `Docs/researches/chunks/subset-b-000991_research.md`
- `subset-b-000992`: lines 27894-32825, `Docs/researches/chunks/subset-b-000992_research.md`
- `subset-b-000993`: lines 32826-37748, `Docs/researches/chunks/subset-b-000993_research.md`
- `subset-b-000994`: lines 37749-42833, `Docs/researches/chunks/subset-b-000994_research.md`
- `subset-b-000995`: lines 42834-45067, `Docs/researches/chunks/subset-b-000995_research.md`

## Chunk Research

### subset-b-000986: lines 1-4331

# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/gaudi2_blocks_linux_driver.h lines 1-4331

## Scope

This chunk is the opening slice of the auto-generated Gaudi2 block-map header used by the Habana Labs Linux accelerator driver. It covers the file preamble, include guard, and the first 4,317 `#define` register-window macros. The visible range describes tensor-processing-core (TPC) and embedded logic (EML) block windows from `DCORE0_TPC0` through all of `DCORE2_TPC4`, then stops inside the beginning of `DCORE2_TPC5` after `DCORE2_TPC5_EML_TPC_CFG_KERNEL_TENSOR_2_MAX_OFFSET`.

The code is not Ceph distributed filesystem logic despite living in a Ceph-client source snapshot. It is ASIC register-address metadata for the upstream-style Linux `habanalabs` accelerator driver.

## Purpose

The header gives driver C code symbolic names for Gaudi2 MMIO block base addresses, maximum offsets, and section spans. In this chunk, every hardware window follows a generated triplet pattern:

- `mm..._BASE`: an unsigned 64-bit MMIO base address, written with an `ull` suffix.
- `..._MAX_OFFSET`: the register-window size or legal offset limit for that block.
- `..._SECTION`: the generated span to the next related block or section boundary.

The purpose is to keep low-level driver code from hard-coding numeric offsets when programming, dumping, protecting, or validating Gaudi2 TPC-related hardware blocks. The constants define the address layout for TPC ROM tables, embedded trace/debug blocks, queue-manager ARC memories, TPC configuration blocks, tensor descriptor regions, sync objects, queue-manager apertures, AXUSER attributes, debug windows, clock-gating controls, and common CS windows across DCORE instances.

## Important APIs, Types, And Functions

This chunk contains no functions, structs, enums, inline helpers, or executable APIs. Its interface is the C preprocessor symbol set exported by `gaudi2_blocks_linux_driver.h`.

The visible file-level wrapper is:

- `GAUDI2_BLOCKS_LINUX_DRIVER_H_`: include guard that prevents duplicate macro definitions in a single translation unit.

The important macro families are:

- `mmDCORE*_TPC*_ROM_TABLE_BASE`, plus matching max offset and section macros, for 4 KiB ROM-table windows at the start of each TPC aperture.
- `mmDCORE*_TPC*_EML_SPMU_BASE`, `EML_ETF`, `EML_STM`, `EML_CTI`, `EML_FUNNEL`, and `EML_BUSMON_0..3`, which define embedded monitoring, tracing, cross-trigger, funnel, and bus-monitor windows.
- `mmDCORE*_TPC*_QM_ARC_RTT_BASE`, with `MAX_OFFSET 0x1400` and a larger `SECTION 0x35000`, for the TPC queue-manager ARC RTT area.
- `mmDCORE*_TPC*_EML_CFG_BASE` and `EML_CFG_SPECIAL_BASE`, for EML configuration and special-register windows.
- `mmDCORE*_TPC*_EML_TPC_CFG_BASE` and the nested `KERNEL_TENSOR_0..15`, `KERNEL_SYNC_OBJECT`, `KERNEL`, `QM_TENSOR_0..15`, `QM_SYNC_OBJECT`, `QM`, `AXUSER`, and `SPECIAL` windows, which model the TPC configuration and queue-manager-visible tensor/sync/user-attribute regions.
- `mmDCORE*_TPC*_EML_QM_DCCM_BASE`, `EML_QM_ARCAUX_BASE`, and `EML_QM_ARCAUX_SPECIAL_BASE`, which describe local QM memory and ARC auxiliary register windows.
- `mmDCORE*_TPC*_EML_TPC_QM_BASE` and nested `QMAN_WR64_BASE_ADDR0..15`, `AXUSER_SECURED`, `AXUSER_NONSECURED`, `DBG_HBW`, `DBG_LBW`, `CGM`, and `SPECIAL` windows, which define queue-manager command, address, attribute, debug, and clock-gating/register-special regions.
- `mmDCORE*_TPC*_EML_CS_BASE`, the closing common/status window for each TPC block aperture.

## Address Layout And Repetition

The visible range is highly regular. Each complete TPC instance contributes 79 `mm..._BASE` macros and 158 non-`mm` companion macros for a total of 237 definitions. In lines 1-4331, the complete TPC instances are:

- `DCORE0_TPC0` through `DCORE0_TPC6`.
- `DCORE1_TPC0` through `DCORE1_TPC5`.
- `DCORE2_TPC0` through `DCORE2_TPC4`.

The assigned chunk also includes the first 33 macros of `DCORE2_TPC5`, ending in its early `EML_TPC_CFG_KERNEL_TENSOR_2` region. The full `DCORE2_TPC5` block therefore belongs partly to the next chunk and should be reconciled there by the merge lane.

Within a complete TPC instance, the base addresses step through a consistent local aperture:

- TPC aperture start: `ROM_TABLE_BASE`.
- Early 4 KiB debug/trace windows: `SPMU`, `ETF`, `STM`, `CTI`, `FUNNEL`, `BUSMON_0..3`.
- Queue-manager ARC RTT at local `0xB000`.
- EML CFG at local `0x40000`, then TPC CFG/tensor/sync/QM descriptor subwindows beginning at local `0x41000`.
- QM DCCM and ARCAUX at local `0x42000` and `0x4A000`.
- TPC QM command-manager region at local `0x4C000`, with 16 `QMAN_WR64_BASE_ADDR*` bases spaced eight bytes apart.
- Closing EML CS at the end of the TPC aperture, such as `DCORE0_TPC0_EML_CS_BASE 0x1FF000`.

Most complete TPC apertures are spaced by `0x200000`. DCORE transitions add larger section spans on the last TPC of a DCORE in this chunk, for example `DCORE0_TPC6_EML_CS_SECTION 0x201000` before `DCORE1_TPC0`, and `DCORE1_TPC5_EML_CS_SECTION 0x401000` before `DCORE2_TPC0`. These section spans are metadata for traversing the generated register block map and should not be assumed to be the same as each block's max offset.

## Control Flow

There is no runtime control flow in this chunk. The only compile-time flow is normal header inclusion:

1. A C file includes `gaudi2_blocks_linux_driver.h`.
2. The include guard defines `GAUDI2_BLOCKS_LINUX_DRIVER_H_` the first time the header is seen.
3. The compiler/preprocessor makes the generated address constants available to subsequent code.

All runtime behavior happens in other driver files that consume these macros for MMIO reads, MMIO writes, debug dumping, register range checks, or protection programming.

## State And Persistence Behavior

This chunk does not allocate memory, mutate kernel state, persist data, or directly touch hardware. It defines constants only.

The constants represent persistent ASIC address-map knowledge: if they are wrong, every consumer compiled against this header will target wrong MMIO windows until the driver is rebuilt with corrected definitions. The hardware state itself is changed only when other code uses these addresses with MMIO helpers.

Because the file is auto-generated and marked "DO NOT EDIT BELOW," the true source of persistence is likely an internal register database or generation pipeline rather than this checked-in header alone. Manual edits to this file would be fragile and likely overwritten by regeneration.

## Dependencies And Integration Points

The direct dependency is the C preprocessor and the consumers that include this header. There are no local include directives in this slice beyond the include guard.

Primary integration points are Habana Labs Gaudi2 driver code that needs block-level register windows, including likely code paths for:

- MMIO register access through `RREG32`, `WREG32`, or equivalent helpers.
- Device bring-up and reset flows that program TPC, QM, ARC, EML, AXUSER, and debug register blocks.
- Debugfs or diagnostic register dumps that iterate over generated block ranges using base, max-offset, and section metadata.
- Security/protection logic that maps named hardware blocks to address ranges.
- Error handling paths that decode addresses back to TPC/DCORE regions.

The header sits under `drivers/accel/habanalabs/include/gaudi2/asic_reg`, so it integrates with Gaudi2-specific ASIC register headers rather than common Linux subsystem APIs.

## Risks And Edge Cases

Generated headers are brittle at the consumer boundary. A stale or incorrect base address can silently redirect an MMIO operation to the wrong hardware block, which may cause device initialization failures, misreported diagnostics, security gaps, or register writes with unintended side effects.

The repeated macro names are easy to misuse. For each block, `MAX_OFFSET` and `SECTION` are different concepts. Some `SECTION` values are much larger than max offset, especially for `QM_ARC_RTT`, `TPC_QM_SPECIAL`, and DCORE-boundary `EML_CS` entries. Code that treats section spans as safe register access limits could overrun a block's intended register window.

Several generated definitions are duplicated or alias-like within each TPC instance. For example, `EML_CFG_SPECIAL_SECTION` appears before and after `EML_TPC_CFG_KERNEL_TENSOR_0_BASE` in each complete TPC group, and `EML_TPC_CFG_BASE` shares the same base as `KERNEL_TENSOR_0`. This is probably intentional generator output, but duplicate macro names can hide drift if the generator ever emits conflicting values.

The chunk boundary cuts through `DCORE2_TPC5`. Any file-level research or generated summaries must merge this note with the next chunk before drawing conclusions about the full DCORE2 TPC5 address map.

The constants use `ull`, which is appropriate for the 64-bit-looking MMIO namespace. Consumers that store these values in narrower integer types risk truncation as addresses grow past 32-bit ranges.

## Test Signals

Useful validation signals for this chunk are mostly static or hardware-integration oriented:

- Kernel build succeeds with no macro redefinition warnings or missing symbol errors from Gaudi2 driver consumers.
- Static checks confirm every complete TPC block in this slice has the expected 79 base macros plus matching `MAX_OFFSET` and `SECTION` companions.
- Generated register-dump tooling can walk from `DCORE0_TPC0` through `DCORE2_TPC4` without overlapping ranges unexpectedly or treating section spans as max offsets.
- On Gaudi2 hardware or simulation, driver initialization can access TPC/QM/EML registers named from these macros without MMIO faults, RAZWI events, or address decode errors.
- Security and debug tests that use TPC QM, AXUSER, debug HBW/LBW, and special-register windows hit the expected DCORE/TPC instance.
- Regeneration from the source register database produces byte-for-byte identical definitions for lines 1-4331, except for known generator-version changes.

### subset-b-000987: lines 4332-8831

# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/gaudi2_blocks_linux_driver.h lines 4332-8831

## Scope

This chunk covers a 4,500-line slice of the auto-generated Gaudi2 block address map used by the Habana Labs accelerator driver. The file is explicitly marked generated and included by `include/gaudi2/asic_reg/gaudi2_regs.h`, which then fans these constants into the Gaudi2 driver, security setup, MMU setup, queue-manager setup, RAZWI/error reporting, and user-mapped block descriptions.

Every line in this range is a preprocessor `#define`. There are exactly 1,500 register-block entries, and each entry is represented as a triplet:

- `mm..._BASE`: absolute MMIO base address for a hardware block.
- `..._MAX_OFFSET`: maximum register offset considered valid for that block.
- `..._SECTION`: mapped/stride section size used to step to the next related block or to describe the block aperture.

The range starts in the middle of the DCORE2 TPC5 EML TPC configuration block at `DCORE2_TPC5_EML_TPC_CFG_KERNEL_TENSOR_2_SECTION`, continues through all DCORE3 TPC0-TPC5 EML/TPC-QM block descriptors, then describes DCORE0 TPC0-TPC6 queue/config blocks, DCORE0 HMMU0-HMMU3 blocks, DCORE0 MME blocks, DCORE0 sync-manager blocks, DCORE0 HIF0-HIF3 blocks, and the start of DCORE0 router blocks through `DCORE0_RTR2_RTR_LBW_XACT_STAT_MAX_OFFSET`. The following chunk continues with `DCORE0_RTR2_RTR_LBW_XACT_STAT_SECTION`, remaining RTR2 debug blocks, and DCORE0 RTR3.

This is not filesystem code despite the repository path containing `distributed-fs/ceph-client`; it is Linux kernel accelerator-driver hardware metadata for Gaudi2 devices.

## Purpose

The chunk provides the generated block-level MMIO layout that higher-level Gaudi2 code uses to calculate register addresses safely and consistently. It does not define individual registers, bit fields, executable logic, or data structures. Instead, it supplies the base apertures on top of which per-block register headers such as `dcore0_tpc0_qm_regs.h`, `dcore0_hmmu0_mmu_regs.h`, `dcore0_sync_mngr_objs_regs.h`, and router/master-interface headers define individual offsets.

The covered hardware domains are:

- Tail of DCORE2 TPC5 EML configuration and TPC-QM blocks around `0x2A410A0` through `0x2BFF000`.
- DCORE3 TPC0-TPC5 EML blocks from `0x3000000` through `0x3E3FF000`, including coresight/debug blocks, ARC RTT, EML CFG, tensor configuration, sync-object windows, QMAN windows, AXUSER windows, DCCM/ARCAUX, TPC-QM WR64 base-address arrays, CGM, special blocks, and CS windows.
- DCORE0 TPC0-TPC6 non-EML QMAN/configuration blocks from `0x4000000` through `0x406FE80`, including QM DCCM, ARCAUX, TPC_QM, WR64 base-address registers, AXUSER secured/nonsecured apertures, debug HBW/LBW, CGM, CFG tensor windows, kernel/QM sync-object windows, and master-interface sub-blocks.
- DCORE0 HMMU0-HMMU3 from `0x4080000` through `0x40BFE80`, covering MMU/STLB, HBW/LBW AXI master interfaces, RR shared/private HBW/LBW windows, E2E credit windows, AXUSER, debug, core HBW/LBW, and special blocks.
- DCORE0 MME from `0x40C0000` through `0x40FAE80`, covering MME QMAN/ARC/DCCM, QMAN WR64 base-address arrays, AXUSER, debug/CGM, duplicate engine, accelerator, sync-object windows, SBTE, control low block, AGU/tensor/non-tensor sub-blocks, WBC/WB blocks, and MME master interfaces.
- DCORE0 sync-manager, HIF, and router infrastructure from `0x4100000` through `0x4154680`, covering sync objects/global state/master interfaces, host-interface special blocks, and RTR0-RTR2 router control/H3/master-interface/address-decoder/transaction-stat windows.

## Important APIs, Types, And Constants

There are no C functions, structs, enums, or runtime APIs in this chunk. The important "API" is the naming and value convention of the generated macros:

- `mmDCORE*_..._BASE` macros provide 64-bit literal MMIO bases with an `ull` suffix. Callers use them directly in address arithmetic and register access macros.
- `DCORE*_..._MAX_OFFSET` macros express the maximum offset within the named register block. These are commonly paired with block-size validation, generated register offsets, debug traversal, and range checks.
- `DCORE*_..._SECTION` macros describe the aperture/stride assigned to the block. Many are larger than the max offset because the hardware address map leaves reserved space before the next block.
- Repeated tensor blocks (`*_KERNEL_TENSOR_0..15`, `*_QM_TENSOR_0..15`) are separated by `0x50`-byte base increments while sharing wider `0x5000` section metadata.
- Repeated QMAN WR64 base-address blocks (`*_QMAN_WR64_BASE_ADDR0..15`) are separated by `0x8`-byte base increments while generally sharing `0x8000` max/section metadata, except the last entry in several groups has a shorter section because it ends the local sub-aperture.
- DCORE-level arithmetic elsewhere depends on regular spacing. For example, DCORE3 TPC instances are laid out at `0x3000000`, `0x3200000`, `0x3400000`, `0x3600000`, `0x3800000`, and `0x3A00000`, while DCORE0 TPC QMAN DCCM blocks start at `0x4000000` and increment by `0x10000`.

Representative constants in this range include:

- `mmDCORE3_TPC0_ROM_TABLE_BASE` through `mmDCORE3_TPC5_EML_CS_BASE` for DCORE3 TPC debug/EML/TPC-QM apertures.
- `mmDCORE0_TPC0_QM_DCCM_BASE` through `mmDCORE0_TPC6_MSTR_IF_SPECIAL_BASE` for DCORE0 TPC queue/config/master-interface apertures.
- `mmDCORE0_HMMU0_MMU_BASE` through `mmDCORE0_HMMU3_MSTR_IF_SPECIAL_BASE` for DCORE0 HMMU and HMMU master-interface programming.
- `mmDCORE0_MME_QM_ARC_DCCM_BASE`, `mmDCORE0_MME_QM_BASE`, `mmDCORE0_MME_ACC_BASE`, `mmDCORE0_MME_CTRL_LO_BASE`, `mmDCORE0_MME_SBTE0_BASE`, and `mmDCORE0_MME_WB*_MSTR_IF_*_BASE` for DCORE0 MME control and data-movement windows.
- `mmDCORE0_SYNC_MNGR_OBJS_BASE` and `mmDCORE0_SYNC_MNGR_GLBL_BASE` for sync-manager user/object and global windows.
- `mmDCORE0_RTR0_CTRL_BASE`, `mmDCORE0_RTR1_CTRL_BASE`, and `mmDCORE0_RTR2_CTRL_BASE` for router control and diagnostics.

## Control Flow

There is no executable control flow in this header slice. Runtime flow is indirect:

1. Source files include `gaudi2_regs.h`.
2. `gaudi2_regs.h` includes this generated block map before including per-block register-offset headers.
3. Gaudi2 code combines a block base from this file with a per-register offset from another generated header or with an arithmetic stride such as `DCORE_OFFSET`, `DCORE_HMMU_OFFSET`, or router instance offsets.
4. Register access helpers such as `RREG32`, `WREG32`, and `RMWREG32` use the resulting absolute addresses to program or inspect the device.

Examples of actual call-site patterns visible in adjacent driver code:

- `gaudi2_user_mapped_blocks_init()` uses `mmDCORE0_SYNC_MNGR_OBJS_BASE + i * DCORE_OFFSET` and `mmDCORE0_SYNC_MNGR_GLBL_BASE + i * DCORE_OFFSET` to expose sync-manager blocks for other DCOREs.
- `gaudi2_security.c` seeds protection-block metadata with `mmDCORE0_SYNC_MNGR_OBJS_BASE`, router bases such as `mmDCORE0_RTR0_CTRL_BASE`, and HMMU bases such as `mmDCORE0_HMMU0_MMU_BASE`.
- `gaudi2.c` uses `mmDCORE0_TPC0_QM_DCCM_BASE` and `mmDCORE0_MME_QM_ARC_DCCM_BASE` in ARC/DCCM base tables, `mmDCORE0_HMMU0_MMU_BASE` in MMU base calculation, and `mmDCORE0_RTR0_CTRL_BASE` in RAZWI/router diagnostic address derivation.

## State And Persistence Behavior

This chunk has no mutable state and persists nothing at runtime. Its macros are compile-time constants embedded into driver code. The state effects happen only when callers use the constants to access hardware:

- Queue-manager and ARC-related bases identify DCCM, ARCAUX, QMAN, CGM, WR64, AXUSER, and debug windows that the driver programs during engine initialization, queue setup, context restore, diagnostics, and reset handling.
- TPC CFG tensor and sync-object bases identify per-engine tensor configuration and sync apertures that can be reset, restored, or used by command submission paths.
- HMMU bases identify MMU/STLB and master-interface windows that persist context ASID, page-table, bypass, AXUSER, and error-reporting configuration until reset or reprogramming.
- MME bases identify QMAN, accelerator, SBTE, tensor, writeback, and control windows that hold runtime engine configuration, error causes, and completion/synchronization state.
- Sync-manager object/global bases identify SOB/monitor/CQ resources. These hardware values are runtime synchronization state; the constants only locate the apertures.
- Router and HIF bases identify routing, RAZWI, address-decoder, transaction-statistic, and host-interface diagnostic/protection windows.

Because the file is generated, source-of-truth persistence is external to the C source tree. Manual edits would be overwritten by regeneration and could desynchronize the driver from the hardware spec.

## Dependencies And Integration Points

The direct dependency is `gaudi2_regs.h`, which includes this header before the detailed register headers. That aggregate header is then included by Gaudi2 driver and security code. The constants in this chunk integrate with:

- Generated per-block register headers for individual offsets and masks.
- Gaudi2 topology constants such as DCORE count, TPC/MME/HMMU/router instance counts, and inter-instance offsets.
- Common Habana Labs register-access macros and helper functions that expect absolute MMIO addresses.
- Security/protection setup code that uses base/section relationships to configure protected blocks and special regions.
- User-mapped block initialization, where selected hardware windows are exposed to user space with fixed sizes.
- MMU initialization and error handling, where HMMU base constants are combined with dcore and instance offsets.
- RAZWI and router diagnostics, where router base constants anchor captured-address and initiator decoding.
- Queue and engine metadata tables in `gaudi2.c`, especially DCCM/QMAN/ARC base tables for TPC and MME blocks.

The `*_MAX_OFFSET` and `*_SECTION` values are important for tooling and traversal even when individual hand-written call sites primarily reference only `mm..._BASE` constants.

## Risks And Edge Cases

The main risk is silent address-map drift. Since these constants are compile-time values, an incorrect base, offset, or section can make the driver read or write the wrong hardware block with no type-system help.

Boundary risk is present because this work item starts and ends inside logical hardware groups. It begins with only the `SECTION` line for `DCORE2_TPC5_EML_TPC_CFG_KERNEL_TENSOR_2`; the corresponding `BASE` and `MAX_OFFSET` are on the previous lines. It also ends at `DCORE0_RTR2_RTR_LBW_XACT_STAT_MAX_OFFSET`; the `SECTION` and later RTR2 blocks are outside this chunk. Any merge-stage summary should reconcile those split triplets with adjacent chunks.

Repeated block families rely on exact enum/topology ordering. TPC, HMMU, MME, sync-manager, HIF, and RTR callers often derive later instances from DCORE0/DCORE3 base constants plus offsets. A single irregular section size or instance gap can invalidate arithmetic assumptions.

Some section sizes intentionally exceed max offsets. Treating `SECTION` as the valid register range, or treating `MAX_OFFSET` as the stride, would produce incorrect mapping and traversal behavior.

There are a few generated oddities worth preserving rather than normalizing by hand:

- Duplicate-looking `*_CFG_SPECIAL_SECTION` lines occur around TPC CFG/kernel tensor transitions in this generated map.
- Several last WR64 base-address entries have shortened sections.
- The DCORE2 TPC5 and DCORE0 RTR2 content is split across chunk boundaries.

Security and user mapping are sensitive consumers. A wrong sync-manager base or section could expose the wrong MMIO aperture to user space or configure protection bits for the wrong block. A wrong HMMU or router base could break MMU fault reporting, RAZWI attribution, or protected-block programming.

## Test Signals

Useful validation signals for this header are compile-time, generated-map, and hardware-integration signals:

- The driver builds with `gaudi2_regs.h` including this file and all referenced `mm..._BASE`, `*_MAX_OFFSET`, and `*_SECTION` macros resolving.
- Generated-map consistency checks confirm every complete block entry has a base/max/section triplet and that adjacent chunks complete the split DCORE2 TPC5 and DCORE0 RTR2 entries.
- Probe/init succeeds on Gaudi2 hardware or simulation without invalid MMIO access warnings when initializing TPC, HMMU, MME, sync-manager, HIF, and router blocks.
- MMU tests exercise HMMU0-HMMU3 base calculations and confirm page-table, ASID, STLB, and MMU error-register accesses hit the expected blocks.
- Queue/engine tests exercise TPC0-TPC6 and MME QMAN/DCCM/ARCAUX bases, including ARC DCCM scrubbing, QMAN setup, WR64 base programming, AXUSER setup, and debug register reads.
- Security/protection tests confirm protected-block configuration covers the intended sync-manager, HMMU, HIF, router, TPC, and MME apertures without over-covering neighboring blocks.
- User-mapped-block tests confirm sync-manager object/global addresses derived from `mmDCORE0_SYNC_MNGR_*_BASE` plus `DCORE_OFFSET` map the expected DCORE apertures.
- Error-injection or diagnostic tests confirm RAZWI/router reports use the expected RTR0-RTR2 base addresses and that transaction-stat windows report HBW/LBW/E2E activity from the intended router instance.
- Regeneration diff review should flag any unexpected changes to base alignment, max offsets, or section sizes in this range, especially for repeated tensor, WR64, HMMU, MME, sync-manager, and router families.

### subset-b-000988: lines 8832-13499

# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/gaudi2_blocks_linux_driver.h lines 8832-13499

## Scope

This chunk is a generated Gaudi2 Linux-driver register block map. It contains only preprocessor constants: 4,668 `#define` lines, organized as 1,556 block-address triplets of `mm..._BASE`, `..._MAX_OFFSET`, and `..._SECTION` values. There are no C functions, structs, branches, or executable control flow in this range.

The covered address window starts at the tail of the DCORE0 router map around `DCORE0_RTR2_RTR_LBW_XACT_STAT_SECTION`, continues through DCORE0 router instances 3-7, DCORE0 SRAM banks 0-7, DCORE0 EDMA0/EDMA1, DCORE0 decoder and video decoder blocks, then enters DCORE1 with HIF0-HIF3, sync-manager, TPC0-TPC5, HMMU0-HMMU3, MME, router instances 0-7, and the beginning of DCORE1 SRAM0 debug-counter definitions. The first and last lines are chunk boundaries inside generated block groups: adjacent chunks carry the missing partner definitions for the first/last triplets.

This is accelerator driver hardware description data, not Ceph filesystem logic, despite being stored under the `sources/distributed-fs/ceph-client` source snapshot.

## Purpose

The header gives the Habana Labs Gaudi2 driver symbolic names for memory-mapped hardware block ranges. Driver code can use the macros to compute register addresses, validate block mmap ranges, iterate special blocks, program MMU/AXUSER/QMAN registers, diagnose RAZWI and fabric errors, and dump or clear status counters without hard-coding numeric addresses at each call site.

The macro naming convention carries most of the semantics:

- `mm<block>_BASE` is the absolute MMIO base address for the block or sub-block.
- `<block>_MAX_OFFSET` is the maximum register offset or range bound expected for that block class.
- `<block>_SECTION` is the spacing to the next repeated section, bank, engine, or logical slice when a block has generated instances.

The values use `ull` suffixes for base addresses so callers can safely hold them in 64-bit arithmetic before eventually using lower-level `RREG32`, `WREG32`, BAR mapping, or mmap helpers.

## Important Macro Families

DCORE0 router definitions:

- The range opens at the tail of `DCORE0_RTR2` transaction-status/debug-address definitions, then fully covers `DCORE0_RTR3` through `DCORE0_RTR7`.
- Each full router instance has control and H3 blocks; master-interface range-register, AXUSER, debug, E2E credit, and core HBW/LBW blocks; address decoder HBW/LBW blocks; router status blocks; link-layer statistics for HBW/LBW read/write request/response channels; MFIFO and E2E statistics; special blocks; and debug-address special ranges.
- Common section sizes encode hardware layout: many control/H3/debug blocks use `0xE800`, special blocks use `0x1800`, master RR lanes use `0x2000`, transaction statistics use `0x8000`, E2E router statistics often use `0x7800`, and debug-address special sections use `0x2180`.

DCORE0 SRAM definitions:

- `DCORE0_SRAM0` through `DCORE0_SRAM7` define bank and router bases, matching special ranges, and debug-counter groups.
- Each SRAM bank includes north/south/left HBW and LBW debug counters, left-bank0/left-bank1 HBW counters, HBW/LBW link-layer read/write request/response statistic counters, and a debug-counter special block.
- The banks are laid out at regular `0x8000` strides from `0x4180000` through `0x41B8000`, with per-bank internal offsets such as bank at `+0x0000`, router at `+0x1000`, debug counters at `+0x2000`, and special windows at `+0x0E80`, `+0x1E80`, or `+0x2E80`.

DCORE0 EDMA definitions:

- `DCORE0_EDMA0` and `DCORE0_EDMA1` each include queue-manager DCCM, ARC AUX, QMAN control, WR64 base-address registers 0-15, secured/non-secured AXUSER, debug HBW/LBW, CGM, special blocks, DMA core, core context, context AXUSER, KDMA CGM, and master-interface blocks.
- The QMAN WR64 base-address entries are eight-byte spaced register slots with large `0x8000` max-offset ranges and a shorter final section (`0x1880`) for the last entry in the group.
- These macros back EDMA initialization, queue tests, memory scrubbing, MMU-bypass setup, and DMA error/idle diagnostics in the Gaudi2 driver implementation.

DCORE0 decoder/video decoder definitions:

- `DCORE0_DEC0` and `DCORE0_DEC1` provide `CMD`, `L2C`, and `VSI` blocks.
- `DCORE0_VDEC0` and `DCORE0_VDEC1` provide control blocks, video bridge read/write request/response status and transaction-statistics blocks, bridge special blocks, and master-interface blocks.
- Decoder ranges are used by decoder init/stop paths, abnormal/normal interrupt handling, idle checks, and user-visible block mmap support.

DCORE1 HIF, sync-manager, HMMU, TPC, MME, router, and SRAM definitions:

- `DCORE1_HIF0` through `DCORE1_HIF3` define host-interface base and special windows.
- `DCORE1_SYNC_MNGR_OBJS`, `DCORE1_SYNC_MNGR`, and `DCORE1_SYNC_MNGR_RESERVED_*` cover sync-manager object space, reserved monitor/SOB/CQ style regions, AXUSER/debug/core windows, and special ranges.
- `DCORE1_TPC0` through `DCORE1_TPC5` repeat the TPC layout: QMAN DCCM/ARC AUX/QMAN/WR64/AXUSER/debug/CGM/special ranges, TPC config, 16 kernel tensor descriptors, kernel sync object, kernel config block, 16 QM tensor descriptors, QM sync object, QM config block, config AXUSER/special, and master-interface blocks.
- `DCORE1_HMMU0` through `DCORE1_HMMU3` define MMU, STLB, scramble-output, and master-interface windows for the four HBM MMU instances in this dcore.
- `DCORE1_MME` is the densest family in the chunk. It includes MME QMAN/ARC/DUP-engine ranges, QMAN WR64 entries, AXUSER/debug/CGM/special blocks, `CTRL_LO` and `CTRL_HI` architectural tensor/AGU/metadata ranges, accumulator and EU ranges, SBTE0-SBTE4 blocks, and WB0/WB1 blocks.
- `DCORE1_RTR0` through `DCORE1_RTR7` mirror the DCORE0 router pattern with bases beginning at `0x4340000` for RTR0 and ending near `0x437DE80` for RTR7 debug-address special.
- The chunk ends at `DCORE1_SRAM0_DBG_CNT_S_LBW_DBG_CNT_MAX_OFFSET`; the corresponding section macro is outside this chunk.

## Control Flow

There is no runtime control flow in this header chunk. The effective flow is compile-time substitution:

1. C source includes Gaudi2 register headers.
2. The preprocessor replaces symbolic block names with numeric constants.
3. Driver code combines base macros with register offsets or table indexes.
4. Register access helpers, mmap helpers, special-block iterators, firmware event handlers, and error-dump code use those computed addresses to read or write device MMIO.

The generated order is still operationally important. Many families are mechanically ordered by physical topology, for example router instance number, SRAM bank number, EDMA engine number, TPC number, HMMU number, MME sub-block, then DCORE1 router number. Code and generated tables in adjacent driver files often assume those families stay aligned with enum order, queue IDs, engine IDs, or special-block metadata.

## State And Persistence Behavior

The chunk itself stores no mutable state and creates no persistence. It is a static hardware-address contract compiled into the kernel driver.

Runtime state affected indirectly includes:

- Hardware MMIO registers addressed through these bases.
- Driver tables that hold block bases for QMANs, TPCs, MME, HMMUs, routers, SRAM debug counters, and user-mappable blocks.
- Kernel logs and debug dumps that name or traverse these blocks while diagnosing MMU faults, RAZWI captures, QMAN failures, link-layer errors, ECC, decoder issues, DMA state, and idle status.
- User-visible mmap validation where a block base and allowed extent determine which MMIO windows can be exposed.

Any value change in this header is persistent at the build-artifact level: the compiled driver will target different device addresses until rebuilt again.

## Dependencies And Integration Points

The direct dependency is the C preprocessor and any Gaudi2 source file that includes `gaudi2_blocks_linux_driver.h` directly or through broader generated register-map headers. The values integrate with the rest of the Habana Labs driver through:

- Gaudi2 implementation code in `drivers/accel/habanalabs/gaudi2/gaudi2.c`, which uses generated `mm...` names in register reads/writes, queue/engine initialization, MMU setup, event handlers, reset paths, idle checks, and block mmap.
- Generated register field/mask headers such as `gaudi2_masks.h` and block-specific register headers, which provide offsets and bit fields that are added to these bases.
- Common driver helpers such as `RREG32`, `WREG32`, `RMWREG32`, `hl_poll_timeout`, MMU helpers, firmware helpers, debugfs/state-dump paths, and user mmap paths.
- Hardware topology constants and tables for DCOREs, TPCs, EDMAs, HMMUs, MME engines, routers, SRAM banks, decoders, sync-manager objects, and queue managers.
- Firmware and diagnostic interfaces that report event IDs or engine IDs; handlers map those IDs to the relevant generated block base before reading cause, status, or address-capture registers.

## Risks And Edge Cases

The highest risk is silent address skew. A wrong base, section stride, or max offset will still compile but can make the driver program the wrong hardware block, read misleading fault state, expose the wrong mmap window, or fail to clear an interrupt.

Generated repetition makes off-by-one and copy-generation errors hard to spot manually. This chunk has several long repeated families whose only differences are dcore number, engine number, bank number, tensor index, or small base-address increments. Review should compare generated output against the ASIC register database, not against hand intuition.

Boundary handling matters for chunked research and reconciliation. The first line is only `DCORE0_RTR2_RTR_LBW_XACT_STAT_SECTION`; its base and max-offset definitions are above this range. The final visible block is only partially represented: `mmDCORE1_SRAM0_DBG_CNT_S_LBW_DBG_CNT_BASE` and its max offset are present, while the section macro is after line 13499.

There is a duplicate-looking `DCORE1_TPC4_QM_SPECIAL_SECTION 0x1800` near the transition from TPC4 QMAN special to TPC4 config definitions. Because this file is generated and this task is research-only, it should be treated as a signal for generator or reconciliation checks rather than edited here.

Max-offset and section values do not all match simple block sizes. Some are hardware-specific iteration spans, diagnostic-section distances, or special sentinel extents such as `0x8000`, `0xD400`, `0xA600`, `0x13180`, `0x15A00`, `0x1E000`, and `0x23180`. Callers must use the intended macro for range validation versus repeated-section stepping instead of assuming the fields are interchangeable.

Security and user-mapping risk is concentrated in AXUSER, secured/non-secured QMAN, special, and block-mmap-related ranges. If those bases are wrong, the driver can configure the wrong transaction attributes or expose registers that should remain inaccessible.

Router and RAZWI diagnostics are topology-sensitive. Router master-interface, address-decoder, transaction-stat, and debug-address bases must match dcore/router numbering and HBW/LBW/E2E lane semantics; otherwise RAZWI and fabric-fault logs can implicate the wrong initiator or address path.

## Test Signals

Useful validation signals for this generated header are compile-time and hardware-integration oriented:

- A full driver build succeeds with no missing macro references from Gaudi2 implementation files.
- Generated macro audits confirm every complete block in the range has exactly one `mm..._BASE`, one `..._MAX_OFFSET`, and one `..._SECTION`, allowing for documented chunk-boundary partial triplets.
- Address monotonicity checks pass for repeated families: DCORE0 routers 3-7, DCORE0 SRAM banks 0-7, EDMA0/EDMA1, TPC0-TPC5, HMMU0-HMMU3, and DCORE1 routers 0-7.
- Driver probe on Gaudi2 hardware completes MMU, QMAN, TPC, MME, EDMA, decoder, sync-manager, and HMMU initialization without invalid-register or timeout errors.
- Queue tests, EDMA memory scrub, context setup, and device idle checks reach the expected block instances, especially DCORE0 EDMA and DCORE1 TPC/MME ranges covered here.
- Injected or firmware-reported QMAN, MMU, MME, TPC, decoder, router, SRAM, and RAZWI events produce cause logs from the expected dcore/block instance.
- User block mmap attempts accept exactly the intended Gaudi2 blocks and reject offsets beyond the relevant `MAX_OFFSET` or mapped section extent.
- Special-block traversal and global-error scans do not access unmapped holes or skip intended `SPECIAL` windows.
- Register-dump comparisons against hardware documentation or firmware-provided maps show the same base addresses from `0x4154700` through the visible `0x4382500` range.

### subset-b-000989: lines 13500-18084

# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/gaudi2_blocks_linux_driver.h lines 13500-18084

## Purpose

This chunk is a generated Gaudi2 ASIC block-address map for the HabanaLabs Linux driver. It contains only preprocessor constants: each hardware sub-block is represented by a base address macro, a maximum offset macro, and a section-size/stride macro. The driver includes this file through `gaudi2_regs.h`, so these constants become the common compile-time address vocabulary for Gaudi2 MMIO, queue-manager, SRAM, TPC, MME, router, HIF, HMMU, decoder, and DMA logic.

The selected range starts in the middle of the `DCORE1_SRAM0_DBG_CNT` definitions and ends in the middle of the `DCORE2_EDMA0_QM_QMAN_WR64_BASE_ADDR` table. Within those boundaries it covers the tail of DCORE1 SRAM0, all DCORE1 SRAM1-7, DCORE1 EDMA0/EDMA1, DCORE1 decoder/video-decoder bridge areas, a large DCORE2 compute/interconnect slice, all DCORE2 SRAM0-7, and the beginning of DCORE2 EDMA0 QM.

The file header marks this as auto-generated and says not to edit below the header. The research implication is that human changes should normally happen in the generator or source register database, not by hand-editing these literal addresses.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or runtime APIs in this chunk. The public interface is the macro namespace it contributes to every C file that includes `gaudi2_regs.h`.

The macro pattern is consistent:

- `mm<block>_BASE`: absolute Gaudi2 MMIO offset for the start of a block or sub-region, written as an unsigned long long literal such as `0x43CA000ull`.
- `<block>_MAX_OFFSET`: maximum valid offset span used by range-oriented code, register dump code, protection logic, or generated validation tables.
- `<block>_SECTION`: generated section size or spacing value for the block family. In repeated blocks this is often the stride to the next logical section, while for "special" windows it marks the special aperture size.

Important block families in this range include:

- `DCORE1_SRAM[0-7]`: bank, router, debug-counter, high-bandwidth and low-bandwidth request/response/stat-counter regions. SRAM1-7 are complete in this chunk; SRAM0 starts mid debug-counter group.
- `DCORE1_EDMA[0-1]`: queue-manager DCCM, ARC auxiliary, QM base, 16 WR64 base-address entries, AXUSER secured/non-secured windows, debug HBW/LBW windows, CGM, core, context, KDMA CGM, and master-interface regions.
- `DCORE1_DEC[0-1]` and `DCORE1_VDEC[0-1]`: decoder command/L2C/VSI blocks and video-decoder bridge/control/master-interface windows.
- `DCORE2_TPC[0-5]`: TPC queue-manager and configuration windows, including DCCM, ARC auxiliary, QM base, WR64 base-address slots, AXUSER, debug windows, CGM, kernel tensor descriptors, kernel and QM tensor descriptor arrays, CFG QM, EML CFG, master-interface blocks, and special regions.
- `DCORE2_HMMU[0-3]`: MMU, STLB, scrambler, and master-interface windows.
- `DCORE2_MME`: MME QM and ARC windows, MME control low/high and middle controls, tensor/AGU descriptor regions, SBTE0-4, accumulator, EU, writeback blocks, and master interfaces.
- `DCORE2_SYNC_MNGR`, `DCORE2_HIF[0-3]`, and `DCORE2_RTR[0-7]`: synchronization-manager objects/global/master-interface ranges, host-interface windows, router control/stat/add-dec/debug regions.
- `DCORE2_SRAM[0-7]`: complete bank/router/debug-counter maps for DCORE2 SRAM.
- `DCORE2_EDMA0_QM`: starts at the end of the chunk with DCCM, ARC auxiliary, QM base, and WR64 base-address entries 0 through 11. Entries 12-15 and the rest of EDMA0 continue after line 18084.

## Control Flow

This header has no executable control flow. Its effect is entirely at preprocessing and compilation time:

1. `gaudi2_regs.h` includes `gaudi2_blocks_linux_driver.h`.
2. Gaudi2 driver C files include `gaudi2_regs.h`.
3. The compiler substitutes the generated constants into static tables, register calculations, MMIO reads/writes, firmware CPU address tables, queue-manager mappings, interrupt handling, reset flows, and debug/range logic.

Representative integration in `gaudi2.c` shows how these macros are consumed. Queue ID tables map DCORE queue identifiers to QM base macros such as `mmDCORE1_TPC*_QM_BASE`, `mmDCORE2_TPC*_QM_BASE`, `mmDCORE2_EDMA0_QM_BASE`, and `mmDCORE2_MME_QM_BASE`. ARC CPU tables map firmware CPU IDs to QM ARC auxiliary and DCCM base macros such as `mmDCORE1_EDMA0_QM_ARC_AUX_BASE`, `mmDCORE2_EDMA0_QM_ARC_AUX_BASE`, and `mmDCORE2_EDMA0_QM_DCCM_BASE`. Event handling also selects QM base constants for HDMA events, including DCORE1 and DCORE2 EDMA queue managers.

Because the chunk is a linear list of constants, apparent "flow" is the hardware address-space ordering: DCORE1 SRAM gives way to DCORE1 EDMA and VDEC, then DCORE2 TPC/HMMU/MME/sync/HIF/router/SRAM, then the beginning of DCORE2 EDMA0.

## State And Persistence Behavior

The chunk stores no runtime software state and performs no persistence. It defines immutable compile-time literals. The persistent behavior is indirect: any compiled driver binary that used these constants will issue MMIO accesses to the encoded hardware offsets until rebuilt with different generated headers.

The macros describe hardware address state rather than owning it. Consumers may read or write SRAM bank registers, router counters, QM state, ARC DCCM/AUX windows, tensor configuration windows, MME controls, or synchronization-manager objects using these addresses. Incorrect literals can therefore persist as incorrect hardware behavior across every driver execution built from the bad header.

Boundary state matters for reconciliation. The first line in this chunk is not the first macro for `DCORE1_SRAM0`; it starts after earlier `DCORE1_SRAM0_BANK`, `RTR`, and initial debug-counter entries. The last line is not the end of `DCORE2_EDMA0_QM`; it stops after `DCORE2_EDMA0_QM_QMAN_WR64_BASE_ADDR11_SECTION`.

## Dependencies

This chunk depends on the generated Gaudi2 register-map source used by HabanaLabs tooling. Local code should treat the file as generated output.

Compile-time dependencies and consumers include:

- `include/gaudi2/asic_reg/gaudi2_regs.h`, which directly includes this header before the per-block register headers.
- Gaudi2 driver implementation files such as `gaudi2.c`, which use the block base macros in queue-base tables, ARC DCCM/AUX address tables, and event-specific queue-manager selection.
- Per-block generated register headers included by `gaudi2_regs.h`; those headers provide offsets inside many of the blocks whose base addresses are defined here.
- Kernel/HabanaLabs MMIO helpers such as register read/write macros, which combine these constants with offsets and device BAR mappings.
- Firmware and hardware contracts for Gaudi2 DCORE numbering, SRAM layout, QM/ARC windows, DCCM/AUX sizes, TPC/MME topology, and router/interconnect block placement.

The file uses the `ull` suffix for base literals because several generated addresses are 64-bit-style constants even when stored into narrower driver tables in specific consumers. Refactors need to preserve type expectations at use sites.

## Integration Points

This header is a low-level integration layer between the generated ASIC map and the Linux driver.

Queue management integration is especially visible. TPC, MME, and EDMA QM base constants from this chunk are used to build queue ID to QM base mappings. WR64 base-address sub-region constants identify the 16 address slots within a QM register area. ARC auxiliary and DCCM constants support driver-to-firmware access to embedded ARC processors attached to TPC, MME, and EDMA queue managers.

Compute integration is represented by the DCORE2 TPC0-5 and MME maps. TPC configuration blocks expose kernel tensor, synchronization object, kernel descriptor, and QM tensor windows. MME blocks expose QM/ARC state, control-low/control-high descriptor regions, middle controls, SBTEs, accumulator/EU windows, and writeback interfaces.

Memory and interconnect integration is represented by SRAM, HMMU, router, sync-manager, and HIF regions. SRAM bank/router/debug counters and HBW/LBW request/response stat counters support memory-path diagnostics. HMMU blocks provide MMU/STLB/scrambler windows. Router blocks expose control, H3, master-interface, address-decoder, transaction-stat, MFIFO, E2E, and debug-address windows. Sync-manager and HIF constants integrate DCORE2 synchronization and host-interface MMIO surfaces.

Security and diagnostics code can also consume the `SPECIAL`, `AXUSER`, `MSTR_IF`, `DBG_HBW`, `DBG_LBW`, and `E2E_CRDT` sub-block definitions when building protected access rules, register dumps, or error isolation coverage.

## Risks And Edge Cases

- A wrong generated base address can redirect MMIO to another hardware block. In this driver layer that can cause queue corruption, firmware access failures, false debug data, or destructive writes to unrelated Gaudi2 registers.
- The chunk is mechanically repetitive. Copy/generator drift across DCORE instances is hard to notice by review alone; for example DCORE1 and DCORE2 SRAM layouts are mostly isomorphic but intentionally offset by DCORE base address.
- The source range begins and ends mid-family. A chunk-level consumer must not infer that `DCORE1_SRAM0` or `DCORE2_EDMA0_QM` are complete from this document alone.
- Some generated section values are not identical to max offsets and are not always simple block sizes. Consumers that reinterpret `_SECTION` as a byte length without matching the generator contract can overrun or under-cover register windows.
- There are duplicate-looking macro lines in the broader generated file, including repeated special-section names around TPC CFG/QM boundaries. Because this is generated hardware data, apparent duplication should be checked against the generator and hardware database before "cleanup".
- Constants are untyped macros, so the compiler provides little domain validation. Passing a DCORE1 base where a DCORE2 table entry is expected can compile cleanly.
- Static driver arrays may store selected base macros in `u32` tables. Current addresses in this range fit in 32 bits, but the source literals are `ull`; future map growth or tooling changes should be checked for truncation risk.
- This header is included broadly through `gaudi2_regs.h`; modifying any macro can have a wide rebuild and runtime blast radius even if only one local use is obvious.

## Test Signals

Useful validation for this chunk is mostly static generation validation plus hardware bring-up:

- Build the Gaudi2 driver with `gaudi2_regs.h` included and ensure there are no duplicate macro, overflow, or initializer warnings from the changed/generated block map.
- Run a generator consistency check that every block in this range has matching `_BASE`, `_MAX_OFFSET`, and `_SECTION` definitions, except where the chunk intentionally starts or ends mid-block.
- Compare repeated DCORE1/DCORE2 SRAM and DCORE2 TPC layouts against the authoritative hardware database for expected strides and address deltas.
- Exercise Gaudi2 initialization paths that populate queue-base tables, ARC DCCM/AUX tables, and HDMA event handling for DCORE1 EDMA, DCORE2 EDMA0, DCORE2 TPC0-5, and DCORE2 MME.
- On hardware or simulation, read representative registers from each covered family: SRAM debug counters, EDMA QM/ARC/DCCM, TPC QM and CFG, HMMU, MME control/SBTE/writeback, sync-manager, HIF, router, and DCORE2 SRAM.
- Validate register dump, error reporting, and security/protection tooling against representative `SPECIAL`, `AXUSER`, `DBG_*`, `MSTR_IF`, and `E2E_CRDT` sub-blocks.
- Confirm that queue submission, firmware communication, DMA event handling, tensor processing, MME execution, synchronization-manager operation, and memory/router diagnostics still address the expected DCORE2 blocks after any regeneration.

### subset-b-000990: lines 18085-22762

# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/gaudi2_blocks_linux_driver.h lines 18085-22762

## Purpose

This chunk is a middle section of the auto-generated Gaudi2 ASIC block-map header used by the HabanaLabs accelerator driver. It does not implement Ceph filesystem behavior despite the repository path; it provides compile-time MMIO block metadata for Gaudi2 hardware. The file is included by `gaudi2_regs.h`, which is the aggregate register include for the Gaudi2 driver.

The covered range contains 4,678 `#define` entries: 1,560 block base macros, 1,559 `_MAX_OFFSET` macros, and 1,559 `_SECTION` macros. Most entries are normal macro triplets:

- `mm..._BASE`: 64-bit base address for a hardware block.
- `..._MAX_OFFSET`: maximum register offset covered by the generated per-block register file.
- `..._SECTION`: generated block spacing or reserved section size.

The chunk starts mid-family at `mmDCORE2_EDMA0_QM_QMAN_WR64_BASE_ADDR12_BASE` and ends at `mmPSOC_ARC0_MSTR_IF_E2E_CRDT_BASE`, whose matching max-offset and section entries are outside this chunk. Per-file research must reconcile adjacent chunks before claiming complete block coverage.

## Important APIs, Types, And Definitions

There are no C functions, structs, enums, or executable APIs in this chunk. The API surface is the exported preprocessor namespace. Major families covered here are:

- Tail of DCORE2 EDMA/video aperture: remaining `DCORE2_EDMA0` queue-manager/core/master-interface blocks, full `DCORE2_EDMA1`, decoder blocks `DCORE2_DEC0/1`, and video decoder bridge/control/master-interface blocks `DCORE2_VDEC0/1`.
- DCORE3 compute blocks: six TPCs (`DCORE3_TPC0` through `DCORE3_TPC5`), four HMMUs, one MME complex, sync-manager global/object/master-interface blocks, four HIF blocks, eight routers, eight SRAM banks, two EDMAs, two decoder command/VSI/L2C groups, and two VDEC groups.
- Top-level interrupt and host/control aperture: `mmGIC_BASE`, PCIe wrapper/DBI/core/aux/PHY/MSI/ELBI/MSTR/LBW/MSIX blocks, and the start of PSOC peripheral/config blocks.
- PSOC and management peripherals through the chunk boundary: I2C, SPI, QSPI, UARTs, timer, watchdog, timestamp, efuse, global configuration, GPIOs, boot-loader, trace, DFT efuse, RPM, PID, ARC0 CFG, and the first ARC0 master-interface entries.

Representative base macros from this range include `mmDCORE3_TPC0_QM_BASE`, `mmDCORE3_MME_QM_BASE`, `mmDCORE3_HMMU0_MMU_BASE`, `mmDCORE3_SYNC_MNGR_OBJS_BASE`, `mmDCORE3_RTR0_CTRL_BASE`, `mmDCORE3_EDMA0_QM_BASE`, `mmGIC_BASE`, `mmPCIE_WRAP_BASE`, `mmPCIE_MSIX_BASE`, `mmPSOC_TIMESTAMP_BASE`, `mmPSOC_GLOBAL_CONF_BASE`, and `mmPSOC_ARC0_CFG_BASE`.

## Control Flow

This header has no runtime control flow. Its control path is compile-time inclusion and later MMIO use:

1. `gaudi2_regs.h` includes `gaudi2_blocks_linux_driver.h` before per-register headers.
2. Gaudi2 driver code includes `gaudi2_regs.h` through private device headers.
3. Runtime paths combine these block bases with per-register offsets, derived strides, or stream indices.
4. MMIO helpers and security helpers use the computed addresses to read, write, protect, or expose hardware blocks.

The order of definitions tracks the generated hardware address map. In this chunk, addresses move from DCORE2 around `0x45CA960`, through DCORE3 from `0x4600000` to `0x47F5E80`, then GIC at `0x4800000`, PCIe around `0x4C01000` to `0x4C17000`, and PSOC from `0x4C40000` through the partial ARC0 master-interface block at `0x4C5A800`.

## State And Persistence Behavior

The header owns no software state and persists no data. Its constants encode a hardware ABI for one generated Gaudi2 register map. State changes happen only in consumers that use these constants for MMIO.

For example, queue-manager paths map queue IDs and error events to bases such as `mmDCORE3_TPC0_QM_BASE`, `mmDCORE3_MME_QM_BASE`, and `mmDCORE3_EDMA0_QM_BASE`; HMMU setup and fault handling derive HMMU addresses from `mmDCORE3_HMMU0_MMU_BASE`; security setup uses PSOC and PCIe bases to program protection ranges; and LBW range initialization programs router ranges from generated router, PSOC, PCIe, and TPC debug apertures.

If a base address is wrong, software state may still look internally consistent while MMIO lands on the wrong hardware block. That makes this file a generated contract rather than ordinary configuration.

## Dependencies

- `gaudi2_regs.h` directly includes this header and defines derived strides from it, including `DCORE_OFFSET`, `DCORE_EDMA_OFFSET`, `DCORE_TPC_OFFSET`, `DCORE_DEC_OFFSET`, `DCORE_HMMU_OFFSET`, `DCORE_MME_SBTE_OFFSET`, `DCORE_MME_WB_OFFSET`, `DCORE_RTR_OFFSET`, `DCORE_VDEC_OFFSET`, and `PCIE_VDEC_OFFSET`.
- Per-block generated register headers depend on these bases conceptually; runtime code combines a block base from this file with offsets from files such as `dcore*_tpc*_qm_regs.h`, `dcore*_hmmu*_mmu_regs.h`, `pcie_*_regs.h`, and `psoc_*_regs.h`.
- Gaudi2 topology constants in `include/gaudi2/gaudi2.h`, such as `NUM_OF_DCORES`, `NUM_OF_TPC_PER_DCORE`, `NUM_OF_HMMU_PER_DCORE`, and `NUM_OF_RTR_PER_DCORE`, constrain loops that use these generated offsets.
- `gaudi2_security.c` uses these bases to build protection-bit block arrays and LBW range registers.
- `gaudi2.c` uses queue-manager bases from this range in queue ID tables and event/error dispatch.

The source is explicitly auto-generated. Changes should come from the ASIC register database/generator rather than hand edits in this header.

## Integration Points

Important integration points observed in the Gaudi2 driver include:

- Queue-manager lookup: DCORE3 TPC, EDMA, and MME queue IDs map to `mmDCORE3_*_QM_BASE` values from this chunk; error handling computes TPC queue-manager bases with `mmDCORE3_TPC0_QM_BASE + index * DCORE_TPC_OFFSET`.
- Engine event handling: TPC, MME, and HDMA events select the appropriate generated base before queue-manager diagnostics and resets.
- HMMU handling: HMMU instance selection uses `mmDCORE3_HMMU0_MMU_BASE` together with `DCORE_HMMU_OFFSET` and dcore offsets.
- Protection/security setup: arrays such as Gaudi2 PSOC and PCIe protection blocks include `mmPSOC_EFUSE_BASE`, `mmPSOC_BTL_BASE`, `mmPSOC_GLOBAL_CONF_BASE`, `mmPSOC_ARC0_CFG_BASE`, and `mmPCIE_WRAP_BASE`.
- LBW router range setup: security initialization writes short and long ranges using bases from this chunk, including PSOC peripheral ranges, PCIe DBI doorbell ranges, DCORE router bases, and TPC debug coverage ending at a DCORE3 TPC debug block.
- Interrupt/device integration: `mmGIC_BASE` and the hard-coded `mmGIC_DISTRIBUTOR__5_GICD_SETSPI_NSR` alias in `gaudi2_regs.h` place interrupt-controller access in the same address neighborhood as this chunk.

## Risks And Edge Cases

- The chunk is not self-contained. It starts in the middle of DCORE2 EDMA0 QMAN write64 base-address definitions and ends after a PSOC ARC0 base without its `_MAX_OFFSET` and `_SECTION` companions.
- Repeated-engine arithmetic is high risk. `DCORE_OFFSET`, `DCORE_TPC_OFFSET`, `DCORE_HMMU_OFFSET`, `DCORE_RTR_OFFSET`, and similar macros depend on exact differences between sibling bases. A single generated value drift can redirect loops over dcores, TPCs, HMMUs, routers, decoders, or VDECs.
- `_MAX_OFFSET` and `_SECTION` are generated metadata, not always simple bounds. Some generated max offsets exceed or differ from section sizes, so validation should compare against the ASIC generator rather than assume a universal invariant like `MAX_OFFSET <= SECTION`.
- Bases are `ull` literals. Storing them in too-small intermediates, especially before subtracting low-level config bases or programming protection/range registers, can truncate addresses.
- Security and LBW range programming depend on exact endpoints. Incorrect PSOC, PCIe, router, or TPC debug bases could leave sensitive blocks accessible or block required firmware/driver access.
- Manual edits are especially dangerous because consumers often reference only the first base of a repeated family and derive all siblings arithmetically.

## Test Signals

Useful validation signals for this chunk are mostly build, static-generation, and hardware bring-up signals:

- Build all Gaudi2 driver translation units that include `gaudi2_regs.h`; missing or renamed macros should fail at compile time.
- Regenerate `gaudi2_blocks_linux_driver.h` from the authoritative ASIC register source and compare this chunk byte-for-byte, allowing only intentional generator updates.
- Static-check triplet structure within the requested range: 1,560 visible `mm..._BASE` macros, 1,559 `_MAX_OFFSET` macros, and 1,559 `_SECTION` macros, with expected exceptions at the chunk boundaries.
- Verify derived stride macros in `gaudi2_regs.h` against representative sibling bases for dcore, TPC, EDMA, HMMU, router, MME SBTE/WB, decoder, and VDEC families.
- Exercise queue-manager diagnostics and reset/error flows for DCORE3 TPCs, DCORE3 EDMA0/1, and DCORE3 MME; regressions often appear as wrong-engine diagnostics, failed resets, or hung queues.
- Exercise Gaudi2 security initialization and LBW range programming, including PSOC peripheral access, PCIe wrap/DBI/MSIX access, DCORE router ranges, HMMU protection, and TPC debug range coverage.
- On hardware or simulator, perform representative MMIO readback through GIC, PCIe, PSOC timestamp/global configuration, DCORE3 HMMU, DCORE3 router, DCORE3 SRAM, DCORE3 TPC, and DCORE3 EDMA blocks to catch address-map drift.

### subset-b-000991: lines 22763-27893

# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/gaudi2_blocks_linux_driver.h lines 22763-27893

## Scope

This chunk is a generated Gaudi2 Linux-driver register-block map. It contains preprocessor constants only: each hardware block is represented by a `mm..._BASE` address macro plus matching `..._MAX_OFFSET` and `..._SECTION` sizing macros. The chunk starts in the middle of the `PSOC_ARC0_MSTR_IF` group, at `PSOC_ARC0_MSTR_IF_E2E_CRDT_MAX_OFFSET`, and ends in the middle of the `NIC1_QPC0` group at `NIC1_QPC0_AXUSER_QPC_RESP_MAX_OFFSET`; adjacent chunks are needed for the missing base at the beginning and the final section/special blocks at the end.

## Purpose

The purpose of this range is to give the Habanalabs Gaudi2 driver compile-time addresses for MMIO windows in the SoC management, DMA, CPU, PMMU, crossbar, PCIe, HBM, rotation, scaling/router, ARC-farm, and NIC register spaces. These constants are consumed by lower-level register-access helpers elsewhere in the driver to calculate absolute device register addresses, validate register ranges, build debug dumps, and program block-specific security, AXUSER, clock, queue-manager, and master-interface registers.

There is no executable logic here. The behavioral contract is data accuracy: names, base addresses, maximum offsets, and section extents must match the hardware address map generated for Gaudi2.

## Important API Surface

The API exposed by this chunk is the macro naming convention:

- `mm<block>_BASE`: absolute Gaudi2 MMIO base address for a register block, expressed as an unsigned long long literal such as `0x4C5AA80ull`.
- `<block>_MAX_OFFSET`: largest documented offset for that block's register file or aperture.
- `<block>_SECTION`: section size or stride-like region extent used by register-table consumers and debug/validation code.

Major block families visible in this chunk include:

- PSOC and PSOC-adjacent management blocks: `PSOC_ARC0`, `PSOC_ARC1`, `PSOC_SECURITY`, `JT`, `SMI`, `I2C_S`, `PSOC_SVID[0-2]`, `PSOC_*_PLL`, `PSOC_RESET_CONF`, `PSOC_AVS[0-2]`, `PSOC_PWM[0-1]`, `SVID[0-2]_AC`, and `PSOC_MSTR_IF`.
- Queue-manager and DMA-style blocks for `PDMA0`, `PDMA1`, `ROT0`, `ROT1`, `ARC_FARM_KDMA`, and NIC queue managers. These include repeated `QMAN_WR64_BASE_ADDR0` through `QMAN_WR64_BASE_ADDR15`, AXUSER windows, debug HBW/LBW windows, CGM windows, ARC DCCM/AUX windows, core context windows, and master-interface windows.
- CPU and PMMU blocks: `CPU_CA53_CFG`, `CPU_IF`, `CPU_TIMESTAMP`, `CPU_MSTR_IF`, `PMMU_HBW_MMU`, `PMMU_HBW_STLB`, `PMMU_HBW_MSTR_IF`, `PMMU_PIF`, and PMMU PLL windows.
- Crossbar and DCORE clock/transport blocks: `XBAR_MID_*`, `XBAR_EDGE_*`, `DCORE[0-3]_XBAR_*_PLL`, `DCORE[0-3]_XFT`, `DCORE[0-3]_{HBM,TPC,PCI,NIC}_PLL`, `DCORE[0-3]_TS`, and `DCORE[0-3]_TSTDVS`.
- Router/scaler blocks: `SFT[0-3]_HBW_RTR_IF[0-1]`, `SFT[0-3]_LBW_RTR_IF`, their `RTR_CTRL`, `RTR_H3`, `MSTR_IF`, and `ADDR_DEC` sub-blocks.
- ARC farm blocks: `ARC_FARM_FARM`, `ARC_FARM_ARC[0-3]_AUX`, `DUP_ENG`, `ACP_ENG`, and `DCCM[0-1]`.
- PCIe decode/video-decode blocks: `PCIE_DEC[0-1]`, `PCIE_VDEC[0-1]`, `PCIE_VDEC*_BRDG_CTRL`, MSI-X/AXUSER sub-windows, and `PCIE_PMA_0/1`.
- HBM blocks: `HBM[0-5]_MC0`, `HBM[0-5]_MC1`, `HBM[0-5]_MC[0-1]BIST[0-8]`, and `HBM[0-5]_PHY`.
- NIC0 and NIC1 blocks: UMR doorbells and completion queues, QMs, QPC DBFIFO completion-index update addresses, AXUSER windows, timer/RX/TX engines, master interface, serdes/PHY, MAC, and port MAC blocks.

## Control Flow

There is no runtime control flow in this chunk. The only "flow" is structural ordering in the generated header:

1. Management/PSOC register windows are listed first, beginning with the continuation of `PSOC_ARC0_MSTR_IF` and then covering ARC1, security, service interfaces, SVID/AVS/PWM, PSOC PLLs, reset, and master interface.
2. Engine-local blocks follow, including PDMA0/PDMA1, CPU, PMMU, XBAR/DCORE PLLs, ROT0/ROT1, and SFT router/scaler windows.
3. Shared firmware/control blocks follow through the ARC farm.
4. PCIe decode and DCORE-side PLL groups transition the address map into the HBM and NIC ranges.
5. HBM0 through HBM5 are enumerated in repeated MC/BIST/PHY patterns.
6. NIC0 is mostly complete in this chunk, including UMR0/UMR1, QM0/QM1, QPC0/QPC1, RX/TX, MAC, PHY, and master-interface blocks.
7. NIC1 begins with UMR0, QM0, and most of QPC0, but continues into the next chunk after line 27893.

Because consumers compile these macros into register reads and writes, control decisions occur outside this header. This chunk's contribution is the static address data used by those decisions.

## State and Persistence Behavior

The macros represent persistent hardware address-map facts, not software state. They do not allocate storage, mutate memory, or persist driver state. Hardware state changes only when other driver code uses these addresses through MMIO accessors. The persistence concern is source-level persistence: if generated constants are stale or mismatched to the ASIC revision, driver code may read/write the wrong registers consistently across boots until the header is regenerated.

Several repeated groups imply stateful hardware apertures:

- Queue manager WR64 base address windows likely back command submission or DMA doorbell programming.
- QPC DBFIFO completion-index update address windows and UMR doorbell/completion-queue windows expose NIC queue state.
- PLL control/divider windows expose clock configuration state.
- AXUSER and secured/nonsecured windows encode transaction attributes and security/privilege behavior.
- Debug HBW/LBW windows expose diagnostic state for high-bandwidth and low-bandwidth paths.

The header itself does not enforce access ordering, locking, reset sequencing, or save/restore policy for any of those stateful hardware units.

## Dependencies and Integration Points

This file depends on the broader Habanalabs/Gaudi2 register naming scheme and generated ASIC register metadata. Integration happens at compile time through `#include` usage by Gaudi2 driver code that knows these macro names. The values are expected to line up with:

- Gaudi2 MMIO access helpers and register read/write macros.
- Debugfs, register dump, and error collection paths that iterate or address block sections.
- Reset and initialization flows that program PSOC, PLL, PMMU, DMA, PCIe, NIC, HBM, and DCORE/XBAR windows.
- Security and privilege programming paths using `AXUSER`, `SECURED`, `NONSECURED`, `SPECIAL`, and master-interface sub-blocks.
- Queue and networking paths that need NIC UMR, QPC, QM, RX/TX, MAC, PHY, and serdes addresses.

The repeated master-interface sub-block pattern is a key integration point. Many hardware units expose `RR_SHRD_HBW`, `RR_PRVT_HBW`, `RR_SHRD_LBW`, `RR_PRVT_LBW`, `E2E_CRDT`, `AXUSER`, `DBG_HBW`, `DBG_LBW`, `CORE_HBW`, `CORE_LBW`, and `SPECIAL` windows. Code that constructs block tables from naming patterns is sensitive to any spelling or ordering drift.

## Risks

- Address-map drift is the primary risk. A wrong `BASE`, `MAX_OFFSET`, or `SECTION` can turn a valid register access into a read/write against a different hardware unit.
- Chunk boundaries split logical groups. `PSOC_ARC0_MSTR_IF_E2E_CRDT_BASE` is just before this chunk, and the final `NIC1_QPC0_AXUSER_QPC_RESP_SECTION`, `NIC1_QPC0_AXUSER_QPC_REQ`, and `NIC1_QPC0_SPECIAL` entries are just after this chunk. Merge logic must not treat this chunk as a complete file-level view.
- Repeated generated patterns can hide single-entry anomalies. Examples visible here include shorter final section sizes such as `*_QMAN_WR64_BASE_ADDR15_SECTION 0x1880`, router/address-decoder LBW sizes such as `0xA800`, and varying `SPECIAL_SECTION` values like `0x1180`, `0x2180`, `0x3180`, `0x4180`, `0x5180`, and larger ranges. Consumers should not derive all sizes from a uniform template unless the hardware spec guarantees it.
- Security-sensitive windows are interleaved with normal windows. `AXUSER_SECURED`, `AXUSER_NONSECURED`, `DBFIFOSECUR`, `DBFIFOPRIVIL`, MSI-X AXUSER, and special windows must be kept distinct to avoid changing access attributes or privilege handling.
- Large NIC and HBM repeated tables increase copy/regeneration risk. Off-by-one queue indices, completion queue indices, or BIST instance numbers would be hard to catch by inspection.
- Since these are preprocessor definitions, the compiler will not validate that a macro is semantically paired with its intended block. Incorrect but syntactically valid constants compile cleanly.

## Test Signals

Useful validation signals for this chunk are data- and integration-focused:

- Build coverage for every driver translation unit that includes `gaudi2_blocks_linux_driver.h`; missing or duplicated macro names should fail at compile time when referenced.
- Register-map consistency checks comparing generated `BASE`, `MAX_OFFSET`, and `SECTION` triples against the authoritative Gaudi2 register database.
- Smoke tests for device initialization, reset, PLL setup, PMMU setup, DMA queue manager setup, NIC bring-up, and HBM training, because those flows exercise the largest groups in this range.
- Debug dump or register enumeration tests that verify block ranges do not overlap unexpectedly and do not exceed the intended device MMIO aperture.
- NIC-focused tests covering UMR doorbells, completion queue CI updates, DBFIFO update addresses, RXE/TXE/TXB/TXS, MAC, PHY, and serdes access paths.
- Boundary tests for generated chunk merge/reconciliation: ensure the final per-file research/doc merge includes the preceding `PSOC_ARC0_MSTR_IF_E2E_CRDT_BASE` line and following `NIC1_QPC0_AXUSER_QPC_RESP_SECTION` and `NIC1_QPC0_SPECIAL` lines from adjacent chunks.

## Chunk Inventory

- Lines 22763-23107: PSOC/management continuation and PSOC master-interface windows.
- Lines 23110-23359: `PDMA0` and `PDMA1` queue-manager/core/master-interface windows.
- Lines 23362-23500: CPU and PMMU windows.
- Lines 23503-23926: XBAR, DCORE XBAR PLL, and PCIe PMA entries.
- Lines 23935-24172: `ROT0` and `ROT1` queue-manager, descriptor, and master-interface windows.
- Lines 24175-24844: `SFT0` through `SFT3` HBW/LBW router, master-interface, and address-decoder windows.
- Lines 24847-25039: ARC farm, ARC auxiliary, duplicate engine, ACP engine, KDMA, and DCCM windows.
- Lines 25042-25179: PCIe decode and video-decode windows for instances 0 and 1.
- Lines 25180-25474: DCORE XFT, HBM/TPC/PCI/NIC PLL, timestamp, and test/DVS windows.
- Lines 25477-26212: HBM0 through HBM5 memory-controller, BIST, and PHY windows.
- Lines 26215-27469: NIC0 UMR, QM, QPC, timer, RX/TX, master-interface, PHY/serdes, port MAC, and MAC statistic/channel windows.
- Lines 27472-27893: NIC1 UMR0, QM0, and partial QPC0 windows.

### subset-b-000992: lines 27894-32825

# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/gaudi2_blocks_linux_driver.h lines 27894-32825

## Scope

This chunk is a middle slice of the auto-generated Gaudi2 Linux-driver block map header. It is not Ceph filesystem logic despite the repository source path; it belongs to the HabanaLabs accelerator driver register-definition layer.

The covered range contains 4,932 preprocessor definitions: 1,644 block base macros, 1,644 maximum-offset macros, and 1,644 section-size macros. It starts inside the `NIC1_QPC0` definition group at `NIC1_QPC0_AXUSER_QPC_RESP_SECTION`, then covers the rest of NIC1's Linux-driver-visible NIC blocks, all NIC2/NIC3/NIC4 block-map entries, and the beginning of NIC5 through `NIC5_QPC0_DBFIFO6_CI_UPD_ADDR_MAX_OFFSET`. The matching `NIC5_QPC0_DBFIFO6_CI_UPD_ADDR_SECTION` is outside this chunk.

## Purpose

The header provides coarse MMIO aperture metadata for Gaudi2 hardware blocks. Each complete block normally appears as a generated macro triplet:

- `mm..._BASE`: 64-bit base address of a hardware block or sub-block.
- `..._MAX_OFFSET`: maximum generated register offset associated with that block.
- `..._SECTION`: generated section size or spacing used by the block map.

This chunk is focused on NIC register apertures. The address range runs from the tail of `NIC1_QPC0` at approximately `0x549f...` through early `NIC5_QPC0` at `0x569f...`. It names queue manager, queue-pair context, user memory region, receive/transmit datapath, master-interface, PHY/SERDES, port MAC, and MAC statistics sub-blocks for NIC1 through NIC5. Driver code uses these bases directly for queue-manager routing and security range programming, and indirectly through `gaudi2_regs.h`, which includes this generated block map before the per-register headers.

## Important APIs, Types, And Definitions

This chunk defines no C functions, structs, enums, or executable APIs. Its public surface is the generated macro namespace exported by `gaudi2_regs.h`.

Important macro families in the covered range include:

- `NIC1_QPC0` tail: the chunk begins with the final `AXUSER_QPC_RESP` section macro, followed by complete `AXUSER_QPC_REQ` and `SPECIAL` triplets.
- `NIC1_UMR1_*`: 15 user-memory-region windows, numbered `0` through `14`, each with `UNSECURE_DOORBELL0`, `UNSECURE_DOORBELL1`, `COMPLETION_QUEUE_CI_0`, `COMPLETION_QUEUE_CI_1`, and `SPECIAL` sub-blocks.
- `NIC1_QM1` and `NIC5_QM0`: queue-manager DCCM/ARC auxiliary windows, the queue-manager base, sixteen `QMAN_WR64_BASE_ADDR*` windows, secured/non-secured AXUSER windows, high/low bandwidth debug windows, CGM, and `SPECIAL` regions.
- `NIC1_QPC1`, `NIC2_QPC0`, `NIC2_QPC1`, `NIC3_QPC0`, `NIC3_QPC1`, `NIC4_QPC0`, `NIC4_QPC1`, and early `NIC5_QPC0`: queue-pair context windows with dense `DBFIFO0` through `DBFIFO29` CI update address triplets, secure and privileged DBFIFO entries, AXUSER windows for congestion queues, RX WQE, TX WQE/LBW QMAN backpressure, DB FIFO, event queue/LBW interrupt, error FIFO, QPC response, QPC request, and a `SPECIAL` region.
- `NIC2_UMR0/UMR1`, `NIC3_UMR0/UMR1`, `NIC4_UMR0/UMR1`, and `NIC5_UMR0`: each UMR instance follows the same 15-window pattern as `NIC1_UMR1`.
- `NIC1`, `NIC2`, `NIC3`, and `NIC4` datapath blocks: timer (`TMR`), receive buffer (`RXB_CORE`), receive engines (`RXE0`, `RXE1`), receive AXUSER completion-queue windows `CQ0` through `CQ31`, transmit scheduler/engine/buffer blocks (`TXS0`, `TXS1`, `TXE0`, `TXE1`, `TXB`), master-interface arbitration/debug/core windows, and `TX_AXUSER`.
- `NIC1` through `NIC4` physical/MAC-side blocks: `SERDES0`, `SERDES1`, `PHY`, `PHY_SPECIAL`, `PRT*_MAC_AUX`, `PRT*_MAC_CORE`, `NIC*_MAC_RS_FEC`, MAC global stat control, RX/TX statistic windows, RS-FEC stats, and four channel groups containing `MAC_PCS`, `MAC_128`, and `MAC_AN`.

Representative base macros from this chunk include `mmNIC2_QM0_BASE`, `mmNIC2_QM1_BASE`, `mmNIC3_QM0_BASE`, `mmNIC3_QM1_BASE`, `mmNIC4_QM0_BASE`, `mmNIC4_QM1_BASE`, and `mmNIC5_QM0_BASE`. These queue-manager bases are consumed directly by Gaudi2 queue ID tables in `gaudi2.c`.

## Control Flow

There is no runtime control flow in this header. The effective flow is compile-time inclusion and runtime address consumption:

1. `include/gaudi2/asic_reg/gaudi2_regs.h` includes `gaudi2_blocks_linux_driver.h`.
2. Gaudi2 driver C files include the aggregated generated register namespace.
3. Runtime tables and setup code select a block base macro, such as `mmNIC4_QM1_BASE`, for a queue, event source, or security aperture.
4. MMIO helpers or lower-level security/configuration code combine the block base with per-register offsets, queue offsets, protection-bit offsets, or fixed block sizes.

The chunk's ordering follows the generated hardware address map rather than a hand-authored software control path. For NIC2 through NIC4 the pattern is complete and regular: `UMR0`, `QM0`, `QPC0`, `UMR1`, `QM1`, `QPC1`, timer, RX/TX datapath, master interface, physical layer, port MAC, and MAC channel/statistics regions. NIC1 and NIC5 are partial only because of the requested line boundaries.

## State And Persistence Behavior

The header stores no mutable software state and persists nothing by itself. The constants are compiled into the driver and become a hardware ABI for Gaudi2's Linux-driver-visible register map.

The named MMIO regions represent hardware state:

- UMR doorbell and completion-queue CI windows are part of the NIC queue and completion path. Writes or reads by the driver or device agents affect queue progress and completion visibility.
- QM/QMAN regions hold queue-manager control, debug, AXUSER, and WR64 base-address plumbing used to drive NIC work submission.
- QPC DBFIFO CI update and AXUSER windows affect queue-pair context, doorbell FIFO, event/error FIFO, congestion queue, and WQE routing behavior.
- RX/TX datapath, timer, master-interface, PHY/SERDES, and MAC regions expose live NIC datapath, link, statistics, and debug/control state.

Any state persistence belongs to the device: register contents remain until changed by driver writes, firmware/hardware activity, reset, or reinitialization. The header's role is to ensure callers address the intended hardware state.

## Dependencies

Direct dependencies and related files:

- `include/gaudi2/asic_reg/gaudi2_regs.h` includes this generated block map and makes the macros available to Gaudi2 driver code.
- Per-register generated headers included after `gaudi2_blocks_linux_driver.h` provide offsets inside many of the block bases defined here.
- Gaudi2 driver MMIO helpers consume these constants as register aperture addresses.
- `gaudi2.c` uses NIC queue-manager base macros from this generated namespace to map `GAUDI2_QUEUE_ID_NIC_*` entries to QMAN base addresses.
- `gaudi2_security.c` uses MAC and TX AXUSER base macros to define LBW protection ranges for NIC blocks.
- Common security code depends on the repeated NIC layout and notes the regular offset between adjacent NIC UMR windows.

The file is marked auto-generated with a "DO NOT EDIT BELOW" banner. Changes should come from the ASIC register database/generator rather than manual patching.

## Integration Points

The strongest integration point in this chunk is queue routing. `gaudi2.c` maps groups of four NIC queue IDs to queue-manager bases. For example, queue IDs for NIC2/NIC3/NIC4/NIC5 logical engines use `mmNIC1_QM0_BASE`, `mmNIC1_QM1_BASE`, `mmNIC2_QM0_BASE`, `mmNIC2_QM1_BASE`, `mmNIC3_QM0_BASE`, `mmNIC3_QM1_BASE`, `mmNIC4_QM0_BASE`, `mmNIC4_QM1_BASE`, and `mmNIC5_QM0_BASE` from this chunk. If one of these bases is wrong, command submission, event attribution, or queue-manager error handling can target the wrong NIC engine.

Security range setup is another direct integration point. `gaudi2_security.c` builds LBW register ranges beginning at `mmNIC*_TX_AXUSER_BASE` and ending at `mmNIC*_MAC_CH3_MAC_PCS_BASE + HL_BLOCK_SIZE` for NIC0 through NIC10. For NIC1 through NIC4, both endpoints are covered in this chunk; for NIC5 the lower TX/MAC-side endpoint appears later in the file, while this chunk covers the earlier queue-side windows.

The QPC and UMR definitions integrate with NIC doorbell, completion, and queue-pair handling. The repeated `UNSECURE_DOORBELL*`, `COMPLETION_QUEUE_CI_*`, and `DBFIFO*_CI_UPD_ADDR` windows define the addressable apertures used by NIC hardware and low-level driver paths to signal producer/consumer index and doorbell movement.

The MAC and PHY definitions integrate with link management, diagnostics, and statistics collection. The chunk supplies base regions for PCS, 128-bit MAC, autonegotiation, RS-FEC, global RX/TX statistics, per-port MAC aux/core registers, SERDES, and PHY special regions.

## Risks And Edge Cases

The chunk starts and ends mid-definition group. Line 27894 is only `NIC1_QPC0_AXUSER_QPC_RESP_SECTION`; the matching base and max-offset lines are in the preceding chunk. Lines 32824-32825 define the base and max offset for `NIC5_QPC0_DBFIFO6_CI_UPD_ADDR`, but the section macro is in the following chunk. Chunk-level analysis must not treat either boundary as a complete block.

Generated triplets are hardware contracts. A bad `_BASE`, `_MAX_OFFSET`, or `_SECTION` can silently redirect MMIO to a neighboring NIC sub-block, corrupt queue state, break completion signaling, misreport MAC statistics, or leave security apertures underprotected.

The NIC families are repetitive but not interchangeable. NIC2 through NIC4 are complete in this chunk and share the same shape, while NIC1 lacks its earlier `UMR0/QM0/QPC0` prefix here and NIC5 lacks its later `QPC0/QM1/QPC1/datapath/MAC` tail here. Consumers should use the full generated header, not a chunk-local assumption, when deriving all-NIC coverage.

Some sub-blocks have `MAX_OFFSET` values larger than nearby `SECTION` values or vice versa. This appears to be generated hardware metadata, not a simple validation invariant. Static checks should verify exact generated output against the ASIC source rather than imposing a universal relationship between max offset and section size.

Address constants use `ull` and may exceed 32-bit assumptions in other parts of the file. Code that stores these base addresses in too-small intermediates, or subtracts/adds offsets with the wrong type, can truncate the register address.

Queue-manager base arrays create high blast radius for copy/generation drift. A single wrong `mmNIC*_QM*_BASE` macro can make multiple logical queue IDs share or target the wrong QMAN aperture.

Security code depends on exact range endpoints. Incorrect MAC channel or TX AXUSER bases can exclude sensitive control registers from protection or over-protect unrelated registers needed by firmware or diagnostics.

## Test Signals

Useful validation signals for this chunk are mostly build-time, generator, and hardware bring-up oriented:

- Compile Gaudi2 driver code that includes `include/gaudi2/asic_reg/gaudi2_regs.h`; missing or renamed macros from this chunk should fail at compile time.
- Regenerate the block map from the authoritative ASIC register database and compare this header byte-for-byte, especially the NIC1 through NIC5 ranges covered here.
- Static-check complete triplets inside the chunk: every visible `mm..._BASE` should have matching `_MAX_OFFSET` and `_SECTION` companions, except for the explicit chunk-boundary cases.
- Validate queue-manager tables in `gaudi2.c` by checking that NIC queue IDs map to the expected `mmNIC*_QM[01]_BASE` macros for NIC1 through NIC5.
- Run Gaudi2 NIC queue bring-up or simulator tests that submit through queue IDs backed by `mmNIC2_QM0_BASE`, `mmNIC2_QM1_BASE`, `mmNIC3_QM0_BASE`, `mmNIC3_QM1_BASE`, `mmNIC4_QM0_BASE`, `mmNIC4_QM1_BASE`, and `mmNIC5_QM0_BASE`.
- Exercise completion and doorbell paths for UMR/QPC windows, watching for stalled queues, stale completion indices, missed DBFIFO CI updates, or interrupts associated with the wrong NIC.
- Validate security initialization by reading back or tracing LBW protection entries for NIC1 through NIC4 TX/MAC ranges and for the queue-side regions that overlap this chunk.
- Exercise link/statistics diagnostics for NIC1 through NIC4 MAC/PHY regions, including PCS, autonegotiation, RS-FEC, and global RX/TX statistic windows.
- Use static analysis or targeted assertions to ensure these `ull` base constants are not truncated when passed through MMIO, protection-bit, or queue-base calculations.

Regression indicators include queue submissions hanging only on one NIC index, event reports naming the wrong NIC QMAN, completion queues not advancing, MAC statistics reads returning impossible data, link-management failures isolated to one repeated NIC, or security range programming touching unexpected LBW addresses.

### subset-b-000993: lines 32826-37748

# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/gaudi2_blocks_linux_driver.h lines 32826-37748

## Purpose

This chunk is a generated Gaudi2 Linux-driver block-map slice for the NIC configuration/MMIO aperture. It contains no executable code; it exports symbolic block windows used by the HabanaLabs Gaudi2 driver to locate NIC queue-manager, user-mapped doorbell/completion, packet-processing, MAC/PHY, SerDes, and port blocks.

The covered range begins in the middle of the `NIC5_QPC0` DB FIFO completion-index update address table and ends in the middle of the `NIC9_UMR0_14` user-mapped region. Within this range there are 4,923 `#define` entries: 1,641 `mm..._BASE` macros, 1,641 `..._MAX_OFFSET` macros, and 1,641 `..._SECTION` macros. The first complete base macro in the chunk is `mmNIC5_QPC0_DBFIFO7_CI_UPD_ADDR_BASE` at `0x569F758ull`; the last complete base macro is `mmNIC9_UMR0_14_COMPLETION_QUEUE_CI_1_BASE` at `0x588E180ull`. The line range also includes the beginning of `mmNIC9_UMR0_14_SPECIAL_BASE` and `mmNIC9_QM_DCCM0_BASE` just after the requested end, but those entries are outside this chunk's final complete triplet set.

## Important APIs, Types, And Definitions

This chunk does not define C functions, structs, enums, or runtime APIs. Its interface is the generated preprocessor namespace included through `include/gaudi2/asic_reg/gaudi2_regs.h`.

Each hardware window is represented by a triplet:

- `mm<block>_BASE`: 64-bit base address in the Gaudi2 register address map.
- `<block>_MAX_OFFSET`: maximum register offset associated with that generated block.
- `<block>_SECTION`: generated section size or stride reservation for the block.

Major block families covered here are:

- `NIC5_QPC0` tail and `NIC5_QPC1`: QPC DB FIFO completion-index update address entries, including numbered DB FIFO channels, secure and privileged FIFO update entries, AXUSER subwindows for congestion queues, RX/TX WQEs, DB FIFO, event queues, error FIFO, QPC responses/requests, and `SPECIAL` windows.
- `NIC5_UMR1`, `NIC6_UMR0/UMR1`, `NIC7_UMR0/UMR1`, `NIC8_UMR0/UMR1`, and the start of `NIC9_UMR0`: fifteen UMR blocks per UMR half where complete, each with `UNSECURE_DOORBELL0`, `UNSECURE_DOORBELL1`, `COMPLETION_QUEUE_CI_0`, `COMPLETION_QUEUE_CI_1`, and `SPECIAL` windows. The UMR blocks use a visible `0x1000` stride between block IDs.
- `NIC5`, `NIC6`, `NIC7`, and `NIC8` queue-manager regions: `QM_DCCM0/1`, `QM_ARC_AUX0/1`, `QM0`, `QM1`, per-QM `QMAN_WR64_BASE_ADDR0..15`, AXUSER secured/non-secured windows, debug HBW/LBW windows, CGM, and `SPECIAL` windows.
- `NIC5`, `NIC6`, `NIC7`, and `NIC8` datapath blocks: `TMR`, `RXB_CORE`, `RXE0`, `RXE1`, `RXE0_AXUSER`, `RXE1_AXUSER`, `TXS0/1`, `TXE0/1`, `TXB`, `MSTR_IF`, `TX_AXUSER`, `SERDES0/1`, and `PHY`.
- `PRT5` through `PRT8` port/MAC blocks: `MAC_AUX`, `MAC_CORE`, and their `SPECIAL` windows.
- `NIC5` through `NIC8` MAC blocks: `MAC_RS_FEC`, global statistic control/RX/TX/RSFEC stats, and per-channel `MAC_PCS`, `MAC_128`, and `MAC_AN` windows for channels 0-3.

The complete repeated NIC6-NIC8 portions are structurally symmetric. NIC5 is partial at the start because earlier `NIC5_QPC0`, `NIC5_UMR0`, `NIC5_QM0`, and related entries are in preceding chunks. NIC9 is partial at the end because this chunk stops during `NIC9_UMR0`; its queue-manager, datapath, MAC, and port entries continue later.

## Control Flow

There is no runtime control flow in this header chunk. Its compile-time flow is:

1. `gaudi2_regs.h` includes `gaudi2_blocks_linux_driver.h`.
2. Gaudi2 C files include the aggregated register definitions through private ASIC headers.
3. Runtime code uses the generated base macros directly, or uses them as arithmetic anchors for repeated blocks.
4. MMIO helpers, user-mapping setup, and security setup operate on the computed addresses.

The surrounding driver treats many of these blocks as regular arrays rather than individually naming every generated macro. For example, UMR user mappings are derived from `mmNIC0_UMR0_0_UNSECURE_DOORBELL0_BASE` plus NIC, QM, and UMR strides, while the explicit per-NIC macros in this chunk document the generated map that those stride calculations must match.

## State And Persistence Behavior

The header owns no software state and persists nothing. Its constants become part of the compiled driver's hardware contract for a specific Gaudi2 register map.

The named hardware windows do hold device state when accessed by consuming code:

- UMR doorbell and completion-queue consumer-index windows expose user-facing doorbell/CQ state used for NIC submission/completion paths.
- QPC DB FIFO CI update address windows point the NIC queue-pair controller at completion-index update targets for DB FIFO channels.
- Queue-manager `QMAN_WR64_BASE_ADDR*`, AXUSER, debug, and CGM windows configure NIC QMs and affect command submission, security attributes, and diagnostics.
- RX/TX datapath, MAC statistics, FEC, PCS, autonegotiation, PHY, and SerDes windows expose live NIC link, packet, and error state.

That hardware state persists until changed by driver initialization, firmware, user doorbell writes through mapped regions, link-management flows, or reset. The header's role is only to name the correct addresses.

## Dependencies

- `include/gaudi2/asic_reg/gaudi2_regs.h` is the integration header that includes this block-map header.
- Per-register generated headers supply offsets inside many of these block windows. This file supplies coarse block bases and section sizes; it does not define individual register fields.
- `gaudi2.c` consumes NIC QM, ARC AUX, and DCCM bases in static maps such as queue-ID base tables and ARC CPU base tables. The visible consumers include `mmNIC5_QM0_BASE`, `mmNIC5_QM1_BASE`, `mmNIC6_QM0_BASE`, `mmNIC7_QM1_BASE`, `mmNIC8_QM0_BASE`, and related ARC/DCCM bases.
- `gaudi2_user_mapped_blocks_init()` derives user-visible NIC UMR mappings from the NIC UMR address pattern and publishes each block with `HL_BLOCK_SIZE`.
- `gaudi2_security.c` uses NIC address bounds such as `mmNIC5_TX_AXUSER_BASE` through `mmNIC5_MAC_CH3_MAC_PCS_BASE + HL_BLOCK_SIZE` to program LBW range registers, and uses UMR/QPC ranges elsewhere to decide which NIC registers can be unsecured.
- Driver MMIO helpers such as `WREG32()` and `RREG32()` ultimately use these constants after base/offset arithmetic.

## Integration Points

The highest-value integration points are address-map consumers that assume regularity across NIC instances:

- Queue ID mapping: Gaudi2 queue IDs for NIC engines map four queues at a time to `NICx_QM0_BASE` or `NICx_QM1_BASE`. The complete NIC6-NIC8 portions in this chunk provide the bases for queue IDs 12-17, and NIC5 entries cover queue ID 11 for `QM1` while `QM0` appears in an earlier chunk.
- ARC management: NIC queue-manager ARC AUX and DCCM bases are indexed by `CPU_ID_NIC_QMAN_ARC*`. The chunk includes NIC5 `QM_ARC_AUX1`/`QM_DCCM1`, complete NIC6-NIC8 `QM_ARC_AUX0/1` and `QM_DCCM0/1`, and prepares the next NIC9 DCCM range immediately after the chunk.
- User mapping: UMR windows are exposed to userspace as fixed-size blocks. The generated `UNSECURE_DOORBELL*` and `COMPLETION_QUEUE_CI_*` windows are the address-map evidence behind that exported ABI.
- Security: range-register setup secures or unsecures large NIC configuration spans using the first TX AXUSER block and a MAC-channel endpoint. Per-register security allowlists also rely on UMR and QPC windows having exact bases and strides.
- NIC link and telemetry handling: MAC global statistic, RS-FEC, channel PCS/MAC/autonegotiation, PHY, and SerDes windows are the block anchors for link status, error counters, and bring-up diagnostics.

## Risks And Edge Cases

- The chunk boundaries are partial. It starts after `NIC5_QPC0_DBFIFO0..6` and ends before the full `NIC9_UMR0_14_SPECIAL` triplet and all later NIC9 blocks. Per-file reconciliation must combine adjacent chunks before making complete-file claims.
- Generated triplets must stay aligned. A missing `BASE`, `MAX_OFFSET`, or `SECTION` companion can break scripts or code that expects one triplet per block.
- Arithmetic consumers depend on regular strides. UMR blocks visibly advance by `0x1000`; DB FIFO CI update entries advance by `0x8`; RXE AXUSER CQ entries advance by `0x50`; QMAN WR64 base-address entries advance by `0x8`. A bad generated literal may compile cleanly but map the driver to the wrong NIC register window.
- Security exposure is sensitive. Incorrect UMR/QPC/MAC bounds can either expose privileged NIC configuration to userspace or block required user doorbell/completion accesses.
- Many names are near-duplicates across NIC instances and QM halves. Manual edits or review-by-eye are error-prone, especially around `UMR0` versus `UMR1`, `QM0` versus `QM1`, and `RXE0` versus `RXE1`.
- `MAX_OFFSET` and `SECTION` are not always the same size. Consumers should not infer one from the other without checking the generated values.

## Test Signals

- Build coverage for Gaudi2 driver files that include `gaudi2_regs.h` will catch renamed or missing macros referenced by `gaudi2.c`, `gaudi2_security.c`, and related NIC code.
- Static generated-map checks should verify this chunk has 1,641 complete triplets and that each `mm..._BASE` has matching `..._MAX_OFFSET` and `..._SECTION` macros in the same line range.
- Pattern checks should validate repeated strides: UMR block IDs at `0x1000`, DB FIFO CI update address entries at `0x8`, QMAN WR64 base entries at `0x8`, and RXE AXUSER CQ windows at `0x50`.
- Runtime smoke signals include successful NIC queue-manager initialization, user doorbell mapping, completion-queue CI updates, and NIC link bring-up for NIC5-NIC8 plus the early NIC9 UMR range.
- Security tests should exercise LBW range-register programming and UMR/QPC access policy, because failures here can surface as user MMIO faults, blocked doorbell writes, or unexpectedly accessible privileged registers.

### subset-b-000994: lines 37749-42833

# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/gaudi2_blocks_linux_driver.h lines 37749-42833

## Purpose

This chunk is part of the generated Gaudi2 Linux-driver ASIC block map. It defines preprocessor constants that describe memory-mapped register apertures for hardware blocks, not executable driver logic. Each represented aperture is encoded as a `BASE` address macro plus paired `MAX_OFFSET` and `SECTION` metadata macros.

The assigned range covers 5,085 lines. It starts inside the tail of the `NIC9_UMR0_14` entry, finishes the `NIC9` register-block map, then defines the complete `NIC10` and `NIC11` maps in this address region. It then transitions into data-core address ranges, covering all visible `DCORE0` and `DCORE1` debug/trace/performance-monitor blocks and the beginning of `DCORE2`, ending at `mmDCORE2_VDEC0_USER_CTI_BASE`.

The constants give other Gaudi2 driver code a single source of truth for register block base addresses and block spans. Consumers can compute register-window membership, debug dump windows, MMIO allow-list/protection ranges, and hardware block layout without embedding raw physical offsets in C code.

## Important APIs, Types, And Functions

This chunk defines macros only. It declares no C functions, structs, enums, or callable APIs.

The important macro families are:

- `mm..._BASE`: 64-bit unsigned MMIO base addresses, using the `ull` suffix. Examples include `mmNIC10_QM0_BASE`, `mmNIC11_MAC_CH3_MAC_AN_BASE`, `mmDCORE0_MME_CTRL_ROM_TABLE_BASE`, and `mmDCORE2_EDMA1_QM_ARC_RTT_BASE`.
- `..._MAX_OFFSET`: block-local maximum offset metadata. Most debug/trace blocks use `0x1000`; NIC subwindows use values such as `0x8000`, `0x5000`, `0x5800`, `0x31C0`, `0xA400`, and `0x4400`.
- `..._SECTION`: encoded section/span metadata for the Linux driver block table. Values vary by block, with common sections such as `0x1000`, `0x1800`, `0x4000`, `0x8000`, and larger aggregate spans such as `0x610800` for the final `NIC11_MAC_CH3_MAC_AN` section in this chunk.

The visible top-level prefixes and base-macro counts are:

- `NIC9`: 341 base macros in this range, starting at `mmNIC9_UMR0_14_SPECIAL_BASE` and ending at `mmNIC9_MAC_CH3_MAC_AN_BASE`.
- `NIC10`: 415 base macros, from `mmNIC10_UMR0_0_UNSECURE_DOORBELL0_BASE` through `mmNIC10_MAC_CH3_MAC_AN_BASE`.
- `NIC11`: 415 base macros, from `mmNIC11_UMR0_0_UNSECURE_DOORBELL0_BASE` through `mmNIC11_MAC_CH3_MAC_AN_BASE`.
- `PRT9`, `PRT10`, `PRT11`: four base macros each for MAC AUX/core and their special regions.
- `DCORE0`: 175 base macros, from `mmDCORE0_ROM_TABLE_L_BASE` through `mmDCORE0_VDEC1_BMON_2_BASE`.
- `DCORE1`: 175 base macros, from `mmDCORE1_ROM_TABLE_L_BASE` through `mmDCORE1_VDEC1_BMON_2_BASE`.
- `DCORE2`: 162 base macros visible in this chunk, from `mmDCORE2_ROM_TABLE_L_BASE` through `mmDCORE2_VDEC0_USER_CTI_BASE`.

## Covered Register Areas

The `NIC9`, `NIC10`, and `NIC11` regions are highly regular. For complete NIC instances, the chunk covers:

- UMR doorbell and completion-consumer-index regions: `UMR0_0` through `UMR0_14` and `UMR1_0` through `UMR1_14`, with unsecure doorbell windows, completion queue CI windows, and special windows.
- Queue manager blocks: `QM_DCCM0/1`, `QM_ARC_AUX0/1`, `QM0`, `QM1`, sixteen `QMAN_WR64_BASE_ADDR*` entries per QM, AXUSER secured/nonsecured, HBW/LBW debug, CGM, and special windows.
- QPC blocks: `QPC0` and `QPC1`, thirty DBFIFO CI update-address windows, secure and privileged DBFIFO windows, AXUSER subwindows for congestion queue, RX/TX WQE, doorbell FIFO, event queue interrupts, error FIFO, and QPC request/response.
- NIC packet-path blocks: `TMR`, `RXB_CORE`, `RXE0`, `RXE1`, RXE AXUSER completion-queue windows `CQ0` through `CQ31`, `TXS0/1`, `TXE0/1`, `TXB`, master-interface windows, `TX_AXUSER`, `SERDES0/1`, and `PHY`.
- MAC and port blocks: `PRT*_MAC_AUX`, `PRT*_MAC_CORE`, `NIC*_MAC_RS_FEC`, MAC global-stat control, RX/TX statistic windows, RS-FEC statistics, and four MAC channels with PCS, 128-bit MAC, and auto-negotiation windows.

The `DCORE0`, `DCORE1`, and visible `DCORE2` areas cover trace/debug infrastructure around compute and media blocks:

- One low ROM table region per data core, such as `mmDCORE0_ROM_TABLE_L_BASE`.
- Four HMMU groups per visible data core, each with CoreSight ROM table, STM, CTI, ETF, SPMU, BMON CTI, user CTI, and BMON windows.
- MME control, SBTE0 through SBTE4, and MME accumulator debug groups, mostly using ROM table, STM, CTI, ETF, SPMU, CTI0/CTI1, BMON, and ARC RTT windows.
- Scalar monitor/debug blocks: `SM_CS_DBG_ROM_TBL`, `SM_STM`, `SM_CTI`, `SM_ETF`, `SM_SPMU`, `SM_BMON_CTI`, `SM_USER_CTI`, `SM_BMON`, and `SM_BMON1`.
- Trace funnels and router/MIF funnel topology: `XFT`, `TFT0` through `TFT2`, `RTR0` through `RTR7`, and `MIF0` through `MIF3`, with ordering differing between even and odd data cores.
- EDMA0/EDMA1 debug groups and video decoder groups. `DCORE0` and `DCORE1` include both `VDEC0` and `VDEC1`; this chunk reaches only the beginning of `DCORE2_VDEC0`.

## Control Flow

There is no runtime control flow in this chunk. All content is preprocessor data used at compile time. The only ordering semantics are table-layout semantics: macros are grouped by ascending address and by hardware subsystem. The order is useful to generated consumers and reviewers because it mirrors the Gaudi2 MMIO address space.

The macro pattern is deterministic:

1. A block base macro names a register aperture and gives its absolute Gaudi2 MMIO address.
2. A `MAX_OFFSET` macro follows, describing the highest relevant block-local offset or range class used by generated driver tables.
3. A `SECTION` macro follows, describing the section/span grouping used by the Linux driver block map.

Most logical blocks use this exact triple. Long array-like blocks use sequentially numbered triples, such as `QMAN_WR64_BASE_ADDR0` through `QMAN_WR64_BASE_ADDR15`, DBFIFO update-address windows `0` through `29`, and RXE AXUSER completion-queue windows `CQ0` through `CQ31`.

## State And Persistence Behavior

The macros do not create software state and do not directly change hardware state. Their persistent value is build-time: every object file that includes this header sees the same symbolic addresses for Gaudi2 blocks. At runtime, driver code that uses these macros may read or write persistent hardware state through MMIO, but that side effect occurs in the consumer code, not in this header.

Because the values are compile-time constants, changing one macro changes every downstream binary use after recompilation. There is no runtime discovery, validation, or fallback in this chunk. Correctness depends on the generated constants matching the Gaudi2 hardware address map and the rest of the generated register headers.

## Dependencies

This header fragment depends on the broader Gaudi2 ASIC register generation scheme:

- Consumers expect `mm`-prefixed names for absolute MMIO base addresses.
- Consumers expect the paired non-`mm` `MAX_OFFSET` and `SECTION` names to share the same logical block prefix as the base macro.
- The constants must align with register-offset headers for individual registers under the same Gaudi2 ASIC family.
- The values are likely consumed by HabanaLabs debug, block-dump, register-access, security, and address-range code that accepts `u64` base addresses.

The chunk itself has no include dependencies in the local range, but the full header is integrated through Gaudi2 driver code under `drivers/accel/habanalabs` and must remain compatible with the C preprocessor and kernel integer constant rules.

## Integration Points

The primary integration point is any Gaudi2 driver path that needs block-level MMIO metadata rather than individual register offsets. Likely consumers include register dump collection, MMIO range validation, debugfs register access, RAZWI/error decoding, security aperture setup, and hardware bring-up diagnostics.

The NIC block constants integrate with Gaudi2 networking support. Queue managers and QPC constants expose the address layout for doorbells, completion queues, DBFIFOs, AXUSER settings, transmit/receive engines, timers, PHY/SERDES, and MAC/statistics regions. A driver component can use these macros to refer to `NIC10_QPC1_DBFIFOSECUR_CI_UPD_ADDR` or `NIC11_MAC_GLOB_STAT_RX*` windows without recomputing offsets.

The data-core constants integrate with compute, DMA, media, and hardware trace/debug support. HMMU, MME, SBTE, EDMA, VDEC, SPMU, CTI, ETF, STM, BMON, funnel, router, and MIF windows are all represented as block apertures. Diagnostic tooling can use these block definitions to decide which trace components exist under each DCORE and what address ranges are safe to traverse.

For final per-file reconciliation, this chunk must be joined with adjacent chunks because it begins mid-`NIC9_UMR0_14` and ends mid-`DCORE2`. The complete source file likely includes earlier NIC instances and later data-core blocks outside this chunk.

## Risks And Edge Cases

- The file is generated-style data with thousands of near-duplicate names. Copy/generation drift is the main risk: a single wrong digit in `NIC10`, `NIC11`, DCORE number, queue number, or address can direct MMIO access to the wrong block.
- Chunk boundaries are not semantic boundaries. The first line is only `NIC9_UMR0_14_COMPLETION_QUEUE_CI_1_SECTION`, whose base and max-offset macros are in the previous chunk. The last visible DCORE2 VDEC0 group continues beyond this chunk with at least the section macro for `DCORE2_VDEC0_USER_CTI` and later VDEC/BMON entries.
- Array-like naming must remain contiguous. Missing entries in `QMAN_WR64_BASE_ADDR*`, DBFIFO, or `RXE*_AXUSER_CQ*` sequences can break code that assumes fixed counts or generated loops.
- `BASE`, `MAX_OFFSET`, and `SECTION` values are not self-validating. A malformed value still compiles and can fail only during hardware access, debug collection, or security validation.
- Some section values are much larger than the adjacent block's `MAX_OFFSET`, especially end-of-group sections such as `NIC11_MAC_CH3_MAC_AN_SECTION 0x610800`. Consumers need to know whether `SECTION` is a local aperture length, a grouping carry value, or a generator-specific stride marker.
- The address map uses 64-bit constants. Consumers should avoid truncating `mm..._BASE` values into 32-bit variables even though the values visible in this chunk fit below 4 GiB.
- Security-sensitive users of these macros, such as allow-list or protection-table code, inherit the correctness of the generated map. An overly broad section or wrong base could expose or block unrelated MMIO.
- Data-core router/MIF funnel order differs between DCORE0/DCORE2 and DCORE1 in this chunk. Reviewers should not mechanically sort or normalize the order without checking hardware topology.

## Test Signals

Useful validation for this chunk is mostly static and hardware-integration focused:

- A generated-header consistency check should verify every `mm..._BASE` macro in the range has matching `..._MAX_OFFSET` and `..._SECTION` macros, except where the chunk boundary intentionally cuts a triple.
- Address monotonicity checks should confirm the listed blocks progress through the expected Gaudi2 MMIO ranges: `NIC9` near `0x588EE80` to `0x58EF800`, `NIC10` near `0x5900000` to `0x596F800`, `NIC11` near `0x5980000` to `0x59EF800`, then `DCORE0` at `0x6000000`, `DCORE1` at `0x6200000`, and `DCORE2` at `0x6400000`.
- Sequence checks should verify the repeated counts for complete NICs: two UMR banks with indices `0..14`, two QMs, two QPCs, DBFIFO update windows `0..29`, secure/privileged DBFIFO windows, and RXE completion queues `CQ0..CQ31`.
- Cross-instance diffs should compare `NIC10` and `NIC11` names and relative offsets. They should be structurally identical aside from NIC number and base-address stride.
- Cross-core diffs should compare `DCORE0` and `DCORE1` groups and flag intentional topology differences, such as funnel/router/MIF ordering and section sizes.
- Runtime smoke tests should exercise driver paths that enumerate block maps for NIC debug dumps, MAC statistics, HMMU/MME/EDMA/VDEC trace blocks, and register-access validation.
- Hardware error and debug tests should confirm that register dumps using these block bases do not fault, do not skip expected blocks, and do not read outside allowed Gaudi2 MMIO apertures.
- Security tests should confirm that any protection or allow-list code consuming `SECTION` metadata treats the large group-ending section values correctly and does not grant unintended access to adjacent blocks.

### subset-b-000995: lines 42834-45067

# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/gaudi2_blocks_linux_driver.h lines 42834-45067

## Purpose

This chunk is the final range of the auto-generated Gaudi2 block address map consumed by the HabanaLabs Linux driver. It contains only C preprocessor constants: each hardware block is represented by a `mm..._BASE` physical MMIO base address plus companion `..._MAX_OFFSET` and `..._SECTION` constants. The file is included by `gaudi2_regs.h`, so these constants become part of the generated register-definition layer used by Gaudi2 driver code, debug code, register dumps, and hardware bring-up paths.

The assigned range starts at the tail of the DCORE2 VDEC0 debug block definitions and then covers DCORE2 VDEC1, the full DCORE3 debug/CoreSight-style block map, host/PCIe/PSOC/CPU/PMMU/PDMA/KDMA/ROT/ARC-farm debug regions, HBM memory-controller debug regions, and NIC0 through NIC11 debug regions. It ends at the header guard close for `GAUDI2_BLOCKS_LINUX_DRIVER_H_`, so this is also the final chunk of the file.

The constants describe debug, trace, bus-monitor, CoreSight, and performance-monitor apertures rather than executable control logic. The important behavior is therefore not runtime branching, but stable address-space partitioning: later code can take a block base, know the valid offset range, and know how much address space is reserved before the next block.

## Important APIs, Types, And Data Surfaces

There are no functions, structs, enums, or exported runtime APIs in this range. The public surface is the generated macro namespace.

The macro pattern is:

- `mm<block>_BASE`: 64-bit unsigned MMIO base address for a Gaudi2 register block, using `ull` constants.
- `<block>_MAX_OFFSET`: highest modeled offset span for the block, usually `0x1000`, with larger values for RTT windows such as `0x1400`, CA53 at `0x141000`, and a few generated aggregate/special regions.
- `<block>_SECTION`: reserved section size for the block in the global address map. This is often equal to `0x1000`, but can be larger when a block reserves address space for sparse subregions or when it is the last named block before a larger gap.

Major block groups in this chunk include:

- DCORE2/DCORE3 video decode and DCORE3 subsystem debug blocks: VDEC, HMMU0-HMMU3, MME control/SBTE/ACC, SM, EDMA0/EDMA1, and XFT/TFT/RTR/MIF funnels.
- DCORE3 tracing and monitor blocks: CoreSight ROM tables, STM, CTI, ETF, SPMU, BMON, ARC RTT, user CTI, and funnel definitions.
- Host-facing debug blocks: CA53, PCI/PCIE, TOP/PSOC, PSOC ARC0/ARC1, PDMA0/PDMA1, XDMA, CPU, PMMU, DCORE XBAR funnels, ROT0/ROT1, ARC farm, KDMA, and PCIE VDEC0/VDEC1.
- HBM debug blocks for HBM0 through HBM5, each with MC0 and MC1 CoreSight debug blocks, user CTI regions, and funnel sections.
- NIC debug blocks for NIC0 through NIC11, each with two debug instances (`_0` and `_1`) covering CoreSight ROM table, STM, CTI, ETF, SPMU, user CTI, BMON CTI, BMON0/BMON1/BMON2, ARC RTT, TX funnel, and NCH funnel.

The final `#endif /* GAUDI2_BLOCKS_LINUX_DRIVER_H_ */` closes the include guard opened at the top of the generated header.

## Control Flow

This chunk has no runtime control flow. It is evaluated by the C preprocessor when translation units include `gaudi2_regs.h`, which includes this header. The operational flow is compile-time and declarative:

1. The include guard prevents multiple definition passes in the same translation unit.
2. The compiler sees a flat list of block-address macros.
3. Driver code can use these macros in MMIO access helpers, register dump tables, debug feature setup, or address validation logic.
4. The generated constants disappear after preprocessing and become literal numeric values in compiled code wherever referenced.

Although there are no loops or branches, the address map itself is structured. DCORE3 begins at `0x6600000`, host/PSOC/PDMA/CPU/PMMU/ROT/ARC/KDMA/PCIE debug blocks occupy roughly `0x6800000` through `0x6F1FFFF`, HBM debug blocks occupy roughly `0x7010000` through `0x72FFFFF`, and NIC debug blocks occupy `0x7300000` through `0x75FFFFF`. The repeated NIC layout increments by `0x40000` per NIC and uses a consistent `_0`/`_1` instance subdivision.

## State And Persistence Behavior

The file does not allocate state, mutate driver state, write hardware registers, or persist data to disk. Its only persistence is source-level: it stores the generated Gaudi2 hardware address map in the repository.

At build time these constants become compile-time literals. At runtime, any stateful effects come from other driver code that uses these bases to read or write hardware registers. If a macro is wrong, the persistent runtime effect would be in that consuming code: reads could target the wrong diagnostic block, writes could configure the wrong trace component, and register-range validation could admit or reject the wrong addresses.

The `MAX_OFFSET` and `SECTION` distinction is part of the persistent hardware-map contract. `MAX_OFFSET` describes the modeled register span inside a block, while `SECTION` describes the reserved address-space span before the next section. They should not be treated as interchangeable.

## Dependencies

This chunk depends on the generated-register build process that produced `gaudi2_blocks_linux_driver.h`. The header itself is marked as auto-generated and should not be hand-edited. It also depends on the broader Gaudi2 register namespace: `gaudi2_regs.h` includes this file so the block constants are available alongside per-register offsets.

Important external assumptions are:

- Driver MMIO helpers understand the Gaudi2 device address space and can translate these offsets into host-accessible register apertures.
- Consuming code uses the `mm..._BASE` constants with offsets from matching generated register headers rather than mixing unrelated block namespaces.
- Debug and tracing setup code knows the semantics of CoreSight-style components represented here: ROM tables, STM, CTI, ETF, SPMU, funnels, bus monitors, and ARC RTT windows.
- Hardware, firmware, and driver versions agree on this exact address map. These constants are not self-describing at runtime.

The visible direct integration point from a source perspective is `sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/gaudi2_regs.h`, which includes this header.

## Integration Points

The chunk is a foundation for Gaudi2 debug and observability integration. The DCORE, PCIe, PSOC, CPU, PMMU, ROT, ARC-farm, HBM, and NIC blocks named here are the address anchors for:

- Register dump and diagnostic code that walks generated block tables.
- CoreSight trace setup and collection paths using STM, CTI, ETF, ETR, funnel, ROM-table, and SPMU components.
- Bus-monitor and performance-monitor paths using BMON and SPMU blocks.
- Firmware or low-level driver debug paths that access ARC RTT windows for MME, EDMA, PDMA, ROT, NIC, PSOC ARC, and ARC farm components.
- Device bring-up, reset, and failure-analysis tooling that needs stable block boundaries for Gaudi2.

The HBM definitions integrate memory-controller debug surfaces into the same generated address map. The NIC0-NIC11 repeated definitions integrate all network-interface debug blocks with a common layout, making mechanical register dump or trace collection possible across NIC instances.

Because this is the final chunk of the header, merge/reconciliation should connect it to the preceding chunk as the continuation of the same auto-generated map and note that it closes the include guard.

## Risks And Edge Cases

- The file is auto-generated. Manual edits to a single macro can create subtle mismatches with hardware documentation, firmware expectations, or generated per-register offsets.
- Base addresses are security and reliability sensitive. A wrong `mm..._BASE` can cause MMIO reads or writes to hit a different unit than intended, which is especially risky for debug blocks that may affect tracing, monitoring, or firmware-visible state.
- `MAX_OFFSET` is commonly `0x1000`, but not always. RTT blocks often use `0x1400`, CA53 uses a much larger span, and aggregate/funnel sections can reserve large gaps. Consumers that assume every block is one 4 KiB page will mishandle these entries.
- `SECTION` often exceeds `MAX_OFFSET`; using `SECTION` as a valid register access limit may expose reserved or unmapped holes, while using `MAX_OFFSET` as an iteration stride may skip later blocks.
- The repeated NIC layout invites copy/paste or generator drift. NIC0 through NIC11 should remain structurally symmetric except for the expected base-address increments and final section sizes.
- The chunk starts after earlier DCORE2 VDEC0 lines. Research or tooling for only this chunk should not treat `DCORE2_VDEC0_USER_CTI_SECTION` as a complete block definition; its base and max-offset were defined before the requested range.
- The chunk ends the header. Removing or corrupting the final `#endif` would break every translation unit that includes `gaudi2_regs.h`.
- These constants are compile-time only; no runtime validation proves that a running ASIC actually implements the exact map. Hardware revision mismatches can therefore appear as MMIO failures or misleading debug dumps.

## Test Signals

Useful verification signals are mostly build, static, and hardware-diagnostic checks:

- The HabanaLabs driver should compile with `gaudi2_regs.h` including this header and no duplicate/missing macro-definition errors.
- Static generation checks should compare this range against the authoritative Gaudi2 hardware register database, especially DCORE3, HBM0-HBM5, and NIC0-NIC11 repeated layouts.
- A simple parser can verify every complete block triple has a `mm..._BASE`, matching `..._MAX_OFFSET`, and matching `..._SECTION` name, while allowing the first partial `DCORE2_VDEC0_USER_CTI_SECTION` line because the chunk starts mid-block.
- Register-dump tooling should be able to enumerate representative blocks from each group: `DCORE3_HMMU*`, `DCORE3_MME_*`, `PCIE_*`, `PSOC_*`, `PDMA*`, `PMMU_*`, `HBM*_MC*`, and `NIC*_DBG_*`.
- Hardware smoke tests should read non-destructive identification or status registers from selected CoreSight ROM table/funnel/ETF/SPMU/BMON blocks and confirm accesses land at the expected units.
- NIC debug validation should compare NIC0 through NIC11 block spacing and ensure `_0` and `_1` debug-instance layouts remain symmetric.
- HBM debug validation should confirm both MC0 and MC1 definitions exist for each HBM stack and that their funnel sections reserve the expected address space.
- Include-guard validation should preprocess a file that includes `gaudi2_regs.h` multiple times and confirm the guard prevents redefinition noise.
