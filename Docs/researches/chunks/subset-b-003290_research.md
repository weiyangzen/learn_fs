# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 75599-77966

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.7.0 shift/mask register-layout header. It defines C preprocessor constants for bit positions and masks in PCIe link-root and PCIe-port register blocks. The paired register addresses and base-index constants are in `nbio_7_7_0_offset.h`; this file only describes how to decode or compose fields after a caller has selected the correct register offset.

The requested range starts in the middle of `BIFPLR4_0_PCIE_ESM_CAP_7`, continues through the rest of the `BIFPLR4_0` enhanced PCIe link/root capability area, then switches at `addressBlock: nbio_pcie0_bifp0_pciedir_p` into the `BIFP0_0` PCIe port/direct block. Near the end it switches again at `addressBlock: nbio_pcie0_bifp1_pciedir_p` and begins the equivalent `BIFP1_0` port block. It ends partway through `BIFP1_0_PCIE_RX_CNTL`, so the last register group is incomplete in this chunk.

At a high level, the range covers:

- PCIe enhanced speed-mode capability, Data Link Feature capability/status, 16 GT/s and 32 GT/s link capability/control/status, lane equalization, lane margining, CCIX/ESM capability, and 20/25 GT/s ESM equalization fields in `BIFPLR4_0`.
- `BIFP0_0` PCIe port control, requester ID, lane status, error control, RX behavior, RX credit allocation, error injection, link-controller training/speed/width/power/equalization controls, strap-derived capability controls, save/restore controls, TX sequence/replay/credit controls, and advertised flow-control credit fields.
- The beginning of the same port-control surface for `BIFP1_0`, including scratch/reserved, port control, requester ID, lane status, error control, and only the first few `PCIE_RX_CNTL` fields before the chunk boundary.

## Important APIs, Types, And Functions

There are no functions, structs, classes, enums, or callable APIs in this chunk. The exported interface is the generated macro namespace:

- `BIFPLR4_0_<REGISTER>__<FIELD>__SHIFT` and `BIFPLR4_0_<REGISTER>__<FIELD>_MASK`.
- `BIFP0_0_<REGISTER>__<FIELD>__SHIFT` and `BIFP0_0_<REGISTER>__<FIELD>_MASK`.
- `BIFP1_0_<REGISTER>__<FIELD>__SHIFT` and `BIFP1_0_<REGISTER>__<FIELD>_MASK`.

The chunk contains 2,167 `#define` entries. Most fields appear as a pair of `__SHIFT` and `_MASK` macros. Several logical register groups repeat per lane or per port, so consumers must use the register prefix as part of the hardware identity, not just the field suffix. For example, `BIFPLR4_0_LANE_0_EQUALIZATION_CNTL_16GT`, `BIFPLR4_0_ESM_LANE_0_EQUALIZATION_CNTL_20GT`, `BIFPLR4_0_ESM_LANE_0_EQUALIZATION_CNTL_25GT`, and `BIFP0_0_PCIE_LC_FORCE_COEFF*` all describe different equalization-related control surfaces.

The important macro groups in this chunk are:

- `BIFPLR4_0_PCIE_ESM_CAP_7`: final ESM-capability bitmap bits in this chunk, covering `ESM_25P0G` through `ESM_28P0G`.
- `BIFPLR4_0_PCIE_DLF_ENH_CAP_LIST`, `DATA_LINK_FEATURE_CAP`, and `DATA_LINK_FEATURE_STATUS`: enhanced-capability header fields plus local/remote Data Link Feature support and exchange-enable/valid bits.
- `BIFPLR4_0_PCIE_PHY_16GT_ENH_CAP_LIST`, `LINK_CAP_16GT`, `LINK_CNTL_16GT`, `LINK_STATUS_16GT`, parity mismatch status registers, and per-lane `LANE_<0-15>_EQUALIZATION_CNTL_16GT`.
- `BIFPLR4_0_PCIE_MARGINING_ENH_CAP_LIST`, `MARGINING_PORT_CAP`, `MARGINING_PORT_STATUS`, and per-lane `LANE_<0-15>_MARGINING_LANE_CNTL/STATUS`.
- `BIFPLR4_0_PCIE_CCIX_*`: CCIX capability-list, headers, capability bits, required/optional ESM capability, ESM status/control, translation capability/control, and 20/25 GT/s ESM lane equalization controls.
- `BIFPLR4_0_LINK_CAP_32GT`, `LINK_CNTL_32GT`, and `LINK_STATUS_32GT`: 32 GT/s capability/control/status fields including supported link speed vectors, retimer presence detection, equalization phases, modified compliance receive, lower SKP OS, and lane equalization request.
- `BIFP0_0_PCIEP_PORT_CNTL`, `PCIE_TX_REQUESTER_ID`, `PCIE_P_PORT_LANE_STATUS`, `PCIE_ERR_CNTL`, `PCIE_RX_CNTL`, `PCIE_RX_CNTL3`, and RX credit/error-injection groups.
- `BIFP0_0_PCIE_LC_*`: the largest part of the chunk, defining link-controller state, training, width, speed, power-management, equalization, save/restore, link-management mask, and clock-gating fields.
- `BIFP0_0_PCIE_TX_*` and `BIFP0_0_PCIE_FC_*`: transmit sequence/replay/ack latency, TX credit thresholds/advertisement/initialization/status, outstanding NP request limit, DLLP send controls, and VC0/VC1 advertised flow-control credit fields.
- `BIFP1_0_PCIEP_*` and early `BIFP1_0_PCIE_*`: the beginning of the second PCIe port direct block.

## Control Flow

This header has no executable control flow. Runtime behavior comes from driver code that includes this generated register map, chooses NBIO 7.7.0 for the detected ASIC, uses the paired offset header to identify an MMIO or indexed-register address, and applies these masks/shifts to decode or update fields.

Typical consumer flow is:

1. Select a register address from `nbio_7_7_0_offset.h`, such as `regBIFPLR4_0_DATA_LINK_FEATURE_CAP`, `regBIFP0_0_PCIE_LC_SPEED_CNTL`, or `regBIFP1_0_PCIEP_PORT_CNTL`.
2. Read the register through the AMDGPU NBIO/register-access path for the selected base index.
3. Extract fields with `value & *_MASK`, shifted by the matching `*__SHIFT`.
4. For writable control registers, preserve unrelated and reserved bits, insert shifted field values, and write the register back through the same register-access path.

The hardware flows represented by the fields include PCIe data-link feature negotiation, 16/20/25/32 GT/s equalization and ESM negotiation, CCIX-related enhanced capability reporting, PCIe lane margining commands/status, LTSSM/link training, link width and speed changes, ASPM/L1 substate power entry/exit, receiver detection, retimer and SRIS handling, error reporting and error injection, TX replay/ack timing, and flow-control credit advertisement.

## State And Persistence

The header itself is stateless and persists no data. It is compile-time metadata that maps field names to bit positions and masks.

The state described by the macros lives in NBIO/PCIe hardware registers. Capability and strap-derived fields such as ESM support, DLF support, CCIX/translation support, lane margining mode, retimer presence support, advertised generation support, lane negotiation capability, and LTR/OBFF/extended-format support are generally hardware-, strap-, or firmware-defined inputs. Control fields such as DLF exchange enable, link reset, training controls, target link speed overrides, reconfiguration commands, auto speed-change limits, equalization coefficients, L1 substate overrides, clock-gating overrides, TX credit controls, and error-injection controls are mutable hardware state.

Status and observation fields include remote DLF support validity, equalization phase completion, parity mismatch status, margining ready/status payloads, CCIX/ESM status, link status at 32 GT/s, lane reversal/width, error-control halt status, RX expected sequence, LC state snapshots, bandwidth-change reasons, speed-change status, save/restore done/acknowledge, TX sequence/replay counters, and TX credit error/current status. These may be live, latched, sticky, or write-one-to-clear depending on the register's hardware semantics; the generated masks do not encode that policy.

Persistence across events is owned by hardware and higher-level driver code, not by this header. PCIe reset, GPU reset, FLR, hot reset, suspend/resume, runtime power transitions, and link retraining can reset or alter many of these registers. Save/restore fields in `BIFP0_0_PCIE_LC_SAVE_RESTORE_1/2` expose a hardware mechanism for link-controller data save/restore, but this chunk only defines its control and data bitfields.

## Dependencies And Integration Points

The immediate dependency is the matching NBIO 7.7.0 offset header. For example, `BIFP0_0_PCIE_LC_SPEED_CNTL__LC_CURRENT_DATA_RATE_MASK` is meaningful only when paired with `regBIFP0_0_PCIE_LC_SPEED_CNTL` and its base index. The same pairing requirement applies to `BIFPLR4_0_*`, `BIFP0_0_*`, and `BIFP1_0_*` names.

Integration points include:

- AMDGPU NBIO 7.7.0 ASIC support that includes generated `asic_reg/nbio` headers.
- PCIe link-management paths that inspect or program LTSSM state, link width, advertised/current/target speed, reconfiguration commands, retrain/speed-change reasons, ESM settings, equalization coefficients, retimer/SRIS flags, and safe-recovery behavior.
- PCIe power-management paths that use ASPM, L0s/L1/L23, L1 substate, CLKREQ/refclk, lane powerdown, and receiver-idle controls.
- Debug and diagnostics code that decodes `PCIE_LC_STATE0` through `PCIE_LC_STATE5`, bandwidth-change status, timeout/illegal-state fields, lane corruption masks, parity mismatch registers, TX replay/sequence counters, and TX credit status.
- PCIe capability or compliance tooling that examines Data Link Feature, 16 GT/s PHY, 32 GT/s link, lane margining, CCIX, and translation capability fields.
- RAS/error-handling and validation paths that use `PCIE_ERR_CNTL`, RX ignore/timeout/NAK controls, physical/transaction error injection, BCH ECC status, and TX credit error bits.
- Register dump tools that need stable field names for interpreting NBIO 7.7.0 PCIe port state.

The `BIFP0_0` and `BIFP1_0` blocks are separate PCIe port/direct address blocks. Their field names are intentionally parallel, but the register offsets differ. Code that abstracts across ports must select the correct prefix and offset pair together.

## Risks

The main risk is silent hardware misprogramming if a mask or shift is stale, wrong, or combined with an offset from the wrong ASIC or wrong port block. A single bit error in this range could misreport link speed, force an unintended speed change, alter equalization behavior, suppress error handling, inject a physical or transaction error, corrupt flow-control credit advertisement, or change L1/CLKREQ/refclk behavior.

This chunk has important boundary hazards. It starts after the first `BIFPLR4_0_PCIE_ESM_CAP_7` shift definitions, so adjacent preceding lines are needed for the complete register group. It ends after only three `BIFP1_0_PCIE_RX_CNTL` shift definitions (`RX_IGNORE_IO_ERR`, `RX_IGNORE_BE_ERR`, and `RX_IGNORE_MSG_ERR`); the rest of `BIFP1_0_PCIE_RX_CNTL` is outside the requested range. Any merged per-file research or generator audit must reconcile these adjacent chunks before treating either boundary register as complete.

Many fields are low-level link-controller controls rather than ordinary PCI config fields. Driver writes to `LC_RESET_LINK`, `LC_RECONFIG_NOW`, `LC_GO_TO_RECOVERY`, `LC_INITIATE_LINK_SPEED_CHANGE`, equalization coefficient force fields, L1 substate override fields, error-injection fields, or TX replay/credit controls can disrupt the live PCIe link. Consumers should use read-modify-write with reserved-bit preservation and should avoid writes unless the hardware programming sequence is known.

Generated field names with repeated words can be easy to misuse. `BIFP0_0_PCIE_LC_LINK_MANAGEMENT_MASK__..._MASK_MASK` is mechanically correct because both the register and field names include `MASK`, but code review should check that such names refer to interrupt/event mask bits and not data masks. Similarly, `*_STATUS`, `*_CNTL`, `*_CAP`, `*_STRAP_*`, and `*_SAVE_RESTORE_*` encode different semantics even though each compiles as an integer constant.

The repeated lane and generation suffixes are another copy/paste risk. `LANE_<n>_EQUALIZATION_CNTL_16GT`, `ESM_LANE_<n>_EQUALIZATION_CNTL_20GT`, `ESM_LANE_<n>_EQUALIZATION_CNTL_25GT`, `LC_FORCE_COEFF`, `LC_FORCE_COEFF2`, and `LC_FORCE_COEFF3` target related but distinct speed/equalization mechanisms.

The generated masks do not identify access type, reset defaults, atomicity requirements, clear-on-read/write-one-to-clear behavior, synchronization with firmware, or required waits between control writes and status polling. Those constraints must come from the NBIO hardware specification and from existing AMDGPU programming sequences.

## Test Signals

Useful validation signals are hardware- and integration-facing:

- The AMDGPU tree builds with NBIO 7.7.0 headers included, proving the generated macro names referenced by code resolve.
- Static generator checks confirm that complete register groups in this chunk have matching `regBIFPLR4_0_*`, `regBIFP0_0_*`, or `regBIFP1_0_*` offset/base-index definitions in `nbio_7_7_0_offset.h`.
- Register-dump tooling on matching hardware decodes plausible DLF, 16 GT/s PHY, 32 GT/s link, CCIX, ESM, lane margining, port control, requester ID, lane-width/reversal, RX/TX, and flow-control credit fields.
- PCIe link tests observe expected current/advertised/target speeds, negotiated width, LTSSM state, bandwidth-change reasons, speed-change attempt status, and equalization phase/status bits across boot, retrain, hot reset, and GPU reset.
- Power-management tests cover ASPM/L1/L1.1/L1.2 entry and exit, CLKREQ/refclk behavior, wake from L23/L1SS, and suspend/resume restoration of writable controls.
- Error-path tests or controlled hardware validation exercise physical/transaction error injection, RX ignore/timeout/NAK controls, BCH ECC status, TX replay counters, and TX credit error/current status without leaving the link wedged.
- Margining and equalization diagnostics verify per-lane control/status symmetry for lanes 0-15 and confirm that 16/20/25/32 GT/s generation-specific fields are decoded against the right register groups.
- Multi-port tests confirm that `BIFP0_0` and `BIFP1_0` decode independently and that shared helper code never pairs a port-0 mask with a port-1 offset or vice versa.
