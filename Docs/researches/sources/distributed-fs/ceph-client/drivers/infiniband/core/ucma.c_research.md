# sources/distributed-fs/ceph-client/drivers/infiniband/core/ucma.c

## Purpose

`ucma.c` implements the userspace RDMA Connection Manager access device exposed as the misc character device `infiniband/rdma_cm`. It translates packed `rdma_ucm_*` write commands from userspace into RDMA CM operations, reports asynchronous CM events back to userspace, and owns the userspace-visible IDs for RDMA CM contexts and multicast memberships. It is the bridge between librdmacm-style connection management and kernel `rdma_cm_id` state.

## Important APIs, Types, and Functions

- `struct ucma_file` is per-open-file state: command mutex, file pointer, context list, event list, and poll waitqueue.
- `struct ucma_context` wraps a userspace CM ID. It stores the integer ID, `rdma_cm_id`, file ownership, UID supplied by userspace, reference count, completion used during destruction, backlog accounting, multicast list, and deferred close work.
- `struct ucma_multicast` stores multicast membership IDs, join state, user UID, target address, event count, and owner context.
- `struct ucma_event` is queued to `ucma_file.event_list` and carries the `rdma_ucm_event_resp` returned by `RDMA_USER_CM_CMD_GET_EVENT`.
- Global `ctx_table` and `multicast_table` xarrays allocate and resolve userspace IDs. Entries are temporarily replaced with `XA_ZERO_ENTRY` during teardown to prevent duplicate destroy paths.
- Command handlers include `ucma_create_id`, `ucma_destroy_id`, `ucma_bind`, `ucma_resolve_addr`, `ucma_resolve_route`, `ucma_query`, `ucma_connect`, `ucma_listen`, `ucma_accept`, `ucma_reject`, `ucma_disconnect`, `ucma_set_option`, `ucma_join_multicast`, `ucma_leave_multicast`, `ucma_migrate_id`, and `ucma_write_cm_event`.
- File operations are `ucma_open`, `ucma_write`, `ucma_poll`, and `ucma_close`.
- Module registration is through `misc_register`, a sysfs `abi_version` attribute, a `net/rdma_ucm/max_backlog` sysctl, and an `ib_client` named `rdma_cm`.

## Control Flow

Userspace writes a `rdma_ucm_cmd_hdr` followed by command-specific input to `ucma_write`. The dispatcher validates safe file access, command number, input length, and command availability, then calls the indexed handler from `ucma_cmd_table`. Most handlers copy a command struct from userspace, resolve a `ucma_context` with `ucma_get_ctx` or `ucma_get_ctx_dev`, serialize against `ctx->mutex`, invoke an `rdma_*` CM API, copy an optional response, and drop the context reference.

`ucma_create_id` allocates a context ID in `ctx_table`, creates an `rdma_cm_id` with `ucma_event_handler`, sets the userspace UID, and publishes the context to the file's context list and xarray. Listener connect requests follow a different path: `ucma_event_handler` routes `RDMA_CM_EVENT_CONNECT_REQUEST` to `ucma_connect_event_handler`, which decrements listener backlog, creates a child `ucma_context` around the new `rdma_cm_id`, queues a connect-request event, and only exposes the child after it is in the file context list.

Events are generated from RDMA CM callbacks by `ucma_create_uevent`. `ucma_get_event` blocks unless `O_NONBLOCK` is set, copies the first queued event to userspace, updates reported-event counters, restores listener backlog for connect requests after userspace consumes them, and frees the event. Query paths convert route, address, GID, path, and service-record kernel state into older user ABI structs.

Multicast joins are allocated in `ucma_process_join`. The code creates a private `ucma_multicast`, reserves an xarray ID, links it on `ctx->mc_list`, calls `rdma_join_multicast`, copies the multicast ID back, and only then stores the public xarray pointer. Leaving erases the xarray entry, calls `rdma_leave_multicast`, cleans queued events for that multicast, reports the number of delivered events, and frees the object.

Device removal is handled asynchronously. `ucma_event_handler` queues `close_work` when it sees `RDMA_CM_EVENT_DEVICE_REMOVAL`. `ucma_close_id` waits for outstanding references, destroys the `rdma_cm_id`, and clears `ctx->cm_id`, while the userspace context can remain until explicit destruction.

## State and Persistence

All state is runtime kernel memory. Persistence is limited to registered device nodes, sysfs attributes, and the sysctl while the module is loaded. Important mutable state includes xarray ID mappings, file-owned context and event lists, context reference counts, RDMA CM state in `rdma_cm_id`, backlog counts, and multicast join records. `ctx->file` can change during `ucma_migrate_id`; that path locks the RDMA handler and xarray, moves queued events between files, and reports prior event counts.

## Dependencies and Integration Points

The file integrates tightly with `rdma_cm`, `ib_cm`, SA path conversion helpers, RDMA netlink client discovery, Linux misc devices, xarrays, waitqueues, sysctl, and security namespace helpers. It uses `ib_copy_*_to_user` marshalling helpers for ABI structs and `rdma_cap_*` protocol checks to format route responses for IB, RoCE, and iWARP.

## Risks

The primary risks are lifetime and concurrency bugs at the userspace/kernel boundary: racing destroy, event callback, file close, migrate, and device removal paths. The xarray `XA_ZERO_ENTRY`, refcount completion, handler locks, and per-file mutexes are essential. User-provided sizes, command lengths, UIDs, QP types, private data lengths, and multicast address sizes need strict validation because this is a world-writable device node. Backlog accounting is subtle: connect-request events decrement backlog before queueing and increment it when userspace consumes the event. Any missed cleanup of queued connect-request child contexts can leak CM IDs. Copy-to-user failures after kernel-side operations can also leave partially completed state, so error unwinds are security-sensitive.

## Test Signals

Useful signals include successful `rdma_cm` ABI version reads, create/destroy ID cycles, blocking and nonblocking event reads, listener backlog exhaustion and recovery, connect request accept/reject paths, address and route resolution across IB/RoCE/iWARP, multicast join/leave with event counts, migration between two open FDs, safe denial after credential changes, and device-removal teardown without use-after-free or leaked xarray entries. Fault injection around `copy_to_user`, allocation failures, and RDMA CM callbacks is especially relevant.
