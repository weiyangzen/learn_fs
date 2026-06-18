<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/common.h -->
# sources/distributed-fs/openafs/src/libadmin/test/common.h

## Purpose
Provides shared error macros, common command-argument indexes, and global handle declarations for the `afscp` libadmin test modules.

## Important APIs, Types, And Functions
`ERR_EXT` prints an error string and exits. `ERR_ST_EXT` translates an `afs_status_t` through `util_AdminErrorCodeTranslate`, prints message, symbolic text, and numeric code, then exits. `CommonParm_t` fixes parser offsets for `-authuser`, `-authpassword`, `-authcell`, `-execcell`, `-noauth`, and `-usetokens`. The header declares `SetupCommonCmdArgs`, `cellHandle`, and `tokenHandle`.

## Control Flow
Command modules call `SetupCommonCmdArgs(ts)` after adding command-specific options. Runtime hooks in `afscp.c` use the shared indexes to parse auth options and initialize the declared global handles before handlers run.

## State And Persistence
The header declares but does not define `cellHandle` and `tokenHandle`. The macros exit the process immediately on failures, so cleanup is intentionally coarse in this test harness.

## Dependencies And Integration Points
It depends on `util_AdminErrorCodeTranslate` being available via module includes. It ties all `afscp` command modules to the same auth/cell setup convention.

## Risks And Test Signals
Immediate `exit(1)` can skip module-local cleanup, and hard-coded parameter offsets require command modules not to collide with common options. Tests should confirm common options appear at the expected offsets and translated status output is meaningful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/common.h -->
