# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 105827-108246

## Scope

This chunk is a slice of AMDGPU's generated NBIO 2.3 register-field shift/mask header. It contains C preprocessor constants only: no functions, structs, enums, global variables, allocation, locking, direct MMIO, or runtime branches.

The assigned range covers `BIF_CFG_DEV0_EPF0_*_1` PCI configuration-space field layouts for SR-IOV-style endpoint virtual functions:

- the tail of `VF10_1`, starting at `CAP_PTR` field definitions and continuing through PCIe, MSI/MSI-X, vendor-specific, AER, ATS, and ARI capability fields;
- complete `VF11_1` and `VF12_1` config blocks, from vendor/device ID through ARI control;
- the first part of `VF13_1`, from vendor/device ID through the beginning of `MSIX_PBA`.

The range starts in the middle of the `VF10_1` register block because the `//BIF_CFG_DEV0_EPF0_VF10_1_CAP_PTR` marker is in the previous chunk. It also ends in the middle of `BIF_CFG_DEV0_EPF0_VF13_1_MSIX_PBA`; this chunk contains its two shift definitions, while the corresponding masks continue in the next chunk.

Although the repository path is under a local `ceph-client` tree, this source file is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem logic.

## Purpose

`nbio_2_3_sh_mask.h` is the bit-layout side of the generated NBIO 2.3 register description. The macros in this chunk give named shift and mask constants for PCI/PCIe configuration registers exposed by AMD NBIF/BIF endpoint virtual functions. Driver code, diagnostics, generated validation tools, and register access helpers can use these names instead of open-coded bit numbers.

The naming convention is consistent across the range:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field's encoded bit mask.

This chunk is therefore a compile-time hardware ABI. Consumers combine these field definitions with matching addresses from `nbio_2_3_offset.h` and, where useful, reset values from `nbio_2_3_default.h`. The expected runtime usage pattern is through AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, and related NBIO/SOC15 accessors.

## Important Macro Families

The `VF10_1` portion starts with capability pointer and interrupt/min-grant/max-latency fields, then defines PCIe capability, device capability/control/status, link capability/control/status, PCIe capability 2 device/link fields, MSI, MSI-X, vendor-specific capability headers, AER, ATS, and ARI fields.

`VF11_1` and `VF12_1` each define a complete endpoint config-space layout:

- standard PCI header identity and class fields: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `HEADER`, and `BIST`;
- command/status control bits: I/O and memory enable, bus mastering, parity/SERR/error reporting, interrupt disable, capability-list presence, 66 MHz capability, fast back-to-back, target/master abort, system error, and parity error status;
- BAR and address-style fields: `BASE_ADDR_1` through `BASE_ADDR_6`, `CARDBUS_CIS_PTR`, `ADAPTER_ID`, `ROM_BASE_ADDR`, and `CAP_PTR`;
- legacy interrupt and timing fields: interrupt line/pin, min grant, max latency, cache line size, and latency timer;
- PCIe capability list, PCIe capability header, device capability/control/status, link capability/control/status, device/link capability 2, device/link control 2, and link status 2;
- MSI and MSI-X capability list, message control, message address/data, mask, pending, table, and pending-bit-array fields;
- PCIe vendor-specific extended capability headers and scratch registers;
- AER extended capability fields for uncorrectable/correctable error status, masks, severity, capability/control, header logs, and TLP prefix logs;
- ATS extended capability/list/control fields and ARI extended capability/list/control fields.

The `VF13_1` portion repeats the same endpoint-header and early capability pattern through `MSIX_PBA`, but its vendor-specific, AER, ATS, and ARI families are outside this chunk.

The PCIe device-control fields include error reporting enables (`CORR_ERR_EN`, `NON_FATAL_ERR_EN`, `FATAL_ERR_EN`, `USR_REPORT_EN`), ordering and snoop policy (`RELAXED_ORD_EN`, `NO_SNOOP_EN`), payload/read request sizing, extended tags, phantom functions, AUX power PM, and `INITIATE_FLR`. Device-status fields cover correctable/non-fatal/fatal/unsupported-request observations, AUX power, pending transactions, and emergency power-reduction detection.

The link fields describe negotiated and target link behavior: link speed, width, ASPM/power-management support, L0s/L1 latency, clock power management, surprise-down reporting, data-link active reporting, bandwidth notification, link disable/retrain, common clock, extended sync, autonomous width/speed disable, link bandwidth interrupts, DRS signaling, current speed/width, link training, slot clock, data-link active, equalization status, de-emphasis, crosslink/downstream presence, and related PCIe 2.0+ status/control bits.

The MSI and MSI-X families define interrupt capability wiring for each virtual function. MSI fields include enable, multi-message capability and enablement, 64-bit message support, per-vector masking support, low/high message address, message data, mask, pending, and 64-bit variants. MSI-X fields include table size, function mask, enable, table BAR indicator/offset, and PBA BAR indicator/offset.

The AER families in `VF10_1`, `VF11_1`, and `VF12_1` define uncorrectable error status/mask/severity bits for data-link protocol, surprise-down, poisoned TLP, flow-control protocol, completion timeout, completion abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic-op egress blocking, TLP prefix blocking, and poisoned-TLP egress blocking. Correctable error status/mask fields include receiver error, bad TLP, bad DLLP, replay rollover, replay timeout, advisory non-fatal, corrected internal error, and header log overflow. AER control fields include first error pointer, ECRC generation/check capability and enable bits, multiple-header recording, TLP prefix log presence, and completion timeout prefix/header log controls.

The ATS and ARI fields define capability IDs, versions, next pointers, invalidation queue depth, page-aligned request support, STU, enable bits, next-function-number fields, function-group capability, and ACS function-group behavior. These are relevant to virtualized PCIe topology and address translation behavior.

No callable APIs or C types are declared here. The public surface is the set of generated macro names.

## Control Flow

There is no executable control flow in this header. At runtime, surrounding AMDGPU code follows the usual generated-register pattern:

1. Select a register offset from `nbio_2_3_offset.h` or a companion generated address macro.
2. Read the corresponding NBIO/BIF/PCIe config register through a SOC15, PCIe, or indirect register accessor.
3. Use `__SHIFT` and `_MASK` constants from this file, commonly through `REG_SET_FIELD` or `REG_GET_FIELD`, to compose or decode a field.
4. Write the modified register value back, poll a status bit, route an interrupt, log decoded hardware state, or expose a capability result to higher-level driver code.

The chunk itself does not decide whether a field is readable, writable, write-one-to-clear, sticky, reset-only, or firmware-owned. Those semantics come from the AMD register specification and the runtime sequences that consume the generated constants.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-visible PCI/PCIe configuration state for NBIO 2.3 endpoint virtual functions. The underlying state is controlled by GPU reset, PCIe reset, function-level reset, SR-IOV/PF policy, firmware initialization, host PCI enumeration, power transitions, suspend/resume, link retraining, interrupt configuration, and error handling.

The represented state includes:

- identity and enumeration metadata such as vendor ID, device ID, class code, header type, subsystem ID, BARs, ROM BAR, and capability pointers;
- command/status policy such as memory-space enable, bus mastering, interrupt disable, SERR, parity, and abort/error status;
- PCIe capability state such as payload size, maximum read request size, no-snoop, relaxed ordering, extended tags, FLR, LTR, OBFF, completion timeout, emergency power reduction, 10-bit tags, atomic operations, and TLP prefix behavior;
- link capability, control, and status for negotiated width/speed, target speed, retraining, compliance, de-emphasis, equalization, DRS, and data-link presence;
- interrupt-routing state for MSI and MSI-X message control, addresses, data, masks, pending bits, tables, and PBAs;
- error-state and diagnostics for AER status, masks, severity, header logs, TLP prefix logs, and root-error-style control fields where present;
- virtualization/topology capability state for ATS and ARI.

Some fields are pure status, some are policy controls, and some trigger side effects. Examples of side-effect-sensitive fields include `INITIATE_FLR`, link retrain, status bits that may be write-one-to-clear, AER logs, MSI/MSI-X enable and mask controls, completion-timeout controls, and link compliance/speed controls. The macros provide only bit positions; they do not protect callers from using a field with the wrong access semantics.

## Dependencies And Integration Points

The direct dependency is the generated AMD NBIO 2.3 register database. This header must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h`, which supplies matching `cfgBIF_CFG_DEV0_EPF0_VF*_1_*` offsets;
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h`, which supplies reset/default constants for the same register generation where generated;
- AMDGPU register helper macros and accessors, especially `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`;
- PCI core, SR-IOV, AER, MSI/MSI-X, ATS, and ARI expectations, because these generated layouts describe standard PCIe capability structures as implemented by the AMD NBIO block.

The closest source-tree integration path for this generated header is AMDGPU NBIO code such as `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, plus virtualization and power-management paths that include NBIO register headers for PCIe, ASPM/LTR, doorbell, interrupt, SR-IOV, and link policy. Specific `VF10_1` through `VF13_1` symbols may be accessed indirectly or only by tooling, but their correctness is still part of the generated ABI for the NBIO 2.3 register map.

Because the macros are untyped numeric constants, a missing or renamed macro usually fails at compile time, while an incorrect shift or mask can compile cleanly and cause runtime corruption of adjacent PCI/PCIe fields.

## Risks And Edge Cases

- Chunk-boundary risk is explicit. The range starts without the `VF10_1_CAP_PTR` marker and ends before `VF13_1_MSIX_PBA` masks; adjacent chunks are required for full register-family context.
- Width mismatches are easy to miss. The chunk describes 8-bit, 16-bit, and 32-bit PCI config fields using C integer constants. Consumers must pair masks with the matching register offset and access width.
- VF copy/paste drift is high risk. `VF11_1` and `VF12_1` are nearly identical blocks, and `VF10_1`/`VF13_1` are adjacent partial blocks. A wrong VF number, register suffix, or bit mask can silently route a decode or write to the wrong virtual function.
- PCIe link controls can destabilize hardware. Incorrect shifts for target speed, retraining, common clock, ASPM, LTR, OBFF, DRS, equalization, de-emphasis, or autonomous speed/width disable can reduce bandwidth, break resume, or cause link loss.
- MSI/MSI-X fields affect interrupt delivery. Bad message-control, table, PBA, address, data, mask, or pending-bit masks can produce lost interrupts, interrupt storms, or vectors delivered to the wrong target.
- AER fields are side-effect sensitive. Treating status/log fields as ordinary read-modify-write state can clear diagnostic evidence, mask serious errors, or apply wrong severity policy.
- ATS and ARI fields affect virtualization and topology behavior. Wrong queue-depth, page-aligned request, enable, next-function, or function-group masks can break isolation assumptions or PCIe function traversal.
- BAR, ROM, and capability-list fields are structural. Incorrect masks can break enumeration, capability walking, resource sizing, or emulation of VF configuration space.
- Field names are generated and long. Manual references are prone to subtle spelling mistakes; using the wrong `VF*_1` macro may compile if another generated symbol exists with the same field layout.

## Test Signals

Useful validation is mostly build, generated-header consistency, and PCIe/SR-IOV hardware behavior:

- Build AMDGPU configurations that include NBIO 2.3, SR-IOV, PCIe ASPM/LTR, MSI/MSI-X, AER, ATS, and ARI support; missing or renamed macros should be caught by compile failures in consumers.
- Compare `nbio_2_3_sh_mask.h` against the authoritative AMD register database and against `nbio_2_3_offset.h` to ensure every `BIF_CFG_DEV0_EPF0_VF10_1` through `VF13_1` field maps to the intended register and width.
- Run PCI enumeration and capability traversal with SR-IOV enabled; malformed identity, class, BAR, ROM, capability pointer, PCIe capability, MSI/MSI-X, ATS, or ARI layouts should appear as `lspci`/kernel decode anomalies.
- Exercise VF reset and FLR paths. `INITIATE_FLR`, pending transaction status, command/status, MSI/MSI-X masking, and capability restoration are useful signals for bit layout correctness.
- Test MSI and MSI-X interrupt delivery for VFs, including enable/disable, function mask, per-vector masking, pending bits, and table/PBA decode.
- Test PCIe link behavior across speed/width negotiation, retraining, ASPM/LTR, completion-timeout settings, DRS, equalization, suspend/resume, and hot reset where the platform supports it.
- Use AER/error-injection or fault-observation paths when available to confirm uncorrectable/correctable status, mask, severity, header-log, and TLP-prefix-log fields decode correctly for the affected VF config spaces.
- In virtualization environments, validate ATS/ARI behavior, function enumeration, isolation, and VF config-space emulation, since these macros define the field-level contract exposed to guests or PF-managed VFs.

## Chunk-Specific Notes For Merge

When the final per-file report is reconciled, merge this chunk with adjacent `nbio_2_3_sh_mask.h` chunks. Do not present `VF10_1_CAP_PTR` or `VF13_1_MSIX_PBA` as fully covered by this range alone. This range is best summarized as the VF10 tail, full VF11/VF12, and VF13 early endpoint PCIe config-space shift/mask definitions for NBIO 2.3.
