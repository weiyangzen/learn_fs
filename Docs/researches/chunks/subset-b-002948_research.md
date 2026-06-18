# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 108247-110670

## Scope

This chunk is a generated AMD NBIO 2.3 shift/mask header segment for SR-IOV virtual-function PCI configuration-space fields. It starts at the final mask definitions for `BIF_CFG_DEV0_EPF0_VF13_1_MSIX_PBA`, covers the rest of VF13, complete VF14, complete VF15, complete VF16, and ends at the `BIF_CFG_DEV0_EPF0_VF17_1_BASE_ADDR_1__BASE_ADDR__SHIFT` definition. The matching mask for `VF17_1_BASE_ADDR_1` is on the following line outside this chunk.

The file content in this range is C preprocessor data only. It defines no functions, structs, variables, storage, locking, allocation, branching, loops, or direct MMIO operations. Its public interface is the generated naming convention:

- `<REGISTER>__<FIELD>__SHIFT` for a field bit offset.
- `<REGISTER>__<FIELD>_MASK` for the bit mask used to isolate or compose that field.

## Purpose

`nbio_2_3_sh_mask.h` supplies the bitfield side of the NBIO 2.3 hardware ABI. AMDGPU and related platform code include it with the companion `nbio_2_3_offset.h` address header and `nbio_2_3_default.h` reset/default header. Runtime code then uses register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and `WREG32_FIELD15` to build or decode register values without hard-coding bit numbers.

This chunk's specific role is to describe PCI and PCIe configuration fields for NBIO SR-IOV virtual functions. The complete VF14, VF15, and VF16 maps expose standard PCI identity/header fields, BARs, interrupt fields, PCIe device/link capability and control fields, MSI/MSI-X state, vendor-specific extended capability fields, Advanced Error Reporting, header/TLP-prefix logs, ATS, and ARI. The VF13 and VF17 coverage is partial because the assigned line range cuts across repeated VF blocks.

## Important Macro Families

### VF13 Tail

The first two lines complete `BIF_CFG_DEV0_EPF0_VF13_1_MSIX_PBA` by defining `MSIX_PBA_BIR_MASK` and `MSIX_PBA_OFFSET_MASK`. The preceding `VF13_1_MSIX_PBA` comment and shift definitions are in the previous chunk.

The rest of VF13 in this range covers:

- `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, `PCIE_VENDOR_SPECIFIC1`, and `PCIE_VENDOR_SPECIFIC2`, which describe a vendor-specific enhanced capability header and scratch/data fields.
- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, AER uncorrectable status/mask/severity, correctable status/mask, AER capability/control, and the four `PCIE_HDR_LOG*` registers.
- Four `PCIE_TLP_PREFIX_LOG*` registers for captured TLP prefix data.
- `PCIE_ATS_ENH_CAP_LIST`, `PCIE_ATS_CAP`, and `PCIE_ATS_CNTL`, including invalidate queue depth, page-aligned request support, global invalidate support, STU, and ATC enable.
- `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL`, including MFVC/ACS function group capability and enable bits plus next-function/function-group fields.

### Complete VF14, VF15, and VF16 Maps

The chunk contains full repeated address blocks for:

- `nbio_nbif0_bif_cfg_dev0_epf0_vf14_bifcfgdecp`
- `nbio_nbif0_bif_cfg_dev0_epf0_vf15_bifcfgdecp`
- `nbio_nbif0_bif_cfg_dev0_epf0_vf16_bifcfgdecp`

Each full VF block begins with `VENDOR_ID` and `DEVICE_ID`, then defines the standard PCI configuration header fields: command, status, revision/class fields, cache-line size, latency timer, header type, BIST, six base address registers, CardBus CIS pointer, subsystem/vendor adapter ID, ROM base address, capability pointer, interrupt line/pin, and min/max latency.

For `COMMAND`, the repeated fields include IO and memory access enables, bus-master enable, special-cycle and memory-write-invalidate enables, palette snoop, parity-error response, SERR enable, fast back-to-back enable, and interrupt disable. For `STATUS`, the maps include readiness, interrupt status, capability-list presence, 66 MHz and fast-back capability flags, data parity error, DEVSEL timing, target/master abort status, system error, and parity error detected.

The PCIe capability families include:

- `PCIE_CAP_LIST` and `PCIE_CAP` fields for capability ID, next pointer, PCIe capability version, device type, slot implementation, and interrupt message number.
- `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` fields for payload sizing, phantom functions, extended tags, endpoint L0s/L1 latency, attention/power indicators, role-based error reporting, captured slot power, FLR capability/control, correctable/nonfatal/fatal/unsupported-request reporting, relaxed ordering, max payload size, extended tag enable, phantom function enable, AUX power PM enable, no-snoop enable, max read request size, bridge configuration retry, and transaction pending/AUX power status.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` fields for supported/current speed and width, ASPM/L0s/L1 behavior, clock power management, surprise-down reporting, data-link active reporting, port number, retraining, common clock, extended sync, hardware autonomous width disable, link bandwidth management/status, and autonomous bandwidth status/interrupt controls.
- `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` for completion timeout ranges and controls, ARI and atomic-operation support, 32/64/128-bit CAS capability, no-RO-enabled PR-PR passing, LTR support/enable, TPH completion support, OBFF, emergency power reduction, ID-based ordering, ten-bit tags, end-to-end TLP prefix behavior, target link speed, compliance/deemphasis controls, equalization state, selected deemphasis, transmit margin, and downstream component presence/DRS bits.

The interrupt capability families include `MSI_CAP_LIST`, `MSI_MSG_CNTL`, `MSI_MSG_ADDR_LO`, `MSI_MSG_ADDR_HI`, `MSI_MSG_DATA`, `MSI_MASK`, `MSI_MSG_DATA_64`, `MSI_MASK_64`, `MSI_PENDING`, `MSI_PENDING_64`, `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`. These describe vector enable/count state, 64-bit MSI layout, per-vector masking capability, message address/data, mask and pending bitmaps, MSI-X table size, function mask, MSI-X enable, table BAR indicator, table offset, PBA BAR indicator, and PBA offset.

The diagnostics and extended capability families include vendor-specific headers, AER uncorrectable/correctable status and masks, AER severity, AER capability/control, four header-log dwords, four TLP-prefix log dwords, ATS capability/control, and ARI capability/control.

### VF17 Beginning

The final section begins `nbio_nbif0_bif_cfg_dev0_epf0_vf17_bifcfgdecp`. This chunk covers VF17 `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, revision/class/header fields, cache line, latency, `HEADER`, `BIST`, and only the `BASE_ADDR_1__BASE_ADDR__SHIFT` line. VF17's `BASE_ADDR_1` mask and the rest of the VF17 PCI/PCIe map continue in the next chunk.

## Control Flow

There is no executable control flow in this header. The practical flow is external and compile-time driven:

1. AMDGPU NBIO 2.3, virtualization, or platform power-management code includes the generated NBIO offset, shift/mask, and default headers.
2. The code selects a concrete VF register symbol, such as a `BIF_CFG_DEV0_EPF0_VF16_1_*` field and the matching `cfgBIF_CFG_DEV0_EPF0_VF16_1_*` offset.
3. Register helper macros combine masks and shifts to compose writes or extract read fields.
4. PCIe/NBIO hardware, firmware, a PF driver, a VF guest, or a hypervisor observes the resulting register state according to the access path and permissions.

Because this is PCI configuration-space material, the actual access path may be PCI config access, NBIO/SMN indexed register access, PF-mediated SR-IOV handling, firmware mediation, or hypervisor emulation. Those access paths live outside this generated header.

## State and Persistence Behavior

The header has no local state. It names hardware-visible state in NBIO PCI configuration registers for virtual functions. That state can persist until an explicit write, PCI reset, function-level reset, VF teardown, GPU reset, power transition, firmware action, or hypervisor action changes it.

Important represented state includes:

- Per-VF PCI identity, class code, header type, BIST, BAR, ROM BAR, subsystem ID, capability pointer, and interrupt presentation.
- Per-VF command/status state controlling memory access, bus mastering, interrupt disable, parity/SERR policy, and status/error latches.
- PCIe device/link capability, control, and status state for payload/read-request sizing, relaxed ordering, no-snoop, FLR, completion timeouts, ASPM, link retraining, current speed/width, equalization, LTR, OBFF, emergency power reduction, atomic operations, ID-based ordering, ten-bit tags, and TLP prefix behavior.
- MSI and MSI-X programming state, including address/data fields, vector enable/count, mask and pending bitmaps, MSI-X table location, PBA location, and function-level masking.
- AER state for uncorrectable/correctable errors, mask/severity policy, first-error pointer, ECRC generation/checking, multi-header logging, header log capture, and TLP prefix logs.
- ATS and ARI state used for address translation caching and alternative routing ID behavior in virtualized PCIe topologies.

Many PCIe fields have side effects or special write semantics. Examples include status latches, AER clear/status bits, FLR initiation, link retrain controls, interrupt pending/mask fields, and capability-control enables. The macros only describe bit positions and masks; ordering, polling, write-one-to-clear rules, reset timing, and access permissions must come from the owning driver code and the hardware specification.

## Dependencies and Integration Points

The direct dependencies are the generated NBIO 2.3 register headers:

- `nbio_2_3_offset.h` supplies matching `cfgBIF_CFG_DEV0_EPF0_VF*_1_*` addresses. For example, this source tree maps `cfgBIF_CFG_DEV0_EPF0_VF13_1_VENDOR_ID` at `0xfffe1030d000`, `cfgBIF_CFG_DEV0_EPF0_VF16_1_PCIE_ATS_CAP` at `0xfffe103102b4`, and `cfgBIF_CFG_DEV0_EPF0_VF17_1_BASE_ADDR_1` at `0xfffe10311010`.
- `nbio_2_3_default.h` supplies reset/default values for the same config-space families, including VF13 through VF17 defaults adjacent to this chunk's register names.
- AMDGPU register-helper macros consume the `__SHIFT` and `_MASK` names through field composition and extraction helpers.

Observed source-tree consumers of `nbio_2_3_sh_mask.h` include:

- `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, the main NBIO 2.3 implementation using the matching offset, mask, and default headers.
- `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, virtualization-oriented AMDGPU code that includes this NBIO 2.3 mask header.
- `drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c` and `drivers/gpu/drm/amd/pm/swsmu/smu11/sienna_cichlid_ppt.c`, which include the same generated NBIO headers for platform power-management behavior.

The offset-header chunk for the same VF address blocks supplies full physical-looking config addresses on 0x1000 VF boundaries. This shift/mask chunk supplies bit-level interpretation for those offsets; it does not define which actor may legally access each field.

## Risks

- Bitfield drift is high impact. A wrong mask or shift can alter unrelated PCIe configuration bits, break VF enumeration, corrupt BAR presentation, disable memory or bus-master access, disrupt interrupts, or hide protocol errors.
- The VF maps are highly repetitive. VF14, VF15, and VF16 are structurally near-identical, while VF13 and VF17 are partial at chunk boundaries. Copying a macro from the wrong VF can compile cleanly but target the wrong virtual function.
- Chunk-boundary incompleteness matters. This range starts after `VF13_1_MSIX_PBA` shifts and ends before the `VF17_1_BASE_ADDR_1` mask. The final per-file report should reconcile neighboring chunks before making complete claims about VF13 or VF17.
- PCIe status, AER, FLR, MSI/MSI-X, and link-control fields can have side effects. Treating every mask as an ordinary read/write storage bit can clear evidence, trigger a function reset, retrain a link, mask interrupts, or change guest-visible capability state.
- MSI layout is mode-dependent. Normal and `_64` message-data/mask/pending definitions reflect PCI MSI capability layout variants and aliases, not necessarily independent live storage in every configuration.
- ATS, ARI, atomic operations, LTR, OBFF, ten-bit tags, ID-based ordering, and TLP-prefix controls affect host interconnect behavior. Enabling unsupported combinations in an SR-IOV environment can produce PCIe errors or isolation problems.
- AER header and TLP-prefix logs are diagnostic evidence. Incorrect decoding or clearing can obscure the first failing TLP and make hardware or platform failures harder to triage.
- Access policy is virtualization-sensitive. PF, VF guest, hypervisor, and firmware may see the same generated names but have different access rights and side-effect expectations.

## Test and Validation Signals

Useful validation is mostly compile, generated-header consistency, SR-IOV enumeration, PCIe behavior, and hardware diagnostic coverage:

- Build AMDGPU paths that include `nbio_2_3_sh_mask.h`, especially NBIO 2.3, MXGPU/SR-IOV, and SMU11 platform code.
- Compare this shift/mask header against `nbio_2_3_offset.h` and `nbio_2_3_default.h` for VF13 through VF17 to catch missing registers, mask-width drift, and repeated-family naming errors.
- SR-IOV VF enumeration should expose expected PCI IDs, class/header fields, BAR sizing, capability pointer chains, PCIe capability values, MSI/MSI-X capabilities, AER structures, ATS, and ARI for VF14 through VF16, with VF13 and VF17 reconciled through adjacent chunks.
- VF reset and teardown tests should verify FLR initiation, command/status defaults, BAR reset behavior, and return to expected PCI config state.
- MSI/MSI-X interrupt tests should validate message address/data programming, vector enable counts, mask/pending behavior, table/PBA decoding, and function-mask behavior.
- PCIe link and power-management tests should cover payload/read-request sizing, relaxed ordering/no-snoop policy, ASPM/LTR/OBFF controls, link retraining, bandwidth-management status, and equalization status.
- AER error-injection or diagnostic tests should validate uncorrectable/correctable status, masks, severity, first-error pointer, header log capture, TLP prefix log capture, and clear behavior.
- Static checks should verify that VF14, VF15, and VF16 remain mechanically consistent with neighboring VF maps except for intentional VF-number and address differences.

## Unresolved Cross-Chunk References

The first two lines belong to `BIF_CFG_DEV0_EPF0_VF13_1_MSIX_PBA`, whose comment and shift definitions are in the previous chunk. The range then completes the late VF13 capability blocks and contains full VF14, VF15, and VF16 maps. The final line is only `BIF_CFG_DEV0_EPF0_VF17_1_BASE_ADDR_1__BASE_ADDR__SHIFT`; the corresponding mask and all subsequent VF17 fields are in the next chunk. The merge/reconciliation lane should stitch these boundaries before producing the final source-file report.
