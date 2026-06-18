# sources/distributed-fs/openafs/src/volser/dump.h

## Purpose
Defines the on-wire/on-file volume dump format constants and `DumpHeader` structure used by volserver dump/restore tools.

## Important APIs, Types, And Constants
`DUMPVERSION`, `DUMPBEGINMAGIC`, and `DUMPENDMAGIC` identify dump streams. Section tags are `D_DUMPHEADER`, `D_VOLUMEHEADER`, `D_VNODE`, and `D_DUMPEND`. `DumpHeader` stores the dumped volume id/name and up to `MAXDUMPTIMES` from/to timestamp pairs. `SHAKE1` through `SHAKE5` and `SHAKE_ABORT` are volume move handshaking constants.

## Format And Control Flow
The comments document the tag grammar: legacy short tags, TLV-style standard tags with variable-length length fields, indefinite length value `0x80`, and critical-tag marker `0x7e`. Separate known tag tables are documented for dump header, volume header, and vnode sections.

## Persistence And Integration
This header is the shared contract for `dumpstuff.c`, `restorevol.c`, `vol-dump.c`, and volserver RPC paths. It maps serialized dump fields back to `VolumeDiskData` and `VnodeDiskObject` fields.

## Risks And Test Signals
Risks include format drift between writer and reader, unbounded or unsupported dump-time counts, incorrect handling of unknown critical tags, and compatibility with historical nonstandard tags. Test signals include dump/restore round trips, incremental dump tests, unknown noncritical tag skipping, unknown critical tag rejection, big-file `h` records, and `MAXDUMPTIMES` boundary tests.
