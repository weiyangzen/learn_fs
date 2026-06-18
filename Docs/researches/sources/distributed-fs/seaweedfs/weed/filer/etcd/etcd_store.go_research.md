# sources/distributed-fs/seaweedfs/weed/filer/etcd/etcd_store.go

## Purpose
This file implements the SeaweedFS filer store using etcd v3 as the metadata backend. It maps each directory/name pair to a lexicographically ordered key and stores encoded entry metadata as the value.

## Important APIs, Types, and Functions
- `EtcdStore` holds the etcd client, key prefix, and timeout.
- `Initialize` reads endpoints, credentials, key prefix, timeout, and TLS files.
- `initialize` creates the client, verifies connectivity with `Status`, and stores the client.
- Store methods: `InsertEntry`, `UpdateEntry`, `FindEntry`, `DeleteEntry`, `DeleteFolderChildren`, `ListDirectoryPrefixedEntries`, `ListDirectoryEntries`, and `Shutdown`.
- Key helpers: `genKey`, `genDirectoryKeyPrefix`, and `getNameFromKey`.

## Control Flow and State
Initialization parses timeout and optional TLS CA/client cert/key into an etcd TLS config, then connects and checks status. Insert/update encode metadata, optionally gzip large chunk metadata, and `Put` under `etcdKeyPrefix + dir + NUL + name`. Find gets that key and decodes the first KV. Delete removes the key. Folder deletion deletes all keys with the directory prefix. Listing computes a prefix and optional start key, uses an etcd range ending at `GetPrefixRangeEnd`, applies `limit+1`, decodes values, skips start when exclusive, and invokes `eachEntryFunc`.

## State and Persistence Behavior
Metadata persists as etcd keys. The NUL separator makes keys sort by directory then name. `etcdKeyPrefix` namespaces all keys. There is no explicit transaction implementation and no TTL handling in this file.

## Dependencies and Integration Points
It depends on `go.etcd.io/etcd/client/v3`, etcd TLS transport helpers, SeaweedFS `filer.Entry` encoding, `filer_pb.ErrNotFound`, and `weed_util.FullPath`.

## Risks and Edge Cases
- Values are stored via `string(meta)`, which preserves bytes in Go but relies on etcd API accepting arbitrary string bytes.
- `getNameFromKey` is called with full etcd keys including prefix; because it scans from the last NUL, prefix contents are safe unless names contain NUL.
- No transaction support.
- Range listing assumes etcd key ordering matches filename ordering after the directory prefix.
- Connection status only checks the first endpoint.

## Test Signals
`etcd_store_test.go` documents a disabled integration test path requiring docker and `make test_etcd`. Useful tests should cover CRUD, listing, prefix listing, delete folder children, TLS config, and key-prefix namespacing.
