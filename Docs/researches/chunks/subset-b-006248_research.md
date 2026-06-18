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
