# sources/distributed-fs/ceph-client/net/netfilter/nft_limit.c

Purpose: implements nftables rate limiting as both expressions and named objects, supporting packet-rate and byte-rate token buckets with optional inverted matching.

Important APIs/types/functions: `struct nft_limit` contains the spinlock, last timestamp, and tokens. `struct nft_limit_priv` stores bucket parameters and flags. `nft_limit_eval()` is the shared token-bucket engine. Packet mode wraps it in `struct nft_limit_priv_pkts` with precomputed per-packet cost; byte mode computes cost from `skb->len`. Object and expression select_ops choose packet or byte variants from `NFTA_LIMIT_TYPE`.

Control flow: init parses rate/unit/burst/flags, checks multiplication/addition overflow, applies default packet burst of 5, computes maximum tokens, allocates a bucket, and initializes timestamp/tokens. Eval locks with `spin_lock_bh()`, replenishes by elapsed ns up to max, subtracts cost if possible, and returns whether to set `NFT_BREAK` considering invert. Dump emits rate, unit seconds, burst, type, and flags. Clone creates a fresh full bucket, not a copy of current token level.

State/persistence: state is mutable token count and last-time per expression/object; objects allow shared rate state between rules. Dependencies are ktime, spinlocks, netlink parsing, and nf_tables object registration. Risks include overflow in byte cost multiplication, clock jumps, clone semantics resetting bucket fullness, invert confusion, and object size inconsistency between packet and byte ops. Test signals: packet and byte limits, burst behavior, invert, zero/overflow rate or unit, concurrent packet paths, object sharing, clone/reset behavior, dump round trip, and module registration rollback.
