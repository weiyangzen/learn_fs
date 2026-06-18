<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/fs.pm -->
# sources/distributed-fs/openafs/src/tests/OpenAFS/fs.pm

## Purpose
Provides Perl wrappers for `fs` cache-manager and filesystem control commands, including ACLs, quota/volume inspection, mount points, cache flushing, cell/server preferences, sysname, and workstation cell queries.

## Important APIs, Types, And Functions
Exports many `AFS_fs_*` functions: `getacl`, `setacl`, `cleanacl`, quota and volume functions, mount-point functions, flush/check commands, `newcell`, Rx statistics, cache size, cell controls, crypt controls, client addresses, `copyacl`, `storebehind`, server preferences, server checks, exportafs, cache parameters, cell status, monitoring, sysname, `whichcell`, and `wscell`.

## Control Flow
Most functions build `fs` argv and delegate to `wrapper`. Read functions parse output into lists/hashes. `AFS_fs_setacl` emits separate positive and negative `setacl` calls, using `none` for empty rights and special handling for `-clear`. `AFS_fs_examine` computes quota and partition percentages after parsing.

## State And Persistence
State changes are external to the module: directory ACLs, volume quota/MOTD, mount points, cache manager cell list, Rx stat settings, cache size, server prefs, encryption mode, client addresses, monitor host, sysname list, and cache contents.

## Dependencies And Integration Points
Uses `OpenAFS::wrapper` and `OpenAFS::util` globals. The ACL smoke scripts depend heavily on `getacl`, `setacl`, and `copyacl`; setup scripts use mount, ACL, volume, checkvolumes, and wscell helpers.

## Risks And Test Signals
Exact output parsing is fragile across `fs` versions and locales. Several functions treat falsey values carefully, but some option builders may skip intended zero/empty arguments. ACL tests, mount-point creation/removal, `fs examine`, cache preference queries, and workstation-cell discovery are the main integration signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/fs.pm -->
