# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_1_sh_mask.h lines 1-2921

## Scope

This chunk covers the first 2,921 lines of AMDGPU's generated NBIF 6.1 register field header. It starts with the MIT-style AMD copyright and include guard, then defines field-position macros for the first part of the NBIF register map. The chunk contains 2,118 `#define` entries in the covered range. They are almost entirely `REGISTER__FIELD__SHIFT` constants; the corresponding `REGISTER__FIELD_MASK` constants are not present in this line range and appear later in the full generated header. There are no C functions, structs, enums, allocated data, or executable control flow.

The visible address blocks are:

- `bif_cfg_dev0_epf0_bifcfgdecp`
- `bif_cfg_dev0_swds_bifcfgdecp`
- `rcc_shadow_reg_shadowdec`
- `bif_bx_pf_SUMDEC`
- `gdc_GDCDEC`
- `nbif_sion_SIONDEC`
- `syshub_mmreg_direct_syshubdirect`
- `gdc_ras_gdc_ras_regblk`
- `gdc_rst_GDCRST_DEC`
- `bif_bx_pf_SYSDEC`
- `bif_bx_pf_SYSPFVFDEC`
- `rcc_dwn_BIFDEC1`
- `rcc_dwnp_BIFDEC1`
- `rcc_ep_BIFDEC1`
- `bif_bx_pf_BIFDEC1`
- `rcc_pf_0_BIFDEC1`
- `rcc_pf_0_BIFDEC2`
- `rcc_strap_BIFDEC1`
- beginning of `bif_bx_pf_BIFPFVFDEC1`

## Purpose

`nbif_6_1_sh_mask.h` is a generated hardware ABI header for the NBIF/NBIO PCIe and bridge fabric block on AMD GPUs. This chunk tells driver code where each field begins inside 32-bit hardware registers. Driver code normally pairs these shift definitions with register offsets from `nbif_6_1_offset.h` and, in the full header, the matching masks. Common AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15` rely on this generated naming convention to compose and decode MMIO and PCI configuration register values.

Although the repository path sits under `distributed-fs/ceph-client`, this file is Linux AMDGPU hardware-description data, not Ceph client logic. In this snapshot, `amdgpu/uvd_v7_0.c` includes the companion `nbif/nbif_6_1_offset.h`; a direct include of `nbif_6_1_sh_mask.h` was not found in the scanned AMDGPU C sources. The header still belongs to the generated ASIC register set and may be consumed through broader include paths, conditional ASIC code, or out-of-tree/generated build combinations.

## Important Macro Families

The `bif_cfg_dev0_epf0_bifcfgdecp` block defines standard endpoint PCI configuration and PCIe capability fields. It starts with `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, revision/class/header/BIST, BARs, subsystem IDs, ROM base, capability pointer, interrupt line/pin, and PCI power-management fields. It then covers PCIe capability fields for device and link capabilities/control/status, MSI/MSI-X tables and pending bits, virtual channel resources, device serial number, advanced error reporting, BAR enhancement, power budget, dynamic power allocation, secondary PCIe link/equalization, ACS, ATS, PRI, PASID, TPH requester, multicast, LTR, ARI, and SR-IOV. These fields define the software-visible PCIe personality of function 0.

The same endpoint block contains a large GPU IOV vendor-specific capability family: `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_*`. It includes SR-IOV shadow fields, interrupt enable/status bits for VF0-VF13, reset notification bits, hypervisor/VM mailbox dwords, context indicators, total framebuffer size, offsets, per-VF framebuffer size/offset fields for VF0-VF15, and scheduler dwords for UVD, VCE, and GFX. These are privilege-sensitive virtualization fields because they describe VF resources, reset paths, and hypervisor-to-device communication.

The `bif_cfg_dev0_swds_bifcfgdecp` block defines downstream/bridge-style PCI fields: bus numbers, IO and memory windows, secondary status, prefetchable windows, bridge interrupt/control bits, slot capability/control/status fields, and subsystem ID capability fields. These mirror PCI-to-PCI bridge register concepts and are likely used when NBIF exposes or models downstream/root-port behavior.

`rcc_shadow_reg_shadowdec` contains shadowed command, BAR, bus-number, IO/memory-window, prefetchable-window, and bridge-control update fields. These macros describe upstream/shadow copies such as `IOEN_UP`, `MEMEN_UP`, `BAR*_UP`, secondary/subordinate bus updates, and VGA/ISA/reset control updates. `SUC_INDEX` and `SUC_DATA` expose an indexed shadow/update channel.

`bif_bx_pf_SUMDEC` is a small indexed register pair, `SUM_INDEX` and `SUM_DATA`, for system-update or summary-style indirect access. As with other indexed pairs in generated register headers, the sequencing and valid index space are defined by caller logic and hardware documentation, not by this header.

`gdc_GDCDEC` begins with AXI-to-system/fabric control fields. `A2S_CNTL_CL0` through `CL4` map snoop, pass posted-write, response, block-level, data-error, EXOKAY, and response behavior per client/class. `A2S_CNTL_SW0` through `SW2` define tag minimums, response reorder controls, write/read response FIFO behavior, response priority, and WRR read/write weights. The same block also includes `NGDC_MGCG_CTRL`, `A2S_MISC_CNTL`, `NGDC_SDP_PORT_CTRL`, doorbell ranges for SDMA0, SDMA1, IH, and MMSCH0, a doorbell fence enable, 64-bit doorbell support disables, and secondary security-level mapping fields.

`nbif_sion_SIONDEC` is a large repeated SION credit and scheduling block. For classes `CL0` through `CL5`, it defines read-response, write-response, and request burst-target/time-slot registers plus request, data, read-response, and write-response pool-credit allocation registers split across low/high dwords. It also includes `SION_CNTL_REG0`, which has many control bits for virtual/physical channels, mode, idle state, performance optimization, reset control, read/write ordering, timer persistence, and timeout-related behavior.

`syshub_mmreg_direct_syshubdirect` defines system-hub and DMA arbitration/power behavior. It includes SOCCLK and SHUBCLK deep-sleep allow fields per host/DMA client, deep-sleep timers, bus-generator enhancement bypass/immediate enables, DMA clock QoS control registers, per-client/class reset and QoS override controls, system-hub clock-gating timers, per-PF/VF transaction-idle status bits, a scratch register, and high-priority timer fields.

`gdc_ras_gdc_ras_regblk` defines RAS leaf controls for leaves 0 through 5. Each leaf has poison detection, poison error-event, poison stall, parity detection, parity error-event, parity stall, received event/link-disable indicators, poison/parity detected status, error-event-sent status, and egress-stalled status fields. These are diagnostic and reliability controls for fabric error handling.

`gdc_rst_GDCRST_DEC` defines reset controls for system-hub PF and VF function-level resets, GFX driver-mode reset, link reset, hard reset, soft reset, and SDP port reset. The PF0 VF FLR register has individual bits for VF0 through VF15 plus a soft-PF FLR bit.

`bif_bx_pf_SYSDEC` defines firmware scratch registers, BIOS scratch registers, RLC/VCE/UVD interrupt-control status bits, MMIO CAM address/remap fields, and the beginning of endpoint PCIe control fields. The interrupt controls encode command-complete, hang-self-recovered, hang-needs-FLR, and VM-busy-transition indications for RLC, VCE, and UVD. The endpoint PCIe fields include device/link capability/control/status, VC resource control, uncorrectable/correctable error status/mask/severity, AER header logs, LTR, OBFF, DPA, PME, TX/RX controls, requester ID, error-control flags, and link-speed strap bits.

`bif_bx_pf_BIFDEC1` is the main PF BIF control area. It covers MM indirect-access disable, broad bus-control fields, scratch registers, reset enables, MM config register selection and write-to-config enable, link-training reset control, interrupt control and dummy-read setup, clock request pad controls and performance counter, clock readiness/BACO bypass, feature-disables and routing controls, doorbell control/interrupt/fence/global apertures, slave arbitration, framebuffer read/write enable, busy delay, performance counter control/results, master/slave transaction-pending status, BACO entry/exit control and timers, memory type control, VDDGFX power status and compare windows, HDP/XDMA/VGA framebuffer compare controls, HDP flush remap controls, BIF ring-buffer control/base/read-pointer/write-pointer/writeback address fields, mailbox index, GPU IOV reset notification/config size registers, GMI WRR weights, strap-write once enable, and pad controls.

`rcc_pf_0_BIFDEC1`, `rcc_pf_0_BIFDEC2`, and `rcc_strap_BIFDEC1` define root-complex/control and strap fields. They include BACO request-disables, reset enables, VDM support, peer register ranges, RCC bus controls, VGA/config aperture controls, XDMA aperture, feature-control behavior for unsupported requests and MSI pending handling, bus-number and device/function ID lists, host bus-number capture, peer framebuffer offset enables, link-down entry/exit controls, common link controls, MSI-X vector address/data/control fields, and extensive device/port/function strap fields. Strap groups describe link speed/width, ASPM, slot power, AER/ACS/ATS/ARI/SR-IOV/PASID/DPA/DSN/VC/MSI/MSI-X support, class codes, subsystem IDs, BAR aperture sizes, resize-BAR support, doorbell and framebuffer aperture sizes, VGA disable, VF register protection, VF MSI capability, and function enable/power-management flags for EPF0 and the start of EPF1.

The chunk ends at the start of `bif_bx_pf_BIFPFVFDEC1`, with only `BIF_BME_STATUS` and the first two `BIF_ATOMIC_ERR_LOG` shifts visible. The remainder of this PF/VF-specific BIF block is outside this chunk.

## Control Flow and State Behavior

This header has no executable control flow. The compile-time behavior is preprocessor substitution: a caller names a field such as `BIF_DOORBELL_CNTL__DOORBELL_MONITOR_EN__SHIFT`, and helper macros use the numeric shift to place or extract a value in the corresponding hardware register.

Runtime state lives in GPU hardware registers, PCI configuration space, or shadow/strap state, not in this file. The covered fields represent several state classes:

- Durable configuration state, such as PCIe device/link capabilities, BAR and aperture sizes, bus-number routing, bridge memory windows, doorbell ranges, QoS/WRR weights, clock-gating/deep-sleep enables, BACO timers, and strap-derived feature enables.
- Command or handshake state, such as FLR reset bits, link reset, mailbox dwords, reset notifications, ring-buffer pointers, doorbell interrupt clear bits, performance counter reset bits, and indexed `*_INDEX`/`*_DATA` access windows.
- Status and diagnostic state, such as PCIe/AER error status, RAS leaf status, transaction-idle bits, master/slave pending bits, clock readiness, power status, ring-buffer overflow, and BME-low/atomic-error indicators.
- Privilege and isolation state, such as SR-IOV VF count/stride/device ID, per-VF framebuffer size/offset, VF FLR bits, GPU IOV context/reset/mailbox fields, PASID/ATS/PRI/ACS controls, and VF BAR/doorbell aperture straps.

The file does not encode ordering requirements. Driver code must still perform read-modify-write operations, clear write-one-to-clear status bits correctly, poll status/acknowledge bits with appropriate timeouts, and coordinate power/reset transitions with the rest of AMDGPU.

## Dependencies and Integration Points

The direct dependencies are the C preprocessor and the AMD generated register naming convention. Practical consumers also need:

- the companion `nbif_6_1_offset.h` register-address header;
- the later mask section of this same header, or equivalent field-mask definitions;
- AMDGPU field helpers such as `REG_SET_FIELD` and `REG_GET_FIELD`;
- SOC15/MMIO access helpers such as `RREG32_SOC15`, `WREG32_SOC15`, and indirect register accessors;
- PCIe, NBIO/NBIF, SR-IOV, BACO, RAS, interrupt, doorbell, and reset initialization paths.

The scanned tree shows `amdgpu/uvd_v7_0.c` including `nbif/nbif_6_1_offset.h`, which places NBIF 6.1 in the Vega-era UVD/media driver integration surface. Similar generated NBIF/NBIO headers are used by NBIO source files for doorbell range setup, interrupt handling, RAS interrupt clears, BACO/power sequencing, and link/PCIe configuration. Even when this exact shift header is not directly included in the visible sources, its field names follow the same integration model.

## Risks

Field-position drift is high impact. A wrong shift can cause the driver to program the wrong PCIe control bit, expose the wrong BAR aperture, clear the wrong interrupt/status bit, reset the wrong PF/VF, or corrupt virtualization-resource assignment.

This chunk is highly repetitive. Families such as `PCIE_LANE_0..15_EQUALIZATION_CNTL`, `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_VF0..15_FB`, `SION_CL0..5_*`, `GDC_RAS_LEAF0..5_CTRL`, DMA clock/client/class controls, and `RCC_DEV0_EPF*` strap groups are vulnerable to generated-index or copy/paste errors. Review and regeneration checks should pay attention to skipped indices and field names that differ by only a suffix.

The chunk boundary is important. The covered range contains shift definitions but not the normal matching mask definitions, and it ends just after `BIF_ATOMIC_ERR_LOG__UR_ATOMIC_REQEN_LOW__SHIFT`. Any final per-file report must merge subsequent chunks before making whole-header claims about mask coverage or the full PF/VF BIF block.

Several fields cross security and isolation boundaries: SR-IOV enable/count/stride, per-VF framebuffer windows, VF FLR controls, GPU IOV mailboxes and reset notifications, ACS/ATS/PRI/PASID support, VF register-protection straps, doorbell global apertures, and peer framebuffer offsets. Incorrect use can break VF isolation or route DMA/MMIO transactions incorrectly.

Power and reset fields can create hard-to-debug failures. BACO, clock gating, deep sleep, link reset, hard/soft reset, SDP reset, and FLR bits can strand hardware if toggled in the wrong order or while transactions are pending. The nearby pending/idle/status fields are signals callers should use, but this header cannot enforce that sequencing.

PCIe/AER status and mask fields require care because status bits may be latched and clears may be write-one-to-clear in hardware. Treating all fields as ordinary read/write configuration can lose diagnostic information or leave interrupts asserted.

## Test and Validation Signals

Useful validation is integration-level:

- Build AMDGPU configurations that include NBIF/NBIO 6.1 register headers to catch missing, renamed, or malformed generated macros.
- Hardware boot tests on matching ASICs should validate PCI config space, BAR enumeration, subsystem/class IDs, MSI/MSI-X setup, PCIe link capability/status, and bridge/downstream-window behavior.
- Doorbell tests should verify SDMA, IH, MMSCH, and global doorbell aperture programming, 32-bit versus 64-bit doorbell behavior, interrupt status/clear fields, and doorbell monitor/fence behavior.
- SR-IOV/GPU IOV tests should cover VF count/stride/device ID, VF framebuffer size/offset assignment, VF FLR/reset notifications, hypervisor mailbox dwords, VF BAR/doorbell aperture straps, ACS/ATS/PRI/PASID controls, and VF register protection.
- RAS/error tests should inject or surface PCIe AER, GDC poison/parity, and NBIF doorbell/RAS interrupt events, then confirm status, mask, severity, header-log, and clear fields line up with hardware.
- Power-management tests should exercise BACO entry/exit, clock request pads, deep-sleep allow/timers, clock-gating controls, VDDGFX compare/stall windows, and transaction-idle/pending checks across suspend/resume and runtime power transitions.
- Reset and recovery tests should cover PF/VF FLR, link reset, hard/soft reset, GFX driver-mode reset, SDP reset, RLC/VCE/UVD hang-needs-FLR interrupt indications, and BME-low/atomic-error reporting.
- Performance and diagnostic smoke tests should program BIF performance counter selectors, read counter results, and inspect SION/SYSHUB/QoS/pending status under DMA, UVD/VCE, and graphics workloads.

## Cross-Chunk Notes

This report covers only lines 1-2921. Later chunks of `nbif_6_1_sh_mask.h` must be consulted for the rest of `bif_bx_pf_BIFPFVFDEC1`, subsequent NBIF blocks, and the matching `*_MASK` macros for the shifts described here. The final per-file research document should reconcile this chunk's shift-only view with the later mask section and companion offset/default headers.
