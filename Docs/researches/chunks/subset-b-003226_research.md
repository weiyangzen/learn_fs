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
