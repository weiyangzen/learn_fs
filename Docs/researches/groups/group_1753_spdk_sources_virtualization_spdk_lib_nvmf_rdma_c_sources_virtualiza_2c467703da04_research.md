# Group Research: group_1753_spdk_sources_virtualization_spdk_lib_nvmf_rdma_c_sources_virtualiza_2c467703da04

Scope: `Docs/research_subset_a.md` virtualization/SPDK NVMe-oF transport files. Both listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvmf/rdma.c -->
# File Research: sources/virtualization/spdk/lib/nvmf/rdma.c

## Purpose

`rdma.c` implements SPDK’s NVMe-oF RDMA target transport. It wires the NVMe-oF transport abstraction to RDMA CM/libibverbs resources: RDMA devices, protection domains, memory registration maps, completion queues, shared receive queues, queue pairs, work requests, request state transitions, connection handling, polling, interrupt handling, disconnect handling, and transport statistics.

This file is central to the virtualization/block-storage lane because it exposes NVMe namespaces over RDMA as an NVMe-oF target transport.

## Major Data Structures

- `spdk_nvmf_rdma_transport`: transport-global state, including RDMA CM event channel, accept poller, data work-request mempool, devices, listening ports, poll groups, retry-listen ports, and RDMA-specific options.
- `spdk_nvmf_rdma_device`: per-IB/RDMA device state, including `ibv_context`, `ibv_device_attr`, protection domain, memory map, interrupt handle, readiness/removal flags, and SRQ count.
- `spdk_nvmf_rdma_poll_group`: SPDK transport poll group wrapper with RDMA pollers and aggregate pending-buffer stats.
- `spdk_nvmf_rdma_poller`: per-device poller within a poll group. Owns CQ/comp channel, optional SRQ, shared resources, qpair tree, active qpair list, pending send/recv qpairs, and detailed counters.
- `spdk_nvmf_rdma_qpair`: per-connection state. Tracks RDMA QP, CM IDs, SRQ use, negotiated queue/read/send depths, pending request queues, active-list membership, fused-command tracking, close/destruct state, and cached listen TRID.
- `spdk_nvmf_rdma_resources`: arrays of request objects, recv descriptors, command capsules, completion capsules, in-capsule buffers, plus incoming and free queues.
- `spdk_nvmf_rdma_request`: RDMA-specific wrapper around `spdk_nvmf_request`; tracks request state, recv capsule, data/response WRs, outstanding data WR counts, iov position/offset, fused-pair state, and split RDMA READ chains.
- `spdk_nvmf_rdma_recv`: posted receive WR plus command/in-capsule SGLs and a back pointer to the qpair.

## Transport Registration

The file defines `spdk_nvmf_transport_rdma` and registers it with `SPDK_NVMF_TRANSPORT_REGISTER(rdma, &spdk_nvmf_transport_rdma)`. Its callbacks include:

- option initialization: `nvmf_rdma_opts_init`
- create/destroy: `nvmf_rdma_create`, `nvmf_rdma_destroy`
- listen/stop-listen/discovery: `nvmf_rdma_listen`, `nvmf_rdma_stop_listen`, `nvmf_rdma_discover`
- poll group lifecycle: create, destroy, add/remove qpair, poll, dump stats
- request lifecycle: free, complete, get-buffers-done
- qpair lifecycle and metadata: close, peer/local/listen TRID getters, abort request

## Request State Machine

`nvmf_rdma_request_process()` is the core state machine. Important states:

- `FREE`: request is reusable.
- `NEW`: recv capsule is paired with a request; command is decoded and transfer direction is determined.
- `NEED_DATA_WR`: request needs extra RDMA data WR objects from `data_wr_pool`, usually for multi-SGL or DIF-expanded transfers.
- `NEED_BUFFER`: request needs SPDK iobuf data buffers.
- `HAVE_BUFFER`: local buffers and WR SGLs are ready.
- `DATA_TRANSFER_TO_CONTROLLER_PENDING`: waits for send/read depth before RDMA READ from host.
- `TRANSFERRING_HOST_TO_CONTROLLER`: RDMA READs are outstanding.
- `READY_TO_EXECUTE`: command can enter the NVMe-oF target layer.
- `EXECUTING`: target layer owns execution.
- `EXECUTED`: target execution completed; next step is RDMA WRITE or response SEND.
- `DATA_TRANSFER_TO_HOST_PENDING`: waits for send-depth before RDMA WRITE to host.
- `READY_TO_COMPLETE_PENDING`: waits for send-depth before response SEND.
- `READY_TO_COMPLETE`: queues response and optional controller-to-host data transfer.
- `TRANSFERRING_CONTROLLER_TO_HOST`: RDMA WRITEs plus response SEND are outstanding.
- `COMPLETING`: response SEND is outstanding without data.
- `COMPLETED`: request resources are released.

The state machine also handles qpair error state, inactive qpair cleanup, fused command ordering, DIF generation/verification, pending queues, partial RDMA READ submission, and direct completion on protocol errors.

## Data Transfer Handling

For host-to-controller commands, keyed host SGLs are translated into RDMA READ work requests. If the request needs more RDMA READs than current queue/read depth allows, `request_prepare_transfer_in_part()` splits the chain and resumes later with `nvmf_rdma_request_reset_transfer_in()`.

For controller-to-host commands, local buffers are described as SGEs and chained into RDMA WRITE WRs followed by the response SEND.

For in-capsule data, `nvmf_rdma_request_parse_icd()` validates offset/length against `in_capsule_data_size` and points the request iov directly into the received capsule buffer.

For keyed and multi-SGL descriptors, `nvmf_rdma_request_parse_sgl()`, `nvmf_rdma_request_fill_iovs()`, and `nvmf_rdma_request_fill_iovs_multi_sgl()` allocate buffers, translate local memory into lkeys, fill WR SGEs, and set remote address/rkey fields.

## DIF/Metadata Support

The RDMA path integrates SPDK DIF support:

- `nvmf_rdma_dif_error_to_compl_status()` maps guard/application/reference tag errors to NVMe media status.
- Host-to-controller writes generate DIF before target execution.
- Controller-to-host reads verify DIF after execution and before transfer.
- DIF insert/strip can allocate stripped buffers for controller-to-host operations.
- `nvmf_rdma_fill_wr_sgl_with_dif()` builds SGLs that account for data block size, metadata size, stripped buffers, and WR splitting.

When transport-level `dif_insert_or_strip` is enabled, controller data initialization disables in-capsule data by reducing `ioccsz`.

## RDMA Resource Management

`nvmf_rdma_resources_create()` allocates DMA-capable arrays for request objects, recv descriptors, capsules, completions, and optional in-capsule buffers. It initializes recv WRs, translates local memory to lkeys, queues receive WRs to either a QP or SRQ, initializes response/data WR templates, and populates the free request queue.

`nvmf_rdma_resources_destroy()` frees those resource arrays.

Data WRs beyond the request’s embedded WR are allocated from `rtransport->data_wr_pool` and returned through `nvmf_rdma_request_free_data()` / `_nvmf_rdma_request_free_data()`.

## Connection and QPair Lifecycle

`nvmf_rdma_connect()` handles RDMA CM connect requests. It validates private data, negotiates queue depth/read depth using target limits, local NIC limits, remote RDMA parameters, and host queue sizes, allocates an RDMA qpair, stores CM/listen metadata, sets NUMA information, and submits the qpair to the target.

`nvmf_rdma_poll_group_add()` selects the poller matching the qpair device, initializes QP/resources with `nvmf_rdma_qpair_initialize()`, inserts the qpair into the poller RB tree, and accepts the connection.

`nvmf_rdma_close_qpair()` marks the qpair for close, rejects uninitialized connections if needed, disconnects the provider QP, and attempts destruction after drain.

`nvmf_rdma_destroy_drained_qpair()` waits for outstanding sends/recvs and, for SRQ-capable devices, `LAST_WQE_REACHED` before destroying.

`nvmf_rdma_qpair_destroy()` releases queued requests, RB-tree membership, unprocessed SRQ receives, provider QP, per-qpair resources, async event context, destruct channel, CM ID, and the qpair itself.

## Polling and Completion Processing

`nvmf_rdma_poller_poll()` polls up to 32 CQ entries, handles WR completions by type, updates qpair queue-depth counters, advances request state, reposts receives, submits batched sends/recvs, processes active qpairs, and disconnects on CQ errors.

Completion behavior by WR type:

- `RDMA_WR_TYPE_RECV`: increments current recv depth, timestamps the request, places recv on incoming queue, activates qpair, and increments queue depth.
- `RDMA_WR_TYPE_DATA`: tracks RDMA READ completion, read/send depth, partial read continuation, and transition to ready-to-execute.
- `RDMA_WR_TYPE_SEND`: marks response completion, frees request state, and decrements send depth including chained data WRs.

`_poller_submit_recvs()` and `_poller_submit_sends()` flush batched WRs to SRQs/QPs. Failure paths disconnect affected qpairs and repair local counters.

The file supports both normal polling and interrupt mode. Interrupt mode uses completion channels and `nvmf_rdma_poll_group_intr()`.

## Device, Port, and Event Handling

`nvmf_rdma_create()` initializes transport state, parses RDMA-specific JSON options, validates max I/O size and in-capsule minimums, creates the RDMA CM event channel, creates the data WR pool, discovers RDMA devices, creates `spdk_nvmf_rdma_device` objects, builds poll fds, and registers the accept poller.

`create_ib_device()` queries device attributes, handles SEND_WITH_INVALIDATE capability quirks, creates/obtains a protection domain, creates a memory map, and registers async interrupts when needed.

`nvmf_rdma_listen()` validates TRID service ID/address family, creates/binds/listens on an RDMA CM ID, maps it to a known ready device, and stores the listening port.

`nvmf_rdma_accept()` polls the RDMA CM event channel plus device async fds. It also retries listen ports after device removal/reappearance.

`nvmf_process_cm_events()` handles RDMA CM events including connect requests, disconnects, device removals, and address changes. Port/device removal paths stop listening, disconnect affected qpairs, move ports to retry lists, and remove pollers/devices asynchronously.

`nvmf_process_ib_event()` handles verbs async events. QP fatal/access/request errors mark qpairs in error; LAST_WQE_REACHED is forwarded to the qpair thread; device fatal marks the device for removal.

## Scheduling and Load Balancing

`nvmf_rdma_get_optimal_poll_group()` picks poll groups for new qpairs. Admin qpairs rotate round-robin; I/O qpairs scan poll groups and choose the one with the lowest current I/O plus unassociated qpair count, then rotate from that point.

## Abort Semantics

`nvmf_rdma_qpair_abort_request()` finds the in-flight RDMA request matching an abort CID. `_nvmf_rdma_qpair_abort_request()` handles abort by state:

- executing requests delegate to controller abort.
- pending buffer/data-WR/RDMA-read/RDMA-write/send requests are removed from their queues and completed as aborted.
- host-to-controller transfers wait until timeout if RDMA READs are in flight.
- missing target request completes the abort command normally.

## Statistics and Tracing

The file registers tracepoints for RDMA request states, QP create/disconnect/destroy, RDMA CM async events, and IB async events. `nvmf_rdma_poll_group_dump_stat()` emits JSON stats including polls, idle polls, completions, requests, request latency, pending queues, total send/recv WRs, and doorbell updates.

## Error Handling Patterns

The implementation is defensive around hardware and asynchronous teardown:

- queue depth and send/read depth are asserted and throttled.
- CQ resize failure rejects qpair initialization.
- invalid SGLs complete with NVMe SGL status codes.
- no-buffer paths queue requests and resume through callbacks.
- CQ/WR failures move qpairs into error state and disconnect.
- device removal avoids new verbs operations and only destroys resources.
- SRQ late completions for destroyed QPs are ignored and recvs are reposted.
- rxe/iWARP limitations are explicitly handled.

## External Dependencies

This file depends heavily on:

- SPDK NVMe-oF internals: qpair/request execution, buffer allocation, poll groups, transport ops.
- SPDK RDMA provider wrappers: QP/SRQ create, accept, disconnect, queue/flush WRs, stats.
- SPDK RDMA utilities: memory maps, lkey translation, CQ polling.
- RDMA CM and libibverbs: CM events, device attributes, CQs, comp channels, async events, QPs/SRQs.
- SPDK tracing, logging, JSON, mempool, iobuf, threading, interrupts, and DIF helpers.

## Notable Implementation Details

- The RDMA transport supports both per-QP receive queues and shared receive queues.
- Request objects are intentionally separate from recv capsules because RDMA completions may deliver new commands when no request object is free.
- Work request batching is the default; `no_wr_batching` forces immediate flushes.
- Multi-SGL support uses in-capsule descriptors and extra data WRs from a mempool.
- SEND_WITH_INVALIDATE is conditionally enabled and disabled for Soft-RoCE devices despite reported capabilities.
- Listener ports removed by device events are retried after device rescan.
- The qpair tree is keyed by QP number to map SRQ receive completions back to qpairs.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvmf/rdma.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvmf/stubs.c -->
# File Research: sources/virtualization/spdk/lib/nvmf/stubs.c

## Purpose

`stubs.c` provides fallback implementations for optional NVMe-oF features when SPDK is built without selected configuration capabilities. It keeps the NVMf library linkable while making unsupported feature use explicit.

## Conditional Stub Areas

### Authentication Without EVP MAC

When `SPDK_CONFIG_HAVE_EVP_MAC` is not defined, this file stubs NVMe-oF authentication support:

- `nvmf_qpair_auth_init()` returns `-ENOTSUP`.
- `nvmf_qpair_auth_destroy()` asserts that `qpair->auth` is `NULL`.
- `nvmf_qpair_auth_dump()` emits nothing.
- `nvmf_auth_request_exec()` completes the request with generic invalid opcode status and returns asynchronous completion status.
- `nvmf_auth_is_supported()` returns `false`.
- Registers the `nvmf_auth` log component in this build mode.

The behavior is explicit: authentication is unavailable, and authentication commands are rejected as invalid opcodes.

### RDMA Hooks Without RDMA

When `SPDK_CONFIG_RDMA` is not defined, `spdk_nvmf_rdma_init_hooks()` logs an error and aborts. This prevents code from silently installing RDMA hooks in a build that lacks RDMA transport support.

### mDNS PRR Without Avahi

When `SPDK_CONFIG_AVAHI` is not defined, this file stubs mDNS PRR publishing:

- `nvmf_publish_mdns_prr()` logs that Avahi support is required and returns `-ENOTSUP`.
- `nvmf_tgt_stop_mdns_prr()` is a no-op.
- `nvmf_tgt_update_mdns_prr()` returns success.

## Dependencies

The file includes SPDK config, logging, NVMe-oF transport declarations, and `nvmf_internal.h`. Its behavior is entirely controlled by compile-time feature macros.

## Role in the Source Tree

This is a small build-configuration compatibility file. It does not implement normal transport or filesystem behavior; instead, it defines clear failure/no-op behavior for optional authentication, RDMA, and Avahi-dependent mDNS features when those dependencies are absent.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvmf/stubs.c -->