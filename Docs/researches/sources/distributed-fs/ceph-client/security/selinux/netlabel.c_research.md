<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/netlabel.c -->
# sources/distributed-fs/ceph-client/security/selinux/netlabel.c

## Purpose
Provides SELinux glue for NetLabel/CIPSO-style packet and socket labeling. It maps NetLabel security attributes to SIDs, maps SIDs back to NetLabel attributes, labels sockets and packets, enforces receive permissions, preserves labels across connection setup, and protects established socket labels from userspace option replacement.

## Important APIs, Types, and Functions
Core helpers include `selinux_netlbl_sidlookup_cached()`, `selinux_netlbl_sock_genattr()`, and `selinux_netlbl_sock_getattr()`. Public functions include `selinux_netlbl_cache_invalidate()`, `selinux_netlbl_err()`, `selinux_netlbl_sk_security_free()`, `selinux_netlbl_sk_security_reset()`, `selinux_netlbl_skbuff_getsid()`, `selinux_netlbl_skbuff_setsid()`, SCTP/TCP connection setup helpers, `selinux_netlbl_socket_post_create()`, `selinux_netlbl_sock_rcv_skb()`, `selinux_netlbl_socket_setsockopt()`, and connect helpers.

## Control Flow
Inbound skb SID lookup first checks whether NetLabel is enabled, obtains skb attributes, then calls `security_netlbl_secattr_to_sid()` and caches cacheable mappings. Outbound labeling uses a socket-cached secattr when possible, otherwise converts the requested SID and calls NetLabel skb/socket/connection setters. Socket creation labels INET/INET6 sockets immediately if destination-independent labeling is possible, otherwise marks the socket `NLBL_REQSKB` for per-packet/per-connection labeling. Receive checks map packet attributes to a SID and enforce `RECVFROM` on the receiving socket class.

## State and Persistence
Persistent per-socket state lives in `sk_security_struct`: `nlbl_secattr` and `nlbl_state` (`NLBL_UNSET`, `NLBL_LABELED`, `NLBL_REQSKB`, `NLBL_CONNLABELED`). NetLabel subsystem caches persist mapping results until invalidated. Request sockets and SCTP associations carry labels into accepted/cloned sockets.

## Dependencies and Integration Points
Depends on NetLabel APIs, IPv4/IPv6 headers, sockets, request sockets, SCTP associations, SELinux socket security, AVC permission checks, and NetLabel category import/export from the MLS bitmap layer. It integrates with socket create, connect, receive, setsockopt, SCTP association, and packet send paths.

## Risks
Socket locking is critical: reset/connect helpers assume callers hold locks in some paths and acquire them in others. `setsockopt()` must block removal of real on-the-wire labels without blocking unrelated options. AF_UNSPEC disconnect deliberately deletes connection labels and moves back to request-per-skb mode. Error signaling to NetLabel on denied labeled packets must avoid sending misleading errors for unlabeled traffic.

## Test Signals
Exercise labeled and unlabeled inbound packets, NetLabel disabled builds/runtime, socket post-create with destination-required labels, TCP accept and SCTP association/peeloff label preservation, connect/disconnect relabeling, setsockopt attempts to replace IP options/HBH options, cache invalidation, and AVC denials producing protocol-appropriate NetLabel errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/netlabel.c -->
