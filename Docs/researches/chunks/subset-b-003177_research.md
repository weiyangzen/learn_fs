# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 41596-43964

## Purpose

This chunk is a generated AMD NBIO 7.2.0 register field map. It exports C preprocessor constants for bit shifts and masks used to encode or decode fields in PCIe root-complex control, BIF/BX, physical-function, virtual-function, HDP coherency, mailbox, and strap registers. There are no functions, data structures, or executable control paths in this region; the operational behavior comes from AMDGPU register-access code that includes this header and combines these constants with register addresses from the matching `*_d.h` headers.

The chunk starts at the tail of downstream device 0 strap definitions, covers `nbio_nbif0_rcc_dwnp_dev0_BIFDEC1`, `nbio_nbif0_rcc_dev0_BIFDEC1`, `nbio_nbif0_bif_bx_BIFDEC1`, `nbio_nbif0_bif_bx_pf_BIFPFVFDEC1`, and most of `nbio_nbif0_rcc_strap_rcc_strap_internal`, and ends partway through endpoint function 1 strap 0.

## Register Areas Covered

- Downstream/root-complex PCIe control: `RCC_DWN_DEV0_1_DN_PCIE_STRAP_MISC2`, `RCC_DWNP_DEV0_1_PCIE_ERR_CNTL`, `PCIE_RX_CNTL`, `PCIE_LC_SPEED_CNTL`, `PCIE_LC_CNTL2`, `PCIEP_STRAP_MISC`, and `LTR_MSG_INFO_FROM_EP`.
- RCC device 0 control: interrupt, BACO request blocking, reset enable, VDM support, PCIe lane margining parameters, GPUIOV region selection, host VM enable, console IOV mode, peer register ranges, bus control, VGA/config apertures, XDMA bounds, requester/bus/devfunc lists, peer frame-buffer offsets, link state controls, LTR latency, and MH arbitration.
- BIF_BX1 common block: bus coherency and traffic class controls, scratch registers, reset controls, MM config access, interrupt/dummy-read controls, CLKREQ and other pad controls, doorbell monitor and interrupt controls, FB read/write enables, transaction-pending status, GFX address LUT entries 0-15, VF register/doorbell/FB enable and status bitmaps, HDP remap flush controls, ring-buffer base/read/write pointers, mailbox index, GPUIOV config sizes, PERST/PX/REFCLK/CLKREQ/PWRBRK/WAKE/VAUX pads, PCIe parameter save/restore, and S5 memory/dummy registers.
- BIF_BX_PF1 physical-function block: BME status, atomic unsupported-request logging and clears, self-ring doorbell GPA aperture base/control, HDP register/memory flush and invalidate controls, per-engine GPU HDP flush/invalidate request and done bitmaps, transaction-pending status, GFX LUT bypass, four transmit and four receive mailbox data dwords, mailbox valid/ack control, mailbox interrupt enables, and VM/HV compact mailbox fields.
- Strap defaults: device 0, device 1, and device 2 port straps 0-9; BIF straps 0-6; endpoint function 0 straps 0, 1, 2, 3, 4, 5, 8, 9, 13, and 14; and the beginning of endpoint function 1 strap 0.

## Important APIs, Types, and Constants

The only exported API surface is macro naming of the form:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

Important groups in this chunk include:

- PCIe error and link handling: `RCC_DWNP_DEV0_1_PCIE_ERR_CNTL__ERR_REPORTING_DIS_MASK`, `AER_HDR_LOG_TIMEOUT_MASK`, `SEND_ERR_MSG_IMMEDIATELY_MASK`, `RCC_DWNP_DEV0_1_PCIE_RX_CNTL__RX_PCIE_CPL_TIMEOUT_DIS_MASK`, and link speed strap masks for Gen2/Gen3/Gen4.
- RCC policy fields: `RCC_DEV0_1_RCC_BUS_CNTL__PMI_*`, `ROOT_ERR_LOG_ON_EVENT`, poisoned completion logging, downstream/primary completion abort/unsupported request handling, and private max payload/read-request size controls.
- Virtualization fields: `RCC_DEV0_1_RCC_GPUIOV_REGION__LFB_REGION_MASK`, `MAX_REGION_MASK`, `RCC_DEV0_1_RCC_GPU_HOSTVM_EN__GPU_HOSTVM_EN_MASK`, `RCC_DEV0_1_RCC_CONSOLE_IOV_MODE_CNTL__RCC_CONSOLE_IOV_MODE_ENABLE_MASK`, `MULTIOS_IH_SUPPORT_EN_MASK`, first-VF offset and VF stride masks.
- BIF_BX VF bitmaps: `BIF_BX1_VF_REGWR_EN__VF_REGWR_EN_VF0..VF30`, `BIF_BX1_VF_DOORBELL_EN__VF_DOORBELL_EN_VF0..VF31`, `BIF_BX1_VF_FB_EN__VF_FB_EN_VF0..VF30`, and corresponding `*_STATUS` fields.
- HDP coherency fields: `BIF_BX_PF1_GPU_HDP_FLUSH_ONLY_REQ`, `GPU_HDP_INVALIDATE_ONLY_REQ`, `GPU_HDP_FLUSH_REQ`, and `GPU_HDP_FLUSH_DONE`, each mapping CP0-CP9, SDMA0-SDMA1, and reserved engine bits across the 32-bit register.
- Mailbox fields: `BIF_BX_PF1_MAILBOX_MSGBUF_TRN_DW0..DW3`, `RCV_DW0..DW3`, `BIF_BX_PF1_MAILBOX_CONTROL__TRN_MSG_VALID_MASK`, `TRN_MSG_ACK_MASK`, `RCV_MSG_VALID_MASK`, and `RCV_MSG_ACK_MASK`.
- Strap fields for PCIe capabilities: ARI, ACS, AER, ECRC, DSN, extended tags, link speeds, L0s/L1 latency, lane equalization presets, LTR, OBFF, PM support, MSI/MSI-X, PASID, ATS, page request, resize BAR, FLR, atomics, PME, class/vendor/device IDs, BAR aperture sizes, SR-IOV VF counts and mapping, GPUIOV VSEC revision, and power-budget fields.

## Control Flow

There is no runtime control flow in this header chunk. Inclusion of this file makes the macros available to compile-time expressions used by low-level register helpers. A typical consuming flow is:

1. Select a register address from the matching NBIO address-definition header.
2. Read or prepare a 32-bit register value through AMDGPU MMIO/SMN/indirect register helpers.
3. Extract a field with `(value & FIELD_MASK) >> FIELD_SHIFT`, or update it by clearing `FIELD_MASK` and OR-ing the shifted new value.
4. Write the modified value back, if the register is writable.

The repeated `CP0..CP9`, `SDMA0..SDMA1`, `RSVD_ENG0..RSVD_ENG19`, `VF0..VF31`, `ID0..ID7`, and power-budget byte fields are intentionally encoded as separate macros rather than loops or arrays. Consumers must decide any iteration scheme.

## State and Persistence Behavior

This file stores no state. The represented hardware registers do hold persistent or semi-persistent device state while the GPU is powered:

- Strap registers represent reset-sampled configuration or firmware-programmed defaults for PCIe capabilities, identity, aperture sizing, virtualization, power management, and link behavior.
- Enable/status registers such as VF register-write, VF doorbell, VF FB, transaction-pending, BME, and HDP flush done reflect live hardware state.
- Clear/status fields in atomic error logs, doorbell interrupt control, and mailbox handshakes indicate write-one-clear or explicit acknowledge style semantics, but the exact side effects are defined by hardware documentation and consuming driver code, not by this header.
- BACO, S5 memory power, link-state, reset, and pad-control fields can affect low-power transitions or post-reset behavior if written by driver paths.

Because this is a generated mask header, persistence risks are indirect: wrong masks or shifts cause consumers to read, clear, or program the wrong hardware bits.

## Dependencies and Integration Points

The chunk depends only on the C preprocessor and the include order of AMDGPU ASIC register headers. It is expected to be paired with the same-version address header for NBIO 7.2.0 registers. The constants integrate with:

- AMDGPU NBIO/PCIe setup and error-handling code that controls PCIe AER, completion timeout, requester ID, LTR, ASPM/L1, link reset, link speed, and payload-size behavior.
- SR-IOV and GPUIOV paths that expose or restrict VF register writes, doorbells, frame-buffer access, VF BAR sizing, PASID/ATS/page-request capabilities, and console IOV behavior.
- Doorbell and interrupt paths that program BIF doorbell monitors, doorbell interrupts, interrupt dummy reads, MSI/MSI-X capabilities, and self-ring GPA apertures.
- HDP coherency/flush paths that request and poll per-engine HDP flush, invalidate, and flush-done bits for CP and SDMA engines.
- Mailbox and VM/HV communication paths that use transmit/receive data dwords, valid/ack bits, and interrupt-enable bits.
- Power-management and platform paths that rely on straps for ASPM timers, LTR behavior, PME, CLKREQ/WAKE/PWRBRK/VAUX pad fields, BACO request disables, S5 memory controls, and emergency power-reduction support.

The local tree contains similar macro names in other generated ASIC families such as `nbif_6_3_1_sh_mask.h`, so consumers may be shared across ASIC generations through versioned include selection or generated register tables.

## Risks and Edge Cases

- Register width assumptions matter. Most masks are 32-bit and use an `L` suffix; consumers should avoid sign-extension or type-width surprises when composing values, especially for high-bit masks such as `0x80000000L`.
- Adjacent multi-bit fields require preserving reserved bits. Writes should clear only the target mask and keep unrelated and reserved fields unchanged unless hardware guidance says otherwise.
- VF bitmaps are not uniform: some groups cover VF0-VF30 while doorbell enable/status includes VF31. Code that assumes all VF maps have 32 usable bits can overprogram unsupported fields.
- Strap fields are capability declarations. Changing or misreading them can advertise unsupported PCIe capabilities such as PASID, ATS, ACS, AER, atomics, MSI/MSI-X, resize BAR, or SR-IOV.
- HDP request/done fields encode many engines in one register. Polling the wrong engine mask can produce data-coherency bugs or false timeouts.
- Clear and acknowledge fields share registers with status fields in several blocks. Read-modify-write code must avoid unintentionally clearing interrupt/error/mailbox state.
- The chunk ends in the middle of the endpoint-function strap sequence, so full per-file research must be merged with adjacent chunks before drawing whole-file conclusions about all EPF1 strap fields.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware-integration oriented:

- The header compiles through AMDGPU builds that select NBIO 7.2.0 without duplicate or missing macro definitions.
- Register field helper tests or static checks confirm each mask equals `((field_max << shift) & mask)` for the intended field width and that high-bit masks are treated as unsigned values by consumers.
- SR-IOV/GPUIOV tests can verify VF register-write, doorbell, and FB enable/status behavior for boundary VFs, especially VF30 versus VF31.
- PCIe capability and link-management tests can verify advertised AER/ACS/ARI/ATS/PASID/MSI/MSI-X/resize-BAR/link-speed straps against expected device capabilities after reset.
- Doorbell and mailbox tests should exercise valid/ack and interrupt-enable fields without losing pending messages.
- HDP flush tests should request CP/SDMA flush or invalidate and poll matching `GPU_HDP_FLUSH_DONE` bits under workloads that require memory coherency.
- Power-management tests should cover BACO/S5, ASPM/LTR/PME/CLKREQ, link reset/down-entry behavior, and wake/power-break pad fields on hardware using NBIO 7.2.0.
