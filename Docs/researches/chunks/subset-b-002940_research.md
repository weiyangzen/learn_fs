# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 88737-91171

## Scope

This chunk is a generated AMDGPU NBIO 2.3 shift/mask header segment. It contains preprocessor constants only: 2,141 `#define` macros in this line range, split into 1,059 `__SHIFT` definitions and 1,082 `_MASK` definitions. There are no C functions, structs, enums, local variables, allocation paths, locks, loops, branches, or direct MMIO accesses in the chunk.

The range starts in the tail of `PSWUSCFG0_1_PCIE_ESM_CAP_5`, covers the remainder of the `PSWUSCFG0_1` PCIe extended capability surface, crosses into the `nbio_nbif0_bif_bx_pf_SYSPFVFDEC:1` indirect PF/VF MMIO window, then covers most of the `nbio_nbif0_bif_cfg_dev0_swds_bifcfgdecp` downstream-port PCI/PCIe configuration-space masks. It ends at the first fields of `BIF_CFG_DEV0_EPF0_1_COMMAND` in the next `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` address block, so both the first and last register groups are chunk-boundary partials.

Although this source path is under a local `ceph-client` mirror, the file is AMDGPU hardware metadata. It describes GPU NBIO/NBIF PCIe register fields, not Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header section is to publish the bit-level ABI for NBIO 2.3 PCIe configuration, link training, extended speed mode, margining, CCIX, downstream bridge, AER, ACS, data-link feature, and endpoint command fields. Matching offset macros in `nbio_2_3_offset.h` identify register addresses; this file identifies the bit positions and masks inside those registers.

Driver code consumes these macros through AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_*`, `WREG32_*`, PCI config access helpers, and SOC15/NBIO-specific wrappers. The macro names are the contract: a typo or stale mask generally still compiles if the macro exists, but it can make the driver program the wrong hardware bit.

The main hardware surfaces in this chunk are:

- `PSWUSCFG0_1` PCIe extended capability fields for ESM capability bitmaps, data-link feature exchange, 16 GT/s PHY status, lane equalization, PCIe receiver margining, CCIX ESM controls/status, 20 GT/s and 25 GT/s lane equalization presets, and CCIX optimized TLP format control.
- `BIF_BX_PF0_MM_INDEX`, `BIF_BX_PF0_MM_DATA`, and `BIF_BX_PF0_MM_INDEX_HI` fields for an indirect PF/VF MMIO index/data aperture.
- `BIF_CFG_DEV0_SWDS1_*` PCI-to-PCI bridge and PCIe downstream-port configuration fields, including standard PCI header fields, bridge base/limit windows, PM capability, PCIe capability, device/link/slot capability and control/status, MSI, SSID, vendor-specific capability, virtual channel resources, device serial number, AER, secondary PCIe capability, per-lane equalization, ACS, data-link feature, 16 GT/s PHY, and lane margining fields.
- A partial `BIF_CFG_DEV0_EPF0_1_*` endpoint config-space start covering vendor ID, device ID, and the beginning of the PCI command register.

## Important Macro Families

### PSWUSCFG0_1 ESM, DLF, PHY, Margining, And CCIX

The first line of the chunk is already inside `PSWUSCFG0_1_PCIE_ESM_CAP_5`, carrying the final shifts and all masks for ESM speed support bits from `ESM_19P0G` through `ESM_21P9G`. The next full groups continue this bitmap pattern:

- `PSWUSCFG0_1_PCIE_ESM_CAP_6` covers `ESM_22P0G` through `ESM_24P9G`.
- `PSWUSCFG0_1_PCIE_ESM_CAP_7` covers `ESM_25P0G` through `ESM_28P0G`.

These are one-bit support masks for extended speed mode data-rate steps. The field names encode decimal speeds using `P` in place of a decimal point, and the masks are sequential single-bit values. This is highly regular generated data, but regularity is also the risk: a one-bit shift or name drift can advertise or control the wrong speed capability.

`PSWUSCFG0_1_PCIE_DLF_ENH_CAP_LIST`, `DATA_LINK_FEATURE_CAP`, and `DATA_LINK_FEATURE_STATUS` define the enhanced capability header fields plus local and remote data-link feature support. The capability/status pair includes `DLF_EXCHANGE_ENABLE` and `REMOTE_DLF_SUPPORTED_VALID`, so users must distinguish advertised capability, exchange enablement, and valid remote status.

`PSWUSCFG0_1_PCIE_PHY_16GT_ENH_CAP_LIST`, `LINK_CAP_16GT`, `LINK_CNTL_16GT`, `LINK_STATUS_16GT`, `LOCAL_PARITY_MISMATCH_STATUS_16GT`, `RTM1_PARITY_MISMATCH_STATUS_16GT`, and `RTM2_PARITY_MISMATCH_STATUS_16GT` define the PCIe 16 GT/s PHY extended capability surface. The link status group exposes equalization-complete and phase-success bits plus link-equalization request status. The local/retimer parity status groups expose receiver/transmitter coefficient status mismatch bits.

`PSWUSCFG0_1_LANE_0_EQUALIZATION_CNTL_16GT` through `LANE_15_EQUALIZATION_CNTL_16GT` repeat the same per-lane fields: downstream-port TX preset, downstream-port RX preset hint, upstream-port TX preset, upstream-port RX preset hint, and a reserved bit. The mask pattern is identical per lane, so generated-header consistency checks should expect only the lane number to change.

`PSWUSCFG0_1_PCIE_MARGINING_ENH_CAP_LIST`, `MARGINING_PORT_CAP`, and `MARGINING_PORT_STATUS` describe PCIe receiver margining support. The port capability fields include whether independent error sampler, voltage offset, timing offset, sample reporting, maximum lanes, and margining-time capabilities exist. The port status fields track ready state, margin software-ready status, margin command complete, margin command status, sampled receivers, and lane margining active.

`PSWUSCFG0_1_LANE_0_MARGINING_LANE_CNTL` through `LANE_15_MARGINING_LANE_STATUS` repeat per-lane margining command/status fields. Control registers carry receiver number, margin type, usage model, and payload; status registers mirror receiver number status, margin type status, usage model status, and payload status.

`PSWUSCFG0_1_PCIE_CCIX_*` groups define the CCIX extended capability header, CCIX-specific header words, ESM capability/status/control, optional/reserved ESM capability, required speed support, per-lane 20 GT/s and 25 GT/s ESM equalization presets, and CCIX transaction capability/control. The `PCIE_CCIX_ESM_CNTL` fields include data-rate selections, perform-calibration, enable, extended equalization phase timeouts, link-reach target, retimer-present, and quick-equalization timeout selection.

### PF/VF Indirect MMIO Window

The `nbio_nbif0_bif_bx_pf_SYSPFVFDEC:1` address block in this chunk contains:

- `BIF_BX_PF0_MM_INDEX__BIF_BX_PF_MM_REG_ADDR`
- `BIF_BX_PF0_MM_INDEX__BIF_BX_PF_MM_APER`
- `BIF_BX_PF0_MM_INDEX__BIF_BX_PF_MM_WR_EN`
- `BIF_BX_PF0_MM_DATA__BIF_BX_PF_MM_DATA`
- `BIF_BX_PF0_MM_INDEX_HI__BIF_BX_PF_MM_REG_ADDR`

These macros describe an indirect index/data access mechanism, where software selects a target register address/aperture and write-enable state through index fields, then transfers data through the data field. The macros do not enforce ordering; the runtime code using the register pair must perform index/data sequencing correctly.

### BIF_CFG_DEV0_SWDS1 Standard Bridge Header

The `nbio_nbif0_bif_cfg_dev0_swds_bifcfgdecp` address block begins with the downstream-port bridge's standard PCI configuration header:

- Identity and class fields: vendor ID, device ID, revision ID, programming interface, subclass, and base class.
- Command/status fields: I/O access, memory access, bus master, SERR, interrupt disable, parity/error status, target/master abort status, DEVSEL timing, and capability-list presence.
- Header and BIST fields: cache line size, latency timer, header type, multi-function device, and BIST controls/status.
- Bridge BAR and bus-window fields: base addresses, primary/secondary/subordinate bus numbers, secondary latency, I/O base/limit, memory base/limit, prefetchable base/limit and upper 32-bit windows, high I/O base/limit, ROM base, interrupt line/pin, and IRQ bridge control.

These masks map directly to conventional PCI/PCIe bridge configuration-space fields. Some fields are control bits, some are status or write-one-clear style PCI status bits, and some are base/limit encodings that require PCI bridge window semantics outside this header.

### BIF_CFG_DEV0_SWDS1 Power Management And PCIe Capabilities

The PM capability groups include `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`. They define PM capability version, PME support, D1/D2 support, auxiliary current, power state, PME enable/status, data select/scale, and bus power enablement.

The PCIe capability groups include `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `SLOT_CAP`, `SLOT_CNTL`, `SLOT_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`, `SLOT_CAP2`, `SLOT_CNTL2`, and `SLOT_STATUS2`.

Notable field families include:

- Device error reporting enables/status bits for correctable, non-fatal, fatal, and unsupported-request conditions.
- Max payload size, max read request size, relaxed ordering, no-snoop, extended tags, atomics, ARI forwarding, LTR, OBFF, ten-bit tags, end-to-end TLP prefixes, and completion timeout controls.
- Link speed/width capability and status, ASPM/PM controls, common clock, link retrain/disable, bandwidth notification, DRS signaling, autonomous speed/width controls, equalization status, and retimer presence.
- Slot hot-plug, attention/power indicators, power controller, command complete, presence detect, data-link state change, physical slot number, and slot power limit fields.

### MSI, SSID, Vendor-Specific, VC, Serial Number, AER, Secondary, ACS, DLF, 16GT, And Margining

The SWDS1 MSI groups define the MSI capability list/header, address low/high, message data, 64-bit message data aliasing, mask, 64-bit mask aliasing, and pending fields. The overlapping MSI field names reflect PCI MSI layout variants; consumers must interpret them according to the MSI capability format, not as unique independent storage.

`BIF_CFG_DEV0_SWDS1_SSID_*` exposes subsystem vendor and subsystem IDs. `PCIE_VENDOR_SPECIFIC_*` exposes vendor-specific capability header and data words.

The VC enhanced capability block covers port VC capability/control/status, VC0 and VC1 resource capability/control/status, arbitration capability, TC/VC maps, load-table controls, and VC negotiation pending status. These fields affect virtual channel resource allocation and traffic class routing.

`PCIE_DEV_SERIAL_NUM_*` exposes the device serial number enhanced capability header and two data dwords.

The AER block exposes uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, header logs, and TLP prefix logs. The status/mask/severity macros distinguish DLP, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal errors, MC blocked TLP, atomic egress blocked, and TLP prefix blocked conditions.

The secondary PCIe capability block exposes link control 3, lane error status, and lane 0-15 equalization controls. Each lane equalization control repeats downstream TX preset, downstream RX preset hint, upstream TX preset, upstream RX preset hint, and reserved fields.

The ACS enhanced capability block exposes source validation, translation blocking, peer-to-peer request/completion redirect, upstream forwarding, peer-to-peer egress control, direct translated peer-to-peer, and egress control vector size/control enablement. These fields are especially sensitive for IOMMU, virtualization, and peer-to-peer isolation.

The SWDS1 DLF, 16 GT/s PHY, and margining groups mirror the same concepts as the earlier `PSWUSCFG0_1` groups, but under the downstream-port `BIF_CFG_DEV0_SWDS1_*` namespace. The 16 GT/s status and parity fields describe equalization phase status and coefficient mismatch states. The lane 0-15 margining control/status groups repeat receiver number, margin type, usage model, and payload fields.

### Partial Endpoint Config Start

The chunk ends after entering `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp`. It includes complete masks for `BIF_CFG_DEV0_EPF0_1_VENDOR_ID` and `DEVICE_ID`, then starts `BIF_CFG_DEV0_EPF0_1_COMMAND` with shifts for I/O access, memory access, bus mastering, special cycles, memory-write-invalidate, palette snoop, parity error response, address/data stepping, SERR, fast back-to-back, and interrupt disable. The corresponding masks for this command register continue in the next chunk.

## Control Flow

There is no executable control flow in this header chunk. The runtime flow is provided by C code that includes the generated NBIO 2.3 headers:

1. A driver path selects an ASIC/IP-version-specific register offset from `nbio_2_3_offset.h`.
2. It selects one or more field masks/shifts from this `nbio_2_3_sh_mask.h` file.
3. It reads or writes the register through PCI config, SMN, SOC15, or NBIO access helpers.
4. For field updates, it uses read/modify/write helpers or explicit mask/shift operations to preserve unrelated fields.
5. Hardware applies the effect as PCIe capability presentation, link training/equalization control, error reporting, margining, CCIX ESM control, bridge-window programming, MSI/VC/ACS setup, or endpoint command behavior.

In-tree include points for `nbio_2_3_sh_mask.h` are `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, and SMU11 PPT files `navi10_ppt.c` and `sienna_cichlid_ppt.c`. A direct symbol search over the main AMDGPU, PM, and display C/H trees did not find references to the exact `PSWUSCFG0_1_*`, `BIF_CFG_DEV0_SWDS1_*`, or `BIF_CFG_DEV0_EPF0_1_*` macro names from this chunk, so the most likely consumers are lower-level config-space tooling, generated-register consistency, hardware diagnostics, or indirect use through versioned include coverage rather than explicit named calls in the checked C files.

## State And Persistence Behavior

This header stores no software state and persists nothing to disk. Its macros describe hardware-backed state whose lifetime is controlled by reset type, PCIe configuration, firmware/BIOS setup, driver programming, power-state transitions, link retraining, hot reset/FLR, and SR-IOV or PF/VF policy where applicable.

The represented hardware state includes:

- ESM and CCIX capability, status, calibration, data-rate, retimer, timeout, and optimized TLP format fields.
- Data-link feature local/remote capability and exchange state.
- 16 GT/s equalization and parity mismatch status for local and retimer paths.
- Per-lane equalization presets and margining command/status payloads for 16 lanes.
- PF/VF indirect MMIO index/data aperture selector and data fields.
- PCI bridge config state: command, status, class, BARs, bus numbers, I/O and memory windows, prefetchable windows, ROM base, interrupts, and bridge control.
- PCIe PM, device, link, slot, MSI, SSID, vendor-specific, VC, serial-number, AER, secondary PCIe, ACS, DLF, PHY, and margining capability state.
- Endpoint vendor/device ID and PCI command state at the chunk tail.

Some fields are persistent configuration until reset or reprogramming, such as command bits, bridge windows, link controls, MSI control, VC resource controls, ACS controls, and CCIX/ESM controls. Other fields are live status, latched error, write-one-clear, log, or capability-reporting fields. The header does not encode those access semantics, so callers must rely on the PCIe specification, AMD's ASIC register database, and existing AMDGPU access patterns.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 2.3 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h`, which supplies the matching register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h`, which supplies generated defaults where available.
- AMDGPU register helper conventions such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and related NBIO/SMN/SOC15 access wrappers.
- PCI and PCIe config-space semantics for standard bridge headers, capabilities, enhanced capabilities, AER, ACS, MSI, VC, DLF, PHY, margining, and CCIX.

Important integration points are:

- NBIO bring-up and link-management code in `nbio_v2_3.c`, which includes this header family and programs PCIe, ASPM/LTR, clock-gating, interrupt, doorbell, and HDP-related NBIO state using adjacent NBIO 2.3 masks.
- MxGPU/virtualization code in `mxgpu_nv.c`, which includes this register family for NBIO state relevant to PF/VF coordination.
- SMU11 power-management code in `navi10_ppt.c` and `sienna_cichlid_ppt.c`, which includes the NBIO 2.3 masks and offsets for ASIC-specific power-management register access.
- Hardware debug or validation tooling that walks PCIe enhanced capabilities, checks lane equalization/margining status, reads AER logs, verifies ACS/VC setup, or inspects CCIX/ESM capability state.

## Risks And Edge Cases

- Generated hardware contract drift is the primary risk. A wrong shift or mask can compile cleanly but program or read the wrong bit in hardware.
- Chunk boundaries are artificial. The range starts mid-`PSWUSCFG0_1_PCIE_ESM_CAP_5` and ends mid-`BIF_CFG_DEV0_EPF0_1_COMMAND`; the final per-file report must merge adjacent chunks before claiming complete coverage of those registers.
- Repeated per-lane blocks are easy to corrupt mechanically. A lane-number mismatch, missing field, or copied mask from the wrong lane can break equalization or margining on one lane while others work.
- ESM speed capability bitmaps are sequential and dense. Off-by-one shifts can advertise unsupported speeds or hide supported speeds, causing link-training, CCIX, or diagnostic confusion.
- PCI status, AER status, slot status, and some error fields can have write-one-clear behavior. Treating all masks as ordinary persistent control bits can accidentally clear diagnostics or fail to clear latched errors.
- Bridge base/limit fields are encoded PCI windows, not raw byte addresses. Consumers must apply PCI bridge sizing/alignment rules when interpreting or programming them.
- MSI fields intentionally alias depending on 32-bit versus 64-bit MSI layout. Code must choose the proper interpretation based on MSI capability state.
- ACS and VC fields affect isolation and routing. Incorrect masks can break peer-to-peer isolation, IOMMU behavior, traffic class routing, or virtualization assumptions.
- Indirect MMIO index/data fields require strict sequencing. Writing data before the correct index/aperture/write-enable fields are set can target the wrong register.
- Link control, equalization, margining, CCIX ESM, and retimer fields are timing-sensitive. Bad field definitions can produce intermittent link training failures, margining timeouts, or speed-dependent behavior rather than immediate deterministic errors.

## Test Signals

Useful validation signals for this chunk are mostly generated-header checks, build coverage, and hardware/runtime PCIe tests:

- Build AMDGPU configurations that include `nbio_v2_3.c`, `mxgpu_nv.c`, `navi10_ppt.c`, and `sienna_cichlid_ppt.c`; missing renamed macros or include-order problems should surface at compile time.
- Run generated-header consistency checks: each field should usually have a matching `__SHIFT` and `_MASK`, masks should align with the shift and field width, and repeated lane 0-15 blocks should differ only in lane numbering.
- Compare representative fields against the matching `nbio_2_3_offset.h` register groups and AMD NBIO 2.3 register database, especially chunk-boundary groups, ESM capability bitmaps, PCIe AER/ACS groups, and per-lane equalization/margining blocks.
- Exercise PCIe enumeration and config-space reads for the downstream bridge and endpoint surfaces; vendor/device IDs, class code, capability pointers, bridge windows, MSI, AER, ACS, VC, DLF, PHY, and margining capability headers should decode correctly.
- Exercise link training, retraining, ASPM, LTR, and speed changes around 16 GT/s and extended-speed/CCIX capability paths. Failures can show up as bad negotiated speed/width, equalization phase failure, or repeated link retraining.
- Use PCIe AER injection or diagnostics where available; correctable and uncorrectable status/mask/severity fields should latch, report, and clear without disturbing unrelated fields.
- Validate ACS and VC behavior under IOMMU, peer-to-peer, and virtualization scenarios; routing or isolation regressions are strong indicators of mask drift.
- Exercise receiver margining diagnostics across all lanes; per-lane command/status payloads should be lane-correct and should not cross-write adjacent lane fields.
- Validate indirect PF/VF MMIO index/data access in any debug or virtualization path that uses this aperture; wrong register selection, stale data, or unexpected write effects point at index/data field drift.
