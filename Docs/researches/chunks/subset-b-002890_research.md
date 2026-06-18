# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_sh_mask.h lines 32584-32806

## Scope

This chunk is the final section of the generated AMD NBIF 6.3.1 shift/mask header. It contains C preprocessor constants for hardware register bit positions and masks; it defines no C functions, structs, enums, variables, locks, memory allocations, or executable logic.

The range starts at the tail of the `BIF_BX_DEV0_EPF0_VF23_GPU_HDP_FLUSH_REQ` mask family, covers the complete `BIF_BX_DEV0_EPF0_VF23_GPU_HDP_FLUSH_DONE` family, VF23 transaction-pending status, mailbox data/control/interrupt fields, the compact VM/hypervisor mailbox, VF23 indirect MM access windows, VF23 RCC error and SR-IOV identity/configuration fields, four VF23 graphics MSI-X vector entries, the graphics MSI-X pending-bit array, and the closing `#endif`.

The source file is under `sources/distributed-fs/ceph-client`, but this header is AMDGPU DRM hardware-description data. It is unrelated to Ceph client filesystem behavior.

## Purpose

`nbif_6_3_1_sh_mask.h` supplies the field side of the NBIF 6.3.1 hardware ABI. Driver code pairs these `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros with register offsets from `nbif_6_3_1_offset.h` and SOC15/register helper APIs. The specific slice describes per-virtual-function register layouts for EPF0 VF23 and a small RCC/MSI-X tail block.

The covered fields support:

- HDP coherency flush request/done synchronization for command processor and SDMA engines.
- VF23 transaction-idle detection through BIF master/slave pending flags.
- PF/VF mailbox transport and receive buffers, valid/ack handshakes, and interrupt enables.
- A compact VMHV mailbox with 4-bit transmit/receive payload nibbles plus valid/ack and interrupt-enable bits.
- Indirect MM register access through index/data/high-index registers.
- RCC-side SR-IOV diagnostics and VF identification/configuration registers.
- VF23 graphics MSI-X table programming for four vectors and pending-bit reporting.

Because this is a generated register header, its central purpose is exact bitfield naming and numeric accuracy rather than algorithmic behavior. A single bad mask can make higher-level driver code read, poll, or write the wrong hardware bit.

## Important Macro Families

### HDP Flush Request and Done

The first three lines are the end of `BIF_BX_DEV0_EPF0_VF23_GPU_HDP_FLUSH_REQ`, defining masks for reserved engines 17, 18, and 19 at bits 29, 30, and 31. The rest of the request register is in the previous chunk.

`BIF_BX_DEV0_EPF0_VF23_GPU_HDP_FLUSH_DONE` is complete in this chunk. It defines matching one-bit fields for:

- `CP0` through `CP9` at bits 0-9.
- `SDMA0` and `SDMA1` at bits 10-11.
- `RSVD_ENG0` through `RSVD_ENG19` at bits 12-31.

The masks are the direct powers-of-two equivalents from `0x00000001L` through `0x80000000L`. The layout mirrors other NBIF/NBIO HDP flush register families used by AMDGPU. In `amdgpu/nbif_v6_3_1.c`, the PF0 variants of this family are wired into `nbif_v6_3_1_hdp_flush_reg`, and `nbif_v6_3_1_get_hdp_flush_req_offset()` / `nbif_v6_3_1_get_hdp_flush_done_offset()` return the PF0 request/done offsets. VF23 uses the same conceptual request/done protocol, with VF-specific register names and offsets.

### Transaction Pending

`BIF_BX_DEV0_EPF0_VF23_BIF_TRANS_PENDING` exposes:

- `BIF_MST_TRANS_PENDING` at bit 0.
- `BIF_SLV_TRANS_PENDING` at bit 1.

These fields indicate outstanding master-side and slave-side NBIF transactions for the VF23 BIF window. They are natural polling/status inputs for reset, FLR, quiesce, suspend, or virtualization management flows.

### Full-Word Mailbox Buffers

The mailbox message buffers are full 32-bit fields:

- Transmit buffers: `BIF_BX_DEV0_EPF0_VF23_MAILBOX_MSGBUF_TRN_DW0` through `_DW3`.
- Receive buffers: `BIF_BX_DEV0_EPF0_VF23_MAILBOX_MSGBUF_RCV_DW0` through `_DW3`.

Each register exposes `MSGBUF_DATA` with shift `0x0` and mask `0xFFFFFFFFL`. Together, the transmit and receive sides provide four doublewords each for PF/VF mailbox payloads.

### Mailbox Control and Interrupt Control

`BIF_BX_DEV0_EPF0_VF23_MAILBOX_CONTROL` defines the mailbox handshake bits:

- `TRN_MSG_VALID` at bit 0.
- `TRN_MSG_ACK` at bit 1.
- `RCV_MSG_VALID` at bit 8.
- `RCV_MSG_ACK` at bit 9.

`BIF_BX_DEV0_EPF0_VF23_MAILBOX_INT_CNTL` defines:

- `VALID_INT_EN` at bit 0.
- `ACK_INT_EN` at bit 1.

The split between transmit valid/ack and receive valid/ack encodes a hardware handshake protocol. Software must treat these as synchronization bits, not as arbitrary persistent storage.

### VMHV Mailbox

`BIF_BX_DEV0_EPF0_VF23_BIF_VMHV_MAILBOX` is a compact VM/hypervisor mailbox register with both data and control in one 32-bit word:

- `VMHV_MAILBOX_TRN_ACK_INTR_EN` at bit 0.
- `VMHV_MAILBOX_RCV_VALID_INTR_EN` at bit 1.
- `VMHV_MAILBOX_TRN_MSG_DATA` in bits 8-11 (`0x00000F00L`).
- `VMHV_MAILBOX_TRN_MSG_VALID` at bit 15.
- `VMHV_MAILBOX_RCV_MSG_DATA` in bits 16-19 (`0x000F0000L`).
- `VMHV_MAILBOX_RCV_MSG_VALID` at bit 23.
- `VMHV_MAILBOX_TRN_MSG_ACK` at bit 24.
- `VMHV_MAILBOX_RCV_MSG_ACK` at bit 25.

This is a lower-bandwidth mailbox than the four-doubleword message-buffer interface. It is suitable for small command/status nibbles plus interrupt-assisted valid/ack signaling.

### Indirect MM Access

The `nbif_bif_bx_dev0_epf0_vf23_SYSPFVFDEC` address block defines:

- `BIF_BX_DEV0_EPF0_VF23_MM_INDEX`, with `MM_OFFSET` in bits 0-30 and `MM_APER` at bit 31.
- `BIF_BX_DEV0_EPF0_VF23_MM_DATA`, with full-width `MM_DATA`.
- `BIF_BX_DEV0_EPF0_VF23_MM_INDEX_HI`, with full-width `MM_OFFSET_HI`.

The matching offset header places these at base index 0 (`regBIF_BX_DEV0_EPF0_VF23_MM_INDEX`, `reg...MM_DATA`, and `reg...MM_INDEX_HI`). This is an indirect access aperture: software programs an index/offset, optionally high offset bits, then reads or writes the data window. Correct ordering is enforced by the caller and hardware semantics, not by this macro header.

### RCC VF23 Error and SR-IOV Configuration

The `nbif_rcc_dev0_epf0_vf23_BIFPFVFDEC1` block defines:

- `RCC_DEV0_EPF0_VF23_RCC_ERR_LOG`: `INVALID_REG_ACCESS_IN_SRIOV_STATUS` at bit 0 and `DOORBELL_READ_ACCESS_STATUS` at bit 1.
- `RCC_DEV0_EPF0_VF23_RCC_DOORBELL_APER_EN`: `BIF_DOORBELL_APER_EN` at bit 0.
- `RCC_DEV0_EPF0_VF23_RCC_CONFIG_MEMSIZE`: full-width `CONFIG_MEMSIZE`.
- `RCC_DEV0_EPF0_VF23_RCC_CONFIG_RESERVED`: full-width `CONFIG_RESERVED`.
- `RCC_DEV0_EPF0_VF23_RCC_IOV_FUNC_IDENTIFIER`: `FUNC_IDENTIFIER` at bit 0 and `IOV_ENABLE` at bit 31.

These fields are SR-IOV and register-protection sensitive. Error-log bits report invalid SR-IOV register access and doorbell-read access status. Doorbell aperture enable controls whether the VF can use the BIF doorbell aperture. The function identifier and `IOV_ENABLE` bit describe whether this virtual function participates in IOV mode.

### VF23 Graphics MSI-X Table

The `nbif_rcc_dev0_epf0_vf23_BIFDEC2` block defines four graphics MSI-X vector entries:

- `RCC_DEV0_EPF0_VF23_GFXMSIX_VECT0_*` through `VECT3_*`.
- Each vector has `ADDR_LO`, `ADDR_HI`, `MSG_DATA`, and `CONTROL`.
- `ADDR_LO.MSG_ADDR_LO` starts at bit 2 and uses mask `0xFFFFFFFCL`, reflecting the alignment of MSI-X message addresses.
- `ADDR_HI.MSG_ADDR_HI` and `MSG_DATA.MSG_DATA` are full-width fields.
- `CONTROL.MASK_BIT` is bit 0 for vector masking.

`RCC_DEV0_EPF0_VF23_GFXMSIX_PBA` exposes pending bits 0 and 1 only in this NBIF 6.3.1 VF23 chunk. The companion offset header confirms the vector registers use base index 3 and that the PBA is at offset `0x0800` in the same base-index domain.

## Control Flow and Runtime Use

This header has no executable control flow. Runtime behavior comes from driver code that includes the header and uses the macros with register offsets and MMIO helpers.

Known local integration around this generation:

1. `amdgpu/nbif_v6_3_1.c` includes `nbif/nbif_6_3_1_offset.h` and `nbif/nbif_6_3_1_sh_mask.h`.
2. The NBIF 6.3.1 implementation exposes HDP flush request/done offsets to ring code through `adev->nbio.funcs->get_hdp_flush_req_offset` and `get_hdp_flush_done_offset`.
3. It populates `struct nbio_hdp_flush_reg` with HDP flush done masks for PF0 CP and SDMA clients. Generic GFX and SDMA ring paths use those masks as reference/mask values when emitting HDP flush packets or polling commands.
4. VF23-specific HDP flush, mailbox, and MSI-X macros in this chunk are not directly referenced by the searched C implementation, but they follow the same generated ABI pattern and are available for virtualization, debug, register dump, firmware-interaction, or future VF-specific code paths.

The implied hardware flows are:

- A client writes or triggers a `GPU_HDP_FLUSH_REQ` bit for an engine, then waits until the corresponding `GPU_HDP_FLUSH_DONE` bit is observed.
- Reset or quiesce code can inspect `BIF_TRANS_PENDING` before assuming the VF's BIF path is idle.
- Mailbox senders write message data, assert valid, and wait for an ack; receivers observe valid, consume data, and assert ack. Interrupt enables decide whether valid/ack transitions raise interrupts.
- MSI-X setup programs message address/data fields and clears or sets vector mask bits; pending bits report interrupts that are pending while vectors are masked.

## State and Persistence Behavior

The header stores no software state. The represented state lives in hardware registers and persists according to GPU reset, FLR, power management, PF/VF assignment, firmware programming, and explicit driver writes.

Important state classes:

- HDP flush request/done bits are transient synchronization state. They gate cache/coherency visibility for engines such as CP and SDMA.
- Transaction-pending bits are status state owned by the BIF hardware.
- Mailbox data buffers and valid/ack bits are shared communication state between PF/VF or VM/hypervisor participants.
- Mailbox interrupt-enable bits are configuration state that controls whether mailbox handshakes generate interrupts.
- Indirect MM index/data registers are access-window state. A stale index can redirect a later data access to the wrong register.
- RCC error-log bits are diagnostic/latch-like status; clearing semantics are determined by the hardware contract outside this header.
- Doorbell aperture enable, config memsize/reserved, and IOV function identifier state are virtualization configuration inputs.
- MSI-X address/data/control and PBA bits are interrupt routing and delivery state. Vector masking persists until changed or reset.

## Dependencies and Integration Points

Direct generated dependencies:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_offset.h` supplies matching register addresses and base indices. For this chunk, the VF23 BIFPFVFDEC1 registers use base index 2, the indirect MM window uses base index 0, and the graphics MSI-X table uses base index 3.
- Other chunks of `nbif_6_3_1_sh_mask.h` define the beginning of the VF23 `GPU_HDP_FLUSH_REQ` family, PF0 equivalents used directly by `nbif_v6_3_1.c`, and the broader NBIF PCIe/RCC/SR-IOV register contract.

Driver integration:

- `amdgpu/nbif_v6_3_1.c` is the direct NBIF 6.3.1 consumer and includes this header.
- `amdgpu/amdgpu_nbio.h` defines `struct nbio_hdp_flush_reg` and the NBIO function hooks used by graphics and SDMA rings.
- `amdgpu/amdgpu_gfx.c` uses `adev->nbio.hdp_flush_reg` to derive CP HDP flush masks for graphics rings.
- SDMA implementations such as `sdma_v6_0.c`, `sdma_v5_2.c`, and `sdma_v4_4_2.c` use NBIO-provided HDP flush offsets and masks to emit ring-level HDP flush/poll operations.
- MSI-X, SR-IOV, mailbox, and doorbell fields are hardware integration points for PCIe interrupt setup, VF management, PF/VF communication, and hypervisor-facing device control even when this exact VF23 name set is not referenced by a local C file.

## Risks and Edge Cases

- The chunk begins mid-register-family. The first three macros are only the tail of `BIF_BX_DEV0_EPF0_VF23_GPU_HDP_FLUSH_REQ`; final per-file reconciliation must merge the previous chunk for CP, SDMA, and earlier reserved-engine request bits.
- Bitfield drift in generated masks is high impact. Incorrect HDP flush done masks can make ring code wait on the wrong bit, skip a needed coherency flush, or time out.
- Reserved-engine bits are not free scratch bits. Other NBIO generations explicitly warn that some reserved HDP flush bits can be firmware-owned; callers should only use engine mappings documented for the ASIC.
- Mailbox valid/ack fields require protocol sequencing. Setting valid before payload writes, clearing ack too early, or enabling interrupts without a handler can lose messages or create interrupt storms.
- The indirect MM index/data interface is order-sensitive. Concurrent users need external serialization, and stale `MM_INDEX` or `MM_INDEX_HI` state can make a later `MM_DATA` access hit the wrong register.
- SR-IOV error and doorbell fields are isolation-sensitive. Wrong use can expose doorbells, hide invalid register access, or misidentify IOV state for a VF.
- MSI-X vector fields are interrupt-critical. Bad address/data masks or stale `MASK_BIT` state can misroute interrupts, leave interrupts masked, or report misleading pending bits.
- The VF23 block repeats patterns present for other VFs. Mechanical generation errors are plausible around VF numbers, base indices, vector numbers, and pending-bit counts. Adjacent offset/mask chunks should be compared when validating a generator update.

## Test and Verification Signals

Useful validation is mostly build, register readback, and hardware integration:

- Build AMDGPU code that includes `nbif_6_3_1_sh_mask.h` and `nbif_6_3_1_offset.h`; this catches missing or malformed generated names.
- On NBIF 6.3.1 hardware, issue HDP flushes through graphics and SDMA rings and confirm the expected request/done bits transition before memory-visible operations proceed.
- Exercise reset, FLR, suspend/resume, or VF teardown paths and confirm `BIF_TRANS_PENDING` reaches idle before destructive actions.
- In SR-IOV or VF debug environments, verify VF23 mailbox traffic by writing transmit buffers, setting `TRN_MSG_VALID`, observing `TRN_MSG_ACK`, and checking receive valid/ack behavior with and without mailbox interrupts enabled.
- Validate VMHV mailbox nibble payloads and valid/ack interrupt enables using firmware or hypervisor diagnostics that can see both endpoints.
- Test indirect MM access by programming `MM_INDEX`/`MM_INDEX_HI`, reading/writing `MM_DATA`, and confirming the targeted register changes while unrelated registers remain untouched.
- Inject or provoke invalid SR-IOV register access and doorbell-read cases, then check `RCC_ERR_LOG` status bits.
- Program the VF23 graphics MSI-X vectors, toggle `CONTROL.MASK_BIT`, generate interrupts, and confirm delivery or PBA pending behavior matches mask state.
- Compare register dumps against `nbif_6_3_1_offset.h` base-index plus offset calculations for the VF23 BIFPFVFDEC1, SYSPFVFDEC, and BIFDEC2 blocks.

## Cross-Chunk Notes

This is the end of `nbif_6_3_1_sh_mask.h`. The previous chunk is required for the start of `BIF_BX_DEV0_EPF0_VF23_GPU_HDP_FLUSH_REQ` and for earlier VF23 BIF/RCC fields such as BME status, atomic error logging, doorbell self-ring GPA aperture, and HDP coherency flush control. The final per-file report should describe the repeated VF register pattern across all VFs and explain that this header is a generated bitfield contract, while behavior is implemented in AMDGPU NBIF/NBIO, ring, PCIe, SR-IOV, mailbox, and interrupt code.
