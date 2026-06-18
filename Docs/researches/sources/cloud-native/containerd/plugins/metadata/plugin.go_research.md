# sources/cloud-native/containerd/plugins/metadata/plugin.go

## Purpose
Registers the Bolt-backed metadata DB plugin that centralizes containerd metadata, content labels/policy, snapshotter references, and event publishing.

## Important APIs, Types, And Functions
`BoltConfig` controls content sharing policy and unsafe async bbolt mode. `Validate` accepts `shared` or `isolated`. The plugin init opens `meta.db`, configures bbolt options, gathers content store, snapshotters, and event publisher, creates `metadata.DB`, and initializes it.

## Control Flow
Startup creates the root directory, loads dependencies, sets bbolt options including no freelist sync and configurable open timeout, validates sharing policy, records plugin exports (`policy`, `path`), logs slow opens after 10 seconds, opens `meta.db`, builds DB options with event publisher and optional isolated policy, initializes metadata buckets, and returns the DB.

## State And Persistence
Persists all metadata in `meta.db` under the plugin root. Content sharing policy and no-sync settings affect persistence semantics. Snapshotter map and content store are attached to the metadata DB.

## Dependencies And Integration Points
Requires content, event, and snapshot plugins. Integrates with bbolt, timeout registry, metadata stores, content store policy, event publisher, and downstream services such as images, containers, leases, diff, and CRI.

## Risks
`NoSync`/`NoGrowSync` improve performance at data-loss risk. Bolt open can wait indefinitely by default. Invalid sharing policy prevents startup. Directory mode and DB file permissions are security-sensitive.

## Test Signals
No direct tests in this subset; nearly all containerd integration tests depend on this plugin.
