<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/levelds/levelds.go -->
# sources/distributed-fs/ipfs-kubo/plugin/plugins/levelds/levelds.go

## Purpose

This datastore plugin registers LevelDB-backed repo datastore support.

## Important APIs, Types, and Functions

`leveldsPlugin` implements `PluginDatastore` with type name `levelds`. The parser requires `path` and optionally accepts `compression` values `none`, `snappy`, empty, or nil. `DiskSpec` records type/path. `Create` resolves relative paths and calls `levelds.NewDatastore` with the selected compression.

## Control Flow, State, and Integration

Once injected into fsrepo, configs using `levelds` instantiate persistent LevelDB directories under the repo or absolute path.

## Dependencies, Risks, and Test Signals

Dependencies are go-ds-leveldb and goleveldb options. Risks include unrecognized compression values, filesystem corruption risks if used concurrently, and path resolution mistakes. Repo datastore config tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/levelds/levelds.go -->
