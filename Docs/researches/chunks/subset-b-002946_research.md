# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 103397-105826

## Scope

This chunk is a generated AMDGPU NBIO 2.3 shift/mask header segment. It contains 2,138 preprocessor field definitions across 2,430 source lines. There are no C functions, structs, enums, variables, locks, allocations, or executable statements in this range.

The line range starts in the late extended-capability area of `BIF_CFG_DEV0_EPF0_VF6_1_*`, covers complete virtual-function PCI configuration bitfield maps for `VF7`, `VF8`, and `VF9`, and then begins the `VF10` address block through the `ROM_BASE_ADDR` field before the `CAP_PTR` fields continue in the next chunk. The source boundary is artificial: VF6 standard PCI/PCIe/MSI/VSEC fields are before this chunk, and most of VF10 is after it.

## Purpose

`nbio_2_3_sh_mask.h` is the bitfield half of the generated NBIO 2.3 hardware interface. For each named NBIO/PCI configuration register, it provides:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position for packing or extracting the field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or preserve the field.

The matching register addresses live in `nbio_2_3_offset.h`, and reset/default values live in `nbio_2_3_default.h`. Runtime AMDGPU code includes these generated headers and applies the masks through register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, PCIe/NBIO config accessors, and lower-level MMIO paths.

This chunk specifically documents SR-IOV virtual-function PCI configuration-space layout for endpoint function 0. The repeated `BIF_CFG_DEV0_EPF0_VF<n>_1_*` names describe how each VF presents PCI identity, BAR/resource, PCIe capability, interrupt, Advanced Error Reporting, Address Translation Service, and Alternative Routing-ID Interpretation fields.

## Important Macro Families

The VF6 tail contains the Advanced Error Reporting, ATS, and ARI portion of a VF config image:

- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST` exposes the AER extended-capability ID, version, and next-pointer fields.
- `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY` define uncorrectable PCIe error classes: data-link protocol, surprise down, poisoned TLP, flow-control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic-op egress blocked, and TLP prefix blocked.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK` cover correctable receiver, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal, corrected internal, and header-log-overflow events.
- `PCIE_ADV_ERR_CAP_CNTL` covers first-error pointer, ECRC generation/check capability and enable bits, multi-header received capability/enablement, TLP prefix log presence, and completion-timeout log capability.
- `PCIE_HDR_LOG[0-3]` and `PCIE_TLP_PREFIX_LOG[0-3]` define four 32-bit diagnostic capture words for failed TLP headers and prefixes.
- `PCIE_ATS_*` covers ATS enhanced-capability metadata, invalidate queue depth, page-aligned request support, global invalidate support, small translation unit, and ATC enable.
- `PCIE_ARI_*` covers ARI enhanced-capability metadata, MFVC/ACS function-group capability bits, next-function number, enables, and function-group selection.

The complete `VF7`, `VF8`, and `VF9` blocks repeat the full virtual-function PCI configuration template:

- Conventional PCI header fields: vendor/device ID, command, status, revision, class bytes, cache-line size, latency, header type, BIST, BAR1 through BAR6, CIS pointer, subsystem adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, and max latency.
- PCI command/status fields: I/O access, memory access, bus mastering, special cycle, memory write invalidate, parity response, SERR, interrupt disable, readiness, capability-list presence, DEVSEL timing, target/master abort, system error, and parity error status.
- PCIe capability fields: capability-list header, PCIe version and device type, device capability/control/status, link capability/control/status, device capability/control/status 2, and link capability/control/status 2.
- Device and link controls: error-report enables, relaxed ordering, max payload size, extended tags, no-snoop, max read request size, FLR initiation, completion timeout, ARI forwarding, atomic operation controls, ID-based ordering, LTR enable, emergency power reduction, ten-bit tag requester enable, OBFF, end-to-end TLP prefix blocking, link disable/retrain, common clock, ASPM/PM control, bandwidth interrupts, DRS signaling, target link speed, compliance controls, de-emphasis, and equalization status.
- MSI/MSI-X fields: capability IDs and next pointers, MSI enable and multiple-message fields, 32-bit and 64-bit message address/data fields, mask and pending fields, MSI-X table size, function mask, enable, table BIR/offset, and PBA BIR/offset.
- Vendor-specific extended capability fields: VSEC capability-list metadata, VSEC ID/revision/length, and two 32-bit scratch payload registers.
- AER, ATS, and ARI fields with the same semantics as the VF6 tail.

The VF10 start covers only the conventional PCI header beginning: identity, command/status, revision/class/header/BIST fields, six BAR-sized base-address fields, CardBus CIS pointer, adapter/subsystem ID, and ROM base address. VF10 capability pointer and later capability sections are outside this chunk.

## APIs, Types, And Functions

There are no runtime APIs or C types here. The public interface is the macro namespace itself. Consumers depend on the generated spelling, bit positions, and masks staying synchronized with companion offset/default headers and the hardware register database.

The masks are untyped integer constants, commonly 8-, 16-, or 32-bit register fields with an `L` suffix. Because the macros do not encode access size or read/write semantics, the caller must already know whether a field belongs to PCI config space, MMIO, an extended capability, a read-only capability field, a read/write control field, a sticky status bit, or a command bit with side effects.

## Control Flow

This header has no local control flow. Runtime flow is external:

1. AMDGPU, firmware-facing, SR-IOV, or PCIe code selects a register offset from `nbio_2_3_offset.h`.
2. The code reads or composes a register value using these `__SHIFT` and `_MASK` constants, directly or through field helper macros.
3. The value is written back, decoded, polled, or reported according to PCIe/NBIO hardware semantics.

Likely flows using these fields include VF config-space exposure, PCI command and BAR/resource programming, PCIe link/device negotiation, function-level reset, MSI/MSI-X interrupt setup, AER status collection and masking, ATS/IOMMU translation enablement, ARI routing, and SR-IOV virtualization validation.

## State And Persistence Behavior

The header itself stores no state. It names hardware-visible state in NBIO PCI configuration registers for SR-IOV virtual functions. Persistence is controlled by GPU/NBIO reset domains, PCI config save/restore, firmware initialization, hypervisor or PF management, VF FLR, suspend/resume, and explicit driver writes.

Represented state includes static PCI identity and capability data, host-programmed command bits, BAR and interrupt routing state, device/link control settings, hardware-updated link/device status, MSI/MSI-X message address/data/mask/pending state, AER sticky status/mask/severity and diagnostic logs, ATS translation cache controls, and ARI function-routing state.

Several fields are not ordinary storage bits. Status and AER fields may be sticky or write-one-to-clear, `INITIATE_FLR` starts a function-level reset, link retrain/disable controls affect PCIe link state, MSI/MSI-X enable/mask fields affect interrupt delivery, and ATS/ARI controls affect isolation and enumeration. This generated file only provides bit layout; side-effect ordering and privilege rules are enforced elsewhere.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 2.3 header set:

- `nbio_2_3_offset.h` supplies the matching `cfgBIF_CFG_DEV0_EPF0_VF*_1_*` register/config-space addresses.
- `nbio_2_3_default.h` supplies generated defaults for related registers.
- AMDGPU register helper macros consume `__SHIFT` and `_MASK` definitions for field extraction and update.

Observed include-level integration in this tree includes `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, and SMU power-management files such as `pm/swsmu/smu11/navi10_ppt.c` and `pm/swsmu/smu11/sienna_cichlid_ppt.c`, all of which include the NBIO 2.3 generated headers. The per-VF fields integrate with PCI enumeration/configuration, SR-IOV VF presentation, PF/VF or hypervisor-managed virtualization paths, interrupt delivery, AER reporting, IOMMU/ATS behavior, ARI routing, reset handling, and PCIe link management.

Although this source path is under a `ceph-client` mirror, the content is AMDGPU hardware metadata and has no direct distributed-filesystem behavior.

## Risks And Edge Cases

- Generated bitfield drift can compile cleanly while making software touch the wrong hardware bit. This is especially risky for command, DMA enable, interrupt, FLR, AER clear, ATS, and ARI fields.
- The range starts and ends inside repeated VF templates. Merge/reconciliation must combine adjacent chunks before making complete claims about VF6 or VF10.
- Repetition across VF7, VF8, and VF9 is intentional. Any per-VF mismatch may indicate generator or register-database drift, but chunk-boundary truncation must not be mistaken for such drift.
- PCI command bits control memory access, bus mastering, SERR, parity behavior, and interrupt disable. Wrong masks can break VF probing or weaken DMA/resource isolation.
- Link controls, completion timeout, payload/read-request sizing, relaxed ordering, no-snoop, ID-based ordering, and atomic operation controls affect PCIe liveness and memory-ordering behavior.
- MSI/MSI-X masks, table offsets, pending bits, and enable fields can cause lost, repeated, or misrouted interrupts if decoded or programmed incorrectly.
- AER logs can be diagnostic evidence; treating status/log fields as normal writable state can clear useful data or fail to clear real errors.
- ATS and ARI controls affect IOMMU translation caching and function routing. Incorrect masks can break invalidation, enumeration, or isolation.

## Test Signals

- Compile AMDGPU with NBIO 2.3/Navi support enabled. Missing or misspelled macros should be caught by users of the generated header set.
- Runtime probe on affected AMD GPUs should show stable PCI config enumeration for SR-IOV virtual functions, valid BAR sizing, and correct capability-chain traversal.
- SR-IOV validation should exercise multiple VFs, not just one, because this chunk has mechanically repeated `VF7`, `VF8`, and `VF9` families.
- Interrupt smoke tests should verify MSI/MSI-X delivery, masking, pending-bit behavior, and absence of spurious interrupts.
- PCIe health signals include expected negotiated link width/speed, successful FLR/retrain paths, no unexpected AER storms in logs, and preserved AER diagnostics when errors are injected.
- ATS/ARI/IOMMU tests should verify VF enumeration, translation enable/disable, invalidation behavior, and isolation under virtualization.
