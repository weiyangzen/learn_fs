# sources/distributed-fs/openafs/src/kauth/kadatabase.c

## Purpose
Implements low-level KA database storage management over Ubik transactions. It initializes and validates the database header, allocates and frees fixed-size records, maintains name hash chains, iterates entries, manages special-server old-key records, and maintains an in-memory server-key cache.

## Important APIs, Types, And Functions
Important functions include `NameHash`, `kawrite`, `karead`, `init_kadatabase`, `CheckInit`, `AllocBlock`, `FreeBlock`, `FindBlock`, `ThreadBlock`, `UnthreadBlock`, `NextBlock`, `ka_NewKey`, `ka_DelKey`, `ka_debugKeyCache`, `ka_Encache`, `ka_LookupKvno`, `ka_LookupKey`, `ka_FillKeyCache`, `update_admin_count`, and `name_instance_legal`. Internal state includes `keycache_lock`, `keyCache`, `keyCacheVersion`, `maxCachedKeys`, `maxKeyLifetime`, and `dbfixup`.

## Control Flow
`CheckInit` delegates to `ubik_CheckCache`, whose callback reads the KA header, verifies both initial and terminal version fields, caches `cheader`, and optionally rebuilds an empty database. Allocation either pops `cheader.freePtr` or extends `eofPtr`; freeing writes a `KAFFREE` block and threads it onto the free list. Name lookup hashes name+instance and walks `cheader.nameHash`. Thread/unthread modify either the header hash bucket or a prior entry's `next` field. Old-key management scans the global `kvnoPtr` chain, supersedes current keys, drops expired or colliding kvnos, creates old-key blocks as needed, and increments `specialKeysVersion` to invalidate key caches.

## State And Persistence
Persistent state is the Ubik database: `kaheader`, fixed 200-byte `kaentry`/`kaOldKeys` records, free-list, EOF pointer, name hash table, admin count, stats, and old-key chain. Runtime state is a growable key cache guarded by `keycache_lock`. Fields on disk are mostly network byte order.

## Dependencies And Integration Points
This file is used by `kaprocs.c` and `kaserver.c` for every account and key operation. It depends on Ubik transaction APIs, Rx locks, kauth generated definitions, server layout from `kaserver.h`, and utility functions for debugging.

## Risks And Test Signals
Risks include fixed on-disk layout coupling, mixed byte-order handling, cache invalidation correctness, `realloc` fatal exit on allocation failure, a likely misleading expired-key log after zeroing fields, and lookup behavior that treats NULL instance as wildcard. Test signals include database creation, create/delete/list/get-entry round trips, hash-chain integrity, free-list reuse, old-key rollover and lookup by kvno, cache invalidation after special key changes, and corruption handling through `CheckInit`.
