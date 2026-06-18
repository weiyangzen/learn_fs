# sources/distributed-fs/lustre-release/lnet/lnet/lib-me.c

## Purpose

`lib-me.c` manages LNet match entries. An ME is a portal-table entry that defines which incoming PUT/GET traffic can attach to an MD by requester ID and match/ignore bits. This file creates MEs in the correct portal match table/hash bucket, orders them according to insertion policy, and unlinks/frees an ME together with any attached MD when required.

## Important APIs, Types, and Functions

- `LNetMEAttach()` is the exported constructor. It validates the portal, chooses the match table via `lnet_mt_of_attach()`, allocates from `lnet_mes_cachep`, initializes match criteria, stores unlink policy and CPT, chooses either the ignore hash bucket or the normal hash head from `lnet_mt_match_head()`, and inserts before/after.
- `lnet_me_unlink()` removes the ME from its list, detaches any attached MD from the portal, unlinks that MD, and frees the ME slab object. It must be called with the LNet resource lock held.
- The disabled `lib_me_dump()` is a debug helper showing the ME fields and list neighbors.

## Control Flow

ME creation requires `the_lnet.ln_refcount > 0`. `LNetMEAttach()` rejects portals beyond `ln_nportals`, asks portal code for the attach match table, and rejects incompatible portal types with `-EPERM`. After allocation, it locks `mtable->mt_cpt`, fills fields from caller parameters, selects a list head based on `ignore_bits` and match hash, records the bucket offset in `me_pos`, inserts at head or tail according to `LNET_INS_BEFORE`, `LNET_INS_AFTER`, or `LNET_INS_LOCAL`, then unlocks and returns the pointer.

Unlink is synchronous from the ME perspective. It removes the list node first, then if an MD is attached it calls `lnet_ptl_detach_md()` and `lnet_md_unlink()`. The MD might only become zombie if active operations hold references. Finally the ME slab object is freed.

## State and Persistence Behavior

MEs persist in portal match-table hash lists until unlinked directly or until an attached MD created with `LNET_UNLINK` causes `lnet_md_unlink()` to unlink the ME. The ME stores portal index, match ID, match bits, ignore mask, unlink policy, MD pointer, CPT, list position, and list linkage. There is no disk persistence.

## Dependencies and Integration Points

The file depends on portal match-table helpers (`lnet_mt_of_attach()`, `lnet_mt_match_head()`), resource locking, ME slab cache accounting, and MD/portal detach functions from `lib-md.c` and portal code. `LNetMDAttach()` in `lib-md.c` consumes an empty ME and either attaches an MD to it or unlinks it on MD build failure.

## Risks and Edge Cases

- The public API returns a raw `struct lnet_me *` rather than an opaque handle in this tree, so consumers must preserve locking/lifetime discipline.
- `lnet_me_unlink()` assumes the caller holds the resource lock and that the ME is linked; misuse can corrupt match lists.
- Portal compatibility is delegated to `lnet_mt_of_attach()`, making ME correctness dependent on portal table configuration.
- `ignore_bits != 0` forces use of the ignore bucket, which may have different performance and matching behavior than exact-hash buckets.
- The interaction between `me_unlink == LNET_UNLINK` and MD auto-unlink needs coverage because ME lifetime can be triggered by MD completion rather than explicit ME operations.

## Test Signals

Tests should validate invalid portals, incompatible portal types, allocation failure, insertion order for before/after/local modes, ignore-bucket versus hashed-bucket placement, ME/MD attach then unlink behavior, auto-unlink through MD unlink policy, and resource-lock assertions under debug builds.
