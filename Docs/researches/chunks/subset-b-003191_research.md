# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 75797-78230

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.2.0 shift/mask header. It defines C preprocessor constants used to extract or compose fields in NBIO PCIe/BIF port registers. The macros describe bit geometry only; they do not implement Ceph, filesystem, or runtime driver logic despite the source tree path.

The range contains 2,161 `#define` entries: 1,083 `__SHIFT` definitions and 1,116 `_MASK` definitions, plus commented register-block markers. The shift/mask imbalance is mostly a chunk-boundary artifact: the range starts at the first shift for `BIFPLR1_0_PCIE_ESM_CAP_7`, while its comment marker is immediately above the chunk, and it ends inside `BIFPLR2_0_PCIE_ESM_CAP_5` after only the first five shift definitions.

At a high level, the chunk covers:

- The tail of the `BIFPLR1_0` PCIe link/root-port capability region: ESM advertised speed bits through 28.0 GT/s, Data Link Feature capability/status, 16 GT/s PHY equalization status and lane presets, PCIe lane margining controls/status for lanes 0-15, CCIX capability/ESM controls, 20 GT/s and 25 GT/s ESM lane equalization presets, and CCIX optimized TLP format capability/control.
- The start and most of the `BIFPLR2_0` address block (`nbio_pcie0_bifplr2_cfgdecp`): bridge-style PCI configuration header, PM and PCIe capability fields, MSI, SSID, MSI mapping, vendor-specific capability, virtual channel capability, device serial number, AER, secondary PCIe capability, ACS, multicast, L1 PM substates, DPC, root-port PIO error logging, and ESM capability fields through part of `PCIE_ESM_CAP_5`.

## Important APIs, Types, and Macros

There are no functions, structs, typedefs, enums, or callable APIs in this range. The public surface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: zero-based bit position for a field.
- `<REGISTER>__<FIELD>_MASK`: field mask already shifted into register position.

The `BIFPLR1_0` portion begins with `PCIE_ESM_CAP_7`, a dense bitmap of ESM supported rates from `ESM_25P0G` through `ESM_28P0G`. It then defines:

- `PCIE_DLF_ENH_CAP_LIST`, `DATA_LINK_FEATURE_CAP`, and `DATA_LINK_FEATURE_STATUS`: enhanced capability header fields, local scaled-flow-control support, local/remote DLF support bitmaps, exchange enable, and remote-support-valid status.
- `PCIE_PHY_16GT_ENH_CAP_LIST`, `LINK_CAP_16GT`, `LINK_CNTL_16GT`, and `LINK_STATUS_16GT`: 16 GT/s capability header plus equalization complete, phase success, and link equalization request bits. `LINK_CAP_16GT` and `LINK_CNTL_16GT` are represented as full-width reserved fields.
- `LOCAL_PARITY_MISMATCH_STATUS_16GT`, `RTM1_PARITY_MISMATCH_STATUS_16GT`, and `RTM2_PARITY_MISMATCH_STATUS_16GT`: 16-bit parity mismatch status vectors.
- `LANE_0_EQUALIZATION_CNTL_16GT` through `LANE_15_EQUALIZATION_CNTL_16GT`: per-lane downstream/upstream 16 GT/s transmit preset nibbles.
- `PCIE_MARGINING_ENH_CAP_LIST`, `MARGINING_PORT_CAP`, `MARGINING_PORT_STATUS`, and `LANE_0_MARGINING_LANE_CNTL/STATUS` through `LANE_15_MARGINING_LANE_CNTL/STATUS`: software margining support/readiness plus per-lane receiver number, margin type, usage model, and payload command/status fields.
- `PCIE_CCIX_*`: CCIX enhanced capability list, header dwords, ESM support capability, required/optional ESM speed support, ESM status/control, 20 GT/s and 25 GT/s lane preset fields, and optimized TLP format support/enable.

The `BIFPLR2_0` address block starts with standard PCI/PCIe bridge configuration fields:

- Identity and bridge header: vendor/device ID, `COMMAND`, `STATUS`, revision, programming interface, subclass/base class, cache line, latency, header, BIST, primary/secondary/subordinate bus numbers, I/O and memory base/limit windows, prefetchable windows, ROM base, interrupt line/pin, bridge control, vendor capability list, and adapter ID.
- PM capability/status-control: capability list metadata, version, PME support/status, D-state selection, no-soft-reset, data select/scale, and bridge-extension bits.
- PCIe capability: device/link/slot/root capabilities and control/status fields, including error reporting enables, payload/read-request sizing, ASPM/RCB/link disable/retrain controls, negotiated link state, slot controls/status, root error command/status, and PCIe 2.0 device/link/slot secondary fields.
- MSI, SSID, MSI map, vendor-specific, virtual-channel, and device-serial-number capability structures.
- AER: uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, header logs, root error command/status, source IDs, and TLP prefix logs.
- Secondary PCIe capability: link control 3, lane error status, and lane 0-15 equalization controls.
- ACS, multicast, L1 PM substate, DPC, root-port PIO status/mask/severity/sys-error/exception/header/prefix logs, and ESM capability list/header/status/control plus ESM capability bitmaps through `PCIE_ESM_CAP_4` and the first shifts of `PCIE_ESM_CAP_5`.

## Control Flow and Runtime Behavior

This header has no runtime control flow. It is included at compile time so AMDGPU/NBIO code can pair these field macros with register addresses from the matching offset header and with register access helpers.

The implied hardware flows are:

1. PCIe/NBIO initialization and enumeration read or program `BIFPLR2_0` identity, command, bridge-window, bus-number, capability-list, PM, and PCIe control/status fields.
2. Link setup and diagnostics use `BIFPLR1_0` and `BIFPLR2_0` link capability/control/status fields for 16 GT/s equalization, lane error status, 20/25 GT/s ESM presets, DLF exchange, and link margining.
3. Error handling reads AER, DPC, root error, and root-port PIO fields, applies mask/severity policy, and can decode header or prefix logs for failing TLPs.
4. Power-management code inspects and programs PM capability fields and L1 PM substate timing/power controls.
5. Isolation and topology code uses ACS, multicast, virtual-channel, bridge-window, slot/root, and ESM capability data to configure or validate port behavior.

The header itself does not sequence any of those operations, poll readiness, clear latched error bits, validate field values, or persist state.

## State and Persistence

The file owns no memory, allocates no objects, performs no I/O, and persists nothing. The represented state is hardware register state in NBIO/BIF PCIe configuration space.

State categories represented in this chunk include:

- Link capability and training state: DLF exchange/support, 16 GT/s equalization status, per-lane 16/20/25 GT/s transmit presets, lane margining command/status, lane error status, and ESM supported-rate bitmaps.
- PCI bridge identity and routing state: IDs, class codes, command/status, bus numbering, I/O and memory aperture windows, ROM base, interrupt pins, and bridge controls.
- PCIe policy state: device/link/slot/root controls, payload sizes, error-reporting enables, ASPM/L1-substate configuration, MSI control, VC setup, ACS controls, multicast routing/filtering, DPC enables, and ESM controls.
- Diagnostic state: parity mismatch vectors, AER status/mask/severity, root error status, DPC status/source, RP PIO status/mask/severity/sys-error/exception, and TLP header/prefix logs.

Persistence across GPU reset, PCI reset, FLR, suspend/resume, runtime power transitions, or BACO is not specified by this generated header. A wrong macro value would persist in the compiled driver until the generated register header is corrected and rebuilt.

## Dependencies and Integration Points

The direct companion file in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h`, which supplies the register offsets and base indices for this NBIO 7.2.0 register map. For example, it has matching offset entries for `regBIFPLR1_0_PCIE_DLF_ENH_CAP_LIST`, `regBIFPLR2_0_VENDOR_ID`, `regBIFPLR2_0_PCIE_DPC_CNTL`, and `regBIFPLR2_0_PCIE_ESM_CAP_5`. This directory contains only the `nbio_7_2_0_offset.h` and `nbio_7_2_0_sh_mask.h` companions for the 7.2.0 variant.

Likely integration areas in AMDGPU include:

- NBIO 7.2.0 ASIC bring-up code that includes generated ASIC register headers.
- PCIe root-port or bridge configuration code that programs `BIFPLR2_0` command, windows, bus numbers, PM, PCIe device/link/slot/root, MSI, VC, ACS, multicast, L1 PM, and DPC fields.
- Link training and PHY diagnostics paths that decode 16 GT/s equalization, lane margining, CCIX/ESM, and 20/25 GT/s per-lane preset fields.
- RAS/AER recovery paths that decode AER, DPC, root error, RP PIO, parity mismatch, TLP header, and TLP prefix logs.
- Power-management and suspend/resume paths that restore PM and L1 PM substate policy fields after hardware reset or low-power transitions.

Integration depends on exact symbol names. `BIFPLR1_0_*` and `BIFPLR2_0_*` are not interchangeable even when their field layouts resemble generic PCIe capability structures.

## Risks

- Chunk boundaries split definitions. The `BIFPLR1_0_PCIE_ESM_CAP_7` comment is just before this range, and `BIFPLR2_0_PCIE_ESM_CAP_5` continues after line 78230. Pair-completeness checks must run after adjacent chunks are merged.
- Repeated lane blocks are mechanically similar across lanes 0-15 and across 16/20/25 GT/s variants. A single wrong lane number or speed suffix can silently tune or decode the wrong lane.
- Status, mask, severity, control, and log registers have similar field names in AER, DPC, and RP PIO sections. Confusing them can hide errors, classify errors incorrectly, or corrupt diagnostics.
- Bridge aperture and bus-number fields affect PCI routing. Incorrect masks for I/O, memory, prefetchable, or bus-range fields can break enumeration or misroute transactions.
- Link and power controls such as ASPM, L1 PM substate timing, equalization presets, DLF exchange, DPC enable, ACS, VC, multicast, and ESM controls can affect link stability, power behavior, isolation, and recovery.
- Full-dword log fields and dense ESM support bitmaps look simple but are easy to misattribute to the wrong port/function prefix.
- Many masks use small-width or full-width literals with an `L` suffix. Consumers should keep normal unsigned register-width handling when shifting or composing fields.

## Test and Validation Signals

Useful validation is mostly generated-header consistency plus hardware or emulator coverage:

- Build AMDGPU configurations that include NBIO 7.2.0 headers to catch malformed macro names, duplicate definitions, or missing dependencies.
- After adjacent chunks are merged, verify every field has the expected `__SHIFT` and `_MASK` pair; the local expected exceptions are the boundary around `BIFPLR1_0_PCIE_ESM_CAP_7` and the incomplete ending `BIFPLR2_0_PCIE_ESM_CAP_5`.
- Cross-check all visible register names against `nbio_7_2_0_offset.h` so field macros have matching offset macros where expected.
- Run symmetry checks across lane 0-15 equalization and margining blocks, ensuring identical field geometry with only the lane number and speed suffix changing.
- Decode PCIe configuration dumps from NBIO 7.2.0 hardware and compare bridge header, capability-list, PM, PCIe, MSI, VC, ACS, multicast, DPC, AER, RP PIO, and ESM fields against expected register values.
- Exercise link training and margining diagnostics, confirming 16 GT/s equalization status, per-lane presets, margining readiness, command payloads, and status payloads decode correctly.
- Inject or observe PCIe AER/DPC/root-port PIO errors and confirm status, masks, severities, source IDs, header logs, prefix logs, and DPC controls decode as intended.
- Validate suspend/resume, reset, and low-power transitions to ensure driver code restores policy fields that this header describes but does not itself persist.

## Chunk Boundary Notes

The range begins at line 75797 with `BIFPLR1_0_PCIE_ESM_CAP_7__ESM_25P0G__SHIFT`; the `//BIFPLR1_0_PCIE_ESM_CAP_7` marker is line 75796, just outside the requested chunk. Lines 75859-76527 complete the visible `BIFPLR1_0` tail from DLF through CCIX transfer control.

Line 76530 starts `// addressBlock: nbio_pcie0_bifplr2_cfgdecp`, followed by the `BIFPLR2_0` bridge/root-port-style configuration image. The chunk ends at line 78230 after `BIFPLR2_0_PCIE_ESM_CAP_5__ESM_19P4G__SHIFT`; the remaining shifts and masks for `PCIE_ESM_CAP_5` continue in the next work item.
