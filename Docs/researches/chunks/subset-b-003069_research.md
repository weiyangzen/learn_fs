# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 2467-4969

## Scope

This chunk is a generated AMD NBIO 7.0 register shift/mask header segment. It contains C preprocessor constants only: `*_SHIFT` bit positions and `*_MASK` bit masks for PCIe/NBIO configuration-space fields. There are no C functions, structs, enums, variables, direct register reads or writes, allocation paths, locks, loops, or branches in this range.

The source path is under a local `ceph-client` source mirror, but this file is AMDGPU hardware metadata for the Linux DRM AMD driver. It is not Ceph filesystem logic.

The assigned range covers lines 2467-4969 of `nbio_7_0_sh_mask.h`. It starts in the middle of the `BIF_CFG_DEV1_RC0_PCIE_VC0_RESOURCE_CAP` field list, continues through the rest of the DEV1 root-complex PCIe extended-capability field masks, then covers two PCIe dummy configuration blocks, most of the DEV0 endpoint function 0 field masks including AER, ATS/PRI/PASID/SR-IOV and AMD GPUIOV vendor-specific fields, and ends inside the first DEV0 endpoint function 1 PCIe device capability block.

## Purpose

The purpose of this header segment is to publish symbolic bitfield definitions for NBIO 7.0 PCI/PCIe configuration registers. AMDGPU code pairs these macros with register offsets from `nbio_7_0_offset.h` when extracting fields from register values or composing values for read/modify/write operations.

Each logical register is represented by one or more `__<FIELD>__SHIFT` constants and matching `__<FIELD>_MASK` constants. The macros describe how a field is packed in the register, not whether that field is writable, read-only, sticky, write-one-to-clear, firmware-owned, PCI-core-owned, or safe for a driver-side update.

## Important Macro Families

The opening `BIF_CFG_DEV1_RC0_PCIE_*` portion finishes the DEV1 root-complex PCIe extended capability map. It covers virtual-channel resources for VC0 and VC1, serial-number extended capability dwords, AER capability fields, uncorrectable/correctable error status, masks and severity controls, header and TLP-prefix logs, root-error command/status/source ID fields, secondary PCIe link-control and lane-equalization fields for lanes 0 through 15, and ACS capability/control masks. These names are prefixed with `BIF_CFG_DEV1_RC0_`, distinguishing this root-complex view from the unprefixed DEV0 EPF0 endpoint view later in the chunk.

The `NB_PCIEDUMMY0_0_*` and `NB_PCIEDUMMY1_0_*` blocks provide compact dummy PCIe configuration images. Each has vendor/device identity fields, status/command bits, class-code/revision fields, and header-type fields. These are small decode surfaces compared with the full endpoint/root-complex blocks.

The `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` block uses mostly unprefixed names such as `COMMAND`, `STATUS`, `DEVICE_CAP`, `PCIE_UNCORR_ERR_STATUS`, and `PCIE_SRIOV_CONTROL`. It defines DEV0 endpoint function 0 PCI configuration-space field layout. The first part mirrors standard PCI header and capability fields: vendor/device ID, command/status, revision/class, BARs, ROM BAR, capability pointer, interrupt line/pin, vendor capability, power management capability/status, PCIe capability, device/link capability/control/status, Device/Link Capability 2, MSI, MSI-X table/PBA, vendor-specific capability, virtual-channel capability, serial number, AER, and BAR enhanced capability.

The EPF0 AER block is detailed. It includes uncorrectable error status/mask/severity fields for DLP, surprise-down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC-blocked TLP, AtomicOp egress blocked, and TLP prefix blocked conditions. Correctable error status/mask fields include receiver error, bad TLP/DLLP, replay rollover, replay timer timeout, advisory non-fatal, corrected internal error, and header-log overflow. AER capability/control fields include first-error pointer, ECRC generation/check capability and enable bits, multiple-header recording, TLP prefix log present, completion-timeout prefix/header log capability, and log overflow status.

The EPF0 PCIe feature-capability portion covers power budget, dynamic power allocation, secondary PCIe link-control/equalization, ACS, ATS, page request interface, PASID, TPH requester, multicast, LTR, ARI, and SR-IOV. These fields are important to DMA isolation, address translation, peer routing, virtualization, PCIe ordering, and platform power policy. For example, ATS control includes `STU` and `ATC_ENABLE`, PRI has enable/reset/status and outstanding request counters, PASID has enable and permission-mode bits, and SR-IOV has VF enable, migration, VF memory-space enable, ARI hierarchy, VF counts, VF BARs, supported/system page size, and migration-state array fields.

The AMD GPUIOV vendor-specific extended capability block starts at `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST_GPUIOV` and is one of the most hardware-specific parts of this slice. It includes VSEC list/header fields, `SRIOV_SHADOW` fields for VF enable and VF number, interrupt enable/status bits for GFX/UVD/VCE command-complete, self-recovered hang, FLR-needed hang, VM-busy transition events, plus HVVM mailbox transmit-ack and receive-valid interrupts. It also defines `RESET_CONTROL` for software PF FLR, `HVVM_MBOX_DW0` message/index fields, `HVVM_MBOX_DW1` per-VF `TRN_ACK` and `RCV_VALID` bits for VF0 through VF15, `HVVM_MBOX_DW2` PF ack/valid bits, GPUIOV context and frame-buffer accounting fields, per-VF frame-buffer base/size fields for VF0 through VF15, and scheduler dwords for UVD, VCE, and GFX.

The closing `nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` block begins the DEV0 endpoint function 1 field map. In this chunk it covers standard PCI identity/header fields through `BIF_CFG_DEV0_EPF1_0_DEVICE_CAP`. The next chunk must cover the rest of EPF1 PCIe capabilities and extended capabilities.

## APIs, Types, And Functions

This chunk exports no typed API. Its public interface is the set of preprocessor macro names made visible by including `nbio_7_0_sh_mask.h`.

The practical API contract is the generated AMDGPU register-header convention:

- `nbio_7_0_offset.h` provides register offsets for the same logical register names.
- `nbio_7_0_sh_mask.h` provides field shifts and masks for those registers.
- `nbio_7_0_default.h` provides reset/default values for selected registers.
- Including code uses masks and shifts with register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, and explicit bit operations around AMDGPU register accessors.

Because this is a generated mask header, consumers depend on exact spelling and namespace matching. The unprefixed EPF0 macros, the `BIF_CFG_DEV1_RC0_` root-complex macros, and the `BIF_CFG_DEV0_EPF1_0_` endpoint-function-1 macros are separate register namespaces even when they describe similar PCIe standard fields.

## Control Flow

There is no executable control flow in this header. Runtime control flow occurs in including code:

1. Driver code reads a PCIe/NBIO register through an AMDGPU access path or obtains a configuration value through a PCI/config-space path.
2. It applies one of these `*_MASK` values and shifts by the matching `*_SHIFT` to decode a field.
3. For writable fields, it composes a new value using the mask/shift pair, usually through AMDGPU helper macros, and writes it back through the relevant hardware access path.
4. Hardware, firmware, the Linux PCI core, the PF driver, or a virtualization manager observes or updates the underlying state depending on field ownership.

The chunk itself does not sequence device initialization, link training, SR-IOV enablement, mailbox handshakes, AER handling, or reset. It only defines the bit positions those paths must use when they touch NBIO 7.0 registers.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-backed state in PCI/PCIe configuration and vendor-specific extended capability registers.

The represented state includes PCI identity and class fields, command/status bits, BAR and ROM BAR address fields, power-management state, PCIe device/link/slot capabilities and controls, MSI/MSI-X configuration, VC arbitration state, AER status/mask/severity/log registers, secondary PCIe lane-equalization controls and lane error status, ACS routing controls, ATS/PRI/PASID address-translation controls, TPH requester policy, multicast controls, LTR capability values, ARI next-function and function-group controls, SR-IOV VF enumeration and VF BAR/page-size/migration state, and AMD GPUIOV PF/VF mailbox, interrupt, reset, context, frame-buffer, and scheduler state.

Ownership is mixed. Generic PCI header and capability fields overlap Linux PCI core ownership. AER fields may be hardware-updated and sometimes sticky. SR-IOV and GPUIOV fields are typically PF or virtualization-manager owned. ATS/PRI/PASID fields cross driver, IOMMU, and PCIe core policy. The mask header does not encode those ownership rules or side effects.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 7.0 register database staying synchronized. Register names in this file need to align with offset macros in `nbio_7_0_offset.h` and defaults in `nbio_7_0_default.h`. A mismatch can compile if all macros still exist, but the driver may manipulate the wrong bitfield.

The direct integration domain is AMDGPU NBIO and PCIe support. The constants are relevant anywhere NBIO 7.0 code decodes or programs PCIe configuration-space fields, link controls, AER handling, interrupt setup, SR-IOV virtualization, or GPU IOV mailbox state.

The Linux PCI core is an implicit integration point. Standard PCIe fields such as command/status, PM, MSI/MSI-X, AER, ACS, ATS, PASID, PRI, ARI, LTR, and SR-IOV have generic kernel policy and enumeration behavior. AMDGPU-specific code must avoid treating generic PCI-owned fields as private NBIO state unless the access is intentionally hardware-specific and coordinated.

IOMMU and virtualization paths are also key integration points. ATS, PRI, PASID, ACS, ARI, SR-IOV, VF BAR, migration, and GPUIOV fields affect DMA translation, peer routing, VF exposure, PF/VF isolation, mailbox delivery, reset handling, and frame-buffer partitioning.

Hardware diagnostics and reliability paths integrate through AER and lane-status fields. Uncorrectable/correctable error masks, severities, root-error reporting, header/TLP-prefix logs, link control 3, and per-lane equalization masks are the bit definitions consumers need when collecting error evidence or changing PCIe error policy.

## Risks And Edge Cases

- These are untyped preprocessor constants. A stale or incorrect mask/shift can compile cleanly and still corrupt PCIe configuration or decode status incorrectly.
- The namespace is repetitive and easy to confuse. `BIF_CFG_DEV1_RC0_PCIE_*`, unprefixed `PCIE_*`, and `BIF_CFG_DEV0_EPF1_0_PCIE_*` may describe analogous standard PCIe fields for different functions or hardware views.
- The chunk boundaries are artificial. The range begins after the first two `BIF_CFG_DEV1_RC0_PCIE_VC0_RESOURCE_CAP` field definitions and ends before the full EPF1 PCIe capability set, so whole-file conclusions require adjacent chunk reports.
- Standard PCIe fields have side effects and ownership rules not visible here. Status and AER bits can be sticky or write-one-to-clear; control fields can trigger link, reset, interrupt, or translation behavior.
- AER log and mask/severity fields are diagnostic-critical. Incorrect masks or field extraction can hide root causes, misclassify fatal/non-fatal errors, or clear evidence during read/modify/write sequences.
- ATS, PRI, PASID, ACS, ARI, SR-IOV, and multicast fields affect DMA routing and isolation. Wrong bit definitions or namespace mixups can break IOMMU translation, allow unintended peer traffic, expose VFs incorrectly, or destabilize passthrough/virtualization.
- GPUIOV mailbox and interrupt fields have dense per-engine and per-VF packing. An off-by-one VF bit, wrong ack/valid bit, or wrong interrupt mask can lose PF/VF messages, route events to the wrong VF, or wedge virtualization management.
- Per-VF frame-buffer allocation fields and total frame-buffer accounting are packed as base/limit or available/consumed fields. Bad masks can mis-partition VRAM or cause VF-visible memory ranges to overlap.
- Lane equalization fields are repeated for lanes 0 through 15. Copy or generation drift between lane numbers can make link-training diagnostics or overrides target the wrong physical lane.
- Several fields use full-width masks such as `0xFFFFFFFFL`, while others use narrow 8/16-bit masks in 32-bit registers. Consumers must preserve reserved bits when updating writable fields.

## Test Signals

Useful validation is mostly build-time, generated-header consistency, and hardware integration:

- Build AMDGPU configurations that include NBIO 7.0 support. Missing or renamed field macros should surface in code that includes `nbio_7_0_sh_mask.h`.
- Cross-check this mask range against `nbio_7_0_offset.h` for matching logical register names across DEV1 RC0, DEV0 EPF0, dummy PCIe blocks, and DEV0 EPF1.
- Run basic PCIe enumeration and device bring-up on NBIO 7.0 ASICs, watching command/status, BAR sizing, PM capability, PCIe capability, MSI/MSI-X, AER, and link-status paths.
- Exercise PCIe error reporting with platform AER diagnostics where available, confirming uncorrectable/correctable status, mask, severity, root-error status, source ID, header log, and TLP-prefix log fields decode as expected.
- Validate link training and recovery paths at supported link speeds and widths, including Link Control 3 and lane 0-15 equalization/status reporting.
- Run SR-IOV scenarios with PF/VF enumeration, VF enable/disable, VF memory-space enable, VF BAR exposure, VF page-size programming, VF migration-state fields, PF/VF reset, and MSI/MSI-X delivery.
- Exercise GPU IOV mailbox flows, checking HVVM mailbox `TRN_ACK`/`RCV_VALID` bits for VF0-VF15, PF ack/valid bits, GPUIOV interrupt enable/status fields, and GFX/UVD/VCE scheduler dword handling.
- Test IOMMU-backed features where platform support exists: ACS routing, ATS enablement, PRI page request handling, PASID enablement and permission bits, ARI next-function behavior, TPH requester configuration, and multicast/LTR policy.
- Use suspend/resume, runtime power management, GPU reset, FLR, and passthrough stress as integration tests because these paths combine PCIe status/control, AER, SR-IOV, ATS/PASID, and GPUIOV reset/mailbox state.

## Chunk Notes

- Lines 2467-2976 finish DEV1 RC0 PCIe VC, serial-number, AER, root-error, secondary PCIe, lane equalization, and ACS field masks.
- Lines 2977-3028 cover two small `NB_PCIEDUMMY*_0` PCIe dummy configuration blocks.
- Lines 3029-4432 cover DEV0 EPF0 standard PCI header fields, PM/PCIe/MSI/MSI-X, VC, serial number, AER, BAR enhanced, power budget, DPA, secondary PCIe, ACS, ATS, PRI, PASID, TPH, multicast, LTR, ARI, and SR-IOV fields.
- Lines 4433-4768 cover the AMD GPUIOV vendor-specific capability: VSEC header, SR-IOV shadow, GPUIOV interrupt enable/status, soft PF FLR, HVVM mailbox dwords, context, frame-buffer accounting, per-VF frame-buffer fields, and UVD/VCE/GFX scheduler dwords.
- Lines 4769-4969 begin DEV0 EPF1 standard PCI/PM/PCIe capability masks and stop inside `BIF_CFG_DEV0_EPF1_0_DEVICE_CAP`; the remainder of EPF1 is outside this work item.
