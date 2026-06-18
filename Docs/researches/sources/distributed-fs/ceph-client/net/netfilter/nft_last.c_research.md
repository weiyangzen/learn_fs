# sources/distributed-fs/ceph-client/net/netfilter/nft_last.c

Purpose: implements the stateful nftables `last` expression that records whether a rule was hit and the jiffies timestamp of the last hit.

Important APIs/types/functions: `struct nft_last` stores `jiffies` and `set`; `struct nft_last_priv` points to an allocated `nft_last`. `nft_last_init()` supports optional restore from `NFTA_LAST_SET` and elapsed milliseconds. `nft_last_eval()` updates the timestamp and set flag with `READ_ONCE`/`WRITE_ONCE`. `nft_last_dump()` reports whether set and elapsed milliseconds since last hit.

Control flow: init allocates state and, if userspace says the value is set, converts milliseconds to jiffies and backdates the timestamp. Eval writes current `jiffies` if changed and sets the flag. Dump detects time wrap/clock anomaly with `time_before(jiffies, last_jiffies)` and clears the state if the stored time is in the future. Clone duplicates the state into a new allocation.

State/persistence: this is explicitly `NFT_EXPR_STATEFUL`; state lives in a heap allocation rather than expression inline data. Dependencies include jiffies conversion helpers and netlink dump padding. Risks include races on non-atomic multi-field consistency, jiffies wrap/future timestamp clearing, clone preserving old timestamps, and restore values beyond representable jiffies. Test signals: first hit, repeated hit elapsed time, dump before/after hit, restore from netlink, clone behavior, future timestamp handling, and concurrent packet/dump access.
