# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_nx2.h

## Purpose

`qla_nx2.h` is the ISP8044/NX2 hardware-definition companion to `qla_nx2.c`. It defines 8044 register offsets, address ranges, flash command constants, reset-template opcodes and layouts, minidump entry layouts, IDC metadata, CRB register indices, and PEX-DMA descriptors. The header is a binary and MMIO contract rather than an implementation file.

## Important APIs, Types, and Constants

- IDC/reset coordination: `QSNT_ACK_TOV`, `INTENT_TO_RECOVER`, `PROCEED_TO_RECOVER`, `IDC_LOCK_RECOVERY_*`, `DONTRESET_BIT0`, `GRACEFUL_RESET_BIT1`, and IDC version constants describe multi-function recovery protocol fields.
- Address helpers: 8044 DDR/QDR/OCM/PCI address ranges and `addr_in_range()` support validated MS memory access in the implementation.
- Register map: `QLA8044_FLASH_*`, `QLA8044_DRV_LOCK*`, `QLA8044_CRB_*`, `QLA8044_PEG_*`, `QLA8044_FW_*`, `QLA8044_LINK_*`, semaphore, mailbox, reset, and interrupt-related offsets define the 8044 CRB/MMIO surface.
- Flash constants: lock timeouts, sector size, status ready value, erase/write command signatures, burst sizing, SPI control bits, and status-register write patterns drive optrom erase/write paths.
- Reset-template ABI: `struct qla8044_reset_template_hdr`, `struct qla8044_reset_entry_hdr`, `struct qla8044_poll`, `struct qla8044_rmw`, `struct qla8044_entry`, `struct qla8044_quad_entry`, and `struct qla8044_reset_template` define the flash-resident restart template and the driver's interpreter state.
- Reset opcodes: `OPCODE_WRITE_LIST`, `OPCODE_READ_WRITE_LIST`, `OPCODE_POLL_LIST`, `OPCODE_POLL_WRITE_LIST`, `OPCODE_READ_MODIFY_WRITE`, `OPCODE_SEQ_PAUSE`, `OPCODE_SEQ_END`, `OPCODE_TMPL_END`, and `OPCODE_POLL_READ_LIST` are consumed by `qla8044_process_reset_template()`.
- Minidump ABI: `struct qla8044_minidump_template_hdr` plus entry structures for CRB, cache, OCM, memory, PEX-DMA memory, ROM, mux, queue, pollrd, rddfe, rdmdio, pollwr, rdmux2, and pollrdmwr match firmware-provided dump templates.
- IDC information: `struct qla8044_idc_information` packages request descriptor and auxiliary IDC fields.
- CRB direct-register indices: `enum qla_regs` and `CRB_REG_INDEX_MAX` define the valid indices for `qla8044_rd_direct()`/`qla8044_wr_direct()`.
- PEX-DMA: `struct qla8044_pex_dma_descriptor` defines the descriptor written into MS memory to accelerate minidump memory reads.

## Control Flow

There is no standalone control flow except the inline `addr_in_range()` predicate. The reset-template and minidump structures define data-driven control flow for `qla_nx2.c`: firmware supplies a sequence of opcodes or dump entries, and the C file dispatches on these numeric command/type values. CRB index enum values also constrain direct register reads and writes through `qla8044_reg_tbl[]`.

## State and Persistence Behavior

The header defines the shape of persistent flash content, including reset templates, bootloader/firmware image locations, optrom sector operations, and minidump templates. It also names runtime CRB state that persists across cooperating PCI functions while the adapter is powered: driver active/presence, driver acknowledgement, device state, IDC version, IDC control, lock ownership, firmware heartbeat, halt status, ASIC temperature, NPAR state, and link state/speed registers. `struct qla8044_reset_template` is driver-local runtime state containing parsed template offsets, interpreter indices, scratch array values, and end/error flags.

## Dependencies

- Assumes inclusion through `qla_def.h` or related qla2xxx headers that already provide kernel integer types, `bool`, `u64`, `uint*_t`, `__packed`, bit macros, and shared 82xx definitions such as `MIU_TA_CTL_*`.
- Shares minidump entry type constants and debug opcodes with `qla_nx.h`; `qla_nx2.c` mixes 8044-specific structures with 82xx minidump opcodes.
- The packed structures are consumed by firmware/flash parsing code and cannot be treated as ordinary in-memory-only C structs.

## Integration Points

- Included from `qla_def.h`, making 8044 definitions visible driver-wide.
- `qla_nx2.c` is the primary consumer for every register constant, reset opcode, and packed structure in this header.
- `qla_init.c`, `qla_mbx.c`, `qla_attr.c`, `qla_os.c`, and BSG/mailbox paths reference selected constants and exported 8044 operations through `qla_gbl.h`.
- `struct qla8044_reset_template` is embedded in `struct scsi_qla_host`, so reset template state is per virtual host.

## Risks and Edge Cases

- Packed reset/minidump structures are firmware ABI. Alignment, padding, and field-width changes would corrupt parsing.
- Many constants encode hardware magic values with limited self-description. Changing them requires hardware documentation or empirical validation.
- `addr_in_range()` uses inclusive low/high bounds; callers must pass the correct maximum address and ensure transfer size does not extend beyond the range after the starting address is accepted.
- `CRB_REG_INDEX_MAX` must stay synchronized with `enum qla_regs` and `qla8044_reg_tbl[]`; mismatch can reject valid registers or allow out-of-bounds table access.
- Reset-template sizes and offsets are fixed around `QLA8044_RESTART_TEMPLATE_SIZE`; larger future templates would require implementation changes.
- Flash burst constants constrain optrom writes to 2 through 64 dwords; callers and flash descriptors must agree with those constraints.

## Test Signals

- Compile-time coverage should catch missing constants or struct type changes in `qla_nx2.c`.
- Firmware-template tests should validate that reset-template headers with `RESET_TMPLT_HDR_SIGNATURE` and `QLA8044_RESET_SEQ_VERSION` parse into correct init/start/stop offsets.
- Minidump tests should validate that each packed entry layout matches firmware-provided template sizes and entry-type dispatch.
- Flash tests should exercise sector erase, status writes, and buffer/dword write modes using the constants here.
- IDC tests should verify lock recovery state bits, owner encoding, and dont-reset/graceful-reset controls across multiple functions.
