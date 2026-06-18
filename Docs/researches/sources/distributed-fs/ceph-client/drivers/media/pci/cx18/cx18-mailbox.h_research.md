# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-mailbox.h

## Purpose
This header defines cx18 mailbox constants, firmware mailbox layouts, MDL acknowledgment layout, and mailbox/API function prototypes.

## Important APIs, Types, and Functions
Constants include `MAX_MB_ARGUMENTS`, `CX2341X_MBOX_MAX_DATA`, reserved handles, and processor IDs `APU`, `CPU`, `EPU`, and `HPU`. `struct cx18_mdl_ack` describes firmware completion data for MDLs. `struct cx18_mailbox` defines request/ack fields, reserved space, command, up to six args, and error. Prototypes include `cx18_api()`, `cx18_vapi_result()`, `cx18_vapi()`, `cx18_api_func()`, `cx18_api_epu_cmd_irq()`, and `cx18_in_work_handler()`.

## Control Flow
No executable flow lives in the header. It defines the shared memory protocol consumed by the outgoing API path, IRQ path, workqueue path, and SCB structures.

## State and Persistence
Mailbox instances live in the firmware SCB memory region and are mirrored into `cx18_in_work_order` objects for deferred handling. The header itself stores no state.

## Dependencies and Integration Points
The mailbox structures are dictated by firmware and must match `cx18-scb.h` layout. The API function declarations connect cx2341x controls, stream management, firmware init, IRQ handling, and incoming work.

## Risks and Edge Cases
Changing structure layout, reserved fields, argument count, or processor IDs would break firmware communication. `CX2341X_MBOX_MAX_DATA` is larger than cx18 mailbox args for compatibility, so callers must respect `MAX_MB_ARGUMENTS` when sending commands.

## Test Signals
Successful firmware API commands, DMA completion processing, no mailbox timeout logs, and correct argument/error propagation are the main validation signals.
