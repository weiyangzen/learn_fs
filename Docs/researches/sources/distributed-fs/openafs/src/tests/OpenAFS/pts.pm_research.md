<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/pts.pm -->
# sources/distributed-fs/openafs/src/tests/OpenAFS/pts.pm

## Purpose
Provides AFStools Perl wrappers around `pts` user/group and protection database operations.

## Important APIs, Types, And Functions
Exports `AFS_pts_createuser`, `creategroup`, `delete`, `rename`, `examine`, `chown`, `setf`, `listmax`, `setmax`, `add`, `remove`, `members`, and `listown`. `%AFS_Help` records signatures. `AFS_pts_setf` can merge partial access-flag strings with the current flags from `AFS_pts_examine`.

## Control Flow
Each function builds a `pts` subcommand, appends `-cell`, runs `wrapper`, and returns parsed IDs, hashes, lists, or `1`. Membership functions parse indented output lines into arrays. `setf` optionally performs a read-modify-write of the five-character privacy flags.

## State And Persistence
Persistent changes occur in the PTS database: users, groups, ownership, group quota, privacy flags, max ID counters, and memberships. The module stores no long-lived state itself.

## Dependencies And Integration Points
Depends on `OpenAFS::wrapper` and `OpenAFS::util`. ACL test scripts use it to create users/groups before modifying ACLs. `afs-newcell.pl` invokes raw `pts` commands for the initial administrator rather than this module.

## Risks And Test Signals
Parser patterns require exact legacy output. `AFS_pts_setf` tests `$gquota ne ''`, which warns or misbehaves if undef. Create/delete/add/remove smoke tests and ACL tests that resolve PTS names are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/pts.pm -->
