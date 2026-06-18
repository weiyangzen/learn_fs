# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_sh_mask.h lines 1-2525

## Scope

This chunk is the opening slice of the generated AMD NBIO 7.9.0 register shift/mask header. It contains only C preprocessor constants and comments: no functions, structs, enums, executable control flow, allocations, locking, or software-owned persistent objects. The definitions give bit positions and masks for NBIO/BIF/RCC/GDC hardware registers used by the AMDGPU driver when accessing PCIe, SR-IOV, doorbell, HDP flush, mailbox, partitioning, and fabric steering state.

The slice starts at the file guard and covers these address blocks:

- `aid_nbio_nbif0_bif_bx_SYSDEC`
- `aid_nbio_nbif0_rcc_dwn_dev0_BIFDEC1`
- `aid_nbio_nbif0_rcc_dwnp_dev0_BIFDEC1`
- `aid_nbio_nbif0_rcc_ep_dev0_BIFDEC1`
- `aid_nbio_nbif0_bif_bx_pf_SYSPFVFDEC`
- `aid_nbio_nbif0_bif_bx_BIFDEC1`
- `aid_nbio_nbif0_rcc_dev0_BIFDEC1`
- `aid_nbio_nbif0_rcc_dev0_epf0_BIFDEC2`
- `aid_nbio_nbif0_rcc_strap_BIFDEC1`
- `aid_nbio_nbif0_bif_bx_pf_BIFPFVFDEC1`
- `aid_nbio_nbif0_rcc_dev0_epf0_BIFPFVFDEC1[13440..14975]`
- the beginning of `aid_nbio_nbif0_gdc_GDCDEC`, ending inside the `GDC0_A2S_CNTL_SW2` register definition.

## Purpose and Register Families

The header provides the field layout half of AMDGPU's ASIC register database for NBIO 7.9.0. Companion `*_d.h` files provide register offsets; this `*_sh_mask.h` file provides `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants for field extraction and update.

The covered `SYSDEC` block defines indirect PCIe register index/data windows (`BIF_BX0_PCIE_INDEX`, `DATA`, `INDEX2`, `DATA2`, high index bytes), BIOS/SBIOS/driver/firmware scratch registers, and GFX MMIO register CAM mappings. The CAM entries expose eight address/remap pairs plus enable/completion controls, allowing hardware/driver configuration of MMIO remapping behavior. Scratch registers are full 32-bit fields and serve as mailbox-like state shared by firmware, SBIOS, and driver code.

The downstream and downstream-port RCC blocks expose PCIe control fields for hidden config decode, extended tag override, FLR extension, bus/PMI behavior, error reporting, AER header logging, RX ignore policies, link speed straps up to Gen5, link bandwidth notifications, multi-function strap state, and LTR message capture from endpoints.

The endpoint RCC block defines endpoint-side PCIe control and status fields. It includes interrupt enable/status bits for correctable, non-fatal, fatal, user-detected, miscellaneous, and power-state-change events; malformed atomic operation and unsupported-request behavior; config decode to hidden Gen2-Gen5 registers; LTR transmit control fields; dynamic power allocation capability/status/substate power allocations for functions 0 and 1; TPH support; requester ID fields; AER timer-expired bits for functions 0-7; RX error suppression bits for PASID/prefix/TPH cases; and link speed straps through Gen5.

The PF system/PF-VF decode block supplies indirect MMIO and RSMU access windows for physical function 0: MM index/data/high-offset fields and RSMU index/data/high-index fields. These constants are integration points for register accesses that are routed through a PF aperture rather than direct MMIO addresses.

The main BIF block covers bridge/interface control state: MM indirect access disable/write-disable, bus coherency and traffic-class policy, reset enables, config-register selection, interrupt handler controls, CLKREQB pad bits, feature-control bits for BIF request/completion paths, HDP outstanding/atomic limits, doorbell controls and interrupt status/clear/disable bits, framebuffer read/write enables, RAS vector selection, master/slave transaction pending masks, BACO entry/exit control and timers, memory-type control, NBIF GFX address LUT entries 0-15, HDP flush remap addresses, BIF ring-buffer control/base/pointers/writeback address, mailbox index, MP1 BACO exit interrupt, and pad-control aggregates for PERSTB/PX_EN/REFPADKIN/CLKREQB/PWRBRK.

The RCC device block defines higher-level root-complex/device controls: invalid SR-IOV register-access interrupts, BACO request-disable bits, doorbell aperture reset enable, VDM support flags, PCIe margining parameters, GPU IOV region/host-VM enables, console IOV mode and VF layout, peer register ranges, PMI and poisoned-completion policy, bridge/config aperture sizes, XDMA aperture bounds, feature controls for ATC/PASID/Page Request/invalid completion handling, bus/dev/function number lists and autoupdate, host bus capture, peer framebuffer offsets, link-down entry/exit controls, common LTR/PM link controls, endpoint requester-ID restore, LTR latency, and MH arbitration policy.

The endpoint-function MSI-X block defines four GFX MSI-X vectors: address low/high, message data, per-vector mask bit, and a four-bit pending-bit array. These constants are used when programming or inspecting hardware-backed MSI-X table/PBA state for EPF0.

The RCC strap block is dense configuration-strap metadata. It covers global BIF straps for link generation disable/kill through Gen5, ROM/VGA/memory aperture defaults, error-ignore behavior, margining, ASPM/LTR, GSI/SMN behavior, power-break handling, and protocol capability flags. It also covers downstream port straps for device/vendor/subsystem IDs, ARI/ACS/AER/atomic/VC/DLF/TPH/DOE/CTO capabilities, payload/link-width/link-speed support, equalization presets for 16 GT/s and 32 GT/s, power budget tables, alternate protocol fields, reset timing, port/bus/device/function identity, and root/endpoint revision metadata. EPF0 and EPF1 strap definitions include function enable, legacy type, D1/D2/PME/AUX power, SR-IOV, VF device ID and total VFs, supported page size, PASID/ATS/Page Request, MSI/MSI-X, resizable BAR, doorbell/memory/register/ROM aperture sizes, VF aperture sizes, GPUIOV VSEC revision, FLR/reset/D3hot timing, and function class/vendor/subsystem IDs.

The PF BIFPFVF block defines runtime status and per-PF facilities: DMA-on-BME-low status/clear, unsupported atomic operation error logging/clear bits, self-ring doorbell GPA aperture base/control, HDP register/memory flush and invalidate trigger registers, GPU HDP flush request/done bits for CP0-CP9 and SDMA0-SDMA1 plus reserved engine lanes, master/slave transaction pending bits, GFX address LUT bypass, mailbox transmit/receive data words and control/interrupt bits, VM/hypervisor mailbox data/valid/ack fields, and compute/memory partition capability/status fields for SPX/DPX/TPX/QPX/CPX and NPS modes.

The EPF0 PF/VF decode mini-block defines endpoint-function runtime state for invalid SR-IOV register access and doorbell read access logging, doorbell aperture enable, config memory size/reserved fields, and an IOV function identifier with enable bit.

The final partial GDC block begins AXI-to-SDP/GDC steering and response mapping definitions. It includes `GDC0_A2S_CNTL_CL0/CL1`, `GDC0_A2S_CNTL3_CL0/CL1`, and `GDC0_A2S_CNTL_SW0/SW1`, then starts `GDC0_A2S_CNTL_SW2`. These fields map snoop/passpw/block/data-error/EXOKAY/response behavior, read-response error modes, static VC selection, write steering/tagging, response reorder, chain disable behavior, and WRR read/write weights.

## Important APIs, Types, and Macros

There are no callable APIs in this file. The important exported interface is the macro naming contract:

- `REGISTER__FIELD__SHIFT` is the low bit of a field.
- `REGISTER__FIELD_MASK` is the raw mask for that field in a register value.
- Most masks are 32-bit constants with an `L` suffix; narrow fields may use masks such as `0xFFL`, `0xFFFFL`, or `0x001FL`.

These constants are consumed by AMDGPU/SOC15 helper macros and register accessors, commonly including patterns such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and field-write helpers. The register address definitions are expected to come from the matching `nbio_7_9_0_d.h` header. The combination lets driver code name hardware fields symbolically while the preprocessor expands the field's shift and mask.

The repeated register families have predictable structure that driver code may rely on:

- Scratch and mailbox data registers are generally whole-register 32-bit fields.
- Status/control pairs often place status bits in low positions and clear bits around bit 16 or higher, for example BIF doorbell interrupt clear fields and atomic error clear fields.
- Address low fields often start at bit 2 and mask off natural alignment bits, for example MSI-X low addresses, ring writeback low addresses, and HDP remap addresses.
- Capability/strap registers encode many one-bit feature flags with multi-bit values for payload size, PM support, aperture size, PASID width, link speed, equalization preset, and timing values.

## Control Flow and Data Flow

This chunk implements no control flow directly. Runtime behavior is created at macro expansion sites elsewhere in the driver:

1. Driver code selects an NBIO/BIF/RCC/GDC register address from the companion address header.
2. The driver reads a register, extracts a field with the `__SHIFT`/`_MASK` pair, or builds a new value by clearing a mask and shifting a field value into position.
3. Writes to control fields alter hardware behavior immediately within the register's power/reset domain.
4. Reads of status fields observe hardware, firmware, PCIe core, or GPU engine state that may change asynchronously.
5. Clear fields and write-one-to-clear style fields are used by driver interrupt/error handling paths to acknowledge hardware events.

Representative data-flow surfaces in this chunk include:

- BIOS/SBIOS/driver/firmware scratch registers carrying boot or handoff data across firmware and driver phases.
- Doorbell configuration flowing from aperture base/size/mode/enables into GPU queue notification behavior.
- HDP flush request bits flowing from software or GPU clients to flush completion status bits.
- Mailbox transmit/receive words and valid/ack bits carrying PF/VF or host/firmware messages.
- PCIe strap fields seeding exposed PCIe capability/configuration state before software enumerates or tunes the device.
- Link, margining, AER, DPC-adjacent, and LTR fields feeding PCIe diagnostics and power-management policy.

## State and Persistence

The macros themselves are compile-time constants and have no state. The state represented by the constants lives in hardware registers:

- Scratch registers can preserve firmware/driver handoff values until reset or explicit overwrite.
- Status/log registers such as PCIe interrupt status, AER timer-expired bits, atomic error logs, DMA-on-BME-low status, invalid SR-IOV access status, and HDP flush done bits persist according to hardware clear semantics.
- Strap registers represent latched fuse/ROM/pin/default configuration and should be treated as hardware capability/default state, not as proof that a feature is usable without checking the actual device context.
- Control registers for doorbells, BACO, ring buffers, address LUTs, peer mappings, console IOV, host VM, mailbox, HDP flush, and GDC steering persist only within their hardware power/reset domains.
- Partition capability/status fields expose hardware partition modes such as SPX/DPX/TPX/QPX/CPX and NPS modes; changing or interpreting these fields must align with platform partitioning policy and reset sequencing.

Because many fields are low-level hardware controls, an incorrect constant changes the meaning of every call site that uses it. There is no runtime validation layer inside this header.

## Dependencies and Integration Points

This file is generated AMDGPU hardware-description data under `drivers/gpu/drm/amd/include/asic_reg/nbio`. Its main dependencies are:

- The matching NBIO 7.9.0 register-address header for offsets and address-space selection.
- AMDGPU SOC15 register access infrastructure and bitfield helper macros.
- PCI/PCIe core concepts for config space, capabilities, MSI-X, AER-style error reporting, FLR, ATS/PASID/Page Request, SR-IOV, ARI, ACS, LTR, ASPM, PM states, payload/read-request sizing, link speed/width/equalization, and root/endpoint behavior.
- AMDGPU subsystems that program NBIO, doorbells, HDP flushes, RAS/error routing, BACO/power management, virtualization, partitioning, and mailbox paths.
- Firmware/BIOS/strap initialization that determines the initial values read from many of these registers.

Important integration points visible from the field names:

- Doorbell and HDP flush fields connect NBIO/BIF register programming to queue notification and CPU/GPU memory coherency.
- Ring-buffer and mailbox fields connect BIF to interrupt/message transport paths.
- SR-IOV, PF/VF, IOV function identifiers, VF aperture sizes, and console IOV fields connect this header to virtualization and mediated partition workflows.
- PCIe link, strap, error, and margining fields connect to link training, power-management, and diagnostics paths.
- Partition compute/memory capability fields connect to GPU partition mode discovery and management.
- GDC A2S fields connect request/response mapping and virtual-channel steering to fabric behavior.

## Risks and Edge Cases

- Generated mask/shift drift from the hardware spec would silently corrupt register field extraction or writes. High-risk fields include doorbell aperture sizes/bases, HDP flush request/done bits, BIF ring-buffer pointers, BACO controls/timers, SR-IOV enables, peer mappings, and GDC steering values.
- Status and clear bits are often adjacent but semantically different. For example, BME and atomic error status bits live in low positions while clear bits live at bit 16 and above. Treating clear bits as ordinary state can lose diagnostics or leave interrupts stuck.
- Repeated fields invite lane/function/vector copy errors. MSI-X vectors 0-3, GFX address LUT entries 0-15, DPA substate allocations 0-7, CP/SDMA HDP flush bits, peer offsets 0-3, and EPF0/EPF1 straps all need exact indexing.
- Strap definitions describe hardware-default/capability inputs, not necessarily mutable runtime controls. Driver code must not assume a feature exists merely because this header defines a mask for it.
- Many PCIe error-ignore and unsupported-request controls can mask real platform errors. Enabling them without ASIC-specific rationale may hide AER, PASID, TPH, prefix, or completion-timeout failures.
- Doorbell and HDP coherency fields are security and correctness sensitive under SR-IOV. Incorrect aperture, translation, or VF protection settings can expose host/guest memory or break queue signaling.
- Bus number, dev/function list, peer framebuffer offset, and XDMA aperture fields affect routing. Bad programming can misroute PCIe transactions or peer accesses.
- The chunk ends in the middle of the GDC block at `GDC0_A2S_CNTL_SW2`; later merge work must combine this with the next chunk before making whole-file conclusions about GDC coverage.

## Test and Validation Signals

This header has no standalone unit tests; validation is mostly compile-time and hardware-integration based. Useful signals include:

- Successful AMDGPU build for ASICs that include NBIO 7.9.0, proving all macro names referenced by code expand.
- Boot/probe logs showing NBIO initialization succeeds without register access faults, PCIe enumeration errors, or invalid SR-IOV access events.
- PCIe capability and status checks through `lspci -vv`, debugfs, or driver logs for link speed/width, AER, ACS, ATS/PASID, SR-IOV, MSI-X, LTR, and PM capability state matching expected hardware straps.
- Doorbell tests where queues submit and signal correctly for PF and VF contexts, with no unexpected doorbell read/access errors.
- HDP flush paths where CP/SDMA clients request flushes and observe matching done bits without timeout.
- RAS/error-injection or stress logs confirming atomic error, invalid register access, doorbell, AER-like, and mailbox interrupt/status clear flows behave as expected.
- BACO suspend/resume or runtime power-management tests proving BACO control and exit timer fields do not regress device wake and reinitialization.
- SR-IOV validation with VF enable/disable, VF FLR, VF BAR/aperture sizing, PASID/ATS/Page Request, and mailbox traffic.
- Partition-mode discovery tests verifying compute and memory partition capability/status fields match platform configuration.
- GDC/fabric traffic stress that exercises response mapping, VC steering, write tags, chain controls, and WRR read/write weights after the full GDC register block is reconciled.
