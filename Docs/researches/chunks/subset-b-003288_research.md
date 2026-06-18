# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 70766-73184

## Scope

This chunk covers a generated AMD NBIO 7.7.0 register shift/mask header section. It starts at the tail of `BIFPLR2_0_LANE_12_MARGINING_LANE_CNTL`, continues through the end of the `BIFPLR2_0` PCIe margining, CCIX, ESM, and 32GT link-extension masks, then enters `addressBlock: nbio_pcie0_bifplr3_cfgdecp` and covers the beginning of the `BIFPLR3_0` PCIe bridge/root-port configuration-space masks. The covered `BIFPLR3_0` range includes standard PCI configuration header fields, PCIe capability, MSI, subsystem/vendor-specific capabilities, virtual channels, device serial number, AER, secondary PCIe capability, ACS, multicast, L1 PM substates, DPC/root-port PIO logging, ESM data-rate support, data-link feature exchange, 16GT PHY equalization status, and the first PCIe margining registers. It ends after the first field of `BIFPLR3_0_LANE_1_MARGINING_LANE_CNTL`, so the rest of lane 1 and later margining lanes are in the next chunk.

The file is data-only C preprocessor material. It defines no functions, structs, variables, locks, allocations, persistence objects, or direct MMIO operations. Its public interface is the generated pair convention:

- `<REGISTER>__<FIELD>__SHIFT` for bit offsets.
- `<REGISTER>__<FIELD>_MASK` for the bit mask used to extract or compose a field.

## Purpose

This header section is the bitfield side of the NBIO 7.7.0 register ABI used by AMDGPU. The companion `nbio_7_7_0_offset.h` file supplies register/config-space addresses and base indices such as `regBIFPLR2_0_PCIE_CCIX_ESM_CNTL`, `regBIFPLR2_0_LINK_STATUS_32GT`, `cfgBIFPLR3_0_COMMAND`, `cfgBIFPLR3_0_PCIE_UNCORR_ERR_STATUS`, and `regBIFPLR3_0_PCIE_ESM_CAP_1`; this file supplies the field layouts for those registers.

Consumers normally use these masks through AMDGPU register helpers and generated macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT`. In this source tree, `amdgpu/nbio_v7_7.c` directly includes `nbio_7_7_0_offset.h` and `nbio_7_7_0_sh_mask.h`; most macros in this chunk describe PCIe config-space capability layout and hardware-visible status rather than ordinary C APIs.

## Important Macro Families

### BIFPLR2 PCIe Margining, CCIX, ESM, and 32GT Fields

The first section completes the later lanes of `BIFPLR2_0` PCIe margining. Lane control/status registers use a repeated layout for lanes 12-15 in this chunk:

- `LANE_N_RECEIVER_NUMBER` / `LANE_N_RECEIVER_NUMBER_STATUS` at bits 0-2.
- `LANE_N_MARGIN_TYPE` / `LANE_N_MARGIN_TYPE_STATUS` at bits 3-5.
- `LANE_N_USAGE_MODEL` / `LANE_N_USAGE_MODEL_STATUS` at bit 6.
- `LANE_N_MARGIN_PAYLOAD` / `LANE_N_MARGIN_PAYLOAD_STATUS` at bits 8-15.

The CCIX capability block defines extended capability list and header fields (`CAP_ID`, `CAP_VER`, `NEXT_PTR`, vendor ID, revision, length), ESM capability bits, required data-rate support flags for 2.5GT, 5GT, 8GT, 16GT, 20GT, and 25GT, current ESM status, ESM control, and CCIX TLP format support/control. The `BIFPLR2_0_PCIE_CCIX_ESM_CNTL` register is the main control surface here: it has two 7-bit data-rate fields, calibration strobe, enable bit, phase-2/phase-3 extended equalization timeout fields, compliance mode, link-reach target, retimer-present flag, and quick-equalization timeout selector.

`BIFPLR2_0_ESM_LANE_0..15_EQUALIZATION_CNTL_20GT` and `BIFPLR2_0_ESM_LANE_0..15_EQUALIZATION_CNTL_25GT` define per-lane downstream/upstream transmit preset fields. Each lane packs two 4-bit presets: DSP in bits 0-3 and USP in bits 4-7. The sibling offset header aliases four lanes per 32-bit register address, so the lane-specific masks are the way software names the packed fields without hard-coding bit positions.

`BIFPLR2_0_LINK_CAP_32GT`, `BIFPLR2_0_LINK_CNTL_32GT`, and `BIFPLR2_0_LINK_STATUS_32GT` describe PCIe 32GT link extension state: support/disable bits for equalization bypass and no-equalization-needed behavior, modified TS usage modes, equalization phase success/completion, link equalization request, modified TS received, enhanced link behavior control, transmitter precoding state/request, and no-equalization-needed received.

### BIFPLR3 Base PCI and PCIe Capability Configuration

After `addressBlock: nbio_pcie0_bifplr3_cfgdecp`, the chunk begins a full generated field map for `BIFPLR3_0` PCI bridge/root-port configuration space. It covers base identification and bridge-window fields such as vendor/device ID, command/status, revision/class, cache-line/latency/header/BIST, primary/secondary/subordinate bus numbers, IO base/limit, secondary status, memory and prefetchable memory windows, ROM base, interrupt line/pin, bridge control, vendor capability, subsystem IDs, and power-management capability/status.

The PCIe capability portion defines standard device, link, slot, root, and secondary capability fields:

- `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` cover payload size, phantom functions, extended tag, endpoint L0s/L1 latency, attention/phantom role bits, error reporting enables, relaxed ordering, max read request size, no-snoop, aux power, transaction pending, and fatal/nonfatal/correctable/unsupported-request status.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` cover link speed/width, ASPM, L0s/L1 exit latency, clock PM, surprise-down, active-state reporting, link disable/retrain, common clock, extended sync, hardware autonomous width disable, speed/width/slot clock/DL-active reporting, and bandwidth management/autonomous bandwidth status.
- `SLOT_*` and `ROOT_*` fields cover hotplug/indicator/power-limit/attention controls, slot status, SERR/PM interrupt controls, CRS visibility, PME requestor/status/pending, and secondary capability bits.
- `DEVICE_CAP2`, `DEVICE_CNTL2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` cover completion timeout, ARI, atomics, LTR, TPH, 10-bit tag, OBFF, end-to-end TLP prefixes, emergency power reduction, FRS, supported link speeds, SKP OS support, retimer presence, target link speed, compliance/deemphasis, and 8GT equalization status.

### MSI, Vendor-Specific, Virtual Channel, Serial Number, and AER Fields

The MSI block defines capability-list pointer fields, MSI enable/multiple-message/64-bit/per-vector/ext-data fields, MSI address low/high, and message data fields. SSID and MSI-map capability fields provide subsystem vendor/device IDs and MSI remap enable/fixed/type bits.

Vendor-specific and virtual-channel extended capability blocks include capability list/header fields, scratch DWs, VC port capability/control/status, and VC0/VC1 resource capability/control/status. These fields map traffic-class to VC assignment, VC enable/ID, arbitration table loading/selection, table status, and VC negotiation pending state.

The AER block covers uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, header logs, root error command/status, error source IDs, and TLP prefix logs. Field names cover standard PCIe error categories such as data-link protocol, surprise down, poisoned TLP, flow control, completion timeout/abort/unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal errors, MC blocked TLP, atomic egress blocked, TLP prefix blocked, advisory nonfatal, replay timer rollover, replay number rollover, bad DLLP, bad TLP, receiver error, root status, and first-error pointers.

### Secondary PCIe, ACS, Multicast, L1 PM Substates, DPC, and RP PIO

`BIFPLR3_0_PCIE_SECONDARY_ENH_CAP_LIST`, `PCIE_LINK_CNTL3`, `PCIE_LANE_ERROR_STATUS`, and `PCIE_LANE_0..15_EQUALIZATION_CNTL` provide secondary PCIe capability metadata, enhanced equalization control, per-lane error bitmap, and lane-specific downstream/upstream preset/hint fields.

ACS capability/control fields define source validation, translation blocking, P2P request/completion redirect, upstream forwarding, P2P egress control, direct translated P2P, enhanced capability, and P2P memory target access control bits. Multicast fields describe MC capability/control, MC base/receive/block/overlay BAR registers, and block-untranslated state.

L1 PM substate fields define ASPM L1.1/L1.2 and PCI-PM L1.1/L1.2 support, common-mode restore time, LTR L1.2 thresholds, link activation controls, and power-on timing scale/value.

DPC fields describe capability metadata, trigger controls, completion/interrupt/correctable-error controls, poisoned-TLP egress blocking, software trigger, DL-active error correction, status/reason/busy fields, and DPC source ID. The root-port PIO block defines status/mask/severity/system-error/exception triplets for CFG/IO/MEM unsupported-request completions, completer-abort completions, and completion timeouts, followed by header and prefix logs.

### BIFPLR3 ESM, DLF, 16GT PHY, and Margining Start

The `BIFPLR3_0_PCIE_ESM_*` family defines extended speed mode capability metadata, vendor header, minimum time in EI value/scale, ESM Gen3/Gen4 data-rate control, enable bit, and seven dense support bitmaps. `PCIE_ESM_CAP_1..7` enumerate supported ESM rates from 8.0G through 28.0G in 0.1G increments, with one bit per rate. This is a large repeated generated section and is sensitive to off-by-one naming errors.

`BIFPLR3_0_DATA_LINK_FEATURE_CAP` and `DATA_LINK_FEATURE_STATUS` define local and remote DLF support bitmaps, scaled flow-control support, exchange enable, and remote-valid status. `PCIE_PHY_16GT_ENH_CAP_LIST`, `LINK_CAP_16GT`, `LINK_CNTL_16GT`, `LINK_STATUS_16GT`, parity mismatch status, and `LANE_0..15_EQUALIZATION_CNTL_16GT` provide 16GT-specific capability/control/status fields and per-lane downstream/upstream 16GT transmit presets.

The chunk ends in the beginning of PCIe margining support for `BIFPLR3_0`: margining enhanced capability list, port capability/status (`MARGINING_USES_SOFTWARE`, `MARGINING_READY`, `MARGINING_SOFTWARE_READY`), complete lane 0 margining control/status fields, and the first lane 1 control field. Remaining lane 1 fields and later lanes belong to the next chunk.

## Control Flow and State Behavior

There is no runtime control flow in this header. Its effect is compile-time: C code includes the generated names and the preprocessor expands field shifts/masks into constants used for register composition and decoding.

The state represented by this chunk is persistent or latched hardware state in PCIe/NBIO registers, not software-owned storage in the header. Important hardware state includes PCI bridge command/status bits, BAR/window decode fields, power-management state, PCIe device/link/slot/root control and status, MSI/MSI-map state, VC negotiation and arbitration state, AER/DPC/RP PIO error status and logs, ACS/multicast policy, L1 PM substate timing, ESM data-rate support and control, 16GT/32GT equalization status and lane presets, DLF exchange state, and PCIe margining request/status payloads.

Several fields are status or command-like rather than durable configuration. Examples include status/error bits in `STATUS`, `DEVICE_STATUS`, `LINK_STATUS`, `LINK_STATUS2`, AER status, DPC status, RP PIO status, VC negotiation/table status, ESM calibration/enable/control, equalization request/completion bits, and margining ready/software-ready/status fields. The macros do not encode ordering, clear semantics, polling intervals, timeout policy, or which fields are read-only versus write-one-to-clear; that sequencing belongs to the AMDGPU caller and hardware specification.

## Dependencies and Integration Points

This chunk depends on the generated NBIO 7.7.0 register header set:

- `nbio_7_7_0_offset.h` supplies matching `reg*`, `cfg*`, and base-index definitions for the register names in this file.
- Other NBIO generation headers define similar but not interchangeable fields. Cross-generation names such as `BIFPLR3_0_PCIE_*` recur in `nbio_7_0`, `nbio_7_2`, and related headers, but field presence and layout can differ.
- AMDGPU register helper macros consume the `__SHIFT` and `_MASK` convention through `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, and MMIO helpers.

Observed integration in this source tree:

- `amdgpu/nbio_v7_7.c` directly includes this mask header and the matching offset header while implementing NBIO 7.7 runtime hooks.
- The same NBIO 7.7 implementation uses the generated headers for HDP flush offsets/masks, PCIe index/data port offsets, doorbell range programming, memory-controller access enablement, interrupt control, PCIe master control, clock-gating, and low-power memory settings.
- PCIe/NBIO access helpers exposed by `nbio_v7_7_get_pcie_index_offset`, `nbio_v7_7_get_pcie_data_offset`, `nbio_v7_7_get_pcie_port_index_offset`, and `nbio_v7_7_get_pcie_port_data_offset` are the likely access path for config/port registers represented by these masks.
- Linux PCIe core, platform firmware, and GPU hardware/firmware own much of the standard PCIe config-space behavior. The AMDGPU driver must not treat all advertised fields as freely programmable runtime knobs.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can target unrelated PCIe/NBIO fields, causing link training failures, broken MSI delivery, lost error reporting, invalid bridge windows, or GPU hangs.
- The chunk has repeated lane and rate families. Per-lane margining/equalization fields and the dense `PCIE_ESM_CAP_1..7` 0.1G rate bitmap are easy to corrupt mechanically.
- Some registers are partial at chunk boundaries. `BIFPLR2_0_LANE_12_MARGINING_LANE_CNTL` begins before this chunk, and `BIFPLR3_0_LANE_1_MARGINING_LANE_CNTL` continues after it. A merged report must avoid treating those partial families as complete here.
- PCIe error/status fields have subtle clear and severity semantics. Misusing AER, DPC, or RP PIO status/mask/severity/system-error fields can hide fatal link errors or generate incorrect system error signaling.
- PCIe power and link-management fields are platform-sensitive. ASPM/L1 PM substate timing, target link speed, equalization, retimer, DLF, and ESM settings must remain coordinated with firmware, hardware capabilities, and the Linux PCIe core.
- Capability-list and header fields must remain consistent with the PCIe config-space layout. Broken `CAP_ID`, `CAP_VER`, `NEXT_PTR`, length, or vendor/header fields can make capability traversal and feature discovery unreliable.
- ACS, VC, multicast, and bridge-window fields affect routing/isolation. Incorrect values can break peer-to-peer behavior, traffic-class mapping, request forwarding, multicast targeting, or access isolation.
- CCIX/ESM fields are specialized. Enabling optimized TLP format, ESM, calibration, compliance mode, or data-rate selections without the right hardware/link partner support can destabilize the link.

## Test and Validation Signals

Useful validation is primarily build and hardware integration coverage:

- Build AMDGPU with `amdgpu/nbio_v7_7.c` and the generated NBIO 7.7.0 headers; this catches missing or renamed macros.
- NBIO bring-up tests should verify HDP flush masks, doorbell aperture/range setup, interrupt control, PCIe index/data accessors, memory-controller access enablement, clock-gating, and low-power settings still compile and run.
- PCIe enumeration and config-space validation should confirm vendor/device/class/header fields, bridge bus/window registers, capability lists, MSI capability, PCIe capability, AER, DPC, ACS, VC, L1 PM, and ESM extended capabilities decode as expected.
- Link training tests should cover Gen3/Gen4/Gen5 paths, 8GT/16GT/32GT equalization status, per-lane preset fields, retimer presence/status, target link speed, link retrain, and equalization request/completion reporting.
- Error-handling tests should inject or observe AER/DPC/RP PIO conditions and verify status, mask, severity, source ID, header log, prefix log, and root error reporting fields.
- Power-management tests should exercise ASPM and L1 PM substate entry/exit, common-mode restore time, LTR thresholds, power-on timing, and suspend/resume interaction.
- PCIe margining validation should verify margining ready/software-ready state and lane control/status payload behavior across lane 0 and later lanes once adjacent chunks are reconciled.

## Unresolved Cross-Chunk References

Line 70766 is only the final `LANE_12_MARGIN_PAYLOAD_MASK` field for `BIFPLR2_0_LANE_12_MARGINING_LANE_CNTL`; the register comment and earlier shift/mask fields belong to the previous chunk. Line 73184 starts `BIFPLR3_0_LANE_1_MARGINING_LANE_CNTL` but includes only `LANE_1_RECEIVER_NUMBER__SHIFT`; the rest of lane 1 and subsequent margining lanes are in the next chunk. The final per-file reconciliation should stitch both boundaries before making source-file-level completeness claims.
