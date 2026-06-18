<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/kas.pm -->
# sources/distributed-fs/openafs/src/tests/OpenAFS/kas.pm

## Purpose
Wraps `krbkas`/kaserver maintenance commands for principal creation, deletion, inspection, flag/key/password changes, listing, and DES key conversion in the AFStools test harness.

## Important APIs, Types, And Functions
Exports `AFS_kas_create`, `delete`, `examine`, `list`, `setf`, `setkey`, `setpw`, `stringtokey`, and `randomkey`. Helpers `parsestamp`, `stringize_key`, and `unstringize_key` convert command timestamps and 8-byte DES keys. `@kas_err_parse` and `@kas_entry_parse` centralize output parsing.

## Control Flow
Wrappers construct `krbkas` argv, add `-noauth` and `-cell` as needed, and parse command output through `wrapper`. Listing/examination collect stanza fields into hashes, convert flags into arrays, and mark expired principals. Key functions translate binary keys to escaped octal strings for command-line transport.

## State And Persistence
All persistent state lives in the kaserver database and server KeyFile-derived security context. The module mutates principals, passwords, keys, flags, expiration, lockout state, and failed-authentication policy through external commands.

## Dependencies And Integration Points
Depends on `OpenAFS::util`, `OpenAFS::wrapper`, `POSIX::mktime`, and `krbkas`. `afs-newcell.pl` can create a kaserver bnode, but these wrappers are not directly used by the listed smoke scripts.

## Risks And Test Signals
`AFS_kas_create` declares `$print` but uses `$princ`, and `AFS_kas_examine` declares `$vol` but uses `$princ`, which are likely runtime bugs under strictness or warnings. Kaserver is deprecated. Test signals include principal create/examine/list/delete round trips and key conversion returning exactly eight bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/kas.pm -->
