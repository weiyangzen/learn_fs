<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/plugin/plugin.go -->
# sources/cloud-native/containerd/plugins/content/local/plugin/plugin.go

## Purpose
Registers the local content store as a containerd content plugin.

## Important APIs, Types, And Functions
init registers plugins.ContentPlugin with ID content and an InitFn.

## Control Flow
InitFn reads PropertyRootDir from plugin context, exports it in metadata, and returns local.NewStore(root).

## State And Persistence
Creates/uses the content root directory via NewStore. Plugin metadata exports root path.

## Dependencies And Integration Points
Integrates containerd plugin registry with plugins/content/local package.

## Risks And Edge Cases
Root property must be populated by plugin host. Label store is nil, so mutable labels are not supported by this plugin instance unless wrapped elsewhere.

## Test Signals
Covered by plugin integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/plugin/plugin.go -->
