# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 137667-140115

## Scope

This chunk is a generated AMD NBIO 7.7.0 register shift/mask slice. It starts in the tail of the `BIF_CFG_DEV2_RC1` PCIe 16 GT/s lane equalization definitions, covers the full PCIe margining extended capability for `DEV2_RC1`, then enters address block `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` and maps a large part of `BIF_CFG_DEV0_EPF0_1` PCI/PCIe configuration space.

The `DEV0_EPF0_1` portion includes standard PCI config header fields, PM capability, PCIe capability, MSI/MSI-X, vendor-specific capability, virtual channel resources, device serial number, Advanced Error Reporting, BAR enhanced capability, power budget, Dynamic Power Allocation, secondary PCIe equalization, ACS, ATS, PRI/page request, PASID, multicast, LTR, ARI, SR-IOV, Data Link Feature, 16 GT/s PHY, PCIe margining, VF resizable BARs, and the beginning of an AMD GPUIOV vendor-specific capability. The chunk ends inside `BIF_CFG_DEV0_EPF0_1_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_VF12_FB`, after the `VF12_FB_SIZE__SHIFT` field and before the remaining VF12 framebuffer field definitions.

This file range defines preprocessor constants only. It has no C functions, structs, variables, allocations, runtime branches, or direct register I/O.

## Purpose

The purpose of this header section is to provide the bitfield contract between AMDGPU NBIO 7.7.0 driver code and the hardware PCIe configuration-space image exposed by NBIO. Every field is represented with the generated pair:

- `REGISTER__FIELD__SHIFT`, the bit offset used when extracting or composing the field.
- `REGISTER__FIELD_MASK`, the raw register mask used with the field value.

Driver code combines these constants with register addresses from `nbio_7_7_0_offset.h` and AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`. The mask header by itself does not know whether a register is readable, writeable, sticky, write-one-to-clear, or command-like; it only encodes the generated bit layout.

## Important Macro Families

### DEV2_RC1 16 GT/s Equalization and Margining

The first lines complete `BIF_CFG_DEV2_RC1_LANE_6_EQUALIZATION_CNTL_16GT`, then define 16 GT/s equalization control for lanes 7 through 15. Each lane uses the same two nibble fields: downstream-port 16 GT transmit preset at bits 3:0 and upstream-port 16 GT transmit preset at bits 7:4. These values are part of PCIe Gen4/16 GT link equalization handling.

`BIF_CFG_DEV2_RC1_PCIE_MARGINING_ENH_CAP_LIST` defines the PCIe margining enhanced-capability header fields `CAP_ID`, `CAP_VER`, and `NEXT_PTR`. `MARGINING_PORT_CAP` and `MARGINING_PORT_STATUS` expose whether software participates in margining and whether hardware/software margining is ready. Lanes 0 through 15 then have matching `MARGINING_LANE_CNTL` and `MARGINING_LANE_STATUS` registers. The per-lane layout is regular:

- `RECEIVER_NUMBER` or `RECEIVER_NUMBER_STATUS` at bits 2:0.
- `MARGIN_TYPE` or `MARGIN_TYPE_STATUS` at bits 5:3.
- `USAGE_MODEL` or `USAGE_MODEL_STATUS` at bit 6.
- `MARGIN_PAYLOAD` or `MARGIN_PAYLOAD_STATUS` at bits 15:8.

These fields support per-lane PCIe electrical margin commands and returned status/payload values. They are diagnostic and link-health integration points rather than ordinary graphics runtime controls.

### DEV0_EPF0_1 Standard PCI and PM Configuration

The `addressBlock: nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` marker starts a new endpoint-function configuration-space block. The early macros describe standard PCI header fields:

- Identity and class fields: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS`.
- Command/status bits: I/O space, memory space, bus master, special cycle, memory write/invalidate, VGA palette snoop, parity response, stepping, SERR, fast back-to-back, interrupt disable, capability-list presence, DEVSEL timing, parity, abort, and system-error status.
- Header/BIST and resource fields: cache line, latency, header type/device type, BIST completion/start/capability, BAR1 through BAR6, CardBus CIS pointer, adapter/subsystem ID, ROM BAR, capability pointer, interrupt line/pin, min grant, and max latency.
- Vendor and PM capability headers plus PM capability/control fields for D-state support, PME support, current power state, PME enable/status, data select/scale, bus power enable, and PM data.

These macros describe persistent PCI configuration state visible to platform firmware, the Linux PCI core, and AMDGPU initialization paths. Incorrect values here can affect enumeration, BAR assignment, interrupt routing, and power-management behavior.

### DEV0_EPF0_1 PCIe Capability, Link, and Interrupts

The PCIe capability block maps endpoint capability and control/status registers. `PCIE_CAP_LIST` and `PCIE_CAP` identify the capability and device type. `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` cover max payload support/size, error reporting enables/status, relaxed ordering, no-snoop, extended tags, FLR capability/initiation, auxiliary power, transactions pending, and emergency power-reduction reporting.

`LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` describe supported and current link speed/width, ASPM and PM controls, link disable/retrain, common clock, extended sync, clock power management, hardware autonomous width disable, link bandwidth interrupts, DRS signaling, slot clock, data-link active, and bandwidth status bits. `DEVICE_CAP2`, `DEVICE_CNTL2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` add completion-timeout controls, ARI, AtomicOp, IDO, LTR, OBFF, 10-bit tags, TLP prefixes, target speed, compliance controls, equalization status, SKP ordered-set support, RTM presence, crosslink status, and DRS message status.

The interrupt capability region includes MSI and MSI-X fields. MSI message control covers enable, multi-message capability/enable, 64-bit address support, per-vector mask support, and extended message-data support/enable. MSI address/data/mask/pending registers cover both 32-bit and 64-bit forms. MSI-X fields expose table size, function mask, enable bit, table BIR/offset, and PBA BIR/offset. These masks are used by low-level PCI/interrupt setup and validation, even if the Linux PCI core owns much of the generic MSI/MSI-X policy.

### Error Reporting, VC, BAR, Power, and Link Training

The AER block includes `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, uncorrectable error status/mask/severity, correctable error status/mask, advanced error capability/control, four TLP header-log doublewords, and four TLP prefix-log doublewords. Covered uncorrectable conditions include DLP, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress blocked, TLP prefix blocked, and poisoned TLP egress blocked. Correctable conditions include receiver error, bad TLP/DLLP, replay rollover, replay timer timeout, advisory non-fatal, correctable internal error, and header-log overflow.

Virtual Channel fields map the VC enhanced capability header, port VC capability/control/status, and VC0/VC1 resource capability/control/status. These fields describe traffic-class mapping, low-priority extended VC count, arbitration support, table offset, VC ID, TC/VC mapping, load/select controls, VC enable, and negotiation pending status.

The PF resizable BAR enhanced capability covers BAR1 through BAR6. Each BAR has supported-size masks and control fields for `BAR_INDEX`, `BAR_TOTAL_NUM`, `BAR_SIZE`, and upper supported-size bits. Power-related extended capabilities include power budget data select/data/capability fields and Dynamic Power Allocation capability, latency indicator, status, control, and eight substate power-allocation registers.

Secondary PCIe and link-training fields include `PCIE_LINK_CNTL3`, lane error status, per-lane 8 GT/s equalization controls for lanes 0 through 15, 16 GT/s PHY capability/header fields, 16 GT/s link status, local/RTM parity mismatch status, and per-lane 16 GT/s transmit presets. The 8 GT/s lane controls use downstream/upstream TX preset and RX preset-hint fields; the 16 GT/s controls use downstream and upstream transmit preset nibbles.

### Isolation, Address Translation, and Virtualization Capabilities

The chunk contains many virtualization and IOMMU-facing capabilities for `DEV0_EPF0_1`:

- ACS capability/control fields for source validation, translation blocking, P2P request/completion redirect, upstream forwarding, egress control, direct translated P2P, and egress vector support.
- ATS capability/control fields for invalidation queue depth, page-aligned request support, STU, and enable.
- PRI/page request fields for enable/reset, response failure, unexpected page-request group/index, PASID required, stopped status, PRG response PASID required, outstanding capacity, and outstanding allocation.
- PASID capability/control fields for execute permission, privileged mode, max PASID width, and PASID enables.
- Multicast fields for group count, window size, ECRC regeneration, MC enable, base address, receive vectors, block-all vectors, and block-untranslated vectors.
- LTR fields for max snoop and no-snoop latency values/scales.
- ARI fields for function-group capability/enables, next-function number, and function group.
- SR-IOV fields for migration capability/status, ARI hierarchy preservation/control, VF enable, VF migration interrupt enable, VF memory-space enable, VF counts, function dependency link, first VF offset, VF stride, VF device ID, supported/system page size, VF BAR base addresses, and migration state array location.
- DLF fields for local/remote data-link feature support, exchange enable, and remote-valid status.

These fields are privilege- and isolation-sensitive. Incorrect masks can alter VF enumeration, VF BAR layout, DMA translation behavior, peer-to-peer routing, or function isolation under VFIO/SR-IOV workloads.

### Margining, VF Resizable BARs, and GPUIOV

`DEV0_EPF0_1` has its own PCIe margining capability and lane 0 through lane 15 control/status fields with the same receiver/type/usage/payload layout as the earlier `DEV2_RC1` margining block. It also has a VF resizable BAR enhanced capability for VF BAR1 through VF BAR6, with `VF_BAR_SIZE_SUPPORTED`, `VF_BAR_INDEX`, `VF_BAR_TOTAL_NUM`, `VF_BAR_SIZE`, and `VF_BAR_SIZE_SUPPORTED_UPPER` fields.

The final part of the chunk starts AMD's GPUIOV vendor-specific PCIe extended capability. It defines the enhanced-capability header, VSEC header, SR-IOV shadow fields (`VF_EN`, `VF_NUM`), soft PF FLR control, and hypervisor/VF mailbox doublewords:

- `HVVM_MBOX_DW0` selects `VF_INDEX` and contains transmit message data, transmit-valid, receive message data, and receive-ack fields.
- `HVVM_MBOX_DW1` provides per-VF transmit-ack and receive-valid bits for VF0 through VF15 across the full 32-bit register.
- `CONTEXT` describes context size, location, and offset.
- `TOTAL_FB` reports total framebuffer available and consumed.
- `VF0_FB` through the start of `VF12_FB` define per-VF framebuffer size/offset pairs, with this chunk ending after `VF12_FB_SIZE__SHIFT`.

The GPUIOV fields are used for GPU virtualization resource accounting, PF/VF mailbox handshakes, PF reset control, and per-VF framebuffer partitioning. Adjacent chunks are required to complete the VF12 field and later GPUIOV framebuffer/scheduler fields.

## Control Flow and State Behavior

There is no executable control flow in this chunk. The effective flow is compile-time substitution: a translation unit includes `nbio_7_7_0_sh_mask.h`, reads or prepares a 16-bit/32-bit NBIO or PCI configuration register value, then uses the generated `*_MASK` and `*_SHIFT` macros to extract or compose fields.

The persistent state represented by these macros lives in hardware, not in the header. Important state includes PCI command/status, BAR advertisements and size controls, MSI/MSI-X configuration, PM/PME bits, PCIe device/link capability and control state, AER status/mask/severity/log state, VC resource state, DPA and power-budget data, lane equalization and margining state, ACS/ATS/PRI/PASID/LTR/ARI controls, SR-IOV VF counts and BARs, DLF exchange state, GPUIOV mailbox state, and per-VF framebuffer allocations.

Some fields are configuration bits expected to persist until reset or reprogramming, such as BAR sizes, ACS controls, MSI/MSI-X enables, SR-IOV controls, VF BAR controls, and GPUIOV framebuffer partitions. Others are status, sticky error, or command-like fields, such as AER status bits, link retrain/compliance bits, FLR initiation, PME status, margining status payloads, mailbox valid/ack bits, soft PF FLR, and SR-IOV migration status. The masks do not encode write-one-to-clear or sequencing rules; consumers must follow the PCIe spec, hardware programming guide, and surrounding AMDGPU code.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header convention. In this checkout, `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c` includes both `nbio/nbio_7_7_0_offset.h` and this `nbio/nbio_7_7_0_sh_mask.h`; `nbio_7_7_0_offset.h` supplies register addresses and this file supplies bit positions and masks. I did not find a sibling `nbio_7_7_0_default.h` in the NBIO include directory, so reset defaults are not assumed here.

The main software integration points are:

- AMDGPU NBIO 7.7 initialization and register access code in `nbio_v7_7.c` and the `nbio_v7_7_funcs` hooks selected by GPU discovery.
- SOC15 register access helpers and any NBIO/PCIe diagnostic path that decodes PCIe config-space fields using generated masks.
- PCIe link training and diagnostics paths that inspect link status, lane errors, equalization phases, 16 GT/s parity mismatch, and margining payloads.
- Interrupt setup/validation paths that touch MSI/MSI-X capability fields.
- Error handling paths that decode and clear AER status, masks, severity, header logs, and prefix logs.
- SR-IOV, VFIO, hypervisor, and GPUIOV paths that depend on VF counts, VF BARs, migration fields, per-VF framebuffer partitioning, mailbox handshakes, and PF reset controls.
- IOMMU and peer-to-peer isolation flows that depend on ACS, ATS, PRI, PASID, ARI, multicast, and LTR capability encodings.

The semantic dependencies are the PCI/PCIe specifications and AMD NBIO 7.7.0 hardware register definitions. Similar field names exist across other NBIO generations, but capability presence, register offsets, field widths, and reserved bits can differ. Consumers should not mix this mask file with offset headers from other NBIO versions.

## Risks and Maintenance Notes

- Bitfield drift is high impact. A wrong shift or mask can silently decode the wrong hardware bit or write unrelated/reserved bits.
- Standard PCI header and capability-chain fields affect enumeration. Bad `CAP_ID`, `CAP_VER`, `NEXT_PTR`, class, command/status, BAR, or interrupt masks can confuse firmware, the Linux PCI core, or user-space config-space inspection.
- AER fields may be sticky or write-one-to-clear. Treating status masks as ordinary read/write configuration can lose diagnostic evidence or fail to clear real errors.
- Link training, equalization, margining, DPA, and power-management fields affect PCIe stability, advertised latency, and device readiness. Incorrect writes can cause link retraining failures, bad Gen4 equalization state, or power-management regressions.
- ACS, ATS, PRI, PASID, ARI, multicast, and SR-IOV fields are security- and virtualization-sensitive. Incorrect advertisement or control masks can affect DMA translation, peer-to-peer forwarding, VF routing, and VFIO isolation.
- GPUIOV mailbox and framebuffer fields are privilege-sensitive. Wrong masks can break PF/VF communication, reset control, resource accounting, or per-VF framebuffer partitioning.
- The chunk starts and ends mid-family. `DEV2_RC1` lane 6 equalization begins before this chunk, and GPUIOV VF12 framebuffer fields continue in the next chunk. The final merged per-file report should reconcile these boundaries.
- Repetitive lane and VF definitions are easy to review incorrectly. Lane numbers, VF numbers, status/control suffixes, and mask widths should be checked mechanically where possible.
- Constants use `L` suffixes and full-width masks such as `0xFFFFFFFFL`; callers should keep the established AMDGPU helper types to avoid signedness or truncation surprises.

## Test and Validation Signals

Useful validation signals for this chunk are mostly build, static consistency, and hardware/config-space tests:

- Build AMDGPU translation units that include `nbio_7_7_0_sh_mask.h`, especially `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, to catch missing or renamed macros.
- Static checks should verify each field has consistent `*_SHIFT` and `_MASK` definitions, masks align with their shifts, repeated lane/VF layouts remain consistent, and full-width fields use expected masks.
- Cross-header checks should verify register names in this chunk have matching address macros in `nbio_7_7_0_offset.h`.
- PCI config-space dumps on NBIO 7.7 hardware should match decoded vendor/device/class/header/BAR/capability-chain, PM, PCIe, MSI/MSI-X, AER, VC, power-budget, DPA, ACS, ATS, PRI, PASID, SR-IOV, DLF, margining, and GPUIOV fields.
- PCIe link tests should verify negotiated speed/width, retrain behavior, 8 GT/s and 16 GT/s equalization status, lane error status, RTM parity mismatch status, and margining command/status behavior.
- AER validation should inject or observe correctable and uncorrectable errors and confirm status, mask, severity, header-log, and prefix-log decoding.
- SR-IOV/VFIO validation should enable VFs, verify VF counts/stride/device IDs/page sizes, validate VF BAR base and resize behavior, exercise migration-state fields when supported, and check ACS/ATS/PRI/PASID isolation behavior.
- GPUIOV validation should cover mailbox valid/ack sequencing, selected VF index handling, soft PF FLR behavior, total framebuffer accounting, and per-VF framebuffer size/offset reporting.
