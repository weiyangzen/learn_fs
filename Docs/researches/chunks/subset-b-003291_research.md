# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 77967-80272

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.7.0 shift/mask header. It defines C preprocessor constants for PCIe direct-register bitfields under the NBIO PCIe port blocks `BIFP1_0` and `BIFP2_0`. The constants provide only bit positions and masks; register addresses and base indices are in the paired `nbio_7_7_0_offset.h` header.

The range starts in the middle of `BIFP1_0_PCIE_RX_CNTL`, so the first `RX_IGNORE_*` shift definitions are in the previous chunk while this chunk contains the later shifts and the complete mask set. It then covers the rest of the `BIFP1_0` receive, link-control, link-training, link-status, power-management, equalization, transmit, and flow-control field layouts. At line 79407 it switches to `addressBlock: nbio_pcie0_bifp2_pciedir_p`, repeats the same early PCIe direct-register layout for the `BIFP2_0` port, and ends after the `BIFP2_0_PCIE_LC_LINK_MANAGEMENT_MASK` field masks. The next `BIFP2_0_PCIEP_STRAP_LC` register starts immediately after the requested range and is outside this chunk.

## Major Register Groups

The `BIFP1_0` portion covers PCIe receive-side controls and link-controller state for port 1:

- RX policy and diagnostics: `PCIE_RX_CNTL`, expected sequence number, vendor-specific RX data/status, PASID/ATS-related `PCIE_RX_CNTL3`, posted/non-posted/completion credit allocation, physical-layer and transaction-layer error-injection controls, and NAK counters.
- Link controller controls: `PCIE_LC_CNTL`, training control, link-width control, N-FTS counts, speed control, link-controller state snapshots `LC_STATE0` through `LC_STATE5`, secondary controls, bandwidth-change controls, CDR controls, lane control, and control registers `LC_CNTL3` through `LC_CNTL12`.
- Equalization and high-speed training fields: forced coefficient registers, best equalization settings, forced equalization-request coefficients, second and third coefficient sets, scheduled RXEQ evaluation fields, ESM/retimer/SRIS controls, link-management event mask bits, and safe-recovery controls.
- PCIe low-power and persistence-related fields: `LC_L1_PM_SUBSTATE` through `LC_L1_PM_SUBSTATE5`, L1.1/L1.2 timing, common-mode restore timing, power-on value capture, and L1 PM state tracking.
- Transmit and flow-control fields: TX sequence/replay state, ACK latency limits, FCU thresholds, TX vendor-specific fields, NOP DLLP generation, request-count limits, advertised and initialized credits for P/NP/CPL traffic, credit status, and per-virtual-channel flow-control registers.

The `BIFP2_0` portion begins a second PCIe direct-register port at `nbio_pcie0_bifp2_pciedir_p`. Within this chunk it includes the port reserved/scratch/control fields, requester ID, lane-status, error-control, RX controls and credits, error-injection controls, NAK counters, link-controller controls, link-state snapshots, bandwidth/CDR/lane controls, equalization coefficient controls, SRIS/retimer/ESM fields, and the link-management interrupt/event mask register.

## Important APIs, Types, And Functions

There are no functions, structs, enums, or callable APIs in this header range. Its exported interface is the generated macro namespace:

- `BIFP1_0_<REGISTER>__<FIELD>__SHIFT` and `BIFP2_0_<REGISTER>__<FIELD>__SHIFT` give zero-based bit positions.
- `BIFP1_0_<REGISTER>__<FIELD>_MASK` and `BIFP2_0_<REGISTER>__<FIELD>_MASK` give masks in the containing 32-bit NBIO/PCIe direct register.

The chunk contains 2,187 `#define` entries and 117 register/comment markers. Most logical fields appear as `__SHIFT` and `_MASK` pairs, but the chunk boundaries matter: the first register is partial because `BIFP1_0_PCIE_RX_CNTL` starts before line 77967, and the next `BIFP2_0_PCIEP_STRAP_LC` register begins after line 80272.

AMDGPU's NBIO 7.7 implementation includes this file together with `nbio_7_7_0_offset.h` from `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`. That source uses standard AMDGPU helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, and `REG_SET_FIELD`; those helpers are the runtime API that pairs these shift/mask macros with actual MMIO or PCIe-port register access.

## Control Flow

This header has no executable control flow. Runtime behavior is created by AMDGPU code that selects the NBIO 7.7 register map for a detected ASIC, reads or writes a register through SOC15/NBIO or PCIe-port helpers, and uses these masks and shifts to extract or update individual fields.

Typical consumer flow is:

1. Select the matching register offset, such as `regBIFP1_0_PCIE_LC_SPEED_CNTL` or `regBIFP2_0_PCIE_LC_LINK_MANAGEMENT_MASK`, from `nbio_7_7_0_offset.h`.
2. Read the register through the NBIO/PCIe-port access path. In `nbio_v7_7.c`, the PCIe-port index/data offsets are exposed by `nbio_v7_7_get_pcie_port_index_offset()` and `nbio_v7_7_get_pcie_port_data_offset()`.
3. Decode fields with `value & *_MASK`, shifted by the matching `*__SHIFT`, or update fields through the driver's `REG_SET_FIELD` style macros.
4. For writable control registers, preserve unrelated bits and write the updated value back through the same access path.

The hardware flows represented here include PCIe link training and retraining, speed and width negotiation, SRIS/SRNS behavior, retimer detection, L0s/L1/L1.1/L1.2 power transitions, receive completion timeout policy, credit accounting, TX replay/ACK behavior, flow-control advertisement, error injection, NAK generation/counting, and link-management event masking.

## State And Persistence

The header itself is stateless and persists no data. It is a compile-time description of hardware register layout.

The state described by these macros lives in NBIO PCIe direct registers. Link-controller registers hold live hardware state such as negotiated width, speed, lane reversal, LTSSM/link-controller state, equalization progress, retimer presence, SRIS detection state, and link-management events. RX/TX and flow-control registers hold live protocol state such as expected sequence numbers, NAK counters, replay state, ACK latency limits, posted/non-posted/completion credits, and virtual-channel flow-control values.

Some fields are configuration controls whose lifetime depends on PCIe reset, GPU reset, suspend/resume, and power-gating domains. Examples include ignore/error-mask controls in `PCIE_RX_CNTL`, completion timeout policy, `LC_RESET_LINK`, link-width and speed change controls, forced equalization coefficients, L1 PM timing controls, SRIS/retimer overrides, link-management event masks, error-injection bits, and TX credit/request limits. Other fields are read-only or hardware-updated status observations, but this generated header does not encode access policy, reset defaults, latch behavior, or write-one-to-clear semantics.

## Dependencies And Integration Points

The macros must be paired with the NBIO 7.7.0 offset definitions. The offset header places `BIFP1_0` under `addressBlock: nbio_pcie0_bifp1_pciedir_p` with base address `0x11141000`, and `BIFP2_0` under `addressBlock: nbio_pcie0_bifp2_pciedir_p` with base address `0x11142000`; both use base index 5 for the registers shown here. A shift/mask macro alone is not enough to locate hardware.

Primary integration points include:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which includes this header and the matching offset header for NBIO 7.7 ASIC support.
- AMDGPU SOC15 register helpers and PCIe-port accessors, including `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT`.
- PCIe link-management code that needs speed, width, training, equalization, ESM, SRIS, retimer, safe-recovery, and bandwidth-change fields.
- Power-management and suspend/resume code that programs or restores ASPM/L1/L1-substate timing and power-management behavior.
- RAS, diagnostics, or validation tooling that reads error counters, NAK counters, header/status logs, error-injection controls, and link state snapshots.
- Debug register dump tools that need stable symbolic names for port 1 and port 2 field layouts.

## Risks

The main risk is silent hardware misprogramming if a mask or shift is wrong, stale, or paired with an offset from the wrong port or ASIC revision. A one-bit error can change link reset behavior, disable error reporting, mask completion timeouts, force invalid equalization coefficients, break L1-substate timing, or misdecode link-state diagnostics.

This chunk has two specific boundary hazards. It begins after the start of `BIFP1_0_PCIE_RX_CNTL`, so a standalone analysis of this chunk does not contain every shift for that register. It ends immediately before the `BIFP2_0_PCIEP_STRAP_LC` definitions, so the strap register comment visible after the range is not part of the requested work item.

The `BIFP1_0` and `BIFP2_0` namespaces are structurally similar. Copy/paste errors can compile cleanly while targeting the wrong PCIe port. The same applies to similarly named link-control registers such as `LC_CNTL`, `LC_CNTL2`, `LC_CNTL7`, `LC_CNTL12`, `LC_FORCE_COEFF`, `LC_FORCE_COEFF2`, and `LC_FORCE_COEFF3`.

Several fields intentionally alter low-level PCIe behavior: error injection, receive error ignore policy, NAK generation, link reset, lane enable/reversal, speed-change commands, equalization coefficients, safe-recovery events, and low-power timing. These fields should not be written by generic debug or recovery paths without hardware-specific sequencing, because incorrect writes can drop the link, hide protocol errors, or leave the port in a state that requires reset.

Generated masks named with repeated `MASK` fragments, such as `BIFP*_PCIE_LC_LINK_MANAGEMENT_MASK__LINK_SPEED_UPDATE_MASK_MASK`, are awkward but intentional: the register is itself a mask register and the field name ends in `_MASK`. Consumers must use the exact generated spelling.

## Test Signals

Useful validation signals are hardware- and integration-facing:

- The AMDGPU tree builds with `nbio_v7_7.c` including `nbio_7_7_0_offset.h` and `nbio_7_7_0_sh_mask.h`, proving referenced macro names resolve.
- Static generator checks confirm that every complete `BIFP1_0` and `BIFP2_0` register group in this chunk has a matching `regBIFP1_0_*` or `regBIFP2_0_*` offset/base-index entry in `nbio_7_7_0_offset.h`.
- Register dumps on matching NBIO 7.7 hardware show plausible values for link width, speed, LTSSM/link-controller state, lane reversal, NAK counters, RX/TX credit values, and flow-control advertisements on ports 1 and 2.
- Link retraining, speed-change, width-change, and equalization tests show expected transitions in `LC_STATE*`, `LC_SPEED_CNTL`, `LC_LINK_WIDTH_CNTL`, `LC_BEST_EQ_SETTINGS`, and link-management event fields.
- Suspend/resume and low-power testing verifies ASPM/L1/L1-substate behavior and confirms any writable timing controls are restored by driver code when required.
- Error-injection or RAS validation checks that physical-layer and transaction-layer error-injection fields, receive error ignore bits, NAK counters, and error-control fields produce expected hardware and driver-visible events.
- PCIe stress tests using posted, non-posted, and completion traffic monitor credit allocation/status fields and TX replay/ACK behavior for stalls, underruns, or unexpected completions.
