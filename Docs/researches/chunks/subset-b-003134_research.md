# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 29592-32042

## Scope

This chunk is a generated AMDGPU NBIO 7.11.0 shift/mask header segment. It contains only preprocessor constants for hardware register bitfields; there are no functions, structs, enums, globals, locks, allocations, or executable statements in this range.

The slice starts in the middle of `BIF_CFG_DEV0_EPF1_0_LANE_4_EQUALIZATION_CNTL_16GT`, covers the tail of the `BIF_CFG_DEV0_EPF1_0` endpoint-function capability layout, then defines the complete `nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp` PCI configuration-space shift/mask block. It then begins the `nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp` block and stops inside `BIF_CFG_DEV0_EPF3_0_PCIE_ARI_CAP`. Adjacent chunks are required for the beginning of the EPF1 lane-4 equalization register and the remaining EPF3 ARI capability/control and later capability fields.

Although this repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU hardware metadata and has no direct Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_11_0_sh_mask.h` provides the field-layout half of the generated NBIO register interface for AMD GPU drivers. For each hardware register field it exports:

- `<REGISTER>__<FIELD>__SHIFT`: the starting bit position.
- `<REGISTER>__<FIELD>_MASK`: the shifted mask used to isolate, preserve, clear, or compose the field.

Runtime code combines these macros with address definitions from `nbio_7_11_0_offset.h` and AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, and `SOC15_REG_OFFSET`. The local NBIO 7.11 implementation, `drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c`, includes this exact shift/mask header and uses that helper pattern.

## Important Macro Families

The EPF1 tail covers advanced PCIe link and capability fields:

- `BIF_CFG_DEV0_EPF1_0_LANE_[4-15]_EQUALIZATION_CNTL_16GT` provides 16 GT/s downstream/upstream transmit preset fields. The lane-4 register is only partially inside this chunk; lanes 5-15 are complete here.
- `BIF_CFG_DEV0_EPF1_0_PCIE_MARGINING_ENH_CAP_LIST`, `MARGINING_PORT_CAP`, and `MARGINING_PORT_STATUS` describe PCIe lane-margining capability discovery and software-readiness bits.
- `BIF_CFG_DEV0_EPF1_0_LANE_[0-15]_MARGINING_LANE_CNTL` and `..._STATUS` repeat the same per-lane layout: receiver number, margin type, usage model, and 8-bit margin payload/status fields.
- `BIF_CFG_DEV0_EPF1_0_PCIE_VF_RESIZE_BAR_ENH_CAP_LIST` and `PCIE_VF_RESIZE_BAR[1-6]_{CAP,CNTL}` describe virtual-function resizable BAR support and control fields, including BAR index, total BAR count, selected size, and upper supported-size bits.
- `BIF_CFG_DEV0_EPF1_0_PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2` expose Readiness Time Reporting fields for reset, data-link-up, FLR, D3hot-to-D0 timing, and validity.

The EPF2 block is complete in this slice and mirrors a full endpoint-function PCI/PCIe configuration image:

- Conventional PCI identity and header fields: vendor/device IDs, command/status, revision/class codes, cache line, latency, header, BIST, BARs 1-6, adapter ID, ROM BAR, capability pointer, interrupt line/pin, minimum grant, and maximum latency.
- Vendor and power-management capability fields: `VENDOR_CAP_LIST`, writable adapter ID, `PMI_CAP_LIST`, `PMI_CAP`, `PMI_STATUS_CNTL`, `SBRN`, `FLADJ`, and `DBESL_DBESLD`.
- PCIe capability fields: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, plus PCIe capability 2 fields for completion timeouts, ARI forwarding, atomic operations, ID-based ordering, LTR, OBFF, ten-bit tags, end-to-end TLP prefixes, emergency power reduction, FRS, supported link speeds, equalization status, and compliance controls.
- MSI/MSI-X fields: capability headers, MSI enable/multiple-message/64-bit/per-vector/extended-data controls, message address/data registers, masks, pending bits, MSI-X table/PBA BIR and offsets, function mask, and enable bit.
- SATA capability/IDP fields: SATA capability revision, BAR location/offset, index, and data registers.
- Vendor-specific enhanced capability fields: VSEC header and two full-width scratch dwords.
- Advanced Error Reporting fields: uncorrectable error status/mask/severity for DLP, surprise down, poison, flow-control, completion timeout/abort, unexpected completion, receive overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic-op egress blocked, TLP-prefix blocked, and poisoned-TLP egress blocked; correctable error status/mask; AER capability/control; four TLP header-log dwords; and four TLP-prefix-log dwords.
- Resizable BAR, power, and DPA fields: `PCIE_BAR[1-6]_{CAP,CNTL}`, power budget capability/data selection/data, DPA capability/latency/status/control, and DPA substate power allocation 0-7.
- Isolation and address-space capabilities: ACS capability/control, PASID capability/control, ARI capability/control, and RTR data.

The EPF3 block repeats the same generated endpoint-function layout from vendor/device identity through most of the advanced PCIe capabilities:

- It covers the full conventional header, PM, PCIe device/link capability, MSI/MSI-X, SATA, VSEC, AER, header/TLP-prefix logs, resizable BAR, power budget, DPA, ACS, and PASID sections.
- It reaches `BIF_CFG_DEV0_EPF3_0_PCIE_ARI_ENH_CAP_LIST` and the first five field definitions of `BIF_CFG_DEV0_EPF3_0_PCIE_ARI_CAP`, ending after the `ARI_ACS_FUNC_GROUPS_CAP_MASK`. The `ARI_NEXT_FUNC_NUM_MASK`, `PCIE_ARI_CNTL`, and any later EPF3 registers continue outside this work item.

## APIs, Types, And Functions

There are no callable APIs or C data types in this range. The public interface is the generated macro namespace. Macro values are integer constants, mostly `L`-suffixed masks, that encode bit geometry only.

These definitions do not encode register addresses, reset values, read/write permissions, write-one-to-clear behavior, reserved-bit policy, access size, firmware ownership, or operation ordering. Consumers must pair them with `nbio_7_11_0_offset.h`, the appropriate AMDGPU register access path, and hardware-specific knowledge of each field's semantics.

## Control Flow And Runtime Behavior

This header has no local control flow. The runtime flow implied by these constants is:

1. AMDGPU or platform firmware code selects the appropriate NBIO/PCIe register address for the active endpoint function and register instance.
2. Code reads a register and decodes fields with `*_MASK` and `*__SHIFT`, or composes a new value with `REG_SET_FIELD` while preserving unrelated bits.
3. The resulting hardware state participates in PCIe endpoint enumeration, BAR sizing, MSI/MSI-X routing, link training, link equalization, lane margining, power management, DPA substate management, ACS/PASID/ARI isolation and address-space controls, AER error reporting, and readiness-time reporting.

Several represented fields are asynchronous protocol or hardware state rather than simple software-owned values: PCIe link speed/width/training, equalization completion and phase success, lane-margining status, PME status, MSI/MSI-X pending/masking, AER status and logs, DPA substate status, and readiness-time validity.

## State And Persistence Behavior

The header owns no state and persists nothing. The represented state lives in NBIO 7.11.0 hardware registers and PCIe configuration-space views.

State categories described by this chunk include:

- EPF1 link-training and diagnostics state for 16 GT/s lane equalization, lane margining control/status, VF resizable BAR controls, and readiness-time reporting.
- EPF2 and EPF3 conventional PCI configuration state: identity, command/status, BARs, ROM BAR, capability pointers, interrupt line/pin, and class/revision fields.
- PCIe endpoint policy: payload/read-request sizing, relaxed/no-snoop ordering, completion timeout, function-level reset, ARI forwarding, atomic operations, LTR/OBFF, ten-bit tags, end-to-end TLP prefix behavior, target link speed, compliance mode, and link disable/retrain controls.
- Interrupt routing and pending state for MSI and MSI-X, including 32-bit and 64-bit message address/data variants, mask registers, pending bits, MSI-X table/PBA offsets, function masking, and enable controls.
- Error-observation and error-policy state for AER status, masks, severity, ECRC generation/checking, first-error pointer, multi-header capture, header logs, and TLP-prefix logs.
- Resource sizing and power management state for resizable BARs, power budget data, DPA capability/status/control, and DPA substate power allocations.
- Isolation and process-addressing controls through ACS, PASID, and ARI capability/control registers.

Retention across GPU reset, PCI reset, FLR, BACO, suspend/resume, runtime power transitions, or firmware reinitialization is not specified by the macros. Driver initialization and restore paths must reprogram any non-retained policy registers and must observe hardware-specific status/log clearing rules.

## Dependencies And Integration Points

Primary generated dependencies are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_offset.h` for matching register addresses and base indices. This NBIO generation has an offset header; no sibling `nbio_7_11_0_smn.h` or `nbio_7_11_0_default.h` file is present in the local tree.
- Adjacent chunks of `nbio_7_11_0_sh_mask.h`, because this range begins inside an EPF1 lane equalization register and ends inside an EPF3 ARI capability register.
- AMDGPU helper macros and SOC15/NBIO accessors that consume generated shift/mask definitions.

Integration areas include:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c`, which includes `nbio_7_11_0_offset.h` and `nbio_7_11_0_sh_mask.h` and uses generated field macros for NBIO programming.
- PCIe endpoint setup, enumeration, BAR sizing, resizable BAR and VF resizable BAR support, MSI/MSI-X setup, link training/equalization diagnostics, lane margining diagnostics, and readiness-time reporting.
- GPU reset, FLR, suspend/resume, and runtime power-management paths that must restore PCIe/NBIO policy fields and avoid losing diagnostic status.
- Error handling and RAS-adjacent paths that read AER status/mask/severity fields and capture header/TLP-prefix logs before clearing status bits.
- Virtualization/IOMMU/KFD-adjacent paths that depend on ACS, PASID, ARI, BAR, and interrupt-routing behavior for isolation and per-process addressing.

## Risks And Edge Cases

- Generated mask/shift drift can compile cleanly while causing wrong-bit programming. In this chunk that can affect BAR sizing, endpoint enablement, interrupts, link behavior, power management, AER policy, isolation, or PASID/ARI behavior.
- The range is highly repetitive across EPF2 and EPF3. A generator or manual correction error can be topology-dependent if one endpoint function differs while another remains correct.
- Status, mask, and severity registers have very similar names. Confusing AER `*_STATUS`, `*_MASK`, and `*_SEVERITY` fields can either hide errors or report them with the wrong severity.
- Some PCIe status and AER fields are usually write-one-to-clear or log-sensitive, but that access behavior is not visible in this header. Code must capture header and prefix logs before clearing related status bits.
- MSI/MSI-X address/data, mask, pending, table, and PBA fields are interrupt-routing sensitive. Bad restore values or wrong masks can misroute, suppress, or spuriously trigger interrupts.
- Link-control, equalization, lane-margining, DPA, and power-management fields can trigger asynchronous hardware transitions. Callers need timeout and recovery handling outside this header.
- ACS, PASID, and ARI controls affect DMA isolation, address-space tagging, and function routing. Misprogramming can break peer-to-peer traffic, virtualization isolation, or process-address-space semantics.
- The source boundaries are artificial: EPF1 lane-4 equalization is incomplete at the start, and EPF3 ARI capability is incomplete at the end. Reconciliation must not treat those boundary omissions as source defects.

## Test And Validation Signals

Useful validation combines generated-header checks with hardware-facing tests:

- Build AMDGPU configurations that include NBIO 7.11 support to catch missing or renamed generated symbols.
- Run mechanical consistency checks over the assigned range: every complete field should have both a `__SHIFT` and `_MASK`, masks should match the intended bit positions, and repeated EPF2/EPF3 register layouts should match where the hardware template is expected to be identical.
- Cross-check field names against `nbio_7_11_0_offset.h` so every complete register family in this chunk has a matching address definition where expected.
- Exercise PCIe endpoint enumeration and resource programming on supported hardware: command/status bits, BAR/ROM BAR sizing, VF resizable BARs, MSI/MSI-X delivery, interrupt masking, and reset/FLR restore.
- Validate link and diagnostics paths: negotiated link speed/width, 16 GT/s equalization presets, link-control/status2 fields, lane margining command/status readback, and readiness-time reporting validity.
- Exercise error paths where hardware validation permits: AER correctable and uncorrectable status/mask/severity reporting, ECRC controls, first-error pointer, header-log capture, and TLP-prefix-log capture before status clear.
- Validate power and isolation features: power budget and DPA substate fields, ACS policy bits, PASID enable/width and privilege/execute controls, and ARI capability/control behavior.

## Chunk Boundary Notes

Line 29592 is already inside `BIF_CFG_DEV0_EPF1_0_LANE_4_EQUALIZATION_CNTL_16GT`; only the lane-4 DSP/USP 16 GT/s preset shift/mask lines are visible here. The register comment and any earlier lane-4 fields belong to the previous chunk.

Line 32042 stops after `BIF_CFG_DEV0_EPF3_0_PCIE_ARI_CAP__ARI_ACS_FUNC_GROUPS_CAP_MASK`. The remaining EPF3 ARI capability mask for `ARI_NEXT_FUNC_NUM`, the EPF3 ARI control register, and later EPF3 registers continue in the next chunk. Merge/reconciliation should stitch both boundaries before producing the final per-file research document.
