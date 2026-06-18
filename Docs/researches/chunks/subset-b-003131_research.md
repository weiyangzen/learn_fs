# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 22131-24686

## Scope

This chunk is a generated AMDGPU NBIO 7.11.0 shift/mask header segment. It contains 2,141 `#define` field-layout macros over 2,556 source lines, covering 377 register names and 13 address-block comments. There are no C functions, structs, enums, variables, allocations, locks, or executable statements in this range.

The range starts in the middle of the `BIF_CFG_DEV1_EPF0_LANE_3_MARGINING_LANE_STATUS` field definitions, covers PCIe lane-margining fields for lanes 4-15, root/endpoint NBIO configuration, miscellaneous NBIO control, traps, RAS/poison reporting, IOMMU L2A controls, IOAPIC feature enables, and USB4/PCIe adapter-layer controls, then ends immediately after the `BIF_CFG_DEV0_RC0_COMMAND` register comment. Adjacent chunks are needed to complete the lane 3 status register and the dev0 RC0 command register.

Although this repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware register metadata and has no direct distributed-filesystem or Ceph behavior.

## Purpose

`nbio_7_11_0_sh_mask.h` is the bitfield half of AMD's generated NBIO 7.11.0 register interface. For each hardware field it provides:

- `<REGISTER>__<FIELD>__SHIFT`, the starting bit position used to encode or extract the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, clear, preserve, or update the field.

This chunk describes NBIO register layout for PCIe configuration, error handling, RAS signaling, IOMMU cache control, and PCIe-over-USB4 transport control. Driver code combines these macros with companion address/default headers and AMDGPU register helpers to read status, decode error state, or compose write values without hard-coding bit numbers at call sites.

## Important Macro Families

The PCIe lane-margining section covers `BIF_CFG_DEV1_EPF0_LANE_4_MARGINING_LANE_CNTL` through lane 15 plus status registers, with a tail from lane 3 status. Each lane has receiver number, margin type, usage model, and margin payload fields, mirrored by status fields. The chunk also includes router enhanced capability list and router data fields for `BIF_CFG_DEV1_EPF0_PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2`.

The NB configuration blocks cover `NB_NBCFG0_*` PCI-compatible identity/control registers, fast-register aperture layout, and a large `nbio_iohub_nb_misc_misc_cfgdec` group. Notable fields include PCI command/status/class/header/subsystem IDs, NB PCI arbitration and control, scratch registers, revision ID, LCLK deep-sleep mask, bus-number control, MMIO and DRAM aperture bounds, SB/SW location records, software NMI/SMI/SCI/GIC-SPI controls, sync-flood controls, CAM target/index/data matching registers, VDM routing/control registers, xbar stall controls, PSP/SMU/FASTREG/MISC base-address pairs, SMU CPU block control/status, and scratch/trap infrastructure.

The trap section defines request and response plumbing: `TRAP_STATUS`, `TRAP_REQUEST0`-`TRAP_REQUEST5`, byte-enable/data payload registers, `TRAP_RESPONSE_CONTROL`, `TRAP_RESPONSE0`, response data registers, and 16 repeated trap comparators (`TRAP0` through `TRAP15`) with enable, SMU interrupt, cross-trigger, low/high address, command, address mask, and command mask fields. These macros describe a hardware filter/response path for NBIO transactions rather than software exception handling.

The bridge and interrupt section covers `SB_*` secondary-bus bridge fields, USB QoS fields, MCA SMN interrupt request/MCM/aperture/control fields, and internal sideband steering/latency fields. These definitions are integration points between NBIO, system management, interrupt routing, and PCIe bridge configuration.

The RAS groups cover `PARITY_CONTROL_*`, parity severity controls for uncorrected/corrected/UCP groups, miscellaneous severity and RAS control, RAS scratch registers, sync-flood and NMI status, internal poison status/mask, egress poison status/mask/severity fields, and APML status/control/trigger. A PSP-specific RAS block mirrors poison status reporting for `PSP_INTERNAL_POISON_STATUS` and `PSP_EGRESS_POISON_STATUS_LO/HI`.

The IOMMU `L2A` block covers performance counter selection/counts, L2 status, cache behavior controls, DTC/ITC/PTC cache invalidation and bypass/parity/way/hash controls, credit controls, update-filter controls, error-rule disable/lock fields, page-size controls, memory power-gating controls, and ECO control. These fields describe IOMMU translation-cache and memory-power behavior exposed through NBIO register space.

The final PCIe/USB4 section covers IOAPIC `FEATURES_ENABLE`, PCIe/USB4 TXAL/RXAL/AL control, hysteresis timers, error-recording mode, router path clearing, clock/power gating, PCIe control, TX power control, and master-control payload/read-request/tag overrides. The range ends as the next `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` block begins.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated preprocessor macro namespace. The constants are untyped integer literals, mostly with an `L` suffix, and encode only field geometry.

These definitions do not encode register addresses, defaults, access widths, read/write permissions, reset domains, write-one-to-clear behavior, ownership, or sequencing. Consumers must use the matching generated address/default metadata, such as NBIO 7.11.0 offset/SMN/default headers, together with AMDGPU bitfield and register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, or the appropriate PCI config/SMN/NBIO access path.

## Control Flow

This header has no local runtime control flow. Runtime flow is external:

1. AMDGPU or platform code selects a register address from the companion generated register metadata.
2. It reads a hardware register and decodes fields with the `__SHIFT` and `_MASK` constants, or creates a write value by inserting field values while preserving unrelated and reserved bits.
3. The resulting values drive PCIe configuration, error reporting, RAS handling, IOMMU setup, bridge routing, trap/cross-trigger behavior, or PCIe/USB4 link and power-management control.

The field names imply asynchronous hardware flows outside this file: PCIe lane margining, router capability discovery, CAM match/cross-triggering, trap request/response capture, parity error generation/severity routing, sync-flood propagation, poison status latching, APML NMI/sync-flood signaling, IOMMU cache invalidation and performance counting, and PCIe/USB4 adapter-layer reset/idle/reconfiguration handshakes.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes hardware-visible state in NBIO registers. Persistence depends on the GPU reset domain, PCIe reset, power and clock gating, firmware/BIOS initialization, PSP/SMU ownership, suspend/resume restore, and explicit driver writes.

Represented state includes PCI configuration bits, base/limit apertures, scratch registers, bus and bridge routing state, software interrupt/status vectors, CAM/trap comparator programming, request/response payloads, parity and poison status latches, severity policies, APML trigger enables, IOMMU cache/power/performance-counter controls, and PCIe/USB4 adapter-layer reset, idle, clock-gating, and payload/tag policy bits.

Several names indicate status or latch semantics (`STATUS`, `RW1C`, `TRIGGER`, poison and sync-flood bits, trap request/response fields). The shift/mask header does not define how those bits clear or whether a read has side effects; callers must follow the hardware spec and companion generated metadata.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.11.0 register database and must stay synchronized with sibling headers that provide register addresses and defaults. It is intended to be included through AMDGPU ASIC register include stacks under `drivers/gpu/drm/amd/include/asic_reg/nbio`.

Primary integration points are AMDGPU NBIO, PCIe, PSP/SMU, RAS, IOMMU/ATS, interrupt routing, and power-management code paths. The lane-margining and USB4 fields are relevant to PCIe link diagnostics and PCIe-over-USB4 tunneling behavior. The RAS and poison fields integrate with error logging and escalation paths such as NMI, SMI, SCI, APML, sync-flood, and SMU interrupt/cross-trigger routing. The L2A fields integrate with IOMMU translation-cache behavior and performance/debug instrumentation.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while causing writes to the wrong hardware bit, leading to broken PCIe configuration, missed errors, false interrupts, poisoned-transaction mishandling, IOMMU cache corruption, or unstable PCIe/USB4 link behavior.
- This chunk starts and ends mid-register-family. Whole-file reconciliation must include the preceding lane 3 status fields and following `BIF_CFG_DEV0_RC0_COMMAND` fields before treating either boundary register as complete.
- Repeated lane-margining and trap-comparator definitions are mechanically patterned. A single lane/trap mismatch can affect only one lane or comparator, making failures appear intermittent or topology-specific.
- `NB_SPARE2` exposes 32 `RW1C` fields. Read-modify-write helpers that do not account for write-one-to-clear semantics can accidentally clear latched state.
- Trap, CAM, parity error-generation, APML trigger, sync-flood, and cross-trigger fields can inject or escalate hardware events. Writes must be tightly scoped and restored after diagnostics.
- RAS severity and mask fields change whether errors are corrected, escalated, ignored, or routed to NMI/SMI/SCI/APML paths. Incorrect programming can hide fatal conditions or cause unnecessary system-level interruptions.
- Poison status/status-mask fields span low/high register pairs. Consumers must handle 64-bit status coherently and avoid mixing stale halves.
- IOMMU L2A invalidation, bypass, parity, way-disable, page-size, and memory-power-gating fields are translation-cache sensitive; incorrect values can cause address-translation faults or silent data-path instability.
- USB4 adapter-layer reset/idle/flush/reconfiguration bits describe handshake-sensitive paths. Skipping required waits or forcing pass/ignore fields can create suspend/resume, hotplug, or tunneled-PCIe failures.

## Test Signals

- Build AMDGPU with NBIO 7.11.0 support enabled. Compile-time coverage catches removed, renamed, or malformed generated symbols used by consumers.
- Run generated-header consistency checks: every `__SHIFT` should have a compatible `_MASK`, masks should fit their register width, patterned lane/trap/status fields should align, and repeated low/high status blocks should expose expected bit coverage.
- Cross-check every register name in this chunk against NBIO 7.11.0 address/default headers so field layouts map to known registers and reset values.
- On supported hardware, validate PCIe link enumeration, lane-margining diagnostics, bridge bus-number/aperture setup, hotplug or retrain paths, suspend/resume, and GPU reset recovery.
- Exercise RAS paths where available: parity injection, poison status reporting, sync-flood/NMI/APML routing, SMU interrupt/cross-trigger behavior, and clearing of latched status without losing unrelated bits.
- Exercise IOMMU/ATS workloads and fault paths while sampling L2A performance counters and cache invalidation controls; watch for translation faults, stale mappings, or parity/error-rule regressions.
- For PCIe/USB4 systems, validate tunneled PCIe traffic across reset, low-power transitions, path clear, reconfiguration, and clock-gating states, with register traces confirming reserved bits are preserved.
