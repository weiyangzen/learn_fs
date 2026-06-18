# sources/distributed-fs/lizardfs/src/common/generic_lru_cache.h

Purpose: implements a generic fixed-capacity LRU-style cache that stores large keys once.

Important APIs/types/functions: `GenericLruCache<Key,Value,DefaultCapacity,Hasher,Comparator>`, `Queue` list of key/value pairs, `CacheMap` from `reference_wrapper<const Key>` to queue iterator, `insert`, rvalue insert, `emplace`, `clear`, `size`, `find`, `findByValue`, and iterators.

Control flow: inserts evict the queue back when at capacity, then check map existence, push new entries to the front, and insert a map reference to the list key. Finds use the map and splice found entries to the front. `findByValue` scans the list and also promotes the result.

State and persistence: in-memory list plus unordered map. No persistence or synchronization.

Dependencies and integration: depends on `<list>`, `<unordered_map>`, `<functional>`, and `<algorithm>`. It is suitable for caches with expensive key copies.

Risks: if `capacity_` is zero, insert tries to access `queue_.back()` on an empty list. The code evicts before checking whether the key already exists, so inserting an existing key at full capacity can evict an unrelated entry and then return the old entry without updating value. `reference_wrapper` keys require list node keys to outlive map entries, which is maintained only if erase/pop paths stay correct.

Test signals: no direct tests in this subset.
