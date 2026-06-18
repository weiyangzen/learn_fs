# sources/distributed-fs/juicefs/pkg/object/etcd.go


Purpose: implements etcd v3 as an object-storage backend behind `!noetcd`, registering `etcd`.

Important APIs and flow: `etcdClient` stores an etcd client and KV interface. `Get` fetches one key and slices the value by offset/limit. `Put` reads the full reader into memory and stores it as a string value. `Head` reports size from value length and uses current time as mtime. `Delete` deletes the key. `List` supports prefix scans without delimiters, using `genNextKey(prefix)` as the range end and sorted keys with limit. `buildTlsConfig` builds TLS settings from URL query parameters.

State and persistence: each object is one etcd key/value. There is no durable mtime metadata, directory metadata, or chunking.

Dependencies and integration: uses `go.etcd.io/etcd/client/v3`, transport TLS helpers, shared `obj`, and `DefaultObjectStorage`.

Risks: whole-object values are unsuitable for large data and constrained by etcd value size and cluster performance. `Put` converts arbitrary bytes to string, which preserves bytes in Go but may be surprising. `genNextKey` can underflow on empty strings, though `List` avoids it for empty prefixes. Delimiter listing and multipart operations are unsupported. Mtime is synthetic and changes on every `Head`/`List`.

Test signals: `TestEtcd` is environment-gated and runs the broad storage suite when `ETCD_ADDR` is set.
