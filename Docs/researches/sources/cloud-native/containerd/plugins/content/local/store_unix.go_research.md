<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/store_unix.go -->
# sources/cloud-native/containerd/plugins/content/local/store_unix.go

## Purpose
Linux/Solaris access-time extraction for content.Info UpdatedAt.

## Important APIs, Types, And Functions
getATime reads syscall.Stat_t.Atim or falls back to ModTime.

## Control Flow
Called by store.info.

## State And Persistence
No state; reads file metadata.

## Dependencies And Integration Points
Platform-specific store.go helper.

## Risks And Edge Cases
Depends on Unix Stat_t Atim field presence.

## Test Signals
Indirect platform coverage only.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/store_unix.go -->
