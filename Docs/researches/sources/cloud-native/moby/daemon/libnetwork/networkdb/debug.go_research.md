# sources/cloud-native/moby/daemon/libnetwork/networkdb/debug.go

## Purpose
Debug helpers for NetworkDB encryption key logging and table dumping.

## Important APIs, Types, And Functions
`logEncKeys(ctx, keys ...[]byte)` writes hex-encoded keys to the file named by `NETWORKDBKEYLOGFILE`. `DebugDumpTable(tname string)` returns a formatted dump of entries in a table prefix.

## Control Flow
Key logging no-ops when the env var is unset; otherwise it opens/creates the file mode `0600`, appends hex key lines, and logs any open/write/close errors. `DebugDumpTable` snapshots the table root under read lock and walks the prefix into a `strings.Builder`.

## State And Persistence
`logEncKeys` persists sensitive key material to a caller-selected file for debugging. `DebugDumpTable` only reads in-memory radix indexes.

## Dependencies And Integration Points
Called by key-management paths in `cluster.go`. Table dump supports diagnostics for NetworkDB tables.

## Risks
`NETWORKDBKEYLOGFILE` is intentionally dangerous: it writes encryption keys to disk and must only be used in controlled debug scenarios. Dump output may expose table values.

## Test Signals
No direct tests in this subset.
