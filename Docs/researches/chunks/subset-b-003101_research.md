# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 80597-83011

## Scope

This chunk covers a generated NBIO 7.0 shift/mask register header segment. It starts in the tail of `PSP_EGRESS_POISON_STATUS_LO` mask definitions, covers the full `PSP_EGRESS_POISON_STATUS_HI` and PSP parity/error-action families, then moves through NB device-indirect configuration blocks, IOMMU and IOAPIC indirect windows, IOMMU L2 PCI/SMMU capability fields, and the beginning of the IOMMU L2 index-control block. The final line is only the `//L2_L2B_MEMPWR_GATE_2` marker; the field definitions for that register begin in the next chunk and are out of scope here.

The file is a generated hardware ABI map. It defines preprocessor constants only: no functions, structs, storage, locking, persistence code, or executable control flow live in this range.

## Purpose

The purpose of this section is to give AMDGPU and related power-management code the bit positions for NBIO 7.0 register fields. Each register field is represented by the usual pair:

- `<REGISTER>__<FIELD>__SHIFT`, the field's bit offset.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to extract or compose the field.

Consumers combine these constants with AMD register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15`, `RREG32_PCIE`, `WREG32_PCIE`, and `SOC15_REG_OFFSET`. The main local include users for `nbio_7_0_sh_mask.h` are `amdgpu/nbio_v7_0.c`, `amdgpu/soc15.c`, and `pm/powerplay/hwmgr/smu10_inc.h`. The companion `nbio_7_0_default.h` gives reset defaults for these same logical registers; the NBIO 7.0 offset header uses `cfg...` names for many configuration-space blocks rather than the `reg...` style seen in newer NBIO variants.

## Important Macro Families

### PSP Poison and Parity Status

The opening definitions complete `PSP_EGRESS_POISON_STATUS_LO` and then define all 32 bit positions for `PSP_EGRESS_POISON_STATUS_HI`. Together these expose a 64-bit poison-status bitmap from the Platform Security Processor egress path.

The PSP parity block then defines:

- `PSP_PARITY_CONTROL_0`, with independent 16-bit corrected and uncorrected-parity threshold fields.
- `PSP_PARITY_STATUS`, with summary flags for corrected, non-fatal, fatal, and SERR-class parity errors.
- `PSP_PARITY_ERROR_STATUS_UNCORR_GRP0..4`, `PSP_PARITY_ERROR_STATUS_UCP_GRP0..4`, and `PSP_PARITY_ERROR_STATUS_CORR_GRP0..4`, each exposing 32 one-bit `ParityErrDetected_Id*` fields.
- `PSP_PARITY_COUNTER_UCP_GRP0..4` and `PSP_PARITY_COUNTER_CORR_GRP0..4`, each with a 16-bit `ThresholdCounter` and a high-bit `ResetEn`.
- `PSP_ParitySerr_ACTION_CONTROL`, `PSP_ParityFatal_ACTION_CONTROL`, `PSP_ParityNonFatal_ACTION_CONTROL`, and `PSP_ParityCorr_ACTION_CONTROL`, each exposing `APML_ERR_En`.

The reset defaults in `nbio_7_0_default.h` show zeroed status/counter/action registers and `smnPSP_PARITY_CONTROL_0_DEFAULT` as `0x00010001`, indicating nonzero default thresholds. These masks are therefore relevant to RAS/error reporting paths, even though no in-tree direct consumer of these exact field names was found in the requested search scope.

### NB Device-Indirect Configuration Bridges

The range contains repeated device-indirect configuration blocks for:

- `NB_PCIE0DEVINDCFG0..6`
- `NB_NBIF1DEVINDCFG0..1`
- `NB_INTSBDEVINDCFG0`

Each instance has the same pattern:

- `IOHC_Bridge_CNTL`: disables or policy bits for bridge, bus master, config access, peer-to-peer, VDM, unsupported-request masking, posted-write passing, no-snoop, forced posted-write response, IDO mode, external device plug/CRS handling, CRS enable, APIC enable, and APIC range.
- `IOHC_Bridge_STATUS`: `MaskUR_Status`.
- `STEERING_CNTL`: `ForceSteering` and 8-bit `SteeringValue`.
- `IOHC_Bridge_SCRATCH_0/1`: full-width scratch fields.

These repeated macros model per-port or per-device NB routing and bridge behavior. The default header shows these blocks defaulting to zero. A driver or firmware path that programs these fields is changing low-level PCIe/NBIO routing, config visibility, APIC routing, and unsupported-request behavior for a specific device-indirect target.

### PCIe Dummy Configuration Functions

`NB_PCIEDUMMY0_1_*` and `NB_PCIEDUMMY1_1_*` describe minimal PCI configuration fields for dummy PCIe functions:

- vendor and device ID.
- command and status words.
- class code and revision ID.
- header type and writeable header-type device-type bit.

The defaults show `HEADER_TYPE` values with the device-type bit set and `HEADER_TYPE_W` defaulting to `0x80`. These fields appear intended to expose or emulate dummy config-space endpoints rather than drive normal GPU engines.

### Indirect Register Access Windows

The chunk defines simple full-width index/data windows:

- `IOMMU_SMN_INDEX_0`, `IOMMU_SMN_DATA_0`, `IOMMU_SMN_INDEX_1`, `IOMMU_SMN_DATA_1`.
- `IOAPIC_MIO_INDEX`, `IOAPIC_MIO_DATA`.
- `NB_PCIE0RCBDG_INDCFG0..6_RC_SMN_INDEX/DATA`.
- `NB_NBIF1RCBDG_INDCFG0..1_RC_SMN_INDEX/DATA`.

These macros describe indirect access registers rather than ordinary configuration knobs. Correct control flow for consumers is write-index then read or write data, with any required serialization handled by the calling driver or firmware path. The header itself does not encode sequencing or locking, so callers must avoid interleaving accesses to the same indirect window.

### IOMMU L2 PCI Capability and SMMU Identity

The `IOMMU_L2_1_*` block defines PCI-like configuration fields for the IOMMU L2 function:

- basic PCI identity and command/status fields, including IO, memory, bus-master, parity, SERR, interrupt disable, abort/error, and capability-list bits.
- revision, programming interface, class, cache-line, latency, header, BIST, adapter ID, capabilities pointer, interrupt line/pin, and MSI/MSI mapping fields.
- AMD IOMMU capability fields for cap header, base address low/high, range, miscellaneous capability sizing, guest/GA features, SMMU MMIO enable/lock, and writeable capability controls.
- DSFX/DSSX/DSCX control or dummy status fields.
- L2-to-IOHC poison/stall controls.
- SMMU ID registers: `SMMU_MMIO_IDR0_W`, `IDR1_W`, `IDR2_W`, `IDR3_W`, `IDR5_W`, `IIDR_W`, and `AIDR_W`.

Defaults in `nbio_7_0_default.h` include AMD vendor ID `0x1022`, device ID `0x15d1`, an interrupt pin default of `1`, and nonzero capability/feature defaults such as `IOMMU_MMIO_CONTROL0_W`, `IOMMU_MMIO_CONTROL1_W`, and `SMMU_MMIO_IDR0_W`. These masks are therefore part of the contract through which the hardware advertises IOMMU/SMMU capabilities to platform code.

### IOMMU L2 Index-Control Block

The final part of the chunk enters `nbio_iohub_iommu_l2indx_l2indxcfg` and defines control fields for IOMMU L2 behavior:

- `L2_STATUS_1` and `L2_SB_LOCATION`, exposing L2 status and sideband location fields.
- `L2_CONTROL_5` and `L2_CONTROL_6`, controlling queue arbitration priority, flow-control disables, DTC update policy, forced table-walk behavior, partial PTC control, hysteresis, sequential invalidation burst limits, and performance thresholding.
- `L2_PDC_CONTROL`, `L2_PDC_HASH_CONTROL`, and `L2_PDC_WAY_CONTROL`, configuring the page-directory cache: LRU update priority, parity enable/support, invalidation selection, soft invalidate, search direction, bypass, way/entry counts, address mask, and disabled/access-disabled ways.
- `L2B_UPDATE_FILTER_CNTL`, covering L2B update-filter bypass and read latency.
- `L2_TW_CONTROL`, `L2_TW_CONTROL_1..3`, covering table-walker coherency, prefetch, PTE behavior on untranslated/address-translation excludes, filter disables, parity-error walking behavior, access/AP bit handling, guest prefetch, and debug address controls.
- `L2_CP_CONTROL` and `L2_CP_CONTROL_1`, covering command-processor prefetch disable, flush-on-wait/invalidate, read delay, and L1-off controls.
- `IOMMU_L2_GUEST_ADDR_CNTRL`, defining a 24-bit guest address mask.
- `L2_CREDIT_CONTROL_0/1`, defining flow-control credit counts and override bits for FC, ATS, PDTI, TWEL, CP prefetch, and PPR MCIF paths.
- `L2_ERR_RULE_CONTROL_0..2`, defining rule locks and disable bitmaps.
- `L2_L2B_CK_GATE_CONTROL`, controlling L2B register/dynamic/misc/cache clock gating, gating length, and stop timing.
- `PPR_CONTROL`, controlling page-request interrupt time/request delays and interrupt coalescing.
- `L2_L2B_PGSIZE_CONTROL`, defining guest and host page-size fields.
- `L2_L2B_MEMPWR_GATE_1`, enabling light sleep, deep sleep, shutdown, and memory selection bits for L2B/register/cache power gating.

The default header gives meaningful nonzero reset values for several of these, including `L2_CONTROL_5`, `L2_CONTROL_6`, `L2_PDC_CONTROL`, `L2B_UPDATE_FILTER_CNTL`, `L2_TW_CONTROL`, `L2_CP_CONTROL`, `L2_CREDIT_CONTROL_0/1`, `L2_L2B_CK_GATE_CONTROL`, and `L2_L2B_PGSIZE_CONTROL`. That makes these fields part of hardware initialization state even when the driver never explicitly writes them.

## Control Flow

There is no runtime control flow in this header. Runtime flow is imposed by caller code that reads, modifies, and writes registers. For ordinary fields, the typical pattern is read register, compose a new value with `REG_SET_FIELD` or masks/shifts, then write it back. For status fields, callers read and mask with the relevant `_MASK` constant and shift if needed.

Indirect windows in this chunk require stronger ordering from callers: write an index register such as `IOMMU_SMN_INDEX_*` or `*_RC_SMN_INDEX`, then access the matching data register. The header does not provide mutual exclusion, so any shared indirect window needs caller-side serialization.

Command-like fields also need caller discipline. Examples include `PDCSoftInvalidate`, counter `ResetEn` bits, action-control enables, and debug/table-walker controls. These are not passive metadata fields; writes may trigger hardware state changes, reset counters, alter invalidation behavior, or expose error signaling paths.

## State and Persistence

The macros themselves are compile-time constants and hold no state. The state is in hardware registers:

- PSP poison/parity status and counters persist in device register state until hardware clears them, driver code clears them, or reset occurs.
- NB bridge control, steering, scratch, dummy PCI config, IOMMU capability overrides, and IOMMU L2 controls are device configuration state.
- Indirect index registers are transient cursor state for their matching data ports.
- L2 cache, table-walker, credit, page-size, clock-gating, and power-gating fields directly affect IOMMU runtime behavior while programmed.

The companion default header records reset defaults for the same logical registers, but this chunk does not enforce defaults or restore state across suspend/resume, GPU reset, PCI function reset, or SR-IOV transitions.

## Dependencies and Integration Points

This chunk depends on AMDGPU register-helper conventions and the matching NBIO 7.0 generated headers:

- `nbio_7_0_offset.h` for configuration register offsets, especially `cfg...` definitions.
- `nbio_7_0_default.h` for default values.
- `nbio_7_0_smn.h` for the smaller set of SMN constants used by this NBIO generation.
- SOC15/NBIO access helpers used by `amdgpu/nbio_v7_0.c` and `amdgpu/soc15.c`.
- SMU10 power-management include aggregation through `pm/powerplay/hwmgr/smu10_inc.h`.

Although direct in-tree references to many field names in this exact chunk are sparse, the header is included wholesale for NBIO 7.0 ASIC support. Generated register headers are integration boundaries with firmware tables, hardware programming sequences, RAS handling, IOMMU setup, and platform power-management code.

## Risks

- Wrong masks or shifts silently program the wrong hardware bits. This is especially risky for bridge disable, bus-master/config disable, P2P, APIC routing, IOMMU capability, table-walker, and clock/power-gating fields.
- Indirect index/data windows can race if multiple callers use the same window without serialization.
- Treating status bits as writeable configuration, or configuration bits as harmless status, can clear diagnostics, reset counters, or alter hardware behavior.
- Reserved fields are explicitly represented in several registers. Callers should preserve reserved bits unless hardware documentation says otherwise.
- `L2_PDC_CONTROL`, `L2_TW_CONTROL`, credit controls, and page-size controls can affect address translation correctness and performance. Bad programming may cause DMA/IOMMU faults, stale translations, invalid prefetch behavior, or page-request storms.
- Power and clock-gating fields can create hangs or lost register accesses if changed while the L2 block is active or without the required idle checks.
- The chunk boundary is mid-register-family: `L2_L2B_MEMPWR_GATE_2` is named but its fields are not included here. Research consumers should merge this with the following chunk before making conclusions about the full memory-power-gating family.

## Test Signals

Useful validation signals for changes touching consumers of these macros include:

- Successful build of the AMDGPU driver with NBIO 7.0 support enabled; generated macro names must compile in all included translation units.
- Boot/probe logs showing NBIO 7.0 ASIC initialization without PCI config, IOMMU, PSP, or RAS errors.
- Register readback checks where a caller writes a field via `REG_SET_FIELD` and confirms only the intended masked bits changed.
- IOMMU stress with DMA, GPU memory management, KFD/ROCm workloads, and page-request capable clients to catch `L2_*`, PDC, table-walker, and PPR regressions.
- Suspend/resume and GPU reset tests to confirm hardware defaults or driver restore paths leave parity status, indirect windows, IOMMU capabilities, and L2 controls coherent.
- RAS/error-injection or fault-observation tests, where available, to validate PSP parity status, counters, action controls, poison status, and APML error signaling.
- SR-IOV or multi-function PCI tests if bridge control, dummy config functions, steering, or per-device indirect config fields are touched by platform code.
