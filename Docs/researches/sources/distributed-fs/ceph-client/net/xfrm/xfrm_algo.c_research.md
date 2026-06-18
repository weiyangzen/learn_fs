# sources/distributed-fs/ceph-client/net/xfrm/xfrm_algo.c

Purpose: `xfrm_algo.c` is the algorithm registry and lookup layer for IPsec. It maps XFRM/PF_KEY algorithm identifiers and names to Linux crypto API transform names, default IV generators, ICV sizes, block sizes, key lengths, compression thresholds, and PF_KEY support flags.

Important data and APIs: Static descriptor tables cover AEAD (`rfc4106(gcm(aes))`, `rfc4309(ccm(aes))`, GMAC, ChaCha20-Poly1305), authentication (`hmac(md5)`, SHA variants, AES-XCBC, CMAC, SM3), encryption (`ecb(cipher_null)`, CBC ciphers, AES-CTR, SM4), and compression (`deflate`, `lzs`, `lzjh`). Exported lookups include `xfrm_aalg_get_byid()`, `xfrm_ealg_get_byid()`, `xfrm_calg_get_byid()`, name lookups for auth/encryption/compression/AEAD, index lookups for PF_KEY enumeration, `xfrm_probe_algs()`, and PF_KEY supported counters.

Control flow: `xfrm_find_algo()` scans the chosen table, optionally probes crypto availability through `crypto_has_aead()`, `crypto_has_ahash()`, `crypto_has_skcipher()`, or `crypto_has_acomp()`, caches availability in the descriptor, and returns matching descriptors. `xfrm_probe_algs()` refreshes availability for PF_KEY registration outside softirq context.

State and persistence: The only mutable state is per-descriptor `available`, cached in memory for the running kernel. No user configuration is persisted.

Dependencies and integration: XFRM user and PF_KEY code use descriptors to validate SA algorithms and advertise supported algorithms. IPComp uses compression descriptors for thresholds. ESP/AH code relies on matching crypto transform names and ICV metadata.

Risks: Descriptor mistakes can allow invalid key sizes, advertise unsupported algorithms, break IKE negotiation, or mismatch PF_KEY IDs. Availability caching is unsynchronized; current use is simple integer updates, but new concurrent mutation would need care. `BUG_ON(in_softirq())` in probing signals that callers must not run full probes from softirq.

Test signals: Use `ip xfrm state add` and PF_KEY registration with each advertised algorithm, including compat names like `aes` and `sha1`; test missing crypto modules, module autoload, AEAD ICV variants, IPComp threshold behavior, and PF_KEY algorithm counts before/after `xfrm_probe_algs()`.
