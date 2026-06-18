<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/loader/Rules.mk -->
# sources/distributed-fs/ipfs-kubo/plugin/loader/Rules.mk

## Purpose

This Make fragment declares how generated plugin loader preload code participates in builds.

## Important APIs, Types, and Functions

It includes `mk/header.mk`, adds `$(d)/preload.go` to `DEPS_GO`, and includes `mk/footer.mk`.

## Control Flow, State, and Integration

Any target depending on `DEPS_GO` will include the generated preload file in dependency tracking.

## Dependencies, Risks, and Test Signals

Dependencies are make header/footer and preload generation. Risks include stale `preload.go` not causing rebuilds. Plugin build tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/loader/Rules.mk -->
