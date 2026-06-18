# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 48959-51417

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask header segment. It exports C preprocessor constants for hardware register bit positions and masks; it contains no executable code, functions, type declarations, allocation, locking, or direct register I/O.

The range starts in the tail of the `BIF_CFG_DEV0_EPF1` PCIe multicast/SR-IOV capability area, covers the full visible `nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp` address block, enters most of the `nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp` block, and ends inside the `RCC_EP_DEV0_1_PCIE_F0_DPA_SUBSTATE_PWR_ALLOC_2` definition. It also includes RCC port-decode and endpoint PCIe control blocks for device 0 instance 1.

The chunk defines 2,134 `#define` rows across 314 distinct register-name prefixes. The interface is entirely macro based: each register field is represented by a `__SHIFT` value and a matching `_MASK` value.

## Purpose

`nbio_4_3_0_sh_mask.h` is the bitfield-layout half of AMD's generated NBIO 4.3.0 register interface. This slice lets AMDGPU code and related firmware-facing paths decode or compose NBIF/BIF PCI configuration-space and RCC endpoint register values without hard-coding bit offsets.

The main naming families are:

- `BIF_CFG_DEV0_EPF1_PCIE_*` for endpoint function 1 PCIe extended capabilities, especially multicast, LTR, ARI, SR-IOV, and VF resizable BAR controls.
- `BIF_CFG_DEV0_EPF2_*` for a complete endpoint function 2 PCI/PCIe configuration decode block.
- `BIF_CFG_DEV0_EPF3_*` for endpoint function 3 configuration decode fields through its ARI capability area.
- `RCC_DEV0_1_RCC_*` for root/control-complex port behavior, link policy, requester-ID restore, LTR, arbitration, and margining parameters.
- `RCC_EP_DEV0_1_*` for endpoint-side PCIe scratch, error interrupt, unsupported-request handling, LTR transmission, straps, and DPA state.

The companion `nbio_4_3_0_offset.h` supplies the register addresses; this file supplies the per-field shifts and masks that register helpers use after reading those addresses.

## Address Blocks and Register Coverage

Visible address-block markers in this range:

- `nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp`
- `nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp`
- `nbio_nbif0_rcc_dev0_RCCPORTDEC`
- `nbio_nbif0_rcc_ep_dev0_RCCPORTDEC`

The leading `EPF1` portion completes higher-level PCIe capability definitions:

- Multicast receive and block registers: `PCIE_MC_RCV*`, `PCIE_MC_BLOCK_ALL*`, and `PCIE_MC_BLOCK_UNTRANSLATED_*`.
- Latency Tolerance Reporting: `PCIE_LTR_ENH_CAP_LIST` and `PCIE_LTR_CAP`.
- ARI capability/control: `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL`.
- SR-IOV capability/control/status and VF layout: `PCIE_SRIOV_*`, including VF counts, first VF offset, VF stride, VF device ID, page-size masks, six VF BAR base registers, and migration-state-array offset.
- VF resizable BAR capability/control registers for VF BAR1 through VF BAR6.

The `EPF2` and `EPF3` BIF configuration blocks define standard PCI and PCIe configuration-space fields:

- Basic PCI header fields: vendor/device ID, command/status, revision/class, cache line, latency, header type, BIST, six BARs, CardBus CIS pointer, adapter/subsystem IDs, ROM BAR, capability pointer, interrupt line/pin, min grant, and max latency.
- PM and vendor capabilities: vendor capability list, writable adapter ID mirror, PMI capability list, PM capability, PM status/control, SBRN, FLADJ, and DBESL/DBESLD.
- PCIe device/link capability and control: device type, max payload/read request size, relaxed ordering, no-snoop, FLR, power states, ASPM/link disable/retrain, common clock, link speed/width, link bandwidth notification, DRS signaling, equalization, supported speed vectors, and compliance controls.
- Interrupt capabilities: MSI and MSI-X capability headers, MSI message control/address/data/mask/pending registers, MSI extended data, 64-bit variants, MSI-X table control, table BIR/offset, and PBA BIR/offset.
- PCIe extended capabilities: vendor-specific extended capability, AER status/mask/severity, correctable-error status/mask, AER capability/control, TLP header logs, TLP prefix logs, resizable BAR capabilities, power-budgeting registers, DPA capability/status/control and substate power allocation, ACS, PASID, and ARI.

The RCC blocks define non-config-space controls around the PCIe port and endpoint:

- `RCC_VDM_SUPPORT` exposes VDM/MCTP/AMPTP support and root-mode routing checks.
- `RCC_BUS_CNTL` covers bus-reset, error-log, poisoned TLP, completion-abort/unsupported-request, and downstream primary/secondary error signaling policy.
- `RCC_FEATURES_CONTROL_MISC` controls unsupported-request handling for ATC/PASID, translated requests, page requests, invalid completions, MSI/MSI-X pending cleanup, BME checks, ECRC device-error behavior, and poison-flag handling.
- `RCC_DEV0_LINK_CNTL` and `RCC_CMN_LINK_CNTL` cover link-down entry/exit, PME blocking, L1/LTR timing, and reset gating around link-down transitions.
- `RCC_EP_REQUESTERID_RESTORE`, `RCC_LTR_LSWITCH_CNTL`, `RCC_MH_ARB_CNTL`, and `RCC_MARGIN_PARAM_CNTL*` describe requester-ID restoration, LTR switch latency, arbitration mode/priority, and PCIe margining parameters.
- `RCC_EP_DEV0_1_*` defines endpoint scratch, PCIe control, error interrupt enable/status, invalid-PASID unsupported-request handling, hidden-register decode enablement, private LTR transmit controls, straps, DPA fields, and initial DPA substate power allocation entries.

## Important APIs, Types, and Functions

There are no C functions, structures, or callable APIs in this range. The consumed API surface is the macro namespace itself.

Important macro groups:

- `*_COMMAND__*` and `*_STATUS__*` define standard PCI command/status bits such as I/O access, memory access, bus mastering, SERR, interrupt disable, capability-list presence, parity, aborts, and system-error reporting.
- `*_BASE_ADDR_*`, `*_ROM_BASE_ADDR__*`, `*_MSIX_TABLE__*`, `*_MSIX_PBA__*`, and `*_SRIOV_VF_BASE_ADDR_*` define address-like fields where low bits can encode enablement, BIR, type, validation, or reserved state.
- `*_DEVICE_CAP*`, `*_DEVICE_CNTL*`, and `*_DEVICE_STATUS*` model PCIe device controls such as payload sizing, read request sizing, FLR, error reporting, relaxed ordering, no-snoop, completion timeout, atomic operations, LTR, OBFF, ten-bit tags, and end-to-end TLP prefixes.
- `*_LINK_CAP*`, `*_LINK_CNTL*`, and `*_LINK_STATUS*` define link speed/width capability, ASPM, retraining, disablement, common clock, autonomous width/speed controls, DRS, equalization, compliance settings, and live negotiated-link status.
- `*_MSI_*` and `*_MSIX_*` define interrupt-delivery fields for MSI enablement, multiple-message capability/enables, 64-bit addressing, per-vector masking, extended data, vector masks, pending bits, MSI-X function mask/enable, table location, and PBA location.
- `*_PCIE_UNCORR_ERR_*`, `*_PCIE_CORR_ERR_*`, `*_PCIE_ADV_ERR_CAP_CNTL__*`, `*_PCIE_HDR_LOG*`, and `*_PCIE_TLP_PREFIX_LOG*` define AER status, masks, severity policy, ECRC support/enables, first-error pointers, multi-header logging, and diagnostic packet capture words.
- `*_PCIE_ACS_*`, `*_PCIE_PASID_*`, and `*_PCIE_ARI_*` describe access-control, process address-space ID, and alternate routing-ID capabilities and controls used by PCIe/IOMMU/SR-IOV integration.
- `*_PCIE_DPA_*` and `RCC_EP_DEV0_1_*DPA*` define dynamic power allocation capability, latency indicators, substate status, compliance mode, and per-substate power allocation fields.
- `RCC_*` macros expose NBIO root/endpoint policy controls that are not simply standard PCI config-space fields, including unsupported-request filtering, pending MSI cleanup, BME checks, link-down reset behavior, requester-ID restore, and margining geometry.

## Control Flow

This chunk has no runtime control flow. Inclusion is controlled by the enclosing generated header guard outside this slice. At compile time, any translation unit that includes the NBIO 4.3.0 generated headers receives these constants.

Typical consumer flow is inferred from the macro design:

1. Select a register offset from `nbio_4_3_0_offset.h`.
2. Read the register through AMDGPU MMIO, PCI config, or SOC15 register helpers.
3. Extract fields with the `*_MASK`/`__SHIFT` pair, commonly via generated-register helper macros such as `REG_GET_FIELD`.
4. Compose updated values with matching masks/shifts, commonly with `REG_SET_FIELD`, then write the register back when enabling or disabling PCIe, interrupt, SR-IOV, AER, ACS/PASID/ARI, power, or RCC policy bits.

## State and Persistence Behavior

The header itself stores no software state and has no persistence behavior. It describes state held in NBIO/PCIe hardware registers.

Configuration fields such as `MEM_ACCESS_EN`, `BUS_MASTER_EN`, MSI/MSI-X enables, MSI-X function mask, PM state, FLR initiation, payload sizing, link controls, AER masks/severity, ACS/PASID/ARI enables, SR-IOV VF enables/counts/page sizes, VF BAR sizes, and RCC policy bits persist in hardware until changed by driver, firmware, PCI core, SR-IOV management, function-level reset, hot reset, or broader GPU reset.

Status fields such as device/link status, MSI pending bits, AER status, DPA status, equalization status, interrupt status, migration status, and TLP/header logs are hardware-updated. Some are sticky or clear-on-write according to PCIe/NBIO semantics, so mask misuse can acknowledge or hide events rather than merely inspect them.

Address-like fields in BAR, ROM BAR, MSI-X table/PBA, SR-IOV VF BAR, migration-state-array, and capability-list registers include encoded low bits. The masks in this header distinguish payload address/offset bits from control or selector bits, but consumers must preserve fields that are outside the intended update.

The RCC endpoint scratch register is a raw 32-bit field and may be used by low-level firmware/driver coordination, but this chunk does not define higher-level ownership or lifetime rules.

## Dependencies and Integration Points

This chunk integrates with:

- `nbio_4_3_0_offset.h`, which provides the corresponding register offsets for the field layouts described here.
- Other generated NBIO 4.3.0 headers such as defaults and register-base definitions, which must stay synchronized with this shift/mask file.
- AMDGPU/SOC15 register helper macros that expect the generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` naming convention.
- `amdgpu/nbio_v4_3.c` and SMU/DC display power-management code paths that include the NBIO 4.3.0 generated headers for PCIe/NBIO control.
- Linux PCI/PCIe subsystems for command/status, PM, MSI/MSI-X, AER, resizable BAR, DPA, ACS, PASID, ARI, SR-IOV, and link-management semantics.
- IOMMU and SR-IOV orchestration paths where PASID, ACS, ARI, VF BAR sizing, VF stride/offset, and VF enablement define how PFs and virtual functions are exposed and isolated.
- Hardware diagnostics and recovery paths that depend on AER status/mask/severity, ECRC controls, header logs, TLP prefix logs, RCC interrupt status, and link-down controls.

## Risks and Edge Cases

- The file is generated and very repetitive. A single shift or mask generation error can silently corrupt every consumer of that field.
- This chunk begins mid-`EPF1` area and ends mid-`RCC_EP_DEV0_1` DPA substate definition. Merge/reconciliation should not treat it as a complete file or even a complete final address-block slice.
- `EPF2` and `EPF3` are structurally similar, but some partial-boundary differences are due to chunking rather than hardware differences. Cross-function comparison checks should account for the truncated start/end of the range.
- Status, mask, and severity AER registers share nearly identical field names. Using a status mask where a severity or enable mask is required can suppress reporting, misclassify faults, or clear the wrong condition.
- MSI/MSI-X fields are split across 32-bit and 64-bit variants. Incorrect use of `*_64` definitions can program the wrong data/mask/pending register layout.
- BAR-like fields include encoded low bits. Treating the full masked value as a plain byte address can lose BIR, enable, validation, or type information.
- Link-control fields such as retrain, disable, autonomous speed/width controls, compliance entry, and equalization controls can affect reachability if written without PCIe state-machine coordination.
- ACS, PASID, ARI, ATS-related RCC behavior, and SR-IOV VF controls interact with IOMMU isolation and PCIe routing. Enabling them without platform support can break DMA translation, function discovery, or VF isolation.
- RCC policy bits around unsupported requests, BME checks, MSI pending cleanup, ECRC, poison handling, and completion abort/unsupported-request signaling can hide real hardware errors or generate unexpected errors if configured incorrectly.
- DPA, LTR, and power-management fields influence latency and power behavior. Bad values may cause incorrect power-state transitions, missed LTR messages, or poor link/power performance.

## Test Signals

Useful validation signals for this chunk:

- Build AMDGPU configurations that include `nbio_4_3_0_sh_mask.h`; malformed, missing, or duplicate macros should fail at compile time.
- Run generated-header consistency checks against the authoritative NBIO 4.3.0 register database and against `nbio_4_3_0_offset.h`, especially for offset-to-field pairing and address-block boundaries.
- Compare `EPF2` and `EPF3` register families for expected structural parity while ignoring the known chunk boundaries.
- SR-IOV smoke tests that enable VFs, verify VF counts/stride/first-offset/device-ID exposure, exercise VF BAR sizing, and bind/unbind PF/VF drivers.
- PCIe capability inspection with `lspci -vv` or driver debug output to confirm command/status, PM, MSI/MSI-X, AER, ACS, PASID, ARI, resizable BAR, DPA, and link capability fields decode as expected.
- MSI/MSI-X tests that program vectors, toggle masks/function mask, check pending state, and verify delivery and quiescing for EPF2/EPF3 paths.
- AER injection or observation tests that verify correctable/uncorrectable status, masks, severity, first-error pointer, ECRC controls, TLP header logs, and TLP prefix logs.
- Link-management tests around retraining, speed/width negotiation, equalization, DRS, ASPM/LTR, and reset/link-down transitions.
- Power-management tests for PM states, LTR transmit controls, DPA latency/substate/power-allocation fields, and RCC L1/LTR timers.
- RCC error-path tests that toggle unsupported-request filtering, invalid PASID handling, BME checks, poison/ECRC behavior, and endpoint interrupt enable/status bits, then verify visible driver error reporting.
