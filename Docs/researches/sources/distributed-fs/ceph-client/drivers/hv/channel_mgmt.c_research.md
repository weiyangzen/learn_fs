<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/channel_mgmt.c -->
# sources/distributed-fs/ceph-client/drivers/hv/channel_mgmt.c

## Purpose

`channel_mgmt.c` implements VMBus channel discovery, offer/rescind handling, channel object lifetime, relative-id mapping, integration-component negotiation helpers, CPU target selection, and dispatch for host channel protocol messages. It is the management side of the Hyper-V VMBus core: it turns host offers into `hv_device` instances, tracks primary and sub-channel lists, handles hibernation re-offers, and resolves host responses for synchronous channel operations.

## Important APIs, Types, and Functions

- `vmbus_devs[]` maps well-known Hyper-V GUIDs to internal device types, performance-channel hints, preferred ring sizes, and isolation allow-lists.
- `vmbus_prep_negotiate_resp()` validates IC negotiation packets and picks the best framework and service version supported by both guest and host.
- `alloc_channel()`, `free_channel()`, `vmbus_channel_map_relid()`, and `vmbus_channel_unmap_relid()` manage `struct vmbus_channel` objects and the global relid lookup table.
- `vmbus_process_offer()` and `vmbus_add_channel_work()` classify primary versus sub-channel offers, bind channels to CPUs, insert them into global or sub-channel lists, and defer device registration or sub-channel callbacks to dedicated workqueues.
- `vmbus_onoffer()`, `vmbus_onoffer_rescind()`, `vmbus_hvsock_device_unregister()`, and `hv_process_channel_removal()` implement offer, rescind, hvsock unregister, and final removal.
- `vmbus_initiate_unload()` and `vmbus_wait_for_unload()` send and wait for host unload acknowledgement, including a crash path that polls SynIC message pages directly.
- `channel_message_table[]` and `vmbus_onmessage()` dispatch host channel protocol messages to response handlers such as open, GPADL create/teardown, modify-channel, version, and unload responses.
- `vmbus_request_offers()`, `vmbus_set_sc_create_callback()`, and `vmbus_set_chn_rescind_callback()` are exported integration points used by VMBus bus and client drivers.

## Control Flow

Host offers enter `vmbus_onoffer()`. The code validates isolation/confidential-channel constraints, checks whether the offer is a hibernation re-offer for an existing primary channel, or allocates a new channel. `vmbus_setup_channel_state()` records connection IDs, monitor bits, offer contents, and device type. `vmbus_process_offer()` then serializes with CPU hotplug and `channel_mutex`, detects primary/sub-channel relationships, assigns `target_cpu`, tracks channels that must close before suspend, maps the child relid, and queues primary and sub-channel processing on separate workqueues to avoid driver-probe and sub-channel deadlocks.

Rescinds enter `vmbus_onoffer_rescind()`. It waits for all in-progress offers to finish, grabs one rescind reference under `channel_mutex`, disables the channel callback, marks the channel rescinded, wakes any waiter blocked on that channel, waits for probe completion, and then invokes a driver rescind callback, unregisters the device, or removes an unbound sub-channel. Channel operation responses scan `vmbus_connection.chn_msg_list` under `channelmsg_lock`, match child relids/open IDs/GPADL handles, copy the host response into the waiting `msginfo`, and complete its wait event.

## State and Persistence Behavior

Persistent state lives primarily in `vmbus_connection`: `chn_list`, per-relid `channels[]`, channel message wait list, workqueues, completion objects, and suspend counters. Each `vmbus_channel` persists until the driver core or sub-channel cleanup drops the kobject. The relid map is updated with explicit ordering via `virt_store_mb()` because interrupt-side event scheduling can dereference it on other CPUs. CPU allocation state is stored in `hv_context.hv_numa_map` and reset when performance channels are removed. The unload path changes `conn_state` atomically to prevent duplicate unloads.

## Dependencies and Integration Points

This file depends on `hyperv_vmbus.h`, `<linux/hyperv.h>`, SynIC message pages from `hv.c`, `vmbus_connection` from `connection.c`, VMBus driver-core helpers from `vmbus_drv.c`, channel open/close helpers from `channel.c`, and tracepoints from `hv_trace.h`. Client drivers use its exported callbacks for sub-channel creation and rescind notification. Utility drivers use `vmbus_prep_negotiate_resp()`.

## Risks and Edge Cases

The key risks are ordering bugs between offer and rescind processing, relid reuse after suspend or hibernation, and CPU hotplug races while channels are bound to target CPUs. The code has explicit barriers and long comments for those cases, so future changes should preserve the documented ordering. Isolation checks must stay synchronized with `vmbus_devs[]`; otherwise confidential guests may accept unsupported devices. `vmbus_wait_for_unload()` is intentionally polling and bounded, but crash paths can still continue without host acknowledgement. Channel removal must not access a channel after driver-core unregister may free it.

## Test Signals

Useful signals include boot-time offer enumeration completing, primary and sub-channel probe ordering under synchronous probe drivers, rescind during open/GPADL waits, hvsock suspend/resume relid invalidation, VMBus unload during crash and non-crash paths, CPU hotplug migration of performance channels, and tracepoints for offer, rescind, open result, GPADL, modify-channel, request-offers, and relid release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/channel_mgmt.c -->
