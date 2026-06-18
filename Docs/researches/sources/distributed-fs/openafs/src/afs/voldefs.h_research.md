# sources/distributed-fs/openafs/src/afs/voldefs.h

Purpose: defines common volume type IDs and volume header filename conventions.

Important APIs/types: aliases `readwriteVolume`, `readonlyVolume`, and `backupVolume` map to `RWVOL`, `ROVOL`, and `BACKVOL`. Type IDs are `RWVOL = 0`, `ROVOL = 1`, `BACKVOL = 2`. Header file naming uses `VHDREXT`/`VFORMAT`, with `.vl` on AIX/HPUX and `.vol` elsewhere. `VMAXPATHLEN` caps external volume path length at 64 bytes.

Control flow: compile-time constants; `AFS_VOLID_FMT` from `afs/param.h` must be available before including this file.

State and persistence: affects persistent on-disk volume header filenames on file servers and related tooling.

Dependencies and integration points: consumed by volume and VLDB code, including `afs_volume.c` when choosing RW/RO/BK IDs from entries.

Risks: changing numeric type IDs or file-name formats breaks compatibility. The comments warn against clever token-pasting because historical compilers handled it inconsistently.

Test signals: build with AIX/HPUX and non-AIX/HPUX formats, verify generated names for representative volume IDs, and confirm volume type indexing matches VLDB arrays.
