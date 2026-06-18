# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 7363-9837

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.11 shift/mask header. It describes bit positions and masks for PCI/PCIe configuration-space registers exposed through NBIF/BIF configuration decoder blocks. The covered range is metadata only: it contains preprocessor constants that let driver code extract or program fields in hardware registers without embedding literal bit offsets.

The line range starts at the tail of `BIF_CFG_DEV0_EPF1_LINK_STATUS2`, continues through the rest of the `nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` register field set, then covers most of `nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp`, and finally enters the beginning of `nbio_nbif0_bif_cfg_dev2_epf0_bifcfgdecp`. In PCIe terms, the chunk is dominated by endpoint function configuration fields for `DEV0_EPF1` and `DEV0_EPF2`, including MSI/MSI-X, PCIe advanced error reporting, resizable BARs, power-budgeting, dynamic power allocation, lane equalization, ACS/ATS/PASID/ARI, SR-IOV, data-link feature, 16 GT/s PHY capability, lane margining, VF resizable BARs, and readiness-time-reporting registers.

## Important APIs, Types, and Macros

There are no functions, structs, typedefs, or enums in this range. The public surface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: starting bit for a field.
- `<REGISTER>__<FIELD>_MASK`: shifted mask for the field in its register.

The chunk contains 2,118 `#define` entries spanning 350 register names: 1,184 macros under `BIF_CFG_DEV0_EPF1`, 878 under `BIF_CFG_DEV0_EPF2`, and 56 at the start of `BIF_CFG_DEV2_EPF0`.

Major `DEV0_EPF1` register families in this chunk are:

- MSI/MSI-X: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, address/data/extended-data/mask/pending registers, plus `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`.
- Vendor/device identity and PCIe capability structures: vendor-specific enhanced capability, device serial number, advanced error reporting, BAR enhanced capability, power budget, DPA, secondary PCIe capability, ACS, ATS, page request, PASID, multicast, LTR, ARI, SR-IOV, data-link feature, 16 GT/s PHY, margining, VF resizable BAR, and RTR capability blocks.
- AER status and policy fields: uncorrectable status/mask/severity, correctable status/mask, error capability/control, header logs, and TLP prefix logs. These expose completion timeout, unsupported request, ECRC, poisoned TLP, ACS violation, internal error, malformed TLP, receiver overflow, advisory non-fatal, replay timer timeout, bad DLLP/TLP, and related PCIe error classes.
- BAR and VF BAR controls: BAR1 through BAR6 capability/control pairs and VF resizable BAR1 through BAR6 capability/control pairs, with BAR size and resize controls.
- Link training and physical-layer diagnostics: 8 GT/s lane equalization control for lanes 0-15, 16 GT/s lane equalization coefficients for lanes 0-15, local/RTM parity mismatch status, lane error status, link equalization control, and lane margining control/status for lanes 0-15.
- Virtualization and address-translation helpers: ACS capability/control, ATS capability/control, page request control/status/capacity/allocation, PASID capability/control, multicast address/receive/block fields, ARI capability/control, and SR-IOV VF count, stride, offset, device ID, page size, and VF BAR fields.

Major `DEV0_EPF2` register families are similar but shorter in this chunk:

- Standard PCI configuration header: vendor/device IDs, command/status, revision/class code, cache line, latency, header type, BIST, six base address registers, adapter ID, ROM base, capability pointer, interrupt line/pin, and min/max latency.
- Power-management and PCIe base capabilities: vendor capability list, adapter ID write field, PMI capability/status-control, SBRN/FLADJ/DBESL fields, PCIe capability list/capability, device capability/control/status, link capability/control/status, and second-generation device/link capability/control/status registers.
- Interrupt and AER fields: MSI, MSI-X, SATA capability/index/data fields, vendor-specific enhanced capability, advanced error reporting status/mask/severity/log fields, and TLP prefix logs.
- BAR, power, and security/virtualization controls: BAR enhanced capability/control for BAR1-BAR6, power-budgeting, DPA, ACS, PASID, ARI, and RTR data.

The `DEV2_EPF0` block begins at line 9771 and includes only the first standard PCI configuration fields through `BIF_CFG_DEV2_EPF0_LATENCY`. The next chunk continues that endpoint-function block.

## Control Flow and Runtime Behavior

This header has no runtime control flow. It is consumed by C preprocessor expansion during compilation. Runtime behavior appears only when AMDGPU or firmware-facing code combines these masks with register-address macros from the matching NBIO 7.11 offset/SMN headers and register access helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, or SOC15/NBIO read-modify-write wrappers.

The implied hardware flows are:

1. PCI capability discovery and setup code reads capability-list and enhanced-capability fields to identify MSI, MSI-X, AER, ACS, ATS, PASID, ARI, SR-IOV, DPA, LTR, data-link, 16 GT/s PHY, lane margining, VF BAR, and RTR support.
2. Interrupt setup uses MSI/MSI-X control, address, data, mask, pending, table, and PBA fields to enable message-signaled interrupts and to mask or observe per-vector state.
3. PCIe error handling uses AER status, mask, severity, and log fields to classify correctable versus uncorrectable events, choose which events are masked, and capture header or TLP-prefix context for diagnostics.
4. Link-training and link-health code may inspect link status, equalization, lane error, 16 GT/s parity mismatch, and lane margining registers to diagnose negotiated speed/width issues or physical-layer problems.
5. Address-translation and isolation paths use ACS, ATS, page request, and PASID fields to expose or configure PCIe peer-to-peer isolation, translation request behavior, and process address space identifiers.
6. Virtualization setup uses SR-IOV and VF resizable BAR fields to describe virtual functions, VF BAR sizing, VF stride/offset, supported/system page size, and VF device identity.
7. Power-management and readiness paths use PMI, power-budgeting, DPA, LTR, and RTR fields to describe power states, allocated substate power, latency tolerance, and reset/link-up/FLR/D3hot-to-D0 timing.

The header does not enforce sequencing. Callers must still follow PCIe and ASIC-specific ordering, such as disabling a capability before changing size fields, masking errors before clearing status, programming MSI/MSI-X address/data before enabling delivery, or respecting reset and power-transition timing.

## State and Persistence

The file owns no state, allocates no memory, performs no I/O, and persists nothing. It names hardware state that lives in PCIe/NBIO configuration registers.

Represented state includes:

- Capability topology: capability IDs, versions, and next pointers for standard PCI and PCIe extended capability lists.
- Endpoint identity/configuration: vendor/device IDs, command and status bits, revision/class code fields, header type, BIST, BARs, ROM base, adapter ID, interrupt line/pin, and latency/min-grant fields.
- Interrupt state: MSI enable/multiple-message/64-bit/per-vector/ext-data fields, MSI message address/data/mask/pending fields, and MSI-X table/PBA location plus enable/function-mask/table-size state.
- Error-reporting state: AER uncorrectable/correctable status, masks, severity, first-error pointer, ECRC generation/check capability and enable bits, multiple header recording, header logs, and TLP prefix logs.
- Link and PHY state: link control/status, link control/status 2, lane equalization coefficients, equalization-complete flags, lane error status, 16 GT/s status, parity mismatch status, and lane margining control/status.
- Isolation and address-translation state: ACS, ATS, page request, PASID, ARI, multicast, and SR-IOV fields.
- Power and timing state: PMI status/control, DBESL, LTR, power-budget data, DPA capability/status/control/substate power allocation, and RTR reset/link/FLR/D3hot timing fields.

Persistence across GPU reset, PCI function-level reset, BACO, suspend/resume, runtime power management, or hot reset is not specified by this header. Those semantics depend on the hardware block and on driver reinitialization paths that reprogram or reread these fields.

## Dependencies and Integration Points

This file is useful only with the adjacent generated NBIO 7.11 register metadata:

- `nbio_7_11_0_offset.h` for register offsets that pair with these field names.
- `nbio_7_11_0_smn.h` for SMN-addressed NBIO registers where applicable.
- `nbio_7_11_0_default.h` for reset/default values where generated.
- Neighboring chunks of `nbio_7_11_0_sh_mask.h`: the previous chunk owns the start of `BIF_CFG_DEV0_EPF1_LINK_STATUS2`, and the next chunk continues `BIF_CFG_DEV2_EPF0` after `LATENCY`.

Likely AMDGPU integration areas include:

- NBIO 7.11 initialization and low-level register access paths that include generated ASIC register headers.
- PCIe capability setup, link management, and error handling code in the AMDGPU/SOC15 stack.
- RAS and diagnostic paths that read AER, lane error, parity mismatch, TLP prefix, and header-log registers.
- SR-IOV and virtualization code paths that need VF count, offset, stride, page-size, VF BAR, ARI, ACS, ATS, and PASID field geometry.
- Power-management code that inspects or programs PCI power management, LTR, DPA, power-budget, and readiness-time-reporting capabilities.

Integration is name-based and fragile: a caller must use the `*_SHIFT` and `*_MASK` macros for the same register as the address macro being accessed. The header does not include value enums for multi-bit fields, so interpretation of field values comes from PCIe specifications, ASIC register documentation, or companion driver code.

## Risks

- A wrong shift or mask can silently corrupt PCIe configuration programming. In this chunk, high-impact fields include MSI/MSI-X enables, AER masks/severity, ACS/ATS/PASID controls, SR-IOV controls, BAR resize controls, and link equalization/margining controls.
- The chunk starts and ends in the middle of logical register blocks. `BIF_CFG_DEV0_EPF1_LINK_STATUS2` begins in the previous chunk, and `BIF_CFG_DEV2_EPF0` continues in the next chunk. Per-file reconciliation must merge adjacent chunks before judging completeness.
- Many repeated lane registers use lane-indexed names for lanes 0-15. A generator error affecting one lane can be hard to catch if tests exercise only lane 0 or only the negotiated active-width subset.
- AER fields are similar across status, mask, and severity registers. Mixing them up can hide real hardware errors, report stale errors, or classify fatal/nonfatal/corrected errors incorrectly.
- Capability fields are repeated for `DEV0_EPF1` and `DEV0_EPF2` with mostly parallel schemas but not identical capability coverage. Copying assumptions from one endpoint function to the other can reference nonexistent or differently scoped fields.
- BAR and VF BAR resize controls can affect address aperture layout. Incorrect programming can break MMIO mapping, VF resource assignment, or guest-visible BAR sizing.
- SR-IOV, ATS, PASID, ACS, and ARI fields touch isolation and address-translation behavior. Bad writes can compromise peer-to-peer isolation expectations or make DMA/address-translation behavior inconsistent with IOMMU setup.
- Lane margining, equalization, and 16 GT/s PHY fields are diagnostic/control surfaces for physical-link behavior; using them outside documented sequences can destabilize the link.

## Test and Validation Signals

Useful validation is mostly mechanical plus hardware-facing smoke coverage:

- Build AMDGPU configurations that include NBIO 7.11 generated headers to catch malformed or missing macro names.
- Run a generated-header consistency check that every complete register in this line range has expected `__SHIFT`/`_MASK` pairs for each field, allowing the intentional boundary splits at `DEV0_EPF1_LINK_STATUS2` and `DEV2_EPF0_LATENCY`.
- Cross-check every register name in this chunk against the matching NBIO 7.11 offset/default headers so field masks are paired with address/default metadata where expected.
- Compare repeated schemas across `DEV0_EPF1` and `DEV0_EPF2`, especially MSI/MSI-X, AER, BAR enhanced capability, power budget, DPA, ACS, PASID, ARI, and RTR fields.
- Validate AER by injecting or provoking controlled correctable and uncorrectable PCIe errors on supported hardware and confirming status, mask, severity, header-log, TLP-prefix-log, and clear behavior.
- Validate MSI/MSI-X setup by enabling interrupts, masking vectors, checking pending bits, and confirming message address/data handling under interrupt load.
- Exercise SR-IOV-capable configurations, checking VF count, stride, offset, page-size, VF BAR, ARI, ACS, ATS, and PASID reporting against PCI config-space dumps.
- Exercise link diagnostics by comparing link status, lane error, equalization, 16 GT/s parity mismatch, and lane margining fields with `lspci`, debugfs, and hardware validation tools on affected ASICs.
- Run reset, FLR, suspend/resume, and runtime power-management coverage to ensure driver code reinitializes policy fields and interprets readiness-time-reporting and DPA/PMI state correctly.

## Chunk Boundary Notes

Line 7363 begins with the last four `BIF_CFG_DEV0_EPF1_LINK_STATUS2` mask definitions; the corresponding register comment and shift definitions are in the previous work item. Lines 7367-8761 complete the remainder of `DEV0_EPF1` through `BIF_CFG_DEV0_EPF1_RTR_DATA2`. Lines 8762-9770 cover `DEV0_EPF2` from standard PCI identity fields through `BIF_CFG_DEV0_EPF2_RTR_DATA2`. Lines 9771-9837 start `DEV2_EPF0` and stop at `BIF_CFG_DEV2_EPF0_LATENCY`; the rest of that address block belongs to the following chunk.
