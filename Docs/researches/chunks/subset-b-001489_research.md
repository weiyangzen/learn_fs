# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_sh_mask.h lines 1-4658

## Scope

This chunk is the opening part of the generated AMD BIF 5.1 register shift/mask header. It begins with the `BIF_5_1_SH_MASK_H` include guard and defines preprocessor constants for register bit fields through line 4658. The covered range has no C functions or structs; it is a hardware-description contract consumed by AMDGPU/PowerPlay code together with the companion address header `bif_5_1_d.h`.

The chunk covers roughly 669 register field families. Each field is represented as a pair of macros:

- `<REGISTER>__<FIELD>_MASK`
- `<REGISTER>__<FIELD>__SHIFT`

The covered families include direct MMIO/config-space register fields, `_IND` variants for indirect access paths, PCIe configuration capability fields, BIF reset/power/doorbell/coherency controls, PCIe link training and error-reporting controls, and early BIF reset fields. The requested slice stops at `BIF_RESET_EN__PIF_STRAP_ALLVALID__SHIFT`; later fields in the same `BIF_RESET_EN` family continue after this chunk.

## Purpose

The header gives driver code symbolic names for BIF 5.1 bit positions and masks. BIF is the bus interface block that connects the GPU to PCIe and to internal clients such as SRBM, HDP, VGA, ROM, audio, XDMA, SDMA, CP, SMU, and video engines. These definitions keep register programming readable and reduce hard-coded hex constants in code that configures bus access, PCIe link behavior, interrupt routing, power gating, BAR layout, doorbells, coherency flushes, peer apertures, BACO power transitions, and Advanced Error Reporting.

This content is source-tree local to a Ceph client snapshot, but it is not Ceph filesystem logic. It is Linux DRM AMDGPU hardware register metadata for older Sea Islands / CIK-era ASIC support. For example, `iceland_ih.c` includes this header directly, and CIK-era power management code uses fields such as `PCIE_LC_SPEED_CNTL__LC_CURRENT_DATA_RATE`, `LC_FORCE_EN_SW_SPEED_CHANGE`, and `LC_INITIATE_LINK_SPEED_CHANGE` when reading or changing PCIe link speed.

## Important APIs, Types, And Macros

There are no callable APIs in this range. The exported interface is the macro set itself, usually paired with register address macros from `bif_5_1_d.h` and access helpers such as `RREG32`, `WREG32`, `RREG32_PCIE_PORT`, and read/modify/write helpers.

Important macro groups in this chunk include:

- Indexed MMIO access: `MM_INDEX`, `MM_INDEX_HI`, `MM_DATA`, and `BIF_MM_INDACCESS_CNTL` define the indirect register aperture fields used to select and transfer MMIO register values.
- Core BIF setup: `BUS_CNTL`, `CONFIG_CNTL`, `CONFIG_MEMSIZE`, `CONFIG_F0_BASE`, `CONFIG_APER_SIZE`, `CONFIG_REG_APER_SIZE`, `BIF_FB_EN`, and BIF scratch registers describe VGA enablement, ROM access, BAR/aperture sizing, frame-buffer read/write enablement, traffic-class routing, and firmware/driver scratch state.
- Credits, arbitration, interrupts, and debug: `MASTER_CREDIT_CNTL`, `SLAVE_REQ_CREDIT_CNTL`, `BIF_SLVARB_MODE`, `INTERRUPT_CNTL`, `INTERRUPT_CNTL2`, `BIF_DEBUG_CNTL`, `BIF_DEBUG_MUX`, `BIF_DEBUG_OUT`, and `HW_DEBUG` expose backpressure, request credits, interrupt generation, dummy reads, non-snoop controls, and debug muxing.
- Pad, SMBus, and CLKREQ controls: `CLKREQB_PAD_CNTL`, `SMBDAT_PAD_CNTL`, and `SMBCLK_PAD_CNTL` define electrical/pad control fields such as mode, select, slew, wake, Schmitt enable, and control-enable bits.
- Apertures and peer routing: `BIF_XDMA_LO/HI`, `PEER_REG_RANGE0/1`, `PEER0..3_FB_OFFSET_HI/LO`, `BIF_BUSNUM_*`, and `BIF_DEVFUNCNUM_*` configure XDMA windows, peer frame-buffer mappings, and bus/device/function matching.
- Doorbells and ring buffer: `BIF_DOORBELL_CNTL`, `BIF_DOORBELL_GBLAPER1/2_*`, `BIF_RB_CNTL`, `BIF_RB_BASE`, `BIF_RB_RPTR`, `BIF_RB_WPTR`, and writeback address registers define host doorbell handling and BIF ring-buffer state.
- Coherency flush controls: `HDP_REG_COHERENCY_FLUSH_CNTL`, `HDP_MEM_COHERENCY_FLUSH_CNTL`, `GARLIC_FLUSH_CNTL`, `GARLIC_FLUSH_ADDR_START_0..7`, `GARLIC_FLUSH_ADDR_END_0..7`, `GPU_HDP_FLUSH_REQ/DONE`, `GPU_GARLIC_FLUSH_REQ/DONE`, and `GARLIC_COHE_*` fields define flush request/done bits and remapped coherent register addresses for CP, SDMA, UVD, VCE, display, SAM, host doorbells, and related clients.
- Power and reset: `BACO_CNTL`, `BACO_CNTL_MISC`, `BF_ANA_ISO_CNTL`, `MEM_TYPE_CNTL`, `SMU_BIF_VDDGFX_PWR_STATUS`, `BIF_VDDGFX_*`, `BIF_RFE_*`, `BIF_PWDN_*`, `NEW_REFCLKB_TIMER*`, `BIF_CLK_PDWN_DELAY_TIMER`, and the start of `BIF_RESET_EN` describe BACO entry/exit, power-good signals, VDDGFX access stalling, warm/soft reset propagation, clock gating timers, and reset source enables.
- PCI and PCIe standard capability space: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, class/revision fields, BARs, ROM base, interrupt line/pin, adapter ID, PM capability, PCIe capability, device/link control and status, MSI, vendor-specific capability, virtual channel, device serial number, AER, BAR enhanced capability, power budget, DPA, secondary PCIe capability, ACS, ATS, page request, and PASID-related fields.
- PCIe controller internals: `PCIE_INDEX/DATA`, `PCIE_CNTL`, `PCIE_CONFIG_CNTL`, `PCIE_DEBUG_CNTL`, `PCIE_INT_CNTL/STATUS`, `PCIE_CNTL2`, `PCIE_RX_CNTL*`, `PCIE_TX_*`, `PCIE_CI_CNTL`, `PCIE_BUS_CNTL`, `PCIE_LC_*`, `PCIE_P_*`, `PCIE_OBFF_CNTL`, `PCIE_TX_LTR_CNTL`, `PCIE_PERF_*`, `PCIE_STRAP_*`, `PCIE_PRBS_*`, and `PCIEP_*` expose controller-private link, PHY, protocol, performance, strap, PRBS, flow-control, equalization, and error-injection state.
- `_IND` aliases: many early BIF register families are repeated with `_IND` suffixes. These retain the same field layout while targeting the indirect register namespace used by indirect access macros.

## Control Flow

The header itself has no runtime control flow. Its constants become part of runtime control paths when included by C files that build values to write to BIF/PCIe registers or decode values read from those registers.

Typical use follows a read/modify/write pattern:

1. Read a register offset from `bif_5_1_d.h`, for example `ixPCIE_LC_SPEED_CNTL` or `mmBACO_CNTL`.
2. Clear or test fields with the corresponding `*_MASK`.
3. Position new field values with the matching `*__SHIFT`.
4. Write the register back, or poll until a status field reaches the expected value.

The link-speed path in CIK-era code is a representative consumer: it reads `PCIE_LC_SPEED_CNTL`, extracts `LC_CURRENT_DATA_RATE`, sets or clears software/hardware speed-change enable fields, writes a target speed, sets `LC_INITIATE_LINK_SPEED_CHANGE`, and polls for that initiation bit to clear. BACO hwmgr code uses `BACO_CNTL` masks in table-driven command sequences that write enable/isolation/power-off/reset fields and wait on `BACO_MODE`, power-good, or `RCU_BIF_CONFIG_DONE` status bits.

Several macros encode request/done handshakes rather than ordinary configuration. For HDP and GARLIC coherency, driver or firmware code can assert client-specific request bits such as `CP0`, `SDMA0`, or `SDMA1` and then observe matching `DONE` bits. For reset and power paths, control bits are mixed with status bits and timers, so the sequencing is external to this header but depends on these exact fields.

## State And Persistence Behavior

This header does not allocate host-side state. It names bits in hardware registers whose values live in the GPU's MMIO, PCI configuration, indirect, or PCIe-port register spaces. Persistence depends on the register family:

- PCI configuration and capability fields reflect configuration-space state negotiated with the host and can survive until reset, function-level reset, hot reset, or explicit OS/driver reconfiguration.
- Link control/status fields represent current PCIe link training, width, speed, equalization, replay, flow-control, lane, and error state. Some fields are latched status or clear-on-write status fields, while others are persistent knobs until reset or reprogramming.
- BACO, clock, reset, VDDGFX, and RFE fields influence low-power state transitions and reset propagation. They are reset-sensitive and can directly affect whether downstream register access is possible.
- Scratch registers and BIOS scratch fields can be used as firmware/driver handoff or diagnostic state.
- Flush request/done and error-status fields represent transient synchronization or fault state and must be interpreted with the hardware semantics of the specific register.

Because many fields are mirrors of hardware straps or capabilities, the macros are stable compile-time constants while their corresponding register values may be read-only, write-one-to-clear, write-protected, strap-derived, or only writable during specific power/reset windows.

## Dependencies And Integration Points

The direct dependency is `bif_5_1_d.h`, which provides the register offsets (`mm*`, `ix*`, and related address constants). This shift/mask header is also part of a larger generated register set under `drivers/gpu/drm/amd/include/asic_reg/`, and the same field names are often reused in newer NBIO/BIF headers with ASIC-specific prefixes.

Important integration points include:

- AMDGPU MMIO access helpers, which turn `mm*` offsets plus these masks/shifts into 32-bit register reads and writes.
- PCIe port access helpers such as `RREG32_PCIE_PORT`, used for `PCIE_LC_*` controller registers.
- CIK/Sea Islands power management and link-management code, which depends on `PCIE_LC_SPEED_CNTL` and `BACO_CNTL` fields for link speed reporting, link retraining, and BACO transitions.
- Interrupt handling and IH setup for BIF 5.1 devices, where the header is included to describe BIF interrupt and dummy-read controls.
- Firmware and BIOS handoff paths that use BIOS scratch, adapter ID, BAR, PM, MSI, AER, ACS, ATS, PASID, DPA, and strap fields.
- Coherency and command submission paths that require HDP/GARLIC flush request/done and doorbell aperture fields to line up with hardware.

The `_IND` macro families are especially sensitive because they let code address equivalent fields through a different register access path. A direct/indirect mismatch can cause a driver to appear correct in one path while programming the wrong register through another.

## Risks And Edge Cases

The main risk is silent register-field drift. These are raw hardware bit definitions; a wrong mask, shift, or copied field name can compile cleanly while causing the driver to modify unrelated bits. That is high impact for reset, BACO, PCIe link training, AER masking, BAR sizing, ACS/ATS/PASID capability exposure, and coherency flush paths.

Several fields use full-register masks such as `0xffffffff`, while others use tightly packed subfields. Code must not assume all fields can be updated with simple assignment; many registers require preserving reserved bits, strap-derived values, or write-one-to-clear status bits.

The chunk contains repeated direct and `_IND` definitions with nearly identical names. Manual edits or generated-header merges can easily update one side and miss the other. The same applies to repeated indexed families such as `GARLIC_FLUSH_ADDR_START_0..7`, lane equalization controls for lanes 0..15, DPA substates 0..7, PRBS error counters 0..15, PCIe state history registers, and peer aperture registers.

Security and isolation fields are easy to misuse. ACS, ATS, page request, PASID, requester ID, peer FB offsets, bus/device/function matching, and doorbell translation fields all affect address routing, peer-to-peer access, or process address-space behavior. Incorrect exposure can break IOMMU expectations or allow traffic to be routed outside intended apertures.

Power/reset fields can make the device temporarily inaccessible. `BACO_CNTL`, `BIF_RESET_EN`, `BIF_RESET_CNTL_IND`, RFE soft-reset triggers, clock power-down timers, and VDDGFX compare/stall fields need sequencing with firmware/SMU and PCIe link state. Setting a reset-enable or power-off bit without the expected status polling can wedge link training or lose config state.

The requested line range ends mid-family at `BIF_RESET_EN__PIF_STRAP_ALLVALID__SHIFT`. Any final per-file report should reconcile this with the following chunk, which continues `BIF_RESET_EN` with BIF core reset, FLR enables, and per-function reset delay fields.

## Test Signals

Useful validation signals include:

- Kernel build coverage for BIF 5.1/CIK paths, catching missing or renamed macros used by AMDGPU, PowerPlay, and IH code.
- Register readback tests on matching hardware showing PCIe link speed/width extraction from `PCIE_LC_SPEED_CNTL`, `LINK_STATUS`, and `PCIE_LC_STATUS*` matches `lspci` and kernel logs.
- Link retraining tests where software-initiated speed changes set `LC_INITIATE_LINK_SPEED_CHANGE`, clear after polling, and result in the expected negotiated speed.
- BACO entry/exit tests that observe expected transitions of `BACO_MODE`, `BACO_BCLK_OFF`, `BACO_POWER_OFF`, power-good bits, and `RCU_BIF_CONFIG_DONE`.
- Doorbell and ring-buffer tests confirming global doorbell apertures, BIF RB writeback, overflow status/clear, and self-ring/translation checks behave as expected.
- Coherency tests that request HDP/GARLIC flushes for CP/SDMA/video/display clients and observe the matching done bits before dependent memory reads.
- AER/MSI/PCIe error injection or fault logging tests that validate uncorrectable/correctable error status, masks, severity, header logs, and interrupt status fields.
- IOMMU and peer-to-peer validation around ACS, ATS, PASID, page request, peer FB offsets, and bus/device/function ID filters.
- Generated-header consistency checks ensuring every `*_MASK` has a matching `*__SHIFT`, direct and `_IND` field sets stay aligned where they are meant to mirror each other, and companion `bif_5_1_d.h` register names exist for the field families used by code.
