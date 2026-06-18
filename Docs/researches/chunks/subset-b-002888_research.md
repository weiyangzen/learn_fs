# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_sh_mask.h lines 27551-30056

## Scope

This chunk covers a generated AMD NBIF 6.3.1 register shift/mask header section for SR-IOV virtual-function register blocks. It starts in the middle of `BIF_BX_DEV0_EPF0_VF8_BIF_ATOMIC_ERR_LOG`, then covers the rest of the VF8 block, complete repeated blocks for VF9 through VF14, and the beginning of VF15 through `BIF_BX_DEV0_EPF0_VF15_MAILBOX_MSGBUF_TRN_DW2`.

The file is data-only C preprocessor material. It defines no functions, structs, variables, locks, allocations, or direct MMIO operations. Its public interface is the standard generated register-field convention:

- `<REGISTER>__<FIELD>__SHIFT` for bit positions.
- `<REGISTER>__<FIELD>_MASK` for the corresponding 32-bit field mask.

The matching register addresses live in `nbif_6_3_1_offset.h`. Active C users include `amdgpu/nbif_v6_3_1.c`, which includes both the offset and shift/mask headers and consumes the same field families through AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

## Purpose

These macros describe the ABI between AMDGPU/NBIO code, firmware, and NBIF hardware for per-VF BIF and RCC register windows on NBIF 6.3.1 ASICs. The covered virtual functions are mostly VF8 through VF14, plus partial VF15. Each full VF block repeats the same semantic layout:

- BIF bus-master and PCIe atomic-operation error status.
- Doorbell self-ring guest-physical-address aperture base and control fields.
- HDP register/memory coherency flush command fields.
- GPU HDP flush request and done bits for CP, SDMA, and reserved engines.
- Transaction-pending status.
- PF/VF mailbox transmit and receive message buffers, control, interrupt enable, and VM/HV compact mailbox fields.
- VF indirect MMIO index/data/index-high window fields.
- RCC SR-IOV error, doorbell aperture, memory-size, reserved config, and IOV identity fields.
- RCC MSI-X vector table and pending-bit array fields.

The chunk is primarily a generated hardware register contract. It does not decide policy itself, but it allows policy code and firmware-facing paths to compose exact register values for SR-IOV virtual functions.

## Important Macro Families

### BIF Error and Bus-Master Status

For VF9 through VF15, and the tail of VF8 at the chunk start, `BIF_BME_STATUS` exposes `DMA_ON_BME_LOW` plus `CLEAR_DMA_ON_BME_LOW`. `BIF_ATOMIC_ERR_LOG` exposes unsupported-request atomic error causes: opcode, request enable low, length, and non-relaxed/NR state, along with clear bits for each latch.

These fields are status/clear style, not ordinary configuration. The `CLEAR_*` bits imply write-to-clear behavior and need read/modify/write care so software does not accidentally drop adjacent error state.

### Doorbell Self-Ring Aperture

Each covered VF has:

- `DOORBELL_SELFRING_GPA_APER_BASE_HIGH`
- `DOORBELL_SELFRING_GPA_APER_BASE_LOW`
- `DOORBELL_SELFRING_GPA_APER_CNTL`

The base registers are full-width 32-bit halves of a guest physical address. The control register has enable, mode, and size fields. The PF0 version of this family is actively used in `nbif_v6_3_1_enable_doorbell_selfring_aperture()`, where the driver writes `adev->doorbell.base` into the base-low/high registers, sets enable and mode, and programs size through `REG_SET_FIELD`. The VF variants in this chunk describe equivalent per-VF doorbell self-ring aperture state.

### HDP Coherency Flush Controls

The chunk defines one-bit address fields for:

- `HDP_REG_COHERENCY_FLUSH_CNTL`
- `HDP_MEM_COHERENCY_FLUSH_CNTL`
- `HDP_MEM_COHERENCY_FLUSH_ONLY_CNTL`
- `HDP_MEM_COHERENCY_INVALIDATE_ONLY_CNTL`

The PF0 equivalents are used by NBIF register remapping and rMMIO setup in `nbif_v6_3_1_remap_hdp_registers()` and `nbif_v6_3_1_set_reg_remap()`. For VFs, these masks describe the per-function flush/invalidate aperture used to keep host data path visibility coherent across guest, host, and GPU engines.

### GPU HDP Flush Request/Done Handshake

`GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE` are full 32-bit bitmaps. Bits 0-9 are `CP0` through `CP9`, bits 10-11 are `SDMA0` and `SDMA1`, and bits 12-31 are reserved engine bits. The layout is repeated for each full VF block and the partial VF15 block.

The PF0 form is wired into `nbif_v6_3_1_get_hdp_flush_req_offset()`, `nbif_v6_3_1_get_hdp_flush_done_offset()`, and `nbif_v6_3_1_hdp_flush_reg`. GFX, MES, and SDMA code later use the NBIO function table and `struct nbio_hdp_flush_reg` masks to submit flush requests and wait for done bits. The VF masks provide the same per-engine handshake layout for virtualized register spaces.

Reserved engine bits are exposed by the generated header, but comparable NBIO code comments in other versions note that reserved HDP bits may be firmware-owned. Consumers should not assign new engine semantics to `RSVD_ENG*` bits without hardware/firmware confirmation.

### PF/VF Mailboxes and VM/HV Mailbox

For VF8 through VF14, the chunk defines four transmit message buffer dwords, four receive message buffer dwords, mailbox control bits, interrupt enable bits, and a compact `BIF_VMHV_MAILBOX` register. VF15 includes only transmit dwords 0 through 2 before the chunk ends.

The message buffer dwords are full-width `MSGBUF_DATA` fields. `MAILBOX_CONTROL` exposes transmit valid/ack and receive valid/ack bits. `MAILBOX_INT_CNTL` enables valid and ack interrupts. `BIF_VMHV_MAILBOX` packs VM/HV transmit/receive data nibbles, valid bits, ack bits, and interrupt enables into one register.

These fields implement a small state machine: producer writes message data, asserts valid, waits for ack; receiver observes valid, consumes data, and asserts ack. The header only supplies bit positions; ordering, timeout, and interrupt-routing rules come from mailbox users and firmware contracts.

### VF Indirect MMIO Window

For VF8 through VF14, `MM_INDEX`, `MM_DATA`, and `MM_INDEX_HI` define an indirect MMIO access window. `MM_INDEX` packs a 31-bit offset plus `MM_APER` in bit 31, `MM_INDEX_HI` extends the offset, and `MM_DATA` carries the read/write payload.

This is a critical integration surface for virtualized MMIO access because it can let guest-visible function code address selected register apertures without direct physical register mapping. Incorrect masks here can redirect register access to the wrong aperture or truncate high address bits.

### RCC SR-IOV Configuration and Error State

For VF8 through VF14, `RCC_ERR_LOG` exposes invalid SR-IOV register access and doorbell-read access status. `RCC_DOORBELL_APER_EN` enables the BIF doorbell aperture. `RCC_CONFIG_MEMSIZE` and `RCC_CONFIG_RESERVED` are full-width configuration registers. `RCC_IOV_FUNC_IDENTIFIER` exposes function identity and a high-bit `IOV_ENABLE`.

The PF0 doorbell aperture equivalent is used by `nbif_v6_3_1_enable_doorbell_aperture()` through `WREG32_FIELD15_PREREG`. The VF variants map the same kind of state into per-VF RCC decode blocks.

### RCC MSI-X Vector State

For VF8 through VF14, each block defines MSI-X vector 0 through vector 3 address-low, address-high, message-data, and control registers, plus `GFXMSIX_PBA`. Address-low masks bits 31:2, matching the natural alignment of MSI/MSI-X message addresses. Control exposes a `MASK_BIT`. The PBA exposes two pending bits.

These macros describe guest interrupt delivery state. They integrate with PCIe/MSI-X programming and interrupt handling, even though the source chunk itself has no interrupt handler code.

## Control Flow and State Behavior

There is no executable control flow in this header. Its behavior is compile-time: C code includes it and uses the generated constants to build and decode NBIF MMIO values.

The state represented by the fields is persistent hardware state until overwritten, reset, or cleared by status-specific write semantics. Persistent configuration includes doorbell base/control registers, RCC memory-size and IOV identity state, indirect MMIO aperture selectors, and MSI-X table values. Transient or command/status state includes BME-low and atomic-error latches, HDP flush request/done bits, transaction-pending bits, mailbox valid/ack bits, mailbox interrupt enables, RCC error logs, and MSI-X pending bits.

The implied control-flow patterns are hardware handshakes rather than C branches:

- Doorbell aperture setup writes base low/high before enabling the control register.
- HDP flushing writes a request bit for the relevant engine and waits for the matching done bit.
- PF/VF mailbox exchange writes message data, toggles valid, observes ack, and may use interrupt-enable bits for valid/ack events.
- Error logs are read, decoded, and cleared with matching clear bits.
- Indirect MMIO access writes index/index-high state and transfers payload through data.

## Dependencies and Integration Points

This chunk depends on generated NBIF and AMDGPU infrastructure:

- `nbif_6_3_1_offset.h` supplies the matching `reg...` addresses and base indices.
- `nbif_6_3_1_sh_mask.h` supplies the field masks in this chunk and adjacent PF/VF chunks.
- `soc15.h`-style AMDGPU helpers consume the `__SHIFT` and `_MASK` naming convention.
- `amdgpu/nbif_v6_3_1.c` includes this header and registers `nbif_v6_3_1_funcs`, including doorbell aperture setup, HDP flush offsets, rMMIO HDP remap, indirect PCIe index/data offsets, ASPM programming, and RAS interrupt hooks.
- GFX, MES, and SDMA paths use NBIO HDP flush offsets/masks through the NBIO function table and `adev->nbio.hdp_flush_reg`.
- SR-IOV and virtualization paths are the natural owners of the per-VF BIF/RCC blocks, because all covered register names are scoped under `DEV0_EPF0_VF*`.
- PCIe/MSI-X interrupt delivery integrates with the `GFXMSIX_*` vector table and PBA fields.

## Risks

- Generated bitfield drift is high impact. A wrong shift or mask can target the wrong NBIF field, breaking doorbells, coherency flushes, mailbox handshakes, indirect MMIO, or interrupt delivery.
- The VF blocks are mechanically repetitive. Copy-generation errors between VF8, VF9, VF10, VF11, VF12, VF13, VF14, and VF15 could silently isolate one virtual function from doorbells, HDP flush completion, or MSI-X delivery.
- Status clear bits share registers with status bits. Careless writes to `CLEAR_*`, mailbox ack/valid bits, or error-clear fields can lose diagnostic state or acknowledge events prematurely.
- Doorbell aperture base/control fields are security-sensitive under SR-IOV. Misprogramming can expose wrong guest physical addresses, disable guest doorbells, or route writes across function boundaries.
- HDP flush masks must match engine ownership. Using reserved engine bits or mixing request/done masks can cause hangs, false completion, stale CPU/GPU memory visibility, or firmware conflicts.
- Indirect MMIO index/data fields are sensitive because wrong offset or aperture bits can redirect register access. In a virtualized environment, this can become both a stability and isolation issue.
- Mailbox valid/ack sequencing needs timeout and ordering discipline. The macros do not enforce producer/consumer ordering or interrupt masking rules.
- MSI-X vector fields affect interrupt routing. Corrupt address, data, mask, or pending-bit interpretation can drop interrupts, signal the wrong host vector, or leave a VF stuck with masked interrupts.
- The chunk boundaries are partial: the start omits the first VF8 atomic-error fields and the end cuts VF15 mailbox definitions mid-block. The merge lane must use neighboring chunks before making complete per-VF coverage claims.

## Test and Validation Signals

Useful validation is mostly compile-time coverage plus hardware or emulated SR-IOV bring-up:

- Build AMDGPU with `amdgpu/nbif_v6_3_1.c` including `nbif/nbif_6_3_1_offset.h` and `nbif/nbif_6_3_1_sh_mask.h`; this catches missing or renamed generated macros.
- Exercise NBIF 6.3.1 device initialization paths that call `nbif_v6_3_1_funcs`, especially doorbell aperture setup, doorbell self-ring setup, HDP register remapping, and rMMIO remap selection.
- Run GFX, MES, and SDMA ring tests that issue HDP flushes through `get_hdp_flush_req_offset()`, `get_hdp_flush_done_offset()`, and `nbif_v6_3_1_hdp_flush_reg`; failures can reveal incorrect CP/SDMA request/done masks.
- In SR-IOV mode, validate VF8 through VF14 and the completed VF15 block after merge: doorbell writes, HDP flush completion, mailbox valid/ack exchange, and indirect MMIO access should work per VF without cross-function leakage.
- Verify PCIe/MSI-X interrupt setup for virtual functions by programming vector address/data/control fields, toggling mask bits, and checking pending-bit behavior.
- Inject or observe BIF atomic unsupported-request and BME-low events where possible; confirm status bits set and clear through the documented clear masks.
- Stress suspend/resume, FLR, VF reset, and GPU reset paths. Persistent doorbell, mailbox, MSI-X, and indirect-MMIO state should be reinitialized or cleared consistently.
- Run virtualization isolation tests that attempt invalid SR-IOV register and doorbell-read accesses and confirm `RCC_ERR_LOG` status is reported without exposing unauthorized register state.

## Unresolved Cross-Chunk References

Line 27551 starts inside `BIF_BX_DEV0_EPF0_VF8_BIF_ATOMIC_ERR_LOG`; the register comment and first atomic-error fields are in the previous chunk. Line 30056 ends inside `BIF_BX_DEV0_EPF0_VF15_MAILBOX_MSGBUF_TRN_DW2`; the rest of VF15 mailbox, MMIO, RCC, and MSI-X definitions are in the following chunk. The final per-file reconciliation should stitch these boundaries before summarizing complete VF8 or VF15 behavior.
