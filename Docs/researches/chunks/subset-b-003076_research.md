# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 19638-22048

## Scope

This chunk is a generated AMDGPU NBIO 7.0 shift/mask header segment for PCIe bridge/root-port configuration-space registers. It contains 2,170 `#define` field-layout macros across 239 register comment blocks. There are no C functions, structs, enums, global objects, locks, allocations, branches, or executable statements in this range.

The range starts inside the `BIFPLR2_0` PCIe Advanced Error Reporting area, immediately after the `BIFPLR2_0_PCIE_ROOT_ERR_STATUS__ADV_ERR_INT_MSG_NUM_MASK` definition from the previous register block. It then finishes the tail of the `BIFPLR2_0` enhanced capability chain through Equalization Status Monitoring capabilities. The chunk also introduces the `nbio_pcie0_bifplr3_cfgdecp` address block and covers the beginning of the `BIFPLR3_0` PCI/PCIe bridge configuration register map through the first part of `BIFPLR3_0_PCIE_ESM_CAP_1`. The next chunk is required for the remaining `BIFPLR3_0_PCIE_ESM_CAP_1` masks and later ESM capability registers.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield half of the generated NBIO 7.0 register interface. For each register field, it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the field's starting bit.
- `<REGISTER>__<FIELD>_MASK`, the field's bit mask.

The companion `nbio_7_0_offset.h` supplies matching `cfg*` offsets for these configuration-space registers. Runtime AMDGPU code combines these constants with register access helpers, `REG_GET_FIELD`/`REG_SET_FIELD`-style operations, SOC15/NBIO accessors, and PCIe/NBIO generation code. This source path is under a Ceph mirror, but the content is AMD GPU hardware metadata, not distributed-filesystem logic.

The represented hardware purpose is PCIe root-port and bridge configuration for NBIO 7.0: PCI command/status and bridge window decoding, MSI/MSI mapping, PCIe capability negotiation, advanced error reporting, access control services, multicast, L1 power-management substates, downstream port containment, root-port PIO error reporting, and equalization/status-monitoring capability discovery.

## Important Macro Families

The opening `BIFPLR2_0` portion completes a PCIe capability and enhanced-capability tail:

- AER continuation: `ERR_SRC_ID`, four `TLP_PREFIX_LOG*` registers, and the chunk-leading final `ROOT_ERR_STATUS` mask from the previous block. These fields identify correctable and fatal/nonfatal error sources and preserve logged TLP prefixes.
- Secondary PCIe and link equalization: `PCIE_SECONDARY_ENH_CAP_LIST`, `PCIE_LINK_CNTL3`, `PCIE_LANE_ERROR_STATUS`, and `PCIE_LANE_0_EQUALIZATION_CNTL` through `PCIE_LANE_15_EQUALIZATION_CNTL`. These fields expose Gen3 equalization request/control, lower SKP ordered-set generation, per-lane error status, and downstream/upstream TX/RX preset or hint nibbles.
- ACS: `PCIE_ACS_ENH_CAP_LIST`, `PCIE_ACS_CAP`, and `PCIE_ACS_CNTL`, covering source validation, translation blocking, peer-to-peer request/completion redirect, upstream forwarding, direct translated P2P, and egress-control vector sizing.
- Multicast: `PCIE_MC_ENH_CAP_LIST`, `PCIE_MC_CAP`, `PCIE_MC_CNTL`, address/receive/block/untranslated bitmaps, and overlay BAR fields for multicast group address decoding and blocking policy.
- L1 power-management substates: `PCIE_L1_PM_SUB_CAP`, `PCIE_L1_PM_SUB_CNTL`, and `PCIE_L1_PM_SUB_CNTL2`, including L1.1/L1.2 support and enables, common-mode restore time, power-on scale/value, and T_POWER_ON.
- DPC and RP PIO: DPC capability/control/status/error-source fields plus `PCIE_RP_PIO_STATUS`, `MASK`, `SEVERITY`, `SYSERROR`, `EXCEPTION`, TLP header logs, implementation-specific log, and prefix logs. These fields classify unsupported request, completer abort, and completion-timeout errors across config, I/O, and memory spaces.
- ESM: `PCIE_ESM_CAP_LIST`, ESM headers/status/control, and `PCIE_ESM_CAP_1` through `PCIE_ESM_CAP_7`, where capability bits enumerate supported data-rate points from 8.0 GT/s through 28.0 GT/s in 0.1 increments across multiple registers.

The `BIFPLR3_0` portion begins a parallel bridge/root-port configuration map:

- Conventional PCI bridge config fields: vendor/device ID, command/status, revision/class, cache-line/latency/header/BIST, subordinate/secondary/primary bus numbers, I/O and memory base/limit windows, prefetchable windows, capability pointer, interrupt line/pin, bridge control, and extension bridge control.
- Power management and PCIe capabilities: PMI capability/status/control; PCIe capability, device/link/slot/root capability/control/status, and device/link/slot second-generation capability/control/status registers.
- Interrupt and identity extensions: MSI capability, message control/address/data fields, subsystem IDs, MSI map capability and address fields, vendor-specific enhanced capability headers/data, virtual-channel capability/resource controls for VC0 and VC1, and device serial number fields.
- AER for `BIFPLR3_0`: enhanced capability list, uncorrectable status/mask/severity, correctable status/mask, advanced error capability/control, header logs, root error command/status, source IDs, and TLP prefix logs.
- The same secondary PCIe, lane equalization, ACS, multicast, L1 PM substate, DPC, RP PIO, and ESM capability families seen for `BIFPLR2_0`, ending in the first half of `BIFPLR3_0_PCIE_ESM_CAP_1`.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public contract is the preprocessor macro namespace and its generated naming convention. Consumers use register names and field names to extract or update bits, while the actual address selection comes from `nbio_7_0_offset.h`.

The constants are untyped integer literals, with masks usually carrying an `L` suffix. They encode bit positions only. They do not encode access width, read/write permissions, reset values, write-one-to-clear behavior, polling rules, firmware ownership, side effects, or whether a field is legal to program in a given PCIe link state. Those semantics must come from the PCIe specification, AMD's register database, and the code path performing the hardware access.

## Control Flow

This header segment has no local control flow. Runtime flow is external:

1. NBIO, PCIe, display/resource, power-management, diagnostics, or reset code selects a `BIFPLR2_0` or `BIFPLR3_0` configuration register offset.
2. The caller reads a register, decodes fields with the generated shift/mask constants, or composes a new register value by preserving unrelated bits and inserting field values.
3. The caller writes through the AMDGPU register access path or exposes decoded values through diagnostics.
4. Hardware consumes the values as PCIe configuration state, capability reporting, link equalization state, power-management policy, error-reporting state, DPC/RP PIO status, or ESM capability data.

Typical higher-level flows include NBIO initialization, PCIe bridge capability setup, link-training/equalization observation, AER and DPC error handling, L1 substate policy programming, MSI/MSI-map setup, virtual-channel setup, suspend/resume reinitialization, GPU reset, and register dumps.

## State And Persistence Behavior

The header stores no software state. It names state held in NBIO 7.0 PCIe configuration registers. Persistence is determined by PCIe configuration-space reset semantics, GPU reset domains, function-level reset, hot/warm reset, power management transitions, firmware/SMU initialization, and any driver save/restore path.

Represented state includes bridge decode windows, command/status bits, capability-list links, MSI and MSI-map configuration, PCIe device/link/slot/root capability state, AER status/masks/severity/logs, root error reporting enables, per-lane equalization controls and status, ACS controls, multicast routing policy, L1 PM substate controls, DPC enable/status/trigger/reporting state, RP PIO error masks/severity/syserror/exception bits, and ESM support/control state.

Several fields are not passive storage. AER and DPC status bits may be latched and clear-sensitive; interrupt and root error command bits alter reporting behavior; bridge windows affect transaction routing; ACS and multicast controls affect peer-to-peer and multicast forwarding; L1 substate controls affect link power management; equalization controls interact with PCIe link training; and ESM fields expose link-rate monitoring capability and enablement. The generated masks alone are not enough to infer whether a write is safe.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 7.0 register header set:

- `nbio_7_0_offset.h` supplies matching `cfgBIFPLR2_0_*` and `cfgBIFPLR3_0_*` offsets for the register names in this chunk.
- AMDGPU register helper macros consume the `__SHIFT` and `_MASK` naming convention for field extraction and read-modify-write updates.
- The generated values must remain synchronized with AMD's NBIO 7.0 register database and with equivalent later-generation headers, which carry closely related `BIFPLR2_0`/`BIFPLR3_0` capability maps.

Observed include users in this tree include `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, `drivers/gpu/drm/amd/amdgpu/soc15.c`, `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`, and display resource code that includes NBIO 7.0 offsets. The integration surface is the AMDGPU PCIe/NBIO stack: ASIC bring-up, resource discovery, bus and bridge setup, power management, error handling, diagnostics, and reset recovery.

## Risks And Edge Cases

- The chunk begins and ends mid-register family. `BIFPLR2_0_PCIE_ROOT_ERR_STATUS` starts before this range, and `BIFPLR3_0_PCIE_ESM_CAP_1` continues after it. Final file-level research must reconcile these boundaries.
- Generated shift/mask drift can compile cleanly while decoding or programming the wrong hardware bit. High-risk fields include bridge decode windows, AER clear/status bits, DPC controls, ACS controls, MSI mapping, equalization controls, and L1 substate controls.
- `BIFPLR2_0` and `BIFPLR3_0` families are highly repetitive. A copy/generator error may affect one bridge instance while neighboring instances still look correct.
- Capability-list `NEXT_PTR` fields and overlapping capability/control register offsets must match `nbio_7_0_offset.h`; otherwise capability walking or debug decode can point at the wrong structure.
- Status and clear-sensitive fields need hardware-specific handling. Treating AER, DPC, RP PIO, or bridge status bits as ordinary writable state may drop error evidence or leave stale events latched.
- Link equalization, L1 PM substate, DPC containment, and ESM enable fields are tied to PCIe link state. Writes during training, reset, or low-power transitions can cause link instability or misleading diagnostics.
- ACS, multicast, bridge windows, and MSI mapping affect transaction routing and isolation. Incorrect values can break peer-to-peer paths, DMA routing, interrupts, or virtualization/security boundaries.
- Reserved masks are present for preservation, but driver code should avoid intentionally changing reserved bits unless the hardware programming guide requires a specific sequence.

## Test Signals

- Build AMDGPU configurations that include NBIO 7.0, SOC15, SMU10 power-management includes, and display/resource include paths; this catches missing or renamed generated symbols.
- Run generated-header consistency checks against the authoritative NBIO 7.0 register database: shift/mask non-overlap, mask width, field order, capability-list links, and matching offsets in `nbio_7_0_offset.h`.
- Validate cross-instance consistency between `BIFPLR2_0` and `BIFPLR3_0` where the register families are intended to mirror each other, while allowing legitimate differences in base offsets or conventional bridge fields.
- Runtime tests on affected AMD GPUs should cover PCIe enumeration, negotiated speed/width, Gen3 equalization, L1.1/L1.2 entry and exit, suspend/resume, warm reset, GPU reset, and error recovery.
- AER/DPC/RP PIO validation should inject or observe correctable, nonfatal, fatal, unsupported-request, completer-abort, and completion-timeout paths where supported, confirming status, mask, severity, source-ID, header-log, prefix-log, and root-error reporting behavior.
- Routing tests should verify bridge memory/I/O windows, ACS policy, multicast fields if used, MSI/MSI-map delivery, and VC resource programming.
- ESM diagnostics should confirm that data-rate capability bits, status timing fields, and enable/control fields decode consistently with hardware support and the PCIe link speeds exposed by the platform.
