<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/flatfs/flatfs.go -->
# sources/distributed-fs/ipfs-kubo/plugin/plugins/flatfs/flatfs.go

## Purpose

This datastore plugin registers the FlatFS datastore backend.

## Important APIs, Types, and Functions

`flatfsPlugin` implements `PluginDatastore` with type name `flatfs`. The parser requires string `path`, string `shardFunc`, and bool `sync`; it parses the shard function with `flatfs.ParseShardFunc`. `DiskSpec` records type/path/shardFunc. `Create` resolves relative path and calls `flatfs.CreateOrOpen`.

## Control Flow, State, and Integration

The plugin registers a config handler with fsrepo during loader injection. Persistent state lives in the configured FlatFS directory.

## Dependencies, Risks, and Test Signals

Dependencies are go-ds-flatfs and fsrepo. Risks include strict config type requirements, malformed shard functions, and a misleading error message for missing path. Repo init/open tests with flatfs specs validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/flatfs/flatfs.go -->
