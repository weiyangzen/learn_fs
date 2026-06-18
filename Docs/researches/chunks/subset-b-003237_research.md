# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 26924-29367

## Purpose

This chunk is part of the generated NBIO 7.4 register shift/mask header used by the AMDGPU driver. It does not define executable logic; it defines C preprocessor constants that describe bit positions and masks for PCIe configuration-space registers behind NBIO/BIF. The range covers the tail of `BIF_CFG_DEV0_EPF0_0` extended PCIe capability fields, a large AMD GPU IOV vendor-specific capability block, and the beginning of the `BIF_CFG_DEV0_EPF1_0` PCI configuration block.

The definitions are intended to be paired with register address constants from `nbio_7_4_offset.h` and register access helpers such as `RREG32_PCIE`, `WREG32_PCIE`, `REG_GET_FIELD`, `REG_SET_FIELD`, and `WREG32_FIELD15`. Consumers include `drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c` and power-management code that include `nbio/nbio_7_4_sh_mask.h`.

## Macro API Surface

Every register field follows the generated naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of the field.
- `<REGISTER>__<FIELD>_MASK` gives the already-positioned mask.

The important register groups in this chunk are:

- EPF0 PCIe extended capabilities: device serial number, Advanced Error Reporting, Resizable BAR, power budgeting, Dynamic Power Allocation, Secondary PCIe Capability, ACS, ATS, Page Request Interface, PASID, Multicast, Latency Tolerance Reporting, ARI, SR-IOV, TPH requester, Data Link Feature, 16 GT/s PHY, lane margining, VF Resizable BAR, and AMD GPU IOV vendor-specific capability registers.
- EPF0 lane arrays: lane equalization controls for lanes 0-15, 16 GT/s per-lane preset controls for lanes 0-15, and margining control/status pairs for lanes 0-15. These repeated definitions have consistent field layouts, so driver code can use one lane's field names as the template for hardware documentation checks, while still needing exact per-lane macro names for generated register access.
- EPF0 GPU IOV vendor-specific registers: interrupt enable/status bits, reset control, HV/VM mailbox dwords, context, total framebuffer, offsets, P2P-over-XGMI enable, per-VF framebuffer size/offset entries for VF0-VF30, and scheduler state dwords for UVD, VCE, GFX, and UVD1.
- EPF1 PCI configuration registers: vendor/device IDs, command/status, class/revision/header/BIST, BARs, subsystem IDs, ROM base, interrupt line/pin, vendor capability, power-management capability, PCIe capability, device/link capabilities and controls, MSI/MSI-X, vendor-specific enhanced capability, and virtual-channel capability/resource controls.

There are no functions, structs, enums, or storage declarations in this chunk. The public interface is the macro namespace itself.

## Control Flow and Data Flow

This header has compile-time data flow only. The macros are expanded by C code that performs MMIO, PCIe config-space, or SOC15 register operations. Typical usage is:

1. A consumer includes `nbio_7_4_offset.h` for an address and this file for field metadata.
2. The consumer reads a register through an AMDGPU register helper.
3. It extracts or updates a field using the matching `__SHIFT` and `_MASK` constants, often indirectly through `REG_GET_FIELD` or `REG_SET_FIELD`.
4. It writes the modified value back to the hardware register.

`nbio_v7_4.c` includes this header alongside `nbio_7_4_offset.h` and `nbio_7_4_0_smn.h`. In that file, the same generated-mask pattern is used to program NBIO doorbell ranges, memory-controller access, PCIe light sleep, LTR enablement, and RAS-related paths. This particular chunk provides field metadata for many PCIe capability registers that may be read by diagnostic, virtualization, reset, error-reporting, and platform-configuration code even when there is no direct reference in `nbio_v7_4.c`.

## State and Persistence Behavior

The macros do not store state. The underlying registers do:

- AER status/mask/severity fields represent PCIe error state and policy, including correctable and uncorrectable error categories such as DLP, completion timeout, malformed TLP, ECRC, unsupported request, ACS violation, and TLP prefix blocked errors.
- Link, equalization, 16 GT/s, and margining fields reflect or request physical-link training behavior. Some fields are status-only from the driver perspective, while control fields can trigger equalization or margining operations.
- ACS, ATS, PRI, PASID, ARI, SR-IOV, MSI, MSI-X, and VC registers affect PCIe isolation, address translation, virtualization, interrupts, and traffic-class mapping. These settings persist in hardware until reset or rewritten by firmware/driver/platform code.
- GPU IOV fields describe virtualization-visible state: interrupt enables/status, reset notification/control, host/guest mailbox payloads, per-VF framebuffer layout, active context, total framebuffer accounting, and scheduler dwords. These are hardware/firmware coordination registers rather than Linux-owned persistent software state.

Because this is PCIe/NBIO hardware state, writes can have device-wide effects, especially for SR-IOV, PASID/PRI/ATS, ACS, MSI/MSI-X, and VC resource controls.

## Dependencies and Integration Points

Primary dependencies:

- `nbio_7_4_offset.h`: supplies the register addresses that correspond to these masks.
- AMDGPU register helpers and field helpers: `RREG32*`, `WREG32*`, `REG_GET_FIELD`, `REG_SET_FIELD`, and SOC15 register-offset helpers.
- PCIe configuration semantics: the bit layouts mirror PCIe capability structures, AER, SR-IOV, MSI/MSI-X, ATS/PRI/PASID, VC, and extended capability headers.
- Firmware/hypervisor interfaces for GPU IOV: mailbox, reset, scheduler, and VF framebuffer layout fields are meaningful only with the matching firmware/virtualization contract.

Notable integration signals from the tree:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c` includes this header directly and uses the NBIO 7.4 register/mask pattern for device bring-up and runtime configuration.
- SMU powerplay files for Arcturus/Aldebaran also include this mask header, so PCIe/NBIO fields may be used by power-management or platform feature code.
- Similar GPUIOV definitions appear in other NBIO generations, which suggests this chunk is generated from a common hardware register database and should remain synchronized with offsets and other ASIC-specific headers.

## Risks

- Mask/address mismatch: these field masks must match the paired `nbio_7_4_offset.h` addresses. A mismatch can silently update the wrong bit field in hardware.
- Width and reserved-bit handling: many registers contain reserved fields or full-width scratch/mailbox dwords. Driver writes must preserve unrelated bits unless the hardware spec says a full write is safe.
- Virtualization safety: SR-IOV, GPU IOV, PASID, PRI, ATS, ACS, and VF BAR layout fields can affect isolation between PF/VF contexts and between DMA address spaces.
- Error-reporting side effects: AER status bits may be write-one-to-clear or otherwise side-effectful depending on the register. Code must not treat masks as ordinary RAM bitfields without checking the PCIe register semantics.
- Repeated lane definitions: lane 0-15 equalization and margining layouts are repetitive, but copy/paste or generated-name errors can target the wrong lane and make link training failures hard to diagnose.
- Capability-list pointer fields must remain coherent with actual config-space layout. Incorrect `NEXT_PTR`, capability ID, or version interpretation can break capability walking.

## Test Signals

Useful validation signals for changes touching this chunk or its consumers:

- Compile coverage for AMDGPU with NBIO 7.4 ASIC support enabled; missing or renamed macros should fail at build time.
- Static checks that every used mask macro has a matching shift macro and that masks align with shifts for contiguous fields.
- Runtime PCIe bring-up on NBIO 7.4 devices, especially Arcturus/Aldebaran-class paths that include this header.
- SR-IOV smoke tests: PF load, VF enumeration, VF BAR assignment, reset notification, and mailbox behavior.
- PCIe AER tests or fault-injection where available: verify correctable/uncorrectable status, mask, and severity handling.
- Link-training diagnostics: negotiated speed/width, 8 GT/s and 16 GT/s equalization status, margining readiness/status, and absence of unexpected AER errors after link events.
- Interrupt tests for MSI/MSI-X enablement and vector masking on EPF1 paths.

## Chunk Boundary Notes

The chunk starts immediately after the EPF0 device-serial-number enhanced-capability list field definitions and ends in the middle of `BIF_CFG_DEV0_EPF1_0_PCIE_VC1_RESOURCE_CNTL`. The following chunk is needed to complete EPF1 VC1 resource control and any subsequent EPF1/EPF block definitions. Whole-file reconciliation should merge this with adjacent chunks to describe the complete NBIO 7.4 mask header.
