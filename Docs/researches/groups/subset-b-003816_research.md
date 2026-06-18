# subset-b-003816 Research

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/connection.c -->
# sources/distributed-fs/ceph-client/drivers/hv/connection.c

## Purpose

`connection.c` owns the global VMBus connection to the Hyper-V host. It negotiates the VMBus protocol version, allocates shared interrupt and monitor pages, creates management workqueues, posts channel protocol messages, dispatches per-channel event callbacks, and signals host events.

## Important APIs, Types, and Functions

- `struct vmbus_connection vmbus_connection` is the exported global connection state.
- `vmbus_proto_version` records the negotiated host protocol version.
- `vmbus_negotiate_version()` sends `CHANNELMSG_INITIATE_CONTACT`, waits for `CHANNELMSG_VERSION_RESPONSE`, and records the host-selected message connection ID for newer protocols.
- `vmbus_connect()` creates workqueues, initializes lists and locks, allocates interrupt and monitor pages, decrypts monitor pages when needed, tries supported protocol versions newest to oldest, and allocates the relid channel table.
- `vmbus_disconnect()` unloads from the host, destroys workqueues, and frees or re-encrypts shared pages.
- `relid2channel()` safely looks up a mapped channel by relid.
- `vmbus_on_event()` invokes a channel callback and manages batched ring-buffer read completion/rescheduling.
- `vmbus_post_msg()` wraps `hv_post_message()` with retry/backoff and VMBus-specific status translation.
- `vmbus_set_event()` signals a channel to the host through monitor interrupts or hypercalls, including SNP/TDX paravisor paths.

## Control Flow

Connection starts in `vmbus_connect()`: state becomes `CONNECTING`, four workqueues are created, shared pages are allocated, monitor pages are decrypted and zeroed, and a reusable `msginfo` is allocated. The version loop calls `vmbus_negotiate_version()` with each allowed version until the host accepts. For protocol 5.0 and newer, initiate-contact uses connection ID 4, carries the message SINT and VTL, and later switches to the host-returned connection ID. Confidential VMBus is advertised only for version 6.0 and newer. On success the global relid table is allocated and state is `CONNECTED`; on failure cleanup funnels through `vmbus_disconnect()`.

Channel events enter `vmbus_on_event()`, which reads the current callback pointer, invokes it if present, and for batched channels calls `hv_end_read()` followed by `hv_begin_read()` and tasklet rescheduling when more packets are pending. Outgoing management messages use `vmbus_post_msg()` with exponential microsecond/millisecond delays and special handling for old hosts that reject connection ID 4 during initiate-contact.

## State and Persistence Behavior

`vmbus_connection` persists globally and contains connection state, workqueues, relid table, shared interrupt page split into send/receive halves, monitor pages, message wait list, and channel list. The negotiated protocol gates feature use throughout the VMBus stack. Monitor page encryption state is deliberately conservative: if decryption fails, the page pointer is nulled and memory is leaked rather than returned with unknown encryption state. Message posting itself uses per-CPU hypercall pages managed by `hv_common.c` and `hv.c`.

## Dependencies and Integration Points

This file integrates `hv_post_message()` from `hv.c`, unload and message handlers from `channel_mgmt.c`, ring-buffer helpers from `ring_buffer.c`, channel callbacks from client drivers, and Hyper-V isolation helpers from `hv_common.c` and architecture code. It exports `vmbus_connection`, `vmbus_proto_version`, and `vmbus_set_event()` for the broader VMBus driver.

## Risks and Edge Cases

Error unwinding must handle partially created workqueues and partially allocated/decrypted pages. `vmbus_disconnect()` destroys workqueues only if pointers are non-null but does not reset all workqueue pointers, so repeated connect/disconnect flows rely on higher-level lifecycle sequencing. `vmbus_post_msg()` can sleep or busy-wait depending on `can_sleep` and delay size; callers must choose correctly for crash or atomic contexts. Event callbacks can disappear during driver unload, so `vmbus_on_event()` reads them with `READ_ONCE()`.

## Test Signals

Test version fallback with `max_version`, protocol 5+ message connection IDs, isolation requiring at least Win10 v5.2, confidential-channel negotiation, monitor-page encryption failure paths, post-message retries for invalid connection and insufficient buffer statuses, batched versus direct channel read modes, and event signaling in normal, nested, SNP, and TDX paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/connection.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv.c -->
# sources/distributed-fs/ceph-client/drivers/hv/hv.c

## Purpose

`hv.c` provides low-level Hyper-V runtime services for the VMBus driver: per-CPU Hyper-V context allocation, hypervisor message posting, Synthetic Interrupt Controller page allocation and register programming, event-page cleanup during CPU hotplug, and channel CPU migration when a CPU goes offline.

## Important APIs, Types, and Functions

- `struct hv_context hv_context` is the exported global per-CPU Hyper-V context.
- `hv_init()` allocates `struct hv_per_cpu_context` storage.
- `hv_post_message()` formats `struct hv_input_post_message` and posts it via direct, nested, GHCB, or TDX hypercall paths.
- `hv_synic_alloc()` and `hv_synic_free()` allocate/free per-present-CPU SynIC message/event pages, paravisor pages, optional TDX post-message pages, and `hv_numa_map`.
- `hv_synic_init()` enables hypervisor and optional paravisor SynIC pages and interrupts and initializes the legacy synthetic timer.
- `hv_synic_cleanup()` migrates channels away from an offlined CPU when possible, waits for pending event bits to drain, disables SynIC/timer state, and disables per-CPU IRQs.
- `hv_hyp_synic_enable_regs()`, `hv_hyp_synic_disable_regs()`, and paravisor equivalents program SIMP, SIEFP, SINT, and SCONTROL registers.

## Control Flow

Initialization starts with `hv_init()`, then `hv_synic_alloc()` zeroes all per-CPU contexts and allocates the pages required for the current environment. Non-root, non-paravisor guests allocate hypervisor SynIC pages directly; root and paravisor environments memremap host-provided pages when enabling registers. Confidential VMBus additionally allocates encrypted paravisor SynIC pages. `hv_synic_init()` enables paravisor registers first when confidential, then enables hypervisor registers, enables interrupts through the correct controller, and sets up the synthetic timer.

Message posting disables local interrupts, chooses the per-CPU input page or TDX decrypted post-message page, copies the payload, and selects the hypercall path. CPU cleanup first refuses to offline the connect CPU while connected. For other CPUs it scans primary and sub-channels under `channel_mutex`, uses `vmbus_channel_set_cpu()` to migrate channels, waits briefly for event flags to clear, and then disables timer, SynIC pages, and IRQs.

## State and Persistence Behavior

The global `hv_context` persists for the VMBus lifetime. Per-CPU contexts hold SynIC message/event pages, tasklets, and optional paravisor/post-message pages. Allocation and freeing deliberately leak pages if encryption state cannot be restored safely. `hv_context.hv_numa_map` tracks CPU assignment for performance channels and is consumed by `channel_mgmt.c`. SynIC page pointers are temporarily set to memremapped host/paravisor pages while a CPU is online and cleared during disable.

## Dependencies and Integration Points

This file depends on architecture Hyper-V MSR and hypercall primitives from `<asm/mshyperv.h>`, per-CPU hypercall argument pages from `hv_common.c`, VMBus constants and tasklet callbacks from `hyperv_vmbus.h`, channel migration from `channel.c`, and timer setup from `clocksource/hyperv_timer.h`. It also calls weak isolation/paravisor hooks defined in `hv_common.c` and overridden by architecture code.

## Risks and Edge Cases

Encryption-state failures are handled by leaking memory, which is intentional but should remain visible in diagnostics. CPU offline can fail with `-EBUSY` if channels cannot migrate or event bits stay pending. The connect CPU cannot be offlined while VMBus is connected. Confidential VMBus sequencing is delicate: data must not be posted after interrupts are disabled, and hypervisor/paravisor register programming must stay in the documented order.

## Test Signals

Exercise boot and CPU hotplug on non-confidential, SNP, TDX, root, nested, and paravisor configurations; verify page encryption transitions; test `hv_post_message()` payload-size and isolation path selection; validate channel migration on CPU offline; and use lockdep/trace output to confirm event bits drain before cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_common.c -->
# sources/distributed-fs/ceph-client/drivers/hv/hv_common.c

## Purpose

`hv_common.c` contains architecture-neutral Hyper-V support that must be built in when `CONFIG_HYPERV` is enabled. It defines shared Hyper-V globals, allocates per-CPU hypercall argument pages, records VP indexes, reports panic data to Hyper-V, seeds randomness from a Microsoft ACPI table, queries extended capabilities, exposes weak architecture hooks, identifies partition type, and maps Hyper-V status codes to Linux errors and strings.

## Important APIs, Types, and Functions

- Exported globals include `hv_current_partition_id`, `hv_curr_partition_type`, `hv_nested`, `ms_hyperv`, `hv_vp_index`, `hv_max_vp_index`, `hyperv_pcpu_input_arg`, `hyperv_pcpu_output_arg`, and `hv_synic_eventring_tail`.
- `hv_common_init()` initializes panic reporting, sysctl state, per-CPU hypercall pointers, root output pages, event-ring tails, and VP-index storage.
- `hv_common_free()` tears down sysctl, panic dump hooks, VP indexes, and per-CPU pointer arrays.
- `hv_common_cpu_init()` allocates per-CPU hypercall input/output pages, decrypts them for isolated guests when required, records `HV_MSR_VP_INDEX`, and allocates root SynIC event-ring tails.
- `hv_common_cpu_die()` frees root event-ring tail storage.
- `hv_kmsg_dump()` and `hv_die_panic_notify_crash()` report panic/oops information through Hyper-V crash MSRs.
- `hv_get_partition_id()`, `get_vtl()`, `hv_query_ext_cap()`, `hv_identify_partition_type()`, `hv_result_to_errno()`, and `hv_result_to_string()` are exported utility functions.

## Control Flow

`hv_common_init()` obtains hypervisor version information, disables panic-message recording by default for isolated guests, and if crash MSRs are available registers a sysctl plus panic/die/kmsg dump notifiers. It then allocates per-CPU holders for input and optional output hypercall pages and initializes `hv_vp_index[]` to invalid. Per-CPU bring-up calls `hv_common_cpu_init()`, which lazily allocates the real hypercall pages, handles memory decryption before publishing `hyperv_pcpu_input_arg`, reads the VP index MSR, updates the maximum VP index, and prepares root event-ring state.

Panic reporting either sends register-only crash notification or, when enabled and supported, writes kmsg tail data into `hv_panic_page`, programs crash MSRs P0-P4, and sets crash control notify bits. `hv_query_ext_cap()` performs a one-time extended capability hypercall and caches the result. Partition type is inferred from privilege bits while explicitly ignoring root privileges when isolation is present.

## State and Persistence Behavior

Most state is global and persists for the kernel lifetime or Hyper-V platform lifetime. Per-CPU hypercall pages are intentionally retained across CPU offline because later interrupt reassignment may still need them. `hv_extended_cap` is static and cached after first query. Panic-page allocation persists while crash reporting is registered. Weak hook definitions provide default no-op behavior until architecture-specific code overrides them at link time.

## Dependencies and Integration Points

This file is used by architecture initialization, VMBus core, MSHV root/VTL code, Hyper-V timer code, balloon page reporting, DMA setup, and crash/kexec paths. It depends on Hyper-V Hvhdk definitions, ACPI, sysctl, panic notifier, kmsg dumper, DMA-map ops, and architecture hypercall/MSR helpers.

## Risks and Edge Cases

`BUG_ON()` is used for fatal allocation failures in Hyper-V boot-critical paths. If `set_memory_decrypted()` fails in CPU init, memory may be unsafe to free and is intentionally left allocated. Panic reporting is deliberately limited in isolated guests. `hv_status_infos[]` contains duplicate status entries with different errno values for a couple of codes; first match wins. Status-to-errno mapping is necessarily lossy, so call sites still need context-specific handling.

## Test Signals

Verify boot on guest, root, L1VH, nested, SNP, TDX, and VTL configurations; CPU hotplug with retained hypercall pages; panic/oops reporting with sysctl enabled and disabled; ACPI OEM0 entropy seeding and table zeroing; extended capability caching; partition-type identification; and status-to-errno/string mappings for known and unknown hypercall statuses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/hv/hv_debugfs.c

## Purpose

`hv_debugfs.c` creates a Hyper-V debugfs hierarchy used to inject artificial delays into VMBus channel interrupt and message paths for fuzzing and timing tests. It also exposes a per-device boolean that enables or disables these delay injections.

## Important APIs, Types, and Functions

- `hv_debug_init()` creates the top-level `hyperv` debugfs directory.
- `hv_debug_add_dev_dir()` creates a per-device directory plus `fuzz_test_state` and `delay/` files.
- `hv_debug_rm_dev_dir()` and `hv_debug_rm_all_dir()` remove per-device or all Hyper-V debugfs entries.
- `hv_debug_delay_test()` is the runtime hook called from event/message paths to apply configured microsecond delays.
- `hv_debugfs_delay_get/set()` and `hv_debugfs_state_get/set()` implement bounded debugfs accessors.

## Control Flow

When a VMBus device is added, `hv_debug_add_dev_dir()` creates `hyperv/<device>/`, adds `fuzz_test_state`, creates a `delay` child directory, and adds `fuzz_test_buffer_interrupt_delay` and `fuzz_test_message_delay`. Delay writes are accepted only up to 1000 microseconds; state writes accept only 0 or 1. Runtime code calls `hv_debug_delay_test(channel, delay_type)`, which maps a sub-channel back to its primary channel, checks `fuzz_testing_state`, and applies the interrupt or message `udelay()`.

## State and Persistence Behavior

The global `hv_debug_root` dentry persists until `hv_debug_rm_all_dir()`. Each `hv_device` stores its debugfs directory in `dev->debug_dir`. The actual delay and enable state live in `struct vmbus_channel` fields, so settings follow channel lifetime. There is no persistent storage beyond debugfs runtime state.

## Dependencies and Integration Points

This file depends on debugfs, VMBus channel structures from `hyperv_vmbus.h`, and delay hooks in the VMBus event/message path. It is optional test infrastructure and has no direct host protocol role.

## Risks and Edge Cases

The code relies on debugfs helpers and generally treats `IS_ERR()` as the failure check. If debugfs is disabled or unavailable, callers must tolerate missing entries. Artificial delays run in sensitive interrupt/tasklet-related paths and can perturb timing significantly, though they are capped at 1000 microseconds. Sub-channels share primary-channel fuzz settings.

## Test Signals

Check debugfs directory creation/removal for device add/remove, input validation for delay and state files, sub-channel inheritance of primary settings, no delay when disabled, and expected latency when interrupt or message delay is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_kvp.c -->
# sources/distributed-fs/ceph-client/drivers/hv/hv_kvp.c

## Purpose

`hv_kvp.c` implements the Hyper-V Key Value Pair integration component. It negotiates the KVP protocol with the host, forwards host key/value and IP configuration requests to a userspace daemon, converts between UTF-16 host strings and UTF-8 userspace strings, handles daemon registration, and sends serialized responses back to the host.

## Important APIs, Types, and Functions

- `kvp_transaction` stores the single active host transaction: state, receive length, current `hv_kvp_msg`, channel, and request ID.
- `hv_kvp_onchannelcallback()` is the VMBus receive path for host KVP messages.
- `kvp_on_msg()` processes daemon writes through `hv_utils_transport`.
- `kvp_send_key()` converts and sends host requests to userspace.
- `kvp_respond_to_host()` converts daemon responses back to host format and sends the VMBus response.
- `kvp_handle_handshake()`, `kvp_register()`, and `kvp_register_done()` manage daemon registration and version compatibility.
- `process_ib_ipinfo()` and `process_ob_ipinfo()` translate inbound and outbound IP information structures.
- `hv_kvp_init()`, `hv_kvp_init_transport()`, `hv_kvp_pre_suspend()`, `hv_kvp_pre_resume()`, and `hv_kvp_deinit()` integrate with `hv_util.c`.

## Control Flow

`hv_kvp_init()` receives the shared utility receive buffer and channel, sets a larger maximum packet size, and marks the device waiting for daemon registration. `hv_kvp_init_transport()` creates the userspace transport. Host callbacks are ignored during early daemon negotiation except for scheduling a delayed host-handshake poll to avoid losing failover IP messages. Once ready, `hv_kvp_onchannelcallback()` receives a packet, handles IC negotiation directly, or stores a KVP exchange in `kvp_transaction`, marks `HVUTIL_HOSTMSG_RECEIVED`, schedules `kvp_sendkey_work`, and arms a timeout.

`kvp_send_key()` builds a daemon message according to operation type, translating keys, values, and IP fields. `kvp_on_msg()` receives the daemon reply, derives the error code according to daemon protocol version, cancels the timeout, responds to the host, and polls the VMBus channel again. Timeout and reset paths fail the host transaction and reset the state machine.

## State and Persistence Behavior

The implementation intentionally keeps only one outstanding transaction because the Hyper-V IC protocol is request/response. `dm_reg_value` records daemon registration protocol. `recv_buffer` points into the utility service buffer owned by `hv_util.c`; `hvt` owns the transport. Delayed work items persist across transactions and are cancelled on suspend or deinit. On suspend the tasklet is disabled, work is cancelled, and state is forced to ready so resume negotiation can proceed even if userspace writes arrive out of order.

## Dependencies and Integration Points

This file depends on VMBus utility service wiring in `hv_util.c`, negotiation helper `vmbus_prep_negotiate_resp()`, structures from `<linux/hyperv.h>`, connector/misc transport from `hv_utils_transport.c`, and the userspace KVP daemon using `/dev/vmbus/hv_kvp` or legacy connector IDs.

## Risks and Edge Cases

The global transaction model depends on host serialization and driver-side state checks. Buffer-size validation is present for IC headers, but KVP union fields require operation-specific care. String conversion must preserve NUL room and report failures. If userspace is absent or slow, host transactions fail after timeout. Reset/open races with the transport intentionally fail pending host requests.

## Test Signals

Test host IC negotiation, daemon registration versions, daemon absence and timeout, GET/SET/DELETE/ENUMERATE operations, IP GET/SET conversions, UTF-16/UTF-8 conversion failures, transport reset during active requests, suspend/resume ordering, and channel polling after completed transactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_kvp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_proc.c -->
# sources/distributed-fs/ceph-client/drivers/hv/hv_proc.c

## Purpose

`hv_proc.c` provides Hyper-V root-partition processor and memory-deposit hypercall helpers. It allocates pages for child/root partition deposits, retries processor creation when Hyper-V reports insufficient memory, adds logical processors, creates VPs, notifies that processors have started, and probes whether an LP index exists.

## Important APIs, Types, and Functions

- `hv_call_deposit_pages()` allocates exactly the requested number of pages, fills a `hv_deposit_memory` input page, and performs `HVCALL_DEPOSIT_MEMORY`.
- `hv_deposit_memory_node()` chooses deposit count and partition target based on insufficient-memory status codes.
- `hv_result_needs_memory()` identifies hypercall statuses that require a memory deposit and retry.
- `hv_call_add_logical_proc()` wraps `HVCALL_ADD_LOGICAL_PROCESSOR` with memory-deposit retry.
- `hv_call_create_vp()` wraps `HVCALL_CREATE_VP`, including an empirical pre-deposit for non-current partitions and retry on memory pressure.
- `hv_call_notify_all_processors_started()` sends `HVCALL_NOTIFY_PARTITION_EVENT`.
- `hv_lp_exists()` probes `HVCALL_GET_LOGICAL_PROCESSOR_RUN_TIME` and treats `HV_STATUS_INVALID_LP_INDEX` as nonexistence.

## Control Flow

Deposit flow allocates a temporary page to hold page pointers, separately allocates a counts array, then allocates all deposit pages in the largest orders possible before disabling interrupts. With interrupts disabled it uses the per-CPU Hyper-V input page, populates partition ID and GPA page list, issues a rep hypercall, and either transfers ownership to Hyper-V or frees all pages on failure. Processor add/create functions build input structures on the per-CPU hypercall page, call Hyper-V, and if the status indicates insufficient memory call `hv_deposit_memory_node()` before retrying.

## State and Persistence Behavior

Successful deposits transfer page ownership to Hyper-V and the pages are not freed by Linux. Failed deposits free each split page. The helper itself keeps no persistent state, but it relies on globally initialized per-CPU input/output pages from `hv_common.c`, `hv_current_partition_id`, and root-partition capability state. `hv_call_create_vp()` may deposit pages into child partitions before creating a VP.

## Dependencies and Integration Points

The file depends on Hyper-V Hvhdk structures, `hyperv_pcpu_input_arg`, `hyperv_pcpu_output_arg`, `hv_result_to_errno()`, `hv_status_err()`, NUMA-to-PXM helpers, and root partition code that creates logical processors or VPs. It is exported for GPL consumers.

## Risks and Edge Cases

`hv_call_deposit_pages()` requires interrupts enabled before entry because it disables interrupts around per-CPU hypercall page use after doing all allocations. `HV_DEPOSIT_MAX` bounds the page list to one Hyper-V page. High-order allocation fallback splits pages and must free every split page on failure. The empirical 90-page pre-deposit for child VP creation is host behavior dependent. Unexpected root-memory statuses in non-root partitions are rejected.

## Test Signals

Test exact deposit counts including zero and over-limit, allocation fallback and cleanup, insufficient-memory retry loops for LP and VP creation, root versus child partition deposit targets, notify-all-processors-started errors, and `hv_lp_exists()` for valid, invalid, and unexpected status codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_snapshot.c -->
# sources/distributed-fs/ceph-client/drivers/hv/hv_snapshot.c

## Purpose

`hv_snapshot.c` implements the Hyper-V Volume Shadow Copy Service integration component. It negotiates VSS protocol with the host, forwards freeze/thaw/hot-backup operations to a userspace daemon, handles daemon registration and timeouts, and returns completion status to the host.

## Important APIs, Types, and Functions

- `vss_transaction` stores the single active host VSS transaction: state, receive buffer length, channel, request ID, and current `hv_vss_msg`.
- `hv_vss_onchannelcallback()` handles host VSS and negotiation messages.
- `vss_on_msg()` handles daemon writes through the utility transport.
- `vss_handle_request()`, `vss_send_op()`, and `vss_respond_to_host()` drive host-to-daemon-to-host request flow.
- `vss_timeout_func()` fails operations when userspace does not respond; freeze gets the longer `VSS_FREEZE_TIMEOUT`.
- `vss_handle_handshake()` supports legacy and reply-required daemon registration.
- `hv_vss_init()`, `hv_vss_init_transport()`, `hv_vss_pre_suspend()`, `hv_vss_pre_resume()`, and `hv_vss_deinit()` are consumed by `hv_util.c`.

## Control Flow

Initialization refuses hosts older than Win8.1, stores the utility receive buffer, sets the channel maximum packet size to two Hyper-V pages, and marks the transaction state waiting for daemon registration. Host callbacks ignore new packets while a transaction is active. Negotiation packets are answered directly with `vmbus_prep_negotiate_resp()`. VSS packets are length-checked, stored in `vss_transaction`, and processed in workqueue context. Freeze, thaw, and hot-backup operations require userspace; they transition to `HVUTIL_HOSTMSG_RECEIVED`, send an operation to the daemon, and arm a timeout. `GET_DM_INFO` is answered in-kernel.

Daemon replies enter `vss_on_msg()`. Registration messages are accepted only outside an active transaction. Operation replies are accepted only after a userspace request was sent; the code updates hot-backup flags when requested, cancels timeout, responds to the host, and polls the channel again. Suspend sends a best-effort fake THAW to userspace after cancelling pending work so filesystems are not left frozen.

## State and Persistence Behavior

Like KVP, VSS relies on one global active transaction. `recv_buffer` is shared with `hv_util.c`, while `hvt` owns the daemon transport. `dm_reg_value` records daemon protocol. Delayed and normal work items persist and are cancelled on reset, suspend, or deinit. State is forced to ready during suspend so later daemon writes fail and force daemon reset instead of completing stale host work.

## Dependencies and Integration Points

This file integrates with `hv_util.c`, `hv_utils_transport.c`, VMBus packet APIs, Hyper-V VSS structures from `<linux/hyperv.h>`, and the userspace `hv_vss_daemon`. It uses the VSS GUID service entry in the utility driver.

## Risks and Edge Cases

The freeze timeout is long because host expectations require it, so hung userspace can delay host-visible completion. Correct thaw-on-suspend behavior is critical to avoid leaving filesystems frozen. Host packets must fit `VSS_MAX_PKT_SIZE`; this is tied to structure comments in Hyper-V headers. Transport reset or daemon restart fails active host transactions.

## Test Signals

Test protocol negotiation, daemon registration modes, freeze/thaw/hot-backup success and timeout, `GET_DM_INFO`, daemon reset mid-transaction, suspend fake thaw, resume tasklet re-enable, unsupported old host versions, and packet length validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_snapshot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_trace.c -->
# sources/distributed-fs/ceph-client/drivers/hv/hv_trace.c

## Purpose

`hv_trace.c` is the tracepoint definition translation unit for the Hyper-V VMBus trace events declared in `hv_trace.h`. It includes VMBus type definitions, defines `CREATE_TRACE_POINTS`, and includes the trace header exactly once so the kernel tracepoint storage and registration metadata are emitted.

## Important APIs, Types, and Functions

- `CREATE_TRACE_POINTS` controls tracepoint definition emission.
- `#include "hv_trace.h"` instantiates all VMBus trace events declared there.
- There are no runtime functions in this file; its API surface is the generated tracepoint symbols.

## Control Flow

Build-time inclusion is the only control flow. Other Hyper-V files include `hv_trace.h` to call `trace_vmbus_*()` helpers, while this file provides the single definition site required by Linux tracepoint infrastructure.

## State and Persistence Behavior

Tracepoint state is managed by the kernel tracing subsystem. This file owns no driver state and has no persistence beyond the generated static tracepoint objects.

## Dependencies and Integration Points

It depends on `hyperv_vmbus.h` for event argument types and `hv_trace.h` for trace event declarations. It integrates with ftrace/perf/tracefs consumers.

## Risks and Edge Cases

The main risk is duplicate tracepoint definitions if another C file defines `CREATE_TRACE_POINTS` for `hv_trace.h`, or missing tracepoints if this file is not linked into the VMBus build. Because it contains no logic, behavioral regressions usually appear as build or trace availability failures.

## Test Signals

Build the Hyper-V driver with tracing enabled, verify `trace/events/hyperv` entries exist, and exercise VMBus offer/open/close paths while checking that the events can be enabled and produce records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_trace.h -->
# sources/distributed-fs/ceph-client/drivers/hv/hv_trace.h

## Purpose

`hv_trace.h` declares tracepoints for Hyper-V VMBus channel management and channel operations. It gives maintainers observability into host messages, offers, rescinds, open/close, GPADL setup/teardown, version negotiation, event scheduling, and modify-channel operations.

## Important APIs, Types, and Functions

- Event class `vmbus_hdr_msg` backs `vmbus_on_msg_dpc` and `vmbus_on_message`.
- `TRACE_EVENT(vmbus_onoffer)` records relid, monitor ID, dedicated interrupt flag, connection ID, interface GUIDs, channel flags, MMIO size, and sub-channel index.
- Response events cover rescind, open result, GPADL created/torndown, modify-channel response, and version response.
- Send-side events cover request-offers, open, close, establish GPADL header/body, teardown GPADL, negotiate version, release relid, TL connect, and modify-channel.
- Event class `vmbus_channel` backs channel scheduling, set-event, and channel callback events.

## Control Flow

The header follows Linux trace event convention: it defines `TRACE_SYSTEM hyperv`, guards declarations with `_HV_TRACE_H` and `TRACE_HEADER_MULTI_READ`, sets `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE`, and includes `<trace/define_trace.h>` outside the guard. Call sites invoke generated `trace_vmbus_*()` functions; enabled tracepoints copy selected fields into trace buffers and format them via `TP_printk`.

## State and Persistence Behavior

The header defines static tracepoint metadata, field layouts, and print formats. Runtime state is owned by the tracing subsystem. The selected fields are stable observability contracts: changing field names or types affects trace consumers and tooling.

## Dependencies and Integration Points

Trace arguments depend on VMBus protocol structures from `hyperv_vmbus.h` and GUID export formatting. Events are used by `channel_mgmt.c`, `connection.c`, and channel/ring code to debug VMBus lifecycle and host communication.

## Risks and Edge Cases

Tracepoints must not dereference invalid channel or message pointers after an object can be freed. GUID arrays must be filled with `export_guid()` before `%pUl` formatting. Print formats and field names are user-visible in tracefs and should be treated as compatibility-sensitive. Include-path settings must match the source layout or trace generation fails.

## Test Signals

Enable each event group under tracefs, run VMBus device enumeration, channel open/close, GPADL creation, rescind, CPU retargeting, and TL connect scenarios, and verify field values match host messages without build warnings from trace macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_trace_balloon.h -->
# sources/distributed-fs/ceph-client/drivers/hv/hv_trace_balloon.h

## Purpose

`hv_trace_balloon.h` declares the Hyper-V balloon driver tracepoint used to observe guest memory pressure reports and dynamic-memory accounting.

## Important APIs, Types, and Functions

- `TRACE_SYSTEM hyperv` places the event in the Hyper-V trace system.
- `TRACE_EVENT(balloon_status)` records available pages, committed pages, raw `vm_memory_committed()`, pages ballooned, pages hot-added, and pages onlined.
- Generated `trace_balloon_status()` is called by `post_status()` in `hv_balloon.c`.

## Control Flow

The header follows the standard trace-event pattern with a multi-read guard, field declarations, fast assignment, print formatting, `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and an out-of-guard include of `<trace/define_trace.h>`. `hv_balloon.c` defines `CREATE_TRACE_POINTS` before including this header, so the balloon tracepoint is instantiated in the balloon module/object rather than `hv_trace.c`.

## State and Persistence Behavior

The tracepoint owns no balloon state. It snapshots counters passed by `hv_balloon.c` at pressure-report time and leaves buffering, enablement, and persistence to the tracing subsystem.

## Dependencies and Integration Points

This file depends on Linux tracepoint infrastructure and the accounting semantics in `hv_balloon.c`. It is useful with debugfs counters from the balloon driver to correlate host pressure reports with internal counters.

## Risks and Edge Cases

Field units must stay aligned with the caller. `hv_balloon.c` passes page counts before converting the VMBus status message to Hyper-V page units, so trace consumers should interpret values as Linux page counts except where named otherwise. Moving `CREATE_TRACE_POINTS` could cause duplicate or missing tracepoint definitions.

## Test Signals

Enable `hyperv:balloon_status`, trigger periodic pressure reports, balloon-up, unballoon, and hot-add activity, and verify trace records match debugfs `hv-balloon` counters and host status behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_trace_balloon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_util.c -->
# sources/distributed-fs/ceph-client/drivers/hv/hv_util.c

## Purpose

`hv_util.c` is the VMBus utility driver for Hyper-V integration components: shutdown, time synchronization, heartbeat, KVP, and VSS. It registers one `hv_driver` matching several utility GUIDs, opens utility channels in direct-read mode, delegates KVP/VSS to their modules, and implements shutdown, restart, hibernate, heartbeat, host time synchronization, and a read-only Hyper-V PTP clock.

## Important APIs, Types, and Functions

- `struct hv_util_service` instances `util_shutdown`, `util_timesynch`, `util_heartbeat`, `util_kvp`, and `util_vss` bind service callbacks and lifecycle hooks.
- `shutdown_onchannelcallback()` handles negotiation and shutdown/restart/hibernate host requests.
- `timesync_onchannelcallback()`, `adj_guesttime()`, `hv_get_adj_host_time()`, and `hv_set_host_time()` maintain host time samples and discipline guest time when requested.
- `heartbeat_onchannelcallback()` increments heartbeat sequence numbers and responds.
- `util_probe()`, `util_remove()`, `util_suspend()`, and `util_resume()` implement shared utility channel lifecycle.
- `hv_timesync_init()`, `hv_timesync_pre_suspend()`, and `hv_timesync_deinit()` manage work and PTP clock registration.
- `ptp_hyperv_info` exposes `gettime64` backed by the latest host time sample.

## Control Flow

Probe allocates a receive buffer, runs service-specific init, switches the channel to `HV_CALL_DIRECT`, stores driver data, opens the VMBus channel with utility-sized rings, and initializes optional userspace transport. Shutdown callbacks read one packet, negotiate if requested, otherwise inspect shutdown flags and schedule process-context poweroff, reboot, or hibernate uevent work after sending a host response. Timesync drains all available packets and uses the last host sample; version 4+ messages include a reference time for better precision. Heartbeat drains packets, negotiates or increments `seq_num`, and replies.

Suspend calls service-specific pre-suspend hooks, then closes the channel while userspace is frozen. Resume calls pre-resume hooks and reopens the channel. KVP and VSS hooks handle tasklet disable/enable and daemon state. Module init registers `hv_utils`; module exit unregisters it.

## State and Persistence Behavior

Each utility service has a persistent `recv_buffer` and channel pointer while probed. Shutdown keeps global hibernate work context and hibernation support state. Timesync stores the latest `host_time` and `ref_time` under `host_ts.lock`, plus a PTP clock pointer and adjustment work. Negotiated service versions are stored globally per service. Utility request buffers are reused for responses.

## Dependencies and Integration Points

This file depends on VMBus packet APIs, `vmbus_prep_negotiate_resp()` from `channel_mgmt.c`, KVP/VSS entry points from `hv_kvp.c` and `hv_snapshot.c`, `hv_read_reference_counter()` from `hv_common.c`, Linux reboot/poweroff, hibernation uevents, PTP clock APIs, and Hyper-V IC protocol structures.

## Risks and Edge Cases

Packet length checks are critical because host data is parsed in shared buffers. Timesync samples can become stale; PTP `gettime64` returns `-ESTALE` after a fixed threshold. `timesync_implicit` works around missing resume sync flags by forcing sync if guest time lags host. Shutdown work is scheduled only after the host response is sent. KVP can handle only one message at a time, which is why direct read mode is forced for all utility services.

## Test Signals

Test service negotiation for all GUIDs, shutdown/restart/hibernate requests, hibernation unsupported status, heartbeat sequence increment, timesync v3 and v4 samples, explicit and implicit clock sync, stale PTP reads, suspend/resume for all utility services, and KVP/VSS transport initialization failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_utils_transport.c -->
# sources/distributed-fs/ceph-client/drivers/hv/hv_utils_transport.c

## Purpose

`hv_utils_transport.c` provides the kernel-to-userspace transport abstraction used by Hyper-V KVP and VSS daemons. It supports both legacy connector/netlink and newer misc character devices, serializes one outbound message at a time for char devices, receives daemon replies, and handles reset/destroy state transitions.

## Important APIs, Types, and Functions

- Global `hvt_list` plus `hvt_list_lock` tracks transports for connector callback lookup.
- `hvt_op_open()`, `hvt_op_read()`, `hvt_op_write()`, `hvt_op_poll()`, and `hvt_op_release()` implement misc device file operations.
- `hvt_cn_callback()` routes connector messages to the matching transport.
- `hvutil_transport_send()` sends a kernel message to userspace via connector or char device and optionally calls `on_read_cb` when consumed.
- `hvutil_transport_init()` allocates a transport, registers the misc device, and optionally registers a connector callback.
- `hvutil_transport_destroy()` marks destroy state, wakes readers, unregisters connector and misc device, and waits for open char-device release when necessary.
- `hvt_reset()` clears pending outbound state and invokes service reset callback.

## Control Flow

Initialization fills connector IDs, miscdevice metadata, embedded file operations, waitqueue, mutex, and completion, adds the transport to the global list, registers the misc device, and optionally registers connector callback. A daemon can communicate via connector first, which switches mode from INIT to NETLINK, or open the char device, which switches INIT or NETLINK to CHARDEV and resets any netlink state. `hvutil_transport_send()` rejects INIT/DESTROY, allocates and sends a connector message in NETLINK mode, or stores a single `outmsg`, wakes readers, and records an `on_read` callback in CHARDEV mode.

Reads block until an outbound message exists or mode changes, copy the whole message, free it, and call `on_read`. Writes copy user data and pass it to the service's `on_msg()` callback. Release resets pending state and returns to INIT unless destroy is active; destroy waits for that release if a char-device fd is open.

## State and Persistence Behavior

`struct hvutil_transport` persists from init to destroy and stores mode, callbacks, pending outbound message, waitqueue, lock, miscdevice, connector ID, and release completion. The mode is the core state machine: INIT, NETLINK, CHARDEV, DESTROY. Pending char-device messages are single-slot; services must not queue a second message before userspace reads the first.

## Dependencies and Integration Points

The transport depends on miscdevice, connector, poll, usercopy, and service callbacks supplied by `hv_kvp.c` and `hv_snapshot.c`. It is initialized by those services through `hv_util.c`.

## Risks and Edge Cases

Mode transitions can reset active service transactions, so reset callbacks must fail or clean pending host work. `hvutil_transport_send()` in NETLINK mode calls `on_read_cb` immediately because delivery completion is unknown; char-device mode waits for actual read. A second char-device outbound send fails with `-EFAULT` if the previous message was not read. Destroy must avoid freeing a transport while file operations are active.

## Test Signals

Test char-device open/read/write/poll/release, connector fallback, switching from netlink to char device, daemon reset during active KVP/VSS transactions, destroy with and without open fds, send before daemon registration, duplicate send before read, and wakeup behavior on destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_utils_transport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_utils_transport.h -->
# sources/distributed-fs/ceph-client/drivers/hv/hv_utils_transport.h

## Purpose

`hv_utils_transport.h` declares the shared userspace transport contract for Hyper-V utility services such as KVP and VSS. It defines the transport mode state machine, the transport object layout, and init/send/destroy APIs.

## Important APIs, Types, and Functions

- `enum hvutil_transport_mode` defines `HVUTIL_TRANSPORT_INIT`, `HVUTIL_TRANSPORT_NETLINK`, `HVUTIL_TRANSPORT_CHARDEV`, and `HVUTIL_TRANSPORT_DESTROY`.
- `struct hvutil_transport` embeds miscdevice and file operations state, connector ID, list node, callbacks, pending outbound message, waitqueue, mutex, and release completion.
- `hvutil_transport_init()` creates a named transport with connector IDs and service callbacks.
- `hvutil_transport_send()` sends one kernel-originated message to userspace and can run an `on_read` callback.
- `hvutil_transport_destroy()` tears down connector/misc resources and synchronizes with open character-device users.

## Control Flow

Service code includes this header, creates a transport during its utility-service init path, sends requests to userspace with `hvutil_transport_send()`, receives daemon replies through the `on_msg` callback supplied at init, and destroys the transport during service deinit. The mode enum tells the implementation whether communication is unregistered, connector-based, character-device-based, or being destroyed.

## State and Persistence Behavior

The header exposes implementation state because `hv_utils_transport.c` embeds the `file_operations` in the transport and uses `container_of()` from file operations. Service users should treat fields as owned by the transport implementation and interact through the three exported functions plus callbacks.

## Dependencies and Integration Points

It depends on Linux connector and miscdevice headers. The interface is consumed by `hv_kvp.c` and `hv_snapshot.c` and indirectly by `hv_util.c`.

## Risks and Edge Cases

Because the full struct is visible, accidental external mutation could break locking, mode transitions, or pending-message ownership. The callback contract is important: `on_msg` must validate user input and `on_reset` must make service state consistent after daemon disconnect or transport mode switch.

## Test Signals

Compile users of the header after signature changes, test all mode transitions through the C implementation, and verify KVP/VSS reset and daemon reply paths still conform to the callback contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_utils_transport.h -->
