<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/plugin/plugin.go -->
# sources/cloud-native/stargz-snapshotter/service/plugin/plugin.go

## Purpose
Registers the stargz snapshotter plugin through a package `init`, making it available when this package is imported by a containerd build.

## Important APIs, Types, And Functions
- Imports `service/plugincore`.
- `init()` calls `plugincore.RegisterPlugin()`.

## Control Flow
Registration happens automatically at package initialization time. There is no runtime branching in this file.

## State And Persistence
No file-local state. It mutates containerd's global plugin registry through `RegisterPlugin`.

## Dependencies And Integration Points
This is the thin public plugin entrypoint. Actual config, keychain, and snapshotter setup live in `service/plugincore/plugin.go`.

## Risks And Edge Cases
Import side effects are required. If the package is omitted from a build, the plugin is not registered.

## Test Signals
Containerd plugin registry should include snapshot plugin `stargz` after importing this package.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/plugin/plugin.go -->
