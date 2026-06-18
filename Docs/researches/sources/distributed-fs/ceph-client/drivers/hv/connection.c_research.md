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
