# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h lines 17349-17381

## Scope

This chunk is the final 33-line tail of the generated AMDGPU NBIO 4.3.0 offset header. It contains C preprocessor constants only, followed by the closing `#endif` for `_nbio_4_3_0_OFFSET_HEADER`. There are no C functions, structs, enums, variables, locks, allocations, loops, or executable statements in this range.

The range starts in the middle of the `cfgBIF_CFG_DEV0_EPF3_1_PCIE_BAR*` extended-capability block, covering BAR5/BAR6, power-budgeting, Dynamic Power Allocation, ACS, PASID, and ARI offsets for `BIF_CFG_DEV0_EPF3_1`. The immediately preceding lines contain the start of the same endpoint-function PCIe capability sequence, including BAR1-BAR4 and AER/TLP diagnostic offsets.

Although this repository path is under a `ceph-client` mirror, this file is AMD GPU register metadata for DRM/AMDGPU. It has no direct Ceph distributed-filesystem behavior.

## Purpose

`nbio_4_3_0_offset.h` publishes generated register/configuration-space addresses for the NBIO 4.3.0 IP block. This chunk supplies the tail of the PCIe extended-capability offset map for device 0, endpoint function 3, instance 1:

- `cfgBIF_CFG_DEV0_EPF3_1_PCIE_BAR5_CAP` through `cfgBIF_CFG_DEV0_EPF3_1_PCIE_BAR6_CNTL` identify BAR sizing and BAR-control capability registers at offsets `0x0224` through `0x0230`.
- `cfgBIF_CFG_DEV0_EPF3_1_PCIE_PWR_BUDGET_*` identifies the PCIe power-budgeting extended capability at `0x0240` through `0x024c`.
- `cfgBIF_CFG_DEV0_EPF3_1_PCIE_DPA_*` identifies Dynamic Power Allocation capability, status/control, and per-substate power-allocation bytes at `0x0250` through `0x0267`.
- `cfgBIF_CFG_DEV0_EPF3_1_PCIE_ACS_*` identifies Access Control Services capability and control offsets at `0x02a0` through `0x02a6`.
- `cfgBIF_CFG_DEV0_EPF3_1_PCIE_PASID_*` identifies PASID capability and control offsets at `0x02d0` through `0x02d6`.
- `cfgBIF_CFG_DEV0_EPF3_1_PCIE_ARI_*` identifies Alternative Routing-ID Interpretation capability and control offsets at `0x0328` through `0x032e`.

The matching field layouts live in `nbio_4_3_0_sh_mask.h`. Runtime consumers combine these offset macros with shift/mask macros and AMDGPU register/config access helpers. This offset header does not define register field width, access permissions, reset values, side effects, or ordering requirements.

## Important APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the macro namespace itself. Consumers use the constants as hardware ABI names.

The source tree includes `nbio_4_3_0_offset.h` together with `nbio_4_3_0_sh_mask.h` in NBIO, SMU, and display code, including:

- `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c`, which uses NBIO 4.3.0 register definitions with helpers such as `RREG32_SOC15`, `WREG32_SOC15`, and `REG_SET_FIELD`.
- `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c` and `smu_v13_0_7_ppt.c`, which include the NBIO 4.3.0 register headers for power-management integration.
- `drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c` and `dcn321_resource.c`, which include the same offset header for display-resource code on matching ASICs.

The exact macros in this slice are not directly referenced by non-generated C code in the observed tree, but they remain part of the generated ASIC register contract. They may be consumed by generic register helpers, debug tooling, generated tables, or downstream code that programs or decodes endpoint-function PCIe config space.

## Control Flow

This header has no local control flow. The effective runtime pattern is external:

1. ASIC-specific AMDGPU code includes the NBIO 4.3.0 offset and shift/mask headers.
2. A caller selects one of these `cfgBIF_CFG_DEV0_EPF3_1_*` offsets when it needs to read, write, expose, or decode PCIe configuration space for endpoint function 3.
3. The caller applies companion shift/mask macros from `nbio_4_3_0_sh_mask.h`, or a PCI/NBIO accessor, to extract fields, compose values, clear sticky bits, or program controls.
4. Hardware, firmware, PCI core, IOMMU, virtualization, or power-management logic observes the resulting PCIe capability state.

The ordering and safety rules are determined by the consuming driver path and the PCIe/NBIO hardware specification, not by this generated header.

## State And Persistence Behavior

The chunk stores no software state and persists nothing to disk. It names hardware-visible configuration and capability registers. Persistence is therefore governed by GPU reset domains, PCI config-space save/restore, firmware initialization, suspend/resume, function-level reset, hot reset, and explicit driver or firmware writes.

The represented hardware state includes BAR capability/control metadata, power-budget selection/data, DPA capability and substate allocation state, ACS isolation controls, PASID enablement, and ARI function-routing controls. Some registers are static capability descriptors, some are host- or firmware-programmed controls, and some may be hardware-updated status. The offset macros do not distinguish read-only capability fields from read/write controls, sticky status, or command fields.

## Dependencies And Integration Points

The direct dependencies are the sibling generated NBIO 4.3.0 headers:

- `nbio_4_3_0_sh_mask.h` supplies field shifts and masks for these register names. For example, the companion masks define BAR size-supported fields, power-budget data fields, DPA substate and latency fields, ACS capability/control bits, PASID controls, and ARI controls.
- Other generated NBIO 4.3.0 headers, where present, provide related defaults or register metadata outside this offset-only file.

The broader integration points are AMDGPU NBIO initialization, SMU power-management code, PCIe capability exposure, PCI resource/BAR handling, AER and RAS diagnostics in adjacent lines, IOMMU/PASID integration, SR-IOV or multi-function routing, and isolation features such as ACS. These offsets are tied to the NBIO 4.3.0 generation; similar names exist in NBIO 2.3, 7.x, and other generated headers, but their offset encoding and base-index model can differ.

## Risks And Edge Cases

- Generated offset drift can compile cleanly if macro names remain stable but values change incorrectly. The driver would then access the wrong PCIe config register.
- This chunk starts inside a capability sequence. BAR1-BAR4 and prior AER/TLP-prefix offsets are in the preceding chunk, so the final per-file report should merge adjacent chunks before describing the complete `EPF3_1` endpoint-function layout.
- The offsets are byte-oriented PCIe config offsets, including halfword and byte registers such as DPA control and substate allocation entries. Consumers must use access sizes and alignment rules appropriate to PCI configuration space.
- BAR capability/control offsets affect resource sizing and aperture exposure. Incorrect use can corrupt enumeration, BAR sizing, or resource assignment.
- Power-budget and DPA registers affect power management and platform power reporting. Wrong offsets or field interpretation can cause misleading power capability data or incorrect substate control.
- ACS, PASID, and ARI are isolation and routing sensitive. Misprogramming these registers can affect peer-to-peer forwarding, IOMMU translation tagging, process address-space IDs, function enumeration, and virtualization boundaries.
- The closing `#endif` means this is the physical end of the generated header. Any accidental truncation before this point would break the include guard and likely fail compilation; accidental edits after it might be ignored or create duplicate-definition hazards.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Build AMDGPU with NBIO 4.3.0 support enabled. Include-guard damage, missing macros, or syntax drift should surface at compile time.
- Run generated-register consistency checks against the authoritative NBIO 4.3.0 register database, verifying the offset sequence from BAR5/BAR6 through ARI and the closing header structure.
- Boot affected AMD GPUs and confirm PCI config-space enumeration, capability-chain traversal, BAR sizing, and endpoint-function resource reporting remain stable.
- Exercise SMU and power-management paths on matching ASICs, checking that PCIe power budgeting and DPA-related reporting do not regress.
- Validate IOMMU/PASID and ACS behavior under workloads that use process address spaces, peer-to-peer traffic restrictions, or virtualization-sensitive routing.
- Check ARI and multi-function enumeration paths where endpoint function 3 is visible, especially after suspend/resume and function reset.

## Chunk-Specific Notes For Merge

Merge this chunk with the preceding `nbio_4_3_0_offset.h` chunks before producing the final per-file research document. Preserve that this slice covers only the tail of `cfgBIF_CFG_DEV0_EPF3_1` PCIe extended-capability offsets, from BAR5 capability at `0x0224` through ARI control at `0x032e`, and the file-closing `#endif`.
