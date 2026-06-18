# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 97339-99658

## Scope

This chunk is a generated AMDGPU NBIO 7.2.0 shift/mask header segment. It contains 2,185 `#define` field-layout macros and 133 register-family comments. There are no C functions, structs, enums, variables, locks, allocations, or executable statements in this range.

The range starts in the middle of `BIFP5_PCIEP_ERROR_INJECT_PHYSICAL`, covers the remainder of the BIFP5 PCIe port/link-control field definitions, switches at `addressBlock: nbio_pcie0_bifp6_pciedir_p`, and then covers the beginning and middle of the mechanically similar BIFP6 PCIe port block through `BIFP6_PCIEP_STRAP_LC`. Adjacent chunks are required for a complete view of the opening BIFP5 physical-layer error-injection register and the trailing BIFP6 strap register fields.

## Purpose

`nbio_7_2_0_sh_mask.h` is the bitfield geometry half of AMD's generated NBIO register interface. For each register field it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used when placing or extracting a value.
- `<REGISTER>__<FIELD>_MASK`, the encoded bit mask used to isolate, preserve, clear, or update that field.

This chunk describes PCIe transaction, data-link, physical-link, link-controller, link-management, strap, hot-plug, performance-counter, CCIX, flow-control, error-control, and RX/TX credit fields for BIFP5 and BIFP6 ports. The constants let AMDGPU code decode status or compose writes for NBIO PCIe registers without hard-coding bit positions at call sites.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware metadata and has no direct Ceph or distributed-filesystem behavior.

## Important Macro Families

The BIFP5 section begins with PCIe diagnostic and link-controller state:

- Error injection and counters: `BIFP5_PCIEP_ERROR_INJECT_TRANSACTION` exposes transaction-layer injections such as flow-control, replay rollover, bad DLLP/TLP, unsupported request, ECRC, malformed TLP, unexpected completion, completer abort, and completion timeout; `BIFP5_PCIEP_NAK_COUNTER` counts received/generated NAKs; LTR capture fields expose snoop and non-snoop threshold values/scales.
- AER private and surprise-down controls: `BIFP5_PCIE_AER_PRIV_UNCORRECTABLE_MASK` and `BIFP5_PCIE_AER_PRIV_TRIGGER` define private masking and forced/fake data-link-active transition behavior.
- Link-controller control and training: `BIFP5_PCIE_LC_CNTL`, `LC_TRAINING_CNTL`, `LC_LINK_WIDTH_CNTL`, `LC_N_FTS_CNTL`, and `LC_SPEED_CNTL` define reset, ASPM/L0s/L1 behavior, L2/L3 entry/exit, receiver idle gating, training state control, lane-width renegotiation/upconfiguration, fast-training-sequence counts, Gen2/Gen3/Gen4 straps, target speed override, software/hardware speed-change forcing, current rate, partner support, and speed-change status.
- Link-state history and bandwidth management: `BIFP5_PCIE_LC_STATE0` through `STATE5` expose the current and previous LTSSM states; `BIFP5_PCIE_LINK_MANAGEMENT_CNTL2`, `LC_BW_CHANGE_CNTL`, `LINK_MANAGEMENT_STATUS`, `LINK_MANAGEMENT_MASK`, and `LINK_MANAGEMENT_CNTL` define bandwidth hints, quiesce/equalization requests, link power state, link-up/port-powered-down status, speed/width update events, power-down completion, and event masks.
- Equalization and signal settings: `LC_CNTL3` through `LC_CNTL12`, `LC_FORCE_COEFF`, `LC_BEST_EQ_SETTINGS`, `LC_FORCE_EQ_REQ_COEFF`, `LC_FORCE_COEFF2`, and `LC_FORCE_EQ_REQ_COEFF2` cover deemphasis, hot-plug and recovery controls, Gen3/Gen4 equalization bypass/redo/search behavior, forced presets and cursor coefficients, best FOM/readback fields, retimer presence overrides, preset masks, default preset overrides, RX recover behavior, EIEOS handling, local preset conversion, LSLD status, loopback, and lane/powerdown sequencing quirks.
- Static strap and platform controls: `BIFP5_PCIEP_STRAP_LC`, `STRAP_MISC`, `STRAP_LC2`, `LC_L1_PM_SUBSTATE`, `LC_L1_PM_SUBSTATE2`, `LC_PORT_ORDER`, `PCIEP_BCH_ECC_CNTL`, `PCIEP_HPGI_PRIVATE`, `PCIEP_HPGI`, and `PCIEP_HCNT_DESCRIPTOR` define lane negotiation, reversed lanes, compliance, LTR/OBFF/CCIX support, ESM capability, L1.1/L1.2 override and timing behavior, port ordering, BCH ECC status, hot-plug presence/status/SCI/SMI signaling, and hot-plug descriptor fields.
- Performance and clock gating: `BIFP5_PCIEP_PERF_CNTL_COUNT_TXCLK`, `PCIEP_PERF_CNTL_COUNT_TXCLK_LC`, and `PCIE_LC_FINE_GRAIN_CLK_GATE_OVERRIDES` define TXCLK event counters and link-controller clock-gating override bits.
- Save/restore: `BIFP5_PCIE_LC_SAVE_RESTORE_1` through `_3` expose low-power or reset save/restore state for LC context such as last active link power state, L1 substate, target speed, bandwidth notifications, dynamic lane power state, and speed-change flags.

The BIFP6 section restarts the same PCIe-port pattern at a new generated address block:

- Basic port/TX path: `BIFP6_PCIEP_RESERVED`, `SCRATCH`, `PORT_CNTL`, `PCIE_TX_CNTL`, `TX_REQUESTER_ID`, `TX_VENDOR_SPECIFIC`, `TX_REQUEST_NUM_CNTL`, `TX_SEQ`, `TX_REPLAY`, `TX_ACK_LATENCY_LIMIT`, `TX_NOP_DLLP`, and `TX_SKID_CTRL` define per-port scratch, link/port enables, TX pass/block controls, requester ID encoding, vendor/NOP DLLP injection, outstanding non-posted request limits, replay sequence/timer fields, ACK latency limit override, and skid-credit override.
- Flow-control and credits: `TX_CREDITS_ADVT_*`, `TX_CREDITS_INIT_*`, `TX_CREDITS_STATUS`, `TX_CREDITS_FCU_THRESHOLD`, `PCIE_FC_*`, `PCIE_FC_*_VC1`, and `RX_CREDITS_ALLOCATED_*` define advertised, initialized, allocated, current, error, and FCU threshold credits for posted, non-posted, and completion traffic across VC0 and VC1.
- CCIX and routing: `TX_CCIX_PORT_CNTL0`, `TX_CCIX_PORT_CNTL1`, `PCIE_CCIX_STACKED_BASE`, `PCIE_CCIX_STACKED_LIMIT`, and `PCIE_CCIX_MISC_STATUS` describe CCIX request attributes, target/source IDs, optional header enablement, QoS, stacked address window base/limit, and CCIX unsupported-request error status.
- RX and error behavior: `PCIE_ERR_CNTL`, `PCIE_RX_CNTL`, `RX_EXPECTED_SEQNUM`, `RX_VENDOR_SPECIFIC`, and `RX_CNTL3` define error-reporting disable bits, generated LCRC/ECRC errors, AER header log timeout, slave-buffer halt status/reset, immediate error-message behavior, RX ignore/drop policy for many TLP/CRC/UR/PASID/prefix/completion cases, completion-timeout behavior, TPH disable, and expected sequence number.
- Error injection, NAK, LTR, AER, LC, and link-management registers then repeat the BIFP5 naming and bit layout for BIFP6: physical/transaction error injection, NAK counters, captured LTR thresholds, private AER controls, `LC_CNTL`, `LC_TRAINING_CNTL`, `LC_LINK_WIDTH_CNTL`, `LC_N_FTS_CNTL`, `LC_SPEED_CNTL`, `LC_STATE0` through `STATE5`, `LINK_MANAGEMENT_CNTL2`, `LC_CNTL2` through `LC_CNTL7`, and `LINK_MANAGEMENT_STATUS/MASK/CNTL`.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace. The constants are untyped preprocessor integer literals, mostly with an `L` suffix, and encode only field geometry.

These definitions do not provide register addresses, default values, access width, read/write permissions, reset-domain behavior, write-one-to-clear semantics, firmware ownership, or sequencing requirements. Consumers must combine them with sibling generated address/default metadata and AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, or the NBIO/SMN/PCIe access path appropriate for the target register.

## Control Flow

This header has no local runtime control flow. Runtime flow is external:

1. AMDGPU code selects a BIFP5 or BIFP6 NBIO PCIe register address from companion generated metadata.
2. It reads the register and extracts a status field with these `__SHIFT` and `_MASK` constants, or composes a write while preserving unrelated and reserved bits.
3. The decoded or written value affects PCIe initialization, link training, speed/width changes, L1 substate handling, equalization, error injection, AER handling, flow-control credit management, hot-plug signaling, CCIX behavior, or diagnostics.

The field names imply asynchronous hardware flows outside this header: LTSSM progression and history capture, speed-change attempts, width renegotiation, receiver detect, RX recovery, Gen3/Gen4 equalization, retimer detection, link bandwidth notification, L1.1/L1.2 entry and exit, credit advertisement/allocation, replay/ACK timing, error logging/reporting, hot-plug presence changes, and performance-counter sampling.

## State And Persistence Behavior

The header owns no memory state and persists nothing by itself. It describes hardware-visible state in NBIO PCIe registers. Persistence depends on the GPU reset domain, PCIe hot/warm reset, link reset, power/clock gating, firmware or BIOS programming, suspend/resume restore, and explicit AMDGPU register writes.

Represented state includes writable control bits, strap-latched capability bits, status latches, history fields, event masks, counters, thresholds, forced debug/error-injection controls, equalization presets and coefficients, link power-state fields, save/restore context, flow-control credits, transaction sequence numbers, and hot-plug SCI/SMI status. Several fields are probably live or latched hardware status (`*_STATUS`, `CURRENT_*`, `PREV_STATE*`, `LINK_UP`, `*_DONE`, `*_FAILED`, credit errors, NAK counters), while others are policy or override inputs.

Because these are link-level PCIe fields, stale or incorrect state across suspend/resume, GPU reset, or retraining can affect device reachability and data integrity. The mask definitions alone are not enough to infer reset values or persistence; those properties must come from hardware documentation and sibling generated default/address headers.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.2.0 register database and must remain synchronized with sibling headers:

- `nbio_7_2_0_offset.h` and/or `nbio_7_2_0_smn.h` provide the matching register addresses.
- `nbio_7_2_0_default.h` provides matching reset/default values where generated.
- AMDGPU SOC15/NBIO access code and bitfield helper macros use this header when reading or updating PCIe registers.

Integration points are PCIe bring-up, runtime link management, GPU reset recovery, suspend/resume, ASPM/L1SS policy, bandwidth and speed management, equalization/retimer handling, hot-plug handling, AER and error recovery, CCIX enablement, and hardware diagnostics. The BIFP5 and BIFP6 sections are mechanically repeated port instances, so consumers typically select the relevant port based on ASIC topology.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while causing software to read or write the wrong PCIe bit, leading to failed link training, wrong negotiated width/rate, broken ASPM/L1SS behavior, masked errors, or corrupted diagnostics.
- This chunk starts and ends mid-register-family. The later merge lane must include neighboring chunks before treating `BIFP5_PCIEP_ERROR_INJECT_PHYSICAL` or `BIFP6_PCIEP_STRAP_LC` as complete.
- Many fields are overrides, force bits, clear bits, or injected-error controls. Leaving them set after debug or recovery can create persistent link instability or false error reports.
- Link training, equalization, RX recovery, speed/width renegotiation, and hot-plug changes are asynchronous hardware flows. Polling code must use timeouts and tolerate transient state.
- Some masks include fields named `*_MASK_MASK` because the hardware field itself is a mask. Call sites must distinguish hardware mask fields from the generated C mask suffix.
- BIFP5 and BIFP6 are similar but not necessarily interchangeable. Blind copy/paste between port instances can target the wrong address block or miss port-specific defaults.
- Error-reporting and RX-ignore fields can hide real PCIe protocol failures if programmed too broadly.
- Credit, replay, requester-ID, and sequence-number fields are transaction-critical. Incorrect writes can hang traffic, violate PCIe flow control, or make diagnostics misleading.
- L1 substate, refclk request, clock-gating, and save/restore fields are power-management sensitive and can regress suspend/resume or low-power idle paths.

## Test Signals

- Build AMDGPU with NBIO 7.2.0 support enabled. Compile-time coverage catches missing or renamed generated symbols used by consumers.
- Run generated-header consistency checks: each `__SHIFT` should match a compatible `_MASK`, masks should not overlap unexpectedly within a register, and BIFP5/BIFP6 repeated register families should match where the hardware database says they are equivalent.
- Cross-check every BIFP5 and BIFP6 register family in this range against sibling address and default headers so field layouts map to real registers and expected reset values.
- On supported hardware, validate PCIe cold boot, hot/warm reset, GPU reset, suspend/resume, link retraining, negotiated width/rate, ASPM, L1.1/L1.2, and link bandwidth notification behavior.
- Exercise diagnostic paths where safe: physical/transaction error injection, NAK counters, AER reporting, LTR capture, LTSSM state history, hot-plug presence signaling, performance counters, and link-management event masks.
- For code that writes these fields, inspect register traces to confirm reserved bits are preserved, write-to-clear/status bits are handled correctly, and temporary override or injection bits are restored after use.
