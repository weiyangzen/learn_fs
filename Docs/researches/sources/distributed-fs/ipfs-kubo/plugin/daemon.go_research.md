<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/daemon.go -->
# sources/distributed-fs/ipfs-kubo/plugin/daemon.go

## Purpose

This file defines the public daemon plugin interface for plugins that run after the Kubo daemon starts.

## Important APIs, Types, and Functions

`PluginDaemon` embeds `Plugin` and adds `Start(coreiface.CoreAPI) error`.

## Control Flow, State, and Integration

The loader calls `Start` after injection during `PluginLoader.Start`, passing a CoreAPI wrapper around the node.

## Dependencies, Risks, and Test Signals

Dependency is `coreiface`. Risks are plugin startup failures causing loader close and daemon startup errors. Loader integration tests or daemon plugin tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/daemon.go -->
