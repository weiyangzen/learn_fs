<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/erofs/plugin/plugin_linux.go -->
# sources/cloud-native/containerd/plugins/snapshots/erofs/plugin/plugin_linux.go

## Purpose
Provides the Linux implementation of EROFS plugin ID-mapped mount capability probing.

## Important APIs, Types, And Functions
`supportsIDMappedMounts` delegates to `overlayutils.SupportsIDMappedMounts`.

## Control Flow
During plugin initialization, `plugin.go` calls this helper; a true result adds `erofs.WithRemapIDs` and advertises the `remap-ids` capability.

## State And Persistence
No persistent state. The helper may trigger overlayutils' temporary mount/probe work.

## Dependencies And Integration Points
Depends on `plugins/snapshots/overlay/overlayutils`, reusing the same kernel feature probe as overlayfs.

## Risks And Edge Cases
EROFS remap support is inferred through overlay utility logic, so false negatives or probe permission failures cause the EROFS plugin to omit remap capability even if parts of the stack might support it.

## Test Signals
Indirectly covered by plugin initialization and EROFS/overlay ID-mapped mount behavior on Linux.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/erofs/plugin/plugin_linux.go -->
