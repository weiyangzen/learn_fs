# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 27174-29592

## Scope

This chunk is a generated AMD NBIO 4.3.0 shift/mask header segment. It contains only C preprocessor constants; there are no functions, structs, enums, variables, branches, loops, allocations, locks, direct MMIO operations, or local persistence behavior.

The range starts inside `BIF_CFG_DEV0_EPF0_VF10_0_DEVICE_CAP2`, after that register's first capability-field shifts have already been defined by the previous chunk. It then completes the rest of the VF10 PCIe capability/control, MSI/MSI-X, vendor-specific, AER, ARI, and reset-time-reporting masks. The range fully covers the generated PCI configuration-space field layouts for `VF11` and `VF12`. It begins the `VF13` block and stops inside `BIF_CFG_DEV0_EPF0_VF13_0_PCIE_UNCORR_ERR_MASK`, so the remainder of VF13 AER mask/severity/log/ARI fields continues after this work item.

Although this source tree is under a `ceph-client` mirror, this file is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

`nbio_4_3_0_sh_mask.h` gives AMDGPU code symbolic bit layouts for NBIO 4.3.0 registers. Each field is exported as:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used to pack or extract a field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate or update a field.

This specific range describes PCI configuration-space fields for SR-IOV-style virtual functions under `BIF_CFG_DEV0_EPF0_VF<n>_0_*`. Runtime code pairs these macros with matching addresses from `nbio_4_3_0_offset.h`, then typically applies them through `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15_PREREG`, or related SOC15/NBIO helpers.

The assigned interval contains 2,139 `#define` entries across 272 register-name prefixes: 1,067 shift definitions and 1,072 mask definitions. The mask/shift imbalance is expected because the chunk begins and ends at artificial boundaries inside register definitions.

## Important Macro Families

The VF10 opening fragment completes PCIe 2.0+ and interrupt/error-reporting fields. It includes `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` fields for completion timeout, ARI forwarding, AtomicOp support/control, ID-based ordering, LTR, OBFF, 10-bit tags, TLP prefix support/blocking, supported link speeds, de-emphasis, equalization status, crosslink status, DRS, and downstream-component presence.

The VF10 interrupt portion defines MSI and MSI-X layouts: capability-list IDs and next pointers, MSI enable/multiple-message/64-bit/per-vector-mask/extended-data bits, MSI address/data/mask/pending dwords, MSI 64-bit aliases, MSI-X table size/function-mask/enable, table BIR/offset, and pending-bit-array BIR/offset.

The VF10 PCIe extended capability portion defines vendor-specific enhanced capability headers and scratch dwords, AER capability headers, uncorrectable and correctable error status/mask/severity bits, AER capability/control fields, header-log dwords, TLP-prefix-log dwords, ARI capability/control fields, and reset-time-reporting fields. High-risk AER bits include DLP, surprise down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, AtomicOp egress blocked, TLP prefix blocked, and poisoned TLP egress blocked.

The `VF11` and `VF12` blocks are complete generated PCI configuration-space layouts. Each block starts with identity and standard PCI header fields: vendor/device ID, command, status, revision/class codes, cache line, latency, header type, BIST, six BAR dwords, CardBus CIS pointer, subsystem IDs, ROM base and validation fields, capability pointer, legacy interrupt line/pin, and min/max latency.

The full VF11/VF12 PCIe capability groups define device capability/control/status and link capability/control/status fields. These cover max payload and read request sizes, FLR capability/control, extended tags, relaxed ordering, no-snoop, error-reporting enables/status bits, ASPM capability/control, link speed/width, link training, slot clock, data-link active, bandwidth-management interrupts, clock power management, retrain/link disable, common clock configuration, and DRS signaling.

VF11/VF12 then repeat the `DEVICE_CAP2`/`CNTL2` and `LINK_CAP2`/`CNTL2`/`STATUS2` families described above, followed by the same MSI/MSI-X capability and AER/ARI/RTR extended capability groups used by VF10.

The VF13 block is complete only through early AER. It includes identity/header, BAR, PCIe capability, device/link capability/control/status, PCIe 2.0+ capability/control/status, MSI/MSI-X, vendor-specific enhanced capability, AER enhanced capability, and uncorrectable error status. The range ends after the first three shift definitions of `VF13_0_PCIE_UNCORR_ERR_MASK`; the matching masks and later VF13 AER severity/log/ARI/RTR fields are outside this chunk.

## Control Flow

There is no executable control flow in this header. The runtime pattern is external:

1. NBIO 4.3.0 AMDGPU code includes the generated offset and shift/mask headers for this ASIC generation.
2. The caller chooses a VF-specific register address from `nbio_4_3_0_offset.h`.
3. It reads or composes a 16-bit or 32-bit PCI configuration-space value through the NBIO/SOC15 register-access path.
4. It uses this header's `__SHIFT` and `_MASK` constants, directly or through field helper macros, to inspect or modify individual PCIe capability, interrupt, or error-reporting fields.

The `VF10`, `VF11`, `VF12`, and `VF13` suffixes are part of the hardware address namespace. Reusing a mask with the wrong VF register can still compile, but it represents the wrong virtual function's PCI configuration state.

## State And Persistence Behavior

This header stores no software state and persists nothing to disk. It describes hardware-backed PCI configuration and NBIO state owned by the GPU, platform PCIe logic, firmware, the host kernel, and SR-IOV/hypervisor policy.

The represented state includes VF identity and class presentation, PCI command/status, BARs and ROM decode state, capability-list linkage, PCIe capability and control fields, link-training and link-status bits, completion-timeout and ordering controls, LTR/OBFF/AtomicOp/ARI controls, MSI and MSI-X programming state, AER status/mask/severity/log state, TLP prefix logs, vendor-specific scratch registers, ARI function-group controls, and reset-time-reporting values.

Some fields are software-programmed controls, some are hardware-updated status, and some may be sticky diagnostics with clear semantics defined by PCIe/AER behavior or hardware documentation. The generated masks do not encode reset defaults, access widths, write-one-to-clear behavior, polling timeouts, ownership rules, or ordering requirements.

## Dependencies And Integration Points

The primary dependency is the AMD generated NBIO 4.3.0 register database. This file must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h`, where the corresponding `cfgBIF_CFG_DEV0_EPF0_VF<n>_0_*` addresses are defined.

Direct in-tree include users of the NBIO 4.3.0 offset/mask pair include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_7_ppt.c`

Display DCN32/DCN321 resource files include the matching NBIO 4.3.0 offset header, while field-level NBIO programming in AMDGPU and SMU code uses the shift/mask header. The most relevant integration surfaces for this chunk are SR-IOV VF enumeration/configuration, VF BAR and ROM presentation, VF PCIe capability reporting, VF MSI/MSI-X programming, VF AER reporting, ARI support, link-capability reporting, and function reset/power-transition timing metadata.

## Risks And Edge Cases

- The chunk boundaries are artificial. The range starts inside VF10 `DEVICE_CAP2` and ends inside VF13 `PCIE_UNCORR_ERR_MASK`; adjacent chunks are required for full VF10 and VF13 coverage.
- These macros are untyped constants. A stale or mismatched mask can compile while reading or writing the wrong hardware bit.
- The repeated VF blocks are mechanically similar. Off-by-one suffix mistakes around VF10/VF11/VF12/VF13 can affect another virtual function's PCI config, interrupt, or error-reporting state.
- PCI configuration registers frequently pack multiple fields into 8-, 16-, or 32-bit values. Using the wrong access width or treating adjacent fields as separate registers can corrupt neighboring capability state.
- MSI and MSI-X layouts contain intentional aliases and format-dependent fields, especially 32-bit versus 64-bit MSI data/mask/pending locations. Consumers must follow the matching PCI capability format.
- AER status/mask/severity bits can be sticky, write-one-to-clear, or policy-sensitive. Generic read/modify/write treatment can lose diagnostic evidence, fail to clear latched errors, or mask significant PCIe faults.
- Capability `NEXT_PTR` fields define the PCIe capability chain. Incorrect generated values or wrong offsets can break VF capability discovery by the host, guest, or hypervisor.
- ARI and function-group fields affect multi-function/VF enumeration. Incorrect masks can make VF routing or capability walking look valid while exposing the wrong function topology.
- Link capability/status fields are status/control metadata. Misreporting supported speeds, widths, equalization state, or DRS/crosslink support can confuse PCIe policy and diagnostics.

## Test Signals

Useful validation is mostly build-time, generated-header consistency, and hardware/SR-IOV integration oriented:

- Build AMDGPU with NBIO 4.3.0 support enabled; missing, renamed, or duplicated macros should surface in `nbio_v4_3.c` or SMU13 include paths.
- Diff this chunk against the authoritative NBIO 4.3.0 register database and `nbio_4_3_0_offset.h` to confirm register names, VF suffixes, and field masks remain synchronized.
- In SR-IOV environments, enumerate VFs spanning at least VF10 through VF13 and verify PCI config-space identity, BARs, capability chains, PCIe capability values, MSI/MSI-X capabilities, and ARI/AER visibility.
- Exercise VF MSI and MSI-X enable, mask, unmask, pending-bit, and interrupt-delivery paths; lost or misrouted interrupts can indicate address/data/mask field drift.
- Trigger or observe PCIe/AER diagnostics and confirm correct uncorrectable/correctable status, mask, severity, header-log, and TLP-prefix-log behavior for the affected VFs.
- Exercise FLR, D3hot-to-D0, reset-time-reporting, suspend/resume, and VF teardown paths while watching for stuck completion-timeout, transaction, or AER states.
- Run link retrain/equalization and PCIe power-management tests where available, checking that link capability/control/status fields report coherent speed, width, ASPM, LTR, OBFF, and equalization state.

## Chunk Notes

- Lines 27174-27611 complete the VF10 PCIe capability, MSI/MSI-X, vendor-specific, AER, ARI, and RTR field definitions started by the previous chunk.
- Lines 27612-28333 cover a complete `nbio_nbif0_bif_cfg_dev0_epf0_vf11_bifcfgdecp` field-mask block.
- Lines 28334-29055 cover a complete `nbio_nbif0_bif_cfg_dev0_epf0_vf12_bifcfgdecp` field-mask block.
- Lines 29056-29592 begin `nbio_nbif0_bif_cfg_dev0_epf0_vf13_bifcfgdecp` and stop inside `BIF_CFG_DEV0_EPF0_VF13_0_PCIE_UNCORR_ERR_MASK`.
