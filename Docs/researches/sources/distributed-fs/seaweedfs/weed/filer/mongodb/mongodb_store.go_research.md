# sources/distributed-fs/seaweedfs/weed/filer/mongodb/mongodb_store.go

## Purpose

`mongodb_store.go` implements SeaweedFS filer metadata storage using MongoDB. It stores each entry as one document keyed by `(directory, name)`, creates a unique index, supports TLS/auth configuration, and implements directory listing with sorted Mongo queries.

## Important APIs, Types, and Functions

`MongodbStore` holds the Mongo client, database name, and collection name. `Model` maps document fields `directory`, `name`, and `meta`. The store implements initialization, TLS setup, unique index creation, no-op transactions, entry upsert/find/delete, directory child deletion, prefixed listing, and shutdown.

## Control Flow

Initialization reads URI, pool, TLS, credential, and database configuration, builds `options.Client`, optionally configures TLS and explicit credentials, connects with a 10-second timeout, and creates a unique index on `directory,name`. Entry update validates against null bytes, encodes/gzips metadata, then uses `UpdateOne` with upsert and BSON builders. Find validates path parts, queries by directory/name, maps no document or empty meta to `ErrNotFound`, and decodes the entry.

Listing builds a query on `directory`, optional anchored regex for prefix using `regexp.QuoteMeta`, and `$gt`/`$gte` for pagination, sorts by `name`, limits results, decodes each document, and invokes the callback.

## State and Persistence Behavior

Metadata persists as BSON documents in the `filemeta` collection. The unique compound index enforces one row per directory/name. No MongoDB transactions are used, so multi-entry operations are not atomic. Delete-folder-children deletes documents whose `directory` exactly equals the requested path, i.e. direct children only.

## Dependencies and Integration Points

The file depends on the official MongoDB Go driver, TLS certificate files, SeaweedFS entry encoding, and the filer store registry. It integrates with MongoDB auth/TLS deployments and shared filer operations.

## Risks and Edge Cases

TLS configuration requires client cert/key and CA files whenever `ssl` is true; it does not support system-root-only TLS in this path. `FindEntry` logs and returns `ErrNotFound` for non-no-document query errors, which can hide backend failures. Prefix listing uses regex plus sort; index usage depends on Mongo's query planner and collation. Null-byte validation is defense-in-depth.

## Test Signals

Tests should cover unique index creation, TLS config errors, credential override while preserving URI auth options, upsert/find/delete, direct-child deletion, prefix and pagination ordering, null-byte rejection, and backend error mapping.
