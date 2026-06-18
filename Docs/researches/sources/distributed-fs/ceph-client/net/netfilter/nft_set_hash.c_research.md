
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_set_hash.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_set_hash.c

## Purpose

`nft_set_hash.c` implements three nftables hash set backends: fixed hash, fixed hash fast path for 32-bit keys, and resizable `rhashtable` for dynamic sets with timeouts and expression evaluation.

## Important APIs, Types, and Functions

`struct nft_rhash` wraps `rhashtable` and delayed GC work; `struct nft_rhash_elem` adds rhash node, walk node, GC sequence, and extensions. `nft_rhash_lookup()`, `nft_rhash_update()`, `nft_rhash_delete()`, and `nft_rhash_gc()` serve dynamic sets. `struct nft_hash` stores seed and bucket array for fixed sets; `nft_hash_lookup()`, `nft_hash_lookup_fast()`, and `nft_hash_insert()` serve declared-size sets. The exported set types are `nft_set_rhash_type`, `nft_set_hash_type`, and `nft_set_hash_fast_type`.

## Control Flow

Resizable lookup constructs a compare argument with key, generation mask, and timestamp; the rhashtable comparator rejects dead, expired, inactive, or mismatched elements. Dynamic update first looks up any-generation element, otherwise creates a dynset element and races insertion with `rhashtable_lookup_get_insert_key()`. GC walks the rhashtable, marks expired/dead or expression-needing-GC entries, batches them into async transactions, and reschedules itself. Fixed hash uses jhash plus reciprocal bucket scaling and RCU hlist traversal.

## State and Persistence Behavior

Resizable hash state persists in the rhashtable and delayed work item; GC sequence fields avoid double-queuing elements during unstable walks. Fixed hash state is a seeded bucket table sized from the declared element hint. Element active/dead/expired state lives in nf_tables extensions.

## Dependencies and Integration Points

Dependencies include Linux rhashtable, jhash, workqueues, nf_tables dynset helpers, set GC transaction APIs, RCU, and nft generation masks. The rhash backend supports maps, objects, timeouts, and evaluated element expressions; fixed hash supports maps and objects but not timeouts.

## Risks and Test Signals

Risks include missing NULL checks after deactivate lookup, rhashtable walk `-EAGAIN` handling, races between dynset insertion and GC, walk-list recursion during validation, and hash collision behavior. Test dynamic sets with timeouts, dynset update races, expression GC, fixed-size hash selection, 32-bit fast lookup, deletion, flush, and module teardown canceling delayed work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_set_hash.c -->
