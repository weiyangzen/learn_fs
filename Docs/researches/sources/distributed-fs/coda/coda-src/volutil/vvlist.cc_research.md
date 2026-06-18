# sources/distributed-fs/coda/coda-src/volutil/vvlist.cc

## Purpose

`vvlist.cc` implements backup dump version-vector list support. The complete 276-line file was read. It writes per-vnode version-vector records for dumps and reads earlier lists to decide whether each vnode changed for incremental backups.

## Important APIs, Types, and Functions

Functions include `getlistfilename()`, `ValidListVVHeader()`, `DumpListVVHeader()`, `ListVV()`, `vvtable::vvtable()`, `vvtable::~vvtable()`, `vvtable::IsModified()`, `vvent_iterator::vvent_iterator()`, and `vvent_iterator::operator()()`. It works with `vvent`, `ViceStoreId`, `ViceVersionVector`, `Volume`, and `VnodeDiskObject`.

## Control Flow

Dump helpers build backup-list filenames and write human-readable headers and vnode lines. The `vvtable` constructor parses a previous list file, hashes entries by vnode bit number, and stops at `ENDLARGEINDEX` for large-vnode lists or EOF for small-vnode lists. `IsModified()` checks whether the current vnode's unique and store id match an old entry and applies dump-level rules so a lower-level incremental includes changes from higher-level incrementals when needed.

## State and Persistence Behavior

The persisted state is a text file in the backup directory named from group id, replica id, and suffix. In memory, `vvtable` owns an array of linked `vvent` lists and marks entries `isThere` when encountered. It frees all entries in the destructor.

## Dependencies and Integration Points

Dependencies include `vcrcommon.h`, `voltypes.h`, `srv.h`, `vrdb.h`, `vutil.h`, `vice_file.h`, and `vvlist.h`. The code integrates with volume dump/backup paths that need incremental backup decisions.

## Risks and Test Signals

Risks include fixed line sizes, loose parsing compatibility (`n == 12` defaulting dump level to zero), asserts on bad vnode indexes, and linked-list memory ownership. Tests should cover header validation, filename generation with and without group ids, round-trip line parsing, new/unchanged/changed vnode decisions, multilevel incremental behavior, bad index handling, and iterator traversal.
