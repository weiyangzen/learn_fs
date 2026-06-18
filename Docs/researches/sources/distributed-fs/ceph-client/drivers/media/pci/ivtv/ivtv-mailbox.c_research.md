# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-mailbox.c

## Purpose
This file implements the mailbox transport used to send CX2341x encoder, decoder, and OSD firmware API commands. It handles mailbox claiming, command argument/result marshalling, caching idempotent commands, timeouts, special DMA mailbox behavior, and variadic helper wrappers.

## Important APIs, Types, and Functions
Public functions are `ivtv_api`, `ivtv_api_func`, `ivtv_vapi_result`, `ivtv_vapi`, `ivtv_api_get_data`, and `ivtv_mailbox_cache_invalidate`. Internals include `struct ivtv_api_info`, the `api_info` command metadata table, `try_mailbox`, `get_mailbox`, `write_mailbox`, `clear_all_mailboxes`, and `ivtv_api_call`.

## Control Flow
Callers submit a command and arguments. `ivtv_api_call` validates the command, clears unused data words, optionally skips cached commands issued with identical data, chooses the encoder or decoder mailbox region, then either claims a DMA mailbox or searches non-DMA mailboxes. For result commands it polls briefly, then sleeps or delays until firmware marks the mailbox done or a timeout expires, copies result words back, clears flags, and releases the busy bit. `ivtv_api` retries once on busy.

## State and Persistence Behavior
The file mutates firmware mailbox MMIO/shared memory, `mbdata->busy` bits, and `itv->api_cache[cmd]` data and timestamps. Cached commands persist for up to 30 minutes unless invalidated. It can clear all mailbox flags after failure, which resets driver/firmware mailbox ownership state.

## Dependencies and Integration Points
It depends on CX2341x command IDs, ivtv mailbox memory mappings, jiffies/timeouts, MMIO read/write helpers, sleep/delay helpers, and the many ivtv modules that control firmware through `ivtv_vapi` or `ivtv_vapi_result`.

## Risks
Mailbox ownership is central to device liveness. Busy-bit leaks, bad timeout choices, over-aggressive mailbox clearing, or incorrect cache eligibility can desynchronize driver and firmware. DMA commands intentionally do not wait for normal results, so completion is validated by IRQ paths instead.

## Test Signals
Signals include firmware ping/version calls, repeated cached OSD/control calls, high-volume DMA scheduling under load, timeout injection, mailbox busy recovery, invalid command validation, and firmware restart followed by cache invalidation.
