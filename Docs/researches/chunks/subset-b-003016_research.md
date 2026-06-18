# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 27021-29468

## Scope

This chunk is a generated AMDGPU NBIO 6.1 shift/mask header segment. It contains C preprocessor constants only: `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros for NBIO/NBIF PCIe configuration-space register fields. There are no C functions, structs, enums, branches, loops, locks, allocations, MMIO operations, or disk persistence in this range.

The range is part of the `BIF_CFG_DEV0_EPF0_VF*_1_*` namespace, which describes PCIe configuration-space fields for virtual functions under device 0, endpoint function 0. It starts in the tail of the VF0 `LINK_CAP2` register masks, then covers the rest of VF0's PCIe capability, MSI/MSI-X, VSEC, AER, ATS, and ARI capability field definitions. It then covers complete visible blocks for VF1, VF2, and VF3 from standard PCI header fields through ARI control. The final section begins the VF4 address block and reaches only the first fields of `BIF_CFG_DEV0_EPF0_VF4_1_DEVICE_CAP`, so VF4's later capability, MSI/MSI-X, AER, ATS, and ARI fields are outside this chunk.

The source path sits under a local `ceph-client` mirror, but this file is AMDGPU hardware metadata. Its purpose is GPU NBIO/PCIe register description, not Ceph or distributed filesystem behavior.

## Purpose

The purpose of these definitions is to publish exact bit positions and masks for NBIO 6.1 PCIe configuration registers associated with SR-IOV virtual-function configuration spaces. Runtime driver code pairs these masks with matching register offsets from `nbio_6_1_offset.h` and access helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and `WREG32_FIELD15`.

The chunk's functional surface is PCIe configuration and capability modeling for VFs:

- Standard PCI header identity and control fields for VF1, VF2, VF3, and the start of VF4: vendor/device ID, command/status, revision and class code, cache-line/latency/header/BIST, BARs, subsystem ID, ROM BAR, capability pointer, interrupt line, and interrupt pin.
- PCIe capability fields: PCIe capability header, device capabilities/control/status, link capabilities/control/status, second-generation device and link capabilities/control/status, and reserved slot capability/control/status placeholders.
- MSI and MSI-X capability fields: capability-list headers, MSI enable/multiple-message/64-bit/per-vector-mask controls, MSI address/data/mask/pending registers, MSI-X table/PBA BIR and offset fields, MSI-X table size, function mask, and MSI-X enable.
- PCIe vendor-specific enhanced capability fields: VSEC enhanced capability header, VSEC ID/revision/length, and scratch registers.
- Advanced Error Reporting fields: enhanced capability header, uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, header log words, and TLP prefix log words.
- Address Translation Services and Alternative Routing-ID Interpretation fields: ATS enhanced capability, ATS capability/control, ARI enhanced capability, ARI capability, and ARI control.

These macros are a hardware ABI. A wrong shift or mask can compile cleanly while causing driver or firmware code to advertise a wrong PCIe capability, corrupt adjacent bits during read/modify/write, misread a VF error status, misconfigure MSI/MSI-X routing, or expose incorrect virtualization and IOMMU behavior.

## Important Macro Families

### VF0 Tail

The chunk begins with only the final masks for `BIF_CFG_DEV0_EPF0_VF0_1_LINK_CAP2`, specifically crosslink-supported and reserved bits. The shift definitions and earlier fields for this register are in the previous chunk.

The remaining VF0 content covers:

- `LINK_CNTL2`, `LINK_STATUS2`, and reserved slot second-capability registers for target link speed, compliance entry, autonomous speed disable, selectable de-emphasis, transmit margin, equalization completion, per-phase equalization success, and link equalization request.
- MSI/MSI-X capability blocks, including message address/data registers, 64-bit MSI variants, mask and pending bitmaps, MSI-X table/PBA location fields, and MSI-X enable/function-mask state.
- PCIe VSEC enhanced capability and VSEC header/scratch fields.
- AER enhanced capability, uncorrectable and correctable error status/mask/severity fields, AER capability/control, header logs, and TLP prefix logs.
- ATS and ARI enhanced capabilities and controls, including ATS STU and ATC enable, invalidate queue depth, page-aligned request, global invalidate support, ARI next function number, ARI function group, and MFVC/ACS function-group bits.

### VF1, VF2, And VF3 Complete Visible Blocks

The address-block markers `nbio_nbif_bif_cfg_dev0_epf0_vf1_bifcfgdecp`, `vf2_bifcfgdecp`, and `vf3_bifcfgdecp` start repeated VF configuration-space blocks. Each visible VF1/VF2/VF3 block has the same broad layout:

- Standard PCI configuration header: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`, six `BASE_ADDR_*` registers, `ADAPTER_ID`, `ROM_BASE_ADDR`, `CAP_PTR`, `INTERRUPT_LINE`, and `INTERRUPT_PIN`.
- PCIe capability: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`, and reserved slot capability/control/status2 registers.
- MSI and MSI-X capability: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, MSI address/data/mask/pending registers, `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`.
- VSEC and AER extended capability: `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, scratch registers, `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, AER status/mask/severity/control registers, header logs, and TLP prefix logs.
- ATS and ARI extended capability: `PCIE_ATS_ENH_CAP_LIST`, `PCIE_ATS_CAP`, `PCIE_ATS_CNTL`, `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL`.

The repetition is important. These macros are separate names for separate VF register windows; code must use the VF-specific offset and mask set consistently. Reusing a VF1 mask name with a VF2/VF3 register address would be semantically wrong even if the bit layout happens to match.

### Standard PCI Header Fields

The standard PCI header macros define the VF-visible identity and control surface. `COMMAND` includes I/O enable, memory enable, bus master enable, parity response, SERR, fast back-to-back, and interrupt disable bits. `STATUS` includes interrupt status, capability-list presence, parity and abort/error status, DEVSEL timing, and system error indicators.

`BASE_ADDR_1` through `BASE_ADDR_6`, `ROM_BASE_ADDR`, `ADAPTER_ID`, and class-code fields are especially sensitive because they participate in PCI enumeration, BAR sizing, resource assignment, subsystem identity, and driver binding. For VFs, these values are also part of the virtualization contract between PF firmware/hardware, the host PCI core, and guest-visible VF state.

### PCIe Capability And Link Fields

The PCIe capability macros cover device capability/control/status and link capability/control/status. Important fields include max payload support and size, phantom functions, extended tags, acceptable L0s/L1 latencies, role-based error reporting, captured slot power, error-reporting enables, relaxed ordering, max read request size, no-snoop, AUX power, transaction pending, max link speed/width, ASPM support/control, common clock, retrain/link disable, bandwidth notification, data link active, slot clock, and current link speed/width.

The second-generation capability fields add completion timeout ranges and controls, ARI forwarding, atomic operation capability and routing controls, ID-based ordering, LTR support and enablement, OBFF support/enablement, emergency power reduction controls, TPH completion support, end-to-end TLP prefix support, target link speed, compliance controls, de-emphasis/margin fields, link equalization completion and per-phase success bits, and crosslink support.

### MSI, MSI-X, VSEC, And AER

The MSI block defines capability IDs and next pointers plus enablement and payload fields for MSI address/data, 64-bit data, masks, and pending bits. The MSI-X block defines table size, function mask, enablement, table BIR/offset, and PBA BIR/offset. These masks govern interrupt capability advertisement and interrupt routing state for VFs.

The VSEC block contains enhanced capability list fields, VSEC ID/revision/length, and scratch registers. These fields are vendor-specific and should be interpreted with AMD's generated register database and surrounding driver/firmware ownership rules.

The AER block is the largest repeated family in this chunk. It exposes uncorrectable errors such as data link protocol, surprise down, poisoned TLP, flow control, completion timeout, completion abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress blocked, and TLP prefix blocked. It also exposes matching masks and severities, correctable error status/masks for receiver error, bad TLP/DLLP, replay rollover, replay timer timeout, advisory non-fatal error, corrected internal error, header log overflow, AER control bits, multiple error indicators, ECRC generation/checking capability/enable bits, header log words, and TLP prefix logs.

### ATS And ARI

The ATS macros define enhanced capability list fields, invalidate queue depth, page-aligned request support, global invalidate support, STU, and ATC enable. These fields interact with the IOMMU/address-translation path and with per-VF address translation state elsewhere in the GPU.

The ARI macros define enhanced capability list fields, MFVC/ACS function group capabilities/enables, the next function number, and the ARI function group. These fields affect PCIe function numbering and routing behavior when ARI is enabled by platform policy.

### VF4 Opening

The `nbio_nbif_bif_cfg_dev0_epf0_vf4_bifcfgdecp` block begins near the end of the chunk. The visible VF4 portion covers the standard PCI header through `PCIE_CAP` and the first `DEVICE_CAP` fields visible at the boundary. The rest of VF4's `DEVICE_CAP`, device/link controls, MSI/MSI-X, AER, ATS, and ARI definitions are in the next chunk.

## Important APIs, Types, And Functions

This chunk defines no callable APIs, C types, or functions. Its exported interface is the macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives a field's bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field's already-shifted bit mask.
- Register names are paired with address macros in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_offset.h`.

The practical API is the AMDGPU register-helper layer. Code typically reads a register, clears a `_MASK`, shifts a value by `__SHIFT`, and writes the register back, or uses helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` that rely on these exact generated names. `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c` includes `nbio_6_1_sh_mask.h` and uses the same generated-mask contract for revision ID extraction, doorbell aperture setup, HDP flush masks, interrupt setup, clock/power management, ASPM/LTR programming, register remapping, and NBIO function-table registration. PowerPlay include headers for Vega10/Vega12 also include this NBIO 6.1 mask header.

## Control Flow

There is no executable control flow in this header. Runtime control flow is supplied by the NBIO, PCIe, SR-IOV, power-management, and firmware paths that consume the generated register definitions:

1. IP discovery selects NBIO 6.1 support and installs the NBIO function table.
2. Driver or firmware code selects a VF-specific register address from `nbio_6_1_offset.h`.
3. The code selects the matching field macro from this mask header.
4. It reads, decodes, updates, or writes the hardware register through SOC15/PCIe/MMIO helpers.
5. Hardware, PCIe config-space emulation, the host PCI core, IOMMU, or guest-visible VF state observes the changed field.

Concrete in-tree NBIO 6.1 code demonstrates the helper pattern even when it does not directly manipulate these VF1-VF4 config registers in the searched C file. For example, `nbio_v6_1_set_reg_remap()` chooses a remap offset based on `mmBIF_BX_DEV0_EPF0_VF0_HDP_MEM_COHERENCY_FLUSH_CNTL` for SR-IOV VF cases, and `nbio_v6_1_program_aspm()` performs read/modify/write updates using NBIO 6.1 PCIe capability and link-control masks. The VF configuration fields in this chunk are the same generated register ABI for VF PCIe configuration-space state.

## State And Persistence Behavior

The header stores no software state and persists nothing to disk. It describes hardware-backed PCIe configuration and status state whose lifetime depends on device reset, function-level reset, SR-IOV enablement, PF policy, guest assignment, PCI config writes, power transitions, firmware initialization, and explicit driver programming.

Important state represented by this chunk includes:

- VF PCI identity and enumeration state: IDs, class code, command/status, BARs, subsystem IDs, ROM BAR, capability pointers, and interrupt pins.
- VF PCIe capability state: payload size, read request size, error reporting enables, relaxed ordering/no-snoop, link control/status, link equalization state, LTR/OBFF/emergency power reduction, ARI forwarding, atomic operation controls, and completion timeout controls.
- VF interrupt state: MSI/MSI-X enablement, message address/data, mask and pending bits, MSI-X table/PBA locations, and function mask state.
- Error-reporting state: AER masks, severities, sticky error status, ECRC controls, header logs, and TLP prefix logs.
- Address translation and routing state: ATS capability/control and ARI capability/control bits.

Some fields are configuration values that may remain stable until reset or PF/firmware reprogramming. Other fields are live status, sticky error bits, latched diagnostic logs, pending interrupt masks, or capability advertisements synthesized from straps and hardware policy. The macro names do not encode access semantics such as read-only, write-one-clear, self-clearing, sticky, guest-owned, PF-owned, or firmware-owned. Consumers must rely on the hardware register database, PCIe rules, SR-IOV ownership model, and established AMDGPU programming sequences.

## Dependencies And Integration Points

This chunk must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_offset.h`, which supplies the matching register addresses.
- Other NBIO 6.1 generated headers, including `nbio_6_1_default.h` and `nbio_6_1_smn.h`, where defaults and SMN aliases are needed.
- AMDGPU register-helper conventions in NBIO, SOC15, PCIe indirect/direct access, and read/modify/write helper code.
- PCIe, MSI/MSI-X, AER, ATS, ARI, SR-IOV, and IOMMU architectural semantics.

Principal in-tree integration points are:

- `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, the NBIO 6.1 implementation consumer for this generated header family.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h` and `vega12_inc.h`, which include the NBIO 6.1 mask header for power-management and hardware-manager code.
- SR-IOV and PCI assignment paths that depend on consistent per-VF configuration-space layout, even if the direct register manipulation is firmware-owned or in code outside this chunk.
- MMHUB/IOMMU-related ATS state, since ATS capability/control bits in VF PCI config space must line up with address-translation enablement in memory-management hardware.

## Risks And Edge Cases

- Generation mismatch is the main risk. NBIO headers contain many similar PCIe config-space register families across versions and VF numbers; using NBIO 6.1 masks with another generation's offsets can silently corrupt the wrong bits.
- The chunk has artificial boundaries. VF0 `LINK_CAP2` is incomplete at the start, and VF4 `DEVICE_CAP` is incomplete at the end. Whole-register or whole-VF conclusions require adjacent chunks.
- Per-VF repetition is easy to misuse. VF1, VF2, and VF3 have nearly identical field layouts, but the symbolic names still represent distinct register windows.
- PCI config-space fields are often OS-visible. Changing command bits, BARs, link controls, MSI/MSI-X state, or capability pointers behind the PCI core or guest can break enumeration, resource routing, interrupts, or guest-visible device behavior.
- MSI/MSI-X masks and pending bits may have side effects or ownership constraints. Generic read/modify/write can lose pending state if access semantics are ignored.
- AER status and log fields may be sticky, write-one-clear, or latch-on-error. Incorrect masks can hide errors, clear evidence prematurely, or report a wrong severity to the host.
- ATS fields affect IOMMU isolation and address translation. Advertising or enabling ATS inconsistently with MMHUB/IOMMU policy can cause translation faults or isolation failures.
- ARI fields affect function numbering and routing. Incorrect ARI next-function or group controls can confuse PCI topology handling, especially under SR-IOV.
- Reserved fields are explicitly represented in several registers. Writing nonzero reserved bits or failing to preserve them during read/modify/write can create hardware-specific failures that are difficult to reproduce.

## Test And Verification Signals

Useful validation for this chunk is mostly compile coverage, register/header consistency checks, and PCIe/SR-IOV runtime testing:

- Build AMDGPU configurations that include `nbio_v6_1.c`, Vega10/Vega12 power-management includes, and the NBIO 6.1 generated headers. This catches missing, renamed, or malformed macros.
- Run generated-header consistency checks that pair each `__SHIFT` with the expected `_MASK`, verify masks fit field widths, and compare register names against `nbio_6_1_offset.h`.
- On NBIO 6.1 hardware with SR-IOV enabled, inspect VF PCI configuration space with `lspci -vv` or equivalent tools and verify identity, BAR, command/status, PCIe capability, MSI/MSI-X, AER, ATS, and ARI fields match platform policy.
- Exercise VF assignment and guest driver load/unload. Interrupt delivery, MSI/MSI-X masking, BAR mapping, config-space reads/writes, and reset behavior are strong signals for this region.
- Trigger or inject PCIe/AER errors where supported and confirm uncorrectable/correctable status, severity, mask, header log, and TLP prefix fields map to the intended VF and error type.
- Validate ATS/IOMMU behavior with VF DMA workloads, page invalidation paths, and translation-fault handling. ATS capability/control mismatches should show up as IOMMU faults, stalled DMA, or guest-visible errors.
- Test ARI/SR-IOV enumeration with multiple VFs. Function numbering, capability chains, and next-function behavior should remain stable across PF reset, VF FLR, suspend/resume, and guest rebind.
