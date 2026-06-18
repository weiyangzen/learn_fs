# sources/distributed-fs/ceph-client/security/apparmor/include/net.h

## Purpose
`net.h` defines AppArmor network permission masks, socket security context, network audit helpers, secmark structures, apparmorfs feature entries, and public network mediation functions.

## Important APIs and types
Permission aliases map send/receive to write/read and define shutdown, connect, accept, bind, listen, get/set option, network masks, filesystem-socket masks, and peer masks. `struct aa_sk_ctx` stores socket label and peer labels. `DEFINE_AUDIT_NET` and `DEFINE_AUDIT_SK` initialize network audit payloads. Public functions include `aa_do_perms`, `aa_match_to_prot`, `aa_profile_af_perm`, `aa_af_perm`, `aa_sk_perm`, `aa_sock_file_perm`, and `apparmor_secmark_check`.

## Control flow and integration
Socket LSM hooks and AF_UNIX code use these helpers to match address family, socket type, protocol, and operation against policydb DFA states. File revalidation delegates socket files to `aa_sock_file_perm` unless AF_UNIX requires special peer/path handling.

## State and persistence
Per-socket state lives in the socket LSM blob as RCU labels. `aa_secmark` entries are loaded policy state for packet/secmark mediation.

## Dependencies
It depends on net/sock, Linux paths, apparmorfs, labels, permissions, policy, and audit structures.

## Risks
Network v8/v9 compatibility and fallback behavior must match policy compiler output. `aa_sk_ctx.peer_lastupdate` is pointer-comparison-only and must not be dereferenced. AF_UNIX reuses network masks but sometimes delegates to file/path permissions.

## Test signals
Test AF_INET/AF_UNIX create/connect/bind/listen/accept/send/receive/option checks, secmark checks, socket-file mediation, and feature reporting for network_v8/network_v9.
