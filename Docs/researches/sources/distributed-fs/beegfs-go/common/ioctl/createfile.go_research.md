<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/ioctl/createfile.go -->
# sources/distributed-fs/beegfs-go/common/ioctl/createfile.go

Purpose: user-friendly wrapper for BeeGFS `CreateFileV3` ioctl with functional options for file type, symlink target, permissions, ownership, preferred targets, and storage pool.

Important APIs/types/functions: `createFileConfig`, `FileType`, constants `S_REGULAR` and `S_SYMBOLIC`, option functions `SetType`, `SetSymlinkTo`, `SetPermissions`, `SetUID`, `SetGID`, `SetPreferredTargets`, `SetStoragePool`, and `CreateFile`.

Control flow: `CreateFile` initializes defaults, applies options, infers regular vs symlink type, rejects inconsistent symlink type, opens the parent directory, gets parent entry info through ioctl, builds null-terminated byte slices, conditionally builds symlink pointer, invokes `iocCreateFileV3`, and keeps slices alive until syscall returns.

State and persistence: creates a new BeeGFS file or symlink and may set mode, uid/gid, preferred targets, and storage pool depending on privileges/server setup.

Dependencies and integration points: depends on ABI `mkFileV3Arg`, `GetEntryInfo`, and unsafe syscall behavior. `SetPreferredTargets` appends a terminating zero required by the kernel API.

Risks: `PrefTargetsLen` is set to `len(cfg.preferredTargets) * 8` even though targets are `uint16`; this should be verified against the C ABI. `SetPreferredTargets` appends to the caller-provided slice and may mutate/reuse backing storage. Parent entry info from `GetEntryInfo` is untrimmed because ioctls need fixed arrays.

Test signals: `createfile_test.go` is build-tagged and verifies regular file and symlink creation/mode on a real BeeGFS mount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/ioctl/createfile.go -->
