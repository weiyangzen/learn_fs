# sources/distributed-fs/lizardfs/src/nfs-ganesha/main.c

## Purpose
Registers and configures the LizardFS FSAL module for NFS-Ganesha, parses module/export parameters, creates exports, and initializes pNFS support.

## Important APIs, Types, And Functions
Defines static FSAL info defaults, module-level config items, export config items, `lzfs_fsal_create_export`, `lzfs_fsal_init_config`, `lzfs_fsal_support_ex`, `MODULE_INIT init`, and `MODULE_FINI finish`.

## Control Flow
Module init registers the FSAL, installs module ops, DS ops, export creation, config initialization, and pNFS module ops. Config init copies default static info and applies config file overrides. Export creation allocates `lzfs_fsal_export`, initializes export ops, loads export parameters, initializes the LizardFS client instance with the Ganesha export fullpath as subfolder, attaches the export, optionally sets up pNFS DS fileinfo cache and DS registration, optionally enables pNFS MDS ops, fetches root attributes, and creates the root handle. Finish unregisters the FSAL and aborts if unload fails.

## State And Persistence Behavior
Owns global module object `gLizardFSM` and per-export initialization of `liz_t`, cache parameters, pNFS flags, and root handle. Persistent cluster state is accessed but not stored locally beyond the mounted client instance.

## Dependencies And Integration Points
Depends on Ganesha FSAL init/config/commonlib, pNFS utils, `common/special_inode_defs.h`, `context_wrap`, `lzfs_internal`, and protocol size constants. Integrates the entire FSAL plugin into Ganesha.

## Risks And Edge Cases
Export error cleanup frees the LizardFS instance/cache but does not detach an export if failure occurs after attach. Config defaults bound write workers/cache/timeouts and pNFS cache sizes; mismatch with production load can cause performance issues. Password and md5 password config values are handled as plain config fields. `support_ex` returns true unconditionally.

## Test Signals
Plugin load/unload tests, config parsing tests, export mount failure tests, pNFS DS registration conflicts, and root lookup tests are core signals.
