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
