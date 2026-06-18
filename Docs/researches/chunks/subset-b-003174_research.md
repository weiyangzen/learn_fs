# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 34271-36712

## Scope

This chunk covers generated shift and mask macros for AMD NBIO 7.2.0 register fields. It starts at the final mask for `BIF_BX0_BIF_DOORBELL_INT_CNTL` and then covers several address blocks:

- BIF/BX0 fields for framebuffer access, RAS interrupt vector selection, VF transaction-pending status, NBIF graphics address LUT entries, HDP remap flush controls, and BIF ring-buffer control/pointers.
- PF0 BIF fields for bus-mastering status, unsupported atomic error logging, self-ring doorbell GPA aperture setup, HDP coherency flush/invalidate controls, per-engine HDP flush request/done masks, transaction pending status, and graphics-address LUT bypass.
- RCC device 0 EPF0 MSI-X vector table fields for vectors 0 through 3, including address low/high, message data, vector mask, and pending bits, plus PBA entries.
- GDC fields for SDP/SHUB interface control, NBIF graphics doorbell status, SDMA/IH/VCN/RLC doorbell ranges, ATDMA arbitration, doorbell fencing, S2A 64-bit doorbell support, and SHUBCLK DPM accounting.
- SYSHUB direct fields for OBFF emulation, urgent modes, and reset behavior on several host-clock switch/client controls.
- GDC RAS control and status groups for SOC, SHUB, and NIC domains.
- GDC reset controls for PF FLR, graphics-driver reset, link reset, hard/soft reset, and SDP port reset.
- Root-complex PCI configuration fields for vendor/device/class IDs, bridge windows, PM/PCIe/MSI/SSID/MSI-map capabilities, vendor-specific and virtual-channel enhanced capabilities, device serial number, AER status/masks/severity/header logs/root error reporting, link control 3, lane error status, and lane 0-3 equalization controls.

The file is a generated hardware register bitfield map. This chunk defines preprocessor constants only: there are no C functions, structs, variables, storage allocations, or executable control flow.

## Purpose

The purpose of this header section is to provide the bit-level ABI between AMDGPU NBIO 7.2 driver code and the NBIO/BIF/GDC/PCIe hardware register layout. Each field is represented in the standard generated form:

- `<REGISTER>__<FIELD>__SHIFT`, the starting bit.
- `<REGISTER>__<FIELD>_MASK`, the field mask used to isolate, set, or test the field.

Driver code pairs these macros with register addresses from `nbio_7_2_0_offset.h` and helper macros such as `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, and `SOC15_REG_OFFSET`. The masks avoid hard-coded bit positions in code that enables framebuffer access, maps doorbell ranges, controls HDP flushes, configures reset behavior, and interprets PCIe configuration or AER status.

## Important Macro Families

### BIF/BX0 Access, LUT, and Ring Buffer Fields

`BIF_BX0_BIF_FB_EN` exposes the basic framebuffer read/write enable bits used by NBIO bring-up paths before memory controller access is considered available. `BIF_BX0_BIF_INTR_CNTL` selects the RAS interrupt vector source, while `BIF_BX0_BIF_MST_TRANS_PENDING_VF` and `BIF_BX0_BIF_SLV_TRANS_PENDING_VF` expose 31-bit pending transaction masks for VF-visible master/slave traffic.

`BIF_BX0_NBIF_GFX_ADDR_LUT_CNTL` controls a 16-entry graphics address LUT through enable, MSI address mode, and broadcast mode fields. `BIF_BX0_NBIF_GFX_ADDR_LUT_0` through `_15` each provide a 24-bit address field. `BIF_BX0_REMAP_HDP_MEM_FLUSH_CNTL` and `BIF_BX0_REMAP_HDP_REG_FLUSH_CNTL` provide remap addresses for HDP memory/register flush controls; `nbio_v7_2_remap_hdp_registers()` writes these registers from `adev->rmmio_remap.reg_offset`.

`BIF_BX0_BIF_RB_CNTL`, `BIF_BX0_BIF_RB_BASE`, `BIF_BX0_BIF_RB_RPTR`, `BIF_BX0_BIF_RB_WPTR`, and writeback address high/low registers define the NBIF ring-buffer control surface. Fields cover enable, size, write-pointer writeback, writeback timer, translation, interrupt priority/arbitration, reset-by-FLR disable, overflow clear, base address, read/write offsets, overflow status, and writeback address.

### PF0 Doorbell, HDP, and Error Handling

`BIF_BX_PF0_BIF_BME_STATUS` tracks DMA activity while bus mastering is low and has a matching clear bit. `BIF_BX_PF0_BIF_ATOMIC_ERR_LOG` captures unsupported-request atomic conditions for opcode, requester-enable-low, length, and non-relaxed/non-request-like cases, with separate clear bits for each.

`BIF_BX_PF0_DOORBELL_SELFRING_GPA_APER_BASE_LOW/HIGH` and `BIF_BX_PF0_DOORBELL_SELFRING_GPA_APER_CNTL` define the self-ring doorbell GPA aperture base, enable, mode, and size. `nbio_v7_2_enable_doorbell_selfring_aperture()` composes these fields when programming `adev->doorbell.base`.

The HDP coherency group includes register/memory flush address fields, flush-only and invalidate-only address fields, and three repeated 32-bit per-engine bitmaps: `BIF_BX_PF0_GPU_HDP_FLUSH_ONLY_REQ`, `BIF_BX_PF0_GPU_HDP_INVALIDATE_ONLY_REQ`, `BIF_BX_PF0_GPU_HDP_FLUSH_REQ`, and `BIF_BX_PF0_GPU_HDP_FLUSH_DONE`. Each bitmap names CP0-CP9, SDMA0-SDMA1, and reserved engine bits 0-19. `nbio_v7_2.c` exposes the HDP flush request/done register offsets and uses the `BIF_BX_PF0_GPU_HDP_FLUSH_DONE__CP*` and `__SDMA*` masks in its `amdgpu_nbio_hdp_flush_reg` integration.

### MSI-X Table Fields

The `RCC_DEV0_EPF0_0_GFXMSIX_*` register family defines MSI-X table entries for vectors 0 through 3. Each vector has low address fields, high address fields, message data fields, and control fields. The `_1` and `_2` suffixed variants expose adjacent packed portions or alternate views with the same field names. Control fields include `MASK_BIT` and `PENDING_BIT`; PBA registers expose 32-bit pending bit arrays.

These fields form the device-side PCIe interrupt delivery table rather than the Linux MSI-X API itself. Driver code should treat them as hardware register encodings and leave allocation, masking policy, and interrupt routing coordinated with the PCI core and AMDGPU interrupt handling.

### GDC Doorbells, Arbitration, and DPM

`GDC0_NGDC_SDP_PORT_CTRL`, `GDC0_NGDC_SDP_PORT_CTRL_SOCCLK`, and `GDC0_NGDC_SDP_PORT_CTRL1_SOCCLK` cover SDP disconnect hysteresis, OBFF urgent early wakeup, ATDMA response pool count, and virtual-channel credit reservations. `GDC0_SHUB_REGS_IF_CTL` controls whether non-PF MMREG requests dropped by SHUB also set errors.

`GDC0_BIF_SDMA0_DOORBELL_RANGE`, `GDC0_BIF_IH_DOORBELL_RANGE`, `GDC0_BIF_VCN0_DOORBELL_RANGE`, and `GDC0_BIF_RLC_DOORBELL_RANGE` share the same `OFFSET` and `SIZE` encoding. These are directly used by `nbio_v7_2_sdma_doorbell_range()`, `nbio_v7_2_vcn_doorbell_range()`, and `nbio_v7_2_ih_doorbell_range()` to enable or disable engine doorbell windows. `GDC0_NBIF_GFX_DOORBELL_STATUS` reports whether a graphics doorbell was sent.

`GDC0_ATDMA_MISC_CNTL` and `GDC0_S2A_MISC_CNTL` configure arbitration and 64-bit doorbell support across SDMA, CP, RLC, and other channels. `GDC0_BIF_DOORBELL_FENCE_CNTL` controls doorbell fencing for CP, SDMA0-SDMA5, and RLC plus a once-trigger disable bit. `GDC0_SHUBCLK_DPM_CTRL`, `GDC0_SHUBCLK_DPM_WR_WEIGHT`, `GDC0_SHUBCLK_DPM_RD_WEIGHT`, and read/write counters provide SHUBCLK DPM metering state for DMA read/write activity.

### SYSHUB, RAS, and Reset Fields

`OBFF_EMU_CFG_SOCCLK`, `OBFF_EMU_CFG_SHUBCLK`, and `OBFF_EMU_CFG_NICCLK` expose OBFF emulation enable and urgent-mode controls in several clock domains. `HST_CLK*_SW*_CL*_CNTL` registers provide FLR-on-reset and link-reset-on-reset enable bits for host-clock switch/client combinations.

The RAS groups follow a regular control/status layout for `GDCSOC`, `GDCSHUB`, and `GDCNIC` domains. Central status registers report egress-stall and error-event detection. Leaf control registers enable error-event detection, poison/parity/receiver-error event handling, egress stalls, and propagation. Leaf status registers report event reception, poison/parity detection, generated error events, generated egress stalls, propagated error events, and propagated stalls.

The reset block includes `SHUB_PF_FLR_RST` per-device/per-PF FLR reset bits, `SHUB_GFX_DRV_VPU_RST`, `SHUB_LINK_RESET` per-link reset bits, hard and soft reset enables for core/register/STY/SDP/SION domains, and `SHUB_SDP_PORT_RST` bits for NBIF, ATHUB, ATDMA, MP4SDP, GDC, NTB, and SION reset lines.

### Root Complex PCIe Configuration and AER

The `BIF_CFG_DEV0_RC0_*` block maps root-complex PCI configuration space. It includes conventional identity, command, status, class, header, BAR/window, bus-number, interrupt, and bridge-control fields; PM capability fields; PCIe capability, device/link/slot/root capability and control/status fields; MSI message address/data fields; subsystem ID and MSI-map fields; vendor-specific enhanced capability fields; virtual channel capability/control/status fields; and device serial-number fields.

The AER section covers enhanced capability headers, uncorrectable error status/mask/severity, correctable error status/mask, advanced error capability/control, TLP header logs, root error command/status, error source ID, and TLP prefix logs. Error classes include DLP, surprise down, poison, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic-op egress blocked, TLP prefix blocked, and poisoned TLP egress blocked. The chunk ends in the lane-equalization family after lane 3's receive-preset-hint mask; the lane 3 upstream preset fields continue in the next chunk.

## Control Flow and State Behavior

This header has no runtime control flow. It influences compiled driver behavior by defining the constants used to compose and decode 16-bit and 32-bit MMIO/config-space register values.

The persistent state described here is hardware state. Key durable or latched state includes framebuffer access enablement, pending transaction bits, address LUT entries, HDP remap addresses, BIF ring-buffer configuration and pointers, self-ring doorbell aperture base/control, per-engine HDP flush request and completion bits, MSI-X vector table contents, doorbell window offset/size fields, DPM counters, RAS control/status latches, reset control bits, PCI bridge windows, PCIe capability/control/status fields, MSI address/data, virtual channel mappings, and AER error logs.

Some fields are command-like or clear-on-write style rather than persistent configuration. Examples include atomic error clear bits, BME status clear, BIF ring write-pointer overflow clear, SHUBCLK DPM clear, reset assertion bits, HDP flush/invalidate request bits, root error reporting enables, and AER status/mask/severity updates. Correct consumers must follow the sequencing, polling, and timeout rules in the owning AMDGPU/NBIO/PCIe code and hardware specification; the generated masks do not encode ordering.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header convention:

- `nbio_7_2_0_offset.h` supplies register addresses such as `regBIF_BX0_BIF_FB_EN`, `regBIF_BX0_REMAP_HDP_MEM_FLUSH_CNTL`, `regBIF_BX_PF0_GPU_HDP_FLUSH_REQ`, `regGDC0_BIF_SDMA0_DOORBELL_RANGE`, and the `BIF_CFG_DEV0_RC0_*` config offsets.
- `nbio_7_2_0_default.h`, where present, supplies reset/default values for the same register set.
- AMDGPU register helpers consume the `__SHIFT` and `_MASK` definitions through `REG_SET_FIELD`, `REG_GET_FIELD`, SOC15 MMIO helpers, and PCIe-port accessors.

Observed integration in this tree includes `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, which includes this header and uses these fields to:

- Enable or disable framebuffer reads/writes through `BIF_BX0_BIF_FB_EN`.
- Remap HDP memory/register flush controls through `BIF_BX0_REMAP_HDP_*`.
- Program SDMA, VCN, and IH doorbell ranges through `GDC0_BIF_*_DOORBELL_RANGE`.
- Program the self-ring doorbell aperture through `BIF_BX_PF0_DOORBELL_SELFRING_GPA_APER_*`.
- Expose HDP flush request/done registers and completion masks through `BIF_BX_PF0_GPU_HDP_FLUSH_DONE__CP*` and `__SDMA*`.

The PCIe config macros are integration points for PCIe capability handling, platform firmware defaults, Linux PCI enumeration, and AER/RAS diagnostics. The RAS and reset macros integrate with reliability, recovery, FLR, link-reset, and suspend/resume paths even where this specific chunk is not directly referenced by a local C file.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can write unrelated NBIO, BIF, GDC, or PCIe config fields, causing memory access failure, lost interrupts, broken doorbells, incomplete HDP flushes, reset storms, or PCIe link/configuration regressions.
- Repeated register families are easy to corrupt mechanically. HDP per-engine bitmaps, MSI-X vector entries, RAS leaf controls/statuses, and lane equalization registers have very similar names but encode different hardware state.
- Doorbell range fields directly control engine-visible MMIO doorbell windows. Wrong offset or size values can route notifications to the wrong engine or disable queues for SDMA, VCN, IH, or RLC.
- HDP flush request/done masks are synchronization-sensitive. Missing a done bit, using the wrong engine bit, or confusing flush-only, invalidate-only, and full flush registers can leave CPU/GPU memory views incoherent.
- RAS and AER fields include sticky error/status and severity policy. Clearing, masking, or reclassifying errors incorrectly can hide real hardware faults or produce noisy false reporting.
- Reset fields affect PFs, links, SHUB domains, and SDP ports. Accidental writes can reset active functions, break link training, or disrupt unrelated IP blocks.
- PCIe root-complex fields overlap OS-owned configuration policy. Driver changes should avoid fighting the Linux PCI core over BAR/window, MSI, virtual-channel, PM, and link-control ownership.
- This chunk starts with a trailing macro from `BIF_BX0_BIF_DOORBELL_INT_CNTL` and ends mid-register-family in `BIF_CFG_DEV0_RC0_PCIE_LANE_3_EQUALIZATION_CNTL`; the merged per-file report must connect adjacent chunks for complete family coverage.

## Test and Validation Signals

Useful validation is primarily build, bring-up, and hardware integration coverage:

- Build AMDGPU with NBIO 7.2 support enabled to catch renamed, missing, or incompatible generated macros.
- NBIO bring-up tests should verify framebuffer read/write enablement, revision/memsize access, HDP remap writes, and HDP flush request/done completion for CP and SDMA engines.
- Doorbell tests should exercise SDMA, VCN, IH, and RLC doorbell ranges, including disabled-size paths and self-ring aperture programming.
- Interrupt tests should cover MSI/MSI-X delivery, masking, pending bits, IH doorbell delivery, and AER/root-error interrupt reporting.
- Suspend/resume, FLR, link reset, and GPU reset tests should cover SHUB reset fields and confirm active functions and links recover cleanly.
- RAS validation should inject or observe SOC/SHUB/NIC leaf errors, confirm central status propagation, and verify status clear/mask behavior follows policy.
- PCIe validation should check command/status, link speed/width, payload/read-request sizing, PM state, virtual-channel negotiation status, AER logs, and lane equalization status after boot and after reset.

## Unresolved Cross-Chunk References

Line 34271 is the final mask for `BIF_BX0_BIF_DOORBELL_INT_CNTL`; that register's earlier shift and mask fields belong to the previous chunk. The lane 3 equalization control family continues after line 36712 with the upstream preset and hint masks in the next chunk. The merge/reconciliation lane should join those adjacent pieces when producing the final per-file document.
