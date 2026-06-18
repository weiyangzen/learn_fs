# sources/distributed-fs/ceph-client/include/linux/netfilter/nfnetlink_osf.h

Purpose: Declares passive OS fingerprint matching structures and lookup APIs for nfnetlink OSF.

Important APIs, types, and functions: Exports match-state enum, global `nf_osf_fingers`, `struct nf_osf_finger`, `struct nf_osf_data`, `nf_osf_match()`, and `nf_osf_find()`. Detected source surface: 38 lines; includes `uapi/linux/netfilter/nfnetlink_osf.h`; macros `_NFOSF_H`; structs `list_head`, `nf_osf_data`, `nf_osf_finger`, `nf_osf_user_finger`, `rcu_head`; enums `osf_fmatch_states`; typedefs none; function-like declarations/helpers `nf_osf_find`, `nf_osf_match`.

Control flow: OSF code compares TCP/IP header characteristics from skb data against loaded fingerprint lists, optionally fills match data, and reports whether a signature matches.

State and persistence behavior: Fingerprint lists are global loaded rule data indexed by generation/family; per-call `nf_osf_data` stores the result view.

Dependencies and integration points: Depends on the nfnetlink OSF UAPI fingerprint format and packet parsing. Integrated with netfilter matches that classify remote OSes.

Risks and test signals: Risks are stale signatures, list concurrency, overbroad wildcard matches, and malformed TCP option parsing. Test known OS fingerprints, unknown packets, IPv4/IPv6 families, and dynamic fingerprint updates.
