# sources/distributed-fs/seaweedfs/weed/filer/cassandra2/cassandra_store.go

## Purpose
This file implements the newer Cassandra2 SeaweedFS filer store. It extends the Cassandra backend with TLS/mTLS configuration and a schema that adds `dirhash` to reduce partitioning and query costs.

## Important APIs, Types, and Functions
- `Cassandra2Store` mirrors the original store with cluster config, session, and super-large-directory hash map.
- `Initialize` reads credentials, TLS paths, host verification, large directories, local DC, and timeout.
- `initialize` validates TLS file combinations and existence, configures gocql `SslOptions`, optionally uses AWS Keyspaces port 9142, then creates a local-quorum session.
- CRUD/list methods mirror Cassandra but query `filemeta` using `dirhash`, `directory`, and `name`.
- Transaction methods are no-ops.

## Control Flow and State
TLS options are set before session creation when CA/cert/key paths are provided. Insert/update apply super-large-directory rewriting, encode and optionally gzip metadata, then insert `(dirhash,directory,name,meta)` with TTL. Find, delete, folder delete, and listing compute `util.HashStringToLong(dir)` and include it in predicates. Listing orders by `name` within a hashed directory and returns `limit+1` rows.

## State and Persistence Behavior
Rows persist `dirhash` beside directory and name. This schema is distinct from the original Cassandra backend and must match table definitions. TTL comes from entry attributes. Super-large-directory behavior still disables normal listing/deletion for those directories.

## Dependencies and Integration Points
It integrates with gocql v2, TLS file paths from configuration, SeaweedFS `filer.Stores`, `filer.Entry` encoding, `filer_pb.ErrNotFound`, and `util.HashStringToLong`.

## Risks and Edge Cases
- TLS path validation requires cert and key together but permits CA-only TLS.
- Hosts without explicit ports switch to 9142 when TLS is enabled, which is suitable for AWS Keyspaces but may surprise standard Cassandra users.
- No transaction support.
- Prefix listing is unsupported.
- Hash collisions are guarded by also storing/querying directory, but schema design must preserve this.

## Test Signals
Tests should cover TLS config validation, port selection, CRUD/listing against the Cassandra2 schema, large-directory behavior, and unsupported prefix listing. No local tests are listed.
