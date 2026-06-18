# Group Research: group_1751_spdk_sources_virtualization_spdk_lib_nvmf_ctrlr_discovery_c_sources_8e60729ed46a

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvmf/ctrlr_discovery.c -->
# File Research: sources/virtualization/spdk/lib/nvmf/ctrlr_discovery.c

Read completely: yes, 332 lines.

Purpose: implements NVMe-oF discovery log generation and asynchronous Get Log Page handling for discovery controllers.

Key responsibilities:
- Maintains discovery generation changes through `spdk_nvmf_send_discovery_log_notice()`.
- Filters discovery entries by transport type, address, service ID, and optional custom filter.
- Builds a dynamic `spdk_nvmf_discovery_log_page` from active subsystems, active listeners, and target referrals.
- Completes Get Log Page asynchronously on the app thread, copying requested ranges into request iovecs and zero-filling the remainder.

Important control flow:
- `nvmf_generate_discovery_log()` iterates all target subsystems, skips inactive/deactivating subsystems, enforces host access, checks listener active state, applies discovery filters, then appends entries.
- Discovery subsystem entries set `DUPRETINFO` and `EPCSD` flags.
- Referral entries are appended after subsystem listener entries, subject to referral host allow-list checks.
- `nvmf_get_discovery_log_page_async()` snapshots host NQN, offset, length, source trid, and RAE flag, then sends work to the app thread.

Concurrency and ownership:
- Discovery log generation asserts app-thread execution.
- Async context owns duplicated `hostnqn` and is freed after request completion.
- Generated log pages are heap allocated and freed after copying.

Notable edge cases:
- Offset at or beyond generated log size returns Invalid Field.
- If allocation fails during entry growth, generation stops at the entries already accumulated.
- Custom discovery filter is only valid when target setup supplied `g_custom_discovery_filter`.

Dependencies:
- Uses target/subsystem/listener internals from `nvmf_internal.h`.
- Calls transport-specific `nvmf_transport_listener_discover()` to fill transport fields.
- Relies on `spdk_nvmf_referral_host_allowed()` from `nvmf.c`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvmf/ctrlr_discovery.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvmf/fc.c -->
# File Research: sources/virtualization/spdk/lib/nvmf/fc.c

Read completely: yes, 4007 lines.

Purpose: implements the NVMe-oF Fibre Channel transport integration, including transport registration, FC hardware port/nport/rport administration, poll-group and hardware-queue routing, IO request lifecycle, ABTS handling, and SPDK transport callbacks.

Major components:
- FC tracepoint registration and request state naming.
- Global FC transport state: `g_nvmf_ftransport`, `g_spdk_nvmf_fc_port_list`, `g_nvmf_fc_main_thread`, and FC poll groups.
- Per-connection request pools sized at twice queue depth to tolerate CQ/RQ race windows.
- HWQP initialization with DPDK hash tables for connection IDs and RPIs.
- Poll-group assignment, add/remove HWQP messaging, and FC queue polling.
- FC admin event handlers for HW port init/free/online/offline/reset, nport create/delete, I_T add/delete, and ABTS receive.

IO path:
- `nvmf_fc_hwqp_process_frame()` dispatches LS requests to `fc_ls.c` or command IUs to `nvmf_fc_hwqp_handle_request()`.
- `nvmf_fc_hwqp_handle_request()` validates command IU fields, rejects bidirectional transfers, looks up connection ID, validates source/destination IDs, checks association/connection/qpair state, enforces max IO size, allocates an FC request, copies NVMe command data, records VMID/priority, and executes or queues pending-buffer work.
- `nvmf_fc_request_execute()` allocates exchange and data buffers, then either receives host-to-controller data or submits read/no-data commands to the generic NVMf executor.
- `nvmf_fc_request_complete()` sends read data, ERSP/RSP responses, or abort completion depending on request state and completion status.

Abort and ABTS handling:
- `nvmf_fc_handle_abts_frame()` identifies HWQPs with active connections for an RPI, sends ABTS work to pollers, and emits BLS accept/reject.
- If no OXID is found and queue sync is available, the code posts queue-sync markers and retries.
- `nvmf_fc_request_abort()` marks requests aborted, notifies bdev for bdev-phase work, issues FC aborts for transfer/response phases, removes pending/fused requests directly, and completes through poller API.

Transport API:
- Registers `spdk_nvmf_transport_fc`.
- Defaults: max queue depth 128, admin depth 32, max qpairs per controller 5, max IO size 65536, IO unit size 4096.
- `nvmf_fc_create()` requires at least two cores, initializes the low-level driver, registers an accept poller, and records the main thread.
- `nvmf_fc_discover()` fills FC discovery log fields.
- Listen/stop-listen are stubs returning success/no-op; actual FC nport listener population is handled by admin nport events.

Administration model:
- Low-level FC driver events are funneled through `nvmf_fc_main_enqueue_event()` onto the FC main thread.
- HW port online marks LS and IO queues online and assigns IO queues to least-loaded FC poll groups.
- HW port offline marks queues offline and asynchronously removes HWQPs from poll groups.
- Nport creation also adds FC listener addresses to subsystems allowing any listener.
- Nport deletion removes listener addresses and deletes all rports.
- I_T delete removes pending LS work, marks rport deleting, deletes all matching associations, and frees rport after associations drain.

Concurrency and ownership:
- Main-thread assertions protect FC admin object mutation.
- Poll-group list updates are protected by `g_nvmf_ftransport->lock`.
- Many operations are asynchronous through `spdk_thread_send_msg()` and callback contexts.
- Request objects are pool-owned by connections; `_nvmf_fc_request_free()` returns exchange, buffers, and request object.

Notable risks and sharp edges:
- `nvmf_fc_adm_evnt_hw_port_offline()` initializes `pending_remove_hwqp` to `num_io_queues`; a zero-IO-queue port would not use the async callback path.
- Several admin paths use `DEV_VERIFY()` for conditions that become non-fatal in promoted builds, so callers may see partial zombie states.
- `nvmf_fc_adm_add_rem_nport_listener()` calls `spdk_nvmf_tgt_listen_ext()` even on remove path before pausing/removing listener, which is unusual but matches current code.
- The code relies heavily on correct callback ownership; duplicate delete operations often return `-ENODEV` rather than queueing callbacks.

Dependencies:
- Works with `fc_ls.c` for LS association/connection handling.
- Delegates hardware operations to `fc_lld.h` functions.
- Uses generic NVMf transport hooks, qpair lifecycle, request execution, and subsystem listener APIs.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvmf/fc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvmf/fc_ls.c -->
# File Research: sources/virtualization/spdk/lib/nvmf/fc_ls.c

Read completely: yes, 1729 lines.

Purpose: implements NVMe/FC Link Service request processing and poller-side FC connection management.

Major responsibilities:
- Formats LS accept/reject headers and reject descriptors.
- Allocates and frees FC associations and their preallocated connection arrays.
- Handles LS Create Association, Create Connection, and Disconnect requests.
- Deletes FC connections and associations asynchronously through poller APIs.
- Maintains poller lookup tables for connection ID and RPI-to-connection lists.
- Exposes `nvmf_fc_poller_api_func()` to marshal poller operations onto HWQP threads.

Association and connection lifecycle:
- `nvmf_fc_ls_new_association()` validates rport presence, initializes host/subsystem NQN data, stores subsystem and transport pointers, allocates connection slots, and links association to nport/rport.
- `nvmf_fc_ls_new_connection()` pulls a connection from the association free list, initializes qpair state, queue depth, RPI, IDs, transport, outstanding queue, and FC trid.
- `nvmf_fc_ls_add_conn_to_poller()` creates per-connection request pools, builds add-connection operation data, and asks generic NVMf target code to place the qpair in a poll group.
- `nvmf_fc_ls_add_conn_cb()` fills returned connection IDs into LS accept responses and transmits them.
- Delete paths mark objects `TO_BE_DELETED`, abort outstanding requests, disconnect qpairs, remove hash entries, return connections to free lists, and free the association when its connection count reaches zero.

LS validation:
- Create Association validates request length, descriptor list length, descriptor tags/lengths, ERSP ratio, admin SQ size, subsystem NQN lookup, and host permission.
- Create Connection validates association ID descriptor, connection command descriptor, ERSP ratio, SQ size, association state, and max qpair count.
- Disconnect validates association ID and disconnect command descriptors before scheduling association deletion.
- Invalid LS commands receive LS reject.

Poller API:
- Add connection inserts connection ID and RPI lookup data.
- Delete connection aborts in-use requests, handles AER specially, disconnects the qpair, removes hash data, and completes callbacks.
- ABTS received searches by RPI/OXID and aborts matching request or reports OXID not found.
- Queue sync stores callback args until a matching sync-done tag arrives.
- Add/remove HWQP updates poll-group HWQP lists on the HWQP thread.

Important data structures:
- Association lists live under nport.
- Rport association counts are incremented/decremented with association membership.
- Connection hash maps `conn_id -> fc_conn`.
- RPI hash maps `rpi -> list of fc_conn` for ABTS lookup.

Concurrency and ownership:
- LS request response buffers are owned by receive queue buffers and released after transmit path.
- Delete callback contexts may be chained on association or connection `ls_del_op_ctx`.
- Poller callbacks are bounced back to the callback thread through `nvmf_fc_poller_api_perform_cb()`.
- Connection deletion waits for qpair finalization when upper-layer disconnect is still pending.

Notable risks and sharp edges:
- `nvmf_fc_ls_alloc_connections()` allocates `(max_qpairs_per_ctrlr + 1) * sizeof(conn)` but loops only `max_qpairs_per_ctrlr`; the extra slot is unused.
- Pointer arithmetic in `nvmf_fc_ls_alloc_connections()` uses `assoc->conns_buf + (i * sizeof(struct spdk_nvmf_fc_conn))`; because `conns_buf` is a `struct spdk_nvmf_fc_conn *`, this scales by struct size twice and appears suspicious unless the declared type differs in headers.
- Delete paths depend on callback completion to free operation contexts and associations; missed callbacks would leak or stall deletion.
- Several reject paths use Create Association request struct aliases for formatting, but only access common header fields.

Dependencies:
- Consumes object types and poller API declarations from `nvmf_fc.h`.
- Uses generic target/subsystem host validation APIs from NVMf core.
- Calls `fc.c` helpers for request pools, connection deletion integration, request abort completion, HWQP validation, and transport/qpair behavior.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvmf/fc_ls.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvmf/mdns_server.c -->
# File Research: sources/virtualization/spdk/lib/nvmf/mdns_server.c

Read completely: yes, 290 lines.

Purpose: optional Avahi-backed mDNS Pull Registration Request publisher for NVMe-oF discovery listeners.

Build condition:
- Entire implementation is guarded by `SPDK_CONFIG_AVAHI`.

Key responsibilities:
- Owns one global Avahi simple poll, client, entry group, and publish context.
- Publishes active discovery subsystem listeners as `_nvme-disc._tcp.local` services.
- Supports updating service entries when listeners change.
- Provides target-scoped stop/destroy helpers.

Control flow:
- `nvmf_publish_mdns_prr()` ensures only one target is published globally, finds the discovery subsystem, requires at least one listener, creates Avahi poll/client objects, stores context, and registers an SPDK poller.
- `publish_client_new_callback()` waits for Avahi running state, then creates an entry group and publishes listeners.
- `nvmf_avahi_publish_iterate()` advances the Avahi simple poll from an SPDK poller.
- `nvmf_tgt_update_mdns_prr()` resets the entry group and republishes listeners.
- `nvmf_tgt_stop_mdns_prr()` unregisters the poller and frees Avahi state if the target matches.

Published service data:
- Service name base is `spdk` plus a per-listener id.
- TCP listeners publish protocol TXT `p=tcp` and discovery NQN TXT.
- RDMA listeners are skipped because the code cannot distinguish RoCE and iWARP.
- Other transport types are rejected for mDNS PRR.

Ownership:
- `nvmf_avahi_publish_destroy()` frees entry group, Avahi client, simple poll, context, and clears globals.
- TXT lists are freed per listener after service add attempt.

Notable edge cases:
- `spdk_nvmf_tgt_find_subsystem()` result is not null-checked before `TAILQ_EMPTY(&subsystem->listeners)`.
- `spdk_strtol()` return is assigned to `uint16_t port` without explicit parse error/range handling.
- Only one target can publish mDNS at a time due to global Avahi state.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvmf/mdns_server.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvmf/nvmf.c -->
# File Research: sources/virtualization/spdk/lib/nvmf/nvmf.c

Read completely: yes, 2170 lines.

Purpose: core NVMe-oF target lifecycle, transport registry integration, referrals, poll groups, qpair disconnect handling, configuration dump, listen APIs, target pause/resume, and subsystem state propagation.

Major responsibilities:
- Tracks all NVMf targets in global `g_nvmf_tgts`.
- Creates/destroys targets and registers them as SPDK IO devices.
- Adds/removes transports across all poll-group channels.
- Creates and destroys poll groups and their per-transport poll groups.
- Handles qpair placement, qpair disconnect, qpair finalization, and controller destruction when last qpair is gone.
- Maintains discovery referrals and referral host allow-lists.
- Dumps target configuration as JSON RPC replay data.
- Propagates subsystem namespace/channel state into poll groups and emits namespace/ANA async events.

Referral handling:
- `spdk_nvmf_tgt_add_referral()` validates/normalizes subnqn, deduplicates by transport ID, creates a discovery log entry, initializes host policy, links referral, and sends discovery log notice.
- Referral host add/remove validates NQN and emits host-specific discovery notices.
- `spdk_nvmf_referral_host_allowed()` requires a valid host NQN and either `allow_any_host` or explicit host match.

Target lifecycle:
- `spdk_nvmf_tgt_create()` copies versioned opts, checks unique target name, enforces custom discovery callback presence when requested, initializes subsystems bit array, RB tree, mutex, lists, IO device registration, and running state.
- `spdk_nvmf_tgt_destroy()` removes target from global list and unregisters IO device.
- Destroy callback clears referrals, stops mDNS PRR, removes subsystem listeners, destroys subsystems, frees subsystem ID bitmap, then destroys transports sequentially.

Poll-group lifecycle:
- `nvmf_tgt_create_poll_group()` creates per-transport poll groups, allocates subsystem poll-group array, initializes queued request lists, adds existing subsystems, and links the group to the target.
- `nvmf_tgt_destroy_poll_group_qpairs()` disconnects all qpairs before dropping the IO channel reference.
- `nvmf_tgt_cleanup_poll_group()` destroys transport poll groups and releases namespace IO channels.

Qpair lifecycle:
- `spdk_nvmf_tgt_new_qpair()` asks transport for an optimal poll group, otherwise round-robins, increments unassociated count, and sends add work to that group thread.
- `spdk_nvmf_poll_group_add()` initializes qpair fields, adds it to the transport poll group, links it to the poll group, and marks it connecting.
- `spdk_nvmf_qpair_disconnect()` serializes disconnect with `disconnect_started`, bounces to the group thread if necessary, marks deactivating, drains outstanding work, aborts pending zcopy/AER, and eventually calls `_nvmf_qpair_destroy()`.
- Finalization removes qpair from transport and group, frees auth, invokes transport qpair fini, clears controller qpair bits, and destructs controller on the subsystem thread when no qpairs remain.

Subsystem/poll-group state:
- `poll_group_update_subsystem()` allocates namespace channel state, detects namespace add/remove/replacement/resize and ANA group changes, updates reservation info, and sends namespace/ANA async events to controllers on the current thread.
- Add subsystem clears stale queued requests, updates namespace channels, marks subsystem and namespace info active.
- Remove subsystem marks inactive, disconnects matching qpairs, then releases namespace channels and state.
- Pause subsystem waits for management or namespace IO counters to drain before marking paused.
- Resume subsystem refreshes namespace state, marks active, and replays queued requests via zcopy or normal exec.

Transport/listen behavior:
- `spdk_nvmf_tgt_add_transport()` creates transport poll groups on every target IO channel before linking the transport globally, with rollback on failure.
- Mixed `dif_insert_or_strip` values are deprecated but still allowed with a deprecation log.
- `spdk_nvmf_tgt_listen_ext()` validates opts, finds transport by `trstring`, copies versioned listen opts, and delegates to transport listen op.
- `spdk_nvmf_tgt_stop_listen()` delegates to transport stop-listen.

Configuration dump:
- Emits max subsystem and CRDT settings.
- Dumps transport creation RPCs.
- Dumps referrals.
- Emits batched subsystem creation, host addition, namespace addition, namespace-host visibility, and active listener addition RPCs.
- Listener dump includes transport-specific options, secure channel flag, and optional socket implementation.

Concurrency and ownership:
- Poll-group lists and counts use target mutex.
- Qpair state changes assert execution on the poll-group thread.
- Target transport add/remove uses `spdk_for_each_channel()`.
- Target destroy may re-enter while asynchronous subsystem destruction is in progress.
- Referrals and discovery changes assert app-thread execution.

Notable edge cases:
- `nvmf_tgt_destroy_cb()` frees referrals directly without freeing per-referral host lists, unlike explicit referral removal.
- `nvmf_tgt_destroy_poll_group_qpairs()` logs allocation failure but cannot report it through the destroy callback path.
- `spdk_nvmf_tgt_find_subsystem()` rejects non-null-terminated NQNs within max length before RB lookup.
- Removal and destroy loops retry by reposting messages while qpairs are still disconnecting, so progress depends on transport disconnect completion.

Dependencies:
- Central integration point for `ctrlr_discovery.c` referral filtering and discovery notices.
- Calls mDNS stop/update hooks from `mdns_server.c`.
- Transport-specific behavior is delegated through `transport.h` wrappers and registered transport ops such as FC.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvmf/nvmf.c -->