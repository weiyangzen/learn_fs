# sources/distributed-fs/ceph-client/drivers/infiniband/core/mad.c

## Purpose
`mad.c` implements the kernel InfiniBand Management Datagram access layer for QP0 SMI and QP1 GSI traffic. It registers MAD agents, creates the per-port PD/CQ/QP plumbing, routes inbound MADs to either device firmware hooks or registered clients, handles outgoing sends, retries, timeouts, local directed-route SMP completions, and integrates RMPP support for kernel agents.

## Important APIs, types, and functions
- Exported client APIs include `ib_register_mad_agent()`, `ib_unregister_mad_agent()`, `ib_create_send_mad()`, `ib_free_send_mad()`, `ib_post_send_mad()`, `ib_modify_mad()`, `ib_free_recv_mad()`, `ib_response_mad()`, `ib_get_mad_data_offset()`, `ib_is_mad_class_rmpp()`, `ib_get_rmpp_segment()`, and `ib_mad_kernel_rmpp_agent()`.
- `ib_mad_port_private` owns one port's MAD resources: device/port identity, PD, CQ, ordered workqueue, QP0/QP1 state, and registration tables keyed by class version, management class, method, and optional vendor OUI.
- `ib_mad_agent_private` wraps the public `ib_mad_agent` with send, wait, local-completion, RMPP, and backlog lists plus reference counting and timeout work.
- `ib_mad_send_wr_private` is the send state object. It carries the UD WR, SGEs, DMA mappings, TID, retry counters, RMPP segment cursor, and `enum ib_mad_state`.
- `ib_register_mad_agent()` validates QP type, class/version, RMPP mode, SMI/GSI class restrictions, security setup, and non-overlapping method registration before publishing the agent in the xarray TID namespace.
- `ib_post_send_mad()`, `ib_send_mad()`, `ib_mad_send_done()`, `ib_mad_complete_send_wr()`, `timeout_sends()`, and `retry_send()` form the send pipeline.
- `ib_mad_recv_done()`, `validate_mad()`, `find_mad_agent()`, `ib_find_send_mad()`, and `ib_mad_complete_recv()` form the receive and response-matching path.
- `handle_outgoing_dr_smp()`, `handle_ib_smi()`, `handle_opa_smi()`, and `local_completions()` implement locally consumed or locally generated directed-route SMP behavior.
- `ib_mad_init()` and `ib_mad_cleanup()` register the `mad` `ib_client`; device add/remove callbacks open and close all MAD-capable ports.

## Control flow
Initialization clamps the `send_queue_size` and `recv_queue_size` module parameters, initializes the global port list, and registers an `ib_client`. For each RDMA device, `ib_mad_init_device()` opens every port that advertises MAD capability, then opens the agent helper side. `ib_mad_port_open()` allocates a per-port object, PD, CQ, optional SMI QP0, optional GSI QP1, and ordered workqueue, links the port into the global list, transitions QPs through INIT/RTR/RTS, requests CQ notifications, and posts receive buffers.

Agent registration first checks protocol capability and registration consistency: QP0 only accepts subnet management classes, QP1 rejects them, non-RMPP classes cannot request RMPP, and newer vendor classes require a nonzero OUI. It allocates private state, security context, a high-TID xarray ID, then installs method ownership under `port_priv->reg_lock`. Responses route by high 32 bits of TID through `ib_mad_clients`; requests route through version/class/method tables and vendor OUI tables.

Sending starts in `ib_post_send_mad()`. Directed-route SMPs may be handled locally; otherwise the work request is given a timeout/retry budget and enters `IB_MAD_STATE_SEND_START` or `IB_MAD_STATE_QUEUED` if solicited flow-control limits are exceeded. `ib_send_mad()` maps header and payload DMA, posts to the QP if active slots are available, or appends to the overflow list. Send completions unmap DMA, drain overflow sends, update the state machine, call RMPP completion logic when active, move timed requests to the wait list, and notify the client send handler. Timeout work retries until `retries_left` is exhausted and then reports `IB_WC_RESP_TIMEOUT_ERR`.

Receive completions unmap the receive buffer, build an `ib_mad_recv_wc`, validate base version and QP/class pairing, allocate a response buffer, run SMI directed-route processing for DR SMPs, then give `device->ops.process_mad()` first refusal. Device replies are sent immediately through `agent_send_response()`. Otherwise `find_mad_agent()` selects a client and `ib_mad_complete_recv()` applies security, RMPP reassembly, response matching, callback ordering, and send completion for matched responses. Unmatched GET/SET requests can receive an unsupported-method response.

## State and persistence
State is in kernel memory and RDMA core objects, not durable storage. The global port list is protected by `ib_mad_port_list_lock`; per-port registration tables use `reg_lock`; each agent's send/wait/backlog/local/RMPP lists use `agent->lock`; QP send/receive queues use `ib_mad_queue.lock`. Agent lifetime is reference counted and unregistration waits for completions, cancels sends, removes method registrations, flushes the port workqueue, cancels RMPP receives, and RCU-frees the private agent.

The send state machine moves through INIT, QUEUED, SEND_START, WAIT_RESP, EARLY_RESP, CANCELED, and DONE. Solicited flow-control counters cap outstanding CM, SA, and subnet-management requests and release backlog entries when responses or failures retire work. Receive buffers are continuously reposted; buffers consumed by clients are freed through `ib_free_recv_mad()`.

## Dependencies and integration points
This file is central to `ib_core`. It depends on RDMA device capability helpers, verbs object APIs, DMA mapping, xarray allocation, security hooks from `agent.h`, tracing events, `smi.h` and `opa_smi.h` directed-route helpers, `mad_rmpp.c` for RMPP, `agent_send_response()` for generated responses, and device driver `process_mad` callbacks. It exports symbols used by SA, CM, user MAD, and other kernel RDMA clients.

## Risks
- The send and receive paths are highly concurrent. Incorrect list movement or state transitions can double-complete a send, leak an agent reference, or make responses match canceled requests.
- Registration-table overlap checks must remain exact, especially for class 0 aliasing of directed-route SMPs and vendor OUI slots.
- DMA mapping and unmapping paths differ for normal sends, overflow sends, retries, receive reposting, and local SMP handling. Error path changes can leak mappings or free posted receive buffers.
- RMPP integration changes can affect both request completion ordering and response matching.
- `ib_mad_port_close()` still notes unhandled deallocation of registration tables; correctness depends on agents unregistering before port teardown.
- OPA MAD sizing and pkey-index handling differ from classic IB MADs; mixed IB/OPA paths need careful bounds checks.

## Test signals
- Build with InfiniBand core, MAD, SA, CM, user MAD, and OPA-capable configurations to catch symbol/API drift.
- Exercise agent registration conflicts for duplicate method masks, invalid class versions, SMI/GSI class mismatch, vendor OUI exhaustion, and send-only agents.
- Runtime tests should cover QP0 and QP1 send/receive, solicited request timeout and retry, cancel through `ib_modify_mad(..., 0)`, overflow queue drain, and response-before-send-completion ordering.
- Directed-route SMP tests should cover local consume, local response, switch forwarding, permissive LID validation, and OPA base-version behavior.
- Fault injection around `ib_post_send()`, `ib_post_recv()`, DMA mapping, `process_mad()`, and workqueue teardown is valuable because most bugs here are lifetime or cleanup bugs.
