<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/badgerds/badgerds.go -->
# sources/distributed-fs/ipfs-kubo/plugin/plugins/badgerds/badgerds.go

## Purpose

This built-in datastore plugin registers the deprecated Badger v1 datastore backend.

## Important APIs, Types, and Functions

`badgerdsPlugin` implements `PluginDatastore` with type name `badgerds`. Its parser requires `path`, optionally accepts `syncWrites`, `truncate`, and string `vlogFileSize` parsed by `humanize.ParseBytes`. `datastoreConfig.DiskSpec` returns datastore metadata. `Create` prints/logs a deprecation warning, resolves relative paths against repo path, creates the directory, configures Badger options, and calls `badgerds.NewDatastore`.

## Control Flow, State, and Integration

After loader injection, fsrepo can instantiate badgerds repos. The plugin persists data in the configured directory and writes a prominent warning to stderr every creation.

## Dependencies, Risks, and Test Signals

Dependencies are go-ds-badger, humanize, fsrepo, repo datastore interface, and filesystem directory creation. Risks include deprecated upstream bugs, future removal, path/config type errors, and noisy stderr. Repo open tests for badger configs and migration guidance are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/badgerds/badgerds.go -->
