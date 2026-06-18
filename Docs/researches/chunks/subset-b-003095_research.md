# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 66206-68539

## Scope

This chunk covers generated NBIO 7.0 PCIe register shift/mask definitions for AMDGPU. The range starts inside the `BIFP0_PCIE_RX_CREDITS_ALLOCATED_P` family, continues through the rest of the BIFP0 PCIe-port field map, covers the complete BIFP1 PCIe-port field map, and then covers the start of BIFP2 through the first four shift definitions of `BIFP2_PCIEP_ERROR_INJECT_PHYSICAL`.

The requested range contains 2,181 `#define` lines: 1,092 `__SHIFT` macros and 1,089 `_MASK` macros across 148 register groups. It is purely a generated hardware bitfield header. There are no C functions, structs, enums, variables, includes, allocation paths, locks, or executable control flow in this slice.

## Purpose

The header provides the bit-level ABI between AMDGPU NBIO/PCIe code and NBIO 7.0 hardware registers. Each field is represented with the generated convention:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset for composing or extracting the field.
- `<REGISTER>__<FIELD>_MASK`, the field mask used with the shift value.

The matching address side is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_offset.h`; reset/default values are in `nbio_7_0_default.h`. Runtime code combines those register offsets and these field constants through AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

Although this source path is under a local `ceph-client` mirror, this chunk is AMD GPU PCIe/NBIO register metadata and does not implement Ceph or distributed filesystem behavior.

## Important Macro Families

### BIFP0 Tail

The BIFP0 portion begins with the end of receive credit allocation:

- `BIFP0_PCIE_RX_CREDITS_ALLOCATED_NP` and `_CPL` expose allocated non-posted and completion data/header credits.
- `BIFP0_PCIEP_ERROR_INJECT_PHYSICAL` exposes physical-layer fault injection fields for lane errors, framing errors, bad SKP parity/LFSR, loopback underflow/overflow, deskew errors, 8b/10b errors, SKP ordered-set errors, invalid ordered-set identifiers, and bad sync headers.
- `BIFP0_PCIEP_ERROR_INJECT_TRANSACTION` exposes transaction/link-layer fault injection for flow-control errors, replay-number rollover, bad DLLP/TLP, unsupported request, ECRC, malformed TLP, unexpected completion, completer abort, and completion timeout.
- `BIFP0_PCIEP_NAK_COUNTER` tracks received and generated NAK counts.
- `BIFP0_PCIEP_RX_CAPTURED_LTR_CTRL_STATUS` and `_THRESHOLD_VALUES` expose captured LTR interrupt/status masks and snoop/non-snoop threshold value, scale, and requirement bits.

Most of the BIFP0 coverage is link-controller state:

- `BIFP0_PCIE_LC_CNTL`, `_TRAINING_CNTL`, `_LINK_WIDTH_CNTL`, `_N_FTS_CNTL`, and `_SPEED_CNTL` define controls for link reset, L0s/L1/L23 behavior, receiver idle handling, link training, power state, renegotiation, upconfiguration, dynamic lane power, target/current data rate, software/hardware speed changes, and failed speed-change status.
- `BIFP0_PCIE_LC_STATE0` through `_STATE5` provide packed link-training state fields such as current/previous/next states, timeout state, receiver-detect state, exit-to-PU state, and substate indicators.
- `BIFP0_PCIE_LINK_MANAGEMENT_CNTL2`, `_STATUS`, `_MASK`, and `_CNTL` describe link-management events and interrupts for data-rate, link-width, autonomous bandwidth, bandwidth-management, and target-speed-change conditions.
- `BIFP0_PCIE_LC_CNTL2` through `_CNTL7`, `_BW_CHANGE_CNTL`, `_CDR_CNTL`, `_LANE_CNTL`, `_FORCE_COEFF`, `_BEST_EQ_SETTINGS`, and `_FORCE_EQ_REQ_COEFF` cover equalization, coefficient forcing, directed speed changes, receiver-detect timing, lane reversal, lane disable/turnoff behavior, CDR controls, FOM/phase observation, Gen3 equalization knobs, and test/debug behavior.
- `BIFP0_PCIE_LC_L1_PM_SUBSTATE` and `_SUBSTATE2` expose L1.1/L1.2, T-power-on, common-mode restore, PHY powerup, and related PCIe L1 PM substate controls.

The BIFP0 tail also includes strap and miscellaneous port-side fields:

- `BIFP0_PCIEP_STRAP_LC` and `_STRAP_MISC` describe hardware strap-derived defaults for FTS/TSx counts, SKP interval, receiver-detect bypass, compliance, lane reversal, lane negotiation, E2E prefix, OBFF, and LTR support.
- `BIFP0_PCIE_LC_PORT_ORDER` records port ordering.
- `BIFP0_PCIEP_BCH_ECC_CNTL`, `_HPGI_PRIVATE`, `_HPGI`, `_HCNT_DESCRIPTOR`, and `_PERF_CNTL_COUNT_TXCLK` define BCH/ECC selection, high-priority/general interrupt-style fields, descriptor fields, and a TXCLK performance-count control.

### BIFP1 Complete Port Map

The BIFP1 block starts at `addressBlock: nbio_pcie0_bifp1_pciedir_p` and is complete inside this range. Its early groups define port-local scratch and transmit/receive datapath fields:

- `BIFP1_PCIEP_RESERVED`, `_SCRATCH`, and `_PORT_CNTL` provide reserved/scratch storage and port controls such as client-independent reset, HOLD training flags, link reset, hot-reset generation, bridge enable, end-of-chain, ECRC enable, and transition-to-recovery behavior.
- `BIFP1_PCIE_TX_CNTL`, `_REQUESTER_ID`, `_VENDOR_SPECIFIC`, `_REQUEST_NUM_CNTL`, `_SEQ`, `_REPLAY`, and `_ACK_LATENCY_LIMIT` define TX error handling, packet generation options, replay/sequence state, requester ID, vendor-specific TX data, and ACK latency limits.
- `BIFP1_PCIE_TX_CREDITS_ADVT_*`, `_INIT_*`, `_STATUS`, and `_FCU_THRESHOLD` describe advertised/initial posted, non-posted, and completion credits plus credit error/current-status flags and FCU thresholds for VC0/VC1.
- `BIFP1_PCIE_P_PORT_LANE_STATUS` exposes lane reversal and PHY link width.
- `BIFP1_PCIE_FC_P`, `_FC_NP`, and `_FC_CPL` expose posted, non-posted, and completion flow-control credits.
- `BIFP1_PCIE_ERR_CNTL` defines error reporting disable, first-error logging strap, ECRC drop/generation controls, LCRC generation controls, AER header log timeout, slave-buffer halt status/reset, immediate error-message sending, and poisoned advisory-nonfatal behavior.
- `BIFP1_PCIE_RX_CNTL`, `_EXPECTED_SEQNUM`, `_VENDOR_SPECIFIC`, `_CNTL3`, and `RX_CREDITS_ALLOCATED_*` define RX ignore/NAK/timeout/TPH/PASID behavior, expected sequence number, vendor-specific RX data/status, root-complex PASID unsupported-request handling, and allocated RX credits.

BIFP1 then repeats the same physical error injection, transaction error injection, NAK counter, LTR capture, LC control, LC state, link-management, strap, L1 PM substate, ECC/HPGI/descriptor, and TXCLK performance-count families described above for BIFP0, but with `BIFP1_` register names. Because the BIFP1 address block is complete in this chunk, it is the most self-contained part of the slice.

### BIFP2 Start

The BIFP2 portion starts at `addressBlock: nbio_pcie0_bifp2_pciedir_p` and covers the same early port, TX, credit, FC, error, and RX families as BIFP1:

- `BIFP2_PCIEP_RESERVED`, `_SCRATCH`, `_PORT_CNTL`.
- `BIFP2_PCIE_TX_*` requester, vendor-specific, request-number, sequence, replay, ACK latency, advertised/init credit, credit status, and FCU threshold groups.
- `BIFP2_PCIE_P_PORT_LANE_STATUS`, `PCIE_FC_P`, `PCIE_FC_NP`, and `PCIE_FC_CPL`.
- `BIFP2_PCIE_ERR_CNTL`, `PCIE_RX_CNTL`, `PCIE_RX_EXPECTED_SEQNUM`, `PCIE_RX_VENDOR_SPECIFIC`, `PCIE_RX_CNTL3`, and `PCIE_RX_CREDITS_ALLOCATED_*`.

The chunk ends at lines 68535-68539 after only the first four `BIFP2_PCIEP_ERROR_INJECT_PHYSICAL` shift definitions. The remaining BIFP2 physical error injection masks and later BIFP2 LC/link-management families belong to the next chunk.

## Control Flow

There is no runtime control flow in this header. It influences control flow indirectly because compiled AMDGPU code uses these constants to compose and decode 32-bit MMIO values. The driver supplies all sequencing: PCIe/NBIO initialization, link training, speed and width changes, reset handling, error injection, interrupt mask/status processing, power-state transitions, and diagnostic polling.

Important command-like fields represented here include `LC_RESET_LINK`, `LC_RECONFIG_NOW`, `LC_RENEGOTIATE_EN`, `LC_INITIATE_LINK_SPEED_CHANGE`, `LC_CLR_FAILED_SPD_CHANGE_CNT`, hot-reset generation, error-injection fields, HPGI status/enable/clear-style fields, and link-management interrupt masks. The macros do not say whether a bit is read-only, sticky, write-one-to-clear, self-clearing, strap-derived, or strobe-like; that behavior is defined by hardware and consuming AMDGPU code.

## State And Persistence Behavior

This chunk stores no software state. It describes hardware-backed PCIe/NBIO state for three port instances:

- Link controller configuration and status: reset state, training state, L0s/L1/L23 behavior, link width, negotiated/current speed, renegotiation/upconfiguration support, lane power state, receiver-detect behavior, CDR, equalization, and coefficient forcing.
- Transaction and data-path state: TX/RX credits, flow-control credits, sequence/replay counters, ACK latency limit, requester ID, vendor-specific data/status, expected sequence number, NAK counters, and RX ignore/timeout policies.
- Error and diagnostic state: AER/ECRC/LCRC controls, error reporting disable, error injection controls, link-management status/mask bits, FOM/equalization observation, and BCH/ECC selection.
- Power-management capability/state: LTR capture and thresholds, L1 PM substate controls, strap-derived LTR/OBFF/prefix support, PHY powerup/common-mode restore timing, and transition-to-L0s/L1 controls.
- Port identity and wiring state: lane reversal, lane negotiation, PHY link width, port ordering, bridge/end-of-chain controls, and strap-derived defaults.

Persistence is hardware-defined. Configuration fields generally persist until reset, power gating, reinitialization, or a later driver write. Status counters, link-state fields, captured LTR status, error status, and training/equalization observations can change asynchronously as the PCIe link trains, retrains, enters low-power states, encounters errors, or is reset.

## Dependencies And Integration Points

The direct dependencies are the generated NBIO 7.0 register headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_offset.h` supplies matching register offsets for these field names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_default.h` supplies reset/default values for many of the same register families.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_smn.h` supplies SMN-side addresses used by NBIO code outside the normal per-register offset tables.

Primary integration is through AMDGPU NBIO and PCIe helpers. `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c` includes the NBIO 7.0 generated headers and is the ASIC-specific integration point for doorbells, interrupt handling, memory-controller access, SR-IOV-related NBIO state, and PCIe/NBIO register programming. Broader AMDGPU PCIe and power-management paths may use the `PCIE_LC_*`, `PCIE_LINK_MANAGEMENT_*`, `PCIE_RX/TX_*`, and `PCIEP_STRAP_*` fields to validate link capabilities, force or observe speed/width changes, handle error status, and coordinate low-power states.

The BIFP0/BIFP1/BIFP2 duplication is intentional: each port instance has a separate register namespace with similar field layouts. Consumers must pair the right `BIFP<n>` mask constants with the matching `BIFP<n>` offsets; cross-instance mixups can compile cleanly while touching the wrong port.

## Risks And Edge Cases

- Bitfield drift is high impact. A wrong shift or mask can write unrelated PCIe/NBIO fields and cause link-training failures, surprise retrains, incorrect speed/width negotiation, broken low-power entry/exit, lost interrupts, or GPU hangs.
- Repeated port blocks are mechanically fragile. BIFP0, BIFP1, and BIFP2 share many names and layouts, but chunk boundaries are not aligned with complete port families; BIFP0 starts mid-credit group and BIFP2 ends mid-error-injection group.
- Error-injection fields should not be treated as normal error handling. Accidentally enabling physical or transaction error injection can create artificial PCIe faults.
- Link speed/width and equalization controls are sequencing-sensitive. `LC_INITIATE_LINK_SPEED_CHANGE`, target speed overrides, coefficient forcing, CDR settings, receiver-detect controls, and upconfiguration fields must be used only with the correct training and polling sequence.
- RX error-ignore fields can mask real PCIe problems. Overbroad use of `RX_IGNORE_*`, completion timeout disables, PASID unsupported-request ignore bits, or TPH disable can hide protocol errors or change observable fault handling.
- Strap fields describe hardware-derived policy and capability defaults. Treating strap-derived support bits as freely writable runtime policy can desynchronize software assumptions from fused or board-level configuration.
- LTR and L1 PM substate fields affect platform power behavior. Wrong threshold, scale, common-mode restore, PHY powerup, or L1.1/L1.2 settings can produce latency, wake, suspend/resume, or interoperability failures.
- Counters and status fields may be live, sticky, or clear-on-read/write depending on hardware. The generated macro names do not encode those side effects.

## Test And Validation Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU with NBIO 7.0 support enabled; missing or renamed macros should fail in NBIO/PCIe code that includes `nbio_7_0_sh_mask.h`.
- Mechanically compare this shift/mask chunk against AMD's authoritative NBIO 7.0 register database and ensure the same register names exist in `nbio_7_0_offset.h`.
- Verify BIFP instance pairing by checking that BIFP0, BIFP1, and BIFP2 uses reference matching address blocks and do not mix masks from another port instance.
- Exercise PCIe link bring-up, hot reset, GPU reset, suspend/resume, ASPM/L1 PM substates, link retraining, speed changes, and lane-width negotiation on NBIO 7.0 hardware.
- Monitor negotiated link width/speed, link-management status, NAK counters, RX/TX credit status, AER/ECRC/LCRC behavior, and kernel logs for PCIe errors or retraining loops.
- For diagnostics-only paths, validate physical and transaction error-injection programming under controlled tests and confirm that injected errors are reported, masked, or cleared as expected.
- Test LTR/OBFF/prefix/PASID-related behavior where platform support exists, especially around low-power entry/exit and completion timeout handling.

## Cross-Chunk Notes

Adjacent chunks are required for a complete per-file account. The previous chunk owns the beginning of BIFP0 receive-control and posted-credit allocation definitions. The next chunk owns the rest of `BIFP2_PCIEP_ERROR_INJECT_PHYSICAL` plus later BIFP2 LC/link-management/strap/L1 PM fields. The merge lane should avoid treating this document as a complete summary of all BIFP0 or BIFP2 register groups.
