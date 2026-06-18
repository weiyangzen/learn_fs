# File Research: sources/block-storage/linux-dm/drivers/md/dm-cache-policy.c

Implements the registry for DM cache policy plugins. A global spinlock protects a list of `dm_cache_policy_type` records. Registration rejects duplicate names and only accepts hint sizes of 0 or 4 bytes.

Policy lookup first searches the in-memory registry and takes the owner module reference with `try_module_get()`. If absent, it calls `request_module("dm-cache-%s", name)` and retries. Creation calls the policy type's `create()` method and stores the type pointer in `policy->private`.

Destruction calls the policy object's destroy method and releases the module reference. Query helpers return the effective policy name, version, and hint size; aliases report their real policy name when `type->real` is set.

The file exports register/unregister/create/destroy/query symbols for policy modules and cache core code.
