# sources/distributed-fs/ceph-client/security/tomoyo/network.c

## Purpose

This file implements TOMOYO's network policy parser, auditor, and LSM-side socket permission checks for INET and UNIX sockets. It translates policy lines such as `network inet stream bind ...` and `network unix dgram send ...` into ACL objects, then checks bind, listen, connect, and datagram send operations against those ACLs.

## Important APIs, types, and functions

The local address carriers are `tomoyo_inet_addr_info`, `tomoyo_unix_addr_info`, and `tomoyo_addr_info`. Public helpers include `tomoyo_parse_ipaddr_union`, `tomoyo_print_ip`, `tomoyo_write_inet_network`, `tomoyo_write_unix_network`, `tomoyo_socket_listen_permission`, `tomoyo_socket_connect_permission`, `tomoyo_socket_bind_permission`, and `tomoyo_socket_sendmsg_permission`. Internal matchers and mergers include `tomoyo_same_inet_acl`, `tomoyo_same_unix_acl`, `tomoyo_merge_inet_acl`, `tomoyo_merge_unix_acl`, `tomoyo_check_inet_acl`, and `tomoyo_check_unix_acl`. The `tomoyo_inet2mac` and `tomoyo_unix2mac` tables map protocol/operation pairs into TOMOYO MAC indices.

## Control Flow

Policy writes parse protocol and operation tokens, build permission bitmaps, parse IP/name and port/number unions, then call `tomoyo_update_domain()` with duplicate detection and bitmap merge callbacks. Runtime hooks first reject kernel threads and unsupported families/protocols, then normalize the kernel socket operation into a `tomoyo_addr_info`. INET checks decode sockaddr family, address, and port before `tomoyo_inet_entry()` initializes a request, scans ACLs, and sends an audit/supervisor request. UNIX checks encode abstract or pathname socket names through `tomoyo_encode2()`, fill path metadata, then follow the same request/audit loop.

## State and Persistence

Persistent policy is stored in domain ACL lists updated through TOMOYO common code. This file keeps no long-lived mutable state beyond static lookup tables. Request-local state includes sockaddr-derived address pointers and temporary encoded UNIX names. Permission bitmaps are updated with `READ_ONCE()`/`WRITE_ONCE()` because readers can race with policy merge paths.

## Dependencies and Integration Points

It depends on TOMOYO common parsers, groups, request initialization, ACL traversal, audit/supervisor logging, and path encoding. It is called from LSM socket hooks registered in `tomoyo.c`. It depends on kernel networking types, `in4_pton`, `in6_pton`, sockaddr layout, and socket operation callbacks such as `getname`.

## Risks and Test Signals

Risks include sockaddr length mistakes, IPv4/IPv6 range comparison errors, raw-socket protocol-as-port handling, abstract UNIX socket encoding, unsupported protocol table entries mapping to zero and silently disabling checks, and policy merge races. Useful signals are policy parser tests for address ranges/groups and port ranges, bind/listen/connect/sendmsg tests for INET and UNIX sockets, audit replay tests, and LSM integration tests for kernel-thread bypass and unsupported family bypass.
