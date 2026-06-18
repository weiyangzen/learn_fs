# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 113579-115931

## Scope

This chunk covers generated shift and mask definitions from the AMD NBIO 7.7.0 register mask header. The range begins in the tail of the `TRAP3` command definitions, continues through `TRAP4` through `TRAP15`, covers a small set of secondary-bus and MCA SMN interrupt fields, and then enters the `nbio_iohub_nb_rascfg_ras_cfgdec` address block for RAS/parity reporting and response controls.

The chunk is a C preprocessor register-field map only. It defines `#define` constants for bit shifts and masks; it does not define functions, types, data storage, allocation, locks, or executable control flow.

## Purpose

The purpose of this section is to encode the bit-level ABI used by AMDGPU NBIO code when reading, composing, and writing NBIO 7.7.0 registers. Each hardware field is represented in the generated AMD style:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit.
- `<REGISTER>__<FIELD>_MASK` gives the field mask before shifting down.

Driver code normally combines these macros with the companion NBIO register offset headers and AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`. This header supplies only the field positions; other headers and register-access helpers supply addresses and the actual MMIO/SMN/config-space transactions.

## Important Macro Families

### Trap Comparator Fields

The first portion covers trap comparator slots. `TRAP3` appears only as the final command and mask fields because the chunk begins in the middle of that slot. `TRAP4` through `TRAP15` are complete and share the same generated layout:

- `TRAPn_CONTROL0` exposes `TrapnEn`, `TrapnSMUIntr`, and `TrapnCrossTrigger`. These fields enable a trap, select SMU interrupt behavior, and configure cross-trigger routing.
- `TRAPn_ADDRESS_LO` and `TRAPn_ADDRESS_HI` define the compared address. The low-address field starts at bit 2 and uses `0xFFFFFFFC`, so trap addresses are naturally aligned to at least four bytes.
- `TRAPn_COMMAND` exposes two command comparators, `TrapnCmd0` at bits 5:0 and `TrapnCmd1` at bits 13:8.
- `TRAPn_ADDRESS_LO_MASK`, `TRAPn_ADDRESS_HI_MASK`, and `TRAPn_COMMAND_MASK` define the corresponding address and command compare masks.

These macros are integration points for low-level NBIO debug, tracing, or error-trigger mechanisms. A consumer can program an address/command match pattern and enable cross-trigger or SMU interrupt side effects. Because the slots are generated and nearly identical, copy/paste or generator drift in one slot would be easy to miss without checking the numerical suffixes against the field names.

### Secondary-Bus and Bridge Configuration Fields

After the trap slots, the chunk defines secondary-bus bridge-style fields:

- `SB_COMMAND` controls I/O, memory, and bus-master access enables.
- `SB_SUB_BUS_NUMBER_LATENCY` carries secondary and subordinate bus numbers.
- `SB_IO_BASE_LIMIT`, `SB_IO_BASE_LIMIT_HI`, `SB_MEM_BASE_LIMIT`, `SB_PREF_BASE_LIMIT`, `SB_PREF_BASE_UPPER`, and `SB_PREF_LIMIT_UPPER` encode I/O, memory, and prefetchable-memory bridge windows.
- `SB_IRQ_BRIDGE_CNTL` exposes ISA/VGA routing controls.
- `SB_EXT_BRIDGE_CNTL` exposes `IO_PORT_80_EN`.
- `SB_PMI_STATUS_CNTL` exposes the current power-state field.
- `SB_SLOT_CAP` carries slot power limit value and scale.
- `SB_ROOT_CNTL` exposes CRS software-visibility enable.
- `SB_DEVICE_CNTL2` exposes ARI forwarding enable.

These fields mirror standard PCI/PCIe bridge and root-port concepts in the NBIO register image. They are used by configuration, enumeration, hotplug, virtualization, or firmware-coordination paths that need to reason about bus ranges, decode apertures, slot power limits, CRS behavior, and ARI hierarchy forwarding.

### MCA SMN Interrupt Fields

The `MCA_SMN_INT_*` macros define a compact interface for MCA-originated SMN interrupt routing:

- `MCA_SMN_INT_REQ_ADDR` masks a 20-bit SMN interrupt request address.
- `MCA_SMN_INT_MCM_ADDR` masks a 4-bit MCM address.
- `MCA_SMN_INT_APERTUREID` masks a 12-bit aperture ID.
- `MCA_SMN_INT_CONTROL` exposes a 4-bit `MCACrossTrigger` selector.

These are register-field definitions for wiring machine-check or RAS events into NBIO/SMN interrupt and cross-trigger mechanisms. They are not Linux MCA handling code themselves; they are the constants that lower-level NBIO register code uses when it configures or decodes the hardware interface.

### RAS Parity Configuration and Severity

The `nbio_iohub_nb_rascfg_ras_cfgdec` address block starts with parity configuration and severity controls:

- `PARITY_CONTROL_0` provides 16-bit thresholds for correctable parity and UCP parity events.
- `PARITY_CONTROL_1` selects an injected parity error group, group type, ID, command, trigger bit, and inject-allow bit. This is the most explicit test-injection surface in the chunk.
- `PARITY_SEVERITY_CONTROL_UNCORR_0`, `PARITY_SEVERITY_CONTROL_CORR_0`, and `PARITY_SEVERITY_CONTROL_UCP_0` provide two-bit severity fields for parity groups 0 through 9 in each class.
- `MISC_SEVERITY_CONTROL` provides severity selections for generic error-event and PCIe parity-error classes.

These definitions let RAS code classify parity conditions and, where supported, inject a selected parity event for validation. The severity fields are compact packed two-bit fields, so callers must use the exact generated masks rather than hard-coded shifts to avoid clobbering adjacent group severities.

### RAS Global Status

`RAS_GLOBAL_STATUS_LO` and `RAS_GLOBAL_STATUS_HI` define top-level RAS event summary bits.

`RAS_GLOBAL_STATUS_LO` reports parity categories and output paths, including correctable, non-fatal, fatal, and SERR parity event summaries, HPLGWA NMI/SCI/SMI, software SMI/SCI/NMI, APML NMI and sync flood states, pin sync-flood NMI, and private APML sync-flood state.

`RAS_GLOBAL_STATUS_HI` maps per-port error summary bits for `PCIE0` ports A through F, `PCIE1` ports A through F, `PCIE2` ports A through D, `PCIE3` port A, and `NBIF1` ports A through C. These summary bits are the first diagnostic fan-out point before more specific per-group parity status registers are examined.

### Per-Group Parity Status and Counters

The largest part of the chunk is a regular matrix of parity status registers:

- `PARITY_ERROR_STATUS_UNCORR_GRP0` through `PARITY_ERROR_STATUS_UNCORR_GRP7`.
- `PARITY_ERROR_STATUS_CORR_GRP0` through `PARITY_ERROR_STATUS_CORR_GRP7`.
- `PARITY_ERROR_STATUS_UCP_GRP0` through `PARITY_ERROR_STATUS_UCP_GRP7`.

Each group register defines `ParityErrDetected_Id0` through `ParityErrDetected_Id31`, with one bit per detected parity-error ID. This creates 8 groups times 32 IDs for each error class. Consumers can walk these bitmaps to map a top-level RAS status to a precise parity source ID.

The chunk also defines `PARITY_COUNTER_CORR_GRP0` through `GRP7` and `PARITY_COUNTER_UCP_GRP0` through `GRP7`. Each counter register contains a 16-bit `ThresholdCounter` and a `ResetEn` bit at bit 31. These counters support threshold-based reporting and reset behavior for repeated parity events.

### Miscellaneous RAS Control, Scratch, and Action Registers

`MISC_RAS_CONTROL` controls routing and suppression for RAS outputs. It includes sync-flood/NMI enable, GNB southbridge link behavior, output disable bits for interrupt/link-disable/sync-flood paths, PCIe NMI/SCI/SMI enables, and software SCI/SMI/NMI enables.

`RAS_SCRATCH_0` and `RAS_SCRATCH_1` are full-width scratch registers. Their persistence semantics are hardware-defined; from the header alone they are simply 32-bit fields that firmware or driver code may use to leave diagnostic breadcrumbs across a narrower part of the NBIO RAS flow.

The action-control registers define per-event response policy:

- `ErrEvent_ACTION_CONTROL`.
- `ParitySerr_ACTION_CONTROL`.
- `ParityFatal_ACTION_CONTROL`.
- `ParityNonFatal_ACTION_CONTROL`.
- `ParityCorr_ACTION_CONTROL`.
- `PCIE0PortASerr_ACTION_CONTROL`.
- `PCIE0PortAIntFatal_ACTION_CONTROL`.
- `PCIE0PortAIntNonFatal_ACTION_CONTROL`.
- `PCIE0PortAIntCorr_ACTION_CONTROL`.
- `PCIE0PortAExtFatal_ACTION_CONTROL`, whose remaining related PCIE0 port-A action controls continue beyond this chunk.

These action registers share the same response fields: `APML_ERR_En`, `IntrGenSel`, `LinkDis_En`, and `SyncFlood_En`. They determine whether a detected event is signaled through APML, interrupt generation, link disable, or sync flood. Misprogramming these fields can turn a recoverable parity condition into a disruptive system response, or suppress a response that platform RAS policy expects.

## Control Flow

There is no executable control flow in this chunk. Runtime behavior appears only in consumers that use these macros to implement read-modify-write or decode paths. The implied control flow for a typical RAS consumer is:

1. Read `RAS_GLOBAL_STATUS_LO` and `RAS_GLOBAL_STATUS_HI` to determine which event class or port reported an error.
2. Read the relevant `PARITY_ERROR_STATUS_*_GRP*` bitmap registers to locate the parity group and ID.
3. Consult or update severity and action-control registers to map the event to interrupt, APML, link-disable, or sync-flood behavior.
4. Use threshold counters and reset bits to rate-limit, count, or clear repeated correctable/UCP parity events.

For trap consumers, the implied sequence is to program address, command, and mask registers, then enable the trap and optional interrupt/cross-trigger behavior in `TRAPn_CONTROL0`.

## State and Persistence Behavior

All state described by this chunk is hardware register state, not software-owned memory. The header does not store state; it names fields in device registers. Persistence depends on the actual NBIO register block, reset domain, firmware policy, and driver save/restore code.

The state classes are:

- Programmed trap comparator state: enable bits, address/command comparators, and masks.
- PCI/bridge configuration-visible state: bus numbers, decode windows, access enables, slot power, CRS, ARI, and power state.
- MCA/SMN interrupt routing state: request address, MCM address, aperture ID, and cross-trigger selection.
- RAS status state: global summary bits and per-group parity detection bitmaps.
- RAS configuration state: parity thresholds, severity maps, output routing, and action policy.
- Diagnostic scratch state: two full-width RAS scratch registers.

Status and counter registers may be sticky, write-one-to-clear, reset-on-read, or reset-controlled depending on the underlying hardware specification; this header alone does not encode those access semantics. Consumers must follow the ASIC register programming guide or existing AMDGPU NBIO/RAS code when clearing or resetting any status bit.

## Dependencies and Integration Points

This chunk depends on the surrounding generated AMD ASIC register ecosystem:

- Matching NBIO 7.7.0 offset/address headers identify the register addresses.
- AMDGPU register helper macros perform field extraction/composition and MMIO/SMN access.
- NBIO initialization, PCIe configuration, SR-IOV/VFIO, hotplug, and RAS code are likely consumers of the bridge, ARI, trap, and parity fields.
- Platform firmware and SMU/MCA flows may interact with the trap, MCA SMN interrupt, APML, NMI/SCI/SMI, link-disable, and sync-flood fields.
- Linux DRM AMDGPU RAS reporting paths can use these masks to map raw NBIO error registers into kernel logs, rasdaemon-visible records, or debugfs/sysfs diagnostic output.

The file is generated and source-tree-aligned with AMD hardware naming. Downstream code usually should not rename these macros or invent wrapper names unless the wrapper clearly belongs to a broader AMDGPU register abstraction.

## Risks

- Register layout drift: these constants must match NBIO 7.7.0 hardware exactly. A single bad shift or mask can corrupt adjacent RAS severity, bridge decode, or action-control fields.
- Copy/paste suffix mistakes: repeated `TRAPn`, `PARITY_ERROR_STATUS_*_GRP*`, and action-control blocks are vulnerable to numeric suffix mismatches between register and field names.
- Dangerous RAS response policy: action-control fields can enable link disable or sync flood, so writing the wrong event policy can create avoidable outages.
- Error injection misuse: `PARITY_CONTROL_1` exposes parity injection selection and trigger bits. Test-only paths must gate this carefully.
- Ambiguous status clearing: the header gives masks but not clear semantics. Treating sticky status fields as ordinary writable fields can fail to clear errors or accidentally clear unrelated bits.
- Address alignment assumptions: trap low-address fields mask off bits 1:0. Consumers that pass unaligned addresses should account for hardware comparison granularity.
- Bridge aperture programming: secondary-bus base/limit and command fields affect decode and bus-mastering behavior. Incorrect programming can expose or hide MMIO/I/O windows.

## Test Signals

Useful validation signals for code that consumes this chunk include:

- Build-time coverage that includes this header through AMDGPU NBIO/RAS code without macro redefinition or missing-symbol failures.
- Register-field unit checks, where available, that compose and extract representative fields with `REG_SET_FIELD`/`REG_GET_FIELD`, especially packed two-bit severity fields and 32-bit parity bitmaps.
- Hardware or emulator RAS tests that inject a parity event through `PARITY_CONTROL_1` and verify global status, per-group status, threshold counter, interrupt/APML behavior, and clearing/reset behavior.
- Negative tests that confirm correctable parity events do not trigger fatal/link-disable/sync-flood responses unless the corresponding action-control policy is enabled.
- PCIe configuration tests that validate secondary/subordinate bus windows, ARI forwarding, CRS visibility, and slot power fields after NBIO initialization or resume.
- Trap diagnostic tests that program one `TRAPn` slot, verify aligned address and command masks, and confirm that SMU interrupt or cross-trigger routing fires only for the intended transaction.
- Suspend/resume or GPU reset tests that check whether NBIO RAS configuration, counters, scratch registers, and bridge fields are restored or intentionally reinitialized according to platform policy.
