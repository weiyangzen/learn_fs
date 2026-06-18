# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 56615-59014

## Scope

This chunk is a generated AMDGPU NBIO 7.0 shift/mask header segment. It contains 2,181 `#define` field-layout macros and 215 register-family comments. There are no functions, structs, enums, variables, allocations, locks, or executable statements in this range.

The range starts inside the tail of `BIFPLR1_1_PCIE_ESM_CAP_6`, completes `BIFPLR1_1_PCIE_ESM_CAP_7`, covers the `nbio_pcie0_bifplr2_cfgdecp` address block from `BIFPLR2_1_VENDOR_ID` through `BIFPLR2_1_PCIE_ESM_CAP_7`, and then begins the `nbio_pcie0_bifplr3_cfgdecp` address block through the first field masks of `BIFPLR3_1_DEVICE_CAP2`. Adjacent chunks are required for the complete `BIFPLR1_1_PCIE_ESM_CAP_6` and `BIFPLR3_1_DEVICE_CAP2` register views.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield half of AMD's generated NBIO 7.0 register interface. Each visible register field exports:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position used to encode or decode the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, clear, or update the field.

This chunk maps PCIe bridge/root-port configuration-space fields for the `BIFPLR2_1` instance and the start of the same layout for `BIFPLR3_1`. The constants describe standard PCI/PCIe bridge identity, command/status, bus-number, BAR/window, interrupt, power-management, PCIe capability, slot/root/device/link, MSI, subsystem ID, virtual channel, device serial number, AER, secondary PCIe, equalization, ACS, multicast, L1 PM substate, DPC, root-port PIO, and ESM capability registers. Although this repository path is under a `ceph-client` source mirror, this header segment is AMDGPU hardware metadata and has no direct distributed-filesystem behavior.

## Important Macro Families

The opening `BIFPLR1_1_PCIE_ESM_CAP_*` tail completes ESM capability bitmap definitions for advertised equalization/speed-mode points. `PCIE_ESM_CAP_6` maps `ESM_22P0G` through `ESM_24P9G` masks, and `PCIE_ESM_CAP_7` maps `ESM_25P0G` through `ESM_28P0G` shifts and masks.

The `BIFPLR2_1` base PCI bridge configuration fields cover identity and bridge setup: vendor/device ID, command and status bits, revision/class/prog-interface bytes, cache-line and latency timer, header/BIST, primary/secondary/subordinate bus numbers, secondary latency, IO/memory/prefetchable bridge windows, upper prefetchable window halves, high IO base/limit, capability pointer, interrupt line/pin, bridge control, and extended bridge control.

The `BIFPLR2_1` power-management and PCIe capability fields describe capability-list headers, PCI PM version/PME/D-state support, PM status/control, PCIe capability type/version/slot/interrupt identity, device capabilities/control/status, link capabilities/control/status, slot capabilities/control/status, root control/capability/status, and PCIe 2.0+ device/link/slot capability/control/status registers.

The MSI and platform identity area provides MSI capability list/control/address/data fields, 64-bit MSI data, subsystem vendor/device IDs, and MSI mapping capability/address registers. Vendor-specific enhanced capability headers, two scratch registers, and capability-list links are also defined.

The virtual-channel area defines VC enhanced capability headers, port VC capability/control/status, and VC0/VC1 resource capability/control/status. These fields include traffic-class to VC mapping, port arbitration table load/select/status, VC ID, VC enable, max time slots, and negotiation-pending indicators.

The AER and secondary PCIe areas are large: uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, header and TLP prefix logs, root error command/status/source ID, secondary PCIe capability, link control 3, aggregate lane error status, and per-lane equalization controls for lanes 0 through 15. The lane equalization registers repeat the same downstream/upstream TX preset and RX preset-hint field layout for every lane.

The access/isolation and advanced feature area covers ACS capability/control bits, multicast capability/control/address/receive/block/overlay BAR fields, L1 PM substate capability/control/timing fields, DPC capability/control/status/error-source fields, root-port PIO status/mask/severity/system-error/exception fields, and PIO header/implementation-specific/prefix logs.

The `BIFPLR2_1_PCIE_ESM_*` block defines ESM enhanced capability metadata, header/status/control registers, and capability bitmaps from `PCIE_ESM_CAP_1` through `PCIE_ESM_CAP_7`. These bitmaps advertise support points from `ESM_0P0G` up through `ESM_28P0G`.

The closing `BIFPLR3_1` section begins a second PCIe bridge/root-port decode block. It mirrors the early `BIFPLR2_1` base, power-management, and PCIe capability layout: identity, command/status, bus windows, interrupt/bridge control, PM capability/control, PCIe device/link/slot/root controls and status, and starts `DEVICE_CAP2` before the chunk ends.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace. The constants are untyped preprocessor integer literals, mostly with an `L` suffix, and encode only field geometry.

These definitions do not provide register addresses, reset values, access width, access permissions, write-one-to-clear behavior, side-effect semantics, or sequencing requirements. Consumers must combine them with companion NBIO 7.0 address/default headers and AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, PCI config helpers, or NBIO/SMN accessors appropriate for the target register.

## Control Flow

This header has no local runtime control flow. Runtime flow is external:

1. AMDGPU or PCIe-related code selects a `BIFPLR*_1_*` register address from sibling generated metadata.
2. The code reads a PCIe/NBIO register and decodes fields with these `__SHIFT` and `_MASK` constants, or composes a new register value while preserving unrelated and reserved bits.
3. The decoded or written values influence PCIe bridge enumeration, link training, root-port power management, MSI routing, AER/DPC error handling, access-control policy, virtual-channel setup, L1 PM substates, lane equalization, and ESM capability handling.

The chunk implies several asynchronous hardware/protocol flows outside the header: capability-list walking, PME signaling, link retraining and equalization, AER status capture and masking, DPC containment, VC negotiation, ACS isolation enforcement, L1 substate entry/exit timing, MSI delivery, and root-port PIO error logging.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes hardware-visible configuration and status state in NBIO PCIe bridge/root-port registers. Persistence depends on GPU reset domains, PCIe hot/warm reset, firmware/BIOS initialization, suspend/resume restore, runtime power management, and explicit AMDGPU or PCI core writes.

Represented state includes identity readbacks, configuration enables, bridge windows, bus numbering, error-status latches, error masks and severities, PME/D-state state, link speed/width/training state, equalization status and presets, MSI addresses/data, VC and ACS policy state, L1 PM substate timing and enables, DPC trigger/status/source state, root-port PIO logs, and ESM capability/control/status bitmaps. Some fields are capability/read-only indicators, some are live status or latched error bits, and some are writable policy/control fields. The mask definitions alone do not distinguish those access classes.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.0 register database and must remain synchronized with sibling generated headers, especially NBIO 7.0 offset/address/default metadata. Include users normally reach these macros through AMDGPU ASIC register include stacks rather than including the chunk directly.

Important integration points include AMDGPU NBIO initialization, PCIe bridge/root-port setup, GPU reset and resume restore paths, PCIe link training/recovery, AER and DPC handling, MSI configuration, virtual-channel programming, access-control/peer-to-peer isolation, L1 power-management policy, and diagnostics that inspect lane equalization or ESM capability state. The Linux PCI core may own many standard PCI/PCIe config fields conceptually, while AMDGPU accesses NBIO-specific instances and hardware-generated mirrors through SOC15/NBIO access paths.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while causing the driver to decode or write the wrong PCIe bridge bit, which may appear as enumeration failures, broken BAR/window routing, bad interrupt/MSI setup, incorrect error reporting, or unstable link recovery.
- The chunk boundaries split two register families: `BIFPLR1_1_PCIE_ESM_CAP_6` starts before this range, and `BIFPLR3_1_DEVICE_CAP2` continues after it. Whole-file research must reconcile adjacent chunks before treating those registers as complete.
- Many status and error registers are likely latched or write-one-to-clear in hardware, but that behavior is not encoded in these macros. Call sites need the hardware spec or access helpers to avoid losing diagnostics or clearing errors accidentally.
- Bridge window and bus-number masks affect address routing. Incorrect field use can route MMIO/IO transactions to the wrong downstream range or block valid traffic.
- Link control, equalization, and L1 PM substate fields are timing and signal-integrity sensitive. Bad values can degrade performance or produce intermittent link failures rather than immediate software errors.
- ACS, VC, multicast, and DPC fields affect isolation, peer-to-peer routing, traffic-class mapping, and containment. Misprogramming can create security/isolation holes or overly aggressive error containment.
- Repeated `BIFPLR2_1_PCIE_LANE_N_EQUALIZATION_CNTL` definitions are mechanically similar across lanes 0-15, so a generator or copy error may affect only one lane and be hard to detect without per-lane validation.
- Reserved fields are explicitly present in several registers. Writers must preserve reserved bits unless hardware documentation explicitly permits a value.

## Test Signals

- Build AMDGPU with NBIO 7.0 support enabled. Compile-time coverage catches missing, renamed, or malformed generated symbols used by consumers.
- Run generated-header consistency checks: every field should have a compatible `__SHIFT`/`_MASK` pair, masks within a register should not overlap unexpectedly, and repeated lane-equalization definitions should match across lanes except for lane number.
- Cross-check this header against sibling NBIO 7.0 address/default headers so each `BIFPLR1_1`, `BIFPLR2_1`, and `BIFPLR3_1` field maps to a known register and reset/default definition.
- On supported hardware, validate PCIe enumeration, bridge window programming, BAR reachability, MSI delivery, link speed/width negotiation, link retraining, suspend/resume, hot/warm reset, and GPU reset recovery.
- Exercise AER/DPC paths by checking correct decoding of uncorrectable/correctable/root error status, masks, severities, source IDs, header logs, TLP prefix logs, and root-port PIO logs.
- Validate power-management behavior around PM D-states, PME, ASPM/L1 substates, common-mode restore time, LTR thresholds, and T-power-on timing.
- Inspect lane equalization and ESM readbacks during Gen3+ link training to ensure decoded presets, phase status, lane error state, and advertised speed-mode capability bits match hardware expectations.
