# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 41522-43896

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.4 shift/mask header. It defines C preprocessor constants for bit positions and bit masks in two adjacent hardware register areas:

- The tail of the `nbio_nbif0_bif_cfg_dev0_epf0_vf15_bifcfgdecp` PCI configuration-space image for virtual function 15 (`BIF_CFG_DEV0_EPF0_VF15_0_*`).
- The start and most of the `nbio_pcie0_pswusp0_pciedir_p` / `nbio_pcie0_pciedir` PCIe controller register masks (`PCIEP_*`, `PCIE_TX_*`, `PCIE_RX_*`, `PCIE_LC_*`, and shared `PCIE_*` blocks).

The file contains no executable code. Its purpose is to provide the field-layout contract used by NBIO, PCIe, power-management, and diagnostics code when composing or decoding raw register values. Addresses for the same register names are supplied by `nbio_7_4_offset.h` for config/MMIO-style registers and by `nbio_7_4_0_smn.h` or local `smn*` definitions for SMN-accessed PCIe registers; this header supplies only `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants.

## Major Register Groups

The chunk opens at line 41522 in the middle of `BIF_CFG_DEV0_EPF0_VF15_0_COMMAND`, beginning with the `INT_DIS` shift and then the command masks for I/O access, memory access, bus mastering, special cycles, memory-write-invalidate, palette snoop, parity response, stepping, SERR, fast back-to-back, and interrupt disable. It then covers the rest of VF15's PCI/PCIe configuration layout.

The `BIF_CFG_DEV0_EPF0_VF15_0_*` block includes conventional PCI fields: status bits for interrupt, capability-list presence, parity and abort errors; revision, class, cache-line, latency, header type, BIST, BARs 1-6, subsystem/vendor adapter IDs, ROM BAR, capability pointer, interrupt line, and interrupt pin.

The VF15 PCIe capability fields describe endpoint/device and link capabilities and controls. Notable masks cover maximum payload and read request size, relaxed ordering, no-snoop, FLR, completion timeout controls, ARI forwarding, atomic operation controls, LTR enable, target link speed, enter-compliance controls, hardware autonomous speed disable, de-emphasis, equalization request, current speed/width, slot-clock config, data-link-layer active, link bandwidth status, and 8 GT/s equalization status. The slot capability/control/status 2 register names are present, but in this chunk they are empty placeholders with no field macros.

Interrupt capability fields cover MSI and MSI-X: capability IDs and next pointers, MSI enable, multi-message capability and enable, 64-bit MSI support, per-vector masking support, extended message data capability/enable, message address/data registers, mask/pending registers, MSI-X table/PBA BIR and offsets, function mask, and MSI-X enable.

Enhanced capability fields cover vendor-specific capability headers and payload words, Advanced Error Reporting, ATS, and ARI. AER masks include uncorrectable status/mask/severity bits for data-link protocol, poisoned TLP, flow control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic egress blocked, TLP prefix blocked, and poisoned TLP egress blocked. Correctable AER status/mask fields cover receiver error, bad TLP, bad DLLP, replay rollover, replay timeout, advisory non-fatal, corrected internal error, header-log overflow, and enhanced capability prefix errors. Header log and TLP prefix log registers are full 32-bit fields. ATS exposes invalidation queue depth, page-aligned request support, STU, and ATC enable. ARI exposes MFVC/ACS function group support/enables, function group, and next-function number.

After the VF15 block, the chunk enters `nbio_pcie0_pswusp0_pciedir_p`. This group defines low-level PCIe port and data-link behavior:

- `PCIEP_RESERVED` and `PCIEP_SCRATCH` full-width registers.
- `PCIEP_PORT_CNTL`, including slave port request enable, snoop override, hotplug/PME/power fault controls, bus-master PMI disable, static completion allocation limit, private maximum completion payload size, poisoned unsupported-request mode, and completion payload sizing mode.
- TX controls for lane width, credit scheduling, bad DLLP generation, payload/nullified-byte handling, malformed TLP handling, completion timeout behavior, NAK deferral, N_FTS arbitration, end-to-end ID forcing, and unsupported request generation.
- TX requester ID, vendor-specific messages, request-number limits, sequence/replay tracking, ACK latency limits, NOP DLLP, advertised and initialized P/NP/CPL credits, live credit status, and FCU thresholds.
- Per-lane port status for electrical idle, lane reversal, lane numbers, and link width.
- Flow-control registers for posted, non-posted, and completion header/data credits, including VC1 equivalents.
- Error and RX controls for replay memory size, ECRC controls, flow-control initialization, DLLP ignore/ordering behavior, receiver expected sequence number, vendor-specific routing, RX credit allocation, and physical/transaction error injection.
- SR-IOV private controls and NAK counters.

The `PCIE_LC_*` link-control group describes link training, width, speed, state, equalization, lane, CDR, and L1 power-management behavior. `PCIE_LC_TRAINING_CNTL` has masks for compliance receive, TS1 matching, L0s/L1 training, power state, speed-change initialization, hot-reset quick exit, autonomous change disable, upconfigure disable, hardware link disable, ASPM L1 NAK timers, receive-enable behavior in recovery/test, and equalization request timing. `PCIE_LC_LINK_WIDTH_CNTL`, `PCIE_LC_N_FTS_CNTL`, and `PSWUSP0_PCIE_LC_SPEED_CNTL` expose negotiated/configured link width, lane reversal, N_FTS values for multiple speeds, current data rate, speed-change attempts, and directed speed changes. State registers `PCIE_LC_STATE0` through `PCIE_LC_STATE5` expose LC state-machine counters and status. Later masks cover management controls/status/masks, L1 PM substates, port order, BCH ECC controls, and additional LC control/equalization coefficient registers through `PCIE_LC_FORCE_EQ_REQ_COEFF2`.

The `nbio_pcie0_pciedir` block then covers shared PCIe controller registers: reserved/scratch, NAK counters, `PCIE_CNTL`, `PCIE_CONFIG_CNTL`, TX tracking address/control/status, bandwidth-by-unit-ID, `PCIE_CNTL2`, RX control 2, function and SWUS TX attributes, client-interface control, bus control, LC states 6-11, LC status registers, TX control 3, write-protect-region control, last received/transmitted TLP capture registers, I2C register address/data expansion, hidden config decode enablement, CLKREQB mapping, port-order enable, PHY controls and PHY status/error counters, RX advisory/drop/unsupported-request policy, and SDP control/attribute override registers.

The assigned range ends at line 43896 inside `PCIE_SDP_SWUS_SLV_ATTR_CTRL`. The final three masks present in this chunk are relaxed-ordering and SNR override masks for memory writes, memory reads, and atomics. The `CI_SWUS_SLV_IDO_OVERRIDE_*` masks and the following `PCIE_PERF_COUNT_CNTL` / performance-counter register definitions begin after this chunk and belong to the next work item.

## Important APIs, Types, And Functions

There are no functions, structs, enums, or runtime APIs in this chunk. The public interface is entirely generated preprocessor symbols:

- `REGISTER__FIELD__SHIFT`: zero-based bit offset of a field.
- `REGISTER__FIELD_MASK`: register-width mask with the field bits set.

Consumers typically combine these with AMDGPU helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`, using the matching address macro from `nbio_7_4_offset.h` or `nbio_7_4_0_smn.h`.

The important symbol families in this range are `BIF_CFG_DEV0_EPF0_VF15_0_*` for VF15 PCI configuration decoding, `PCIEP_*` for port-side PCIe pipe/link behavior, `PCIE_TX_*` and `PCIE_RX_*` for transaction/data-link transmit and receive controls, `PCIE_LC_*` / `PSWUSP0_PCIE_LC_*` for link controller training and power states, and shared `PCIE_*` masks for controller control, status, hidden decode, PHY, RX policy, SDP, and TLP capture.

## Control Flow

This header has no runtime control flow. Runtime behavior is created by code that:

1. Selects the NBIO 7.4 register set for an ASIC such as Vega20/Arcturus/Aldebaran-class hardware.
2. Reads a config, MMIO, or SMN PCIe register using the paired address definition.
3. Extracts fields by applying the mask and shift, often through `REG_GET_FIELD`.
4. For writable fields, performs a read-modify-write that preserves unrelated and reserved bits, often through `REG_SET_FIELD`.

The hardware flows described by the fields are substantial even though this chunk is declarative. VF15 fields participate in PCI enumeration, SR-IOV virtual-function capability exposure, interrupt setup, AER logging, ATS enablement, and ARI function routing. The `PCIEP_*`, `PCIE_TX_*`, and `PCIE_RX_*` fields influence credit exchange, sequence/replay behavior, transaction validation, TLP error injection, MSI/PME/vendor message handling, and NAK accounting. The `PCIE_LC_*` fields influence link training, retraining, directed speed change, equalization, lane configuration, L0/L1/L1-substate transitions, and link-management interrupts. The shared `PCIE_*` fields cover hidden configuration register access, controller arbitration, ordering attributes, low-power memory controls, captured TLP diagnostics, PHY error status, and SDP-side requester/completer behavior.

## State And Persistence

The header itself is stateless and persists no data. It is a compile-time description of hardware bit layouts.

The state described by these macros lives in PCI configuration space and NBIO/PCIe hardware registers. Some fields are static or firmware/hardware-populated capability state, such as capability IDs, next pointers, device/link capabilities, MSI/MSI-X capabilities, AER capability metadata, ATS/ARI capabilities, lane capability, flow-control widths, credit-advertisement formats, and port capabilities.

Other fields describe live or sticky status: PCI status errors, PCIe device and link status, AER correctable/uncorrectable status, header and TLP prefix logs, MSI pending bits, link state counters, link-management status bits, NAK counters, credit status, RX/TX last TLP capture registers, PHY overflow/underflow/decode/deskew/symbol-unlock errors, and RX drop/unsupported-request policy effects.

Writable controls persist only as hardware register contents within their reset and power domains. They include PCI command bits, device/link controls, MSI/MSI-X enables and masks, AER masks/severity, ATS/ARI controls, port controls, TX/RX policy controls, link training and speed controls, L1 PM substate controls, hidden decode enables, CLKREQB mapping, PHY behavior, SDP disconnect/TPH/LTR/poison controls, and SWUS slave attribute overrides. This header does not encode reset defaults, access permissions, read side effects, or write-one-to-clear behavior.

## Dependencies And Integration Points

This chunk depends on exact synchronization with the NBIO 7.4 address headers. `nbio_7_4_offset.h` provides matching `cfgBIF_CFG_DEV0_EPF0_VF15_0_*` config offsets, including the command/status/class/BAR/capability/AER/ATS/ARI registers described here. `nbio_7_4_0_smn.h` provides SMN addresses for shared PCIe registers such as `smnPCIE_CNTL2` and `smnPCIE_PERF_COUNT_CNTL`; `nbio_v7_4.c` also defines several local `smnPCIE_LC_*` addresses while including this mask header.

Direct integration points include:

- `amdgpu/nbio_v7_4.c`, which includes `nbio_7_4_offset.h`, `nbio_7_4_sh_mask.h`, and `nbio_7_4_0_smn.h` for NBIO initialization, doorbell setup, PCIe control, RAS-related handling, and link-related programming.
- `pm/swsmu/smu11/arcturus_ppt.c`, `pm/swsmu/smu13/aldebaran_ppt.c`, `pm/swsmu/smu13/smu_v13_0_6_ppt.c`, and `pm/powerplay/hwmgr/vega20_hwmgr.c`, which include the NBIO 7.4 mask header for platform power-management and PCIe link/ESM-related operations.
- Generic AMDGPU PCIe access paths that read and write through `RREG32_PCIE` / `WREG32_PCIE`, plus debug and performance paths in `soc15.c` that use PCIe counter and NAK registers adjacent to this chunk.
- Linux PCI/SR-IOV and device-reset behavior indirectly, because the VF15 config-space masks describe a virtual function's command/status, MSI/MSI-X, AER, ATS, and ARI capability layout.

The repeated register families are part of the ABI between generated register headers and hand-written driver code. A symbol such as `BIF_CFG_DEV0_EPF0_VF15_0_DEVICE_CNTL__MAX_PAYLOAD_SIZE_MASK` is only valid with the corresponding VF15 config offset; similarly, generic `PCIE_LC_*` masks must be paired with the correct NBIO 7.4 SMN/MMIO address for the active PCIe instance.

## Risks

The main risk is silent hardware misprogramming if a generated mask or shift is wrong, truncated, or paired with the wrong offset. A one-bit error can enable the wrong PCI command, decode the wrong link speed/width, mask or clear the wrong AER error, corrupt MSI/MSI-X programming, alter ATS/ARI behavior, or change low-level link-training policy.

Register naming is highly repetitive across virtual functions, lanes, VC credit types, link-controller states, and TX/RX policy registers. Copy-generation mistakes are easy to miss in review because adjacent blocks have nearly identical field names with different prefixes, widths, or state numbers.

Many fields are status or diagnostic registers with hardware-defined side effects. The header does not say whether PCI status, AER status, link-management status, NAK counters, PHY errors, last-TLP captures, MSI pending bits, or RX/TX tracking registers are read-only, sticky, write-one-to-clear, latch-on-read, or destructive-on-read. Consumers must follow the hardware specification and existing driver patterns before writing these fields.

The chunk boundary itself is a risk for research reconciliation: the `PCIE_SDP_SWUS_SLV_ATTR_CTRL` register is incomplete in this item, and `PCIE_PERF_COUNT_CNTL` starts immediately after line 43896. Merge logic should not assume this chunk covers all SDP attribute masks or performance-counter fields.

Access-path mismatch is another practical risk. Some names are config-space offsets (`cfgBIF_CFG_*`), some are NBIO MMIO offsets, and some are SMN addresses. Using the correct mask with the wrong access path can appear to compile while targeting a different register aperture.

## Test Signals

Useful validation signals are hardware-facing and integration-oriented:

- The AMDGPU tree builds with `nbio_7_4_sh_mask.h` included by NBIO and PM code, proving all referenced mask names resolve.
- Generated-header consistency checks confirm every covered `BIF_CFG_DEV0_EPF0_VF15_0_*` register has a matching `cfg*` offset in `nbio_7_4_offset.h`.
- PCI/SR-IOV enumeration on NBIO 7.4 hardware exposes plausible VF15 vendor/device/class, BAR, PCIe, MSI/MSI-X, AER, ATS, and ARI capability data.
- Link diagnostics report expected negotiated speed and width, no unexpected LC training failures, and coherent LC state/status counters across boot, resume, reset, and directed speed-change paths.
- MSI/MSI-X interrupt setup for virtual functions works without lost or misrouted interrupts, including mask and pending behavior where exercised.
- AER/RAS tests or fault-injection paths decode uncorrectable/correctable errors, severity, header logs, and TLP prefix logs consistently with hardware documentation.
- PCIe low-power and power-management testing covers ASPM/L1/L1-substate transitions, CLKREQB mapping, PME/hotplug/power-fault controls, and SDP disconnect behavior.
- PCIe diagnostics that read NAK counters, flow-control credits, last TLP captures, PHY error status, and RX/TX tracking registers produce stable, explainable values and do not regress after suspend/resume or GPU reset.
