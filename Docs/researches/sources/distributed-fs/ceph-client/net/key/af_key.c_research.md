# sources/distributed-fs/ceph-client/net/key/af_key.c

## Purpose
Implements the kernel PF_KEYv2 socket family (`PF_KEY`, protocol `PF_KEY_V2`) and registers it as an XFRM key-manager bridge. It lets privileged userspace key managers create, update, delete, dump, and monitor IPsec security associations and policies through RFC2367/KAME-style SADB messages. It also translates XFRM kernel events back into PF_KEY notifications for registered sockets.

## Important APIs, types, and functions
- `struct netns_pfkey` stores the per-net namespace PF_KEY socket hlist and socket count.
- `struct pfkey_sock` extends `struct sock` with registration bits, promiscuous mode, dump walk state, a dump skb, and `dump_lock`.
- `pfkey_create`, `pfkey_release`, and `pfkey_ops` provide the socket-family surface. Creation requires `CAP_NET_ADMIN`, `SOCK_RAW`, and `PF_KEY_V2`.
- `parse_exthdrs`, `verify_address_len`, `verify_key_len`, and `verify_sec_ctx_len` validate SADB extension structure, duplicate extension use, lengths, families, key sizes, and security contexts.
- `pfkey_msg2xfrm_state` and `__pfkey_xfrm_state2msg` are the central bidirectional conversion routines between SADB SA messages and `struct xfrm_state`.
- `pfkey_spdadd`, `pfkey_spddelete`, `pfkey_spdget`, `pfkey_spddump`, and `pfkey_compile_policy` handle SPD policy import/export through `struct xfrm_policy`.
- `pfkey_funcs[]` dispatches SADB message types to handlers such as `SADB_GETSPI`, `SADB_ADD`, `SADB_DELETE`, `SADB_REGISTER`, `SADB_DUMP`, and SPD commands.
- `pfkeyv2_mgr` registers callbacks with XFRM: `.notify`, `.acquire`, `.compile_policy`, `.new_mapping`, `.notify_policy`, `.migrate`, and `.is_alive`.

## Control flow
`pfkey_sendmsg` copies a userspace message into an skb, validates the base `sadb_msg` with `pfkey_get_base_msg`, serializes XFRM configuration under `net->xfrm.xfrm_cfg_mutex`, broadcasts a clone to promiscuous PF_KEY sockets, parses extensions, and dispatches through `pfkey_funcs`. Errors are converted into unicast PF_KEY error replies by `pfkey_error`.

SA operations parse SADB addresses, algorithms, lifetimes, NAT-T data, mode, reqid, and security context into XFRM state, then call `xfrm_state_add`, `xfrm_state_update`, `xfrm_state_delete`, `xfrm_alloc_spi`, or lookup helpers. Policy operations build selectors from source/destination SADB addresses, parse embedded `sadb_x_ipsecrequest` templates, then call XFRM policy insert/delete/by-id/walk helpers. Dump operations store a long-lived XFRM walk in `pfkey_sock.dump` and resume from `pfkey_recvmsg` when receive buffer pressure allows.

XFRM callbacks flow in the other direction. Kernel SA and policy events call `pfkey_send_notify` or `pfkey_send_policy_notify`, which compose SADB messages and broadcast them to all or registered PF_KEY sockets. Acquire events allocate a sequence number and include algorithm proposal combinations derived from XFRM template masks.

## State and persistence behavior
State is runtime-only and namespaced. Per-net state is the PF_KEY socket hlist and socket counter. Per-socket state includes registration bitmask, promiscuous mode, and a resumable dump walker. Persistent IPsec state lives in XFRM state and policy databases, not in this file. Reference behavior depends on socket queues, RCU hlist traversal, `pfkey_mutex` for list mutation, and `dump_lock` for dump walker lifetime. `/proc/net/pfkey` is created per namespace when procfs is enabled.

## Dependencies and integration points
This file depends heavily on XFRM core (`xfrm_state_*`, `xfrm_policy_*`, algorithm descriptors, XFRM manager registration), LSM XFRM security hooks, net namespaces, procfs, sockets/skbs, RCU, and IPv4/IPv6 sockaddr support. It integrates with legacy key managers such as setkey/racoon-style PF_KEY users, while coexisting with newer netlink XFRM APIs. Module init registers `key_proto`, pernet state, the socket family, and the XFRM manager; exit unregisters them in reverse.

## Risks and edge cases
The largest risk surface is untrusted binary SADB parsing and length arithmetic. The code does substantial minimum-length, alignment, duplicate-extension, family, prefix, key, and security-context validation, but every conversion path remains sensitive to malformed extension combinations. Dump state is backpressure-sensitive and must terminate correctly on socket destruction. PF_KEY is marked deprecated and scheduled for removal in 2027, so new work should avoid expanding this interface. Migration support is conditional on `CONFIG_NET_KEY_MIGRATE`; policy expiration notifications are effectively stubbed.

## Test signals
Useful signals include PF_KEY socket creation permission/type/protocol failures, SADB error replies for malformed messages, successful `SADB_REGISTER` supported-algorithm replies, add/update/delete/get/dump behavior reflected in XFRM state, SPD add/delete/get/dump behavior, acquire/expire/flush broadcasts to registered sockets, `/proc/net/pfkey` output, namespace teardown warnings, and fuzzing of SADB extension parsing.
