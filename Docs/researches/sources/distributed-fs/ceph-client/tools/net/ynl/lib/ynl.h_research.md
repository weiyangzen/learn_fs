# sources/distributed-fs/ceph-client/tools/net/ynl/lib/ynl.h

Purpose: Public C header for consumers of generated YNL bindings and the C runtime.

Important APIs and types: Defines `enum ynl_error_code`, `struct ynl_error`, opaque-ish generated family metadata `struct ynl_family`, socket wrapper `struct ynl_sock`, and array string helper `struct ynl_string`. Exposes `ynl_sock_create()`, `ynl_sock_destroy()`, `ynl_subscribe()`, `ynl_socket_get_fd()`, `ynl_ntf_check()`, `ynl_ntf_dequeue()`, and `ynl_ntf_free()`. `ynl_dump_foreach()` and `ynl_dump_empty()` support generated dump result traversal.

Control flow: Applications create a socket with a generated `struct ynl_family`, call generated operation wrappers that use the private runtime, inspect `ys->err` on failures, iterate dump lists with `ynl_dump_foreach()`, optionally subscribe/check/dequeue notifications, and destroy the socket to close and free runtime state.

Dependencies and integration: Includes Linux generic netlink and type headers and the private header because generated code needs inline/private definitions. Generated family-specific headers expose typed request/reply structures that embed this runtime ABI.

State and persistence: `struct ynl_sock` stores runtime state including error text, file descriptor, sequence, family id, multicast group table, notification queue, and internal tx/rx buffers. All state is process-local.

Risks: The public header exposes many private fields through `struct ynl_sock`, so source compatibility is weaker than a fully opaque handle. Users must free generated dump responses and notifications according to generated APIs. `ynl_dump_empty()` relies on the sentinel pointer value from `ynl.c`.

Test signals: Compile generated users against installed headers, create/destroy sockets, inspect error propagation from `ynl_sock_create()`, iterate empty and nonempty dumps, use notification subscription/dequeue APIs, and verify ABI assumptions under both static archive and installed-header builds.
