## sources/distributed-fs/openafs/src/libacl/netprocs.c

Purpose: `netprocs.c` converts internal ACL structures between host and network byte order with validation.

Important APIs: `acl_HtonACL` validates host-order header fields with `CheckAccessList`, converts active positive and negative entries, then converts header fields with `htonl`. `acl_NtohACL` converts header fields first with `ntohl`, validates them, then converts active entries with `ntohl`.

Control flow and validation: `CheckAccessList` rejects negative/too-large totals, mismatched positive+negative totals, and ACL sizes smaller than the minimum required for the declared active entries. The code intentionally allows `size` to exceed the minimum.

State and persistence: operates in-place on ACL structures, so callers must know whether the object is currently host or network order. The conversion supports on-disk/network persistence of ACLs.

Dependencies and integration points: depends on `acl.h`, rx/xdr byte-order environment, and ptclient includes for shared ACL type context.

Risks: in-place conversion means a failed or repeated conversion can corrupt caller expectations. Only active positive and negative entries are converted; unused slots are ignored. Callers must not call `acl_HtonACL` on already-network-order data because validation expects host-order counts.

Test signals: should be covered by round-trip tests that allocate ACLs with positive and negative entries, hton/ntoh them, and compare fields; no direct test in `acltest.c` is obvious from the source.
