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
