# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 41494-43919

## Scope

This chunk covers a generated AMD NBIO 2.3 register shift/mask header section for PCIe BIF configuration space exposed through SR-IOV virtual functions. It starts in the middle of `BIF_CFG_DEV0_EPF0_VF18_DEVICE_CNTL2`, covers the rest of VF18's extended PCIe capability fields, all generated field macros for VF19 and VF20, and the front of VF21 through the first two `PCIE_ATS_CAP` shift definitions.

The range is C preprocessor data only. It defines no functions, structs, variables, runtime branches, locks, memory allocations, or direct register accesses. Its interface is the generated AMD register-field convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field bit mask.

The chunk contains 2,426 source lines and about 2,141 `#define` entries. The visible virtual-function prefixes are `BIF_CFG_DEV0_EPF0_VF18`, `VF19`, `VF20`, and `VF21`.

## Purpose

`nbio_2_3_sh_mask.h` is the field-layout side of the NBIO 2.3 hardware register ABI. Companion headers such as `nbio_2_3_offset.h` provide register offsets, while this file provides the bit positions and masks that software needs to compose or decode PCI configuration registers for AMDGPU NBIO/BIF blocks.

This chunk is focused on repeated PCI configuration-space layouts for endpoint function 0 virtual functions. The fields mirror standard PCI/PCIe configuration concepts: vendor/device IDs, command/status, BARs, PCIe capabilities, link control and status, MSI/MSI-X, vendor-specific capabilities, Advanced Error Reporting, Address Translation Services, and Alternative Routing-ID Interpretation.

Consumers normally use these macros through AMDGPU register helpers and generated idioms such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, or NBIO-specific read/write paths. The macros themselves are not policy; they are constants that make driver reads and writes land on the correct hardware bits.

## Important Macro Families

### VF18 Tail

The chunk begins after the first part of `VF18_DEVICE_CNTL2`. Lines 41494-41862 complete VF18's extended PCIe capability layout:

- `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` cover completion timeout, ARI forwarding, atomic operation request/egress control, IDO, LTR, OBFF, end-to-end TLP prefix blocking, supported target link speeds, compliance entry, equalization status, retimer presence, crosslink state, downstream presence, and DRS message state.
- `MSI_*` and `MSIX_*` registers cover MSI enable/multivector/64-bit/per-vector masking, message address/data, mask and pending bitmaps, MSI-X table/PBA BIR and offsets, function mask, and MSI-X enable.
- `PCIE_VENDOR_SPECIFIC_*` exposes VSEC capability header fields and scratch registers.
- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, `PCIE_UNCORR_ERR_SEVERITY`, `PCIE_CORR_ERR_STATUS`, `PCIE_CORR_ERR_MASK`, `PCIE_ADV_ERR_CAP_CNTL`, header logs, and TLP prefix logs map Advanced Error Reporting state, masks, severity bits, ECRC controls, first-error pointer, and captured TLP diagnostic data.
- `PCIE_ATS_*` and `PCIE_ARI_*` cover ATS capability/control and ARI capability/control fields.

Because the start line is mid-register, the preceding `VF18_DEVICE_CNTL2` shift definitions and early masks are outside this chunk and must be considered during final merge.

### Complete VF19 and VF20 Blocks

Lines 41864-42558 define the complete `addressBlock: nbio_nbif0_bif_cfg_dev0_epf0_vf19_bifcfgdecp`; lines 42560-43254 define the complete equivalent VF20 block. These two blocks have the same generated structure:

- Basic PCI header registers: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`, BARs `BASE_ADDR_1` through `BASE_ADDR_6`, `CARDBUS_CIS_PTR`, `ADAPTER_ID`, `ROM_BASE_ADDR`, `CAP_PTR`, interrupt line/pin, and latency/grant fields.
- PCIe capability registers: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS`.
- PCIe 2+ extended device/link registers: `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- Interrupt capability families: MSI capability list/control/address/data/mask/pending plus MSI-X capability list/control/table/PBA fields.
- Vendor-specific capability and scratch fields.
- Advanced Error Reporting families for uncorrectable status, mask, severity, correctable status, correctable mask, AER capability/control, header logs, and TLP prefix logs.
- ATS and ARI enhanced capabilities and control registers.

The fields encode standard enable/status/control surfaces: memory and bus-master enable, interrupt disable, error response/status bits, payload/request size, relaxed ordering, no-snoop, AUX power, phantom functions, link speed/width, ASPM, read completion boundary, retrain/link-disable controls, clock power management, and bandwidth/autonomous status.

### VF21 Front

Lines 43256-43919 start the `addressBlock: nbio_nbif0_bif_cfg_dev0_epf0_vf21_bifcfgdecp`. The covered portion includes the same PCI header, PCIe capability, MSI/MSI-X, VSEC, and AER families as VF19/VF20, then reaches `PCIE_ATS_ENH_CAP_LIST` and only the first two shift fields of `PCIE_ATS_CAP`:

- Covered `PCIE_ATS_CAP` fields at the chunk end are `INVALIDATE_Q_DEPTH` and `PAGE_ALIGNED_REQUEST` shifts.
- The `GLOBAL_INVALIDATE_SUPPORTED` shift, all `PCIE_ATS_CAP` masks, `PCIE_ATS_CNTL`, `PCIE_ARI_*`, and the transition to VF22 are in the next chunk.

## Control Flow and State Behavior

There is no executable control flow. These definitions affect the build by making symbolic bit positions available to C code that includes the header. Runtime behavior occurs only in the consuming driver paths that read, mask, shift, set, and write PCIe/NBIO registers.

The represented state is hardware PCI configuration state for SR-IOV virtual functions. Some fields are persistent configuration until reset or reprogramming, including command enables, BAR layout, MSI/MSI-X routing, device/link control, ARI/ATS enablement, AER masks, and error severity policy. Other fields are status or latched diagnostic state, including PCI status bits, link status, error status, MSI pending bits, AER header logs, TLP prefix logs, and AER first-error information.

The header does not express sequencing rules. Correct behavior for control-like fields depends on the owning driver and PCIe spec rules: status bits may be write-1-to-clear, link retraining and compliance bits need ordering and polling, MSI/MSI-X changes must coordinate with interrupt setup, and AER/ATS/ARI settings must match platform capabilities and IOMMU policy.

## Dependencies and Integration Points

This chunk depends on the generated NBIO header set:

- `nbio_2_3_offset.h` provides matching register offsets such as VF19/VF20 MSI masks and AER mask/status offsets.
- `nbio_2_3_default.h` provides reset/default values for the same generated register names.
- `nbio_2_3_sh_mask.h` is included by AMDGPU NBIO and virtualization-related code; observed include sites in this tree include `amdgpu/nbio_v2_3.c`, `amdgpu/mxgpu_nv.c`, and SMU power-management files such as `pm/swsmu/smu11/navi10_ppt.c` and `sienna_cichlid_ppt.c`.

Integration with driver logic is indirect. The AMDGPU NBIO layer can use these macros to inspect or update NBIO PCIe configuration fields for Navi-era ASICs. SR-IOV and virtual-GPU paths are the most relevant higher-level users because the macros are specifically for endpoint virtual functions. Power-management and reliability paths may also decode link state, error-reporting fields, or vendor-specific capability state when coordinating reset, suspend/resume, FLR, AER handling, or virtualization setup.

## Risks

- Bitfield drift is high impact. A wrong mask or shift can write the wrong PCI configuration bit, causing broken BAR decoding, disabled bus mastering, lost interrupts, malformed MSI/MSI-X setup, bad link control, or hidden PCIe errors.
- The VF blocks are highly repetitive. Mechanical generation errors are easy to miss because VF19, VF20, and VF21 should be structurally identical but occupy different address blocks. A copied prefix, missing field, or swapped mask would compile cleanly and fail only on affected virtual functions.
- AER fields are reliability-sensitive. Incorrect uncorrectable/correctable masks, severity bits, ECRC controls, or status-clear handling can hide real PCIe faults or report false fatal/nonfatal events.
- MSI/MSI-X fields are interrupt-sensitive. Bad address/data/mask/table/PBA fields can break interrupt delivery or leave interrupts enabled during teardown.
- Link control/status fields are timing-sensitive. Misprogramming retrain, disable, compliance, ASPM, common-clock, or target-speed fields can destabilize PCIe links.
- ATS and ARI fields interact with IOMMU, requester IDs, and SR-IOV routing. Enabling or decoding them incorrectly can produce address-translation faults or route transactions to the wrong function.
- Chunk boundaries are partial. The VF18 start and VF21 end cannot be treated as complete register families until adjacent chunk reports are merged.

## Test and Validation Signals

Useful validation is mainly build, hardware, and virtualization coverage:

- Build AMDGPU paths that include `nbio/nbio_2_3_sh_mask.h`; this catches renamed, missing, or syntactically invalid generated macros.
- Exercise NBIO 2.3 device initialization, suspend/resume, reset, and FLR paths on affected ASICs to catch bad command, link, BAR, or capability bit definitions.
- Run SR-IOV virtual-function creation, assignment, reset, and teardown tests that instantiate enough VFs to cover VF18 through VF21.
- Validate MSI and MSI-X delivery for these VFs, including masking/unmasking, pending bits, table/PBA BAR selection, and interrupt teardown.
- Check PCIe link status and retraining flows under normal boot, low-power transitions, and error recovery.
- Inject or observe AER correctable and uncorrectable events where supported, then verify status, mask, severity, header-log, TLP-prefix-log, and clear behavior decode correctly.
- Validate ATS/ARI behavior with an IOMMU-enabled SR-IOV configuration, including requester ID routing and translation-cache enable/disable handling.
- Compare generated masks against hardware XML/register specifications or the corresponding `nbio_2_3_offset.h` and `nbio_2_3_default.h` rows for VF19/VF20/VF21.

## Unresolved Cross-Chunk References

Line 41494 begins inside `BIF_CFG_DEV0_EPF0_VF18_DEVICE_CNTL2`; the `CPL_TIMEOUT_VALUE`, `CPL_TIMEOUT_DIS`, `ARI_FORWARDING_EN`, `ATOMICOP_REQUEST_EN`, `ATOMICOP_EGRESS_BLOCKING`, `IDO_REQUEST_ENABLE`, and `IDO_COMPLETION_ENABLE` masks plus all shift definitions for that register are in the previous chunk. Line 43919 ends inside `BIF_CFG_DEV0_EPF0_VF21_PCIE_ATS_CAP` after `PAGE_ALIGNED_REQUEST__SHIFT`; the remaining `GLOBAL_INVALIDATE_SUPPORTED` shift, all ATS capability masks, ATS control fields, ARI fields, and the next VF block are in the following chunk. The final per-file merge must join those boundaries before making whole-file claims about VF18 or VF21 completeness.
