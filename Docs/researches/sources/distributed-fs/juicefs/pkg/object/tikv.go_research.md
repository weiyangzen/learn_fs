# sources/distributed-fs/juicefs/pkg/object/tikv.go

Purpose: implements a TiKV RawKV object store behind `tikv`.

Important APIs and types: `tikv` embeds `DefaultObjectStorage` and owns a `rawkv.Client` plus address string. It implements whole-value `Get`, `Put`, `Head`, `Delete`, simple `List`, and `newTiKV`.

Control flow and state: reads and writes map object keys directly to RawKV keys. `Get` and `Head` convert missing or empty values to `os.ErrNotExist` in slightly different ways. Range reads are implemented by slicing the returned byte slice. `List` rejects delimiters, defaults marker to prefix, caps to `rawkv.MaxRawKVScanLimit`, scans from marker, and emits objects with current-time mtimes.

Persistence and integration: data persists in TiKV RawKV. `newTiKV` reduces PingCAP logging based on JuiceFS log level, parses PD endpoints, fills default port 2379, and configures TLS/security from URL query (`ca`, `cert`, `key`, `verify-cn`).

Risks and test signals: object metadata has no real mtime; values are whole-object loaded into memory. `List` does not explicitly filter by prefix before `generateListResult`, so correctness depends on downstream behavior. No TiKV-specific tests are present.
