# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_sh_mask.h lines 9895-12283

## Scope

This chunk is a generated AMD NBIO 7.9.0 register field header section. It contains preprocessor constants only: each hardware register field is represented by a `__SHIFT` constant and a matching `_MASK` constant. There are no C functions, structs, enums, storage objects, or executable control flow in this range.

The covered range starts at the tail of the `BIF_CFG_DEV0_EPF0_0_PCIE_SRIOV_FIRST_VF_OFFSET` definition and then describes a large PCIe configuration-space span for `DEV0_EPF0_0`, followed by the beginning of a second address block for `DEV0_EPF1_0`. The macros are paired with register-address constants from `nbio_7_9_0_offset.h` and are consumed through AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15*`, and `WREG32_SOC15*` in NBIO and RAS code.

## Purpose

The purpose of this chunk is to give NBIO 7.9.0 driver code stable symbolic names for bit extraction and bit construction in PCIe/NBIO registers. It avoids hard-coded shifts and masks in consumers and keeps the driver aligned with the generated hardware register database.

The covered registers describe:

- SR-IOV virtual-function layout and VF BAR configuration for endpoint function 0.
- Data Link Feature and high-speed PCIe PHY capability/status fields.
- PCIe 16.0 GT/s and 32.0 GT/s equalization, parity, and link-status fields.
- PCIe lane margining controls/status for lanes 0 through 15.
- AMD GPU IOV vendor-specific capability fields, including host/VF mailbox bits, framebuffer partition registers, scheduler data words, and engine interrupt bitmap registers.
- Standard PCI configuration header and capability blocks for endpoint function 1.
- MSI/MSI-X layout for endpoint function 1.
- Vendor-specific and Advanced Error Reporting fields for endpoint function 1, ending in the uncorrectable-error mask block.

## Important APIs, Types, and Functions

This header range does not define APIs in the function-call sense. Its important interface is the naming convention used by AMDGPU register helper macros:

- `BIF_CFG_DEV0_EPF0_0_<REGISTER>__<FIELD>__SHIFT`: bit offset of a field inside the named register.
- `BIF_CFG_DEV0_EPF0_0_<REGISTER>__<FIELD>_MASK`: bit mask for that field.
- `BIF_CFG_DEV0_EPF1_0_<REGISTER>__<FIELD>__SHIFT` and `_MASK`: same convention for endpoint function 1.

Consumers normally combine these with:

- `REG_GET_FIELD(value, REGISTER, FIELD)` to extract fields using `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`.
- `REG_SET_FIELD(value, REGISTER, FIELD, field_value)` to write a field into a composed register value.
- `RREG32_SOC15*` and `WREG32_SOC15*` to read or write the actual NBIO register identified by the companion `reg...` macro in `nbio_7_9_0_offset.h`.

Direct consumers observed in this source tree include `drivers/gpu/drm/amd/amdgpu/nbio_v7_9.c` and `drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_nbio_v7_9.c`, both of which include this header alongside `nbio_7_9_0_offset.h`. The specific fields in this chunk are more likely to be used by SR-IOV, PCIe capability, AER, mailbox, virtualization, or diagnostic paths than by the basic doorbell setup paths shown in `nbio_v7_9.c`.

## Register Groups Covered

### EPF0 SR-IOV Capability Tail

The range begins with the end of `BIF_CFG_DEV0_EPF0_0_PCIE_SRIOV_FIRST_VF_OFFSET`, then defines:

- `PCIE_SRIOV_VF_STRIDE`: spacing between VFs in PCI function numbering.
- `PCIE_SRIOV_VF_DEVICE_ID`: device ID reported for VFs.
- `PCIE_SRIOV_SUPPORTED_PAGE_SIZE` and `PCIE_SRIOV_SYSTEM_PAGE_SIZE`: page-size capability/control fields.
- `PCIE_SRIOV_VF_BASE_ADDR_0` through `_5`: VF BAR aperture values.
- `PCIE_SRIOV_VF_MIGRATION_STATE_ARRAY_OFFSET`: split into a BAR indicator (`BIR`, bits 0-2) and an aligned offset field (bits 3-31).

These are state-bearing PCI configuration fields. Writes may affect VF enumeration, BAR layout, and migration-related memory placement.

### Data Link Feature and 16 GT/s Link Blocks

`PCIE_DLF_ENH_CAP_LIST`, `DATA_LINK_FEATURE_CAP`, and `DATA_LINK_FEATURE_STATUS` describe capability-list metadata, locally supported DLF bits, DLF exchange enable, remote supported bits, and validity status.

The 16 GT/s group includes:

- `PCIE_PHY_16GT_ENH_CAP_LIST`.
- Reserved `LINK_CAP_16GT` and `LINK_CNTL_16GT`.
- `LINK_STATUS_16GT` bits for equalization complete, phase 1/2/3 success, and equalization request.
- `LOCAL_PARITY_MISMATCH_STATUS_16GT`, `RTM1_PARITY_MISMATCH_STATUS_16GT`, and `RTM2_PARITY_MISMATCH_STATUS_16GT`.
- `LANE_0_EQUALIZATION_CNTL_16GT` through `LANE_15_EQUALIZATION_CNTL_16GT`, each exposing downstream-port and upstream-port 16 GT/s TX preset nibbles.

The per-lane repetition is significant: all lanes use the same field layout, but the generated names encode the lane number. Any table-driven consumer must map lane indices to distinct register symbols in C, since these are preprocessor names rather than indexable data.

### PCIe Lane Margining

The margining block starts with `PCIE_MARGINING_ENH_CAP_LIST`, `MARGINING_PORT_CAP`, and `MARGINING_PORT_STATUS`. It then defines control/status pairs for lanes 0 through 15:

- `LANE_N_MARGINING_LANE_CNTL` fields: receiver number, margin type, usage model, and margin payload.
- `LANE_N_MARGINING_LANE_STATUS` fields: status mirrors for receiver number, margin type, usage model, and payload.

These fields support PCIe margining diagnostics. They are likely used by low-level bring-up, validation, or service tooling rather than normal display operation. Incorrect masks here can corrupt diagnostic commands or misread link-quality status on a per-lane basis.

### 32 GT/s Link Capability, Control, and Status

The 32 GT/s registers describe PCIe Gen5 link behavior:

- `LINK_CAP_32GT`: support for equalization bypass to highest rate, no-equalization-needed mode, and modified training-sequence usage modes.
- `LINK_CNTL_32GT`: disable/select bits for equalization bypass, no-equalization-needed, and modified training-sequence usage mode.
- `LINK_STATUS_32GT`: equalization phase status, link equalization request, modified training sequence reception, enhanced link behavior control, transmitter precoding status/request, and no-equalization-needed received.

These are hardware link-training fields. Consumers must treat them as hardware-owned or link-state-sensitive unless the PCIe specification and ASIC programming guide allow writes.

### GPUIOV Vendor-Specific Capability

The chunk defines a large AMD vendor-specific capability for GPU IOV under `BIF_CFG_DEV0_EPF0_0_PCIE_VENDOR_SPECIFIC_*_GPUIOV`.

Notable fields include:

- Enhanced capability list metadata: capability ID, version, and next pointer.
- Vendor-specific header fields: VSEC ID, revision, and length.
- Interrupt enable/status fields for HVVM mailbox transmit-ack and receive-valid events.
- `RESET_CONTROL__SOFT_PF_FLR`: software PF function-level reset control.
- `HVVM_MBOX_DW0`: selected VF index, transmit data, transmit valid bit, receive data, and receive acknowledgement bit.
- `HVVM_MBOX_DW1`: per-VF transmit-ack and receive-valid bits for VF0 through VF15.
- `HVVM_MBOX_DW2`: per-VF transmit-ack and receive-valid bits for VF16 through VF31.
- `CONTEXT`, `TOTAL_FB`, `REGION`, `P2P_OVER_XGMI_ENABLE`, and `VF0_FB` through `VF30_FB`: virtualization resource/configuration fields.
- `OFFSETS` through `OFFSETS4`: encoded resource offset fields.
- Scheduler data words for UVD0 through UVD11 and GFX0 through GFX7, each as `DW0` through `DW8` full-width 32-bit masks.
- Engine interrupt enable/status bitmaps for `ENGA_A0_7`, `ENGA_A8_15`, `ENGB_B0_7`, and `ENGB_B8_15`.

This section is the highest-risk part of the chunk because it describes virtualization mailbox, reset, framebuffer partitioning, and scheduler state surfaces. A bad mask or mismatched register address can affect PF/VF coordination, VF memory assignment, interrupt routing, or reset semantics.

### EPF1 Standard PCI Configuration Header

The address-block comment switches to `aid_nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp`, and the names change to `BIF_CFG_DEV0_EPF1_0_*`.

The EPF1 standard header fields include:

- `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, and `STATUS`.
- `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS`.
- `CACHE_LINE`, `LATENCY`, `HEADER`, and `BIST`.
- BARs `BASE_ADDR_1` through `BASE_ADDR_6`.
- `CARDBUS_CIS_PTR`, `ADAPTER_ID`, `ROM_BASE_ADDR`, `CAP_PTR`.
- Interrupt line/pin and min-grant/max-latency fields.
- Vendor capability, adapter ID write alias, and power-management capability/status/control.

These fields represent PCI configuration state for a secondary endpoint function. They interact with generic PCI enumeration and resource assignment logic, even though this header only gives AMDGPU code the bit layout.

### EPF1 PCIe, MSI, MSI-X, VSEC, and AER

The EPF1 PCIe capability block covers:

- PCIe capability list metadata and capability word.
- Device capability/control/status.
- Link capability/control/status.
- Device capability/control/status 2.
- Link capability/control/status 2.

The MSI/MSI-X block covers:

- MSI capability metadata and message control.
- MSI address/data fields, extended message-data fields, mask and pending registers, and 64-bit variants.
- MSI-X capability metadata, table size/function mask/enable, table BAR indicator and offset, and PBA BAR indicator and offset.

The VSEC and AER block covers:

- Vendor-specific enhanced capability list and header.
- Two full-width scratch/vendor-specific registers.
- Advanced Error Reporting enhanced capability list.
- `PCIE_UNCORR_ERR_STATUS`: uncorrectable PCIe error status bits such as data-link protocol error, surprise down, poisoned TLP, flow-control protocol error, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC error, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress blocked, TLP prefix blocked, and poisoned TLP egress blocked.
- `PCIE_UNCORR_ERR_MASK`: the same bit positions represented as mask-control fields. The chunk ends before the complete surrounding AER group finishes; the next chunk continues with the remaining mask bits/severity/correctable-error definitions.

## Control Flow

There is no runtime control flow in this chunk. The effective control flow appears in consumers:

1. Driver code reads a register value through a SOC15 register accessor using a `reg...` offset macro.
2. It extracts a field with `REG_GET_FIELD`, which depends on these `__SHIFT` and `_MASK` definitions.
3. For writes, it composes or updates a register value with `REG_SET_FIELD`.
4. It writes the result back through a `WREG32_SOC15*` accessor.

For stateful capability/configuration registers, the hardware, firmware, PCI core, hypervisor, or PF/VF management path may also update the register asynchronously from the perspective of ordinary AMDGPU code.

## State and Persistence Behavior

The header itself has no memory or persistence. The defined fields describe hardware or PCI configuration state that persists in device registers across normal software reads/writes and usually resets on device reset, function-level reset, bus reset, or ASIC reset.

State-sensitive areas in this chunk include:

- SR-IOV VF counts, spacing, BARs, page size, and migration state offset. These affect VF exposure and guest-visible configuration.
- Link status, equalization, parity mismatch, and margining fields. These reflect physical link state and may change as the PCIe link trains or diagnostics run.
- GPUIOV mailbox valid/ack/status fields. These are handshake state and may be consumed by PF/VF, firmware, hypervisor, or management logic.
- GPUIOV framebuffer and scheduler data words. These describe virtualization resource assignment or scheduling state.
- EPF1 command/status, MSI/MSI-X, and AER masks/status. These affect PCI enablement, interrupt routing, and error reporting behavior.

Because many fields are PCI configuration-space fields, writes may be visible outside the driver through PCI config reads, guest VF configuration, firmware policy, or host error-reporting paths.

## Dependencies

Direct dependencies for useful consumption are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_offset.h`: provides the matching register addresses and base indices.
- AMDGPU register helper macros in the AMDGPU driver infrastructure, including `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15*`, and `WREG32_SOC15*`.
- SOC15/NBIO instance routing and ASIC register access plumbing in AMDGPU.
- PCIe, SR-IOV, AER, MSI/MSI-X, and AMD GPU IOV hardware specifications for the semantics behind the fields.

The generated naming must stay synchronized with the offset header. A correct mask with a mismatched `reg...` offset still produces incorrect hardware access.

## Integration Points

Observed local integration points:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_9.c` includes this mask header and the matching offset header. That file implements NBIO operations such as revision detection, memory-controller access gating, doorbell aperture setup, interrupt handling, register remap, partition-mode reads, and RAS interrupt fallback handling.
- `drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_nbio_v7_9.c` includes the same headers while registering NBIO RAS interrupt sources.
- The matching `nbio_7_9_0_offset.h` defines register symbols for many covered fields, including SR-IOV registers, GPUIOV VSEC registers, and EPF1 configuration/AER registers.

Likely broader integration points:

- SR-IOV PF/VF setup and management paths use the SR-IOV and GPUIOV fields to expose VFs, map VF BARs, partition framebuffer, and communicate mailbox state.
- PCIe diagnostics or service tooling may use the 16 GT/s, 32 GT/s, equalization, parity, and margining definitions.
- Interrupt and error-reporting paths use MSI/MSI-X and AER definitions when configuring endpoint-function interrupt behavior or interpreting PCIe errors.
- RAS/error telemetry may consume PCIe error status bits, even if this specific chunk does not define executable RAS handlers.

## Risks and Review Notes

- Generated-header drift is the primary risk. If this file is regenerated from an incorrect register database, all consumers compile cleanly but operate on wrong bits.
- Field-name duplication by convention is easy to misuse. For example, `*_MASK_MASK` names are valid generated symbols for mask registers, not a typo.
- The range starts and ends inside larger logical groups. Any manual review or merge must include adjacent chunks for complete SR-IOV and AER context.
- GPUIOV mailbox and reset fields are sensitive. Writing valid/ack/reset bits with the wrong mask can break PF/VF handshakes or trigger unexpected reset behavior.
- Per-lane PCIe fields are repetitive. Copy/paste or table-generation mistakes can silently target the wrong lane.
- Reserved/full-width fields such as scheduler `DWn` and vendor scratch registers should not be interpreted without the matching hardware specification.
- Link-training and margining fields can be hardware-owned. Polling or writing them without respecting PCIe timing/state rules can produce misleading diagnostics or unstable link behavior.
- PCI config command/status, MSI/MSI-X, and AER mask/status writes affect system-visible behavior and may interact with Linux PCI core ownership.

## Test Signals

Useful validation signals for changes involving this chunk:

- Compile coverage for AMDGPU with NBIO 7.9.0 enabled; this catches missing or renamed generated symbols.
- Static comparison against the authoritative register database or a known-good generated header, especially for shift/mask pairs and lane/VF repetition.
- Boot/probe on NBIO 7.9.0 hardware with `amdgpu` loaded; confirm no register-access faults or PCI enumeration regressions.
- SR-IOV validation: PF probe, VF creation, VF BAR sizing, VF device ID exposure, guest VF probe, and GPUIOV mailbox traffic.
- PCIe link validation: expected negotiated speed/width, equalization completion bits, and absence of unexpected parity/margining errors under normal operation.
- AER validation: correct reporting/masking of EPF1 PCIe uncorrectable errors, ideally through controlled PCIe error injection or platform error logs.
- Interrupt validation: MSI/MSI-X enablement and delivery for EPF1 paths if that function is active.
- RAS validation: NBIO RAS interrupt registration still succeeds and PCIe/NBIO error telemetry remains coherent.

## Summary

Lines 9895-12283 define the bit-level ABI between AMDGPU NBIO 7.9.0 software and a large PCIe configuration/register surface. The chunk is not executable code, but it is high impact because the macros govern SR-IOV layout, PCIe link diagnostics, GPU IOV mailbox/resource state, EPF1 interrupt configuration, and the beginning of EPF1 AER handling. Correctness depends on exact synchronization between these masks, the companion offset header, and the underlying NBIO 7.9.0 hardware register specification.
