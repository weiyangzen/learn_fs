# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_d.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001486`: lines 1-2975, `Docs/researches/chunks/subset-b-001486_research.md`
- `subset-b-001487`: lines 2976-3577, `Docs/researches/chunks/subset-b-001487_research.md`

## Chunk Research

### subset-b-001486: lines 1-2975

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

### subset-b-001487: lines 2976-3577

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_d.h lines 2976-3577

## Scope And Purpose

This chunk is the tail of AMDGPU's generated BIF 5.1 register address header. It contains only C preprocessor `#define` constants; there are no functions, structs, enums, local variables, or executable statements. The constants map symbolic register names to numeric register addresses for the Bus Interface (BIF), PCIe controller/link-management logic, PCIe PHY, and PIF blocks for the `PSX80` and `PSX81` instances.

The practical purpose is to give low-level AMDGPU code stable compile-time names for indirect PCIe/BIF/PHY/PIF registers. Driver code can then pass these addresses to register-access helpers, usually together with field masks from the paired `bif_5_1_sh_mask.h` header. Correctness depends on the exact numeric values: a one-bit or one-instance error in this file can redirect a read or write to the wrong hardware register without creating an obvious compile-time failure.

This range starts by completing the `PSX80_BIF_LM_*` link-management address family, then defines the full `PSX81_BIF_PCIE_*`, `PSX81_BIF_SWRST_*`, `PSX81_BIF_LM_*`, `PSX80_PHY0_*`, `PSX81_PHY0_*`, `PSX80_PIF0_*`, and `PSX81_PIF0_*` address families. It ends with the header guard close for `BIF_5_1_D_H`.

## Important APIs, Types, And Macros

There are no C APIs or types in this chunk. The exported interface is the macro namespace:

- `ixPSX80_BIF_LM_*` and `ixPSX81_BIF_LM_*` name PCIe link-management registers such as TX/RX lane mux controls, lane enable, PRBS control, and power-control registers.
- `ixPSX81_BIF_PCIE_*` names PCIe controller registers for scratch/debug state, RX NAK counters, controller/config/bus controls, link-controller state/status, last received/transmitted TLP capture, I2C register access, port status, performance counters, strap registers, PRBS status/counters, and the controller-side soft-reset command/control region.
- `ixPSX81_BIF_SWRST_*` names command/status, general-control, command, and control registers used for BIF/PCIe soft-reset sequencing.
- `ixPSX80_PHY0_COM_COMMON_*` and `ixPSX81_PHY0_COM_COMMON_*` name common PCIe PHY registers for fuses, electrical idle, design-for-test/debug, de-emphasis selection, lane power management, adaptation controls, lane control, TX/RX test debug, and CDR phase/frequency controls.
- `ixPSX80_PHY0_RX_*` and `ixPSX81_PHY0_RX_*` name RX command-bus, RX control, DLL control, RX test, electrical-idle debug, adaptation, FOM calculation, adaptation-bypass, debug-bypass, and adaptation-debug registers. Each group has a broadcast address and per-lane addresses for lanes 0 through 7.
- `ixPSX80_PHY0_TX_*` and `ixPSX81_PHY0_TX_*` name TX command-bus, DFX, de-emphasis, margin/de-emphasis test/status, TX control, and TX global command-bus registers, again with broadcast and lane 0 through 7 variants.
- `ixPSX80_PHY0_HTPLL_ROPLL_*`, `ixPSX81_PHY0_HTPLL_ROPLL_*`, `ixPSX80_PHY0_LCPLL_LCPLL_*`, and `ixPSX81_PHY0_LCPLL_LCPLL_*` name ring/HT PLL and LC PLL power, control, test/debug, frequency-mode, update, fuse/process, and VCO-control registers.
- `ixPSX80_PIF0_*` and `ixPSX81_PIF0_*` name PIF scratch/debug/strap/control, TX/RX control, global override, command-bus status/control, and per-lane override registers for lanes 0 through 7.

The naming convention matters. `ix` prefixes indicate indexed or indirect register addresses rather than the ordinary `mm` register offsets at the start of the file. The `PSX80` and `PSX81` prefixes distinguish two sibling PCIe/PHY/PIF address spaces: for example the `PSX80` BIF PCIe region is based around `0x1400000`, while `PSX81` is based around `0x1410000`; `PSX80_PHY0` uses `0x120...` addresses, while `PSX81_PHY0` uses `0x121...`; `PSX80_PIF0` uses `0x110...`, while `PSX81_PIF0` uses `0x111...`.

## Control Flow

This chunk has no runtime control flow. It shapes caller behavior by providing the register addresses that consumers use in hardware read, write, and read-modify-write sequences.

A typical consumer flow is:

1. Select the correct BIF 5.1 register header for the ASIC/IP generation.
2. Choose an `ixPSX80_*` or `ixPSX81_*` macro for the intended PCIe, BIF, PHY, PLL, or PIF register.
3. Access the register through the AMDGPU register I/O layer or through a PCIe/indirect register-access path.
4. If modifying fields, combine this address macro with field masks and shifts from `bif_5_1_sh_mask.h`.
5. Poll status, program controls, clear counters, or trigger state changes according to the hardware block's access semantics.

The line range is mainly an address map, so branching and sequencing live in callers such as VI-era interrupt handling, UVD setup, PCIe management, power-management, diagnostics, and hardware bring-up code. Files such as `tonga_ih.c`, `cz_ih.c`, `iceland_ih.c`, and `uvd_v6_0.c` include `bif_5_1_d.h`; the IH files also include `bif_5_1_sh_mask.h` and use the register/mask pattern through `RREG32()`, `WREG32()`, and `REG_SET_FIELD()` for BIF interrupt-control registers. This chunk's `ix*` addresses support the same generated-register contract for indirect PCIe/PHY/PIF blocks rather than ordinary `mm*` offsets.

## State And Persistence Behavior

The header chunk stores no Linux or driver state. It defines names for hardware registers whose values live in the GPU and PCIe/PHY/PIF blocks.

Registers named here can expose or control persistent hardware state such as link-management muxing, lane enablement, PRBS mode and error counters, PCIe controller counters and captured TLP data, soft-reset command state, PHY fuses, electrical-idle detection, RX/TX adaptation and debug controls, PLL power/control state, and per-lane PIF override configuration. Those hardware values may persist until a later driver write, firmware/SMU action, link retrain, soft reset, suspend/resume transition, BACO or power-gating transition, hot reset, or full device reset.

The header does not encode register access semantics. Some addresses likely identify read-only status, some are writable controls, some may be sticky status or counter registers, and some control fields may be self-clearing or safe only in specific link states. Callers must rely on hardware documentation, generated field masks, and established driver sequencing to avoid treating a diagnostic/status address like an ordinary writable configuration register.

## Dependencies And Integration Points

The direct dependency is only the C preprocessor and the `BIF_5_1_D_H` include guard. In practice, this file is part of a generated AMD ASIC register-header set:

- `bif_5_1_d.h` supplies register addresses.
- `bif_5_1_sh_mask.h` supplies the bit masks and shifts for fields inside those registers.
- AMDGPU register helpers such as `RREG32()`, `WREG32()`, `REG_SET_FIELD()`, and PCIe/indirect variants perform the actual I/O.
- The surrounding VI/Polaris-era AMDGPU driver chooses this BIF generation through include selection in IP blocks such as interrupt handling and UVD support.

Important integration points for this chunk are PCIe link-management and diagnostics paths. `BIF_LM_*` addresses support lane muxing, lane enable, PRBS, and power-control operations. `BIF_PCIE_*` addresses support controller status, link-controller state capture, performance counters, straps, PRBS counters, last-TLP debug capture, and soft-reset controls. `PHY0_*` addresses support common PHY configuration, RX/TX lane programming, RX adaptation/FOM/debug, TX margin/de-emphasis/control, and PLL control. `PIF0_*` addresses support lane overrides and command-bus/global PIF controls.

The source path is under a repository named `ceph-client`, but this file is AMDGPU Linux kernel driver register metadata. There is no Ceph filesystem behavior in this chunk.

## Risks And Edge Cases

The main risk is silent hardware misaddressing. These macros are raw numeric addresses; if a macro points at the wrong base, lane, or instance, the compiler will still accept callers, but runtime reads and writes will target the wrong register.

The `PSX80` and `PSX81` families are intentionally similar and differ mostly by address-space base. Copy/paste or generation mistakes that swap `0x120...` with `0x121...`, `0x110...` with `0x111...`, or `0x140...` with `0x141...` would affect only one instance and could be hard to diagnose on systems that do not exercise both paths.

The lane-indexed PHY and PIF definitions are repetitive and vulnerable to lane-offset errors. RX lane addresses step by `0x100` from lane 0 through lane 7, TX lane addresses use a separate `0x...2000`-style base and also step by `0x100`, and broadcast addresses use high `0xfe` or `0xff` lane-selector encodings. A swapped lane suffix or broadcast/per-lane mix-up could make debugging tools report the wrong lane, power down the wrong lane, or apply an adaptation override globally when a per-lane write was intended.

Several register groups control low-level link stability. Misuse of link-management power-control, PRBS, PIF lane override, RX adaptation, TX de-emphasis, PLL power/control, or BIF soft-reset addresses can cause link retraining failures, reduced link width/speed, transient GPU disappearance, or persistent PCIe errors until reset.

This chunk begins after the first two `ixPSX80_BIF_LM_PCIETXMUX*` entries, which are in the previous chunk. The final per-file reconciliation should keep the complete `PSX80_BIF_LM_*` family together across the chunk boundary.

## Test Signals

Useful validation is mostly build-time and hardware-observable:

- Kernel build coverage for AMDGPU configurations that include `bif_5_1_d.h` catches missing or renamed macros.
- Register smoke tests or driver bring-up on BIF 5.1 ASICs should read sensible values from `PSX80` and `PSX81` PCIe, PHY, and PIF address spaces.
- PCIe link speed and width should remain stable across boot, reset, suspend/resume, runtime power transitions, and link retrain operations.
- PRBS diagnostics should show counters changing on the expected lanes and clear through the expected control/status registers.
- PHY/PIF lane override and power-management testing should affect only the intended lane or broadcast domain.
- PLL programming and power transitions should not produce hangs, link drops, or repeated recovery/equalization loops.
- Interrupt/UVD/IP-block builds that include this header should continue to compile with the paired `bif_5_1_sh_mask.h` field definitions.

Regression symptoms from bad constants include wrong debug/status readings, PRBS errors attributed to the wrong lane, failed lane power transitions, unexpected link downtraining, AER or PCIe error noise, resume failures, GPU resets during link-management operations, or inability to access the intended indirect register instance.

## Cross-Chunk Notes

The previous chunk of `bif_5_1_d.h` contains the ordinary `mm*` BIF offsets, much of the base BIF/PCIe address map, and the start of the `PSX80_BIF_PCIE` and `PSX80_BIF_LM` families. This chunk completes the file by adding the second `PSX81` PCIe/BIF instance plus the repeated PHY/PIF address families for `PSX80` and `PSX81`. The final per-file document should treat both chunks as one generated hardware address map paired with `bif_5_1_sh_mask.h`, not as executable driver logic.
