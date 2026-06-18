# sources/distributed-fs/openafs/src/tools/dumpscan/dumptool.c

Purpose: standalone interactive tool for inspecting and restoring MR-AFS/OpenAFS dump files. It predates or sits beside the callback-based dumpscan library and contains its own dump parser, directory walker, and optional MR-AFS residency helpers.

Important APIs/functions: `main` opens a dump, reads the dump header and volume header, scans vnodes twice, validates the dump trailer, then either lists all FIDs (`-i`), performs MR-AFS residency operations, or starts `InteractiveRestore`. `ReadDumpHeader`, `ReadVolumeHeader`, and `ScanVnodes` parse tagged records into `VolumeDiskData` and `VnodeDiskObject`. `InsertVnode`/`GetVnode` maintain large-directory and small-file vnode indexes. Interactive commands route to `DirectoryList`, `ChangeDirectory`, `CopyFile`, `CopyVnode`, and optional `DumpAllFiles`.

State/persistence: builds in-memory indexes and caches directory vnode data; copy commands write files from dump data to the host filesystem. It uses global arrays, counters, terminal width, and MR-AFS option state. Dependencies include OpenAFS volume/vnode/dir headers, large-file stdio, optional residency server APIs, and POSIX terminal/file calls.

Risks/test signals: the code has legacy assumptions, globals, limited bounds checks, and conditional MR-AFS code. It handles corrupt or incomplete dumps with `-f` only for trailer absence. Strong signals are interactive restore success and correct FID/path listing from real dumps.
