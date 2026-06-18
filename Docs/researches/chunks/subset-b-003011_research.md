# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 14625-17126

## Scope

This chunk is a generated AMD NBIO 6.1 register shift/mask header segment. It contains only C preprocessor constants; there are no functions, structs, runtime variables, allocations, locks, branches, loops, or direct MMIO operations in this range.

The slice begins in the tail of the `BIF_CFG_DEV0_EPF0_VF12_0` PCIe extended-capability area, covering AER log/prefix-log masks plus ATS and ARI masks. It then covers complete repeated PCIe virtual-function configuration-space blocks for `BIF_CFG_DEV0_EPF0_VF13_0`, `BIF_CFG_DEV0_EPF0_VF14_0`, and `BIF_CFG_DEV0_EPF0_VF15_0`. After the VF blocks, the chunk defines NBIO/BIF indirect access, scratch, interrupt, GFX MMIO CAM, Syshub, strap, endpoint RCC, downstream RCC, and downstream-port PCIe control masks. The final block is a boundary fragment that stops inside `PCIE_RX_CNTL` for `nbio_nbif_rcc_dwnp_dev0_BIFDEC1`.

Although this file is located under a `ceph-client` source mirror, this header is AMDGPU ASIC register metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header range is to publish bitfield layouts for NBIO 6.1 PCIe configuration, SR-IOV virtual-function, and RCC control registers. Each generated field follows the AMD register-header convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset used when packing or extracting a field.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask used to isolate, preserve, clear, or update that field.

The companion address header, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_offset.h`, supplies matching register offsets. Runtime AMDGPU code combines offsets from that header with these masks through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

## Important Macro Families

The opening VF12 tail completes AER log and virtualization capability definitions for `BIF_CFG_DEV0_EPF0_VF12_0`. It includes TLP header log and TLP prefix log dwords, ATS enhanced capability list/capability/control fields, and ARI enhanced capability/capability/control fields. These masks expose ATS invalidate queue depth, page-aligned request support, global invalidate support, STU programming, ATC enable, ARI next-function number, MFVC/ACS function-group support, function-group enables, and selected ARI function group.

The complete VF13, VF14, and VF15 blocks repeat a standard PCI Type 0 SR-IOV virtual-function configuration image:

- Identity and header fields: vendor ID, device ID, command, status, revision ID, programming interface, subclass, base class, cache-line size, latency timer, header/device type, BIST, BAR1 through BAR6, subsystem vendor/device adapter ID, ROM base, capability pointer, interrupt line, and interrupt pin.
- PCIe capability fields: capability-list linkage, PCIe version/type/slot/message number, device capability/control/status, link capability/control/status, device capability/control/status 2, link capability/control/status 2, and slot capability/control/status 2 placeholders.
- Interrupt capability fields: MSI capability list/control, MSI message address/data/mask/pending registers, 64-bit MSI aliases, MSI-X capability list/control, MSI-X table BIR/offset, and PBA BIR/offset.
- Vendor-specific and AER fields: PCIe vendor-specific enhanced capability list/header, two vendor-specific payload dwords, AER enhanced capability list, uncorrectable error status/mask/severity, correctable error status/mask, advanced error capability/control, four TLP header log registers, and four TLP prefix log registers.
- Virtualization-oriented capability fields: ATS enhanced capability/capability/control and ARI enhanced capability/capability/control for each VF.

Important PCIe device and link fields include max payload support/size, phantom functions, extended tags, acceptable L0s/L1 latency, role-based error reporting, captured slot power, FLR capability/initiation, error-reporting enables, relaxed ordering, no-snoop, max read request size, transactions pending, link speed/width, ASPM, read completion boundary, link disable/retrain, common clock configuration, extended sync, clock power management, hardware autonomous width/speed disable, bandwidth management interrupts, completion timeout ranges and disable, ARI forwarding, atomic operation controls, ID-based ordering, LTR, OBFF, end-end TLP prefix support/blocking, 10-bit tag support, target link speed, enter compliance, de-emphasis, equalization controls/status, and downstream component presence status.

The `nbio_nbif_bif_bx_pf_SYSPFVFDEC` and `nbio_nbif_bif_bx_pf_SYSDEC` sections publish index/data register masks and PF/system control state. They include `MM_INDEX`, `MM_DATA`, `MM_INDEX_HI`, Syshub and PCIe indirect index/data pairs, SBIOS and BIOS scratch dwords, BIF interrupt control masks for RLC/VCE/UVD, GFX MMIO register CAM address/remap pairs, CAM control/completion registers, and Syshub index/data masks.

The strap and RCC endpoint sections define platform and endpoint-side PCIe policy state. Strap masks cover generic BIF strap bits and `RCC_DEV0_EPF0_STRAP0__STRAP_FUNC_EN_DEV0_F0`. Endpoint RCC masks cover scratch state, write-lock and unsupported-request controls, interrupt enable/status bits, invalid PASID UR handling, immediate PME behavior, decode-to-hidden-register enables, LTR transmit policy, Dynamic Power Allocation data for functions 0 and 1, PME service timer, TX snoop/relaxed-ordering/TPH controls, requester ID packing, AER reporting and header-log timeout bits, RX error-ignore controls, TPH receive disable, and Gen2/Gen3 link-speed strap bits.

The downstream RCC sections define downstream-port controls. `DN_PCIE_CNTL` includes hardware-init write lock, downstream unsupported-request reporting disable, and LTR-message UR ignore controls. `DN_PCIE_CONFIG_CNTL`, `DN_PCIE_RX_CNTL2`, `DN_PCIE_BUS_CNTL`, and `DN_PCIE_CFG_CNTL` cover extended-tag override, FLR extend mode, immediate PME disable, AER completion-timeout relaxed-ordering disable, and hidden-register decode enables. The final downstream-port section starts generic `PCIE_ERR_CNTL` and `PCIE_RX_CNTL` masks for error-reporting disable, AER header-log timeout, immediate error-message sending, completion-timeout disable, short-prefix ignore, and RCB FLR timeout disable.

## Control Flow

There is no executable control flow in this header. Its effect is compile-time: consuming code receives the constants needed to compose or decode NBIO 6.1 register values.

Typical runtime use follows this pattern:

1. AMDGPU code selects a `cfgBIF_CFG_DEV0_EPF0_VF*_0_*`, `reg*`, or `smn*` offset from the NBIO 6.1 offset/SMN headers or local constants.
2. The register access layer reads a PCIe, SOC15, or SMN register value, or prepares a value to write.
3. Code applies this header's `__SHIFT` and `_MASK` macros directly or through field helpers.
4. The resulting value configures a VF control bit, decodes capability/status state, clears or masks an error, updates link/power policy, programs interrupt behavior, or inspects diagnostics.

Runtime flows that can consume these fields include SR-IOV VF config-space presentation, PF-side VF management, guest driver binding, VF FLR/reset handling, MSI/MSI-X delivery, PCIe link and power-management setup, AER collection and masking, ATS/ARI capability handling, LTR/PME/DPA policy, NBIO indirect register access, BIOS/firmware scratch exchange, GFX MMIO CAM remapping, and downstream-port error policy.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-backed register state owned by the GPU, firmware, platform straps, the host PCIe fabric, Linux PCI core policy, and AMDGPU NBIO/SR-IOV/power-management code.

The represented VF state includes identity/header values, BAR and ROM resource windows, command/status bits, capability-list pointers, PCIe device/link capability and control fields, link training and equalization state, MSI/MSI-X programming state, vendor-specific capability payloads, AER status/mask/severity/log state, ATS translation controls, and ARI function grouping. Some fields are static capability declarations, some are software-programmed controls, some are hardware-updated status, and some are sticky or write-one-to-clear diagnostics.

The represented non-VF state includes indirect register-index windows, BIOS/SBIOS scratch registers, interrupt enable/status registers, GFX MMIO CAM translation and completion state, strap-derived function enablement, endpoint/downstream PCIe control policy, LTR/DPA/PME settings, requester ID state, RX/TX/AER controls, and link-speed straps. The masks do not encode reset defaults, access permissions, side effects, polling rules, firmware ownership, write-one-to-clear behavior, or ordering constraints.

VF13 through VF15 are complete within this chunk. VF12 and the final downstream-port `PCIE_RX_CNTL` block are boundary fragments and require adjacent chunks before making whole-block claims.

## Dependencies And Integration Points

The primary dependency is the generated NBIO 6.1 register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_offset.h` supplies matching config-space and register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h` and `nbio_6_1_smn.h` provide related reset/default and SMN address definitions where used by NBIO 6.1 code.
- AMDGPU register helpers consume the generated `__SHIFT`/`_MASK` convention.

Observed direct include sites for the NBIO 6.1 shift/mask header in this source tree include `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c`, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h`, and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_inc.h`. Nearby users include PSP and display code that include the NBIO 6.1 offset header.

Concrete integration examples in this tree include `nbio_v6_1.c` reading and writing `EP_PCIE_TX_LTR_CNTL` through a hard-coded NBIO 6.1 SMN address and using `EP_PCIE_TX_LTR_CNTL__LTR_PRIV_MSG_DIS_IN_PM_NON_D0_MASK` from this mask namespace. That makes the endpoint RCC portion of this chunk directly relevant to PCIe LTR behavior during AMDGPU NBIO setup. `mxgpu_ai.c` is the SR-IOV/MxGPU integration point most likely to consume the VF-oriented config-space definitions.

Relevant integration surfaces are NBIO initialization, PCIe fabric setup, GPU power management on Vega10/Vega12-era ASICs, SR-IOV VF lifecycle, PF/VF isolation, guest config-space emulation or inspection, interrupt delivery, AER diagnostics, FLR and reset recovery, link retraining, LTR/PME/DPA policy, platform firmware scratch handoff, and GFX MMIO aperture remapping.

## Risks And Edge Cases

- The chunk boundaries are artificial. It starts after the beginning of the VF12 AER log area and stops inside the downstream-port `PCIE_RX_CNTL` masks; adjacent chunks are needed for complete VF12 and downstream-port analysis.
- These are untyped preprocessor constants. A stale shift or mask can compile cleanly while reading, clearing, or programming the wrong hardware bit.
- The VF13, VF14, and VF15 blocks are mechanically repetitive. Suffix mistakes can silently target the wrong virtual function and affect SR-IOV isolation, interrupt delivery, FLR, ATS/ARI behavior, or diagnostics.
- Register-address and field-mask synchronization is critical. A valid VF14 mask applied to a VF15 or non-VF offset can produce plausible bit operations while corrupting unrelated PCIe config state.
- PCIe control fields are interoperability-sensitive. Incorrect max payload, max read request, relaxed ordering, no-snoop, completion timeout, FLR, LTR, OBFF, ARI, ATS, atomic-op, link retrain, or target-speed values can cause DMA ordering bugs, enumeration failures, IOMMU translation failures, link instability, reset failures, or platform-specific hangs.
- MSI/MSI-X fields carry interrupt-delivery side effects. Width, address/data aliasing, table and PBA BIR/offset, mask, pending, or enable mistakes can cause lost interrupts, misrouted interrupts, or unexpectedly unmasked vectors.
- AER status, severity, mask, header log, and TLP prefix log fields may be sticky, hardware-owned, or write-one-to-clear. Generic read/modify/write treatment can clear diagnostic evidence or leave serious errors masked.
- ATS and ARI fields are virtualization-sensitive. Incorrect ATC enable/STU values, invalidate support decoding, next-function numbers, or ARI function-group controls can break guest enumeration, DMA translation, or PF/VF management assumptions.
- Endpoint and downstream RCC policy masks can affect global PCIe behavior, not just one VF. Error-reporting disables, hidden-register decode enables, FLR extend mode, LTR ignore/disable behavior, TPH disables, requester ID packing, and link-speed straps should not be changed without ASIC-specific ownership rules.
- BIOS/SBIOS scratch and strap fields may be firmware- or bootloader-owned. Treating them as free software scratch space can violate platform handoff contracts.
- GFX MMIO CAM masks affect register-window remapping. Incorrect CAM address/remap/control programming can route MMIO reads or writes to the wrong engine register space.

## Test Signals

Useful validation is primarily build-time and hardware-integration oriented:

- Build AMDGPU with NBIO 6.1, Vega10/Vega12 powerplay, and MxGPU/SR-IOV support enabled; missing, renamed, or duplicated macros should surface in `nbio_v6_1.c`, `mxgpu_ai.c`, `vega10_inc.h`, or `vega12_inc.h`.
- Compare this chunk's VF13 through VF15 register names and field widths against `nbio_6_1_offset.h` to ensure config-space offsets and masks remain synchronized.
- Boot affected ASICs and confirm PCIe config-space exposure for VF13, VF14, and VF15: identity/header fields, BARs, capability list, PCIe capability, MSI/MSI-X, VSEC, AER, ATS, and ARI should decode consistently.
- In SR-IOV configurations, create and remove VFs covering the VF12-VF15 range, bind guest drivers, run VF FLR, and verify VF isolation, config-space access, ARI enumeration, ATS/IOMMU behavior, and interrupt delivery.
- Exercise graphics, compute, DMA, and guest workloads with MSI/MSI-X enabled; lost interrupts, stuck pending bits, unexpected vector masking, or wrong requester IDs can indicate mask/offset drift.
- Run PCIe reset, suspend/resume, runtime power, and link retraining tests while monitoring link speed/width, completion-timeout behavior, LTR state, PME behavior, DPA state, FLR completion, and downstream-port error policy.
- Use AER/error-injection or platform diagnostics where available to verify uncorrectable/correctable status, masks, severity fields, header logs, TLP prefix logs, and endpoint/downstream error controls map to expected PCIe errors.
- Validate NBIO indirect index/data paths and GFX MMIO CAM programming on hardware paths that use them; wrong masks can appear as inaccessible registers, misrouted MMIO accesses, or invalid completion behavior.

## Chunk Notes

- Lines 14625-14683 cover the tail of `BIF_CFG_DEV0_EPF0_VF12_0`, from AER header/prefix logs through ATS and ARI capability/control masks.
- Lines 14687-15332 cover the complete `BIF_CFG_DEV0_EPF0_VF13_0` PCIe VF config-space block.
- Lines 15341-15986 cover the complete `BIF_CFG_DEV0_EPF0_VF14_0` PCIe VF config-space block.
- Lines 15995-16640 cover the complete `BIF_CFG_DEV0_EPF0_VF15_0` PCIe VF config-space block.
- Lines 16649-16835 define PF/system, indirect index/data, BIOS scratch, interrupt, GFX MMIO CAM, and Syshub masks.
- Lines 16840-16852 define strap masks, including function-enable strap state for device 0 function 0.
- Lines 16864-17068 define endpoint RCC PCIe masks for scratch, control, interrupts, RX/TX policy, LTR, DPA, PME, requester ID, AER, and link-speed straps.
- Lines 17073-17103 define downstream RCC PCIe masks for scratch, control, extended-tag override, FLR extend mode, bus control, and hidden-register decode.
- Lines 17107-17126 begin downstream-port `PCIE_ERR_CNTL` and `PCIE_RX_CNTL`; the final `PCIE_RX_CNTL` masks continue after this chunk.
