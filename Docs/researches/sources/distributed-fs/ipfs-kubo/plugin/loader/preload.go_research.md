<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/loader/preload.go -->
# sources/distributed-fs/ipfs-kubo/plugin/loader/preload.go

## Purpose

This generated file preloads Kubo's built-in plugins into the plugin loader.

## Important APIs, Types, and Functions

The `init` function calls `Preload` for git, dag-jose, badgerds, flatfs, levelds, pebbleds, peerlog, fxtest, nopfs, and telemetry plugin slices.

## Control Flow, State, and Integration

At package initialization time, each plugin slice is appended to the global preload list. `NewPluginLoader` later loads that list before scanning external plugins.

## Dependencies, Risks, and Test Signals

Dependencies are all built-in plugin packages. Risks include generated order changes, stale generated file after plugin list edits, and unavoidable side effects from importing plugin packages. `preload.sh` and plugin startup tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/loader/preload.go -->
