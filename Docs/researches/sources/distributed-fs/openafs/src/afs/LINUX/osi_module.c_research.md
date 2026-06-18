# sources/distributed-fs/openafs/src/afs/LINUX/osi_module.c

## Purpose
This file is the main Linux OpenAFS filesystem kernel module entry/exit implementation. It initializes global OSI state, syscall hooks, inode cache, filesystem registration, proc/ioctl/sysctl/keyring/pagecopy support, NFS translator hooks, and tears them down on unload.

## Important APIs, types, and functions
- Globals: `afs_global_lock`, `afs_global_owner`, `afs_ns`, and optionally `afs_mnt_idmap`.
- `afs_init_idmap` records the mount idmap from the current fs root for idmapped setattr compatibility.
- `afs_init` is the `module_init` function.
- `afs_cleanup` is the `module_exit` function.
- Module metadata declares the OpenAFS license URL and description.

## Control flow and behavior
Initialization records the current user namespace and mount idmap where configured, calls `osi_Init`, initializes `CellLRU`, initializes NFS translator server hooks unless disabled, installs syscall support, initializes the inode cache, registers `afs_fs_type`, then initializes sysctl, keyring, procfs, ioctl proc endpoint, and background pagecopy support. Error handling unwinds syscall/inode-cache/filesystem setup for early failures.

Cleanup runs the reverse-ish sequence: shutdown pagecopy, keyring, sysctl, syscall support, filesystem registration, inode cache, NFS translator hooks, sleep subsystem, tracked allocator memory, ioctl endpoint, and procfs entries.

## State and persistence
The module maintains global lock ownership, namespace/idmap pointers, registered filesystem/proc/sysctl/keyring state, inode caches, syscall hooks, NFS auth hooks, pagecopy thread, sleep events, and tracked allocations. Persistent user data is not written here; cache/filesystem persistence is handled in lower layers.

## Dependencies and integration points
It integrates all Linux AFS platform components plus the portable cache manager. It depends on `afs_fs_type`, `osi_syscall_*`, `afs_init_inodecache`, `register_filesystem`, sysctl/proc/ioctl/pagecopy/keyring functions, NFS translator hooks, and allocator/sleep shutdown functions.

## Risks
Initialization error unwinding covers early stages but later init calls such as sysctl/keyring/proc/ioctl/pagecopy do not propagate failures. Cleanup order matters: currently `osi_syscall_clean` runs before filesystem unregister and inode cache destruction, while proc/ioctl cleanup occurs after allocator cleanup; any active proc/ioctl use during unload must be quiesced by module reference handling elsewhere. Stored namespace/idmap pointers assume the chosen root context remains valid enough for later setattr wrappers.

## Test signals
Module load/unload tests with and without keyring/NFS translator/idmapped support, failure injection at syscall/inodecache/register_filesystem stages, proc/sysctl/ioctl availability after init, pagecopy thread creation/shutdown, filesystem mount/unmount, and leak checks after unload.
