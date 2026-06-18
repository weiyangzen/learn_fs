# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002995`: lines 1-2944, `Docs/researches/chunks/subset-b-002995_research.md`
- `subset-b-002996`: lines 2945-5829, `Docs/researches/chunks/subset-b-002996_research.md`
- `subset-b-002997`: lines 5830-8638, `Docs/researches/chunks/subset-b-002997_research.md`
- `subset-b-002998`: lines 8639-11461, `Docs/researches/chunks/subset-b-002998_research.md`
- `subset-b-002999`: lines 11462-14269, `Docs/researches/chunks/subset-b-002999_research.md`
- `subset-b-003000`: lines 14270-17079, `Docs/researches/chunks/subset-b-003000_research.md`
- `subset-b-003001`: lines 17080-19894, `Docs/researches/chunks/subset-b-003001_research.md`
- `subset-b-003002`: lines 19895-22340, `Docs/researches/chunks/subset-b-003002_research.md`

## Chunk Research

### subset-b-002995: lines 1-2944

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h lines 1-2944

## Scope

This chunk is the opening 2,944 lines of the generated AMDGPU NBIO 6.1 default-value header. It contains the MIT license, the `_nbio_6_1_DEFAULT_HEADER` include guard, and 2,779 preprocessor `#define` constants that name reset/default values for NBIO 6.1 PCIe configuration space, NBIF/RCC registers, GDC/SYSHUB/SION registers, and a small tail of a second RCC downstream-port block. There are no C functions, structs, enums, variables, locks, allocations, loops, or executable statements in this range.

Although the repository root is a `ceph-client` mirror, this file is AMD DRM/AMDGPU ASIC register metadata. The chunk has no direct distributed-filesystem behavior.

## Purpose

`nbio_6_1_default.h` publishes generated reset/default values for the NBIO 6.1 hardware block. Runtime code can include it together with `nbio_6_1_offset.h`, `nbio_6_1_sh_mask.h`, and `nbio_6_1_smn.h` to compare, initialize, decode, or document NBIO register state. This chunk covers two main regions.

The first region, lines 25-2104, describes PCIe configuration-space defaults:

- `cfgPSWUSCFG0_*` defaults for the PSW upstream-switch configuration decoder, including standard PCI header fields, PCIe capability chain pointers, MSI/SSID, vendor-specific capabilities, VC, AER, secondary PCIe capability, ACS, multicast, LTR, ARI, L1 PM substate, and ESM defaults.
- `cfgBIF_CFG_DEV0_EPF0_0_*` and `cfgBIF_CFG_DEV0_EPF1_0_*` defaults for endpoint functions 0 and 1. These include base BARs, MSI/MSI-X, PCIe BAR capability, power budgeting, Dynamic Power Allocation, ACS, ATS, page-request, PASID, TPH requester, multicast, LTR, ARI, SR-IOV, and AMD GPUIOV vendor-specific mailbox and scheduling register defaults.
- `cfgBIF_CFG_DEV0_SWDS0_*` bridge/downstream-port defaults, including interrupt pin `1`, PCIe capability type `0x62`, link status `0x00002001`, AER masks, VC resource defaults, lane equalization defaults, and ACS defaults.
- `cfgBIF_CFG_DEV0_EPF0_VF0_0_*` through `cfgBIF_CFG_DEV0_EPF0_VF15_0_*` default values for 16 virtual functions. These repeat a compact VF endpoint profile: PCI header defaults, BAR defaults, MSI/MSI-X defaults, vendor-specific capability, AER, ATS, and ARI. Common nonzero defaults include interrupt line `0xff`, PCIe capability pointer `0xa000`, device capability `0x10000000`, device control `0x2810`, link capability `0x11c03`, MSI control `0x80`, AER severity `0x00440010`, correctable-error mask `0x2000`, ATS capability-list pointer `0x2c000000`, and ARI capability-list pointer `0x33000000`.

The second region, lines 2107-2944, describes NBIF, RCC, GDC, SYSHUB, SION, and additional SMN-named defaults:

- Indexed MMIO and PCIe aperture defaults such as `mmMM_INDEX_DEFAULT`, `mmMM_DATA_DEFAULT`, `mmPCIE_INDEX_DEFAULT`, and `mmPCIE_DATA_DEFAULT`.
- Scratch, BIOS scratch, interrupt, GFX MMIO register CAM, and remap defaults in the `SYSDEC` block.
- RCC strap, endpoint, downstream, PF/PF-VF, reset, peer register range, bus-number, XDMA, link, LTR, mailbox, and doorbell aperture defaults.
- BIF defaults for reset enables, clock request pad control, BACO exit timers, VDDGFX address windows, doorbell global apertures, HDP flush remap registers, ring-buffer registers, GPUIOV configuration sizes, and pad controls.
- GDC defaults for SDP port controls, SDMA/IH/MMSCH doorbell ranges, and MSIX vector table defaults.
- SYSHUB direct defaults for clock-domain controls, QoS controls, DMA cache-line controls, clock gating, timers, NIC400 function modifiers, and scratch values.
- SION credit, burst-target, and time-slot defaults for client groups CL0 through CL5, all zero in this chunk.
- GDC reset/RAS defaults, a second `smnBIF_CFG_DEV0_SWDS1_*` downstream-port default set, PF1 mirrored BIF/PF-VF defaults, shadow PCI configuration defaults, and the beginning of `smnRCC_DWN_DEV0_1_*` downstream-port defaults.

## Important APIs, Types, And Functions

There are no callable APIs or C data types here. The public interface is the macro namespace. The macro prefixes encode the access domain:

- `cfg*` names PCI configuration-space defaults for generated config decoders.
- `mm*` names MMIO register defaults used through SOC15 register-offset helpers.
- `smn*` names System Management Network register defaults or SMN-addressed aliases.

The direct in-tree users of this header are:

- `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, which includes `nbio_6_1_default.h` with the offset, shift/mask, and SMN headers for NBIO 6.1 runtime code. That file programs and reads registers such as `mmREMAP_HDP_MEM_FLUSH_CNTL`, `mmRCC_DEV0_EPF0_STRAP0`, `mmBIF_FB_EN`, `mmRCC_PF_0_0_RCC_CONFIG_MEMSIZE`, doorbell ranges, interrupt controls, and clock-gating fields through helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `WREG32_FIELD15`, `SOC15_REG_OFFSET`, and `REG_SET_FIELD`.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h`, which aggregates Vega10 ASIC register headers, including `nbio_6_1_default.h`, for power-management code.

Most macros in this exact chunk are not referenced directly by handwritten C code in the observed tree. They remain part of the generated ASIC register contract and may be used by generated tables, debugging, register-dump comparison, downstream code, or future initialization paths.

## Control Flow

This header has no local control flow. The effective runtime pattern is external:

1. An NBIO 6.1 consumer includes the default, offset, shift/mask, and SMN headers.
2. The consumer selects a register macro namespace appropriate to the access path: PCI config, MMIO, or SMN.
3. The consumer reads or writes hardware using AMDGPU access helpers and applies field masks from `nbio_6_1_sh_mask.h`.
4. Defaults from this file may be used as expected reset values, baseline values before `REG_SET_FIELD` updates, or documentation for hardware state after reset.

The actual ordering rules are in the consuming driver and hardware specification. For example, `nbio_v6_1.c` enables/disables FB access, remaps HDP flush registers, programs doorbell apertures and ranges, configures IH interrupt behavior, and toggles BIF clock gating. This default header only supplies constants and does not enforce any sequencing.

## State And Persistence Behavior

The chunk stores no software state and persists nothing to disk. It describes hardware-visible defaults. Persistence is governed by GPU reset domains, PCI config-space save/restore, firmware initialization, suspend/resume, function-level reset, hot reset, and explicit driver/firmware writes after reset.

The represented state includes PCIe capability-chain state, BAR defaults, MSI/MSI-X defaults, AER masks/severity, lane equalization defaults, ATS/PASID/ARI/SR-IOV capability defaults, GPUIOV mailbox/scheduler defaults, RCC and BIF reset controls, BACO timing defaults, VDDGFX address windows, doorbell apertures, HDP flush remap values, SYSHUB clock/QoS/cache-line defaults, GDC reset/RAS defaults, and SION arbitration/credit defaults. Many defaults are zero, but the nonzero values are meaningful hardware ABI values and should not be treated as filler.

## Dependencies And Integration Points

The direct companion files are:

- `nbio_6_1_offset.h`, which provides the register/config offsets for these names.
- `nbio_6_1_sh_mask.h`, which provides field shifts and masks used to interpret or update values.
- `nbio_6_1_smn.h`, which provides SMN-addressed register names used with PCIE/SMN access helpers.

Broader integration points include AMDGPU NBIO initialization, Vega10 power management, PCIe capability exposure, interrupt/MSI setup, HDP flush remapping for KFD/compute paths, doorbell aperture programming, SR-IOV/GPUIOV virtualization, IOMMU-facing ATS/PASID behavior, AER/RAS reporting, BACO and clock-gating power states, and suspend/resume restore paths.

## Risks And Edge Cases

- Generated default drift can compile cleanly while changing hardware behavior assumptions. A wrong nonzero default can mislead initialization, reset validation, register-dump comparison, or downstream diagnostics.
- Names overlap across access domains. For example, `cfg*`, `mm*`, and `smn*` variants may refer to related hardware concepts but are not interchangeable access paths.
- The assigned chunk ends mid-block at `smnRCC_DWN_DEV0_1_DN_PCIE_RX_CNTL2_DEFAULT`; the rest of that RCC downstream-port block is in the next chunk. The final per-file report should not treat line 2944 as a semantic file boundary.
- PCIe configuration defaults are security- and virtualization-sensitive. Incorrect defaults around ACS, ATS, PASID, ARI, SR-IOV, GPUIOV mailboxes, and VF BAR/MSI state can affect isolation, address translation, function routing, and guest/host boundaries.
- Doorbell and HDP flush defaults are performance and correctness sensitive. Bad doorbell aperture ranges or remap values can break queue submission, interrupts, and CPU/GPU coherency.
- Reset and power-management defaults such as `mmBX_RESET_EN_DEFAULT`, `mmRCC_RESET_EN_DEFAULT`, BACO timers, clock-gating controls, and SYSHUB QoS/cache-line defaults can cause intermittent failures that only appear after suspend/resume, BACO entry/exit, FLR, or heavy DMA traffic.
- Many macros are unused by current handwritten code, so compile-only validation may miss semantic drift. Hardware validation or generated-register database comparison is needed for confidence.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Build AMDGPU with Vega10/NBIO 6.1 support enabled. Include-guard damage, duplicate macros, missing macros, or syntax drift should fail compilation in `nbio_v6_1.c` or `vega10_inc.h` users.
- Compare the generated defaults against the authoritative NBIO 6.1 register database, especially all nonzero PCIe capability-chain, AER, VF, SR-IOV/GPUIOV, RCC, BIF, SYSHUB, GDC, and reset defaults.
- Boot affected AMD GPUs and check PCIe enumeration, capability traversal, BAR sizing, MSI/MSI-X setup, link speed/state reporting, and AER masks.
- Exercise SR-IOV or VF paths where available, validating VF config-space defaults, GPUIOV mailbox behavior, ATS/PASID/ARI visibility, and guest isolation.
- Exercise KFD/compute and graphics queue submission to validate doorbell ranges, HDP flush remap registers, interrupt delivery, and BIF transaction-pending behavior.
- Run suspend/resume, BACO entry/exit, FLR, and GPU reset tests to catch persistence and reset-domain mistakes.
- Check power-management and clock-gating paths for regressions in BIF light sleep, medium-grain clock gating, SYSHUB clock gating, DPA/LTR behavior, and BACO timers.

## Chunk-Specific Notes For Merge

This is the first chunk of `nbio_6_1_default.h`. Merge it with later chunks before producing the final per-file research document. Preserve that this slice covers the include guard, PCIe config defaults for PSW/EPF0/EPF1/SWDS0/VF0-VF15, first-instance NBIF/RCC/GDC/SYSHUB/SION defaults, mirrored `smn*` SWDS1 and PF1 defaults, shadow config defaults, and only the beginning of the `smnRCC_DWN_DEV0_1` downstream-port block.

### subset-b-002996: lines 2945-5829

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h lines 2945-5829

## Scope

This chunk is a generated AMDGPU NBIO 6.1 default-value header segment. It contains 2,792 `#define` constants across lines 2945-5829. There are no C functions, structs, enums, variables, allocations, locks, branches, or executable statements in this range.

The range begins near the end of the downstream RCC device-0 PCIe defaults and ends in the first part of the DWC E12MP PHY x4 lane-3 defaults. The source boundary is artificial: earlier RCC/downstream defaults are in the previous chunk, and the remainder of the lane-3 PHY defaults plus later NBIO reset values are in following chunks.

Although this path sits under a `ceph-client` source mirror, the content is Linux AMDGPU hardware metadata. It has no distributed-filesystem behavior.

## Purpose

`nbio_6_1_default.h` provides reset/default register values for the Vega/NBIO 6.1 register model. The companion generated headers provide the other halves of the register interface:

- `nbio_6_1_offset.h` maps register names to MMIO/config-space offsets.
- `nbio_6_1_sh_mask.h` maps register fields to shifts and masks.
- `nbio_6_1_smn.h` maps selected registers to SMN addresses.

This default header gives callers and diagnostic code a symbolic reset value for each generated register name, using the `<register>_DEFAULT` macro namespace. In this chunk, those defaults cover NBIF/RCC control blocks, PF and VF PCI configuration images, MSI-X table/PBA storage, PCIe wrapper/control registers, and DWC PCIe PHY lane tuning/status defaults.

## Address Blocks Covered

The chunk is organized by generated `// addressBlock:` comments:

- `nbio_nbif_rcc_dwnp_dev0_RCCPORTDEC`: downstream-port PCIe error, RX, link-speed, LC, strap, and LTR defaults.
- `nbio_nbif_rcc_strap_rcc_strap_internal`: RCC strap default for device 0 endpoint function 0.
- `nbio_nbif_bif_bx_pf_SUMDEC`: indexed summary register defaults, `SUM_INDEX` and `SUM_DATA`.
- `nbio_nbif_bif_misc_bif_misc_regblk`: NBIF/BIF scratch, interrupt line, outstanding VC allocation, misc controls, DMA attribute overrides, virtual-wire controls, clock-gating/light-sleep, SMN master endpoint controls, BME/THT/GSI/PCIEFUNC/SDP/perf counters, REGIF error control, select-ring, and GMI WRR defaults.
- `nbio_nbif_rcc_pfc_amdgfx_RCCPFCDEC` and `nbio_nbif_rcc_pfc_amdgfxaz_RCCPFCDEC`: PFC LTR, PME restore, sticky restore, and AUX power defaults for graphics functions.
- `nbio_nbif_bif_rst_bif_rst_regblk`: hard reset, RSMU soft reset, self reset, VPU reset, reset misc controls, PF/VF FLR, D3hot-to-D0, power, and D-state interrupt/status/mask/reset defaults.
- `nbio_nbif_bif_ras_bif_ras_regblk`: BIF RAS leaf, miscellaneous, IOHUB RAS IH, and virtual-wire defaults.
- `nbio_nbif_bif_cfg_dev0_epf0_bifcfgdecp` and `nbio_nbif_bif_cfg_dev0_epf1_bifcfgdecp`: default PCI/PCIe configuration-space images for physical functions EPF0 and EPF1.
- `nbio_nbif_bif_cfg_dev0_epf0_vf0_bifcfgdecp` through `vf15`: repeated default PCI/PCIe configuration-space images for sixteen SR-IOV virtual functions under device 0 function 0.
- `nbio_nbif_pciemsix_amdgfx_MSIXTDEC` and `nbio_nbif_pciemsix_amdgfx_MSIXPDEC`: MSI-X vector table and pending-bit-array defaults for the graphics function.
- `nbio_pcie_pswusp0_pciedir_p` and `nbio_pcie_pciedir`: PCIe wrapper/control/status defaults including straps, link controls, error/status, replay, indirect access, hot reset, and counter/control registers.
- `nbio_pipe_pcs_dwc_e12mp_phy_x4_ns0_dwc_e12mp_phy_x4_ns_UP16_dwc_e12mp_phy_x4_ns_UP16_mem_map`: start of DWC E12MP x4 PHY common/lane defaults, covering global reset/control, SRAM/CMN/PLL blocks, lane 0-2, and the first lane-3 ASIC override defaults.

## Important Macro Families

The NBIF/RCC and reset defaults establish the hardware baseline for low-level PCIe/NBIO behavior:

- `smnRCC_DWNP_DEV0_1_*_DEFAULT` values describe downstream-port error handling, link controls, strap-derived behavior, and endpoint LTR message state.
- `smnBIFC_*_DEFAULT`, `smnNBIF_*_DEFAULT`, `smnSMN_MST_*_DEFAULT`, `smnBME_*_DEFAULT`, and `smnBIF_SELFRING_*_DEFAULT` values describe internal NBIF control, master endpoint, virtual-wire, DMA-attribute, performance-counter, and select-ring defaults.
- `smnHARD_RST_CTRL_DEFAULT`, `smnRSMU_SOFT_RST_CTRL_DEFAULT`, `smnBIF_RST_MISC_CTRL*_DEFAULT`, `smnDEV0_PF*_FLR_RST_CTRL_DEFAULT`, `smnBIF_*_INTR_*_DEFAULT`, and `smnDEV0_PF*_D3HOTD0_RST_CTRL_DEFAULT` values define reset-domain and interrupt-mask defaults for PF FLR, VF FLR, D3hot-to-D0, power, and D-state events.
- `smnBIF_RAS_*_DEFAULT` values define default RAS control/reporting state for BIF/NBIO error handling.

The PF and VF config-space blocks repeat standard PCI/PCIe layout defaults:

- Conventional PCI header fields: vendor/device ID, command, status, revision, class-code bytes, cache-line size, latency, header, BIST, BARs, adapter/subsystem IDs, ROM BAR, capability pointer, interrupt line/pin, minimum grant, and maximum latency.
- Power-management and PCIe capability fields: PMI capability/status/control; PCIe capability list entries; device, link, slot, and second-generation device/link capability/control/status registers.
- MSI/MSI-X defaults: capability-list pointers, message control, message address/data, mask, pending, table, and PBA fields. The physical functions expose more full capability images than the VFs, but most default storage is zero until programmed.
- Vendor-specific, VC, device serial number, Advanced Error Reporting, ARI, and Readiness Time Reporting extended capability defaults. Repeated values such as `0x11000000`, `0x14000000`, `0x15000000`, `0x20020000`, `0x2c000000`, and `0x33000000` encode extended-capability headers or next pointers in the generated reset image.

The SR-IOV VF blocks are a major part of this chunk. `smnBIF_CFG_DEV0_EPF0_VF<n>_1_*_DEFAULT` appears for VF0 through VF15, giving each VF a mostly repeated PCIe endpoint config template. Common non-zero values include interrupt line `0x000000ff`, PCIe capability list `0x0000a000`, PCIe capability `0x00000002`, device capability `0x10000000`, device control `0x00002810`, link capability `0x00011c03`, link status `0x00000001`, link capability 2 `0x0000000e`, link control 2 `0x00000003`, MSI capability list `0x0000c000`, and MSI message control `0x00000080`.

The MSI-X table/PBA block defines per-vector reset state:

- `smnPCIEMSIX_VECT<n>_ADDR_LO_DEFAULT`, `ADDR_HI_DEFAULT`, `MSG_DATA_DEFAULT`, and `CONTROL_DEFAULT` repeat for 32 vectors, all zero in this slice.
- `smnPCIEMSIX_PBA_DEFAULT` is also zero, meaning no pending MSI-X bits in the generated reset image.

The PCIe wrapper/control block includes link and PHY-facing defaults:

- `smnPSWUSP0_PCIE_LC_CNTL*_DEFAULT`, `smnPSWUSP0_PCIEP_STRAP_*_DEFAULT`, and `smnPCIE_LC_*_DEFAULT` values define link-control, lane, training, equalization, link-state, and strap baselines.
- `smnPCIE_CNTL*_DEFAULT`, `smnPCIE_CONFIG_CNTL_DEFAULT`, `smnPCIE_TX_REQUESTER_ID_DEFAULT`, `smnPCIE_PRBS_*_DEFAULT`, `smnPCIE_SCRATCH_DEFAULT`, and `smnPCIE_PERF_*_DEFAULT` cover wrapper-level control, request IDs, test/PRBS, scratch, error injection, performance counting, indirect-index/data, and hot-reset handling.
- `smnCPM_CONTROL_DEFAULT`, `smnSMU_CLKREQ_*_DEFAULT`, `smnPCIEP_HW_DEBUG_DEFAULT`, `smnLNCNT_*_DEFAULT`, `smnLNC_BW_CHANGE_CNTL_DEFAULT`, `smnSWRST_*_DEFAULT`, and `smnRSMU_*_DEFAULT` establish power-management, debug, lane-count, clock-request, software-reset, and RSMU handshake defaults.

The DWC E12MP PHY block starts a dense set of low-level analog/digital defaults:

- Common/global defaults include `smnDWC_E12MP_PHY_X4_NS_X4_0_GLBL_*`, `CMN_*`, `SRAM_*`, `MPLLA_*`, `MPLLB_*`, `VCOCAL_*`, `SUP_*`, `RTERM_*`, `PCS_*`, and `RAWLANEAON_*`.
- Lane blocks define ASIC override inputs/outputs, TX and RX power-state tables, power-up timing, LBERT controls, RX VCO calibration, align masks, CDR controls/status, DPLL frequency/bounds, RX adaptation configuration/status, slicer/DFE offsets, RX statistic match/control/counters, digital-to-analog override outputs, and analog TX/RX control defaults.
- Lane 0, lane 1, and lane 2 are substantially complete in this chunk; lane 3 begins at `smnDWC_E12MP_PHY_X4_NS_X4_0_LANE3_DIG_ASIC_*_DEFAULT` and continues in the next chunk.

Most values in this slice are zero: 2,106 of 2,792 defaults are `0x00000000`. The non-zero defaults are therefore the highest-risk values during regeneration or manual comparison because they encode actual hardware reset policy.

## APIs, Types, And Functions

There are no runtime APIs, C types, or functions in this chunk. The exported interface is the macro namespace:

- Macro names use an SMN-oriented prefix such as `smnBIF_CFG_DEV0_EPF0_1_DEVICE_CNTL_DEFAULT`.
- Values are untyped preprocessor integer literals, typically 32-bit hexadecimal constants.
- Names must stay synchronized with the generated offset, shift/mask, and SMN-address headers. A default macro without the matching register offset or field metadata is hard to use safely.

Consumers include this header directly or indirectly and then use the constants as symbolic reset/default values when comparing, initializing, debugging, or preserving register state. The header does not describe access width, read/write permission, write-one-to-clear behavior, volatility, privilege, timing, or side effects.

## Control Flow

There is no local control flow. Runtime flow is external to this file:

1. AMDGPU or power-management code includes the NBIO 6.1 generated header set.
2. A call site chooses a register via an offset/SMN macro, often using helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `SOC15_REG_OFFSET`, `REG_GET_FIELD`, or `REG_SET_FIELD`.
3. The default macro can be used as a known reset baseline, comparison value, or initial image for a register/config-space table.
4. Hardware, firmware, BIOS straps, PCI enumeration, SR-IOV management, suspend/resume, or explicit driver writes may move the actual register away from this generated default.

Observed includers in this source tree are:

- `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, which includes `nbio_6_1_default.h` along with offset, shift/mask, and SMN headers for Vega/NBIO 6.1 operations such as HDP remapping, revision ID reads, memory-controller access, doorbell ranges, interrupt control, clock gating, light sleep, and PCIe link/power policy.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h`, which aggregates generated THM, MP, GC, and NBIO headers for Vega10 power-management code.

## State And Persistence Behavior

This header stores no software state. It names hardware reset/default state for NBIO, BIF, RCC, PCIe, MSI-X, and PHY registers. Persistence is controlled by hardware reset domains and by firmware/driver policy, not by the header.

The represented state includes:

- PCIe/NBIO control state: link controls, request IDs, replay behavior, counters, hot reset, error controls, straps, LTR, clock requests, power gating, and lane-count changes.
- PF/VF PCI configuration state: identity registers, command/status, BARs, capability list pointers, MSI/MSI-X programming, PCIe device/link controls, AER registers, ARI controls, vendor-specific extended capabilities, and readiness-time reporting.
- Interrupt/reset state: FLR, D3hot-to-D0, power, D-state, reset status, and interrupt mask defaults.
- MSI-X storage: vector message address/data/control entries and pending-bit array.
- RAS state: BIF RAS control and IOHUB reporting defaults.
- PHY state: PLL, VCO calibration, TX/RX power states, power-up timings, CDR/DPLL, adaptation, slicer/DFE, LBERT, statistics, analog override, and calibration/status defaults.

Some represented registers are passive storage, but many are not. PCI command bits can enable memory access and bus mastering; FLR and reset controls can trigger reset behavior; link controls can retrain or change the PCIe link; MSI/MSI-X controls affect interrupt delivery; AER status/log registers may be sticky or write-one-to-clear; PHY override and calibration controls can affect signal integrity and link training. The default header does not encode those side-effect rules.

## Dependencies And Integration Points

The immediate dependencies are the generated NBIO 6.1 header family in the same directory:

- `nbio_6_1_offset.h` for offsets.
- `nbio_6_1_sh_mask.h` for bitfield packing/extraction.
- `nbio_6_1_smn.h` for SMN addresses.

The runtime integration is through AMDGPU SOC15/NBIO access code. `nbio_v6_1.c` includes the generated headers and uses NBIO register helpers for operations around doorbells, HDP flushing, interrupt setup, memory-controller access, PCIe clock gating/light sleep, LTR/ASPM policy, and link state. Power-management code reaches the same register namespace through `vega10_inc.h`.

The hardware integration points are broader than the direct textual references suggest:

- PCI and PCIe enumeration consume the PF/VF configuration-space image and capability defaults.
- SR-IOV depends on the repeated VF0-VF15 default templates being consistent with virtualization expectations.
- Interrupt setup depends on MSI/MSI-X defaults and later OS-programmed vector table values.
- Reset and recovery paths depend on FLR, D3hot-to-D0, hard reset, soft reset, and interrupt-mask defaults.
- RAS/error handling depends on BIF RAS and PCIe AER defaults.
- Link training, power management, and signal integrity depend on the wrapper and DWC PHY defaults.

## Risks And Edge Cases

- Generated-header skew is the main risk. If `_DEFAULT` names drift from `nbio_6_1_offset.h`, `nbio_6_1_sh_mask.h`, or `nbio_6_1_smn.h`, code may compare or initialize the wrong register.
- The chunk contains many repeated PF/VF PCI config templates. A one-line generation error can affect all VFs, while a single missing VF-specific exception can break only one virtual function and be hard to notice.
- Most values are zero, so non-zero defaults such as PCIe capability headers, link capability/control values, device control, MSI message control, reset controls, and PHY tuning constants deserve focused review after regeneration.
- Default values are not necessarily safe write values. Some status bits are hardware-updated, sticky, write-one-to-clear, read-only, strap-derived, or firmware-owned.
- PCI config defaults may be overwritten by BIOS, firmware, host PCI enumeration, SR-IOV enablement, hypervisor policy, or Linux PCI core programming before AMDGPU reads them.
- PHY defaults are tightly coupled to silicon characterization. Changing constants such as TX/RX power-state tables, CDR/DPLL controls, adaptation settings, VCO calibration timing, or analog termination can cause link instability that ordinary compile tests will not catch.
- Reset/default behavior can differ by reset source. Hard reset, soft reset, FLR, D3hot-to-D0, suspend/resume, and GPU reset may not all restore the same subset of registers to these values.
- The file exposes raw integer macros with no type checking. A default for an SMN register can accidentally be used with a config-space offset or a different ASIC revision if names are copied manually.
- This chunk ends mid-`LANE3`; any per-lane comparison must include the following chunk before drawing conclusions about lane symmetry.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Header generation consistency checks: every `_DEFAULT` macro in this chunk should have the expected matching register in the generated NBIO 6.1 offset/SMN metadata, and macro names should remain unique.
- Build coverage for `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c` and Vega10 power-management code that includes `vega10_inc.h`; compile failures usually catch renamed or missing macros but not wrong values.
- Static diff review of non-zero default changes, especially PF/VF PCIe capability headers, `DEVICE_CNTL`, `LINK_CAP`, `LINK_STATUS`, `MSI_MSG_CNTL`, reset controls, RAS controls, PCIe wrapper controls, and DWC PHY calibration/tuning values.
- Runtime PCIe enumeration checks on NBIO 6.1/Vega hardware: PF/VF config space, BAR sizing, PCIe capabilities, MSI/MSI-X setup, AER capability visibility, ARI/RTR fields, and SR-IOV VF creation.
- Link stability and power-management tests: boot, suspend/resume, runtime power transitions, ASPM/LTR behavior, clock-gating/light-sleep enablement, link retrain, bandwidth-change notifications, and hot reset.
- Reset/recovery tests: GPU reset, PF FLR, VF FLR, D3hot-to-D0, and RAS/error recovery paths should not leave NBIO, PCIe, MSI-X, or PHY state inconsistent with driver expectations.
- Hardware diagnostics comparing selected registers after a known reset against these generated defaults, with allowances for strap-, firmware-, BIOS-, or OS-programmed fields.

### subset-b-002997: lines 5830-8638

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h lines 5830-8638

## Scope

This chunk is part of a generated AMD NBIO 6.1 default-value header. It contains C preprocessor `#define` constants only; there are no functions, structs, variables, branches, loops, locks, allocations, or direct register accesses in this range.

The assigned slice starts in the middle of the `smnDWC_E12MP_PHY_X4_NS_X4_0_LANE3` register-default block, immediately after lane 3 RX override input defaults have already begun. It then covers the rest of lane 3 PHY defaults, common raw PHY memory table defaults, raw per-lane always-on defaults for lanes 0-3, shared `SUPX` PLL/support defaults, generic `LANEX` defaults, and the start of `RAWCMNX` common memory defaults. It ends in the middle of `RAWCMNX_DIG_MEM_CMN4_B6`; later `RAWCMNX` rows are outside this work item.

Although the path is under a local `ceph-client` source mirror, this file is AMDGPU hardware register metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this chunk is to publish hardware reset or generator-provided default values for NBIO 6.1 PCIe/PHY SMN registers associated with a Synopsys DWC E12MP x4 PHY instance (`DWC_E12MP_PHY_X4_NS_X4_0`). Runtime AMDGPU code can use these constants as known baseline values, comparison values, or generated metadata alongside the matching offset and shift/mask headers.

Each macro follows the generated naming pattern:

- `smnDWC_E12MP_PHY_X4_NS_X4_0_<REGISTER_OR_TABLE_ENTRY>_DEFAULT`
- a literal 32-bit hexadecimal value such as `0x000003e8`, `0x00000000`, or table-programming values under `RAWCMN` and `RAWCMNX`.

The paired register-address and field-layout metadata live in `nbio_6_1_offset.h`, `nbio_6_1_sh_mask.h`, and `nbio_6_1_smn.h`. The principal in-tree include users are `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c` and `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h`.

## Important Macro Families

The opening `LANE3` section completes the lane 3 digital ASIC, TX, RX, and analog default block. It includes TX/RX override inputs and outputs, TX power-state and power-up timing defaults, RX power-state and power-up timing defaults, RX VCO calibration control/time/status defaults, RX alignment masks, LBERT control/error defaults, CDR control/status defaults, DPLL frequency/bounds defaults, RX adaptation configuration/status defaults, DFE and slicer DAC offset defaults, RX statistics comparator/counter defaults, digital-to-analog override outputs, analog RX DAC/AFE/scope/slicer/IQ defaults, and lane-level analog TX/RX override, ATB, termination, boost, calibration, and measurement defaults.

The `RAWCMN_DIG_MEM_CMN2` through `RAWCMN_DIG_MEM_CMN6` sections dominate the middle of the chunk. These are common PHY memory table defaults arranged as bank/row macros (`B<n>_R<n>`). The values are opaque generated programming entries rather than self-describing bitfields in this header. They likely seed firmware or hardware micro-table state for common PHY calibration, equalization, PLL, sequencer, or initialization behavior.

The `RAWLANE0` through `RAWLANE3` groups define per-lane raw always-on digital defaults. The covered fields include RX adaptation IQ/FOM/phase-adjust state, adaptation tap/status registers, slicer controls, DCC calibration code defaults, loss-of-signal mask and signal-detect filter/calibration defaults, override outputs, VREF generator defaults, and signal-detect configuration. Most values are zeroed status or disabled override defaults, with a few repeated nonzero calibration/control seeds.

The `SUPX` group contains support/common PLL and clocking defaults such as `MPLLA_*`, clock control, transmit clock, RX PPM control, power-down, spread-spectrum clocking, and ASIC input/output defaults. These constants sit between raw lane-specific data and generic lane templates, reflecting shared PHY support logic rather than one physical lane.

The `LANEX` group provides generic lane-template defaults similar to the earlier concrete `LANE3` block. It covers ASIC override inputs/outputs, TX/RX power-state and timing defaults, RX VCO calibration, CDR, DPLL, adaptation, DFE/slicer, statistics, digital analog overrides, and analog TX/RX defaults. The `LANEX` template can be used by generated consumers or documentation to describe defaults common to all lanes, while concrete `LANE0`-`LANE3` blocks describe lane-specific register names.

The final `RAWCMNX_DIG_MEM_CMN2` through partial `RAWCMNX_DIG_MEM_CMN4` section mirrors the common raw memory-table pattern for an `X` common instance. This chunk includes complete `RAWCMNX` CMN2 and CMN3 blocks and runs through `RAWCMNX_DIG_MEM_CMN4_B6_R8_DEFAULT`; the remaining CMN4 and later entries continue after line 8638.

## Control Flow

There is no executable control flow in this header chunk. Runtime behavior is indirect:

1. AMDGPU NBIO or power-management code includes this header together with the matching offset, shift/mask, and SMN headers.
2. Code selects an NBIO/PCIe/PHY register address from generated address metadata.
3. Register helpers such as `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, `REG_SET_FIELD`, and `REG_GET_FIELD` read, compare, compose, or write values.
4. Default constants from this file may be used as reset baselines, generator cross-checks, or initialization reference values for PHY and NBIO paths.

The active NBIO 6.1 implementation in `nbio_v6_1.c` programs memory-controller access, doorbell apertures and ranges, interrupt control, clock gating, light sleep, LTR/ASPM-related registers, and PCIe-facing state. This chunk does not itself perform those operations; it supplies generated constants that must remain consistent with the register database used by those operations.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. The values describe hardware-backed state in the GPU NBIO/PCIe PHY block. Real state lives in device registers, hardware sequencers, firmware-programmed PHY tables, Linux PCIe policy, and AMDGPU driver state.

The represented hardware state includes lane 3 TX/RX override and calibration settings, TX and RX low-power state timings, RX CDR/DPLL/adaptation state, DFE and slicer offsets, RX statistics counters and match controls, analog TX/RX overrides and measurements, common PHY raw memory tables, raw per-lane always-on adaptation/signal-detect defaults for lanes 0-3, common PLL/support defaults, and generic all-lane template defaults.

Many macros have `0x00000000` defaults, indicating disabled overrides, reset status values, or unprogrammed counters. Nonzero defaults are concentrated in power-state timing, calibration, DPLL/CDR, adaptation, slicer/DFE offsets, termination, and raw common memory table entries. The header does not encode access permissions, write-one-to-clear semantics, sequencing requirements, polling delays, firmware ownership, or whether a default is a true silicon reset value versus a generated initialization expectation.

## Dependencies And Integration Points

The primary dependencies are the other generated NBIO 6.1 headers:

- `nbio_6_1_offset.h` for register offsets.
- `nbio_6_1_sh_mask.h` for field shifts and masks.
- `nbio_6_1_smn.h` for SMN-addressed register definitions.

Direct include integration appears in `amdgpu/nbio_v6_1.c`, where NBIO 6.1 runtime logic uses generated register metadata for device initialization, doorbells, interrupt routing, clock gating, memory access enablement, and PCIe policy. `pm/powerplay/hwmgr/vega10_inc.h` also includes the NBIO 6.1 default, offset, and shift/mask headers alongside THM, MP, and GC register metadata for Vega10-era power-management code.

Hardware integration points include PCIe link bring-up and retraining, PHY calibration, TX/RX power transitions, ASPM/LTR and light-sleep behavior, clock gating, suspend/resume, reset, interrupt routing, doorbell aperture setup, signal-detect behavior, and diagnostics that inspect RX adaptation, CDR, DPLL, LBERT, or lane statistics.

## Risks And Edge Cases

- The chunk boundaries are artificial. It starts after lane 3 defaults have already begun and ends before the `RAWCMNX` common memory table is complete.
- These are untyped preprocessor constants. Wrong values, stale generated output, or macro-name drift can compile cleanly while changing hardware programming semantics.
- The `RAWCMN` and `RAWCMNX` memory-table entries are opaque in this header. Reviewers cannot infer bit ownership or side effects from the macro names alone, so validation must compare against the authoritative register-generation source or hardware documentation.
- Lane-specific and generic lane-template sections are highly repetitive. Copy/generation errors can swap `LANE3`, `LANEX`, or `RAWLANE<n>` data without producing compile errors.
- PHY defaults are signal-integrity sensitive. Incorrect CDR, DPLL, VCO calibration, RX adaptation, DFE, slicer, TX termination, TX boost, or power timing defaults can produce intermittent link training failures, width/speed downgrades, AER noise, suspend/resume failures, or platform-specific instability.
- Some status-looking defaults are zeroed counters or hardware-updated registers. Treating them as writable initialization values in runtime code could clear useful diagnostic state or fight hardware ownership.
- Common PLL/support defaults affect all lanes. A single bad `SUPX`, `RAWCMN`, or `RAWCMNX` entry may surface as multi-lane link failure rather than a localized lane issue.
- This source path lives under a Ceph mirror, but the content is GPU hardware metadata. Cross-subsystem tooling must avoid classifying this chunk as filesystem logic.

## Test Signals

Useful validation is mostly build-time and hardware-integration oriented:

- Build AMDGPU with NBIO 6.1/Vega10 support enabled; missing or renamed generated macros should surface through `nbio_v6_1.c`, `vega10_inc.h`, or transitive generated-header includes.
- Compare the macro names and ordering against `nbio_6_1_offset.h`, `nbio_6_1_sh_mask.h`, and `nbio_6_1_smn.h` to ensure each default value still aligns with the intended register name and SMN address.
- Diff this generated header against the authoritative AMD register database or a known-good kernel import when refreshing hardware metadata.
- Boot affected Vega10/NBIO 6.1 hardware and verify PCIe link width/speed, retraining, ASPM/LTR behavior, clock gating, light sleep, suspend/resume, and reset paths.
- Exercise high-bandwidth PCIe DMA and interrupt-heavy workloads to expose marginal PHY settings, lost interrupts from related NBIO setup, or link instability.
- Monitor `lspci -vv`, kernel PCIe/AER logs, AMDGPU debug output, and platform error counters for receiver errors, replay timeouts, link downtraining, equalization failures, or unexpected correctable/uncorrectable errors.
- Use available PHY diagnostics, LBERT hooks, lane statistics, or vendor debug tooling to inspect CDR/DPLL lock, RX adaptation convergence, signal detect, DFE/slicer behavior, and per-lane error rates.

## Chunk Notes

- Lines 5830-5987 complete concrete `LANE3` PHY defaults.
- Lines 5988-7278 cover `RAWCMN_DIG_MEM_CMN2` through `RAWCMN_DIG_MEM_CMN6` bank/row table defaults.
- Lines 7279-7705 cover raw always-on per-lane defaults for `RAWLANE0` through `RAWLANE3`.
- Lines 7706-7778 cover `SUPX` shared PLL/support defaults.
- Lines 7779-7952 cover generic `LANEX` lane-template defaults.
- Lines 7953-8638 cover `RAWCMNX_DIG_MEM_CMN2`, `RAWCMNX_DIG_MEM_CMN3`, and the beginning of `RAWCMNX_DIG_MEM_CMN4`.

### subset-b-002998: lines 8639-11461

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h lines 8639-11461

## Scope

This chunk is a generated AMDGPU NBIO 6.1 default-value header segment. It contains only C preprocessor constants of the form `*_DEFAULT`; there are no functions, structures, enums, includes, allocation paths, locking, or direct register reads/writes in this range.

The range covers 2,805 `#define` rows. It starts in the middle of the `nbio_pipe_pcs_dwc_e12mp_phy_x4_ns0...mem_map` area, at `smnDWC_E12MP_PHY_X4_NS_X4_0_RAWCMNX_DIG_MEM_CMN4_B5_R14_DEFAULT`, proceeds through raw common memory, MPLL, lane digital, DXIO/KP, PCS, and PCIe x16 gasket defaults, then enters the `nbio_pipe_pcs_dwc_e12mp_phy_x4_ns1...mem_map` area. It ends in the middle of the `smnDWC_E12MP_PHY_X4_NS_X4_1_RAWCMN_DIG_MEM_CMN6` table at `B6_R3`.

Visible address-block markers in this slice are:

- `nbio_pipe_pcs_lcu_pcie_pcs_prime_phyx4_pcs_prime_dir`
- `nbio_lcu_kpfifo_kpfifo0_kpfifo_dir`
- `nbio_lcu_kpnp_kpnp0_kpnp_dir`
- `nbio_pipe_pcs_pcs_core0_dir`
- `nbio_pipe_pcs_pcs_pciex16_gaskt_pcs_pciex16_gaskt_dir`
- `nbio_pipe_pcs_dwc_e12mp_phy_x4_ns1_dwc_e12mp_phy_x4_ns_UP16_dwc_e12mp_phy_x4_ns_UP16_mem_map`

Because the chunk begins and ends inside generated register families, the merge lane should treat this as a partial source-file slice, not as a complete logical register block.

## Purpose

`nbio_6_1_default.h` is the reset/default-value half of AMD's generated NBIO 6.1 register interface. The companion NBIO headers provide offsets, SMN addresses, and field masks; this file gives the reset or expected default values for those registers. Driver code can include it when it needs ASIC-specific constants for comparing observed hardware state, programming known initial values, or carrying generated register metadata through build-time consumers.

This chunk focuses on the physical/link side of NBIO rather than PCI configuration-space defaults. The largest families describe Synopsys `DWC_E12MP_PHY_X4` PCIe PHY instances, including common memory table rows, MPLL spread-spectrum and bandwidth defaults, lane adaptation/calibration controls, RX/TX PCS/PMA handoff signals, analog lane defaults, and common/supervisor controls. Smaller sections cover DXIO linkage, KP FIFO/KPNP reset/link request defaults, PCS core global controls, per-lane x16 control/coefficients, and PCIe x16 gasket defaults.

## Macro Families and Coverage

The first 687 definitions are a continuation from the prior address block, covering the tail of the `NS_X4_0` PHY map. This includes:

- `RAWCMNX_DIG_MEM_CMN4` rows from `B5_R14` through `B7_R31`, then full `RAWCMNX_DIG_MEM_CMN5` and most of `RAWCMNX_DIG_MEM_CMN6`.
- `RAWCMNX_DIG_MPLLA_*` and `RAWCMNX_DIG_MPLLB_*` defaults such as bandwidth override and spread-spectrum override values.
- `RAWLANEX_DIG_*` lane defaults for PCS/PMA transfer, fast state-machine calibration/power-up controls, always-on adaptation values, DFE/AFE offsets, IRQ controls, TX/RX control, RTUNE, and RX data enable/loss-of-signal behavior.

The explicit intermediate address blocks then define:

- `smnDXIO_*`, `smnMAC_CAPABILITIES*`, and PCS aperture/capability/reset defaults in the prime PHY/PCS direction block.
- `smnKPFIFO0_*` defaults for HSCID, per-lane primary TX FIFO controls, and PCS/PMA soft reset.
- `smnKPNP_SNPS0_*` defaults for KPNP hardware version, lane ID/request control/status, PHY information/control, PMA control, and reset control.
- `smnPCS_PCIEX16_*` defaults in the PCS core, including global controls, soft reset, LCU control, per-lane controls for lanes 0 through 15, and `smnPCS_EXTENDED_CAP_DEFAULT`.
- `smnPCS_GLOBAL_CONTROL17` through `30`, eight lane-group mappings, and repeated `smnPCS_LANE{0..15}_CNTRL1/COEFF1/COEFF2/COEFF3` defaults in the PCIe x16 gasket block.

The final 1,953 definitions are the start and middle of the `NS_X4_1` PHY map. This portion includes:

- `SUP_DIG_*` and `SUP_ANA_*` defaults for ID codes, reference clock overrides, MPLLA/MPLLB overrides, PLL power-control timing thresholds, spread-spectrum frequency/phase, RTUNE status/set values, and analog switch/bandgap measurement defaults.
- Four lane families, `LANE0` through `LANE3`, covering ASIC RX/TX inputs/outputs, analog TX/RX defaults, RX adaptation configuration/status, CDR, DPLL bounds/frequency, LBERT, RX/TX power-state timing, status match/counter controls, VCO calibration, TX equalization override outputs, slicer/DAC controls, and PMA/PCS interface defaults.
- `RAWCMN_DIG_MEM_CMN2`, `CMN3`, `CMN4`, `CMN5`, and a partial `CMN6` table. The chunk ends while `CMN6` is still being enumerated.

Across the whole slice, 837 of the 2,805 default values are `0x00000000`. Nonzero patterns include repeated ID/default timing constants such as `0x000074cd`, `0x00000733`, `0x00000043`, `0x00005000`, `0x00000080`, `0x00000800`, `0xa6121400`, `0xa6141700`, and `0xd02c1d00`.

## Important APIs, Types, and Functions

There are no callable APIs, C types, or functions in this chunk. The exported interface is the generated macro namespace:

- `smnDWC_E12MP_PHY_X4_NS_X4_0_*_DEFAULT` for the first visible x4 PHY instance and its raw common/lane defaults.
- `smnDWC_E12MP_PHY_X4_NS_X4_1_*_DEFAULT` for the next x4 PHY instance, including supervisor, lane 0-3, and raw common memory defaults.
- `smnDXIO_*_DEFAULT`, `smnKPFIFO0_*_DEFAULT`, `smnKPNP_SNPS0_*_DEFAULT`, `smnPCS_*_DEFAULT`, and `smnMAC_*_DEFAULT` for DXIO, KP FIFO, KPNP, PCS, and MAC/PCS capability or reset defaults.

Consumers use these names as compile-time constants. Address selection comes from `nbio_6_1_offset.h` or `nbio_6_1_smn.h`; field extraction/composition comes from `nbio_6_1_sh_mask.h`.

## Control Flow

This chunk has no runtime control flow. Inclusion is controlled by the header guard at the top of `nbio_6_1_default.h`, outside this slice.

The inferred consumer flow is:

1. Include the NBIO 6.1 generated header set.
2. Select an NBIO/SMN register address from the offset or SMN header.
3. Optionally compare a hardware readback against the matching `*_DEFAULT` macro, or use the default as a base value before field updates.
4. Use `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_*`, or `RREG32_*` style helpers in AMDGPU code for actual register access.

The source reader should not infer any ordering or polling semantics from the macro order alone. The sequence mirrors the generated register database layout, not executable initialization code.

## State and Persistence Behavior

The header stores no software state and has no persistence behavior. It documents hardware reset/default values for NBIO, DXIO, PCS, KPNP, KP FIFO, and Synopsys PHY registers.

The represented hardware state persists in registers after reset according to the ASIC and firmware initialization sequence. Runtime code, firmware, PCIe link training, power management, soft reset, clock gating, PHY calibration, lane adaptation, and GPU reset can change those registers after their default state. Many status-like defaults are zero because the corresponding hardware state is produced later by calibration or link bring-up.

The raw memory-table defaults (`*_DIG_MEM_CMN*_B*_R*`) are dense generated constants rather than named bitfields. They should be treated as opaque vendor PHY programming data unless cross-referenced with the authoritative register database. Hand-editing individual values without the generator context is risky.

## Dependencies and Integration Points

This chunk integrates with:

- `nbio_6_1_offset.h`, `nbio_6_1_sh_mask.h`, and `nbio_6_1_smn.h`, which provide the companion address and field metadata for the same NBIO 6.1 register database.
- `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, which includes all NBIO 6.1 generated headers and uses SOC15/PCIE register helpers for NBIO setup, doorbells, interrupt control, clock gating, link power management, and related register programming.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h`, which includes NBIO 6.1 generated defaults, offsets, and masks alongside THM, MP, and GC generated headers for Vega10 power-management code.
- AMDGPU register helper conventions such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `REG_SET_FIELD`, and `REG_GET_FIELD`.
- Hardware/firmware expectations for Synopsys E12MP PHY calibration, PLL setup, spread-spectrum clocking, lane adaptation, PCIe PCS behavior, and DXIO/KP reset state.

## Risks and Edge Cases

- The file is generated. A one-value generation error can compile cleanly while causing subtle PHY, PCS, or link-training failures.
- This chunk has partial boundaries at both ends. It begins mid `NS_X4_0_RAWCMNX_DIG_MEM_CMN4` and ends mid `NS_X4_1_RAWCMN_DIG_MEM_CMN6`, so local counts are not complete family counts.
- Raw common memory tables encode opaque PHY programming. Treating `B*_R*` rows as independently meaningful registers without the generator spec can lead to incorrect patches.
- Several sections are highly repetitive across lanes and PHY instances. Copy/paste or generator skew between lane 0-3, lane group 0-7, and lane 0-15 PCS definitions may only show up as signal-integrity or link-width/speed problems.
- Default constants for reset, override, IRQ clear/status, calibration status, and power-state timing have different runtime semantics. Using a default value as a blind writeback can clear events, force overrides, or reset link-related blocks unexpectedly.
- Zero defaults are common but do not always mean "disabled forever"; many zero-valued status and calibration fields are expected to become nonzero after firmware, hardware FSMs, or link training run.
- PLL, spread-spectrum, RTUNE, RX/TX power-up timing, and DFE/AFE defaults are board/ASIC-sensitive. Incorrect values can affect PCIe stability, clock tolerance, or low-power transitions.
- PCS lane coefficient defaults are repeated for lanes 0-15. An incorrect per-lane value may only appear under specific negotiated widths, lane reversal, or degraded-link cases.

## Test Signals

Useful validation signals for this chunk:

- Build AMDGPU configurations that include `nbio_6_1_default.h`; missing, malformed, or duplicate macros should fail at compile time.
- Run generated-header consistency checks against the authoritative NBIO 6.1 register database, especially for `*_DEFAULT` alignment with `nbio_6_1_offset.h`, `nbio_6_1_smn.h`, and `nbio_6_1_sh_mask.h`.
- Compare repeated lane families for expected parity across `LANE0` through `LANE3` in the `NS_X4_1` PHY map and lanes 0 through 15 in PCS coefficient/control defaults.
- Compare the partial `NS_X4_0` and `NS_X4_1` raw common memory table patterns with neighboring chunks to catch boundary or generator ordering errors.
- Boot and suspend/resume tests on NBIO 6.1 hardware with PCIe link training at expected widths and speeds.
- PCIe diagnostics such as link speed/width readback, AER absence under idle and load, and stable retraining behavior after GPU reset or runtime power transitions.
- PHY/link stress tests under ASPM, clock gating, low-power transitions, and high-throughput DMA to expose bad PLL, RTUNE, PCS, or lane adaptation defaults.
- Register readback spot checks after reset or early init for high-signal constants such as `smnDXIO_HWDID_DEFAULT`, `smnPCS_PCIEX16_GLOBAL_CONTROL0_DEFAULT`, `smnPCS_LANE*_COEFF*`, supervisor ID-code defaults, and PLL timing defaults.

### subset-b-002999: lines 11462-14269

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h lines 11462-14269

## Scope

This chunk is a generated AMDGPU NBIO 6.1 default-value header segment. It contains only C preprocessor constants of the form `#define <register>_DEFAULT <hex-value>`; it has no functions, structs, enums, variables, allocation, locking, direct MMIO access, or executable control flow.

The range covers 2,799 `#define` rows. It starts in the middle of the `DWC_E12MP_PHY_X4_NS_X4_1_RAWCMN` common-memory default table, continues through X4_1 raw-lane, supervisor, generic-lane, and raw-common templates, includes small `KPFIFO1` and `KPNP_SNPS1` default blocks, then starts the `DWC_E12MP_PHY_X4_NS_X4_2` supervisor and lane defaults. The chunk ends inside `X4_2_LANE3_DIG_RX_STAT_MATCH_CTL0`, so the `X4_2_LANE3` block is incomplete in this slice.

Visible address-block markers in or near this range include:

- `nbio_lcu_kpfifo_kpfifo1_kpfifo_dir`
- `nbio_lcu_kpnp_kpnp1_kpnp_dir`
- `nbio_pipe_pcs_dwc_e12mp_phy_x4_ns2_dwc_e12mp_phy_x4_ns_UP16_dwc_e12mp_phy_x4_ns_UP16_mem_map`

The surrounding file header identifies this as the default-value half of the NBIO 6.1 generated register set. Related include-level integration is visible in `amdgpu/nbio_v6_1.c`, which includes `nbio_6_1_default.h` together with `nbio_6_1_offset.h`, `nbio_6_1_sh_mask.h`, and `nbio_6_1_smn.h`; Vega10 powerplay headers also include this default header.

## Purpose

`nbio_6_1_default.h` records hardware reset or generator-specified default values for NBIO 6.1 registers. This chunk is focused on Synopsys DesignWare E12MP x4 PIPE/PCS/PHY register defaults for NBIO PCIe/NBIO link units rather than PCI configuration-space fields.

The covered defaults describe:

- Common PHY memory/register defaults for `X4_1_RAWCMN` and `X4_1_RAWCMNX`, including many `DIG_MEM_CMN*` rows.
- Per-lane raw PCS/PMA control defaults for `X4_1_RAWLANE0` through `X4_1_RAWLANE3`, plus generic `RAWLANEX` defaults.
- Supervisor/common PLL defaults for `X4_1_SUPX` and `X4_2_SUP`, including IDCODE, reference-clock override, MPLLA/MPLLB override, spread-spectrum clocking, analog PLL, RTUNE, and common power-control timing values.
- Per-lane ASIC, TX/RX power-control, RX VCO calibration, CDR/DPLL, RX adaptation, statistics, and analog TX/RX defaults for `X4_1_LANEX` and `X4_2_LANE0` through part of `X4_2_LANE3`.
- KPFIFO and KPNP defaults for lane FIFO control, PCS/PMA soft reset, PHY identity, lane request/control/status, PMA controls, PHY/lane soft reset, and reset control.

Most values are `0x00000000`, which is expected for status, monitor, override-disabled, scratch, and analog-measurement registers. Nonzero defaults encode hardware bring-up policy: PLL bandwidth and SSC values, ID codes, lane power-state encodings, TX/RX power-up timers, CDR/DPLL tuning, RX adaptation presets, slicer and DAC offsets, reset defaults, and lane/FIFO control defaults.

## Important Macro Families

There are no callable APIs or C types. The consumed API surface is the macro namespace itself.

Important families in this slice are:

- `smnDWC_E12MP_PHY_X4_NS_X4_1_RAWCMN_DIG_MEM_CMN6_B6_R4_DEFAULT` through the rest of `B6_R31`, continuing a common-memory bank that began before the chunk. These are all zero in this slice.
- `smnDWC_E12MP_PHY_X4_NS_X4_1_RAWCMN_DIG_MPLLA_*` and `*_MPLLB_*` defaults, with PLL bandwidth override values such as `0x00000043`, SSC control `0x00005000`, and SSC enable defaults of zero.
- `smnDWC_E12MP_PHY_X4_NS_X4_1_RAWLANE{0..3}_DIG_PCS_XF_*`, `DIG_FSM_*`, `DIG_AON_*`, `DIG_IRQ_CTL_*`, `DIG_PMA_XF_*`, `DIG_TX_CTL_*`, and `DIG_RX_CTL_*`, which repeat per raw lane. These cover PCS/PMA override inputs/outputs, TX/RX PCS interfaces, adaptation acknowledgements, FSM fast-path/status registers, always-on analog offset defaults, IRQ clear/mask defaults, PMA lane/supervisor handoff, and TX/RX control defaults.
- `smnDWC_E12MP_PHY_X4_NS_X4_1_SUPX_*` and `smnDWC_E12MP_PHY_X4_NS_X4_2_SUP_*`, which expose common/supervisor PLL and analog defaults. Notable values include IDCODE low/high defaults, refclk override `0x00000070`, MPLLA/MPLLB override encodings, PLL power timing thresholds, SSC phase/frequency values, analog misc values, and RTUNE defaults.
- `smnDWC_E12MP_PHY_X4_NS_X4_1_LANEX_*` and `smnDWC_E12MP_PHY_X4_NS_X4_2_LANE{0..3}_*`, which define generic and concrete lane defaults for ASIC handoff, TX power states, RX power states, VCO calibration, RX alignment, LBERT, CDR, DPLL, adaptation control/status, RX statistics, and analog TX/RX controls.
- `smnDWC_E12MP_PHY_X4_NS_X4_1_RAWCMNX_DIG_MEM_CMN*` defaults, a large common-memory template with many repeated nonzero calibration/control words such as `0x00005306`, `0x00001f4f`, `0x000001af`, `0x000001b6`, `0x0000080e`, and zero-filled gaps.
- `smnKPFIFO1_*` defaults, covering primary TX FIFO HSCID, per-lane FIFO control for lanes 0-3, and PCS/PMA soft reset.
- `smnKPNP_SNPS1_*` defaults, covering KPNP hardware version/PHY info/lane ID, lane request control and status, PMA control registers, PHY and lane soft reset defaults, and reset control.

## Control Flow

This header segment has no runtime control flow. Inclusion is controlled by the full file's header guard. At compile time, translation units that include `nbio_6_1_default.h` receive these constants.

The intended consumer pattern is external to this file:

1. Select a register address from `nbio_6_1_offset.h` or `nbio_6_1_smn.h`.
2. Use field layout from `nbio_6_1_sh_mask.h` when a bitfield must be decoded or composed.
3. Use the matching `_DEFAULT` macro from this header as a reset/default comparison value, initialization seed, generated-table input, or documentation of hardware reset state.
4. Perform actual access through AMDGPU register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `REG_SET_FIELD`, or related NBIO/SOC15 helpers.

The local `amdgpu/nbio_v6_1.c` runtime implementation mostly manipulates NBIO/PCIe registers through offset and mask headers; direct default-value usage is not obvious in the inspected section. The default header still remains part of the generated NBIO 6.1 interface and must stay synchronized with offsets, SMN addresses, and masks.

## State and Persistence Behavior

The header stores no software state and performs no persistence. It describes default state held in NBIO/PHY hardware registers.

State represented by these constants includes:

- Static identity and revision values for supervisor PHY blocks.
- Default PLL, SSC, refclock, RTUNE, and common analog settings.
- Per-lane TX/RX power-state defaults and wake/power-up timing values.
- RX VCO calibration, CDR, DPLL, adaptation, slicer, DAC, DFE, and statistics defaults.
- PCS/PMA override inputs and outputs, ASIC handoff defaults, and PMA/supervisor interface defaults.
- IRQ mask/clear defaults and reset/default values for KPFIFO/KPNP control registers.
- Raw common-memory banks that likely seed PHY firmware/microsequence or generated common control tables.

Persistence and lifetime are hardware-defined. These values may be present after power-on reset, GPU reset, NBIO reset, PHY/lane reset, or firmware initialization, but runtime firmware and the AMDGPU driver can alter many of the same registers during link training, PCIe power management, clock gating/light sleep, reset handling, or diagnostics. Status and monitor registers default to zero but are updated by hardware after bring-up. Override and reset defaults are especially sensitive because writing the default value may assert/deassert control, not merely restore a passive software variable.

## Dependencies and Integration Points

This chunk integrates with:

- `nbio_6_1_offset.h`, which supplies register offsets for the same NBIO 6.1 generated register database.
- `nbio_6_1_sh_mask.h`, which supplies field masks/shifts when code needs to modify pieces of these registers rather than comparing whole defaults.
- `nbio_6_1_smn.h`, which supplies SMN address constants for direct SMN/PCIe register access.
- `amdgpu/nbio_v6_1.c`, the NBIO 6.1 runtime implementation, which includes the default, offset, mask, and SMN headers together and uses SOC15/PCIe register helpers for NBIO control.
- `pm/powerplay/hwmgr/vega10_inc.h`, which also includes this generated default header as part of Vega10/NBIO register metadata.
- PCIe PHY/link bring-up, power management, clock gating, reset, link-training, and error/recovery flows that rely on NBIO 6.1 register definitions.
- The generated register source used to create `default`, `offset`, `sh_mask`, and `smn` headers. A mismatch between these headers can produce valid C that programs or validates the wrong hardware register.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMD GPU driver hardware metadata and has no direct Ceph or distributed-filesystem behavior.

## Risks and Edge Cases

- The file is generated and highly repetitive. A single bad default can be difficult to spot manually and may only appear as unstable PCIe link training, bad power transitions, failed reset recovery, or poor signal integrity.
- This chunk begins and ends inside larger logical regions. The `X4_1_RAWCMN` memory bank starts before line 11462, and `X4_2_LANE3` continues after line 14269. Merge/reconciliation should not treat either boundary as complete.
- Per-lane blocks are mechanically repeated. `RAWLANE0` through `RAWLANE3`, `LANEX`, and `X4_2_LANE0` through `X4_2_LANE2` should be compared after normalizing the lane number, while `X4_2_LANE3` is partial in this slice.
- The naming distinction between concrete lanes (`LANE0`), raw lanes (`RAWLANE0`), generic lane templates (`LANEX`/`RAWLANEX`), common blocks (`RAWCMN`/`RAWCMNX`), and supervisor blocks (`SUP`/`SUPX`) is meaningful. Accidentally using a generic-template default for a concrete lane or the wrong x4 instance can program the wrong hardware block.
- Many zeros are intentional, but zero is not always harmless. Defaults for reset, clear, mask, override, enable, and status registers can have side effects if code writes them back during runtime.
- Nonzero PHY calibration and analog values are hardware-tuned constants. Changes to defaults such as PLL bandwidth/SSC, CDR/DPLL, VCO calibration, DFE/slicer offsets, TX/RX power timing, and PMA controls can affect PCIe link margin, speed negotiation, power, or reliability.
- KPNP reset defaults include nonzero PMA/reset values (`PMA_CONTROL1`, `PMA_CONTROL2`, `LANE_SOFT_RESET`, `REG_RST_CTRL`). Misinterpreting these as arbitrary reset-state documentation could leave PHY lanes held in reset or released too early.
- The `_DEFAULT` header does not encode access semantics. Consumers still need the offset, mask, SMN address, and hardware rules for read-only, write-one-to-clear, sticky, volatile, or self-clearing registers.

## Test Signals

Useful validation signals for this chunk:

- Compile AMDGPU configurations that include `nbio_6_1_default.h`, especially `amdgpu/nbio_v6_1.c` and Vega10 powerplay paths. Missing, malformed, or duplicate macros should fail at build time.
- Run generated-header consistency checks against the authoritative NBIO 6.1 register database, verifying that defaults, offsets, masks, and SMN names stay synchronized.
- Mechanically count and validate this slice: it should contain 2,799 `#define` rows in the requested line range, all with hexadecimal default values.
- Normalize lane numbers and compare repeated `RAWLANE0`-`RAWLANE3` groups for expected structural parity; compare `X4_2_LANE0`-`X4_2_LANE2` similarly and treat `X4_2_LANE3` as partial.
- Check chunk-boundary reconciliation with adjacent research chunks so `X4_1_RAWCMN` and `X4_2_LANE3` are represented as partial here, not as full blocks.
- On NBIO 6.1/Vega10-class hardware, use PCIe link smoke tests after boot, suspend/resume, GPU reset, and module reload to catch PHY default regressions: link comes up, negotiated speed/width are expected, no repeated retraining occurs, and AER/error counters remain stable.
- Exercise power-management and light-sleep/clock-gating paths that interact with NBIO/PCIe, watching for link-down events, reset storms, or poor LTR/ASPM behavior.
- If low-level diagnostics are available, compare selected PHY/PCS registers after reset with the generated defaults before firmware or driver writes modify them.
- Stress SR-IOV or multi-function configurations only as an integration signal; this chunk is PHY/PCS default metadata rather than PCI configuration-space VF layout, but PHY defaults can still affect VF-visible link stability.

### subset-b-003000: lines 14270-17079

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h lines 14270-17079

## Scope

This chunk is a generated AMD NBIO 6.1 default-register header segment. It contains only C preprocessor `#define` constants with reset/default values; there are no functions, structs, variables, allocation paths, locks, loops, branches, or direct register accesses in this range.

The whole assigned range is under the `smnDWC_E12MP_PHY_X4_NS_X4_2_*` namespace, describing default values for a Synopsys DWC E12MP x4 PCIe PHY instance. It starts in the tail of the concrete `LANE3` receive/stat and analog-default block, continues through large common PHY microcode/memory default tables, repeated raw per-lane PHY defaults for lanes 0 through 3, aggregate `SUPX`/`LANEX` defaults, and ends in the first eight entries of the `RAWCMNX_DIG_MEM_CMN5` table.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header range is to publish power-on or expected reset values for NBIO 6.1 PCIe PHY registers. Each macro follows the generated form:

- `smnDWC_E12MP_PHY_X4_NS_X4_2_<REGISTER_OR_TABLE_ENTRY>_DEFAULT`, the default value associated with one NBIO 6.1 SMN PHY register or generated table entry.

Runtime AMDGPU code can pair these constants with addresses from `nbio_6_1_offset.h` and bit definitions from `nbio_6_1_sh_mask.h` when validating hardware state, initializing register tables, comparing against defaults, or carrying generated register metadata through ASIC-specific include headers.

## Important Macro Families

The opening `LANE3` fragment covers the end of the physical lane 3 block. It includes receive-stat defaults such as match controls, statistic controls, sample/count registers, and calibration comparator clock control. It then covers digital-to-analog override outputs for TX termination/equalization and RX control/power/VCO/DAC/slicer/phase controls, followed by lane-level analog TX and RX defaults for measurement, power override, ATB paths, TX termination code, RX CDR/AFE, calibration muxes, termination, slicer, and VREG state.

The `RAWCMN_DIG_MEM_CMN2` through `RAWCMN_DIG_MEM_CMN6` families are dense generated memory-table defaults. `CMN2`, `CMN3`, `CMN4`, and `CMN5` each contribute 256 entries arranged as bank/register names `B<n>_R<n>`, while `CMN6` contributes 224 entries through `B6_R31`. These values look like firmware-style initialization words for common PHY digital control, sequencing, calibration, PLL, and training tables. Many entries are zero, while nonzero words such as `0x00005306`, `0x00001f4f`, `0x00000800`, `0x000001af`, and `0x0000ffff` recur in structured patterns.

The compact `RAWCMN_DIG_*` control block after the common memory tables defines common PHY controls for `CMN_CTL`, MPLLA/MPLLB bandwidth override, and spread-spectrum clocking override/enables. The defaults show both PLLs sharing the same bandwidth and SSC control defaults in this slice.

The `RAWLANE0` through `RAWLANE3` blocks repeat the same per-lane raw PHY layout. Each lane includes PCS transfer defaults for TX/RX override input/output, PCS input/output, RX adaptation acknowledgements, figure-of-merit, TX pre/main/post cursor direction, and lane number. The lane blocks also include FSM override/monitor/status defaults, fast calibration/adaptation state defaults, always-on AFE/DFE/RX/MPLL/RTUNE/init/adaptation defaults, IRQ request/clear/mask defaults, PMA transfer defaults, TX FSM/clock control, and RX FSM/loss-of-signal/data-enable/adaptation status defaults.

The `SUPX` block is an aggregate or indexed supervisor/common-PHY variant. It includes ID code, reference clock override, MPLLA/MPLLB override and ASIC input defaults, analog override outputs, MPLL power-control and timing thresholds, SSC phase/frequency values, analog MPLL/RTUNE/switch/bandgap defaults, and RTUNE config/status/set/stat registers.

The `LANEX` block is the aggregate per-lane variant. It mirrors the lane-level ASIC override, TX/RX power-state timing, RX VCO calibration, RX CDR/DPLL/adaptation, RX statistic collection, digital analog override, and lane analog TX/RX defaults without binding the names to a numeric lane. This is useful for generated code or documentation that references a lane-template register definition rather than `LANE0` through `LANE3`.

The closing `RAWCMNX_DIG_MEM_CMN2` through `RAWCMNX_DIG_MEM_CMN4` families mirror the earlier common memory tables for an indexed/common-template namespace. `RAWCMNX_DIG_MEM_CMN2`, `CMN3`, and `CMN4` are complete 256-entry tables in this chunk. The range then begins `RAWCMNX_DIG_MEM_CMN5` and stops at `B0_R7`, so the rest of `CMN5` and any later `RAWCMNX` defaults are outside this work item.

## Control Flow

There is no executable control flow in this header. Runtime behavior appears only when other AMDGPU code includes the generated constants:

1. ASIC-specific code selects an NBIO 6.1 register offset or SMN address from the matching generated address headers.
2. Driver code reads, writes, or compares a register through AMDGPU helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, and `REG_GET_FIELD`.
3. These `_DEFAULT` values may be used as generated metadata for reset-state comparison, table-driven initialization, debugging, or documentation of expected hardware state.

The chunk itself does not decide whether a value is writable, read-only, sticky, hardware-owned, volatile, or safe to restore after reset. Those semantics must come from the corresponding mask/header metadata, hardware documentation, and the NBIO/PCIe/PHY access path.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware reset/default state for an NBIO 6.1 PCIe PHY instance.

The represented state includes PHY common memory tables, PLL bandwidth and spread-spectrum defaults, lane PCS/ASIC/PMA override values, lane TX/RX power-state timing, fast calibration and adaptation defaults, AFE/DFE offset defaults, RX VCO/CDR/DPLL defaults, RX statistic counters and match controls, IRQ status/clear/mask defaults, and analog TX/RX measurement/termination/calibration defaults. Some registers describe static reset state, some are override controls, some are hardware status/monitor paths, and some look like initialization RAM words consumed by PHY sequencers or firmware-like hardware state machines.

The chunk boundaries are artificial. The first lines are the tail of a `LANE3` block that began before line 14270, and the final lines are only the start of `RAWCMNX_DIG_MEM_CMN5`. Whole-PHY analysis for those boundary families requires adjacent chunks.

## Dependencies And Integration Points

The primary dependencies are the generated NBIO 6.1 register headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_offset.h`, which supplies matching register addresses/offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h`, which supplies matching field shifts and masks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_smn.h`, which supplies SMN-space addresses used by NBIO code.

Direct include integration appears in `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, which includes `nbio_6_1_default.h`, `nbio_6_1_offset.h`, `nbio_6_1_sh_mask.h`, and `nbio_6_1_smn.h`. Powerplay include aggregation for Vega-era hardware also includes this default header through `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h`; related Vega include paths consume the NBIO 6.1 offset and mask headers.

The broader runtime integration surfaces are AMDGPU NBIO/BIF setup, PCIe PHY bring-up, clock gating and light sleep policy, link training and retraining, suspend/resume, reset recovery, SR-IOV or passthrough scenarios that depend on stable PCIe link behavior, and diagnostics comparing hardware state against generated reset values.

## Risks And Edge Cases

- These are untyped preprocessor constants. A stale or misgenerated default value can compile cleanly and still mislead reset comparison, diagnostics, or table-driven initialization.
- The namespace is highly repetitive. Copy or generation drift between `LANE0`, `LANE1`, `LANE2`, `LANE3`, `LANEX`, `RAWCMN`, and `RAWCMNX` can silently associate a plausible value with the wrong lane or template register.
- The common memory-table blocks are dense and opaque. A single wrong `B<n>_R<n>` value can alter hardware sequencing, PLL setup, calibration, equalization, or link-training behavior without an obvious source-level symptom.
- Boundary coverage is incomplete. This chunk starts after the beginning of `LANE3` and stops after eight `RAWCMNX_DIG_MEM_CMN5` entries, so it should not be used alone to make whole-lane or whole-table completeness claims.
- PHY analog defaults are interoperability-sensitive. Incorrect TX termination/equalization, RX CDR/AFE, slicer, DFE, VCO, RTUNE, or PLL/SSC defaults can cause marginal links, speed downgrade, link training failures, resume failures, or platform-specific PCIe instability.
- IRQ and status defaults include request, clear, mask, monitor, and counter-style registers. Treating a status or clear register as an ordinary restore target can clear evidence or mask a live hardware event if runtime code uses these values naively.
- Default values do not encode access permissions or side effects. Some values may describe read-only status, hardware-updated state, write-one-to-clear bits, test/ATB paths, or fuse/ASIC input mirrors.

## Test Signals

Useful validation is mostly build-time and hardware-integration oriented:

- Build AMDGPU with NBIO 6.1/Vega support enabled; missing, renamed, or duplicated generated macros should surface through `nbio_v6_1.c`, Vega powerplay include paths, or generated-header consumers.
- Cross-check this default range against `nbio_6_1_offset.h` and `nbio_6_1_sh_mask.h` for matching `DWC_E12MP_PHY_X4_NS_X4_2` register names, lane/template naming, and table ordering.
- On affected hardware, boot and confirm PCIe link speed/width, link retraining, ASPM/light-sleep behavior, and clock-gating transitions remain stable.
- Exercise suspend/resume, runtime power management, GPU reset, and driver unload/reload; PHY default drift often appears as resume link failures, delayed retraining, or unstable RX/TX calibration.
- Run graphics, compute, DMA, and interrupt-heavy workloads while watching for PCIe AER messages, lost interrupts, GPU hangs, link speed downgrade, or corrected-error storms.
- For systems with available diagnostics, compare readback of NBIO/PHY registers after reset or resume against the generated defaults, while excluding volatile status/counter/clear registers.

## Chunk Notes

- Lines 14270-14338 finish the concrete `LANE3` receive-stat, digital analog override, and analog TX/RX default blocks.
- Lines 14339-15586 cover `RAWCMN_DIG_MEM_CMN2` through `RAWCMN_DIG_MEM_CMN6`, with complete 256-entry `CMN2`-`CMN5` tables and a 224-entry `CMN6` table ending at `B6_R31`.
- Lines 15587-15593 cover compact `RAWCMN_DIG_*` common controls for common control, MPLLA/MPLLB bandwidth, and SSC defaults.
- Lines 15594-16065 cover repeated `RAWLANE0` through `RAWLANE3` raw per-lane PCS/FSM/AON/IRQ/PMA/TX/RX control defaults.
- Lines 16066-16138 cover the aggregate `SUPX` supervisor/common defaults.
- Lines 16139-16303 cover the aggregate `LANEX` lane-template defaults.
- Lines 16304-17079 cover complete `RAWCMNX_DIG_MEM_CMN2`, `CMN3`, and `CMN4` tables, then stop inside `RAWCMNX_DIG_MEM_CMN5` after `B0_R7`.

### subset-b-003001: lines 17080-19894

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h lines 17080-19894

## Scope

This chunk is part of AMDGPU's generated NBIO 6.1 default-register header. The selected range contains `#define ..._DEFAULT` constants for the DesignWare Controller E12MP x4 PCIe PHY (`DWC_E12MP_PHY_X4`) exposed through the NBIO SMN register namespace. It does not define executable code, C types, or callable APIs; its API surface is the macro namespace consumed by NBIO/powerplay code together with the matching `nbio_6_1_offset.h`, `nbio_6_1_sh_mask.h`, and `nbio_6_1_smn.h` register descriptions.

The range starts in the middle of `smnDWC_E12MP_PHY_X4_NS_X4_2_RAWCMNX_DIG_MEM_CMN5` and ends in the lane-1 AON adaptation controls for `smnDWC_E12MP_PHY_X4_NS_X4_3_RAWLANE1`. It should be merged later with adjacent chunks for the full generated file-level view.

## Purpose

These macros encode hardware reset/default values for NBIO 6.1 PCIe PHY common and lane registers. The values are used as authoritative constants for register programming, validation, diagnostics, or generated include completeness in the Vega10/NBIO v6.1 driver stack. They preserve ASIC-specific strap/PHY tuning data in source form rather than deriving it at runtime.

The relevant register families in this chunk are:

- `NS_X4_2_RAWCMNX_DIG_MEM_CMN5` and `CMN6`: 16-bit `DATA` defaults for common-side PHY micro/register memory banks, arranged as bank/register pairs (`B0_R8` through `B6_R31` in this chunk).
- `NS_X4_2_RAWLANEX` and `NS_X4_3_LANE0..LANE3`: per-lane digital and analog defaults for override paths, power-state timing, RX adaptation, TX/RX controls, status counters, PLL calibration, and analog tuning.
- `NS_X4_3_RAWCMN_DIG_MEM_CMN2..CMN6`: common-memory bank defaults for the next x4 PHY instance.
- `NS_X4_3_RAWCMN_DIG_*`: common digital controls for MPLLA/MPLLB bandwidth and spread-spectrum override inputs.
- `NS_X4_3_RAWLANE0` and `RAWLANE1`: raw per-lane PCS/FSM/AON/IRQ/PMA/TX/RX defaults, ending partway through lane 1 AON adaptation controls.

## Important Macro Groups

The common-memory register groups are mostly opaque generated names with a single `DATA` field in `nbio_6_1_sh_mask.h` (`DATA_MASK` is `0xFFFFL`). Their ordering and values matter more than semantic field names in this header. Patterns such as repeated address-like values (`0x00180`, `0x001af`, `0x0078d`) followed by data-like values indicate packed PHY initialization table material for common memory banks.

The named raw common/lane groups have clearer semantics via the corresponding shift/mask header:

- `RAWCMN_DIG_CMN_CTL` and `RAWCMN_DIG_MPLLA/MPLLB_*`: common PHY controls for PLL bandwidth and SSC override inputs. Defaults keep most override enable paths disabled, while bandwidth/SSC control defaults (`0x43`, `0x5000`) encode the reset tuning for both PLLs.
- `RAWLANE*_DIG_PCS_XF_TX_*` and `RAWLANE*_DIG_PCS_XF_RX_*`: PCS cross-function override and PCS input/output registers. RX PCS input masks include rate, width, power state, low-power detect, CDR/VCO, AFE/DFE adaptation enable/request/continuous bits, off-cancel continuous state, and reset. RX equalization fields include attenuation, VGA gain, CTLE boost/pole, DFE tap, adaptation acknowledge, figure-of-merit, and TX preset direction feedback.
- `RAWLANE*_DIG_FSM_*`: fast-path FSM and calibration status defaults for RX startup calibration, AFE/DFE calibration/adaptation, bypass/reference-level/IQ calibration, TX common-mode, RX detect, RX power-up, VCO wait/calibration, and common calibration status.
- `RAWLANE*_DIG_AON_*`: always-on calibration and adaptation storage, including AFE/DFE offset defaults (`0x80` neutral midpoint in many fields), phase adjust, MPLL coarse tune, resistor tune values, initial power-up done, RX adaptation result/status fields, slicer controls, and AON adaptation control registers.
- `RAWLANE0_DIG_IRQ_CTL_*`: reset, RX reset/request/rate/pstate/adaptation IRQ status/clear/mask defaults. The reset return request default is asserted (`0x1`); interrupt status, clear, and mask defaults are otherwise zero in this slice.
- `RAWLANE0_DIG_PMA_XF_*`: PMA lane/support/TX/RX override and input defaults. Lane override in/out defaults are `0x3`, while PMA TX/RX override paths are mostly disabled/zero.
- `RAWLANE0_DIG_TX_CTL_*` and `RAWLANE0_DIG_RX_CTL_*`: TX FSM/clock and RX FSM/LOS/data-enable controls. The TX FSM default `0xDE` enables selected RX-detect allowances and encodes MPLL-off wait timing; TX clock default enables the TX clock. RX LOS mask and RX data-enable override defaults are nonzero tuning constants.

## Control Flow

There is no runtime control flow in this range. At compile time the preprocessor makes these default values available to code that includes `nbio_6_1_default.h`. The observed direct includes are:

- `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, which also includes the offset, shift/mask, and SMN headers and uses NBIO register macros with `RREG32_*`, `WREG32_*`, and `REG_SET_FIELD` helpers.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h`, an aggregate Vega10 include that exposes NBIO default/offset/mask constants to powerplay code.

In normal driver flow, NBIO v6.1 code reads and writes hardware registers through SOC15/SMN access helpers. This chunk supplies constants only; any sequencing, polling, and side effects live in the consumers that use the matching offset/mask/SMN definitions.

## State and Persistence

The macros are immutable compile-time constants. They do not allocate memory, cache state, persist user data, or directly touch hardware. The state they describe is hardware reset/default state for NBIO/PCIe PHY registers. When consumers write these values to hardware, the persisted state is in device registers and is lost or reset according to GPU reset, power management, suspend/resume, or PCIe link reinitialization behavior.

Because many values tune analog/PHY behavior, the source file acts as persistent source-of-truth metadata for ASIC-specific defaults. Any change to a constant can alter link training, PLL behavior, receiver adaptation, power-state transition timing, interrupt masking, or calibration defaults even though this header itself has no executable path.

## Dependencies and Integration Points

This chunk depends on register naming consistency across the NBIO 6.1 generated headers:

- `nbio_6_1_offset.h` and `nbio_6_1_smn.h` provide register addresses/SMN identifiers for the same symbolic register names.
- `nbio_6_1_sh_mask.h` provides field masks and shifts. For the memory-bank registers in this chunk, the common field is typically a 16-bit `DATA` mask. For PCS/FSM/AON/IRQ/PMA/TX/RX controls, the shift/mask header exposes meaningful fields used by register access helpers.
- `nbio_v6_1.c` integrates the header into the AMDGPU NBIO block implementation alongside runtime register access macros.
- `vega10_inc.h` makes the generated defaults available to Vega10 powerplay/hardware-manager code.

The names also overlap conceptually with Display Core PHY/DPCS raw-lane register families (`RAWLANE*_DIG_PCS_XF_*` appears in display encoder headers), but this file's namespace is NBIO/PCIe PHY, not DC link encoder programming.

## Risks

- Generated-header drift: default, offset, SMN, and shift/mask headers must remain synchronized. A renamed or reordered default macro without matching address/mask changes can silently break consumers or diagnostics.
- Opaque memory-bank values: `RAWCMN*_DIG_MEM_CMN*` macros expose only `DATA`; reviewers cannot infer safety from field names. Changes require hardware table provenance or comparison against generated register specs.
- PHY tuning sensitivity: defaults around MPLL bandwidth/SSC, RX adaptation, DFE/CTLE offsets, slicer control, LOS masking, and TX/RX power-state timing can affect PCIe link stability across speeds, lanes, boards, and suspend/resume paths.
- Partial-lane coverage in this chunk: the selected line range ends inside `RAWLANE1_DIG_AON_*`. Per-file analysis must merge adjacent chunks before drawing conclusions about all lanes or the full x4 instance.
- Include bloat/compile coupling: the header is very large and included by low-level driver and powerplay aggregate headers. Macro name collisions or accidental edits can have broad compile impact even when no C code changes.

## Test Signals

Useful validation signals for changes touching this region include:

- Build coverage for AMDGPU with NBIO 6.1/Vega10 paths enabled, catching missing macro names or inconsistent generated headers.
- Static comparison against regenerated `nbio_6_1_default.h`, `nbio_6_1_offset.h`, `nbio_6_1_sh_mask.h`, and `nbio_6_1_smn.h` from the same register database.
- Boot/probe logs on Vega10-class hardware confirming AMDGPU initialization, NBIO setup, and powerplay initialization complete without register access faults.
- PCIe link training and stability checks: negotiated generation/width, retrain events, AER errors, link down/up events, and suspend/resume or GPU reset behavior.
- Stress tests that exercise PCIe traffic and power transitions, including runtime power management, clock gating/light sleep, interrupt delivery, doorbell usage, and high-throughput DMA.
- Hardware diagnostics for PHY calibration/adaptation status where available, especially RX adaptation done/FOM/status fields and IRQ status bits for reset/rate/pstate/adaptation events.

### subset-b-003002: lines 19895-22340

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h lines 19895-22340

## Scope

This chunk is the 2,446-line tail of the generated AMDGPU NBIO 6.1 default-value header. It contains C preprocessor constants and the file-closing `#endif` for `_nbio_6_1_DEFAULT_HEADER`. There are no C functions, structs, enums, global variables, allocations, locks, loops, branches, or direct I/O operations in this range.

The range starts in the middle of a DesignWare E12MP PHY x4 default block for `smnDWC_E12MP_PHY_X4_NS_X4_3_RAWLANE1`, continues through lane 2, lane 3, shared `SUPX`, `LANEX`, and `RAWLANEX` PHY defaults, then covers the `KPFIFO3` and `KPNP3` link/PHY directory defaults, per-VF NBIF/BIF defaults for virtual functions 0 through 15, final SYSHUB indirect defaults, and the closing include guard.

Although this repository path is under a `ceph-client` source tree, this file is AMD GPU register metadata for DRM/AMDGPU. It does not implement Ceph distributed-filesystem behavior.

## Purpose

`nbio_6_1_default.h` publishes generated reset/default values for registers in the NBIO 6.1 IP block. Runtime code combines these `_DEFAULT` macros with sibling offset and shift/mask headers when it needs generated hardware metadata for initialization, diagnostics, register programming, or generated-table consistency.

This chunk supplies defaults for several hardware areas:

- `smnDWC_E12MP_PHY_X4_NS_X4_3_RAWLANE1` tail and `RAWLANE2`/`RAWLANE3` full lane defaults: PCS/PMA transfer overrides, RX/TX override inputs and outputs, receive adaptation state, AON calibration offsets, DFE tap defaults, IRQ status/clear/mask defaults, PMA lane override defaults, TX/RX finite-state-machine controls, loss-of-signal masking, and RX data-enable override defaults.
- `smnDWC_E12MP_PHY_X4_NS_X4_3_SUPX`: shared PHY/supervisor defaults such as ID code values, reference-clock overrides, MPLLA/MPLLB override inputs, PLL power-control timing thresholds, spread-spectrum clocking defaults, analog override/status defaults, and RTUNE control/status defaults.
- `smnDWC_E12MP_PHY_X4_NS_X4_3_LANEX`: generic per-lane defaults for ASIC lane override inputs, TX/RX power states, power-up timings, LBERT controls, RX VCO calibration, CDR controls, adaptation configuration/status, DFE/slicer offsets, RX statistic counters, and link counters.
- `smnDWC_E12MP_PHY_X4_NS_X4_3_RAWLANEX`: generic raw-lane defaults mirroring the concrete raw-lane register families for PCS transfer, FSM, AON adaptation, IRQ, PMA transfer, and TX/RX control defaults.
- `nbio_lcu_kpfifo_kpfifo3_kpfifo_dir`: `KPFIFO3` primary TX FIFO and PCS/PMA soft-reset defaults.
- `nbio_lcu_kpnp_kpnp3_kpnp_dir`: `KPNP_SNPS3` PHY information, lane request/status, PMA control, PHY/lane soft-reset, and reset-control defaults.
- `nbio_nbif_bif_bx_dev0_epf0_vf{0..15}_SYSPFVFDEC`: per-virtual-function indirect MMIO index/data register defaults.
- `nbio_nbif_bif_bx_dev0_epf0_vf{0..15}_BIFPFVFDEC1`: per-virtual-function BIF defaults for BME status, atomic error log, doorbell self-ring GPA aperture base/control, HDP coherency flush controls, GPU HDP flush request/done, transaction-pending status, transmit/receive mailbox buffers, mailbox control/interrupt control, and VM/HV mailbox state.
- `syshub_mmreg_ind_syshubind`: SYSHUB deep-sleep and clock-domain defaults, DMA/HST QoS and client-control defaults, clock-gating controls, scratch/default mask values, and NIC400 function-modifier defaults.

Most values are zero reset/defaults. Non-zero defaults in this range are the important review anchors: lane/PHY tuning values such as `0x80` DFE/AON offsets, RX/TX control values, PLL timing thresholds, KPNP PMA and lane reset defaults, VF doorbell aperture control `0x00000100`, SYSHUB QoS `0x0000001e`, SYSHUB DMA client control `0x20200000`, clock-gating/deep-sleep timer values, and the PHY/shared ID defaults.

## Important APIs, Types, And Functions

This chunk defines no callable APIs or C types. The public interface is the generated macro namespace. The macros are compile-time constants named after hardware registers with a `_DEFAULT` suffix.

The matching register addresses live in `nbio_6_1_offset.h`, and field layouts live in `nbio_6_1_sh_mask.h`. Consumers normally use the offset and field headers with AMDGPU helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `WREG32_FIELD15`, and `REG_SET_FIELD`. This default header is included directly by `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c` and by Vega power-management include bundles such as `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h`.

Relevant integration examples in the source tree include:

- `nbio_v6_1.c` includes `nbio_6_1_default.h`, `nbio_6_1_offset.h`, `nbio_6_1_sh_mask.h`, and `nbio_6_1_smn.h`, then programs NBIO doorbell apertures, HDP flush remapping, interrupt control, PCIe ASPM/LTR, and clock-gating behavior.
- `nbio_v6_1_set_reg_remap()` uses the VF0 HDP memory coherency flush register offset as the SR-IOV VF/MMIO remap fallback, tying the per-VF register family in this chunk to KFD/MMIO remapping behavior.
- `mxgpu_ai.c` uses NBIO 6.1 offset and mask metadata for host/VF mailbox handling in SR-IOV paths. This chunk supplies the reset/default values for the analogous per-VF mailbox buffer/control registers.
- `psp_v3_1.c`, `vega10_inc.h`, and `vega12_inc.h` include NBIO 6.1 register headers as part of the Vega ASIC register contract used by firmware, PSP, and power-management paths.

## Control Flow

There is no local control flow in the header. The effective runtime flow is external:

1. ASIC-specific AMDGPU, PSP, virtualization, or power-management code includes the generated NBIO 6.1 headers.
2. The caller selects a register through the offset header, optionally compares or documents the reset value through this default header, and composes fields with the shift/mask header.
3. Driver code reads or writes the hardware through SOC15, PCIe, SMN, or MMIO helper paths.
4. Hardware, firmware, PCIe link-training logic, SR-IOV virtualization, HDP cache-coherency flush machinery, or SYSHUB fabric state observes the register value.

The PHY-related defaults affect link bring-up indirectly: firmware and low-level hardware sequencing can use reset values for PLLs, lane power states, CDR, RX adaptation, DFE offsets, PMA/PCS transfer, soft reset, and IRQ signaling. The VF BIF defaults affect the initial state seen by PF/VF mailbox and HDP flush paths. SYSHUB defaults affect fabric clocking, QoS, idle/deep-sleep, and NIC400 behavior before any explicit driver override.

## State And Persistence Behavior

The file stores no software state and persists nothing to disk. It names hardware reset/default state. Persistence is therefore governed by GPU reset domains, power gating, firmware initialization, PCI function-level reset, hot reset, suspend/resume, SR-IOV PF/VF lifecycle, and explicit driver or firmware writes.

The state represented by this chunk includes:

- PCIe/PHY lane electrical and protocol state: CDR, VCO calibration, DFE offsets, slicer controls, RX adaptation, lane power states, loopback/BERT controls, IRQ status/clear/mask bits, and PCS/PMA override wiring.
- Shared PHY and PLL state: reference-clock selection, MPLLA/MPLLB override inputs, power-up/down timing thresholds, spread-spectrum clocking, RTUNE controls, and analog status/override defaults.
- Link-controller sideband state: KPFIFO3 FIFO/lane control and KPNP3 lane request/status, PMA control, soft-reset, and reset-control defaults.
- Per-VF BIF state: VF-local indirect MMIO selector/data registers, doorbell self-ring GPA aperture programming, HDP coherency flush request/done state, transaction-pending state, and PF/VF mailbox buffers/control.
- SYSHUB fabric state: deep-sleep controls, QoS/client-control defaults for DMA/HST clocks, clock-gating controls, scratch/mask defaults, and NIC400 function modifiers.

The `_DEFAULT` constants do not identify which registers are read-only, write-one-to-clear, sticky, firmware-owned, volatile status, or driver-programmable. That information must come from field masks, hardware documentation, and the consuming code paths.

## Dependencies And Integration Points

Direct dependencies are the generated NBIO 6.1 sibling headers:

- `nbio_6_1_offset.h` provides addresses/base indices for the same register names without `_DEFAULT`.
- `nbio_6_1_sh_mask.h` provides field shifts and masks, including the field definitions for KPFIFO, KPNP, mailbox/control, HDP flush, SYSHUB clock-gating, and PHY control/status registers.
- `nbio_6_1_smn.h` provides SMN address constants used by PCIe/NBIO paths in the same IP generation.

Broader integration points are:

- AMDGPU NBIO 6.1 initialization and function table plumbing through `nbio_v6_1_funcs`.
- PCIe link management, ASPM/LTR programming, and clock-gating behavior in `nbio_v6_1.c`.
- Doorbell aperture setup, self-ring doorbell aperture programming, and interrupt-ring doorbell range setup.
- HDP coherency flushing and KFD MMIO remapping, including SR-IOV-specific VF register remap behavior.
- SR-IOV/MxGPU mailbox communication between guest VF and host/PF firmware or hypervisor components.
- PSP and power-management include bundles for Vega-generation ASICs.
- Low-level firmware or bring-up tooling that validates generated PHY reset values against the hardware register database.
- SYSHUB fabric clock/QoS/idle behavior and NIC400 interconnect integration.

## Risks And Edge Cases

- Generated default drift can be hard to catch in ordinary C builds. Macro names may remain valid while default values silently change, leaving hardware bring-up, diagnostics, or generated-register validation inconsistent with the ASIC database.
- This chunk starts mid-block. The final per-file report should merge adjacent chunks to describe the complete `DWC_E12MP_PHY_X4_NS_X4_3` PHY default set rather than treating line 19895 as a natural hardware boundary.
- The DWC PHY defaults include sensitive analog/PHY tuning values. Incorrect PLL timing, RX adaptation, CDR, VCO calibration, DFE, slicer, LOS mask, PMA/PCS override, or lane power-state defaults can affect PCIe link training, stability, speed negotiation, error rate, low-power transitions, and resume behavior.
- Many PHY status and IRQ defaults are zero, while `RESET_RTN_REQ` defaults to one in the raw-lane IRQ block. Consumers must not assume every zero-valued default means "safe to write zero"; status/clear and request semantics may be write-sensitive.
- Per-VF blocks are highly repetitive from VF0 through VF15. Mechanical generation or manual edits can accidentally change one VF while leaving the others unchanged. VF0 is especially important because current NBIO/KFD remap logic references VF0 HDP coherency flush offsets.
- VF mailbox defaults are all zero, which is a sane reset state, but mailbox runtime protocols rely on strict valid/ack ownership and interrupt-control semantics. Treating default values as protocol state after reset can race with host firmware or hypervisor updates.
- `DOORBELL_SELFRING_GPA_APER_CNTL_DEFAULT` is `0x00000100` for every VF. Any incorrect interpretation of that non-zero reset/default can affect doorbell aperture enable/mode/size programming, guest isolation, or self-ring notification behavior.
- HDP flush request/done and transaction-pending defaults are stateful hardware synchronization points. Polling code must handle reset, VF lifecycle, and timeout cases rather than relying only on the default constants.
- SYSHUB defaults such as DMA QoS `0x1e`, client control `0x20200000`, clock-gating `0x00082000`, and MGCG `0x80` can influence fabric latency, power, and idle detection. Misaligned defaults can cause performance, power, or suspend/resume regressions.
- The closing `#endif` is part of this chunk. Any truncation before it breaks the include guard and should fail compilation; duplicate or misplaced definitions around the tail can create subtle macro redefinition or stale-metadata hazards.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Build AMDGPU with NBIO 6.1/Vega support enabled. Syntax errors, missing include guard closure, or macro redefinition issues should surface at compile time.
- Run generated-register consistency checks against the authoritative NBIO 6.1 register database, specifically covering the `DWC_E12MP_PHY_X4_NS_X4_3` lane/shared/generic defaults, `KPFIFO3`, `KPNP3`, VF0-VF15 BIF defaults, and final SYSHUB indirect defaults.
- Boot affected Vega/NBIO 6.1 hardware and confirm PCIe link training, negotiated width/speed, ASPM/LTR behavior, suspend/resume, and warm-reset behavior remain stable.
- Exercise SR-IOV/MxGPU flows with multiple VFs. Check PF/VF mailbox valid/ack behavior, mailbox interrupts, guest reset, VF teardown/recreate, and host-driven messages.
- Validate KFD/MMIO remapping and HDP coherency flush behavior, including the VF path that uses `BIF_BX_DEV0_EPF0_VF0_HDP_MEM_COHERENCY_FLUSH_CNTL` as the remap fallback.
- Run graphics, compute, and DMA workloads that stress doorbells, interrupt rings, SDMA, and HDP flushes while monitoring for hangs, stale cache/coherency symptoms, and timeout diagnostics.
- Check power-management and fabric behavior through clock-gating, deep-sleep, and SYSHUB idle paths, especially after runtime suspend/resume and under mixed DMA/display/compute load.
- For PHY-specific modifications, use hardware link diagnostics and error counters to verify CDR/VCO/adaptation behavior, link error rate, retraining frequency, and low-power lane transitions.

## Chunk-Specific Notes For Merge

This is the final chunk of `nbio_6_1_default.h` and includes the closing `#endif`. It should be merged with preceding chunks before producing the final per-file research document because the first lines here continue an existing DWC E12MP PHY raw-lane block. Preserve that this slice covers the tail of the generated NBIO 6.1 default-value ABI: DWC PHY x4 instance 3 lane/shared/generic defaults, KPFIFO3/KPNP3 defaults, all `BIF_BX_DEV0_EPF0_VF0` through `VF15` per-VF defaults, and final SYSHUB indirect defaults.
