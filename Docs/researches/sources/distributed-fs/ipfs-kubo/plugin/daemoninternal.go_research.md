<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/daemoninternal.go -->
# sources/distributed-fs/ipfs-kubo/plugin/daemoninternal.go

## Purpose

This file defines an internal daemon plugin interface that receives direct `*core.IpfsNode` access.

## Important APIs, Types, and Functions

`PluginDaemonInternal` embeds `Plugin` and adds `Start(*core.IpfsNode) error`.

## Control Flow, State, and Integration

The loader starts these plugins after injection. Built-in peerlog and telemetry use this interface because they need node internals.

## Dependencies, Risks, and Test Signals

Dependency is Kubo core. The interface is explicitly unstable; plugins can break across internal graph changes. Built-in plugin tests and daemon startup validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/daemoninternal.go -->
