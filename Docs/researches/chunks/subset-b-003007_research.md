# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 4882-7314

## Scope

This chunk covers lines 4882-7314 of the generated AMD NBIO 6.1 shift/mask header. It contains 2,433 source lines, including 2,126 `#define` entries and 301 register-group comments. The chunk is pure C preprocessor data: it defines bit positions (`__SHIFT`) and bit masks (`_MASK`) for NBIO/PCIe configuration-space registers. There are no functions, structs, enums, storage objects, allocations, locking primitives, or executable branches in this slice.

The slice starts in the middle of the `BIF_CFG_DEV0_EPF1_0_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_HVVM_MBOX_DW1` field group, after the shift definitions and early masks from the previous chunk. It ends in the middle of `BIF_CFG_DEV0_EPF0_VF1_0_PCIE_UNCORR_ERR_MASK`, with the remainder of that register's mask/shift definitions continuing in the next chunk.

## Purpose

The purpose of this header section is to expose the hardware bit layout for several NBIO 6.1 PCIe configuration address blocks to AMDGPU code. AMDGPU register helpers build register values by concatenating a register macro name and field macro name, so a definition such as:

- `BIF_CFG_DEV0_SWDS0_DEVICE_CNTL__MAX_PAYLOAD_SIZE__SHIFT`
- `BIF_CFG_DEV0_SWDS0_DEVICE_CNTL__MAX_PAYLOAD_SIZE_MASK`

is the compile-time contract that lets `REG_SET_FIELD(value, BIF_CFG_DEV0_SWDS0_DEVICE_CNTL, MAX_PAYLOAD_SIZE, field_value)` clear and insert the correct bits.

The covered register groups are mostly PCI/PCIe configuration-space fields for:

- the tail of an EPF1 GPUIOV vendor-specific SR-IOV mailbox/resource block,
- the `nbio_nbif_bif_cfg_dev0_swds_bifcfgdecp` address block for a downstream-port style `SWDS0` function,
- the beginning of `nbio_nbif_bif_cfg_dev0_epf0_vf0_bifcfgdecp`, a virtual-function configuration block for EPF0 VF0,
- the beginning of `nbio_nbif_bif_cfg_dev0_epf0_vf1_bifcfgdecp`, a similar block for EPF0 VF1.

The definitions are hardware-descriptive rather than policy-descriptive. Runtime policy lives in AMDGPU NBIO, PCIe, interrupt, SR-IOV, reset, and power-management code that reads/writes these registers through the companion address and default headers.

## Main Register Areas

### EPF1 GPUIOV Vendor-Specific Block

Lines 4882-5094 complete a GPUIOV VSEC-style block under the `BIF_CFG_DEV0_EPF1_0_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_*` prefix.

Important field families:

- `HVVM_MBOX_DW1` tail masks for `VF2` through `VF15`, where each VF has `TRN_ACK` and `RCV_VALID` bits. These are mailbox handshake/status fields for host/virtual-machine communication in a GPU I/O virtualization path.
- `HVVM_MBOX_DW2` fields `PF_TRN_ACK` and `PF_RCV_VALID`, providing the physical-function side of the same handshake pattern.
- `CONTEXT` fields `CONTEXT_SIZE`, `LOC`, and `CONTEXT_OFFSET`, which describe the size/location/offset metadata for the GPUIOV context payload.
- `TOTAL_FB` fields `TOTAL_FB_AVAILABLE` and `TOTAL_FB_CONSUMED`, splitting a 32-bit register into lower and upper 16-bit accounting fields for frame-buffer capacity tracking.
- `OFFSETS` fields `UVDSCH_OFFSET`, `VCESCH_OFFSET`, and `GFXSCH_OFFSET`, which point to scheduler blocks for UVD, VCE, and GFX resources.
- `VF0_FB` through `VF15_FB`, each split into `VF*_FB_SIZE` and `VF*_FB_OFFSET` 16-bit fields. These describe per-virtual-function frame-buffer allocation windows.
- `UVDSCH_DW0..DW8`, `VCESCH_DW0..DW8`, and `GFXSCH_DW0..DW8`, each exposing one full 32-bit `DW*` field. These are opaque scheduler descriptor dwords from the field-header perspective.

This part is SR-IOV-sensitive. If any size, offset, or valid/ack mask is wrong, PF/VF resource discovery or mailbox synchronization can fail in ways that are hard to diagnose from ordinary graphics tests.

### SWDS0 PCI/PCIe Configuration Block

Lines 5097-6184 define the full `nbio_nbif_bif_cfg_dev0_swds_bifcfgdecp` address block, with macros under `BIF_CFG_DEV0_SWDS0_*`.

The block starts with classic PCI configuration fields:

- identity and class registers: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`;
- command/status registers: `COMMAND`, `STATUS`, `SECONDARY_STATUS`;
- bridge-like layout registers: `HEADER`, `BIST`, `BASE_ADDR_1`, `SUB_BUS_NUMBER_LATENCY`, `IO_BASE_LIMIT`, `MEM_BASE_LIMIT`, `PREF_BASE_LIMIT`, `PREF_BASE_UPPER`, `PREF_LIMIT_UPPER`, and `IO_BASE_LIMIT_HI`;
- interrupt and bridge-control fields: `CAP_PTR`, `INTERRUPT_LINE`, `INTERRUPT_PIN`, and `IRQ_BRIDGE_CNTL`.

It then defines PCI power-management capability fields:

- `PMI_CAP_LIST` with `CAP_ID` and `NEXT_PTR`;
- `PMI_CAP` with version, PME clock, device-specific init, auxiliary-current, D1/D2 support, and PME support fields;
- `PMI_STATUS_CNTL` with power state, PME enable/status, data select/scale, bus power enable, and data fields.

The PCIe capability section covers:

- `PCIE_CAP_LIST` and `PCIE_CAP`;
- `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS`;
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS`;
- `SLOT_CAP`, `SLOT_CNTL`, and `SLOT_STATUS`;
- `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`, and reserved slot-capability-2 registers;
- MSI message capability fields (`MSI_CAP_LIST`, `MSI_MSG_CNTL`, address/data registers);
- SSID and vendor-specific capability fields;
- virtual-channel capability/control/status fields for VC0 and VC1;
- device serial-number enhanced capability fields;
- PCIe advanced error reporting fields;
- secondary PCIe enhanced capability and per-lane equalization control fields for lanes 0 through 15;
- ACS enhanced capability fields (`PCIE_ACS_ENH_CAP_LIST`, `PCIE_ACS_CAP`, `PCIE_ACS_CNTL`).

The SWDS0 block is a high-density map of downstream-port capability state. Field names mirror PCIe architectural concepts: max payload and max read request sizing, relaxed ordering and no-snoop controls, link speed/width/training state, ASPM and clock power management, hotplug/slot controls, MSI configuration, VC arbitration, AER reporting/masking/severity, equalization presets, and ACS validation/translation/blocking controls.

### EPF0 VF0 Configuration Block

Lines 6185-6838 define the start and most of the complete `nbio_nbif_bif_cfg_dev0_epf0_vf0_bifcfgdecp` address block under `BIF_CFG_DEV0_EPF0_VF0_0_*`.

This block repeats endpoint/VF-oriented PCI configuration fields rather than the SWDS0 bridge-oriented subset:

- PCI identity and class fields (`VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`);
- endpoint command/status and header fields;
- six BAR-style registers (`BASE_ADDR_1` through `BASE_ADDR_6`) and `ROM_BASE_ADDR`;
- subsystem identity via `ADAPTER_ID`;
- interrupt line/pin and capability pointer fields;
- PCIe capability fields for device/link control and status;
- device capability 2/control 2/link capability 2/control 2/status 2;
- MSI and MSI-X capability blocks, including 64-bit message-data, mask, pending, table, and PBA fields;
- vendor-specific enhanced capability header and scratch registers;
- advanced error reporting status/mask/severity, correctable error status/mask, AER capability/control, header logs, and TLP prefix logs;
- ATS enhanced capability/control fields;
- ARI enhanced capability/control fields.

Notable semantic differences from SWDS0 include endpoint-specific BAR coverage, `INITIATE_FLR` in `DEVICE_CNTL`, and virtualization-related capabilities such as ATS and ARI. These fields are relevant to SR-IOV VF exposure, PCIe function reset behavior, interrupt delivery, and DMA address-translation behavior.

### EPF0 VF1 Configuration Block Start

Lines 6839-7314 begin the `nbio_nbif_bif_cfg_dev0_epf0_vf1_bifcfgdecp` block under `BIF_CFG_DEV0_EPF0_VF1_0_*`.

The VF1 block closely mirrors the VF0 block through:

- identity, command/status, class, header, BIST, BAR, ROM, adapter ID, cap pointer, and interrupt fields;
- PCIe capability, device/link capability/control/status fields;
- capability 2 and link 2 fields;
- MSI/MSI-X fields;
- vendor-specific enhanced capability fields;
- the advanced-error-reporting enhanced capability list;
- `PCIE_UNCORR_ERR_STATUS`;
- the first four shift definitions for `PCIE_UNCORR_ERR_MASK` before the chunk ends.

Because the chunk ends mid-register, consumers of `BIF_CFG_DEV0_EPF0_VF1_0_PCIE_UNCORR_ERR_MASK` depend on the next chunk for the remaining fields and masks. A merge/reconciliation pass must treat these adjacent chunks as one continuous generated register map.

## APIs, Types, and Usage Pattern

There are no C APIs or types declared here. The important "API" is the macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the already-shifted bit mask.

AMDGPU helpers use that convention. In this tree, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c` includes:

- `nbio/nbio_6_1_default.h`,
- `nbio/nbio_6_1_offset.h`,
- `nbio/nbio_6_1_sh_mask.h`,
- `nbio/nbio_6_1_smn.h`.

That implementation uses SOC15/MMIO helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15`, and `REG_SET_FIELD` to manipulate NBIO registers. The exact chunk fields are not heavily hand-referenced by name in C code; they are part of a generated register-definition surface where address macros from `nbio_6_1_offset.h`, defaults from `nbio_6_1_default.h`, and field masks from this file must stay synchronized.

The immediate companion defaults for this region exist in `nbio_6_1_default.h`, including default values for the GPUIOV VSEC registers, SWDS0 config registers, VF0 registers, and VF1 registers. Those default values are useful for generated-table validation and bring-up comparisons, but this `sh_mask` file is the source of field extraction/insertion bit positions.

## Control Flow

This chunk has no executable control flow. Its effect occurs at compile time:

1. The preprocessor makes the constants available to AMDGPU source files.
2. Register helper macros splice register and field names into the corresponding `__SHIFT` and `_MASK` identifiers.
3. Compiled code reads or writes hardware registers using the computed masks/shifts.
4. Hardware behavior changes according to the actual PCIe/NBIO register semantics.

The runtime control flow that uses this style appears in `nbio_v6_1.c`: NBIO initialization and helper callbacks configure HDP remapping, memory-controller access, doorbell ranges, IH interrupt controls, clock gating, PCIe ordering, ASPM/LTR-related state, and NBIO function tables. This chunk is data that such code can use, not code that schedules or branches by itself.

## State and Persistence

The header defines constants only and holds no software state. State lives in hardware registers and PCIe configuration space:

- GPUIOV mailbox bits track transient PF/VF communication state.
- GPUIOV frame-buffer and scheduler descriptor fields describe per-VF resource assignment state.
- PCI command, status, capability, BAR, MSI/MSI-X, AER, ATS, ARI, VC, ACS, and link registers are device configuration state.
- Some fields are sticky hardware status bits, write-one-to-clear error bits, or capability fields controlled by hardware/firmware rather than ordinary driver writes.

Persistence depends on hardware reset domains. Many fields reset on function-level reset, secondary-bus reset, hot reset, GPU reset, or full device reset; some capability values are effectively fixed by hardware straps or firmware. The source file does not encode reset policy, ordering constraints, or write semantics; those must be inferred from hardware manuals, companion default headers, and driver code.

## Dependencies and Integration Points

Key dependencies:

- `nbio_6_1_offset.h` supplies register addresses/offsets matching these register names.
- `nbio_6_1_default.h` supplies default register values for the same generated register groups.
- `nbio_6_1_smn.h` supplies SMN addresses used by NBIO access paths.
- AMDGPU register helpers (`REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15`, `RREG32_PCIE`, `WREG32_PCIE`) depend on the exact macro naming convention.
- Linux PCI/PCIe core behavior is an external integration point for config-space concepts such as BARs, MSI/MSI-X, AER, ACS, ATS, ARI, link status, and FLR.

Driver integration concerns by domain:

- SR-IOV and virtualization: GPUIOV mailbox, VF FB size/offset, scheduler descriptors, ATS, ARI, and VF BAR/MSI/MSI-X fields affect PF/VF provisioning and guest-visible device behavior.
- PCIe link and power management: link capability/control/status, ASPM-related fields, LTR enablement, OBFF, and completion timeout controls tie into NBIO power/performance tuning.
- Error handling: AER uncorrectable/correctable status, masks, severity, header logs, and TLP prefix logs feed diagnostics and recovery behavior.
- Isolation/security: ACS fields define source validation, translation blocking, P2P request/completion redirect, upstream forwarding, egress control, and direct translated P2P behavior.
- Interrupt delivery: MSI and MSI-X fields define enablement, vector counts, message address/data, masks, pending bits, table/PBA BAR indicator, and table offsets.

## Risks

- Bitfield drift: This is generated hardware data. A single wrong mask or shift can silently target the wrong hardware bit while still compiling cleanly.
- Cross-header mismatch: The register names in this file must align with offsets in `nbio_6_1_offset.h` and defaults in `nbio_6_1_default.h`. A mismatch can cause code to write correct bitfields to the wrong address, or to interpret defaults incorrectly.
- Chunk-boundary hazards: This chunk begins and ends mid-register-group. Research or generation tools must merge adjacent chunks before making per-file conclusions about `HVVM_MBOX_DW1` and `BIF_CFG_DEV0_EPF0_VF1_0_PCIE_UNCORR_ERR_MASK`.
- SR-IOV isolation risk: GPUIOV VF frame-buffer sizing/offset, scheduler descriptors, ATS, ARI, ACS, and MSI-X fields affect guest-visible resource boundaries and interrupt routing. Incorrect definitions can become isolation or stability bugs, not just display bugs.
- Error-reporting ambiguity: AER status/mask/severity fields often have special write/clear semantics. Treating status bits as ordinary writable configuration fields can lose diagnostics or mask real link errors.
- Reserved-field handling: Several registers include reserved fields or full-width opaque dwords. Driver code must preserve reserved bits unless hardware documentation explicitly allows writes.
- Capability consistency: PCIe capability-list `NEXT_PTR`, capability IDs, and enhanced capability headers must be coherent with the actual config-space layout. Incorrect constants can confuse enumeration, debug tooling, or virtualization emulation.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware bring-up oriented:

- Build coverage: compile AMDGPU code that includes `nbio_6_1_sh_mask.h`; macro naming errors are caught when `REG_SET_FIELD`/`REG_GET_FIELD` references are compiled.
- Generated-header consistency checks: compare this header against the matching `nbio_6_1_offset.h` and `nbio_6_1_default.h` for missing/renamed register groups, especially around GPUIOV, SWDS0, EPF0 VF0, and EPF0 VF1.
- PCIe config-space inspection: use debugfs, lspci-style dumps, or driver traces on supported hardware to verify decoded PCIe capability fields such as link speed/width, MSI/MSI-X tables, AER status, ACS, ATS, and ARI match expected hardware behavior.
- SR-IOV validation: enable VFs and confirm PF/VF mailbox handshakes, per-VF FB accounting, VF BAR exposure, MSI/MSI-X delivery, FLR behavior, and guest attach/detach paths.
- Error-path validation: inject or observe PCIe AER events and confirm status, mask, severity, header-log, and TLP-prefix-log fields decode correctly.
- Reset and suspend/resume validation: exercise FLR, GPU reset, suspend/resume, and VM attach/detach to ensure hardware state returns to expected defaults and driver programming still lands on the intended fields.

## Summary

This chunk is a generated NBIO 6.1 register-field contract for GPU I/O virtualization and PCIe configuration-space blocks. It does not implement runtime behavior, but it is a critical dependency for any code that decodes or programs these registers. The main engineering concern is preserving exact alignment between hardware documentation, generated offsets/defaults, and the `__SHIFT`/`_MASK` pairs used by AMDGPU register helper macros.
