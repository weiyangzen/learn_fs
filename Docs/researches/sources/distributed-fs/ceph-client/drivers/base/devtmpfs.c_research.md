# sources/distributed-fs/ceph-client/drivers/base/devtmpfs.c

## Purpose
`devtmpfs.c` implements the kernel-maintained `/dev` filesystem. It creates an internal tmpfs or ramfs mount, registers a public `devtmpfs` filesystem type that references the existing mount, and serializes device-node create/delete requests through the `kdevtmpfs` kernel thread.

## Important APIs, Types, And Functions
Public entry points are `devtmpfs_init()`, `devtmpfs_mount()`, `devtmpfs_create_node()`, and `devtmpfs_delete_node()`. Internal helpers include `devtmpfs_submit_req()`, `handle_create()`, `handle_remove()`, `create_path()`, `delete_path()`, `dev_mkdir()`, `dev_rmdir()`, `dev_mynode()`, `devtmpfs_work_loop()`, and `devtmpfs_configure_context()`. State includes global `mnt`, worker `thread`, request list, spinlock, and mount boot parameter.

## Control Flow, State, And Persistence
Initialization mounts the backing filesystem with `mode=0755`, configures fs_context ops so external mounts reuse the same superblock, registers the filesystem, and starts `kdevtmpfs` in a private namespace rooted on the internal mount. Device registration calls submit stack-allocated requests, waits for completion, and frees temporary devnode names. Creates derive name, mode, uid/gid, and block/char type from the device, create parent directories, mknod, apply attributes, and tag kernel-created inodes.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies include VFS create/remove helpers, init namespace syscalls, tmpfs/ramfs, block-device detection, device devnode callbacks, idmapped mount API, and early boot init ordering. Risks include synchronous request lifetime, worker availability before requests, protecting user-created nodes from deletion, hardlink permission reset, path length/depth handling, and mount option differences under `CONFIG_DEVTMPFS_SAFE`. Test signals include boot auto-mount, nested device node creation/removal, custom devnode ownership/mode, user-created node preservation, block versus char nodes, and fallback to ramfs.
