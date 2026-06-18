# sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsIoctl.c

## Purpose
`FhgfsOpsIoctl.c` implements BeeGFS client ioctl commands for version queries, mount/config discovery, stripe layout inspection, file creation with hints or explicit metadata, inode/entry information queries, node ping diagnostics, and privileged file-state changes. It is the user-space control/query entry point for operations that do not fit standard POSIX VFS calls.

## Important APIs, Types, And Functions
- Dispatchers: `FhgfsOpsIoctl_ioctl()` and `FhgfsOpsIoctl_compatIoctl()`.
- Config/mount probes: `FhgfsOpsIoctl_getCfgFile()`, `FhgfsOpsIoctl_getRuntimeCfgFile()`, `FhgfsOpsIoctl_testIsFhGFS()`, and `FhgfsOpsIoctl_getMountID()`.
- Stripe queries: `FhgfsOpsIoctl_getStripeInfo()`, `FhgfsOpsIoctl_getStripeTarget()`, `FhgfsOpsIoctl_getStripeTargetV2()`, `getStripePatternImpl()`, and `resolveNodeToString()`.
- Creation helpers: `FhgfsOpsIoctl_mkfileWithStripeHints()` and `FhgfsOpsIoctl_createFile()` for ioctl create versions 1 through 3.
- Metadata/diagnostic helpers: `FhgfsOpsIoctl_getInodeID()`, `FhgfsOpsIoctl_getEntryInfo()`, `FhgfsOpsIoctl_pingNode()`, and `FhgfsOpsIoctl_setFileState()`.

## Control Flow
The main ioctl dispatcher logs the command and switches on BeeGFS ioctl numbers. Old `GETVERSION` commands map to `inode->i_generation`; `TCGETS` is rejected as `-ENOTTY` to satisfy `isatty()` probes; unknown commands return `-ENOIOCTLCMD`. The compat dispatcher only remaps 32-bit get-version commands and forwards them to the main dispatcher through `compat_ptr()`.

Simple getters validate user memory implicitly or explicitly, format mount/config strings, and copy bounded data to user space. Stripe target resolution validates that the file is not a directory, reads the inode stripe pattern, resolves buddy-mirror groups into primary/secondary targets, maps targets to node IDs, resolves node aliases from the storage node store, and copies all requested fields to user space.

Creation ioctls check directory permissions and mount writeability, copy versioned argument structures through `IoctlHelper`, build `CreateInfo`, translate preferred targets and storage pool IDs, optionally override uid/gid for privileged callers, construct parent `EntryInfo`, and perform `mkfile` or symlink helper remoting. Cleanup frees all copied strings and target lists and drops mount write references.

`FhgfsOpsIoctl_pingNode()` copies ping parameters, validates node type/count/interval, references the selected node, acquires or reuses a stream socket, sends heartbeat requests, skips the first sample to avoid connection overhead, records latency and NIC type, invalidates sockets on request failure, releases node/socket resources, and copies results back.

`FhgfsOpsIoctl_setFileState()` copies and validates a filename, requires a directory fd and `CAP_SYS_ADMIN`, takes a mount write reference, looks up the target under the parent entry-info lock, validates regular-file type, sends `SetFileState`, then releases lookup output, entry info, and write reference.

## State And Persistence Behavior
Read-only ioctls expose local mount config, runtime proc path, generated inode IDs, `EntryInfo`, and stripe layout. Mutating ioctls create files/symlinks with server-persistent metadata, optional stripe/storage-pool preferences, and event-log records. `SET_FILE_STATE` changes server-side access/data state. Ping does not persist filesystem data but exercises node connection pools and can invalidate a failed socket.

## Dependencies And Integration Points
This file integrates with the public `uapi/beegfs_client.h` ioctl ABI, `IoctlHelper`, `FhgfsOpsRemoting`, `FhgfsOpsHelper`, `FhgfsOpsInode`, `CreateInfo`, `EntryInfo`, `TargetMapper`, `MirrorBuddyGroupMapper`, `NodeStoreEx`, `NodeConnPool`, heartbeat messages, mount write accounting, Linux user-copy helpers, and capability checks.

## Risks
- User-copy structure versioning must stay ABI-compatible with `uapi/beegfs_client.h`.
- Creation ioctls accept many user-supplied pointers/strings and must free all partial allocations on every error path.
- Stripe target queries depend on open-file stripe pattern state; missing pattern returns errors expected to be unreachable.
- `pingNode` loops from `0` through `count` to skip the first sample, so result arrays must be sized for `count` samples after validation.
- `setFileState` must preserve privilege and filename validation because it changes server-side file state outside normal POSIX permissions.
- Mount write references (`mnt_want_write*`) must always be dropped on all post-acquire paths.

## Test Signals
Ioctl ABI tests for 32-bit and 64-bit callers, fuzzed user-copy failures, create-file v1/v2/v3 argument cleanup, stripe info for buddy-mirrored and non-mirrored files, directory/error cases, ping validation and socket failure injection, and privileged/unprivileged `SET_FILE_STATE` tests are key signals.
