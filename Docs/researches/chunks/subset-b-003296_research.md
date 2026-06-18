# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 89761-92179

## Scope

This chunk is a generated AMDGPU NBIO 7.7.0 PCIe register field-mask header segment. It contains C preprocessor constants only: every register field has a `__SHIFT` macro for the bit position and a matching `_MASK` macro for the covered bits. There are no functions, structs, executable branches, or persistent software objects in this slice.

The covered lines finish the `BIFPLR1_1` PCIe logical port register definitions and then enter the next address block, `nbio_pcie1_bifplr2_cfgdecp`, beginning the `BIFPLR2_1` PCI configuration and PCIe capability space definitions through `BIFPLR2_1_PCIE_LANE_ERROR_STATUS`.

## Purpose

The header gives AMDGPU NBIO client code stable names for extracting and composing hardware register fields on NBIO 7.7.0 ASICs. Consumers include the matching offset/default headers and use these masks with register access helpers such as `RREG32`, `WREG32`, `REG_GET_FIELD`, `REG_SET_FIELD`, and related AMDGPU macro families. The constants encode the hardware ABI, not a software policy layer.

Within this chunk, the purpose is split across two PCIe port/function families:

- `BIFPLR1_1_*` macros cover advanced PCIe and CCIX capabilities for port/function 1, including multicast, L1 PM sub-states, Downstream Port Containment, Root Port PIO error logging, ESM/CCIX data-rate capabilities, Data Link Feature exchange, 16 GT/s and 32 GT/s link capability/status fields, per-lane equalization, and per-lane margining.
- `BIFPLR2_1_*` macros start the next PCIe bridge/function configuration block, covering standard PCI config header fields, bridge bus/window registers, PCI/PCIe capability structures, MSI and SSID capabilities, Virtual Channel capability registers, device serial number, Advanced Error Reporting, root error reporting, TLP/header logs, secondary PCIe enhanced capability, and initial lane error status.

## Important Macro Families

The first lines continue `BIFPLR1_1_PCIE_MC_CAP` from the previous chunk, then define multicast control/address/receive/block/overlay BAR fields:

- `BIFPLR1_1_PCIE_MC_CNTL` provides `MC_NUM_GROUP` and `MC_ENABLE`.
- `BIFPLR1_1_PCIE_MC_ADDR0/ADDR1` define multicast index and base address fields.
- `BIFPLR1_1_PCIE_MC_RCV*`, `MC_BLOCK_ALL*`, and `MC_BLOCK_UNTRANSLATED_*` expose 32-bit bitmaps for multicast receive/block behavior.
- `BIFPLR1_1_PCIE_MC_OVERLAY_BAR*` splits overlay size and base address pieces.

Power-management and containment definitions follow:

- `BIFPLR1_1_PCIE_L1_PM_SUB_CAP_LIST`, `PCIE_L1_PM_SUB_CAP`, `PCIE_L1_PM_SUB_CNTL`, and `PCIE_L1_PM_SUB_CNTL2` map PCIe L1.1/L1.2 support, enable bits, common-mode restore timing, LTR threshold, and T_POWER_ON encoding.
- `BIFPLR1_1_PCIE_DPC_*` maps Downstream Port Containment enhanced capability, capability bits, control bits, trigger status/reason, interrupt status, busy status, and error source ID.
- `BIFPLR1_1_PCIE_RP_PIO_*` maps root-port PIO status, masks, severity, system-error, exception, header logs, and prefix logs for config, I/O, and memory completion failures.

The ESM and high-speed link portion is large and mostly table-like:

- `BIFPLR1_1_PCIE_ESM_*` defines enhanced speed mode capability headers, status/control bits, and capability bitmap registers. `ESM_CAP_4` through `ESM_CAP_7` enumerate individual supported rates from 16.0 GT/s through 28.0 GT/s at 0.1 GT/s increments.
- `BIFPLR1_1_PCIE_DLF_*` and `DATA_LINK_FEATURE_*` define data-link feature capability/status and exchange enable/valid bits.
- `BIFPLR1_1_PCIE_PHY_16GT_*`, `LINK_STATUS_16GT`, parity mismatch status, and `LANE_0` through `LANE_15_EQUALIZATION_CNTL_16GT` define Gen4/16 GT/s equalization state and per-lane downstream/upstream presets.
- `BIFPLR1_1_PCIE_MARGINING_*` defines margining capability/status plus lane-specific control/status pairs for lanes 0-15. Each lane control/status pair uses receiver number, margin type, usage model, and payload fields.
- `BIFPLR1_1_PCIE_CCIX_*` maps CCIX capability headers, ESM required/optional capability, ESM status/control, transport capability/control, and 20 GT/s and 25 GT/s per-lane equalization preset fields for lanes 0-15.
- `BIFPLR1_1_LINK_CAP_32GT`, `LINK_CNTL_32GT`, and `LINK_STATUS_32GT` define 32 GT/s equalization bypass/no-equalization support, modified training-sequence modes, selected usage mode, enhanced link behavior status, transmitter precoding status/request, and 32 GT/s equalization completion/phase bits.

The chunk then opens `// addressBlock: nbio_pcie1_bifplr2_cfgdecp` and starts `BIFPLR2_1_*`:

- Standard PCI config header fields: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`.
- Bridge layout/window fields: `SUB_BUS_NUMBER_LATENCY`, `IO_BASE_LIMIT`, `SECONDARY_STATUS`, `MEM_BASE_LIMIT`, `PREF_BASE_LIMIT`, `PREF_BASE_UPPER`, `PREF_LIMIT_UPPER`, `IO_BASE_LIMIT_HI`, `CAP_PTR`, `ROM_BASE_ADDR`, `INTERRUPT_LINE`, `INTERRUPT_PIN`, and `EXT_BRIDGE_CNTL`.
- PCI/PMI/PCIe capability fields: `PMI_CAP*`, `PCIE_CAP*`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, slot/root capability-control-status registers, `DEVICE_CAP2`, `DEVICE_CNTL2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- MSI and ID capabilities: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, MSI address/data registers, `SSID_CAP_LIST`, `SSID_CAP`, `MSI_MAP_CAP_LIST`, and `MSI_MAP_CAP`.
- Vendor-specific and Virtual Channel capabilities: `PCIE_VENDOR_SPECIFIC_*`, `PCIE_VC_ENH_CAP_LIST`, port VC capability/control/status, and VC0/VC1 resource capability/control/status registers.
- AER and logging registers: `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, `PCIE_UNCORR_ERR_SEVERITY`, `PCIE_CORR_ERR_STATUS`, `PCIE_CORR_ERR_MASK`, `PCIE_ADV_ERR_CAP_CNTL`, `PCIE_HDR_LOG0-3`, `PCIE_ROOT_ERR_CMD`, `PCIE_ROOT_ERR_STATUS`, `PCIE_ERR_SRC_ID`, and `PCIE_TLP_PREFIX_LOG0-3`.
- Secondary PCIe capability entry: `PCIE_SECONDARY_ENH_CAP_LIST`, `PCIE_LINK_CNTL3`, and the chunk-ending `PCIE_LANE_ERROR_STATUS` comment; the actual `LANE_ERROR_STATUS_BITS` field starts in the next chunk.

## Control Flow and State

There is no local control flow. The only "flow" represented by this file is the ordering of hardware register definitions as generated from the NBIO register database. Capability-list registers expose fields such as `CAP_ID`, `CAP_VER`, and `NEXT_PTR`, but the header itself does not walk those lists.

State is entirely in hardware registers. The macros describe:

- Read-only or status state such as link speed/width, link training, equalization phase success, DPC trigger status, PME status, AER status, TLP/header logs, and ESM calibration completion.
- Writable control state such as command enables, L1 PM substate enables, DPC interrupt/trigger controls, link retrain/disable controls, MSI enable/data fields, AER mask/severity bits, ECRC enable bits, CCIX/ESM enable/calibration controls, 32 GT/s control bits, and margining/equalization controls.
- Hardware-persistent-until-cleared status bits, especially PCI status, slot status, DPC status, AER correctable/uncorrectable status, root error status, and log registers. The clear semantics are not encoded here; callers must follow the PCIe/NBIO register specification and the driver access patterns for write-one-to-clear or sticky behavior.

## Dependencies and Integration Points

This header depends on consumers selecting the correct ASIC-generation header set. It is meaningful only together with the matching NBIO 7.7.0 register offset/header files, especially the corresponding `nbio_7_7_0_offset.h` and other AMDGPU `asic_reg/nbio` generated headers.

Integration points are preprocessor-level:

- AMDGPU NBIO/PCIe code includes these masks when reading or updating NBIO PCIe registers.
- The macro naming pattern is part of the generated register contract: `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`.
- Repeated lane macros allow callers to address lane-specific controls using explicit names rather than generated loops. This is important for debug dumps, equalization tuning, margining, and bring-up code where lane numbers must match hardware documentation exactly.
- The `BIFPLR1_1` to `BIFPLR2_1` boundary is significant: it switches to a new PCIe logical register block. A consumer must not combine a `BIFPLR1_1` mask with a `BIFPLR2_1` register offset just because the field names look similar.

## Risks and Maintenance Notes

- The file is generated register ABI data. Hand edits are risky because a single wrong shift or mask changes hardware programming behavior and can be difficult to diagnose from software symptoms.
- Many fields are narrow, adjacent, and repeated. Copy/paste drift is a real hazard in lane-specific macros, especially for `LANE_0` through `LANE_15` equalization and margining definitions.
- Similar field names recur across standard PCIe capability structures, BIFPLR instances, and NBIO generations. The same-looking field can have a different register instance, field width, or supported semantics on another ASIC generation.
- Some control bits have side effects outside normal memory state, including link retraining, compliance entry, ESM calibration, DPC software trigger, MSI enable, AER reporting, and CCIX TLP format selection. Callers should modify them only with the documented sequencing for the device and link state.
- Status/log macros expose error and training diagnostics but not clear behavior. Incorrect clear/write masks can lose diagnostic evidence or leave interrupts asserted.
- Capability-list `NEXT_PTR` and VSEC length fields must remain aligned with the matching offset layout; mismatches break PCIe extended capability traversal and tooling that decodes config space.
- The chunk boundary leaves `BIFPLR2_1_PCIE_LANE_ERROR_STATUS` without its field macros until the following chunk, so the final per-file merge should reconcile that continuation rather than treating it as an empty register.

## Test Signals

This header has no standalone unit-test surface. Useful validation signals are compile-time and hardware-oriented:

- Build coverage for AMDGPU targets that include NBIO 7.7.0 headers catches missing or renamed macros.
- Static searches for macro consumers can verify that callers use `BIFPLR1_1` and `BIFPLR2_1` masks with matching offsets.
- Hardware bring-up or CI on affected ASICs should validate PCIe link enumeration, negotiated speed/width, L1 substate behavior, MSI delivery, AER/DPC reporting, lane equalization status, margining status, and CCIX/ESM capability reporting.
- Register dump tools should decode fields using these masks without overlapping bits or losing high-bit fields such as `NEXT_PTR`, AER root interrupt message numbers, and 32-bit log registers.
- Cross-generation diffs against adjacent NBIO headers are useful, but only as review aids. The acceptance test is consistency with the NBIO 7.7.0 register source data and live hardware behavior.
