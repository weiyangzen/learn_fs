# sources/distributed-fs/ceph-client/net/ipv4/cipso_ipv4.c

## Purpose
`cipso_ipv4.c` implements CIPSO v4 label handling for NetLabel and IPv4. It manages DOI definitions, caches parsed label mappings, validates CIPSO IP options, translates between on-wire CIPSO tags and local LSM security attributes, and adds/removes CIPSO options on sockets, request sockets, and skbs.

## Important APIs, types, and functions
Global controls include `cipso_v4_cache_enabled`, `cipso_v4_cache_bucketsize`, `cipso_v4_rbm_optfmt`, and `cipso_v4_rbm_strictvalid`. DOI APIs include `cipso_v4_doi_add()`, `cipso_v4_doi_remove()`, `cipso_v4_doi_getdef()`, `cipso_v4_doi_putdef()`, `cipso_v4_doi_walk()`, and `cipso_v4_doi_free()`. Cache APIs include `cipso_v4_cache_invalidate()` and `cipso_v4_cache_add()`. Packet/socket APIs include `cipso_v4_optptr()`, `cipso_v4_validate()`, `cipso_v4_error()`, `cipso_v4_sock_setattr()`, `cipso_v4_req_setattr()`, `cipso_v4_sock_delattr()`, `cipso_v4_req_delattr()`, `cipso_v4_getattr()`, `cipso_v4_sock_getattr()`, `cipso_v4_skbuff_setattr()`, and `cipso_v4_skbuff_delattr()`.

## Control flow
Initialization allocates the fixed bucket array for the mapping cache. DOI add validates DOI/tag/type compatibility, sets a refcount, inserts the DOI under a spinlock with RCU list semantics, and audits the result. DOI removal deletes from the RCU list, drops a reference, invalidates the cache when the last reference is released, and frees with `call_rcu()`. Option generation tries the DOI's configured tags in order, maps MLS level/categories from host to network, emits one supported tag, and writes the CIPSO option header. Option parsing first checks the cache, then looks up the DOI and dispatches by tag type to reconstruct NetLabel security attributes. Validation walks all tags in an option, checks DOI and tag membership, enforces tag lengths and mapping validity, and rejects local tags unless the skb is loopback. Socket/request setters allocate new `ip_options_rcu`, install a generated option, and update TCP extended-header length/MSS for established INET connection sockets. Skb setters may grow or shrink the IPv4 header, overwrite options to guarantee label placement, update `IPCB(skb)->opt`, total length, IHL, and checksum.

## State and persistence
DOI definitions live in the RCU-protected `cipso_v4_doi_list` with refcounts and audit-visible add/remove events. The mapping cache is a fixed hash table of bucket lists protected by per-bucket spinlocks; entries reference `netlbl_lsm_cache` objects. Socket labels persist in `inet_opt` or request-sock options until explicitly removed or the socket/request is freed. Packet labels persist only in skb data.

## Dependencies and integration points
The file integrates with IPv4 options, ICMP errors, NetLabel/LSM security attributes, audit logging, RCU, spinlocks, jhash, skb copy-on-write, TCP MSS recalculation through `inet_connection_sock`, request sockets, and unaligned network-byte-order helpers. It is built when `CONFIG_NETLABEL` enables CIPSO support in the IPv4 Makefile.

## Risks and invariants
CIPSO option length is capped by the 40-byte IPv4 option space; generation must fail rather than emit truncated security labels. The implementation assumes one MAC tag per option in parsing/generation, matching supported use but limiting future multi-tag behavior. DOI lifetime and cache references must stay synchronized to avoid use-after-free; cache invalidation on DOI release is critical. `cipso_v4_skbuff_setattr()` overwrites existing options by design, which can affect packets carrying other IPv4 options. Strict validation of restricted bitmap tags is sysctl-controlled and has interoperability/security tradeoffs.

## Test signals
Tests should cover DOI add/remove/walk for pass, trans, and local mappings; invalid tag/type combinations; cache hit/miss/add/invalidate behavior; validation errors with correct offending option offsets; RBM/ENUM/RANGE/LOCAL tag generation and parsing; socket/request set/get/delete paths including TCP MSS updates; skb set/delete with header growth and shrink; loopback-only local tags; ICMP administrative-prohibited errors; and NetLabel integration with LSM secattr cache references.
