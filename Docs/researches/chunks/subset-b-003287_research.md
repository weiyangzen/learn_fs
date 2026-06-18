# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 68352-70765

## Purpose

This chunk is an auto-generated AMD NBIO 7.7 register shift/mask slice for PCIe/NBIO configuration-space fields. It closes the `BIFPLR1_0` root-port block with high-speed ESM, CCIX transaction, and 32 GT/s link capability/control/status fields, then starts the `// addressBlock: nbio_pcie0_bifplr2_cfgdecp` block and defines most of the `BIFPLR2_0` PCIe root-port configuration layout.

The file does not implement register access or policy. Its public surface is a large set of C preprocessor constants that encode bit positions and masks for AMDGPU code that reads, decodes, composes, or writes hardware register values through companion offset/default headers and AMDGPU register helpers.

## Public Surface In This Chunk

The exported API is entirely macro based:

- `REGISTER__FIELD__SHIFT` gives the field's bit offset.
- `REGISTER__FIELD_MASK` gives the field's mask in the raw register value.

The `BIFPLR1_0` tail contains per-lane ESM equalization presets for 25 GT/s lanes 0-15 plus the final lane-15 20 GT/s entry, CCIX transaction capability/control bits, and 32 GT/s link capability/control/status bits for equalization bypass, "no equalization needed", modified training sequence usage, precoding state, enhanced link behavior control, and equalization phase completion.

The `BIFPLR2_0` block begins with standard PCI/PCI bridge configuration header fields: vendor/device IDs, command/status, revision/class-code bytes, cache/latency/header/BIST, bus numbering, I/O and memory window registers, prefetchable window upper dwords, capability pointer, ROM base address, interrupt line/pin, extended bridge control, vendor capability, and subsystem IDs. It then covers PM capability/status-control, PCIe capability, MSI and MSI-map capability, SSID, vendor-specific enhanced capability, virtual channel, device serial number, AER, secondary PCIe, ACS, multicast, L1 PM substates, DPC, RP PIO, ESM, data-link feature, 16 GT/s PHY, and margining capability families.

The chunk ends inside the margining per-lane definitions at `BIFPLR2_0_LANE_12_MARGINING_LANE_CNTL`; adjacent chunks are required for the remaining lane-12 status and later lane margining registers.

## Important Register Families

The standard `BIFPLR2_0` PCI header fields define the root-port identity and bridge routing surface. `COMMAND` controls I/O, memory, bus-mastering, parity/SERR, and interrupt disable behavior. `STATUS` and `SECONDARY_STATUS` expose conventional PCI error and capability-list state. The bus-number and I/O/memory/prefetchable window masks describe how downstream address ranges are decoded, while `ROM_BASE_ADDR`, interrupt fields, bridge control, vendor capability, and subsystem ID fields provide the surrounding configuration-space identity and routing metadata.

The PM and PCIe capability groups expose power state, PME enable/status, D-state support, payload/read-request sizing, error reporting enables, relaxed/no-snoop ordering, FLR, link capability/control/status, slot capability/control/status, root control/status, and PCIe capability version/type fields. The PCIe 2.0 extension fields add completion timeout controls, ARI forwarding, AtomicOp, IDO, LTR, OBFF, 10-bit tags, end-to-end TLP prefix handling, emergency power reduction, supported/target link speeds, equalization completion status, de-emphasis, transmit margin, compliance/decode controls, lower SKP ordered-set support, DRS, and slot power-limit extensions.

The interrupt and ID-related capability groups include MSI capability list/control, message address/data fields, MSI-map capability/address fields, SSID fields, and vendor-specific enhanced capability header/data fields. These macros are used by code that needs to decode or program interrupt routing and AMD-specific PCIe capability payloads, but the header itself does not validate legal capability-chain ordering.

The virtual-channel group covers enhanced capability headers, port VC capability/control/status, VC0 and VC1 resource capabilities, arbitration table offset/load/select fields, VC ID/enable, traffic-class maps, reject-snoop behavior, and negotiation pending status. These fields affect traffic-class to virtual-channel mapping and need coordinated hardware policy outside this generated header.

The AER group is extensive. It includes uncorrectable error status/mask/severity bits for data-link protocol, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress block, TLP prefix block, and poisoned TLP egress block. Correctable error status/mask covers receiver error, bad TLP/DLLP, replay rollover, replay timer timeout, advisory non-fatal, correctable internal, and header-log overflow. AER capability/control, four TLP header-log dwords, root error command/status, source IDs, and TLP prefix logs complete the error reporting surface.

The secondary PCIe and lane equalization fields define link control 3, lane error status, PCIe lane equalization controls for lanes 0-15, and later PHY-16GT-specific equalization controls for lanes 0-15. The lane controls use uniform downstream/upstream TX preset and RX preset hint fields in the PCIe secondary capability, then PHY-specific 16 GT/s downstream/upstream TX preset fields. The `BIFPLR1_0` ESM equalization tail has the same repeated per-lane shape for 20/25 GT/s presets.

ACS, multicast, L1 PM substate, DPC, and RP PIO families expose higher-level PCIe containment and isolation behavior. ACS capability/control fields describe source validation, translation blocking, peer-to-peer redirection/completion redirection, upstream forwarding, egress control, direct-translated P2P, and egress vector presence. Multicast fields describe group count, window size, enablement, base address, receive/block-all vectors, and overlay BAR. L1 PM substate fields describe L1.1/L1.2 support and enablement, common-mode restore time, power-on scale/value, ASPM/PCI-PM L1.2 controls, and LTR threshold scale/value. DPC fields cover capability/control/status, containment interrupt/error flags, software trigger, DL-active indication, RP extension, PIO logging support, and error source IDs. RP PIO fields expose status, mask, severity, system-error, exception, header logs, implementation-specific logs, and prefix logs for config/I/O/memory unsupported-request, completer-abort, and completion-timeout cases.

The ESM, data-link feature, 16 GT/s PHY, and margining families are newer high-speed PCIe feature surfaces. ESM capability/header/status/control fields describe the enhanced speed mode capability and supported decimal data-rate bands from 8.0 GT/s through 28.0 GT/s across `PCIE_ESM_CAP_1` through `PCIE_ESM_CAP_7`. Data Link Feature fields advertise local scaled flow control, local feature support, exchange enablement, and remote support validity. The 16 GT/s PHY fields expose link status, local/RTM parity mismatch status, and per-lane presets. Margining fields expose whether margining uses software, readiness state, and per-lane control/status payload fields for receiver number, margin type, usage model, and payload.

## Control Flow And State

There is no runtime control flow in this header. The effective flow is compile-time substitution:

1. A driver translation unit includes `nbio_7_7_0_sh_mask.h`.
2. Code reads or prepares a matching NBIO/PCIe register value using a register address macro from `nbio_7_7_0_offset.h` or a related offset header.
3. The caller applies the generated `*_MASK` and `*_SHIFT` constants to extract, test, or compose an individual field.

The header stores no C state and has no persistence behavior of its own. Persistent state lives in the GPU's NBIO PCIe configuration registers. Some fields are stable identity/configuration fields, while others represent dynamic hardware state or side-effectful controls: PCI command enables, bridge windows, PME state, MSI routing, link training/equalization status, AER status/masks/severity, VC negotiation, ACS isolation, multicast windows, L1 PM substate controls, DPC containment status, RP PIO logs, ESM enablement, data-link feature exchange, PHY parity status, and margining command/status payloads.

## Dependencies And Integration Points

This chunk depends on AMD's generated register-header convention. The `_sh_mask` header supplies field bit positions and masks; `nbio_7_7_0_offset.h` supplies the matching `regBIFPLR...` register addresses and base indices for NBIO 7.7; and related default headers provide reset/default values where generated. Spot checks show `BIFPLR2_0` offsets in `nbio_7_7_0_offset.h`, such as `regBIFPLR2_0_VENDOR_ID`, `regBIFPLR2_0_PCIE_DPC_ENH_CAP_LIST`, `regBIFPLR2_0_PCIE_ESM_CAP_LIST`, and `regBIFPLR2_0_LANE_12_MARGINING_LANE_CNTL`.

The direct in-tree consumer for this generation is `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which includes `nbio/nbio_7_7_0_sh_mask.h`. Wider AMDGPU integration is through NBIO, SOC, PCIe, interrupt, power-management, reset, and error-reporting paths that use generated register macros with AMDGPU register access helpers.

The semantic dependencies are the PCI and PCI Express specifications for standard and bridge configuration headers, PM capability, MSI, PCIe capability, VC, AER, secondary PCIe/equalization, ACS, multicast, L1 PM substates, DPC, RP PIO, data-link feature exchange, PHY 16 GT/s, lane margining, CCIX transaction formats, and AMD-specific ESM/vendor capability definitions. This header names the fields but does not encode ordering rules, legal values, reset sequencing, write-clear behavior, or device-specific policy.

## Risks And Maintenance Notes

- The chunk is generated and highly repetitive. Small generation drift in a lane number, prefix, shift, or mask would be hard to notice in review but could decode or program the wrong hardware bit.
- The range starts mid-family in `BIFPLR1_0` and ends mid-family in `BIFPLR2_0` margining lane definitions. Cross-chunk reconciliation is needed for complete per-file coverage.
- These masks must match NBIO 7.7 exactly. Similar NBIO generations use nearby names and layouts, but register offsets, field widths, and feature presence can differ.
- Status and log registers may have hardware side effects such as write-one-to-clear semantics or capture-on-error behavior. A macro name and mask do not imply that generic read-modify-write is safe.
- Control fields for PCI command, bridge windows, MSI/MSI-map, link retraining/equalization, AER, VC, ACS, multicast, L1 PM substates, DPC, RP PIO, ESM, data-link features, and margining can affect interrupt delivery, memory decoding, isolation, error containment, power behavior, and PCIe link stability.
- Full-width masks such as `0xFFFFFFFFL` and high-bit masks with `L` suffixes should continue to be used through the established AMDGPU register helper types to avoid signedness or truncation mistakes.
- Per-lane families use uniform fields across lanes 0-15, but hardware may expose fewer active lanes depending on negotiated width, board routing, fuses, or runtime link state.

## Test Signals

Useful validation signals for this chunk are:

- Build coverage for AMDGPU translation units that include `nbio_7_7_0_sh_mask.h`, especially `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`.
- Static checks that every `*_SHIFT` macro in the slice has the expected matching `*_MASK`, masks align with shifts, and repeated lane families remain consistent across lanes.
- Cross-header checks that `BIFPLR1_0` and `BIFPLR2_0` register names in this slice have matching NBIO 7.7 offset definitions and appropriate generated defaults where expected.
- Runtime register dumps on NBIO 7.7 hardware comparing decoded vendor/device IDs, bridge windows, command/status bits, PM state, PCIe link speed/width, slot/root state, MSI fields, VC resources, AER status/masks/logs, ACS controls, multicast state, L1 PM substate settings, DPC/RP PIO status, ESM capabilities, data-link feature status, PHY parity status, and lane margining payloads against `lspci -vvxxx` and AMDGPU debug register reads.
- Error-path tests that inject or observe AER/DPC/RP PIO conditions and verify the driver reports, masks, clears, and logs the intended bits without touching unrelated status.
- Link and power-management tests around retrain-link, 16/32 GT/s equalization completion, per-lane preset programming, ESM enablement, L1.1/L1.2 transitions, LTR thresholds, PME/wake behavior, and lane margining readiness.
