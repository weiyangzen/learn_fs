# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 19907-22328

## Scope

This chunk is a generated AMD NBIO 4.3.0 register shift/mask header segment. It contains only C preprocessor constants; there are no functions, structs, variables, dynamic allocations, locks, branches, loops, or direct register accesses in this range.

The assigned lines contain 2,142 `#define` entries: 1,071 `__SHIFT` constants and 1,071 `_MASK` constants across 272 commented register blocks. The slice starts in the middle of the `BIF_CFG_DEV0_EPF0_VF0_0_LINK_CNTL` definition, completes the remainder of the `VF0_0` PCIe virtual-function configuration image, contains complete `BIF_CFG_DEV0_EPF0_VF1_0` and `BIF_CFG_DEV0_EPF0_VF2_0` blocks, and starts `BIF_CFG_DEV0_EPF0_VF3_0` before stopping after the first field of `VF3_0_PCIE_ADV_ERR_RPT_ENH_CAP_LIST`.

Although this file lives under a local `ceph-client` source mirror, this header is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this range is to publish bitfield positions for NBIO 4.3.0 PCIe/SR-IOV virtual-function configuration-space registers. Each hardware field is represented as:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used when packing or extracting a field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, clear, preserve, or update a field.

The companion address header, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h`, supplies matching `regBIF_CFG_DEV0_EPF0_VF*_*` register offsets and base indices. Runtime AMDGPU code combines those offsets with this shift/mask header through the normal register helper layer, including `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

## Important Macro Families

The opening VF0 fragment starts at `BIF_CFG_DEV0_EPF0_VF0_0_LINK_CNTL__PTM_PROP_DELAY_ADAPT_INTER_B__SHIFT`, so the `PM_CONTROL` shift immediately before it is outside this chunk while the matching `PM_CONTROL_MASK` is inside. The rest of VF0 covers link status, PCIe device/link capability 2 controls and status, MSI and MSI-X capability fields, vendor-specific extended capability fields, AER status/mask/severity/log fields, ARI capability/control fields, route-through-router enhanced capability, and `RTR_DATA1`/`RTR_DATA2` payload fields.

The complete VF1 and VF2 blocks repeat a full Type 0 PCI configuration-space image for `BIF_CFG_DEV0_EPF0`. Each block includes identity/header fields (`VENDOR_ID`, `DEVICE_ID`, command/status, revision/class codes, cache line, latency, header/device type, BIST), BAR fields `BASE_ADDR_1` through `BASE_ADDR_6`, CardBus CIS pointer, subsystem vendor/device adapter ID, ROM base address, capability pointer, interrupt line/pin, and min-grant/max-latency fields.

The VF1 and VF2 PCIe capability sections define `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`. Important fields include max payload support/size, max read request size, relaxed ordering, no-snoop, extended tag, phantom function support, role-based error reporting, function-level reset capability/initiation, completion timeout controls, atomic operation support/enables, ID-based ordering, LTR, OBFF, emergency power reduction, 10-bit tags, link speed/width, ASPM, clock power management, link disable/retrain, common clock, autonomous width/speed disables, DRS signaling, de-emphasis, compliance controls, equalization status, and downstream component presence.

The interrupt capability portions cover MSI and MSI-X. MSI fields include capability-list linkage, enable/multiple-message/64-bit/per-vector masking controls, MSI message address low/high, message data, extended message data, mask and pending dwords, and 64-bit aliases for data, extended data, mask, and pending state. MSI-X fields include table size, function mask, enable, table BIR/offset, and pending-bit-array BIR/offset.

The vendor-specific and AER portions define PCIe vendor-specific enhanced capability list/header fields, two scratch payload dwords, AER enhanced capability list fields, uncorrectable error status/mask/severity bits, correctable error status/mask bits, advanced error capability/control bits, four TLP header log dwords, and four TLP prefix log dwords. Covered AER bits include DLP, surprise down, poisoned TLP, flow-control, completion timeout, completion abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic-op egress blocked, TLP prefix blocked, poisoned TLP egress blocked, receiver error, bad TLP, bad DLLP, replay rollover, replay timeout, advisory non-fatal, correctable internal error, and header-log overflow conditions.

The ARI and router portions expose `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, `PCIE_ARI_CNTL`, `PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2`. ARI fields include capability ID/version/next pointer, MFVC and ACS function-group capability, next-function number, MFVC/ACS enable, and function-group selection. Router fields are opaque full-dword payload masks in this header.

The VF3 block is only partial in this chunk. It covers VF3 from identity/header fields through BARs, PCIe device/link controls, MSI/MSI-X, vendor-specific enhanced capability fields, and the first `PCIE_ADV_ERR_RPT_ENH_CAP_LIST__CAP_ID__SHIFT` line. The rest of VF3 AER, ARI, router, and any following VF definitions are outside this work item.

## Control Flow

There is no executable control flow in this header. Runtime behavior occurs only in code that includes these generated constants:

1. AMDGPU code selects a `regBIF_CFG_DEV0_EPF0_VF*_*` offset from `nbio_4_3_0_offset.h`.
2. It reads or composes a PCIe configuration-space dword through the AMD register access layer.
3. It applies this header's `__SHIFT` and `_MASK` macros directly or via helpers such as `REG_SET_FIELD` and `REG_GET_FIELD`.
4. It writes a control value, decodes a capability/status value, polls a hardware-owned bit, clears a sticky diagnostic bit, or exposes decoded state to PCIe, SR-IOV, interrupt, reset, RAS, or diagnostics code.

Typical consuming flows include VF configuration-space presentation, SR-IOV VF lifecycle handling, PCIe link/power policy, function-level reset, MSI/MSI-X interrupt delivery, AER diagnostics, ARI enumeration, route-through-router configuration, and PF or hypervisor inspection of VF state.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-backed PCIe configuration-space state owned by the GPU, firmware, host PCIe fabric, Linux PCI core policy, and AMDGPU NBIO/SR-IOV management code.

The represented state includes VF identity/header values, BAR and ROM address windows, command/status bits, capability-list pointers, PCIe capability/control/status fields, link capability and link-training state, MSI/MSI-X programming state, vendor-specific scratch fields, AER error status/mask/severity/log state, ARI function-group controls, and router data payloads. Some fields are static capability descriptions, some are software-programmed controls, some are hardware-updated status, and some may be sticky or write-one-to-clear diagnostics. The generated masks do not encode access permissions, reset defaults, side effects, polling rules, or ownership boundaries.

VF1 and VF2 are complete within this chunk and can be reasoned about as complete repeated config-space layouts. VF0 and VF3 are boundary fragments and require adjacent chunks before making whole-VF or whole-register claims.

## Dependencies And Integration Points

The primary dependency is the generated NBIO 4.3.0 register database. This file must remain synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h`, which supplies the matching register addresses and base indices. This tree has no sibling `nbio_4_3_0_default.h`, so reset/default-value validation for these fields must come from the hardware database, firmware behavior, or runtime observations rather than a local default header.

Direct in-tree consumers of the NBIO 4.3 generated headers include `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c` and SMU13 power-management files such as `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c` and `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_7_ppt.c`. `amdgpu_discovery.c` selects `nbio_v4_3_funcs` or `nbio_v4_3_sriov_funcs`, and `nbio_v4_3.c` provides the NBIO v4.3 operations for HDP flush offsets, PCIe index/data offsets, memory access enablement, doorbell range programming, interrupt handler control, clock gating/light sleep, LTR/ASPM programming, register remapping, and RAS error-event handling.

The most relevant integration surfaces are AMDGPU NBIO/BIF setup, PCIe index/data indirect access, SR-IOV VF initialization and teardown, VF interrupt delivery, PCIe link and power-management policy, FLR/reset flows, AER/RAS diagnostics, ARI-capable enumeration, router/VSEC diagnostics, suspend/resume, and runtime power transitions. These fields also overlap generic PCIe concepts managed by platform firmware and the Linux PCI core: command/status, BARs, MSI/MSI-X, PCIe device/link control, AER, ARI, LTR, OBFF, completion timeout, and FLR.

## Risks And Edge Cases

- The chunk boundaries are artificial. It starts after `VF0_0_LINK_CNTL__PM_CONTROL__SHIFT` but includes `PM_CONTROL_MASK`, and it stops before the mask fields for `VF3_0_PCIE_ADV_ERR_RPT_ENH_CAP_LIST`; adjacent chunks are required for complete VF0 and VF3 analysis.
- These are untyped preprocessor constants. A stale mask or shift can compile cleanly while decoding or programming the wrong hardware bit.
- The VF blocks are mechanically repetitive. Off-by-one suffix mistakes around `VF0_0`, `VF1_0`, `VF2_0`, and `VF3_0` can silently target the wrong virtual function and break SR-IOV isolation, interrupt routing, or diagnostics.
- Register-address and field-mask mismatches are easy in generated headers. A valid `VF2_0_LINK_CNTL` mask applied to a `VF1_0`, `VF3_0`, or non-VF offset may still produce plausible bit operations while corrupting unrelated config state.
- PCIe control fields are interoperability-sensitive. Incorrect FLR, max payload, max read request, completion timeout, relaxed ordering, no-snoop, LTR, OBFF, ARI, link disable/retrain, or target-speed values can cause DMA ordering bugs, enumeration failures, link instability, reset failures, or platform-specific hangs.
- MSI/MSI-X fields carry interrupt-delivery side effects. Width, aliasing, table offset/BIR, mask, pending-bit, or enable mistakes can cause lost interrupts, misrouted interrupts, or unexpectedly unmasked vectors.
- AER status, mask, severity, header log, and TLP prefix log fields can be sticky, write-one-to-clear, or hardware-owned. Generic read/modify/write treatment can clear diagnostic evidence or leave errors masked incorrectly.
- BAR and ROM fields affect resource exposure. Incorrect masks can expose invalid apertures, confuse VF resource sizing, or undermine isolation expectations in virtualized configurations.
- ARI and router/VSEC fields affect enumeration and routing semantics. Incorrect next-function numbers, function-group controls, or opaque router data interpretation can affect VF discovery and PF/hypervisor coordination.

## Test Signals

Useful validation is primarily build-time and hardware-integration oriented:

- Build AMDGPU with NBIO 4.3 support enabled; missing, renamed, or duplicated macros should surface in `nbio_v4_3.c`, SMU13 power-management files, or generated-header include paths.
- Compare the VF0 through VF3 field layouts against `nbio_4_3_0_offset.h` to confirm register names, order, and repeated VF stride remain synchronized.
- Boot affected hardware and confirm PCIe config exposure remains sane: VF identity/header fields, BARs, capability list, PCIe capability, MSI/MSI-X, vendor-specific capability, AER, ARI, and router fields should decode consistently.
- In SR-IOV configurations, create and remove VFs around VF0 through VF3, bind guest drivers, exercise VF FLR, and verify that VF isolation, config-space access, ARI behavior, mailbox/reset flows, and PF-visible diagnostics remain stable.
- Exercise graphics, compute, and DMA workloads with MSI/MSI-X enabled; lost interrupts, stuck pending bits, or unexpected vector masking can indicate MSI field layout or offset drift.
- Run PCIe reset, suspend/resume, runtime power, ASPM/LTR, and link retraining tests while monitoring link speed/width, completion timeout behavior, DRS/link bandwidth status, and FLR completion.
- Use AER/error-injection or platform diagnostics where available to verify uncorrectable/correctable status, masks, severity fields, header logs, and TLP prefix logs map to expected PCIe errors.
- For ARI-capable configurations, verify function enumeration, next-function values, and function-group controls through PCIe config-space dumps before and after VF lifecycle and reset operations.

## Chunk Notes

- Lines 19907-20402 are the tail of `BIF_CFG_DEV0_EPF0_VF0_0`, starting inside `LINK_CNTL` and completing through `RTR_DATA2`.
- Lines 20403-22024 are complete `BIF_CFG_DEV0_EPF0_VF1_0` and `BIF_CFG_DEV0_EPF0_VF2_0` PCIe VF config-space shift/mask blocks.
- Lines 22025-22328 begin `BIF_CFG_DEV0_EPF0_VF3_0` and end after `PCIE_ADV_ERR_RPT_ENH_CAP_LIST__CAP_ID__SHIFT`; the rest of that register and the following VF3 AER/ARI/router fields continue after this chunk.
