# sources/distributed-fs/seaweedfs/weed/filer/elastic/v7/elastic_store.go

## Purpose
This build-tagged file implements SeaweedFS filer stores for Elasticsearch 7 and 8. It stores each entry as JSON in Elasticsearch, partitions metadata by top-level path-derived index, supports listing via parent id searches, and keeps a separate KV index.

## Important APIs, Types, and Functions
- Build tag: `//go:build elastic`.
- Globals define index type, prefix, KV index, and KV mapping.
- `ESEntry` stores `ParentId`, optional `Id` for ES8 sorting, and the `filer.Entry`.
- `ElasticStore` holds the client, max page size, and ES8 mode flag.
- `Elastic8Store` embeds `ElasticStore` and toggles ES8 mode.
- Initialization configures URL, basic auth, sniff/healthcheck, max result window, creates the KV index if needed, and registers both store types.
- Filer methods: `InsertEntry`, `UpdateEntry`, `FindEntry`, `DeleteEntry`, `DeleteFolderChildren`, `ListDirectoryEntries`, and unsupported `ListDirectoryPrefixedEntries`.
- Search helpers: `listSorter`, `search`, `searchAfter`, `deleteIndex`, `deleteEntry`, and `getIndex`.

## Control Flow and State
Insert computes the target index from the path, sets parent id to MD5 of the directory, sets document id to MD5 of full path, marshals `ESEntry`, and indexes it. ES8 additionally stores the id in an indexed field because `_id` fielddata is disallowed. Find does a direct get by id. Delete removes the entry and, when deleting a top-level directory, attempts to delete the corresponding bucket index. Folder deletion lists child entries and deletes them one by one. Listing refreshes the index, creates it if absent, searches by parent id, sorts descending by `_id` or `Id.keyword`, and pages with `search_after`.

## State and Persistence Behavior
Entry metadata persists as JSON documents that include the full `filer.Entry`. Index selection is based on the first path segment. The root/top-level index is `.seaweedfs_`; deeper paths use `.seaweedfs_<top-level>`. KV data lives in `.seaweedfs_kv_entries`.

## Dependencies and Integration Points
It uses `github.com/olivere/elastic/v7`, `jsoniter`, SeaweedFS filer store registration, `filer.Entry`, `filer_pb.ErrNotFound`, and `weed_util.FullPath`/hash helpers.

## Risks and Edge Cases
- Prefix directory listing is unsupported.
- Sorting by MD5 document id does not obviously match filename lexical order, so pagination/list order should be scrutinized.
- `SearchAfter(after)` passes a string hash and must match sort-field values, especially for ES8 `Id.keyword`.
- `DeleteFolderChildren` is iterative and can be costly for large folders.
- `getIndex` lowercases top-level names, which can merge differently cased names.
- The build tag means this code may receive less routine CI coverage.

## Test Signals
Tests should run under the `elastic` build tag against ES7/ES8, covering index creation, insert/find/delete, top-level directory deletion, listing pagination/order, missing index behavior, and KV operations.
