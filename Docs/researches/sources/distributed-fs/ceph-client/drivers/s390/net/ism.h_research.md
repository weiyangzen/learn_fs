# sources/distributed-fs/ceph-client/drivers/s390/net/ism.h

## Purpose
`ism.h` defines the s390 ISM PCI device command ABI, event queue structures, summary-bit area layout, device state container, and low-level zpci command/move helpers used by `ism_drv.c`. It is the wire/register contract between the Linux ISM driver, DIBS clients, and the s390 PCI instruction interface.

## Important APIs, Types, And Functions
- Command codes: `ISM_REG_SBA`, `ISM_REG_IEQ`, `ISM_READ_GID`, VLAN commands, query commands, DMB register/unregister, signal IEQ, and unregister commands.
- Event constants: `enum ism_event_type` and `enum ism_event_code`.
- Request/response headers: `struct ism_req_hdr` and `struct ism_resp_hdr`.
- Command unions with alignment requirements: `ism_reg_sba`, `ism_reg_ieq`, `ism_read_gid`, `ism_qi`, `ism_query_rgid`, `ism_reg_dmb`, `ism_sig_ieq`, `ism_unreg_dmb`, `ism_cmd_simple`, and `ism_set_vlan_id`.
- Event and shared-memory layouts: `struct ism_eq_header`, `struct ism_event`, `struct ism_eq`, and `struct ism_sba`.
- Runtime device state: `struct ism_dev` holds command lock, DIBS/PPCI pointers, coherent SBA/IEQ DMA mappings, DMB allocation bitmap, and event queue index.
- Inline hardware helpers: `__ism_read_cmd()`, `__ism_write_cmd()`, and `__ism_move()` use zpci load/store instructions.

## Control Flow
`ism_drv.c` fills the command unions, writes payload after the request header, writes the header to trigger a command, then reads the response header and payload. DMB movement uses `ISM_CREATE_REQ()` to compose a device memory buffer request and `__ism_move()` to store data through zpci. IRQ handling reads and clears `struct ism_sba` bits and scans `struct ism_eq` entries defined here.

## State And Persistence Behavior
The header describes hardware-visible memory that persists only while the driver has registered coherent pages with the device. `struct ism_sba` contains summary/event bits, DMB bits, and masks updated by the device and cleared by the interrupt handler. `struct ism_eq` contains an event ring. `struct ism_dev` tracks the live software view.

## Dependencies And Integration Points
This file depends on Linux PCI, spinlock, DIBS, and s390 zpci instruction headers. It is directly consumed by `ism_drv.c` and indirectly defines the DIBS provider behavior exposed to clients. Alignment attributes are integration-critical for the device ABI.

## Risks
- Command unions and alignment must match hardware expectations exactly. Field reordering or type-size changes can break device commands.
- `__ism_read_cmd()` and `__ism_write_cmd()` assume 8-byte granularity and command lengths consistent with the hardware protocol.
- `struct ism_sba` reserves the first DMB word for alignment; bitmap indexing must consistently account for `ISM_DMB_BIT_OFFSET`.
- UUID/GID mapping comments indicate compatibility behavior; changing GID layout can break remote matching.

## Test Signals
- Hardware or emulator tests should verify every command union length/alignment and command code path.
- IRQ tests should validate SBA bit indexing and IEQ ring entry parsing.
- DIBS client tests should validate DMB registration, move requests across page boundaries, VLAN operations, and event signaling.
