<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/fastopen.c -->
# sources/distributed-fs/ceph-client/net/mptcp/fastopen.c

## Purpose
Handles server-side MPTCP Fast Open receive-data handoff from the TCP subflow queue into the MPTCP meta-socket receive queue after SYNACK processing.

## Important APIs, Types, and Functions
`mptcp_fastopen_subflow_synack_set_params()` marks the subflow as MPTFO, extracts the first queued skb from the TCP subflow, adjusts subflow sequence accounting, rewrites MPTCP skb control block metadata, transfers memory ownership, queues the skb to the MPTCP socket, updates received bytes, and notifies data readiness.

## Control Flow
The function returns early if early fallback already removed the subflow. It peeks the first TCP receive skb, unlinks it, resets extensions, lends/borrows forward memory between subflow and MPTCP sockets, advances `copied_seq` and `ssn_offset` because Fast Open data is outside MPTCP sequence space, sets a negative `map_seq` delta and `cant_coalesce`, then enqueues the skb under the MPTCP data lock and calls `sk_data_ready()`.

## State and Persistence
Persistent changes include `subflow->is_mptfo`, `subflow->ssn_offset`, TCP `copied_seq`, MPTCP `bytes_received`, receive queue contents, and skb ownership/accounting. No global state is stored.

## Dependencies and Integration Points
Depends on MPTCP protocol internals, TCP Fast Open receive queue behavior, skb extension/control block helpers, socket memory accounting, and MPTCP data locking. It is called from subflow SYN receive handling when Fast Open data is accepted.

## Risks
The code assumes exactly one queued Fast Open skb exists and warns if absent. Sequence offsets are subtle: Fast Open bytes must not enter MPTCP sequence space. Memory-accounting transfer must remain balanced across subflow and meta-socket. The MPTCP socket must not be user-owned while the data lock section runs.

## Test Signals
Server-side MPTCP Fast Open with data in SYN, early fallback path, receive queue ownership/accounting checks, correct application-visible data delivery, no duplicate MPTCP sequence mapping, and WARN coverage for unexpected empty subflow queue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/fastopen.c -->
