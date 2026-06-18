# sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_cm.c

Implements ERDMA iWARP connection management over TCP sockets: callback interception, MPA negotiation, IWCM upcalls, connect/listen/accept/reject, endpoint lifetime, timers, and QP transition coupling.

Important functions include socket upcall save/assign/restore helpers, `erdma_socket_disassoc`, `erdma_cep_socket_assoc`, CEP reference/work helpers, `erdma_send_mpareqrep`, `erdma_recv_mpa_rr`, `erdma_proc_mpareq`, `erdma_proc_mpareply`, `erdma_cm_work_handler`, `erdma_connect`, `erdma_accept`, `erdma_reject`, `erdma_create_listen`, and `erdma_destroy_listen`.

Active connect allocates a CEP and TCP socket, associates QP and IWCM ID references, installs callbacks, binds/connects nonblocking, sends an MPA request on TCP establishment, waits for MPA reply, moves the QP to RTS, and reports connect reply. Passive listen accepts child sockets, waits for MPA request, reports connect request, and on accept moves QP to RTS, sends MPA reply, and reports established. Work items serialize with `cep->in_use`.

Persistent state includes global CM workqueue, per-device CEP list, per-CEP socket, IWCM ID, QP pointer, state, kref, work freelist, MPA buffers, timers, ORD/IRD, private data, and saved socket callbacks. Dependencies include Linux TCP sockets, workqueues, IWCM, ERDMA QP state functions, and device attributes.

Risks include callback restore races, CEP refcount imbalance, delayed-work reuse, partial MPA read handling, private-data bounds, listen parent references, QP/CEP teardown races, unsupported IPv6/MPA marker/CRC paths, and an `erdma_accept` IRD limit check that appears to compare against `max_ord`. Test signals include active/passive iWARP establishment, rejects, private data, timeouts, peer close during MPA, simultaneous destroy/close, backlog handling, IPv6 negative tests, marker/CRC rejection, and refcount/KCSAN runs.
