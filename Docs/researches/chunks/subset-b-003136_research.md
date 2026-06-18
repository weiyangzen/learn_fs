# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 34497-36940

## Scope

This chunk covers lines 34497-36940 of AMDGPU's generated NBIO 7.11.0 shift/mask header. The range is C preprocessor register metadata only: comments naming registers/address blocks and `#define` constants for bit shifts and already-positioned masks. It has no executable functions, structs, enums, allocation, locks, I/O, or direct runtime side effects.

The chunk starts inside the `BIF_CFG_DEV0_EPF6_0` PCIe configuration space block, covers the remainder of the EPF6 extended capability area, covers a full `BIF_CFG_DEV0_EPF7_0` endpoint-function PCI configuration block, then enters the `nbio_nbif0_bif_cfg_dev1_rc_bifcfgdecp` root-complex block through most of `BIF_CFG_DEV1_RC0_PCIE_UNCORR_ERR_MASK`.

## Purpose

`nbio_7_11_0_sh_mask.h` gives AMDGPU driver code symbolic field geometry for NBIO 7.11.0 registers. This specific slice describes PCI configuration and PCIe extended-capability fields for NBIF endpoint functions EPF6/EPF7 and the beginning of DEV1 RC0. Driver code pairs these macros with matching register address macros from the NBIO 7.11.0 offset/SMN headers and with helper macros such as `REG_GET_FIELD` or `REG_SET_FIELD` to decode status, compose read-modify-write values, and avoid hard-coded bit literals.

The covered fields map to standard and AMD-specific PCIe configuration concepts: command/status, BARs, MSI/MSI-X, PCI PM, PCIe device/link/slot/root capabilities and controls, Advanced Error Reporting, vendor-specific capabilities, resizable BAR controls, dynamic power allocation, ACS, PASID, ARI, routing ID interpretation, root-port bridge windows, virtual channels, serial number capability, and PCIe uncorrectable-error status/mask bits.

## Important APIs, Types, and Macros

There are no callable APIs or data types in this range. The generated public interface is the repeated macro form:

- `<REGISTER>__<FIELD>__SHIFT`: zero-based starting bit for a field.
- `<REGISTER>__<FIELD>_MASK`: field mask shifted into register position.

Important register families in this chunk are:

- EPF6 tail registers: `BIF_CFG_DEV0_EPF6_0_LINK_CNTL2`, `LINK_STATUS2`, MSI and MSI-X capability registers, SATA capability and IDP registers, vendor-specific capability/header/scratch registers, AER status/mask/severity/capability/header-log/TLP-prefix-log registers, BAR enhanced capability and BAR1-BAR6 resize controls, power-budgeting registers, dynamic power allocation, ACS, PASID, ARI, and RTR capability/data fields.
- Full EPF7 standard PCI header fields: vendor/device IDs, command/status, revision/class codes, cache/latency/header/BIST, six BARs, adapter ID, ROM base, capability pointer, interrupt pin/line, min grant/max latency, and vendor/adapter capability aliases.
- EPF7 power-management and PCIe capability fields: `PMI_CAP_LIST`, `PMI_CAP`, `PMI_STATUS_CNTL`, `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- EPF7 interrupt capability registers: MSI capability list/control/address/data/mask/pending fields and MSI-X capability list/control/table/PBA fields.
- EPF7 extended capabilities: SATA, vendor-specific, AER, resizable BAR, power budget, DPA, ACS, PASID, ARI, and RTR registers with the same field schemas as EPF6.
- DEV1 RC0 standard/root-port PCI configuration fields: command/status, class/header/BIST, BARs, secondary/subordinate bus numbers, bridge latency, I/O and memory base/limit windows, prefetchable upper base/limit, capability pointer, ROM base, interrupt fields, bridge control, and extended bridge control.
- DEV1 RC0 PCIe root-port capability fields: PM, PCIe capability, device/link/slot/root capability/control/status registers, second-generation device/link/slot registers, MSI capability, SSID and MSI-map capabilities, vendor-specific capability, virtual-channel capability and resource registers, device serial number, AER capability list, and uncorrectable-error status/mask fields.
- AER uncorrectable-error fields are repeated for EPF6, EPF7, and DEV1 RC0. They include DLP, surprise-down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, AtomicOp egress blocked, TLP prefix blocked, and poisoned-TLP egress blocked bits.
- Correctable-error fields for EPF6 and EPF7 include receiver error, bad TLP, bad DLLP, replay rollover, replay timeout, advisory nonfatal, internal corrected, header-log overflow, and corrected internal/status mask bits.

## Control Flow and Runtime Behavior

This header chunk has no runtime control flow. Its behavior is compile-time substitution of constants into driver code that performs PCI configuration-space or NBIO register accesses.

The implied hardware flows are:

1. PCI core or AMDGPU NBIO code reads and writes endpoint-function configuration registers using address macros and these masks to enable bus mastering, memory and I/O decoding, parity/SERR reporting, interrupts, and capability-specific controls.
2. Link-management code can inspect or program PCIe link capability/control/status fields, including negotiated width/speed, ASPM, retrain/link disable, extended sync, autonomous bandwidth, target link speed, compliance controls, equalization state, crosslink/RTM presence, and DRS indicators.
3. Interrupt setup code can interpret MSI/MSI-X capability list pointers, enable bits, multiple-message fields, 32-bit versus 64-bit message address/data layouts, table/PBA BAR indicators, masks, and pending bitmaps.
4. AER or RAS-adjacent PCIe error handling code reads status and masks, records header/TLP-prefix logs, checks severity, and programs ECRC and multi-header controls. The same uncorrectable-error bit layout appears for endpoint functions and the root-complex port.
5. Resizable BAR, DPA, ACS, PASID, ARI, power budget, and RTR paths use capability-list and control fields to expose or constrain PCIe features used by the OS, firmware, or GPU driver.
6. DEV1 RC0 root-port bridge fields describe subordinate bus routing, I/O and memory window apertures, bridge error controls, root-control interrupt enables, root status, slot controls, and VC resource negotiation.

The header does not order operations, clear sticky status bits, or enforce PCIe capability dependencies. Callers must still follow PCI/PCIe programming rules, NBIO access rules, and hardware reset/power sequencing requirements.

## State and Persistence

The file owns no software state and persists nothing. The represented state lives in NBIO/PCIe hardware registers and PCI configuration space.

State represented by this chunk includes:

- EPF6 and EPF7 endpoint capability state for link controls, interrupt delivery, PCIe errors, BAR sizing, power budgeting, DPA, ACS, PASID, ARI, routing ID interpretation, and vendor-specific scratch fields.
- EPF7 PCI identity/configuration state, including command/status enables, class information, BARs, ROM base, capability chain pointers, and interrupt routing.
- DEV1 RC0 bridge/root-port state, including bus-number windows, I/O/memory/prefetchable apertures, bridge control bits, PM/PCIe capabilities, device/link/slot/root controls and statuses, virtual-channel resource controls, serial number dwords, and AER status/mask latches.
- Sticky or latched hardware observation state in status registers such as PCI status, device/link/slot/root status, MSI pending bits, AER status, VC negotiation pending/status bits, and header/TLP-prefix logs.

Retention across GPU reset, function-level reset, BACO, suspend/resume, runtime power transitions, or PCI hot reset is not defined here. AMDGPU initialization and PCI core restore paths must reprogram non-retained control state and treat status retention according to NBIO/ASIC documentation.

## Dependencies and Integration Points

This chunk depends on the surrounding generated NBIO 7.11.0 register headers:

- `nbio_7_11_0_offset.h` for corresponding config/MMIO register offsets.
- `nbio_7_11_0_smn.h` for SMN-addressed registers where applicable.
- `nbio_7_11_0_default.h` for reset/default values.
- Adjacent chunks of `nbio_7_11_0_sh_mask.h`; this chunk starts after the first part of EPF6 and ends before the completion of the DEV1 RC0 uncorrectable-error mask and severity block.

Likely integration areas in the AMDGPU tree are:

- NBIO 7.11 setup and low-level access code that includes generated NBIO register metadata.
- SOC15-era register helpers that combine register offsets with `*_SHIFT` and `*_MASK` values.
- PCIe link setup, power-management, interrupt, resizable-BAR, PASID/ARI/ACS, and AER/error-reporting paths.
- Firmware or platform-management code that needs consistent views of PCIe capability layouts for endpoint functions and root-complex ports.
- Kernel PCI core interactions where AMDGPU or platform code mirrors standard PCI capability state through ASIC-specific register windows.

Because the symbols are generated, integration is primarily by exact name matching. A field macro must be paired with the correct register address macro for the same ASIC generation and register block.

## Risks

- Wrong shifts or masks can silently program unrelated PCI configuration bits. In this range that can affect memory decoding, bus mastering, interrupt enablement, link retraining, BAR sizing, AER masking, bridge windows, or root-port slot/root behavior.
- The chunk is highly repetitive across EPF6 and EPF7. Generator or copy/paste mistakes may only affect one function and can be missed if validation covers a single endpoint function.
- AER status, mask, and severity registers share very similar field names. Mixing status and mask macros can hide errors or report false faults.
- MSI/MSI-X layouts include overlapping offset behavior between 32-bit and 64-bit forms. Using the wrong `*_64` field set or address/data field can break interrupt delivery.
- Resizable BAR control fields are repeated for BAR1-BAR6. Programming an unsupported size or the wrong BAR control field can expose incorrect apertures to the PCI core.
- DEV1 RC0 bridge window fields control downstream I/O and memory routing. Incorrect base/limit composition can break enumeration, DMA reachability, or isolation.
- ACS, PASID, ARI, AtomicOp, IDO, LTR, OBFF, and TLP-prefix controls influence ordering, translation, routing, and isolation behavior. Incorrect enablement can create subtle interoperability or security issues.
- The work item ends mid-register at `BIF_CFG_DEV1_RC0_PCIE_UNCORR_ERR_MASK`: the final five mask definitions for ACS violation through poisoned-TLP egress blocked are inside this chunk, while the next chunk begins with the remaining mask fields and then the severity register. Merge/reconciliation should treat that as a chunking artifact, not an inherent source defect.

## Test and Validation Signals

Useful validation is mostly mechanical plus hardware/PCIe behavior testing:

- Build an AMDGPU configuration that includes NBIO 7.11.0 headers to catch malformed macro definitions and symbol-name drift.
- Run a generated-header consistency check that each complete register in this line range has paired `__SHIFT` and `_MASK` definitions, allowing the intentional boundary split at `BIF_CFG_DEV1_RC0_PCIE_UNCORR_ERR_MASK`.
- Cross-check register names against `nbio_7_11_0_offset.h` and defaults so the shift/mask register names have matching address/default definitions where expected.
- Compare repeated EPF6 and EPF7 capability schemas for symmetry in field positions, especially MSI/MSI-X, AER, BAR resize, power budget, DPA, ACS, PASID, ARI, and RTR registers.
- Exercise PCIe link setup on NBIO 7.11.0 hardware and confirm link status, equalization, target speed, retrain/autonomous-bandwidth, and link-capability fields decode correctly.
- Validate interrupt setup by enabling MSI and MSI-X and checking message address/data, mask, pending, table, and PBA behavior.
- Validate AER handling by injecting or provoking controlled correctable and uncorrectable PCIe errors where available, then checking status/mask/severity/header-log/TLP-prefix-log decoding for EPF and RC paths.
- Validate resizable BAR enumeration and resize flows for every BAR control register described here.
- Validate root-port bridge configuration by checking subordinate bus numbers, I/O/memory/prefetchable windows, slot/root status bits, and virtual-channel negotiation on systems that expose DEV1 RC0.

## Chunk Boundary Notes

The first line completes the preceding `BIF_CFG_DEV0_EPF6_0_LINK_CAP2` register by providing only `DRS_SUPPORTED_MASK`. The prior chunk owns most of that register's shifts and masks.

The range then continues through the rest of EPF6, the entire EPF7 configuration block, and the start of DEV1 RC0. The final visible register, `BIF_CFG_DEV1_RC0_PCIE_UNCORR_ERR_MASK`, is incomplete at the line boundary: this chunk includes shifts for all uncorrectable-error mask fields and masks through `ACS_VIOLATION_MASK_MASK`; subsequent masks and the following severity register are expected in the next chunk.
