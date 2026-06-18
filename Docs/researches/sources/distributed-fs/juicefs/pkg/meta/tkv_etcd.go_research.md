# sources/distributed-fs/juicefs/pkg/meta/tkv_etcd.go

## Purpose
`tkv_etcd.go` adapts etcd v3 to the transactional KV metadata interface, enabled unless `noetcd` is set. It lets JuiceFS metadata live in an etcd cluster under a path-derived prefix.

## Important APIs, Types, and Functions
Key types are `etcdTxn` and `etcdClient`. Transaction methods implement point gets, batched gets capped at 128 keys, range scans, prefix existence checks, buffered set/delete, append, and counter increments. Client methods implement transaction execution, conflict detection, paginated scans, reset, TLS config parsing, and `newEtcdClient`.

## Control Flow and State
`etcdTxn` records observed mod revisions for reads and buffers writes. `commmit` builds compare conditions from observed revisions and then put/delete ops from the buffer; unsuccessful compares return the package-level `conflicted` error so `kvMeta.txn` retries. To avoid huge etcd transactions, `set` auto-commits when the buffer reaches 128 operations and clears observations. Top-level scans establish a current revision, then page through ranges with `WithMaxModRev`, serializable reads, and duplicate skipping across pages.

## State and Persistence Behavior
All metadata persists in etcd under `u.Path + "\xFD"` via `withPrefix`. Etcd transaction ids and changelog rewind are currently zero, so generic changelog id generation is effectively unavailable for etcd. Prefix reset deletes all keys under the supplied prefix. The client uses optional URL user/password and TLS query parameters.

## Dependencies and Integration Points
It depends on `go.etcd.io/etcd/client/v3`, etcd transport TLS helpers, URL parsing, and `prefixClient`. It integrates with `newKVMeta("etcd", ...)`, generic KV metadata operations, and tests requiring `ETCD_ADDR`.

## Risks and Test Signals
Risks include partial logical transactions because auto-commit can split large buffered writes, no useful transaction id for changelog, scanning stale/revision-limited data, 128-op transaction limits, and TLS/host parsing mistakes. Tests include `TestEtcdClient`, `TestEtcd`, and shared `testTKV`; further coverage should stress large metadata mutations and changelog-enabled etcd behavior.
