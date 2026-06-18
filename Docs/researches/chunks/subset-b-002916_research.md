# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 29341-31771

## Scope

This chunk covers generated NBIO 2.3 shift/mask definitions for SR-IOV virtual-function PCI configuration-space fields. It starts in the `BIF_CFG_DEV0_EPF0_VF1_DEVICE_ID` field definitions, then contains the rest of the VF1 PCI/PCIe capability bitfields, complete VF2 and VF3 PCI configuration bitfields, and the beginning of VF4 through `BIF_CFG_DEV0_EPF0_VF4_LINK_CAP2`.

The file is data-only C preprocessor material. It defines no functions, structs, variables, locks, allocations, or direct MMIO operations. Its public interface is the generated pair convention:

- `<REGISTER>__<FIELD>__SHIFT` for a field bit offset.
- `<REGISTER>__<FIELD>_MASK` for the field mask.

## Purpose

`nbio_2_3_sh_mask.h` is the bitfield side of the NBIO 2.3 hardware ABI. The companion `nbio_2_3_offset.h` header gives the register/config-space offsets, and `nbio_2_3_default.h` gives reset/default values. AMDGPU code combines these names with register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and `WREG32_FIELD15`.

This chunk describes how virtual functions VF1, VF2, VF3, and the first part of VF4 expose PCI and PCIe configuration bits: command/status, identity/class/header fields, BARs, PCIe link/device capabilities, MSI/MSI-X, vendor-specific extended capability fields, Advanced Error Reporting, ATS, and ARI. These definitions matter for SR-IOV because PF, VF, firmware, and hypervisor paths need a consistent bit layout when presenting and controlling each virtual function's PCI config space.

## Important Macro Families

### VF1 Configuration and Capability Fields

The range begins after the VF1 `VENDOR_ID` comment and inside `BIF_CFG_DEV0_EPF0_VF1_DEVICE_ID`. It then covers nearly the entire VF1 configuration map:

- PCI command/status fields such as IO and memory access enables, bus mastering, parity/SERR behavior, interrupt disable, readiness, capability-list presence, and abort/parity status bits.
- Class/header fields including revision ID, programming interface, subclass, base class, cache-line size, latency timer, header type, BIST, six BAR-sized base-address masks, CardBus CIS pointer, subsystem/vendor adapter ID, ROM BAR, capability pointer, interrupt line/pin, and min/max latency.
- PCIe capability fields: capability-list header, PCIe version/device type, device capability/control/status, link capability/control/status, device capability/control/status 2, and link capability/control/status 2.
- MSI and MSI-X fields: message control, 32-bit and 64-bit message address/data registers, mask and pending registers, MSI-X table and pending-bit-array fields.
- Extended capabilities: vendor-specific capability headers/data, AER uncorrectable/correctable status/mask/severity, AER capability/control, header logs, TLP prefix logs, ATS capability/control, and ARI capability/control.

The VF1 PCIe control fields include feature toggles for error reporting, relaxed ordering, payload/read-request size, extended tags, no-snoop, function-level reset, completion timeout, ARI forwarding, atomic operations, ID-based ordering, LTR, emergency power reduction, ten-bit tags, OBFF, and end-to-end TLP prefix blocking. Link fields expose supported/current speed and width, ASPM/power-management controls, retrain/disable/common-clock controls, bandwidth status/interrupt enables, compliance controls, and de-emphasis/margin settings.

### Complete VF2 and VF3 Maps

The chunk then enters `addressBlock: nbio_nbif0_bif_cfg_dev0_epf0_vf2_bifcfgdecp` and later `vf3_bifcfgdecp`. VF2 and VF3 repeat the same register-family layout as VF1, beginning with `VENDOR_ID` and `DEVICE_ID` and continuing through ARI control.

These repeated maps are not abstractions; each VF number has its own generated macro names. That lets driver, firmware, or tooling refer to a specific virtual function's config-space fields without runtime string construction, but it also means mechanical drift between repeated families is a real risk.

### VF4 Partial Map

The final section starts `addressBlock: nbio_nbif0_bif_cfg_dev0_epf0_vf4_bifcfgdecp`. It covers VF4 identity, command/status, class/header, BAR, adapter, interrupt, PCIe device/link capability/control/status, device capability/control/status 2, and `LINK_CAP2`.

The chunk ends at `BIF_CFG_DEV0_EPF0_VF4_LINK_CAP2__DRS_SUPPORTEDRESERVED_MASK`. VF4 `LINK_CNTL2`, `LINK_STATUS2`, MSI/MSI-X, vendor-specific, AER, ATS, and ARI fields continue in the next chunk.

## Control Flow

There is no executable control flow in this header. The flow is compile-time and external:

1. AMDGPU NBIO 2.3 or related SR-IOV code includes the generated NBIO offset, mask, and default headers.
2. Code selects the needed VF register/config-space macro.
3. Helper macros shift and mask fields when composing writes or decoding reads.
4. PCIe/NBIO hardware, firmware, or hypervisor state changes according to the resulting register access.

Because these are PCI configuration-space definitions, access may be through PCI config mechanisms, SMN/index-data paths, PF-mediated virtualization code, or firmware/hypervisor interfaces rather than ordinary direct C calls in this header.

## State and Persistence Behavior

The header has no local state. It names hardware-visible state in NBIO PCI configuration registers for virtual functions. That state persists until reset, FLR, VF teardown, power transition, firmware action, hypervisor action, or explicit driver writes.

Important state represented here includes:

- Per-VF PCI identity, class, header, BAR, ROM, subsystem, interrupt, and capability-chain presentation.
- PCI command/status enables and error/status latches.
- PCIe device and link capability/control/status fields, including negotiated link width/speed, payload sizing, read request sizing, relaxed ordering, no-snoop, FLR, completion timeout, LTR, OBFF, and compliance controls.
- MSI/MSI-X programming state for VF1-VF3, including message address/data, masking, pending bits, table location, and PBA location.
- AER status, masks, severity, capability/control, captured header log, and TLP prefix log fields.
- ATS and ARI capability/control state used by address translation and alternative routing ID behavior.

Several fields are command-like or write-one-to-clear style in the PCIe specification, such as status/error bits, FLR initiation, link retraining, AER clear/status fields, and interrupt pending/mask controls. The macros only describe bit positions; ordering, polling, and clear semantics come from the owning PCIe/NBIO code and hardware specification.

## Dependencies and Integration Points

This chunk depends on the generated NBIO 2.3 header set:

- `nbio_2_3_offset.h` supplies the matching `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` offsets.
- `nbio_2_3_default.h` supplies reset/default values for related NBIO registers.
- AMDGPU SOC15/register helpers consume the generated `__SHIFT` and `_MASK` names through field composition/extraction macros.

Observed source-tree integration includes:

- `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, which includes `nbio_2_3_sh_mask.h` with the matching offset/default headers for NBIO 2.3 register programming.
- `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, which includes this mask header in virtualization-oriented AMDGPU code.
- `drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c` and `sienna_cichlid_ppt.c`, which include the same generated NBIO headers for NBIO/PCIe-related SMU platform behavior.

The specific `BIF_CFG_DEV0_EPF0_VF*` fields align with the offset-header chunk that maps per-VF PCI configuration offsets. The mask header gives bit-level interpretation for those offsets; it does not by itself identify the access path or access permissions for PF versus VF contexts.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can alter unrelated PCIe configuration bits, break VF enumeration, disable memory/bus-master access, misreport capabilities, or mask real PCIe errors.
- Repeated VF maps are easy to damage mechanically. VF1, VF2, VF3, and VF4 use near-identical families with only the VF number changed; copying a field from the wrong VF macro can compile cleanly while targeting the wrong virtual function.
- PCIe status, AER, MSI/MSI-X, FLR, and link-control fields have side effects. Treating all masks as ordinary read/write configuration can lose error evidence, trigger resets, disrupt interrupts, or retrain/disable links unexpectedly.
- MSI layout aliases must be interpreted according to enabled 32-bit versus 64-bit MSI format. The presence of both normal and `_64` message-data/mask/pending families reflects layout-dependent interpretation, not independent storage for every mode.
- ATS, ARI, LTR, OBFF, atomic operation, ten-bit tag, IDO, and TLP-prefix fields affect host interconnect behavior. Enabling unsupported combinations can create protocol errors or bad performance in SR-IOV guests.
- AER header and TLP prefix log fields are diagnostic state. Incorrect clearing or decoding can hide the first failing transaction and make field failures hard to diagnose.
- VF access rights are virtualization-sensitive. PF, VF guest, hypervisor, and firmware may not all be allowed to program the same fields, even though the bit definitions are visible in a shared header.
- The chunk boundaries are partial: the first VF1 `VENDOR_ID` and the complete VF4 tail are outside this document. File-level conclusions need reconciliation with neighboring chunks.

## Test and Validation Signals

Useful validation is mostly build, SR-IOV, PCIe, and hardware bring-up coverage:

- Build AMDGPU code paths that include `nbio_2_3_sh_mask.h`, especially NBIO 2.3, MXGPU, and SMU11 platform files.
- SR-IOV VF enumeration should expose correct PCI IDs, class codes, BARs, capability pointers, PCIe capabilities, MSI/MSI-X capabilities, AER, ATS, and ARI structures for VF1-VF4.
- VF reset and teardown tests should verify FLR initiation/status behavior and that command/status bits return to expected defaults.
- MSI/MSI-X interrupt tests should validate message programming, mask/pending behavior, vector delivery, and PBA/table interpretation for VF1-VF3.
- PCIe link and power-management tests should verify payload/read-request sizing, ASPM/LTR/OBFF controls, link retraining, bandwidth status, and compliance bits do not regress.
- AER diagnostics or error-injection tests should verify uncorrectable/correctable status, mask, severity, header log, and TLP prefix log decoding and clearing.
- Static generated-header checks can compare repeated VF1-VF4 field layouts against adjacent chunks and against `nbio_2_3_offset.h` to catch missing fields, mask-width drift, or mid-family truncation.

## Unresolved Cross-Chunk References

Line 29341 is inside `BIF_CFG_DEV0_EPF0_VF1_DEVICE_ID`; the `VF1_VENDOR_ID` field and the comment introducing `VF1_DEVICE_ID` are in the previous chunk. Line 31771 ends at the last visible `VF4_LINK_CAP2` mask; the following VF4 `LINK_CNTL2`, `LINK_STATUS2`, MSI/MSI-X, vendor-specific, AER, ATS, and ARI fields are in the next chunk. The final per-file research document should stitch these boundaries before making complete claims about VF1 or VF4.
