# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_adminq.h

## Purpose
Declares the i40e Admin Queue ring, command-detail, event, and top-level queue state structures, descriptor accessor macros, default alignment/sizing constants, firmware-error to POSIX-error conversion helper, and descriptor initialization prototype.

## Important APIs, Types, and Functions
`I40E_ADMINQ_DESC` indexes a descriptor ring, and `I40E_ADMINQ_DETAILS` indexes the ASQ command-detail array. `I40E_ADMINQ_DESC_ALIGNMENT`, `I40E_AQ_LARGE_BUF`, and `I40E_ASQ_CMD_TIMEOUT` define memory alignment, large-buffer threshold, and synchronous command timeout. `struct i40e_adminq_ring` stores descriptor DMA memory, command/event buffer metadata, per-descriptor DMA buffer arrays, count, receive buffer length, and ring indices. `struct i40e_asq_cmd_details` carries callback, cookie, flag masks, async/postpone controls, and optional writeback descriptor. `struct i40e_arq_event_info` is the caller-facing event container. `struct i40e_adminq_info` owns ASQ/ARQ rings, sizes, firmware/API versions, mutexes, and last statuses. `i40e_aq_rc_to_posix` maps firmware AQ return codes to Linux errors. `i40e_fill_default_direct_cmd_desc` initializes a direct command descriptor.

## Control Flow
The header has only inline control flow in `i40e_aq_rc_to_posix`, which bounds-checks the firmware return code and maps it through a static table. Runtime AdminQ behavior is implemented in `i40e_adminq.c`.

## State and Persistence Behavior
The declared structs define long-lived AdminQ state inside `struct i40e_hw`. Descriptor rings and command/event buffers are DMA-visible to firmware and persist for the lifetime of the initialized AdminQ. Mutexes serialize ASQ sends and ARQ event cleaning. Last-status fields preserve the most recent firmware return values but can race if read outside the locked v2 send path.

## Dependencies and Integration Points
Includes Linux mutex support, i40e allocation helpers, and AdminQ command descriptor definitions. It is consumed by AdminQ C code, firmware command wrappers in common/prototype code, and PF lifecycle code that initializes/shuts down firmware communication.

## Risks
The ring accessor macros assume descriptor and detail buffers are allocated and typed exactly as expected. Alignment must remain compatible with hardware DMA requirements. The POSIX mapping table must stay synchronized with `enum libie_aq_err`; unknown codes map to `-ERANGE`. Async/postpone fields in `i40e_asq_cmd_details` are subtle because callers control whether tail is rung and whether completion is waited for.

## Test Signals
Compile all AdminQ users, verify descriptor alignment, ASQ/ARQ ring index access, firmware error mappings including out-of-range codes, direct descriptor initialization, async/postpone command callers, and lockdep coverage for ASQ/ARQ mutex-protected access.
