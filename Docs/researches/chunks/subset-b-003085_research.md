# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 41513-43979

## Scope

This chunk is a generated AMDGPU NBIO 7.0 shift/mask header segment. It contains 2,118 `#define` field-layout macros and 343 register/address comments for PCIe configuration-space registers under `BIF_CFG_DEV0_EPF1_1`, `BIF_CFG_DEV0_EPF2_1`, `BIF_CFG_DEV0_EPF3_1`, and the beginning of `BIF_CFG_DEV0_EPF4_1`. There are no functions, structs, enums, variables, locks, allocations, or executable statements in this range.

The range starts in the middle of `BIF_CFG_DEV0_EPF1_1_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_HVVM_MBOX_DW1`, so the `VF0` through `VF7` shift definitions and the register comment are in the previous chunk while this chunk still includes the later shifts and all masks for the register. It ends in the middle of `BIF_CFG_DEV0_EPF4_1_LINK_STATUS2`, after the `EQUALIZATION_PHASE2_SUCCESS` shift; the remaining `LINK_STATUS2` shifts and all masks continue in the next chunk. The merge lane must reconcile those boundary registers before treating either family as complete.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware metadata and has no direct distributed-filesystem behavior.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield half of AMD's generated NBIO 7.0 register interface. For each hardware register field it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position used to place or extract the field.
- `<REGISTER>__<FIELD>_MASK`, the encoded mask used to isolate, preserve, clear, or update that field.

This chunk describes the PCIe configuration layout for several endpoint functions exposed through NBIO/BIF. The first section completes part of the `EPF1` GPU-I/O virtualization vendor-specific capability, including host/virtual-machine mailbox handshakes, context and framebuffer accounting fields, per-VF framebuffer allocations, and scheduler data windows. The rest of the chunk moves through repeated PCI-compatible endpoint-function configuration blocks for `EPF2`, `EPF3`, and `EPF4`: standard header fields, BARs, power management, PCI Express capabilities, AER, BAR enhanced capabilities, power budgeting, dynamic power allocation, ACS, ARI, MSI, MSIX, SATA IDP, and selected PCIe link-control/status fields.

## Important Macro Families

The `EPF1` GPU-I/O virtualization section covers:

- `GPUIOV_HVVM_MBOX_DW1` and `GPUIOV_HVVM_MBOX_DW2`, which expose per-VF transmit-acknowledge and receive-valid bits for VFs 0-15 plus PF transmit/receive handshake bits.
- `GPUIOV_CONTEXT`, which defines context size, location, and offset fields for virtualization context storage.
- `GPUIOV_TOTAL_FB` and `GPUIOV_VF0_FB` through `GPUIOV_VF15_FB`, which split each word into framebuffer size and offset fields and expose aggregate available/consumed framebuffer accounting.
- `GPUIOV_OFFSETS`, which points to UVD, VCE, and GFX scheduler windows.
- `GPUIOV_UVDSCH_DW0` through `DW8`, `GPUIOV_VCESCH_DW0` through `DW8`, and `GPUIOV_GFXSCH_DW0` through `DW8`, which are full-width data words for virtualization scheduler payloads.

The `EPF2` and `EPF3` blocks are full repeated PCI endpoint-function configuration layouts:

- Standard PCI header fields: vendor/device IDs, command/status, revision/programming interface/subclass/base class, cache-line/latency/header/BIST, six BARs, ROM BAR, capability pointer, interrupt line/pin, min grant, max latency, and adapter IDs.
- Power management capability fields: capability-list headers, capability version, device-specific initialization, auxiliary-current, PME support, PME enable/status, data select/scale, and power state.
- PCI Express capability fields: capability list/header, device capabilities, device control/status, link capabilities/control/status, device/link capability 2, control 2, status 2, slot capability/control/status 2, and feature bits such as payload size, read request size, FLR, relaxed ordering, no-snoop, LTR, OBFF, IDO, ARI forwarding, atomic operations, completion timeout, link speed/width, retraining, ASPM, and equalization status.
- MSI and MSIX fields: MSI control, 32/64-bit message address/data, mask and pending words, MSIX table and pending-bit-array descriptors.
- Vendor-specific and PCIe extended capabilities: vendor capability headers and payload words, Advanced Error Reporting status/mask/severity/log fields, BAR enhanced capability controls for BAR1-BAR6, power-budget data selection and capability fields, DPA capability/control/status/substate allocation fields, ACS capability/control fields, and ARI capability/control fields.

The `EPF4` block begins the same repeated endpoint-function layout, starting at standard PCI identity/header/BAR fields and continuing through power management, PCIe device/link capabilities, and PCIe link status 2. This chunk stops before the rest of `EPF4` link-status2 masks and later MSI/MSIX/extended-capability fields.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace. The constants are untyped preprocessor integer literals, mostly with an `L` suffix, and encode only field geometry.

These definitions do not encode register addresses, reset values, access width, read/write permissions, write-one-to-clear behavior, sequencing requirements, firmware ownership, or hardware side effects. Consumers must combine them with sibling generated metadata in `nbio_7_0_offset.h`, `nbio_7_0_default.h`, and `nbio_7_0_smn.h`, then access the registers through AMDGPU helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, or `SOC15_REG_OFFSET` depending on the register aperture.

## Control Flow

This header has no local runtime control flow. Runtime flow is external:

1. AMDGPU code selects a NBIO/BIF PCI configuration register from generated address metadata.
2. The code reads a register value, extracts fields with the `__SHIFT` and `_MASK` constants, or composes a new value while preserving unrelated and reserved bits.
3. The decoded or composed value participates in PCIe device bring-up, SR-IOV/GPU-I/O virtualization setup, doorbell and interrupt routing, power management, link training, error reporting, BAR programming, or capability exposure.

The field names imply several hardware/firmware-managed flows outside the header: PF/VF mailbox handshakes, per-VF framebuffer partitioning, scheduler-table publication for UVD/VCE/GFX virtualization, PCIe power-state transitions, FLR initiation, completion-timeout handling, link retraining/equalization, AER logging, MSI/MSIX interrupt delivery, ACS/ARI routing, DPA substate allocation, and power-budget reporting.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes hardware-visible state in NBIO PCIe configuration and vendor-specific registers. Persistence depends on the GPU reset domain, PCIe reset, function-level reset, firmware/BIOS configuration, virtualization manager programming, suspend/resume restore, and explicit AMDGPU writes.

Represented state includes PCI identity and class-code fields, command/status bits, BAR apertures, ROM BAR values, capability-list pointers, power-management state, PCIe device/link capabilities and controls, MSI/MSIX routing state, AER masks/status/logs, BAR capability controls, power-budget and DPA data, ACS and ARI enables, GPUIOV mailbox bits, GPUIOV framebuffer allocations, and scheduler data words. Some fields are status or latched hardware state (`CORR_ERR`, `FATAL_ERR`, `TRANSACTIONS_PEND`, `LINK_TRAINING`, equalization status, AER logs, MSI pending bits), while others are configuration controls that software or firmware may write.

Because many registers are PCI configuration surfaces, values can be visible to the host PCI core, hypervisors, guests, firmware, or user-space diagnostic tooling. Call sites must not infer reset persistence from the mask definitions alone; defaults and reset behavior belong to hardware documentation and sibling generated default/address headers.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.0 register database and must remain synchronized with sibling headers:

- `nbio_7_0_offset.h` provides the matching register offsets.
- `nbio_7_0_default.h` provides generated reset/default values.
- `nbio_7_0_smn.h` provides SMN-indexed NBIO register names used by PCIe/NBIO access paths.
- `nbio_7_0_sh_mask.h` consumers use AMDGPU register helpers to apply these field layouts.

Direct include users in this tree include `amdgpu/nbio_v7_0.c`, `amdgpu/soc15.c`, and `pm/powerplay/hwmgr/smu10_inc.h`. `nbio_v7_0.c` shows the expected integration pattern: include the default/offset/shift-mask/SMN headers together, then use `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `SOC15_REG_OFFSET`, and `REG_SET_FIELD` around generated symbols. This exact chunk's `EPF1`-`EPF4` symbols are not directly matched by name in those local `.c` files, so they are mostly latent hardware metadata for platform code, firmware interaction, virtualization, PCI config decoding, or future call sites rather than active high-level driver logic in the visible source.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while causing software to read or write the wrong PCIe configuration bit, leading to broken capability reporting, bad BAR sizing, lost interrupts, AER misreporting, or PCIe link/power-management regressions.
- The chunk starts and ends mid-register. Adjacent chunks are required for complete `GPUIOV_HVVM_MBOX_DW1` and `EPF4_LINK_STATUS2` coverage.
- `EPF2`, `EPF3`, and `EPF4` are mechanically repeated blocks. A generation error in one function can affect only a single virtual or physical endpoint function, which is hard to notice if tests exercise only `EPF0` or `EPF1`.
- GPUIOV mailbox fields are handshake bits. Polling code needs timeouts and must handle missed acknowledgements, stale receive-valid bits, VF index mismatches, and PF/VF ownership races.
- GPUIOV framebuffer size/offset fields are partitioning data. Incorrect masks can expose overlapping VF framebuffer windows or misreport available/consumed memory to virtualization layers.
- PCIe control bits such as FLR, link disable, retrain link, target link speed, completion timeout, no-snoop, relaxed ordering, LTR, OBFF, ARI, ACS, and atomic-operation enables have system-visible effects and may be constrained by firmware, topology, or the host PCI core.
- AER status and log fields may use write-one-to-clear or latch-on-error semantics depending on the hardware register. The mask header does not describe those semantics, so consumers must avoid blind writes.
- Reserved fields are explicitly represented in several registers. Writers should preserve reserved bits unless the hardware specification requires a defined value.

## Test Signals

- Build AMDGPU with NBIO 7.0 and SMU10 paths enabled. Compile-time coverage catches missing or renamed generated symbols used by `nbio_v7_0.c`, `soc15.c`, and power-management include stacks.
- Run generated-header consistency checks: every field with both shift and mask should have a compatible mask position, masks should not overlap unexpectedly within a register, and repeated `EPF2`/`EPF3`/`EPF4` layouts should match except for the endpoint-function number.
- Cross-check this shift/mask chunk against `nbio_7_0_offset.h` and `nbio_7_0_default.h` so every `BIF_CFG_DEV0_EPF*_1_*` field maps to a known register offset and expected default.
- On supported hardware, validate PCI enumeration, BAR sizing, MSI/MSIX interrupt delivery, AER reporting, power-management state transitions, FLR behavior, GPU reset recovery, suspend/resume, and PCIe link retraining/equalization with NBIO 7.0 enabled.
- For virtualization/SR-IOV scenarios, exercise GPUIOV PF/VF mailbox exchange, VF framebuffer allocation reporting, UVD/VCE/GFX scheduler data publication, VF reset handling, and guest-visible PCI capability surfaces.
- For any code that writes these fields, capture register traces before and after changes to confirm reserved bits are preserved, write-one-to-clear fields are handled intentionally, and capability/control fields remain consistent across cold boot, warm reset, and resume.
