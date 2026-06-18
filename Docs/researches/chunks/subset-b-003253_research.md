# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h lines 17060-19479

## Purpose

This chunk is an auto-generated AMD NBIO 7.7.0 register-offset slice for the second PCIe/NBIO instance. It exports preprocessor constants that map PCIe root-port configuration decode blocks and PCIe port-directory blocks to SOC15 register addresses. The macros are consumed by AMDGPU register helpers together with the companion shift/mask header; the header itself has no executable code.

The chunk starts in the middle of the `nbio_pcie1_bifplr3_cfgdecp` address block at `BIFPLR3_1_ROOT_CAP` and continues through the rest of that root-port configuration space. It then covers complete `BIFPLR4_1` and `BIFPLR5` root-port configuration decode blocks, complete `BIFP0_1` through `BIFP4_1` PCIe directory blocks, and the first four register entries in the `BIFP5` PCIe directory block.

## Public Surface In This Chunk

The exported API is 2,388 `#define` macros: 1,194 register-address macros plus 1,194 matching `*_BASE_IDX` macros. Every entry in this chunk uses base index `5`, which is the SOC15 NBIO register base selected by callers such as `SOC15_REG_OFFSET(NBIO, instance, reg...)`, `RREG32_SOC15`, `WREG32_SOC15`, and PCIe-port access helpers.

The named prefixes covered here are:

- `regBIFPLR3_1_*`: 464 macros for the tail of the root-port config block at `0x11203000`, beginning with PCIe root capability/status and continuing through extended PCIe capabilities.
- `regBIFPLR4_1_*`: 548 macros for the full root-port config block at `0x11204000`.
- `regBIFPLR5_*`: 548 macros for the full root-port config block at `0x11205000`.
- `regBIFP0_1_*` through `regBIFP4_1_*`: five repeated PCIe port-directory blocks at `0x11240000`, `0x11241000`, `0x11242000`, `0x11243000`, and `0x11244000`.
- `regBIFP5_*`: the first four PCIe port-directory offsets at `0x11245000`: reserved, scratch, port control, and TX requester ID.

There are no C types, functions, structs, or inline helpers in this range. Its stable interface is purely the generated macro naming convention and the address values encoded in those macros.

## Important Register Families

The `BIFPLR3_1` tail contains PCIe capability and extended-capability offsets for a root-port-like configuration space. It includes root capability/status; PCIe 2.0 device, link, and slot capability/control/status entries; MSI address/data and MSI mapping entries; SSID entries; vendor-specific enhanced capability entries; Virtual Channel capability/control/status and VC0/VC1 resource registers; Device Serial Number registers; Advanced Error Reporting status, masks, severities, control, header logs, root error command/status, error source ID, and TLP prefix logs; Secondary PCIe link-control and per-lane equalization entries for lanes 0-15; ACS capability/control; multicast capability/control/address/receive/block/overlay entries; L1 PM substate capability/control entries; DPC and RP PIO entries; ESM controls, capabilities, status, lane equalization at 16/20/25 GT, CCIX transition controls, and 32 GT link capability/control/status entries.

The `BIFPLR4_1` and `BIFPLR5` blocks repeat the full root-port configuration-space layout. They start with standard PCI header fields such as vendor/device ID, command/status, revision/class code, cache/latency/header/BIST, bus-number and bridge window registers, capability pointer, interrupt fields, and bridge control. They continue through PM capability, PCIe capability, device/link/slot/root capability and control registers, MSI/MSI-map/SSID, vendor-specific capability, VC resources, serial number, AER, secondary PCIe equalization, ACS, multicast, L1 PM substates, DPC/RP PIO, ESM, CCIX transition, and 32 GT link registers.

The `BIFP0_1` through `BIFP4_1` PCIe directory blocks expose port-facing link and data-link-layer controls rather than PCI config-space headers. Each block defines offsets for scratch and port control, TX requester ID, lane status, error control, RX control/expected sequence/vendor-specific/control3, RX credits for posted/non-posted/completion traffic, physical and transaction error injection, NAK counters, link-control and training registers, link-width and speed controls, link-state registers, bandwidth-change and CDR controls, lane controls, equalization coefficient controls, link-management masks, strap registers, L1 PM substate controls, BCH ECC control, fine-grain clock-gating override, save/restore registers, TX sequence/replay/ack-latency/credit threshold/vendor-specific/NOP/request-count controls, advertised and initial TX credits, credit status, and flow-control counters for posted, non-posted, and completion traffic on VC0 and VC1.

The `BIFP5` section is intentionally incomplete in this chunk. It begins the next PCIe port-directory block but stops at `regBIFP5_PCIE_TX_REQUESTER_ID`; the rest of that block is expected in the adjacent chunk.

## Control Flow And State

This header has no runtime control flow. The only "flow" is compile-time expansion:

1. A translation unit includes `nbio_7_7_0_offset.h` and usually `nbio_7_7_0_sh_mask.h`.
2. Driver code passes one of these `reg...` constants through AMDGPU/SOC15 register access macros.
3. The access helper combines the encoded offset and base index with the selected hardware instance and performs the actual MMIO, SMN, or PCIe-port-indexed read/write.

No state is stored in the header. Persistent state lives in the GPU hardware registers described by these constants. Writes through consumers can affect PCIe enumeration-visible config space, bridge windows, interrupt routing, link training and equalization, AER/DPC error reporting, ACS isolation, virtual-channel arbitration, multicast routing, L1 PM substates, ESM state, port error injection, credit accounting, and clock/power-related link controls.

Several macros intentionally share the same address where two PCIe fields occupy different halves of the same dword, for example device control/status, link control/status, slot control/status, MSI address/data overlays, ACS capability/control, and multicast capability/control. Correct users must pair these offset macros with the appropriate field masks from the shift/mask header instead of assuming one logical register per address.

## Dependencies And Integration Points

The direct C integration point for this specific generated header is `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which includes both `nbio_7_7_0_offset.h` and `nbio_7_7_0_sh_mask.h`. That file uses the generated constants with `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, and `REG_SET_FIELD` to implement NBIO v7.7 operations such as HDP flush remapping, revision ID extraction, memory-size reads, doorbell aperture setup, interrupt handling setup, PCIe index/data offset reporting, register initialization, clock gating, light sleep, and register remapping.

The companion `nbio_7_7_0_sh_mask.h` supplies field-level masks and shifts for the same register names. Reset/default information for corresponding NBIO register families is present in generated default headers such as `nbio_7_0_default.h`, including entries for `BIFPLR4_1`, `BIFPLR5`, and repeated `BIFP*` blocks. Semantic interpretation depends on AMD's NBIO 7.7.0 hardware spec and PCI/PCIe capability specifications for root ports, MSI, PM, PCIe extended capabilities, AER, VC, ACS, multicast, L1 PM substates, DPC, RP PIO, equalization, ESM, CCIX, and high-speed link controls.

## Risks And Maintenance Notes

- This is generated hardware contract data. Any wrong offset or base index can make otherwise correct driver code read or write the wrong NBIO register.
- The chunk boundaries are partial: it starts after the beginning of `BIFPLR3_1` and ends near the start of `BIFP5`. Adjacent chunk research is required for complete per-block coverage.
- The repetition across `BIFPLR4_1`, `BIFPLR5`, and `BIFP0_1` through `BIFP4_1` makes generation drift hard to review manually; a single dropped or shifted entry could be hidden among mostly identical names.
- Shared-address aliases are expected in PCIe config-space layouts. Callers that read-modify-write without the correct field mask can corrupt sibling fields in the same dword.
- Many target registers have hardware side effects or policy impact outside this header: AER and DPC status may be write-one-to-clear, error-injection registers can deliberately poison link behavior, link training/equalization controls can destabilize PCIe connectivity, ACS and bridge-window fields affect isolation and routing, and MSI/MSI-map fields affect interrupt delivery.
- These offsets are version-specific. Similar NBIO generations can use different address encodings or larger addresses, so these macros should not be reused for non-7.7.0 ASICs without the matching generated header.

## Test Signals

Useful validation signals for this chunk are:

- Build coverage for `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c` and any configuration that includes `nbio_7_7_0_offset.h` with `nbio_7_7_0_sh_mask.h`.
- Static generation checks that every non-`*_BASE_IDX` register macro in lines 17060-19479 has exactly one matching `*_BASE_IDX` macro and that all base indices remain `5`.
- Cross-header checks that register names in this offset slice have matching shift/mask definitions where fields are decoded or updated, and matching generated defaults where reset values are modeled.
- Hardware smoke tests on an NBIO 7.7.0 ASIC that compare decoded root-port config space and PCIe port-directory dumps against `lspci -vvxxx`, debugfs/MMIO register dumps, or firmware-provided register tables.
- Runtime tests around PCIe link speed/width reporting, retraining, equalization state, AER/DPC logging and clearing, MSI delivery, bridge-window programming, ACS isolation behavior, L1 PM substate transitions, and port credit/status counters.
- Negative tests should avoid writing error-injection, link-control, DPC, ACS, and bridge-routing registers on production hardware unless the test harness can recover the link and restore the device cleanly.
