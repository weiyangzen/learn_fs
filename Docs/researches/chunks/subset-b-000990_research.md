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
