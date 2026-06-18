# sources/distributed-fs/juicefs/pkg/meta/tkv_prefix.go

## Purpose
`tkv_prefix.go` scopes a `tkvClient` to a fixed byte prefix so multiple JuiceFS metadata namespaces can share one backend safely.

## Important APIs, Types, and Functions
Types are `prefixTxn`, `prefixIterator`, and `prefixClient`. Key functions are `realKey`, `origKey`, transaction wrappers, `scan`, `reset`, optional changelog delegation, and `withPrefix`.

## Control Flow and State
`prefixTxn` prepends the namespace prefix to every key before delegating to the underlying transaction and strips the prefix from scan/iterator keys before returning them. `prefixClient.simpleTxn` and `txn` wrap the closure with a prefixed transaction. `scan` scans the physical prefixed range and returns logical keys. `reset` only accepts `nil` and maps it to a physical prefix reset.

## State and Persistence Behavior
The wrapper has only in-memory prefix state. Persistence is in the underlying backend with all keys physically namespaced. If the wrapped backend implements `tkvChangelogClient`, changelog key creation/range scanning is delegated; otherwise generic logical `XLOG` keys are used inside the prefix.

## Dependencies and Integration Points
It depends on the generic KV interfaces and `nextKey`. Etcd, TiKV, and FDB constructors use this wrapper to isolate path or query-prefix namespaces.

## Risks and Test Signals
Risks include prefix stripping panics if an underlying backend returns keys outside the prefix, reset rejecting non-nil prefixes, and optional iterator support requiring the wrapped transaction to implement `iterKvTxn`. Shared `TestMemKV` wraps `memkv` with a prefix and runs `testTKV`.
