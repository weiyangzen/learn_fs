# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_1_sh_mask.h lines 5620-8351

## Scope

This chunk is part of AMDGPU's generated NBIF 6.1 register bitfield mask header. It contains C preprocessor `#define` constants only, almost entirely `REGISTER__FIELD__MASK` macros for 32-bit hardware register fields. The companion earlier part of the same header provides the matching `__SHIFT` constants; companion generated address headers provide register offsets. There are no C functions, structs, enums, allocations, locks, or executable control flow in this chunk.

The covered range starts at the tail of the PCIe BAR3 control masks and ends in the duplicated internal RCC strap view for `RCCSTRAPRCCSTRAP_RCC_DEV0_EPF0_STRAP2`. Because this is a large generated header, adjacent chunks are required to reconstruct the complete per-file narrative and to preserve families split at the boundaries.

## Purpose

The chunk describes NBIF/Pcie/GDC/SION/SYSHUB/RCC bit layouts used by AMDGPU and related virtualization paths to program the PCIe-facing northbridge interface. Major purposes include:

- PCIe extended capability masks for BAR resize capability/control, power budgeting, Dynamic Power Allocation, Secondary PCIe, lane equalization, ACS, ATS, Page Request Interface, PASID, TPH requester, multicast, LTR, ARI, and SR-IOV.
- AMD vendor-specific GPU IOV capability masks for VF enablement, mailbox signaling, interrupt/status bits, reset control, context location, framebuffer accounting, per-VF framebuffer size/offsets, and UVD/VCE/GFX scheduler data words.
- Bridge, shadow, and indirect-access register masks for downstream bridge windows, upstream-shadowed bridge settings, SUC/SUM indexed data windows, MM/PCIE/SYSHUB indirect apertures, and PCIe endpoint/downstream hidden configuration controls.
- GDC/SION/SYSHUB controls for address-to-system response mapping, SION credit and timeslot programming, clock/deep-sleep gating, QoS, RAS leaf error controls, and reset lines.
- BIF system controls for scratch registers, GPUIOV/RLC/UVD/VCE interrupts, MMIO CAM remapping, doorbell ranges, ring buffer state, HDP flush requests/done bits, mailbox transport/receive buffers, BACO power-state timers, VDDGFX gated register ranges, and performance counters.
- RCC root-complex/controller controls, MSI-X tables, peer framebuffer offsets, bus/devfunc filters, host-bus capture, and extensive strap fields for port and endpoint-function capability advertisement.

The macros let driver code build and decode register values through field-aware helpers instead of embedding raw hexadecimal constants in call sites.

## Important Macro Families

`PCIE_BAR4_CAP/CNTL` through `PCIE_BAR6_CAP/CNTL` and the tail of `PCIE_BAR3_CNTL` define resize BAR capability and control fields. The control masks expose BAR index, total count, and selected size; the capability masks expose supported sizes. These are relevant to resizable BAR setup and hardware capability reporting.

`PCIE_PWR_BUDGET_*`, `PCIE_DPA_*`, and `PCIE_F0_DPA_*` describe power budget and Dynamic Power Allocation capability fields. They encode capability-list IDs/versions/next pointers, base power, scale, PM state/substate, power rail, DPA substates, transition latency units/values, substate status/control, and per-substate power allocations 0-7.

`PCIE_LINK_CNTL3`, `PCIE_LANE_ERROR_STATUS`, and `PCIE_LANE_0_EQUALIZATION_CNTL` through `PCIE_LANE_15_EQUALIZATION_CNTL` provide Gen3 link-equalization controls and lane status fields. The repeated lane layout has downstream/upstream TX presets, RX preset hints, and a reserved bit. Any code that touches these fields is operating on training/equalization hardware behavior.

`PCIE_ACS_*`, `PCIE_ATS_*`, `PCIE_PAGE_REQ_*`, and `PCIE_PASID_*` define isolation and address-translation capability/control fields. ACS covers source validation, translation blocking, peer-to-peer redirection, upstream forwarding, egress control, and direct translated P2P. ATS exposes invalidate queue depth, page-aligned request and global invalidate support, STU, and ATC enable. PRI/Page Request exposes enable/reset/status/capacity/allocation fields. PASID exposes execute/privilege support, max PASID width, and enable bits.

`PCIE_TPH_REQR_*`, `PCIE_MC_*`, `PCIE_LTR_*`, and `PCIE_ARI_*` describe optional PCIe capabilities: TPH requester modes and steering table shape, multicast group/window/register masks, latency tolerance reporting values/scales, and ARI function-group/next-function controls.

`PCIE_SRIOV_*` defines SR-IOV capability, control, status, VF count, VF offset/stride/device ID, page-size, VF BAR, and migration-state array offset masks. These are the public PCIe SR-IOV capability registers exposed by the device.

`PCIE_VENDOR_SPECIFIC_*_GPUIOV` is the AMD GPU IOV vendor-specific capability block. It includes VSEC header identity/length, shadow SR-IOV state, interrupt enable/status bits for GFX/UVD/VCE command completion, self-recovered hangs, FLR-needed hangs, VM-busy transitions, and hypervisor/VM mailbox valid/ack events. The mailbox fields cover selected VF index, transmit/receive message nibbles, valid/ack handshakes for VF0-VF15 and PF, plus four full-word transmit and receive message buffers in the later BIFPFVF block. The capability also carries context size/location/offset, total framebuffer available/consumed, scheduler offset words, per-VF framebuffer size/offset entries for VF0-VF15, and full 32-bit scheduler words for UVD, VCE, and GFX.

`SUB_BUS_NUMBER_LATENCY`, `IO_BASE_LIMIT`, `MEM_BASE_LIMIT`, `PREF_BASE_LIMIT`, upper limit/base registers, `IRQ_BRIDGE_CNTL`, `SLOT_*`, and `SSID_*` are PCI-to-PCI bridge and slot/subsystem capability masks. The matching `SHADOW_*` registers in `rcc_shadow_reg_shadowdec` mirror selected upstream bridge settings such as command, BARs, bus numbers, I/O and memory window limits, and bridge-control bits.

`SUC_INDEX/DATA`, `SUM_INDEX/DATA`, `MM_INDEX/MM_DATA/MM_INDEX_HI`, `PCIE_INDEX/DATA`, `PCIE_INDEX2/DATA2`, `SYSHUB_INDEX/DATA`, and `SYSHUB_INDEX_OVLP/DATA_OVLP` define indexed or indirect register access windows. These masks are full-width data/index selectors, except where aperture or high-offset bits are separated.

`A2S_CNTL_CL0` through `A2S_CNTL_CL4`, `A2S_CNTL_SW0` through `A2S_CNTL_SW2`, `A2S_MISC_CNTL`, `S2A_MISC_CNTL`, and `A2S_CNTL2_SEC_CL*` configure GDC address-to-system mapping, response/reorder behavior, request pass-through mapping, read/write weights, security-level mapping, and 64-bit doorbell support disable bits. The adjacent doorbell range masks cover SDMA0, SDMA1, IH, and MMSCH0 offsets/sizes plus a doorbell fence enable.

`SION_CL0` through `SION_CL5` repeat a 64-bit split-register model for read response, write response, request burst targets, timeslots, and request/data/read-response/write-response pool credit allocations. `SION_CNTL_REG0` exposes many clock override bits and `SION_CNTL_REG1` exposes livelock watchdog and clock-gating hysteresis values.

`SYSHUB_*` masks cover SOCCLK and SHUBCLK deep-sleep controls, bgen bypass/immediate-enable controls, DMA QoS controls, per-client clock/reset/QoS static overrides, clock-gating timers, transaction-idle reporting for VF0-VF15 plus PF, and scratch/timer registers. These fields integrate NBIF traffic management with power management and virtualization-aware idle detection.

`GDC_RAS_LEAF0_CTRL` through `GDC_RAS_LEAF5_CTRL` repeat poison/parity detection enable, error-event enable, stall enable, received/sent event, link-disable, detected-error, and egress-stalled bits. `SHUB_*_RST` masks cover PF FLR reset lines, PF0 VF0-VF15 FLR resets, soft PF FLR reset, link reset, hard/soft reset enables for core/register/sticky/NIC400/SDP paths, and SDP port reset.

`SBIOS_SCRATCH_*`, `BIOS_SCRATCH_*`, `BIF_SCRATCH*`, and `SYSHUB_SCRATCH` are full-width persistence/communication registers. `BIF_RLC_INTR_CNTL`, `BIF_VCE_INTR_CNTL`, and `BIF_UVD_INTR_CNTL` mirror GPUIOV-style command complete, self-recovered hang, FLR-needed hang, and VM-busy transition bits for specific engines.

`GFX_MMIOREG_CAM_*` provides eight CAM address/remap pairs plus enable and completion-value registers. These fields are used to remap selected GFX MMIO register accesses and define zero/one/programmed completion behavior.

`DN_PCIE_*`, `PCIEP_*`, and `EP_PCIE_*` define downstream, port, and endpoint control fields: hardware-init write locks, UR/error reporting controls, LTR ignore behavior, hidden config decode enables, strap fields, PCIe RX error ignores, link-speed straps, OBFF controls, LTR transmit controls, requester ID fields, PME service timers, and endpoint interrupt enable/status bits.

`BUS_CNTL`, `BIF_FEATURES_CONTROL_MISC`, `BIF_DOORBELL_CNTL`, `BIF_DOORBELL_INT_CNTL`, `BIF_RB_*`, `BIF_TRANS_PENDING`, `BIF_BME_STATUS`, `BIF_ATOMIC_ERR_LOG`, `GPU_HDP_FLUSH_REQ/DONE`, `MAILBOX_*`, and `BIF_VMHV_MAILBOX` are central NBIF runtime masks. They cover power-management interrupt disables, VGA coherency, traffic-class overrides, reset behavior, interrupt generation, doorbell monitoring and interrupts, framebuffer access enable, ring buffer state/writeback, transaction-pending status, bus-master/atomic error logging, HDP flush request/done bits for CP0-CP9 and SDMA0-1, and a PF/VF mailbox valid/ack protocol.

`BACO_CNTL` and `BIF_BACO_EXIT_TIMER*` describe BACO low-power state entry/exit and timers, including enable, LCLK switch, dummy/power-off bits, reset interrupt mask, mode, config-done, auto-exit, sideband/lclk/dummy/enable clear timers, and hardware-exit behavior.

`BIF_VDDGFX_*` masks define lower/upper register address ranges for GFX0-GFX5 and reserved ranges, with compare-enable and stall-enable controls, plus framebuffer compare/stall enables for HDP, XDMA, and VGA. These fields gate or stall selected accesses while the GFX power domain is off.

`RCC_*` masks cover root-complex/control behavior: BACO request disables, DB aperture reset, vendor-defined message support, peer register ranges, bus control and error logging modes, VGA/config aperture sizing, XDMA bounds, UR/poison and pending-packet feature controls, bus number/devfunc filter lists, host bus capture, peer framebuffer offsets/enables for peers 0-3, link-down entry/exit bits, LTR switch latency, multihost arbitration, and three GFX MSI-X vector entries plus PBA bits.

`RCC_DEV0_PORT_STRAP*`, `RCC_DEV1_PORT_STRAP*`, `RCCSTRAPRCCSTRAP_RCC_DEV0_PORT_STRAP*`, `RCC_DEV0_EPF0_STRAP*`, `RCC_DEV0_EPF1_STRAP*`, and the internal `RCCSTRAPRCCSTRAP_RCC_DEV0_EPF0_STRAP*` aliases encode boot/strap-time capability advertisement. They include ARI/ACS/AER/ATS/PASID/SR-IOV/DPA/DSN/VC/atomic enablement, device/subsystem IDs, class codes, interrupt pins, max payload/read/link width/speed, link latencies, LTR/OBFF/MSI/MSI-X/PME/AUX power support, BAR/doorbell/register/ROM aperture sizing, resizable BAR support, VF mapping mode, and port/bus/dev/function identifiers.

## Control Flow and State

This header has no executable control flow. The implied hardware flows are encoded by related field groups:

1. Enumeration or firmware/strap setup exposes PCIe capability state through BAR, bridge, slot, ACS/ATS/PRI/PASID, SR-IOV, and vendor-specific GPU IOV fields.
2. Driver initialization programs NBIF, GDC, SION, SYSHUB, RCC, doorbell, mailbox, indirect-access, MMIO CAM, and power-management registers using these masks and matching shifts/offsets from generated companion headers.
3. Runtime virtualization paths use SR-IOV and GPUIOV masks to enable VFs, size and map VF framebuffer regions, exchange mailbox messages, handle valid/ack interrupts, and request PF/VF FLR or reset notifications.
4. Runtime synchronization paths issue HDP flush requests for CP/SDMA clients and wait for the matching `GPU_HDP_FLUSH_DONE` bits, inspect `BIF_TRANS_PENDING`, and manage ring-buffer write/read pointers.
5. Power-management and reset paths use BACO, VDDGFX range-stall, deep-sleep, clock-gating, FLR, hard/soft reset, link reset, and strap write-once controls.
6. Error handling and diagnostics use RAS leaf controls, PCIe error/interrupt status, atomic error logs, doorbell/RAS interrupt clear bits, BME status, performance counters, scratch registers, and MSI-X vector/PBA fields.

State persists in hardware registers rather than in this header. Some fields are stable configuration until reset or later writes, such as strap-derived capability bits, aperture bounds, doorbell ranges, VF sizes, bus filters, QoS weights, and deep-sleep enables. Other fields are transient or write-to-clear/handshake controls, such as reset request bits, mailbox valid/ack bits, HDP flush request/done bits, interrupt status/clear masks, atomic/BME clear bits, and ring-buffer overflow clear.

## Dependencies and Integration Points

These macros depend on the C preprocessor and on the generated AMD register naming convention. Driver code normally combines them with:

- companion NBIF 6.1 register offset/address headers under `drivers/gpu/drm/amd/include/asic_reg/nbif`;
- matching `__SHIFT` macros from the earlier portion of this same `nbif_6_1_sh_mask.h` file;
- AMDGPU register helpers such as field set/get macros and MMIO/indirect register accessors;
- PCIe, SR-IOV, IOMMU/ATS/PASID/PRI, interrupt, mailbox, doorbell, HDP flush, BACO, reset, RAS, and power-management code in the AMDGPU kernel driver;
- virtualization management code that interprets GPUIOV vendor-specific capability registers and PF/VF mailbox/register state.

The repository path is under `sources/distributed-fs/ceph-client`, but the source file itself is Linux AMD GPU DRM driver hardware-description data. It does not integrate with Ceph client behavior.

## Risks

Bitfield correctness is critical. A wrong mask in this file can silently write or decode the wrong hardware bits, causing PCIe capability misreporting, failed link training, broken resizable BAR setup, invalid SR-IOV VF enumeration, missing interrupts, lost mailbox handshakes, bad doorbell routing, stale HDP flushes, failed reset/FLR, or hangs in BACO/deep-sleep transitions.

The chunk is highly repetitive. Generation or merge errors are plausible around numeric suffixes for lanes 0-15, VF0-VF15, CP0-CP9, SION CL0-CL5, GFX MMIO CAM0-7, BIOS scratch0-15, RCC peer0-3, MSI-X vectors 0-2, and strap families for DEV0/DEV1 and EPF0/EPF1. The range starts and ends mid-family, so final reconciliation must verify neighboring chunks for the missing beginning/end of split register groups.

Several fields are security/isolation sensitive. ACS/ATS/PRI/PASID, SR-IOV, GPUIOV per-VF framebuffer allocation, VF register protection, peer framebuffer windows, requester IDs, and doorbell aperture controls define isolation between PF, VFs, host, and peer devices. Incorrect caller use can expose memory or MMIO across functions or devices.

Power and reset fields are stateful and timing sensitive. BACO timers, VDDGFX stall ranges, deep-sleep enables, clock-gating hysteresis, FLR reset bits, and link reset controls must be sequenced by higher-level code. The masks do not enforce ordering, polling, or timeout behavior.

Error/status bits may be write-one-to-clear or handshake-driven depending on the hardware register contract. Code must not treat all masked fields as ordinary read/write storage; status/clear/valid/ack fields such as mailbox, interrupt, atomic, BME, HDP flush, and RAS bits need protocol-specific handling.

## Test and Validation Signals

Useful validation is mostly compile-time and hardware-integration level:

- AMDGPU builds that include `nbif_6_1_sh_mask.h` and use NBIF 6.1 register helpers; missing, renamed, or malformed macros should fail compilation.
- Register readback tests for PCIe BAR, ACS/ATS/PRI/PASID, SR-IOV, GPUIOV, doorbell, RCC, and bridge-window fields after initialization.
- PCIe link tests that validate advertised link widths/speeds, Gen2/Gen3 strap behavior, lane equalization settings, AER/error reporting, LTR/OBFF, and resizable BAR capability/control.
- SR-IOV tests that create/destroy VFs, verify VF BAR/framebuffer sizing, validate ACS/ATS/PASID/PRI isolation, exercise PF/VF FLR, and confirm GPUIOV mailbox valid/ack interrupts.
- HDP flush tests that write `GPU_HDP_FLUSH_REQ` bits for CP and SDMA clients and verify corresponding `GPU_HDP_FLUSH_DONE` bits before memory-visible operations continue.
- Doorbell tests that confirm SDMA/IH/MMSCH/global/self-ring apertures, interrupt status/clear bits, and GPA aperture controls behave as expected.
- Power/reset tests covering BACO entry/exit timers, VDDGFX access stalls, deep-sleep/clock-gating controls, PF/VF FLR masks, hard/soft reset enables, and transaction-pending checks.
- RAS and error-injection tests for GDC RAS leaf poison/parity detection, PCIe endpoint/downstream interrupt status, BME-low DMA status, atomic unsupported request logging, and MSI-X vector/PBA behavior.

## Cross-Chunk Notes

This report covers only lines 5620-8351. The first two lines belong to the end of `PCIE_BAR3_CNTL`, and the final line stops inside `RCCSTRAPRCCSTRAP_RCC_DEV0_EPF0_STRAP2`. Earlier chunks contain preceding PCIe config/header capability masks and matching shift macros; later chunks should contain the remainder of the internal EPF0 strap2 fields and subsequent NBIF strap/register blocks. The final per-file document should reconcile duplicate strap aliases (`RCC_DEV0_*` versus `RCCSTRAPRCCSTRAP_RCC_DEV0_*`) and explain that this generated header supplies bit masks, not behavior by itself.
