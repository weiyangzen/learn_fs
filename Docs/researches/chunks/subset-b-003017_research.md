# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 29469-31897

## Scope

This chunk is a generated AMDGPU NBIO 6.1 shift/mask header segment. It contains 2,137 `#define` field-layout macros across 2,429 source lines, plus register-family comments and address-block markers. There are no C functions, structs, enums, global variables, allocations, locks, or executable statements in this range.

The range starts inside the `BIF_CFG_DEV0_EPF0_VF4_1_DEVICE_CAP` register family, after the first VF4 PCIe capability fields were defined in the prior chunk. It then covers the remainder of the VF4 PCIe/device/link/MSI/MSI-X/vendor/AER/ATS/ARI field layout, complete repeated configuration templates for VF5 and VF6, and most of the VF7 template through `PCIE_TLP_PREFIX_LOG2`. The following chunk is needed for the tail of VF7 TLP prefix logging and the remaining VF7 ATS/ARI definitions.

## Purpose

`nbio_6_1_sh_mask.h` is the bitfield half of AMD's generated NBIO 6.1 hardware register interface. For each named NBIO register or PCI configuration-space word, it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position used to place or extract a field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, clear, or update that field.

The companion `nbio_6_1_offset.h` supplies matching register offsets, and `nbio_6_1_default.h` supplies reset/default values for the same generated register names. Runtime AMDGPU code combines those offsets and masks through helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `REG_GET_FIELD`, and `REG_SET_FIELD`.

This chunk specifically describes the software-visible PCI configuration image for SR-IOV virtual functions under endpoint function 0. The register names use `BIF_CFG_DEV0_EPF0_VF{4,5,6,7}_1_*`, so the repeated structures are per-VF templates rather than ordinary PF-only NBIO control registers.

## Important Macro Families

The VF4 portion begins after the early PCI capability header fields and covers:

- PCIe device capability/control/status fields: payload size, phantom functions, extended tags, acceptable L0s/L1 latency, role-based error reporting, captured slot power, FLR capability, error-reporting enables, relaxed ordering, no-snoop, max read request size, and `INITIATE_FLR`.
- PCIe link capability/control/status fields: supported/current speed, link width, ASPM/power-management controls, retrain/disable controls, common clock, extended sync, hardware autonomous width/speed disable, bandwidth-management interrupt enables, data-link active status, target speed, compliance, de-emphasis, equalization status, and transmit margin.
- PCIe capability 2 fields: completion-timeout ranges and disable support, ARI forwarding, atomic operation support, ID-based ordering, LTR, OBFF, extended format/TLP prefix support, ten-bit tags, emergency power reduction, and lower-power-entry latency.
- Slot 2 placeholder fields, MSI capability fields, MSI message address/data/mask/pending fields for 32-bit and 64-bit MSI forms, MSI-X table/PBA metadata, vendor-specific extended capability fields, AER fields, ATS capability/control fields, and ARI capability/control fields.

The VF5 and VF6 portions are complete repeated virtual-function PCI configuration templates. Each covers:

- Conventional PCI header fields: vendor/device ID, command, status, revision, programming interface, subclass, base class, cache line, latency, header type, BIST, BAR1 through BAR6, adapter/subsystem ID, ROM BAR, capability pointer, interrupt line, and interrupt pin.
- PCI command/status bits: I/O and memory decode, bus mastering, special cycles, memory-write-invalidate, VGA palette snoop, parity response, SERR, fast back-to-back, interrupt disable, immediate readiness, capability-list presence, interrupt status, DEVSEL timing, target/master abort reporting, system error, and detected parity error.
- PCIe base capability, device capability/control/status, link capability/control/status, device/link capability 2, and slot capability/control/status 2 layouts.
- MSI and MSI-X layouts, including capability metadata, enable/multiple-message state, 64-bit address capability, per-vector masking support, message address/data, mask, pending bits, MSI-X table size, function mask, enable bit, table BIR/offset, and PBA BIR/offset.
- Vendor-specific extended capability layout with generic header and scratch fields.
- Advanced Error Reporting layout: enhanced capability list, uncorrectable error status/mask/severity, correctable error status/mask, advanced error capability/control, header log words, and TLP prefix log words.
- Address Translation Service fields: enhanced capability list, invalidate queue depth, page-aligned request, global invalidate support, STU, and ATC enable.
- Alternative Routing-ID Interpretation fields: enhanced capability list, multifunction group capability, ACS function group capability, next-function number, multifunction group select, and ACS function group enable.

The VF7 portion repeats the same template from the conventional PCI header through AER and TLP prefix logging, but this chunk ends before the VF7 ATS and ARI families are complete.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace consumed by other kernel code.

The constants are untyped preprocessor integer literals, mostly with an `L` suffix. They encode only field position and field mask. They do not encode register access width, reset value, read/write permission, write-one-to-clear behavior, required privilege level, ordering requirements, or hardware side effects. Callers must use the matching offset/default headers and the NBIO/PCIe access path appropriate for the register being touched.

## Control Flow

This header has no local control flow. Runtime flow is external:

1. AMDGPU code selects a VF PCI configuration register offset from `nbio_6_1_offset.h` or through PCI/NBIO indirect access.
2. The code reads a register/config word, extracts fields with these `__SHIFT` and `_MASK` constants, or composes a new value with `REG_SET_FIELD`.
3. The decoded value drives PCI/SR-IOV policy or diagnostics, or the composed value is written back to hardware.

Likely flows represented by this chunk include VF PCI enumeration, VF BAR/resource assignment, memory and bus-master enablement, MSI/MSI-X programming, virtual-function FLR, PCIe link capability reporting, AER reporting and masking, TLP/header-log collection, ATS enablement, ARI routing, and PF/VF virtualization management.

## State And Persistence Behavior

The header itself stores no state. It names hardware-visible state in NBIO's PCI configuration-space image for SR-IOV virtual functions. Persistence depends on the GPU/NBIO reset domain, PCI conventional reset, function-level reset, SR-IOV enable/disable sequencing, PF-driven VF initialization, hypervisor policy, firmware setup, suspend/resume save-restore, and explicit driver writes.

Represented state includes static identity and class-code data, command/status bits, BAR decode windows, interrupt-line and MSI/MSI-X programming state, PCIe device/link controls, capability-list pointers, AER status/mask/severity and logs, ATS translation-cache controls, and ARI routing/group controls.

Several fields have direct hardware or virtualization consequences. `MEM_ACCESS_EN` and `BUS_MASTER_EN` gate MMIO decode and DMA for a VF. `INITIATE_FLR` triggers VF reset behavior. MSI/MSI-X enable, mask, table, and pending fields control interrupt delivery. AER status/log bits may be sticky or write-one-to-clear. ATS and ARI fields affect IOMMU translation caching and requester-ID routing. The generated masks do not provide those semantics by themselves, so call sites must preserve reserved bits, honor capability bits, and use the correct reset and synchronization path.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 6.1 register database and must stay synchronized with sibling generated headers:

- `nbio_6_1_offset.h` supplies matching offsets for the `BIF_CFG_DEV0_EPF0_VF*_1_*` register names.
- `nbio_6_1_default.h` supplies reset/default values for the same VF register families.
- `nbio_6_1_smn.h` supplies related SMN address metadata for NBIO access paths.

Direct include users in this tree include `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c`, `drivers/gpu/drm/amd/amdgpu/psp_v3_1.c`, Vega power-management include wrappers, and display resource code. The nearby NBIO 6.1 runtime code uses the same generated mask style for doorbell apertures, interrupt handling, HDP flush status, PCIe configuration, LTR, clock gating, and SR-IOV mailbox flows. `mxgpu_ai.c` is particularly relevant because it handles VF-to-PF mailbox messaging and virtualized GPU access/reset coordination.

Although this repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware metadata. It has no direct Ceph or distributed-filesystem behavior.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while causing software to read, preserve, clear, or set the wrong bit in VF PCI configuration space.
- The range starts mid-VF4 and ends mid-VF7. Adjacent chunks are required for a complete per-VF capability-chain view.
- The VF5/VF6 definitions are mechanically repeated. A lane, VF number, or register-name copy error would be easy to miss in review but could affect only one virtual function.
- PCI command and BAR masks affect MMIO decode and DMA. Incorrect fields can break VF probing, expose the wrong address window, or enable DMA before isolation is ready.
- MSI/MSI-X fields affect interrupt routing. Bad masks can produce lost, repeated, or misrouted VF interrupts.
- AER status, severity, mask, header log, and TLP prefix log fields are diagnostic evidence. Treating sticky or W1C fields like ordinary writable storage can lose error context or fail to clear a fault.
- ATS and ARI fields affect IOMMU translation caching and requester-ID routing. Incorrect values can break VF assignment, translation invalidation, or isolation assumptions.
- FLR, transactions-pending, link training, and bandwidth status fields interact with asynchronous hardware state. Polling or reset flows must use timeouts and should not assume immediate convergence from a bitfield definition alone.
- Reserved fields are present in several capability/status registers. Writers must preserve reserved bits unless the hardware specification explicitly says otherwise.

## Test Signals

- Build AMDGPU with NBIO 6.1 support enabled. Compile-time coverage catches missing or renamed generated symbols used by NBIO, PSP, display, power-management, and SR-IOV code.
- Run generated-header consistency checks against the authoritative NBIO 6.1 register database: offset/name pairing, shift/mask width checks, overlap checks within each register, default-value compatibility, capability-list continuity, and VF4/VF5/VF6/VF7 repetition checks.
- Exercise SR-IOV on supported ASICs: PF enables VFs, VFs enumerate with expected vendor/device/class/capability data, VF BARs size and map correctly, and memory/bus-master bits transition only when expected.
- Validate VF reset paths: FLR initiation, transactions-pending handling, PF/VF mailbox coordination, and recovery after GPU init/fini/reset access requests.
- Validate interrupt delivery with MSI and MSI-X: message address/data programming, table/PBA offsets, masking, pending bits, and absence of lost or spurious VF interrupts.
- Use PCIe/AER fault observation or injection where available to confirm uncorrectable/correctable status, mask, severity, first-error pointer, header logs, and TLP prefix logs decode correctly.
- For passthrough or mediated virtualization scenarios, verify ATS enablement/invalidation behavior, ARI next-function routing, requester-ID behavior, and IOMMU isolation.
- Check suspend/resume and GPU reset paths for restoration of VF-visible PCI configuration state and for no stale AER/MSI/ATS/ARI state leaking across reset boundaries.
