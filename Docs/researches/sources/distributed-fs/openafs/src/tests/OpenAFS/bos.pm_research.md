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
