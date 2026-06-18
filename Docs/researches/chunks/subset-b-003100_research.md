# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 78265-80596

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.0 shift/mask header. It defines preprocessor constants for bit positions and masks in NBIO IO hub registers, primarily the `nbio_iohub_nb_rascfg_ras_cfgdec` RAS configuration address block and the beginning of the `nbio_iohub_nb_psprascfg_pspras_cfgdec` PSP-facing RAS status block.

The first few lines complete the preceding IOHC SION traffic-management area for client 4: S0/S1 write-response time slots, S1 request/read-response/write-response burst targets and time slots, request/data/read-response/write-response pool-credit allocation dwords, and a live-lock watchdog threshold. The main body then defines parity, global RAS, PCIe/NBIF action, sync-flood, poison, APML, and PSP status fields.

This is hardware metadata, not executable driver logic. AMDGPU register access helpers consume these constants with companion offset/SMN/default headers so C code can encode and decode individual hardware fields without embedding literal bit positions.

## Important APIs, Types, and Macros

There are no functions, structs, typedefs, or enums in this range. The public interface is the generated macro pattern:

- `<REGISTER>__<FIELD>__SHIFT`: the field's starting bit.
- `<REGISTER>__<FIELD>_MASK`: the field mask already shifted into register position.

Major register families in this chunk are:

- `IOHC_SION_*Client4*` and `IOHC_SION_LiveLock_WatchDog_Threshold`: 32-bit lower/upper masks for SION client 4 request, read-response, and write-response burst/time-slot scheduling, plus pool-credit allocation dwords for request, data, read-response, and write-response pools. These fields are full-width dwords except the watchdog threshold, which uses bits 7:0.
- `PARITY_CONTROL_0` and `PARITY_CONTROL_1`: parity corrected/UCP thresholds and parity error-injection selectors. `PARITY_CONTROL_1` selects group, group type, ID, command, trigger, and injection-allow bits.
- `PARITY_SEVERITY_CONTROL_UNCORR_0`, `PARITY_SEVERITY_CONTROL_CORR_0`, and `PARITY_SEVERITY_CONTROL_UCP_0`: two-bit severity selectors for parity groups 0-4, split by uncorrectable, correctable, and UCP classes.
- `RAS_GLOBAL_STATUS_LO` and `RAS_GLOBAL_STATUS_HI`: top-level RAS status bits. The low dword reports parity classes, HPLGWA interrupt classes, software SMI/SCI/NMI, APML NMI/sync-flood status, pin sync-flood NMI, and private APML sync-flood. The high dword reports PCIE0 ports A-G and NBIF1 ports A-B error sources.
- `PARITY_ERROR_STATUS_UNCORR_GRP[0-4]`, `PARITY_ERROR_STATUS_CORR_GRP[0-4]`, and `PARITY_ERROR_STATUS_UCP_GRP[0-4]`: per-ID status bitmaps, 32 IDs per group, for each parity class.
- `PARITY_COUNTER_CORR_GRP[0-4]` and `PARITY_COUNTER_UCP_GRP[0-4]`: 16-bit per-group counters for correctable and UCP parity errors.
- `MISC_SEVERITY_CONTROL` and `MISC_RAS_CONTROL`: severity for miscellaneous event and PCIe parity errors, plus global RAS output controls and enables for pin NMI sync flood, GNB sideband link disable behavior, interrupt/link-disable/sync-flood output suppression, PCIe NMI/SCI/SMI, and software SCI/SMI/NMI.
- `RAS_SCRATCH_0` and `RAS_SCRATCH_1`: full-width software scratch fields.
- `*_ACTION_CONTROL`: a repeated action-control schema for error classes. Each register exposes `APML_ERR_En`, two-bit `IntrGenSel`, `LinkDis_En`, and `SyncFlood_En`. This chunk covers generic error event and parity classes, PCIE0 ports A-G SERR/internal fatal/internal nonfatal/internal corrected/external fatal/external nonfatal/external corrected/parity-error actions, and NBIF1 ports A-B with the same subevents.
- `SYNCFLOOD_STATUS` and `NMI_STATUS`: source status for sync-flood and pin NMI events. Sync-flood status includes RAS control, APML, pin, private, and IOHC port bits 8-31.
- `POISON_ACTION_CONTROL`: action routing for internal poison, low-side egress poison, and high-side egress poison. Each category repeats APML error enable, interrupt-generation selection, link-disable enable, and sync-flood enable fields.
- `INTERNAL_POISON_STATUS`, `INTERNAL_POISON_MASK`, `EGRESS_POISON_STATUS_LO`, `EGRESS_POISON_STATUS_HI`, `EGRESS_POISON_MASK_LO`, `EGRESS_POISON_MASK_HI`, `EGRESS_POISON_SEVERITY_DOWN`, and `EGRESS_POISON_SEVERITY_UPPER`: internal and egress poison source bitmaps, masks, and severity bitmaps.
- `APML_STATUS`, `APML_CONTROL`, and `APML_TRIGGER`: APML-facing corrected/nonfatal/fatal/SERR/poison status, NMI and sync-flood enable controls, output-disable control, and software NMI trigger bit.
- `PSP_SYNCFLOOD_STATUS`, `PSP_INTERNAL_POISON_STATUS`, and the start of `PSP_EGRESS_POISON_STATUS_LO`: PSP-visible mirrors for sync-flood and poison sources. This chunk includes all PSP sync-flood source bits, all PSP internal poison bits 0-7, and the `PSP_EGRESS_POISON_STATUS_LO` shifts for bits 0-31 plus masks through bit 27.

These macros are expected to be used through AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, and the SOC15/NBIO register read-write wrappers. Register addresses come from the matching NBIO 7.0 offset or SMN headers; this file only supplies field geometry.

## Control Flow and Runtime Behavior

This chunk has no runtime control flow. It is included at compile time and contributes constants to read-modify-write operations in NBIO, PCIe, RAS, poison-handling, interrupt-routing, APML, and PSP integration code.

The implied hardware flows are:

1. IOHC SION client-4 scheduling and pool-credit registers shape request, data, read-response, and write-response arbitration. The lower/upper fields indicate 64-bit-style split programming surfaces stored as pairs of 32-bit registers.
2. Parity RAS setup writes threshold, severity, and error-injection fields before hardware detects or injects parity events. Status registers then expose per-group/per-ID latches for uncorrectable, correctable, and UCP classes, and counters accumulate selected corrected/UCP events.
3. Global RAS status aggregates individual parity, PCIe port, NBIF port, software, APML, and pin-originated events into low/high status dwords. Driver code can use these masks to classify an event source before reading lower-level status registers.
4. Action-control registers map each RAS event class to externally visible consequences: APML error reporting, an interrupt generation class, link disable, and sync flood. The same four-field schema appears for generic parity events and each PCIE0/NBIF1 port subevent.
5. Sync-flood, NMI, and poison status registers provide source bitmaps that firmware, RAS code, or debug code can read after a fatal path, link-disabling path, APML notification, or poison propagation.
6. APML control/status/trigger fields expose RAS events to platform management and can also trigger APML NMI behavior when enabled.
7. The PSP RAS block mirrors selected sync-flood and poison information for the Platform Security Processor's view of the same IO hub events.

All side effects are in the hardware registers that callers access. The header does not sequence operations, clear status bits, or enforce ordering; the driver and firmware-facing code must apply any required status-clear, mask-before-enable, or trigger-after-programming ordering.

## State and Persistence

The header owns no state, allocates no memory, performs no I/O, and persists nothing. The represented state is in NBIO 7.0 hardware registers.

State categories represented here include:

- Scheduler and credit configuration for IOHC SION client 4, including full-width burst-target/time-slot and pool-credit dwords plus an 8-bit live-lock watchdog threshold.
- RAS policy state: parity thresholds, error-injection selectors, parity severity controls, miscellaneous severity controls, global RAS output suppression, PCIe/software interrupt enables, APML output control, and per-event action routing.
- RAS observation state: global status low/high dwords, parity status bitmaps, corrected/UCP parity counters, sync-flood and NMI source status, poison source status, APML status, and PSP-visible sync-flood/poison mirrors.
- Scratch state in `RAS_SCRATCH_0` and `RAS_SCRATCH_1`, which are full 32-bit fields intended for software/firmware coordination or diagnostics.
- Mask and severity state for poison events, including internal poison masking and egress poison low/high masks and severity bitmaps.

Persistence across GPU reset, PCI reset, suspend/resume, BACO, or runtime power transitions is not specified by this header. Those semantics are defined by NBIO hardware behavior and any driver reinitialization that uses these constants after a reset or power-state transition.

## Dependencies and Integration Points

Primary dependencies are the adjacent generated NBIO 7.0 headers:

- `nbio_7_0_offset.h` for MMIO/config-space register offsets corresponding to these register names.
- `nbio_7_0_smn.h` for SMN-addressed NBIO registers.
- `nbio_7_0_default.h` for reset/default values.
- Adjacent chunks of `nbio_7_0_sh_mask.h`: the previous chunk owns the start of the IOHC SION client-4 section, and the next chunk completes `PSP_EGRESS_POISON_STATUS_LO`.

Likely integration areas in the AMDGPU tree include:

- NBIO 7.0 setup and low-level register access in `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`.
- SOC15-era initialization paths that include NBIO generated metadata.
- AMDGPU RAS handling that classifies parity, poison, PCIe, NBIF, sync-flood, fatal, nonfatal, corrected, and SERR events.
- Platform management paths that expose events through APML NMI/sync-flood mechanisms.
- PSP/firmware coordination paths that read PSP-facing sync-flood and poison mirrors.
- PCIe/NBIO link and error-reporting paths where action-control bits can generate interrupts, request link disable, or propagate sync flood.

Because the file is generated metadata, integration is by symbol naming. A register accessor must pair a `*_SHIFT`/`*_MASK` macro from this file with the matching register address macro from the offset/SMN header and with hardware documentation for field value meanings.

## Risks

- Incorrect masks or shifts can silently program the wrong RAS policy bit or misread the wrong status bit. In this chunk that can affect fatal/nonfatal/corrected event classification, poison handling, APML notification, sync flood, link disable, or interrupt routing.
- Action-control registers are highly repetitive across parity, PCIE0 ports A-G, and NBIF1 ports A-B. A generator or copy/paste error in one port/subevent may be missed if testing exercises only one PCIe port.
- Many status and mask registers have similar names. Confusing `*_STATUS_*` with `*_MASK_*`, or corrected parity groups with UCP/uncorrectable groups, can suppress events or report false events.
- `PARITY_CONTROL_1` exposes error-injection fields, including trigger and injection-allow bits. Misuse by debug or validation code can intentionally create hardware errors outside controlled test paths.
- `MISC_RAS_CONTROL`, APML controls, and action-control fields can disable outputs or enable disruptive actions such as link disable and sync flood. Bad writes can either hide critical errors or escalate recoverable events.
- Poison handling fields are split across internal poison, egress low-side, and egress high-side paths. Using the wrong mask or severity bitmap can misroute poison reporting.
- The chunk boundary is in the middle of the PSP egress poison low-status register: masks for bits 28-31 are not present in this work item and must be taken from the next chunk.
- Full-width SION scheduling and pool-credit fields have no in-header value constraints. Callers need hardware-programming knowledge to avoid starvation, deadlock, or live-lock watchdog behavior.

## Test and Validation Signals

Useful validation signals are generated-header consistency checks plus hardware or emulator coverage:

- Build AMDGPU configurations that include NBIO 7.0 users to catch missing or malformed macro definitions.
- Check that complete registers in lines 78265-80596 have paired `__SHIFT` and `_MASK` definitions, while allowing the intentional split for `PSP_EGRESS_POISON_STATUS_LO` masks 28-31 at the chunk end.
- Cross-check register names against `nbio_7_0_offset.h`, `nbio_7_0_smn.h`, and `nbio_7_0_default.h` so every register with field masks has an address/default definition where expected.
- Run mechanical symmetry checks across repeated action-control registers: generic parity actions, PCIE0 ports A-G, and NBIF1 ports A-B should share the same four field positions (`APML_ERR_En`, `IntrGenSel`, `LinkDis_En`, `SyncFlood_En`).
- Validate parity RAS paths by reading thresholds/severity, injecting controlled parity events through `PARITY_CONTROL_1` where hardware validation permits it, and confirming global status, per-group status, counters, interrupts, APML reporting, and clear behavior.
- Validate poison handling by exercising internal and egress poison reporting and checking the corresponding status, mask, severity, APML, and PSP mirror fields.
- Validate sync-flood and NMI source reporting by checking RAS-control, APML, pin, private, and IOHC port source bits after controlled events.
- Run reset and suspend/resume coverage on NBIO 7.0 ASICs to ensure driver initialization restores RAS policy registers and that status/scratch registers behave according to expected retention semantics.

## Chunk Boundary Notes

This chunk starts mid-IOHC-SION client-4 register family at the `IOHC_SION_S0_Client4_WrRsp_TimeSlot_Lower` field and quickly transitions into the `nbio_iohub_nb_rascfg_ras_cfgdec` address block. It covers that RAS block through `APML_TRIGGER`, then enters `nbio_iohub_nb_psprascfg_pspras_cfgdec`.

The final register in this work item, `PSP_EGRESS_POISON_STATUS_LO`, is incomplete by line range: shifts for bits 0-31 and masks for bits 0-27 are inside this chunk, while masks for bits 28-31 begin in the next chunk at line 80597. Merge/reconciliation should treat that as an artifact of chunking, not a missing-definition defect in the source.
