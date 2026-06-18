# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 63891-66318

## Scope

This chunk is a generated AMDGPU NBIO 2.3 shift/mask header fragment. It defines C preprocessor constants for PCI/PCIe configuration-space register fields, not executable code. Each field appears as a `REGISTER__FIELD__SHIFT` macro and a matching `REGISTER__FIELD_MASK` macro. These names are meant to be used with the matching offsets from `nbio_2_3_offset.h` and AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, and SOC15 accessors.

The range starts at the tail of virtual function 8 (`VF8`) PCIe Advanced Error Reporting, ATS, and ARI field definitions. It then fully covers the generated config-space field masks for `VF9`, `VF10`, and `VF11`, and ends partway through `VF12` at `BIF_CFG_DEV0_EPF0_VF12_0_ROM_BASE_ADDR`.

## Purpose

These macros describe the bit layout of NBIO 2.3 PCIe configuration-space images for SR-IOV virtual functions. The covered register families model standard PCI header fields and extended PCIe capabilities for `BIF_CFG_DEV0_EPF0_VF*` functions:

- Vendor/device identity, command/status, revision/class codes, header/BIST, BARs, subsystem identity, ROM base, capability pointer, interrupt line/pin, and latency/grant fields.
- PCIe capability list, PCIe device/link capability, control, and status registers.
- PCIe 2.0/3.0 capability extensions such as device capability/control/status 2 and link capability/control/status 2.
- MSI and MSI-X capability control, message address/data, mask, pending, table, and PBA fields.
- Vendor-specific enhanced capability headers and payload registers.
- Advanced Error Reporting capability headers, uncorrectable/correctable error status, masks, severities, AER capability/control, header logs, and TLP prefix logs.
- ATS capability/control and ARI capability/control fields for address translation and alternative routing ID support.

Because this file is generated hardware metadata, its main contract is exact symbolic naming, shift values, and masks. Runtime behavior depends on code that uses these masks with the corresponding `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` offsets and with the correct NBIO instance/access path.

## Important Macro Families

VF8 tail:

- Lines 63891-64107 finish `BIF_CFG_DEV0_EPF0_VF8_0` AER, ATS, and ARI masks.
- AER uncorrectable status/mask/severity registers expose the common PCIe AER bits: data link protocol, surprise down, poisoned TLP, flow control protocol, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, AtomicOp egress blocked, and TLP prefix blocked.
- Correctable AER status/mask fields include receiver error, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal, correctable internal error, and header-log overflow.
- AER logs use full-width `TLP_HDR` and `TLP_PREFIX` fields across four registers each.
- ATS fields include capability-list metadata, invalidate queue depth, page-aligned request support, global invalidate support, STU, and `ATC_ENABLE`.
- ARI fields include enhanced capability metadata, MFVC/ACS function-group capability bits, next function number, function-group enables, and the function-group selector.

VF9, VF10, and VF11 complete blocks:

- Each complete VF block starts with an address block marker such as `nbio_nbif0_bif_cfg_dev0_epf0_vf9_bifcfgdecp`.
- Standard PCI header fields use narrow masks for identity and class-code registers, byte-wide cache-line/latency/header-type style registers, and full 32-bit masks for BARs and CardBus CIS pointer fields.
- `COMMAND` exposes enable/policy bits for IO access, memory access, bus master, special cycle, memory write invalidate, palette snoop, parity response, SERR, fast back-to-back, and interrupt disable.
- `STATUS` exposes readiness, interrupt status, capability-list availability, PCI 66 MHz and fast back-to-back capability, parity and abort/error indications, and DEVSEL timing.
- `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` define the endpoint's PCIe capability contract, including max payload/read request sizing, phantom functions, extended tags, error reporting enables, relaxed ordering, no-snoop, auxiliary power, link speed/width, ASPM/L0s/L1 exit latencies, clock/power-management bits, retrain/common-clock/link-disable controls, and negotiated link status.
- `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` cover newer PCIe capability fields such as completion timeout ranges and controls, ARI forwarding, AtomicOp support/blocking, LTR, OBFF, EETLP prefix support, target link speeds, equalization controls, de-emphasis, and equalization status phases.
- MSI/MSI-X fields cover capability IDs and next pointers, MSI enable and multiple-message controls, 64-bit MSI address/data aliases, per-vector masking, pending bits, MSI-X table size/enable/mask, table BIR/offset, and PBA BIR/offset.
- Vendor-specific enhanced capability fields provide capability ID/version/next-pointer metadata, VSEC ID/revision/length, and two full-width vendor-specific payload registers.
- AER, ATS, and ARI families repeat the same field layout as the VF8 tail.

VF12 partial block:

- Lines 66204-66318 begin the `VF12` address block and define masks from vendor/device ID through `ROM_BASE_ADDR`.
- The rest of `VF12` is outside this chunk, so consumers and final merged documentation must combine this with the following chunk before treating `VF12` as complete.

## APIs, Types, And Data

This chunk defines no functions, structs, enums, storage objects, or callable APIs. Its exported interface is the preprocessor namespace:

- `BIF_CFG_DEV0_EPF0_VF{8,9,10,11,12}_0_<REGISTER>__<FIELD>__SHIFT`
- `BIF_CFG_DEV0_EPF0_VF{8,9,10,11,12}_0_<REGISTER>__<FIELD>_MASK`

The offset-side companion is `nbio_2_3_offset.h`, which defines matching `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` offsets. Within the checked offset header, representative offsets include standard PCI header locations (`VENDOR_ID` at `0x0000`, `COMMAND` at `0x0004`, `ROM_BASE_ADDR` at `0x0030`), PCIe capability offsets (`PCIE_CAP_LIST` at `0x0064`, `DEVICE_CNTL` at `0x006c`, `LINK_STATUS` at `0x0076`), MSI/MSI-X offsets (`MSI_CAP_LIST` at `0x00a0`, `MSIX_CAP_LIST` at `0x00c0`), AER offsets (`PCIE_ADV_ERR_RPT_ENH_CAP_LIST` at `0x0150`), ATS offsets (`PCIE_ATS_ENH_CAP_LIST` at `0x02b0`), and ARI offsets (`PCIE_ARI_ENH_CAP_LIST` at `0x0328`).

The offsets are config-space offsets within the generated VF config image. They must not be treated as ordinary MMIO register addresses without the correct NBIO/PCIe config access mechanism.

## Control Flow

There is no local control flow. At compile time, the preprocessor substitutes numeric shifts and masks. Runtime control flow is supplied by code that includes the NBIO 2.3 generated headers.

The direct include points found in this repository snapshot are:

- `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`
- `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`
- `drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c`
- `drivers/gpu/drm/amd/pm/swsmu/smu11/sienna_cichlid_ppt.c`

`nbio_v2_3.c` is the central NBIO 2.3 integration file. It uses the same generated header family to program NBIO/PCIe behavior such as memory-controller access, doorbell apertures and ranges, interrupt control, HDP flush/remap registers, PCIe link and ASPM/LTR policy, clock/light-sleep controls, and SR-IOV-aware register access. The specific VF9-VF12 config-space macro names in this chunk do not appear to be directly referenced by current in-tree C code found during this pass; they remain generated register contracts for SR-IOV VF configuration-space decode, firmware/PF management, diagnostics, and future or out-of-tree consumers.

`mxgpu_nv.c` is the Navi SR-IOV/MxGPU communication path. It includes the NBIO 2.3 masks while handling VF/PF runtime service state and message acknowledgement behavior, which is conceptually adjacent to these VF config-space definitions even when it does not directly touch this exact macro range.

The SMU11 PPT files include NBIO 2.3 masks for power-management and PCIe-related policy, such as reading NBIO straps and checking PCIe DPM feature state. Their direct usage is mostly outside the VF config-space names covered here.

## State And Persistence Behavior

The macros themselves are stateless compile-time constants. The state they describe is hardware PCIe configuration-space state associated with SR-IOV virtual functions.

Important persistent or semi-persistent hardware state represented by this chunk includes:

- VF command/status enables and error latches. Access enable bits, bus mastering, interrupt disable, SERR/parity response, and status error bits directly affect VF enumeration, driver binding, DMA permission, and error handling.
- VF BARs and ROM base address fields. These determine the PCI resources exposed to a VF and must align with PF/SR-IOV resource allocation.
- MSI/MSI-X state. Message address/data, masks, pending bits, MSI-X table/PBA layout, and enable bits affect interrupt delivery and can persist until reset, function-level reset, VF reset, or PF reinitialization.
- PCIe device/link controls. Max payload/read request size, relaxed ordering, no-snoop, extended tags, link control, ASPM-related controls, completion timeout, LTR, and target link speed fields influence transaction behavior and link policy.
- AER state. Correctable and uncorrectable error status bits may be sticky until cleared, masks determine whether errors are surfaced, severity bits influence fatal/nonfatal classification, and header/TLP prefix logs capture error context.
- ATS/ATC state. ATS capability and `ATC_ENABLE` describe or control address-translation cache participation; incorrect state can affect IOMMU interaction and memory isolation.
- ARI state. ARI capability/control fields affect function numbering and routing behavior for multifunction or virtualized PCIe layouts.

This state is owned by hardware, firmware, the PF, host PCI core, and VF drivers depending on platform mode. It is not durable file-system state. It can be reset by device reset, FLR/VF reset, hot reset, suspend/resume reinitialization, or PF/firmware reprogramming.

## Dependencies

Generated-register dependencies:

- `nbio_2_3_offset.h` supplies the matching `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` config offsets.
- `nbio_2_3_default.h` supplies default values for other NBIO 2.3 registers, though this VF config-space chunk is primarily a shift/mask contract.
- Other chunks of `nbio_2_3_sh_mask.h` define PF fields, earlier VF blocks, and the rest of `VF8`/`VF12`.
- AMDGPU register helpers provide the actual access semantics and masking helpers. The same mask values are only meaningful when routed through the correct NBIO/PCIe config access path.

Driver and platform dependencies:

- SR-IOV ownership matters. PF, VF, firmware, and host PCI core may each own different parts of VF config-space state.
- Linux PCI and PCIe capability handling may program or validate many standard fields rather than AMDGPU touching every field directly.
- Host IOMMU/ATS policy determines whether ATS/ATC fields are usable for a VF.
- AER support depends on PCIe error reporting being enabled in the platform and kernel.
- MxGPU/SR-IOV paths depend on mailbox/runtime-service behavior outside this header, but the VF config-space layout must remain consistent with those virtualization flows.

## Integration Points

The practical integration point is the AMDGPU NBIO 2.3 register include tree:

- `nbio_v2_3.c` includes this header with the matching offset/default headers and uses the generated NBIO field names in PCIe, doorbell, interrupt, HDP, and power-management setup.
- `mxgpu_nv.c` integrates Navi SR-IOV runtime services and VF/PF communication while including the same generated NBIO 2.3 mask namespace.
- SMU11 power-management files include the NBIO 2.3 masks for NBIO straps and PCIe DPM policy.
- The generated `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` offsets are aligned with this mask namespace and should be considered the authoritative companion data for any VF config-space access.
- Adjacent NBIO generations, including 6.1 and 7.4 in this tree, define very similar VF config-space names and offsets. That makes cross-generation naming familiar but also increases the risk of using the wrong generated header pair.

## Risks And Edge Cases

- Generation mismatch is the primary risk. Similar `BIF_CFG_DEV0_EPF0_VF*_0_*` names exist in other NBIO headers, but masks, offsets, ownership, and supported capabilities can differ by ASIC generation.
- This chunk is not a complete VF range. It starts after the beginning of `VF8` and ends before the end of `VF12`; merged per-file research must combine adjacent chunks before drawing whole-function conclusions for those VFs.
- Config offsets such as `0x006c` and `0x0150` are PCIe config-space offsets, not normal MMIO offsets. Using them with the wrong accessor can touch the wrong register or fail silently.
- MSI 32-bit and 64-bit layouts intentionally alias some offsets, for example message data and mask fields. Code must interpret the fields according to whether 64-bit MSI and per-vector masking are enabled.
- Sticky AER status bits and header logs require careful clear/read sequencing. Clearing too early loses diagnostic evidence; failing to clear can cause repeated error reporting.
- ATS/ATC enablement affects address translation and isolation. Enabling it without host/IOMMU support or PF policy coordination can break VF DMA behavior or isolation assumptions.
- ARI fields affect function routing and numbering. Incorrect ARI forwarding or function group programming can make VFs unreachable or misidentified.
- BAR and ROM base fields expose resources to VFs. Incorrect masks or writes can overlap resources, expose PF-owned apertures, or break VF driver probing.
- Some fields are standard PCIe capability state normally coordinated by the host PCI core. AMDGPU or firmware writes must avoid racing generic PCI config management.
- Hand-editing generated shift/mask headers is risky because build success does not prove hardware bit contracts are correct.

## Test And Verification Signals

Useful validation signals for this chunk are mostly compile coverage, static pairing checks, and SR-IOV/PCIe runtime inspection:

- Build AMDGPU configurations that include `nbio_v2_3.c`, `mxgpu_nv.c`, and the SMU11 PPT files against `nbio_2_3_offset.h` plus `nbio_2_3_sh_mask.h`.
- Run a static pairing check that every `BIF_CFG_DEV0_EPF0_VF{8,9,10,11,12}_0_*` register in this chunk has a matching `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` offset where the covered register is complete.
- Validate that `VF9`, `VF10`, and `VF11` each expose the expected standard PCI, PCIe capability, MSI/MSI-X, VSEC, AER, ATS, and ARI register families with identical field layouts.
- Treat `VF8` and `VF12` as partial in chunk-local checks; do not report missing beginning/end registers until adjacent chunks are merged.
- On NBIO 2.3 SR-IOV-capable hardware, enumerate VFs and compare `lspci -vvv` capability decode for VF9-VF11 against the generated capability offsets and field masks.
- Exercise VF reset/FLR and confirm command/status, MSI/MSI-X, AER status/logs, ATS enable, and ARI state return to expected PF/firmware-configured values.
- Inject or observe PCIe AER events where platform support exists, then verify correctable/uncorrectable status, mask, severity, and header-log fields decode according to these masks.
- Enable VF MSI/MSI-X paths and confirm interrupt masking, pending bits, table/PBA offsets, and 64-bit MSI aliases behave as expected.
- If ATS is enabled for VFs, validate host IOMMU integration and DMA correctness before and after VF reset, suspend/resume, and PF-mediated reconfiguration.
