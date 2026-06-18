# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_d.h

Chunk: `subset-b-001486`
Covered source range: lines 1-2975 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_d.h`

## Purpose

This chunk is the front 2,975 lines of AMD's generated BIF 5.1 register address header. It does not implement executable driver logic. Its purpose is to publish C preprocessor constants that map symbolic BIF, PCIe, RFE, PSX, and PCI configuration register names to the numeric offsets or indirect addresses used by AMDGPU and PowerPlay code for VI-era ASICs such as Tonga, Iceland, Carrizo, and Polaris-family paths.

The header pairs with `bif_5_1_sh_mask.h`, which supplies field masks and shifts for the same registers. This `*_d.h` file supplies register addresses only. Callers combine these address macros with access helpers such as `RREG32`, `WREG32`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, or command-table entries, then use the mask header when they need field-level read/modify/write behavior.

The assigned range contains 2,950 `#define` lines. The main covered register families are:

- top-level BIF MMIO registers, indirect MM access registers, bus/config apertures, scratch registers, reset controls, interrupt controls, HDP/GARLIC coherency flush controls, doorbell controls, host bus tracking, peer framebuffer offsets, BACO controls, VDDGFX ranges, BIOS scratch registers, and a BIF ring-buffer block;
- PCI configuration and enhanced capability offsets for function 0, including PCIe, MSI, VC, AER, BAR, DPA, ACS, ATS, PASID, LTR, and related capability records;
- indirect aliases for many top-level BIF registers with `_IND` suffixes, using address spaces such as `0x109...` and `0x130...`;
- PCIe core and port register addresses such as link control, link training, speed, width, flow-control, RX/TX credits, error control, performance counters, straps, PRBS diagnostics, and DPA controls;
- repeated D2F1 through D3F5 device/function blocks, each defining the same PCIe port, PCI bridge/config, slot/root, MSI, AER, lane equalization, ACS, and multicast capability address layout with a different high address prefix;
- PSX80 and PSX81 wrapper/BIF blocks for strap, link training, per-port hold-training, lane-count accounting, EFUSE, wrap scratch, DTM, delayline, and PIF adaptation registers;
- RFE reset/power-down command/status registers and the beginning of the PSX80 BIF PCIe block up to `ixPSX80_BIF_SWRST_CONTROL_6` at the chunk boundary.

The range ends at line 2975 in the middle of the PSX80 BIF register list. Later chunks must cover the remaining PSX80 BIF entries and the file footer before a final file-level report is complete.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, typedefs, or runtime APIs in this chunk. The public surface is macro names.

The naming conventions are the important API:

- `mm*` macros are direct register offsets in MMIO or indexed register spaces used by the AMDGPU register access helpers.
- `ix*` macros are indirect or indexed register addresses, commonly used through PCIe or NB/GBIF index/data apertures.
- `_IND` suffixes are alternate indirect addresses for top-level BIF registers.
- `D2F1`, `D2F2`, ..., `D3F5` prefixes encode repeated PCI device/function register spaces. The low offsets are mostly identical within each instance, while the high nibble/prefix selects the target function.
- `PSX80` and `PSX81` prefixes identify wrapper instances or related address domains for PCIe/BIF wrapper registers.

Important direct BIF register groups include:

- `mmMM_INDEX`, `mmMM_INDEX_HI`, `mmMM_DATA`, and `mmBIF_MM_INDACCESS_CNTL`: indirect MM register access selectors/data and controls.
- `mmBUS_CNTL`, `mmCONFIG_CNTL`, `mmCONFIG_MEMSIZE`, `mmCONFIG_F0_BASE`, `mmCONFIG_APER_SIZE`, and `mmCONFIG_REG_APER_SIZE`: host bus and PCI configuration aperture setup.
- `mmBIF_SCRATCH0`, `mmBIF_SCRATCH1`, and `mmBIOS_SCRATCH_0` through `mmBIOS_SCRATCH_15`: scratch registers used for driver/firmware/BIOS handoff and display or power-management state.
- `mmBX_RESET_EN`, `mmBX_RESET_CNTL`, `mmBIF_RESET_EN`, `mmBIF_RESET_CNTL`, `mmBIF_RFE_SOFTRST_CNTL`, `mmBIF_RFE_CLIENT_SOFTRST_TRIGGER`, and related RFE reset macros: reset-enablement and reset-trigger address definitions.
- `mmINTERRUPT_CNTL` and `mmINTERRUPT_CNTL2`: BIF-side interrupt-controller setup used by VI interrupt handlers to configure dummy reads and interrupt behavior.
- `mmBIF_DOORBELL_CNTL`, `mmBIF_DOORBELL_GBLAPER*_LOWER`, and `mmBIF_DOORBELL_GBLAPER*_UPPER`: doorbell monitor/global aperture address definitions.
- `mmBIF_FB_EN`, `mmBIF_XDMA_LO`, `mmBIF_XDMA_HI`, peer range/offset registers, and VDDGFX range registers: framebuffer aperture, peer access, and power-domain range definitions.
- `mmHDP_*_COHERENCY_FLUSH_CNTL`, `mmGPU_HDP_FLUSH_REQ`, `mmGPU_HDP_FLUSH_DONE`, `mmGARLIC_FLUSH_*`, `mmGPU_GARLIC_FLUSH_REQ`, and `mmGPU_GARLIC_FLUSH_DONE`: addresses for coherency and cache-flush request/done handshakes.
- `mmBIF_RB_CNTL`, `mmBIF_RB_BASE`, `mmBIF_RB_RPTR`, `mmBIF_RB_WPTR`, and write-pointer address registers: BIF ring-buffer register definitions.
- `mmBACO_CNTL`, `mmBACO_CNTL_MISC`, `mmBIF_BACO_DEBUG`, and `mmBIF_BACO_DEBUG_LATCH`: BACO power-state and debug register addresses.

Important PCIe/config register groups include:

- standard PCI config aliases such as `mmVENDOR_ID`, `mmDEVICE_ID`, `mmCOMMAND`, `mmSTATUS`, BAR registers, `mmROM_BASE_ADDR`, `mmCAP_PTR`, and interrupt line/pin registers;
- PCIe capability registers such as `mmPCIE_CAP`, `mmDEVICE_CAP`, `mmDEVICE_CNTL`, `mmLINK_CAP`, `mmLINK_CNTL`, `mmLINK_STATUS`, and their version-2 equivalents;
- enhanced capability blocks for vendor-specific capability, VC, device serial number, AER, BAR, power budget, DPA, secondary PCIe, ACS, ATS, page request, PASID, TPH requester, multicast, and LTR;
- PCIe core indirect registers such as `ixPCIE_CNTL`, `ixPCIE_CONFIG_CNTL`, `ixPCIE_LC_*`, `ixPCIE_RX_*`, `ixPCIE_TX_*`, `ixPCIE_PERF_*`, strap registers, PRBS registers, and DPA substate allocation registers.

The repeated D2F/D3F blocks define the same conceptual API for ten secondary functions. Each block includes a port index/data pair, port control, TX/RX credit and sequence registers, link-control registers, PCI bridge/config registers, slot/root capability registers, MSI mapping registers, AER status/log registers, lane equalization registers, ACS registers, and multicast/overlay BAR registers.

## Control Flow

This header has no runtime control flow. The only compile-time control flow in the assigned range is the include guard:

- `#ifndef BIF_5_1_D_H`
- `#define BIF_5_1_D_H`

Runtime control flow appears in consumers that use these constants as register addresses. Typical patterns are:

- read a register address macro with `RREG32` or a PCIe/SOC15 variant;
- use a corresponding field macro from `bif_5_1_sh_mask.h` or a sibling mask header to update selected bits;
- write the value back with `WREG32` or a command-table read/modify/write operation;
- poll a status register until a hardware bit changes.

Concrete integration examples visible in the tree include VI interrupt handlers (`tonga_ih.c`, `iceland_ih.c`, `cz_ih.c`) writing `mmINTERRUPT_CNTL2`, reading `mmINTERRUPT_CNTL`, setting BIF interrupt fields, and writing `mmINTERRUPT_CNTL` during interrupt-ring initialization. Tonga BACO code uses `mmBACO_CNTL`, `mmBIF_FB_EN`, and `mmBIOS_SCRATCH_6/7` inside BACO entry/exit command tables. GMC code uses `mmBIF_FB_EN` to enable or disable framebuffer reads/writes. ATOM BIOS/display code reads and writes `mmBIOS_SCRATCH_*`. VI/CIK PCIe code uses `ixPCIE_LC_SPEED_CNTL`, `ixPCIE_LC_*`, `ixPCIE_PERF_*`, and RX NAK counters for link management and diagnostics.

## State And Persistence Behavior

The header itself is stateless. It contributes constants at compile time and does not allocate memory, persist data, or execute initialization.

The referenced hardware registers do hold mutable device state. Writes through these macros can affect:

- PCI configuration-space identity, command/status, BAR, bridge, MSI, slot/root, and enhanced capability state;
- PCIe link training, link speed, link width, equalization, flow-control credits, RX/TX sequencing, replay behavior, PRBS/error counters, and performance counters;
- BIF interrupt routing and dummy-read behavior;
- host/GPU coherency flush request/done state for HDP and GARLIC paths;
- framebuffer access enablement and peer/doorbell apertures;
- BACO entry/exit, isolation, clocks, reset, and debug state;
- reset/power-down state in RFE and PSX wrapper domains;
- scratch registers used as retained handoff or diagnostic state across firmware, BIOS, driver, suspend/resume, or reset paths depending on hardware retention rules.

Because this is an address header, persistence behavior is indirect: the same constant can be harmless when read for diagnostics or disruptive when used as a write target. Incorrect addresses can silently target the wrong register and leave persistent hardware state inconsistent until reset or power-cycle.

## Dependencies And Integration Points

Direct dependencies are minimal: a C preprocessor and consumers that include the header. The file is guarded by `BIF_5_1_D_H` and has no includes of its own in the assigned range.

Important paired or adjacent headers include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_sh_mask.h` for field masks/shifts;
- older/newer BIF address headers such as `bif_4_1_d.h`, `bif_5_0_d.h`, and later NBIF/NBIO `*_offset.h` headers that carry same-named or successor registers;
- PCIe and interrupt mask headers used by consumers that combine address constants from this file with field constants from matching generation headers.

Known direct include sites for this header are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v6_0.c`;
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/tonga_ih.c`;
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/iceland_ih.c`;
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cz_ih.c`.

Broader integration points are AMDGPU's register access layer, PowerPlay BACO command sequencing, GMC framebuffer aperture setup, ATOM BIOS scratch handling, interrupt-handler initialization, PCIe link-management paths, and hardware diagnostics/performance-counter flows. Several same-named address macros appear in later NBIF/NBIO generations with different base-index handling, so integration code must use the header matching the ASIC generation and access method.

## Risks And Edge Cases

The main risk is silent hardware misaddressing. These macros are plain numbers; the compiler cannot verify that a `mm*` direct MMIO offset is used with the right accessor, that an `ix*` indirect address is written through the right index/data path, or that a D2F/D3F function prefix matches the intended hardware function.

Address-family confusion is especially risky:

- top-level `mmPCIE_*` config offsets, global `ixPCIE_*` indirect addresses, and per-function `ixD2F*_*`/`ixD3F*_*` addresses can describe similar conceptual registers in different address spaces;
- `_IND` aliases add another access path for many BIF registers;
- PSX80/PSX81 wrapper addresses share repeated names and port letters, so instance selection errors can be hard to spot in review;
- repeated lane equalization macros intentionally map lane pairs to the same dword offsets, so duplicate numeric values are expected and should not automatically be treated as generator defects.

Many target registers control disruptive hardware behavior: BACO power-off/isolation, BIF/RFE/PSX resets, framebuffer access, doorbells, interrupt control, PCIe link training, link speed/width, RX/TX credit behavior, and PRBS/error injection or diagnostics. A wrong write can hang the PCIe link, break interrupt delivery, corrupt peer or doorbell aperture behavior, make the framebuffer inaccessible, or require a GPU reset.

The chunk boundary is a research boundary, not a logical file boundary. It stops in the middle of the PSX80 BIF register block at `ixPSX80_BIF_SWRST_CONTROL_6`; later registers and the closing include guard are outside this work item. Any final file-level conclusions about the complete PSX80 block must be reconciled with subsequent chunks.

Generated headers also carry review risk. Numeric edits may look mechanical but encode silicon contracts. Manual edits, generator changes, or mixing constants from neighboring ASIC generations can compile cleanly while changing low-level behavior.

## Test Signals

Useful validation is mostly build, static consistency, and hardware behavior coverage:

- Compile translation units that include `bif_5_1_d.h`, especially `uvd_v6_0.c`, `tonga_ih.c`, `iceland_ih.c`, and `cz_ih.c`.
- Build PowerPlay/Tonga BACO and GMC paths that use same-generation BIF address macros with `bif_5_1_sh_mask.h` field definitions.
- Static checks for duplicate macro names, unexpected value changes versus the generated register database, and consistency between address macros in `bif_5_1_d.h` and field-prefix macros in `bif_5_1_sh_mask.h`.
- Static checks that direct `mm*` registers are accessed through direct MMIO/SOC15 helpers and `ix*` registers through the intended indirect/PCIe helpers.
- Interrupt-ring initialization tests on supported VI hardware, validating that `mmINTERRUPT_CNTL` and `mmINTERRUPT_CNTL2` programming allows MSI/interrupt delivery and dummy-read behavior to work.
- GMC framebuffer aperture tests around `mmBIF_FB_EN`, including init, suspend/resume, reset, and BACO transitions.
- BACO enter/exit tests on Tonga/related ASICs covering `mmBACO_CNTL`, BIF clock/reset/isolation state, and scratch-register cleanup.
- PCIe link-management tests for speed changes, width changes, retraining, ASPM/L0s/L1 behavior, hot reset, function-level reset, and recovery after link errors using the `ixPCIE_LC_*`, `ixPCIE_RX_*`, and `ixPCIE_TX_*` families.
- Diagnostic/performance tests that read `ixPCIE_PERF_*`, RX NAK counters, PRBS counters, and lane equalization/status registers and compare against expected hardware behavior.
- Suspend/resume and runtime-PM tests that verify scratch, doorbell, interrupt, framebuffer, PCIe, and BACO state is restored or intentionally retained after low-power transitions.
