# sources/distributed-fs/ceph-client/tools/net/ynl/lib/ynl.c

Purpose: Implements the C YNL runtime: socket lifecycle, generic/classic netlink request execution, response and dump parsing, extended ACK annotation, attribute validation, multicast subscription, notification queuing, and dump-list assembly.

Important APIs and state: Public entry points include `ynl_sock_create()`, `ynl_sock_destroy()`, `ynl_subscribe()`, `ynl_socket_get_fd()`, `ynl_ntf_check()`, `ynl_ntf_dequeue()`, and `ynl_ntf_free()`. Generated code uses `ynl_exec()`, `ynl_exec_dump()`, `ynl_gemsg_start_req()`, `ynl_gemsg_start_dump()`, and validation/error helpers. `struct ynl_sock` owns the raw socket, sequence, portid, family id, multicast group cache, tx/rx buffers, and queued parsed notifications.

Control flow: Socket creation allocates one object plus two fixed buffers, opens a netlink socket, enables CAP_ACK and EXT_ACK, binds, records portid and random sequence, then either uses a classic family id or queries generic-netlink family metadata. Request execution finalizes the message, sends it, receives messages until ACK or completion, routes alien async messages to notification parsing, and invokes generated parse callbacks for matching replies. Dump execution allocates one list node per decoded object and terminates the list with `YNL_LIST_END`.

Dependencies and integration: Depends on Linux netlink/genetlink headers, generated family descriptors and parse callbacks, generated policy tables, and kernel generic-netlink controller replies for dynamic families.

State and persistence: Runtime state is in memory only. Multicast groups are cached in `ys->mcast_groups`, notifications are queued as parsed allocations, and error details are reset on each new message. No disk persistence occurs.

Risks: `ynl_get_family_info_cb()` initializes `found_id` to true, so missing family ID may not be reported as intended. `ynl_ntf_parse()` does not check `calloc()` failure before dereferencing the response object. Notification parse failure calls the generated free callback, so generated free functions must tolerate partially initialized objects. Extack path reconstruction depends on request policy and offsets remaining consistent with kernel reports.

Test signals: Socket creation failure paths, missing generic family, multicast group enumeration/subscription, ACK-only requests, kernel extack with bad and missing attributes, malformed replies, interrupted dumps, alien notifications during requests, empty and multi-object dumps, notification dequeue/free, and allocation failure injection.
