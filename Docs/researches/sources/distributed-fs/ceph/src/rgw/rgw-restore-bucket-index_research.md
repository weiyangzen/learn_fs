# sources/distributed-fs/ceph/src/rgw/rgw-restore-bucket-index

## Purpose
Interactive experimental recovery script that reconstructs lost bucket index entries by scanning a bucket data pool for head objects matching a bucket marker, deriving RGW object names, and invoking `radosgw-admin object reindex`.

## Important APIs, Types, and Functions
- `get_pool()` infers the data pool from bucket instance explicit placement or zone placement pools.
- `handle_versioned()` handles versioned buckets by reading OLH xattrs, decoding `RGWOLHInfo`, sorting object versions by mtime, and building an objects file with version ids.
- `test_temp_space()` aborts when the temp filesystem or inode space is exhausted.
- Final action is `radosgw-admin object reindex --bucket=... --objects-file=... --yes-i-really-mean-it`.

## Control Flow
The script validates required tools (`radosgw-admin`, `ceph-dencoder`, `jq`) and decoder support, parses bucket/realm/zone/pool/temp/proceed/debug options, fetches bucket entry and instance metadata, determines shard count and data pool, scans either live `rados ls` output or a provided listing for names with the bucket marker, derives object names, optionally runs versioned-bucket handling, prompts the operator unless `-y` was supplied, and reindexes the objects.

## State and Persistence
Temporary metadata, marker listing, object-list, versioned object-list, zone info, decoded OLH info, and optional debug log are written under the temp directory. Unless debug disables cleanup, temp files are removed at completion or termination. Durable cluster changes happen only through `radosgw-admin object reindex`.

## Dependencies and Integration Points
Integrates with RGW metadata (`bucket:` and `bucket.instance:`), zone placement config, RADOS object xattrs, `ceph-dencoder` for `RGWOLHInfo`, and the admin object reindex path. It supports multisite selectors via realm, zonegroup, and zone arguments.

## Risks and Edge Cases
It is destructive/recovery-oriented and can restore wrong or stale entries if marker parsing is wrong or the input `rados ls` file is stale. Versioned bucket logic depends on OLH metadata and `stat2` mtimes. Several shell expansions are unquoted around object names, pool names, and temp paths, so unusual names may break processing. Operator review is the main guard unless `-y` is used.

## Test Signals
Tests should use fixture metadata JSON and listing files for non-versioned and versioned buckets, pool inference cases, missing tool/decoder checks, temp-space aborts, empty object list handling, prompt bypass with `-y`, and correct object-file format for `object reindex`.
