# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 80273-82592

## Purpose

This chunk is part of the generated AMDGPU NBIO 7.7.0 register shift/mask header. It does not contain executable code; it publishes C preprocessor constants that describe bit positions and pre-shifted masks for PCIe port registers in the NBIO PCIe directory address blocks.

The range begins in the `BIFP2_0_PCIEP_STRAP_LC` definitions, completes the rest of the `BIFP2_0` PCIe-port control, link-controller, transmit-credit, and flow-control groups, covers the full `nbio_pcie0_bifp3_pciedir_p` address block, and starts `nbio_pcie0_bifp4_pciedir_p` through `BIFP4_0_PCIE_RX_CNTL`. These blocks describe repeated PCIe port instances, so most field layouts are repeated with different `BIFP2_0`, `BIFP3_0`, and `BIFP4_0` prefixes.

These constants are intended to be used with the paired NBIO offset definitions and AMDGPU register helpers, including `RREG32_SOC15`, `WREG32_SOC15`, PCIe-index/data helpers, and bitfield helpers such as `REG_GET_FIELD` and `REG_SET_FIELD`.

## Macro API Surface

The only API surface in this span is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask already positioned in the register word.

Important groups in this chunk:

- `BIFP2_0_PCIEP_STRAP_LC`, `STRAP_MISC`, and `STRAP_LC2`: strap-derived link configuration fields, including FTS/count timing, lane reversal, lane negotiation, compliance behavior, automatic speed negotiation disable bits for 16 GT/s and 32 GT/s, software margining ownership, RTM presence support, E2E-prefix/extended-format/OBFF/LTR/CCIX support, and ESM calibration timing.
- `BIFP2_0_PCIE_LC_L1_PM_SUBSTATE*`: L1.1/L1.2 override controls, power-on timing, FCH target address fields, CLKREQ/refclk behavior, LTR threshold fields, wake/block/abort behavior, and other L1 substate entry/exit controls.
- `BIFP2_0_PCIEP_BCH_ECC_CNTL`: BCH ECC enable, error threshold, and error-status fields for PCIe-port protection logic.
- `BIFP2_0_PCIE_LC_CNTL8` through `LC_CNTL12`, `LC_SPEED_CNTL2`, `LC_FORCE_COEFF2/3`, `LC_FORCE_EQ_REQ_COEFF2/3`, `LC_FINE_GRAIN_CLK_GATE_OVERRIDES`, and `LC_SAVE_RESTORE_*`: link-controller equalization, loopback, ESM, FAAE, preset, PHY rate, recovery, retraining, clock-gating, and save/restore controls.
- `BIFP2_0_PCIE_TX_*`: transmit sequence/replay controls, ACK latency limits, FCU thresholds, vendor/NOP DLLP data, request-number controls, advertised and initialized posted/non-posted/completion credits, and credit error/current-status bits.
- `BIFP2_0_PCIE_FC_*` and `_VC1`: flow-control credit fields for posted, non-posted, and completion traffic on VC0 and VC1.
- `BIFP3_0_PCIEP_RESERVED`, `SCRATCH`, `PORT_CNTL`, `TX_REQUESTER_ID`, `P_PORT_LANE_STATUS`, `ERR_CNTL`, `RX_CNTL`, `RX_EXPECTED_SEQNUM`, `RX_VENDOR_SPECIFIC`, `RX_CNTL3`, `RX_CREDITS_ALLOCATED_*`, `PCIEP_ERROR_INJECT_*`, and `PCIEP_NAK_COUNTER`: the BIFP3 port management, requester identity, lane status, error policy, receive policy, credit accounting, physical/transaction error injection, and NAK counter register fields.
- `BIFP3_0_PCIE_LC_CNTL` through `LC_LINK_MANAGEMENT_MASK`: the BIFP3 link-controller fields for wake behavior, lane activity, block/unblock, link training, lane-width negotiation, N_FTS timing, speed changes, link states, bandwidth-change handling, CDR, equalization, presets, ESM, clock-gating, and event masks.
- `BIFP3_0_PCIEP_STRAP_*`, `LC_L1_PM_SUBSTATE*`, `PCIEP_BCH_ECC_CNTL`, `LC_CNTL8` through `LC_SPEED_CNTL2`, and the BIFP3 TX/FC groups: a full repetition of the same BIFP2 strap, L1 substate, ECC, link-controller, transmit-credit, and flow-control surfaces for the BIFP3 port instance.
- `BIFP4_0_PCIEP_RESERVED`, `SCRATCH`, `PORT_CNTL`, `TX_REQUESTER_ID`, `P_PORT_LANE_STATUS`, `ERR_CNTL`, and `RX_CNTL`: the start of the BIFP4 PCIe-port block, covering port enable/PME/hotplug/completion policy, requester IDs, lane reversal/link width, error reporting/injection controls, and receive-side error filtering/timeout/DPC controls.

There are no functions, structs, enums, variables, or storage declarations in this line range.

## Control Flow and Data Flow

This header supplies compile-time metadata only. It has no branches, loops, calls, allocation, locking, or runtime data flow by itself.

The runtime pattern is implemented by AMDGPU NBIO and PCIe code that includes this generated header:

1. Include the offset header to get a register address and this shift/mask header to get field layout.
2. Read a PCIe-port or NBIO register through the correct MMIO/config accessor.
3. Extract fields by applying `<FIELD>_MASK` and `<FIELD>__SHIFT`, often through `REG_GET_FIELD`.
4. Modify one or more fields with mask/shift arithmetic or `REG_SET_FIELD`.
5. Write the updated register value back while preserving unrelated bits.

For this chunk specifically, the repeated `BIFP2_0`, `BIFP3_0`, and `BIFP4_0` prefixes are the port-instance selector encoded in the macro name. Consumers must combine the matching prefix from this header with the matching address macro from the NBIO 7.7.0 offset header. Mixing a `BIFP3_0` mask with a `BIFP4_0` address would usually compile, because these are plain macros, but would make the code semantically wrong.

## State and Persistence Behavior

The macros hold no state. The underlying hardware registers described by the macros do hold port and link state until reset, link retraining, firmware/SMU intervention, hot reset, FLR, or driver writes change them.

Stateful surfaces in this chunk include:

- Strap fields: describe latched platform or fuse/strap policy for link negotiation, lane reversal, capability advertisement, RTM support, ESM support, CCIX support, and margining ownership.
- Link-controller fields: control or reflect link training, speed negotiation, lane-width negotiation, equalization, loopback, recovery, CDR, FAAE, ESM, power management, and link-management events.
- L1 substate fields: affect low-power entry/exit timing, CLKREQ/refclk behavior, LTR thresholds, FCH copy target addresses, and L1.1/L1.2 powerdown behavior.
- Error and receive-control fields: decide whether specific malformed, unsupported, poisoned, PASID, prefix, timeout, ECRC/LCRC, DPC, and UR conditions are ignored, reported, injected, or converted into containment behavior.
- Credit and flow-control fields: expose or program transmit credit advertisement, initialization, FCU thresholds, current credit status, and allocated receive credits for posted, non-posted, and completion traffic.
- Error-injection fields: can intentionally perturb physical or transaction-layer behavior for diagnostics and validation.

Some status fields may be clear-on-write, write-one-to-clear, sticky-until-reset, or side-effectful according to the hardware register specification. This generated header does not encode those access rules; callers must know them from the register documentation or surrounding driver conventions.

## Dependencies and Integration Points

This file is generated AMD register metadata and depends on convention rather than C types:

- The matching address constants live in the NBIO 7.7.0 offset/header set, especially the corresponding `nbio_7_7_0_offset.h` address definitions.
- `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c` includes this header for NBIO 7.7.0 register programming.
- Generic AMDGPU register helpers provide the actual read/modify/write behavior; this header only supplies masks and shifts.
- PCIe core behavior is external to this file. Fields mirror PCIe concepts such as ASPM/L1 substates, PME, requester IDs, posted/non-posted/completion credits, completion timeouts, AER-like error policy, DPC, PASID/prefix handling, lane equalization, margining, and advertised link speeds.
- The `BIFP2_0`, `BIFP3_0`, and `BIFP4_0` names must stay synchronized with generated hardware address blocks and any ASIC register tables used by the driver.

## Risks and Edge Cases

- Because these are untyped preprocessor constants, the compiler cannot prevent use of a mask with the wrong port instance or wrong register address.
- Several field names contain repeated `MASK_MASK` wording, such as link-management mask fields. That appears to be generated naming for fields whose hardware names already include `MASK`; consumers should not "simplify" those names manually.
- Link training, equalization, ESM, lane-width, and speed-control fields are high-risk to modify. Bad values can cause link downtraining, failed retraining, intermittent PCIe errors, or a lost device.
- Error-ignore and error-injection fields are especially sensitive. Enabling ignores can hide real data-path faults; enabling injection outside validation paths can create artificial link failures.
- L1 substate and CLKREQ/refclk timing fields interact with platform power management. Incorrect settings can cause resume latency, wake failures, or instability around ASPM/L1.2 transitions.
- Credit and flow-control fields affect PCIe throughput and deadlock/timeout behavior. Width errors or stale generated masks can lead to overflowed fields or misprogrammed credit counts.
- This generated header is large and repetitive, so manual edits are risky. The safer maintenance path is to regenerate from the authoritative register database and review diffs for prefix/address-block alignment.

## Test Signals

Useful validation signals for consumers of this chunk:

- Build coverage: the kernel or AMDGPU module must compile with `nbio_v7_7.c` and any code referencing these macros, catching renamed or missing generated symbols.
- Static checks: validate that every `*_MASK` matches its declared shift and field width, and that BIFP2/BIFP3/BIFP4 address prefixes are used consistently with matching offset macros.
- Runtime smoke tests: boot an affected ASIC, confirm GPU enumeration, BAR setup, interrupts, doorbells, and normal graphics/compute workloads.
- PCIe link tests: inspect negotiated speed/width, retraining behavior, ASPM/L1 substate transitions, bandwidth-change notifications, and resume from runtime/system suspend.
- Error-path tests: exercise AER/DPC/reporting paths and confirm that injected physical/transaction errors are used only under controlled validation and produce expected counters/status changes.
- Credit/flow-control tests: stress DMA and peer/host traffic while monitoring completion timeouts, NAK counters, replay behavior, and credit-status error bits.
- Regeneration tests: compare this generated section against the authoritative NBIO 7.7.0 register source to ensure field names, shifts, masks, and address-block boundaries remain synchronized.
