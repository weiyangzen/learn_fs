# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h lines 5829-8700

## Scope

This chunk is a generated AMD NBIO 2.3 default-register header segment. It contains preprocessor constants only: each `*_DEFAULT` macro names the reset/default value for a concrete NBIO register or PCI configuration-space register. There are no C functions, structs, runtime branches, loops, locks, allocations, or direct MMIO operations in this range.

The range starts in the middle of the `nbio_nbif0_bif_cfg_dev0_epf0_vf23_bifcfgdecp` address block, so it only contains the tail defaults for `smnBIF_CFG_DEV0_EPF0_VF23_*`. It then covers complete `smn` defaults for virtual functions `VF24` through `VF30`, the USB MSI-X table/PBA defaults, PCIe port/link/default-control blocks, the `cfgBIF_CFG_DEV0_SWDS0_*` downstream-switch configuration defaults, and complete `cfg` defaults for virtual functions `VF0` through `VF9`. The final covered source line is only the `// addressBlock: nbio_nbif0_bif_cfg_dev0_epf0_vf10_bifcfgdecp` marker; the `VF10` defaults begin after this chunk.

Major covered families are:

- Tail of `smnBIF_CFG_DEV0_EPF0_VF23_*` MSI, MSI-X, vendor-specific, AER, ATS, and ARI defaults.
- Full `smnBIF_CFG_DEV0_EPF0_VF24_*` through `smnBIF_CFG_DEV0_EPF0_VF30_*` virtual-function PCIe configuration defaults.
- `smnPCIEMSIX_VECT0_*` through `smnPCIEMSIX_VECT255_*`, four default registers per MSI-X vector: low address, high address, message data, and vector control.
- `smnPCIEMSIX_PBA_0_DEFAULT` through `smnPCIEMSIX_PBA_7_DEFAULT`.
- `smnPCIEP_*`, `smnPCIE_TX_*`, `smnPCIE_RX_*`, `smnPCIE_LC_*`, flow-control, error-injection, SR-IOV, clock/power, and save/restore defaults for the PCIe port-side directory block.
- `smnPCIE_*`, performance-counter, PRBS, software-reset, CPM, aperture, lane-counter, power-gating, RX margining, and presence-detect defaults for the broader PCIe directory block.
- `cfgBIF_CFG_DEV0_SWDS0_*` PCIe downstream-switch defaults, including bridge config header fields, PCIe capabilities, virtual-channel capability defaults, AER defaults, secondary PCIe capability, ACS, data-link feature, 16 GT/s PHY capability placeholders, and per-lane equalization/margining defaults.
- `cfgBIF_CFG_DEV0_EPF0_VF0_0_*` through `cfgBIF_CFG_DEV0_EPF0_VF9_0_*` virtual-function PCIe configuration defaults.

## Purpose

The purpose of this header segment is to publish ASIC reset/default values for NBIO 2.3 hardware registers so driver code, diagnostics, generated register tooling, and bring-up checks have a single symbolic view of expected initial state. The companion `nbio_2_3_offset.h` header identifies register offsets, and `nbio_2_3_sh_mask.h` identifies field positions. This default header supplies the value expected before driver or firmware programming changes the register.

For the virtual-function blocks, these defaults describe SR-IOV VF PCI configuration space as exposed by the NBIO/BIF register database. Most fields default to zero because VF identity, BARs, MSI state, AER status, ATS control, ARI state, and error logs are either disabled, assigned by later software/firmware, or status-like. The repeated nonzero defaults encode the static capability list shape:

- VF config blocks use `CAP_PTR_DEFAULT` of `0x00000048`.
- PCIe capability list defaults commonly use `0x0000a000`, with `PCIE_CAP_DEFAULT` of `0x00000002`.
- Link capability defaults use `0x00000d04`, and Link Capability 2 defaults use `0x0000001e`.
- Device Capability 2 defaults use `0x00010000`.
- MSI capability list defaults use `0x0000c000`, and VF MSI message control defaults usually use `0x00000082`.
- Vendor-specific enhanced capability list defaults use `0x11000000`.
- Advanced Error Reporting enhanced capability list defaults use `0x20020000`.
- ATS enhanced capability list defaults use `0x2c000000`.
- VF adapter ID defaults are `0x73101002` for the full VF blocks in this chunk.

For the PCIe directory and port blocks, the defaults describe low-level link, transaction, flow-control, clock/power, reset, debug, and training behavior. These values are not policy chosen by C code in this file; they are generated hardware metadata that driver code may compare with, rely on as reset baseline, or override through MMIO programming paths.

For the USB MSI-X table and PBA blocks, all defaults are zero. This models unprogrammed MSI-X vector address/data/control entries and clear pending bits before software assigns interrupt vectors.

## Important Macro Families

### SR-IOV VF Config Defaults

The chunk contains two VF naming styles:

- `smnBIF_CFG_DEV0_EPF0_VF23_*` tail and full `smnBIF_CFG_DEV0_EPF0_VF24_*` through `VF30_*`.
- `cfgBIF_CFG_DEV0_EPF0_VF0_0_*` through `VF9_0_*`.

The full VF blocks each expose the same PCI config-space default layout:

- Type/header identity fields: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE`, `LATENCY`, `HEADER`, and `BIST`.
- BAR and ROM defaults: `BASE_ADDR_1` through `BASE_ADDR_6`, `CARDBUS_CIS_PTR`, `ROM_BASE_ADDR`, and `ADAPTER_ID`.
- Interrupt and capability-list pointers: `CAP_PTR`, `INTERRUPT_LINE`, `INTERRUPT_PIN`, `MIN_GRANT`, and `MAX_LATENCY`.
- PCIe capability registers: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- MSI/MSI-X defaults: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, message address/data fields, mask and pending fields, and MSI-X capability/table/PBA fields.
- Extended capabilities and error reporting: vendor-specific enhanced capability, AER status/mask/severity/log fields, TLP prefix logs, ATS capability/control, and ARI capability/control.

Most VF control, status, address, and log defaults are zero. The repeated nonzero capability constants are important because they define the PCI capability chain and the advertised static capability baseline for each VF. Incorrect values here can make a VF appear to have a malformed PCIe capability list, bad MSI capability state, wrong link capability, or incorrect extended capability chaining.

### USB MSI-X Table and PBA

The `nbio_nbif0_pciemsix_0_usb_MSIXTDEC` block defines 256 MSI-X vector entries:

- `smnPCIEMSIX_VECTn_ADDR_LO_DEFAULT`
- `smnPCIEMSIX_VECTn_ADDR_HI_DEFAULT`
- `smnPCIEMSIX_VECTn_MSG_DATA_DEFAULT`
- `smnPCIEMSIX_VECTn_CONTROL_DEFAULT`

Every entry defaults to `0x00000000`. This is the reset state for an unprogrammed MSI-X table: no target address, no message data, and no vector-control state set by this generated default table. The `nbio_nbif0_pciemsix_0_usb_MSIXPDEC` block adds `smnPCIEMSIX_PBA_0_DEFAULT` through `PBA_7_DEFAULT`, also all zero, representing a clear pending-bit array.

This family is stateful at runtime even though this header is static. Once Linux configures MSI-X, vector address/data/control and pending bits are hardware/software state, not persistent constants from this header.

### PCIe Port Directory Defaults

The `nbio_pcie0_pswusp0_pciedir_p` address block covers port-side PCIe defaults. Nonzero values include:

- `smnPCIEP_PORT_CNTL_DEFAULT` at `0x06000009`.
- `smnPCIE_TX_CNTL_DEFAULT` at `0x00408000`, `smnPCIE_TX_REQUEST_NUM_CNTL_DEFAULT` at `0x02000000`, `smnPCIE_TX_REPLAY_DEFAULT` at `0x00480003`, `smnPCIE_TX_CNTL_2_DEFAULT` at `0x00000004`, and `smnPCIE_TX_CREDITS_FCU_THRESHOLD_DEFAULT` at `0x03330333`.
- Flow-control defaults such as `smnPCIE_FC_P_DEFAULT` and `smnPCIE_FC_P_VC1_DEFAULT` at `0x00020008`, and `smnPCIE_FC_NP_DEFAULT` at `0x00020002`.
- Error/link-control defaults such as `smnPSWUSP0_PCIE_ERR_CNTL_DEFAULT` at `0x00000500`, `smnPSWUSP0_PCIE_RX_CNTL_DEFAULT` at `0x01084000`, `smnPCIE_LC_CNTL_DEFAULT` at `0x40010050`, `smnPCIE_LC_TRAINING_CNTL_DEFAULT` at `0x94009880`, `smnPCIE_LC_LINK_WIDTH_CNTL_DEFAULT` at `0xda800006`, `smnPCIE_LC_N_FTS_CNTL_DEFAULT` at `0x00ffc20c`, and `smnPSWUSP0_PCIE_LC_SPEED_CNTL_DEFAULT` at `0x10000200`.
- Link-control extension defaults such as `smnPSWUSP0_PCIE_LC_CNTL2_DEFAULT` at `0x96180280`, `smnPCIE_LC_CDR_CNTL_DEFAULT` at `0x01018060`, `smnPCIE_LC_CNTL3_DEFAULT` at `0xa850a020`, `smnPCIE_LC_CNTL4_DEFAULT` at `0x0340048c`, `smnPCIE_LC_CNTL5_DEFAULT` at `0x40200000`, `smnPCIE_LC_CNTL6_DEFAULT` at `0x8a000090`, `smnPCIE_LC_CNTL7_DEFAULT` at `0x010002ee`, `smnPCIE_LC_CNTL8_DEFAULT` at `0x00400000`, `smnPCIE_LC_CNTL9_DEFAULT` at `0xf0ffec00`, `smnPCIE_LC_CNTL10_DEFAULT` at `0x30000003`, `smnPCIE_LC_CNTL11_DEFAULT` at `0x00602000`, and `smnPCIE_LC_CNTL12_DEFAULT` at `0x00000017`.
- Link management mask/default state such as `smnPCIE_LINK_MANAGEMENT_MASK_DEFAULT` at `0x00003fff`.
- Power/substate and ECC defaults such as `smnPCIE_LC_L1_PM_SUBSTATE_DEFAULT` at `0x04540000` and `smnPCIEP_BCH_ECC_CNTL_DEFAULT` at `0x00000100`.

These defaults align with runtime code in `amdgpu/nbio_v2_3.c`, which uses direct `smn...` addresses for PCIe config, link training, ASPM, clock gating, LTR, and workaround programming. The header is not where those policies execute, but it documents generated baseline values for the same hardware domain.

### PCIe Directory Defaults

The `nbio_pcie0_pciedir` address block defines defaults for the broader PCIe directory:

- Core control/config/debug: `smnPCIE_CNTL_DEFAULT` is `0x80811000`, `smnPCIE_CONFIG_CNTL_DEFAULT` is `0x0000000f`, `smnPCIE_DEBUG_CNTL_DEFAULT` is `0x00000001`, `smnPCIE_CNTL2_DEFAULT` is `0x0e000109`, `smnPCIE_CI_CNTL_DEFAULT` is `0x40000010`, and `smnPCIE_WPR_CNTL_DEFAULT` is `0x00000005`.
- Link/power defaults: `smnPCIE_LC_PM_CNTL_DEFAULT` is `0x76543210`, `smnPCIE_P_CNTL_DEFAULT` is `0x00850000`, `smnPCIE_P_RCV_L0S_FTS_DET_DEFAULT` is `0x000000ff`, `smnPCIE_RX_AD_DEFAULT` is `0x00000003`, and `smnPCIE_SDP_CTRL_DEFAULT` is `0x00000002`.
- HIP, strap, PRBS, performance, last-TLP, and tracking registers mostly default to zero, except `smnPCIE_HIP_REG8_DEFAULT` at `0x00008000`.
- Software reset defaults include `smnSWRST_GENERAL_CONTROL_DEFAULT` at `0x02001002`, `smnSWRST_COMMAND_1_DEFAULT` at `0x04000000`, `smnSWRST_CONTROL_0_DEFAULT` at `0x5600ff00`, `smnSWRST_CONTROL_1_DEFAULT` at `0xc220ffff`, `smnSWRST_CONTROL_4_DEFAULT` at `0x5c00ff01`, `smnSWRST_CONTROL_5_DEFAULT` at `0xfe20ffff`, `smnSWRST_CONTROL_6_DEFAULT` at `0x000007ff`, and `smnSWRST_EP_CONTROL_0_DEFAULT` at `0x00000500`.
- Clock/power and margining defaults include `smnCPM_CONTROL_DEFAULT` at `0x0080ca00`, `smnPCIE_PGSLV_CNTL_DEFAULT` at `0x00000004`, `smnLC_CPM_CONTROL_1_DEFAULT` at `0x00000001`, and `smnPCIE_LC_DEBUG_CNTL_DEFAULT` at `0x00010000`.

This family is the default baseline for PCIe operations that `nbio_v2_3.c` later changes through `RREG32_PCIE`, `WREG32_PCIE`, `REG_SET_FIELD`, and `WREG32_SOC15` helpers.

### SWDS0 Downstream-Switch Config Defaults

The `cfgBIF_CFG_DEV0_SWDS0_*` block represents a PCIe downstream switch/bridge config-space default set. It differs from the VF blocks because several bridge and downstream-port fields have meaningful nonzero defaults:

- `VENDOR_ID_DEFAULT` is `0x00001002`.
- `SUB_CLASS_DEFAULT` is `0x00000004`, and `BASE_CLASS_DEFAULT` is `0x00000006`, matching a PCI bridge class layout.
- `INTERRUPT_LINE_DEFAULT` is `0x000000ff`.
- `PMI_CAP_DEFAULT` is `0x0000c800`.
- `PCIE_CAP_LIST_DEFAULT` is `0x0000a000`, and `PCIE_CAP_DEFAULT` is `0x00000062`.
- `DEVICE_CNTL_DEFAULT` is `0x00002810`.
- `LINK_STATUS_DEFAULT` is `0x00002001`, and `LINK_CNTL2_DEFAULT` is `0x00000004`.
- MSI message control defaults to `0x00000080`.
- Virtual-channel enhanced capability list defaults to `0x14000000`, with `VC0_RESOURCE_CNTL_DEFAULT` at `0x000000fe`.
- Device serial number, AER, secondary PCIe, ACS, data-link feature, 16 GT/s PHY, and margining enhanced capability list defaults are represented.
- AER masks/severity are nonzero: uncorrectable error mask `0x00400000`, uncorrectable error severity `0x00440010`, and correctable error mask `0x00006000`.
- PCIe lane equalization defaults for lanes 0 through 15 are `0x00007f7f`.
- PCIe margining lane control defaults for lanes 0 through 15 are `0x00009c38`.

These defaults define the static config-space and capability baseline for the downstream-switch entity. They are sensitive because PCI enumeration, topology reporting, AER policy, lane equalization, and margining behavior can depend on these register reset values.

## APIs, Types, and Functions

This chunk defines no APIs, types, or functions in the C sense. Its exported interface is the set of macro names and literal constants. The effective API contract is naming consistency with the generated AMDGPU register headers:

- `nbio_2_3_offset.h` supplies the matching `mm...`, `smn...`, and `cfg...` register offsets or addresses.
- `nbio_2_3_sh_mask.h` supplies the matching field shift and mask macros.
- Driver code includes all three headers and uses the names through SOC15 and PCIE access helpers.

The important "callers" are preprocessor consumers. If a macro is renamed, deleted, or assigned a wrong value, the build may fail only when a consumer references it directly. If a wrong default remains syntactically valid, it can silently corrupt diagnostics, default-state checks, or generated-table consumers.

## Control Flow and State Behavior

There is no executable control flow in this chunk. There are no conditionals, no state machines, and no software-side persistence.

The state represented by the macros is hardware register state:

- Reset/default configuration state for SR-IOV VF PCI config spaces.
- Reset/default MSI-X table and pending-bit-array state.
- Reset/default PCIe link, transaction, flow-control, power, clock, reset, and debug state.
- Reset/default downstream-switch PCIe bridge/capability state.
- Reset/default status/log placeholders for AER, ATS, ARI, TLP prefix logs, last TLPs, PRBS counters, performance counters, and software reset status fields.

Runtime persistence belongs to hardware and to the driver/firmware programming sequence. For example, MSI/MSI-X vector registers are zero in this header but become live interrupt-routing state after PCI/MSI setup. PCIe link-control defaults become runtime link-training, ASPM, clock-gating, and workaround state once `nbio_v2_3.c` writes the corresponding registers. AER status/log fields default to zero but can later hold error state that should not be confused with immutable software constants.

## Dependencies and Integration Points

Direct dependencies are the generated AMD register-header convention and the matching NBIO 2.3 files:

- `drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h` for register offsets and addresses.
- `drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h` for field masks and shifts.
- `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, which includes `nbio_2_3_default.h`, `nbio_2_3_offset.h`, and `nbio_2_3_sh_mask.h`.

Observed runtime integration in `nbio_v2_3.c` includes:

- PCIe indirect/data access helpers via `nbio_v2_3_get_pcie_index_offset()` and `nbio_v2_3_get_pcie_data_offset()`, returning the `mmPCIE_INDEX2` and `mmPCIE_DATA2` offsets from the same NBIO generation.
- PCIe config initialization in `nbio_v2_3_init_registers()`, which reads and updates `smnPCIE_CONFIG_CNTL`.
- Medium-grain clock gating in `nbio_v2_3_update_medium_grain_clock_gating()`, which reads and writes `smnCPM_CONTROL`.
- Light sleep in `nbio_v2_3_update_medium_grain_light_sleep()`, which reads and writes `smnPCIE_CNTL2`.
- ASPM and LTR programming in `nbio_v2_3_enable_aspm()`, `nbio_v2_3_program_ltr()`, and `nbio_v2_3_program_aspm()`, which program registers in the same PCIe/link-control family represented by `smnPCIE_LC_CNTL*`, `smnPSWUSP0_PCIE_LC_CNTL2`, `smnBIF_CFG_DEV0_EPF0_DEVICE_CNTL2`, and related defaults.
- Link-width workarounds in `nbio_v2_3_apply_lc_spc_mode_wa()` and `nbio_v2_3_apply_l1_link_width_reconfig_wa()`, which interact with `smnPCIE_LC_LINK_WIDTH_CNTL` and `smnPCIE_LC_CNTL6`.
- SR-IOV-aware register-remap behavior in `nbio_v2_3_set_reg_remap()`, which uses VF-related NBIO registers from the same generated family.

The header also integrates indirectly with Linux PCI enumeration, SR-IOV VF setup, MSI/MSI-X programming, AER handling, GPU reset flows, suspend/resume, and clock/power-management paths because those subsystems read or modify the hardware state whose defaults are described here.

## Risks

- Generated default drift is often silent. A wrong literal can compile cleanly but make diagnostics, reset comparisons, or generated register-table consumers trust a bad hardware baseline.
- PCI capability-list defaults are enumeration-sensitive. Bad `CAP_PTR`, `PCIE_CAP_LIST`, `MSI_CAP_LIST`, or enhanced-capability-list defaults can make a virtual function or downstream port appear to have a malformed capability chain.
- MSI/MSI-X defaults are interrupt-sensitive. Incorrect table/PBA defaults could hide stale pending state assumptions or cause a driver to mishandle vector initialization in diagnostics or emulation-like flows.
- SR-IOV VF defaults are virtualization-sensitive. Wrong VF BAR, MSI, ATS, ARI, AER, or adapter-ID defaults may only surface under VF assignment, guest probing, or reset of virtual functions.
- PCIe link-control defaults are platform-sensitive. Values in `PCIE_LC_*`, `PSWUSP0_PCIE_*`, flow-control, CDR, equalization, and speed-control registers can affect link training, ASPM, L1 substates, hotplug/removable-device behavior, and Navi-specific workarounds.
- SWDS0 AER defaults are error-reporting-sensitive. Wrong uncorrectable/correctable masks or severity values can change which PCIe errors are surfaced, masked, or classified as fatal/nonfatal.
- Lane equalization and margining defaults are signal-integrity-sensitive. Incorrect per-lane defaults may only show up on certain boards, link widths, cable/removable paths, or high-speed modes.
- Software-reset defaults are sequencing-sensitive. Bad `SWRST_*` defaults can affect reset isolation, endpoint reset, or recovery behavior if tooling or firmware relies on the generated reset baseline.
- Status and log defaults should not be treated as durable configuration. Fields such as AER status/logs, PRBS counters, last-TLP registers, and MSI-X PBA bits become live hardware state after boot.
- The chunk boundaries are artificial. The beginning omits the first part of `VF23`, and the ending includes only the `VF10` address-block marker without any `VF10` defaults.

## Test and Validation Signals

Useful validation is mostly build, register-database comparison, and hardware integration testing:

- Build AMDGPU with NBIO 2.3 support to catch missing or renamed generated macros referenced by `nbio_v2_3.c` or related register tooling.
- Compare this generated `nbio_2_3_default.h` segment with the authoritative AMD register database, especially repeated VF blocks, MSI-X vector ranges, AER masks/severity values, and per-lane SWDS0 equalization/margining defaults.
- Boot hardware using NBIO 2.3 and verify PCI enumeration, GPU device config space, bridge/downstream-port config space, and SR-IOV VF creation/probing.
- Enable and assign VFs where supported; check that guest-visible config space, MSI/MSI-X setup, ATS/ARI exposure, and VF reset behavior are consistent with expectations.
- Exercise MSI and MSI-X interrupt setup and teardown, including USB/MSI-X vectors if that block is used by the platform, and verify no stale pending bits or malformed vector-table assumptions.
- Stress PCIe link-management paths: ASPM enable/disable, LTR programming, suspend/resume, link retraining, removable-device paths, and the Navi10/Navi12 link-width workarounds in `nbio_v2_3.c`.
- Check AER behavior with controlled PCIe error injection or platform error logs, confirming SWDS0 and VF error masks/status/severity fields decode and reset as expected.
- Run GPU reset and recovery tests to exercise `SWRST_*`, endpoint reset, and doorbell/register-remap flows around NBIO.
- Validate clock-gating and light-sleep transitions by checking `CPM_CONTROL`, `PCIE_CNTL2`, and related link-control state before and after power-management operations.
- For generated-table maintenance, count the MSI-X table shape: 256 vectors with four defaults each, plus eight PBA defaults, and verify the range does not accidentally drop or duplicate a vector.

## Cross-Chunk Notes

The first covered line is already inside `VF23`; the complete `smnBIF_CFG_DEV0_EPF0_VF23_*` block must be reconciled with the previous chunk. Line 8700 is only the address-block comment for `VF10`; the actual `cfgBIF_CFG_DEV0_EPF0_VF10_0_*` defaults belong to the following chunk. The final per-file report should merge these boundaries before making whole-file statements about VF coverage.
