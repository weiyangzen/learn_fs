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
