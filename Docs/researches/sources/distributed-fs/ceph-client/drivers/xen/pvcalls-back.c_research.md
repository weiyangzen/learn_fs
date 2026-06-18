# sources/distributed-fs/ceph-client/drivers/xen/pvcalls-back.c

## Purpose
`pvcalls-back.c` implements the Xen PV Calls backend. It exposes host networking services to a frontend over Xenbus, command rings, event channels, and grant-mapped data rings, translating frontend socket requests into kernel `AF_INET/SOCK_STREAM` sockets.

## Important APIs, types, and functions
Important structures are `struct pvcalls_fedata` for each frontend, `struct sock_mapping` for active connected sockets, `struct sockpass_mapping` for passive listening sockets, and `struct pvcalls_ioworker` for ordered I/O processing. Core functions include `backend_connect`, `backend_disconnect`, `pvcalls_back_work`, `pvcalls_back_handle_cmd`, socket command handlers for socket/connect/release/bind/listen/accept/poll, `pvcalls_new_active_socket`, data movers `pvcalls_conn_back_read` and `pvcalls_conn_back_write`, and xenbus callbacks `pvcalls_back_probe`/`pvcalls_back_changed`.

## Control flow
Probe publishes supported version, maximum ring order, and function-call mode to xenstore, then waits for a frontend. When the frontend connects, the backend reads the frontend event channel and ring grant reference, maps the command ring, binds an IRQ, and moves to `Connected`. Command-ring interrupts copy requests and dispatch them. Connect and accept create host sockets and active grant rings; bind/listen create passive mappings in a radix tree. Per-connection event-channel interrupts and socket callbacks queue ordered work that drains outbound data into `inet_sendmsg` or reads host socket data with `inet_recvmsg`, then updates shared-ring indexes and notifies the frontend. Disconnect releases all active and passive mappings.

## State and persistence
All state is in kernel memory: a global frontend list protected by a semaphore, per-frontend command ring and socket maps, per-active grant mappings, event-channel IRQs, workqueues, atomics for read/write/io/release/eoi scheduling, and saved socket callbacks. State is removed when the Xenbus device disconnects or the module exits; nothing persists across reload or reboot.

## Dependencies and integration points
The backend depends on Xenbus, grant-table mapping, Xen event channels with late EOI, ring macros from `xen/interface/io/pvcalls.h`, Linux socket internals, radix trees, workqueues, semaphores, and inet socket operations. It integrates with the PV Calls frontend protocol and the host network stack.

## Risks and test signals
Risks include shared-ring memory ordering, only-one-inflight accept/poll limitations, callback restoration races, grant mapping cleanup, frontend-provided ring order validation, event-channel EOI handling, socket lifetime under disconnect, and partial send/receive behavior. Test signals include frontend/backend loopback socket tests, nonblocking accept and poll, backend disconnect during active I/O, grant-map failure injection, malformed command IDs/lengths, full ring behavior, and host socket errors reflected in `in_error`/`out_error`.
