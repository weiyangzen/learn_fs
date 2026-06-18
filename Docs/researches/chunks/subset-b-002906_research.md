# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 4961-7402

## Scope

This chunk is a slice of AMDGPU's generated NBIO 2.3 shift/mask header. It contains C preprocessor constants only. There are no functions, typedefs, structs, runtime branches, allocation sites, locks, reference counts, or persistent software objects in this range.

The selected lines begin with the field definitions for `BIF_CFG_DEV0_EPF0_0_LINK_STATUS` after the register-name comment at line 4960. The range then covers a large part of the `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` PCI configuration-space map: PCIe link/device capability registers, MSI/MSI-X, vendor-specific PCIe capabilities, virtual-channel capabilities, device serial number, Advanced Error Reporting, resizable BAR and power budgeting/DPA metadata, PCIe secondary/equalization/margining capabilities, ACS/ATS/PRI/PASID/multicast/LTR/ARI/SR-IOV/TPH/DLF/16GT PHY capability blocks, VF resizable BARs, and the AMD GPU IOV vendor-specific capability block.

Near the end of the range, the address block switches to `nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp`. This chunk covers the start of endpoint function 1's standard PCI config header and capability registers through `BIF_CFG_DEV0_EPF1_0_LINK_CAP__L1_EXIT_LATENCY_MASK`. The remaining `EPF1` link-capability masks continue just after the assigned line range, so file-level reconciliation must merge adjacent chunks before making whole-register claims.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU hardware register metadata. It does not implement Ceph or distributed filesystem logic.

## Purpose

The header publishes the bitfield ABI for NBIO 2.3 PCIe/NBIF configuration registers. The macros are meant to be combined with sibling offset/default headers and AMDGPU register helpers to decode or update hardware register words. Each field usually appears as:

- `<REGISTER>__<FIELD>__SHIFT`, the low bit index for the field.
- `<REGISTER>__<FIELD>_MASK`, the mask for the encoded field in the 16-bit or 32-bit register word.

Examples in this range include `BIF_CFG_DEV0_EPF0_0_LINK_STATUS__CURRENT_LINK_SPEED__SHIFT` with `BIF_CFG_DEV0_EPF0_0_LINK_STATUS__CURRENT_LINK_SPEED_MASK`, AER fields such as `BIF_CFG_DEV0_EPF0_0_PCIE_UNCORR_ERR_STATUS__MALFORMED_TLP_STATUS_MASK`, GPU IOV fields such as `BIF_CFG_DEV0_EPF0_0_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_INTR_ENABLE__VF0_FLR_NOTIFY_MASK`, and the beginning of `EPF1` link capability fields such as `BIF_CFG_DEV0_EPF1_0_LINK_CAP__LINK_WIDTH_MASK`.

The companion `nbio_2_3_offset.h` supplies the matching config offsets for these symbols, for example `cfgBIF_CFG_DEV0_EPF0_0_LINK_STATUS`, `cfgBIF_CFG_DEV0_EPF0_0_LINK_STATUS2`, the `cfgBIF_CFG_DEV0_EPF0_0_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_*` range, and `cfgBIF_CFG_DEV0_EPF1_0_LINK_CAP`. Runtime code includes this header through NBIO and virtualization files such as `amdgpu/nbio_v2_3.c` and `amdgpu/mxgpu_nv.c`.

## Important Macro Families

The first group describes endpoint function 0 PCIe capability state. `BIF_CFG_DEV0_EPF0_0_LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` expose current link speed and width, link training, data-link active status, completion-timeout support/control, ARI and atomic operation capability/control, LTR and OBFF capability/control, target link speed, compliance controls, deemphasis and equalization status, downstream-component presence, DRS, and related PCIe Gen3+ behavior.

The MSI and MSI-X groups define capability-list headers, MSI enable/multiple-message controls, 32-bit and 64-bit message address/data fields, vector masks and pending fields, MSI-X table/PBA BIR and offset fields, table size, function mask, and MSI-X enable. These macros name the PCI interrupt delivery configuration exposed by the endpoint's config space; actual interrupt routing is configured by PCI/MSI code and AMDGPU initialization paths.

The generic PCIe vendor-specific and virtual-channel capability groups expose enhanced capability headers, vendor-specific length/revision/vendor ID, VC capability/control/status registers, and VC0/VC1 resource capability/control/status fields. The VC resource macros cover port arbitration capability, rejected snoop/non-snoop transactions, maximum time slots, arbitration select/table offsets, resource identifiers, traffic-class masks, and negotiation pending/status fields.

The device serial number and Advanced Error Reporting blocks define serial-number dwords, AER capability headers, uncorrectable error status/mask/severity bits, correctable error status/mask bits, AER capability/control fields, header logs, and TLP prefix logs. The AER masks name PCIe error conditions such as data-link protocol error, surprise down, poisoned TLP, flow-control protocol error, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal errors, MC blocked TLP, atomic-op egress blocking, TLP prefix blocking, and poisoned TLP egress blocking.

The resizable BAR, power budgeting, and dynamic power allocation groups name PCIe extended capability registers for BAR1 through BAR6, selected power budget data, power budget capability, DPA substate capacity/status/control, and per-substate power allocation values. The BAR control macros expose BAR size and size-enable fields that must stay aligned with PCIe resource assignment and firmware policy.

The PCIe secondary, lane equalization, and lane margining groups provide link-control-3 equalization settings, lane error status, per-lane equalization controls for lanes 0-15, 16GT capability/control/status/parity mismatch fields, and per-lane margining control/status for lanes 0-15. These definitions support low-level PCIe signal integrity and training diagnostics, not high-level device logic.

The access/isolation capability group includes ACS, ATS, Page Request Interface, PASID, multicast, LTR, ARI, and SR-IOV macros. Important examples are `BIF_CFG_DEV0_EPF0_0_PCIE_ACS_CAP`, `PCIE_ACS_CNTL`, `PCIE_ATS_CAP`, `PCIE_ATS_CNTL`, `PCIE_PAGE_REQ_CNTL`, `PCIE_PAGE_REQ_STATUS`, `PCIE_PASID_CAP`, `PCIE_PASID_CNTL`, `PCIE_MC_*`, `PCIE_LTR_CAP`, `PCIE_ARI_CAP`, `PCIE_ARI_CNTL`, and `PCIE_SRIOV_*`. These define field layouts for request routing, address translation, PASID width/enablement, page-request status, multicast controls, latency tolerance, alternate routing ID behavior, and virtual-function BAR/page-size/count/stride metadata.

The TPH requester and data-link feature groups expose steering mode, ST table location/size, requester enable mode, local ST table size, and data-link feature exchange/status. The 16GT PHY capability block names Gen4/16GT equalization controls, link status, and parity mismatch status for local/RTM paths plus lane-specific equalization fields.

The GPU IOV vendor-specific capability block is the densest virtualization-oriented family in this chunk. `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST_GPUIOV` and `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV*` cover VSEC identity/length/revision, shadow SR-IOV state, interrupt enable/status bits for command completion and hang/FLR/VM-busy/mailbox events, reset control, hypervisor/VM mailbox dwords, context size/location/offset, total framebuffer accounting, global offsets/regions, peer-to-peer-over-XGMI enablement, per-VF framebuffer size/offset entries for VF0 through VF30, and scheduler dwords for UVD, VCE, GFX, and UVD1. These are PF/hypervisor-facing resource partitioning and mailbox layout definitions.

The final `EPF1` group begins a second endpoint-function config decoder block. It defines standard PCI header fields such as vendor/device ID, command/status, revision/class code, cache line, latency, header/BIST, BAR1-BAR6, CardBus pointer, subsystem adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, max latency, a vendor capability, power-management capability/status/control, PCIe capability header, device capability/control/status, and the first portion of link capability. This mirrors the standard PCI/PCIe config-space layout for function 1, but the assigned range ends before the full `LINK_CAP` field set is present.

## APIs, Types, And Functions

This chunk has no callable APIs, C types, or functions. Its public surface is the macro namespace consumed at compile time.

The practical API contract is the combination of:

- Register-name comments such as `//BIF_CFG_DEV0_EPF0_0_PCIE_UNCORR_ERR_STATUS`.
- `__SHIFT` macros for bit offsets.
- `_MASK` macros for field masks.
- Matching `cfg...` register offsets in `nbio_2_3_offset.h`.
- AMDGPU helper macros/functions outside this file, commonly `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and `SOC15_REG_OFFSET`.

Because the constants are untyped, the C compiler cannot verify that a mask from one register family is paired with the correct offset. Correctness depends on generated-header consistency and careful use by versioned NBIO/PCIe/virtualization code.

## Control Flow

There is no executable control flow in this header slice. Runtime behavior is supplied by consumers:

1. Driver or firmware-facing code chooses a register offset from `nbio_2_3_offset.h` or from hardcoded SMN/config constants.
2. The code reads a 16-bit or 32-bit register value through PCIe, SOC15, or indirect config-space access helpers.
3. It uses the `__SHIFT` and `_MASK` definitions, often through `REG_GET_FIELD` or `REG_SET_FIELD`, to extract, test, clear, or encode a field.
4. It writes the modified value back, polls a status field, or reports the decoded field through a diagnostic path.

For integration context, `amdgpu/nbio_v2_3.c` includes `nbio_2_3_sh_mask.h` for NBIO 2.3 initialization and register programming. `amdgpu/mxgpu_nv.c` also includes this header and implements SR-IOV mailbox transactions using NBIO 2.3 register definitions and mailbox offsets. The control flow for mailbox valid/ack polling, GPU-access requests, doorbell setup, HDP remapping, link/power handling, and reset policy is in those `.c` files, not in this generated header.

## State And Persistence Behavior

The file stores no software state and persists nothing to disk. It describes hardware-visible PCI config and extended capability state whose lifetime is controlled by the GPU, PCIe hierarchy, firmware, PF/hypervisor policy, reset/FLR, suspend/resume, BACO/power transitions, and driver programming.

The represented hardware state includes link status and control, completion timeout configuration, MSI/MSI-X interrupt configuration, VC resource negotiation state, AER status/masks/severity/logs, BAR sizing controls, power budgeting and DPA values, lane equalization and margining diagnostics, ACS/ATS/PRI/PASID controls, multicast filters, LTR/ARI/SR-IOV configuration, TPH/data-link feature state, Gen4/16GT training and parity status, GPU IOV resource/mailbox/interrupt state, and the start of function 1's standard PCI configuration space.

Some fields are persistent configuration until reset or reprogramming, such as BAR sizing, ACS/ATS/PASID enables, SR-IOV page size and VF counts, MSI/MSI-X table configuration, and GPU IOV framebuffer allocation fields. Others are hardware-owned status or logs, such as link training/equalization status, AER status and header/TLP prefix logs, lane error/margining status, SR-IOV status, and mailbox valid/ack/status bits. Some registers have command or write-one-to-clear semantics in the underlying hardware, but this header intentionally only names bit positions and masks.

## Dependencies And Integration Points

The direct dependency is the generated NBIO 2.3 register database. This shift/mask header must remain synchronized with `nbio_2_3_offset.h` and `nbio_2_3_default.h`, which provide the corresponding offsets and reset/default values. For example, the offset header maps the GPU IOV VSEC fields from `cfgBIF_CFG_DEV0_EPF0_0_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV` through scheduler dwords, and maps `cfgBIF_CFG_DEV0_EPF1_0_LINK_CAP` for the final partial register family in this chunk.

Runtime integration points include:

- NBIO 2.3 setup in `amdgpu/nbio_v2_3.c`, which includes this header with the offset/default headers and uses NBIO register fields for doorbells, memory access, interrupts, HDP remapping, power/clock behavior, and ASIC-specific setup.
- SR-IOV and GPU virtualization in `amdgpu/mxgpu_nv.c`, which uses NBIO 2.3 register definitions and mailbox offsets for PF/VF message valid/ack handshakes and GPU access requests.
- PCIe interrupt setup using MSI/MSI-X fields and table/PBA locations.
- PCIe link diagnostics and policy code using link speed, width, training, equalization, 16GT, DRS, and lane error/margining fields.
- AER/RAS/error handling paths that decode or mask correctable and uncorrectable PCIe error conditions and consume header/TLP prefix logs.
- Isolation and address-translation policy through ACS, ATS, PRI, PASID, ARI, SR-IOV, and GPU IOV per-VF resource fields.
- Power and resource reporting through power budgeting, DPA, LTR, OBFF, and link power-management fields.

The macros also align structurally with later NBIO/NBIF generations. Similar names appear in NBIO 7.x and NBIF 6.x/7.x headers, but masks should not be copied across generations without checking the exact offset and field definitions.

## Risks And Edge Cases

- The chunk boundary is artificial. The `LINK_STATUS` register-name comment is one line before the assigned start, and the `EPF1 LINK_CAP` register continues after line 7402. Adjacent chunks are required for complete per-register and per-file analysis.
- Generated names are long and repetitive. Register families such as lane 0-15 equalization/margining, VF0-VF30 framebuffer fields, and UVD/VCE/GFX scheduler dwords are vulnerable to index drift, skipped entries, or field-width mistakes if edited by hand.
- Some mask names include repeated words like `...ERR_MASK__..._MASK`, which reflects the generated `register__field_MASK` convention. Renaming these for readability would break consumers.
- Width and access-size assumptions matter. Many PCI capability fields are 16-bit-style masks such as `0xFFFFL` or `0x00FFL`, while AER logs, BAR controls, mailbox dwords, scheduler dwords, and many GPU IOV fields are full 32-bit values. Consumers must use the correct register access width and offset.
- AER status, page-request status, MSI pending, link status, margining status, and mailbox bits may be sticky, hardware-owned, clear-on-write, or handshake-driven. The header does not encode side effects, so generic read-modify-write logic can be unsafe on some fields.
- MSI/MSI-X programming is interrupt-delivery sensitive. Wrong masks for enable/function mask, table BIR/offset, PBA BIR/offset, message address/data, or per-vector masks can cause lost interrupts, spurious interrupts, or broken virtualization interrupt routing.
- ACS/ATS/PRI/PASID/ARI/SR-IOV/GPU IOV fields are isolation-sensitive. Incorrect programming can route requests through the wrong function, enable address translation unexpectedly, expose the wrong VF framebuffer slice, or break PF/VF reset and mailbox ownership.
- Link training, 16GT equalization, and lane margining fields are platform-sensitive. Wrong decode or control writes can misreport link health, force unsuitable compliance/equalization behavior, or hide signal-integrity failures.
- GPU IOV mailbox and interrupt bits are handshake surfaces between PF, VF, hypervisor, firmware, and the guest driver. Misinterpreting valid/ack/interrupt bits can wedge access negotiation or cause a VF to miss reset/hang notifications.
- The final `EPF1` register block is only a prefix in this range. Treating it as complete would omit several `LINK_CAP` masks and later `EPF1` link/control/status/capability families.

## Test Signals

Useful validation signals for any change touching this header area include:

- Build AMDGPU configurations that include NBIO 2.3, SR-IOV, PCIe AER, MSI, MSI-X, ATS, PASID, and virtualization support. Missing or renamed macros should fail at compile time in versioned NBIO or virtualization code.
- Run generated-header consistency checks against the AMD register database or against sibling `nbio_2_3_offset.h`/`nbio_2_3_default.h` so each offset has the expected shift/mask fields and no unintended overlaps.
- Enumerate affected GPUs and verify PCI capability traversal for MSI/MSI-X, PCIe, AER, ACS/ATS/PRI/PASID, ARI, SR-IOV, and vendor-specific GPU IOV capability blocks.
- Exercise MSI/MSI-X interrupt delivery under bare-metal and SR-IOV configurations, including vector masking and pending-bit behavior where available.
- Use PCIe link diagnostics to confirm decoded speed, width, training state, equalization, DRS, 16GT, and lane error/margining status match hardware and platform expectations.
- In SR-IOV deployments, create and destroy VFs, validate VF BAR and framebuffer sizing, exercise PF/VF FLR/reset notifications, and confirm GPU IOV mailbox valid/ack interrupts and per-VF framebuffer fields remain isolated.
- Exercise AER or error-injection diagnostics, where supported, to confirm uncorrectable/correctable error status, masks, severity, header logs, and TLP prefix logs decode to the expected bit names.
- Test suspend/resume, FLR, BACO/power transitions, and reset paths to ensure PCIe config, MSI/MSI-X, link, SR-IOV, and GPU IOV state is restored or renegotiated correctly.

## Chunk Notes For Merge

When creating the final per-file research document, merge this with neighboring chunks for the same `nbio_2_3_sh_mask.h` source. The merged report should preserve that this file is a generated NBIO 2.3 hardware bitfield catalog, while this specific chunk covers late `EPF0` PCIe capability and GPU IOV VSEC definitions plus the beginning of `EPF1` PCI/PCIe configuration definitions.
