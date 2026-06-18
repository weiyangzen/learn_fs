# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_1_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002868`: lines 1-2921, `Docs/researches/chunks/subset-b-002868_research.md`
- `subset-b-002869`: lines 2922-5619, `Docs/researches/chunks/subset-b-002869_research.md`
- `subset-b-002870`: lines 5620-8351, `Docs/researches/chunks/subset-b-002870_research.md`
- `subset-b-002871`: lines 8352-10281, `Docs/researches/chunks/subset-b-002871_research.md`

## Chunk Research

### subset-b-002868: lines 1-2921

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

### subset-b-002869: lines 2922-5619

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_1_sh_mask.h lines 2922-5619

## Scope

This chunk is part of AMDGPU's generated NBIF 6.1 register bitfield header. It contains C preprocessor constants only: `__SHIFT` definitions in the first part of the chunk and, beginning later in the chunk, matching `_MASK` definitions for many of the same PCIe/NBIF register fields. There are no functions, structs, enums, allocations, locks, or executable control flow here. Runtime behavior is supplied by AMDGPU code that includes `nbio/nbio_6_1_sh_mask.h` together with the companion address/default headers and then uses helpers such as `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `WREG32_FIELD15`.

The line range starts at the tail of `BIF_ATOMIC_ERR_LOG` shift definitions and ends inside the mask definitions for PCIe resizable/enhanced BAR capability registers. Neighboring chunks are needed for the complete file-level view.

## Purpose

The chunk documents the bit layout for NBIF 6.1 host-interface and PCIe configuration registers used by the AMD GPU driver. Its main purpose is to let driver code compose and decode 32-bit hardware register values without hard-coded bit numbers. The covered registers span doorbell apertures, HDP coherency flush handshakes, mailbox signaling, PF/VF and SR-IOV identification, strap-driven PCIe capability exposure, reset and power-state interrupts, BME error logging, DMA attribute overrides, LTR/PME/sticky restore, MSI-X table entries, syshub indirect controls, clock/deep-sleep/QoS settings, and PCIe extended capability masks.

Although the repository path is under a Ceph client source tree, this file is Linux AMDGPU hardware-description data for GPU PCIe/NBIF programming.

## Important Macro Families

`DOORBELL_SELFRING_GPA_APER_BASE_HIGH`, `DOORBELL_SELFRING_GPA_APER_BASE_LOW`, and `DOORBELL_SELFRING_GPA_APER_CNTL` define the self-ring doorbell aperture base and control fields. The control register exposes the aperture enable bit and size field in this chunk. In the NBIO 6.1 implementation, `nbio_v6_1_enable_doorbell_selfring_aperture()` writes the low/high base from `adev->doorbell.base` and sets the control fields through `REG_SET_FIELD`.

`HDP_REG_COHERENCY_FLUSH_CNTL`, `HDP_MEM_COHERENCY_FLUSH_CNTL`, `GPU_HDP_FLUSH_REQ`, and `GPU_HDP_FLUSH_DONE` describe the HDP coherency flush protocol. Request and done bits are provided for command processor engines `CP0`-`CP9` and `SDMA0`/`SDMA1`. `nbio_v6_1_get_hdp_flush_req_offset()`, `nbio_v6_1_get_hdp_flush_done_offset()`, and `nbio_v6_1_hdp_flush_reg` integrate these fields with the common AMDGPU HDP flush path.

`BIF_TRANS_PENDING` exposes master and slave transaction-pending bits. Driver reset, suspend, or error recovery paths can use this kind of status to avoid resetting NBIF while outstanding host transactions remain.

`MAILBOX_MSGBUF_TRN_DW*`, `MAILBOX_MSGBUF_RCV_DW*`, `MAILBOX_CONTROL`, `MAILBOX_INT_CNTL`, and `BIF_VMHV_MAILBOX` define simple host/firmware or VM/hypervisor mailbox data, valid, acknowledge, and interrupt-enable fields. The `BIF_VMHV_MAILBOX` register packs transmit/receive data nibbles, valid bits, ack bits, and interrupt enables into one register.

`RCC_DOORBELL_APER_EN`, `RCC_CONFIG_MEMSIZE`, `RCC_CONFIG_RESERVED`, and `RCC_IOV_FUNC_IDENTIFIER` cover PF/VF-facing RCC fields. They provide the global doorbell aperture enable, configured memory size, reserved config data, function identifier, and IOV enable state. `nbio_v6_1_get_memsize()` reads the corresponding memsize register, and `nbio_v6_1_enable_doorbell_aperture()` writes the aperture enable field.

`SYSHUB_INDEX` and `SYSHUB_DATA` define the indirect syshub MMREG access pair. Later `SYSHUBMMREGIND_*` families in this chunk define fields reached through that indirect aperture.

The `RCCSTRAPRCCSTRAP_RCC_DEV*_PORT_STRAP*` families define root/downstream port strap fields for device 0 and device 1. They encode PCIe capability exposure such as ARI, ACS, AER, ECRC generation/check, extended tags, VC count, Gen2/Gen3 enablement, target link speed, L0s/L1 latencies, LTR, OBFF, MSI, atomic operations, power-management support, power budget data, port number, bus/device/function identity, and ACS forwarding/redirect policy. These are strap-level hardware defaults rather than normal dynamic driver state.

The `RCC*_EPF*_STRAP*` families define endpoint physical-function strap fields for functions 0-7. They repeat per-function identity and capability fields: device ID, major/minor/ATI revision ID, function enable, legacy device type, D1/D2 support, 64-bit BAR and resizable BAR support, MSI/MSI-X support, ARI/AER/ACS/ATS, DPA, DSN, VC, page request, PASID, FLR, PME, interrupt pin, auxiliary power, subsystem IDs, aperture enable/prefetchability/size, ROM aperture, class code, and function-specific selectors such as SATA/USB fields. `nbio_v6_1_get_rev_id()` reads the PF0 strap revision ID via these shift/mask constants.

`DEV0_PF*_FLR_RST_CTRL`, `BIF_PF_FLR_INTR_*`, `BIF_PF0_VF_FLR_INTR_*`, `BIF_PF_FLR_RST`, and `BIF_PF0_VF_FLR_RST` describe function-level reset handling for PF0-PF7 and VF0-VF15 under PF0. The fields include PF config/private reset enable, sticky retention controls, FLR grace mode and timeout, dummy response status selections, interrupt status, masks, and reset request bits.

`BIF_DEV0_PF*_DSTATE_VALUE`, `DEV0_PF*_D3HOTD0_RST_CTRL`, `BIF_D3HOTD0_INTR_*`, `BIF_POWER_INTR_*`, `BIF_PF_DSTATE_INTR_*`, and `BIF_PORT0_DSTATE_VALUE` define PCI power-state target/acknowledge tracking, D3hot-to-D0 reset controls, PME turn-off and D-state interrupt status/masks, and port D-state state machine fields.

`MISC_SCRATCH`, `INTR_LINE_POLARITY`, `INTR_LINE_ENABLE`, `OUTSTANDING_VC_ALLOC`, `BIFC_MISC_CTRL0`, and `BIFC_MISC_CTRL1` cover miscellaneous NBIF behavior: scratch storage, legacy interrupt line polarity/enable, DMA/host outstanding virtual-channel allocation, chain locking, atomic length checking, PCIe capability protection, port D-state bypass, PME turn-off mode, poison/ACS violation reporting, unsupported command status, ordering overrides, and BME drop behavior.

`BIFC_BME_ERR_LOG` and `BIFC_RCCBIH_BME_ERR_LOG` provide per-function bus-master-enable violation status and matching clear bits. These can signal DMA or RCC/BIH activity while PCI command BME is low for functions 0-7.

`BIFC_DMA_ATTR_OVERRIDE_DEV0_F*_F*` groups provide per-function DMA transaction attribute overrides for ID-based ordering, relaxed ordering, and snoop/no-snoop request attributes across posted and non-posted traffic. These fields can materially change ordering and cache-coherency behavior for PCIe transactions.

`RCCPFCAMDGFXAZ_RCC_PFC_*` covers port-function-controller behavior: LTR snoop/non-snoop latency values and scales, PME enable/status restore, sticky restore for selected AER error status and TLP header/prefix log fields, and auxiliary-power override/detection fields.

`PCIEMSIX_VECT0` through `PCIEMSIX_VECT31` define MSI-X table entry fields for 32 vectors: message address low/high, message data, and per-vector mask bit. `PCIEMSIX_PBA` defines pending bits for the MSI-X pending-bit array.

`SYSHUBMMREGIND_*` covers syshub indirect registers for SOCCLK and SHUBCLK deep-sleep allowance, deep-sleep timers, BGEN enhancement bypass/immediate enable, DMA QoS control, client controls, read/write WRR weights, clock gating, transaction idle status for PF and VF0-VF15, scratch, and high-priority timer fields.

The final section in this chunk switches to `_MASK` definitions for PCIe capability registers. It includes vendor-specific extended capability list/header/scratch fields, virtual channel capability/control/status/resource fields, device serial number fields, Advanced Error Reporting status/mask/severity/control/header log/root error/source ID/TLP prefix log fields, and enhanced BAR capability/control masks for BAR1-BAR3 before the chunk ends.

## Control Flow and State

This header has no direct control flow. The implicit hardware workflows encoded by the fields are:

1. Initialization code reads strap registers to identify revision, enabled functions, endpoint/port capabilities, BAR shape, interrupt support, and virtualization features.
2. Doorbell setup code enables the global doorbell aperture, optionally programs the self-ring GPA aperture base low/high, and writes the aperture control register.
3. HDP flush users write request bits for CP or SDMA engines and poll or compare the matching done bits using the masks exported through `nbio_v6_1_hdp_flush_reg`.
4. Power-management and reset paths inspect D-state, PME, FLR, link-reset, and transaction-pending status, mask/unmask the corresponding interrupts, and write reset control bits when needed.
5. Virtualization/SR-IOV code can rely on PF/VF function ID, VF FLR, VF transaction-idle, MSI-X, ATS/PASID/page-request, aperture, and IOV enable fields to manage per-function isolation and reset.
6. Error-handling and diagnostics code can read AER, BME error logs, sticky restore fields, TLP header/prefix logs, and PCIe root error status/source fields.

Register state persists in hardware until reset, power transition, firmware action, or a later driver write changes it. Strap fields are generally sampled hardware defaults and should be treated as platform/ASIC configuration. Interrupt status, reset request, mailbox valid/ack, error-log clear, performance/QoS override, and HDP flush request/done bits are stateful protocol fields whose ordering and clear semantics must be handled by callers.

## Dependencies and Integration Points

This chunk depends only on the C preprocessor and the hardware register naming convention. It is normally paired with `nbio_6_1_offset.h`, `nbio_6_1_default.h`, and `nbio_6_1_smn.h` for register addresses/defaults and SMN addresses.

The primary in-tree integration is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, which includes `nbio/nbio_6_1_sh_mask.h`. That implementation uses these macros for revision-ID extraction, memsize/doorbell aperture handling, self-ring aperture programming, HDP flush register offsets/masks, interrupt/clock/power setup, ASPM/LTR programming, and NBIO function registration through `nbio_v6_1_funcs`.

The macro names also match patterns used by neighboring NBIO/NBIF versions (`nbio_v2_3.c`, `nbio_v7_0.c`, `nbio_v7_2.c`, `nbio_v7_11.c`, `nbif_v6_3_1.c`). That makes this header part of a generated register ABI: the driver code expects stable `REG__FIELD__SHIFT` and `REG__FIELD_MASK` names across ASIC revisions where the same hardware concept exists.

Broader integration points include AMDGPU PCIe/NBIO setup, KFD MMIO remapping for HDP flush controls, GPU scheduler/ring code that needs HDP flushes, interrupt handling through MSI/MSI-X and IH doorbells, SR-IOV/virtualization reset flows, PCIe AER diagnostics, and power-management paths for ASPM/LTR/PME/deep-sleep controls.

## Risks

Bitfield errors are high impact because callers use these constants to write hardware registers directly. A wrong shift or mask can enable the wrong doorbell aperture, miss an HDP flush completion, expose or hide PCIe capabilities incorrectly, corrupt PF/VF reset handling, or misprogram PCIe ordering/coherency attributes.

The strap and function families are extremely repetitive. Generation or copy mistakes around function suffixes (`F0`-`F7`), virtual functions (`VF0`-`VF15`), and port/device prefixes can compile cleanly while targeting the wrong function or capability bit.

Fields controlling ACS, ATS, PASID, page requests, MSI/MSI-X, VF aperture sizing, IOV enablement, and FLR affect isolation and virtualization correctness. Incorrect use can break SR-IOV guests, leak access across functions, or leave stale DMA state after reset.

The DMA attribute override and BME drop/error-log fields affect PCIe transaction ordering, snooping, and legal DMA behavior. Bad values may surface only under load as data corruption, timeouts, or platform-specific hangs.

HDP flush request/done bits are used to enforce host-data-path coherency. If the CP/SDMA bit mapping is wrong or callers poll the wrong mask, command streams can observe stale memory.

MSI-X table and PBA fields are architecturally sensitive. Incorrect address/data/mask handling can lose interrupts, deliver them to the wrong vector, or leave vectors masked.

This chunk boundary starts after the beginning of `BIF_ATOMIC_ERR_LOG` and ends before the complete enhanced BAR mask family. Final reconciliation must include adjacent chunks before drawing conclusions about complete register groups.

## Test and Validation Signals

Useful validation is mostly build and integration based:

- Compile AMDGPU with NBIO 6.1 support; missing or renamed macros should fail where `nbio_v6_1.c` and shared register helpers use them.
- Boot on NBIO 6.1 hardware and verify `nbio_v6_1_get_rev_id()` reports the expected revision from `RCC_DEV0_EPF0_STRAP0`.
- Exercise doorbell initialization and ring submission; failures often appear as queues that do not ring, IH/SDMA doorbells not firing, or GPU hangs after self-ring aperture changes.
- Run command processor and SDMA workloads that force HDP flushes and confirm the request/done bits for CP0-CP9 and SDMA0-SDMA1 complete reliably.
- Test suspend/resume, D3hot-to-D0, FLR, and GPU reset paths while checking PF/VF reset interrupts, D-state target/ack fields, transaction-pending bits, and PME status.
- Validate SR-IOV guests for VF FLR, VF transaction-idle reporting, MSI-X delivery, aperture sizing, ATS/PASID/page-request capabilities, and isolation after guest reset.
- Check PCIe AER and BME diagnostics under injected or naturally occurring errors; the expected status, mask, severity, header log, source ID, and clear bits should behave according to PCIe semantics.
- Use register readback/debugfs traces to verify LTR, PME restore, syshub deep-sleep, clock-gating, QoS, and DMA attribute override writes land in the expected bit positions.

## Cross-Chunk Notes

This report covers only lines 2922-5619. Earlier chunks contain the first part of the NBIF 6.1 shift definitions, including the start of `BIF_ATOMIC_ERR_LOG` and many PCIe configuration fields. Later chunks should contain the remainder of the PCIe BAR/enhanced capability masks and subsequent NBIF mask definitions. The final per-file research document should merge those adjacent chunks before claiming complete coverage of any register family that crosses this boundary.

### subset-b-002870: lines 5620-8351

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

### subset-b-002871: lines 8352-10281

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_1_sh_mask.h lines 8352-10281

## Scope

This chunk is the tail of AMDGPU's generated NBIF 6.1 register bitfield header. It contains C preprocessor `*_MASK` constants only; there are no functions, structs, enums, allocations, locks, or executable branches. The macros describe hardware register fields that driver code combines with companion register-address and shift definitions, normally through AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, `WREG32`, and indirect MMIO accessors.

The range starts in the middle of the `RCCSTRAPRCCSTRAP_RCC_DEV0_EPF0_STRAP2` mask family and ends at the file's `#endif`, so adjacent chunks are needed for the matching shift definitions and the first masks in the same strap register.

## Purpose

The chunk maps NBIF register fields for PCIe endpoint strap configuration, BIF reset and interrupt control, BIF miscellaneous behavior, RAS reporting, PCI function-control restore state, MSI-X table entries, and System Hub indirect QoS/power-management controls. These masks let AMDGPU code program or decode 32-bit hardware registers without embedding raw bit constants in C logic.

Although the repository path is under `distributed-fs/ceph-client`, this source is Linux AMD GPU driver hardware-description data under `drivers/gpu/drm/amd/include/asic_reg/nbif`; it is not Ceph client protocol or filesystem logic.

## Important Macro Families

`RCCSTRAPRCCSTRAP_RCC_DEV0_EPF0_STRAP2` through `RCC_DEV1_EPF2_STRAP13` define PCI endpoint-function strap masks. They cover device/subsystem/vendor IDs, revision and class-code fields, function enable, legacy-device type, D1/D2 support, MSI/MSI-X, AER/ACS/ATS/PASID, atomics, FLR, PME, interrupt pin, BAR and aperture sizing, ROM and VGA disables, doorbell aperture sizing, SR-IOV VF mapping, VF aperture sizes, resize BAR support, and per-function capability toggles. The families repeat across device 0 functions 0-7 and device 1 functions 0-2, with function-specific omissions such as extra VF/doorbell fields on graphics-facing functions.

`HARD_RST_CTRL`, `RSMU_SOFT_RST_CTRL`, and `SELF_SOFT_RST` define reset enables or asserted reset bits for dispatch/config/private endpoint paths, sticky reset handling, SWUS shadow reset, strap reload, SDP port reset, and core reset. `GFX_DRV_MODE1_RST_CTRL` adds PF/VF driver-mode reset controls.

`DEV0_PF*_FLR_RST_CTRL` and `DEV0_PF*_D3HOTD0_RST_CTRL` describe which PF, VF, soft-PF, config, private, sticky, FLR-exception, and dummy-response behaviors participate in function-level reset or D3hot-to-D0 reset. PF0 has the broadest VF/soft-PF coverage; PF1-PF7 mostly carry PF reset enables plus FLR grace and dummy response status fields.

`BIF_INST_RESET_INTR_STS/MASK`, `BIF_PF_FLR_INTR_STS/MASK`, `BIF_D3HOTD0_INTR_STS/MASK`, `BIF_POWER_INTR_STS/MASK`, `BIF_PF_DSTATE_INTR_STS/MASK`, and `BIF_PF0_VF_FLR_INTR_STS/MASK` define interrupt status and mask bits for link reset, driver reset modes, PF FLR, D3hot-D0 transitions, PME turnoff, port D-state changes, PF D-state changes, and PF0 VF FLR events. Matching `BIF_PF_FLR_RST` and `BIF_PF0_VF_FLR_RST` masks trigger or represent PF/VF reset state.

`BIF_DEV0_PF*_DSTATE_VALUE` and `BIF_PORT0_DSTATE_VALUE` expose target and acknowledge D-state fields, with a per-PF `NEED_D3TOD0_RESET` bit. Callers use these when coordinating PCI power-state transitions with reset policy.

`BIF_RST_MISC_CTRL*` and `BIF_RST_GFXVF_FLR_IDLE` capture reset policy knobs and idle observability: error-status retention across PERST, driver reset mode, auto-clear behavior, link-reset grace timers, SR-IOV VF-save behavior, DMA dummy response behavior, reset transaction idle bits, strap reload delays, PME turnoff timeout/mode, and per-VF/soft-PF transaction-idle reporting.

`MISC_SCRATCH`, `INTR_LINE_POLARITY`, `INTR_LINE_ENABLE`, and `OUTSTANDING_VC_ALLOC` provide scratch, interrupt-line routing, and outstanding-request allocation fields for DMA and host virtual channels.

`BIFC_MISC_CTRL0/1`, `BIFC_THT_CNTL`, `BIFC_HSTARB_CNTL`, `BIFC_GSI_CNTL`, `BIFC_PCIEFUNC_CNTL`, and `BIFC_SDP_CNTL_0` cover BIF client behavior: virtual-wire unit-ID checks, chain locking, DMA atomic checks, PCIe capability protection, VC7 DMA config disable, port D-state/PME modes, poison and ACS violation reporting, unsupported command status handling, ordering overrides, BME drop controls, credit allocation thresholds, host/GSI arbitration policy, completion interleaving, unsupported-request generation, non-PCIe bus/device/function mapping, and SDP disconnect hysteresis.

`BIFC_BME_ERR_LOG` and `BIFC_RCCBIH_BME_ERR_LOG` expose per-function "DMA or RCCBIH while BME low" status bits and corresponding clear bits. `BME_DUMMY_CNTL_0` controls dummy response status per function.

`BIFC_DMA_ATTR_OVERRIDE_DEV0_F0_F1` through `DEV0_F6_F7` define posted/non-posted override fields for ID-based ordering, relaxed ordering, and no-snoop attributes per PCI function. These masks are paired by two functions per register.

`NBIF_VWIRE_CTRL`, `NBIF_SMN_VWR_*`, and `NBIF_SDP_VWR_*` define virtual-wire reset delays, posted/block-level behavior, voltage-change disable sets, reset default or override values, and trigger bits for SMN and SDP virtual-wire paths.

`SMN_MST_CNTL0` and `SMN_MST_EP_CNTL1..4` configure SMN master behavior such as posted-mask enable, multi-transaction-ID disable, and zero byte-enable read/write handling for downstream and endpoint PF0-PF7 paths. `NBIF_REGIF_ERRSET_CTRL` controls whether non-PF MMREG requests set errors.

`BIFC_PERF_CNTL_0/1` and `BIFC_PERF_CNT_MMIO_RD/WR`, `BIFC_PERF_CNT_DMA_RD/WR` define enable, reset, select, and 32-bit value fields for MMIO and DMA read/write performance counters.

`BIF_RAS_LEAF0_CTRL` through `BIF_RAS_LEAF2_CTRL`, `BIF_RAS_MISC_CTRL`, `BIF_IOHUB_RAS_IH_CNTL`, and `BIF_RAS_VWR_FROM_IOHUB` describe RAS poison/parity detection, error-event generation, stall behavior, received/sent status, link-disable event reporting, IOHub RAS interrupt enable, and virtual-wire trigger status.

`RCC_PFC_*` and duplicated `RCCPFCAMDGFXAZ_RCC_PFC_*` masks cover PCI function-control latency tolerance reporting, PME restore state, sticky AER-style error restore fields, saved TLP header/prefix words, and auxiliary power override state for two related PFC decode blocks.

`PCIEMSIX_VECT0` through `PCIEMSIX_VECT31` define MSI-X table entry fields: low and high message address, message data, and vector mask bit. `PCIEMSIX_PBA` exposes the MSI-X pending-bit array.

`SYSHUBMMREGIND_*` masks define System Hub indirect controls for SOCCLK and SHUBCLK deep-sleep eligibility, deep-sleep timers, BGEN bypass/immediate enable, DMA switch QoS mode/min/max values, per-client reset-on-FLR/link-reset behavior, static QoS override, read/write weighted round-robin weights, clock gating, transaction-idle status for PF and VF0-VF15, a high-priority timer, and scratch storage.

## Control Flow and State

This header has no direct control flow. Its implicit runtime flow is imposed by the hardware protocols that callers implement:

1. Strap fields describe reset-sampled or firmware-provided PCI function capabilities that determine how Linux enumerates functions, BARs, MSI/MSI-X, SR-IOV, ATS/ACS/AER/PASID, atomics, and power-management capabilities.
2. Reset code selects hard, RSMU soft, self soft, FLR, link-reset, or D3hot-D0 reset masks, then observes idle, interrupt, D-state, or acknowledge-style fields before continuing.
3. Interrupt-handling code reads status masks, filters through matching mask registers, and clears or services PF, VF, power, D-state, and link/reset events.
4. BIF misc and virtual-wire setup code programs arbitration, attribute override, SMN/SDP virtual-wire, BME-dummy, and performance counter fields as ASIC initialization or debug policy requires.
5. RAS paths enable poison/parity detection and report/inspect error and stall status.
6. MSI-X setup treats each vector as a four-register table entry and uses the PBA masks to inspect pending vector bits.
7. System Hub power and QoS paths configure deep-sleep, clock gating, reset-on-FLR/link-reset, client QoS, and WRR weights, then may read transaction-idle fields during reset or power transitions.

State represented by these masks lives in GPU hardware registers, strap latches, MSI-X table storage, status latches, counters, or scratch registers. Some fields are durable configuration until reset or later writes; others are event/status/clear bits, reset triggers, performance counter reset bits, or transient idle indicators. This file does not enforce ordering, polling, locking, or persistence semantics; callers must sequence MMIO writes and reads according to NBIF hardware requirements.

## Dependencies and Integration Points

The macros depend only on the C preprocessor, but they are useful only with the generated NBIF 6.1 register address and shift headers. In AMDGPU they integrate with:

- ASIC initialization code that programs NBIF, PCIe, reset, power, and virtualization registers.
- PCI/SR-IOV setup paths that interpret endpoint-function capabilities, BAR/aperture sizing, VF mapping, ATS/ACS/AER/PASID, and MSI/MSI-X support.
- GPU reset and recovery paths that handle FLR, link reset, hard/soft reset, D3hot-D0 transitions, and transaction-idle polling.
- Interrupt paths for PF/VF FLR, link reset, power, PME, and D-state events.
- RAS code that enables or reads poison/parity error reporting from BIF leaves and IOHub interrupt wiring.
- Debug/perf code that selects and reads BIFC MMIO/DMA counters or scratch registers.
- Power-management code that programs NBIF clock gating, SOCCLK/SHUBCLK deep sleep, and System Hub transaction-idle checks.

## Risks

Bitfield accuracy is critical. A wrong mask can silently write the wrong hardware bit, causing PCI enumeration failures, incorrect BAR sizing, broken MSI/MSI-X delivery, bad SR-IOV VF isolation, ATS/ACS/AER/PASID capability mismatches, reset hangs, missed interrupts, RAS under-reporting, or performance/power regressions.

The chunk is highly repetitive across functions, VFs, vectors, and client lanes. Copy-generation mistakes are plausible around suffixes such as `DEV0_F*`, `DEV1_EPF*`, `PF0_VF*`, `PCIEMSIX_VECT*`, and `DMA_CLK*_SW*_CL*`. The line-range boundary also starts mid-register-family, so reconciliation with the previous chunk should confirm no `STRAP2` masks are dropped.

Several fields are security or isolation sensitive: SR-IOV VF mapping, VF aperture sizes, ATS/ACS/PASID enables, function enable bits, PCIe capability protection disable, non-PF MMREG request error handling, and SMN/SDP virtual-wire controls. Misprogramming them can expose memory or configuration state across PF/VF boundaries.

Reset and power fields are stateful and timing-sensitive. Incorrect grace timers, auto-clear settings, strap reload delays, dummy responses, transaction-idle checks, or D3hot-D0 reset participation may produce intermittent hangs that appear only under FLR, suspend/resume, hot reset, or virtualization teardown.

Performance and QoS masks can degrade behavior without obvious functional failure. Bad WRR weights, static QoS overrides, outstanding VC allocation, arbitration modes, or deep-sleep timers can surface as latency spikes, throughput loss, or power-state instability.

## Test Signals

Useful validation signals are build-time and hardware-facing rather than unit-level:

- The AMDGPU driver should compile with this generated header and companion offset/shift headers without duplicate or missing macro errors.
- PCI enumeration should expose expected device IDs, class codes, BARs, MSI/MSI-X, SR-IOV, ATS/ACS/AER/PASID, FLR, and PME capabilities for NBIF 6.1 ASICs.
- GPU reset tests should cover FLR, VF FLR, link reset, driver reset modes, D3hot-D0 transitions, suspend/resume, and transaction-idle polling without timeouts.
- Interrupt tests or logs should show expected PF/VF FLR, power, D-state, and link-reset interrupt status/mask behavior.
- RAS injection or error-reporting tests should confirm poison/parity enable and status fields are decoded correctly.
- MSI-X tests should confirm all 32 vector table entries and pending bits behave as expected.
- Power/performance telemetry should be checked after QoS, clock-gating, SOCCLK/SHUBCLK deep-sleep, and BIFC counter programming changes.
