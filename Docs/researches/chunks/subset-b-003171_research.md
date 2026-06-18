# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 26924-29354

## Scope

This chunk is a generated AMDGPU NBIO 7.2.0 shift/mask header slice. It contains 2,169 preprocessor definitions and register-family comments only; there are no functions, structs, branches, locks, allocations, or runtime storage in this range. The slice starts at the end of `BIFPLR4_LANE_2_EQUALIZATION_CNTL_16GT` masks, covers the rest of the `BIFPLR4` PCIe 16 GT/CCIX/ESM-related capability and config-space field maps, crosses the `addressBlock: nbio_pcie0_bifplr5_cfgdecp` boundary, and ends inside `BIFPLR5_PCIE_ESM_CAP_7`.

Because this is a chunk of a large generated header, both boundaries are artificial. The matching `BIFPLR4_LANE_2_EQUALIZATION_CNTL_16GT` shift fields are before this chunk, and the masks for `BIFPLR5_PCIE_ESM_CAP_7` plus later `BIFPLR5` registers continue after it.

## Purpose

The purpose of this region is to provide bit positions and masks for AMD NBIO PCIe root-port or bridge configuration registers. Runtime code can combine these constants with register offsets from `nbio_7_2_0_offset.h` and AMDGPU register helpers to read, write, or decode NBIO PCIe capability/configuration fields without open-coding bit arithmetic.

The covered register families are mostly PCIe configuration-space and extended-capability metadata:

- `BIFPLR4_*` per-lane 16 GT equalization presets, PCIe margining controls/status, CCIX capability/control/status fields, 20 GT and 25 GT enhanced speed mode lane equalization fields, and the end of the BIFPLR4 capability set.
- `BIFPLR5_*` conventional bridge config header fields, PCI power management, PCIe capability registers, MSI, subsystem ID, MSI mapping, vendor-specific capability, virtual channel, device serial number, AER, secondary PCIe, access control services, multicast, L1 PM substates, downstream port containment, root-port PIO error reporting, and enhanced speed mode capability fields.

## Important Macros And Field Families

The `BIFPLR4_LANE_<n>_EQUALIZATION_CNTL_16GT` definitions expose two 4-bit fields per lane: downstream port 16 GT transmit preset at bits 0-3 and upstream port 16 GT transmit preset at bits 4-7. This chunk completes lanes 3-15 and includes the final masks for lane 2.

`BIFPLR4_PCIE_MARGINING_ENH_CAP_LIST`, `BIFPLR4_MARGINING_PORT_CAP`, and `BIFPLR4_MARGINING_PORT_STATUS` define a PCIe margining enhanced capability header and readiness/software-readiness bits. `BIFPLR4_LANE_0_MARGINING_LANE_CNTL` through `BIFPLR4_LANE_15_MARGINING_LANE_STATUS` repeat a lane control/status template with receiver number, margin type, usage model, and margin payload fields.

`BIFPLR4_PCIE_CCIX_*` defines CCIX capability-list/header fields, protocol/speed-width capability flags, required/optional ESM support bitmaps, status, control, and transaction capability/control fields. The ESM required and optional maps use dense one-bit-per-speed fields such as `ESM_SUPPORT_20P0G` through `ESM_SUPPORT_25P0G`.

`BIFPLR4_ESM_LANE_<n>_EQUALIZATION_CNTL_20GT` and `BIFPLR4_ESM_LANE_<n>_EQUALIZATION_CNTL_25GT` mirror the per-lane preset pattern for enhanced speed mode operation. Each lane has DSP and USP transmit-preset fields at nibbles 0 and 1.

`BIFPLR5_VENDOR_ID` through `BIFPLR5_IRQ_BRIDGE_CNTL` map the beginning of a PCI-to-PCI bridge configuration header: IDs, command/status bits, class code, bus numbers, IO/memory/prefetchable ranges, ROM base, interrupt routing, and bridge-control flags. These fields are configuration-space definitions rather than normal MMIO control flow.

`BIFPLR5_PMI_*`, `BIFPLR5_PCIE_*`, and `BIFPLR5_MSI_*` cover standard PCI PM, PCIe, and MSI capability fields. Important groups include device/link/slot/root capability, control, and status fields; link speed/width and retrain/autonomous-bandwidth status; extended tags, relaxed ordering, no-snoop, max payload/read request size; MSI address/data and vector count fields.

`BIFPLR5_PCIE_VC*`, `BIFPLR5_PCIE_ACS_*`, `BIFPLR5_PCIE_MC_*`, and `BIFPLR5_PCIE_L1_PM_SUB_*` expose virtual-channel, ACS, multicast, and L1 PM substate capability/control fields. These are integration points for PCIe topology, isolation, power management, and advanced routing behavior.

`BIFPLR5_PCIE_UNCORR_ERR_*`, `BIFPLR5_PCIE_CORR_ERR_*`, `BIFPLR5_PCIE_ADV_ERR_CAP_CNTL`, `BIFPLR5_PCIE_ROOT_ERR_*`, `BIFPLR5_PCIE_DPC_*`, and `BIFPLR5_PCIE_RP_PIO_*` describe AER/DPC/root-port PIO error status, mask, severity, command, source-ID, and header/prefix log fields. These masks are the decode table for error reporting and containment diagnostics.

`BIFPLR5_PCIE_ESM_CAP_LIST`, `BIFPLR5_PCIE_ESM_HEADER_*`, `BIFPLR5_PCIE_ESM_STATUS`, `BIFPLR5_PCIE_ESM_CTRL`, and `BIFPLR5_PCIE_ESM_CAP_1` through the partial `CAP_7` range provide enhanced-speed-mode capability metadata. The cap maps are one-bit support tables for speeds in 0.1 GT/s increments, starting at 4.0 GT/s in `CAP_1` and reaching 25.6 GT/s at this chunk's end.

## Control Flow And State Behavior

There is no control flow in this chunk. The only behavior is compile-time substitution by the C preprocessor. State belongs to NBIO/PCIe hardware registers outside this file; these macros merely define how callers isolate or place fields within those registers.

The state represented here includes hardware configuration and live PCIe link state, such as equalization presets, lane margining control/status, advertised capabilities, command/status enables, AER/DPC error latches, MSI routing fields, link status bits, and enhanced speed-mode support bitmaps. Persistence is hardware-defined: many fields are strap-, firmware-, or reset-initialized, some are writable configuration bits, and status/error fields may be sticky until hardware or software clears them. The header itself persists no values.

## Dependencies And Integration Points

The nearest required companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h`, which defines matching `cfgBIFPLR4_*` and `cfgBIFPLR5_*` offsets. For example, the offset header maps `cfgBIFPLR4_LANE_3_EQUALIZATION_CNTL_16GT` and `cfgBIFPLR4_PCIE_MARGINING_ENH_CAP_LIST`, then begins the `cfgBIFPLR5_*` config-space address block used by the masks in this chunk.

Consumers include AMDGPU NBIO code and common AMD register helper macros such as `REG_GET_FIELD`, `REG_SET_FIELD`, `REG_FIELD_MASK`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET` when those paths need field-aware access. The exact runtime users may be indirect because the generated header is usually included through NBIO version-specific aggregate headers rather than referenced as a standalone API.

The BIFPLR4/BIFPLR5 names line up with PCIe config decode blocks, so integration is mainly with PCI enumeration/configuration, link training/equalization, link diagnostics, SR-IOV/IOMMU isolation expectations through ACS/ATS-adjacent capabilities in surrounding headers, interrupt programming through MSI fields, power management through PM/L1 substate fields, and error handling through AER/DPC/root-port PIO fields.

## Risks And Edge Cases

- The chunk begins and ends mid-family. A whole-file summary must merge the previous chunk for complete `BIFPLR4_LANE_2_EQUALIZATION_CNTL_16GT` semantics and the next chunk for complete `BIFPLR5_PCIE_ESM_CAP_7` masks plus later BIFPLR5 fields.
- These macros are generated hardware ABI constants. A single incorrect shift or mask can silently corrupt neighboring bits in PCIe config space, which can affect link training, power management, interrupt delivery, or error handling.
- Several fields are status/error latches or capability advertisements rather than driver-owned policy bits. Treating read-only, reserved, or hardware-owned fields as writable could produce undefined hardware behavior.
- Repeated lane and speed bitmap definitions are easy to misuse with copy/paste logic. Lane number, direction (`DSP` versus `USP`), speed family (`16GT`, `20GT`, `25GT`, or ESM cap speed buckets), and BIFPLR instance must all match the intended register offset.
- PCIe extended capability list fields (`CAP_ID`, `CAP_VER`, `NEXT_PTR`) are structural. Bad interpretation can break capability traversal or cause diagnostics to attribute fields to the wrong capability.
- The BIFPLR5 block is a bridge/root-port view rather than an endpoint-function view. Code shared with endpoint masks should not assume the same offsets, access permissions, or bit meanings.

## Test And Validation Signals

Useful validation for this chunk is mostly compile-time and hardware-facing:

- Build coverage should compile NBIO 7.2.0 AMDGPU code with this header and its offset companion included, catching missing or renamed macros.
- Static checks can compare each `__SHIFT`/`_MASK` pair against generated register metadata and verify that masks occupy the expected bit ranges.
- Hardware or simulator smoke tests should exercise PCIe config reads for BIFPLR4/BIFPLR5 capability headers and confirm `CAP_ID`, `CAP_VER`, and `NEXT_PTR` decoding matches the PCIe capability chain.
- Link-training diagnostics can verify that 16 GT, 20 GT, and 25 GT equalization/margining fields decode correctly per lane and do not swap upstream/downstream presets.
- Error-injection or AER/DPC tests can confirm uncorrectable/correctable/root-port PIO status, mask, severity, source-ID, and header-log fields decode as expected.
- Power-management tests should observe PM and L1 substate capability/control fields around suspend/resume or ASPM changes, while ensuring reserved bits are preserved.

## Chunk Boundary Notes

Line 26924 is the second mask for `BIFPLR4_LANE_2_EQUALIZATION_CNTL_16GT`; its comment and shift macros are in the previous chunk. Lines 26926-28130 continue BIFPLR4 lane equalization, margining, CCIX, and ESM definitions. Around the explicit `addressBlock: nbio_pcie0_bifplr5_cfgdecp` comment, the namespace changes to BIFPLR5 and starts a new PCIe config decode block. Line 29354 stops after `BIFPLR5_PCIE_ESM_CAP_7__ESM_25P6G__SHIFT`; the masks and remaining ESM speed bits continue after this chunk.
