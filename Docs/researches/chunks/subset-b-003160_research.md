# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 1-2445

## Purpose

This chunk is the opening portion of AMDGPU's generated NBIO 7.2 shift/mask header. It defines C preprocessor constants for bitfield positions in NBIF/BIF PCI configuration-space registers. The source path is under a `ceph-client` mirror, but this header is GPU register metadata and does not implement Ceph or distributed-filesystem behavior.

The range starts with the AMD MIT-style license and `_nbio_7_2_0_SH_MASK_HEADER` include guard, then covers generated `__SHIFT` and `_MASK` constants for root-complex PCI configuration decoder address blocks:

- The complete visible `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` block for `BIF_CFG_DEV0_RC`, from vendor/device identity through PCIe 5.0-style lane margining controls and statuses.
- The beginning of `nbio_nbif0_bif_cfg_dev1_rc_bifcfgdecp` for `BIF_CFG_DEV1_RC`, from vendor/device identity through most of `PCIE_UNCORR_ERR_STATUS`.

Within lines 1-2445 there are 2,147 `#define` entries across 271 commented register blocks: 185 `BIF_CFG_DEV0_RC` register blocks and 86 `BIF_CFG_DEV1_RC` register blocks. The defines comprise 1,074 `__SHIFT` constants and 1,072 complete `_MASK` constants within the requested range; the apparent mask deficit is a chunk-boundary artifact because line 2445 stops before the final two masks for `BIF_CFG_DEV1_RC_PCIE_UNCORR_ERR_STATUS`.

## Important APIs, Types, and Macros

There are no functions, structs, typedefs, or enums in this range. The public interface is the generated register-field macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: zero-based starting bit for a field.
- `<REGISTER>__<FIELD>_MASK`: the field mask already shifted into register position.

The `DEV0_RC` block defines standard PCI/PCI bridge configuration fields: vendor/device ID, command/status bits, revision and class codes, cache-line and latency fields, bridge header/BIST, two base-address registers, primary/secondary/subordinate bus numbering, I/O and memory windows, prefetchable memory windows, capability pointer, ROM BAR, interrupt line/pin, and bridge control. It also includes power-management capability and status/control fields such as PME support/status, D-state control, no-soft-reset, data select/scale, and bridge-extension flags.

The PCIe capability section of `DEV0_RC` includes capability-list metadata, PCIe capability type/version, root-port device capability/control/status, link capability/control/status, slot capability/control/status, root control/capability/status, and PCIe capability 2/link 2/slot 2 fields. These fields cover error-reporting enables, max payload and read-request sizes, relaxed ordering and no-snoop control, completion timeout policy, ARI forwarding, AtomicOp support/blocking, ID ordering, LTR, OBFF, target link speed, autonomous speed/width disable, equalization status, RTM presence detection, downstream component presence, and DRS signaling.

The interrupt and identity capability fields include MSI capability headers and message address/data registers, subsystem ID capability, MSI mapping capability, and vendor-specific PCIe enhanced capability header/payload registers. Full-dword scratch and message address/log fields use a shift of zero with `0xFFFFFFFFL`-style masks, while narrower registers use 8-bit, 16-bit, or sub-dword masks.

The virtual-channel and device serial number groups define VC enhanced capability headers, port VC capabilities/control/status, VC0/VC1 resource capability/control/status, and a two-dword PCIe device serial number. The AER group defines uncorrectable error status/mask/severity, correctable error status/mask, advanced error capability/control, header logs, root error command/status/source ID, and TLP prefix logs. Covered AER bits include data-link protocol, surprise down, poisoned TLP, flow-control protocol, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress blocked, TLP prefix blocked, and poisoned-TLP egress blocked.

The `DEV0_RC` secondary/link-extension tail defines PCIe secondary enhanced capability, link control 3, lane error status, per-lane 8 GT/s equalization controls for lanes 0-15, ACS capability/control, data-link feature exchange capability/status, PCIe 16 GT/s PHY enhanced capability, 16 GT/s link capability/control/status, parity mismatch status, per-lane 16 GT/s equalization controls for lanes 0-15, and lane margining capability/status plus lane margining control/status pairs for lanes 0-15.

The `DEV1_RC` block begins with the same root-complex structure and repeats the standard bridge header, PM, PCIe device/link/slot/root, MSI, SSID, MSI map, vendor-specific, virtual-channel, serial-number, and AER uncorrectable-status layout. This chunk ends before the last two masks of `BIF_CFG_DEV1_RC_PCIE_UNCORR_ERR_STATUS`, so the next chunk is required for complete `DEV1_RC` AER status and subsequent AER mask/severity definitions.

## Control Flow and Runtime Behavior

This header has no runtime control flow. It is consumed at compile time by AMDGPU code that pairs these constants with register offsets from the matching NBIO 7.2 offset header and with register read/modify/write helpers.

The implied hardware flows are:

1. NBIO or PCIe initialization reads identity, class, bridge, BAR/window, capability-list, and link-capability fields for the root-complex functions.
2. Driver setup programs command, bridge control, PM, PCIe device control, link control, MSI, ACS, VC, data-link feature, equalization, and margining fields using these masks.
3. Error-handling paths read AER status and root error fields, apply AER mask/severity policy, and decode header/TLP prefix logs for PCIe diagnostics.
4. Link-training, speed-change, and signal-integrity paths inspect negotiated width/speed, equalization state, 16 GT/s parity/mismatch status, and lane margining control/status fields.

The file itself does not perform register access, validate values, clear sticky status bits, or sequence link retraining or margining operations. Those semantics live in AMDGPU/NBIO code and the NBIO 7.2 hardware specification.

## State and Persistence

The header owns no mutable state, allocates no memory, persists no data, and performs no I/O. It describes bit layouts for hardware state stored in NBIO/BIF PCI configuration-space registers.

State represented by this chunk includes:

- PCI bridge identity and enumeration state: vendor/device IDs, revision/class codes, bridge header, bus numbers, memory and I/O windows, ROM BAR, capability pointer, and interrupt routing.
- Configuration policy state: command enables, bridge control, PM controls, PCIe error-reporting enables, payload/read-request sizing, relaxed-ordering/no-snoop controls, link controls, MSI setup, VC mapping, ACS policy, DLF exchange, and lane margining controls.
- Observation and diagnostic state: PCI/PCIe status bits, slot/root status, link status, AER uncorrectable/correctable status, root error status/source IDs, header logs, TLP prefix logs, lane error status, 16 GT/s parity mismatch status, and per-lane margining status.
- Link capability and training state: maximum and current link speed/width, ASPM and exit-latency capabilities, equalization controls/statuses, RTM presence indicators, DRS signaling, and 16 GT/s equalization metadata.

Persistence across GPU reset, PCI reset, function-level reset, suspend/resume, or power-gating is not described here. A wrong generated constant, however, persists in the compiled driver until the header is regenerated or patched and the driver is rebuilt.

## Dependencies and Integration Points

The direct companion header in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h`, which supplies the register address/offset side of the same NBIO 7.2 register map. No `nbio_7_2_0_default.h` or `nbio_7_2_0_smn.h` companion was present beside this header in the inspected directory.

Direct include sites found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, which includes both `nbio_7_2_0_offset.h` and `nbio_7_2_0_sh_mask.h`.
- Display resource files under `drivers/gpu/drm/amd/display/dc/resource/dcn301` and `dcn31`, which include the NBIO 7.2 offset header and may share the same register-map family for display-side address constants.

Likely integration areas are NBIO 7.2 ASIC bring-up, PCIe root-port setup, bridge/window programming, MSI configuration, AER/RAS diagnostics, link training and speed management, data-link feature negotiation, ACS isolation, virtual-channel traffic-class mapping, and PCIe 4.0/5.0 equalization or margining workflows.

Integration depends on exact symbol prefixes. `BIF_CFG_DEV0_RC_*` and `BIF_CFG_DEV1_RC_*` are structurally similar root-complex maps but refer to different NBIF configuration decoder address blocks.

## Risks

- The line range ends inside a register definition. `BIF_CFG_DEV1_RC_PCIE_UNCORR_ERR_STATUS` is missing its final `TLP_PREFIX_BLOCKED_ERR_STATUS_MASK` and `POISONED_TLP_EGRESS_BLOCKED_STATUS_MASK` entries from this chunk because they are on lines 2446-2447.
- Generated root-complex blocks are highly repetitive. Accidentally combining a `DEV0_RC` shift/mask with a `DEV1_RC` offset can decode the right-shaped field from the wrong hardware function.
- PCIe status, mask, severity, and control registers reuse very similar field names. Confusing AER status with mask or severity can hide real faults, generate noisy reporting, or misclassify fatal/nonfatal behavior.
- Link-control and training fields affect live PCIe topology. Wrong masks for target speed, autonomous speed/width disable, retrain, common clock, ASPM, equalization, DRS, or 16 GT/s controls can cause link instability, enumeration failures, or performance regressions.
- ACS, VC, MSI, PM, and bridge-window fields affect isolation, interrupt delivery, traffic-class routing, and resource decoding. Incorrect values can create DMA isolation issues, interrupt loss, resource conflicts, or broken power-management behavior.
- Lane equalization and margining definitions are dense and repeated for lanes 0-15. Off-by-one lane selection or copied constants from the wrong speed generation can mislead signal-integrity diagnostics.
- Many masks carry an `L` suffix and include full 32-bit values. Consumers should keep normal unsigned register-width handling when composing values to avoid width/sign surprises.

## Test and Validation Signals

Useful validation is mostly generated-header consistency plus hardware or emulator coverage:

- Build AMDGPU configurations that include `nbio_v7_2.c` and the NBIO 7.2 generated headers to catch malformed macros or duplicate definitions.
- After adjacent chunks are merged, check that every field has a matching `__SHIFT` and `_MASK` pair. For this chunk alone, expect the boundary exception at `BIF_CFG_DEV1_RC_PCIE_UNCORR_ERR_STATUS`.
- Cross-check register comments and macro prefixes against `nbio_7_2_0_offset.h` so each shift/mask block has a matching address macro where expected.
- Run symmetry checks between `BIF_CFG_DEV0_RC` and `BIF_CFG_DEV1_RC` for common bridge, PM, PCIe, MSI, SSID, MSI-map, vendor-specific, VC, serial-number, and AER groups, while accounting for chunk truncation of the `DEV1_RC` block.
- Decode PCI config-space dumps from NBIO 7.2 hardware for `DEV0_RC` and `DEV1_RC` and compare identity, bridge windows, PM, PCIe capability, MSI, VC, AER, link, equalization, and margining fields against expected values.
- Exercise PCIe AER paths with controlled correctable and uncorrectable errors, then confirm status, masks, severity, root error status/source ID, header log, and TLP-prefix decoding.
- Validate link speed changes, retraining, equalization reporting, 16 GT/s status, and margining controls/status on hardware that exposes these root-complex capabilities.
- Validate suspend/resume, reset, and runtime power transitions to confirm AMDGPU restores policy fields and can still decode status and diagnostic registers correctly.

## Chunk Boundary Notes

Lines 1-24 contain the license and include guard. Lines 25-1638 cover the visible `BIF_CFG_DEV0_RC` address block completely within this chunk, ending with lane 15 margining lane status.

Line 1639 starts `nbio_nbif0_bif_cfg_dev1_rc_bifcfgdecp`. Lines 1640-2445 cover `BIF_CFG_DEV1_RC` from vendor ID through the `ATOMICOP_EGRESS_BLOCKED_STATUS_MASK` entry of `PCIE_UNCORR_ERR_STATUS`. The remaining two masks for that same register and the following `DEV1_RC` AER definitions are outside this work item and belong to the next chunk.
