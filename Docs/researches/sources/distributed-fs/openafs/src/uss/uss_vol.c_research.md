
# sources/distributed-fs/openafs/src/uss/uss_vol.c

Purpose: `uss_vol.c` handles volume and VLDB operations for `uss`: resolving servers and partitions, creating and deleting user volumes, mounting volumes, setting quota/owner/temporary ACL, and discovering volume/server/partition metadata from an existing mount point.

Important APIs and functions: `uss_vol_GetServer()` parses dotted IPv4 or resolves hostnames. `uss_vol_GetPartitionID()` parses numeric, `a`, `vicepa`, or `/vicepa` forms. `uss_vol_CreateVol()` is the main template action for volume creation and setup. `uss_vol_DeleteVol()` calls `UV_DeleteVolume()`. `uss_vol_GetVolInfoFromMountPoint()` reads cache-manager volume status and VLDB entry data into `uss_common` globals. Internal `InitThisModule()` initializes Rx, config, security, VLDB server connections, Ubik client, and `cstruct` for volser helpers. Additional helpers translate host/partition IDs, detect double mount points, and support old/new VLDB entry APIs.

Control flow: create applies command-line overrides over template server/partition/mountpoint values, resolves server/partition, initializes VLDB access, calls `UV_CreateVolume()`, handles existing volume with overwrite prompting and double-mount detection, creates the mountpoint symlink, sets disk quota, records `uss_MountPoint`, chowns mountpoint, pushes final ACL state, and grants temporary creator ACL. Delete initializes VLDB and deletes by server/partition/volume ID. Mountpoint info fetches status through `uss_fs_GetVolStat()`, tolerates missing/unreachable mountpoints by zeroing metadata, then validates VLDB read/write single-server placement.

State and persistence: persistent effects include volume creation/deletion in VLDB/volserver, symlink mountpoints, quota, ownership, and ACLs. Module state includes VLDB connection arrays, `uconn_vldbP`, `NoAuthFlag`, and `initDone`; it also writes volume metadata globals.

Dependencies and integration: depends on Rx, Ubik, VLDB, volser, cache-manager pioctls, host utilities, `uss_acl`, `uss_fs`, and `uss_procs`.

Risks: create is not transactional; failures after `UV_CreateVolume()` can leave volumes or mountpoints behind. Existing-volume overwrite prompts block noninteractive runs unless `-overwrite` is set. Mountpoint symlink creation is implemented directly instead of via `uss_fs_MkMountPoint()`. Fixed buffers and `strcpy()`/`sprintf()` are common. Test signals should cover server/partition parsing, VLDB init without tokens, existing volume/mountpoint paths, dry-run, quota/ACL failures after volume creation, and non-RW or multi-server VLDB entries.
