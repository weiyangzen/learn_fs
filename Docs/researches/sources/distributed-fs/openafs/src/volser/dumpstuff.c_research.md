# sources/distributed-fs/openafs/src/volser/dumpstuff.c

## Purpose
Implements the volserver dump, multidump, restore, and dump-size calculation engine over RX calls and OpenAFS inode/vnode handles.

## Important APIs And Functions
Public entry points are `DumpVolume`, `DumpVolMulti`, `RestoreVolume`, `SizeDumpVolume`, and `ProcessIndex`. The internal `iod` layer abstracts RX input/output and supports multi-call writes with per-call error codes. Serialization helpers read/write tags, integers, strings, ACL byte strings, vnode files, and standard TLV lengths. Restore helpers include `ReadDumpHeader`, `ReadVolumeHeader`, `ReadVnodes`, and `volser_WriteFile`.

## Control Flow
Dump flow writes a dump header, volume header, large vnode index, small vnode index, and dump end marker. Vnode dumping emits metadata for every non-null vnode and file data only when `serverModifyTime >= fromtime` or forced for directories. Restore flow reads the dump header and volume header, snapshots existing large/small vnode index entries, streams new vnodes into newly created inodes, removes old vnode inodes not present in the dump, copies or clears stats, rewrites `V_disk(vp)`, clears `destroyMe`, and calls `VUpdateVolume`.

## State And Persistence
The file reads/writes vnode index files, special inode data, ACLs, and volume disk data. It decrements old inode references when overwriting or cleaning restore state. It preserves existing volume stats only when `DoPreserveVolumeStats` is set, otherwise clears day/week stats. It sets `V_needsSalvaged` when inode creation/write failures may leave inconsistent disk state.

## Dependencies And Integration
Dependencies include RX, inode handles, vnode classes, ACL conversion, FSSYNC/daemon headers, volserver error codes, and volume macros. `dump.h` defines the stream grammar.

## Risks And Test Signals
High-risk areas are untrusted dump parsing, duplicate file data tags, large-file length handling, partial restore cleanup, ACL byte-order conversion, and size calculation staying in sync with actual dump emission. Test signals include malformed dumps, duplicate `f`/`h` tags, invalid ACLs, interrupted RX streams, partial restore failure injection, incremental restore deletion behavior, multidump with one failed receiver, and comparing `SizeDumpVolume` with actual byte counts.
