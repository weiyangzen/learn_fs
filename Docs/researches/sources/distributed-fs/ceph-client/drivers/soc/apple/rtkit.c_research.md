# sources/distributed-fs/ceph-client/drivers/soc/apple/rtkit.c

## Purpose
This file implements the Apple RTKit IPC protocol library used by client drivers to communicate with Apple coprocessors over the Apple mailbox and shared memory buffers.

## Important APIs, Types, And Functions
Exports include `apple_rtkit_init()`, `devm_apple_rtkit_init()`, `apple_rtkit_free()`, `apple_rtkit_boot()`, `apple_rtkit_shutdown()`, `apple_rtkit_poweroff()`, `apple_rtkit_idle()`, `apple_rtkit_quiesce()`, `apple_rtkit_wake()`, `apple_rtkit_start_ep()`, `apple_rtkit_send_message()`, `apple_rtkit_poll()`, `apple_rtkit_is_running()`, and `apple_rtkit_is_crashed()`. Key internal handlers cover management hello/endpoint map/power acks, shared buffer requests, crashlog, ioreport, syslog, oslog, and RX work dispatch.

## Control Flow
Initialization obtains a mailbox, installs the RX callback, creates an ordered high-priority workqueue, and starts the mailbox. RX callback checks endpoint discovery, optionally lets clients handle app endpoints early, then queues work. Management hello negotiates protocol version. Endpoint-map messages set endpoint bits, start required system endpoints, and complete boot discovery. Boot waits for endpoint map and IOP power ACK, then sets AP power on. Send paths enforce crash/running checks for application endpoints and use DMA barriers before mailbox writes. Shutdown, idle, quiesce, poweroff, and wake are implemented as AP/IOP power-state message exchanges plus optional reinitialization.

## State, Persistence, And Dependencies
State includes endpoint bitmap, completions, version, boot result, AP/IOP power states, crash flag, shared-memory buffers, syslog buffer, and ordered workqueue. Dependencies include the Apple mailbox, DMA coherent memory or client `shmem_setup`/`shmem_destroy`, completions, bitfield macros, and public client ops.

## Integration Points
Client drivers provide `struct apple_rtkit_ops` callbacks for receiving messages, early handling, shared memory setup, and crash notification. RTKit manages system endpoints internally and passes application endpoints from `0x20` upward to clients.

## Risks
Shared state is largely protected by sequencing rather than locks; RX work during reinit is handled by stopping mailbox and flushing the workqueue. `apple_rtkit_common_rx_get_buffer()` trusts firmware-requested sizes and relies on DMA allocation or client validation. Syslog index check uses `idx > n_entries`, which may allow `idx == n_entries`. Failure to allocate RX work silently drops messages. Crash state blocks later sends.

## Test Signals
Test protocol version negotiation, endpoint map pagination, system endpoint startup, boot timeouts, AP/IOP power-state transitions, app endpoint send gating, shared memory request paths with and without client mapping, syslog log entries, crashlog copy and callback, reinit during traffic, and mailbox poll fallback.
