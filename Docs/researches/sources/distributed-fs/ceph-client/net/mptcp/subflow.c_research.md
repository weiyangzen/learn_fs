# sources/distributed-fs/ceph-client/net/mptcp/subflow.c

## Purpose
This file is the core MPTCP subflow glue between ordinary TCP sockets and an owning `struct mptcp_sock`. It overrides TCP request, address-family, protocol, and ULP callbacks so MP_CAPABLE and MP_JOIN handshakes can create or attach subflows, then validates DSS mappings on the receive path before data is exposed to the MPTCP-level socket.

## APIs, Types, and Functions
Exported or externally used entry points include `mptcp_subflow_init_cookie_req()`, `mptcp_subflow_reset()`, `__mptcp_sync_state()`, `mptcp_subflow_reqsk_alloc()`, `mptcp_subflow_drop_ctx()`, `__mptcp_subflow_fully_established()`, `mptcp_subflow_data_available()`, `mptcp_space()`, `mptcpv6_handle_mapped()`, `mptcp_info2sockaddr()`, `__mptcp_subflow_connect()`, cgroup inheritance helpers, `mptcp_subflow_create_socket()`, `mptcp_subflow_queue_clean()`, `mptcp_subflow_init()`, and `mptcp_subflow_v6_init()`. Important callback families are `subflow_v4_route_req()`/`subflow_v6_route_req()`, `subflow_*_send_synack()`, `subflow_syn_recv_sock()`, `subflow_finish_connect()`, `subflow_data_ready()`, `subflow_state_change()`, `subflow_ulp_init()`, `subflow_ulp_clone()`, and `subflow_ulp_release()`. `enum mapping_status` classifies receive-side mapping outcomes as OK, invalid, empty, DATA_FIN, fallback dummy, bad checksum, or missing DSS.

## Control Flow
Passive opens start with TCP request allocation redirected to MPTCP-sized request sockets. `subflow_check_req()` parses MPTCP SYN options, rejects prohibited endpoint-manager listener attempts, allocates MP_CAPABLE tokens, resolves MP_JOIN tokens to an existing MPTCP socket, records nonces and local IDs, and stores syncookie JOIN state when needed. ACK processing enters `subflow_syn_recv_sock()`, which clones a TCP child, either creates a new MPTCP parent for MP_CAPABLE or attaches the child to an existing MPTCP socket for MP_JOIN after HMAC and policy checks, and falls back or sends resets for invalid cases.

Active opens complete through `subflow_finish_connect()`. MP_CAPABLE SYN/ACKs establish keys, checksum policy, remote join-id policy, and parent socket state. MP_JOIN SYN/ACKs verify truncated HMAC, record remote nonce/id/backup status, call `mptcp_finish_join()`, and prepare the final HMAC for the third ACK. Additional subflows are opened by `__mptcp_subflow_connect()`, which creates a kernel TCP socket, attaches the MPTCP ULP, syncs sockopts, binds the local address, sends an MP_JOIN connect, and grafts the subflow into the parent socket.

The receive path is driven by `subflow_data_ready()`, `subflow_state_change()`, and `mptcp_subflow_data_available()`. `get_mapping_status()` reads MPTCP skb extensions, installs DSS mapping state, handles DATA_FIN, rejects infinite or mismatched mappings, verifies TCP subflow sequence coverage, and optionally validates DSS checksums across queued skbs. `subflow_check_data_avail()` advances duplicate data, marks data available, enters RFC 8684 checksum failure handling via MP_FAIL when possible, or tries TCP fallback/reset on middlebox-like corruption.

## State and Persistence
Runtime state lives in `struct mptcp_subflow_context` attached as TCP ULP data, in request-sock `struct mptcp_subflow_request_sock`, in parent `struct mptcp_sock`, and in TCP socket queues. Persistent per-subflow fields include local/remote keys, token, nonces, subflow IDs, backup/request flags, local and remote IDs, sequence offsets, current DSS map, checksum accumulator, fallback/failure flags, delegated work state, and saved TCP callbacks. Init functions build alternate request-sock caches and AF/proto callback tables marked `__ro_after_init`; ULP registration is process-wide.

## Dependencies and Integration
The file depends heavily on TCP core request handling, inet/IPv6 AF ops, `tcp_set_ulp()`, MPTCP crypto/token/path-manager helpers, MPTCP work scheduling, MIB counters, tracepoints, cgroup and memcg socket inheritance, LSM `security_mptcp_add_subflow()`, and optional IPv6 and BPF config paths. It is the integration point where Linux TCP sockets become MPTCP subflows and where receive-side TCP data is promoted to MPTCP data.

## Risks
The highest-risk areas are handshake fallback versus fatal reset decisions, ownership transfer of `subflow_req->msk`, lock ordering around listener accept queues and parent sockets, checksum validation across multiple queued skbs, syncookie JOIN reconstruction, and callback/proto restoration during fallback or release. Mapping validation has little tolerance for middlebox-dropped DSS options and can close sockets with `EBADMSG`. Request and child disposal paths rely on exact refcount and list semantics.

## Test Signals
Signals include MPTCP selftests covering MP_CAPABLE, MP_JOIN, backup subflows, port mismatch, fallback, DSS checksum, DATA_FIN, IPv6/v4-mapped behavior, reset reasons, and path-manager policy. Runtime counters such as `MPTCP_MIB_JOIN*`, `MPTCP_MIB_DSS*`, `MPTCP_MIB_DATACSUMERR`, and tracepoints (`trace_get_mapping_status`, `trace_subflow_check_data_avail`) are useful diagnostics.
