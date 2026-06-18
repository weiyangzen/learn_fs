# subset-b-007803 Research

Grouped research for OpenAFS test harness modules, cell setup/removal utilities, BOS/ACL smoke tests, and filesystem stress helpers. Each section preserves its source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/bos.pm -->
# sources/distributed-fs/openafs/src/tests/OpenAFS/bos.pm

## Purpose
Provides the AFStools Perl API for BOS server administration by building `bos` command arguments, applying the global authentication and cell parameters, executing through `OpenAFS::wrapper`, and parsing selected command output into Perl values.

## Important APIs, Types, And Functions
Exports `AFS_bos_addhost`, `addkey`, `adduser`, `create`, `delete`, `exec`, `getdate`, `getlog`, `getrestart`, `install`, `listhosts`, `listkeys`, `listusers`, `prune`, `removehost`, `removekey`, `removeuser`, `restart`, `salvage`, `setauth`, `setcellname`, `setrestart`, `shutdown`, `start`, `startup`, `status`, `stop`, and `uninstall`. `%AFS_Help` documents call signatures. Complex parsers populate arrays/hashes for hosts, keys, superusers, dates, restart times, and bnode status.

## Control Flow
Each wrapper constructs an argv list, conditionally adds `-noauth`, `-localauth`, and `-cell`, runs `wrapper('bos', ...)`, and returns either `1` or parsed structures. `AFS_bos_status` keeps state across output stanzas, flushes the previous bnode when a new `Instance` line appears, and appends parsed command lines.

## State And Persistence
The module itself stores only exported metadata. Operations mutate external BOS state: CellServDB hosts, KeyFile keys, UserList entries, BosConfig bnodes, installed server files, restart schedules, auth policy, running server processes, and salvager side effects.

## Dependencies And Integration Points
Depends on `OpenAFS::util` global parameters and command discovery, `OpenAFS::wrapper` parsing/execution, and the installed `bos` binary. Test scripts in this group call these functions to provision, inspect, start, stop, and remove a `sleeper` bnode plus BOS users, hosts, keys, and salvage actions.

## Risks And Test Signals
Several functions rely on exact legacy English output strings. `AFS_bos_prune` appears to include boolean option names and values in the initial argv and then appends the same flags again, which could produce malformed commands. Test signals are successful BOS smoke scripts, parsed `status -long` fields, correct key checksum parsing, and failure propagation through `wrapper`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/bos.pm -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/errtrans.pm -->
# sources/distributed-fs/openafs/src/tests/OpenAFS/errtrans.pm

## Purpose
Translates between symbolic AFS/com_err/POSIX/Rx/volume error names, numeric error codes, and human-readable strings for the AFStools test environment.

## Important APIs, Types, And Functions
Exports `errcode` and `errstr`. Private helpers `_tbl_to_num`, `_num_to_tbl`, `_load_system_errors`, and `_load_error_table` implement com_err package encoding, reverse decoding, POSIX `errno.h` scanning, and `.et` table parsing. Tables `%Vol_Codes`, `%Vol_Desc`, `%Rx_Codes`, and `%Rx_Desc` cover special OpenAFS values.

## Control Flow
`errcode($pkg,$code)` encodes a com_err table/code directly. `errcode($name)` lazily loads system errors, checks volume/Rx/system maps, tries `POSIX::constant`, and then loads every error table in `$err_table_dir`. `errstr` handles Rx first, optional volume errors, plain system errors, and then com_err table lookups.

## State And Persistence
State is in-memory caches: `%Codes`, `%Desc`, `%Have_Table`, and `%did_include`. Persistent input is `/usr/include` headers and `$err_table_dir` table files.

## Dependencies And Integration Points
Depends on `OpenAFS::config`, `OpenAFS::util`, `Symbol`, and `POSIX`. The module supports wrapper error checking and test diagnostics where OpenAFS tools return numeric com_err/Rx values.

## Risks And Test Signals
The `.et` parser is permissive but simplistic and can silently return on malformed files. Recursive include scanning of `/usr/include` may be platform-sensitive. Test signals include translating known POSIX names, Rx constants, volume constants, table-defined symbols, and unknown values returning `-999` or `Unknown code`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/errtrans.pm -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/util.pm -->
# sources/distributed-fs/openafs/src/tests/OpenAFS/util.pm

## Purpose
Provides shared AFStools initialization, tracing, global parameters, command-path discovery, and AFS-style option parsing used by the Perl command wrappers and tests.

## Important APIs, Types, And Functions
Exports `AFS_Init`, `AFS_Trace`, and `AFS_SetParm`; optional exports include `%AFS_Parms`, `%AFS_Trace`, `%AFS_Help`, `%AFScmd`, `GetOpts_AFS`, and `GetOpts_AFS_Help`. `_which_opt` handles abbreviated option matching.

## Control Flow
`AFS_Init` sets default auth level, config directory, and local cell, then searches configured command paths for every command in `@CmdList`, caching paths in `%AFScmd`. `GetOpts_AFS` consumes explicit and positional AFS-style options, supports boolean, scalar, and multi-argument options, applies defaults, and dies on missing/extra arguments unless help was requested.

## State And Persistence
Stores global in-process state in `%AFS_Parms`, `%AFS_Trace`, `%AFScmd`, and `%AFS_Help`. It reads local cell configuration through `OpenAFS::afsconf` but writes no persistent state.

## Dependencies And Integration Points
Depends on `OpenAFS::config` and requires `OpenAFS::afsconf` to avoid circular imports. All wrapper modules use `%AFScmd` and `%AFS_Parms`; `wrapper.pm` uses tracing and command paths.

## Risks And Test Signals
Missing any command in `@CmdList` makes `AFS_Init` fail even if a specific test needs only one binary. Abbreviation matching returns the ambiguous input unchanged, which later looks like an unknown option. Test signals are successful initialization and option parser coverage for required, default, multi-argument, abbreviated, and unadorned arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/util.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/vos.pm -->
# sources/distributed-fs/openafs/src/tests/OpenAFS/vos.pm

## Purpose
Wraps `vos` volume/VLDB commands for volume creation, removal, movement, replication, dumps/restores, synchronization, locking, partition status, listing, and transaction status.

## Important APIs, Types, And Functions
Exports `AFS_vos_create`, `remove`, `rename`, `move`, `examine`, `addsite`, `remsite`, `release`, `backup`, `backupsys`, `dump`, `restore`, `listvldb`, `delentry`, `syncserv`, `syncvldb`, `lock`, `unlock`, `unlockvldb`, `changeaddr`, `listpart`, `partinfo`, `listvol`, `zap`, and `status`. `$vos_err_parse` extracts the specific error from the line preceding `Error in vos ... command`.

## Control Flow
Functions build `vos` argv, apply auth/cell/vostrace flags, and call `wrapper`. Listing functions parse multi-line volume stanzas, flushing accumulated hashes when a new stanza starts. Dump can pass stdout directly when no output file is supplied.

## State And Persistence
External persistent state includes volumes, VLDB entries, replication sites, read-only releases, backup volumes, dump/restore data, transaction locks, server addresses, partition contents, and volume server transaction state.

## Dependencies And Integration Points
Depends on `OpenAFS::util` and `OpenAFS::wrapper`. `afs-newcell.pl`, `baduniq.pl`, and helper tests use volume creation, restore, salvage, mount, release, and inspection paths.

## Risks And Test Signals
The module is highly sensitive to `vos` output format. `vostrace` can alter parsing by forwarding all output. Full coverage needs create/examine/listvldb/listvol/addsite/release/remove and dump/restore tests, including error parsing from failed volume operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/vos.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/wrapper.pm -->
# sources/distributed-fs/openafs/src/tests/OpenAFS/wrapper.pm

## Purpose
Implements the generic subprocess execution and line-oriented parsing engine used by the AFStools wrappers, plus a generated-code `fast_wrapper` variant.

## Important APIs, Types, And Functions
Exports `wrapper`; optionally exports `fast_wrapper`. `_fastwrap_gen` emits Perl code for a parsing instruction list. Parser actions support scalar, array, hash, code, result-key strings, stop-line `.`, skip `+n`, error `-`, and print `?`.

## Control Flow
`wrapper` combines built-in wrapper/command error patterns with caller parse instructions, resolves the executable path from `%AFScmd` unless overridden, forks with a pipe, redirects stderr/stdout according to options, execs the command, and applies every parsing instruction to each output line until EOF or an exception. `fast_wrapper` compiles equivalent parser code, forks similarly, and invokes the generated parser.

## State And Persistence
Uses dynamic local `%result` for parser output and reads `%AFS_Trace`/`%AFScmd`; it writes no persistent state. Side effects are entirely from the invoked child command and optional pass-through output.

## Dependencies And Integration Points
Depends on `OpenAFS::util`, `Exporter`, and `Symbol`. All `bos`, `fs`, `pts`, `vos`, and `kas` modules route command execution through it.

## Risks And Test Signals
The code often checks `%options` as `$options{...}` instead of `$options->{...}`, so `pass_stdout`/`pass_stderr` behavior may not match the supplied hash reference. `exec($path $cmd, @$args)` is unusual and risks argv/path bugs. Fast wrapper generation contains fragile emitted hash/code action logic. Signals are wrapper unit tests for stderr capture, stdout pass-through, parse actions, command-not-found, and generated parser parity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/wrapper.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/acladdgroup.pl -->
# sources/distributed-fs/openafs/src/tests/acladdgroup.pl

## Purpose
Smoke-tests adding a PTS group to a directory's positive ACL in the workstation cell.

## Important APIs, Types, And Functions
Calls `AFS_Init`, `AFS_fs_wscell`, `AFS_pts_creategroup`, `AFS_fs_getacl`, and `AFS_fs_setacl`.

## Control Flow
Initializes AFStools, finds the workstation cell, best-effort creates `group1`, creates `/afs/<cell>/service/acltest`, snapshots ACLs, adds `group1 rl`, reads ACLs again, and exits nonzero unless exactly one positive entry for `group1` is found.

## State And Persistence
Creates or reuses PTS group `group1`, creates an AFS directory, and mutates its positive ACL. It does not restore the original ACL or remove the group.

## Dependencies And Integration Points
Depends on the AFStools Perl modules, writable `/afs/<cell>/service`, PTS service, and cache manager ACL commands.

## Risks And Test Signals
The test assumes `service/acltest` can be created and that prior ACL state will not contain duplicate `group1` entries. Success is exit `0`; any missing positive ACL entry exits `1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/acladdgroup.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/acladdnegrights.pl -->
# sources/distributed-fs/openafs/src/tests/acladdnegrights.pl

## Purpose
Verifies adding negative ACL rights for a PTS user.

## Important APIs, Types, And Functions
Uses `AFS_Init`, `AFS_fs_wscell`, `AFS_pts_createuser`, `AFS_fs_getacl`, and `AFS_fs_setacl`.

## Control Flow
Creates `user1` if possible, makes `/afs/<cell>/service/acltest`, records ACLs, calls `AFS_fs_setacl` with an empty positive ACL and negative `user1 rl`, then scans the returned negative ACL for exactly one `user1` entry.

## State And Persistence
Persists PTS user `user1`, directory creation, and a negative ACL entry. No cleanup is attempted.

## Dependencies And Integration Points
Requires the protection database, `fs setacl -negative`, and a writable service volume.

## Risks And Test Signals
Preexisting negative entries can affect the exact count. The test does not validate rights string beyond presence. Exit `0` means the negative ACL entry was found once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/acladdnegrights.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/acladdrights.pl -->
# sources/distributed-fs/openafs/src/tests/acladdrights.pl

## Purpose
Checks that setting an existing/new positive ACL entry to broader rights (`rlidw`) is reflected by `fs listacl`.

## Important APIs, Types, And Functions
Uses `AFS_pts_createuser`, `AFS_fs_getacl`, and `AFS_fs_setacl` after AFStools initialization.

## Control Flow
Creates `user1`, creates the ACL test directory, captures original ACLs, sets `user1 rlidw`, reads ACLs again, and exits `1` if the matching entry has any rights string other than `rlidw`.

## State And Persistence
Adds or modifies `user1` on the positive ACL and leaves the directory/user in place.

## Dependencies And Integration Points
Tests the `OpenAFS::fs` ACL representation and the underlying `fs setacl/listacl` round trip.

## Risks And Test Signals
The script builds unused temporary arrays and does not restore original rights. Success is an exact rights-string parse from command output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/acladdrights.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/acladduser.pl -->
# sources/distributed-fs/openafs/src/tests/acladduser.pl

## Purpose
Smoke-tests adding a PTS user to a positive ACL with read/list rights.

## Important APIs, Types, And Functions
Calls `AFS_Init`, `AFS_fs_wscell`, `AFS_pts_createuser`, `AFS_fs_getacl`, and `AFS_fs_setacl`.

## Control Flow
Initializes, creates `user1`, creates the common ACL test directory, sets `user1 rl`, then scans the positive ACL for one matching user entry.

## State And Persistence
Creates `user1`, creates `/afs/<cell>/service/acltest`, and leaves an ACL entry behind.

## Dependencies And Integration Points
Exercises PTS user creation and filesystem ACL mutation through the shared wrapper modules.

## Risks And Test Signals
Preexisting ACL state can mask or duplicate the target entry. Exit `0` is the only success signal; failures are by explicit exit `1` or wrapper exception.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/acladduser.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/aclclearnegrights.pl -->
# sources/distributed-fs/openafs/src/tests/aclclearnegrights.pl

## Purpose
Tests changing/clearing negative ACL rights for `user1` and comparing the resulting ACL shape.

## Important APIs, Types, And Functions
Uses `AFS_pts_createuser`, `AFS_fs_getacl`, and `AFS_fs_setacl` with negative ACL input.

## Control Flow
Creates `user1`, creates the ACL test directory, reads initial ACLs, sets negative `user1 r`, verifies the read-back rights are `r`, then compares reconstructed negative/positive ACL arrays with prior state and exits nonzero on mismatch.

## State And Persistence
Mutates the directory's negative ACL. It leaves the PTS user and directory present.

## Dependencies And Integration Points
Depends on negative ACL support in `fs setacl` and list parsing in `OpenAFS::fs`.

## Risks And Test Signals
Array comparisons use Perl scalar array length, not deep ACL equality, so the check is weak. Success signals only that the target negative rights were parsed as `r` and counts matched.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/aclclearnegrights.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/aclcopy.pl -->
# sources/distributed-fs/openafs/src/tests/aclcopy.pl

## Purpose
Verifies copying one directory ACL to another through `fs copyacl`.

## Important APIs, Types, And Functions
Uses `AFS_fs_copyacl`, `AFS_fs_getacl`, `AFS_fs_wscell`, and setup calls.

## Control Flow
Creates `acltest` and `acltest2` under `/afs/<cell>/service`, reads ACLs from the source, calls `AFS_fs_copyacl($path, [$path2], 1)` to clear/copy to the target, reads target ACLs, and compares positive and negative ACL entry counts.

## State And Persistence
Creates two directories and overwrites the target ACL. No cleanup is performed.

## Dependencies And Integration Points
Exercises `OpenAFS::fs::AFS_fs_copyacl` and `fs listacl` parsing.

## Risks And Test Signals
The test checks only array lengths, not entry identity or rights. Exit `0` means target positive/negative ACL counts matched source counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/aclcopy.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/aclremovegroup.pl -->
# sources/distributed-fs/openafs/src/tests/aclremovegroup.pl

## Purpose
Attempts to remove `group1` from the positive ACL on the common ACL test directory.

## Important APIs, Types, And Functions
Uses `AFS_fs_getacl` and `AFS_fs_setacl` after AFStools initialization.

## Control Flow
Reads current positive ACL, scans for `group1`, builds a string that resembles an ACL list for remaining entries, exits `1` if `group1` was absent, and calls `AFS_fs_setacl` with the constructed value.

## State And Persistence
Mutates `/afs/<cell>/service/acltest` ACL if the wrapper accepts the generated list. Leaves directory in place.

## Dependencies And Integration Points
Depends on prior `acladdgroup.pl` state and the `OpenAFS::fs` ACL setter.

## Risks And Test Signals
`$listref` is a string, not an array reference matching `AFS_fs_setacl`'s API, so this script may fail or behave unexpectedly. Success is weak because it does not verify that the group was actually removed after the call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/aclremovegroup.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/aclremoveuser.pl -->
# sources/distributed-fs/openafs/src/tests/aclremoveuser.pl

## Purpose
Attempts to remove `user1` from the positive ACL on the common ACL test directory.

## Important APIs, Types, And Functions
Uses AFStools initialization, `AFS_fs_wscell`, `AFS_fs_getacl`, and `AFS_fs_setacl`.

## Control Flow
Scans the positive ACL for `user1`, constructs a list-like string of other entries, fails if `user1` was not found, calls `AFS_fs_setacl`, and exits `0` without confirming the postcondition.

## State And Persistence
Intended to mutate the ACL by removing `user1`, but leaves all other test state intact.

## Dependencies And Integration Points
Depends on state produced by earlier ACL user tests and on `OpenAFS::fs` accepting a correctly structured positive ACL argument.

## Risks And Test Signals
The same string-vs-array-reference bug as `aclremovegroup.pl` likely invalidates the setter call. A meaningful test signal would require a post-call `getacl` check for absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/aclremoveuser.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/afs-newcell.pl -->
# sources/distributed-fs/openafs/src/tests/afs-newcell.pl

## Purpose
Interactive or batch provisioning script for creating an initial test OpenAFS cell with database servers, file server, client startup, root volumes, replicated/unreplicated test volumes, ACLs, and Kerberos/kaserver security initialization.

## Important APIs, Types, And Functions
Defines `prompt`, `mkvol`, and `check_program`. Uses `OpenAFS::ConfigUtils::run/unwind`, `OpenAFS::Dirpath`, `OpenAFS::OS`, `OpenAFS::Auth`, `Getopt::Long`, `Pod::Usage`, and `Socket`. Options control batch/debug/unwind, server, cell, partition, admin principal, Kerberos type/realm/keytab, DAFS mode, and server command options.

## Control Flow
Validates root, absence of prior config/database files, required binaries, keytab/auth mode, hostname forward/reverse lookup, partition id, empty `/vicep<part>`, and stopped server processes. It writes `run-tests.conf`, stops services, configures client files, creates required directories, starts `bosserver -noauth`, sets cell/host/user, starts ptserver/vlserver and optional kaserver, creates security keys/admin, restarts DB servers, starts file services, creates `root.afs`, starts client, authorizes as admin, creates/mounts/releases `root.cell`, creates `user`, `service`, `unrep`, and `rep`, adds RO sites, and clears unwind actions on success.

## State And Persistence
Writes AFS configuration files, BosConfig, databases, KeyFile/krb config, `run-tests.conf`, server directories, `/vicep<part>` volume data, PTS admin entries, VLDB entries, volumes, mount points, ACLs, and saved batch script when requested. On failure, the `END` block can run queued unwind commands.

## Dependencies And Integration Points
Integrates OS-specific service control, Kerberos/auth helpers, BOS/VOS/PTS/FS binaries, DNS, vice partitions, and the local cache manager. Later smoke tests assume the volumes and `/afs/<cell>/service` tree created here.

## Risks And Test Signals
The script is intentionally destructive and root-only. Quoting of saved shell options is simple and can be unsafe for unusual values. Sleeps assume startup timing. Unwind cannot guarantee complete rollback after partial server/database changes. Signals include successful `info: DONE`, running BOS/DB/file servers, created volumes, released RO paths, valid tokens, and passing follow-on ACL/BOS tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/afs-newcell.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/afs-rmcell.pl -->
# sources/distributed-fs/openafs/src/tests/afs-rmcell.pl

## Purpose
Root-only cleanup utility that removes local OpenAFS cell configuration, databases, logs, local state, and volume files for a selected vice partition.

## Important APIs, Types, And Functions
Uses `OpenAFS::Dirpath`, `OpenAFS::OS`, `OpenAFS::ConfigUtils::run`, `Term::ReadLine`, `Getopt::Long`, and `Pod::Usage`. Options are `--debug`, `--help`, `--batch`, `--partition-id`, and `--ostype`.

## Control Flow
Parses options, checks root, validates the partition abbreviation, prompts for the literal confirmation word `destroy` unless batch mode is used, creates an OS helper, configures the client, stops client/fileserver services, force-stops the client, and removes database, BosConfig, logs, local files, cell config, KeyFile, krb.conf, client CellServDB/ThisCell, and `/vicep<id>` volume data/locks.

## State And Persistence
Deletes persistent OpenAFS state from AFS db/config/local/log directories and one vice partition. It does not remove arbitrary nonstandard partition names.

## Dependencies And Integration Points
Complements `afs-newcell.pl`; the new-cell script points users to this cleanup when old config files exist.

## Risks And Test Signals
Highly destructive by design. Batch mode bypasses confirmation. Removal uses OS helper glob behavior, so quoting/platform semantics matter. Success signal is stopped services and missing config/database/volume files before rerunning `afs-newcell.pl`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/afs-rmcell.pl -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/afscp.c -->
# sources/distributed-fs/openafs/src/tests/afscp.c

## Purpose
Direct RX fileserver copy/lock utility used to exercise AFS fetch/store paths independently of normal file I/O. It can copy local-to-AFS, AFS-to-local, AFS-to-AFS, and release an AFS file lock.

## Important APIs, Types, And Functions
Key functions are `statfile`, `start_cb_server`, `do_rx_Init`, `get_sc`, `int_handler`, and `main`. It uses `pioctl` operations `VIOC_FILE_CELL_NAME`, `VIOCGETFID`, and `VIOCWHEREIS`; RX calls such as `RXAFS_CreateFile`, `FetchStatus`, `Start/EndRXAFS_FetchData`, `Start/EndRXAFS_StoreData`, `ReleaseLock`, and `GiveUpCallBacks`.

## Control Flow
Options set block size, local source/destination modes, sleep delay, unauthenticated mode, unlock mode, and loop duration. `statfile` resolves either normal AFS paths via pioctl or explicit `@afs:cell:server:volume:vnode:uniq`. Main initializes RX and a callback service, creates source/destination connections, creates or opens the destination, fetches status, streams bytes between local fds and RX calls, optionally loops until time/SIGINT, gives up callbacks, reports transfer rate, and exits nonzero on fetch/store errors.

## State And Persistence
Creates/truncates local files or AFS files and may release AFS locks. Maintains transient RX connections/calls, callback registration, data buffers, and security classes.

## Dependencies And Integration Points
Depends on OpenAFS RX, fileserver interfaces, callback stubs from `afscp_callback.c`, pioctl cache-manager access, DNS, and null RX security in this build.

## Risks And Test Signals
Authentication is effectively forced to null (`sscindex = scindex_NULL`), so secure-copy coverage is limited. Error cleanup relies on goto labels and can use partially initialized state. `strncpy` may not NUL-terminate long cell names. Signals include successful copy in all mode combinations, unlock output, callback give-up messages absent, and expected transfer-rate reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/afscp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/afscp_callback.c -->
# sources/distributed-fs/openafs/src/tests/afscp_callback.c

## Purpose
Provides minimal RXAFSCB callback service implementations needed by `afscp.c` so fileservers can probe or identify the client during direct RX fetch/store tests.

## Important APIs, Types, And Functions
Defines globals `afs_cb_inited` and `afs_cb_interface`, helper `init_afs_cb`, and many `SRXAFSCB_*` RPC handlers. Most handlers return success with no data or `RXGEN_OPCODE`; `WhoAreYou` and `ProbeUuid` return meaningful interface/UUID data.

## Control Flow
`init_afs_cb` creates a UUID, gathers local interface addresses with `rx_getAllAddr`, converts addresses to host byte order for XDR, and marks initialized. `WhoAreYou` lazily initializes and copies the interface address. `ProbeUuid` compares the supplied UUID to the local callback UUID.

## State And Persistence
Only transient process globals store callback UUID and interface addresses. No disk state is written.

## Dependencies And Integration Points
Compiled with `afscp.c`, OpenAFS callback interface definitions, RX utilities, and the RX callback service registered by `start_cb_server`.

## Risks And Test Signals
Most callbacks are stubs, so this is sufficient for simple copy tests but not cache manager behavior validation. Multihomed address handling depends on `AFS_MAX_INTERFACE_ADDR`. Signals are fileserver callbacks/probes succeeding during `afscp` transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/afscp_callback.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/append-over-page.c -->
# sources/distributed-fs/openafs/src/tests/append-over-page.c

## Purpose
Tests append writes crossing page-sized/cache boundaries and validates read consistency by comparing normal read data to `mmap` data.

## Important APIs, Types, And Functions
Defines large static `long_buf`, `compare_file`, `doit`, and `main`. Uses `open`, `write`, `close`, `fstat`, `read`, `mmap`, `memcmp`, and `err` diagnostics.

## Control Flow
Creates/truncates a file, appends `foobar\n`, closes it, compares read-vs-mmap views, reopens in append mode, writes `long_buf`, closes, and compares again. The optional argv file name defaults to `blaha`.

## State And Persistence
Creates or overwrites the target test file and leaves it present. Allocates temporary read buffers and maps the file read-only.

## Dependencies And Integration Points
Exercises the filesystem/cache manager under test through POSIX append, mmap, read, and close semantics.

## Risks And Test Signals
It does not unmap `mmap_buf`, though process exit reclaims it. Non-ASCII copyright bytes are present in comments. Success is exit `0`; failures identify open/write/read/mmap/compare errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/append-over-page.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/append1 -->
# sources/distributed-fs/openafs/src/tests/append1

## Purpose
Shell smoke test for append redirection and file content preservation.

## Important APIs, Types, And Functions
Uses `$objdir/echo-n`, shell redirection, `cat`, `test`, and `rm`.

## Control Flow
Writes `hej` without newline to `foo`, verifies exact content, appends `hopp`, verifies `hejhopp`, and removes the file.

## State And Persistence
Creates and deletes `foo` in the current test directory.

## Dependencies And Integration Points
Depends on the built `echo-n` helper and a shell running in the filesystem under test.

## Risks And Test Signals
Backtick command substitution strips trailing newlines, which is acceptable because `echo-n` suppresses them. Exit `0` confirms basic append semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/append1 -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/apwd.c -->
# sources/distributed-fs/openafs/src/tests/apwd.c

## Purpose
Tests pathname reconstruction and current-working-directory behavior, including libc `getcwd`, a direct Linux `getcwd` syscall path when available, a classic inode-walking implementation, and a Linux `/proc/self/cwd` implementation.

## Important APIs, Types, And Functions
Important helpers include `initial_string`, `expand_string`, `guarantee_room`, `getcwd_classic`, optional `getcwd_proc`, optional `getcwd_syscall`, `test_1`, `test_it`, `usage`, and `main`. It uses `lstat`, `opendir/readdir`, `readlink`, buffer growth, `agetarg`, and verbose logging.

## Control Flow
The classic implementation walks upward using `..`, compares device/inode pairs to root, scans parent directories to find the current name, and prepends path components into a dynamically growing buffer. `test_1` compares each implementation with libc `getcwd`, including caller-supplied buffers, allocated buffers, ERANGE growth behavior, and overwrite guards. `main` parses `--verbose`/`--help`, writes diagnostics to fd 4 when available, and runs libc, syscall, classic, and proc variants according to platform macros.

## State And Persistence
No persistent filesystem writes are intended. It allocates transient buffers and writes verbose diagnostics to file descriptor 4 or `/dev/null`.

## Dependencies And Integration Points
`checkpwd` invokes this binary. It validates directory/inode behavior of the filesystem under test, including mount-point transitions, direct kernel getcwd behavior, Linux procfs behavior, and buffer boundary handling.

## Risks And Test Signals
`guarantee_room` uses `opr_min(*size * 2, len)`, which appears inverted for ensuring room and may not grow enough. Filesystems with unstable inode/device reporting will fail classic reconstruction. Signals are zero exit and matching custom/libc paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/apwd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/asu.c -->
# sources/distributed-fs/openafs/src/tests/asu.c

## Purpose
Small privilege-drop wrapper for running a program as a named user during tests.

## Important APIs, Types, And Functions
Defines `usage` and `main`. Uses `getpwnam`, `setgroups`, `setgid`, `setuid`, `setegid`, `seteuid`, and `execvp`.

## Control Flow
Requires `user program [args...]`. If running as root, resolves the user, switches primary group and uid/euid/gid/egid to that account, then `execvp`s the requested program. If not root, it simply execs the program.

## State And Persistence
No filesystem persistence. It changes process credentials before replacing the process image.

## Dependencies And Integration Points
Useful for tests requiring non-root user semantics against AFS ACLs and tokens.

## Risks And Test Signals
If any credential change fails, it exits through `err`. It does not call `initgroups`, so supplementary groups are reduced to one primary group. Success is the child program's exit status after credential switch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/asu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/baduniq.pl -->
# sources/distributed-fs/openafs/src/tests/baduniq.pl

## Purpose
Regression test for restoring/salvaging a volume with problematic vnode uniquifier data and verifying a file is visible afterward.

## Important APIs, Types, And Functions
Uses `AFS_vos_restore`, `AFS_bos_salvage`, `AFS_fs_mkmount`, and `AFS_fs_rmmount`.

## Control Flow
Restores volume `badvol` on localhost partition `a` from `/tmp/t.uniq-bad` using id `100` and full overwrite, salvages it, mounts it at `badvol`, checks for `badvol/test`, removes the mount point, and exits `0` only if the file exists.

## State And Persistence
Creates/restores `badvol`, invokes salvage, creates/removes a mount point, and leaves the restored volume unless external cleanup removes it.

## Dependencies And Integration Points
Depends on a prepared dump file `/tmp/t.uniq-bad`, working VOS/BOS/FS wrappers, and a test cell.

## Risks And Test Signals
The dump path is absolute and external to the repository. The test does not remove the volume. Success indicates the salvaged volume exposes the expected file through a mount point.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/baduniq.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/blocks-new-file.c -->
# sources/distributed-fs/openafs/src/tests/blocks-new-file.c

## Purpose
Checks that a newly created sparse-ish file reports nonzero allocated block count after a seek-and-write.

## Important APIs, Types, And Functions
Defines `doit` and `main`. Uses `open`, `lseek`, `write`, `close`, `stat`, `unlink`, and `st_blocks`.

## Control Flow
Creates/truncates a file, seeks to 1 MiB, writes three bytes, closes, stats, unlinks, and fails if `st_blocks == 0`.

## State And Persistence
Temporarily creates a target file (`foo` by default), then removes it.

## Dependencies And Integration Points
Exercises filesystem allocation/stat behavior after sparse writes in the current directory.

## Risks And Test Signals
Some filesystems legitimately report block counts differently, so this is a portability-sensitive test. Exit `0` confirms nonzero `st_blocks`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/blocks-new-file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/boot-strap-arla -->
# sources/distributed-fs/openafs/src/tests/boot-strap-arla

## Purpose
Build stress test that unpacks and compiles an Arla release tree, including the `milko` subcomponent, inside the filesystem under test.

## Important APIs, Types, And Functions
Shell script using `FAST`, `AFSROOT`, `mkdir`, `gzip`, `tar`, `configure`, and `make`.

## Control Flow
Skips when `FAST` is set. Creates `src` and `obj`, extracts `arla-0.34.tar.gz` from `$AFSROOT`, configures from the object directory, runs `make`, enters `milko`, and builds again.

## State And Persistence
Creates source/object trees and build outputs in the current directory.

## Dependencies And Integration Points
Depends on an AFS mirror path under `$AFSROOT`, build tools, and enough workspace. It stresses metadata, directory traversal, hardlinks/symlinks as used by the build, and large file I/O.

## Risks And Test Signals
External archive availability and old build dependencies are brittle. Success is complete configure/build exit `0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/boot-strap-arla -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosaddhost.pl -->
# sources/distributed-fs/openafs/src/tests/bosaddhost.pl

## Purpose
Smoke-tests adding a BOS database server host entry.

## Important APIs, Types, And Functions
Calls `AFS_Init` and `AFS_bos_addhost(localhost, "128.2.1.2")`.

## Control Flow
Reads hostname but does not use it, initializes AFStools, adds the hard-coded host to localhost's BOS host list, and exits `0` if the wrapper does not throw.

## State And Persistence
Adds `128.2.1.2` to the server CellServDB/BOS host list.

## Dependencies And Integration Points
Part of the BOS host add/list/remove smoke sequence.

## Risks And Test Signals
Uses a hard-coded IP address and assumes localhost BOS access. Follow-on `boslisthosts.pl` verifies presence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosaddhost.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosaddkey.pl -->
# sources/distributed-fs/openafs/src/tests/bosaddkey.pl

## Purpose
Tests adding a BOS server encryption key with key version number 250.

## Important APIs, Types, And Functions
Calls `AFS_bos_addkey(localhost, "\000...\007", 250)`.

## Control Flow
Initializes AFStools, submits an eight-byte binary key to `bos addkey`, and exits `0` on wrapper success.

## State And Persistence
Persists a key in the server KeyFile/key list.

## Dependencies And Integration Points
Follow-on `boslistkeys.pl` checks the key checksum and `bosremovekey.pl` removes it.

## Risks And Test Signals
Binary NULs in Perl string arguments and shell/exec handling are the key risk. Success means `bos addkey` accepted the key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosaddkey.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosadduser.pl -->
# sources/distributed-fs/openafs/src/tests/bosadduser.pl

## Purpose
Adds `testuser1` to the BOS superuser list.

## Important APIs, Types, And Functions
Calls `AFS_bos_adduser(localhost, [testuser1])`.

## Control Flow
Initializes AFStools, calls the BOS wrapper, and exits on success.

## State And Persistence
Mutates the server UserList/superuser list.

## Dependencies And Integration Points
Used with `boslistusers.pl` and `bosremoveuser.pl` to verify list mutation.

## Risks And Test Signals
Uses bareword `testuser1`; under this non-strict script it becomes a string. Success is later list output containing `testuser1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosadduser.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/boscreate.pl -->
# sources/distributed-fs/openafs/src/tests/boscreate.pl

## Purpose
Creates and starts a simple BOS bnode named `sleeper` for BOS lifecycle tests.

## Important APIs, Types, And Functions
Uses local file I/O, `chmod`, `AFS_bos_install`, and `AFS_bos_create`.

## Control Flow
Writes an executable `sleeper.sh` that sleeps forever, installs it through BOS, creates a simple bnode with command `/usr/afs/bin/sleeper.sh`, and exits `0`.

## State And Persistence
Creates local `sleeper.sh`, installs it into the server binary directory, and writes a BosConfig entry for the `sleeper` bnode.

## Dependencies And Integration Points
Foundational state for `bosstatus`, `bosstop`, `bosstart`, `bosshutdown`, `bosrestartstopped`, `bosdeleterunning`, and `bosdelete`.

## Risks And Test Signals
Hard-codes `/usr/afs/bin/sleeper.sh`, which may not match Dirpath on all platforms. Success is a running `sleeper` status stanza.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/boscreate.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosdelete.pl -->
# sources/distributed-fs/openafs/src/tests/bosdelete.pl

## Purpose
Deletes the `sleeper` BOS bnode after lifecycle tests.

## Important APIs, Types, And Functions
Calls `AFS_bos_delete(localhost, sleeper)`.

## Control Flow
Initializes AFStools, invokes delete, and exits `0` if the wrapper succeeds.

## State And Persistence
Removes the `sleeper` BosConfig instance; it does not uninstall the script file.

## Dependencies And Integration Points
Requires a stopped/removable bnode created by `boscreate.pl`.

## Risks And Test Signals
Bareword `sleeper` relies on old Perl semantics. Deleting a running bnode is separately tested to fail in `bosdeleterunning.pl`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosdelete.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosdeleterunning.pl -->
# sources/distributed-fs/openafs/src/tests/bosdeleterunning.pl

## Purpose
Negative test ensuring BOS refuses or errors when deleting a running `sleeper` bnode.

## Important APIs, Types, And Functions
Uses `eval { AFS_bos_delete(...) }` to inspect wrapper exceptions.

## Control Flow
Initializes AFStools, attempts to delete `sleeper`, exits `1` if no exception was raised, and exits `0` if an exception occurred.

## State And Persistence
Intended not to mutate state; if deletion unexpectedly succeeds, the bnode is removed and the test fails.

## Dependencies And Integration Points
Depends on `sleeper` being running from previous BOS lifecycle setup.

## Risks And Test Signals
The signal is inverted: success means a wrapper error was thrown. Any output-format change that hides the BOS error could invalidate the test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosdeleterunning.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosexec.pl -->
# sources/distributed-fs/openafs/src/tests/bosexec.pl

## Purpose
Tests remote BOS execution of an installed script by checking for its side effect.

## Important APIs, Types, And Functions
Uses `AFS_bos_exec`, `OpenAFS::ConfigUtils`, `OpenAFS::Dirpath`, and `OpenAFS::OS`.

## Control Flow
Initializes AFStools, calls `bos exec` for `$openafsdirpath->{'afssrvbindir'}/foo.sh`, verifies `/tmp/garbage` was created, deletes it, and exits `0`.

## State And Persistence
Runs server-side command and temporarily creates `/tmp/garbage`.

## Dependencies And Integration Points
Requires `bosinstall.pl` to install `foo.sh` first and expects Dirpath global availability.

## Risks And Test Signals
The script references `$openafsdirpath` without qualification/import visible in the file, which may be a bug unless imported by modules. Success is the `/tmp/garbage` side effect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosexec.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosinstall.pl -->
# sources/distributed-fs/openafs/src/tests/bosinstall.pl

## Purpose
Tests installing an executable file through BOS.

## Important APIs, Types, And Functions
Creates `foo.sh`, sets executable mode, and calls `AFS_bos_install(localhost, ["foo.sh"])`.

## Control Flow
Writes a shell script that touches `/tmp/garbage`, chmods it, installs it with BOS, and exits `0`.

## State And Persistence
Creates local `foo.sh` and installs it into the server binary area.

## Dependencies And Integration Points
Prepares state for `bosexec.pl`.

## Risks And Test Signals
No cleanup of installed file. Success is `bos install` output accepted by the wrapper and later executable via BOS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosinstall.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/boslisthosts.pl -->
# sources/distributed-fs/openafs/src/tests/boslisthosts.pl

## Purpose
Verifies BOS host list contains the workstation cell name, local hostname, and optionally the added hard-coded host.

## Important APIs, Types, And Functions
Uses `AFS_fs_wscell` and `AFS_bos_listhosts`.

## Control Flow
Gets local hostname and cell, lists hosts from localhost, checks first returned item equals the cell name, then accepts each host only if it is the local hostname or `128.2.1.2`.

## State And Persistence
Read-only.

## Dependencies And Integration Points
Follows `bosaddhost.pl` and validates `OpenAFS::bos` output parsing.

## Risks And Test Signals
Hostname canonicalization differences can fail the test. Exit `0` confirms parsed host list contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/boslisthosts.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/boslistkeys.pl -->
# sources/distributed-fs/openafs/src/tests/boslistkeys.pl

## Purpose
Verifies the added test key appears in `bos listkeys` with an expected checksum.

## Important APIs, Types, And Functions
Calls `AFS_bos_listkeys(localhost)`.

## Control Flow
Lists keys, iterates returned hash keys, and if key version 250 is present, requires the checksum to match one of two accepted values.

## State And Persistence
Read-only.

## Dependencies And Integration Points
Depends on `bosaddkey.pl` having added kvno 250 and the wrapper parsing checksum output.

## Risks And Test Signals
The test does not fail if kvno 250 is absent because it only checks when seen. Success is therefore weak; meaningful signal is presence with accepted checksum.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/boslistkeys.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/boslistusers.pl -->
# sources/distributed-fs/openafs/src/tests/boslistusers.pl

## Purpose
Checks BOS superuser list after adding `testuser1`.

## Important APIs, Types, And Functions
Calls `AFS_bos_listusers(localhost)`.

## Control Flow
Lists superusers and allows only `admin` and `testuser1`; any other listed user exits `1`.

## State And Persistence
Read-only.

## Dependencies And Integration Points
Depends on the UserList state from `afs-newcell.pl` and `bosadduser.pl`.

## Risks And Test Signals
Sites with extra legitimate superusers will fail. Exit `0` indicates list parsing and expected state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/boslistusers.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosremovehost.pl -->
# sources/distributed-fs/openafs/src/tests/bosremovehost.pl

## Purpose
Tests removing the hard-coded BOS host entry and verifying only the local host remains.

## Important APIs, Types, And Functions
Uses `AFS_bos_removehost` and `AFS_bos_listhosts`.

## Control Flow
Removes `128.2.1.2`, lists hosts, validates first item is the cell name and all remaining hosts equal local hostname.

## State And Persistence
Mutates CellServDB/BOS host list by removing the test host.

## Dependencies And Integration Points
Completes the add/list/remove host sequence.

## Risks And Test Signals
Assumes no other hosts in the cell. Exit `0` verifies removal and parser behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosremovehost.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosremovekey.pl -->
# sources/distributed-fs/openafs/src/tests/bosremovekey.pl

## Purpose
Intended to remove key version 250 from the BOS key list.

## Important APIs, Types, And Functions
Calls `AFS_bos_removekey(localhost, 250)`.

## Control Flow
Initializes AFStools, removes the key, then iterates `%ret` to check kvno 250 is gone.

## State And Persistence
Deletes kvno 250 from server key storage.

## Dependencies And Integration Points
Completes the key add/list/remove sequence.

## Risks And Test Signals
`%ret` is never populated after removal, so the verification loop cannot catch failure. Real signal is wrapper success or an external listkeys check.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosremovekey.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosremoveuser.pl -->
# sources/distributed-fs/openafs/src/tests/bosremoveuser.pl

## Purpose
Removes `testuser1` from the BOS superuser list and verifies only `admin` remains.

## Important APIs, Types, And Functions
Uses `AFS_bos_removeuser` and `AFS_bos_listusers`.

## Control Flow
Calls removeuser for `[testuser1]`, lists users, and exits `1` if any listed user is not `admin`.

## State And Persistence
Mutates UserList/superuser list.

## Dependencies And Integration Points
Completes the add/list/remove BOS user sequence.

## Risks And Test Signals
Assumes no extra administrative users. Exit `0` is a strong parser/state signal in the controlled test cell.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosremoveuser.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosrestartstopped.pl -->
# sources/distributed-fs/openafs/src/tests/bosrestartstopped.pl

## Purpose
Tests restarting a stopped BOS bnode and verifying status counters/state.

## Important APIs, Types, And Functions
Uses `AFS_bos_restart` and `AFS_bos_status`.

## Control Flow
Restarts `sleeper`, reads long status, dereferences the `sleeper` info hash, and requires `num_starts == 2` and status text `temporarily enabled, currently running normally.`

## State And Persistence
Changes the runtime and BosConfig temporary state of the `sleeper` bnode.

## Dependencies And Integration Points
Assumes prior tests created and stopped/shutdown `sleeper` so the start count expectation is deterministic.

## Risks And Test Signals
Exact status string and start count are brittle. Exit `0` confirms restart and status parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosrestartstopped.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bossalvagepart.pl -->
# sources/distributed-fs/openafs/src/tests/bossalvagepart.pl

## Purpose
Smoke-tests invoking BOS salvage for partition `a`.

## Important APIs, Types, And Functions
Calls `AFS_bos_salvage("localhost", "a", ...)`.

## Control Flow
Initializes AFStools, invokes salvage for a single partition, and exits `0` on wrapper success.

## State And Persistence
Runs salvager on partition `a`, potentially modifying volume metadata and salvage logs.

## Dependencies And Integration Points
Tests BOS salvager command integration in the configured cell.

## Risks And Test Signals
Destructive/repair operation on live test partition; should run only in disposable cell. Success is accepted BOS salvage output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bossalvagepart.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bossalvageserver.pl -->
# sources/distributed-fs/openafs/src/tests/bossalvageserver.pl

## Purpose
Smoke-tests salvaging all partitions on localhost through BOS.

## Important APIs, Types, And Functions
Calls `AFS_bos_salvage("localhost", undef, undef, undef, 1, ...)` with the `all` flag.

## Control Flow
Initializes AFStools, invokes all-partition salvage, and exits on wrapper success.

## State And Persistence
May inspect/repair every server partition and write salvage logs.

## Dependencies And Integration Points
Exercises the `-all` path in `OpenAFS::bos::AFS_bos_salvage`.

## Risks And Test Signals
Potentially expensive and disruptive. Test signal is normal BOS completion output parsed by the wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bossalvageserver.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bossalvagevolume.pl -->
# sources/distributed-fs/openafs/src/tests/bossalvagevolume.pl

## Purpose
Smoke-tests salvaging one volume, `unrep`, on partition `a`.

## Important APIs, Types, And Functions
Calls `AFS_bos_salvage("localhost", "a", "unrep", ...)`.

## Control Flow
Initializes AFStools, invokes volume-specific salvage, and exits `0` if no wrapper exception occurs.

## State And Persistence
May modify the `unrep` volume's on-disk metadata and salvage logs.

## Dependencies And Integration Points
Depends on `afs-newcell.pl` creating the `unrep` volume.

## Risks And Test Signals
Exact BOS output around salvage start/completion is parsed. Success confirms the wrapper's partition/volume argument path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bossalvagevolume.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosshutdown.pl -->
# sources/distributed-fs/openafs/src/tests/bosshutdown.pl

## Purpose
Tests `bos shutdown -wait` on the `sleeper` bnode and verifies temporary disabled status.

## Important APIs, Types, And Functions
Uses `AFS_bos_shutdown` and `AFS_bos_status`.

## Control Flow
Shuts down `sleeper`, reads status, requires `num_starts == 2` and status `temporarily disabled, currently shutdown.`

## State And Persistence
Stops the running bnode and marks it temporarily disabled.

## Dependencies And Integration Points
Part of sequential BOS lifecycle tests.

## Risks And Test Signals
Start-count expectations depend on exact test ordering. Exit `0` confirms shutdown and status parser behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosshutdown.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosstart.pl -->
# sources/distributed-fs/openafs/src/tests/bosstart.pl

## Purpose
Tests starting the `sleeper` bnode and verifying normal running status.

## Important APIs, Types, And Functions
Uses `AFS_bos_start` and `AFS_bos_status`.

## Control Flow
Starts `sleeper`, fetches its status, and requires `num_starts == 2` plus `currently running normally.`

## State And Persistence
Starts an existing disabled/stopped bnode.

## Dependencies And Integration Points
Assumes prior stop state and deterministic start counter.

## Risks And Test Signals
Exact status string and start count are brittle. Exit `0` confirms start command and parser.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosstart.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosstatus.pl -->
# sources/distributed-fs/openafs/src/tests/bosstatus.pl

## Purpose
Verifies initial long-status parsing for the `sleeper` BOS bnode.

## Important APIs, Types, And Functions
Uses `AFS_bos_status`.

## Control Flow
Reads status for `sleeper`, dereferences the returned hash entry, and requires one start and normal-running status.

## State And Persistence
Read-only.

## Dependencies And Integration Points
Depends on `boscreate.pl` having created and started `sleeper`.

## Risks And Test Signals
Status text is exact and English. Exit `0` validates `AFS_bos_status` output parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosstatus.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosstop.pl -->
# sources/distributed-fs/openafs/src/tests/bosstop.pl

## Purpose
Tests stopping the `sleeper` bnode with wait semantics.

## Important APIs, Types, And Functions
Uses `AFS_bos_stop` and `AFS_bos_status`.

## Control Flow
Stops `sleeper`, reads status, and requires `num_starts == 1` plus `disabled, currently shutdown.`

## State And Persistence
Stops and disables the bnode.

## Dependencies And Integration Points
Part of the ordered BOS lifecycle smoke suite.

## Risks And Test Signals
Depends on initial start count and exact status strings. Exit `0` validates stop behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosstop.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/build-and-run-rcs -->
# sources/distributed-fs/openafs/src/tests/build-and-run-rcs

## Purpose
Builds GNU RCS from a tarball and runs a simple check-in/check-out workflow to stress build, hardlink/archive, and file update behavior.

## Important APIs, Types, And Functions
Shell script using `gzip`, `tar`, `mkdir`, `configure`, `make`, `ci`, `co`, and `wc`.

## Control Flow
Extracts `rcs-5.7.tar.gz` from `$AFSROOT`, configures/builds in a separate object directory, creates `testfile`, performs three `ci -u` and `co -l` cycles with appended rows, and verifies the file has three lines.

## State And Persistence
Creates source/object directories, build outputs, RCS archive files, and testfile artifacts.

## Dependencies And Integration Points
Uses fd 4 for build logs, `$MAKEFLAGS`, `$AFSROOT`, and POSIX build tools. Stresses AFS behavior with real-world build tools.

## Risks And Test Signals
External archive and legacy RCS build dependencies are brittle. Success is final `wc -l` matching `3 testfile`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/build-and-run-rcs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/build-emacs -->
# sources/distributed-fs/openafs/src/tests/build-emacs

## Purpose
Runs the generic build harness on Emacs 20.7 as a large filesystem/build stress test.

## Important APIs, Types, And Functions
Shell wrapper around `$srcdir/generic-build` with `$AFSROOT/.../emacs-20.7.tar.gz`.

## Control Flow
Skips when `FAST` is set; otherwise invokes the generic build script with optional shell verbosity.

## State And Persistence
Creates unpacked source, object, and build outputs as determined by `generic-build`.

## Dependencies And Integration Points
Requires `$srcdir`, `$AFSROOT`, shell, compiler toolchain, and the archive.

## Risks And Test Signals
Old source may not build on modern systems. Success is generic-build exit `0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/build-emacs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/build-emacs-j -->
# sources/distributed-fs/openafs/src/tests/build-emacs-j

## Purpose
Parallel-build variant of the Emacs build stress test.

## Important APIs, Types, And Functions
Sets `MAKEFLAGS="-j"` and invokes `$srcdir/generic-build` for Emacs 20.7.

## Control Flow
Skips under `FAST`; otherwise runs the same build as `build-emacs` but with parallel make enabled.

## State And Persistence
Creates build artifacts and stresses concurrent metadata/data operations.

## Dependencies And Integration Points
Requires generic build harness, archive, and a toolchain. The parallelism stresses filesystem locking/cache consistency more than the serial variant.

## Risks And Test Signals
Race-sensitive and external-build dependent. Success is complete parallel build with exit `0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/build-emacs-j -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/build-gdb -->
# sources/distributed-fs/openafs/src/tests/build-gdb

## Purpose
Runs the generic build harness on GDB 5.0 as another large source-tree stress test.

## Important APIs, Types, And Functions
Shell wrapper around `$srcdir/generic-build` using `$AFSROOT/.../gdb-5.0.tar.gz`.

## Control Flow
Skips when `FAST` is set; otherwise delegates to generic-build.

## State And Persistence
Creates extracted source and build outputs.

## Dependencies And Integration Points
Depends on archive availability, compiler toolchain, and generic-build.

## Risks And Test Signals
Legacy GDB may not build on modern platforms. Success is generic-build exit `0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/build-gdb -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/build-openafs -->
# sources/distributed-fs/openafs/src/tests/build-openafs

## Purpose
Builds OpenAFS 1.2.2 from a tarball inside the filesystem under test and runs a translated error-table helper as a post-build signal.

## Important APIs, Types, And Functions
Uses `${FS} sq . 0`, optional `FAST`, `/usr/tmp` archive cache, `wget`, `generic-build`, and `translate_et`.

## Control Flow
Sets quota on current directory to unlimited, skips when `FAST` is set, copies or downloads the OpenAFS tarball, invokes generic-build, and runs `openafs-1.2.2/src/finale/translate_et 180480`.

## State And Persistence
Creates tarball copy/download and a full OpenAFS build tree in the current directory.

## Dependencies And Integration Points
Requires an `fs` command path, network or cached tarball, compiler toolchain, and generic-build.

## Risks And Test Signals
Network URL and vintage source are brittle. Uses `>& 4`, which is shell-specific. Success includes build completion and `translate_et` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/build-openafs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/checkpwd -->
# sources/distributed-fs/openafs/src/tests/checkpwd

## Purpose
Tiny wrapper that runs the `apwd` current-directory test binary.

## Important APIs, Types, And Functions
Invokes `$objdir/apwd`.

## Control Flow
No arguments or cleanup; exit status is inherited from `apwd`.

## State And Persistence
No direct persistent state.

## Dependencies And Integration Points
Integrates the shell test harness with the compiled `apwd.c` utility.

## Risks And Test Signals
Requires `$objdir` to point at built test binaries. Success is `apwd` exit `0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/checkpwd -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/compare-inum-mp -->
# sources/distributed-fs/openafs/src/tests/compare-inum-mp

## Purpose
Tests directory entry inode consistency across an AFS mount point.

## Important APIs, Types, And Functions
Uses `${FS}` for ACL and mount operations plus `$objdir/readdir-vs-lstat`.

## Control Flow
Grants `system:anyuser all` on current directory, creates a `root.cell` mount point, runs `readdir-vs-lstat` on `.` and the mount point, removes the mount point, and exits on first failure.

## State And Persistence
Temporarily changes ACLs and creates/removes a mount point.

## Dependencies And Integration Points
Requires the `fs` command, built `readdir-vs-lstat`, and a valid `root.cell` volume.

## Risks And Test Signals
ACL broadening may persist if cleanup fails. Success confirms readdir inode values match lstat across normal and mount-point directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/compare-inum-mp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/compare-inums -->
# sources/distributed-fs/openafs/src/tests/compare-inums

## Purpose
Tests directory entry inode reporting for many newly created files.

## Important APIs, Types, And Functions
Invokes `$objdir/create-files 100 0` and `$objdir/readdir-vs-lstat .`.

## Control Flow
Creates 100 empty numeric files, then validates every `readdir` inode against `lstat` for the current directory.

## State And Persistence
Leaves the 100 files unless the surrounding harness cleans them.

## Dependencies And Integration Points
Uses compiled helpers `create-files` and `readdir-vs-lstat`.

## Risks And Test Signals
Preexisting numeric files can conflict with `O_EXCL` in `create-files`. Success is zero exit from both helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/compare-inums -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/compare-with-local -->
# sources/distributed-fs/openafs/src/tests/compare-with-local

## Purpose
Compares copy/move/cat file operations between the filesystem under test and a local temporary directory.

## Important APIs, Types, And Functions
Defines shell function `compare` using `cmp` and `diff`. Uses `cp`, `mv`, `cat`, `test`, and `${objdir}/rm-rf`.

## Control Flow
Creates `$TMPDIR/compare-with-local-$$`, writes a reference file, copies/moves/cats it into and out of the current directory with content comparisons, repeats with slightly different content to test overwrite behavior, removes the temp directory, and exits `0`.

## State And Persistence
Creates transient files in both local temp and current directory; local temp is removed on success.

## Dependencies And Integration Points
Exercises standard POSIX file data operations against AFS and local disk as oracle.

## Risks And Test Signals
Uses `function` syntax, which is not strictly POSIX `/bin/sh`. Cleanup only happens on success; failures can leave temp files. Signal is all `cmp` checks passing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/compare-with-local -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/copy-and-diff-gnu-mirror -->
# sources/distributed-fs/openafs/src/tests/copy-and-diff-gnu-mirror

## Purpose
Large test that copies a GNU mirror subtree from AFS/local source into the current directory and verifies every copied file.

## Important APIs, Types, And Functions
Uses `FAST`, `LARGE`, `tar`, `find`, and `cmp`.

## Control Flow
Skips under `FAST` or without `LARGE`. Sets source to argv or `$AFSROOT/stacken.kth.se/ftp/pub`, streams `gnu` through tar into current directory, and compares every copied file against the original.

## State And Persistence
Creates a `gnu` subtree in the current directory.

## Dependencies And Integration Points
Requires a source mirror, enough space/time, and tar/cmp utilities.

## Risks And Test Signals
Large and environment-dependent. Success is all file comparisons returning equal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/copy-and-diff-gnu-mirror -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/copy-file -->
# sources/distributed-fs/openafs/src/tests/copy-file

## Purpose
Repeated simple copy test for file data stability.

## Important APIs, Types, And Functions
Uses here-document file creation and repeated `cp foo foo2`.

## Control Flow
Creates `foo` with fixed text and copies it to `foo2` many times, exiting on first failed copy.

## State And Persistence
Leaves `foo` and `foo2` in the current directory.

## Dependencies And Integration Points
Exercises file create, overwrite, and copy paths in the filesystem under test.

## Risks And Test Signals
No content comparison after copy, so it mainly catches command/write failures. Exit `0` means all repeated copies succeeded.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/copy-file -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/creat1 -->
# sources/distributed-fs/openafs/src/tests/creat1

## Purpose
Minimal shell test for creating an empty file and verifying it has zero size.

## Important APIs, Types, And Functions
Uses shell redirection, `test -f`, `test -s`, and `rm`.

## Control Flow
Truncates/creates `foobar`, fails if it is absent or nonempty, then removes it.

## State And Persistence
Temporarily creates `foobar` and deletes it.

## Dependencies And Integration Points
Basic filesystem create/stat/unlink smoke test.

## Risks And Test Signals
Very narrow coverage. Exit `0` confirms empty-file creation semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/creat1 -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/create-dirs.c -->
# sources/distributed-fs/openafs/src/tests/create-dirs.c

## Purpose
Creates a requested number of numeric directories to stress mkdir and directory entry creation.

## Important APIs, Types, And Functions
Defines `creat_dirs`, `usage`, and `main`. Uses `strtol`, `snprintf`, `mkdir`, and `err`.

## Control Flow
Parses one numeric argument, loops from `0` to `count-1`, creates a directory named by the loop index with mode `0777`, and exits on first failure.

## State And Persistence
Leaves all created directories in the current directory.

## Dependencies And Integration Points
Used by shell/harness tests for directory creation workloads.

## Risks And Test Signals
Existing numeric directory names cause failure. Success is all requested directories created.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/create-dirs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/create-files.c -->
# sources/distributed-fs/openafs/src/tests/create-files.c

## Purpose
Creates a requested number of numeric files of a requested size for filesystem stress tests.

## Important APIs, Types, And Functions
Defines `creat_files`, `usage`, and `main`. Uses `open(O_CREAT|O_EXCL)`, repeated `write`, `close`, `strtol`, and `opr_min`.

## Control Flow
Parses count and file size, creates each file named `0`, `1`, etc., writes up to 8192-byte chunks until the requested size is reached, and exits on short write or close error.

## State And Persistence
Leaves created files in the current directory.

## Dependencies And Integration Points
Used by `compare-inums` and other tests requiring many file entries.

## Risks And Test Signals
The write buffer is uninitialized, which is acceptable for size stress but not deterministic content. Existing numeric files fail due to `O_EXCL`. Success confirms create/write/close paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/create-files.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/create-remove-dirs -->
# sources/distributed-fs/openafs/src/tests/create-remove-dirs

## Purpose
Shell wrapper for repeated directory create/remove stress.

## Important APIs, Types, And Functions
Uses `$objdir/create-remove dir 1000`.

## Control Flow
Skips when `FAST` is set; otherwise asks the compiled helper to create and remove one directory name 1000 times.

## State And Persistence
No intended persistent files on success.

## Dependencies And Integration Points
Depends on `create-remove.c` helper and current directory filesystem semantics.

## Risks And Test Signals
Failures can leave the temporary directory. Exit `0` means 1000 mkdir/rmdir cycles completed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/create-remove-dirs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/create-remove-files -->
# sources/distributed-fs/openafs/src/tests/create-remove-files

## Purpose
Shell wrapper for repeated file create/unlink stress.

## Important APIs, Types, And Functions
Uses `$objdir/create-remove file 1000`.

## Control Flow
Skips when `FAST` is set; otherwise runs the compiled helper for 1000 create/unlink cycles.

## State And Persistence
No intended persistent files on success.

## Dependencies And Integration Points
Depends on `create-remove.c` helper.

## Risks And Test Signals
Failures can leave a `foo-...` file. Exit `0` means repeated create/unlink completed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/create-remove-files -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/create-remove.c -->
# sources/distributed-fs/openafs/src/tests/create-remove.c

## Purpose
Compiled helper that repeatedly creates and removes either one file or one directory name to stress metadata operations.

## Important APIs, Types, And Functions
Defines `creat_dir`, `remove_dir`, `creat_file`, `unlink_file`, `usage`, `creat_many`, and `main`. Uses `mkdir`, `rmdir`, `open`, `close`, `unlink`, `snprintf`, and `strtol`.

## Control Flow
Parses type (`file` or `dir`) and count. `creat_many` builds a process-specific name `foo-<num>-<pid>`, then loops count times calling the create and delete callbacks.

## State And Persistence
No persistent state on success; a failed iteration may leave the current test file/directory.

## Dependencies And Integration Points
Used by `create-remove-dirs` and `create-remove-files`.

## Risks And Test Signals
`creat_file` reports open failures as `mkdir` in the error message. The same name is reused each cycle, stressing cache invalidation and name reuse. Success means all cycles completed without POSIX errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/create-remove.c -->
