# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_4_1_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001479`: lines 1-4515, `Docs/researches/chunks/subset-b-001479_research.md`
- `subset-b-001480`: lines 4516-8504, `Docs/researches/chunks/subset-b-001480_research.md`
- `subset-b-001481`: lines 8505-10252, `Docs/researches/chunks/subset-b-001481_research.md`

## Chunk Research

### subset-b-001479: lines 1-4515

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

### subset-b-001480: lines 4516-8504

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_4_1_sh_mask.h

Chunk: `subset-b-001480`
Covered source range: lines 4516-8504 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_4_1_sh_mask.h`

## Purpose

This chunk is the middle section of AMD's generated BIF 4.1 register field mask header. It is not executable driver logic; it supplies preprocessor constants that identify bit masks and shift positions for fields inside BIF/PCIe physical bus interface registers.

The covered range is centered on the physical bus interface, or PB, register space:

- the tail of `PB0_RX_LANE*_CTRL_REG0` and `PB0_RX_LANE*_SCI_STAT_OVRD_REG0` definitions for RX lanes 5-15;
- all covered `PB0_TX_*` global and per-lane transmitter fields, including TX global control, lane skew, coefficient accept tables, global overrides, and TX lanes 0-15;
- a large `PB1_*` block covering global controls, SCI status overrides, straps, DFT/jitter injection, PLL controls/status overrides, RX global/lane controls, and TX global/per-lane fields;
- the beginning of the `PB0_PIF_*` block, including PIF scratch/debug/program timing controls, lane pairing, power-down controls, sequence controls, programmed delay fields, and the first part of per-lane PDNB override definitions.

The chunk begins in the middle of `PB0_RX_LANE5_CTRL_REG0`: the matching `PB0_RX_LANE5_CTRL_REG0__RX_BACKUP_5_MASK` is in the previous chunk, while this range starts at its shift constant. The chunk also ends in the middle of `PB0_PIF_PDNB_OVERRIDE_3`: later constants for lane 3 and lanes 4-15 are in the next chunk. The final file-level report must reconcile these boundaries.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or runtime APIs in this range. The interface is entirely macro constants.

The generated naming contract is:

- `<REGISTER>__<FIELD>_MASK` gives the 32-bit mask for a field;
- `<REGISTER>__<FIELD>__SHIFT` gives the right-shift count used to encode or decode that field;
- register prefixes match address macros in `bif_4_1_d.h`, such as `ixPB0_TX_GLB_CTRL_REG0`, `ixPB1_RX_LANE15_SCI_STAT_OVRD_REG0`, and `ixPB0_PIF_CNTL2`.

Important macro families in this range include:

- `PB0_RX_LANE5..15_CTRL_REG0`: per-lane RX backup/debug/test and power-sense override fields, including `RX_DBG_ANALOG_SEL_*`, `RX_TST_BSCAN_EN_*`, and `RX_CFG_OVR_PWRSF_*`.
- `PB0_RX_LANE5..15_SCI_STAT_OVRD_REG0`: per-lane RX SCI status override fields for RX power, electrical-idle detection enable, preset hint, figure-of-merit request/enable, and response mode.
- `PB0_TX_GLB_CTRL_REG0`: global transmitter delay, reset value, stagger, clock-gating, preset table bypass, coefficient rounding, LSx clock, and TX frontend power behavior.
- `PB0_TX_GLB_LANE_SKEW_CTRL`: lane-group enable fields for x1, x2, x4, x8, and x16 grouping. These fields describe how lanes are grouped for TX skew management across the physical link width.
- `PB0_TX_GLB_SCI_STAT_OVRD_REG0`: global TX SCI update ignore and status override controls across lane groups.
- `PB0_TX_GLB_COEFF_ACCEPT_TABLE_REG0..3`: coefficient acceptance tables for per-lane TX equalization/preset behavior. These are dense packed fields, with table slots encoded as repeated multi-bit fields.
- `PB0_TX_GLB_OVRD_REG0..4`: global TX override controls for driver data, transmit detect, reset, power, data enable, disable/valid signaling, coefficient command values, and post-cursor/pre-cursor coefficient fields.
- `PB0_TX_LANE0..15_CTRL_REG0`, `PB0_TX_LANE0..15_OVRD_REG0`, and `PB0_TX_LANE0..15_SCI_STAT_OVRD_REG0`: per-lane TX backup, debug, override, power, reset, enable, coefficient, de-emphasis, margin, and deemphasis-related fields.
- `PB1_GLB_CTRL_REG0..5`, `PB1_GLB_SCI_STAT_OVRD_REG0..4`, and `PB1_GLB_OVRD_REG0..2`: matching global control and override fields for physical bus interface instance 1.
- `PB1_STRAP_*`: strap-derived global, TX, RX, PLL, and pin configuration fields, including lane reversal, debug muxing, spread-spectrum, common-mode, and PLL mode settings.
- `PB1_DFT_*`: design-for-test and jitter injection control/status fields.
- `PB1_PLL_RO*` and `PB1_PLL_LC*`: ring-oscillator and LC PLL control, override, and SCI status fields, including PLL power, frequency mode, divider, bypass, lock, calibration, and test controls.
- `PB1_RX_GLB_*` and `PB1_RX_LANE0..15_*`: RX global and per-lane control/status/override fields for data enable, equalization, termination, electrical idle, offset calibration, power states, preset hints, and response modes.
- `PB1_TX_GLB_*` and `PB1_TX_LANE0..15_*`: the instance-1 counterpart to the PB0 TX global/per-lane transmitter fields.
- `PB0_PIF_*`: PIF scratch/debug fields, programmable timing values, lane-pairing controls, power-down policy for lanes 0-3, TX PHY status bits, sequence-control phase/lane-resume bits, serial per-lane disable bits, and early PDNB/RXEN/TXPWR/RXPWR override fields.

## Control Flow

The chunk has no runtime control flow. It is a sequence of `#define` constants inside the include guard established at the top of the header.

Runtime control flow appears in consumers that include this header and use the masks with AMDGPU register access helpers. Typical usage is:

1. read a 32-bit register through direct MMIO or indexed PCIE access, for example `RREG32_PCIE(ixPB0_PIF_PWRDOWN_0)`;
2. clear a field with the generated `_MASK`;
3. encode a new value by shifting with the generated `__SHIFT`;
4. write the register back with `WREG32_PCIE`, `WREG32`, or command-table read/modify/write helpers;
5. optionally poll a status bit or field until hardware reports the expected state.

Concrete tree integration includes `amdgpu/cik.c`, which manipulates PIF power-down fields around PCIe link behavior. For example, it reads `ixPB0_PIF_PWRDOWN_0` and `ixPB0_PIF_PWRDOWN_1`, clears `PB0_PIF_PWRDOWN_*__PLL_POWER_STATE_IN_OFF_*_MASK` and `PB0_PIF_PWRDOWN_*__PLL_POWER_STATE_IN_TXS2_*_MASK`, then writes values shifted by the matching `__SHIFT` constants. Other CIK files include this header for BIF 4.1 register definitions used during interrupt setup, GMC setup, SDMA setup, graphics setup, BACO power management, and SMU/PowerPlay initialization.

The TX/RX/PLL/PIF constants in this chunk are meant for low-level link bring-up and service flows: lane power sequencing, L0s/L1/L2 behavior, speed changes, PLL ramp timing, electrical idle handling, link-width grouping, coefficient updates, and per-lane override/debug paths. The macros do not enforce sequencing; callers must follow ASIC programming requirements.

## State And Persistence Behavior

The header itself is stateless and persistent only as compiled constants. It does not allocate memory, keep state, perform I/O, or persist data.

The fields described by these constants map to persistent hardware register state in the GPU's BIF/PCIe block. Writes made through these masks can remain active until changed by driver code, firmware, link retraining, hot reset, function reset, BACO transition, suspend/resume, or full ASIC reset.

State categories represented in this range include:

- per-lane RX and TX power/enable/reset/status override state;
- PLL power, lock, divider, and calibration state;
- PIF sequence, lane pairing, lane disable, power-down, and programmable delay state;
- strap-derived configuration state copied from hardware straps or firmware-visible settings;
- debug/test state, including analog debug selection, boundary scan, DFT jitter injection, and override controls;
- scratch/debug fields such as `PB0_PIF_SCRATCH`, which can be used for diagnostics or firmware/driver coordination depending on platform conventions outside this header.

Incorrect writes to these fields can leave the PCIe link in a degraded or unusable state until reset. Because the macros are just constants, they do not record ownership, restore original values, or distinguish safe status fields from disruptive override fields.

## Dependencies And Integration Points

The direct dependency is the C preprocessor. The practical dependency is the matching BIF 4.1 address header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_4_1_d.h`

That address header defines the corresponding `ixPB0_*`, `ixPB1_*`, and `mm*` register addresses. In the covered range, examples include `ixPB0_TX_GLB_CTRL_REG0` at `0x1208000`, `ixPB1_TX_GLB_CTRL_REG0` at `0x2208000`, `ixPB0_PIF_CNTL2` at `0x1100014`, and `ixPB0_PIF_PDNB_OVERRIDE_*` addresses starting at `0x1100020`.

Known consumers in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik_sdma.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik_ih.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v7_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v7_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/ci_baco.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/ci_smumgr.c`

The main integration pattern is inclusion alongside other generated ASIC register headers and use through AMDGPU helper macros such as `RREG32`, `WREG32`, `RREG32_PCIE`, `WREG32_PCIE`, `REG_GET_FIELD`, and `REG_SET_FIELD`. PowerPlay BACO tables use the same generated mask/shift style for read/modify/write and wait-for command entries, although the specific BACO fields are outside this chunk.

This header is generation-specific. Same-named PB/PIF/PLL/RX/TX fields exist in adjacent BIF generations, but masks, semantic details, and addresses can differ. Consumers must include the BIF 4.1 header only for ASICs using the BIF 4.1 register layout.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. The compiler cannot verify that a `PB0` mask is used with a `PB0` address, that a `PB1` mask is used with `PB1`, or that a field value fits in the mask before shifting.

Mask/shift pairs must remain synchronized. A stale mask with a new shift, or a field copied from another generation, can update the wrong bits while producing valid C. This is especially risky for packed lane group fields, TX coefficient tables, PLL power/frequency fields, PIF programmable delays, and per-lane power overrides.

The chunk boundaries split two field families. Line 4516 starts with a `__SHIFT` whose matching `_MASK` is in chunk `subset-b-001479`. Line 8504 ends before most of `PB0_PIF_PDNB_OVERRIDE_3` and all later PDNB override lanes, which are expected in chunk `subset-b-001481`. Any automated validation at chunk granularity must tolerate these incomplete pairs at the boundaries while the final file-level merge should validate the full header.

Many constants are replicated across 16 lanes and across PB0/PB1 instances. Off-by-one lane selection, lexicographic confusion around lanes 10-15, or mixing PB0 and PB1 prefixes can pass review and builds but target the wrong physical lane.

Several fields are disruptive: PIF lane disable, sequence control, PLL power overrides, TX/RX power-state overrides, TX/RX enable/reset overrides, boundary scan/test enables, and DFT/jitter injection. Driver changes using these fields should be reviewed as hardware sequencing changes, not as ordinary bit cleanup.

Some fields describe status or strap-derived values while nearby fields are override enables or override values. Updating status-like macros is safe only as constants, but runtime writes to similarly named registers may not be safe. Callers need register-spec knowledge to distinguish read-only status from writable override paths.

The constants are untyped. Callers should use unsigned 32-bit arithmetic for field assembly and avoid relying on signed promotion, especially for high-bit masks such as lane 15 resume or PLL override values near bit 31.

## Test Signals

Useful validation signals include:

- build coverage for CIK-era AMDGPU and PowerPlay translation units that include `bif_4_1_sh_mask.h`;
- generated-header consistency checks that every `_MASK` has a matching `__SHIFT` across the complete file, with known chunk-boundary exceptions resolved after merge;
- duplicate-definition checks that no macro name is redefined with a different value;
- consistency checks against `bif_4_1_d.h`, verifying that register prefixes in field macros have matching address macros;
- static review of PB0/PB1 use sites to ensure instance prefixes match the addressed register;
- PCIe link tests on supported CIK hardware, including boot, link training, Gen2/Gen3 speed changes, link-width negotiation, ASPM/L0s/L1 transitions, suspend/resume, hot reset, and driver reset;
- BACO and low-power transition tests, because this header is included by CIK BACO/PowerPlay code and adjacent BIF fields can affect resume and link recovery;
- controlled readback tests for representative PIF power-down fields, PIF programmed delay fields, TX global control fields, and RX/TX lane status fields after known-safe writes;
- hardware-lab validation for per-lane TX coefficient/equalization and RX electrical-idle/preset-hint fields, because lane-indexed values can compile cleanly while degrading signal integrity;
- negative testing around invalid or out-of-range field values in call sites, ensuring callers mask and shift values rather than ORing raw constants into registers.

### subset-b-001481: lines 8505-10252

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_4_1_sh_mask.h

Chunk: `subset-b-001481`
Covered source range: lines 8505-10252 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_4_1_sh_mask.h`

## Purpose

This chunk is the final portion of AMD's generated BIF 4.1 register field mask header. It is not executable driver logic; it supplies C preprocessor constants for extracting and updating bitfields in BIF/PIF/RFE registers on ASICs that use the BIF 4.1 register layout.

The header pairs with `bif_4_1_d.h`, which defines the corresponding register addresses. In this chunk the paired address macros include indexed PIF PHY registers such as `ixPB0_PIF_PDNB_OVERRIDE_*`, `ixPB1_PIF_CNTL`, `ixPB1_PIF_SEQ_STATUS_*`, and MMIO registers such as `mmBIF_RFE_SOFTRST_CNTL`, `mmBIF_IMPCTL_RXCNTL`, `mmBIF_RESET_EN`, and `mmBIF_RESET_CNTL`.

The range starts in the middle of the `PB0_PIF_PDNB_OVERRIDE_3` field family, completes the remaining PB0 lane powerdown override and sequence-status definitions, defines the PB1 PIF control/status/powerdown/override families, and ends with BIF RFE, powerdown, impedance calibration, clock, link counter, reset, TX clock switch, BACO, and access-mode field definitions. The final line closes the `BIF_4_1_SH_MASK_H` include guard.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or runtime objects in this chunk. The API surface is entirely generated macro constants:

- `<REGISTER>__<FIELD>_MASK` isolates or clears a field in a 32-bit register value.
- `<REGISTER>__<FIELD>__SHIFT` gives the bit position used when packing or unpacking a field.
- `PB0_*` and `PB1_*` prefixes distinguish the two physical bus interface instances.
- Register names align with address macros in `bif_4_1_d.h`, while this file supplies the field-level masks and shifts.

Major register families in this chunk:

- `PB0_PIF_PDNB_OVERRIDE_3` through `PB0_PIF_PDNB_OVERRIDE_15`: per-lane TX/RX powerdown, RX enable, TX power, and RX power override enable/value fields for PB0 lanes. The chunk begins after the first `TX_PDNB_OVERRIDE_EN_3` pair, so `PB0_PIF_PDNB_OVERRIDE_3` is incomplete in this work item.
- `PB0_PIF_SEQ_STATUS_0` through `PB0_PIF_SEQ_STATUS_15`: per-lane sequence status bits for calibration, RX detect, L1/L0s/L0 entry/exit, speed change, and 3-bit sequence phase.
- `PB1_PIF_SCRATCH`, `PB1_PIF_HW_DEBUG`, and `PB1_PIF_PRG0` through `PB1_PIF_PRG7`: scratch/debug bits and programmable timing fields for RX detect sampling, PLL ramp-up, service step delays, speed-change delays, and LS2 exit timing.
- `PB1_PIF_CNTL` and `PB1_PIF_CNTL2`: PIF-level controls for serial configuration, FIFO reset modes, PHY command modes, electrical idle detection, PLL binding, calibration behavior, LS2 exit timing, RX enable gating, RX detect overrides for lanes 0-15, staggering, PLL1 always-on, and long speed-change delays.
- `PB1_PIF_PAIRING`: lane-pairing and width grouping fields for x2, x4, x8, x16, and multi-PIF configurations.
- `PB1_PIF_PWRDOWN_0` through `PB1_PIF_PWRDOWN_3`: per-group TX/RX/PLL power states, TX 2.5 clock gating, PLL ramp-up time, and PLL power override fields.
- `PB1_PIF_TXPHYSTATUS`, `PB1_PIF_SC_CTL`, and `PB1_PIF_SC_CTL2`: per-lane TX PHY status, sequence-control phase/resume bits, and serial configuration per-lane disable bits.
- `PB1_PIF_PDNB_OVERRIDE_0` through `PB1_PIF_PDNB_OVERRIDE_15` and `PB1_PIF_SEQ_STATUS_0` through `PB1_PIF_SEQ_STATUS_15`: PB1 equivalents of the lane power override and sequence-status fields.
- `BIF_RFE_*`: register front-end snoop, warm reset, soft reset, impedance reset, client/master reset trigger, master command status, timeout status, and MM-to-config controls.
- `BIF_PWDN_COMMAND` and `BIF_PWDN_STATUS`: powerdown command/status bits for BU, RWREG/RFEWDBIF, and BX blocks.
- `BIF_CC_RFE_IMP_OVERRIDECNTL`, `BIF_IMPCTL_SMPLCNTL`, `BIF_IMPCTL_RXCNTL`, `BIF_IMPCTL_TXCNTL_pd`, `BIF_IMPCTL_TXCNTL_pu`, and `BIF_IMPCTL_CONTINUOUS_CALIBRATION_PERIOD`: impedance override, sampling, RX/TX adjustment, lock/readback, comparator ambiguity, calibration done, and continuous calibration period fields.
- `BIF_CLOCKS_BITS`, `BIF_LNCNT_RESET`, `LNCNT_CONTROL`, `NEW_REFCLKB_TIMER`, `NEW_REFCLKB_TIMER_1`, `BIF_CLK_PDWN_DELAY_TIMER`, and `BIF_PIF_TXCLK_SWITCH_TIMER`: reference-clock, link-counter, PHY PLL powerdown, clock powerdown delay, and PLL switch timer fields.
- `BIF_RESET_EN` and `BIF_RESET_CNTL`: reset source enables, pulse widths, delay selectors, PIF reset/strap controls, BIF core reset, function-level reset enables, reset-done, link-train, strap-valid, and warm-reset recapture controls.
- `BIF_BACO_MSIC` and `BIF_RFE_CNTL_MISC`: BACO clock/link reset selection and RFE access-mode adaptation for PIF0, PIF1, power registers, and PCIe core.

## Control Flow

The chunk has no runtime control flow. The only compile-time structure is the closing `#endif` for the file include guard.

Runtime control flow appears in callers that use these constants in normal register read/modify/write sequences. A typical pattern is:

1. read a BIF or PIF register with an MMIO or indexed-register helper;
2. clear a field with `value &= ~REGISTER__FIELD_MASK`;
3. optionally set a new value with `value |= encoded << REGISTER__FIELD__SHIFT`;
4. write the register back;
5. poll a status field until it reflects the requested hardware transition.

The source tree shows BIF 4.1 definitions included by CIK-era amdgpu and PowerPlay code, including `amdgpu/cik.c`, `amdgpu/cik_ih.c`, `amdgpu/cik_sdma.c`, `amdgpu/gmc_v7_0.c`, `amdgpu/gfx_v7_0.c`, `pm/powerplay/hwmgr/ci_baco.c`, and `pm/powerplay/smumgr/ci_smumgr.c`. The same naming pattern is used by code that adjusts PIF power and timing fields; for example, related SI/CIK paths clear `PB*_PIF_PWRDOWN_*__PLL_RAMP_UP_TIME_*_MASK` and update `PB*_PIF_CNTL__LS2_EXIT_TIME__SHIFT` through PIF PHY access helpers.

## State And Persistence Behavior

This header has no mutable software state and performs no persistence itself. Its values are compiled into translation units that include it.

The affected state is hardware register state. Writes made with these masks can alter PCIe/BIF behavior until the register is changed again, the GPU is reset, the PCIe link is retrained, BACO or suspend/resume changes the power island state, or firmware/hardware reinitializes the block. This is especially relevant for:

- lane powerdown and RX/TX enable override fields, which can force per-lane electrical behavior;
- PIF sequence-control and status fields, which reflect or influence link training and low-power transitions;
- RFE soft/warm reset and master/client reset triggers, which can reset internal register-front-end clients or masters;
- BIF powerdown command/status fields, which coordinate block-level power gating;
- impedance calibration controls, which tune RX and TX electrical impedance and expose lock/readback status;
- reset enable/control fields, which determine how hot reset, link disable/down reset, driver reset, FLR, PIF reset, strap valid, and BIF core reset propagate.

Scratch and status fields may be observed across driver/firmware handoff or diagnostics depending on hardware retention rules, but this header does not define those rules.

## Dependencies And Integration Points

The direct dependency is the C preprocessor. The constants are meaningful only when used with the matching BIF 4.1 register address definitions in:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_4_1_d.h`
- adjacent generation-specific headers only when a caller intentionally targets that generation's register layout

Important address pairings from `bif_4_1_d.h` include:

- `ixPB0_PIF_PDNB_OVERRIDE_3` through `ixPB0_PIF_PDNB_OVERRIDE_15` and `ixPB0_PIF_SEQ_STATUS_0` through `ixPB0_PIF_SEQ_STATUS_15`;
- `ixPB1_PIF_SCRATCH`, `ixPB1_PIF_CNTL`, `ixPB1_PIF_CNTL2`, `ixPB1_PIF_PAIRING`, `ixPB1_PIF_PWRDOWN_*`, `ixPB1_PIF_SC_CTL*`, `ixPB1_PIF_PDNB_OVERRIDE_*`, and `ixPB1_PIF_SEQ_STATUS_*`;
- `mmBIF_RFE_SNOOP_REG`, `mmBIF_RFE_WARMRST_CNTL`, `mmBIF_RFE_SOFTRST_CNTL`, `mmBIF_PWDN_COMMAND`, `mmBIF_PWDN_STATUS`, `mmBIF_RFE_MMCFG_CNTL`;
- `mmBIF_IMPCTL_SMPLCNTL`, `mmBIF_IMPCTL_RXCNTL`, `mmBIF_IMPCTL_TXCNTL_pd`, `mmBIF_IMPCTL_TXCNTL_pu`, and `mmBIF_IMPCTL_CONTINUOUS_CALIBRATION_PERIOD`;
- `mmBIF_RESET_EN`, `mmBIF_RESET_CNTL`, `mmBIF_BACO_MSIC`, `mmBIF_CLOCKS_BITS`, `mmNEW_REFCLKB_TIMER`, and related clock/link-counter registers.

The included users are low-level GPU initialization, interrupt, memory-controller, graphics, SDMA, display, ATOM BIOS, BACO, and SMU management code. These consumers typically access registers through AMDGPU helper macros rather than through typed wrappers, so the register prefix and field macro names are the primary contract.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. These are untyped numeric macros; the compiler cannot prove that `PB1_PIF_CNTL__LS2_EXIT_TIME_MASK` is used only with `ixPB1_PIF_CNTL`, or that a PB0 field is not accidentally applied to a PB1 register.

The assigned range starts in the middle of `PB0_PIF_PDNB_OVERRIDE_3`. The first pair for `TX_PDNB_OVERRIDE_EN_3` is outside the work item, while the rest of the lane-3 override value and RX/TX power fields are inside it. Final file-level analysis must merge this with the preceding chunk before treating PB0 lane 3 as complete.

Lane-indexed definitions are repetitive and easy to misuse. PB0/PB1, lane 0-15, and grouped powerdown registers all compile cleanly even if a caller selects the wrong lane, wrong PIF instance, or wrong group register.

Many fields control disruptive link and device behavior. Bad writes to PIF powerdown overrides, RX detect overrides, sequence-control resume bits, PLL timers, RFE reset triggers, BIF powerdown commands, impedance force/reset fields, or `BIF_RESET_EN` can hang PCIe access, break link retraining, lose MMIO/config reachability, or require a full GPU reset.

Mask/shift pairs must remain synchronized. Errors are particularly dangerous for multi-bit fields such as lane pairing, power states, ramp-up timers, reset pulse widths, function reset delay selectors, impedance thresholds/readbacks, and RFE timeout timers.

Generation drift is a real concern. BIF 5.0 contains closely related names but not identical fields, such as additional RFE master/powerdown fields in some places. Code should not mix BIF 4.1 masks with another generation's `*_d.h` address header unless the compatibility is explicitly known.

## Test Signals

Useful validation signals are mostly build, static consistency, and hardware behavior checks:

- Compile all translation units that include `bif_4_1_sh_mask.h`, especially CIK amdgpu, GMC/GFX/SDMA, PowerPlay BACO, and SMU manager paths.
- Run a generated-header consistency check that every `_MASK` has a matching `__SHIFT` and that both use the same register/field prefix. This range has an intentional boundary exception for the start of `PB0_PIF_PDNB_OVERRIDE_3`.
- Cross-check field register prefixes against `bif_4_1_d.h` address macros so every `PB1_PIF_*` and `BIF_*` field family maps to a corresponding address definition.
- Exercise PCIe link bring-up, lane width changes, speed changes, ASPM/L0s/L1/LS2 transitions, and suspend/resume on BIF 4.1 hardware to cover PIF control, sequence status, powerdown, PLL timer, and reset fields.
- Validate BACO entry/exit and clock/reference-clock behavior where `BIF_BACO_MSIC`, `BIF_CLOCKS_BITS`, `NEW_REFCLKB_TIMER*`, and reset controls may be involved.
- Test FLR, hot reset, link-disable reset, link-down reset, driver reset, and BIF core reset paths to catch incorrect `BIF_RESET_EN` or `BIF_RESET_CNTL` masks.
- Use controlled lab or bring-up tests for impedance calibration fields: force/suspend/reset behavior, `RX_IMP_LOCKED`, `TX_IMP_LOCKED_*`, readback selectors, comparator ambiguity, and `CAL_DONE`.
- For any regenerated version of this header, compare macro names and values against the authoritative register database and perform representative readback/writeback tests on single-bit and multi-bit fields.
