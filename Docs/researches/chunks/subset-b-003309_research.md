# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 120813-123212

## Scope

This chunk is a generated AMDGPU NBIO 7.7.0 shift/mask header segment. It contains 2,173 `#define` constants and 225 register/address-block comments. There are no functions, structs, enums, variables, branches, loops, locks, allocations, direct MMIO operations, or persistence code in this range.

The slice starts inside `BIFPLR0_2_PCIE_UNCORR_ERR_MASK`, with the final seven AER uncorrectable error-mask constants for unsupported request through poisoned TLP egress blocked. It then covers the tail of the `BIFPLR0_2` PCIe root-port capability map through 16 GT and 32 GT link capability/status fields, begins `addressBlock: nbio_pcie0_bifplr1_cfgdecp`, and continues through `BIFPLR1_2_PCIE_L1_PM_SUB_CNTL`. The matching tail of `BIFPLR1_2_PCIE_L1_PM_SUB_CNTL` and later BIFPLR1_2 extended capabilities are outside this chunk.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMD GPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

`nbio_7_7_0_sh_mask.h` publishes bitfield geometry for the NBIO 7.7.0 register database. For each field it emits:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used to extract or encode the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, clear, preserve, or compose the field.

This chunk describes PCI and PCI Express configuration-space layouts for NBIO `BIFPLR*_2` port instances. Runtime AMDGPU code combines these constants with sibling offset/default headers and register helpers to decode link state, configure bridge and PCIe controls, route MSI, inspect PCIe errors, expose capability chains, and restore hardware policy after reset or power transitions. The header itself only describes bit locations; it does not encode access permissions, reset defaults, side effects, timing, ownership, or protocol sequencing rules.

## Important Macro Families

The opening `BIFPLR0_2` section finishes AER uncorrectable error mask fields and then defines related AER severity, correctable error status/mask, advanced error capability/control, TLP header logs, root error command/status, error source IDs, and TLP prefix logs. Covered error categories include data link protocol, surprise down, poisoned TLP, flow control, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic-op egress blocked, TLP-prefix blocked, and poisoned-TLP egress blocked.

The `BIFPLR0_2` secondary PCIe and lane-training area defines enhanced capability list headers, Link Control 3, lane error status, and lane 0 through lane 15 equalization controls. Each lane equalization register has downstream TX preset, downstream RX preset hint, upstream TX preset, and upstream RX preset hint fields. These constants are used for PCIe Gen3+ equalization diagnostics and policy programming.

The `BIFPLR0_2` ACS, multicast, and L1 PM substate sections describe access-control policy, multicast routing windows/bitmaps, and PCI-PM/ASPM L1.1/L1.2 capability and control timing. These fields affect peer-to-peer routing, IOMMU isolation expectations, multicast address filtering, latency tolerance, and link power behavior.

The `BIFPLR0_2` DPC and Root Port PIO sections define Downstream Port Containment capability/control/status/source fields and root-port PIO status, mask, severity, system-error, exception, header log, and TLP prefix log fields. These are diagnostic and recovery-oriented registers for downstream PCIe error containment and root-port error logging.

The `BIFPLR0_2` ESM block defines ESM capability-list metadata, vendor headers, status/control fields, and capability bitmaps `PCIE_ESM_CAP_1` through `PCIE_ESM_CAP_7`. The bitmap macros enumerate supported ESM data-rate points from 8.0G through 28.0G in 0.1G increments, plus 16 GT and 32 GT link-capability/status/control fields covering equalization bypass, modified TS usage modes, 32 GT precoding, enhanced link behavior control, no-equalization-needed signaling, and link equalization request/status.

The `BIFPLR1_2` block begins a second mechanically similar PCIe bridge/root-port instance. This chunk covers its conventional PCI bridge identity and decode fields, PM capability, PCIe device/link/slot/root capabilities and controls, MSI capability and MSI map fields, subsystem ID, vendor-specific enhanced capability, virtual-channel capability/resource fields, device serial number, AER status/mask/severity/log/root-error fields, secondary PCIe link/equalization controls for lanes 0-15, ACS capability/control, multicast capability/control/address/receive/block/overlay fields, and the start of L1 PM substate capability/control fields.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The exported interface is the preprocessor macro namespace:

- `BIFPLR0_2_*__SHIFT` and `BIFPLR0_2_*_MASK` for the tail of one NBIO 7.7.0 PCIe port capability map.
- `BIFPLR1_2_*__SHIFT` and `BIFPLR1_2_*_MASK` for the beginning and middle of the next PCIe port capability map.

The values are untyped integer literals, commonly with an `L` suffix for masks. Consumers must pair them with the matching register address namespace from `nbio_7_7_0_offset.h` and, where relevant, default values from `nbio_7_7_0_default.h`. In-tree integration for this generated header is visible in `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which includes both `nbio_7_7_0_offset.h` and `nbio_7_7_0_sh_mask.h`; `amdgpu_discovery.c` wires `nbio_v7_7_funcs` for discovered NBIO 7.7 hardware.

## Control Flow

This header has no runtime control flow. Runtime behavior is entirely in consumers:

1. AMDGPU or PCI-related code selects a NBIO 7.7.0 register offset for a specific `BIFPLR0_2` or `BIFPLR1_2` port instance.
2. Code reads a configuration, SMN, or MMIO-backed register through the relevant AMDGPU access helper.
3. It applies `__SHIFT` and `_MASK` constants, often through generated-register helper macros, to decode state or compose an updated value while preserving unrelated bits.
4. It reports status, changes policy, clears sticky error state according to hardware rules, restores reset/suspend state, or coordinates with the Linux PCI core and platform firmware.

Likely runtime contexts include PCIe bridge resource setup, root-port capability exposure, MSI programming, AER and DPC diagnostics, link retraining/equalization, link speed capability handling, ASPM/L1 PM substate policy, ACS routing/isolation, multicast and virtual-channel configuration, hotplug/slot state reporting, GPU reset, and suspend/resume restore.

## State And Persistence Behavior

The chunk owns no software state and writes no persistent data. It describes hardware-backed state in NBIO PCIe configuration registers. Persistence and reset behavior are determined by GPU reset domains, conventional PCIe reset, link reset/retrain, firmware setup, platform power policy, Linux PCI core actions, and AMDGPU restore logic.

Represented state includes capability declarations, writable control policy, hardware-updated link and slot status, bridge bus/window decode values, MSI routing values, PM/ASPM/LTR/OBFF policy, AER status/masks/severities/logs, root error command/status/source IDs, lane equalization presets and hints, ACS routing/isolation controls, multicast group/window/receive/block bitmaps, DPC containment status, Root Port PIO diagnostics, ESM rate-capability bitmaps, and 16 GT/32 GT equalization status. Some fields are read-only capabilities, some are ordinary writable controls, some are sticky status, and some may be write-one-to-clear; the shift/mask header does not distinguish those cases.

## Dependencies And Integration Points

Primary dependencies are the sibling generated NBIO 7.7.0 metadata files:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h` for register offsets and address symbols.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_default.h` for reset/default values where generated.
- AMDGPU register helpers and bitfield helper macros used by NBIO, SOC15, PCIe, RAS, reset, and power-management code.

Direct in-tree integration includes `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which uses the NBIO 7.7 register database for HDP flush offsets, PCIe index/data offsets, doorbell aperture controls, IH control, memory-controller access gating, clock-gating/light-sleep controls, initialization, and register remapping. The discovery path in `amdgpu_discovery.c` selects `nbio_v7_7_funcs` for matching hardware.

External integration surfaces include Linux PCI enumeration and resource assignment, PCIe AER/DPC infrastructure, MSI interrupt delivery, IOMMU and peer-to-peer routing policy, firmware-owned configuration setup, platform ASPM and L1 substate policy, GPU reset recovery, suspend/resume, and diagnostic tools that dump or decode PCIe configuration space.

## Risks And Edge Cases

- Chunk boundaries are artificial: the first lines are only the final masks for `BIFPLR0_2_PCIE_UNCORR_ERR_MASK`, and the final lines stop inside `BIFPLR1_2_PCIE_L1_PM_SUB_CNTL` before all masks for that register are present.
- Generated macro drift can compile cleanly while causing a caller to decode or program the wrong PCIe bit. Errors here can break link training, enumeration, interrupt routing, power management, error reporting, or isolation policy.
- `BIFPLR0_2` and `BIFPLR1_2` are repeated port-instance namespaces with very similar layouts. Consumers must not mix a field macro from one instance with an offset from another instance.
- AER, DPC, Root Port PIO, slot status, and link status fields can have sticky, write-one-to-clear, or side-effecting semantics. Treating them as ordinary read/modify/write fields can erase diagnostic logs or leave errors uncleared.
- Link Control, Link Control 2/3, 16 GT/32 GT controls, and per-lane equalization fields affect asynchronous link training. Bad values can trigger non-converging equalization, degraded link width/speed, reset loops, or device disappearance.
- ACS, multicast, VC, and bridge window fields affect traffic routing and isolation. Incorrect masks or mismatched offsets can create DMA reachability bugs, peer-to-peer routing surprises, or virtualization/IOMMU policy violations.
- MSI address/data/control and MSI-map fields are interrupt-routing sensitive. Stale restore values or bitfield mistakes can cause lost, duplicated, or misrouted interrupts.
- L1 PM substate, LTR, OBFF, and ESM fields interact with platform power policy and latency. Enabling unsupported combinations can produce wake failures, latency spikes, or unstable links.
- The masks do not encode reserved-bit policy. Writers must preserve reserved bits and consult hardware documentation/default headers before composing values.

## Test Signals

- Build AMDGPU with NBIO 7.7 support so references in `nbio_v7_7.c`, discovery wiring, and any PCIe/NBIO consumers catch missing or renamed generated symbols.
- Run generated-header consistency checks for the chunk: complete registers should have compatible `__SHIFT`/`_MASK` pairs, while the opening `BIFPLR0_2_PCIE_UNCORR_ERR_MASK` tail and closing `BIFPLR1_2_PCIE_L1_PM_SUB_CNTL` partial register should be reconciled with adjacent chunks.
- Cross-check the `BIFPLR0_2` and `BIFPLR1_2` register names against `nbio_7_7_0_offset.h` and `nbio_7_7_0_default.h` so field layouts, addresses, and defaults remain synchronized.
- On NBIO 7.7 hardware, dump PCIe configuration space and compare decoded bridge, PM, PCIe, MSI, VSEC, VC, AER, ACS, multicast, L1 PM, DPC, RP PIO, ESM, and 16/32 GT link fields against expected capability-chain layout.
- Exercise PCIe link speed changes, retraining, suspend/resume, GPU reset, runtime power transitions, and lane equalization diagnostics while checking Link Status, Link Status 2, Link Control 2/3, lane error status, per-lane presets, and 16/32 GT status bits.
- Use AER or platform error injection where available to verify uncorrectable/correctable status, mask, severity, first-error pointer, header logs, TLP prefix logs, root error status/source IDs, DPC status, and Root Port PIO logs decode correctly and are cleared only after capture.
- Stress MSI delivery under graphics, compute, reset, and power-transition workloads to catch message-control, message-address/data, and MSI-map regressions.
- Validate PCI bridge resource assignment and enumeration across cold boot, warm reboot, GPU reset, and resume, especially bus-number, I/O, memory, prefetchable, command/status, and bridge-control fields.
- In systems using ACS, peer-to-peer DMA, multicast, or strict IOMMU isolation, test routing/isolation behavior before and after reset and power transitions.

## Chunk Notes

- Lines 120813-120819 finish the mask half of `BIFPLR0_2_PCIE_UNCORR_ERR_MASK`; the earlier shift and mask definitions for that register are in the previous chunk.
- Lines 120820-121945 complete the visible `BIFPLR0_2` capability tail from AER severity through ESM and 16/32 GT link fields.
- Lines 121946-123171 begin `addressBlock: nbio_pcie0_bifplr1_cfgdecp` and cover `BIFPLR1_2` conventional PCI bridge, PM, PCIe, MSI, VSEC, VC, serial-number, AER, secondary link, lane equalization, ACS, and multicast sections.
- Lines 123172-123212 start the `BIFPLR1_2` L1 PM substate section and end inside `BIFPLR1_2_PCIE_L1_PM_SUB_CNTL`; adjacent chunks are required for the remaining masks and subsequent BIFPLR1_2 extended capability fields.
