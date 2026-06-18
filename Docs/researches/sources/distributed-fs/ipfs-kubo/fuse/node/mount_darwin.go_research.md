<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/node/mount_darwin.go -->
# sources/distributed-fs/ipfs-kubo/fuse/node/mount_darwin.go

## Purpose

This Darwin-specific file installs a pre-mount check for macFUSE/OSXFUSE helper binaries.

## Important APIs, Types, and Functions

`init` assigns `platformFuseChecks = darwinFuseCheck`. `macFUSEPaths` lists known mount helper locations. `darwinFuseCheck` returns nil if any helper exists and otherwise returns a multi-line installation error.

## Control Flow, State, and Integration

The check runs before node-level mount orchestration. It does not mount or persist anything; it fails early with actionable guidance.

## Dependencies, Risks, and Test Signals

Dependencies are `os.Stat`, Kubo core types, and current macFUSE installation paths. Risks include path changes or installed but unusable macFUSE. macOS FUSE integration tests and user mount attempts are the practical signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/node/mount_darwin.go -->
