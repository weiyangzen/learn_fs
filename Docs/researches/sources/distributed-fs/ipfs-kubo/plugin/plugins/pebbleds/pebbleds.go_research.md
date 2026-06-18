<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/pebbleds/pebbleds.go -->
# sources/distributed-fs/ipfs-kubo/plugin/plugins/pebbleds/pebbleds.go

## Purpose

This datastore plugin registers experimental Pebble-backed repo datastore support with tunable Pebble options.

## Important APIs, Types, and Functions

`pebbledsPlugin` implements `PluginDatastore` with type name `pebbleds`. The parser requires `path`, reads numeric/bool options via `getConfigInt` and `getConfigBool`, handles cache size, sync/WAL/format/compaction/memtable options, warns about older format major versions, and builds optional `pebble.Options`. `Create` resolves the path, checks it with `fsutil.DirWritable`, and calls `pebbleds.NewDatastore` with cache and Pebble options.

## Control Flow, State, and Integration

After loader injection, fsrepo can create Pebble datastores. The datastore persists data in the configured directory and may ratchet DB format to the newest format when not configured, affecting downgrade compatibility.

## Dependencies, Risks, and Test Signals

Dependencies are CockroachDB Pebble v2, go-ds-pebble, fsutil, fsrepo, and repo interfaces. Risks include int/float64 config coercion truncation, downgrade prevention from format ratcheting, unsafe WAL disabling, and write-throttle misconfiguration. Telemetry tests use pebbleds to create a repo, giving a basic integration signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/pebbleds/pebbleds.go -->
