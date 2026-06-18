# sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst_pvt.c

## Purpose
This file contains private helper routines for SST MMIO access, firmware-state updates, IPC wait timeouts, IPC message/block allocation, generic IPC construction, runtime PM put, header filling, private ID allocation, stream validation/lookup, IMR address relocation, and queued IPC dispatch.

## Important APIs, types, and functions
MMIO helpers are `sst_shim_write()`, `sst_shim_read()`, `sst_reg_read64()`, `sst_shim_write64()`, and `sst_shim_read64()`. Synchronization helpers are `sst_set_fw_state_locked()`, `sst_wait_timeout()`, `sst_create_ipc_msg()`, `sst_create_block_and_ipc_msg()`, and `sst_assign_pvt_id()`. Message construction is handled by `sst_prepare_and_post_msg()`, `sst_fill_header_mrfld()`, and `sst_fill_header_dsp()`. Stream helpers are `sst_clean_stream()`, `sst_validate_strid()`, `get_stream_info()`, and `get_stream_id_mrfld()`. `relocate_imr_addr_mrfld()` maps physical DDR base into the firmware virtual IMR window.

## Control flow
Most firmware commands call `sst_prepare_and_post_msg()`: allocate a private ID, optionally create a wait block, create an IPC message, fill the host and DSP headers, copy payload data, post synchronously or queue asynchronously, wait for response when requested, duplicate returned data for the caller, free the block, and clear the private-ID bit. `sst_wait_timeout()` waits up to `SST_BLOCK_TIMEOUT`; on timeout it marks firmware reset and returns `-EBUSY`.

## State and persistence behavior
The helper mutates `ctx->sst_state`, `ctx->pvt_id`, `ctx->ipc_dispatch_list`, stream status fields, and runtime PM usage through `pm_runtime_put_autosuspend()`. Message and block allocations are transient.

## Dependencies and integration points
It is shared by loader, IPC, stream, interface, PCI, and PM code. It depends on waitqueues, spinlocks, runtime PM, firmware IPC structures, and MMIO accessors.

## Risks and edge cases
`sst_prepare_and_post_msg()` assumes large messages have allocated mailbox data before copying DSP headers. If message allocation succeeds but block allocation fails, the large-message mailbox buffer is not separately freed in the error path. Private IDs are limited by `SST_MAX_BLOCKS` and use bit operations on `volatile long unsigned pvt_id`. Timeouts forcibly set firmware reset state, affecting unrelated users.

## Test signals
Test IPC construction for large/short, sync/async, response/no-response combinations; private ID exhaustion; wait timeout; stream ID validation; pipe-to-stream lookup; IMR relocation math; runtime PM put errors; and dispatch-list posting while IPC is busy/free.
