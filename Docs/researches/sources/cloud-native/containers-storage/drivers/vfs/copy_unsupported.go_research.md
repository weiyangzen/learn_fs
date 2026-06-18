<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/vfs/copy_unsupported.go -->
# sources/cloud-native/containers-storage/drivers/vfs/copy_unsupported.go

## Purpose
This non-Linux VFS helper provides directory copy behavior via tar archive streaming.

## Important APIs, Types, And Functions
`dirCopy(srcDir, dstDir string) error` calls `chrootarchive.NewArchiver(nil).CopyWithTar`.

## Control Flow
All copy logic is delegated to the archive package.

## State And Persistence
It writes a complete destination directory copy for VFS child layers.

## Dependencies And Integration Points
The `!linux` build tag selects this fallback for platforms without the Linux copy implementation.

## Risks And Test Signals
Tar copy behavior may differ from Linux copy behavior for platform-specific metadata. Cross-platform VFS tests are the primary signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/vfs/copy_unsupported.go -->
