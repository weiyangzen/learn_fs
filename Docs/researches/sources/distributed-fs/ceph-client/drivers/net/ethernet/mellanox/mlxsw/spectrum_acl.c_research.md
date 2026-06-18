<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl.c

## Purpose

`spectrum_acl.c` is the high-level ACL manager for the Spectrum driver. It owns AFK creation, dummy FID lifetime, ACL ruleset/rule hash tables, TC flower and multicast-router rule APIs, action construction helpers, statistics, and periodic rule activity polling. It bridges Linux flow blocks and flow actions to hardware-profile operations implemented below `spectrum_acl_tcam.c`.

## Important APIs, Types, And Functions

- `struct mlxsw_sp_acl` stores the AFK handle, dummy FID, ruleset hash table, global rule list, delayed activity work, and TCAM state.
- `struct mlxsw_sp_acl_ruleset` is keyed by flow block, chain index, and profile ops; it owns a rule hash table, refcount, priority range, and profile-private storage.
- `struct mlxsw_sp_acl_rule` stores cookie, ruleset pointer, `rulei`, last-used/stats baselines, and profile-private entry storage.
- Ruleset APIs include `mlxsw_sp_acl_ruleset_get()`, `lookup()`, `put()`, `bind()`, `unbind()`, `group_id()`, and priority query.
- Rule-info APIs build match keys and actions: key/mask setters, `commit()`, continue/jump/terminate/drop/trap/fwd/mirror/vlan/priority/mangle/police/count/fid/ignore/sample.
- Rule APIs include `mlxsw_sp_acl_rule_create()`, `add()`, `del()`, `destroy()`, `lookup()`, `action_replace()`, and `get_stats()`.
- `mlxsw_sp_acl_init()` and `mlxsw_sp_acl_fini()` own subsystem lifetime.

## Control Flow

Rulesets are looked up or created by profile. Creation allocates profile-private storage, initializes the per-ruleset rule hash table, calls profile `ruleset_add()`, then inserts into the ACL ruleset hash. The first rule added to chain 0 causes the ruleset to bind to all existing flow-block bindings; nonzero chains are reached by jump actions instead of direct port binding. Rule add calls profile `rule_add()`, inserts the cookie into the ruleset hash, updates the global activity list, and increments flow-block counters and ingress/egress bind blockers. Rule delete reverses these steps and unbinds chain 0 when the ruleset becomes singular again.

Action helpers append operations to an AFA block and record state needed for cleanup or stats. Spectrum-1 only supports QoS mangle fields, while Spectrum-2 also supports L4 port and IP address mangling. IPv6 address mangles must arrive in expected odd/even 32-bit pairs so the helper can emit one hardware action per 64-bit half. Periodic delayed work walks the global rule list under `rules_lock`, asks profile `rule_activity_get()` for each rule, and updates `last_used`. Stats read counters and policer drop counters, return deltas since the previous read, and update the cached baselines.

## State And Persistence

All persistent driver state is memory-resident and refcounted. Hardware state is delegated through profile ops and AFA/KVDL/counter/policer/span helpers. The dummy FID is held while ACL is initialized. The delayed work reschedules itself until finalization cancels it. Rule stats are cumulative in hardware but exposed as deltas by cached last packet/byte/drop values in `struct mlxsw_sp_acl_rule`.

## Dependencies And Integration Points

This file integrates Linux flow block binding, TC actions, AFK flexible keys, AFA flexible actions, flow counters, policers, SPAN/mirror/sampling, port range register allocation, dummy FID handling, and profile ops from the TCAM layer. It is called by TC flower offload, multicast routing, and other Spectrum policy paths that need ACL rule construction.

## Risks

- Ruleset binding is conditional on chain 0 and refcount shape; refcount bugs can bind too early, leave ports unbound, or leak rulesets.
- IPv6 mangle pairing is order-sensitive and rejects unexpected ordering.
- The global activity worker can report and reschedule through transient hardware errors; repeated errors are logged but do not stop the worker.
- Stats are delta-based and mutate cached baselines on read, so callers must not expect idempotent reads.
- Cleanup depends on every rule being deleted before `mlxsw_sp_acl_fini()`, which warns on a non-empty list.

## Test Signals

Test TC flower add/delete across ingress and egress, shared flow blocks, chain jumps, rule replacement rejection for flower, mangle field coverage on Spectrum-1 versus Spectrum-2, mirror/sample single-source validation, policer/count stats deltas, activity timestamps, and failure unwinds for profile rule insertion and binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl.c -->
