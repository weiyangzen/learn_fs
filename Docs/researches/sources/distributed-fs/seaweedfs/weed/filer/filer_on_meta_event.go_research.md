<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_on_meta_event.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_on_meta_event.go

## Purpose
Handles metadata events after local or remote processing, reloading configuration, notifying bucket-aware stores, and updating empty-folder cleanup state.

## Important APIs and Functions
`onMetadataChangeEvent` dispatches to specialized handlers. `onBucketEvents` maps create/delete/rename events under `DirBucketsPath` to store bucket callbacks. `onEmptyFolderCleanupEvents` mirrors creates/deletes/renames to the cleaner. `maybeReloadFilerConfiguration`, `readEntry`, `reloadFilerConfiguration`, `LoadFilerConf`, `LoadRemoteStorageConfAndMapping`, and `maybeReloadRemoteStorageConfigurationAndMapping` handle config reload paths.

## Control Flow and State
Config reload triggers only for events touching `/etc/seaweedfs` and new entry named `filer.conf`. Reload reads inline content or chunks and replaces `f.FilerConf`. Bucket events use event directory and `NewParentPath` to detect create/delete/rename into or out of bucket root. Empty-folder cleanup uses event timestamps.

## Persistence Behavior
This file primarily reads persisted config chunks and mutates in-memory `FilerConf`/remote config state. Store bucket callbacks may create/drop backend bucket structures depending on implementation.

## Dependencies and Integration Points
Uses filer protobuf event helpers, `StreamContent`, `FilerConf`, remote storage config loading, empty-folder cleanup, and `VirtualFilerStore` bucket callbacks.

## Risks
Remote storage reload is marked FIXME and not implemented for events. A typo in a log message is harmless. Config reload errors leave existing config in place. Bucket event correctness depends on metadata event directory fields.

## Test Signals
`filer_on_meta_event_test.go` covers rename into bucket root creating a bucket. Config reload and empty-folder event handling are not directly tested in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_on_meta_event.go -->
