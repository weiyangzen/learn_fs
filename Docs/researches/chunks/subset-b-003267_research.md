# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 19739-22179

## Purpose

This chunk is part of the generated AMDGPU NBIO 7.7.0 register shift/mask header. It does not contain executable code; it publishes C preprocessor constants that describe bit positions and already-positioned masks for NBIO PCIe bridge/root-port configuration registers.

The covered range starts in the tail of the `BIFPLR1` PCIe lane-margining block, completes `BIFPLR1` CCIX and extended-speed-mode definitions, then switches to the `nbio_pcie0_bifplr2_cfgdecp` address block. Most of the chunk defines `BIFPLR2` PCI/PCIe bridge capability fields: conventional bridge config space, power-management and MSI capability fields, PCIe device/link/slot/root controls, virtual-channel resources, AER, secondary PCIe, lane equalization, multicast, LTR, ARI, DPC/RP PIO, ESM, data-link feature exchange, 16 GT/s PHY, lane margining, CCIX, and the beginning of 20 GT/s ESM lane equalization.

These macros are meant to be consumed with the paired address definitions in `nbio_7_7_0_offset.h` and AMDGPU register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, `REG_GET_FIELD`, and `REG_SET_FIELD`.

## Macro API Surface

The public interface is the generated macro namespace. Each field follows the standard AMD register pattern:

- `<REGISTER>__<FIELD>__SHIFT` is the field's low-bit position.
- `<REGISTER>__<FIELD>_MASK` is the field mask already shifted into register position.

Important groups in this chunk:

- `BIFPLR1_LANE_13/14/15_MARGINING_LANE_*`: final `BIFPLR1` per-lane margining status/control fields, with receiver number, margin type, usage model, and margin payload/status payload fields.
- `BIFPLR1_PCIE_CCIX_*`: CCIX enhanced capability header fields, ESM capability bits, required/optional ESM capability registers, current ESM data rate, and calibration-complete status.
- `BIFPLR1_ESM_LANE_0..15_EQUALIZATION_CNTL_20GT` and `_25GT`: per-lane downstream/upstream TX preset fields for 20 GT/s and 25 GT/s operation.
- `BIFPLR1_PCIE_CCIX_TRANS_CAP`: CCIX optimized TLP-format support bit.
- `BIFPLR2_VENDOR_ID` through `BIFPLR2_EXT_BRIDGE_CNTL`: conventional PCI bridge identity, command/status, class/revision/header/BIST, BAR, bus-number, I/O, memory, prefetchable-memory, interrupt, and bridge-control fields.
- `BIFPLR2_PMI_*`, `BIFPLR2_PCIE_*`, `BIFPLR2_MSI_*`, and `BIFPLR2_SSID_*`: standard PCI power-management, PCIe capability, MSI address, MSI-map, and subsystem-id fields.
- `BIFPLR2_DEVICE_*`, `BIFPLR2_LINK_*`, `BIFPLR2_SLOT_*`, and `BIFPLR2_ROOT_*`: PCIe device, link, slot, and root-port controls/status, including payload/read-request sizes, error reporting enables, link speed/width, ASPM, retraining, bandwidth notifications, hotplug, and PME status.
- `BIFPLR2_PCIE_VENDOR_SPECIFIC*` and `BIFPLR2_PCIE_VC*`: vendor-specific capability header/data plus virtual-channel capability, control, status, and resource controls for VC0/VC1.
- `BIFPLR2_PCIE_ADV_ERR_*`, `BIFPLR2_PCIE_UNCORR_ERR_*`, `BIFPLR2_PCIE_CORR_ERR_*`, and log/source registers: Advanced Error Reporting status, mask, severity, header logs, root error command, source IDs, and TLP prefix logs.
- `BIFPLR2_PCIE_SECONDARY_*` and `BIFPLR2_PCIE_LANE_*_EQUALIZATION_CNTL`: secondary PCIe capability, lane error status, and lane 0-15 equalization fields.
- `BIFPLR2_PCIE_ACS_ENH_CAP_LIST`, `BIFPLR2_PCIE_MC_*`, `BIFPLR2_PCIE_LTR_*`, and `BIFPLR2_PCIE_ARI_*`: enhanced capability-list headers and multicast, latency-tolerance reporting, and alternative routing-ID interpretation fields.
- `BIFPLR2_PCIE_DPC_*` and `BIFPLR2_PCIE_RP_PIO_*`: downstream port containment capability/status, error source, RP PIO status/mask/severity/system-error/exception fields, and header/prefix logs.
- `BIFPLR2_PCIE_ESM_*`: ESM capability header, status/control, and capability bitmaps for many supported rates from roughly 8.0 GT/s through 28.0 GT/s.
- `BIFPLR2_DATA_LINK_FEATURE_*`, `BIFPLR2_PCIE_PHY_16GT_*`, `BIFPLR2_LINK_*_16GT`, parity mismatch status, and `BIFPLR2_LANE_0..15_EQUALIZATION_CNTL_16GT`: data-link feature exchange and 16 GT/s PHY/equalization definitions.
- `BIFPLR2_PCIE_MARGINING_*` and `BIFPLR2_LANE_0..15_MARGINING_LANE_*`: PCIe lane margining port capability/status and per-lane control/status fields.
- `BIFPLR2_PCIE_CCIX_*` and `BIFPLR2_ESM_LANE_0..6_EQUALIZATION_CNTL_20GT`: CCIX enhanced capability metadata and the first seven per-lane 20 GT/s ESM TX preset fields before this chunk ends.

There are no functions, structs, enums, or storage declarations in this span.

## Control Flow and Data Flow

This header contributes compile-time data only. Runtime control flow is in AMDGPU C files that include the generated offset and mask headers, read or write hardware registers, and use the mask/shift constants to preserve unrelated bits.

Typical flow:

1. A consumer includes `nbio/nbio_7_7_0_offset.h` for register addresses and this header for field layout.
2. The driver reads a config/MMIO register through an AMDGPU access helper.
3. The driver extracts fields with mask/shift arithmetic or through `REG_GET_FIELD`.
4. The driver updates individual fields with `REG_SET_FIELD` and writes the modified value back.

`drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c` directly includes this header and demonstrates the pattern for NBIO 7.7.0 register programming: it reads fields such as revision IDs, configures doorbell apertures/ranges, interrupt controls, HDP flush/remap offsets, PCIe index/data windows, and other NBIO state. This particular line range is more PCIe capability and link-feature metadata than core bring-up logic, so many fields are likely used by generic PCIe handling, diagnostics, firmware/platform code, or future ASIC-specific paths rather than by a dense local call graph in `nbio_v7_7.c`.

## State and Persistence Behavior

The macros themselves hold no state. The underlying hardware registers do, and many fields in this chunk represent persistent device or link state until reset, retraining, firmware intervention, or driver writes:

- Conventional bridge command/status and bridge-control fields can affect I/O, memory, bus mastering, parity/SERR, VGA/ISA routing, and secondary-bus behavior.
- PCIe device/link/slot/root control fields influence error-reporting enables, relaxed ordering, max payload/read-request size, ASPM, read-completion boundary, link retraining, common-clock config, bandwidth notification, hotplug, and PME handling.
- AER and DPC/RP PIO fields expose error state and policy. Some status bits may be write-one-to-clear or otherwise side-effectful depending on PCIe semantics.
- VC, multicast, ARI, ACS-list, LTR, MSI/MSI-map, and vendor-specific capability fields influence routing, isolation, interrupt delivery, latency policy, and resource allocation.
- ESM, CCIX, data-link feature, 16 GT/s PHY, lane equalization, and margining fields reflect or request link training, calibration, TX preset, margining, and high-speed capability state. Incorrect programming can degrade or drop PCIe links.

Because this is hardware configuration state, persistence is external to Linux memory. Values may be initialized by firmware, changed by PCI core or platform code, reset by device reset/link reset, and read by AMDGPU for diagnostics or ASIC-specific control.

## Dependencies and Integration Points

Primary dependencies and integration points:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h` supplies corresponding `cfgBIFPLR2_*` and other register addresses. For example, the offset file maps `cfgBIFPLR2_PCIE_DPC_*`, `cfgBIFPLR2_PCIE_ESM_*`, `cfgBIFPLR2_LANE_*_MARGINING_*`, `cfgBIFPLR2_PCIE_CCIX_*`, and `cfgBIFPLR2_ESM_LANE_*_EQUALIZATION_CNTL_*` addresses that match this chunk's field macros.
- `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c` includes both the offset and mask headers and is the ASIC-specific NBIO integration file for this generation.
- AMDGPU register helper macros provide the field access contract. The generated `__SHIFT` and `_MASK` names are what `REG_GET_FIELD` and `REG_SET_FIELD` expect.
- PCIe architecture semantics matter for the standard capability blocks: PM, MSI, PCIe capability, VC, AER, secondary PCIe, multicast, LTR, ARI, DPC, data-link feature, 16 GT/s PHY, and lane margining.
- CCIX/ESM definitions integrate with high-speed coherent/interconnect link behavior. Their meaning depends on matching hardware, firmware, and platform support.

## Risks

- Address/mask mismatch: a mask from `nbio_7_7_0_sh_mask.h` must be used with the matching register address from `nbio_7_7_0_offset.h`. Mixing NBIO generations or BIFPLR instances can silently modify the wrong field.
- Repeated lane fields: lane 0-15 definitions for equalization, margining, and ESM presets are highly repetitive. Copy/paste mistakes can target the wrong lane while still compiling.
- Reserved and side-effectful bits: many registers include reserved fields or status/log bits. Consumers must preserve unrelated bits and honor PCIe write-clear semantics.
- Link stability: ESM, data-link feature exchange, 16 GT/s, 20/25 GT/s presets, lane equalization, CCIX, and margining controls can affect link training and negotiated speed/width.
- Error containment and reporting: AER and DPC/RP PIO policy/status fields interact with error recovery. Incorrect masks or clear operations can hide real faults or trigger containment behavior unexpectedly.
- Virtualization/isolation: ARI, ACS-list headers, multicast, MSI/MSI-map, bridge routing, and VC resources can affect isolation and routing assumptions in multi-function or virtualized setups.

## Test Signals

Useful validation signals for changes touching this chunk or its consumers:

- Build AMDGPU with NBIO 7.7 support enabled; renamed or missing generated macros should fail at compile time.
- Static consistency checks that every field has a matching `__SHIFT` and `_MASK`, masks align with shifts, and paired offset/mask register names remain synchronized.
- Runtime NBIO 7.7 device bring-up: PCIe config access, doorbell setup, interrupt delivery, HDP flush paths, and successful load/unload of `amdgpu`.
- PCIe link diagnostics: negotiated speed/width, stable retraining, 16 GT/s equalization status, data-link feature status validity, ESM calibration status, and absence of unexpected AER after link events.
- Error-path tests where available: AER correctable/uncorrectable reporting, DPC trigger/status/source logging, and RP PIO log capture.
- Lane-level diagnostics for high-speed links: per-lane equalization presets, margining control/status payloads, and parity mismatch status.
- Platform or firmware validation for CCIX/ESM capabilities: advertised data-rate support, calibration-complete behavior, and TX preset programming across BIFPLR1/BIFPLR2 instances.
