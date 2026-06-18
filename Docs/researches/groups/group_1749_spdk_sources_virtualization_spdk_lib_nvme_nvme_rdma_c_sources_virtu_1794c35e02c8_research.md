# Group Research: group_1749_spdk_sources_virtualization_spdk_lib_nvme_nvme_rdma_c_sources_virtu_1794c35e02c8

Scope: `Docs/research_subset_a.md`, covering `sources/virtualization/spdk`.

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_rdma.c -->
# File Research: sources/virtualization/spdk/lib/nvme/nvme_rdma.c

Implements SPDK's NVMe-oF RDMA initiator transport and registers it through `SPDK_NVME_TRANSPORT_REGISTER(rdma, &rdma_ops)`. The file owns RDMA-specific controller, qpair, poll-group, request, response, memory-registration, connection, completion, and teardown behavior behind the generic NVMe transport interface.

Key structures:
- `nvme_rdma_ctrlr`: embeds `spdk_nvme_ctrlr`, tracks max SGE, RDMA CM channel, and queued/free CM event wrappers.
- `nvme_rdma_qpair`: embeds `spdk_nvme_qpair`, owns RDMA CM ID, provider QP, CQ/channel, SRQ association, request/response pools, memory map, outstanding/free request lists, state, retry, and disconnect bookkeeping.
- `nvme_rdma_poller` and `nvme_rdma_poll_group`: share CQs/SRQs per RDMA device and coordinate active, connecting, and disconnected qpairs.
- `spdk_nvme_rdma_req` and `spdk_nvme_rdma_rsp`: per-command send and receive WR context, with completion flags used to wait for both SEND and RECV completion before completing an NVMe request.

Connection flow:
- `nvme_rdma_ctrlr_construct()` allocates the RDMA controller, clamps retry and ACK timeout options, discovers RDMA devices to determine `max_sge`, initializes generic controller state, creates a nonblocking RDMA CM event channel, creates admin qpair, and registers the process.
- `nvme_rdma_ctrlr_connect_qpair()` parses destination/source addresses, creates an RDMA CM ID, starts address resolution, and enqueues qpairs into a poll-group connecting list when applicable.
- `nvme_rdma_process_event_start()` and `nvme_rdma_process_event_poll()` drive async RDMA CM events through expected states. Stale connection rejection is treated specially with retry and lingering cleanup.
- `nvme_rdma_qpair_init()` creates or attaches to CQ/SRQ resources, gets a protection domain via hooks or SPDK RDMA utils, creates the provider QP, records QP number, and inserts SRQ qpairs into an RB tree for completion lookup.
- After RDMA connection establishment, `nvme_rdma_connect_established()` creates the memory map, request pool, response buffers, posts receives, then moves to Fabric CONNECT send/poll and optional authentication states.

Request construction:
- Supports null, contiguous, callback SGL, and iovec payloads.
- Uses keyed SGLs for normal RDMA data transfer, and inline in-capsule data when the operation is host-to-controller, payload fits `ioccsz_bytes`, and `icdoff == 0`.
- Enforces `NVME_RDMA_MAX_KEYED_SGL_LENGTH`, controller SGE limits, and capsule descriptor size.
- `nvme_rdma_get_memory_translation()` either translates a caller memory domain into RDMA keys or uses the qpair memory map.
- Optional accel/UMR path uses poll-group accel hooks to create per-I/O virtual contiguous memory and reverses sequences for controller-to-host data.

Completion flow:
- SEND and RECV work completions are processed either per-qpair or through shared pollers.
- `nvme_rdma_process_recv_completion()` stores the NVMe completion, reposts receives when safe, and completes only after SEND completion has also arrived.
- `nvme_rdma_process_send_completion()` marks SEND completion and similarly waits for RECV completion.
- `nvme_rdma_request_ready()` handles memory-domain transfer callbacks or completes the NVMe request.
- Completion errors map to transport failure and trigger qpair disconnect.

Disconnect and failure handling:
- Qpairs move through `EXITING`, `LINGERING`, and `EXITED`; lingering avoids freeing WR memory while shared CQ completions may still reference it.
- Stale connection retry has a separate `STALE_CONN` and `STALE_CONN_LINGERING` path to avoid use-after-free when reconnecting after rejected stale CM state.
- `nvme_rdma_qpair_abort_reqs()` completes outstanding requests with aborted status but avoids aborting in-progress accel transfers until safe.
- Destruction carefully acknowledges CM events, removes pending events, destroys QP/CQ/channel, releases poller/SRQ references, frees request/response pools, frees memory maps, releases PD, and destroys CM ID last.

Poll groups and stats:
- A poll group holds one poller per RDMA device. Pollers may own shared CQs and optional SRQs.
- Shared SRQ mode maps completions back to qpairs by QP number using an RB tree.
- `nvme_rdma_poll_group_process_completions()` handles disconnected qpairs, connecting qpairs, CM events, CQ polling, active qpair submit flushing, receive reposting, and timeout checks.
- `nvme_rdma_poll_group_get_stats()` reports per-device polls, idle polls, completions, queued requests, and RDMA send/recv WR and doorbell counters.

Transport ops:
- Implements controller construct/destruct/enable/interrupts, register access through fabrics helpers, max transfer/SGE reporting, IO qpair create/delete/connect/disconnect, memory-domain reporting, transport event processing, qpair submit/poll/reset/abort/authenticate, admin AER abort, and poll-group lifecycle/stats.
- `spdk_nvme_rdma_init_hooks()` stores external RDMA hooks globally in `g_nvme_hooks`.

Filesystem/storage relevance:
- This is a host-side remote block storage transport for NVMe namespaces over RDMA. It is not a filesystem implementation, but it is directly in the storage substrate path: request payload mapping, DMA memory registration, transport recovery, and completion behavior all affect block I/O visibility and latency to higher layers.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_rdma.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_stubs.c -->
# File Research: sources/virtualization/spdk/lib/nvme/nvme_stubs.c

Provides compile-time fallback stubs for optional NVMe features when SPDK is built without specific configuration flags.

Covered feature gates:
- `!SPDK_CONFIG_NVME_CUSE`: CUSE controller/namespace naming, register, unregister, and namespace update APIs log unsupported errors. Functions returning status use `-ENOTSUP`; namespace update is `void` and only logs.
- `!SPDK_CONFIG_RDMA`: `spdk_nvme_rdma_init_hooks()` logs that RDMA transport is unavailable and aborts. This prevents silently accepting RDMA hook configuration in a build without RDMA support.
- `!SPDK_CONFIG_HAVE_EVP_MAC`: NVMe in-band authentication async, poll, and public qpair authenticate APIs return `-ENOTSUP`, with logging on entry points.

Role in the codebase:
- Keeps public/internal symbols available across reduced builds without forcing callers to scatter feature-conditionals.
- Makes unsupported features fail explicitly rather than linking to missing symbols.
- The RDMA hook stub is intentionally fatal, unlike CUSE/auth stubs, because installing RDMA hooks when RDMA is unavailable indicates an invalid build/runtime path.

Filesystem/storage relevance:
- Indirect storage infrastructure support. It controls feature availability for NVMe device presentation, RDMA transport hooks, and fabric authentication, all of which may affect how block devices are exposed to upper layers.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_stubs.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_tcp.c -->
# File Research: sources/virtualization/spdk/lib/nvme/nvme_tcp.c

Implements SPDK's NVMe/TCP initiator transport and registers it through `SPDK_NVME_TRANSPORT_REGISTER(tcp, &tcp_ops)`. The file owns TCP socket connection setup, ICReq/ICResp negotiation, NVMe-oF Fabric CONNECT, optional authentication, PDU parsing/validation, request serialization, H2C/C2H data movement, digest handling, TLS PSK setup, poll-group socket polling, stats, and trace registration.

Key structures:
- `nvme_tcp_ctrlr`: embeds `spdk_nvme_ctrlr` and stores TLS PSK identity/key/cipher-suite state.
- `nvme_tcp_qpair`: embeds `spdk_nvme_qpair`, owns socket, request pools, send queue, receive/send PDUs, PDU receive state, negotiated digest and data limits, connection state, polling and timeout list links, stats pointer, and async completion count.
- `nvme_tcp_req`: per-command state including NVMe request pointer, CID, transfer tags, offsets, R2T tracking, ordering bits, payload iovs, response cache, and PDU pointer.

Connection flow:
- `nvme_tcp_ctrlr_construct()` allocates controller state, optionally derives TLS credentials from an NVMe TCP interchange PSK, clamps ACK timeout, initializes generic controller state, marks accel-sequence support, creates admin qpair, and registers the process.
- `nvme_tcp_qpair_connect_sock()` parses destination/source addresses, chooses SSL socket implementation when PSK is configured, sets socket options including priority, zero-copy for IO qpairs, source address/port, ACK timeout, and connect timeout, then starts async connect.
- `nvme_tcp_sock_connect_cb_fn()` moves to `INITIALIZING` and sends ICReq.
- `nvme_tcp_icresp_handle()` validates protocol format version, `maxh2cdata`, `cpda`, negotiates header/data digests, adjusts receive buffer sizing, then advances to Fabric CONNECT once ICReq send is acknowledged.
- `nvme_tcp_ctrlr_connect_qpair_poll()` drives socket connecting, ICReq timeout, Fabric CONNECT send/poll, optional authentication, and final connected state.

Request submission:
- `nvme_tcp_alloc_reqs()` creates cacheline-aligned request array and DMA PDU buffers.
- `nvme_tcp_req_init()` assigns CID, builds NVMe TCP transport SGL descriptors, and decides whether host-to-controller data can be sent as in-capsule data.
- Supports contiguous, callback SGL, and iovec payloads; controller-to-host payload iovs are built when C2H data arrives.
- Memory-domain payloads are translated to the system domain through `nvme_tcp_try_memory_translation()`.
- `nvme_tcp_qpair_capsule_cmd_send()` creates Capsule Command PDUs, handles padding and digests, attaches in-capsule data when applicable, and sends asynchronously.

PDU handling:
- Receive state machine: `AWAIT_PDU_READY`, common header, protocol-specific header, request buffer/data, quiescing, and error.
- `nvme_tcp_pdu_ch_handle()` validates PDU type, header length, payload length, and sequence legality, sending H2C TermReq on protocol errors.
- `nvme_tcp_pdu_psh_handle()` verifies header digest when present and dispatches ICResp, Capsule Response, C2H Data, C2H TermReq, or R2T.
- `nvme_tcp_c2h_data_hdr_handle()` validates CID, flags, `datao`, `datal`, range, and maps target data into request payload iovs.
- `nvme_tcp_r2t_hdr_handle()` validates R2T offset/length and max active R2T count, supports a queued subsequent R2T while waiting for H2C send acknowledgement, and sends H2C Data PDUs.
- `nvme_tcp_pdu_payload_handle()` validates data digest when enabled and completes payload processing.

Completion ordering:
- TCP requests complete only when send acknowledgement, data/response receipt, and any accel operation have all completed.
- `nvme_tcp_req_complete_safe()` centralizes this gate.
- `nvme_tcp_qpair_cmd_send_complete()` handles command send acknowledgement and may trigger deferred H2C send after R2T.
- `nvme_tcp_c2h_data_payload_handle()` and `nvme_tcp_capsule_resp_hdr_handle()` set response/data receipt and may finish/reverse accel sequences before completing.
- `nvme_tcp_req_complete()` removes the request from outstanding list, updates queue depth and tracepoints, returns it to the free list, and calls the original NVMe callback.

Digest and accel behavior:
- Header digest is computed inline when negotiated.
- Data digest may use accel `append_crc32c` when available and constraints are met, falling back to software CRC32C on resource exhaustion.
- Existing request accel sequences are finished before transmitting host-to-controller data and reversed before completing controller-to-host transfers.

Disconnect and failure:
- `nvme_tcp_ctrlr_disconnect_qpair()` removes sockets from poll groups, closes sockets, clears send queue, aborts requests, and either quiesces async qpairs or completes disconnect immediately for synchronous paths.
- `nvme_tcp_qpair_abort_reqs()` completes non-accel in-flight requests with aborted status.
- Quiescing waits for outstanding requests, especially accel-backed ones, before moving receive state to error and final disconnect.
- Transport errors set `SPDK_NVME_QPAIR_FAILURE_UNKNOWN` and disconnect the qpair.

Poll groups, stats, and trace:
- Poll groups own an SPDK socket group, `needs_poll` list for qpairs that require progress without socket events, timeout-enabled list, and aggregate TCP stats.
- `nvme_tcp_poll_group_process_completions()` polls socket events, handles disconnected qpairs, forces polling for `needs_poll`, runs timeout checks, and accumulates socket/NVMe completion stats.
- `nvme_tcp_poll_group_get_stats()` snapshots TCP stats into generic transport stats.
- `nvme_tcp_trace()` registers TCP submit/complete tracepoints and relations to socket request tracepoints.

Transport ops:
- Implements controller construct/destruct/enable, fabric register access helpers, max transfer/SGE reporting, IO qpair lifecycle, system memory-domain reporting, qpair submit/poll/reset/abort/authenticate, admin AER abort, poll-group lifecycle/stats, and trace registration.
- No interrupt fd support is implemented here; socket poll groups are the primary event path.

Filesystem/storage relevance:
- This is the TCP remote block transport for NVMe namespaces. It is critical to storage behavior because it converts NVMe requests into TCP PDUs, handles target-driven reads/writes through C2H/H2C flows, enforces protocol correctness, manages data integrity digests, and determines error/reconnect semantics exposed to upper storage users.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_tcp.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_transport.c -->
# File Research: sources/virtualization/spdk/lib/nvme/nvme_transport.c

Implements the generic NVMe transport registry and dispatch layer used by PCIe, RDMA, TCP, and other transports. It stores registered transport ops, exposes availability queries, wraps controller/qpair operations, handles poll-group membership state, and stores process-wide transport options.

Registry:
- `g_spdk_nvme_transports` is a global TAILQ of registered transports.
- `g_transports` is a fixed array of 16 transport slots.
- `spdk_nvme_transport_register()` rejects duplicate transport names and over-capacity registration, then copies the ops table and appends it to the registry.
- `nvme_get_transport()` performs case-insensitive lookup by transport name; helpers expose first/next iteration and availability by type or name.

Controller dispatch:
- Construction, scan, attached scan, destruct, enable, readiness, register access, CMB/PMR operations, max transfer size, max SGEs, memory-domain reporting, and transport-event processing are all routed to transport ops.
- Optional ops return explicit unsupported defaults such as `-ENOTSUP`, `-ENOSYS`, `NULL`, or `0` depending on semantics.
- Async register operations fall back to synchronous op execution followed by a queued synthetic completion via `nvme_queue_register_operation_completion()`.

Qpair lifecycle:
- `nvme_transport_ctrlr_create_io_qpair()` delegates qpair creation and stores the transport pointer on non-admin qpairs for fast IO-path dispatch.
- Delete deliberately looks up the transport by controller TRID instead of trusting `qpair->transport`, because multiprocess PCIe cases can invalidate function-pointer objects across processes.
- Connect sets qpair state to connecting, clears current transport failure reason while saving the previous one, invokes transport connect, attaches poll-group state, and busy-polls synchronous connects until the qpair leaves connecting state.
- Connect failure restores the saved failure reason and disconnects.
- Disconnect moves the qpair to disconnecting, updates poll-group membership when owned by the active process, and delegates transport-specific disconnect.
- `nvme_transport_ctrlr_disconnect_qpair_done()` aborts queued requests for the active process/admin queue, marks disconnected, wakes poll-group disconnect handling, and cleans up outstanding fabric/auth polling state.

Qpair operation dispatch:
- Abort, reset, submit, process completions, and iterate requests use `qpair->transport` for non-admin qpairs and lookup-by-controller for admin qpairs.
- Authentication and admin AER abort are dispatched through transport ops.
- Qpair fd retrieval is optional and returns `-ENOTSUP` when absent.

Poll groups:
- `nvme_transport_poll_group_create()` delegates creation, records the transport, initializes connected/disconnected qpair lists, and starts connected count at zero.
- Add/remove operate only on disconnected qpairs.
- Connect/disconnect transitions move qpairs between connected and disconnected STAILQs and maintain `num_connected_qpairs`.
- Completion processing, disconnected qpair checks, destroy, stats get/free are delegated to transport ops.

Transport options:
- Global defaults: RDMA SRQ size `0`, RDMA max CQ size `0`, RDMA CM event timeout `1000 ms`, RDMA UMR-per-I/O disabled, TCP connect timeout `0`.
- `spdk_nvme_transport_get_opts()` and `spdk_nvme_transport_set_opts()` copy fields based on struct size/offset for ABI compatibility.
- Setter validates `tcp_connect_timeout_ms <= INT_MAX`.
- Static assert requires `spdk_nvme_transport_opts` size to remain 32 bytes unless copy logic is updated.

Filesystem/storage relevance:
- This file is the common transport abstraction for all SPDK NVMe block-device access. It does not move data itself, but it defines how higher-level NVMe controller and qpair code interacts with local and fabric transports, including connection state, polling, failure, options, and stats routing.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_transport.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_util.c -->
# File Research: sources/virtualization/spdk/lib/nvme/nvme_util.c

Provides utility helpers for command-line transport ID usage text, parsing extended transport ID entries, and building human-readable NVMe controller/namespace names.

`spdk_nvme_transport_id_usage()`:
- Prints `-r` / optional `--transport` usage text for transport IDs.
- Adapts output based on flags for mandatory/optional, no PCIe, no fabric, namespace support, host NQN, host address, alternative transport address, and multiple entries.
- Documents accepted keys including `trtype`, fabric `adrfam`, `traddr`, `trsvcid`, `subnqn`, optional `ns`, `hostnqn`, `hostaddr`, and `alt_traddr`.
- Prints PCIe and RDMA examples and a note for multi-target input when enabled.

`spdk_nvme_trid_entry_parse()`:
- Initializes the transport ID to PCIe and default discovery NQN before parsing the generic transport ID string.
- Parses optional `ns:` or `ns=` into a 16-bit namespace ID, rejecting IDs longer than five digits, zero, or greater than 65535.
- Parses optional `hostnqn:`/`hostnqn=`, enforcing destination buffer length.
- Parses optional `hostaddr:`/`hostaddr=`, allowing it only for fabrics transports and enforcing `SPDK_NVMF_TRADDR_MAX_LEN`.
- Initializes `failover_trid` from the primary TRID, then applies optional `alt_traddr:`/`alt_traddr=` with length validation.
- Returns `-EINVAL` on malformed input and logs specific validation errors.

`spdk_nvme_build_name()`:
- Builds readable names by transport type:
  - PCIe: `PCIE (<traddr>)`, optionally adding PCI vendor/device ID when a PCI device is available.
  - RDMA: `RDMA (addr:<traddr> subnqn:<subnqn>)`.
  - TCP: `TCP (addr:<traddr> subnqn:<subnqn>)`.
  - VFIOUSER and CUSTOM with transport address.
- Optionally appends `NSID <id>` when a namespace is provided.
- Returns formatting errors when `snprintf()` fails or unknown transport type is encountered.

Implementation notes:
- Uses case-insensitive substring searches for extension keys, supporting both colon and equals separators.
- Parsing is simple and whitespace-delimited; it assumes values do not contain spaces.
- The `hostnqn += strlen("hostnqn:")` style also works for `hostnqn=` because the key length is the same.

Filesystem/storage relevance:
- This file supports operational tooling and user input for selecting NVMe block devices and namespaces. It is not on the data path, but it shapes how local PCIe and NVMe-oF targets are identified, named, and configured by SPDK applications.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_util.c -->