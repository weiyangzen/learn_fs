# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 81347-82050

## Scope

This chunk is the final 704-line segment of the generated AMDGPU NBIO 4.3.0 shift/mask header. It contains preprocessor-only bitfield definitions for the tail of the `BIF_CFG_DEV0_EPF3_1_*` PCIe configuration-space template and then closes the header guard. There are no C functions, structs, enums, runtime variables, locks, allocations, or executable statements in this range.

The chunk starts at the mask definitions for `BIF_CFG_DEV0_EPF3_1_LINK_CNTL`, then covers link status, PCIe Device/Link Capability 2, MSI and MSI-X, vendor-specific extended capability, Advanced Error Reporting, resizable/enhanced BAR capability registers, power budgeting, Dynamic Power Allocation, ACS, PASID, ARI, Readiness Time Reporting, one standalone `PCIE_LC_RXRECOVER_RXSTANDBY_CNTL` mask, and the final `#endif`. The corresponding offsets are expected in the matching NBIO 4.3.0 offset header; this file only defines field positions and masks.

## Purpose

`nbio_4_3_0_sh_mask.h` is generated hardware metadata for AMDGPU's NBIO 4.3.0 block. Its public interface is a macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's starting bit.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask used to isolate, preserve, clear, or compose that field.

This chunk describes PCI/PCIe configuration and extended-capability fields for device 0, endpoint function 3, instance/index `1`. The fields model hardware-visible PCIe state: link negotiation, extended PCIe capabilities, interrupt programming, error reporting, BAR sizing/control, power management capability data, access-control/isolation features, PASID/ARI routing, and reset/readiness timing. Driver code can combine these masks with register offsets and AMDGPU register helpers to decode or update NBIO config-space values without hard-coded bit numbers.

Although this source tree is under a `ceph-client` mirror, this header is AMDGPU hardware metadata and has no direct distributed-filesystem logic.

## Important Macro Families

The initial lines complete `BIF_CFG_DEV0_EPF3_1_LINK_CNTL` masks:

- `PM_CONTROL`, `LINK_DIS`, `RETRAIN_LINK`, `COMMON_CLOCK_CFG`, `EXTENDED_SYNC`, and `CLOCK_POWER_MANAGEMENT_EN` map ASPM/link-management controls.
- `HW_AUTONOMOUS_WIDTH_DISABLE`, `LINK_BW_MANAGEMENT_INT_EN`, `LINK_AUTONOMOUS_BW_INT_EN`, and `DRS_SIGNALING_CONTROL` affect autonomous width changes, bandwidth notifications, and dynamic speed/DRS signaling.

PCIe link and device extension fields follow:

- `LINK_STATUS` exposes negotiated link speed/width, link training, slot clock configuration, data-link-layer active state, and bandwidth-management/autonomous-bandwidth status bits.
- `DEVICE_CAP2` advertises completion-timeout ranges, ARI forwarding, AtomicOp routing and completion support, CAS128 completion support, no-relaxed-ordering P2P passing, LTR, TPH completer support, local node/system cache-line size, ten-bit tag support, OBFF support, end-to-end TLP prefix support, emergency power reduction, and FRS support.
- `DEVICE_CNTL2` controls completion timeout, ARI forwarding, AtomicOp requests and egress blocking, ID-based ordering for requests/completions, LTR, emergency power reduction request, ten-bit tag requester enable, OBFF, and end-to-end TLP prefix blocking.
- `DEVICE_STATUS2` is marked fully reserved by a single 16-bit reserved mask.
- `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` describe supported link speeds, crosslink/skip-ordered-set capabilities, retimer presence detect support, target link speed, compliance/test controls, transmit margin, de-emphasis, equalization phases for 8 GT/s, crosslink resolution, downstream component presence, and DRS message receipt.

Interrupt capability definitions cover both MSI and MSI-X:

- `MSI_CAP_LIST` and `MSIX_CAP_LIST` define conventional capability ID and next-pointer bytes.
- `MSI_MSG_CNTL` defines MSI enable, multiple-message capability and enable fields, 64-bit address support, per-vector masking support, and extended message data support/enable bits.
- `MSI_MSG_ADDR_LO`, `MSI_MSG_ADDR_HI`, `MSI_MSG_DATA`, `MSI_EXT_MSG_DATA`, `MSI_MASK`, `MSI_PENDING`, and their 64-bit layout variants define MSI target address, message data, mask, and pending fields.
- `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA` define MSI-X table size, function mask, enable bit, table BAR indicator and offset, and PBA BAR indicator and offset.

Vendor-specific and Advanced Error Reporting definitions include:

- `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, `PCIE_VENDOR_SPECIFIC1`, and `PCIE_VENDOR_SPECIFIC2` define VSEC metadata and two 32-bit scratch payload registers.
- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST` defines AER extended-capability ID, version, and next pointer.
- `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY` cover DLP, surprise down, poisoned TLP, flow-control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress blocked, TLP prefix blocked, and poisoned-TLP egress blocked classes.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK` cover receiver error, bad TLP, bad DLLP, replay number rollover, replay timer timeout, advisory non-fatal, corrected internal error, and header log overflow.
- `PCIE_ADV_ERR_CAP_CNTL` defines first-error pointer, ECRC generation/check capability and enable bits, multi-header received capability/enable bits, TLP prefix log presence, and completion-timeout log capability.
- `PCIE_HDR_LOG[0-3]` and `PCIE_TLP_PREFIX_LOG[0-3]` provide full 32-bit masks for captured diagnostic TLP header and prefix log words.

BAR, power, isolation, addressing, and readiness capability families close the PCIe template:

- `PCIE_BAR_ENH_CAP_LIST` and `PCIE_BAR[1-6]_{CAP,CNTL}` define enhanced BAR capability metadata, supported BAR-size bitmaps, BAR index, total number, selected size, and upper supported-size bits for BAR1 through BAR6.
- `PCIE_PWR_BUDGET_ENH_CAP_LIST`, `PCIE_PWR_BUDGET_DATA_SELECT`, `PCIE_PWR_BUDGET_DATA`, and `PCIE_PWR_BUDGET_CAP` define power budgeting table selection, base power, scale, PM state/substate, type, power rail, and whether the budget is system allocated.
- `PCIE_DPA_ENH_CAP_LIST`, `PCIE_DPA_CAP`, `PCIE_DPA_LATENCY_INDICATOR`, `PCIE_DPA_STATUS`, `PCIE_DPA_CNTL`, and `PCIE_DPA_SUBSTATE_PWR_ALLOC_0` through `_7` define Dynamic Power Allocation capability metadata, substate count, transition latency encoding, power allocation scale, current/enabled substate status, control, and per-substate power allocation bytes.
- `PCIE_ACS_ENH_CAP_LIST`, `PCIE_ACS_CAP`, and `PCIE_ACS_CNTL` define Access Control Services support and controls for source validation, translation blocking, P2P request/completion redirect, upstream forwarding, P2P egress control, direct translated P2P, enhanced capability, egress vector size, I/O request blocking, downstream/upstream memory target access controls, and unclaimed request redirect.
- `PCIE_PASID_ENH_CAP_LIST`, `PCIE_PASID_CAP`, and `PCIE_PASID_CNTL` define PASID capability metadata, execute-permission support, privileged-mode support, maximum PASID width, and enable bits.
- `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL` define Alternative Routing-ID Interpretation capability metadata, MFVC/ACS function-group capability bits, next function number, function-group enables, and selected ARI function group.
- `PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2` define Readiness Time Reporting metadata and reset, data-link-up, FLR, D3hot-to-D0, and validity fields.
- `PCIE_LC_RXRECOVER_RXSTANDBY_CNTL__LC_RX_L0S_STANDBY_EN_MASK` is a standalone link-control mask for RX recover/RX standby L0s behavior.

## APIs, Types, And Functions

There are no callable APIs or declared C types in this chunk. The only interface is the generated macro set. Consumers are expected to combine these constants with:

- companion register/config offsets from the NBIO 4.3.0 offset header,
- generated reset/default metadata where present,
- AMDGPU/SOC15 register access macros,
- generic field helpers such as `REG_GET_FIELD` and `REG_SET_FIELD`,
- PCI/NBIO config-space access paths that understand the relevant address space and access width.

The constants are simple integer literals, mostly with an `L` suffix. They do not carry access permissions, reset values, volatility, field width type, write-one-to-clear rules, polling requirements, or side-effect semantics. Those rules come from hardware documentation and the driver call sites.

## Control Flow

This header has no local control flow. Runtime control flow is external and typically looks like:

1. AMDGPU/NBIO, PCIe, SR-IOV, interrupt, reset, or diagnostic code selects an NBIO register or PCI config-space offset.
2. Code reads the raw register/config value through the appropriate MMIO or config access path.
3. The value is decoded with this file's shift and mask constants, often through register helper macros.
4. For writable control fields, code composes a new raw value by preserving unrelated bits, clearing the target mask, and inserting a shifted field value.
5. Hardware observes the write, or the driver uses the decoded status/capability value to decide enumeration, interrupt, link, power, AER, reset, or virtualization policy.

Likely flows include link training and retrain handling, PCIe capability enumeration, MSI/MSI-X setup, AER status reporting and masking, BAR sizing/resource control, power budgeting and DPA reporting, ACS/PASID/ARI virtualization setup, and FLR/reset readiness timing.

## State And Persistence Behavior

The header itself stores no state. It names bits in hardware-backed PCIe configuration and NBIO registers. Persistence depends on the GPU/NBIO reset domain, PCI reset, function-level reset, power management transitions, firmware initialization, driver save/restore, and host or hypervisor configuration.

The represented state falls into several categories:

- Static or mostly static capability state, such as supported link speeds, MSI/MSI-X capability data, AER/VSEC/enhanced-capability metadata, supported BAR sizes, power budget descriptors, DPA capabilities, ACS/PASID/ARI support, and RTR capability data.
- Host-programmed control state, such as link control, device control 2, MSI/MSI-X enable/mask/address/data, AER masks and severities, selected BAR sizes, DPA controls, ACS controls, PASID enablement, and ARI controls.
- Hardware-updated status state, such as link status/training/equalization bits, MSI pending bits, AER status and diagnostic logs, DPA substate status, and RTR validity/timing information.
- Side-effect trigger or policy bits, such as link disable/retrain, compliance entry, emergency power reduction request, interrupt enable/mask bits, and ACS/ARI/PASID routing controls.

Because this generated file only gives layouts, callers must enforce ordering and privilege rules. A mask that is harmless when used for readback can be dangerous when used for writes to status, interrupt, link-control, AER, or routing fields.

## Dependencies And Integration Points

This chunk depends on the rest of the generated AMDGPU NBIO register header set:

- `nbio_4_3_0_offset.h` supplies the matching `BIF_CFG_DEV0_EPF3_1_*` register/config offsets.
- Other NBIO 4.3.0 generated headers provide defaults or related register definitions when present.
- AMDGPU register helper macros consume the `__SHIFT` and `_MASK` names for field extraction and update.

Integration points include AMDGPU NBIO initialization, PCIe link-management code, PCI capability/configuration handling, SR-IOV PF/VF management, interrupt setup, AER/error collection paths, power-management policy, reset/FLR handling, and virtualization/isolation plumbing. The ACS, PASID, and ARI fields are especially relevant where GPU functions interact with IOMMU, VFIO, hypervisor, or SR-IOV flows.

The final `#endif` means this range also closes the whole `_nbio_4_3_0_SH_MASK_HEADER` include guard. Any edits here can affect successful inclusion of the entire generated header, not just the final PCIe capability template.

## Risks And Edge Cases

- Generated register drift can compile cleanly while decoding or programming the wrong hardware bit. High-risk fields include MSI/MSI-X enable/mask/address/data, AER status/mask/severity, link retrain/disable/compliance controls, ACS/PASID/ARI controls, BAR sizing controls, and DPA/power-budget selectors.
- This chunk starts mid-register after `LINK_CNTL` shifts and earlier masks were defined in the previous chunk. Merge/reconciliation must not treat the visible `LINK_CNTL` masks as a complete register description for this chunk alone.
- Many status fields may be sticky, hardware-updated, or write-one-to-clear. The masks do not say which. Misusing AER status/log masks can destroy diagnostic evidence or leave active faults uncleared.
- Link control and equalization fields influence PCIe liveness. Wrong target speed, compliance, retrain, or de-emphasis handling can cause link training failures or performance degradation.
- MSI/MSI-X fields affect interrupt delivery. Incorrect message address/data, table/PBA offsets, or mask bits can lead to lost, repeated, or misrouted interrupts.
- BAR capability/control fields affect host resource sizing and mapping. Incorrect masks can produce invalid apertures or resource conflicts.
- ACS/PASID/ARI controls affect isolation, routing, and address-space tagging. Misprogramming can break VF discovery, IOMMU integration, peer-to-peer routing, or security assumptions.
- RTR timing fields should only be trusted when their validity bit and capability chain are sane. Underestimating reset, DL-up, FLR, or D3hot-to-D0 timing can cause premature access after reset or power transition.
- The standalone `PCIE_LC_RXRECOVER_RXSTANDBY_CNTL` mask is outside the `BIF_CFG_DEV0_EPF3_1_*` naming family; consumers should verify its offset/address-space pairing rather than infer one from neighboring PCI config definitions.

## Test Signals

- Compile AMDGPU with NBIO 4.3.0 support enabled. Direct macro users should catch missing, renamed, or malformed definitions.
- Run PCI enumeration on affected AMD hardware and verify stable capability chains, link status, BAR sizing, MSI/MSI-X capability reporting, AER capability reporting, ACS/PASID/ARI capability reporting, and no malformed config-space reads.
- Exercise MSI and MSI-X interrupt setup, masking, unmasking, and pending behavior; watch for lost interrupts, unexpected interrupt storms, or incorrect table/PBA placement.
- Validate PCIe link behavior across boot, suspend/resume, retrain, speed changes, and error recovery. Expected signals include sane negotiated width/speed, successful equalization, and no unexpected link-down events.
- Inject or observe PCIe AER events where possible and confirm status, mask, severity, header log, and TLP prefix log decoding matches hardware behavior without clearing evidence unexpectedly.
- Exercise SR-IOV/VFIO/hypervisor paths that rely on ACS, PASID, and ARI; expected signals are correct function enumeration, preserved isolation policy, and correct IOMMU/PASID behavior.
- Test FLR and power-state transitions with RTR timing honored. Hardware should not be accessed before reported reset/DL-up/FLR/D3hot-to-D0 readiness windows have elapsed.
- Compare generated masks against the authoritative register database or adjacent NBIO generation headers before changing this file; mechanical consistency is a strong validation signal for generated register metadata.
