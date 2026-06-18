# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 71627-74047

## Scope

This chunk is a generated AMD NBIO 4.3.0 register shift/mask header segment. It contains only C preprocessor constants; there are no functions, structs, variables, allocation paths, locks, branches, loops, or direct MMIO accesses in this range.

The slice starts at the tail of `BIF_CFG_DEV0_EPF0_VF6_1_LINK_CAP`, covers the rest of the `BIF_CFG_DEV0_EPF0_VF6_1` PCIe virtual-function configuration-space block, then covers complete `BIF_CFG_DEV0_EPF0_VF7_1` and `BIF_CFG_DEV0_EPF0_VF8_1` blocks. It begins `BIF_CFG_DEV0_EPF0_VF9_1` and stops at `BIF_CFG_DEV0_EPF0_VF9_1_PCIE_VENDOR_SPECIFIC_HDR`; VF9 vendor-specific payload, AER, ATS, ARI, and later fields continue after this chunk.

Although this file is located under a `ceph-client` source mirror, this header is AMDGPU ASIC register metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header range is to publish bitfield layouts for NBIO 4.3.0 SR-IOV virtual-function PCI configuration-space images. Each generated field is represented by the usual AMD register macro pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position used when packing or extracting a field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, clear, preserve, or update that field.

The companion address header, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h`, supplies the matching register offsets. Runtime code combines those offsets with this header through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15_PREREG`, and `SOC15_REG_OFFSET`.

## Important Macro Families

The opening VF6 fragment completes `LINK_CAP` fields for link speed, link width, power-management support, L0s/L1 exit latency, clock power management, surprise-down reporting, data-link active reporting, bandwidth notification capability, ASPM optionality, and port number. The rest of VF6 then defines link control/status, PCIe capability 2, MSI/MSI-X, vendor-specific enhanced capability, AER, and ARI/router-related fields.

The full VF7 and VF8 blocks repeat a standard PCI Type 0 virtual-function configuration image:

- Identity and header fields: vendor ID, device ID, command, status, revision, programming interface, subclass, base class, cache line, latency, header type, BIST, BAR1 through BAR6, CardBus CIS pointer, adapter/subsystem ID, ROM base, capability pointer, interrupt line/pin, min grant, and max latency.
- PCIe capability fields: capability-list linkage, PCIe type/version/slot/message fields, device capability/control/status, link capability/control/status, device capability/control/status 2, and link capability/control/status 2.
- Interrupt capability fields: MSI capability list/control, MSI address/data/ext-data/mask/pending registers, 64-bit MSI aliases, MSI-X table-size/function-mask/enable, table BIR/offset, and PBA BIR/offset.
- Vendor-specific and AER fields: vendor-specific enhanced capability list/header, two scratch payload dwords, AER enhanced capability list, uncorrectable error status/mask/severity, correctable error status/mask, advanced error capability/control, four TLP header log dwords, and four TLP prefix log dwords.
- Virtualization-oriented capability fields: ARI enhanced capability list/capability/control and router data fields. Unlike some related NBIO generations, this specific slice exposes ARI/RTR tails here and not a complete ATS family for these VFs inside the covered range.

The VF9 block repeats the same layout from identity/header fields through PCIe, MSI/MSI-X, and the beginning of vendor-specific enhanced capability state. This chunk ends after the VF9 vendor-specific header mask, before VF9 vendor-specific scratch payload, AER, ARI/RTR, and any remaining extended capability fields.

Important PCIe fields in these blocks include max payload support/size, phantom functions, extended tags, endpoint L0s/L1 acceptable latency, function-level reset capability/initiation, completion timeout controls, ARI forwarding, atomic operation controls, ID-based ordering, LTR, OBFF, 10-bit tag support, target link speed, link retraining/disable, common clock configuration, autonomous width/speed disable controls, de-emphasis, equalization status, DRS status, and link bandwidth status. AER fields cover conditions such as DLP errors, surprise down, poisoned TLP, flow-control protocol error, completion timeout, completion abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic-op egress blocked, and TLP prefix blocked.

## Control Flow

There is no executable control flow in this header. Its effect is compile-time: it gives C code the constants needed to compose and decode NBIO PCIe configuration-space register values.

Typical runtime use follows this pattern:

1. AMDGPU code selects a `cfgBIF_CFG_DEV0_EPF0_VF*_1_*` or related NBIO register offset from `nbio_4_3_0_offset.h`.
2. The register access layer reads or writes a 16-bit or 32-bit PCIe/NBIO configuration value through SOC15 helpers.
3. Code applies this header's `__SHIFT` and `_MASK` macros directly or via field helpers.
4. The resulting value configures a VF control bit, decodes capability/status state, clears a sticky error, polls hardware-owned state, or exposes decoded state to PCIe, SR-IOV, reset, interrupt, power-management, or diagnostics code.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-backed PCIe configuration-space state owned by the GPU, firmware, host PCIe fabric, Linux PCI core policy, and AMDGPU PF/SR-IOV management paths.

The represented state includes VF identity/header values, BAR and ROM resource windows, command/status bits, capability-list pointers, PCIe device/link capability and control state, link training and equalization status, MSI/MSI-X programming state, vendor-specific capability payloads, AER error status/mask/severity/log state, ARI function controls, and router data fields. Some fields are static capability declarations, some are software-programmed controls, some are hardware-updated status, and some are sticky or write-one-to-clear diagnostics. The generated masks do not encode reset defaults, access permissions, side effects, ordering requirements, polling timeouts, or ownership boundaries.

VF7 and VF8 are complete within this chunk. VF6 and VF9 are boundary fragments and require adjacent chunks before making whole-VF claims.

## Dependencies And Integration Points

The primary dependency is the generated NBIO 4.3.0 register database:

- `nbio_4_3_0_offset.h` supplies the matching register addresses and base indices.
- `nbio_4_3_0_sh_mask.h` supplies the field positions and masks in this chunk.
- AMDGPU register helpers in the SOC15/NBIO access layer consume the generated `__SHIFT`/`_MASK` convention.

Observed direct include sites for this generated header include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c`, which uses NBIO 4.3 offsets and masks for revision discovery, framebuffer access enablement, doorbell aperture/range setup, interrupt handling, clock gating, and related NBIO control.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_7_ppt.c`, which include the same NBIO 4.3 generated headers in SMU13 power-management paths.

The most relevant integration surfaces for these VF configuration fields are SR-IOV VF creation/removal, PF-side VF config-space emulation or inspection, guest driver binding, VF FLR/reset flows, MSI/MSI-X interrupt delivery, PCIe link and power-management policy, AER diagnostics, ARI enumeration/function grouping, suspend/resume, runtime power transitions, and SMU/NBIO coordination on hardware that uses the NBIO 4.3.0 register map.

## Risks And Edge Cases

- The chunk boundaries are artificial. It starts after the VF6 `LINK_CAP` shift lines and stops inside VF9's vendor-specific capability area; adjacent chunks are needed for complete VF6 and VF9 analysis.
- These are untyped preprocessor constants. A stale or incorrect mask can compile cleanly while reading or writing the wrong hardware bit.
- The VF blocks are mechanically repetitive. Suffix mistakes between VF6, VF7, VF8, and VF9 can silently target the wrong virtual function and affect SR-IOV isolation, interrupt delivery, or diagnostics.
- Register-address and field-mask synchronization is critical. Applying a valid VF8 mask to a VF9 or non-VF offset can produce plausible bit operations while corrupting unrelated configuration state.
- PCIe control fields are interoperability-sensitive. Incorrect FLR, max payload, max read request, relaxed-ordering, no-snoop, LTR, OBFF, ARI, link retraining, completion-timeout, or autonomous speed/width values can cause DMA ordering bugs, enumeration failures, link instability, reset failures, or platform-specific hangs.
- MSI/MSI-X fields carry interrupt-delivery side effects. Wrong address/data width, table/PBA BIR, table offset, mask, pending, or enable fields can cause lost interrupts, misrouted interrupts, or unexpectedly unmasked vectors.
- AER status, mask, severity, header log, and TLP prefix log fields can be sticky, write-one-to-clear, or hardware-owned. Generic read/modify/write treatment can clear diagnostic evidence or leave serious errors masked.
- BAR and ROM masks describe resource exposure. Wrong masks can confuse VF resource sizing or expose invalid apertures.
- Vendor-specific and ARI/router fields are virtualization-sensitive. Incorrect capability-list linkage, VSEC length, ARI function controls, or router data decoding can break guest enumeration or PF/VF management assumptions.

## Test Signals

Useful validation is primarily build-time and hardware-integration oriented:

- Build AMDGPU with NBIO 4.3.0 and SMU13 support enabled; missing, renamed, or duplicated macros should surface in `nbio_v4_3.c` or the SMU13 PPT files that include this generated header.
- Compare VF6 through VF9 register names against `nbio_4_3_0_offset.h` to confirm field masks and offsets remain synchronized across repeated VF blocks.
- Boot affected hardware and confirm PCIe config-space exposure remains sane for VF7 and VF8: identity/header fields, BARs, capability list, PCIe capability, MSI/MSI-X, vendor-specific capability, AER, ARI, and router data should decode consistently.
- In SR-IOV configurations, create and remove VFs covering the VF6-VF9 range, bind guest drivers, perform VF FLR, and verify VF isolation, config-space access, reset behavior, ARI enumeration, and interrupt delivery.
- Exercise graphics, compute, DMA, and guest workloads with MSI/MSI-X enabled; lost interrupts, stuck pending bits, or unexpected vector masking can indicate MSI field layout or offset drift.
- Run PCIe reset, suspend/resume, runtime power, and link retraining tests while monitoring link speed/width, completion-timeout behavior, LTR/OBFF state, and FLR completion.
- Use AER/error-injection or platform diagnostics where available to verify uncorrectable/correctable status, masks, severity fields, header logs, and TLP prefix logs map to expected PCIe errors.

## Chunk Notes

- Lines 71627-72119 complete the latter portion of `BIF_CFG_DEV0_EPF0_VF6_1`, beginning at `LINK_CAP` masks and ending with `RTR_DATA2`.
- Lines 72120-72841 cover the complete `BIF_CFG_DEV0_EPF0_VF7_1` address block.
- Lines 72842-73563 cover the complete `BIF_CFG_DEV0_EPF0_VF8_1` address block.
- Lines 73564-74047 begin `BIF_CFG_DEV0_EPF0_VF9_1` and end at `PCIE_VENDOR_SPECIFIC_HDR`; later VF9 vendor-specific, AER, ARI/RTR, and remaining extended capability fields are outside this work item.
