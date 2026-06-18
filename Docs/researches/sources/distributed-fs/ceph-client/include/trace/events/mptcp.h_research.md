# sources/distributed-fs/ceph-client/include/trace/events/mptcp.h

Purpose: Defines tracepoints for Multipath TCP subflow selection, mapping-extension inspection, ACK advancement, data-availability checks, and receive-buffer growth. It turns MPTCP socket/subflow state into stable ftrace/perf records without adding runtime state outside the tracing subsystem.

Important APIs/types/functions: `TRACE_SYSTEM mptcp`; `mptcp_subflow_get_send`; `DECLARE_EVENT_CLASS(mptcp_dump_mpext)` reused by `mptcp_sendmsg_frag` and `get_mapping_status`; `ack_update_msk`; `subflow_check_data_avail`; `mptcp_rcvbuf_grow`. The events read `struct sock`, `struct mptcp_subflow_context`, `struct mptcp_ext`, `struct mptcp_sock`, TCP `write_seq`, subflow token, data sequence numbers, mapping lengths, checksum flags, and reset reasons.

Control flow: MPTCP transmit paths emit send-subflow and mapping events while choosing where data is sent. Receive paths emit ACK-update, data-available, and receive-buffer growth events as DSS mappings are validated and the meta socket advances. Trace fast-assign blocks snapshot mutable socket fields into ring-buffer entries before printing.

State and persistence: No durable state is owned. Event records are transient tracing output; sampled state belongs to MPTCP sockets, TCP subflows, and skb extension metadata.

Dependencies and integration points: Depends on TCP/IPv6/MPTCP socket structures, `sock_diag`, reset-reason helpers, and `trace/events/net_probe_common.h` address/port assignment macros. It integrates with `net/mptcp` diagnostic workflows and generic kernel trace infrastructure.

Risks and test signals: Risks include reading subflow fields after lifecycle changes, confusing host/network byte order in address fields, format drift when MPTCP structs change, and tracepoint overhead on hot data paths. Test with MPTCP selftests for multi-subflow send/receive, DSS checksum, fallback/reset, IPv4/IPv6, and tracepoint enable/disable while exercising packet loss and re-injection.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/mptcp.h` completely for this pass (264 lines, 7145 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/mptcp.h_research.md`.
