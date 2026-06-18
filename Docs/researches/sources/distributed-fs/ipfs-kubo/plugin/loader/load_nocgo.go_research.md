<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/loader/load_nocgo.go -->
# sources/distributed-fs/ipfs-kubo/plugin/loader/load_nocgo.go

## Purpose

This file disables dynamic plugin loading when building on supported Unix-like platforms without cgo.

## Important APIs, Types, and Functions

`init` assigns `loadPluginFunc = nocgoLoadPlugin`. `nocgoLoadPlugin` returns `not built with cgo support`.

## Control Flow, State, and Integration

Preloaded compiled-in plugins still work; only runtime `.so` loading fails. The loader will surface the error if executable files are found in the plugins directory.

## Dependencies, Risks, and Test Signals

Dependencies are build tags and plugin interface types. Risks include confusing users who expect dynamic plugins in cgo-disabled builds. Build matrix tests with `CGO_ENABLED=0` validate this path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/loader/load_nocgo.go -->
