<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/store_openbsd.go -->
# sources/cloud-native/containerd/plugins/content/local/store_openbsd.go

## Purpose
OpenBSD access-time extraction for content.Info UpdatedAt.

## Important APIs, Types, And Functions
getATime reads syscall.Stat_t.Atim or falls back to ModTime.

## Control Flow
Called by store.info.

## State And Persistence
No state; reads file metadata.

## Dependencies And Integration Points
Platform-specific store.go helper.

## Risks And Edge Cases
OpenBSD Stat_t field differs from other BSDs, hence separate file.

## Test Signals
Indirect platform coverage only.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/store_openbsd.go -->
