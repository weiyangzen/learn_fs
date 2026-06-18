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
