<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugin.go -->
# sources/distributed-fs/ipfs-kubo/plugin/plugin.go

## Purpose

This file defines the base plugin contract and initialization environment shared by all Kubo plugin types.

## Important APIs, Types, and Functions

`Environment` carries repo path and arbitrary plugin config from `Plugins.Plugins["plugin-name"].Config`. `Plugin` requires `Name`, `Version`, and `Init`, and may optionally also implement `io.Closer`.

## Control Flow, State, and Integration

The loader constructs an `Environment` for each loaded plugin during initialization. Implementations use it to persist repo paths or parse config.

## Dependencies, Risks, and Test Signals

There are no external dependencies. Risks include untyped config causing runtime assertions in plugins and plugin name/version collisions. Loader duplicate checks and built-in plugin tests validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugin.go -->
