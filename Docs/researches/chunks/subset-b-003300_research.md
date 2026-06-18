# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 99441-101850

## Scope

This chunk is a generated AMDGPU NBIO 7.7.0 shift/mask header segment. It contains only C preprocessor constants for hardware register field geometry: `REGISTER__FIELD__SHIFT` bit positions and `REGISTER__FIELD_MASK` raw masks. There are no functions, structs, enums, variables, locks, allocations, direct register reads/writes, or executable control flow in this range.

The line range starts at the first field of `BIFPLR5_0_SLOT_CNTL`; the `//BIFPLR5_0_SLOT_CNTL` register marker is one line earlier, outside this chunk. It covers the latter PCIe capability and extended-capability surface for `BIFPLR5_0`, then crosses into `// addressBlock: nbio_pcie1_bifp0_pciedir_p` and starts the `BIFP0_1` PCIe port-directory/register block. The range ends at `BIFP0_1_PCIE_RX_CREDITS_ALLOCATED_NP__RX_CREDITS_ALLOCATED_NPD_MASK`, before the matching NPH mask and before the following completion-credit and error-injection registers. Adjacent chunks are therefore required for exact boundary reconciliation.

Although this repository path is under a `ceph-client` mirror, this file is AMD DRM/AMDGPU hardware metadata and does not implement distributed-filesystem behavior.

## Purpose

`nbio_7_7_0_sh_mask.h` is the bitfield half of AMD's generated NBIO 7.7.0 register interface. This slice lets AMDGPU code decode or compose PCIe root-port, extended-capability, link-training, error-reporting, power-management, and low-level PCIe port control fields without embedding numeric bit positions at call sites.

The macros in this chunk are meant to be paired with matching register-address macros from `nbio_7_7_0_offset.h` and with AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, and `WREG32_PCIE`. The header does not describe access permissions, reset values, legal enum values, write-one-to-clear behavior, firmware ownership, or sequencing; it only provides field layout constants.

## Public Surface

The exported surface is entirely macro based:

- `BIFPLR5_0_*__*__SHIFT` and `BIFPLR5_0_*__*_MASK` cover a PCIe root-port-like configuration and extended-capability block.
- `BIFP0_1_*__*__SHIFT` and `BIFP0_1_*__*_MASK` begin the NBIO PCIe port-directory block for PCIe instance 1, port 0.
- Full-width data/log/scratch fields use masks such as `0xFFFFFFFFL`; narrow fields use the PCIe configuration-space bit widths encoded by the generated register database.

No C type safety is present. Callers must preserve reserved bits and use the correct register address, base index, access path, and hardware sequencing outside this header.

## Important Register Families

The opening `BIFPLR5_0` root/slot and PCIe 2.0 capability fields cover slot interrupt enables and status bits, root SERR/PME control, root capability/status, Device Capabilities 2 and Control 2, Link Capabilities/Control/Status 2, Slot Cap/Control/Status 2, MSI capability list/control/address/data fields, subsystem ID capability, and MSI-map capability. These fields affect hotplug notification, slot power indicators, PME visibility, completion-timeout and ARI/AtomicOp/LTR/OBFF controls, 10-bit tags, TLP prefix handling, emergency power reduction, supported and target link speeds, 8 GT/s equalization state, MSI routing, and subsystem identification.

The vendor-specific, virtual-channel, serial-number, and AER groups expose enhanced capability list headers, AMD/vendor scratch payloads, VC port and resource capability/control/status fields for VC0/VC1, device serial number dwords, and advanced error reporting. The AER surface includes uncorrectable status/mask/severity bits for DLP, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress block, TLP prefix block, and poisoned TLP egress block. Correctable error status/mask, AER capability/control, TLP header logs, root error command/status, error source IDs, and TLP prefix logs are also represented.

The secondary PCIe, lane equalization, ACS, multicast, L1 PM substate, DPC, and RP PIO groups describe higher-level PCIe link and containment behavior. They include Link Control 3, lane error status, per-lane 8 GT/s equalization controls for lanes 0-15, ACS capability/control, multicast group/window/receive/block/overlay BAR fields, L1.1/L1.2 capability and control fields, DPC capability/control/status/error-source fields, and RP PIO status/mask/severity/system-error/exception/header-log/prefix-log registers.

The ESM, data-link feature, PHY 16 GT/s, margining, CCIX, and 32 GT/s groups are the high-speed link feature surface. ESM capability/header/status/control fields advertise and manage enhanced speed modes and supported decimal data-rate bands from 8.0 GT/s through 28.0 GT/s. Data Link Feature fields cover local scaled-flow-control support, local/remote feature support, exchange enablement, and remote-valid state. The 16 GT/s PHY fields include equalization status, local/RTM parity mismatch status, and per-lane downstream/upstream TX preset controls for lanes 0-15. Margining fields provide port readiness and per-lane command/status payloads for receiver number, margin type, usage model, and margin payload across lanes 0-15. CCIX transaction capability/control fields expose optimized TLP format support/enablement, and the 32 GT/s fields expose equalization bypass, no-equalization-needed, modified training sequence, precoding, enhanced link control, and phase/status bits.

The final `BIFP0_1` port-directory section starts a different address block: `nbio_pcie1_bifp0_pciedir_p`. It defines reserved and scratch registers, `PCIEP_PORT_CNTL`, requester ID programming, physical lane status, error control, RX control, expected sequence number, vendor-specific RX data/status, RX control 3, posted RX credit allocation, and the first field of non-posted RX credit allocation. These fields are lower-level PCIe port controls rather than PCI configuration capability records: they cover slave-port request enablement, snoop overrides, hotplug/PME/power-fault messages, completion payload limits, requester IDs, lane reversal/width, AER logging and synthetic RX error generation controls, RX ignore/drop/timeout/NAK behavior, PASID/atomic/poison handling, sequence tracking, and credit accounting.

## Control Flow

There is no runtime control flow in this header. Runtime behavior follows the including driver:

1. AMDGPU includes `nbio_7_7_0_sh_mask.h` along with the matching offset header.
2. A call site selects a register address, reads a raw value, and uses these masks and shifts to extract fields, or prepares a new raw value while preserving unrelated bits.
3. Hardware and firmware implement the actual state machines for PCIe link training, MSI delivery, hotplug/PME signaling, virtual-channel negotiation, AER/DPC/RP PIO capture, ACS routing, multicast windows, L1 PM substates, ESM/data-link feature exchange, PHY equalization, margining, CCIX transaction formatting, and port RX/TX protocol handling.

The field names imply asynchronous hardware flows but the macros do not enforce ordering. Examples include link retraining and equalization phases, write-sensitive AER/DPC/RP PIO status/log handling, DPC containment completion, PME pending/status transitions, margining command completion, DLF exchange validity, RX timeout behavior, and credit/sequence-number evolution.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes hardware-visible state in NBIO PCIe configuration and port registers. Persistence depends on GPU reset domains, PCIe hot/warm reset, FLR, D-state transitions, suspend/resume, BIOS or firmware initialization, and driver writes.

Represented state includes slot/root/PME controls, MSI address/data configuration, subsystem and vendor-specific capability payloads, VC resource mappings, serial numbers, AER masks/status/severity/logs, ACS controls, multicast receive/block/overlay settings, L1 PM substate thresholds and enablement, DPC control/status/source IDs, RP PIO logs and masks, ESM and DLF capability/status, 16/32 GT/s link status, margining lane command/status data, and `BIFP0_1` port state such as requester IDs, lane width/reversal, error-control bits, RX ignore/timeout/poison controls, sequence number, vendor status, and credit allocations.

Many fields are live status or latched diagnostics rather than stable configuration. The mask names alone do not tell whether a bit is read-only, read/write, self-clearing, write-one-to-clear, clear-on-read, sampled at reset, firmware-owned, or safe for ordinary read-modify-write.

## Dependencies And Integration Points

The immediate generated dependency is `drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h`, which provides matching register addresses and base indices. Representative offset names exist for this slice, including `regBIFPLR5_0_SLOT_CNTL`, `regBIFPLR5_0_PCIE_DPC_CNTL`, `regBIFPLR5_0_LINK_STATUS_32GT`, `regBIFP0_1_PCIEP_PORT_CNTL`, `regBIFP0_1_PCIE_RX_CNTL`, and `regBIFP0_1_PCIE_RX_CNTL3`. Reset/default data for nearby generated families also appears in NBIO default headers such as `nbio_7_0_default.h`.

The direct in-tree include site for this generation is `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which includes both `nbio_7_7_0_offset.h` and `nbio_7_7_0_sh_mask.h`. Runtime integration flows through AMDGPU NBIO setup, PCIe configuration handling, interrupt routing, error reporting, GPU reset/FLR, suspend/resume, link-speed policy, power management, debugging, and low-level NBIO/PCIe port access paths.

The semantic dependencies are the PCI and PCI Express specifications plus AMD-specific NBIO register definitions for root ports, MSI/MSI-map, VC, AER, secondary PCIe, ACS, multicast, L1 PM substates, DPC, RP PIO, ESM, DLF, 16/32 GT/s PHY/equalization, margining, CCIX, and PCIe port RX/error-control behavior.

## Risks And Edge Cases

- The range starts after the `BIFPLR5_0_SLOT_CNTL` marker and ends before the full `BIFP0_1_PCIE_RX_CREDITS_ALLOCATED_NP` definition. Merge/reconciliation must stitch those boundaries with adjacent chunks.
- Generated shift/mask drift can compile cleanly while targeting the wrong bit, causing broken hotplug/PME signaling, link instability, missed or stuck AER/DPC interrupts, bad MSI routing, incorrect ACS/P2P isolation, invalid L1 PM behavior, or low-level PCIe port protocol failures.
- Status/log registers may have side effects. A generic read-modify-write using these masks can lose diagnostic data or fail to clear an interrupt if the underlying register is write-one-to-clear, capture-on-error, or firmware-owned.
- Link control, target speed, equalization, ESM, 16/32 GT/s status, margining, DLF exchange, and CCIX controls are sequencing-sensitive and hardware-dependent.
- ACS, multicast, VC, MSI, and requester-ID fields affect routing, isolation, traffic classes, and interrupt delivery. Incorrect masks can create subtle virtualization, IOMMU, peer-to-peer, or interrupt bugs.
- Full-width fields and high-bit masks use `L`-suffixed integer constants. Consumers should keep using established AMDGPU `u32` register helper patterns to avoid signedness, truncation, or host-width assumptions.
- Repeated per-lane families for lanes 0-15 are easy to review mechanically but can hide one-lane copy/generation errors. Active hardware lane count may be lower than the defined maximum depending on board routing, fuses, and negotiated link width.
- `BIFP0_1` port controls include error injection/generation and RX ignore controls. Misprogramming can mask genuine link faults or inject synthetic failures into a live link.

## Test Signals

Useful validation is mostly generated-data consistency plus hardware integration:

- Build AMDGPU configurations that include NBIO 7.7.0 support, especially translation units including `nbio_v7_7.c`.
- Mechanically check that every visible `__SHIFT` macro has the intended matching `_MASK`, masks align with shifts, and repeated lane/margining/equalization families remain structurally consistent across lanes.
- Cross-check every `BIFPLR5_0_*` and `BIFP0_1_*` register name in this slice against `nbio_7_7_0_offset.h` and generated default/reset data where available.
- Decode known-good NBIO 7.7.0 register dumps and compare slot/root/PME/MSI/VC/AER/ACS/multicast/L1 PM/DPC/RP PIO/ESM/DLF/PHY/margining/CCIX/32 GT/s and `BIFP0_1` port fields against hardware documentation, `lspci -vvxxx`, and AMDGPU debug output.
- Exercise PCIe link speed, retraining, 8/16/32 GT/s equalization, ESM negotiation, DLF exchange, L1.1/L1.2 transitions, PME/wake, hotplug/slot events where applicable, and suspend/resume or FLR recovery.
- Exercise AER/DPC/RP PIO paths through supported error injection or observed hardware errors, verifying status, masks, severity, source IDs, header logs, prefix logs, containment status, and clear behavior.
- Validate interrupt delivery under MSI programming, port requester-ID behavior, RX timeout/ignore policies, poison/atomic/PASID handling, and credit/status decoding on supported hardware or simulation.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-003300`. The final per-file document should merge it with neighboring chunks for complete `nbio_7_7_0_sh_mask.h` coverage. The previous chunk owns the end of `BIFPLR5_0_SLOT_CAP` and the `//BIFPLR5_0_SLOT_CNTL` marker. The next chunk completes `BIFP0_1_PCIE_RX_CREDITS_ALLOCATED_NP` and continues the `BIFP0_1` port-directory block.
