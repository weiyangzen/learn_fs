# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 94992-97338

## Purpose

This chunk is a generated AMD NBIO 7.2 register shift/mask slice for PCIe BIF port instances. It contains only preprocessor constants that describe bit positions and masks inside NBIO PCIe registers; the matching register offsets live in the companion offset header. The range begins in the tail of the `BIFP3` link-management mask section, covers the end of the `BIFP3` PCIe link-control/equalization/save-restore block, contains a full `addressBlock: nbio_pcie0_bifp4_pciedir_p`, and starts `addressBlock: nbio_pcie0_bifp5_pciedir_p`.

The exported convention is the generated AMD register format:

- `REGISTER__FIELD__SHIFT` gives the field low-bit position.
- `REGISTER__FIELD_MASK` gives the raw 32-bit mask for that field.

This range has 2,347 source lines, 2,177 `#define` statements, 1,085 shift macros, 1,092 mask macros, and 166 register/comment separators. There are no C functions, structs, enums, or executable statements.

## Public Surface In This Chunk

The public surface is macro definitions for hardware field extraction and composition. Consumers normally use these constants through AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_*`, and `WREG32_*`, together with the generated `nbio_7_2_0_offset.h` register address macros.

Important macro families in this chunk are:

- `BIFP3_PCIE_*` tail fields for link-management control/masks, straps, L1 PM substates, hot-plug/general interrupt state, performance counters, 16 GT/s equalization controls, fine-grain clock gating, receiver-detect/equalization controls, and save/restore fields.
- Complete `BIFP4_PCIEP_*` and `BIFP4_PCIE_*` field maps for reserved/scratch/port control, TX/RX control, flow-control credits, CCIX controls, AER/private error controls, physical/transaction error injection, NAK counters, captured LTR thresholds, link controller state machines, speed/width negotiation, equalization, ESM, link-management status/masks, straps, hot-plug status, performance counters, clock-gating overrides, and link-controller save/restore registers.
- Initial `BIFP5_PCIEP_*` and `BIFP5_PCIE_*` field maps through `BIFP5_PCIEP_ERROR_INJECT_PHYSICAL`, mirroring the early `BIFP4` TX/RX, flow-control, CCIX, error-control, and error-injection layout for another PCIe port instance.

## Register Families

The chunk is mostly port-instance repetition. `BIFP3`, `BIFP4`, and `BIFP5` identify separate NBIO PCIe BIF port blocks with nearly identical field layouts, allowing common driver code or generated accessors to apply the same bit operations to different physical ports by selecting the matching register offset and macro family.

`BIFP4_PCIEP_PORT_CNTL` and related `PCIEP_RESERVED`/`SCRATCH` fields expose basic port-level controls such as port-present/private flags, hotplug enablement, CI slave response behavior, atomic operation blocking, and scratch storage. These fields are low-level PCIe-port controls rather than general kernel state.

The TX block includes `PCIE_TX_CNTL`, requester ID, vendor-specific data/status, request number controls, sequence/replay counters, ACK latency limits, NOP DLLP data, skid controls, advertised and initial flow-control credits for posted/non-posted/completion traffic, credit status/thresholds, and CCIX port routing or attribute fields. These macros describe transmit-path behavior and credit accounting for both normal PCIe and CCIX-related operation.

The RX block includes `PCIE_RX_CNTL`, expected sequence number, vendor-specific data/status, `PCIE_RX_CNTL3` root-complex PASID/ATS-related unsupported-request controls, and allocated RX credits. It controls which receive errors may be ignored, completion timeout behavior, TPH disablement, prefix/PASID error filtering, FIFO-full NAK behavior, and flow-control initialization from registers.

Error and diagnostic sections include `PCIE_ERR_CNTL`, `PCIEP_ERROR_INJECT_PHYSICAL`, `PCIEP_ERROR_INJECT_TRANSACTION`, `PCIEP_NAK_COUNTER`, private AER mask/trigger fields, and CCIX miscellaneous unsupported-request status. These support error reporting policy, deliberate LCRC/ECRC/TLP/DLLP error generation, injected physical-layer faults, and counters/status for link diagnostics.

The link controller (`LC`) sections are the largest semantic group. `PCIE_LC_CNTL`, `LC_TRAINING_CNTL`, `LC_LINK_WIDTH_CNTL`, `LC_N_FTS_CNTL`, `LC_SPEED_CNTL`, `LC_STATE0` through `LC_STATE5`, `LINK_MANAGEMENT_CNTL2`, `LC_CNTL2` through `LC_CNTL12`, `LC_BW_CHANGE_CNTL`, `LC_CDR_CNTL`, `LC_LANE_CNTL`, and equalization force/best-setting registers describe PCIe link training, speed changes, lane width negotiation, FTS counts, ASPM/L0s/L1/L23 behavior, receiver detection, lane reversal, equalization phase control, ESM handling, SRIS/autodetect settings, and debug state capture.

`PCIE_LINK_MANAGEMENT_STATUS`, `PCIE_LINK_MANAGEMENT_MASK`, and `PCIE_LINK_MANAGEMENT_CNTL` expose event/status bits for speed, width, bandwidth, power-state, equalization, ESM, and partner-capability changes. The paired status/mask naming is important: status fields report link-management events, while mask fields gate those events.

Strap and power-management sections include `PCIEP_STRAP_LC`, `PCIEP_STRAP_MISC`, `PCIEP_STRAP_LC2`, `PCIE_LC_L1_PM_SUBSTATE`, `PCIE_LC_L1_PM_SUBSTATE2`, and `PCIE_LC_PORT_ORDER`. These macros define hardware strap-derived capabilities and software override fields for lane negotiation, compliance, lane reversal, ESM support, L1.1/L1.2 policy, CLKREQ filtering, power-on timing, LTR thresholds, and port ordering.

Hot-plug and auxiliary blocks include `PCIEP_HPGI_PRIVATE`, `PCIEP_HPGI`, and `PCIEP_HCNT_DESCRIPTOR` for presence-detect, SMI/SCI event enable/status, descriptor slot number, and active-port indication. `PCIEP_BCH_ECC_CNTL` exposes BCH ECC enable, threshold, and status fields. Performance counter macros select/count TXCLK and link-controller events.

`PCIE_LC_SAVE_RESTORE_1`, `_2`, and `_3` define fields used for saving/restoring link-controller state such as EQ settings, link speed, link state, lane reversal, link width, and link-up indication across hardware-managed transitions.

## Control Flow And Data Flow

There is no runtime control flow in this header. The effective data flow is compile-time macro substitution:

1. A driver translation unit includes this shift/mask header and the corresponding NBIO 7.2 offset header.
2. Driver code reads a 32-bit hardware register from the relevant BIF port instance.
3. The code extracts fields with `*_MASK` and `*_SHIFT`, often via `REG_GET_FIELD`.
4. For writable fields, the driver composes a new register value with the same masks/shifts, often via `REG_SET_FIELD`, and writes it back through the AMDGPU register access path.

The macros do not encode read-only/write-only status, clear-on-write behavior, posted write ordering, reset requirements, legal values, link-training sequencing, or whether fields are valid on a given ASIC package or board strap. Those semantics live in the hardware specification and in caller sequencing.

## State And Persistence

The header itself has no state and persists nothing. It describes hardware state stored in NBIO PCIe registers.

Many fields named here represent persistent hardware configuration until a reset, power transition, strap reload, link retrain, or explicit driver write changes them. Examples include link width/speed controls, ASPM and L1 substate overrides, ESM/SRIS policy, credit initialization, error-reporting masks, hot-plug interrupt enables, flow-control thresholds, and save/restore values. Other fields are live status or counters, such as link-up, training states, expected sequence numbers, NAK counters, captured LTR thresholds, AER/private status, and error-injection status. The generated names do not state which status bits are sticky or write-one-to-clear.

## Dependencies And Integration Points

This chunk depends on the generated NBIO register-header contract and on the matching offset definitions for `nbio_7_2_0`. It is consumed by AMDGPU NBIO/PCIe code that programs AMD ASIC register fields for link setup, power management, interrupts, error handling, and diagnostics.

Semantic dependencies include:

- PCI Express link training and status state-machine behavior.
- AMD NBIO PCIe BIF port layout for instances `BIFP3`, `BIFP4`, and `BIFP5`.
- PCIe flow-control credit accounting for posted, non-posted, and completion traffic.
- PCIe AER, ECRC/LCRC, DLLP/TLP, completion timeout, and error-injection behavior.
- ASPM, L0s/L1/L1.1/L1.2, LTR, CLKREQ, and platform power-management policy.
- PCIe 8 GT/s and 16 GT/s equalization, coefficient, preset, FOM, EIEOS, and ESM/SRIS behavior.
- Hot-plug/presence-detect signaling through SMI/SCI/status bits.
- CCIX-related request attributes, target/source IDs, stacked base/limit ranges, and optional header handling.

Because this is a generated header, same-looking fields across `BIFP3`, `BIFP4`, and `BIFP5` should be treated as same-generation port-instance mirrors, not as portable definitions for other NBIO generations.

## Risks And Maintenance Notes

- The chunk starts mid-register: the first visible lines are trailing `BIFP3_PCIE_LINK_MANAGEMENT_MASK` masks whose corresponding shifts are in the previous chunk.
- The chunk ends mid-`BIFP5_PCIEP_ERROR_INJECT_PHYSICAL`; the remaining masks for later physical error-injection fields and the following `BIFP5` sections are in the next chunk.
- Field names containing `MASK_MASK`, such as `PCIE_LINK_MANAGEMENT_MASK__..._MASK_MASK`, are generated names for fields inside a mask register. They are awkward but intentional; manual cleanup could break consumers.
- Link-controller fields are high risk. Wrong masks or writes can force retraining, reset links, change speed/width negotiation, disable equalization, or break ASPM/L1 substate behavior.
- Error-injection fields are diagnostic-only and hazardous outside controlled tests. Accidentally programming them can generate physical-layer, transaction-layer, LCRC/ECRC, DLLP, TLP, unsupported-request, malformed-TLP, or completion-timeout errors.
- Status and mask registers have different semantics despite similar bit layouts. Treating status bits as normal storage can lose events or fail to clear latched hardware state.
- TX/RX credit and flow-control fields can affect PCIe forward progress and throughput. They require hardware-approved values and sequencing.
- CCIX fields overlap PCIe-port control surfaces and may be invalid on systems or ASIC configurations without CCIX support.
- Hot-plug SMI/SCI fields can affect firmware/OS event routing; incorrect programming can hide or spam presence-detect events.
- Generated constants must remain synchronized with the hardware register database. A single stale shift/mask can silently corrupt unrelated fields in a packed 32-bit register.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage for AMDGPU code that includes `nbio_7_2_0_sh_mask.h`.
- Generated-header consistency checks that every visible `REGISTER__FIELD__SHIFT` has the expected companion mask in this chunk or an adjacent chunk when the register is split at a chunk boundary.
- Cross-header checks that every register family in this chunk has a corresponding address macro in `nbio_7_2_0_offset.h`.
- Hardware register dump comparisons on NBIO 7.2 ASICs for `BIFP4` and neighboring port instances, especially link speed/width, LC state, L1 substate, hot-plug, flow-control credit, error-status, and save/restore fields.
- PCIe link retrain, ASPM, L1.1/L1.2, SRIS/ESM, and 8 GT/s or 16 GT/s equalization tests that confirm driver writes use the intended fields.
- Negative/diagnostic tests for error-injection and AER paths in controlled environments, checking that expected status bits and kernel error reports appear.
- Hot-plug or presence-detect tests that validate `HPGI` enable/status behavior where platform wiring supports it.
- Static review of any code touching `*_ERROR_INJECT_*`, `*_LC_RESET_LINK*`, `*_RECONFIG_NOW*`, `*_LINK_SPEED*`, and `*_LINK_WIDTH*` fields, because those writes have direct link-stability impact.
