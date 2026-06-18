# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 46535-48958

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask header slice. It contains only C preprocessor constants for register-field shifts and masks in NBIF/BIF PCI configuration decode space. There are no functions, structs, enums, executable statements, allocation paths, locks, or runtime initialization in this range.

The range starts in the middle of the `BIF_CFG_DEV0_EPF0_VF14_PCIE_CAP` definitions, completes the rest of the `EPF0_VF14` PCIe capability block, covers the full `nbio_nbif0_bif_cfg_dev0_epf0_vf15_bifcfgdecp` virtual-function block, and then begins `nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` through the first `PCIE_MC_RCV0` shift definition. The chunk ends before the `PCIE_MC_RCV0` mask and before later EPF1 multicast, LTR, ARI, SR-IOV, and trailing register families.

## Purpose

The macros provide symbolic bit layouts for NBIO 4.3.0 PCI/PCIe configuration registers so AMDGPU code can decode and compose hardware register values without embedding raw bit numbers. The dominant interface is the paired macro convention:

- `BIF_CFG_DEV0_EPF0_VF14_<REGISTER>__<FIELD>__SHIFT`
- `BIF_CFG_DEV0_EPF0_VF14_<REGISTER>__<FIELD>_MASK`
- `BIF_CFG_DEV0_EPF0_VF15_<REGISTER>__<FIELD>__SHIFT`
- `BIF_CFG_DEV0_EPF0_VF15_<REGISTER>__<FIELD>_MASK`
- `BIF_CFG_DEV0_EPF1_<REGISTER>__<FIELD>__SHIFT`
- `BIF_CFG_DEV0_EPF1_<REGISTER>__<FIELD>_MASK`

The companion generated offset header supplies concrete register addresses and base indices; this file supplies the field encodings consumed by `REG_GET_FIELD`, `REG_SET_FIELD`, and direct mask/shift operations.

## Register Coverage

The `EPF0_VF14` portion is partial at the beginning. It starts after the first `PCIE_CAP` shift fields and then covers the rest of VF14's PCIe capability and extended capability layout:

- PCIe capability, device, and link registers: `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, plus PCIe 2.0 style `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- MSI/MSI-X: capability list pointers, MSI message control, message address/data fields, mask and pending fields, 64-bit variants, MSI-X table size/function mask/enable, table BIR/offset, and PBA BIR/offset.
- Vendor-specific PCIe extended capability header and payload registers.
- Advanced Error Reporting: uncorrectable status/mask/severity, correctable status/mask, AER capability/control, four TLP header log words, and four TLP prefix log words.
- ARI enhanced capability, ARI capability, and ARI control fields.

The `EPF0_VF15` block is complete in this chunk. It repeats the full per-VF PCI configuration model:

- Standard PCI header registers: vendor/device ID, command, status, revision and class code bytes, cache line, latency, header type, BIST, six BARs, CardBus CIS pointer, subsystem adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, and max latency.
- PCIe capability, device/link control and status, completion timeout, FLR, ASPM/L1 PM substates, link speed/width, link retrain/disable, autonomous width/speed disable, equalization completion, and link speed vector fields.
- MSI/MSI-X, vendor-specific PCIe extended capability, AER, TLP logs, TLP prefix logs, and ARI.

The `EPF1` block begins at line 47795 and is partial at the end. In this chunk it covers:

- Standard PCI header registers and base address fields for endpoint function 1.
- Vendor capability list and writable adapter ID fields.
- Power Management Interface: `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`.
- PCIe capability, device/link control and status, MSI/MSI-X, vendor-specific capability, device serial number, AER, and TLP log fields.
- Resizable BAR enhanced capability and `BAR1` through `BAR6` capability/control fields.
- Power budget capability/data/select fields.
- Dynamic Power Allocation capability, status/control, latency indicator, and substate power allocation registers 0 through 7.
- Secondary PCIe extended capability, link control 3, lane error status, and lane 0 through lane 15 equalization control fields.
- ACS capability/control, PASID capability/control, and the start of multicast capability registers: `PCIE_MC_ENH_CAP_LIST`, `PCIE_MC_CAP`, `PCIE_MC_CNTL`, `PCIE_MC_ADDR0`, `PCIE_MC_ADDR1`, and the first shift definition for `PCIE_MC_RCV0`.

## Important APIs, Types, and Functions

There are no callable APIs, declared types, or functions in this chunk. The externally visible interface is the macro namespace.

Important macro families:

- `*_COMMAND__*` and `*_STATUS__*` mirror standard PCI command/status bits, including I/O access, memory access, bus mastering, special cycle, memory write/invalidate, VGA palette snoop, parity response, SERR, fast back-to-back enable, interrupt disable, capability-list presence, abort status, parity status, and PME status.
- `*_BASE_ADDR_*`, `*_ROM_BASE_ADDR__*`, `*_MSIX_TABLE__*`, `*_MSIX_PBA__*`, and EPF1 resizable BAR control fields expose BAR-like encodings where low bits are attributes, BIR selectors, or enable bits rather than address bits.
- `*_PCIE_CAP*`, `*_DEVICE_*`, and `*_LINK_*` define PCIe version/type, slot implementation, interrupt message number, payload and read request sizing, relaxed ordering, no-snoop, FLR, completion timeout, ASPM, L1 PM substates, link speed, link width, retrain/disable, common clock, extended sync, bandwidth interrupt enables, equalization completion, and compliance flags.
- `*_MSI_*` and `*_MSIX_*` cover interrupt capability programming: MSI enable, multi-message capability and enable values, 64-bit address support, per-vector masking support, address/data programming, masks, pending bits, MSI-X table size, function mask, table location, and PBA location.
- `*_PCIE_UNCORR_ERR_*`, `*_PCIE_CORR_ERR_*`, and `*_PCIE_ADV_ERR_CAP_CNTL__*` encode AER status, reporting masks, severity classification, ECRC generation/check support and enables, multi-header recording, first-error pointer, completion-timeout prefix/header logging, and TLP prefix log presence.
- `*_PCIE_HDR_LOG*` and `*_PCIE_TLP_PREFIX_LOG*` expose raw captured diagnostic words for PCIe error analysis.
- `*_PCIE_ARI_*` encodes alternate routing-ID support, next function number, and function group controls for VF14/VF15.
- EPF1-only capability families in this range add serial number fields, resizable BAR sizing/control, power budget reporting, DPA power allocation, secondary capability link control and lane equalization, ACS peer-to-peer/isolation controls, PASID enablement and width, and multicast base/receive/control definitions.

## Control Flow

This header chunk has no runtime control flow. Inclusion is controlled by the enclosing header guard outside this slice. At compile time, translation units including `nbio_4_3_0_sh_mask.h` receive these constants.

Typical consumer flow is inferred from the generated-register pattern:

1. Use the matching `nbio_4_3_0_offset.h` register macro to identify the MMIO/config-space address.
2. Read the register through AMDGPU PCI config, NBIO, or MMIO helpers.
3. Extract fields using the `*_MASK` and `*_SHIFT` constants, usually through generated register helper macros.
4. Compose and write new values when enabling PCIe features, interrupt routing, AER policy, power management, BAR sizing, ACS/PASID/multicast policy, or VF-visible configuration state.

## State and Persistence Behavior

The header stores no software state and persists nothing. It describes state held by PCI/PCIe hardware configuration registers.

Control fields described here can persist until reset, function-level reset, PF reconfiguration, or driver/PCI core writes. Examples include command bits such as memory access and bus mastering, interrupt disable, MSI/MSI-X enable and mask bits, payload/read request size, completion timeout control, link control, AER masks and severity bits, ECRC enables, ARI controls, EPF1 resizable BAR sizing enables, power-management controls, ACS isolation controls, PASID enables, and multicast controls.

Status and diagnostic fields are hardware-owned or sticky according to PCIe semantics. Examples include device and link status, AER correctable and uncorrectable status, first-error pointer, TLP header and prefix logs, MSI pending bits, lane error status, equalization completion flags, DPA status, and multicast receive bits. These may be read-only, write-one-to-clear, clear-on-reset, or hardware-updated depending on the underlying register.

The VF14 and VF15 blocks represent SR-IOV virtual-function configuration decode windows under `EPF0`. EPF1 is a separate endpoint-function configuration block with richer physical-function style capabilities in this range, including resizable BAR, power budget, DPA, ACS, PASID, and multicast support.

## Dependencies and Integration Points

This chunk integrates with:

- `nbio_4_3_0_offset.h`, which maps these symbolic field layouts to concrete register offsets and base indices.
- `nbio_4_3_0_default.h`, where generated defaults for the same ASIC register set are expected.
- AMDGPU generated register helpers such as `REG_GET_FIELD` and `REG_SET_FIELD`, which rely on the exact `__SHIFT`/`_MASK` naming convention.
- NBIO 4.3 code such as `amdgpu/nbio_v4_3.c`, and SMU 13 power-management files that include `nbio/nbio_4_3_0_sh_mask.h`.
- Linux PCI/PCIe, MSI/MSI-X, SR-IOV, AER, ARI, ACS, PASID/IOMMU, resizable BAR, power management, and DPA concepts mirrored by the field names.
- Firmware and hardware register database generation. The file is generated and should generally be updated from the authoritative register description rather than hand-edited.

## Risks and Edge Cases

- This range has chunk-boundary partial registers. It starts after the first `VF14_PCIE_CAP` shift fields and ends before the `EPF1_PCIE_MC_RCV0` mask; reconciliation should avoid treating those two register definitions as complete inside this chunk alone.
- The definitions are highly repetitive. Copy-generation drift between VF14, VF15, and EPF1 register families can be hard to detect visually because most macro names differ only by function or VF number.
- A wrong shift or mask silently corrupts all consumers of that field. This is especially risky for AER status/mask/severity fields, which have similar names but different behavior.
- BAR, ROM BAR, MSI-X table/PBA, resizable BAR, and multicast address fields contain encoded attribute or selector bits. Consumers must not treat every masked bit as a plain byte address.
- Link-control, equalization, autonomous width/speed, and retrain fields can affect link stability and device reachability when written incorrectly.
- Interrupt fields have multiple layers of masking and enablement. Confusing MSI mask/pending fields, MSI-X function mask, and PCI command interrupt disable can produce lost or unexpected interrupts.
- ACS and PASID controls interact with IOMMU isolation and process-address-space translation. Incorrect enablement can break DMA translation or peer-to-peer access policy.
- AER fields may be sticky and write-one-to-clear. Using the wrong mask or severity definition can clear evidence, hide errors, or misclassify fatal/non-fatal conditions.
- Literal mask widths vary from byte and word fields to full 32-bit fields, all expressed as `L` constants. Callers should avoid implicit truncation, signedness, or read-modify-write assumptions.

## Test Signals

Useful validation signals for this chunk:

- Build coverage of AMDGPU translation units that include `nbio_4_3_0_sh_mask.h`; malformed macro names or missing field pairs should fail compile-time consumers.
- Generated-register consistency checks against `nbio_4_3_0_offset.h`, `nbio_4_3_0_default.h`, and the upstream hardware register database.
- Pattern checks comparing `EPF0_VF15` against neighboring VF blocks, with explicit allowance that `EPF0_VF14` is partial in this chunk.
- Pattern checks comparing EPF1 fields against other ASIC versions with the same capability families, especially ACS, PASID, multicast, DPA, power budget, and resizable BAR definitions.
- SR-IOV runtime tests that enumerate enough VFs to exercise VF14 and VF15, bind/unbind guest or host drivers, trigger VF FLR, and verify command, MSI/MSI-X, AER, and ARI-visible config state.
- Interrupt tests that program MSI and MSI-X vectors, toggle masks, inspect pending bits, and verify delivery and quiescence for VF and EPF1 contexts.
- PCIe capability inspection with `lspci -vv` or driver debug output to confirm payload sizes, link speed/width, FLR support, completion timeout, MSI/MSI-X, AER, ARI, ACS, PASID, power budget, and resizable BAR fields match hardware expectations.
- AER injection or observation tests validating uncorrectable/correctable status, masks, severity, first-error pointer, header logs, and TLP prefix logs.
- Link training and equalization diagnostics for EPF1, including lane error status and lane 0 through 15 equalization control fields.
- Reset/lifecycle tests around PF reset, VF FLR, SR-IOV enable/disable, suspend/resume, and hotplug-like teardown to ensure control/status fields return to expected defaults.
