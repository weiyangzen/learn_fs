# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 46475-48482

## Purpose

This chunk is the final slice of AMDGPU's generated NBIO 7.4 register field mask header. It provides C preprocessor constants for decoding and composing bitfields inside NBIO, BIF, RCC, IOHC, and RAS registers for this ASIC generation. The range is not executable logic; it is compile-time hardware metadata used with the companion `nbio_7_4_offset.h` register-address definitions and AMDGPU register access helpers.

The chunk starts at the tail of the `VF7` virtual-function register area, specifically the last masks for `BIF_BX_DEV0_EPF0_VF7_BIF_VMHV_MAILBOX`, then finishes the `VF7` graphics MSI-X vector table/PBA fields. It then repeats a complete SR-IOV virtual-function register shape for `VF8` through `VF15`. Each full VF block contains:

- System PF/VF indirect MMIO window fields.
- RCC PF/VF decode fields for SR-IOV access/error logging and configuration.
- BIF PF/VF decode fields for bus mastering, atomic error status, doorbell aperture, HDP flush, transaction pending, address LUT bypass, and mailbox transport.
- RCC BIFDEC2 graphics MSI-X vector and pending-bit-array fields.

The file ends after global IOHC interrupt end-of-interrupt and RAS status masks, followed by the header guard terminator. Because this is the tail chunk of the file, it contributes both the last repeated VF definitions and the final global NBIO status definitions needed by later merge/reconciliation work.

## Important Macros And Register Families

There are no functions, structs, enums, or runtime APIs in this chunk. The exported interface consists entirely of generated macros using the standard AMD register-header naming convention:

- `REGISTER__FIELD__SHIFT`: bit position of a field inside its register.
- `REGISTER__FIELD_MASK`: bitmask covering that field inside its register value.

The `VF7` material in this chunk has two pieces. The opening lines close out `BIF_BX_DEV0_EPF0_VF7_BIF_VMHV_MAILBOX`, defining VM-to-HV mailbox receive/transmit message-data, valid, and acknowledge masks. The following `nbio_nbif0_rcc_dev0_epf0_vf7_BIFDEC2` block defines `RCC_DEV0_EPF0_VF7_GFXMSIX_VECT0` through `VECT2` address-low, address-high, message-data, and control-mask fields, plus `RCC_DEV0_EPF0_VF7_GFXMSIX_PBA` pending bits 0 through 2.

For `VF8` through `VF15`, the full repeating block begins with `BIF_BX_DEV0_EPF0_VF*_MM_INDEX`, `MM_DATA`, and `MM_INDEX_HI`. These expose an indirect MMIO access model: low offset bits, high offset bits, an aperture selector bit, and a full data dword. Consumers must pair these masks with the matching offset macros to address the intended virtual function's system PF/VF decode window.

The `RCC_DEV0_EPF0_VF*_RCC_*` block covers root-complex side PF/VF controls:

- `RCC_ERR_LOG` status bits for invalid register access in SR-IOV and doorbell read access.
- `RCC_DOORBELL_APER_EN` for enabling the BIF doorbell aperture.
- `RCC_CONFIG_MEMSIZE` and `RCC_CONFIG_RESERVED` full-width configuration fields.
- `RCC_IOV_FUNC_IDENTIFIER`, with the VF function identifier bit and the high `IOV_ENABLE` bit.

The `BIF_BX_DEV0_EPF0_VF*_*` PF/VF decode block contains the largest set of fields:

- `BIF_BME_STATUS` reports DMA activity while bus mastering is low and provides a clear bit.
- `BIF_ATOMIC_ERR_LOG` reports unsupported-request-style atomic error causes and provides matching clear bits for opcode, request-enable-low, length, and non-relaxed conditions.
- `DOORBELL_SELFRING_GPA_APER_BASE_HIGH`, `BASE_LOW`, and `CNTL` describe the guest physical address doorbell aperture, including enable, mode, and size fields.
- `HDP_REG_COHERENCY_FLUSH_CNTL` and `HDP_MEM_COHERENCY_FLUSH_CNTL` point at HDP flush control address bits.
- `GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE` provide per-client request/done bits for `CP0` through `CP9` and `SDMA0`/`SDMA1`.
- `BIF_TRANS_PENDING` reports master and slave BIF transaction-pending state.
- `NBIF_GFX_ADDR_LUT_BYPASS` exposes the LUT bypass bit.
- `MAILBOX_MSGBUF_TRN_DW0` through `DW3` and `MAILBOX_MSGBUF_RCV_DW0` through `DW3` expose four transmit and four receive mailbox data dwords.
- `MAILBOX_CONTROL` exposes transmit valid/ack and receive valid/ack bits.
- `MAILBOX_INT_CNTL` exposes interrupt enables for valid and ack events.
- `BIF_VMHV_MAILBOX` exposes compact VM/HV mailbox interrupt enables, transmit and receive message nibbles, valid bits, and ack bits.

The `RCC_DEV0_EPF0_VF*_GFXMSIX_*` BIFDEC2 block repeats for each VF. Each virtual function has three graphics MSI-X vectors. Every vector contains a low message address field with bits `[31:2]`, a full high address field, a full message-data field, and a single mask bit in the vector control register. The per-VF `GFXMSIX_PBA` register exposes pending bits for the three vectors.

The global tail contains:

- `IOHC_INTERRUPT_EOI`, with end-of-interrupt bits for SMI, SCI, and NMI.
- `RAS_GLOBAL_STATUS_LO`, with parity error status classes and firmware/software/APML/pin-triggered SMI, SCI, NMI, and sync-flood indicators.
- `RAS_GLOBAL_STATUS_HI`, with PCIE0 Port A and NBIF0 Port A error indicators.

## Control Flow

This header contributes no executable control flow. Runtime flow emerges when AMDGPU code includes this ASIC-specific mask header, reads or writes a register address from `nbio_7_4_offset.h`, and applies these constants to isolate or set fields.

A typical decode or update path outside this file is:

1. ASIC selection chooses the NBIO 7.4 register headers for the detected GPU.
2. Driver code obtains the offset for a BIF, RCC, IOHC, or RAS register from the companion offset header.
3. The code reads the register through MMIO, indirect MMIO, PCI configuration, or an ASIC wrapper helper.
4. A field is decoded with the corresponding `*_MASK` and `*_SHIFT`, often through local helper macros such as field-get/set wrappers.
5. For writable fields, the driver performs a read-modify-write sequence that preserves unrelated bits and writes only hardware-defined control or clear bits.

For the SR-IOV virtual-function blocks, higher-level control flow may configure VF doorbell apertures, service or poll mailbox state, inspect pending BIF transactions before reset, check HDP flush completion for command processor and SDMA clients, or program MSI-X vectors for VF interrupt delivery. For global tail registers, RAS and interrupt paths may check status bits, acknowledge IOHC interrupt classes, or report NBIF/PCIe error status through the driver's diagnostics.

## State And Persistence

The header itself is immutable generated metadata and stores no runtime state.

The represented state lives in hardware registers. Some fields represent configuration programmed by firmware, the PF driver, or virtualization setup, such as VF function identity, IOV enablement, doorbell aperture enable/base/size/mode, address LUT bypass, MSI-X vector address/data/control, mailbox interrupt enables, and mailbox message data. Other fields represent live hardware state, including bus-mastering anomalies, atomic-operation error logs, HDP flush request/done state, transaction-pending flags, mailbox valid/ack handshakes, MSI-X pending bits, global interrupt EOI acknowledgements, and RAS error indicators.

Persistence follows the hardware reset and power domains, not this file. GPU reset, PCI function reset, SR-IOV VF teardown, suspend/resume, firmware reinitialization, or driver unload/reload may clear or reprogram these registers. Error/status fields may be sticky, clear-on-write, write-one-to-clear, read-only, or side-effectful depending on the hardware register semantics. This mask header names bit positions only; it does not encode whether a field is safe to write, how it clears, or which reset domain owns it.

## Dependencies And Integration Points

The direct dependency is the matching NBIO 7.4 offset header. These masks are only meaningful when paired with the correct register offsets for the same ASIC generation and virtual-function index. The chunk also depends on AMDGPU's generated-register include conventions, where ASIC code selects the appropriate `asic_reg/nbio/nbio_7_4_*` headers and shared macros perform field extraction/composition.

Important integration points include:

- AMDGPU NBIO and PCIe initialization paths that select NBIO 7.4 definitions and configure BIF/RCC state.
- SR-IOV PF/VF management code that handles VF identity, IOV enablement, invalid SR-IOV register access logging, VF memory windows, and VF lifecycle reset.
- Doorbell setup paths that program PF/VF doorbell apertures and guest physical address ranges.
- HDP flush and synchronization paths that request and observe flush completion for CP and SDMA clients.
- Mailbox communication paths between a VF and the hypervisor/PF side, using transmit/receive dwords, valid/ack bits, interrupt enables, and VM/HV compact mailbox fields.
- MSI-X setup and interrupt-delivery code for graphics VF vectors, including vector table address/data/control and pending-bit-array fields.
- Reset/recovery paths that wait for BIF master/slave transaction pending to drain and clear BME or atomic error logs.
- RAS and interrupt handling paths that decode IOHC EOI and global NBIO/PCIe parity, sync-flood, APML, SMI/SCI/NMI, PCIE0, and NBIF0 status fields.

Although the repository path is under a Ceph client source mirror, the content is AMD GPU kernel-driver register metadata. It integrates with DRM/AMDGPU hardware code, not distributed filesystem logic.

## Risks

The main risk is silent hardware misdecode or misprogramming if any generated mask or shift is wrong or paired with the wrong offset/header generation. In this chunk, a single incorrect bit definition can affect VF interrupt delivery, doorbell routing, mailbox handshakes, HDP flush synchronization, SR-IOV access reporting, transaction quiescence checks, or RAS status reporting.

The repetition across `VF8` through `VF15` creates copy/generation risks. A typo isolated to one VF index can produce failures only for high-numbered virtual functions, making it hard to detect in systems that test only the first few VFs. Similar repetition across MSI-X vectors 0 through 2 and mailbox dwords 0 through 3 can create vector-specific or word-specific defects.

Access semantics are not captured by the macro names. Fields with `CLEAR_` in the name likely participate in clear-on-write flows, but the header does not enforce write-one-to-clear behavior. Treating status or clear bits like ordinary persistent fields could drop diagnostic evidence, leave sticky errors uncleared, or perturb live hardware state.

The indirect MMIO window fields are hazardous if used with the wrong aperture or high/low offset split. A bad `MM_INDEX` or `MM_INDEX_HI` composition can target a different register space than intended. Similarly, the MSI-X address-low mask intentionally excludes low address bits, and consumers must preserve alignment semantics when composing message addresses.

The chunk starts in the middle of the `VF7` mailbox/BIFDEC2 area and ends at the file terminator. Merge logic must not treat this chunk alone as complete coverage for VF7; preceding chunks contain most of the `VF7` PF/VF definitions.

## Test Signals

Useful validation signals are mostly build-time and hardware/integration-facing:

- Kernel or module builds including `nbio_7_4_sh_mask.h` complete without duplicate, missing, or malformed macro definitions.
- Generated mask definitions remain synchronized with `nbio_7_4_offset.h` and the ASIC register database for every `VF7` through `VF15` register referenced here.
- SR-IOV test runs create and exercise high-numbered VFs, especially `VF8` through `VF15`, rather than only low-numbered VFs.
- VF mailbox tests show correct transmit/receive valid and ack transitions, correct interrupt enable behavior, and correct four-dword message-buffer ordering.
- Doorbell tests confirm VF doorbell aperture base, size, mode, and enable fields route guest doorbells to the expected GPU queue paths.
- HDP flush tests verify request and done bits for `CP0` through `CP9` and `SDMA0`/`SDMA1` across all covered VFs.
- MSI-X tests confirm all three graphics vectors per covered VF program expected address/data/control values and surface pending bits in `GFXMSIX_PBA`.
- Reset and teardown tests observe BIF transaction-pending fields, clear BME and atomic error logs correctly, and avoid stale VF mailbox or interrupt state after FLR/GPU reset.
- RAS and error-injection tests confirm `IOHC_INTERRUPT_EOI`, `RAS_GLOBAL_STATUS_LO`, and `RAS_GLOBAL_STATUS_HI` decode SMI/SCI/NMI, parity, sync-flood, APML, PCIE0, and NBIF0 status consistently with hardware documentation and driver logs.
