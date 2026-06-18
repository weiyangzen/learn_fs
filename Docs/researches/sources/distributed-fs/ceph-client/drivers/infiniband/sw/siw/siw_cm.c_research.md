# sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_cm.c

Purpose: Implements SoftiWARP iWARP connection management over kernel TCP sockets and MPA request/reply negotiation. It bridges RDMA IWCM events to socket operations, performs active connect and passive listen/accept/reject, negotiates MPA v1/v2 options, IRD/ORD, CRC, GSO, and peer-to-peer RTR mode, then hands established sockets to the QP RX/TX path.

Important APIs/types/functions: `siw_connect()`, `siw_accept()`, `siw_reject()`, `siw_create_listen()`, and `siw_destroy_listen()` are registered as iWARP CM verbs. `siw_cep_alloc()`, `siw_cep_get/put()`, `siw_cep_set_inuse/free()`, and `siw_cm_alloc_work()` manage endpoint lifetime and serialized CEP state. `siw_send_mpareqrep()`, `siw_recv_mpa_rr()`, `siw_proc_mpareq()`, and `siw_proc_mpareply()` implement MPA framing and negotiation. Socket callbacks include `siw_cm_llp_state_change()`, `siw_cm_llp_data_ready()`, `siw_cm_llp_error_report()`, and the temporary `siw_rtr_data_ready()` callback for MPAv2 RTR establishment.

Control flow: Active connect creates a TCP socket, binds/connects synchronously, associates a CEP/QP/IWCM id, sends MPA REQ, and schedules timeout work. Data-ready work reads MPA REP, validates keys/options, transitions the QP to RTS via `siw_qp_modify()`, installs QP socket callbacks, optionally sends zero-length RTR traffic, then emits `IW_CM_EVENT_CONNECT_REPLY`. Passive listen binds a TCP socket, accepts child sockets in workqueue context, waits for MPA REQ, upcalls `IW_CM_EVENT_CONNECT_REQUEST`, and later `siw_accept()` transitions the QP to RTS before sending MPA REP.

State and persistence behavior: CEP state moves through IDLE, LISTENING, CONNECTING, AWAIT_MPAREQ, RECVD_MPAREQ, AWAIT_MPAREP, RDMA_MODE, and CLOSED. State lives only in memory. CEP krefs cover socket callback ownership, IWCM references, queued work, listener-child links, and QP associations. Timers are implemented as delayed work.

Dependencies/integration: Uses Linux kernel sockets/TCP, IWCM, RDMA core, MPA/iWARP helpers, QP state functions, and module parameters from `siw_main.c`. `siw_cm_init()` creates a single-threaded CM workqueue for ordered endpoint processing.

Risks: High-risk areas are socket callback replacement/restoration, CEP/QP refcount transfer, MPA private-data length handling, timeout cancellation races, listener wildcard binding, and failure unwinding that must not double-release sockets or IWCM ids. MPA CRC/marker negotiation affects interoperability.

Test signals: Validate IPv4/IPv6 active/passive connects, MPA v1/v2 private data, CRC strict/required modes, peer reject and timeout, listener destruction with pending children, simultaneous close, first RDMA frame arriving immediately after MPA REP, lockdep with callback reclassification, and QP destroy during handshake.
