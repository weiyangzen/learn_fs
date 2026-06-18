# sources/distributed-fs/coda/coda-src/volutil/vol-salvage.cc

## Purpose

`vol-salvage.cc` implements Coda's partition and volume salvager. The complete 1715-line file was read. It can run as startup/full salvager or as a volume utility request, scans partition inodes, summarizes RVM volume headers, repairs vnode/inode correspondence, clears salvage flags, optionally verifies directory completeness and resolution logs, and cleans orphaned inodes or destroyed volumes.

## Important APIs, Types, and Functions

The public RPC/direct entry point is `S_VolSalvage()`. Major helpers include `SalvageFileSys()`, `SalvageVolumeGroup()`, `QuickCheck()`, `SalvageVolHead()`, `VnodeInodeCheck()`, `DirCompletenessCheck()`, `DistilVnodeEssence()`, `JudgeEntry()`, `MarkLogEntries()`, `CleanInodes()`, `ClearROInUseBit()`, `AskOffline()`, `AskOnline()`, `GetSkipVolumeNumbers()`, `SanityCheckFreeLists()`, `DestroyBadVolumes()`, `FixInodeLinkcount()`, `GetInodeSummary()`, `GetVolumeSummary()`, `CompareInodes()`, and `CompareVolumes()`.

## Control Flow

`S_VolSalvage` initializes global flags, chooses `volumeUtility` or `salvager` mode, reads skip lists and free-list state for full salvage, then salvages either all partitions or a selected partition/volume. `SalvageFileSys` locks the partition, handles `FORCESALVAGE`, offlines a selected volume, builds a sorted inode summary file, builds a sorted volume summary from RVM, and salvages each matching volume group in one RVM transaction. `SalvageVolumeGroup` skips configured volumes, fast-paths clean headers through `QuickCheck`, loads the group's inodes, checks volume headers, validates/repairs small vnode inode references, optionally runs directory completeness checks, and fixes remaining inode link counts.

## State and Persistence Behavior

The salvager mutates RVM volume headers (`inUse`, `needsSalvaged`, `dontSalvage`, `needsCallback`, file/block counts), vnode disk objects, free lists, resolution logs, volume hash entries, and underlying vice inode link counts. It uses temporary files `/tmp/salvage.inodes` and `/tmp/salvage.temp` for inode listings and summaries. Many mutations are inside RVM transactions, but raw inode operations are not rolled back by transaction aborts. Global state is reset by `zero_globals()`.

## Dependencies and Integration Points

Dependencies span `partition` inode listing, `inodeops`, `rvmlib`, `codadir`, `volume`, `fssync`, `vutil`, `index`, `recov`, `camprivate`, `volhash`, `bitmap`, `recle`, and `vice_file`. It coordinates with the running fileserver through FSYNC offline/online requests and lock files, and with resolution logging through `recov_vol_log`.

## Risks and Test Signals

Risks include raw inode side effects that survive RVM aborts, heavy use of `CODA_ASSERT` on corrupt input, fixed `/tmp` file names, a likely typo `unlink("forcepath")`, commented-out directory repair despite checking, and ambiguity for read-only versus read-write volume identity. Tests should cover full and single-volume salvage, skip list handling, clean `DONT_SALVAGE` quick path, missing inode repair, barren/debarrenize flows, orphan inode cleanup, destroyed-volume removal, directory completeness fatal cases, resolution-log salvage, and interrupted salvage followed by restart.
