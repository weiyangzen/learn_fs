# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 70924-73370

## Purpose

This chunk is a generated AMD NBIO 7.2.0 shift/mask header slice for PCIe configuration and extended-capability registers. It defines preprocessor constants that describe bit positions inside registers; it does not define executable code. The constants are the field-layout half of the NBIO register ABI and are paired with address macros in `nbio_7_2_0_offset.h`.

The range begins at the tail of the `BIF_CFG_DEV2_EPF2_0_PCIE_PWR_BUDGET_DATA` field masks and then covers the rest of the `BIF_CFG_DEV2_EPF2_0` endpoint-function capability fields for power budget, dynamic power allocation, ACS, PASID, ARI, TPH requester, and TPH steering table entries 0-63. It then enters the `addressBlock: nbio_pcie0_bifplr0_cfgdecp` block and covers most of the `BIFPLR0_0` PCIe bridge/root-port-style configuration field map through the start marker for `BIFPLR0_0_LANE_2_EQUALIZATION_CNTL_16GT`.

## Public Surface

The public API is the macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the bit index for a field.
- `<REGISTER>__<FIELD>_MASK`: the raw register mask for that field.

There are no functions, structs, enums, variables, or inline helpers in this chunk. Consumers include the header and pass these constants to AMDGPU field helpers such as `REG_GET_FIELD` and `REG_SET_FIELD`, combined with raw register reads/writes through SOC15/NBIO accessors.

## Covered Register Areas

- `BIF_CFG_DEV2_EPF2_0_PCIE_PWR_BUDGET_CAP`: `SYSTEM_ALLOCATED` capability bit, following the power-budget data field that starts before this chunk.
- `BIF_CFG_DEV2_EPF2_0_PCIE_DPA_*`: enhanced capability-list metadata, dynamic power allocation capabilities, latency indicator, status/control, and per-substate power allocation entries 0-7.
- `BIF_CFG_DEV2_EPF2_0_PCIE_ACS_*`: ACS extended capability metadata plus source validation, translation blocking, peer-to-peer redirect, upstream forwarding, egress control, and direct translated P2P capability/control fields.
- `BIF_CFG_DEV2_EPF2_0_PCIE_PASID_*`: PASID capability and control fields, including enable, executable permission, privileged mode, and max PASID width fields.
- `BIF_CFG_DEV2_EPF2_0_PCIE_ARI_*`: ARI capability/control fields for function-group support and next-function-number metadata.
- `BIF_CFG_DEV2_EPF2_0_PCIE_TPH_REQR_*` and `TPH_ST_TABLE_0..63`: TPH requester capability/control fields and 64 steering-tag table registers, each with lower and upper 8-bit entries.
- `BIFPLR0_0` conventional PCI/PCIe bridge config fields: vendor/device ID, command/status, revision/class, cache-line/latency/header/BIST, bus numbering, IO/memory/prefetchable bridge windows, capability pointer, ROM base, interrupt line/pin, bridge control, vendor capability, adapter ID, power-management capability, and PCIe capability registers.
- `BIFPLR0_0` PCIe device/link/slot/root capability and control/status fields: device capability/control/status, link capability/control/status, slot capability/control/status, root control/capability/status, and PCIe 2.0 device/link/slot capability extensions.
- `BIFPLR0_0` MSI and identification capabilities: MSI message control/address/data fields, SSID capability, MSI map capability, and vendor-specific extended capability header/payload fields.
- `BIFPLR0_0` virtual channel and device serial number fields: VC capability/control/status and VC0/VC1 resource capability/control/status definitions, plus serial number dwords.
- `BIFPLR0_0` AER fields: uncorrectable/correctable error status, masks, severity, AER capability/control, header logs, root error command/status/source ID, and TLP prefix logs.
- `BIFPLR0_0` secondary PCIe and lane equalization fields: link control 3, lane error status, and `PCIE_LANE_0..15_EQUALIZATION_CNTL` downstream/upstream preset and coefficient fields.
- `BIFPLR0_0` ACS, multicast, L1 PM substate, and DPC/RP PIO fields: capability/control/status, multicast address/receive/block/overlay fields, L1.1/L1.2 support and threshold/timing fields, downstream port containment controls/status/source IDs, and root-port PIO status/mask/severity/system-error/exception/header/prefix logs.
- `BIFPLR0_0` ESM and data-link feature fields: ESM capability headers/status/control plus `PCIE_ESM_CAP_1..7` capability bitmaps for lane count, rate, preset, equalization, retimer, reach, and calibration properties; Data Link Feature capability/status fields.
- `BIFPLR0_0` 16 GT PHY fields through the start of lane 2: 16 GT capability/control/status, local/RTM parity mismatch status, and lane 0-1 16 GT equalization controls. The assigned line range ends on the `BIFPLR0_0_LANE_2_EQUALIZATION_CNTL_16GT` section marker, before the lane 2 shift/mask lines.

## Control Flow

This header chunk has no runtime branches or call graph. Its effective flow is compile-time substitution:

1. Code chooses a register address from `nbio_7_2_0_offset.h`, such as a `regBIF_CFG_DEV2_EPF2_0_*` or `regBIFPLR0_0_*` macro.
2. Code reads a raw register value or prepares one for writing using AMDGPU register access helpers.
3. The matching `__SHIFT` and `_MASK` constants from this header isolate or compose fields with helpers such as `REG_GET_FIELD` or `REG_SET_FIELD`.
4. Any observable behavior comes from the hardware register access, not from this header.

The register layout is highly repetitive, especially in steering-table, lane-equalization, ESM capability, and error-log families. The preprocessor does not provide arrays or computed names, so any loop in consumer code must map an index to explicit register names or use a higher-level generated table elsewhere.

## State and Persistence Behavior

The header stores no state. It describes hardware-backed state in PCIe endpoint-function and root-port configuration spaces:

- Capability fields such as ACS/PASID/ARI/TPH, PCIe device/link/slot/root capabilities, AER capability, L1 PM substate capability, DPC capability, ESM capability, DLF capability, and 16 GT PHY capability are generally read-only or firmware/hardware-populated reports.
- Control fields such as command, bridge control, device/link/slot/root controls, MSI control, ACS control, PASID control, ARI control, TPH requester control, VC controls, AER root error command, secondary link control, multicast control, L1 PM substate controls, DPC control, ESM control, and DLF exchange enable represent mutable hardware state when the underlying register allows writes.
- Status/log fields such as PCI status, link/slot/root/device status, DPA status, AER status/logs, lane error status, DPC status, RP PIO logs, ESM status, DLF remote status, and 16 GT parity/equalization status reflect current or latched hardware events.
- Persistence, reset behavior, write-one-to-clear behavior, and side effects are not encoded here. They are defined by PCIe rules, AMD NBIO 7.2 hardware documentation, firmware setup, and the access path used by the driver.

## Dependencies

- `nbio_7_2_0_offset.h`: supplies the paired register offsets and base-index macros. These shift/mask definitions are meaningful only when matched to the correct register address family.
- AMDGPU register helpers: typical consumers use `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, `SOC15_REG_OFFSET`, `REG_GET_FIELD`, and `REG_SET_FIELD`.
- PCI and PCI Express architecture: many names mirror standard PM, MSI, PCIe capability, AER, ACS, PASID, ARI, TPH, VC, multicast, L1 PM substate, DPC, Data Link Feature, and 16 GT PHY capability definitions.
- AMD NBIO 7.2 register generation: the numeric masks and shifts are ASIC-generation-specific and must remain synchronized with the generated offset and default/reset metadata for the same NBIO version.

## Integration Points

The direct AMDGPU NBIO 7.2 integration point in this tree is `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, which includes both `nbio_7_2_0_offset.h` and `nbio_7_2_0_sh_mask.h`. Even when a particular `BIF_CFG_DEV2_EPF2_0` or `BIFPLR0_0` field is not touched by current code, the header is available to NBIO 7.2 paths that need PCIe configuration, link, power, interrupt, or error-diagnostic programming.

The `BIF_CFG_DEV2_EPF2_0` symbols integrate with endpoint-function configuration space. They are relevant to PCIe power budgeting, DPA power substates, isolation/translation controls, PASID/ARI virtualization-related behavior, and TPH steering. The `BIFPLR0_0` symbols integrate with a root-port/downstream-port style PCIe block and cover bridge aperture programming, link negotiation, MSI routing, slot/root behavior, AER/DPC containment, lane equalization, L1 substate power management, and extended-speed diagnostics.

Correct integration requires matching the full register prefix. Similar field names recur across endpoint-function blocks, `BIFPLR` port instances, standard PCIe fields, secondary PCIe fields, ESM fields, and 16 GT PHY fields.

## Risks and Edge Cases

- A wrong mask or shift silently reads or writes the wrong hardware bits. That is high risk for bridge windows, MSI, ACS/PASID/ARI/TPH, link control, AER/DPC, L1 PM substates, and lane equalization because errors can affect DMA isolation, interrupt delivery, PCIe enumeration, power state transitions, or link stability.
- Some registers are packed views over the same dword or word. Read-modify-write sequences must preserve unrelated fields and avoid clearing write-one-to-clear status bits accidentally.
- Access permissions are not represented. Capability fields may be read-only, status bits may be sticky or write-clear, and control fields may be firmware-owned or valid only in specific link/power states.
- The generated namespace is repetitive. It is easy to mix `BIF_CFG_DEV2_EPF2_0` with another endpoint function, or `BIFPLR0_0` with another port instance, or to confuse normal lane equalization with 16 GT/ESM equalization fields.
- The chunk starts and ends on non-semantic boundaries. It begins after the `BIF_CFG_DEV2_EPF2_0_PCIE_PWR_BUDGET_DATA` field definitions have already started, and it ends on the section marker for `BIFPLR0_0_LANE_2_EQUALIZATION_CNTL_16GT`; adjacent chunks are needed for complete per-register coverage.
- Large capability bitmaps such as `BIFPLR0_0_PCIE_ESM_CAP_1..7` encode many rate/reach/preset/calibration bits. Review should compare the generated bit numbering against the ASIC register database rather than inferring meaning from adjacent names.

## Test Signals

- Build AMDGPU configurations that include `nbio_7_2_0_sh_mask.h` to catch missing or misspelled macros consumed by NBIO 7.2 code.
- Static generated-header checks should verify that every field macro has a matching shift/mask pair where expected, that masks align with their shifts, and that register names correspond to offsets in `nbio_7_2_0_offset.h`.
- Runtime PCIe signals include successful GPU enumeration, correct bridge windows, stable negotiated link speed/width, functional MSI delivery, clean AER/DPC logs, and expected ACS/PASID/ARI/TPH capability reporting in PCI config-space dumps.
- Power/link tests should cover suspend/resume, hot reset or GPU reset, link retraining, L1.1/L1.2 transitions, high-throughput DMA, and error injection or AER/DPC handling where available.
- Diagnostic checks can compare `lspci -vvxxx`, kernel PCIe/AER logs, AMDGPU initialization logs, and hardware register dumps against expected NBIO 7.2 field decoding for `BIF_CFG_DEV2_EPF2_0` and `BIFPLR0_0`.
