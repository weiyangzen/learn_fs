# sources/distributed-fs/openafs/src/volser/vol-dump.c

## Purpose
Implements `voldump`, a standalone utility that attaches a local volume directly from partition files and emits a `vos dump`-format stream without using volserver.

## Important APIs And Functions
`main` initializes the volume package as `volumeUtility` and registers command options. `handleit` parses partition, volume id, output file, verbosity, dump time, and `-pad-errors`. `HandleVolume` reads the `.vol` header, validates magic/version, converts it to `VolumeHeader`, and calls `AttachVolume`. `AttachVolume` builds a minimal in-memory `Volume` with inode handles and reads volume/index/link headers. Dump helpers mirror `dumpstuff.c`: `DumpDumpHeader`, `DumpVolumeHeader`, `DumpVnodeIndex`, `DumpVnode`, `DumpFile`, and `DumpEnd`.

## Control Flow And State
The utility attaches partitions, locates the requested volume header, constructs a `Volume`, opens the output fd or stdout, writes dump header/volume header/vnodes/end marker, then closes the fd. Incremental filtering uses `serverModifyTime >= fromtime`; directories can be force-dumped through the `dumpAllDirs` argument, currently false in this utility.

## Persistence And Integration
It reads persistent volume headers, vnode indexes, link table, ACLs, and vnode file inodes. It writes only the dump output, except for no runtime volume metadata changes. `-pad-errors` can convert file read errors or premature EOF into NUL-filled output while preserving declared size.

## Risks And Test Signals
Risks include code duplication with `dumpstuff.c`, minimal attach cleanup, ACL byte-order mutation while dumping directory vnode buffers, stdout close behavior, dump stream corruption on partial writes, and padded dumps hiding media errors. Test signals include direct dump/volserver dump comparison, corrupted header/version rejection, date parser coverage, large-file dumps, invalid ACL handling, `-pad-errors` behavior, and round-trip restore tests.
