<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/erofs/plugin/plugin_other.go -->
# sources/cloud-native/containerd/plugins/snapshots/erofs/plugin/plugin_other.go

## Purpose
Provides the non-Linux EROFS plugin capability shim.

## Important APIs, Types, And Functions
`supportsIDMappedMounts` returns `false, nil`.

## Control Flow
When the common plugin initializer runs on non-Linux builds, remap support is never enabled and the snapshotter receives no `WithRemapIDs` option.

## State And Persistence
No state or filesystem effects.

## Dependencies And Integration Points
Compiled under `!linux` and used only by the common EROFS plugin registration code.

## Risks And Edge Cases
The common plugin may still register EROFS and advertise `rebase`/`only-remap-ids` on platforms where the actual snapshotter helpers are stubs; unsupported runtime paths must fail with `ErrNotImplemented`.

## Test Signals
Compile-time coverage for non-Linux builds; no file-local tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/erofs/plugin/plugin_other.go -->
