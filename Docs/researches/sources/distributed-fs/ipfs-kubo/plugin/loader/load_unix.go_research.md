<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/loader/load_unix.go -->
# sources/distributed-fs/ipfs-kubo/plugin/loader/load_unix.go

## Purpose

This file enables dynamic Go plugin loading on supported Unix-like platforms when cgo is available and `noplugin` is not set.

## Important APIs, Types, and Functions

`init` assigns `loadPluginFunc = unixLoadPlugin`. `unixLoadPlugin` calls `plugin.Open`, looks up the exported `Plugins` symbol, asserts it is `*[]plugin.Plugin`, and returns the slice.

## Control Flow, State, and Integration

`loadDynamicPlugins` in `loader.go` invokes this for executable files in the repo plugins directory. Loaded plugins then enter the normal loader state machine.

## Dependencies, Risks, and Test Signals

Dependencies are Go's `plugin` package, cgo, and compatible buildmode/plugin artifacts. Risks include ABI/version mismatch, symbol type mismatch, platform support gaps, and the typo in the error message. Dynamic plugin build/load smoke tests validate this path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/loader/load_unix.go -->
