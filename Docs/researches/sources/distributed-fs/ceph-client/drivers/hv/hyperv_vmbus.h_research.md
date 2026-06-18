# sources/distributed-fs/ceph-client/drivers/hv/hyperv_vmbus.h

## Purpose

`hyperv_vmbus.h` is the private VMBus/SynIC coordination header for the Hyper-V guest bus. It defines monitor-page layouts, per-CPU SynIC state, global Hyper-V context, connection/channel bookkeeping, ring-buffer APIs, message dispatch metadata, utility-device states, debug hooks, and helpers used by VMBus channel and utility drivers.

## Important APIs, Types, and Functions

- `struct hv_per_cpu_context` stores host/paravisor SynIC message/event pages, a decrypted `post_msg_page` for TDX/paravisor `HVCALL_POST_MESSAGE`, and per-CPU message tasklet state.
- `struct hv_context` carries the guest ID, per-CPU contexts, and NUMA CPU allocation map.
- `struct vmbus_connection` is the central VMBus state object: connection state, interrupt pages, monitor pages, channel lists/maps, workqueues, suspend counters, and offer-delivery completions.
- Ring-buffer API declarations include `hv_ringbuffer_init`, `hv_ringbuffer_write`, `hv_ringbuffer_read`, and cleanup/preinit helpers.
- Message/connection APIs include `hv_init`, `hv_post_message`, `hv_synic_init`, `vmbus_connect`, `vmbus_post_msg`, `vmbus_on_event`, and `vmbus_on_msg_dpc`.
- `vmbus_signal_eom()` safely clears a SynIC message slot and writes the EOM MSR if another message is pending.
- CPU allocation helpers (`hv_is_allocated_cpu`, `hv_set_allocated_cpu`, `hv_clear_allocated_cpu`, `hv_update_allocated_cpus`) manage NUMA affinity for performance channels.

## Control Flow

VMBus initialization allocates SynIC pages per CPU, connects to the host using `vmbus_connect`, receives channel offers through message handlers, and tracks channels by relid in `vmbus_connection.channels`. Channel interrupts are represented by bits in the send/receive interrupt pages; `vmbus_send_interrupt()` sets the relid bit for host notification. Incoming events and messages are dispatched via per-CPU tasklets/workqueues according to `channel_message_table` entries, where handlers are explicitly marked blocking or non-blocking.

## State and Persistence Behavior

`hv_context` and `vmbus_connection` are long-lived global state. Per-channel state persists through the channel list and relid map until unmap/free. Suspend behavior is represented by `ignore_any_offer_msg`, close-on-suspend counters, and completions. SynIC and monitor pages are memory shared with Hyper-V or the paravisor and must be treated as externally mutable.

## Dependencies and Integration Points

The header depends on Linux list, atomic, tasklet, interrupt, bit operation, Hyper-V UAPI/internal definitions, `hvhdk.h`, and `hv_trace.h`. It integrates with VMBus channel management, Hyper-V utility services (`kvp`, `vss`), ring-buffer sysfs/debugfs, and confidential-computing paths that distinguish host-accessible and paravisor-only SynIC pages.

## Risks and Edge Cases

Shared SynIC pages are host/hypervisor visible in non-CoCo configurations, so consumers must validate data read from them. `vmbus_signal_eom()` has crash-path races and uses `try_cmpxchg` to avoid clearing a newly delivered message. CPU allocation helpers assume `channel_mutex` is held. Channel count limits depend on Hyper-V page size and event-flag counts.

## Test Signals

Useful signals include VMBus connect/disconnect tests, channel offer/rescind handling, relid map/unmap correctness, ring-buffer read/write coverage, suspend/resume channel cleanup, confidential VM post-message behavior, EOM pending-message delivery, debugfs/sysfs creation, and lockdep coverage around channel mutex and tasklet/workqueue dispatch.
