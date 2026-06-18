# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_4_1_sh_mask.h

Chunk: `subset-b-001479`
Covered source range: lines 1-4515 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_4_1_sh_mask.h`

## Purpose

This chunk is the front portion of AMD's generated BIF 4.1 register field mask header. It contains no executable driver logic. Its role is to publish preprocessor constants that describe bit masks and shift counts for BIF, PCI, PCIe, PCIEP, and early PB0 PHY registers used by CIK-era AMD GPU support code.

The header pairs with `bif_4_1_d.h`, which defines register addresses such as `mmBACO_CNTL`, `mmPCIE_UNCORR_ERR_STATUS`, `ixPCIE_LC_SPEED_CNTL`, and `ixPB0_GLB_CTRL_REG0`. This file supplies the field-level constants used to extract, compose, poll, and update those registers.

The covered range includes:

- global BIF, MM index/data, bus, VGA/config aperture, reset, interrupt, debug, and scratch fields;
- SMBus pad/control fields, XDMA windows, BIF feature controls, doorbell filtering, bus/device/function lists, and BIF performance counters;
- HDP and GARLIC coherency flush request/done fields, peer framebuffer offset windows, SSA aperture windows, and BACO power/isolation/status fields;
- PCI configuration-space fields for vendor/device IDs, command/status, BARs, PM capability, PCIe capability, MSI, VSEC, VC, device serial number, AER, BAR sizing, power budget, DPA, ACS, ATS, PRI/page request, PASID, TPH, multicast, and LTR capabilities;
- PCIe indirect index/data registers, debug, interrupt, RX/TX control, flow-control, error, link-controller, strap, PRBS, performance-counter, and PCIEP port/link fields;
- the start of PB0 physical bus interface definitions, including global controls, SCI status overrides, straps, DFT/jitter injection, PLL controls/overrides, RX global controls, RX overrides, and RX lane 0-4 plus the first lane 5 field.

The source file continues beyond this chunk to line 10252. This chunk ends inside the PB0 RX lane field family, so later chunk reports must complete the lane, TX, and remaining PHY/PB blocks before a final file-level report is merged.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or runtime APIs in this range. The exposed interface is entirely macro constants.

The dominant naming contract is:

- `<REGISTER>__<FIELD>_MASK` gives the bit mask for the field inside a 32-bit register.
- `<REGISTER>__<FIELD>__SHIFT` gives the right shift needed to normalize that field.
- Register prefixes match address macros in `bif_4_1_d.h`, usually with `mm` for memory-mapped/config-space registers and `ix` for indexed PCIe/PHY registers.

The assigned range contains 4,490 `#define` lines: 2,245 mask constants and 2,244 shift constants. The one intentional chunk-boundary imbalance is `PB0_RX_LANE5_CTRL_REG0__RX_BACKUP_5_MASK` at line 4515; its matching shift appears at line 4516 outside this work item.

Important register families in this chunk include:

- `MM_INDEX`, `MM_INDEX_HI`, and `MM_DATA`: indirect MMIO address/data field definitions.
- `BUS_CNTL`, `CONFIG_CNTL`, `CONFIG_MEMSIZE`, `CONFIG_F0_BASE`, `CONFIG_APER_SIZE`, and `CONFIG_REG_APER_SIZE`: host aperture, VGA, BIOS ROM, and config aperture control fields.
- `BIF_SCRATCH*` and `BIOS_SCRATCH_*`: 32-bit scratch fields used by firmware/driver handoff and diagnostics.
- `BACO_CNTL`, `BF_ANA_ISO_CNTL`, `MEM_TYPE_CNTL`, `BIF_BACO_DEBUG`, `BIF_BACO_DEBUG_LATCH`, and `BACO_CNTL_MISC`: BACO entry/exit, clock gating, isolation, reset, power-good, memory/analog isolation, and request-blocking fields.
- `BIF_BUSNUM_*`, `BIF_DEVFUNCNUM_*`, `CAPTURE_HOST_BUSNUM`, and `HOST_BUSNUM`: bus/device/function filtering, capture, and autoupdate fields.
- `BIF_XDMA_*`, `BIF_FB_EN`, `PEER_REG_RANGE*`, and `PEER*_FB_OFFSET_*`: XDMA and peer/framebuffer aperture controls.
- `GPU_HDP_FLUSH_REQ/DONE` and `GPU_GARLIC_FLUSH_REQ/DONE`: per-engine request/done bits for CP0-CP9 and SDMA0/1 coherency flushes.
- `GARLIC_FLUSH_*` and `GARLIC_COHE_*`: global GARLIC flush controls, address windows 0-7, flush request, and register-address mappings for CP, UVD, SDMA, SAM/SAB, VCE, and doorbell-related coherency points.
- `COMMAND`, `STATUS`, `PMI_*`, `PCIE_CAP*`, `DEVICE_*`, `LINK_*`, `MSI_*`, `PCIE_ADV_ERR_*`, `PCIE_UNCORR_ERR_*`, `PCIE_CORR_ERR_*`, and `PCIE_HDR_LOG*`: PCI/PCIe standard and extended capability fields.
- `PCIE_ACS_*`, `PCIE_ATS_*`, `PCIE_PAGE_REQ_*`, `PCIE_PASID_*`, `PCIE_TPH_REQR_*`, `PCIE_MC_*`, and `PCIE_LTR_*`: IOMMU/virtualization, page request, PASID, TPH, multicast, and latency-tolerance capability controls.
- `PCIE_CNTL`, `PCIE_CONFIG_CNTL`, `PCIE_RX_CNTL*`, `PCIE_TX_*`, `PCIE_FC_*`, `PCIE_ERR_CNTL`, `PCIE_INT_*`, and `PCIE_PERF_*`: internal PCIe controller controls, ordering/error behavior, transmit credits, requester ID, interrupts, and performance counters.
- `PCIE_LC_*`: link-controller controls for LTSSM state/history, link width, speed changes, equalization coefficients, FTS counts, corrupted/disabled lanes, L0s/L1 behavior, reconfiguration, bandwidth change, hot reset, wake behavior, and equalization settings.
- `PCIE_STRAP_*` and `PCIEP_STRAP_*`: strap-derived enable bits for functions 0-2, capability exposure, link config, PASID width, FLR, clock PM, compliance modes, lane reversal, OBFF/LTR, and related PCIe/PCIEP options.
- `PCIE_PRBS_*`: PRBS enable, mode, lock, bit count, error count, and lane status fields used for link/PHY validation.
- `PB0_*`: beginning of the physical bus block 0 register definitions, covering PHY global debug/control, SCI override of lane mode/frequency/DLL lock, termination and power-good overrides, straps for RX/TX/PLL/pins, DFT jitter injection, PLL RO/LC controls, RX global equalization/CDR/FOM/DLL settings, RX power overrides, and RX lane status/control fields.

Some generated macro names include awkward doubled suffixes, for example `BF_ANA_ISO_CNTL__BF_ANA_ISO_DIS_MASK_MASK` and `PCIE_PRBS_MISC__PRBS_CHK_ERR_MASK_MASK`. These are still part of the generated ABI and should not be manually "cleaned up" without changing all users and verifying the hardware database source.

## Control Flow

This header has no runtime control flow. The only compile-time control structure in the assigned range is the include guard:

- `#ifndef BIF_4_1_SH_MASK_H`
- `#define BIF_4_1_SH_MASK_H`

At runtime, the constants influence control flow in the callers that read or write hardware registers. Common call patterns are:

- read a 32-bit register through an AMDGPU helper such as `RREG32`, `RREG32_PCIE`, or `RREG32_PCIE_PORT`;
- isolate a field with `value & <REGISTER>__<FIELD>_MASK`;
- normalize it with `>> <REGISTER>__<FIELD>__SHIFT`;
- compare against a state value, branch on that state, or poll until it changes;
- update a field by clearing the mask, shifting the desired value into position, ORing it in, and writing the register back.

Examples visible elsewhere in the tree include `cik.c` reading `PCIE_LC_SPEED_CNTL__LC_CURRENT_DATA_RATE_MASK` and `PCIE_LC_SPEED_CNTL__LC_CURRENT_DATA_RATE__SHIFT` to report PCIe data rate, and BACO command tables in `ci_baco.c` waiting on `BACO_CNTL__BACO_MODE_MASK` during BACO entry and exit.

The hardware-level flows represented by the constants are state machines even though the header is not: BACO power transitions, PCIe link training and speed changes, AER error recording, interrupt status/mask handling, coherency flush request/done handshakes, PRBS tests, and PHY RX/PLL override sequences all rely on these fields being correct.

## State And Persistence Behavior

The header itself is stateless. Its constants are compiled into consumers and do not allocate memory, mutate data, or persist anything on disk.

The state affected by consumers is device state in memory-mapped, configuration-space, or indexed hardware registers. Depending on the register, writes can persist until driver rewrite, firmware action, FLR, BACO transition, suspend/resume, PCIe link reset, hot reset, GPU reset, or full power removal.

Important state classes in this chunk are:

- configuration and capability exposure state, such as command/status bits, BAR sizing controls, PCIe capabilities, PASID/ATS/PRI/ACS enables, and strap-derived function capability bits;
- power-management state, including BACO mode, power-good fields, BCLK/DRAM/analog isolation controls, PCIe PM/ASPM-related fields, OBFF, DPA, LTR, and RX/PLL power state overrides;
- link-training state, including link width/speed, LTSSM state history, equalization status, coefficients, lane disable/corruption fields, FTS controls, and PRBS counters;
- coherency state, including HDP and GARLIC flush request/done registers and range registers;
- diagnostic and handoff state, including BIF/BIOS/PCIE/PCIEP scratch registers, header logs, TLP prefix logs, PRBS error counters, performance counters, and debug bus selectors.

Because these are raw masks, a wrong constant can silently write a neighboring bit and leave persistent hardware in a bad state. The most sensitive fields are those that reset blocks, power down lanes or clocks, mask/unmask PCIe errors, disable link logic, override PHY calibration, or change capability exposure.

## Dependencies And Integration Points

Direct dependencies are limited to the C preprocessor and the generated address header for the same ASIC generation:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_4_1_d.h`

Observed consumers and adjacent integration points include:

- `drivers/gpu/drm/amd/amdgpu/cik.c`, which includes this header and uses `PCIE_LC_SPEED_CNTL` fields for PCIe speed reporting;
- `drivers/gpu/drm/amd/amdgpu/cik_ih.c`, `cik_sdma.c`, `gmc_v7_0.c`, and `gfx_v7_0.c`, which include the BIF 4.1 mask header for CIK-era register programming;
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/ci_baco.c`, which includes this header and uses `BACO_CNTL__BACO_MODE_MASK` in BACO command-table wait operations;
- other BACO implementations in the tree that use same-named `BACO_CNTL` masks across related BIF/NBIO generations, making generation-specific values important;
- legacy and newer power-management code that uses the same `PCIE_LC_LINK_WIDTH_CNTL` and `PCIE_LC_SPEED_CNTL` naming pattern with generation-specific masks and shifts.

This chunk also mirrors standard PCI/PCIe capability layouts. Linux PCI core code owns generic enumeration and policy, while AMDGPU-specific low-level code uses these constants when it needs direct register access, hardware workarounds, debug state, ASIC-specific power sequencing, or link-status extraction outside generic PCI helpers.

## Risks And Edge Cases

The core risk is silent hardware misprogramming. These macros have no type safety: the compiler cannot tell whether a field mask belongs to the register being read, whether the matching shift was used, or whether a value exceeds the field width.

Mask/shift synchronization matters. The range has one incomplete pair at the chunk boundary: `PB0_RX_LANE5_CTRL_REG0__RX_BACKUP_5_MASK` is present on line 4515 while its `__SHIFT` is line 4516 outside this work item. The final file-level analysis should not report this as a file defect unless the complete file still lacks the pair.

Generation mixing is a concrete hazard. Same-named fields exist in BIF 3.0, BIF 4.1, BIF 5.x, NBIO, and PCIE headers, but masks and shifts differ for some generations. For example, `PCIE_LC_SPEED_CNTL__LC_CURRENT_DATA_RATE_MASK` is `0x6000` in this BIF 4.1 header, while later SMU/PCIE paths in the tree define other masks such as `0xE0` or `0xC000` for different IP blocks. Including the wrong generation header can compile cleanly and report the wrong link speed.

Several fields are operationally dangerous if written incorrectly:

- `BACO_CNTL` and related isolation/power-good fields can break power transitions or leave the GPU inaccessible.
- `PCIE_LC_SPEED_CNTL`, `PCIE_LC_LINK_WIDTH_CNTL`, `PCIE_LC_LANE_CNTL`, and equalization fields can destabilize link training or width/speed negotiation.
- `PCIE_ERR_CNTL`, AER masks/severity/status fields, and interrupt masks can hide or misclassify real PCIe faults.
- `PCIE_RX_CNTL`, `PCIE_TX_CNTL`, and flow-control/credit fields can alter packet ordering, completion handling, or credit behavior.
- PB0 PLL/RX/strap/DFT overrides can interfere with PHY calibration, lane power, CDR, equalization, and lab-only test paths.

Generated names with repeated `MASK` tokens and unusual suffixes are easy to mishandle in manual searches or scripts. Validation tooling should parse the actual suffix pattern instead of assuming every field base is human-clean.

Lane-indexed definitions are repetitive and prone to off-by-one mistakes in caller code. The assigned range includes RX lane 0-4 complete and starts lane 5; later chunks must complete lane 5 and the remaining lane families.

## Test Signals

Useful validation is mostly compile, static consistency, and hardware behavior coverage:

- Build CIK-era AMDGPU translation units that include this header, especially `cik.c`, `cik_ih.c`, `cik_sdma.c`, `gmc_v7_0.c`, `gfx_v7_0.c`, and `ci_baco.c`.
- Static checks that every `_MASK` has a matching `__SHIFT` in the complete generated file. For this chunk alone, allow the single line-boundary exception at `PB0_RX_LANE5_CTRL_REG0__RX_BACKUP_5_MASK`.
- Cross-check register prefixes against `bif_4_1_d.h` so field macro families map to address macros for the same register names.
- Exercise PCIe link reporting on CIK hardware and verify extracted link speed and width from `PCIE_LC_SPEED_CNTL` and `PCIE_LC_LINK_WIDTH_CNTL` match PCI core/lspci-observed values.
- Run BACO entry/exit and resume tests on supported ASICs, checking `BACO_CNTL__BACO_MODE_MASK`, power-good fields, isolation controls, and recovery after wake.
- Validate HDP and GARLIC flush paths with GPU workloads that require CPU/GPU coherency, including CP and SDMA activity.
- Exercise PCIe AER/error paths where possible: corrected/nonfatal/fatal error interrupt enables, status clearing, header log capture, and severity/mask programming.
- Cover ATS/PASID/PRI/IOMMU-related paths when supported by the platform, since those fields affect address translation and fault reporting.
- Run suspend/resume, FLR, hot reset, speed-change, ASPM/L0s/L1, and link retraining tests to catch bad link-controller or power-management field values.
- Use lab or debug validation for PRBS, PB0 PLL/RX/DFT, and lane override fields, because these fields may compile and remain dormant in normal functional tests while still being critical for board bring-up and diagnostics.
