# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 22329-24747

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask header segment. It contains 2,141 preprocessor field definitions across 2,419 source lines. There are no C functions, structs, enums, variables, allocations, locks, or executable statements in this range.

The range starts inside the `BIF_CFG_DEV0_EPF0_VF3_0_*` virtual-function PCI configuration template at the Advanced Error Reporting extended capability, covers complete `VF4`, `VF5`, and `VF6` templates, and ends near the beginning of `VF7` after the `COMMAND` fields start. The source boundary is artificial: the earlier standard PCI/PCIe/MSI/MSI-X/VSEC fields for VF3 are in the previous chunk, and most of VF7 is in the next chunk.

## Purpose

`nbio_4_3_0_sh_mask.h` is the bitfield half of the generated NBIO 4.3.0 hardware register interface. For each named NBIO/PCI configuration register, it provides:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position used when packing or extracting the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, or update the field.

The companion `nbio_4_3_0_offset.h` supplies matching register/config-space offsets, and AMDGPU code uses both headers through register field helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, SOC15 register addressing helpers, and NBIO/PCI config access paths.

This chunk specifically describes SR-IOV virtual-function PCI configuration-space layout for NBIO device 0, endpoint function 0. The repeated `BIF_CFG_DEV0_EPF0_VF<n>_0_*` names map per-VF identity, BAR/resource, PCIe capability, interrupt, vendor-specific, Advanced Error Reporting, ARI, and Readiness Time Reporting fields.

## Important Macro Families

The VF3 tail in this chunk covers the later extended-capability portion of a virtual-function config image:

- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST` defines the AER extended-capability ID, version, and next-pointer fields.
- `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY` define uncorrectable PCIe error classes: data-link protocol, surprise down, poisoned TLP, flow-control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic-op egress blocked, TLP prefix blocked, and poisoned-TLP egress blocked.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK` cover correctable receiver, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal, corrected internal, and header-log-overflow events.
- `PCIE_ADV_ERR_CAP_CNTL` covers first-error pointer, ECRC generation/check capability and enable bits, multi-header receive capability/enablement, TLP prefix log presence, and completion-timeout log capability.
- `PCIE_HDR_LOG[0-3]` and `PCIE_TLP_PREFIX_LOG[0-3]` expose four 32-bit diagnostic words each for captured TLP headers and prefixes.
- `PCIE_ARI_*` covers Alternative Routing-ID Interpretation capability metadata, MFVC/ACS function-group capability bits, next-function number, function-group enables, and selected ARI function group.
- `PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2` define Readiness Time Reporting metadata and timing fields: reset time, DL-up time, FLR time, D3hot-to-D0 time, and the validity bit.

The complete `VF4`, `VF5`, and `VF6` blocks repeat the full VF PCI configuration template:

- Conventional PCI header fields: vendor/device ID, command, status, revision ID, class-code bytes, cache-line size, latency, header type, BIST, BAR1 through BAR6, CardBus CIS pointer, subsystem adapter ID, ROM BAR, capability pointer, interrupt line/pin, minimum grant, and maximum latency.
- PCI command/status bits: I/O and memory access, bus mastering, special cycle, memory write invalidate, parity response, SERR, interrupt disable, immediate readiness, interrupt status, capability-list presence, DEVSEL timing, target/master abort, signaled system error, and parity-error detected.
- PCIe capability fields: PCIe capability-list header, PCIe version, device/port type, slot implementation, interrupt message number, device capability/control/status, link capability/control/status, device capability/control/status 2, and link capability/control/status 2.
- Device and link controls: correctable/non-fatal/fatal/unsupported-request reporting, relaxed ordering, max payload, extended tags, phantom functions, aux power PM, no-snoop, max read request size, bridge config retry, function-level reset initiation, link disable/retrain, common clock, extended sync, ASPM controls, bandwidth-management interrupts, target link speed, compliance controls, de-emphasis, equalization status, completion-timeout settings, ARI forwarding, atomic operation controls, ID-based ordering, LTR, OBFF, emergency power reduction, ten-bit tags, and end-to-end TLP prefix blocking.
- MSI/MSI-X fields: capability IDs and next pointers, MSI enable and multiple-message fields, 32-bit and 64-bit message address/data fields, mask and pending fields, MSI-X table size, function mask, MSI-X enable, table BIR/offset, and PBA BIR/offset.
- Vendor-specific extended capability fields: VSEC capability-list metadata, VSEC ID/revision/length, and two 32-bit scratch payload registers.
- AER, ARI, and RTR fields with the same semantics as the VF3 tail.

The VF7 start covers only `VENDOR_ID`, `DEVICE_ID`, and the beginning of `COMMAND`; the rest of VF7 is outside this chunk.

## APIs, Types, And Functions

There are no runtime APIs or C types here. The public interface is the macro namespace itself. Consumers rely on the generated names, shifts, and masks staying synchronized with the companion offset/default headers and the hardware register database.

The constants are untyped preprocessor integer literals, usually using an `L` suffix and sized to the represented field. They do not encode access width, volatility, reset value, read/write permission, write-one-to-clear behavior, or side effects. Callers must know whether a field is PCI config space, an extended capability, a read-only capability bit, a writable control bit, a sticky status bit, or a command bit that triggers hardware behavior.

## Control Flow

This header has no local control flow. Runtime flow is external:

1. AMDGPU, firmware-facing, SR-IOV, or PCIe code selects a register/config offset from `nbio_4_3_0_offset.h`.
2. The code reads, decodes, composes, or updates a register value using this file's `__SHIFT` and `_MASK` constants directly or through field helper macros.
3. The updated or decoded value is written back, polled, saved/restored, reported, or used to make PCIe/NBIO policy decisions.

Likely flows using these fields include VF config-space presentation, PCI enumeration, BAR sizing and resource programming, command-bit enablement for memory access and bus mastering, PCIe link/device negotiation, function-level reset, MSI/MSI-X interrupt setup, AER status collection and masking, ARI routing, Readiness Time Reporting, and SR-IOV validation.

## State And Persistence Behavior

The header itself stores no state. It names hardware-visible state in NBIO PCI configuration registers for SR-IOV virtual functions. Persistence is determined by the GPU/NBIO reset domain, firmware initialization, PF/VF management, hypervisor policy, VF FLR, suspend/resume save-restore, and explicit driver writes.

Represented state includes static PCI identity and capability data, host-programmed command bits, BAR and ROM resource registers, interrupt routing state, MSI/MSI-X message address/data/mask/pending state, PCIe device/link control settings, hardware-updated link/device status, AER sticky status/mask/severity and diagnostic logs, vendor-specific scratch payloads, ARI function-routing controls, and RTR timing-validity data.

Several fields are not ordinary storage bits. PCI command bits enable memory access and bus mastering, `INITIATE_FLR` starts a function-level reset, link retrain/disable controls affect PCIe link state, MSI/MSI-X enable and mask fields affect interrupt delivery, and AER status/log fields can be sticky or write-one-to-clear depending on hardware semantics. This generated file only gives the bit layout; ordering, privilege, and side-effect rules are implemented by hardware and driver call sites.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 4.3.0 header set:

- `nbio_4_3_0_offset.h` supplies matching `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` offsets.
- Other generated NBIO 4.3.0 headers provide related defaults and register metadata where present.
- AMDGPU register helper macros consume the `__SHIFT` and `_MASK` definitions for field extraction and update.

Observed include-level integration in this tree includes `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c`, SMU 13 power-management files such as `pm/swsmu/smu13/smu_v13_0_0_ppt.c` and `pm/swsmu/smu13/smu_v13_0_7_ppt.c`, and display resource files that include the matching offset header. The per-VF fields integrate with PCI enumeration/configuration, SR-IOV VF exposure, PF/VF or hypervisor-managed virtualization, interrupt delivery, AER reporting, reset handling, ARI routing, PCIe link management, and readiness-time reporting.

Although this source path is under a `ceph-client` mirror, the content is AMDGPU hardware metadata and has no direct distributed-filesystem behavior.

## Risks And Edge Cases

- Generated bitfield drift can compile cleanly while making software touch the wrong hardware bit. This is most risky for command, DMA enable, interrupt, FLR, AER clear/mask, link-control, ARI, and RTR fields.
- The chunk starts and ends inside repeated VF templates. Merge/reconciliation should combine adjacent chunks before making complete per-VF claims about VF3 or VF7.
- Repetition across VF4, VF5, and VF6 is intentional. Any per-VF mismatch may indicate generator or register-database drift, but chunk-boundary truncation must not be misread as such drift.
- PCI command bits control memory access, bus mastering, SERR/parity behavior, and interrupt disable. Wrong masks can break VF probing, DMA enablement, or isolation assumptions.
- Link controls, completion-timeout controls, payload/read-request sizing, relaxed ordering, no-snoop, ID-based ordering, and atomic operation bits affect PCIe liveness and memory-ordering behavior.
- MSI/MSI-X table offsets, pending bits, masks, and enables can cause lost, repeated, or misrouted interrupts if decoded or programmed incorrectly.
- AER logs are diagnostic evidence. Treating status/log fields as normal writable state can clear useful error data or fail to clear real errors.
- ARI controls affect function routing and enumeration. Incorrect masks can break VF discovery or route transactions to the wrong function.
- RTR fields report timing characteristics for reset, DL-up, FLR, and D3hot-to-D0 transitions. Incorrect masks can make management software under-wait, over-wait, or trust invalid timing data.

## Test Signals

- Build AMDGPU with NBIO 4.3.0 support enabled. Missing or misspelled macros should be caught by direct users of the generated header set.
- Runtime probe on affected AMD GPUs should show stable PCI config enumeration for SR-IOV virtual functions, valid vendor/device IDs, correct class/capability data, and sane BAR sizing.
- SR-IOV validation should exercise multiple VFs, especially VF4 through VF6, because this chunk contains mechanically repeated per-VF templates.
- Interrupt smoke tests should verify MSI/MSI-X enablement, masking, pending-bit behavior, and absence of spurious or lost interrupts.
- PCIe health signals include expected negotiated link width/speed, successful FLR and link-retrain paths, no unexpected AER storms, and preserved AER diagnostics when errors are injected.
- ARI/virtualization tests should verify VF enumeration, function routing, and isolation under PF/VF and hypervisor-controlled setups.
- RTR-related validation should compare advertised reset/DL-up/FLR/D3hot-to-D0 timing fields against observed wait paths and ensure the `VALID` bit is honored before timing data is trusted.
