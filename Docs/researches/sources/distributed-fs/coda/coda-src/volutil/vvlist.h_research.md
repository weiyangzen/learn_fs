# sources/distributed-fs/coda/coda-src/volutil/vvlist.h

## Purpose

`vvlist.h` declares the text-format version-vector list API used by Coda backup and incremental dump code. The complete 64-line header was read.

## Important APIs, Types, and Functions

It defines `vvent`, `ENDLARGEINDEX`, `LISTLINESIZE`, class `vvtable`, class `vvent_iterator`, and functions `ValidListVVHeader()`, `DumpListVVHeader()`, `ListVV()`, and `getlistfilename()`.

## Control Flow

The header exposes construction of a parsed table from an ancient list file, lookup of modification state through `IsModified()`, and one-bucket iteration through `vvent_iterator`.

## State and Persistence Behavior

`vvent` stores parsed previous-dump state: unique id, store id, seen flag, linked-list next pointer, and dump level. The header describes in-memory ownership but the text files are produced/consumed by `vvlist.cc`.

## Dependencies and Integration Points

Dependencies include `vcrcommon.h` and `cvnode.h`; callers also need volume and vnode disk types. It is part of the volutil backup/dump implementation boundary.

## Risks and Test Signals

Risks include manual linked-list ownership, fixed list line length, and friend-based iterator access. Tests should compile users against the public declarations and exercise table construction, `IsModified()`, and iterator behavior through `vvlist.cc`.
