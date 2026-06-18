<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/main.c -->
# sources/distributed-fs/openafs/src/vfsck/main.c

## Purpose
Top-level driver for the OpenAFS-modified UFS/HFS fsck. It parses command-line options, selects filesystems from arguments or fstab/vfstab, schedules parallel preen checks by disk, invokes setup and passes 1 through 5, reports summaries, updates clean state, and triggers AFS salvager recovery when repaired partitions contain Vice inodes.

## Important APIs, Types, And Functions
The main entry points are `main`, `finddisk`, `addpart`, `startdisk`, `checkfilesys`, `blockcheck`, platform-specific `check_sanity`, `numbers`, `unrawname`, and `rawname`. Internal scheduling types are `struct disk` and `struct part`. Important globals include `tryForce`, `returntosingle`, `nrun`, `ndisks`, `maxrun`, `wflag`, HP-UX `ge_danger`/`fixed`, and Sun `exitstat`.

## Control Flow
`main` syncs disks, parses legacy BSD, Sun, and HP-UX options, installs signal handlers, and either checks explicitly named devices or walks filesystem tables. In preen mode it groups partitions by disk, forks workers up to `maxrun`, collects exit statuses, and reports unexpected inconsistencies. `checkfilesys` canonicalizes the device with `EnsureDevice`, calls `setup`, optionally performs sanity-only mode, then runs `pass1`, optional `pass1b`, `pass2`, `pass3`, `pass4`, and `pass5`. It prints summary statistics and updates clean-state flags.

After a modification, `checkfilesys` closes device descriptors and, if Vice inodes were found or `/TRYFORCE` exists, temporarily mounts the block device on `/etc/vfsck.<device>` or the parent mount point fallback, creates `FORCESALVAGE`, unmounts it, and removes the temporary directory. This is the OpenAFS integration point that forces a full fileserver salvager pass after low-level repairs.

## State And Persistence
The driver coordinates all persistent filesystem changes made by the pass files. It also changes superblock clean state, may create and remove temporary mount directories under `/etc`, and may create a durable `FORCESALVAGE` marker in a repaired AFS partition. Process state includes fstab-derived queues, child process IDs, global flags, and per-check maps freed after each filesystem.

## Dependencies And Integration Points
It depends on HP-UX/Sun/BSD filesystem tables, mount APIs, device naming conventions, generated `AFS_component_version_number.c`, `EnsureDevice`, `setup`, pass functions, buffer finalization, and logging through `vfscklogprintf`. The `FORCESALVAGE` marker integrates this UFS-level checker with the OpenAFS volume salvager and fileserver startup behavior.

## Risks And Test Signals
Risks include destructive operation on mounted/root/swap devices when force flags are misused, legacy option parsing, possible compile hazards in disabled/conditional branches, hard-coded `/etc/vfsck.*`, temporary mounting during boot, and close ordering around `ckfini`. Tests should cover explicit-device checks, fstab preen scheduling, `-n/-y/-p/-P/-m/-F` combinations, dirty Vice partition salvage marker creation, clean filesystem early exits, root filesystem modified exits, and failed temporary mount handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/main.c -->
