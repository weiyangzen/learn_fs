# sources/distributed-fs/ceph-client/include/trace/events/nbd.h

Purpose: Defines trace event classes for Network Block Device transport I/O and request send attempts. It exposes byte counts, handles, request types, and index/name information for diagnosing userspace-backed block device traffic.

Important APIs/types/functions: `DECLARE_EVENT_CLASS(nbd_transport_event)` underlies `nbd_header_sent`, `nbd_payload_sent`, `nbd_header_received`, and `nbd_payload_received`. `DECLARE_EVENT_CLASS(nbd_send_request)` underlies request-send events and captures `struct nbd_request`, command cookie, type string, index, and size.

Control flow: NBD send and receive paths emit transport events as headers or payload fragments cross a socket. Request submission emits send-request traces as block requests are prepared for the NBD protocol. Shared event classes keep the output schema identical across send and receive phases.

State and persistence: No state is stored by the header. It snapshots transient socket/request state from the NBD device, including cookies and lengths; persistence remains in the block layer request queue and userspace NBD server.

Dependencies and integration points: Depends on Linux tracepoints and NBD internal structs from the including C files. It integrates with block layer request diagnostics, NBD socket transport, and ftrace/perf.

Risks and test signals: Risks include mismatched format specifiers for cookies or sizes, tracing partial payloads as complete transfers, and assuming request pointers remain valid outside fast assignment. Test NBD connect/disconnect, read/write/flush/discard, short sends, reconnects, timeout paths, and tracing under high queue depth.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/nbd.h` completely for this pass (107 lines, 2188 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/nbd.h_research.md`.
