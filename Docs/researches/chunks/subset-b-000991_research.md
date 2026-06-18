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
