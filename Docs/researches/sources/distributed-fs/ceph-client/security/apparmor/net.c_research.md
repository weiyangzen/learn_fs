# sources/distributed-fs/ceph-client/security/apparmor/net.c

Purpose: implements generic network-family mediation, Unix audit formatting helpers, socket-file permission bridging, and optional secmark checks.

Important APIs/functions: `aa_sfs_entry_network[]` and `aa_sfs_entry_networkv9[]` report network features. `audit_net_cb()` emits family/type/protocol, net permission masks, Unix addresses, and peer labels. `aa_do_perms()` applies modes and checks permissions. `aa_match_to_prot()` matches AF/type/protocol triples. `aa_profile_af_perm()`, `aa_af_perm()`, `aa_sk_perm()`, and `aa_sock_file_perm()` mediate create/socket operations. With secmark enabled, `apparmor_secmark_init()`, `aa_secmark_perm()`, and `apparmor_secmark_check()` map label strings to secids and enforce packet labels.

Control flow: socket hooks in `lsm.c` pass current label and socket metadata. Policy starts at network class, matches big-endian family/type/protocol, optionally uses early permissions when `AA_CONT_MATCH` is not required, then audits via `audit_net_cb()`.

State and persistence: secmark entries cache resolved secids in rulesets. Socket labels live in `aa_sk_ctx`, not here.

Dependencies and integration: depends on AF/Unix helpers, labels, policy DBs, secid conversion, audit, and apparmorfs feature reporting. Risks include family/type bounds, protocol matching differences, lazy secmark initialization in atomic contexts, wildcard secids, and Unix abstract address audit escaping. Test AF create/connect/listen/bind paths, Unix peer audit, socket file receive, secmark allow/deny/audit/wildcard, and unconfined bypass.
