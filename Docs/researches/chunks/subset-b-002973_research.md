# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 29593-31977

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask header segment. It contains preprocessor constants only: field `__SHIFT` values and `_MASK` values for NBIF/BIF PCIe configuration and port-control registers. There are no C functions, structs, enums, local variables, loops, branches, allocations, locks, or direct register accesses in the range.

The range starts in the middle of `BIF_CFG_DEV0_EPF0_VF13_0_PCIE_UNCORR_ERR_STATUS`, completes the VF13 AER tail, contains complete PCI/PCIe configuration layouts for `BIF_CFG_DEV0_EPF0_VF14_0_*` and `BIF_CFG_DEV0_EPF0_VF15_0_*`, then enters the `nbio_pcie0_pswusp0_pciedir_p` address block and covers PCIe port/link-control register fields through `PCIE_LC_CNTL6`. The next chunk is needed for the continuation after `PCIE_LC_CNTL6`.

Although this file is under the local `ceph-client` source mirror, the content is AMDGPU hardware metadata. It describes GPU NBIO/NBIF PCIe bitfields, not Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header slice is to publish the bit-level ABI for NBIO 4.3.0 PCIe virtual-function configuration space and PSWUSP0 PCIe link-control registers. Companion offset headers provide the register addresses; this file provides the field positions and masks used to extract or compose register values.

The dominant macro patterns are:

- `BIF_CFG_DEV0_EPF0_VF13_0_*`, for the tail of VF13 Advanced Error Reporting and ARI/RTR fields.
- `BIF_CFG_DEV0_EPF0_VF14_0_*` and `BIF_CFG_DEV0_EPF0_VF15_0_*`, for complete SR-IOV virtual-function PCI config-space images.
- `PCIEP_*`, `PSWUSP0_PCIE_*`, `PCIE_RX_*`, and `PCIE_LC_*`, for physical PCIe port, receiver, error injection, link training, equalization, lane, speed, and retimer controls.

Driver code consumes these macros through generated-register helper conventions such as `REG_GET_FIELD`, `REG_SET_FIELD`, raw mask/shift operations, and AMDGPU register access wrappers. The macros are a hardware contract: stale or shifted values can compile cleanly while causing the driver to inspect, mask, or program the wrong bit.

## Important Macro Families

### VF13 AER Tail

The chunk opens in the tail of `BIF_CFG_DEV0_EPF0_VF13_0_PCIE_UNCORR_ERR_STATUS` and then covers `PCIE_UNCORR_ERR_MASK`, `PCIE_UNCORR_ERR_SEVERITY`, `PCIE_CORR_ERR_STATUS`, `PCIE_CORR_ERR_MASK`, `PCIE_ADV_ERR_CAP_CNTL`, four `PCIE_HDR_LOG*` words, four `PCIE_TLP_PREFIX_LOG*` words, ARI enhanced capability/cap/control fields, RTR enhanced capability, and `RTR_DATA1/2`.

These fields model the Advanced Error Reporting status/mask/severity split for DLP, surprise down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal, multicast-blocked, atomic egress blocked, TLP-prefix blocked, and poisoned-egress-blocked errors. The ARI/RTR fields expose alternate routing-ID capability/control and reset/DL-up/FLR/D3hot-D0 timing data. The chunk boundary means VF13's earlier PCI config fields are not complete here.

### VF14 and VF15 PCI Configuration Images

The full `nbio_nbif0_bif_cfg_dev0_epf0_vf14_bifcfgdecp` and `nbio_nbif0_bif_cfg_dev0_epf0_vf15_bifcfgdecp` blocks repeat the same generated layout for virtual functions 14 and 15:

- Standard PCI identity and header fields: vendor ID, device ID, command, status, revision ID, programming interface, subclass, base class, cache line size, latency timer, header type, BIST, six BARs, CardBus CIS pointer, adapter/subsystem ID, ROM BAR, capability pointer, interrupt line/pin, min grant, and max latency.
- PCIe capability fields: capability-list header, PCIe capability, device capability/control/status, link capability/control/status, device capability/control/status 2, link capability/control/status 2.
- Interrupt capability fields: MSI capability list, MSI message control, MSI address low/high, MSI data, extended data, mask, 64-bit data and mask aliases, pending bits, MSI-X capability list, MSI-X message control, table descriptor, and PBA descriptor.
- Vendor-specific and AER extended capability fields: vendor-specific enhanced capability header/data, AER enhanced capability header, uncorrectable and correctable error status/mask/severity, AER capability/control, TLP header logs, and TLP prefix logs.
- ARI and RTR fields: ARI enhanced capability list, ARI capability/control, RTR enhanced capability, and reset/DL-up/FLR/D3hot-D0 timing validity fields.

The VF14 and VF15 layouts should be structurally identical except for the VF number in the macro prefix. This repetition is useful for generated-header validation: fields with the same suffix should carry the same shifts and masks across both VFs unless the hardware database explicitly diverges.

### PSWUSP0 PCIe Port Registers

At `nbio_pcie0_pswusp0_pciedir_p`, the chunk moves from VF config-space images to the physical PCIe port and link-control surface:

- `PCIEP_RESERVED`, `PCIEP_SCRATCH`, and `PCIEP_PORT_CNTL` expose miscellaneous port state and control bits such as power state, hotplug message control, DLLP receive behavior, lane reversal, bridge-side flush behavior, ECRC checking, routing-ID logic, interrupt message selection, and wake masking.
- `PCIE_TX_REQUESTER_ID` exposes function, device, and bus-number fields used to form requester IDs.
- `PCIE_P_PORT_LANE_STATUS` exposes per-lane receive-valid and lane-reversal status.
- `PSWUSP0_PCIE_ERR_CNTL` exposes link-training and error-handling controls, including CRC checking, ECRC skipping, link-down error masking, data-parity masking, poisoned-advisory-nonfatal masking, and AER private masks for bad DLLP/TLP.
- `PSWUSP0_PCIE_RX_CNTL` is a dense receiver-error policy register. It controls whether the receiver ignores IO/BE/message/CRC/config/completion/EP/length/max-payload/TC/unsupported-request/AT/PASID/prefix errors, whether to NAK on FIFO full or generate a NAK, completion-timeout behavior, TPH disablement, FLR timeout handling, CTO masking, RTRC/BFRC swapping, and DPC private trigger behavior.
- `PCIE_RX_EXPECTED_SEQNUM`, `PCIE_RX_VENDOR_SPECIFIC`, `PCIE_RX_CNTL3`, and the three `PCIE_RX_CREDITS_ALLOCATED_*` groups expose expected sequence number, vendor-specific receive state, receiver filtering/poison behavior, tag availability checks, expected sequence number reset, and posted/non-posted/completion credit allocation.
- `PCIEP_ERROR_INJECT_PHYSICAL` and `PCIEP_ERROR_INJECT_TRANSACTION` expose deliberate error-injection controls for physical-layer and transaction-layer testing.
- `PCIEP_NAK_COUNTER` exposes the NAK count field used for link diagnostics.

### Link Controller, Training, Speed, Width, and Equalization

The `PCIE_LC_*` and `PSWUSP0_PCIE_LC_*` groups define the link controller surface:

- `PCIE_LC_CNTL` covers LC enablement, link reversal enablement, hot reset, link disablement, receiver detection, standby and lane-active status, extended sync, lane-count selection, link-status clear, common clock config, ASPM and L1 controls, configured link width, lane-allocated status, ASPM gating while in L0, and directed speed change.
- `PCIE_LC_TRAINING_CNTL` covers training sequencing and timeout policy, including configuration-link timeouts, link-lost detection, deassertion delays, skip-order set behavior, DLLP behavior, electrical idle handling, EIEOS/EIOS behavior, directed/link-down resets, reserved lane selection, and safe mode.
- `PCIE_LC_LINK_WIDTH_CNTL` covers negotiated/configured link width, lane-to-slot selection, link-width read/write controls, renegotiation enablement, upconfigure support, short-reconfigure behavior, reconfiguration arcs, and reversal decisions.
- `PCIE_LC_N_FTS_CNTL` and `PSWUSP0_PCIE_LC_SPEED_CNTL` cover fast-training-sequence counts, lane-change FTS programming, initial speed, current data rate, speed-change command/status, auto-speed-change enablement, equalization search mode, equalization disablement at 8 GT/s, and speed-change failure counters.
- `PCIE_LC_STATE0` through `PCIE_LC_STATE5` expose low-level LTSSM/debug state encodings for link-controller state machines.
- `PSWUSP0_PCIE_LC_CNTL2`, `PCIE_LC_BW_CHANGE_CNTL`, `PCIE_LC_CDR_CNTL`, and `PCIE_LC_LANE_CNTL` expose additional bandwidth-change, receiver-detection, EIEOS, L1 powerdown, auto disable, parity ignore, recovery, quiesce, clock-data-recovery, and per-lane control fields.
- `PCIE_LC_CNTL3`, `PCIE_LC_CNTL4`, `PCIE_LC_CNTL5`, `PCIE_LC_FORCE_COEFF`, `PCIE_LC_BEST_EQ_SETTINGS`, `PCIE_LC_FORCE_EQ_REQ_COEFF`, and the visible start of `PCIE_LC_CNTL6` cover deemphasis, auto speed-change retry policy, hot plug, reconfiguration, equalization coefficients, local presets, forced 8 GT/s coefficient settings, best equalization results, requested coefficient forcing, SRIS/SRNS support, and retimer presence overrides/status.

These fields are timing-sensitive. They do not implement link training themselves, but they define the masks used by runtime code that steers link bring-up, retraining, equalization, speed changes, margin/debug behavior, and error recovery.

## Important APIs, Types, and Functions

This chunk declares no functions, types, or exported C symbols. Its API is the generated macro namespace.

Important consumer-facing field categories are:

- Standard PCI fields such as `*_COMMAND__BUS_MASTER_EN`, `*_COMMAND__MEM_ACCESS_EN`, `*_STATUS__CAP_LIST`, BAR address masks, ROM enable/address fields, and interrupt line/pin fields.
- PCIe device/link fields such as max payload, max read request, relaxed ordering, no-snoop, completion timeout, FLR, ASPM, link retrain, link disable, negotiated speed/width, equalization-complete and phase-success bits, target link speed, and DRS/retimer status.
- MSI/MSI-X fields for vector enablement, masking, pending state, message address/data, table size, function mask, table BIR/offset, and PBA BIR/offset.
- AER fields for correctable/uncorrectable status, masks, severity, first-error pointer, ECRC generation/checking, header logs, and TLP prefix logs.
- ARI/RTR fields for function-group capability/control, next-function number, reset-time validity, DL-up timing, FLR timing, and D3hot-D0 timing.
- Port-level `PCIEP_*`, `PSWUSP0_PCIE_*`, `PCIE_RX_*`, and `PCIE_LC_*` fields for physical port control, receiver error policy, credit accounting, error injection, LTSSM/link training, link width/speed management, equalization, SRIS, and retimers.

The usual integration contract is that the matching `__SHIFT` and `_MASK` names are passed to helper macros or used by hand-coded bit operations. A missing or mismatched pair is a compile-time or generated-header correctness issue; a wrong numeric value is a hardware behavior issue.

## Control Flow

There is no executable control flow in this header chunk. Runtime flow is supplied by AMDGPU code that includes the NBIO 4.3.0 register headers:

1. Code selects an ASIC/IP-version-specific register address from the companion offset header.
2. It selects the field mask and shift from this header.
3. It reads the target register through PCI config, MMIO, SMN, SOC15, or NBIO-specific helpers.
4. It extracts fields or composes a read/modify/write value using `REG_GET_FIELD`, `REG_SET_FIELD`, or equivalent mask/shift logic.
5. Hardware applies the change as PCIe VF capability state, interrupt capability programming, AER policy/logging, ARI/RTR behavior, receiver policy, error injection, link training, speed/width/equalization policy, or retimer/SRIS state.

For the port/link-controller groups, higher-level code must also respect hardware sequencing: link disable/retrain, directed speed changes, coefficient forcing, error injection, and indirect state-machine controls can require ordering, polling, and timeout handling outside this header.

## State and Persistence Behavior

The header itself stores no software state and persists nothing. It describes hardware-backed register fields whose state is controlled by reset, firmware/BIOS setup, PCI enumeration, SR-IOV PF/VF policy, guest or host drivers, power management, link retraining, FLR, hot reset, and error-recovery paths.

For VF14 and VF15, represented state includes PCI command/status, class and BAR presentation, ROM and subsystem IDs, MSI/MSI-X configuration, PCIe device/link controls, AER status/masks/severity/logs, ARI controls, and RTR timing data. Some of these fields are durable configuration until reset or reprogramming; others are read-only capability bits, hardware-updated status bits, sticky diagnostics, or write-one-clear error state depending on PCIe semantics.

For PSWUSP0, represented state includes receiver ignore policies, completion-timeout behavior, NAK and credit accounting, error injection settings, LC training/speed/width controls, LTSSM debug state, equalization coefficients, bandwidth-change controls, lane controls, SRIS/SRNS settings, and retimer presence overrides/status. Many control bits can alter live link behavior immediately. Status fields such as lane-valid, lane-reversal, link-state, equalization results, speed-change failure counters, and retimer presence are hardware-updated.

The header does not encode access permissions or clear semantics. Callers must know whether a field is read-only, read/write, sticky, write-one-clear, self-clearing, reserved, or timing-sensitive from the PCIe specification, AMD's register database, and existing AMDGPU access patterns.

## Dependencies and Integration Points

This chunk depends on the generated NBIO 4.3.0 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h`, which supplies matching register offsets.
- Any NBIO 4.3.0 default-value header generated from the same hardware database.
- AMDGPU register helper conventions such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_*`, `WREG32_*`, `RREG32_PCIE`, `WREG32_PCIE`, SOC15 helpers, and NBIO-specific access wrappers.
- Linux PCI/PCIe, MSI/MSI-X, SR-IOV, AER, ARI, link management, and error-recovery semantics.
- Firmware and platform policy that initially strap or expose VF capabilities, BARs, interrupt capability, link width/speed support, equalization behavior, SRIS mode, and retimer presence.

Important integration surfaces are SR-IOV VF enumeration and reset paths, VF interrupt setup, PCIe AER diagnostics and recovery, link bring-up/retrain paths, ASPM/LTR/power-management policy, PCIe speed-change and equalization code, error-injection diagnostics, and hardware validation tools that inspect generated NBIO register fields.

## Risks and Edge Cases

- The range starts mid-`VF13_0_PCIE_UNCORR_ERR_STATUS` and ends mid-file after `PCIE_LC_CNTL6`; adjacent chunks are needed for complete register-group coverage at both boundaries.
- Generated hardware contract drift is the main risk. A wrong mask or shift can silently program a different field while all C code still compiles.
- VF14 and VF15 are highly repetitive. A copied field with the wrong VF prefix, missing field, or different mask is easy to miss and can affect only one virtual function.
- AER status, mask, and severity groups use nearly identical field names. Mixing them can hide errors, misclassify errors, or clear/inspect the wrong diagnostic bit.
- MSI and MSI-X fields contain encoded address/table/PBA bits and aliasing layout variants. Treating every field as an independent plain address can corrupt vector setup.
- PCI BAR, ROM BAR, and MSI-X table/PBA fields carry type, enable, BIR, and reserved low-bit encodings. Consumers must preserve and interpret those bits according to PCI layout.
- Receiver ignore bits and AER private masks can suppress hardware diagnostics. Setting them to work around one condition can hide real data-link, transaction-layer, PASID, prefix, or timeout failures.
- Error-injection fields should be used only in controlled diagnostic paths. Accidental writes can create artificial physical or transaction-layer failures.
- Link controller fields are timing-sensitive. Incorrect masks for retrain, link disable, directed speed change, width renegotiation, equalization, SRIS, or retimer override fields can cause intermittent link training failures, speed fallback, loss of device reachability, or recovery loops.
- LTSSM/debug state masks are observability aids, not stable software state. Tests should tolerate hardware-updated state changing during reads.
- Literal masks use `L` suffixes and vary across 8-bit, 16-bit, and 32-bit register layouts. Callers should avoid signedness or truncation assumptions.

## Test Signals

Useful validation signals for this chunk are mostly generated-header checks, build coverage, and PCIe hardware behavior:

- Build AMDGPU configurations that include the NBIO 4.3.0 register headers; malformed macro names, missing generated pairs, or include-order breakage should surface at compile time.
- Run generated-header consistency checks: each field should usually have a matching `__SHIFT` and `_MASK`, masks should align with the shift and width, and VF14/VF15 matching suffixes should carry the same numeric values.
- Compare representative fields against `nbio_4_3_0_offset.h`, any matching defaults file, and the source hardware register database, especially chunk-boundary VF13 fields, VF14/VF15 AER/MSI/MSI-X fields, and `PCIE_LC_*` link-control masks.
- Enable enough SR-IOV VFs to exercise VF14 and VF15, enumerate them, bind/unbind guest or host drivers, run VF FLR, and verify config-space fields decode as expected.
- Exercise MSI/MSI-X on VF14/VF15: program vectors, mask/unmask, verify pending bits, and confirm interrupts are delivered and quiesced correctly.
- Use PCIe AER injection or observed error paths to verify correctable and uncorrectable status/mask/severity fields, header logs, and prefix logs decode without disturbing unrelated bits.
- Exercise link retrain, directed speed change, ASPM/L1 paths, equalization, width negotiation, and retimer/SRIS configurations on hardware using this NBIO version. Symptoms of mask drift include speed/width mismatches, equalization phase failures, repeated retraining, link-down recovery loops, or unexpected LTSSM states.
- Validate receiver policy and completion-timeout behavior by checking that expected errors are reported or masked only when the corresponding policy bits are intentionally configured.
- Run controlled error-injection diagnostics for `PCIEP_ERROR_INJECT_PHYSICAL` and `PCIEP_ERROR_INJECT_TRANSACTION`, confirming injected failures are attributable and reversible.
