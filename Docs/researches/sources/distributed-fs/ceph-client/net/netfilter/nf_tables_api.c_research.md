# Research: sources/distributed-fs/ceph-client/net/netfilter/nf_tables_api.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006248`: lines 1-10477, `Docs/researches/chunks/subset-b-006248_research.md`
- `subset-b-006249`: lines 10478-12266, `Docs/researches/chunks/subset-b-006249_research.md`

## Chunk Research

### subset-b-006248: lines 1-10477

# sources/distributed-fs/ceph-client/net/netfilter/nf_tables_api.c lines 1-10477

## Scope

This chunk covers the first 10,477 lines of `nf_tables_api.c`, the main nf_tables netlink API implementation. The range starts at module includes and global registries, then covers transaction allocation/staging, table, chain, expression, rule, set, set element, stateful object, flowtable, generation-info, callback dispatch, validation, commit-preparation, deferred destruction, and the beginning of transaction-GC helpers. The assigned range ends inside the GC support area after `nft_trans_gc_trans_free()`, so later commit, abort, register parsing, verdict/data helpers, netns teardown, and module init/exit logic are intentionally left to later chunks.

## Purpose

This code is the kernel-side control plane for nftables objects manipulated through nfnetlink. It converts netlink messages into staged transactions against per-network-namespace nf_tables state, validates references and jump graphs, registers/unregisters packet hooks and flowtable hooks, emits notifications/audit records, and prepares the RCU-visible datapath rule blobs used by `nf_tables_core`.

The core model is transactional. Batch callbacks parse and enqueue `struct nft_trans` entries into `nftables_pernet.commit_list`; objects are made visible or invisible through generation masks and RCU lists, then later committed or aborted as a unit. Read callbacks run under RCU and dump the current generation. This chunk includes most object-specific create/update/delete/get/dump paths and the early commit helpers that rebuild chain blobs and release old state.

## Important APIs, Types, and Global State

- Global extension registries:
  - `nf_tables_expressions`, `nf_tables_objects`, and `nf_tables_flowtables` hold registered expression types, stateful object types, and flowtable types.
  - `chain_type[NFPROTO_NUMPROTO][NFT_CHAIN_T_MAX]` holds registered base-chain types.
  - `nft_objname_ht` is a global rhltable for object lookup by `(table, name)`.
  - `nf_tables_gc_list` and `trans_gc_work` start the asynchronous set-element transaction-GC path; the chunk only includes the beginning of that subsystem.
- Per-netns state is reached with `nft_pernet(net)` and includes table lists, commit/notify/binding/module lists, validation state, generation cursor/base sequence, commit mutex, and destroy work.
- `struct nft_ctx` is the per-command context carrying `net`, family, table, chain, parsed attributes, portid, report flag, netlink flags, sequence, recursion level, and initialized-register bitmap.
- `struct nft_trans` and typed containers (`nft_trans_table`, `nft_trans_chain`, `nft_trans_rule`, `nft_trans_set`, `nft_trans_elem`, `nft_trans_obj`, `nft_trans_flowtable`) represent staged mutations.
- Exported registration/lookup helpers in this chunk include `nft_register_chain_type()`, `nft_unregister_chain_type()`, `nft_register_expr()`, `nft_unregister_expr()`, `nft_register_obj()`, `nft_unregister_obj()`, `nft_register_flowtable_type()`, `nft_unregister_flowtable_type()`, `nft_set_lookup_global()`, `nft_obj_lookup()`, `nft_flowtable_lookup()`, `nft_chain_add()`, `nft_chain_del()`, and hook/GC helpers such as `nft_hook_find_ops()` and `nft_hook_find_ops_rcu()`.

## Netlink Surfaces

The `nf_tables_cb` array maps `NFT_MSG_*` commands to handlers and validation policies. Batch-mutating callbacks include:

- Tables: `nf_tables_newtable()` and `nf_tables_deltable()`.
- Chains: `nf_tables_newchain()` and `nf_tables_delchain()`.
- Rules: `nf_tables_newrule()` and `nf_tables_delrule()`.
- Sets and elements: `nf_tables_newset()`, `nf_tables_delset()`, `nf_tables_newsetelem()`, and `nf_tables_delsetelem()`.
- Stateful objects: `nf_tables_newobj()` and `nf_tables_delobj()`.
- Flowtables: `nf_tables_newflowtable()` and `nf_tables_delflowtable()`.

RCU read callbacks include the corresponding `GET*` operations and reset variants for rules, set elements, and objects. Dump functions use `netlink_dump_start()` through `nft_netlink_dump_start_rcu()`, which temporarily drops/reacquires RCU around dump setup while holding a module reference. Fill helpers such as `nf_tables_fill_table_info()`, `nf_tables_fill_chain_info()`, `nf_tables_fill_rule_info()`, `nf_tables_fill_set()`, `nf_tables_fill_setelem_info()`, `nf_tables_fill_obj_info()`, `nf_tables_fill_flowtable_info()`, and `nf_tables_fill_gen_info()` serialize kernel objects back into nft netlink attributes.

## Control Flow

### Transaction Staging

`nft_ctx_init()` normalizes netlink metadata into `struct nft_ctx`. Object-specific helpers allocate transactions with `nft_trans_alloc()` and append them through `nft_trans_commit_list_add_tail()` or `nft_trans_commit_list_add_elem()`. Anonymous-set and bound-chain transactions also enter `binding_list`; new sets enter `commit_set_list` for same-batch ID lookup. Consecutive set-element transactions can be compacted by `nft_trans_try_collapse()` into a single `nft_trans_elem`, capped by `NFT_MAX_SET_NELEMS` to avoid large `krealloc()` requests.

Creation paths usually allocate the kernel object, mark it active in the next generation, enqueue a transaction, then add it to an RCU list/hash. Deletion paths enqueue a delete transaction, mark the object inactive in the next generation, decrement table/chain/set/object use counters, and defer actual release until commit cleanup. Error paths undo use counters, hook registration, module refs, expression refs, and RCU-visible inserts carefully.

### Tables

`nf_tables_newtable()` supports create or update. It validates supported protocol families, owner/dormant/persist flags, initializes chain hash/list heads, assigns a handle, stores owner portid and userdata, enqueues a `NEWTABLE` transaction, and links the table into the per-netns table list. `nf_tables_updtable()` handles dormant/owner flag changes and uses internal `__NFT_TABLE_F_*` flags to prevent multiple off/on dormant transitions in a single transaction. Dormant toggles register or unregister base-chain hooks as needed.

`nf_tables_deltable()` either flushes matching tables or deletes a selected table by name/handle. `nft_flush_table()` recursively queues deletion of rules, non-anonymous sets, flowtables, objects, chains, and finally the table. Owner checks prevent a different netlink portid from modifying owned tables.

### Chains and Hooks

Chains are looked up by name through per-table `chains_ht`, by handle through the table list, or by same-batch ID through `commit_list`. Base chains parse `NFTA_CHAIN_HOOK` with `nft_chain_parse_hook()`, resolve chain type modules, validate hook number/priority/device attributes, and initialize `nf_hook_ops`. Netdev base chains can bind multiple devices or device-name prefixes through `struct nft_hook` lists; non-netdev chains reject device attributes.

`nf_tables_addchain()` creates either a base chain or regular chain, allocates initial empty rule blobs for both generation slots, increments table use, queues a `NEWCHAIN` transaction, inserts into the chain hash/list, then registers hooks last so packets cannot see a partially initialized chain. `nf_tables_updchain()` stages policy, counters, rename, and netdev hook additions; new netdev hooks are registered before the transaction is appended and are unregistered on failure. `nf_tables_delchain()` can delete selected netdev hooks or recursively queue all rule deletions before deleting the chain, while preserving use-count checks for referenced chains.

### Expressions and Rules

Expression types are registered globally and selected by family-specific or family-unspecified name. `nf_tables_expr_parse()` parses expression netlink attributes, obtains module refs, and calls optional `select_ops()`. Stateful expression allocation uses `nft_expr_init()` and rejects non-`NFT_EXPR_STATEFUL` types for set-element/object contexts. Expression destruction always releases type module refs and type-specific resources.

Rule creation parses up to `NFT_RULE_MAXEXPRS`, totals expression data length into the 12-bit rule `dlen` field, allocates `struct nft_rule` plus inline expressions/userdata, initializes each expression, optionally builds a flow offload rule for hardware-offloaded chains, increments chain use, queues `NEWRULE`, and inserts into the chain's rule list before/after a position or at head/tail depending on flags. Replace first queues deletion of the old rule and then links the new rule at the old position. Rule deletion stages `DELRULE`, creates a flow rule for offloaded deletion, marks the rule inactive in the next generation, decrements chain use, and deactivates all expression references.

Validation is deferred by table state. Any expression with `ops->validate`, or map element verdicts that jump/goto, mark the table as needing validation. `nft_chain_validate()` recursively walks active rules from each base chain, calls expression validation hooks, rejects jumps to base chains, enforces `NFT_JUMP_STACK_SIZE`, and caches per-chain hook/type/depth validation state to avoid redundant work. `nf_tables_validate()` upgrades `NFT_VALIDATE_NEED` to `NFT_VALIDATE_DO`, validates all affected tables, and resets them to skip on success.

### Sets and Set Elements

`nf_tables_newset()` parses set key/data/object types, flags, timeout/gc interval, policy, concat descriptor, and optional per-element expressions. It selects a backend from `nft_set_types` using each backend's `estimate()` result and policy. Existing named sets are treated idempotently only if their structural attributes and expression ops match. New sets allocate backend private storage, generated/explicit name, userdata, refs/bindings/catchall lists, backend init, element expression templates, handle, and a `NEWSET` transaction before linking to the table.

Set binding APIs are central integration points for expressions. `nf_tables_bind_set()` validates map verdict data for all active elements and catchall elements, rejects multiple bindings to anonymous sets, increments set use, links the binding, and marks pending anonymous set transactions as bound. `nf_tables_deactivate_set()` handles different transaction phases, including prepare errors, abort/release, anonymous-map deactivation, and event emission when an anonymous set becomes unbound.

Element creation in `nft_add_set_elem()` is the densest path in the chunk. It validates catchall/key requirements, interval-end restrictions, map/object data requirements, key-end rules, timeout/expiration bounds, and element-expression compatibility. It parses key/key_end/data, validates map verdicts against already-bound chains, resolves object references and bumps object use, lays out requested extensions through `nft_set_ext_tmpl`, initializes the element private storage, copies userdata last because extension offsets are `u8`, clones/sets up expressions, checks set capacity, allocates a `NEWSETELEM` transaction, and inserts into either the backend or catchall list. Duplicate elements can either fail, update timeout/expiration through `struct nft_elem_update`, or be treated as no-op for special interval backend return codes.

Element deletion parses a lookup element, deactivates it through backend or catchall path, releases data/object references, and queues `DELSETELEM`. Flush walks the backend with `NFT_ITER_UPDATE_CLONE`, queues delete transactions for every active element, and handles catchall elements separately. Dump/get paths skip inactive, expired, or dead elements; reset variants produce audit records. Element lifecycle helpers distinguish full destruction with reference release, commit-time destruction after references were already dropped, and abort-time undo of new/delete transactions.

### Stateful Objects

Object types are registered globally and optionally autoloaded by numeric type. `nf_tables_newobj()` creates or updates objects. New objects increment table use, get the object type/module, initialize private object data through object ops, assign handle/name/userdata, stage a `NEWOBJ` transaction, insert into `nft_objname_ht`, and link to the table list. Existing objects can be updated only if the object's ops provide `update`; the replacement object is initialized and stored in the transaction until commit applies `obj->ops->update()` and destroys the temporary object. Deletes require zero use and stage `DELOBJ`.

Object dumps and reset gets can audit reset operations. `nft_obj_notify()` is exported for object implementations to emit notifications and audit records for object register/unregister events.

### Flowtables

Flowtable types are registered globally and selected by family, with module autoload support. Flowtables attach to netdev ingress hooks only. `nft_flowtable_parse_hook()` parses hook number/priority/devices, builds per-device `nf_hook_ops`, and points each op at `flowtable->data.type->hook`.

`nf_tables_newflowtable()` creates a flowtable, initializes type-specific `nf_flowtable` data, parses hooks, queues a `NEWFLOWTABLE` transaction, registers flowtable net hooks last, and links it to the table. Updates can add hooks or change compatible flags; duplicate hook additions are rejected both against live flowtables and pending same-batch transactions. Deletion can remove selected hooks or delete the whole flowtable if its use count is zero. Hook registration/unregistration calls the flowtable type `setup()` callback for `FLOW_BLOCK_BIND`/`FLOW_BLOCK_UNBIND` around net hook registration.

Netdevice events are handled by `nf_tables_flowtable_event()`. Under the per-netns commit mutex, device register/unregister/changename events add or remove hook ops for matching flowtable hook name/prefixes, keeping flowtable offload hooks synchronized with netdev lifetime.

### Notifications, Audit, and Generation Info

Notify helpers allocate netlink skbs only when the request asked for reports or listeners exist on `NFNLGRP_NFTABLES`. Notifications are queued on `nft_net->notify_list` rather than sent immediately in these object paths. The chunk also maps nft message types to audit operation IDs and emits audit records for rule resets, set-element resets, object resets, and object notify operations.

`nf_tables_fill_gen_info()` and `nf_tables_getgen()` report the current base sequence plus current process pid/name. `nf_tables_gen_notify()` broadcasts generation changes after successful mutations when requested or listened for.

### Commit Preparation and Early Release Helpers

The chunk reaches the first commit helper block. `nf_tables_commit_chain_prepare()` builds a new contiguous `struct nft_rule_blob` for each changed active chain by copying active rule expressions into datapath layout and appending a trailer rule. `nf_tables_commit_chain()` publishes `blob_next` into the next generation slot (`blob_gen_0` or `blob_gen_1`) according to the generation cursor and frees the old generation blob after an RCU grace period. `nf_tables_commit_chain_prepare_cancel()` frees prepared blobs on preparation failure.

`nft_chain_commit_update()` applies staged chain rename/counter/policy changes, with drop policy sometimes deferred by `nft_chain_commit_drop_policy()` to avoid dropping packets before all staged rules are active. `nft_obj_commit_update()` applies staged object replacement. `nft_commit_release()` is the common post-commit release path for delete transactions and temporary update state, and `nf_tables_trans_destroy_work()` defers release from `destroy_list` until after `synchronize_rcu()`.

The final lines in this chunk begin transaction-GC support for set elements. `nft_trans_gc_setelem_remove()` deactivates data and removes expired/private elements from a set backend, `nft_trans_gc_trans_free()` decrements non-catchall element counts and destroys elements after RCU, and `nft_trans_gc_destroy()` drops the set and net references held by a GC transaction.

## State and Persistence Behavior

- nftables state is per network namespace but some type registries are module-global. Per-netns tables own chains, rules, sets, objects, and flowtables.
- Visibility is generation based. Mutations activate/deactivate objects in the next generation, then commit flips generation state and publishes new rule blobs under RCU.
- `use` counters prevent deletion while tables/chains/sets/objects/flowtables are still referenced. Helpers use `nft_use_inc()`, `nft_use_dec()`, and restore variants during abort/commit cleanup.
- RCU protects readers of tables, chains, rules, sets, objects, flowtables, hooks, and rule blobs. The commit mutex protects mutation and many lookup paths assert it or RCU.
- Module references are held for chain types, expression types, object types, and flowtable types while instances or parsed operations require them.
- Anonymous sets and binding chains have extra transaction binding bookkeeping so a single batch can create a resource, bind it from a rule/expression, and correctly release it on abort or delete.
- Netdev hooks and flowtable ops are external kernel state. They are registered late and unregistered on dormant toggles, hook deletion, flowtable deletion, netdev events, or error paths.
- User-visible persistence is in kernel memory until namespace teardown or explicit delete; handles increase per table and table handles per netns.

## Dependencies and Integration Points

- nfnetlink: message dispatch, batch semantics, dump callbacks, extack bad-attribute reporting, multicast groups, and netlink skb serialization.
- nf_tables core headers: object layouts, generation helpers, expression/rule iteration, set backend APIs, register/data/verdict helpers, offload hooks, and datapath blob format.
- Netfilter hook API: `nf_register_net_hook()`, `nf_unregister_net_hook()`, base-chain hook ops, and hook type callbacks.
- Flowtable/offload API: `nf_flow_table`, flowtable type init/free/setup/hook, flow block bind/unbind, and hardware offload rule helpers.
- Linux kernel infrastructure: RCU, rhashtable/rhltable, percpu counters, refcounts, workqueues, module autoload/refcounting, net namespaces, netdevice notifier, audit, jiffies/time conversion, and lockdep.
- Set backends: hash, rhash, bitmap, rbtree, pipapo, and optional AVX2 pipapo implement `init`, `destroy`, `insert`, `deactivate`, `remove`, `walk`, `flush`, `get`, `estimate`, and optional GC/update behavior consumed here.
- Expression/object modules integrate through registered ops and callbacks such as `init`, `destroy`, `validate`, `activate`, `deactivate`, `dump`, `clone`, `update`, `select_ops`, and `release_ops`.

## Risks and Edge Cases

- Transaction ordering is delicate. Hooks are registered late on create but some updates register hooks before commit; every failure/abort path must unregister exactly what was registered and release module/use references.
- Generation-mask and RCU mistakes can expose partially initialized objects to dumps or packet traversal, or free objects while readers still hold references.
- Set-element handling has high risk: extension layout uses small offsets, userdata must remain last, duplicate handling can become update/no-op/error depending on backend return codes, and timeout/expiration updates keep old elements alive.
- Recursive validation protects against loops and base-chain jumps. Missing validation triggers on verdict maps or expression changes could admit invalid jump graphs.
- Owner and anonymous binding rules are security relevant. Incorrect owner portid checks, anonymous-set binding, or object/set use counts can allow unauthorized mutation or premature deletion of resources still referenced by rules.
- Netdev prefix matching for base-chain and flowtable hooks can add/remove hooks as devices appear. Rename/unregister races are serialized with commit mutex and rtnl interactions; changes here can cause stale hooks or missed hooks.
- Flowtable hook registration couples `setup(FLOW_BLOCK_BIND)` with net hook registration. Error paths must undo both to avoid offload state leaks.
- Rule blob preparation copies expression memory into datapath blobs and relies on expression sizes and `dlen` limits. Overflow checks and RCU publication are critical for datapath safety.
- The assigned chunk stops before full commit/abort logic, register parsing, and module teardown. Some behavior described here is completed by later code paths outside this chunk.

## Test and Validation Signals

- Netlink API tests should cover create/update/delete/get/dump for tables, chains, rules, sets, elements, objects, and flowtables, including idempotent create, `NLM_F_EXCL`, `NLM_F_REPLACE`, `NLM_F_APPEND`, `NLM_F_NONREC`, handle/name lookup, same-batch IDs, and destroy variants that tolerate missing objects.
- Transaction tests should exercise mixed batches with aborts at each object type, ensuring use counts, module refs, RCU lists, hooks, object hashes, anonymous bindings, and set elements are restored or released.
- Validation tests should include rule jumps/gotos, verdict maps, chained maps, recursion-depth failures, attempted jumps to base chains, and expression validation hooks.
- Set tests should stress interval and concat keys, catchall elements, duplicate element updates, timeout/expiration update paths, object-reference sets, map verdict validation, anonymous constant sets, flush, reset dumps, and backend capacity behavior.
- Netdev and flowtable tests should create netdev base chains and flowtables with exact and prefix device hooks, then register/unregister/rename devices and confirm hook ops follow device lifetime.
- Concurrency signals include lockdep, KASAN/KCSAN, RCU stall warnings, refcount warnings, and nf_tables trace/dump consistency during concurrent dumps and batch commits.
- Notification/audit tests should verify multicast/report behavior, reset audit records, generation notifications, and correct event payloads after commit.
- Datapath tests should confirm committed rule changes rebuild chain blobs correctly, old blobs remain valid through RCU grace periods, and hardware-offload chains create/destroy flow rules on rule add/delete.

### subset-b-006249: lines 10478-12266

# sources/distributed-fs/ceph-client/net/netfilter/nf_tables_api.c lines 10478-12266

## Scope

This chunk covers the tail of `nf_tables_api.c`, starting in the asynchronous set-element garbage-collection transaction worker and ending at module metadata. It includes:

- GC transaction allocation, queuing, catchall-expired-element collection, and race checks against control-plane transactions.
- The nf_tables commit and abort engines that finalize or roll back batched netlink transactions.
- Commit notification batching, audit aggregation, module autoload cleanup, generation-ID validation, and nfnetlink subsystem registration.
- Exported helper APIs for chain dependency/hook validation, u32 netlink parsing, register parsing/dumping/validation, and generic nft data/verdict parsing.
- Per-net namespace initialization/teardown, netlink-port-owner cleanup, module init/exit, and global subsystem wiring.

The source tree path is under a Ceph client snapshot, but this file is generic Linux netfilter/nftables control-plane infrastructure. It does not implement CephFS behavior directly.

## Purpose

This chunk is the transaction and lifetime boundary for nftables. Earlier parts of `nf_tables_api.c` parse netlink requests and append `struct nft_trans` records to the per-net `commit_list`. The code here is responsible for making those requested changes visible to packet processing atomically, or undoing them if validation, generation checks, module autoload, or other batch processing fails.

The commit side converts staged table, chain, rule, set, set-element, object, and flowtable transactions into live ruleset state. It prepares per-chain rule blobs, validates bindings and full ruleset consistency, advances the net namespace generation counter, switches the generation cursor used by packet lookup, emits notifications and audit records, and defers destructive frees through RCU/workqueues.

The abort side walks the transaction list in reverse order and restores the pre-batch state. It handles restored reference counts, reactivation of deleted objects/elements/rules, destruction of newly-created objects, hook unregister rollback, set backend abort hooks, RCU synchronization, and pending module autoload handling.

The GC path coordinates data-plane set timeout cleanup with control-plane mutations. It uses a per-net `gc_seq` odd/even sequence to detect active mutations and to discard stale asynchronous GC batches that raced with ruleset changes or set destruction.

The final helper and lifecycle sections make this implementation consumable by nft expression modules and by netfilter core: they register exported validation/parsing helpers, net namespace operations, netlink-notifier cleanup, the nfnetlink subsystem callbacks, flowtable/netdevice hooks, offload support, object-name hashing, and module init/exit ordering.

## Important APIs, Types, And Functions

Garbage collection transaction handling:

- `nft_trans_gc_work_done()` locks the per-net `commit_mutex`, rejects stale async GC transactions if `nft_net->gc_seq` changed or the target set is dead, and otherwise removes queued expired set elements under transaction protection.
- `nft_trans_gc_work()` drains the global `nf_tables_gc_list` under `nf_tables_gc_list_lock`, then either destroys stale transactions immediately or schedules successful transaction structs for RCU freeing.
- `nft_trans_gc_alloc()` allocates `struct nft_trans_gc`, grabs a net namespace reference with `maybe_get_net()`, increments the set refcount, stores the set and expected GC sequence, and returns the batch container.
- `nft_trans_gc_elem_add()` appends an element-private pointer into the GC transaction's fixed `priv[]` batch.
- `nft_trans_gc_queue_async()` and `nft_trans_gc_queue_async_done()` enqueue full/non-empty async GC batches to the global worker list.
- `nft_trans_gc_queue_sync()` and `nft_trans_gc_queue_sync_done()` perform the same batching for callers already holding `commit_mutex`; these skip workqueue staging and RCU-free completed transaction batches directly.
- `nft_trans_gc_catchall_async()` scans `set->catchall_list` under RCU, marks expired catchall elements dead, batches them, and uses `GFP_ATOMIC`.
- `nft_trans_gc_catchall_sync()` scans catchall elements while the commit lock is held, uses a stable per-net timestamp, deactivates element data, removes the catchall wrapper, and batches the element private data for deferred freeing.

Commit support:

- `nf_tables_module_autoload_cleanup()` frees completed module autoload requests after the transaction list is empty.
- `nf_tables_commit_release()` moves committed transactions from `commit_list` to `destroy_list`, pins the net namespace on the last transaction, schedules `destroy_work`, and releases `commit_mutex`. Empty commits only clean autoload requests and unlock.
- `nft_commit_notify()` batches queued notification SKBs in `nft_net->notify_list`, coalescing messages with the same report flag up to `NLMSG_GOODSIZE`, and sends them to `NFNLGRP_NFTABLES`.
- `nf_tables_commit_audit_alloc()`, `nf_tables_commit_audit_collect()`, `nf_tables_commit_audit_log()`, and helpers aggregate per-table audit data for a committed batch. Set element transactions count by element count rather than transaction count.
- `nft_set_commit_update()` runs backend `set->ops->commit()` once per set on the temporary `set_update_list`, skipping dead sets.
- `nft_gc_seq_begin()` and `nft_gc_seq_end()` bracket mutating control-plane windows. The first increments `gc_seq` to an odd "busy" value; the second increments again to publish a new even stable value.
- `nf_tables_commit()` is the nfnetlink batch commit callback. It validates anonymous set/chain bindings, validates the complete ruleset, commits flow-rule offload state, prepares next-generation chain rule blobs, publishes them, advances `net->nft.base_seq` and `gencursor`, applies every staged transaction, emits notifications/audit/generation events, closes the GC sequence, and releases the commit.

Abort and generation handling:

- `nf_tables_module_autoload()` temporarily drops `commit_mutex` to call `request_module()` for pending autoload requests, then reacquires the lock and restores the request list. It must run after `gc_seq` is updated because it opens a race window.
- `nf_tables_abort_release()` frees transaction-owned resources after rollback, destroying new tables/chains/rules/sets/elements/objects/flowtables or hook lists depending on transaction type and update mode.
- `nft_set_abort_update()` invokes backend `set->ops->abort()` once per set on the rollback update list.
- `__nf_tables_abort()` walks `commit_list` in reverse order and undoes each pending transaction. It restores flags, owner state, use counts, active bits, hook registration, hardware offload temporary rules, set/map/object/flowtable state, and then synchronizes RCU before releasing transaction resources.
- `nf_tables_abort()` wraps rollback with a GC sequence bump, resets table validation state for `NFNL_ABORT_NONE`, handles module autoload or cleanup, unlocks `commit_mutex`, and returns any validation retry signal.
- `nf_tables_valid_genid()` is the nfnetlink generation-ID gate. It takes `commit_mutex`, updates the per-net timestamp, and returns true only for genid 0 or a matching `nft_base_seq(net)`. On success, commit/abort owns the responsibility to unlock.
- `nf_tables_subsys` binds the nftables nfnetlink subsystem to `nf_tables_cb`, `nf_tables_commit`, `nf_tables_abort`, and `nf_tables_valid_genid`.

Exported validation and parsing helpers:

- `nft_chain_validate_dependency()` lets expression/object modules require that a base chain uses a specific chain type, returning `-EOPNOTSUPP` on mismatch.
- `nft_chain_validate_hooks()` verifies that a base chain's hook number is in a caller-provided hook bitmask.
- `nft_parse_u32_check()` reads a big-endian u32 netlink attribute, compares it against a maximum, and stores it on success.
- `nft_parse_register()` maps legacy 128-bit register numbers and newer 32-bit register numbers into the internal 32-bit register index space.
- `nft_dump_register()` performs the inverse mapping for netlink dumps, emitting legacy register numbers when the internal register is 128-bit aligned for compatibility.
- `nft_parse_register_load()` validates source-register loads and rejects reads from registers that have not been initialized in `ctx->reg_inited`.
- `nft_parse_register_store()` validates destination-register stores, enforces verdict/value type compatibility, bounds-checks length against `struct nft_regs`, and marks written registers initialized.
- `nft_data_init()`, `nft_data_release()`, and `nft_data_dump()` parse, release, and dump generic `struct nft_data` values, including verdict data that may hold a chain reference.
- `nft_verdict_init()` parses verdict attributes, validates jump/goto chain targets, rejects base chains and already-bound chains, rejects set-element verdicts that target binding chains, and increments target-chain use counts.
- `nft_verdict_uninit()` decrements jump/goto target-chain use counts.

Namespace, owner, and module lifetime:

- `__nft_release_hook()` unregisters all chain and flowtable net hooks for one table.
- `__nft_release_hooks()` unregisters hooks for all non-owner tables during pre-exit.
- `__nft_release_table()` destroys all rules, flowtables, sets, objects, chains, and finally the table. It skips bound chains during the rule pass and deactivates map/object set payloads before set destruction.
- `__nft_release_tables()` removes and destroys all non-owner tables in a net namespace.
- `nft_rcv_nl_event()` handles `NETLINK_URELEASE` for `NETLINK_NETFILTER`: owner tables for the released portid either become orphaned if persistent or are removed and destroyed after RCU grace periods.
- `nf_tables_init_net()`, `nf_tables_pre_exit_net()`, `nf_tables_exit_net()`, and `nf_tables_exit_batch()` implement per-net initialization and teardown for nftables state.
- `nf_tables_module_init()` registers per-net state, chain filter/core support, netdevice notifier, object-name rhashtable, offload support, netlink notifier, nfnetlink subsystem, and route chain support in dependency order.
- `nf_tables_module_exit()` unregisters the subsystem and notifiers, exits offload/filter/route/pernet support, cancels pending GC work, waits for RCU callbacks, destroys the object-name hash table, and exits core support.

## Control Flow

Asynchronous GC begins when set backend code allocates a `struct nft_trans_gc`, appends expired element private pointers, and calls `nft_trans_gc_queue_async_done()`. The queue path adds non-empty batches to the global `nf_tables_gc_list` and schedules `trans_gc_work`. The worker splices the global list into a local list under a spinlock, then processes each batch while holding the target net namespace's `commit_mutex`. The important race check is `READ_ONCE(nft_net->gc_seq) != trans->seq || trans->set->dead`: if any control-plane transaction bracket changed the sequence, or the set was destroyed, the GC batch is stale and is destroyed without touching the set. Successful GC removal calls into the prior helper `nft_trans_gc_setelem_remove()` and frees the transaction via RCU.

Synchronous GC uses the same transaction container but requires `commit_mutex` by lockdep check. When a batch fills, it is sent directly to `call_rcu()` rather than put on the global work list because the caller is already in the serialized mutation path. Catchall handling has separate async and sync variants. The async variant marks expired elements dead under RCU and batches them. The sync variant, used under commit lock, checks expiry against `nft_net_tstamp()`, deactivates element data, removes the catchall list node, and then batches the element for deferred free.

Commit flow starts through nfnetlink after `nf_tables_valid_genid()` has accepted the request generation and left `commit_mutex` held. Empty commits just unlock. Non-empty commits first create a fresh `nft_ctx` from the netlink header and reject unbound anonymous sets or binding chains left on `binding_list`. It then validates the complete ruleset. Validation failure sets `validate_state` to `NFT_VALIDATE_DO` and returns `-EAGAIN`, allowing the batch machinery to roll back and retry validation/reporting.

Before making changes irreversible, `nf_tables_commit()` commits pending flow-rule offload state and prepares next-generation chain rule blobs for every rule add/delete transaction. Preparation failure cancels all prepared chain blobs and frees audit bookkeeping. Once preparation succeeds, every chain in every table publishes its prepared blob through `nf_tables_commit_chain()`. Only after that does the function advance `net->nft.base_seq` with release semantics, begin a GC busy sequence, and switch `net->nft.gencursor` to the next generation. The comment marks this as the point after which commit cannot fail.

Transaction application is a single forward pass over `commit_list`. For new tables/chains/sets/objects/flowtables, the code distinguishes updates from first-time creation. Updates commit flag or hook/name/stat changes and may keep the transaction object for RCU destruction; creations clear the inactive bit with `nft_clear()`, notify userspace, and destroy the transaction immediately when safe. Deletions remove objects from RCU-visible lists, unregister hooks where needed, deactivate rule expressions or set element data, and leave transaction resources for deferred destruction.

Rules are special because packet evaluation uses compact rule blobs. The chain prepare/publish phase has already made the new blob visible; the transaction pass then clears new rules, deletes old rules from the list, sends notifications, deactivates expressions on committed delete, and releases temporary hardware offload rules for offloaded chains.

Set element transactions are applied through `nft_trans_elems_add()` and `nft_trans_elems_remove()`. If a set backend has a `commit()` method, the set is placed on a per-commit `set_update_list` only once. After all transactions have been applied, `nft_set_commit_update()` runs backend commits, then notification SKBs are sent, a generation notification is emitted, audit records are logged with the final generation ID, the GC sequence is closed, validation state is reset to skip, and `nf_tables_commit_release()` moves transactions to async destruction and unlocks.

Abort flow reverses the commit-list order to preserve dependency unwinding. `nf_tables_abort()` begins a GC busy sequence, calls `__nf_tables_abort()`, then closes the GC sequence before any module autoload unlock/relock window. Optional validation can happen first for `NFNL_ABORT_VALIDATE`, returning `-EAGAIN` if the currently visible ruleset still needs validation handling.

Rollback actions mirror commit actions but restore the prior state. New tables are removed from the table list or update flags are reverted; deleted tables are cleared back to active. New chains unregister newly installed hooks, free updated hook/stat/name staging, or remove entirely with restored table use counts. Deleted chains restore table use and clear inactive state. New rules restore chain use count, delete the rule, and deactivate expressions with `NFT_TRANS_ABORT`; deleted rules restore chain use, reactivate expressions, and clear inactive state. New sets remove `list_trans_newset`, restore table use, mark unbound new sets dead, and remove them from the table. Deleted sets restore use, clear active state, and reactivate maps if needed. New set elements call `nft_trans_elems_new_abort()` and queue backend abort; deleted elements call `nft_trans_elems_destroy_abort()`. Objects and flowtables similarly restore table use, list membership, hooks, and update staging.

After rollback, the code warns if `commit_set_list` is non-empty, runs backend set abort hooks, calls `synchronize_rcu()`, removes every transaction from `commit_list`, and frees transaction-owned new resources through `nf_tables_abort_release()`. The public abort wrapper then either requests modules for `NFNL_ABORT_AUTOLOAD` or cleans request records, unlocks `commit_mutex`, and returns.

Data and register helper flow is mostly parser validation. Register loads require a valid source register range and also consult `ctx->reg_inited`; this prevents expressions from reading registers that no earlier expression in the rule wrote. Register stores require verdict data for `NFT_REG_VERDICT` and value data for payload registers, check non-zero length and bounds, then mark the register range initialized. Generic data parsing accepts either a raw value or a nested verdict, but verdict parsing is only allowed with a non-NULL `ctx` because chain lookup and use-count management need table/net context.

Net namespace teardown is split to avoid packet-path use-after-free. Pre-exit unregisters hooks for non-owner tables while holding `commit_mutex`. Exit begins a GC busy sequence, warns about impossible pending commit/set state, cleans module autoload records, cancels the per-net destroy work, releases all non-owner tables, closes the GC sequence, unlocks, and checks that per-net lists are empty. A batch exit hook flushes global GC work. Separately, netlink port release events remove tables owned by the dead portid unless they are persistent, in which case owner state is stripped and the table survives as an orphan.

Module initialization is ordered so dependencies come up before userspace can send nfnetlink nftables messages. The nfnetlink subsystem registration is explicitly last. Error unwinding unregisters in reverse order. Module exit unregisters nfnetlink first, then netlink/netdevice/offload/filter/route/pernet facilities, cancels GC work, waits for RCU callbacks, and destroys the object-name hash after users are gone.

## State And Persistence Behavior

All state in this chunk is in-memory kernel networking state. There is no filesystem persistence.

Key persistent-in-memory state includes:

- `struct nftables_pernet`: owns `tables`, `commit_list`, `destroy_list`, `commit_set_list`, `binding_list`, `module_list`, `notify_list`, `commit_mutex`, `gc_seq`, `validate_state`, `tstamp`, and `destroy_work`.
- `net->nft.base_seq`: the ruleset generation ID used by dumps, batch generation checks, and packet-path invalidation. Commit skips zero and publishes the new value with `smp_store_release()`.
- `net->nft.gencursor`: selects which generation bit is current for active/inactive nft objects after commit.
- `nft_net->gc_seq`: odd values indicate a mutation window; async GC transactions only apply if their saved sequence still matches and the set is not dead.
- `commit_list`: staged `struct nft_trans` objects allocated by netlink request handlers. Commit moves them to `destroy_list` for asynchronous cleanup, while abort removes and frees them after RCU synchronization.
- `destroy_list` and `destroy_work`: defer expensive/freeing side effects until after the commit has made all logical state visible and released the commit lock.
- `notify_list`: holds notification SKBs built during transaction processing and flushed after a successful commit.
- `module_list`: holds pending expression/object/set module requests; autoload can temporarily release `commit_mutex`.
- Per-object flags and use counts: `NFT_TABLE_F_DORMANT`, owner/orphan flags, `__NFT_TABLE_F_UPDATE`, `set->dead`, chain/rule/set/object active bits, table/chain/set/object use counts, hook lists, flowtable flags, and pending set update list nodes.
- `ctx->reg_inited`: an expression-construction bitmap tracking which registers have been written before later loads in a rule.

RCU is central to persistence and visibility. Committed deletes remove list nodes with `list_del_rcu()`, publish new rule blobs before flipping the generation cursor, free old blobs and GC transaction objects through `call_rcu()`, and use `synchronize_rcu()` during abort and owner-table deletion before destroying objects that readers may still see.

The code deliberately separates logical visibility from memory reclamation. `nf_tables_commit_release()` comments that side effects, such as a deleted chain name becoming unavailable to the next transaction, must be visible immediately, while memory reclaim is asynchronous to avoid a costly `synchronize_rcu()` in the commit phase.

## Dependencies And Integration Points

This chunk depends on core netfilter/nftables types and helpers defined earlier in the same file and in nftables headers:

- `struct nft_trans` plus typed containers for tables, chains, rules, sets, set elements, objects, and flowtables.
- `struct nft_ctx`, `struct nft_table`, `struct nft_chain`, `struct nft_rule`, `struct nft_set`, `struct nft_object`, `struct nft_flowtable`, `struct nft_trans_elem`, and `struct nft_trans_gc`.
- Transaction helpers such as `nft_trans_destroy()`, `nft_trans_list_del()`, `nft_clear()`, `nft_use_inc_restore()`, `nft_use_dec_restore()`, `nft_trans_*()` accessors, and typed destroy/release functions.
- Rule blob helpers `nf_tables_commit_chain_prepare()`, `nf_tables_commit_chain()`, and cancellation/free paths from the immediately preceding code.
- Set element helpers such as `nft_trans_elems_add()`, `nft_trans_elems_remove()`, `nft_trans_elems_new_abort()`, `nft_trans_elems_destroy_abort()`, `nft_setelem_data_deactivate()`, and catchall helpers.

It integrates with nfnetlink through `nf_tables_subsys`. The callbacks in `nf_tables_cb` parse individual messages, while this chunk supplies the batch `commit`, `abort`, and `valid_genid` operations. Notification output uses `nfnetlink_send()` to `NFNLGRP_NFTABLES` and generation notifications through `nf_tables_gen_notify()`.

It integrates with the kernel audit subsystem through `audit_log_nfcfg()` and `nft2audit_op`, producing per-table audit records summarizing the committed operation and entry count.

It integrates with kernel module loading through `request_module()` and the per-net `module_list`. The autoload path intentionally drops `commit_mutex`, so GC sequence and validation state ordering around it are part of the transaction contract.

It integrates with netdevice and flowtable infrastructure through hook registration/unregistration helpers, `nf_tables_flowtable_notifier`, `nft_flow_rule_offload_commit()`, `nft_offload_init()/exit()`, `nft_flow_rule_destroy()`, and flowtable net hook cleanup.

It integrates with net namespace lifecycle through `pernet_operations` registration, with netlink socket lifecycle through `netlink_register_notifier()` and `NETLINK_URELEASE`, and with RCU/workqueue infrastructure through `call_rcu()`, `synchronize_rcu()`, `flush_work()`, and per-net/global work items.

The exported symbols in this chunk are used by nft expression/object modules outside this file. Register and data helpers enforce common netlink ABI behavior, target-chain reference accounting, and expression construction safety for modules that parse expression attributes.

## Risks And Edge Cases

GC and control-plane transaction races are a major risk. Async GC batches carry raw element private pointers, so applying them after a set was destroyed or after any transaction changed the ruleset would risk stale pointer use. The `gc_seq` and `set->dead` checks are therefore critical, and any path that mutates sets without bracketing `gc_seq` would weaken this protection.

Commit has a hard no-fail boundary after rule blobs are published and `base_seq` is advanced. All allocation, validation, offload commit, and chain prepare work must happen before that point. Adding new transaction types or side effects after this boundary must avoid errors or provide preallocation/validation earlier.

Commit and abort must stay mirror images. Reference counts, active bits, hook lists, hardware offload temporary rules, flowtable flags, dormant/owner/orphan flags, and backend set commit/abort hooks have paired behavior. A mismatch can leak references, expose stale hooks, double-free staged resources, or leave objects visible in the wrong generation.

Binding validation protects anonymous sets and binding chains from being committed unbound. Missing this check would allow invalid ruleset objects with unclear ownership/lifetime and potential later deletion/use-count failures.

RCU ordering is delicate. Deletes use `list_del_rcu()` and defer freeing, abort uses `synchronize_rcu()` before release, netlink owner cleanup batches up to eight tables and synchronizes before destruction, and module exit waits with `rcu_barrier()`. Reordering these can create packet-path use-after-free or module-unload races.

Notification batching assumes that SKBs in `notify_list` can be concatenated when their report flags match and size remains below `NLMSG_GOODSIZE`. Incorrect length accounting or mixing report modes could corrupt netlink messages or misdeliver notifications.

Audit aggregation stores table pointers and logs after commit application. Transactions that destroy tables are still represented by transaction/destroy-list lifetime, so changing when table memory is freed could invalidate audit logging.

Module autoload temporarily releases `commit_mutex`. The code updates GC sequence before autoload and restores/cleans module-list entries afterward. New shared state touched around autoload must tolerate another actor observing the partially aborted transaction state only through the intended retry path.

Generation-ID validation intentionally leaves the mutex locked on success. Callers must always pair successful `valid_genid` with commit or abort. Incorrect direct use would deadlock nftables control-plane operations.

Register validation prevents uninitialized register reads during rule construction. Expressions that bypass `nft_parse_register_load()` or fail to call `nft_parse_register_store()` for writes can undermine this static safety check and allow runtime reads of undefined register contents.

Verdict data holds chain references. Every successful `nft_verdict_init()` for jump/goto must be paired with `nft_data_release()`/`nft_verdict_uninit()` on error paths and object destruction; otherwise chain use counts leak and chain deletion can return busy forever.

Netlink owner cleanup deletes tables in small batches. The restart path is required when more than eight tables are owned by one portid. Persistent tables clear owner state and survive; non-persistent tables unregister hooks before list removal and table destruction after RCU.

Module init ordering is security-relevant because nfnetlink registration exposes userspace entry points. It is deliberately last; moving it earlier could permit requests before per-net, offload, notifier, or hash-table infrastructure is ready.

## Test Signals

Useful validation signals for this chunk include:

- Kernel build coverage with nftables, nfnetlink, module autoload, flowtable/offload, netdev family, audit, and namespace teardown configurations enabled.
- Transaction tests for empty commit, successful multi-object batch commit, validation failure returning `-EAGAIN`, generation-ID mismatch, and retry behavior.
- Commit tests covering table create/update/delete/destroy, dormant table enable/disable, owner/orphan flags, base sequence changes, generation notifications, and audit records.
- Chain tests covering base-chain hook update, binding-chain validation, hook unregister on delete, name/hash update, policy/stat update, and abort restoration.
- Rule tests covering add/delete in the same and different chains, next-generation rule blob preparation failure, hardware offload temporary rule destruction, expression deactivate/reactivate behavior, and packet-path continuity during generation switch.
- Set tests covering anonymous unbound rejection, set update of timeout/gc interval/size, set deletion marking `dead`, set backend `commit()` and `abort()` called once per batch, and map/object set activation/deactivation.
- Set element tests covering multi-element audit counts, add/remove/destroy commit, add/remove abort, catchall element expiry, sync and async GC, full GC batch rollover, stale `gc_seq` discard, and destroyed-set GC discard.
- Object and flowtable tests covering new/update/delete/destroy commit and abort, object replacement cleanup, flowtable hook update rollback, flowtable flag updates, net hook unregister, and netdevice notifier interaction.
- Notification tests verifying `notify_list` batching by report flag, `NLMSG_GOODSIZE` splitting, generation notification emission, and no leaked notification SKBs after commit or namespace exit.
- Audit tests verifying one record per touched table, correct operation mapping, correct set-element entry counts, and stable table name/generation formatting for table deletion batches.
- Module autoload tests for missing expression/object/set modules, `NFNL_ABORT_AUTOLOAD`, mutex unlock/relock race behavior, completed request cleanup, and no leftover `module_list` entries after abort/commit/namespace exit.
- Register parser tests for legacy and 32-bit register encodings, invalid register ranges, zero-length loads/stores, bounds overflow, uninitialized load returning `-ENODATA`, verdict/value type mismatches, and dump compatibility.
- Data/verdict parser tests for raw values, fixed-length values, oversize/zero-length values, jump/goto by name and ID, missing chain target, base-chain rejection, bound-chain rejection, set-element binding-chain rejection, `NF_QUEUE` rejection, use-count increment/decrement, and dump output.
- Net namespace tests for init defaults (`base_seq = 1`, `gc_seq = 0`, validation skip), pre-exit hook unregister, exit cleanup with pending destroy work, global GC flush in exit batch, and empty-list warnings.
- Netlink owner tests for owner table deletion on `NETLINK_URELEASE`, persistent owner table orphaning, batch deletion of more than eight tables, and RCU-safe destruction after hook release.
- Module init/exit tests or fault-injection tests for each init failure label: pernet registration, chain filter, core module, netdevice notifier, object-name rhashtable, offload, netlink notifier, nfnetlink subsystem registration, and reverse-order cleanup.
