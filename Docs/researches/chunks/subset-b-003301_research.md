# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 101851-104155

## Purpose

This chunk is an auto-generated AMD NBIO 7.7 register shift/mask slice for PCIe BIF port blocks. It starts at the tail of the `BIFP0_1` receive-credit allocation family, covers most of the `BIFP0_1` PCIe physical/link-control and transmit-flow-control register fields, then begins the `// addressBlock: nbio_pcie1_bifp1_pciedir_p` block and defines the first part of the mirrored `BIFP1_1` port/link-control surface.

The file does not implement executable behavior. Its public contract is a set of C preprocessor constants that encode field bit positions and raw-bit masks for NBIO 7.7 registers. AMDGPU code combines these constants with register offsets from `nbio_7_7_0_offset.h` and helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT`.

## Public Surface In This Chunk

The exported API is entirely macro based:

- `REGISTER__FIELD__SHIFT` defines the low bit for a field.
- `REGISTER__FIELD_MASK` defines the field mask in the unshifted register value.

The `BIFP0_1` portion includes:

- Receive credit allocation/status fields for completion credits and NAK counters.
- Error-injection fields for physical-layer and transaction-layer PCIe faults.
- Link controller control, training, width, speed, state-history, bandwidth-change, CDR, lane, equalization, retimer/SRIS, ESM, link-management interrupt-mask, strap, L1 PM substate, BCH ECC, clock-gating override, save/restore, and speed-change fields.
- 8 GT/s, 16 GT/s, and 32 GT/s coefficient override/request fields, including local/best equalization settings and force-EQ request parameters.
- Transmit sequence/replay, ACK latency, FCU threshold, vendor-specific DLLP, NOP DLLP, outstanding NP request limit, advertised/init/current flow-control credits, and VC1 flow-control credit fields.

The `BIFP1_1` portion begins a second PCIe port/address block. It covers reserved/scratch registers, port controls, requester IDs, lane status, error controls, receive controls, receive sequence/vendor fields, RX PASID/atomic/poison controls, RX credit allocation, error injection, NAK counters, and the start of link-control/training/width/speed/state/control/equalization/strap/L1 substate definitions. This chunk stops inside `BIFP1_1_PCIE_LC_L1_PM_SUBSTATE`; later chunks are needed for the remainder of the `BIFP1_1` PM, ECC, high-speed equalization, and TX/flow-control families.

## Important Register Families

The receive and transmit flow-control families expose the PCIe credit accounting surface for posted, non-posted, and completion traffic. `RX_CREDITS_ALLOCATED_*` and `TX_CREDITS_ADVT_*`/`TX_CREDITS_INIT_*` split data/header credits into low and high halfwords. `TX_CREDITS_STATUS` exposes per-credit-type error and current-status bits, while `PCIE_FC_*` and `PCIE_FC_*_VC1` expose current or advertised credits for VC0/VC1. These definitions matter for diagnosing stalls, credit exhaustion, and virtual-channel behavior.

The error-injection and replay families are a hardware validation/debug surface. `PCIEP_ERROR_INJECT_PHYSICAL` can target lane, framing, SKP parity/LFSR, loopback underflow/overflow, deskew, 8b/10b disparity/decode, ordered-set, and sync-header errors. `PCIEP_ERROR_INJECT_TRANSACTION` covers flow-control errors, replay rollover, bad DLLP/TLP, unsupported request, ECRC, malformed TLP, unexpected completion, completer abort, and completion timeout. `PCIE_TX_REPLAY`, `PCIE_TX_SEQ`, and `PCIE_TX_ACK_LATENCY_LIMIT` expose sequence, replay, timer, ACK latency, and replay-disable/stall controls.

The link-control families are the largest part of the chunk. `PCIE_LC_CNTL`, `PCIE_LC_TRAINING_CNTL`, `PCIE_LC_LINK_WIDTH_CNTL`, `PCIE_LC_N_FTS_CNTL`, `PCIE_LC_SPEED_CNTL`, and `PCIE_LC_SPEED_CNTL2` define how software or straps can control link reset, L0s/L1/L23 behavior, training enablement, receiver behavior during speed changes/tests, negotiated/current width, dynamic lane power state, upconfigure/reconfigure support, advertised and target speeds from Gen2 through Gen5, N_FTS/EIE handling, and explicit speed-change initiation/forcing/deferral.

The state and diagnostic families (`PCIE_LC_STATE0` through `PCIE_LC_STATE5`, `PCIE_LC_CNTL2`, `PCIE_LC_BW_CHANGE_CNTL`, `PCIE_LC_CDR_CNTL`, and `PCIE_LC_LANE_CNTL`) expose the LTSSM current/previous-state history, timeout and illegal-state flags, electrical-idle handling, powerdown permissions, bandwidth-change sources/failures, CDR test controls, and corrupted-lane masks. These fields are key for link training failures or runtime width/speed changes.

The equalization families cover high-speed PCIe link tuning. `PCIE_LC_CNTL3` through `PCIE_LC_CNTL12`, `PCIE_LC_FORCE_COEFF`, `PCIE_LC_BEST_EQ_SETTINGS`, `PCIE_LC_FORCE_EQ_REQ_COEFF`, and their 16 GT/s and 32 GT/s variants expose local presets, pre/cursor/post cursor values, figures of merit, requested FS/LF values, TX swing, safe recovery, loopback EQ, default preset override, no-EQ/high-rate behavior, precoding controls, live deskew, EQ request phase handling, and recovery interactions. This is a sensitive surface because incorrect field use can destabilize a PCIe link.

The power-management and low-power families include L1 substate controls, LTR threshold fields, T_POWER_ON values and FCH target-address fields, common-mode restore timing, CLKREQ/reference-clock behavior, L1.1/L1.2 powerdown controls, and L1SS abort/exit behavior. `PCIE_LC_CNTL6` and `PCIE_LC_CNTL7` also expose SRIS/SRNS, retimer presence, ESM PLL/init state, scheduled RX equalization evaluation, and link-management event masking. These fields integrate PCIe link management with board clocking, retimers, and platform power policy.

The strap families (`PCIEP_STRAP_LC`, `PCIEP_STRAP_MISC`, and `PCIEP_STRAP_LC2`) expose fuse/strap-derived or strap-like capability controls for FTS/TS counts, skip interval, receiver-detect bypass, compliance mode, lane reversal, auto speed negotiation disables for 16/32 GT/s, lane negotiation width, software margining, RTM presence, E2E prefix, extended format, OBFF, LTR, CCIX, and ESM support/timing. Software should treat these as capability and policy inputs unless the hardware programming guide says writes are supported.

The `BIFP1_1` opening block mirrors much of the same surface for the second port, but starts earlier in the port directory. `PCIEP_PORT_CNTL` controls slave-port request enablement, snoop override, hotplug/PME/power-fault behavior, completion static allocation, private max completion payload size, poisoned unsupported-request mode, and completion payload size mode. `PCIE_TX_REQUESTER_ID` carries normal and SWUS requester IDs. `PCIE_RX_CNTL` and `PCIE_RX_CNTL3` expose error-ignore policy, NAK behavior, completion timeouts, prefix/PASID/TPH handling, DPC private triggers, enhanced atomic enablement, and poisoned-ingress/egress handling.

## Control Flow And State

There is no runtime control flow in this header. The effective flow is compile-time substitution:

1. An AMDGPU translation unit includes `nbio_7_7_0_sh_mask.h`.
2. The caller selects a matching register address from `nbio_7_7_0_offset.h`.
3. The caller reads, writes, or modifies the register through SOC15 or PCIe-port accessors.
4. The caller applies the generated `*_MASK` and `*_SHIFT` macros directly or through `REG_GET_FIELD`/`REG_SET_FIELD`.

The header has no C state and persists nothing by itself. Persistent and dynamic state lives in the GPU's NBIO PCIe registers. Some fields are strap/capability snapshots, some are live hardware state, some are sticky error/status bits, and some are side-effectful controls. Examples in this chunk include link reset and speed-change initiators, error-injection triggers, replay/timer controls, L1 substate powerdown controls, interrupt masks, credit error bits, NAK counters, LTSSM history fields, FCH target address fields, and vendor/NOP DLLP send bits.

## Dependencies And Integration Points

This chunk depends on AMD's generated register-header convention. The `_sh_mask` header supplies field layout; `nbio_7_7_0_offset.h` supplies matching `regBIFP0_1_*` and `regBIFP1_1_*` addresses and base indices. Spot checks show the covered registers are in base index 5, with `BIFP0_1` addresses around `0x450080` through `0x4501ab` and `BIFP1_1` addresses starting around `0x450400`.

The direct in-tree consumer for this generated header is `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which includes both `nbio/nbio_7_7_0_offset.h` and `nbio/nbio_7_7_0_sh_mask.h`. That driver registers `nbio_v7_7_funcs` for NBIO IP versions 7.7.0 and 7.7.1 via AMDGPU discovery, and uses generated masks for NBIO initialization, memory-controller access, interrupt handling, doorbell programming, HDP flush offsets, clock gating, and light sleep. The specific `BIFP0_1`/`BIFP1_1` link and flow-control fields in this chunk are mostly a lower-level hardware-facing surface for future code, diagnostics, bring-up, and debug tooling rather than high-level policy code in the current driver.

The semantic dependencies are PCI Express link training, flow-control, replay, virtual-channel, ASPM/L1 substate, retimer/SRIS, equalization, margining/ESM, AER/DPC-style error handling, MSI/PME/hotplug behavior, and AMD NBIO-specific register semantics. The macro names describe bit layout only; they do not encode legal values, reset values, ordering constraints, write-one-to-clear behavior, clock/power domain requirements, privilege restrictions, or whether a field is read-only on a given SKU.

## Risks And Maintenance Notes

- This is generated, repetitive, hardware-specific data. A single bad shift, mask, prefix, or port number can silently decode or program the wrong bit.
- The range starts mid-family and ends mid-family. The preceding chunk is needed for the start of `BIFP0_1` receive-control/credit definitions, and the following chunk is needed for the rest of `BIFP1_1`.
- `BIFP0_1` and `BIFP1_1` are closely mirrored but have distinct register offsets. Copying masks between ports without using the matching offset macro can target the wrong hardware block.
- Many fields are not safe for generic read-modify-write. Link reset, speed change, error injection, replay disable, DLLP send, L1SS powerdown, FCH target address, and status-clear fields may have side effects or sequencing requirements outside this header.
- Link equalization, coefficient forcing, retimer/SRIS, ESM, and Gen5/32 GT/s controls can cause link instability, training failure, or degraded bandwidth if programmed with invalid policy.
- Error-ignore, poisoned-TLP, PASID, atomic, DPC trigger, and AER-private mask fields can affect isolation, containment, and error visibility.
- Flow-control credit and outstanding request fields can affect throughput or deadlock behavior if used incorrectly.
- Full-width and high-bit masks use `L` suffixes. Code should keep using the established AMDGPU `u32` register helpers to avoid signedness or truncation mistakes.

## Test Signals

Useful validation signals for this chunk are:

- Build coverage for AMDGPU files that include `nbio_7_7_0_sh_mask.h`, especially `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`.
- Static generation checks that every `*_SHIFT` macro has its matching `*_MASK`, each mask aligns to its shift and width, and repeated port/lane families are consistent across `BIFP0_1` and `BIFP1_1`.
- Cross-header checks that each register family in this slice has a matching `regBIFP0_1_*` or `regBIFP1_1_*` offset/base-index definition in `nbio_7_7_0_offset.h`.
- Runtime register dumps on NBIO 7.7 hardware comparing decoded link speed/width, LTSSM state history, N_FTS values, L1 substate state, retimer/SRIS status, flow-control credits, NAK counters, requester IDs, and RX/TX credit status against PCIe debug tooling and AMDGPU debugfs/MMIO reads.
- Link-training tests that exercise Gen2 through Gen5 capability advertisement, target-speed override, width renegotiation/upconfigure, safe recovery, loopback EQ, and retimer/SRIS paths without unexpected AER, DPC, or replay errors.
- Power-management tests around ASPM L0s/L1/L1.1/L1.2, CLKREQ/refclk behavior, PME wake, FCH T_POWER_ON copy/target-address fields, and recovery from aborted L1SS entry.
- Error-path and validation tests that inject physical/transaction-layer errors, observe NAK/replay/credit counters, and verify driver error reporting and recovery do not touch unrelated bits.
