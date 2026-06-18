# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 83609-86241

## Scope

This chunk covers generated NBIO 2.3 shift and mask macros for SR-IOV virtual-function register windows. It starts in the VF16 BIF PF/VF decode block after the VF16 HDP flush-done fields, then covers full repeated field layouts for VF17 through most of VF26, ending at `RCC_DEV0_EPF0_VF26_GFXMSIX_VECT3_ADDR_HI`.

The range contains 2,633 source lines with 2,014 `#define` constants: 1,007 `__SHIFT` values and 1,007 matching `_MASK` values. It has no C functions, structs, variables, allocation, locks, or executable branches. Its purpose is purely ABI description for hardware register fields.

## Purpose

`nbio_2_3_sh_mask.h` is the bitfield half of the NBIO 2.3 generated register contract. The matching offset header identifies the register addresses; this header identifies where each field lives inside each register. Driver code can then compose, extract, or test register values with `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15`, and direct bit masks without duplicating raw bit positions.

This specific chunk describes VF-local views for AMDGPU virtualization and PCIe/NBIO plumbing. The repeated VF blocks expose:

- indirect MMIO aperture index/data fields for each VF;
- RCC error, doorbell-aperture, config-memory, and IOV-identifier fields;
- BIF bus-master/atomic-error status and clear bits;
- self-ring doorbell GPA aperture base/control fields;
- HDP coherency flush request/done fields for CP and SDMA engines;
- transaction-pending indicators;
- VF transmit/receive mailbox data, valid, ack, and interrupt-enable fields;
- compact VM/hypervisor mailbox fields;
- four GFX MSI-X vector-table entries and a pending-bit array for each VF.

## Important Macro Families

### VF16 Tail

The assigned slice begins at the end of the VF16 `BIFPFVFDEC1` block. The covered VF16 fields include:

- `BIF_BX_DEV0_EPF0_VF16_NBIF_GFX_ADDR_LUT_BYPASS`, a single `LUT_BYPASS` bit for bypassing NBIF graphics address translation.
- `BIF_BX_DEV0_EPF0_VF16_MAILBOX_MSGBUF_TRN_DW0..DW3` and `RCV_DW0..DW3`, each exposing full-width `MSGBUF_DATA`.
- `BIF_BX_DEV0_EPF0_VF16_MAILBOX_CONTROL`, with `TRN_MSG_VALID`, `TRN_MSG_ACK`, `RCV_MSG_VALID`, and `RCV_MSG_ACK`.
- `BIF_BX_DEV0_EPF0_VF16_MAILBOX_INT_CNTL`, with valid/ack interrupt enables.
- `BIF_BX_DEV0_EPF0_VF16_BIF_VMHV_MAILBOX`, a compact VM/hypervisor mailbox with transmit and receive data nibbles, valid bits, ack bits, and interrupt enables.

It then defines the VF16 `BIFDEC2` MSI-X view: four `RCC_DEV0_EPF0_VF16_GFXMSIX_VECT*` entries, each with low/high message address, message data, and control mask bit, plus `RCC_DEV0_EPF0_VF16_GFXMSIX_PBA` pending bits 0 through 3.

### VF17-VF26 Repeated Decode Blocks

VF17 through VF26 repeat the same generated register pattern. Each VF has an address-block sequence:

- `nbio_nbif0_bif_bx_dev0_epf0_vf*_SYSPFVFDEC` for `MM_INDEX`, `MM_DATA`, and `MM_INDEX_HI`.
- `nbio_nbif0_rcc_dev0_epf0_vf*_BIFPFVFDEC1` for RCC error, doorbell aperture enable, config memory size/reserved, and IOV function identifier.
- `nbio_nbif0_bif_bx_dev0_epf0_vf*_BIFPFVFDEC1` for BIF status, atomic-error logging, doorbell self-ring aperture, HDP flush, transaction-pending, address-LUT bypass, and mailbox fields.
- `nbio_nbif0_rcc_dev0_epf0_vf*_BIFDEC2` for GFX MSI-X vector table and pending-bit fields.

The macro names are VF-numbered, but the field layouts are intentionally identical across the VFs in this range. That repetition lets generated code or diagnostics select a VF-specific register name while preserving the same bit semantics.

### MMIO Indirect Aperture Fields

For VF17 through VF26, `BIF_BX_DEV0_EPF0_VF*_MM_INDEX` splits the index register into:

- `MM_OFFSET`, bits 0 through 30, mask `0x7fffffff`;
- `MM_APER`, bit 31, mask `0x80000000`.

`BIF_BX_DEV0_EPF0_VF*_MM_DATA` exposes a full 32-bit `MM_DATA` field, while `MM_INDEX_HI` exposes a full 32-bit `MM_OFFSET_HI`. Together these fields describe the VF-visible indirect MMIO path used by NBIF/BIF decode windows.

### RCC VF State

Each VF has `RCC_DEV0_EPF0_VF*_RCC_ERR_LOG`, with status bits for invalid SR-IOV register access and doorbell read access. `RCC_DOORBELL_APER_EN` gates the BIF doorbell aperture with `BIF_DOORBELL_APER_EN`. `RCC_CONFIG_MEMSIZE` and `RCC_CONFIG_RESERVED` are full-width configuration fields. `RCC_IOV_FUNC_IDENTIFIER` has a low `FUNC_IDENTIFIER` bit and a high `IOV_ENABLE` bit at bit 31.

These fields mirror the PF/VF RCC controls used elsewhere in NBIO code, but this chunk publishes the per-VF16-through-VF26 macro names rather than the PF or VF0 names used by common runtime paths.

### BIF Status, Doorbell, and Atomic Error Fields

`BIF_BX_DEV0_EPF0_VF*_BIF_BME_STATUS` records `DMA_ON_BME_LOW` and has a high `CLEAR_DMA_ON_BME_LOW` bit. `BIF_ATOMIC_ERR_LOG` has status and clear pairs for unsupported atomic opcode, request-enable-low, length, and non-relaxed/NR conditions. The clear bits live in the high halfword, so callers must preserve unrelated status bits when acknowledging a condition.

The self-ring GPA doorbell aperture is split across:

- `DOORBELL_SELFRING_GPA_APER_BASE_HIGH`;
- `DOORBELL_SELFRING_GPA_APER_BASE_LOW`;
- `DOORBELL_SELFRING_GPA_APER_CNTL`, with enable at bit 0, mode at bit 1, and size in bits 8 through 19.

These VF-specific fields match the PF programming pattern in `nbio_v2_3_enable_doorbell_selfring_aperture()`, where the PF aperture base is loaded from `adev->doorbell.base` and the control word is composed with `REG_SET_FIELD`.

### HDP Flush and Transaction State

Each VF block includes register and memory coherency flush selectors:

- `HDP_REG_COHERENCY_FLUSH_CNTL__HDP_REG_FLUSH_ADDR`;
- `HDP_MEM_COHERENCY_FLUSH_CNTL__HDP_MEM_FLUSH_ADDR`.

It then defines `GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE` bits for CP0 through CP9 plus SDMA0 and SDMA1. The bit positions are stable across all VFs in this chunk: CP0 starts at bit 0, CP9 is bit 9, SDMA0 is bit 10, and SDMA1 is bit 11.

`BIF_TRANS_PENDING` exposes master and slave pending bits. Runtime code can use the matching offset/mask pair to determine whether outstanding traffic exists before reset, suspend, FLR, or VF teardown.

### Mailbox and VM/HV Mailbox Fields

Each VF has four transmit message buffer dwords and four receive message buffer dwords. The field name is always `MSGBUF_DATA`, mask `0xffffffff`, shift 0.

`MAILBOX_CONTROL` exposes the handshake state:

- transmit valid at bit 0;
- transmit ack at bit 1;
- receive valid at bit 8;
- receive ack at bit 9.

`MAILBOX_INT_CNTL` enables valid and ack interrupts. `BIF_VMHV_MAILBOX` packs a smaller VM/hypervisor mailbox into one register: interrupt enables at bits 0 and 1, transmit data in bits 8 through 11, transmit valid at bit 15, receive data in bits 16 through 19, receive valid at bit 23, transmit ack at bit 24, and receive ack at bit 25.

The integration model is visible in `amdgpu/mxgpu_nv.c`, which includes the NBIO 2.3 offset and shift/mask headers and implements VF/PF mailbox handshakes by writing transmit dwords, asserting valid, polling ack, reading receive dwords, and acknowledging receive messages.

### GFX MSI-X Vector Fields

For VF16 through the covered part of VF26, each `RCC_DEV0_EPF0_VF*_GFXMSIX_VECT0..3` entry contains:

- `ADDR_LO__MSG_ADDR_LO`, shifted by 2 with mask `0xfffffffc`, reflecting DWORD alignment of the low message address;
- `ADDR_HI__MSG_ADDR_HI`, full 32 bits;
- `MSG_DATA__MSG_DATA`, full 32 bits;
- `CONTROL__MASK_BIT`, bit 0.

Each VF block also has `GFXMSIX_PBA` pending bits 0 through 3. The chunk boundary cuts through the VF26 MSI-X block after `VECT3_ADDR_HI`; `VECT3_MSG_DATA`, `VECT3_CONTROL`, and `GFXMSIX_PBA` continue in the next chunk.

## Control Flow

This header has no local control flow. The runtime control flow is external:

1. AMDGPU selects NBIO 2.3 support for the ASIC and includes `nbio_2_3_offset.h`, `nbio_2_3_sh_mask.h`, and `nbio_2_3_default.h`.
2. Code computes or selects a register address using the offset header and SOC15 helpers.
3. Code reads a register, uses this header's shift/mask macros via `REG_SET_FIELD`, `REG_GET_FIELD`, or direct masking, then writes the result back.
4. Hardware applies the result to VF MMIO decode, doorbell routing, mailbox signaling, HDP coherency, transaction state, MSI-X delivery, or SR-IOV error/status handling.

For mailbox and status registers, the higher-level flow is a hardware handshake rather than a C branch in this file. A producer writes message buffer dwords and sets valid; the peer observes valid, consumes the dwords, and sets ack; the original producer clears valid to complete the exchange. Error-log and BME status fields use status/clear pairs, so callers must use the documented clear bits rather than overwriting the whole register blindly.

## State and Persistence Behavior

The header itself stores no state. It names state held in NBIO/NBIF hardware registers. That state persists until changed by MMIO/config writes, VF FLR, PF-mediated reset, ASIC reset, power transitions, firmware action, or hypervisor/VF management logic.

Persistent hardware state represented in this chunk includes:

- VF indirect MMIO aperture index and data values;
- VF IOV enable/function identifier and configured memory size;
- invalid SR-IOV access and doorbell-read error status;
- bus-master-low DMA and atomic-request error latches;
- doorbell self-ring GPA aperture base, enable, mode, and size;
- HDP flush request/done handshakes for CP and SDMA engines;
- BIF master/slave transaction pending status;
- mailbox payload dwords, valid/ack state, and mailbox interrupt enables;
- VM/hypervisor compact mailbox state;
- GFX MSI-X message addresses, message data, mask bits, and pending bits.

Ownership is shared. PF driver code, VF driver code, firmware, hypervisor logic, and hardware engines can all influence different fields. The generated header does not enforce ownership; it only names the bit locations.

## Dependencies and Integration Points

This chunk depends on the generated NBIO 2.3 register specification and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h`, which supplies matching `mm*`, `reg*`, and `cfg*` register addresses and base indices;
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h`, which supplies reset/default values for the same register families;
- AMDGPU SOC15 access helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_NO_KIQ`, `WREG32_NO_KIQ`, `REG_SET_FIELD`, `REG_GET_FIELD`, and `WREG32_FIELD15`;
- PCIe/SR-IOV, MSI-X, doorbell, HDP coherency, and VM/hypervisor mailbox hardware semantics.

Direct NBIO 2.3 consumers include `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, which includes this header and uses related PF field families for memory access, doorbell aperture enablement, self-ring doorbell programming, interrupt setup, HDP flush offsets/masks, and register remapping. `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c` also includes the NBIO 2.3 headers and uses the mailbox register interface for VF/PF communication. Power-management code under SMU11 includes this header for NBIO/PCIe strap and policy fields.

The exact VF16-through-VF26 names in this chunk are mostly generated ABI coverage rather than common hand-written C references. Their important integration role is keeping the per-VF register map available to diagnostics, generated code, virtualization paths, and any future code that needs to address a specific high-numbered VF window.

## Risks

- A wrong shift or mask compiles cleanly but changes the wrong hardware bit. In this chunk that can break VF doorbells, mailbox handshakes, MSI-X delivery, HDP flush completion checks, or SR-IOV error reporting.
- The VF blocks are highly repetitive. Copying a macro from the wrong VF number can target a different VF's register window even though the field layout is identical.
- The chunk begins and ends mid-pattern. VF16's earlier BME/atomic/HDP fields are in the previous chunk, and VF26's final MSI-X fields continue in the next chunk. Merge/reconciliation must not treat this slice as a complete source-file summary.
- Status and clear bits share registers. Whole-register writes can clear diagnostics or acknowledge events unintentionally.
- Doorbell aperture mistakes have virtualization security implications because they affect guest/host address routing and command-submission visibility.
- HDP flush bits are synchronization-critical. Missing or mis-numbering a CP/SDMA done bit can produce stale CPU/GPU memory visibility or hangs in code that waits for flush completion.
- Mailbox valid/ack ordering matters. Setting valid before payload dwords are visible, failing to clear valid, or reading receive dwords outside the expected valid state can lose PF/VF messages.
- MSI-X address low fields intentionally mask off low two bits. Treating the field as a full 32-bit low address can misprogram interrupt messages.

## Test Signals

Useful validation is mostly build, hardware, and virtualization oriented:

- Kernel build coverage should compile NBIO 2.3 users without missing or mismatched field macros.
- Generated-header consistency checks should confirm every VF16-VF26 shift has a matching mask and matching register address in the offset header.
- SR-IOV PF/VF bring-up should validate VF enumeration, IOV enable/function identity, config memory size visibility, and protected invalid-access logging.
- VF mailbox tests should verify transmit/receive dword payloads, valid/ack transitions, ack polling, valid clearing, and valid/ack interrupt enable behavior.
- Doorbell tests should confirm per-VF doorbell aperture enablement and self-ring GPA aperture programming do not misroute guest doorbells.
- HDP coherency tests should exercise CP0..CP9 and SDMA0/SDMA1 request/done bits under VF workloads.
- MSI-X tests should verify all four GFX vectors per VF program aligned message addresses, message data, mask bits, and pending-bit behavior.
- Reset/FLR tests should check that BME status, atomic error latches, transaction-pending bits, mailbox state, and MSI-X mask/pending state settle to expected values after VF reset.
