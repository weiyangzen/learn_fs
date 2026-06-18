<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/config.pm -->
# sources/distributed-fs/openafs/src/tests/OpenAFS/config.pm

## Purpose
Defines site/install-level AFStools defaults used by the test wrappers: configuration directory, command names, command search paths, and error-table directory.

## Important APIs, Types, And Functions
Exports `$def_ConfDir`, `@CmdList`, `@CmdPath`, and `$err_table_dir`. `$def_ConfDir` comes from `OpenAFS::Dirpath`. `@CmdList` names `fs`, `pts`, `vos`, `bos`, `kas`, `krbkas`, and `sys`. `@CmdPath` searches server and workstation binary directories.

## Control Flow
There is no runtime control flow beyond package initialization. `OpenAFS::util::AFS_Init` imports these values and resolves executable paths for every command in `@CmdList`.

## State And Persistence
No persistent state is written. These constants influence which external binaries are executed and where configuration/error-table files are read.

## Dependencies And Integration Points
Depends on `OpenAFS::Dirpath` and `Exporter`. It is consumed by `OpenAFS::util` and `OpenAFS::errtrans`; indirectly every `fs`, `pts`, `vos`, `bos`, and `kas` wrapper depends on it.

## Risks And Test Signals
Hard-coded `$err_table_dir = '/usr/local/lib/errtbl'` may not match build/test installations. Command lookup fails the whole AFStools initialization if any listed binary is missing. Test signals are `AFS_Init()` returning `0` and `errtrans` finding expected error tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/config.pm -->
