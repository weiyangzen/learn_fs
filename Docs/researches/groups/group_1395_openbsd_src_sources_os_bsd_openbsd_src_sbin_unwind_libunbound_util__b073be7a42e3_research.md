# Group Research: group_1395_openbsd_src_sources_os_bsd_openbsd_src_sbin_unwind_libunbound_util__b073be7a42e3

Scope verified against `Docs/research_subset_a.md`: this group is inside `sources/os/bsd/openbsd-src`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/random.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/random.c

Implements Unbound’s random-number abstraction behind `struct ub_randstate`. The file provides `ub_initstate`, `ub_random`, `ub_random_max`, and `ub_randfree`, with backend selection controlled by build configuration.

Key behavior:
- In fuzzing builds, randomness is intentionally deterministic: a counter is incremented and masked to 31 bits, with `ub_random_max` using modulo.
- With `HAVE_SSL` or `HAVE_LIBBSD`, the state is only a placeholder allocation and calls go to `arc4random()` / `arc4random_uniform()`.
- With NSS, `PK11_GenerateRandom` fills a `long int`; failures are fatal because upstream DNS query IDs and source-port choices require secure randomness.
- With Nettle, a Yarrow-256 context is seeded from `getentropy`; unseeded generation logs an error and returns masked zero-derived output.
- `ub_random_max` for NSS/Nettle uses rejection sampling against `MAX_VALUE` to avoid modulo bias.

Important constants and constraints:
- `MAX_VALUE` is `0x7fffffff`, making the public result a portable 31-bit positive range.
- `ub_random_max` assumes `x > 0` and smaller than `2^31`; that precondition is documented in the header, not enforced here.

Integration points:
- Uses `util/log.h` for allocation and entropy errors.
- Uses backend crypto APIs only under compile-time feature macros.
- The `from` seed parameter is ignored in these implementations.

<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/random.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/random.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/random.h

Declares the public random-state API used by Unbound utility code.

Key API:
- Opaque `struct ub_randstate`.
- `ub_initstate(struct ub_randstate* from)` allocates and initializes a generator state.
- `ub_random(struct ub_randstate* state)` returns a 31-bit random value.
- `ub_random_max(struct ub_randstate* state, long int x)` returns an unbiased value in `[0, x - 1]`.
- `ub_randfree(struct ub_randstate* state)` frees the state.

Contract notes:
- `x` for `ub_random_max` must be positive and less than `2^31`.
- The header describes thread-safe, repeatable per-state random use, similar to `arc4random()` but with explicit initialization.
- The `from` parameter is documented as a possible seed source, though the OpenBSD/Unbound implementation in this group ignores it for the active backends.

<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/random.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/rbtree.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/rbtree.c

Implements a generic intrusive red-black tree originally adapted from NSD. User objects embed `rbnode_type` as their first field, and comparison is supplied per tree.

Core behavior:
- `rbtree_create` allocates and initializes a tree; `rbtree_init` initializes caller-provided storage.
- Insert walks by `cmp`, rejects duplicate keys, links a red node, then rebalances with standard rotations and recoloring.
- Delete searches by key, swaps with the in-order successor when deleting a two-child node, then performs red-black delete fixup.
- Search uses `rbtree_find_less_equal`, which can return exact matches or the predecessor.
- `rbtree_first`, `rbtree_last`, `rbtree_next`, and `rbtree_previous` provide ordered traversal.
- `traverse_postorder` calls a callback after children, useful for freeing embedded-node objects without mutating the tree during traversal.

Invariants and implementation details:
- Uses a global black sentinel `rbtree_null_node`, exposed as `RBTREE_NULL`.
- The tree stores only key pointers and node links; object lifetime is owned by callers.
- The comparison callback is checked through `fptr_wlist` before use.
- Delete code changes parent/child pointers rather than swapping key/data because the rb node is embedded in caller-owned structures.

Integration points:
- Used by DNS-name/address trees and TCP connection limit storage in this group.
- Uses `log_assert` for structural assumptions during rotation and deletion.

<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/rbtree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/rbtree.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/rbtree.h

Defines the intrusive red-black tree interface.

Key structures:
- `rbnode_type`: parent/left/right links, `key`, and color byte. Must be the first member of user objects.
- `rbtree_type`: root pointer, node count, and comparison callback.
- `RBTREE_NULL`: global sentinel node, not a C null pointer.

Public operations:
- Create/init: `rbtree_create`, `rbtree_init`.
- Mutation: `rbtree_insert`, `rbtree_delete`.
- Lookup: `rbtree_search`, `rbtree_find_less_equal`.
- Traversal: `rbtree_first`, `rbtree_last`, `rbtree_next`, `rbtree_previous`, `RBTREE_FOR`, `traverse_postorder`.

Usage contract:
- Callers allocate and free contained objects.
- Duplicate keys are rejected on insert.
- `traverse_postorder` callback must not remove nodes because rebalancing would invalidate traversal assumptions.

<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/rbtree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/regional.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/regional.c

Implements a lightweight region allocator for many short-lived allocations freed as a group.

Core behavior:
- `regional_create` creates an 8192-byte default region with the `struct regional` stored inside the first chunk.
- `regional_create_custom` allows a custom initial chunk size.
- `regional_create_nochunk` sets the large-object threshold to zero, making all user allocations separate malloc blocks.
- `regional_alloc` aligns allocations to `sizeof(uint64_t)`, serves small allocations from chunks, and puts large allocations on a separate list.
- `regional_free_all` frees secondary chunks and large allocations, then reinitializes the first chunk.
- `regional_destroy` frees all allocations and the first chunk itself.
- Helper functions copy, zero, duplicate strings, log stats, and estimate total memory.

Important details:
- Overflow protection rejects near-maximum `size_t` sizes before alignment and allocation.
- Chunk links and large-object links are stored in the first pointer-sized bytes of each allocated block.
- Large-object accounting uses `total_large`; chunk accounting is derived by walking the chunk list.
- The allocator has no per-allocation free and no cleanup callback list.

Integration points:
- Used by TCP connection limit configuration storage in this group.
- Uses `util/log.h` for assertions and stats.

<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/regional.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/regional.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/regional.h

Declares and documents the region allocator.

Key structure:
- `struct regional` stores chunk list head, large-object list head, large-byte total, first chunk size, available bytes, current data pointer, large-object threshold, and padding for alignment.

Public API:
- Creation: `regional_create`, `regional_create_custom`, `regional_create_nochunk`.
- Lifetime: `regional_free_all`, `regional_destroy`.
- Allocation: `regional_alloc`, `regional_alloc_init`, `regional_alloc_zero`, `regional_strdup`.
- Diagnostics: `regional_log_stats`, `regional_get_mem`.

Design notes:
- The first block is also the `struct regional`.
- Secondary chunks and large allocations form singly linked lists.
- This is intentionally simpler than NSD’s older region allocator: no recycle bin, cleanup list, function-pointer setup, or full stats collection.

<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/regional.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/rfc_1982.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/rfc_1982.c

Implements RFC 1982 serial number arithmetic for 32-bit serials.

Functions:
- `compare_1982(a, b)` returns `0` if equal, `-1` if `a` is before `b` in serial arithmetic, and `1` otherwise.
- `subtract_1982(a, b)` returns the forward distance from `a` to `b` when `b` is known to be larger in RFC 1982 order; otherwise returns zero.

Important details:
- Uses a cutoff of `2^31` to determine wraparound ordering.
- Avoids signed subtraction and `a - b < 0` style comparisons, which are unsafe for unsigned serial arithmetic and compiler optimization.
- The ambiguous half-range case follows the file’s comparison branches and falls into the final `else`/wrong-case behavior.

Integration points:
- Useful for DNS SOA serial comparisons and other wraparound counters.

<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/rfc_1982.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/rfc_1982.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/rfc_1982.h

Declares the RFC 1982 serial arithmetic helpers.

Public API:
- `compare_1982(uint32_t a, uint32_t b)`.
- `subtract_1982(uint32_t a, uint32_t b)`.

Contract:
- Operates on 32-bit unsigned serial values.
- `subtract_1982` is meaningful when the caller already knows `b` is larger than `a` in serial-number order.
- Documentation emphasizes avoiding compiler-sensitive signed-difference logic.

<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/rfc_1982.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/rtt.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/rtt.c

Implements UDP round-trip-time estimation for resend timeouts.

Core behavior:
- Global `RTT_MIN_TIMEOUT` defaults to 50 ms and `RTT_MAX_TIMEOUT` defaults to 120000 ms; comments state configuration may overwrite them.
- `rtt_init` starts `srtt` at zero, initializes `rttvar` from `UNKNOWN_SERVER_NICENESS / 4`, and computes the initial RTO.
- `calc_rto` computes `srtt + 4 * rttvar`, clamped to configured min/max.
- `rtt_update` uses the standard smoothed estimator: `srtt += delta / 8`, `rttvar += (abs(delta) - rttvar) / 4`.
- `rtt_lost` performs exponential backoff using the original timeout to prevent many simultaneous queries from multiplying the cached timeout repeatedly.
- `rtt_unclamped` returns the current timeout after fallback/backoff, otherwise returns raw `srtt + 4 * rttvar`.
- `rtt_notimeout` returns the clamped calculated RTO without timeout-backoff effects.

Integration points:
- Includes `iterator/iterator.h` for `UNKNOWN_SERVER_NICENESS`.
- Used by resolver infrastructure for server selection and retry timing.

<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/rtt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/rtt.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/rtt.h

Defines the RTT estimator state and API.

Key structure:
- `struct rtt_info`: `srtt`, `rttvar`, and current `rto`, all in milliseconds.

Public API:
- `rtt_init`, `rtt_timeout`, `rtt_unclamped`, `rtt_notimeout`, `rtt_update`, `rtt_lost`.
- Extern globals `RTT_MIN_TIMEOUT` and `RTT_MAX_TIMEOUT`.

Usage contract:
- Callers allocate the `struct rtt_info`.
- Valid responses call `rtt_update`.
- Timeout observations call `rtt_lost` with the original timeout value used for that query.

<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/rtt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/siphash.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/siphash.c

Contains the SipHash reference implementation, lightly adapted for Unbound.

Core behavior:
- Implements default SipHash-2-4 with `cROUNDS = 2` and `dROUNDS = 4`.
- `siphash(in, inlen, k, out, outlen)` accepts a 16-byte key and writes either 8 or 16 output bytes.
- Input is processed in 8-byte little-endian words, with tail bytes packed into the final block.
- For 16-byte output, it applies the SipHash-128 domain-separation steps and emits a second 64-bit word.

Adaptations:
- Uses `config.h` rather than standalone standard includes.
- Includes `util/siphash.h` to avoid missing-prototype warnings.
- The assert on `outlen` is inside the function for C90 compatibility.
- Fallthrough annotations use `ATTR_FALLTHROUGH`.

Notes:
- This is a keyed hash, suitable for hash-table hardening and short authenticator-style uses, but the file exposes only the one-shot API.
- Debug tracing is compiled only with `DEBUG`.

<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/siphash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/siphash.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/siphash.h

Declares the one-shot SipHash function.

Public API:
- `int siphash(const uint8_t *in, size_t inlen, const uint8_t *k, uint8_t *out, size_t outlen);`

Contract:
- `k` must point to a 16-byte key.
- `outlen` must be either 8 or 16 bytes; the implementation asserts this.
- Returns zero on success.

<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/siphash.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/Makefile.inc -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/Makefile.inc

OpenBSD make include for the `libunbound/util/storage` subdirectory.

Build behavior:
- Adds `.PATH` for `${.CURDIR}/libunbound/util/storage`.
- Adds storage utility sources to `SRCS`: `dnstree.c`, `lookup3.c`, `lruhash.c`, and `slabhash.c`.

Role:
- Wires the storage support modules into the OpenBSD `sbin/unwind` build of libunbound.

<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/dnstree.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/dnstree.c

Implements DNS-oriented wrappers around the generic red-black tree for domain names and address/netblock lookup.

Name tree behavior:
- `name_tree_compare` sorts first by DNS class, then by `dname_lab_cmp`.
- `name_tree_insert` initializes a caller-owned node and inserts it.
- `name_tree_init_parents` walks ordered nodes and sets closest-encloser parent pointers using label-match counts.
- `name_tree_find` performs exact lookup.
- `name_tree_lookup` returns the closest enclosing configured name for a queried wire-format name/class.
- `name_tree_next_root` finds root-name entries by class, using recursive advancement to skip classes without root entries.

Address tree behavior:
- `addr_tree_compare` sorts by address, then netblock size.
- `addr_tree_addrport_compare` sorts using `sockaddr_cmp_scopeid`, effectively address/port/scope-oriented comparison.
- `addr_tree_insert` copies a socket address into the node and inserts it.
- `addr_tree_init_parents_node` and `addr_tree_init_parents` compute enclosing-subnet parent links by walking ordered nodes and using common-prefix lengths.
- `addr_tree_lookup` returns the closest enclosing netblock for a socket address.
- `addr_tree_find` performs exact netblock lookup.

Integration points:
- Depends on `util/data/dname.h` for DNS name comparison/root checks.
- Depends on `util/net_help.h` for sockaddr comparison, IP-family checks, and prefix matching.
- Used by TCP connection limit storage in this group.

<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/dnstree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/dnstree.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/dnstree.h

Defines DNS-name and address tree node types plus lookup APIs.

Key structures:
- `struct name_tree_node`: embedded `rbnode_type`, closest-encloser parent, wire-format name, length, label count, and DNS class.
- `struct addr_tree_node`: embedded `rbnode_type`, enclosing-netblock parent, `sockaddr_storage`, address length, and prefix length.

Public API:
- Name tree: `name_tree_init`, `name_tree_insert`, `name_tree_init_parents`, `name_tree_find`, `name_tree_lookup`, `name_tree_next_root`, `name_tree_compare`.
- Address tree: `addr_tree_init`, `addr_tree_addrport_init`, `addr_tree_insert`, `addr_tree_init_parents`, `addr_tree_init_parents_node`, `addr_tree_lookup`, `addr_tree_find`, `addr_tree_compare`, `addr_tree_addrport_compare`.

Usage contract:
- Nodes are caller allocated and typically embedded in larger records.
- Parent pointers must be initialized after insertions and before closest-encloser lookups.
- Tree objects are plain `rbtree_type` instances initialized with the appropriate comparator.

<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/dnstree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/lookup3.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/lookup3.c

Contains Bob Jenkins’ public-domain lookup3 hash, adapted for Unbound.

Active public behavior:
- `hash_set_raninit(v)` sets a process-global randomized initial value used by later hashes.
- `hashword(k, length, initval)` hashes arrays of `uint32_t`.
- `hashlittle(key, length, initval)` hashes arbitrary byte arrays to a 32-bit value.
- Hash state initialization incorporates `raninit`, input length, and caller-provided `initval`.

Implementation details:
- Endianness is determined via configured target endianness when available, otherwise via platform macros and system headers.
- `mix` and `final` macros perform Jenkins’ reversible mixing/final avalanche operations.
- `ARRAY_CLEAN_ACCESS` is always enabled here, so tail reads avoid intentional overread/mask tricks; this favors auditability and valgrind cleanliness.
- `hashlittle` has optimized paths for little-endian 32-bit aligned input, little-endian 16-bit aligned input, and byte-by-byte fallback.
- `hashbig` is present inside `#if 0` and is not compiled.
- `hashword2`, `hashlittle2`, and test drivers are compiled only under `SELF_TEST`.

Security and usage notes:
- The comments explicitly say lookup3 is not cryptographic.
- The randomized `raninit` is Unbound-specific hardening against predictable hash placement.
- The global seed should be set before threads and before hashing persistent structures, because changing it changes all subsequent hash results.

<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/lookup3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/lookup3.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/lookup3.h

Declares the lookup3 hashing API.

Public API:
- `hashword(const uint32_t *k, size_t length, uint32_t initval)`.
- `hashlittle(const void *k, size_t length, uint32_t initval)`.
- `hash_set_raninit(uint32_t v)`.

Contract:
- `hashword` length is measured in 32-bit words.
- `hashlittle` length is measured in bytes.
- `initval` supports chained or caller-seeded hashing.
- `hash_set_raninit` must be called before threaded use and before hashing stored data whose lookup depends on stable hash values.

<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/lookup3.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/lruhash.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/lruhash.c

Implements a locked hash table with overflow chains, an LRU list, memory accounting, resizing, and eviction.

Core lifecycle:
- `lruhash_create` allocates the table, initializes the table lock, callback functions, bin array, and per-bin locks.
- `lruhash_delete` destroys locks and deletes entries through callback functions.
- `lruhash_clear` removes all entries while respecting bin and entry locks.

Lookup and mutation:
- `lruhash_insert` inserts a new entry or updates an existing entry’s data. Existing-key updates delete the new key and old data, then store the new data.
- `lruhash_lookup` locks the table and bin, finds the entry, touches it to the front of the LRU list, then obtains a read or write lock on the entry before releasing the bin.
- `lruhash_remove` unlinks an entry from bin and LRU structures, optionally marks it pending deletion, and calls delete callbacks after releasing table/bin locks.
- `lruhash_insert_or_retrieve` is getdns-specific: it returns a write-locked existing entry if present, otherwise inserts and write-locks the supplied entry.

Eviction and growth:
- `reclaim_space` removes LRU-end entries until memory is within `space_max`, keeping the MRU entry so the table is not emptied by reclaim.
- Reclaimed entries are put on a temporary list and freed outside the main critical section.
- `table_grow` doubles the bin array when `num >= size`, moves overflow chains using the new mask, then destroys old bin locks.
- `lruhash_update_space_used` and `lruhash_update_space_max` adjust accounting and may trigger eviction.

Diagnostics and traversal:
- `lruhash_status` logs entry count, memory use, array size, and optional per-bin collision stats.
- `lruhash_get_mem` includes table, bins, entry-accounted memory, and lock overhead.
- `lruhash_traverse` locks the table and each bin, locks each entry, invokes a callback, then unlocks.

Important invariants:
- Table lock protects lookup array, LRU list, size, memory counters, and growth.
- Bin locks protect overflow chains.
- Entry rwlocks protect entry contents, not hash/key/LRU/overflow links.
- Function pointers are checked with `fptr_wlist` before callback use.

<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/lruhash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/lruhash.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/lruhash.h

Defines the LRU hash table data structures, callbacks, and API.

Key structures:
- `struct lruhash`: table lock, callback functions, bin array, LRU head/tail, entry count, memory counters, and collision stats.
- `struct lruhash_bin`: per-bin quick lock and overflow-chain head.
- `struct lruhash_entry`: entry rwlock, overflow link, LRU links, hash, key, and data.

Callback types:
- `lruhash_sizefunc_type`, `lruhash_compfunc_type`, `lruhash_delkeyfunc_type`, `lruhash_deldatafunc_type`, `lruhash_markdelfunc_type`.

Public API:
- Lifecycle: `lruhash_create`, `lruhash_delete`, `lruhash_clear`.
- Core operations: `lruhash_insert`, `lruhash_lookup`, `lruhash_remove`.
- LRU/memory control: `lru_touch`, `lru_demote`, `lruhash_update_space_used`, `lruhash_update_space_max`.
- Diagnostics/traversal: `lruhash_status`, `lruhash_get_mem`, `lruhash_traverse`.
- getdns-only helper: `lruhash_insert_or_retrieve`.
- Unit-test/internal helpers are exposed for bins, growth, reclaim, and LRU manipulation.

Concurrency contract:
- The header gives a detailed lock ordering strategy: table lock, bin lock, then entry lock.
- Callers must release entry locks after lookup.
- Callers must not hold locks on multiple hash entries acquired through separate normal lookups.

<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/lruhash.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/slabhash.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/slabhash.c

Implements a slabbed hash table: an array of independent `lruhash` tables selected by high bits of the hash.

Core behavior:
- `slabhash_create` allocates a `struct slabhash`, checks that slab count is a power of two, computes a high-bit mask/shift, and creates each underlying `lruhash` with `maxmem / numtables`.
- `slab_idx` selects a slab using `(hash & mask) >> shift`.
- Insert, lookup, remove, memory-update, and get-table operations dispatch to the selected `lruhash`.
- Delete and clear iterate all slabs.
- Status, size checks, memory accounting, traversal, entry counting, collision stats, and max-size adjustment aggregate or iterate across slabs.

Design intent:
- Unlike `lruhash`, the slab table itself does not grow.
- Multiple smaller `lruhash` tables provide multiple locks and multiple LRU lists, reducing contention.
- The slab structure is immutable after creation, so it needs no own lock for dispatch.

Test helpers:
- Defines simple test key/data structures and size/compare/delete functions to support slabhash unit tests without separate linkage to callback code.

<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/slabhash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/slabhash.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/slabhash.h

Defines the slabbed hash table interface.

Key structure:
- `struct slabhash`: number of slabs, high-bit mask, shift count, and array of `struct lruhash*`.

Public API:
- Lifecycle: `slabhash_create`, `slabhash_delete`, `slabhash_clear`.
- Dispatch operations: `slabhash_insert`, `slabhash_lookup`, `slabhash_remove`, `slabhash_update_space_used`, `slabhash_gettable`.
- Diagnostics and sizing: `slabhash_status`, `slabhash_get_size`, `slabhash_is_size`, `slabhash_get_mem`, `count_slabhash_entries`, `get_slabhash_stats`, `slabhash_adjust_size`.
- Traversal/control: `slabhash_setmarkdel`, `slabhash_traverse`.

Constants and test types:
- `HASH_DEFAULT_SLABS` defaults to 4.
- Test-only structures `slabhash_testkey` and `slabhash_testdata` are declared with helper callback prototypes.

Usage notes:
- Slab count must be a power of two.
- Each slab receives an equal share of the configured maximum memory.

<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/slabhash.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/tcp_conn_limit.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/tcp_conn_limit.c

Implements storage and accounting for per-client TCP connection limits.

Core lifecycle:
- `tcl_list_create` allocates `struct tcl_list` and a regional allocator.
- `tcl_list_delete` traverses the address tree postorder, destroys each node lock, destroys the region, and frees the list.

Configuration loading:
- `tcl_list_apply_cfg` clears the region, initializes the address tree, reads `cfg->tcp_connection_limits`, and initializes parent pointers for closest-netblock lookup.
- `tcl_list_str_cfg` parses a netblock string with `netblockstrtoaddr`, parses the limit with `atoi`, then inserts a node.
- Duplicate address entries are logged at query verbosity if requested.

Runtime accounting:
- `tcl_addr_lookup` returns the closest matching `tcl_addr` netblock node for a client socket address.
- `tcl_new_connection` locks the matched node and increments `count` only if below `limit`; returns false when the limit is reached.
- `tcl_close_connection` decrements the count with an assertion that it was positive.
- If no matching limit node is supplied, new/close operations are effectively allowed/no-op.

Other utilities:
- `tcl_list_get_mem` reports structure plus regional memory.
- `tcl_list_swap_tree` swaps tree and region pointers between two lists; callers are responsible for managing node locks.

Integration points:
- Uses regional allocation for config-owned `tcl_addr` nodes.
- Uses `addr_tree_*` from `dnstree.c` for closest netblock lookup.
- Depends on config parsing, localzone port constants, and networking helpers.

<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/tcp_conn_limit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/tcp_conn_limit.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/tcp_conn_limit.h

Defines the TCP connection limit data structures and API.

Key structures:
- `struct tcl_list`: regional allocator plus address `rbtree_type`.
- `struct tcl_addr`: address tree node, quick lock, configured limit, and current count.

Public API:
- `tcl_list_create`, `tcl_list_delete`.
- `tcl_list_apply_cfg`.
- `tcl_new_connection`, `tcl_close_connection`.
- `tcl_addr_lookup`.
- `tcl_list_get_mem`.
- `tcl_list_swap_tree`.

Usage contract:
- A caller first looks up the client address, then passes the returned `tcl_addr*` to connection open/close accounting.
- Passing NULL to `tcl_new_connection` permits the connection.
- Node locks protect `limit`/`count` mutation.

<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/tcp_conn_limit.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/timehist.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/timehist.c

Implements an exponential-bucket histogram for `struct timeval` values.

Core behavior:
- `timehist_setup` allocates a histogram with `NUM_BUCKETS_HIST` buckets and initializes bucket ranges.
- Bucket setup starts at zero and doubles the upper bound each bucket; the first bucket is `[0, 1 usec]`, then exponential growth.
- `timehist_insert` increments the first bucket whose upper bound is greater than or equal to the inserted value, falling back to the final bucket.
- `timehist_clear` zeros counts.
- `timehist_print` prints nonempty buckets to stdout.
- `timehist_log` logs quartiles and nonempty bucket ranges.
- `timehist_quartile` estimates a percentile by locating the bucket containing the requested item position and linearly interpolating within that bucket.
- `timehist_export` and `timehist_import` copy counts to/from a `long long` array.

Important details:
- Quartile estimation returns zero if fewer than four observations are present.
- Uses `timeval_smaller` from `timeval_func.c`.
- Not internally locked; callers must synchronize if shared.

<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/timehist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/timehist.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/timehist.h

Declares the time histogram API.

Key constants and structures:
- `NUM_BUCKETS_HIST` is 40.
- `struct th_buck`: lower bound, upper bound, and count.
- `struct timehist`: bucket count and bucket array pointer.

Public API:
- Lifecycle: `timehist_setup`, `timehist_delete`, `timehist_clear`.
- Data operations: `timehist_insert`, `timehist_quartile`.
- Output: `timehist_print`, `timehist_log`.
- Serialization: `timehist_export`, `timehist_import`.

Usage notes:
- Values are `struct timeval`.
- Percentile argument should be between 0 and 1; the implementation does not enforce this beyond its search behavior.

<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/timehist.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/timeval_func.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/timeval_func.c

Implements helper functions for `struct timeval`.

Functions:
- `timeval_subtract(d, end, start)` computes `end - start`, borrowing from seconds if needed.
- `timeval_add(d, add)` adds another timeval into `d`, normalizing microseconds above one million.
- `timeval_divide(avg, sum, d)` divides a timeval sum by an integer denominator, carrying leftover seconds into microseconds.
- `timeval_smaller(x, y)` returns true if `x <= y` by seconds and microseconds.

Important details:
- Division by nonpositive denominator returns zero.
- Negative computed average fields are clamped to zero.
- `timeval_smaller` treats equality as smaller/true, matching histogram upper-bound insertion behavior.
- `S_SPLINT_S` guards suppress bodies for static-analysis mode.

<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/timeval_func.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/timeval_func.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/timeval_func.h

Declares timeval helper functions and portability macros.

Definitions:
- Includes `<sys/time.h>`.
- Defines `timeval_isset(tv)` if absent.
- Defines `timeval_clear(tv)` if absent.

Public API:
- `timeval_subtract`.
- `timeval_add`.
- `timeval_divide`.
- `timeval_smaller`.

Usage note:
- No include guard is present in this header, but contents are simple declarations/macros.

<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/timeval_func.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/tube.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/tube.c

Implements Unbound’s “tube” pipe/message service with separate Unix and Winsock implementations.

Unix implementation:
- `tube_create` allocates a tube, creates a `socketpair(AF_UNIX, SOCK_STREAM)` or falls back to `pipe`, stores read/write fds, and sets both nonblocking.
- Messages are framed as a 32-bit length followed by payload bytes.
- `tube_write_msg` can test an initial nonblocking write, then switches the fd to blocking to finish length and payload, restoring nonblocking before return.
- `tube_read_msg` similarly reads the length and payload, rejects messages of at least `65536 * 2`, allocates the payload, and restores nonblocking.
- `tube_poll`, `tube_wait`, and `tube_wait_timeout` use `poll`.
- Background reading uses a raw comm point and `tube_handle_listen`, which incrementally reads length and payload, then invokes the configured callback.
- Background writing uses `tube_queue_item` plus `tube_handle_write`, maintaining a FIFO list and partial-write offset.
- Delete removes event registrations, closes fds, frees partial command buffers and queued results.

Windows implementation:
- Uses an in-memory FIFO protected by `lock_basic_type` and signaled by a `WSAEVENT`.
- `tube_write_msg` duplicates the payload and queues it.
- `tube_read_msg` polls or waits on the event, pops one queued item, and resets the event when the queue becomes empty.
- Background listen registers the WSA event with the Unbound event layer; `tube_handle_signal` drains queued messages and invokes callbacks.
- There is no meaningful read fd on Windows; `tube_read_fd` returns `-1`.

Important integration points:
- Uses `util/netevent.h` comm points for async operation.
- Uses `util/ub_event.h` for Winsock event registration.
- Callback function pointers are checked through `fptr_wlist`.
- Direct read/write APIs should not be mixed with background listen/write APIs on the same tube.

<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/tube.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/tube.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/tube.h

Defines the tube message-pipe abstraction.

Key types:
- `tube_callback_type`: callback receiving tube, message pointer, length, error code, and user argument.
- `struct tube`: platform-specific state.
  - Unix: read/write fds, background comm points, read state, write queue.
  - Winsock: callback state, WSA event, optional event wrapper, lock, and FIFO queue.
- `struct tube_res_list`: queued message node with buffer and length.

Public API:
- Lifecycle and fd control: `tube_create`, `tube_delete`, `tube_close_read`, `tube_close_write`, `tube_read_fd`.
- Synchronous framed I/O: `tube_write_msg`, `tube_read_msg`.
- Readiness: `tube_poll`, `tube_wait`, `tube_wait_timeout`.
- Async setup: `tube_setup_bg_listen`, `tube_remove_bg_listen`, `tube_setup_bg_write`, `tube_remove_bg_write`, `tube_queue_item`.
- Callback entry points for function-pointer whitelisting: `tube_handle_listen`, `tube_handle_write`, `tube_handle_signal`.

Usage notes:
- Queued message buffers are freed by the tube machinery after writing or removal.
- The header explicitly warns not to mix direct read/write style with background style for the same direction.

<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/tube.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/ub_event.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/ub_event.h

Declares Unbound’s event abstraction layer.

Key concepts:
- Opaque `struct ub_event_base` and `struct ub_event`.
- Event bit constants mirror libevent/libev concepts: timeout, read, write, signal, persist.
- The API hides whether the backend is mini-event, libevent, libev, or Winsock.

Public API:
- Version/system info: `ub_event_get_version`, `ub_get_event_sys`.
- Base management: `ub_default_event_base`, `ub_libevent_event_base`, `ub_libevent_get_event_base`, `ub_event_base_free`, `ub_event_base_dispatch`, `ub_event_base_loopexit`.
- Event creation: `ub_event_new`, `ub_signal_new`, `ub_winsock_register_wsaevent`.
- Event mutation/lifetime: `ub_event_add_bits`, `ub_event_del_bits`, `ub_event_set_fd`, `ub_event_free`, `ub_event_add`, `ub_event_del`.
- Specialized activation: `ub_timer_add`, `ub_timer_del`, `ub_signal_add`, `ub_signal_del`.
- Winsock helpers: `ub_winsock_unregister_wsaevent`, `ub_winsock_tcp_wouldblock`.
- Time helper: `ub_comm_base_now`.

Usage role:
- This is the interface consumed by networking and tube code so they do not directly depend on a specific event backend.

<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/ub_event.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/ub_event_pluggable.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/ub_event_pluggable.c

Implements the pluggable event abstraction declared in `ub_event.h`.

Backend wrapping:
- Defines private `struct my_event_base` containing `struct ub_event_base` plus native `struct event_base*`.
- Defines private `struct my_event` containing `struct ub_event` plus native `struct event`.
- Uses vtables from `libunbound/unbound-event.h`; public functions validate `UB_EVENT_MAGIC` and dispatch through the vtable.
- Default vtables wrap libevent/libev/mini-event operations.

Event-bit handling:
- If Unbound event bits differ from native backend bits, macros translate between them.
- Callback wrapper functions are generated for known internal callbacks so native events can call back with translated bit values.
- `NATIVE_BITS_CB` maps known callback addresses to wrappers; unknown callbacks become NULL in that translation mode.

Base creation:
- `ub_default_event_base` creates a mini-event base when `USE_MINI_EVENT` is set.
- Otherwise it creates libev or libevent bases depending on configured APIs.
- `ub_libevent_event_base` wraps an externally supplied libevent base when not using mini-event.
- `ub_libevent_get_event_base` exposes the native base only for the default wrapper vtable and non-mini-event builds.

Event creation and operations:
- `my_event_new` uses `event_set` and `event_base_set`.
- `my_signal_new` uses `signal_set`.
- Timer add reinitializes the event as timeout-only and uses `evtimer_add`.
- Add/delete/free/set-fd/bit operations manipulate the underlying `struct event`.
- Winsock registration only works for `USE_MINI_EVENT && USE_WINSOCK`; otherwise those helpers are no-ops or return NULL.

System reporting:
- `ub_get_event_sys` reports backend name/system/method for Winsock, mini-event, libev, or libevent.
- libev backend method can be mapped to strings like select, poll, epoll, kqueue, devpoll, or evport when backend constants are available.

Time update:
- `ub_comm_base_now` updates the `comm_base` cached `time_t` and `timeval` using `gettimeofday`, except when mini-event owns time updates.

Safety/integration:
- Public wrappers check magic values and use `fptr_wlist` assertions to ensure default vtable entries match expected local functions.
- This file is central glue between Unbound networking code, libunbound pluggable event users, and platform-specific event backends.

<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/ub_event_pluggable.c -->