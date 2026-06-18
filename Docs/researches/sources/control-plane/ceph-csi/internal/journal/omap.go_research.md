# sources/control-plane/ceph-csi/internal/journal/omap.go

## Purpose
`omap.go` centralizes low-level RADOS OMAP operations used by CSI journal code. It fetches, lists, sets, and removes OMAP keys while normalizing common Ceph errors to Ceph-CSI utility errors.

## Important APIs, Types, And Functions
`chunkSize` controls `ListOmapValues` pagination. `getOMapValues()` fetches selected keys by iterating OMAP entries with a prefix. `listOMapValues()` returns all keys under a prefix. `setOMapKeys()` writes key/value pairs. `removeMapKeys()` removes keys and tolerates missing OMAP objects. `omapPoolError()` wraps missing pool errors as `util.ErrPoolNotFound`.

## Control Flow And State
Each operation obtains an IO context from the journal connection, sets the namespace when configured, performs a RADOS OMAP operation, logs results, and destroys the IO context. List operations advance `startAfter` from the last key seen until no new keys are returned or an error occurs.

## State And Persistence Behavior
State lives in Ceph RADOS OMAP objects. Values are stored as strings converted to byte slices. Missing pools and missing OMAP objects are mapped differently depending on operation: fetch/list treat missing objects as `util.ErrKeyNotFound`, while remove treats missing objects as a non-error for backward compatibility.

## Dependencies And Integration Points
The file depends on `github.com/ceph/go-ceph/rados`, `util.ClusterConnection`, and Ceph-CSI logging. `voljournal.go` and `volumegroupjournal.go` build reservation semantics on top of these helpers.

## Risks And Edge Cases
`getOMapValues()` lists through the prefix and filters in memory instead of using direct key retrieval, so large OMAP objects still require pagination. If a key is not in the requested prefix, it will not be found even if listed in `keys`. The missing-object behavior differs between removal and reads, so callers must understand idempotent cleanup semantics.

## Test Signals
No direct tests are included in this subset. Higher-level journal flows should test missing pool, missing OMAP, namespace, prefix filtering, pagination, set/remove idempotency, and logging-safe handling of sensitive values.
