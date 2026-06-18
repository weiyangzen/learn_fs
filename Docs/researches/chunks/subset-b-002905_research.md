# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 2541-4960

## Scope

This chunk is part of AMDGPU's generated NBIO 2.3 register-field shift/mask catalog. It contains C preprocessor constants only: no functions, structs, enums, variables, allocation, locking, runtime branches, or direct register accesses.

The assigned range starts in the middle of `PSWUSCFG0_0_IRQ_BRIDGE_CNTL`, at the remaining bridge-control masks, then covers the rest of the `PSWUSCFG0_0` PCI/PCIe capability and extended-capability field definitions through `PSWUSCFG0_0_PCIE_CCIX_TRANS_CNTL`. It then begins `addressBlock: nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp`, covering the standard endpoint-function config header and early power-management/PCIe capability fields for `BIF_CFG_DEV0_EPF0_0` through `BIF_CFG_DEV0_EPF0_0_LINK_CNTL`. The final line is only the `//BIF_CFG_DEV0_EPF0_0_LINK_STATUS` marker; that register's fields continue in the next chunk.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header slice is to name the bit layout for NBIO 2.3 PCI configuration and PCIe extended capability registers. Consumers combine these constants with addresses from `nbio_2_3_offset.h` and AMDGPU register helpers to pack, extract, set, clear, or test individual fields in 16-bit and 32-bit hardware register words.

The generated convention is:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field's encoded mask.

These macros form a compile-time hardware ABI. The same names are consumed by `REG_SET_FIELD`, `REG_GET_FIELD`, direct mask operations, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and related SOC15/NBIO helpers in AMDGPU.

## Important Macro Families

The `PSWUSCFG0_0` portion describes a PCIe bridge/upstream-port style config space. It includes bridge interrupt/control bits, extended bridge control, vendor capability headers, adapter/subsystem IDs, PCI power-management capability and status/control fields, PCIe capability headers, device/link capability and control/status registers, MSI message control/address/data fields, SSID and MSI mapping capabilities, and vendor-specific capability headers.

The base PCIe capability fields cover payload and read-request sizing, relaxed ordering, no-snoop, extended tags, function-level reset, correctable/non-fatal/fatal/unsupported-request reporting, link speed/width, ASPM/power-management support, common-clock, retrain/link-disable controls, DRS signaling, completion-timeout policy, LTR enablement, OBFF, atomic-op support, target link speed, compliance/speed disable, de-emphasis, transmit margin, equalization status, and downstream component presence.

The AER block includes `PSWUSCFG0_0_PCIE_UNCORR_ERR_STATUS`, `..._MASK`, and `..._SEVERITY` fields for data-link protocol, surprise down, poisoned TLP, flow-control protocol, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic-op egress blocked, TLP prefix blocked, and poisoned-TLP egress blocked conditions. It also includes correctable error status/mask fields, AER capability/control, header logs, and TLP prefix logs.

The link-training and PCIe extended capability area covers secondary PCIe link control, lane error status, per-lane equalization controls for lanes 0-15, ACS capability/control, multicast capability/control/address/block/overlay BAR fields, LTR capability, ARI capability/control, L1 PM substates capability/control, data-link feature capability/status, 16 GT/s PHY capability/control/status, per-lane 16 GT/s equalization control, and PCIe lane margining control/status for lanes 0-15.

The `PSWUSCFG0_0_PCIE_ESM_*` and CCIX-related families describe extended speed mode and cache-coherent interconnect capability surfaces. They include ESM headers/status/control, large capability bitmaps for supported data-rate/vector combinations, CCIX required/optional ESM capability, CCIX ESM status/control, per-lane 20 GT/s and 25 GT/s equalization controls, and CCIX transport capability/control fields.

The `BIF_CFG_DEV0_EPF0_0` portion begins a physical endpoint function config decoder block. It covers standard PCI config header fields: vendor/device IDs, command and status, revision/class code, cache line, latency, header type, BIST, BARs 1-6, CardBus CIS pointer, subsystem adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, and max latency. It then covers vendor, PM, and PCIe capability headers plus early PCIe device/link capability and control fields. Relative to the bridge-style `PSWUSCFG0_0` device-control fields, the endpoint block's `DEVICE_CNTL` uses `INITIATE_FLR` at bit 15 and `DEVICE_STATUS` includes `EMER_POWER_REDUCTION_DETECTED`.

No callable APIs or C types are declared in this range; the public surface is entirely macro names.

## Control Flow

There is no executable control flow in this header. Runtime behavior appears in AMDGPU code that includes the header:

1. Code selects an address from `nbio_2_3_offset.h` or an SMN/PCIe address literal for the same hardware block.
2. It reads a register value through NBIO/SOC15/PCIe helpers.
3. It uses these `__SHIFT` and `_MASK` constants, usually through `REG_SET_FIELD`, `REG_GET_FIELD`, or direct bitwise operations, to update or decode fields.
4. It writes the resulting value back, polls status, or reports decoded state according to the hardware programming sequence.

`nbio_v2_3.c` is the closest integration example in this source tree. It includes `nbio_2_3_sh_mask.h`, programs PCIe max-read-request policy, ASPM/LTR behavior, light-sleep/clock-gating state, indirect PCIe index/data offsets, and related NBIO registers. Some specific masks used by that file are outside this exact line range, but the access pattern is the same for the capability and endpoint fields defined here.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes MMIO/config-space hardware state whose lifetime is controlled by GPU reset, PCIe reset, function-level reset, power transitions, firmware policy, link retraining, suspend/resume, SR-IOV PF/VF policy, and host PCI enumeration.

The represented state includes bridge/device command bits, PCI/PCIe capability-list links, subsystem identity, BAR and ROM aperture fields, MSI routing data, PCIe device and link policy, AER masks/status/severity/logs, lane equalization and margining controls/status, ACS/ARI/multicast/LTR/L1 PM-substate policy, data-link feature status, high-speed PHY training state, ESM/CCIX capability and control, and endpoint function config header fields.

Several fields are status or sticky logs rather than ordinary writable configuration. AER status/log fields, link training/equalization status, lane margining status, emergency power-reduction detection, and pending/error bits are hardware-owned observations. Other fields are command strobes or side-effect controls, such as link retrain, function-level reset, completion-timeout policy, interrupt/message enables, and status clear bits. The header names bit positions but does not encode read/write side effects.

## Dependencies And Integration Points

The direct dependency is the generated NBIO 2.3 register database. This shift/mask header must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h`, which provides matching `cfgPSWUSCFG0_0_*` and `cfgBIF_CFG_DEV0_EPF0_0_*` offsets for these config-space fields.
- `nbio_2_3_default.h`, where generated defaults exist for the same generation.
- AMDGPU helper macros and accessors such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

Observed includes in this tree are `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, and SMU11 power-management files for Navi10/Sienna Cichlid. That places this header on the integration path for NBIO initialization, PCIe power management, ASPM/LTR, link configuration, interrupt setup, SR-IOV mailbox/GPU virtualization support, and GPU power-management policy.

Because the macros are untyped constants, a renamed field normally fails at compile time, but a wrong shift or mask can compile cleanly and corrupt an adjacent PCIe field at runtime.

## Risks And Edge Cases

- Chunk-boundary risk is high. The first lines are only the tail masks of `PSWUSCFG0_0_IRQ_BRIDGE_CNTL`; its shifts and early masks are in the previous chunk. The final line is only the `BIF_CFG_DEV0_EPF0_0_LINK_STATUS` marker; its fields are in the next chunk.
- Width and access-size mismatches matter. This chunk mixes 8-bit, 16-bit, and 32-bit PCI config fields, while the masks are C constants. Consumers must use access widths and offsets matching the generated register definition.
- AER fields are side-effect sensitive. Treating status/log/clear behavior as a normal read-modify-write register can hide errors, clear diagnostic evidence, or leave severity/mask policy inconsistent with the driver.
- PCIe link-control fields can cause interoperability regressions. Incorrect target speed, retrain, common-clock, ASPM, L1 PM-substate, LTR, DRS, equalization, or 16 GT/s settings can produce link instability, bandwidth loss, resume failures, or device disappearance.
- MSI fields affect interrupt routing. Wrong message address/data, multi-message enable, 64-bit address capability, or per-vector behavior can cause lost or spurious interrupts.
- ACS, ARI, multicast, CCIX, ESM, and SR-IOV-adjacent fields affect isolation and topology behavior. Using a bridge/upstream-port macro against endpoint-function offsets, or vice versa, is syntactically valid but semantically wrong.
- Repeated per-lane equalization and margining definitions are prone to off-by-one generation mistakes. A single lane-number shift/mask mismatch can make diagnostics report the wrong lane or train the wrong per-lane control.
- Capability-list pointer fields are structural. Wrong `CAP_ID`, `NEXT_PTR`, `PCIE_CAP_ID`, or capability version masks can break PCI capability traversal and feature detection.

## Test Signals

Useful validation is mostly build, generated-header consistency, and hardware integration:

- Build AMDGPU configurations that include NBIO 2.3, Navi10/Sienna Cichlid SMU paths, SR-IOV support, PCIe ASPM/LTR, MSI, and AER support.
- Compare the generated `nbio_2_3_sh_mask.h` field names, widths, and masks against the matching AMD register database and `nbio_2_3_offset.h` config offsets.
- Exercise PCI enumeration and capability traversal; malformed capability IDs, next pointers, class/header fields, BAR fields, or MSI/PCIe capability layouts should appear as enumeration or lspci-style decode anomalies.
- Run PCIe link tests covering speed/width negotiation, retraining, ASPM, L1 PM substates, LTR, 16 GT/s status, equalization, lane error status, and lane margining diagnostics.
- Exercise interrupt delivery with MSI enabled and disabled; lost/spurious interrupts can indicate message-control or address/data mask drift.
- Use AER/error-injection or fault-observation paths where available to verify uncorrectable/correctable status, masks, severity, header logs, and TLP prefix logs decode correctly.
- In SR-IOV or virtualized environments, test PF/VF mailbox and function reset flows, because endpoint function config, FLR, ARI, ACS, and capability layouts are part of the isolation and reset contract.

## Chunk-Specific Notes For Merge

When the final per-file report is reconciled, this chunk should be merged with adjacent `nbio_2_3_sh_mask.h` chunks. The whole-file report should avoid presenting `PSWUSCFG0_0_IRQ_BRIDGE_CNTL` or `BIF_CFG_DEV0_EPF0_0_LINK_STATUS` as fully covered by this range alone, because both registers cross chunk boundaries.
