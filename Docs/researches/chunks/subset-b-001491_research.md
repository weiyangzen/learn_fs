# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_sh_mask.h lines 8788-12892

## Purpose

This chunk is a generated AMDGPU BIF 5.1 register field mask/shift section. It contains no executable C logic; its purpose is to publish compile-time constants for decoding and programming PCIe/BIF hardware registers on Sea Islands / GCN-era AMD GPUs that use the BIF 5.1 register map.

The line range is centered on downstream PCIe functions `D2F3`, `D2F4`, and the beginning of `D2F5`. Each register field is represented as paired macros:

- `REGISTER__FIELD_MASK` gives the already-positioned bit mask.
- `REGISTER__FIELD__SHIFT` gives the field's least-significant bit position.

Driver code combines these field constants with register address constants from the matching `bif_5_1_d.h` header and accesses the device through AMDGPU register helpers such as `RREG32_PCIE()`, `WREG32_PCIE()`, and indirect PCIE index/data helpers. The header is therefore a hardware layout contract: correctness depends on exact masks and shifts, not on local algorithms in this file.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or storage objects in this chunk. The macro namespace is the API surface.

The requested range starts in the tail of `D2F3_PCIE_ERR_CNTL` and continues through the rest of the `D2F3` function's PCIe internal, PCIe capability, bridge/configuration-space, MSI, power-management, error-reporting, virtual-channel, equalization, ACS, and multicast definitions. It then covers a full `D2F4` function block and the first part of `D2F5`.

Major macro groups in this range are:

- PCIe internal transaction/link control for `D2F3`, `D2F4`, and `D2F5`: `PCIE_TX_*`, `PCIE_RX_*`, `PCIE_ERR_CNTL`, `PCIE_FC_*`, `PCIEP_ERROR_INJECT_*`, `PCIEP_PORT_CNTL`, `PCIEP_HW_DEBUG`, and `PCIEP_SCRATCH`.
- Link controller programming: `PCIE_LC_CNTL`, `PCIE_LC_CNTL2`, `PCIE_LC_CNTL3`, `PCIE_LC_CNTL4`, `PCIE_LC_CNTL5`, `PCIE_LC_CNTL6`, `PCIE_LC_BW_CHANGE_CNTL`, `PCIE_LC_TRAINING_CNTL`, `PCIE_LC_LINK_WIDTH_CNTL`, `PCIE_LC_N_FTS_CNTL`, `PCIE_LC_SPEED_CNTL`, `PCIE_LC_CDR_CNTL`, `PCIE_LC_LANE_CNTL`, `PCIE_LC_FORCE_COEFF`, `PCIE_LC_BEST_EQ_SETTINGS`, `PCIE_LC_FORCE_EQ_REQ_COEFF`, and `PCIE_LC_STATE0` through `PCIE_LC_STATE5`.
- PCI configuration-space fields: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`, bridge window fields, secondary status, bridge/IRQ bridge control, and bus-number fields.
- PCIe capability fields: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `SLOT_CAP`, `SLOT_CNTL`, `SLOT_STATUS`, `ROOT_CNTL`, `ROOT_CAP`, `ROOT_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`, `SLOT_CAP2`, `SLOT_CNTL2`, and `SLOT_STATUS2`.
- MSI and power-management capability fields: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, message address/data fields, MSI mapping capability/address fields, `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`.
- Advanced PCIe capabilities: vendor-specific extended capability headers, VC capability/control/status for VC0/VC1, device serial number, AER uncorrectable/correctable status/mask/severity, AER capability/control, header and TLP-prefix logs, root error command/status/source ID, secondary PCIe capability, link control 3, lane error status, lane equalization controls, ACS capability/control, and multicast capability/control/address/block/overlay fields.

The `D2F4` section is the most complete in this chunk. It includes the function's direct port index/data pair, PCIEP port/debug controls, full TX/RX credit and error fields, full link-controller definitions, complete capability/configuration-space fields, per-lane equalization controls for lanes 0-15, ACS fields, and multicast fields. `D2F3` is complete only after accounting for lines before this chunk, and `D2F5` is only partially covered here.

## Control Flow

This file has no runtime control flow. Every line is a preprocessor definition. Runtime behavior appears only in consumers that read, mask, shift, modify, and write hardware registers.

A typical caller flow is:

1. Select a BIF/PCIe register address from `bif_5_1_d.h`, for example an `ixD2F4_PCIE_LC_SPEED_CNTL`-style indirect register or a `D2F4_PCIE_PORT_INDEX/DATA` path.
2. Read the register with the ASIC's PCIe access helper.
3. Extract a field with `(value & REGISTER__FIELD_MASK) >> REGISTER__FIELD__SHIFT`, or clear and insert a new field value with the same pair.
4. Write the modified register back if the field is writable and the link/power state permits it.

The control-sensitive fields are concentrated in the link-controller and transaction layers. Examples include speed-change initiation, link width reconfiguration, equalization redo/quiesce controls, link reset/recovery controls, ASPM/L0s/L1 behavior, completion timeout controls, RX ignore/unsupported-request policy, TX replay and flow-control settings, and error injection bits. The macro definitions themselves do not enforce safe sequencing.

## State And Persistence Behavior

The header stores no software state and has no persistence mechanism. It describes state held in GPU hardware registers.

The described hardware state includes PCIe function configuration and capabilities, link speed and width, ASPM and L-state policy, lane reversal and equalization state, TX/RX flow-control credits, sequence/replay status, requester IDs, AER status and masks, MSI and power-management capability fields, virtual-channel resource state, ACS policy, multicast address/block settings, and debug/error-injection controls.

Persistence depends on the specific register and platform sequencing. Some fields are status-only snapshots, some are sticky status or write-one-to-clear error fields, some are strap-derived capability fields, and some are control/override fields that remain programmed until a later driver or firmware write, PCIe retrain, function reset, hot reset, suspend/resume transition, power-gating/BACO transition, or full device reset. The mask header does not encode those access semantics, so consumers must rely on the hardware specification and established AMDGPU sequences.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register naming contract and the matching BIF 5.1 address header, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_d.h`. The address header supplies the register locations such as `ixD2F3_PCIE_RX_CNTL`, `ixD2F4_PCIE_LC_SPEED_CNTL`, and `ixD2F5_PCIE_TX_CNTL`; this file supplies the fields inside those registers.

Direct include points found in this tree are the CIK/Sea Islands interrupt-handler sources:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/iceland_ih.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cz_ih.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/tonga_ih.c`

More broadly, the same AMDGPU BIF/PCIe access pattern is used by ASIC setup, PCIe link management, power management, interrupt handling, debugfs register access, and hardware diagnostics. Register helpers and indirect accessors live outside this header; this file only provides the bit layout.

Although the path is under a local `ceph-client` source mirror, this chunk is AMDGPU Linux kernel driver register metadata. It has no Ceph filesystem semantics, distributed-storage protocol behavior, or persistent filesystem state.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. A wrong mask or shift can compile cleanly while reading the wrong status bit, failing to update a desired field, or corrupting neighboring fields in packed PCIe registers.

High-risk fields include link training and power controls such as `LC_RESET_LINK`, `LC_RECONFIG_NOW`, `LC_RENEGOTIATE_EN`, `LC_INITIATE_LINK_SPEED_CHANGE`, `LC_GO_TO_RECOVERY`, `LC_REDO_EQ`, `LC_SET_QUIESCE`, ASPM/L0s/L1 inactivity fields, lane powerdown permissions, and equalization preset/coefficient controls. Incorrect use can leave the device at the wrong width/speed, trigger retraining loops, quiesce traffic, or destabilize suspend/resume.

RX/TX transaction controls are also sensitive. `RX_IGNORE_*`, completion timeout disables, NAK controls, TPH/PASID-related unsupported-request ignores, TX replay controls, requester ID fields, advertised/initialized credit fields, and flow-control update thresholds can change error handling, ordering, and liveness. Misprogramming these fields can mask real PCIe errors or generate spurious AER/completion-timeout behavior.

Capability and strap-like fields must be treated carefully. Device, link, slot, root, VC, ACS, multicast, MSI, and power-management fields describe what PCI enumeration and the OS believe the function supports. Changing or mis-decoding them can cause feature exposure mismatches, broken virtualization/IOMMU isolation expectations, incorrect MSI behavior, or bad power-management negotiation.

The repetitive `D2F3`/`D2F4`/`D2F5` naming makes copy/generation errors hard to spot. A field value that is correct for one function but attached to another function's macro would only show up when that downstream function is used. Per-lane equalization macros are similarly repetitive and vulnerable to lane-number or half-register mixups.

This chunk has line-boundary splits. It begins after the first `D2F3_PCIE_ERR_CNTL` mask/shift entries have already been defined, and it ends inside `D2F5_PCIE_LC_CNTL3`; later lines continue that register and the rest of `D2F5`. The final per-file merge should avoid treating those boundaries as real omissions in the source file.

## Test Signals

Useful validation signals are mostly compile-time and hardware-behavior oriented:

- Kernel build coverage for AMDGPU ASICs that include `bif_5_1_sh_mask.h`; missing, renamed, or malformed macros should surface as compile failures in CIK/Sea Islands paths.
- Static register-map validation comparing every generated `*_MASK`/`*__SHIFT` pair against AMD's source register database and the adjacent address definitions in `bif_5_1_d.h`.
- PCIe link bring-up, retrain, suspend/resume, and runtime power-management tests that confirm negotiated speed, width, lane reversal, ASPM/L-state behavior, and recovery/equalization status remain sane.
- PCIe error-path tests that exercise AER correctable/uncorrectable status, completion timeout, unsupported request, ECRC/LCRC, malformed TLP, and header/TLP-prefix log behavior.
- Flow-control and liveness checks that watch posted, non-posted, and completion credit status across TX/RX paths.
- MSI, power-management, virtual-channel, ACS, and multicast capability inspection from PCI configuration space to ensure decoded fields match expected hardware capabilities.
- Debug or lab diagnostics using error-injection, lane equalization, link-controller state registers, and per-lane status fields to confirm the expected bit positions are observed.

Regression symptoms from bad constants include link stuck at a lower generation, reduced link width after resume, repeated link retraining, GPU disappearance after power transitions, unexpected AER noise, masked PCIe errors, broken MSI/configuration-space reporting, or diagnostics showing activity on the wrong lane/function.

## Cross-Chunk Notes

Earlier chunks of `bif_5_1_sh_mask.h` define the beginning of the BIF 5.1 mask namespace and the first part of the `D2F3` downstream-function block. Later chunks continue `D2F5` after `PCIE_LC_CNTL3` and complete the rest of the header. The final per-file research document should treat the full file as one generated hardware register layout contract rather than as independent algorithms per chunk.
