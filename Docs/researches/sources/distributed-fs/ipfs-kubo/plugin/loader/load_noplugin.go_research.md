<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/loader/load_noplugin.go -->
# sources/distributed-fs/ipfs-kubo/plugin/loader/load_noplugin.go

## Purpose

This file disables dynamic plugin loading when Kubo is built with the `noplugin` tag.

## Important APIs, Types, and Functions

`init` assigns `loadPluginFunc = nopluginLoadPlugin`. `nopluginLoadPlugin` returns `not built with plugin support`.

## Control Flow, State, and Integration

The loader can still manage preloaded plugins compiled into the binary, but dynamic plugin files cannot be loaded.

## Dependencies, Risks, and Test Signals

Dependencies are build tags and plugin interface types. Risks are user confusion and startup errors if plugin files are present. Build-tag tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/loader/load_noplugin.go -->
