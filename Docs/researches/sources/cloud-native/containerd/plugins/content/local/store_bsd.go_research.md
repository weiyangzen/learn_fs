<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/store_bsd.go -->
# sources/cloud-native/containerd/plugins/content/local/store_bsd.go

## Purpose
BSD/Darwin/NetBSD access-time extraction for content.Info UpdatedAt.

## Important APIs, Types, And Functions
getATime reads syscall.Stat_t.Atimespec or falls back to ModTime.

## Control Flow
Called by store.info when building content.Info.

## State And Persistence
No state; reads os.FileInfo syscall data.

## Dependencies And Integration Points
Platform-specific companion to store.go.

## Risks And Edge Cases
Depends on Stat_t shape for darwin/freebsd/netbsd.

## Test Signals
Covered indirectly by Info tests on those platforms.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/store_bsd.go -->
