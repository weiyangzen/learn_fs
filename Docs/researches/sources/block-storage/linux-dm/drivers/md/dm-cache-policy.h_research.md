# File Research: sources/block-storage/linux-dm/drivers/md/dm-cache-policy.h

Defines the public cache policy interface. `enum policy_operation` and `struct policy_work` describe migration work requested by policies: promote, demote, or write back an origin/cache block pair.

`struct dm_cache_policy` is a vtable embedded in policy-specific objects. It supports lookup, optional immediate lookup-with-work, background work issue/complete, dirty state updates, initial mapping load, mapping invalidation, hint retrieval, residency reporting, optional periodic ticks, config emission/set, and migration enable/disable.

`struct dm_cache_policy_type` describes a registered policy module: name, version, optional alias target, hint size, owner module, and create callback. Names are limited to 16 bytes and versions to three integers.

The comments define important behavioral contracts: lookup must not block; background completion must use the original work pointer; hints are per-cache-block policy state; and policy registration is separate from policy object lifetime.
