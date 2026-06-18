# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003327`: lines 1-2525, `Docs/researches/chunks/subset-b-003327_research.md`
- `subset-b-003328`: lines 2526-4978, `Docs/researches/chunks/subset-b-003328_research.md`
- `subset-b-003329`: lines 4979-7452, `Docs/researches/chunks/subset-b-003329_research.md`
- `subset-b-003330`: lines 7453-9894, `Docs/researches/chunks/subset-b-003330_research.md`
- `subset-b-003331`: lines 9895-12283, `Docs/researches/chunks/subset-b-003331_research.md`
- `subset-b-003332`: lines 12284-15100, `Docs/researches/chunks/subset-b-003332_research.md`
- `subset-b-003333`: lines 15101-17790, `Docs/researches/chunks/subset-b-003333_research.md`
- `subset-b-003334`: lines 17791-20320, `Docs/researches/chunks/subset-b-003334_research.md`
- `subset-b-003335`: lines 20321-22702, `Docs/researches/chunks/subset-b-003335_research.md`
- `subset-b-003336`: lines 22703-25135, `Docs/researches/chunks/subset-b-003336_research.md`
- `subset-b-003337`: lines 25136-27410, `Docs/researches/chunks/subset-b-003337_research.md`
- `subset-b-003338`: lines 27411-29891, `Docs/researches/chunks/subset-b-003338_research.md`
- `subset-b-003339`: lines 29892-32328, `Docs/researches/chunks/subset-b-003339_research.md`
- `subset-b-003340`: lines 32329-34751, `Docs/researches/chunks/subset-b-003340_research.md`
- `subset-b-003341`: lines 34752-37218, `Docs/researches/chunks/subset-b-003341_research.md`
- `subset-b-003342`: lines 37219-38900, `Docs/researches/chunks/subset-b-003342_research.md`

## Chunk Research

### subset-b-003327: lines 1-2525

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

### subset-b-003328: lines 2526-4978

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_sh_mask.h lines 2526-4978

## Scope

This chunk covers lines 2526-4978 of AMDGPU's generated NBIO 7.9.0 shift/mask header. It contains 2,127 preprocessor `#define` entries: 1,063 `__SHIFT` constants and 1,064 `_MASK` constants. There are no C functions, structs, enums, global variables, allocation paths, locks, direct register reads/writes, or persistent software data structures in this range.

The range starts inside `GDC0_A2S_CNTL_SW2`, after its first `STATIC_VC_ENABLE` and `STATIC_VC_VALUE` shift definitions were emitted in the previous chunk. It then covers GDC0 AXI/SDP arbitration, tag allocation, SHUB protection, NGDC clock/power gating, GFX doorbell status, ATDMA arbitration, and S2A controls. At line 2673 it switches to `addressBlock: aid_nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp`, a PCIe endpoint-function 0 configuration-space field map for `BIF_CFG_DEV0_EPF0`. The chunk runs through standard PCI header fields, PM, PCIe, MSI/MSI-X, vendor-specific, virtual-channel, serial-number, AER, BAR, power, DPA, secondary PCIe, per-lane equalization, ACS, ATS, PRI/page request, PASID, multicast, LTR, ARI, SR-IOV, data-link, 16 GT/s/32 GT/s PHY/equalization, lane margining, and GPUIOV vendor-specific virtualization fields. It ends inside `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_UVD0SCH_DW3`, with only the `DW3` shift present; the `DW3` mask and following scheduler fields continue in the next chunk.

Although this file sits under a local `ceph-client` source mirror, the content is AMD GPU NBIO/PCIe register metadata. It does not implement Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_9_0_sh_mask.h` is the generated bitfield companion for NBIO 7.9.0 register and PCIe configuration-space offsets. Each macro encodes one of two pieces of field geometry:

- `REGISTER__FIELD__SHIFT`: least-significant bit position of a field.
- `REGISTER__FIELD_MASK`: bit mask of that field in the containing register.

Driver code combines these names with matching offsets from `nbio_7_9_0_offset.h` and AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and `SOC15_REG_OFFSET`. The goal is to keep NBIO, PCIe, interrupt, power-management, error-reporting, and virtualization programming symbolic instead of hard-coding bit numbers.

## Important Definitions

The opening GDC0/NGDC portion describes internal NBIO fabric behavior:

- `GDC0_A2S_CNTL_SW2`, `GDC0_A2S_TAG_ALLOC_0`, `GDC0_A2S_TAG_ALLOC_1`, and `GDC0_A2S_MISC_CNTL` expose virtual-channel selection, response reorder controls, SDP write chaining, weighted read/write arbitration, per-VC tag allocation, tag FIFO behavior, and minimum read/write tag set sizes.
- `GDC0_SHUB_REGS_IF_CTL` controls SHUB register request protection, including non-PF request handling and VF protection disablement.
- `GDC0_NGDC_MGCG_CTRL`, `GDC0_NGDC_PG_MISC_CTRL`, `GDC0_NGDC_PGMST_CTRL`, and `GDC0_NGDC_PGSLV_CTRL` define medium-grain clock gating, SRAM fine-grain clock gating, endpoint D3-only power gating policy, clock permissions, power-gating hysteresis, idleness-count enables, firmware power-gating exits, and per-clock idle hysteresis.
- `GDC0_NBIF_GFX_DOORBELL_STATUS` exposes the 16-bit GFX doorbell-sent status bitmap.
- `GDC0_ATDMA_MISC_CNTL` and `GDC0_S2A_MISC_CNTL` cover ATDMA/S2A arbitration modes, virtual-channel weights, host completion behavior, HDP performance enhancement disablement, and write-response arbitration.

The `BIF_CFG_DEV0_EPF0` address block maps the physical endpoint-function PCI configuration image:

- Conventional PCI header fields include vendor/device ID, command/status, revision/class code, cache line, latency, header type, BIST, BAR1-BAR6, CardBus CIS pointer, subsystem adapter IDs, ROM BAR, capability pointer, interrupt line/pin, min grant, max latency, and vendor capability list fields.
- PM capability fields include capability IDs and next pointers, version, PME clock/support, D1/D2 support, auxiliary current, power state, PME enable/status, data select/scale, bus-power enable, and PMI data.
- PCIe capability fields include device type, device capability/control/status, link capability/control/status, Device/Link Capability 2, Device/Link Control 2 including `LTR_EN`, OBFF, atomic op, ARI forwarding, IDO, ten-bit tag, and end-to-end TLP prefix controls, plus Link Status 2 equalization, retimer, crosslink, downstream-component, and DRS status.
- MSI and MSI-X fields define capability lists, enable bits, multi-message capability/enable, 64-bit addressing, per-vector masking, extended message data, message address/data, masks, pending bits, table/PBA BIRs, table offsets, function mask, and MSI-X enable.
- Vendor-specific and virtual-channel fields include VSEC headers, scratch dwords, VC enhanced capability, port VC capability/control/status, and VC0/VC1 resource capability/control/status for TC/VC mapping and arbitration.
- Serial number and AER fields include device serial dwords, uncorrectable/correctable error status, masks, severity, ECRC capability/enable bits, first-error pointer, multi-header support, TLP prefix log presence, header logs, and TLP prefix logs.
- Extended endpoint capability families include resizable/enhanced BAR controls for BAR1-BAR6, power budget data/select/capability, dynamic power allocation capability/status/control and per-substate power allocation, secondary PCIe Link Control 3, lane error status, and lane 0-15 equalization controls.
- Isolation and address-translation families include ACS capability/control, ATS capability/control, page request interface control/status/capacity/allocation, PASID capability/control, multicast capability/control/address/receive/blocking fields, LTR capability, and ARI capability/control.
- SR-IOV fields include capability/control/status, initial/total/current VF counts, function dependency link, first VF offset, VF stride, VF device ID, supported/system page sizes, VF BARs 0-5, and VF migration-state array offset.
- High-speed link and diagnostic fields include Data Link Feature capability/status, 16 GT/s link capability/control/status, 16 GT/s parity mismatch status and per-lane equalization controls, lane margining capability/status and per-lane control/status for lanes 0-15, and 32 GT/s link capability/control/status.

The closing GPUIOV vendor-specific capability is AMD virtualization metadata:

- `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST_GPUIOV` and `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV` define the GPUIOV extended-capability and VSEC headers.
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_INTR_ENABLE`, `INTR_STATUS`, and `RESET_CONTROL` define hypervisor/VF mailbox interrupt enable/status bits and a soft PF FLR bit.
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_HVVM_MBOX_DW0` selects a VF and carries small transmit/receive message payloads, valid, and acknowledgement bits.
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_HVVM_MBOX_DW1` maps transmit-acknowledge and receive-valid bits for VF0-VF15.
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_HVVM_MBOX_DW2` maps the same mailbox state for VF16-VF30 and PF.
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_CONTEXT`, `TOTAL_FB`, `REGION`, `P2P_OVER_XGMI_ENABLE`, and `VF0_FB` through `VF30_FB` describe virtualization context placement, total/used framebuffer accounting, region ID, peer-over-XGMI enablement, and per-VF framebuffer size/offset.
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_OFFSETS` through `OFFSETS4` provide scheduler metadata offsets for VCN0-VCN11 and GFX0-GFX7.
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_UVD0SCH_DW0` through the start of `UVD0SCH_DW3` expose full-width scheduler data words; the last register is split by the chunk boundary.

## APIs, Types, And Functions

There are no callable APIs, C types, or functions in this chunk. The exported interface is the generated macro namespace. The macros are meaningful only when paired with the correct NBIO 7.9.0 address metadata and with the access path expected by the register family:

- GDC0/NGDC names pair with `regGDC0_*` offsets and SOC15/NBIO register access.
- `BIF_CFG_DEV0_EPF0_*` names pair with endpoint-function config-space offsets such as `cfgBIF_CFG_DEV0_EPF0_*` in `nbio_7_9_0_offset.h`.
- GPUIOV names pair with the GPUIOV capability offsets in the same endpoint config-space image.

The macros encode field positions and masks only. They do not encode reset values, access permissions, side effects, write-one-to-clear behavior, firmware ownership, or required register ordering.

## Control Flow

This header has no local runtime control flow. Runtime use is external and normally follows this pattern:

1. AMDGPU selects the NBIO 7.9.0 register offset or PCIe config offset matching the active ASIC/IP version.
2. It reads the register through the proper SOC15, PCIe, or SMN/MMIO helper.
3. It extracts a field with the generated mask and shift, or composes a read-modify-write value using the field macros while preserving unrelated bits.
4. Hardware applies the semantics: arbitration, tag allocation, clock/power gating, doorbell-status reporting, endpoint enumeration, interrupt routing, PCIe link training, power-management transitions, AER reporting, isolation/translation policy, SR-IOV/GPUIOV virtualization state, or scheduler metadata exchange.

The order in the file follows the generated register database, not an execution sequence. Repeated status, mask, severity, and control register families often share bit positions while representing different operations.

## State And Persistence Behavior

The chunk owns no software state and persists nothing. All state named here lives in NBIO hardware registers or in hardware-backed PCIe configuration-space/capability images.

Represented state includes:

- Fabric configuration: GDC0 virtual-channel selection, tag allocations, arbitration weights, response ordering, SHUB VF protection, ATDMA/S2A routing, and doorbell status.
- Clock and power controls: NGDC medium-grain clock gating, SRAM fine-grain gating, endpoint D3-only behavior, power-gating hysteresis, idle-count policies, and firmware exit controls.
- PCI configuration state: command bits, BAR decode, interrupt disable, PM state, PME enable/status, MSI/MSI-X programming, link controls, payload/read-request sizing, LTR enablement, OBFF, ARI forwarding, atomic/IDO controls, ACS/ATS/PASID/PRI controls, multicast controls, SR-IOV controls, and GPUIOV mailbox/framebuffer allocation.
- Capability and diagnostic state: PCI/PCIe identity, capability-chain headers, link capabilities/status, AER status/masks/severity/logs, lane/equalization/margining status, data-link feature status, 16 GT/s and 32 GT/s status, and GPUIOV mailbox valid/ack state.

Persistence is determined by PCIe reset rules, GPU/NBIO reset domains, function-level reset, SR-IOV VF lifecycle, suspend/resume restore, runtime power transitions, firmware initialization, and explicit driver writes. Callers must know from the hardware specification which fields are read-only, sticky, write-one-to-clear, reserved, firmware-owned, or safe for read-modify-write.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 7.9.0 offset header staying synchronized with the mask header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_offset.h` supplies matching `regGDC0_*` offsets and `cfgBIF_CFG_DEV0_EPF0_*` config-space offsets.

No `nbio_7_9_0_default.h` file is present in this source tree, so reset/default information is not available from a sibling generated default header here.

Integration points are AMDGPU NBIO and PCIe platform behavior: GPU enumeration, BAR/resource setup, interrupt setup, ASPM/LTR policy, power management, suspend/resume, GPU reset recovery, AER logging and clearing, PCIe link diagnostics, ACS/IOMMU isolation, ATS/PASID/PRI address translation, SR-IOV VF creation and BAR assignment, GPUIOV mailbox handling, framebuffer partitioning, VCN/GFX scheduler metadata, and debug register dumps. Older NBIO implementations in this tree use the same semantic families, for example NBIO code programs `BIF_CFG_DEV0_EPF0_DEVICE_CNTL2__LTR_EN_MASK` when enabling or disabling LTR on related generations.

## Risks And Edge Cases

- The chunk starts mid-`GDC0_A2S_CNTL_SW2`; the first two shift definitions for that register are outside this work item. It ends mid-`PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_UVD0SCH_DW3`; the mask for `DW3` is outside this work item. Merge/reconciliation must combine adjacent chunks before making whole-register conclusions.
- Shift/mask mistakes compile cleanly but can read or write adjacent bits, corrupting PCI command state, BAR sizing, interrupt configuration, link controls, AER policy, SR-IOV state, or GPUIOV mailbox/framebuffer metadata.
- Status, mask, severity, and control registers intentionally reuse similar field names. Copying a field between `*_STATUS`, `*_MASK`, and `*_SEVERITY` groups can change clearing behavior, reporting policy, or fatal/nonfatal classification.
- AER, PCI status, device status, link status, lane status, margining status, and GPUIOV interrupt status may be sticky or write-one-to-clear. Generic read-modify-write code can accidentally clear diagnostics if it writes a status register without W1C-aware handling.
- Reserved fields are present, including full-register reserved masks. Writers should preserve reserved bits unless hardware documentation explicitly says otherwise.
- GDC0 arbitration, tag, and VC controls are performance and forward-progress sensitive. Incorrect tag allocation or weighting can cause starvation, reduced throughput, or ordering issues under load.
- SHUB VF protection, ACS, ATS, PASID, PRI, SR-IOV, GPUIOV, and VF framebuffer allocation fields are virtualization-sensitive. Misprogramming can break isolation, expose PF/VF state incorrectly, or invalidate VFIO/IOMMU assumptions.
- Link retraining, compliance, equalization, 16 GT/s/32 GT/s, and lane margining fields are operationally sensitive. Changing them on an active link can destabilize PCIe connectivity or produce misleading diagnostics.
- Similar names exist across NBIO generations and endpoint/function/VF namespaces. Code must include the header matching the active IP version and pair a mask with the correct `reg*` or `cfg*` offset.

## Test Signals

- Build AMDGPU configurations that include NBIO 7.9.0 support. Compile failures catch missing or malformed symbols and mismatches between generated headers and driver users.
- Run generated-header consistency checks against the authoritative NBIO 7.9.0 register database: every field in this chunk should have the expected shift and mask, every register family should have a matching offset in `nbio_7_9_0_offset.h`, and chunk-boundary split fields should reconcile cleanly with neighboring chunks.
- Validate PCIe enumeration on matching hardware with `lspci -vv`: vendor/device/class IDs, BARs, capability pointers, PM/PCIe/MSI/MSI-X/VSEC/VC/AER/ACS/ATS/PASID/ARI/SR-IOV/Data Link/16 GT/s/32 GT/s/GPUIOV capabilities, and link capability/status should decode coherently.
- Exercise interrupt setup and teardown: MSI/MSI-X enable bits, table/PBA BAR indicators, pending/mask bits, and GPUIOV mailbox interrupt status should behave as expected.
- Exercise ASPM/LTR and runtime power-management paths, including suspend/resume and GPU reset recovery, to confirm PM state, `LTR_EN`, NGDC clock/power gating controls, and restored configuration state remain consistent.
- Exercise PCIe AER and link diagnostics where hardware and platform support it: correctable/uncorrectable status, masks, severity, ECRC controls, header/TLP prefix logs, lane error status, equalization status, margining status, and 16 GT/s/32 GT/s link status should match platform observations.
- Validate SR-IOV/GPUIOV workflows on capable hardware: VF counts, VF BARs, page sizes, first VF offset/stride, mailbox valid/ack bits, PF/VF reset behavior, per-VF framebuffer size/offset, and VCN/GFX scheduler offsets should match the hypervisor or firmware contract.
- Compare this NBIO 7.9.0 layout with neighboring generation headers before sharing code across generations; fields with the same semantic name may live at different offsets or have different reserved bits.

## Boundary Notes

- Line 2526 begins after the `GDC0_A2S_CNTL_SW2__STATIC_VC_ENABLE__SHIFT` and `STATIC_VC_VALUE__SHIFT` definitions. This chunk contains the remaining shifts and all masks for that register family.
- Line 4978 contains only `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_UVD0SCH_DW3__DW3__SHIFT`; its `_MASK` definition is expected in the following chunk.

### subset-b-003329: lines 4979-7452

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_sh_mask.h lines 4979-7452

## Scope

This chunk is a generated AMD NBIO 7.9.0 shift/mask header segment. It contains C preprocessor constants only: 2,108 `#define` entries, split into 1,054 `__SHIFT` constants and 1,054 `_MASK` constants. The equal count hides two chunk-boundary partials: the range starts with only the mask for `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_UVD0SCH_DW3`, whose shift is in the previous chunk, and ends with only the shift for `BIF_CFG_DEV0_RC0_MSI_MSG_ADDR_LO`, whose mask is in the next chunk.

The covered source belongs to AMDGPU's generated `drivers/gpu/drm/amd/include/asic_reg/nbio` register database. It has no Ceph or distributed-filesystem logic despite the source tree prefix. It also has no executable code, structs, enums, callbacks, locks, or allocation paths.

The range covers three main areas:

- The tail of the GPU IOV vendor-specific PCIe capability area for `DEV0_EPF0`, especially schedule dwords for UVD/VCN and GFX engines plus GPU IOV engine interrupt enable/status bitmaps.
- The complete visible `aid_nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` address block for `BIF_CFG_DEV0_EPF1`, from standard PCI config identity fields through ARI capability fields.
- The beginning and most of the PCIe capability area for `aid_nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp`, `BIF_CFG_DEV0_RC0`, from root-complex standard PCI bridge fields through the first MSI address-low shift.

## Purpose

The purpose of this header chunk is to define bit positions and masks for NBIO/BIF PCI configuration-space and GPU IOV vendor-specific registers on AMD ASICs using NBIO 7.9.0. The naming convention is consistent throughout the file:

- `<REGISTER>__<FIELD>__SHIFT` is the zero-based bit position of a field.
- `<REGISTER>__<FIELD>_MASK` is the already-shifted field mask used for extraction, tests, and read-modify-write updates.

The companion `nbio_7_9_0_offset.h` supplies the register addresses and base indices. For example, that file maps the GPU IOV schedule and interrupt registers under `regBIF_CFG_DEV0_EPF0_0_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_*` with base index 8, maps `cfgPCIE_VENDOR_SPECIFIC_HDR_GPUIOV_*` config-space offsets such as UVD/GFX schedule dwords and engine interrupt status/enable dwords, and maps the `BIF_CFG_DEV0_EPF1` and `BIF_CFG_DEV0_RC0` PCI configuration registers. This chunk supplies the field geometry for those addresses.

Runtime code does not call this header directly. AMDGPU code includes it from `amdgpu/nbio_v7_9.c` and `ras/ras_mgr/amdgpu_ras_nbio_v7_9.c` together with the offset header. Register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `WREG32_FIELD15_PREREG`, and PCIe index/data accessors consume these generated constants.

## Important Macro Families

### GPU IOV Schedule Dwords

The chunk begins inside `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_UVD0SCH_DW3` and continues through UVD/VCN schedule dwords for `UVD0SCH` through `UVD11SCH`. Each schedule entry has dwords `DW0` through `DW8`; each dword field is represented as a full 32-bit value at shift 0 with mask `0xFFFFFFFFL`.

The same schedule shape then appears for graphics engines `GFX0SCH` through `GFX7SCH`, again with `DW0` through `DW8` full-dword fields. These definitions are opaque layout constants for AMD's GPU IOV vendor-specific PCIe capability. They do not interpret the schedule payload; they only state that each dword occupies the full register.

The preceding chunk defines the offset summary registers (`PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_OFFSETS*`) and the first UVD0 schedule dwords. The matching offsets in `nbio_7_9_0_offset.h` show the schedule register sequence in config space and in generated `regBIF_CFG_DEV0_EPF0_0_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_*` macros.

### GPU IOV Engine Interrupt Enable and Status

After the schedule dwords, the chunk defines GPU IOV engine interrupt bitmaps:

- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_ENGA_A0_7_INTR_ENABLE`
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_ENGB_B0_7_INTR_ENABLE`
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_ENGB_B8_15_INTR_ENABLE`
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_ENGA_A0_7_INTR_STATUS`
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_ENGB_B0_7_INTR_STATUS`
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_ENGB_B8_15_INTR_STATUS`

For each engine slot, four interrupt classes repeat in adjacent bits: command complete, hang self recovered, hang needs FLR, and VM busy transition. The `A0_7` and `B0_7` registers use all 32 bits for eight engines times four events. The `B8_15` status/enable registers in this chunk define engines B8 through B11, using bits 0 through 15. Comments for `ENGA_A8_15_INTR_ENABLE` and `ENGA_A8_15_INTR_STATUS` appear without field definitions in this chunk, so those register blocks are empty in the generated range.

These fields are virtualization and recovery oriented. They describe how GPU IOV exposes per-engine completion, hang, FLR-needed, and VM-busy-transition events to the PCIe vendor-specific capability image. They are not Linux interrupt handlers by themselves.

### DEV0 EPF1 Standard PCI Header

The `BIF_CFG_DEV0_EPF1` block starts with ordinary PCI config header fields:

- Identity and class fields: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS`.
- Command and status registers: I/O access, memory access, bus mastering, special cycles, memory-write-invalidate, parity response, SERR, interrupt disable, immediate readiness, interrupt status, capability-list presence, fast back-to-back support, DEVSEL timing, target/master abort, system error, and parity error bits.
- Header/control fields: cache line, latency, header type, BIST, six BARs, CardBus CIS pointer, adapter/subsystem ID, ROM BAR, capability pointer, interrupt line/pin, minimum grant, maximum latency, and vendor capability/adapter write fields.

These are PCI configuration-image fields for endpoint function 1. Firmware, PCI core enumeration, and device reset state normally own much of this surface. AMDGPU code using these masks must pair them with the `BIF_CFG_DEV0_EPF1` offsets, not with the visually similar root-complex or endpoint-function-zero registers.

### DEV0 EPF1 Power, PCIe, Link, and MSI Capabilities

The endpoint function 1 section includes PCI PM capability fields:

- `PMI_CAP_LIST` and `PMI_CAP` for capability ID, next pointer, version, PME clock, immediate readiness on return to D0, D1/D2 support, PME support, and auxiliary-current fields.
- `PMI_STATUS_CNTL` for power state, no-soft-reset, PME enable/status, bridge-extension bits, data select/scale, and PM data.

It also defines PCIe capability fields:

- `PCIE_CAP_LIST` and `PCIE_CAP` for capability ID, next pointer, PCIe capability version, device/port type, slot implemented, and interrupt message number.
- `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` for payload size, phantom functions, extended tags, acceptable L0s/L1 latency, role-based error reporting, captured slot power, FLR capability/initiation, error-reporting enables, relaxed ordering, no-snoop, max read request size, aux power, transactions pending, and emergency power reduction status.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` for speed/width, ASPM support/control, exit latencies, clock power management, surprise-down reporting, data-link active reporting, link bandwidth notification, link disable/retrain, common clock, extended sync, autonomous width disable, bandwidth interrupt enables, DRS signaling, current speed, negotiated width, link training, slot clock, and link active/status bits.
- `DEVICE_CAP2`, `DEVICE_CNTL2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` for completion timeout, ARI, atomic ops, ID-based ordering, LTR, OBFF, 10-bit tags, end-to-end TLP prefixes, emergency power reduction, FRS/DRS, Gen3 equalization state, crosslink state, RTM presence, and downstream component presence.

The MSI/MSI-X section defines capability headers, MSI message control, 32-bit and 64-bit message address/data registers, extended message data, MSI mask and pending registers, MSI-X message control, table BIR/offset, and PBA BIR/offset. These are bit layouts only; interrupt allocation, vector ownership, MSI remapping, and table lifetime are managed by PCI and AMDGPU interrupt code.

### DEV0 EPF1 Extended Capabilities

The `BIF_CFG_DEV0_EPF1` block continues through several PCIe extended capability families:

- Vendor-specific enhanced capability: `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, and scratch payload dwords.
- Advanced Error Reporting: uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, TLP header logs, and TLP prefix logs.
- BAR enhanced capability: BAR1 through BAR6 capability/control definitions for fixed-size support, size capability, selected size, BAR index, number of BARs, and atomic operation routing/blocking support.
- Power budget and DPA: power budget selectors/data/capability, DPA latency indicator, status/control, and substate power allocation 0 through 7.
- ACS, PASID, and ARI: source validation, translation blocking, peer-to-peer request/completion redirect, upstream forwarding, egress control, direct translated P2P, PASID execution/privileged mode, max PASID width, PASID enable bits, ARI next function/function group, and ACS function group controls.

These fields are especially relevant to virtualization, IOMMU isolation, peer-to-peer routing, PCIe error reporting, power management, and BAR sizing. The masks do not encode policy or legal value transitions.

### DEV0 RC0 Root Complex and Bridge Fields

The final part of the chunk starts the `BIF_CFG_DEV0_RC0` root-complex block. It includes standard bridge-style PCI fields:

- Root-complex identity, class, revision, header, BIST, BARs, primary/secondary/subordinate bus numbers, secondary latency timer, I/O base/limit, memory base/limit, prefetchable base/limit and upper halves, I/O base/limit high, capability pointer, ROM BAR, interrupt line/pin, bridge control, and extended bridge control.
- PM capability and PCIe capability fields analogous to the endpoint block where applicable.
- Root port specific slot and root fields: `SLOT_CAP`, `SLOT_CNTL`, `SLOT_STATUS`, `ROOT_CNTL`, `ROOT_CAP`, and `ROOT_STATUS`.
- Root-side device/link capability/control/status 1 and 2 fields.
- The start of root-complex MSI capability fields through `BIF_CFG_DEV0_RC0_MSI_MSG_ADDR_LO__MSI_MSG_ADDR_LO__SHIFT`.

The next chunk continues the `RC0` MSI address-low mask and later root-complex capability definitions. This chunk therefore should not be treated as a complete final description of `BIF_CFG_DEV0_RC0`.

## Control Flow and Runtime Behavior

There is no control flow in this header. It is compile-time data used to produce constants in AMDGPU code. Runtime behavior appears when other code:

1. Selects NBIO 7.9.0 support for the ASIC and includes `nbio_7_9_0_offset.h` plus this shift/mask header.
2. Computes an MMIO or PCI configuration register address using generated offset macros and SOC15/NBIO helper functions.
3. Uses a field macro pair through `REG_SET_FIELD`, `REG_GET_FIELD`, direct mask tests, or read-modify-write helpers.
4. Reads or writes hardware-owned state such as GPU IOV interrupt status, PCIe link controls, AER status, MSI/MSI-X state, BAR capability values, ACS/PASID/ARI controls, or root port status.

The local `nbio_v7_9.c` integration demonstrates this pattern through NBIO init, doorbell range programming, interrupt-control setup, HDP flush offsets, PCIe index/data offset reporting, partition status reads, BACO setup, and RAS interrupt handling. The exact macros in this chunk are largely field definitions for config-space and vendor-specific capability surfaces rather than standalone call sites.

## State and Persistence

This header owns no software state and persists nothing. Its constants are fixed into the compiled driver.

The state described by the macros lives in NBIO/BIF hardware register and PCI configuration images:

- GPU IOV schedule dwords and engine interrupt status/enable bits reflect virtualization scheduling and per-engine event state.
- PCI command/status, BARs, capability pointers, ROM BAR, interrupt line/pin, and class-code fields reflect endpoint or root-complex enumeration state.
- PM, PCIe device, link, slot, root, MSI, MSI-X, ACS, PASID, ARI, AER, BAR, power-budget, and DPA registers reflect hardware capabilities, driver/PCI-core policy, sticky status, diagnostic logs, and reset-sensitive configuration.
- AER status and root/slot/link status fields can be sticky or write-one-to-clear according to PCIe semantics, but the generated masks do not express clear-on-write or read side effects.

Persistence across FLR, hot reset, GPU reset, BACO, runtime suspend, or full PCI reset depends on NBIO and PCIe hardware reset domains. A wrong generated mask value would persist in the driver binary until the header is regenerated or corrected.

## Dependencies and Integration Points

Direct dependencies and integration points in this source tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_offset.h`, the required companion for register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_9.c`, which includes this header and uses NBIO 7.9 generated masks with SOC15 register helpers for initialization, doorbells, HDP flushing, PCIe index/data windows, interrupt controls, partition status, and RAS interrupt fallback handling.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_nbio_v7_9.c`, which includes this header while registering NBIO RAS interrupt sources.
- AMDGPU bitfield helpers such as `REG_SET_FIELD` and `REG_GET_FIELD`, which depend on the exact `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` spelling.
- PCIe and SR-IOV/IOV integration paths, where GPU IOV schedule, interrupt, FLR-needed, VM-busy, ACS, PASID, ARI, MSI/MSI-X, and AER fields interact with PCI core policy, IOMMU routing, firmware, and virtualization management.

Cross-generation headers such as `nbio_7_2_0_sh_mask.h`, `nbio_7_7_0_sh_mask.h`, and `nbio_7_11_0_sh_mask.h` contain structurally similar names, but consumers must use the NBIO 7.9.0 mask file with the matching NBIO 7.9.0 offset file. Register maps and endpoint coverage vary by generation.

## Risks

- Chunk-boundary incompleteness: this range starts with a mask whose shift is in the previous chunk and ends with a shift whose mask is in the next chunk. Pair-completeness checks must happen after merge.
- Register/mask mismatch: using these 7.9.0 masks with another NBIO generation's offsets can silently decode or program the wrong bits.
- Function confusion: `BIF_CFG_DEV0_EPF1` endpoint fields and `BIF_CFG_DEV0_RC0` root-complex fields have similar PCIe capability names but target different PCI configuration images.
- GPU IOV event corruption: engine interrupt enable/status bits are dense repeated bitmaps. A one-bit error can enable the wrong engine event, miss a hang-needs-FLR signal, or clear the wrong status.
- Full-dword schedule payloads: UVD/GFX schedule dwords are opaque `0xFFFFFFFF` fields. The mask says nothing about internal subfields, ownership, or valid values.
- PCIe control hazards: link control, completion timeout, max payload/read request, relaxed ordering, no-snoop, LTR, OBFF, emergency power reduction, DPA, ACS, PASID, and ARI fields can affect bus stability, isolation, and performance.
- Interrupt routing hazards: MSI/MSI-X enable, mask, pending, table, PBA, and message address/data fields must remain coordinated with PCI core, interrupt remapping, and AMDGPU interrupt setup.
- AER handling hazards: status, mask, and severity registers look similar but have different semantics. Confusing them can hide faults, over-report recoverable errors, or damage diagnostic logs.
- Reserved-bit damage: generated masks expose named fields but do not identify all reserved bits or write constraints. Writes should preserve unrelated fields and follow PCIe/NBIO programming sequences.

## Test Signals

Useful validation signals for work touching this chunk include:

- AMDGPU builds that include `nbio_v7_9.c` and `amdgpu_ras_nbio_v7_9.c` with no missing, renamed, or duplicate NBIO 7.9.0 macros.
- Mechanical checks that every field has a matching shift/mask pair after adjacent chunk reconciliation, accounting for the two expected local boundary partials.
- Cross-checks against `nbio_7_9_0_offset.h` so every register family here has the expected generated address macro and base index.
- Hardware or emulator PCI config-space dumps for NBIO 7.9 devices decode expected `DEV0_EPF1` and `DEV0_RC0` capability chains, including PM, PCIe, MSI/MSI-X, AER, ACS, PASID, ARI, and vendor-specific capability headers.
- SR-IOV or GPU IOV validation confirms UVD/VCN and GFX schedule registers, engine command-complete events, self-recovered hang events, hang-needs-FLR events, and VM-busy-transition events report and clear as expected.
- PCIe stress tests show no new completion timeout, malformed TLP, ECRC, unsupported request, receiver overflow, surprise-down, or root-port PME anomalies.
- Interrupt tests verify MSI/MSI-X delivery, masking, pending-bit accounting, and root/endpoint message address/data programming.
- Reset coverage, including FLR, GPU reset, hot reset, suspend/resume, and runtime power transitions, confirms PCIe control, AER status/mask/severity, MSI/MSI-X, ACS/PASID/ARI, and GPU IOV event state are restored or intentionally reset.

### subset-b-003330: lines 7453-9894

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_sh_mask.h lines 7453-9894

## Scope

This chunk covers lines 7453-9894 of AMDGPU's generated NBIO 7.9.0 shift/mask header. It contains C preprocessor constants only: no functions, structs, enums, variables, allocations, locks, persistence code, or direct register reads/writes.

The range starts at the `BIF_CFG_DEV0_RC0_MSI_MSG_ADDR_LO__MSI_MSG_ADDR_LO_MASK` line, immediately after the matching shift definition in the previous line/chunk. It then covers PCIe configuration-space field geometry for the `BIF_CFG_DEV0_RC0_*` root-complex/root-port-style block through Gen4/Gen5 link-extension fields. The chunk then enters `addressBlock: aid_nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` and covers most of the embedded physical function 0 configuration-space image, from base PCI identity fields through the `BIF_CFG_DEV0_EPF0_0_PCIE_SRIOV_FIRST_VF_OFFSET__SRIOV_FIRST_VF_OFFSET__SHIFT` line. The matching first-VF-offset mask and the rest of the SR-IOV register set continue after this chunk.

Although this repository path is under a `ceph-client` mirror, the content is AMD GPU NBIO/PCIe register metadata. There is no Ceph or distributed-filesystem runtime behavior in this file section.

## Purpose

`nbio_7_9_0_sh_mask.h` is the generated bitfield-definition companion for NBIO 7.9.0 registers. Each exported macro provides one piece of hardware field geometry:

- `REGISTER__FIELD__SHIFT`: the least-significant bit index of a field.
- `REGISTER__FIELD_MASK`: the bit mask for the field inside the containing register.

Driver code combines these definitions with `nbio_7_9_0_offset.h` register addresses, reset/default headers, and AMDGPU register helper macros such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`. The header lets NBIO and PCIe code use symbolic field names instead of hard-coded bit positions when decoding or composing PCI configuration-space and NBIO register values.

This chunk is primarily a PCIe capability-surface map. It describes MSI, subsystem/vendor-specific capabilities, virtual channels, device serial number, AER, secondary PCIe capability, per-lane equalization, ACS, data link feature, 16 GT/s and 32 GT/s link extensions, EPF0 standard PCI header fields, EPF0 PM/PCIe/MSI/MSI-X capability fields, EPF0 resizable BAR and power/DPA fields, ATS/PRI/PASID, multicast, LTR, ARI, and the beginning of EPF0 SR-IOV.

## Important Macro Families

### RC0 MSI, SSID, Vendor-Specific, and Virtual Channel Fields

The opening lines finish part of the `BIF_CFG_DEV0_RC0_MSI_MSG_ADDR_LO` field set and then define RC0 MSI address/data fields:

- `MSI_MSG_ADDR_HI`, `MSI_MSG_DATA`, `MSI_EXT_MSG_DATA`, `MSI_MSG_DATA_64`, and `MSI_EXT_MSG_DATA_64` provide 32-bit and 64-bit message-address/data encodings.
- `SSID_CAP_LIST` and `SSID_CAP` expose capability ID, next pointer, subsystem vendor ID, and subsystem ID fields.
- `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, and scratch VSEC words provide PCIe vendor-specific enhanced capability metadata.
- `PCIE_VC_ENH_CAP_LIST`, `PCIE_PORT_VC_CAP_REG1/2`, `PCIE_PORT_VC_CNTL`, `PCIE_PORT_VC_STATUS`, and VC0/VC1 resource capability/control/status registers encode virtual-channel count, arbitration tables, TC-to-VC maps, VC IDs, enable bits, and negotiation/status bits.

These root-complex-style fields describe the PCIe configuration image that software or firmware may expose for the RC0 function. The MSI and VC fields are not executable APIs; they are masks used by code that reads or programs those PCIe capability registers.

### RC0 Device Serial Number and AER

The RC0 device serial number and advanced error reporting block includes:

- `PCIE_DEV_SERIAL_NUM_ENH_CAP_LIST`, `PCIE_DEV_SERIAL_NUM_DW1`, and `PCIE_DEV_SERIAL_NUM_DW2`.
- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`.
- `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY`.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK`.
- `PCIE_ADV_ERR_CAP_CNTL`, `PCIE_HDR_LOG0..3`, `PCIE_ROOT_ERR_CMD`, `PCIE_ROOT_ERR_STATUS`, `PCIE_ERR_SRC_ID`, and `PCIE_TLP_PREFIX_LOG0..3`.

The uncorrectable-error groups cover PCIe error bits such as data-link-protocol error, surprise down, poisoned TLP, flow-control protocol error, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC error, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic-op egress blocked, TLP prefix blocked, and poisoned-TLP egress blocked. The same conceptual bit positions recur across status, mask, and severity registers, but their semantics differ: one reports/clears state, one suppresses reporting, and one classifies severity.

The correctable-error groups include receiver error, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal, correctable internal error, header-log overflow, and integer-error status or mask fields. Header-log and TLP-prefix-log fields are full-width diagnostic words.

### RC0 Secondary PCIe, Lane Equalization, ACS, DLF, and High-Speed Link Extensions

The RC0 secondary PCIe capability portion defines:

- `PCIE_SECONDARY_ENH_CAP_LIST`, `PCIE_LINK_CNTL3`, and `PCIE_LANE_ERROR_STATUS`.
- `PCIE_LANE_0_EQUALIZATION_CNTL` through `PCIE_LANE_15_EQUALIZATION_CNTL`, each with downstream-port TX preset, downstream-port RX preset hint, upstream-port TX preset, and upstream-port RX preset hint fields.
- `PCIE_ACS_ENH_CAP_LIST`, `PCIE_ACS_CAP`, and `PCIE_ACS_CNTL`.
- `PCIE_DLF_ENH_CAP_LIST`, `DATA_LINK_FEATURE_CAP`, and `DATA_LINK_FEATURE_STATUS`.
- `PCIE_PHY_16GT_ENH_CAP_LIST`, `LINK_CAP_16GT`, `LINK_CNTL_16GT`, `LINK_STATUS_16GT`, local/RTM parity mismatch status registers, and per-lane `LANE_N_EQUALIZATION_CNTL_16GT` fields.
- `PCIE_MARGINING_ENH_CAP_LIST`, margining port capability/status, lane 0-15 margining control/status registers, and `LINK_CAP_32GT`, `LINK_CNTL_32GT`, `LINK_STATUS_32GT`.

These macros represent PCIe link-training and diagnostic surfaces. The regular lane-equalization groups are repetitive by lane and must remain lane-number aligned. The 16 GT/s block captures Gen4-style equalization completion/phase status, retimer presence, link equalization requests, and per-lane preset coefficients. The 32 GT/s block captures Gen5-style equalization bypass, modified TS usage, lane equalization controls, equalization phase status, link-flap status, precoding status, and downstream/upstream component presence.

ACS capability/control fields are security and routing sensitive: source validation, translation blocking, P2P request/completion redirect, upstream forwarding, egress control, direct translated P2P, and egress vector behavior affect peer-to-peer DMA and IOMMU isolation assumptions.

### EPF0 Base PCI Header and PM/PCIe Capabilities

The `aid_nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` address block starts in this chunk and maps the embedded physical function 0 PCI configuration-space image. The base header fields include:

- `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS`.
- `COMMAND` and `STATUS`, covering I/O enable, memory enable, bus master enable, special cycle, write-and-invalidate, VGA snoop, parity-response enable, stepping, SERR enable, fast-back enable, interrupt disable, capability-list status, interrupt status, DEVSEL timing, abort, parity, and system-error status bits.
- `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`, `BASE_ADDR_1..6`, `CARDBUS_CIS_PTR`, `ADAPTER_ID`, `ROM_BASE_ADDR`, `CAP_PTR`, interrupt line/pin, `MIN_GRANT`, and `MAX_LATENCY`.
- Vendor capability and adapter ID write-alias fields.

The PM capability block includes `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`. These expose PCI PM capability metadata, supported D-states, PME support, current power state, no-soft-reset behavior, PME enable/status, data select/scale, bus power/clock control, B2/B3 support, and PM data fields.

The EPF0 PCIe capability block includes `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`. These fields describe endpoint/device type, payload and request sizes, error-reporting enables/status, relaxed ordering, no-snoop, extended tags, FLR, emergency power reduction, link speeds/widths, ASPM and link-management controls, data-link-active reporting, bandwidth notifications, completion-timeout policy, ARI/atomic/IDO/LTR/OBFF/10-bit-tag/TLP-prefix support, target link speed, compliance/deemphasis settings, equalization phase status, retimer presence, crosslink status, and DRS message receipt.

### EPF0 MSI, MSI-X, Vendor-Specific, VC, Serial Number, and AER

EPF0 interrupt-related capability fields include:

- `MSI_CAP_LIST`, `MSI_MSG_CNTL`, `MSI_MSG_ADDR_LO/HI`, 32-bit and 64-bit message data, extended data, mask, and pending fields.
- `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`, with table size, function mask, MSI-X enable, BIR, and table/PBA offset fields.

The EPF0 vendor-specific and virtual-channel groups mirror the RC0 capability families, using the `BIF_CFG_DEV0_EPF0_0_*` prefix and the EPF0 offset range. The same caveats apply: VSEC capability IDs, versions, lengths, next pointers, scratch words, VC arbitration fields, TC-to-VC maps, VC IDs, enable bits, and negotiation status are field geometry only.

EPF0 also has its own device serial number and AER block:

- `PCIE_DEV_SERIAL_NUM_ENH_CAP_LIST`, serial number low/high words.
- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, uncorrectable status/mask/severity, correctable status/mask, advanced error capability/control, header logs, and TLP prefix logs.

Unlike RC0, the EPF0 AER portion in this chunk does not include root error command/status or error source ID fields, which are root-port-specific in the RC0 section.

### EPF0 Resizable BAR, Power Budget, DPA, Secondary PCIe, and Lane Equalization

The EPF0 resizable BAR extended capability defines `PCIE_BAR_ENH_CAP_LIST` plus BAR1 through BAR6 capability/control pairs:

- `BAR_SIZE_SUPPORTED` fields advertise supported sizes.
- `BAR_INDEX`, `BAR_TOTAL_NUM`, `BAR_SIZE`, and `BAR_SIZE_SUPPORTED_UPPER` fields select and control resizable BAR size information.

The power budget and dynamic power allocation fields include `PCIE_PWR_BUDGET_ENH_CAP_LIST`, data select/data/capability registers, `PCIE_DPA_ENH_CAP_LIST`, DPA capability, latency indicator, status/control, and substate power allocation registers 0 through 7. These fields are part of the PCIe power-management surface exposed by the device.

EPF0 secondary PCIe and per-lane equalization definitions mirror the RC0 structure: secondary enhanced capability header, link control 3, lane error status, and lane 0-15 equalization control fields. This gives software symbolic masks for EPF0 link training, error visibility, and equalization preset programming/status decode.

### EPF0 ACS, ATS, PRI, PASID, Multicast, LTR, ARI, and SR-IOV Start

The later EPF0 portion covers isolation, address translation, virtualization, and latency reporting capabilities:

- `PCIE_ACS_ENH_CAP_LIST`, `PCIE_ACS_CAP`, and `PCIE_ACS_CNTL` define ACS support and control bits for source validation, translation blocking, P2P request/completion redirect, upstream forwarding, egress control, direct translated P2P, and egress vector capacity/control.
- `PCIE_ATS_ENH_CAP_LIST`, `PCIE_ATS_CAP`, and `PCIE_ATS_CNTL` cover ATS invalidation queue depth, page-aligned requests, global invalidation support, relaxed ordering support, STU, and ATC enable.
- `PCIE_PAGE_REQ_ENH_CAP_LIST`, `PCIE_PAGE_REQ_CNTL`, `PCIE_PAGE_REQ_STATUS`, `PCIE_OUTSTAND_PAGE_REQ_CAPACITY`, and `PCIE_OUTSTAND_PAGE_REQ_ALLOC` represent PRI/page-request enable/reset, response failure, unexpected page-request group/index, stopped status, PASID-required status, and outstanding request capacity/allocation.
- `PCIE_PASID_ENH_CAP_LIST`, `PCIE_PASID_CAP`, and `PCIE_PASID_CNTL` describe PASID execute permission, privileged mode, max PASID width, and enable bits.
- `PCIE_MC_ENH_CAP_LIST`, `PCIE_MC_CAP`, `PCIE_MC_CNTL`, multicast address, receive, block-all, and untranslated-block fields describe PCIe multicast support and filtering.
- `PCIE_LTR_ENH_CAP_LIST` and `PCIE_LTR_CAP` expose maximum snoop and no-snoop latency values and scales.
- `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL` expose ARI function-group support/enables, function group selection, and next function number.
- `PCIE_SRIOV_ENH_CAP_LIST`, `PCIE_SRIOV_CAP`, `PCIE_SRIOV_CONTROL`, `PCIE_SRIOV_STATUS`, `PCIE_SRIOV_INITIAL_VFS`, `PCIE_SRIOV_TOTAL_VFS`, `PCIE_SRIOV_NUM_VFS`, `PCIE_SRIOV_FUNC_DEP_LINK`, and the first line of `PCIE_SRIOV_FIRST_VF_OFFSET` begin the SR-IOV capability field set.

The SR-IOV fields are privilege and resource sensitive. This chunk includes VF migration capability/status, ARI hierarchy preservation/control, VF 10-bit tag support/enable, VF enable, VF migration enable/interrupt enable, VF memory-space enable, initial/total/active VF counts, function dependency link, and the shift for first VF offset. The first-VF-offset mask plus VF stride, VF device ID, supported/system page size, VF BARs, and migration-state-array fields are outside this exact range.

## APIs, Types, and Functions

There are no callable APIs, C types, or functions in this chunk. The exported interface is the generated macro namespace. Consumer code includes this header together with `nbio_7_9_0_offset.h` and uses field helper macros to isolate or compose values.

The file supplies field geometry only. It does not encode reset values, register offsets, read/write permissions, reserved-bit policy, write-one-to-clear behavior, side effects, firmware ownership, ordering requirements, or polling/timeout rules. Those semantics come from the matching offset/default headers, AMDGPU NBIO code, PCIe specification semantics, firmware policy, and ASIC documentation.

AMDGPU NBIO 7.9 code includes this header in files such as `drivers/gpu/drm/amd/amdgpu/nbio_v7_9.c` and NBIO RAS support. The visible NBIO 7.9 implementation uses generated masks for register-field composition and extraction through `REG_GET_FIELD` and `REG_SET_FIELD`, while this chunk's PCIe configuration macros are part of the same generated field namespace.

## Control Flow

This header has no local runtime control flow. Runtime use is external and generally follows this pattern:

1. Driver, firmware-facing, or diagnostic code selects an NBIO 7.9 register offset from `nbio_7_9_0_offset.h`.
2. It reads or prepares a register value through the appropriate AMDGPU access path, PCI configuration-space path, or generated SOC15 helper.
3. It extracts a field with `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`, or uses a read-modify-write helper that preserves unrelated bits.
4. Hardware applies the relevant PCIe/NBIO behavior: interrupt delivery, capability advertisement, link training, AER reporting, ACS routing/isolation, ATS/PRI/PASID translation services, multicast filtering, LTR reporting, ARI function enumeration, SR-IOV VF enumeration, or resource sizing.

The order in this file follows the generated register database and PCI capability layout. It is not an execution sequence. Repeated status, mask, severity, and control bit names can share positions while requiring different software handling.

## State and Persistence Behavior

The chunk owns no software state and persists nothing. It names fields whose state lives in NBIO hardware registers or the PCIe configuration-space image for RC0 and EPF0. Persistence depends on PCIe reset rules, GPU/NBIO reset domains, function-level reset, firmware initialization, runtime power management, suspend/resume restore, SR-IOV state transitions, and explicit driver writes.

Represented state includes:

- Configuration state: PCI command bits, BAR and ROM BAR values, MSI/MSI-X enables/masks/address/data, PM state, PME enable, PCIe device/link controls, VC controls, AER masks/severity, ACS controls, ATS/PRI/PASID enables, multicast controls, ARI controls, DPA controls, resizable BAR controls, and SR-IOV VF enable/count controls.
- Capability and identity state: vendor/device/class IDs, capability IDs and next pointers, subsystem IDs, VSEC metadata, device serial number, PCIe device/link capabilities, VC capabilities, AER capabilities, resizable BAR support, power budget and DPA capabilities, ACS/ATS/PRI/PASID capabilities, multicast/LTR/ARI capabilities, and SR-IOV capability fields.
- Status and diagnostic state: PCI status, PM/PME status, PCIe device/link status, VC status, AER correctable/uncorrectable status, header logs, TLP prefix logs, lane error status, per-lane equalization status, data link feature exchange status, 16 GT/s and 32 GT/s link/equalization/parity status, PRI status, SR-IOV migration status, and MSI pending bits.

Callers must distinguish writable controls from read-only capabilities, sticky/W1C status bits from ordinary status, command-like bits from persistent configuration, and reserved bits from valid fields. The mask names alone do not provide those behavioral rules.

## Dependencies and Integration Points

This chunk depends on the generated NBIO 7.9.0 register-header set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_offset.h` supplies matching `regBIF_CFG_DEV0_RC0_*` and `regBIF_CFG_DEV0_EPF0_0_*` offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_default.h`, where present, supplies generated default/reset values.
- AMDGPU NBIO 7.9 source, RAS source, SOC15 register helpers, and PCI/NBIO code consume the shift/mask naming convention when building and decoding register values.

Practical integration points include:

- GPU PCIe enumeration and capability-chain decoding for RC0 and EPF0.
- Interrupt setup and diagnostics through MSI/MSI-X fields.
- PCIe link management, equalization, margining, high-speed link extension status, retimer/precoding visibility, and lane error diagnostics.
- AER diagnostics and recovery, including uncorrectable/correctable status, masks, severity, header logs, TLP prefix logs, and root-port reporting fields for RC0.
- Resource sizing and exposure through EPF0 BARs, resizable BAR registers, and ROM BAR fields.
- Power management through PCI PM, LTR, power budget, and DPA fields.
- IOMMU, peer-to-peer DMA, VFIO, and virtualization behavior through ACS, ATS, PRI, PASID, ARI, multicast, and SR-IOV fields.
- GPU reset and SR-IOV transitions where PF/VF configuration, VF enablement, VF counts, and memory-space enable state must be preserved, restored, or intentionally reinitialized.

## Risks and Edge Cases

- The range starts and ends mid-register. `BIF_CFG_DEV0_RC0_MSI_MSG_ADDR_LO__MSI_MSG_ADDR_LO__SHIFT` is on the previous line, and `BIF_CFG_DEV0_EPF0_0_PCIE_SRIOV_FIRST_VF_OFFSET__SRIOV_FIRST_VF_OFFSET_MASK` is on the next line after this chunk. The merge lane must reconcile adjacent chunks before describing those registers as complete.
- Bitfield drift is high impact. A wrong shift or mask can compile cleanly while decoding the wrong PCIe bit, corrupting adjacent fields, breaking MSI/MSI-X setup, misadvertising capabilities, changing link behavior, or writing reserved bits.
- AER status, mask, and severity registers intentionally reuse many field names and bit positions. Copying handling between them can accidentally clear diagnostics, suppress errors, or change fatal/non-fatal classification.
- PCI status, device/link status, AER status, lane error status, PRI status, SR-IOV migration status, MSI pending bits, and similar fields can be sticky, W1C, or side-effectful depending on the hardware specification. Generic read-modify-write operations can lose diagnostics.
- ACS, ATS, PRI, PASID, ARI, multicast, and SR-IOV fields are virtualization and isolation sensitive. Incorrect masks can affect IOMMU group isolation, peer DMA routing, VF enumeration, address translation, page-request behavior, and passthrough assumptions.
- MSI and MSI-X address/data/mask/pending fields overlap in the PCI capability layout depending on 32-bit versus 64-bit forms. Callers must use the capability control bits and matching offsets; the masks alone do not enforce layout selection.
- Repeated lane 0-15 equalization and margining groups are copy-error prone. Prefix or lane-number mix-ups may compile if the target macro exists but decode or program the wrong lane.
- RC0 and EPF0 define many similar capability names under different prefixes and offset ranges. Prefix mix-ups can target the wrong PCIe function or root-complex image.
- Resizable BAR and SR-IOV resource fields affect memory aperture sizing and VF layout. Incorrect writes can break PCI enumeration, VF BAR placement, firmware resource accounting, or guest-visible device configuration.
- High-speed 16 GT/s and 32 GT/s link extension fields are generation-specific. Treating them like older PCIe link fields can misread equalization, retimer, precoding, or link-flap state.
- The header provides masks and shifts, not access ordering. Link retrain/equalization, FLR, SR-IOV enablement, PRI reset, and mailbox-like fields in nearby capability spaces require sequencing and timeout policy from driver or hardware documentation.

## Test Signals

- Build AMDGPU configurations that include NBIO 7.9.0 support. Compile failures catch malformed generated symbols or mismatches between generated headers and driver users.
- Run generated-header consistency checks against the authoritative NBIO 7.9.0 register database: every field should have the expected shift and mask, every register in this chunk should have a matching offset, and defaults should align where generated.
- Cross-check `BIF_CFG_DEV0_RC0_*` and `BIF_CFG_DEV0_EPF0_0_*` repeated capability families for expected common layouts and intentional root-port-versus-endpoint differences, especially AER root-error fields and SR-IOV-only endpoint fields.
- Validate PCIe enumeration on matching hardware with tools such as `lspci -vv`: vendor/device/class IDs, BARs, PM/PCIe/MSI/MSI-X/AER/ACS/ATS/PRI/PASID/LTR/ARI/SR-IOV capability chains, link capabilities, and resizable BAR information should decode coherently.
- Exercise MSI and MSI-X setup paths, interrupt masking/unmasking, and pending-bit diagnostics to catch address/data/mask field mismatches.
- Exercise PCIe link behavior at supported speeds: negotiated speed/width, link retraining, equalization phase status, per-lane equalization controls, lane error reporting, 16 GT/s parity/equalization status, 32 GT/s retimer/precoding/link-flap status, and margining status where available.
- Exercise AER paths where hardware and platform support allow: correctable/uncorrectable status, mask/severity policy, header logs, TLP prefix logs, root-port error command/status/source IDs for RC0, and clearing behavior.
- Validate ACS/IOMMU and peer-to-peer DMA behavior on systems exposing these registers, especially for VFIO or passthrough deployments.
- Validate ATS/PRI/PASID operation with IOMMU-enabled workloads where supported: translation enablement, page request capacity/allocation, response-failure status, PASID width, and PASID privilege/execute permission behavior.
- Validate SR-IOV transitions on supported devices: initial/total/active VF counts, VF enable, VF memory-space enable, ARI hierarchy, first VF offset continuity with the following chunk, and reset/suspend/resume restoration.
- Run suspend/resume and GPU reset recovery tests to verify hardware state represented by these masks is restored or intentionally reinitialized according to AMDGPU policy.

### subset-b-003331: lines 9895-12283

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_sh_mask.h lines 9895-12283

## Scope

This chunk is a generated AMD NBIO 7.9.0 register field header section. It contains preprocessor constants only: each hardware register field is represented by a `__SHIFT` constant and a matching `_MASK` constant. There are no C functions, structs, enums, storage objects, or executable control flow in this range.

The covered range starts at the tail of the `BIF_CFG_DEV0_EPF0_0_PCIE_SRIOV_FIRST_VF_OFFSET` definition and then describes a large PCIe configuration-space span for `DEV0_EPF0_0`, followed by the beginning of a second address block for `DEV0_EPF1_0`. The macros are paired with register-address constants from `nbio_7_9_0_offset.h` and are consumed through AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15*`, and `WREG32_SOC15*` in NBIO and RAS code.

## Purpose

The purpose of this chunk is to give NBIO 7.9.0 driver code stable symbolic names for bit extraction and bit construction in PCIe/NBIO registers. It avoids hard-coded shifts and masks in consumers and keeps the driver aligned with the generated hardware register database.

The covered registers describe:

- SR-IOV virtual-function layout and VF BAR configuration for endpoint function 0.
- Data Link Feature and high-speed PCIe PHY capability/status fields.
- PCIe 16.0 GT/s and 32.0 GT/s equalization, parity, and link-status fields.
- PCIe lane margining controls/status for lanes 0 through 15.
- AMD GPU IOV vendor-specific capability fields, including host/VF mailbox bits, framebuffer partition registers, scheduler data words, and engine interrupt bitmap registers.
- Standard PCI configuration header and capability blocks for endpoint function 1.
- MSI/MSI-X layout for endpoint function 1.
- Vendor-specific and Advanced Error Reporting fields for endpoint function 1, ending in the uncorrectable-error mask block.

## Important APIs, Types, and Functions

This header range does not define APIs in the function-call sense. Its important interface is the naming convention used by AMDGPU register helper macros:

- `BIF_CFG_DEV0_EPF0_0_<REGISTER>__<FIELD>__SHIFT`: bit offset of a field inside the named register.
- `BIF_CFG_DEV0_EPF0_0_<REGISTER>__<FIELD>_MASK`: bit mask for that field.
- `BIF_CFG_DEV0_EPF1_0_<REGISTER>__<FIELD>__SHIFT` and `_MASK`: same convention for endpoint function 1.

Consumers normally combine these with:

- `REG_GET_FIELD(value, REGISTER, FIELD)` to extract fields using `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`.
- `REG_SET_FIELD(value, REGISTER, FIELD, field_value)` to write a field into a composed register value.
- `RREG32_SOC15*` and `WREG32_SOC15*` to read or write the actual NBIO register identified by the companion `reg...` macro in `nbio_7_9_0_offset.h`.

Direct consumers observed in this source tree include `drivers/gpu/drm/amd/amdgpu/nbio_v7_9.c` and `drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_nbio_v7_9.c`, both of which include this header alongside `nbio_7_9_0_offset.h`. The specific fields in this chunk are more likely to be used by SR-IOV, PCIe capability, AER, mailbox, virtualization, or diagnostic paths than by the basic doorbell setup paths shown in `nbio_v7_9.c`.

## Register Groups Covered

### EPF0 SR-IOV Capability Tail

The range begins with the end of `BIF_CFG_DEV0_EPF0_0_PCIE_SRIOV_FIRST_VF_OFFSET`, then defines:

- `PCIE_SRIOV_VF_STRIDE`: spacing between VFs in PCI function numbering.
- `PCIE_SRIOV_VF_DEVICE_ID`: device ID reported for VFs.
- `PCIE_SRIOV_SUPPORTED_PAGE_SIZE` and `PCIE_SRIOV_SYSTEM_PAGE_SIZE`: page-size capability/control fields.
- `PCIE_SRIOV_VF_BASE_ADDR_0` through `_5`: VF BAR aperture values.
- `PCIE_SRIOV_VF_MIGRATION_STATE_ARRAY_OFFSET`: split into a BAR indicator (`BIR`, bits 0-2) and an aligned offset field (bits 3-31).

These are state-bearing PCI configuration fields. Writes may affect VF enumeration, BAR layout, and migration-related memory placement.

### Data Link Feature and 16 GT/s Link Blocks

`PCIE_DLF_ENH_CAP_LIST`, `DATA_LINK_FEATURE_CAP`, and `DATA_LINK_FEATURE_STATUS` describe capability-list metadata, locally supported DLF bits, DLF exchange enable, remote supported bits, and validity status.

The 16 GT/s group includes:

- `PCIE_PHY_16GT_ENH_CAP_LIST`.
- Reserved `LINK_CAP_16GT` and `LINK_CNTL_16GT`.
- `LINK_STATUS_16GT` bits for equalization complete, phase 1/2/3 success, and equalization request.
- `LOCAL_PARITY_MISMATCH_STATUS_16GT`, `RTM1_PARITY_MISMATCH_STATUS_16GT`, and `RTM2_PARITY_MISMATCH_STATUS_16GT`.
- `LANE_0_EQUALIZATION_CNTL_16GT` through `LANE_15_EQUALIZATION_CNTL_16GT`, each exposing downstream-port and upstream-port 16 GT/s TX preset nibbles.

The per-lane repetition is significant: all lanes use the same field layout, but the generated names encode the lane number. Any table-driven consumer must map lane indices to distinct register symbols in C, since these are preprocessor names rather than indexable data.

### PCIe Lane Margining

The margining block starts with `PCIE_MARGINING_ENH_CAP_LIST`, `MARGINING_PORT_CAP`, and `MARGINING_PORT_STATUS`. It then defines control/status pairs for lanes 0 through 15:

- `LANE_N_MARGINING_LANE_CNTL` fields: receiver number, margin type, usage model, and margin payload.
- `LANE_N_MARGINING_LANE_STATUS` fields: status mirrors for receiver number, margin type, usage model, and payload.

These fields support PCIe margining diagnostics. They are likely used by low-level bring-up, validation, or service tooling rather than normal display operation. Incorrect masks here can corrupt diagnostic commands or misread link-quality status on a per-lane basis.

### 32 GT/s Link Capability, Control, and Status

The 32 GT/s registers describe PCIe Gen5 link behavior:

- `LINK_CAP_32GT`: support for equalization bypass to highest rate, no-equalization-needed mode, and modified training-sequence usage modes.
- `LINK_CNTL_32GT`: disable/select bits for equalization bypass, no-equalization-needed, and modified training-sequence usage mode.
- `LINK_STATUS_32GT`: equalization phase status, link equalization request, modified training sequence reception, enhanced link behavior control, transmitter precoding status/request, and no-equalization-needed received.

These are hardware link-training fields. Consumers must treat them as hardware-owned or link-state-sensitive unless the PCIe specification and ASIC programming guide allow writes.

### GPUIOV Vendor-Specific Capability

The chunk defines a large AMD vendor-specific capability for GPU IOV under `BIF_CFG_DEV0_EPF0_0_PCIE_VENDOR_SPECIFIC_*_GPUIOV`.

Notable fields include:

- Enhanced capability list metadata: capability ID, version, and next pointer.
- Vendor-specific header fields: VSEC ID, revision, and length.
- Interrupt enable/status fields for HVVM mailbox transmit-ack and receive-valid events.
- `RESET_CONTROL__SOFT_PF_FLR`: software PF function-level reset control.
- `HVVM_MBOX_DW0`: selected VF index, transmit data, transmit valid bit, receive data, and receive acknowledgement bit.
- `HVVM_MBOX_DW1`: per-VF transmit-ack and receive-valid bits for VF0 through VF15.
- `HVVM_MBOX_DW2`: per-VF transmit-ack and receive-valid bits for VF16 through VF31.
- `CONTEXT`, `TOTAL_FB`, `REGION`, `P2P_OVER_XGMI_ENABLE`, and `VF0_FB` through `VF30_FB`: virtualization resource/configuration fields.
- `OFFSETS` through `OFFSETS4`: encoded resource offset fields.
- Scheduler data words for UVD0 through UVD11 and GFX0 through GFX7, each as `DW0` through `DW8` full-width 32-bit masks.
- Engine interrupt enable/status bitmaps for `ENGA_A0_7`, `ENGA_A8_15`, `ENGB_B0_7`, and `ENGB_B8_15`.

This section is the highest-risk part of the chunk because it describes virtualization mailbox, reset, framebuffer partitioning, and scheduler state surfaces. A bad mask or mismatched register address can affect PF/VF coordination, VF memory assignment, interrupt routing, or reset semantics.

### EPF1 Standard PCI Configuration Header

The address-block comment switches to `aid_nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp`, and the names change to `BIF_CFG_DEV0_EPF1_0_*`.

The EPF1 standard header fields include:

- `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, and `STATUS`.
- `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS`.
- `CACHE_LINE`, `LATENCY`, `HEADER`, and `BIST`.
- BARs `BASE_ADDR_1` through `BASE_ADDR_6`.
- `CARDBUS_CIS_PTR`, `ADAPTER_ID`, `ROM_BASE_ADDR`, `CAP_PTR`.
- Interrupt line/pin and min-grant/max-latency fields.
- Vendor capability, adapter ID write alias, and power-management capability/status/control.

These fields represent PCI configuration state for a secondary endpoint function. They interact with generic PCI enumeration and resource assignment logic, even though this header only gives AMDGPU code the bit layout.

### EPF1 PCIe, MSI, MSI-X, VSEC, and AER

The EPF1 PCIe capability block covers:

- PCIe capability list metadata and capability word.
- Device capability/control/status.
- Link capability/control/status.
- Device capability/control/status 2.
- Link capability/control/status 2.

The MSI/MSI-X block covers:

- MSI capability metadata and message control.
- MSI address/data fields, extended message-data fields, mask and pending registers, and 64-bit variants.
- MSI-X capability metadata, table size/function mask/enable, table BAR indicator and offset, and PBA BAR indicator and offset.

The VSEC and AER block covers:

- Vendor-specific enhanced capability list and header.
- Two full-width scratch/vendor-specific registers.
- Advanced Error Reporting enhanced capability list.
- `PCIE_UNCORR_ERR_STATUS`: uncorrectable PCIe error status bits such as data-link protocol error, surprise down, poisoned TLP, flow-control protocol error, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC error, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress blocked, TLP prefix blocked, and poisoned TLP egress blocked.
- `PCIE_UNCORR_ERR_MASK`: the same bit positions represented as mask-control fields. The chunk ends before the complete surrounding AER group finishes; the next chunk continues with the remaining mask bits/severity/correctable-error definitions.

## Control Flow

There is no runtime control flow in this chunk. The effective control flow appears in consumers:

1. Driver code reads a register value through a SOC15 register accessor using a `reg...` offset macro.
2. It extracts a field with `REG_GET_FIELD`, which depends on these `__SHIFT` and `_MASK` definitions.
3. For writes, it composes or updates a register value with `REG_SET_FIELD`.
4. It writes the result back through a `WREG32_SOC15*` accessor.

For stateful capability/configuration registers, the hardware, firmware, PCI core, hypervisor, or PF/VF management path may also update the register asynchronously from the perspective of ordinary AMDGPU code.

## State and Persistence Behavior

The header itself has no memory or persistence. The defined fields describe hardware or PCI configuration state that persists in device registers across normal software reads/writes and usually resets on device reset, function-level reset, bus reset, or ASIC reset.

State-sensitive areas in this chunk include:

- SR-IOV VF counts, spacing, BARs, page size, and migration state offset. These affect VF exposure and guest-visible configuration.
- Link status, equalization, parity mismatch, and margining fields. These reflect physical link state and may change as the PCIe link trains or diagnostics run.
- GPUIOV mailbox valid/ack/status fields. These are handshake state and may be consumed by PF/VF, firmware, hypervisor, or management logic.
- GPUIOV framebuffer and scheduler data words. These describe virtualization resource assignment or scheduling state.
- EPF1 command/status, MSI/MSI-X, and AER masks/status. These affect PCI enablement, interrupt routing, and error reporting behavior.

Because many fields are PCI configuration-space fields, writes may be visible outside the driver through PCI config reads, guest VF configuration, firmware policy, or host error-reporting paths.

## Dependencies

Direct dependencies for useful consumption are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_offset.h`: provides the matching register addresses and base indices.
- AMDGPU register helper macros in the AMDGPU driver infrastructure, including `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15*`, and `WREG32_SOC15*`.
- SOC15/NBIO instance routing and ASIC register access plumbing in AMDGPU.
- PCIe, SR-IOV, AER, MSI/MSI-X, and AMD GPU IOV hardware specifications for the semantics behind the fields.

The generated naming must stay synchronized with the offset header. A correct mask with a mismatched `reg...` offset still produces incorrect hardware access.

## Integration Points

Observed local integration points:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_9.c` includes this mask header and the matching offset header. That file implements NBIO operations such as revision detection, memory-controller access gating, doorbell aperture setup, interrupt handling, register remap, partition-mode reads, and RAS interrupt fallback handling.
- `drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_nbio_v7_9.c` includes the same headers while registering NBIO RAS interrupt sources.
- The matching `nbio_7_9_0_offset.h` defines register symbols for many covered fields, including SR-IOV registers, GPUIOV VSEC registers, and EPF1 configuration/AER registers.

Likely broader integration points:

- SR-IOV PF/VF setup and management paths use the SR-IOV and GPUIOV fields to expose VFs, map VF BARs, partition framebuffer, and communicate mailbox state.
- PCIe diagnostics or service tooling may use the 16 GT/s, 32 GT/s, equalization, parity, and margining definitions.
- Interrupt and error-reporting paths use MSI/MSI-X and AER definitions when configuring endpoint-function interrupt behavior or interpreting PCIe errors.
- RAS/error telemetry may consume PCIe error status bits, even if this specific chunk does not define executable RAS handlers.

## Risks and Review Notes

- Generated-header drift is the primary risk. If this file is regenerated from an incorrect register database, all consumers compile cleanly but operate on wrong bits.
- Field-name duplication by convention is easy to misuse. For example, `*_MASK_MASK` names are valid generated symbols for mask registers, not a typo.
- The range starts and ends inside larger logical groups. Any manual review or merge must include adjacent chunks for complete SR-IOV and AER context.
- GPUIOV mailbox and reset fields are sensitive. Writing valid/ack/reset bits with the wrong mask can break PF/VF handshakes or trigger unexpected reset behavior.
- Per-lane PCIe fields are repetitive. Copy/paste or table-generation mistakes can silently target the wrong lane.
- Reserved/full-width fields such as scheduler `DWn` and vendor scratch registers should not be interpreted without the matching hardware specification.
- Link-training and margining fields can be hardware-owned. Polling or writing them without respecting PCIe timing/state rules can produce misleading diagnostics or unstable link behavior.
- PCI config command/status, MSI/MSI-X, and AER mask/status writes affect system-visible behavior and may interact with Linux PCI core ownership.

## Test Signals

Useful validation signals for changes involving this chunk:

- Compile coverage for AMDGPU with NBIO 7.9.0 enabled; this catches missing or renamed generated symbols.
- Static comparison against the authoritative register database or a known-good generated header, especially for shift/mask pairs and lane/VF repetition.
- Boot/probe on NBIO 7.9.0 hardware with `amdgpu` loaded; confirm no register-access faults or PCI enumeration regressions.
- SR-IOV validation: PF probe, VF creation, VF BAR sizing, VF device ID exposure, guest VF probe, and GPUIOV mailbox traffic.
- PCIe link validation: expected negotiated speed/width, equalization completion bits, and absence of unexpected parity/margining errors under normal operation.
- AER validation: correct reporting/masking of EPF1 PCIe uncorrectable errors, ideally through controlled PCIe error injection or platform error logs.
- Interrupt validation: MSI/MSI-X enablement and delivery for EPF1 paths if that function is active.
- RAS validation: NBIO RAS interrupt registration still succeeds and PCIe/NBIO error telemetry remains coherent.

## Summary

Lines 9895-12283 define the bit-level ABI between AMDGPU NBIO 7.9.0 software and a large PCIe configuration/register surface. The chunk is not executable code, but it is high impact because the macros govern SR-IOV layout, PCIe link diagnostics, GPU IOV mailbox/resource state, EPF1 interrupt configuration, and the beginning of EPF1 AER handling. Correctness depends on exact synchronization between these masks, the companion offset header, and the underlying NBIO 7.9.0 hardware register specification.

### subset-b-003332: lines 12284-15100

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_sh_mask.h lines 12284-15100

## Scope

This chunk covers lines 12284-15100 of AMDGPU's generated NBIO 7.9.0 shift/mask header. It contains C preprocessor constants only: no functions, structs, enums, variables, allocation, locking, persistence code, or direct register accesses.

The range starts at the tail of `BIF_CFG_DEV0_EPF1_0_PCIE_UNCORR_ERR_MASK`, then covers the rest of the PCIe extended capability and RCC/RCCPFC field map for device 0, endpoint function 1 / RCC device 1. It ends inside the MSI-X table field map after `PCIEMSIX_VECT162_ADDR_LO`, with line 15100 only introducing the `PCIEMSIX_VECT162_ADDR_HI` register heading; that register's shift and mask definitions continue in the next chunk.

Although this repository path is under a `ceph-client` source tree mirror, the content is AMD GPU NBIO/PCIe register metadata. It has no Ceph or distributed-filesystem runtime behavior.

## Purpose

`nbio_7_9_0_sh_mask.h` is the bitfield-definition companion to the NBIO 7.9.0 register map. Each macro provides one of two pieces of field geometry:

- `REGISTER__FIELD__SHIFT`: the least-significant bit index for a hardware field.
- `REGISTER__FIELD_MASK`: the bit mask for that field in the containing register.

AMDGPU NBIO and RAS code includes this header with the matching NBIO 7.9.0 offset header, then uses common register helpers such as `REG_GET_FIELD` and `REG_SET_FIELD` around SOC15/MMIO/PCI configuration accesses. This chunk supplies symbolic field names for PCIe AER/capability registers, RCC endpoint/downstream controls, sticky restore registers, and a large MSI-X vector table.

## Important Definitions

The opening `BIF_CFG_DEV0_EPF1_0` section completes and extends endpoint-function PCIe configuration-space capability definitions:

- AER uncorrectable error mask tail bits for atomic-operation egress blocked, TLP prefix blocked, and poisoned-TLP egress blocked.
- AER uncorrectable error severity fields for DLP, surprise down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic-op egress blocked, TLP prefix blocked, and poisoned-TLP egress blocked classifications.
- Correctable error status and mask fields for receiver error, bad TLP/DLLP, replay rollover, replay timer timeout, advisory nonfatal, internal correctable error, and header-log overflow.
- Advanced error capability/control fields for first-error pointer, ECRC generation/checking capability and enables, multi-header logging, TLP prefix log presence, and completion timeout log capability.
- Header log and TLP prefix log registers, each modeled as 32-bit `TLP_HDR` or `TLP_PREFIX` payload fields.
- BAR enhancement capability and per-BAR capability/control fields for BAR1 through BAR6, including supported size bitmaps, selected BAR index, total BAR count, active BAR size, and upper supported-size bits.
- Power budgeting fields: capability list metadata, data select, base power, scale, PM substate/state, type, power rail, and system-allocated indication.
- Dynamic Power Allocation fields: capability list, substate maximum, transition latency units/values, power allocation scale, latency indicator, current substate status, control enablement, and substate power allocation entries 0-7.
- ACS fields for capability and control: source validation, translation blocking, peer-to-peer request/completion redirection, upstream forwarding, egress control, direct translated peer-to-peer, enhanced capability, egress vector size, I/O request blocking, downstream/upstream memory target access controls, and unclaimed request redirection.
- PASID and ARI capability/control fields for process address-space IDs, execute/privileged mode support and enablement, maximum PASID width, ARI next function number, multifunction VC/ACS function groups, and function-group selection.

The RCC/RCCPFC sections describe nonstandard NBIO-side PCIe control and restore registers:

- `RCC_DEV0_1` fields for vendor-defined message support, bus-disable policy, DMA/disconnect behavior, memory/io decode checks, AER and LTSSM/root-complex behavior, local/remote ordering controls, requester ID restoration, LTR switch control, multi-host arbitration, and link margining parameters.
- `RCC_EP_DEV0_1` endpoint fields for scratch/control/status, interrupt control/status, configuration decode, LTR transmit policy, strap mirrors, function-0 DPA state, PME control, transmit control/requester ID, error controls, receiver error-ignore policy, completion-timeout controls, TPH handling, and per-generation link speed straps up through Gen5.
- `RCC_DWN_DEV0_1` downstream fields for reserved/scratch storage, hardware-init write lock, unsupported-request reporting, LTR unsupported-request handling, extended tag override, FLR extend mode, immediate PMI disable, AER completion timeout read-only disable, hidden register decode enables for Gen2-Gen5, and function/clock/64-bit/master-completion-timeout strap mirrors.
- `RCC_DWNP_DEV0_1` downstream-port fields for error reporting disable, AER header-log timeout, error message behavior, received-error clear bits, receiver ignore controls, FLR timeout control, Gen2-Gen5 link speed straps, data-link/link-bandwidth notification disables, multifunction strap mirror, and LTR message information from the endpoint.
- `RCC_PFC_AMDGFX` fields for programmed LTR snoop/nonsnoop latency values/scales/requirements, PME restore, sticky restore of selected AER status bits, TLP header/prefix restore payloads, and auxiliary power/current override.

The closing `PCIEMSIX` section begins `addressBlock: aid_nbio_nbif0_pciemsix_0_usb_MSIXTDEC` and defines the MSI-X table field layout for vectors 0 through 161, plus vector 162 address-low. Each complete vector has:

- `PCIEMSIX_VECTn_ADDR_LO__MSG_ADDR_LO`: low message address bits, shifted by 2 and masked with `0xFFFFFFFC`.
- `PCIEMSIX_VECTn_ADDR_HI__MSG_ADDR_HI`: high message address bits, full 32-bit mask.
- `PCIEMSIX_VECTn_MSG_DATA__MSG_DATA`: MSI-X message data, full 32-bit mask.
- `PCIEMSIX_VECTn_CONTROL__MASK_BIT`: per-vector mask bit at bit 0.

## APIs, Types, And Functions

There are no callable APIs, C types, or functions in this range. The exported interface is the generated macro namespace for NBIO 7.9.0 register fields.

Consumers combine these macros with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_offset.h` for register offsets and base indices.
- AMDGPU register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `WREG32_SOC15_EXT`, `REG_GET_FIELD`, and `REG_SET_FIELD`.
- NBIO/RAS integration code that includes the header, including `amdgpu/nbio_v7_9.c` and `ras/ras_mgr/amdgpu_ras_nbio_v7_9.c`.

The macros encode only bit positions and masks. They do not encode access permissions, reset/default values, read-clear or write-one-to-clear semantics, firmware ownership, ordering requirements, or side effects.

## Control Flow

This header has no local runtime control flow. Runtime use is external and generally follows this pattern:

1. Driver code selects an NBIO 7.9.0 register offset for PCIe configuration, RCC control, RCCPFC restore, or MSI-X table state.
2. It reads the register through an AMDGPU SOC15/MMIO/PCI configuration access path.
3. It decodes a field with the matching `__SHIFT` and `_MASK`, or constructs a read-modify-write value while preserving unrelated bits.
4. Hardware applies the corresponding PCIe/NBIO behavior: AER reporting and classification, correctable-error masking, ECRC control, BAR sizing advertisement, DPA/PM policy, ACS/PASID/ARI capability exposure, RCC decode/error/link controls, sticky AER/TLP restore, LTR/PME/aux-power handling, or MSI-X interrupt delivery.

The order in the file follows the generated register database rather than an execution sequence. Similar names in status, mask, severity, control, clear, and restore registers can imply different hardware operations even when the bit positions are related.

## State And Persistence Behavior

The chunk owns no software state and persists nothing. It names fields whose state lives in NBIO hardware registers, PCIe configuration-space decode/shadow registers, RCC sideband/control registers, and MSI-X table storage. Persistence depends on PCIe reset rules, GPU/NBIO reset domains, firmware initialization, function-level reset, runtime power transitions, suspend/resume restore, and explicit driver writes.

Represented hardware state includes:

- Error state and policy: AER uncorrectable severity, correctable status/masks, header and TLP-prefix logs, RCC error reporting controls, received-error clear bits, receiver ignore controls, completion-timeout controls, and sticky restore fields for AER/TLP diagnostics.
- Configuration and capability state: BAR enhancement, power budgeting, DPA, ACS, PASID, ARI, VDM support, bus decode disables, requester ID restore, LTR, PME, aux power, strap mirrors, function enablement, multifunction capability, hidden register decode, and Gen2-Gen5 link speed strap fields.
- Operational interrupt state: MSI-X message address, message data, and per-vector mask bits for vectors 0-161, with vector 162 starting at the chunk boundary.

Callers must rely on hardware documentation and surrounding AMDGPU policy to decide which fields are read-only, sticky, write-one-to-clear, write-lockable, firmware-owned, security-sensitive, or unsafe to modify while the link/function is active.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 7.9.0 register-header set staying synchronized:

- `nbio_7_9_0_offset.h` supplies matching register offsets and base indices.
- Any generated default/reset header for NBIO 7.9.0, where present in the source tree, supplies reset values separately from these masks.
- AMDGPU's SOC15 register access layer, NBIO platform code, interrupt code, RAS code, PCIe support, and KFD/GPU memory-management paths consume NBIO register definitions indirectly.

Practical integration points are GPU PCIe and interrupt behavior rather than filesystem behavior: GPU PCIe enumeration, AER/RAS diagnosis, BAR sizing and resource setup, power budgeting, Dynamic Power Allocation, ACS/IOMMU isolation, PASID and ARI exposure for virtualization and process address spaces, LTR/PME/power restore, link training and Gen5 capability gating, endpoint/downstream port error policy, MSI-X table programming, interrupt masking, reset recovery, and debug register dumps.

## Risks And Edge Cases

- The chunk begins in the middle of `BIF_CFG_DEV0_EPF1_0_PCIE_UNCORR_ERR_MASK` and ends immediately after the `PCIEMSIX_VECT162_ADDR_HI` heading. Adjacent chunks are required for whole-register conclusions at both boundaries.
- A wrong generated shift or mask can compile cleanly while decoding or writing the wrong hardware bit, corrupting adjacent PCIe configuration, hiding errors, changing severity policy, misprogramming BAR capability, or masking the wrong MSI-X vector.
- AER status, mask, severity, control, and restore registers use overlapping terminology. Copying field handling between these groups can accidentally change fatality classification, suppress reporting, clear diagnostics, or restore stale error state.
- Correctable error status and RCC received-error clear fields may have sticky or write-one-to-clear behavior. Generic read-modify-write code can lose diagnostic evidence if it writes these registers without W1C-aware handling.
- ACS and PASID fields are security- and isolation-sensitive. Incorrect programming can affect IOMMU grouping, peer-to-peer routing, VFIO/passthrough assumptions, process-address-space routing, and privileged/executable PASID behavior.
- RCC hidden decode, strap mirror, link speed, FLR, LTR, PME, requester ID, and error-message controls are platform-sensitive. Misuse can destabilize PCIe links, break reset recovery, or create mismatches between advertised PCIe capabilities and hardware behavior.
- MSI-X table fields represent interrupt routing state. Incorrect address/data/mask handling can route interrupts to the wrong CPU vector, drop interrupts, violate expected per-vector masking, or race with the PCI/MSI core if accessed outside the kernel's MSI-X programming rules.
- Repeated `PCIEMSIX_VECTn_*` macro groups are mechanically similar. Off-by-one vector use or prefix mix-ups are easy to miss in review because every vector has the same field layout.
- Full-width `0xFFFFFFFFL` masks and narrow `0xFFL`/`0x01L` masks mix 32-bit and smaller configuration fields. Callers must preserve register width and reserved bits when composing writes.

## Test Signals

- Build AMDGPU configurations that include NBIO 7.9.0 support. Compile failures catch malformed generated symbols, missing offsets, or mismatches between generated headers and driver users.
- Run generated-header consistency checks against the authoritative NBIO 7.9.0 register database: every field should have the expected shift/mask, every register should have a matching offset, and repeated MSI-X vector records should maintain the same four-register stride.
- Cross-check `BIF_CFG_DEV0_EPF1_0` PCIe capability fields against PCIe capability decoding from matching hardware, including AER, power budgeting, DPA, ACS, PASID, ARI, and BAR enhancement entries.
- Validate PCIe enumeration and diagnostics with tools such as `lspci -vv` on matching hardware: capability chain pointers, AER status/mask/severity, ACS/PASID/ARI capabilities, BAR sizing, power-management data, and link/PME behavior should decode coherently.
- Exercise GPU reset, FLR, suspend/resume, runtime power transitions, and PME/LTR restore paths to confirm RCC/RCCPFC state is preserved, restored, or reinitialized as intended.
- Exercise AER/RAS paths where available: correctable and uncorrectable error reporting, severity classification, header/TLP-prefix logs, sticky restore behavior, received-error clear bits, and error-message generation should match hardware expectations.
- Exercise MSI-X setup and interrupt handling: vector address/data programming, per-vector mask/unmask, interrupt delivery under load, reset recovery, and teardown should not lose or misroute interrupts.
- Validate ACS/IOMMU, PASID, ARI, and peer-to-peer DMA behavior on systems exposing these NBIO 7.9.0 blocks, especially in virtualization, passthrough, or process-address-space use cases.

### subset-b-003333: lines 15101-17790

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_sh_mask.h lines 15101-17790

## Scope

This chunk covers lines 15101-17790 of AMDGPU's generated NBIO 7.9.0 shift/mask header. It contains C preprocessor constants only: no functions, structs, enums, variables, locking, allocation, persistence code, or direct register accesses.

The range starts in the middle of the PCIe MSI-X vector table definitions at `PCIEMSIX_VECT162_ADDR_HI`/`MSG_DATA`/`CONTROL`, continues through vectors 163-255, covers MSI-X pending-bit array registers 0-7 and a small software-index/data window, then moves into NBIF RCC strap fields, BIF reset and reset-interrupt controls, and the beginning of BIF miscellaneous registers. The final section covers ROM/strap BIOS control, doorbell range entries 0-20, and VF base-address mapping registers through `AID0_XCC1_VF5_BASE_ADDR`.

Although this repository path sits under a `ceph-client` source tree mirror, the content is AMD GPU NBIO/PCIe register metadata. It has no Ceph or distributed-filesystem runtime behavior.

## Purpose

`nbio_7_9_0_sh_mask.h` is the bitfield-definition companion to the NBIO 7.9.0 register map. Each macro provides one of two pieces of hardware field geometry:

- `REGISTER__FIELD__SHIFT`: the least-significant bit index of the field.
- `REGISTER__FIELD_MASK`: the field mask in the containing register.

The definitions let AMDGPU code use symbolic NBIO, NBIF, PCIe, reset, strap, MSI-X, doorbell, and virtualization field names instead of hard-coded bit positions while reading, decoding, or updating ASIC registers through generated offsets and driver register helpers. This chunk is focused on the tail of the MSI-X table, strap-programmed PCIe capability/personality controls, reset behavior, reset-related interrupt reporting, doorbell aperture programming, and multi-AID/multi-XCC VF base address mapping.

## Important Definitions

The MSI-X section covers the upper vector-table entries:

- `PCIEMSIX_VECT162_*` through `PCIEMSIX_VECT255_*` define the per-vector message address, message data, and mask bit fields. Each vector uses `ADDR_LO.MSG_ADDR_LO` with shift 2 and mask `0xFFFFFFFC`, `ADDR_HI.MSG_ADDR_HI` and `MSG_DATA.MSG_DATA` as full 32-bit fields, and `CONTROL.MASK_BIT` as bit 0.
- `PCIEMSIX_PBA_0` through `PCIEMSIX_PBA_7` define full 32-bit pending-bit-array words for MSI-X pending state.

The `aid_nbio_nbif0_bif_swus_SUMDEC` block provides a simple software access window:

- `SUM_INDEX` and `SUM_DATA` expose full 32-bit index/data fields.
- `SUM_INDEX_HI` supplies the upper 8 bits of the index path. Together these fields support indirect access to an indexed NBIF/SWUS register space.

The `aid_nbio_nbif0_rcc_strap_rcc_strap_internal` block is the densest part of the chunk. It describes strap-derived PCIe/root-complex configuration fields:

- `RCC_STRAP1_RCC_DEV0_PORT_STRAP0` through `_STRAP14` cover downstream/root-port identity and capability straps: device and subsystem IDs, ARI, ACS, AER, MSI, VC, DSN, ECRC, E2E prefix, LTR, OBFF, atomic operations, two-VC support, ACS subfeatures, retimer presence, 10-bit tags, Gen2/Gen3/Gen4/Gen5 compliance and target speed, lane equalization presets for 16 GT/s and 32 GT/s, power budget data, interrupt pin, PM support, link latencies, DPC enablement, PASID/ATS page request handling, and capability pointer locations.
- `RCC_DEV1_PORT_STRAP*` and `RCC_DEV2_PORT_STRAP*` are present only as comment anchors in this chunk, with no shift/mask macros following them in this range.
- `RCC_STRAP1_RCC_BIF_STRAP0` through `_STRAP6` describe BIF-wide behavior such as bus/device/function numbering, extended config and alternate routing behavior, doorbell/VF aperture sizing, SR-IOV/VF mapping, ATS/PRI/PASID and page-request related capabilities, MSI-X/MSI behavior, power management, FLR, IOV, GPU IOV VSEC sizing/revision, BAR behavior, and timer/reset-related values.
- `RCC_STRAP1_RCC_DEV0_EPF0_STRAP*` and `RCC_STRAP1_RCC_DEV0_EPF1_STRAP*` describe endpoint function 0 and function 1 PCIe personality: function enablement, IDs, revision/class code, legacy device type, D-state support, AER/ACS/DPA/VC/PASID capability exposure, MSI/MSI-X controls, power management and PME support, interrupt pin, FLR support, resize BAR, BAR aperture sizes, doorbell BAR disable, ROM/I/O/VGA disable, VF aperture sizes, SR-IOV total VFs and VF mapping, ATS invalidate queue depth, reset timing, D3hot-to-D0 timing, VF reset/FLR timing, and GPU IOV VSEC length.

The `aid_nbio_nbif0_bif_rst_bif_rst_regblk` block defines reset and reset-notification control:

- `HARD_RST_CTRL`, `SELF_SOFT_RST`, and `SELF_SOFT_RST_2` select reset domains such as DSPT config/private paths, endpoint config/private paths, sticky reset paths, SDP ports, strap reset/reload, and core reset.
- `BIF_GFX_DRV_VPU_RST` describes driver-mode reset bits for PF/VF config and private reset domains.
- `BIF_RST_MISC_CTRL`, `_CTRL2`, and `_CTRL3` define reset policy knobs: driver reset mode, auto-clear behavior, FLR auto-clear, link reset protection and transaction-idle state, link reset grace timing, PME turnoff timeout/mode, strap reload delays, SR-IOV save-on-VF-enable-clear behavior, and dummy response behavior during reset.
- `DEV0_PF0_FLR_RST_CTRL` and `DEV0_PF1_FLR_RST_CTRL` define PF/VF reset routing for function-level reset, soft PF reset, sticky reset domains, grace modes/timeouts, dummy response status, and PF copy/private reset behavior.
- `DEV0_PF0_D3HOTD0_RST_CTRL` and `DEV0_PF1_D3HOTD0_RST_CTRL` define reset behavior tied to D3hot-to-D0 transitions.
- `BIF_INST_RESET_INTR_STS`, `BIF_PF_FLR_INTR_STS`, `BIF_D3HOTD0_INTR_STS`, `BIF_POWER_INTR_STS`, and `BIF_PF_DSTATE_INTR_STS` expose reset, FLR, D3hot-to-D0, PME turnoff, port D-state, and PF D-state interrupt status.
- The matching `*_INTR_MASK` registers expose masks for those interrupt sources.
- `BIF_PF_FLR_RST`, `BIF_DEV0_PF0_DSTATE_VALUE`, `BIF_DEV0_PF1_DSTATE_VALUE`, and `BIF_PORT0_DSTATE_VALUE` define explicit FLR reset trigger bits and target/ack D-state value fields.

The `aid_nbio_nbif0_bif_misc_bif_misc_regblk` portion begins miscellaneous NBIF programming:

- `REGS_ROM_OFFSET_CTRL.ROM_OFFSET` selects a 7-bit ROM register offset.
- `NBIF_STRAP_BIOS_CNTL` gates BIOS-driven strap override behavior, including PCIe ID strap override.
- `DOORBELL0_CTRL_ENTRY_0` through `_20` define doorbell range offset, range size, and fence-enable fields for 21 doorbell apertures.
- `AID*_VF*_BASE_ADDR`, `AID*_XCC*_VF*_BASE_ADDR`, and `AID0_{NBIF,ATHUB,IH,HDP}_VF*_BASE_ADDR` define 16-bit base-address fields for VF0 through part of VF5 across AID, XCC, NBIF, ATHUB, IH, and HDP mapping domains. `AID0_XCC0_VF*` entries in this range use a 17-bit mask (`0x0001FFFF`), while most adjacent base fields use 16-bit masks.

## APIs, Types, And Functions

There are no callable APIs, C types, or functions in this range. The exported interface is the generated macro namespace. Consumers combine these masks and shifts with matching NBIO 7.9.0 register offset/default headers and AMDGPU register-access helpers for MMIO, SMN, PCI configuration, indirect indexed access, or generated field composition/extraction.

The macros encode only field positions. They do not encode reset values, access permissions, firmware ownership, volatility, W1C behavior, reserved-bit policy, ordering requirements, or side effects.

## Control Flow

This header has no local runtime control flow. Runtime use is external and generally follows this pattern:

1. Driver or firmware-facing AMDGPU code selects the appropriate NBIO 7.9.0 register offset for the MSI-X, SUMDEC, strap, reset, doorbell, or VF-base register.
2. It reads a register and extracts fields using the matching `__SHIFT`/`_MASK`, or builds a write value by shifting and masking the desired field.
3. For writable control registers, code usually performs a read-modify-write that preserves unrelated and reserved bits.
4. Hardware applies the actual semantics: interrupt vector delivery and masking, pending-bit reporting, indirect register access, strap-controlled PCIe capability exposure, reset sequencing, interrupt status/masking, D-state acknowledgement, doorbell aperture routing, and VF address decode.

The order in the file follows the generated register database, not an execution order. Repeated field names across status, mask, reset-trigger, and reset-control registers can have different operational semantics even when the bit positions look similar.

## State And Persistence Behavior

The chunk owns no software state and persists nothing. It names hardware state that lives in NBIO/NBIF registers, PCIe configuration decode/shadow registers, strap latches, MSI-X table/PBA state, doorbell routing registers, reset-control registers, and virtualization address decode registers.

Represented hardware state includes:

- Interrupt state: per-vector MSI-X address/data/mask fields, PBA pending bits, reset interrupt status, FLR/D3hot/D-state/PME status, and interrupt masks.
- Strap-derived configuration: identity/class/revision fields, capability enables, link speed and lane equalization capability, BAR/ROM/doorbell/VF aperture sizing, SR-IOV and GPU IOV configuration, ACS/AER/ATS/PRI/PASID exposure, MSI/MSI-X behavior, power-management support, and reset timing defaults.
- Reset state and policy: hard reset enables, self soft reset bits, sticky reset domains, strap reload controls, link reset protection, FLR and D3hot-to-D0 reset routing, auto-clear behavior, grace timers, and reset transaction-idle/dummy-response state.
- Address decode and routing state: doorbell range offsets/sizes/fence enables and VF base addresses across AID/XCC/NBIF/ATHUB/IH/HDP domains.

Persistence is determined by hardware reset domains, strap reload behavior, PCIe function-level reset, D3hot-to-D0 transitions, GPU mode resets, suspend/resume restore, BIOS/firmware initialization, SR-IOV enablement, and explicit driver writes. Strap fields may be sampled from fuses, pins, firmware tables, or BIOS override paths; the shift/mask header does not distinguish immutable sampled straps from writable override registers.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 7.9.0 register-header set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_offset.h` supplies the matching register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_default.h` supplies reset/default values where generated.
- AMDGPU NBIO, PCIe, reset, interrupt, SR-IOV, GPU IOV, doorbell, and VM/HDP/IH/ATHUB code includes the generated NBIO headers and uses the common shift/mask convention through register helper macros.

Practical integration points are GPU platform behavior rather than filesystem behavior: MSI-X setup and masking, interrupt pending diagnostics, PCIe enumeration and capability exposure, root-complex and endpoint personality straps, link training/equalization, AER/ACS policy, ATS/PRI/PASID capability reporting, SR-IOV VF mapping, GPU IOV VSEC reporting, FLR and mode reset handling, D3hot-to-D0 recovery, runtime power management, suspend/resume, doorbell aperture assignment, queue/doorbell fencing, and multi-die/multi-XCC VF address routing.

## Risks And Edge Cases

- The range starts mid-vector-table and ends mid-VF-base-address family. Adjacent chunks must be reconciled before drawing whole-table or whole-family conclusions.
- A wrong MSI-X address/data/mask bitfield can compile cleanly but break interrupt delivery, leave a vector masked, or direct messages to the wrong APIC/interrupt remapping address.
- MSI-X PBA bits are status-like. Treating pending bits as ordinary writable data can lose diagnostics or interact badly with interrupt masking/unmasking.
- Strap fields are capability-defining. Incorrect masks can misadvertise PCIe capabilities such as ACS, AER, ATS, PASID, SR-IOV, DPA, VC, MSI-X, Gen5, or 10-bit tags, which can affect enumeration, IOMMU grouping, passthrough policy, and OS feature enablement.
- Reset fields are operationally sensitive. Misprogramming hard reset, self reset, FLR, sticky reset, strap reload, or D3hot-to-D0 reset controls can hang the GPU, drop PCIe config state, fail to reset VFs, or reset more domains than intended.
- Status and mask register pairs have similar names. Code that accidentally writes a status mask to a status register or vice versa can suppress interrupts or fail to clear/observe reset events.
- D-state target and acknowledgement fields are state-machine interfaces. Polling the wrong field or failing to preserve unrelated bits can make power transitions appear stuck.
- Doorbell range and fence fields affect queue submission routing and ordering. Bad range sizes or offsets can cause queues to ring the wrong engine, expose another function's doorbells, or bypass required fencing.
- VF base-address fields are repeated across AIDs, XCCs, and client blocks. Prefix mix-ups may not be caught at compile time and can route a VF to the wrong die, compute complex, NBIF, ATHUB, IH, or HDP aperture.
- `AID0_XCC0_VF*` fields use a wider 17-bit mask than many neighboring 16-bit base fields. Generic assumptions about base-address field width can truncate values or fail consistency checks.
- BIOS strap override controls can change identity/capability reporting before the OS driver observes the device. Debugging must account for firmware-programmed state, not just static generated defaults.

## Test Signals

- Build AMDGPU configurations that include NBIO 7.9.0 support. Compile failures catch malformed generated symbols or mismatches between generated offset/default headers and shift/mask users.
- Run generated-header consistency checks against the authoritative NBIO 7.9.0 register database: every field should have the expected shift/mask, every register should have a matching offset, and defaults should match where present.
- Validate MSI-X programming on matching hardware: vectors 162-255 should accept message address/data programming, mask/unmask correctly, and report pending status coherently through PBA words.
- Exercise PCIe enumeration and capability decode with `lspci -vv` or equivalent debug output: IDs, class codes, MSI/MSI-X, AER, ACS, ATS, PASID, PRI, SR-IOV, power management, link speed, lane equalization, and vendor-specific GPU IOV capability data should match strap policy.
- Exercise FLR, GPU mode reset, link reset, D3hot-to-D0 transition, runtime suspend/resume, and full device reset paths while checking reset interrupt status/masks, D-state target/ack fields, strap reload behavior, and that unrelated functions/VFs survive when policy says they should.
- Validate SR-IOV enable/disable and VF reset paths: VF counts, VF base mapping, VF doorbell/register/memory aperture sizes, PASID/ATS behavior, and PF/VF reset isolation should match the represented fields.
- Validate doorbell routing under queue creation and teardown: doorbell offsets, aperture sizes, fence-enable fields, and per-function isolation should remain consistent across reset and power transitions.
- Cross-check multi-AID/multi-XCC VF base-address programming on hardware with multiple AIDs or XCCs, especially the wider `AID0_XCC0_VF*` masks.
- Use debugfs/register dumps or firmware diagnostics to compare strap, reset, and doorbell register values before and after BIOS override, driver init, SR-IOV enablement, FLR, suspend/resume, and GPU reset.

### subset-b-003334: lines 17791-20320

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_sh_mask.h lines 17791-20320

## Scope

This chunk covers lines 17791-20320 of AMDGPU's generated NBIO 7.9.0 shift/mask header. It contains C preprocessor constants only. There are no functions, structs, enums, inline helpers, storage objects, allocation paths, locks, or executable control flow in this range.

The range starts in the middle of the `AID0_XCC1_VF5_BASE_ADDR` field definitions, continues through VF5/VF6/VF7 and PF base-address fields, then covers a broad NBIF/BIFC/RCC/BIF_BX1 register-field surface. It ends in the middle of `BIF_BX1_NBIF_GFX_ADDR_LUT_12`, with only the `ADDR` shift visible in this chunk and the matching mask outside the requested line range.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMD GPU driver register metadata. It has no Ceph or distributed-filesystem runtime behavior.

## Purpose

`nbio_7_9_0_sh_mask.h` is the bitfield-layout companion for NBIO 7.9.0 hardware registers. Each generated macro names either:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit position of a field.
- `<REGISTER>__<FIELD>_MASK`: the field mask inside the containing register.

Driver code combines these constants with matching register offsets from `nbio_7_9_0_offset.h` and common AMDGPU register helpers to read, decode, and update NBIO, NBIF, BIFC, RCC, and BIF_BX register state without hard-coded bit numbers.

This chunk is focused on PCIe/NBIO virtualization, doorbell access, DMA/MMIO attribute policy, error logging, power management, virtual-wire triggers, root-complex controls, indirect PCIe/BIF access, scratch registers, reset/interrupt controls, BACO controls, and GFX address lookup-table fields.

## Important Definitions

The opening base-address section names PF/VF routing fields:

- The first line is the trailing mask for `AID0_XCC1_VF5_BASE_ADDR`.
- `AID*_XCC*_VF5_BASE_ADDR`, `AID*_VF6_BASE_ADDR`, `AID*_XCC*_VF6_BASE_ADDR`, `AID*_VF7_BASE_ADDR`, `AID*_XCC*_VF7_BASE_ADDR`, and `AID0_NBIF/ATHUB/IH/HDP_VF*` define base-address field geometry for virtual functions across AID and XCC instances.
- `AID*_PF_BASE_ADDR` and `AID*_XCC*_PF_BASE_ADDR` define the corresponding physical-function base-address fields.
- Most base-address masks are 16-bit (`0x0000FFFFL`); `AID0_XCC0_VF6_BASE_ADDR` and `AID0_XCC0_VF7_BASE_ADDR` use a wider 17-bit mask (`0x0001FFFFL`), which is a field-width detail consumers must preserve.

NBIF/BIFC control and accounting registers include:

- `NBIF_RRMT_CNTL`: partition mode, AID die ID, RRMT enable, and invalid-address high bits.
- `BIFC_DOORBELL_ACCESS_EN_PF` and `BIFC_DOORBELL_ACCESS_EN_VF0` through `VF7`: per-function doorbell access enable masks.
- `MISC_SCRATCH`, `INTR_LINE_POLARITY`, and `INTR_LINE_ENABLE`: scratch and interrupt-line polarity/enable fields.
- `OUTSTANDING_VC_ALLOC`: DMA and host outstanding virtual-channel allocation and threshold fields.
- `BIFC_MISC_CTRL0` and `BIFC_MISC_CTRL1`: control bits for virtual-wire unit ID checking, active vlink behavior, DMA VC status, DMA chain break, host/GSI arbitration, split read stalls, atomic checks, SR-IOV/PF-VF handling, page/PH behavior, reset and ATS-message blocking, PCIe capability protection, D-state/PME behavior, HDP P2P adjustment, FLR/pending controls, ATS/atomic request disable, BME disable, and extended cache/host behavior.
- `BIFC_BME_ERR_LOG_LB`, `BIFC_RCCBIH_BME_ERR_LOG0`, `BIF_ATOMIC_ERR_LOG_DEV0_F0`, `BIF_ATOMIC_ERR_LOG_DEV0_F1`, `BIF_DMA_MP4_ERR_LOG`, and `BIF_PASID_ERR_LOG`: error-log field definitions for bus-master-enable, atomic, DMA, and PASID-related diagnostics.
- `BIF_PASID_ERR_CLR`: control fields to clear PASID error state.
- `BIFC_DMA_ATTR_OVERRIDE_DEV0_F0_F1`, `_F2_F3`, `_F4_F5`, and `_F6_F7`: per-function DMA attribute override fields for no-snoop, RO, ID-based ordering, PASID, ATS, privilege, and related request attributes.
- `BIFC_DMA_ATTR_CNTL2_DEV0`: additional DMA attribute controls for PASID/ATS and default attributes.
- `BME_DUMMY_CNTL_0`, `BIFC_THT_CNTL`, `BIFC_HSTARB_CNTL`, `BIFC_GSI_CNTL`, `BIFC_PCIEFUNC_CNTL`, `BIFC_PASID_CHECK_DIS`, `BIFC_SDP_CNTL_0/1/2`, `BIFC_PASID_STS`, `BIFC_ATHUB_ACT_CNTL`, `BIFC_PGMST_CTRL`, `NBIF_PGMST_CTRL`, `NBIF_PGSLV_CTRL`, and `NBIF_PG_MISC_CTRL`: throttling, host arbitration, GSI/SDP routing, PASID checking/status, ATHUB activity, and NBIF power-gating master/slave policy fields.
- `BIFC_PERF_CNTL_0`, `BIFC_PERF_CNTL_1`, and the low/high halves of MMIO/DMA read/write performance counters: performance counter selection/control and counter-value field geometry.

SMN, self-ring, strap, power, and virtual-wire groups include:

- `SMN_MST_CNTL0/1` and `SMN_MST_EP_CNTL1` through `EP_CNTL5`: SMN master and endpoint controls, including IDs, ordering, timeout, credit, and request behavior fields.
- `BIF_SELFRING_BUFFER_VID` and `BIF_SELFRING_VECTOR_CNTL`: self-ring buffer/vector controls.
- `NBIF_STRAP_WRITE_CTRL`, `NBIF_INTX_DSTATE_MISC_CNTL`, and `NBIF_PENDING_MISC_CNTL`: strap-write and D-state/pending behavior controls.
- `BIF_GMI_WRR_WEIGHT`, `BIF_GMI_WRR_WEIGHT2`, and `BIF_GMI_WRR_WEIGHT3`: weighted round-robin fields for GMI traffic classes.
- `NBIF_PWRBRK_REQUEST`: power-brake request field.
- `NBIF_VWIRE_CTRL`, `NBIF_SMN_VWR_VCHG_DIS_CTRL`, `NBIF_SMN_VWR_VCHG_RST_CTRL0`, `NBIF_SMN_VWR_VCHG_TRIG`, `NBIF_SMN_VWR_WTRIG_CNTL`, `NBIF_SMN_VWR_VCHG_DIS_CTRL_1`, and the matching `NBIF_SDP_VWR_*` controls: virtual-wire value-change disable, reset, trigger, and write-trigger controls for SMN/SDP paths.
- `NBIF_MGCG_CTRL_LCLK` and `NBIF_DS_CTRL_LCLK`: LCLK clock-gating and deep-sleep controls.
- `NBIF_SHUB_TODET_*`: timeout-detection client control/status and sync-flood behavior fields.
- `BIFC_HRP_SDP_WRRSP_POOLCRED_ALLOC`, `BIFC_HRP_SDP_RDRSP_POOLCRED_ALLOC`, `BIFC_GMI_SDP_REQ_POOLCRED_ALLOC`, and `BIFC_GMI_SDP_DAT_POOLCRED_ALLOC`: response/request/data pool-credit allocation fields.
- `DISCON_HYSTERESIS_HEAD_CTRL`, `BIFC_EARLY_WAKEUP_CNTL`, `BIFC_A2S_SDP_PORT_CTRL`, `BIFC_A2S_CNTL_SW0`, `BIFC_A2S_MISC_CNTL`, `BIFC_A2S_TAG_ALLOC_0`, `BIFC_A2S_TAG_ALLOC_1`, and `BIFC_A2S_CNTL_CL0`: disconnect hysteresis, early wakeup, A2S port, tag allocation, and client/software control fields.

The middle of the chunk crosses generated address-block boundaries:

- `addressBlock: aid_nbio_nbif0_rcc_dwn_dev0_BIFDEC1` covers downstream PCIe reserved/scratch/control/config/RX/bus/strap fields.
- `addressBlock: aid_nbio_nbif0_rcc_dwnp_dev0_BIFDEC1` covers downstream-port error, RX, link-speed, link-control, strap, and LTR-message fields.
- `addressBlock: aid_nbio_nbif0_rcc_ep_dev0_BIFDEC1` covers endpoint PCIe scratch/control/interrupt/status/RX/bus/config/TX/LTR, DPA, PME, error, and link-speed fields.
- `addressBlock: aid_nbio_nbif0_rcc_dev0_BIFDEC1` covers root-complex controller error interrupt, BACO/reset, VDM support, lane margining parameters, GPU IOV/host-VM/console IOV, peer register ranges, bus controls, configuration aperture, XDMA, features, bus-number lists, host-bus capture, peer framebuffer offsets, device/function lists, link controls, requester-ID restore, LTR switch, and multi-host arbitration fields.

The closing `BIF_BX1` sections describe the BIF bridge/system decode block:

- `BIF_BX1_PCIE_INDEX`, `PCIE_DATA`, `PCIE_INDEX2`, `PCIE_DATA2`, and high-index registers expose indirect PCIe access fields.
- `BIF_BX1_SBIOS_SCRATCH_*`, `BIF_BX1_BIOS_SCRATCH_*`, `BIF_BX1_DRIVER_SCRATCH_*`, and `BIF_BX1_FW_SCRATCH_*` expose firmware, BIOS, driver, and SBIOS scratch dwords.
- `BIF_BX1_GFX_MMIOREG_CAM_ADDR0` through `ADDR7`, matching `REMAP_ADDR0` through `REMAP_ADDR7`, and CAM completion/control registers define GFX MMIO register remap CAM fields.
- `BIF_BX_PF1_MM_INDEX`, `BIF_BX_PF1_MM_DATA`, and `BIF_BX_PF1_MM_INDEX_HI` define PF1 indirect MMIO index/data fields.
- `BIF_BX1_CC_BIF_BX_STRAP0`, `BIF_BX1_CC_BIF_BX_PINSTRAP0`, `BIF_BX1_BIF_MM_INDACCESS_CNTL`, `BIF_BX1_BUS_CNTL`, `BIF_BX1_BIF_SCRATCH0/1`, `BIF_BX1_BX_RESET_EN`, `BIF_BX1_MM_CFGREGS_CNTL`, `BIF_BX1_BX_RESET_CNTL`, `BIF_BX1_INTERRUPT_CNTL`, `BIF_BX1_INTERRUPT_CNTL2`, and `BIF_BX1_CLKREQB_PAD_CNTL` define strap, bus, reset, interrupt, MMIO-indirect, and clock-request pad controls.
- `BIF_BX1_BIF_FEATURES_CONTROL_MISC`, `BIF_BX1_HDP_ATOMIC_CONTROL_MISC`, `BIF_BX1_BIF_DOORBELL_CNTL`, `BIF_BX1_BIF_DOORBELL_INT_CNTL`, `BIF_BX1_BIF_FB_EN`, `BIF_BX1_BIF_INTR_CNTL`, `BIF_BX1_BIF_MST_TRANS_PENDING_VF`, `BIF_BX1_BIF_SLV_TRANS_PENDING_VF`, `BIF_BX1_BACO_CNTL`, `BIF_BX1_BIF_BACO_EXIT_TIME0`, `BIF_BX1_BIF_BACO_EXIT_TIMER1` through `TIMER4`, and `BIF_BX1_MEM_TYPE_CNTL` define feature gating, HDP atomic outstanding limit, doorbell monitor/interrupt behavior, framebuffer read/write enables, transaction-pending status, BACO entry/exit timers, and memory PHY mode fields.
- `BIF_BX1_NBIF_GFX_ADDR_LUT_CNTL` and `BIF_BX1_NBIF_GFX_ADDR_LUT_0` through the beginning of `_12` define the GFX address LUT enable/mode bits and 24-bit address entries.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The exported interface is the generated macro namespace. Consumers normally pair these symbols with register address macros from `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_offset.h`.

The repository shows direct NBIO 7.9.0 consumers in:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_9.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_nbio_v7_9.c`

Those source files include both `nbio_7_9_0_offset.h` and `nbio_7_9_0_sh_mask.h`, making this header part of the AMDGPU NBIO/RAS register-access ABI for this ASIC generation.

The macros encode only bit geometry. They do not encode reset values, read/write permissions, access width, side effects, sticky/write-one-to-clear behavior, firmware ownership, or sequencing requirements.

## Control Flow

This header contributes no local runtime control flow. Runtime behavior appears at call sites that:

1. Select a matching `reg*` address from `nbio_7_9_0_offset.h`.
2. Read or compose a 32-bit register value through AMDGPU register access helpers.
3. Use the `__SHIFT` and `_MASK` macros to extract, set, preserve, or clear a field.
4. Let hardware apply the NBIO/BIFC/RCC/BIF_BX side effect, such as changing access policy, recording status, gating traffic, enabling interrupts, controlling BACO, or steering address decode.

The order in this generated file is a register-database order, not an execution sequence. Address-block comments mark hardware decode regions rather than software control-flow boundaries.

## State And Persistence Behavior

The file stores no software state and persists nothing. It names state that lives in NBIO 7.9.0 hardware registers and related PCIe/root-complex decode blocks.

Represented state includes:

- PF/VF/AID/XCC base-address state for virtualization and per-function register aperture routing.
- Doorbell access-enable state for PF and VF0-VF7, plus BIF_BX1 doorbell monitor and interrupt status/clear/disable bits.
- NBIF partition/RRMT state, invalid-address high bits, and AID die identity fields.
- DMA/MMIO request policy state: no-snoop, relaxed ordering, PASID, ATS, privilege, ID-based ordering, attribute override, and outstanding virtual-channel allocation.
- Error and diagnostic state: BME error logs, RCCBIH BME logs, atomic error logs, DMA/PASID error logs and clears, timeout-detection status, transaction-pending status, interrupt status, and scratch registers.
- Power/reset/clock state: NBIF power-gating master/slave controls, LCLK MGCG/deep-sleep controls, D-state/PME controls, reset enables, BACO control and exit timers, clock-request pad controls, early wakeup, and disconnect hysteresis.
- Root-complex and PCIe decode state: downstream, downstream-port, endpoint, and root-complex controller fields for RX/TX, link speed, link control, error handling, LTR, DPA, PME, VDM, bus numbers, requester ID, peer FB offsets, XDMA, console IOV, GPU IOV, and host-VM behavior.
- BIF_BX1 indirect access, scratch, GFX MMIO CAM/remap, MM index/data, framebuffer enable, interrupt, BACO, and GFX address LUT state.

Persistence of these hardware fields is governed by GPU reset domains, PCIe/function-level reset, BACO entry/exit, runtime power management, firmware/SBIOS initialization, driver reinitialization, and explicit writes. This header does not tell callers which fields survive which reset or power transition.

## Dependencies And Integration Points

The primary dependency is the matching generated offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_offset.h`

This repository does not show a sibling `nbio_7_9_0_default.h` in the same directory, so reset/default metadata may be absent or supplied through another generated source for this ASIC family.

Integration points include:

- AMDGPU NBIO 7.9 initialization and runtime code in `amdgpu/nbio_v7_9.c`.
- AMDGPU RAS NBIO 7.9 code in `ras/ras_mgr/amdgpu_ras_nbio_v7_9.c`, which can decode or program RAS/error-reporting registers using these symbols.
- Common AMDGPU register helper macros that expect generated `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` naming.
- PCIe/SR-IOV and virtualization paths that rely on PF/VF base-address, doorbell, PASID, ATS, host-VM, console-IOV, and register-write/access-control fields.
- Power-management and reset paths that touch NBIF power gating, D-state/PME, BACO, LCLK gating, reset enables, and transaction-pending fields.
- Diagnostics, RAS, and recovery paths that decode BME, atomic, DMA, PASID, timeout, interrupt, and transaction-pending status.
- Firmware/SBIOS/driver coordination via scratch registers and strap/pinstrap fields.
- GFX/MMIO routing and debug paths that program indirect PCIE/MMIO access, GFX MMIO CAM entries, and the NBIF GFX address LUT.

## Risks And Edge Cases

- The chunk starts and ends inside register definitions. `AID0_XCC1_VF5_BASE_ADDR` is missing its comment and shift in this range, while `BIF_BX1_NBIF_GFX_ADDR_LUT_12` is missing its mask. The final merge pass must reconcile adjacent chunks before treating those registers as complete.
- A wrong mask or shift can compile cleanly while targeting adjacent hardware bits. For this chunk, the blast radius includes PF/VF routing, doorbell permissions, DMA attributes, interrupt state, power management, reset behavior, PCIe link/root-complex controls, and error reporting.
- Similar PF/VF/AID/XCC names are easy to confuse. Some fields differ subtly in width, such as 17-bit `AID0_XCC0_VF6/VF7_BASE_ADDR` masks versus mostly 16-bit base-address masks.
- Doorbell access and BIF doorbell interrupt fields affect isolation and event delivery. Incorrect enable/disable/clear handling can expose doorbells to the wrong function, lose interrupts, or create spurious interrupt status.
- Status and clear registers may be write-one-to-clear or otherwise write-sensitive. The availability of a mask does not imply a generic read-modify-write is safe for PASID errors, BME errors, atomic errors, interrupt status, timeout status, or transaction-pending diagnostics.
- DMA attribute override fields can change ordering, snooping, PASID, ATS, and privilege semantics. Misprogramming can break coherency, IOMMU translations, virtualization isolation, or peer-to-peer DMA assumptions.
- NBIF power gating, LCLK gating, D-state, BACO, reset, and pending-transaction fields require sequencing with active traffic. Changing them without draining or checking pending state can hang, drop requests, or corrupt recovery.
- Root-complex and endpoint PCIe fields include link speed/control, requester ID, bus numbers, peer FB offsets, XDMA, and LTR behavior. Copying field names across ASICs or address blocks can target the wrong port or root-complex instance.
- Scratch registers are shared coordination surfaces. Their presence in the mask header does not establish ownership between firmware, SBIOS, driver, and diagnostics.
- The header is generated hardware metadata. Manual edits should be treated as high risk unless regenerated from the authoritative register database and checked against matching offsets.

## Test Signals

Useful verification signals for this chunk are mostly compile-time, generated-header consistency, and hardware runtime checks:

- Build AMDGPU configurations that include NBIO 7.9.0 support. Compile failures catch malformed macro names and missing offset/mask users.
- Run generated-header consistency checks: every complete field in this chunk should have both a `__SHIFT` and `_MASK`, masks should align with their shifts, and every named register should have a matching `reg*` entry in `nbio_7_9_0_offset.h`.
- Explicitly account for boundary exceptions: `AID0_XCC1_VF5_BASE_ADDR` is partial at the start and `BIF_BX1_NBIF_GFX_ADDR_LUT_12` is partial at the end.
- Compare repeated register families against the authoritative NBIO 7.9.0 register database: PF/VF base-address matrices, `BIFC_DMA_ATTR_OVERRIDE_DEV0_F*` groups, virtual-wire SMN/SDP groups, `RCC_*` address blocks, scratch-register sequences, GFX CAM entries, and GFX address LUT entries should be structurally consistent where expected.
- Boot and probe matching hardware to exercise NBIO 7.9 register access through `nbio_v7_9.c`.
- Exercise SR-IOV or virtualization configurations if available: PF/VF base apertures, doorbell access, PASID/ATS behavior, host-VM/console-IOV settings, and isolation should match expectations.
- Exercise interrupts, RAS, and recovery: doorbell interrupt status/clear/disable behavior, BME/atomic/DMA/PASID error logging, timeout detection, sync-flood policy, and RAS NBIO decoding should report coherent fields.
- Exercise suspend/resume, BACO entry/exit, runtime power management, GPU reset, and function-level reset to verify that power, reset, pending, scratch, and restore-sensitive fields are initialized or restored correctly.
- Validate PCIe link/root-complex behavior on supported platforms: bus numbers, requester ID, LTR, DPA/PME, link speed/control, peer FB offsets, XDMA, and error-control fields should remain coherent after enumeration and recovery.

### subset-b-003335: lines 20321-22702

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_sh_mask.h lines 20321-22702

## Scope

This chunk covers lines 20321-22702 of AMDGPU's generated NBIO 7.9.0 shift/mask header. It contains C preprocessor constants only: no functions, structs, enums, storage, allocation, locking, or direct register accesses.

The range begins at the tail of the `BIF_BX1_NBIF_GFX_ADDR_LUT_*` group, continues through BIF/PF virtualization and mailbox fields, RCC strap fields, SION/GDC doorbell and arbitration controls, SHUB reset controls, SysHub/NIC400 QoS fields, and ends inside the `NB_SPARE2` register of the NB misc block. The requested slice defines 2,167 macros, almost evenly split between `__SHIFT` constants and `_MASK` constants.

Although this repository path is under a `ceph-client` source-tree mirror, this file is AMD GPU NBIO register metadata. It does not implement distributed-filesystem behavior.

## Purpose

`nbio_7_9_0_sh_mask.h` is the bitfield-layout companion for the NBIO 7.9.0 register map. Each generated macro describes where a named hardware field lives inside a 32-bit register:

- `REGISTER__FIELD__SHIFT` gives the least-significant bit position.
- `REGISTER__FIELD_MASK` gives the raw unshifted mask for that field.

Driver code combines these constants with the matching NBIO 7.9.0 register-offset header and AMDGPU register helpers to extract status bits, compose read/modify/write values, and decode debug dumps. This chunk is centered on NBIF/BIF virtualization surfaces, PCIe/function straps, GPU doorbell routing, GDC/SION traffic controls, SHUB reset domains, SysHub/NIC400 QoS controls, and a small NB misc tail.

## Register Families

The opening `BIF_BX1` section finishes graphics address LUT entries 13-15, then defines virtual-function gating and status bitmaps:

- `BIF_BX1_VF_REGWR_EN`, `BIF_BX1_VF_DOORBELL_EN`, and `BIF_BX1_VF_FB_EN` expose per-VF enables for register writes, doorbells, and framebuffer access across VF0-VF30.
- Matching `BIF_BX1_VF_REGWR_STATUS`, `BIF_BX1_VF_DOORBELL_STATUS`, and `BIF_BX1_VF_FB_STATUS` expose per-VF status bits.
- `BIF_BX1_REMAP_HDP_*_FLUSH_CNTL`, `BIF_BX1_BIF_RB_*`, `BIF_BX1_MAILBOX_INDEX`, `BIF_BX1_BIF_MP1_INTR_CTRL`, pad controls, and VCN GPUIOV config-size fields support BIF ring-buffer, mailbox, interrupt, pad, and virtualization configuration plumbing.

The `addressBlock: aid_nbio_nbif0_bif_bx_pf_BIFPFVFDEC1` section defines PF1-oriented control/status fields:

- BME and atomic error log fields, including clear bits for DMA-on-BME-low and unsupported atomic request conditions.
- Doorbell self-ring GPA aperture base and control fields.
- HDP register/memory coherency flush and invalidate controls.
- `GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE` bitmaps for CP0-CP9, SDMA0-1, and reserved engine bits.
- Transaction-pending, address-LUT bypass, transmit/receive mailbox data words, mailbox valid/ack controls, mailbox interrupt enables, and VM/HV mailbox fields.
- Compute and memory partition capability/status fields, including SPX/DPX/TPX/QPX/CPX support and NPS1/NPS2/NPS3/NPS4/NPS6/NPS8 support.

The `addressBlock: aid_nbio_nbif0_rcc_strap_BIFDEC1:1` section is a large strap decode block:

- `RCC_BIF_STRAP0-6` describe global BIF/PCIe feature straps: Gen3/Gen4/Gen5 disable/kill controls, VGA/BIOS ROM/memory aperture pins, error-ignore policy, margining, DLF/16GT, SWUS aperture behavior, power/link timers, power-brake behavior, emergency power reduction, and link-down reset behavior.
- `RCC_DEV0_PORT_STRAP*` describes device-0 port capabilities and policy such as port presence, bifurcation or link sizing, ASPM/LTR/PM behavior, reset behavior, MSI/MSI-X or AER-related capabilities, peer-to-peer/security policy, and link/power-management knobs.
- `RCC_DEV0_EPF0_STRAP*` and `RCC_DEV0_EPF1_STRAP*` describe endpoint function straps for function 0 and function 1: device/revision IDs, function enablement, D-state support, PASID capability, AER/ACS/VC/DPA/FLR/atomic/PME support, MSI/MSI-X capabilities, subsystem IDs, aperture sizes, SR-IOV VF mapping and aperture sizing, BAR/ROM/VGA controls, resize-BAR, clock/power management, and GPUIOV VSEC revision.
- Several empty strap comments, such as `EPF1_STRAP20-25` and `EPF1_STRAP7`, mark generated register names that have no fields in this slice.

The SION/GDC sections describe doorbell routing and NBIF-to-GDC traffic behavior:

- `S2A_DOORBELL_ENTRY_0_CTRL` through `_15_CTRL` repeat a per-port layout: enable, AWID, fence enable, range offset, range size, 64-bit support disable, range-offset deduction, and AWADDR high nibble value.
- `S2A_DOORBELL_COMMON_CTRL_REG` provides a common doorbell control bit for the SION block.
- `GDC1_A2S_CNTL_CL0/CL1`, `GDC1_A2S_CNTL3_CL0/CL1`, and `GDC1_A2S_CNTL_SW0/SW1/SW2` define A2S client arbitration, outstanding-request, QoS, ordering, and reset-related controls.
- `GDC1_A2S_TAG_ALLOC_*`, `GDC1_A2S_MISC_CNTL`, `GDC1_SHUB_REGS_IF_CTL`, `GDC1_NGDC_MGCG_CTRL`, `GDC1_ATDMA_MISC_CNTL`, and `GDC1_S2A_MISC_CNTL` describe tag allocation, miscellaneous ordering/arbitration, SHUB register-interface behavior, clock gating, ATDMA WRR weights, and S2A response behavior.
- `GDC1_NBIF_GFX_DOORBELL_STATUS` and `XCC_DOORBELL_FENCE` expose doorbell-sent/fence state for graphics, XCCs, CP engines, and remote clients.
- `GDC1_NGDC_EARLY_WAKEUP_CTRL`, `GDC1_NGDC_PG_MISC_CTRL`, `GDC1_NGDC_PGMST_CTRL`, and `GDC1_NGDC_PGSLV_CTRL` describe early-wakeup and power-gating hysteresis/enable behavior.

The reset and SysHub/NIC400 tail provides reset-domain and interconnect QoS fields:

- `SHUB_PF_FLR_RST`, `SHUB_GFX_DRV_VPU_RST`, `SHUB_LINK_RESET`, `SHUB_HARD_RST_CTRL`, `SHUB_SOFT_RST_CTRL`, and `SHUB_SDP_PORT_RST` expose PF FLR, link, hard/soft, NIC400, SION, and SDP-port reset bits.
- `HST_CLK0_*_CNTL` and `DMA_CLK0_*_CNTL` configure FLR/link-reset response and, for DMA clients, static QoS override and read/write WRR weights.
- `NIC400_*_FN_MOD`, `NIC400_2_ASIB_*_QOS_CNTL`, `MAX_OT`, `MAX_COMB_OT`, AW/AR rate parameters, target latency, KI flow-control latency, and QoS range fields expose ARM NIC400 interconnect read/write override, outstanding transaction, rate/flow-control, latency, and QoS tuning.
- `NB_NBCFG0_NBCFG_SCRATCH_4`, `NB_CNTL`, `NB_SPARE1`, and the first part of `NB_SPARE2` provide NB scratch, hardware-initialization write-lock, spare RW, and spare RW1C bit definitions. The chunk ends before all `NB_SPARE2` mask lines are included.

## Important APIs, Types, and Functions

There are no callable APIs, C types, or functions in this chunk. The exported interface is the generated macro namespace, and each symbol is meaningful only when paired with the matching NBIO 7.9.0 register address definitions.

Important macro categories are:

- Per-field geometry macros for register helpers: `*_SHIFT` and `*_MASK`.
- Per-VF bitmaps for VF0-VF30 enable/status controls.
- Per-engine bitmaps for CP, SDMA, reserved engines, XCCs, remote clients, and SHUB reset ports.
- Per-doorbell-port definitions repeated for 16 S2A doorbell entries.
- Strap fields that describe hardware fuse/ROM strap inputs, policy overrides, and capability exposure.
- QoS and arbitration fields for GDC, ATDMA, SysHub, DMA clients, and NIC400 interfaces.

Typical consumers use these macros through AMDGPU helpers such as field extract/set macros and SOC15/NBIO register accessors. The companion address/default headers provide offsets and reset values; this file only supplies bit positions and masks.

## Control Flow and Data Flow

This header has no local control flow. Runtime use is indirect:

1. AMDGPU code chooses an NBIO 7.9.0 register offset from the generated address header.
2. The driver reads or constructs a 32-bit register value.
3. A field helper uses the `__SHIFT` and `_MASK` macro for the named field.
4. The driver decodes hardware state or writes a preserved read/modify/write value.
5. Hardware applies the field semantics in the relevant BIF, PF/VF, GDC, SION, SHUB, SysHub, NIC400, or NB domain.

The ordering in the header follows the generated register database, not an execution sequence. For example, a reset flow might use SHUB reset bits before polling transaction-pending or HDP flush-done status, but this file only declares the bit layouts. Similarly, mailbox message buffers and valid/ack bits imply a producer/consumer handshake, but the handshake policy is implemented by external driver and firmware code.

## State and Persistence Behavior

The chunk stores no software state and persists nothing in files or memory. The represented state lives in hardware registers:

- Virtualization state: VF register-write, doorbell, and framebuffer enable/status bitmaps; SR-IOV and VF aperture/mapping strap fields; GPUIOV config-size and VSEC strap fields.
- Addressing and aperture state: graphics address LUT entries, doorbell self-ring GPA aperture base/control, BAR/ROM/memory/register aperture strap sizing, SWUS aperture fields, and NB scratch/spare registers.
- Flush and coherency state: HDP flush request/done bits, coherency flush/invalidate controls, and transaction-pending bits.
- Mailbox state: transmit/receive message buffers, valid/ack bits, interrupt enables, VM/HV mailbox data and valid/ack flags.
- Capability and policy state: fuse/ROM strap validity, PCIe generation disable/kill straps, AER/ACS/VC/DPA/PASID/FLR/atomic/PME/MSI/MSI-X/resize-BAR/DOE support straps, D-state support, LTR/ASPM behavior, and error-ignore policy.
- Doorbell and fence state: S2A per-port range routing, fence enables, XCC/CP/remote-client fence state, and NBIF graphics doorbell sent status.
- Interconnect and QoS state: GDC A2S/S2A arbitration, tag allocation, outstanding transaction controls, WRR weights, QoS ranges, target latencies, and NIC400 rate/flow-control settings.
- Reset and power state: PF FLR, link resets, SHUB hard/soft reset enables, SDP port resets, early wakeup controls, clock gating, and NGDC power-gating hysteresis/enable bits.

Persistence follows hardware reset and power-domain rules. Some strap-derived values are sampled from fuse/ROM/pins and should be treated as firmware or hardware-owned. Some status and spare bits are write-one-to-clear or sticky. Reset bits can immediately affect live hardware state and may clear or reinitialize other registers in this same slice.

## Dependencies and Integration Points

This chunk depends on the generated AMDGPU NBIO 7.9.0 register header set staying synchronized:

- The matching `nbio_7_9_0_d.h` or offset/address header supplies register addresses.
- Optional generated default headers supply reset/default values where available.
- AMDGPU register helpers require the generated naming convention to stay stable.
- ASIC/IP-version selection code must include this header only for hardware whose NBIO layout matches version 7.9.0.

Practical integration points include:

- AMDGPU NBIO initialization and reset paths.
- PCIe/BIF link and endpoint policy derived from RCC straps.
- SR-IOV/GPUIOV virtualization setup, VF aperture programming, and VF access gating.
- Doorbell routing for graphics, CP, SDMA, XCC, remote clients, and S2A ports.
- HDP flush/coherency paths used before CPU/GPU-visible memory synchronization.
- Firmware or hypervisor mailbox flows using PF1 and VM/HV mailbox registers.
- GPU partition discovery for compute partition modes and memory/NPS modes.
- GDC/SION arbitration, power gating, clock gating, and early-wakeup tuning.
- SHUB reset recovery, FLR handling, link reset handling, and SDP port reset flows.
- SysHub/NIC400 QoS and outstanding-transaction tuning for host and DMA traffic.
- Register dump and diagnostics code that decodes NBIO 7.9.0 fields for supportability.

## Risks and Edge Cases

- This chunk starts and ends mid-family. LUT entry 12 begins before the range, and `NB_SPARE2` masks continue after the range. The final per-file reconciliation should merge adjacent chunks before making whole-register claims.
- Generated mask/shift drift can compile cleanly while changing hardware behavior. High-impact fields include VF access gating, doorbell aperture/range programming, HDP flush bits, mailbox valid/ack bits, reset enables, strap-derived capability exposure, and NIC400 QoS controls.
- Per-VF and per-engine bitmaps are repetitive. A single misplaced bit can affect only one VF, CP engine, XCC, SDMA path, or SDP port, making failures dependent on partitioning, virtualization, or traffic pattern.
- Doorbell ranges and fence controls are security-sensitive in virtualized environments. Wrong ranges, sizes, AWIDs, or address high bits can route doorbells to the wrong client or expose VF/PF interactions.
- HDP flush request/done fields require ordering and polling discipline outside this header. Treating request/done masks as ordinary writable state can cause stale CPU/GPU memory visibility or false completion.
- Mailbox valid/ack fields imply handshakes with firmware or a hypervisor. Incorrect clear/set ordering can lose messages, wedge notification state, or generate interrupt storms.
- Strap fields describe sampled hardware policy, not necessarily writable runtime configuration. Driver code should not assume a strap mask is safe to change after initialization.
- Reset controls can affect broad domains such as SHUB, NIC400, SION, SDP ports, and links. Incorrect read/modify/write behavior can reset active paths or leave dependent state inconsistent.
- Several fields appear to be sticky, clear-on-write, or write-one-to-clear by name, such as clear bits and `RW1C` spare bits. Generic writes may destroy diagnostic evidence.
- NIC400 and GDC QoS tuning can produce performance or deadlock-like symptoms without obvious correctness failures if outstanding-transaction, latency, WRR, or QoS-range masks are wrong.
- Empty generated strap comments should not be mistaken for missing implementation bugs in this chunk; they may represent reserved registers or fields defined outside the requested range.

## Test and Validation Signals

Validation is indirect because this file is compile-time metadata:

- Build AMDGPU configurations that include NBIO 7.9.0 support. Missing, renamed, or malformed field symbols should fail at consumer call sites.
- Run generated-header consistency checks against the authoritative NBIO 7.9.0 register database: every field should have the expected shift and mask, and every field-bearing register should have a matching address definition.
- Compare NBIO 7.9.0 register dumps from matching hardware against decoded VF enable/status, BIF ring-buffer, mailbox, partition, doorbell, GDC, SHUB, SysHub, NIC400, and NB misc fields.
- Exercise SR-IOV/GPUIOV scenarios with multiple VFs: VF register-write, doorbell, framebuffer, VF aperture size, VF mapping mode, and VF MSI capability bits should decode and behave as expected.
- Test doorbell delivery and fencing for CP/SDMA/XCC/remote clients and S2A ports, including 64-bit doorbells, range-offset deduction, range sizing, and fence-sent/clear-pending state.
- Exercise HDP flush/coherency paths under CPU/GPU memory synchronization workloads and confirm request/done bits progress for CP and SDMA engines.
- Validate PF1 and VM/HV mailbox handshakes under firmware/hypervisor interactions: message data, valid/ack bits, and interrupt enables should transition coherently.
- Test GPU reset, FLR, link reset, suspend/resume, and power-gating transitions while checking SHUB reset bits, transaction-pending status, GDC early wakeup, NGDC power-gating controls, and restored QoS settings.
- Cross-check strap-derived capability reporting against PCI config-space observations: AER, ACS, VC, PASID, MSI/MSI-X, FLR, atomic ops, resize-BAR, D-states, PME, Gen3/Gen4/Gen5, DLF, and 16GT support should match platform expectations.
- Run performance or stress tests that exercise host and DMA traffic while observing NIC400/GDC QoS, outstanding transaction, WRR weight, and latency fields for unexpected throttling or starvation.

### subset-b-003336: lines 22703-25135

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_sh_mask.h lines 22703-25135

## Scope

This chunk covers lines 22703-25135 of AMDGPU's generated NBIO 7.9.0 shift/mask header. It contains C preprocessor constants only: no functions, structs, variables, allocation, locking, or direct register I/O. The range starts in the middle of `NB_SPARE2`, covers most of the `aid_nbio_iohub_nb_misc_misc_cfgdec` register field map, and then begins `aid_nbio_iohub_nb_rascfg_ras_cfgdec` through the first fields of `PARITY_ERROR_STATUS_UNCORR_GRP14`.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMD GPU NBIO register metadata. It has no Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_9_0_sh_mask.h` is the bitfield-definition companion for NBIO 7.9.0 registers. Each generated field exposes:

- `REGISTER__FIELD__SHIFT`: the least-significant bit index of the field.
- `REGISTER__FIELD_MASK`: the raw mask for the field in the containing register.

Driver code combines these macros with matching offsets from `nbio_7_9_0_offset.h` and AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15*`, and `WREG32_SOC15*`. The chunk's definitions describe northbridge configuration, memory window, software interrupt, VDM/MCTP routing, debug trap, bridge configuration, MCA interrupt, and RAS parity status fields.

## Important Register Families

The opening range completes `NB_SPARE2`, a 32-bit write-one-to-clear-style spare register family named `NB_SPARE2_RW1C_0` through `_31`. The chunk starts at bit 6, so the full register's shift list begins in the previous chunk. Its masks still cover every bit from `0x00000001L` through `0x80000000L`.

The NB miscellaneous configuration fields include:

- Identification and clock state: `NB_REVID` exposes a 10-bit `REVISION_ID`, and `NBIO_LCLK_DS_MASK` exposes a full-width LCLK deep-sleep mask.
- Bus and memory topology: `NB_BUS_NUM_CNTL` carries bus number, bus-latency mode, and segment fields; `NB_MMIOBASE` and `NB_MMIOLIMIT` are full-width MMIO aperture registers; `NB_LOWER_TOP_OF_DRAM2`, `NB_UPPER_TOP_OF_DRAM2`, `NB_LOWER_DRAM2_BASE`, `NB_UPPER_DRAM2_BASE`, `NB_TOP_OF_DRAM3`, and `NB_DRAM3_BASE` describe DRAM aperture boundaries and enables.
- Location and remap fields: `SB_LOCATION` and `SW_US_LOCATION` hold port/core locations; `NB_PROG_DEVICE_REMAP_PBr0` through `PBr8` and `PBr10` through `PBr13` expose 8-bit programmed device/function remap values.
- Software interrupt/status controls: `SW_NMI_CNTL`, `SW_SMI_CNTL`, and `SW_SCI_CNTL` are full-width software status registers; `APML_SW_STATUS` exposes `APML_NMI_STATUS`; `SW_GIC_SPI_CNTL` maps software NMI/SMI/SCI GIC SPI vectors; `SW_SYNCFLOOD_CNTL` exposes private and APML sync-flood request bits.

The CAM and dropped-DMA sections define debugging/diagnostic surfaces:

- `CAM_CONTROL` has enable, operation, access type, data-match enable, virtual channel, and cross-trigger fields.
- `CAM_TARGET_*` registers define index/data and address/data comparison values plus masks.
- `P_DMA_DROPPED_LOG_LOWER`, `P_DMA_DROPPED_LOG_UPPER`, `NP_DMA_DROPPED_LOG_LOWER`, and `NP_DMA_DROPPED_LOG_UPPER` are repeated 32-bit bitmaps for posted and non-posted dropped-DMA logging.

The PCIe VDM and stall-control fields include:

- `PCIE_VDM_NODE0_CTRL4` bus range base/limit and node-present fields.
- `PCIE_VDM_CNTL2` controls VDM peer-to-peer mode, MCTP endpoint/multisegment enablement, routing to SMU, route-all-to-MCTP-master policy, MCTP master segment, and MCTP master ID.
- `PCIE_VDM_CNTL3` exposes APMTP master valid and ID fields.
- `STALL_CONTROL_XBARPORT0_0` through `STALL_CONTROL_XBARPORT5_1` repeat request/response stall-enable fields for virtual channels 0, 1, 2, 3, 4, 5, and 7 on crossbar ports 0-5. Each VC field is a two-bit slot spaced on four-bit boundaries.

The PSP/SMU and trap sections are broad:

- `PSP_BASE_ADDR_LO/HI` and `SMU_BASE_ADDR_LO/HI` define low/high base-address fields, with low halves shifted by bit 16.
- `SCRATCH_4`, `SCRATCH_5`, `SMU_BLOCK_CPU`, and `SMU_BLOCK_CPU_STATUS` are full-width scratch/blocking/status surfaces.
- `TRAP_STATUS` reports trap request validity, trap number, stage-2 validity, and stage-2 number.
- `TRAP_REQUEST0` through `TRAP_REQUEST5`, `TRAP_REQUEST_DATASTRB0/1`, and `TRAP_REQUEST_DATA0` through `DATA15` expose captured trap request address, command, attributes, length, VC, block-level, chain, I/O, pass-posted-write flags, unit ID, security level, data VC/error/parity, byte enables, and payload data.
- `TRAP_RESPONSE_CONTROL`, `TRAP_RESPONSE0`, and `TRAP_RESPONSE_DATA0` through `DATA15` define response trigger/passthrough controls, response status, data status, and read-response payload fields.
- `TRAP0_*` through `TRAP15_*` define 16 configurable trap comparators. Each comparator has `CONTROL0` fields for enable, SMU interrupt, stage-2 pointer, cross-trigger, and stage-2 enable; address low/high match fields; command match fields; address masks; and command masks.

The SB bridge/MCA section maps PCI bridge-like and interrupt-routing fields:

- `SB_COMMAND`, `SB_SUB_BUS_NUMBER_LATENCY`, `SB_IO_BASE_LIMIT`, `SB_MEM_BASE_LIMIT`, `SB_PREF_BASE_LIMIT`, `SB_PREF_BASE_UPPER`, `SB_PREF_LIMIT_UPPER`, and `SB_IO_BASE_LIMIT_HI` describe I/O/memory/bus-master enables and bridge decode windows.
- `SB_IRQ_BRIDGE_CNTL`, `SB_EXT_BRIDGE_CNTL`, `SB_PMI_STATUS_CNTL`, `SB_SLOT_CAP`, `SB_ROOT_CNTL`, and `SB_DEVICE_CNTL2` expose ISA/VGA decode controls, port-80 enablement, power state, slot power limit, CRS visibility, and ARI forwarding.
- `MCA_SMN_INT_REQ_ADDR`, `MCA_SMN_INT_MCM_ADDR`, `MCA_SMN_INT_APERTUREID`, and `MCA_SMN_INT_CONTROL` define SMN interrupt target/request address fields and MCA cross-trigger control.

The RAS configuration block begins at line 24180:

- `PARITY_CONTROL_0` contains corrected and uncorrected-poison threshold fields.
- `PARITY_CONTROL_1` contains parity error injection controls: group selection, group type, ID, command, trigger, and inject-allow.
- `PARITY_SEVERITY_CONTROL_UNCORR_0`, `PARITY_SEVERITY_CONTROL_CORR_0`, and `PARITY_SEVERITY_CONTROL_UCP_0` assign two-bit severity values per group. Uncorrectable and corrected variants cover groups 0-15; UCP covers groups 0-12 in this chunk.
- `RAS_GLOBAL_STATUS_LO` reports global parity, SERR, hotplug wake alarm, software NMI/SMI/SCI, APML NMI, and sync-flood state.
- `RAS_GLOBAL_STATUS_HI` reports PCIe and NBIF port error bits.
- `PARITY_ERROR_STATUS_UNCORR_GRP0` through `GRP13` are complete 32-bit per-ID uncorrectable parity status bitmaps. The chunk ends inside `PARITY_ERROR_STATUS_UNCORR_GRP14`, after shifts and masks through bit 17; the remainder belongs to the next chunk.

## APIs, Types, And Functions

There are no callable APIs, types, or functions in this range. The exported surface is the generated macro namespace. Direct NBIO 7.9.0 in-tree consumers include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_9.c`, which includes the matching offset and shift/mask headers for NBIO setup paths.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_nbio_v7_9.c`, which includes these headers while registering NBIF RAS interrupt source IDs.

The current `amdgpu_ras_nbio_v7_9.c` implementation registers RAS controller and ATHUB error-event interrupts but leaves their process callbacks as dummy paths because the BIF-ring hardware path is disabled. That means many RAS macros in this chunk are available for decode/injection support, register dumps, or future paths, but this file does not currently perform active parity-status decoding with them.

## Control Flow

This header has no runtime control flow. Runtime use follows the standard generated-register pattern:

1. Driver code selects an NBIO 7.9.0 register offset from `nbio_7_9_0_offset.h`.
2. It reads a raw register value through the SOC15 MMIO/SMN/indirect access path appropriate for NBIO.
3. It decodes a field with the corresponding `_MASK` and `__SHIFT`, or composes a write value with `REG_SET_FIELD`.
4. Hardware applies the actual semantics: bus/memory window programming, software interrupt signaling, sync-flood generation, dropped-DMA logging, VDM/MCTP routing, crossbar stalling, trap matching, bridge decode, MCA interrupt triggering, or RAS parity reporting.

The order in this generated header follows the register database and address blocks, not an execution sequence.

## State And Persistence Behavior

The chunk stores no software state and persists nothing. It names fields whose state lives in NBIO hardware registers, PCI bridge/configuration decode registers, and RAS status/control registers. Persistence depends on the specific hardware reset domain, firmware initialization, GPU reset, function-level reset, power transitions, and explicit driver writes.

Represented hardware state includes:

- Configuration state: bus number/segment selection, MMIO/DRAM windows, programmed device remaps, VDM routing, stall controls, PSP/SMU base addresses, trap comparator configuration, SB bridge windows, slot/root/device controls, MCA interrupt targets, and parity severity/injection controls.
- Status and diagnostic state: revision ID, software NMI/SMI/SCI/APML status, dropped-DMA bitmaps, trap request/response captures, SMU block status, RAS global status, and parity error status groups.
- Request/side-effect state: software sync-flood bits, trap response trigger, parity error generation trigger, MCA cross-trigger, and possibly write-one-to-clear or sticky status bits.

The macros do not encode read/write permissions, write-one-to-clear behavior, reset values, volatility, reserved-bit rules, posted-write ordering, or whether a read/write has side effects. Callers must rely on ASIC documentation and local driver conventions for those semantics.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 7.9.0 header set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_offset.h` supplies matching register addresses and base indices.
- Other generated NBIO 7.9.0 headers, where present, provide reset/default values and adjacent register-family definitions.
- AMDGPU SOC15 register helper macros provide the extraction, composition, and access mechanisms that make these masks useful.

Practical integration points include GPU/NBIO initialization, memory aperture setup, PCIe bridge/resource decode, software interrupt delivery, APML and GIC SPI routing, VDM/MCTP control, SMU/PSP mailbox or base-address programming, diagnostics for dropped DMA and traps, MCA/SMN interrupt routing, RAS interrupt registration, parity severity/error injection, and debug register dumps.

## Risks And Edge Cases

- The chunk starts and ends mid-family. `NB_SPARE2` begins before line 22703, and `PARITY_ERROR_STATUS_UNCORR_GRP14` continues after line 25135. The later merge step must reconcile adjacent chunks before making whole-register claims.
- A generated shift/mask drift can compile cleanly while decoding or writing the wrong hardware bit. This is especially risky in repeated 32-bit bitmap families such as dropped-DMA logs and parity error status groups.
- Status, trigger, request, and clear registers are not distinguished by macro shape. Generic read-modify-write code can accidentally clear sticky diagnostics, trigger sync-flood/trap/parity injection, or preserve stale status if the field semantics are not checked.
- NB bus/MMIO/DRAM and SB bridge-window fields affect host-visible address decode. Incorrect values can break enumeration, memory routing, peer access, or MMIO isolation.
- VDM/MCTP routing fields can redirect vendor-defined messages to SMU or MCTP master paths. Wrong master segment/ID or route-all policy can affect platform management traffic.
- Crossbar stall controls and trap comparators are debug-sensitive. Enabling them on live systems without a narrow policy can stall traffic, redirect errors, interrupt SMU unexpectedly, or perturb timing-sensitive paths.
- PSP/SMU base-address fields and SMU block controls are firmware-facing. Incorrect masks or stale writes can interfere with firmware communication and CPU/SMU arbitration.
- RAS severity and injection controls intentionally share compact repeated layouts. Confusing corrected, uncorrected, and UCP severity families can misclassify errors or hide/fabricate parity events.
- High-bit masks use `0x80000000L` and full-width masks use `0xFFFFFFFFL`; consumers should keep values in unsigned 32-bit register paths to avoid signedness surprises.

## Test Signals

Useful validation signals for this chunk include:

- Build AMDGPU configurations that include NBIO 7.9.0 support; malformed symbols or header mismatches should fail at compile time.
- Run generated-header consistency checks against the authoritative NBIO 7.9.0 register database: each field should have the expected shift/mask, repeated bitmap groups should be monotonic, and every register here should have a matching offset definition.
- Cross-check `nbio_7_9_0_sh_mask.h` against nearby NBIO generations only where the hardware spec says fields are shared; similar names across generations may have different field presence or base indices.
- On matching hardware, compare decoded NBIO/SB bus numbers, segment, MMIO/DRAM windows, bridge command bits, and bridge resource windows with PCI configuration dumps and AMDGPU debug output.
- Exercise software interrupt/APML/sync-flood paths only in controlled debug or validation environments, confirming status bits and GIC SPI vector fields behave as expected.
- Validate VDM/MCTP routing with platform-management traffic tests, including endpoint enablement, route-to-SMU controls, and master ID/segment programming.
- Use debug or lab-only flows for trap comparators and crossbar stall controls; confirm trap request capture, response data/status, cross-trigger, and stage-2 fields decode correctly without affecting adjacent trap slots.
- Validate RAS paths by checking interrupt registration for NBIF RAS sources, register dumps for `RAS_GLOBAL_STATUS_*`, parity severity settings, and parity error group bitmaps. Error injection should verify trigger/allow/group/ID fields and ensure corrected/uncorrected/UCP classification matches the intended severity.
- Regression-test suspend/resume, GPU reset, and firmware reinitialization because many represented fields are hardware state rather than software-owned persistent state.

### subset-b-003337: lines 25136-27410

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_sh_mask.h lines 25136-27410

## Scope

This chunk is a generated AMD NBIO 7.9 register shift/mask header segment. It contains C preprocessor constants only; there are no functions, structs, storage definitions, or executable control flow. The constants describe bit positions and masks for NBIO RAS parity status, parity counters, RAS policy controls, scratch registers, and the first part of per-event PCIe action-control registers. The paired register-address definitions for these names are in `nbio_7_9_0_offset.h`, mostly in the `0xe88018` through `0xe88070` NBIO RAS register range.

## Purpose

The purpose of this chunk is to let NBIO 7.9 driver code build and decode 32-bit register values using symbolic field names rather than hard-coded bit arithmetic. The repeated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` pattern is consumed by AMDGPU register helpers such as `REG_SET_FIELD()` and `REG_GET_FIELD()` after including this file together with `nbio_7_9_0_offset.h`.

The covered registers are RAS-oriented:

- `PARITY_ERROR_STATUS_UNCORR_GRP14` tail fields and complete groups `15` and `16`: one-bit `ParityErrDetected_IdN` flags for uncorrectable parity events.
- `PARITY_ERROR_STATUS_CORR_GRP0` through `7` and `10` through `17`: one-bit corrected parity event flags.
- `PARITY_COUNTER_CORR_GRP0` through `7` and `10` through `17`: 8-bit corrected parity counters split into `ParityErrorCount0` through `ParityErrorCount3`.
- `PARITY_ERROR_STATUS_UCP_GRP0` through `7` and `10` through `12`: one-bit UCP parity event flags.
- `PARITY_COUNTER_UCP_GRP0` through `7` and `10` through `12`: 8-bit UCP counters split into four counter fields.
- `MISC_SEVERITY_CONTROL`, `MISC_RAS_CONTROL`, `RAS_SCRATCH_0`, and `RAS_SCRATCH_1`: global RAS severity, interrupt/output control, and scratch storage fields.
- `ErrEvent_ACTION_CONTROL`, generic parity action controls, and PCIe port A/early port B action controls through `PCIE0PortBExtFatal_ACTION_CONTROL` at the end of the assigned range.

## Important Definitions

The status registers use a uniform 32-bit bitmap layout. Each `ParityErrDetected_IdN` field maps directly to bit `N`, with shifts `0x0` through `0x1f` and masks from `0x00000001L` through `0x80000000L`. This chunk starts in the middle of `PARITY_ERROR_STATUS_UNCORR_GRP14`, at `Id5`, so IDs `0` through `4` and the group comment are in the previous chunk.

Corrected and UCP counter registers use four byte-wide fields:

- `ParityErrorCount0`: shift `0x0`, mask `0x000000FFL`.
- `ParityErrorCount1`: shift `0x8`, mask `0x0000FF00L`.
- `ParityErrorCount2`: shift `0x10`, mask `0x00FF0000L`.
- `ParityErrorCount3`: shift `0x18`, mask `0xFF000000L`.

`MISC_SEVERITY_CONTROL` defines two 2-bit severity selectors:

- `ErrEventErrSev`: bits `5:4`, mask `0x00000030L`.
- `PcieParityErrSev`: bits `7:6`, mask `0x000000C0L`.

`MISC_RAS_CONTROL` exposes output and interrupt policy bits:

- `PIN_NMI_SyncFlood_En` and `GNB_SB_LinkNeverDis` at bits `2` and `3`.
- Output suppressors: `InterruptOutputDis`, `LinkDisOutputDis`, and `SyncFldOutputDis` at bits `9`, `10`, and `11`.
- PCIe event routing enables for `NMI`, `SCI`, and `SMI` at bits `12`, `13`, and `14`.
- Software event routing enables for `SCI`, `SMI`, and `NMI` at bits `15`, `16`, and `17`.

The scratch registers are full-width:

- `RAS_SCRATCH_0__SCRATCH_0_MASK` is `0xFFFFFFFFL`.
- `RAS_SCRATCH_1__SCRATCH_1_MASK` is `0xFFFFFFFFL`.

The action-control registers in this chunk have a common low-bit layout:

- `APML_ERR_En`: bit `0`, mask `0x00000001L`.
- `IntrGenSel`: bits `2:1`, mask `0x00000006L`.
- `LinkDis_En`: bit `3`, mask `0x00000008L`.
- `SyncFlood_En`: bit `4`, mask `0x00000010L`.

This repeated layout applies to `ErrEvent_ACTION_CONTROL`, `ParitySerr_ACTION_CONTROL`, `ParityFatal_ACTION_CONTROL`, `ParityNonFatal_ACTION_CONTROL`, `ParityCorr_ACTION_CONTROL`, `PCIE0PortASerr_ACTION_CONTROL`, `PCIE0PortAIntFatal_ACTION_CONTROL`, `PCIE0PortAIntNonFatal_ACTION_CONTROL`, `PCIE0PortAIntCorr_ACTION_CONTROL`, `PCIE0PortAExtFatal_ACTION_CONTROL`, `PCIE0PortAExtNonFatal_ACTION_CONTROL`, `PCIE0PortAExtCorr_ACTION_CONTROL`, `PCIE0PortAParityErr_ACTION_CONTROL`, `PCIE0PortBSerr_ACTION_CONTROL`, `PCIE0PortBIntFatal_ACTION_CONTROL`, `PCIE0PortBIntNonFatal_ACTION_CONTROL`, `PCIE0PortBIntCorr_ACTION_CONTROL`, and `PCIE0PortBExtFatal_ACTION_CONTROL`.

## Control Flow

There is no direct control flow in this header segment. At runtime, control flow exists in consumers that include this header:

- `amdgpu/nbio_v7_9.c` includes this file and uses the same register helper ecosystem for NBIO setup, doorbell routing, interrupt setup, partition state, and other NBIO 7.9 hardware interactions. The RAS constants from this chunk are available there even though the visible code paths primarily use other NBIO fields.
- `ras/ras_mgr/amdgpu_ras_nbio_v7_9.c` includes this file and registers NBIO RAS interrupt sources with `amdgpu_irq_add_id()`. Its IRQ set/process callbacks are dummy by design in the current implementation because the BIF ring path is disabled due to a hardware issue, so these masks are mostly latent support for RAS register programming and future diagnostics.

Any future executable path would combine the `reg...` address from `nbio_7_9_0_offset.h` with these masks through helpers such as `RREG32_SOC15()`, `WREG32_SOC15()`, `REG_GET_FIELD()`, and `REG_SET_FIELD()`.

## State and Persistence

The header itself holds no state and persists nothing. The represented hardware state is persistent only in NBIO registers while the GPU is powered and configured:

- Parity status registers are hardware-owned sticky or status bitmaps for detected events.
- Counter registers expose hardware-maintained counts for corrected and UCP parity classes.
- `MISC_RAS_CONTROL` and action-control registers are policy state that can alter interrupt, link-disable, APML error, and sync-flood behavior if written.
- `RAS_SCRATCH_0` and `RAS_SCRATCH_1` are full 32-bit scratch fields whose persistence depends on the NBIO register lifetime across reset, power gating, or firmware/driver ownership.

Because these definitions are compile-time constants, any mismatch between the header and silicon register layout becomes a runtime hardware programming error rather than a C language type error.

## Dependencies

This chunk depends on the AMDGPU register access convention:

- The paired address/base-index definitions in `nbio_7_9_0_offset.h`.
- AMDGPU SOC15 accessors such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_OFFSET`.
- Field helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD`, which assume the `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` naming convention.
- NBIO 7.9 IP selection through the `NBIO` hardware block and base index values, where these RAS registers use base index `8` in the offset header.

The chunk mirrors equivalent RAS action-control and parity layouts in other NBIO generation headers, including NBIO 7.0, 7.2, and 7.7 variants. That repetition is useful for cross-generation review but risky if a generated copy is accepted without checking NBIO 7.9-specific address and field changes.

## Integration Points

The main integration point is inclusion by NBIO 7.9 driver code:

- `amdgpu/nbio_v7_9.c` includes the header alongside `nbio_7_9_0_offset.h`; it uses many neighboring NBIO fields for register programming. The RAS fields in this chunk are therefore in the same namespace and available for NBIO 7.9 runtime programming.
- `ras/ras_mgr/amdgpu_ras_nbio_v7_9.c` includes this header and the NBIO IRQ source IDs. It wires RAS controller and err-event ATHUB interrupts into the AMDGPU IRQ layer, even though the callbacks are currently inert.
- The register offsets in `nbio_7_9_0_offset.h` align this chunk with concrete addresses from `regPARITY_ERROR_STATUS_UNCORR_GRP14` at `0xe88018` through `regPCIE0PortBExtFatal_ACTION_CONTROL` at `0xe8806e`, plus adjacent registers continuing after the chunk.

The status and counter definitions are likely intended for RAS collection, error reporting, and clear-on-write flows. The action-control definitions integrate with platform-level error response policy, including APML signaling, generated interrupt selection, link disable, and sync flood behavior.

## Risks

- The assigned range begins mid-register for `PARITY_ERROR_STATUS_UNCORR_GRP14`; any chunk-level interpretation of that group must merge with the previous chunk to recover IDs `0` through `4` and the group boundary.
- The status/counter groups skip numbers `8` and `9` in several families. This appears intentional because the paired offset header has corresponding address gaps, but generated-table consumers must not assume dense group numbering.
- Since these are untyped macros, bad masks, shifted field widths, or address/header mismatches compile successfully and can silently corrupt hardware programming.
- Action-control fields can affect severe platform behavior. Incorrect writes to `LinkDis_En`, `SyncFlood_En`, or interrupt routing bits could escalate recoverable parity events into link disable, sync flood, or unwanted platform interrupts.
- `RAS_SCRATCH_0/1` are full-width fields with no semantic typing here; firmware/driver ownership assumptions need external documentation or cross-file evidence before use.
- Current NBIO 7.9 RAS manager interrupt processing is deliberately dummy, so compile-time presence of these masks does not prove that all represented RAS events are surfaced to Linux error reporting today.

## Test Signals

Useful validation signals are mostly compile-time and hardware/driver integration checks:

- Build AMDGPU code that includes `nbio_7_9_0_sh_mask.h`; failures in `REG_SET_FIELD`/`REG_GET_FIELD` use sites would catch naming drift for referenced fields.
- Compare this chunk against generated hardware register metadata or neighboring NBIO generation headers to detect accidental mask/shift drift.
- Verify each field mask corresponds to its shift and width: 32 one-bit status masks, four 8-bit counter masks, two 2-bit severity fields, and the common low-bit action-control layout.
- On NBIO 7.9 hardware or emulation, read the paired offsets from `nbio_7_9_0_offset.h` and confirm that status/counter/action-control fields respond according to the documented bit positions.
- RAS testing should include corrected, uncorrectable, and UCP parity injection where available, then confirm status bitmaps/counters and interrupt/action policy behavior.
- Because `amdgpu_ras_nbio_v7_9.c` currently registers dummy IRQ processing paths, tests should distinguish raw hardware register updates from Linux IRQ/error-report delivery.

## Chunk Boundary Notes

The previous chunk owns the start of `PARITY_ERROR_STATUS_UNCORR_GRP14`. The next chunk continues after `PCIE0PortBExtFatal_ACTION_CONTROL` into the remaining port B and later action-control register definitions. A final per-file merge should connect those boundaries before drawing whole-file conclusions about all NBIO 7.9 RAS masks.

### subset-b-003338: lines 27411-29891

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_sh_mask.h lines 27411-29891

## Scope

This chunk covers generated shift and mask macros from the AMD NBIO 7.9.0 register bitfield header. The range starts at `PCIE0PortBExtNonFatal_ACTION_CONTROL` and ends at `BIF_CFG_DEV0_RC_PCIE_LANE_14_EQUALIZATION_CNTL`, with the lane 14 mask definitions continuing in the next chunk.

The chunk contains 2,142 `#define` entries across 276 register names. It is declarative hardware ABI data only: there are no C functions, structs, variables, allocations, branches, loops, locking operations, or direct register accesses in this section.

The covered register groups are:

- PCIe0 port B through G and NBIF1 port A RAS/AER action-control fields.
- Sync flood, NMI, poison, egress poison, APML status/control/trigger fields.
- NB device-indirect steering controls for PCIE0, NBIF1, and internal sideband windows.
- NB root-complex bridge indirect SMN index/data windows for PCIE0 and NBIF1.
- IOMMU L2A and L2B/indexed L2 control, cache, page-table cache, command processor, performance, power, parity, and error-rule fields.
- IOAPIC feature-enable fields.
- NBIF0 root-complex bridge PCI configuration-space fields for device 0, including PCI header, PM, PCIe, MSI, vendor-specific, virtual-channel, serial-number, AER, secondary PCIe, and lane equalization registers.

## Purpose

The purpose of this header section is to give NBIO 7.9.0 driver code named bit positions for hardware registers. Each register field is represented by the standard generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the field's least-significant bit position.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or compose that field.

Consumers use these definitions with the matching `nbio_7_9_0_offset.h` address macros and AMDGPU helper macros such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `WREG32_SOC15_EXT`. The offset header tells the driver where a register is; this mask header tells it how to interpret or construct the 32-bit value at that address.

## Important Macro Families

### PCIe Port RAS Action Controls

The first region defines repeated `*_ACTION_CONTROL` layouts for PCIe0 ports B through G and NBIF1 port A. Each port/error-class register uses the same four logical fields:

- `APML_ERR_En` at bit 0.
- `IntrGenSel` at bits 2:1.
- `LinkDis_En` at bit 3.
- `SyncFlood_En` at bit 4.

The names distinguish SERR, internal fatal/nonfatal/correctable errors, external fatal/nonfatal/correctable errors, and parity errors. These fields define the action policy for fabric or PCIe error events: whether to signal APML, choose an interrupt generation mode, disable the link, or trigger sync flood. Because the layout repeats across many ports and severities, copy-generation correctness matters; using the wrong register name would route a policy to a different port or error class even though the bit layout is identical.

### Sync Flood, NMI, Poison, and APML

`SYNCFLOOD_STATUS` records sync-flood origins from RAS control, APML, pin, private, and MCA sources. `NMI_STATUS` exposes the pin-origin NMI bit. `APML_STATUS`, `APML_CONTROL`, and `APML_TRIGGER` expose APML-visible corrected, nonfatal, fatal, SERR, internal poison, and egress poison status bits plus NMI/sync-flood/output controls and a software NMI trigger bit.

The poison region covers both internal and egress poison handling:

- `POISON_ACTION_CONTROL` contains three action-policy groups: internal poison, egress poison low status, and egress poison high status. Each group has APML error enable, interrupt generation selection, link-disable enable, and sync-flood enable fields.
- `INTERNAL_POISON_STATUS` has eight one-bit internal poison status lanes, and `INTERNAL_POISON_MASK` masks those eight lanes.
- `EGRESS_POISON_STATUS_LO` and `EGRESS_POISON_STATUS_HI` each expose 32 individual status bits, giving 64 egress poison status bits across the low/high registers.
- `EGRESS_POISON_MASK_LO`, `EGRESS_POISON_MASK_HI`, `EGRESS_POISON_SEVERITY_DOWN`, and `EGRESS_POISON_SEVERITY_UPPER` are full-width 32-bit masks or severity maps.

This region is the direct NBIO hardware vocabulary for poison propagation, error escalation, and platform management signaling. The header does not encode clear-on-read or write-one-to-clear behavior; consumers must follow the register specification and owning RAS path when reading, clearing, masking, or escalating these events.

### Device-Indirect Steering and RC Bridge Indirect Windows

The `NB_PCIE0DEVINDCFG{0..6}_STEERING_CNTL`, `NB_NBIF1DEVINDCFG0_STEERING_CNTL`, and `NB_INTSBDEVINDCFG0_STEERING_CNTL` registers all expose:

- `ForceSteering` at bit 0.
- `SteeringValue` at bits 15:8.

These fields steer device-indirect configuration accesses for multiple PCIE0 instances, NBIF1, and the internal sideband path. Incorrect steering can send indirect config traffic to the wrong target instance.

The root-complex bridge indirect windows are grouped under address blocks for `PCIE0rcbdg_indcfg0` through `PCIE0rcbdg_indcfg6` and `NBIF1rcbdg_indcfg0`. Each window has:

- `RC_SMN_INDEX_EXTENSION`, an 8-bit index extension.
- `RC_SMN_INDEX`, a full 32-bit index.
- `RC_SMN_DATA`, a full 32-bit data register.

Together these fields define indexed SMN access paths through root-complex bridge configuration windows. Their integration depends on the matching offset macros such as `regNB_PCIE0RCBDG_INDCFG0_RC_SMN_INDEX_EXTENSION`, not on this mask header alone.

### IOMMU L2A and L2B Controls

The IOMMU region starts with `aid_nbio_iohub_iommu_l2a_l2acfg` and continues through `aid_nbio_iohub_iommu_l2indx_l2indxcfg`. It defines performance counters, cache controls, page-table cache controls, power controls, error-rule controls, and command/page-request controls for the NBIO IOMMU L2 block.

L2A-visible fields include:

- `L2_PERF_CNTL_0/1` and `L2_PERF_COUNT_0..3` for four performance-event selectors, upper count fields, and 32-bit count values.
- `L2_STATUS_0` as a full-width status register.
- `L2_CONTROL_0/1` for L1 cache response allowances, untranslated/address-translation exception side PTE behavior, large-page caching, input FIFO burst length, client priority, sequential invalidation burst limits, DBUS disable, and performance threshold.
- `L2_DTC_CONTROL`, `L2_ITC_CONTROL`, and `L2_PTC_A_CONTROL` for data/instruction/page-table cache behavior: parity enable/support, invalidation selection, soft invalidate, bypass, LRU priority, way count, entry count, and page-table-cache-specific separate storage, 2 MiB mode, overlapping-page invalidation, and guest fast invalidation.
- Hash and way-control registers for DTC, ITC, and PTCA, with address masks plus way disable and way access disable bitmaps.
- `L2A_UPDATE_FILTER_CNTL`, `L2_ERR_RULE_CONTROL_3..5`, `L2_L2A_CK_GATE_CONTROL`, `L2_L2A_PGSIZE_CONTROL`, `L2_PWRGATE_CNTRL_REG_0/3`, and `L2_ECO_CNTRL_0`.

The indexed/L2B region includes:

- `L2_STATUS_1` and `L2_SB_LOCATION` for status and sideband port/core location.
- `L2_CONTROL_5/6`, `L2_PDC_CONTROL`, `L2_PDC_HASH_CONTROL`, and `L2_PDC_WAY_CONTROL` for queue arbitration, flow-control disables, DTC update policy, partial page-table-cache control, page-directory cache parity/invalidation/bypass/way sizing, and related cache address masks.
- `L2_TW_CONTROL`, `L2_TW_CONTROL_1..3` for table-walker coherence, prefetch, filtering, error continuation, access-bit/AP-bit behavior, nested PTE caching, trace enable/no-wrap/force-disable/mask, and trace address low/high fields.
- `L2_CP_CONTROL`, `L2_CP_CONTROL_1..3` for command processor prefetch, flushing, request pass-through, outstanding-command limiting, read delay, L1-off controls, invalidation mode fields, wait-completion behavior, and scheduler/interlock timing fields.
- `L2_CREDIT_CONTROL_0/1`, `L2_ERR_RULE_CONTROL_0..2`, `L2_L2B_CK_GATE_CONTROL`, `PPR_CONTROL`, `L2_L2B_PGSIZE_CONTROL`, `L2_PERF_CNTL_2/3`, `L2_PERF_COUNT_4..7`, `L2B_SDP_PARITY_ERROR_EN`, and `L2_ECO_CNTRL_1`.

These fields are sensitive because they affect address translation caching, invalidation progress, page-request handling, parity/error behavior, performance counters, and clock/power gating. The header provides bit positions; the actual sequencing and ordering rules belong to the IOMMU/NBIO driver logic and hardware specification.

### IOAPIC Feature Enable

`FEATURES_ENABLE` under `aid_nbio_iohub_nb_ioapiccfg_ioapic_cfgdec` exposes feature toggles such as `FEATURE_ENABLED`, `LEGACY_REDIR`, `IOAPIC_ID`, and interrupt remapping selection bits. These fields are part of NBIO's IOAPIC configuration decode and interact with platform interrupt routing rather than GPU command submission.

### NBIF0 Root-Complex PCI Configuration Header

The `aid_nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` address block begins a root-complex bridge PCI configuration-space image for NBIF0 device 0.

The base PCI bridge header fields include:

- Identity and class fields: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS`.
- `BIF_CFG_DEV0_RC_COMMAND` bits for I/O space, memory space, bus master, parity/error response, SERR, fast back-to-back, interrupt disable, and reserved bits.
- `BIF_CFG_DEV0_RC_STATUS` bits for interrupt status, capability-list presence, 66 MHz capable, fast back-to-back capable, parity/abort/system-error status, DEVSEL timing, and detected parity.
- Cache-line, latency, header, BIST, base-address, bus-number/latency, I/O base/limit, memory base/limit, prefetchable memory base/limit, upper prefetchable address, high I/O base/limit, capability pointer, ROM base, interrupt line/pin, bridge control, and extended bridge control fields.

This section mirrors standard PCI-to-PCI bridge configuration concepts. A wrong mask here can affect enumeration-visible bridge resources, bus numbering, legacy VGA/ISA behavior, SERR propagation, or memory/I/O aperture decoding.

### Power Management, PCIe Capability, Slot, and Link Controls

The PM capability fields cover `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`, including version, PME support, D-state support, auxiliary current, power state, PME enable/status, data select/scale, bus power enable, and PM data fields.

The PCIe capability fields include:

- `PCIE_CAP_LIST` and `PCIE_CAP` for capability ID, next pointer, version, device type, slot implemented, and interrupt message number.
- `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` for payload sizes, phantom functions, extended tags, relaxed ordering, no-snoop, error-report enables/status, role-based error reporting, captured slot power, FLR capability, auxiliary power, transactions pending, and emergency power reduction status.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` for supported/current link speed, link width, ASPM/PM control, link disable/retrain, common clock, extended sync, clock power management, bandwidth interrupts, DRS signaling, link training, slot clock config, and data-link active status.
- `SLOT_CAP`, `SLOT_CNTL`, and `SLOT_STATUS` for hotplug, power controller, MRL sensor, attention/power indicators, slot power limit, physical slot number, command-completed interrupt, presence detection, electromechanical interlock, and data-link state change.
- `ROOT_CNTL`, `ROOT_CAP`, and `ROOT_STATUS` for PME interrupt routing and root-port PME status/requester information.

The PCIe 2/secondary capability fields add completion timeout, ARI, atomic operation, IDO, LTR, OBFF, TLP prefix, emergency power reduction, FRS, target link speed, compliance/deemphasis controls, 8 GT/s equalization phase status, RTM presence, crosslink status, and DRS message receipt.

### MSI, Vendor-Specific, Virtual Channel, Serial Number, and AER

The MSI capability group defines capability-list fields, MSI enable, multi-message capability/enable, 64-bit addressing, per-vector masking capability, extended message-data capability/enable, MSI address low/high, data, extended data, and 64-bit message-data aliases.

The subsystem and vendor-specific capability fields include subsystem vendor/device IDs, vendor-specific enhanced capability headers, VSEC ID/revision/length, and two full-width vendor-specific data registers.

The virtual-channel group exposes VC enhanced capability headers, port VC capabilities, VC arbitration capability/table offsets, port arbitration capability, VC arbitration selection, load-table control/status, and VC0/VC1 resource capability/control/status fields. These fields can affect transaction-class to VC mapping and load-table state.

The device serial number registers expose two full 32-bit serial-number words. The AER region includes:

- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`.
- `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY` for DLP, surprise down, poisoned TLP, flow-control protocol, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal uncorrectable, multicast blocked TLP, atomic-op egress blocked, TLP-prefix blocked, and poisoned-TLP egress-blocked events.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK` for receiver error, bad TLP, bad DLLP, replay rollover, replay timeout, advisory nonfatal, internal correctable, and header-log overflow.
- `PCIE_ADV_ERR_CAP_CNTL`, header logs `HDR_LOG0..3`, root error command/status, error source IDs, and TLP prefix logs `TLP_PREFIX_LOG0..3`.

This AER region is one of the highest-risk parts of the chunk. It controls error visibility and severity classification for PCIe root-port errors, and also records diagnostic payload such as TLP headers, prefix logs, and source IDs.

### Secondary PCIe and Lane Equalization

The final region starts the secondary PCIe extended capability and lane equalization definitions:

- `PCIE_SECONDARY_ENH_CAP_LIST` defines the enhanced capability header.
- `PCIE_LINK_CNTL3` exposes perform equalization, link equalization request interrupt enable, and lower SKP ordered-set generation controls.
- `PCIE_LANE_ERROR_STATUS` exposes a 16-bit lane error bitmap.
- `PCIE_LANE_0_EQUALIZATION_CNTL` through `PCIE_LANE_14_EQUALIZATION_CNTL` define per-lane downstream port 8 GT/s transmit preset, downstream receive preset hint, upstream transmit preset, and upstream receive preset hint fields.

Lane 14 starts in this chunk and its mask definitions continue in the next chunk. The merge lane should connect this report with the following chunk for the remaining lane 14 fields and later lane/register definitions.

## Control Flow and State Behavior

This chunk has no executable control flow. Its macros influence runtime behavior only after included C code expands them into bit manipulations and register I/O operations.

The state represented here is hardware state in NBIO, IOMMU L2, IOAPIC configuration, and PCIe root-complex configuration registers. Some fields are persistent configuration until reset or reprogramming, such as error-action policy bits, poison masks/severity maps, indirect steering values, IOMMU cache and clock-gating controls, PCI command/bridge aperture fields, PM controls, MSI programming, virtual-channel resource controls, AER masks/severities, and link-control settings. Other fields are status or command-like bits, such as sync-flood status, NMI status, poison status, APML status, IOMMU performance counters/status, PCIe device/link/slot/root/AER status, header/TLP logs, error source IDs, lane error status, retrain/equalization trigger bits, and soft-invalidate controls.

The header cannot describe side effects such as sticky status clearing, write-one-to-clear behavior, polling requirements, ordering requirements around invalidations, or reset-domain persistence. Those rules are supplied by the hardware specification and by driver code that uses the macros.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header convention and on the matching NBIO 7.9.0 register address header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_offset.h` supplies `reg*` addresses and base indices.
- Neighboring generated headers for NBIO defaults and IV source IDs supply reset values and interrupt source identifiers.
- AMDGPU register helper macros compose and extract fields using the `__SHIFT` and `_MASK` definitions from this file.

Direct include users observed in this source tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_9.c`, which includes this mask header with the 7.9.0 offset header and uses the standard SOC15 register access pattern for NBIO initialization, revision discovery, memory-controller access, doorbell aperture/range programming, and related NBIO setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_nbio_v7_9.c`, which includes the same generated headers while registering NBIO RAS interrupt sources. In the current file, the RAS handlers are dummy/no-op for the disabled BIF-ring path and do not directly reference the specific bitfield names in this chunk.

Likely integration areas for this chunk's fields include NBIO RAS policy setup, APML/NMI/sync-flood signaling, poison event handling, indirect register access routing, IOMMU cache and invalidation tuning, page-request/PPR interrupt coalescing, PCI bridge enumeration and resource windows, PCIe link training and status diagnostics, MSI programming, virtual-channel configuration, and PCIe AER reporting.

The macros are ASIC-generation-specific. Similar register names appear in other NBIO 7.x headers, but field presence and reserved-bit definitions can differ. Code must include matching 7.9.0 offset/mask/default headers rather than mixing definitions from neighboring ASIC versions.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can write reserved bits, mask the wrong hardware status, set the wrong PCIe capability/control bit, or misdecode link/error state.
- Repeated action-control layouts make copy mistakes hard to spot. The same four fields are repeated for many ports and error severities; the register name, not just the mask value, determines which error path is affected.
- Poison, APML, NMI, and sync-flood bits are escalation paths. Incorrect masks can suppress critical hardware events, over-escalate recoverable events, disable links unexpectedly, or produce platform management signals at the wrong time.
- IOMMU L2 cache, invalidation, and table-walker controls affect address translation correctness. Misprogramming soft invalidation, bypass, parity, cache way, page size, credit, command processor, or table-walker fields can cause stale translations, hangs, performance loss, or false parity/error reporting.
- Clock and power gating fields can create timing-sensitive failures if changed outside the expected power-management sequence.
- PCI bridge header masks affect enumeration-visible state such as BARs, bus numbers, memory/I/O windows, ROM enable, interrupt routing, and bridge control. Wrong masks can break PCI resource assignment or legacy decode behavior.
- PCIe AER mask/severity/status fields are diagnostic and reliability-sensitive. Incorrect values can hide real errors, flood interrupts, misclassify fatal versus nonfatal errors, or corrupt captured header/TLP logs.
- Lane equalization fields are per-lane and repetitive. Lane-number or suffix mistakes can tune the wrong lane or misreport equalization state, especially at the chunk boundary where lane 14 continues into the next chunk.

## Test Signals

Useful validation signals for this generated header section include:

- Compile coverage for `nbio_v7_9.c` and `amdgpu_ras_nbio_v7_9.c`, proving the 7.9.0 offset and mask headers remain syntactically compatible with AMDGPU register helper macros.
- Static checks that every `__SHIFT` macro in this chunk has a matching `_MASK` macro for the same register/field, except where the chunk intentionally starts or ends mid-register.
- Generated-header comparison against the authoritative NBIO 7.9.0 register database for action-control, poison/APML, IOMMU L2, PCIe root bridge, AER, and lane equalization fields.
- Runtime smoke on NBIO 7.9.0 hardware or emulation that reads stable PCI configuration fields such as vendor/device/class IDs, link status, PM/PCIe capability IDs, MSI capability bits, and AER capability headers.
- RAS/error-injection or platform diagnostics that confirm poison status, APML status, sync-flood status, AER status/mask/severity, and root error status bits are decoded and cleared according to hardware expectations.
- IOMMU stress covering ATS/translation workloads, invalidation, page requests, and performance counters after any change to L2 cache, table-walker, command processor, or page-size masks.

## Cross-Chunk Notes

The source file is an oversized generated register header, so this document describes only lines 27411-29891. Adjacent chunks are needed for the whole-file report. This chunk begins after prior PCIe0 port B definitions and ends in the middle of the lane 14 equalization control register; the following chunk should contain the remaining `BIF_CFG_DEV0_RC_PCIE_LANE_14_EQUALIZATION_CNTL` masks and subsequent NBIO 7.9.0 register fields.

### subset-b-003339: lines 29892-32328

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_sh_mask.h lines 29892-32328

## Purpose

This chunk is a generated AMD NBIO 7.9.0 shift/mask header slice for PCIe/NBIO configuration-space register fields. It is not executable driver code; it exports preprocessor constants that describe bit positions and masks for registers whose addresses live in the matching `nbio_7_9_0_offset.h` header.

The range starts in the tail of the root-complex PCIe 8.0 GT/s per-lane equalization definitions, covers the root-complex ACS, DLF, PCIe 16.0 GT/s PHY, PCIe margining, and PCIe 32.0 GT/s link fields, then moves into the `aid_nbio_nbif0_bif_cfg_dev0_epf0_vf*_bifcfgdecp` PCI configuration-space blocks for virtual functions 0, 1, and the beginning of 2. The range ends mid-block at `BIF_CFG_DEV0_EPF0_VF2_MSIX_CAP_LIST__CAP_ID_MASK`, so the final VF2 MSI-X capability-list field set continues in a later chunk.

## Public Surface

The exported API is macro-only:

- `REGISTER__FIELD__SHIFT` gives the bit offset for a field.
- `REGISTER__FIELD_MASK` gives the raw bit mask for that field.

No functions, structs, enums, storage, or inline helpers are defined here. Consumers combine these masks with AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15` after selecting the corresponding register address from an offset header.

## Register Families Covered

The first root-complex section completes PCIe 8.0 GT/s lane equalization for lane 15 and carries the tail masks for lane 14. The fields describe downstream/upstream transmit presets and receiver preset hints for per-lane link training.

The ACS section defines the enhanced capability-list header plus ACS capability and control bits: source validation, translation blocking, peer-to-peer request/completion redirect, upstream forwarding, P2P egress control, direct translated P2P, enhanced capability reporting, I/O request blocking, downstream/upstream memory target access controls, and unclaimed-request redirect behavior. These fields are isolation and routing controls for PCIe peer traffic.

The DLF section defines the data-link feature enhanced capability list and local/remote DLF support state. It includes the exchange-enable and remote-valid bits used to negotiate PCIe data-link features.

The 16.0 GT/s PHY section defines enhanced-capability header fields, reserved link capability/control dwords, equalization completion/phase/link-request status, parity mismatch status for local/RTM1/RTM2 contexts, and per-lane 16.0 GT/s downstream/upstream transmit presets for lanes 0 through 15.

The PCIe margining section defines the margining enhanced capability list, port capability/status, and per-lane control/status registers for lanes 0 through 15. Each lane has receiver number, margin type, usage model, and margin payload fields, with parallel status fields. These are software-visible controls for link margining diagnostics.

The 32.0 GT/s section defines link capability/control/status fields for equalization bypass, no-equalization-needed behavior, modified training sequence usage modes, equalization phase completion, modified TS receipt, enhanced link behavior control, transmitter precoding state/request, and no-EQ-needed receipt.

The VF0/VF1/VF2 endpoint-function sections mirror standard PCI/PCIe configuration-space layouts for SR-IOV or virtual-function-facing config spaces. For each covered VF, this includes conventional PCI identity and command/status fields, BARs and ROM BAR fields, subsystem IDs, capability pointers, PCIe capability/device/link/device2/link2 status and controls, MSI/MSI-X capability fields, vendor-specific enhanced capability fields, AER status/mask/severity/capability/log fields, ATS capability/control, and ARI capability/control. VF2 coverage stops before the MSI-X capability-list group is complete.

## Important Fields

PCI command/status masks control I/O space, memory space, bus mastering, parity/SERR response, interrupt disable, capability-list presence, abort/error status, and parity detection. These are standard PCI config-space fields but are generated in chip-specific NBIO naming.

PCIe device control fields include correctable, non-fatal, fatal, and unsupported-request reporting enables; relaxed ordering; max payload size; extended tags; phantom functions; auxiliary power PM; no-snoop; max read request size; and FLR initiation. Device status fields expose matching error status, auxiliary power, pending transactions, and emergency power reduction detection.

PCIe link fields include maximum/current link speed, negotiated width, ASPM/PM controls, retrain/link-disable/common-clock/extended-sync controls, clock power management, bandwidth-management interrupts, data-link active reporting, DRS signaling, and 8.0 GT/s equalization status. Link capability 2 and control 2 add target link speed, compliance entry, autonomous speed disable, transmit margin, de-emphasis, lower SKP OS support, RTM presence detect support, crosslink, and DRS support/status.

MSI/MSI-X fields describe enable state, multi-message capability/enables, 64-bit support, per-vector masking support, extended message data capability/enable, message address/data fields, mask and pending bitmaps, MSI-X table size/function mask/enable, and MSI-X table/PBA BIR and offset fields.

AER fields are extensive. The uncorrectable status/mask/severity groups cover DLP, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast-blocked TLP, AtomicOp egress blocked, TLP prefix blocked, and poisoned TLP egress blocked. Correctable status/mask covers receiver error, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal, correctable internal error, and header-log overflow. AER capability/control includes first-error pointer, ECRC generate/check capability and enables, multi-header record support/enables, TLP prefix log presence, and completion-timeout log capability. Header and TLP prefix log registers are full-width capture dwords.

ATS fields define the enhanced capability header, invalidation queue depth, page-aligned request support, global invalidate support, STU, and ATC enable. ARI fields define the enhanced capability header, MFVC/ACS function-group capabilities, next function number, MFVC/ACS group enables, and ARI function group.

## Control Flow And State

There is no runtime control flow in this header. Use is compile-time substitution:

1. An NBIO 7.9 translation unit includes `nbio/nbio_7_9_0_offset.h` and `nbio/nbio_7_9_0_sh_mask.h`.
2. Driver code selects a register address from the offset header.
3. Driver code reads or prepares a raw register value.
4. The relevant `*_MASK` and `*_SHIFT` macros decode, test, clear, or compose fields.

The header itself stores no state and has no persistence behavior. Persistent or semi-persistent state lives in hardware: PCIe config registers, VF BAR/MSI/MSI-X/ATS/ARI configuration, AER masks and logs, ACS routing controls, link equalization/margining controls, and link status registers. Some fields are configuration state programmed by firmware, the kernel PCI core, or AMDGPU; others are live status bits, hardware-owned logs, write-one-to-clear error status, or training/margining handshakes.

## Dependencies And Integration Points

The immediate dependency is the generated AMD register-header convention. This `_sh_mask` header supplies bit layouts; `nbio_7_9_0_offset.h` supplies addresses such as the root-complex ACS, margining, 32.0 GT/s link, and VF0/VF1/VF2 configuration-space registers. Default-value headers from nearby NBIO generations show the same generated family pattern, but this chunk should be reconciled against the NBIO 7.9.0 offsets for exact address pairing.

The NBIO 7.9 generation is included by `amdgpu/nbio_v7_9.c` and `ras/ras_mgr/amdgpu_ras_nbio_v7_9.c`. Direct handwritten use of the specific macro names in this chunk was not found outside generated register headers in the inspected tree, which means these fields are primarily part of the chip register ABI and may be used indirectly by generic register dumps, generated tooling, or future NBIO/RAS/PCIe feature code.

Semantic dependencies come from PCI, PCI Express, AER, ACS, ATS, ARI, MSI/MSI-X, SR-IOV/VF configuration-space behavior, and AMD NBIO hardware specifications. Correct behavior also depends on the kernel PCI core, AMDGPU's SOC15 register access paths, firmware-provided PCIe setup, and hardware link-training/error-reporting side effects.

## Risks And Maintenance Notes

- This file is generated and highly repetitive. A single bad shift or mask can silently decode or program the wrong hardware bit.
- The chunk boundaries are partial: it begins after earlier lane-14 equalization fields and ends before VF2 MSI-X capability-list completion. Merge-time reconciliation must include adjacent chunks.
- VF0, VF1, and VF2 groups are structurally similar but not interchangeable at the register-address level. Copying masks across VF address blocks without the matching offset can target the wrong VF.
- PCIe ACS, ATS, ARI, and AER fields affect isolation, IOMMU/translation behavior, error containment, and peer-to-peer routing. Incorrect masks can create security or reliability issues in SR-IOV and peer-memory scenarios.
- Link equalization, margining, and 32.0 GT/s controls are hardware-sensitive. Writing control bits outside the expected link-training or diagnostic flow can destabilize the PCIe link.
- AER status, mask, severity, and log fields have side effects and ordering rules that the macros do not express. Callers must know which bits are write-one-to-clear, sticky, hardware-owned, or log-capture fields.
- Full-width and high-bit masks such as `0xFFFFFFFFL` and `0x80000000L` should remain in unsigned register-value paths to avoid signedness or truncation bugs.
- Similar NBIO generations expose near-identical names with subtle differences in field presence and offsets. Version-specific includes must not be mixed.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage for NBIO 7.9 AMDGPU and RAS files that include `nbio_7_9_0_sh_mask.h`.
- Static generated-header checks that every `*_SHIFT` has a matching aligned `*_MASK`, repeated lane/VF groups are complete within their intended ranges, and masks do not overlap unexpectedly inside a register.
- Cross-header checks that every register family named in this chunk has a matching `cfg*` or `reg*` address in `nbio_7_9_0_offset.h`.
- Runtime PCIe register dumps on NBIO 7.9 hardware comparing decoded command/status, PCIe capability, link capability/status, MSI/MSI-X, AER, ATS, and ARI fields against `lspci -vvxxx` and AMDGPU debug output.
- SR-IOV validation that VF0/VF1/VF2 config-space fields decode independently and that BAR, MSI/MSI-X, AER, ATS, and ARI state does not bleed across VFs.
- Link-training diagnostics that verify 8.0/16.0/32.0 GT/s equalization status and per-lane preset fields after speed changes.
- PCIe margining diagnostics that toggle lane margining controls through supported software paths and observe matching lane status payloads.
- Error-injection or platform RAS tests that exercise AER correctable/uncorrectable status, mask, severity, and header/TLP-prefix log decode without clearing or misclassifying unrelated bits.

### subset-b-003340: lines 32329-34751

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_sh_mask.h lines 32329-34751

## Scope

This chunk is a generated AMD NBIO 7.9.0 shift/mask header fragment. It contains C preprocessor constants only: `__SHIFT` and `_MASK` macros for fields in PCIe configuration-space style registers exposed through the NBIO/BIF device-function decode for `DEV0_EPF0` virtual functions.

The requested range starts in the middle of the VF2 PCIe capability block at `BIF_CFG_DEV0_EPF0_VF2_MSIX_MSG_CNTL`, covers the remainder of VF2's MSI-X/AER/vendor/ATS/ARI masks, covers complete VF3 and VF4 config-space mask blocks, and covers most of VF5 through `BIF_CFG_DEV0_EPF0_VF5_PCIE_ATS_CNTL`, ending at the start of `BIF_CFG_DEV0_EPF0_VF5_PCIE_ARI_ENH_CAP_LIST`. Adjacent chunks are needed for the earlier VF2 base/MSI definitions and the remainder of VF5 ARI plus later VFs.

There are no functions, structs, enums, storage definitions, locks, allocation paths, or runtime branches in this chunk. Its purpose is compile-time description of hardware bitfields.

## Purpose and Register Families

The macros describe how to extract or set individual fields in the NBIO 7.9.0 BIF PCI configuration register images for SR-IOV virtual functions. The register names follow AMDGPU's generated convention:

- `BIF_CFG_DEV0_EPF0_VF<n>_<REGISTER>__<FIELD>__SHIFT`
- `BIF_CFG_DEV0_EPF0_VF<n>_<REGISTER>__<FIELD>_MASK`

The covered register families are:

- VF2 tail: MSI-X message control/table/PBA, vendor-specific extended capability, PCIe Advanced Error Reporting, header/TLP-prefix logs, Address Translation Services, and Alternative Routing-ID Interpretation masks.
- VF3 complete block: conventional PCI header fields, BARs, ROM, capability pointer, interrupts, PCIe capability/control/status, link capability/control/status, MSI/MSI-X, vendor-specific capability, AER, ATS, and ARI masks.
- VF4 complete block with the same PCI/PCIe/SR-IOV virtual-function layout as VF3.
- VF5 partial block: conventional PCI header through ATS control, plus the first ARI enhanced-capability comment and initial fields at the chunk boundary.

The generated content models the PCIe-visible configuration structure for GPU virtual functions rather than the higher-level Linux PCI core abstractions. It gives AMDGPU and diagnostics exact bit positions for fields such as command/status flags, link training state, MSI/MSI-X enablement, AER status/masks/severity, ECRC controls, ATS enablement, and ARI grouping.

## Important APIs, Types, and Macros

This chunk exports no callable API. The important interface is the macro naming contract consumed by AMDGPU register helpers:

- `REG_GET_FIELD(value, REGISTER, FIELD)` expects `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` to exist and extracts a field from a register value.
- `REG_SET_FIELD(value, REGISTER, FIELD, field_value)` uses the same generated macros to update a field without hand-coded shifts.
- `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15_PREREG`, and related helpers pair shift/mask headers with companion offset headers such as `nbio_7_9_0_offset.h`.

Representative field groups in this chunk:

- PCI command/status: `IO_ACCESS_EN`, `MEM_ACCESS_EN`, `BUS_MASTER_EN`, `INT_DIS`, `CAP_LIST`, `MASTER_DATA_PARITY_ERROR`, target/master abort flags, system error, and parity error.
- PCI identity and layout: `VENDOR_ID`, `DEVICE_ID`, class-code bytes, revision ID, cache line, latency, header type, BIST, BAR addresses, subsystem adapter ID, ROM base, capability pointer, interrupt line/pin, min grant, and max latency.
- PCIe capability: `CAP_ID`, `NEXT_PTR`, `PCIE_CAP_VERSION`, `DEVICE_TYPE`, `SLOT_IMPLEMENTED`, `INT_MESSAGE_NUM`, maximum payload/read request sizes, relaxed ordering, no-snoop, phantom functions, extended tags, error reporting enables, aux power, FLR, and transaction-pending state.
- PCIe link capability/control/status: maximum speed/width, ASPM support/control, L0s/L1 exit latency, clock power management, hotplug-related bits, retrain/common-clock/extended-sync controls, negotiated link speed/width, slot clock, training, link bandwidth management/status, target link speed, speed disable, equalization, retimer presence, crosslink, current de-emphasis, and downstream component presence.
- MSI/MSI-X: capability-list pointers, MSI enable/multi-message fields, 64-bit support, per-vector masking, extended message-data support, message address/data/mask/pending fields, MSI-X table size, function mask, enable, table BIR/offset, and PBA BIR/offset.
- Vendor-specific extended capability: VSEC capability id/version/next pointer, VSEC id/revision/length, and scratch registers.
- AER: uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control including ECRC generation/check capability and enable bits, multi-header logging, TLP-prefix log presence, completion-timeout log capability, header logs, and TLP prefix logs.
- ATS and ARI: ATS enhanced capability list, invalidate queue depth, page-aligned requests, global invalidate support, relaxed ordering support, STU, ATC enable, ARI capability list, MFVC/ACS function-group capability, next function number, and ARI function-group controls where present in this range.

The complete VF3/VF4 blocks are useful as pattern anchors for merge-time validation because the same named registers and fields repeat with only the VF number changed.

## Control Flow and Data Flow

There is no direct control flow inside the header. Runtime behavior is indirect:

1. NBIO 7.9.0 driver code includes `nbio/nbio_7_9_0_sh_mask.h`.
2. Code reads a NBIO/BIF register or PCI configuration register image through AMDGPU's SOC15, PCIE-indexed, or config-space access path.
3. The read value is decoded with `REG_GET_FIELD()` using a macro pair from this header.
4. For writable fields, code builds a new value with `REG_SET_FIELD()` and writes it back through the matching offset/access helper.

The companion source `amdgpu/nbio_v7_9.c` demonstrates the general integration style for this header family: it includes `nbio_7_9_0_sh_mask.h`, uses generated masks with `REG_SET_FIELD()` for doorbell and interrupt-control programming, uses generated masks for HDP flush completion references, and registers `nbio_v7_9_funcs` callbacks used by the rest of AMDGPU. `ras/ras_mgr/amdgpu_ras_nbio_v7_9.c` also includes this header while wiring NBIO RAS interrupt sources.

This specific line range is dominated by virtual-function PCI config masks, so the main data flow is configuration/status interpretation rather than active initialization logic. Examples include decoding whether a VF has bus mastering enabled, whether link retraining is active, whether MSI-X is enabled or masked, whether an AER bit reports a poisoned TLP or completion timeout, and whether ATS/ARI features are advertised or enabled.

## State and Persistence

The header has no software state and no persistence. All constants are compile-time metadata.

The state described by these macros lives in hardware-maintained or PCIe configuration-space registers:

- Conventional PCI command/status bits represent enablement and error state for each virtual function and may be changed by firmware, hypervisor/PF management, or PCI configuration writes.
- BAR, ROM, class, subsystem, capability-list, and interrupt fields define the VF's PCI-visible identity and resources.
- PCIe device/link control and status bits track negotiated payload sizes, link speed/width, power-management policy, link training/equalization state, completion timeout behavior, and FLR/transaction-pending state.
- MSI/MSI-X registers hold interrupt-routing state including message addresses/data, vector masking, pending bits, table location, and PBA location.
- AER registers persist or latch PCIe error status until cleared according to hardware/PCIe semantics; mask and severity registers affect which errors are reported and how they are classified.
- ATS/ARI fields expose address-translation and routing capabilities that interact with IOMMU, virtualization, and PCIe hierarchy behavior.

Incorrect masks or shifts do not corrupt this header at runtime, but they make every compiled consumer extract or update the wrong hardware bits. Because the macros are compile-time constants, such errors are systematic and can survive normal type checking.

## Dependencies and Integration Points

This chunk depends on the generated AMD register database staying synchronized across:

- `nbio_7_9_0_sh_mask.h`, which supplies field encodings.
- `nbio_7_9_0_offset.h`, which supplies register addresses/base indices.
- AMDGPU's SOC15 register access macros and `REG_GET_FIELD`/`REG_SET_FIELD` helpers.
- NBIO 7.9.0 implementation files such as `amdgpu/nbio_v7_9.c`.
- NBIO RAS registration paths such as `ras/ras_mgr/amdgpu_ras_nbio_v7_9.c`.
- SR-IOV virtualization flows, where multiple VFs expose similar config spaces and field correctness must hold across VF numbers.

External integration is with PCIe-defined behavior: MSI/MSI-X, AER, ATS, ARI, link capability/control/status, and conventional PCI config header fields. Linux PCI core code may own many standard config-space writes, while AMDGPU/NBIO code and diagnostics need the hardware-specific generated masks to inspect, report, or manipulate NBIO-exposed fields.

## Risks and Edge Cases

- The chunk starts and ends on partial logical blocks. Merge logic must not treat this as a complete VF2 or complete VF5 report.
- VF3 and VF4 are highly repetitive. Generator drift can create a single wrong VF-numbered macro that still compiles but decodes the wrong VF field.
- Fields with the same bit numbers across status, mask, and severity registers are easy to confuse. For example, AER uncorrectable status, mask, and severity use parallel names but have different semantics.
- Some masks are 16-bit PCI config fields and others are 32-bit extended capability fields. Using a mask with the wrong access width can silently drop or misinterpret bits.
- MSI and MSI-X fields include overlapping address/data layouts for 32-bit and 64-bit modes. Wrong mask selection can misprogram vectors or pending masks.
- AER status fields can be sticky or write-one-to-clear depending on the underlying register. The masks only identify bits; driver code must still obey the hardware clear semantics.
- ATS and ARI enablement affects IOMMU and PCIe routing behavior. A wrong `ATC_ENABLE`, `STU`, function-group, or next-function-number interpretation can affect VF DMA translation or enumeration.
- Link control/status bits are live hardware state. Decoding retrain, equalization, bandwidth-management, and speed/width fields incorrectly can lead to misleading diagnostics or unsafe policy choices.
- Because this is a generated header, local manual edits are high risk unless regenerated from the authoritative hardware register specification.

## Test and Validation Signals

Useful validation is mostly compile-time plus hardware/SR-IOV behavior:

- Build AMDGPU with NBIO 7.9.0 enabled; missing or renamed macros fail at compile time in consumers using `REG_GET_FIELD()` or `REG_SET_FIELD()`.
- Compare this generated chunk against the authoritative NBIO 7.9.0 register spec and the matching `nbio_7_9_0_offset.h` entries for VF2 through VF5.
- Cross-check repeated VF3/VF4/VF5 macro sets mechanically: field names, shifts, and masks should match for equivalent registers unless the hardware spec intentionally differs.
- Exercise SR-IOV with multiple VFs enabled and confirm PCI config reads for VF3/VF4/VF5 report plausible vendor/device IDs, command/status bits, BARs, MSI/MSI-X capability structures, PCIe capability fields, AER capability structures, ATS, and ARI.
- Validate MSI and MSI-X interrupt delivery per VF, including masking/unmasking, pending bits, table/PBA location interpretation, and 64-bit MSI address/data layouts.
- Inject or observe PCIe/AER conditions where available and verify correct decoding of uncorrectable/correctable status, masks, severity, header logs, and TLP-prefix logs.
- Test link-state diagnostics on NBIO 7.9.0 hardware for negotiated speed/width, retrain/equalization state, ASPM-related controls, and bandwidth-management status.
- Run suspend/resume, FLR, GPU reset, and VF hot/unplug or rebind flows to verify VF config state is reinitialized or preserved as expected by firmware, PF management, and Linux PCI core.

### subset-b-003341: lines 34752-37218

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_sh_mask.h lines 34752-37218

## Scope

This chunk covers generated shift and mask macros from the NBIO 7.9.0 AMD GPU register mask header. The range starts at the tail of the `BIF_CFG_DEV0_EPF0_VF5` PCIe ARI capability, then covers complete PCI configuration-space images for `VF6` and `VF7`, followed by per-virtual-function BIF/RCC register blocks for `VF0`, `VF1`, and `VF2`. It ends after the `RCC_DEV0_EPF0_VF2_GFXMSIX_PBA` fields, immediately before the `VF3` BIF register block begins.

The covered register families are:

- `BIF_CFG_DEV0_EPF0_VF5_PCIE_ARI_CAP` and `BIF_CFG_DEV0_EPF0_VF5_PCIE_ARI_CNTL`, completing the previous VF5 PCIe ARI extended capability block.
- Full `BIF_CFG_DEV0_EPF0_VF6_*` and `BIF_CFG_DEV0_EPF0_VF7_*` PCI/PCIe virtual-function configuration headers, including base PCI header fields, PCIe device/link capabilities, MSI/MSI-X, vendor-specific extended capability fields, AER status/mask/logging, ATS, and ARI.
- `BIF_BX_DEV0_EPF0_VF0_*`, `VF1_*`, and `VF2_*` BIF PF/VF decode blocks for BME status, atomic error logging, doorbell self-ring aperture, HDP coherency flush controls, GPU HDP flush request/done bits, transaction-pending status, address LUT bypass, mailbox data/control, and VM/hypervisor mailbox signaling.
- `BIF_BX_DEV0_EPF0_VF0_MM_*`, `VF1_MM_*`, and `VF2_MM_*` system PF/VF decode indexed MMIO access registers.
- `RCC_DEV0_EPF0_VF0_*`, `VF1_*`, and `VF2_*` RCC blocks for SR-IOV error logging, doorbell aperture enable, config memory sizing/reserved state, IOV function identification, and four GFX MSI-X vector table entries plus pending-bit array.

This is a generated hardware bitfield map. It defines C preprocessor constants only. There are no C functions, structs, variables, allocations, locks, or executable control-flow constructs in this chunk.

## Purpose

The purpose of this section is to provide bit-level ABI constants for NBIO 7.9.0 virtual-function PCIe configuration space and per-VF BIF/RCC control registers. Every field follows the generated pattern:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the containing register value.

The masks pair with address definitions from `nbio_7_9_0_offset.h` and related NBIF offset headers. Driver code includes this header from `drivers/gpu/drm/amd/amdgpu/nbio_v7_9.c` and `drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_nbio_v7_9.c`, then consumes the constants through AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`. For example, NBIO 7.9 setup code uses the matching VF0 HDP coherency flush offset as the remapped MMIO base when running as an SR-IOV virtual function.

## Important Macro Families

### VF5 ARI Tail

The first lines finish the `BIF_CFG_DEV0_EPF0_VF5` Alternative Routing-ID Interpretation fields:

- `PCIE_ARI_CAP` exposes multifunction/ACS function group capability bits and `ARI_NEXT_FUNC_NUM`.
- `PCIE_ARI_CNTL` exposes ARI function-group enable bits and the current function-group selector.

These fields affect VF function numbering and routing in PCIe SR-IOV environments. They are sensitive because incorrect ARI capability/control masks can change how software discovers or addresses VFs behind a PF.

### VF6 and VF7 PCI Configuration Images

The `VF6` and `VF7` address blocks are complete virtual-function PCI configuration-space maps. They repeat the same layout for two adjacent VFs:

- Base identity and class fields: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS`.
- Command/status fields: I/O enable, memory enable, bus mastering, SERR, interrupt disable, capability-list presence, parity/abort/system-error bits, and DEVSEL timing.
- BAR and legacy header fields: `BASE_ADDR_1` through `BASE_ADDR_6`, `ROM_BASE_ADDR`, `CARDBUS_CIS_PTR`, `ADAPTER_ID`, capability pointer, interrupt line/pin, min grant, and max latency.
- PCIe capability fields: capability list/header, endpoint device capability/control/status, link capability/control/status, and PCIe 2.0+ `DEVICE_CAP2`, `DEVICE_CNTL2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- MSI/MSI-X fields: MSI message control/address/data/mask/pending registers in 32-bit and 64-bit forms, plus MSI-X capability, table BIR/offset, PBA BIR/offset, function mask, enable, and table size.
- Vendor-specific extended capability fields: extended capability header, VSEC ID/revision/length, and two full-width vendor-specific data registers.
- AER fields: uncorrectable error status/mask/severity, correctable error status/mask, advanced error capability/control, four TLP header-log dwords, and four TLP prefix-log dwords.
- ATS fields: enhanced capability header, invalidation queue depth, page-aligned/global-invalidate/relaxed-ordering support, smallest translation unit, and ATC enable.
- ARI fields: enhanced capability header, group capability bits, next function number, group enable bits, and function group selector.

These macros define the values exposed in the VF PCI configuration image rather than ordinary runtime queue state. They are tied to PCIe enumeration, interrupt programming, AER diagnostics, IOMMU address-translation behavior, and SR-IOV function routing.

### VF0-VF2 BIF PF/VF Decode Blocks

The `BIF_BX_DEV0_EPF0_VF0_*`, `VF1_*`, and `VF2_*` blocks expose per-VF BIF control/status registers. The repeated layout is important because driver code and firmware can index across VFs while expecting identical bit positions:

- `BIF_BME_STATUS` records DMA activity while bus mastering is low and includes a clear bit. This is a VF isolation and debug signal for bus-master-enable violations.
- `BIF_ATOMIC_ERR_LOG` records unsupported or invalid atomic request conditions: opcode, request-enable-low, length, and non-relaxed/non-request state, each with matching clear bits.
- `DOORBELL_SELFRING_GPA_APER_BASE_HIGH`, `BASE_LOW`, and `CNTL` configure a self-ring doorbell GPA aperture, including enable, mode, and size.
- `HDP_REG_COHERENCY_FLUSH_CNTL`, `HDP_MEM_COHERENCY_FLUSH_CNTL`, `HDP_MEM_COHERENCY_FLUSH_ONLY_CNTL`, and `HDP_MEM_COHERENCY_INVALIDATE_ONLY_CNTL` provide per-VF coherency flush/invalidate control hooks.
- `GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE` expose one bit per engine class: `CP0` through `CP9`, `SDMA0`, `SDMA1`, and reserved engine slots 0 through 19. The request/done pairing is the bit protocol used to order CPU-visible memory and GPU/HDP writes.
- `BIF_TRANS_PENDING` indicates outstanding BIF master/slave transactions.
- `NBIF_GFX_ADDR_LUT_BYPASS` controls graphics address LUT bypass.
- `MAILBOX_MSGBUF_TRN_DW0..DW3` and `MAILBOX_MSGBUF_RCV_DW0..DW3` provide 128-bit transmit and receive message buffers.
- `MAILBOX_CONTROL` provides transmit valid/ack and receive valid/ack handshake bits; `MAILBOX_INT_CNTL` controls valid/ack interrupt enables.
- `BIF_VMHV_MAILBOX` provides a compact hypervisor/VF mailbox register with interrupt enables, transmit/receive data fields, valid bits, and ack bits.

AMDGPU NBIO 7.9 code uses the corresponding VF0 HDP coherency flush address when setting MMIO remap state for SR-IOV VF operation. The broader VF1/VF2 definitions are present for the same hardware layout even if this source tree's direct C references are mostly to VF0 offsets.

### VF0-VF2 System MMIO Index/Data Registers

Each VF has a small `SYSPFVFDEC` block:

- `MM_INDEX` contains a low MMIO offset and `MM_APER` aperture selector.
- `MM_DATA` contains the data payload.
- `MM_INDEX_HI` contains high MMIO offset bits.

Together these define an indexed access window. The split high/low offset fields are a dependency for any code or firmware path that needs to reach VF MMIO spaces wider than the low index field can encode.

### VF0-VF2 RCC Blocks and MSI-X Table State

The `RCC_DEV0_EPF0_VF0_*`, `VF1_*`, and `VF2_*` blocks expose resource/configuration controller state:

- `RCC_ERR_LOG` records invalid register access in SR-IOV mode and doorbell read access status.
- `RCC_DOORBELL_APER_EN` controls BIF doorbell aperture enable.
- `RCC_CONFIG_MEMSIZE` and `RCC_CONFIG_RESERVED` are full-width configuration values.
- `RCC_IOV_FUNC_IDENTIFIER` exposes a function identifier and a top-bit `IOV_ENABLE`.
- `GFXMSIX_VECT0..VECT3_ADDR_LO`, `ADDR_HI`, `MSG_DATA`, and `CONTROL` describe four GFX MSI-X vector table entries. Low message addresses are masked from bit 2 upward, preserving PCIe MSI-X alignment.
- `GFXMSIX_PBA` exposes pending bits for MSI-X vectors 0 and 1 in this range.

These fields integrate PCIe interrupt delivery with virtualized graphics functions. Mask-bit definitions in the vector controls are security and reliability relevant because they determine whether a VF can generate interrupts into programmed host addresses.

## Control Flow and State Behavior

This chunk has no executable control flow. The effective runtime flow is in callers that read, compose, and write register values:

1. A caller obtains an address from the matching offset header, often through `SOC15_REG_OFFSET` or `reg*` symbols.
2. It reads a register with an AMDGPU MMIO helper or starts from a zero/local value.
3. It extracts or updates fields using the `__SHIFT` and `_MASK` constants through `REG_GET_FIELD` or `REG_SET_FIELD`.
4. It writes the result back through an AMDGPU register helper or uses the computed offset for an MMIO remap.

The state represented here is hardware-resident and partly guest/host visible:

- PCI configuration-space fields persist in the device's config image across normal software reads and writes and are reset by device/function reset flows.
- Error status registers such as BME, atomic, AER, and RCC error logs are sticky hardware status surfaces with explicit clear bits or write-one-clear style behavior implied by the paired clear/status fields.
- Mailbox valid/ack bits are handshake state between VF, PF, and hypervisor-facing firmware/software. Ordering matters: data words must be coherent with valid/ack transitions.
- HDP flush request/done fields are synchronization state. Software must not treat request bits as complete until matching done bits are observed.
- MSI/MSI-X address/data/control state controls interrupt routing and remains active until rewritten, masked, reset, or disabled through PCI/MSI-X control.

## Dependencies and Integration Points

The main dependencies are generated AMD ASIC register headers:

- `nbio_7_9_0_offset.h` supplies matching `reg*` addresses and base indices for NBIO 7.9.0 registers.
- This `nbio_7_9_0_sh_mask.h` chunk supplies bit encodings for those addresses.
- NBIF offset headers expose matching configuration-space offsets for the VF config images.
- `amdgpu/nbio_v7_9.c` includes this header and uses NBIO masks for register programming, MMIO remap setup, doorbell programming, HDP flush offsets, interrupt control, partition status, and clock/power-management related NBIO state.
- `ras/ras_mgr/amdgpu_ras_nbio_v7_9.c` includes the header alongside NBIO offset and IRQ source headers for NBIO RAS interrupt registration.

Important integration surfaces are PCIe/SR-IOV enumeration, VF BAR and memory decode, host/VF interrupt programming, IOMMU/ATS behavior, HDP coherency, doorbell apertures, mailbox communication, and RAS/error reporting. Because these are preprocessor constants, compile-time success only proves that macro names exist; it does not prove that field values match the hardware specification.

## Risks

- Generated-header drift: any mismatch between these masks and `nbio_7_9_0_offset.h` or the ASIC register specification can silently corrupt field extraction or writes.
- VF isolation risk: command, BAR, BME, doorbell, ATS, ARI, RCC error, and address LUT fields directly affect SR-IOV isolation boundaries and host/VF routing.
- Interrupt routing risk: MSI/MSI-X address/data/control masks must preserve alignment and mask semantics; wrong fields can misroute interrupts or leave vectors unmasked.
- Error handling risk: AER, atomic error, BME status, and RCC error-log masks must distinguish status bits from clear bits. Confusing them can either fail to clear errors or clear diagnostics before they are consumed.
- Coherency risk: HDP flush request/done masks must stay synchronized across engine bits. Missing or shifted done bits can make software observe stale GPU writes or wait on the wrong engine.
- Mailbox protocol risk: transmit/receive valid and ack bits are packed near data fields. Incorrect masks can cause lost messages, duplicate acknowledgements, or unexpected interrupts.
- Chunk-boundary risk: this slice starts mid-VF5 ARI capability and ends just before VF3 BIF definitions. Review or generated-doc tooling must merge adjacent chunks before drawing conclusions about the full source file.

## Test Signals

Useful validation signals for changes touching this generated area include:

- Build coverage for AMDGPU NBIO 7.9 users, especially `drivers/gpu/drm/amd/amdgpu/nbio_v7_9.c` and `drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_nbio_v7_9.c`, to catch renamed or missing macros.
- Generated-header consistency checks comparing `*_SHIFTS`, `_MASK` values, and register comments against the authoritative ASIC register database and the matching offset header.
- SR-IOV boot and enumeration tests that create PF/VF configurations and verify VF6/VF7 config-space visibility, ARI routing, ATS advertisement/control, BAR layout, and MSI/MSI-X capability behavior.
- VF interrupt tests that program MSI-X vectors, toggle vector mask bits, and verify pending-bit behavior through the RCC GFXMSIX fields.
- Doorbell and self-ring aperture tests that confirm enable/mode/size/base fields isolate each VF's doorbell aperture.
- HDP coherency tests that issue flush requests for CP and SDMA engines and verify the expected `GPU_HDP_FLUSH_DONE` bits before reading host-visible memory.
- Mailbox tests that exercise transmit/receive data words, valid/ack transitions, and interrupt enable bits across PF/hypervisor/VF paths.
- Error-injection or negative-access tests that trigger BME-low DMA, invalid atomic operations, invalid SR-IOV register accesses, and AER status paths, then verify status and clear-bit behavior.

### subset-b-003342: lines 37219-38900

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_sh_mask.h lines 37219-38900

## Scope

This chunk is the tail of the generated AMD NBIO 7.9.0 shift/mask header. It contains C preprocessor constants only: bit-position `__SHIFT` macros and bit-field `MASK` macros for NBIO/BIF/RCC registers. The range begins with the final four masks for the VF2 RCC MSI-X pending-bit array, then covers the complete repeated virtual-function field definitions for `DEV0_EPF0` VF3 through VF7, and ends at the header guard's closing `#endif`.

The source is part of AMDGPU's generated register database under `drivers/gpu/drm/amd/include/asic_reg/nbio`. It defines no executable code, functions, types, storage, locks, callbacks, or direct register access helpers. Its role is to describe field layouts for register addresses supplied by companion offset headers.

## Purpose and Register Families

The macros describe bit layouts for SR-IOV virtual-function register windows in NBIO 7.9.0 hardware. For each VF3 through VF7, the chunk repeats the same register families with the VF number encoded in the macro name:

- `BIF_BX_DEV0_EPF0_VF<n>_BIF_BME_STATUS`: bus-master enable status, including `DMA_ON_BME_LOW` and a clear bit at bit 16.
- `BIF_BX_DEV0_EPF0_VF<n>_BIF_ATOMIC_ERR_LOG`: unsupported or invalid PCIe atomic operation flags plus corresponding clear bits at bits 16-19.
- `DOORBELL_SELFRING_GPA_APER_BASE_HIGH`, `_BASE_LOW`, and `_CNTL`: doorbell self-ring guest-physical aperture base and enable/mode/size fields.
- `HDP_REG_COHERENCY_FLUSH_CNTL`, `HDP_MEM_COHERENCY_FLUSH_CNTL`, `HDP_MEM_COHERENCY_FLUSH_ONLY_CNTL`, and `HDP_MEM_COHERENCY_INVALIDATE_ONLY_CNTL`: one-bit HDP register/memory coherency control fields.
- `GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE`: one bit per request/completion source, covering CP0-CP9, SDMA0-SDMA1, and reserved engine bits through bit 31.
- `BIF_TRANS_PENDING`: master and slave transaction-pending status bits.
- `NBIF_GFX_ADDR_LUT_BYPASS`: a one-bit graphics address LUT bypass field.
- `MAILBOX_MSGBUF_TRN_DW0..DW3` and `MAILBOX_MSGBUF_RCV_DW0..DW3`: full 32-bit transmit and receive mailbox data words.
- `MAILBOX_CONTROL` and `MAILBOX_INT_CNTL`: transmit/receive valid/ack bits and valid/ack interrupt enables.
- `BIF_VMHV_MAILBOX`: compact VM/HV mailbox fields for interrupt enables, 4-bit transmit/receive message payloads, valid bits, and ack bits.
- `MM_INDEX`, `MM_DATA`, and `MM_INDEX_HI`: indexed register access fields in the VF system PF/VF decode block.
- `RCC_ERR_LOG`, `RCC_DOORBELL_APER_EN`, `RCC_CONFIG_MEMSIZE`, `RCC_CONFIG_RESERVED`, and `RCC_IOV_FUNC_IDENTIFIER`: RCC-side SR-IOV status/configuration fields.
- `RCC_GFXMSIX_VECT0..3_{ADDR_LO,ADDR_HI,MSG_DATA,CONTROL}` and `RCC_GFXMSIX_PBA`: MSI-X vector address/data/mask and pending-bit fields.

The trailing VF7 block is immediately followed by `#endif`, so this chunk closes the file. The first four lines belong to the prior VF2 MSI-X PBA block and should be reconciled with the preceding chunk during merge.

## Important APIs, Types, and Macros

This file's interface is the AMDGPU register-field macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the already-shifted mask used for extraction, composition, or clearing.
- The register prefix includes the hardware path and VF number, for example `BIF_BX_DEV0_EPF0_VF5_MAILBOX_CONTROL__RCV_MSG_VALID_MASK`.

These macros are normally paired with the same register names from `nbio_7_9_0_offset.h` and accessed through AMDGPU/SOC15 helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, and related instance-aware variants. The chunk itself does not call those helpers.

The header is included directly by:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_9.c`, which performs NBIO 7.9.0 initialization, register remapping, doorbell setup, memory-controller access toggles, and revision/memsize queries.
- `drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_nbio_v7_9.c`, which wires NBIO RAS interrupt sources and includes the register database even though its handlers are currently dummy hooks.

Specific VF3-VF7 macros in this chunk are generated definitions and may be consumed indirectly by future or configuration-specific NBIO, SR-IOV, RAS, debug, or register-dump paths.

## Control Flow and Data Flow

There is no runtime control flow in the chunk. The effective flow at runtime is:

1. AMDGPU builds NBIO 7.9.0 support and includes the offset and shift/mask headers.
2. Driver code reads a hardware register identified by a `reg...` macro from the companion offset file.
3. Driver code uses these `__SHIFT` and `_MASK` macros, usually through `REG_GET_FIELD` or `REG_SET_FIELD`, to extract or compose a field value.
4. The result affects hardware state such as VF doorbell apertures, HDP coherency operations, mailbox handshakes, BIF transaction status, RCC error reporting, function identification, or MSI-X interrupt delivery.

The repeated VF blocks imply per-virtual-function isolation: the same field layout exists for VF3, VF4, VF5, VF6, and VF7, but each macro names a separate VF register window. The field values themselves are not held in software; they are MMIO/configuration-visible hardware register bits.

## State and Persistence

The header has only compile-time constants and no mutable state or persistence.

The hardware state described by the masks is persistent according to NBIO, PCIe, SR-IOV, reset, and power-domain semantics:

- Doorbell aperture base/control fields define where a VF's doorbell self-ring aperture is exposed and whether it is enabled.
- HDP coherency request/control fields coordinate CPU/GPU-visible memory ordering and cache flush/invalidate behavior.
- `GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE` form a request/acknowledgement register pair across command processor, SDMA, and reserved engine sources.
- Mailbox message buffers and control bits represent PF/VF or VM/HV communication state; valid and ack bits are handshake state that can be updated asynchronously by hardware/firmware peers.
- BME, atomic error, transaction-pending, and RCC error-log fields are status or clear-on-write style indicators; their precise clear/read behavior comes from the hardware specification, with this header only providing the bit geometry.
- MSI-X vector table and PBA fields hold interrupt target addresses, message data, mask bits, and pending indicators for VF interrupt delivery.

An incorrect mask or shift is a compile-time constant bug that can systematically corrupt field extraction/composition wherever used.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header ecosystem for NBIO 7.9.0:

- `nbio_7_9_0_offset.h` supplies the corresponding register addresses and base indices.
- AMDGPU register helper macros consume the shifts and masks for field-level reads and writes.
- `nbio_v7_9.c` is the main NBIO 7.9.0 integration point; it includes this file alongside the offset header and uses related NBIO fields for hardware initialization paths.
- `amdgpu_ras_nbio_v7_9.c` includes this header for NBIO RAS integration with BIF interrupt source IDs.
- SR-IOV/virtualization code paths depend on the VF-numbered register layout remaining isolated and consistent across VF3-VF7.
- PCIe/MSI-X behavior depends on the RCC MSI-X vector/PBA field layout matching the device's PCI configuration semantics.

The repeated macro blocks also mirror generated NBIF/NBIO headers for other ASIC revisions, which can help reviewers spot generator drift, but NBIO 7.9.0 hardware documentation remains the authority for semantics.

## Risks and Edge Cases

- The chunk boundary starts inside the VF2 RCC MSI-X PBA block. The merge lane should preserve those four VF2 field definitions with the preceding VF2 material.
- Repetition across VF3-VF7 makes generator or copy errors easy to miss. A single wrong VF number, mask, or shift may only fail when that virtual function is enabled.
- Full-width fields such as mailbox data, config memsize/reserved, MM data, and address high/low masks use `0xFFFFFFFFL`; callers must avoid extra shifts or signed assumptions.
- MSI-X address-low fields start at bit 2 and mask with `0xFFFFFFFC`, reflecting alignment. Treating them as full 32-bit low addresses would mishandle the low reserved bits.
- Clear/status pairs use separate low status bits and high clear bits for BME and atomic error logs. Code must not blindly write a readback value without understanding write-one-to-clear semantics.
- HDP flush request/done fields are synchronization-sensitive. Wrong bit selection can produce hangs, stale memory visibility, or false completion.
- Mailbox valid/ack and interrupt-enable bits cross software/firmware or PF/VF boundaries. Misusing the masks can lose messages, wedge a handshake, or signal the wrong side.
- `RCC_IOV_FUNC_IDENTIFIER` exposes a one-bit function identifier plus `IOV_ENABLE` at bit 31 in this generated block; code assuming a wider function id would not match these masks.

## Test and Validation Signals

Useful validation is mostly compile-time plus hardware integration:

- Build AMDGPU with NBIO 7.9.0 enabled so the include paths and generated macro names are validated.
- Compare this shift/mask header against `nbio_7_9_0_offset.h` to ensure every VF3-VF7 register address has matching field definitions.
- Exercise SR-IOV with multiple VFs, especially VF3 through VF7, and verify doorbell programming, queue submission, and mailbox handshakes per VF.
- Validate HDP coherency paths under GPU memory workloads by checking that flush requests reach done bits without hangs or stale host/GPU data.
- Test MSI-X interrupt delivery per VF: vector address/data programming, mask/unmask behavior, and PBA pending-bit updates.
- Check BME, atomic error, RCC error-log, and BIF transaction-pending reporting during reset, FLR, illegal access, and PCIe stress scenarios.
- Run suspend/resume and GPU reset flows to confirm VF doorbell, mailbox, HDP, and MSI-X state is either restored by the responsible driver path or reset by hardware/firmware as expected.
