# sources/distributed-fs/ceph-client/net/ipv4/tcp_ulp.c

## Purpose

`tcp_ulp.c` implements registration, lookup, attachment, update, listing, and cleanup for pluggable TCP upper-layer protocols such as TLS or other TCP ULP modules. It provides the mechanism behind selecting an ULP by name and binding ULP callbacks to a TCP socket.

## Important APIs, Types, and Functions

Exported functions are `tcp_register_ulp()`, `tcp_unregister_ulp()`, `tcp_get_available_ulp()`, `tcp_update_ulp()`, `tcp_cleanup_ulp()`, and `tcp_set_ulp()`. Internal helpers are `tcp_ulp_find()`, `__tcp_ulp_find_autoload()`, and `__tcp_set_ulp()`. The key type is `struct tcp_ulp_ops`, containing `name`, `owner`, `init`, optional `release`, optional `update`, optional `clone`, and list linkage.

## Control Flow

Registration takes `tcp_ulp_list_lock`, rejects duplicate names, and appends the ops to an RCU-protected global list. Unregistration deletes from the list and waits for `synchronize_rcu()`. Lookup is a linear RCU traversal. `__tcp_ulp_find_autoload()` first searches the list, optionally requests module `tcp-ulp-$name` for capable admins, searches again, and pins the module with `try_module_get()`.

`tcp_set_ulp()` requires the caller to own the socket, resolves the ops, and delegates to `__tcp_set_ulp()`. Attachment rejects sockets that already have a ULP, clears zero-copy support on the socket, rejects LISTEN sockets for ULPs without clone support, calls the ULP `init()` callback, stores `icsk_ulp_ops`, or releases the module reference on failure. Cleanup calls the ULP release callback if present, drops the module reference, and clears the pointer.

## State and Persistence Behavior

The global ULP registry persists while modules are registered. Per-socket ULP state is represented by `inet_connection_sock::icsk_ulp_ops` plus private state created by the ULP `init()` callback. Module references persist for attached sockets until `tcp_cleanup_ulp()`.

## Dependencies and Integration Points

The file depends on Linux lists, spinlocks, RCU, module autoloading, capability checks, socket ownership conventions, and the TCP connection socket. ULP modules call the register API at module init. Socket options or protocol setup call `tcp_set_ulp()` to attach by name. Clone/update hooks integrate with accept, proto replacement, and write-space changes.

## Risks and Edge Cases

Name lookup is linear but expected to be small. Module autoload is gated by `CAP_NET_ADMIN`. Failure to pair attachment cleanup would leak module references. Clearing `SOCK_SUPPORT_ZC` changes socket capabilities when a ULP is installed. LISTEN sockets require clone support because accepted children may need ULP state inheritance. `tcp_cleanup_ulp()` intentionally skips ownership assertions because destruction occurs after normal socket use.

## Test Signals

Tests should verify duplicate registration, unregister synchronization, available-name formatting and truncation warning, autoload success/failure, attach to established sockets, attach rejection for duplicate ULPs and unsupported LISTEN sockets, init failure cleanup, update callback dispatch, release callback dispatch, and module refcount behavior.
