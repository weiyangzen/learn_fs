# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 126304-128753

## Scope

This chunk is part of AMDGPU's generated NBIO 7.2.0 shift/mask header. It covers the tail of the `BIFPLR6_1` PCIe root-port configuration block, the complete `BIF_CFG_DEV0_RC1` root-complex configuration block, and the beginning of the `BIF_CFG_DEV1_RC1` root-complex configuration block. The range starts in `BIFPLR6_1_LANE_15_EQUALIZATION_CNTL_16GT` and ends after `BIF_CFG_DEV1_RC1_DEVICE_CNTL__MAX_READ_REQUEST_SIZE_MASK`, so both outer edges are intentionally partial.

The file is not executable logic. It exposes generated C preprocessor constants in the standard register-field forms:

- `REGISTER__FIELD__SHIFT`: the zero-based bit position for a field.
- `REGISTER__FIELD_MASK`: the mask for that field in the register value.

These constants are paired with generated offsets in `nbio_7_2_0_offset.h` and consumed through AMDGPU register access helpers or direct bit operations.

## Purpose

The chunk describes PCIe/NBIO register layouts for high-speed link management, lane margining, CCIX/ESM capability reporting, and PCI/PCIe root-complex configuration space. It lets AMDGPU code and diagnostics decode or compose NBIO 7.2.0 register values without hard-coding bit positions.

At a high level the range provides:

- Final 16 GT/s per-lane equalization preset fields for `BIFPLR6_1` lane 15.
- `BIFPLR6_1` PCIe lane margining enhanced capability metadata, port capability/status, and per-lane control/status definitions for lanes 0 through 15.
- `BIFPLR6_1` CCIX enhanced capability metadata, CCIX protocol capability fields, ESM capability/status/control fields, 20 GT/s and 25 GT/s per-lane ESM equalization preset definitions for lanes 0 through 15, and CCIX transport capability/control fields.
- A full `BIF_CFG_DEV0_RC1` conventional PCI bridge and PCIe root-port style configuration block, including base PCI config registers, PM, PCIe, MSI, SSID, MSI mapping, virtual channel, device serial number, AER, secondary PCIe, ACS, data link feature, 16 GT/s PHY, and lane margining definitions.
- The start of `BIF_CFG_DEV1_RC1`, from vendor/device identity through PCIe device capability and most of device control.

## Important Definitions

There are no functions, structs, or enums in this chunk. The important public surface is the macro namespace itself.

The `BIFPLR6_1` lane margining group includes:

- `BIFPLR6_1_PCIE_MARGINING_ENH_CAP_LIST`, with `CAP_ID`, `CAP_VER`, and `NEXT_PTR` fields for PCIe enhanced capability walking.
- `BIFPLR6_1_MARGINING_PORT_CAP` and `BIFPLR6_1_MARGINING_PORT_STATUS`, which expose whether margining uses software and whether hardware/software margining readiness has been reached.
- `BIFPLR6_1_LANE_0_MARGINING_LANE_CNTL` through `BIFPLR6_1_LANE_15_MARGINING_LANE_CNTL`, each carrying receiver number, margin type, usage model, and margin payload fields.
- Matching `BIFPLR6_1_LANE_N_MARGINING_LANE_STATUS` groups for lanes 0 through 15, using parallel status field names for receiver number, margin type, usage model, and payload.

The `BIFPLR6_1` CCIX and ESM group includes:

- `BIFPLR6_1_PCIE_CCIX_CAP_LIST`, `PCIE_CCIX_HEADER_1`, and `PCIE_CCIX_HEADER_2`, which define enhanced-capability IDs, versions, next pointers, vendor ID, length, port number, component ID, and similar metadata.
- `BIFPLR6_1_PCIE_CCIX_CAP`, with protocol capability bits such as direct cache access and opt-in features including ID space and fabric-based ordering support.
- `BIFPLR6_1_PCIE_CCIX_ESM_REQD_CAP` and `BIFPLR6_1_PCIE_CCIX_ESM_OPTL_CAP`, which advertise required and optional extended speed mode rates.
- `BIFPLR6_1_PCIE_CCIX_ESM_STATUS` and `BIFPLR6_1_PCIE_CCIX_ESM_CNTL`, which hold current/selected ESM rates, enable/control bits, link reach, retimer presence, and timeout select fields.
- `BIFPLR6_1_ESM_LANE_0_EQUALIZATION_CNTL_20GT` through lane 15, plus the matching 25 GT/s lane groups, each with downstream and upstream transmit preset fields.
- `BIFPLR6_1_PCIE_CCIX_TRANS_CAP` and `BIFPLR6_1_PCIE_CCIX_TRANS_CNTL`, which describe and control CCIX transport behavior such as message support and optimized TLP enablement.

The complete `BIF_CFG_DEV0_RC1` block mirrors a PCI-to-PCI bridge/root-port configuration image:

- Base PCI identity and bridge configuration: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`, `BASE_ADDR_1`, `BASE_ADDR_2`, bus-number fields, I/O and memory windows, prefetchable memory upper/lower fields, ROM base, interrupt line/pin, bridge control, and extended bridge control.
- Power management: `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`, including power state, PME enable/status, data select/scale, bus power enable, and PMI data fields.
- PCIe capability: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, slot/root capability and control/status registers, and PCIe 2.0-style device/link/slot capability/control/status registers.
- Interrupt and identity capabilities: `MSI_CAP_LIST`, MSI message control/address/data registers, `SSID_CAP_LIST`, `SSID_CAP`, `MSI_MAP_CAP_LIST`, and `MSI_MAP_CAP`.
- Extended PCIe capabilities: vendor-specific, virtual channel, device serial number, advanced error reporting, secondary PCIe, ACS, data link feature, 16 GT/s PHY, 16 GT/s per-lane equalization, and lane margining.

The `BIF_CFG_DEV1_RC1` portion begins a second root-complex configuration block with the same structural pattern. This chunk contains identity, base class, bridge window, PM, PCIe capability, device capability, and most of device control fields, but the rest of DEV1 RC1 device status, link, MSI, AER, ACS, 16 GT/s, and margining definitions continue after the requested line range.

## Control Flow

This header contributes no runtime control flow. Control flow appears in consumers such as `amdgpu/nbio_v7_2.c`, which includes `nbio_7_2_0_sh_mask.h` with the matching NBIO register map. Typical use follows this pattern:

1. Select the NBIO 7.2.0 register offset from `nbio_7_2_0_offset.h` or a related generated address header.
2. Read the register through AMDGPU MMIO, SOC15, or config-space access helpers.
3. Extract fields using this header's `*_MASK` and `*__SHIFT` constants, often through helper macros such as `REG_GET_FIELD`.
4. For writable controls, clear the field mask, insert the shifted value, and write the composed value back.

The lane groups are repetitive by design. Higher-level code usually selects a lane-specific register name or generated offset and then uses the corresponding lane-specific mask names. The header itself does not provide loops, lane arrays, access-width metadata, or write semantics.

## State And Persistence

The header has no mutable state and persists no data. It describes the layout of NBIO/PCIe hardware state.

The represented state lives in PCIe configuration-space shadows and NBIO registers. Capability-list IDs, versions, next pointers, maximum link widths/speeds, CCIX capability bits, ACS capability bits, and lane-count-related fields are generally static or firmware-initialized. Control fields such as PCI command enables, bridge controls, PM state/PME enables, PCIe device and link controls, MSI enables, AER masks/severity, ACS controls, data-link feature controls, 16 GT/s equalization controls, lane margining controls, and CCIX ESM controls are writable hardware state. Status fields such as PCI status, device status, link status, AER status/logs, data-link feature status, margining ready/status, ESM status, and parity mismatch status are live or sticky hardware observations.

Persistence is governed by the hardware reset and power domains, not by this file. Warm reset, FLR, BACO, suspend/resume, GPU reset, or PCIe hot reset can clear or reinitialize many of these values. Driver code must therefore pair these masks with the appropriate init, resume, and error-recovery paths rather than treating the macros as policy.

## Dependencies And Integration Points

Primary generated-header dependencies:

- `nbio_7_2_0_offset.h` supplies the register offsets and base indices for the register names defined here.
- `nbio_7_2_0_default.h` supplies generated reset/default values for the same register namespace.
- `nbio_7_2_0_smn.h` supplies SMN-addressed NBIO definitions used by indirect or fabric-visible access paths.

Driver integration points:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c` includes this mask header and is the main NBIO 7.2 implementation site. It demonstrates the expected generated-register usage model even though most PCIe capability fields in this large chunk are hardware description rather than hot-path code.
- SOC15 and AMDGPU register helper macros rely on the `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` naming convention for field extraction and composition.
- PCIe capability enumeration, link management, RAS/AER diagnostics, DPC/error recovery, power management, and reset paths are the higher-level domains that give semantic meaning to fields such as AER status, link equalization status, lane margining status, ACS control, and PM state.
- External diagnostics such as `lspci -vvv`, kernel PCIe AER logs, and AMDGPU debug register dumps can be correlated with these field definitions on matching NBIO 7.2.0 hardware.

## Risks

- ASIC-generation mismatch is the main risk. These bit positions are specific to NBIO 7.2.0; using them with NBIO 7.0, 7.4, 7.7, 7.9, or later hardware can silently decode or write the wrong bits.
- The chunk is highly repetitive. Per-lane margining and equalization groups are vulnerable to generated-header drift where a single lane's prefix, shift, or mask differs from the surrounding pattern.
- The slice boundaries are partial. It starts after most `BIFPLR6_1_LANE_15_EQUALIZATION_CNTL_16GT` context and ends before the rest of `BIF_CFG_DEV1_RC1`; consumers must not treat this chunk as the full BIFPLR6_1 or DEV1 RC1 map.
- Many fields are PCIe status or error registers with hardware-specific side effects. AER, device status, secondary status, margining status, and similar fields may be sticky or write-one-to-clear; this header describes bit positions only and does not encode those semantics.
- Writeable controls can affect link stability, routing, interrupts, isolation, and power state. Misusing command, bridge control, PM, PCIe link/device control, MSI, AER mask/severity, ACS, data-link feature, 16 GT/s equalization, lane margining, or CCIX ESM control fields can break enumeration, disable memory or bus-master access, hide errors, weaken isolation, or destabilize link training.
- Mixed register widths matter. Some fields are 8-bit or 16-bit PCI config fields represented as masks with `L` suffixes, while many enhanced capabilities and logs are 32-bit fields. Callers must use the access width expected by the register block and preserve reserved bits on read-modify-write.

## Test Signals

Useful validation is mostly build-time, generated-header consistency, and hardware observation:

- AMDGPU builds with NBIO 7.2 support enabled, proving referenced generated macro names still resolve.
- Generated header comparison against AMD's register source or adjacent NBIO 7.2 generated files confirms that every `*_MASK` matches the corresponding `*__SHIFT` and register width.
- Static comparison of repeated lane groups catches lane prefix swaps, missing lane numbers, or copy-generation errors across lanes 0 through 15.
- PCIe enumeration on matching hardware reports coherent root-port capability chains, including PM, PCIe, MSI, virtual channel, serial number, AER, secondary PCIe, ACS, data link feature, 16 GT/s PHY, margining, and CCIX/ESM where present.
- Link training and retraining tests show expected negotiated speed/width and no unexpected 16 GT/s equalization or parity-mismatch status.
- Lane margining diagnostics return plausible per-lane receiver, margin type, payload, ready, error, and sample data without cross-lane swaps.
- AER/RAS fault-injection or hardware error tests decode correctable and uncorrectable errors, source IDs, header logs, and TLP prefix logs consistently with kernel PCIe AER reports.
- Reset, FLR, suspend/resume, and GPU reset testing verifies that writable command, PM, link, interrupt, AER, ACS, 16 GT/s, margining, and CCIX controls are restored or reinitialized according to driver policy.
