# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 85520-87941

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.2.0 shift/mask header. It defines C preprocessor constants for decoding and programming bitfields in NBIO/BIF PCIe root-port configuration registers. The constants describe register field positions only; there is no Ceph or distributed-filesystem behavior here despite the source tree path containing `ceph-client`.

The range contains 2,164 `#define` entries across 256 commented register blocks. There are 1,078 `__SHIFT` definitions and 1,086 `_MASK` definitions. The mask surplus is expected for this chunk because it begins at the tail of `BIFPLR5_0_PCIE_RP_PIO_STATUS`, where the matching shift definitions are in the previous chunk, and it ends inside `BIFPLR6_0_PCIE_MC_RCV0`, before that field's mask appears in the next chunk.

At a high level, the chunk covers:

- The tail of `BIFPLR5_0` root-port DPC/RP PIO diagnostics, from `RP_PIO_STATUS` masks through PIO mask, severity, system-error, exception, TLP header log, and TLP prefix log fields.
- `BIFPLR5_0` PCIe 5.0-era extended speed mode, 16 GT/s PHY, data-link feature, lane equalization, lane margining, CCIX, CCIX ESM, and CCIX translation capability fields.
- The beginning and most of the standard/extended PCIe configuration image for `BIFPLR6_0` under `addressBlock: nbio_pcie0_bifplr6_cfgdecp`, from vendor/device ID through multicast capability receive bitmap setup.

## Important APIs, Types, and Macros

This header chunk defines no functions, structs, typedefs, enums, or storage. Its only API is the generated bitfield macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: zero-based bit position for the field.
- `<REGISTER>__<FIELD>_MASK`: already-shifted bit mask for the field.

Important `BIFPLR5_0` groups in this chunk include:

- `PCIE_RP_PIO_*`: root-port PIO status, mask, severity, system-error, and exception classification for configuration, I/O, and memory completion failures (`UR`, `CA`, and completion timeout), plus four full-dword TLP header logs and four full-dword TLP prefix logs.
- `PCIE_ESM_*`: Extended Speed Mode capability metadata, status, enable control, and seven capability dwords advertising many discrete ESM rates from 8.0 GT/s up through the 70 GT/s range.
- `DATA_LINK_FEATURE_*`: data-link feature exchange metadata such as local/remote data-link feature support and remote-valid status.
- `PCIE_PHY_16GT_*`, `LINK_*_16GT`, parity mismatch status, and `LANE_0` through `LANE_15_EQUALIZATION_CNTL_16GT`: 16 GT/s link capability/control/status and per-lane downstream/upstream TX preset and RX preset hint fields.
- `PCIE_MARGINING_*` and `LANE_0` through `LANE_15_MARGINING_LANE_{CNTL,STATUS}`: port and per-lane margining controls/status, including margin payloads, error counts, voltage/timing margins, receiver number, and usage model bits.
- `PCIE_CCIX_*` and `ESM_LANE_*_EQUALIZATION_CNTL_{20GT,25GT}`: CCIX capability headers, required/optional ESM capability, ESM status/control, per-lane equalization presets at 20 GT/s and 25 GT/s, and CCIX translation capability/control.

Important `BIFPLR6_0` groups include:

- Standard PCI/PCI bridge header fields: vendor/device ID, command/status, revision and class codes, cache line, latency, header/BIST, bus numbers, I/O and memory base/limit windows, prefetchable windows, ROM base, interrupt line/pin, IRQ bridge control, and extended bridge control.
- Power management and PCIe capability blocks: `PMI_*`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, slot/root capability and status/control, and PCIe capability version/type/interrupt fields.
- PCIe Capability 2 blocks: device, link, and slot capability/control/status 2, including completion timeout support/control, atomic operations, LTR, OBFF, ID ordering, E2E TLP prefix controls, target link speed, equalization, retimer and link-speed-vector fields.
- MSI, SSID, MSI map, vendor-specific enhanced capability, virtual-channel capability/resource fields, and device serial number fields.
- Advanced Error Reporting: uncorrectable error status/mask/severity, correctable error status/mask, ECRC and first-error-pointer control, header logs, root error command/status, error source IDs, and TLP prefix logs.
- Secondary PCIe capability and per-lane equalization: `PCIE_LINK_CNTL3`, lane error status, and `PCIE_LANE_0` through `PCIE_LANE_15_EQUALIZATION_CNTL`.
- Access Control Services and Multicast: ACS capability/control fields for source validation, translation blocking, peer-to-peer redirect, upstream forwarding, egress control, and direct translated P2P; multicast capability/control, address, receive, block, untranslated-block, and overlay BAR fields. This chunk stops after `BIFPLR6_0_PCIE_MC_RCV0__MC_RECEIVE_0__SHIFT`.

## Control Flow and Runtime Behavior

There is no runtime control flow in this chunk. The C preprocessor makes these field constants available to code that includes `nbio_7_2_0_sh_mask.h`.

Runtime behavior is implied by consumers that pair these masks with addresses from `nbio_7_2_0_offset.h` and use AMDGPU register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, `SOC15_REG_OFFSET`, and `REG_SET_FIELD`. The local C integration point is `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, which includes both the offset and shift/mask headers for NBIO 7.2.0.

The hardware flows represented by these definitions are:

1. PCI/PCIe enumeration and bridge setup read identity, class, header, bus-number, BAR/window, capability-pointer, interrupt, and status fields.
2. NBIO and PCIe setup code programs command, power management, PCIe device/link/slot/root controls, MSI mapping, bridge windows, virtual channels, ACS, and multicast policy through masked writes.
3. Link training, retimer/equalization, ESM, 16 GT/s, 20 GT/s, 25 GT/s, and lane-margining paths inspect or program per-lane presets, receiver hints, margin commands, error counts, and link status.
4. Error handling and diagnostics read AER status/mask/severity, DPC/RP PIO state, root error state, error source IDs, and logged TLP header/prefix dwords.
5. CCIX and multicast-capable configurations use the capability/control fields to advertise, enable, or constrain peer/interconnect behavior.

The header itself does not validate values, sequence hardware writes, clear status bits, or preserve any register state.

## State and Persistence

The macros are compile-time metadata and hold no software state. The represented state lives in NBIO PCIe configuration and extended-capability registers.

State categories represented by this chunk include:

- Enumeration and topology state: vendor/device IDs, class codes, bridge bus numbers, I/O and memory windows, prefetchable windows, ROM base, capability lists, device serial number, and subsystem/vendor IDs.
- Policy/control state: command enables, bridge controls, power-management controls, PCIe device/link/slot/root controls, completion timeout and LTR/OBFF controls, MSI mapping, virtual-channel resources, ACS isolation, multicast enablement, CCIX/ESM controls, and lane margin/equalization commands.
- Error and diagnostic state: DPC/RP PIO completion failure classification, AER uncorrectable/correctable status, masks and severities, ECRC control, root error command/status, error source IDs, lane error status, TLP header logs, and TLP prefix logs.
- Link and signal-integrity state: link speed/width/status, link training flags, equalization state, retimer presence, 16 GT/s parity mismatch status, per-lane equalization presets, and lane margining status and sample/error counters.
- Multicast state: maximum group/window sizing, enabled group count, address indexes and base addresses, receive bitmaps, block-all/untranslated filters, and overlay BAR sizing.

Persistence across GPU reset, PCI reset, function-level reset, suspend/resume, runtime power transitions, or BACO is determined by hardware and driver reinitialization, not by this header. A wrong mask or shift value is persistent in the compiled driver until the generated register header is corrected and rebuilt.

## Dependencies and Integration Points

The direct companion header is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h`, which supplies the address side of the same register map. The inspected tree has no sibling `nbio_7_2_0_default.h`; default/reset values, if needed, must come from hardware documentation, another generated source, or runtime reads.

Primary local integration points are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, which includes `nbio_7_2_0_offset.h` and `nbio_7_2_0_sh_mask.h` for NBIO 7.2 register access.
- SOC15/NBIO register access macros and bitfield helpers used across AMDGPU, especially `REG_SET_FIELD` and read/modify/write wrappers.
- PCIe/NBIO initialization, reset, doorbell, memory aperture, link-management, and diagnostics code that needs exact register-field geometry.
- Error handling, AER/RAS diagnostics, and link-training or signal-integrity tooling that decodes root-port PIO, AER, lane error, margining, and TLP log registers.

Integration is by exact generated symbol names. `BIFPLR5_0_*` and `BIFPLR6_0_*` identify different PCIe/root-port register images; structurally similar fields must still be paired with the matching offset macro and hardware block.

## Risks

- Chunk boundaries split register definitions. This range starts with only the mask half of `BIFPLR5_0_PCIE_RP_PIO_STATUS` and ends after only the shift half of `BIFPLR6_0_PCIE_MC_RCV0__MC_RECEIVE_0`.
- Many fields are repeated across lanes 0-15 and across speed families. Off-by-one lane use or mixing 16 GT/s, 20 GT/s, 25 GT/s, and base PCIe equalization fields can silently program the wrong lane or speed context.
- AER, DPC/RP PIO, root error, and lane-error registers have similar status/mask/severity/log naming. Confusing status with masks or severity can hide errors, misclassify fatality, or corrupt diagnostics.
- PCIe control fields affect bus behavior. Incorrect masks for maximum payload/read-request size, ASPM, target link speed, completion timeout, LTR, OBFF, ACS, VC resources, or multicast can cause enumeration failures, link instability, DMA isolation issues, or performance regressions.
- Lane margining and equalization controls are signal-integrity sensitive. Bad payload, receiver, timing, voltage, or preset fields can make hardware validation misleading or destabilize links during training.
- CCIX and ESM fields advertise and control high-speed/coherent interconnect behavior. Cross-wiring capability and control bits can expose unsupported rates or modes.
- Some capability/control fields share the same underlying register address in the offset header, with distinct bit ranges. Masked writes must preserve unrelated neighboring fields.
- The generated `L`-suffixed integer constants should be used with normal unsigned 32-bit register handling to avoid width/sign surprises in composed expressions.

## Test and Validation Signals

Useful validation signals for this chunk are mostly generated-header consistency checks plus hardware-level coverage:

- Build AMDGPU code paths that include `nbio_7_2_0_sh_mask.h` and `nbio_7_2_0_offset.h`, especially `amdgpu/nbio_v7_2.c`.
- After adjacent chunks are merged, verify every field has a matching `__SHIFT` and `_MASK` pair. Expected local boundary exceptions are the starting `BIFPLR5_0_PCIE_RP_PIO_STATUS` masks and the ending `BIFPLR6_0_PCIE_MC_RCV0` shift.
- Cross-check the 256 visible register blocks against `nbio_7_2_0_offset.h` so each mask block has a matching address macro where expected.
- Decode PCI config-space dumps from matching NBIO 7.2 hardware and compare vendor/device, bridge, PM, PCIe, MSI, VC, AER, ACS, multicast, CCIX, ESM, and lane fields against expected capability chains.
- Exercise PCIe AER/DPC diagnostics with controlled correctable, uncorrectable, root-port PIO, and lane-error events; confirm status, mask, severity, source ID, header log, and prefix log decoding.
- Validate link training and signal-integrity paths by reading and, where safe, programming per-lane equalization and margining registers across all 16 lanes.
- Validate ACS and multicast behavior through enumeration, peer-to-peer, DMA isolation, group/window sizing, receive bitmap, and blocked/untranslated traffic tests.
- Run suspend/resume, reset, and link retraining coverage to ensure runtime initialization restores policy fields and diagnostics still decode plausibly afterward.

## Chunk Boundary Notes

The chunk starts at line 85520 with `BIFPLR5_0_PCIE_RP_PIO_STATUS` masks; the matching shifts for that register are immediately before this chunk. Lines 85529-86731 complete the visible `BIFPLR5_0` tail from RP PIO controls/logs through ESM, data-link features, 16 GT/s PHY/link/lane fields, lane margining, CCIX, CCIX ESM equalization, and CCIX translation fields.

Line 86734 starts `addressBlock: nbio_pcie0_bifplr6_cfgdecp`. Lines 86735-87941 cover the beginning of the `BIFPLR6_0` PCIe root-port configuration image from standard PCI/bridge fields through PM, PCIe, MSI, vendor-specific, VC, AER, secondary PCIe, lane equalization, ACS, and the start of multicast capability fields. The next chunk is required for the rest of `BIFPLR6_0_PCIE_MC_RCV0` and later multicast/L1 PM/DPC fields.
