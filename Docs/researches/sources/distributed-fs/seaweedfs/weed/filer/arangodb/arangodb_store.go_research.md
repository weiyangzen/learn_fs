# sources/distributed-fs/seaweedfs/weed/filer/arangodb/arangodb_store.go

## Purpose
This file implements the SeaweedFS filer store for ArangoDB. It registers the backend, connects to or creates the configured database, stores entries as Arango documents, supports bucket-specific collections, and implements filer CRUD/list transactions.

## Important APIs, Types, and Functions
- `ArangodbStore` holds the connection, client, database, KV collection, bucket collection cache, lock, and database name.
- `Model` maps stored documents with `_key`, directory, name, ttl, and metadata encoded as `[]uint64`.
- `Initialize` reads config and calls `connection`.
- `connection` creates the HTTP connection, authenticates, opens or creates the database, and ensures the KV collection.
- Transaction methods begin exclusive transactions over cached bucket collections plus KV collection, then commit or abort using a context-stored transaction id.
- Filer methods: `InsertEntry`, `UpdateEntry`, `FindEntry`, `DeleteEntry`, `DeleteFolderChildren`, `ListDirectoryPrefixedEntries`, `ListDirectoryEntries`, and `Shutdown`.

## Control Flow and State
Insert/update derive directory and name, encode entry metadata, optionally gzip large chunk metadata, build a `Model`, set TTL timestamp text, find the target collection from the full path, and create or update a document keyed by MD5 hash of the full path. Insert conflicts call `UpdateEntry`. Finds read the hashed document and decode metadata. Deletes remove by hashed full path. Folder deletion runs an AQL query to remove documents whose directory equals or appears under the target. Listing builds an AQL query for name range, optional prefix, exact directory, sorting, and limit, then decodes each document and calls the listing callback.

## State and Persistence Behavior
Each entry persists as one document. ArangoDB cannot store arbitrary binary directly in this model, so metadata bytes are converted to a length-prefixed `[]uint64`. TTL is stored in a field indexed by helpers. Bucket paths map to per-bucket collections, while non-bucket paths use a default collection. The bucket collection cache is in-memory and lazily filled.

## Dependencies and Integration Points
It integrates with `github.com/arangodb/go-driver`, SeaweedFS `filer.Stores`, `filer.Entry` encoding, `filer_pb.ErrNotFound`, S3 bucket path conventions, and helper functions in `helpers.go` for keying, byte conversion, collection selection, and index creation.

## Risks and Edge Cases
- Listing and delete queries concatenate `startFileName`, `prefix`, and transformed full path into AQL, creating injection or quoting risks if names contain special characters.
- `DeleteFolderChildren` transforms `/` to `,` for `starts_with`, which looks suspicious and should be validated against intended directory encoding.
- `BeginTransaction` only includes collections currently in the cache; a transaction may miss a lazily created bucket collection.
- `UpdateEntry` stores TTL `"none"` while insert stores empty string when no TTL; TTL index semantics depend on Arango behavior for these values.
- Hashing full paths with MD5 gives compact keys but collision handling is absent.

## Test Signals
No local tests are listed. Store-level tests should cover create/update conflict fallback, find/delete not found behavior, TTL, bucket collection mapping, directory listing order and prefix filtering, and transaction coverage across buckets.
