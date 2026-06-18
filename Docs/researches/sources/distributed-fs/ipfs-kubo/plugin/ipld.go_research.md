<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/ipld.go -->
# sources/distributed-fs/ipfs-kubo/plugin/ipld.go

## Purpose

This file defines the interface for plugins that register IPLD codecs.

## Important APIs, Types, and Functions

`PluginIPLD` embeds `Plugin` and requires `Register(multicodec.Registry) error`.

## Control Flow, State, and Integration

The loader calls `Register` against `multicodec.DefaultRegistry` during injection. Built-in git and dag-jose plugins use it.

## Dependencies, Risks, and Test Signals

Dependency is go-ipld-prime multicodec. Risks include codec ID collisions, decode/encode registration errors, and process-global registry mutation. IPLD import/export paths validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/ipld.go -->
