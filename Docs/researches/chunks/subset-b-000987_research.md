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
