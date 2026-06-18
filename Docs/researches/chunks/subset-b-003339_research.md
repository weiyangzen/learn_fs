# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_sh_mask.h lines 29892-32328

## Purpose

This chunk is a generated AMD NBIO 7.9.0 shift/mask header slice for PCIe/NBIO configuration-space register fields. It is not executable driver code; it exports preprocessor constants that describe bit positions and masks for registers whose addresses live in the matching `nbio_7_9_0_offset.h` header.

The range starts in the tail of the root-complex PCIe 8.0 GT/s per-lane equalization definitions, covers the root-complex ACS, DLF, PCIe 16.0 GT/s PHY, PCIe margining, and PCIe 32.0 GT/s link fields, then moves into the `aid_nbio_nbif0_bif_cfg_dev0_epf0_vf*_bifcfgdecp` PCI configuration-space blocks for virtual functions 0, 1, and the beginning of 2. The range ends mid-block at `BIF_CFG_DEV0_EPF0_VF2_MSIX_CAP_LIST__CAP_ID_MASK`, so the final VF2 MSI-X capability-list field set continues in a later chunk.

## Public Surface

The exported API is macro-only:

- `REGISTER__FIELD__SHIFT` gives the bit offset for a field.
- `REGISTER__FIELD_MASK` gives the raw bit mask for that field.

No functions, structs, enums, storage, or inline helpers are defined here. Consumers combine these masks with AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15` after selecting the corresponding register address from an offset header.

## Register Families Covered

The first root-complex section completes PCIe 8.0 GT/s lane equalization for lane 15 and carries the tail masks for lane 14. The fields describe downstream/upstream transmit presets and receiver preset hints for per-lane link training.

The ACS section defines the enhanced capability-list header plus ACS capability and control bits: source validation, translation blocking, peer-to-peer request/completion redirect, upstream forwarding, P2P egress control, direct translated P2P, enhanced capability reporting, I/O request blocking, downstream/upstream memory target access controls, and unclaimed-request redirect behavior. These fields are isolation and routing controls for PCIe peer traffic.

The DLF section defines the data-link feature enhanced capability list and local/remote DLF support state. It includes the exchange-enable and remote-valid bits used to negotiate PCIe data-link features.

The 16.0 GT/s PHY section defines enhanced-capability header fields, reserved link capability/control dwords, equalization completion/phase/link-request status, parity mismatch status for local/RTM1/RTM2 contexts, and per-lane 16.0 GT/s downstream/upstream transmit presets for lanes 0 through 15.

The PCIe margining section defines the margining enhanced capability list, port capability/status, and per-lane control/status registers for lanes 0 through 15. Each lane has receiver number, margin type, usage model, and margin payload fields, with parallel status fields. These are software-visible controls for link margining diagnostics.

The 32.0 GT/s section defines link capability/control/status fields for equalization bypass, no-equalization-needed behavior, modified training sequence usage modes, equalization phase completion, modified TS receipt, enhanced link behavior control, transmitter precoding state/request, and no-EQ-needed receipt.

The VF0/VF1/VF2 endpoint-function sections mirror standard PCI/PCIe configuration-space layouts for SR-IOV or virtual-function-facing config spaces. For each covered VF, this includes conventional PCI identity and command/status fields, BARs and ROM BAR fields, subsystem IDs, capability pointers, PCIe capability/device/link/device2/link2 status and controls, MSI/MSI-X capability fields, vendor-specific enhanced capability fields, AER status/mask/severity/capability/log fields, ATS capability/control, and ARI capability/control. VF2 coverage stops before the MSI-X capability-list group is complete.

## Important Fields

PCI command/status masks control I/O space, memory space, bus mastering, parity/SERR response, interrupt disable, capability-list presence, abort/error status, and parity detection. These are standard PCI config-space fields but are generated in chip-specific NBIO naming.

PCIe device control fields include correctable, non-fatal, fatal, and unsupported-request reporting enables; relaxed ordering; max payload size; extended tags; phantom functions; auxiliary power PM; no-snoop; max read request size; and FLR initiation. Device status fields expose matching error status, auxiliary power, pending transactions, and emergency power reduction detection.

PCIe link fields include maximum/current link speed, negotiated width, ASPM/PM controls, retrain/link-disable/common-clock/extended-sync controls, clock power management, bandwidth-management interrupts, data-link active reporting, DRS signaling, and 8.0 GT/s equalization status. Link capability 2 and control 2 add target link speed, compliance entry, autonomous speed disable, transmit margin, de-emphasis, lower SKP OS support, RTM presence detect support, crosslink, and DRS support/status.

MSI/MSI-X fields describe enable state, multi-message capability/enables, 64-bit support, per-vector masking support, extended message data capability/enable, message address/data fields, mask and pending bitmaps, MSI-X table size/function mask/enable, and MSI-X table/PBA BIR and offset fields.

AER fields are extensive. The uncorrectable status/mask/severity groups cover DLP, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast-blocked TLP, AtomicOp egress blocked, TLP prefix blocked, and poisoned TLP egress blocked. Correctable status/mask covers receiver error, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal, correctable internal error, and header-log overflow. AER capability/control includes first-error pointer, ECRC generate/check capability and enables, multi-header record support/enables, TLP prefix log presence, and completion-timeout log capability. Header and TLP prefix log registers are full-width capture dwords.

ATS fields define the enhanced capability header, invalidation queue depth, page-aligned request support, global invalidate support, STU, and ATC enable. ARI fields define the enhanced capability header, MFVC/ACS function-group capabilities, next function number, MFVC/ACS group enables, and ARI function group.

## Control Flow And State

There is no runtime control flow in this header. Use is compile-time substitution:

1. An NBIO 7.9 translation unit includes `nbio/nbio_7_9_0_offset.h` and `nbio/nbio_7_9_0_sh_mask.h`.
2. Driver code selects a register address from the offset header.
3. Driver code reads or prepares a raw register value.
4. The relevant `*_MASK` and `*_SHIFT` macros decode, test, clear, or compose fields.

The header itself stores no state and has no persistence behavior. Persistent or semi-persistent state lives in hardware: PCIe config registers, VF BAR/MSI/MSI-X/ATS/ARI configuration, AER masks and logs, ACS routing controls, link equalization/margining controls, and link status registers. Some fields are configuration state programmed by firmware, the kernel PCI core, or AMDGPU; others are live status bits, hardware-owned logs, write-one-to-clear error status, or training/margining handshakes.

## Dependencies And Integration Points

The immediate dependency is the generated AMD register-header convention. This `_sh_mask` header supplies bit layouts; `nbio_7_9_0_offset.h` supplies addresses such as the root-complex ACS, margining, 32.0 GT/s link, and VF0/VF1/VF2 configuration-space registers. Default-value headers from nearby NBIO generations show the same generated family pattern, but this chunk should be reconciled against the NBIO 7.9.0 offsets for exact address pairing.

The NBIO 7.9 generation is included by `amdgpu/nbio_v7_9.c` and `ras/ras_mgr/amdgpu_ras_nbio_v7_9.c`. Direct handwritten use of the specific macro names in this chunk was not found outside generated register headers in the inspected tree, which means these fields are primarily part of the chip register ABI and may be used indirectly by generic register dumps, generated tooling, or future NBIO/RAS/PCIe feature code.

Semantic dependencies come from PCI, PCI Express, AER, ACS, ATS, ARI, MSI/MSI-X, SR-IOV/VF configuration-space behavior, and AMD NBIO hardware specifications. Correct behavior also depends on the kernel PCI core, AMDGPU's SOC15 register access paths, firmware-provided PCIe setup, and hardware link-training/error-reporting side effects.

## Risks And Maintenance Notes

- This file is generated and highly repetitive. A single bad shift or mask can silently decode or program the wrong hardware bit.
- The chunk boundaries are partial: it begins after earlier lane-14 equalization fields and ends before VF2 MSI-X capability-list completion. Merge-time reconciliation must include adjacent chunks.
- VF0, VF1, and VF2 groups are structurally similar but not interchangeable at the register-address level. Copying masks across VF address blocks without the matching offset can target the wrong VF.
- PCIe ACS, ATS, ARI, and AER fields affect isolation, IOMMU/translation behavior, error containment, and peer-to-peer routing. Incorrect masks can create security or reliability issues in SR-IOV and peer-memory scenarios.
- Link equalization, margining, and 32.0 GT/s controls are hardware-sensitive. Writing control bits outside the expected link-training or diagnostic flow can destabilize the PCIe link.
- AER status, mask, severity, and log fields have side effects and ordering rules that the macros do not express. Callers must know which bits are write-one-to-clear, sticky, hardware-owned, or log-capture fields.
- Full-width and high-bit masks such as `0xFFFFFFFFL` and `0x80000000L` should remain in unsigned register-value paths to avoid signedness or truncation bugs.
- Similar NBIO generations expose near-identical names with subtle differences in field presence and offsets. Version-specific includes must not be mixed.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage for NBIO 7.9 AMDGPU and RAS files that include `nbio_7_9_0_sh_mask.h`.
- Static generated-header checks that every `*_SHIFT` has a matching aligned `*_MASK`, repeated lane/VF groups are complete within their intended ranges, and masks do not overlap unexpectedly inside a register.
- Cross-header checks that every register family named in this chunk has a matching `cfg*` or `reg*` address in `nbio_7_9_0_offset.h`.
- Runtime PCIe register dumps on NBIO 7.9 hardware comparing decoded command/status, PCIe capability, link capability/status, MSI/MSI-X, AER, ATS, and ARI fields against `lspci -vvxxx` and AMDGPU debug output.
- SR-IOV validation that VF0/VF1/VF2 config-space fields decode independently and that BAR, MSI/MSI-X, AER, ATS, and ARI state does not bleed across VFs.
- Link-training diagnostics that verify 8.0/16.0/32.0 GT/s equalization status and per-lane preset fields after speed changes.
- PCIe margining diagnostics that toggle lane margining controls through supported software paths and observe matching lane status payloads.
- Error-injection or platform RAS tests that exercise AER correctable/uncorrectable status, mask, severity, and header/TLP-prefix log decode without clearing or misclassifying unrelated bits.
