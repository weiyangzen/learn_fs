# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi.c

## Purpose
`mcdi.c` is the core Management Controller Driver Interface implementation for the Solarflare/Xilinx `sfc` NIC driver. It serializes commands to firmware, supports synchronous and asynchronous RPCs, decodes poll/event completions, handles MC reboot/assertion/BIST conditions, and exposes common firmware services for attach/detach, board configuration, firmware version, workarounds, privilege masks, NVRAM, wake-on-LAN, LEDs, and reset.

## Important APIs, Types, And Functions
Public RPC APIs are `efx_mcdi_rpc()`, `efx_mcdi_rpc_quiet()`, `efx_mcdi_rpc_start()`, `efx_mcdi_rpc_finish()`, and `efx_mcdi_rpc_async()`. Lifecycle APIs are `efx_mcdi_init()`, `efx_mcdi_detach()`, and `efx_mcdi_fini()`. Core helpers include `efx_mcdi_send_request()`, `efx_mcdi_read_response_header()`, `efx_mcdi_poll()`, `efx_mcdi_await_completion()`, `efx_mcdi_release()`, `efx_mcdi_complete_async()`, and `efx_mcdi_abandon()`.

`efx_mcdi_process_event()` dispatches MCDI events for command completions, link changes, sensors, PTP/time sync, queue flushes, DMA errors, proxy responses, MC reboot, bad assertions, and BIST. Firmware-service helpers include `efx_mcdi_print_fwver()`, `efx_mcdi_get_board_cfg()`, `efx_mcdi_log_ctrl()`, NVRAM test/info/metadata/update/read-write helpers, WOL filter helpers, workaround helpers, `efx_mcdi_get_privilege_mask()`, and optional MTD callbacks.

## Control Flow
Synchronous RPCs validate command support and buffer aliasing, acquire the single per-NIC MCDI channel by transitioning `MCDI_STATE_QUIESCENT` to `RUNNING_SYNC`, build an MCDI v1 or v2 header, submit through `efx->type->mcdi_request`, then wait by polling or events. Completion reads response headers, validates sequence numbers, maps raw firmware errors to Linux errno, copies response/error data, handles MC reboot signals, and releases the channel.

Event-mode requests wait for `MCDI_STATE_COMPLETED`; if mode switches back to polling, the waiter polls shared memory directly. Asynchronous RPCs allocate `struct efx_mcdi_async_param`, queue under `async_lock`, start only in event mode, and complete from NAPI or timer context. The async completer is called exactly once, then `efx_mcdi_release()` starts the next queued async request.

Proxy authorization is handled by detecting `MC_CMD_ERR_PROXY_PENDING`, entering `MCDI_STATE_PROXY_WAIT`, waiting for `MCDI_EVENT_CODE_PROXY_RESPONSE`, and retrying the original command on approval. Reboot/assertion/BIST paths abort proxy waits, complete synchronous requests when possible, set `new_epoch`, consume status words, and schedule the appropriate reset.

## State And Persistence Behavior
`struct efx_mcdi_iface` holds volatile per-NIC state: mode, request state, wait queues, locks, sequence number, late-completion credits, response metadata, async queue/timer, proxy state, and `new_epoch`. Persistent device effects are only through firmware commands: NVRAM writes/erases, WOL filters, LED settings, driver attach state, and resets. MTD partition `updating` is RAM state used to bracket NVRAM update sessions.

## Dependencies And Integration Points
The file depends on `net_driver.h`, `nic.h`, `io.h`, `mcdi_pcol.h`, MCDI buffer macros, timers, wait queues, spinlocks, PCI reset, and optional MTD support. It integrates with NIC type callbacks (`mcdi_request`, response reads, poll/reboot hooks), reset scheduling, link/sensor/PTP/time handlers, queue flush accounting, filter/RSS code, monitor code, MAC/PHY code, ethtool paths, and MTD partition support.

## Risks And Edge Cases
The highest-risk areas are concurrency around `state`, `seqno`, response metadata, late completions, async timer completion, and event/poll mode transitions. Timeout handling intentionally switches to `MCDI_MODE_FAIL` and schedules FLR recovery; changing this can cause permanent firmware deadlock or reset storms. Proxy wait paths must always release the interface on denial/error. NVRAM update finish maps many firmware verification codes to errno and affects persistent flash, so it is high impact.

## Test Signals
Useful tests include event-mode and poll-mode RPCs, async timeout and flush, late completion after timeout, MC reboot/assertion/BIST injection, proxy approval/denial, NVRAM update verification mapping, and builds with `CONFIG_SFC_MCDI_LOGGING` and `CONFIG_SFC_MTD`. Watch logs for response mismatches, missing completion events, MC reboot detection, MCDI timeout recovery, and NVRAM verification failures.
