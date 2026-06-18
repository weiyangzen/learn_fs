# sources/distributed-fs/ceph-client/net/xfrm/xfrm_state.c

## Purpose

`xfrm_state.c` is the core Security Association Database implementation. It owns XFRM state allocation, hash indexes, type/mode registration, state lookup, acquire state creation, add/update/delete/flush, lifetime timers, replay timers, migration, SPI allocation, key-manager registration/notifications, AF registration, socket policy compilation dispatch, audit records, and per-net SAD initialization.

## Important APIs, Types, and Functions

The per-net SAD is indexed by destination tuple (`state_bydst`), source tuple (`state_bysrc`), SPI/protocol/destination (`state_byspi`), and acquire sequence (`state_byseq`). `struct xfrm_hash_state_ptrs` snapshots RCU-protected hash table pointers and mask under a seqcount. `XFRM_STATE_INSERT` keeps packet-offload SAs at the head of chains so hardware lookups can short-circuit.

Registration APIs include `xfrm_register_type()`, `xfrm_unregister_type()`, `xfrm_register_type_offload()`, `xfrm_unregister_type_offload()`, `xfrm_set_type_offload()`, `xfrm_register_mode_cbs()`, `xfrm_unregister_mode_cbs()`, `xfrm_state_register_afinfo()`, and `xfrm_state_unregister_afinfo()`.

Lifecycle APIs include `xfrm_state_alloc()`, `xfrm_state_free()`, `__xfrm_state_destroy()`, `__xfrm_state_delete()`, `xfrm_state_delete()`, `xfrm_state_flush()`, `xfrm_dev_state_flush()`, `xfrm_state_insert()`, `xfrm_state_add()`, `xfrm_state_update()`, `xfrm_state_check_expire()`, `xfrm_init_state()`, `__xfrm_init_state()`, `xfrm_state_init()`, and `xfrm_state_fini()`.

Lookup and acquire APIs include `xfrm_input_state_lookup()`, `xfrm_state_find()`, `xfrm_stateonly_find()`, `xfrm_state_lookup_byspi()`, `xfrm_state_lookup()`, `xfrm_state_lookup_byaddr()`, `xfrm_find_acq()`, `xfrm_find_acq_byseq()`, `xfrm_get_acqseq()`, `verify_spi_info()`, and `xfrm_alloc_spi()`.

Key-manager and user-policy APIs include `xfrm_register_km()`, `xfrm_unregister_km()`, `km_query()`, `km_state_notify()`, `km_policy_notify()`, `km_state_expired()`, `km_policy_expired()`, `km_new_mapping()`, `km_report()`, optional `km_migrate()`, and `xfrm_user_policy()`. Optional compatibility translator APIs are registered under `CONFIG_XFRM_USER_COMPAT`.

## Control Flow

State initialization begins with `xfrm_state_alloc()`, which sets namespace, reference count, hash/list nodes, timers, default lifetime limits, add time, replay notification thresholds, and locks. User/netlink-created states call `xfrm_init_state()`, which resolves inner/outer modes, loads the protocol type module if needed, calls the type `init_state`, validates NAT keepalive constraints, initializes optional mode callbacks, initializes replay mode, and marks the state valid.

Adding a state through `xfrm_state_add()` checks for existing states by SPI or address, optionally finds and deletes a matching acquire state, bumps generation IDs of related cached users, inserts into all relevant hash tables, starts timers, updates counters, and triggers hash growth if a collision occurs. `xfrm_state_update()` either replaces an acquire state with a valid state or updates mutable fields on an existing valid state while preserving identity constraints.

Outbound policy resolution calls `xfrm_state_find()`. It first consults the policy's state cache, then the by-destination hash, then wildcard-source entries. It chooses the best valid state by selector/security match, per-CPU acquire policy, dying state, and add time. If no state exists and key managers are alive, it creates an acquire state, initializes a temporary selector, optionally configures packet offload acquisition, calls `km_query()`, inserts the acquire into indexes, and starts the acquire timer.

Inbound packet lookup calls `xfrm_input_state_lookup()`, which first checks a per-CPU input cache, then by-SPI hash. Valid hits are moved to the head of the per-CPU cache under the state lock. BPF XDP helpers in another file call the exported `xfrm_state_lookup()`.

Deletion sets `km.state` to DEAD, unlinks the state from all indexes and caches, decrements the namespace count, updates NAT keepalive tracking, deletes device state, releases tunnel dependencies, and drops the allocation reference. Actual memory/freeing is RCU-delayed through `xfrm_state_gc_work`, which cancels timers, frees algorithms, replay ESN storage, encapsulation/coaddr, offload state, security context, mode state, protocol type reference, and the slab object.

Lifetime handling is split between `xfrm_timer_handler()` for soft/hard add/use expirations and byte/packet limit checks in `xfrm_state_check_expire()`. Replay async events use `xfrm_replay_timer_handler()`. Key-manager notification functions fan out over the RCU `xfrm_km_list`.

## State and Persistence Behavior

Each `struct xfrm_state` persists identity (`id.daddr`, SPI, proto), source address, reqid, mode, family, selector, marks, interface ID, security context, algorithms, encapsulation, coaddr, replay state, offload metadata, NAT keepalive fields, lifetime counters, timers, generation ID, optional tunnel relation, and key-manager state. Per-net state persists hash tables, state count, all-state walk list, per-CPU input caches, and hash resize work.

Hash table replacement uses seqcounts and RCU so lockless readers can retry safely. State references are protected with `refcount_inc_not_zero()` in RCU readers. Device offload state has a separate GC list so drivers can free resources after deletion and netdev teardown.

Acquire states are temporary but persisted in the SAD so subsequent packets do not flood key managers. Their hard-add lifetime is taken from `net->xfrm.sysctl_acq_expires`.

## Dependencies and Integration Points

This file depends on protocol type implementations for ESP/AH/IPCOMP/tunnel headers, mode callback modules such as IPTFS, crypto AEAD for MTU calculation, key managers, XFRM policy code, replay code, XFRM device offload, NAT keepalive, LSM hooks, audit, netlink extack, random SPI allocation, RCU/hash helpers, per-net namespaces, and optional user compatibility translation.

Integration points include outbound bundle creation in `xfrm_policy.c`, inbound state lookup in `xfrm_input.c`, user/netlink/PF_KEY state management, BPF XDP state lookup, hardware offload drivers, IKE/key-manager daemons through acquire/expire/migrate callbacks, and proc statistics through `xfrm_state_update_stats()`.

## Risks and Edge Cases

Identity and index consistency are critical. A state can be indexed by multiple hash tables plus per-policy/per-CPU caches; deletion must remove all links exactly once and invalidate cached users through generation IDs. RCU readers and hash resize seqcounts must not observe freed tables or states.

Acquire logic deliberately rate-limits key-manager requests. Bugs can either flood acquire messages or fail to request missing SAs, causing traffic drops. Per-CPU acquire policy adds another matching dimension and fallback behavior.

Lifetime timers interact with soft expiry, hard expiry, device stats updates, and audit/key-manager notifications. Changes can produce duplicate expiry messages, stale valid SAs, or premature deletion. Offload state ordering is sensitive because hardware resources and software SAD entries must stay coherent.

State initialization loads modules and validates modes/types/NAT keepalive/replay. Missing validation can admit impossible SAs; over-strict validation can break existing IPsec configurations. SPI allocation must avoid collisions across protocol and state tables while handling signals.

## Test Signals

Useful tests add, update, delete, flush, and walk states for ESP/AH/IPCOMP over IPv4 and IPv6; exercise acquire creation and expiration; allocate SPIs over fixed and random ranges; verify input lookup by SPI and output lookup by template; test packet offload and crypto offload; run namespace teardown; validate soft/hard lifetime notifications; and confirm audit records for SAD add/delete/replay/notfound/ICV failures.

Runtime observability includes `ip xfrm state`, `ip xfrm monitor`, `/proc/net/xfrm_stat`, XFRM audit messages, key-manager acquire/expire events, device offload callbacks, and MIB counters for missing states, expired states, proto/mode/sequence errors, and direction errors.
