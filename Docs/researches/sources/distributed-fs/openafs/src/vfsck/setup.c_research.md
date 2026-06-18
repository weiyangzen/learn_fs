<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/setup.c -->
# sources/distributed-fs/openafs/src/vfsck/setup.c

## Purpose
Prepares a filesystem device for checking. It validates device safety, opens read/write descriptors, reads and verifies the superblock and alternate superblock, handles clean-state early exits and format conversion, reads summary information, allocates fsck maps, and initializes the buffer cache.

## Important APIs, Types, And Functions
Key functions are `setup`, `readsb`, `badsb`, `calcsb`, `is_mounted`, `is_swap`, `is_pre_init`, `is_roroot`, `is_hotroot`, `is_root`, `vfsck_getline`, `freply`, and HP-UX 11 `UpdateAlternateSuper`. Important local structures are `asblk`, `pbp`, and the `CGSIZE` macro for dynamic cylinder group sizing.

## Control Flow
`setup` resets per-run globals, stats and canonicalizes the target, resolves Solaris directory mount points through vfstab, checks mounted/root/swap safety unless `-n` or force modes apply, opens the device read-only and optionally write-only, allocates superblock buffers, and calls `readsb`. If the primary superblock is bad and no alternate was specified, it may search alternate superblocks. It validates optimization and minfree fields, honors HP-UX preen-clean early exits, can convert old/new Sun cylinder-group formats, flushes an alternate superblock when needed, reads summary info, optionally skips clean Sun filesystems in preen mode, allocates `blockmap`, `statemap`, and `lncntp`, then calls `bufinit`.

`readsb` reads the selected superblock, validates magic and geometry, computes `dev_bsize`, reads the first alternate superblock, copies dynamic fields into it, and compares static fields. Helper functions identify mounted, root, read-only root, and swap devices to protect live filesystems.

## State And Persistence
Setup initializes or mutates global device descriptors, `hotroot`, `mountedfs`, `havesb`, `dev_bsize`, superblock buffers, summary pointers, clean/conversion flags, and allocation maps. It may persist repaired superblock fields or converted format metadata before the main passes.

## Dependencies And Integration Points
It is called by `checkfilesys` before any pass. It depends on platform mount tables, `ustat`, HP-UX `pstat`, Sun vfstab/mnttab APIs, UFS headers, `bread`/`bwrite` from `utilities.c`, and `bufinit`. Its clean-state decisions affect whether main returns without running passes.

## Risks And Test Signals
Risks include device safety false negatives, alternate superblock comparison drift, hard-coded platform assumptions, memory allocation failures on huge filesystems, and writes during format conversion. Tests should cover bad primary superblock with alternate recovery, clean preen early exit, mounted/root/swap prompts, read-only/no-write mode, summary read failures, Sun format conversion, HP-UX clean-state returns, and map allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/setup.c -->
