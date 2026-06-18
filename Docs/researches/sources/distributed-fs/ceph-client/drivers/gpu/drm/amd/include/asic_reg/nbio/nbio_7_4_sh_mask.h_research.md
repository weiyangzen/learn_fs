# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003226`: lines 1-2434, `Docs/researches/chunks/subset-b-003226_research.md`
- `subset-b-003227`: lines 2435-4879, `Docs/researches/chunks/subset-b-003227_research.md`
- `subset-b-003228`: lines 4880-7320, `Docs/researches/chunks/subset-b-003228_research.md`
- `subset-b-003229`: lines 7321-9744, `Docs/researches/chunks/subset-b-003229_research.md`
- `subset-b-003230`: lines 9745-12178, `Docs/researches/chunks/subset-b-003230_research.md`
- `subset-b-003231`: lines 12179-14599, `Docs/researches/chunks/subset-b-003231_research.md`
- `subset-b-003232`: lines 14600-17033, `Docs/researches/chunks/subset-b-003232_research.md`
- `subset-b-003233`: lines 17034-19455, `Docs/researches/chunks/subset-b-003233_research.md`
- `subset-b-003234`: lines 19456-22067, `Docs/researches/chunks/subset-b-003234_research.md`
- `subset-b-003235`: lines 22068-24525, `Docs/researches/chunks/subset-b-003235_research.md`
- `subset-b-003236`: lines 24526-26923, `Docs/researches/chunks/subset-b-003236_research.md`
- `subset-b-003237`: lines 26924-29367, `Docs/researches/chunks/subset-b-003237_research.md`
- `subset-b-003238`: lines 29368-31801, `Docs/researches/chunks/subset-b-003238_research.md`
- `subset-b-003239`: lines 31802-34237, `Docs/researches/chunks/subset-b-003239_research.md`
- `subset-b-003240`: lines 34238-36659, `Docs/researches/chunks/subset-b-003240_research.md`
- `subset-b-003241`: lines 36660-39092, `Docs/researches/chunks/subset-b-003241_research.md`
- `subset-b-003242`: lines 39093-41521, `Docs/researches/chunks/subset-b-003242_research.md`
- `subset-b-003243`: lines 41522-43896, `Docs/researches/chunks/subset-b-003243_research.md`
- `subset-b-003244`: lines 43897-46474, `Docs/researches/chunks/subset-b-003244_research.md`
- `subset-b-003245`: lines 46475-48482, `Docs/researches/chunks/subset-b-003245_research.md`

## Chunk Research

### subset-b-003226: lines 1-2434

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 1-2434

## Scope

This chunk is the opening segment of AMDGPU's generated NBIO 7.4 shift/mask header. It contains 2,161 `#define` field-layout macros and 248 comment lines in the requested range. There are no C functions, structs, enums, variables, allocations, locks, or executable statements here.

The range covers all of the first address block, `nbio_pcie0_pswuscfg0_cfgdecp`, then begins the second address block, `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp`, through the start of `BIF_CFG_DEV0_EPF0_0_DEVICE_CNTL2`. The first block describes PCI/PCIe configuration-space and enhanced capability fields for `PSWUSCFG0`; the second block restarts the same style of endpoint-function configuration fields under the `BIF_CFG_DEV0_EPF0_0_*` namespace. The chunk ends mid-register-family, so adjacent chunks are required for the complete `BIF_CFG_DEV0_EPF0_0_DEVICE_CNTL2` definition and the rest of that endpoint-function block.

Although this repository path sits under a `ceph-client` source mirror, the file is AMDGPU hardware register metadata. It has no direct Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_4_sh_mask.h` exports the bit geometry for NBIO 7.4 registers. Each field generally has:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used to encode or extract the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, clear, or update the field.

This chunk lets AMDGPU and SMU/power-management code address PCI bridge/root-port and endpoint-function PCIe configuration fields without hard-coding bit positions. Consumers combine these masks with the sibling address metadata in `nbio_7_4_offset.h` and register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, or other NBIO/SMN accessors.

## Important Macro Families

The `PSWUSCFG0_*` section starts with conventional PCI configuration header fields:

- Identification and class fields: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `HEADER`, and `BIST`.
- Command and status control: `COMMAND` exposes I/O access, memory access, bus master, parity/SERR, fast back-to-back, and interrupt disable bits; `STATUS` and `SECONDARY_STATUS` expose capability-list presence and PCI error/status latches.
- Bridge resource windows: `SUB_BUS_NUMBER_LATENCY`, `IO_BASE_LIMIT`, `IO_BASE_LIMIT_HI`, `MEM_BASE_LIMIT`, `PREF_BASE_LIMIT`, `PREF_BASE_UPPER`, and `PREF_LIMIT_UPPER` describe bus numbering and I/O, memory, and prefetchable-memory bridge windows.
- Interrupt and bridge policy: `CAP_PTR`, `INTERRUPT_LINE`, `INTERRUPT_PIN`, `IRQ_BRIDGE_CNTL`, and `EXT_BRIDGE_CNTL` cover capability-list traversal, interrupt routing, bridge reset/VGA/ISA behavior, and port-80 decode.
- Vendor and subsystem IDs: `VENDOR_CAP_LIST`, `ADAPTER_ID_W`, and later `SSID_CAP` describe capability headers and subsystem vendor/device IDs.

The PCI power-management and standard PCIe capability groups include:

- `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL` for PM capability versioning, PME support/enables/status, D-state selection, auxiliary current, bus-power support, and PM data.
- `PCIE_CAP_LIST` and `PCIE_CAP` for the PCIe capability header, device type, slot implementation, and interrupt message number.
- `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` for max payload support/selection, relaxed ordering, extended tags, no-snoop, max read request, FLR or bridge retry behavior, error enables/status, auxiliary power, and transactions-pending status.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` for supported/current link speed, width, ASPM/power-management control, retraining, common-clock configuration, clock power management, data-link active reporting, and bandwidth-management events.
- `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` for completion-timeout support/control, atomic operations, ARI, LTR, OBFF, ten-bit tags, emergency power reduction, target speed, Enter Compliance, equalization controls, selected de-emphasis, retimer presence, and downstream-component presence.

Message signaling and capability-list metadata are represented by:

- `MSI_CAP_LIST`, `MSI_MSG_CNTL`, `MSI_MSG_ADDR_LO`, `MSI_MSG_ADDR_HI`, `MSI_MSG_DATA`, and `MSI_MSG_DATA_64`.
- `MSI_MAP_CAP_LIST`, `MSI_MAP_CAP`, `MSI_MAP_ADDR_LO`, and `MSI_MAP_ADDR_HI`, which define MSI mapping enable/fixed/capability type and address fields.
- Vendor-specific enhanced capability headers and scratch registers: `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, `PCIE_VENDOR_SPECIFIC1`, and `PCIE_VENDOR_SPECIFIC2`.

The PCIe enhanced-capability section covers link features and advanced error reporting:

- Virtual channels: `PCIE_VC_ENH_CAP_LIST`, port VC capability/control/status registers, and `PCIE_VC0_RESOURCE_*`/`VC1_RESOURCE_*` for traffic-class-to-VC mapping, arbitration-table load/status, VC IDs, VC enablement, and negotiation-pending status.
- Device serial number: `PCIE_DEV_SERIAL_NUM_ENH_CAP_LIST` plus low/high serial-number dwords.
- AER: `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, `PCIE_UNCORR_ERR_SEVERITY`, `PCIE_CORR_ERR_STATUS`, `PCIE_CORR_ERR_MASK`, `PCIE_ADV_ERR_CAP_CNTL`, four header-log dwords, and four TLP-prefix-log dwords. Fields include DLP, surprise-down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, malformed TLP, ECRC, unsupported request, ACS violation, atomic egress blocked, corrected receive/bad TLP/DLLP/replay statuses, ECRC enablement, first-error pointer, and multi-header logging.
- Secondary PCIe and equalization: `PCIE_SECONDARY_ENH_CAP_LIST`, `PCIE_LINK_CNTL3`, `PCIE_LANE_ERROR_STATUS`, and `PCIE_LANE_0_EQUALIZATION_CNTL` through `LANE_15_EQUALIZATION_CNTL`, defining equalization trigger/status and per-lane downstream/upstream TX preset and RX preset-hint fields.
- ACS, multicast, LTR, ARI, and L1 substates: `PCIE_ACS_*`, `PCIE_MC_*`, `PCIE_LTR_*`, `PCIE_ARI_*`, and `PCIE_L1_PM_SUB_*` describe peer-to-peer isolation controls, multicast address/receive/block vectors, latency tolerance values/scales, alternate routing ID capabilities/control, and L1.1/L1.2 enable/timing thresholds.
- ESM, DLF, 16GT PHY, and receiver margining: `PCIE_ESM_*` exposes Emergency Signaling Mode status/control and many advertised data-rate capability bits from 8.0G through 28.0G; `DATA_LINK_FEATURE_*` exposes data-link feature support/exchange state; `LINK_*_16GT`, parity mismatch status, and per-lane 16GT equalization preset controls describe Gen4/16GT link training; `MARGINING_PORT_*` plus per-lane margining control/status registers expose PCIe receiver margining software readiness and per-lane payload/status.

The second address block, `BIF_CFG_DEV0_EPF0_0_*`, begins a device/function endpoint configuration namespace:

- It repeats endpoint identity, command/status, class, cache-line, latency, header, BIST, BAR1-BAR6, subsystem IDs, ROM BAR, capability pointer, interrupt line/pin, min grant, max latency, vendor capability, PM capability, PCIe capability, device capability/control/status, link capability/control/status, and device capability 2.
- Compared with the first bridge-oriented `PSWUSCFG0` block, this endpoint section uses endpoint-style BARs and includes `INITIATE_FLR` in `DEVICE_CNTL` plus `EMER_POWER_REDUCTION_DETECTED` in `DEVICE_STATUS`.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated preprocessor macro namespace.

The macros are untyped integer literals, mostly with an `L` suffix. They do not encode register addresses, reset values, read/write permissions, volatile semantics, write-one-to-clear behavior, side effects, firmware ownership, or sequencing rules. Those properties must come from sibling generated headers, hardware documentation, and the AMDGPU code that uses these definitions.

## Control Flow

This header has no runtime control flow. Runtime control is external:

1. AMDGPU or SMU code selects a register address from `nbio_7_4_offset.h` or related NBIO/SMN metadata.
2. It reads a register and extracts fields with the `__SHIFT` and `_MASK` constants, or composes a write while preserving unrelated bits.
3. Hardware then acts on the resulting PCIe configuration, power-management, AER, virtual-channel, ACS, multicast, LTR, ARI, DLF, 16GT equalization, or receiver-margining state.

The field names imply asynchronous hardware flows outside this file: PCIe link training and retraining, equalization, data-link active changes, bandwidth-management notifications, completion-timeout handling, AER logging, PME generation, FLR, L1.1/L1.2 entry and exit, multicast filtering, ACS redirection/blocking, DLF exchange, and receiver margining. Driver code that touches these registers must provide the ordering, polling, timeout, and recovery behavior.

## State And Persistence Behavior

The header owns no memory and persists nothing by itself. It describes hardware-visible state in PCIe configuration and enhanced capability registers. Persistence depends on reset domain, PCIe hot/warm reset, function-level reset, GPU reset, suspend/resume, power/clock gating, firmware/BIOS initialization, and explicit AMDGPU writes.

Represented state includes read-only capability bits, writable control bits, status latches, event masks, error severity policy, header/TLP-prefix logs, MSI message address/data fields, bridge windows, BARs, subsystem IDs, link speed/width policy, equalization presets, L1 substate timing, LTR latency values, ACS isolation controls, multicast receive/block vectors, DLF status, and receiver-margining controls. Many fields named `*_STATUS`, `*_PENDING`, `*_DETECTED`, `*_ACTIVE`, `*_COMPLETE`, or `*_SUCCESS` are live or latched hardware status rather than durable software state.

Incorrect values can survive long enough to affect later driver phases, especially across suspend/resume, GPU reset recovery, FLR, or link retraining. The mask header alone is not sufficient to decide whether a field is safe to write or whether a status bit must be cleared by writing one.

## Dependencies And Integration Points

This chunk must stay synchronized with the generated NBIO 7.4 register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_offset.h` provides matching `cfgPSWUSCFG0_*` and related register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_0_smn.h` provides SMN-style address metadata used by NBIO 7.4 code.
- Consumers include `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c`, `pm/powerplay/hwmgr/vega20_hwmgr.c`, `pm/powerplay/hwmgr/vega20_inc.h`, and SMU power-management files for Arcturus, Aldebaran, and SMU 13.0.6.

Integration points are PCIe configuration-space access, NBIO bring-up, power-management policy, SMU telemetry/control, GPU reset and FLR behavior, interrupt/MSI setup, AER/RAS reporting, link capability negotiation, ASPM/L1SS, data-link feature negotiation, Gen4 equalization, receiver margining, and virtualization/isolation policy through ACS/ARI/multicast controls.

## Risks And Edge Cases

- Generated mask drift can compile cleanly while decoding or programming the wrong bit, causing PCIe enumeration, link training, power management, AER, interrupt, FLR, or isolation failures.
- The chunk ends inside `BIF_CFG_DEV0_EPF0_0_DEVICE_CNTL2`; the merge lane must combine adjacent chunks before treating that register family or the second address block as complete.
- Some field names end in `_MASK_MASK` because the hardware field itself is a mask. Call sites must distinguish hardware mask fields from the generated macro suffix.
- Bridge-window, BAR, ROM BAR, and MSI address/data fields are address-sensitive; incorrect shifts or masks can route MMIO/MSI traffic incorrectly.
- Error-status and error-mask fields can either hide real PCIe errors or create noisy false reports if programmed incorrectly.
- Equalization, 16GT, DLF, L1SS, ESM, and receiver-margining fields are timing-sensitive link controls. Writes may require hardware-specific sequencing, polling, and rollback.
- FLR, PME, bus reset, link disable/retrain, and secondary-bus reset bits can disrupt the device or downstream topology if used outside controlled reset paths.
- Capability-list `NEXT_PTR` and enhanced capability `NEXT_PTR` fields are part of PCIe config-space discovery; bad metadata can break capability walking or diagnostics.

## Test Signals

- Build AMDGPU configurations that include NBIO 7.4, Vega20, Arcturus, Aldebaran, and SMU 13.0.6 paths. Compile-time coverage catches missing or renamed generated symbols.
- Run generated-header consistency checks: every field should have coherent `__SHIFT` and `_MASK` values, masks in a register should not overlap unexpectedly, and repeated lane families should follow the expected per-lane pattern.
- Cross-check this chunk against `nbio_7_4_offset.h` so each register-family comment has a corresponding address where expected.
- On supported hardware, validate PCIe cold boot, enumeration, BAR programming, MSI/MSI mapping, GPU reset, FLR, suspend/resume, link retraining, negotiated speed/width, ASPM/L1SS, and AER/RAS event reporting.
- For diagnostic or recovery code touching these fields, inspect register traces to confirm reserved bits are preserved, status bits are cleared according to hardware rules, temporary debug/force/injection controls are restored, and polling paths have timeouts for asynchronous link state.

### subset-b-003227: lines 2435-4879

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 2435-4879

## Scope

This chunk is a generated AMDGPU NBIO 7.4 shift/mask header segment for PCIe configuration-space and AMD GPU-IOV vendor-specific fields. It contains 2,093 `#define` entries over 2,445 source lines, with 1,052 `__SHIFT` definitions and 1,073 `_MASK` definitions. The count is not a strict pair count because the chunk starts and ends inside register definitions, and because some generated hardware field names themselves contain `MASK`.

The range begins inside `BIF_CFG_DEV0_EPF0_0_DEVICE_CNTL2`, covering the remaining EPF0 PCIe Device Control 2 fields and masks. It then runs through a large EPF0 endpoint-function capability area, including MSI/MSI-X, vendor-specific and virtual-channel capabilities, AER, resizable BAR and VF BAR metadata, DPA, secondary PCIe, ACS/ATS/PASID/PRI/multicast/LTR/ARI/SR-IOV/TPH/data-link/16 GT/s PHY/lane-margining features, and AMD GPU-IOV mailbox/framebuffer/scheduler registers. The chunk then enters `addressBlock: nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` and covers EPF1 standard PCI/PCIe configuration fields from vendor ID through the first `BIF_CFG_DEV0_EPF1_0_DEVICE_CAP2` masks. The previous chunk is needed for the first fields of EPF0 `DEVICE_CNTL2`, and the next chunk is needed to complete EPF1 `DEVICE_CAP2` and the later EPF1 capability space.

Although this mirror lives under `sources/distributed-fs/ceph-client`, the file is AMDGPU hardware register metadata. It has no Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_4_sh_mask.h` publishes symbolic bit positions and masks for NBIO 7.4 registers. The companion `nbio_7_4_offset.h` header identifies register offsets such as `cfgBIF_CFG_DEV0_EPF0_0_DEVICE_CNTL2`, while this file identifies the individual fields inside those registers. Driver code uses these macros with AMDGPU register access helpers, `REG_SET_FIELD`/`REG_GET_FIELD` style helpers, or direct read/modify/write logic so it does not hard-code bit numbers.

This chunk's specific purpose is to describe the bit layouts for two endpoint-function regions:

- The tail of EPF0 PCIe capability and extended capability space, including virtualization and GPU-IOV fields used by PF/VF resource control.
- The beginning of EPF1 PCI configuration space and early PCIe capability fields, mirroring the standard endpoint-function configuration model for a second function.

## Important Macro Families

The EPF0 Device Control 2 and Link Capability 2 area covers completion timeout controls, ARI forwarding, atomic-op request/egress behavior, ID-based ordering, LTR enable, emergency power reduction, 10-bit tag request support, OBFF, end-to-end TLP prefix blocking, supported link speed vectors, crosslink/RTM presence support, target link speed, compliance controls, autonomous speed disable, de-emphasis, equalization status, and downstream component presence.

The MSI/MSI-X groups define capability list headers, MSI enable/multiple-message/64-bit/per-vector masking fields, MSI message address and data fields, mask and pending vectors, MSI-X table size/function mask/enable fields, table BIR/offset, and PBA BIR/offset. These fields are central to interrupt delivery and masking for the endpoint function.

The EPF0 vendor-specific, virtual-channel, serial-number, and AER groups cover VSEC headers and scratch registers, VC capability/control/status for port and VC0/VC1 resources, device serial number dwords, uncorrectable and correctable AER status/mask/severity fields, AER capability/control, header logs, and TLP prefix logs. Notable AER fields include data-link protocol, surprise down, poisoned TLP, flow-control protocol, completion timeout, completer abort, unexpected completion, unsupported request, ECRC, ACS violation, internal error, atomic-op egress blocked, and TLP prefix blocked indications.

The BAR, power, DPA, secondary PCIe, and lane-diagnostic groups include PCIe BAR enhanced capability headers, BAR1-BAR6 capability/control pairs, power budget selection/data/capability fields, DPA capability/latency/status/control and eight substate power-allocation registers, link control 3, lane error status, and lane 0-15 equalization controls. These fields describe BAR sizing, active BAR size selection, power budget encoding, dynamic power substate support, and per-lane equalization presets/cursors.

The isolation and address-translation groups cover ACS, ATS, Page Request Interface, PASID, multicast, LTR, ARI, SR-IOV, TPH requester, and Data Link Feature capabilities. These fields expose source validation, translation blocking, request/completion redirection, upstream forwarding, egress control, ATS invalidate queue depth, PRI enable/reset/status, PASID execution/privileged/no-privileged mode support, multicast receive/block masks, LTR snoop/no-snoop latencies, ARI next-function/grouping, SR-IOV VF enable/count/stride/device/page-size/VF BAR fields, TPH steering modes, and data-link feature exchange support.

The 16 GT/s PHY and lane-margining blocks define enhanced capability headers, 16 GT/s link capability/control/status, local and RTM parity mismatch status, lane 0-15 equalization controls, margining port capability/status, and lane 0-15 margining control/status pairs. These fields are highly repetitive and lane-indexed; they are used for high-speed link training diagnostics and margining request/result payloads.

The VF resizable BAR and AMD GPU-IOV vendor-specific section is the largest EPF0 vendor area in this chunk. It covers VF BAR1-BAR6 capability/control fields, a GPUIOV VSEC header, SR-IOV shadow state, interrupt enable/status bits, reset control, HVVM mailbox dwords, context/total-framebuffer/offset fields, P2P-over-XGMI enable bits, `VF0_FB` through `VF30_FB` size/offset pairs, and repeated scheduler dwords for UVD, VCE, GFX, and UVD1 engines. Scheduler fields include mode, command buffer address/size, queue pointers, doorbell offsets, context save area address/size, engine IDs, VF counts, timing windows, flags, and status/control payloads.

The EPF1 section starts at `addressBlock: nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp`. It covers vendor/device ID, command/status, revision/interface/subclass/base-class bytes, cache-line/latency/header/BIST fields, BAR1-BAR6, adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant/max latency, vendor capability list, writable adapter ID, PM capability and PM status/control, PCIe capability header, device capability/control/status, link capability/control/status, and the beginning of Device Capability 2.

## APIs, Types, And Functions

There are no callable APIs, C types, functions, variables, locks, allocations, or executable statements in this range. The public interface is the generated preprocessor namespace:

- `BIF_CFG_DEV0_EPF0_0_<REGISTER>__<FIELD>__SHIFT` and `BIF_CFG_DEV0_EPF0_0_<REGISTER>__<FIELD>_MASK` describe EPF0 fields.
- `BIF_CFG_DEV0_EPF1_0_<REGISTER>__<FIELD>__SHIFT` and `BIF_CFG_DEV0_EPF1_0_<REGISTER>__<FIELD>_MASK` describe EPF1 fields.
- Hardware fields named `MASK` naturally produce generated macro names like `*_MASK_MASK`; these are valid names and should not be normalized by hand.

The macro values are only field geometry. They do not encode access width, reset value, read/write permissions, write-one-to-clear behavior, firmware ownership, or ordering requirements.

## Control Flow

This header has no local runtime control flow. The runtime pattern is external:

1. AMDGPU code selects an NBIO 7.4 register for the active ASIC and endpoint function.
2. `nbio_7_4_offset.h` supplies the register offset or config-space address, such as EPF0 `DEVICE_CNTL2` at `cfgBIF_CFG_DEV0_EPF0_0_DEVICE_CNTL2`.
3. This shift/mask header supplies the bit location for a field extraction, comparison, or read/modify/write update.
4. Access happens through AMDGPU MMIO, SMN, or PCIe config access helpers outside this header.

The direct NBIO 7.4 implementation file, `drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c`, includes both `nbio/nbio_7_4_offset.h` and `nbio/nbio_7_4_sh_mask.h`. That implementation handles NBIO revision reads, memory-controller access gating, doorbell ranges, interrupt control, RAS paths, ASPM/LTR programming, and register remapping. For example, the NBIO 7.4 ASPM/LTR path uses the EPF0 Device Control 2 LTR enable bit through a local SMN alias and mask, which corresponds semantically to the `BIF_CFG_DEV0_EPF0_0_DEVICE_CNTL2__LTR_EN` field in this generated file.

## State And Persistence Behavior

The header itself stores no software state and persists nothing. It describes hardware-visible PCIe configuration and AMD vendor-specific NBIO state.

State represented by this chunk includes PCIe link and device control, MSI/MSI-X programming and pending/mask bits, VC negotiation state, AER status/mask/severity/logs, BAR and VF BAR sizing, DPA and power-budget data, lane equalization and margining results, ACS/ATS/PASID/PRI/SR-IOV enablement, LTR latency values, ARI function grouping, TPH requester configuration, Data Link Feature exchange status, GPUIOV interrupts, GPUIOV mailbox valid/ack payloads, PF/VF reset state, framebuffer allocation per VF, P2P-over-XGMI enables, and per-engine scheduler state.

Persistence depends on hardware and platform events: PCI conventional reset, hot reset, function-level reset, SR-IOV enable/disable, suspend/resume, power-gating, firmware or hypervisor ownership, and explicit driver writes. Fields named `STATUS`, `ERR_STATUS`, `PENDING`, `MASK`, `INTR_STATUS`, `TRN_ACK`, `RCV_VALID`, or `RESET_CONTROL` should be assumed to have side effects or latching semantics until the programming guide or caller code proves otherwise.

## Dependencies And Integration Points

This generated file depends on AMD's NBIO 7.4 register database and must stay synchronized with `nbio_7_4_offset.h`. The offset header supplies matching `cfgBIF_CFG_DEV0_EPF0_0_*` and `cfgBIF_CFG_DEV0_EPF1_0_*` offsets, including the EPF0 GPUIOV register window and the EPF1 block beginning at `cfgBIF_CFG_DEV0_EPF1_0_VENDOR_ID`.

Source-tree consumers include `amdgpu/nbio_v7_4.c`, power management code such as the Vega20 and SMU PPT paths, display code that includes NBIO 7.4 offsets, PSP code, and SOC discovery setup that installs `nbio_v7_4_funcs` and `nbio_v7_4_ras`. The protocol-level dependencies are the PCI and PCI Express specifications plus AMD-specific NBIO, GPU-IOV, SR-IOV, mailbox, scheduler, and XGMI virtualization contracts.

Major integration areas are PCIe enumeration and capability handling, BAR and VF BAR sizing, MSI/MSI-X interrupt delivery, AER/RAS reporting, ASPM and LTR power management, link training and lane diagnostics, ACS/ATS/PASID/PRI/IOMMU-aware DMA flows, SR-IOV and VF provisioning, GPUIOV PF/VF mailbox exchange, framebuffer partitioning, scheduler setup for virtualized engines, reset/recovery, and debug or register-dump tooling.

## Risks And Edge Cases

- The chunk starts inside EPF0 `DEVICE_CNTL2` and ends inside EPF1 `DEVICE_CAP2`; adjacent chunks are required for a complete per-register and per-file view.
- Generated header drift can compile cleanly while programming the wrong bit, especially in dense fields such as AER severity/masks, ACS controls, SR-IOV state, MSI/MSI-X masks, LTR/ASPM controls, and GPUIOV mailbox bits.
- EPF0 and EPF1 names are similar but target different endpoint functions. Applying an EPF0 mask to an EPF1 offset, or vice versa, can silently corrupt the wrong function's configuration.
- Repeated lane, VF, BAR, and scheduler blocks are susceptible to mechanical review errors. Lane number, VF index, engine family, and BAR index are often the only visible differences across many definitions.
- Full-width masks such as `0xFFFFFFFFL` describe field coverage, not permission to write all bits as one. Reserved or log fields may have hardware-defined clear or sticky behavior.
- AER, MSI pending, interrupt status, mailbox, and error-log fields can be sticky, write-one-to-clear, read-sensitive, or owned by firmware/hypervisor logic. Generic read/modify/write code can drop diagnostic evidence or break a handshake.
- ACS, ATS, PASID, PRI, multicast, and SR-IOV fields affect DMA isolation and address translation. Incorrect masks can become security, IOMMU fault, or peer-to-peer routing issues.
- Link equalization, 16 GT/s PHY, and margining fields are timing-sensitive. Incorrect lane masks can produce intermittent link training or signal integrity failures isolated to one lane.
- GPUIOV framebuffer and scheduler fields encode virtualization resource contracts. Wrong size/offset, doorbell, queue pointer, or engine assignment fields can affect only one VF or one media/graphics engine, making failures hard to correlate.

## Test Signals

Useful validation signals for this chunk are:

- Build coverage for AMDGPU translation units that include `nbio/nbio_7_4_sh_mask.h`, especially `amdgpu/nbio_v7_4.c`, Vega20/SMU power-management files, and display/PSP users that depend on NBIO 7.4 headers.
- Mechanical cross-checks that every `BIF_CFG_DEV0_EPF0_0_*` and `BIF_CFG_DEV0_EPF1_0_*` register family in this chunk has a matching `cfg...` definition in `nbio_7_4_offset.h`.
- Generated-header comparison against AMD's authoritative NBIO 7.4 register database, with extra focus on repeated lane 0-15, VF0-VF30, BAR1-BAR6, and scheduler DW0-DW8 patterns.
- Static validation that each field mask is plausible for its shift and width, that reserved/full-width fields remain intentional, and that generated `*_MASK_MASK` names are preserved.
- Hardware or simulator checks that PCIe capability decoding matches `lspci -vvxxx`-style observations for MSI/MSI-X, link capability/control/status, Device Capability 2, AER, ACS, ATS, PASID, PRI, LTR, ARI, SR-IOV, TPH, and Data Link Feature fields.
- Interrupt tests covering MSI/MSI-X address/data/mask/pending behavior and GPUIOV interrupt enable/status bits.
- Link-training diagnostics on NBIO 7.4 hardware for 8 GT/s and 16 GT/s equalization, parity mismatch reporting, lane error status, and lane margining request/status fields.
- Error injection or RAS observation that verifies AER status/mask/severity, header logs, TLP prefix logs, and source decoding are not mis-shifted.
- Virtualization tests that enable/disable SR-IOV, verify VF counts/strides/page sizes/VF BAR sizing, exercise GPUIOV mailbox valid/ack flows, validate framebuffer partition reporting for VF0-VF30, and confirm UVD/VCE/GFX/UVD1 scheduler state per VF.
- Power-management tests around ASPM, LTR, DPA, PM capability/status, suspend/resume, and reset/FLR paths to ensure field programming survives or is restored according to platform policy.

## Merge Notes

The final per-file report should merge this chunk with adjacent `nbio_7_4_sh_mask.h` chunks. This range should not be presented as owning the full EPF0 `DEVICE_CNTL2` register or the full EPF1 `DEVICE_CAP2` register because both cross chunk boundaries.

### subset-b-003228: lines 4880-7320

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 4880-7320

## Purpose

This chunk is an auto-generated AMD NBIO 7.4 shift/mask slice for PCI/PCIe configuration-space fields. It contains no executable driver logic. Its purpose is to expose stable preprocessor constants that let NBIO 7.4 consumers extract, compare, and program individual fields in hardware registers using the matching offsets from `nbio_7_4_offset.h`.

The selected range starts in the mask half of `BIF_CFG_DEV0_EPF1_0_DEVICE_CAP2`, covers the rest of the `BIF_CFG_DEV0_EPF1_0` PCIe capability and extended-capability map through SR-IOV, VF resize-BAR, and AMD GPU-IOV vendor-specific registers, then enters the `nbio_nbif0_bif_cfg_dev0_swds_bifcfgdecp` address block and reaches the early `BIF_CFG_DEV0_SWDS0` PCIe link capability/control area.

## Public Surface In This Chunk

The public surface is 2,093 `#define` macros in this line range: 1,041 `__SHIFT` constants and 1,052 `_MASK` constants, grouped under 346 generated register comments. The counts are not perfectly paired because the chunk begins mid-register, includes whole-register payload/log fields, and has hardware fields whose generated names already include `MASK`.

Macro names follow the generated register-field convention:

- `BIF_CFG_DEV0_EPF1_0_<REGISTER>__<FIELD>__SHIFT` gives the bit position for a field in the EPF1 function's config-space register.
- `BIF_CFG_DEV0_EPF1_0_<REGISTER>__<FIELD>_MASK` gives the pre-shifted mask for that field.
- `BIF_CFG_DEV0_SWDS0_<REGISTER>__<FIELD>__SHIFT` and `_MASK` provide the same contract for the SWDS0 config-decode block.

There are no functions, structs, enums, inline helpers, storage objects, or runtime APIs in this range. The API contract is the exact macro spelling and numeric value, which must stay synchronized with the same ASIC generation's offset header and AMD's register database.

## Register Coverage

For `BIF_CFG_DEV0_EPF1_0`, this chunk covers the tail of PCIe capability 2 and a broad set of conventional and enhanced capabilities:

- Device/link/slot capability 2, control 2, and status 2 fields, including completion timeout, ARI, atomic operations, ID-based ordering, LTR, OBFF, 10-bit tags, end-to-end TLP prefixes, emergency power reduction, target link speed, compliance controls, de-emphasis, equalization status, crosslink state, and downstream-component presence.
- MSI and MSI-X capability fields: capability-list headers, MSI enable/multi-message/64-bit/per-vector-mask bits, message address/data, mask and pending vectors, MSI-X table size, function mask, enable, table BIR/offset, and PBA BIR/offset.
- Vendor-specific and virtual-channel capabilities: VSEC headers/scratch registers, VC enhanced-capability headers, port VC capability/control/status, and VC0/VC1 resource capability, arbitration, port arbitration, ID mapping, enable, negotiation, and pending status.
- Device serial number, Advanced Error Reporting, header/TLP-prefix logs, and resizable BAR-like capability/control blocks for BAR1 through BAR6.
- Power budget and Dynamic Power Allocation registers, including data selection/value fields, capability fields, transition latency indicators, DPA enable/status, substate count, and per-substate power allocation entries.
- Secondary PCIe, ACS, ATS, Page Request Interface, PASID, multicast, LTR, ARI, SR-IOV, TPH requester, Data Link Feature, 16 GT PHY/equalization, and lane-margining capability groups.
- VF resize-BAR capability/control groups for VF BAR1 through VF BAR6.
- AMD GPU-IOV VSEC fields for SR-IOV shadowing, interrupts, reset control, HVVM mailbox dwords, context, total frame-buffer size, offsets, P2P-over-XGMI enablement, per-VF framebuffer slices for VF0 through VF30, and scheduler dwords for UVD, VCE, GFX, and UVD1 scheduling state.

The chunk then declares the start of the `BIF_CFG_DEV0_SWDS0` block:

- Conventional PCI identification and class/header fields: vendor ID, device ID, command, status, revision, program interface, subclass, base class, cache line, latency, header type, BIST, and base address.
- Bridge-style bus/window and interrupt fields: secondary/subordinate bus numbers, secondary latency, I/O base/limit, secondary status, memory and prefetchable memory windows, upper prefetchable bounds, upper I/O bounds, capability pointer, interrupt line/pin, and bridge control.
- SWDS0 power-management and PCIe capability fields through `LINK_CAP`, with `LINK_CNTL` beginning immediately after the assigned range.

## Field Semantics

The EPF1 fields mirror PCI Express endpoint and extended-capability layouts. Capability fields advertise supported protocol features, while control fields enable or disable policy such as completion timeout behavior, ARI forwarding, atomic requests, LTR, OBFF, end-to-end prefixes, MSI/MSI-X routing, VC negotiation, ACS isolation, address translation, page requests, PASID execution/privilege, multicast routing, SR-IOV VF creation, TPH steering, and resizable BAR sizing.

AER-related fields expose uncorrectable/correctable error status, masks, severity policy, first error pointer, ECRC generation/checking controls, multiple-header recording, header logs, and TLP prefix logs. These are integration-sensitive because the masks and severity bits determine which PCIe errors are reported, suppressed, or treated as fatal.

The link-training sections are highly repetitive and lane-oriented. PCIe 8 GT and 16 GT equalization blocks expose per-lane downstream/upstream transmit preset fields for lanes 0 through 15. The 16 GT PHY block also reports equalization completion and phase success, local/retimer parity mismatch vectors, modified TS usage, and lane margining capability/status/control fields for each lane.

The virtualization portion is split between standards-based SR-IOV and AMD-specific GPU-IOV VSEC registers. SR-IOV fields describe VF enablement, migration, VF counts, first VF offset, VF stride, VF device ID, system page size, VF BARs, and migration-state array offset. GPU-IOV fields describe hypervisor-facing mailbox words, interrupt status/enable bits, reset triggers, global/per-VF framebuffer allocation fields, peer-to-peer-over-XGMI enablement, and scheduling dwords for media and graphics engines.

The SWDS0 block has bridge/root-port style semantics. It combines conventional PCI command/status and decode-window fields with PM and PCIe capability fields for payload sizing, request sizing, relaxed ordering, no-snoop, error reporting, function-level reset, link speed/width, ASPM, exit latencies, clock power management, surprise-down reporting, data-link-active reporting, bandwidth notifications, and port number.

## Control Flow And State

There is no runtime control flow in this header. The effective flow is compile-time substitution:

1. NBIO 7.4-aware AMDGPU, display, or power-management code includes `nbio/nbio_7_4_sh_mask.h` with the matching NBIO 7.4 offset header.
2. Driver code selects a `cfgBIF_CFG_DEV0_EPF1_0_*` or `cfgBIF_CFG_DEV0_SWDS0_*` offset from `nbio_7_4_offset.h`.
3. These `__SHIFT` and `_MASK` macros are used by register helpers or open-coded bit operations to extract, insert, preserve, or compare fields.
4. Actual reads and writes happen through PCI config-space, MMIO, indirect register, or SMU/PSP integration code outside this header.

The header stores no software state and persists nothing by itself. Persistent state lives in NBIO/PCIe hardware registers. Some fields are configuration controls that survive until reset, function reset, power transition, link retrain, VF lifecycle change, or explicit reprogramming. Other fields are hardware-updated status, sticky error, mailbox, log, pending, or write-one-to-clear fields whose behavior is defined by the hardware and PCIe specifications.

## Dependencies And Integration Points

The direct generated-header dependency is `drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_offset.h`; every mask in this chunk must be paired with the same-generation offset macro. Source-tree include sites for NBIO 7.4 masks include `amdgpu/nbio_v7_4.c`, `pm/swsmu/smu11/arcturus_ppt.c`, `pm/swsmu/smu13/aldebaran_ppt.c`, `pm/swsmu/smu13/smu_v13_0_6_ppt.c`, and older PowerPlay Vega20 code. NBIO 7.4 offsets are also used by PSP and display DCN paths.

Semantic dependencies include the PCI and PCI Express configuration-space specifications, SR-IOV, ATS, PRI, PASID, ACS, MSI/MSI-X, AER, VC, multicast, LTR, DPA, TPH, Data Link Feature, 16 GT PHY/equalization, lane margining, and AMD's NBIO/GPU-IOV register definitions.

Because this is a generated header, most integration is indirect. Callers may use these macros through AMDGPU register helper macros, power-management feature code, debug/register dump paths, virtualization setup code, or firmware-facing SMU/PSP coordination paths. The macros do not encode access width, reset value, read/write permissions, side effects, sequencing, or W1C behavior; consumers must get those rules from the hardware programming guide and surrounding driver logic.

## Risks And Maintenance Notes

- The range starts and ends mid-context. It begins after part of `BIF_CFG_DEV0_EPF1_0_DEVICE_CAP2` and ends after `BIF_CFG_DEV0_SWDS0_LINK_CAP`, just before `BIF_CFG_DEV0_SWDS0_LINK_CNTL` continues in the next chunk.
- Repeated per-lane and per-VF blocks are easy to mis-review. Lane number, VF number, speed suffix, preset direction, and scheduler engine name are often the only visible differences across many consecutive definitions.
- Wrong shifts or masks can silently misprogram hardware: examples include AER severity, ACS isolation, SR-IOV VF counts/stride/BARs, GPU-IOV framebuffer allocation, MSI/MSI-X routing, or link equalization presets.
- Names like `*_MASK_MASK` are valid when the hardware field is itself named `MASK`; tooling or reviewers should not normalize them by hand.
- Full-width `0xFFFFFFFFL` masks often represent whole-register payloads, logs, mailbox words, serial-number halves, BAR capability bitmaps, or reserved fields. They should not be interpreted as permission to write all bits as ones.
- Status/log/pending fields may be sticky, hardware-updated, firmware-owned, or write-one-to-clear. Control fields can affect link state, virtualization isolation, interrupt routing, power behavior, address translation, and BAR decode.
- EPF1 and SWDS0 prefixes are not interchangeable. Each mask prefix must remain paired with the matching `cfgBIF_CFG_DEV0_EPF1_0_*` or `cfgBIF_CFG_DEV0_SWDS0_*` offset prefix.

## Test Signals

Useful validation signals for this chunk are:

- Build coverage for NBIO 7.4 include sites, especially `amdgpu/nbio_v7_4.c`, Arcturus/Aldebaran/SMU 13.0.6 power-management files, and Vega20 PowerPlay code.
- Cross-header checks that each register block represented here has a matching `cfgBIF_CFG_DEV0_EPF1_0_*` or `cfgBIF_CFG_DEV0_SWDS0_*` definition in `nbio_7_4_offset.h`.
- Generated-header comparison against AMD's authoritative NBIO 7.4 register database, with special attention to AER, ACS/ATS/PRI/PASID, SR-IOV, GPU-IOV VSEC, per-lane equalization, lane margining, and SWDS0 bridge windows.
- Static checks that field masks fit the intended 8/16/32-bit register widths and that every field with a `__SHIFT` has the expected generated `_MASK`.
- Hardware or simulator register dumps that decode the EPF1 capability chain and SWDS0 bridge config space consistently with `lspci -vvxxx`-style PCIe output.
- SR-IOV and GPU-IOV validation that VF count, BAR sizing, VF framebuffer allocation, interrupt/reset/mailbox, and scheduler fields decode correctly without cross-VF leakage.
- PCIe link-training tests on NBIO 7.4 hardware that exercise 8 GT and 16 GT equalization, parity mismatch reporting, margining control/status, and bandwidth/link-status reporting.
- Error-injection tests for AER and downstream isolation paths, checking status, masks, severity, header logs, TLP prefix logs, source behavior, and driver reporting.

### subset-b-003229: lines 7321-9744

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 7321-9744

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.4 shift/mask header. It defines C preprocessor constants for decoding and programming bitfields in NBIF/BIF PCI configuration-space registers. The macros are register-field geometry only; they do not implement Ceph or distributed-filesystem behavior despite the mirrored source path.

The inspected range contains 2,424 source lines, 280 commented register blocks, and 2,140 `#define` entries: 1,072 `__SHIFT` constants and 1,068 `_MASK` constants. The shift/mask imbalance is from chunk boundaries: the chunk starts after the `BIF_CFG_DEV0_SWDS0_LINK_CAP` shifts have already been defined in the previous chunk and ends before all masks for `BIF_CFG_DEV0_EPF0_VF1_0_PCIE_UNCORR_ERR_MASK` have appeared.

At a high level, this range covers:

- The tail of `BIF_CFG_DEV0_SWDS0_LINK_CAP`, then the rest of the `DEV0_SWDS0` PCIe switch/downstream-port capability map through lane margining.
- Complete visible PCI configuration images for `DEV0_EPF0_VF0_0` from vendor/device identity through ATS and ARI capability/control blocks.
- The beginning and most of the same shape for `DEV0_EPF0_VF1_0`, from vendor/device identity through the start of the Advanced Error Reporting uncorrectable-error mask block.

## Important APIs, Types, and Macros

There are no functions, structs, typedefs, or enums in this range. The only API surface is the generated register-field macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: zero-based bit position for a field.
- `<REGISTER>__<FIELD>_MASK`: field mask already shifted into register position.

The `DEV0_SWDS0` section describes a downstream/switch-style PCIe capability set. It includes standard link and slot controls/status, device capability/control 2, link capability/control/status 2, MSI message registers, subsystem ID capability, vendor-specific enhanced capability fields, virtual channel capability/control/status for VC0 and VC1, device serial number, Advanced Error Reporting, secondary PCIe capability, per-lane equalization, ACS, data-link feature capability, 16 GT/s PHY capability and status, and lane margining controls/status for lanes 0-15.

Important `DEV0_SWDS0` macro groups include:

- Link and slot management: `LINK_CNTL`, `LINK_STATUS`, `SLOT_CAP`, `SLOT_CNTL`, `SLOT_STATUS`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- PCIe 4.0/16 GT/s related fields: `PHY_16GT_ENH_CAP_LIST`, `LINK_CAP_16GT`, `LINK_CNTL_16GT`, `LINK_STATUS_16GT`, local and RTM parity mismatch status, and `LANE_n_EQUALIZATION_CNTL_16GT`.
- Error handling: `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, `PCIE_UNCORR_ERR_SEVERITY`, `PCIE_CORR_ERR_STATUS`, `PCIE_CORR_ERR_MASK`, `PCIE_ADV_ERR_CAP_CNTL`, header logs, and TLP prefix logs.
- Lane diagnostics: `PCIE_LANE_ERROR_STATUS`, `PCIE_LANE_n_EQUALIZATION_CNTL`, and `LANE_n_MARGINING_LANE_CNTL`/`STATUS` for lanes 0 through 15.
- Isolation and routing: ACS capability/control, data-link feature capability/status, virtual-channel resource capability/control/status, and vendor-specific enhanced capability registers.

The `DEV0_EPF0_VF0_0` and `DEV0_EPF0_VF1_0` blocks define virtual-function PCI configuration fields. Each has the standard PCI header identity and configuration registers: vendor/device ID, `COMMAND`, `STATUS`, revision and class-code fields, cache-line size, latency, header type, BIST, six base-address registers, adapter ID, ROM BAR, capability pointer, interrupt line/pin, PCIe capability list/header, device capability/control/status, link capability/control/status, device/link capability 2, MSI and MSI-X structures, vendor-specific enhanced capability, and AER status/logging fields.

`DEV0_EPF0_VF0_0` continues past AER into ATS and ARI:

- `PCIE_ATS_ENH_CAP_LIST`, `PCIE_ATS_CAP`, and `PCIE_ATS_CNTL` define address translation service metadata, invalidation queue depth, page-aligned request support, small translation unit, and ATS enable.
- `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL` define alternative routing-ID interpretation next-function, function-group, and MSI function-group controls.

`DEV0_EPF0_VF1_0` repeats the same standard VF layout visible in this chunk, but the range stops inside `PCIE_UNCORR_ERR_MASK`. Its later AER, ATS, and ARI definitions are expected in the next chunk.

## Control Flow and Runtime Behavior

This header has no runtime control flow. It is included at compile time and contributes constants to AMDGPU register access code. Runtime behavior is supplied by callers that combine these masks with matching register offsets and hardware access helpers.

The implied hardware flows are:

1. PCIe/NBIO initialization or enumeration reads identity, class-code, BAR, ROM BAR, capability pointer, interrupt, and PCIe capability fields for each exposed function.
2. Driver or firmware setup programs command enables, device control, link control, link speed targets, MSI/MSI-X controls, ACS, ATS, ARI, virtual-channel policy, and lane diagnostic controls using these masks.
3. Link bring-up and diagnostics inspect current speed/width, link training, data-link-layer active state, equalization completion, lane errors, 16 GT/s equalization, parity mismatch, and margining results.
4. PCIe error handling reads AER status, applies mask/severity policy, and decodes header/TLP-prefix logs for the selected downstream port or virtual function.
5. Virtualization paths use the VF-prefixed blocks to decode per-VF PCI configuration images and to program ATS/ARI behavior where available.

The file itself does not read or write registers, clear status bits, enforce ordering between hardware operations, or validate field values. Those semantics belong to AMDGPU's NBIO/PCIe code and the NBIO 7.4 hardware specification.

## State and Persistence

The header owns no mutable state, allocates no memory, persists nothing, and performs no I/O. The represented state lives in NBIO/BIF PCI configuration-space registers.

State categories represented by this chunk include:

- PCIe link and slot state: ASPM controls, link disable/retrain, common clock, current link speed, negotiated width, data-link-layer active state, bandwidth-management notifications, slot hotplug/presence/power bits, and link capability 2 fields.
- PCIe device policy: completion timeout, atomic operation controls, ID-based ordering, LTR, OBFF, ten-bit tags, end-to-end TLP prefix controls, and virtual-channel resource assignments.
- Interrupt state: MSI capability, message control, 32/64-bit address/data, masks, pending bits, MSI-X table/PBA offset and BIR fields.
- Error-observation and error-policy state: AER uncorrectable/correctable status, masks, severity, ECRC controls, first-error pointer, multiple-header-recording controls, header logs, TLP prefix logs, and lane error status.
- Link-training diagnostics: equalization controls for lanes 0-15, 16 GT/s lane equalization coefficients, parity mismatch status, and lane margining command/status fields.
- Virtual-function configuration state: VF0/VF1 standard PCI header fields, BARs, ROM BAR, capability chain, PCIe device/link controls, AER, vendor-specific scratch fields, ATS controls, and ARI controls.

Persistence across GPU reset, PCI reset, FLR, suspend/resume, BACO, or runtime power transitions is not described by this header. A wrong macro value is persistent in the compiled driver until the generated header is corrected and the driver is rebuilt.

## Dependencies and Integration Points

The direct companion in this directory is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_offset.h`, which supplies the register address/offset side of the same NBIO 7.4 register map. `nbio_7_4_0_smn.h` is also present for SMN-level register definitions, while this file provides field shifts and masks for register values.

Likely AMDGPU integration areas include:

- NBIO 7.4 ASIC initialization and low-level register read/modify/write paths that include generated ASIC register headers.
- PCIe link management code that programs ASPM, retraining, target speed, bandwidth notifications, equalization, and 16 GT/s training fields.
- AER and RAS diagnostic paths that classify correctable and uncorrectable PCIe errors and decode logged TLP headers/prefixes.
- Interrupt setup for MSI and MSI-X message/control/table/PBA fields.
- Virtualization paths that expose or manage `EPF0_VF0_0` and `EPF0_VF1_0` PCI configuration images, including ATS and ARI where present.
- Isolation and routing setup that depends on ACS, virtual channels, ATS, and ARI fields.
- Manufacturing, bring-up, or debug paths that use lane equalization, parity mismatch, lane error, and margining registers.

Integration is primarily by exact symbol naming. The repeated VF0/VF1 register layouts are intentionally similar, but the prefix selects a different hardware function image.

## Risks

- Chunk boundaries split register definitions. This range starts with only the masks for the tail of `BIF_CFG_DEV0_SWDS0_LINK_CAP` and ends before all masks for `BIF_CFG_DEV0_EPF0_VF1_0_PCIE_UNCORR_ERR_MASK`; pair-completeness checks must run after adjacent chunks are merged.
- Repeated layouts are easy to cross-wire. Using a `VF0_0` macro while accessing a `VF1_0` offset, or using a `SWDS0` macro for a VF register, can silently decode the wrong register image.
- AER status, mask, and severity blocks have nearly identical field names. Confusing them can suppress errors, misclassify severity, or damage diagnostics.
- Link-control fields can affect enumeration and stability. Incorrect masks for retrain, link disable, target speed, autonomous speed/width disable, ASPM, equalization, or 16 GT/s fields can cause link bring-up failures or performance regressions.
- MSI/MSI-X address, data, mask, pending, table, and PBA fields are security- and reliability-sensitive. Incorrect extraction can route interrupts through the wrong BAR, vector, or mask state.
- ACS, ATS, ARI, and virtual-channel fields affect isolation and routing. Bad masks can undermine DMA isolation, break IOMMU/ATS behavior, or misroute PCIe functions.
- Lane margining and equalization registers are dense and repeated across 16 lanes. Off-by-one lane macro use can make diagnostics or tuning target the wrong lane.
- Full-dword log and scratch fields look simple, but the endpoint prefix still matters. Decoding the wrong function's header/TLP-prefix log can misattribute a PCIe fault.
- Generated `L`-suffixed masks should be used with normal unsigned register-width handling to avoid width/sign surprises when composing values.

## Test and Validation Signals

Useful validation signals for this chunk are mostly generated-header consistency checks plus hardware or emulator coverage:

- Build AMDGPU configurations that include `nbio_7_4_sh_mask.h` to catch malformed macro names, duplicate definitions, and compile-time include issues.
- After adjacent chunks are merged, verify every field has a matching `__SHIFT` and `_MASK` pair. Expected local exceptions are the starting `SWDS0_LINK_CAP` masks and the ending partial `VF1_0_PCIE_UNCORR_ERR_MASK` block.
- Cross-check register names in this range against `nbio_7_4_offset.h` so field macros have matching address macros where expected.
- Run mechanical symmetry checks across `DEV0_EPF0_VF0_0` and `DEV0_EPF0_VF1_0` for the common PCI header, PCIe, MSI/MSI-X, vendor-specific, and AER fields that are both visible in this chunk.
- Decode PCI configuration-space dumps from NBIO 7.4 hardware for `DEV0_SWDS0`, `DEV0_EPF0_VF0_0`, and `DEV0_EPF0_VF1_0`, comparing link, slot, MSI/MSI-X, AER, ATS, and ARI fields with expected capability chains.
- Exercise PCIe AER paths with controlled correctable and uncorrectable errors, then confirm status, mask, severity, first-error pointer, header log, and TLP-prefix log decoding.
- Validate MSI/MSI-X setup by checking message control, 64-bit address/data, vector masks, pending bits, table offset/BIR, and PBA offset/BIR for VF0 and VF1.
- Exercise link training and recovery paths across supported speeds, including 16 GT/s equalization where hardware supports it, and confirm link status, lane error, parity mismatch, and equalization result decoding.
- Validate ACS/ATS/ARI behavior under virtualization and IOMMU-enabled configurations, confirming function routing, DMA isolation, ATS enablement, and VF enumeration.
- Use lane margining diagnostics on hardware or simulation to confirm lane-numbered control/status macros map to the expected physical/logical lanes.

## Chunk Boundary Notes

Lines 7321-7322 are the final masks for `BIF_CFG_DEV0_SWDS0_LINK_CAP`; the matching shifts and earlier masks are in the previous chunk. Lines 7323-8554 cover the rest of the visible `DEV0_SWDS0` downstream-port/switch register definitions from `LINK_CNTL` through lane 15 margining status.

Lines 8555-9238 cover the `nbio_nbif0_bif_cfg_dev0_epf0_vf0_bifcfgdecp` address block for `DEV0_EPF0_VF0_0`, from `VENDOR_ID` through ARI control. Lines 9239-9744 begin the `nbio_nbif0_bif_cfg_dev0_epf0_vf1_bifcfgdecp` block for `DEV0_EPF0_VF1_0`, from `VENDOR_ID` through the first masks of `PCIE_UNCORR_ERR_MASK`. The next chunk is required for the rest of the VF1 AER mask block and later VF1 registers.

### subset-b-003230: lines 9745-12178

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 9745-12178

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.4 register shift/mask header. It defines preprocessor constants for bitfield extraction and composition in NBIF/BIF PCI configuration-space registers exposed by NBIO. The file is a hardware register contract: it contains no executable logic, but downstream AMDGPU code depends on these names, shifts, and masks matching the ASIC register map exactly.

The requested range contains 2,434 source lines and 2,138 `#define` entries. Of those definitions, 1,070 are `__SHIFT` constants and 1,068 are `_MASK` constants. The slight imbalance comes from chunk boundaries: the range starts partway through `BIF_CFG_DEV0_EPF0_VF1_0_PCIE_UNCORR_ERR_MASK`, after some earlier shifts were defined in the previous chunk, and ends partway through `BIF_CFG_DEV0_EPF0_VF5_0_LINK_CAP`, before the matching masks appear in the next chunk.

At a high level, the chunk covers:

- The tail of virtual function 1 (`BIF_CFG_DEV0_EPF0_VF1_0`) PCIe AER, TLP logging, ATS, and ARI field definitions.
- Complete visible register-field layouts for `VF2_0`, `VF3_0`, and `VF4_0` under `nbio_nbif0_bif_cfg_dev0_epf0_vf*_bifcfgdecp`.
- The beginning of `VF5_0`, from standard PCI identity/header fields through PCIe device control/status and the first `LINK_CAP` shifts.

Despite the repository path containing `ceph-client`, this source is AMD GPU driver register metadata. It does not implement distributed filesystem behavior.

## Important APIs, Types, and Macros

There are no functions, structs, typedefs, or enums in this range. The public interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: zero-based starting bit for a field.
- `<REGISTER>__<FIELD>_MASK`: field mask already shifted into register position.

The most important macro groups are organized by PCIe virtual function.

The `VF1_0` tail continues from the previous chunk and includes:

- `PCIE_UNCORR_ERR_MASK`: remaining uncorrectable-error mask shifts plus masks for data link protocol, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast-blocked TLP, AtomicOp egress blocked, and TLP prefix blocked errors.
- `PCIE_UNCORR_ERR_SEVERITY`: severity classification fields for the same uncorrectable PCIe error sources.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK`: corrected-error observation and masking for receiver error, bad TLP, bad DLLP, replay counter rollover, replay timeout, advisory nonfatal error, corrected internal error, and header-log overflow.
- `PCIE_ADV_ERR_CAP_CNTL`: first-error pointer, ECRC generation/check capability and enable bits, multi-header-recording capability and enable bits, TLP prefix log presence, and completion-timeout logging capability.
- `PCIE_HDR_LOG0` through `PCIE_HDR_LOG3` and `PCIE_TLP_PREFIX_LOG0` through `PCIE_TLP_PREFIX_LOG3`: full-dword AER diagnostic log fields.
- `PCIE_ATS_*`: ATS enhanced capability list, invalidate queue depth, page-aligned request, global invalidate support, STU, and ATC enable fields.
- `PCIE_ARI_*`: ARI enhanced capability, next-function number, MFVC/ACS function-group support, enable bits, and function group selector.

The `VF2_0`, `VF3_0`, and `VF4_0` sections repeat a complete PCI/PCIe virtual-function configuration shape. Each block includes standard PCI header and capability fields:

- Identity and header fields: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE`, `LATENCY`, `HEADER`, and `BIST`.
- Resource fields: `BASE_ADDR_1` through `BASE_ADDR_6`, `ADAPTER_ID`, `ROM_BASE_ADDR`, `CAP_PTR`, `INTERRUPT_LINE`, and `INTERRUPT_PIN`.
- PCIe capability fields: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`, `SLOT_CAP2`, `SLOT_CNTL2`, and `SLOT_STATUS2`.
- MSI and MSI-X fields: capability list pointers, message control, 32-bit and 64-bit message address/data fields, mask and pending fields, MSI-X table BIR/offset, and MSI-X PBA BIR/offset.
- Vendor-specific extended capability fields: enhanced capability list header, vendor-specific header, and two scratch payload dwords.
- AER fields: enhanced capability header, uncorrectable status/mask/severity, correctable status/mask, advanced error capability/control, header logs, and TLP prefix logs.
- ATS and ARI fields: enhanced capability headers plus control/capability fields for address translation services and alternative routing-ID interpretation.

The `VF5_0` portion begins at line 11975 and is incomplete within this chunk. It defines `VF5_0` identity, standard PCI command/status, class/header/BIST, BARs, subsystem adapter ID, ROM base, capability pointer, interrupt line/pin, PCIe capability header, device capability/control/status, and the start of `LINK_CAP` shifts through `DL_ACTIVE_REPORTING_CAPABLE`. The remaining `LINK_CAP` shifts and masks continue after line 12178.

## Control Flow and Runtime Behavior

This header has no runtime control flow. It is consumed at compile time by AMDGPU and power-management code that reads or writes NBIO registers with generated address constants from the companion offset header and field helpers such as `REG_SET_FIELD` or equivalent mask/shift operations.

The implied runtime flow in consumers is:

1. Select the NBIO/BIF config register address for a virtual function using the matching offset header.
2. Read the register through an AMDGPU MMIO, SMN, or PCIe-port access helper.
3. Decode a field with the generated `_MASK` and `__SHIFT`, or compose a new register value by clearing the mask and inserting a shifted field value.
4. Write the modified value back when the field is writable, or use the decoded value for diagnostics, link state, interrupt setup, or virtualization policy.

Hardware behavior represented by these fields includes PCI enumeration, BAR/resource reporting, bus-master and memory-space enablement, interrupt masking, MSI/MSI-X programming, PCIe link capability/control/status, AER policy and diagnostic capture, ATS translation enablement, and ARI function routing.

The header does not encode access permissions, reset values, write-one-to-clear behavior, timing requirements, or side effects. For example, AER status bits and PCIe device status bits may be sticky or clear-on-write in hardware, while capability bits are generally read-only. Callers must use the hardware specification and existing driver sequencing.

## State and Persistence

The file owns no state, allocates no memory, and persists nothing. It describes hardware register state that exists in NBIO/BIF PCI configuration-space images for SR-IOV-like virtual functions.

State represented by this chunk includes:

- Enumeration and identity state: vendor/device IDs, revision and class codes, header type, BIST, capability pointer, interrupt line/pin, subsystem IDs, ROM base, and BAR encodings.
- Control policy state: PCI command enables, parity/SERR/interrupt-disable settings, PCIe error-report enables, relaxed ordering, no-snoop, maximum payload size, maximum read request size, extended tags, phantom functions, function-level reset initiation, ASPM/link controls, completion-timeout policy, and link disable/retrain controls.
- Interrupt state: MSI enablement, multi-message capability/enable fields, 64-bit addressing, per-vector masking, pending bits, MSI-X enable/function mask, table offsets/BIRs, and PBA offsets/BIRs.
- Error state and policy: AER uncorrectable/correctable status bits, error masks, severity classification, first-error pointer, ECRC controls, header-log overflow, and captured TLP header/prefix logs.
- Translation and routing state: ATS invalidate queue depth, ATC enable/STU, ARI next-function information, and ARI function-group controls.
- Link state: advertised speed/width, power-management support, exit latencies, surprise-down reporting, data-link active reporting, current negotiated speed/width, link training, slot clock configuration, link bandwidth status, target speed, equalization status, de-emphasis, and autonomous speed/width controls.

Persistence of these hardware fields across reset, FLR, suspend/resume, runtime power transitions, or BACO is not defined by this header. A wrong macro value, however, persists in the compiled driver until the generated header is regenerated or fixed and the driver is rebuilt.

## Dependencies and Integration Points

The direct companion headers in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_offset.h`, which supplies the register address/offset constants corresponding to these field definitions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_0_smn.h`, which supplies NBIO 7.4 SMN-level register definitions used by some NBIO code.

Files in this tree that include `nbio_7_4_sh_mask.h` include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_inc.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_hwmgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/arcturus_ppt.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/aldebaran_ppt.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_6_ppt.c`

Several display and PSP files include the NBIO 7.4 offset header without this shift/mask header, so they may use raw offsets or different field definitions for their limited needs. The main low-level integration point for the full mask namespace is `amdgpu/nbio_v7_4.c`, while power-management code uses the same generated register contract for ASIC-specific setup and telemetry paths.

The macros in this chunk are tightly coupled to exact symbol names. `BIF_CFG_DEV0_EPF0_VF2_0_*`, `VF3_0_*`, `VF4_0_*`, and `VF5_0_*` describe different virtual-function configuration images even when the field layout is mechanically identical. A consumer must pair the correct function-prefixed mask with the matching function-prefixed offset.

## Risks and Edge Cases

- The chunk starts and ends inside register definitions. `VF1_0_PCIE_UNCORR_ERR_MASK` is missing some earlier shifts from the previous chunk, and `VF5_0_LINK_CAP` is missing its later shifts and all masks in this chunk. Pair-completeness checks must be done after adjacent chunks are merged.
- Generated names such as `PCIE_UNCORR_ERR_MASK__DLP_ERR_MASK_MASK` are easy to misread. The first `MASK` is part of the hardware register/field name and the final `_MASK` is the generated macro suffix.
- Repeated VF layouts create cross-function hazards. A `VF2_0` mask may have the same numeric value as a `VF3_0` mask, but using it with the wrong offset hides the fact that code is accessing the wrong virtual function.
- PCI command and device-control fields affect memory decoding, bus mastering, parity/SERR response, interrupt disable, relaxed ordering, no-snoop, FLR, maximum payload, and maximum read request size. Incorrect masks can break enumeration, DMA, interrupts, or PCIe transaction sizing.
- AER status/mask/severity fields have similar names but different semantics. Confusing status with mask or severity can suppress errors, misclassify fatal/nonfatal events, or lose diagnostic context.
- Header and TLP prefix logs are full-dword fields. They look simple, but decoding the wrong VF's log can send debugging toward the wrong function or transaction.
- MSI/MSI-X offset and BIR fields are packed into the same registers. Bad extraction can point interrupt setup at the wrong BAR aperture or table.
- ATS and ARI controls affect address translation, invalidation behavior, function routing, and virtualization isolation. Incorrect field definitions or wrong-function usage can cause IOMMU/PASID integration failures or routing bugs.
- Link capability/control/status bits are timing-sensitive when used for retrain, target speed, ASPM, and link status polling. The existence of a mask does not mean the driver may freely write the field.
- The macros use C integer literals with `L` suffixes and mixed logical widths (`0xFFL`, `0xFFFFL`, `0xFFFFFFFFL`). Consumers should preserve unsigned register-width handling when composing 32-bit values.

## Test and Validation Signals

Useful validation for this chunk is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU configurations that include NBIO 7.4 headers and the known consumers listed above. This catches malformed macro names, duplicate definitions, and missing symbols used by driver code.
- After merging adjacent chunks, mechanically verify every field has a matching `__SHIFT` and `_MASK` pair. Expected local boundary exceptions are the partial `VF1_0_PCIE_UNCORR_ERR_MASK` at the start and partial `VF5_0_LINK_CAP` at the end.
- Cross-check every `BIF_CFG_DEV0_EPF0_VF[2-5]_0_*` register name in this range against `nbio_7_4_offset.h` so field macros have corresponding address definitions where expected.
- Run symmetry checks across `VF2_0`, `VF3_0`, and `VF4_0`; their common standard PCI, PCIe, MSI/MSI-X, vendor-specific, AER, ATS, and ARI field layouts should match unless the generated register database intentionally differs.
- Validate PCI configuration-space dumps on NBIO 7.4 hardware by decoding VF2/VF3/VF4 and the visible VF5 fields with these masks and comparing identity, BAR, capability-list, MSI/MSI-X, link, AER, ATS, and ARI values against expected hardware documentation.
- Exercise MSI and MSI-X interrupt setup, including masking and pending-bit behavior, for virtual functions whose config images are represented here.
- Exercise PCIe error handling with controlled correctable and uncorrectable errors and confirm decoded status, mask, severity, first-error pointer, header log, and TLP prefix log fields.
- Validate link-management paths by checking reported current speed/width, negotiated width, link-training status, data-link-layer active, bandwidth status, ASPM controls, target link speed, and equalization-related fields where present.
- Validate virtualization and IOMMU paths involving ATS and ARI, including ATC enable/STU programming, invalidate queue-depth interpretation, next-function number decoding, and ARI function-group controls.
- Run suspend/resume, FLR, hot reset, and GPU reset coverage to ensure policy fields are restored by driver code and status fields still decode correctly after reset-domain transitions.

## Chunk Boundary Notes

The range begins at line 9745 inside `BIF_CFG_DEV0_EPF0_VF1_0_PCIE_UNCORR_ERR_MASK`, starting with `UNEXP_CPL_MASK__SHIFT`. The earlier uncorrectable-error mask shifts are in the previous work item, while this range includes all masks for that register and then continues through the rest of the visible `VF1_0` AER/ATS/ARI tail.

Lines 9923, 10607, and 11291 introduce complete address blocks for `VF2_0`, `VF3_0`, and `VF4_0`. Each full block runs from standard PCI identity fields through ARI control fields.

Line 11975 introduces `nbio_nbif0_bif_cfg_dev0_epf0_vf5_bifcfgdecp`. The range covers `VF5_0_VENDOR_ID` through the first part of `VF5_0_LINK_CAP`, ending at line 12178 with `DL_ACTIVE_REPORTING_CAPABLE__SHIFT`. The remaining `VF5_0_LINK_CAP` shifts, all `LINK_CAP` masks, and later `VF5_0` fields belong to the next chunk.

### subset-b-003231: lines 12179-14599

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 12179-14599

## Scope And Purpose

This chunk is part of AMDGPU's generated NBIO 7.4 register bitfield header. It contains C preprocessor definitions for shift positions and masks used to encode and decode PCI/PCIe configuration-space registers in the NBIO BIF configuration decoder. The visible range starts in the middle of virtual function 5 (`BIF_CFG_DEV0_EPF0_VF5_0`) PCIe link/capability definitions, covers all of virtual functions 6 and 7, and reaches the beginning-to-middle of virtual function 8, ending inside `BIF_CFG_DEV0_EPF0_VF8_0_PCIE_CORR_ERR_STATUS`.

The source is declarative register metadata, not executable logic. Its purpose is to give AMDGPU NBIO, power-management, and hardware-access code stable symbolic names for bit extraction and field composition. Register addresses are defined separately in the paired `nbio_7_4_offset.h`; this file supplies the field-level `__SHIFT` and `_MASK` constants for those address macros.

Within lines 12179-14599 there are 2141 `#define` entries: 1070 shift macros and 1071 mask macros. The one-count difference comes from the chunk boundary starting after the comment for `VF5_0_LINK_CAP` and including some masks for fields whose shifts were defined before line 12179.

## Register Blocks Covered

The chunk follows generated address-block structure:

- Lines 12179-12655: tail of `nbio_nbif0_bif_cfg_dev0_epf0_vf5_bifcfgdecp`, from `VF5_0_LINK_CAP` masks through PCIe ARI control.
- Lines 12659-13339: full `nbio_nbif0_bif_cfg_dev0_epf0_vf6_bifcfgdecp`.
- Lines 13343-14023: full `nbio_nbif0_bif_cfg_dev0_epf0_vf7_bifcfgdecp`.
- Lines 14027-14599: start of `nbio_nbif0_bif_cfg_dev0_epf0_vf8_bifcfgdecp`, from standard PCI config header fields through part of PCIe advanced error reporting.

VF6 and VF7 have the complete repeated register layout in this chunk: vendor/device identity, PCI command and status, class/revision/header/BIST fields, BARs, subsystem IDs, ROM base, capability pointer, interrupt line/pin, PCIe capability, device/link capability and control/status registers, MSI/MSI-X capability registers, vendor-specific enhanced capability registers, Advanced Error Reporting registers, header/TLP-prefix logs, ATS capability/control, and ARI capability/control. VF8 follows the same layout but this chunk ends before its AER corrected-error block is complete.

## Important Macros And Field Families

The macros use the generated naming form:

- `BIF_CFG_DEV0_EPF0_VF<N>_0_<REGISTER>__<FIELD>__SHIFT`
- `BIF_CFG_DEV0_EPF0_VF<N>_0_<REGISTER>__<FIELD>_MASK`

Important field groups in this chunk include:

- Standard PCI command/status controls: `IO_ACCESS_EN`, `MEM_ACCESS_EN`, `BUS_MASTER_EN`, `PARITY_ERROR_RESPONSE`, `SERR_EN`, `INT_DIS`, status error bits, `CAP_LIST`, and device timing/status indicators.
- PCI identity and header fields: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE_SIZE`, `LATENCY_TIMER`, `HEADER_TYPE`, `DEVICE_TYPE`, and BIST fields.
- BAR and adapter registers: `BASE_ADDR_1` through `BASE_ADDR_6`, `SUBSYSTEM_VENDOR_ID`, `SUBSYSTEM_ID`, and `ROM_BASE_ADDR`.
- PCIe capability registers: `VERSION`, `DEVICE_TYPE`, `SLOT_IMPLEMENTED`, `INT_MESSAGE_NUM`, device capability/control/status, link capability/control/status, and PCIe 2.0 capability/control/status.
- Link management fields: `LINK_SPEED`, `LINK_WIDTH`, `PM_SUPPORT`, `L0S_EXIT_LATENCY`, `L1_EXIT_LATENCY`, `CLOCK_POWER_MANAGEMENT`, surprise-down reporting, data-link active reporting, bandwidth notification, target link speed, compliance controls, equalization status, de-emphasis, and downstream component presence.
- Interrupt capability fields: MSI capability list and message control, message address/data, mask and pending registers, 64-bit MSI variants, MSI-X table/PBA BIR and offset, table size, function mask, and enable bit.
- Vendor-specific enhanced capability fields: VSEC list header fields, VSEC ID/revision/length, and two scratch registers.
- Advanced Error Reporting fields: uncorrectable error status/mask/severity bits for DLP, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic-op egress blocked, and TLP-prefix blocked conditions.
- Correctable error fields: receiver error, bad TLP, bad DLLP, replay rollover, replay timeout, advisory non-fatal, correctable internal error, and header-log overflow. The VF8 corrected-error status masks continue beyond the chunk.
- Error log fields: four `PCIE_HDR_LOG*` 32-bit TLP header words and four `PCIE_TLP_PREFIX_LOG*` 32-bit prefix words.
- ATS/ARI virtualization fields: ATS capability/control fields such as invalidate queue depth, page-aligned request, global invalidate support, STU, and ATC enable; ARI capability/control fields such as MFVC/ACS function group support, next function number, enable bits, and function group selection.

## Control Flow

There is no runtime control flow in this header. All behavior is compile-time substitution by the C preprocessor. Downstream code includes this header, reads or writes MMIO/config-space registers using address macros from `nbio_7_4_offset.h`, then applies these masks and shifts to isolate or construct field values.

The implicit data flow for consumers is:

1. Select a register address such as `cfgBIF_CFG_DEV0_EPF0_VF6_0_LINK_CNTL2` from `nbio_7_4_offset.h`.
2. Read the hardware register through the AMDGPU register-access helpers, or prepare a register value for writing.
3. Use this header's `...__FIELD_MASK` and `...__FIELD__SHIFT` macros to test, extract, clear, or set the target bitfield.
4. Write updated control values back to hardware only when the register is writable and the operation is valid for the active virtual function.

Because these are raw bit definitions, the header does not enforce read-only, write-1-to-clear, sticky status, reset, or side-effect semantics. Those semantics must be honored by the calling driver code and the hardware specification.

## State And Persistence Behavior

This chunk does not allocate memory or persist software state. The persistent state represented by these definitions is hardware state in PCI/PCIe configuration registers for SR-IOV-style virtual functions. Fields such as command enables, bus mastering, MSI/MSI-X enable/mask state, link control, AER masks/severity settings, ATS enable, and ARI control can affect hardware behavior until reset or reprogramming. Fields such as status, link status, AER status, header logs, TLP-prefix logs, MSI pending bits, and corrected/uncorrected error reports reflect hardware-observed state and may be sticky depending on register semantics outside this header.

The repeated VF5/VF6/VF7/VF8 naming is significant: each virtual function exposes the same PCIe register layout, but each macro is namespaced to one function. This reduces accidental cross-function field use when paired with matching per-VF offset macros.

## Dependencies And Integration Points

The header guard `_nbio_7_4_SH_MASK_HEADER` makes the file safe for repeated inclusion. The file is included by `drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c` and several power-management paths, including Arcturus, Aldebaran, SMU 13.0.6, and Vega20 code. Those consumers use NBIO 7.4 register names to configure or inspect GPU PCIe/NBIO behavior.

Important adjacent generated files are:

- `nbio_7_4_offset.h`, which defines the corresponding register offsets, for example `cfgBIF_CFG_DEV0_EPF0_VF6_0_*`, `VF7`, and `VF8` addresses.
- `nbio_7_4_default.h`, which records reset/default values for many of the same registers.
- Other ASIC NBIO headers such as `nbio_6_1_*`, `nbio_2_3_*`, and `nbio_4_3_0_*`, which expose similar generated fields for different hardware IP versions or address encodings.

These macros integrate with the AMDGPU register access conventions and common bitfield helpers such as masking, shifting, `REG_GET_FIELD`-style extraction, and read/modify/write operations. The exact helper use is in C implementation files, not in this header.

## Risks And Edge Cases

The main risk is metadata drift from the hardware register specification. A wrong shift or mask can silently decode the wrong status bit or program the wrong control bit, which is especially risky for PCIe link training, bus mastering, MSI/MSI-X, AER severity/masking, ATS, and ARI controls.

Chunk-boundary risk is present here. The range begins after some `VF5_0_LINK_CAP` shift definitions and ends before the full `VF8_0_PCIE_CORR_ERR_STATUS` block is complete, so the eventual per-file merge must reconcile this report with neighboring chunks before treating VF5 and VF8 coverage as complete.

The names contain repeated words such as `..._MASK__..._MASK` for mask-register fields. This is expected generated style: the first `MASK` is part of the hardware register or field name, while the final `_MASK` suffix denotes the bitmask macro. Reviewers should not "simplify" these names manually because downstream generated code and register documentation rely on exact spellings.

Many masks are 16-bit or 32-bit constants with an `L` suffix. Callers should take care with integer width, sign extension, and casts when combining these with 64-bit register addresses from other NBIO generations. The mask constants describe field width, not register address width.

Read/write semantics are not visible in this file. Status fields, AER log fields, MSI pending bits, and link status fields may require write-1-to-clear, polling, or hardware sequencing rules defined elsewhere. Using only these masks without consulting register semantics can cause missed errors, uncleared sticky bits, or disruptive link/control changes.

## Test Signals

There are no unit tests for this header in the chunk itself. Practical validation signals are mostly compile-time and hardware/integration oriented:

- The kernel build should compile all consumers including `nbio_v7_4.c` and PM files that include `nbio_7_4_sh_mask.h`.
- Generated offset, default, and mask headers should stay internally consistent: every field mask should match the intended register width and every register family should align with the paired `cfgBIF_CFG_DEV0_EPF0_VF<N>_0_*` offset definitions.
- Static checks can verify paired `__SHIFT` and `_MASK` macros for each field, expected repeated layouts across VF6 and VF7, and expected continuation into VF8 in later chunks.
- Runtime smoke tests on NBIO 7.4 ASICs should cover PCIe link status decoding, bus-master/memory access programming, MSI/MSI-X enable paths, AER status reporting/masking, and SR-IOV virtual-function enumeration where applicable.
- Regression signals include incorrect PCI config values in debug dumps, AER errors being misclassified or not masked, virtual functions failing enumeration, MSI/MSI-X interrupts not enabling, ATS/ARI capability negotiation failures, and link speed/width reporting mismatches.

## Cross-Chunk Notes

This chunk is not a standalone final file report. The merge lane should combine it with earlier and later chunks for the full `nbio_7_4_sh_mask.h` analysis. Neighboring chunks are needed to cover the start of VF5 and the remainder of VF8 plus subsequent virtual-function/register families.

### subset-b-003232: lines 14600-17033

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 14600-17033

## Scope

This chunk is a generated AMDGPU NBIO 7.4 shift/mask header slice for PCIe configuration-space fields. It starts inside the `BIF_CFG_DEV0_EPF0_VF8_0_PCIE_CORR_ERR_STATUS` definitions, completes the tail of the `VF8` PCIe advanced-error, ATS, and ARI capability masks, then covers complete PCI configuration images for `BIF_CFG_DEV0_EPF0_VF9_0`, `BIF_CFG_DEV0_EPF0_VF10_0`, and `BIF_CFG_DEV0_EPF0_VF11_0`. It ends inside the `BIF_CFG_DEV0_EPF0_VF12_0_DEVICE_CAP2` shift definitions after covering the conventional header, PCIe capability, and link control/status fields for `VF12`.

The file is not executable logic. It is a hardware layout contract: paired `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros define how AMDGPU code decodes or composes register values after selecting the matching address from `nbio_7_4_offset.h`.

## Purpose

`nbio_7_4_sh_mask.h` describes bit positions for NBIO 7.4 registers. This chunk focuses on SR-IOV-style endpoint virtual-function PCIe config blocks under `DEV0_EPF0`, specifically virtual functions 8 through 12. These fields mirror standard PCI/PCIe capability layouts and AMD/vendor-specific enhanced capability space for each VF.

The macros support code that needs to:

- decode PCI identity, command, status, class, header, BAR, interrupt, and capability-pointer fields;
- program or inspect PCIe Device/Link Capability, Control, and Status registers;
- configure or diagnose MSI and MSI-X capability registers for VFs 9-11;
- decode Advanced Error Reporting status, masks, severity, header logs, and TLP prefix logs;
- inspect or control ATS and ARI enhanced capabilities.

The source path matters because these definitions are ASIC-generation-specific. A field name that is correct for `nbio_7_4_sh_mask.h` must be paired with the corresponding NBIO 7.4 offset/base definitions and not with a similar register from another NBIO generation.

## Major Register Groups

The chunk opens with the tail of `BIF_CFG_DEV0_EPF0_VF8_0`. The covered VF8 registers are PCIe AER correctable error status/mask, AER capability/control, four TLP header log DWORDs, four TLP prefix log DWORDs, ATS enhanced capability list/capability/control, and ARI enhanced capability list/capability/control. Important VF8 fields include receiver, bad TLP, bad DLLP, replay rollover, replay timeout, advisory nonfatal, internal correctable, header-log-overflow status/mask bits, ECRC generation/check enable bits, ATS `STU` and `ATC_ENABLE`, and ARI function-group controls.

`BIF_CFG_DEV0_EPF0_VF9_0`, `VF10_0`, and `VF11_0` each receive a complete repeated PCIe VF config-layout block in this range. Each block includes:

- Conventional PCI header fields: vendor ID, device ID, command, status, revision ID, programming interface, subclass, base class, cache line size, latency timer, header type, BIST, six BARs, subsystem vendor/device ID, ROM base address, capability pointer, interrupt line, and interrupt pin.
- PCIe capability fields: capability list ID/next pointer, PCIe capability version/device type/slot/interrupt metadata, Device Capability, Device Control, Device Status, Link Capability, Link Control, Link Status, Device Capability 2, Device Control 2, Device Status 2, Link Capability 2, Link Control 2, Link Status 2, and second-generation slot registers.
- Interrupt capabilities: MSI capability list/control, MSI message address/data, 32-bit and 64-bit mask/pending layouts, MSI-X capability list/control, MSI-X table offset/BIR, and MSI-X PBA offset/BIR.
- Vendor-specific enhanced capability registers: enhanced capability list header, vendor-specific header, and two vendor-specific payload registers.
- PCIe Advanced Error Reporting registers: AER enhanced capability list, uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, TLP header logs, and TLP prefix logs.
- ATS and ARI enhanced capability registers: capability IDs/versions/next pointers, ATS invalidate queue depth, page-aligned request and global invalidate support, ATS control `STU` and `ATC_ENABLE`, ARI multi-function/ACS function group support, next-function number, enable bits, and function-group selection.

The `VF12_0` portion begins at its address-block marker and covers the same conventional PCI header and first PCIe capability sections through the start of Device Capability 2. It includes Device/Link Capability, Control, and Status, then the `DEVICE_CAP2` shift fields through `MAX_END_END_TLP_PREFIXES`. The chunk boundary stops before the matching `VF12_0_DEVICE_CAP2` mask fields and before later VF12 MSI, AER, ATS, and ARI groups.

## Important APIs, Types, And Functions

There are no functions, structs, enums, or runtime APIs in this range. The important public surface is the macro naming convention:

- `BIF_CFG_DEV0_EPF0_VF<N>_0_<REGISTER>__<FIELD>__SHIFT` gives the zero-based bit position.
- `BIF_CFG_DEV0_EPF0_VF<N>_0_<REGISTER>__<FIELD>_MASK` gives the field mask in the logical register value.

Consumers typically combine these masks with AMDGPU register helpers such as `REG_GET_FIELD` and `REG_SET_FIELD`, or with explicit mask/shift operations, after reading a raw value through the relevant PCI config, MMIO, or SOC15 access path. The paired address macros live in `nbio_7_4_offset.h`, for example `cfgBIF_CFG_DEV0_EPF0_VF9_0_DEVICE_CNTL`, `cfgBIF_CFG_DEV0_EPF0_VF10_0_PCIE_UNCORR_ERR_STATUS`, and corresponding entries for VF11/VF12.

The field groups are mostly standard PCIe concepts rather than AMD-specific types. Examples include `BUS_MASTER_EN`, `INT_DIS`, `MAX_PAYLOAD_SIZE`, `MAX_READ_REQUEST_SIZE`, `INITIATE_FLR`, `CURRENT_LINK_SPEED`, `NEGOTIATED_LINK_WIDTH`, `MSI_EN`, `MSIX_EN`, AER error bits, ECRC controls, ATS `ATC_ENABLE`, and ARI forwarding/function-group controls.

## Control Flow

This header has no runtime control flow. Runtime behavior is created in consumers that:

1. Detect an ASIC using the NBIO 7.4 register set.
2. Choose a VF register address from `nbio_7_4_offset.h`.
3. Read a PCIe configuration or NBIO register value using AMDGPU access helpers.
4. Decode fields using these `SHIFT` and `MASK` constants.
5. For writable controls, update only the intended field and preserve reserved or unrelated bits on writeback.

The fields in this chunk affect hardware flows such as VF PCI command enablement, function-level reset initiation, link training/retraining, link bandwidth interrupt reporting, MSI/MSI-X programming, AER error masking/severity classification, AER log capture, ATS enablement for translated requests, and ARI function enumeration/control. The macros themselves do not enforce access width, side-effect rules, or write ordering; those rules come from the PCIe spec, AMD register documentation, and existing driver access paths.

## State And Persistence

The header is compile-time-only and has no stored state. It persists no values and performs no initialization.

The state described by these macros lives in hardware PCIe configuration registers for virtual functions. Some fields are effectively static capability state, such as capability IDs, versions, next pointers, supported payload sizes, link speed/width capability, MSI/MSI-X capability layout, AER capability bits, ATS queue depth/support bits, and ARI next-function metadata. Other fields are live controls, including command bits, Device Control, Link Control, MSI/MSI-X enable/mask bits, AER masks/severity controls, ECRC enables, ATS `ATC_ENABLE`, and ARI function-group enables.

Status fields can be transient, sticky, or write-one-to-clear depending on the register. Examples include conventional PCI status error bits, PCIe Device Status, Link Status, AER correctable and uncorrectable status, MSI pending bits, and AER header/prefix logs. This generated header does not encode reset defaults, read-only/write-only permissions, write-one-to-clear behavior, or persistence across FLR, hot reset, GPU reset, suspend/resume, or power-gating. Consumers must preserve reserved bits and follow the hardware-defined reset domain.

## Dependencies And Integration Points

The closest dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_offset.h`, which supplies the matching `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` offsets. This shift/mask header is only meaningful when its field macros are paired with the matching offset symbol for the same VF and register.

The header is included by NBIO and power-management code in this tree, including `drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c` and several SMU/powerplay files. Those consumers use the broader NBIO 7.4 definition set for ASIC-specific register access. This particular chunk is most relevant to VF PCIe configuration, SR-IOV diagnostics, PCIe link setup/status reporting, interrupt setup, AER/RAS handling, ATS/IOMMU integration, and ARI function enumeration.

Other integration points include:

- Linux PCI/PCIe enumeration expectations for VF capability layout.
- SR-IOV VF enablement and reset paths that rely on stable VF config-space layout.
- Interrupt setup code that programs MSI or MSI-X message address/data, masks, pending bits, table offsets, and PBA offsets.
- RAS/AER paths that decode uncorrectable/correctable error status, severity, masks, header logs, and prefix logs.
- IOMMU/ATS paths that need ATS capability/control fields to agree with the rest of the GPU memory-translation stack.
- Link-management paths that inspect or write speed, width, retrain, common-clock, autonomous bandwidth, and completion-timeout controls.

The repeated `VF9`, `VF10`, and `VF11` sections share identical field layouts but target distinct VF config images. Exact macro spelling is part of the ABI between generated headers and driver code.

## Risks And Edge Cases

The largest risk is silent misprogramming from a one-bit mask or shift error. In this chunk, that could enable bus mastering or memory access on the wrong bit, hide or misclassify AER errors, corrupt MSI/MSI-X programming, initiate FLR unintentionally, misreport link speed/width, or enable ATS/ARI behavior contrary to the platform policy.

The repetitive generated layout makes copy/generation drift plausible. VF9, VF10, and VF11 should have the same field definitions for equivalent registers; a mismatch in one VF would only surface when that VF number is configured or diagnosed. VF12 is partial in this chunk, so the merge lane must not infer that the VF12 Device Capability 2 block is complete at line 17033.

Register width is another risk. Some macros describe 8-bit or 16-bit PCI config fields, while others describe 32-bit BARs, AER logs, capability headers, or table offsets. Callers must use the correct access size and preserve reserved bits. MSI registers also have overlapping 32-bit and 64-bit layouts, for example message data and mask offsets that differ depending on whether 64-bit MSI addressing and per-vector masking are active.

AER and status registers can have side effects. The presence of a `_MASK` macro does not imply that a field is safe to write as an ordinary read-modify-write. Error status may be sticky or write-one-to-clear, and log registers may be meaningful only after a captured error. Similar caution applies to link retraining, FLR initiation, MSI/MSI-X enablement, and ATS/ARI enable controls.

The chunk starts and ends inside repeated generated blocks. Chunk-local analysis should account for the missing earlier VF8 uncorrectable-error context and the missing later VF12 Device Control 2, MSI, AER, ATS, and ARI context. A final per-file report should reconcile this chunk with adjacent chunks before making claims about the whole `VF8` or `VF12` register set.

## Test Signals

Useful validation signals are mostly compile-time and hardware-integration oriented:

- Build AMDGPU code paths that include `nbio_7_4_sh_mask.h` with `nbio_7_4_offset.h`, confirming the generated macro names referenced by NBIO 7.4 consumers still resolve.
- Compare every covered `BIF_CFG_DEV0_EPF0_VF9_0`, `VF10_0`, `VF11_0`, and partial `VF12_0` register name against `nbio_7_4_offset.h` to ensure matching offsets exist for the same VF/register names.
- Cross-check repeated VF9/VF10/VF11 field definitions for identical masks and shifts on equivalent registers.
- On matching hardware, enable SR-IOV VFs and verify PCI enumeration reports plausible vendor/device/class, BAR, PCIe capability, MSI/MSI-X, AER, ATS, and ARI information.
- Exercise VF reset paths, especially `INITIATE_FLR`, and confirm command/status, device status, link status, MSI/MSI-X, AER, ATS, and ARI controls settle to expected values afterward.
- Validate MSI/MSI-X delivery, masking, pending-bit behavior, table offset/BIR, and PBA offset/BIR for VFs covered by this chunk.
- Use PCIe/AER fault injection or hardware error telemetry to verify correctable and uncorrectable error bits, masks, severity fields, header logs, and TLP prefix logs decode consistently with PCIe documentation and AMD expectations.
- Check link diagnostics under normal boot, reset, and power-management transitions: negotiated speed/width, link training, data-link active, common-clock, bandwidth-management status, and autonomous-bandwidth status should decode correctly.
- Exercise ATS/ARI-aware configurations with IOMMU enabled and disabled, checking that `ATC_ENABLE`, STU, queue-depth support, ARI next-function, and function-group controls are interpreted consistently.

### subset-b-003233: lines 17034-19455

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 17034-19455

## Purpose

This chunk is an auto-generated AMD NBIO 7.4 shift/mask slice for PCI/PCIe configuration-space fields exposed through `BIF_CFG_DEV0_EPF0_VF*_0` virtual-function blocks. It contains no executable driver logic. Its purpose is to publish preprocessor constants that let AMDGPU, display, PSP, and power-management code decode or program individual bitfields in NBIO-backed PCIe configuration registers.

The selected line range starts in the middle of the VF12 PCIe capability tail, covers the complete VF13 and VF14 configuration-field masks, and then covers most of the VF15 block through `PCIE_TLP_PREFIX_LOG3`. The remainder of VF15, including ATS and ARI fields, continues immediately after this chunk.

## Public Surface In This Chunk

The public surface is 2,135 `#define` macros in the assigned range: 1,060 `__SHIFT` constants and 1,075 `_MASK` constants. The count is not pair-perfect because the chunk starts and ends inside register groups, because full-width and reserved fields still have generated masks, and because fields named `*_MASK` generate macro names such as `*_MASK_MASK`.

Macro naming follows the generated register-field convention:

- `BIF_CFG_DEV0_EPF0_VF12_0_<REGISTER>__<FIELD>__SHIFT` and `_MASK` describe the tail of VF12 registers in this range.
- `BIF_CFG_DEV0_EPF0_VF13_0_<REGISTER>__<FIELD>__SHIFT` and `_MASK` describe a full VF13 PCIe config decode block.
- `BIF_CFG_DEV0_EPF0_VF14_0_<REGISTER>__<FIELD>__SHIFT` and `_MASK` describe a full VF14 PCIe config decode block.
- `BIF_CFG_DEV0_EPF0_VF15_0_<REGISTER>__<FIELD>__SHIFT` and `_MASK` describe VF15 from conventional PCI header fields through AER/TLP prefix logs in this range.

There are no functions, structs, enums, storage objects, or inline helpers here. The API contract is the exact macro spelling and numeric value, which must remain synchronized with `nbio_7_4_offset.h` and AMD's NBIO 7.4 register database.

## Register Coverage

The VF12 portion begins at the `DEVICE_CAP2` tail and covers PCIe capability 2, MSI/MSI-X, vendor-specific extended capability, Advanced Error Reporting, ATS, and ARI field definitions. This is the continuation of a VF12 block that began earlier in the header.

The VF13 and VF14 portions each provide a complete virtual-function PCI configuration decode map:

- Conventional PCI header fields: vendor/device ID, command, status, revision ID, class code bytes, cache-line size, latency timer, header type, BIST, six BARs, adapter ID, ROM BAR, capability pointer, interrupt line, and interrupt pin.
- PCIe capability fields: capability list header, PCIe capability flags, device capability/control/status, link capability/control/status, device capability/control/status 2, link capability/control/status 2, and reserved slot capability/control/status 2 placeholders.
- MSI and MSI-X fields: capability IDs, next pointers, MSI enable/multiple-message controls, 64-bit MSI addressing/data/mask/pending forms, MSI-X table size, function mask, enable bit, table BIR/offset, and PBA BIR/offset.
- Vendor-specific enhanced capability fields: capability ID/version/next pointer, VSEC ID/revision/length, and two scratch payload registers.
- Advanced Error Reporting fields: AER capability list, uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, four TLP header log dwords, and four TLP prefix log dwords.
- ATS fields: ATS enhanced capability list, invalidate queue depth, page-aligned request/global invalidate capability, STU, and ATC enable.
- ARI fields: ARI enhanced capability list, MFVC/ACS function group capabilities, next function number, MFVC/ACS group enables, and function group selection.

The VF15 portion repeats the same layout as VF13/VF14 from vendor ID through `PCIE_TLP_PREFIX_LOG3`. The line range stops before VF15 `PCIE_ATS_ENH_CAP_LIST`, so ATS and ARI coverage for VF15 belongs to the next chunk.

## Field Semantics

The conventional PCI fields describe enumeration-visible identity, device class, BAR aperture attributes, command enables, status/error bits, interrupt routing, and capability-chain entry points for SR-IOV virtual functions. Command and status masks cover memory/I/O decode, bus mastering, parity/SERR handling, interrupt disable/status, capability-list presence, aborts, and parity/system-error observation.

The PCIe device and link fields expose negotiated and advertised behavior for payload sizing, phantom functions, extended tags, endpoint L0s/L1 latency, role-based error reporting, completion timeouts, ARI forwarding, atomic operations, ID-based ordering, LTR, OBFF, 10-bit tags, emergency power reduction, TLP prefixes, target link speed, compliance entry, autonomous speed disable, de-emphasis, equalization status, and downstream component presence.

The MSI/MSI-X fields describe interrupt-message routing state rather than CPU interrupt delivery code. They provide masks for enable bits, message count fields, 64-bit address/data registers, per-vector mask and pending bits, MSI-X table/PBA BAR indicators, and MSI-X function masking. The overlapping offsets in the matching offset header for MSI 32-bit versus 64-bit forms mean consumers must interpret these fields according to the enabled MSI capability format.

The AER fields are diagnostics and policy controls. Uncorrectable status/mask/severity covers data-link protocol, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic-op egress blocked, and TLP prefix blocked conditions. Correctable status/mask covers receiver errors, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal errors, correctable internal errors, and header-log overflow. AER capability/control fields include first-error pointer, ECRC generation/check support and enable bits, multi-header-record support, TLP prefix log presence, and completion-timeout log capability.

The ATS and ARI fields are virtualization-sensitive. ATS controls address-translation cache behavior through invalidate queue depth, STU, and ATC enable. ARI controls alternative routing and function grouping so many virtual functions can be represented beyond the legacy PCI function-number limit. These fields are meaningful only when platform IOMMU, PCIe hierarchy, and SR-IOV policy agree.

## Control Flow And State

There is no runtime control flow in this header. The effective flow is compile-time substitution:

1. A translation unit includes `nbio/nbio_7_4_offset.h` and `nbio/nbio_7_4_sh_mask.h`.
2. Driver code selects a register address macro such as `cfgBIF_CFG_DEV0_EPF0_VF13_0_DEVICE_CNTL2`.
3. Register helpers or open-coded bit operations use the corresponding `BIF_CFG_DEV0_EPF0_VF13_0_DEVICE_CNTL2__<FIELD>__SHIFT` and `_MASK` macros to insert, extract, preserve, or compare fields.
4. Actual state changes occur through NBIO/PCI config, MMIO, SMN, or indirect register access code outside this header.

The header stores no software state and persists nothing by itself. Persistent state lives in hardware registers, PCIe config space, or firmware-managed NBIO state. Some fields are writable configuration controls that survive until reset, FLR, link reset, power transition, or driver reprogramming. Other fields are hardware-updated status, sticky error, log, or write-one-to-clear bits whose behavior must be inferred from the PCIe specification and AMD hardware documentation rather than from the macro names.

## Dependencies And Integration Points

The matching address definitions are in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_offset.h`, where the same VF12 through VF15 registers use `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` offsets. These shift/mask macros must be paired with that same NBIO 7.4 offset header; mixing ASIC generations can silently target the wrong register or field.

Direct include sites in this tree include:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c`, which is the main NBIO 7.4 implementation and uses generated masks with SOC15/NBIO register helpers.
- `drivers/gpu/drm/amd/pm/swsmu/smu11/arcturus_ppt.c`, `drivers/gpu/drm/amd/pm/swsmu/smu13/aldebaran_ppt.c`, and `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_6_ppt.c`, which use NBIO 7.4 register fields for platform power-management behavior.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_hwmgr.c` and `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_inc.h`, which include the same generated NBIO 7.4 mask surface for older powerplay paths.

Semantic dependencies are the PCI and PCI Express configuration-space specifications, SR-IOV virtual-function behavior, MSI/MSI-X interrupt capability layouts, AER, ATS, ARI, and AMD's generated NBIO 7.4 register database. The macros do not encode reset values, access permissions, lock sequencing, firmware ownership, side effects, or whether a field is valid on every NBIO 7.4 ASIC variant.

## Risks And Maintenance Notes

- The range is chunked mid-register context. It starts after the beginning of VF12 `DEVICE_CAP2` and ends before VF15 ATS/ARI, so adjacent chunks are required for a complete per-file report.
- VF13, VF14, and VF15 are intentionally repetitive. Prefix mistakes are the main review risk: a `VF14` mask paired with a `VF13` offset can compile cleanly while addressing the wrong virtual function.
- Wrong AER masks or severities can suppress important PCIe errors, misclassify fatal/non-fatal conditions, or misdecode sticky hardware logs.
- MSI/MSI-X mask misuse can affect interrupt routing, vector masking, pending-bit interpretation, or table/PBA BAR location.
- ATS and ARI fields interact with IOMMU and SR-IOV topology. Enabling or decoding them incorrectly can affect address translation, isolation, and virtual-function enumeration.
- Full-width `0xFFFFFFFFL` masks usually represent payload/log/scratch fields, not permission to write all bits indiscriminately.
- Names such as `*_MASK_MASK` are valid generated names when the hardware field is named `MASK`; cleanup scripts should not rename or normalize them.
- This generated header has no type safety. Field widths, access width, and side effects must be validated against the offset header and hardware documentation.

## Test Signals

Useful validation signals for this chunk are:

- Build coverage for all NBIO 7.4 include sites, especially `amdgpu/nbio_v7_4.c` and the Arcturus/Aldebaran/SMU power-management files.
- Cross-header checks that each register prefix in this chunk has a matching `cfgBIF_CFG_DEV0_EPF0_VF12_0_*`, `cfgBIF_CFG_DEV0_EPF0_VF13_0_*`, `cfgBIF_CFG_DEV0_EPF0_VF14_0_*`, or `cfgBIF_CFG_DEV0_EPF0_VF15_0_*` offset in `nbio_7_4_offset.h`.
- Generated-header comparison against AMD's authoritative NBIO 7.4 register database, with special attention to the repetitive VF13/VF14/VF15 blocks and the chunk boundary at VF15 ATS.
- Static checks that masks fit the expected 8-, 16-, or 32-bit PCI config register widths and that each `__SHIFT` has the expected generated mask.
- Hardware or simulator PCI config-space dumps for SR-IOV virtual functions 12 through 15, compared with `lspci -vvxxx`-style decoding for PCIe capabilities, MSI/MSI-X, AER, ATS, and ARI.
- Error-injection or observation tests that verify AER status, mask, severity, header log, and TLP prefix log fields decode correctly.
- Virtualization tests that enumerate many SR-IOV VFs, validate ARI behavior, enable/disable ATS under IOMMU control, and confirm that interrupt delivery through MSI/MSI-X remains stable.

### subset-b-003234: lines 19456-22067

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 19456-22067

## Scope

This chunk covers generated shift and mask macros from the AMDGPU NBIO 7.4 register mask header. It starts at the tail of the VF15 PCIe extended capability area and runs through the beginning of the GDC RAS status block, ending inside `GDCSOC_RAS_LEAF4_STATUS`.

The range is organized by the source file's `addressBlock` comments:

- VF15 PCIe ATS and ARI extended capability fields.
- `nbio_nbif0_bif_bx_pf_SYSPFVFDEC` and `nbio_nbif0_bif_bx_SYSDEC`, including MM/PCIE indirect indexes, system hub indirect windows, BIOS scratch registers, interrupt controls, and graphics MMIO register CAM mappings.
- RCC strap, endpoint, downstream, PF/VF, and device-level BIF decode fields for PCIe policy, LTR, DPA, error reporting, peer apertures, bus numbers, reset, BACO, and address LUTs.
- BIF decode fields for interrupt control, doorbells, framebuffer access, HDP flush/remap, ring-buffer state, mailbox registers, and VM-hypervisor mailbox signaling.
- GDC and duplicated `GDC0_` blocks for NGDC/SYSHUB control, SDMA/IH/MMSCH/ACV doorbell ranges, doorbell fences, and S2A arbitration controls.
- MSI-X vector register fields for graphics vectors 0 through 2 and the pending bit array.
- SYSHUB direct clock, deep-sleep, transaction-idle, scratch, reset, QoS, and NIC400 interconnect controls.
- SION credit, burst, time-slot, and control registers.
- GDC reset and GDC RAS central/leaf control/status fields.

The file is purely generated register metadata. This chunk defines preprocessor constants only; it has no C functions, structs, global variables, runtime storage, or executable control flow.

## Purpose

The purpose of this section is to describe the bit-level ABI for NBIO 7.4 hardware registers. Each hardware register field is represented by the standard pair:

- `<REGISTER>__<FIELD>__SHIFT`, the field bit offset.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate, test, or compose that field in a 32-bit register value.

The sibling `nbio_7_4_offset.h` header supplies register addresses such as `mmBIF_FB_EN`, `mmGPU_HDP_FLUSH_REQ`, `mmGPU_HDP_FLUSH_DONE`, `mmBIF_DOORBELL_INT_CNTL`, `mmBIF_IH_DOORBELL_RANGE`, and `mmREMAP_HDP_MEM_FLUSH_CNTL`; this header supplies the field layout at those addresses. Driver code consumes these constants through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and `SOC15_REG_OFFSET`.

## Important Macro Families

### PCIe ATS, ARI, and Indirect Windows

The opening lines finish the VF15 PCIe capability area. `BIF_CFG_DEV0_EPF0_VF15_0_PCIE_ATS_ENH_CAP_LIST`, `BIF_CFG_DEV0_EPF0_VF15_0_PCIE_ATS_CAP`, and `BIF_CFG_DEV0_EPF0_VF15_0_PCIE_ATS_CNTL` define capability-list linkage, invalidate queue depth, page-aligned/global invalidate capability, STU, and `ATC_ENABLE`. `BIF_CFG_DEV0_EPF0_VF15_0_PCIE_ARI_*` fields expose ARI capability, next-function number, function-group capabilities, and ARI control.

`MM_INDEX`, `MM_DATA`, `MM_INDEX_HI`, `SYSHUB_INDEX_OVLP`, `SYSHUB_DATA_OVLP`, `PCIE_INDEX`, `PCIE_DATA`, `PCIE_INDEX2`, and `PCIE_DATA2` are indirect access windows. In `nbio_v7_4.c`, `nbio_v7_4_get_pcie_index_offset()` and `nbio_v7_4_get_pcie_data_offset()` return the SOC15 offsets for `mmPCIE_INDEX2` and `mmPCIE_DATA2`, so other AMDGPU code can route PCIe register accesses through this NBIO aperture.

### Scratch, Interrupt, and MMIO CAM Registers

`SBIOS_SCRATCH_0..3` and `BIOS_SCRATCH_0..15` are full-width scratch registers used as firmware/BIOS-visible state exchange slots. The masks are full `0xFFFFFFFFL`, meaning the header documents storage width but not ownership or protocol.

`BIF_RLC_INTR_CNTL`, `BIF_VCE_INTR_CNTL`, and `BIF_UVD_INTR_CNTL` expose command-complete, self-recovered hang, FLR-needed hang, and VM-busy transition interrupt controls for RLC, VCE, and UVD. `BIF_UVD_INTR_CNTL` also includes an `UVD_INST_SEL` field in the top nibble.

`GFX_MMIOREG_CAM_ADDR0..7`, matching `GFX_MMIOREG_CAM_REMAP_ADDR0..7`, `GFX_MMIOREG_CAM_CNTL`, and the completion policy registers describe a small CAM for graphics MMIO address remapping. The address/remap masks cover 20-bit values, `GFX_MMIOREG_CAM_CNTL__CAM_ENABLE_MASK` enables eight entries, and the zero/one/programmable completion registers are full-width. Incorrect CAM values can redirect MMIO accesses to the wrong block or change completion behavior.

### RCC PCIe Endpoint, Downstream, and Device Control

The RCC strap and endpoint/downstream groups cover PCIe behavior visible early in device setup:

- `RCC_BIF_STRAP0` and `RCC_DEV0_EPF0_STRAP0` include strap-derived revision/device behavior, including `STRAP_ATI_REV_ID_DEV0_F0`, which `nbio_v7_4_get_rev_id()` reads and shifts.
- `EP_PCIE_*`, `DN_PCIE_*`, and unprefixed `PCIE_*` registers define endpoint/downstream scratch, control, config, RX/TX policy, error reporting, link-speed control, LTR control, PME, DPA capabilities, and DPA per-substate power allocation.
- `EP_PCIE_TX_LTR_CNTL` includes LTR message policy fields. `nbio_v7_4_program_ltr()` in `nbio_v7_4.c` writes the corresponding SMN register and clears `EP_PCIE_TX_LTR_CNTL__LTR_PRIV_MSG_DIS_IN_PM_NON_D0_MASK` as part of ASPM/LTR programming.
- `RCC_ERR_LOG`, `RCC_ERR_INT_CNTL`, `RCC_DOORBELL_APER_EN`, `RCC_CONFIG_MEMSIZE`, `RCC_IOV_FUNC_IDENTIFIER`, `RCC_BACO_CNTL_MISC`, `RCC_RESET_EN`, `RCC_VDM_SUPPORT`, `RCC_MARGIN_PARAM_CNTL0/1`, peer range registers, bus-number controls, peer framebuffer offsets, common link control, requester-id restore, and multi-host arbitration fields provide the low-level knobs for PCIe error handling, memory-size discovery, SR-IOV, peer apertures, link/power policy, and multi-host traffic.

`nbio_v7_4_get_memsize()` reads `mmRCC_CONFIG_MEMSIZE`, and `nbio_v7_4_enable_doorbell_aperture()` writes the `RCC_DOORBELL_APER_EN__BIF_DOORBELL_APER_EN` field.

### BIF Doorbells, Framebuffer Access, HDP Flush, and Mailboxes

The `nbio_nbif0_bif_bx_BIFDEC1` and PF decode groups are the highest-impact driver integration area in this chunk.

`BUS_CNTL`, `BIF_FEATURES_CONTROL_MISC`, `BIF_DOORBELL_CNTL`, and `BIF_DOORBELL_INT_CNTL` control coherency, endpoint path disable bits, atomic error interrupts, self-ring/doorbell translation behavior, doorbell monitor interrupt generation, and doorbell/RAS interrupt status/clear/disable bits. `nbio_v7_4_handle_ras_controller_intr_no_bifring()` and `nbio_v7_4_handle_ras_err_event_athub_intr_no_bifring()` read `BIF_DOORBELL_INT_CNTL` status fields and write the matching clear fields when the BIF ring is disabled. `nbio_v7_4_enable_doorbell_interrupt()` toggles `DOORBELL_INTERRUPT_DISABLE`.

`BIF_FB_EN` has `FB_READ_EN` and `FB_WRITE_EN`; `nbio_v7_4_mc_access_enable()` writes these bits to allow or block memory-controller framebuffer access through NBIO.

`BIF_INTR_CNTL__RAS_INTR_VEC_SEL` selects the RAS interrupt vector. The v7.4 RAS interrupt setup paths set it to vector 1 for the bare-metal case.

`BACO_CNTL` and the `BIF_BACO_EXIT_TIMER*` registers describe BACO enable, dummy mode, power-off, D-state bypass, interrupt masking, auto-exit, and exit timing. `nbio_v7_4_init_registers()` clears `BACO_DUMMY_EN` and `BACO_EN` for IP version 7.4.4 when not running as an SR-IOV VF.

`BIF_SDMA0_DOORBELL_RANGE`, `BIF_SDMA1_DOORBELL_RANGE`, `BIF_IH_DOORBELL_RANGE`, `BIF_MMSCH0_DOORBELL_RANGE`, `BIF_ACV_DOORBELL_RANGE`, plus duplicated `GDC0_` range registers, all use the same `OFFSET`/`SIZE` layout. `nbio_v7_4_sdma_doorbell_range()`, `nbio_v7_4_vcn_doorbell_range()`, and `nbio_v7_4_ih_doorbell_range()` use these masks to program doorbell ownership windows for SDMA, VCN/MMSCH, and IH.

`HDP_REG_COHERENCY_FLUSH_CNTL`, `HDP_MEM_COHERENCY_FLUSH_CNTL`, `GPU_HDP_FLUSH_REQ`, `GPU_HDP_FLUSH_DONE`, `REMAP_HDP_MEM_FLUSH_CNTL`, and `REMAP_HDP_REG_FLUSH_CNTL` define the HDP flush interface. `nbio_v7_4_get_hdp_flush_req_offset()` and `nbio_v7_4_get_hdp_flush_done_offset()` return the request/done offsets, while `nbio_v7_4_hdp_flush_reg` publishes done masks for CP0..CP9 and SDMA0..SDMA1. `nbio_v7_4_remap_hdp_registers()` writes remap offsets used by KFD MMIO remapping. The chunk's request/done masks are the synchronization contract for cache flush completion.

The mailbox group (`MAILBOX_MSGBUF_TRN_DW*`, `MAILBOX_MSGBUF_RCV_DW*`, `MAILBOX_CONTROL`, `MAILBOX_INT_CNTL`, and `BIF_VMHV_MAILBOX`) provides transmit/receive message data, valid/ack handshakes, interrupt enables, and compact VM/hypervisor mailbox fields. These fields are stateful protocol registers: valid and ack bits must be ordered with the associated data fields.

### GDC, SYSHUB, NIC400, SION, Reset, and RAS

The GDC/SYSHUB blocks define clock/power and fabric controls:

- `NGDC_MGCG_CTRL`, `GDC0_NGDC_MGCG_CTRL`, `SYSHUB_MGCG_CTRL_SOCCLK`, and `SYSHUB_MGCG_CTRL_SHUBCLK` control medium-grain clock gating enable/mode/hysteresis and sub-block disables.
- `SYSHUB_DS_CTRL_*`, `SYSHUB_DS_CTRL2_*`, and bgen bypass/immediate-enable registers control deep-sleep and bus-generator behavior for HST/DMA/SYSHUB clients.
- `SYSHUB_TRANS_IDLE_SOCCLK` provides per-VF and PF transaction-idle status bits. These are especially relevant to SR-IOV teardown, FLR, and reset sequencing.
- `HST_CLK*`, `DMA_CLK*`, and `NIC400_*` fields configure FLR/link-reset behavior, static QoS overrides, read/write weighted round-robin values, outstanding transaction limits, rate/fairness controls, target flow-control latency, and QoS ranges.
- `SION_CL*` registers define request/data/read-response/write-response burst targets, time slots, and pool-credit allocation across four client lanes. `SION_CNTL_REG0/1` collect force, idle, sleep, credit, reset, and timeout behavior.

`SHUB_PF_FLR_RST`, `SHUB_PF0_VF_FLR_RST`, `SHUB_LINK_RESET`, `SHUB_HARD_RST_CTRL`, `SHUB_SOFT_RST_CTRL`, `SHUB_SDP_PORT_RST`, and `SHUB_RST_MISC_TRL` define reset triggers and reset-domain selection for PFs, VFs, links, NIC400, SDP ports, SION, and RSMU-assisted soft reset.

The final RAS block starts with `GDCL_RAS_CENTRAL_STATUS` and `GDCSOC_RAS_CENTRAL_STATUS`, then covers `GDCSOC_RAS_LEAF0_CTRL` through `GDCSOC_RAS_LEAF6_CTRL`, `GDCSOC_RAS_LEAF2_MISC_CTRL`, and status registers from `GDCSOC_RAS_LEAF0_STATUS` through the start of `GDCSOC_RAS_LEAF4_STATUS`. Leaf controls expose detection enables, poison/parity error event enables, stall enables, generated/propagated event enables, and, on leaf 2, RAS interrupt/stall/drop/mask-disabling fields. Leaf status registers expose received error events, poison/parity detection, generated-event state, and egress-stall/propagation state.

## Control Flow and State Behavior

There is no local control flow in this header. The runtime flow is created by consumers that read or write registers with these masks:

1. Read a register through `RREG32_SOC15`, `RREG32_PCIE`, or a raw register offset.
2. Extract fields with `REG_GET_FIELD` or test masks directly.
3. Compose updated values with `REG_SET_FIELD` or mask operations.
4. Write the register back with `WREG32_SOC15`, `WREG32_PCIE`, `WREG32_FIELD15`, or a raw write.

Several fields represent persistent hardware configuration until reset or later reprogramming: doorbell ranges, framebuffer access enablement, BACO control, PCIe LTR/DPA policy, SYSHUB deep-sleep/clock-gating, NIC400 QoS, SION credits, reset-domain enables, and RAS control bits.

Other fields represent transient hardware state or command handshakes: `GPU_HDP_FLUSH_REQ`/`GPU_HDP_FLUSH_DONE`, mailbox valid/ack bits, doorbell interrupt status/clear bits, transaction-pending bits, SYSHUB transaction-idle bits, FLR/reset strobes, and RAS central/leaf status bits. These require ordering and polling discipline; treating a status bit as durable configuration, or vice versa, can deadlock reset/flush paths or lose interrupts.

## Dependencies and Integration Points

Direct compile-time dependencies are the AMDGPU register helper macros and the corresponding offset header. Runtime dependencies are the NBIO, PCIe, GDC/SYSHUB, HDP, RAS, KFD, and SR-IOV paths that program the registers.

Important consumers observed in this tree include:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c`, which includes this header and uses fields from this chunk for revision ID extraction, memory-controller access, doorbell apertures and ranges, IH control, HDP flush request/done offsets, BACO cleanup, RAS doorbell interrupt handling, RAS interrupt vector selection, HDP register remapping, and ASPM/LTR programming.
- SMU/PowerPlay files such as `pm/swsmu/smu11/arcturus_ppt.c`, `pm/swsmu/smu13/aldebaran_ppt.c`, `pm/swsmu/smu13/smu_v13_0_6_ppt.c`, and `pm/powerplay/hwmgr/vega20_hwmgr.c`, which include the NBIO 7.4 masks for power-management register programming on supported ASICs.
- HDP implementations use the same register-helper idiom for power/flush state, and NBIO v7.4 publishes HDP flush masks from this chunk through `nbio_v7_4_hdp_flush_reg`.

The constants also integrate with firmware and virtualization protocols. BIOS scratch fields, RCC straps, `BIF_VMHV_MAILBOX`, PF/VF FLR reset bits, per-VF transaction-idle bits, and doorbell aperture/range fields are shared boundaries between host driver, firmware/PSP/SMU, hypervisor, and guest-visible device state.

## Risks and Review Notes

- Generated-header drift is high risk. A wrong mask or shift silently writes the wrong hardware bit and can break PCIe link policy, memory access, HDP coherency, reset sequencing, RAS delivery, or VF isolation.
- Full-width scratch/mailbox/data masks do not define ownership. Callers must know the firmware or hypervisor protocol before writing them.
- Doorbell range `OFFSET` and `SIZE` fields are security-sensitive. Incorrect values can expose another engine's doorbells, disable an engine's doorbells, or let a VF ring queues outside its intended aperture.
- HDP flush request/done masks are synchronization-sensitive. Missing or stale `DONE` masks can cause cache flush waits to time out or complete before writes are visible.
- RAS status/clear fields are easy to mishandle. The v7.4 driver explicitly clears doorbell interrupt status and harvests counters when the BIF ring is disabled; changes must preserve that ordering.
- Reset and FLR bits can affect PF/VF isolation and fabric stability. Writes to `SHUB_PF0_VF_FLR_RST`, `SHUB_LINK_RESET`, `SHUB_HARD_RST_CTRL`, or `SHUB_SOFT_RST_CTRL` should be reviewed with transaction-idle and pending-status handling.
- Some fields are ASIC-variant-sensitive. `nbio_v7_4.c` carries ALDEBARAN-specific register aliases and temporary masks, showing that this header may not fully describe every v7.4.x derivative.

## Test Signals

Useful validation signals for changes touching consumers of this chunk include:

- Successful kernel build with `W=1` coverage for AMDGPU configurations that include NBIO 7.4 ASICs.
- Driver probe on affected ASICs with correct `get_rev_id`, memory-size reporting, and no unexpected BACO dummy-mode warnings.
- Doorbell smoke tests: SDMA, IH, VCN/MMSCH, KFD queues, and interrupt delivery continue to function after range/aperture programming.
- HDP flush tests: CP and SDMA flush request/done paths do not time out and memory visibility is correct across VRAM/GTT/KFD paths.
- ASPM/LTR and power-management tests: suspend/resume, runtime power transitions, BACO entry/exit, and SMU power-state changes remain stable.
- SR-IOV tests: VF FLR, PF/VF transaction-idle, mailbox valid/ack, and VF doorbell isolation behave correctly.
- RAS tests: injected or simulated NBIF/ATHUB error events increment CE/UE counters, clear status, and invoke the expected global RAS ISR path without repeated stale interrupts.
- Register audit tests comparing generated mask/shift pairs against the hardware register database for NBIO 7.4 and known derivatives.

### subset-b-003235: lines 22068-24525

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 22068-24525

## Purpose

This chunk is a generated AMD NBIO 7.4 register shift/mask slice. It contains no executable logic; its purpose is to publish C preprocessor constants that tell AMDGPU NBIO, power-management, debug, and RAS code where individual bitfields live inside NBIO/PCIe configuration and sideband registers.

The selected range starts in the tail of the `GDCSOC_RAS_LEAF4_STATUS` field definitions, covers `GDCSOC_RAS_LEAF5_STATUS`, `GDCSOC_RAS_LEAF6_STATUS`, `GDCSHUB_RAS_CENTRAL_STATUS`, the full `nbio_nbif0_bif_cfg_dev0_swds_bifcfgdecp` / `BIF_CFG_DEV0_SWDS0_*` PCIe config-space block, RCC strap/endpoint/downstream/shadow register blocks for BIF decode and RCC port decode views, then enters `nbio_nbif0_bif_misc_bif_misc_regblk` and ends partway through `BIFC_DMA_ATTR_OVERRIDE_DEV0_F0_F1`.

## Public Surface In This Chunk

The public surface is 2,136 `#define` macros over 283 register names in the assigned line range. The macros are split into 1,073 `__SHIFT` constants and 1,063 `_MASK` constants. The counts are not balanced because the chunk begins in the middle of `GDCSOC_RAS_LEAF4_STATUS` and stops in the middle of `BIFC_DMA_ATTR_OVERRIDE_DEV0_F0_F1`.

Macro names follow the generated AMD register-field pattern:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's starting bit.
- `<REGISTER>__<FIELD>_MASK` gives the pre-shifted bit mask.
- Prefixes such as `BIF_CFG_DEV0_SWDS0`, `RCC_EP_DEV0_0`, `RCC_EP_DEV0_1`, `RCC_DWN_DEV0_0`, `RCC_DWN_DEV0_1`, `SHADOW`, and `BIFC` identify the hardware register namespace that must be paired with same-generation NBIO 7.4 offsets.

There are no functions, structs, enums, variables, or inline helpers. The ABI-like contract is the exact macro spelling and numeric value, because downstream register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, and `WREG32_SOC15` depend on these names matching the generated offset and SMN headers.

## Register Coverage

The opening RAS definitions expose leaf and hub status bits:

- `GDCSOC_RAS_LEAF4_STATUS` tail fields plus full `GDCSOC_RAS_LEAF5_STATUS` and `GDCSOC_RAS_LEAF6_STATUS` definitions for received error events, poison/parity detection, generated-status propagation, and egress-stall propagation.
- `GDCSHUB_RAS_CENTRAL_STATUS` fields for L2C/C2L egress-stall and error-event detection.

The `BIF_CFG_DEV0_SWDS0_*` block models a PCI-to-PCI/PCIe bridge-style configuration space:

- Conventional PCI identity and command/status fields: vendor/device ID, I/O and memory enable, bus master enable, SERR, interrupt disable, parity/abort/system-error status, revision/class bytes, cache line, latency, header type, BIST, BAR1, bridge bus numbers, I/O and memory windows, prefetchable memory windows, interrupt line/pin, and bridge control.
- Power-management and PCIe capability structures: PM capability/status/control, PCIe capability header, device/link/slot capability/control/status, Device Capabilities 2, Device Control 2, Link Capabilities 2, Link Control 2, Link Status 2, and slot capability/control/status 2.
- Interrupt and identity capabilities: MSI capability list/control/address/data, SSID capability, and PCIe vendor-specific enhanced capability headers and payload words.
- Virtual-channel and isolation features: VC enhanced capability, port VC capability/control/status, VC0/VC1 resource capability/control/status, device serial number, Advanced Error Reporting, ACS capability/control, Data Link Feature capability/status, 16 GT PHY capability/status, and lane margining.
- Diagnostics and error logs: AER uncorrectable status/mask/severity, correctable status/mask, AER capability/control, PCIe header logs, TLP prefix logs, secondary PCIe link control 3, lane error status, local/RTM parity mismatch at 16 GT, and per-lane equalization and margining status.

The per-lane groups are highly repetitive and cover lanes 0 through 15:

- `BIF_CFG_DEV0_SWDS0_PCIE_LANE_<n>_EQUALIZATION_CNTL` with downstream/upstream transmit preset fields and preset hint.
- `BIF_CFG_DEV0_SWDS0_LANE_<n>_EQUALIZATION_CNTL_16GT` with 16 GT transmit preset fields.
- `BIF_CFG_DEV0_SWDS0_LANE_<n>_MARGINING_LANE_CNTL` and `_STATUS` with receiver number, margin type, usage model, payload, request, software-ready, independent error sampler, and margin status fields.

The RCC endpoint/downstream sections expose internal NBIO controls around the same PCIe function:

- `RCC_STRAP0_RCC_DEV0_EPF0_STRAP0` and `RCC_STRAP1_RCC_DEV0_EPF0_STRAP0` for strapped device ID, revision ID, function enable, legacy device type, and D1/D2 support.
- `RCC_EP_DEV0_0_*` under `BIFDEC1` and `RCC_EP_DEV0_1_*` under `RCCPORTDEC`, including scratch, endpoint PCIe control, interrupt enable/status, RX control, bus/config control, transmit LTR control, DPA capability/latency/control/substate power allocation, PME control, TX control/requester ID, endpoint error control, RX error ignores, and link speed strap controls.
- `RCC_DWN_DEV0_0_*` and `RCC_DWN_DEV0_1_*` downstream controls for scratch/reserved, control, config, RX, bus, and CFG control.
- `RCC_DWNP_DEV0_0_*` and `RCC_DWNP_DEV0_1_*` downstream port controls for error control, RX control, link speed control, link control 2, and LTR message information from the endpoint.

The shadow and miscellaneous blocks cover bridge decode mirrors and BIFC policy/status:

- `SHADOW_*` bridge window mirrors for command, BAR1/BAR2, secondary/subordinate bus numbers, I/O base/limit, memory and prefetchable memory windows, upper prefetchable limits, high I/O base/limit, bridge control, and `SUC_INDEX`/`SUC_DATA`.
- `MISC_SCRATCH`, interrupt line polarity/enable, and `OUTSTANDING_VC_ALLOC` for outstanding request allocation per VC.
- `BIFC_MISC_CTRL0` and `BIFC_MISC_CTRL1` for BIFC/GMI/GSI/DMA policy bits: unit ID checking, DMA VC status, chain locking, split-read stall behavior, DMA atomic handling, SR-IOV/BME-drop handling, SDP read-response error forcing, unsupported command status, request ordering, request attribute masks, credit suppression, completion buffering, and message block-level selection.
- `BIFC_BME_ERR_LOG` and `BIFC_RCCBIH_BME_ERR_LOG0` for DMA/RCCBIH activity while bus mastering is low across dev0 functions 0-7, with corresponding clear bits.
- The beginning of `BIFC_DMA_ATTR_OVERRIDE_DEV0_F0_F1`, which provides two-bit override fields for ID-based ordering, relaxed ordering, snoop/no-snoop, and block-level behavior for dev0 functions 0 and 1. The rest of this override family continues after the chunk.

## Field Semantics

Most `BIF_CFG_DEV0_SWDS0_*` fields mirror PCI/PCI Express configuration-space semantics. Command/status fields determine whether the device decodes I/O or memory, can bus-master, reports parity or system errors, and exposes capability lists. Bridge window fields control how bus numbers and I/O/memory apertures are decoded. PCIe device/link/slot fields describe max payload/read request sizing, relaxed ordering, no-snoop, FLR, LTR/OBFF, link speed/width, ASPM, retrain and bandwidth events, slot power/attention signaling, and downstream presence.

AER and correctable/uncorrectable status fields are diagnostic and policy-sensitive. Status fields report error classes such as data link protocol, poisoned TLP, flow-control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic egress blocked, TLP prefix blocked, and poisoned TLP egress blocked. Mask and severity fields decide what is suppressed and which errors are treated as fatal/nonfatal. Header and TLP prefix log masks are whole-register payloads, not ordinary feature enables.

Lane equalization, 16 GT PHY, and margining fields describe link-training and receiver-margin controls. The driver or firmware must keep lane indexes, speed-generation suffixes, and downstream/upstream preset directions aligned with the correct hardware lane. Misusing one repeated lane macro can corrupt only a single lane's training policy, which makes failures intermittent and platform-dependent.

RCC endpoint/downstream fields are lower-level PCIe fabric controls than the config-space capability fields. They cover unsupported-request reporting, malformed atomic handling, LTR message behavior, interrupt sources, DPA power allocation, PME, requester ID, AER header-log timer behavior, RX error ignores for payload/traffic-class/prefix/PASID/TPH cases, and link generation straps up to Gen5. These fields are integrated with `nbio_v7_4.c`; for example NBIO 7.4 ASPM/LTR programming writes `smnRCC_EP_DEV0_0_EP_PCIE_TX_LTR_CNTL` and clears `EP_PCIE_TX_LTR_CNTL__LTR_PRIV_MSG_DIS_IN_PM_NON_D0_MASK`.

BIFC controls are crossbar/fabric policy fields. They influence DMA ordering, atomic request handling, GMI/RCC/BIH BME-drop behavior, SDP/GSI error response forcing, outstanding VC allocation, and per-function bus-master error logging. These fields should be treated as low-level hardware policy and status bits, not as generic software flags.

## Control Flow And State

There is no runtime control flow in this header. The effective flow is compile-time substitution:

1. NBIO 7.4 consumers include `nbio/nbio_7_4_offset.h`, `nbio/nbio_7_4_sh_mask.h`, and, where needed, `nbio/nbio_7_4_0_smn.h`.
2. Driver or PM code reads a register through AMDGPU MMIO/SMN helpers such as `RREG32_PCIE` or `RREG32_SOC15`.
3. `REG_GET_FIELD` uses the generated `_MASK` and `__SHIFT` constants to decode fields, or `REG_SET_FIELD`/open-coded masks are used before writing back.
4. Actual state changes happen in NBIO/PCIe hardware registers, not in this file.

The header itself stores no state and persists nothing. Persistence belongs to the hardware registers: straps reflect sampled hardware/firmware configuration, config-space controls can persist until reset or function-level reset, link training fields persist until retrain or reprogramming, and error/log/status registers may be sticky or write-one-to-clear depending on the register. The RAS flow in `amdgpu/nbio_v7_4.c` demonstrates this pattern by reading RAS status, incrementing software error counters elsewhere, and writing hardware status values back to clear latched conditions.

## Dependencies And Integration Points

The direct generated-header dependencies are the matching NBIO 7.4 offset and SMN headers in the same `include/asic_reg/nbio` directory. Masks in this chunk must not be mixed with offsets from another NBIO generation or from a different decode prefix.

Known source-tree consumers include:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c`, which includes this header for NBIO 7.4 register access, RAS interrupt handling, RAS error counting, doorbell control, clock/power setup, ASPM, and LTR programming.
- Power-management code such as `pm/powerplay/hwmgr/vega20_hwmgr.c`, `pm/powerplay/hwmgr/vega20_inc.h`, `pm/swsmu/smu11/arcturus_ppt.c`, `pm/swsmu/smu13/aldebaran_ppt.c`, and `pm/swsmu/smu13/smu_v13_0_6_ppt.c`, which include the same NBIO 7.4 headers while programming ASIC power/link behavior.
- AMDGPU discovery and RAS plumbing that selects `nbio_v7_4_funcs` / `nbio_v7_4_ras` for applicable ASIC IP versions.

Semantic dependencies include the PCI and PCI Express specifications, AMD's generated NBIO 7.4 register database, and ASIC-specific programming guides for side effects, read/write permissions, reset values, and write-one-to-clear behavior. The macros alone do not encode access type, reset value, ordering constraints, or whether firmware owns a field.

## Risks And Maintenance Notes

- The chunk boundaries are partial. It starts after the first `GDCSOC_RAS_LEAF4_STATUS` shift definition and ends before the rest of the `BIFC_DMA_ATTR_OVERRIDE_DEV0_*` definitions, so adjacent chunks are required for a complete per-file view.
- Generated names with prefixes that differ only by `0` versus `1`, such as `RCC_EP_DEV0_0_*` and `RCC_EP_DEV0_1_*`, are not interchangeable. They represent different decode views and must stay paired with their matching offsets.
- The per-lane equalization and margining blocks are repetitive; lane number, speed suffix, and preset direction are the primary differences. Manual edits or copied code can easily target the wrong lane or speed generation.
- Full-width masks such as `0xFFFFFFFFL` normally indicate an entire data/log/register payload. They should not be interpreted as permission to blindly write all bits as one.
- Error status, AER, RAS, BME log, and interrupt status fields may be sticky, hardware-updated, or write-one-to-clear. Incorrect read-modify-write sequences can lose error evidence or fail to clear interrupts.
- Link and power-management fields can affect ASPM/LTR, DPA, PME, link retraining, and link generation capability. Bad values can produce performance loss, hangs, hot-reset behavior, or platform-specific link instability.
- Fields whose hardware name contains `MASK` can generate identifiers ending in `_MASK_MASK`; tooling should not normalize or de-duplicate these names.

## Test Signals

Useful validation signals for this chunk are:

- Compile coverage for all NBIO 7.4 consumers, especially `amdgpu/nbio_v7_4.c` and the SMU/power-management files that include `nbio_7_4_sh_mask.h`.
- Cross-header checks that every register prefix represented here has a matching `reg*` or `smn*` definition in the NBIO 7.4 offset/SMN headers where expected.
- Generated-header comparison against AMD's authoritative NBIO 7.4 register database, focusing on repeated lane 0-15 blocks, AER status/mask/severity fields, RCC endpoint/downstream duplicates, and BIFC BME/DMA policy fields.
- Static validation that each field mask fits within its register width and corresponds to the documented shift and bit width; this is especially useful for multi-bit fields and partial chunks.
- Hardware register dumps decoded with these masks and compared with PCIe config-space tools such as `lspci -vvxxx` for command/status, capability chain, MSI, AER, ACS, link, slot, DLF, 16 GT PHY, and lane margining fields.
- RAS/error-injection testing that verifies NBIO RAS leaf/hub status, AER status, BME logs, interrupt status, and clear paths are decoded and cleared correctly without losing counts.
- ASPM/LTR and link-training tests on NBIO 7.4 hardware, including Gen4/Gen5 link speed policy, 16 GT equalization status, lane margining readiness, DPA/PME behavior, and absence of unexpected retrains.
- SR-IOV and BME policy tests for per-function DMA/RCCBIH BME-low logs and BIFC drop/override behavior, since several fields distinguish dev0 functions and VF/PF handling.

### subset-b-003236: lines 24526-26923

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 24526-26923

## Scope

This chunk covers generated shift and mask macros from the NBIO 7.4 AMD GPU register mask header. It starts in the middle of the `BIFC_DMA_ATTR_OVERRIDE_DEV0_F0_F1` mask definitions and ends at the `BIF_CFG_DEV0_EPF0_0_PCIE_DEV_SERIAL_NUM_ENH_CAP_LIST` register comment, before that register's field definitions in the next chunk.

The covered range includes:

- DMA transaction attribute override masks for device 0 functions F0-F7, including ID-based ordering, relaxed ordering, no-snoop, and block-level controls for posted and non-posted traffic.
- BIF client controls for BME dummy responses, transaction credit thresholds, host/slave arbitration, GSI request/completion arbitration, PCIe function control, PASID checking/status, ATHUB activity, performance counters, MMIO/DMA counter values, and register-interface error injection/logging.
- SMN master endpoint control, self-ring buffer/vector controls, INTx/D-state pending controls, GMI weighted round-robin weights, and power-break request fields.
- Per-function atomic unsupported-request error logs, DMA MP4/PASID error logging and clearing, NBIF virtual-wire control, virtual-wire change disable/reset/trigger registers, and LCLK clock/power-gating controls.
- RCC PFC blocks for AMDGFX and AMDGFXAZ latency tolerance reporting, PME restore, sticky restore state, and auxiliary power control.
- BIF reset block masks for hard/soft reset, graphics/VPU reset, PF function-level reset, D3hot-to-D0 reset, reset/power/D-state interrupt status and masks, and PF/VF FLR reset strobes.
- BIF RAS central/leaf control and status registers, IOHUB RAS interrupt handling, and RAS virtual-wire state from IOHUB.
- SUM indexed register access fields.
- The start of the PF0 PCI configuration-space bitfield map, from vendor/device IDs through base address registers, ROM BAR, capability pointers, power-management capability, PCIe device/link capability and control/status registers, MSI/MSI-X capability registers, vendor-specific enhanced capability registers, and virtual-channel capability/resource registers. The final line is the serial-number enhanced capability comment only.

This header chunk is generated data: it defines preprocessor constants only. It contains no functions, structs, runtime variables, locks, storage objects, or executable control flow.

## Purpose

The purpose of this section is to provide the bit-level ABI used by AMDGPU NBIO 7.4 code when composing and decoding MMIO and PCI configuration register values. Each hardware field is represented by the standard generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset of a field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or place that field.

Driver code combines these constants with AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and `SOC15_REG_OFFSET`. The sibling NBIO offset/default headers supply register addresses and reset values; this file supplies the field layout for those addresses.

## Important Macro Families

### DMA, Ordering, and BME Controls

The `BIFC_DMA_ATTR_OVERRIDE_DEV0_F*_F*` registers pack two functions per register. Each function gets 2-bit fields for posted and non-posted IDO override, relaxed-ordering override, no-snoop override, and block-level selection for IDO/non-IDO traffic. The chunk begins after the F0/F1 shifts and includes the F0/F1 masks plus complete F2/F3, F4/F5, and F6/F7 shift/mask groups.

`BIFC_DMA_ATTR_CNTL2_DEV0` adds per-function `BLKLVL_BYPASS_PCIE_IDO_CONTROL` bits for F0-F7. `BME_DUMMY_CNTL_0` carries per-function dummy response status fields used when bus mastering is disabled or being handled defensively. These fields sit directly on PCIe transaction attribute behavior, so consumers must preserve function-specific packing and avoid applying a PF0 mask to another function's bit positions.

### Arbitration, GSI, PASID, and Performance Counters

`BIFC_THT_CNTL`, `BIFC_HSTARB_CNTL`, and `BIFC_GSI_CNTL` describe credit-allocation thresholds and arbitration modes for read/write virtual channels, host/slave arbitration, SDP/SMN request arbitration, completion response arbitration, completion interleaving, and unsupported-request generation for several completion sources.

`BIFC_PCIEFUNC_CNTL`, `BIFC_PASID_CHECK_DIS`, `BIFC_SDP_CNTL_0`, `BIFC_SDP_CNTL_1`, `BIFC_PASID_STS`, and `BIFC_ATHUB_ACT_CNTL` expose PCIe function controls, PASID check bypass/status, SDP disconnect hysteresis/disable policy, and ATHUB activity status. These definitions are integration points for address-translation, KFD/PASID, virtualization, and link-idle policy code.

`BIFC_PERF_CNTL_0`, `BIFC_PERF_CNTL_1`, and the four `BIFC_PERF_CNT_*` data registers define enable, reset, selector, and 32-bit count fields for MMIO read/write and DMA read/write counters. The enable/reset bits are command-like controls around hardware counters; the count registers expose observed hardware state.

### Error Logging, Virtual Wires, and Power/Clock Controls

The chunk defines per-function `BIF_ATOMIC_ERR_LOG_DEV0_F0` through `_F7` fields for unsupported atomic opcode, request-enable-low, length, and non-relaxed request conditions. Each log has matching clear bits in the upper half of the register. `BIF_DMA_MP4_ERR_LOG`, `BIF_PASID_ERR_LOG`, and `BIF_PASID_ERR_CLR` provide additional DMA/PASID error capture and clearing.

`NBIF_VWIRE_CTRL`, `NBIF_SMN_VWR_*`, and `NBIF_SDP_VWR_*` define virtual-wire control, virtual-wire change disable bits, reset controls, trigger controls, and write-trigger behavior. These are used around low-power state signaling and sideband state propagation.

`NBIF_MGCG_CTRL_LCLK`, `NBIF_DS_CTRL_LCLK`, `SMN_MST_CNTL0`, and `SMN_MST_EP_CNTL1/2/3/4/5` describe LCLK medium-grain clock gating, deep-sleep controls, and SMN master endpoint behavior. These fields are power-management sensitive and generally need to be programmed in the sequencing expected by the NBIO initialization and suspend/resume paths.

### RCC PFC, Reset, and RAS Blocks

The `RCC_PFC_AMDGFX_*` and `RCC_PFC_AMDGFXAZ_*` groups cover latency tolerance reporting controls, PME restore fields, sticky restore registers, and auxiliary power controls for two RCC PFC address blocks. These fields persist or restore PCIe/power-management-facing state across power transitions.

The `nbio_nbif0_bif_rst_bif_rst_regblk` portion covers reset control and interrupt state: `HARD_RST_CTRL`, `RSMU_SOFT_RST_CTRL`, `SELF_SOFT_RST`, `BIF_GFX_DRV_VPU_RST`, `BIF_RST_MISC_CTRL*`, per-PF FLR and D3hot/D0 reset controls, interrupt status/mask registers for instance reset, PF FLR, D3hot/D0, power, PF D-state, and PF0 VF FLR, plus PF/PF0-VF reset strobe registers and per-PF D-state value registers.

The `nbio_nbif0_bif_ras_bif_ras_regblk` portion defines BIF RAS central control/status, leaf control/status registers, IOHUB RAS interrupt handling, and RAS virtual-wire state from IOHUB. These masks back reliability diagnostics and error-signaling code rather than normal data-path configuration.

### PF0 PCI Configuration Space

The chunk begins the `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` block for device 0 endpoint PF0 PCI configuration space. It includes:

- Standard header fields such as vendor ID, device ID, command/status, revision/class codes, cache line, latency, header, BIST, BAR1-BAR6, adapter ID, ROM BAR, capability pointer, interrupt line/pin, minimum grant, and maximum latency.
- Power-management capability fields such as PME support, D-state support, PME enable/status, data select/scale, and power-management state.
- PCIe capability fields for device type, slot/interrupt message number, device capability/control/status, link capability/control/status, and second-generation device/link capability/control/status.
- MSI and MSI-X capability fields for capability lists, enable bits, vector count/control, message address/data, mask/pending state, table BIR/offset, and PBA BIR/offset.
- Vendor-specific enhanced capability fields and scratch registers.
- PCIe virtual-channel enhanced capability, port VC capability/control/status, and VC0/VC1 resource capability/control/status fields.

The range ends on the `BIF_CFG_DEV0_EPF0_0_PCIE_DEV_SERIAL_NUM_ENH_CAP_LIST` comment. Its actual `CAP_ID`, `CAP_VER`, and `NEXT_PTR` field macros are outside this chunk.

## Control Flow and State Behavior

There is no runtime control flow in this file. The header influences compiled driver behavior by defining how other C code shifts, masks, sets, clears, and reads hardware register fields.

The persistent state described here lives in hardware registers, not in this header. Important state includes per-function DMA transaction attribute policy, PASID checking state, SDP disconnect policy, performance counter enables/selectors/counts, sticky error-log bits, virtual-wire change state, clock/power gating policy, reset and interrupt mask/status bits, RAS status bits, and PF0 PCI configuration/capability state.

Several fields are not ordinary durable configuration values. Error-log clear bits, PASID error clear bits, reset strobes, virtual-wire triggers, performance-counter resets, FLR/D3hot reset controls, interrupt clear/status bits, and PCIe control bits such as `INITIATE_FLR` have command or side-effect semantics. Callers must use the sequencing, polling, and timeout rules implemented by the owning NBIO/PCIe/AMDGPU paths; the macros alone do not encode ordering.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header convention:

- `nbio_7_4_offset.h` provides register offsets and base-index definitions corresponding to these field names.
- `nbio_7_4_default.h` provides reset/default values where generated.
- Common AMDGPU bitfield helpers consume the `__SHIFT` and `_MASK` names to avoid hard-coded bit positions.

Likely integration points in the driver tree include:

- NBIO 7.4 initialization, suspend/resume, reset, and interrupt code that programs BIF reset, D-state, power, clock-gating, virtual-wire, and RCC PFC state.
- PCIe capability and error-handling paths that inspect or update PF0 command/status, link status, MSI/MSI-X, virtual-channel, advanced capability, and FLR-related fields through MMIO or PCI config access helpers.
- PASID/KFD/IOMMU integration paths that depend on PASID check/status and PASID error log/clear fields.
- RAS and diagnostics paths that consume BIF RAS central/leaf status and atomic/DMA/PASID error logs.
- Performance/debug paths that enable, reset, select, and read the BIFC MMIO/DMA counters.
- Virtualization/SR-IOV-adjacent flows that must keep per-function masks, PF/VF reset status, and PCIe function-specific state separated.

## Risks

- The chunk starts mid-register: `BIFC_DMA_ATTR_OVERRIDE_DEV0_F0_F1` shift macros are in the previous chunk, while its masks begin here. Any generated documentation or tooling must merge adjacent chunks before treating that register as complete.
- The chunk ends at a register comment. `BIF_CFG_DEV0_EPF0_0_PCIE_DEV_SERIAL_NUM_ENH_CAP_LIST` is mentioned but its fields are not included in this range.
- Many groups repeat nearly identical layouts across functions F0-F7. Copying a mask between functions without preserving the encoded bit positions can silently target the wrong PCIe function.
- Clear, reset, trigger, and strobe fields have side effects. Read-modify-write code must not accidentally set upper-half clear bits or reset bits while updating unrelated fields.
- PCIe configuration fields mirror standardized PCI/PCIe capability layout, but this generated header is ASIC-specific. Cross-generation NBIO headers can expose similar names with different offsets, defaults, or supported bits.
- Some fields touch low-level ordering, no-snoop, relaxed-ordering, PASID, VC, MSI/MSI-X, link, reset, and power behavior. Incorrect programming can cause data ordering bugs, lost interrupts, failed FLR/D-state transitions, link errors, or hidden RAS diagnostics.

## Test Signals

Useful validation for code using these macros includes:

- Compile coverage for NBIO 7.4 sources that include `nbio_7_4_sh_mask.h`, especially code using `REG_SET_FIELD`/`REG_GET_FIELD` with fields in this chunk.
- Boot and GPU probe logs showing successful NBIO discovery, PCIe capability setup, MSI/MSI-X enablement, and absence of unexpected BIF reset, D-state, or power interrupt status.
- Suspend/resume and runtime power-management tests that preserve RCC PFC sticky restore state, virtual-wire behavior, LCLK clock-gating/deep-sleep settings, and PF D-state values.
- FLR and PCI reset tests that exercise per-PF FLR/D3hot-D0 reset controls and verify matching interrupt status/mask behavior.
- RAS/error-injection or fault-observation tests that confirm atomic, DMA MP4, PASID, and BIF RAS status bits latch and clear as expected.
- PASID/KFD workload tests that run with PASID checking enabled and verify no unexpected PASID status/error logs.
- Performance/debug tests that enable and reset BIFC MMIO/DMA counters, then confirm counter registers increment for matching traffic.
- PCIe link and capability inspection through kernel logs or config-space reads, checking device/link capability/control/status, MSI/MSI-X table/PBA fields, and VC resource negotiation where supported.

### subset-b-003237: lines 26924-29367

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 26924-29367

## Purpose

This chunk is part of the generated NBIO 7.4 register shift/mask header used by the AMDGPU driver. It does not define executable logic; it defines C preprocessor constants that describe bit positions and masks for PCIe configuration-space registers behind NBIO/BIF. The range covers the tail of `BIF_CFG_DEV0_EPF0_0` extended PCIe capability fields, a large AMD GPU IOV vendor-specific capability block, and the beginning of the `BIF_CFG_DEV0_EPF1_0` PCI configuration block.

The definitions are intended to be paired with register address constants from `nbio_7_4_offset.h` and register access helpers such as `RREG32_PCIE`, `WREG32_PCIE`, `REG_GET_FIELD`, `REG_SET_FIELD`, and `WREG32_FIELD15`. Consumers include `drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c` and power-management code that include `nbio/nbio_7_4_sh_mask.h`.

## Macro API Surface

Every register field follows the generated naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of the field.
- `<REGISTER>__<FIELD>_MASK` gives the already-positioned mask.

The important register groups in this chunk are:

- EPF0 PCIe extended capabilities: device serial number, Advanced Error Reporting, Resizable BAR, power budgeting, Dynamic Power Allocation, Secondary PCIe Capability, ACS, ATS, Page Request Interface, PASID, Multicast, Latency Tolerance Reporting, ARI, SR-IOV, TPH requester, Data Link Feature, 16 GT/s PHY, lane margining, VF Resizable BAR, and AMD GPU IOV vendor-specific capability registers.
- EPF0 lane arrays: lane equalization controls for lanes 0-15, 16 GT/s per-lane preset controls for lanes 0-15, and margining control/status pairs for lanes 0-15. These repeated definitions have consistent field layouts, so driver code can use one lane's field names as the template for hardware documentation checks, while still needing exact per-lane macro names for generated register access.
- EPF0 GPU IOV vendor-specific registers: interrupt enable/status bits, reset control, HV/VM mailbox dwords, context, total framebuffer, offsets, P2P-over-XGMI enable, per-VF framebuffer size/offset entries for VF0-VF30, and scheduler state dwords for UVD, VCE, GFX, and UVD1.
- EPF1 PCI configuration registers: vendor/device IDs, command/status, class/revision/header/BIST, BARs, subsystem IDs, ROM base, interrupt line/pin, vendor capability, power-management capability, PCIe capability, device/link capabilities and controls, MSI/MSI-X, vendor-specific enhanced capability, and virtual-channel capability/resource controls.

There are no functions, structs, enums, or storage declarations in this chunk. The public interface is the macro namespace itself.

## Control Flow and Data Flow

This header has compile-time data flow only. The macros are expanded by C code that performs MMIO, PCIe config-space, or SOC15 register operations. Typical usage is:

1. A consumer includes `nbio_7_4_offset.h` for an address and this file for field metadata.
2. The consumer reads a register through an AMDGPU register helper.
3. It extracts or updates a field using the matching `__SHIFT` and `_MASK` constants, often indirectly through `REG_GET_FIELD` or `REG_SET_FIELD`.
4. It writes the modified value back to the hardware register.

`nbio_v7_4.c` includes this header alongside `nbio_7_4_offset.h` and `nbio_7_4_0_smn.h`. In that file, the same generated-mask pattern is used to program NBIO doorbell ranges, memory-controller access, PCIe light sleep, LTR enablement, and RAS-related paths. This particular chunk provides field metadata for many PCIe capability registers that may be read by diagnostic, virtualization, reset, error-reporting, and platform-configuration code even when there is no direct reference in `nbio_v7_4.c`.

## State and Persistence Behavior

The macros do not store state. The underlying registers do:

- AER status/mask/severity fields represent PCIe error state and policy, including correctable and uncorrectable error categories such as DLP, completion timeout, malformed TLP, ECRC, unsupported request, ACS violation, and TLP prefix blocked errors.
- Link, equalization, 16 GT/s, and margining fields reflect or request physical-link training behavior. Some fields are status-only from the driver perspective, while control fields can trigger equalization or margining operations.
- ACS, ATS, PRI, PASID, ARI, SR-IOV, MSI, MSI-X, and VC registers affect PCIe isolation, address translation, virtualization, interrupts, and traffic-class mapping. These settings persist in hardware until reset or rewritten by firmware/driver/platform code.
- GPU IOV fields describe virtualization-visible state: interrupt enables/status, reset notification/control, host/guest mailbox payloads, per-VF framebuffer layout, active context, total framebuffer accounting, and scheduler dwords. These are hardware/firmware coordination registers rather than Linux-owned persistent software state.

Because this is PCIe/NBIO hardware state, writes can have device-wide effects, especially for SR-IOV, PASID/PRI/ATS, ACS, MSI/MSI-X, and VC resource controls.

## Dependencies and Integration Points

Primary dependencies:

- `nbio_7_4_offset.h`: supplies the register addresses that correspond to these masks.
- AMDGPU register helpers and field helpers: `RREG32*`, `WREG32*`, `REG_GET_FIELD`, `REG_SET_FIELD`, and SOC15 register-offset helpers.
- PCIe configuration semantics: the bit layouts mirror PCIe capability structures, AER, SR-IOV, MSI/MSI-X, ATS/PRI/PASID, VC, and extended capability headers.
- Firmware/hypervisor interfaces for GPU IOV: mailbox, reset, scheduler, and VF framebuffer layout fields are meaningful only with the matching firmware/virtualization contract.

Notable integration signals from the tree:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c` includes this header directly and uses the NBIO 7.4 register/mask pattern for device bring-up and runtime configuration.
- SMU powerplay files for Arcturus/Aldebaran also include this mask header, so PCIe/NBIO fields may be used by power-management or platform feature code.
- Similar GPUIOV definitions appear in other NBIO generations, which suggests this chunk is generated from a common hardware register database and should remain synchronized with offsets and other ASIC-specific headers.

## Risks

- Mask/address mismatch: these field masks must match the paired `nbio_7_4_offset.h` addresses. A mismatch can silently update the wrong bit field in hardware.
- Width and reserved-bit handling: many registers contain reserved fields or full-width scratch/mailbox dwords. Driver writes must preserve unrelated bits unless the hardware spec says a full write is safe.
- Virtualization safety: SR-IOV, GPU IOV, PASID, PRI, ATS, ACS, and VF BAR layout fields can affect isolation between PF/VF contexts and between DMA address spaces.
- Error-reporting side effects: AER status bits may be write-one-to-clear or otherwise side-effectful depending on the register. Code must not treat masks as ordinary RAM bitfields without checking the PCIe register semantics.
- Repeated lane definitions: lane 0-15 equalization and margining layouts are repetitive, but copy/paste or generated-name errors can target the wrong lane and make link training failures hard to diagnose.
- Capability-list pointer fields must remain coherent with actual config-space layout. Incorrect `NEXT_PTR`, capability ID, or version interpretation can break capability walking.

## Test Signals

Useful validation signals for changes touching this chunk or its consumers:

- Compile coverage for AMDGPU with NBIO 7.4 ASIC support enabled; missing or renamed macros should fail at build time.
- Static checks that every used mask macro has a matching shift macro and that masks align with shifts for contiguous fields.
- Runtime PCIe bring-up on NBIO 7.4 devices, especially Arcturus/Aldebaran-class paths that include this header.
- SR-IOV smoke tests: PF load, VF enumeration, VF BAR assignment, reset notification, and mailbox behavior.
- PCIe AER tests or fault-injection where available: verify correctable/uncorrectable status, mask, and severity handling.
- Link-training diagnostics: negotiated speed/width, 8 GT/s and 16 GT/s equalization status, margining readiness/status, and absence of unexpected AER errors after link events.
- Interrupt tests for MSI/MSI-X enablement and vector masking on EPF1 paths.

## Chunk Boundary Notes

The chunk starts immediately after the EPF0 device-serial-number enhanced-capability list field definitions and ends in the middle of `BIF_CFG_DEV0_EPF1_0_PCIE_VC1_RESOURCE_CNTL`. The following chunk is needed to complete EPF1 VC1 resource control and any subsequent EPF1/EPF block definitions. Whole-file reconciliation should merge this with adjacent chunks to describe the complete NBIO 7.4 mask header.

### subset-b-003238: lines 29368-31801

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 29368-31801

## Scope

This chunk covers generated shift and mask macros for a portion of the AMD NBIO 7.4 register bitfield header. It starts in the middle of the `BIF_CFG_DEV0_EPF1_0_PCIE_VC1_RESOURCE_CNTL` field set and continues through:

- EPF1 PCIe extended capability fields: device serial number, Advanced Error Reporting, Resizable BAR, power budgeting, Dynamic Power Allocation, secondary PCIe, ACS, ATS, Page Request Interface, PASID, Multicast, LTR, ARI, SR-IOV, TPH requester, Data Link Feature, 16 GT/s PHY, margining, and VF Resizable BAR capabilities.
- A GPU IOV vendor-specific PCIe capability block for EPF1, including SR-IOV shadow state, interrupt enable/status bits, PF reset control, hypervisor/VF mailbox registers, VF framebuffer partition fields, P2P-over-XGMI enablement, and scheduler data windows for UVD, VCE, GFX, and UVD1 engines.
- The beginning of the `nbio_nbif0_bif_cfg_dev0_epf0_vf0_bifcfgdecp` address block, covering the standard PCI configuration header and PCIe/MSI/MSI-X/VSEC/AER fields for `BIF_CFG_DEV0_EPF0_VF0_0` through the start of its uncorrectable error severity fields.

The file is generated hardware metadata. This range defines preprocessor constants only: there are no C functions, structs, global variables, or executable branches in the chunk.

## Purpose

The purpose of this header section is to provide the bit-level ABI for NBIO 7.4 PCIe configuration-space and vendor-specific registers. Each field appears in the normal AMD register-header form:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset of the field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to extract or compose the field.

Driver code pairs these definitions with register addresses from `nbio_7_4_offset.h` and with AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, indirect PCI config access helpers, or SR-IOV-specific PF/VF register accessors. The macros let code refer to PCIe capability fields symbolically rather than hard-coding bit positions.

## Important Macro Families

### EPF1 PCIe Capability and Error Reporting Fields

The first part of the chunk completes EPF1 virtual-channel resource control/status fields, including traffic-class to virtual-channel mapping, port arbitration table load/status, VC ID, VC enable, and negotiation-pending state.

The AER block defines fields for uncorrectable error status, masks, and severity; correctable error status and masks; Advanced Error Capability/Control; header logs; and TLP prefix logs. The covered uncorrectable errors include DLP, surprise down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal errors, MC blocked TLP, atomic operation egress blocked, and TLP prefix blocked. Correctable fields include receiver error, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal, internal correctable error, and header-log overflow.

These macros are important for diagnostics, error masking, severity classification, and kernel AER integration. They describe which bits are status, mask, or severity bits, but the header does not encode clear semantics or ordering.

### BAR, Power, DPA, Link, and Lane Training Fields

The EPF1 extended capability portion includes:

- Device serial number high/low dwords and capability-list headers.
- Resizable BAR capability/control registers for BAR1 through BAR6, exposing supported sizes, BAR index, total BAR count, and selected BAR size.
- Power Budgeting fields for selected data, power budget values, scale, PM sub-state, type, power rail, and system allocation support.
- Dynamic Power Allocation fields for transition latency indicators, substate mask/status/control, and substate power allocations 0 through 7.
- Secondary PCIe capability fields for target link speed and link equalization request.
- Per-lane equalization control for lanes 0 through 15, with downstream/upstream TX presets and RX preset hints.

These fields back PCIe link training, power reporting, and BAR sizing behavior exposed to the OS or configured by firmware/driver policy.

### ACS, ATS, PRI, PASID, MC, LTR, ARI, and SR-IOV

The chunk describes several PCIe capabilities that matter for IOMMU, peer-to-peer routing, and virtualization:

- ACS capability/control fields cover source validation, translation blocking, P2P request/completion redirect, upstream forwarding, P2P egress control, direct translated P2P, and egress vector size.
- ATS fields expose invalidate queue depth, page-aligned/global invalidate support, smallest translation unit, and ATC enable.
- PRI fields expose PRI enable/reset, response failure, unexpected page-request group index, stopped state, PASID-required response state, outstanding page-request capacity, and allocation.
- PASID fields expose execute permission support, privileged-mode support, maximum PASID width, and enable bits.
- Multicast fields expose group count, window size requirement, ECRC regeneration support, receive/block bitmaps, and block-untranslated bitmaps.
- LTR fields expose snooped and non-snooped maximum latency values and scales.
- ARI fields expose function-group capabilities, next function number, enable bits, and function group selection.
- SR-IOV fields expose migration support, ARI hierarchy preservation, VF ten-bit tag support, VF enable, VF MSE, migration interrupt enable/status, initial/total/active VF counts, function dependency link, first VF offset, VF stride, VF device ID, supported/system page size, six VF BAR base registers, and migration state array offset/BIR.

These macros are consumed by PF-side setup, virtualization flows, and PCI core interactions. They are especially sensitive because they help define isolation boundaries, address translation behavior, and how VF configuration space is presented.

### TPH, Data Link Feature, 16 GT/s PHY, and Margining

The TPH requester capability fields include no-ST mode, interrupt/vector mode, device-specific mode support, extended TPH requester support, ST table location/size, ST mode selection, and requester enable.

The Data Link Feature capability/status fields expose local feature support bits and remote feature support/valid bits for scaled flow control and the data link feature exchange path.

The 16 GT/s PHY capability group includes equalization bypass, modified TS usage, retimer presence flags, 10-bit tag completeness, 16 GT/s data-rate signaling enablement, equalization complete/phase-success status, link-down reason, local and retimer parity mismatch status, and per-lane 16 GT/s downstream/upstream EQ control for lanes 0 through 15.

The margining block exposes port capability/status plus lane margining control/status for lanes 0 through 15. Each lane has receiver number, margin type, usage model, and payload fields, with matching status fields. These fields are integration points for PCIe signal-integrity diagnostics and link qualification rather than normal data-path programming.

### VF Resizable BAR and GPUIOV Vendor-Specific Capability

The VF Resizable BAR capability covers VF BAR1 through VF BAR6 supported sizes and selected sizes. This mirrors the PF BAR sizing concepts but applies to VF BAR windows.

The `BIF_CFG_DEV0_EPF1_0_PCIE_VENDOR_SPECIFIC_*_GPUIOV` block is AMD-specific virtualization surface:

- Capability-list and VSEC header fields expose capability ID, version, next pointer, VSEC ID, revision, and VSEC length.
- `SRIOV_SHADOW` exposes shadowed `VF_EN` and `VF_NUM`.
- Interrupt enable/status fields cover GFX, UVD, UVD1, and VCE command-complete, self-recovered hang, hang requiring FLR, and VM-busy transition events, plus hypervisor/VF mailbox transmit-ack and receive-valid events.
- `RESET_CONTROL` provides `SOFT_PF_FLR`.
- `HVVM_MBOX_DW0` through `DW2` define a PF/hypervisor and VF mailbox: VF index, transmit data/valid, receive data/ack, and per-VF transmit-ack/receive-valid bits for VF0 through VF31.
- `CONTEXT`, `TOTAL_FB`, `OFFSETS`, `P2P_OVER_XGMI_ENABLE`, and `VF0_FB` through `VF30_FB` describe VF context size/location, total framebuffer size, offset granularity, P2P-over-XGMI enablement, and per-VF framebuffer size/offset pairs.
- Scheduler dword windows for `UVDSCH`, `VCESCH`, `GFXSCH`, and `UVD1SCH` expose opaque 32-bit scheduler payload slots.

This block is one of the highest-risk areas in the chunk because it controls PF/VF coordination, partition metadata, mailbox signaling, engine scheduling metadata, and reset behavior for GPU virtualization.

### EPF0 VF0 PCI Configuration-Space Fields

Near line 31244 the chunk starts the `BIF_CFG_DEV0_EPF0_VF0_0` address block. It defines field masks for a VF's conventional PCI configuration header and the first capability structures:

- Vendor/device ID, command, status, revision/interface/class, cache line, latency, header type, BIST, BAR1 through BAR6, adapter ID, ROM base, capability pointer, interrupt line, and interrupt pin.
- PCIe capability list, PCIe capability register, device capability/control/status, link capability/control/status, device capability/control/status 2, link capability/control/status 2, and reserved slot capability/control/status 2 fields.
- MSI and MSI-X capability list/control/address/data/mask/pending/table/PBA fields.
- Vendor-specific capability header and scratch fields.
- The beginning of AER for VF0, including uncorrectable error status, mask, and the start of severity definitions.

This mirrors much of the EPF1 capability layout but is scoped to `EPF0_VF0_0`, the first virtual function under endpoint function 0.

## Control Flow and State Behavior

This header has no runtime control flow. It affects compiled driver behavior by defining how C code packs and unpacks 16-bit and 32-bit PCIe configuration register values.

The state represented by these macros lives in hardware configuration space or NBIO-side register windows. Some fields are persistent configuration bits, such as BAR sizes, ACS/ATS/PASID/SR-IOV enables, MSI/MSI-X enables, link controls, and interrupt masks. Others are status or diagnostic fields, such as AER status, link status, data link feature status, lane error status, equalization status, margining status, GPUIOV interrupt status, mailbox ack/valid state, and VF migration status. Some are command-like or reset-oriented fields, such as PRI reset, link equalization request, `SOFT_PF_FLR`, and mailbox valid/ack bits.

The macros do not describe sequencing. Users must follow the PCIe specification, AMDGPU PF/VF ownership rules, and the code paths that own the relevant capability. For example, enabling ATS/PASID/PRI is only useful when the IOMMU and driver memory-management paths are ready; SR-IOV VF enablement must be coordinated with BAR sizing and VF framebuffer partitioning; GPUIOV mailbox bits require valid/ack handshakes; and AER status handling requires the correct clear/mask semantics.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header set:

- `nbio_7_4_offset.h` supplies addresses such as `cfgBIF_CFG_DEV0_EPF1_0_PCIE_SRIOV_CONTROL`, `cfgBIF_CFG_DEV0_EPF1_0_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV`, and the surrounding `cfgBIF_CFG_DEV0_EPF0_VF0_0_*` registers.
- `nbio_7_4_default.h`, where present, supplies reset/default values for corresponding NBIO registers.
- AMDGPU SOC15 and PCI config access helpers consume these `__SHIFT` and `_MASK` macros through `REG_SET_FIELD`, `REG_GET_FIELD`, and related helpers.

Important integration points include:

- AMDGPU NBIO initialization and reset code, which includes NBIO generation-specific offset/mask headers to program PCIe, doorbell, interrupt, and power-management-facing registers.
- AMDGPU SR-IOV and virtualization code, especially PF-controlled paths that expose VFs, size VF BARs, set VF memory apertures, process GPUIOV mailbox events, trigger FLR/reset flows, or route GFX/UVD/UVD1/VCE virtualization interrupts.
- Linux PCI and IOMMU-facing behavior for ACS, ATS, PRI, PASID, ARI, MSI, MSI-X, AER, LTR, Resizable BAR, and SR-IOV capabilities.
- Diagnostic and validation paths that inspect PCIe link equalization, 16 GT/s PHY status, lane margining, data link feature exchange, and AER logs.

Cross-generation similarity is high, but these definitions must stay paired with NBIO 7.4 offsets. Older NBIO headers expose similar capability names with different line positions or possibly different field availability, and newer headers may add or remove vendor-specific virtualization fields.

## Risks

- Bitfield drift can corrupt PCIe configuration behavior. A wrong shift or mask can silently program adjacent capability bits, misreport features, break enumeration, or alter link state.
- AER definitions are safety-critical for diagnostics. Incorrect status, mask, or severity fields can hide real PCIe faults, over-report errors, or misclassify fatal/non-fatal events.
- ACS/ATS/PRI/PASID mistakes can affect address translation and isolation. Enabling the wrong bits before IOMMU and driver setup is complete can lead to DMA faults or security-sensitive routing behavior.
- SR-IOV and GPUIOV fields are privilege-sensitive. Incorrect VF counts, strides, BAR sizes, framebuffer offsets, mailbox indexing, interrupt enables, or `SOFT_PF_FLR` handling can break PF/VF isolation, reset the wrong function, lose mailbox events, or expose invalid framebuffer ranges.
- Repeated lane and VF families are mechanically fragile. Lane equalization, lane margining, VF BAR, per-VF mailbox, and per-VF framebuffer macros are repetitive; copy-generation errors are easy to miss because names differ only by lane or VF number.
- Link training and margining fields require hardware-specific sequencing. Treating status fields as controls or issuing equalization/margining changes without the required polling can destabilize a PCIe link.
- The chunk starts and ends mid-family. `BIF_CFG_DEV0_EPF1_0_PCIE_VC1_RESOURCE_CNTL` begins before this chunk, and `BIF_CFG_DEV0_EPF0_VF0_0_PCIE_UNCORR_ERR_SEVERITY` continues after it. The final merged report must stitch those adjacent fields together.

## Test and Validation Signals

Useful validation signals are mostly integration and hardware bring-up tests:

- Build coverage for AMDGPU files that include `nbio/nbio_7_4_sh_mask.h`, paired with `nbio_7_4_offset.h`, catches missing or renamed generated macros.
- PCI enumeration tests should verify VF0 config header fields, BAR sizing, capability-list chaining, MSI/MSI-X capability decoding, and SR-IOV capability layout.
- AER tests should inject or observe correctable and uncorrectable PCIe errors and confirm status, mask, severity, header log, and TLP prefix log decoding.
- IOMMU and peer-to-peer tests should exercise ACS, ATS, PRI, PASID, ARI, and multicast-related behavior under real DMA workloads.
- SR-IOV validation should create/destroy VFs, verify VF counts/stride/device ID/page size/VF BARs, confirm per-VF framebuffer size/offset programming, and check FLR/reset behavior.
- GPUIOV tests should cover mailbox transmit/receive valid and ack transitions, per-VF mailbox bits for VF0 through VF31, virtualization interrupt enable/status bits for GFX/UVD/UVD1/VCE, and P2P-over-XGMI enablement where supported.
- PCIe link tests should validate equalization, 16 GT/s status, data link feature status, lane error status, and margining payload/status behavior across supported link widths.

## Unresolved Cross-Chunk References

The source range begins after the `BIF_CFG_DEV0_EPF1_0_PCIE_VC1_RESOURCE_CNTL` comment and first field definitions, so the previous chunk owns the start of that register. This range also ends while `BIF_CFG_DEV0_EPF0_VF0_0_PCIE_UNCORR_ERR_SEVERITY` is still being defined, so the next chunk owns the remaining severity fields and following VF0 AER capability definitions.

### subset-b-003239: lines 31802-34237

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 31802-34237

## Purpose

This chunk is an auto-generated AMD NBIO 7.4 register shift/mask slice for PCIe configuration-space fields under `BIF_CFG_DEV0_EPF0`. It contains no executable logic; its job is to expose compile-time constants that NBIO 7.4 consumers can pair with register offsets from `nbio_7_4_offset.h` when decoding or programming PCIe endpoint virtual-function configuration registers.

The selected range starts at the tail of the VF0 Advanced Error Reporting area, then covers full config-space decode blocks for `VF1`, `VF2`, and `VF3`, and begins the `VF4` block through the early `DEVICE_CNTL2` fields. These definitions model standard PCI/PCIe config registers plus MSI/MSI-X, AER, ATS, and ARI capability fields for SR-IOV virtual functions exposed by the GPU's NBIO/PCIe block.

## Public Surface In This Chunk

The public surface is preprocessor-only:

- 2,436 source lines in the assigned range.
- 2,138 `#define` lines.
- 1,067 `__SHIFT` definitions.
- 1,176 `_MASK`-bearing definitions.
- 290 generated register-comment or address-block comment lines.

Macro names follow the generated convention:

- `BIF_CFG_DEV0_EPF0_VF<n>_0_<REGISTER>__<FIELD>__SHIFT` gives a field's low bit position.
- `BIF_CFG_DEV0_EPF0_VF<n>_0_<REGISTER>__<FIELD>_MASK` gives the pre-shifted field mask.
- Names such as `*_ERR_MASK__DLP_ERR_MASK_MASK` are intentional: the hardware register is itself an error-mask register, so the generated field name also contains `MASK`.

There are no functions, structs, enums, storage objects, inline helpers, or runtime APIs. The ABI is the exact macro name/value set generated from AMD's NBIO 7.4 register database.

## Register Coverage

The VF0 portion continues from the previous chunk and covers the end of AER for `BIF_CFG_DEV0_EPF0_VF0_0`:

- Correctable error status/mask bits for receiver errors, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal, internal correctable error, and header-log overflow.
- AER capability/control fields for first error pointer, ECRC generation/checking capability and enable bits, multiple-header recording, TLP-prefix logging, and completion-timeout logging.
- Header log and TLP prefix log dwords.
- ATS enhanced-capability header, ATS capability, and ATS control.
- ARI enhanced-capability header, ARI capability, and ARI control.

The VF1, VF2, and VF3 blocks are complete virtual-function config-space maps in this range. Each block includes:

- Conventional PCI identity and command/status fields: vendor/device ID, command enables, status flags, revision/class/program interface, cache line, latency, header type, BIST, six BARs, subsystem IDs, ROM BAR, capability pointer, and interrupt line/pin.
- PCIe capability fields: PCIe capability header, device/link capability, control, and status, plus capability/control/status 2 groups.
- MSI and MSI-X capability fields: enable bits, multi-message fields, 64-bit and per-vector masking support, message address/data, mask and pending vectors, MSI-X table/PBA BIR and offsets, table size, function mask, and global enable.
- Vendor-specific enhanced capability fields with VSEC header and scratch dwords.
- AER enhanced capability fields: uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, header logs, and TLP prefix logs.
- ATS and ARI enhanced-capability groups with capability-list metadata and enable/control bits.

The VF4 block begins in this chunk and covers identity/config basics through part of PCIe device control 2:

- Conventional PCI identity, command/status, class/revision, BAR, subsystem, ROM, interrupt, PCIe capability, device/link capability/control/status, and early device capability 2 fields.
- The range ends mid-`BIF_CFG_DEV0_EPF0_VF4_0_DEVICE_CNTL2`, after fields such as completion timeout control, ARI forwarding, atomic request/egress behavior, ID-based ordering, LTR enable, and emergency power reduction request have begun. The remaining VF4 device-control-2 masks and later VF4 capability groups are in the following chunk.

## Important Fields And Semantics

The conventional PCI fields gate host-visible access for each VF. `COMMAND` fields control I/O access, memory access, bus mastering, parity/SERR reporting, and interrupt disable behavior. `STATUS` fields expose capability-list presence and legacy error indications. BAR and ROM fields describe or decode VF address apertures, while adapter/subsystem fields identify the virtual function to the host.

The PCIe device/link fields advertise and control transport behavior. `DEVICE_CAP` and `DEVICE_CAP2` expose payload size support, extended tags, FLR capability, completion-timeout support, ARI forwarding support, atomic operations, LTR, OBFF, 10-bit tags, TLP prefixes, and emergency power reduction support. `DEVICE_CNTL` and `DEVICE_CNTL2` enable error reporting, relaxed ordering, no-snoop, maximum payload/read request sizes, FLR, completion-timeout policy, ARI forwarding, atomics, ID-based ordering, LTR, OBFF, and prefix blocking.

The link fields describe negotiated PCIe link state for each VF's config view: supported/current link speed, link width, ASPM/PM support, exit latencies, clock power management, surprise-down/data-link-active reporting, bandwidth notification capability, retrain/link-disable controls, target link speed, compliance controls, de-emphasis, equalization status, crosslink status, and downstream presence.

The MSI/MSI-X fields drive interrupt routing for virtual functions. MSI macros expose enablement, number of messages, 64-bit addressing, per-vector masking, address/data payloads, mask vectors, and pending vectors. MSI-X macros expose table size, enable/function mask bits, table BIR/offset, and PBA BIR/offset. Misdecoding these fields can break VF interrupt delivery or isolation.

The AER fields define how PCIe errors are captured and classified. Uncorrectable status/mask/severity fields cover DLP, surprise down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal errors, multicast blocked TLP, atomic egress blocking, and TLP prefix blocking. Correctable fields cover receiver errors, bad TLP/DLLP, replay issues, advisory non-fatal, internal correctable errors, and header-log overflow. Header and prefix logs are full-register payload fields used for post-error diagnosis.

ATS and ARI capability groups expose virtualization and address-translation controls. ATS fields advertise invalidate queue depth, page-aligned request support, global invalidation, STU, and ATC enable. ARI fields advertise function grouping and next-function metadata and allow MFVC/ACS function-group enablement and function-group selection.

## Control Flow And State

There is no runtime control flow in this header. The effective flow is compile-time substitution:

1. NBIO 7.4-aware code includes `nbio/nbio_7_4_sh_mask.h` and the matching `nbio/nbio_7_4_offset.h`.
2. A caller selects a config-space offset such as `cfgBIF_CFG_DEV0_EPF0_VF1_0_COMMAND`, `cfgBIF_CFG_DEV0_EPF0_VF2_0_LINK_STATUS`, `cfgBIF_CFG_DEV0_EPF0_VF3_0_PCIE_UNCORR_ERR_STATUS`, or `cfgBIF_CFG_DEV0_EPF0_VF4_0_DEVICE_CNTL2`.
3. The caller uses these `__SHIFT` and `_MASK` constants through AMD's register helper macros or open-coded bit operations to extract, preserve, insert, or compare fields.
4. The actual access occurs through PCI config-space, MMIO, indirect PCIE access, firmware-mediated paths, or debug/register-dump logic outside this header.

The header stores no software state and persists nothing by itself. Persistent state lives in hardware config registers and may be owned by the host PCI core, AMDGPU, firmware, a hypervisor, or hardware state machines depending on platform mode. Control fields persist until reset, FLR, VF teardown/recreation, power transition, link retrain, or explicit reprogramming. Status, log, pending, and error fields may be hardware-updated, sticky, write-one-to-clear, or read-only according to the PCIe spec and AMD hardware rules.

## Dependencies And Integration Points

The direct generated-header dependency is `drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_offset.h`. The matching offset header defines the config addresses for the same register names; for example, `cfgBIF_CFG_DEV0_EPF0_VF<n>_0_COMMAND` at `0x0004`, `LINK_STATUS` at `0x0076`, `DEVICE_CNTL2` at `0x008c`, `PCIE_UNCORR_ERR_STATUS` at `0x0154`, `PCIE_ATS_CNTL` at `0x02b6`, and `PCIE_ARI_CNTL` at `0x032e` for VF0 through VF4.

NBIO 7.4 mask include sites in this source tree include `amdgpu/nbio_v7_4.c`, SMU power-management files for Arcturus/Aldebaran/SMU 13.0.6, and Vega20 PowerPlay code. A repository search did not find direct in-tree references to the long `BIF_CFG_DEV0_EPF0_VF<n>_0_*` macro names in AMDGPU/PM C files, which indicates this range is mostly generated register ABI surface for config decoders, diagnostics, future feature code, or paths not using these full macro names directly.

Semantic dependencies include the PCI and PCI Express configuration-space specifications plus the PCIe extended capabilities represented here: MSI, MSI-X, AER, ATS, ARI, LTR, OBFF, atomic operations, completion timeout, end-to-end TLP prefixes, and VF function-level reset. For virtualization, these fields also integrate with Linux PCI SR-IOV enumeration, hypervisor-managed VF lifecycle, VF BAR sizing/mapping, interrupt remapping, and AMDGPU firmware/PSP/SMU policy where those components configure or virtualize PCIe state.

## Risks And Maintenance Notes

- The assigned range starts and ends mid-context: it begins after part of VF0 AER severity and ends inside VF4 `DEVICE_CNTL2`. Adjacent chunks are required for a complete VF0 and VF4 view.
- Prefixes are not interchangeable. `VF1`, `VF2`, `VF3`, and `VF4` macros have repeated register names and often identical numeric masks, but they must be paired with the matching `cfgBIF_CFG_DEV0_EPF0_VF<n>_0_*` offset and function context.
- Generated names with doubled `MASK` are valid and should not be "cleaned up" manually.
- Full-width `0xFFFFFFFFL` masks identify whole-register BARs, addresses, logs, scratch registers, masks, pending vectors, or payload dwords; they do not imply all bits are writable or safe to set.
- AER status/severity/mask errors can change driver-visible fault classification, hide real hardware faults, or turn non-fatal conditions into fatal paths.
- MSI/MSI-X field mistakes can break VF interrupt delivery, vector masking, pending-bit handling, or isolation between functions.
- ATS and ARI control bits affect address translation and function routing. Incorrect decoding can cause IOMMU/PRI/ATS failures or cross-function behavior in virtualized deployments.
- PCIe link-control fields can trigger retraining, compliance behavior, power-management changes, or bandwidth notification state; consumers must preserve reserved bits and respect hardware sequencing.
- The header does not encode access width, reset value, read/write permissions, sticky/W1C behavior, firmware ownership, or side effects. Those rules must come from the PCIe spec, AMD register documentation, and surrounding driver code.

## Test Signals

Useful validation signals for this chunk are:

- Compile coverage for NBIO 7.4 include sites: `amdgpu/nbio_v7_4.c`, Arcturus/Aldebaran/SMU 13.0.6 power-management files, and Vega20 PowerPlay code.
- Generated-header consistency checks that every register represented here has the corresponding `cfgBIF_CFG_DEV0_EPF0_VF<n>_0_*` offset in `nbio_7_4_offset.h`.
- Static validation that masks fit the intended PCI config register widths and match their shifts, especially 8-bit identity/class fields, 16-bit command/status/link fields, and 32-bit AER/log/BAR fields.
- Hardware or simulator config-space dumps for VF1 through VF4 decoded with these masks and compared with `lspci -vvxxx`-style PCIe capability output.
- SR-IOV bring-up tests that create VFs, enumerate them, map BARs, issue FLR, and confirm command/status, device/link, MSI/MSI-X, ATS, and ARI fields decode consistently per VF.
- PCIe AER injection or fault-reporting tests that verify correct uncorrectable/correctable status bits, mask behavior, severity handling, first-error pointer, ECRC controls, header logs, and TLP-prefix logs.
- Interrupt tests that exercise MSI and MSI-X enablement, vector masking, pending bits, table/PBA offsets, and per-VF isolation.
- ATS/ARI virtualization tests with IOMMU enabled, checking ATC enablement, STU handling, invalidate support, ARI forwarding/function grouping, and absence of cross-VF leakage.

### subset-b-003240: lines 34238-36659

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 34238-36659

## Scope

This chunk covers a generated section of AMDGPU's NBIO 7.4 shift/mask header for PCIe configuration-space fields under `BIF_CFG_DEV0_EPF0` virtual-function address blocks. It starts in the middle of `BIF_CFG_DEV0_EPF0_VF4_0_DEVICE_CAP2`: the first lines in this chunk are the tail of the `DEVICE_CAP2` `__SHIFT` definitions, and the corresponding `DEVICE_CAP2` masks are in this chunk. It then completes the rest of the `VF4_0` PCIe capability and enhanced-capability blocks, covers complete `VF5_0` and `VF6_0` endpoint virtual-function configuration images, and covers `VF7_0` from conventional PCI identity/header registers through AER header log registers. The next chunk continues `VF7_0` with TLP prefix logs and later enhanced capabilities.

The chunk is declarative generated C preprocessor data. It contains no functions, structs, enums, runtime storage, loops, branches, or persistence logic. The public surface is a large set of symbols following the generated AMD register bitfield convention:

- `BIF_CFG_DEV0_EPF0_VF*_0_<REGISTER>__<FIELD>__SHIFT`
- `BIF_CFG_DEV0_EPF0_VF*_0_<REGISTER>__<FIELD>_MASK`

These constants are meant to be paired with register-address definitions from `nbio_7_4_offset.h`.

## Purpose

`nbio_7_4_sh_mask.h` provides the bit layout contract for NBIO 7.4 registers. This slice describes PCI/PCIe configuration fields for SR-IOV-style virtual-function config images on device 0, endpoint function 0, especially VFs 4 through 7. Consumers use the shifts and masks to extract hardware-reported capability/status bits or compose safe read-modify-write values for writable control fields.

The field families in this chunk are standard PCI/PCIe-facing areas: PCI command/status and BAR metadata, PCIe device/link capability and control, MSI/MSI-X interrupt capability registers, vendor-specific enhanced capability headers/payloads, Advanced Error Reporting, Address Translation Services, and Alternative Routing-ID Interpretation. The header does not decide policy for these features; it only names bit positions for code that already knows when and how to touch the registers.

## Major Register Families

### Tail Of `BIF_CFG_DEV0_EPF0_VF4_0`

The `VF4_0` portion begins after `LINK_STATUS`, with `DEVICE_CAP2` and `DEVICE_CNTL2` PCIe capability 2 fields. These define completion-timeout support and control, ARI forwarding support/enable, atomic operation support and request enablement, ID-based ordering enables, LTR support/enable, OBFF support/control, 10-bit tag support/control, end-to-end TLP prefix support/blocking, and emergency power reduction fields.

The remaining `VF4_0` block includes:

- `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` for supported/target link speeds, compliance controls, de-emphasis/transmit margin, autonomous speed disable, 8 GT/s equalization completion and phase success, link equalization request, retimer presence, crosslink status, and downstream component presence.
- Sparse slot capability/control/status 2 registers represented as all-reserved masks.
- MSI and MSI-X capability registers, including capability IDs/next pointers, MSI enable, multi-message capability/enable, 64-bit MSI support, per-vector masking capability, message address/data, mask and pending bitmaps, MSI-X table size, function mask, enable, table BIR/offset, and PBA BIR/offset.
- PCIe vendor-specific enhanced capability list/header plus two 32-bit scratch payload registers.
- PCIe AER capability, uncorrectable status/mask/severity, correctable status/mask, AER capability/control, header logs, and TLP prefix logs.
- ATS capability/control, including invalidate queue depth and small enable/stall fields.
- ARI capability/control, including multifunction/device-function-group capability, next function number, function group, and ACS function group enable.

Because the chunk starts mid-register, whole-register research for `VF4_0_DEVICE_CAP2` must also consult the previous chunk for the earliest `DEVICE_CAP2` shift definitions.

### Complete `BIF_CFG_DEV0_EPF0_VF5_0` And `VF6_0`

The `VF5_0` and `VF6_0` address blocks are complete in this range and have the same generated shape. Each block starts with conventional PCI configuration header fields:

- Identity and class fields: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, cache-line size, latency timer, header type, and BIST.
- `COMMAND` and `STATUS`: I/O, memory, bus master, special cycle, memory write invalidate, VGA palette snoop, parity response, SERR, fast back-to-back, interrupt disable, interrupt/status and error indication bits, capability-list support, devsel timing, target/master abort, signaled system error, and parity error detection.
- BAR and resource metadata: six base address registers, adapter/subsystem identity, ROM base address, capability pointer, interrupt line, and interrupt pin.

Each full VF block then defines PCIe capability fields:

- `PCIE_CAP_LIST` and `PCIE_CAP` expose PCIe capability ID, next pointer, capability version, device/port type, slot implemented, interrupt message number, and related capability metadata.
- `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` describe maximum payload support, phantom functions, extended tag, endpoint L0s/L1 latency, role-based error reporting, FLR support, corrected/nonfatal/fatal/unsupported request status, AUX power, and pending transaction state.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` describe max speed/width, ASPM and L1 exit latency, clock power management, surprise down and DLL active reporting support, link bandwidth notification capability, ASPM enables, read completion boundary, link disable/retrain/common clock/extended sync, negotiated speed/width, training, slot clock, data-link active, and bandwidth status bits.
- Capability 2 and link 2 registers repeat the modern PCIe controls and statuses noted for `VF4_0`.

The interrupt and enhanced-capability tail of each full block mirrors `VF4_0`: MSI/MSI-X, vendor-specific enhanced capability, AER status/mask/severity/control/logs, ATS, and ARI.

### Partial `BIF_CFG_DEV0_EPF0_VF7_0`

The `VF7_0` section is complete from its address-block marker through `PCIE_HDR_LOG3`, but not through the whole virtual-function capability image. It includes the same conventional PCI header, PCIe capability, device/link capability/control/status, MSI/MSI-X, vendor-specific capability, and AER status/mask/severity/control fields as `VF5_0` and `VF6_0`.

The chunk ends exactly at `BIF_CFG_DEV0_EPF0_VF7_0_PCIE_HDR_LOG3__TLP_HDR_MASK`. The subsequent `VF7_0` TLP prefix logs, ATS, ARI, and any later capability definitions are outside this work item.

## Important APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The important interface is the macro namespace itself. Callers normally use these constants through AMDGPU register helpers such as `REG_GET_FIELD` and `REG_SET_FIELD`, or through explicit mask/shift arithmetic after reading the associated register via NBIO/PCIE register access helpers.

The header is included with `nbio_7_4_offset.h` by NBIO and platform code such as `drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c`, SMU power-management files, PSP files, and display-resource code that needs NBIO 7.4 register definitions. `nbio_v7_4.c` provides the runtime NBIO 7.4 function table for revision ID, memory size, doorbell apertures, interrupt/doorbell ranges, clock gating, RAS interrupt handling, LTR/ASPM programming, and PCIE index/data access. This chunk's VF-specific PCIe config macros are part of the same generated register ABI, even when individual symbols are consumed indirectly by hardware debug, RAS, PCIe, or future enablement paths rather than visibly referenced one by one.

## Control Flow

This header section has no local control flow. Runtime flow belongs to consumers:

1. Select NBIO 7.4 support based on the detected `NBIO_HWIP` version.
2. Use the paired `nbio_7_4_offset.h` symbol for the target `BIF_CFG_DEV0_EPF0_VF*_0_*` register.
3. Read the register through AMDGPU MMIO, SOC15, or PCIe-index/data access paths.
4. Decode fields with the `*_MASK` and `*__SHIFT` constants, usually through `REG_GET_FIELD`.
5. For writable controls, preserve unrelated and reserved bits, insert a shifted field value with the matching mask, and write the register only when the PCIe/NBIO programming sequence allows it.

The runtime flows affected by these definitions include PCIe VF enumeration and configuration visibility, link-state reporting, completion timeout policy, LTR/OBFF and ASPM-adjacent power behavior, MSI/MSI-X interrupt programming, AER diagnostics, ATS enablement, and ARI routing metadata.

## State And Persistence

The macros are compile-time constants and store no state. The state they describe lives in NBIO/PCIe configuration registers for virtual functions.

Capability fields such as vendor/device IDs, class codes, maximum payload support, link speed/width support, MSI/MSI-X table layout, AER capability metadata, ATS queue depth, and ARI multifunction support are generally hardware- or firmware-defined values. Control fields such as PCI command enables, device control, link control, completion timeout disable/value, LTR enable, MSI/MSI-X enable and masking, AER masks/severity, ATS enable/stall, and ARI/ACS function-group enables are writable only where the underlying config-space register permits it. Status fields such as PCI error status, device status, link training/equalization status, MSI pending bits, and AER correctable/uncorrectable status are hardware-updated and can be sticky or write-one-to-clear depending on the PCIe specification and ASIC register rules.

Persistence is therefore hardware-domain-specific. Software does not persist these fields in this header; values may survive until FLR, hot reset, GPU reset, link reset, power-gating transition, suspend/resume, or explicit driver reprogramming depending on the register and platform.

## Dependencies And Integration Points

- Requires exact synchronization with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_offset.h`. A shift/mask macro is only meaningful with the matching `regBIF_CFG_DEV0_EPF0_VF*_0_*` address and base-index definition.
- Integrates with AMDGPU NBIO 7.4 runtime code in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c`, which includes the generated NBIO 7.4 headers and supplies NBIO callbacks selected by `amdgpu_discovery.c` for NBIO IP versions 7.4.x.
- Supports PM/SMU, PSP, display, and legacy powerplay files that include NBIO 7.4 generated headers to access platform-specific NBIO registers.
- Supports PCIe and virtualization-facing functionality: VF config-space exposure, MSI/MSI-X programming, AER/RAS decode, ATS translation services, ARI routing, link capability/status reporting, and power/link policy controls such as LTR, OBFF, and ASPM-adjacent bits.
- Relies on generic AMDGPU register helper conventions; the macros do not define access width, register reset values, write masks, side effects, or sequencing requirements.

## Risks

- Generated-header drift is the main risk. A wrong bit shift or mask silently misdecodes config-space state or writes the wrong field, which can affect VF enumeration, BAR interpretation, PCI command enables, MSI/MSI-X routing, link policy, AER masking, ATS enablement, or ARI routing.
- The chunk boundaries split logical `VF4_0` and `VF7_0` sections. A per-file merge must not treat this chunk as the full source of `VF4_0_DEVICE_CAP2` or the full `VF7_0` enhanced-capability tail.
- Repetition across `VF5_0`, `VF6_0`, and `VF7_0` makes copy/generation mistakes hard to review manually. A single wrong VF number in a macro name would compile but target the wrong config image in source code.
- PCIe status and AER fields have hardware-defined side effects that masks alone do not communicate. Writing a status register as if it were ordinary RAM can clear sticky diagnostics or lose first-error/header-log context.
- Mixed field widths matter. This range contains 8-bit, 16-bit, and 32-bit logical fields in config registers. Consumers must use the access width and read-modify-write discipline required by the register path and hardware documentation.
- Control fields for MSI/MSI-X, ATS, ARI, LTR, OBFF, atomic operations, and completion timeout can alter interrupt delivery, address translation behavior, routing, ordering, and link/power behavior. They should only be modified in established initialization, reset, or policy paths.

## Test Signals

- Build signal: AMDGPU sources that include `nbio_7_4_sh_mask.h` and `nbio_7_4_offset.h` compile without undefined, duplicate, or mismatched macro errors.
- Static generation signal: compare this section against the NBIO 7.4 register database/spec and verify matching offset symbols exist for every `BIF_CFG_DEV0_EPF0_VF4_0`, `VF5_0`, `VF6_0`, and `VF7_0` register covered here.
- PCIe enumeration signal: on hardware using NBIO 7.4.x paths, virtual functions expose plausible vendor/device/class/header/BAR/capability-chain data and do not report corrupted capability pointers.
- Interrupt signal: MSI/MSI-X setup, mask/unmask, pending-bit behavior, table/PBA decoding, and interrupt delivery work for VFs that use these capability images.
- Link/power signal: device/link status, negotiated speed/width, LTR/OBFF-related controls, completion-timeout settings, and equalization status decode consistently with `lspci -vv` style diagnostics and platform logs.
- Error-handling signal: AER/RAS decode reports correct uncorrectable/correctable error bits, masks, severities, first-error pointers, ECRC controls, and header-log contents under fault injection or captured hardware errors.
- Reset/resume signal: FLR, hot reset, GPU reset, suspend/resume, and SR-IOV enable/disable paths restore or reinitialize writable VF PCIe controls without stale MSI/MSI-X, ATS, ARI, AER, or link-control state.

### subset-b-003241: lines 36660-39092

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 36660-39092

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.4 shift/mask header. It contains register-field geometry for NBIF/BIF PCIe configuration-space registers, not executable driver logic. The constants let NBIO 7.4 code combine matching register offsets from `nbio_7_4_offset.h` with bit shifts and masks from this file when decoding or programming hardware registers.

The range starts at the tail of `BIF_CFG_DEV0_EPF0_VF7_0`, covers complete `nbio_nbif0_bif_cfg_dev0_epf0_vf8_bifcfgdecp`, `vf9_bifcfgdecp`, and `vf10_bifcfgdecp` address blocks, then enters `vf11_bifcfgdecp` and stops after `BIF_CFG_DEV0_EPF0_VF11_0_LINK_STATUS2`. These are virtual-function PCI configuration images for device 0, endpoint PF0, virtual functions 8 through 11, plus the final ATS/ARI definitions for VF7.

## Public Surface

The public surface in this slice is generated C preprocessor macros only. There are 2,139 `#define` entries in 282 commented register groups: 1,072 `__SHIFT` constants and 1,067 canonical `_MASK` constants. A broader text search sees additional `_MASK` strings because some hardware fields are themselves named `MASK`, producing valid names such as `MSI_MASK__MSI_MASK_MASK`.

Macro names follow the established AMDGPU generated-register convention:

- `BIF_CFG_DEV0_EPF0_VF8_0_<REGISTER>__<FIELD>__SHIFT` gives the zero-based field bit position.
- `BIF_CFG_DEV0_EPF0_VF8_0_<REGISTER>__<FIELD>_MASK` gives the pre-shifted field mask.
- `VF9_0`, `VF10_0`, and `VF11_0` prefixes repeat the same layout for different virtual-function config images.

There are no functions, structs, typedefs, enums, locks, allocations, or runtime APIs in this chunk. The API contract is exact macro spelling plus numeric shift/mask value.

## Register Coverage

The VF7 tail contains the end of its advanced PCIe capability chain:

- TLP prefix log dwords 0-3.
- ATS enhanced capability list, ATS capability, and ATS control fields, including invalidate queue depth, page-aligned request support, global invalidate support, STU, and ATC enable.
- ARI enhanced capability list, ARI capability, and ARI control fields, including next function number, function-group capabilities, and function-group enables.

The VF8, VF9, and VF10 blocks are complete in this chunk. Each block covers the same virtual-function PCI configuration shape:

- Conventional PCI header fields: vendor ID, device ID, command, status, revision/class-code bytes, cache-line size, latency timer, header type, BIST, six BAR dwords, adapter/subsystem ID, ROM BAR, capability pointer, and interrupt line/pin.
- PCIe capability fields: capability-list header, PCIe capability header, device capability/control/status, link capability/control/status, device capability/control/status 2, link capability/control/status 2, and reserved slot capability/control/status 2 fields.
- Interrupt capabilities: MSI capability-list/header fields, MSI enable/multi-message/64-bit/per-vector-mask controls, MSI message address/data, MSI mask and pending registers, and MSI-X capability, table, and PBA fields.
- Vendor-specific enhanced capability: VSEC capability-list metadata, VSEC header, and two full-width scratch registers.
- Advanced Error Reporting: AER capability list, uncorrectable error status/mask/severity, correctable error status/mask, advanced error capability/control, TLP header logs 0-3, and TLP prefix logs 0-3.
- Translation and routing capabilities: ATS enhanced capability/capability/control and ARI enhanced capability/capability/control.

The VF11 block begins the same layout and reaches through PCIe link status 2:

- PCI identity/header/BAR/capability-pointer fields.
- PCIe device and link capability/control/status groups through `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- MSI, MSI-X, VSEC, AER, ATS, and ARI groups for VF11 are outside this chunk and must be supplied by the next chunk.

## Field Semantics

The command and status fields expose standard PCI control and observation bits: I/O enable, memory enable, bus mastering, SERR, interrupt disable, capability-list presence, abort/error indicators, parity reporting, and interrupt status. The BAR and ROM BAR masks are full-width address payload fields; actual sizing, decode enablement, and access permissions are determined by PCI config semantics and surrounding driver or firmware policy.

The PCIe capability fields describe per-VF protocol support and policy. `DEVICE_CAP` advertises maximum payload, phantom function, extended tag, acceptable latencies, role-based error reporting, slot power fields, and FLR capability. `DEVICE_CNTL` controls error enables, relaxed ordering, payload size, extended tag, no-snoop, read request size, and FLR initiation. `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` describe and control link speed, width, ASPM/PM, retrain/disable, common clock, clock power management, bandwidth-management interrupts, current speed/width, training state, slot clock configuration, and data-link active state.

The capability 2 fields expose newer PCIe behavior: completion timeout policy, ARI forwarding, atomic operation routing/completion support, ID-based ordering, LTR, TPH completer support, ten-bit tags, OBFF, extended format and end-to-end TLP prefix support, emergency power reduction, target link speed, compliance controls, de-emphasis, 8 GT/s equalization status, crosslink state, RTM presence detection, and downstream component presence.

The interrupt sections model MSI and MSI-X config-space structures. MSI fields cover enablement, multiple-message capability/enables, 64-bit message addressing, per-vector masking, address/data payloads, vector masks, and pending bits. MSI-X fields expose table size, function mask, enable bit, and table/PBA BIR and offset fields. These constants only describe bit layout; actual interrupt programming and masking are performed by PCI core, AMDGPU, firmware, or virtualization code elsewhere.

The AER groups expose error-observation and error-policy fields for data link protocol errors, surprise-down, poisoned TLPs, flow-control protocol errors, completion timeout/abort, unexpected completions, receiver overflow, malformed TLPs, ECRC, unsupported requests, ACS violations, internal errors, multicast blocked TLPs, atomic egress blocking, and TLP prefix blocking. Status, mask, and severity registers intentionally share most field names, so the register prefix is critical.

ATS and ARI fields are virtualization and IOMMU relevant. ATS capability/control fields describe invalidation queue depth, page alignment and global invalidate support, smallest translation unit, and ATC enable. ARI fields describe next-function routing and multifunction/ACS function grouping. For these VF-prefixed blocks, misuse can affect virtual function enumeration, request routing, or translated DMA behavior.

## Control Flow and State

There is no control flow in this header. The practical compile-time flow is:

1. An NBIO 7.4 include site includes this generated shift/mask header together with the matching offset header.
2. Driver code chooses a `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` address macro from `nbio_7_4_offset.h`.
3. It uses the corresponding `BIF_CFG_DEV0_EPF0_VF*_0_*__FIELD__SHIFT` and `_MASK` macros with AMDGPU register helpers or direct bit operations.
4. The actual read, write, read-modify-write, polling, or error decode occurs outside this header.

This file stores no software state and persists nothing. The represented state lives in NBIO/BIF PCI configuration-space hardware. Some fields are read-only capability or identity fields, some are writable configuration policy, some are hardware-updated status bits, and some are sticky error/log/pending fields whose clearing rules are defined by PCIe and AMD hardware specifications. Persistence across FLR, VF reset, GPU reset, suspend/resume, BACO, or power-gating transitions is not encoded here.

## Dependencies and Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_offset.h`. For example, this chunk's `BIF_CFG_DEV0_EPF0_VF8_0_VENDOR_ID__VENDOR_ID_MASK` pairs with `cfgBIF_CFG_DEV0_EPF0_VF8_0_VENDOR_ID`, and the VF11 link-status-2 masks pair with `cfgBIF_CFG_DEV0_EPF0_VF11_0_LINK_STATUS2`. Default-value headers for neighboring NBIO versions show the same generated register family, but this chunk must remain synchronized with the NBIO 7.4 offset map.

In-tree include sites for `nbio_7_4_sh_mask.h` include `amdgpu/nbio_v7_4.c`, SMU power-management files for Arcturus, Aldebaran, and SMU 13.0.6, plus Vega20 PowerPlay/HWMgr code. The specific VF8-VF11 constants may be consumed indirectly through common generated-register helpers, debug/register dump paths, virtualization setup, PCIe error handling, interrupt setup, IOMMU/ATS coordination, or firmware-mediated NBIO programming.

External semantic dependencies are the PCI and PCI Express configuration-space specifications plus MSI, MSI-X, AER, ATS, ARI, LTR, OBFF, atomic operations, ten-bit tags, TLP prefixing, FLR, and AMD NBIO/GPU virtualization register definitions. The macros do not encode access width, reset value, read/write permission, write-one-to-clear behavior, required sequencing, or firmware ownership.

## Risks and Maintenance Notes

- The chunk starts mid-block. VF7 identity, PCIe, MSI/MSI-X, VSEC, and most AER definitions are in the previous chunk; this chunk only contains VF7's TLP prefix log tail plus ATS/ARI.
- The chunk ends mid-block. VF11 is only covered through link status 2; its MSI/MSI-X, vendor-specific, AER, ATS, and ARI definitions continue in the next chunk.
- VF8, VF9, and VF10 are intentionally near-identical. Copying a mask from one VF prefix while using another VF's offset can compile cleanly while decoding or programming the wrong config image.
- AER `STATUS`, `MASK`, and `SEVERITY` groups have very similar fields. Confusing them can suppress errors, over-report errors, or misclassify severity.
- MSI/MSI-X mask and pending field names produce generated symbols with repeated `MASK` text. Tooling must preserve those names exactly.
- Link-control and capability-2 fields can affect link stability and performance if used for writes: target speed, retrain, link disable, autonomous speed/width behavior, ASPM, compliance, de-emphasis, LTR, OBFF, atomic operations, and TLP prefix policy are not interchangeable diagnostics.
- ATS and ARI fields affect IOMMU translation, request routing, and VF enumeration. Incorrect masks or wrong-prefix usage can break isolation or guest behavior.
- Full-width `0xFFFFFFFFL` masks for BARs, logs, scratch registers, message addresses, and payload registers should not be interpreted as permission to write arbitrary all-ones values.
- Generated `L`-suffixed masks should be used with normal register-width-aware unsigned operations to avoid host integer width or sign-extension surprises in composed values.

## Test and Validation Signals

Useful validation for this chunk is mostly generated-header consistency plus hardware or simulator coverage:

- Build AMDGPU configurations that include NBIO 7.4 headers, especially `amdgpu/nbio_v7_4.c`, Arcturus/Aldebaran/SMU 13.0.6 power-management code, and Vega20 PowerPlay code.
- Cross-check every visible `BIF_CFG_DEV0_EPF0_VF8_0`, `VF9_0`, `VF10_0`, and partial `VF11_0` register group against matching `cfgBIF_CFG_DEV0_EPF0_*` offsets in `nbio_7_4_offset.h`.
- Run mechanical pair checks after adjacent chunks are merged: each complete field should have both `__SHIFT` and `_MASK`, with expected exceptions at the VF7 start boundary and VF11 end boundary.
- Compare this generated header slice against AMD's authoritative NBIO 7.4 register database, especially AER status/mask/severity, MSI/MSI-X table/PBA fields, ATS control, ARI routing, and link capability/control/status 2 fields.
- Decode PCI config-space dumps for VF8, VF9, VF10, and VF11 on NBIO 7.4 hardware or simulation and compare vendor/device/class, BAR, capability chain, PCIe device/link fields, MSI/MSI-X, AER, ATS, and ARI values.
- Exercise SR-IOV or mediated virtualization flows that expose these VFs, checking VF enumeration, BAR sizing, FLR capability, MSI/MSI-X delivery, ATS enablement, ARI routing, and absence of cross-VF leakage.
- Inject or observe PCIe AER events and verify uncorrectable/correctable status, masks, severity, first-error pointer, header logs, and TLP prefix logs decode to the expected fields.
- Exercise PCIe link training and recovery paths while observing current speed/width, training state, DL active, bandwidth-management status, target speed, compliance, de-emphasis, and 8 GT/s equalization indicators.

## Chunk Boundary Notes

Lines 36660-36716 finish the `BIF_CFG_DEV0_EPF0_VF7_0` capability chain with TLP prefix log, ATS, and ARI fields. Lines 36717-37400 cover complete `BIF_CFG_DEV0_EPF0_VF8_0` definitions. Lines 37401-38084 cover complete `BIF_CFG_DEV0_EPF0_VF9_0` definitions. Lines 38085-38768 cover complete `BIF_CFG_DEV0_EPF0_VF10_0` definitions. Lines 38769-39092 begin `BIF_CFG_DEV0_EPF0_VF11_0` and stop at `LINK_STATUS2`; the next chunk is required for the rest of VF11.

### subset-b-003242: lines 39093-41521

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 39093-41521

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.4 shift/mask header. It defines C preprocessor constants for PCIe/NBIO configuration-space bitfields in the `BIF_CFG_DEV0_EPF0` SR-IOV virtual-function register blocks.

The range starts in the middle of the `VF11` block, at the mask definitions for `BIF_CFG_DEV0_EPF0_VF11_0_LINK_CAP2`, continues through the rest of `VF11`, covers complete `VF12`, `VF13`, and `VF14` configuration images, and ends at the first command-field shifts for `VF15`. The constants encode bit offsets and masks only; register addresses are supplied by the paired NBIO offset header and runtime accessors elsewhere in AMDGPU.

## Major Register Groups

The `VF11` portion covers the PCIe capability tail for a virtual function. It includes Link Capability 2, Link Control 2, Link Status 2, reserved slot capability/control/status 2 fields, MSI/MSI-X capability fields, AMD vendor-specific enhanced capability fields, AER fields, ATS fields, and ARI fields.

The `VF12`, `VF13`, and `VF14` blocks are full repeated virtual-function PCI configuration images under address blocks named like `nbio_nbif0_bif_cfg_dev0_epf0_vf12_bifcfgdecp`. Each complete VF block defines:

- Conventional PCI header fields: vendor/device IDs, command/status, revision and class-code bytes, cache line, latency, header type, BIST, BAR placeholders, adapter ID, ROM BAR, capability pointer, interrupt line, and interrupt pin.
- PCIe capability fields: capability-list metadata, PCIe capability version/type/slot/interrupt-message fields, Device Capability/Control/Status, Link Capability/Control/Status, Device Capability 2, Device Control 2, Device Status 2, Link Capability 2, Link Control 2, and Link Status 2.
- Interrupt capability fields: MSI list/control, MSI message address/data, mask and pending registers, 64-bit MSI variants, MSI-X list/control, MSI-X table, and MSI-X PBA.
- Vendor-specific and AER enhanced capability fields: enhanced capability headers, AMD vendor scratch fields, uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, TLP header logs, and TLP prefix logs.
- IOMMU/SR-IOV-adjacent PCIe capabilities: ATS capability/control and ARI capability/control, with enhanced capability list headers for each.

The final `VF15` portion only begins the next repeated block. It includes vendor ID, device ID, and the first `COMMAND` shifts through `FAST_B2B_EN`; the corresponding `COMMAND` mask definitions and following status fields are outside this chunk.

## Important APIs, Types, And Functions

There are no functions, structs, enums, or callable APIs in this chunk. The exported interface is the generated macro namespace:

- `BIF_CFG_DEV0_EPF0_VF<n>_0_<REGISTER>__<FIELD>__SHIFT` gives the zero-based bit position for a field.
- `BIF_CFG_DEV0_EPF0_VF<n>_0_<REGISTER>__<FIELD>_MASK` gives the field mask in the containing PCI config register.

The macros are intended for use with AMDGPU register helpers or direct bit manipulation after the caller has selected the matching NBIO 7.4 register offset. The chunk contains 2,133 `#define` entries across 285 register-name groups, with most layouts repeated exactly for `VF12`, `VF13`, and `VF14`.

## Control Flow

This header has no executable control flow. Runtime behavior is supplied by code that includes this header, chooses the NBIO 7.4 register table for the detected ASIC, reads or writes a PCIe/NBIO configuration register, and combines the raw value with these shift and mask constants.

Typical consumer flow is:

1. Use the paired offset/base-index macro for a `BIF_CFG_DEV0_EPF0_VF*_0_*` register.
2. Read the register through AMDGPU MMIO, indexed register, or PCI configuration access paths.
3. Decode fields with the `*_MASK` and `*__SHIFT` constants.
4. For writable controls, preserve unrelated and reserved bits, insert the shifted field value, and write the result back.

The hardware flows represented by the fields include PCI command enablement, PCI status reporting, BAR decode metadata, PCIe payload/read-request sizing, relaxed ordering and no-snoop control, FLR and completion-timeout control, link training and retraining, 8 GT/s equalization status, MSI/MSI-X programming, AER reporting and masking, ATS address-translation cache control, and ARI function-group control.

## State And Persistence

The header itself is stateless and persists no data. It is a compile-time description of register layout.

The state described by the macros lives in hardware PCIe/NBIO configuration registers. Capability fields such as vendor/device IDs, class codes, PCIe capability metadata, supported link speeds/widths, MSI/MSI-X capability sizes, AER capability bits, ATS queue depth, and ARI support are generally hardware- or firmware-defined. Control fields such as `COMMAND`, `DEVICE_CNTL`, `LINK_CNTL`, `DEVICE_CNTL2`, `LINK_CNTL2`, MSI/MSI-X enables and masks, AER masks/severity, ATS `ATC_ENABLE`, and ARI function-group enables are writable hardware state whose lifetime depends on the relevant PCIe function reset, FLR, GPU reset, suspend/resume, and power-management domains.

Status fields such as PCI status error bits, Device Status, Link Status, Link Status 2 equalization flags, MSI pending bits, uncorrectable/correctable AER status, AER header logs, TLP prefix logs, and ATS/ARI status-like capability data are live hardware observations. This header does not encode reset defaults, access width, read-only/write-only behavior, write-one-to-clear semantics, or whether reads have side effects.

## Dependencies And Integration Points

These definitions must remain synchronized with the matching NBIO 7.4 register offset header. A macro such as `BIF_CFG_DEV0_EPF0_VF14_0_PCIE_UNCORR_ERR_STATUS__CPL_TIMEOUT_STATUS_MASK` is only meaningful when paired with the corresponding `VF14` register address; using the same field mask with a different VF or ASIC register map can silently decode or update the wrong bits.

Integration points include:

- AMDGPU NBIO 7.4 ASIC support that includes generated `asic_reg/nbio` headers for register access.
- PCIe configuration and diagnostics paths that inspect virtual-function vendor/device identity, class code, command/status, BAR, capability-list, and interrupt metadata.
- SR-IOV virtual-function setup and reset paths, where repeated `VF11` through `VF15` register layouts distinguish individual virtual-function config images.
- PCIe link-management code that decodes link capability/control/status, negotiated speed/width, retrain state, bandwidth status, and 8 GT/s equalization fields.
- Interrupt setup code that programs or verifies MSI/MSI-X enablement, address/data, masks, pending bits, table BIR/offset, PBA BIR/offset, function mask, and table size.
- RAS/AER handling paths that decode uncorrectable/correctable errors, masks, severity policy, first-error pointer, ECRC controls, header logs, and TLP prefix logs.
- IOMMU and PCIe feature integration that uses ATS controls and ARI capability/control fields for translated requests and alternative function numbering.

## Risks

The main risk is silent hardware misprogramming if generated masks or shifts are wrong, truncated at a chunk boundary, or combined with an offset from the wrong virtual-function block. A single bit-position error can enable the wrong PCI command bit, misdecode link training status, corrupt MSI/MSI-X setup, suppress the wrong AER error, or toggle ATS/ARI controls unexpectedly.

The repeated VF layouts are useful but easy to misuse. `VF12`, `VF13`, and `VF14` field names often differ only by the VF number; copy/paste errors in consumers can target the wrong virtual function while compiling cleanly. The chunk boundaries also split logical register groups: it begins after the `VF11_LINK_CAP2` shift definitions and ends before the `VF15_COMMAND` masks, so generated documentation or audits must merge adjacent chunks before treating either register group as complete.

Reserved fields and status registers need special care. Many `RESERVED` masks are present only so generated layouts cover the full register; software should not infer that reserved bits are writable. AER status, PCI status, Device Status, MSI pending, and log registers may have hardware-specific clear or latch semantics that are not represented by these macros.

Access width is another risk. Several fields describe 8- or 16-bit PCI configuration concepts inside generated 32-bit macro naming, while AER logs, BARs, MSI-X table/PBA offsets, and vendor scratch registers use 32-bit masks. Consumers must use the access width and read-modify-write rules expected by the hardware and surrounding driver code.

## Test Signals

Useful validation signals are mostly integration and hardware-facing:

- The AMDGPU tree builds with NBIO 7.4 headers included, proving that the generated macro names referenced by consumers resolve.
- Static checks or generator validation confirm that each register in this chunk has a matching NBIO 7.4 offset/base-index definition for the same `BIF_CFG_DEV0_EPF0_VF*_0_*` name.
- PCIe enumeration of matching AMD hardware reports plausible virtual-function vendor/device/class data, PCIe capabilities, MSI/MSI-X capabilities, AER capability, ATS capability, and ARI capability.
- SR-IOV enable/disable and VF reset paths can configure `VF12`, `VF13`, and `VF14` independently without cross-programming neighboring VF blocks.
- MSI/MSI-X interrupts for virtual functions work under enable, mask, pending, table, and PBA scenarios.
- Link diagnostics decode expected negotiated speed/width and equalization status from the Link Status and Link Status 2 fields.
- AER/RAS tests or fault injection decode correctable and uncorrectable error status, masks, severity, and logged TLP headers/prefixes consistently with hardware documentation.
- Suspend/resume, FLR, hot reset, and GPU reset testing verifies that writable PCIe controls, interrupt controls, AER policy, ATS enablement, and ARI controls are restored or reinitialized by higher-level driver paths rather than relying on this header for defaults.

### subset-b-003243: lines 41522-43896

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 41522-43896

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.4 shift/mask header. It defines C preprocessor constants for bit positions and bit masks in two adjacent hardware register areas:

- The tail of the `nbio_nbif0_bif_cfg_dev0_epf0_vf15_bifcfgdecp` PCI configuration-space image for virtual function 15 (`BIF_CFG_DEV0_EPF0_VF15_0_*`).
- The start and most of the `nbio_pcie0_pswusp0_pciedir_p` / `nbio_pcie0_pciedir` PCIe controller register masks (`PCIEP_*`, `PCIE_TX_*`, `PCIE_RX_*`, `PCIE_LC_*`, and shared `PCIE_*` blocks).

The file contains no executable code. Its purpose is to provide the field-layout contract used by NBIO, PCIe, power-management, and diagnostics code when composing or decoding raw register values. Addresses for the same register names are supplied by `nbio_7_4_offset.h` for config/MMIO-style registers and by `nbio_7_4_0_smn.h` or local `smn*` definitions for SMN-accessed PCIe registers; this header supplies only `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants.

## Major Register Groups

The chunk opens at line 41522 in the middle of `BIF_CFG_DEV0_EPF0_VF15_0_COMMAND`, beginning with the `INT_DIS` shift and then the command masks for I/O access, memory access, bus mastering, special cycles, memory-write-invalidate, palette snoop, parity response, stepping, SERR, fast back-to-back, and interrupt disable. It then covers the rest of VF15's PCI/PCIe configuration layout.

The `BIF_CFG_DEV0_EPF0_VF15_0_*` block includes conventional PCI fields: status bits for interrupt, capability-list presence, parity and abort errors; revision, class, cache-line, latency, header type, BIST, BARs 1-6, subsystem/vendor adapter IDs, ROM BAR, capability pointer, interrupt line, and interrupt pin.

The VF15 PCIe capability fields describe endpoint/device and link capabilities and controls. Notable masks cover maximum payload and read request size, relaxed ordering, no-snoop, FLR, completion timeout controls, ARI forwarding, atomic operation controls, LTR enable, target link speed, enter-compliance controls, hardware autonomous speed disable, de-emphasis, equalization request, current speed/width, slot-clock config, data-link-layer active, link bandwidth status, and 8 GT/s equalization status. The slot capability/control/status 2 register names are present, but in this chunk they are empty placeholders with no field macros.

Interrupt capability fields cover MSI and MSI-X: capability IDs and next pointers, MSI enable, multi-message capability and enable, 64-bit MSI support, per-vector masking support, extended message data capability/enable, message address/data registers, mask/pending registers, MSI-X table/PBA BIR and offsets, function mask, and MSI-X enable.

Enhanced capability fields cover vendor-specific capability headers and payload words, Advanced Error Reporting, ATS, and ARI. AER masks include uncorrectable status/mask/severity bits for data-link protocol, poisoned TLP, flow control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic egress blocked, TLP prefix blocked, and poisoned TLP egress blocked. Correctable AER status/mask fields cover receiver error, bad TLP, bad DLLP, replay rollover, replay timeout, advisory non-fatal, corrected internal error, header-log overflow, and enhanced capability prefix errors. Header log and TLP prefix log registers are full 32-bit fields. ATS exposes invalidation queue depth, page-aligned request support, STU, and ATC enable. ARI exposes MFVC/ACS function group support/enables, function group, and next-function number.

After the VF15 block, the chunk enters `nbio_pcie0_pswusp0_pciedir_p`. This group defines low-level PCIe port and data-link behavior:

- `PCIEP_RESERVED` and `PCIEP_SCRATCH` full-width registers.
- `PCIEP_PORT_CNTL`, including slave port request enable, snoop override, hotplug/PME/power fault controls, bus-master PMI disable, static completion allocation limit, private maximum completion payload size, poisoned unsupported-request mode, and completion payload sizing mode.
- TX controls for lane width, credit scheduling, bad DLLP generation, payload/nullified-byte handling, malformed TLP handling, completion timeout behavior, NAK deferral, N_FTS arbitration, end-to-end ID forcing, and unsupported request generation.
- TX requester ID, vendor-specific messages, request-number limits, sequence/replay tracking, ACK latency limits, NOP DLLP, advertised and initialized P/NP/CPL credits, live credit status, and FCU thresholds.
- Per-lane port status for electrical idle, lane reversal, lane numbers, and link width.
- Flow-control registers for posted, non-posted, and completion header/data credits, including VC1 equivalents.
- Error and RX controls for replay memory size, ECRC controls, flow-control initialization, DLLP ignore/ordering behavior, receiver expected sequence number, vendor-specific routing, RX credit allocation, and physical/transaction error injection.
- SR-IOV private controls and NAK counters.

The `PCIE_LC_*` link-control group describes link training, width, speed, state, equalization, lane, CDR, and L1 power-management behavior. `PCIE_LC_TRAINING_CNTL` has masks for compliance receive, TS1 matching, L0s/L1 training, power state, speed-change initialization, hot-reset quick exit, autonomous change disable, upconfigure disable, hardware link disable, ASPM L1 NAK timers, receive-enable behavior in recovery/test, and equalization request timing. `PCIE_LC_LINK_WIDTH_CNTL`, `PCIE_LC_N_FTS_CNTL`, and `PSWUSP0_PCIE_LC_SPEED_CNTL` expose negotiated/configured link width, lane reversal, N_FTS values for multiple speeds, current data rate, speed-change attempts, and directed speed changes. State registers `PCIE_LC_STATE0` through `PCIE_LC_STATE5` expose LC state-machine counters and status. Later masks cover management controls/status/masks, L1 PM substates, port order, BCH ECC controls, and additional LC control/equalization coefficient registers through `PCIE_LC_FORCE_EQ_REQ_COEFF2`.

The `nbio_pcie0_pciedir` block then covers shared PCIe controller registers: reserved/scratch, NAK counters, `PCIE_CNTL`, `PCIE_CONFIG_CNTL`, TX tracking address/control/status, bandwidth-by-unit-ID, `PCIE_CNTL2`, RX control 2, function and SWUS TX attributes, client-interface control, bus control, LC states 6-11, LC status registers, TX control 3, write-protect-region control, last received/transmitted TLP capture registers, I2C register address/data expansion, hidden config decode enablement, CLKREQB mapping, port-order enable, PHY controls and PHY status/error counters, RX advisory/drop/unsupported-request policy, and SDP control/attribute override registers.

The assigned range ends at line 43896 inside `PCIE_SDP_SWUS_SLV_ATTR_CTRL`. The final three masks present in this chunk are relaxed-ordering and SNR override masks for memory writes, memory reads, and atomics. The `CI_SWUS_SLV_IDO_OVERRIDE_*` masks and the following `PCIE_PERF_COUNT_CNTL` / performance-counter register definitions begin after this chunk and belong to the next work item.

## Important APIs, Types, And Functions

There are no functions, structs, enums, or runtime APIs in this chunk. The public interface is entirely generated preprocessor symbols:

- `REGISTER__FIELD__SHIFT`: zero-based bit offset of a field.
- `REGISTER__FIELD_MASK`: register-width mask with the field bits set.

Consumers typically combine these with AMDGPU helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`, using the matching address macro from `nbio_7_4_offset.h` or `nbio_7_4_0_smn.h`.

The important symbol families in this range are `BIF_CFG_DEV0_EPF0_VF15_0_*` for VF15 PCI configuration decoding, `PCIEP_*` for port-side PCIe pipe/link behavior, `PCIE_TX_*` and `PCIE_RX_*` for transaction/data-link transmit and receive controls, `PCIE_LC_*` / `PSWUSP0_PCIE_LC_*` for link controller training and power states, and shared `PCIE_*` masks for controller control, status, hidden decode, PHY, RX policy, SDP, and TLP capture.

## Control Flow

This header has no runtime control flow. Runtime behavior is created by code that:

1. Selects the NBIO 7.4 register set for an ASIC such as Vega20/Arcturus/Aldebaran-class hardware.
2. Reads a config, MMIO, or SMN PCIe register using the paired address definition.
3. Extracts fields by applying the mask and shift, often through `REG_GET_FIELD`.
4. For writable fields, performs a read-modify-write that preserves unrelated and reserved bits, often through `REG_SET_FIELD`.

The hardware flows described by the fields are substantial even though this chunk is declarative. VF15 fields participate in PCI enumeration, SR-IOV virtual-function capability exposure, interrupt setup, AER logging, ATS enablement, and ARI function routing. The `PCIEP_*`, `PCIE_TX_*`, and `PCIE_RX_*` fields influence credit exchange, sequence/replay behavior, transaction validation, TLP error injection, MSI/PME/vendor message handling, and NAK accounting. The `PCIE_LC_*` fields influence link training, retraining, directed speed change, equalization, lane configuration, L0/L1/L1-substate transitions, and link-management interrupts. The shared `PCIE_*` fields cover hidden configuration register access, controller arbitration, ordering attributes, low-power memory controls, captured TLP diagnostics, PHY error status, and SDP-side requester/completer behavior.

## State And Persistence

The header itself is stateless and persists no data. It is a compile-time description of hardware bit layouts.

The state described by these macros lives in PCI configuration space and NBIO/PCIe hardware registers. Some fields are static or firmware/hardware-populated capability state, such as capability IDs, next pointers, device/link capabilities, MSI/MSI-X capabilities, AER capability metadata, ATS/ARI capabilities, lane capability, flow-control widths, credit-advertisement formats, and port capabilities.

Other fields describe live or sticky status: PCI status errors, PCIe device and link status, AER correctable/uncorrectable status, header and TLP prefix logs, MSI pending bits, link state counters, link-management status bits, NAK counters, credit status, RX/TX last TLP capture registers, PHY overflow/underflow/decode/deskew/symbol-unlock errors, and RX drop/unsupported-request policy effects.

Writable controls persist only as hardware register contents within their reset and power domains. They include PCI command bits, device/link controls, MSI/MSI-X enables and masks, AER masks/severity, ATS/ARI controls, port controls, TX/RX policy controls, link training and speed controls, L1 PM substate controls, hidden decode enables, CLKREQB mapping, PHY behavior, SDP disconnect/TPH/LTR/poison controls, and SWUS slave attribute overrides. This header does not encode reset defaults, access permissions, read side effects, or write-one-to-clear behavior.

## Dependencies And Integration Points

This chunk depends on exact synchronization with the NBIO 7.4 address headers. `nbio_7_4_offset.h` provides matching `cfgBIF_CFG_DEV0_EPF0_VF15_0_*` config offsets, including the command/status/class/BAR/capability/AER/ATS/ARI registers described here. `nbio_7_4_0_smn.h` provides SMN addresses for shared PCIe registers such as `smnPCIE_CNTL2` and `smnPCIE_PERF_COUNT_CNTL`; `nbio_v7_4.c` also defines several local `smnPCIE_LC_*` addresses while including this mask header.

Direct integration points include:

- `amdgpu/nbio_v7_4.c`, which includes `nbio_7_4_offset.h`, `nbio_7_4_sh_mask.h`, and `nbio_7_4_0_smn.h` for NBIO initialization, doorbell setup, PCIe control, RAS-related handling, and link-related programming.
- `pm/swsmu/smu11/arcturus_ppt.c`, `pm/swsmu/smu13/aldebaran_ppt.c`, `pm/swsmu/smu13/smu_v13_0_6_ppt.c`, and `pm/powerplay/hwmgr/vega20_hwmgr.c`, which include the NBIO 7.4 mask header for platform power-management and PCIe link/ESM-related operations.
- Generic AMDGPU PCIe access paths that read and write through `RREG32_PCIE` / `WREG32_PCIE`, plus debug and performance paths in `soc15.c` that use PCIe counter and NAK registers adjacent to this chunk.
- Linux PCI/SR-IOV and device-reset behavior indirectly, because the VF15 config-space masks describe a virtual function's command/status, MSI/MSI-X, AER, ATS, and ARI capability layout.

The repeated register families are part of the ABI between generated register headers and hand-written driver code. A symbol such as `BIF_CFG_DEV0_EPF0_VF15_0_DEVICE_CNTL__MAX_PAYLOAD_SIZE_MASK` is only valid with the corresponding VF15 config offset; similarly, generic `PCIE_LC_*` masks must be paired with the correct NBIO 7.4 SMN/MMIO address for the active PCIe instance.

## Risks

The main risk is silent hardware misprogramming if a generated mask or shift is wrong, truncated, or paired with the wrong offset. A one-bit error can enable the wrong PCI command, decode the wrong link speed/width, mask or clear the wrong AER error, corrupt MSI/MSI-X programming, alter ATS/ARI behavior, or change low-level link-training policy.

Register naming is highly repetitive across virtual functions, lanes, VC credit types, link-controller states, and TX/RX policy registers. Copy-generation mistakes are easy to miss in review because adjacent blocks have nearly identical field names with different prefixes, widths, or state numbers.

Many fields are status or diagnostic registers with hardware-defined side effects. The header does not say whether PCI status, AER status, link-management status, NAK counters, PHY errors, last-TLP captures, MSI pending bits, or RX/TX tracking registers are read-only, sticky, write-one-to-clear, latch-on-read, or destructive-on-read. Consumers must follow the hardware specification and existing driver patterns before writing these fields.

The chunk boundary itself is a risk for research reconciliation: the `PCIE_SDP_SWUS_SLV_ATTR_CTRL` register is incomplete in this item, and `PCIE_PERF_COUNT_CNTL` starts immediately after line 43896. Merge logic should not assume this chunk covers all SDP attribute masks or performance-counter fields.

Access-path mismatch is another practical risk. Some names are config-space offsets (`cfgBIF_CFG_*`), some are NBIO MMIO offsets, and some are SMN addresses. Using the correct mask with the wrong access path can appear to compile while targeting a different register aperture.

## Test Signals

Useful validation signals are hardware-facing and integration-oriented:

- The AMDGPU tree builds with `nbio_7_4_sh_mask.h` included by NBIO and PM code, proving all referenced mask names resolve.
- Generated-header consistency checks confirm every covered `BIF_CFG_DEV0_EPF0_VF15_0_*` register has a matching `cfg*` offset in `nbio_7_4_offset.h`.
- PCI/SR-IOV enumeration on NBIO 7.4 hardware exposes plausible VF15 vendor/device/class, BAR, PCIe, MSI/MSI-X, AER, ATS, and ARI capability data.
- Link diagnostics report expected negotiated speed and width, no unexpected LC training failures, and coherent LC state/status counters across boot, resume, reset, and directed speed-change paths.
- MSI/MSI-X interrupt setup for virtual functions works without lost or misrouted interrupts, including mask and pending behavior where exercised.
- AER/RAS tests or fault-injection paths decode uncorrectable/correctable errors, severity, header logs, and TLP prefix logs consistently with hardware documentation.
- PCIe low-power and power-management testing covers ASPM/L1/L1-substate transitions, CLKREQB mapping, PME/hotplug/power-fault controls, and SDP disconnect behavior.
- PCIe diagnostics that read NAK counters, flow-control credits, last TLP captures, PHY error status, and RX/TX tracking registers produce stable, explainable values and do not regress after suspend/resume or GPU reset.

### subset-b-003244: lines 43897-46474

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 43897-46474

## Scope

This chunk is part of AMDGPU's generated NBIO 7.4 register field mask header. It contains C preprocessor constants for bit shifts and masks, not executable functions. The companion NBIO 7.4 driver includes this file from `amdgpu/nbio_v7_4.c` together with `nbio_7_4_offset.h` and SMN address headers, then uses these definitions through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, and `WREG32_SOC15`.

The line range covers:

- PCIe performance counter control fields for TX, master/slave request/completion clocks, event port selection, and counter values.
- PCIe HIP address-translation aperture fields and PRBS link-test status/counter fields.
- Software reset command, reset-control, reset-enable, and endpoint reset fields.
- NBIO clock/power-management, SMN aperture, RSMU, link-near counter, interrupt sharing, and PCIe power-gating fields.
- Repeated SR-IOV per-VF field maps for VF0 through the beginning of VF7: per-VF MM index/data windows, RCC error/config/IOV fields, BIF BME/atomic/doorbell/HDP flush/mailbox fields, and MSI-X vector/PBA fields for VF0-VF6.

## Purpose

The purpose of this section is to give the driver exact bit layouts for NBIO 7.4 PCIe/NBIF registers. The header separates register address knowledge from field layout knowledge: address macros live in the matching `*_offset.h`/SMN headers, while this file supplies each register's `__FIELD__SHIFT` and `__FIELD_MASK` constants.

The constants let driver code update specific hardware fields without hard-coding bit positions at each call site. This is important for NBIO because the same register programming idioms are used across ASIC generations while field positions can drift. Examples from the NBIO 7.4 integration path include reading `CPM_CONTROL__LCLK_DYN_GATE_ENABLE_MASK` to report clock-gating state and using related masks when programming BIF clock/light-sleep behavior.

## Important APIs, Types, and Macro Families

This chunk defines macros only. The effective API surface is the naming convention consumed by AMDGPU register helpers:

- `REGISTER__FIELD__SHIFT`: bit offset used when extracting or inserting a field.
- `REGISTER__FIELD_MASK`: field mask at its final register position.
- Repeated per-VF register prefixes such as `BIF_BX_DEV0_EPF0_VF0_*` through `BIF_BX_DEV0_EPF0_VF7_*`, where the VF number selects a virtual-function register aperture.
- RCC-side per-VF prefixes such as `RCC_DEV0_EPF0_VF0_*` through `RCC_DEV0_EPF0_VF6_*` for VF error/config/MSI-X fields.

Major register groups in this chunk:

- `PCIE_PERF_COUNT_CNTL`, `PCIE_PERF_CNTL_*`, `PCIE_PERF_COUNT*_*`, `PCIE_PERF_CNTL_EVENT*_PORT_SEL`: global enable/reset/shadow controls, event selectors, counter-upper fields, 32-bit counter values, and performance-event port routing.
- `PCIE_HIP_REG0` through `PCIE_HIP_REG8`: HIP aperture base/limit/enable/PASID/ReqAT/ReqIO configuration fields for two address-translation windows plus a HIP mask register.
- `PCIE_PRBS_*`: PRBS clear/polarity, lock/error status, bit-count completion, freerun mode, generator/checker controls, user pattern, bit counters, and per-lane error counters 0-15.
- `SWRST_COMMAND_STATUS`, `SWRST_GENERAL_CONTROL`, `SWRST_COMMAND_0/1`, `SWRST_CONTROL_0` through `SWRST_CONTROL_6`, `SWRST_EP_COMMAND_0`, `SWRST_EP_CONTROL_0`: NBIO software reset status, policy, command bits, reset cause enables, atomic reset enables, write-reset enables, lane-training holds, and endpoint reset controls.
- `CPM_CONTROL`, `PCIE_PGMST_CNTL`, `PCIE_PGSLV_CNTL`: BIF clock and power management controls including LCLK/TXCLK/refclk gating, L1/L1.1/L1.2 power gates, idleness indicators, early wake, and power-gate hysteresis.
- `SMN_APERTURE_ID_A/B`, `RSMU_*`, `SMU_PCIE_DF_Address`: SMN aperture IDs, RSMU message/invalid-access/power-gating/timer fields, and an SMU-visible Data Fabric RAS interrupt-control address field.
- `LNCNT_*`, `LNC_*_WACC_REGISTER`: link-near counter enable, quantization, weighting, and accumulated total/BW/common counters.
- `SMU_INT_PIN_SHARING_PORT_INDICATOR`: packed link-management, LTR, and DPC interrupt status per port.
- `BIF_BX_DEV0_EPF0_VF*_MM_INDEX`, `MM_DATA`, `MM_INDEX_HI`: per-VF indirect MMIO index/data windows.
- `RCC_DEV0_EPF0_VF*_RCC_ERR_LOG`, `RCC_DOORBELL_APER_EN`, `RCC_CONFIG_MEMSIZE`, `RCC_CONFIG_RESERVED`, `RCC_IOV_FUNC_IDENTIFIER`: per-VF invalid SR-IOV access logging, doorbell aperture enable, config sizing/reserved values, and IOV function identity/enable fields.
- `BIF_BX_DEV0_EPF0_VF*_BIF_BME_STATUS`, `BIF_ATOMIC_ERR_LOG`, `DOORBELL_SELFRING_GPA_APER_*`, `HDP_*_COHERENCY_FLUSH_CNTL`, `GPU_HDP_FLUSH_REQ/DONE`, `BIF_TRANS_PENDING`, `NBIF_GFX_ADDR_LUT_BYPASS`: per-VF bus-master, atomic-error, doorbell self-ring, HDP coherency flush, transaction-pending, and address-LUT bypass fields.
- `BIF_BX_DEV0_EPF0_VF*_MAILBOX_*`, `BIF_VMHV_MAILBOX`, `MAILBOX_INT_CNTL`: per-VF VM/HV transmit/receive message buffers, valid/ack handshake bits, compact VMHV mailbox data/valid/ack bits, and mailbox interrupt enables.
- `RCC_DEV0_EPF0_VF*_GFXMSIX_*`, `GFXMSIX_PBA`: per-VF MSI-X vector address/data/control fields and pending-bit-array fields for three graphics MSI-X vectors.

## Control Flow and Data Flow

There is no runtime control flow in this header. Runtime behavior emerges when the driver combines these masks with register access helpers:

- A driver reads a 32-bit register value from the PCIe, SMN, SOC15, or MMIO aperture.
- It extracts fields with masks/shifts or updates fields through AMDGPU helper macros.
- It writes the modified value back to the same hardware register.

For this chunk's most directly visible integration, `amdgpu/nbio_v7_4.c` includes the header and reads `smnCPM_CONTROL`; if `CPM_CONTROL__LCLK_DYN_GATE_ENABLE_MASK` is set, it reports `AMD_CG_SUPPORT_BIF_MGCG` in the clock-gating state. The same field family is used by nearby NBIO generations to enable/disable BIF clock gating with read-modify-write sequences. That makes the mask values part of the power-management control path even though this file itself is generated metadata.

The per-VF groups describe repeated hardware windows. Data flow is expected to be indexed by VF-specific addresses from the companion address header, with these masks applied to each VF's register contents. The register names indicate separate state paths for:

- Host/guest mailbox data transfer and acknowledgement.
- Doorbell aperture base/size/mode programming.
- HDP coherency flush request/done handshakes for CP0-CP9 and SDMA0-SDMA1.
- Error-status capture and clear-on-write style fields for BME and unsupported atomic operations.
- MSI-X vector routing and masking.

## State and Persistence Behavior

The macros are compile-time constants and hold no state. The state they describe lives in hardware registers and is generally volatile across device reset, suspend/resume, GPU reset, VF reset, PCIe link reset, power gating, or firmware reinitialization.

Important state classes represented by this chunk:

- Counter state: PCIe performance counters, PRBS bit/error counters, and LNC accumulated counters are hardware-maintained values. Some are sampled via shadow writes or global count controls.
- Sticky/status state: reset completion/wait-state bits, invalid SR-IOV access logs, BME-low and atomic error logs, transaction-pending bits, PRBS lock/error status, and MSI-X pending bits reflect hardware events and often require explicit clear bits or reset sequences.
- Configuration state: clock gating, power gating, reset enable masks, doorbell aperture configuration, self-ring GPA aperture base/size, mailbox interrupt enables, HIP apertures, RSMU invalid-access behavior, and IOV enable/function identity persist only as long as the register block retains context.
- Per-VF state: VF0-VF7 fields isolate virtual function control/status surfaces so SR-IOV guest-visible behavior can be programmed and diagnosed independently.

Because this file only defines bit positions, persistence correctness depends on call sites preserving unrelated bits during read-modify-write operations and replaying necessary programming after reset paths.

## Dependencies and Integration Points

Direct dependencies are implicit:

- C preprocessor inclusion from AMDGPU NBIO code.
- Companion register address headers, especially `nbio_7_4_offset.h` and `nbio_7_4_0_smn.h`.
- AMDGPU register helper macros that expect the `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` naming convention.
- Hardware/firmware documentation or generated register database that produced the values.

Runtime integration points in the driver tree include:

- NBIO v7.4 setup and query code in `amdgpu/nbio_v7_4.c`, especially clock-gating state and NBIO register access setup.
- Common AMDGPU PCIe performance counter code paths in older/generic ASIC files, which use identically named `PCIE_PERF_*` fields to program events and read counter overflow bits.
- Doorbell and HDP flush setup paths that program base/size registers and use request/done masks to synchronize CP/SDMA memory coherency.
- SR-IOV virtualization paths that need VF-specific RCC/BIF register layouts for guest-visible errors, doorbells, mailbox handshakes, and MSI-X programming.
- RAS/SMU-related paths that may use SMU interrupt address/status fields and RSMU behavior controls.

## Risks and Edge Cases

- Generated-header drift: if the hardware register database changes but this header does not, `REG_SET_FIELD` can silently program the wrong bits. These failures often appear as device hangs, failed link training, missing interrupts, or broken SR-IOV VF behavior rather than compile errors.
- Name collision across ASIC generations: many field names such as `CPM_CONTROL__*`, `PCIE_PERF_*`, and `SWRST_*` exist in multiple headers. Including the wrong generation-specific header or mixing address macros from another generation can compile but target incompatible layouts.
- Partial VF coverage in this chunk: VF0-VF6 include MSI-X blocks in this range, while VF7 begins and continues beyond the chunk. Reconciliation must merge adjacent chunks before producing per-file conclusions about complete VF7 coverage.
- Status versus clear bits: registers such as BME/atomic error logs expose both status and `CLEAR_*` fields. Incorrect read-modify-write logic can clear diagnostics prematurely or fail to clear sticky errors.
- Reset and power-gating hazards: `SWRST_*` and `CPM_CONTROL` fields affect link state, clock domains, and power gates. Bad masks can strand the device in reset, gate clocks while active transactions are pending, or misreport clock-gating state.
- Counter sampling hazards: performance and PRBS counters use enable/reset/shadow/upper-counter fields. Reads without the expected shadowing or reset sequence can report inconsistent diagnostics.
- SR-IOV isolation risk: per-VF mailbox, MSI-X, doorbell, and invalid-access fields are security-sensitive. A wrong VF prefix/address pairing can cross wires between virtual functions.

## Test and Validation Signals

Useful validation is mostly integration and hardware focused:

- Build signal: compile AMDGPU with NBIO 7.4 support and ensure all `REG_SET_FIELD`/`REG_GET_FIELD` references resolve with this header and the matching address headers.
- Boot/probe signal: NBIO v7.4 ASICs should probe without PCIe, doorbell, interrupt, or RAS initialization failures.
- Clock-gating signal: reading clock-gating state should accurately reflect `CPM_CONTROL__LCLK_DYN_GATE_ENABLE_MASK`; toggling BIF clock/light-sleep features should not produce hangs or link errors.
- PCIe diagnostics signal: perf counter paths should produce sane counts and counter-overflow fields; PRBS status should show lock/error behavior expected by link-test procedures.
- Reset signal: software reset and endpoint reset sequences should set completion/wait-state/status bits as expected and recover link/device operation.
- Doorbell/HDP signal: doorbell aperture programming should deliver interrupts/work submissions correctly, and HDP flush request/done handshakes should complete for CP and SDMA engines.
- SR-IOV signal: VF0-VF7 guest operation should preserve per-VF isolation, mailbox valid/ack handshakes, MSI-X delivery/masking, invalid-access logging, and BME/atomic error reporting.
- Static review signal: verify every mask is a shifted version of its documented field width, masks do not unintentionally overlap within a register unless fields are aliases/status-vs-command pairs, and per-VF repeated blocks remain structurally identical except for VF number and chunk boundary truncation.

### subset-b-003245: lines 46475-48482

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 46475-48482

## Purpose

This chunk is the final slice of AMDGPU's generated NBIO 7.4 register field mask header. It provides C preprocessor constants for decoding and composing bitfields inside NBIO, BIF, RCC, IOHC, and RAS registers for this ASIC generation. The range is not executable logic; it is compile-time hardware metadata used with the companion `nbio_7_4_offset.h` register-address definitions and AMDGPU register access helpers.

The chunk starts at the tail of the `VF7` virtual-function register area, specifically the last masks for `BIF_BX_DEV0_EPF0_VF7_BIF_VMHV_MAILBOX`, then finishes the `VF7` graphics MSI-X vector table/PBA fields. It then repeats a complete SR-IOV virtual-function register shape for `VF8` through `VF15`. Each full VF block contains:

- System PF/VF indirect MMIO window fields.
- RCC PF/VF decode fields for SR-IOV access/error logging and configuration.
- BIF PF/VF decode fields for bus mastering, atomic error status, doorbell aperture, HDP flush, transaction pending, address LUT bypass, and mailbox transport.
- RCC BIFDEC2 graphics MSI-X vector and pending-bit-array fields.

The file ends after global IOHC interrupt end-of-interrupt and RAS status masks, followed by the header guard terminator. Because this is the tail chunk of the file, it contributes both the last repeated VF definitions and the final global NBIO status definitions needed by later merge/reconciliation work.

## Important Macros And Register Families

There are no functions, structs, enums, or runtime APIs in this chunk. The exported interface consists entirely of generated macros using the standard AMD register-header naming convention:

- `REGISTER__FIELD__SHIFT`: bit position of a field inside its register.
- `REGISTER__FIELD_MASK`: bitmask covering that field inside its register value.

The `VF7` material in this chunk has two pieces. The opening lines close out `BIF_BX_DEV0_EPF0_VF7_BIF_VMHV_MAILBOX`, defining VM-to-HV mailbox receive/transmit message-data, valid, and acknowledge masks. The following `nbio_nbif0_rcc_dev0_epf0_vf7_BIFDEC2` block defines `RCC_DEV0_EPF0_VF7_GFXMSIX_VECT0` through `VECT2` address-low, address-high, message-data, and control-mask fields, plus `RCC_DEV0_EPF0_VF7_GFXMSIX_PBA` pending bits 0 through 2.

For `VF8` through `VF15`, the full repeating block begins with `BIF_BX_DEV0_EPF0_VF*_MM_INDEX`, `MM_DATA`, and `MM_INDEX_HI`. These expose an indirect MMIO access model: low offset bits, high offset bits, an aperture selector bit, and a full data dword. Consumers must pair these masks with the matching offset macros to address the intended virtual function's system PF/VF decode window.

The `RCC_DEV0_EPF0_VF*_RCC_*` block covers root-complex side PF/VF controls:

- `RCC_ERR_LOG` status bits for invalid register access in SR-IOV and doorbell read access.
- `RCC_DOORBELL_APER_EN` for enabling the BIF doorbell aperture.
- `RCC_CONFIG_MEMSIZE` and `RCC_CONFIG_RESERVED` full-width configuration fields.
- `RCC_IOV_FUNC_IDENTIFIER`, with the VF function identifier bit and the high `IOV_ENABLE` bit.

The `BIF_BX_DEV0_EPF0_VF*_*` PF/VF decode block contains the largest set of fields:

- `BIF_BME_STATUS` reports DMA activity while bus mastering is low and provides a clear bit.
- `BIF_ATOMIC_ERR_LOG` reports unsupported-request-style atomic error causes and provides matching clear bits for opcode, request-enable-low, length, and non-relaxed conditions.
- `DOORBELL_SELFRING_GPA_APER_BASE_HIGH`, `BASE_LOW`, and `CNTL` describe the guest physical address doorbell aperture, including enable, mode, and size fields.
- `HDP_REG_COHERENCY_FLUSH_CNTL` and `HDP_MEM_COHERENCY_FLUSH_CNTL` point at HDP flush control address bits.
- `GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE` provide per-client request/done bits for `CP0` through `CP9` and `SDMA0`/`SDMA1`.
- `BIF_TRANS_PENDING` reports master and slave BIF transaction-pending state.
- `NBIF_GFX_ADDR_LUT_BYPASS` exposes the LUT bypass bit.
- `MAILBOX_MSGBUF_TRN_DW0` through `DW3` and `MAILBOX_MSGBUF_RCV_DW0` through `DW3` expose four transmit and four receive mailbox data dwords.
- `MAILBOX_CONTROL` exposes transmit valid/ack and receive valid/ack bits.
- `MAILBOX_INT_CNTL` exposes interrupt enables for valid and ack events.
- `BIF_VMHV_MAILBOX` exposes compact VM/HV mailbox interrupt enables, transmit and receive message nibbles, valid bits, and ack bits.

The `RCC_DEV0_EPF0_VF*_GFXMSIX_*` BIFDEC2 block repeats for each VF. Each virtual function has three graphics MSI-X vectors. Every vector contains a low message address field with bits `[31:2]`, a full high address field, a full message-data field, and a single mask bit in the vector control register. The per-VF `GFXMSIX_PBA` register exposes pending bits for the three vectors.

The global tail contains:

- `IOHC_INTERRUPT_EOI`, with end-of-interrupt bits for SMI, SCI, and NMI.
- `RAS_GLOBAL_STATUS_LO`, with parity error status classes and firmware/software/APML/pin-triggered SMI, SCI, NMI, and sync-flood indicators.
- `RAS_GLOBAL_STATUS_HI`, with PCIE0 Port A and NBIF0 Port A error indicators.

## Control Flow

This header contributes no executable control flow. Runtime flow emerges when AMDGPU code includes this ASIC-specific mask header, reads or writes a register address from `nbio_7_4_offset.h`, and applies these constants to isolate or set fields.

A typical decode or update path outside this file is:

1. ASIC selection chooses the NBIO 7.4 register headers for the detected GPU.
2. Driver code obtains the offset for a BIF, RCC, IOHC, or RAS register from the companion offset header.
3. The code reads the register through MMIO, indirect MMIO, PCI configuration, or an ASIC wrapper helper.
4. A field is decoded with the corresponding `*_MASK` and `*_SHIFT`, often through local helper macros such as field-get/set wrappers.
5. For writable fields, the driver performs a read-modify-write sequence that preserves unrelated bits and writes only hardware-defined control or clear bits.

For the SR-IOV virtual-function blocks, higher-level control flow may configure VF doorbell apertures, service or poll mailbox state, inspect pending BIF transactions before reset, check HDP flush completion for command processor and SDMA clients, or program MSI-X vectors for VF interrupt delivery. For global tail registers, RAS and interrupt paths may check status bits, acknowledge IOHC interrupt classes, or report NBIF/PCIe error status through the driver's diagnostics.

## State And Persistence

The header itself is immutable generated metadata and stores no runtime state.

The represented state lives in hardware registers. Some fields represent configuration programmed by firmware, the PF driver, or virtualization setup, such as VF function identity, IOV enablement, doorbell aperture enable/base/size/mode, address LUT bypass, MSI-X vector address/data/control, mailbox interrupt enables, and mailbox message data. Other fields represent live hardware state, including bus-mastering anomalies, atomic-operation error logs, HDP flush request/done state, transaction-pending flags, mailbox valid/ack handshakes, MSI-X pending bits, global interrupt EOI acknowledgements, and RAS error indicators.

Persistence follows the hardware reset and power domains, not this file. GPU reset, PCI function reset, SR-IOV VF teardown, suspend/resume, firmware reinitialization, or driver unload/reload may clear or reprogram these registers. Error/status fields may be sticky, clear-on-write, write-one-to-clear, read-only, or side-effectful depending on the hardware register semantics. This mask header names bit positions only; it does not encode whether a field is safe to write, how it clears, or which reset domain owns it.

## Dependencies And Integration Points

The direct dependency is the matching NBIO 7.4 offset header. These masks are only meaningful when paired with the correct register offsets for the same ASIC generation and virtual-function index. The chunk also depends on AMDGPU's generated-register include conventions, where ASIC code selects the appropriate `asic_reg/nbio/nbio_7_4_*` headers and shared macros perform field extraction/composition.

Important integration points include:

- AMDGPU NBIO and PCIe initialization paths that select NBIO 7.4 definitions and configure BIF/RCC state.
- SR-IOV PF/VF management code that handles VF identity, IOV enablement, invalid SR-IOV register access logging, VF memory windows, and VF lifecycle reset.
- Doorbell setup paths that program PF/VF doorbell apertures and guest physical address ranges.
- HDP flush and synchronization paths that request and observe flush completion for CP and SDMA clients.
- Mailbox communication paths between a VF and the hypervisor/PF side, using transmit/receive dwords, valid/ack bits, interrupt enables, and VM/HV compact mailbox fields.
- MSI-X setup and interrupt-delivery code for graphics VF vectors, including vector table address/data/control and pending-bit-array fields.
- Reset/recovery paths that wait for BIF master/slave transaction pending to drain and clear BME or atomic error logs.
- RAS and interrupt handling paths that decode IOHC EOI and global NBIO/PCIe parity, sync-flood, APML, SMI/SCI/NMI, PCIE0, and NBIF0 status fields.

Although the repository path is under a Ceph client source mirror, the content is AMD GPU kernel-driver register metadata. It integrates with DRM/AMDGPU hardware code, not distributed filesystem logic.

## Risks

The main risk is silent hardware misdecode or misprogramming if any generated mask or shift is wrong or paired with the wrong offset/header generation. In this chunk, a single incorrect bit definition can affect VF interrupt delivery, doorbell routing, mailbox handshakes, HDP flush synchronization, SR-IOV access reporting, transaction quiescence checks, or RAS status reporting.

The repetition across `VF8` through `VF15` creates copy/generation risks. A typo isolated to one VF index can produce failures only for high-numbered virtual functions, making it hard to detect in systems that test only the first few VFs. Similar repetition across MSI-X vectors 0 through 2 and mailbox dwords 0 through 3 can create vector-specific or word-specific defects.

Access semantics are not captured by the macro names. Fields with `CLEAR_` in the name likely participate in clear-on-write flows, but the header does not enforce write-one-to-clear behavior. Treating status or clear bits like ordinary persistent fields could drop diagnostic evidence, leave sticky errors uncleared, or perturb live hardware state.

The indirect MMIO window fields are hazardous if used with the wrong aperture or high/low offset split. A bad `MM_INDEX` or `MM_INDEX_HI` composition can target a different register space than intended. Similarly, the MSI-X address-low mask intentionally excludes low address bits, and consumers must preserve alignment semantics when composing message addresses.

The chunk starts in the middle of the `VF7` mailbox/BIFDEC2 area and ends at the file terminator. Merge logic must not treat this chunk alone as complete coverage for VF7; preceding chunks contain most of the `VF7` PF/VF definitions.

## Test Signals

Useful validation signals are mostly build-time and hardware/integration-facing:

- Kernel or module builds including `nbio_7_4_sh_mask.h` complete without duplicate, missing, or malformed macro definitions.
- Generated mask definitions remain synchronized with `nbio_7_4_offset.h` and the ASIC register database for every `VF7` through `VF15` register referenced here.
- SR-IOV test runs create and exercise high-numbered VFs, especially `VF8` through `VF15`, rather than only low-numbered VFs.
- VF mailbox tests show correct transmit/receive valid and ack transitions, correct interrupt enable behavior, and correct four-dword message-buffer ordering.
- Doorbell tests confirm VF doorbell aperture base, size, mode, and enable fields route guest doorbells to the expected GPU queue paths.
- HDP flush tests verify request and done bits for `CP0` through `CP9` and `SDMA0`/`SDMA1` across all covered VFs.
- MSI-X tests confirm all three graphics vectors per covered VF program expected address/data/control values and surface pending bits in `GFXMSIX_PBA`.
- Reset and teardown tests observe BIF transaction-pending fields, clear BME and atomic error logs correctly, and avoid stale VF mailbox or interrupt state after FLR/GPU reset.
- RAS and error-injection tests confirm `IOHC_INTERRUPT_EOI`, `RAS_GLOBAL_STATUS_LO`, and `RAS_GLOBAL_STATUS_HI` decode SMI/SCI/NMI, parity, sync-flood, APML, PCIE0, and NBIF0 status consistently with hardware documentation and driver logs.
