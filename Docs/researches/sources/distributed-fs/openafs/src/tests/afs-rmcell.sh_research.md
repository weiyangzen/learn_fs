<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/afs-rmcell.sh -->
# sources/distributed-fs/openafs/src/tests/afs-rmcell.sh

## Purpose
Legacy shell cleanup script for deleting OpenAFS database, configuration, server local/log, and `/vicepa`/`/vicepb` data files.

## Important APIs, Types, And Functions
Sources `OpenAFS/Dirpath.sh` and invokes `/bin/rm -rf` on path variables such as `AFSDBDIR`, `AFSCONFDIR`, `AFSBOSCONFIGDIR`, `AFSLOGSDIR`, and `AFSLOCALDIR`.

## Control Flow
There is no prompting or validation. It removes DB files, server cell config, KeyFile/krb config/UserList, BosConfig, logs, local state, and selected vice partition data, then exits `0`.

## State And Persistence
Destructively deletes local server configuration and volume files, hard-coded to `/vicepa` and `/vicepb`.

## Dependencies And Integration Points
Older counterpart to `afs-rmcell.pl`; depends on the generated Dirpath shell environment.

## Risks And Test Signals
No root check, no confirmation, no service stop, no partition validation, and broad globs make it riskier than the Perl version. Test signal is only command exit status and file absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/afs-rmcell.sh -->
