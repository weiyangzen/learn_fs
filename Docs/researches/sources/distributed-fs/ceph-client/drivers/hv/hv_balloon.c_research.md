<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_balloon.c -->
# sources/distributed-fs/ceph-client/drivers/hv/hv_balloon.c

## Purpose

`hv_balloon.c` implements the Hyper-V Dynamic Memory service. It negotiates the dynamic-memory protocol with the host, reports guest memory pressure, handles balloon-up and unballoon requests, hot-adds host-provided memory ranges, exposes debugfs state, and optionally reports cold free pages back to Hyper-V through the memory heat hint hypercall.

## Important APIs, Types, and Functions

- Dynamic memory protocol structures include `dm_header`, `dm_version_request`, `dm_capabilities`, `dm_status`, `dm_balloon`, `dm_balloon_response`, `dm_unballoon_request`, `dm_hot_add`, `dm_hot_add_response`, and `dm_info_msg`.
- `struct hv_dynmem_device dm_device` stores protocol state, completions, worker state, hot-add region lists, counters, negotiated version, page reporting info, and the bound `hv_device`.
- Hot-add helpers include `hv_hotadd_state`, `hv_hotadd_gap`, `process_hot_add()`, `handle_pg_range()`, `hv_mem_hot_add()`, `hv_online_page()`, and `hv_memory_notifier()`.
- Balloon helpers include `compute_balloon_floor()`, `alloc_balloon_pages()`, `free_balloon_pages()`, `balloon_up()`, and `balloon_down()`.
- `balloon_onchannelcallback()` dispatches host messages.
- `balloon_connect_vsp()` performs VMBus open, version negotiation, and capability reporting.
- `hv_free_page_report()`, `enable_page_reporting()`, and `disable_page_reporting()` integrate with Linux page reporting.
- `balloon_probe()`, `balloon_remove()`, `balloon_suspend()`, and `balloon_resume()` are the VMBus driver lifecycle hooks.

## Control Flow

Probe computes hot-add chunk size, initializes completions, work items, locks, hot-add lists, memory hotplug callbacks, and then calls `balloon_connect_vsp()`. The connect path opens the VMBus channel, sends the newest dynamic-memory version request, waits for host acceptance, falls back through older versions in `version_resp()`, sends capabilities, and waits for host acceptance. After connection, page reporting is enabled and a kernel thread posts memory status every second after the initial delay.

Host messages are received in `balloon_onchannelcallback()`. Version and capability responses complete the negotiation wait. Balloon requests schedule `balloon_up()`, which respects a computed memory floor, allocates 2 MB chunks first then page-size chunks, marks pages offline, updates balloon counters, and sends one or more range responses. Unballoon requests free returned pages and send a final response when the host has no more ranges. Hot-add requests schedule `hot_add_req()`, which creates or extends hot-add regions, calls `add_memory()` in memory-block-sized chunks, waits briefly for onlining, and reports partial or permanent failure semantics back to the host.

## State and Persistence Behavior

`dm_device` is a single global device instance. Persistent counters include ballooned, added, and onlined pages. Hot-add ranges and gaps persist in `ha_region_list` so later backing requests and memory-offline notifications can distinguish backed versus unbacked PFNs. `trans_id` monotonically tags protocol messages. `last_post_time` rate-limits pressure reports. Hibernation support disables actual balloon/hot-add behavior while still advertising host-required capability bits and ignoring requests.

## Dependencies and Integration Points

The driver integrates with VMBus, Linux memory hotplug, page reporting, debugfs, `vm_memory_committed()`, `si_mem_available()`, Hyper-V extended capability queries from `hv_common.c`, per-CPU hypercall input pages, and `hv_trace_balloon.h` tracepoints. It registers as the `HV_DM_GUID` VMBus driver.

## Risks and Edge Cases

This file has high state complexity. Risks include stale hot-add gaps, memory-offline accounting underflow, page reporting hypercall failures, races between pressure reports and transaction IDs, hibernation interactions, and partial balloon response rollback if `vmbus_sendpacket()` fails. Non-4K page-size guests disable ballooning. ARM64 disables hot-add because the protocol lacks NUMA placement information. Suspend/resume must stop the thread and work before closing the channel.

## Test Signals

Test version fallback, capability rejection, balloon floor enforcement, 2 MB and 4 KB allocation paths, unballoon freeing, hot-add with explicit and inferred regions, gaps/backing in existing regions, memory on/offline notifications, page reporting invalid-parameter downgrade, debugfs counters, hibernation ignoring behavior, and suspend/resume reconnection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_balloon.c -->
