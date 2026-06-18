# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 54233-56614

## Scope

This chunk is a generated AMDGPU NBIO 7.0 shift/mask header segment. It contains 2,382 source lines in the requested range, including 1,100 `__SHIFT` constants, 1,082 `_MASK` constants, and 198 register comment markers. There are no C functions, structs, enums, storage declarations, locks, allocations, or executable statements here.

The range starts at the tail of `BIFPLR0_1_PCIE_L1_PM_SUB_CAP`, where only the final mask definitions are present because the shift definitions and first masks are in the previous chunk. It then completes the `BIFPLR0_1` L1 PM Substates, Downstream Port Containment, Root Port PIO error logging, and Enhanced Speed Mode capability register layouts. The range then enters `addressBlock: nbio_pcie0_bifplr1_cfgdecp` and covers most of the `BIFPLR1_1` PCI/PCIe bridge configuration space: classic PCI config fields, PCIe capability, MSI and subsystem IDs, vendor-specific and VC capabilities, AER, secondary PCIe capability, per-lane equalization controls for lanes 0-15, ACS, multicast, L1 PM Substates, DPC, Root Port PIO logging, and ESM capability registers through the middle of `BIFPLR1_1_PCIE_ESM_CAP_6`. The next chunk is required for the remaining `ESM_CAP_6` masks and later `BIFPLR1_1` registers.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield half of the generated NBIO 7.0 hardware register interface. Each hardware field is represented by:

- `<REGISTER>__<FIELD>__SHIFT`, the least significant bit position of the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate or update the field.

Runtime AMDGPU code combines these constants with addresses from `nbio_7_0_offset.h`/`nbio_7_0_smn.h`, defaults from `nbio_7_0_default.h`, and register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, and `WREG32_PCIE`. This range does not implement PCIe policy itself; it defines the software-visible bit layout needed by NBIO 7.0 bridge, PCIe link, error-reporting, isolation, multicast, and power-management paths.

## Important Macro Families

The `BIFPLR0_1` tail provides the second half of one PCIe root-port block:

- `BIFPLR0_1_PCIE_L1_PM_SUB_*` defines L1 PM Substates capability/control fields: L1.1/L1.2 support and enables, ASPM and PCI-PM enable bits, common-mode restore time, LTR L1.2 threshold value/scale, and T_POWER_ON scale/value.
- `BIFPLR0_1_PCIE_DPC_*` defines Downstream Port Containment enhanced capability headers, DPC trigger enables, completion/interrupt controls, software trigger, corrected-error enable, poison-egress blocking, trigger status/reason, root-port busy, first-error pointer, and DPC error source ID.
- `BIFPLR0_1_PCIE_RP_PIO_*` defines Root Port PIO status/mask/severity/sys-error/exception bits for configuration, I/O, and memory unsupported-request completions, completer aborts, and completion timeouts, plus TLP header logs, implementation-specific log, and prefix logs.
- `BIFPLR0_1_PCIE_ESM_*` defines Enhanced Speed Mode capability list/header/status/control and ESM capability bitmaps. The ESM bitmaps map one bit per tenth-GT/s bucket, from `ESM_2P5G` through the `ESM_CAP_7` region starting at `ESM_25P0G` and later values outside this chunk.

The `BIFPLR1_1` address block begins a repeated NBIO PCIe bridge/function register map:

- Standard PCI bridge config registers include vendor/device ID, command/status, revision/interface/class, cache/latency/header/BIST, secondary/subordinate bus numbers, I/O and memory windows, prefetchable base/limit upper halves, interrupt line/pin, bridge control, and extended bridge control.
- Power management and PCIe capability registers include PMI capability/status/control, PCIe capability flags, device capability/control/status, link capability/control/status, slot capability/control/status, root control/capability/status, and the PCIe 2.0 capability/control/status extensions.
- MSI and identity-related registers include MSI capability list/message control, message address/data fields, subsystem ID capability, MSI map capability/address, and vendor-specific enhanced capability headers.
- Virtual Channel registers define port VC capability/control/status and VC0/VC1 resource capability/control/status fields, including traffic-class maps, arbitration select/table offsets, load controls, and negotiation-pending status.
- AER registers define uncorrectable error status/mask/severity bits, correctable error status/mask bits, AER capability/control, header logs, root error command/status, error source IDs, and TLP prefix logs.
- Secondary PCIe capability registers define link control 3, lane error status, and per-lane equalization controls for lanes 0-15. Each lane equalization register provides downstream TX preset, downstream RX preset hint, upstream TX preset, and upstream RX preset hint fields.
- ACS registers define access-control capability and enable bits: source validation, translation blocking, peer-to-peer request/completion redirect, upstream forwarding, peer-to-peer egress control, direct translated peer-to-peer, and egress vector size.
- Multicast registers define multicast capability/control, MC base address words, receive vectors, block-all vectors, untranslated blocking vectors, and overlay BAR sizing/base fields.
- The second `BIFPLR1_1_PCIE_L1_PM_SUB_*`, `DPC_*`, `RP_PIO_*`, and `ESM_*` families mirror the `BIFPLR0_1` definitions for this bridge/function instance.

## APIs, Types, And Functions

There are no callable APIs or local C types in this source range. The API surface is the generated preprocessor namespace. Consumers depend on exact spelling and value consistency among register names, field names, shifts, masks, offsets, SMN names, and defaults.

The constants are untyped integer macros. The mask literals use an `L` suffix and cover 8-bit, 16-bit, and 32-bit config-space fields depending on the register. They describe bit placement only. They do not encode access permissions, side effects, write-one-to-clear behavior, sticky/latch behavior, polling rules, firmware ownership, reset domains, ordering requirements, or whether a field is implemented on a given ASIC/package. Those semantics must come from the hardware register database and the code path using the field.

## Control Flow

This header segment has no local control flow. Runtime flow is external:

1. AMDGPU code selects the NBIO 7.0 register address from the generated offset or SMN header.
2. It reads a register, decodes fields with these `__SHIFT`/`_MASK` constants, or composes a new register value with field helper macros.
3. The driver writes the result back, polls a status bit, forwards decoded status to error handling, or uses it in PCIe link/power-management policy.

Likely runtime flows touching this region include PCIe bridge enumeration support, bus-master/memory/interrupt enable handling, PCIe capability discovery, link capability reporting, link status diagnostics, ASPM/L1.1/L1.2 programming, MSI setup, AER error collection, DPC containment handling, ACS isolation policy, virtual-channel and multicast capability exposure, PCIe Gen3+ equalization diagnostics, and ESM capability reporting.

## State And Persistence Behavior

The header stores no state. It names hardware-visible state in NBIO 7.0 PCIe configuration and extended capability registers. Persistence is governed by PCIe config-space reset rules, NBIO reset domains, ASIC reset, firmware/BIOS initialization, Linux PCI core configuration, AMDGPU initialization, runtime power management, suspend/resume restore, GPU reset, and SR-IOV PF/VF ownership.

Represented state includes command enables, bridge window configuration, interrupt routing, PM status/control, device/link/slot/root capability and status, MSI address/data programming, VC negotiation and resource controls, AER masks/severity/status/logs, root error reporting, lane equalization presets and hints, ACS controls, multicast vectors and overlay BAR fields, L1 Substate timing/control, DPC control/status/source, Root Port PIO error classifications and logs, and ESM supported-speed bitmaps.

Many status and error fields are not ordinary persistent storage. AER, Root Port PIO, DPC, lane error, link status, and root error status fields may be sticky, write-one-to-clear, hardware-updated, or interrupt-coupled depending on the underlying register semantics. Command/control fields such as bus mastering, memory access, ASPM/L1 Substates, DPC trigger/interrupt enable, ACS redirect, multicast enable, and bridge windows can affect live traffic and isolation.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 7.0 register database and must stay aligned with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_offset.h` for matching config/SMN register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_smn.h` for SMN-addressed register names used by PCIE/NBIO access helpers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_default.h` for reset/default values. The companion defaults include the same `smnBIFPLR0_1` and `smnBIFPLR1_1` register families, including L1 PM Substates, DPC, RP PIO, ESM, PCIe capability, AER, lane equalization, ACS, and multicast defaults.

Direct include users in this source tree are `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, `drivers/gpu/drm/amd/amdgpu/soc15.c`, and `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`. Display resource files include the NBIO 7.0 offset header for address-level integration. The functional NBIO 7.0 code around these includes manages revision detection, memory-controller access, doorbell ranges, HDP remaps, clock gating, interrupt handling, GPU virtualization, and PCIe/NBIO register access; this chunk supplies part of the bitfield vocabulary for that broader surface.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware metadata and has no direct Ceph or distributed-filesystem behavior.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while causing wrong PCIe config-space decoding or programming. The highest-risk fields in this chunk are bridge command/window bits, AER status/mask/severity, DPC control/status, ACS controls, L1 Substate enables/timing, lane equalization fields, multicast vectors, and error log fields.
- The range begins and ends mid-register-family. `BIFPLR0_1_PCIE_L1_PM_SUB_CAP` is incomplete without the previous chunk, and `BIFPLR1_1_PCIE_ESM_CAP_6` is incomplete without the next chunk.
- The `BIFPLR0_1` and `BIFPLR1_1` families are repetitive by design. A difference in prefix may simply identify another bridge/function instance, while a mismatched mask width or shift can indicate register-database or generator drift.
- Some PCIe status and error fields may be write-one-to-clear, latched, or hardware-updated. Blind read-modify-write sequences can accidentally clear events, preserve stale error bits, or change interrupt behavior.
- ACS, multicast, bridge window, and command-register fields affect DMA reachability, peer-to-peer routing, memory/I/O forwarding, and isolation. Incorrect values can create functional failures or security/isolation regressions.
- L1 PM Substates and link/equalization controls affect live PCIe link behavior. Bad settings can produce link training failures, retrains, poor resume behavior, timeouts, or AER storms.
- DPC and Root Port PIO fields are tied to containment and error reporting. Incorrect masks or enables can hide endpoint failures, over-report benign errors, or leave a device contained unexpectedly.
- ESM capability bitmaps encode advertised speed support. A one-bit shift error can misreport supported link speeds to later policy code or diagnostics.

## Test Signals

- Build AMDGPU with SOC15/NBIO 7.0 and SMU10 support enabled. Direct macro users catch missing or renamed generated symbols.
- Run generated-header consistency checks against the authoritative NBIO 7.0 register database: offset/default/shift/mask name alignment, mask-width checks, field non-overlap checks, and repeated-instance comparisons between `BIFPLR0_1` and `BIFPLR1_1`.
- Validate chunk boundaries during merge: `BIFPLR0_1_PCIE_L1_PM_SUB_CAP` should be complete when the previous chunk is present, and `BIFPLR1_1_PCIE_ESM_CAP_6` should continue with the remaining shifts/masks in the next chunk.
- On NBIO 7.0 hardware, boot and enumerate PCIe devices while checking negotiated link width/speed, link status, AER counters, DPC status, and absence of unexpected PCIe error logs.
- Exercise suspend/resume, runtime power management, GPU reset, and link retraining paths with ASPM/L1.1/L1.2 enabled and disabled to catch L1 Substate field regressions.
- Run PCIe error-injection or fault tests where available to confirm AER, Root Port PIO, DPC status/source/log fields decode as expected.
- Validate ACS/IOMMU isolation and peer-to-peer DMA behavior on platforms where ACS policy matters.
- Use lane equalization diagnostics on high-speed links to check per-lane preset/hint decoding for lanes 0-15.
- Compare visible defaults against `nbio_7_0_default.h` and hardware reset reads for representative registers such as L1 PM Substate controls, AER masks/severity, lane equalization defaults, RP PIO masks, and ESM capability bitmaps.
