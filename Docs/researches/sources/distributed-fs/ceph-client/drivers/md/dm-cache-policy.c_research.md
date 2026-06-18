# sources/distributed-fs/ceph-client/drivers/md/dm-cache-policy.c

## Purpose
`dm-cache-policy.c` implements the registry and factory for DM cache policy modules. It lets policy implementations register named types, supports module auto-loading by policy name, pins owner modules while policies are live, and exposes policy identity helpers.

## Important APIs, Types, and Functions
The private registry is `register_list` protected by `register_lock`. Public functions are `dm_cache_policy_register()`, `dm_cache_policy_unregister()`, `dm_cache_policy_create()`, `dm_cache_policy_destroy()`, `dm_cache_policy_get_name()`, `dm_cache_policy_get_version()`, and `dm_cache_policy_get_hint_size()`. Internal helpers include `__find_policy()`, `__get_policy_once()`, `get_policy_once()`, `get_policy()`, and `put_policy()`.

## Control Flow
Policy creation looks up a registered type under the spinlock and tries to get its module reference. If missing, it calls `request_module("dm-cache-%s", name)` and retries. It then invokes the type's `create()` method and stores the policy type in `p->private`. Destroy calls the policy's `destroy()` method and drops the module reference. Registration rejects duplicate names and hint sizes other than 0 or 4 bytes.

## State and Persistence
The registry state is in-memory only. The policy type pointer stored in each policy object is runtime state used for destroy and identity access. Persistent metadata uses the name, version, and hint size returned by this registry path to validate saved hints.

## Dependencies and Integration Points
The file depends on Linux module loading/refcounting, lists, spinlocks, slab error conventions, DM logging, and the policy structs from `dm-cache-policy-internal.h`. SMQ and other policy modules register through this API; the cache target creates selected policies through it.

## Risks and Edge Cases
Owner module pinning can fail, in which case lookup returns an error-like pointer internally and creation reports unknown policy. Alias policy types use `real` so `dm_cache_policy_get_name()` returns the real policy name for metadata compatibility, while version currently comes from the alias type. Unregister does not wait for live users itself; correctness depends on module references taken during create.

## Test Signals
Useful signals include duplicate registration rejection, invalid hint-size rejection, auto-loading by policy name, create/destroy balancing module refs, alias name reporting for `default`, and clean unregister after policy module unload.
