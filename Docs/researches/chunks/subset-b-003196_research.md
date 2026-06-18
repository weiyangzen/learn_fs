# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 87942-90324

## Scope

This chunk is a generated AMD NBIO 7.2.0 register shift/mask header segment. It contains C preprocessor constants only: each hardware register field is represented by a `__SHIFT` bit position and a `MASK` value. There are no functions, structs, storage objects, or executable control flow in this slice.

The covered region starts in the `BIFPLR6_0` PCIe configuration/register capability space and then enters the `addressBlock: nbio_pcie0_bifp0_pciedir_p` block for `BIFP0` PCIe port/link registers. The constants are intended to be included by AMDGPU NBIO/PCIe code that reads, writes, or decodes ASIC MMIO/config-space registers.

## Purpose

The chunk provides the bit layout for several PCIe/NBIO feature areas:

- PCIe MC receive/block/overlay BAR fields: `BIFPLR6_0_PCIE_MC_RCV*`, `MC_BLOCK_ALL*`, `MC_BLOCK_UNTRANSLATED_*`, and `MC_OVERLAY_BAR*`.
- PCIe L1 PM Substates capability and control fields: `BIFPLR6_0_PCIE_L1_PM_SUB_CAP_LIST`, `PCIE_L1_PM_SUB_CAP`, `PCIE_L1_PM_SUB_CNTL`, and `PCIE_L1_PM_SUB_CNTL2`.
- Downstream Port Containment and root-port PIO error reporting: `PCIE_DPC_*`, `PCIE_RP_PIO_STATUS`, `MASK`, `SEVERITY`, `SYSERROR`, `EXCEPTION`, header logs, and prefix logs.
- Extended Speed Mode capability/status/control metadata: `PCIE_ESM_*` capability headers, enable/status fields, and capability bitmaps spanning rates from 8.0G through 28.0G.
- Data Link Feature, 16GT PHY, lane equalization, and margining capability/control/status fields.
- CCIX capability and ESM-related controls, including 20GT/25GT lane equalization fields and optimized TLP format controls.
- `BIFP0` PCIe port, transmit, receive, flow-control, error injection, AER private, and link-controller registers through `BIFP0_PCIE_LC_CNTL7`.

## Important API Surface

This header's API surface is macro names. Drivers rely on the naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the least significant bit of the field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the register word.

The most important register groups in this chunk are:

- `BIFPLR6_0_PCIE_L1_PM_SUB_*`: advertises and controls PCIe L1.1/L1.2 support, common-mode restore time, LTR threshold scale/value, and power-on timing.
- `BIFPLR6_0_PCIE_DPC_*`: exposes DPC capabilities, trigger enables, software trigger, interrupt/status bits, busy state, trigger reason, and error source ID.
- `BIFPLR6_0_PCIE_RP_PIO_*`: tracks configuration, I/O, and memory unsupported-request/completer-abort/completion-timeout events. The parallel `STATUS`, `MASK`, `SEVERITY`, `SYSERROR`, and `EXCEPTION` registers use the same field layout, and `HDR_LOG*`/`PREFIX_LOG*` hold captured TLP data.
- `BIFPLR6_0_PCIE_ESM_*`: identifies the ESM vendor capability, status/control bits, and rate support bitmaps. `PCIE_ESM_CAP_1` through `CAP_7` define one-bit support flags for many fractional data rates.
- `BIFPLR6_0_LINK_*_16GT` and `BIFPLR6_0_LANE_*_EQUALIZATION_CNTL_16GT`: describe 16GT link equalization request/status and per-lane downstream/upstream port preset values.
- `BIFPLR6_0_LANE_*_MARGINING_*`: per-lane margining controls/status for lanes 0-15, including error-count limit, margin type, timing/voltage step, sampler/reporting method, and valid/error-status flags.
- `BIFPLR6_0_PCIE_CCIX_*`: exposes CCIX capability headers, ESM required/optional capabilities, ESM status/control, 20GT and 25GT per-lane equalization, and CCIX optimized TLP support/enable bits.
- `BIFP0_PCIE_TX_*` and `BIFP0_PCIE_RX_*`: port-level transmit/receive controls, requester/vendor fields, sequence/replay/ACK/NOP timing, credit advertisement/init/status, LTR capture, and RX credit allocation.
- `BIFP0_PCIE_LC_*`: link controller controls for reset, L0s/L1/L23 behavior, width negotiation, speed negotiation, FTS/EIEOS settings, LTSSM state history, bandwidth-change status, lane state, equalization, SRIS, and ESM handshaking.

## Control Flow and Data Flow

There is no direct control flow in this header. At runtime, control flow comes from the AMDGPU code that includes these macros and performs register I/O. Typical usage is:

1. Read a 16-bit or 32-bit PCIe/NBIO register through an AMDGPU register accessor.
2. Extract a field with `(value & FIELD_MASK) >> FIELD_SHIFT`.
3. Compose a new register value by clearing `FIELD_MASK` and OR-ing a shifted field value.
4. Write the register back for control registers, or log/report decoded fields for status registers.

The field groups imply several hardware data flows:

- Link power management flows from capability bits (`L1_PM_SUB_CAP*`) into policy-controlled enable bits (`L1_PM_SUB_CNTL*`).
- Error containment flows from detected PCIe/DPC/RP PIO events into status bits and captured TLP header/prefix logs, with masks and severity/sys-error routing determining reporting behavior.
- Link bring-up and retraining flows through `LC_SPEED_CNTL`, `LC_LINK_WIDTH_CNTL`, `LC_TRAINING_CNTL`, `LC_CNTL*`, and lane equalization controls.
- PCIe flow control state is represented by advertised, initialized, and allocated credit fields for posted, non-posted, and completion traffic, including VC1 variants.
- ESM/CCIX data-rate negotiation is represented by capability bitmaps, enable/control bits, calibration/status fields, and per-lane equalization settings for 20GT/25GT paths.

## State and Persistence Behavior

The macros do not persist state themselves. They describe hardware-backed state in NBIO/PCIe registers. Persistence characteristics are determined by the ASIC and PCIe reset domains:

- Status and log fields such as DPC status, RP PIO status, header logs, prefix logs, NAK counters, lane status, current/previous LC state, and captured LTR values reflect transient hardware observations.
- Control fields such as L1 substate enables, DPC enables, error masks, CCIX/ESM controls, link-speed controls, and link-width controls are writable hardware state and may persist until function reset, link reset, ASIC reset, suspend/resume reinitialization, or driver reprogramming.
- Strap/capability fields such as supported speeds, advertised data rates, and vendor capability headers are usually read-only or strap-derived from firmware/hardware configuration.
- Error injection fields are particularly stateful and should be treated as test/debug controls. Leaving them enabled can intentionally corrupt PCIe physical or transaction-layer behavior.

## Dependencies and Integration Points

The dependency is primarily naming compatibility with companion AMDGPU generated headers:

- Address/register offset headers for NBIO 7.2.0 provide the register addresses corresponding to these shift/mask macros.
- AMDGPU register helpers and NBIO/PCIe service code use the masks to decode or program hardware fields.
- PCIe capability management code may map these hardware fields to Linux PCI concepts such as ASPM/L1 substates, AER/DPC, link speed/width, margining, and error reporting.
- Debugfs, RAS, link-training, suspend/resume, reset, and bring-up code can use these fields to inspect link state or adjust controls.

The `BIFPLR6_0` prefix denotes the PCIe link/root-port capability-space style block in this generated header, while the later `BIFP0` prefix begins an address block for PCIe port 0 internal port/link-controller registers. Code using these macros must pair them with the correct address block and hardware instance.

## Risks and Edge Cases

- Generated-header drift: if offsets or field encodings are regenerated from a different hardware description but users include mismatched address headers, register accesses can silently target wrong fields.
- Width assumptions: masks range from single-bit flags to full 32-bit fields. Callers must avoid shifting values wider than the masked field and should use unsigned types for masks such as `0xFFFFFFFFL` and high-bit masks.
- Repeated lane layouts: lane 0-15 equalization and margining registers have repeated field names. Copy/paste errors in callers can easily select the wrong lane's macros.
- Register semantics are not encoded here. Some fields are status-only, write-one-to-clear, sticky, strap-derived, or destructive controls; the masks alone do not communicate access type.
- Error injection and forced link/equalization controls can destabilize PCIe links. Production paths should gate use behind debug or bring-up policy.
- Power-management fields can interact with ASPM, LTR, common-mode restore, and T_POWER_ON timing. Incorrect programming may cause resume latency, link retraining, or device disappearance.
- DPC/RP PIO masks and severity routing affect error visibility. Overmasking may hide real faults; undermasking may trigger unexpected containment or system errors.
- CCIX/ESM and high-speed equalization fields are sensitive to platform topology, retimers, reach, and negotiated rates. Values that work on one board may fail on another.

## Test Signals

Useful validation signals for code that consumes this chunk include:

- Compile coverage for all including AMDGPU/NBIO translation units, catching macro renames or missing generated definitions.
- Register readback tests on supported ASICs verifying that field extraction with selected masks/shifts produces expected PCIe link width, speed, L1 substate, DPC, and ESM capability values.
- Suspend/resume and GPU reset testing to confirm NBIO/PCIe controls are restored and status/log decoding remains correct.
- Link retraining tests across Gen1/Gen2/Gen3/Gen4 paths, checking `LC_SPEED_CNTL`, `LC_LINK_WIDTH_CNTL`, 16GT equalization, and `LC_STATE*` observations.
- ASPM/L1.1/L1.2 validation with latency-sensitive traffic, verifying LTR threshold and T_POWER_ON programming.
- AER/DPC fault-injection or hardware-error tests confirming DPC status, error source ID, RP PIO status/mask/severity/sys-error, and TLP header/prefix logs decode as intended.
- Lane margining/equalization diagnostics across lanes 0-15, ensuring repeated per-lane macros are indexed correctly by higher-level code.
- Static checks for mask/shift consistency where generated fields should be contiguous and non-overlapping within each register.
