# sources/distributed-fs/ceph-client/drivers/misc/ibmasm/ibmasmfs.c

## Purpose
`ibmasmfs.c` implements the `ibmasmfs` pseudo filesystem. When mounted, it creates per-service-processor directories with files for dot-command execution, event reads/cancellation, reverse heartbeat control, and remote-video display settings.

## Important APIs, Types, and Functions
Filesystem registration uses `ibmasmfs_register()`, `ibmasmfs_unregister()`, and `ibmasmfs_add_sp()`. Superblock helpers are `ibmasmfs_init_fs_context()`, `ibmasmfs_fill_super()`, `ibmasmfs_make_inode()`, `ibmasmfs_create_file()`, `ibmasmfs_create_dir()`, and `ibmasmfs_create_files()`. File operations are grouped under `command_fops`, `event_fops`, `r_heartbeat_fops`, and `remote_settings_fops`.

## Control Flow
Mount creates a single anonymous superblock root and then iterates the global service-processor list to create directories and files. Command writes validate one complete dot command, allocate a command, execute it synchronously with the protocol-specific timeout, and command reads return the completed response once. Event reads register a reader at open, allow one active blocking read, and writes cancel a sleeper. Reverse heartbeat reads run the periodic heartbeat loop until failure/interruption; writes stop an active loop. Remote settings read/write directly access MMIO display width, height, and depth registers.

## State and Persistence
The global `service_processors` list determines mount contents. Per-open private data stores command, event reader, or reverse-heartbeat state. The filesystem has no backing storage; remote setting writes persist only in service-processor registers.

## Dependencies and Integration Points
It depends on VFS simple directory helpers, anonymous superblocks, dot-command helpers, command/event/reverse-heartbeat modules, and remote register macros. `module.c` registers the filesystem and adds service processors after successful probe.

## Risks and Edge Cases
Service processors are added to a global list but not removed in `ibmasm_remove_one()`, creating a stale pointer risk for later mounts or mounted files after device removal. The list is not locked during mount creation. `remote_settings_file_write()` uses `simple_strtoul()` and writes unchecked values to MMIO. Command reads clear the stored command before verifying copyout success, so failed user copies lose the response.

## Test Signals
Mount/unmount with zero and multiple service processors, command write/read success and timeout, concurrent command reads/writes, event cancellation, reverse heartbeat stop, remote settings MMIO reads/writes, and hot-remove while mounted.
