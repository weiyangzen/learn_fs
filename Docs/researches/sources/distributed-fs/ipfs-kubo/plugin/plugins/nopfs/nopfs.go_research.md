<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/nopfs/nopfs.go -->
# sources/distributed-fs/ipfs-kubo/plugin/plugins/nopfs/nopfs.go

## Purpose

This Fx plugin integrates `nopfs` content blocking into Kubo's block service, name system, and path resolvers.

## Important APIs, Types, and Functions

`nopfsPlugin` stores the repo path during `Init` and implements `PluginFx`. `MakeBlocker` loads default denylist files and repo-local `denylists` files, then creates a `nopfs.Blocker`. `PathResolvers` wraps online and offline IPLD/UnixFS path resolvers. `Options` returns original FX options when `IPFS_CONTENT_BLOCKING_DISABLE` is set, otherwise provides the blocker and decorates block service, name system, and resolvers.

## Control Flow, State, and Integration

At node construction time, Fx creates the blocker from filesystem denylist files and decorates core dependencies. The plugin reads repo-local state under `<repo>/denylists` but does not itself persist data.

## Dependencies, Risks, and Test Signals

Dependencies are ipfs-shipyard/nopfs, Kubo core/node fetchers, and Fx. Risks include denylist read failures breaking node construction, broad resolver wrapping, environment-disable bypass, and stale denylists needing restart. Integration tests should verify blocked CIDs/paths and disable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/nopfs/nopfs.go -->
