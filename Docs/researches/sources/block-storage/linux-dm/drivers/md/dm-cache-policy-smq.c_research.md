# File Research: sources/block-storage/linux-dm/drivers/md/dm-cache-policy-smq.c

Implements the stochastic multi-queue (`smq`) cache replacement policy plus `mq`, `cleaner`, and `default` registrations. It uses compact indexed `entry` objects instead of pointers: entries carry hash/list links, level, dirty/allocated/sentinel/pending flags, and origin block.

Core data structures include indexed intrusive lists, multi-level queues, hash tables for cache and hotspot lookup, entry allocators, clean/dirty/cache/hotspot queues, hit bitsets, confidence stats, rotating sentinels, and a background work tracker. The hotspot queue tracks larger origin regions to decide promotion candidates; clean and dirty queues track actual cache residency.

Lookup first checks the cache hash table, requeues hits upward once per period, and returns the cache block. Misses update the hotspot queue; if the hotspot entry reaches read/write promotion thresholds, the policy queues promotion work. If no cache entries are free, promotion attempts can trigger demotion work to maintain free space.

Background work includes promotions, demotions, and writebacks. Promotions reserve a cache entry immediately and complete by either installing it into hash/queue or freeing it on failure. Demotions remove clean entries on success or requeue them on failure. Writebacks clear pending state and requeue entries, while dirty/clean transitions move entries between dirty and clean queues.

Periodic `tick()` rotates writeback/demotion sentinels, clears hit bitsets, redistributes queue levels, resets stats, and adjusts hotspot promotion aggressiveness. `cleaner` disables migrations, making the policy focus on writeback/cleaning behavior. `mq` is an alias-compatible mode that accepts old tunables but warns they no longer have effect.
