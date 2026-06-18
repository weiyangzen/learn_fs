# sources/distributed-fs/ceph-client/net/netfilter/nft_ct_fast.c

Purpose: provides `nft_ct_get_fast_eval()`, a small exported fast evaluation helper used when mitigation/retpoline builds want direct code paths for common conntrack get keys.

Important APIs/types/functions: the single exported function reads `struct nft_ct` private data, calls `nf_ct_get()`, and writes common values to the nft register file. It supports `NFT_CT_STATE`, `NFT_CT_DIRECTION`, `NFT_CT_STATUS`, and conditionally `NFT_CT_MARK` and `NFT_CT_SECMARK`.

Control flow: state is always reported even when no conntrack exists, mapping to tracked, untracked, or invalid state bits. For all other keys, missing conntrack sets `NFT_BREAK`. Unsupported keys trigger `WARN_ON_ONCE(1)` and break evaluation. The function is compiled only when `CONFIG_NFT_CT` is enabled and is exported with `EXPORT_SYMBOL_GPL`.

State/persistence: no local state is allocated; it reads the skb's conntrack pointer and expression metadata. Dependencies are nf_tables core register helpers and nf_conntrack. Risks are divergence from `nft_ct_get_eval()` semantics, especially READ_ONCE handling for mark in the full path versus direct field reads here, and accidental selection for unsupported keys. Test signals include comparing outputs between fast and normal get ops for all supported keys, no-ct and untracked skbs, config combinations for mark/secmark, and warning assertions for invalid dispatch.
