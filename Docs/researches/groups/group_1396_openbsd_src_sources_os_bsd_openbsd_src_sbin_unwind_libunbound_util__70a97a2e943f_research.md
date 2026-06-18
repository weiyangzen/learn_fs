# Group Research: group_1396_openbsd_src_sources_os_bsd_openbsd_src_sbin_unwind_libunbound_util__70a97a2e943f

Scope confirmed against `Docs/research_subset_a.md`: all listed files are under `sources/os/bsd/openbsd-src`, which is included in subset A. I read every listed source file completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/winsock_event.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/winsock_event.c

## Purpose
Implements Unbound's Windows-specific event loop adapter when `USE_WINSOCK` is enabled. It provides a small libevent-like API over WinSock `WSAWaitForMultipleEvents`, plus special handling for TCP readiness because Windows socket events do not behave like Unix level-triggered readiness in practice.

When `USE_WINSOCK` is not defined, the file only exports `winsock_unused_symbol` to keep archive tools happy.

## Main Responsibilities
- Creates and destroys `struct event_base` with fixed WinSock wait capacity, timeout rbtree, signal table, and shared time pointers.
- Implements event registration, deletion, dispatch, and loop exit functions compatible with Unbound's event abstraction.
- Converts WinSock network events (`FD_READ`, `FD_WRITE`, `FD_CONNECT`, `FD_ACCEPT`, `FD_CLOSE`) into Unbound event bits (`EV_READ`, `EV_WRITE`, `EV_TIMEOUT`).
- Maintains "sticky" TCP readiness state until callers report `WSAEWOULDBLOCK` through `winsock_tcp_wouldblock`.
- Supports timer-only events through an rbtree sorted by absolute timeout.
- Supports both C signal callbacks and user-provided `WSAEVENT` callbacks.

## Key Functions
- `mini_ev_cmp`: orders events in the timeout rbtree by `ev_timeout`, then pointer address for uniqueness.
- `event_init`: allocates the event base, initializes time, event arrays, rbtree, and signal table.
- `handle_timeouts`: expires due timeout events and calculates the next wait interval.
- `handle_select`: builds the WinSock wait array, waits or sleeps, enumerates socket events, runs callbacks, and updates sticky TCP state.
- `event_base_dispatch`: main loop that alternates timeout processing and WinSock waits until `need_to_exit`.
- `event_add`: registers socket/time events, creates `WSAEVENT`s, calls `WSAEventSelect`, detects TCP/listening sockets, and inserts timeout nodes.
- `event_del`: removes timeout/socket events, compacts the event array, disables `WSAEventSelect`, closes event handles, and clears active wait slots.
- `signal_add` / `signal_del`: simple process-signal callback registration using a single global `signal_base`.
- `winsock_register_wsaevent` / `winsock_unregister_wsaevent`: lets callers add externally owned `WSAEVENT` objects to the same wait loop.

## Control Flow
The dispatch loop first updates wall-clock time, runs all expired timeout callbacks, then waits on currently registered `WSAEVENT`s. If TCP sticky events exist, the wait timeout becomes zero so callbacks are retried until the socket operation reports would-block. During callback processing, `waitfor[]` entries can be zeroed by deletion to avoid invoking callbacks for events removed during another callback.

## Dependencies and Integration
Depends on `util/winsock_event.h`, `util/rbtree`, Unbound logging/assertion helpers, WinSock APIs, and `util/fptr_wlist.h` callback whitelist checks. It is an internal compatibility layer for Unbound code expecting libevent-style functions.

## Notable Constraints and Risks
- WinSock wait limit is fixed at `WSK_MAX_ITEMS` / 64.
- `signal_base` is global, so signal handling is not multi-base safe.
- The code assumes callers report would-block for TCP streams; otherwise sticky readiness may continue to fire.
- `event_base_free` frees the timeout tree container but expects events themselves to be managed elsewhere.
- `event_add` logs WinSock errors but does not always abort registration after failed `WSACreateEvent` or `WSAEventSelect`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/winsock_event.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/winsock_event.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/winsock_event.h

## Purpose
Declares Unbound's Windows WinSock event API and maps common libevent symbols onto the local `winsockevent_*` implementation when `USE_WINSOCK` is enabled.

## Main Contents
- Defines libevent-compatible event flags: `EV_TIMEOUT`, `EV_READ`, `EV_WRITE`, `EV_SIGNAL`, and `EV_PERSIST`.
- Renames event APIs such as `event_init`, `event_add`, `event_del`, and `signal_add` to WinSock-specific names to avoid symbol collision.
- Defines fixed limits: `MAX_SIG` for signals and `WSK_MAX_ITEMS` for waitable WinSock objects.
- Declares `struct event_base`, which stores timeout tree, active item array, signal table, time pointers, TCP sticky counters, and current wait handles.
- Declares `struct event`, which stores public event metadata plus WinSock-private fields such as array index, `WSAEVENT`, TCP sticky state, signal-event flag, and callback processing marker.

## Public API
- Event base lifecycle: `event_init`, `event_base_dispatch`, `event_base_loopexit`, `event_base_free`.
- Event setup and registration: `event_set`, `event_base_set`, `event_add`, `event_del`.
- Timer aliases: `evtimer_add`, `evtimer_del`.
- Signal support: `signal_set`, `signal_add`, `signal_del`.
- WinSock-specific helpers: `winsock_tcp_wouldblock`, `winsock_register_wsaevent`, `winsock_unregister_wsaevent`.
- `mini_ev_cmp` is exposed for timeout rbtree ordering.

## Design Notes
The header documents the main portability problem: Windows socket readiness behaves differently from Unix readiness, and TCP streams require remembered event bits until the application reports `WSAEWOULDBLOCK`. It also records practical Windows constraints: no generic file-descriptor waits, limited wait handles, non-small socket numbers, and TCP I/O should use `recv`/`send`.

## Dependencies and Integration
Only active under `USE_WINSOCK`. It depends on Unbound's `rbtree.h` and WinSock types such as `WSAEVENT`. Consumers include `winsock_event.c` and other Unbound code compiled against event/libevent-like APIs.

## Notable Constraints
The structures are not opaque in this header, so internal implementation details are visible to callers. That matches the local libevent compatibility style but makes ABI/layout changes more exposed.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/winsock_event.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/Makefile.inc -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/Makefile.inc

## Purpose
OpenBSD make include fragment that adds the libunbound validator source directory and validator source files to the `unwind` build.

## Contents
- Sets `.PATH` to `${.CURDIR}/libunbound/validator`.
- Appends validator C files to `SRCS`.

## Source List
Includes trust anchor, key cache, key entry, negative proof/cache, DNSSEC algorithm/signature utility, and main validator files:
`autotrust.c`, `val_anchor.c`, `val_kcache.c`, `val_kentry.c`, `val_neg.c`, `val_nsec.c`, `val_nsec3.c`, `val_secalgo.c`, `val_sigcrypt.c`, `val_utils.c`, and `validator.c`.

## Integration
This file is build-system glue only. It has no runtime behavior, but it determines which validator implementation files are compiled into OpenBSD's `sbin/unwind` libunbound copy.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/autotrust.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/autotrust.c

## Purpose
Implements RFC5011 automated DNSSEC trust anchor management for Unbound. It loads, persists, probes, verifies, updates, revokes, and removes trust anchor keys using the RFC5011 state table.

## Main Responsibilities
- Maintains global probe ordering in `autr_global_data.probe`.
- Parses auto-trust-anchor files, including metadata comments, `$ORIGIN`, multiline DNS records, DS/DNSKEY filtering, and per-file single-trust-point enforcement.
- Assembles valid autotrust key lists into heap-backed `ub_packed_rrset_key` DS/DNSKEY rrsets for validator use.
- Writes updated autotrust files atomically through a unique temporary file, flush/fsync, close, then rename.
- Verifies probed DNSKEY rrsets against current trust anchors.
- Detects self-signed revoked DNSKEYs and transitions stored keys into revoked/removed states.
- Implements add, delete, missing, revoked, and keep-missing holddown behavior.
- Schedules DNSKEY probe queries through the mesh and resets worker timers.

## Important State
`struct autr_ta` stores one tracked key and its RFC5011 state, pending count, last-change time, fetched marker, and revoked marker. `struct autr_point_data` stores per-trust-point file path, probe-tree node, key list, probe timing, query intervals, failure count, and revoked flag.

## Key Functions
- `autr_global_create` / `autr_global_delete`: allocate and initialize the global probe rbtree.
- `probetree_cmp`: orders trust points by `next_probe_time`, then by anchor identity.
- `autr_read_file`: reads persisted autotrust state and assembles rrsets.
- `parse_comments`: extracts per-key `state=`, `count=`, and `lastchange=` metadata.
- `autr_write_file`: persists state via temp-file replacement.
- `autr_assemble`: builds DS and DNSKEY packed rrsets from current key states.
- `verify_dnskey`: validates probed DNSKEY rrsets against trust anchor material.
- `check_contains_revoked`: finds self-signed revoked KSKs and marks stored keys revoked.
- `update_events`: notes fetched KSKs, adds new keys, bootstraps DNSKEYs from matching DS records, and updates query/retry intervals.
- `anchor_state_update`: applies the RFC5011 state transition matrix for each key.
- `autr_process_prime`: central processing path after a DNSKEY probe result.
- `probe_anchor`, `todo_probe`, `autr_probe_timer`: drive scheduled active DNSKEY probes.

## Control Flow
Startup/config loading calls `autr_read_file`, which creates or finds the trust point, loads keys, parses RFC5011 metadata, and assembles rrsets. Runtime probing calls `autr_probe_timer`, which selects due trust points, moves their next probe to a retry interval, clears cached DNSKEY/key-cache entries, and submits an active DNSKEY query. When the DNSKEY set is processed by `autr_process_prime`, the code checks revoked keys, verifies the DNSKEY set, updates fetched/new-key state, applies holddowns, cleans removed keys, schedules the next probe, writes the file, and reassembles rrsets if changed.

## Dependencies and Integration
Integrates tightly with `val_anchor`, `val_sigcrypt`, `val_utils`, `val_kcache`, rrset cache, mesh query service, regional scratch allocation, Unbound config, random jitter, and sldns wire/text conversion helpers. It stores autotrust points inside the same `val_anchors` tree as static trust anchors, with additional probe-tree membership.

## Notable Constraints and Risks
- File parsing is permissive enough to continue after bad individual records, but the final trust point must exist.
- Auto-trust files may contain only one anchor name/class; mixed names are rejected.
- `autr_write_file` uses fatal exits for persistent write/rename failure, reflecting that broken trust-anchor persistence is treated as critical.
- The implementation tracks ZSK-to-KSK bootstrap behavior for initially configured ZSKs, which is subtle and security-sensitive.
- Lock ordering is carefully managed: anchor tree lock and trust-point locks are released/reacquired in paths that mutate probe trees or run mesh queries.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/autotrust.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/autotrust.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/autotrust.h

## Purpose
Declares the data structures and public functions for RFC5011 automated trust anchor maintenance.

## Main Types
- `autr_state_type`: RFC5011 states `START`, `ADDPEND`, `VALID`, `MISSING`, `REVOKED`, and `REMOVED`.
- `struct autr_ta`: metadata for one tracked trust anchor RR, including wire RR, lengths, last change, state, pending count, fetched flag, and revoked flag.
- `struct autr_point_data`: per-trust-point autotrust state, including backing file path, probe-tree node, key list, last query/success times, next probe time, query/retry intervals, failure counter, and trust-point revoked flag.
- `struct autr_global_data`: global rbtree of autotrust anchors sorted by next probe time.

## Public API
- Global lifecycle: `autr_global_create`, `autr_global_delete`.
- Introspection/timers: `autr_get_num_anchors`, `autr_probe_timer`, `probetree_cmp`.
- Persistence: `autr_read_file`, `autr_write_file`.
- Trust point lifecycle: `autr_point_delete`.
- Probe processing: `autr_process_prime`, `probe_answer_cb`.
- Debug output: `autr_debug_print`.

## Integration
The header bridges validator trust-anchor storage (`val_anchors`, `trust_anchor`) with module runtime state (`module_env`, `module_qstate`, `val_env`) and packed DNS rrsets.

## Notable Constraints
The API exposes internal structures because autotrust state is embedded directly in `struct trust_anchor`. Callers must observe locking rules from `val_anchor` when reading or mutating these fields.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/autotrust.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_anchor.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_anchor.c

## Purpose
Implements validator trust anchor storage. It loads static trust anchors, insecure domains, BIND-style trusted-key files, and autotrust files into an rbtree keyed by class and domain name, then assembles DS/DNSKEY rrsets for validation.

## Main Responsibilities
- Creates/deletes `val_anchors` storage and all contained `trust_anchor` objects.
- Maintains parent pointers so lookup can find the closest enclosing trust anchor.
- Stores DS/DNSKEY trust anchor records from strings, zone files, and BIND `trusted-keys` syntax.
- Stores insecure points as trust anchors with no DS/DNSKEY records.
- Supports wildcard expansion for `trusted-keys-file` when `glob` is available.
- Assembles `ta_key` linked-list contents into `ub_packed_rrset_key` DS/DNSKEY rrsets.
- Filters out trust anchors whose DS/DNSKEY algorithms are all unsupported.
- Adds/deletes insecure points dynamically.
- Exposes keytag listing and keytag lookup helpers.

## Key Functions
- `anchors_create` / `anchors_delete`: allocate and free trust-anchor store plus autotrust global state.
- `anchor_cmp`: canonical rbtree ordering by class and domain-label order.
- `anchors_init_parents_locked`: recomputes closest parent pointers after tree mutation.
- `anchor_find` and `anchors_lookup`: exact and closest-enclosing lookup, returning locked anchors.
- `anchor_store_str`, `anchor_read_file`: parse textual DS/DNSKEY records and store them.
- `anchor_read_bind_file`, `process_bind_contents`: parse BIND `trusted-keys { ... };` format.
- `anchors_apply_cfg`: applies all trust-anchor-related configuration sources.
- `anchors_assemble_rrsets`: assembles usable rrsets and removes anchors with no supported algorithms.
- `anchors_add_insecure` / `anchors_delete_insecure`: dynamic insecure point management.
- `anchor_list_keytags`, `anchor_has_keytag`: keytag utilities.
- `anchors_swap_tree`: swaps anchor/probe trees with preallocated data.

## Control Flow
Configuration application inserts insecure LAN zones and `domain-insecure` entries first, then loads trust-anchor files, BIND trusted-key files, inline trust-anchor strings, and finally autotrust files. Static anchors are then assembled and parent pointers are initialized. Lookup later uses the sorted tree and parent pointers to return the closest applicable trust anchor for a query name/class.

## Dependencies and Integration
Uses `val_sigcrypt` for algorithm/keytag checks, `autotrust` for RFC5011 files, sldns parsing helpers, Unbound lock/rbtree utilities, AS112 insecure LAN zones, and packed rrset structures.

## Notable Constraints and Risks
- The assembled rrsets reuse `ta_key->data` pointers; deletion paths must avoid double-free by only freeing wrapper arrays/data structures appropriately.
- BIND parser is purpose-built for trusted-key clauses rather than a full named.conf parser.
- Lookup returns locked anchors, so callers must unlock.
- Unsupported algorithms are warned about; anchors with no supported material are removed from the tree.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_anchor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_anchor.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_anchor.h

## Purpose
Defines trust anchor storage types and declares validator trust-anchor management functions.

## Main Types
- `struct val_anchors`: global trust-anchor store with a lock, canonical rbtree, and autotrust global data.
- `struct ta_key`: one stored DS or DNSKEY trust anchor rdata blob.
- `struct trust_anchor`: one anchor point keyed by name/class, with lock, parent pointer, key list, optional autotrust data, DS/DNSKEY counts, assembled rrsets, and class.

## Public API
- Store lifecycle: `anchors_create`, `anchors_delete`.
- Configuration: `anchors_apply_cfg`.
- Parent maintenance: `anchors_init_parents_locked`.
- Lookup: `anchors_lookup`, `anchor_find`.
- Parsing/storage: `anchor_store_str`.
- Memory accounting: `anchors_get_mem`.
- Ordering: `anchor_cmp`.
- Insecure points: `anchors_add_insecure`, `anchors_delete_insecure`.
- Keytag helpers: `anchor_list_keytags`, `anchor_has_keytag`.
- Discovery/swap: `anchors_find_any_noninsecure`, `anchors_swap_tree`.

## Locking Model
The header documents the important ordering rule: lock the global tree first, find an anchor, then lock the anchor. To delete an anchor, callers may need to release and look up again because parent pointers and tree membership are protected globally.

## Integration
This is the core shared trust-anchor representation used by static anchors, autotrust, and the DNSSEC validator's chain-building logic.

## Notable Constraints
`trust_anchor` contains both static-anchor and autotrust fields. Code must distinguish static anchors from autotrust anchors by checking `ta->autr`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_anchor.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_kcache.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_kcache.c

## Purpose
Implements the validator key cache, a shared slabhash-backed cache of validated key entries and negative/insecure key states.

## Main Responsibilities
- Creates and destroys `struct key_cache`.
- Inserts copied `key_entry_key` objects into the slabhash.
- Looks up exact key entries under lock.
- Performs closest-enclosing key lookup by walking up labels from the queried name to root.
- Checks TTL before returning a region-allocated copy.
- Removes exact entries from the cache.
- Reports memory use.

## Key Functions
- `key_cache_create`: uses `cfg->key_cache_slabs` and `cfg->key_cache_size` to create the slabhash with key-entry callbacks.
- `key_cache_insert`: deep-copies a key entry, hashes it, and inserts it.
- `key_cache_search`: exact lookup helper returning a locked cache entry.
- `key_cache_obtain`: repeatedly searches the queried name and parent names until it finds an unexpired key entry or reaches root.
- `key_cache_remove`: exact remove by name/class.
- `key_cache_get_mem`: returns wrapper plus slabhash memory.

## Dependencies and Integration
Uses `val_kentry` for key-entry hashing/copy/delete callbacks, `slabhash` for concurrent cache storage, `dname_remove_label` for parent traversal, and Unbound configuration/logging.

## Notable Constraints
Expired entries are ignored by `key_cache_obtain` but not removed there. Returned entries are copies allocated in the caller's regional allocator, while the original cache entry lock is released before return.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_kcache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_kcache.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_kcache.h

## Purpose
Declares the validator key cache API.

## Main Type
`struct key_cache` wraps a `struct slabhash*` that stores `key_entry_key` / `key_entry_data` pairs.

## Public API
- `key_cache_create`: create cache from config.
- `key_cache_delete`: free cache.
- `key_cache_insert`: copy and insert/update a key entry.
- `key_cache_remove`: remove exact key entry by name/class.
- `key_cache_obtain`: find the closest unexpired key entry above a query name and copy it to a region.
- `key_cache_get_mem`: report memory usage.

## Integration
This header connects validator chain logic with the shared cache and depends on `util/storage/slabhash.h`. Concrete key-entry semantics are defined in `val_kentry.h`.

## Notable Constraints
Insertion may silently fail on memory pressure, as documented. Consumers must tolerate cache misses.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_kcache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_kentry.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_kentry.c

## Purpose
Implements validator key-entry storage, copying, comparison, construction, and conversion routines used by the key cache and validation pipeline.

## Main Responsibilities
- Provides slabhash/lruhash callbacks for size, compare, delete-key, and delete-data.
- Hashes key entries by class and domain name.
- Deep-copies key entries either to malloc storage or to a regional allocator.
- Represents three key-entry states: good key rrset, bad key with reason/EDE, and null/insecure entry.
- Creates key entries from null, bad, and rrset inputs.
- Converts a stored key entry back into a region-allocated packed rrset.
- Computes the smallest ZSK key size in a good DNSKEY rrset.

## Key Functions
- `key_entry_sizefunc`: estimates memory use including name, data, lock, rrset data, reason, and algorithm list.
- `key_entry_compfunc`: orders entries by class and query dname.
- `key_entry_hash`: class plus dname lookup3 hash.
- `key_entry_copy_toregion`: region deep-copy for query processing.
- `key_entry_copy`: malloc deep-copy for cache insertion.
- `key_entry_isnull`, `key_entry_isgood`, `key_entry_isbad`: state predicates.
- `key_entry_create_null`, `key_entry_create_rrset`, `key_entry_create_bad`: constructors.
- `key_entry_get_rrset`: reconstructs a `ub_packed_rrset_key` from stored data.
- `key_entry_keysize`: scans DNSKEY records for ZSK flags and returns smallest supported key size calculation.

## Dependencies and Integration
Uses packed rrset utilities, dname comparison/hash helpers, regional allocation, network byte-order helpers, and sldns raw DNSKEY key-size routines. The resulting objects are consumed by `val_kcache` and DNSSEC validation code.

## Notable Constraints and Risks
- Region constructors intentionally tolerate failure to store optional reason strings.
- `key_entry_copy` conditionally copies the reason string based on `copy_reason`; callers decide whether cached entries own that diagnostic text.
- Algorithm list memory is treated as NUL-terminated string data for size/copy purposes.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_kentry.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_kentry.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_kentry.h

## Purpose
Defines validator key-entry structures and declares helper functions for key cache storage and DNSSEC validation.

## Main Types
- `struct key_entry_key`: lruhash key containing hash entry, key name, name length, and DNS class.
- `struct key_entry_data`: cached key state containing absolute TTL, optional rrset data, reason string, EDE code, algorithm list, rrset type, and bad-key flag.

## Represented States
- Good key: `isbad == 0` and `rrset_data != NULL`.
- Bad key: `isbad == 1`.
- Null/insecure entry: `isbad == 0` and `rrset_data == NULL`.

## Public API
Includes lruhash callbacks, hashing, malloc/region copy helpers, state predicates, reason/EDE accessors, constructors for null/good/bad entries, rrset reconstruction, and key-size calculation.

## Integration
This header is the contract between the validator cache (`val_kcache`), packed rrset storage, and validator chain logic.

## Notable Constraints
Function comments specify whether returned objects are malloc-owned, region-owned, or references to entry-owned data. Correct allocator ownership matters for avoiding leaks or invalid frees.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_kentry.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_neg.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_neg.c

## Purpose
Implements aggressive negative caching for DNSSEC denial-of-existence records. It indexes secure NSEC/NSEC3 rrsets by zone and owner name, then synthesizes negative responses or DS insecurity proofs from cached denial material.

## Main Responsibilities
- Maintains a locked negative cache with a zone rbtree, per-zone data rbtree, global LRU list, memory accounting, and size limit.
- Inserts secure NSEC records from negative replies and secure NSEC/NSEC3 records from referrals.
- Creates parent-chain nodes for zones/data so closest-enclosing lookup is efficient.
- Evicts least-recently-used denial records to stay within `neg_cache_size`.
- Removes stale/conflicting cached denial entries covered by newly inserted NSEC spans.
- Retrieves NSEC/NSEC3 rrsets from the rrset cache and verifies security/TTL suitability before using them.
- Synthesizes NOERROR/NODATA, NXDOMAIN, wildcard-derived answers, and DS negative proofs.

## Key Functions
- `val_neg_create`, `neg_cache_delete`, `val_neg_get_mem`: lifecycle and memory accounting.
- `neg_delete_data`, `neg_delete_zone`, `neg_make_space`: eviction/removal mechanics.
- `neg_create_zone`, `neg_insert_data`: build zone/data chain entries and insert denial records.
- `val_neg_addreply`: caches secure NSEC records from replies with SOA or signer-derived zone.
- `val_neg_addreferral`: caches NSEC/NSEC3 records from referrals after bailiwick/signer checks.
- `grab_nsec`: fetches a suitable NSEC/NSEC3 rrset from rrset cache, optionally checking absence of a type bit.
- `neg_find_nsec`: finds the best cached NSEC denial for a qname.
- `neg_find_nsec3_ce`, `neg_nsec3_getnc`, `neg_nsec3_proof_ds`: NSEC3 closest-encloser/next-closer DS proof logic.
- `add_soa`: adds SOA authority data when producing external negative responses.
- `val_neg_getmsg`: central message synthesis entry point.
- `val_neg_adjust_size`: updates cache limit and evicts as needed.

## Control Flow
Insertion paths find or create the relevant zone, mark it in-use, add each suitable denial rrset as an in-use data node, update NSEC3 parameters when applicable, and wipe cached records made obsolete by the inserted denial span. Lookup first tries NSEC-based NODATA/name-error synthesis. If aggressive NSEC is disabled, only DS queries continue. For DS queries, NSEC3 proof logic may create a response from closest-encloser and opt-out/next-closer records.

## Dependencies and Integration
Uses `val_nsec`, `val_nsec3`, `val_utils`, rrset cache, DNS message construction helpers, Unbound config, dname canonical ordering, and locks/rbtrees. The cache stores only indexes; actual rrset payloads are retrieved from the rrset cache.

## Notable Constraints and Risks
- The cache indexes denial records but depends on rrset cache retention; indexed records can become unusable if corresponding rrsets expire or are evicted.
- NSEC3 aggressive use is restricted mainly to DS proof handling.
- Large NSEC3 salts above `MAX_SALT_LENGTH` are declined for caching to avoid expensive hash work.
- `val_neg_getmsg` respects `cfg->aggressive_nsec` except for DS queries, which still use negative-cache proof paths.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_neg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_neg.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_neg.h

## Purpose
Declares aggressive negative-cache structures and APIs for validator denial-of-existence synthesis.

## Main Types
- `struct val_neg_cache`: shared locked cache with zone tree, LRU pointers, memory limits, NSEC3 iteration limit, and statistics counters.
- `struct val_neg_zone`: per-zone cache node with name/class, parent pointer, usage count, NSEC3 parameters, data tree, and in-use flag.
- `struct val_neg_data`: per-denial owner node with name, parent, count, zone pointer, LRU links, and in-use flag.

## Public API
- Lifecycle/memory: `val_neg_create`, `val_neg_get_mem`, `neg_cache_delete`, `val_neg_adjust_size`.
- Ordering: `val_neg_data_compare`, `val_neg_zone_compare`.
- Insertions: `val_neg_addreply`, `val_neg_addreferral`.
- Lookup/synthesis: `val_neg_getmsg`.
- Unit-test-exposed internals: `neg_insert_data`, `neg_delete_data`, `neg_find_zone`, `neg_create_zone`, `val_neg_zone_take_inuse`.

## Design Notes
The header explains the two-level tree design: zones hold NSEC data trees, while actual rrsets remain in the rrset cache. Parent placeholder nodes are intentionally stored to make insertion, deletion, and closest lookup logarithmic while preserving subtree counts.

## Integration
Used by the validator environment to opportunistically answer or prove negative results from already validated denial records.

## Notable Constraints
The cache is guarded by one coarse lock because rbtrees and LRU state are shared. This favors correctness and simple mutation semantics over fine-grained concurrency.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_neg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_nsec.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_nsec.c

## Purpose
Implements NSEC denial-of-existence helper logic for the DNSSEC validator. It checks NSEC type bitmaps, validates NSEC rrsets before use, and determines whether NSEC records prove NODATA, NXDOMAIN, insecure delegation, wildcard use, or wildcard absence.

## Main Responsibilities
- Parses NSEC type bitmaps safely by window.
- Extracts the NSEC next owner name from rdata.
- Verifies NSEC rrset security status through cache status or signature validation.
- Checks DS-specific NODATA proofs at delegations.
- Checks NODATA proofs for exact names, empty non-terminals, wildcard NSEC records, and wildcard empty non-terminals.
- Checks name-error coverage using canonical ordering and wraparound handling.
- Determines closest encloser from an NSEC owner/next pair.
- Proves positive wildcard applicability and absence of wildcard records.

## Key Functions
- `nsecbitmap_has_type_rdata`: low-level NSEC type bitmap membership test.
- `nsec_has_type`: checks a type in the first NSEC RR's bitmap.
- `nsec_get_next`: returns the next owner name and validates its dname encoding.
- `val_nsec_proves_no_ds`: validates DS absence or insecure non-delegation semantics for DS replies.
- `nsec_verify_rrset`: verifies or refreshes an NSEC rrset's secure status.
- `val_nsec_prove_nodata_dsreply`: DS-reply-specific proof orchestration using authority-section NSECs.
- `nsec_proves_nodata`: general NODATA proof logic.
- `val_nsec_proves_name_error`: NXDOMAIN/name-error coverage check.
- `val_nsec_proves_insecuredelegation`: detects parent-side NSEC proving insecure delegation.
- `nsec_closest_encloser`: derives closest encloser from NSEC proof material.
- `val_nsec_proves_positive_wildcard`: proves qname nonexistence and correct wildcard use.
- `val_nsec_proves_no_wc`: proves no applicable wildcard exists.

## Control Flow
Higher-level validator code passes candidate NSEC rrsets and query info into these predicates. DS-specific logic first looks for exact qname NSEC and validates it; if absent, it scans authority NSECs for empty-nonterminal and closest-encloser/wildcard conditions. General proof routines combine canonical owner/next coverage, type bitmap absence, CNAME/delegation exclusions, and wildcard closest-encloser checks.

## Dependencies and Integration
Uses validator utilities, signature verification, rrset cache security status updates, reply lookup helpers, dname canonical comparison, packed rrset structures, and sldns type constants.

## Notable Constraints and Risks
- Functions generally inspect the first NSEC RR in an rrset for owner/bitmap proof data.
- DS handling has special parent/child-side checks involving SOA, NS, and DS bits.
- Several routines return simple boolean proof results, so callers must attach appropriate validation status/reason handling.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_nsec.c -->