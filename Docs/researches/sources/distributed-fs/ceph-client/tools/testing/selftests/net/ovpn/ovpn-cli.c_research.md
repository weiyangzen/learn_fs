# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/ovpn-cli.c

## Purpose
`ovpn-cli.c` is the C control utility used by the OVPN selftests to create/delete OVPN interfaces, create sockets, register peers, configure keys, query state, swap keys, and listen for OVPN multicast notifications. It speaks directly to rtnetlink and the `ovpn` generic-netlink family.

## Important APIs, types, and functions
- `struct ovpn_ctx` is the central command context: command, cipher/key material, addresses, peer IDs, interface name/index, socket FDs, keepalive values, key slot/id, socket mark, symmetric/asymmetric ID mode, and peer file path.
- `struct nl_ctx` owns a libnl socket/message/callback set plus the resolved OVPN family id.
- Netlink helpers `nl_ctx_alloc_flags`, `ovpn_nl_msg_send`, `ovpn_nl_cb_error`, `ovpn_nl_cb_ack`, and `ovpn_nl_cb_finish` build and send generic-netlink requests with extended ACK reporting.
- Key helpers `ovpn_parse_key`, `ovpn_parse_cipher`, `ovpn_parse_key_direction`, and `ovpn_parse_key_slot` decode base64 key files into encrypt/decrypt keys and nonce tails.
- Socket helpers `ovpn_socket`, `ovpn_udp_socket`, `ovpn_listen`, `ovpn_accept`, and `ovpn_connect` create UDP/TCP sockets, set reuse options and optional `SO_MARK`, bind/listen/connect, and keep sockets alive for kernel peer ownership.
- Peer/key operations include `ovpn_new_peer`, `ovpn_set_peer`, `ovpn_del_peer`, `ovpn_get_peer`, `ovpn_new_key`, `ovpn_del_key`, `ovpn_get_key`, and `ovpn_swap_keys`.
- Rtnetlink helpers `ovpn_addattr`, `ovpn_nest_start`, `ovpn_rt_send`, `ovpn_new_iface`, and `ovpn_del_iface` create/delete OVPN netdevices with optional P2P/MP mode.
- Multicast helpers `ovpn_get_mcast_id`, `ovpn_listen_mcast`, and `ovpn_handle_msg` subscribe to peer notifications.
- CLI parsing is split across `ovpn_parse_cmd`, `ovpn_parse_cmd_args`, and `ovpn_run_cmd`.

## Control flow
`main` parses the command, initializes defaults (`AF_UNSPEC`, no cipher), parses command-specific arguments, then dispatches through `ovpn_run_cmd`. Interface creation uses rtnetlink. Peer and key commands use generic netlink with nested OVPN attributes. `listen` accepts TCP clients listed in a peers file and registers each accepted socket; `connect` opens a TCP socket, registers a peer, optionally installs a key, sends test data, then backgrounds itself. UDP multi-peer mode creates one socket and registers all peers from a table. Long-lived socket commands call `ovpn_waitbg`, daemonizing and pausing until signaled so the kernel can keep using their socket FDs.

## State and persistence
Persistent effects are kernel netdevices, peer entries, key slots, keepalive settings, socket ownership, and multicast subscription state while the process runs. Key material is read from a base64 file and stored only in process memory before being sent to the kernel. TCP/UDP socket commands intentionally persist as daemonized processes until killed by test cleanup.

## Dependencies and integration points
It depends on `linux/ovpn.h`, libnl generic netlink, rtnetlink, mbedTLS base64/error helpers, kselftest headers, and standard socket APIs. Shell tests call it through `ip netns exec` for every OVPN management operation. The YNL notification fixtures rely on the same kernel OVPN multicast events this tool can listen to through `listen_mcast`.

## Risks and edge cases
Argument validation is uneven: many `strtoul` calls rely on `errno` without always resetting it, and `del_key` requires a slot in practice despite usage suggesting it is optional. Backgrounding via `daemon(1,1); pause()` requires cleanup to kill helpers, otherwise sockets and peer state can linger. Peer-file parsing is fixed-width with `fscanf` and `MAX_PEERS` only enforced in TCP listen mode. The code carries compatibility shims for older libnl; changes in `linux/ovpn.h` attributes or libnl behavior can break message construction.

## Test signals
The shell tests treat zero exit codes as success and grep/observe side effects through traffic, `get_peer`, `get_key`, YNL notification diffs, and socket behavior. CLI stderr/stdout includes useful signals such as created/deleted interfaces, accepted/connected TCP sockets, peer/key dumps, multicast notification names, and detailed kernel extended ACK messages on failure.
