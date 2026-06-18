# sources/cloud-native/containers-storage/pkg/system/mknod.go

Purpose: default Unix implementation of filesystem node creation and device-number packing for platforms other than Windows and FreeBSD.

Important APIs/types/functions: exports `Mknod(path string, mode uint32, dev uint32) error`, a thin wrapper over `unix.Mknod`, and `Mkdev(major, minor int64) uint32`, which encodes Linux-style major/minor device numbers.

Control flow: `Mknod` delegates directly to the kernel through `x/sys/unix`. `Mkdev` masks and shifts major/minor fields into the historical Linux device encoding.

State/persistence: `Mknod` creates persistent filesystem nodes. `Mkdev` is pure computation.

Dependencies/integration: used by archive extraction and layer application paths that need to recreate device nodes from tar metadata. Depends on `golang.org/x/sys/unix`.

Risks: creating device nodes requires privileges and correct mode bits; errors are not wrapped with path context here. The Linux device encoding is intentionally used on several non-Windows/non-FreeBSD targets, so portability depends on build tags matching syscall expectations.

Test signals: integration tests should cover major/minor round trips, permission-denied behavior, and archive extraction of character/block devices on supported Unix platforms.
