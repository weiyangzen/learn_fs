<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/dagjose/dagjose.go -->
# sources/distributed-fs/ipfs-kubo/plugin/plugins/dagjose/dagjose.go

## Purpose

This IPLD plugin registers the dag-jose codec for Kubo.

## Important APIs, Types, and Functions

`dagjosePlugin` implements `PluginIPLD`, returns name `ipld-codec-dagjose`, version `0.0.1`, no-op init, and registers dag-jose encoder/decoder under multicodec `DagJose`.

## Control Flow, State, and Integration

Loader injection mutates the global multicodec registry. Once registered, IPLD operations can encode/decode dag-jose blocks.

## Dependencies, Risks, and Test Signals

Dependencies are Ceramic's dag-jose library and go-ipld-prime multicodec. Risks include codec registration conflicts and decoder behavior changes. IPLD codec round-trip tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/dagjose/dagjose.go -->
