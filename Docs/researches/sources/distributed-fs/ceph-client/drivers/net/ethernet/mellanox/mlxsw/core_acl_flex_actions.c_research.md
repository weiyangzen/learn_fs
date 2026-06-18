# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_acl_flex_actions.c

## Purpose
`core_acl_flex_actions.c` builds and owns encoded ACL flexible action blocks for mlxsw devices. It turns high-level actions such as drop, trap, mirror, forward, VLAN rewrite, QoS rewrite, counters, policers, FID set, ignore, multicast router, NAT IP/L4 rewrites, and sampling into hardware action-set byte encodings. It also deduplicates action sets and hardware resources so multiple rules can share KVD linear entries, forwarding entries, cookies, and policers.

## Important APIs, Types, And Functions
- `struct mlxsw_afa` owns action-builder global state: maximum actions per set, hardware operations, operation private pointer, rhashtables for encoded sets/forwarding entries/cookies/policers, an IDR for cookie indexes, and a policer list.
- `struct mlxsw_afa_set` represents one encoded action set (`MLXSW_AFA_SET_LEN`) with hash key, KVDL index, first-set marker, trap/police flags, refcount, and pre-commit `prev`/`next` links.
- `struct mlxsw_afa_block` is a rule action chain. It owns the first/current set, current action index, finished flag, and a resource destructor list.
- `struct mlxsw_afa_ops` callbacks allocate/delete KVDL action sets and forwarding entries, read activity, allocate/free counters, create/delete mirrors, policers, and samplers.
- Creation/destruction APIs are `mlxsw_afa_create()`, `mlxsw_afa_destroy()`, `mlxsw_afa_block_create()`, `mlxsw_afa_block_destroy()`, and `mlxsw_afa_block_commit()`.
- Block terminal APIs are `mlxsw_afa_block_continue()`, `mlxsw_afa_block_jump()`, and `mlxsw_afa_block_terminate()`.
- Exported append APIs encode specific actions: `mlxsw_afa_block_append_vlan_modify()`, `drop()`, `trap()`, `trap_and_forward()`, `mirror()`, `fwd()`, QoS DSCP/ECN/switch-priority helpers, allocated/new counters, `police()`, `fid_set()`, `ignore()`, `mcrouter()`, `ip()`, `l4port()`, and `sampler()`.
- `mlxsw_afa_cookie_lookup()` maps a hardware user-defined cookie index back to a `flow_action_cookie` under RCU.

## Control Flow
An AFA instance is created with operation callbacks and initialized rhashtables. A caller creates an action block, appends actions, terminates or jumps/continues the binding, commits the block, and later destroys it. A block always starts with at least one pass-by-default set; if `dummy_first_set` is requested, the first set remains empty and the second set carries real actions.

Appending an action calls `mlxsw_afa_block_append_action_ext()`. It rejects already finished blocks, creates a new set if the action would exceed `max_acts_per_set`, and also splits when trap and police actions would otherwise share a set, working around a hardware limitation. It marks trap/police presence, advances the set action cursor, writes the action type, and returns the payload area for the action-specific packer.

Commit walks from the current set backward. For each set it looks for an identical encoded set in `set_ht`; if found it bumps the refcount and discards the duplicate, otherwise it calls `ops->kvdl_set_add()` and inserts the new set into the hash. Previous sets are patched with `NEXT` pointers to the committed KVDL index of their successor. The first set is returned directly to rules; subsequent sets live in KVD linear memory.

Actions requiring hardware resources allocate a resource object before appending and link it onto the block's resource list. On append failure the resource is immediately destroyed; on block destruction every registered destructor releases its resource. Forwarding entries are keyed by local port and backed by KVDL PBS entries. Cookies are keyed by raw `flow_action_cookie`, assigned 20-bit nonzero IDR indexes, and freed with RCU. Policers are keyed by flow-action index and kept in both a rhashtable and list. Mirrors and samplers call span/psample callbacks and store returned span IDs.

## State And Persistence Behavior
AFA state is in-memory plus hardware resources allocated through `mlxsw_afa_ops`. Encoded action sets and forwarding entries persist in hardware KVD linear space until their refcounts drop to zero. Cookie indexes persist in the instance IDR while any block references them. Counter, mirror, policer, and sampler resources persist until block destruction. `mlxsw_afa_destroy()` warns if policers or cookies remain, which catches leaked block/resource references.

## Dependencies And Integration Points
The file depends on Linux rhashtable, IDR, refcount, RCU, flow offload cookies, psample groups, and netlink extack. It uses local item-field helpers to define and pack hardware bitfields, and local trap IDs for ACL discard trap actions. Device-specific allocation and deletion are intentionally delegated through `struct mlxsw_afa_ops`, allowing Spectrum implementations to map these abstract actions to their KVDL/counter/mirror/policer/sampler facilities.

## Risks And Edge Cases
- Hash keys include the whole encoded set and `is_first`; uninitialized bytes would break deduplication, so sets are zero-allocated and packers must only write defined fields.
- `mlxsw_afa_block_first_kvdl_index()` warns if there is no second set; callers must only request activity for blocks with KVDL-backed continuation.
- Drop-with-cookie uses a 20-bit IDR range and reserves index zero; exhaustion returns an error and must propagate to flow offload.
- Police and trap splitting is required for hardware correctness. New trap-like or police-like actions must use the correct action type.
- Forward-to-ingress-port is explicitly unsupported and returns `-EOPNOTSUPP`.
- Resource destructors depend on block lifetime. Destroying an AFA instance before all blocks are destroyed leaves warnings and potential hardware resource leaks.
- Cookie lookup requires RCU read-side protection because cookies are freed with `kfree_rcu()`.

## Test Signals
Exercise block creation, append, commit, and destruction with single-set and multi-set action chains; duplicate blocks should share KVDL entries and refcounts. Validate trap+police splitting, dummy-first-set behavior, cookie allocation/lookup/free under RCU, policer reuse by `fa_index`, mirror/sampler cleanup on append errors, sampler rate limit rejection, counter allocation/free pairing, and extack strings on expected failures.
