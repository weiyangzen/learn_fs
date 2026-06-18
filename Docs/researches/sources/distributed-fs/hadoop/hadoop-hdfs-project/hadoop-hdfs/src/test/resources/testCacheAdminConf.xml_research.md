# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/testCacheAdminConf.xml

## Purpose

`testCacheAdminConf.xml` is the HDFS cacheadmin CLI test definition. The complete 580-line file was read. It defines 22 test cases for `hdfs cacheadmin` usage, cache pool lifecycle, directive lifecycle, filtering, statistics, TTL/limit formatting, and replication override behavior.

## Important APIs, Types, and Functions

The XML uses `<cache-admin-command>` entries inside the CLI test schema. Commands include bare usage, `-listPools`, `-addPool`, `-modifyPool`, `-removePool`, `-addDirective`, `-modifyDirective`, `-removeDirective`, `-removeDirectives`, `-listDirectives`, `-help addPool`, `-stats`, `-id`, `-pool`, `-path`, `-ttl`, `-limit`, `-maxTtl`, `-owner`, `-group`, `-mode`, and `-defaultReplication`. Comparators are mostly `SubstringComparator`, checking stable text tables and result counts.

## Control Flow

The tests start with usage and empty pool listing. Pool cases add, modify, delete, list all, and list one pool. Directive cases create directives in pools, remove pools to delete directives, filter by pool/path/path+pool, remove one directive by ID, remove every directive for a path using a relative path, modify directive path and pool, and list a single directive by ID. Later cases verify help text, pool and directive statistics columns, max TTL formatting (`never`, `000:04:00:00.000`), unlimited limits, and default/overridden replication after pool and directive modification.

## State and Persistence Behavior

The fixture mutates NameNode cache-manager state: cache pools, owners, groups, modes, byte limits, max TTLs, default replication, cache directives, directive IDs, paths, directive replication, and directive TTLs. Cleanup removes created pools, which also removes their directives.

## Dependencies and Integration Points

It integrates with the `CacheAdmin` CLI, NameNode cache manager RPCs, table formatting, directive ID allocation, path normalization, permission-style mode rendering, stats counters, and CLI comparator framework.

## Risks and Edge Cases

Risks include directive ID sequence assumptions, table spacing drift, TTL formatting changes, pool removal failing to purge directives, path normalization bugs for relative `../../foo`, incorrect inheritance/override of default replication, and stale cache-manager state between tests.

## Test Signals

Signals are expected success messages, result counts (`Found 0/1/2/3`), exact table substrings for owners/groups/modes/limits/TTLs/replication, zero-valued stats columns, successful help text, and final directive listings after remove/modify operations showing only intended entries.
