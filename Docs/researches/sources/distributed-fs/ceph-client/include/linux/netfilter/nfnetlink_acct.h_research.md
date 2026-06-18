# sources/distributed-fs/ceph-client/include/linux/netfilter/nfnetlink_acct.h

Purpose: Declares nfnetlink accounting object lookup, reference, update, and quota helpers.

Important APIs, types, and functions: Exports accounting use flags, opaque `struct nf_acct`, `nfnl_acct_find_get()`, `nfnl_acct_put()`, `nfnl_acct_update()`, and `nfnl_acct_overquota()`. Detected source surface: 20 lines; includes `net/net_namespace.h`, `uapi/linux/netfilter/nfnetlink_acct.h`; macros `_NFNL_ACCT_H_`; structs `nf_acct`; enums none; typedefs none; function-like declarations/helpers `nfnl_acct_overquota`, `nfnl_acct_put`, `nfnl_acct_update`.

Control flow: Rule evaluation obtains an accounting object, updates byte/packet counters from skb traffic, checks quota state, and drops the reference when done.

State and persistence behavior: Accounting objects are named, reference-counted net namespace state whose counters persist until userspace deletes or resets them.

Dependencies and integration points: Depends on nfnetlink acct UAPI and net namespace types. Integrated by xt/nft accounting matches and targets.

Risks and test signals: Risks are reference leaks, counter wrap expectations, quota race behavior, and namespace lookup confusion. Test object creation/deletion under traffic, quota crossing, and concurrent readers.
