# sources/distributed-fs/ceph-client/net/sctp/bind_addr.c

Purpose: manages SCTP bind address lists for endpoints and associations, including scoped copying, add/delete, raw SCTP parameter conversion, matching/conflict checks, wildcard handling, and address scope evaluation.

Important APIs/types/functions: `sctp_bind_addr_init/free/clean()` own list lifecycle. `sctp_bind_addr_copy()` and `dup()` copy with scope and IPv4/IPv6 peer-support filtering. `sctp_add_bind_addr()` and `sctp_del_bind_addr()` allocate, RCU-add, invalidate, RCU-remove, and free address entries. `sctp_bind_addrs_to_raw()` and `sctp_raw_to_bind_addrs()` serialize/parse SCTP address parameters. Match/conflict/state helpers inspect address lists. `sctp_find_unmatch_addr()`, `sctp_is_any()`, `sctp_in_scope()`, `sctp_is_ep_boundall()`, and `sctp_scope()` support ASCONF, wildcard, and policy behavior.

Control flow: lists start empty with a port. Copy operations iterate source entries, expand wildcard addresses from the global local list, and include only in-scope addresses supported by local and peer address families. Raw parsing walks address parameters, converts through address-family callbacks, deduplicates, and cleans partial results on error. Readers traverse under RCU and skip invalidated entries.

State and persistence: volatile RCU list of `sctp_sockaddr_entry` values with address, state, validity flag, and hooks. The bind port is stored separately and filled into addresses with no port. Deletion sets `valid=0` before RCU removal.

Dependencies/integration: SCTP AF dispatch, protocol-family compare callbacks, global local address list, net namespace SCTP scope policy, RCU, debug counters, endpoint matching, association address setup, cookie reconstruction, ASCONF, and socket bind conflict paths.

Risks: scope policy can silently omit addresses. Malformed raw parameters and unknown AFs must clean partial state. Single-address raw serialization intentionally returns no raw list. RCU readers must honor `valid`. IPv6-only and wildcard behavior depends on caller flags and socket family.

Test signals: wildcard expansion, IPv4/IPv6 support flags, scope policies, add/delete exact address, duplicate and malformed raw parsing, match/conflict checks, bound-all detection, single-address raw omission, ASCONF unmatch lookup, and concurrent RCU read/delete behavior.
