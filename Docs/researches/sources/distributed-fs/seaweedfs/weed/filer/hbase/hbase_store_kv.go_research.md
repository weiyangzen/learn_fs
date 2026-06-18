# sources/distributed-fs/seaweedfs/weed/filer/hbase/hbase_store_kv.go

## Purpose

`hbase_store_kv.go` provides the HBase-backed generic KV operations used by the filer for auxiliary state such as metadata replication offsets. It also centralizes HBase put/get/delete helpers for both KV and metadata families.

## Important APIs, Types, and Functions

The public methods are `KvPut`, `KvGet`, and `KvDelete`. Shared helpers are `doPut`, `doPutWithOptions`, `doGet`, and `doDelete`. `COLUMN_NAME` defines the single qualifier `a` used in each family.

## Control Flow

`KvPut` calls `doPut` with family `kv` and no TTL. `doPut` chooses HBase options: `AsyncWal` always, plus `TTL` when `ttlSecond > 0`. `doPutWithOptions` builds a nested family/qualifier value map and calls gohbase `Put`. `doGet` builds a family-restricted `Get`, returns the first cell value, and maps empty results to `filer.ErrKvNotFound`. `doDelete` builds a qualifier-specific delete and sends it with async WAL durability.

## State and Persistence Behavior

KV values are stored in the same HBase table as metadata but under the `kv` column family. Metadata helper calls use the `meta` family and may apply TTL from the entry. All writes use async WAL durability, so acknowledged writes may be more exposed to region-server failure than fully synced WAL writes.

## Dependencies and Integration Points

The code depends on gohbase `hrpc` request builders and the `HbaseStore` table/client fields. It is used by the HBase metadata store and by filer components that call `FilerStore.Kv*`, including replication offset storage.

## Risks and Edge Cases

`doGet` uses `context.Background()` instead of the caller's context when constructing the HBase get, so cancellation/deadline propagation is incomplete for reads. It returns only the first cell and assumes one qualifier. Empty value and missing key are indistinguishable for callers because empty cell sets yield `ErrKvNotFound`.

## Test Signals

Tests should cover put/get/delete round trips, not-found mapping, caller context cancellation behavior, TTL option behavior for metadata puts, and HBase failures from each RPC path.
