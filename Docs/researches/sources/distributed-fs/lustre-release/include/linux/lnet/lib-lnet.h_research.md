# sources/distributed-fs/lustre-release/include/linux/lnet/lib-lnet.h

Purpose: top-level internal LNet library header. It ties together global state (`the_lnet`), locking, handle lookup, NI/peer/message lifecycle helpers, routing, portals, fault injection, sockets, discovery, recovery, and stats.

Important APIs/functions: inline helpers cover wire-handle validation, MD exhaustion/unlinkability, cookie-to-CPT mapping, resource/net locks, NI status get/set, MD wait/free, handle-to-MD lookup, refcount helpers for peers/NIs, message and response tracker allocation, NID hashing, network hash lookup, and header conversions for nid4/nid16 wire forms. Declarations cover `lnet_configure`, NI/net allocation/free, route add/delete/get, router buffer pools, dynamic net/NI add/delete, message attach/commit/send/receive/finalize, portal/match-table operations, fault rule management, counters, LND registration, acceptor/socket helpers, ping buffer/discovery, peer table operations, health adjustment, UDSP parsing, and notifier integration.

Control flow: LNet operations typically enter through public APIs, select CPT/locks, allocate messages/MDs, resolve local NI and peer/route, commit credits, call LND send/recv, and finalize events. Discovery and monitor threads handle peer push/ping, router checks, recovery queues, response timeouts, and resend queues.

State and persistence: all state is in kernel memory: `the_lnet`, per-CPT locks/containers/counters, peer tables, routes, queues, LND registrations, ping buffers, fault rules, and module parameters. No on-disk persistence.

Dependencies/integration: includes public and internal LNet/UAPI headers, Linux networking APIs, libcfs debug/private APIs, and Lustre lock compatibility. It is the central integration point for LND implementations and LNet core source files.

Risks and test signals: concurrency and lifetime are primary risks: resource locks, peer refcounts, MD handler races, response tracker zombies, route/health updates, and dynamic config changes. ABI risks exist around nid4/nid16 conversion and netlink/ioctl structures. Test signals are init/unconfigure cycles, concurrent PUT/GET/finalize, route failover, peer discovery push/ping, dynamic NI add/delete, fault injection, response timeout/resend, and lockdep coverage for documented lock nesting.
