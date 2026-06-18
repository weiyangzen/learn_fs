# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_sh_mask.h lines 30057-32583

## Purpose

This chunk is generated AMDGPU NBIF 6.3.1 register bitfield metadata. It contains `#define` constants for register field shifts and masks, not executable code. The covered region describes per-SR-IOV-virtual-function fields for the device 0 endpoint function 0 VF aperture, spanning the end of VF15, complete VF16 through VF22 blocks, and the beginning of VF23.

The macros are paired with the sibling offset header, `nbif_6_3_1_offset.h`, where the same register names receive address and base-index definitions. Driver code includes `nbif/nbif_6_3_1_sh_mask.h` from `amdgpu/nbif_v6_3_1.c`; generic AMDGPU register helpers such as `REG_SET_FIELD()` and `REG_GET_FIELD()` consume the `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` naming convention throughout the driver tree.

## Register Groups Covered

The slice is organized by generated `addressBlock` comments:

- Tail of `nbif_bif_bx_dev0_epf0_vf15_BIFPFVFDEC1`: VF15 mailbox transmit/receive data words, mailbox control/interrupt enable, and compact VM/HV mailbox fields.
- `nbif_bif_bx_dev0_epf0_vf15_SYSPFVFDEC`: VF15 indirect MMIO index/data/index-high fields.
- `nbif_rcc_dev0_epf0_vf15_BIFPFVFDEC1`: VF15 RCC error, doorbell aperture enable, config memory size/reserved, and IOV function identity fields.
- `nbif_rcc_dev0_epf0_vf15_BIFDEC2`: VF15 GFX MSI-X vector table and pending-bit array fields.
- Repeated full `BIFPFVFDEC1`, `SYSPFVFDEC`, RCC `BIFPFVFDEC1`, and RCC `BIFDEC2` blocks for VF16, VF17, VF18, VF19, VF20, VF21, and VF22.
- Beginning of `nbif_bif_bx_dev0_epf0_vf23_BIFPFVFDEC1`: VF23 BME/atomic/doorbell/HDP coherency and GPU HDP flush request fields, ending inside the VF23 GPU HDP flush done field definitions.

The repeated full VF blocks define the same field layout per VF with only the `VF##` register-name component changing. This makes the region a generated map of isolated virtual-function register windows rather than a set of independent hand-written definitions.

## Important APIs, Types, and Macros

There are no C functions or types in this chunk. The important API surface is the macro naming contract:

- `REGISTER__FIELD__SHIFT`: bit position used by field extraction and insertion helpers.
- `REGISTER__FIELD_MASK`: bit mask for the same field.
- Register comments such as `//BIF_BX_DEV0_EPF0_VF16_GPU_HDP_FLUSH_REQ`: delimit one hardware register's fields.
- Address block comments such as `// addressBlock: nbif_bif_bx_dev0_epf0_vf16_BIFPFVFDEC1`: preserve the hardware address-space grouping from AMD register generation.

Notable field families:

- `BIF_BME_STATUS`: `DMA_ON_BME_LOW` status and `CLEAR_DMA_ON_BME_LOW` write/clear bit, used to observe and clear DMA activity while bus-master enable is low.
- `BIF_ATOMIC_ERR_LOG`: unsupported-request atomic error latches for opcode, request-enable-low, length, and non-relaxed/NR-style conditions, plus clear bits at positions 16-19.
- `DOORBELL_SELFRING_GPA_APER_*`: high/low base and control fields for VF doorbell self-ring guest physical aperture enable, mode, and size.
- `HDP_REG_COHERENCY_FLUSH_CNTL` and `HDP_MEM_COHERENCY_FLUSH_CNTL`: single-bit flush-address controls for register and memory coherency.
- `GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE`: 32-bit engine bitmaps for CP0-CP9, SDMA0-SDMA1, and reserved engines. Request and done masks must align bit-for-bit for polling or completion checks.
- `BIF_TRANS_PENDING`: a single `TRANS_PENDING` status bit.
- `MAILBOX_MSGBUF_TRN_DW*` and `MAILBOX_MSGBUF_RCV_DW*`: full 32-bit data words for VF mailbox transmit and receive payloads.
- `MAILBOX_CONTROL`: transmit/receive valid and acknowledge bits at positions 0, 1, 8, and 9.
- `MAILBOX_INT_CNTL`: valid and ack interrupt enables.
- `BIF_VMHV_MAILBOX`: compact VM/HV mailbox interrupt enables, 4-bit data fields, valid bits, and ack bits.
- `MM_INDEX`, `MM_DATA`, `MM_INDEX_HI`: indirect MMIO index/data window with low 31-bit offset, aperture selector at bit 31, and high offset extension.
- `RCC_ERR_LOG`, `RCC_DOORBELL_APER_EN`, `RCC_CONFIG_MEMSIZE`, `RCC_CONFIG_RESERVED`, and `RCC_IOV_FUNC_IDENTIFIER`: RCC-side SR-IOV status/configuration fields.
- `GFXMSIX_VECT[0-3]_*` and `GFXMSIX_PBA`: MSI-X message address, data, per-vector mask bit, and two pending bits.

## Control Flow and State Behavior

This header contributes no direct control flow. Runtime behavior emerges when AMDGPU code reads or writes the corresponding registers through the offset definitions and these masks.

State represented here is hardware-resident and mostly volatile:

- Error-status registers expose latched hardware conditions and paired clear bits. Using the wrong clear mask can either fail to clear a condition or clear the wrong latch.
- Doorbell aperture fields configure guest-visible doorbell routing for each VF. These values affect how VF software signals queues or rings.
- HDP flush request/done fields model a request/completion handshake. Software sets request bits for engines and polls matching done bits, so request/done field drift is a coherency and hang risk.
- Mailbox registers model persistent-in-register handshakes until the peer updates valid/ack bits. The transmit and receive data words are full 32-bit payload registers.
- MSI-X vector fields hold interrupt message address/data/mask state, with pending bits recording delivery state.
- Indirect MMIO index/data fields preserve the usual indexed-register access state: writes to index select an offset/aperture, and data accesses target that selection.

No disk persistence, memory allocation, locking, or driver-owned data structure is defined in this chunk.

## Dependencies and Integration Points

The chunk depends on the generated AMD register naming scheme and its companion headers:

- `nbif_6_3_1_offset.h` supplies addresses and base indices for these same register names, for example VF16 `GPU_HDP_FLUSH_REQ`, `MAILBOX_CONTROL`, and `RCC_DEV0_EPF0_VF16_GFXMSIX_VECT0_ADDR_LO`.
- Older or alternate generated headers such as `include/asic_reg/nbio/nbio_2_3_sh_mask.h`, `nbio_2_3_offset.h`, and `nbio_2_3_default.h` contain analogous NBIO register metadata and defaults for related ASIC blocks.
- `amdgpu/nbif_v6_3_1.c` includes this header, so any driver code in that compilation unit can use these bit masks directly.
- AMDGPU register helper macros rely on exact names and suffixes. A field named `X` for register `Y` is expected to define `Y__X__SHIFT` and `Y__X_MASK`.

The immediate integration surface is low-level GPU initialization, SR-IOV virtualization support, mailbox handling between PF/VF or VM/HV contexts, interrupt/MSI-X setup, doorbell aperture programming, and HDP coherency-flush handling.

## Risks

- Generated constants are easy to treat as inert, but a single incorrect shift or mask can corrupt hardware programming across all VFs sharing the repeated pattern.
- The repeated VF16-VF22 blocks should remain structurally identical except for VF number. Divergence may indicate a generation issue unless backed by hardware documentation.
- This chunk starts and ends mid-VF context: it begins after earlier VF15 definitions and stops inside VF23. File-level research must reconcile adjacent chunks before drawing conclusions about complete VF15 and VF23 coverage.
- `GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE` define 32 one-bit fields each. Any mismatch between engine bit names, masks, or offsets can break flush completion polling and cause stale CPU/GPU-visible memory state.
- Mailbox valid/ack bits are small single-bit handshakes. Swapping transmit and receive fields or using a data mask on control bits can deadlock PF/VF or VM/HV communication.
- MSI-X address-low fields start at shift 2 with mask `0xFFFFFFFC`, reflecting aligned message addresses. Treating the field as a raw 32-bit value can discard or mis-handle low address bits.
- Clear bits for BME and atomic error logs are separate high-half bits, not the same bits as the status latches. Read/modify/write helpers need to avoid accidentally writing stale status bits as commands.

## Test and Validation Signals

Useful validation for this chunk is mostly structural and hardware-facing:

- Build coverage: compile AMDGPU code paths that include `nbif/nbif_6_3_1_sh_mask.h`, especially `amdgpu/nbif_v6_3_1.c`, to catch missing or renamed generated macros.
- Header consistency checks: verify every `REGISTER__FIELD__SHIFT` in the slice has the matching `REGISTER__FIELD_MASK`, and that each register has a companion address/base index in `nbif_6_3_1_offset.h` where expected.
- Pattern checks: compare VF16 through VF22 field sets for exact shape equality after replacing `VF16`...`VF22` with a placeholder.
- Runtime SR-IOV tests: create VFs, exercise doorbells, mailbox send/receive, MSI-X delivery/masking, and reset/error-clear paths.
- Coherency tests: submit CP/SDMA work that requires HDP flushes and confirm request bits transition to matching done bits without timeout.
- Error-injection or negative tests: trigger invalid SR-IOV register access, doorbell read access, atomic unsupported-request logging, and BME-low DMA detection, then confirm the documented clear bits reset the latched status.
